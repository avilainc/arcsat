from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import BaseModel
from ..database import customers_collection, deals_collection, activities_collection, db
from collections import defaultdict

router = APIRouter()

class BIQuery(BaseModel):
    name: str
    description: str = ""
    data_sources: List[str] = []  # customers, deals, activities
    aggregation: List[dict] = []
    dimensions: List[str] = []  # Campos para agrupar
    metrics: List[str] = []  # Campos para calcular
    filters: dict = {}
    time_range: Optional[dict] = None  # {start: date, end: date, field: "created_at"}

@router.post("/bi/query")
async def execute_bi_query(query: BIQuery):
    """Executar query personalizada de BI"""
    # Selecionar collection
    collection_map = {
        "customers": customers_collection,
        "deals": deals_collection,
        "activities": activities_collection
    }
    
    results = {}
    for source in query.data_sources:
        collection = collection_map.get(source)
        if not collection:
            continue
        
        # Construir pipeline
        pipeline = []
        
        # Filtros
        match_stage = query.filters.copy() if query.filters else {}
        if query.time_range:
            field = query.time_range.get("field", "created_at")
            match_stage[field] = {
                "$gte": query.time_range.get("start"),
                "$lte": query.time_range.get("end")
            }
        
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        # Agregação personalizada ou padrão
        if query.aggregation:
            pipeline.extend(query.aggregation)
        else:
            # Agregação automática baseada em dimensions e metrics
            if query.dimensions:
                group_stage = {"_id": {}}
                for dim in query.dimensions:
                    group_stage["_id"][dim] = f"${dim}"
                
                # Adicionar métricas
                for metric in query.metrics:
                    if metric == "count":
                        group_stage["count"] = {"$sum": 1}
                    elif metric.startswith("sum_"):
                        field = metric.replace("sum_", "")
                        group_stage[metric] = {"$sum": f"${field}"}
                    elif metric.startswith("avg_"):
                        field = metric.replace("avg_", "")
                        group_stage[metric] = {"$avg": f"${field}"}
                
                pipeline.append({"$group": group_stage})
        
        # Executar
        cursor = collection.aggregate(pipeline)
        data = await cursor.to_list(length=10000)
        results[source] = data
    
    return {
        "query_name": query.name,
        "results": results,
        "executed_at": datetime.now()
    }

