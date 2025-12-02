# IF.emotion Complete Guide
**The Single Source of Truth for IF.emotion Architecture, Deployment, and Operations**

**Version:** 2.0
**Last Updated:** 2025-12-01
**Status:** Production + Design Phase (Claude Max CLI Integration Pending)
**Maintainers:** InfraFabric / IF.guard Council
**Contributors:** Dr Sergio V..

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Frontend Components](#frontend-components)
4. [Backend Architecture](#backend-architecture)
5. [Deployment Infrastructure](#deployment-infrastructure)
6. [Configuration Reference](#configuration-reference)
7. [Operations & Monitoring](#operations--monitoring)
8. [Known Issues & Gotchas](#known-issues--gotchas)
9. [Deployment Procedures](#deployment-procedures)
10. [Future Development](#future-development)

---

## Executive Summary

**IF.emotion** is a production-grade emotional intelligence conversational UI deployed on Proxmox Container 200 (85.239.243.227). It provides a chat interface with session persistence, multi-language support, export capabilities, and optional RAG augmentation through Sergio personality DNA.

### Key Characteristics
- **Frontend:** React 18 + TypeScript + Tailwind CSS (Sergio color scheme)
- **Active Backend:** Claude Max CLI with OpenWebUI compatibility (port 3001)
- **Inactive Backend:** OpenRouter proxy (port 5000, not used)
- **Data Storage:** ChromaDB collections (personality, rhetorical, humor, corpus)
- **Deployment:** Docker container with nginx reverse proxy
- **Hosting:** Proxmox virtualization at 85.239.243.227

### Project Repositories
- **Frontend Source:** https://github.com/dannystocker/if-emotion-ux.git (`/home/setup/if-emotion-ux`)
- **Backend:** `/root/sergio_chatbot/` (inside container 200)
- **Deployed Frontend:** `/opt/if-emotion/dist/`

---

## System Architecture

### 2.1 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Client Browser (User)                            │
│              https://85.239.243.227 (or localhost)                  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTPS/HTTP
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    Host nginx (port 80)                              │
│                   85.239.243.227:80                                  │
│  - SSL termination (if enabled)                                      │
│  - Static file serving                                               │
│  - Reverse proxy routing                                             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ localhost:5000 (TCP)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│        Proxmox Container 200 (LXC Linux Container)                  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              nginx (container port 80)                        │  │
│  │                                                               │  │
│  │  - Reverse proxy: /api/* → http://localhost:3001            │  │
│  │  - Static files: /* → /opt/if-emotion/dist/                 │  │
│  │  - SSE headers configured for streaming                      │  │
│  │  - Document root: /opt/if-emotion/dist                       │  │
│  └────────┬─────────────────────────────┬──────────────────────┘  │
│           │                             │                         │
│           │ HTTP (localhost:80)         │                         │
│           ▼                             ▼                         │
│  ┌──────────────────────────┐  ┌────────────────────────────┐    │
│  │ Frontend Files           │  │ Backend Services           │    │
│  │ /opt/if-emotion/dist/    │  │                            │    │
│  │ - index.html             │  │ Port 3001 (ACTIVE):        │    │
│  │ - *.js, *.css            │  │ claude_api_server_rag.py   │    │
│  │ - assets/                │  │ - Claude Max CLI wrapper   │    │
│  └──────────────────────────┘  │ - ChromaDB RAG queries     │    │
│                                 │ - SSE streaming            │    │
│                                 │                            │    │
│                                 │ Port 5000 (INACTIVE):      │    │
│                                 │ openwebui_server.py        │    │
│                                 │ - OpenRouter proxy         │    │
│                                 │ - Not currently used       │    │
│                                 └────────┬─────────────────┘    │
│                                          │                      │
│                                          ▼                      │
│                           ┌──────────────────────────┐           │
│                           │  ChromaDB Instance       │           │
│                           │ /root/sergio_chatbot/    │           │
│                           │  chromadb/               │           │
│                           │                          │           │
│                           │  4 Collections:          │           │
│                           │  - sergio_personality    │           │
│                           │  - sergio_rhetorical     │           │
│                           │  - sergio_humor          │           │
│                           │  - sergio_corpus         │           │
│                           └──────────────────────────┘           │
│                                                                  │
│           ┌─────────────────────────────────────────┐           │
│           │  Claude Max CLI                         │           │
│           │  ~/.local/bin/claude (v2.0.55+)         │           │
│           │                                         │           │
│           │  --print --output-format stream-json    │           │
│           │  OAuth via ~/.claude/.credentials.json  │           │
│           └─────────────────────────────────────────┘           │
│                                                                  │
│           ┌─────────────────────────────────────────┐           │
│           │  Credentials Sync (Cron 5min)           │           │
│           │  WSL → Proxmox Container                │           │
│           └─────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Container Networking

| Service | Port (Container) | Port (Host) | Protocol | Notes |
|---------|------------------|------------|----------|-------|
| nginx | 80 | 80 → LB → 85.239.243.227 | HTTP/HTTPS | Reverse proxy, static files |
| Backend RAG | 3001 | Internal only | HTTP | Claude Max API server |
| Backend OpenRouter | 5000 | Internal only | HTTP | Not currently active |
| ChromaDB | 8000 | Internal only | HTTP | Vector database |

### 2.3 Storage Architecture

| Component | Location | Size | Purpose |
|-----------|----------|------|---------|
| Frontend Build | `/opt/if-emotion/dist/` | ~2.5MB | Compiled React app |
| ChromaDB Data | `/root/sergio_chatbot/chromadb/` | ~184KB | Vector embeddings (4 collections) |
| Backend Code | `/root/sergio_chatbot/` | Various | Python backend services |
| Logs | `/tmp/rag_api.log` | Rotating | Backend request logs |
| nginx logs | `/var/log/nginx/` | Rotating | HTTP access/error logs |

---

## Frontend Components

### 3.1 Technology Stack

```json
{
  "name": "if-emotion-ux",
  "framework": "React 18.3.1",
  "language": "TypeScript 5.8.2",
  "styling": "Tailwind CSS 4",
  "build": "Vite 6.2.0",
  "ui-icons": "lucide-react 0.344.0",
  "markdown": "react-markdown 9.0.1",
  "pdf": "jsPDF 2.5.1",
  "node": "v20.19.5",
  "npm": "v10.8.2"
}
```

### 3.2 Directory Structure

```
/home/setup/if-emotion-ux/
├── App.tsx                           # Main application component
├── index.tsx                         # React entry point
├── index.html                        # HTML shell
├── vite.config.ts                    # Vite build configuration
├── tsconfig.json                     # TypeScript configuration
├── package.json                      # Dependencies
├── package-lock.json                 # Lockfile
│
├── components/                       # React components
│   ├── ChatInput.tsx                # Message input with off-record toggle
│   ├── ChatMessage.tsx              # Message display wrapper
│   ├── ExportModal.tsx              # Export to JSON/PDF/MD/TXT
│   ├── Header.tsx                   # Top navigation bar
│   ├── InputArea.tsx                # Combined input + actions
│   ├── JourneyHeader.tsx            # Title section
│   ├── MessageActions.tsx           # Message reactions/delete
│   ├── MessageBubble.tsx            # Styled message container
│   ├── OffTheRecordToggle.tsx       # Privacy mode toggle
│   ├── SettingsModal.tsx            # Configuration dialog
│   └── Sidebar.tsx                  # Session list + navigation
│
├── services/                         # Backend integration
│   ├── openwebui.ts                 # OpenWebUI API client
│   └── gemini.ts                    # Gemini API client (unused)
│
├── types.ts                         # TypeScript interfaces
├── constants.ts                     # App constants (text, labels)
├── utils.ts                         # Utility functions
│
├── dist/                            # Compiled output (Vite build)
├── .git/                            # Git repository
└── node_modules/                    # Dependencies (not deployed)
```

### 3.3 Component Details

#### **App.tsx** (Main Application)
- **Purpose:** Central state management and orchestration
- **State Managed:**
  - `sessions` - Array of chat sessions
  - `currentSessionId` - Active session UUID
  - `messages` - Messages in current session
  - `isLoading` - Streaming status
  - `isOffTheRecord` - Privacy mode toggle
  - `selectedModel` - Active AI model selection
  - `settings` - User preferences (baseUrl, apiKey)
- **Key Features:**
  - Responsive sidebar (auto-hidden on mobile <768px, shown on desktop)
  - Session persistence via localStorage
  - Model discovery from backend
  - SSE streaming for real-time responses

**Code Reference:**
```typescript
// Session management
const [sessions, setSessions] = useState<Session[]>([]);
const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
const [messages, setMessages] = useState<Message[]>([]);

// Off-record (privacy) mode
const [isOffTheRecord, setIsOffTheRecord] = useState(false);

// Settings stored in localStorage
const [settings, setSettings] = useState<UserSettings>(() => {
  const saved = localStorage.getItem('if.emotion.settings');
  return saved ? JSON.parse(saved) : {
    baseUrl: window.location.origin,  // nginx proxy
    apiKey: 'if-emotion-local'       // placeholder
  };
});

// Responsive sidebar
const [isSidebarOpen, setIsSidebarOpen] = useState(() =>
  typeof window !== 'undefined' && window.innerWidth >= 768
);
```

#### **Sidebar.tsx** (Session Navigation)
- **Purpose:** List, create, and manage chat sessions
- **Features:**
  - Group sessions by date (Today, Yesterday, Older)
  - New chat creation
  - Session selection
  - Delete session
  - Mobile overlay with backdrop blur
  - Responsive positioning (fixed overlay on mobile)

#### **ChatInput.tsx** (Message Input)
- **Purpose:** User message composition with context
- **Features:**
  - Auto-expanding textarea (max 150px height)
  - Send on Enter (Shift+Enter for newline)
  - Off-record toggle (privacy mode indicator)
  - Loading state handling
  - Sergio color scheme styling

**Color Palette:**
```css
/* Sergio brand colors */
.bg-sergio-50    /* Light beige background */
.bg-sergio-100   /* Lighter sidebar */
.border-sergio-200 /* Light borders */
.border-sergio-300 /* Medium borders */
.bg-sergio-900   /* Dark overlay */
```

#### **ExportModal.tsx** (Export Functionality)
- **Purpose:** Download conversation in multiple formats
- **Supported Formats:**
  - JSON (raw data)
  - TXT (plain text)
  - MD (markdown)
  - PDF (formatted document with jsPDF)
- **Implementation:** Uses `jsPDF` library for PDF generation

#### **SettingsModal.tsx** (Configuration)
- **Purpose:** User preferences and backend configuration
- **Settable Options:**
  - Backend URL (baseUrl)
  - API Key
  - Model selection
  - Language preference

### 3.4 Types and Interfaces

```typescript
// Message types (types.ts)
export enum Role {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system'
}

export interface Message {
  id: string;           // UUID
  role: Role;
  content: string;
  timestamp: Date;
  pending?: boolean;    // For optimistic updates
  error?: boolean;      // Error state
  reactions?: string[]; // User reactions (heart, reflect, question)
}

// Session types
export interface Session {
  id: string;
  title: string;
  updated_at: number;   // Unix timestamp
  folder_id?: string;
}

// Configuration
export interface UserSettings {
  baseUrl: string;      // Backend URL
  apiKey: string;       // Auth token
}

// Export options
export type ExportFormat = 'json' | 'txt' | 'md' | 'pdf';
```

### 3.5 Build & Development

**Development Server:**
```bash
cd /home/setup/if-emotion-ux
npm install
npm run dev
# Starts on http://localhost:3000
```

**Production Build:**
```bash
npm run build
# Outputs to ./dist/ directory
```

**Build Configuration (vite.config.ts):**
```typescript
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  return {
    server: {
      port: 3000,
      host: '0.0.0.0',  // Listen on all interfaces
    },
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      }
    }
  };
});
```

---

## Backend Architecture

### 4.1 Active Backend: claude_api_server_rag.py

**Location:** `/root/sergio_chatbot/claude_api_server_rag.py` (inside container 200)
**Port:** 3001
**Status:** PRODUCTION - ACTIVE
**Purpose:** OpenWebUI-compatible API with Claude Max CLI + ChromaDB RAG

#### 4.1.1 Key Features

1. **Claude Max CLI Integration**
   - Subprocess wrapper around `claude` binary (v2.0.55+)
   - Invokes: `claude --print --output-format stream-json`
   - Handles OAuth credentials from `~/.claude/.credentials.json`
   - Supports automatic token refresh on expiry

2. **ChromaDB RAG Enhancement**
   - Queries 4 personality collections before invoking Claude
   - Contextual prompt augmentation with Sergio DNA
   - 4 Collections:
     - `sergio_personality` (20 docs) - frameworks, values, constraints
     - `sergio_rhetorical` (5 docs) - rhetorical devices and patterns
     - `sergio_humor` (28 docs) - humor patterns and comedic timing
     - `sergio_corpus` (70 docs) - conversation examples and precedents
   - Weighted retrieval (personality > corpus > rhetorical > humor)

3. **Server-Sent Events (SSE) Streaming**
   - Implements `/api/chat/completions` endpoint (OpenWebUI standard)
   - Streams responses in real-time to browser
   - Parses Claude CLI JSON stream output
   - Handles connection drops gracefully

4. **Health & Monitoring Endpoints**
   - `GET /api/health` - Server status
   - `GET /api/models` - Available models list
   - `GET /api/version` - API version info
   - `POST /api/chat/completions` - Main inference endpoint

#### 4.1.2 API Endpoints

```
GET /api/health
Response: { status: "ok", timestamp: "2025-12-01T10:30:00Z" }

GET /api/models
Response: { models: ["claude-max", "claude-opus", "claude-sonnet"] }

GET /api/version
Response: { version: "1.0.0", claude_cli: "2.0.55" }

POST /api/chat/completions
Body: {
  model: "claude-max",
  messages: [
    { role: "user", content: "Hello" },
    { role: "assistant", content: "Hi!" }
  ],
  stream: true,
  temperature?: 0.7,
  max_tokens?: 2048
}

Response: SSE stream of JSON events:
  data: {"type":"content_block_start","content_block":{"type":"text"}}
  data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"Hello..."}}
  ...
```

#### 4.1.3 ChromaDB Collections

**Collection Structure:**
```python
# Vector database path
/root/sergio_chatbot/chromadb/

# Collections included
- sergio_personality     # Framework, values, decision-making patterns
- sergio_rhetorical      # Rhetorical devices, speaking patterns
- sergio_humor          # Comedic timing, jokes, humor strategies
- sergio_corpus         # Conversation examples, precedents

# Database Statistics
- Total embeddings: 123 documents
- Vector dimension: 1536 (OpenAI embeddings)
- Size: ~184KB (SQLite + embeddings)
- Query latency: <100ms
```

**RAG Augmentation Flow:**
```
User Query
    ↓
ChromaDB Query (similarity search)
    ↓
Retrieve top-k documents from 4 collections
    ↓
Weighted merge: personality (0.4) + corpus (0.3) + rhetorical (0.2) + humor (0.1)
    ↓
System prompt augmentation
    ↓
Claude Max CLI invocation with enhanced context
    ↓
Stream response to frontend
```

#### 4.1.4 Error Handling & Resilience

- **Token Expiry:** Auto-detect and prompt for re-authentication
- **CLI Crash:** Restart subprocess, preserve conversation context
- **Connection Loss:** Graceful disconnect, client reconnect support
- **Timeout:** 300s default (configurable via valves)
- **Empty Collections:** Graceful degradation (RAG disabled)

### 4.2 Inactive Backend: openwebui_server.py

**Location:** `/opt/if-emotion/backend/openwebui_server.py`
**Port:** 5000
**Status:** INACTIVE - LEGACY
**Purpose:** OpenRouter proxy (not used in current deployment)

#### 4.2.1 Configuration

```python
# Alternative backend configuration
OPENROUTER_API_KEY = "sk-or-v1-..."
OPENROUTER_BASE_URL = "https://openrouter.io/api/v1"

# Supported models via OpenRouter:
# - OpenAI GPT-4, GPT-3.5
# - Anthropic Claude (via OpenRouter)
# - Meta Llama
# - Mistral
```

**Why Not Active:**
- Claude Max CLI provides direct, authenticated access to Claude
- OpenRouter adds unnecessary latency and cost
- OAuth credentials managed natively by Claude CLI
- RAG integration cleaner with direct CLI wrapper

### 4.3 Logging & Debugging

**Backend Logs:**
```bash
# View real-time logs
tail -f /tmp/rag_api.log

# Log format
[2025-12-01 10:30:45] INFO - Incoming request: POST /api/chat/completions
[2025-12-01 10:30:45] DEBUG - RAG query: "user message" (4 collections)
[2025-12-01 10:30:46] INFO - Claude CLI response: 1250 tokens
[2025-12-01 10:30:46] DEBUG - SSE stream started (45 chunks)
```

**nginx Logs:**
```bash
# Access logs
tail -f /var/log/nginx/access.log

# Error logs
tail -f /var/log/nginx/error.log

# Example access log
85.239.243.227 - - [01/Dec/2025:10:30:45 +0000] "POST /api/chat/completions HTTP/1.1" 200 2048 "https://85.239.243.227/" "Mozilla/5.0..."
```

---

## Deployment Infrastructure

### 5.1 Host Infrastructure

**Physical Host:**
- **IP:** 85.239.243.227
- **Hypervisor:** Proxmox VE
- **Location:** Data center deployment

**nginx Reverse Proxy (Host Level):**
- **Port:** 80 (HTTP) / 443 (HTTPS if enabled)
- **Function:** Public gateway to container
- **Configuration:** `/etc/nginx/sites-enabled/default` (host)
- **Proxy Target:** Container 200 port 80

**Port Forwarding:**
```
85.239.243.227:80 (host) → Container 200:80 (nginx)
  ├─ Static: /* → /opt/if-emotion/dist/
  └─ API: /api/* → http://localhost:3001
```

### 5.2 Container 200 (LXC Linux Container)

**Container Specifications:**
- **Container ID:** 200
- **OS:** Debian/Ubuntu Linux
- **Memory:** [varies by Proxmox config]
- **Storage:** [varies by Proxmox config]
- **Networking:** Bridge interface to 85.239.243.227

**Container nginx Configuration:**
```nginx
# /etc/nginx/sites-enabled/default (inside container)

upstream backend_rag {
    server localhost:3001;
    keepalive 32;
}

server {
    listen 80;
    server_name _;
    client_max_body_size 100M;

    # Root directory for static files
    root /opt/if-emotion/dist;
    index index.html;

    # API proxy - SSE streaming configuration
    location /api/ {
        proxy_pass http://backend_rag;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE streaming headers (crucial!)
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding on;

        # Timeouts for long-lived connections
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }

    # Static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # SPA routing - serve index.html for all unmatched routes
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

**Key nginx Configuration Notes:**
1. **SSE Headers:** `proxy_buffering off` + `chunked_transfer_encoding on` required for streaming
2. **Keepalive:** Configured for connection reuse to backend
3. **Timeouts:** 600s to accommodate long Claude responses
4. **Two nginx Instances:** Host (reverse proxy) + Container (application server)
  - Only container nginx should be active
  - Host nginx forwards to container nginx
  - Legacy duplicate configs should be removed

### 5.3 Directory Structure (Container)

```
/opt/if-emotion/
├── dist/                    # Frontend compiled files (symlink or direct copy)
│   ├── index.html          # SPA shell
│   ├── assets/
│   │   ├── *.js            # Compiled JavaScript
│   │   └── *.css           # Compiled CSS
│   └── favicon.ico
│
└── backend/                # Backend code directory
    └── openwebui_server.py # Legacy OpenRouter backend (not active)

/root/sergio_chatbot/
├── claude_api_server_rag.py     # ACTIVE backend
├── chromadb/                    # Vector database
│   ├── chroma.sqlite3           # Metadata store
│   ├── embeddings_index/        # Vector index
│   └── data/                    # Collection data
└── logs/
    └── rag_api.log              # Backend logs
```

### 5.4 Credentials Management

**Claude CLI OAuth Credentials:**

Location: `~/.claude/.credentials.json` (inside container at `/root/.claude/`)

```json
{
  "accessToken": "sk-auth-...",
  "refreshToken": "sk-refresh-...",
  "expiresAt": 1735689600000,
  "subscriptionType": "free|pro",
  "apiVersion": "2024-12-01"
}
```

**Credential Sync Mechanism:**

Automated sync from WSL `~/.claude/` to container `/root/.claude/` every 5 minutes:

```bash
# Sync script location
/home/setup/.claude/sync-creds-to-proxmox.sh

# Cron job (runs every 5 minutes)
*/5 * * * * /home/setup/.claude/sync-creds-to-proxmox.sh >> /home/setup/.claude/.sync-proxmox.log 2>&1

# Sync process
1. Check local credentials hash
2. scp to Proxmox host /tmp/.credentials.json
3. pct push into container /root/.claude/.credentials.json
4. chmod 600 inside container
5. Clean up temp file
```

**Sync Log Location:** `/home/setup/.claude/.sync-proxmox.log` (on WSL)

---

## Configuration Reference

### 6.1 Frontend Environment Variables

**Location:** `/home/setup/if-emotion-ux/.env` (development)

```bash
# Backend API configuration
VITE_API_URL=http://localhost:3001    # Dev: local backend
VITE_API_URL=https://85.239.243.227   # Prod: remote backend

# Optional: Gemini API (currently unused)
VITE_GEMINI_API_KEY=your-key-here

# Build-time constants (in vite.config.ts)
process.env.API_KEY = "if-emotion-local"
process.env.GEMINI_API_KEY = ""
```

**Runtime Configuration:**
```typescript
// App.tsx - Load settings from localStorage
const [settings, setSettings] = useState<UserSettings>(() => {
  const saved = localStorage.getItem('if.emotion.settings');
  return saved ? JSON.parse(saved) : {
    baseUrl: window.location.origin,    // Use current origin (nginx)
    apiKey: 'if-emotion-local'         // Placeholder
  };
});
```

### 6.2 Backend Configuration (claude_api_server_rag.py)

**Configurable Parameters (Valves):**

```python
class Pipe:
    class Valves(BaseModel):
        CLAUDE_CLI_PATH: str = Field(
            default="claude",
            description="Path to Claude CLI binary"
        )
        CHROMADB_PATH: str = Field(
            default="/root/sergio_chatbot/chromadb",
            description="ChromaDB persistence directory"
        )
        ENABLE_RAG: bool = Field(
            default=True,
            description="Enable Sergio personality RAG"
        )
        AUTO_UPDATE_CLI: bool = Field(
            default=False,
            description="Auto-check Claude CLI updates"
        )
        MIN_CLI_VERSION: str = Field(
            default="2.0.55",
            description="Minimum Claude CLI version"
        )
        SESSION_TIMEOUT: int = Field(
            default=300,
            description="CLI subprocess timeout (seconds)"
        )
        MAX_RAG_CONTEXT: int = Field(
            default=2000,
            description="Maximum RAG context tokens"
        )
        RAG_WEIGHTS: dict = Field(
            default={
                "personality": 0.4,
                "corpus": 0.3,
                "rhetorical": 0.2,
                "humor": 0.1
            },
            description="Collection weighting for RAG"
        )
```

### 6.3 nginx Configuration Details

**Host nginx (85.239.243.227):**

```nginx
# /etc/nginx/sites-available/default (on host)

upstream proxmox_container_200 {
    server 127.0.0.1:5000;  # Or container IP if accessible
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://proxmox_container_200;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Container nginx (inside container 200):**

See section [5.2 Container nginx Configuration](#52-container-200-lxc-linux-container)

### 6.4 Docker/Container Variables

**Environment variables (if using Docker):**

```bash
# Backend configuration
CLAUDE_CLI_PATH=/root/.local/bin/claude
CHROMADB_PATH=/root/sergio_chatbot/chromadb
ENABLE_RAG=true
MAX_RAG_CONTEXT=2000

# Frontend
NGINX_ROOT=/opt/if-emotion/dist
BACKEND_URL=http://localhost:3001

# Credentials
CREDENTIALS_FILE=/root/.claude/.credentials.json
```

---

## Operations & Monitoring

### 7.1 Health Checks

**Frontend Status:**
```bash
# Test via container
curl -I http://localhost:80/

# Expected response
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Cache-Control: public
```

**Backend RAG Status:**
```bash
# Health endpoint
curl http://localhost:3001/api/health

# Expected response
{
  "status": "ok",
  "timestamp": "2025-12-01T10:30:00Z",
  "claude_cli": "2.0.55",
  "chromadb": "ready",
  "collections": 4
}
```

**Model Listing:**
```bash
curl http://localhost:3001/api/models

# Expected response
{
  "models": ["claude-max", "claude-opus", "claude-sonnet"],
  "default": "claude-max"
}
```

**Full System Check Script:**

```bash
#!/bin/bash
# /root/health_check.sh

echo "IF.emotion System Health Check"
echo "=============================="

# Frontend
echo -n "Frontend (nginx): "
curl -s -o /dev/null -w "%{http_code}" http://localhost:80/ && echo " OK" || echo " FAIL"

# Backend
echo -n "Backend (port 3001): "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/api/health && echo " OK" || echo " FAIL"

# ChromaDB
echo -n "ChromaDB Collections: "
python3 << 'EOF'
import chromadb
client = chromadb.PersistentClient(path="/root/sergio_chatbot/chromadb")
collections = client.list_collections()
print(f"{len(collections)} collections OK")
EOF

# Claude CLI
echo -n "Claude CLI: "
which claude > /dev/null && echo "OK" || echo "FAIL"
claude --version 2>/dev/null || echo "Version check failed"

# Credentials
echo -n "Credentials file: "
[ -f ~/.claude/.credentials.json ] && echo "OK" || echo "MISSING"

# Logs
echo -n "Recent errors: "
grep -i "error" /tmp/rag_api.log 2>/dev/null | wc -l
```

### 7.2 Log Monitoring

**Backend Logs (RAG API Server):**

```bash
# Real-time tail
tail -f /tmp/rag_api.log

# Filter errors
grep -i "error\|exception\|fatal" /tmp/rag_api.log

# Count requests per minute
grep "INFO.*Request" /tmp/rag_api.log | cut -d' ' -f1-2 | sort | uniq -c

# Monitor RAG queries
grep "RAG query" /tmp/rag_api.log

# Example log output
[2025-12-01 10:30:45] INFO - Starting claude_api_server_rag.py
[2025-12-01 10:30:45] INFO - ChromaDB loaded: 4 collections (123 docs)
[2025-12-01 10:30:46] INFO - Claude CLI available: v2.0.55
[2025-12-01 10:30:47] INFO - Incoming: POST /api/chat/completions
[2025-12-01 10:30:47] DEBUG - RAG: 'hello' → retrieved 8 docs
[2025-12-01 10:30:48] INFO - Claude response: 1245 tokens, 45 chunks
```

**nginx Logs:**

```bash
# Access logs
tail -f /var/log/nginx/access.log

# Error logs
tail -f /var/log/nginx/error.log

# Real-time monitoring
watch 'tail -n 20 /var/log/nginx/access.log'

# Request count per hour
grep "01/Dec/2025" /var/log/nginx/access.log | cut -d' ' -f4 | cut -d: -f2 | sort | uniq -c
```

**Credential Sync Logs:**

```bash
# WSL side (host machine)
tail -f /home/setup/.claude/.sync-proxmox.log

# Example output
[2025-12-01 10:30:00] 🔄 Syncing credentials to Proxmox container 200...
[2025-12-01 10:30:02] ✅ Synced successfully (2025-12-01 10:30:02) - 2048 bytes
[2025-12-01 10:30:02] ✅ Permissions set to 600
[2025-12-01 10:35:00] 🔄 Syncing credentials to Proxmox container 200...
[2025-12-01 10:35:02] ✅ Synced successfully (2025-12-01 10:35:02) - 2048 bytes
```

### 7.3 Performance Monitoring

**Response Time Monitoring:**

```bash
# Extract response times from nginx logs
awk '{print $NF}' /var/log/nginx/access.log | sort -n | tail -20

# Calculate percentiles
grep "POST /api/chat" /var/log/nginx/access.log | awk '{print $NF}' | sort -n | awk '
  {times[NR] = $1}
  END {
    n = length(times)
    print "P50: " times[int(n*0.5)]
    print "P95: " times[int(n*0.95)]
    print "P99: " times[int(n*0.99)]
  }'
```

**Resource Usage:**

```bash
# Check container memory/CPU
lxc-info -n 200 -s

# Monitor in real-time
watch -n 1 'lxc-info -n 200 -s | grep -E "CPU|Memory"'

# Check disk usage
du -sh /opt/if-emotion/
du -sh /root/sergio_chatbot/chromadb/
```

### 7.4 Alerting & Escalation

**Critical Issues:**

| Issue | Detection | Action |
|-------|-----------|--------|
| Backend crash | Health check fails | Restart `python -m claude_api_server_rag` |
| nginx crash | Port 80 unreachable | Restart `systemctl restart nginx` |
| Cred sync failure | Sync log has errors | Manual sync or check SSH keys |
| Claude CLI missing | `which claude` fails | Install Claude CLI |
| ChromaDB corrupted | Query timeouts | Restore from backup |
| Disk full | df shows 100% | Clean logs or expand storage |

---

## Known Issues & Gotchas

### 8.1 Duplicate nginx Configurations

**Issue:** Two nginx configs were created:
- Default nginx config (should be active)
- `if-emotion` specific config (conflicts with default)

**Impact:** Only the default nginx config should be enabled
- Multiple configs listening on port 80 cause binding errors
- Legacy `if-emotion` nginx config should be disabled

**Resolution:**
```bash
# Inside container 200
# Verify active config
ls -la /etc/nginx/sites-enabled/

# Expected: Only 'default' link should be active
# If 'if-emotion' exists, disable it:
rm /etc/nginx/sites-enabled/if-emotion
systemctl reload nginx

# Verify
curl http://localhost:80/  # Should work
```

### 8.2 Sidebar Mobile Behavior

**Issue:** Sidebar visibility varies by screen width

**Behavior:**
- Desktop (≥768px): Sidebar auto-visible on load
- Mobile (<768px): Sidebar auto-hidden on load (requires click to show)

**Code Reference (App.tsx):**
```typescript
const [isSidebarOpen, setIsSidebarOpen] = useState(() => {
  return typeof window !== 'undefined' && window.innerWidth >= 768;
});

// Responsive handler
useEffect(() => {
  const handleResize = () => {
    if (window.innerWidth >= 768) {
      setIsSidebarOpen(true);      // Auto-open on desktop
    } else {
      setIsSidebarOpen(false);     // Auto-close on mobile
    }
  };
  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, []);
```

**Workaround:** Manually click hamburger icon to toggle sidebar on mobile

### 8.3 OpenRouter Backend Not Active

**Issue:** `openwebui_server.py` exists but is not used

**Reason:** Claude Max CLI provides better benefits:
- Direct OAuth authentication (no separate API keys)
- Lower latency (no proxy hops)
- ChromaDB RAG integration cleaner
- Cost-effective (no OpenRouter fees)

**Status:** Legacy code, safe to keep for reference but should not be deployed

**If Needed to Reactivate:**
```bash
# Start on port 5000 (not forwarded currently)
python /opt/if-emotion/backend/openwebui_server.py

# Would require nginx config change:
# location /api/ {
#     proxy_pass http://localhost:5000;  # Instead of 3001
# }
```

### 8.4 ChromaDB Size (Not a Bottleneck)

**Issue:** ChromaDB is only 184KB - seems small

**Reality:** This is normal and healthy
- SQLite database is highly efficient
- Vector embeddings compressed
- 123 documents across 4 collections
- Query latency <100ms

**Scaling:** If needed:
- ChromaDB handles 1000s of documents without performance issues
- Currently nowhere near limits

### 8.5 SSE Streaming Configuration

**Issue:** If responses aren't streaming in real-time:

**Symptoms:**
- Long delay before first character appears
- Response comes all at once instead of incrementally

**Root Causes & Fixes:**

```nginx
# WRONG: causes buffering
proxy_buffering on;

# CORRECT: disables buffering for streaming
proxy_buffering off;
proxy_cache off;
chunked_transfer_encoding on;
proxy_set_header Connection '';
```

**Verify Streaming:**
```bash
# Check if response streams properly
curl -N http://localhost:3001/api/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-max","messages":[{"role":"user","content":"hello"}],"stream":true}'

# Should output in real-time, not all at once
```

### 8.6 Credentials Sync Timing

**Issue:** Claude CLI credentials expire and don't auto-refresh

**Context:**
- Cron sync runs every 5 minutes
- If credentials expire between syncs, users see auth errors
- Backend should prompt for re-login

**Current Behavior:**
- Backend detects token expiry
- Returns auth error to frontend
- User can manually update credentials or re-authenticate

**Future Improvement:**
- Add frontend UI for OAuth flow
- Automatic re-auth with browser redirect
- Graceful token refresh without user intervention

---

## Deployment Procedures

### 9.1 Initial Deployment (New Environment)

**Prerequisites:**
- Proxmox container 200 running Linux (Debian/Ubuntu)
- Node.js v20+ installed
- Python 3.8+ installed
- Claude CLI installed in container
- Internet access for dependencies

**Step 1: Build Frontend**

```bash
# On local machine (or WSL)
cd /home/setup/if-emotion-ux
npm install
npm run build

# Output in /home/setup/if-emotion-ux/dist/
```

**Step 2: Copy to Server**

```bash
# Sync frontend files to Proxmox host
scp -r dist/ root@85.239.243.227:/tmp/if-emotion-dist/

# Or using pct push
pct push 200 /home/setup/if-emotion-ux/dist /opt/if-emotion/
```

**Step 3: Deploy in Container**

```bash
# Inside container 200
mkdir -p /opt/if-emotion/dist
cp -r /tmp/if-emotion-dist/* /opt/if-emotion/dist/

# Verify
ls -la /opt/if-emotion/dist/
# Should show: index.html, assets/, favicon.ico
```

**Step 4: Setup Backend**

```bash
# Copy backend code
mkdir -p /root/sergio_chatbot
cp claude_api_server_rag.py /root/sergio_chatbot/

# Create ChromaDB directory
mkdir -p /root/sergio_chatbot/chromadb

# Install Python dependencies
pip install chromadb flask anthropic

# Create systemd service (optional, for auto-start)
# See section 9.4
```

**Step 5: Configure nginx**

```bash
# Inside container
# Ensure /etc/nginx/sites-enabled/default exists and points to:
# - root /opt/if-emotion/dist;
# - upstream localhost:3001 for /api/*

# Test config
nginx -t
# Should output: "nginx: configuration syntax is ok"

# Start nginx
systemctl restart nginx
```

**Step 6: Start Backend**

```bash
# Inside container
cd /root/sergio_chatbot
python -m claude_api_server_rag &

# Or with logging
nohup python -m claude_api_server_rag > /tmp/rag_api.log 2>&1 &

# Verify
curl http://localhost:3001/api/health
```

**Step 7: Verify Full Stack**

```bash
# From WSL
curl https://85.239.243.227/

# Should return HTML of if.emotion frontend
# Then in browser: https://85.239.243.227/
```

### 9.2 Rolling Update (Frontend Only)

**Use Case:** Update React UI without restarting backend

**Procedure:**

```bash
# 1. Build new frontend locally
cd /home/setup/if-emotion-ux
npm run build

# 2. Copy to server
scp -r dist/* root@85.239.243.227:/tmp/if-emotion-dist/

# 3. Update in container
pct exec 200 -- /bin/bash << 'EOF'
rm -rf /opt/if-emotion/dist/*
cp -r /tmp/if-emotion-dist/* /opt/if-emotion/dist/
systemctl reload nginx
EOF

# 4. Verify
curl https://85.239.243.227/
```

**Zero-Downtime:** Users on active chats can continue. New users get updated version.

### 9.3 Rolling Update (Backend Only)

**Use Case:** Update Claude API server without frontend rebuild

**Procedure:**

```bash
# 1. Copy new backend code
scp claude_api_server_rag.py root@85.239.243.227:/tmp/

# 2. Update in container
pct exec 200 -- /bin/bash << 'EOF'
# Kill old process (can be graceful or hard)
pkill -f claude_api_server_rag || true

# Wait for graceful shutdown
sleep 2

# Copy new code
cp /tmp/claude_api_server_rag.py /root/sergio_chatbot/

# Start new process
cd /root/sergio_chatbot
nohup python -m claude_api_server_rag > /tmp/rag_api.log 2>&1 &

# Verify
sleep 3
curl http://localhost:3001/api/health
EOF
```

**Impact:** 2-3 second downtime for active streams (reconnect required)

### 9.4 Systemd Service (Auto-start Backend)

**Purpose:** Automatically restart backend on container reboot

**File:** `/etc/systemd/system/if-emotion-rag.service`

```ini
[Unit]
Description=IF.emotion Claude Max RAG Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/sergio_chatbot
ExecStart=/usr/bin/python3 -m claude_api_server_rag
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

**Enable Service:**

```bash
# Inside container
systemctl daemon-reload
systemctl enable if-emotion-rag.service
systemctl start if-emotion-rag.service

# Verify
systemctl status if-emotion-rag.service

# View logs
journalctl -u if-emotion-rag.service -f
```

### 9.5 Rollback Procedure

**Scenario:** New deployment causes issues, need to revert

**Frontend Rollback:**

```bash
# If you have previous build backed up
tar -xzf /backups/if-emotion-dist-2025-11-30.tar.gz -C /opt/if-emotion/
systemctl reload nginx
```

**Backend Rollback:**

```bash
# If you have previous version backed up
cp /backups/claude_api_server_rag_2025-11-30.py /root/sergio_chatbot/claude_api_server_rag.py
pkill -f claude_api_server_rag || true
sleep 2
cd /root/sergio_chatbot
nohup python -m claude_api_server_rag > /tmp/rag_api.log 2>&1 &
```

**Best Practice:** Always keep 2-3 previous builds backed up:

```bash
# Create backup before deployment
tar -czf /backups/if-emotion-dist-$(date +%Y-%m-%d).tar.gz /opt/if-emotion/dist/
tar -czf /backups/claude_api_server_rag_$(date +%Y-%m-%d).tar.gz /root/sergio_chatbot/claude_api_server_rag.py

# Keep last 3 backups
cd /backups && ls -t if-emotion-dist-*.tar.gz | tail -n +4 | xargs rm -f
```

---

## Future Development

### 10.1 Planned Features: Claude Max CLI Integration

**Status:** Design Phase (CLAUDE_MAX_OPENWEBUI_WRAPPER_DESIGN.md)

**Vision:** Full Claude Max OpenWebUI pipe function with:
- Native OAuth token management
- Enhanced RAG with 4 ChromaDB collections
- Automatic token refresh on expiry
- Version checking for CLI updates

**Component Architecture:**

```
ClaudeMaxPipe (OpenWebUI Pipe Function)
├── AuthenticationManager
│   ├── Read ~/.claude/.credentials.json
│   ├── Validate token expiry
│   ├── Refresh expired tokens
│   └── Prompt re-login if needed
├── ChromaDBIntegrator
│   ├── Query 4 personality collections
│   ├── Build context augmentation
│   └── Weighted retrieval (personality > corpus > rhetoric > humor)
└── CLISubprocessHandler
    ├── Spawn claude --print --output-format stream-json
    ├── Parse SSE stream
    ├── Handle timeouts
    └── Implement error recovery
```

### 10.2 Performance Optimizations

**Potential Improvements:**

1. **Frontend:**
   - Code splitting for lazy loading
   - Image optimization with WebP
   - Service Worker for offline mode
   - Virtual scrolling for large message lists

2. **Backend:**
   - RAG query caching (Redis)
   - ChromaDB index optimization
   - Connection pooling to Claude CLI
   - Response streaming optimization

3. **Infrastructure:**
   - CDN for static assets
   - Database replication/clustering
   - Load balancing across containers
   - Horizontal scaling

### 10.3 Security Enhancements

**Recommended:**

1. **Authentication:**
   - Session tokens (JWT)
   - Rate limiting per user
   - HTTPS/TLS enforcement
   - CSRF token rotation

2. **Data Protection:**
   - Encryption at rest (ChromaDB)
   - Encryption in transit (TLS 1.3)
   - PII detection and masking
   - Audit logging

3. **Access Control:**
   - Role-based access (RBAC)
   - API key rotation
   - IP whitelisting
   - DDoS protection

### 10.4 Monitoring & Observability

**Recommended Tools:**

1. **Metrics:**
   - Prometheus for metrics collection
   - Grafana for dashboards
   - Custom health check endpoint

2. **Logging:**
   - ELK stack (Elasticsearch, Logstash, Kibana)
   - Log aggregation and analysis
   - Distributed tracing (Jaeger)

3. **Alerting:**
   - PagerDuty integration
   - Slack notifications
   - Custom alert rules

### 10.5 Testing & Quality Assurance

**Recommended:**

1. **Frontend Testing:**
   - Jest unit tests
   - React Testing Library
   - Cypress E2E tests
   - Accessibility testing

2. **Backend Testing:**
   - Pytest for Python
   - Mock Claude CLI responses
   - Integration tests
   - Load testing with k6

3. **Deployment Testing:**
   - Canary deployments
   - Blue-green deployments
   - Smoke tests
   - Rollback drills

---

## Appendix: Quick Reference

### A.1 Essential Commands

**Container Access:**
```bash
# SSH into container
pct exec 200 /bin/bash

# Or via Proxmox
ssh root@85.239.243.227
lxc-attach -n 200 -s
```

**Service Management (inside container):**
```bash
# nginx
systemctl restart nginx
systemctl status nginx
tail -f /var/log/nginx/access.log

# Backend (if systemd service)
systemctl restart if-emotion-rag
systemctl status if-emotion-rag
journalctl -u if-emotion-rag -f
```

**File Operations:**
```bash
# Copy from host
scp -r /local/path root@85.239.243.227:/remote/path

# Copy from host to container
pct push 200 /local/path /container/path

# Copy from container to host
pct pull 200 /container/path /local/path
```

**Debugging:**
```bash
# Test API
curl http://localhost:3001/api/health
curl http://localhost:3001/api/models
curl -X POST http://localhost:3001/api/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-max","messages":[{"role":"user","content":"test"}],"stream":true}'

# Check logs
tail -f /tmp/rag_api.log
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Monitor resources
watch -n 1 'top -b -n 1 | head -20'
df -h
du -sh /*
```

### A.2 Port Reference

| Port | Service | Protocol | Note |
|------|---------|----------|------|
| 80 | nginx | HTTP | Host gateway |
| 80 | nginx | HTTP | Container app server |
| 3001 | Claude API RAG | HTTP | Backend (ACTIVE) |
| 5000 | OpenRouter API | HTTP | Backend (INACTIVE) |
| 8000 | ChromaDB | HTTP | Internal only |

### A.3 File Locations Summary

| Path | Description |
|------|-------------|
| `/home/setup/if-emotion-ux` | Frontend source (WSL) |
| `/home/setup/if-emotion-ux/dist` | Frontend build output |
| `/opt/if-emotion/dist` | Deployed frontend (container) |
| `/root/sergio_chatbot/` | Backend code directory |
| `/root/sergio_chatbot/claude_api_server_rag.py` | Main backend server |
| `/root/sergio_chatbot/chromadb/` | Vector database |
| `/root/.claude/.credentials.json` | OAuth credentials (container) |
| `/tmp/rag_api.log` | Backend logs |
| `/var/log/nginx/` | Web server logs |
| `/etc/nginx/sites-enabled/default` | nginx config (container) |

### A.4 Error Resolution Guide

**Problem: Frontend shows 404**
```bash
# Check nginx is serving files
curl http://localhost:80/index.html

# Verify dist directory exists and has content
ls -la /opt/if-emotion/dist/

# Reload nginx config
nginx -t && systemctl reload nginx
```

**Problem: Backend returns 502/503**
```bash
# Check if backend is running
ps aux | grep claude_api_server_rag

# Check if port is listening
netstat -tlnp | grep 3001

# Restart backend
cd /root/sergio_chatbot
nohup python -m claude_api_server_rag > /tmp/rag_api.log 2>&1 &
```

**Problem: Streaming responses don't appear in real-time**
```bash
# Check nginx buffering config
grep proxy_buffering /etc/nginx/sites-enabled/default

# Should be: proxy_buffering off;

# Reload nginx if changed
systemctl reload nginx
```

**Problem: Messages not saving**
```bash
# Check if backend is storing sessions
curl http://localhost:3001/api/chats

# Check ChromaDB is accessible
python3 << 'EOF'
import chromadb
client = chromadb.PersistentClient(path="/root/sergio_chatbot/chromadb")
print(client.list_collections())
EOF
```

**Problem: Claude CLI not found**
```bash
# Check installation
which claude
claude --version

# If missing, install
curl https://claude.sh | bash
# Or: pip install claude-cli

# Ensure it's in PATH
export PATH="$HOME/.local/bin:$PATH"
```

---

## Document Metadata

**File Location:** `/home/setup/infrafabric/docs/IF_EMOTION_COMPLETE_GUIDE.md`

**Version History:**
- v2.0 (2025-12-01) - Comprehensive architecture + deployment guide
- v1.0 (2025-11-30) - Initial documentation framework

**Maintainer:** IF.guard Council / InfraFabric Project

**Last Reviewed:** 2025-12-01
**Next Review:** 2025-12-15 (or on major changes)

**Related Documents:**
- `/home/setup/if-emotion-ux/CLAUDE_MAX_OPENWEBUI_WRAPPER_DESIGN.md` - Claude Max design spec
- `/home/setup/infrafabric/agents.md` - Project-wide documentation
- `/home/setup/.claude/sync-creds-to-proxmox.sh` - Credential sync script
- `/home/setup/.claude/.sync-proxmox.log` - Sync operation logs

**Contact/Questions:**
- Review with IF.guard Council
- Consult agents.md for broader project context
- Check CLAUDE.md for local environment setup
