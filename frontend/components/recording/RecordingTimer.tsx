'use client';

import React from 'react';
import { Clock } from 'lucide-react';

interface RecordingTimerProps {
  duration: number;
  maxDuration?: number;
  isRecording: boolean;
}

export const RecordingTimer: React.FC<RecordingTimerProps> = ({
  duration,
  maxDuration = 3600,
  isRecording,
}) => {
  const formatTime = (seconds: number): string => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hrs > 0) {
      return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const formatMaxTime = (seconds: number): string => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);

    if (hrs > 0) {
      return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:00`;
    }
    return `${mins.toString().padStart(2, '0')}:00`;
  };

  const progress = (duration / maxDuration) * 100;
  const isNearLimit = progress > 90;
  const isAtLimit = progress >= 100;

  return (
    <div className="text-center space-y-2">
      {/* 時間表示 */}
      <div className="flex items-center justify-center gap-2">
        <Clock className={`h-5 w-5 ${isRecording ? 'text-red-500' : 'text-gray-500'}`} />
        <span 
          className={`text-2xl font-mono font-bold ${
            isAtLimit ? 'text-red-600' : 
            isNearLimit ? 'text-orange-500' : 
            isRecording ? 'text-red-500' : 'text-gray-700'
          }`}
        >
          {formatTime(duration)}
        </span>
        <span className="text-sm text-gray-500">
          / {formatMaxTime(maxDuration)}
        </span>
      </div>

      {/* プログレスバー */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${
            isAtLimit ? 'bg-red-600' :
            isNearLimit ? 'bg-orange-500' :
            'bg-red-500'
          }`}
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>

      {/* 警告メッセージ */}
      {isNearLimit && !isAtLimit && (
        <p className="text-sm text-orange-600">
          まもなく最大録音時間に達します
        </p>
      )}
      
      {isAtLimit && (
        <p className="text-sm text-red-600">
          最大録音時間に達しました
        </p>
      )}
    </div>
  );
};