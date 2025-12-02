/**
 * useStreamingChat - React Hook for consuming Server-Sent Events from OpenWebUI `/api/chat/completions`
 *
 * Provides production-ready streaming chat functionality with:
 * - SSE connection lifecycle management
 * - Token accumulation and batching
 * - Error handling with exponential backoff retry
 * - Timeout detection and recovery
 * - TypeScript type safety
 *
 * Citation: if://citation/openwebui-api-20251130-spec-v1.0
 * @see /home/setup/infrafabric/integration/openwebui_api_spec.md
 */

import { useState, useCallback, useRef, useEffect } from 'react';

/**
 * Message types matching OpenWebUI API specification
 */
export interface ChatMessage {
  id?: string;
  role: 'system' | 'user' | 'assistant';
  content: string;
  timestamp?: number;
}

/**
 * SSE delta response from OpenWebUI
 */
export interface StreamDelta {
  role?: 'assistant';
  content: string | null;
}

/**
 * SSE event choice from OpenWebUI streaming response
 */
export interface StreamChoice {
  index: number;
  delta: StreamDelta;
  finish_reason?: 'stop' | 'length' | 'function_call' | null;
}

/**
 * SSE event response format from OpenWebUI
 */
export interface StreamResponse {
  choices: StreamChoice[];
}

/**
 * Error types for streaming chat
 */
export class StreamingError extends Error {
  constructor(
    public code: 'CONNECTION_FAILED' | 'TIMEOUT' | 'MALFORMED_DATA' | 'API_ERROR' | 'ABORT',
    message: string,
    public statusCode?: number
  ) {
    super(message);
    this.name = 'StreamingError';
  }
}

/**
 * Hook configuration options
 */
export interface UseStreamingChatOptions {
  /** Base URL for OpenWebUI API (default: 'http://localhost:8080') */
  apiUrl?: string;

  /** Model to use for chat completions (default: 'claude-3-opus-20250219') */
  model?: string;

  /** API key or JWT token for authentication */
  apiKey: string;

  /** System prompt to override defaults */
  system?: string;

  /** Temperature for response generation (0.0-2.0) */
  temperature?: number;

  /** Nucleus sampling parameter (0.0-1.0) */
  topP?: number;

  /** Maximum tokens in response */
  maxTokens?: number;

  /** Timeout for stream connection in milliseconds (default: 30000) */
  streamTimeout?: number;

  /** Timeout for initial connection in milliseconds (default: 10000) */
  connectionTimeout?: number;

  /** Maximum number of retries on failure (default: 3) */
  maxRetries?: number;

  /** Callback when new token is received */
  onToken?: (token: string) => void;

  /** Callback when message is complete */
  onComplete?: (message: string) => void;

  /** Callback on error */
  onError?: (error: StreamingError) => void;

  /** Enable debug logging */
  debug?: boolean;
}

/**
 * Hook state for streaming chat
 */
export interface UseStreamingChatState {
  /** Array of all messages in conversation */
  messages: ChatMessage[];

  /** Currently streaming message content */
  currentMessage: string;

  /** Whether actively receiving stream data */
  isStreaming: boolean;

  /** Current error if any */
  error: StreamingError | null;

  /** Number of tokens accumulated in current message */
  tokenCount: number;
}

/**
 * Hook return interface
 */
export interface UseStreamingChatReturn extends UseStreamingChatState {
  /** Send user message and start streaming */
  sendMessage: (text: string, chatId?: string) => Promise<string>;

  /** Abort current streaming operation */
  stopGeneration: () => void;

  /** Retry last failed message */
  retryLast: () => Promise<string>;

  /** Clear error state */
  clearError: () => void;

  /** Add message to history manually */
  addMessage: (message: ChatMessage) => void;
}

/**
 * Main hook implementation
 *
 * Usage example:
 * ```typescript
 * const {
 *   messages,
 *   currentMessage,
 *   isStreaming,
 *   error,
 *   sendMessage,
 *   stopGeneration,
 * } = useStreamingChat({
 *   apiKey: 'your-api-key',
 *   model: 'claude-3-opus-20250219',
 *   apiUrl: 'http://localhost:8080',
 *   onToken: (token) => console.log('Received:', token),
 *   onComplete: (message) => console.log('Complete:', message),
 * });
 *
 * // Send a message
 * await sendMessage('Hello, how are you?');
 *
 * // Monitor streaming
 * {isStreaming && <p>Streaming: {currentMessage}</p>}
 * {error && <p>Error: {error.message}</p>}
 * ```
 */
