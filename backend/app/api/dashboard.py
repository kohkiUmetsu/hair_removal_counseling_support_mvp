"""
Dashboard and analytics API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Union
import logging
from datetime import datetime, timedelta
import uuid

from app.api.deps import get_db, get_current_user
from app.schemas.dashboard import (
    ExecutiveDashboard, CounselorDashboard, OperationDashboard,
    DashboardFilters, PerformanceReportFilters, PerformanceReport,
    CustomReportRequest, CustomReportResponse, TrendAnalysisRequest, TrendAnalysisResponse,
    ExportRequest, ExportResponse
)
from app.schemas.user import User
from app.models.user import User as UserModel
from app.models.clinic import Clinic
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/executive", response_model=ExecutiveDashboard)
async def get_executive_dashboard(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    clinic_id: Optional[str] = Query(None),
    time_zone: str = Query(default="Asia/Tokyo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """エグゼクティブダッシュボード取得"""
    try:
        # 管理者またはマネージャーのみアクセス可能
        if current_user.role not in ["admin", "manager"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # デフォルト期間設定（過去30日）
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # マネージャーは自分のクリニックのみ
        effective_clinic_id = clinic_id
        if current_user.role == "manager":
            effective_clinic_id = current_user.clinic_id
        
        # フィルター設定
        filters = DashboardFilters(
            start_date=start_date,
            end_date=end_date,
            clinic_id=effective_clinic_id
        )
        
        # 分析サービス
        analytics_service = AnalyticsService(db)
        dashboard_data = await analytics_service.get_executive_dashboard(filters)
        
        logger.info(f"Executive dashboard requested by user {current_user.id}")
        return dashboard_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get executive dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/counselor/{counselor_id}", response_model=CounselorDashboard)
async def get_counselor_dashboard(
    counselor_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    comparison_period: Optional[int] = Query(None, description="Comparison period in days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """カウンセラーダッシュボード取得"""
    try:
        # 権限チェック
        if current_user.role == "counselor" and str(current_user.id) != counselor_id:
            raise HTTPException(status_code=403, detail="Access denied")
        elif current_user.role == "manager":
            # マネージャーは同じクリニックのカウンセラーのみ
            target_user = db.query(UserModel).filter(UserModel.id == counselor_id).first()
            if not target_user or target_user.clinic_id != current_user.clinic_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # 対象カウンセラーの存在確認
        counselor = db.query(UserModel).filter(
            UserModel.id == counselor_id,
            UserModel.role == "counselor",
            UserModel.is_deleted == False
        ).first()
        
        if not counselor:
            raise HTTPException(status_code=404, detail="Counselor not found")
        
        # デフォルト期間設定（過去30日）
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # フィルター設定
        filters = DashboardFilters(
            start_date=start_date,
            end_date=end_date,
            counselor_id=counselor_id
        )
        
        # 分析サービス
        analytics_service = AnalyticsService(db)
        dashboard_data = await analytics_service.get_counselor_dashboard(counselor_id, filters)
        
        logger.info(f"Counselor dashboard requested for {counselor_id} by user {current_user.id}")
        return dashboard_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get counselor dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/operations", response_model=OperationDashboard)
async def get_operations_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """オペレーションダッシュボード取得"""
    try:
        # 管理者のみアクセス可能
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # 分析サービス
        analytics_service = AnalyticsService(db)
        dashboard_data = await analytics_service.get_operation_dashboard()
        
        logger.info(f"Operations dashboard requested by user {current_user.id}")
        return dashboard_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get operations dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/performance-report", response_model=PerformanceReport)
async def get_performance_report(
    report_type: str = Query(..., regex="^(counselor|clinic|customer)$"),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    clinic_ids: Optional[List[str]] = Query(None),
    counselor_ids: Optional[List[str]] = Query(None),
    format: str = Query(default="json", regex="^(json|csv|pdf)$"),
    min_sessions: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """パフォーマンスレポート取得"""
    try:
        # 権限チェック
        if current_user.role == "counselor":
            # カウンセラーは自分のレポートのみ
            if counselor_ids and str(current_user.id) not in counselor_ids:
                raise HTTPException(status_code=403, detail="Access denied")
            counselor_ids = [str(current_user.id)]
        elif current_user.role == "manager":
            # マネージャーは自分のクリニックのみ
            if clinic_ids and current_user.clinic_id not in clinic_ids:
                raise HTTPException(status_code=403, detail="Access denied")
            clinic_ids = [current_user.clinic_id]
        
        # レポートフィルター
        filters = PerformanceReportFilters(
            start_date=start_date,
            end_date=end_date,
            clinic_ids=clinic_ids,
            counselor_ids=counselor_ids,
            min_sessions=min_sessions
        )
        
        # レポート生成（簡易版）
        report_id = str(uuid.uuid4())
        
        if report_type == "counselor":
            report_data = await _generate_counselor_report(db, filters)
        elif report_type == "clinic":
            report_data = await _generate_clinic_report(db, filters)
        else:
            report_data = await _generate_customer_report(db, filters)
        
        report = PerformanceReport(
            report_id=report_id,
            report_type=report_type,
            summary=report_data.get("summary", {}),
            detailed_data=report_data.get("detailed_data", []),
            recommendations=report_data.get("recommendations", [])
        )
        
        logger.info(f"Performance report generated: {report_id} by user {current_user.id}")
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate performance report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/custom-report", response_model=CustomReportResponse)
async def create_custom_report(
    request: CustomReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """カスタムレポート作成"""
    try:
        # 管理者またはマネージャーのみ
        if current_user.role not in ["admin", "manager"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # 権限フィルター適用
        if current_user.role == "manager":
            if request.filters.clinic_ids:
                if current_user.clinic_id not in request.filters.clinic_ids:
                    raise HTTPException(status_code=403, detail="Access denied")
            else:
                request.filters.clinic_ids = [current_user.clinic_id]
        
        # カスタムレポート生成（簡易版）
        report_id = str(uuid.uuid4())
        
        # データ取得と集計
        data = await _execute_custom_query(db, request)
        
        # 可視化設定
        visualization_config = {
            "type": request.visualization_type,
            "metrics": request.metrics,
            "dimensions": request.dimensions
        }
        
        response = CustomReportResponse(
            report_id=report_id,
            query_executed=f"Custom {request.visualization_type} report",
            data=data,
            metadata={
                "total_records": len(data),
                "aggregation_method": request.aggregation_method,
                "execution_time_ms": 150  # 固定値
            },
            visualization_config=visualization_config
        )
        
        logger.info(f"Custom report created: {report_id} by user {current_user.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create custom report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/trends", response_model=TrendAnalysisResponse)
async def get_trend_analysis(
    metric: str = Query(..., description="Metric to analyze"),
    time_period: str = Query(..., regex="^(7d|30d|90d|1y)$"),
    granularity: str = Query(default="daily", regex="^(hourly|daily|weekly|monthly)$"),
    counselor_ids: Optional[List[str]] = Query(None),
    clinic_ids: Optional[List[str]] = Query(None),
    include_forecast: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """トレンド分析取得"""
    try:
        # 権限チェック
        effective_clinic_ids = clinic_ids
        if current_user.role == "counselor":
            raise HTTPException(status_code=403, detail="Access denied")
        elif current_user.role == "manager":
            effective_clinic_ids = [current_user.clinic_id]
        
        # トレンド分析リクエスト
        trend_request = TrendAnalysisRequest(
            metric=metric,
            time_period=time_period,
            granularity=granularity,
            counselor_ids=counselor_ids,
            clinic_ids=effective_clinic_ids,
            include_forecast=include_forecast
        )
        
        # トレンド分析実行（簡易版）
        trend_data = await _analyze_trends(db, trend_request)
        
        from app.schemas.dashboard import TrendDirection
        response = TrendAnalysisResponse(
            metric=metric,
            trend_data=trend_data.get("trend_data", []),
            trend_direction=TrendDirection.STABLE,  # 簡易版
            statistical_summary=trend_data.get("summary", {}),
            insights=trend_data.get("insights", [])
        )
        
        logger.info(f"Trend analysis requested for {metric} by user {current_user.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get trend analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/export", response_model=ExportResponse)
async def export_dashboard_data(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ダッシュボードデータのエクスポート"""
    try:
        # 権限チェック
        if current_user.role == "counselor":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # エクスポートID生成
        export_id = str(uuid.uuid4())
        
        # バックグラウンドでエクスポート処理を開始
        background_tasks.add_task(
            _process_export,
            export_id=export_id,
            request=request,
            user_id=str(current_user.id)
        )
        
        response = ExportResponse(
            export_id=export_id,
            status="pending",
            generated_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        logger.info(f"Export requested: {export_id} by user {current_user.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to initiate export: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/export/{export_id}/status")
async def get_export_status(
    export_id: str,
    current_user: User = Depends(get_current_user)
):
    """エクスポート状況確認"""
    try:
        # 実際の実装では、エクスポートタスクの状況をデータベースから取得
        # ここでは簡易的なレスポンスを返す
        return {
            "export_id": export_id,
            "status": "completed",
            "file_url": f"/api/v1/exports/{export_id}/download",
            "file_size_mb": 2.5,
            "expires_at": datetime.utcnow() + timedelta(hours=20)
        }
        
    except Exception as e:
        logger.error(f"Failed to get export status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Helper functions
async def _generate_counselor_report(db: Session, filters: PerformanceReportFilters) -> Dict:
    """カウンセラーレポート生成"""
    # 簡易版実装
    return {
        "summary": {
            "total_counselors": 5,
            "average_score": 7.5,
            "top_performer": "田中 太郎"
        },
        "detailed_data": [
            {"counselor": "田中 太郎", "sessions": 25, "avg_score": 8.2},
            {"counselor": "佐藤 花子", "sessions": 22, "avg_score": 7.8}
        ],
        "recommendations": [
            "質問技法の向上トレーニングを推奨",
            "成功事例の共有セッションを実施"
        ]
    }

async def _generate_clinic_report(db: Session, filters: PerformanceReportFilters) -> Dict:
    """クリニックレポート生成"""
    return {
        "summary": {
            "total_clinics": 3,
            "total_sessions": 150,
            "average_clinic_score": 7.3
        },
        "detailed_data": [
            {"clinic": "新宿クリニック", "sessions": 80, "avg_score": 7.8},
            {"clinic": "渋谷クリニック", "sessions": 70, "avg_score": 6.9}
        ],
        "recommendations": [
            "クリニック間でのベストプラクティス共有",
            "低スコアクリニックへの追加サポート"
        ]
    }

async def _generate_customer_report(db: Session, filters: PerformanceReportFilters) -> Dict:
    """顧客レポート生成"""
    return {
        "summary": {
            "total_customers": 120,
            "satisfaction_rate": 0.85,
            "repeat_rate": 0.72
        },
        "detailed_data": [
            {"customer_type": "初回", "satisfaction": 8.1, "count": 80},
            {"customer_type": "リピート", "satisfaction": 8.5, "count": 40}
        ],
        "recommendations": [
            "初回顧客への丁寧な対応を強化",
            "リピート顧客への特別サービス提供"
        ]
    }

async def _execute_custom_query(db: Session, request: CustomReportRequest) -> List[Dict]:
    """カスタムクエリ実行"""
    # 簡易版実装
    return [
        {"metric1": 7.5, "metric2": 8.2, "dimension1": "カテゴリA"},
        {"metric1": 6.8, "metric2": 7.9, "dimension1": "カテゴリB"}
    ]

async def _analyze_trends(db: Session, request: TrendAnalysisRequest) -> Dict:
    """トレンド分析実行"""
    from app.schemas.dashboard import TrendData
    
    # 簡易版実装
    trend_data = []
    base_date = datetime.utcnow() - timedelta(days=7)
    
    for i in range(7):
        trend_data.append(TrendData(
            date=base_date + timedelta(days=i),
            value=7.0 + (i * 0.1),  # 上昇トレンド
            change_from_previous=0.1 if i > 0 else 0.0
        ))
    
    return {
        "trend_data": trend_data,
        "summary": {
            "min_value": 7.0,
            "max_value": 7.6,
            "average": 7.3,
            "trend_slope": 0.1
        },
        "insights": [
            "過去7日間で改善傾向が見られます",
            "継続的なトレーニング効果が現れています"
        ]
    }

async def _process_export(export_id: str, request: ExportRequest, user_id: str):
    """エクスポート処理（バックグラウンド）"""
    try:
        # 実際の実装では、データの取得、フォーマット変換、ファイル生成を行う
        logger.info(f"Processing export {export_id} for user {user_id}")
        
        # ファイル生成のシミュレーション
        import time
        time.sleep(2)  # 処理時間のシミュレーション
        
        # 実際の実装では、生成されたファイルのURLやステータスをデータベースに保存
        logger.info(f"Export {export_id} completed")
        
    except Exception as e:
        logger.error(f"Export {export_id} failed: {e}")
        # エラー状況をデータベースに記録