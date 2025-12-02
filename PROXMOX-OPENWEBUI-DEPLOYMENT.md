# Proxmox Open WebUI Deployment Plan

**Target:** Deploy Open WebUI + ChromaDB + Redis Commander on Proxmox LXC container
**Executor:** Haiku agents
**Location:** 85.239.243.227 (Proxmox host)
**Status:** Ready for execution

---

## Pre-Deployment Checklist

- [ ] Proxmox accessible at 85.239.243.227
- [ ] SSH access to Proxmox host configured
- [ ] LXC container template available (Ubuntu 22.04 or Debian 12)
- [ ] Docker installed on Proxmox host (for LXC container)
- [ ] Redis L2 running at 85.239.243.227:6379 (verified)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│ Proxmox Host: 85.239.243.227                            │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │ LXC Container: ai-workspace                      │    │
│  │                                                   │    │
│  │  ┌───────────────┐  ┌───────────────┐           │    │
│  │  │ Open WebUI    │  │ ChromaDB      │           │    │
│  │  │ Port: 8080    │  │ Port: 8000    │           │    │
│  │  └───────────────┘  └───────────────┘           │    │
│  │                                                   │    │
│  │  ┌───────────────┐  ┌───────────────┐           │    │
│  │  │ Redis         │  │ Volumes       │           │    │
│  │  │ Commander     │  │ - media/      │           │    │
│  │  │ Port: 8081    │  │ - archives/   │           │    │
│  │  └───────────────┘  └───────────────┘           │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Redis L2 (Existing)                              │    │
│  │ Port: 6379                                        │    │
│  │ Password: @@Redis_InfraFabric_L2_2025$$          │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘

Access from anywhere:
- Open WebUI: http://85.239.243.227:8080
- ChromaDB: http://85.239.243.227:8000
- Redis Commander: http://85.239.243.227:8081
```

---

## Step 1: Create LXC Container

**Executor: Haiku-Infrastructure**

### 1.1 SSH to Proxmox Host

```bash
ssh root@85.239.243.227
```

### 1.2 Create Privileged LXC Container

```bash
# Create container with Ubuntu 22.04 template
pct create 200 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname ai-workspace \
  --memory 4096 \
  --cores 2 \
  --rootfs local-lvm:20 \
  --net0 name=eth0,bridge=vmbr0,firewall=1,ip=dhcp \
  --features nesting=1,keyctl=1 \
  --unprivileged 0 \
  --password "@@AIWorkspace2025$$" \
  --start 1

# Wait for container to boot
sleep 10

# Enter container
pct enter 200
```

**Notes:**
- Container ID: 200 (adjust if conflict)
- 4GB RAM for Open WebUI + ChromaDB
- 2 CPU cores
- 20GB storage
- `nesting=1` enables Docker in LXC
- `unprivileged 0` = privileged container (required for Docker)

---

## Step 2: Install Docker in LXC Container

**Executor: Haiku-Infrastructure**

### 2.1 Update System

```bash
apt update && apt upgrade -y
```

### 2.2 Install Docker

```bash
# Install prerequisites
apt install -y \
  ca-certificates \
  curl \
  gnupg \
  lsb-release

# Add Docker GPG key
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### 2.3 Enable Docker Service

```bash
systemctl enable docker
systemctl start docker
systemctl status docker
```

---

## Step 3: Create Directory Structure

**Executor: Haiku-FileOps**

### 3.1 Create Project Directories

```bash
mkdir -p /opt/ai-workspace/{config,media,archives}

# Media libraries (for Open WebUI file uploads)
mkdir -p /opt/ai-workspace/media/{infrafabric,navidocs,icw,shared}

# Subdirectories per project
for project in infrafabric navidocs icw; do
  mkdir -p /opt/ai-workspace/media/$project/{documents,images,pdfs,videos}
done

# Shared library (read-only knowledge base)
mkdir -p /opt/ai-workspace/media/shared/{research-papers,technical-specs,media}

# Conversation archives
mkdir -p /opt/ai-workspace/archives/{json,markdown,daily-backups,important}

# Set permissions
chmod -R 755 /opt/ai-workspace
```

### 3.2 Verify Structure

```bash
tree -L 3 /opt/ai-workspace
```

---

