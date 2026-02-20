from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import BaseModel
from ..database import db, customers_collection, deals_collection, activities_collection

router = APIRouter()

# Coleção para dashboards personalizados
dashboards_collection = db["custom_dashboards"]
widgets_collection = db["dashboard_widgets"]

class Widget(BaseModel):
    type: str  # chart, metric, table, list, map, calendar
    title: str
    data_source: str  # customers, deals, activities, custom
    visualization: str  # line, bar, pie, donut, area, number, progress, heatmap
    query: dict = {}  # Filtros MongoDB
    aggregation: List[dict] = []  # Pipeline de agregação
    config: dict = {}  # Configurações específicas (cores, labels, etc)
    position: dict = {"x": 0, "y": 0, "w": 6, "h": 4}  # Grid layout
    refresh_interval: int = 300  # Segundos (5 min padrão)

class Dashboard(BaseModel):
    name: str
    description: str = ""
    user_id: str = ""  # Se vazio, dashboard público
    widgets: List[str] = []  # IDs dos widgets
    layout: dict = {}  # Configuração do grid
    filters: dict = {}  # Filtros globais
    is_default: bool = False
    shared_with: List[str] = []  # IDs de usuários

@router.post("/dashboards")
async def create_dashboard(dashboard: Dashboard):
    """Criar dashboard personalizado"""
    dashboard_dict = dashboard.model_dump()
    dashboard_dict["created_at"] = datetime.now()
    dashboard_dict["updated_at"] = datetime.now()
    
    result = await dashboards_collection.insert_one(dashboard_dict)
    dashboard_dict["_id"] = str(result.inserted_id)
    
    return {
        "message": "Dashboard criado com sucesso",
        "dashboard": dashboard_dict
    }

@router.get("/dashboards")
async def list_dashboards(user_id: Optional[str] = None):
    """Listar dashboards"""
    query = {}
    if user_id:
        query["$or"] = [
            {"user_id": user_id},
            {"user_id": ""},  # Públicos
            {"shared_with": user_id}
        ]
    
    cursor = dashboards_collection.find(query).sort("created_at", -1)
    dashboards = await cursor.to_list(length=100)
    
    for dashboard in dashboards:
        dashboard["_id"] = str(dashboard["_id"])
    
    return {"dashboards": dashboards, "total": len(dashboards)}

@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(dashboard_id: str):
    """Obter dashboard por ID"""
    dashboard = await dashboards_collection.find_one({"_id": ObjectId(dashboard_id)})
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    
    dashboard["_id"] = str(dashboard["_id"])
    
    # Buscar widgets
    widget_ids = [ObjectId(wid) for wid in dashboard.get("widgets", [])]
    if widget_ids:
        cursor = widgets_collection.find({"_id": {"$in": widget_ids}})
        widgets = await cursor.to_list(length=100)
        for widget in widgets:
            widget["_id"] = str(widget["_id"])
        dashboard["widgets_data"] = widgets
    
    return dashboard

