'use client';

import React, { useState } from 'react';
import { AudioRecorder } from '@/components/recording/AudioRecorder';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Upload, FileAudio, CheckCircle } from 'lucide-react';

export default function RecordingPage() {
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [error, setError] = useState<string>('');

  const handleRecordingComplete = (blob: Blob) => {
    setRecordedBlob(blob);
    setUploadSuccess(false);
    setError('');
  };

  const handleRecordingError = (error: string) => {
    setError(error);
  };

  const handleUpload = async () => {
    if (!recordedBlob) return;

    setIsUploading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      
      // Step 1: Create recording record and get presigned upload URL
      const uploadUrlResponse = await fetch('/api/v1/recordings/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          customer_id: 'dummy', // TODO: Replace with actual customer ID
          session_date: new Date().toISOString(),
          content_type: 'audio/webm',
          file_size: recordedBlob.size,
          filename: 'recording.webm'
        })
      });

      if (!uploadUrlResponse.ok) {
        throw new Error('Failed to get upload URL');
      }

      const { upload_url, fields, file_path, recording_id } = await uploadUrlResponse.json();

      // Step 2: Upload file to S3
      const uploadResponse = await fetch(upload_url, {
        method: 'PUT',
        body: recordedBlob,
        headers: {
          'Content-Type': 'audio/webm'
        }
      });

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload file to S3');
      }

      // Step 3: Mark upload as complete
      const completeResponse = await fetch(`/api/v1/recordings/${recording_id}/complete`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!completeResponse.ok) {
        throw new Error('Failed to mark upload as complete');
      }
      
      setUploadSuccess(true);
      setRecordedBlob(null);
    } catch (error: unknown) {
      setError('アップロードに失敗しました: ' + (error instanceof Error ? error.message : '不明なエラー'));
    } finally {
      setIsUploading(false);
    }
  };

  const resetRecording = () => {
    setRecordedBlob(null);
    setUploadSuccess(false);
    setError('');
  };

  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="space-y-6">
          {/* ページヘッダー */}
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold text-gray-900">カウンセリング録音</h1>
            <p className="text-gray-600">
              顧客とのカウンセリングセッションを録音し、後で分析することができます
            </p>
          </div>

          {/* エラー表示 */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* アップロード成功表示 */}
          {uploadSuccess && (
            <Alert className="border-green-500 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                録音ファイルのアップロードが完了しました。
              </AlertDescription>
            </Alert>
          )}

          {/* 使用方法 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileAudio className="h-5 w-5" />
                使用方法
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
                <li>「録音開始」ボタンをクリックして録音を開始します</li>
                <li>マイクへのアクセス許可を求められた場合は「許可」をクリックしてください</li>
                <li>カウンセリングセッションの音声が録音されます</li>
                <li>録音を終了したい場合は「停止」ボタンをクリックします</li>
                <li>録音内容をプレビューで確認できます</li>
                <li>問題なければ「アップロード」ボタンでサーバーに保存します</li>
              </ol>
            </CardContent>
          </Card>

          {/* 録音コンポーネント */}
          <div className="flex justify-center">
            <AudioRecorder
              onRecordingComplete={handleRecordingComplete}
              onError={handleRecordingError}
              maxDuration={3600} // 60分
            />
          </div>

          {/* アップロードセクション */}
          {recordedBlob && !uploadSuccess && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  録音完了
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-gray-600">
                  録音が完了しました。内容を確認してからアップロードしてください。
                </p>
                <div className="flex justify-center gap-4">
                  <Button
                    onClick={handleUpload}
                    disabled={isUploading}
                    className="bg-blue-500 hover:bg-blue-600"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    {isUploading ? 'アップロード中...' : 'アップロード'}
                  </Button>
                  <Button
                    onClick={resetRecording}
                    variant="outline"
                    disabled={isUploading}
                  >
                    やり直し
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 技術仕様 */}
          <Card>
            <CardHeader>
              <CardTitle>技術仕様</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700">対応形式:</span>
                  <span className="ml-2">WebM (Opus), MP4</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">音質:</span>
                  <span className="ml-2">128kbps, 44.1kHz</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">最大録音時間:</span>
                  <span className="ml-2">60分</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">最大ファイルサイズ:</span>
                  <span className="ml-2">100MB</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">対応ブラウザ:</span>
                  <span className="ml-2">Chrome, Firefox, Safari</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">セキュリティ:</span>
                  <span className="ml-2">暗号化保存</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </ProtectedRoute>
  );
}