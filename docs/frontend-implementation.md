# フロントエンド実装ドキュメント

## 概要

このドキュメントでは、美容クリニック カウンセリング分析システムのフロントエンド実装について詳細に説明します。バックエンドAPIと完全に統合された包括的なユーザーインターフェースを提供しています。

## アーキテクチャ

### 技術スタック
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI (shadcn/ui)
- **State Management**: React Context + useState
- **Authentication**: JWT Token-based
- **HTTP Client**: Fetch API

### ディレクトリ構造
```
frontend/
├── app/                          # Next.js App Router pages
│   ├── (auth)/                   # Authentication group
│   │   ├── layout.tsx           # Auth layout (no sidebar)
│   │   └── login/               # Login page
│   ├── dashboard/               # Main dashboard
│   │   ├── executive/           # Executive dashboard
│   │   ├── layout.tsx           # Dashboard layout
│   │   └── page.tsx             # Default dashboard
│   ├── sessions/                # Session management
│   │   ├── [id]/                # Session detail pages
│   │   └── page.tsx             # Sessions list
│   ├── recording/               # Audio recording
│   ├── recordings/              # Recording file management
│   ├── transcription/           # Transcription management
│   ├── analysis/                # AI analysis results
│   ├── improvement/             # Improvement suggestions
│   ├── users/                   # User management
│   ├── settings/                # System settings
│   └── layout.tsx               # Root layout
├── components/                   # Reusable components
│   ├── auth/                    # Authentication components
│   ├── layout/                  # Layout components
│   ├── recording/               # Recording components
│   └── ui/                      # Base UI components
└── lib/                         # Utilities and configuration
    ├── auth.tsx                 # Authentication context
    ├── api.ts                   # API utilities
    └── utils.ts                 # General utilities
```

## 実装済み機能

### 1. 認証システム

#### 実装内容
- JWT トークンベースの認証
- ローカルストレージでのトークン管理
- 自動ログアウト（トークン失効時）
- 保護されたルートの実装

#### ファイル
- `lib/auth.tsx` - AuthProvider, useAuth hook
- `components/auth/protected-route.tsx` - ルート保護
- `app/(auth)/login/page.tsx` - ログインページ

#### 特徴
- ロールベースアクセス制御（カウンセラー、マネージャー、管理者）
- 認証状態の自動復元
- 一時的認証無効化機能（開発用）

### 2. レイアウトシステム

#### 実装内容
- 条件付きサイドバー表示
- レスポンシブデザイン
- 統一されたヘッダー・フッター

#### ファイル
- `components/layout/layout-wrapper.tsx` - メインレイアウト
- `components/layout/sidebar.tsx` - ナビゲーションサイドバー
- `components/layout/header.tsx` - ページヘッダー

#### 特徴
- 認証ページでは表示されない
- 動的なナビゲーション（ロールベース）
- アクティブページの強調表示

### 3. 録音機能

#### 実装内容
- ブラウザ内音声録音
- S3への直接アップロード
- プログレス表示
- エラーハンドリング

#### ファイル
- `app/recording/page.tsx` - 録音インターフェース
- `components/recording/AudioRecorder.tsx` - 録音コンポーネント

#### API統合
- `GET /api/v1/recordings/upload-url` - プリサインドURL取得
- `PUT S3_URL` - S3への直接アップロード
- `PUT /api/v1/recordings/{id}/complete` - アップロード完了通知

### 4. 録音ファイル管理

#### 実装内容
- 録音ファイル一覧表示
- ファイルダウンロード機能
- ファイル削除機能（権限ベース）
- 統計情報表示

#### ファイル
- `app/recordings/page.tsx` - 録音ファイル管理ページ

#### 機能
- ファイルサイズ・時間表示
- 検索・フィルタリング
- ステータス表示（完了/処理中/失敗）

### 5. セッション管理

#### 実装内容
- セッション一覧表示
- セッション詳細ページ
- ワークフロー管理（録音→文字起こし→分析）

#### ファイル
- `app/sessions/page.tsx` - セッション一覧
- `app/sessions/[id]/page.tsx` - セッション詳細

#### 機能
- セッションステータス追跡
- 関連ファイルの表示
- 次のステップへの誘導

### 6. 文字起こし管理

#### 実装内容
- 文字起こしタスク管理
- リアルタイム状況更新
- 結果表示・ダウンロード
- 再実行機能

#### ファイル
- `app/transcription/page.tsx` - 文字起こし管理ダッシュボード

#### API統合
- `POST /api/v1/transcription/` - 文字起こし開始
- `GET /api/v1/transcription/status/{task_id}` - 状況確認
- `GET /api/v1/transcription/result/{task_id}` - 結果取得
- `POST /api/v1/transcription/retry/{task_id}` - 再実行

### 7. AI分析機能

#### 実装内容
- 分析タスク管理
- 結果可視化
- 統計情報表示
- レポート出力機能

#### ファイル
- `app/analysis/page.tsx` - AI分析ダッシュボード

#### 機能
- 満足度・エンゲージメント可視化
- センチメント分析結果表示
- 関心事項・推奨事項表示
- トレンド分析

### 8. 改善提案システム

#### 実装内容
- 個別改善提案表示
- 成功パターン分析
- パフォーマンストレンド
- スクリプト生成ツール

#### ファイル
- `app/improvement/page.tsx` - 改善提案ダッシュボード

#### 機能
- AI生成の改善提案
- 成功パターンの学習
- カスタムスクリプト生成
- フィードバック収集

### 9. エグゼクティブダッシュボード

