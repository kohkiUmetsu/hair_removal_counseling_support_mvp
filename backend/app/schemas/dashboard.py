"""
Dashboard and analytics schemas
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from datetime import datetime
from enum import Enum

class HealthStatus(str, Enum):
    """システム健全性ステータス"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class TrendDirection(str, Enum):
    """トレンド方向"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
    UNKNOWN = "unknown"

class DashboardFilters(BaseModel):
    """ダッシュボードフィルター"""
    start_date: datetime
    end_date: datetime
    clinic_id: Optional[str] = None
    counselor_id: Optional[str] = None
    customer_type: Optional[str] = None
    session_status: Optional[str] = None

class KPIMetrics(BaseModel):
    """KPI メトリクス"""
    conversion_rate: float = Field(..., ge=0.0, le=1.0, description="成約率")
    average_session_score: float = Field(..., ge=0.0, le=10.0, description="平均セッションスコア")
    monthly_revenue: float = Field(..., ge=0.0, description="月間売上")
    customer_satisfaction: float = Field(..., ge=0.0, le=10.0, description="顧客満足度")
    total_sessions: int = Field(..., ge=0, description="総セッション数")
    completed_sessions: int = Field(..., ge=0, description="完了セッション数")

class TrendData(BaseModel):
    """トレンドデータ"""
    date: datetime
    value: float
    change_from_previous: float = 0.0
    trend_direction: Optional[TrendDirection] = None

class PerformanceData(BaseModel):
    """パフォーマンスデータ"""
    date: datetime
    score: float = Field(..., ge=0.0, le=10.0)
    session_id: str
    customer_satisfaction: Optional[float] = Field(None, ge=0.0, le=10.0)
    notes: Optional[str] = None

class VolumeData(BaseModel):
    """ボリュームデータ"""
    date: datetime
    volume: int = Field(..., ge=0)
    type: str = Field(..., description="daily, weekly, monthly")
    change_rate: Optional[float] = None

class QualityMetrics(BaseModel):
    """品質メトリクス"""
    transcription_accuracy: float = Field(..., ge=0.0, le=100.0, description="文字起こし精度")
    analysis_reliability: float = Field(..., ge=0.0, le=100.0, description="分析信頼性")
    user_satisfaction: float = Field(..., ge=0.0, le=100.0, description="ユーザー満足度")
    data_completeness: float = Field(..., ge=0.0, le=100.0, description="データ完全性")

class OpportunityItem(BaseModel):
    """改善機会項目"""
    category: str = Field(..., description="カテゴリ")
    issue_count: int = Field(..., ge=0, description="問題数")
    priority: str = Field(..., description="優先度")
    recommendation: str = Field(..., description="推奨事項")
    potential_impact: Optional[float] = Field(None, ge=0.0, le=10.0)

class TopPerformer(BaseModel):
    """トップパフォーマー"""
    counselor_id: str
    name: str
    session_count: int = Field(..., ge=0)
    average_score: float = Field(..., ge=0.0, le=10.0)
    rank: int = Field(..., ge=1)
    improvement_rate: Optional[float] = None

class ExecutiveDashboard(BaseModel):
    """エグゼクティブダッシュボード"""
    kpis: KPIMetrics
    trends: Dict[str, List[TrendData]]
    top_performers: List[Dict[str, Union[str, float, int]]]
    improvement_opportunities: List[Dict[str, Union[str, int, float]]]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    summary_insights: Optional[List[str]] = Field(default_factory=list)

class SkillScore(BaseModel):
    """スキルスコア"""
    score: float = Field(..., ge=0.0, le=10.0)
    sessions_analyzed: int = Field(..., ge=0)
    trend: Optional[TrendDirection] = None
    percentile: Optional[float] = Field(None, ge=0.0, le=100.0)

class CounselorStats(BaseModel):
    """カウンセラー統計"""
    total_sessions: int = Field(..., ge=0)
    average_score: float = Field(..., ge=0.0, le=10.0)
    conversion_rate: float = Field(..., ge=0.0, le=1.0)
    improvement_rate: float = Field(..., description="改善率（%）")
    rank_in_clinic: Optional[int] = Field(None, ge=1)
    months_experience: Optional[int] = Field(None, ge=0)

class CounselorDashboard(BaseModel):
    """カウンセラーダッシュボード"""
    counselor_stats: Dict[str, Union[int, float]]
    skill_breakdown: Dict[str, Dict[str, float]]
    recent_performance: List[PerformanceData]
    personalized_recommendations: List[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    next_review_date: Optional[datetime] = None

class RealTimeMetrics(BaseModel):
    """リアルタイムメトリクス"""
    active_sessions: int = Field(..., ge=0)
    processing_queue: int = Field(..., ge=0)
    system_health: str
    last_updated: str
    server_load: Optional[float] = Field(None, ge=0.0, le=100.0)

class SessionAnalytics(BaseModel):
    """セッション分析"""
    daily_volume: List[VolumeData]
    average_processing_time: float = Field(..., ge=0.0)
    error_rate: float = Field(..., ge=0.0, le=100.0)
    total_tasks_week: int = Field(..., ge=0)
    peak_hours: Optional[List[int]] = Field(default_factory=list)

class OperationDashboard(BaseModel):
    """オペレーションダッシュボード"""
    real_time_metrics: Dict[str, Union[int, str, float]]
    session_analytics: Dict[str, Union[List[VolumeData], float, int]]
    quality_metrics: QualityMetrics
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    alerts: Optional[List[str]] = Field(default_factory=list)

# Request/Response schemas
class DashboardRequest(BaseModel):
    """ダッシュボードリクエスト"""
    filters: DashboardFilters
    include_trends: bool = Field(default=True)
    include_predictions: bool = Field(default=False)
    granularity: str = Field(default="daily", regex="^(hourly|daily|weekly|monthly)$")

class PerformanceReportFilters(BaseModel):
    """パフォーマンスレポートフィルター"""
    start_date: datetime
    end_date: datetime
    clinic_ids: Optional[List[str]] = None
    counselor_ids: Optional[List[str]] = None
    min_sessions: int = Field(default=1, ge=1)
    include_skill_breakdown: bool = Field(default=True)
    include_customer_feedback: bool = Field(default=True)

class PerformanceReport(BaseModel):
    """パフォーマンスレポート"""
    report_id: str
    report_type: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    summary: Dict[str, Union[str, int, float]]
    detailed_data: List[Dict[str, Union[str, int, float]]]
    charts_data: Optional[Dict[str, List[Dict]]] = None
    recommendations: List[str] = Field(default_factory=list)

class CustomReportRequest(BaseModel):
    """カスタムレポートリクエスト"""
    metrics: List[str] = Field(..., min_items=1)
    dimensions: List[str] = Field(..., min_items=1)
    filters: PerformanceReportFilters
    visualization_type: str = Field(..., regex="^(table|chart|graph|heatmap)$")
    aggregation_method: str = Field(default="avg", regex="^(sum|avg|count|min|max)$")

class CustomReportResponse(BaseModel):
    """カスタムレポートレスポンス"""
    report_id: str
    query_executed: str
    data: List[Dict[str, Union[str, int, float]]]
    metadata: Dict[str, Union[str, int]]
    visualization_config: Dict[str, Union[str, List]]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class TrendAnalysisRequest(BaseModel):
    """トレンド分析リクエスト"""
    metric: str = Field(..., description="分析対象メトリクス")
    time_period: str = Field(..., regex="^(7d|30d|90d|1y)$")
    granularity: str = Field(default="daily", regex="^(hourly|daily|weekly|monthly)$")
    counselor_ids: Optional[List[str]] = None
    clinic_ids: Optional[List[str]] = None
    include_forecast: bool = Field(default=False)

class TrendAnalysisResponse(BaseModel):
    """トレンド分析レスポンス"""
    metric: str
    trend_data: List[TrendData]
    trend_direction: TrendDirection
    statistical_summary: Dict[str, float]
    forecast_data: Optional[List[TrendData]] = None
    insights: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class AlertConfiguration(BaseModel):
    """アラート設定"""
    alert_type: str = Field(..., regex="^(threshold|trend|anomaly)$")
    metric: str
    threshold_value: Optional[float] = None
    comparison_operator: Optional[str] = Field(None, regex="^(gt|lt|eq|gte|lte)$")
    notification_channels: List[str] = Field(default_factory=list)
    is_active: bool = Field(default=True)

class DashboardAlert(BaseModel):
    """ダッシュボードアラート"""
    alert_id: str
    alert_type: str
    severity: str = Field(..., regex="^(info|warning|critical)$")
    message: str
    metric_value: float
    threshold_value: Optional[float] = None
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    is_acknowledged: bool = Field(default=False)

# Export schemas
class ExportRequest(BaseModel):
    """エクスポートリクエスト"""
    export_type: str = Field(..., regex="^(csv|pdf|excel|json)$")
    data_source: str = Field(..., regex="^(dashboard|report|analysis)$")
    filters: PerformanceReportFilters
    include_charts: bool = Field(default=True)
    email_recipients: Optional[List[str]] = None

class ExportResponse(BaseModel):
    """エクスポートレスポンス"""
    export_id: str
    file_url: Optional[str] = None
    file_size_mb: Optional[float] = None
    status: str = Field(..., regex="^(pending|completed|failed)$")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None