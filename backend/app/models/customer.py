"""
Customer model
"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Customer(BaseModel):
    """Customer model"""
    __tablename__ = "customers"
    
    name = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Foreign key
    clinic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Relationships
    clinic = relationship("Clinic", back_populates="customers")
    sessions = relationship("Session", back_populates="customer", cascade="all, delete-orphan")
    recordings = relationship("Recording", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}', clinic_id={self.clinic_id})>"
    
    @property
    def total_sessions(self) -> int:
        """Get total number of sessions for this customer"""
        return len(self.sessions)
    
    @property
    def latest_session(self):
        """Get the most recent session"""
        if self.sessions:
            return max(self.sessions, key=lambda s: s.session_date)
        return None