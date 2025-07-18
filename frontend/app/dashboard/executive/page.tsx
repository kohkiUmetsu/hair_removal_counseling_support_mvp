'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Calendar,
  Download,
  RefreshCw,
  Target,
  Award,
  AlertCircle,
  Clock
} from 'lucide-react';
import apiClient from '@/lib/axios';

interface ExecutiveDashboardData {
  overview: {
    total_sessions: number;
    total_counselors: number;
    total_clients: number;
    average_satisfaction: number;
    session_growth_rate: number;
    satisfaction_trend: number;
  };
  performance_metrics: {
    top_performing_counselors: Array<{
      counselor_id: string;
      counselor_name: string;
      average_satisfaction: number;
      total_sessions: number;
      improvement_score: number;
    }>;
    clinic_performance: Array<{
      clinic_id: string;
      clinic_name: string;
      average_satisfaction: number;
      total_sessions: number;
      engagement_score: number;
    }>;
  };
  operational_insights: {
    peak_hours: Array<{
      hour: number;
      session_count: number;
    }>;
    common_concerns: Array<{
      concern: string;
      frequency: number;
      satisfaction_impact: number;
    }>;
    success_factors: Array<{
      factor: string;
      correlation_score: number;
      description: string;
    }>;
  };
  alerts: Array<{
    id: string;
    type: 'warning' | 'error' | 'info';
    title: string;
    description: string;
    created_at: string;
  }>;
}

