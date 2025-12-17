from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from bson import ObjectId
import schemas
from database import deals_collection, customers_collection
from models import deal_helper

router = APIRouter()

@router.get("/", response_model=List[schemas.Deal])
async def get_deals(skip: int = 0, limit: int = 100):
    deals = []
    async for deal in deals_collection.find().skip(skip).limit(limit):
        deals.append(deal_helper(deal))
    return deals

@router.get("/{deal_id}", response_model=schemas.Deal)
async def get_deal(deal_id: str):
    if not ObjectId.is_valid(deal_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    deal = await deals_collection.find_one({"_id": ObjectId(deal_id)})
    if deal is None:
        raise HTTPException(status_code=404, detail="Negócio não encontrado")
    return deal_helper(deal)

@router.post("/", response_model=schemas.Deal)
async def create_deal(deal: schemas.DealCreate):
    # Verificar se o customer existe
    if not ObjectId.is_valid(deal.customer_id):
        raise HTTPException(status_code=400, detail="ID do cliente inválido")
    
    customer = await customers_collection.find_one({"_id": ObjectId(deal.customer_id)})
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    deal_dict = deal.model_dump()
    deal_dict["customer_id"] = ObjectId(deal.customer_id)
    deal_dict["created_at"] = datetime.utcnow()
    deal_dict["updated_at"] = datetime.utcnow()
    
    result = await deals_collection.insert_one(deal_dict)
    new_deal = await deals_collection.find_one({"_id": result.inserted_id})
    return deal_helper(new_deal)

@router.put("/{deal_id}", response_model=schemas.Deal)
async def update_deal(deal_id: str, deal: schemas.DealUpdate):
    if not ObjectId.is_valid(deal_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    update_data = {k: v for k, v in deal.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await deals_collection.update_one(
        {"_id": ObjectId(deal_id)},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        existing = await deals_collection.find_one({"_id": ObjectId(deal_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Negócio não encontrado")
    
    updated_deal = await deals_collection.find_one({"_id": ObjectId(deal_id)})
    return deal_helper(updated_deal)

@router.delete("/{deal_id}")
async def delete_deal(deal_id: str):
    if not ObjectId.is_valid(deal_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    result = await deals_collection.delete_one({"_id": ObjectId(deal_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Negócio não encontrado")
    
    return {"message": "Negócio deletado com sucesso"}
