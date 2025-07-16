'use client';

import React, { useState } from 'react';
import { useMediaRecorder } from '@/hooks/useMediaRecorder';
import { useAudioAnalyzer } from '@/hooks/useAudioAnalyzer';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { RecordingControls } from './RecordingControls';
import { RecordingTimer } from './RecordingTimer';
import { AudioLevelMeter } from './AudioLevelMeter';
import { RecordingPreview } from './RecordingPreview';
import { Mic, MicOff } from 'lucide-react';

interface AudioRecorderProps {
  onRecordingComplete?: (blob: Blob) => void;
  onError?: (error: string) => void;
  maxDuration?: number; // 最大録音時間（秒）
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onRecordingComplete,
  onError,
  maxDuration = 3600, // デフォルト60分
}) => {
  const { state, startRecording, stopRecording, pauseRecording, resumeRecording } = useMediaRecorder();
  const [stream, setStream] = useState<MediaStream | null>(null);
  const audioLevel = useAudioAnalyzer(stream);

  const handleStartRecording = async () => {
    try {
      await startRecording();
      // ストリーム取得のための処理
      const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setStream(mediaStream);
    } catch (error: any) {
      console.error('Failed to start recording:', error);
      onError?.(error.message || '録音の開始に失敗しました');
    }
  };

  const handleStopRecording = () => {
    stopRecording();
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  // 録音完了時の処理
  React.useEffect(() => {
    if (state.blob) {
      onRecordingComplete?.(state.blob);
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
        setStream(null);
      }
    }
  }, [state.blob, onRecordingComplete, stream]);

  // 最大録音時間チェック
  React.useEffect(() => {
    if (state.duration >= maxDuration && state.isRecording) {
      handleStopRecording();
    }
  }, [state.duration, maxDuration, state.isRecording]);

  // エラー処理
  React.useEffect(() => {
    if (state.error) {
      onError?.(state.error);
    }
  }, [state.error, onError]);

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {state.isRecording ? (
            <Mic className="h-5 w-5 text-red-500" />
          ) : (
            <MicOff className="h-5 w-5 text-gray-500" />
          )}
          音声録音
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* エラー表示 */}
        {state.error && (
          <Alert variant="destructive">
            <AlertDescription>{state.error}</AlertDescription>
          </Alert>
        )}

        {/* 録音時間表示 */}
        <RecordingTimer 
          duration={state.duration} 
          maxDuration={maxDuration}
          isRecording={state.isRecording}
        />

        {/* 音声レベルメーター */}
        <AudioLevelMeter 
          level={audioLevel} 
          isRecording={state.isRecording}
        />

        {/* 録音制御ボタン */}
        <RecordingControls
          isRecording={state.isRecording}
          isPaused={state.isPaused}
          onStart={handleStartRecording}
          onStop={handleStopRecording}
          onPause={pauseRecording}
          onResume={resumeRecording}
        />

        {/* 録音プレビュー */}
        {state.blob && (
          <RecordingPreview 
            blob={state.blob}
            duration={state.duration}
          />
        )}

        {/* 録音状態表示 */}
        <div className="text-center text-sm text-gray-600">
          {state.isRecording && !state.isPaused && "録音中..."}
          {state.isRecording && state.isPaused && "録音一時停止中"}
          {!state.isRecording && state.blob && "録音完了"}
          {!state.isRecording && !state.blob && "録音待機中"}
        </div>
      </CardContent>
    </Card>
  );
};