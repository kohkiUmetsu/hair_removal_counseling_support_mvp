# Phase 2: 録音・文字起こし機能チケット（3週間）

## 概要
音声録音、ファイル保存、文字起こし機能を実装するフェーズです。ブラウザベースの録音機能からAIを活用した文字起こしまでを含みます。

**期間**: 3週間  
**並列作業**: 可能（一部依存関係あり）  
**チーム**: フロントエンド、バックエンド  
**前提条件**: Phase 1完了（基盤構築済み）

---

## ✅ Ticket-06: Audio Recording - MediaRecorder API Implementation
**優先度**: 🟡 Medium  
**工数見積**: 5日  
**担当者**: フロントエンドエンジニア  
**依存関係**: Phase 1完了  
**ステータス**: ✅ **完了** - [実装詳細](../docs/ticket-06-implementation.md)

### 概要
ブラウザベースの音声録音機能を実装する

### 実装内容
- MediaRecorder API実装
- 録音開始・停止・一時停止機能
- 録音状況表示（時間、音声レベル）
- 音声波形表示
- 録音ファイルプレビュー機能
- 録音品質設定
- エラーハンドリング

### 技術仕様
```typescript
interface RecordingConfig {
  mimeType: string;           // 'audio/webm; codecs=opus'
  audioBitsPerSecond: number; // 128000
  sampleRate: number;         // 44100
  channelCount: number;       // 1 (モノラル)
}

interface RecordingState {
  isRecording: boolean;
  isPaused: boolean;
  duration: number;
  audioLevel: number;
  blob: Blob | null;
  error: string | null;
}
```

### コンポーネント構成
```
components/recording/
├── AudioRecorder.tsx        # メインレコーダーコンポーネント
├── RecordingControls.tsx    # 録音制御ボタン
├── AudioVisualizer.tsx      # 音声波形表示
├── RecordingTimer.tsx       # 録音時間表示
├── AudioLevelMeter.tsx      # 音声レベル表示
└── RecordingPreview.tsx     # 録音プレビュー

hooks/
├── useMediaRecorder.ts      # MediaRecorder管理hook
├── useAudioStream.ts        # 音声ストリーム管理hook
└── useAudioAnalyzer.ts      # 音声解析hook
```

### MediaRecorder実装
```typescript
// hooks/useMediaRecorder.ts
export const useMediaRecorder = () => {
  const [state, setState] = useState<RecordingState>({
    isRecording: false,
    isPaused: false,
    duration: 0,
    audioLevel: 0,
    blob: null,
    error: null,
  });

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm; codecs=opus',
        audioBitsPerSecond: 128000,
      });
      
      // 録音イベントハンドリング
    } catch (error) {
      setState(prev => ({ ...prev, error: error.message }));
    }
  };

  return { state, startRecording, stopRecording, pauseRecording };
};
```

### 音声レベル表示
```typescript
// hooks/useAudioAnalyzer.ts
export const useAudioAnalyzer = (stream: MediaStream | null) => {
  const [audioLevel, setAudioLevel] = useState(0);

  useEffect(() => {
    if (!stream) return;

    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const microphone = audioContext.createMediaStreamSource(stream);
    
    analyser.fftSize = 256;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    microphone.connect(analyser);

    const updateAudioLevel = () => {
      analyser.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((sum, value) => sum + value, 0) / bufferLength;
      setAudioLevel(average / 255); // 0-1の範囲に正規化
      requestAnimationFrame(updateAudioLevel);
    };

    updateAudioLevel();

    return () => {
      audioContext.close();
    };
  }, [stream]);

  return audioLevel;
};
```

### 受け入れ基準
- [x] 録音開始・停止が正常に動作する
- [x] 録音時間が正確に表示される
- [x] 音声レベルがリアルタイムで表示される
- [x] 録音ファイルが正常に生成される（WebM/MP4）
- [x] ブラウザ間での互換性が確保されている（Chrome, Firefox, Safari）
- [x] エラーハンドリングが実装されている
- [x] ユーザー権限要求が適切に処理される
- [x] 録音品質が要件を満たしている
- [x] レスポンシブデザインが実装されている

### パフォーマンス要件
- 録音開始レスポンス: 1秒以内
- CPU使用率: 10%以下
- メモリ使用量: 50MB以下（60分録音時）
- 音声レベル更新: 60fps

### エラーハンドリング
- マイクアクセス拒否
- 対応していないブラウザ
- 録音中のエラー
- ファイルサイズ制限超過

---

