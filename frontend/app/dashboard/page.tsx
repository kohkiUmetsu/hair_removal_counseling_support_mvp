'use client';

import { useAuth } from '@/lib/auth';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3, Mic, Users, FileText } from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuth();

  const stats = [
    {
      title: '今月のセッション数',
      value: '24',
      description: '前月比 +12%',
      icon: Mic,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: '分析完了',
      value: '18',
      description: '今月処理済み',
      icon: BarChart3,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: '処理待ち',
      value: '6',
      description: '録音・文字起こし待ち',
      icon: FileText,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
    {
      title: '担当顧客数',
      value: '42',
      description: 'アクティブな顧客',
      icon: Users,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          ダッシュボード
        </h1>
        <p className="text-gray-600">
          こんにちは、{user?.full_name}さん
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  {stat.description}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>最近のセッション</CardTitle>
            <CardDescription>
              最新の5件のカウンセリングセッション
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex items-center space-x-4">
                  <div className="flex-1 space-y-1">
                    <p className="text-sm font-medium leading-none">
                      セッション #{i}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {new Date().toLocaleDateString('ja-JP')}
                    </p>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    30分
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>分析サマリー</CardTitle>
            <CardDescription>
              今月の分析結果概要
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm">平均満足度</span>
                <span className="text-lg font-semibold">8.2/10</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">平均セッション時間</span>
                <span className="text-lg font-semibold">28分</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">主要トピック</span>
                <span className="text-sm text-muted-foreground">脱毛相談</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}