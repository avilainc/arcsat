from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Dict
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel
from ..database import customers_collection, activities_collection, deals_collection
import json

router = APIRouter()

# Gerenciador de conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

class Notification(BaseModel):
    type: str  # info, success, warning, error, activity, deal
    title: str
    message: str
    link: str = ""
    user_id: str = ""  # Se vazio, broadcast para todos
    priority: str = "normal"  # low, normal, high, urgent

class NotificationPreference(BaseModel):
    user_id: str
    email_notifications: bool = True
    push_notifications: bool = True
    activity_updates: bool = True
    deal_updates: bool = True
    customer_updates: bool = True
    system_alerts: bool = True

# Armazenamento em memória (em produção, use MongoDB)
notifications_storage = []
preferences_storage = {}

@router.websocket("/notifications/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket para notificações em tempo real"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo de volta (pode ser usado para heartbeat)
            await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@router.post("/notifications/send")
async def send_notification(notification: Notification):
    """Enviar notificação"""
    notification_data = notification.model_dump()
    notification_data["id"] = str(ObjectId())
    notification_data["created_at"] = datetime.now()
    notification_data["read"] = False
    
    # Armazenar notificação
    notifications_storage.append(notification_data)
    
    # Enviar via WebSocket
    message = json.dumps({
        "type": notification.type,
        "title": notification.title,
        "message": notification.message,
        "link": notification.link,
        "priority": notification.priority,
        "timestamp": notification_data["created_at"].isoformat()
    })
    
    if notification.user_id:
        await manager.send_personal_message(message, notification.user_id)
    else:
        await manager.broadcast(message)
    
    return {
        "message": "Notificação enviada",
        "notification_id": notification_data["id"]
    }

@router.get("/notifications/{user_id}")
async def get_notifications(user_id: str, unread_only: bool = False):
    """Obter notificações de um usuário"""
    user_notifications = [
        n for n in notifications_storage
        if n.get('user_id') == user_id or n.get('user_id') == ""
    ]
    
    if unread_only:
        user_notifications = [n for n in user_notifications if not n.get('read', False)]
    
    # Ordenar por data (mais recentes primeiro)
    user_notifications.sort(key=lambda x: x['created_at'], reverse=True)
    
    return {
        "total": len(user_notifications),
        "unread": len([n for n in user_notifications if not n.get('read', False)]),
        "notifications": user_notifications[:50]  # Limitar a 50
    }

@router.put("/notifications/{notification_id}/read")
async def mark_as_read(notification_id: str):
    """Marcar notificação como lida"""
    for notification in notifications_storage:
        if notification['id'] == notification_id:
            notification['read'] = True
            notification['read_at'] = datetime.now()
            return {"message": "Notificação marcada como lida"}
    
    raise HTTPException(status_code=404, detail="Notificação não encontrada")

@router.post("/notifications/{user_id}/mark-all-read")
async def mark_all_as_read(user_id: str):
    """Marcar todas as notificações como lidas"""
    count = 0
    for notification in notifications_storage:
        if (notification.get('user_id') == user_id or notification.get('user_id') == "") and not notification.get('read', False):
            notification['read'] = True
            notification['read_at'] = datetime.now()
            count += 1
    
    return {
        "message": f"{count} notificações marcadas como lidas",
        "count": count
    }

@router.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: str):
    """Deletar notificação"""
    global notifications_storage
    original_length = len(notifications_storage)
    notifications_storage = [n for n in notifications_storage if n['id'] != notification_id]
    
    if len(notifications_storage) == original_length:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    return {"message": "Notificação deletada"}

@router.get("/notifications/preferences/{user_id}")
async def get_notification_preferences(user_id: str):
    """Obter preferências de notificação"""
    if user_id not in preferences_storage:
        # Retornar preferências padrão
        return NotificationPreference(user_id=user_id).model_dump()
    
    return preferences_storage[user_id]

@router.put("/notifications/preferences/{user_id}")
async def update_notification_preferences(user_id: str, preferences: NotificationPreference):
    """Atualizar preferências de notificação"""
    preferences_storage[user_id] = preferences.model_dump()
    return {
        "message": "Preferências atualizadas",
        "preferences": preferences_storage[user_id]
    }

@router.post("/notifications/activity-alert")
async def create_activity_alert(activity_id: str):
    """Criar notificação para atividade vencendo"""
    activity = await activities_collection.find_one({"_id": ObjectId(activity_id)})
    if not activity:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    
    # Buscar cliente relacionado
    customer = None
    if activity.get('customer_id'):
        customer = await customers_collection.find_one({"_id": ObjectId(activity['customer_id'])})
    
    notification = Notification(
        type="activity",
        title="Atividade Vencendo",
        message=f"A atividade '{activity.get('type')}' está vencendo hoje",
        link=f"/activities/{activity_id}",
        priority="high"
    )
    
    await send_notification(notification)
    
    return {"message": "Alerta de atividade criado"}

@router.post("/notifications/deal-alert")
async def create_deal_alert(deal_id: str, alert_type: str):
    """Criar notificação para negócio
    
    alert_type: won, lost, moved, stale
    """
    deal = await deals_collection.find_one({"_id": ObjectId(deal_id)})
    if not deal:
        raise HTTPException(status_code=404, detail="Negócio não encontrado")
    
    messages = {
        "won": f"🎉 Negócio '{deal.get('title')}' foi ganho!",
        "lost": f"❌ Negócio '{deal.get('title')}' foi perdido",
        "moved": f"📊 Negócio '{deal.get('title')}' mudou de estágio",
        "stale": f"⏰ Negócio '{deal.get('title')}' está parado há muito tempo"
    }
    
    priorities = {
        "won": "urgent",
        "lost": "high",
        "moved": "normal",
        "stale": "high"
    }
    
    notification = Notification(
        type="deal",
        title="Atualização de Negócio",
        message=messages.get(alert_type, "Atualização de negócio"),
        link=f"/deals/{deal_id}",
        priority=priorities.get(alert_type, "normal")
    )
    
    await send_notification(notification)
    
    return {"message": "Alerta de negócio criado"}

@router.get("/notifications/stats/{user_id}")
async def get_notification_stats(user_id: str):
    """Estatísticas de notificações"""
    user_notifications = [
        n for n in notifications_storage
        if n.get('user_id') == user_id or n.get('user_id') == ""
    ]
    
    stats = {
        "total": len(user_notifications),
        "unread": len([n for n in user_notifications if not n.get('read', False)]),
        "by_type": {},
        "by_priority": {}
    }
    
    for notification in user_notifications:
        # Por tipo
        ntype = notification.get('type', 'unknown')
        stats["by_type"][ntype] = stats["by_type"].get(ntype, 0) + 1
        
        # Por prioridade
        priority = notification.get('priority', 'normal')
        stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
    
    return stats
