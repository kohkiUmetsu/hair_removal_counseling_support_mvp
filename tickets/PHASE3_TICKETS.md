# Phase 3: AI分析機能チケット（4週間）

## 概要
GPT-4を活用したカウンセリング内容の分析、改善提案、管理者向けダッシュボードを実装するフェーズです。本システムの核となるAI分析機能を含みます。

**期間**: 4週間  
**並列作業**: 一部可能（依存関係に注意）  
**チーム**: バックエンド、フロントエンド、データサイエンス  
**前提条件**: Phase 2完了（文字起こし機能済み）

---

## ✅ Ticket-09: AI Analysis Service - GPT-4 Integration
**優先度**: 🟡 Medium  
**工数見積**: 6日  
**担当者**: バックエンドエンジニア + データサイエンティスト  
**依存関係**: Phase 2完了（文字起こし機能）  
**ステータス**: ✅ 完了

### 概要
GPT-4を使用したカウンセリング分析機能を実装する

### 実装内容
- OpenAI GPT-4 API連携
- カウンセリング分析ロジック
- 分析結果構造化
- プロンプトテンプレート管理
- 分析結果保存
- 非同期処理対応

### 分析項目詳細

#### 1. 質問の誘導性分析
```yaml
分析観点:
  - オープンクエスチョン vs クローズドクエスチョン
  - 顧客の本音を引き出す質問技法
  - 不安や悩みを深掘りする質問
  - 意思決定を促す質問のタイミング

評価指標:
  - 誘導度スコア (1-10)
  - 質問の多様性
  - 顧客発言時間比率
```

#### 2. 顧客不安への対応度評価
```yaml
分析観点:
  - 不安要素の特定と理解
  - 共感的な対応
  - 具体的な解決策提示
  - 不安解消の確認

評価指標:
  - 不安対応スコア (1-10)
  - 共感表現の頻度
  - 解決策提示の具体性
```

#### 3. クロージング手法の評価
```yaml
分析観点:
  - クロージングのタイミング
  - 緊急性の演出
  - 限定性の活用
  - 価格提示の方法
  - 異議処理の技法

評価指標:
  - クロージング効果スコア (1-10)
  - 契約確度
  - 価格受容度
```

#### 4. トーク流れの分析
```yaml
分析観点:
  - セッション構成の論理性
  - 話題転換のスムーズさ
  - 顧客ペースへの配慮
  - 重要ポイントの強調

評価指標:
  - 流れスコア (1-10)
  - セッション満足度予測
  - 改善ポイント特定
```

### API仕様
```yaml
POST /api/analysis
  Headers:
    Authorization: Bearer {token}
  Request:
    transcription_id: UUID
    analysis_type: "full" | "quick" | "specific"
    focus_areas: string[] # ["questioning", "anxiety_handling", "closing", "flow"]
  Response:
    analysis_id: UUID
    task_id: UUID
    status: "started"
    estimated_duration: number

GET /api/analysis/status/{task_id}
  Response:
    task_id: UUID
    status: "pending" | "processing" | "completed" | "failed"
    progress: number
    stage: string # "preprocessing" | "analyzing" | "generating_suggestions" | "completed"

GET /api/analysis/result/{analysis_id}
  Response:
    analysis_id: UUID
    transcription_id: UUID
    overall_score: number
    analysis_details: AnalysisResult
    suggestions: Suggestion[]
    created_at: datetime

POST /api/analysis/batch
  Request:
    transcription_ids: UUID[]
    analysis_type: string
  Response:
    batch_id: UUID
    task_ids: UUID[]
```

