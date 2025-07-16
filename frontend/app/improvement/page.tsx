'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/lib/auth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { 
  Lightbulb, 
  TrendingUp, 
  Star, 
  MessageSquare, 
  RefreshCw,
  FileText,
  Target,
  Award
} from 'lucide-react';

interface ImprovementSuggestion {
  id: string;
  analysis_id: string;
  session_info?: {
    client_name: string;
    session_date: string;
  };
  suggestions: Array<{
    category: string;
    priority: 'high' | 'medium' | 'low';
    suggestion: string;
    impact_score: number;
    implementation_difficulty: number;
  }>;
  created_at: string;
}

interface SuccessPattern {
  id: string;
  pattern_name: string;
  description: string;
  success_rate: number;
  usage_count: number;
  keywords: string[];
  counselor_feedback_score: number;
}

interface PerformanceTrend {
  counselor_id: string;
  counselor_name: string;
  time_period: string;
  satisfaction_trend: number;
  engagement_trend: number;
  improvement_areas: string[];
  strengths: string[];
}

export default function ImprovementPage() {
  const [suggestions] = useState<ImprovementSuggestion[]>([]);
  const [successPatterns, setSuccessPatterns] = useState<SuccessPattern[]>([]);
  const [performanceTrends, setPerformanceTrends] = useState<PerformanceTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedbackText, setFeedbackText] = useState('');
  const [scriptPrompt, setScriptPrompt] = useState('');
  const [generatedScript, setGeneratedScript] = useState('');
  const { user } = useAuth();

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      // Fetch success patterns
      const patternsResponse = await fetch('/api/v1/improvement/success-patterns', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (patternsResponse.ok) {
        const patternsData = await patternsResponse.json();
        setSuccessPatterns(patternsData);
      }

      // Fetch performance trends for current user if counselor
      if (user?.role === 'counselor') {
        const trendsResponse = await fetch(`/api/v1/improvement/performance-trends/${user.id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (trendsResponse.ok) {
          const trendsData = await trendsResponse.json();
          setPerformanceTrends([trendsData]);
        }
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load improvement data');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const generateScript = async () => {
    if (!scriptPrompt.trim()) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/improvement/generate-script', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          prompt: scriptPrompt,
          context: 'counseling_session',
          tone: 'professional_friendly'
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate script');
      }

      const { script } = await response.json();
      setGeneratedScript(script);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate script');
    }
  };

  const submitFeedback = async () => {
    if (!feedbackText.trim()) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/improvement/feedback', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          feedback_text: feedbackText,
          feedback_type: 'general',
          rating: 5
        })
      });

      if (!response.ok) {
        throw new Error('Failed to submit feedback');
      }

      setFeedbackText('');
      alert('フィードバックを送信しました');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit feedback');
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
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
        <h1 className="text-3xl font-bold text-gray-900">改善提案・パフォーマンス</h1>
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

      <Tabs defaultValue="patterns" className="space-y-4">
        <TabsList>
          <TabsTrigger value="patterns">成功パターン</TabsTrigger>
          <TabsTrigger value="suggestions">改善提案</TabsTrigger>
          <TabsTrigger value="performance">パフォーマンス</TabsTrigger>
          <TabsTrigger value="tools">支援ツール</TabsTrigger>
        </TabsList>

        <TabsContent value="patterns" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Award className="w-5 h-5 mr-2" />
                成功パターン分析
              </CardTitle>
            </CardHeader>
            <CardContent>
              {successPatterns.length === 0 ? (
                <div className="text-center py-8">
                  <Award className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">成功パターンデータがありません</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {successPatterns.map((pattern) => (
                    <div key={pattern.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <h3 className="font-medium text-lg">{pattern.pattern_name}</h3>
                        <div className="flex items-center gap-2">
                          <Badge className="bg-green-100 text-green-800">
                            成功率 {(pattern.success_rate * 100).toFixed(1)}%
                          </Badge>
                          <Badge variant="secondary">
                            使用回数 {pattern.usage_count}
                          </Badge>
                        </div>
                      </div>
                      <p className="text-gray-600 mb-3">{pattern.description}</p>
                      <div className="flex flex-wrap gap-2 mb-3">
                        {pattern.keywords.map((keyword, index) => (
                          <Badge key={index} variant="outline">
                            {keyword}
                          </Badge>
                        ))}
                      </div>
                      <div className="flex items-center">
                        <Star className="w-4 h-4 text-yellow-500 mr-1" />
                        <span className="text-sm">
                          カウンセラー評価: {pattern.counselor_feedback_score.toFixed(1)}/5
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="suggestions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Lightbulb className="w-5 h-5 mr-2" />
                個別改善提案
              </CardTitle>
            </CardHeader>
            <CardContent>
              {suggestions.length === 0 ? (
                <div className="text-center py-8">
                  <Lightbulb className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">改善提案がありません</p>
                  <p className="text-sm text-gray-400 mt-2">
                    分析が完了したセッションから自動的に提案が生成されます
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {suggestions.map((suggestion) => (
                    <div key={suggestion.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-center mb-3">
                        <div>
                          <h3 className="font-medium">
                            {suggestion.session_info?.client_name || 'セッション'} の改善提案
                          </h3>
                          <span className="text-sm text-gray-500">
                            {formatDate(suggestion.created_at)}
                          </span>
                        </div>
                      </div>
                      <div className="space-y-3">
                        {suggestion.suggestions.map((item, index) => (
                          <div key={index} className="border-l-4 border-blue-500 pl-4">
                            <div className="flex justify-between items-start mb-2">
                              <div className="flex items-center gap-2">
                                <span className="font-medium">{item.category}</span>
                                <Badge className={getPriorityColor(item.priority)}>
                                  {item.priority}
                                </Badge>
                              </div>
                              <div className="text-sm text-gray-500">
                                影響度: {item.impact_score}/10 | 難易度: {item.implementation_difficulty}/10
                              </div>
                            </div>
                            <p className="text-sm">{item.suggestion}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="w-5 h-5 mr-2" />
                パフォーマンストレンド
              </CardTitle>
            </CardHeader>
            <CardContent>
              {performanceTrends.length === 0 ? (
                <div className="text-center py-8">
                  <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">パフォーマンスデータがありません</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {performanceTrends.map((trend, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <h3 className="font-medium mb-4">{trend.counselor_name} - {trend.time_period}</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-medium">満足度トレンド</span>
                            <span className={`text-sm ${trend.satisfaction_trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {trend.satisfaction_trend > 0 ? '+' : ''}{trend.satisfaction_trend.toFixed(1)}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${trend.satisfaction_trend > 0 ? 'bg-green-600' : 'bg-red-600'}`}
                              style={{ width: `${Math.abs(trend.satisfaction_trend)}%` }}
                            ></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-medium">エンゲージメントトレンド</span>
                            <span className={`text-sm ${trend.engagement_trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {trend.engagement_trend > 0 ? '+' : ''}{trend.engagement_trend.toFixed(1)}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${trend.engagement_trend > 0 ? 'bg-green-600' : 'bg-red-600'}`}
                              style={{ width: `${Math.abs(trend.engagement_trend)}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h4 className="font-medium mb-2 text-green-700">強み</h4>
                          <ul className="list-disc list-inside text-sm space-y-1">
                            {trend.strengths.map((strength, idx) => (
                              <li key={idx}>{strength}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="font-medium mb-2 text-orange-700">改善エリア</h4>
                          <ul className="list-disc list-inside text-sm space-y-1">
                            {trend.improvement_areas.map((area, idx) => (
                              <li key={idx}>{area}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tools" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Script Generation Tool */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  スクリプト生成ツール
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="scriptPrompt">シチュエーションを入力してください</Label>
                  <Textarea
                    id="scriptPrompt"
                    placeholder="例: 施術の効果について不安を感じている顧客への対応"
                    value={scriptPrompt}
                    onChange={(e) => setScriptPrompt(e.target.value)}
                    rows={3}
                  />
                </div>
                <Button onClick={generateScript} disabled={!scriptPrompt.trim()}>
                  <Target className="w-4 h-4 mr-2" />
                  スクリプト生成
                </Button>
                {generatedScript && (
                  <div className="border-t pt-4">
                    <h4 className="font-medium mb-2">生成されたスクリプト</h4>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="whitespace-pre-wrap text-sm">{generatedScript}</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Feedback Tool */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <MessageSquare className="w-5 h-5 mr-2" />
                  フィードバック送信
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="feedback">システムへのフィードバック</Label>
                  <Textarea
                    id="feedback"
                    placeholder="改善提案の精度、システムの使いやすさなどについてお聞かせください"
                    value={feedbackText}
                    onChange={(e) => setFeedbackText(e.target.value)}
                    rows={4}
                  />
                </div>
                <Button onClick={submitFeedback} disabled={!feedbackText.trim()}>
                  <MessageSquare className="w-4 h-4 mr-2" />
                  フィードバック送信
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}