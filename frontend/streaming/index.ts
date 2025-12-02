/**
 * Streaming Message Module
 *
 * Provides token-by-token streaming UI component for real-time AI responses.
 *
 * Citation: if://citation/streaming-ui-component-20251130
 * Component implements A18 requirements: <250ms first token, 60fps animation, accessibility
 */

export { default as StreamingMessage } from './StreamingMessage';
export type { StreamingMessageProps } from './StreamingMessage';

export { useStreamingChat } from './useStreamingChat';
export type {
  ChatMessage,
  StreamDelta,
  StreamChoice,
  StreamResponse,
  StreamingError,
  UseStreamingChatOptions,
  UseStreamingChatState,
  UseStreamingChatReturn,
} from './useStreamingChat';

// CSS must be imported by parent component or build system:
// import './StreamingMessage.css';