### データモデル
```python
# schemas/analysis.py
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class AnalysisType(str, Enum):
    FULL = "full"
    QUICK = "quick"
    SPECIFIC = "specific"

class QuestioningAnalysis(BaseModel):
    score: float  # 1-10
    open_question_ratio: float
    customer_talk_time_ratio: float
    question_diversity: int
    effective_questions: List[str]
    improvements: List[str]

class AnxietyHandlingAnalysis(BaseModel):
    score: float
    anxiety_points_identified: List[str]
    empathy_expressions: int
    solution_specificity: float
    anxiety_resolution_confirmed: bool
    improvements: List[str]

class ClosingAnalysis(BaseModel):
    score: float
    timing_appropriateness: float
    urgency_creation: float
    limitation_usage: float
    price_presentation_method: str
    objection_handling: List[str]
    contract_probability: float
    improvements: List[str]

class FlowAnalysis(BaseModel):
    score: float
    logical_structure: float
    smooth_transitions: float
    customer_pace_consideration: float
    key_point_emphasis: float
    session_satisfaction_prediction: float
    improvements: List[str]

class AnalysisResult(BaseModel):
    overall_score: float
    questioning: QuestioningAnalysis
    anxiety_handling: AnxietyHandlingAnalysis
    closing: ClosingAnalysis
    flow: FlowAnalysis
    session_summary: str
    key_strengths: List[str]
    critical_improvements: List[str]

class Suggestion(BaseModel):
    category: str  # "questioning", "anxiety_handling", "closing", "flow"
    priority: str  # "high", "medium", "low"
    title: str
    description: str
    example_script: Optional[str]
    expected_impact: str
```

### ファイル構成
```
backend/app/
├── api/analysis/
│   ├── __init__.py
│   └── router.py           # 分析API
├── services/
│   ├── analysis_service.py  # GPT-4分析サービス
│   └── prompt_service.py    # プロンプト管理
├── tasks/
│   └── analysis_tasks.py    # Celery分析タスク
├── schemas/
│   └── analysis.py         # 分析スキーマ
├── models/
│   └── analysis.py         # 分析モデル
└── prompts/                # プロンプトテンプレート
    ├── base_analysis.txt
    ├── questioning_analysis.txt
    ├── anxiety_analysis.txt
    ├── closing_analysis.txt
    └── flow_analysis.txt
```

### GPT-4分析サービス実装
```python
# services/analysis_service.py
import openai
from typing import Dict, List
import json
import asyncio
from app.schemas.analysis import AnalysisResult, AnalysisType
from app.services.prompt_service import PromptService

class AnalysisService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.prompt_service = PromptService()
        self.model = "gpt-4-turbo-preview"
        self.max_tokens = 4000
        self.temperature = 0.1

    async def analyze_counseling(
        self, 
        transcription_text: str,
        analysis_type: AnalysisType = AnalysisType.FULL,
        focus_areas: List[str] = None
    ) -> AnalysisResult:
        """カウンセリング内容の包括分析"""
        
        # 前処理: テキストクリーニング
        cleaned_text = await self._preprocess_text(transcription_text)
        
        # 分析実行
        if analysis_type == AnalysisType.FULL:
            return await self._full_analysis(cleaned_text)
        elif analysis_type == AnalysisType.QUICK:
            return await self._quick_analysis(cleaned_text)
        else:
            return await self._specific_analysis(cleaned_text, focus_areas)

    async def _full_analysis(self, text: str) -> AnalysisResult:
        """包括的分析"""
        try:
            # 並列分析実行
            tasks = [
                self._analyze_questioning(text),
                self._analyze_anxiety_handling(text),
                self._analyze_closing(text),
                self._analyze_flow(text)
            ]
            
            questioning, anxiety, closing, flow = await asyncio.gather(*tasks)
            
            # 全体スコア計算
            overall_score = (
                questioning.score * 0.25 +
                anxiety.score * 0.25 +
                closing.score * 0.30 +
                flow.score * 0.20
            )
            
            # 包括的な改善提案生成
            suggestions = await self._generate_comprehensive_suggestions(
                text, questioning, anxiety, closing, flow
            )
            
            return AnalysisResult(
                overall_score=overall_score,
                questioning=questioning,
                anxiety_handling=anxiety,
                closing=closing,
                flow=flow,
                session_summary=await self._generate_session_summary(text),
                key_strengths=await self._identify_strengths(questioning, anxiety, closing, flow),
                critical_improvements=suggestions[:3]  # 上位3つの重要な改善点
            )
            
        except Exception as e:
            raise Exception(f"分析処理エラー: {e}")

    async def _analyze_questioning(self, text: str) -> QuestioningAnalysis:
        """質問技法分析"""
        prompt = self.prompt_service.get_questioning_prompt(text)
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt_service.get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return QuestioningAnalysis(**result)

    async def _analyze_anxiety_handling(self, text: str) -> AnxietyHandlingAnalysis:
        """不安対応分析"""
        prompt = self.prompt_service.get_anxiety_prompt(text)
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt_service.get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return AnxietyHandlingAnalysis(**result)

    async def _analyze_closing(self, text: str) -> ClosingAnalysis:
        """クロージング分析"""
        prompt = self.prompt_service.get_closing_prompt(text)
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt_service.get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return ClosingAnalysis(**result)

    async def _analyze_flow(self, text: str) -> FlowAnalysis:
        """トーク流れ分析"""
        prompt = self.prompt_service.get_flow_prompt(text)
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt_service.get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return FlowAnalysis(**result)

    async def _preprocess_text(self, text: str) -> str:
        """テキスト前処理"""
        # 個人情報のマスキング
        # ノイズ除去
        # 発話者分離
        return text

    async def _generate_session_summary(self, text: str) -> str:
        """セッション要約生成"""
        prompt = f"""
        以下のカウンセリングセッションの内容を200文字以内で要約してください：
        
        {text[:2000]}  # 最初の2000文字のみ
        """
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
```

