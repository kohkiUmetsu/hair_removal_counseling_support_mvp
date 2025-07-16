"""
Improvement suggestions API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.api.deps import get_db, get_current_user
from app.schemas.improvement import (
    SuggestionRequest, SuggestionResponse, ScriptGenerationRequest, ScriptGenerationResponse,
    SuccessPatternRequest, SuccessPatternResponse, FeedbackRequest, FeedbackResponse,
    PerformanceTrendRequest, PerformanceTrendResponse, SuggestionCategory, SuggestionPriority
)
from app.schemas.user import User
from app.schemas.analysis import AnalysisResult
from app.models.analysis import AnalysisTask, AnalysisFeedback
from app.models.session import Session as SessionModel
from app.models.customer import Customer
from app.services.improvement_service import ImprovementSuggestionService
from app.services.script_optimization_service import ScriptOptimizationService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{analysis_id}/suggestions", response_model=SuggestionResponse)
async def get_improvement_suggestions(
    analysis_id: str,
    include_script_recommendations: bool = Query(default=True),
    focus_categories: Optional[List[SuggestionCategory]] = Query(default=None),
    max_suggestions: int = Query(default=10, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """改善提案の取得"""
    try:
        # 分析タスクの取得
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
        
        # 分析結果の取得
        if not analysis_task.full_analysis_result:
            raise HTTPException(status_code=400, detail="Analysis result not available")
        
        analysis_result = AnalysisResult(**analysis_task.full_analysis_result)
        
        # 改善提案サービス
        improvement_service = ImprovementSuggestionService(db)
        
        # 改善提案の生成
        suggestions = improvement_service.generate_suggestions(analysis_result)
        
        # フォーカスカテゴリによるフィルタリング
        if focus_categories:
            suggestions = [s for s in suggestions if s.category in focus_categories]
        
        # 上位制限
        suggestions = suggestions[:max_suggestions]
        
        # 優先度の高い改善提案
        priority_actions = [s for s in suggestions if s.priority.value == "high"][:3]
        
        # スクリプト推奨事項
        script_recommendations = None
        if include_script_recommendations:
            script_recommendations = [
                "オープンクエスチョンの活用を増やす",
                "共感表現を意識的に取り入れる", 
                "クロージングのタイミングを改善する"
            ]
        
        # 成功パターンの取得
        success_patterns = improvement_service.get_success_patterns(
            clinic_id=customer.clinic_id if analysis_task.session_id else None,
            days=30
        )
        
        return SuggestionResponse(
            suggestions=suggestions,
            priority_actions=priority_actions,
            script_recommendations=script_recommendations,
            success_patterns=success_patterns
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get improvement suggestions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/generate-script", response_model=ScriptGenerationResponse)
async def generate_optimized_script(
    request: ScriptGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """最適化スクリプトの生成"""
    try:
        # 顧客IDが指定されている場合の権限チェック
        if request.customer_id:
            customer = db.query(Customer).filter(
                Customer.id == request.customer_id,
                Customer.is_deleted == False
            ).first()
            
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")
            
            if current_user.role == "counselor" and customer.clinic_id != current_user.clinic_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # スクリプト最適化サービス
        script_service = ScriptOptimizationService(db)
        improvement_service = ImprovementSuggestionService(db)
        
        # 成功パターンの取得
        clinic_id = None
        if request.customer_id:
            customer = db.query(Customer).filter(Customer.id == request.customer_id).first()
            clinic_id = customer.clinic_id if customer else None
        elif current_user.role in ["counselor", "manager"]:
            clinic_id = current_user.clinic_id
        
        success_patterns = improvement_service.get_success_patterns(
            clinic_id=clinic_id,
            days=30
        )
        
        # 最適化スクリプトの生成
        optimized_script = script_service.generate_optimized_script(
            request=request,
            success_patterns=success_patterns
        )
        
        # カスタマイズ適用内容
        customization_applied = []
        if request.focus_areas:
            customization_applied.append(f"フォーカス分野: {', '.join(request.focus_areas)}")
        if request.customer_profile:
            customization_applied.append("顧客プロファイルに基づくカスタマイズ")
        if request.previous_analysis_ids:
            customization_applied.append("過去の分析結果を反映")
        
        return ScriptGenerationResponse(
            script_id=optimized_script.script_id,
            optimized_script=optimized_script,
            success_probability=optimized_script.success_probability,
            customization_applied=customization_applied
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate optimized script: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/success-patterns", response_model=SuccessPatternResponse)
async def get_success_patterns(
    clinic_id: Optional[str] = Query(None),
    counselor_id: Optional[str] = Query(None),
    days: int = Query(default=30, ge=7, le=365),
    min_score: float = Query(default=8.0, ge=0.0, le=10.0),
    pattern_types: Optional[List[str]] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """成功パターンの取得"""
    try:
        # 権限チェック
        effective_clinic_id = clinic_id
        if current_user.role == "counselor":
            effective_clinic_id = current_user.clinic_id
        elif current_user.role == "manager":
            if clinic_id and clinic_id != current_user.clinic_id:
                raise HTTPException(status_code=403, detail="Access denied")
            effective_clinic_id = current_user.clinic_id
        
        # 改善提案サービス
        improvement_service = ImprovementSuggestionService(db)
        
        # 成功パターンの取得
        patterns = improvement_service.get_success_patterns(
            clinic_id=effective_clinic_id,
            counselor_id=counselor_id,
            days=days
        )
        
        # パターンタイプによるフィルタリング
        if pattern_types:
            patterns = [p for p in patterns if p.pattern_type in pattern_types]
        
        # ベストプラクティスの生成（簡易版）
        best_practices = []
        for pattern in patterns[:5]:  # 上位5パターン
            from app.schemas.improvement import BestPractice
            best_practice = BestPractice(
                title=f"{pattern.pattern_name}の活用",
                description=pattern.description,
                category=SuggestionCategory.GENERAL,  # デフォルトカテゴリを使用
                effectiveness_score=pattern.effectiveness_score,
                adoption_rate=pattern.success_rate,
                implementation_tips=[
                    "段階的な導入を推奨",
                    "定期的な効果測定",
                    "フィードバックの活用"
                ]
            )
            best_practices.append(best_practice)
        
        # サマリー統計
        summary_stats = {
            "total_patterns": len(patterns),
            "average_success_rate": sum(p.success_rate for p in patterns) / len(patterns) if patterns else 0.0,
            "average_effectiveness": sum(p.effectiveness_score for p in patterns) / len(patterns) if patterns else 0.0,
            "analysis_period_days": days
        }
        
        return SuccessPatternResponse(
            patterns=patterns,
            best_practices=best_practices,
            summary_stats=summary_stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get success patterns: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_improvement_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """改善提案フィードバックの送信"""
    try:
        # 分析タスクの取得と権限チェック
        analysis_task = db.query(AnalysisTask).filter(
            AnalysisTask.id == request.analysis_id,
            AnalysisTask.is_deleted == False
        ).first()
        
        if not analysis_task:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # 権限チェック
        if analysis_task.session_id:
            session = db.query(SessionModel).filter(SessionModel.id == analysis_task.session_id).first()
            if session:
                customer = db.query(Customer).filter(Customer.id == session.customer_id).first()
                if current_user.role == "counselor" and customer.clinic_id != current_user.clinic_id:
                    raise HTTPException(status_code=403, detail="Access denied")
        
        # フィードバックの保存
        feedback = AnalysisFeedback(
            analysis_task_id=analysis_task.id,
            user_id=current_user.id,
            rating=request.rating or 3,  # デフォルト評価
            feedback_text=request.comments,
            category_ratings={
                "feedback_type": request.feedback_type,
                "implementation_status": request.implementation_status
            },
            suggestions_helpful=request.feedback_type in ["helpful", "implemented"],
            accuracy_rating=request.rating,
            improvement_suggestions=request.comments
        )
        
        db.add(feedback)
        db.commit()
        
        logger.info(f"Feedback submitted for analysis {request.analysis_id} by user {current_user.id}")
        
        return FeedbackResponse(
            feedback_id=str(feedback.id),
            status="received",
            message="フィードバックありがとうございます。今後のサービス向上に活用させていただきます。"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/performance-trends/{counselor_id}", response_model=PerformanceTrendResponse)
async def get_performance_trends(
    counselor_id: str,
    days: int = Query(default=30, ge=7, le=365),
    comparison_period: Optional[int] = Query(None, ge=7, le=365),
    include_predictions: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """パフォーマンストレンドの取得"""
    try:
        # 権限チェック
        if current_user.role == "counselor" and str(current_user.id) != counselor_id:
            raise HTTPException(status_code=403, detail="Access denied")
        elif current_user.role == "manager":
            # マネージャーは同じクリニックのカウンセラーのみ
            from app.models.user import User as UserModel
            target_user = db.query(UserModel).filter(UserModel.id == counselor_id).first()
            if not target_user or target_user.clinic_id != current_user.clinic_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # 改善提案サービス
        improvement_service = ImprovementSuggestionService(db)
        
        # パフォーマンストレンドの生成
        trend_data = improvement_service.generate_performance_trend(
            counselor_id=counselor_id,
            days=days
        )
        
        # 改善軌跡データ（簡易版）
        improvement_trajectory = None
        if include_predictions:
            improvement_trajectory = [
                {"period": "過去30日", "score": trend_data.previous_average},
                {"period": "現在", "score": trend_data.current_average},
                {"period": "予測（30日後）", "score": min(10.0, trend_data.current_average + 0.5)}
            ]
        
        # 推奨事項の生成
        from app.schemas.improvement import ImprovementRecommendation
        recommendations = []
        
        if trend_data.trend_direction == "declining":
            recommendations.append(ImprovementRecommendation(
                title="スキル向上トレーニングの実施",
                description="パフォーマンス低下が見られます。基本スキルの見直しを推奨します。",
                category=SuggestionCategory.GENERAL,
                priority=SuggestionPriority.HIGH,
                expected_timeframe_days=14,
                resource_requirements=["トレーニング時間", "指導者のサポート"],
                success_metrics=["平均スコア向上", "顧客満足度改善"]
            ))
        elif trend_data.trend_direction == "improving":
            recommendations.append(ImprovementRecommendation(
                title="現在の成功パターンの維持",
                description="良好な改善傾向です。現在のアプローチを継続してください。",
                category=SuggestionCategory.GENERAL,
                priority=SuggestionPriority.MEDIUM,
                expected_timeframe_days=30,
                resource_requirements=["現状維持の意識"],
                success_metrics=["継続的な改善", "安定したパフォーマンス"]
            ))
        
        # 次回レビュー日の設定
        from datetime import datetime, timedelta
        next_review_date = datetime.utcnow() + timedelta(days=14)
        
        return PerformanceTrendResponse(
            trend_data=trend_data,
            improvement_trajectory=improvement_trajectory,
            recommendations=recommendations,
            next_review_date=next_review_date
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get performance trends: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")