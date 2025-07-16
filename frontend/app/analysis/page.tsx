'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BarChart3, TrendingUp, FileText, Download, RefreshCw, Calendar, Play } from 'lucide-react';

interface AnalysisTask {
  id: string;
  session_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  analysis_type: 'quick' | 'comprehensive' | 'specific';
  created_at: string;
  completed_at?: string;
  session_info?: {
    client_name: string;
    session_date: string;
  };
}

interface AnalysisResult {
  id: string;
  session_id: string;
  satisfaction_score: number;
  engagement_level: number;
  concern_areas: string[];
  recommendations: string[];
  sentiment_analysis: {
    positive: number;
    negative: number;
    neutral: number;
  };
  key_insights: string[];
  created_at: string;
}

interface AnalysisStats {
  total_analyses: number;
  avg_satisfaction_score: number;
  avg_engagement_level: number;
  most_common_concerns: string[];
  trend_data: {
    date: string;
    satisfaction: number;
    engagement: number;
  }[];
}

export default function AnalysisPage() {
  const [tasks, setTasks] = useState<AnalysisTask[]>([]);
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [stats, setStats] = useState<AnalysisStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalysisData();
  }, []);

  const fetchAnalysisData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      // Fetch analysis tasks
      const tasksResponse = await fetch('/api/v1/ai-analysis/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      // Fetch analysis statistics
      const statsResponse = await fetch('/api/v1/ai-analysis/stats', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      let tasksData: AnalysisTask[] = [];

      if (tasksResponse.ok) {
        tasksData = await tasksResponse.json();
        setTasks(tasksData);
      }

      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }

      // Fetch completed analysis results for display
      const completedTasks = tasksData.filter((task: AnalysisTask) => task.status === 'completed');
      if (completedTasks.length > 0) {
        const resultsPromises = completedTasks.slice(0, 5).map(async (task: AnalysisTask) => {
          try {
            const resultResponse = await fetch(`/api/v1/ai-analysis/result/${task.id}`, {
              headers: { 'Authorization': `Bearer ${token}` }
            });
            if (resultResponse.ok) {
              return await resultResponse.json();
            }
          } catch {
            return null;
          }
        });
        
        const resultsData = await Promise.all(resultsPromises);
        setResults(resultsData.filter(Boolean));
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analysis data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={fetchAnalysisData}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">分析結果</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchAnalysisData}>
            <RefreshCw className="w-4 h-4 mr-2" />
            更新
          </Button>
          <Button>
            <Play className="w-4 h-4 mr-2" />
            新規分析開始
          </Button>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            レポート出力
          </Button>
        </div>
      </div>

      {/* Statistics Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
                <span className="ml-2 text-sm font-medium">総分析数</span>
              </div>
              <div className="text-2xl font-bold">{stats.total_analyses}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
                <span className="ml-2 text-sm font-medium">平均満足度</span>
              </div>
              <div className="text-2xl font-bold">{stats.avg_satisfaction_score.toFixed(1)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
                <span className="ml-2 text-sm font-medium">平均エンゲージメント</span>
              </div>
              <div className="text-2xl font-bold">{stats.avg_engagement_level.toFixed(1)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <FileText className="h-4 w-4 text-muted-foreground" />
                <span className="ml-2 text-sm font-medium">主要関心事項</span>
              </div>
              <div className="text-sm text-muted-foreground">
                {stats.most_common_concerns.slice(0, 2).join(', ')}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs defaultValue="tasks" className="space-y-4">
        <TabsList>
          <TabsTrigger value="tasks">分析タスク</TabsTrigger>
          <TabsTrigger value="results">分析結果</TabsTrigger>
          <TabsTrigger value="trends">トレンド分析</TabsTrigger>
        </TabsList>

        <TabsContent value="tasks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>分析タスク一覧</CardTitle>
            </CardHeader>
            <CardContent>
              {tasks.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">分析タスクがありません</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {tasks.map((task) => (
                    <div key={task.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <Badge className={getStatusColor(task.status)}>
                            {task.status}
                          </Badge>
                          <span className="text-sm font-medium">
                            {task.session_info?.client_name || `Session ${task.session_id}`}
                          </span>
                          <span className="text-sm text-gray-500">
                            {task.analysis_type}
                          </span>
                        </div>
                        <div className="mt-1 flex items-center text-sm text-gray-500">
                          <Calendar className="w-4 h-4 mr-1" />
                          {formatDate(task.created_at)}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {task.status === 'completed' && (
                          <Button variant="outline" size="sm">
                            結果表示
                          </Button>
                        )}
                        {task.status === 'failed' && (
                          <Button variant="outline" size="sm">
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
          <Card>
            <CardHeader>
              <CardTitle>分析結果詳細</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {results.length === 0 ? (
                  <div className="text-center py-8">
                    <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">分析結果がありません</p>
                  </div>
                ) : (
                  results.map((result) => (
                    <div key={result.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-4">
                        <h3 className="font-medium">分析ID: {result.id}</h3>
                        <span className="text-sm text-gray-500">
                          {formatDate(result.created_at)}
                        </span>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div className="flex items-center">
                          <span className="text-sm font-medium mr-2">満足度スコア:</span>
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ width: `${result.satisfaction_score * 10}%` }}
                            ></div>
                          </div>
                          <span className="ml-2 text-sm">{result.satisfaction_score}/10</span>
                        </div>
                        <div className="flex items-center">
                          <span className="text-sm font-medium mr-2">エンゲージメント:</span>
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-green-600 h-2 rounded-full" 
                              style={{ width: `${result.engagement_level * 10}%` }}
                            ></div>
                          </div>
                          <span className="ml-2 text-sm">{result.engagement_level}/10</span>
                        </div>
                      </div>
                      {result.concern_areas.length > 0 && (
                        <div className="mb-4">
                          <h4 className="font-medium mb-2">関心事項</h4>
                          <div className="flex flex-wrap gap-2">
                            {result.concern_areas.map((concern, index) => (
                              <Badge key={index} variant="secondary">
                                {concern}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      {result.recommendations.length > 0 && (
                        <div className="mb-4">
                          <h4 className="font-medium mb-2">推奨事項</h4>
                          <ul className="list-disc list-inside space-y-1 text-sm">
                            {result.recommendations.map((rec, index) => (
                              <li key={index}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      <div className="grid grid-cols-3 gap-4 text-center text-sm">
                        <div>
                          <div className="font-medium">ポジティブ</div>
                          <div>{(result.sentiment_analysis.positive * 100).toFixed(1)}%</div>
                        </div>
                        <div>
                          <div className="font-medium">ニュートラル</div>
                          <div>{(result.sentiment_analysis.neutral * 100).toFixed(1)}%</div>
                        </div>
                        <div>
                          <div className="font-medium">ネガティブ</div>
                          <div>{(result.sentiment_analysis.negative * 100).toFixed(1)}%</div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>トレンド分析</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">トレンド分析機能は開発中です</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}