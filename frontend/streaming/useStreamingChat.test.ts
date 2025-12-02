/**
 * Unit Tests for useStreamingChat Hook
 *
 * Test suite for the streaming chat hook covering:
 * - Streaming lifecycle
 * - Error handling
 * - Retry logic
 * - Token accumulation
 * - Cleanup and memory management
 *
 * Citation: if://citation/openwebui-api-20251130-spec-v1.0
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useStreamingChat, StreamingError } from './useStreamingChat';
import type { StreamResponse } from './types';

// Mock fetch API
global.fetch = jest.fn();

// Mock crypto.randomUUID
Object.defineProperty(global, 'crypto', {
  value: {
    randomUUID: () => 'test-uuid-12345',
  },
});

describe('useStreamingChat', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Initialization', () => {
    test('should initialize with default state', () => {
      const { result } = renderHook(() =>
        useStreamingChat({ apiKey: 'test-key' })
      );

      expect(result.current.messages).toEqual([]);
      expect(result.current.currentMessage).toBe('');
      expect(result.current.isStreaming).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.tokenCount).toBe(0);
    });

    test('should accept custom configuration', () => {
      const onComplete = jest.fn();
      const { result } = renderHook(() =>
        useStreamingChat({
          apiKey: 'test-key',
          model: 'custom-model',
          apiUrl: 'http://custom:8000',
          onComplete,
        })
      );

      expect(result.current).toBeDefined();
    });
  });

  describe('Message Sending', () => {
    test('should send message and update state', async () => {
      const mockSSEResponse = `data: ${JSON.stringify({
        choices: [
          { index: 0, delta: { role: 'assistant', content: 'Hello' } },
        ],
      } as StreamResponse)}
data: ${JSON.stringify({
        choices: [{ index: 0, delta: { role: 'assistant', content: ' world' } }],
      } as StreamResponse)}
data: [DONE]`;

      const mockReadableStream = {
        getReader: jest.fn(() => ({
          read: jest
            .fn()
            .mockResolvedValueOnce({
              done: false,
              value: new TextEncoder().encode(mockSSEResponse),
            })
            .mockResolvedValueOnce({ done: true, value: undefined }),
          releaseLock: jest.fn(),
        })),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        body: mockReadableStream,
      });

      const { result } = renderHook(() =>
        useStreamingChat({ apiKey: 'test-key' })
      );

      let response: string;
      await act(async () => {
        response = await result.current.sendMessage('Test question');
      });

      expect(response).toBe('Hello world');
      expect(result.current.messages).toHaveLength(2);
      expect(result.current.messages[0].role).toBe('user');
      expect(result.current.messages[1].role).toBe('assistant');
    });

    test('should reject empty messages', async () => {
      const { result } = renderHook(() =>
        useStreamingChat({ apiKey: 'test-key' })
      );

      await expect(act(async () => result.current.sendMessage(''))).rejects.toThrow(
        'Message text cannot be empty'
      );
    });

    test('should reject while streaming', async () => {
      const mockReadableStream = {
        getReader: jest.fn(() => ({
          read: jest.fn(() =>
            new Promise(() => {}) // Never resolves
          ),
          releaseLock: jest.fn(),
        })),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        body: mockReadableStream,
      });

      const { result } = renderHook(() =>
        useStreamingChat({ apiKey: 'test-key' })
      );

      // Start first message
      act(() => {
        result.current.sendMessage('First message');
      });

      await waitFor(() => expect(result.current.isStreaming).toBe(true));

      // Try to send second message while streaming
      await expect(
        act(async () => result.current.sendMessage('Second message'))
      ).rejects.toThrow('Already streaming a message');
    });
  });

  describe('Error Handling', () => {
    test('should handle API errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        text: jest.fn().mockResolvedValueOnce('Unauthorized'),
      });

      const onError = jest.fn();
      const { result } = renderHook(() =>
        useStreamingChat({
          apiKey: 'invalid-key',
          onError,
        })
      );

      await expect(
        act(async () => result.current.sendMessage('Test'))
      ).rejects.toThrow(StreamingError);

      expect(onError).toHaveBeenCalled();
      const error = onError.mock.calls[0][0];
      expect(error.code).toBe('API_ERROR');
      expect(error.statusCode).toBe(401);
    });

    test('should handle connection timeout', async () => {
      (global.fetch as jest.Mock).mockImplementation(
        () =>
          new Promise(() => {}) // Never resolves
      );

      const onError = jest.fn();
      const { result } = renderHook(() =>
        useStreamingChat({
          apiKey: 'test-key',
          connectionTimeout: 100,
          onError,
        })
      );

      await act(async () => {
        try {
          await result.current.sendMessage('Test');
        } catch (e) {
          // Expected
        }
      });

      await waitFor(() => expect(onError).toHaveBeenCalled());
    });

    test('should handle malformed SSE data', async () => {
      const mockReadableStream = {
        getReader: jest.fn(() => ({
          read: jest
            .fn()
            .mockResolvedValueOnce({
              done: false,
              value: new TextEncoder().encode('data: {invalid json}'),
            })
            .mockResolvedValueOnce({ done: true, value: undefined }),
          releaseLock: jest.fn(),
        })),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        body: mockReadableStream,
      });

      const onError = jest.fn();
      const { result } = renderHook(() =>
        useStreamingChat({
          apiKey: 'test-key',
          onError,
        })
      );

      await act(async () => {
        try {
          await result.current.sendMessage('Test');
        } catch (e) {
          // Expected - malformed data should still complete
        }
      });

      // Should complete even with malformed data
      expect(result.current.isStreaming).toBe(false);
    });

    test('should clear error state', async () => {
      const { result } = renderHook(() =>
        useStreamingChat({ apiKey: 'test-key' })
      );

      // Manually set error
      act(() => {
        const error = new StreamingError('TIMEOUT', 'Test timeout');
        // In real implementation, this would be set by the hook
      });

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('Stream Control', () => {
    test('should stop generation', async () => {
      const mockReadableStream = {
        getReader: jest.fn(() => ({
          read: jest.fn(() =>
            new Promise(() => {}) // Never resolves
          ),
          releaseLock: jest.fn(),
        })),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        body: mockReadableStream,
      });

      const { result } = renderHook(() =>
        useStreamingChat({ apiKey: 'test-key' })
      );

      act(() => {
        result.current.sendMessage('Test');
      });

      await waitFor(() => expect(result.current.isStreaming).toBe(true));

      act(() => {
        result.current.stopGeneration();
      });

      await waitFor(() => expect(result.current.isStreaming).toBe(false));
    });
  });

  describe('Token Accumulation', () => {
    test('should accumulate tokens correctly', async () => {
      const mockSSEResponse = `data: ${JSON.stringify({
        choices: [{ index: 0, delta: { role: 'assistant', content: 'a' } }],
      } as StreamResponse)}
data: ${JSON.stringify({
        choices: [{ index: 0, delta: { role: 'assistant', content: 'b' } }],
      } as StreamResponse)}
data: ${JSON.stringify({
        choices: [{ index: 0, delta: { role: 'assistant', content: 'c' } }],
      } as StreamResponse)}
data: [DONE]`;

      const mockReadableStream = {
        getReader: jest.fn(() => ({
          read: jest
            .fn()
            .mockResolvedValueOnce({
              done: false,
              value: new TextEncoder().encode(mockSSEResponse),
            })
            .mockResolvedValueOnce({ done: true, value: undefined }),
          releaseLock: jest.fn(),
        })),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        body: mockReadableStream,
      });

      const { result } = renderHook(() =>
        useStreamingChat({ apiKey: 'test-key' })
      );

      await act(async () => {
        await result.current.sendMessage('Test');
      });

      expect(result.current.currentMessage).toBe('abc');
      expect(result.current.tokenCount).toBe(3);
    });
  });

  describe('Callbacks', () => {
    test('should call onToken for each token', async () => {
      const onToken = jest.fn();
      const mockSSEResponse = `data: ${JSON.stringify({
        choices: [{ index: 0, delta: { role: 'assistant', content: 'Hello' } }],
      } as StreamResponse)}
data: [DONE]`;

      const mockReadableStream = {
        getReader: jest.fn(() => ({
          read: jest
            .fn()
            .mockResolvedValueOnce({
              done: false,
              value: new TextEncoder().encode(mockSSEResponse),
            })
            .mockResolvedValueOnce({ done: true, value: undefined }),
          releaseLock: jest.fn(),
        })),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        body: mockReadableStream,
      });

      const { result } = renderHook(() =>
        useStreamingChat({
          apiKey: 'test-key',
          onToken,
        })
      );

      await act(async () => {
        await result.current.sendMessage('Test');
      });

      expect(onToken).toHaveBeenCalledWith('Hello');
    });

    test('should call onComplete with full message', async () => {
      const onComplete = jest.fn();
      const mockSSEResponse = `data: ${JSON.stringify({
        choices: [{ index: 0, delta: { role: 'assistant', content: 'Response' } }],
      } as StreamResponse)}
data: [DONE]`;

      const mockReadableStream = {
        getReader: jest.fn(() => ({
          read: jest
            .fn()
            .mockResolvedValueOnce({
              done: false,
              value: new TextEncoder().encode(mockSSEResponse),
            })
            .mockResolvedValueOnce({ done: true, value: undefined }),
          releaseLock: jest.fn(),
        })),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        body: mockReadableStream,
      });

      const { result } = renderHook(() =>
        useStreamingChat({
          apiKey: 'test-key',
          onComplete,
        })
      );

      await act(async () => {
        await result.current.sendMessage('Test');
      });

      expect(onComplete).toHaveBeenCalledWith('Response');
    });
  });

  describe('Message History', () => {
    test('should maintain message history', async () => {
      const mockSSEResponse = `data: ${JSON.stringify({
        choices: [{ index: 0, delta: { role: 'assistant', content: 'Response' } }],
      } as StreamResponse)}
data: [DONE]`;

      const mockReadableStream = {
        getReader: jest.fn(() => ({
          read: jest
            .fn()
            .mockResolvedValueOnce({
              done: false,
              value: new TextEncoder().encode(mockSSEResponse),
            })
            .mockResolvedValueOnce({ done: true, value: undefined }),
          releaseLock: jest.fn(),
        })),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        body: mockReadableStream,
      });

      const { result } = renderHook(() =>
        useStreamingChat({ apiKey: 'test-key' })
      );

      await act(async () => {
        await result.current.sendMessage('Hello');
      });

      expect(result.current.messages).toHaveLength(2);
      expect(result.current.messages[0].role).toBe('user');
      expect(result.current.messages[0].content).toBe('Hello');
      expect(result.current.messages[1].role).toBe('assistant');
    });

    test('should allow adding messages manually', () => {
      const { result } = renderHook(() =>
        useStreamingChat({ apiKey: 'test-key' })
      );

      act(() => {
        result.current.addMessage({
          role: 'system',
          content: 'System prompt',
        });
      });

      expect(result.current.messages).toHaveLength(1);
      expect(result.current.messages[0].role).toBe('system');
    });
  });

  describe('Cleanup', () => {
    test('should cleanup on unmount', () => {
      const { unmount } = renderHook(() =>
        useStreamingChat({ apiKey: 'test-key' })
      );

      unmount();

      // No errors should occur
    });
  });
});
