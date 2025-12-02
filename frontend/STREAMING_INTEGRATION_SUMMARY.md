# Quick Reference: OpenWebUI Streaming Integration

**Status:** Research Complete - Ready for Implementation
**Date:** 2025-11-30
**Source Project:** `/home/setup/if-emotion-ux`

---

## Architecture at a Glance

```
User Input
   ↓
handleSend() in App.tsx
   ├─ Add user message (optimistic)
   ├─ POST to /api/chats/{id}/messages (persist user msg)
   ├─ Call client.sendMessage() → returns ReadableStreamDefaultReader
   │
   └─ Streaming Loop:
      ├─ const { done, value } = await reader.read()
      ├─ decoder.decode(value) → UTF-8 string
      ├─ Split by '\n', parse 'data: {...}' lines
      ├─ Extract data.choices[0].delta.content
      ├─ Accumulate in fullContent variable
      ├─ setMessages(prev => { ...update botMsgId.content = fullContent })
      └─ Repeat until done=true or '[DONE]' received

   └─ POST completed message to /api/chats/{id}/messages
      └─ loadSessions() to update sidebar
```

---

## Key Files & Code Locations

### Frontend (React)

**Main Streaming Logic:**
- `/home/setup/if-emotion-ux/App.tsx` (lines 134-218)
  - `handleSend()` function implements full streaming flow
  - Uses `useState` for messages, `useRef` for client

**Service Layer:**
- `/home/setup/if-emotion-ux/services/openwebui.ts` (lines 96-148)
  - `sendMessage()` method
  - Returns `ReadableStreamDefaultReader<Uint8Array>`

**Components:**
- `components/ChatMessage.tsx` - Message bubble with streaming content
- `components/ChatInput.tsx` - Input control with isLoading state
- `components/Sidebar.tsx` - Session management

**Types:**
- `types.ts` - Message, Session, Role interfaces

### Backend (Python/Flask)

**Streaming Endpoint:**
- `/home/setup/if-emotion-ux/backend/openwebui_server.py` (lines 222-299)
  - `@app.route('/api/chat/completions')`
  - Uses `Response()` with generator for SSE
  - Passes through upstream LLM API streaming

**Message Persistence:**
- Lines 148-183 - Chat and message REST endpoints

---

## Core Streaming Algorithm

```typescript
// 1. Get streaming reader from fetch
const streamReader = await client.sendMessage(...);

// 2. Prepare decoder and accumulator
const decoder = new TextDecoder();
let fullContent = '';

// 3. Read binary stream until complete
while (true) {
  const { done, value } = await streamReader.read();
  if (done) break;

  // 4. Decode bytes to UTF-8 string
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');

  // 5. Parse SSE format (data: {...}\n)
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const dataStr = line.slice(6);
      if (dataStr === '[DONE]') continue;

      try {
        // 6. Extract token from OpenAI-compatible format
        const data = JSON.parse(dataStr);
        const content = data.choices?.[0]?.delta?.content || '';

        if (content) {
          // 7. Accumulate and render
          fullContent += content;
          setMessages(prev =>
            prev.map(m =>
              m.id === botMsgId
                ? { ...m, content: fullContent }
                : m
            )
          );
        }
      } catch (e) {
        // Partial chunks may fail to parse - that's OK
      }
    }
  }
}
```

---

## State Management

**No Redux/Context** - Simple component state:

```typescript
const [messages, setMessages] = useState<Message[]>([]);
const [sessions, setSessions] = useState<Session[]>([]);
const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
const [isLoading, setIsLoading] = useState(false);
const [selectedModel, setSelectedModel] = useState<string>('');
const [availableModels, setAvailableModels] = useState<string[]>([]);
const [isOffTheRecord, setIsOffTheRecord] = useState(false);

const clientRef = useRef(new OpenWebUIClient(settings));
const messagesEndRef = useRef<HTMLDivElement>(null);
```

**Scaling Option:** If needed, extract to custom hook:
```typescript
function useStreamingChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const streamMessage = useCallback(async (...) => { /* streaming loop */ }, []);
  return { messages, isLoading, streamMessage };
}
```

---

## API Endpoints

### OpenWebUI-Compatible REST

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/models` | GET | List available models |
| `/api/version` | GET | Health check |
| `/api/chats` | GET | List all sessions |
| `/api/chats/new` | POST | Create session |
| `/api/chats/{id}` | GET | Get session + messages |
| `/api/chats/{id}` | DELETE | Delete session |
| `/api/chats/{id}/messages` | POST | Add message (persist) |
| `/api/chats/{id}/messages/{id}` | DELETE | Delete message (silent) |

### OpenAI-Compatible Streaming

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/api/chat/completions` | POST | Stream LLM response | `text/event-stream` (SSE) |

