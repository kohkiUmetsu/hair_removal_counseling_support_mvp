from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class RecordingCreate(BaseModel):
    """録音作成リクエスト"""
    customer_id: str = Field(..., description="顧客ID")
    session_date: datetime = Field(..., description="セッション日時")
    content_type: str = Field(..., description="ファイルのContent-Type")
    file_size: Optional[int] = Field(None, description="ファイルサイズ（バイト）")
    filename: Optional[str] = Field(None, description="オリジナルファイル名")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "customer_id": "123e4567-e89b-12d3-a456-426614174000",
                "session_date": "2023-12-01T10:00:00Z",
                "content_type": "audio/webm",
                "file_size": 1024000,
                "filename": "counseling_session.webm"
            }
        }

class RecordingResponse(BaseModel):
    """録音作成レスポンス"""
    recording_id: str = Field(..., description="録音ID")
    file_path: str = Field(..., description="S3ファイルパス")
    upload_url: str = Field(..., description="アップロード用URL")
    fields: Dict[str, Any] = Field(..., description="アップロード用フィールド")
    expires_at: str = Field(..., description="URL有効期限")

    class Config:
        from_attributes = True

class RecordingInfo(BaseModel):
    """録音情報"""
    recording_id: str = Field(..., description="録音ID")
    customer_id: str = Field(..., description="顧客ID")
    file_path: str = Field(..., description="S3ファイルパス")
    content_type: str = Field(..., description="ファイルのContent-Type")
    file_size: Optional[int] = Field(None, description="ファイルサイズ")
    filename: Optional[str] = Field(None, description="オリジナルファイル名")
    uploaded_at: Optional[datetime] = Field(None, description="アップロード日時")
    created_at: datetime = Field(..., description="作成日時")

    class Config:
        from_attributes = True

class RecordingDownload(BaseModel):
    """録音ダウンロード情報"""
    recording_id: str = Field(..., description="録音ID")
    download_url: str = Field(..., description="ダウンロード用URL")
    file_path: str = Field(..., description="ファイルパス")
    metadata: Dict[str, Any] = Field(..., description="ファイルメタデータ")
    expires_at: str = Field(..., description="URL有効期限")

    class Config:
        from_attributes = True


class RecordingMetadata(BaseModel):
    """録音メタデータ"""
    size: int = Field(..., description="ファイルサイズ")
    last_modified: str = Field(..., description="最終更新日時")
    content_type: str = Field(..., description="Content-Type")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="追加メタデータ")
    etag: str = Field(..., description="ETag")
    encryption: Optional[str] = Field(None, description="暗号化方式")

    class Config:
        from_attributes = True

class RecordingList(BaseModel):
    """録音一覧"""
    recordings: list[RecordingInfo] = Field(..., description="録音一覧")
    total: int = Field(..., description="総数")
    page: int = Field(..., description="ページ番号")
    per_page: int = Field(..., description="ページサイズ")

    class Config:
        from_attributes = True

class RecordingUpdate(BaseModel):
    """録音更新"""
    filename: Optional[str] = Field(None, description="ファイル名")
    metadata: Optional[Dict[str, Any]] = Field(None, description="メタデータ")

    class Config:
        from_attributes = True