export function useStreamingChat(options: UseStreamingChatOptions): UseStreamingChatReturn {
  const {
    apiUrl = 'http://localhost:8080',
    model = 'claude-3-opus-20250219',
    apiKey,
    system,
    temperature = 0.7,
    topP = 1.0,
    maxTokens,
    streamTimeout = 30000,
    connectionTimeout = 10000,
    maxRetries = 3,
    onToken,
    onComplete,
    onError,
    debug = false,
  } = options;

  // State management
  const [state, setState] = useState<UseStreamingChatState>({
    messages: [],
    currentMessage: '',
    isStreaming: false,
    error: null,
    tokenCount: 0,
  });

  // Refs for lifecycle management
  const abortControllerRef = useRef<AbortController | null>(null);
  const timeoutIdRef = useRef<NodeJS.Timeout | null>(null);
  const lastMessageRef = useRef<ChatMessage | null>(null);
  const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null);
  const retryCountRef = useRef<number>(0);

  /**
   * Internal logging function
   */
  const log = useCallback(
    (message: string, data?: any) => {
      if (debug) {
        console.log(`[useStreamingChat] ${message}`, data || '');
      }
    },
    [debug]
  );

  /**
   * Set error state and invoke callback
   */
  const setError = useCallback(
    (error: StreamingError) => {
      log('Error occurred', error);
      setState((prev) => ({ ...prev, error }));
      onError?.(error);
    },
    [log, onError]
  );

  /**
   * Parse SSE line into JSON
   */
  const parseSSELine = useCallback((line: string): StreamResponse | null => {
    if (!line.startsWith('data: ')) {
      return null;
    }

    const dataStr = line.slice(6).trim();

    if (dataStr === '[DONE]') {
      return null; // Signal completion, not an error
    }

    try {
      const parsed = JSON.parse(dataStr);
      return parsed as StreamResponse;
    } catch (e) {
      log('Failed to parse SSE line', { line, error: String(e) });
      return null;
    }
  }, [log]);

  /**
   * Clean up resources
   */
  const cleanup = useCallback(() => {
    log('Cleaning up resources');

    if (timeoutIdRef.current) {
      clearTimeout(timeoutIdRef.current);
      timeoutIdRef.current = null;
    }

    if (readerRef.current) {
      try {
        readerRef.current.releaseLock();
      } catch (e) {
        // Reader might already be released
      }
      readerRef.current = null;
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, [log]);

  /**
   * Handle stream completion
   */
  const completeStream = useCallback(
    async (chatId?: string, messageId?: string) => {
      const fullContent = state.currentMessage;

      if (!fullContent) return '';

      log('Completing stream', { chatId, contentLength: fullContent.length });

      setState((prev) => ({
        ...prev,
        isStreaming: false,
        messages: [
          ...prev.messages,
          {
            id: messageId,
            role: 'assistant',
            content: fullContent,
            timestamp: Date.now(),
          },
        ],
        currentMessage: '',
        tokenCount: 0,
      }));

      onComplete?.(fullContent);

      // Signal completion to OpenWebUI backend if chatId provided
      if (chatId && messageId) {
        try {
          await fetch(`${apiUrl}/api/chat/completed`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${apiKey}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              id: messageId,
              chat_id: chatId,
              message: {
                id: messageId,
                role: 'assistant',
                content: fullContent,
              },
              model,
            }),
          });
        } catch (e) {
          log('Failed to signal completion to backend', e);
        }
      }

      return fullContent;
    },
    [state.currentMessage, log, onComplete, apiUrl, apiKey, model]
  );

  /**
   * Set stream timeout with auto-cleanup
   */
  const setStreamTimeout = useCallback(() => {
    if (timeoutIdRef.current) {
      clearTimeout(timeoutIdRef.current);
    }

    timeoutIdRef.current = setTimeout(() => {
      log('Stream timeout - no data received');
      cleanup();
      const error = new StreamingError(
        'TIMEOUT',
        'Stream timeout: No data received for 30 seconds'
      );
      setError(error);
      setState((prev) => ({ ...prev, isStreaming: false }));
    }, streamTimeout);
  }, [streamTimeout, cleanup, log, setError]);

  /**
   * Process SSE buffer and extract complete lines
   */
  const processSSEBuffer = useCallback(
    (buffer: string, isComplete: boolean): { remaining: string; lines: string[] } => {
      const lines = buffer.split('\n');
      const remaining = isComplete ? '' : lines.pop() || '';
      return { remaining, lines: lines.filter((l) => l.length > 0) };
    },
    []
  );

  /**
   * Main streaming implementation
   */
  const streamMessages = useCallback(
    async (
      userMessages: ChatMessage[],
      chatId?: string
    ): Promise<string> => {
      log('Starting stream', { messageCount: userMessages.length });

      retryCountRef.current = 0;
      let buffer = '';
      let fullContent = '';
      let messageId = crypto.randomUUID?.() || `msg-${Date.now()}`;

      return new Promise(async (resolve, reject) => {
        try {
          abortControllerRef.current = new AbortController();

          const response = await Promise.race([
            fetch(`${apiUrl}/api/chat/completions`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                model,
                messages: userMessages,
                stream: true,
                chat_id: chatId,
                temperature,
                top_p: topP,
                max_tokens: maxTokens,
                system,
              }),
              signal: abortControllerRef.current.signal,
            }),
            new Promise<Response>((_, reject) =>
              setTimeout(
                () => reject(new Error('Connection timeout')),
                connectionTimeout
              )
            ) as Promise<Response>,
          ]);

          if (!response.ok) {
            const errorData = await response.text();
            log('API error', { status: response.status, data: errorData });
            throw new StreamingError(
              'API_ERROR',
              `API returned ${response.status}: ${errorData}`,
              response.status
            );
          }

          const reader = response.body?.getReader();
          if (!reader) {
            throw new StreamingError('CONNECTION_FAILED', 'No response body available');
          }

          readerRef.current = reader;
          const decoder = new TextDecoder();

          setStreamTimeout();
          setState((prev) => ({ ...prev, isStreaming: true, error: null }));

          try {
            // eslint-disable-next-line no-constant-condition
            while (true) {
              const { done, value } = await reader.read();

              if (done) {
                log('Reader finished');
                break;
              }

              // Reset timeout on each data chunk received
              setStreamTimeout();

              try {
                buffer += decoder.decode(value, { stream: true });

                const { remaining, lines } = processSSEBuffer(
                  buffer,
                  false
                );
                buffer = remaining;

                for (const line of lines) {
                  if (line === '[DONE]' || line === 'data: [DONE]') {
                    log('Received [DONE] signal');
                    break;
                  }

                  const parsed = parseSSELine(line);
                  if (parsed) {
                    const delta = parsed.choices[0]?.delta?.content;

                    if (delta !== null && delta !== undefined && delta !== '') {
                      fullContent += delta;

                      // Batch state updates
                      setState((prev) => ({
                        ...prev,
                        currentMessage: fullContent,
                        tokenCount: prev.tokenCount + 1,
                      }));

                      onToken?.(delta);
                      log('Token received', { token: delta });
                    }
                  }
                }
              } catch (e) {
                log('Error processing buffer', e);
                throw new StreamingError(
                  'MALFORMED_DATA',
                  `Failed to process stream data: ${String(e)}`
                );
              }
            }

            // Process any remaining buffer
            if (buffer.trim()) {
              const { lines } = processSSEBuffer(buffer, true);
              for (const line of lines) {
                const parsed = parseSSELine(line);
                if (parsed) {
                  const delta = parsed.choices[0]?.delta?.content;
                  if (delta) {
                    fullContent += delta;
                    onToken?.(delta);
                  }
                }
              }
            }

            cleanup();

            // Save assistant message
            const assistantMessage: ChatMessage = {
              id: messageId,
              role: 'assistant',
              content: fullContent,
              timestamp: Date.now(),
            };

            lastMessageRef.current = assistantMessage;

            // Complete the stream
            const result = await completeStream(chatId, messageId);
            resolve(result);
          } catch (e) {
            throw e;
          }
        } catch (e) {
          cleanup();

          if (e instanceof StreamingError) {
            setError(e);
            reject(e);
          } else if (e instanceof Error) {
            let streamError: StreamingError;

            if (e.name === 'AbortError') {
              streamError = new StreamingError('ABORT', 'Stream was aborted by user');
            } else if (e.message.includes('timeout')) {
              streamError = new StreamingError(
                'TIMEOUT',
                'Connection timeout exceeded'
              );
            } else {
              streamError = new StreamingError(
                'CONNECTION_FAILED',
                `Connection failed: ${e.message}`
              );
            }

            setError(streamError);
            reject(streamError);
          } else {
            const unknownError = new StreamingError(
              'CONNECTION_FAILED',
              'Unknown error occurred'
            );
            setError(unknownError);
            reject(unknownError);
          }

          setState((prev) => ({ ...prev, isStreaming: false }));
        }
      });
    },
    [
      apiUrl,
      apiKey,
      model,
      temperature,
      topP,
      maxTokens,
      system,
      streamTimeout,
      connectionTimeout,
      cleanup,
      setStreamTimeout,
      parseSSELine,
      processSSEBuffer,
      completeStream,
      log,
      onToken,
      setError,
    ]
  );

  /**
   * Send user message and stream response
   */
  const sendMessage = useCallback(
    async (text: string, chatId?: string): Promise<string> => {
      if (!text.trim()) {
        throw new Error('Message text cannot be empty');
      }

      if (state.isStreaming) {
        throw new Error('Already streaming a message');
      }

      const userMessage: ChatMessage = {
        id: crypto.randomUUID?.() || `msg-${Date.now()}`,
        role: 'user',
        content: text,
        timestamp: Date.now(),
      };

      // Add user message to history
      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, userMessage],
        currentMessage: '',
        error: null,
      }));

      lastMessageRef.current = userMessage;

      // Build message history for API call
      const messagesForAPI: ChatMessage[] = [
        ...state.messages,
        userMessage,
      ];

      try {
        return await streamMessages(messagesForAPI, chatId);
      } catch (e) {
        throw e;
      }
    },
    [state.messages, state.isStreaming, streamMessages]
  );

  /**
   * Stop current streaming operation
   */
  const stopGeneration = useCallback(() => {
    log('Stopping generation');

    if (state.isStreaming && abortControllerRef.current) {
      abortControllerRef.current.abort();
      cleanup();
      setState((prev) => ({ ...prev, isStreaming: false }));
    }
  }, [state.isStreaming, cleanup, log]);

  /**
   * Retry last message with exponential backoff
   */
  const retryLast = useCallback(async (): Promise<string> => {
    if (!lastMessageRef.current) {
      throw new Error('No previous message to retry');
    }

    if (retryCountRef.current >= (maxRetries || 3)) {
      throw new Error('Maximum retry attempts exceeded');
    }

    retryCountRef.current += 1;
    const backoffMs = Math.pow(2, retryCountRef.current - 1) * 1000;

    log('Retrying with backoff', { attempt: retryCountRef.current, backoffMs });

    await new Promise((resolve) => setTimeout(resolve, backoffMs));

    // Remove last assistant message if it exists
    const lastMessage = state.messages[state.messages.length - 1];
    const messagesToKeep =
      lastMessage?.role === 'assistant'
        ? state.messages.slice(0, -1)
        : state.messages;

    setState((prev) => ({
      ...prev,
      messages: messagesToKeep,
    }));

    return sendMessage(
      lastMessageRef.current.content
    );
  }, [maxRetries, log, state.messages, sendMessage]);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  /**
   * Manually add message to history
   */
  const addMessage = useCallback((message: ChatMessage) => {
    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, message],
    }));
  }, []);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      cleanup();
    };
  }, [cleanup]);

  return {
    ...state,
    sendMessage,
    stopGeneration,
    retryLast,
    clearError,
    addMessage,
  };
}

export default useStreamingChat;
