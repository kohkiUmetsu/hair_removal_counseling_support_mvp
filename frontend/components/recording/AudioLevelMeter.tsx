'use client';

import React from 'react';
import { Volume2, VolumeX } from 'lucide-react';

interface AudioLevelMeterProps {
  level: number; // 0-1の範囲
  isRecording: boolean;
}

export const AudioLevelMeter: React.FC<AudioLevelMeterProps> = ({
  level,
  isRecording,
}) => {
  // レベルを0-100のパーセンテージに変換
  const levelPercentage = Math.min(level * 100, 100);
  
  // レベルに応じた色を決定
  const getColorClass = (percentage: number) => {
    if (percentage < 20) return 'bg-gray-400';
    if (percentage < 40) return 'bg-green-400';
    if (percentage < 70) return 'bg-yellow-400';
    if (percentage < 90) return 'bg-orange-400';
    return 'bg-red-500';
  };

  // バーの数（20本）
  const barCount = 20;
  const activeBars = Math.round((levelPercentage / 100) * barCount);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-center gap-2">
        {isRecording ? (
          <Volume2 className="h-4 w-4 text-gray-600" />
        ) : (
          <VolumeX className="h-4 w-4 text-gray-400" />
        )}
        <span className="text-sm text-gray-600">
          音声レベル: {Math.round(levelPercentage)}%
        </span>
      </div>

      {/* 音声レベルバー */}
      <div className="flex items-center justify-center gap-1">
        {Array.from({ length: barCount }, (_, index) => {
          const isActive = index < activeBars && isRecording;
          const barHeight = Math.min(4 + (index * 2), 24); // 高さを段階的に変化
          
          return (
            <div
              key={index}
              className={`w-2 transition-all duration-100 rounded-sm ${
                isActive 
                  ? getColorClass(levelPercentage)
                  : 'bg-gray-200'
              }`}
              style={{ height: `${barHeight}px` }}
            />
          );
        })}
      </div>

      {/* 数値表示 */}
      <div className="text-center">
        <span className={`text-xs font-mono ${
          isRecording ? 'text-gray-700' : 'text-gray-400'
        }`}>
          {level.toFixed(3)}
        </span>
      </div>
    </div>
  );
};