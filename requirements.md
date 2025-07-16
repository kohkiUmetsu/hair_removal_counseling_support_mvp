# 美容医療脱毛クリニック カウンセリング分析システム 要件定義書

## 1. プロジェクト概要

### 1.1 プロジェクトの目的
美容医療脱毛クリニックにおいて「安価なプランで集客 → 来店時に高額プランを提案」というビジネスモデルの中で、カウンセリング担当者の成約率向上とスクリプトの標準化を実現するシステムを構築する。

### 1.2 背景・課題
- カウンセラーの成約率にばらつきがある
- カウンセリング品質の標準化ができていない
- 効果的なトークスクリプトが体系化されていない
- カウンセリング内容の客観的分析ができていない

### 1.3 期待される効果
- カウンセラーの成約率向上
- カウンセリング品質の標準化
- データに基づく継続的な改善
- 新人カウンセラーの早期戦力化

## 2. 対象ユーザー

### 2.1 プライマリユーザー
- **美容医療脱毛クリニックのカウンセラー**
  - 日常のカウンセリング業務を行う担当者
  - 成約率向上を目指す

### 2.2 セカンダリユーザー
- **店舗管理者・経営者**
  - 店舗全体の売上・成約率管理
  - カウンセラーの人事評価

- **カウンセリング品質管理者**
  - カウンセリング内容の品質管理
  - スクリプト改善・標準化

## 3. 機能要件（MVP）

### 3.1 音声録音・管理機能

#### 3.1.1 録音機能
- **ブラウザベースの音声録音**
  - MediaRecorder APIを使用
  - 録音開始・停止・一時停止機能
  - 録音状況表示

#### 3.1.2 音声ファイル管理
- **顧客別録音管理**
  - 顧客IDに紐づいた録音ファイル保存
  - セッション日時・担当者情報の記録
  - ファイル名の自動生成（顧客ID_日時_担当者）

#### 3.1.3 ストレージ管理
- **AWS S3での音声ファイル保存**
  - セキュアなファイルアップロード
  - ファイル暗号化
  - アクセス権限管理

### 3.2 文字起こし機能

#### 3.2.1 自動文字起こし
- **OpenAI Whisper API連携**
  - 音声ファイルアップロード後の自動実行
  - 日本語音声の高精度文字起こし
  - 処理状況のリアルタイム表示

#### 3.2.2 文字起こし結果管理
- **テキストデータの保存・表示**
  - セッション毎のテキスト保存
  - 検索・絞り込み機能
  - エクスポート機能（PDF、CSV）

### 3.3 カウンセリング分析機能

#### 3.3.1 AI分析
- **OpenAI GPT-4を活用した分析**
  - 質問の誘導性分析
  - 顧客不安への対応度評価
  - クロージング手法の評価
  - トーク流れの分析

#### 3.3.2 改善提案
- **具体的な改善アドバイス**
  - より良いクロージング案の提示
  - 不安解消のためのトーク例
  - 次回セッションでの注意点

#### 3.3.3 スクリプト最適化
- **動的スクリプト表示**
  - 分析結果に基づく最適化されたスクリプト
  - シチュエーション別トーク例
  - 成功パターンの蓄積・共有

## 4. 非機能要件

### 4.1 性能要件
- **レスポンス時間**
  - 画面遷移: 3秒以内
  - 文字起こし: 音声1分あたり30秒以内
  - AI分析: 3分以内

- **同時接続数**
  - 50ユーザーの同時利用をサポート

### 4.2 セキュリティ要件
- **データ保護**
  - 音声ファイルの暗号化保存
  - 個人情報の適切な匿名化

- **認証・認可**
  - JWT認証による安全なログイン
  - ロールベースアクセス制御
  - セッション管理

### 4.3 可用性要件
- **稼働率**: 99.5%以上
- **メンテナンス時間**: 月1回、2時間以内

### 4.4 拡張性要件
- **ユーザー数**: 最大500ユーザーまで対応可能
- **データ容量**: 10TB以上の音声データ保存

## 5. 技術要件

### 5.1 システムアーキテクチャ
```
フロントエンド: Next.js + Tailwind CSS
バックエンド: FastAPI (Python)
データベース: Amazon RDS (PostgreSQL)
ストレージ: Amazon S3
インフラ: AWS ECS/Fargate + Docker
```

### 5.2 外部API
- **OpenAI Whisper API**: 音声文字起こし
- **OpenAI GPT-4 API**: カウンセリング分析
- **AWS SDK**: クラウドサービス連携

### 5.3 開発・デプロイ環境
- **バージョン管理**: Git
- **CI/CD**: GitHub Actions
- **コンテナ**: Docker
- **IaC**: Terraform

## 6. プロジェクト構成

