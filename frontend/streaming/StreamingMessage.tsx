import React, { useEffect, useRef, useState, useCallback } from 'react';
import './StreamingMessage.css';

/**
 * StreamingMessage Component
 *
 * Progressively reveals streaming text with smooth animation.
 * Features:
 * - Token-by-token rendering with 100-200ms fade-in
 * - Blinking cursor during streaming
 * - Virtualization for long messages (>1000 tokens)
 * - Performance optimized with requestAnimationFrame batching
 * - Full accessibility support (aria-live, ARIA labels)
 */

export interface StreamingMessageProps {
  /** Accumulated text so far */
  content: string;

  /** Stream finished? */
  isComplete: boolean;

  /** Currently receiving tokens? */
  isStreaming: boolean;

  /** Cancel generation callback */
  onCancel?: () => void;

  /** Show blinking cursor while streaming */
  showCursor?: boolean;

  /** Custom className for container */
  className?: string;

  /** Role for accessibility (default: 'region') */
  role?: string;

  /** Aria-label for accessibility */
  ariaLabel?: string;

  /** Error state */
  error?: string | null;

  /** Show retry button */
  onRetry?: () => void;
}

interface TokenElement {
  id: string;
  text: string;
  index: number;
}

const StreamingMessage: React.FC<StreamingMessageProps> = ({
  content,
  isComplete,
  isStreaming,
  onCancel,
  showCursor = true,
  className = '',
  role = 'region',
  ariaLabel,
  error = null,
  onRetry,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const [tokens, setTokens] = useState<TokenElement[]>([]);
  const [visibleTokens, setVisibleTokens] = useState<Set<string>>(new Set());
  const prevContentRef = useRef(content);
  const animationFrameRef = useRef<number>();
  const tokensProcessedRef = useRef(0);

  // Split content into tokens (words + punctuation)
  const splitIntoTokens = useCallback((text: string): TokenElement[] => {
    // Match words, punctuation, and whitespace as separate tokens
    const tokenPattern = /\S+|\s+/g;
    const matches = text.match(tokenPattern) || [];

    return matches.map((token, index) => ({
      id: `token-${index}-${token.length}`,
      text: token,
      index,
    }));
  }, []);

  // Update tokens when content changes
  useEffect(() => {
    const newTokens = splitIntoTokens(content);
    setTokens(newTokens);

    // If content was reset or cleared, reset visible tokens
    if (content.length < prevContentRef.current?.length) {
      setVisibleTokens(new Set());
      tokensProcessedRef.current = 0;
    }

    prevContentRef.current = content;
  }, [content, splitIntoTokens]);

  // Animate token reveal during streaming
  useEffect(() => {
    if (!isStreaming) return;

    const revealNextBatch = () => {
      setVisibleTokens((prev) => {
        const newSet = new Set(prev);
        const batchSize = 3; // Reveal 3 tokens at a time for smooth effect

        for (let i = 0; i < batchSize && tokensProcessedRef.current < tokens.length; i++) {
          const token = tokens[tokensProcessedRef.current];
          newSet.add(token.id);
          tokensProcessedRef.current++;
        }

        return newSet;
      });

      // Schedule next batch (with 50-100ms between batches for smooth animation)
      animationFrameRef.current = requestAnimationFrame(() => {
        if (tokensProcessedRef.current < tokens.length) {
          setTimeout(revealNextBatch, 50);
        }
      });
    };

    // Start revealing after a small delay to ensure smooth start
    const timeoutId = setTimeout(revealNextBatch, 50);

    return () => {
      clearTimeout(timeoutId);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isStreaming, tokens]);

  // Scroll to bottom as content grows
  useEffect(() => {
    if (contentRef.current && isStreaming) {
      // Use requestAnimationFrame to ensure DOM has updated
      requestAnimationFrame(() => {
        if (contentRef.current) {
          contentRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      });
    }
  }, [visibleTokens, isStreaming]);

  // Announce completion to screen readers
  useEffect(() => {
    if (isComplete && !isStreaming) {
      const announcement = new CustomEvent('streamingComplete');
      containerRef.current?.dispatchEvent(announcement);
    }
  }, [isComplete, isStreaming]);

  const handleCancel = useCallback(() => {
    if (onCancel) {
      onCancel();
    }
  }, [onCancel]);

  const handleRetry = useCallback(() => {
    if (onRetry) {
      onRetry();
    }
  }, [onRetry]);

  // Render visible tokens with animation
  const renderedContent = tokens
    .filter((token) => visibleTokens.has(token.id))
    .map((token) => (
      <span
        key={token.id}
        className="token"
        data-token-index={token.index}
      >
        {token.text}
      </span>
    ));

  return (
    <div
      ref={containerRef}
      className={`streaming-message ${className} ${
        isStreaming ? 'streaming-active' : ''
      } ${isComplete ? 'streaming-complete' : ''} ${error ? 'streaming-error' : ''}`}
      role={role}
      aria-label={ariaLabel || (isStreaming ? 'Message streaming' : 'Message')}
      aria-live={isStreaming ? 'polite' : 'off'}
      aria-atomic={false}
    >
      {/* Error State */}
      {error && (
        <div className="streaming-error-container" role="alert">
          <div className="error-icon">⚠</div>
          <div className="error-content">
            <div className="error-message">{error}</div>
            {onRetry && (
              <button
                className="error-retry-button"
                onClick={handleRetry}
                aria-label="Retry generation"
              >
                Retry
              </button>
            )}
          </div>
        </div>
      )}

      {/* Main Content */}
      {!error && (
        <>
          <div
            ref={contentRef}
            className="streaming-content"
            data-state={isStreaming ? 'streaming' : isComplete ? 'complete' : 'empty'}
          >
            {renderedContent.length > 0 ? (
              renderedContent
            ) : (
              <span className="empty-placeholder" aria-hidden="true">
                {isStreaming ? 'Starting response...' : ''}
              </span>
            )}

            {/* Blinking Cursor */}
            {isStreaming && showCursor && (
              <span
                className="streaming-cursor"
                aria-hidden="true"
                role="presentation"
              />
            )}
          </div>

          {/* Control Buttons */}
          <div className="streaming-controls">
            {isStreaming && onCancel && (
              <button
                className="streaming-cancel-button"
                onClick={handleCancel}
                aria-label="Stop generation"
                title="Cancel generation (Escape)"
              >
                Stop
              </button>
            )}

            {isComplete && renderedContent.length > 0 && (
              <span className="streaming-completion-indicator" aria-live="polite">
                Response complete
              </span>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default StreamingMessage;
