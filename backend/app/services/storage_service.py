import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import uuid
import logging
from typing import Optional, Dict, Any
import os

from app.core.config import settings

logger = logging.getLogger(__name__)

class S3StorageService:
    """S3を使用したファイルストレージサービス"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        self.expiration = 3600  # プリサインドURLの有効期限（1時間）
        
        logger.info(f"S3StorageService initialized with bucket: {self.bucket_name}")

    def generate_file_path(
        self, 
        clinic_id: str, 
        customer_id: str, 
        session_date: datetime,
        file_extension: str = "webm"
    ) -> str:
        """ファイルパス生成
        
        Args:
            clinic_id: クリニックID
            customer_id: 顧客ID
            session_date: セッション日時
            file_extension: ファイル拡張子
            
        Returns:
            生成されたファイルパス
        """
        date_str = session_date.strftime('%Y%m%d')
        session_id = str(uuid.uuid4())
        return f"{clinic_id}/{customer_id}/{date_str}/{session_id}.{file_extension}"

    async def generate_presigned_upload_url(
        self, 
        file_path: str, 
        content_type: str,
        file_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """アップロード用プリサインドURL生成
        
        Args:
            file_path: S3内のファイルパス
            content_type: ファイルのContent-Type
            file_size: ファイルサイズ（バイト）
            
        Returns:
            プリサインドURL情報
        """
        try:
            # アップロード条件
            conditions = [
                ["content-length-range", 1, 100 * 1024 * 1024],  # 最大100MB
                {"Content-Type": content_type},
                {"ServerSideEncryption": "AES256"},
            ]
            
            # ファイルサイズ制限が指定されている場合
            if file_size:
                conditions[0] = ["content-length-range", file_size, file_size]

            fields = {
                "Content-Type": content_type,
                "ServerSideEncryption": "AES256",
                "x-amz-meta-uploaded-at": datetime.utcnow().isoformat(),
            }

            response = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=file_path,
                Fields=fields,
                Conditions=conditions,
                ExpiresIn=self.expiration
            )
            
            expires_at = datetime.utcnow() + timedelta(seconds=self.expiration)
            
            return {
                "upload_url": response["url"],
                "fields": response["fields"],
                "file_path": file_path,
                "expires_at": expires_at.isoformat()
            }
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned upload URL: {e}")
            raise Exception(f"プリサインドURL生成エラー: {e}")

    async def generate_presigned_download_url(self, file_path: str) -> Dict[str, Any]:
        """ダウンロード用プリサインドURL生成
        
        Args:
            file_path: S3内のファイルパス
            
        Returns:
            プリサインドURL情報
        """
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_path,
                },
                ExpiresIn=self.expiration
            )
            
            expires_at = datetime.utcnow() + timedelta(seconds=self.expiration)
            
            return {
                "download_url": response,
                "file_path": file_path,
                "expires_at": expires_at.isoformat()
            }
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned download URL: {e}")
            raise Exception(f"ダウンロードURL生成エラー: {e}")

    async def delete_file(self, file_path: str) -> bool:
        """ファイル削除
        
        Args:
            file_path: 削除するファイルのパス
            
        Returns:
            削除成功フラグ
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            logger.info(f"File deleted successfully: {file_path}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            raise Exception(f"ファイル削除エラー: {e}")

    async def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """ファイルメタデータ取得
        
        Args:
            file_path: ファイルパス
            
        Returns:
            ファイルメタデータ
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            
            return {
                "size": response['ContentLength'],
                "last_modified": response['LastModified'].isoformat(),
                "content_type": response['ContentType'],
                "metadata": response.get('Metadata', {}),
                "etag": response['ETag'].strip('"'),
                "encryption": response.get('ServerSideEncryption', None)
            }
            
        except ClientError as e:
            logger.error(f"Failed to get file metadata {file_path}: {e}")
            raise Exception(f"メタデータ取得エラー: {e}")

    async def file_exists(self, file_path: str) -> bool:
        """ファイル存在チェック
        
        Args:
            file_path: チェックするファイルパス
            
        Returns:
            ファイル存在フラグ
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"Error checking file existence {file_path}: {e}")
                raise Exception(f"ファイル存在チェックエラー: {e}")

    async def copy_file(self, source_path: str, dest_path: str) -> bool:
        """ファイルコピー
        
        Args:
            source_path: コピー元ファイルパス
            dest_path: コピー先ファイルパス
            
        Returns:
            コピー成功フラグ
        """
        try:
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': source_path
            }
            
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=dest_path,
                ServerSideEncryption='AES256'
            )
            
            logger.info(f"File copied from {source_path} to {dest_path}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to copy file from {source_path} to {dest_path}: {e}")
            raise Exception(f"ファイルコピーエラー: {e}")

    async def list_files(
        self, 
        prefix: str = "", 
        max_keys: int = 1000
    ) -> list[Dict[str, Any]]:
        """ファイル一覧取得
        
        Args:
            prefix: ファイルパスのプレフィックス
            max_keys: 取得する最大ファイル数
            
        Returns:
            ファイル一覧
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        "key": obj['Key'],
                        "size": obj['Size'],
                        "last_modified": obj['LastModified'].isoformat(),
                        "etag": obj['ETag'].strip('"')
                    })
            
            return files
            
        except ClientError as e:
            logger.error(f"Failed to list files with prefix {prefix}: {e}")
            raise Exception(f"ファイル一覧取得エラー: {e}")

    def validate_file_type(self, content_type: str) -> bool:
        """ファイルタイプ検証
        
        Args:
            content_type: ファイルのContent-Type
            
        Returns:
            有効なファイルタイプかどうか
        """
        allowed_types = [
            'audio/webm',
            'audio/mp4',
            'audio/mpeg',
            'audio/wav',
            'audio/ogg'
        ]
        return content_type in allowed_types

    def validate_file_size(self, file_size: int) -> bool:
        """ファイルサイズ検証
        
        Args:
            file_size: ファイルサイズ（バイト）
            
        Returns:
            有効なファイルサイズかどうか
        """
        max_size = 100 * 1024 * 1024  # 100MB
        return 0 < file_size <= max_size