### プロンプト管理サービス
```python
# services/prompt_service.py
from pathlib import Path
from typing import Dict
import jinja2

class PromptService:
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "prompts"
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir)
        )

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
        """

    def get_questioning_prompt(self, text: str) -> str:
        """質問分析プロンプト"""
        template = self.env.get_template("questioning_analysis.txt")
        return template.render(transcription=text)

    def get_anxiety_prompt(self, text: str) -> str:
        """不安対応分析プロンプト"""
        template = self.env.get_template("anxiety_analysis.txt")
        return template.render(transcription=text)

    def get_closing_prompt(self, text: str) -> str:
        """クロージング分析プロンプト"""
        template = self.env.get_template("closing_analysis.txt")
        return template.render(transcription=text)

    def get_flow_prompt(self, text: str) -> str:
        """フロー分析プロンプト"""
        template = self.env.get_template("flow_analysis.txt")
        return template.render(transcription=text)
```

### 受け入れ基準
- [x] GPT-4 APIが正常に動作する
- [x] 4つの分析項目すべてが実装されている
- [x] 分析結果が構造化されて保存される
- [x] プロンプトテンプレートが管理されている
- [x] 分析精度が適切なレベル（手動評価で80%以上の妥当性）
- [x] API利用料金が予算内（月額10万円以内）
- [x] エラーハンドリングが実装されている
- [x] 非同期処理が実装されている
- [x] 個人情報が適切にマスキングされる

### パフォーマンス要件
- 分析時間: 3分以内
- 同時分析数: 3セッションまで
- エラー率: 5%以下
- レスポンス精度: 80%以上

---

## ✅ Ticket-10: Analysis Features - Improvement Suggestions
**優先度**: 🟡 Medium  
**工数見積**: 5日  
**担当者**: バックエンドエンジニア + フロントエンドエンジニア  
**依存関係**: Ticket-09（AI分析完了後）  
**ステータス**: ✅ 完了

### 概要
分析結果に基づく改善提案機能とスクリプト最適化機能を実装する

### 実装内容
- 改善提案生成ロジック
- スクリプト最適化機能
- 成功パターン学習機能
- 改善提案表示UI
- レポート生成機能
- A/Bテスト機能

### 機能詳細

#### 1. 改善提案生成
```python
class ImprovementSuggestionService:
    def generate_suggestions(self, analysis_result: AnalysisResult) -> List[Suggestion]:
        """分析結果から改善提案を生成"""
        suggestions = []
        
        # 質問技法の改善提案
        if analysis_result.questioning.score < 7:
            suggestions.extend(self._generate_questioning_suggestions(analysis_result.questioning))
        
        # 不安対応の改善提案
        if analysis_result.anxiety_handling.score < 7:
            suggestions.extend(self._generate_anxiety_suggestions(analysis_result.anxiety_handling))
        
        # クロージングの改善提案
        if analysis_result.closing.score < 7:
            suggestions.extend(self._generate_closing_suggestions(analysis_result.closing))
        
        # 優先度でソート
        suggestions.sort(key=lambda x: self._calculate_impact_score(x), reverse=True)
        
        return suggestions[:10]  # 上位10件
```

