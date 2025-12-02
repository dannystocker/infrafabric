/**
 * Type Definitions for useStreamingChat Hook
 *
 * Exported separately for easier integration and type reuse
 * across React components and utilities.
 *
 * Citation: if://citation/openwebui-api-20251130-spec-v1.0
 */

/**
 * Message types matching OpenWebUI API specification
 */
export type MessageRole = 'system' | 'user' | 'assistant';

/**
 * Standard message in conversation
 */
export interface ChatMessage {
  /** Unique identifier for message (UUID) */
  id?: string;

  /** Role type: system instructions, user input, or assistant response */
  role: MessageRole;

  /** Message content text */
  content: string;

  /** Unix timestamp when message was created */
  timestamp?: number;
}

/**
 * Message with complete metadata
 */
export interface ChatMessageWithMetadata extends ChatMessage {
  id: string;
  timestamp: number;
  tokenCount?: number;
  completionTime?: number;
}

/**
 * SSE delta chunk - part of token sent from OpenWebUI
 */
export interface StreamDelta {
  /** Role on first token of response */
  role?: MessageRole;

  /** Partial or complete token content */
  content: string | null;
}

/**
 * Single choice in SSE response
 */
export interface StreamChoice {
  /** Index of choice (usually 0) */
  index: number;

  /** Delta containing partial token */
  delta: StreamDelta;

  /** Completion reason if stream ended */
  finish_reason?: 'stop' | 'length' | 'function_call' | null;
}

/**
 * Complete SSE event from OpenWebUI
 */
export interface StreamResponse {
  /** Array of choices (usually single choice) */
  choices: StreamChoice[];
}

/**
 * Error codes for streaming operations
 */
export type StreamingErrorCode =
  | 'CONNECTION_FAILED'   // Network/fetch error
  | 'TIMEOUT'            // Stream or connection timeout
  | 'MALFORMED_DATA'     // Invalid SSE data
  | 'API_ERROR'          // HTTP error from OpenWebUI
  | 'ABORT';             // User stopped generation

/**
 * Streaming operation error with context
 */
export class StreamingError extends Error {
  constructor(
    /** Machine-readable error code */
    public code: StreamingErrorCode,
    /** Human-readable error message */
    message: string,
    /** HTTP status code if applicable */
    public statusCode?: number
  ) {
    super(message);
    this.name = 'StreamingError';
  }

  /**
   * Get recovery suggestion for user
   */
  getRecoverySuggestion(): string {
    switch (this.code) {
      case 'CONNECTION_FAILED':
        return 'Check your internet connection and try again';
      case 'TIMEOUT':
        return 'The connection was too slow. Try again or increase timeout.';
      case 'MALFORMED_DATA':
        return 'Server returned invalid data. Check OpenWebUI logs.';
      case 'API_ERROR':
        return this.statusCode === 401
          ? 'Invalid API key. Check authentication.'
          : `Server error ${this.statusCode}. Try again later.`;
      case 'ABORT':
        return 'You stopped the message generation.';
      default:
        return 'An unexpected error occurred.';
    }
  }
}

/**
 * Hook configuration options
 */
export interface UseStreamingChatOptions {
  /** API key or JWT token for authentication (required) */
  apiKey: string;

  /** Base URL for OpenWebUI instance */
  apiUrl?: string;

  /** Model ID to use for completions */
  model?: string;

  /** System prompt override for all requests */
  system?: string;

  /** Temperature for response generation (0.0-2.0) */
  temperature?: number;

  /** Nucleus sampling parameter (0.0-1.0) */
  topP?: number;

  /** Maximum tokens to generate */
  maxTokens?: number;

  /** Timeout for stream inactivity in milliseconds */
  streamTimeout?: number;

  /** Timeout for initial connection in milliseconds */
  connectionTimeout?: number;

  /** Maximum number of auto-retries on failure */
  maxRetries?: number;

  /** Called for each token received */
  onToken?: (token: string) => void;

  /** Called when message completes */
  onComplete?: (message: string) => void;

  /** Called on any error */
  onError?: (error: StreamingError) => void;

  /** Enable debug console logging */
  debug?: boolean;
}

/**
 * Streaming state snapshot
 */
export interface UseStreamingChatState {
  /** All messages in conversation history */
  messages: ChatMessage[];

  /** Currently accumulating message (while streaming) */
  currentMessage: string;

  /** Whether actively receiving tokens */
  isStreaming: boolean;

  /** Current error if any */
  error: StreamingError | null;

  /** Number of tokens in current message */
  tokenCount: number;
}

/**
 * Hook return interface with all methods
 */
export interface UseStreamingChatReturn extends UseStreamingChatState {
  /**
   * Send user message and stream response
   * @param text - User message text
   * @param chatId - Optional chat session ID for persistence
   * @returns Promise resolving to complete assistant message
   * @throws StreamingError on failure
   */
  sendMessage: (text: string, chatId?: string) => Promise<string>;

  /**
   * Stop current streaming operation
   * Sets error.code to 'ABORT'
   */
  stopGeneration: () => void;

