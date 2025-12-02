# OpenWebUI API Quick Reference for if.emotion Frontend

**Quick Integration Checklist for Frontend Developers**

---

## 1. Authentication Setup (Do This First)

```javascript
// Get API key from: OpenWebUI Settings > Account > Create API Key
const API_KEY = "your-api-key-here";
const BASE_URL = "http://localhost:8080";

// Add to every request:
const headers = {
  Authorization: `Bearer ${API_KEY}`,
  "Content-Type": "application/json",
};
```

---

## 2. List Available Models

```javascript
async function getModels() {
  const res = await fetch(`${BASE_URL}/api/models`, { headers });
  const data = await res.json();
  return data.data; // Array of model objects
}
```

---

## 3. Simple Chat (Non-Streaming)

```javascript
async function chat(model, userMessage) {
  const res = await fetch(`${BASE_URL}/api/chat/completions`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      model,
      messages: [{ role: "user", content: userMessage }],
      stream: false,
    }),
  });
  const data = await res.json();
  return data.choices[0].message.content;
}

// Usage:
const response = await chat("claude-3-opus-20250219", "Hello!");
console.log(response);
```

---

## 4. Streaming Chat (Real-Time Tokens)

```javascript
async function* streamChat(model, userMessage, chatId) {
  const res = await fetch(`${BASE_URL}/api/chat/completions`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      model,
      messages: [{ role: "user", content: userMessage }],
      stream: true,
      chat_id: chatId,
    }),
  });

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split("\n");

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[DONE]") return;

          try {
            const json = JSON.parse(data);
            const token = json.choices[0]?.delta?.content;
            if (token) yield token;
          } catch (e) {}
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

// Usage (with async generator):
let fullText = "";
for await (const token of streamChat("claude-3-opus-20250219", "Explain AI", uuidv4())) {
  fullText += token;
  console.log(token); // Display in real-time
}
```

---

## 5. Create Persistent Chat Session

```javascript
async function createChat(title, model) {
  const res = await fetch(`${BASE_URL}/api/chats/new`, {
    method: "POST",
    headers,
    body: JSON.stringify({ title, model }),
  });
  const data = await res.json();
  return data.id; // Chat UUID
}

// Usage:
const chatId = await createChat("AI Discussion", "claude-3-opus-20250219");
console.log("Chat created:", chatId);
```

---

## 6. Get Chat History

```javascript
async function getChatHistory(chatId) {
  const res = await fetch(`${BASE_URL}/api/chats/${chatId}`, { headers });
  const data = await res.json();
  return data.messages; // Array of all messages
}
```

---

## 7. Full Streaming Workflow with Session Persistence

```javascript
async function fullWorkflow() {
  // 1. Create chat
  const chatId = await createChat("My Session", "claude-3-opus-20250219");

  // 2. Stream response
  let fullContent = "";
  for await (const token of streamChat(
    "claude-3-opus-20250219",
    "What is AI?",
    chatId
  )) {
    fullContent += token;
    updateUI(token); // Update your React component
  }

  // 3. Signal completion to backend
  await fetch(`${BASE_URL}/api/chat/completed`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      id: generateUUID(),
      chat_id: chatId,
      message: {
        id: generateUUID(),
        role: "assistant",
        content: fullContent,
      },
      model: "claude-3-opus-20250219",
    }),
  });

  console.log("Chat completed and saved");
}
```

---

## 8. Upload File & Use in Chat (RAG)

```javascript
// Upload file
async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/api/v1/files`, {
    method: "POST",
    headers: { Authorization: `Bearer ${API_KEY}` }, // No Content-Type for FormData
    body: formData,
  });

  const data = await res.json();
  return data.id; // File UUID
}

// Use file in chat
async function chatWithFile(model, fileId, query) {
  const res = await fetch(`${BASE_URL}/api/chat/completions`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      model,
      messages: [{ role: "user", content: query }],
      files: [{ type: "file", id: fileId }],
      stream: false,
    }),
  });

  const data = await res.json();
  return data.choices[0].message.content;
}

