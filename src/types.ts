export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: string;
}

export interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

export interface MessageListProps {
  messages: Message[];
  loading: boolean;
}

export interface MessageItemProps {
  message: Message;
} 