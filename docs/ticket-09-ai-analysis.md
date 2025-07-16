# Ticket-09: AI Analysis Service - GPT-4 Integration

## 概要
OpenAI GPT-4を使用したカウンセリングセッションの包括的AI分析システムを実装しました。

## 実装内容

### 1. データベースモデル (`app/models/analysis.py`)
- **AnalysisTask**: AI分析タスクを管理
- **AnalysisFeedback**: 分析結果に対するフィードバック
- **SuccessPattern**: 成功パターンの蓄積と学習

### 2. 分析スキーマ (`app/schemas/analysis.py`)
包括的な分析結果構造を定義：
- **QuestioningAnalysis**: 質問技法の分析
- **AnxietyHandlingAnalysis**: 不安対応の評価
- **ClosingAnalysis**: クロージング手法の分析
- **FlowAnalysis**: トーク流れの評価
- **AnalysisResult**: 総合分析結果

### 3. プロンプト管理サービス (`app/services/prompt_service.py`)
- Jinja2テンプレートエンジンによる動的プロンプト生成
- カテゴリ別専門プロンプト（質問技法、不安対応、クロージング、フロー）
- カスタムプロンプト対応

### 4. AI分析サービス (`app/services/analysis_service.py`)
- **包括分析**: 全項目の詳細分析
- **クイック分析**: 高速簡易分析
- **特定項目分析**: フォーカス領域限定分析
- **並列処理**: 複数分析の同時実行
- **エラーハンドリング**: 堅牢な例外処理
- **コスト追跡**: OpenAI API使用料金計算

### 5. API エンドポイント (`app/api/ai_analysis.py`)
- `POST /api/v1/ai-analysis/` - AI分析開始
- `GET /api/v1/ai-analysis/status/{task_id}` - 分析状況取得
- `GET /api/v1/ai-analysis/result/{analysis_id}` - 分析結果取得
- `POST /api/v1/ai-analysis/batch` - バッチ分析開始
- `GET /api/v1/ai-analysis/` - 分析タスク一覧
- `GET /api/v1/ai-analysis/stats` - 分析統計情報

### 6. データベース移行 (`alembic/versions/005_add_analysis_tables.py`)
分析関連テーブルの作成：
- analysis_tasks: 分析タスク管理
- analysis_feedback: フィードバック蓄積
- success_patterns: 成功パターン学習

## 主要機能

### 分析タイプ
1. **FULL**: 全項目包括分析（3分程度）
2. **QUICK**: 高速簡易分析（1分程度）
3. **SPECIFIC**: 特定項目フォーカス分析（2分程度）

### 分析項目
1. **質問技法**: オープン・クローズド質問の使い分け、顧客発話促進
2. **不安対応**: 不安要素特定、共感表現、解決策提示
3. **クロージング**: タイミング、緊急性、限定性活用、価格提示
4. **トーク流れ**: 論理構成、転換スムーズさ、顧客ペース配慮

### セキュリティ・権限制御
- 役割別アクセス制御（admin, manager, counselor）
- クリニック間データ分離
- 個人情報自動マスキング

### バックグラウンド処理
- 非同期タスク実行
- 進捗状況リアルタイム更新
- エラー時の自動復旧機能

## 技術仕様

### 使用技術
- **OpenAI GPT-4 Turbo**: 高精度AI分析
- **FastAPI**: 高性能API フレームワーク
- **SQLAlchemy**: ORM データベース操作
- **Jinja2**: テンプレートエンジン
- **PostgreSQL**: JSONB型による構造化データ保存

### パフォーマンス
- 並列分析処理による高速化
- インデックス最適化によるクエリ高速化
- バックグラウンドタスクによる非同期処理

### 開発支援機能
- OpenAI API キー未設定時のダミーレスポンス
- 詳細ログ出力とエラー追跡
- JSON パース自動修復機能

## 設定項目

### 環境変数
```env
OPENAI_API_KEY=sk-...  # OpenAI API キー
OPENAI_MODEL=gpt-4-turbo-preview  # 使用モデル
```

### 設定可能項目
- max_tokens: 最大トークン数（デフォルト: 4000）
- temperature: 創造性レベル（デフォルト: 0.1）
- 料金レート: トークンあたりコスト

## API使用例

### 分析開始
```python
POST /api/v1/ai-analysis/
{
  "transcription_id": "uuid",
  "analysis_type": "FULL",
  "focus_areas": ["questioning", "closing"],
  "custom_prompts": {
    "questioning": "カスタムプロンプト..."
  }
}
```

### 分析状況確認
```python
GET /api/v1/ai-analysis/status/task-uuid
```

### 分析結果取得
```python
GET /api/v1/ai-analysis/result/analysis-uuid
```

## 今後の拡張予定
1. **学習機能**: 成功パターンからの自動プロンプト最適化
2. **カスタム評価基準**: クリニック別評価指標
3. **リアルタイム分析**: ライブセッション中の即時フィードバック
4. **多言語対応**: 国際展開向け多言語分析

## 完了
✅ GPT-4統合AI分析サービスの実装完了