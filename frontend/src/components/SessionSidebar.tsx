import React, { useEffect, useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { getSessions, createSession } from '../api/client';
import { ChatSession } from '../types';

interface SessionSidebarProps {
  onSelectSession: (id: string) => void;
  activeSessionId?: string;
}

const SessionSidebar: React.FC<SessionSidebarProps> = ({ onSelectSession, activeSessionId }) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSessions = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await getSessions();
        setSessions(response.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()));
      } catch (err) {
        setError('Failed to load sessions.');
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, []);

  const handleNewChat = async () => {
    setError(null);
    try {
      const newSession = await createSession();
      setSessions((prev) => [newSession, ...prev]);
      onSelectSession(newSession.id);
    } catch (err) {
      setError('Failed to create a new session.');
    }
  };

  return (
    <div className="w-64 bg-gray-100 border-r border-gray-300 h-full flex flex-col">
      <div className="p-4 border-b border-gray-300">
        <button
          onClick={handleNewChat}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
        >
          New Chat
        </button>
      </div>
      {error && <div className="text-red-500 text-sm p-4">{error}</div>}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 space-y-4">
            <div className="h-6 bg-gray-300 rounded animate-pulse"></div>
            <div className="h-6 bg-gray-300 rounded animate-pulse"></div>
            <div className="h-6 bg-gray-300 rounded animate-pulse"></div>
          </div>
        ) : (
          <ul>
            {sessions.map((session) => (
              <li
                key={session.id}
                onClick={() => onSelectSession(session.id)}
                className={`p-4 cursor-pointer ${
                  session.id === activeSessionId
                    ? 'bg-gray-200 border-l-4 border-blue-500'
                    : 'hover:bg-gray-100'
                }`}
              >
                <div className="font-medium truncate">{session.title.slice(0, 30)}</div>
                <div className="text-sm text-gray-500">
                  {formatDistanceToNow(new Date(session.created_at), { addSuffix: true })}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default SessionSidebar;