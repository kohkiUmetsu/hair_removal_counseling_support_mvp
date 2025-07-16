import { useState, useRef, useCallback, useEffect } from 'react';

export interface RecordingConfig {
  mimeType: string;
  audioBitsPerSecond: number;
  sampleRate: number;
  channelCount: number;
}

export interface RecordingState {
  isRecording: boolean;
  isPaused: boolean;
  duration: number;
  audioLevel: number;
  blob: Blob | null;
  error: string | null;
}

const DEFAULT_CONFIG: RecordingConfig = {
  mimeType: 'audio/webm; codecs=opus',
  audioBitsPerSecond: 128000,
  sampleRate: 44100,
  channelCount: 1,
};

export const useMediaRecorder = (config: Partial<RecordingConfig> = {}) => {
  const [state, setState] = useState<RecordingState>({
    isRecording: false,
    isPaused: false,
    duration: 0,
    audioLevel: 0,
    blob: null,
    error: null,
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(0);

  const recordingConfig = { ...DEFAULT_CONFIG, ...config };

  const updateDuration = useCallback(() => {
    if (state.isRecording && !state.isPaused) {
      const elapsed = (Date.now() - startTimeRef.current) / 1000;
      setState(prev => ({ ...prev, duration: elapsed }));
    }
  }, [state.isRecording, state.isPaused]);

  useEffect(() => {
    if (state.isRecording && !state.isPaused) {
      timerRef.current = setInterval(updateDuration, 100);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [state.isRecording, state.isPaused, updateDuration]);

  const startRecording = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, error: null }));

      // メディアストリーム取得
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: recordingConfig.sampleRate,
          channelCount: recordingConfig.channelCount,
        },
      });

      streamRef.current = stream;

      // MediaRecorder作成
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: recordingConfig.mimeType,
        audioBitsPerSecond: recordingConfig.audioBitsPerSecond,
      });

      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      // イベントハンドラー設定
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: recordingConfig.mimeType });
        setState(prev => ({ 
          ...prev, 
          blob,
          isRecording: false,
          isPaused: false,
        }));
      };

      mediaRecorder.onerror = (event: any) => {
        console.error('MediaRecorder error:', event);
        setState(prev => ({ 
          ...prev, 
          error: 'Recording error occurred',
          isRecording: false,
          isPaused: false,
        }));
        cleanup();
      };

      // 録音開始
      mediaRecorder.start(1000); // 1秒ごとにデータイベント
      startTimeRef.current = Date.now();
      
      setState(prev => ({ 
        ...prev, 
        isRecording: true,
        isPaused: false,
        duration: 0,
        blob: null,
      }));

    } catch (error: any) {
      console.error('Failed to start recording:', error);
      setState(prev => ({ 
        ...prev, 
        error: error.message || 'Failed to access microphone',
        isRecording: false,
      }));
    }
  }, [recordingConfig]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    cleanup();
  }, []);

  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause();
      setState(prev => ({ ...prev, isPaused: true }));
    }
  }, []);

  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume();
      setState(prev => ({ ...prev, isPaused: false }));
    }
  }, []);

  const cleanup = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  // コンポーネントアンマウント時のクリーンアップ
  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  return {
    state,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    cleanup,
  };
};