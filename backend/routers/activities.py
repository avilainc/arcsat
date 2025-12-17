from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Activity])
def get_activities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    activities = db.query(models.Activity).offset(skip).limit(limit).all()
    return activities

@router.get("/{activity_id}", response_model=schemas.Activity)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if activity is None:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    return activity

@router.post("/", response_model=schemas.Activity)
def create_activity(activity: schemas.ActivityCreate, db: Session = Depends(get_db)):
    db_activity = models.Activity(**activity.model_dump())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.put("/{activity_id}", response_model=schemas.Activity)
def update_activity(activity_id: int, activity: schemas.ActivityUpdate, db: Session = Depends(get_db)):
    db_activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    for key, value in activity.model_dump(exclude_unset=True).items():
        setattr(db_activity, key, value)

    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.delete("/{activity_id}")
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    db_activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    db.delete(db_activity)
    db.commit()
    return {"message": "Atividade deletada com sucesso"}
