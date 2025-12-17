from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from bson import ObjectId
import schemas
from database import activities_collection, customers_collection, deals_collection
from models import activity_helper

router = APIRouter()

@router.get("/", response_model=List[schemas.Activity])
async def get_activities(skip: int = 0, limit: int = 100):
    activities = []
    async for activity in activities_collection.find().skip(skip).limit(limit):
        activities.append(activity_helper(activity))
    return activities

@router.get("/{activity_id}", response_model=schemas.Activity)
async def get_activity(activity_id: str):
    if not ObjectId.is_valid(activity_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    activity = await activities_collection.find_one({"_id": ObjectId(activity_id)})
    if activity is None:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    return activity_helper(activity)

@router.post("/", response_model=schemas.Activity)
async def create_activity(activity: schemas.ActivityCreate):
    # Verificar se o customer existe
    if not ObjectId.is_valid(activity.customer_id):
        raise HTTPException(status_code=400, detail="ID do cliente inválido")
    
    customer = await customers_collection.find_one({"_id": ObjectId(activity.customer_id)})
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Verificar se deal_id é válido (se fornecido)
    if activity.deal_id:
        if not ObjectId.is_valid(activity.deal_id):
            raise HTTPException(status_code=400, detail="ID do negócio inválido")
        deal = await deals_collection.find_one({"_id": ObjectId(activity.deal_id)})
        if not deal:
            raise HTTPException(status_code=404, detail="Negócio não encontrado")
    
    activity_dict = activity.model_dump()
    activity_dict["customer_id"] = ObjectId(activity.customer_id)
    if activity.deal_id:
        activity_dict["deal_id"] = ObjectId(activity.deal_id)
    activity_dict["created_at"] = datetime.utcnow()
    
    result = await activities_collection.insert_one(activity_dict)
    new_activity = await activities_collection.find_one({"_id": result.inserted_id})
    return activity_helper(new_activity)

@router.put("/{activity_id}", response_model=schemas.Activity)
async def update_activity(activity_id: str, activity: schemas.ActivityUpdate):
    if not ObjectId.is_valid(activity_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    update_data = {k: v for k, v in activity.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    result = await activities_collection.update_one(
        {"_id": ObjectId(activity_id)},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        existing = await activities_collection.find_one({"_id": ObjectId(activity_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Atividade não encontrada")
    
    updated_activity = await activities_collection.find_one({"_id": ObjectId(activity_id)})
    return activity_helper(updated_activity)

@router.delete("/{activity_id}")
async def delete_activity(activity_id: str):
    if not ObjectId.is_valid(activity_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    result = await activities_collection.delete_one({"_id": ObjectId(activity_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    
    return {"message": "Atividade deletada com sucesso"}
