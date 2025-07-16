'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Users, 
  UserPlus, 
  Search, 
  Mail, 
  Calendar, 
  Shield,
  Edit,
  Trash2
} from 'lucide-react';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'counselor' | 'manager' | 'admin';
  clinic_id?: string;
  clinic_name?: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const { user: currentUser } = useAuth();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      
      // Since there's no dedicated users endpoint, we'll simulate user data
      // In a real implementation, you'd fetch from a users API endpoint
      const mockUsers: User[] = [
        {
          id: '1',
          email: 'counselor1@clinic.com',
          full_name: '田中 花子',
          role: 'counselor',
          clinic_id: 'clinic1',
          clinic_name: '美容クリニック東京',
          is_active: true,
          created_at: '2024-01-15T10:00:00Z',
          last_login: '2024-01-20T14:30:00Z'
        },
        {
          id: '2',
          email: 'manager1@clinic.com',
          full_name: '佐藤 太郎',
          role: 'manager',
          clinic_id: 'clinic1',
          clinic_name: '美容クリニック東京',
          is_active: true,
          created_at: '2024-01-10T09:00:00Z',
          last_login: '2024-01-20T16:45:00Z'
        },
        {
          id: '3',
          email: 'admin@system.com',
          full_name: '山田 システム',
          role: 'admin',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          last_login: '2024-01-20T09:15:00Z'
        }
      ];

      setUsers(mockUsers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800';
      case 'manager': return 'bg-blue-100 text-blue-800';
      case 'counselor': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'admin': return '管理者';
      case 'manager': return 'マネージャー';
      case 'counselor': return 'カウンセラー';
      default: return role;
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'なし';
    return new Date(dateString).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredUsers = users.filter(user =>
    user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.role.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const canManageUsers = currentUser?.role === 'admin' || currentUser?.role === 'manager';

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
          <Button onClick={fetchUsers}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">ユーザー管理</h1>
        {canManageUsers && (
          <Button>
            <UserPlus className="w-4 h-4 mr-2" />
            新規ユーザー追加
          </Button>
        )}
      </div>

      {/* Search and Filter */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center space-x-2">
            <Search className="w-4 h-4 text-gray-400" />
            <Input
              placeholder="ユーザー名、メールアドレス、ロールで検索..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1"
            />
          </div>
        </CardContent>
      </Card>

      {/* Users Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Users className="h-4 w-4 text-muted-foreground" />
              <span className="ml-2 text-sm font-medium">総ユーザー数</span>
            </div>
            <div className="text-2xl font-bold">{users.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Shield className="h-4 w-4 text-muted-foreground" />
              <span className="ml-2 text-sm font-medium">管理者</span>
            </div>
            <div className="text-2xl font-bold">
              {users.filter(u => u.role === 'admin').length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Users className="h-4 w-4 text-muted-foreground" />
              <span className="ml-2 text-sm font-medium">マネージャー</span>
            </div>
            <div className="text-2xl font-bold">
              {users.filter(u => u.role === 'manager').length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Users className="h-4 w-4 text-muted-foreground" />
              <span className="ml-2 text-sm font-medium">カウンセラー</span>
            </div>
            <div className="text-2xl font-bold">
              {users.filter(u => u.role === 'counselor').length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Users List */}
      <Card>
        <CardHeader>
          <CardTitle>ユーザー一覧</CardTitle>
        </CardHeader>
        <CardContent>
          {filteredUsers.length === 0 ? (
            <div className="text-center py-8">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">
                {searchTerm ? '検索条件に一致するユーザーがありません' : 'ユーザーがありません'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredUsers.map((user) => (
                <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <div className="font-medium">{user.full_name}</div>
                      <Badge className={getRoleColor(user.role)}>
                        {getRoleLabel(user.role)}
                      </Badge>
                      {!user.is_active && (
                        <Badge variant="secondary">無効</Badge>
                      )}
                    </div>
                    <div className="mt-1 space-y-1">
                      <div className="flex items-center text-sm text-gray-500">
                        <Mail className="w-4 h-4 mr-1" />
                        {user.email}
                      </div>
                      {user.clinic_name && (
                        <div className="text-sm text-gray-500">
                          所属: {user.clinic_name}
                        </div>
                      )}
                      <div className="flex items-center text-sm text-gray-500">
                        <Calendar className="w-4 h-4 mr-1" />
                        最終ログイン: {formatDate(user.last_login)}
                      </div>
                    </div>
                  </div>
                  {canManageUsers && (
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Edit className="w-4 h-4 mr-1" />
                        編集
                      </Button>
                      <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
                        <Trash2 className="w-4 h-4 mr-1" />
                        削除
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* User Management Notice */}
      {!canManageUsers && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center text-gray-500">
              <Shield className="w-8 h-8 mx-auto mb-2" />
              <p>ユーザー管理機能を使用するには管理者またはマネージャー権限が必要です。</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}