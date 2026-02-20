from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import BaseModel
from ..database import customers_collection, activities_collection, db
import httpx
import os

router = APIRouter()

# Coleção para mensagens WhatsApp
whatsapp_messages_collection = db["whatsapp_messages"]
whatsapp_templates_collection = db["whatsapp_templates"]

# Configurações WhatsApp Business API
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v18.0")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")

class WhatsAppMessage(BaseModel):
    to: str  # Número com código do país (ex: 5511999999999)
    type: str = "text"  # text, template, image, document, video
    content: str = ""
    template_name: Optional[str] = None
    template_params: List[str] = []
    customer_id: Optional[str] = None
    media_url: Optional[str] = None

class WhatsAppTemplate(BaseModel):
    name: str
    category: str  # marketing, utility, authentication
    language: str = "pt_BR"
    header: Optional[str] = None
    body: str
    footer: Optional[str] = None
    buttons: List[dict] = []  # [{type: "URL", text: "Visitar", url: "https://..."}]
    variables: List[str] = []

class WhatsAppCampaign(BaseModel):
    name: str
    template_name: str
    customer_filter: dict = {}
    schedule_date: Optional[datetime] = None

@router.post("/whatsapp/send")
async def send_whatsapp_message(message: WhatsAppMessage, background_tasks: BackgroundTasks):
    """Enviar mensagem WhatsApp"""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        raise HTTPException(status_code=400, detail="WhatsApp API não configurado")
    
    try:
        # Construir payload baseado no tipo
        if message.type == "text":
            payload = {
                "messaging_product": "whatsapp",
                "to": message.to,
                "type": "text",
                "text": {"body": message.content}
            }
        elif message.type == "template":
            # Mensagem via template aprovado
            components = []
            if message.template_params:
                components.append({
                    "type": "body",
                    "parameters": [{"type": "text", "text": param} for param in message.template_params]
                })
            
            payload = {
                "messaging_product": "whatsapp",
                "to": message.to,
                "type": "template",
                "template": {
                    "name": message.template_name,
                    "language": {"code": "pt_BR"},
                    "components": components
                }
            }
        elif message.type in ["image", "document", "video"]:
            payload = {
                "messaging_product": "whatsapp",
                "to": message.to,
                "type": message.type,
                message.type: {"link": message.media_url}
            }
        else:
            raise HTTPException(status_code=400, detail="Tipo de mensagem inválido")
        
        # Enviar via API do WhatsApp
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_ID}/messages",
                headers={
                    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30.0
            )
            
            response.raise_for_status()
            result = response.json()
        
        # Salvar mensagem no banco
        message_record = {
            "to": message.to,
            "type": message.type,
            "content": message.content,
            "template_name": message.template_name,
            "customer_id": message.customer_id,
            "status": "sent",
            "whatsapp_message_id": result.get("messages", [{}])[0].get("id"),
            "sent_at": datetime.now(),
            "created_at": datetime.now()
        }
        await whatsapp_messages_collection.insert_one(message_record)
        
        # Registrar atividade se customer_id fornecido
        if message.customer_id:
            activity = {
                "customer_id": message.customer_id,
                "type": "whatsapp",
                "description": f"WhatsApp enviado: {message.content[:50]}...",
                "status": "completed",
                "due_date": datetime.now(),
                "created_at": datetime.now()
            }
            await activities_collection.insert_one(activity)
        
        return {
            "message": "WhatsApp enviado com sucesso",
            "to": message.to,
            "whatsapp_id": result.get("messages", [{}])[0].get("id")
        }
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Erro WhatsApp API: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar WhatsApp: {str(e)}")

@router.post("/whatsapp/templates")
async def create_whatsapp_template(template: WhatsAppTemplate):
    """Criar template WhatsApp (precisa ser aprovado pelo Facebook)"""
    template_dict = template.model_dump()
    template_dict["status"] = "pending"  # pending, approved, rejected
    template_dict["created_at"] = datetime.now()
    
    result = await whatsapp_templates_collection.insert_one(template_dict)
    template_dict["_id"] = str(result.inserted_id)
    
    return {
        "message": "Template criado. Aguarde aprovação do Facebook.",
        "template": template_dict
    }

@router.get("/whatsapp/templates")
async def list_whatsapp_templates(status: Optional[str] = None):
    """Listar templates WhatsApp"""
    query = {}
    if status:
        query["status"] = status
    
    cursor = whatsapp_templates_collection.find(query)
    templates = await cursor.to_list(length=100)
    
    for template in templates:
        template["_id"] = str(template["_id"])
    
    return {"templates": templates, "total": len(templates)}

@router.get("/whatsapp/templates/{template_id}")
async def get_whatsapp_template(template_id: str):
    """Obter template WhatsApp por ID"""
    template = await whatsapp_templates_collection.find_one({"_id": ObjectId(template_id)})
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    template["_id"] = str(template["_id"])
    return template