## Step 4: Deploy Docker Compose Stack

**Executor: Haiku-Infrastructure**

### 4.1 Create docker-compose.yml

```bash
cat > /opt/ai-workspace/docker-compose.yml << 'EOF'
version: '3.8'

services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "8080:8080"
    volumes:
      # Open WebUI data storage
      - open-webui-data:/app/backend/data

      # Shared knowledge base (read-only - prevent accidental changes)
      - /opt/ai-workspace/media/shared:/data/shared:ro

      # Project-specific media libraries (read-write)
      - /opt/ai-workspace/media/infrafabric:/data/infrafabric:rw
      - /opt/ai-workspace/media/navidocs:/data/navidocs:rw
      - /opt/ai-workspace/media/icw:/data/icw:rw

      # Conversation archives (for backup scripts)
      - /opt/ai-workspace/archives:/data/archives:rw

    environment:
      # RAG and search features
      - ENABLE_RAG_WEB_SEARCH=true
      - ENABLE_RAG_HYBRID_SEARCH=true
      - ENABLE_RAG_LOCAL_WEB_FETCH=true

      # ChromaDB connection (for vector search)
      - CHROMA_HTTP_HOST=chromadb
      - CHROMA_HTTP_PORT=8000

      # Security and auth
      - WEBUI_AUTH=false
      - ENABLE_COMMUNITY_SHARING=false

      # Data persistence
      - DATA_DIR=/app/backend/data

      # API configurations
      - ANTHROPIC_API_BASE_URL=https://api.anthropic.com
      - OPENAI_API_BASE_URL=https://openrouter.ai/api/v1

    extra_hosts:
      - "host.docker.internal:host-gateway"

    restart: always
    depends_on:
      - chromadb

    networks:
      - ai-workspace

  chromadb:
    image: chromadb/chroma:latest
    container_name: chromadb
    ports:
      - "8000:8000"
    volumes:
      - chromadb-data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
      - ANONYMIZED_TELEMETRY=FALSE
      - CHROMA_SERVER_AUTH_CREDENTIALS_PROVIDER=chromadb.auth.token_authn.TokenAuthenticationServerProvider
      - CHROMA_SERVER_AUTH_PROVIDER=chromadb.auth.token_authn.TokenAuthenticationServerProvider
    restart: always
    networks:
      - ai-workspace

  redis-commander:
    image: ghcr.io/joeferner/redis-commander:latest
    container_name: redis-commander
    ports:
      - "8081:8081"
    environment:
      # Connect to Proxmox Redis L2 (existing instance)
      - REDIS_HOSTS=L2-Proxmox:host.docker.internal:6379:0:@@Redis_InfraFabric_L2_2025$$
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: always
    networks:
      - ai-workspace

volumes:
  open-webui-data:
    driver: local
  chromadb-data:
    driver: local

networks:
  ai-workspace:
    driver: bridge
EOF
```

### 4.2 Start Services

```bash
cd /opt/ai-workspace
docker compose up -d
```

### 4.3 Monitor Deployment

```bash
# Watch containers start
docker compose logs -f

# Check status (wait until all healthy)
docker compose ps
```

**Expected Output:**
```
NAME              IMAGE                                   STATUS
chromadb          chromadb/chroma:latest                  Up
open-webui        ghcr.io/open-webui/open-webui:main      Up
redis-commander   ghcr.io/joeferner/redis-commander:...   Up
```

---

## Step 5: Configure Firewall

**Executor: Haiku-Infrastructure**

### 5.1 Open Ports on Proxmox Host

```bash
# Exit container first
exit

# On Proxmox host, configure firewall
# Add rules to allow traffic to LXC container

# Get container IP
CONTAINER_IP=$(pct exec 200 -- hostname -I | awk '{print $1}')

echo "Container IP: $CONTAINER_IP"

# Configure iptables rules (if needed)
# OR use Proxmox web UI: Datacenter → Firewall → Add rules
```

### 5.2 Verify Accessibility

```bash
# From Proxmox host
curl http://localhost:8080
curl http://localhost:8000
curl http://localhost:8081

# From external (your laptop)
# http://85.239.243.227:8080 (Open WebUI)
# http://85.239.243.227:8000 (ChromaDB)
# http://85.239.243.227:8081 (Redis Commander)
```

