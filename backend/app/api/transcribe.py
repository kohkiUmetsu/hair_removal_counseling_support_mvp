"""
Transcription API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import logging
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user
from app.schemas.transcription import (
    TranscriptionRequest, TranscriptionResponse, TranscriptionStatusResponse,
    TranscriptionRetryRequest, TranscriptionList, TranscriptionStats
)
from app.schemas.user import User
from app.models.transcription import TranscriptionTask
from app.models.recording import Recording
from app.models.session import Session as SessionModel, SessionStatus
from app.models.customer import Customer
from app.services.transcribe_service import TranscriptionService

logger = logging.getLogger(__name__)

router = APIRouter()

async def transcription_background_task(
    task_id: str,
    recording_id: str,
    file_path: str,
    language: str,
    temperature: float,
    db_url: str
):
    """バックグラウンド文字起こしタスク"""
    # 新しいデータベースセッションを作成
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # タスク取得
        task = db.query(TranscriptionTask).filter(
            TranscriptionTask.task_id == task_id
        ).first()
        
        if not task:
            logger.error(f"Task not found: {task_id}")
            return
        
        # 処理開始
        task.start_processing()
        db.commit()
        
        # 文字起こし実行
        service = TranscriptionService()
        result = await service.transcribe_audio(file_path, language, temperature)
        
        # 結果を保存
        task.complete_processing(
            transcription_text=result.text,
            transcription_result=result.model_dump(),
            confidence=result.confidence,
            detected_language=result.language,
            duration=result.duration
        )
        
        # セッションの文字起こしテキストを更新
        if task.session_id:
            session = db.query(SessionModel).filter(
                SessionModel.id == task.session_id
            ).first()
            if session:
                session.transcription_text = result.text
                session.update_status(SessionStatus.TRANSCRIBED)
        
        db.commit()
        logger.info(f"Transcription task completed: {task_id}")
        
    except Exception as e:
        logger.error(f"Transcription task failed: {task_id} - {e}")
        
        # エラーを記録
        task = db.query(TranscriptionTask).filter(
            TranscriptionTask.task_id == task_id
        ).first()
        
        if task:
            task.fail_processing(str(e), "TRANSCRIPTION_ERROR")
            db.commit()
    
    finally:
        db.close()

@router.post("/", response_model=TranscriptionResponse)
async def start_transcription(
    request: TranscriptionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """文字起こし開始"""
    try:
        # 録音レコード取得
        recording = db.query(Recording).filter(
            Recording.id == request.recording_id,
            Recording.is_deleted == False
        ).first()
        
        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        # 権限チェック
        customer = db.query(Customer).filter(Customer.id == recording.customer_id).first()
        if current_user.role == "counselor" and customer.clinic_id != current_user.clinic_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # アップロード完了チェック
        if recording.upload_status != "completed":
            raise HTTPException(status_code=400, detail="Recording not uploaded yet")
        
        # 既存の進行中タスクチェック
        existing_task = db.query(TranscriptionTask).filter(
            TranscriptionTask.recording_id == request.recording_id,
            TranscriptionTask.status.in_(["pending", "processing", "retrying"]),
            TranscriptionTask.is_deleted == False
        ).first()
        
        if existing_task:
            raise HTTPException(
                status_code=400, 
                detail=f"Transcription already in progress: {existing_task.task_id}"
            )
        
        # ファイル検証
        service = TranscriptionService()
        if not await service.validate_audio_file(recording.file_path):
            raise HTTPException(status_code=400, detail="Invalid audio file")
        
        # タスクID生成
        task_id = str(uuid.uuid4())
        
        # 処理時間推定（ダミーの音声長を使用）
        estimated_duration = service.estimate_processing_time(60)  # 60秒と仮定
        
        # セッション取得または作成
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
                status=SessionStatus.TRANSCRIBING
            )
            db.add(session)
            db.flush()  # IDを取得
        else:
            session.update_status(SessionStatus.TRANSCRIBING)
        
        # 文字起こしタスク作成
        task = TranscriptionTask(
            recording_id=request.recording_id,
            session_id=session.id,
            task_id=task_id,
            language=request.language,
            temperature=request.temperature,
            estimated_duration=estimated_duration,
            estimated_completion=datetime.utcnow() + timedelta(seconds=estimated_duration)
        )
        
        db.add(task)
        db.commit()
        
        # バックグラウンドタスク開始
        from app.core.config import settings
        background_tasks.add_task(
            transcription_background_task,
            task_id=task_id,
            recording_id=str(request.recording_id),
            file_path=recording.file_path,
            language=request.language,
            temperature=request.temperature,
            db_url=str(settings.DATABASE_URL)
        )
        
        logger.info(f"Started transcription task: {task_id}")
        
        return TranscriptionResponse(
            task_id=task_id,
            status="pending",
            estimated_duration=estimated_duration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start transcription: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status/{task_id}", response_model=TranscriptionStatusResponse)
async def get_transcription_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """文字起こし状況取得"""
    try:
        # タスク取得
        task = db.query(TranscriptionTask).filter(
            TranscriptionTask.task_id == task_id,
            TranscriptionTask.is_deleted == False
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # 権限チェック
        recording = db.query(Recording).filter(Recording.id == task.recording_id).first()
        customer = db.query(Customer).filter(Customer.id == recording.customer_id).first()
        
        if current_user.role == "counselor" and customer.clinic_id != current_user.clinic_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # 結果作成
        result = None
        if task.is_completed and task.transcription_result:
            from app.schemas.transcription import TranscriptionResult
            result = TranscriptionResult(**task.transcription_result)
        
        return TranscriptionStatusResponse(
            task_id=task.task_id,
            recording_id=str(task.recording_id),
            status=task.status,
            progress=task.progress,
            result=result,
            error=task.error_message,
            started_at=task.started_at or task.created_at,
            completed_at=task.completed_at,
            estimated_completion=task.estimated_completion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transcription status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/result/{task_id}")
async def get_transcription_result(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """文字起こし結果取得"""
    try:
        # タスク取得
        task = db.query(TranscriptionTask).filter(
            TranscriptionTask.task_id == task_id,
            TranscriptionTask.is_deleted == False
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # 完了チェック
        if not task.is_completed:
            raise HTTPException(status_code=400, detail="Transcription not completed yet")
        
        # 権限チェック
        recording = db.query(Recording).filter(Recording.id == task.recording_id).first()
        customer = db.query(Customer).filter(Customer.id == recording.customer_id).first()
        
        if current_user.role == "counselor" and customer.clinic_id != current_user.clinic_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "task_id": task.task_id,
            "transcription": task.transcription_result,
            "confidence": task.confidence,
            "language": task.detected_language,
            "duration": task.duration,
            "completed_at": task.completed_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transcription result: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/retry/{task_id}")
async def retry_transcription(
    task_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """文字起こし再試行"""
    try:
        # タスク取得
        task = db.query(TranscriptionTask).filter(
            TranscriptionTask.task_id == task_id,
            TranscriptionTask.is_deleted == False
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # 再試行可能チェック
        if not task.can_retry:
            raise HTTPException(status_code=400, detail="Cannot retry this task")
        
        # 権限チェック（管理者またはマネージャーのみ）
        if current_user.role not in ["admin", "manager"]:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        recording = db.query(Recording).filter(Recording.id == task.recording_id).first()
        customer = db.query(Customer).filter(Customer.id == recording.customer_id).first()
        
        if current_user.role == "manager" and customer.clinic_id != current_user.clinic_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # 再試行開始
        task.retry_processing()
        db.commit()
        
        # バックグラウンドタスク開始
        from app.core.config import settings
        background_tasks.add_task(
            transcription_background_task,
            task_id=task.task_id,
            recording_id=str(task.recording_id),
            file_path=recording.file_path,
            language=task.language,
            temperature=task.temperature,
            db_url=str(settings.DATABASE_URL)
        )
        
        logger.info(f"Retrying transcription task: {task_id}")
        
        return {"task_id": task.task_id, "status": "retrying"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retry transcription: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=TranscriptionList)
async def list_transcription_tasks(
    recording_id: Optional[str] = Query(None, description="Filter by recording ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """文字起こしタスク一覧取得"""
    try:
        query = db.query(TranscriptionTask).filter(TranscriptionTask.is_deleted == False)
        
        # フィルター適用
        if recording_id:
            query = query.filter(TranscriptionTask.recording_id == recording_id)
        
        if status:
            query = query.filter(TranscriptionTask.status == status)
        
        # 権限フィルター
        if current_user.role == "counselor":
            # カウンセラーは自分のクリニックのタスクのみ
            query = query.join(Recording).join(Customer).filter(
                Customer.clinic_id == current_user.clinic_id
            )
        elif current_user.role == "manager":
            # マネージャーは自分のクリニックのタスクのみ
            query = query.join(Recording).join(Customer).filter(
                Customer.clinic_id == current_user.clinic_id
            )
        
        # 総数取得
        total = query.count()
        
        # ページング
        offset = (page - 1) * per_page
        tasks = query.order_by(TranscriptionTask.created_at.desc()).offset(offset).limit(per_page).all()
        
        # レスポンス変換
        from app.schemas.transcription import TranscriptionTask as TranscriptionTaskSchema
        task_list = []
        for task in tasks:
            result = None
            if task.is_completed and task.transcription_result:
                from app.schemas.transcription import TranscriptionResult
                result = TranscriptionResult(**task.transcription_result)
            
            task_list.append(TranscriptionTaskSchema(
                task_id=task.task_id,
                recording_id=str(task.recording_id),
                status=task.status,
                progress=task.progress,
                result=result,
                error=task.error_message,
                started_at=task.started_at or task.created_at,
                completed_at=task.completed_at,
                estimated_duration=task.estimated_duration
            ))
        
        return TranscriptionList(
            tasks=task_list,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Failed to list transcription tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats", response_model=TranscriptionStats)
async def get_transcription_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """文字起こし統計取得"""
    try:
        query = db.query(TranscriptionTask).filter(TranscriptionTask.is_deleted == False)
        
        # 権限フィルター
        if current_user.role == "counselor":
            query = query.join(Recording).join(Customer).filter(
                Customer.clinic_id == current_user.clinic_id
            )
        elif current_user.role == "manager":
            query = query.join(Recording).join(Customer).filter(
                Customer.clinic_id == current_user.clinic_id
            )
        
        # 統計計算
        all_tasks = query.all()
        total_tasks = len(all_tasks)
        
        if total_tasks == 0:
            return TranscriptionStats(
                total_tasks=0,
                completed_tasks=0,
                failed_tasks=0,
                pending_tasks=0,
                processing_tasks=0,
                average_processing_time=0.0,
                success_rate=0.0
            )
        
        completed_tasks = len([t for t in all_tasks if t.status == "completed"])
        failed_tasks = len([t for t in all_tasks if t.status == "failed"])
        pending_tasks = len([t for t in all_tasks if t.status == "pending"])
        processing_tasks = len([t for t in all_tasks if t.status in ["processing", "retrying"]])
        
        # 平均処理時間
        processing_times = [t.actual_duration for t in all_tasks if t.actual_duration]
        average_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
        
        # 成功率
        success_rate = completed_tasks / total_tasks if total_tasks > 0 else 0.0
        
        return TranscriptionStats(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
            pending_tasks=pending_tasks,
            processing_tasks=processing_tasks,
            average_processing_time=average_processing_time,
            success_rate=success_rate
        )
        
    except Exception as e:
        logger.error(f"Failed to get transcription stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")