**Request Format:**
```json
{
  "model": "anthropic/claude-3.5-sonnet",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "stream": true,
  "temperature": 0.7,
  "max_tokens": 2048
}
```

**Response Format (SSE):**
```
data: {"id":"...", "choices": [{"delta": {"content": "Hello"}, ...}]}

data: {"id":"...", "choices": [{"delta": {"content": " world"}, ...}]}

data: [DONE]
```

---

## Integration Points for YoloGuard

### 1. Pre-send Validation
```typescript
// In handleSend(), after setMessages for user message:
const guardAnalysis = await IF.guard.analyzeUserMessage(text);
if (guardAnalysis.blocked) {
  // Show user message but don't stream response
  return;
}
```

### 2. In-stream Monitoring
```typescript
// In streaming loop, after extracting content:
const guardEval = await IF.guard.evaluateToken(content);
if (guardEval.action === 'block') {
  // Stop stream, show warning
  break;
}
```

### 3. Extend Message Type
```typescript
export interface Message {
  id: string;
  role: Role;
  content: string;
  timestamp: Date;
  // IF.guard additions:
  guardAnalysis?: GuardAnalysis;  // Pre-send evaluation
  guardDecision?: GuardDecision;   // Stream decision
  trustScore?: number;              // Confidence metric
  originalContent?: string;          // If modified
}
```

### 4. Guard Status Component
```typescript
const [guardStatus, setGuardStatus] = useState<'analyzing' | 'clear' | 'warning' | 'blocked'>('analyzing');

// In streaming loop:
const decision = await IF.guard.evaluateToken(content);
setGuardStatus(decision.status);
// Render status indicator in UI
```

---

## Error Handling Patterns

### Graceful Parsing Failures
```typescript
try {
  const data = JSON.parse(dataStr);
  // ...
} catch (e) {
  // Partial chunks may fail - continue with accumulated content
}
```

### Stream Connection Errors
```typescript
try {
  const streamReader = await client.sendMessage(...);
  // streaming loop
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

### Backend Stream Errors
```python
def stream_response(messages, model):
  try:
    response = requests.post(...)
    for line in response.iter_lines():
      # ...
  except Exception as e:
    error_data = {
      'id': 'error',
      'choices': [{'delta': {'content': f'Error: {str(e)}'}}]
    }
    yield f'data: {json.dumps(error_data)}\n\n'

  yield 'data: [DONE]\n\n'
```

---

## Reusable Patterns

### 1. Streaming Reader Consumption
```typescript
async function consumeStream(reader: ReadableStreamDefaultReader<Uint8Array>) {
  const decoder = new TextDecoder();
  const chunks: string[] = [];

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(decoder.decode(value));
  }

  return chunks.join('');
}
```

### 2. SSE Line Parser
```typescript
function parseSSELine(line: string) {
  if (!line.startsWith('data: ')) return null;

  const dataStr = line.slice(6);
  if (dataStr === '[DONE]') return { type: 'DONE' };

  try {
    return JSON.parse(dataStr);
  } catch (e) {
    return null;
  }
}
```

### 3. Token Accumulator
```typescript
function* parseTokenStream(lines: string[]) {
  for (const line of lines) {
    const data = parseSSELine(line);
    if (!data) continue;
    if (data.type === 'DONE') return;

    const content = data.choices?.[0]?.delta?.content;
    if (content) yield content;
  }
}
```

---

## Performance Considerations

### Current Approach
- ✅ Token-by-token UI updates (responsive)
- ✅ Memory efficient (no buffering)
- ❌ Potential re-render thrashing (every token = full re-render)

### Optimization Options

**Option 1: Debounce Updates**
```typescript
const updateMessage = useMemo(
  () => debounce((content: string) => {
    setMessages(prev => prev.map(m =>
      m.id === botMsgId ? { ...m, content } : m
    ));
  }, 50),  // Update every 50ms instead of per-token
  []
);

// In streaming loop:
if (content) {
  fullContent += content;
  updateMessage(fullContent);
}
```

**Option 2: Memoize Message Component**
```typescript
export const ChatMessage = React.memo(ChatMessageImpl, (prev, next) => {
  // Only re-render if content or role changed
  return prev.message.content === next.message.content &&
         prev.message.role === next.message.role;
});
```

**Option 3: Virtualize Long Lists**
```typescript
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={messages.length}
  itemSize={100}
>
  {({ index, style }) => (
    <div style={style}>
      <ChatMessage message={messages[index]} />
    </div>
  )}
