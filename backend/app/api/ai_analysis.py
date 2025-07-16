"""
AI Analysis API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import logging
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user
from app.schemas.analysis import (
    AnalysisRequest, AnalysisResponse, AnalysisStatusResponse,
    BatchAnalysisRequest, BatchAnalysisResponse, AnalysisList, AnalysisStats
)
from app.schemas.user import User
from app.models.analysis import AnalysisTask
from app.models.transcription import TranscriptionTask
from app.models.session import Session as SessionModel, SessionStatus
from app.models.customer import Customer
from app.services.analysis_service import AnalysisService

logger = logging.getLogger(__name__)

router = APIRouter()

async def analysis_background_task(
    task_id: str,
    transcription_task_id: str,
    transcription_text: str,
    analysis_type: str,
    focus_areas: List[str] = None,
    custom_prompts: dict = None,
    db_url: str = None
):
    """バックグラウンドAI分析タスク"""
    # 新しいデータベースセッションを作成
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # タスク取得
        analysis_task = db.query(AnalysisTask).filter(
            AnalysisTask.task_id == task_id
        ).first()
        
        if not analysis_task:
            logger.error(f"Analysis task not found: {task_id}")
            return
        
        # 処理開始
        analysis_task.start_processing("preprocessing")
        db.commit()
        
        # AI分析実行
        service = AnalysisService()
        
        # 前処理段階
        analysis_task.update_progress(20, "preprocessing")
        db.commit()
        
        # 分析実行
        analysis_task.update_progress(30, "analyzing")
        db.commit()
        
        from app.schemas.analysis import AnalysisType
        analysis_result, tokens_used, cost = await service.analyze_counseling(
            transcription_text=transcription_text,
            analysis_type=AnalysisType(analysis_type),
            focus_areas=focus_areas,
            custom_prompts=custom_prompts
        )
        
        # 改善提案生成段階
        analysis_task.update_progress(80, "generating_suggestions")
        db.commit()
        
        # 結果を保存
        analysis_task.complete_processing(
            analysis_result=analysis_result.model_dump(),
            suggestions=None,  # TODO: 改善提案生成機能と統合
            tokens_used=tokens_used,
            cost=cost
        )
        
        # セッションのステータス更新
        if analysis_task.session_id:
            session = db.query(SessionModel).filter(
                SessionModel.id == analysis_task.session_id
            ).first()
            if session:
                session.analysis_result = analysis_result.model_dump()
                session.update_status(SessionStatus.ANALYZED)
        
        db.commit()
        logger.info(f"Analysis task completed: {task_id}")
        
    except Exception as e:
        logger.error(f"Analysis task failed: {task_id} - {e}")
        
        # エラーを記録
        analysis_task = db.query(AnalysisTask).filter(
            AnalysisTask.task_id == task_id
        ).first()
        
        if analysis_task:
            analysis_task.fail_processing(str(e), "ANALYSIS_ERROR")
            db.commit()
    
    finally:
        db.close()

@router.post("/", response_model=AnalysisResponse)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI分析開始"""
    try:
        # 文字起こしタスク取得
        transcription_task = db.query(TranscriptionTask).filter(
            TranscriptionTask.id == request.transcription_id,
            TranscriptionTask.is_deleted == False
        ).first()
        
        if not transcription_task:
            raise HTTPException(status_code=404, detail="Transcription task not found")
        
        # 完了チェック
        if not transcription_task.is_completed:
            raise HTTPException(status_code=400, detail="Transcription not completed yet")
        
        # 権限チェック
        if transcription_task.session_id:
            session = db.query(SessionModel).filter(SessionModel.id == transcription_task.session_id).first()
            if session:
                customer = db.query(Customer).filter(Customer.id == session.customer_id).first()
                if current_user.role == "counselor" and customer.clinic_id != current_user.clinic_id:
                    raise HTTPException(status_code=403, detail="Access denied")
        
        # 既存の進行中分析タスクチェック
        existing_task = db.query(AnalysisTask).filter(
            AnalysisTask.transcription_task_id == request.transcription_id,
            AnalysisTask.status.in_(["pending", "preprocessing", "analyzing", "generating_suggestions"]),
            AnalysisTask.is_deleted == False
        ).first()
        
        if existing_task:
            raise HTTPException(
                status_code=400, 
                detail=f"Analysis already in progress: {existing_task.task_id}"
            )
        
        # タスクID生成
        task_id = str(uuid.uuid4())
        
        # 処理時間推定
        estimated_duration = 180  # 3分と仮定
        if request.analysis_type.value == "quick":
            estimated_duration = 60
        elif request.analysis_type.value == "specific":
            estimated_duration = 120
        
        # 分析タスク作成
        analysis_task = AnalysisTask(
            transcription_task_id=request.transcription_id,
            session_id=transcription_task.session_id,
            task_id=task_id,
            analysis_type=request.analysis_type.value,
            focus_areas=request.focus_areas,
            custom_prompts=request.custom_prompts,
            estimated_duration=estimated_duration,
            estimated_completion=datetime.utcnow() + timedelta(seconds=estimated_duration)
        )
        
        db.add(analysis_task)
        db.commit()
        
        # バックグラウンドタスク開始
        from app.core.config import settings
        background_tasks.add_task(
            analysis_background_task,
            task_id=task_id,
            transcription_task_id=str(request.transcription_id),
            transcription_text=transcription_task.transcription_text or "",
            analysis_type=request.analysis_type.value,
            focus_areas=request.focus_areas,
            custom_prompts=request.custom_prompts,
            db_url=str(settings.DATABASE_URL)
        )
        
        logger.info(f"Started analysis task: {task_id}")
        
        return AnalysisResponse(
            analysis_id=str(analysis_task.id),
            task_id=task_id,
            status="pending",
            estimated_duration=estimated_duration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status/{task_id}", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI分析状況取得"""
    try:
        # タスク取得
        analysis_task = db.query(AnalysisTask).filter(
            AnalysisTask.task_id == task_id,
            AnalysisTask.is_deleted == False
        ).first()
        
        if not analysis_task:
            raise HTTPException(status_code=404, detail="Analysis task not found")
        
        # 権限チェック
        if analysis_task.session_id:
            session = db.query(SessionModel).filter(SessionModel.id == analysis_task.session_id).first()
            if session:
                customer = db.query(Customer).filter(Customer.id == session.customer_id).first()
                if current_user.role == "counselor" and customer.clinic_id != current_user.clinic_id:
                    raise HTTPException(status_code=403, detail="Access denied")
        
        # 結果作成
        result = None
        if analysis_task.is_completed and analysis_task.full_analysis_result:
            from app.schemas.analysis import AnalysisResult
            result = AnalysisResult(**analysis_task.full_analysis_result)
        
        return AnalysisStatusResponse(
            analysis_id=str(analysis_task.id),
            task_id=analysis_task.task_id,
            status=analysis_task.status,
            progress=analysis_task.progress,
            stage=analysis_task.stage or "waiting",
            result=result,
            error=analysis_task.error_message,
            started_at=analysis_task.started_at or analysis_task.created_at,
            completed_at=analysis_task.completed_at,
            estimated_completion=analysis_task.estimated_completion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/result/{analysis_id}")
async def get_analysis_result(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI分析結果取得"""
    try:
        # 分析タスク取得
        analysis_task = db.query(AnalysisTask).filter(
            AnalysisTask.id == analysis_id,
            AnalysisTask.is_deleted == False
        ).first()
        
        if not analysis_task:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # 完了チェック
        if not analysis_task.is_completed:
            raise HTTPException(status_code=400, detail="Analysis not completed yet")
        
        # 権限チェック
        if analysis_task.session_id:
            session = db.query(SessionModel).filter(SessionModel.id == analysis_task.session_id).first()
            if session:
                customer = db.query(Customer).filter(Customer.id == session.customer_id).first()
                if current_user.role == "counselor" and customer.clinic_id != current_user.clinic_id:
                    raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "analysis_id": str(analysis_task.id),
            "transcription_id": str(analysis_task.transcription_task_id),
            "overall_score": analysis_task.overall_score,
            "analysis_details": analysis_task.full_analysis_result,
            "suggestions": analysis_task.suggestions,
            "created_at": analysis_task.created_at,
            "completed_at": analysis_task.completed_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis result: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/batch", response_model=BatchAnalysisResponse)
async def start_batch_analysis(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """バッチAI分析開始"""
    try:
        # 管理者またはマネージャーのみ
        if current_user.role not in ["admin", "manager"]:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # 文字起こしタスク存在チェック
        transcription_tasks = db.query(TranscriptionTask).filter(
            TranscriptionTask.id.in_(request.transcription_ids),
            TranscriptionTask.is_completed == True,
            TranscriptionTask.is_deleted == False
        ).all()
        
        if len(transcription_tasks) != len(request.transcription_ids):
            raise HTTPException(status_code=400, detail="Some transcription tasks not found or not completed")
        
        # 権限チェック（マネージャーは自分のクリニックのみ）
        if current_user.role == "manager":
            for task in transcription_tasks:
                if task.session_id:
                    session = db.query(SessionModel).filter(SessionModel.id == task.session_id).first()
                    if session:
                        customer = db.query(Customer).filter(Customer.id == session.customer_id).first()
                        if customer.clinic_id != current_user.clinic_id:
                            raise HTTPException(status_code=403, detail="Access denied to some sessions")
        
        batch_id = str(uuid.uuid4())
        task_ids = []
        
        # 各文字起こしに対して分析タスクを作成
        for transcription_task in transcription_tasks:
            task_id = str(uuid.uuid4())
            task_ids.append(task_id)
            
            estimated_duration = 180
            if request.analysis_type.value == "quick":
                estimated_duration = 60
            
            analysis_task = AnalysisTask(
                transcription_task_id=transcription_task.id,
                session_id=transcription_task.session_id,
                task_id=task_id,
                analysis_type=request.analysis_type.value,
                estimated_duration=estimated_duration,
                estimated_completion=datetime.utcnow() + timedelta(seconds=estimated_duration)
            )
            
            db.add(analysis_task)
            
            # バックグラウンドタスク開始
            from app.core.config import settings
            background_tasks.add_task(
                analysis_background_task,
                task_id=task_id,
                transcription_task_id=str(transcription_task.id),
                transcription_text=transcription_task.transcription_text or "",
                analysis_type=request.analysis_type.value,
                focus_areas=None,
                custom_prompts=None,
                db_url=str(settings.DATABASE_URL)
            )
        
        db.commit()
        
        logger.info(f"Started batch analysis: {batch_id} with {len(task_ids)} tasks")
        
        return BatchAnalysisResponse(
            batch_id=batch_id,
            task_ids=task_ids,
            total_count=len(task_ids),
            estimated_total_duration=len(task_ids) * 180
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start batch analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=AnalysisList)
async def list_analysis_tasks(
    transcription_id: Optional[str] = Query(None, description="Filter by transcription ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI分析タスク一覧取得"""
    try:
        query = db.query(AnalysisTask).filter(AnalysisTask.is_deleted == False)
        
        # フィルター適用
        if transcription_id:
            query = query.filter(AnalysisTask.transcription_task_id == transcription_id)
        
        if status:
            query = query.filter(AnalysisTask.status == status)
        
        # 権限フィルター
        if current_user.role == "counselor":
            # カウンセラーは自分のクリニックの分析のみ
            query = query.join(SessionModel, AnalysisTask.session_id == SessionModel.id)\
                        .join(Customer, SessionModel.customer_id == Customer.id)\
                        .filter(Customer.clinic_id == current_user.clinic_id)
        elif current_user.role == "manager":
            # マネージャーは自分のクリニックの分析のみ
            query = query.join(SessionModel, AnalysisTask.session_id == SessionModel.id)\
                        .join(Customer, SessionModel.customer_id == Customer.id)\
                        .filter(Customer.clinic_id == current_user.clinic_id)
        
        # 総数取得
        total = query.count()
        
        # ページング
        offset = (page - 1) * per_page
        analysis_tasks = query.order_by(AnalysisTask.created_at.desc()).offset(offset).limit(per_page).all()
        
        # レスポンス変換
        analysis_list = []
        for task in analysis_tasks:
            result = None
            if task.is_completed and task.full_analysis_result:
                from app.schemas.analysis import AnalysisResult
                result = AnalysisResult(**task.full_analysis_result)
            
            analysis_list.append(AnalysisStatusResponse(
                analysis_id=str(task.id),
                task_id=task.task_id,
                status=task.status,
                progress=task.progress,
                stage=task.stage or "waiting",
                result=result,
                error=task.error_message,
                started_at=task.started_at or task.created_at,
                completed_at=task.completed_at,
                estimated_completion=task.estimated_completion
            ))
        
        return AnalysisList(
            analyses=analysis_list,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Failed to list analysis tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats", response_model=AnalysisStats)
async def get_analysis_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI分析統計取得"""
    try:
        query = db.query(AnalysisTask).filter(AnalysisTask.is_deleted == False)
        
        # 権限フィルター
        if current_user.role == "counselor":
            query = query.join(SessionModel, AnalysisTask.session_id == SessionModel.id)\
                        .join(Customer, SessionModel.customer_id == Customer.id)\
                        .filter(Customer.clinic_id == current_user.clinic_id)
        elif current_user.role == "manager":
            query = query.join(SessionModel, AnalysisTask.session_id == SessionModel.id)\
                        .join(Customer, SessionModel.customer_id == Customer.id)\
                        .filter(Customer.clinic_id == current_user.clinic_id)
        
        # 統計計算
        all_tasks = query.all()
        total_analyses = len(all_tasks)
        
        if total_analyses == 0:
            return AnalysisStats(
                total_analyses=0,
                completed_analyses=0,
                failed_analyses=0,
                pending_analyses=0,
                processing_analyses=0,
                average_processing_time=0.0,
                average_overall_score=0.0,
                success_rate=0.0
            )
        
        completed_analyses = len([t for t in all_tasks if t.status == "completed"])
        failed_analyses = len([t for t in all_tasks if t.status == "failed"])
        pending_analyses = len([t for t in all_tasks if t.status == "pending"])
        processing_analyses = len([t for t in all_tasks if t.status in ["preprocessing", "analyzing", "generating_suggestions"]])
        
        # 平均処理時間
        processing_times = [t.actual_duration for t in all_tasks if t.actual_duration]
        average_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
        
        # 平均総合スコア
        scores = [t.overall_score for t in all_tasks if t.overall_score]
        average_overall_score = sum(scores) / len(scores) if scores else 0.0
        
        # 成功率
        success_rate = completed_analyses / total_analyses if total_analyses > 0 else 0.0
        
        return AnalysisStats(
            total_analyses=total_analyses,
            completed_analyses=completed_analyses,
            failed_analyses=failed_analyses,
            pending_analyses=pending_analyses,
            processing_analyses=processing_analyses,
            average_processing_time=average_processing_time,
            average_overall_score=average_overall_score,
            success_rate=success_rate
        )
        
    except Exception as e:
        logger.error(f"Failed to get analysis stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")