---

## Step 6: Deploy Backup Scripts

**Executor: Haiku-FileOps**

### 6.1 Install Python Dependencies

```bash
pct enter 200  # Enter container

apt install -y python3 python3-pip python3-venv redis-tools
pip3 install redis
```

### 6.2 Transfer Backup Scripts from WSL

**On WSL (your laptop):**

```bash
# Copy backup scripts to Proxmox
scp /home/setup/infrafabric/tools/redis_cache_manager.py \
    root@85.239.243.227:/tmp/

scp /home/setup/infrafabric/tools/openwebui_redis_sync.py \
    root@85.239.243.227:/tmp/

scp /home/setup/infrafabric/tools/daily_conversation_backup.sh \
    root@85.239.243.227:/tmp/

scp /home/setup/infrafabric/tools/conversation_templates.md \
    root@85.239.243.227:/tmp/

scp /home/setup/infrafabric/.env.redis \
    root@85.239.243.227:/tmp/
```

**On Proxmox host:**

```bash
# Copy to LXC container
pct push 200 /tmp/redis_cache_manager.py /opt/ai-workspace/tools/redis_cache_manager.py
pct push 200 /tmp/openwebui_redis_sync.py /opt/ai-workspace/tools/openwebui_redis_sync.py
pct push 200 /tmp/daily_conversation_backup.sh /opt/ai-workspace/tools/daily_conversation_backup.sh
pct push 200 /tmp/conversation_templates.md /opt/ai-workspace/tools/conversation_templates.md
pct push 200 /tmp/.env.redis /opt/ai-workspace/.env.redis

# Set permissions
pct exec 200 -- chmod +x /opt/ai-workspace/tools/daily_conversation_backup.sh
pct exec 200 -- chmod 600 /opt/ai-workspace/.env.redis
```

### 6.3 Configure Cron Job

```bash
pct enter 200  # Enter container

# Add daily backup job
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/ai-workspace/tools/daily_conversation_backup.sh") | crontab -

# Verify cron job
crontab -l
```

### 6.4 Test Backup Manually

```bash
# Test backup script
/opt/ai-workspace/tools/daily_conversation_backup.sh

# Check logs
cat /opt/ai-workspace/logs/backup_$(date +%Y-%m-%d).log
```

---

## Step 7: Verification & Testing

**Executor: Haiku-QA**

### 7.1 Service Health Checks

```bash
cd /opt/ai-workspace

# Check all services running
docker compose ps

# Check logs for errors
docker compose logs --tail=50 open-webui
docker compose logs --tail=50 chromadb
docker compose logs --tail=50 redis-commander

# Verify Open WebUI database created
docker exec open-webui ls -lah /app/backend/data/
```

### 7.2 Network Accessibility Tests

```bash
# From container
curl http://localhost:8080 | head -20  # Open WebUI
curl http://localhost:8000/api/v1/heartbeat  # ChromaDB
curl http://localhost:8081 | head -20  # Redis Commander

# From Proxmox host
curl http://$(pct exec 200 -- hostname -I | awk '{print $1}'):8080
```

### 7.3 Redis L2 Connection Test

```bash
# Test Redis L2 connection from container
pct exec 200 -- redis-cli -h 85.239.243.227 -p 6379 \
  -a '@@Redis_InfraFabric_L2_2025$$' \
  PING
```

**Expected:** `PONG`

### 7.4 Media Library Access Test

```bash
# Verify volumes mounted
docker exec open-webui ls -la /data/
docker exec open-webui ls -la /data/infrafabric
docker exec open-webui ls -la /data/shared
```

---

## Step 8: Documentation & Handoff

**Executor: Haiku-Documentation**

### 8.1 Create Quick Reference

```bash
cat > /opt/ai-workspace/README.md << 'EOF'
# AI Workspace - Open WebUI Deployment

## Access URLs

- **Open WebUI:** http://85.239.243.227:8080
- **ChromaDB:** http://85.239.243.227:8000
- **Redis Commander:** http://85.239.243.227:8081

## Container Management

```bash
# SSH to Proxmox
ssh root@85.239.243.227

# Enter container
pct enter 200

# Check services
cd /opt/ai-workspace
docker compose ps

# View logs
docker compose logs -f

