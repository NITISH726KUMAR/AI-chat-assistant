import React from 'react';
import { MessageListProps } from '../types';
import MessageItem from './MessageItem';

const MessageList: React.FC<MessageListProps> = ({ messages, loading }) => {
  if (messages.length === 0 && !loading) {
    return (
      <div className="flex h-full items-center justify-center text-gray-500">
        <p>Start a conversation by typing a message below.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
      
      {loading && (
        <div className="flex items-center space-x-2 animate-pulse">
          <div className="h-3 w-3 rounded-full bg-blue-400"></div>
          <div className="h-3 w-3 rounded-full bg-blue-400"></div>
          <div className="h-3 w-3 rounded-full bg-blue-400"></div>
          <span className="text-sm text-gray-500">AI is thinking...</span>
        </div>
      )}
    </div>
  );
};

export default MessageList; 