"""
Transcription database models
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.base import Base

class TranscriptionTask(Base):
    """文字起こしタスクテーブル"""
    __tablename__ = "transcription_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    recording_id = Column(UUID(as_uuid=True), ForeignKey("recordings.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # タスク情報
    task_id = Column(String(100), nullable=False, unique=True, index=True)  # Celeryタスクまたは外部ID
    status = Column(
        String(20), 
        nullable=False, 
        default="pending",
        server_default="pending"
    )  # pending, processing, completed, failed, retrying
    
    progress = Column(Integer, nullable=False, default=0)  # 0-100
    
    # 設定パラメータ
    language = Column(String(10), nullable=False, default="ja")
    temperature = Column(Float, nullable=False, default=0.0)
    
    # 結果
    transcription_text = Column(Text, nullable=True)
    transcription_result = Column(JSONB, nullable=True)  # 詳細な結果（セグメント等）
    confidence = Column(Float, nullable=True)
    detected_language = Column(String(10), nullable=True)
    duration = Column(Float, nullable=True)
    
    # エラー情報
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    
    # 時間情報
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_completion = Column(DateTime, nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # 秒
    actual_duration = Column(Integer, nullable=True)  # 実際の処理時間（秒）
    
    # 作成・更新日時
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ソフト削除
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # リレーション
    recording = relationship("Recording", back_populates="transcription_tasks")
    session = relationship("Session", back_populates="transcription_tasks")
    analysis_tasks = relationship("AnalysisTask", back_populates="transcription_task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TranscriptionTask(id={self.id}, task_id='{self.task_id}', status='{self.status}')>"

    @property
    def is_completed(self) -> bool:
        """完了済みかどうか"""
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        """失敗したかどうか"""
        return self.status == "failed"

    @property
    def is_processing(self) -> bool:
        """処理中かどうか"""
        return self.status in ["pending", "processing", "retrying"]

    @property
    def can_retry(self) -> bool:
        """再試行可能かどうか"""
        return self.status == "failed" and self.retry_count < 3

    def start_processing(self) -> None:
        """処理開始"""
        self.status = "processing"
        self.started_at = datetime.utcnow()
        self.error_message = None
        self.error_code = None

    def complete_processing(
        self, 
        transcription_text: str,
        transcription_result: dict,
        confidence: float,
        detected_language: str,
        duration: float
    ) -> None:
        """処理完了"""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.progress = 100
        self.transcription_text = transcription_text
        self.transcription_result = transcription_result
        self.confidence = confidence
        self.detected_language = detected_language
        self.duration = duration
        
        if self.started_at:
            self.actual_duration = int((self.completed_at - self.started_at).total_seconds())

    def fail_processing(self, error_message: str, error_code: str = None) -> None:
        """処理失敗"""
        self.status = "failed"
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        self.error_code = error_code
        
        if self.started_at:
            self.actual_duration = int((self.completed_at - self.started_at).total_seconds())

    def retry_processing(self) -> None:
        """再試行"""
        if not self.can_retry:
            raise ValueError("Cannot retry this task")
        
        self.status = "retrying"
        self.retry_count += 1
        self.started_at = datetime.utcnow()
        self.completed_at = None
        self.error_message = None
        self.error_code = None
        self.progress = 0

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "id": str(self.id),
            "recording_id": str(self.recording_id),
            "session_id": str(self.session_id) if self.session_id else None,
            "task_id": self.task_id,
            "status": self.status,
            "progress": self.progress,
            "language": self.language,
            "temperature": self.temperature,
            "transcription_text": self.transcription_text,
            "transcription_result": self.transcription_result,
            "confidence": self.confidence,
            "detected_language": self.detected_language,
            "duration": self.duration,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "retry_count": self.retry_count,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None,
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }