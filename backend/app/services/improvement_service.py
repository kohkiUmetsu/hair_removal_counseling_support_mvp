"""
Improvement suggestion service for analysis results
"""
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.analysis import AnalysisTask, SuccessPattern
from app.models.session import Session as SessionModel, SessionStatus
from app.models.customer import Customer
from app.schemas.analysis import AnalysisResult, QuestioningAnalysis, AnxietyHandlingAnalysis, ClosingAnalysis, FlowAnalysis
from app.schemas.improvement import (
    Suggestion, SuggestionPriority, SuggestionCategory,
    OptimizedScript, ScriptSection, SuccessPatternData,
    ImprovementRecommendation, PerformanceTrend
)

logger = logging.getLogger(__name__)

class ImprovementSuggestionService:
    """改善提案生成サービス"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def generate_suggestions(self, analysis_result: AnalysisResult) -> List[Suggestion]:
        """分析結果から改善提案を生成"""
        suggestions = []
        
        try:
            # 質問技法の改善提案
            if analysis_result.questioning.score < 7.0:
                suggestions.extend(self._generate_questioning_suggestions(analysis_result.questioning))
            
            # 不安対応の改善提案
            if analysis_result.anxiety_handling.score < 7.0:
                suggestions.extend(self._generate_anxiety_suggestions(analysis_result.anxiety_handling))
            
            # クロージングの改善提案
            if analysis_result.closing.score < 7.0:
                suggestions.extend(self._generate_closing_suggestions(analysis_result.closing))
            
            # フローの改善提案
            if analysis_result.flow.score < 7.0:
                suggestions.extend(self._generate_flow_suggestions(analysis_result.flow))
            
            # 優先度とインパクトでソート
            suggestions.sort(key=lambda x: (
                self._get_priority_weight(x.priority),
                x.expected_impact_score
            ), reverse=True)
            
            # 上位10件に制限
            return suggestions[:10]
            
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            return []
    
    def _generate_questioning_suggestions(self, questioning: QuestioningAnalysis) -> List[Suggestion]:
        """質問技法の改善提案"""
        suggestions = []
        
        # オープンクエスチョン比率が低い場合
        if questioning.open_question_ratio < 0.6:
            suggestions.append(Suggestion(
                id=None,
                category=SuggestionCategory.QUESTIONING,
                priority=SuggestionPriority.HIGH,
                title="オープンクエスチョンの活用を増やす",
                description="顧客の本音を引き出すために、「はい・いいえ」で答えられない質問を増やしましょう。",
                example_script="「どのような点でご不安を感じていらっしゃいますか？」「今までの脱毛経験で気になったことはありますか？」",
                expected_impact="顧客の本音や詳細なニーズを把握でき、より適切な提案ができるようになります。",
                implementation_difficulty="easy",
                expected_impact_score=8.5,
                success_rate=0.85,
                related_best_practices=[
                    "感情に関するオープンクエスチョン",
                    "過去の経験を聞く質問",
                    "理想の状態を聞く質問"
                ]
            ))
        
        # 顧客発話時間が少ない場合
        if questioning.customer_talk_time_ratio < 0.5:
            suggestions.append(Suggestion(
                id=None,
                category=SuggestionCategory.QUESTIONING,
                priority=SuggestionPriority.MEDIUM,
                title="顧客の発話時間を増やす",
                description="顧客により多く話してもらうことで、ニーズや不安を深く理解できます。",
                example_script="「もう少し詳しく教えていただけますか？」「他にも気になることはありませんか？」",
                expected_impact="顧客の真のニーズを把握し、満足度の高い提案ができます。",
                implementation_difficulty="medium",
                expected_impact_score=7.8,
                success_rate=0.75,
                related_best_practices=[
                    "沈黙を恐れない",
                    "相槌で促す",
                    "深掘り質問の技法"
                ]
            ))
        
        # 質問の多様性が低い場合
        if questioning.question_diversity < 5:
            suggestions.append(Suggestion(
                id=None,
                category=SuggestionCategory.QUESTIONING,
                priority=SuggestionPriority.MEDIUM,
                title="質問のバリエーションを増やす",
                description="様々な角度から質問することで、顧客の多面的なニーズを把握できます。",
                example_script="機能的ニーズ、感情的ニーズ、社会的ニーズの3つの観点から質問を組み立てましょう。",
                expected_impact="顧客理解が深まり、より説得力のある提案ができます。",
                implementation_difficulty="medium",
                expected_impact_score=7.2,
                success_rate=0.70,
                related_best_practices=[
                    "5W1Hの活用",
                    "仮定質問の技法",
                    "比較質問の技法"
                ]
            ))
        
        return suggestions
    
    def _generate_anxiety_suggestions(self, anxiety: AnxietyHandlingAnalysis) -> List[Suggestion]:
        """不安対応の改善提案"""
        suggestions = []
        
        # 不安要素の特定が不十分な場合
        if len(anxiety.anxiety_points_identified) < 3:
            suggestions.append(Suggestion(
                id=None,
                category=SuggestionCategory.ANXIETY_HANDLING,
                priority=SuggestionPriority.HIGH,
                title="不安要素をより詳細に特定する",
                description="顧客の潜在的な不安も含めて、より多くの不安要素を特定しましょう。",
                example_script="「痛みについてはいかがですか？」「料金面でのご心配はありませんか？」「アフターケアについてはどうでしょう？」",
                expected_impact="不安の見落としを防ぎ、顧客の安心感を高められます。",
                implementation_difficulty="easy",
                expected_impact_score=8.8,
                success_rate=0.90,
                related_best_practices=[
                    "不安の網羅的チェック",
                    "非言語的サインの観察",
                    "仮説的不安の確認"
                ]
            ))
        
        # 共感表現が少ない場合
        if anxiety.empathy_expressions < 3:
            suggestions.append(Suggestion(
                id=None,
                category=SuggestionCategory.ANXIETY_HANDLING,
                priority=SuggestionPriority.HIGH,
                title="共感表現を増やす",
                description="顧客の不安に対してより多くの共感を示し、信頼関係を築きましょう。",
                example_script="「そのお気持ち、とてもよく分かります」「多くの方が同じような不安をお持ちです」",
                expected_impact="顧客との信頼関係が深まり、不安解消効果が高まります。",
                implementation_difficulty="easy",
                expected_impact_score=8.2,
                success_rate=0.85,
                related_best_practices=[
                    "感情のミラーリング",
                    "共感的な相槌",
                    "体験の共有"
                ]
            ))
        
        # 解決策の具体性が低い場合
        if anxiety.solution_specificity < 0.7:
            suggestions.append(Suggestion(
                id=None,
                category=SuggestionCategory.ANXIETY_HANDLING,
                priority=SuggestionPriority.MEDIUM,
                title="より具体的な解決策を提示する",
                description="抽象的な説明ではなく、具体的で分かりやすい解決策を提示しましょう。",
                example_script="「痛みについては、冷却システムにより○○%軽減されます」「料金は月額○○円からの分割払いも可能です」",
                expected_impact="顧客の理解度と納得度が向上し、不安解消につながります。",
                implementation_difficulty="medium",
                expected_impact_score=7.9,
                success_rate=0.80,
                related_best_practices=[
                    "数値による説明",
                    "実例の活用",
                    "視覚的資料の使用"
                ]
            ))
        
        return suggestions
    
    def _generate_closing_suggestions(self, closing: ClosingAnalysis) -> List[Suggestion]:
        """クロージングの改善提案"""
        suggestions = []
        
        # タイミングが不適切な場合
        if closing.timing_appropriateness < 0.7:
            suggestions.append(Suggestion(
                id=None,
                category=SuggestionCategory.CLOSING,
                priority=SuggestionPriority.HIGH,
                title="クロージングのタイミングを改善する",
                description="顧客の準備状況を見極めて、適切なタイミングでクロージングを行いましょう。",
                example_script="「ご質問やご不安は全て解消されましたでしょうか？」で確認してからクロージングへ移行",
                expected_impact="顧客の心理的準備が整った状態でクロージングでき、成約率が向上します。",
                implementation_difficulty="medium",
                expected_impact_score=9.2,
                success_rate=0.82,
                related_best_practices=[
                    "買いシグナルの察知",
                    "準備確認の質問",
                    "段階的なクロージング"
                ]
            ))
        
        # 緊急性の演出が不足している場合
        if closing.urgency_creation < 0.6:
            suggestions.append(Suggestion(
                id=None,
                category=SuggestionCategory.CLOSING,
                priority=SuggestionPriority.MEDIUM,
                title="適切な緊急性を演出する",
                description="過度ではない範囲で、決断を促す緊急性を演出しましょう。",
                example_script="「この特別プランは今月末まで」「予約枠に限りがございます」",
                expected_impact="顧客の決断を促し、機会損失を防げます。",
                implementation_difficulty="easy",
                expected_impact_score=7.5,
                success_rate=0.75,
                related_best_practices=[
                    "期間限定の活用",
                    "希少性の演出",
                    "タイムリミットの設定"
                ]
            ))
        
        # 限定性の活用が不足している場合
        if closing.limitation_usage < 0.6:
            suggestions.append(Suggestion(
                id=None,
                category=SuggestionCategory.CLOSING,
                priority=SuggestionPriority.MEDIUM,
                title="限定性を効果的に活用する",
                description="特別感を演出し、顧客の所有欲を刺激しましょう。",
                example_script="「このプランは月○名様限定です」「初回特典は今回のみ」",
                expected_impact="顧客の特別感を高め、決断を促進できます。",
                implementation_difficulty="easy",
                expected_impact_score=7.8,
                success_rate=0.78,
                related_best_practices=[
                    "数量限定の活用",
                    "会員限定特典",
                    "初回限定オファー"
                ]
            ))
        
        return suggestions
    
    def _generate_flow_suggestions(self, flow: FlowAnalysis) -> List[Suggestion]:
        """フローの改善提案"""
        suggestions = []
        
        # 論理構造が不明確な場合
        if flow.logical_structure < 0.7:
            suggestions.append(Suggestion(
                id=None,
                category=SuggestionCategory.FLOW,
                priority=SuggestionPriority.MEDIUM,
                title="より論理的な構成にする",
                description="セッションの流れを整理し、論理的で分かりやすい構成にしましょう。",
                example_script="「まずお悩みをお聞きし、次に解決策をご提案、最後にプランをご案内します」",
                expected_impact="顧客の理解度が向上し、満足度の高いセッションになります。",
                implementation_difficulty="medium",
                expected_impact_score=7.6,
                success_rate=0.72,
                related_best_practices=[
                    "構成の事前説明",
                    "段階的な進行",
                    "要点の整理"
                ]
            ))
        
        # 話題転換がスムーズでない場合
        if flow.smooth_transitions < 0.7:
            suggestions.append(Suggestion(
                id=None,
                category=SuggestionCategory.FLOW,
                priority=SuggestionPriority.LOW,
                title="話題転換をスムーズにする",
                description="自然で違和感のない話題転換を心がけましょう。",
                example_script="「ニーズについて理解できました。では、それを解決する方法についてお話ししますね」",
                expected_impact="セッションの流れが自然になり、顧客の集中を維持できます。",
                implementation_difficulty="medium",
                expected_impact_score=6.8,
                success_rate=0.68,
                related_best_practices=[
                    "ブリッジフレーズの活用",
                    "要約からの転換",
                    "質問による転換"
                ]
            ))
        
        return suggestions
    
    def _get_priority_weight(self, priority: SuggestionPriority) -> int:
        """優先度の重み付け"""
        weights = {
            SuggestionPriority.HIGH: 3,
            SuggestionPriority.MEDIUM: 2,
            SuggestionPriority.LOW: 1
        }
        return weights.get(priority, 1)
    
    def get_success_patterns(
        self, 
        clinic_id: Optional[str] = None,
        counselor_id: Optional[str] = None,
        days: int = 30
    ) -> List[SuccessPatternData]:
        """成功パターンの取得"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = self.db.query(AnalysisTask).filter(
                AnalysisTask.status == "completed",
                AnalysisTask.overall_score >= 8.0,
                AnalysisTask.created_at >= cutoff_date,
                AnalysisTask.is_deleted == False
            )
            
            if clinic_id:
                query = query.join(SessionModel).join(Customer).filter(
                    Customer.clinic_id == clinic_id
                )
            
            high_score_analyses = query.all()
            
            # パターン分析
            patterns = self._analyze_success_patterns(high_score_analyses)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to get success patterns: {e}")
            return []
    
    def _analyze_success_patterns(self, analyses: List[AnalysisTask]) -> List[SuccessPatternData]:
        """成功パターンの分析"""
        patterns = []
        
        if not analyses:
            return patterns
        
        # 高スコア項目の分析
        high_questioning_count = len([a for a in analyses if a.full_analysis_result and 
                                     a.full_analysis_result.get('questioning', {}).get('score', 0) >= 8.0])
        
        high_anxiety_count = len([a for a in analyses if a.full_analysis_result and 
                                a.full_analysis_result.get('anxiety_handling', {}).get('score', 0) >= 8.0])
        
        high_closing_count = len([a for a in analyses if a.full_analysis_result and 
                                a.full_analysis_result.get('closing', {}).get('score', 0) >= 8.0])
        
        total_count = len(analyses)
        
        if high_questioning_count / total_count >= 0.7:
            patterns.append(SuccessPatternData(
                pattern_type="questioning",
                pattern_name="効果的な質問技法",
                description="オープンクエスチョンと深掘り質問を効果的に組み合わせている",
                success_rate=high_questioning_count / total_count,
                usage_frequency=high_questioning_count,
                effectiveness_score=8.5
            ))
        
        if high_anxiety_count / total_count >= 0.7:
            patterns.append(SuccessPatternData(
                pattern_type="anxiety_handling",
                pattern_name="共感的な不安対応",
                description="顧客の不安に対して十分な共感を示し、具体的な解決策を提示している",
                success_rate=high_anxiety_count / total_count,
                usage_frequency=high_anxiety_count,
                effectiveness_score=8.3
            ))
        
        if high_closing_count / total_count >= 0.7:
            patterns.append(SuccessPatternData(
                pattern_type="closing",
                pattern_name="適切なタイミングでのクロージング",
                description="顧客の準備状況を見極めて、適切なタイミングでクロージングを実行している",
                success_rate=high_closing_count / total_count,
                usage_frequency=high_closing_count,
                effectiveness_score=8.7
            ))
        
        return patterns
    
    def generate_performance_trend(
        self, 
        counselor_id: str,
        days: int = 30
    ) -> PerformanceTrend:
        """パフォーマンストレンドの生成"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # セッション履歴の取得
            sessions = self.db.query(SessionModel).filter(
                SessionModel.counselor_id == counselor_id,
                SessionModel.session_date >= cutoff_date,
                SessionModel.is_deleted == False
            ).order_by(SessionModel.session_date).all()
            
            if not sessions:
                return PerformanceTrend(
                    trend_direction="stable",
                    improvement_rate=0.0,
                    current_average=0.0,
                    previous_average=0.0,
                    key_improvements=[],
                    areas_needing_attention=[]
                )
            
            # 前半と後半での比較
            mid_point = len(sessions) // 2
            early_sessions = sessions[:mid_point] if mid_point > 0 else []
            recent_sessions = sessions[mid_point:] if mid_point < len(sessions) else sessions
            
            early_avg = self._calculate_average_score(early_sessions)
            recent_avg = self._calculate_average_score(recent_sessions)
            
            improvement_rate = ((recent_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
            
            if improvement_rate > 5:
                trend_direction = "improving"
            elif improvement_rate < -5:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
            
            return PerformanceTrend(
                trend_direction=trend_direction,
                improvement_rate=improvement_rate,
                current_average=recent_avg,
                previous_average=early_avg,
                key_improvements=self._identify_improvements(early_sessions, recent_sessions),
                areas_needing_attention=self._identify_attention_areas(recent_sessions)
            )
            
        except Exception as e:
            logger.error(f"Failed to generate performance trend: {e}")
            return PerformanceTrend(
                trend_direction="unknown",
                improvement_rate=0.0,
                current_average=0.0,
                previous_average=0.0,
                key_improvements=[],
                areas_needing_attention=[]
            )
    
    def _calculate_average_score(self, sessions: List[SessionModel]) -> float:
        """平均スコアの計算"""
        if not sessions:
            return 0.0
        
        scores = [s.overall_score for s in sessions if s.overall_score is not None]
        return sum(scores) / len(scores) if scores else 0.0
    
    def _identify_improvements(self, early_sessions: List[SessionModel], recent_sessions: List[SessionModel]) -> List[str]:
        """改善点の特定"""
        improvements = []
        
        # 各カテゴリでの改善を確認
        categories = ['questioning', 'anxiety_handling', 'closing', 'flow']
        
        for category in categories:
            early_avg = self._calculate_category_average(early_sessions, category)
            recent_avg = self._calculate_category_average(recent_sessions, category)
            
            if recent_avg > early_avg + 0.5:  # 0.5ポイント以上の改善
                improvements.append(f"{category}スキルが向上")
        
        return improvements
    
    def _identify_attention_areas(self, sessions: List[SessionModel]) -> List[str]:
        """注意が必要な領域の特定"""
        attention_areas = []
        
        categories = ['questioning', 'anxiety_handling', 'closing', 'flow']
        
        for category in categories:
            avg_score = self._calculate_category_average(sessions, category)
            if avg_score < 6.0:  # 6.0未満は要注意
                attention_areas.append(f"{category}スキルの改善が必要")
        
        return attention_areas
    
    def _calculate_category_average(self, sessions: List[SessionModel], category: str) -> float:
        """カテゴリ別平均スコアの計算"""
        scores = []
        for session in sessions:
            if session.analysis_result and isinstance(session.analysis_result, dict):
                category_data = session.analysis_result.get(category, {})
                if isinstance(category_data, dict):
                    score = category_data.get('score')
                    if score is not None:
                        scores.append(float(score))
        
        return sum(scores) / len(scores) if scores else 0.0