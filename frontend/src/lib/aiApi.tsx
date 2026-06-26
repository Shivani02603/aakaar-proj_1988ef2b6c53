import { API_BASE } from '../config';

export interface Session {
  id: string;
  name: string;
  created_at: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface AIQueryResponse {
  answer: string;
  sources: string[];
}

export const ingestFile = async (file: File, sessionId: string): Promise<{ chunks_indexed: number }> => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Unauthorized');

  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', sessionId);

  const response = await fetch(`${API_BASE}/api/ai/ingest`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to ingest file: ${errorText}`);
  }

  return response.json();
};

export const queryAI = async (query: string, sessionId: string): Promise<AIQueryResponse> => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Unauthorized');

  const response = await fetch(`${API_BASE}/api/ai/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ query, session_id: sessionId }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to query AI: ${errorText}`);
  }

  return response.json();
};

export const streamAnswer = async (
  query: string,
  sessionId: string,
  onToken: (token: string) => void,
  onDone: (citations: string[]) => void
): Promise<void> => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Unauthorized');

  const url = `${API_BASE}/api/ai/stream?query=${encodeURIComponent(query)}&session_id=${encodeURIComponent(sessionId)}`;
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok || !response.body) {
    const errorText = await response.text();
    throw new Error(`Failed to stream answer: ${errorText}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const lines = decoder.decode(value).split('\n').filter((line) => line.startsWith('data:'));
    for (const line of lines) {
      const data = JSON.parse(line.slice(5));
      if (data.token) onToken(data.token);
      if (data.done) {
        onDone(data.citations || []);
        return;
      }
    }
  }
};

export const getSessions = async (): Promise<Session[]> => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Unauthorized');

  const response = await fetch(`${API_BASE}/api/chat/sessions`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to fetch sessions: ${errorText}`);
  }

  return response.json();
};

export const createSession = async (name?: string): Promise<Session> => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Unauthorized');

  const response = await fetch(`${API_BASE}/api/chat/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ name }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to create session: ${errorText}`);
  }

  return response.json();
};

export const getMessages = async (sessionId: string): Promise<Message[]> => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Unauthorized');

  const response = await fetch(`${API_BASE}/api/chat/sessions/${sessionId}/messages`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to fetch messages: ${errorText}`);
  }

  return response.json();
};