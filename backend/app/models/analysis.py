"""
AI Analysis database models
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.base import Base

class AnalysisTask(Base):
    """AI分析タスクテーブル"""
    __tablename__ = "analysis_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    transcription_task_id = Column(UUID(as_uuid=True), ForeignKey("transcription_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # タスク情報
    task_id = Column(String(100), nullable=False, unique=True, index=True)  # バックグラウンドタスクID
    analysis_type = Column(String(20), nullable=False, default="full")  # full, quick, specific
    status = Column(
        String(30), 
        nullable=False, 
        default="pending",
        server_default="pending"
    )  # pending, preprocessing, analyzing, generating_suggestions, completed, failed
    
    progress = Column(Integer, nullable=False, default=0)  # 0-100
    stage = Column(String(50), nullable=True)  # 現在の処理段階
    
    # 設定パラメータ
    focus_areas = Column(JSONB, nullable=True)  # 重点分析項目
    custom_prompts = Column(JSONB, nullable=True)  # カスタムプロンプト
    
    # 分析結果
    overall_score = Column(Float, nullable=True)
    questioning_result = Column(JSONB, nullable=True)
    anxiety_handling_result = Column(JSONB, nullable=True)
    closing_result = Column(JSONB, nullable=True)
    flow_result = Column(JSONB, nullable=True)
    
    session_summary = Column(Text, nullable=True)
    key_strengths = Column(JSONB, nullable=True)  # List[str]
    critical_improvements = Column(JSONB, nullable=True)  # List[str]
    full_analysis_result = Column(JSONB, nullable=True)  # 完全な分析結果
    
    # 改善提案
    suggestions = Column(JSONB, nullable=True)  # List[Suggestion]
    suggestions_generated = Column(Boolean, nullable=False, default=False)
    
    # API使用状況
    openai_tokens_used = Column(Integer, nullable=True)
    openai_cost = Column(Float, nullable=True)
    
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
    transcription_task = relationship("TranscriptionTask", back_populates="analysis_tasks")
    session = relationship("Session", back_populates="analysis_tasks")
    feedback_records = relationship("AnalysisFeedback", back_populates="analysis_task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AnalysisTask(id={self.id}, task_id='{self.task_id}', status='{self.status}')>"

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
        return self.status in ["pending", "preprocessing", "analyzing", "generating_suggestions"]

    @property
    def can_retry(self) -> bool:
        """再試行可能かどうか"""
        return self.status == "failed" and self.retry_count < 3

    def start_processing(self, stage: str = "preprocessing") -> None:
        """処理開始"""
        self.status = "preprocessing"
        self.stage = stage
        self.started_at = datetime.utcnow()
        self.error_message = None
        self.error_code = None
        self.progress = 10

    def update_progress(self, progress: int, stage: str) -> None:
        """進行状況更新"""
        self.progress = min(progress, 100)
        self.stage = stage
        if stage == "analyzing":
            self.status = "analyzing"
        elif stage == "generating_suggestions":
            self.status = "generating_suggestions"

    def complete_processing(
        self, 
        analysis_result: dict,
        suggestions: list = None,
        tokens_used: int = None,
        cost: float = None
    ) -> None:
        """処理完了"""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.progress = 100
        self.stage = "completed"
        
        # 分析結果保存
        self.overall_score = analysis_result.get("overall_score")
        self.questioning_result = analysis_result.get("questioning")
        self.anxiety_handling_result = analysis_result.get("anxiety_handling")
        self.closing_result = analysis_result.get("closing")
        self.flow_result = analysis_result.get("flow")
        self.session_summary = analysis_result.get("session_summary")
        self.key_strengths = analysis_result.get("key_strengths", [])
        self.critical_improvements = analysis_result.get("critical_improvements", [])
        self.full_analysis_result = analysis_result
        
        if suggestions:
            self.suggestions = suggestions
            self.suggestions_generated = True
        
        # API使用状況
        if tokens_used:
            self.openai_tokens_used = tokens_used
        if cost:
            self.openai_cost = cost
        
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
        
        self.status = "pending"
        self.retry_count += 1
        self.started_at = None
        self.completed_at = None
        self.error_message = None
        self.error_code = None
        self.progress = 0
        self.stage = None

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "id": str(self.id),
            "transcription_task_id": str(self.transcription_task_id),
            "session_id": str(self.session_id) if self.session_id else None,
            "task_id": self.task_id,
            "analysis_type": self.analysis_type,
            "status": self.status,
            "progress": self.progress,
            "stage": self.stage,
            "focus_areas": self.focus_areas,
            "custom_prompts": self.custom_prompts,
            "overall_score": self.overall_score,
            "questioning_result": self.questioning_result,
            "anxiety_handling_result": self.anxiety_handling_result,
            "closing_result": self.closing_result,
            "flow_result": self.flow_result,
            "session_summary": self.session_summary,
            "key_strengths": self.key_strengths,
            "critical_improvements": self.critical_improvements,
            "full_analysis_result": self.full_analysis_result,
            "suggestions": self.suggestions,
            "suggestions_generated": self.suggestions_generated,
            "openai_tokens_used": self.openai_tokens_used,
            "openai_cost": self.openai_cost,
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


class AnalysisFeedback(Base):
    """分析結果フィードバックテーブル"""
    __tablename__ = "analysis_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    analysis_task_id = Column(UUID(as_uuid=True), ForeignKey("analysis_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # フィードバック内容
    feedback_type = Column(String(20), nullable=False)  # helpful, not_helpful, implemented, inaccurate
    rating = Column(Integer, nullable=True)  # 1-5の評価
    comments = Column(Text, nullable=True)
    suggestion_id = Column(String(100), nullable=True)  # 特定の提案へのフィードバック
    
    # メタデータ
    feedback_data = Column(JSONB, nullable=True)  # 追加のフィードバックデータ
    
    # 作成・更新日時
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    analysis_task = relationship("AnalysisTask", back_populates="feedback_records")
    user = relationship("User")

    def __repr__(self):
        return f"<AnalysisFeedback(id={self.id}, feedback_type='{self.feedback_type}', rating={self.rating})>"


class SuccessPattern(Base):
    """成功パターンテーブル"""
    __tablename__ = "success_patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    clinic_id = Column(UUID(as_uuid=True), ForeignKey("clinics.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # パターン情報
    pattern_id = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=False, index=True)  # questioning, anxiety_handling, closing, flow
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # 効果指標
    success_rate = Column(Float, nullable=False)
    usage_frequency = Column(Integer, nullable=False, default=0)
    effectiveness_score = Column(Float, nullable=False)
    
    # パターンデータ
    pattern_data = Column(JSONB, nullable=False)  # パターンの詳細情報
    example_sessions = Column(JSONB, nullable=True)  # 成功事例のセッションID
    
    # 学習情報
    learned_from_sessions = Column(Integer, nullable=False, default=0)
    last_updated_from_analysis = Column(DateTime, nullable=True)
    confidence_score = Column(Float, nullable=False, default=0.0)
    
    # 作成・更新日時
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ソフト削除
    is_active = Column(Boolean, nullable=False, default=True)
    
    # リレーション
    clinic = relationship("Clinic")

    def __repr__(self):
        return f"<SuccessPattern(id={self.id}, category='{self.category}', title='{self.title[:30]}...')>"

    def update_effectiveness(self, new_success_rate: float, sessions_count: int) -> None:
        """効果性の更新"""
        self.success_rate = new_success_rate
        self.learned_from_sessions = sessions_count
        self.last_updated_from_analysis = datetime.utcnow()
        
        # 信頼度スコアの計算（セッション数と成功率から）
        if sessions_count >= 10:
            self.confidence_score = min(0.9, self.success_rate * (sessions_count / 50))
        else:
            self.confidence_score = self.success_rate * 0.5

    def increment_usage(self) -> None:
        """使用回数の増加"""
        self.usage_frequency += 1