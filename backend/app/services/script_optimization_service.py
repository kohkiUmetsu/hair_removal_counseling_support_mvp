"""
Script optimization service for generating optimized counseling scripts
"""
from typing import List, Dict, Optional, Union
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.session import Session as SessionModel
from app.models.customer import Customer
from app.models.analysis import AnalysisTask
from app.schemas.improvement import (
    OptimizedScript, ScriptSection, SuccessPatternData,
    ScriptGenerationRequest, ImplementationDifficulty
)

logger = logging.getLogger(__name__)

class ScriptOptimizationService:
    """スクリプト最適化サービス"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def generate_optimized_script(
        self,
        request: ScriptGenerationRequest,
        success_patterns: List[SuccessPatternData] = None
    ) -> OptimizedScript:
        """最適化スクリプトの生成"""
        try:
            # 顧客分析
            customer_insights = self._analyze_customer_characteristics(request)
            
            # 成功パターンの取得
            if success_patterns is None:
                success_patterns = self._get_relevant_success_patterns(request)
            
            # スクリプトセクションの生成
            script_sections = self._generate_script_sections(
                customer_insights, 
                success_patterns, 
                request
            )
            
            # 成功確率の計算
            success_probability = self._calculate_success_probability(
                customer_insights, 
                success_patterns,
                request
            )
            
            return OptimizedScript(
                customer_type=customer_insights.get("customer_type", "standard"),
                opening=script_sections["opening"],
                needs_assessment=script_sections["needs_assessment"],
                presentation=script_sections["presentation"],
                objection_handling=script_sections["objection_handling"],
                closing=script_sections["closing"],
                success_probability=success_probability,
                customization_notes=self._generate_customization_notes(customer_insights, request),
                total_estimated_duration=self._calculate_total_duration(script_sections)
            )
            
        except Exception as e:
            logger.error(f"Failed to generate optimized script: {e}")
            # フォールバック用の基本スクリプト
            return self._generate_fallback_script(request)
    
    def _analyze_customer_characteristics(self, request: ScriptGenerationRequest) -> Dict[str, Union[str, float]]:
        """顧客特性の分析"""
        characteristics = {
            "customer_type": "standard",
            "anxiety_level": 0.5,
            "decision_making_style": "analytical",
            "communication_preference": "detailed",
            "price_sensitivity": 0.5
        }
        
        # 顧客プロファイルが提供されている場合
        if request.customer_profile:
            characteristics.update(request.customer_profile)
        
        # 顧客IDが提供されている場合、過去のセッションデータを分析
        if request.customer_id:
            customer_data = self._get_customer_history(request.customer_id)
            characteristics.update(customer_data)
        
        return characteristics
    
    def _get_customer_history(self, customer_id: str) -> Dict[str, Union[str, float]]:
        """顧客履歴の分析"""
        try:
            # 過去のセッションを取得
            sessions = self.db.query(SessionModel).filter(
                SessionModel.customer_id == customer_id,
                SessionModel.is_deleted == False
            ).order_by(SessionModel.session_date.desc()).limit(5).all()
            
            if not sessions:
                return {}
            
            # 分析結果から特性を抽出
            analysis_data = []
            for session in sessions:
                if session.analysis_result:
                    analysis_data.append(session.analysis_result)
            
            if not analysis_data:
                return {}
            
            # 傾向分析
            anxiety_scores = []
            questioning_scores = []
            
            for data in analysis_data:
                if isinstance(data, dict):
                    anxiety_data = data.get('anxiety_handling', {})
                    if isinstance(anxiety_data, dict):
                        anxiety_scores.append(anxiety_data.get('score', 5.0))
                    
                    questioning_data = data.get('questioning', {})
                    if isinstance(questioning_data, dict):
                        questioning_scores.append(questioning_data.get('score', 5.0))
            
            characteristics = {}
            
            # 不安レベルの推定
            if anxiety_scores:
                avg_anxiety_score = sum(anxiety_scores) / len(anxiety_scores)
                characteristics["anxiety_level"] = max(0.0, min(1.0, (10 - avg_anxiety_score) / 10))
            
            # コミュニケーション特性の推定
            if questioning_scores:
                avg_questioning_score = sum(questioning_scores) / len(questioning_scores)
                if avg_questioning_score > 7.0:
                    characteristics["communication_preference"] = "detailed"
                else:
                    characteristics["communication_preference"] = "simple"
            
            return characteristics
            
        except Exception as e:
            logger.error(f"Failed to analyze customer history: {e}")
            return {}
    
    def _get_relevant_success_patterns(self, request: ScriptGenerationRequest) -> List[SuccessPatternData]:
        """関連する成功パターンの取得"""
        try:
            # 過去30日間の高スコア分析から成功パターンを抽出
            high_score_analyses = self.db.query(AnalysisTask).filter(
                AnalysisTask.overall_score >= 8.0,
                AnalysisTask.status == "completed",
                AnalysisTask.created_at >= datetime.utcnow() - timedelta(days=30),
                AnalysisTask.is_deleted == False
            ).limit(20).all()
            
            patterns = []
            
            # フォーカスエリアに基づいて関連パターンを抽出
            for focus_area in request.focus_areas:
                pattern_data = self._extract_pattern_for_area(high_score_analyses, focus_area)
                if pattern_data:
                    patterns.append(pattern_data)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to get success patterns: {e}")
            return []
    
    def _extract_pattern_for_area(self, analyses: List[AnalysisTask], area: str) -> Optional[SuccessPatternData]:
        """特定エリアの成功パターン抽出"""
        if not analyses:
            return None
        
        high_score_count = 0
        total_count = len(analyses)
        
        for analysis in analyses:
            if analysis.full_analysis_result and isinstance(analysis.full_analysis_result, dict):
                area_data = analysis.full_analysis_result.get(area, {})
                if isinstance(area_data, dict) and area_data.get('score', 0) >= 8.0:
                    high_score_count += 1
        
        if high_score_count / total_count >= 0.6:  # 60%以上で成功パターンとみなす
            return SuccessPatternData(
                pattern_type=area,
                pattern_name=f"効果的な{area}パターン",
                description=f"{area}において高い成果を上げているアプローチ",
                success_rate=high_score_count / total_count,
                usage_frequency=high_score_count,
                effectiveness_score=8.0 + (high_score_count / total_count) * 2
            )
        
        return None
    
    def _generate_script_sections(
        self,
        customer_insights: Dict[str, Union[str, float]],
        success_patterns: List[SuccessPatternData],
        request: ScriptGenerationRequest
    ) -> Dict[str, Union[ScriptSection, Dict[str, ScriptSection]]]:
        """スクリプトセクションの生成"""
        
        # オープニングセクション
        opening = self._generate_opening_script(customer_insights, success_patterns)
        
        # ニーズアセスメントセクション
        needs_assessment = self._generate_needs_assessment_script(customer_insights, success_patterns)
        
        # プレゼンテーションセクション
        presentation = self._generate_presentation_script(customer_insights, success_patterns)
        
        # 異議処理セクション
        objection_handling = self._generate_objection_handling_scripts(customer_insights, success_patterns)
        
        # クロージングセクション
        closing = self._generate_closing_script(customer_insights, success_patterns)
        
        return {
            "opening": opening,
            "needs_assessment": needs_assessment,
            "presentation": presentation,
            "objection_handling": objection_handling,
            "closing": closing
        }
    
    def _generate_opening_script(
        self,
        customer_insights: Dict[str, Union[str, float]],
        success_patterns: List[SuccessPatternData]
    ) -> ScriptSection:
        """オープニングスクリプトの生成"""
        
        anxiety_level = customer_insights.get("anxiety_level", 0.5)
        
        if anxiety_level > 0.7:
            # 高不安顧客向け
            content = """本日はお忙しい中、お時間をいただきありがとうございます。
