# OpenWebUI API Specification for if.emotion Frontend Integration

**Version:** 1.0
**Last Updated:** 2025-11-30
**Purpose:** Enable if.emotion React frontend to replace direct Claude Max calls with OpenWebUI REST API calls

**Citation Source:** if://citation/openwebui-api-20251130
**Based on:** Official OpenWebUI Documentation + GitHub API Reference Discussion #16402

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Core API Endpoints](#core-api-endpoints)
4. [Request/Response Schemas](#requestresponse-schemas)
5. [Chat Streaming (Server-Sent Events)](#chat-streaming-server-sent-events)
6. [Chat Management Endpoints](#chat-management-endpoints)
7. [File & Knowledge Base (RAG)](#file--knowledge-base-rag)
8. [HTTP Status Codes](#http-status-codes)
9. [Implementation Examples](#implementation-examples)
10. [Best Practices](#best-practices)
11. [Common Challenges](#common-challenges)

---

## Overview

OpenWebUI provides a comprehensive REST API for building custom frontends and integrations. The API supports:

- Chat completions with streaming responses (Server-Sent Events)
- Model listing and management
- Chat session persistence
- File uploads and RAG (Retrieval Augmented Generation)
- Multiple authentication methods (Bearer Token, JWT)
- OpenAI-compatible endpoints

**Base URL:** `http://localhost:8080` (or your OpenWebUI instance)

**Key Endpoint Groups:**
- **`/api`** - Main chat management and models
- **`/api/v1`** - File & RAG operations
- **`/v1`** - OpenAI-compatible endpoints
- **`/ollama`** - Native Ollama API passthrough

---

## Authentication

### Overview

All protected endpoints require Bearer Token authentication. You have two options:

1. **API Key** - Generated in Settings > Account
2. **JWT Token** - Obtained via `/api/auth/signin` endpoint

### API Key Method (Recommended for Frontend)

#### Generating an API Key

1. In OpenWebUI web interface, go to **Settings > Account**
2. Click **"Create API Key"**
3. Copy the generated token

#### Using API Key

Include the API key in the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

### JWT Token Method (Session-based)

#### Obtain JWT Token

```bash
curl -X POST http://localhost:8080/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'
```

#### Response Format

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "id": "user-id-uuid",
  "email": "user@example.com",
  "name": "User Name",
  "role": "user",
  "profile_image_url": "https://..."
}
```

#### Using JWT Token

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Environment Variables (Optional)

Set JWT expiration in your OpenWebUI deployment:

```
JWT_EXPIRATION_TIME=3600  # 1 hour
WEBUI_SECRET_KEY=your-secret-key
```

---

## Core API Endpoints

### 1. List Available Models

**Endpoint:** `GET /api/models`

**Authentication:** Required (Bearer Token)

**Description:** Retrieve all models available in this OpenWebUI instance (Ollama, OpenAI, custom models, etc.)

**Request:**

```bash
curl -X GET http://localhost:8080/api/models \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**

```json
{
  "data": [
    {
      "id": "llama2",
      "name": "Llama 2",
      "object": "model",
      "created": 1699564800,
      "owned_by": "meta",
      "permission": [],
      "root": "llama2"
    },
    {
      "id": "mistral",
      "name": "Mistral",
      "object": "model",
      "created": 1699564800,
      "owned_by": "mistral",
      "permission": [],
      "root": "mistral"
    },
    {
      "id": "claude-3-opus-20250219",
      "name": "Claude 3 Opus",
      "object": "model",
      "created": 1699564800,
      "owned_by": "anthropic",
      "permission": [],
      "root": "claude-3-opus-20250219"
    }
  ]
}
```

---

### 2. Chat Completions (Primary Endpoint)

**Endpoint:** `POST /api/chat/completions`

**Authentication:** Required (Bearer Token)

**Description:** Send a message and receive a response. Supports streaming responses via Server-Sent Events.

**Request Headers:**

```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Request Body Schema:**

```json
{
  "model": "string (required)",
  "messages": [
    {
      "role": "string (system|user|assistant, required)",
      "content": "string (required)"
    }
  ],
  "stream": "boolean (optional, default: false)",
  "chat_id": "string (optional, UUID)",
  "temperature": "number (optional, 0.0-2.0, default: 0.7)",
  "top_p": "number (optional, 0.0-1.0, default: 1.0)",
  "max_tokens": "integer (optional)",
  "system": "string (optional, system prompt override)",
  "files": [
    {
      "type": "string (file|collection)",
      "id": "string (file or collection UUID)"
    }
  ],
  "background_tasks": "boolean (optional, enable async title generation)"
}
```

**Request Example (Non-Streaming):**

```bash
curl -X POST http://localhost:8080/api/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-opus-20250219",
    "messages": [
      {
        "role": "user",
        "content": "Explain quantum computing in simple terms"
      }
    ],
    "stream": false
  }'
```

**Response (Non-Streaming, 200 OK):**

```json
{
  "id": "chatcmpl-uuid",
  "object": "text_completion",
  "created": 1699564800,
  "model": "claude-3-opus-20250219",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Quantum computing uses quantum bits (qubits) instead of classical bits. Unlike classical bits (0 or 1), qubits can exist in a superposition of both states simultaneously..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 87,
    "total_tokens": 102
  }
}
```

**Request Example (Streaming):**

```bash
curl -X POST http://localhost:8080/api/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-opus-20250219",
    "messages": [
      {
        "role": "user",
        "content": "Write a haiku about AI"
      }
    ],
    "stream": true,
    "chat_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Response (Streaming, Server-Sent Events):**

```
data: {"choices":[{"index":0,"delta":{"role":"assistant","content":"Silicon"}}]}

data: {"choices":[{"index":0,"delta":{"role":"assistant","content":" minds"}},{"index":1,"delta":{"role":"assistant","content":" think"}},{"index":2,"delta":{"role":"assistant","content":"\n"}}]}

data: {"choices":[{"index":0,"delta":{"role":"assistant","content":"Like"}}]}

data: {"choices":[{"index":0,"delta":{"role":"assistant","content":" shadows"}},{"index":1,"delta":{"role":"assistant","content":" dancing"}},{"index":2,"delta":{"role":"assistant","content":"\n"}}]}

data: {"choices":[{"index":0,"delta":{"role":"assistant","content":"In"}}]}

data: {"choices":[{"index":0,"delta":{"role":"assistant","content":" electric"}},{"index":1,"delta":{"role":"assistant","content":" light"}}]}

data: [DONE]
```

---

### 3. Signal Completion

**Endpoint:** `POST /api/chat/completed`

**Authentication:** Required (Bearer Token)

**Description:** Signals the server that the assistant reply is complete. This triggers backend processing pipelines for title generation, tagging, and other post-processing tasks.

**Request Body:**

```json
{
  "id": "string (UUID, required)",
  "chat_id": "string (UUID, required)",
  "message": {
    "id": "string (UUID)",
    "role": "assistant",
    "content": "string (the full assistant response)"
  },
  "model": "string (required)"
}
```

**Request Example:**

```bash
curl -X POST http://localhost:8080/api/chat/completed \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "msg-uuid-12345",
    "chat_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": {
      "id": "msg-uuid-12345",
      "role": "assistant",
      "content": "Silicon minds think\nLike shadows dancing\nIn electric light"
    },
    "model": "claude-3-opus-20250219"
  }'
```

**Response (200 OK):**

```json
{
  "status": "ok"
}
```

---

## Request/Response Schemas

### Message Schema

```json
{
  "role": "system|user|assistant (string, required)",
  "content": "string (required)"
}
```

**Role Types:**
- `system` - System instructions/context
- `user` - User message
- `assistant` - Assistant response

### Chat Object

```json
{
  "id": "string (UUID)",
  "title": "string",
  "model": "string",
  "system": "string (system prompt)",
  "messages": [
    {
      "id": "string (UUID)",
      "role": "system|user|assistant",
      "content": "string",
      "timestamp": "number (unix timestamp)"
    }
  ],
  "created_at": "number (unix timestamp)",
  "updated_at": "number (unix timestamp)",
  "metadata": {
    "tags": ["string"],
    "folders": ["string"]
  }
}
```

### File Object

```json
{
  "id": "string (UUID)",
  "filename": "string",
  "size": "integer (bytes)",
  "mimetype": "string",
  "uploaded_at": "number (unix timestamp)",
  "status": "pending|processing|processed|error"
}
```

### Knowledge Base Object

```json
{
  "id": "string (UUID)",
  "name": "string",
  "description": "string",
  "document_count": "integer",
  "status": "pending|processing|processed",
  "created_at": "number (unix timestamp)",
  "updated_at": "number (unix timestamp)"
}
```

---

## Chat Streaming (Server-Sent Events)

### Overview

When `stream: true` is specified in a chat completion request, the server returns Server-Sent Events (SSE) with token deltas. The client must reassemble these deltas into the complete message.

### SSE Event Format

```
data: {json_object}

data: [DONE]
```

### SSE Response Structure

```json
{
  "choices": [
    {
      "index": 0,
      "delta": {
        "role": "assistant",
        "content": "token_chunk_or_null"
      },
      "finish_reason": null | "stop" | "length" | "function_call"
    }
  ]
}
```

### Streaming Implementation Example (JavaScript/TypeScript)

```typescript
async function streamChatCompletion(
  model: string,
  messages: Array<{ role: string; content: string }>,
  apiKey: string
) {
  const response = await fetch("http://localhost:8080/api/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      messages,
      stream: true,
      chat_id: generateUUID(),
    }),
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  const reader = response.body?.getReader();
  let fullContent = "";

  if (!reader) throw new Error("No response body");

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = new TextDecoder().decode(value);
      const lines = chunk.split("\n");

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const jsonStr = line.slice(6);

          if (jsonStr === "[DONE]") {
            console.log("Stream complete");
            break;
          }

          try {
            const json = JSON.parse(jsonStr);
            const delta = json.choices[0]?.delta?.content;

            if (delta) {
              fullContent += delta;
              console.log("Received token:", delta);
              // Update UI here in real-time
            }
          } catch (e) {
            console.error("Failed to parse SSE event:", jsonStr);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }

  return fullContent;
}
```

### Reverse Proxy Configuration for SSE

If deploying behind a reverse proxy (Nginx, Apache), disable buffering:

**Nginx:**
```nginx
location /api/chat/completions {
    proxy_pass http://localhost:8080;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_buffering off;
    proxy_cache off;
    proxy_set_header Transfer-Encoding chunked;
}
```

---

## Chat Management Endpoints

### Create New Chat

**Endpoint:** `POST /api/chats/new`

**Authentication:** Required

**Request:**

```bash
curl -X POST http://localhost:8080/api/chats/new \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Chat Session",
    "model": "claude-3-opus-20250219"
  }'
```

**Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "My Chat Session",
  "model": "claude-3-opus-20250219",
  "created_at": 1699564800
}
```

### List User Chats

**Endpoint:** `GET /api/chats`

**Authentication:** Required

**Request:**

```bash
curl -X GET http://localhost:8080/api/chats \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**

```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Understanding AI",
      "model": "claude-3-opus-20250219",
      "updated_at": 1699564900
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Code Review",
      "model": "mistral",
      "updated_at": 1699564850
    }
  ]
}
```

### Get Chat History

**Endpoint:** `GET /api/chats/{chat_id}`

**Authentication:** Required

**Request:**

```bash
curl -X GET http://localhost:8080/api/chats/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Understanding AI",
  "model": "claude-3-opus-20250219",
  "messages": [
    {
      "id": "msg-1",
      "role": "user",
      "content": "What is machine learning?",
      "timestamp": 1699564800
    },
    {
      "id": "msg-2",
      "role": "assistant",
      "content": "Machine learning is a subset of AI...",
      "timestamp": 1699564810
    }
  ]
}
```

### Update Chat

**Endpoint:** `POST /api/chats/{chat_id}`

**Authentication:** Required

**Request:**

```bash
curl -X POST http://localhost:8080/api/chats/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI & Machine Learning",
    "messages": [...]
  }'
```

### Delete Chat

**Endpoint:** `DELETE /api/chats/{chat_id}`

**Authentication:** Required

**Request:**

```bash
curl -X DELETE http://localhost:8080/api/chats/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response (204 No Content):**

---

## File & Knowledge Base (RAG)

### Upload File

**Endpoint:** `POST /api/v1/files`

**Authentication:** Required

**Description:** Upload a file (PDF, DOCX, TXT, MD, etc.) for RAG processing. Content is automatically extracted and embedded into vector database.

**Request:**

```bash
curl -X POST http://localhost:8080/api/v1/files \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@path/to/document.pdf"
```

**Response:**

```json
{
  "id": "file-uuid",
  "filename": "document.pdf",
  "size": 245632,
  "mimetype": "application/pdf",
  "status": "pending",
  "uploaded_at": 1699564800
}
```

### List Files

**Endpoint:** `GET /api/v1/files`

**Authentication:** Required

**Request:**

```bash
curl -X GET http://localhost:8080/api/v1/files \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Delete File

**Endpoint:** `DELETE /api/v1/files/{file_id}`

**Authentication:** Required

**Request:**

```bash
curl -X DELETE http://localhost:8080/api/v1/files/file-uuid \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Create Knowledge Base

**Endpoint:** `POST /api/v1/knowledge/create`

**Authentication:** Required

**Request:**

```bash
curl -X POST http://localhost:8080/api/v1/knowledge/create \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Company Documentation",
    "description": "Internal knowledge base"
  }'
```

**Response:**

```json
{
  "id": "kb-uuid",
  "name": "Company Documentation",
  "description": "Internal knowledge base",
  "document_count": 0,
  "status": "created",
  "created_at": 1699564800
}
```

### Add Files to Knowledge Base

**Endpoint:** `POST /api/v1/knowledge/{knowledge_id}/file/add`

**Authentication:** Required

**Request:**

```bash
curl -X POST http://localhost:8080/api/v1/knowledge/kb-uuid/file/add \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "file-uuid"
  }'
```

### Use Files in Chat

To reference files in a chat completion, include them in the `files` parameter:

```bash
curl -X POST http://localhost:8080/api/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-opus-20250219",
    "messages": [
      {
        "role": "user",
        "content": "Summarize the attached document"
      }
    ],
    "files": [
      {
        "type": "file",
        "id": "file-uuid"
      }
    ]
  }'
```

---

## HTTP Status Codes

| Code | Meaning | Example Scenario |
|------|---------|------------------|
| 200 | OK | Successful chat completion |
| 201 | Created | File upload successful |
| 204 | No Content | Chat deleted successfully |
| 400 | Bad Request | Malformed JSON, missing required fields |
| 401 | Unauthorized | Invalid or missing API key |
| 403 | Forbidden | User lacks permission for resource |
| 404 | Not Found | Chat ID or file ID doesn't exist |
| 422 | Unprocessable Entity | Request validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Backend processing error |
| 503 | Service Unavailable | OpenWebUI is temporarily down |

---

## Implementation Examples

### Example 1: Simple Chat without Streaming

```typescript
async function simpleChat(
  apiKey: string,
  userMessage: string
): Promise<string> {
  const response = await fetch("http://localhost:8080/api/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "claude-3-opus-20250219",
      messages: [
        {
          role: "user",
          content: userMessage,
        },
      ],
      stream: false,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  const data = await response.json();
  return data.choices[0].message.content;
}

// Usage
const answer = await simpleChat(
  "your-api-key",
  "What is 2 + 2?"
);
console.log(answer);
```

### Example 2: Streaming Chat with Session Persistence

```typescript
async function streamingChatWithSession(
  apiKey: string,
  model: string,
  userMessage: string,
  chatId?: string
): Promise<void> {
  // Create new chat if needed
  if (!chatId) {
    const createResponse = await fetch("http://localhost:8080/api/chats/new", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title: "New Conversation",
        model,
      }),
    });
    const chat = await createResponse.json();
    chatId = chat.id;
  }

  // Stream the response
  const response = await fetch("http://localhost:8080/api/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      messages: [
        {
          role: "user",
          content: userMessage,
        },
      ],
      stream: true,
      chat_id: chatId,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  let fullContent = "";
  const reader = response.body?.getReader();

  if (!reader) throw new Error("No reader available");

  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split("\n");

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const dataStr = line.slice(6);

          if (dataStr === "[DONE]") {
            // Signal completion to server
            await fetch("http://localhost:8080/api/chat/completed", {
              method: "POST",
              headers: {
                Authorization: `Bearer ${apiKey}`,
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                id: generateUUID(),
                chat_id: chatId,
                message: {
                  id: generateUUID(),
                  role: "assistant",
                  content: fullContent,
                },
                model,
              }),
            });
            break;
          }

          try {
            const json = JSON.parse(dataStr);
            const delta = json.choices[0]?.delta?.content;
            if (delta) {
              fullContent += delta;
              process.stdout.write(delta); // Print in real-time
            }
          } catch (e) {
            // Ignore parsing errors
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }

  console.log("\n");
}
```

### Example 3: Chat with RAG (File References)

```typescript
async function chatWithFile(
  apiKey: string,
  fileId: string,
  userQuery: string
): Promise<string> {
  const response = await fetch("http://localhost:8080/api/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "claude-3-opus-20250219",
      messages: [
        {
          role: "user",
          content: userQuery,
        },
      ],
      files: [
        {
          type: "file",
          id: fileId,
        },
      ],
      stream: false,
    }),
  });

  const data = await response.json();
  return data.choices[0].message.content;
}
```

---

## Best Practices

### 1. Always Use Chat IDs for Persistent Sessions

When creating a chat, always associate messages with the same `chat_id` to maintain conversation history:

```json
{
  "model": "claude-3-opus-20250219",
  "messages": [...],
  "chat_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. Signal Completion with `/api/chat/completed`

After streaming completes, always call `/api/chat/completed` to trigger backend processing (title generation, tagging):

```bash
POST /api/chat/completed
{
  "id": "message-uuid",
  "chat_id": "chat-uuid",
  "message": { ... },
  "model": "..."
}
```

### 3. Handle Streaming Timeouts

When using streaming through a proxy, configure it to disable buffering. Long-running tool calls may cause proxy timeouts.

### 4. Verify File Status Before Using in RAG

Files go through `pending` → `processing` → `processed` states. Only use files in RAG after status is `processed`:

```typescript
// Poll until processed
while (true) {
  const file = await getFileStatus(fileId, apiKey);
  if (file.status === "processed") break;
  await sleep(1000);
}
```

### 5. Include System Prompt Explicitly

For consistent behavior, pass the system prompt in the request rather than relying on defaults:

```json
{
  "messages": [...],
  "system": "You are a helpful assistant. Be concise and clear."
}
```

### 6. Implement Exponential Backoff

For rate-limited or slow responses, use exponential backoff:

```typescript
async function apiCallWithRetry(
  fn: () => Promise<any>,
  maxRetries = 5
): Promise<any> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(Math.pow(2, i) * 1000);
    }
  }
}
```

---

## Common Challenges

### Challenge 1: Streaming Timeout Behind Reverse Proxy

**Problem:** SSE stream times out after 60 seconds when behind Nginx/Apache

**Solution:** Disable proxy buffering:

**Nginx:**
```nginx
proxy_buffering off;
proxy_cache off;
proxy_http_version 1.1;
```

**Apache:**
```apache
ProxyPass /api/chat/completions http://localhost:8080/api/chat/completions disablereuse=On
```

---

### Challenge 2: Incomplete SSE Chunks

**Problem:** SSE data arrives in incomplete chunks, parsing fails

**Solution:** Buffer chunks until newline delimiter:

```typescript
let buffer = "";
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  buffer += decoder.decode(value, { stream: true });
  const lines = buffer.split("\n");

  // Keep last incomplete line in buffer
  buffer = lines.pop() || "";

  for (const line of lines) {
    // Process complete lines
  }
}
```

---

### Challenge 3: Missing Chat History

**Problem:** Streaming responses don't include full conversation context

**Solution:** Always fetch complete chat history and include all messages in request:

```typescript
const chat = await fetch(`/api/chats/${chatId}`, {
  headers: { Authorization: `Bearer ${apiKey}` },
}).then(r => r.json());

// Send complete history, not just last message
const response = await fetch("/api/chat/completions", {
  method: "POST",
  headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "claude-3-opus-20250219",
    messages: chat.messages, // All messages, not just user's last
    stream: true,
    chat_id: chatId,
  }),
});
```

---

### Challenge 4: File Not Ready for RAG

**Problem:** "File not found" error when referencing recently uploaded file

**Solution:** Poll file status until `processed`:

```typescript
async function waitForFileProcessing(
  fileId: string,
  apiKey: string,
  timeoutMs = 30000
) {
  const startTime = Date.now();

  while (Date.now() - startTime < timeoutMs) {
    const file = await fetch(`/api/v1/files/${fileId}`, {
      headers: { Authorization: `Bearer ${apiKey}` },
    }).then(r => r.json());

    if (file.status === "processed") return file;
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  throw new Error("File processing timeout");
}
```

---

### Challenge 5: Authentication Expired

**Problem:** 401 Unauthorized after extended usage

**Solution:** Implement token refresh for JWT:

```typescript
async function chatWithAutoRefresh(
  apiKey: string,
  email: string,
  password: string,
  messages: any[]
) {
  let token = apiKey;

  try {
    const response = await fetch("/api/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-3-opus-20250219",
        messages,
      }),
    });

    if (response.status === 401) {
      // Token expired, refresh it
      const authResponse = await fetch("/api/auth/signin", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const auth = await authResponse.json();
      token = auth.token;

      // Retry with new token
      return fetch("/api/chat/completions", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "claude-3-opus-20250219",
          messages,
        }),
      });
    }

    return response;
  } catch (error) {
    throw error;
  }
}
```

---

## API Documentation Access

For interactive Swagger/OpenAPI documentation, set the environment variable when starting OpenWebUI:

```bash
ENV=dev docker-compose up
```

Then access: `http://localhost:8080/docs`

---

## Summary

| Feature | Endpoint | Auth | Notes |
|---------|----------|------|-------|
| List Models | `GET /api/models` | Bearer | Returns all available models |
| Chat Completions | `POST /api/chat/completions` | Bearer | Supports streaming via `stream: true` |
| Signal Complete | `POST /api/chat/completed` | Bearer | Triggers post-processing |
| Create Chat | `POST /api/chats/new` | Bearer | Returns new chat UUID |
| Get History | `GET /api/chats/{id}` | Bearer | Full conversation history |
| Upload File | `POST /api/v1/files` | Bearer | Returns file UUID, status=pending initially |
| Create KB | `POST /api/v1/knowledge/create` | Bearer | Create knowledge base for RAG |
| Add Files to KB | `POST /api/v1/knowledge/{id}/file/add` | Bearer | Link files to knowledge base |

---

**Document Version:** 1.0
**Generated:** 2025-11-30
**For:** if.emotion Frontend Integration
**Status:** Complete

IF.citation: `if://citation/openwebui-api-20251130-spec-v1.0`
