from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from ..database import deals_collection, customers_collection, activities_collection
from pydantic import BaseModel

router = APIRouter()

class DealStage(BaseModel):
    name: str
    order: int
    color: str

class PipelineCreate(BaseModel):
    name: str
    stages: List[DealStage]

class DealMove(BaseModel):
    deal_id: str
    new_stage: str

# Estágios padrão do pipeline
DEFAULT_STAGES = [
    {"name": "Prospecção", "order": 1, "color": "#6B7280"},
    {"name": "Qualificação", "order": 2, "color": "#3B82F6"},
    {"name": "Proposta", "order": 3, "color": "#F59E0B"},
    {"name": "Negociação", "order": 4, "color": "#8B5CF6"},
    {"name": "Fechamento", "order": 5, "color": "#10B981"},
]

@router.get("/pipeline/stages")
async def get_pipeline_stages():
    """Obter estágios do pipeline"""
    return {"stages": DEFAULT_STAGES}

@router.get("/pipeline/board")
async def get_pipeline_board():
    """Obter board do pipeline com todos os deals por estágio"""
    try:
        pipeline_data = []
        
        for stage in DEFAULT_STAGES:
            # Buscar deals neste estágio
            deals = await deals_collection.find({
                "stage": stage["name"],
                "status": "open"
            }).sort("created_at", -1).to_list(100)
            
            # Enriquecer com dados do cliente
            enriched_deals = []
            total_value = 0
            
            for deal in deals:
                customer = await customers_collection.find_one({
                    "_id": ObjectId(deal["customer_id"])
                })
                
                enriched_deals.append({
                    "id": str(deal["_id"]),
                    "title": deal["title"],
                    "value": deal.get("value", 0),
                    "customer_name": customer["name"] if customer else "N/A",
                    "customer_id": deal["customer_id"],
                    "created_at": deal["created_at"],
                    "updated_at": deal.get("updated_at"),
                    "probability": deal.get("probability", 50),
                    "expected_close_date": deal.get("expected_close_date"),
                    "description": deal.get("description")
                })
                
                total_value += deal.get("value", 0)
            
            pipeline_data.append({
                "stage": stage["name"],
                "order": stage["order"],
                "color": stage["color"],
                "deals": enriched_deals,
                "count": len(enriched_deals),
                "total_value": total_value
            })
        
        # Calcular totais
        total_deals = sum(s["count"] for s in pipeline_data)
        total_pipeline_value = sum(s["total_value"] for s in pipeline_data)
        
        return {
            "stages": pipeline_data,
            "summary": {
                "total_deals": total_deals,
                "total_value": total_pipeline_value
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar pipeline: {str(e)}")


@router.post("/pipeline/move")
async def move_deal(move: DealMove):
    """Mover deal para outro estágio"""
    if not ObjectId.is_valid(move.deal_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    # Verificar se estágio existe
    valid_stages = [s["name"] for s in DEFAULT_STAGES]
    if move.new_stage not in valid_stages:
        raise HTTPException(status_code=400, detail="Estágio inválido")
    
    # Atualizar deal
    result = await deals_collection.update_one(
        {"_id": ObjectId(move.deal_id)},
        {"$set": {
            "stage": move.new_stage,
            "updated_at": datetime.now()
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Deal não encontrado")
    
    # Registrar atividade
    deal = await deals_collection.find_one({"_id": ObjectId(move.deal_id)})
    await activities_collection.insert_one({
        "title": f"Deal movido para {move.new_stage}",
        "description": f"Deal '{deal['title']}' foi movido para o estágio {move.new_stage}",
        "activity_type": "pipeline_move",
        "status": "completed",
        "customer_id": deal["customer_id"],
        "deal_id": move.deal_id,
        "created_at": datetime.now(),
        "automated": True
    })
    
    return {
        "message": "Deal movido com sucesso",
        "new_stage": move.new_stage
    }


@router.post("/pipeline/deal/{deal_id}/win")
async def win_deal(deal_id: str):
    """Marcar deal como ganho"""
    if not ObjectId.is_valid(deal_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    deal = await deals_collection.find_one({"_id": ObjectId(deal_id)})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal não encontrado")
    
    # Atualizar deal
    await deals_collection.update_one(
        {"_id": ObjectId(deal_id)},
        {"$set": {
            "status": "won",
            "stage": "Fechamento",
            "closed_at": datetime.now(),
            "updated_at": datetime.now()
        }}
    )
    
    # Atualizar cliente para "cliente"
    await customers_collection.update_one(
        {"_id": ObjectId(deal["customer_id"])},
        {"$set": {
            "status": "cliente",
            "valor_contrato": deal.get("value", 0),
            "updated_at": datetime.now()
        }}
    )
    
    # Registrar atividade
    await activities_collection.insert_one({
        "title": f"Deal ganho: {deal['title']}",
        "description": f"Deal fechado com sucesso no valor de R$ {deal.get('value', 0):.2f}",
        "activity_type": "deal_won",
        "status": "completed",
        "customer_id": deal["customer_id"],
        "deal_id": deal_id,
        "created_at": datetime.now(),
        "automated": True
    })
    
    return {
        "message": "Deal marcado como ganho!",
        "value": deal.get("value", 0)
    }


@router.post("/pipeline/deal/{deal_id}/lose")
async def lose_deal(deal_id: str, reason: Optional[str] = None):
    """Marcar deal como perdido"""
    if not ObjectId.is_valid(deal_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    deal = await deals_collection.find_one({"_id": ObjectId(deal_id)})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal não encontrado")
    
    # Atualizar deal
    await deals_collection.update_one(
        {"_id": ObjectId(deal_id)},
        {"$set": {
            "status": "lost",
            "lost_reason": reason,
            "closed_at": datetime.now(),
            "updated_at": datetime.now()
        }}
    )
    
    # Registrar atividade
    await activities_collection.insert_one({
        "title": f"Deal perdido: {deal['title']}",
        "description": f"Deal perdido. Motivo: {reason or 'Não especificado'}",
        "activity_type": "deal_lost",
        "status": "completed",
        "customer_id": deal["customer_id"],
        "deal_id": deal_id,
        "created_at": datetime.now(),
        "automated": True
    })
    
    return {
        "message": "Deal marcado como perdido",
        "reason": reason
    }


@router.get("/pipeline/metrics")
async def get_pipeline_metrics():
    """Métricas do pipeline de vendas"""
    try:
        # Taxa de conversão por estágio
        conversion_rates = []
        
        for i, stage in enumerate(DEFAULT_STAGES[:-1]):
            current_stage = stage["name"]
            next_stage = DEFAULT_STAGES[i + 1]["name"]
            
            current_count = await deals_collection.count_documents({
                "stage": current_stage,
                "status": "open"
            })
            
            # Deals que passaram para o próximo estágio
            moved_count = await deals_collection.count_documents({
                "stage": next_stage,
                "status": {"$in": ["open", "won"]}
            })
            
            conversion_rate = (moved_count / current_count * 100) if current_count > 0 else 0
            
            conversion_rates.append({
                "from": current_stage,
                "to": next_stage,
                "conversion_rate": round(conversion_rate, 2)
            })
        
        # Tempo médio por estágio
        avg_time_by_stage = []
        
        for stage in DEFAULT_STAGES:
            pipeline = [
                {"$match": {"stage": stage["name"]}},
                {"$addFields": {
                    "time_in_stage": {
                        "$divide": [
                            {"$subtract": [
                                {"$ifNull": ["$updated_at", datetime.now()]},
                                "$created_at"
                            ]},
                            86400000  # Convert milliseconds to days
                        ]
                    }
                }},
                {"$group": {
                    "_id": None,
                    "avg_days": {"$avg": "$time_in_stage"}
                }}
            ]
            
            result = await deals_collection.aggregate(pipeline).to_list(1)
            avg_days = result[0]["avg_days"] if result and result[0].get("avg_days") else 0
            
            avg_time_by_stage.append({
                "stage": stage["name"],
                "avg_days": round(avg_days, 1)
            })
        
        # Taxa de vitória geral
        total_closed = await deals_collection.count_documents({
            "status": {"$in": ["won", "lost"]}
        })
        total_won = await deals_collection.count_documents({"status": "won"})
        win_rate = (total_won / total_closed * 100) if total_closed > 0 else 0
        
        # Valor médio de deal
        pipeline = [
            {"$match": {"status": "won"}},
            {"$group": {
                "_id": None,
                "avg_value": {"$avg": "$value"},
                "total_value": {"$sum": "$value"}
            }}
        ]
        value_stats = await deals_collection.aggregate(pipeline).to_list(1)
        avg_deal_value = value_stats[0]["avg_value"] if value_stats else 0
        total_won_value = value_stats[0]["total_value"] if value_stats else 0
        
        return {
            "conversion_rates": conversion_rates,
            "avg_time_by_stage": avg_time_by_stage,
            "win_rate": round(win_rate, 2),
            "avg_deal_value": round(avg_deal_value, 2),
            "total_won_value": round(total_won_value, 2),
            "total_closed_deals": total_closed,
            "total_won_deals": total_won
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular métricas: {str(e)}")


@router.get("/pipeline/forecast")
async def get_pipeline_forecast():
    """Previsão de faturamento baseado no pipeline"""
    try:
        forecast = []
        total_weighted_value = 0
        
        for stage in DEFAULT_STAGES:
            deals = await deals_collection.find({
                "stage": stage["name"],
                "status": "open"
            }).to_list(1000)
            
            stage_value = 0
            weighted_value = 0
            
            for deal in deals:
                value = deal.get("value", 0)
                probability = deal.get("probability", 50) / 100
                
                stage_value += value
                weighted_value += value * probability
            
            forecast.append({
                "stage": stage["name"],
                "total_value": stage_value,
                "weighted_value": weighted_value,
                "deals_count": len(deals)
            })
            
            total_weighted_value += weighted_value
        
        return {
            "forecast_by_stage": forecast,
            "total_weighted_forecast": round(total_weighted_value, 2),
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar forecast: {str(e)}")