まずは、リラックスしてお話しください。
私たちは多くのお客様の脱毛のお悩みを解決してきており、どのようなご不安でもお気軽にお聞かせください。
今日は無理にお決めいただく必要はございませんので、安心してご相談ください。"""
            
            key_points = [
                "安心感の提供",
                "プレッシャーを与えない",
                "経験と実績のアピール"
            ]
            
        else:
            # 標準的な顧客向け
            content = """本日はありがとうございます。
脱毛についてのご相談ということですが、まずはお客様のご希望やお悩みについて詳しくお聞かせください。
お客様に最適なプランをご提案させていただきたいと思います。"""
            
            key_points = [
                "感謝の表現",
                "ニーズ把握の重要性",
                "カスタマイズ提案の予告"
            ]
        
        return ScriptSection(
            content=content,
            key_points=key_points,
            alternative_phrases=[
                "お忙しい中お越しいただき",
                "貴重なお時間をいただき",
                "足をお運びいただき"
            ],
            timing_notes="最初の1-2分で信頼関係構築",
            body_language_tips=[
                "笑顔での挨拶",
                "適度なアイコンタクト",
                "リラックスした姿勢"
            ],
            estimated_duration_minutes=2.0
        )
    
    def _generate_needs_assessment_script(
        self,
        customer_insights: Dict[str, Union[str, float]],
        success_patterns: List[SuccessPatternData]
    ) -> ScriptSection:
        """ニーズアセスメントスクリプトの生成"""
        
        communication_preference = customer_insights.get("communication_preference", "detailed")
        
        if communication_preference == "detailed":
            content = """まず、現在の脱毛に関するお悩みについて詳しくお聞かせください。
