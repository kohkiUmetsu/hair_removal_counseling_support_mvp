"""
Prompt management service for AI analysis
"""
from pathlib import Path
from typing import Dict, Optional
import jinja2
import logging

logger = logging.getLogger(__name__)

class PromptService:
    """プロンプトテンプレート管理サービス"""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "prompts"
        self.template_dir.mkdir(exist_ok=True)
        
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            autoescape=True
        )
        
        # プロンプトテンプレートが存在しない場合は作成
        self._ensure_prompt_templates()
        
        logger.info("PromptService initialized")

    def get_system_prompt(self) -> str:
        """システムプロンプト取得"""
        return """
あなたは美容医療脱毛クリニックのカウンセリング専門家です。
カウンセリングの文字起こしを分析し、以下の観点で客観的に評価してください：

1. 質問技法の効果性
2. 顧客不安への対応
3. クロージング手法  
4. 全体的な流れ

分析結果は必ずJSON形式で返し、具体的な改善提案を含めてください。
スコアは1-10の範囲で、具体例を必ず含めてください。
美容医療業界の専門知識を活用し、実用的なアドバイスを提供してください。
"""

    def get_questioning_prompt(self, text: str) -> str:
        """質問分析プロンプト"""
        try:
            template = self.env.get_template("questioning_analysis.txt")
            return template.render(transcription=text)
        except jinja2.TemplateNotFound:
            # フォールバック用の直接テンプレート
            return f"""
以下のカウンセリング文字起こしを分析し、質問技法について評価してください。

【文字起こし】
{text}

【分析項目】
1. オープンクエスチョンとクローズドクエスチョンの使い分け
2. 顧客の発言時間比率
3. 質問の多様性と深さ
4. 効果的だった質問例
5. 改善すべき質問例

以下のJSON形式で回答してください：
{{
    "score": 7.5,
    "open_question_ratio": 0.6,
    "customer_talk_time_ratio": 0.7,
    "question_diversity": 8,
    "effective_questions": ["具体的な質問例1", "具体的な質問例2"],
    "improvements": ["改善点1", "改善点2"]
}}
"""

    def get_anxiety_prompt(self, text: str) -> str:
        """不安対応分析プロンプト"""
        try:
            template = self.env.get_template("anxiety_analysis.txt")
            return template.render(transcription=text)
        except jinja2.TemplateNotFound:
            return f"""
以下のカウンセリング文字起こしを分析し、顧客の不安への対応について評価してください。

【文字起こし】
{text}

【分析項目】
1. 顧客の不安要素の特定と理解
2. 共感的な対応の質と頻度
3. 具体的な解決策の提示
4. 不安解消の確認
5. 安心感の醸成

以下のJSON形式で回答してください：
{{
    "score": 8.2,
    "anxiety_points_identified": ["不安要素1", "不安要素2"],
    "empathy_expressions": 5,
    "solution_specificity": 0.8,
    "anxiety_resolution_confirmed": true,
    "improvements": ["改善点1", "改善点2"]
}}
"""

    def get_closing_prompt(self, text: str) -> str:
        """クロージング分析プロンプト"""
        try:
            template = self.env.get_template("closing_analysis.txt")
            return template.render(transcription=text)
        except jinja2.TemplateNotFound:
            return f"""
以下のカウンセリング文字起こしを分析し、クロージング手法について評価してください。

【文字起こし】
{text}

【分析項目】
1. クロージングのタイミングの適切さ
2. 緊急性の演出効果
3. 限定性の活用
4. 価格提示の方法と効果
5. 異議処理の技法
6. 契約への誘導力

以下のJSON形式で回答してください：
{{
    "score": 6.8,
    "timing_appropriateness": 0.7,
    "urgency_creation": 0.5,
    "limitation_usage": 0.6,
    "price_presentation_method": "段階的価格提示",
    "objection_handling": ["異議処理例1", "異議処理例2"],
    "contract_probability": 0.75,
    "improvements": ["改善点1", "改善点2"]
}}
"""

    def get_flow_prompt(self, text: str) -> str:
        """フロー分析プロンプト"""
        try:
            template = self.env.get_template("flow_analysis.txt")
            return template.render(transcription=text)
        except jinja2.TemplateNotFound:
            return f"""
以下のカウンセリング文字起こしを分析し、トークの流れについて評価してください。

【文字起こし】
{text}

【分析項目】
1. セッション構成の論理性
2. 話題転換のスムーズさ
3. 顧客ペースへの配慮
4. 重要ポイントの強調
5. 全体的な満足度予測

以下のJSON形式で回答してください：
{{
    "score": 7.9,
    "logical_structure": 0.8,
    "smooth_transitions": 0.7,
    "customer_pace_consideration": 0.9,
    "key_point_emphasis": 0.6,
    "session_satisfaction_prediction": 0.85,
    "improvements": ["改善点1", "改善点2"]
}}
"""

    def get_comprehensive_analysis_prompt(self, text: str) -> str:
        """包括分析プロンプト"""
        return f"""
以下のカウンセリング文字起こしを総合的に分析し、包括的な評価とセッション要約を提供してください。

【文字起こし】
{text}

【総合分析項目】
1. セッション全体の要約（200文字以内）
2. 主な強み（3-5項目）
3. 重要な改善点（3-5項目）
4. 総合スコア（1-10）

以下のJSON形式で回答してください：
{{
    "session_summary": "このセッションの要約...",
    "key_strengths": ["強み1", "強み2", "強み3"],
    "critical_improvements": ["重要改善点1", "重要改善点2", "重要改善点3"],
    "overall_score": 7.5
}}
"""

    def get_custom_prompt(self, template_name: str, **kwargs) -> str:
        """カスタムプロンプト取得"""
        try:
            template = self.env.get_template(f"{template_name}.txt")
            return template.render(**kwargs)
        except jinja2.TemplateNotFound:
            logger.warning(f"Template not found: {template_name}")
            return ""

    def _ensure_prompt_templates(self) -> None:
        """プロンプトテンプレートファイルを確保"""
        templates = {
            "questioning_analysis.txt": """
以下のカウンセリング文字起こしの質問技法を分析してください。

【文字起こし】
{{ transcription }}

【分析観点】
- オープンクエスチョンとクローズドクエスチョンの効果的な使い分け
- 顧客の本音を引き出す質問力
- 質問の多様性と深掘り力
- 顧客の発言を促す質問技法

JSON形式で回答してください：
{
    "score": (1-10のスコア),
    "open_question_ratio": (0-1の比率),
    "customer_talk_time_ratio": (0-1の比率),
    "question_diversity": (質問の種類数),
    "effective_questions": ["効果的だった質問例"],
    "improvements": ["改善提案"]
}
""",
            "anxiety_analysis.txt": """
以下のカウンセリング文字起こしの不安対応を分析してください。

【文字起こし】
{{ transcription }}

【分析観点】
- 顧客の不安要素の特定精度
- 共感的な対応の質と頻度
- 具体的で分かりやすい解決策提示
- 不安解消の確認と安心感の醸成

JSON形式で回答してください：
{
    "score": (1-10のスコア),
    "anxiety_points_identified": ["特定された不安要素"],
    "empathy_expressions": (共感表現の回数),
    "solution_specificity": (0-1の具体性スコア),
    "anxiety_resolution_confirmed": (true/false),
    "improvements": ["改善提案"]
}
""",
            "closing_analysis.txt": """
以下のカウンセリング文字起こしのクロージング手法を分析してください。

【文字起こし】
{{ transcription }}

【分析観点】
- クロージングタイミングの適切さ
- 緊急性と限定性の効果的活用
- 価格提示方法の巧妙さ
- 異議処理の技法
- 契約への誘導力

JSON形式で回答してください：
{
    "score": (1-10のスコア),
    "timing_appropriateness": (0-1のタイミングスコア),
    "urgency_creation": (0-1の緊急性スコア),
    "limitation_usage": (0-1の限定性スコア),
    "price_presentation_method": "価格提示手法の説明",
    "objection_handling": ["異議処理の例"],
    "contract_probability": (0-1の契約確度),
    "improvements": ["改善提案"]
}
""",
            "flow_analysis.txt": """
以下のカウンセリング文字起こしのトーク流れを分析してください。

【文字起こし】
{{ transcription }}

【分析観点】
- セッション構成の論理性と自然さ
- 話題転換のスムーズさ
- 顧客ペースへの配慮
- 重要ポイントの効果的強調
- 全体的な満足度予測

JSON形式で回答してください：
{
    "score": (1-10のスコア),
    "logical_structure": (0-1の論理性スコア),
    "smooth_transitions": (0-1の転換スムーズさ),
    "customer_pace_consideration": (0-1の配慮スコア),
    "key_point_emphasis": (0-1の強調効果),
    "session_satisfaction_prediction": (0-1の満足度予測),
    "improvements": ["改善提案"]
}
"""
        }
        
        for filename, content in templates.items():
            template_path = self.template_dir / filename
            if not template_path.exists():
                try:
                    template_path.write_text(content.strip(), encoding='utf-8')
                    logger.info(f"Created template: {filename}")
                except Exception as e:
                    logger.error(f"Failed to create template {filename}: {e}")

    def validate_template(self, template_name: str) -> bool:
        """テンプレートの妥当性チェック"""
        try:
            template = self.env.get_template(f"{template_name}.txt")
            # 簡単なレンダリングテスト
            template.render(transcription="test")
            return True
        except Exception as e:
            logger.error(f"Template validation failed for {template_name}: {e}")
            return False

    def list_templates(self) -> list[str]:
        """利用可能なテンプレート一覧"""
        if not self.template_dir.exists():
            return []
        
        return [
            f.stem for f in self.template_dir.glob("*.txt")
            if f.is_file()
        ]

    def get_template_content(self, template_name: str) -> Optional[str]:
        """テンプレート内容の取得"""
        template_path = self.template_dir / f"{template_name}.txt"
        if template_path.exists():
            try:
                return template_path.read_text(encoding='utf-8')
            except Exception as e:
                logger.error(f"Failed to read template {template_name}: {e}")
        return None

    def update_template(self, template_name: str, content: str) -> bool:
        """テンプレート内容の更新"""
        template_path = self.template_dir / f"{template_name}.txt"
        try:
            template_path.write_text(content, encoding='utf-8')
            # テンプレート環境をリロード
            self.env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(self.template_dir),
                autoescape=True
            )
            logger.info(f"Updated template: {template_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to update template {template_name}: {e}")
            return False