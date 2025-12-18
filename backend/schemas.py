from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

# Helper para ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


# Customer Schemas
class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    status: str = "active"
    # Dados CNPJ/SEFAZ
    cnpj: Optional[str] = None
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    porte: Optional[str] = None
    natureza_juridica: Optional[str] = None
    capital_social: Optional[float] = None
    # Endereço
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    # Dados adicionais
    atividade_principal: Optional[str] = None
    data_abertura: Optional[str] = None
    situacao: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None
    cnpj: Optional[str] = None
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    porte: Optional[str] = None
    natureza_juridica: Optional[str] = None
    capital_social: Optional[float] = None
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    atividade_principal: Optional[str] = None
    data_abertura: Optional[str] = None
    situacao: Optional[str] = None

class Customer(CustomerBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

# Schema para resposta da API CNPJ
class CNPJData(BaseModel):
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    porte: Optional[str] = None
    natureza_juridica: Optional[str] = None
    capital_social: Optional[float] = None
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    atividade_principal: Optional[str] = None
    data_abertura: Optional[str] = None
    situacao: Optional[str] = None


# Deal Schemas
class DealBase(BaseModel):
    title: str
    description: Optional[str] = None
    value: float
    stage: str
    customer_id: str
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
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# Contact Schemas
class ContactBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    customer_id: str

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None

class Contact(ContactBase):
    id: str = Field(alias="_id")
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# Activity Schemas
class ActivityBase(BaseModel):
    title: str
    description: Optional[str] = None
    activity_type: str
    status: str = "pending"
    customer_id: str
    deal_id: Optional[str] = None
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
    id: str = Field(alias="_id")
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