・どちらの部位を中心にお考えでしょうか？
・今までに脱毛のご経験はございますか？
・どのような仕上がりをイメージされていますか？
・脱毛について不安に思われていることはありますか？
・ご希望のスケジュールなどはございますか？"""
        else:
            content = """脱毛についてのご希望をお聞かせください。
・気になる部位はどちらですか？
・脱毛は初めてですか？
・どんな仕上がりをお望みですか？
・ご不安な点はありますか？"""
        
        return ScriptSection(
            content=content,
            key_points=[
                "オープンクエスチョンの活用",
                "段階的な深掘り",
                "不安要素の早期発見"
            ],
            alternative_phrases=[
                "お聞かせください",
                "教えていただけますか",
                "いかがでしょうか"
            ],
            timing_notes="5-8分程度でじっくりとヒアリング",
            body_language_tips=[
                "メモを取る姿勢",
                "うなずきながら聞く",
                "相手のペースに合わせる"
            ],
            estimated_duration_minutes=7.0
        )
    
    def _generate_presentation_script(
        self,
        customer_insights: Dict[str, Union[str, float]],
        success_patterns: List[SuccessPatternData]
    ) -> ScriptSection:
        """プレゼンテーションスクリプトの生成"""
        
        content = """お聞かせいただいた内容を踏まえ、最適なプランをご提案いたします。

【技術とサービスの特徴】
・最新の脱毛機器による痛みを抑えた施術
・お客様の肌質に合わせたカスタマイズ対応
・経験豊富なスタッフによる安心のサポート

【お客様にお勧めするプラン】
具体的なプラン内容とメリットをご説明いたします。
特にお客様がご心配されていた○○については、このような対応をいたします。"""
        
        return ScriptSection(
            content=content,
            key_points=[
                "顧客ニーズとの関連付け",
                "具体的なメリット説明",
                "不安要素への対応"
            ],
            alternative_phrases=[
                "ご提案いたします",
                "お勧めいたします",
                "ご案内いたします"
            ],
            timing_notes="8-12分程度で詳細説明",
            body_language_tips=[
                "資料を活用した説明",
                "視覚的な資料の使用",
                "確認を取りながら進行"
            ],
            estimated_duration_minutes=10.0
        )
    
    def _generate_objection_handling_scripts(
        self,
        customer_insights: Dict[str, Union[str, float]],
        success_patterns: List[SuccessPatternData]
    ) -> Dict[str, ScriptSection]:
        """異議処理スクリプトの生成"""
        
        price_sensitivity = customer_insights.get("price_sensitivity", 0.5)
        
        objection_scripts = {}
        
        # 料金に関する異議
        if price_sensitivity > 0.6:
            objection_scripts["price"] = ScriptSection(
                content="""料金についてのご心配、とてもよく分かります。
多くのお客様が同じようにお考えになります。

ただ、考えていただきたいのは：
・長期的なコストパフォーマンス
・自己処理の時間と手間の削減
・肌への負担軽減

また、分割払いのオプションもございますので、月々のご負担を抑えることも可能です。""",
                key_points=[
                    "共感の表現",
                    "長期的価値の説明",
                    "支払い方法の提案"
                ],
                timing_notes="料金説明後の反応を見て使用",
                estimated_duration_minutes=3.0
            )
        
        # 痛みに関する異議
        objection_scripts["pain"] = ScriptSection(
            content="""痛みについてのご不安、よく理解できます。
従来の脱毛に比べて、当クリニックの機器は痛みを大幅に軽減しています。

・冷却システムによる痛み軽減
・痛みレベルの調整が可能
・テスト照射で事前確認

まずは実際に体験していただくのが一番です。""",
            key_points=[
                "技術的優位性の説明",
                "個別対応の説明",
                "体験提案"
            ],
            timing_notes="痛みについて質問された時",
            estimated_duration_minutes=2.5
        )
        
        return objection_scripts
    
    def _generate_closing_script(
        self,
        customer_insights: Dict[str, Union[str, float]],
        success_patterns: List[SuccessPatternData]
    ) -> ScriptSection:
        """クロージングスクリプトの生成"""
        
        decision_making_style = customer_insights.get("decision_making_style", "analytical")
        
        if decision_making_style == "analytical":
            content = """ここまでご説明させていただいた内容について、ご質問やご不明な点はございませんでしょうか？

