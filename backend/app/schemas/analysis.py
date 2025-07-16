"""
AI Analysis schemas
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import uuid

class AnalysisType(str, Enum):
    """分析タイプ"""
    FULL = "full"
    QUICK = "quick"
    SPECIFIC = "specific"

class AnalysisStatus(str, Enum):
    """分析ステータス"""
    PENDING = "pending"
    PREPROCESSING = "preprocessing"
    ANALYZING = "analyzing"
    GENERATING_SUGGESTIONS = "generating_suggestions"
    COMPLETED = "completed"
    FAILED = "failed"

class QuestioningAnalysis(BaseModel):
    """質問技法分析結果"""
    score: float = Field(..., ge=1.0, le=10.0, description="質問技法スコア（1-10）")
    open_question_ratio: float = Field(..., ge=0.0, le=1.0, description="オープンクエスチョン比率")
    customer_talk_time_ratio: float = Field(..., ge=0.0, le=1.0, description="顧客発言時間比率")
    question_diversity: int = Field(..., ge=0, description="質問の多様性")
    effective_questions: List[str] = Field(default_factory=list, description="効果的な質問例")
    improvements: List[str] = Field(default_factory=list, description="改善点")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "score": 7.5,
                "open_question_ratio": 0.6,
                "customer_talk_time_ratio": 0.7,
                "question_diversity": 8,
                "effective_questions": ["どのような点がご不安ですか？", "他にご質問はございますか？"],
                "improvements": ["より具体的な質問を増やす", "顧客の感情に寄り添う質問を追加"]
            }
        }

class AnxietyHandlingAnalysis(BaseModel):
    """不安対応分析結果"""
    score: float = Field(..., ge=1.0, le=10.0, description="不安対応スコア（1-10）")
    anxiety_points_identified: List[str] = Field(default_factory=list, description="特定された不安要素")
    empathy_expressions: int = Field(..., ge=0, description="共感表現回数")
    solution_specificity: float = Field(..., ge=0.0, le=1.0, description="解決策の具体性")
    anxiety_resolution_confirmed: bool = Field(..., description="不安解消の確認")
    improvements: List[str] = Field(default_factory=list, description="改善点")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "score": 8.2,
                "anxiety_points_identified": ["痛みへの不安", "料金への心配"],
                "empathy_expressions": 5,
                "solution_specificity": 0.8,
                "anxiety_resolution_confirmed": True,
                "improvements": ["具体的な事例を使った説明を増やす"]
            }
        }

class ClosingAnalysis(BaseModel):
    """クロージング分析結果"""
    score: float = Field(..., ge=1.0, le=10.0, description="クロージングスコア（1-10）")
    timing_appropriateness: float = Field(..., ge=0.0, le=1.0, description="タイミングの適切さ")
    urgency_creation: float = Field(..., ge=0.0, le=1.0, description="緊急性の演出")
    limitation_usage: float = Field(..., ge=0.0, le=1.0, description="限定性の活用")
    price_presentation_method: str = Field(..., description="価格提示方法")
    objection_handling: List[str] = Field(default_factory=list, description="異議処理例")
    contract_probability: float = Field(..., ge=0.0, le=1.0, description="契約確度")
    improvements: List[str] = Field(default_factory=list, description="改善点")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "score": 6.8,
                "timing_appropriateness": 0.7,
                "urgency_creation": 0.5,
                "limitation_usage": 0.6,
                "price_presentation_method": "段階的価格提示",
                "objection_handling": ["料金に関する懸念への対応"],
                "contract_probability": 0.75,
                "improvements": ["限定性をより効果的に活用", "価格提示のタイミング調整"]
            }
        }

class FlowAnalysis(BaseModel):
    """トーク流れ分析結果"""
    score: float = Field(..., ge=1.0, le=10.0, description="流れスコア（1-10）")
    logical_structure: float = Field(..., ge=0.0, le=1.0, description="論理的構成")
    smooth_transitions: float = Field(..., ge=0.0, le=1.0, description="話題転換のスムーズさ")
    customer_pace_consideration: float = Field(..., ge=0.0, le=1.0, description="顧客ペースへの配慮")
    key_point_emphasis: float = Field(..., ge=0.0, le=1.0, description="重要ポイントの強調")
    session_satisfaction_prediction: float = Field(..., ge=0.0, le=1.0, description="セッション満足度予測")
    improvements: List[str] = Field(default_factory=list, description="改善点")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "score": 7.9,
                "logical_structure": 0.8,
                "smooth_transitions": 0.7,
                "customer_pace_consideration": 0.9,
                "key_point_emphasis": 0.6,
                "session_satisfaction_prediction": 0.85,
                "improvements": ["重要ポイントの強調を改善"]
            }
        }

class AnalysisResult(BaseModel):
    """包括的分析結果"""
    overall_score: float = Field(..., ge=1.0, le=10.0, description="総合スコア")
    questioning: QuestioningAnalysis = Field(..., description="質問技法分析")
    anxiety_handling: AnxietyHandlingAnalysis = Field(..., description="不安対応分析")
    closing: ClosingAnalysis = Field(..., description="クロージング分析")
    flow: FlowAnalysis = Field(..., description="流れ分析")
    session_summary: str = Field(..., description="セッション要約")
    key_strengths: List[str] = Field(default_factory=list, description="主な強み")
    critical_improvements: List[str] = Field(default_factory=list, description="重要な改善点")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="分析日時")

    class Config:
        from_attributes = True

class Suggestion(BaseModel):
    """改善提案"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="提案ID")
    category: str = Field(..., description="カテゴリ")
    priority: str = Field(..., description="優先度")
    title: str = Field(..., description="タイトル")
    description: str = Field(..., description="詳細説明")
    example_script: Optional[str] = Field(None, description="例文・スクリプト")
    expected_impact: str = Field(..., description="期待される効果")
    implementation_difficulty: str = Field(..., description="実装難易度")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="成功率")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "category": "questioning",
                "priority": "high",
                "title": "オープンクエスチョンの活用",
                "description": "より多くのオープンクエスチョンを使用して顧客の本音を引き出しましょう",
                "example_script": "「どのような点でご不安をお感じですか？」",
                "expected_impact": "顧客の真のニーズを把握し、適切な提案が可能になります",
                "implementation_difficulty": "easy",
                "success_rate": 0.85
            }
        }

