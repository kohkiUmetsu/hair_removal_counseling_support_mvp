"""
Session model
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.models.base import BaseModel


class SessionStatus(str, enum.Enum):
    """Session status enumeration"""
    RECORDED = "recorded"
    TRANSCRIBING = "transcribing"
    TRANSCRIBED = "transcribed"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    COMPLETED = "completed"
    FAILED = "failed"


class Session(BaseModel):
    """Session model"""
    __tablename__ = "sessions"
    
    # Session details
    session_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    duration_minutes = Column(Integer, nullable=True)
    status = Column(SQLEnum(SessionStatus), nullable=False, default=SessionStatus.RECORDED)
    
    # File and content
    audio_file_path = Column(String(500), nullable=True)
    transcription_text = Column(Text, nullable=True)
    analysis_result = Column(JSONB, nullable=True)
    
    # Additional metadata
    notes = Column(Text, nullable=True)
    
    # Foreign keys
    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    counselor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Relationships
    customer = relationship("Customer", back_populates="sessions")
    counselor = relationship("User", back_populates="sessions")
    recording = relationship("Recording", back_populates="session", uselist=False)
    transcription_tasks = relationship("TranscriptionTask", back_populates="session", cascade="all, delete-orphan")
    analysis_tasks = relationship("AnalysisTask", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Session(id={self.id}, customer_id={self.customer_id}, status='{self.status}')>"
    
    @property
    def is_completed(self) -> bool:
        """Check if session is completed"""
        return self.status == SessionStatus.COMPLETED
    
    @property
    def has_transcription(self) -> bool:
        """Check if session has transcription"""
        return self.transcription_text is not None and len(self.transcription_text.strip()) > 0
    
    @property
    def has_analysis(self) -> bool:
        """Check if session has analysis"""
        return self.analysis_result is not None
    
    @property
    def overall_score(self) -> float:
        """Get overall analysis score"""
        if self.analysis_result and isinstance(self.analysis_result, dict):
            return self.analysis_result.get("overall_score", 0.0)
        return 0.0
    
    def update_status(self, new_status: SessionStatus) -> None:
        """Update session status with validation"""
        valid_transitions = {
            SessionStatus.RECORDED: [SessionStatus.TRANSCRIBING, SessionStatus.FAILED],
            SessionStatus.TRANSCRIBING: [SessionStatus.TRANSCRIBED, SessionStatus.FAILED],
            SessionStatus.TRANSCRIBED: [SessionStatus.ANALYZING, SessionStatus.FAILED],
            SessionStatus.ANALYZING: [SessionStatus.ANALYZED, SessionStatus.FAILED],
            SessionStatus.ANALYZED: [SessionStatus.COMPLETED, SessionStatus.FAILED],
            SessionStatus.FAILED: [SessionStatus.RECORDED]  # Allow retry
        }
        
        if new_status in valid_transitions.get(self.status, []):
            self.status = new_status
        else:
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")
    
    def get_analysis_score(self, category: str) -> float:
        """Get analysis score for specific category"""
        if not self.analysis_result or not isinstance(self.analysis_result, dict):
            return 0.0
        
        return self.analysis_result.get(category, {}).get("score", 0.0)
    
    def get_analysis_suggestions(self, category: str = None) -> list:
        """Get analysis suggestions"""
        if not self.analysis_result or not isinstance(self.analysis_result, dict):
            return []
        
        if category:
            return self.analysis_result.get(category, {}).get("suggestions", [])
        
        # Return all suggestions
        suggestions = []
        for cat_data in self.analysis_result.values():
            if isinstance(cat_data, dict) and "suggestions" in cat_data:
                suggestions.extend(cat_data["suggestions"])
        
        return suggestions