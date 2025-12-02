import React, { useState } from 'react';
import StreamingMessage, { StreamingMessageProps } from './StreamingMessage';

/**
 * Storybook Stories for StreamingMessage Component
 *
 * Demonstrates all component states and usage patterns.
 */

export default {
  title: 'Components/StreamingMessage',
  component: StreamingMessage,
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    isStreaming: {
      control: { type: 'boolean' },
      description: 'Currently receiving tokens',
    },
    isComplete: {
      control: { type: 'boolean' },
      description: 'Stream has finished',
    },
    showCursor: {
      control: { type: 'boolean' },
      description: 'Show blinking cursor while streaming',
    },
    onCancel: {
      action: 'cancelled',
      description: 'Callback when generation is cancelled',
    },
  },
};

// Default story
export const Default = (args: StreamingMessageProps) => (
  <StreamingMessage {...args} />
);

Default.args = {
  content:
    'The StreamingMessage component progressively reveals text with smooth animations, perfect for displaying AI-generated responses in real-time.',
  isStreaming: false,
  isComplete: true,
  showCursor: true,
};

// Streaming state - demonstrates real-time token appearance
export const Streaming = (args: StreamingMessageProps) => {
  const [content, setContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(true);

  React.useEffect(() => {
    const fullText =
      'Streaming real-time responses with token-by-token animation creates an engaging user experience. Each token appears smoothly as it arrives from the API, providing immediate feedback to the user that generation is in progress.';

    let charIndex = 0;
    const interval = setInterval(() => {
      if (charIndex <= fullText.length) {
        setContent(fullText.slice(0, charIndex));
        charIndex += 3; // Simulate token batching
      } else {
        clearInterval(interval);
        setIsStreaming(false);
      }
    }, 50);

    return () => clearInterval(interval);
  }, []);

  return (
    <StreamingMessage
      {...args}
      content={content}
      isStreaming={isStreaming}
      isComplete={!isStreaming}
    />
  );
};

// Error state
export const Error = (args: StreamingMessageProps) => (
  <StreamingMessage
    {...args}
    content="Failed to generate response"
    isStreaming={false}
    isComplete={false}
    error="Connection timeout: No data received for 30 seconds"
    onRetry={() => alert('Retry clicked')}
  />
);

// Long message with virtualization
export const LongMessage = (args: StreamingMessageProps) => (
  <StreamingMessage
    {...args}
    content={
      'Lorem ipsum dolor sit amet, consectetur adipiscing elit. ' +
      'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ' +
      'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris. ' +
      'Nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit. ' +
      'In voluptate velit esse cillum dolore eu fugiat nulla pariatur. ' +
      'Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia. ' +
      'Deserunt mollit anim id est laborum. '.repeat(5)
    }
    isStreaming={false}
    isComplete={true}
  />
);

// Empty state
export const Empty = (args: StreamingMessageProps) => (
  <StreamingMessage
    {...args}
    content=""
    isStreaming={true}
    isComplete={false}
  />
);

// Completed streaming
export const Completed = (args: StreamingMessageProps) => (
  <StreamingMessage
    {...args}
    content="This message has completed streaming and shows the response complete indicator."
    isStreaming={false}
    isComplete={true}
  />
);

// Interactive demo - shows cancellation
export const InteractiveDemo = () => {
  const [content, setContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startStreaming = () => {
    setContent('');
    setIsStreaming(true);
    setIsComplete(false);
    setError(null);

    const fullText =
      'This is an interactive demo of the StreamingMessage component. ' +
      'Click the "Stop" button to cancel the streaming, or let it complete naturally. ' +
      'The component handles all states smoothly with proper accessibility support.';

    let charIndex = 0;
    const interval = setInterval(() => {
      if (charIndex <= fullText.length) {
        setContent(fullText.slice(0, charIndex));
        charIndex += 2;
      } else {
        clearInterval(interval);
        setIsStreaming(false);
        setIsComplete(true);
      }
    }, 30);

    return () => clearInterval(interval);
  };

  const handleCancel = () => {
    setIsStreaming(false);
    setIsComplete(true);
  };

  const handleRetry = () => {
    startStreaming();
  };

  return (
    <div style={{ maxWidth: '600px', padding: '2rem' }}>
      <div style={{ marginBottom: '1rem' }}>
        <button
          onClick={startStreaming}
          disabled={isStreaming}
          style={{
            padding: '0.5rem 1rem',
            marginRight: '0.5rem',
            cursor: isStreaming ? 'not-allowed' : 'pointer',
          }}
        >
          Start Streaming
        </button>
        <button
          onClick={() => {
            setError('Simulated API error: Connection failed');
            setIsStreaming(false);
          }}
          style={{
            padding: '0.5rem 1rem',
            cursor: 'pointer',
          }}
        >
          Simulate Error
        </button>
      </div>

      <StreamingMessage
        content={content}
        isStreaming={isStreaming}
        isComplete={isComplete}
        error={error}
        onCancel={handleCancel}
        onRetry={error ? handleRetry : undefined}
        ariaLabel="Generated response"
      />
    </div>
  );
};

// Code block example
export const CodeExample = (args: StreamingMessageProps) => (
  <StreamingMessage
    {...args}
    content={`function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

const result = fibonacci(10); // Returns 55`}
    isStreaming={false}
    isComplete={true}
  />
);

// Markdown-like content
export const MarkdownContent = (args: StreamingMessageProps) => (
  <StreamingMessage
    {...args}
    content={`## Key Points:

1. **Fast**: Token-by-token rendering with 60fps animations
2. **Accessible**: Full ARIA support for screen readers
3. **Performant**: RequestAnimationFrame batching and memoization
4. **Reliable**: Graceful error handling and retry logic

The StreamingMessage component is production-ready and handles all edge cases properly.`}
    isStreaming={false}
    isComplete={true}
  />
);
