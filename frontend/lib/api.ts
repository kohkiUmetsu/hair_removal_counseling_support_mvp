import axios, { AxiosResponse, AxiosError } from 'axios';
import { ApiResponse } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Generic API call wrapper
export async function apiCall<T>(
  requestFn: () => Promise<AxiosResponse<T>>
): Promise<ApiResponse<T>> {
  try {
    const response = await requestFn();
    return {
      data: response.data,
      status: response.status,
    };
  } catch (error) {
    if (axios.isAxiosError(error)) {
      return {
        error: error.response?.data?.detail || error.message,
        status: error.response?.status || 500,
      };
    }
    return {
      error: 'An unexpected error occurred',
      status: 500,
    };
  }
}

// Auth API calls
export const authApi = {
  login: (username: string, password: string) =>
    apiCall(() => 
      api.post('/api/v1/auth/login', { username, password })
    ),
  
  getMe: () =>
    apiCall(() => 
      api.get('/api/v1/auth/me')
    ),
  
  testToken: () =>
    apiCall(() => 
      api.post('/api/v1/auth/test-token')
    ),
};

// Sessions API calls
export const sessionsApi = {
  getSessions: (skip = 0, limit = 100) =>
    apiCall(() => 
      api.get(`/api/v1/sessions/?skip=${skip}&limit=${limit}`)
    ),
  
  getSession: (id: string) =>
    apiCall(() => 
      api.get(`/api/v1/sessions/${id}`)
    ),
  
  createSession: (sessionData: Record<string, unknown>) =>
    apiCall(() => 
      api.post('/api/v1/sessions/', sessionData)
    ),
  
  updateSession: (id: string, sessionData: Record<string, unknown>) =>
    apiCall(() => 
      api.put(`/api/v1/sessions/${id}`, sessionData)
    ),
  
  uploadRecording: (id: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiCall(() => 
      api.post(`/api/v1/sessions/${id}/upload-recording`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    );
  },
};

// Analysis API calls
export const analysisApi = {
  startTranscription: (sessionId: string) =>
    apiCall(() => 
      api.post(`/api/v1/analysis/${sessionId}/transcribe`)
    ),
  
  startAnalysis: (sessionId: string) =>
    apiCall(() => 
      api.post(`/api/v1/analysis/${sessionId}/analyze`)
    ),
  
  getAnalysisResults: (sessionId: string) =>
    apiCall(() => 
      api.get(`/api/v1/analysis/${sessionId}/analysis`)
    ),
};