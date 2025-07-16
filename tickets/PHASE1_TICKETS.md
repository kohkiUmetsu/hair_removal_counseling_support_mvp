# Phase 1: 基盤構築チケット（4週間）

## 概要
システムの基盤となるインフラストラクチャ、認証システム、データベース、API基盤、フロントエンド基盤を構築するフェーズです。

**期間**: 4週間  
**並列作業**: 可能（依存関係に注意）  
**チーム**: インフラ、バックエンド、フロントエンド  

---

## ✅ Ticket-01: Infrastructure Setup - Terraform for AWS Infrastructure
**優先度**: 🔴 High  
**工数見積**: 5日  
**担当者**: インフラエンジニア  
**依存関係**: なし（最優先で開始）  
**ステータス**: ✅ **完了** - [実装詳細](../docs/ticket-01-implementation.md)

### 概要
Terraformを使用してAWSインフラストラクチャを構築する

### 実装内容
- VPCとサブネット設定
- ECS/Fargateクラスター構築
- RDS PostgreSQL構築
- S3バケット構築（音声ファイル保存用）
- セキュリティグループ設定
- IAMロール・ポリシー設定
- ALB設定

### 技術仕様
- **VPC**: プライベート/パブリックサブネット
- **RDS**: PostgreSQL 14, Multi-AZ構成
- **S3**: 暗号化有効, バージョニング有効
- **ECS**: Fargate, Auto Scaling設定

### ファイル構成
```
infrastructure/
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── ecs/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── rds/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── s3/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       └── terraform.tfvars
└── main.tf
```

### 受け入れ基準
- [x] 開発・ステージング・本番環境が構築されている
- [x] セキュリティグループが適切に設定されている
- [x] S3バケットが暗号化されている
- [x] RDSが適切にバックアップ設定されている
- [x] Terraformコードがモジュール化されている
- [x] terraform plan/applyが正常に動作する
- [x] IAMロールが最小権限の原則に従っている

### セキュリティ要件
- S3バケットのパブリックアクセス無効化
- RDSの暗号化有効
- セキュリティグループの最小権限設定
- IAMロールの最小権限の原則

---

## ✅ Ticket-02: Authentication System - JWT Authentication
**優先度**: 🔴 High  
**工数見積**: 4日  
**担当者**: バックエンドエンジニア  
**依存関係**: Ticket-01（RDS構築後）  
**ステータス**: ✅ **完了** - [実装詳細](../docs/ticket-02-implementation.md)

### 概要
JWT認証とロールベースアクセス制御を実装する

### 実装内容
- JWT認証機能実装
- ユーザーロール管理（counselor, manager, admin）
- ログイン・ログアウト機能
- リフレッシュトークン機能
- 認証ミドルウェア実装
- パスワードハッシュ化（bcrypt）

### API仕様
```yaml
POST /api/auth/login
  Request:
    email: string
    password: string
  Response:
    access_token: string
    refresh_token: string
    user: UserSchema

POST /api/auth/logout
  Headers:
    Authorization: Bearer {token}
  Response:
    message: string

POST /api/auth/refresh
  Request:
    refresh_token: string
  Response:
    access_token: string

GET /api/auth/me
  Headers:
    Authorization: Bearer {token}
  Response:
    user: UserSchema
```

### ファイル構成
```
backend/app/
├── api/auth/
│   ├── __init__.py
│   ├── router.py           # 認証API
│   └── dependencies.py     # 認証依存関数
├── core/
│   ├── auth.py            # JWT設定
│   ├── security.py        # パスワードハッシュ
│   └── config.py          # 設定
├── schemas/
│   ├── auth.py            # 認証スキーマ
│   └── user.py            # ユーザースキーマ
└── services/
    └── auth_service.py     # 認証ビジネスロジック
```

### 受け入れ基準
- [x] JWT認証が正常に動作する
- [x] ロールベースでAPIアクセス制御される
- [x] リフレッシュトークンが実装されている
- [x] パスワードが適切にハッシュ化される
- [x] セキュリティヘッダーが適切に設定されている
- [x] JWT有効期限が適切に設定されている

### セキュリティ要件
- JWT秘密鍵の安全な管理
- パスワード複雑度要件
- CORS設定

---

## ✅ Ticket-03: Database Schema - PostgreSQL Models
**優先度**: 🔴 High  
**工数見積**: 3日  
**担当者**: バックエンドエンジニア  
**依存関係**: Ticket-01（RDS構築後）  
**ステータス**: ✅ **完了** - [実装詳細](../docs/ticket-03-implementation.md)