@router.put("/dashboards/{dashboard_id}")
async def update_dashboard(dashboard_id: str, dashboard: Dashboard):
    """Atualizar dashboard"""
    update_data = dashboard.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    
    result = await dashboards_collection.update_one(
        {"_id": ObjectId(dashboard_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    
    return {"message": "Dashboard atualizado com sucesso"}

@router.delete("/dashboards/{dashboard_id}")
async def delete_dashboard(dashboard_id: str):
    """Deletar dashboard"""
    result = await dashboards_collection.delete_one({"_id": ObjectId(dashboard_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    
    return {"message": "Dashboard deletado com sucesso"}

@router.post("/widgets")
async def create_widget(widget: Widget):
    """Criar widget"""
    widget_dict = widget.model_dump()
    widget_dict["created_at"] = datetime.now()
    widget_dict["updated_at"] = datetime.now()
    
    result = await widgets_collection.insert_one(widget_dict)
    widget_dict["_id"] = str(result.inserted_id)
    
    return {
        "message": "Widget criado com sucesso",
        "widget": widget_dict
    }

@router.get("/widgets/{widget_id}")
async def get_widget(widget_id: str):
    """Obter widget por ID"""
    widget = await widgets_collection.find_one({"_id": ObjectId(widget_id)})
    if not widget:
        raise HTTPException(status_code=404, detail="Widget não encontrado")
    
    widget["_id"] = str(widget["_id"])
    return widget

@router.get("/widgets/{widget_id}/data")
async def get_widget_data(widget_id: str, filters: Optional[dict] = None):
    """Obter dados do widget"""
    widget = await widgets_collection.find_one({"_id": ObjectId(widget_id)})
    if not widget:
        raise HTTPException(status_code=404, detail="Widget não encontrado")
    
    # Selecionar collection baseado no data_source
    collection_map = {
        "customers": customers_collection,
        "deals": deals_collection,
        "activities": activities_collection
    }
    
    collection = collection_map.get(widget.get("data_source"))
    if not collection:
        raise HTTPException(status_code=400, detail="Data source inválido")
    
    # Aplicar filtros
    query = widget.get("query", {})
    if filters:
        query.update(filters)
    
    # Executar agregação ou query simples
    if widget.get("aggregation"):
        pipeline = widget["aggregation"]
        if query:
            pipeline.insert(0, {"$match": query})
        
        cursor = collection.aggregate(pipeline)
        data = await cursor.to_list(length=1000)
    else:
        cursor = collection.find(query).limit(100)
        data = await cursor.to_list(length=100)
        
        # Converter ObjectId para string
        for item in data:
            if "_id" in item:
                item["_id"] = str(item["_id"])
    
    return {
        "widget_id": widget_id,
        "data": data,
        "generated_at": datetime.now()
    }

@router.put("/widgets/{widget_id}")
async def update_widget(widget_id: str, widget: Widget):
    """Atualizar widget"""
    update_data = widget.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    
    result = await widgets_collection.update_one(
        {"_id": ObjectId(widget_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Widget não encontrado")
    
    return {"message": "Widget atualizado com sucesso"}

@router.delete("/widgets/{widget_id}")
async def delete_widget(widget_id: str):
    """Deletar widget"""
    result = await widgets_collection.delete_one({"_id": ObjectId(widget_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Widget não encontrado")
    
    # Remover widget de todos os dashboards
    await dashboards_collection.update_many(
        {"widgets": widget_id},
        {"$pull": {"widgets": widget_id}}
    )
    
    return {"message": "Widget deletado com sucesso"}

@router.get("/dashboards/templates/list")
async def get_dashboard_templates():
    """Templates pré-configurados de dashboards"""
    templates = [
        {
            "name": "Visão Executiva",
            "description": "KPIs principais e métricas de alto nível",
            "widgets": [
                {
                    "type": "metric",
                    "title": "Total de Clientes",
                    "data_source": "customers",
                    "visualization": "number",
                    "aggregation": [{"$count": "total"}],
                    "position": {"x": 0, "y": 0, "w": 3, "h": 2}
                },
                {
                    "type": "metric",
                    "title": "Negócios Ativos",
                    "data_source": "deals",
                    "visualization": "number",
                    "query": {"status": "open"},
                    "aggregation": [{"$match": {"status": "open"}}, {"$count": "total"}],
                    "position": {"x": 3, "y": 0, "w": 3, "h": 2}
                },
                {
                    "type": "chart",
                    "title": "Receita por Mês",
                    "data_source": "deals",
                    "visualization": "bar",
                    "aggregation": [
                        {"$match": {"status": "won"}},
                        {"$group": {
                            "_id": {"$month": "$closed_at"},
                            "total": {"$sum": "$value"}
                        }},
                        {"$sort": {"_id": 1}}
                    ],
                    "position": {"x": 0, "y": 2, "w": 6, "h": 4}
                }
            ]
        },
        {
            "name": "Análise de Vendas",
            "description": "Funil de vendas e performance comercial",
            "widgets": [
                {
                    "type": "chart",
                    "title": "Funil de Vendas",
                    "data_source": "deals",
                    "visualization": "donut",
                    "aggregation": [
                        {"$group": {
                            "_id": "$stage",
                            "count": {"$sum": 1}
                        }}
                    ],
                    "position": {"x": 0, "y": 0, "w": 4, "h": 4}
                },
                {
                    "type": "chart",
                    "title": "Taxa de Conversão",
                    "data_source": "deals",
                    "visualization": "progress",
                    "aggregation": [
                        {"$group": {
                            "_id": "$status",
                            "count": {"$sum": 1}
                        }}
                    ],
                    "position": {"x": 4, "y": 0, "w": 2, "h": 4}
                }
            ]
        },
        {
            "name": "Gestão de Clientes",
            "description": "Análise de base de clientes e segmentação",
            "widgets": [
                {
                    "type": "chart",
                    "title": "Clientes por Categoria",
                    "data_source": "customers",
                    "visualization": "pie",
                    "aggregation": [
                        {"$group": {
                            "_id": "$categoria",
                            "count": {"$sum": 1}
                        }}
                    ],
                    "position": {"x": 0, "y": 0, "w": 4, "h": 4}
                },
                {
                    "type": "chart",
                    "title": "Clientes por Status",
                    "data_source": "customers",
                    "visualization": "bar",
                    "aggregation": [
                        {"$group": {
                            "_id": "$status",
                            "count": {"$sum": 1}
                        }}
                    ],
                    "position": {"x": 4, "y": 0, "w": 4, "h": 4}
                }
            ]
        },
        {
            "name": "Produtividade",
            "description": "Atividades e tarefas da equipe",
            "widgets": [
                {
                    "type": "metric",
                    "title": "Atividades Hoje",
                    "data_source": "activities",
                    "visualization": "number",
                    "query": {
                        "due_date": {
                            "$gte": datetime.now().replace(hour=0, minute=0, second=0),
                            "$lt": datetime.now().replace(hour=23, minute=59, second=59)
                        }
                    },
                    "position": {"x": 0, "y": 0, "w": 3, "h": 2}
                },
                {
                    "type": "chart",
                    "title": "Atividades por Tipo",
                    "data_source": "activities",
                    "visualization": "donut",
                    "aggregation": [
                        {"$group": {
                            "_id": "$type",
                            "count": {"$sum": 1}
                        }}
                    ],
                    "position": {"x": 3, "y": 0, "w": 3, "h": 4}
                }
            ]
        }
    ]
    
    return {"templates": templates, "total": len(templates)}

@router.post("/dashboards/from-template")
async def create_dashboard_from_template(template_name: str, user_id: str):
    """Criar dashboard a partir de template"""
    templates = await get_dashboard_templates()
    
    template = next((t for t in templates["templates"] if t["name"] == template_name), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    # Criar widgets
    widget_ids = []
    for widget_data in template["widgets"]:
        widget = Widget(**widget_data)
        result = await create_widget(widget)
        widget_ids.append(result["widget"]["_id"])
    
    # Criar dashboard
    dashboard = Dashboard(
        name=template["name"],
        description=template["description"],
        user_id=user_id,
        widgets=widget_ids
    )
    
    return await create_dashboard(dashboard)
