'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Play, Pause, Download, RotateCcw } from 'lucide-react';

interface RecordingPreviewProps {
  blob: Blob;
  duration: number;
}

export const RecordingPreview: React.FC<RecordingPreviewProps> = ({
  blob,
  duration,
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [audioUrl, setAudioUrl] = useState<string>('');
  const audioRef = useRef<HTMLAudioElement>(null);

  // Blobから音声URLを作成
  useEffect(() => {
    const url = URL.createObjectURL(blob);
    setAudioUrl(url);

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [blob]);

  // 音声再生状態の監視
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };

    const handlePlay = () => {
      setIsPlaying(true);
    };

    const handlePause = () => {
      setIsPlaying(false);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [audioUrl]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handlePlayPause = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
  };

  const handleRestart = () => {
    const audio = audioRef.current;
    if (!audio) return;

    audio.currentTime = 0;
    setCurrentTime(0);
  };

  const handleDownload = () => {
    const a = document.createElement('a');
    a.href = audioUrl;
    a.download = `recording_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.webm`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">録音プレビュー</CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* 隠れた音声要素 */}
        <audio ref={audioRef} src={audioUrl} preload="metadata" />

        {/* 録音情報 */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">録音時間:</span>
            <span className="ml-2 font-mono">{formatTime(duration)}</span>
          </div>
          <div>
            <span className="text-gray-600">ファイルサイズ:</span>
            <span className="ml-2">{(blob.size / 1024 / 1024).toFixed(2)} MB</span>
          </div>
        </div>

        {/* プログレスバー */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-gray-600">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-100"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* 制御ボタン */}
        <div className="flex justify-center gap-2">
          <Button
            onClick={handlePlayPause}
            variant="outline"
            size="sm"
          >
            {isPlaying ? (
              <Pause className="h-4 w-4 mr-1" />
            ) : (
              <Play className="h-4 w-4 mr-1" />
            )}
            {isPlaying ? '一時停止' : '再生'}
          </Button>

          <Button
            onClick={handleRestart}
            variant="outline"
            size="sm"
          >
            <RotateCcw className="h-4 w-4 mr-1" />
            最初から
          </Button>

          <Button
            onClick={handleDownload}
            variant="outline"
            size="sm"
          >
            <Download className="h-4 w-4 mr-1" />
            ダウンロード
          </Button>
        </div>

        {/* ファイル情報 */}
        <div className="text-xs text-gray-500 space-y-1">
          <div>形式: {blob.type}</div>
          <div>品質: 音声のみ、128kbps</div>
        </div>
      </CardContent>
    </Card>
  );
};