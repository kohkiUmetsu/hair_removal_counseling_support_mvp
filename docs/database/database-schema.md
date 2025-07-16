# Database Schema Documentation

## 概要
美容医療脱毛クリニック カウンセリング分析システムのデータベース設計について説明します。PostgreSQLを使用し、SQLAlchemyとAlembicでORM・マイグレーション管理を行います。

## データベース構成

### エンティティ関係図
```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Clinics   │───────│    Users    │       │  Customers  │
│             │       │             │       │             │
│ - id (PK)   │       │ - id (PK)   │       │ - id (PK)   │
│ - name      │       │ - email     │       │ - name      │
│ - address   │       │ - password  │       │ - phone     │
│ - phone     │       │ - name      │       │ - email     │
│             │       │ - role      │       │ - clinic_id │
└─────────────┘       │ - clinic_id │       └─────────────┘
                      │ - is_active │              │
                      └─────────────┘              │
                             │                     │
                             └──────┐    ┌─────────┘
                                    │    │
                                ┌─────────────┐
                                │  Sessions   │
                                │             │
                                │ - id (PK)   │
                                │ - customer  │
                                │ - counselor │
                                │ - date      │
                                │ - duration  │
                                │ - status    │
                                │ - audio     │
                                │ - transcript│
                                │ - analysis  │
                                └─────────────┘
```

## テーブル定義

### 1. Clinics（クリニック）
クリニックの基本情報を管理

```sql
CREATE TABLE clinics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_clinics_name ON clinics(name);
```

**フィールド説明:**
- `id`: 主キー（UUID）
- `name`: クリニック名（必須）
- `address`: 住所
- `phone`: 電話番号
- `created_at/updated_at`: 作成・更新日時

