/**
 * useStreamingChat Hook - Example Usage
 *
 * This file demonstrates practical implementations of the useStreamingChat hook
 * for different use cases and React component patterns.
 *
 * Citation: if://citation/openwebui-api-20251130-spec-v1.0
 */

import React, { useState, useRef } from 'react';
import { useStreamingChat, StreamingError } from './useStreamingChat';

/**
 * Example 1: Basic Chat Component
 *
 * Minimal implementation showing fundamental streaming chat UI
 */
export function BasicChatExample() {
  const [apiKey, setApiKey] = useState('');
  const {
    messages,
    currentMessage,
    isStreaming,
    error,
    sendMessage,
    stopGeneration,
  } = useStreamingChat({
    apiKey,
    model: 'claude-3-opus-20250219',
    apiUrl: 'http://localhost:8080',
    debug: true,
  });

  const handleSendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const input = (e.currentTarget.elements.namedItem('message') as HTMLInputElement);
    if (!input.value.trim()) return;

    try {
      await sendMessage(input.value);
      input.value = '';
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <strong>{msg.role}:</strong> {msg.content}
          </div>
        ))}

        {isStreaming && (
          <div className="message assistant streaming">
            <strong>Assistant:</strong> {currentMessage}
            <span className="cursor">|</span>
          </div>
        )}

        {error && (
          <div className="error">
            <strong>Error ({error.code}):</strong> {error.message}
          </div>
        )}
      </div>

      <form onSubmit={handleSendMessage} className="input-form">
        <input
          name="message"
          type="text"
          placeholder="Type your message..."
          disabled={isStreaming}
        />
        <button type="submit" disabled={isStreaming}>
          {isStreaming ? 'Streaming...' : 'Send'}
        </button>
        {isStreaming && (
          <button type="button" onClick={stopGeneration}>
            Stop
          </button>
        )}
      </form>

      <div className="api-config">
        <input
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="Enter OpenWebUI API Key"
        />
      </div>
    </div>
  );
}

/**
 * Example 2: Chat with Session Persistence
 *
 * Demonstrates maintaining chat history and using chat IDs
 */
export function ChatWithSessionExample() {
  const [apiKey, setApiKey] = useState('');
  const [chatId, setChatId] = useState<string | undefined>();
  const [sessionTitle, setSessionTitle] = useState('New Chat');

  const {
    messages,
    currentMessage,
    isStreaming,
    error,
    tokenCount,
    sendMessage,
    stopGeneration,
    clearError,
  } = useStreamingChat({
    apiKey,
    model: 'claude-3-opus-20250219',
    apiUrl: 'http://localhost:8080',
    system: 'You are a helpful AI assistant. Provide clear and concise answers.',
    temperature: 0.7,
    onComplete: (message) => {
      console.log('Message completed. Length:', message.length);
      // Here you might auto-generate a title or save to database
    },
    debug: false,
  });

  const inputRef = useRef<HTMLInputElement>(null);

  const handleNewChat = () => {
    setChatId(crypto.randomUUID?.() || `chat-${Date.now()}`);
    setSessionTitle('New Chat');
  };

  const handleSendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!inputRef.current?.value.trim()) return;

    try {
      const messageText = inputRef.current.value;
      inputRef.current.value = '';

      // Create new chat session if needed
      if (!chatId) {
        handleNewChat();
      }

      await sendMessage(messageText, chatId);
    } catch (err) {
      if (err instanceof StreamingError) {
        console.error(`Error (${err.code}): ${err.message}`);
      } else {
        console.error('Failed to send message:', err);
      }
    }
  };

  return (
    <div className="chat-application">
      <header>
        <h1>{sessionTitle}</h1>
        <button onClick={handleNewChat}>New Chat</button>
      </header>

      <main className="chat-area">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome">
              <h2>Start a Conversation</h2>
              <p>Send your first message to begin</p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`message message-${msg.role}`}>
              <div className="message-role">{msg.role === 'user' ? 'You' : 'Assistant'}</div>
              <div className="message-content">{msg.content}</div>
              {msg.timestamp && (
                <div className="message-time">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              )}
            </div>
          ))}

          {isStreaming && (
            <div className="message message-assistant streaming">
              <div className="message-role">Assistant</div>
              <div className="message-content">
                {currentMessage}
                <span className="typing-indicator">▌</span>
              </div>
              <div className="token-counter">Tokens: {tokenCount}</div>
            </div>
          )}

          {error && (
            <div className="message message-error">
              <div className="error-header">
                <strong>{error.code}</strong>
                <button onClick={clearError}>Dismiss</button>
              </div>
              <div className="error-message">{error.message}</div>
            </div>
          )}
        </div>
      </main>

      <footer className="input-area">
        <form onSubmit={handleSendMessage}>
          <div className="input-group">
            <input
              ref={inputRef}
              type="text"
              placeholder="Ask me anything..."
              disabled={isStreaming}
              autoFocus
            />
            <button type="submit" disabled={isStreaming || !apiKey}>
              Send
            </button>
            {isStreaming && (
              <button
                type="button"
                onClick={stopGeneration}
                className="stop-button"
              >
                Stop
              </button>
            )}
          </div>
        </form>

        <details className="settings">
          <summary>Settings</summary>
          <label>
            API Key:
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-..."
            />
          </label>
          {chatId && <p>Chat ID: {chatId}</p>}
        </details>
      </footer>
    </div>
  );
}

