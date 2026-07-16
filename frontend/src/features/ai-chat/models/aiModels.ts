export type AIErrorType =
  | 'Validation'
  | 'Unauthorized'
  | 'Forbidden'
  | 'Maintenance'
  | 'LimitExceeded'
  | 'Offline'
  | 'Unknown';

export class AIError extends Error {
  public type: AIErrorType;
  public status?: number;
  public retryAfter?: number;

  constructor(
    message: string,
    type: AIErrorType = 'Unknown',
    status?: number,
    retryAfter?: number
  ) {
    super(message);
    this.name = 'AIError';
    this.type = type;
    this.status = status;
    this.retryAfter = retryAfter;
  }
}

export type MessageRole = 'user' | 'assistant' | 'system';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: Date;
}

export interface StreamingChunk {
  id: string;
  chunk: string;
  createdAt: Date;
}

export interface ConversationState {
  id: string;
  messages: Message[];
  isStreaming: boolean;
  streamingContent: string;
  error: AIError | null;
  jobStatus: string | null; // e.g., 'processing', 'completed', 'failed'
  jobProgress: number; // 0 - 100
}
