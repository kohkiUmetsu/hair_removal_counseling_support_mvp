"""
Transcription schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class TranscriptionSegment(BaseModel):
    """文字起こしセグメント"""
    id: int = Field(..., description="セグメントID")
    start: float = Field(..., description="開始時間（秒）")
    end: float = Field(..., description="終了時間（秒）")
    text: str = Field(..., description="テキスト")
    confidence: float = Field(..., ge=0.0, le=1.0, description="信頼度")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 0,
                "start": 0.0,
                "end": 5.2,
                "text": "こんにちは、今日はよろしくお願いします。",
                "confidence": 0.95
            }
        }

class TranscriptionResult(BaseModel):
    """文字起こし結果"""
    text: str = Field(..., description="全体のテキスト")
    language: str = Field(..., description="検出された言語")
    confidence: float = Field(..., ge=0.0, le=1.0, description="全体の信頼度")
    duration: float = Field(..., description="音声の長さ（秒）")
    segments: List[TranscriptionSegment] = Field(default_factory=list, description="セグメント一覧")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "text": "こんにちは、今日はよろしくお願いします。脱毛についてご相談があるとのことですが。",
                "language": "ja",
                "confidence": 0.92,
                "duration": 10.5,
                "segments": [
                    {
                        "id": 0,
                        "start": 0.0,
                        "end": 5.2,
                        "text": "こんにちは、今日はよろしくお願いします。",
                        "confidence": 0.95
                    }
                ]
            }
        }

class TranscriptionTask(BaseModel):
    """文字起こしタスク"""
    task_id: str = Field(..., description="タスクID")
    recording_id: str = Field(..., description="録音ID")
    status: str = Field(..., description="ステータス")
    progress: int = Field(..., ge=0, le=100, description="進行状況（%）")
    result: Optional[TranscriptionResult] = Field(None, description="結果")
    error: Optional[str] = Field(None, description="エラーメッセージ")
    started_at: datetime = Field(..., description="開始日時")
    completed_at: Optional[datetime] = Field(None, description="完了日時")
    estimated_duration: Optional[int] = Field(None, description="推定処理時間（秒）")

    class Config:
        from_attributes = True

class TranscriptionRequest(BaseModel):
    """文字起こし開始リクエスト"""
    recording_id: str = Field(..., description="録音ID")
    language: Optional[str] = Field("ja", description="言語コード")
    temperature: Optional[float] = Field(0.0, ge=0.0, le=1.0, description="温度パラメータ")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "recording_id": "123e4567-e89b-12d3-a456-426614174000",
                "language": "ja",
                "temperature": 0.0
            }
        }

class TranscriptionResponse(BaseModel):
    """文字起こし開始レスポンス"""
    task_id: str = Field(..., description="タスクID")
    status: str = Field(..., description="ステータス")
    estimated_duration: int = Field(..., description="推定処理時間（秒）")
    
    class Config:
        from_attributes = True

class TranscriptionStatusResponse(BaseModel):
    """文字起こし状況レスポンス"""
    task_id: str = Field(..., description="タスクID")
    recording_id: str = Field(..., description="録音ID")
    status: str = Field(..., description="ステータス")
    progress: int = Field(..., description="進行状況（%）")
    result: Optional[TranscriptionResult] = Field(None, description="結果")
    error: Optional[str] = Field(None, description="エラーメッセージ")
    started_at: datetime = Field(..., description="開始日時")
    completed_at: Optional[datetime] = Field(None, description="完了日時")
    estimated_completion: Optional[datetime] = Field(None, description="完了予定日時")

    class Config:
        from_attributes = True

class TranscriptionRetryRequest(BaseModel):
    """文字起こし再試行リクエスト"""
    task_id: str = Field(..., description="再試行するタスクID")
    
    class Config:
        from_attributes = True

class TranscriptionList(BaseModel):
    """文字起こしタスク一覧"""
    tasks: List[TranscriptionTask] = Field(..., description="タスク一覧")
    total: int = Field(..., description="総数")
    page: int = Field(..., description="ページ番号")
    per_page: int = Field(..., description="ページサイズ")

    class Config:
        from_attributes = True

class TranscriptionStats(BaseModel):
    """文字起こし統計"""
    total_tasks: int = Field(..., description="総タスク数")
    completed_tasks: int = Field(..., description="完了タスク数")
    failed_tasks: int = Field(..., description="失敗タスク数")
    pending_tasks: int = Field(..., description="待機中タスク数")
    processing_tasks: int = Field(..., description="処理中タスク数")
    average_processing_time: float = Field(..., description="平均処理時間（秒）")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="成功率")

    class Config:
        from_attributes = True