export default function ExecutiveDashboardPage() {
  const [dashboardData, setDashboardData] = useState<ExecutiveDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const { data } = await apiClient.get('/api/v1/dashboard/executive');
      setDashboardData(data);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const exportReport = async () => {
    try {
      const { data } = await apiClient.post('/api/v1/dashboard/export', {
        report_type: 'executive_summary',
        date_range: '30_days',
        format: 'pdf'
      });
      
      const { export_id } = data;
      alert(`レポート生成を開始しました。Export ID: ${export_id}`);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to export report');
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'error': return <AlertCircle className="w-4 h-4 text-red-600" />;
      case 'warning': return <AlertCircle className="w-4 h-4 text-yellow-600" />;
      default: return <AlertCircle className="w-4 h-4 text-blue-600" />;
    }
  };

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'error': return 'border-red-200 bg-red-50';
      case 'warning': return 'border-yellow-200 bg-yellow-50';
      default: return 'border-blue-200 bg-blue-50';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !dashboardData) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'データを読み込めませんでした'}</p>
          <Button onClick={fetchDashboardData}>
            <RefreshCw className="w-4 h-4 mr-2" />
            再試行
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">エグゼクティブダッシュボード</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchDashboardData}>
            <RefreshCw className="w-4 h-4 mr-2" />
            更新
          </Button>
          <Button onClick={exportReport}>
            <Download className="w-4 h-4 mr-2" />
            レポート出力
          </Button>
        </div>
      </div>

      {/* Alerts */}
      {dashboardData.alerts.length > 0 && (
        <div className="space-y-2">
          {dashboardData.alerts.slice(0, 3).map((alert) => (
            <div key={alert.id} className={`border rounded-lg p-3 ${getAlertColor(alert.type)}`}>
              <div className="flex items-start gap-3">
                {getAlertIcon(alert.type)}
                <div className="flex-1">
                  <h4 className="font-medium">{alert.title}</h4>
                  <p className="text-sm text-gray-600">{alert.description}</p>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(alert.created_at).toLocaleDateString('ja-JP')}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Overview Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">総セッション数</p>
                <p className="text-2xl font-bold">{dashboardData.overview.total_sessions.toLocaleString()}</p>
              </div>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="flex items-center text-xs text-muted-foreground mt-1">
              <TrendingUp className="w-3 h-3 mr-1" />
              前月比 +{dashboardData.overview.session_growth_rate.toFixed(1)}%
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">アクティブカウンセラー</p>
                <p className="text-2xl font-bold">{dashboardData.overview.total_counselors}</p>
              </div>
              <Users className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">総クライアント数</p>
                <p className="text-2xl font-bold">{dashboardData.overview.total_clients.toLocaleString()}</p>
              </div>
              <Users className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">平均満足度</p>
                <p className="text-2xl font-bold">{dashboardData.overview.average_satisfaction.toFixed(1)}</p>
              </div>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="flex items-center text-xs text-muted-foreground mt-1">
              <TrendingUp className="w-3 h-3 mr-1" />
              前月比 {dashboardData.overview.satisfaction_trend > 0 ? '+' : ''}{dashboardData.overview.satisfaction_trend.toFixed(1)}%
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="performance" className="space-y-4">
        <TabsList>
          <TabsTrigger value="performance">パフォーマンス</TabsTrigger>
          <TabsTrigger value="insights">インサイト</TabsTrigger>
          <TabsTrigger value="operations">オペレーション</TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Performing Counselors */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Award className="w-5 h-5 mr-2" />
                  トップパフォーマンスカウンセラー
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dashboardData.performance_metrics.top_performing_counselors.map((counselor, index) => (
                    <div key={counselor.counselor_id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                          index === 0 ? 'bg-yellow-100 text-yellow-800' :
                          index === 1 ? 'bg-gray-100 text-gray-800' :
                          index === 2 ? 'bg-orange-100 text-orange-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {index + 1}
                        </div>
                        <div>
                          <div className="font-medium">{counselor.counselor_name}</div>
                          <div className="text-sm text-gray-500">
                            {counselor.total_sessions} セッション
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">{counselor.average_satisfaction.toFixed(1)}</div>
                        <div className="text-sm text-gray-500">満足度</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Clinic Performance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Target className="w-5 h-5 mr-2" />
                  クリニック別パフォーマンス
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dashboardData.performance_metrics.clinic_performance.map((clinic) => (
                    <div key={clinic.clinic_id} className="p-3 border rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <div className="font-medium">{clinic.clinic_name}</div>
                        <div className="text-sm text-gray-500">
                          {clinic.total_sessions} セッション
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <div className="text-gray-500">満足度</div>
                          <div className="font-medium">{clinic.average_satisfaction.toFixed(1)}/10</div>
                        </div>
                        <div>
                          <div className="text-gray-500">エンゲージメント</div>
                          <div className="font-medium">{clinic.engagement_score.toFixed(1)}/10</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Common Concerns */}
            <Card>
              <CardHeader>
                <CardTitle>主要な関心事項</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {dashboardData.operational_insights.common_concerns.map((concern, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="font-medium">{concern.concern}</div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${(concern.frequency / Math.max(...dashboardData.operational_insights.common_concerns.map(c => c.frequency))) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="ml-4 text-sm text-gray-500">
                        {concern.frequency} 件
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Success Factors */}
            <Card>
              <CardHeader>
                <CardTitle>成功要因分析</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {dashboardData.operational_insights.success_factors.map((factor, index) => (
                    <div key={index} className="p-3 border rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <div className="font-medium">{factor.factor}</div>
                        <div className="text-sm font-medium text-green-600">
                          {(factor.correlation_score * 100).toFixed(0)}%
                        </div>
                      </div>
                      <p className="text-sm text-gray-600">{factor.description}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="operations" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Clock className="w-5 h-5 mr-2" />
                ピーク時間分析
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-12 gap-2">
                {Array.from({ length: 24 }, (_, hour) => {
                  const hourData = dashboardData.operational_insights.peak_hours.find(h => h.hour === hour);
                  const sessionCount = hourData?.session_count || 0;
                  const maxSessions = Math.max(...dashboardData.operational_insights.peak_hours.map(h => h.session_count));
                  const intensity = maxSessions > 0 ? (sessionCount / maxSessions) * 100 : 0;
                  
                  return (
                    <div key={hour} className="text-center">
                      <div className="text-xs text-gray-500 mb-1">{hour}:00</div>
                      <div 
                        className="w-full bg-blue-600 rounded" 
                        style={{ 
                          height: `${Math.max(20, intensity)}px`,
                          opacity: intensity > 0 ? Math.max(0.3, intensity / 100) : 0.1
                        }}
                      ></div>
                      <div className="text-xs text-gray-500 mt-1">{sessionCount}</div>
                    </div>
                  );
                })}
              </div>
              <div className="mt-4 text-sm text-gray-600">
                高さはセッション数を表し、濃い色ほど多くのセッションが行われています。
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}