### 6.1 ディレクトリ構造
```
/your-project-root
├── frontend/                 # Next.js App router (音声録音・UI)
│   ├── public/
│   ├── app/
│   │   ├── pages/           # ページコンポーネント
│   │   ├── components/      # 再利用可能コンポーネント
│   │   ├── lib/            # APIクライアント・hooks
│   │   ├── styles/         # スタイル定義
│   │   └── utils/          # ユーティリティ関数
│   ├── next.config.js
│   ├── Dockerfile
│   └── .env.local
│
├── backend/                 # FastAPI (MVC構成)
│   ├── app/
│   │   ├── api/            # ルーティング (Controller)
│   │   │   ├── auth/       # 認証関連API
│   │   │   ├── recording/  # 録音関連API
│   │   │   ├── transcribe/ # 文字起こしAPI
│   │   │   └── analysis/   # 分析API
│   │   ├── core/           # DB接続, JWT, 設定
│   │   ├── models/         # SQLAlchemyモデル (Model)
│   │   ├── schemas/        # Pydanticスキーマ (DTO)
│   │   ├── services/       # ビジネスロジック (Service)
│   │   │   ├── auth_service.py
│   │   │   ├── transcribe_service.py
│   │   │   ├── analysis_service.py
│   │   │   └── storage_service.py
│   │   ├── utils/          # 共通ユーティリティ
│   │   └── main.py         # アプリエントリポイント
│   ├── Dockerfile
│   └── requirements.txt
│
├── infrastructure/          # IaC (Terraform)
│   ├── modules/
│   │   ├── ecs/           # ECSクラスター設定
│   │   ├── rds/           # データベース設定
│   │   ├── s3/            # ストレージ設定
│   │   └── vpc/           # ネットワーク設定
│   ├── environments/
│   │   ├── dev/           # 開発環境
│   │   ├── staging/       # ステージング環境
│   │   └── prod/          # 本番環境
│   └── main.tf
│
├── docker-compose.yml       # ローカル開発用
├── .env                     # 共通環境変数
├── .gitignore
└── README.md
```

### 6.2 MVCアーキテクチャ詳細

#### Controller層 (api/)
- HTTPリクエストの受信・レスポンス返却
- バリデーション
- 認証・認可の確認

#### Service層 (services/)
- ビジネスロジックの実装
- 外部API呼び出し
- トランザクション管理

#### Model層 (models/)
- データベーススキーマ定義
- データアクセスロジック

## 7. データモデル

### 7.1 主要エンティティ

#### Users（ユーザー）
```sql
- id: UUID (PK)
- email: VARCHAR(255) UNIQUE
- name: VARCHAR(100)
- role: ENUM('counselor', 'manager', 'admin')
- clinic_id: UUID (FK)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### Customers（顧客）
```sql
- id: UUID (PK)
- name: VARCHAR(100)
- phone: VARCHAR(20)
- email: VARCHAR(255)
- clinic_id: UUID (FK)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### Sessions（セッション）
```sql
- id: UUID (PK)
- customer_id: UUID (FK)
- counselor_id: UUID (FK)
- audio_file_path: VARCHAR(500)
- transcription_text: TEXT
- analysis_result: JSONB
- session_date: TIMESTAMP
- duration_minutes: INTEGER
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### Clinics（クリニック）
```sql
- id: UUID (PK)
- name: VARCHAR(200)
- address: TEXT
- phone: VARCHAR(20)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

## 8. API設計

### 8.1 認証関連API
```
POST /api/auth/login          # ログイン
POST /api/auth/logout         # ログアウト
GET  /api/auth/me             # ユーザー情報取得
```

### 8.2 録音関連API
```
POST /api/recordings          # 録音開始
PUT  /api/recordings/{id}     # 録音更新
GET  /api/recordings/{id}     # 録音取得
DELETE /api/recordings/{id}   # 録音削除
```

### 8.3 文字起こし関連API
```
POST /api/transcribe          # 文字起こし実行
GET  /api/transcribe/{id}     # 文字起こし結果取得
GET  /api/transcribe/status/{id} # 処理状況取得
```

### 8.4 分析関連API
```
POST /api/analysis            # カウンセリング分析実行
GET  /api/analysis/{id}       # 分析結果取得
GET  /api/analysis/suggestions # 改善提案取得
```

## 9. セキュリティ設計

### 9.1 認証・認可
- **JWT認証**: ステートレスな認証方式
- **ロールベースアクセス制御**: counselor, manager, admin
- **セッション管理**: リフレッシュトークンによる安全な認証継続

### 9.2 データ保護
- **音声ファイル暗号化**: S3での保存時暗号化
- **個人情報の匿名化**: 分析時の自動匿名化処理
- **通信暗号化**: HTTPS/TLS 1.3

## 11. 開発スケジュール（想定）

### Phase 1: 基盤構築（4週間）
- インフラ構築（Terraform）
- 認証システム構築
- 基本的なUI/UX構築

### Phase 2: 録音・文字起こし機能（3週間）
- 音声録音機能実装
- S3連携実装
- Whisper API連携実装

### Phase 3: 分析機能（4週間）
- GPT-4 API連携実装
- 分析ロジック実装
- 改善提案機能実装

### Phase 4: テスト・デプロイ（2週間）
- 結合テスト
- パフォーマンステスト
- 本番デプロイ

## 12. リスク・課題

### 12.1 技術的リスク
- **OpenAI API制限**: レート制限・コスト管理
- **音声品質**: ノイズが多い環境での文字起こし精度
- **レスポンス時間**: 大容量音声ファイルの処理時間

### 12.2 運用リスク
- **個人情報保護**: 音声データの適切な管理
- **ユーザー受容性**: カウンセラーの新システム受容
- **コスト管理**: OpenAI API利用料金の予算管理

### 12.3 対策
- **API制限対策**: キューイングシステムの導入
- **音声品質向上**: ノイズキャンセリング機能
- **段階的導入**: パイロット店舗での検証後展開