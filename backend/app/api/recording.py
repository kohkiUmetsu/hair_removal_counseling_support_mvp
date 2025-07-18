"""
Recording API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging

from app.api.deps import get_db, get_current_user
from app.schemas.recording import (
    RecordingCreate, RecordingResponse, RecordingInfo, RecordingDownload,
    RecordingList
)
from app.schemas.user import User
from app.models.recording import Recording
from app.models.customer import Customer
from app.models.session import Session as SessionModel
from app.services.storage_service import S3StorageService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=RecordingResponse)
async def create_recording_upload_url(
    request: RecordingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """録音ファイルアップロード用URLを生成"""
    try:
        # 顧客存在チェック
        customer = db.query(Customer).filter(
            Customer.id == request.customer_id
        ).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # 権限チェック（カウンセラーは自分のクリニックの顧客のみ）
        if (current_user.role == "counselor" and
                customer.clinic_id != current_user.clinic_id):
            raise HTTPException(status_code=403, detail="Access denied")

        # ファイルタイプ検証
        storage_service = S3StorageService()
        if not storage_service.validate_file_type(request.content_type):
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # ファイルサイズ検証
        if (request.file_size and
                not storage_service.validate_file_size(request.file_size)):
            raise HTTPException(status_code=400, detail="File size too large")

        # ファイルパス生成
        file_extension = request.content_type.split("/")[-1]
        if file_extension == "webm":
            file_extension = "webm"
        elif file_extension == "mp4":
            file_extension = "mp4"
        else:
            file_extension = "webm"  # デフォルト
        file_path = storage_service.generate_file_path(
            clinic_id=str(customer.clinic_id),
            customer_id=str(customer.id),
            session_date=request.session_date,
            file_extension=file_extension
        )
        
        # プリサインドURL生成
        upload_info = await storage_service.generate_presigned_upload_url(
            file_path=file_path,
            content_type=request.content_type,
            file_size=request.file_size
        )
        
        # 録音レコード作成
        recording = Recording(
            customer_id=request.customer_id,
            file_path=file_path,
            original_filename=request.filename,
            content_type=request.content_type,
            file_size=request.file_size,
            upload_status="pending",
            metadata={
                "created_by": str(current_user.id),
                "clinic_id": str(customer.clinic_id)
            }
        )
        
        db.add(recording)
        db.commit()
        db.refresh(recording)
        
        logger.info(f"Created recording upload URL for customer {request.customer_id}")
        
        return RecordingResponse(
            recording_id=str(recording.id),
            file_path=file_path,
            upload_url=upload_info["upload_url"],
            fields=upload_info["fields"],
            expires_at=upload_info["expires_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create recording upload URL: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{recording_id}", response_model=RecordingDownload)
async def get_recording_download_url(
    recording_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """録音ファイルダウンロードURL取得"""
    try:
        # 録音レコード取得
        recording = db.query(Recording).filter(
            Recording.id == recording_id,
            Recording.is_deleted == False
        ).first()
        
        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")

        # 権限チェック
        customer = db.query(Customer).filter(
            Customer.id == recording.customer_id
        ).first()
        if (current_user.role == "counselor" and
                customer.clinic_id != current_user.clinic_id):
            raise HTTPException(status_code=403, detail="Access denied")

        # アップロード完了チェック
        if recording.upload_status != "completed":
            raise HTTPException(status_code=400, detail="Recording not uploaded yet")

        storage_service = S3StorageService()
        
        # ファイル存在チェック
        if not await storage_service.file_exists(recording.file_path):
            raise HTTPException(status_code=404, detail="Recording file not found")
        
        # ダウンロードURL生成
        download_info = await storage_service.generate_presigned_download_url(recording.file_path)
        
        # メタデータ取得
        metadata = await storage_service.get_file_metadata(recording.file_path)
        
        logger.info(f"Generated download URL for recording {recording_id}")
        
        return RecordingDownload(
            recording_id=recording_id,
            download_url=download_info["download_url"],
            file_path=recording.file_path,
            metadata=metadata,
            expires_at=download_info["expires_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recording download URL: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{recording_id}")
async def delete_recording(
    recording_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """録音ファイル削除"""
    try:
        # 録音レコード取得
        recording = db.query(Recording).filter(
            Recording.id == recording_id,
            Recording.is_deleted == False
        ).first()
        
        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")

        # 権限チェック（管理者またはマネージャーのみ）
        if current_user.role not in ["admin", "manager"]:
            raise HTTPException(status_code=403, detail="Permission denied")

        # マネージャーは自分のクリニックのみ
        if current_user.role == "manager":
            customer = db.query(Customer).filter(
                Customer.id == recording.customer_id
            ).first()
            if customer.clinic_id != current_user.clinic_id:
                raise HTTPException(status_code=403, detail="Access denied")

        storage_service = S3StorageService()
        
        # S3からファイル削除
        if await storage_service.file_exists(recording.file_path):
            await storage_service.delete_file(recording.file_path)

        # ソフト削除
        recording.is_deleted = True
        recording.deleted_at = datetime.utcnow()

        db.commit()

        logger.info(f"Deleted recording {recording_id}")

        return {"message": "Recording deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete recording: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=RecordingList)
async def list_recordings(
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """録音一覧取得"""
    try:
        query = db.query(Recording).filter(Recording.is_deleted == False)

        # 顧客フィルター
        if customer_id:
            query = query.filter(Recording.customer_id == customer_id)

        # 権限フィルター
        if current_user.role == "counselor":
            # カウンセラーは自分のクリニックの録音のみ
            query = query.join(Customer).filter(
                Customer.clinic_id == current_user.clinic_id
            )
        elif current_user.role == "manager":
            # マネージャーは自分のクリニックの録音のみ
            query = query.join(Customer).filter(
                Customer.clinic_id == current_user.clinic_id
            )

        # 総数取得
        total = query.count()

        # ページング
        offset = (page - 1) * per_page
        recordings = query.offset(offset).limit(per_page).all()

        # レスポンス変換
        recording_info = []
        for recording in recordings:
            recording_info.append(RecordingInfo(
                recording_id=str(recording.id),
                customer_id=str(recording.customer_id),
                file_path=recording.file_path,
                content_type=recording.content_type,
                file_size=recording.file_size,
                filename=recording.original_filename,
                uploaded_at=recording.uploaded_at,
                created_at=recording.created_at
            ))

        return RecordingList(
            recordings=recording_info,
            total=total,
            page=page,
            per_page=per_page
        )

    except Exception as e:
        logger.error(f"Failed to list recordings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{recording_id}/complete")
async def complete_recording_upload(
    recording_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """録音アップロード完了通知"""
    try:
        # 録音レコード取得
        recording = db.query(Recording).filter(
            Recording.id == recording_id,
            Recording.is_deleted == False
        ).first()
        
        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")

        # 権限チェック
        customer = db.query(Customer).filter(
            Customer.id == recording.customer_id
        ).first()
        if (current_user.role == "counselor" and
                customer.clinic_id != current_user.clinic_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        storage_service = S3StorageService()
        
        # ファイル存在確認
        if not await storage_service.file_exists(recording.file_path):
            raise HTTPException(status_code=400, detail="File not found in storage")

        # メタデータ更新
        metadata = await storage_service.get_file_metadata(recording.file_path)
        recording.file_size = metadata["size"]
        recording.upload_status = "completed"
        recording.uploaded_at = datetime.utcnow()

        # セッションレコード作成または更新
        session = db.query(SessionModel).filter(
            SessionModel.customer_id == recording.customer_id,
            SessionModel.audio_file_path == recording.file_path
        ).first()

        if not session:
            session = SessionModel(
                customer_id=recording.customer_id,
                counselor_id=current_user.id,
                audio_file_path=recording.file_path,
                session_date=recording.created_at,
                duration_minutes=None,  # TODO: 音声から計算
                status="recorded"
            )
            db.add(session)

        recording.session_id = session.id

        db.commit()

        logger.info(f"Completed recording upload for {recording_id}")

        return {
            "message": "Recording upload completed",
            "session_id": str(session.id)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete recording upload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")