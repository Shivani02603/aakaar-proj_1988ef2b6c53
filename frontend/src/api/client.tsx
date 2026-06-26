import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
});

api.interceptors.request.use((config: AxiosRequestConfig) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`,
    };
  }
  return config;
});

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface Document {
  id: string;
  user_id: string;
  filename: string;
  file_path: string;
  file_size: number;
  status: string;
  created_at: string;
  processed_at: string | null;
}

export interface ChatSession {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: string;
  content: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export const login = (data: LoginRequest) => api.post('/api/auth/login', data);

export const register = (data: RegisterRequest) => api.post('/api/auth/register', data);

export const uploadDocument = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post<Document>('/api/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const listDocuments = () => api.get<Document[]>('/api/documents');

export const ingestDocuments = () => api.post('/api/ai/ingest');

export const aiQuery = (query: string) =>
  api.post('/api/ai/query', { query });

export const createChatSession = (title: string) =>
  api.post<ChatSession>('/api/chat/sessions', { title });

export const listChatSessions = () =>
  api.get<ChatSession[]>('/api/chat/sessions');

export const getChatMessages = (sessionId: string) =>
  api.get<ChatMessage[]>(`/api/chat/sessions/${sessionId}/messages`);

export const streamAnswer = (query: string, sessionId: string) =>
  api.post('/api/stream/answer', { query, session_id: sessionId });