#### 2. 動的スクリプト生成
```python
class ScriptOptimizationService:
    def generate_optimized_script(
        self, 
        customer_profile: CustomerProfile,
        session_context: SessionContext,
        analysis_history: List[AnalysisResult]
    ) -> OptimizedScript:
        """顧客プロファイルと過去分析に基づく最適化スクリプト"""
        
        # 顧客特性分析
        customer_insights = self._analyze_customer_characteristics(customer_profile)
        
        # 成功パターン抽出
        success_patterns = self._extract_success_patterns(analysis_history)
        
        # カスタマイズドスクリプト生成
        script_sections = {
            'opening': self._generate_opening_script(customer_insights),
            'needs_assessment': self._generate_needs_script(customer_insights),
            'presentation': self._generate_presentation_script(customer_insights, success_patterns),
            'objection_handling': self._generate_objection_scripts(customer_insights),
            'closing': self._generate_closing_script(customer_insights, success_patterns)
        }
        
        return OptimizedScript(**script_sections)
```

### API仕様
```yaml
GET /api/analysis/{analysis_id}/suggestions
  Response:
    suggestions: Suggestion[]
    priority_actions: Suggestion[]
    script_recommendations: ScriptRecommendation[]

POST /api/analysis/generate-script
  Request:
    customer_id: UUID
    session_type: string
    focus_areas: string[]
  Response:
    script_id: UUID
    optimized_script: OptimizedScript
    success_probability: number

GET /api/analysis/success-patterns
  Query:
    counselor_id: UUID (optional)
    clinic_id: UUID (optional)
    date_range: DateRange
  Response:
    patterns: SuccessPattern[]
    best_practices: BestPractice[]

POST /api/analysis/feedback
  Request:
    analysis_id: UUID
    suggestion_id: UUID
    feedback_type: "helpful" | "not_helpful" | "implemented"
    comments: string
  Response:
    feedback_id: UUID

GET /api/analysis/performance-trends
  Query:
    counselor_id: UUID
    date_range: DateRange
  Response:
    trend_data: PerformanceTrend
    improvement_trajectory: ImprovementTrajectory
```

### データモデル
```python
# schemas/improvement.py
class Suggestion(BaseModel):
    id: UUID
    category: str
    priority: str
    title: str
    description: str
    example_script: Optional[str]
    expected_impact: str
    implementation_difficulty: str
    success_rate: float
    related_best_practices: List[str]

class OptimizedScript(BaseModel):
    script_id: UUID
    customer_type: str
    opening: ScriptSection
    needs_assessment: ScriptSection
    presentation: ScriptSection
    objection_handling: Dict[str, ScriptSection]
    closing: ScriptSection
    success_probability: float
    customization_notes: List[str]

class ScriptSection(BaseModel):
    content: str
    key_points: List[str]
    alternative_phrases: List[str]
    timing_notes: str
    body_language_tips: List[str]

class SuccessPattern(BaseModel):
    pattern_id: UUID
    category: str
    description: str
    success_rate: float
    usage_frequency: int
    example_sessions: List[UUID]
    counselor_performance_correlation: float

class BestPractice(BaseModel):
    practice_id: UUID
    title: str
    description: str
    category: str
    effectiveness_score: float
    adoption_rate: float
    implementation_tips: List[str]
```

### フロントエンド実装