// Usage:
const fileId = await uploadFile(document);
const answer = await chatWithFile("claude-3-opus-20250219", fileId, "Summarize this");
```

---

## 9. Error Handling

```javascript
async function chatSafe(model, message) {
  try {
    const res = await fetch(`${BASE_URL}/api/chat/completions`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        model,
        messages: [{ role: "user", content: message }],
      }),
    });

    if (!res.ok) {
      if (res.status === 401) throw new Error("Invalid API key");
      if (res.status === 404) throw new Error("Model not found");
      if (res.status === 429) throw new Error("Rate limited - try again later");
      throw new Error(`API error: ${res.status}`);
    }

    const data = await res.json();
    return data.choices[0].message.content;
  } catch (error) {
    console.error("Chat failed:", error);
    throw error;
  }
}
```

---

## 10. Important HTTP Status Codes

| Code | Meaning | Fix |
|------|---------|-----|
| 200 | Success | ✓ Proceed |
| 400 | Bad request | Check JSON syntax, required fields |
| 401 | Unauthorized | Verify API key is correct |
| 404 | Not found | Chat/model ID doesn't exist |
| 429 | Rate limited | Wait before retrying |
| 500 | Server error | OpenWebUI is down, try again |

---

## 11. Streaming vs Non-Streaming

| Feature | Non-Streaming | Streaming |
|---------|---------------|-----------|
| Response Time | All at once (slow) | Real-time tokens |
| Code Complexity | Simple | More complex (SSE parsing) |
| UX | Show loading bar | Show text appearing |
| Best For | Simple queries | Long responses, chat UI |

---

## 12. Common Mistakes to Avoid

❌ **Don't:**
```javascript
// Missing chat_id - history lost
streamChat(model, message); // ← NO chat_id!

// Using old/invalid token
headers = { Authorization: `Bearer expired-token` };

// Not handling 401 (expired token)
try { /* API call */ } catch (e) {} // Won't catch 401

// Incomplete message in chat/completed
// Missing .message.content field
```

✓ **Do:**
```javascript
// Include chat_id for persistence
streamChat(model, message, uuidv4()); // ← With chat_id

// Check token validity before use
if (isTokenExpired(apiKey)) refreshToken();

// Handle 401 explicitly
if (res.status === 401) {
  refreshToken();
  retry();
}

// Complete all required fields
await fetch("/api/chat/completed", {
  body: JSON.stringify({
    id: uuid,
    chat_id: uuid,
    message: {
      id: uuid,
      role: "assistant",
      content: "Full message text", // ← Required
    },
    model: "...",
  }),
});
```

---

## 13. React Integration Example

```jsx
import { useState, useRef } from "react";

export function ChatUI() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [chatId, setChatId] = useState(null);

  const handleSend = async (userMessage) => {
    setLoading(true);

    // Create chat on first message
    if (!chatId) {
      const id = await createChat("Chat", "claude-3-opus-20250219");
      setChatId(id);
    }

    let fullResponse = "";

    try {
      // Stream response
      for await (const token of streamChat(
        "claude-3-opus-20250219",
        userMessage,
        chatId
      )) {
        fullResponse += token;
        // Update UI with streaming token
        setMessages((prev) => {
          const copy = [...prev];
          if (copy[copy.length - 1]?.role === "assistant") {
            copy[copy.length - 1].content = fullResponse;
          } else {
            copy.push({ role: "assistant", content: fullResponse });
          }
          return copy;
        });
      }

      // Signal completion
      await fetch(`${BASE_URL}/api/chat/completed`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          id: generateUUID(),
          chat_id: chatId,
          message: { role: "assistant", content: fullResponse },
          model: "claude-3-opus-20250219",
        }),
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {messages.map((msg, i) => (
        <div key={i} className={msg.role}>
          {msg.content}
        </div>
      ))}
      <input
        disabled={loading}
        onSubmit={(e) => {
          e.preventDefault();
          handleSend(e.target.value);
          e.target.value = "";
        }}
      />
    </div>
  );
}
```

---

## 14. Testing Your Integration

```bash
# 1. Test authentication
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:8080/api/models

# 2. Test simple chat
curl -X POST http://localhost:8080/api/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-opus-20250219",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": false
  }'

# 3. Test streaming
curl -X POST http://localhost:8080/api/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-opus-20250219",
    "messages": [{"role": "user", "content": "Write a poem"}],
    "stream": true
  }' | grep -o "data:.*" | head -10
```

---

## 15. Troubleshooting

| Problem | Solution |
|---------|----------|
| 401 Unauthorized | Regenerate API key in Settings |
| 404 Model not found | Run `getModels()` to see available models |
| Streaming times out | Check reverse proxy buffering settings |
| No response | Check OpenWebUI is running on port 8080 |
| Incomplete tokens | Use SSE line-by-line parsing |

---

**For Complete Documentation:** See `/home/setup/infrafabric/integration/openwebui_api_spec.md`

**Need Help?** Check the "Common Challenges" section in the full spec.
