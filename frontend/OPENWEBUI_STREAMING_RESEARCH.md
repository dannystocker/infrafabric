# OpenWebUI React Frontend Streaming Architecture Research

**Agent:** A16 - Research OpenWebUI React Frontend Streaming Structure
**Date:** 2025-11-30
**Status:** Research Complete
**Sources:** if-emotion-ux project (OpenWebUI-compatible React frontend)

---

## Executive Summary

The if-emotion-ux project implements a complete OpenWebUI-compatible React frontend with working SSE (Server-Sent Events) streaming. The implementation uses:

- **ReadableStreamDefaultReader API** for low-level streaming (not EventSource)
- **Response.body.getReader()** to consume fetch response streams
- **React hooks** (useState, useRef, useEffect) for state management
- **Token-by-token streaming** with TextDecoder for SSE parsing
- **Optimistic UI updates** - messages appear as content streams in

The frontend demonstrates production-ready patterns for:
- Streaming response consumption
- Progressive message rendering
- Error handling and fallbacks
- Session/chat persistence
- State management without Redux

---

## Architecture Overview

### High-Level Data Flow

```
┌──────────────────────────────────┐
│   React Component (App.tsx)      │
│  - State: messages, sessions     │
│  - Handlers: handleSend()        │
└───────────────┬──────────────────┘
                │
                ▼
┌──────────────────────────────────┐
│  OpenWebUIClient Service         │
│  (services/openwebui.ts)         │
│  - sendMessage()                 │
│  - Returns ReadableStreamReader  │
└───────────────┬──────────────────┘
                │
                ▼
┌──────────────────────────────────┐
│  Backend: /api/chat/completions  │
│  (Server-Sent Events Stream)     │
│  Response format: data: {...}    │
└──────────────────────────────────┘
```

### Component Hierarchy

```
App (Main Container)
├── JourneyHeader (Top bar with menu, privacy toggle)
├── Sidebar (Session list, grouped by date)
├── MessageContainer (Scrolling message list)
│   ├── ChatMessage[] (Rendered messages)
│   │   ├── MessageBubble (Styled container)
│   │   ├── ReactMarkdown (Content renderer)
│   │   └── MessageActions (Delete button)
│   └── messagesEndRef (Auto-scroll target)
└── ChatInput (Text input + Send button)
```

---

## 1. Streaming Connection Mechanism

### 1.1 Service Layer: OpenWebUIClient

**File:** `/home/setup/if-emotion-ux/services/openwebui.ts`

The client uses **low-level fetch streaming** rather than EventSource:

```typescript
// Send message (returns stream reader)
async sendMessage(
  chatId: string | null,
  content: string,
  history: Message[],
  model: string,
  offTheRecord: boolean = false
): Promise<ReadableStreamDefaultReader<Uint8Array>> {

  const payload: any = {
    model: model,
    messages: contextMessages,
    stream: true,  // Enable streaming
  };

  const endpoint = `${this.config.baseUrl}/api/chat/completions`;

  const res = await fetch(endpoint, {
    method: 'POST',
    headers: this.headers,
    body: JSON.stringify(payload)
  });

  if (!res.body) throw new Error('No response body');
  return res.body.getReader();  // Return stream reader
}
```

**Key Pattern:**
- Uses `Response.body.getReader()` for raw binary streaming
- Returns `ReadableStreamDefaultReader<Uint8Array>` for consumption
- Avoids EventSource API entirely - uses fetch streaming instead

### 1.2 Backend: Server-Sent Events Streaming

**File:** `/home/setup/if-emotion-ux/backend/openwebui_server.py`

The Flask backend implements SSE streaming:

```python
@app.route('/api/chat/completions', methods=['POST'])
def chat_completions():
    """OpenAI-compatible chat completions endpoint with streaming"""
    data = request.get_json()
    messages = data.get('messages', [])
    model = data.get('model', DEFAULT_MODEL)
    stream = data.get('stream', True)

    if stream:
        return Response(
            stream_response(api_messages, model),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )

def stream_response(messages, model):
    """Stream response from LLM API"""
    try:
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={...},
            json={
                'model': model,
                'messages': messages,
                'stream': True,
                ...
            },
            stream=True  # Request streaming from upstream
        )

        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    yield line_str + '\n\n'  # Pass through SSE format

    except Exception as e:
        error_data = {...}
        yield f'data: {json.dumps(error_data)}\n\n'

    yield 'data: [DONE]\n\n'  # Signal completion
```

