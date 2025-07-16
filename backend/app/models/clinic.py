"""
Clinic model
"""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Clinic(BaseModel):
    """Clinic model"""
    __tablename__ = "clinics"
    
    name = Column(String(200), nullable=False, index=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="clinic", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="clinic", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Clinic(id={self.id}, name='{self.name}')>"