@router.get("/bi/cohort-analysis")
async def cohort_analysis(cohort_field: str = "created_at", metric: str = "retention"):
    """Análise de coorte de clientes"""
    # Agrupar clientes por mês de cadastro
    pipeline = [
        {
            "$group": {
                "_id": {
                    "year": {"$year": f"${cohort_field}"},
                    "month": {"$month": f"${cohort_field}"}
                },
                "customers": {"$push": "$$ROOT"}
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]
    
    cursor = customers_collection.aggregate(pipeline)
    cohorts = await cursor.to_list(length=100)
    
    cohort_data = []
    for cohort in cohorts:
        cohort_month = f"{cohort['_id']['year']}-{cohort['_id']['month']:02d}"
        cohort_size = len(cohort['customers'])
        
        # Calcular retenção (exemplo simplificado)
        active_customers = sum(1 for c in cohort['customers'] if c.get('status') == 'active')
        retention_rate = (active_customers / cohort_size * 100) if cohort_size > 0 else 0
        
        cohort_data.append({
            "cohort": cohort_month,
            "size": cohort_size,
            "active": active_customers,
            "retention_rate": round(retention_rate, 2)
        })
    
    return {
        "cohorts": cohort_data,
        "total_cohorts": len(cohort_data)
    }

@router.get("/bi/revenue-analysis")
async def revenue_analysis(period: str = "month"):
    """Análise de receita detalhada"""
    # Period: day, week, month, quarter, year
    date_format = {
        "day": "%Y-%m-%d",
        "week": "%Y-W%V",
        "month": "%Y-%m",
        "quarter": "%Y-Q",
        "year": "%Y"
    }
    
    group_by = {}
    if period == "day":
        group_by = {
            "year": {"$year": "$closed_at"},
            "month": {"$month": "$closed_at"},
            "day": {"$dayOfMonth": "$closed_at"}
        }
    elif period == "month":
        group_by = {
            "year": {"$year": "$closed_at"},
            "month": {"$month": "$closed_at"}
        }
    elif period == "year":
        group_by = {"year": {"$year": "$closed_at"}}
    
    pipeline = [
        {"$match": {"status": "won"}},
        {
            "$group": {
                "_id": group_by,
                "total_revenue": {"$sum": "$value"},
                "deals_count": {"$sum": 1},
                "avg_deal_value": {"$avg": "$value"},
                "max_deal_value": {"$max": "$value"},
                "min_deal_value": {"$min": "$value"}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    cursor = deals_collection.aggregate(pipeline)
    results = await cursor.to_list(length=1000)
    
    # Calcular crescimento mês a mês
    for i in range(1, len(results)):
        prev_revenue = results[i-1]["total_revenue"]
        curr_revenue = results[i]["total_revenue"]
        growth = ((curr_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        results[i]["growth_rate"] = round(growth, 2)
    
    # Totais
    total_revenue = sum(r["total_revenue"] for r in results)
    total_deals = sum(r["deals_count"] for r in results)
    
    return {
        "period": period,
        "data": results,
        "summary": {
            "total_revenue": total_revenue,
            "total_deals": total_deals,
            "avg_revenue_per_period": round(total_revenue / len(results), 2) if results else 0
        }
    }

@router.get("/bi/customer-lifetime-value")
async def customer_lifetime_value():
    """Calcular Customer Lifetime Value (CLV)"""
    # CLV = Valor médio de compra × Frequência de compra × Tempo de vida do cliente
    
    pipeline = [
        {
            "$lookup": {
                "from": "deals",
                "localField": "_id",
                "foreignField": "customer_id",
                "as": "deals"
            }
        },
        {
            "$addFields": {
                "won_deals": {
                    "$filter": {
                        "input": "$deals",
                        "as": "deal",
                        "cond": {"$eq": ["$$deal.status", "won"]}
                    }
                }
            }
        },
        {
            "$addFields": {
                "total_value": {"$sum": "$won_deals.value"},
                "deal_count": {"$size": "$won_deals"},
                "first_deal": {"$min": "$won_deals.created_at"},
                "last_deal": {"$max": "$won_deals.closed_at"}
            }
        },
        {
            "$match": {
                "deal_count": {"$gt": 0}
            }
        },
        {
            "$addFields": {
                "lifetime_days": {
                    "$divide": [
                        {"$subtract": ["$last_deal", "$first_deal"]},
                        86400000  # Converter ms para dias
                    ]
                },
                "avg_deal_value": {"$divide": ["$total_value", "$deal_count"]}
            }
        },
        {
            "$project": {
                "_id": 1,
                "name": 1,
                "total_value": 1,
                "deal_count": 1,
                "avg_deal_value": 1,
                "lifetime_days": 1,
                "clv": "$total_value"  # Simplificado
            }
        },
        {"$sort": {"clv": -1}},
        {"$limit": 100}
    ]
    
    # Nota: Esta query usa $lookup que pode ser pesada. Em produção, considere pre-computar
    cursor = customers_collection.aggregate(pipeline)
    customers = await cursor.to_list(length=100)
    
    # Converter ObjectId
    for customer in customers:
        customer["_id"] = str(customer["_id"])
    
    # Estatísticas gerais
    if customers:
        avg_clv = sum(c["clv"] for c in customers) / len(customers)
        max_clv = max(c["clv"] for c in customers)
        min_clv = min(c["clv"] for c in customers)
    else:
        avg_clv = max_clv = min_clv = 0
    
    return {
        "customers": customers,
        "summary": {
            "avg_clv": round(avg_clv, 2),
            "max_clv": round(max_clv, 2),
            "min_clv": round(min_clv, 2),
            "total_customers": len(customers)
        }
    }

@router.get("/bi/sales-forecast")
async def sales_forecast(months: int = 3):
    """Previsão de vendas usando média móvel"""
    # Buscar histórico dos últimos 12 meses
    twelve_months_ago = datetime.now() - timedelta(days=365)
    
    pipeline = [
        {
            "$match": {
                "status": "won",
                "closed_at": {"$gte": twelve_months_ago}
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$closed_at"},
                    "month": {"$month": "$closed_at"}
                },
                "revenue": {"$sum": "$value"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]
    
    cursor = deals_collection.aggregate(pipeline)
    historical_data = await cursor.to_list(length=12)
    
    if len(historical_data) < 3:
        return {
            "message": "Dados insuficientes para previsão (mínimo 3 meses)",
            "historical": historical_data,
            "forecast": []
        }
    
    # Calcular média móvel simples (3 meses)
    revenues = [d["revenue"] for d in historical_data]
    moving_avg = sum(revenues[-3:]) / 3
    
    # Calcular tendência (crescimento médio)
    if len(revenues) >= 2:
        growth_rates = []
        for i in range(1, len(revenues)):
            if revenues[i-1] > 0:
                rate = (revenues[i] - revenues[i-1]) / revenues[i-1]
                growth_rates.append(rate)
        
        avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0
    else:
        avg_growth = 0
    
    # Gerar previsão
    forecast = []
    current_date = datetime.now()
    forecast_value = moving_avg
    
    for i in range(1, months + 1):
        forecast_date = current_date + timedelta(days=30 * i)
        forecast_value = forecast_value * (1 + avg_growth)
        
        forecast.append({
            "year": forecast_date.year,
            "month": forecast_date.month,
            "predicted_revenue": round(forecast_value, 2),
            "confidence": "medium"  # Simplificado
        })
    
    return {
        "historical": historical_data,
        "forecast": forecast,
        "metrics": {
            "moving_average": round(moving_avg, 2),
            "avg_growth_rate": round(avg_growth * 100, 2)
        }
    }

@router.get("/bi/deal-velocity")
async def deal_velocity():
    """Velocidade de negócios - tempo médio por estágio"""
    pipeline = [
        {"$match": {"status": "won"}},
        {
            "$project": {
                "days_to_close": {
                    "$divide": [
                        {"$subtract": ["$closed_at", "$created_at"]},
                        86400000  # ms para dias
                    ]
                },
                "stage": 1,
                "value": 1
            }
        },
        {
            "$group": {
                "_id": "$stage",
                "avg_days": {"$avg": "$days_to_close"},
                "min_days": {"$min": "$days_to_close"},
                "max_days": {"$max": "$days_to_close"},
                "count": {"$sum": 1},
                "total_value": {"$sum": "$value"}
            }
        }
    ]
    
    cursor = deals_collection.aggregate(pipeline)
    results = await cursor.to_list(length=100)
    
    # Calcular velocidade geral
    total_deals = sum(r["count"] for r in results)
    total_days = sum(r["avg_days"] * r["count"] for r in results)
    avg_velocity = total_days / total_deals if total_deals > 0 else 0
    
    return {
        "by_stage": results,
        "overall": {
            "avg_days_to_close": round(avg_velocity, 2),
            "total_deals_analyzed": total_deals
        }
    }

@router.get("/bi/conversion-rates")
async def conversion_rates():
    """Taxas de conversão detalhadas por estágio"""
    # Contar deals por estágio
    pipeline = [
        {
            "$group": {
                "_id": "$stage",
                "total": {"$sum": 1},
                "won": {
                    "$sum": {"$cond": [{"$eq": ["$status", "won"]}, 1, 0]}
                },
                "lost": {
                    "$sum": {"$cond": [{"$eq": ["$status", "lost"]}, 1, 0]}
                }
            }
        }
    ]
    
    cursor = deals_collection.aggregate(pipeline)
    stages = await cursor.to_list(length=100)
    
    # Calcular taxas
    for stage in stages:
        stage["conversion_rate"] = round((stage["won"] / stage["total"] * 100), 2) if stage["total"] > 0 else 0
        stage["loss_rate"] = round((stage["lost"] / stage["total"] * 100), 2) if stage["total"] > 0 else 0
    
    # Taxa geral
    total_deals = sum(s["total"] for s in stages)
    total_won = sum(s["won"] for s in stages)
    overall_rate = (total_won / total_deals * 100) if total_deals > 0 else 0
    
    return {
        "by_stage": stages,
        "overall_conversion_rate": round(overall_rate, 2),
        "total_deals": total_deals
    }

@router.get("/bi/top-performers")
async def top_performers(metric: str = "revenue", limit: int = 10):
    """Top performers - vendedores, produtos, clientes"""
    if metric == "revenue":
        # Top clientes por receita
        pipeline = [
            {
                "$lookup": {
                    "from": "deals",
                    "localField": "_id",
                    "foreignField": "customer_id",
                    "as": "deals"
                }
            },
            {
                "$addFields": {
                    "total_revenue": {
                        "$sum": {
                            "$map": {
                                "input": "$deals",
                                "as": "deal",
                                "in": {
                                    "$cond": [
                                        {"$eq": ["$$deal.status", "won"]},
                                        "$$deal.value",
                                        0
                                    ]
                                }
                            }
                        }
                    }
                }
            },
            {"$match": {"total_revenue": {"$gt": 0}}},
            {"$sort": {"total_revenue": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "company": 1,
                    "total_revenue": 1
                }
            }
        ]
        
        cursor = customers_collection.aggregate(pipeline)
        results = await cursor.to_list(length=limit)
        
        for result in results:
            result["_id"] = str(result["_id"])
        
        return {
            "metric": "revenue",
            "top_performers": results
        }
    
    elif metric == "deals":
        # Top por número de negócios ganhos
        pipeline = [
            {"$match": {"status": "won"}},
            {
                "$group": {
                    "_id": "$customer_id",
                    "deals_count": {"$sum": 1},
                    "total_value": {"$sum": "$value"}
                }
            },
            {"$sort": {"deals_count": -1}},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "customers",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "customer"
                }
            },
            {"$unwind": "$customer"},
            {
                "$project": {
                    "customer_name": "$customer.name",
                    "deals_count": 1,
                    "total_value": 1
                }
            }
        ]
        
        cursor = deals_collection.aggregate(pipeline)
        results = await cursor.to_list(length=limit)
        
        for result in results:
            result["_id"] = str(result["_id"])
        
        return {
            "metric": "deals_count",
            "top_performers": results
        }
    
    else:
        raise HTTPException(status_code=400, detail="Métrica inválida. Use 'revenue' ou 'deals'")
