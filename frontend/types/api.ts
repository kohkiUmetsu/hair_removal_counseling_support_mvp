export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface Session {
  id: string;
  customer_id: string;
  counselor_id: string;
  session_date: string;
  duration_minutes?: number;
  notes?: string;
  status: 'recorded' | 'transcribed' | 'analyzed' | 'completed';
  recording_url?: string;
  transcript_text?: string;
  analysis_results?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface SessionWithRelations extends Session {
  customer_name: string;
  counselor_name: string;
}

export interface Customer {
  id: string;
  name: string;
  phone?: string;
  email?: string;
  clinic_id: string;
  created_at: string;
  updated_at: string;
}

export interface Clinic {
  id: string;
  name: string;
  address?: string;
  phone?: string;
  created_at: string;
  updated_at: string;
}