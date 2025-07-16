"""
Customer schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class CustomerBase(BaseModel):
    """Base customer schema"""
    name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None


class CustomerCreate(CustomerBase):
    """Customer creation schema"""
    clinic_id: UUID


class CustomerUpdate(BaseModel):
    """Customer update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None


class Customer(CustomerBase):
    """Customer response schema"""
    id: UUID
    clinic_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class CustomerWithStats(Customer):
    """Customer with session statistics"""
    total_sessions: int = 0
    latest_session_date: Optional[datetime] = None
    average_score: Optional[float] = None
    
    class Config:
        orm_mode = True