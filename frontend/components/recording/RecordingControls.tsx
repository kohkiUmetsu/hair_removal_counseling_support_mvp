'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { Mic, Square, Pause, Play } from 'lucide-react';

interface RecordingControlsProps {
  isRecording: boolean;
  isPaused: boolean;
  onStart: () => void;
  onStop: () => void;
  onPause: () => void;
  onResume: () => void;
  disabled?: boolean;
}

export const RecordingControls: React.FC<RecordingControlsProps> = ({
  isRecording,
  isPaused,
  onStart,
  onStop,
  onPause,
  onResume,
  disabled = false,
}) => {
  if (!isRecording) {
    // 録音していない状態
    return (
      <div className="flex justify-center">
        <Button
          onClick={onStart}
          disabled={disabled}
          size="lg"
          className="bg-red-500 hover:bg-red-600 text-white px-8 py-4"
        >
          <Mic className="h-6 w-6 mr-2" />
          録音開始
        </Button>
      </div>
    );
  }

  // 録音中の状態
  return (
    <div className="flex justify-center gap-4">
      {/* 一時停止/再開ボタン */}
      {isPaused ? (
        <Button
          onClick={onResume}
          disabled={disabled}
          size="lg"
          variant="outline"
        >
          <Play className="h-5 w-5 mr-2" />
          再開
        </Button>
      ) : (
        <Button
          onClick={onPause}
          disabled={disabled}
          size="lg"
          variant="outline"
        >
          <Pause className="h-5 w-5 mr-2" />
          一時停止
        </Button>
      )}

      {/* 停止ボタン */}
      <Button
        onClick={onStop}
        disabled={disabled}
        size="lg"
        variant="destructive"
      >
        <Square className="h-5 w-5 mr-2" />
        停止
      </Button>
    </div>
  );
};