#### 改善提案表示コンポーネント
```typescript
// components/analysis/ImprovementSuggestions.tsx
interface ImprovementSuggestionsProps {
  analysisId: string;
}

export const ImprovementSuggestions: React.FC<ImprovementSuggestionsProps> = ({
  analysisId
}) => {
  const { data: suggestions, isLoading } = useQuery(
    ['suggestions', analysisId],
    () => api.getSuggestions(analysisId)
  );

  const { mutate: submitFeedback } = useMutation(
    api.submitSuggestionFeedback
  );

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 優先度の高い改善提案 */}
        <div className="bg-red-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-red-800 mb-4">
            緊急改善事項
          </h3>
          {suggestions?.filter(s => s.priority === 'high').map(suggestion => (
            <SuggestionCard
              key={suggestion.id}
              suggestion={suggestion}
              onFeedback={submitFeedback}
              variant="urgent"
            />
          ))}
        </div>

        {/* 推奨改善提案 */}
        <div className="bg-blue-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-800 mb-4">
            推奨改善事項
          </h3>
          {suggestions?.filter(s => s.priority === 'medium').map(suggestion => (
            <SuggestionCard
              key={suggestion.id}
              suggestion={suggestion}
              onFeedback={submitFeedback}
              variant="recommended"
            />
          ))}
        </div>
      </div>

      {/* スクリプト提案 */}
      <ScriptRecommendations analysisId={analysisId} />
    </div>
  );
};
```

#### スクリプト最適化コンポーネント
```typescript
// components/analysis/ScriptOptimizer.tsx
export const ScriptOptimizer: React.FC = () => {
  const [customerProfile, setCustomerProfile] = useState<CustomerProfile>();
  const [generatedScript, setGeneratedScript] = useState<OptimizedScript>();

  const { mutate: generateScript, isLoading } = useMutation(
    api.generateOptimizedScript,
    {
      onSuccess: (data) => setGeneratedScript(data.optimized_script)
    }
  );

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* 顧客プロファイル入力 */}
      <CustomerProfileForm
        value={customerProfile}
        onChange={setCustomerProfile}
      />

      {/* スクリプト生成ボタン */}
      <div className="text-center">
        <button
          onClick={() => generateScript({
            customer_profile: customerProfile,
            session_type: 'initial_consultation'
          })}
          disabled={isLoading}
          className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? '最適化中...' : '最適化スクリプト生成'}
        </button>
      </div>

      {/* 生成されたスクリプト */}
      {generatedScript && (
        <div className="space-y-6">
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-green-800 mb-2">
              成功確率: {Math.round(generatedScript.success_probability * 100)}%
            </h3>
            <p className="text-green-700">
              このスクリプトは過去の成功パターンに基づいて最適化されています
            </p>
          </div>

          <ScriptSectionTabs script={generatedScript} />
        </div>
      )}
    </div>
  );
};
```

### 成功パターン学習機能
```python
# services/pattern_learning_service.py
class PatternLearningService:
    def learn_success_patterns(self, clinic_id: str) -> List[SuccessPattern]:
        """成功パターンの機械学習による抽出"""
        
        # 高スコアセッションの取得
        high_score_sessions = self._get_high_score_sessions(clinic_id, min_score=8.0)
        
        # 共通パターンの抽出
        patterns = []
        
        # 質問パターンの分析
        question_patterns = self._analyze_question_patterns(high_score_sessions)
        patterns.extend(question_patterns)
        
        # クロージングパターンの分析
        closing_patterns = self._analyze_closing_patterns(high_score_sessions)
        patterns.extend(closing_patterns)
        
        # トーク構成パターンの分析
        flow_patterns = self._analyze_flow_patterns(high_score_sessions)
        patterns.extend(flow_patterns)
        
        return patterns

    def _analyze_question_patterns(self, sessions: List[Session]) -> List[SuccessPattern]:
        """質問パターンの分析"""
        # NLP技術を使用した質問パターンの抽出
        # 共通するフレーズ、構造、タイミングの分析
        pass

    def update_success_rates(self):
        """成功率の更新（定期実行）"""
        # 過去30日間のデータを基に成功率を再計算
        # 新しいパターンの発見
        # 効果が低下したパターンの特定
        pass
```

### 受け入れ基準
- [x] 改善提案が適切に生成される
- [x] スクリプト最適化が動作する
- [x] 成功パターンが学習される
- [x] UIが使いやすい（UXテスト実施）
- [x] レポートが正常に生成される
- [x] データの信頼性が確保されている
- [x] フィードバック機能が動作する
- [x] パフォーマンス要件を満たす

### 品質指標
- 提案の有用性: 80%以上（カウンセラー評価）
- スクリプト成功率向上: 15%以上
- 学習パターン精度: 85%以上

---

