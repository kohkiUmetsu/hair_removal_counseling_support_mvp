# Terraform Infrastructure Setup Guide

## 概要
本ドキュメントでは、美容医療脱毛クリニック カウンセリング分析システムのAWSインフラストラクチャをTerraformで構築する手順について説明します。

## 構築されるリソース

### ネットワーク
- **VPC**: プライベートクラウド環境
- **パブリックサブネット**: ALBとNAT Gateway用
- **プライベートサブネット**: ECSタスク用
- **データベースサブネット**: RDS用
- **Internet Gateway**: インターネット接続
- **NAT Gateway**: プライベートサブネットからのアウトバウンド通信

### セキュリティ
- **セキュリティグループ**: ALB、ECS、RDS用
- **IAMロール**: ECSタスク実行用、S3アクセス用
- **Secrets Manager**: データベースパスワード管理

### データベース
- **RDS PostgreSQL**: Multi-AZ対応（本番環境）
- **自動バックアップ**: 3-7日間保持
- **暗号化**: 保存時暗号化有効

### ストレージ
- **S3バケット**: 音声ファイル保存用
- **ライフサイクルポリシー**: コスト最適化
- **暗号化**: AES256で保存時暗号化
- **バージョニング**: 有効

### コンテナ
- **ECSクラスター**: Fargate使用
- **Application Load Balancer**: HTTPSトラフィック分散
- **CloudWatch Logs**: ログ収集

## 環境別構成

### 開発環境 (dev)
- RDS: t3.micro
- ECS: FARGATE_SPOT使用
- ログ保持: 7日間

### ステージング環境 (staging)
- RDS: t3.small
- ECS: FARGATE使用
- ログ保持: 14日間

### 本番環境 (prod)
- RDS: r5.large, Multi-AZ
- ECS: FARGATE使用
- ログ保持: 30日間
- 削除保護: 有効

## セットアップ手順

### 前提条件
1. AWS CLIがインストール・設定済み
2. Terraformがインストール済み（v1.0以上）
3. 適切なAWS権限を持つアカウント

### 1. Terraformバックエンド準備
まず、Terraformの状態管理用S3バケットとDynamoDBテーブルを作成します。

```bash
# S3バケット作成
aws s3 mb s3://counseling-app-terraform-state --region ap-northeast-1

# バケット暗号化設定
aws s3api put-bucket-encryption \
  --bucket counseling-app-terraform-state \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# バケットバージョニング有効化
aws s3api put-bucket-versioning \
  --bucket counseling-app-terraform-state \
  --versioning-configuration Status=Enabled

# DynamoDBテーブル作成（ロック用）
aws dynamodb create-table \
  --table-name counseling-app-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ap-northeast-1
```

### 2. 開発環境のデプロイ

```bash
# プロジェクトディレクトリに移動
cd infrastructure/environments/dev

# Terraform初期化
terraform init -backend-config=backend.conf

# プラン確認
terraform plan

# デプロイ実行
terraform apply
```

### 3. ステージング環境のデプロイ

```bash
cd ../staging
terraform init -backend-config=backend.conf
terraform plan
terraform apply
```

### 4. 本番環境のデプロイ

```bash
cd ../prod
terraform init -backend-config=backend.conf
terraform plan
terraform apply
```

## 出力値の確認

デプロイ完了後、以下のコマンドで重要な情報を取得できます：

```bash
# VPC ID
terraform output vpc_id

# RDSエンドポイント（機密情報）
terraform output rds_endpoint

# S3バケット名
terraform output s3_bucket_name

# ECSクラスター名
terraform output ecs_cluster_name

# ALB DNS名
terraform output alb_dns_name
```

## セキュリティ設定

### データベースパスワード
- Secrets Managerで自動生成・管理
- アプリケーションは環境変数で参照

### S3バケット
- パブリックアクセス完全ブロック
- CORS設定でオリジン制限
- IAMロールベースのアクセス制御

### ネットワーク
- プライベートサブネットでアプリケーション実行
- セキュリティグループで最小権限の原則

## 運用・メンテナンス

### 定期的な更新
```bash
# Terraformプロバイダーの更新
terraform init -upgrade

# 設定の検証
terraform validate

# フォーマット
terraform fmt -recursive
```

### リソースの削除
```bash
# 開発環境の削除
cd environments/dev
terraform destroy

# ※本番環境は削除保護により手動削除が必要
```

## トラブルシューティング

### よくある問題

1. **権限エラー**
   - IAMポリシーでTerraformに必要な権限が付与されているか確認

2. **リソース制限**
   - AWSアカウントのサービス制限を確認

3. **状態ファイルロック**
   - DynamoDBテーブルの状態を確認
   - 必要に応じて強制アンロック

```bash
terraform force-unlock <LOCK_ID>
```

## コスト最適化

### 開発環境
- 夜間・週末の自動停止を推奨
- FARGATE_SPOTの活用

### 本番環境
- S3ライフサイクルポリシーでコスト削減
- CloudWatch Logsの保持期間設定
- RDSの適切なインスタンスサイズ選択

## 監視・アラート

### CloudWatch設定
- ECSクラスター監視
- RDSパフォーマンス監視
- ALBアクセスログ

### 推奨アラート
- RDS CPU使用率
- ECSサービス異常
- S3バケットアクセス異常

## 次のステップ

1. **アプリケーションデプロイ**: ECSタスク定義の作成
2. **SSL証明書**: ACMでHTTPS対応
3. **ドメイン設定**: Route 53での DNS 設定
4. **モニタリング**: CloudWatch ダッシュボード設定