/**
 * Example 3: Advanced Chat with Retry Logic
 *
 * Shows how to handle errors and implement retry mechanisms
 */
export function ChatWithRetryExample() {
  const [apiKey, setApiKey] = useState('');
  const {
    messages,
    currentMessage,
    isStreaming,
    error,
    sendMessage,
    stopGeneration,
    retryLast,
    clearError,
  } = useStreamingChat({
    apiKey,
    model: 'claude-3-opus-20250219',
    apiUrl: 'http://localhost:8080',
    maxRetries: 3,
    connectionTimeout: 15000,
    streamTimeout: 45000,
    onError: (error) => {
      console.error(`Stream error [${error.code}]: ${error.message}`);
      if (error.statusCode) {
        console.error(`HTTP Status: ${error.statusCode}`);
      }
    },
  });

  const inputRef = useRef<HTMLInputElement>(null);
  const [retryAttempt, setRetryAttempt] = useState(0);

  const handleSendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!inputRef.current?.value.trim()) return;

    try {
      setRetryAttempt(0);
      await sendMessage(inputRef.current.value);
      inputRef.current.value = '';
    } catch (err) {
      if (err instanceof StreamingError) {
        console.error(`Error (${err.code}): ${err.message}`);
      }
    }
  };

  const handleRetry = async () => {
    try {
      setRetryAttempt((prev) => prev + 1);
      await retryLast();
      clearError();
    } catch (err) {
      console.error('Retry failed:', err);
    }
  };

  return (
    <div className="chat-with-retry">
      <div className="messages-list">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message msg-${msg.role}`}>
            {msg.content}
          </div>
        ))}

        {isStreaming && (
          <div className="message msg-assistant-streaming">
            {currentMessage}
          </div>
        )}
      </div>

      {error && (
        <div className="error-container">
          <p className="error-message">
            {error.message}
          </p>
          <div className="error-details">
            <p>Error Code: {error.code}</p>
            {error.statusCode && <p>HTTP Status: {error.statusCode}</p>}
            {retryAttempt < 3 && (
              <button onClick={handleRetry} className="retry-button">
                Retry Attempt {retryAttempt + 1}/3
              </button>
            )}
          </div>
        </div>
      )}

      <form onSubmit={handleSendMessage}>
        <input
          ref={inputRef}
          type="text"
          placeholder="Enter message..."
          disabled={isStreaming}
        />
        <button type="submit" disabled={isStreaming}>
          Send
        </button>
        {isStreaming && (
          <button type="button" onClick={stopGeneration}>
            Cancel
          </button>
        )}
      </form>

      <input
        type="password"
        value={apiKey}
        onChange={(e) => setApiKey(e.target.value)}
        placeholder="API Key"
      />
    </div>
  );
}

/**
 * Example 4: Chat with Custom Callbacks
 *
 * Demonstrates using onToken and onComplete callbacks for real-time updates
 */
export function ChatWithCallbacksExample() {
  const [apiKey, setApiKey] = useState('');
  const [tokenStream, setTokenStream] = useState<string>('');
  const [completionTime, setCompletionTime] = useState<number | null>(null);
  const startTimeRef = useRef<number>(0);

  const {
    messages,
    currentMessage,
    isStreaming,
    sendMessage,
  } = useStreamingChat({
    apiKey,
    model: 'claude-3-opus-20250219',
    apiUrl: 'http://localhost:8080',
    onToken: (token) => {
      // Called for each token as it arrives
      setTokenStream((prev) => prev + token);
      console.log(`Token: "${token}"`);
    },
    onComplete: (message) => {
      // Called when message completes
      const elapsed = Date.now() - startTimeRef.current;
      setCompletionTime(elapsed);
      console.log(`Completed in ${elapsed}ms, length: ${message.length}`);
    },
    onError: (error) => {
      console.error(`Error: ${error.message}`);
    },
  });

  const handleSendMessage = async (text: string) => {
    setTokenStream('');
    setCompletionTime(null);
    startTimeRef.current = Date.now();

    try {
      await sendMessage(text);
    } catch (err) {
      console.error('Failed to send:', err);
    }
  };

  return (
    <div className="callback-demo">
      <div className="section">
        <h3>Messages</h3>
        {messages.map((msg, idx) => (
          <p key={idx}>
            <strong>{msg.role}:</strong> {msg.content}
          </p>
        ))}
      </div>

      <div className="section">
        <h3>Real-time Token Stream</h3>
        <pre className="token-display">
          {isStreaming ? tokenStream + '▌' : tokenStream}
        </pre>
      </div>

      {completionTime && (
        <div className="section">
          <h3>Performance Metrics</h3>
          <p>Completion Time: {completionTime}ms</p>
          <p>Average Token Rate: {Math.round((currentMessage.length / completionTime) * 1000)} tokens/sec</p>
        </div>
      )}

      <div className="controls">
        <input
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="API Key"
        />
        <button
          onClick={() => handleSendMessage('Hello!')}
          disabled={isStreaming}
        >
          Test Message
        </button>
      </div>
    </div>
  );
}

/**
 * Example 5: Multi-turn Conversation with System Prompt
 *
 * Shows how to maintain conversation history with a custom system prompt
 */
export function MultiTurnConversationExample() {
  const [apiKey, setApiKey] = useState('');
  const [systemPrompt, setSystemPrompt] = useState(
    'You are an expert software engineer. Provide detailed, code-focused answers.'
  );

  const {
    messages,
    currentMessage,
    isStreaming,
    sendMessage,
    stopGeneration,
  } = useStreamingChat({
    apiKey,
    model: 'claude-3-opus-20250219',
    apiUrl: 'http://localhost:8080',
    system: systemPrompt,
    temperature: 0.5, // Lower temperature for technical consistency
  });

  const inputRef = useRef<HTMLInputElement>(null);

  const handleSendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!inputRef.current?.value.trim()) return;

    try {
      await sendMessage(inputRef.current.value);
      inputRef.current.value = '';
    } catch (err) {
      console.error('Error:', err);
    }
  };

  return (
    <div className="conversation-app">
      <div className="system-prompt-editor">
        <label>
          System Prompt:
          <textarea
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            placeholder="Enter system prompt..."
            disabled={messages.length > 0}
            rows={3}
          />
        </label>
        {messages.length > 0 && (
          <p className="hint">System prompt locked after first message</p>
        )}
      </div>

      <div className="conversation-history">
        {messages.map((msg, idx) => (
          <div key={idx} className={`exchange exchange-${msg.role}`}>
            <div className="message">
              <strong>{msg.role}:</strong>
              <p>{msg.content}</p>
            </div>
          </div>
        ))}

        {isStreaming && (
          <div className="exchange exchange-assistant streaming">
            <div className="message">
              <strong>Assistant:</strong>
              <p>{currentMessage}▌</p>
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSendMessage} className="message-input">
        <input
          ref={inputRef}
          type="text"
          placeholder="Ask a technical question..."
          disabled={isStreaming}
        />
        <button type="submit" disabled={isStreaming}>
          Send
        </button>
        {isStreaming && (
          <button type="button" onClick={stopGeneration}>
            Stop
          </button>
        )}
      </form>

      <div className="config">
        <input
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="OpenWebUI API Key"
        />
      </div>
    </div>
  );
}

export default BasicChatExample;
