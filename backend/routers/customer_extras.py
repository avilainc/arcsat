from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from datetime import datetime
from bson import ObjectId
from ..database import attachments_collection, interactions_collection, notes_collection
from ..schemas import (
    AttachmentCreate, Attachment,
    InteractionCreate, Interaction,
    NoteCreate, Note
)
import base64

router = APIRouter()

# ============= ANEXOS =============

@router.post("/attachments", response_model=Attachment)
async def create_attachment(attachment: AttachmentCreate):
    """Criar novo anexo para um cliente"""
    attachment_dict = attachment.model_dump()
    attachment_dict["created_at"] = datetime.utcnow()

    result = await attachments_collection.insert_one(attachment_dict)
    new_attachment = await attachments_collection.find_one({"_id": result.inserted_id})

    return Attachment(**new_attachment)


@router.post("/attachments/upload/{customer_id}")
async def upload_file(customer_id: str, file: UploadFile = File(...)):
    """Upload de arquivo para um cliente"""
    # Lê o conteúdo do arquivo
    contents = await file.read()
    file_base64 = base64.b64encode(contents).decode('utf-8')

    attachment_dict = {
        "customer_id": customer_id,
        "filename": file.filename,
        "file_type": file.content_type,
        "file_size": len(contents),
        "file_data": file_base64,
        "created_at": datetime.utcnow()
    }

    result = await attachments_collection.insert_one(attachment_dict)
    new_attachment = await attachments_collection.find_one({"_id": result.inserted_id})

    return Attachment(**new_attachment)


@router.get("/attachments/customer/{customer_id}", response_model=List[Attachment])
async def get_customer_attachments(customer_id: str):
    """Listar anexos de um cliente"""
    attachments = await attachments_collection.find({"customer_id": customer_id}).to_list(100)
    return [Attachment(**attachment) for attachment in attachments]


@router.delete("/attachments/{attachment_id}")
async def delete_attachment(attachment_id: str):
    """Deletar anexo"""
    if not ObjectId.is_valid(attachment_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = await attachments_collection.delete_one({"_id": ObjectId(attachment_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Anexo não encontrado")

    return {"message": "Anexo deletado com sucesso"}


# ============= INTERAÇÕES =============

@router.post("/interactions", response_model=Interaction)
async def create_interaction(interaction: InteractionCreate):
    """Registrar nova interação com cliente"""
    interaction_dict = interaction.model_dump()
    interaction_dict["created_at"] = datetime.utcnow()

    result = await interactions_collection.insert_one(interaction_dict)
    new_interaction = await interactions_collection.find_one({"_id": result.inserted_id})

    return Interaction(**new_interaction)


@router.get("/interactions/customer/{customer_id}", response_model=List[Interaction])
async def get_customer_interactions(customer_id: str):
    """Listar histórico de interações de um cliente"""
    interactions = await interactions_collection.find(
        {"customer_id": customer_id}
    ).sort("data", -1).to_list(100)

    return [Interaction(**interaction) for interaction in interactions]


@router.put("/interactions/{interaction_id}", response_model=Interaction)
async def update_interaction(interaction_id: str, interaction: InteractionCreate):
    """Atualizar interação"""
    if not ObjectId.is_valid(interaction_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    interaction_dict = interaction.model_dump()

    result = await interactions_collection.update_one(
        {"_id": ObjectId(interaction_id)},
        {"$set": interaction_dict}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Interação não encontrada")

    updated_interaction = await interactions_collection.find_one({"_id": ObjectId(interaction_id)})
    return Interaction(**updated_interaction)


@router.delete("/interactions/{interaction_id}")
async def delete_interaction(interaction_id: str):
    """Deletar interação"""
    if not ObjectId.is_valid(interaction_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = await interactions_collection.delete_one({"_id": ObjectId(interaction_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Interação não encontrada")

    return {"message": "Interação deletada com sucesso"}


# ============= NOTAS =============

@router.post("/notes", response_model=Note)
async def create_note(note: NoteCreate):
    """Criar nova nota para um cliente"""
    note_dict = note.model_dump()
    note_dict["created_at"] = datetime.utcnow()

    result = await notes_collection.insert_one(note_dict)
    new_note = await notes_collection.find_one({"_id": result.inserted_id})

    return Note(**new_note)


@router.get("/notes/customer/{customer_id}", response_model=List[Note])
async def get_customer_notes(customer_id: str):
    """Listar notas de um cliente"""
    notes = await notes_collection.find(
        {"customer_id": customer_id}
    ).sort([("pinned", -1), ("created_at", -1)]).to_list(100)

    return [Note(**note) for note in notes]


@router.put("/notes/{note_id}", response_model=Note)
async def update_note(note_id: str, note: NoteCreate):
    """Atualizar nota"""
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    note_dict = note.model_dump()
    note_dict["updated_at"] = datetime.utcnow()

    result = await notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": note_dict}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Nota não encontrada")

    updated_note = await notes_collection.find_one({"_id": ObjectId(note_id)})
    return Note(**updated_note)


@router.put("/notes/{note_id}/pin")
async def toggle_pin_note(note_id: str):
    """Fixar/desafixar nota"""
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    note = await notes_collection.find_one({"_id": ObjectId(note_id)})
    if not note:
        raise HTTPException(status_code=404, detail="Nota não encontrada")

    new_pinned = not note.get("pinned", False)

    await notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": {"pinned": new_pinned}}
    )

    return {"pinned": new_pinned}


@router.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    """Deletar nota"""
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = await notes_collection.delete_one({"_id": ObjectId(note_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Nota não encontrada")

    return {"message": "Nota deletada com sucesso"}