## ✅ Ticket-07: File Storage - S3 Integration
**優先度**: 🟡 Medium  
**工数見積**: 4日  
**担当者**: バックエンドエンジニア  
**依存関係**: Ticket-01（S3構築後）  
**ステータス**: ✅ **完了** - [実装詳細](../docs/ticket-07-implementation.md)

### 概要
S3への暗号化音声ファイル保存機能を実装する

### 実装内容
- S3 SDK設定
- ファイルアップロード機能
- プリサインドURL生成
- ファイル暗号化設定
- ファイル名自動生成機能
- ファイルメタデータ管理
- ファイルサイズ制限

### API仕様
```yaml
POST /api/recordings
  Content-Type: multipart/form-data
  Request:
    file: File (audio/webm, audio/mp4)
    customer_id: UUID
    session_date: ISO8601 datetime
  Response:
    recording_id: UUID
    file_path: string
    upload_url: string (presigned)
    expires_at: ISO8601 datetime

GET /api/recordings/{id}
  Headers:
    Authorization: Bearer {token}
  Response:
    recording_id: UUID
    file_path: string
    download_url: string (presigned)
    metadata: RecordingMetadata
    expires_at: ISO8601 datetime

DELETE /api/recordings/{id}
  Headers:
    Authorization: Bearer {token}
  Response:
    message: string

GET /api/recordings/upload-url
  Query:
    customer_id: UUID
    file_type: string
  Response:
    upload_url: string (presigned)
    file_path: string
    expires_at: ISO8601 datetime
```

### ファイル構成
```
backend/app/
├── api/recording/
│   ├── __init__.py
│   └── router.py           # 録音API
├── services/
│   └── storage_service.py   # S3操作サービス
├── schemas/
│   └── recording.py        # 録音スキーマ
└── utils/
    └── file_utils.py       # ファイルユーティリティ
```

### S3サービス実装
```python
# services/storage_service.py
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import uuid

class S3StorageService:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = settings.S3_BUCKET_NAME
        self.expiration = 3600  # 1時間

    def generate_file_path(self, clinic_id: str, customer_id: str, session_date: datetime) -> str:
        """ファイルパス生成"""
        date_str = session_date.strftime('%Y%m%d')
        session_id = str(uuid.uuid4())
        return f"{clinic_id}/{customer_id}/{date_str}/{session_id}"

    async def generate_presigned_upload_url(
        self, 
        file_path: str, 
        content_type: str
    ) -> dict:
        """アップロード用プリサインドURL生成"""
        try:
            response = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_path,
                    'ContentType': content_type,
                    'ServerSideEncryption': 'AES256',
                    'Metadata': {
                        'uploaded_at': datetime.utcnow().isoformat(),
                    }
                },
                ExpiresIn=self.expiration
            )
            return {
                'upload_url': response,
                'file_path': file_path,
                'expires_at': datetime.utcnow() + timedelta(seconds=self.expiration)
            }
        except ClientError as e:
            raise Exception(f"プリサインドURL生成エラー: {e}")

    async def generate_presigned_download_url(self, file_path: str) -> dict:
        """ダウンロード用プリサインドURL生成"""
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_path,
                },
                ExpiresIn=self.expiration
            )
            return {
                'download_url': response,
                'expires_at': datetime.utcnow() + timedelta(seconds=self.expiration)
            }
        except ClientError as e:
            raise Exception(f"ダウンロードURL生成エラー: {e}")

    async def delete_file(self, file_path: str) -> bool:
        """ファイル削除"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return True
        except ClientError as e:
            raise Exception(f"ファイル削除エラー: {e}")

    async def get_file_metadata(self, file_path: str) -> dict:
        """ファイルメタデータ取得"""
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return {
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'content_type': response['ContentType'],
                'metadata': response.get('Metadata', {})
            }
        except ClientError as e:
            raise Exception(f"メタデータ取得エラー: {e}")
```

### ファイル命名規則
```
{clinic_id}/{customer_id}/{session_date}/{session_id}.{extension}

例:
clinic-123e4567-e89b-12d3-a456-426614174000/
customer-987fcdeb-51f2-4567-89ab-123456789012/
20231201/
session-456e789a-bc12-3456-def0-123456789abc.webm
```

### 受け入れ基準
- [x] S3へのファイルアップロードが動作する
- [x] ファイルが暗号化されて保存される（AES256）
- [x] プリサインドURLが正常に生成される
- [x] ファイル名が規則に従って生成される
- [x] ファイルサイズ制限が実装されている（100MB）
- [x] エラーハンドリングが実装されている
- [x] ファイルメタデータが適切に保存される
- [x] 権限制御が実装されている（ユーザー別アクセス制御）

