export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: 'counselor' | 'manager' | 'admin';
  is_active: boolean;
  clinic_id?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
  isAuthenticated: boolean;
}

export interface TokenPayload {
  sub: string;
  exp: number;
  type: string;
}