</FixedSizeList>
```

---

## Testing Checklist

- [ ] Mock fetch to return SSE stream with delays
- [ ] Assert tokens appear incrementally in UI
- [ ] Verify error handling for malformed chunks
- [ ] Test connection loss mid-stream
- [ ] Verify message persistence after streaming
- [ ] Test model selection changes
- [ ] Verify privacy mode (ephemeral) works
- [ ] Test sidebar session grouping
- [ ] Verify export functionality
- [ ] Test multi-message conversations

---

## Deployment Checklist

- [ ] Backend: Flask server running with CORS enabled
- [ ] Frontend: React built to static assets
- [ ] HTTPS: Required for secure streaming
- [ ] Headers: Verify `text/event-stream` MIME type
- [ ] Keep-alive: Enable on reverse proxy
- [ ] Cache Control: `no-cache` headers on stream endpoints
- [ ] API Keys: Securely inject upstream LLM keys
- [ ] Error Logging: Monitor stream failures
- [ ] Rate Limiting: Implement per-user request limits
- [ ] Health Checks: `/api/version` endpoint working

---

## Next Steps for YoloGuard

1. **Clone if-emotion-ux** to `infrafabric/frontend/openwebui-streaming-reference`
2. **Create GuardedOpenWebUIClient** that wraps base client
3. **Implement token-level evaluation** hook into streaming loop
4. **Add guard status component** to ChatInput
5. **Extend Message interface** with guard metadata
6. **Create test suite** for streaming + guard interactions
7. **Document IF.ceo integration points** for architectural decisions

---

## File Structure Reference

```
if-emotion-ux/
├── App.tsx                          # Main component + streaming logic
├── types.ts                         # Type definitions
├── constants.ts                     # Config
├── utils.ts                         # Helper functions
├── services/
│   └── openwebui.ts                # OpenWebUIClient class
├── components/
│   ├── ChatMessage.tsx             # Message bubble (streaming-ready)
│   ├── ChatInput.tsx               # Input + send button
│   ├── Sidebar.tsx                 # Session list
│   ├── JourneyHeader.tsx           # Header bar
│   ├── SettingsModal.tsx           # Settings UI
│   ├── ExportModal.tsx             # Export dialog
│   ├── MessageActions.tsx          # Delete button
│   └── ...
├── backend/
│   └── openwebui_server.py         # Flask SSE streaming server
├── dist/                           # Build output
├── package.json                    # Dependencies
└── vite.config.ts                  # Vite config
```

---

## Critical Code Snippets

### Full handleSend() Flow (Simplified)
```typescript
const handleSend = async (text: string) => {
  // 1. Add user message
  setMessages(prev => [...prev, { id, role: USER, content: text, timestamp }]);
  setIsLoading(true);

  try {
    // 2. Persist user message if persistent mode
    if (!isOffTheRecord && currentSessionId) {
      await clientRef.current.addMessageToChat(currentSessionId, userMsg);
    }

    // 3. Get streaming response
    const streamReader = await clientRef.current.sendMessage(
      currentSessionId,
      text,
      messages,
      selectedModel,
      isOffTheRecord
    );

    // 4. Create bot message placeholder
    const botMsgId = generateId();
    setMessages(prev => [...prev, { id: botMsgId, role: ASSISTANT, content: '', timestamp }]);

    // 5. Stream and render
    const decoder = new TextDecoder();
    let fullContent = '';

    while (true) {
      const { done, value } = await streamReader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      for (const line of chunk.split('\n')) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          const content = data.choices?.[0]?.delta?.content || '';

          if (content) {
            fullContent += content;
            setMessages(prev => prev.map(m =>
              m.id === botMsgId ? { ...m, content: fullContent } : m
            ));
          }
        }
      }
    }

    // 6. Persist completed message
    if (!isOffTheRecord && currentSessionId) {
      await clientRef.current.addMessageToChat(currentSessionId,
        { ...botMsg, content: fullContent });
      loadSessions();  // Update timestamps
    }

  } catch (e) {
    // Show error message
    setMessages(prev => [...prev, { role: SYSTEM, content: 'Connection error', error: true }]);
  } finally {
    setIsLoading(false);
  }
};
```

---

## Success Metrics

Once integrated, verify:
- [ ] Messages stream in real-time (no buffering)
- [ ] UI responsive during streaming (no freezing)
- [ ] Errors don't lose partial content
- [ ] Sessions persist correctly
- [ ] Model switching works mid-conversation
- [ ] Privacy mode doesn't save transcripts
- [ ] Export includes full conversation history

---

**Research Complete - Implementation Ready** ✓