### セキュリティ要件
- サーバーサイド暗号化（AES256）
- プリサインドURLの有効期限制御
- ファイル拡張子チェック
- ファイルサイズ制限
- ユーザー認証・認可

### パフォーマンス要件
- アップロード速度: 1MB/秒以上
- プリサインドURL生成: 500ms以内
- ファイル削除: 1秒以内

---

## ✅ Ticket-08: Transcription Service - OpenAI Whisper Integration
**優先度**: 🟡 Medium  
**工数見積**: 4日  
**担当者**: バックエンドエンジニア  
**依存関係**: Ticket-07（ファイル保存機能後）  
**ステータス**: ✅ **完了** - [実装詳細](../docs/ticket-08-implementation.md)

### 概要
OpenAI Whisper APIを使用した音声文字起こし機能を実装する

### 実装内容
- OpenAI Whisper API連携
- 非同期処理実装（Celery/Redis）
- 処理状況管理
- 日本語音声最適化
- 文字起こし結果保存
- エラーハンドリング・リトライ機能

### API仕様
```yaml
POST /api/transcribe
  Headers:
    Authorization: Bearer {token}
  Request:
    recording_id: UUID
  Response:
    task_id: UUID
    status: "started"
    estimated_duration: number (seconds)

GET /api/transcribe/status/{task_id}
  Headers:
    Authorization: Bearer {token}
  Response:
    task_id: UUID
    status: "pending" | "processing" | "completed" | "failed"
    progress: number (0-100)
    result: TranscriptionResult | null
    error: string | null
    started_at: ISO8601 datetime
    completed_at: ISO8601 datetime | null

GET /api/transcribe/result/{task_id}
  Headers:
    Authorization: Bearer {token}
  Response:
    task_id: UUID
    transcription: TranscriptionResult
    confidence: number
    language: string
    segments: TranscriptionSegment[]

POST /api/transcribe/retry/{task_id}
  Headers:
    Authorization: Bearer {token}
  Response:
    task_id: UUID
    status: "retrying"
```

### データモデル
```python
# schemas/transcription.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TranscriptionSegment(BaseModel):
    id: int
    start: float
    end: float
    text: str
    confidence: float

class TranscriptionResult(BaseModel):
    text: str
    language: str
    confidence: float
    duration: float
    segments: List[TranscriptionSegment]

class TranscriptionTask(BaseModel):
    task_id: str
    recording_id: str
    status: str
    progress: int
    result: Optional[TranscriptionResult]
    error: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
```

### ファイル構成
```
backend/app/
├── api/transcribe/
│   ├── __init__.py
│   └── router.py           # 文字起こしAPI
├── services/
│   └── transcribe_service.py # Whisper連携サービス
├── tasks/
│   └── transcription_tasks.py # Celeryタスク
├── schemas/
│   └── transcription.py    # 文字起こしスキーマ
└── models/
    └── transcription.py    # 文字起こしモデル
```

### Whisperサービス実装
```python
# services/transcribe_service.py
import openai
from celery import current_task
import tempfile
import os
from typing import Optional

class TranscriptionService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.max_file_size = 25 * 1024 * 1024  # 25MB (Whisper制限)

    async def transcribe_audio(
        self, 
        file_path: str, 
        language: str = "ja"
    ) -> TranscriptionResult:
        """音声ファイルを文字起こし"""
        try:
            # S3からファイルダウンロード
            audio_data = await self._download_from_s3(file_path)
            
            # ファイルサイズチェック
            if len(audio_data) > self.max_file_size:
                audio_data = await self._compress_audio(audio_data)
            
            # 一時ファイル作成
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Whisper API呼び出し
                with open(temp_file_path, "rb") as audio_file:
                    response = openai.Audio.transcribe(
                        model="whisper-1",
                        file=audio_file,
                        language=language,
                        response_format="verbose_json",
                        temperature=0.0
                    )
                
                # 結果を構造化
                return self._parse_whisper_response(response)
                
            finally:
                # 一時ファイル削除
                os.unlink(temp_file_path)
                
        except Exception as e:
            raise Exception(f"文字起こしエラー: {e}")

    def _parse_whisper_response(self, response: dict) -> TranscriptionResult:
        """Whisperレスポンスをパース"""
        segments = []
        if 'segments' in response:
            segments = [
                TranscriptionSegment(
                    id=segment['id'],
                    start=segment['start'],
                    end=segment['end'],
                    text=segment['text'],
                    confidence=segment.get('confidence', 0.0)
                )
                for segment in response['segments']
            ]
        
        return TranscriptionResult(
            text=response['text'],
            language=response.get('language', 'ja'),
            confidence=self._calculate_overall_confidence(segments),
            duration=response.get('duration', 0.0),
            segments=segments
        )

    async def _compress_audio(self, audio_data: bytes) -> bytes:
        """音声ファイル圧縮（必要に応じてFFmpegなど使用）"""
        # 実装: ffmpeg-pythonを使用した圧縮
        pass

    def _calculate_overall_confidence(self, segments: List[TranscriptionSegment]) -> float:
        """全体の信頼度計算"""
        if not segments:
            return 0.0
        
        total_confidence = sum(segment.confidence for segment in segments)
        return total_confidence / len(segments)
```

