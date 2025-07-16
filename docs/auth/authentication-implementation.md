# JWT Authentication System Implementation

## 概要
美容医療脱毛クリニック カウンセリング分析システムのJWT認証システムの実装詳細について説明します。

## アーキテクチャ

### 認証フロー
```
1. ユーザーログイン (email + password)
2. 認証成功時、Access Token + Refresh Token発行
3. APIアクセス時、Authorization Header でAccess Token送信
4. Token検証・ユーザー情報取得
5. Access Token期限切れ時、Refresh Tokenで再発行
```

### セキュリティ機能
- **パスワードハッシュ化**: bcryptを使用
- **JWT署名**: HS256アルゴリズム
- **Token有効期限**: Access Token 30分、Refresh Token 30日
- **ロールベースアクセス制御**: counselor, manager, admin
- **パスワード強度チェック**: 8文字以上、大文字・小文字・数字必須

## 実装ファイル構成

### Core モジュール
```
app/core/
├── config.py          # アプリケーション設定
├── security.py        # JWT・パスワード処理
├── database.py        # DB接続管理
└── deps.py           # 依存性注入
```

### Schema モジュール
```
app/schemas/
├── auth.py           # 認証関連スキーマ
└── user.py           # ユーザー関連スキーマ
```

### Service モジュール
```
app/services/
└── auth_service.py   # 認証ビジネスロジック
```

### API モジュール
```
app/api/auth/
├── __init__.py
└── router.py         # 認証APIエンドポイント
```

## API エンドポイント

### 1. ログイン
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "counselor@clinic.example.com",
  "password": "SecurePass123"
}
```

**レスポンス:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "counselor@clinic.example.com",
    "name": "山田太郎",
    "role": "counselor",
    "clinic_id": "clinic-123",
    "is_active": true,
    "created_at": "2023-12-01T10:00:00Z",
    "updated_at": "2023-12-01T10:00:00Z"
  }
}
```

### 2. トークンリフレッシュ
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. ユーザー登録
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "new-counselor@clinic.example.com",
  "password": "SecurePass123",
  "name": "新人カウンセラー",
  "role": "counselor",
  "clinic_id": "clinic-123"
}
```

### 4. パスワードリセット
```http
POST /api/auth/password-reset-request
Content-Type: application/json

{
  "email": "user@clinic.example.com"
}
```

### 5. 現在ユーザー情報取得
```http
GET /api/auth/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## ユーザーロール

### counselor (カウンセラー)
- 自分の録音・分析データのみアクセス可能
- ダッシュボード閲覧（個人統計のみ）
- プロファイル更新

### manager (マネージャー)
- 所属クリニックの全データアクセス可能
- カウンセラー管理
- レポート生成
- 分析結果閲覧

### admin (管理者)
- 全クリニックデータアクセス可能
- ユーザー管理
- システム設定
- 全機能利用可能

## セキュリティ実装詳細

### パスワードハッシュ化
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### JWT Token生成
```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(subject: str, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    
    to_encode = {"exp": expire, "sub": subject, "type": "access"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
```

### 認証依存性注入
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    # Token検証・ユーザー取得ロジック
    pass
```

## 環境変数設定

### 必須設定
```bash
# セキュリティ
SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# データベース
DATABASE_URL=postgresql://user:password@localhost:5432/counseling_db

# 環境識別
ENVIRONMENT=dev  # dev, staging, prod
```

### 本番環境追加設定
```bash
# 強力なシークレットキー（32バイト以上推奨）
SECRET_KEY=$(openssl rand -hex 32)

# HTTPS強制
FORCE_HTTPS=true

# CORS設定
BACKEND_CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

## エラーハンドリング

### 認証エラー
```json
{
  "detail": "Could not validate credentials",
  "status_code": 401
}
```

### 権限エラー
```json
{
  "detail": "Not enough permissions",
  "status_code": 403
}
```

### バリデーションエラー
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must be at least 8 characters long",
      "type": "value_error"
    }
  ],
  "status_code": 422
}
```

## テスト実装

### 認証テスト例
```python
import pytest
from fastapi.testclient import TestClient

def test_login_success(client: TestClient):
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client: TestClient):
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401
```

## デプロイ時の注意事項

### セキュリティチェックリスト
- [ ] SECRET_KEYが強力な値に設定されている
- [ ] データベース接続が暗号化されている
- [ ] HTTPS強制が有効になっている
- [ ] CORS設定が適切に制限されている
- [ ] ログにパスワードが出力されていない

### パフォーマンス最適化
- [ ] データベースコネクションプール設定
- [ ] JWT Token有効期限の適切な設定
- [ ] Redis等でのセッション管理（オプション）

## 運用・監視

### ログ出力
- ログイン成功/失敗
- Token無効化
- 権限エラー
- パスワードリセット要求

### メトリクス監視
- ログイン成功率
- Token有効期限切れ頻度
- 認証エラー発生数
- アクティブユーザー数

## 今後の拡張予定

### 追加予定機能
1. **多要素認証 (MFA)**
   - TOTP対応
   - SMS認証

2. **ソーシャルログイン**
   - Google OAuth
   - Microsoft Azure AD

3. **セッション管理強化**
   - デバイス管理
   - 同時ログイン制限

4. **監査ログ**
   - ユーザーアクティビティ追跡
   - セキュリティイベント記録