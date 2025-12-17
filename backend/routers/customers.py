from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from bson import ObjectId
import schemas
from database import customers_collection
from models import customer_helper

router = APIRouter()

@router.get("/", response_model=List[schemas.Customer])
async def get_customers(skip: int = 0, limit: int = 100):
    customers = []
    async for customer in customers_collection.find().skip(skip).limit(limit):
        customers.append(customer_helper(customer))
    return customers

@router.get("/{customer_id}", response_model=schemas.Customer)
async def get_customer(customer_id: str):
    if not ObjectId.is_valid(customer_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    customer = await customers_collection.find_one({"_id": ObjectId(customer_id)})
    if customer is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return customer_helper(customer)

@router.post("/", response_model=schemas.Customer)
async def create_customer(customer: schemas.CustomerCreate):
    customer_dict = customer.model_dump()
    customer_dict["created_at"] = datetime.utcnow()
    customer_dict["updated_at"] = datetime.utcnow()
    
    result = await customers_collection.insert_one(customer_dict)
    new_customer = await customers_collection.find_one({"_id": result.inserted_id})
    return customer_helper(new_customer)

@router.put("/{customer_id}", response_model=schemas.Customer)
async def update_customer(customer_id: str, customer: schemas.CustomerUpdate):
    if not ObjectId.is_valid(customer_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    update_data = {k: v for k, v in customer.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await customers_collection.update_one(
        {"_id": ObjectId(customer_id)},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        existing = await customers_collection.find_one({"_id": ObjectId(customer_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    updated_customer = await customers_collection.find_one({"_id": ObjectId(customer_id)})
    return customer_helper(updated_customer)

@router.delete("/{customer_id}")
async def delete_customer(customer_id: str):
    if not ObjectId.is_valid(customer_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    result = await customers_collection.delete_one({"_id": ObjectId(customer_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return {"message": "Cliente deletado com sucesso"}
