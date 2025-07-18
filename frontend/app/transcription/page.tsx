'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  FileText, 
  RefreshCw, 
  Clock, 
  CheckCircle,
  XCircle,
  Loader,
  BarChart3
} from 'lucide-react';
import apiClient from '@/lib/axios';

interface TranscriptionTask {
  id: string;
  recording_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  created_at: string;
  completed_at?: string;
  error_message?: string;
  recording_info?: {
    filename: string;
    duration?: number;
  };
}

interface TranscriptionResult {
  id: string;
  task_id: string;
  text: string;
  confidence_score: number;
  word_count: number;
  segments: Array<{
    start: number;
    end: number;
    text: string;
    confidence: number;
  }>;
  created_at: string;
}

interface TranscriptionStats {
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  average_processing_time: number;
  total_words_transcribed: number;
  average_confidence: number;
}

export default function TranscriptionPage() {
  const [tasks, setTasks] = useState<TranscriptionTask[]>([]);
  const [stats, setStats] = useState<TranscriptionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedResult, setSelectedResult] = useState<TranscriptionResult | null>(null);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      // Fetch tasks and stats in parallel
      const [tasksResponse, statsResponse] = await Promise.all([
        apiClient.get('/api/v1/transcription/'),
        apiClient.get('/api/v1/transcription/stats')
      ]);

      setTasks(tasksResponse.data);
      setStats(statsResponse.data);

    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to load transcription data');
    } finally {
      setLoading(false);
    }
  };

  const retryTranscription = async (taskId: string) => {
    try {
      await apiClient.post(`/api/v1/transcription/retry/${taskId}`);
      fetchData();
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to retry transcription');
    }
  };

  const getTranscriptionResult = async (taskId: string) => {
    try {
      const { data } = await apiClient.get(`/api/v1/transcription/result/${taskId}`);
      setSelectedResult(data);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to get transcription result');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-600" />;
      case 'processing': return <Loader className="w-4 h-4 text-blue-600 animate-spin" />;
      default: return <Clock className="w-4 h-4 text-yellow-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      default: return 'bg-yellow-100 text-yellow-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">文字起こし管理</h1>
        <Button onClick={fetchData}>
          <RefreshCw className="w-4 h-4 mr-2" />
          更新
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <FileText className="h-4 w-4 text-muted-foreground" />
                <span className="ml-2 text-sm font-medium">総タスク数</span>
              </div>
              <div className="text-2xl font-bold">{stats.total_tasks}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
                <span className="ml-2 text-sm font-medium">完了率</span>
              </div>
              <div className="text-2xl font-bold">
                {stats.total_tasks > 0 ? Math.round((stats.completed_tasks / stats.total_tasks) * 100) : 0}%
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
                <span className="ml-2 text-sm font-medium">平均信頼度</span>
              </div>
              <div className="text-2xl font-bold">
                {(stats.average_confidence * 100).toFixed(1)}%
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <FileText className="h-4 w-4 text-muted-foreground" />
                <span className="ml-2 text-sm font-medium">総文字数</span>
              </div>
              <div className="text-2xl font-bold">
                {stats.total_words_transcribed.toLocaleString()}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs defaultValue="tasks" className="space-y-4">
        <TabsList>
          <TabsTrigger value="tasks">タスク一覧</TabsTrigger>
          <TabsTrigger value="results">文字起こし結果</TabsTrigger>
        </TabsList>

        <TabsContent value="tasks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>文字起こしタスク</CardTitle>
            </CardHeader>
            <CardContent>
              {tasks.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">文字起こしタスクがありません</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {tasks.map((task) => (
                    <div key={task.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          {getStatusIcon(task.status)}
                          <span className="font-medium">
                            {task.recording_info?.filename || `Recording ${task.recording_id}`}
                          </span>
                          <Badge className={getStatusColor(task.status)}>
                            {task.status}
                          </Badge>
                        </div>
                        <div className="mt-2 space-y-2">
                          <div className="text-sm text-gray-500">
                            開始日時: {formatDate(task.created_at)}
                            {task.completed_at && (
                              <span className="ml-4">
                                完了日時: {formatDate(task.completed_at)}
                              </span>
                            )}
                          </div>
                          {task.status === 'processing' && task.progress !== undefined && (
                            <div className="space-y-1">
                              <div className="flex justify-between text-sm">
                                <span>進捗</span>
                                <span>{task.progress}%</span>
                              </div>
                              <Progress value={task.progress} className="w-full" />
                            </div>
                          )}
                          {task.error_message && (
                            <div className="text-sm text-red-600">
                              エラー: {task.error_message}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {task.status === 'completed' && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => getTranscriptionResult(task.id)}
                          >
                            <FileText className="w-4 h-4 mr-1" />
                            結果表示
                          </Button>
                        )}
                        {task.status === 'failed' && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => retryTranscription(task.id)}
                          >
                            <RefreshCw className="w-4 h-4 mr-1" />
                            再実行
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results" className="space-y-4">
          {selectedResult ? (
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>文字起こし結果</CardTitle>
                  <Button variant="outline" onClick={() => setSelectedResult(null)}>
                    閉じる
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="font-medium">文字数:</span> {selectedResult.word_count}
                  </div>
                  <div>
                    <span className="font-medium">信頼度:</span> {(selectedResult.confidence_score * 100).toFixed(1)}%
                  </div>
                  <div>
                    <span className="font-medium">作成日時:</span> {formatDate(selectedResult.created_at)}
                  </div>
                </div>
                <div className="border-t pt-4">
                  <h4 className="font-medium mb-2">文字起こしテキスト</h4>
                  <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
                    <p className="whitespace-pre-wrap">{selectedResult.text}</p>
                  </div>
                </div>
                {selectedResult.segments.length > 0 && (
                  <div className="border-t pt-4">
                    <h4 className="font-medium mb-2">タイムスタンプ付きセグメント</h4>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {selectedResult.segments.map((segment, index) => (
                        <div key={index} className="flex gap-4 text-sm">
                          <div className="text-gray-500 min-w-[120px]">
                            {formatDuration(segment.start)} - {formatDuration(segment.end)}
                          </div>
                          <div className="flex-1">{segment.text}</div>
                          <div className="text-gray-500 min-w-[60px]">
                            {(segment.confidence * 100).toFixed(0)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-8">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">文字起こし結果を表示するには、タスク一覧から「結果表示」をクリックしてください</p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}