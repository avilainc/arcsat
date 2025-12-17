from datetime import datetime
from typing import Optional
from bson import ObjectId

# Modelos MongoDB (estrutura de documentos)

def customer_helper(customer) -> dict:
    """Helper para converter documento MongoDB em dict"""
    return {
        "id": str(customer["_id"]),
        "name": customer["name"],
        "email": customer["email"],
        "phone": customer.get("phone"),
        "company": customer.get("company"),
        "status": customer.get("status", "active"),
        "created_at": customer["created_at"],
        "updated_at": customer["updated_at"],
    }

def deal_helper(deal) -> dict:
    """Helper para converter documento MongoDB em dict"""
    return {
        "id": str(deal["_id"]),
        "title": deal["title"],
        "description": deal.get("description"),
        "value": deal["value"],
        "stage": deal["stage"],
        "customer_id": str(deal["customer_id"]),
        "probability": deal.get("probability", 50),
        "expected_close_date": deal.get("expected_close_date"),
        "created_at": deal["created_at"],
        "updated_at": deal["updated_at"],
    }

def contact_helper(contact) -> dict:
    """Helper para converter documento MongoDB em dict"""
    return {
        "id": str(contact["_id"]),
        "name": contact["name"],
        "email": contact.get("email"),
        "phone": contact.get("phone"),
        "position": contact.get("position"),
        "customer_id": str(contact["customer_id"]),
        "created_at": contact["created_at"],
    }

def activity_helper(activity) -> dict:
    """Helper para converter documento MongoDB em dict"""
    return {
        "id": str(activity["_id"]),
        "title": activity["title"],
        "description": activity.get("description"),
        "activity_type": activity["activity_type"],
        "status": activity.get("status", "pending"),
        "customer_id": str(activity["customer_id"]),
        "deal_id": str(activity["deal_id"]) if activity.get("deal_id") else None,
        "due_date": activity.get("due_date"),
        "created_at": activity["created_at"],
    }
