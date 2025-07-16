from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    RECORDED = "recorded"
    TRANSCRIBED = "transcribed"
    ANALYZED = "analyzed"
    COMPLETED = "completed"


class SessionBase(BaseModel):
    customer_id: str
    counselor_id: str
    session_date: datetime
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[SessionStatus] = None
    recording_url: Optional[str] = None
    transcript_text: Optional[str] = None
    analysis_results: Optional[Dict[str, Any]] = None


class SessionInDBBase(SessionBase):
    id: str
    status: SessionStatus
    recording_url: Optional[str] = None
    transcript_text: Optional[str] = None
    analysis_results: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Session(SessionInDBBase):
    pass


class SessionWithRelations(SessionInDBBase):
    customer_name: str
    counselor_name: str