**Key Pattern:**
- Uses Flask `Response()` with generator for streaming
- Passes through upstream SSE format (`data: ...`)
- Handles errors gracefully mid-stream
- Signals completion with `[DONE]` token

**SSE Format:**
```
data: {"choices": [{"delta": {"content": "Hello"}, ...}]}

data: {"choices": [{"delta": {"content": " world"}, ...}]}

data: [DONE]
```

---

## 2. React Streaming Implementation

### 2.1 Main Component: App.tsx

**File:** `/home/setup/if-emotion-ux/App.tsx` (lines 134-218)

The `handleSend()` function implements the complete streaming flow:

```typescript
const handleSend = async (text: string) => {
  const userMsg: Message = {
    id: generateId(),
    role: Role.USER,
    content: text,
    timestamp: new Date()
  };

  // 1. Add user message to UI immediately (optimistic)
  setMessages(prev => [...prev, userMsg]);
  setIsLoading(true);

  try {
    // 2. Persist user message if not in privacy mode
    if (!isOffTheRecord && currentSessionId) {
      await clientRef.current.addMessageToChat(currentSessionId, userMsg)
        .catch(e => console.warn("Failed to persist user msg", e));
    }

    // 3. Get streaming response from service
    const modelToUse = selectedModel || availableModels[0] || 'gpt-3.5-turbo';
    const streamReader = await clientRef.current.sendMessage(
      currentSessionId,
      text,
      messages,
      modelToUse,
      isOffTheRecord
    );

    // 4. Create bot message placeholder
    const botMsgId = generateId();
    const botMsg: Message = {
      id: botMsgId,
      role: Role.ASSISTANT,
      content: '',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, botMsg]);

    // 5. Stream and decode chunks
    const decoder = new TextDecoder();
    let fullContent = '';

    while (true) {
      const { done, value } = await streamReader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6);
          if (dataStr === '[DONE]') continue;

          try {
            const data = JSON.parse(dataStr);
            const content = data.choices?.[0]?.delta?.content || '';

            if (content) {
              fullContent += content;

              // 6. Update UI with accumulated content (token-by-token)
              setMessages(prev =>
                prev.map(m =>
                  m.id === botMsgId
                    ? { ...m, content: fullContent }
                    : m
                )
              );
            }
          } catch (e) {
            // Ignore parse errors for partial chunks
          }
        }
      }
    }

    // 7. Persist completed message
    if (!isOffTheRecord && currentSessionId) {
      const completedBotMsg = { ...botMsg, content: fullContent };
      await clientRef.current.addMessageToChat(currentSessionId, completedBotMsg)
        .catch(e => console.warn("Failed to persist bot msg", e));
      loadSessions(); // Update timestamp
    }

  } catch (e) {
    console.error("Error sending message", e);
    setMessages(prev => [...prev, {
      id: generateId(),
      role: Role.SYSTEM,
      content: "The connection wavered. Please try again.",
      timestamp: new Date(),
      error: true
    }]);
  } finally {
    setIsLoading(false);
  }
};
```

**Key Streaming Patterns:**

1. **Optimistic UI**: User message appears immediately
2. **Streaming Loop**:
   - Uses `while(true)` with `streamReader.read()`
   - `TextDecoder` converts bytes to UTF-8 strings
   - Handles partial chunks (split by `\n`)
3. **Token Accumulation**: Builds `fullContent` incrementally
4. **Real-time Rendering**: Updates state on every token
5. **Error Handling**: Graceful parsing error recovery
6. **Completion Signal**: Exits on `[DONE]` token

### 2.2 React Hooks Used

**State Management (useState):**
- `messages`: Message[] - Current conversation
- `sessions`: Session[] - All persisted chats
- `currentSessionId`: string | null - Active chat
- `isLoading`: boolean - Streaming indicator
- `selectedModel`: string - Current LLM model
- `isOffTheRecord`: boolean - Privacy toggle