## ✅ Ticket-11: Dashboard & Reports - Analytics Dashboard
**優先度**: 🟢 Low  
**工数見積**: 6日  
**担当者**: フロントエンドエンジニア + データエンジニア  
**依存関係**: Ticket-09, 10（分析機能完了後）  
**ステータス**: ✅ 完了

### 概要
管理者向けの分析ダッシュボードと包括的なレポート機能を実装する

### 実装内容
- 成約率ダッシュボード
- カウンセラー別統計
- 顧客分析レポート
- トレンド分析機能
- データエクスポート機能
- リアルタイム監視

### ダッシュボード構成

#### 1. エグゼクティブダッシュボード
```typescript
// 管理者向けの経営指標ダッシュボード
interface ExecutiveDashboard {
  kpis: {
    conversionRate: number;          // 成約率
    averageSessionScore: number;     // 平均セッションスコア
    monthlyRevenue: number;          // 月間売上
    customerSatisfaction: number;    // 顧客満足度
  };
  trends: {
    conversionTrend: TrendData[];
    scoreTrend: TrendData[];
    revenueTrend: TrendData[];
  };
  topPerformers: Counselor[];
  improvementOpportunities: OpportunityItem[];
}
```

#### 2. カウンセラーパフォーマンスダッシュボード
```typescript
interface CounselorDashboard {
  counselorStats: {
    totalSessions: number;
    averageScore: number;
    conversionRate: number;
    improvementRate: number;
  };
  skillBreakdown: {
    questioning: SkillScore;
    anxietyHandling: SkillScore;
    closing: SkillScore;
    flow: SkillScore;
  };
  recentPerformance: PerformanceData[];
  personalizedRecommendations: Recommendation[];
}
```

#### 3. オペレーションダッシュボード
```typescript
interface OperationDashboard {
  realTimeMetrics: {
    activeSessions: number;
    processingQueue: number;
    systemHealth: HealthStatus;
  };
  sessionAnalytics: {
    dailyVolume: VolumeData[];
    averageProcessingTime: number;
    errorRate: number;
  };
  qualityMetrics: {
    transcriptionAccuracy: number;
    analysisReliability: number;
    userSatisfaction: number;
  };
}
```

### API仕様
```yaml
GET /api/dashboard/executive
  Query:
    clinic_id: UUID (optional)
    date_range: DateRange
    time_zone: string
  Response:
    dashboard_data: ExecutiveDashboard

GET /api/dashboard/counselor/{counselor_id}
  Query:
    date_range: DateRange
    comparison_period: DateRange (optional)
  Response:
    dashboard_data: CounselorDashboard

GET /api/dashboard/operations
  Response:
    dashboard_data: OperationDashboard

GET /api/reports/performance
  Query:
    report_type: "counselor" | "clinic" | "customer"
    filters: ReportFilters
    format: "json" | "csv" | "pdf"
  Response:
    report_data: PerformanceReport | File

POST /api/reports/custom
  Request:
    metrics: string[]
    dimensions: string[]
    filters: CustomFilters
    visualization_type: string
  Response:
    report_id: UUID
    report_data: CustomReport

GET /api/analytics/trends
  Query:
    metric: string
    time_period: string
    granularity: "hour" | "day" | "week" | "month"
    counselor_ids: UUID[] (optional)
  Response:
    trend_data: TrendAnalysis
```

### フロントエンド実装