### 概要
PostgreSQLのデータベーススキーマとSQLAlchemyモデルを作成する

### 実装内容
- Users, Customers, Sessions, Clinicsテーブル設計
- SQLAlchemyモデル作成
- Alembicマイグレーション機能実装
- インデックス設定
- 制約設定

### テーブル仕様
```sql
-- Clinics（クリニック）
CREATE TABLE clinics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users（ユーザー）
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('counselor', 'manager', 'admin')) NOT NULL,
    clinic_id UUID REFERENCES clinics(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers（顧客）
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    clinic_id UUID REFERENCES clinics(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions（セッション）
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    counselor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    audio_file_path VARCHAR(500),
    transcription_text TEXT,
    analysis_result JSONB,
    session_date TIMESTAMP NOT NULL,
    duration_minutes INTEGER,
    status VARCHAR(20) DEFAULT 'recorded' CHECK (status IN ('recorded', 'transcribing', 'analyzing', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス設定
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_clinic_id ON users(clinic_id);
CREATE INDEX idx_customers_clinic_id ON customers(clinic_id);
CREATE INDEX idx_sessions_customer_id ON sessions(customer_id);
CREATE INDEX idx_sessions_counselor_id ON sessions(counselor_id);
CREATE INDEX idx_sessions_session_date ON sessions(session_date);
```

### ファイル構成
```
backend/app/
├── models/
│   ├── __init__.py
│   ├── base.py            # ベースモデル
│   ├── clinic.py          # クリニックモデル
│   ├── user.py            # ユーザーモデル
│   ├── customer.py        # 顧客モデル
│   └── session.py         # セッションモデル
├── core/
│   └── database.py        # DB接続設定
└── alembic/               # マイグレーションファイル
    ├── env.py
    └── versions/
```

### 受け入れ基準
- [x] 全テーブルが正常に作成される
- [x] SQLAlchemyモデルが実装されている
- [x] Alembicマイグレーション機能が動作する
- [x] 外部キー制約が適切に設定されている
- [x] インデックスが適切に設定されている
- [x] UUIDが正常に生成される
- [x] タイムスタンプが自動更新される

### パフォーマンス要件
- 必要なインデックスの設定
- クエリパフォーマンスの最適化
- 適切な外部キー制約

---

## ✅ Ticket-04: Backend API Foundation - FastAPI Setup
**優先度**: 🔴 High  
**工数見積**: 4日  
**担当者**: バックエンドエンジニア  
**依存関係**: Ticket-02, 03（認証・DB完了後）  
**ステータス**: ✅ **完了** - [実装詳細](../docs/ticket-04-implementation.md)

### 概要
FastAPIを使用したバックエンドAPIの基盤を構築する

### 実装内容
- FastAPIプロジェクト構造作成
- MVC アーキテクチャ実装
- API ルーティング設定
- データベース接続設定
- CORS設定
- エラーハンドリング実装
- ログ設定
- ヘルスチェックAPI

### ディレクトリ構造
```
backend/
├── app/
│   ├── api/                 # Controller層
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   └── router.py
│   │   ├── recording/
│   │   │   ├── __init__.py
│   │   │   └── router.py
│   │   ├── transcribe/
│   │   │   ├── __init__.py
│   │   │   └── router.py
│   │   └── analysis/
│   │       ├── __init__.py
│   │       └── router.py
│   ├── core/                # 設定・DB接続
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   └── security.py
│   ├── models/              # SQLAlchemyモデル
│   ├── schemas/             # Pydanticスキーマ
│   ├── services/            # ビジネスロジック
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── transcribe_service.py
│   │   ├── analysis_service.py
│   │   └── storage_service.py
│   ├── utils/               # ユーティリティ
│   │   ├── __init__.py
│   │   └── logger.py
│   └── main.py
├── Dockerfile
└── requirements.txt
```

### API基本仕様
```yaml
GET /health
  Response:
    status: "healthy"
    timestamp: "2023-12-01T10:00:00Z"
    database: "connected"

GET /api/v1/docs
  # Swagger UI

GET /api/v1/redoc
  # ReDoc UI
```

### ミドルウェア設定
```python
# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# セキュリティヘッダー
# ログ設定
# エラーハンドリング
```

### 受け入れ基準
- [x] FastAPIが正常に起動する
- [x] MVC構造が実装されている
- [x] データベース接続が正常に動作する
- [x] CORS設定が適切に動作する
- [x] エラーハンドリングが実装されている
- [x] ヘルスチェックAPIが実装されている
- [x] Swagger UIが正常に表示される
- [x] ログが適切に出力される

