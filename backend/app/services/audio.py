"""
Audio processing service for handling recordings and transcription
"""
import boto3
from typing import Optional
import logging

from app.core.config import settings


logger = logging.getLogger(__name__)


class AudioService:
    """Service for handling audio operations"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.transcribe_client = boto3.client(
            'transcribe',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    async def upload_recording(self, file_content: bytes, session_id: str, filename: str) -> str:
        """
        Upload audio recording to S3
        """
        try:
            key = f"recordings/{session_id}/{filename}"
            
            self.s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=key,
                Body=file_content,
                ContentType='audio/mpeg'
            )
            
            url = f"s3://{settings.S3_BUCKET_NAME}/{key}"
            logger.info(f"Recording uploaded successfully: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to upload recording: {e}")
            raise
    
    async def start_transcription(self, recording_url: str, session_id: str) -> str:
        """
        Start transcription job using AWS Transcribe
        """
        try:
            job_name = f"transcribe-{session_id}"
            
            response = self.transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': recording_url},
                MediaFormat='mp3',
                LanguageCode='ja-JP',  # Japanese for beauty clinic
                OutputBucketName=settings.S3_BUCKET_NAME,
                OutputKey=f"transcripts/{session_id}/transcript.json"
            )
            
            logger.info(f"Transcription job started: {job_name}")
            return job_name
            
        except Exception as e:
            logger.error(f"Failed to start transcription: {e}")
            raise
    
    async def get_transcription_result(self, job_name: str) -> Optional[str]:
        """
        Get transcription result from AWS Transcribe
        """
        try:
            response = self.transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            
            job_status = response['TranscriptionJob']['TranscriptionJobStatus']
            
            if job_status == 'COMPLETED':
                transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
                # Download and parse the transcript file
                # TODO: Implement transcript file parsing
                return "Transcribed text would be extracted from the JSON file"
            elif job_status == 'FAILED':
                logger.error(f"Transcription job failed: {job_name}")
                return None
            else:
                # Job is still in progress
                return None
                
        except Exception as e:
            logger.error(f"Failed to get transcription result: {e}")
            raise


# Global audio service instance
audio_service = AudioService()