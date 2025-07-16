# 美容医療脱毛クリニック カウンセリング分析システム 開発チケット

## 📋 フェーズ別チケット一覧

このドキュメントは各フェーズの開発チケットの概要を提供します。  
詳細な実装仕様については、各フェーズ別ドキュメントを参照してください。

### 📁 フェーズ別詳細ドキュメント

- **[Phase 1: 基盤構築](./tickets/PHASE1_TICKETS.md)** - インフラ、認証、DB、API基盤（4週間）
- **[Phase 2: 録音・文字起こし機能](./tickets/PHASE2_TICKETS.md)** - 録音、ファイル保存、文字起こし（3週間）
- **[Phase 3: AI分析機能](./tickets/PHASE3_TICKETS.md)** - GPT-4分析、改善提案、ダッシュボード（4週間）
- **[Phase 4: ドキュメント整備](./tickets/PHASE4_TICKETS.md)** - API仕様書、ユーザーマニュアル、運用ガイド（1週間）

---

## 🗂️ チケット概要

### Phase 1: 基盤構築（4週間）

#### Ticket-01: Infrastructure Setup - Terraform for AWS Infrastructure
**優先度**: 🔴 High  
**工数見積**: 5日  
**担当者**: インフラエンジニア  

#### 概要
Terraformを使用してAWSインフラストラクチャを構築する

#### 実装内容
- VPCとサブネット設定
- ECS/Fargateクラスター構築
- RDS PostgreSQL構築
- S3バケット構築（音声ファイル保存用）
- セキュリティグループ設定
- IAMロール・ポリシー設定
- ALB設定

#### 技術仕様
- **VPC**: プライベート/パブリックサブネット
- **RDS**: PostgreSQL 14, Multi-AZ構成
- **S3**: 暗号化有効, バージョニング有効
- **ECS**: Fargate, Auto Scaling設定

#### 受け入れ基準
- [ ] 開発・ステージング・本番環境が構築されている
- [ ] セキュリティグループが適切に設定されている
- [ ] S3バケットが暗号化されている
- [ ] RDSが適切にバックアップ設定されている
- [ ] Terraformコードがモジュール化されている

#### ファイル構成
```
infrastructure/
├── modules/
│   ├── vpc/
│   ├── ecs/
│   ├── rds/
│   └── s3/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
└── main.tf
```

---

### Ticket-02: Authentication System - JWT Authentication
**優先度**: 🔴 High  
**工数見積**: 4日  
**担当者**: バックエンドエンジニア  

#### 概要
JWT認証とロールベースアクセス制御を実装する

#### 実装内容
- JWT認証機能実装
- ユーザーロール管理（counselor, manager, admin）
- ログイン・ログアウト機能
- リフレッシュトークン機能
- 認証ミドルウェア実装

#### API仕様
```
POST /api/auth/login          # ログイン
POST /api/auth/logout         # ログアウト
POST /api/auth/refresh        # トークンリフレッシュ
GET  /api/auth/me             # ユーザー情報取得
```

#### 受け入れ基準
- [ ] JWT認証が正常に動作する
- [ ] ロールベースでAPIアクセス制御される
- [ ] リフレッシュトークンが実装されている
- [ ] セキュリティヘッダーが適切に設定されている
- [ ] 単体テストが作成されている

---

### Ticket-03: Database Schema - PostgreSQL Models
**優先度**: 🔴 High  
**工数見積**: 3日  
**担当者**: バックエンドエンジニア  

#### 概要
PostgreSQLのデータベーススキーマとSQLAlchemyモデルを作成する

#### 実装内容
- Users, Customers, Sessions, Clinicsテーブル設計
- SQLAlchemyモデル作成
- マイグレーション機能実装
- インデックス設定
- 制約設定

