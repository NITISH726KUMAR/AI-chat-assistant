import React, { useState, useEffect, useRef } from 'react';
import ChatInput from '../components/ChatInput';
import MessageList from '../components/MessageList';
import { Message } from '../types';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const websocketRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize WebSocket connection
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/chat`);
    
    ws.onopen = () => {
      console.log('WebSocket connection established');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.response) {
        const newMessage: Message = {
          id: Date.now().toString(),
          content: data.response,
          role: 'assistant',
          timestamp: new Date().toISOString()
        };
        
        setMessages(prev => [...prev, newMessage]);
        setConversationId(data.conversation_id);
        setLoading(false);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('WebSocket connection error');
    };
    
    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };
    
    websocketRef.current = ws;
    
    return () => {
      ws.close();
    };
  }, []);

  // Scroll to bottom of chat when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load conversation history if conversation ID exists
  useEffect(() => {
    if (conversationId) {
      const loadHistory = async () => {
        try {
          const response = await axios.get(`${API_URL}/api/conversations/${conversationId}`);
          setMessages(response.data);
        } catch (err) {
          console.error('Error loading conversation history:', err);
          setError('Failed to load conversation history');
        }
      };
      
      loadHistory();
    }
  }, [conversationId]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      content: text,
      role: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setError(null);
    
    try {
      // Try WebSocket first
      if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
        websocketRef.current.send(JSON.stringify({
          message: text,
          conversation_id: conversationId
        }));
      } else {
        // Fallback to HTTP if WebSocket is not available
        const response = await axios.post(`${API_URL}/api/chat`, {
          message: text,
          conversation_id: conversationId
        });
        
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: response.data.response,
          role: 'assistant',
          timestamp: new Date().toISOString()
        };
        
        setMessages(prev => [...prev, assistantMessage]);
        setConversationId(response.data.conversation_id);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message');
    } finally {
      if (websocketRef.current?.readyState !== WebSocket.OPEN) {
        setLoading(false);
      }
    }
  };

  return (
    <div className="container mx-auto max-w-4xl p-4">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden flex flex-col h-[90vh]">
        <div className="p-4 bg-blue-600 text-white">
          <h1 className="text-xl font-bold">AI Chat Assistant</h1>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4">
          <MessageList messages={messages} loading={loading} />
          <div ref={messagesEndRef} />
        </div>
        
        {error && (
          <div className="p-2 bg-red-100 text-red-800 text-sm">
            {error}
          </div>
        )}
        
        <div className="border-t p-4">
          <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
        </div>
      </div>
    </div>
  );
};

export default ChatPage; 