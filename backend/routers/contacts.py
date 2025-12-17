from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from bson import ObjectId
import schemas
from database import contacts_collection, customers_collection
from models import contact_helper

router = APIRouter()

@router.get("/", response_model=List[schemas.Contact])
async def get_contacts(skip: int = 0, limit: int = 100):
    contacts = []
    async for contact in contacts_collection.find().skip(skip).limit(limit):
        contacts.append(contact_helper(contact))
    return contacts

@router.get("/{contact_id}", response_model=schemas.Contact)
async def get_contact(contact_id: str):
    if not ObjectId.is_valid(contact_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    contact = await contacts_collection.find_one({"_id": ObjectId(contact_id)})
    if contact is None:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    return contact_helper(contact)

@router.post("/", response_model=schemas.Contact)
async def create_contact(contact: schemas.ContactCreate):
    # Verificar se o customer existe
    if not ObjectId.is_valid(contact.customer_id):
        raise HTTPException(status_code=400, detail="ID do cliente inválido")
    
    customer = await customers_collection.find_one({"_id": ObjectId(contact.customer_id)})
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    contact_dict = contact.model_dump()
    contact_dict["customer_id"] = ObjectId(contact.customer_id)
    contact_dict["created_at"] = datetime.utcnow()
    
    result = await contacts_collection.insert_one(contact_dict)
    new_contact = await contacts_collection.find_one({"_id": result.inserted_id})
    return contact_helper(new_contact)

@router.put("/{contact_id}", response_model=schemas.Contact)
async def update_contact(contact_id: str, contact: schemas.ContactUpdate):
    if not ObjectId.is_valid(contact_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    update_data = {k: v for k, v in contact.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    result = await contacts_collection.update_one(
        {"_id": ObjectId(contact_id)},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        existing = await contacts_collection.find_one({"_id": ObjectId(contact_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Contato não encontrado")
    
    updated_contact = await contacts_collection.find_one({"_id": ObjectId(contact_id)})
    return contact_helper(updated_contact)

@router.delete("/{contact_id}")
async def delete_contact(contact_id: str):
    if not ObjectId.is_valid(contact_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    result = await contacts_collection.delete_one({"_id": ObjectId(contact_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    
    return {"message": "Contato deletado com sucesso"}