  /**
   * Retry last failed message with exponential backoff
   * @returns Promise resolving to complete assistant message
   * @throws StreamingError if max retries exceeded
   */
  retryLast: () => Promise<string>;

  /**
   * Clear error state
   */
  clearError: () => void;

  /**
   * Manually add message to history
   * Useful for loading previous conversations
   * @param message - Message to add
   */
  addMessage: (message: ChatMessage) => void;
}

/**
 * Chat statistics for monitoring
 */
export interface ChatStatistics {
  /** Total messages in conversation */
  totalMessages: number;

  /** Total tokens received */
  totalTokens: number;

  /** Average tokens per message */
  avgTokensPerMessage: number;

  /** Fastest first-token latency */
  minFirstTokenLatency: number;

  /** Slowest first-token latency */
  maxFirstTokenLatency: number;

  /** Average first-token latency */
  avgFirstTokenLatency: number;

  /** Total time streaming */
  totalStreamingTime: number;

  /** Number of errors encountered */
  errorCount: number;

  /** Success rate percentage */
  successRate: number;
}

/**
 * Chat session metadata
 */
export interface ChatSession {
  /** Unique session identifier */
  id: string;

  /** User-visible session title */
  title: string;

  /** Model used for this session */
  model: string;

  /** System prompt used */
  system?: string;

  /** Messages in this session */
  messages: ChatMessage[];

  /** When session was created */
  createdAt: number;

  /** When session was last updated */
  updatedAt: number;

  /** Optional tags for organizing sessions */
  tags?: string[];

  /** Statistics for the session */
  stats?: ChatStatistics;
}

/**
 * Request configuration for chat completions
 */
export interface ChatCompletionRequest {
  /** Model to use */
  model: string;

  /** Messages to send */
  messages: ChatMessage[];

  /** Enable streaming */
  stream: boolean;

  /** Chat session ID */
  chat_id?: string;

  /** Temperature */
  temperature?: number;

  /** Top P sampling */
  top_p?: number;

  /** Max tokens */
  max_tokens?: number;

  /** System prompt */
  system?: string;

  /** File attachments for RAG */
  files?: Array<{
    type: 'file' | 'collection';
    id: string;
  }>;

  /** Enable background task processing */
  background_tasks?: boolean;
}

/**
 * Response from chat completion
 */
export interface ChatCompletionResponse {
  /** Response ID */
  id: string;

  /** Object type */
  object: 'text_completion';

  /** Creation timestamp */
  created: number;

  /** Model used */
  model: string;

  /** Completion choices */
  choices: Array<{
    index: number;
    message?: ChatMessage;
    delta?: StreamDelta;
    finish_reason: string | null;
  }>;

  /** Token usage */
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

/**
 * File object from OpenWebUI
 */
export interface OpenWebUIFile {
  /** File ID */
  id: string;

  /** Original filename */
  filename: string;

  /** File size in bytes */
  size: number;

  /** MIME type */
  mimetype: string;

  /** Processing status */
  status: 'pending' | 'processing' | 'processed' | 'error';

  /** Upload timestamp */
  uploaded_at: number;

  /** Error message if status is 'error' */
  error?: string;
}

/**
 * Knowledge base from OpenWebUI
 */
export interface KnowledgeBase {
  /** KB ID */
  id: string;

  /** KB name */
  name: string;

  /** KB description */
  description?: string;

  /** Number of documents */
  document_count: number;

  /** Processing status */
  status: 'pending' | 'processing' | 'processed';

  /** Creation timestamp */
  created_at: number;

  /** Last update timestamp */
  updated_at: number;
}

/**
 * Retry configuration
 */
export interface RetryConfig {
  /** Maximum number of retry attempts */
  maxRetries: number;

  /** Initial delay in milliseconds */
  initialDelay: number;

  /** Maximum delay in milliseconds */
  maxDelay: number;

  /** Backoff multiplier */
  backoffMultiplier: number;

  /** Jitter factor (0-1) */
  jitter: number;
}

/**
 * Default retry configuration (exponential backoff)
 */
export const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  initialDelay: 1000,
  maxDelay: 30000,
  backoffMultiplier: 2,
  jitter: 0.1,
};

/**
 * Stream event types for event emitters
 */
export type StreamEventType =
  | 'start'
  | 'token'
  | 'complete'
  | 'error'
  | 'timeout'
  | 'abort';

/**
 * Stream event payload
 */
export interface StreamEvent {
  type: StreamEventType;
  timestamp: number;
  data?: any;
}

/**
 * Performance metrics for a single message
 */
export interface MessageMetrics {
  /** Message ID */
  messageId: string;

  /** Time until first token (milliseconds) */
  firstTokenLatency: number;

  /** Total time to complete (milliseconds) */
  totalTime: number;

  /** Number of tokens */
  tokenCount: number;

  /** Tokens per second */
  tokensPerSecond: number;

  /** Whether completed successfully */
  success: boolean;

  /** Error if not successful */
  error?: StreamingError;
}

export default {
  StreamingError,
  DEFAULT_RETRY_CONFIG,
};
