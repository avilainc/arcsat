from fastapi import APIRouter, HTTPException
from typing import List, Dict
from datetime import datetime, timedelta
from bson import ObjectId
from ..database import (
    customers_collection,
    deals_collection,
    activities_collection,
    interactions_collection,
    notes_collection
)

router = APIRouter()

@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Estatísticas gerais do CRM"""
    try:
        # Total de clientes por status
        total_customers = await customers_collection.count_documents({})
        leads = await customers_collection.count_documents({"status": "lead"})
        prospects = await customers_collection.count_documents({"status": "prospect"})
        clientes = await customers_collection.count_documents({"status": "cliente"})
        inativos = await customers_collection.count_documents({"status": "inativo"})
        
        # Novos clientes este mês
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_this_month = await customers_collection.count_documents({
            "created_at": {"$gte": start_of_month}
        })
        
        # Total de deals
        total_deals = await deals_collection.count_documents({})
        open_deals = await deals_collection.count_documents({"status": "open"})
        won_deals = await deals_collection.count_documents({"status": "won"})
        lost_deals = await deals_collection.count_documents({"status": "lost"})
        
        # Valor total em negociações
        pipeline = [
            {"$match": {"status": "open"}},
            {"$group": {"_id": None, "total": {"$sum": "$value"}}}
        ]
        open_value = await deals_collection.aggregate(pipeline).to_list(1)
        total_open_value = open_value[0]["total"] if open_value else 0
        
        # Valor ganho este mês
        won_pipeline = [
            {"$match": {
                "status": "won",
                "updated_at": {"$gte": start_of_month}
            }},
            {"$group": {"_id": None, "total": {"$sum": "$value"}}}
        ]
        won_value = await deals_collection.aggregate(won_pipeline).to_list(1)
        won_this_month = won_value[0]["total"] if won_value else 0
        
        # Atividades pendentes
        pending_activities = await activities_collection.count_documents({"status": "pending"})
        
        # Interações esta semana
        start_of_week = datetime.now() - timedelta(days=7)
        interactions_week = await interactions_collection.count_documents({
            "created_at": {"$gte": start_of_week}
        })
        
        # Top 5 clientes por valor de contrato
        top_customers = await customers_collection.find(
            {"valor_contrato": {"$gt": 0}},
            {"name": 1, "valor_contrato": 1, "email": 1}
        ).sort("valor_contrato", -1).limit(5).to_list(5)
        
        # Conversão de leads
        conversion_rate = (clientes / leads * 100) if leads > 0 else 0
        
        return {
            "customers": {
                "total": total_customers,
                "leads": leads,
                "prospects": prospects,
                "clientes": clientes,
                "inativos": inativos,
                "new_this_month": new_this_month,
                "conversion_rate": round(conversion_rate, 2)
            },
            "deals": {
                "total": total_deals,
                "open": open_deals,
                "won": won_deals,
                "lost": lost_deals,
                "total_open_value": total_open_value,
                "won_this_month": won_this_month
            },
            "activities": {
                "pending": pending_activities
            },
            "interactions": {
                "this_week": interactions_week
            },
            "top_customers": [
                {
                    "id": str(c["_id"]),
                    "name": c["name"],
                    "email": c.get("email"),
                    "valor_contrato": c.get("valor_contrato", 0)
                }
                for c in top_customers
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatísticas: {str(e)}")


@router.get("/dashboard/timeline")
async def get_timeline(days: int = 30):
    """Timeline de atividades dos últimos N dias"""
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        # Clientes criados por dia
        customers_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        customers_timeline = await customers_collection.aggregate(customers_pipeline).to_list(days)
        
        # Deals fechados por dia
        deals_pipeline = [
            {"$match": {
                "status": "won",
                "updated_at": {"$gte": start_date}
            }},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$updated_at"}},
                "count": {"$sum": 1},
                "value": {"$sum": "$value"}
            }},
            {"$sort": {"_id": 1}}
        ]
        deals_timeline = await deals_collection.aggregate(deals_pipeline).to_list(days)
        
        # Interações por dia
        interactions_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        interactions_timeline = await interactions_collection.aggregate(interactions_pipeline).to_list(days)
        
        return {
            "customers": [{"date": c["_id"], "count": c["count"]} for c in customers_timeline],
            "deals": [{"date": d["_id"], "count": d["count"], "value": d["value"]} for d in deals_timeline],
            "interactions": [{"date": i["_id"], "count": i["count"]} for i in interactions_timeline]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar timeline: {str(e)}")


@router.get("/dashboard/funnel")
async def get_sales_funnel():
    """Funil de vendas"""
    try:
        # Contagem por status
        leads = await customers_collection.count_documents({"status": "lead"})
        prospects = await customers_collection.count_documents({"status": "prospect"})
        clientes = await customers_collection.count_documents({"status": "cliente"})
        
        # Valor médio por deal
        pipeline = [
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "avg_value": {"$avg": "$value"},
                "total_value": {"$sum": "$value"}
            }}
        ]
        deals_by_status = await deals_collection.aggregate(pipeline).to_list(10)
        
        return {
            "funnel": [
                {"stage": "Leads", "count": leads, "percentage": 100},
                {"stage": "Prospects", "count": prospects, "percentage": (prospects/leads*100) if leads > 0 else 0},
                {"stage": "Clientes", "count": clientes, "percentage": (clientes/leads*100) if leads > 0 else 0}
            ],
            "deals_by_status": [
                {
                    "status": d["_id"],
                    "count": d["count"],
                    "avg_value": round(d.get("avg_value", 0), 2),
                    "total_value": round(d.get("total_value", 0), 2)
                }
                for d in deals_by_status
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar funil: {str(e)}")


@router.get("/dashboard/top-performers")
async def get_top_performers():
    """Top performers (responsáveis com mais resultados)"""
    try:
        # Deals ganhos por responsável
        pipeline = [
            {"$match": {"status": "won", "responsavel": {"$exists": True, "$ne": None}}},
            {"$group": {
                "_id": "$responsavel",
                "deals_won": {"$sum": 1},
                "total_value": {"$sum": "$value"}
            }},
            {"$sort": {"total_value": -1}},
            {"$limit": 10}
        ]
        top_deals = await deals_collection.aggregate(pipeline).to_list(10)
        
        # Clientes por responsável
        customer_pipeline = [
            {"$match": {"responsavel": {"$exists": True, "$ne": None}}},
            {"$group": {
                "_id": "$responsavel",
                "customers": {"$sum": 1}
            }},
            {"$sort": {"customers": -1}},
            {"$limit": 10}
        ]
        top_customers = await customers_collection.aggregate(customer_pipeline).to_list(10)
        
        return {
            "by_deals": [
                {
                    "responsavel": d["_id"],
                    "deals_won": d["deals_won"],
                    "total_value": round(d["total_value"], 2)
                }
                for d in top_deals
            ],
            "by_customers": [
                {
                    "responsavel": c["_id"],
                    "customers": c["customers"]
                }
                for c in top_customers
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar top performers: {str(e)}")


@router.get("/dashboard/alerts")
async def get_alerts():
    """Alertas e lembretes importantes"""
    try:
        alerts = []
        
        # Atividades vencidas
        overdue_activities = await activities_collection.find({
            "status": "pending",
            "due_date": {"$lt": datetime.now()}
        }).limit(10).to_list(10)
        
        for activity in overdue_activities:
            alerts.append({
                "type": "overdue_activity",
                "priority": "high",
                "message": f"Atividade vencida: {activity['title']}",
                "activity_id": str(activity["_id"]),
                "due_date": activity.get("due_date")
            })
        
        # Clientes sem interação há mais de 30 dias
        thirty_days_ago = datetime.now() - timedelta(days=30)
        inactive_customers = await customers_collection.find({
            "status": "cliente",
            "updated_at": {"$lt": thirty_days_ago}
        }).limit(10).to_list(10)
        
        for customer in inactive_customers:
            alerts.append({
                "type": "inactive_customer",
                "priority": "medium",
                "message": f"Cliente sem interação há 30+ dias: {customer['name']}",
                "customer_id": str(customer["_id"])
            })
        
        # Contratos próximos do vencimento (próximos 30 dias)
        thirty_days_ahead = datetime.now() + timedelta(days=30)
        expiring_contracts = await customers_collection.find({
            "data_fim_contrato": {
                "$gte": datetime.now().isoformat(),
                "$lte": thirty_days_ahead.isoformat()
            }
        }).limit(10).to_list(10)
        
        for customer in expiring_contracts:
            alerts.append({
                "type": "expiring_contract",
                "priority": "high",
                "message": f"Contrato vencendo em breve: {customer['name']}",
                "customer_id": str(customer["_id"]),
                "expiry_date": customer.get("data_fim_contrato")
            })
        
        # Leads sem follow-up há mais de 7 dias
        seven_days_ago = datetime.now() - timedelta(days=7)
        cold_leads = await customers_collection.find({
            "status": "lead",
            "created_at": {"$lt": seven_days_ago}
        }).limit(10).to_list(10)
        
        for lead in cold_leads:
            # Verificar se tem interações
            has_interaction = await interactions_collection.count_documents({
                "customer_id": str(lead["_id"])
            })
            if has_interaction == 0:
                alerts.append({
                    "type": "cold_lead",
                    "priority": "medium",
                    "message": f"Lead sem follow-up há 7+ dias: {lead['name']}",
                    "customer_id": str(lead["_id"])
                })
        
        # Ordenar por prioridade
        priority_order = {"high": 0, "medium": 1, "low": 2}
        alerts.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return {
            "total": len(alerts),
            "alerts": alerts[:20]  # Limitar a 20 alertas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar alertas: {str(e)}")
