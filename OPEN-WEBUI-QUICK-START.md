# Open WebUI Quick Start Guide

**Your New AI Workspace is Deploying!**

---

## What's Being Installed

1. **Open WebUI** - Beautiful chat interface (like Claude.ai + ChatGPT combined)
2. **ChromaDB** - Vector database for semantic search
3. **Redis Commander** - Visual browser for your Redis L2 data

---

## Access URLs (Once Deployed)

| Service | URL | Purpose |
|---------|-----|---------|
| **Open WebUI** | `http://localhost:8080` | Main chat interface |
| **ChromaDB** | `http://localhost:8000` | Vector search API |
| **Redis Commander** | `http://localhost:8081` | Browse Redis L2 data visually |

**From other devices on network:** Replace `localhost` with `85.239.243.227` (if on Proxmox) or your machine's IP

---

## First-Time Setup (After Deployment Completes)

### 1. Open Open WebUI

```bash
# In browser:
http://localhost:8080
```

### 2. Create Admin Account

- **Name:** [Your name]
- **Email:** [Your email]
- **Password:** [Choose secure password]

### 3. Add API Keys

Click **Settings** (gear icon) → **Connections**:

**Anthropic (Claude):**
```
API Key: [Your Anthropic API key]
Base URL: https://api.anthropic.com
```

**OpenRouter (GPT, Gemini, etc.):**
```
API Key: sk-or-v1-...
Base URL: https://openrouter.ai/api/v1
```

**Google (Gemini):**
```
API Key: [Your Google API key]
```

### 4. Configure Folders

Click **Settings** → **Workspace** → **Collections**:

Create collections for your projects:
- **InfraFabric** → Link to `/data/infrafabric`
- **NaviDocs** → Link to `/data/navidocs`
- **ICW NextSpread** → Link to `/data/icw`
- **Shared Library** → Link to `/data/shared`

---

## Daily Usage

### Starting a Conversation

1. Click **New Chat** (+)
2. Select model from dropdown (Claude Sonnet 4.5, GPT-4o, Gemini, etc.)
3. Select workspace/collection (InfraFabric, NaviDocs, etc.)
4. Start chatting!

### Uploading Files

- **Drag & drop** files directly into chat
- Or click **📎** attachment icon
- Files are automatically added to the active collection

### Switching Models Mid-Conversation

- Click model dropdown at top
- Select different model
- Continue conversation with new model
- Previous context is maintained!

### Exporting Conversations

Click **⋮** menu on any conversation:
- **Download as JSON** - Machine-readable, feed to APIs
- **Download as Markdown** - Human-readable, feed to LLMs
- **Share Link** - Create shareable URL
- **Pin** - Pin to top of sidebar
- **Add Tags** - Organize with #tags

---

## File Organization

Your media libraries are mounted as:

```
/home/setup/
├─ shared-media/              → /data/shared (read-only in Open WebUI)
│  ├─ research-papers/
│  ├─ technical-specs/
│  └─ media/
│
├─ infrafabric/media/         → /data/infrafabric
│  ├─ documents/
│  ├─ images/
│  ├─ pdfs/
│  └─ videos/
│
├─ navidocs/media/            → /data/navidocs
│  ├─ documents/
│  ├─ images/
│  ├─ pdfs/
│  └─ videos/
│
└─ icw-nextspread/media/      → /data/icw
   ├─ documents/
   ├─ images/
   └─ pdfs/
```

**Upload a file in Open WebUI → It's saved to your chosen project folder!**

---

## Automatic Backups

Your conversations are automatically backed up:

### Daily Backup (2 AM)

- **Script:** `/home/setup/infrafabric/tools/daily_conversation_backup.sh`
- **Schedule:** Every day at 2:00 AM (cron)
- **Output:**
  - Redis L2: `openwebui:conversation:*` keys (permanent)
  - JSON: `/home/setup/conversation-archives/daily-backups/json/`
  - Markdown: `/home/setup/conversation-archives/daily-backups/markdown/`
  - Archive: `/home/setup/conversation-archives/daily-backups/archives/`

### Manual Backup

```bash
cd /home/setup/infrafabric
python3 tools/openwebui_redis_sync.py
```

---

## Command Reference

### Check Deployment Status

```bash
cd /home/setup/infrafabric
docker compose -f docker-compose-openwebui.yml ps
```

### View Logs