すべてご理解いただけましたら、次のステップについてご案内いたします。
・今月中のお申込みで特別価格の適用
・予約枠に限りがあること
・無料カウンセリングの追加サポート

お客様にとって最適なタイミングでご決断いただければと思いますが、いかがでしょうか？"""
        else:
            content = """いかがでしょうか？お客様のご希望に合うプランをご提案できたでしょうか？

今日お決めいただけるようでしたら、特別なご条件でご案内することが可能です。
この機会にぜひご検討ください。"""
        
        return ScriptSection(
            content=content,
            key_points=[
                "最終確認の質問",
                "決断促進の要素",
                "特典の提示"
            ],
            alternative_phrases=[
                "いかがでしょうか",
                "ご検討ください",
                "ご決断ください"
            ],
            timing_notes="全体説明完了後の自然な流れで",
            body_language_tips=[
                "自信を持った態度",
                "適度な間を取る",
                "相手の反応を観察"
            ],
            estimated_duration_minutes=5.0
        )
    
    def _calculate_success_probability(
        self,
        customer_insights: Dict[str, Union[str, float]],
        success_patterns: List[SuccessPatternData],
        request: ScriptGenerationRequest
    ) -> float:
        """成功確率の計算"""
        base_probability = 0.6  # ベース確率
        
        # 顧客特性による調整
        anxiety_level = customer_insights.get("anxiety_level", 0.5)
        base_probability -= anxiety_level * 0.2  # 不安レベルが高いほど確率低下
        
        # 成功パターンによる調整
        if success_patterns:
            pattern_boost = min(0.3, len(success_patterns) * 0.1)
            base_probability += pattern_boost
        
        # 前回分析結果による調整
        if request.previous_analysis_ids:
            # 過去の分析結果が良好なら確率上昇
            base_probability += min(0.2, len(request.previous_analysis_ids) * 0.05)
        
        return max(0.0, min(1.0, base_probability))
    
    def _generate_customization_notes(
        self,
        customer_insights: Dict[str, Union[str, float]],
        request: ScriptGenerationRequest
    ) -> List[str]:
        """カスタマイズノートの生成"""
        notes = []
        
        anxiety_level = customer_insights.get("anxiety_level", 0.5)
        if anxiety_level > 0.7:
            notes.append("高不安顧客：より多くの安心材料と時間を提供")
        
        communication_preference = customer_insights.get("communication_preference", "detailed")
        if communication_preference == "simple":
            notes.append("簡潔な説明を好む：要点を絞った説明を心がける")
        
        price_sensitivity = customer_insights.get("price_sensitivity", 0.5)
        if price_sensitivity > 0.6:
            notes.append("価格感度高：コストパフォーマンスと支払い方法を強調")
        
        if request.focus_areas:
            notes.append(f"重点分野：{', '.join(request.focus_areas)}")
        
        return notes
    
    def _calculate_total_duration(self, script_sections: Dict) -> float:
        """総所要時間の計算"""
        total_duration = 0.0
        
        for section_name, section in script_sections.items():
            if isinstance(section, ScriptSection):
                total_duration += section.estimated_duration_minutes or 0.0
            elif isinstance(section, dict):
                for sub_section in section.values():
                    if isinstance(sub_section, ScriptSection):
                        total_duration += sub_section.estimated_duration_minutes or 0.0
        
        return total_duration
    
    def _generate_fallback_script(self, request: ScriptGenerationRequest) -> OptimizedScript:
        """フォールバック用基本スクリプト"""
        basic_opening = ScriptSection(
            content="本日はありがとうございます。脱毛についてのご相談をお聞かせください。",
            key_points=["基本的な挨拶", "ニーズ確認"],
            estimated_duration_minutes=2.0
        )
        
        basic_needs = ScriptSection(
            content="どちらの部位を中心にお考えでしょうか？ご不安な点はありますか？",
            key_points=["基本的なヒアリング"],
            estimated_duration_minutes=5.0
        )
        
        basic_presentation = ScriptSection(
            content="お客様のニーズに合わせたプランをご提案いたします。",
            key_points=["基本的な提案"],
            estimated_duration_minutes=8.0
        )
        
        basic_closing = ScriptSection(
            content="ご検討いただけますでしょうか？",
            key_points=["基本的なクロージング"],
            estimated_duration_minutes=3.0
        )
        
        return OptimizedScript(
            customer_type="standard",
            opening=basic_opening,
            needs_assessment=basic_needs,
            presentation=basic_presentation,
            objection_handling={},
            closing=basic_closing,
            success_probability=0.5,
            customization_notes=["基本スクリプト（フォールバック）"],
            total_estimated_duration=18.0
        )