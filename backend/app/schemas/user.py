from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    COUNSELOR = "counselor"
    MANAGER = "manager"
    ADMIN = "admin"


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    is_active: bool = True


class UserCreate(UserBase):
    password: str
    clinic_id: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    clinic_id: Optional[str] = None


class UserInDBBase(UserBase):
    id: str
    clinic_id: Optional[str] = None

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None