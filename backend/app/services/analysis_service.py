"""
AI Analysis service using OpenAI GPT-4
"""
import openai
from typing import Dict, List, Optional, Tuple
import json
import asyncio
import logging
import re
from datetime import datetime

from app.core.config import settings
from app.services.prompt_service import PromptService
from app.schemas.analysis import (
    AnalysisResult, AnalysisType, QuestioningAnalysis, 
    AnxietyHandlingAnalysis, ClosingAnalysis, FlowAnalysis
)

logger = logging.getLogger(__name__)

class AnalysisService:
    """AI分析サービス"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.prompt_service = PromptService()
        self.model = settings.OPENAI_MODEL or "gpt-4-turbo-preview"
        self.max_tokens = 4000
        self.temperature = 0.1
        
        # トークン使用量とコスト追跡
        self.total_tokens_used = 0
        self.total_cost = 0.0
        
        logger.info(f"AnalysisService initialized with model: {self.model}")

    async def analyze_counseling(
        self, 
        transcription_text: str,
        analysis_type: AnalysisType = AnalysisType.FULL,
        focus_areas: List[str] = None,
        custom_prompts: Dict[str, str] = None
    ) -> Tuple[AnalysisResult, int, float]:
        """カウンセリング内容の包括分析
        
        Returns:
            Tuple[AnalysisResult, tokens_used, cost]
        """
        try:
            logger.info(f"Starting analysis: type={analysis_type}, focus_areas={focus_areas}")
            
            # 前処理: テキストクリーニング
            cleaned_text = await self._preprocess_text(transcription_text)
            
            tokens_used = 0
            cost = 0.0
            
            # 分析実行
            if analysis_type == AnalysisType.FULL:
                result, tokens, analysis_cost = await self._full_analysis(cleaned_text, custom_prompts)
            elif analysis_type == AnalysisType.QUICK:
                result, tokens, analysis_cost = await self._quick_analysis(cleaned_text)
            else:
                result, tokens, analysis_cost = await self._specific_analysis(cleaned_text, focus_areas, custom_prompts)
            
            tokens_used += tokens
            cost += analysis_cost
            
            logger.info(f"Analysis completed: tokens={tokens_used}, cost=${cost:.4f}")
            return result, tokens_used, cost
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise Exception(f"分析処理エラー: {e}")

    async def _full_analysis(
        self, 
        text: str, 
        custom_prompts: Dict[str, str] = None
    ) -> Tuple[AnalysisResult, int, float]:
        """包括的分析"""
        try:
            total_tokens = 0
            total_cost = 0.0
            
            # 並列分析実行
            tasks = []
            
            # 各分析項目のタスクを作成
            if custom_prompts and "questioning" in custom_prompts:
                tasks.append(self._analyze_with_custom_prompt("questioning", text, custom_prompts["questioning"]))
            else:
                tasks.append(self._analyze_questioning(text))
            
            if custom_prompts and "anxiety_handling" in custom_prompts:
                tasks.append(self._analyze_with_custom_prompt("anxiety_handling", text, custom_prompts["anxiety_handling"]))
            else:
                tasks.append(self._analyze_anxiety_handling(text))
            
            if custom_prompts and "closing" in custom_prompts:
                tasks.append(self._analyze_with_custom_prompt("closing", text, custom_prompts["closing"]))
            else:
                tasks.append(self._analyze_closing(text))
            
            if custom_prompts and "flow" in custom_prompts:
                tasks.append(self._analyze_with_custom_prompt("flow", text, custom_prompts["flow"]))
            else:
                tasks.append(self._analyze_flow(text))
            
            # 並列実行
            results = await asyncio.gather(*tasks)
            
            questioning = results[0][0]
            anxiety = results[1][0]
            closing = results[2][0]
            flow = results[3][0]
            
            # トークン使用量とコストを集計
            for result in results:
                total_tokens += result[1]
                total_cost += result[2]
            
            # 全体スコア計算
            overall_score = (
                questioning.score * 0.25 +
                anxiety.score * 0.25 +
                closing.score * 0.30 +
                flow.score * 0.20
            )
            
            # 包括的な要約と改善提案生成
            summary_tokens, summary_cost, session_summary, key_strengths, critical_improvements = await self._generate_comprehensive_analysis(
                text, questioning, anxiety, closing, flow
            )
            
            total_tokens += summary_tokens
            total_cost += summary_cost
            
            result = AnalysisResult(
                overall_score=round(overall_score, 2),
                questioning=questioning,
                anxiety_handling=anxiety,
                closing=closing,
                flow=flow,
                session_summary=session_summary,
                key_strengths=key_strengths,
                critical_improvements=critical_improvements,
                analyzed_at=datetime.utcnow()
            )
            
            return result, total_tokens, total_cost
            
        except Exception as e:
            logger.error(f"Full analysis failed: {e}")
            raise Exception(f"包括分析エラー: {e}")

    async def _quick_analysis(self, text: str) -> Tuple[AnalysisResult, int, float]:
        """クイック分析（簡易版）"""
        try:
            prompt = f"""
