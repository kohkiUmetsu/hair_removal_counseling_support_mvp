'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ArrowLeft,
  User, 
  Calendar, 
  FileAudio, 
  FileText, 
  BarChart3,
  Edit,
  Play,
  Upload
} from 'lucide-react';

interface SessionDetail {
  id: string;
  client_name: string;
  client_email: string;
  counselor_id: string;
  counselor_name?: string;
  session_date: string;
  status: 'scheduled' | 'recorded' | 'transcribed' | 'analyzed' | 'completed';
  duration?: number;
  clinic_id: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  recording?: {
    id: string;
    filename: string;
    file_size: number;
    duration?: number;
    status: string;
  };
  transcription?: {
    id: string;
    text: string;
    confidence_score: number;
    word_count: number;
  };
  analysis?: {
    id: string;
    satisfaction_score: number;
    engagement_level: number;
    concern_areas: string[];
    recommendations: string[];
  };
}

export default function SessionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.id as string;
  const [session, setSession] = useState<SessionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (sessionId) {
      fetchSessionDetail();
    }
  }, [sessionId]);

  const fetchSessionDetail = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/sessions/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch session details');
      }

      const data = await response.json();
      setSession(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load session details');
    } finally {
      setLoading(false);
    }
  };

  const startTranscription = async () => {
    if (!session?.recording) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/transcription/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          recording_id: session.recording.id,
          language: 'ja',
          include_timestamps: true
        })
      });

      if (!response.ok) {
        throw new Error('Failed to start transcription');
      }

      alert('文字起こしを開始しました');
      fetchSessionDetail();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start transcription');
    }
  };

  const startAnalysis = async () => {
    if (!session?.transcription) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/ai-analysis/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: sessionId,
          analysis_type: 'comprehensive',
          include_sentiment: true,
          include_recommendations: true
        })
      });

      if (!response.ok) {
        throw new Error('Failed to start analysis');
      }

      alert('AI分析を開始しました');
      fetchSessionDetail();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start analysis');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'recorded': return 'bg-yellow-100 text-yellow-800';
      case 'transcribed': return 'bg-purple-100 text-purple-800';
      case 'analyzed': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'セッションが見つかりません'}</p>
          <Button onClick={() => router.push('/sessions')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            セッション一覧に戻る
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={() => router.push('/sessions')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            戻る
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{session.client_name}のセッション</h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge className={getStatusColor(session.status)}>
                {session.status}
              </Badge>
              <span className="text-gray-500">{formatDate(session.session_date)}</span>
            </div>
          </div>
        </div>
        <Button variant="outline">
          <Edit className="w-4 h-4 mr-2" />
          編集
        </Button>
      </div>

      {/* Session Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center mb-2">
              <User className="w-5 h-5 text-gray-400 mr-2" />
              <span className="font-medium">クライアント情報</span>
            </div>
            <div className="space-y-1 text-sm">
              <div><strong>名前:</strong> {session.client_name}</div>
              <div><strong>メール:</strong> {session.client_email}</div>
              <div><strong>カウンセラー:</strong> {session.counselor_name || 'N/A'}</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center mb-2">
              <Calendar className="w-5 h-5 text-gray-400 mr-2" />
              <span className="font-medium">セッション情報</span>
            </div>
            <div className="space-y-1 text-sm">
              <div><strong>日時:</strong> {formatDate(session.session_date)}</div>
              <div><strong>時間:</strong> {formatDuration(session.duration)}</div>
              <div><strong>ステータス:</strong> {session.status}</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center mb-2">
              <BarChart3 className="w-5 h-5 text-gray-400 mr-2" />
              <span className="font-medium">処理状況</span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>録音:</span>
                <span className={session.recording ? 'text-green-600' : 'text-gray-400'}>
                  {session.recording ? '完了' : '未完了'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>文字起こし:</span>
                <span className={session.transcription ? 'text-green-600' : 'text-gray-400'}>
                  {session.transcription ? '完了' : '未完了'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>AI分析:</span>
                <span className={session.analysis ? 'text-green-600' : 'text-gray-400'}>
                  {session.analysis ? '完了' : '未完了'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Information */}
      <Tabs defaultValue="recording" className="space-y-4">
        <TabsList>
          <TabsTrigger value="recording">録音</TabsTrigger>
          <TabsTrigger value="transcription">文字起こし</TabsTrigger>
          <TabsTrigger value="analysis">分析結果</TabsTrigger>
          <TabsTrigger value="notes">メモ</TabsTrigger>
        </TabsList>

        <TabsContent value="recording" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center">
                  <FileAudio className="w-5 h-5 mr-2" />
                  録音ファイル
                </span>
                {!session.recording && (
                  <Button size="sm">
                    <Upload className="w-4 h-4 mr-1" />
                    録音アップロード
                  </Button>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {session.recording ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="font-medium">ファイル名:</span>
                      <div>{session.recording.filename}</div>
                    </div>
                    <div>
                      <span className="font-medium">サイズ:</span>
                      <div>{formatFileSize(session.recording.file_size)}</div>
                    </div>
                    <div>
                      <span className="font-medium">時間:</span>
                      <div>{formatDuration(session.recording.duration)}</div>
                    </div>
                    <div>
                      <span className="font-medium">ステータス:</span>
                      <div>{session.recording.status}</div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <Play className="w-4 h-4 mr-1" />
                      再生
                    </Button>
                    {!session.transcription && (
                      <Button size="sm" onClick={startTranscription}>
                        <FileText className="w-4 h-4 mr-1" />
                        文字起こし開始
                      </Button>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileAudio className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">録音ファイルがアップロードされていません</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="transcription" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  文字起こし結果
                </span>
                {session.transcription && !session.analysis && (
                  <Button size="sm" onClick={startAnalysis}>
                    <BarChart3 className="w-4 h-4 mr-1" />
                    AI分析開始
                  </Button>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {session.transcription ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="font-medium">文字数:</span> {session.transcription.word_count}
                    </div>
                    <div>
                      <span className="font-medium">信頼度:</span> {(session.transcription.confidence_score * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div className="border-t pt-4">
                    <h4 className="font-medium mb-2">文字起こしテキスト</h4>
                    <div className="bg-gray-50 p-4 rounded-lg max-h-64 overflow-y-auto">
                      <p className="whitespace-pre-wrap text-sm">{session.transcription.text}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">文字起こしが完了していません</p>
                  {session.recording && (
                    <Button className="mt-4" onClick={startTranscription}>
                      <FileText className="w-4 h-4 mr-2" />
                      文字起こしを開始
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                AI分析結果
              </CardTitle>
            </CardHeader>
            <CardContent>
              {session.analysis ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium">満足度スコア</span>
                        <span>{session.analysis.satisfaction_score}/10</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${session.analysis.satisfaction_score * 10}%` }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium">エンゲージメントレベル</span>
                        <span>{session.analysis.engagement_level}/10</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${session.analysis.engagement_level * 10}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                  
                  {session.analysis.concern_areas.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">主な関心事項</h4>
                      <div className="flex flex-wrap gap-2">
                        {session.analysis.concern_areas.map((concern, index) => (
                          <Badge key={index} variant="secondary">
                            {concern}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {session.analysis.recommendations.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">改善提案</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm">
                        {session.analysis.recommendations.map((rec, index) => (
                          <li key={index}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">AI分析が完了していません</p>
                  {session.transcription && (
                    <Button className="mt-4" onClick={startAnalysis}>
                      <BarChart3 className="w-4 h-4 mr-2" />
                      AI分析を開始
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>セッションメモ</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">メモ機能は開発中です</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}