#### 実装内容
- 経営レベルの KPI 表示
- パフォーマンス分析
- オペレーション インサイト
- アラート表示

#### ファイル
- `app/dashboard/executive/page.tsx` - エグゼクティブダッシュボード

#### 機能
- 総合統計表示
- トップパフォーマー表示
- 時間別利用状況
- カスタムレポート生成

### 10. ユーザー管理

#### 実装内容
- ユーザー一覧表示
- ロール管理
- 権限ベースアクセス
- 検索・フィルタリング

#### ファイル
- `app/users/page.tsx` - ユーザー管理ページ

#### 機能
- ユーザー情報表示
- ロール別統計
- 最終ログイン追跡

### 11. システム設定

#### 実装内容
- プロフィール管理
- 通知設定
- システム設定（管理者のみ）
- パスワード変更

#### ファイル
- `app/settings/page.tsx` - 設定ページ

#### 機能
- ユーザープロフィール編集
- 通知の詳細設定
- セキュリティ設定

## UIコンポーネント

### 基本コンポーネント
- `Card`, `CardHeader`, `CardContent`, `CardTitle` - コンテナ
- `Button` - アクション要素
- `Input`, `Textarea` - フォーム要素
- `Badge` - ステータス表示
- `Tabs` - タブ切り替え
- `Progress` - プログレスバー
- `Switch` - トグルスイッチ
- `Select` - ドロップダウン選択

### カスタムコンポーネント
- `AudioRecorder` - 音声録音機能
- `ProtectedRoute` - ルート保護
- `LayoutWrapper` - 条件付きレイアウト

## API統合

### 認証API
```typescript
// ログイン
POST /api/v1/auth/login
// トークン検証
POST /api/v1/auth/test-token
// ユーザー情報取得
GET /api/v1/auth/me
```

### セッション管理API
```typescript
// セッション一覧
GET /api/v1/sessions/
// セッション詳細
GET /api/v1/sessions/{id}
// セッション作成
POST /api/v1/sessions/
// セッション更新
PUT /api/v1/sessions/{id}
```

### 録音関連API
```typescript
// アップロードURL取得
GET /api/v1/recordings/upload-url
// 録音一覧
GET /api/v1/recordings/
// 録音ダウンロード
GET /api/v1/recordings/{id}
// 録音削除
DELETE /api/v1/recordings/{id}
```

### 文字起こしAPI
```typescript
// 文字起こし開始
POST /api/v1/transcription/
// 状況確認
GET /api/v1/transcription/status/{task_id}
// 結果取得
GET /api/v1/transcription/result/{task_id}
// 統計情報
GET /api/v1/transcription/stats
```

### AI分析API
```typescript
// 分析開始
POST /api/v1/ai-analysis/
// 分析状況
GET /api/v1/ai-analysis/status/{task_id}
// 分析結果
GET /api/v1/ai-analysis/result/{analysis_id}
// 統計情報
GET /api/v1/ai-analysis/stats
```

### 改善提案API
```typescript
// 改善提案取得
GET /api/v1/improvement/{analysis_id}/suggestions
// スクリプト生成
POST /api/v1/improvement/generate-script
// 成功パターン
GET /api/v1/improvement/success-patterns
// フィードバック送信
POST /api/v1/improvement/feedback
```

### ダッシュボードAPI
```typescript
// エグゼクティブダッシュボード
GET /api/v1/dashboard/executive
// カウンセラーダッシュボード
GET /api/v1/dashboard/counselor/{id}
// レポート出力
POST /api/v1/dashboard/export
```

## 状態管理

### AuthContext
```typescript
interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
  isAuthenticated: boolean;
}
```

### ローカル状態管理
各ページで独立した状態管理：
- データフェッチの loading 状態
- エラーハンドリング
- フォーム状態
- UI状態（モーダル、タブ等）

## エラーハンドリング

### 統一されたエラー処理
- API エラーの統一表示
- ネットワークエラーの処理
- 認証エラーの自動処理
- ユーザーフレンドリーなメッセージ

### 再試行機能
- 失敗したリクエストの再実行
- バックグラウンドタスクの再開
- 自動リフレッシュ機能

## セキュリティ

### 認証・認可
- JWT トークンベース認証
- ロールベースアクセス制御
- 保護されたルート
- CSRF対策

### データ保護
- クライアントサイドでの機密情報隠蔽
- S3 プリサインドURL使用
- トークンの安全な保存

## パフォーマンス最適化

### コード分割
- Next.js 自動コード分割
- 動的インポート
- レイジーローディング

### キャッシュ戦略
- ブラウザキャッシュ活用
- SWR パターン実装検討
- 静的リソース最適化

## 今後の拡張性

### 予定されている機能
- リアルタイム通知（WebSocket）
- ファイルドラッグ&ドロップ
- 高度な分析チャート
- モバイル対応強化

### アーキテクチャの拡張
- マルチテナント対応
- 国際化（i18n）
- PWA機能
- オフライン対応

## トラブルシューティング

### よくある問題
1. **認証エラー**: トークンの期限切れ → 自動再ログイン
2. **アップロードエラー**: ネットワーク問題 → 再試行機能
3. **表示エラー**: データ不整合 → バリデーション強化

### デバッグ方法
- ブラウザ開発者ツール使用
- ネットワークタブでAPI確認
- コンソールログ確認
- ローカルストレージ確認

## まとめ

本フロントエンド実装は、バックエンドAPIの豊富な機能を最大限活用し、ユーザーフレンドリーで効率的なインターフェースを提供しています。今後の機能拡張やメンテナンスを考慮した設計となっており、継続的な改善が可能な構造となっています。