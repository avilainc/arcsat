from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    company = Column(String)
    status = Column(String, default="active")  # active, inactive, lead
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    deals = relationship("Deal", back_populates="customer")
    contacts = relationship("Contact", back_populates="customer")
    activities = relationship("Activity", back_populates="customer")


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    value = Column(Float)
    stage = Column(String)  # prospect, qualified, proposal, negotiation, closed-won, closed-lost
    customer_id = Column(Integer, ForeignKey("customers.id"))
    probability = Column(Integer, default=50)  # 0-100
    expected_close_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="deals")
    activities = relationship("Activity", back_populates="deal")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String)
    phone = Column(String)
    position = Column(String)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="contacts")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    activity_type = Column(String)  # call, meeting, email, task, note
    status = Column(String, default="pending")  # pending, completed, cancelled
    customer_id = Column(Integer, ForeignKey("customers.id"))
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="activities")
    deal = relationship("Deal", back_populates="activities")