```bash
# All services
docker compose -f docker-compose-openwebui.yml logs -f

# Specific service
docker logs open-webui -f
docker logs chromadb -f
docker logs redis-commander -f
```

### Stop Services

```bash
docker compose -f docker-compose-openwebui.yml stop
```

### Start Services

```bash
docker compose -f docker-compose-openwebui.yml start
```

### Restart Services

```bash
docker compose -f docker-compose-openwebui.yml restart
```

### Remove Everything (WARNING: Deletes data!)

```bash
docker compose -f docker-compose-openwebui.yml down -v
```

---

## Conversation Templates

Located at: `/home/setup/infrafabric/tools/conversation_templates.md`

**5 Templates Available:**
1. **Minimal Context Handoff** - Quick questions
2. **Full Context Handoff** - Complex multi-step work
3. **Code Review Handoff** - Request code reviews
4. **Multi-AI Collaboration** - Pass work between Claude/Gemini/GPT
5. **Session Boundary Handoff** - End of session handoffs

---

## Troubleshooting

### Can't Access Open WebUI

**Check if running:**
```bash
docker ps | grep open-webui
```

**If not running:**
```bash
cd /home/setup/infrafabric
docker compose -f docker-compose-openwebui.yml up -d
```

### Files Not Showing Up

**Check volume mounts:**
```bash
docker inspect open-webui | grep -A 10 Mounts
```

**Verify files exist:**
```bash
ls -la /home/setup/infrafabric/media/
```

### Conversations Not Backing Up

**Check backup logs:**
```bash
cat /home/setup/infrafabric/logs/backup_$(date +%Y-%m-%d).log
```

**Test backup manually:**
```bash
/home/setup/infrafabric/tools/daily_conversation_backup.sh
```

### Redis Commander Won't Connect

**Test Redis L2 connection:**
```bash
redis-cli -h 85.239.243.227 -p 6379 \
  -a '@@Redis_InfraFabric_L2_2025$$' \
  PING
```

Should return: `PONG`

---

## Tips & Tricks

### 1. Use Tags Liberally

Tag conversations for easy filtering:
- `#infrafabric` - InfraFabric work
- `#navidocs` - NaviDocs work
- `#urgent` - Needs attention
- `#research` - Research findings
- `#code-review` - Code reviews

### 2. Pin Important Conversations

Pin critical conversations to top of sidebar:
- Architecture decisions
- Session handoffs
- Important research
- Active projects

### 3. Use Folders for Projects

Organize conversations by project:
- **InfraFabric** folder - All InfraFabric chats
- **NaviDocs** folder - All NaviDocs chats
- **Job Hunt** folder - All job search chats

### 4. Export Before Major Changes

Before making significant code changes:
1. Export conversation as JSON
2. Save to `/home/setup/conversation-archives/important/`
3. Make changes
4. Reference export if you need to revert

### 5. Use Search

Open WebUI has powerful search:
- Search by content: "Redis L1/L2"
- Search by tag: "#redis"
- Search by date: Filter by "Last 7 days"
- Search by model: Filter by "Claude Sonnet 4.5"

---

## Next Steps

1. **Wait for deployment to complete** (5-10 minutes)
2. **Access Open WebUI** at `http://localhost:8080`
3. **Create admin account**
4. **Add API keys** (Anthropic, OpenRouter, Google)
5. **Start first conversation!**

---

## Support & Documentation

- **Conversation Templates:** `/home/setup/infrafabric/tools/conversation_templates.md`
- **Backup Script:** `/home/setup/infrafabric/tools/openwebui_redis_sync.py`
- **Daily Backup:** `/home/setup/infrafabric/tools/daily_conversation_backup.sh`
- **Deployment Logs:** `docker logs open-webui -f`
- **Backup Logs:** `/home/setup/infrafabric/logs/backup_*.log`

---

## What You Get

✅ **Beautiful Web UI** (no tmux needed!)
✅ **Claude.ai-like navigation** (conversation sidebar, search)
✅ **ChatGPT-like organization** (folders, tags, date grouping)
✅ **Export as JSON/Markdown** (LLM-readable formats)
✅ **Shareable links** (URL for each conversation)
✅ **Automatic backups** (Redis L2 + daily files)
✅ **Per-project media libraries** (InfraFabric, NaviDocs, ICW)
✅ **Cross-project search** (find anything)
✅ **Works from any device** (laptop, phone, desktop)
✅ **Completely private** (runs on YOUR server)

**Enjoy your new AI workspace!** 🚀