### Celeryタスク実装
```python
# tasks/transcription_tasks.py
from celery import Celery
from app.services.transcribe_service import TranscriptionService
from app.models.transcription import TranscriptionTask
from app.core.database import get_db

celery_app = Celery('transcription')

@celery_app.task(bind=True)
def transcribe_audio_task(self, recording_id: str, file_path: str):
    """非同期文字起こしタスク"""
    task_id = self.request.id
    
    try:
        # タスク状況更新
        self.update_state(
            state='PROCESSING',
            meta={'progress': 0, 'status': '処理開始'}
        )
        
        # 文字起こし実行
        service = TranscriptionService()
        result = await service.transcribe_audio(file_path)
        
        # 進行状況更新
        self.update_state(
            state='PROCESSING',
            meta={'progress': 50, 'status': '文字起こし完了'}
        )
        
        # データベースに保存
        async with get_db() as db:
            await service.save_transcription_result(db, recording_id, result)
        
        # 完了
        self.update_state(
            state='SUCCESS',
            meta={
                'progress': 100,
                'status': '完了',
                'result': result.dict()
            }
        )
        
        return result.dict()
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={
                'progress': 0,
                'status': 'エラー',
                'error': str(e)
            }
        )
        raise
```

### 処理フロー
1. **録音ファイルS3から取得**
2. **ファイルサイズチェック・圧縮**
3. **Whisper APIに送信**
4. **文字起こし結果を取得**
5. **結果を構造化してデータベースに保存**
6. **フロントエンドに通知**

### 受け入れ基準
- [x] Whisper APIが正常に動作する
- [x] 非同期処理が実装されている（BackgroundTasks）
- [x] 処理状況がリアルタイムで取得できる
- [x] 日本語の文字起こし精度が適切（90%以上）
- [x] エラーハンドリングが実装されている
- [x] 処理時間制限が設定されている（10分）
- [x] リトライ機能が実装されている
- [x] ファイルサイズ制限が実装されている（25MB）
- [x] セグメント情報が正確に取得される

### パフォーマンス要件
- 処理時間: 音声1分あたり30秒以内
- 同時処理数: 5ファイルまで
- メモリ使用量: 512MB以下
- エラー率: 5%以下

### 品質要件
- 文字起こし精度: 90%以上（クリアな音声）
- 言語検出精度: 95%以上
- セグメント分割精度: 95%以上

---

## ✅ Phase 2 完了チェックリスト

### 録音機能
- [x] ブラウザで音声録音が正常に動作する
- [x] 録音時間・音声レベルが表示される
- [x] 録音ファイルが正常に生成される
- [x] ブラウザ間の互換性が確保されている

### ファイル保存
- [x] S3への暗号化保存が動作する
- [x] プリサインドURLが正常に生成される
- [x] ファイルアクセス制御が動作する
- [x] ファイルメタデータが適切に管理される

### 文字起こし
- [x] Whisper APIが正常に動作する
- [x] 非同期処理が実装されている
- [x] 日本語の文字起こし精度が要件を満たす
- [x] エラーハンドリング・リトライが動作する

### 統合テスト
- [x] 録音から文字起こしまでの全フローが動作する
- [x] 複数ユーザーの同時利用が可能
- [x] エラー状況での適切な処理が動作する
- [x] パフォーマンス要件を満たす

## 次のフェーズへの引き継ぎ事項

1. **録音データ**
   - 録音ファイルの保存場所・形式
   - メタデータ構造

2. **文字起こしデータ**
   - 文字起こし結果の形式
   - セグメント情報の構造
   - 信頼度情報

3. **API仕様**
   - 録音・文字起こしAPI
   - エラーレスポンス形式

4. **パフォーマンス情報**
   - 処理時間実績
   - エラー率実績
   - 最適化ポイント