'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface SessionSidebarProps {
  onSelectSession: (id: string) => void;
  activeSessionId?: string;
}

function SessionSidebar({ onSelectSession, activeSessionId }: SessionSidebarProps) {
  const [sessions, setSessions] = useState<{ id: string; title: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSessions = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/chat/sessions', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!response.ok) {
          throw new Error('Failed to fetch sessions');
        }
        const data = await response.json();
        setSessions(data);
      } catch (err) {
        setError('Error loading sessions');
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, []);

  return (
    <div className="flex flex-col h-full border-r border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold">Sessions</h2>
      </div>
      {loading && <div className="p-4">Loading...</div>}
      {error && <div className="p-4 text-red-500">{error}</div>}
      <ul className="flex-1 overflow-y-auto">
        {sessions.map((session) => (
          <li
            key={session.id}
            className={`p-4 cursor-pointer ${
              activeSessionId === session.id ? 'bg-blue-100' : ''
            }`}
            onClick={() => onSelectSession(session.id)}
          >
            {session.title}
          </li>
        ))}
      </ul>
    </div>
  );
}

function DocumentUploader() {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) return;

    const file = event.target.files[0];
    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload document');
      }
    } catch (err) {
      setError('Error uploading document');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-4 border-t border-gray-200">
      <h2 className="text-lg font-semibold mb-2">Upload Document</h2>
      <input
        type="file"
        onChange={handleFileUpload}
        className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
      />
      {uploading && <div className="mt-2 text-blue-500">Uploading...</div>}
      {error && <div className="mt-2 text-red-500">{error}</div>}
    </div>
  );
}

function ChatWindow({ activeSessionId }: { activeSessionId: string | null }) {
  const [messages, setMessages] = useState<{ id: string; role: string; content: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!activeSessionId) return;

    const fetchMessages = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/chat/sessions/${activeSessionId}/messages`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!response.ok) {
          throw new Error('Failed to fetch messages');
        }
        const data = await response.json();
        setMessages(data);
      } catch (err) {
        setError('Error loading messages');
      } finally {
        setLoading(false);
      }
    };

    fetchMessages();
  }, [activeSessionId]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4">
        {loading && <div>Loading messages...</div>}
        {error && <div className="text-red-500">{error}</div>}
        {messages.map((message) => (
          <div key={message.id} className={`mb-4 ${message.role === 'assistant' ? 'text-left' : 'text-right'}`}>
            <div className={`inline-block p-2 rounded-lg ${message.role === 'assistant' ? 'bg-gray-200' : 'bg-blue-500 text-white'}`}>
              {message.content}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ChatPage() {
  const router = useRouter();
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  const handleSelectSession = (id: string) => {
    setActiveSessionId(id);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="flex items-center justify-between p-4 bg-gray-800 text-white">
        <h1 className="text-lg font-semibold">Aakaar Project</h1>
        <button onClick={handleLogout} className="px-4 py-2 bg-red-500 rounded hover:bg-red-600">
          Logout
        </button>
      </div>
      <div className="flex flex-1">
        <div className="w-64 border-r border-gray-200">
          <SessionSidebar onSelectSession={handleSelectSession} activeSessionId={activeSessionId || undefined} />
          <DocumentUploader />
        </div>
        <div className="flex-1">
          <ChatWindow activeSessionId={activeSessionId} />
        </div>
      </div>
    </div>
  );
}