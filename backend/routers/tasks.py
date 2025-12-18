from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import BaseModel
from ..database import db

router = APIRouter()

# Coleção de tarefas
tasks_collection = db["tasks"]

class Task(BaseModel):
    title: str
    description: str = ""
    status: str = "todo"  # todo, in_progress, done
    priority: str = "medium"  # low, medium, high, urgent
    assigned_to: str = ""
    customer_id: Optional[str] = None
    deal_id: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: List[str] = []
    checklist: List[dict] = []  # [{text: str, completed: bool}]
    attachments: List[str] = []
    estimated_hours: float = 0.0
    actual_hours: float = 0.0

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None

class ChecklistItem(BaseModel):
    text: str
    completed: bool = False

@router.post("/tasks")
async def create_task(task: Task):
    """Criar nova tarefa"""
    task_dict = task.model_dump()
    task_dict["created_at"] = datetime.now()
    task_dict["updated_at"] = datetime.now()
    task_dict["completed_at"] = None
    
    result = await tasks_collection.insert_one(task_dict)
    task_dict["_id"] = str(result.inserted_id)
    
    return {
        "message": "Tarefa criada com sucesso",
        "task": task_dict
    }

@router.get("/tasks")
async def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    customer_id: Optional[str] = None,
    deal_id: Optional[str] = None,
    overdue: bool = False,
    page: int = 1,
    per_page: int = 50
):
    """Listar tarefas com filtros"""
    query = {}
    
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    if assigned_to:
        query["assigned_to"] = assigned_to
    if customer_id:
        query["customer_id"] = customer_id
    if deal_id:
        query["deal_id"] = deal_id
    if overdue:
        query["due_date"] = {"$lt": datetime.now()}
        query["status"] = {"$ne": "done"}
    
    # Paginação
    skip = (page - 1) * per_page
    
    cursor = tasks_collection.find(query).sort("created_at", -1).skip(skip).limit(per_page)
    tasks = await cursor.to_list(length=per_page)
    
    total = await tasks_collection.count_documents(query)
    
    # Converter ObjectId para string
    for task in tasks:
        task["_id"] = str(task["_id"])
    
    return {
        "tasks": tasks,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }

@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Obter tarefa por ID"""
    task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    task["_id"] = str(task["_id"])
    return task

@router.put("/tasks/{task_id}")
async def update_task(task_id: str, task_update: TaskUpdate):
    """Atualizar tarefa"""
    update_data = {k: v for k, v in task_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
    
    update_data["updated_at"] = datetime.now()
    
    # Se marcando como done, adicionar data de conclusão
    if update_data.get("status") == "done":
        update_data["completed_at"] = datetime.now()
    
    result = await tasks_collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    updated_task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    updated_task["_id"] = str(updated_task["_id"])
    
    return {
        "message": "Tarefa atualizada com sucesso",
        "task": updated_task
    }

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Deletar tarefa"""
    result = await tasks_collection.delete_one({"_id": ObjectId(task_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    return {"message": "Tarefa deletada com sucesso"}

@router.post("/tasks/{task_id}/checklist")
async def add_checklist_item(task_id: str, item: ChecklistItem):
    """Adicionar item ao checklist"""
    task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    checklist = task.get("checklist", [])
    checklist.append(item.model_dump())
    
    await tasks_collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"checklist": checklist, "updated_at": datetime.now()}}
    )
    
    return {
        "message": "Item adicionado ao checklist",
        "checklist": checklist
    }

@router.put("/tasks/{task_id}/checklist/{item_index}")
async def toggle_checklist_item(task_id: str, item_index: int):
    """Marcar/desmarcar item do checklist"""
    task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    checklist = task.get("checklist", [])
    if item_index < 0 or item_index >= len(checklist):
        raise HTTPException(status_code=400, detail="Índice inválido")
    
    checklist[item_index]["completed"] = not checklist[item_index].get("completed", False)
    
    await tasks_collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"checklist": checklist, "updated_at": datetime.now()}}
    )
    
    return {
        "message": "Item do checklist atualizado",
        "checklist": checklist
    }

@router.delete("/tasks/{task_id}/checklist/{item_index}")
async def remove_checklist_item(task_id: str, item_index: int):
    """Remover item do checklist"""
    task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    checklist = task.get("checklist", [])
    if item_index < 0 or item_index >= len(checklist):
        raise HTTPException(status_code=400, detail="Índice inválido")
    
    checklist.pop(item_index)
    
    await tasks_collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"checklist": checklist, "updated_at": datetime.now()}}
    )
    
    return {
        "message": "Item removido do checklist",
        "checklist": checklist
    }

@router.get("/tasks/stats/summary")
async def get_tasks_summary():
    """Resumo de estatísticas de tarefas"""
    pipeline = [
        {
            "$facet": {
                "by_status": [
                    {"$group": {"_id": "$status", "count": {"$sum": 1}}}
                ],
                "by_priority": [
                    {"$group": {"_id": "$priority", "count": {"$sum": 1}}}
                ],
                "overdue": [
                    {
                        "$match": {
                            "due_date": {"$lt": datetime.now()},
                            "status": {"$ne": "done"}
                        }
                    },
                    {"$count": "count"}
                ],
                "due_today": [
                    {
                        "$match": {
                            "due_date": {
                                "$gte": datetime.now().replace(hour=0, minute=0, second=0),
                                "$lt": datetime.now().replace(hour=23, minute=59, second=59)
                            },
                            "status": {"$ne": "done"}
                        }
                    },
                    {"$count": "count"}
                ],
                "total_hours": [
                    {
                        "$group": {
                            "_id": None,
                            "estimated": {"$sum": "$estimated_hours"},
                            "actual": {"$sum": "$actual_hours"}
                        }
                    }
                ]
            }
        }
    ]
    
    result = await tasks_collection.aggregate(pipeline).to_list(length=1)
    
    if not result:
        return {
            "by_status": {},
            "by_priority": {},
            "overdue": 0,
            "due_today": 0,
            "total_hours": {"estimated": 0, "actual": 0}
        }
    
    data = result[0]
    
    return {
        "by_status": {item["_id"]: item["count"] for item in data.get("by_status", [])},
        "by_priority": {item["_id"]: item["count"] for item in data.get("by_priority", [])},
        "overdue": data.get("overdue", [{}])[0].get("count", 0),
        "due_today": data.get("due_today", [{}])[0].get("count", 0),
        "total_hours": data.get("total_hours", [{}])[0] if data.get("total_hours") else {"estimated": 0, "actual": 0}
    }

@router.get("/tasks/board/kanban")
async def get_tasks_kanban(assigned_to: Optional[str] = None):
    """Obter tarefas em formato Kanban"""
    query = {}
    if assigned_to:
        query["assigned_to"] = assigned_to
    
    cursor = tasks_collection.find(query).sort("priority", -1)
    tasks = await cursor.to_list(length=1000)
    
    # Converter ObjectId para string
    for task in tasks:
        task["_id"] = str(task["_id"])
    
    # Organizar por status
    kanban = {
        "todo": [t for t in tasks if t.get("status") == "todo"],
        "in_progress": [t for t in tasks if t.get("status") == "in_progress"],
        "done": [t for t in tasks if t.get("status") == "done"]
    }
    
    return kanban