# Restart services
docker compose restart

# Stop services
docker compose stop

# Start services
docker compose start
```

## Backup System

**Daily Backup (Automated):**
- Runs at 2:00 AM daily
- Archives to `/opt/ai-workspace/archives/`
- Syncs to Redis L2 (permanent)

**Manual Backup:**
```bash
/opt/ai-workspace/tools/daily_conversation_backup.sh
```

**Check Backup Status:**
```bash
redis-cli -h 85.239.243.227 -p 6379 \
  -a '@@Redis_InfraFabric_L2_2025$$' \
  GET backup:daily:last_run
```

## Troubleshooting

**Open WebUI not accessible:**
```bash
docker compose logs open-webui
docker compose restart open-webui
```

**ChromaDB errors:**
```bash
docker compose logs chromadb
docker exec chromadb ls -la /chroma/chroma
```

**Backup failures:**
```bash
cat /opt/ai-workspace/logs/backup_$(date +%Y-%m-%d).log
```
EOF
```

### 8.2 Copy Quick Start Guide

```bash
# Copy from WSL (if needed)
# This provides user documentation
```

---

## Step 9: Post-Deployment Configuration

**Executor: User (Manual Steps)**

### 9.1 First-Time Open WebUI Setup

1. Open browser: `http://85.239.243.227:8080`
2. Create admin account:
   - Name: [Your name]
   - Email: [Your email]
   - Password: [Secure password]

3. Add API Keys (Settings → Connections):
   - **Anthropic:** API key + `https://api.anthropic.com`
   - **OpenRouter:** `sk-or-v1-...` + `https://openrouter.ai/api/v1`
   - **Google Gemini:** API key

4. Configure Collections (Settings → Workspace):
   - InfraFabric → `/data/infrafabric`
   - NaviDocs → `/data/navidocs`
   - ICW → `/data/icw`
   - Shared → `/data/shared`

---

## Rollback Plan

**If deployment fails:**

### Option 1: Restart Services

```bash
cd /opt/ai-workspace
docker compose down
docker compose up -d
```

### Option 2: Rebuild Container

```bash
# On Proxmox host
pct stop 200
pct destroy 200

# Start from Step 1 again
```

### Option 3: Revert to WSL

```bash
# WSL deployment still intact
# User can continue using WSL while Proxmox debugging
```

---

## Success Criteria

- [ ] LXC container running and accessible
- [ ] Docker installed and operational
- [ ] All 3 services running (Open WebUI, ChromaDB, Redis Commander)
- [ ] Port 8080, 8000, 8081 accessible from external
- [ ] Media libraries mounted correctly
- [ ] Redis L2 connection working (PING → PONG)
- [ ] Backup script tested successfully
- [ ] Cron job configured for daily backups
- [ ] Quick Start guide copied to Proxmox
- [ ] User can create first conversation in Open WebUI

---

## Next Steps After Deployment

1. **Transfer Existing Media Files** (if any from WSL):
   ```bash
   rsync -avz /home/setup/infrafabric/media/ \
     root@85.239.243.227:/opt/ai-workspace/media/infrafabric/

   rsync -avz /home/setup/navidocs/media/ \
     root@85.239.243.227:/opt/ai-workspace/media/navidocs/
   ```

2. **Configure VS Code Remote SSH** (optional):
   - Add Proxmox LXC as SSH target
   - Edit files directly in container
   - Full IDE experience on remote infrastructure

3. **Test Multi-Machine Workflow:**
   - Access from laptop: `http://85.239.243.227:8080`
   - Access from phone: Same URL
   - Verify conversations sync across devices

4. **Set Up Conversation Templates:**
   - Read `/opt/ai-workspace/tools/conversation_templates.md`
   - Practice Claude → Gemini → GPT handoffs
   - Export conversations as JSON/Markdown

---

## Contact & Support

**Deployment Issues:** Check logs at `/opt/ai-workspace/logs/`
**Backup Issues:** Test manually: `/opt/ai-workspace/tools/daily_conversation_backup.sh`
**Service Crashes:** `docker compose restart [service-name]`

**Documentation:**
- Open WebUI docs: https://docs.openwebui.com
- ChromaDB docs: https://docs.trychroma.com
- Redis Commander: https://github.com/joeferner/redis-commander
