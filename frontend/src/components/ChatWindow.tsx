import React, { useEffect, useRef, useState } from 'react';
import MessageBubble from '@/src/components/MessageBubble';
import TypingIndicator from '@/src/components/TypingIndicator';
import { getMessages, queryAI } from '@/src/lib/aiApi';

interface ChatWindowProps {
  sessionId: string | null;
}

interface Message {
  id: string;
  role: string;
  content: string;
  sources?: string[];
}

const ChatWindow: React.FC<ChatWindowProps> = ({ sessionId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setMessages([]);
      return;
    }

    const fetchMessages = async () => {
      setLoading(true);
      setError(null);
      try {
        const fetchedMessages = await getMessages(sessionId);
        setMessages(fetchedMessages.map((msg: any) => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          sources: msg.metadata?.sources || [],
        })));
      } catch (err) {
        setError('Failed to load messages.');
      } finally {
        setLoading(false);
      }
    };

    fetchMessages();
  }, [sessionId]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !sessionId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuery('');
    setLoading(true);
    setError(null);

    try {
      const response = await queryAI(query, sessionId);
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError('Failed to fetch response.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-100">
      <div className="flex-1 overflow-y-auto p-4">
        {sessionId ? (
          messages.length > 0 ? (
            messages.map((message) => (
              <MessageBubble
                key={message.id}
                role={message.role}
                content={message.content}
                sources={message.sources}
              />
            ))
          ) : (
            <p className="text-gray-500 text-center">No messages yet.</p>
          )
        ) : (
          <p className="text-gray-500 text-center">Select a session to start chatting.</p>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form
        onSubmit={handleSubmit}
        className="flex items-center border-t border-gray-300 p-4 bg-white"
      >
        <textarea
          className="flex-1 resize-none border rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={1}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
              handleSubmit(e);
            }
          }}
        />
        <button
          type="submit"
          className="ml-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-300"
          disabled={loading || !query.trim()}
        >
          Send
        </button>
      </form>
      {loading && <TypingIndicator />}
      {error && <p className="text-red-500 text-center mt-2">{error}</p>}
    </div>
  );
};

export default ChatWindow;