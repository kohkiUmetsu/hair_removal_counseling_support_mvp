"""
Transcription service using OpenAI Whisper API
"""
import openai
import tempfile
import os
import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import asyncio
import aiofiles
import json

from app.core.config import settings
from app.services.storage_service import S3StorageService
from app.schemas.transcription import TranscriptionResult, TranscriptionSegment

logger = logging.getLogger(__name__)

class TranscriptionService:
    """文字起こしサービス"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.storage_service = S3StorageService()
        self.max_file_size = 25 * 1024 * 1024  # 25MB (Whisper制限)
        self.supported_formats = ['.webm', '.mp4', '.wav', '.mp3', '.m4a']
        
        logger.info("TranscriptionService initialized")

    async def transcribe_audio(
        self, 
        file_path: str, 
        language: str = "ja",
        temperature: float = 0.0
    ) -> TranscriptionResult:
        """音声ファイルを文字起こし
        
        Args:
            file_path: S3のファイルパス
            language: 言語コード (デフォルト: "ja")
            temperature: 温度パラメータ (0.0-1.0)
            
        Returns:
            文字起こし結果
        """
        temp_file_path = None
        try:
            logger.info(f"Starting transcription for file: {file_path}")
            
            # S3からファイルダウンロード
            audio_data = await self._download_from_s3(file_path)
            
            # ファイルサイズチェック
            if len(audio_data) > self.max_file_size:
                logger.warning(f"File size {len(audio_data)} exceeds limit, attempting compression")
                audio_data = await self._compress_audio(audio_data)
            
            # 一時ファイル作成
            file_extension = self._get_file_extension(file_path)
            temp_file_path = await self._create_temp_file(audio_data, file_extension)
            
            # Whisper API呼び出し
            response = await self._call_whisper_api(
                temp_file_path, 
                language, 
                temperature
            )
            
            # 結果を構造化
            result = self._parse_whisper_response(response)
            
            logger.info(f"Transcription completed for file: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed for file {file_path}: {e}")
            raise Exception(f"文字起こしエラー: {e}")
        finally:
            # 一時ファイル削除
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.debug(f"Temporary file deleted: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {temp_file_path}: {e}")

    async def _download_from_s3(self, file_path: str) -> bytes:
        """S3からファイルをダウンロード"""
        try:
            # プリサインドURLを取得してファイルをダウンロード
            download_info = await self.storage_service.generate_presigned_download_url(file_path)
            
            # TODO: ここで実際にHTTPリクエストを送ってファイルをダウンロード
            # 簡易実装として、ダミーデータを返す
            logger.warning("Using dummy audio data for development")
            return b"dummy_audio_data"  # 実際の実装では、HTTP GETでファイルを取得
            
        except Exception as e:
            logger.error(f"Failed to download file from S3: {e}")
            raise Exception(f"S3ファイルダウンロードエラー: {e}")

    async def _compress_audio(self, audio_data: bytes) -> bytes:
        """音声ファイル圧縮
        
        Note: 実際の実装では ffmpeg-python などを使用してファイルを圧縮
        """
        logger.warning("Audio compression not implemented, returning original data")
        return audio_data

    def _get_file_extension(self, file_path: str) -> str:
        """ファイル拡張子を取得"""
        extension = os.path.splitext(file_path)[1].lower()
        if extension in self.supported_formats:
            return extension
        return '.webm'  # デフォルト

    async def _create_temp_file(self, audio_data: bytes, file_extension: str) -> str:
        """一時ファイル作成"""
        try:
            with tempfile.NamedTemporaryFile(
                suffix=file_extension, 
                delete=False
            ) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            logger.debug(f"Temporary file created: {temp_file_path}")
            return temp_file_path
            
        except Exception as e:
            logger.error(f"Failed to create temporary file: {e}")
            raise Exception(f"一時ファイル作成エラー: {e}")

    async def _call_whisper_api(
        self, 
        file_path: str, 
        language: str, 
        temperature: float
    ) -> Dict[str, Any]:
        """Whisper API呼び出し"""
        try:
            logger.info(f"Calling Whisper API for file: {file_path}")
            
            with open(file_path, "rb") as audio_file:
                # 実際のWhisper API呼び出し
                if settings.OPENAI_API_KEY:
                    response = self.openai_client.audio.transcriptions.create(
                        model=settings.WHISPER_MODEL,
                        file=audio_file,
                        language=language,
                        response_format="verbose_json",
                        temperature=temperature
                    )
                    
                    # レスポンスを辞書形式に変換
                    return response.model_dump()
                else:
                    # 開発環境用のダミーレスポンス
                    logger.warning("OpenAI API key not provided, using dummy response")
                    return self._create_dummy_response()
                
        except Exception as e:
            logger.error(f"Whisper API call failed: {e}")
            raise Exception(f"Whisper API呼び出しエラー: {e}")

    def _create_dummy_response(self) -> Dict[str, Any]:
        """開発用のダミーレスポンス"""
        return {
            "text": "こちらは開発環境用のダミー文字起こし結果です。実際の音声内容ではありません。",
            "language": "ja",
            "duration": 10.5,
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 5.2,
                    "text": "こちらは開発環境用のダミー文字起こし結果です。",
                    "confidence": 0.95,
                    "no_speech_prob": 0.02
                },
                {
                    "id": 1,
                    "start": 5.2,
                    "end": 10.5,
                    "text": "実際の音声内容ではありません。",
                    "confidence": 0.92,
                    "no_speech_prob": 0.03
                }
            ]
        }

    def _parse_whisper_response(self, response: Dict[str, Any]) -> TranscriptionResult:
        """Whisperレスポンスをパース"""
        try:
            # セグメントをパース
            segments = []
            if 'segments' in response and response['segments']:
                for segment in response['segments']:
                    segments.append(TranscriptionSegment(
                        id=segment.get('id', 0),
                        start=float(segment.get('start', 0.0)),
                        end=float(segment.get('end', 0.0)),
                        text=segment.get('text', ''),
                        confidence=float(segment.get('confidence', 0.0))
                    ))
            
            # 全体の信頼度を計算
            overall_confidence = self._calculate_overall_confidence(segments)
            
            return TranscriptionResult(
                text=response.get('text', ''),
                language=response.get('language', 'ja'),
                confidence=overall_confidence,
                duration=float(response.get('duration', 0.0)),
                segments=segments
            )
            
        except Exception as e:
            logger.error(f"Failed to parse Whisper response: {e}")
            raise Exception(f"Whisperレスポンス解析エラー: {e}")

    def _calculate_overall_confidence(self, segments: List[TranscriptionSegment]) -> float:
        """全体の信頼度計算"""
        if not segments:
            return 0.0
        
        # 長さで重み付けした平均を計算
        total_duration = 0.0
        weighted_confidence = 0.0
        
        for segment in segments:
            duration = segment.end - segment.start
            total_duration += duration
            weighted_confidence += segment.confidence * duration
        
        if total_duration > 0:
            return weighted_confidence / total_duration
        else:
            # 全セグメントの単純平均
            return sum(segment.confidence for segment in segments) / len(segments)

    def estimate_processing_time(self, audio_duration: float) -> int:
        """処理時間の推定（秒）
        
        Args:
            audio_duration: 音声の長さ（秒）
            
        Returns:
            推定処理時間（秒）
        """
        # 経験的な値: 音声1秒あたり0.5秒の処理時間
        base_time = audio_duration * 0.5
        
        # 最低10秒、最大300秒（5分）
        return max(10, min(int(base_time), 300))

    async def validate_audio_file(self, file_path: str) -> bool:
        """音声ファイルの検証
        
        Args:
            file_path: ファイルパス
            
        Returns:
            有効なファイルかどうか
        """
        try:
            # ファイル存在チェック
            if not await self.storage_service.file_exists(file_path):
                return False
            
            # ファイル拡張子チェック
            extension = self._get_file_extension(file_path)
            if extension not in self.supported_formats:
                return False
            
            # ファイルメタデータチェック
            metadata = await self.storage_service.get_file_metadata(file_path)
            
            # ファイルサイズチェック
            if metadata['size'] > self.max_file_size * 2:  # 圧縮を考慮して2倍まで
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"File validation failed for {file_path}: {e}")
            return False

    async def cleanup_old_tasks(self, days: int = 7) -> int:
        """古い文字起こしタスクのクリーンアップ
        
        Args:
            days: 削除対象の日数
            
        Returns:
            削除されたタスク数
        """
        # TODO: データベースから古いタスクを削除する実装
        logger.info(f"Cleanup tasks older than {days} days")
        return 0

    def get_supported_languages(self) -> List[str]:
        """サポートされている言語コード一覧"""
        return [
            "ja",  # 日本語
            "en",  # 英語
            "zh",  # 中国語
            "ko",  # 韓国語
            "es",  # スペイン語
            "fr",  # フランス語
            "de",  # ドイツ語
            "it",  # イタリア語
            "pt",  # ポルトガル語
            "ru",  # ロシア語
        ]