class AnalysisRequest(BaseModel):
    """分析開始リクエスト"""
    transcription_id: str = Field(..., description="文字起こしID")
    analysis_type: AnalysisType = Field(default=AnalysisType.FULL, description="分析タイプ")
    focus_areas: Optional[List[str]] = Field(None, description="重点分析項目")
    custom_prompts: Optional[Dict[str, str]] = Field(None, description="カスタムプロンプト")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "transcription_id": "123e4567-e89b-12d3-a456-426614174000",
                "analysis_type": "full",
                "focus_areas": ["questioning", "closing"],
                "custom_prompts": {"questioning": "カスタム質問分析プロンプト"}
            }
        }

class AnalysisResponse(BaseModel):
    """分析開始レスポンス"""
    analysis_id: str = Field(..., description="分析ID")
    task_id: str = Field(..., description="タスクID")
    status: AnalysisStatus = Field(..., description="ステータス")
    estimated_duration: int = Field(..., description="推定処理時間（秒）")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="作成日時")

    class Config:
        from_attributes = True

class AnalysisStatusResponse(BaseModel):
    """分析状況レスポンス"""
    analysis_id: str = Field(..., description="分析ID")
    task_id: str = Field(..., description="タスクID")
    status: AnalysisStatus = Field(..., description="ステータス")
    progress: int = Field(..., ge=0, le=100, description="進行状況（%）")
    stage: str = Field(..., description="現在の処理段階")
    result: Optional[AnalysisResult] = Field(None, description="分析結果（完了時）")
    error: Optional[str] = Field(None, description="エラーメッセージ")
    started_at: datetime = Field(..., description="開始日時")
    completed_at: Optional[datetime] = Field(None, description="完了日時")
    estimated_completion: Optional[datetime] = Field(None, description="完了予定日時")

    class Config:
        from_attributes = True

class BatchAnalysisRequest(BaseModel):
    """バッチ分析リクエスト"""
    transcription_ids: List[str] = Field(..., description="文字起こしIDリスト")
    analysis_type: AnalysisType = Field(default=AnalysisType.FULL, description="分析タイプ")
    priority: str = Field(default="normal", description="優先度")

    class Config:
        from_attributes = True

class BatchAnalysisResponse(BaseModel):
    """バッチ分析レスポンス"""
    batch_id: str = Field(..., description="バッチID")
    task_ids: List[str] = Field(..., description="タスクIDリスト")
    total_count: int = Field(..., description="総件数")
    estimated_total_duration: int = Field(..., description="推定総処理時間（秒）")

    class Config:
        from_attributes = True

class AnalysisList(BaseModel):
    """分析一覧"""
    analyses: List[AnalysisStatusResponse] = Field(..., description="分析一覧")
    total: int = Field(..., description="総数")
    page: int = Field(..., description="ページ番号")
    per_page: int = Field(..., description="ページサイズ")

    class Config:
        from_attributes = True

class AnalysisStats(BaseModel):
    """分析統計"""
    total_analyses: int = Field(..., description="総分析数")
    completed_analyses: int = Field(..., description="完了分析数")
    failed_analyses: int = Field(..., description="失敗分析数")
    pending_analyses: int = Field(..., description="待機中分析数")
    processing_analyses: int = Field(..., description="処理中分析数")
    average_processing_time: float = Field(..., description="平均処理時間（秒）")
    average_overall_score: float = Field(..., description="平均総合スコア")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="成功率")

    class Config:
        from_attributes = True