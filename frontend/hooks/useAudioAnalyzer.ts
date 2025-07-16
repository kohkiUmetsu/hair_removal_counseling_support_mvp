import { useState, useEffect, useRef, useCallback } from 'react';

export const useAudioAnalyzer = (stream: MediaStream | null) => {
  const [audioLevel, setAudioLevel] = useState(0);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const microphoneRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const rafRef = useRef<number | null>(null);

  const updateAudioLevel = useCallback(() => {
    if (!analyserRef.current) return;

    const analyser = analyserRef.current;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    analyser.getByteFrequencyData(dataArray);
    
    // 平均音量を計算
    const average = dataArray.reduce((sum, value) => sum + value, 0) / bufferLength;
    const normalizedLevel = average / 255; // 0-1の範囲に正規化

    setAudioLevel(normalizedLevel);

    rafRef.current = requestAnimationFrame(updateAudioLevel);
  }, []);

  useEffect(() => {
    if (!stream) {
      // ストリームがない場合はクリーンアップ
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
      
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
      
      setAudioLevel(0);
      return;
    }

    const setupAudioAnalyzer = async () => {
      try {
        // AudioContext作成
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        audioContextRef.current = audioContext;

        // AnalyserNode作成
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        analyser.smoothingTimeConstant = 0.8;
        analyserRef.current = analyser;

        // MediaStreamSourceNode作成
        const microphone = audioContext.createMediaStreamSource(stream);
        microphoneRef.current = microphone;

        // 接続
        microphone.connect(analyser);

        // 音声レベル更新開始
        updateAudioLevel();

      } catch (error) {
        console.error('Failed to setup audio analyzer:', error);
      }
    };

    setupAudioAnalyzer();

    return () => {
      // クリーンアップ
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }

      if (microphoneRef.current) {
        microphoneRef.current.disconnect();
        microphoneRef.current = null;
      }

      if (analyserRef.current) {
        analyserRef.current.disconnect();
        analyserRef.current = null;
      }

      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
    };
  }, [stream, updateAudioLevel]);

  return audioLevel;
};

export default useAudioAnalyzer;