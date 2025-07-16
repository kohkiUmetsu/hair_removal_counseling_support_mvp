from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.base import Base

class Recording(Base):
    """録音ファイル管理テーブル"""
    __tablename__ = "recordings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # ファイル情報
    file_path = Column(String(500), nullable=False, unique=True)
    original_filename = Column(String(255), nullable=True)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=True)
    
    # アップロード状況
    upload_status = Column(
        String(20), 
        nullable=False, 
        default="pending",
        server_default="pending"
    )  # pending, uploading, completed, failed
    
    # メタデータ
    metadata = Column(JSONB, nullable=True)
    
    # 日時情報
    uploaded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 削除フラグ
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # リレーション
    customer = relationship("Customer", back_populates="recordings")
    session = relationship("Session", back_populates="recording")
    transcription_tasks = relationship("TranscriptionTask", back_populates="recording", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Recording(id={self.id}, customer_id={self.customer_id}, file_path={self.file_path})>"

    @property
    def is_uploaded(self) -> bool:
        """アップロード完了フラグ"""
        return self.upload_status == "completed"

    @property
    def file_extension(self) -> str:
        """ファイル拡張子を取得"""
        if self.original_filename:
            return self.original_filename.split('.')[-1].lower()
        elif self.file_path:
            return self.file_path.split('.')[-1].lower()
        return ""

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "id": str(self.id),
            "customer_id": str(self.customer_id),
            "session_id": str(self.session_id) if self.session_id else None,
            "file_path": self.file_path,
            "original_filename": self.original_filename,
            "content_type": self.content_type,
            "file_size": self.file_size,
            "upload_status": self.upload_status,
            "metadata": self.metadata,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }