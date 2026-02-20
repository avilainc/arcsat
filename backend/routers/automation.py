from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from ..database import customers_collection, interactions_collection, activities_collection
import asyncio

router = APIRouter()

@router.post("/automation/follow-up/{customer_id}")
async def create_follow_up_sequence(customer_id: str, days: List[int] = [1, 3, 7, 14]):
    """Criar sequência automática de follow-up"""
    if not ObjectId.is_valid(customer_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    customer = await customers_collection.find_one({"_id": ObjectId(customer_id)})
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    activities_created = []

    for day in days:
        activity = {
            "title": f"Follow-up dia {day} - {customer['name']}",
            "description": f"Follow-up automático agendado para {day} dia(s) após o primeiro contato",
            "activity_type": "follow_up",
            "status": "pending",
            "customer_id": customer_id,
            "due_date": datetime.now() + timedelta(days=day),
            "created_at": datetime.now(),
            "automated": True
        }

        result = await activities_collection.insert_one(activity)
        activities_created.append(str(result.inserted_id))

    return {
        "message": f"Sequência de {len(days)} follow-ups criada",
        "activities": activities_created
    }


@router.post("/automation/score-leads")
async def calculate_lead_scores():
    """Calcular score de leads automaticamente"""
    try:
        leads = await customers_collection.find({"status": "lead"}).to_list(1000)
        updated = 0

        for lead in leads:
            score = 0
            lead_id = str(lead["_id"])

            # +20 pontos se tem CNPJ
            if lead.get("cnpj"):
                score += 20

            # +15 pontos se tem website
            if lead.get("website"):
                score += 15

            # +10 pontos se tem LinkedIn
            if lead.get("linkedin"):
                score += 10

            # +20 pontos por cada interação
            interactions_count = await interactions_collection.count_documents({
                "customer_id": lead_id
            })
            score += min(interactions_count * 20, 60)  # Máximo 60 pontos

            # +10 pontos se tem valor de contrato estimado
            if lead.get("valor_contrato") and lead.get("valor_contrato") > 0:
                score += 10

            # +5 pontos se tem responsável atribuído
            if lead.get("responsavel"):
                score += 5

            # Categoria aumenta score
            if lead.get("categoria") == "grande":
                score += 20
            elif lead.get("categoria") == "medio":
                score += 10
            elif lead.get("categoria") == "pequeno":
                score += 5

            # Limitar score entre 0 e 100
            score = min(max(score, 0), 100)

            # Atualizar lead
            await customers_collection.update_one(
                {"_id": lead["_id"]},
                {"$set": {"score": score}}
            )
            updated += 1

        return {
            "message": f"Score calculado para {updated} leads",
            "total_leads": len(leads)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular scores: {str(e)}")


@router.post("/automation/convert-hot-leads")
async def auto_convert_hot_leads(min_score: int = 70):
    """Converter leads com score alto para prospects automaticamente"""
    try:
        hot_leads = await customers_collection.find({
            "status": "lead",
            "score": {"$gte": min_score}
        }).to_list(100)

        converted = 0
        for lead in hot_leads:
            await customers_collection.update_one(
                {"_id": lead["_id"]},
                {"$set": {
                    "status": "prospect",
                    "updated_at": datetime.now()
                }}
            )

            # Criar interação automática
            await interactions_collection.insert_one({
                "customer_id": str(lead["_id"]),
                "tipo": "automacao",
                "titulo": "Lead convertido automaticamente para Prospect",
                "descricao": f"Conversão automática devido ao score alto ({lead.get('score', 0)})",
                "data": datetime.now(),
                "resultado": "positivo",
                "created_at": datetime.now()
            })

            converted += 1

        return {
            "message": f"{converted} leads convertidos para prospect",
            "min_score": min_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao converter leads: {str(e)}")


@router.post("/automation/inactive-customer-alert")
async def alert_inactive_customers(days: int = 30):
    """Criar atividades para clientes inativos"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)

        inactive_customers = await customers_collection.find({
            "status": "cliente",
            "updated_at": {"$lt": cutoff_date}
        }).to_list(100)

        activities_created = 0

        for customer in inactive_customers:
            # Verificar se já existe atividade pendente
            existing = await activities_collection.count_documents({
                "customer_id": str(customer["_id"]),
                "status": "pending",
                "activity_type": "reativacao"
            })

            if existing == 0:
                await activities_collection.insert_one({
                    "title": f"Reativar cliente - {customer['name']}",
                    "description": f"Cliente sem interação há {days}+ dias. Entrar em contato para reativação.",
                    "activity_type": "reativacao",
                    "status": "pending",
                    "customer_id": str(customer["_id"]),
                    "due_date": datetime.now() + timedelta(days=1),
                    "created_at": datetime.now(),
                    "automated": True,
                    "priority": "high"
                })
                activities_created += 1

        return {
            "message": f"{activities_created} atividades de reativação criadas",
            "inactive_customers": len(inactive_customers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar alertas: {str(e)}")


@router.post("/automation/contract-renewal-reminder")
async def contract_renewal_reminders(days_before: int = 30):
    """Criar lembretes de renovação de contrato"""
    try:
        future_date = datetime.now() + timedelta(days=days_before)

        expiring_contracts = await customers_collection.find({
            "data_fim_contrato": {
                "$gte": datetime.now().isoformat(),
                "$lte": future_date.isoformat()
            }
        }).to_list(100)

        reminders_created = 0

        for customer in expiring_contracts:
            # Verificar se já existe lembrete
            existing = await activities_collection.count_documents({
                "customer_id": str(customer["_id"]),
                "status": "pending",
                "activity_type": "renovacao"
            })

            if existing == 0:
                await activities_collection.insert_one({
                    "title": f"Renovação de contrato - {customer['name']}",
                    "description": f"Contrato vence em {customer.get('data_fim_contrato')}. Entrar em contato para renovação.",
                    "activity_type": "renovacao",
                    "status": "pending",
                    "customer_id": str(customer["_id"]),
                    "due_date": datetime.now() + timedelta(days=7),
                    "created_at": datetime.now(),
                    "automated": True,
                    "priority": "high"
                })
                reminders_created += 1

        return {
            "message": f"{reminders_created} lembretes de renovação criados",
            "expiring_contracts": len(expiring_contracts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar lembretes: {str(e)}")


@router.post("/automation/tag-by-segment")
async def auto_tag_by_segment():
    """Adicionar tags automaticamente baseado em segmento"""
    try:
        customers = await customers_collection.find({}).to_list(1000)
        updated = 0

        segment_tags = {
            "tecnologia": ["tech", "inovacao", "digital"],
            "saude": ["saude", "medicina", "hospitalar"],
            "educacao": ["educacao", "ensino", "escola"],
            "financeiro": ["financas", "banco", "investimento"],
            "varejo": ["varejo", "loja", "comercio"],
            "industria": ["industria", "fabrica", "producao"]
        }

        for customer in customers:
            segmento = customer.get("segmento", "").lower()
            if segmento in segment_tags:
                current_tags = customer.get("tags", [])
                new_tags = list(set(current_tags + segment_tags[segmento]))

                await customers_collection.update_one(
                    {"_id": customer["_id"]},
                    {"$set": {"tags": new_tags}}
                )
                updated += 1

        return {
            "message": f"Tags atualizadas para {updated} clientes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar tags: {str(e)}")


@router.get("/automation/recommendations/{customer_id}")
async def get_customer_recommendations(customer_id: str):
    """Recomendações automáticas para um cliente"""
    if not ObjectId.is_valid(customer_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    customer = await customers_collection.find_one({"_id": ObjectId(customer_id)})
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    recommendations = []

    # Recomendação: completar cadastro
    missing_fields = []
    important_fields = ["cnpj", "telefone", "cep", "segmento", "origem", "responsavel"]
    for field in important_fields:
        if not customer.get(field):
            missing_fields.append(field)

    if missing_fields:
        recommendations.append({
            "type": "complete_profile",
            "priority": "medium",
            "message": f"Completar cadastro: {', '.join(missing_fields)}",
            "action": "edit_customer"
        })

    # Recomendação: agendar follow-up
    interactions_count = await interactions_collection.count_documents({
        "customer_id": customer_id
    })

    if interactions_count == 0:
        recommendations.append({
            "type": "first_contact",
            "priority": "high",
            "message": "Agendar primeiro contato com o cliente",
            "action": "create_interaction"
        })

    # Recomendação: aumentar score
    score = customer.get("score", 0)
    if score < 50:
        recommendations.append({
            "type": "increase_score",
            "priority": "medium",
            "message": "Score baixo. Adicione mais informações e interações para qualificar melhor este lead.",
            "action": "add_interactions"
        })

    # Recomendação: converter para prospect
    if customer.get("status") == "lead" and score >= 70:
        recommendations.append({
            "type": "convert_to_prospect",
            "priority": "high",
            "message": "Lead qualificado! Considere converter para Prospect.",
            "action": "change_status"
        })

    # Recomendação: converter para cliente
    if customer.get("status") == "prospect" and interactions_count >= 5:
        recommendations.append({
            "type": "convert_to_customer",
            "priority": "high",
            "message": "Múltiplas interações registradas. Considere fechar o negócio!",
            "action": "create_deal"
        })

    return {
        "customer_id": customer_id,
        "customer_name": customer["name"],
        "total_recommendations": len(recommendations),
        "recommendations": recommendations
    }
