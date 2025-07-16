"""
User model
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    """User role enumeration"""
    COUNSELOR = "counselor"
    MANAGER = "manager"
    ADMIN = "admin"


class User(BaseModel):
    """User model"""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.COUNSELOR)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Foreign key
    clinic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Relationships
    clinic = relationship("Clinic", back_populates="users")
    sessions = relationship("Session", back_populates="counselor", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    def has_permission(self, required_role: UserRole) -> bool:
        """Check if user has required permission level"""
        role_hierarchy = {
            UserRole.COUNSELOR: 1,
            UserRole.MANAGER: 2,
            UserRole.ADMIN: 3
        }
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)
    
    def can_access_clinic(self, clinic_id: str) -> bool:
        """Check if user can access specific clinic"""
        if self.role == UserRole.ADMIN:
            return True
        return str(self.clinic_id) == clinic_id