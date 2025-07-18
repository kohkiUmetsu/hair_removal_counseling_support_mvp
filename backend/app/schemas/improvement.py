"""
Improvement and suggestion schemas
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from datetime import datetime
from enum import Enum
import uuid

class SuggestionPriority(str, Enum):
    """改善提案の優先度"""
    HIGH = "high"
    MEDIUM = "medium" 
    LOW = "low"

class SuggestionCategory(str, Enum):
    """改善提案のカテゴリ"""
    QUESTIONING = "questioning"
    ANXIETY_HANDLING = "anxiety_handling"
    CLOSING = "closing"
    FLOW = "flow"
    GENERAL = "general"

class ImplementationDifficulty(str, Enum):
    """実装難易度"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Suggestion(BaseModel):
    """改善提案"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    category: SuggestionCategory
    priority: SuggestionPriority
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    example_script: Optional[str] = Field(None, max_length=2000)
    expected_impact: str = Field(..., max_length=500)
    implementation_difficulty: ImplementationDifficulty
    expected_impact_score: float = Field(..., ge=0.0, le=10.0)
    success_rate: float = Field(..., ge=0.0, le=1.0)
    related_best_practices: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ScriptSection(BaseModel):
    """スクリプトセクション"""
    content: str = Field(..., min_length=1, max_length=2000)
    key_points: List[str] = Field(default_factory=list)
    alternative_phrases: List[str] = Field(default_factory=list)
    timing_notes: Optional[str] = Field(None, max_length=500)
    body_language_tips: List[str] = Field(default_factory=list)
    estimated_duration_minutes: Optional[float] = Field(None, ge=0.0)

class OptimizedScript(BaseModel):
    """最適化スクリプト"""
    script_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_type: str = Field(..., max_length=100)
    opening: ScriptSection
    needs_assessment: ScriptSection
    presentation: ScriptSection
    objection_handling: Dict[str, ScriptSection] = Field(default_factory=dict)
    closing: ScriptSection
    success_probability: float = Field(..., ge=0.0, le=1.0)
    customization_notes: List[str] = Field(default_factory=list)
    total_estimated_duration: Optional[float] = Field(None, ge=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SuccessPatternData(BaseModel):
    """成功パターンデータ"""
    pattern_type: str = Field(..., max_length=100)
    pattern_name: str = Field(..., max_length=200)
    description: str = Field(..., max_length=1000)
    success_rate: float = Field(..., ge=0.0, le=1.0)
    usage_frequency: int = Field(..., ge=0)
    effectiveness_score: float = Field(..., ge=0.0, le=10.0)
    example_sessions: List[str] = Field(default_factory=list)
    counselor_performance_correlation: Optional[float] = Field(None, ge=-1.0, le=1.0)

class BestPractice(BaseModel):
    """ベストプラクティス"""
    practice_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=1000)
    category: SuggestionCategory
    effectiveness_score: float = Field(..., ge=0.0, le=10.0)
    adoption_rate: float = Field(..., ge=0.0, le=1.0)
    implementation_tips: List[str] = Field(default_factory=list)
    success_stories: List[str] = Field(default_factory=list)

class ImprovementRecommendation(BaseModel):
    """改善推奨事項"""
    recommendation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=1000)
    category: SuggestionCategory
    priority: SuggestionPriority
    expected_timeframe_days: int = Field(..., ge=1)
    resource_requirements: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)
    related_suggestions: List[str] = Field(default_factory=list)

class PerformanceTrend(BaseModel):
    """パフォーマンストレンド"""
    trend_direction: str = Field(..., pattern="^(improving|declining|stable|unknown)$")
    improvement_rate: float = Field(..., description="Percentage improvement rate")
    current_average: float = Field(..., ge=0.0, le=10.0)
    previous_average: float = Field(..., ge=0.0, le=10.0)
    key_improvements: List[str] = Field(default_factory=list)
    areas_needing_attention: List[str] = Field(default_factory=list)
    confidence_level: float = Field(default=0.8, ge=0.0, le=1.0)

# Request/Response schemas
class SuggestionRequest(BaseModel):
    """改善提案リクエスト"""
    analysis_id: str
    include_script_recommendations: bool = Field(default=True)
    focus_categories: Optional[List[SuggestionCategory]] = None
    max_suggestions: int = Field(default=10, ge=1, le=20)

class SuggestionResponse(BaseModel):
    """改善提案レスポンス"""
    suggestions: List[Suggestion]
    priority_actions: List[Suggestion]
    script_recommendations: Optional[List[str]] = None
    success_patterns: List[SuccessPatternData] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class ScriptGenerationRequest(BaseModel):
    """スクリプト生成リクエスト"""
    customer_id: Optional[str] = None
    customer_profile: Optional[Dict[str, Union[str, int, float]]] = None
    session_type: str = Field(..., max_length=100)
    focus_areas: List[str] = Field(default_factory=list)
    previous_analysis_ids: List[str] = Field(default_factory=list)
    customization_preferences: Dict[str, Union[str, bool]] = Field(default_factory=dict)

class ScriptGenerationResponse(BaseModel):
    """スクリプト生成レスポンス"""
    script_id: str
    optimized_script: OptimizedScript
    success_probability: float = Field(..., ge=0.0, le=1.0)
    customization_applied: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class SuccessPatternRequest(BaseModel):
    """成功パターンリクエスト"""
    clinic_id: Optional[str] = None
    counselor_id: Optional[str] = None
    days: int = Field(default=30, ge=7, le=365)
    min_score: float = Field(default=8.0, ge=0.0, le=10.0)
    pattern_types: Optional[List[str]] = None

class SuccessPatternResponse(BaseModel):
    """成功パターンレスポンス"""
    patterns: List[SuccessPatternData]
    best_practices: List[BestPractice]
    summary_stats: Dict[str, Union[int, float]]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class FeedbackRequest(BaseModel):
    """フィードバックリクエスト"""
    analysis_id: str
    suggestion_id: Optional[str] = None
    feedback_type: str = Field(..., pattern="^(helpful|not_helpful|implemented|needs_clarification)$")
    rating: Optional[int] = Field(None, ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=1000)
    implementation_status: Optional[str] = Field(None, pattern="^(planned|in_progress|completed|abandoned)$")

class FeedbackResponse(BaseModel):
    """フィードバックレスポンス"""
    feedback_id: str
    status: str = "received"
    message: str = "フィードバックを受け付けました"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PerformanceTrendRequest(BaseModel):
    """パフォーマンストレンドリクエスト"""
    counselor_id: str
    days: int = Field(default=30, ge=7, le=365)
    comparison_period: Optional[int] = Field(None, ge=7, le=365)
    include_predictions: bool = Field(default=False)

class PerformanceTrendResponse(BaseModel):
    """パフォーマンストレンドレスポンス"""
    trend_data: PerformanceTrend
    improvement_trajectory: Optional[List[Dict[str, Union[str, float]]]] = None
    recommendations: List[ImprovementRecommendation] = Field(default_factory=list)
    next_review_date: Optional[datetime] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# Summary schemas
class ImprovementSummary(BaseModel):
    """改善サマリー"""
    total_suggestions: int
    high_priority_count: int
    medium_priority_count: int
    low_priority_count: int
    categories_covered: List[SuggestionCategory]
    estimated_impact_score: float = Field(..., ge=0.0, le=10.0)
    implementation_complexity: str = Field(..., pattern="^(low|medium|high)$")

class ScriptOptimizationSummary(BaseModel):
    """スクリプト最適化サマリー"""
    total_scripts_generated: int
    average_success_probability: float = Field(..., ge=0.0, le=1.0)
    most_effective_patterns: List[str]
    customization_features_used: List[str]
    performance_improvements: Dict[str, float] = Field(default_factory=dict)