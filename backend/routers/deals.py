from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Deal])
def get_deals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    deals = db.query(models.Deal).offset(skip).limit(limit).all()
    return deals

@router.get("/{deal_id}", response_model=schemas.Deal)
def get_deal(deal_id: int, db: Session = Depends(get_db)):
    deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(status_code=404, detail="Negócio não encontrado")
    return deal

@router.post("/", response_model=schemas.Deal)
def create_deal(deal: schemas.DealCreate, db: Session = Depends(get_db)):
    db_deal = models.Deal(**deal.model_dump())
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    return db_deal

@router.put("/{deal_id}", response_model=schemas.Deal)
def update_deal(deal_id: int, deal: schemas.DealUpdate, db: Session = Depends(get_db)):
    db_deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if db_deal is None:
        raise HTTPException(status_code=404, detail="Negócio não encontrado")

    for key, value in deal.model_dump(exclude_unset=True).items():
        setattr(db_deal, key, value)

    db.commit()
    db.refresh(db_deal)
    return db_deal

@router.delete("/{deal_id}")
def delete_deal(deal_id: int, db: Session = Depends(get_db)):
    db_deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if db_deal is None:
        raise HTTPException(status_code=404, detail="Negócio não encontrado")

    db.delete(db_deal)
    db.commit()
    return {"message": "Negócio deletado com sucesso"}