### パフォーマンス要件
- レスポンス時間: 500ms以内
- 同時接続数: 50ユーザー対応
- エラーレート: 1%未満

---

## ✅ Ticket-05: Frontend Foundation - Next.js Setup
**優先度**: 🔴 High  
**工数見積**: 4日  
**担当者**: フロントエンドエンジニア  
**依存関係**: Ticket-02（認証API完了後）  
**ステータス**: ✅ **完了** - [実装詳細](../docs/ticket-05-implementation.md)

### 概要
Next.js App Routerを使用したフロントエンド基盤を構築する

### 実装内容
- Next.js App Router設定
- Tailwind CSS設定
- 基本的なレイアウトコンポーネント
- 認証状態管理（Context API）
- APIクライアント設定（axios）
- ルーティング設定
- レスポンシブデザイン基盤

### ディレクトリ構造
```
frontend/
├── app/
│   ├── (auth)/              # 認証ページグループ
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── dashboard/           # ダッシュボード
│   │   ├── page.tsx
│   │   └── layout.tsx
│   ├── recording/           # 録音機能
│   │   ├── page.tsx
│   │   └── [id]/
│   │       └── page.tsx
│   ├── analysis/            # 分析機能
│   │   ├── page.tsx
│   │   └── [id]/
│   │       └── page.tsx
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── components/              # 再利用可能コンポーネント
│   ├── ui/                  # 基本UIコンポーネント
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   └── modal.tsx
│   ├── layout/              # レイアウトコンポーネント
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   └── footer.tsx
│   └── auth/                # 認証関連コンポーネント
│       ├── login-form.tsx
│       └── protected-route.tsx
├── lib/                     # APIクライアント・hooks
│   ├── api.ts               # APIクライアント
│   ├── auth.tsx             # 認証Context
│   └── hooks/
│       ├── use-auth.ts
│       └── use-api.ts
├── styles/                  # スタイル定義
│   └── globals.css
├── utils/                   # ユーティリティ関数
│   ├── auth.ts
│   └── constants.ts
├── types/                   # TypeScript型定義
│   ├── auth.ts
│   └── api.ts
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

### 認証状態管理
```typescript
// lib/auth.tsx
interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);
```

### APIクライアント設定
```typescript
// lib/api.ts
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター（JWT付与）
// レスポンスインターセプター（エラーハンドリング）
```

### レイアウト構成
```typescript
// app/layout.tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <AuthProvider>
          <div className="min-h-screen bg-gray-50">
            <Header />
            <main className="container mx-auto px-4 py-8">
              {children}
            </main>
            <Footer />
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
```

### 受け入れ基準
- [x] Next.js App Routerが正常に動作する
- [x] Tailwind CSSが適用されている
- [x] 基本的なレイアウトが実装されている
- [x] 認証状態管理が実装されている
- [x] APIクライアントが設定されている
- [x] レスポンシブデザインが実装されている
- [x] TypeScriptが適切に設定されている
- [x] ルーティングが正常に動作する

### UI/UX要件
- レスポンシブデザイン（モバイル対応）
- アクセシビリティ対応
- ダークモード対応（オプション）
- ローディング状態表示

---

## Phase 1 完了チェックリスト

### インフラストラクチャ
- [x] AWS環境が3つ（dev/staging/prod）構築されている
- [x] RDS PostgreSQLが正常に動作している
- [x] S3バケットが設定されている
- [x] ECSクラスターが構築されている

### バックエンド
- [x] 認証APIが正常に動作している
- [x] データベーススキーマが作成されている
- [x] FastAPIが正常に起動している
- [x] 基本的なAPI エンドポイントが動作している

### フロントエンド
- [x] Next.jsアプリケーションが起動している
- [x] 認証フローが動作している
- [x] 基本的なレイアウトが実装されている
- [x] APIとの通信が確立されている

### セキュリティ
- [x] JWT認証が実装されている
- [x] HTTPS通信が設定されている
- [x] 適切なCORS設定がされている
- [x] セキュリティヘッダーが設定されている

## 次のフェーズへの引き継ぎ事項

1. **環境情報**
   - AWS環境のエンドポイント情報
   - データベース接続情報
   - S3バケット情報

2. **認証情報**
   - JWT設定情報
   - ユーザーロール定義

3. **API仕様**
   - 作成済みAPIエンドポイント
   - レスポンス形式

4. **フロントエンド**
   - 共通コンポーネント
   - 状態管理方式
   - ルーティング構成