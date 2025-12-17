from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Customer Schemas
class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    status: str = "active"

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None

class Customer(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Deal Schemas
class DealBase(BaseModel):
    title: str
    description: Optional[str] = None
    value: float
    stage: str
    customer_id: int
    probability: int = 50
    expected_close_date: Optional[datetime] = None

class DealCreate(DealBase):
    pass

class DealUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    value: Optional[float] = None
    stage: Optional[str] = None
    probability: Optional[int] = None
    expected_close_date: Optional[datetime] = None

class Deal(DealBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Contact Schemas
class ContactBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    customer_id: int

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None

class Contact(ContactBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Activity Schemas
class ActivityBase(BaseModel):
    title: str
    description: Optional[str] = None
    activity_type: str
    status: str = "pending"
    customer_id: int
    deal_id: Optional[int] = None
    due_date: Optional[datetime] = None

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    activity_type: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None

class Activity(ActivityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