以下のカウンセリング内容を簡易分析し、主要な4項目についてスコアと簡潔な評価を提供してください。

【文字起こし】
{text[:2000]}  # 最初の2000文字のみ

以下のJSON形式で回答してください：
{{
    "questioning_score": 7.5,
    "anxiety_handling_score": 8.0,
    "closing_score": 6.5,
    "flow_score": 7.0,
    "session_summary": "セッションの簡潔な要約",
    "key_improvements": ["改善点1", "改善点2", "改善点3"]
}}
"""
            
            response, tokens, cost = await self._call_openai_api(prompt)
            result_data = json.loads(response)
            
            # 簡易結果から詳細結果を構築
            questioning = QuestioningAnalysis(
                score=result_data.get("questioning_score", 5.0),
                open_question_ratio=0.5,  # デフォルト値
                customer_talk_time_ratio=0.5,
                question_diversity=5,
                effective_questions=[],
                improvements=result_data.get("key_improvements", [])[:2]
            )
            
            anxiety = AnxietyHandlingAnalysis(
                score=result_data.get("anxiety_handling_score", 5.0),
                anxiety_points_identified=[],
                empathy_expressions=0,
                solution_specificity=0.5,
                anxiety_resolution_confirmed=False,
                improvements=[]
            )
            
            closing = ClosingAnalysis(
                score=result_data.get("closing_score", 5.0),
                timing_appropriateness=0.5,
                urgency_creation=0.5,
                limitation_usage=0.5,
                price_presentation_method="標準的な提示",
                objection_handling=[],
                contract_probability=0.5,
                improvements=[]
            )
            
            flow = FlowAnalysis(
                score=result_data.get("flow_score", 5.0),
                logical_structure=0.5,
                smooth_transitions=0.5,
                customer_pace_consideration=0.5,
                key_point_emphasis=0.5,
                session_satisfaction_prediction=0.5,
                improvements=[]
            )
            
            overall_score = (
                questioning.score + anxiety.score + closing.score + flow.score
            ) / 4
            
            result = AnalysisResult(
                overall_score=round(overall_score, 2),
                questioning=questioning,
                anxiety_handling=anxiety,
                closing=closing,
                flow=flow,
                session_summary=result_data.get("session_summary", "クイック分析により生成された要約"),
                key_strengths=["クイック分析のため詳細な強み分析は省略"],
                critical_improvements=result_data.get("key_improvements", []),
                analyzed_at=datetime.utcnow()
            )
            
            return result, tokens, cost
            
        except Exception as e:
            logger.error(f"Quick analysis failed: {e}")
            raise Exception(f"クイック分析エラー: {e}")

    async def _specific_analysis(
        self, 
        text: str, 
        focus_areas: List[str],
        custom_prompts: Dict[str, str] = None
    ) -> Tuple[AnalysisResult, int, float]:
        """特定項目分析"""
        try:
            total_tokens = 0
            total_cost = 0.0
            
            # デフォルト値で初期化
            questioning = QuestioningAnalysis(
                score=5.0, open_question_ratio=0.5, customer_talk_time_ratio=0.5,
                question_diversity=5, effective_questions=[], improvements=[]
            )
            anxiety = AnxietyHandlingAnalysis(
                score=5.0, anxiety_points_identified=[], empathy_expressions=0,
                solution_specificity=0.5, anxiety_resolution_confirmed=False, improvements=[]
            )
            closing = ClosingAnalysis(
                score=5.0, timing_appropriateness=0.5, urgency_creation=0.5,
                limitation_usage=0.5, price_presentation_method="標準", objection_handling=[],
                contract_probability=0.5, improvements=[]
            )
            flow = FlowAnalysis(
                score=5.0, logical_structure=0.5, smooth_transitions=0.5,
                customer_pace_consideration=0.5, key_point_emphasis=0.5,
                session_satisfaction_prediction=0.5, improvements=[]
            )
            
            # 指定された項目のみ分析
            if "questioning" in focus_areas:
                if custom_prompts and "questioning" in custom_prompts:
                    questioning, tokens, cost = await self._analyze_with_custom_prompt("questioning", text, custom_prompts["questioning"])
                else:
                    questioning, tokens, cost = await self._analyze_questioning(text)
                total_tokens += tokens
                total_cost += cost
            
            if "anxiety_handling" in focus_areas:
                if custom_prompts and "anxiety_handling" in custom_prompts:
                    anxiety, tokens, cost = await self._analyze_with_custom_prompt("anxiety_handling", text, custom_prompts["anxiety_handling"])
                else:
                    anxiety, tokens, cost = await self._analyze_anxiety_handling(text)
                total_tokens += tokens
                total_cost += cost
            
            if "closing" in focus_areas:
                if custom_prompts and "closing" in custom_prompts:
                    closing, tokens, cost = await self._analyze_with_custom_prompt("closing", text, custom_prompts["closing"])
                else:
                    closing, tokens, cost = await self._analyze_closing(text)
                total_tokens += tokens
                total_cost += cost
            
            if "flow" in focus_areas:
                if custom_prompts and "flow" in custom_prompts:
                    flow, tokens, cost = await self._analyze_with_custom_prompt("flow", text, custom_prompts["flow"])
                else:
                    flow, tokens, cost = await self._analyze_flow(text)
                total_tokens += tokens
                total_cost += cost
            
            # 全体スコア計算（分析された項目のみ）
            analyzed_scores = []
            if "questioning" in focus_areas:
                analyzed_scores.append(questioning.score)
            if "anxiety_handling" in focus_areas:
                analyzed_scores.append(anxiety.score)
            if "closing" in focus_areas:
                analyzed_scores.append(closing.score)
            if "flow" in focus_areas:
                analyzed_scores.append(flow.score)
            
            overall_score = sum(analyzed_scores) / len(analyzed_scores) if analyzed_scores else 5.0
            
            result = AnalysisResult(
                overall_score=round(overall_score, 2),
                questioning=questioning,
                anxiety_handling=anxiety,
                closing=closing,
                flow=flow,
                session_summary=f"特定項目分析: {', '.join(focus_areas)}",
                key_strengths=[f"{area}の分析完了" for area in focus_areas],
                critical_improvements=["特定項目分析のため包括的な改善提案は省略"],
                analyzed_at=datetime.utcnow()
            )
            
            return result, total_tokens, total_cost
            
        except Exception as e:
            logger.error(f"Specific analysis failed: {e}")
            raise Exception(f"特定項目分析エラー: {e}")

    async def _analyze_questioning(self, text: str) -> Tuple[QuestioningAnalysis, int, float]:
        """質問技法分析"""
        try:
            prompt = self.prompt_service.get_questioning_prompt(text)
            response, tokens, cost = await self._call_openai_api(prompt)
            result_data = self._parse_json_response(response)
            
            return QuestioningAnalysis(**result_data), tokens, cost
            
        except Exception as e:
            logger.error(f"Questioning analysis failed: {e}")
            # フォールバック結果
            return QuestioningAnalysis(
                score=5.0, open_question_ratio=0.5, customer_talk_time_ratio=0.5,
                question_diversity=5, effective_questions=[], 
                improvements=[f"分析エラー: {str(e)[:100]}"]
            ), 0, 0.0

    async def _analyze_anxiety_handling(self, text: str) -> Tuple[AnxietyHandlingAnalysis, int, float]:
        """不安対応分析"""
        try:
            prompt = self.prompt_service.get_anxiety_prompt(text)
            response, tokens, cost = await self._call_openai_api(prompt)
            result_data = self._parse_json_response(response)
            
            return AnxietyHandlingAnalysis(**result_data), tokens, cost
            
        except Exception as e:
            logger.error(f"Anxiety handling analysis failed: {e}")
            return AnxietyHandlingAnalysis(
                score=5.0, anxiety_points_identified=[], empathy_expressions=0,
                solution_specificity=0.5, anxiety_resolution_confirmed=False,
                improvements=[f"分析エラー: {str(e)[:100]}"]
            ), 0, 0.0

    async def _analyze_closing(self, text: str) -> Tuple[ClosingAnalysis, int, float]:
        """クロージング分析"""
        try:
            prompt = self.prompt_service.get_closing_prompt(text)
            response, tokens, cost = await self._call_openai_api(prompt)
            result_data = self._parse_json_response(response)
            
            return ClosingAnalysis(**result_data), tokens, cost
            
        except Exception as e:
            logger.error(f"Closing analysis failed: {e}")
            return ClosingAnalysis(
                score=5.0, timing_appropriateness=0.5, urgency_creation=0.5,
                limitation_usage=0.5, price_presentation_method="標準",
                objection_handling=[], contract_probability=0.5,
                improvements=[f"分析エラー: {str(e)[:100]}"]
            ), 0, 0.0

    async def _analyze_flow(self, text: str) -> Tuple[FlowAnalysis, int, float]:
        """トーク流れ分析"""
        try:
            prompt = self.prompt_service.get_flow_prompt(text)
            response, tokens, cost = await self._call_openai_api(prompt)
            result_data = self._parse_json_response(response)
            
            return FlowAnalysis(**result_data), tokens, cost
            
        except Exception as e:
            logger.error(f"Flow analysis failed: {e}")
            return FlowAnalysis(
                score=5.0, logical_structure=0.5, smooth_transitions=0.5,
                customer_pace_consideration=0.5, key_point_emphasis=0.5,
                session_satisfaction_prediction=0.5,
                improvements=[f"分析エラー: {str(e)[:100]}"]
            ), 0, 0.0

    async def _analyze_with_custom_prompt(
        self, 
        analysis_type: str, 
        text: str, 
        custom_prompt: str
    ) -> Tuple[any, int, float]:
        """カスタムプロンプトによる分析"""
        try:
            full_prompt = f"{custom_prompt}\n\n【文字起こし】\n{text}"
            response, tokens, cost = await self._call_openai_api(full_prompt)
            result_data = self._parse_json_response(response)
            
            # 分析タイプに応じて適切なクラスを返す
            if analysis_type == "questioning":
                return QuestioningAnalysis(**result_data), tokens, cost
            elif analysis_type == "anxiety_handling":
                return AnxietyHandlingAnalysis(**result_data), tokens, cost
            elif analysis_type == "closing":
                return ClosingAnalysis(**result_data), tokens, cost
            elif analysis_type == "flow":
                return FlowAnalysis(**result_data), tokens, cost
            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")
                
        except Exception as e:
            logger.error(f"Custom prompt analysis failed for {analysis_type}: {e}")
            raise

    async def _generate_comprehensive_analysis(
        self, 
        text: str, 
        questioning: QuestioningAnalysis,
        anxiety: AnxietyHandlingAnalysis, 
        closing: ClosingAnalysis, 
        flow: FlowAnalysis
    ) -> Tuple[int, float, str, List[str], List[str]]:
        """包括的な要約と改善提案生成"""
        try:
            prompt = self.prompt_service.get_comprehensive_analysis_prompt(text)
            response, tokens, cost = await self._call_openai_api(prompt)
            result_data = self._parse_json_response(response)
            
            session_summary = result_data.get("session_summary", "要約生成に失敗しました")
            key_strengths = result_data.get("key_strengths", [])
            critical_improvements = result_data.get("critical_improvements", [])
            
            return tokens, cost, session_summary, key_strengths, critical_improvements
            
        except Exception as e:
            logger.error(f"Comprehensive analysis generation failed: {e}")
            return 0, 0.0, "要約生成エラー", ["分析完了"], ["詳細分析が必要"]

    async def _call_openai_api(self, prompt: str) -> Tuple[str, int, float]:
        """OpenAI API呼び出し"""
        try:
            if not settings.OPENAI_API_KEY:
                # 開発環境用のダミーレスポンス
                logger.warning("OpenAI API key not provided, using dummy response")
                return self._create_dummy_response(prompt), 0, 0.0
            
            messages = [
                {"role": "system", "content": self.prompt_service.get_system_prompt()},
                {"role": "user", "content": prompt}
            ]
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # コスト計算（概算）
            cost = self._calculate_cost(tokens_used)
            
            self.total_tokens_used += tokens_used
            self.total_cost += cost
            
            return content, tokens_used, cost
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise Exception(f"OpenAI API呼び出しエラー: {e}")

    def _calculate_cost(self, tokens_used: int) -> float:
        """コスト計算（GPT-4の概算料金）"""
        # GPT-4の概算料金（2024年1月時点）
        input_cost_per_1k = 0.03  # $0.03 per 1K tokens
        output_cost_per_1k = 0.06  # $0.06 per 1K tokens
        
        # 簡易計算（入力と出力を半々と仮定）
        return (tokens_used / 1000) * ((input_cost_per_1k + output_cost_per_1k) / 2)

    def _create_dummy_response(self, prompt: str) -> str:
        """開発用のダミーレスポンス"""
        if "questioning" in prompt.lower():
            return json.dumps({
                "score": 7.5,
                "open_question_ratio": 0.6,
                "customer_talk_time_ratio": 0.7,
                "question_diversity": 8,
                "effective_questions": ["どのような点がご不安ですか？", "他にご質問はございますか？"],
                "improvements": ["より具体的な質問を増やす", "顧客の感情に寄り添う質問を追加"]
            })
        elif "anxiety" in prompt.lower():
            return json.dumps({
                "score": 8.2,
                "anxiety_points_identified": ["痛みへの不安", "料金への心配"],
                "empathy_expressions": 5,
                "solution_specificity": 0.8,
                "anxiety_resolution_confirmed": True,
                "improvements": ["具体的な事例を使った説明を増やす"]
            })
        elif "closing" in prompt.lower():
            return json.dumps({
                "score": 6.8,
                "timing_appropriateness": 0.7,
                "urgency_creation": 0.5,
                "limitation_usage": 0.6,
                "price_presentation_method": "段階的価格提示",
                "objection_handling": ["料金に関する懸念への対応"],
                "contract_probability": 0.75,
                "improvements": ["限定性をより効果的に活用", "価格提示のタイミング調整"]
            })
        elif "flow" in prompt.lower():
            return json.dumps({
                "score": 7.9,
                "logical_structure": 0.8,
                "smooth_transitions": 0.7,
                "customer_pace_consideration": 0.9,
                "key_point_emphasis": 0.6,
                "session_satisfaction_prediction": 0.85,
                "improvements": ["重要ポイントの強調を改善"]
            })
        else:
            return json.dumps({
                "session_summary": "開発環境用のダミー分析結果です。顧客のニーズを適切に把握し、不安に対して丁寧に対応されていました。",
                "key_strengths": ["丁寧な説明", "顧客ペースに配慮", "専門知識の活用"],
                "critical_improvements": ["クロージングの強化", "限定性の活用", "価格提示の改善"],
                "overall_score": 7.2
            })

    async def _preprocess_text(self, text: str) -> str:
        """テキスト前処理"""
        if not text:
            return ""
        
        # 基本的なクリーニング
        cleaned = text.strip()
        
        # 個人情報のマスキング（簡易版）
        # 電話番号のマスキング
        cleaned = re.sub(r'\d{2,4}-\d{2,4}-\d{4}', '[電話番号]', cleaned)
        # メールアドレスのマスキング
        cleaned = re.sub(r'\S+@\S+\.\S+', '[メールアドレス]', cleaned)
        
        # 過度に長いテキストの制限（GPT-4のコンテキスト制限を考慮）
        max_length = 8000  # 約8000文字まで
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "...[テキストが制限により切り詰められました]"
            logger.warning(f"Text truncated from {len(text)} to {max_length} characters")
        
        return cleaned

    def _parse_json_response(self, response: str) -> dict:
        """JSONレスポンスのパース"""
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}, response: {response[:200]}...")
            # JSONの修復を試行
            cleaned_response = self._repair_json(response)
            try:
                return json.loads(cleaned_response)
            except json.JSONDecodeError:
                # 最終的に失敗した場合はデフォルト値を返す
                return {"score": 5.0, "improvements": ["JSON解析エラーが発生しました"]}

    def _repair_json(self, response: str) -> str:
        """壊れたJSONの修復を試行"""
        # 一般的なJSON修復パターン
        response = response.strip()
        
        # ```json ブロックの除去
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'\s*```', '', response)
        
        # 不完全な配列やオブジェクトの修復
        if response.endswith(','):
            response = response[:-1]
        
        # 基本的な構造の確認と修復
        if not response.startswith('{'):
            response = '{' + response
        if not response.endswith('}'):
            response = response + '}'
        
        return response

    def get_analysis_statistics(self) -> dict:
        """分析統計情報の取得"""
        return {
            "total_tokens_used": self.total_tokens_used,
            "total_cost": round(self.total_cost, 4),
            "model": self.model,
            "service_status": "active" if settings.OPENAI_API_KEY else "development_mode"
        }