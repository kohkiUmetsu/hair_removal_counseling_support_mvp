'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Download, 
  Trash2, 
  Search, 
  Clock, 
  FileAudio, 
  Calendar,
  User,
  Volume2
} from 'lucide-react';
import apiClient from '@/lib/axios';

interface Recording {
  id: string;
  filename: string;
  file_size: number;
  duration?: number;
  upload_status: 'pending' | 'uploading' | 'completed' | 'failed';
  created_at: string;
  uploaded_by?: string;
  session_id?: string;
  file_key: string;
}

export default function RecordingsPage() {
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    fetchRecordings();
  }, []);

  const fetchRecordings = async () => {
    try {
      setLoading(true);
      const { data } = await apiClient.get('/api/v1/recordings/');
      setRecordings(data);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to load recordings');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (recordingId: string, filename: string) => {
    try {
      const { data } = await apiClient.get(`/api/v1/recordings/${recordingId}`);
      const { download_url } = data;
      
      // Create a temporary anchor element to trigger download
      const link = document.createElement('a');
      link.href = download_url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to download recording');
    }
  };

  const handleDelete = async (recordingId: string) => {
    if (!confirm('この録音ファイルを削除しますか？この操作は取り消せません。')) {
      return;
    }

    try {
      await apiClient.delete(`/api/v1/recordings/${recordingId}`);
      
      // Remove from local state
      setRecordings(prev => prev.filter(r => r.id !== recordingId));
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to delete recording');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'uploading': return 'bg-blue-100 text-blue-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
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

  const filteredRecordings = recordings.filter(recording =>
    recording.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
    recording.uploaded_by?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const canDelete = user?.role === 'admin' || user?.role === 'manager';

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
          <Button onClick={fetchRecordings}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">録音ファイル管理</h1>
        <Button onClick={fetchRecordings}>
          <Volume2 className="w-4 h-4 mr-2" />
          更新
        </Button>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center space-x-2">
            <Search className="w-4 h-4 text-gray-400" />
            <Input
              placeholder="ファイル名やアップロード者で検索..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1"
            />
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <FileAudio className="h-4 w-4 text-muted-foreground" />
              <span className="ml-2 text-sm font-medium">総録音数</span>
            </div>
            <div className="text-2xl font-bold">{recordings.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span className="ml-2 text-sm font-medium">完了</span>
            </div>
            <div className="text-2xl font-bold">
              {recordings.filter(r => r.upload_status === 'completed').length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Volume2 className="h-4 w-4 text-muted-foreground" />
              <span className="ml-2 text-sm font-medium">処理中</span>
            </div>
            <div className="text-2xl font-bold">
              {recordings.filter(r => r.upload_status === 'uploading').length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <FileAudio className="h-4 w-4 text-muted-foreground" />
              <span className="ml-2 text-sm font-medium">総サイズ</span>
            </div>
            <div className="text-2xl font-bold">
              {formatFileSize(recordings.reduce((sum, r) => sum + r.file_size, 0))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recordings List */}
      <Card>
        <CardHeader>
          <CardTitle>録音ファイル一覧</CardTitle>
        </CardHeader>
        <CardContent>
          {filteredRecordings.length === 0 ? (
            <div className="text-center py-8">
              <FileAudio className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">
                {searchTerm ? '検索条件に一致する録音ファイルがありません' : '録音ファイルがありません'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredRecordings.map((recording) => (
                <div key={recording.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <FileAudio className="w-5 h-5 text-gray-400" />
                      <div className="font-medium">{recording.filename}</div>
                      <Badge className={getStatusColor(recording.upload_status)}>
                        {recording.upload_status}
                      </Badge>
                    </div>
                    <div className="mt-1 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-500">
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        {formatDuration(recording.duration)}
                      </div>
                      <div>
                        サイズ: {formatFileSize(recording.file_size)}
                      </div>
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        {formatDate(recording.created_at)}
                      </div>
                      {recording.uploaded_by && (
                        <div className="flex items-center">
                          <User className="w-4 h-4 mr-1" />
                          {recording.uploaded_by}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {recording.upload_status === 'completed' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDownload(recording.id, recording.filename)}
                      >
                        <Download className="w-4 h-4 mr-1" />
                        DL
                      </Button>
                    )}
                    {canDelete && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-red-600 hover:text-red-700"
                        onClick={() => handleDelete(recording.id)}
                      >
                        <Trash2 className="w-4 h-4 mr-1" />
                        削除
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}