#### メインダッシュボードコンポーネント
```typescript
// components/dashboard/ExecutiveDashboard.tsx
export const ExecutiveDashboard: React.FC = () => {
  const [dateRange, setDateRange] = useState<DateRange>(getDefaultDateRange());
  const { data: dashboardData, isLoading } = useQuery(
    ['executive-dashboard', dateRange],
    () => api.getExecutiveDashboard({ date_range: dateRange })
  );

  return (
    <div className="p-6 space-y-6">
      {/* KPI カード */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="成約率"
          value={dashboardData?.kpis.conversionRate}
          format="percentage"
          trend={dashboardData?.trends.conversionTrend}
          target={0.85}
        />
        <KPICard
          title="平均スコア"
          value={dashboardData?.kpis.averageSessionScore}
          format="decimal"
          trend={dashboardData?.trends.scoreTrend}
          target={8.0}
        />
        <KPICard
          title="月間売上"
          value={dashboardData?.kpis.monthlyRevenue}
          format="currency"
          trend={dashboardData?.trends.revenueTrend}
        />
        <KPICard
          title="顧客満足度"
          value={dashboardData?.kpis.customerSatisfaction}
          format="score"
          target={9.0}
        />
      </div>

      {/* チャートエリア */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="成約率トレンド">
          <LineChart
            data={dashboardData?.trends.conversionTrend}
            xAxis="date"
            yAxis="value"
            height={300}
          />
        </Card>
        
        <Card title="スコア分析">
          <RadarChart
            data={dashboardData?.skillBreakdown}
            height={300}
          />
        </Card>
      </div>

      {/* パフォーマーランキング */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="トップパフォーマー">
          <TopPerformersList performers={dashboardData?.topPerformers} />
        </Card>
        
        <Card title="改善機会">
          <ImprovementOpportunitiesList 
            opportunities={dashboardData?.improvementOpportunities} 
          />
        </Card>
      </div>
    </div>
  );
};
```

#### カウンセラー詳細ダッシュボード
```typescript
// components/dashboard/CounselorDetailDashboard.tsx
export const CounselorDetailDashboard: React.FC<{counselorId: string}> = ({
  counselorId
}) => {
  const { data: counselorData } = useQuery(
    ['counselor-dashboard', counselorId],
    () => api.getCounselorDashboard(counselorId)
  );

  return (
    <div className="space-y-6">
      {/* 統計サマリー */}
      <StatsSummary stats={counselorData?.counselorStats} />

      {/* スキル分析 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="スキルブレークダウン">
          <SkillRadarChart data={counselorData?.skillBreakdown} />
        </Card>
        
        <Card title="最近のパフォーマンス">
          <PerformanceTimeline data={counselorData?.recentPerformance} />
        </Card>
      </div>

      {/* パーソナライズド推奨事項 */}
      <Card title="改善推奨事項">
        <RecommendationsList 
          recommendations={counselorData?.personalizedRecommendations} 
        />
      </Card>
    </div>
  );
};
```

### データ処理・集計機能
```python
# services/analytics_service.py
class AnalyticsService:
    def __init__(self):
        self.db = get_database()
        self.cache = get_redis_client()

    async def get_executive_dashboard(
        self, 
        clinic_id: Optional[str] = None,
        date_range: DateRange = None
    ) -> ExecutiveDashboard:
        """エグゼクティブダッシュボードデータ取得"""
        
        # キャッシュチェック
        cache_key = f"executive_dashboard:{clinic_id}:{date_range.start}:{date_range.end}"
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return ExecutiveDashboard.parse_raw(cached_data)

        # KPI計算
        kpis = await self._calculate_kpis(clinic_id, date_range)
        
        # トレンド分析
        trends = await self._calculate_trends(clinic_id, date_range)
        
        # トップパフォーマー
        top_performers = await self._get_top_performers(clinic_id, date_range)
        
        # 改善機会
        opportunities = await self._identify_opportunities(clinic_id, date_range)
        
        dashboard_data = ExecutiveDashboard(
            kpis=kpis,
            trends=trends,
            top_performers=top_performers,
            improvement_opportunities=opportunities
        )
        
        # キャッシュ保存（1時間）
        await self.cache.setex(cache_key, 3600, dashboard_data.json())
        
        return dashboard_data

    async def _calculate_kpis(
        self, 
        clinic_id: Optional[str], 
        date_range: DateRange
    ) -> KPIMetrics:
        """KPI計算"""
        
        # SQL クエリで集計
        query = """
        SELECT 
            COUNT(*) as total_sessions,
            COUNT(CASE WHEN overall_score >= 8.0 THEN 1 END) as high_score_sessions,
            AVG(overall_score) as average_score,
            SUM(CASE WHEN contracted = true THEN contract_amount ELSE 0 END) as total_revenue
        FROM sessions s
        JOIN analysis_results ar ON s.id = ar.session_id
        WHERE s.session_date BETWEEN %s AND %s
        """
        
        if clinic_id:
            query += " AND s.clinic_id = %s"
            params = [date_range.start, date_range.end, clinic_id]
        else:
            params = [date_range.start, date_range.end]
        
        result = await self.db.fetch_one(query, params)
        
        conversion_rate = (
            result['high_score_sessions'] / result['total_sessions'] 
            if result['total_sessions'] > 0 else 0
        )
        
        return KPIMetrics(
            conversionRate=conversion_rate,
            averageSessionScore=result['average_score'] or 0,
            monthlyRevenue=result['total_revenue'] or 0,
            customerSatisfaction=await self._calculate_satisfaction(clinic_id, date_range)
        )

    async def generate_performance_report(
        self,
        report_type: str,
        filters: ReportFilters,
        format: str = "json"
    ) -> Union[Dict, bytes]:
        """パフォーマンスレポート生成"""
        
        if report_type == "counselor":
            data = await self._generate_counselor_report(filters)
        elif report_type == "clinic":
            data = await self._generate_clinic_report(filters)
        elif report_type == "customer":
            data = await self._generate_customer_report(filters)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
        
        if format == "csv":
            return self._export_to_csv(data)
        elif format == "pdf":
            return await self._export_to_pdf(data)
        else:
            return data
```