#### テーブル仕様
```sql
-- Users（ユーザー）
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('counselor', 'manager', 'admin')),
    clinic_id UUID REFERENCES clinics(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers（顧客）
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    clinic_id UUID REFERENCES clinics(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions（セッション）
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id),
    counselor_id UUID REFERENCES users(id),
    audio_file_path VARCHAR(500),
    transcription_text TEXT,
    analysis_result JSONB,
    session_date TIMESTAMP NOT NULL,
    duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clinics（クリニック）
CREATE TABLE clinics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 受け入れ基準
- [ ] 全テーブルが正常に作成される
- [ ] SQLAlchemyモデルが実装されている
- [ ] マイグレーション機能が動作する
- [ ] 外部キー制約が適切に設定されている
- [ ] インデックスが適切に設定されている

---

### Ticket-04: Backend API Foundation - FastAPI Setup
**優先度**: 🔴 High  
**工数見積**: 4日  
**担当者**: バックエンドエンジニア  

#### 概要
FastAPIを使用したバックエンドAPIの基盤を構築する

#### 実装内容
- FastAPIプロジェクト構造作成
- MVC アーキテクチャ実装
- API ルーティング設定
- データベース接続設定
- CORS設定
- エラーハンドリング実装
- ログ設定

#### ディレクトリ構造
```
backend/
├── app/
│   ├── api/                 # Controller層
│   │   ├── auth/
│   │   ├── recording/
│   │   ├── transcribe/
│   │   └── analysis/
│   ├── core/                # 設定・DB接続
│   ├── models/              # SQLAlchemyモデル
│   ├── schemas/             # Pydanticスキーマ
│   ├── services/            # ビジネスロジック
│   ├── utils/               # ユーティリティ
│   └── main.py
├── Dockerfile
└── requirements.txt
```

#### 受け入れ基準
- [ ] FastAPIが正常に起動する
- [ ] MVC構造が実装されている
- [ ] データベース接続が正常に動作する
- [ ] CORS設定が適切に動作する
- [ ] エラーハンドリングが実装されている
- [ ] ヘルスチェックAPIが実装されている

---

### Ticket-05: Frontend Foundation - Next.js Setup
**優先度**: 🔴 High  
**工数見積**: 4日  
**担当者**: フロントエンドエンジニア  

#### 概要
Next.js App Routerを使用したフロントエンド基盤を構築する

#### 実装内容
- Next.js App Router設定
- Tailwind CSS設定
- 基本的なレイアウトコンポーネント
- 認証状態管理
- APIクライアント設定
- ルーティング設定

#### ディレクトリ構造
```
frontend/
├── app/
│   ├── (auth)/              # 認証ページグループ
│   ├── dashboard/           # ダッシュボード
│   ├── recording/           # 録音機能
│   ├── analysis/            # 分析機能
│   ├── layout.tsx
│   └── page.tsx
├── components/              # 再利用可能コンポーネント
├── lib/                     # APIクライアント・hooks
├── styles/                  # スタイル定義
└── utils/                   # ユーティリティ関数
```

#### 受け入れ基準
- [ ] Next.js App Routerが正常に動作する
- [ ] Tailwind CSSが適用されている
- [ ] 基本的なレイアウトが実装されている
- [ ] 認証状態管理が実装されている
- [ ] APIクライアントが設定されている
- [ ] レスポンシブデザインが実装されている

---

## Phase 2: 録音・文字起こし機能（3週間）

### Ticket-06: Audio Recording - MediaRecorder API Implementation
**優先度**: 🟡 Medium  
**工数見積**: 5日  
**担当者**: フロントエンドエンジニア  

#### 概要
ブラウザベースの音声録音機能を実装する

#### 実装内容
- MediaRecorder API実装
- 録音開始・停止・一時停止機能
- 録音状況表示
- 音声波形表示
- 録音ファイルプレビュー機能

#### 技術仕様
- **録音形式**: WebM（Chrome/Firefox）、MP4（Safari）
- **音質**: 44.1kHz, 16bit
- **最大録音時間**: 60分
- **リアルタイム音声レベル表示**

#### 受け入れ基準
- [ ] 録音開始・停止が正常に動作する
- [ ] 録音時間が表示される
- [ ] 音声レベルがリアルタイムで表示される
- [ ] 録音ファイルが正常に生成される
- [ ] ブラウザ間での互換性が確保されている
- [ ] エラーハンドリングが実装されている

---

### Ticket-07: File Storage - S3 Integration
**優先度**: 🟡 Medium  
**工数見積**: 4日  
**担当者**: バックエンドエンジニア  

#### 概要
S3への暗号化音声ファイル保存機能を実装する

#### 実装内容
- S3 SDK設定
- ファイルアップロード機能
- プリサインドURL生成
- ファイル暗号化設定
- ファイル名自動生成機能

#### API仕様
```
POST /api/recordings          # 録音ファイルアップロード
GET  /api/recordings/{id}     # 録音ファイル取得
DELETE /api/recordings/{id}   # 録音ファイル削除
```

#### ファイル命名規則
```
{clinic_id}/{customer_id}/{session_date}/{session_id}.webm
例: clinic-123/customer-456/20231201/session-789.webm
```

#### 受け入れ基準
- [ ] S3へのファイルアップロードが動作する
- [ ] ファイルが暗号化されて保存される
- [ ] プリサインドURLが正常に生成される
- [ ] ファイル名が規則に従って生成される
- [ ] ファイルサイズ制限が実装されている
- [ ] エラーハンドリングが実装されている

---

### Ticket-08: Transcription Service - OpenAI Whisper Integration
**優先度**: 🟡 Medium  
**工数見積**: 4日  
**担当者**: バックエンドエンジニア  

#### 概要
OpenAI Whisper APIを使用した音声文字起こし機能を実装する

#### 実装内容
- OpenAI Whisper API連携
- 非同期処理実装
- 処理状況管理
- 日本語音声最適化
- 文字起こし結果保存

#### API仕様
```
POST /api/transcribe          # 文字起こし実行
GET  /api/transcribe/{id}     # 文字起こし結果取得
GET  /api/transcribe/status/{id} # 処理状況取得
```

#### 処理フロー
1. 音声ファイルS3から取得
2. Whisper APIに送信
3. 文字起こし結果を取得
4. データベースに保存
5. フロントエンドに通知

#### 受け入れ基準
- [ ] Whisper APIが正常に動作する
- [ ] 非同期処理が実装されている
- [ ] 処理状況がリアルタイムで取得できる
- [ ] 日本語の文字起こし精度が適切
- [ ] エラーハンドリングが実装されている
- [ ] 処理時間制限が設定されている

---

## Phase 3: 分析機能（4週間）

### Ticket-09: AI Analysis Service - GPT-4 Integration
**優先度**: 🟡 Medium  
**工数見積**: 6日  
**担当者**: バックエンドエンジニア  

#### 概要
GPT-4を使用したカウンセリング分析機能を実装する

#### 実装内容
- OpenAI GPT-4 API連携
- カウンセリング分析ロジック
- 分析結果構造化
- プロンプトテンプレート管理
- 分析結果保存

#### 分析項目
- 質問の誘導性分析
- 顧客不安への対応度評価
- クロージング手法の評価
- トーク流れの分析
- 改善点の特定

#### API仕様
```
POST /api/analysis            # カウンセリング分析実行
GET  /api/analysis/{id}       # 分析結果取得
GET  /api/analysis/history/{session_id} # 分析履歴取得
```

#### 受け入れ基準
- [ ] GPT-4 APIが正常に動作する
- [ ] 分析結果が構造化されて保存される
- [ ] プロンプトテンプレートが管理されている
- [ ] 分析精度が適切なレベル
- [ ] API利用料金が予算内
- [ ] エラーハンドリングが実装されている

---

### Ticket-10: Analysis Features - Improvement Suggestions
**優先度**: 🟡 Medium  
**工数見積**: 5日  
**担当者**: バックエンドエンジニア + フロントエンドエンジニア  

#### 概要
分析結果に基づく改善提案機能を実装する

#### 実装内容
- 改善提案生成ロジック
- スクリプト最適化機能
- 成功パターン学習機能
- 改善提案表示UI
- レポート生成機能

#### 機能詳細
- より良いクロージング案の提示
- 不安解消のためのトーク例
- 次回セッションでの注意点
- 成功事例との比較
- スコア化とランキング

#### 受け入れ基準
- [ ] 改善提案が適切に生成される
- [ ] スクリプト最適化が動作する
- [ ] 成功パターンが学習される
- [ ] UIが使いやすい
- [ ] レポートが正常に生成される
- [ ] データの信頼性が確保されている

---

### Ticket-11: Dashboard & Reports - Analytics Dashboard
**優先度**: 🟢 Low  
**工数見積**: 6日  
**担当者**: フロントエンドエンジニア  

#### 概要
管理者向けの分析ダッシュボードを実装する

#### 実装内容
- 成約率ダッシュボード
- カウンセラー別統計
- 顧客分析レポート
- トレンド分析機能
- データエクスポート機能

#### ダッシュボード項目
- 日別・月別成約率
- カウンセラー別パフォーマンス
- 顧客満足度スコア
- 改善点ランキング
- 売上予測

#### 受け入れ基準
- [ ] ダッシュボードが正常に表示される
- [ ] 統計データが正確に計算される
- [ ] グラフが適切に表示される
- [ ] データエクスポートが動作する
- [ ] レスポンシブデザインが実装されている
- [ ] パフォーマンスが適切

---

## Phase 4: テスト・デプロイ（2週間）

### Ticket-12: Testing - Comprehensive Test Suite
**優先度**: 🟡 Medium  
**工数見積**: 5日  
**担当者**: 全エンジニア  

#### 概要
包括的なテストスイートを実装する

#### 実装内容
- 単体テスト（Backend: pytest, Frontend: Jest）
- 結合テスト
- E2Eテスト（Playwright）
- パフォーマンステスト
- セキュリティテスト

#### テストカバレッジ目標
- バックエンド: 90%以上
- フロントエンド: 80%以上
- API: 100%（重要なエンドポイント）

#### 受け入れ基準
- [ ] 単体テストが実装されている
- [ ] 結合テストが実装されている
- [ ] E2Eテストが実装されている
- [ ] パフォーマンステストが実施される
- [ ] セキュリティテストが実施される
- [ ] テストカバレッジが目標を達成

---

### Ticket-13: CI/CD Pipeline - GitHub Actions
**優先度**: 🟢 Low  
**工数見積**: 3日  
**担当者**: DevOpsエンジニア  

#### 概要
GitHub Actionsを使用したCI/CDパイプラインを構築する

#### 実装内容
- テスト自動実行
- ビルド自動化
- デプロイ自動化
- セキュリティスキャン
- 品質チェック

#### パイプライン段階
1. コード品質チェック
2. テスト実行
3. セキュリティスキャン
4. ビルド
5. デプロイ（ステージング → 本番）

#### 受け入れ基準
- [ ] CI/CDパイプラインが動作する
- [ ] テストが自動実行される
- [ ] デプロイが自動化されている
- [ ] セキュリティスキャンが実行される
- [ ] 品質ゲートが設定されている
- [ ] ロールバック機能が実装されている

---

### Ticket-14: Documentation - API & User Guides
**優先度**: 🟢 Low  
**工数見積**: 3日  
**担当者**: 全エンジニア  

#### 概要
API仕様書とユーザーガイドを作成する

#### 実装内容
- API仕様書（OpenAPI/Swagger）
- ユーザーマニュアル
- 運用ガイド
- 開発者向けドキュメント
- セットアップ手順書

#### ドキュメント構成
- README.md
- API_REFERENCE.md
- USER_MANUAL.md
- DEPLOYMENT_GUIDE.md
- TROUBLESHOOTING.md

#### 受け入れ基準
- [ ] API仕様書が完成している
- [ ] ユーザーマニュアルが作成されている
- [ ] 運用ガイドが作成されている
- [ ] セットアップ手順が明確
- [ ] ドキュメントが最新状態
- [ ] 多言語対応（日英）

---

## 開発スケジュール

| Phase | 期間 | 並行作業可能なチケット |
|-------|------|----------------------|
| Phase 1 | 4週間 | Ticket-01, 02, 03, 04, 05 |
| Phase 2 | 3週間 | Ticket-06, 07, 08 |
| Phase 3 | 4週間 | Ticket-09, 10, 11 |
| Phase 4 | 1週間 | Ticket-14 |

## 依存関係

- Ticket-02, 03, 04, 05 → Ticket-01 (インフラ構築後)
- Ticket-07 → Ticket-01 (S3設定後)
- Ticket-08 → Ticket-06, 07 (録音・保存機能後)
- Ticket-09, 10 → Ticket-08 (文字起こし機能後)
- Ticket-11 → Ticket-09, 10 (分析機能後)
- Ticket-14 → Phase 1-3 完了後

## リスク管理

### 高リスク項目
- OpenAI API制限・コスト
- 音声品質による文字起こし精度
- レスポンス時間要件

### 対策
- API使用量監視システム
- ノイズキャンセリング機能
- 非同期処理とキューイング

## 成功指標

- 各フェーズの予定通り完了
- テストカバレッジ目標達成
- パフォーマンス要件達成
- セキュリティ要件準拠