### 2. Users（ユーザー）
システムユーザー（カウンセラー、マネージャー、管理者）

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('counselor', 'manager', 'admin')),
    clinic_id UUID REFERENCES clinics(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_clinic_id ON users(clinic_id);
CREATE INDEX idx_users_role ON users(role);
```

**フィールド説明:**
- `id`: 主キー（UUID）
- `email`: メールアドレス（ユニーク、ログイン用）
- `password_hash`: ハッシュ化されたパスワード
- `name`: ユーザー名
- `role`: ユーザーロール（counselor/manager/admin）
- `clinic_id`: 所属クリニック（外部キー）
- `is_active`: アクティブフラグ

**ロール定義:**
- `counselor`: カウンセラー（自分のデータのみアクセス）
- `manager`: マネージャー（クリニック内データアクセス）
- `admin`: 管理者（全データアクセス）

### 3. Customers（顧客）
カウンセリング対象の顧客情報

```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_clinic_id ON customers(clinic_id);
CREATE INDEX idx_customers_name ON customers(name);
```

**フィールド説明:**
- `id`: 主キー（UUID）
- `name`: 顧客名（必須）
- `phone`: 電話番号
- `email`: メールアドレス
- `clinic_id`: 所属クリニック（外部キー、必須）

### 4. Sessions（セッション）
カウンセリングセッションの記録

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    counselor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_date TIMESTAMP NOT NULL,
    duration_minutes INTEGER,
    status VARCHAR(20) DEFAULT 'recorded' CHECK (
        status IN ('recorded', 'transcribing', 'transcribed', 'analyzing', 'analyzed', 'completed', 'failed')
    ),
    audio_file_path VARCHAR(500),
    transcription_text TEXT,
    analysis_result JSONB,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_customer_id ON sessions(customer_id);
CREATE INDEX idx_sessions_counselor_id ON sessions(counselor_id);
CREATE INDEX idx_sessions_session_date ON sessions(session_date);
CREATE INDEX idx_sessions_status ON sessions(status);
```

**フィールド説明:**
- `id`: 主キー（UUID）
- `customer_id`: 顧客ID（外部キー、必須）
- `counselor_id`: 担当カウンセラーID（外部キー）
- `session_date`: セッション実施日時
- `duration_minutes`: セッション時間（分）
- `status`: 処理ステータス
- `audio_file_path`: 音声ファイルのS3パス
- `transcription_text`: 文字起こし結果
- `analysis_result`: AI分析結果（JSON）
- `notes`: メモ・備考

**ステータス遷移:**
```
recorded → transcribing → transcribed → analyzing → analyzed → completed
    ↓           ↓            ↓            ↓          ↓
  failed ←─── failed ←─── failed ←─── failed ←─── failed
```

## SQLAlchemy モデル実装

### ベースモデル
```python
class BaseModel(Base):
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

### リレーションシップ定義
```python
# Clinic → Users (1:N)
users = relationship("User", back_populates="clinic", cascade="all, delete-orphan")

# Clinic → Customers (1:N)
customers = relationship("Customer", back_populates="clinic", cascade="all, delete-orphan")

# User → Sessions (1:N)
sessions = relationship("Session", back_populates="counselor", cascade="all, delete-orphan")

# Customer → Sessions (1:N)
sessions = relationship("Session", back_populates="customer", cascade="all, delete-orphan")
```

## データベース初期化

### マイグレーション作成
```bash
# 初回マイグレーション作成
alembic revision --autogenerate -m "Initial migration"

# マイグレーション適用
alembic upgrade head

# 特定バージョンへのダウングレード
alembic downgrade base
```

### 初期データ投入
```bash
# 開発用データ投入
python scripts/seed_data.py
```

**投入されるデータ:**
- クリニック2件（東京・大阪）
- ユーザー6名（管理者1名、マネージャー2名、カウンセラー3名）
- 顧客5名
- セッション20件（分析結果含む）

## パフォーマンス最適化

### インデックス戦略
```sql
-- 頻繁に検索されるフィールドにインデックス
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_sessions_session_date ON sessions(session_date);
CREATE INDEX idx_sessions_status ON sessions(status);

-- 複合インデックス
CREATE INDEX idx_sessions_customer_counselor ON sessions(customer_id, counselor_id);
CREATE INDEX idx_sessions_date_status ON sessions(session_date, status);
```

### クエリ最適化
```python
# N+1問題を避けるため、JOINを使用
sessions = db.query(Session).options(
    joinedload(Session.customer),
    joinedload(Session.counselor)
).filter(Session.status == SessionStatus.COMPLETED).all()

# ページネーション
sessions = db.query(Session).offset(skip).limit(limit).all()
```

## セキュリティ考慮事項

### データ保護
- **パスワード**: bcryptでハッシュ化
- **個人情報**: 必要最小限の保存
- **音声データ**: S3で暗号化保存
- **分析結果**: 匿名化処理

### アクセス制御
```python
# クリニックレベルでのデータ分離
def get_user_sessions(user: User, db: Session):
    query = db.query(Session)
    
    if user.role == UserRole.COUNSELOR:
        # 自分のセッションのみ
        query = query.filter(Session.counselor_id == user.id)
    elif user.role == UserRole.MANAGER:
        # 同じクリニックのセッションのみ
        query = query.join(Customer).filter(Customer.clinic_id == user.clinic_id)
    # ADMIN は全データアクセス可能
    
    return query.all()
```

### データ整合性
```sql
-- 外部キー制約
FOREIGN KEY (clinic_id) REFERENCES clinics(id) ON DELETE CASCADE
FOREIGN KEY (counselor_id) REFERENCES users(id) ON DELETE SET NULL

-- チェック制約
CHECK (role IN ('counselor', 'manager', 'admin'))
CHECK (status IN ('recorded', 'transcribing', 'transcribed', 'analyzing', 'analyzed', 'completed', 'failed'))
```

## バックアップ・復旧

### 定期バックアップ
```bash
# 日次バックアップ
pg_dump -h $DB_HOST -U $DB_USER -d counseling_db | gzip > backup_$(date +%Y%m%d).sql.gz

# AWS RDS自動バックアップ（7日間保持）
```

### 災害復旧
```bash
# バックアップからの復旧
gunzip -c backup_20231201.sql.gz | psql -h $DB_HOST -U $DB_USER -d counseling_db
```

## 監視・メンテナンス

### パフォーマンス監視
```sql
-- 遅いクエリの特定
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
WHERE mean_exec_time > 1000 
ORDER BY mean_exec_time DESC;

-- インデックス使用状況
SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_tup_read DESC;
```

### 定期メンテナンス
```sql
-- 統計情報更新
ANALYZE;

-- 不要領域回収
VACUUM;

-- インデックス再構築
REINDEX DATABASE counseling_db;
```

## 今後の拡張予定

### 追加テーブル候補
1. **Analytics**: 集計済み分析データ
2. **Templates**: スクリプトテンプレート
3. **Notifications**: 通知履歴
4. **AuditLogs**: 監査ログ
5. **Settings**: ユーザー・クリニック設定

### スケーリング対応
1. **リードレプリカ**: 読み取り専用クエリの分離
2. **パーティショニング**: 日付ベースでのテーブル分割
3. **アーカイブ**: 古いセッションデータの別保存