**Side Effects (useEffect):**
```typescript
useEffect(() => {
  clientRef.current = new OpenWebUIClient(settings);
  localStorage.setItem('if.emotion.settings', JSON.stringify(settings));
  loadModels();
  if (!isOffTheRecord) {
    loadSessions();
  }
}, [settings]);
```

**Refs:**
- `clientRef`: Persistent OpenWebUIClient instance
- `messagesEndRef`: Auto-scroll to latest message

---

## 3. Component Integration Points

### 3.1 ChatMessage Component

**File:** `/home/setup/if-emotion-ux/components/ChatMessage.tsx`

Renders individual messages with streaming support:

```typescript
export function ChatMessage({ message, onDelete }: Props) {
  const isUser = message.role === Role.USER;

  return (
    <div className={`group flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`relative max-w-[85%] md:max-w-[70%]`}>

        {/* Message Bubble - Supports Markdown */}
        <div className={`relative px-6 py-4 rounded-message shadow-sm`}>
          <div className={`prose prose-sm max-w-none`}>
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        </div>

        {/* Timestamp & Actions */}
        <div className="flex items-center gap-3 mt-1.5">
          <time className="text-xs text-sergio-500">
            {formatConversationalTime(message.timestamp)}
          </time>
          <MessageActions messageId={message.id} onDelete={onDelete} />
        </div>

      </div>
    </div>
  );
}
```

**Key Integration Points:**
- `message.content` supports partial content (streaming updates)
- **ReactMarkdown** renders markdown progressively
- Component re-renders as content updates
- **No loading indicators** - content renders as it arrives

### 3.2 ChatInput Component

**File:** `/home/setup/if-emotion-ux/components/ChatInput.tsx`

Input with send trigger and privacy toggle:

```typescript
export function ChatInput({
  onSend,
  isLoading,  // Used to disable input during streaming
  disabled,
  isOffTheRecord,
  onToggleOffTheRecord
}: Props) {
  const [input, setInput] = useState('');

  const handleSubmit = () => {
    if (input.trim() && !isLoading && !disabled) {
      onSend(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-6">
      <textarea
        value={input}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        disabled={disabled || isLoading}  // Disable during streaming
        placeholder={isOffTheRecord ? "Speak freely (not saved)..." : "Write to your future self..."}
        rows={1}
      />
      <button
        onClick={handleSubmit}
        disabled={!input.trim() || isLoading || disabled}
      >
        {isLoading ? <Loader2 className="animate-spin" /> : <SendHorizontal />}
      </button>

      {/* Privacy Toggle */}
      <button onClick={onToggleOffTheRecord}>
        {isOffTheRecord ? <EyeOff /> : <Eye />}
        <span>{isOffTheRecord ? "Save: OFF" : "Save: ON"}</span>
      </button>
    </div>
  );
}
```

**Key Integration Points:**
- `isLoading` prop disables input during streaming
- Loading spinner replaces send icon during request
- Privacy toggle switches between persistent/ephemeral mode

### 3.3 Sidebar Component

**File:** `/home/setup/if-emotion-ux/components/Sidebar.tsx`

Session management with date grouping:

```typescript
export function Sidebar({
  isOpen,
  sessions,
  currentSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession
}: Props) {
  // Group sessions by date
  const groupedSessions = sessions.reduce((acc, session) => {
    const timestamp = session.updated_at * 1000;
    const date = new Date(timestamp);

    let key = 'Older';
    if (isToday(date)) key = 'Today';
    else if (isYesterday(date)) key = 'Yesterday';

    if (!acc[key]) acc[key] = [];
    acc[key].push(session);
    return acc;
  }, {});

  return (
    <div className="fixed w-[280px] h-full bg-sergio-100">
      <button onClick={onNewChat}>New Session</button>

      {Object.keys(groupedSessions).map(group => (
        <div key={group}>
          <h3>{group}</h3>
          {groupedSessions[group].map(session => (
            <SessionItem
              key={session.id}
              session={session}
              isActive={session.id === currentSessionId}
              onSelect={() => onSelectSession(session.id)}
              onDelete={() => onDeleteSession(session.id)}
            />
          ))}
        </div>
      ))}
    </div>
  );
}
```

---

## 4. State Management Architecture

### 4.1 Component-Level State (No Redux/Context)

**In App.tsx:**

```typescript
// Session/Chat State
const [sessions, setSessions] = useState<Session[]>([]);
const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
const [messages, setMessages] = useState<Message[]>([]);

// UI State
const [isLoading, setIsLoading] = useState(false);
const [isSidebarOpen, setIsSidebarOpen] = useState(false);
const [isOffTheRecord, setIsOffTheRecord] = useState(false);

// Settings/Models
const [selectedModel, setSelectedModel] = useState<string>('');
const [availableModels, setAvailableModels] = useState<string[]>([]);
const [settings, setSettings] = useState<UserSettings>(() => {
  const saved = localStorage.getItem('if.emotion.settings');
  return saved ? JSON.parse(saved) : { baseUrl: window.location.origin, apiKey: 'if-emotion-local' };
});
```

**Props Down, Callbacks Up Pattern:**
- Parent (App) holds all state
- Components receive data + callbacks as props
- No Context API or Redux used (simple app scope)

### 4.2 Message Types

**File:** `/home/setup/if-emotion-ux/types.ts`

```typescript
export interface Message {
  id: string;
  role: Role;
  content: string;  // Supports partial content during streaming
  timestamp: Date;
  pending?: boolean;
  error?: boolean;
  reactions?: string[];
}

export enum Role {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system'
}

export interface Session {
  id: string;
  title: string;
  updated_at: number;  // Unix timestamp for sorting
  folder_id?: string;
}

export interface OpenWebUIConfig {
  baseUrl: string;
  apiKey: string;
}
```

---

## 5. Error Handling & Resilience

### 5.1 Streaming Error Recovery

In `handleSend()`:

```typescript
const decoder = new TextDecoder();
let fullContent = '';

while (true) {
  const { done, value } = await streamReader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const dataStr = line.slice(6);
      if (dataStr === '[DONE]') continue;

      try {
        const data = JSON.parse(dataStr);
        const content = data.choices?.[0]?.delta?.content || '';

        if (content) {
          fullContent += content;
          setMessages(prev => prev.map(m =>
            m.id === botMsgId ? { ...m, content: fullContent } : m
          ));
        }
      } catch (e) {
        // Silently ignore JSON parse errors from partial chunks
        // Content accumulated so far is retained
      }
    }
  }
}
```

**Error Patterns:**
- **Parse Errors**: Caught and ignored - partial content preserved
- **Network Errors**: Caught in outer try/catch, error message shown
- **Connection Loss**: Stream ends, message saved with whatever content arrived
- **Backend Errors**: SSE error format handled gracefully

### 5.2 Fallback Error UI

```typescript
} catch (e) {
  console.error("Error sending message", e);
  setMessages(prev => [...prev, {
    id: generateId(),
    role: Role.SYSTEM,
    content: "The connection wavered. Please try again.",
    timestamp: new Date(),
    error: true
  }]);
}
```

---

## 6. Reusable Patterns for Integration

### 6.1 Streaming Hook Pattern (Recommended Enhancement)

Current implementation is inline. Could be extracted:

```typescript
// Hypothetical hook (not in current code)
function useStreamingChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const streamMessage = useCallback(async (
    client: OpenWebUIClient,
    userContent: string,
    context: Message[]
  ) => {
    setIsLoading(true);
    try {
      const reader = await client.sendMessage(...);
      const decoder = new TextDecoder();
      let fullContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        // ... parse and accumulate
        setMessages(prev => [...prev, { id, role: Role.ASSISTANT, content: fullContent }]);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { messages, isLoading, streamMessage };
}
```

### 6.2 SSE Parser Utility

Current implementation parses inline. Could be extracted:

```typescript
// Hypothetical utility
function parseSSELine(line: string): Record<string, any> | null {
  if (!line.startsWith('data: ')) return null;

  const dataStr = line.slice(6);
  if (dataStr === '[DONE]') return { type: 'DONE' };

  try {
    return JSON.parse(dataStr);
  } catch (e) {
    return null;
  }
}

function extractDelta(data: Record<string, any>): string {
  return data.choices?.[0]?.delta?.content || '';
}
```

### 6.3 Loading State Management

Pattern for showing typing indicators while streaming:

```typescript
// Hypothetical extension
const [streamingStatus, setStreamingStatus] = useState<{
  isStreaming: boolean;
  tokensReceived: number;
  lastTokenTime: number;
}>({ isStreaming: false, tokensReceived: 0, lastTokenTime: 0 });

// In streaming loop:
if (content) {
  fullContent += content;
  setStreamingStatus(prev => ({
    isStreaming: true,
    tokensReceived: prev.tokensReceived + 1,
    lastTokenTime: Date.now()
  }));

  // Update UI with token count
}
```

---

## 7. Message Persistence Layer

### 7.1 Lifecycle: Stream → Persist

```
1. User types message
   ↓
2. handleSend() called
   ↓
3. Message added to state immediately (optimistic)
   ↓
4. If persistent: POST to /api/chats/{id}/messages
   ↓
5. Stream response from /api/chat/completions
   ↓
6. Accumulate content in fullContent variable
   ↓
7. Re-render on each token (setMessages with updated content)
   ↓
8. Stream ends ([DONE] received)
   ↓
9. POST completed message to /api/chats/{id}/messages
   ↓
10. loadSessions() to update sidebar timestamps
```

### 7.2 API Endpoints Used

**OpenWebUI-Compatible Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/models` | GET | List available LLM models |
| `/api/version` | GET | Check backend connection |
| `/api/chats` | GET | Get all sessions |
| `/api/chats/new` | POST | Create new session |
| `/api/chats/{id}` | GET | Get session + messages |
| `/api/chats/{id}` | DELETE | Delete session |
| `/api/chats/{id}/messages` | POST | Add message to session |
| `/api/chats/{id}/messages/{msgId}` | DELETE | Delete single message (silent) |
| `/api/chat/completions` | POST | Stream LLM response (SSE) |

---

## 8. Performance Considerations

### 8.1 Streaming Performance

**Positive:**
- Token-by-token UI updates (no buffering)
- Perceived responsiveness - content appears immediately
- Memory efficient - doesn't buffer entire response in memory

**Potential Issues:**
- **Re-render thrashing**: Every token causes full re-render of message
  - Could optimize with `useCallback` + memo components
- **State mutation in loop**: Tight update loop could overwhelm React
  - Could batch updates with `flushSync` or debounce

### 8.2 Optimization Opportunities

```typescript
// Current: Re-renders entire component tree per token
setMessages(prev => prev.map(m =>
  m.id === botMsgId ? { ...m, content: fullContent } : m
));

// Better: Use useReducer + memoized components
dispatch({ type: 'UPDATE_MESSAGE', id: botMsgId, content: fullContent });

// Or: Debounce updates every 50ms instead of per-token
const updateMessage = debounce((content: string) => {
  setMessages(prev => prev.map(m =>
    m.id === botMsgId ? { ...m, content } : m
  ));
}, 50);
```

---

## 9. Integration Points for YoloGuard

### 9.1 Proposed Modifications

Based on this architecture, YoloGuard integration would:

1. **Wrap OpenWebUIClient:**
   ```typescript
   class GuardedOpenWebUIClient extends OpenWebUIClient {
     async sendMessage(...) {
       // Add IF.guard preprocessing
       const guardAnalysis = await analyzeMessage(content);

       // Call parent
       return super.sendMessage(...);
     }
   }
   ```

2. **Intercept Streaming Response:**
   ```typescript
   // In handleSend, after decoder:
   const chunk = decoder.decode(value);
   const guardedChunk = await applyGuardToChunk(chunk);
   // Proceed with guardedChunk
   ```

3. **Add Guard Status Indicator:**
   ```typescript
   const [guardStatus, setGuardStatus] = useState<'clear' | 'warning' | 'blocked'>('clear');

   // In streaming loop:
   const guardResult = evaluateToken(content);
   setGuardStatus(guardResult.status);
   ```

4. **Extend Message Type:**
   ```typescript
   export interface Message {
     id: string;
     role: Role;
     content: string;
     timestamp: Date;
     // Guard additions:
     guardAnalysis?: GuardAnalysis;
     originalContent?: string;  // If modified
     trustScore?: number;
   }
   ```

### 9.2 Hook Points for IF.ceo Integration

- **Pre-message**: Council reviews user intent
- **During-stream**: Real-time token evaluation
- **Post-message**: Council analysis of complete response
- **Error recovery**: Fallback decision making

---

## 10. Files Summary

### Frontend Files

| File | Purpose | Lines | Key Exports |
|------|---------|-------|------------|
| `App.tsx` | Main container, state, streaming logic | 350+ | App component |
| `services/openwebui.ts` | OpenWebUI API client | 163 | OpenWebUIClient class |
| `components/ChatMessage.tsx` | Message bubble rendering | 48 | ChatMessage component |
| `components/ChatInput.tsx` | Text input + send | 93 | ChatInput component |
| `components/Sidebar.tsx` | Session list with date grouping | 100+ | Sidebar component |
| `components/JourneyHeader.tsx` | Top header bar | ~50 | JourneyHeader |
| `components/SettingsModal.tsx` | Settings UI | ~150 | SettingsModal |
| `components/ExportModal.tsx` | Export conversations | ~150 | ExportModal |
| `types.ts` | TypeScript interfaces | 57 | Message, Session, Role enums |
| `utils.ts` | Helper functions | 30+ | generateId, formatTime |
| `constants.ts` | Config constants | 50 | AppConfig |

### Backend Files

| File | Purpose | Lines | Key Endpoints |
|------|---------|-------|--------------|
| `backend/openwebui_server.py` | Flask streaming server | 350+ | /api/chat/completions, /api/chats/*, /api/chats/*/messages |

---

## 11. Architecture Diagram (Text-Based)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BROWSER (React App)                          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                          App.tsx                             │  │
│  │  State: messages, sessions, currentSessionId, isLoading     │  │
│  │  Handler: handleSend(text) → streaming loop                 │  │
│  │                                                              │  │
│  │  ├─ JourneyHeader (menu, model selector)                    │  │
│  │  ├─ Sidebar (sessions grouped by date)                      │  │
│  │  ├─ MessageList (messages with auto-scroll)                 │  │
│  │  │  └─ ChatMessage[] → ReactMarkdown (streaming content)    │  │
│  │  └─ ChatInput (textarea + send button)                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│  ┌──────────────────────────▼──────────────────────────────────┐   │
│  │        OpenWebUIClient (services/openwebui.ts)              │   │
│  │                                                              │   │
│  │  sendMessage():                                             │   │
│  │    POST /api/chat/completions                              │   │
│  │    → fetch Response.body.getReader()                       │   │
│  │    → returns ReadableStreamDefaultReader<Uint8Array>       │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
└─────────────────────────────┼──────────────────────────────────────┘
                              │ HTTP POST + streaming GET
                              │ (Response body as binary stream)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 BACKEND (Flask Server)                              │
│                                                                     │
│  POST /api/chat/completions                                        │
│    ├─ Parse request (messages, model, stream=true)                │
│    ├─ Call upstream LLM API (OpenRouter)                          │
│    └─ stream_response() generator:                                 │
│        ├─ for line in response.iter_lines():                      │
│        │   ├─ decode UTF-8                                        │
│        │   ├─ if startswith('data: '):                            │
│        │   │   └─ yield line + '\n\n' (pass through SSE)         │
│        │   └─                                                      │
│        └─ yield 'data: [DONE]\n\n'                                │
│                                                                     │
│  Response Headers:                                                  │
│    Content-Type: text/event-stream                                 │
│    Cache-Control: no-cache                                         │
│    Connection: keep-alive                                          │
│    X-Accel-Buffering: no                                          │
│                                                                     │
│  Message Endpoints (REST):                                         │
│    GET  /api/chats  → [Chat]                                      │
│    POST /api/chats/new  → Chat                                    │
│    GET  /api/chats/{id}  → Chat + messages[]                     │
│    POST /api/chats/{id}/messages  → Message                      │
│    DELETE /api/chats/{id}/messages/{id}  → void                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 12. Gaps & Recommendations

### 12.1 Missing Implementations

1. **Streaming Hook** - Currently inline in App.tsx
   - Recommendation: Extract to `useStreamingChat()` custom hook
   - Benefit: Reusable across different chat components

2. **SSE Parser Utility** - Parsing is inline
   - Recommendation: Create `parseSSEStream()` utility
   - Benefit: Testable, shareable with backends

3. **Loading Indicators** - No typing animation
   - Recommendation: Add animated "..." or blinking cursor during stream
   - Benefit: UX improvement for slower connections

4. **Token Rate Limiting** - No backpressure handling
   - Recommendation: Implement token queue if streaming too fast
   - Benefit: Prevent UI thrashing

5. **Reconnection Logic** - No automatic retry
   - Recommendation: Add exponential backoff for failed streams
   - Benefit: Better resilience to network issues

6. **Stream Cancellation** - No AbortController
   - Recommendation: Allow user to stop response mid-stream
   - Benefit: User control over long-running requests

### 12.2 Performance Optimizations

1. **Message Component Memoization**
   ```typescript
   export const ChatMessage = React.memo(ChatMessageImpl);
   ```

2. **Debounce State Updates**
   ```typescript
   const updateContent = useMemo(
     () => debounce((content: string) => setMessages(...), 50),
     []
   );
   ```

3. **Virtualization for Long Chats**
   ```typescript
   import { FixedSizeList } from 'react-window';
   // Render only visible messages
   ```

### 12.3 Features for YoloGuard Integration

1. **Pre-send Validation** - Analyze user message before streaming
2. **In-stream Monitoring** - Evaluate response content in real-time
3. **Guard Status Display** - Show council decision status
4. **Fallback Responses** - Guard-approved messages if blocked
5. **Audit Trail** - Log all guard decisions with timestamps

---

## 13. Testing Considerations

### 13.1 Unit Test Patterns

```typescript
// Testing openwebui.ts
describe('OpenWebUIClient', () => {
  it('should parse SSE chunks correctly', async () => {
    const mockResponse = new Response(
      new ReadableStream({
        start(controller) {
          controller.enqueue(
            new TextEncoder().encode('data: {"choices":[{"delta":{"content":"hello"}}]}\n\n')
          );
          controller.close();
        }
      })
    );
    // Parse and assert
  });
});

// Testing streaming integration
describe('handleSend streaming', () => {
  it('should accumulate tokens and update UI', async () => {
    const { getByText, waitFor } = render(<App />);
    // Type message, click send
    // Assert tokens appear incrementally
  });
});
```

### 13.2 Integration Test Patterns

```typescript
// E2E with mock backend
describe('E2E: Message streaming', () => {
  beforeEach(() => {
    server.listen();
  });

  it('should stream response token by token', async () => {
    // Use msw to mock /api/chat/completions
    // Stream mock response with delays
    // Assert UI updates for each token
  });
});
```

---

## 14. Deployment Checklist

- [ ] Frontend: Build React app to static assets
- [ ] Backend: Deploy Flask server with proper CORS headers
- [ ] SSL/TLS: Ensure HTTPS for security (especially if auth required)
- [ ] Streaming Headers: Verify `text/event-stream` MIME type
- [ ] Connection Pooling: Configure keep-alive on reverse proxy
- [ ] Cache Control: Set proper headers to prevent caching streams
- [ ] Error Logging: Implement server-side stream error tracking
- [ ] Rate Limiting: Add per-user request limits
- [ ] Model Selection: Ensure available models configured correctly
- [ ] API Keys: Securely manage upstream LLM API keys

---

## 15. Conclusion

The if-emotion-ux project provides a **production-ready reference implementation** for React frontend SSE streaming integration with OpenWebUI-compatible backends.

**Key Takeaways:**
1. Use `Response.body.getReader()` for streaming (not EventSource)
2. TextDecoder handles UTF-8 decoding from binary streams
3. Accumulate content in state variable, update UI per-token
4. Handle parsing errors gracefully - partial content survives failures
5. Optimistic UI + persistence pattern ensures good UX
6. Component composition with callbacks keeps code modular

**For YoloGuard Integration:**
- Interceptor pattern works at OpenWebUIClient level
- Stream parsing allows token-level analysis
- Message persistence allows audit trails
- State extensions support metadata (guard status, trust score)

---

## References

- **OpenWebUI Docs**: https://docs.openwebui.com/
- **Fetch Streaming API**: https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream
- **Server-Sent Events**: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
- **React Hooks**: https://react.dev/reference/react/hooks
- **Source Project**: `/home/setup/if-emotion-ux/`