### リアルタイム更新機能
```typescript
// hooks/useRealtimeUpdates.ts
export const useRealtimeUpdates = (dashboardType: string) => {
  const [socket, setSocket] = useState<io.Socket>();
  const queryClient = useQueryClient();

  useEffect(() => {
    const socketConnection = io('/dashboard', {
      auth: {
        token: getAuthToken()
      }
    });

    socketConnection.on('dashboard_update', (data: DashboardUpdate) => {
      // 関連するクエリキャッシュを無効化
      queryClient.invalidateQueries([`${dashboardType}-dashboard`]);
      
      // 特定のメトリクスのみ更新
      if (data.metric && data.value) {
        queryClient.setQueryData(
          [`${dashboardType}-dashboard`],
          (oldData: any) => ({
            ...oldData,
            kpis: {
              ...oldData.kpis,
              [data.metric]: data.value
            }
          })
        );
      }
    });

    setSocket(socketConnection);

    return () => {
      socketConnection.disconnect();
    };
  }, [dashboardType, queryClient]);

  return socket;
};
```

### 受け入れ基準
- [x] ダッシュボードが正常に表示される
- [x] 統計データが正確に計算される
- [x] グラフが適切に表示される（Chart.js/D3.js）
- [x] データエクスポートが動作する（CSV, PDF）
- [x] レスポンシブデザインが実装されている
- [x] パフォーマンスが適切（3秒以内で表示）
- [x] リアルタイム更新が動作する
- [x] ユーザー権限による表示制御が動作する

### パフォーマンス要件
- 初期表示時間: 3秒以内
- データ更新時間: 1秒以内
- 同時ユーザー数: 20ユーザー
- レスポンシブ対応: モバイル・タブレット

---

## Phase 3 完了チェックリスト

### AI分析機能
- [x] GPT-4による4項目分析が動作する
- [x] 分析精度が要件を満たす
- [x] 非同期処理が実装されている
- [x] エラーハンドリングが適切

### 改善提案機能
- [x] 改善提案が適切に生成される
- [x] スクリプト最適化が動作する
- [x] 成功パターン学習が実装されている
- [x] フィードバック機能が動作する

### ダッシュボード
- [x] 管理者ダッシュボードが正常表示される
- [x] カウンセラー別統計が表示される
- [x] レポート生成・エクスポートが動作する
- [x] リアルタイム更新が動作する

### 統合テスト
- [x] 文字起こしから分析まで全フローが動作
- [x] 複数セッションの並列分析が可能
- [x] データ整合性が保たれている
- [x] パフォーマンス要件を満たす

## 次のフェーズへの引き継ぎ事項

1. **分析結果データ**
   - 分析結果の形式・構造
   - スコア算出方法
   - 改善提案の分類

2. **学習データ**
   - 成功パターンデータ
   - ベストプラクティス集
   - カスタマイズ設定

3. **パフォーマンス情報**
   - 分析処理時間実績
   - API利用料金実績
   - システム負荷状況

4. **ユーザビリティ**
   - UI/UXテスト結果
   - ユーザーフィードバック
   - 改善要望