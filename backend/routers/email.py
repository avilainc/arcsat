from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import BaseModel, EmailStr
from ..database import customers_collection, activities_collection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

router = APIRouter()

# Configurações de email (via env vars)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)

class EmailTemplate(BaseModel):
    name: str
    subject: str
    body: str
    variables: List[str] = []  # Ex: ["{customer_name}", "{company_name}"]

class EmailSend(BaseModel):
    to: EmailStr
    subject: str
    body: str
    customer_id: Optional[str] = None

class EmailCampaign(BaseModel):
    name: str
    template_id: str
    customer_filter: dict = {}  # Filtro MongoDB para selecionar clientes
    schedule_date: Optional[datetime] = None

# Armazenamento temporário de templates (em produção, use MongoDB)
email_templates = {}

@router.post("/email/templates")
async def create_email_template(template: EmailTemplate):
    """Criar template de email"""
    template_id = str(ObjectId())
    email_templates[template_id] = template.model_dump()
    email_templates[template_id]["id"] = template_id
    email_templates[template_id]["created_at"] = datetime.now()
    
    return {
        "message": "Template criado com sucesso",
        "template_id": template_id,
        "template": email_templates[template_id]
    }

@router.get("/email/templates")
async def list_email_templates():
    """Listar todos os templates de email"""
    return list(email_templates.values())

@router.get("/email/templates/{template_id}")
async def get_email_template(template_id: str):
    """Obter template de email por ID"""
    if template_id not in email_templates:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    return email_templates[template_id]

@router.delete("/email/templates/{template_id}")
async def delete_email_template(template_id: str):
    """Deletar template de email"""
    if template_id not in email_templates:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    del email_templates[template_id]
    return {"message": "Template deletado com sucesso"}

def send_email_smtp(to: str, subject: str, body: str, is_html: bool = True):
    """Enviar email via SMTP"""
    if not SMTP_USER or not SMTP_PASSWORD:
        raise Exception("Credenciais SMTP não configuradas")
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = to
        
        # Adicionar corpo
        mime_type = 'html' if is_html else 'plain'
        msg.attach(MIMEText(body, mime_type))
        
        # Conectar e enviar
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        raise Exception(f"Erro ao enviar email: {str(e)}")

@router.post("/email/send")
async def send_email(email_data: EmailSend, background_tasks: BackgroundTasks):
    """Enviar email individual"""
    try:
        # Enviar email em background
        background_tasks.add_task(
            send_email_smtp,
            email_data.to,
            email_data.subject,
            email_data.body
        )
        
        # Registrar atividade se customer_id fornecido
        if email_data.customer_id:
            activity = {
                "customer_id": email_data.customer_id,
                "type": "email",
                "description": f"Email enviado: {email_data.subject}",
                "status": "completed",
                "due_date": datetime.now(),
                "created_at": datetime.now()
            }
            await activities_collection.insert_one(activity)
        
        return {
            "message": "Email agendado para envio",
            "to": email_data.to,
            "subject": email_data.subject
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/email/send-template/{template_id}")
async def send_template_email(
    template_id: str,
    customer_id: str,
    background_tasks: BackgroundTasks
):
    """Enviar email usando template para um cliente"""
    # Buscar template
    if template_id not in email_templates:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    template = email_templates[template_id]
    
    # Buscar cliente
    customer = await customers_collection.find_one({"_id": ObjectId(customer_id)})
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Substituir variáveis no template
    subject = template['subject']
    body = template['body']
    
    replacements = {
        "{customer_name}": customer.get('name', ''),
        "{company_name}": customer.get('company', ''),
        "{email}": customer.get('email', ''),
        "{phone}": customer.get('phone', ''),
    }
    
    for var, value in replacements.items():
        subject = subject.replace(var, value)
        body = body.replace(var, value)
    
    # Enviar email
    background_tasks.add_task(
        send_email_smtp,
        customer['email'],
        subject,
        body
    )
    
    # Registrar atividade
    activity = {
        "customer_id": customer_id,
        "type": "email",
        "description": f"Email enviado via template: {template['name']}",
        "status": "completed",
        "due_date": datetime.now(),
        "created_at": datetime.now()
    }
    await activities_collection.insert_one(activity)
    
    return {
        "message": "Email agendado para envio",
        "customer": customer.get('name'),
        "email": customer.get('email')
    }

@router.post("/email/campaign")
async def create_email_campaign(campaign: EmailCampaign):
    """Criar campanha de email para múltiplos clientes"""
    # Buscar template
    if campaign.template_id not in email_templates:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    template = email_templates[campaign.template_id]
    
    # Buscar clientes pelo filtro
    cursor = customers_collection.find(campaign.customer_filter)
    customers = await cursor.to_list(length=1000)
    
    if not customers:
        raise HTTPException(status_code=404, detail="Nenhum cliente encontrado com esse filtro")
    
    # Criar registros de envio
    scheduled_emails = []
    for customer in customers:
        # Substituir variáveis
        subject = template['subject']
        body = template['body']
        
        replacements = {
            "{customer_name}": customer.get('name', ''),
            "{company_name}": customer.get('company', ''),
            "{email}": customer.get('email', ''),
            "{phone}": customer.get('phone', ''),
        }
        
        for var, value in replacements.items():
            subject = subject.replace(var, value)
            body = body.replace(var, value)
        
        scheduled_emails.append({
            "customer_id": str(customer['_id']),
            "customer_email": customer.get('email'),
            "subject": subject,
            "body": body,
            "scheduled_for": campaign.schedule_date or datetime.now()
        })
    
    return {
        "message": f"Campanha criada com sucesso",
        "campaign_name": campaign.name,
        "total_emails": len(scheduled_emails),
        "scheduled_for": campaign.schedule_date or "Imediatamente",
        "preview": scheduled_emails[:3] if scheduled_emails else []
    }

@router.post("/email/test")
async def test_email_config(test_email: EmailStr):
    """Testar configuração de email"""
    try:
        send_email_smtp(
            test_email,
            "Teste de Configuração - CRM Arcsat",
            "<h1>Teste de Email</h1><p>Se você recebeu este email, a configuração SMTP está funcionando corretamente!</p>"
        )
        return {
            "message": "Email de teste enviado com sucesso",
            "to": test_email
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar email de teste: {str(e)}")

@router.get("/email/stats")
async def get_email_stats():
    """Obter estatísticas de emails enviados"""
    # Contar atividades de email
    pipeline = [
        {"$match": {"type": "email"}},
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1}
        }}
    ]
    
    result = await activities_collection.aggregate(pipeline).to_list(length=100)
    
    stats = {
        "total": sum(r['count'] for r in result),
        "by_status": {r['_id']: r['count'] for r in result}
    }
    
    # Últimos 7 dias
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_count = await activities_collection.count_documents({
        "type": "email",
        "created_at": {"$gte": seven_days_ago}
    })
    
    stats["last_7_days"] = recent_count
    
    return stats
