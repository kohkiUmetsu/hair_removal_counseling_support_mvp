"""
Clinic schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class ClinicBase(BaseModel):
    """Base clinic schema"""
    name: str = Field(..., min_length=1, max_length=200)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)


class ClinicCreate(ClinicBase):
    """Clinic creation schema"""
    pass


class ClinicUpdate(BaseModel):
    """Clinic update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)


class Clinic(ClinicBase):
    """Clinic response schema"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class ClinicWithStats(Clinic):
    """Clinic with statistics"""
    total_users: int = 0
    total_customers: int = 0
    total_sessions: int = 0
    average_score: Optional[float] = None
    
    class Config:
        orm_mode = True