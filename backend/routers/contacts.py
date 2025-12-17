from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Contact])
def get_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = db.query(models.Contact).offset(skip).limit(limit).all()
    return contacts

@router.get("/{contact_id}", response_model=schemas.Contact)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    return contact

@router.post("/", response_model=schemas.Contact)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = models.Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@router.put("/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db)):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    for key, value in contact.model_dump(exclude_unset=True).items():
        setattr(db_contact, key, value)

    db.commit()
    db.refresh(db_contact)
    return db_contact

@router.delete("/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    db.delete(db_contact)
    db.commit()
    return {"message": "Contato deletado com sucesso"}