@router.post("/whatsapp/send-template")
async def send_template_whatsapp(
    template_name: str,
    customer_id: str,
    params: List[str] = [],
    background_tasks: BackgroundTasks = None
):
    """Enviar WhatsApp usando template para um cliente"""
    # Buscar cliente
    customer = await customers_collection.find_one({"_id": ObjectId(customer_id)})
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    phone = customer.get('phone', '').replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
    if not phone.startswith('55'):
        phone = f"55{phone}"
    
    message = WhatsAppMessage(
        to=phone,
        type="template",
        template_name=template_name,
        template_params=params,
        customer_id=customer_id
    )
    
    return await send_whatsapp_message(message, background_tasks)

@router.post("/whatsapp/campaign")
async def create_whatsapp_campaign(campaign: WhatsAppCampaign):
    """Criar campanha WhatsApp para múltiplos clientes"""
    # Buscar template
    template = await whatsapp_templates_collection.find_one({"name": campaign.template_name})
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    if template.get("status") != "approved":
        raise HTTPException(status_code=400, detail="Template precisa estar aprovado")
    
    # Buscar clientes pelo filtro
    cursor = customers_collection.find(campaign.customer_filter)
    customers = await cursor.to_list(length=1000)
    
    if not customers:
        raise HTTPException(status_code=404, detail="Nenhum cliente encontrado")
    
    scheduled_messages = []
    for customer in customers:
        phone = customer.get('phone', '').replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
        if not phone.startswith('55'):
            phone = f"55{phone}"
        
        scheduled_messages.append({
            "customer_id": str(customer['_id']),
            "phone": phone,
            "template_name": campaign.template_name,
            "scheduled_for": campaign.schedule_date or datetime.now()
        })
    
    return {
        "message": "Campanha WhatsApp criada",
        "campaign_name": campaign.name,
        "total_messages": len(scheduled_messages),
        "scheduled_for": campaign.schedule_date or "Imediatamente",
        "preview": scheduled_messages[:3]
    }

@router.get("/whatsapp/messages")
async def list_whatsapp_messages(
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    per_page: int = 50
):
    """Listar mensagens WhatsApp"""
    query = {}
    if customer_id:
        query["customer_id"] = customer_id
    if status:
        query["status"] = status
    
    skip = (page - 1) * per_page
    cursor = whatsapp_messages_collection.find(query).sort("created_at", -1).skip(skip).limit(per_page)
    messages = await cursor.to_list(length=per_page)
    
    total = await whatsapp_messages_collection.count_documents(query)
    
    for message in messages:
        message["_id"] = str(message["_id"])
    
    return {
        "messages": messages,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }

@router.post("/whatsapp/webhook")
async def whatsapp_webhook(payload: dict):
    """Webhook para receber atualizações do WhatsApp"""
    # Processar status de mensagens (delivered, read, failed)
    if payload.get("entry"):
        for entry in payload["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                # Atualizar status de mensagens
                if value.get("statuses"):
                    for status_update in value["statuses"]:
                        message_id = status_update.get("id")
                        status = status_update.get("status")
                        
                        await whatsapp_messages_collection.update_one(
                            {"whatsapp_message_id": message_id},
                            {"$set": {"status": status, "updated_at": datetime.now()}}
                        )
                
                # Processar mensagens recebidas
                if value.get("messages"):
                    for msg in value["messages"]:
                        # Salvar mensagem recebida
                        incoming = {
                            "from": msg.get("from"),
                            "type": msg.get("type"),
                            "content": msg.get("text", {}).get("body", ""),
                            "whatsapp_message_id": msg.get("id"),
                            "direction": "inbound",
                            "status": "received",
                            "received_at": datetime.now(),
                            "created_at": datetime.now()
                        }
                        await whatsapp_messages_collection.insert_one(incoming)
    
    return {"status": "ok"}

@router.get("/whatsapp/stats")
async def get_whatsapp_stats():
    """Estatísticas de WhatsApp"""
    pipeline = [
        {
            "$facet": {
                "by_status": [
                    {"$group": {"_id": "$status", "count": {"$sum": 1}}}
                ],
                "by_type": [
                    {"$group": {"_id": "$type", "count": {"$sum": 1}}}
                ],
                "last_7_days": [
                    {
                        "$match": {
                            "created_at": {"$gte": datetime.now() - timedelta(days=7)}
                        }
                    },
                    {"$count": "count"}
                ],
                "total": [
                    {"$count": "count"}
                ]
            }
        }
    ]
    
    result = await whatsapp_messages_collection.aggregate(pipeline).to_list(length=1)
    
    if not result:
        return {"by_status": {}, "by_type": {}, "last_7_days": 0, "total": 0}
    
    data = result[0]
    
    return {
        "by_status": {item["_id"]: item["count"] for item in data.get("by_status", [])},
        "by_type": {item["_id"]: item["count"] for item in data.get("by_type", [])},
        "last_7_days": data.get("last_7_days", [{}])[0].get("count", 0),
        "total": data.get("total", [{}])[0].get("count", 0)
    }

@router.post("/whatsapp/test")
async def test_whatsapp_config(phone: str):
    """Testar configuração WhatsApp"""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        raise HTTPException(status_code=400, detail="WhatsApp API não configurado")
    
    try:
        message = WhatsAppMessage(
            to=phone,
            type="text",
            content="🎉 Teste de WhatsApp - CRM Arcsat\n\nSua integração está funcionando perfeitamente!"
        )
        
        result = await send_whatsapp_message(message, BackgroundTasks())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
