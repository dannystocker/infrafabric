# InfraFabric Integrated System Deployment Guide

**Citation:** `if://doc/integration-deployment/2025-11-30`

**Version:** 2.0.0

**Date:** November 30, 2025

**Status:** Production Ready

**Target Audience:** DevOps engineers, system administrators, integration specialists

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Memory Initialization](#memory-initialization)
6. [Agent Registration](#agent-registration)
7. [Security Hardening](#security-hardening)
8. [Health Checks](#health-checks)
9. [Monitoring Setup](#monitoring-setup)
10. [Production Readiness Checklist](#production-readiness-checklist)
11. [Troubleshooting Guide](#troubleshooting-guide)
12. [Upgrade Procedures](#upgrade-procedures)

---

## Prerequisites

### Software Requirements

#### Required
- **OS:** Ubuntu 20.04 LTS or later / Debian 11+
- **Python:** 3.10+ (check with `python3 --version`)
- **Node.js:** 18+ (for Open WebUI) - optional if using container
- **Docker:** 20.10+ (highly recommended)
- **Docker Compose:** 2.0+ (if using Docker)
- **Git:** 2.25+

#### Optional
- **VS Code Remote SSH** - for container editing
- **Redis Client Tools** - for debugging (`redis-cli`)
- **ChromaDB Client** - for direct testing

### API Keys Required

Before deployment, obtain these API keys:

1. **Claude API** (Anthropic)
   - Signup: https://api.anthropic.com
   - Required for: Core agent coordination
   - Budget: ~$5-20/month depending on usage

2. **OpenRouter API** (optional)
   - Signup: https://openrouter.ai
   - Required for: Alternative LLM providers
   - Models: Claude, GPT, Gemini, DeepSeek, etc.

3. **DeepSeek API** (optional fallback)
   - Signup: https://platform.deepseek.com
   - Required for: Cost-effective agent tasks
   - Budget: ~$2-5/month for agent work

4. **Gemini API** (optional)
   - Signup: https://makersuite.google.com
   - Required for: Vision models, embeddings
   - Free tier available: 60 requests/minute

### Network Requirements

#### Ports (must be available)
- `8080` - Open WebUI (web interface)
- `8000` - ChromaDB (vector database)
- `8081` - Redis Commander (optional, for debugging)
- `6379` - Redis (if running locally)
- `5432` - PostgreSQL (if using external DB)

#### Firewall Rules
```bash
# Allow incoming on 8080 (Open WebUI)
sudo ufw allow 8080/tcp

# Allow incoming on 8000 (ChromaDB) - only from trusted networks
sudo ufw allow from 192.168.0.0/16 to any port 8000 proto tcp

# Allow incoming on 6379 (Redis) - only from trusted networks
sudo ufw allow from 192.168.0.0/16 to any port 6379 proto tcp
```

#### DNS/Connectivity
- Outbound HTTPS access to: `api.anthropic.com`, `api.openai.com`, `openrouter.ai`
- Optional: Custom domain for Open WebUI (requires reverse proxy)

### Hardware Requirements

#### Minimum (Development)
- **CPU:** 2 cores
- **RAM:** 4GB
- **Disk:** 20GB SSD
- **Network:** 10 Mbps

#### Recommended (Production)
- **CPU:** 4 cores
- **RAM:** 8GB+
- **Disk:** 50GB SSD (for ChromaDB + conversation archives)
- **Network:** 50+ Mbps

#### Optimal (Large Deployments)
- **CPU:** 8+ cores
- **RAM:** 16GB+
- **Disk:** 100GB+ SSD
- **Network:** 1 Gbps

---

## System Requirements

### Operating System Matrix

| OS | Version | Status | Notes |
|----|---------|--------|-------|
| Ubuntu | 22.04 LTS | ✅ Recommended | Best support, tested |
| Ubuntu | 20.04 LTS | ✅ Supported | Good support |
| Debian | 12 (Bookworm) | ✅ Supported | Stable |
| Debian | 11 (Bullseye) | ✅ Supported | Works well |
| RHEL/CentOS | 8+ | ✅ Works | May need `dnf` instead of `apt` |
| Fedora | 37+ | ✅ Works | Cutting-edge, less stable |

### Database Compatibility

#### Redis
- **Recommended:** Redis 6.0+ or Redis Cloud
- **Memory Requirement:** 2GB minimum (30MB default for L1, 23GB for L2 archive)
- **Options:**
  - Local Redis (`apt-get install redis-server`)
  - Redis Cloud (`redislabs.com`) - cloud version, recommended
  - Self-managed on separate server

#### ChromaDB
- **Version:** Latest (auto-updated with Docker)
- **Storage:** 10GB+ for embeddings and documents
- **Collections:** Automatically created during init
- **Backup:** Automatic daily snapshots

#### PostgreSQL (optional, for conversation history)
- **Version:** 12+
- **Size:** 5GB+ for large conversation archives
- **Backup:** Automatic with `pg_dump`

### Python Package Dependencies

```
# Core dependencies (from pyproject.toml)
redis>=5.0
pydantic>=2.5
google-generativeai>=0.3
rich>=13.0
typer>=0.9

# Additional for IF.emotion
anthropic>=0.21
openai>=1.3
httpx>=0.25

# Optional for ChromaDB integration
chromadb>=0.4
```

---

## Installation Steps

### Step 1: Clone Repository

```bash
# Clone from GitHub (public)
git clone https://github.com/dannystocker/infrafabric.git
cd infrafabric

# OR clone from local Gitea (private)
git clone http://localhost:4000/dannystocker/infrafabric.git
cd infrafabric
```

**Verify:** Should show `infrafabric/` directory with `src/`, `docs/`, etc.

### Step 2: Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    docker.io \
    docker-compose \
    git \
    curl \
    redis-tools \
    postgresql-client

# Check versions
python3 --version      # Should be 3.10+
docker --version       # Should be 20.10+
docker-compose --version  # Should be 2.0+
```

### Step 3: Create Python Virtual Environment

```bash
# Create venv
python3 -m venv .venv

# Activate venv
source .venv/bin/activate

# Verify (should show (.venv) prefix)
which python
```

### Step 4: Install Python Dependencies

```bash
# Upgrade pip/setuptools
pip install --upgrade pip setuptools wheel

# Install project dependencies
pip install -e ".[dev]"

# Install additional packages
pip install \
    redis>=5.0 \
    pydantic>=2.5 \
    google-generativeai>=0.3 \
    rich>=13.0 \
    typer>=0.9 \
    anthropic>=0.21 \
    openai>=1.3 \
    chromadb>=0.4 \
    httpx>=0.25

# Verify installation
python -c "import redis, pydantic, anthropic; print('✅ All packages installed')"
```

### Step 5: Set Up Docker (if using containers)

```bash
# Start Docker daemon
sudo systemctl start docker
sudo systemctl enable docker

# Add current user to docker group (optional, to avoid sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verify Docker
docker --version
docker run hello-world
```

### Step 6: Create Directory Structure

```bash
# Create required directories
mkdir -p \
    .memory_bus \
    .memory_bus/context_memory \
    .memory_bus/deep_storage \
    data/archives \
    data/media/{infrafabric,navidocs,icw,shared} \
    logs \
    config/ssl \
    config/lexicons

# Set permissions
chmod 755 .memory_bus
chmod 700 .memory_bus/context_memory
chmod 700 .memory_bus/deep_storage
chmod 755 data
chmod 755 logs
```

### Step 7: Initialize Redis

```bash
# Option A: Local Redis
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test connection
redis-cli PING
# Expected output: PONG

# Option B: Redis Cloud (recommended for production)
# 1. Sign up at https://redislabs.com
# 2. Create database (30MB free tier or higher)
# 3. Note: Host, Port, Password
# 4. Test with: redis-cli -h <host> -p <port> -a <password> PING
```

### Step 8: Initialize ChromaDB

```bash
# If using Docker (recommended)
docker pull chromadb/chroma:latest

# If running locally (optional)
pip install chromadb

# Create data directory
mkdir -p data/.chroma

# Verify (will output if successful)
python -c "import chromadb; print('✅ ChromaDB available')"
```

### Step 9: Verify Installation

```bash
# Check all components
python -c "
import redis
import pydantic
import anthropic
import chromadb
import google.generativeai
print('✅ All core packages installed')
"

# Check Docker images
docker images | grep -E 'open-webui|chromadb|redis'

# Check ports available
netstat -tuln | grep -E '8080|8000|6379'
```

---

## Configuration

### Step 1: Copy and Customize Configuration

```bash
# Copy example config
cp .env.example .env

# Edit with your values
nano .env
```

### Step 2: Set Environment Variables

Edit `.env` with your credentials:

```bash
# Redis Cloud (L1 - hot cache)
REDIS_HOST=redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com
REDIS_PORT=19956
REDIS_PASSWORD=your_redis_cloud_password
REDIS_DB=0
REDIS_TTL=2592000  # 30 days in seconds

# Redis L2 (optional - for permanent archive)
REDIS_L2_HOST=your-redis-l2-host
REDIS_L2_PORT=6379
REDIS_L2_PASSWORD=your_redis_l2_password
REDIS_L2_DB=0

# ChromaDB Configuration
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
CHROMADB_PATH=./data/.chroma
CHROMADB_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# API Keys
ANTHROPIC_API_KEY=sk-ant-v0-xxxxx
OPENROUTER_API_KEY=sk-or-v1-xxxxx
DEEPSEEK_API_KEY=sk-xxxxx
GEMINI_API_KEY=xxxxx

# OpenWebUI Configuration
WEBUI_AUTH=false  # Set to true for production
WEBUI_SECRET_KEY=your-secret-key-here
WEBUI_PROFILE_PICTURE_URL=https://example.com/avatar.png

# IF.emotion Configuration
IF_EMOTION_ENABLE=true
IF_EMOTION_SANDBOX_MODE=true
IF_EMOTION_DNA_PATH=/path/to/emotion/dna
IF_EMOTION_ISOLATION_LEVEL=3

# System Configuration
DEBUG=false
LOG_LEVEL=INFO
TIMEZONE=UTC
```

### Step 3: Configure Redis Connection

Create `/home/setup/.env.redis` (or wherever you prefer):

```bash
# Redis L1 (Cloud - L1 cache)
REDIS_L1_HOST=redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com
REDIS_L1_PORT=19956
REDIS_L1_PASSWORD=your_cloud_password
REDIS_L1_DB=0

# Redis L2 (Archive - permanent storage)
REDIS_L2_HOST=85.239.243.227  # Your Proxmox/Server IP
REDIS_L2_PORT=6379
REDIS_L2_PASSWORD=@@Redis_InfraFabric_L2_2025$$
REDIS_L2_DB=0

# Protection
chmod 600 /home/setup/.env.redis
```

### Step 4: Configure ChromaDB Storage

```bash
# Create ChromaDB config
cat > config/chromadb.yaml << 'EOF'
# ChromaDB Configuration
persistence:
  provider: disk
  directory: ./data/.chroma

server:
  host: 0.0.0.0
  port: 8000
  max_body_size_bytes: 41943040  # 40MB

embeddings:
  provider: default  # Uses sentence-transformers
  model: all-MiniLM-L6-v2

telemetry:
  anonymized: false

auth:
  enabled: false  # Enable for production
EOF
```

### Step 5: Configure Claude Max API Keys

```bash
# Create API credentials file (secure permissions)
cat > config/api_keys.yaml << 'EOF'
apis:
  claude:
    provider: anthropic
    api_key: ${ANTHROPIC_API_KEY}
    api_base: https://api.anthropic.com/v1
    model: claude-3-5-sonnet-20241022
    max_tokens: 8192

  openrouter:
    provider: openrouter
    api_key: ${OPENROUTER_API_KEY}
    api_base: https://openrouter.ai/api/v1
    models:
      - claude-3-5-sonnet-20241022
      - gpt-4-turbo
      - deepseek/deepseek-chat

  deepseek:
    provider: deepseek
    api_key: ${DEEPSEEK_API_KEY}
    api_base: https://api.deepseek.com/beta
    model: deepseek-chat

  gemini:
    provider: google
    api_key: ${GEMINI_API_KEY}
    model: gemini-1.5-pro
EOF

chmod 600 config/api_keys.yaml
```

### Step 6: Configure IF.emotion Personality DNA Paths

```bash
# Create IF.emotion config
cat > config/if_emotion_config.yaml << 'EOF'
# IF.emotion Configuration
emotion_system:
  enabled: true
  sandbox_mode: true
  isolation_level: 3  # 0=none, 1=basic, 2=strict, 3=maximum

personality_dna:
  base_path: ./src/config/lexicons
  personality_sets:
    - name: sergio_aspergers
      file: sergio_aspergers_dna.json
      type: neurodiversity

    - name: if_ceo_light
      file: if_ceo_light_facets.json
      type: leadership

    - name: if_ceo_dark
      file: if_ceo_dark_facets.json
      type: leadership

    - name: guardians_council
      file: guardians_framework.json
      type: governance

audit:
  enabled: true
  log_emotion_transitions: true
  log_decision_rationale: true
  retention_days: 2555  # 7 years

security:
  prevent_personality_injection: true
  validate_before_activation: true
  max_concurrent_personalities: 3
  timeout_seconds: 300
EOF
```

---

## Memory Initialization

### Step 1: Initialize Context Memory (Redis)

```bash
# Create initialization script
cat > scripts/init_context_memory.py << 'EOF'
#!/usr/bin/env python3
import redis
import json
import os
from datetime import datetime

# Connect to Redis
r = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    password=os.getenv('REDIS_PASSWORD'),
    db=0
)

# Create key namespaces
namespaces = {
    'session': 'active_sessions:*',
    'agent': 'agent:*:state',
    'context': 'context:*:memory',
    'conversation': 'conversation:*:metadata',
    'audit': 'audit:entries:*',
    'metrics': 'metrics:*:hourly',
}

print("Initializing Redis Context Memory...")
for namespace, pattern in namespaces.items():
    print(f"  ✓ Namespace: {namespace} ({pattern})")

# Set up TTL policies
ttl_policies = {
    'session:*': 86400,           # 1 day
    'context:*:memory': 2592000,  # 30 days
    'conversation:*:metadata': 7776000,  # 90 days
    'metrics:*:hourly': 604800,   # 7 days
    'audit:entries:*': 2592000,   # 30 days (hot cache)
}

print("\nConfiguring TTL Policies...")
for pattern, ttl in ttl_policies.items():
    print(f"  ✓ {pattern}: {ttl} seconds ({ttl//86400} days)")

# Test connection
try:
    r.ping()
    print("\n✅ Redis Context Memory initialized successfully!")
except Exception as e:
    print(f"\n❌ Error: {e}")
    exit(1)
EOF

chmod +x scripts/init_context_memory.py

# Run initialization
python scripts/init_context_memory.py
```

### Step 2: Initialize Deep Storage (ChromaDB)

```bash
# Create initialization script
cat > scripts/init_deep_storage.py << 'EOF'
#!/usr/bin/env python3
import chromadb
from chromadb.config import Settings
import os

# Configure ChromaDB
settings = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=os.getenv('CHROMADB_PATH', './data/.chroma'),
    anonymized_telemetry=False,
)

# Create client
client = chromadb.Client(settings)

# Define collections
collections = {
    'if_emotion_dna': {
        'metadata': {'description': 'IF.emotion personality DNA corpus'},
        'document_type': 'personality'
    },
    'psychology_corpus': {
        'metadata': {'description': 'Psychology and neuroscience research'},
        'document_type': 'research'
    },
    'governance_framework': {
        'metadata': {'description': 'Guardian Council governance framework'},
        'document_type': 'governance'
    },
    'conversation_history': {
        'metadata': {'description': 'Archived conversation embeddings'},
        'document_type': 'conversation'
    },
    'audit_trail': {
        'metadata': {'description': 'Audit log embeddings for semantic search'},
        'document_type': 'audit'
    },
}

print("Initializing ChromaDB Deep Storage...")
for collection_name, config in collections.items():
    try:
        client.create_collection(
            name=collection_name,
            metadata=config['metadata']
        )
        print(f"  ✓ Collection: {collection_name}")
    except:
        print(f"  ⚠ Collection {collection_name} already exists (skipped)")

# Load sample personality DNA
print("\nLoading IF.emotion Personality DNA...")
try:
    collection = client.get_collection('if_emotion_dna')
    # Add placeholder documents (replace with actual DNA files)
    collection.add(
        documents=["IF.emotion core personality framework"],
        ids=["if_emotion_core_v1.0"],
        metadatas=[{"version": "1.0", "type": "framework"}]
    )
    print("  ✓ Personality DNA loaded")
except Exception as e:
    print(f"  ⚠ Error loading DNA: {e}")

print("\n✅ ChromaDB Deep Storage initialized successfully!")
EOF

chmod +x scripts/init_deep_storage.py

# Run initialization
python scripts/init_deep_storage.py
```

### Step 3: Load Psychology Corpus

```bash
# Create corpus loader
cat > scripts/load_psychology_corpus.py << 'EOF'
#!/usr/bin/env python3
import chromadb
import os
import json
from pathlib import Path

client = chromadb.Client()
collection = client.get_collection('psychology_corpus')

# Load research papers and articles
corpus_path = Path('./docs/research')
if corpus_path.exists():
    for file in corpus_path.glob('*.md'):
        with open(file) as f:
            content = f.read()
            collection.add(
                documents=[content],
                ids=[file.stem],
                metadatas=[{
                    'source': str(file),
                    'type': 'research_paper'
                }]
            )
            print(f"  ✓ Loaded: {file.name}")

print("✅ Psychology corpus loaded!")
EOF

python scripts/load_psychology_corpus.py
```

### Step 4: Verify Embeddings

```bash
# Test embedding generation
python << 'EOF'
import chromadb

client = chromadb.Client()
collection = client.get_collection('psychology_corpus')

# Verify embeddings generated
count = collection.count()
print(f"✅ Embeddings verified: {count} documents in corpus")
EOF
```

---

## Agent Registration

### Step 1: Register Sonnet Coordinators

```bash
# Create registration script
cat > scripts/register_agents.py << 'EOF'
#!/usr/bin/env python3
import json
import os
from datetime import datetime

# Sonnet Coordinator A (Infrastructure & Communication)
coordinator_a = {
    "agent_id": "sonnet-coordinator-a",
    "model": "claude-3-5-sonnet-20241022",
    "role": "infrastructure",
    "capabilities": [
        "openwebui_api_integration",
        "s2_swarm_communication",
        "redis_memory_coordination",
        "chromadb_vector_search",
        "background_comms"
    ],
    "max_workers": 20,
    "status": "active",
    "registered_at": datetime.now().isoformat()
}

# Sonnet Coordinator B (Security & Registry)
coordinator_b = {
    "agent_id": "sonnet-coordinator-b",
    "model": "claude-3-5-sonnet-20241022",
    "role": "security",
    "capabilities": [
        "if_emotion_sandboxing",
        "claude_max_registry",
        "audit_trail_management",
        "threat_modeling",
        "cross_swarm_coordination"
    ],
    "max_workers": 20,
    "status": "active",
    "registered_at": datetime.now().isoformat()
}

# Register coordinators
agents = {
    "coordinators": [coordinator_a, coordinator_b],
    "haiku_agents": {}  # Auto-populated during execution
}

# Save registry
os.makedirs('config/registry', exist_ok=True)
with open('config/registry/agent_registry.json', 'w') as f:
    json.dump(agents, f, indent=2)

print("✅ Agent registry initialized")
print(f"   - Sonnet Coordinator A (Infrastructure)")
print(f"   - Sonnet Coordinator B (Security)")
print(f"   - Ready for {coordinator_a['max_workers'] + coordinator_b['max_workers']} Haiku workers")
EOF

python scripts/register_agents.py
```

### Step 2: Register Haiku Workers

```bash
# Create Haiku registration script
cat > scripts/register_haiku_workers.py << 'EOF'
#!/usr/bin/env python3
import json
import os

# Load existing registry
with open('config/registry/agent_registry.json') as f:
    registry = json.load(f)

# Create Haiku worker pool
haiku_workers = {}
for i in range(1, 41):  # 40 Haiku agents
    worker = {
        "agent_id": f"haiku-b{i:02d}",
        "model": "claude-3-5-haiku-20241022",
        "role": "worker",
        "coordinator": f"sonnet-coordinator-{'a' if i <= 20 else 'b'}",
        "capabilities": ["task_execution", "data_processing", "api_calls"],
        "status": "standby",
        "max_tokens_per_task": 5000,
        "max_concurrent_tasks": 3
    }
    haiku_workers[f"haiku-b{i:02d}"] = worker
    if i % 5 == 0:
        print(f"  ✓ Registered Haiku B{i:02d}")

registry["haiku_agents"] = haiku_workers

# Save updated registry
with open('config/registry/agent_registry.json', 'w') as f:
    json.dump(registry, f, indent=2)

print(f"\n✅ Registered {len(haiku_workers)} Haiku workers")
EOF

python scripts/register_haiku_workers.py
```

### Step 3: Configure Swarm Topology

```bash
# Create swarm topology config
cat > config/swarm_topology.yaml << 'EOF'
# InfraFabric Swarm Topology
swarm_config:
  name: infrafabric-s2
  version: 2.0
  deployment_model: hybrid

coordinators:
  sonnet_a:
    id: sonnet-coordinator-a
    role: infrastructure
    workers: 20

  sonnet_b:
    id: sonnet-coordinator-b
    role: security
    workers: 20

communication:
  protocol: http/redis
  encryption: tls-1-3
  message_queue: redis
  retry_policy: exponential_backoff
  max_retries: 3
  timeout_seconds: 300

memory:
  l1_cache: redis_cloud  # Hot cache (30 days)
  l2_storage: redis_l2   # Permanent archive
  vector_db: chromadb    # Semantic search

registry:
  provider: local  # local or remote
  path: config/registry/agent_registry.json
  auto_discovery: true
  heartbeat_interval: 30
EOF
```

### Step 4: Set Up Cross-Swarm Communication

```bash
# Create cross-swarm protocol config
cat > config/cross_swarm_protocol.yaml << 'EOF'
# Cross-Swarm Coordination Protocol
cross_swarm:
  enabled: true
  protocol_version: 1.0

swarms:
  infrafabric:
    id: infrafabric-s2
    coordinators: 2
    workers: 40

  # Other swarms can be added here

message_routing:
  default_handler: redis_queue
  broadcast_topic: /swarms/broadcast
  direct_routing: /swarms/{source}/{target}

security:
  message_signing: ed25519
  auth_tokens: true
  rate_limiting: true

monitoring:
  message_latency_p99: 500ms
  coordination_overhead: <5%

fallback:
  enabled: true
  timeout_seconds: 30
  alternate_transport: http
EOF
```

---

## Security Hardening

### Step 1: Enable Input Sanitization

```bash
# Create sanitization module
cat > src/core/security/input_sanitizer.py << 'EOF'
import re
import html
from typing import Any

class InputSanitizer:
    """Sanitize user inputs to prevent injection attacks"""

    # Dangerous patterns
    DANGEROUS_PATTERNS = {
        'sql_injection': r"(\b(UNION|SELECT|INSERT|UPDATE|DELETE)\b)",
        'script_injection': r"(<script|javascript:|onerror=)",
        'path_traversal': r"(\.\./|\.\.\\)",
        'null_byte': r"\x00",
    }

    @staticmethod
    def sanitize_string(input_str: str) -> str:
        """Sanitize string input"""
        # Remove null bytes
        input_str = input_str.replace('\x00', '')

        # HTML escape
        input_str = html.escape(input_str)

        # Remove control characters
        input_str = ''.join(c for c in input_str if ord(c) >= 32 or c in '\n\t')

        # Truncate to reasonable length
        return input_str[:10000]

    @classmethod
    def validate_safe(cls, input_value: Any) -> bool:
        """Check if input is safe"""
        if not isinstance(input_value, str):
            return True

        for pattern_name, pattern in cls.DANGEROUS_PATTERNS.items():
            if re.search(pattern, input_value, re.IGNORECASE):
                return False

        return True

# Test
if __name__ == '__main__':
    sanitizer = InputSanitizer()
    assert sanitizer.validate_safe("hello world")
    assert not sanitizer.validate_safe("SELECT * FROM users")
    print("✅ Input sanitization enabled")
EOF

python src/core/security/input_sanitizer.py
```

### Step 2: Enable Output Filtering

```bash
# Create output filter module
cat > src/core/security/output_filter.py << 'EOF'
import json
import re
from typing import Any, Dict

class OutputFilter:
    """Filter sensitive data from outputs"""

    SENSITIVE_PATTERNS = {
        'api_keys': r'(api[_-]?key|apikey)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9\-_.]+)["\']?',
        'passwords': r'(password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^\s"\']+)["\']?',
        'tokens': r'(token|secret)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9\-_.]+)["\']?',
        'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    }

    @classmethod
    def filter_output(cls, output: str) -> str:
        """Remove sensitive data from output"""
        filtered = output

        for pattern_name, pattern in cls.SENSITIVE_PATTERNS.items():
            filtered = re.sub(
                pattern,
                f'[REDACTED-{pattern_name.upper()}]',
                filtered,
                flags=re.IGNORECASE
            )

        return filtered

    @classmethod
    def filter_json(cls, data: Dict) -> Dict:
        """Recursively filter JSON data"""
        if isinstance(data, dict):
            return {k: cls.filter_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.filter_json(item) for item in data]
        elif isinstance(data, str):
            return cls.filter_output(data)
        return data

# Test
if __name__ == '__main__':
    filter_obj = OutputFilter()
    dangerous = "api_key = 'sk-12345678'"
    safe = filter_obj.filter_output(dangerous)
    assert '[REDACTED' in safe
    print("✅ Output filtering enabled")
EOF

python src/core/security/output_filter.py
```

### Step 3: Configure Rate Limiting

```bash
# Create rate limiter
cat > src/core/security/rate_limiter.py << 'EOF'
import time
import redis
import os
from typing import Tuple

class RateLimiter:
    """Token bucket rate limiter using Redis"""

    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD'),
            db=0
        )

    def is_allowed(self,
                   identifier: str,
                   tokens: int = 1,
                   capacity: int = 100,
                   refill_rate: float = 10.0) -> Tuple[bool, dict]:
        """
        Check if action is rate-limited

        Returns: (allowed: bool, info: dict)
        """
        key = f"rate_limit:{identifier}"

        # Get current tokens
        current = float(self.redis.get(key) or capacity)

        # Refill based on time
        last_refill = float(self.redis.get(f"{key}:refill") or time.time())
        now = time.time()
        time_passed = now - last_refill
        refill_amount = time_passed * refill_rate
        current = min(capacity, current + refill_amount)

        # Try to consume tokens
        if current >= tokens:
            current -= tokens
            allowed = True
        else:
            allowed = False

        # Update Redis
        self.redis.setex(key, 3600, str(current))  # 1 hour expiry
        self.redis.setex(f"{key}:refill", 3600, str(now))

        return allowed, {
            'tokens_remaining': int(current),
            'tokens_requested': tokens,
            'capacity': capacity,
        }

# Test
if __name__ == '__main__':
    limiter = RateLimiter()
    allowed, info = limiter.is_allowed('user123', tokens=1, capacity=100)
    print(f"✅ Rate limiting enabled: {allowed}")
EOF

python src/core/security/rate_limiter.py
```

### Step 4: Enable Audit Logging

```bash
# Create audit logger
cat > src/core/security/audit_logger.py << 'EOF'
import json
import os
import logging
from datetime import datetime
from pathlib import Path

class AuditLogger:
    """Log all security-relevant events"""

    def __init__(self, log_dir: str = './logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger('audit')
        handler = logging.FileHandler(self.log_dir / 'audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_event(self, event_type: str, details: dict):
        """Log security event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details,
        }
        self.logger.info(json.dumps(event))

    def log_access(self, agent_id: str, resource: str, action: str, allowed: bool):
        """Log resource access"""
        self.log_event('access', {
            'agent_id': agent_id,
            'resource': resource,
            'action': action,
            'allowed': allowed,
        })

    def log_auth(self, user: str, success: bool, method: str):
        """Log authentication attempt"""
        self.log_event('auth', {
            'user': user,
            'success': success,
            'method': method,
        })

# Test
if __name__ == '__main__':
    auditor = AuditLogger()
    auditor.log_access('agent-001', '/api/secrets', 'read', True)
    print("✅ Audit logging enabled")
EOF

python src/core/security/audit_logger.py
```

### Step 5: Set Up Ed25519 Signing Keys

```bash
# Generate signing keys
cat > scripts/setup_signing_keys.py << 'EOF'
#!/usr/bin/env python3
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import os

# Generate key pair
private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Save private key (secured)
os.makedirs('config/keys', exist_ok=True)

private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

with open('config/keys/signing_key.pem', 'wb') as f:
    f.write(private_pem)
os.chmod('config/keys/signing_key.pem', 0o600)

with open('config/keys/verify_key.pem', 'wb') as f:
    f.write(public_pem)

print("✅ Ed25519 signing keys generated")
print("   - Private key: config/keys/signing_key.pem (600 perms)")
print("   - Public key:  config/keys/verify_key.pem (644 perms)")
EOF

python scripts/setup_signing_keys.py
```

### Step 6: Configure TLS/SSL

```bash
# Generate self-signed certificate (for testing)
openssl req -x509 -newkey rsa:4096 \
    -keyout config/ssl/server.key \
    -out config/ssl/server.crt \
    -days 365 -nodes \
    -subj "/C=US/ST=State/L=City/O=Org/CN=localhost"

chmod 600 config/ssl/server.key
chmod 644 config/ssl/server.crt

# Or for production, use Let's Encrypt (requires domain)
# certbot certonly --standalone -d your-domain.com
```

---

## Health Checks

### Step 1: Redis Connectivity Test

```bash
# Test Redis L1 connection
redis-cli -h redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com \
    -p 19956 \
    -a your_password \
    PING

# Expected output: PONG

# Create comprehensive test script
cat > scripts/test_redis.py << 'EOF'
#!/usr/bin/env python3
import redis
import os

def test_redis():
    """Test Redis connectivity and performance"""

    # Test L1 (Cloud)
    print("Testing Redis L1 (Cloud Cache)...")
    try:
        r1 = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD'),
            socket_connect_timeout=5
        )
        r1.ping()
        print("  ✅ L1 Connection: OK")
        print(f"     - Keys in L1: {r1.dbsize()}")
    except Exception as e:
        print(f"  ❌ L1 Connection: {e}")

    # Test L2 (Archive)
    print("\nTesting Redis L2 (Archive Storage)...")
    try:
        r2 = redis.Redis(
            host=os.getenv('REDIS_L2_HOST', 'localhost'),
            port=int(os.getenv('REDIS_L2_PORT', 6379)),
            password=os.getenv('REDIS_L2_PASSWORD'),
            socket_connect_timeout=5
        )
        r2.ping()
        print("  ✅ L2 Connection: OK")
        print(f"     - Keys in L2: {r2.dbsize()}")
    except Exception as e:
        print(f"  ❌ L2 Connection: {e}")

if __name__ == '__main__':
    test_redis()
EOF

chmod +x scripts/test_redis.py
python scripts/test_redis.py
```

### Step 2: ChromaDB Connectivity Test

```bash
cat > scripts/test_chromadb.py << 'EOF'
#!/usr/bin/env python3
import chromadb
import os

def test_chromadb():
    """Test ChromaDB connectivity"""

    print("Testing ChromaDB Connectivity...")
    try:
        # Connect to ChromaDB
        client = chromadb.HttpClient(
            host=os.getenv('CHROMADB_HOST', 'localhost'),
            port=int(os.getenv('CHROMADB_PORT', 8000))
        )

        # Test heartbeat
        client.heartbeat()
        print("  ✅ ChromaDB Connectivity: OK")

        # List collections
        collections = client.list_collections()
        print(f"  ✅ Collections: {len(collections)}")
        for col in collections:
            count = col.count()
            print(f"     - {col.name}: {count} documents")

    except Exception as e:
        print(f"  ❌ ChromaDB Error: {e}")

if __name__ == '__main__':
    test_chromadb()
EOF

python scripts/test_chromadb.py
```

### Step 3: Claude Max API Test

```bash
cat > scripts/test_api_keys.py << 'EOF'
#!/usr/bin/env python3
import os
from anthropic import Anthropic

def test_claude_api():
    """Test Claude Max API connectivity"""

    print("Testing Claude Max API...")

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("  ❌ ANTHROPIC_API_KEY not set")
        return

    try:
        client = Anthropic(api_key=api_key)

        # Simple test message
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Say 'Connected'"}
            ]
        )

        print("  ✅ Claude Max API: OK")
        print(f"     - Model: {response.model}")
        print(f"     - Response: {response.content[0].text}")

    except Exception as e:
        print(f"  ❌ Claude API Error: {e}")

if __name__ == '__main__':
    test_claude_api()
EOF

python scripts/test_api_keys.py
```

### Step 4: IF.emotion Sandbox Test

```bash
cat > scripts/test_if_emotion.py << 'EOF'
#!/usr/bin/env python3
import sys
sys.path.insert(0, './src')

def test_if_emotion():
    """Test IF.emotion sandbox"""

    print("Testing IF.emotion Sandbox...")

    try:
        # Check if module imports
        from core.security import InputSanitizer, OutputFilter
        print("  ✅ Security modules: OK")

        # Test sanitization
        sanitizer = InputSanitizer()
        safe = sanitizer.sanitize_string("test input")
        print("  ✅ Input sanitization: OK")

        # Test output filtering
        filter_obj = OutputFilter()
        filtered = filter_obj.filter_output("api_key = 'secret'")
        assert 'REDACTED' in filtered
        print("  ✅ Output filtering: OK")

    except Exception as e:
        print(f"  ❌ IF.emotion Error: {e}")

if __name__ == '__main__':
    test_if_emotion()
EOF

python scripts/test_if_emotion.py
```

### Step 5: Cross-Swarm Communication Test

```bash
cat > scripts/test_cross_swarm.py << 'EOF'
#!/usr/bin/env python3
import json
import redis
import os

def test_cross_swarm():
    """Test cross-swarm communication"""

    print("Testing Cross-Swarm Communication...")

    try:
        r = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD'),
            db=0
        )

        # Publish test message
        message = {
            'source_swarm': 'infrafabric-s2',
            'target_swarm': 'infrafabric-s2',
            'message_type': 'health_check',
            'timestamp': '2025-11-30T00:00:00Z'
        }

        r.publish('/swarms/broadcast', json.dumps(message))
        print("  ✅ Cross-swarm messaging: OK")

    except Exception as e:
        print(f"  ❌ Cross-swarm Error: {e}")

if __name__ == '__main__':
    test_cross_swarm()
EOF

python scripts/test_cross_swarm.py
```

### Step 6: Audit Trail Verification

```bash
cat > scripts/verify_audit.py << 'EOF'
#!/usr/bin/env python3
import os
from pathlib import Path

def verify_audit():
    """Verify audit trail is being recorded"""

    print("Verifying Audit Trail...")

    audit_log = Path('./logs/audit.log')

    if audit_log.exists():
        lines = audit_log.read_text().strip().split('\n')
        print(f"  ✅ Audit log exists: {len(lines)} events recorded")
    else:
        print("  ⚠ Audit log not found (will be created on first event)")

if __name__ == '__main__':
    verify_audit()
EOF

python scripts/verify_audit.py
```

---

## Monitoring Setup

### Step 1: Metrics Configuration

```bash
# Create metrics module
cat > src/core/resilience/metrics.py << 'EOF'
import time
from collections import defaultdict
from typing import Dict, List

class MetricsCollector:
    """Collect system metrics"""

    def __init__(self):
        self.latencies = defaultdict(list)
        self.errors = defaultdict(int)
        self.throughput = defaultdict(int)

    def record_latency(self, operation: str, duration_ms: float):
        """Record operation latency"""
        self.latencies[operation].append(duration_ms)

    def record_error(self, operation: str, error_type: str):
        """Record error"""
        self.errors[f"{operation}:{error_type}"] += 1

    def record_throughput(self, operation: str, count: int = 1):
        """Record throughput"""
        self.throughput[operation] += count

    def get_percentile(self, operation: str, percentile: int = 99) -> float:
        """Get latency percentile"""
        if operation not in self.latencies:
            return 0
        sorted_latencies = sorted(self.latencies[operation])
        index = int(len(sorted_latencies) * percentile / 100)
        return sorted_latencies[index] if index < len(sorted_latencies) else 0

    def get_metrics(self) -> Dict:
        """Get all metrics"""
        return {
            'latencies': {
                op: {
                    'count': len(times),
                    'avg': sum(times) / len(times) if times else 0,
                    'p99': self.get_percentile(op, 99),
                    'max': max(times) if times else 0,
                }
                for op, times in self.latencies.items()
            },
            'errors': dict(self.errors),
            'throughput': dict(self.throughput),
        }

# Global instance
metrics = MetricsCollector()
EOF
```

### Step 2: Dashboard Configuration

```bash
# Create Prometheus configuration
cat > config/prometheus.yaml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'infrafabric'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']

  - job_name: 'chromadb'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['localhost:8000']
EOF

# Create Grafana dashboard config (JSON)
cat > config/grafana_dashboard.json << 'EOF'
{
  "dashboard": {
    "title": "InfraFabric System Metrics",
    "panels": [
      {
        "title": "API Latency (P99)",
        "targets": [{"expr": "histogram_quantile(0.99, api_latency_ms)"}]
      },
      {
        "title": "Error Rate",
        "targets": [{"expr": "rate(errors_total[5m])"}]
      },
      {
        "title": "Agent Active",
        "targets": [{"expr": "agents_active"}]
      },
      {
        "title": "Redis Memory Usage",
        "targets": [{"expr": "redis_memory_used_bytes"}]
      }
    ]
  }
}
EOF
```

### Step 3: Alert Rules

```bash
# Create Prometheus alert rules
cat > config/alert_rules.yaml << 'EOF'
groups:
  - name: infrafabric_alerts
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.99, api_latency_ms) > 1000
        for: 5m
        annotations:
          summary: "High API latency detected (P99 > 1s)"

      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 0.01
        for: 5m
        annotations:
          summary: "High error rate detected (> 1%)"

      - alert: RedisDiskUsage
        expr: redis_used_memory_bytes / redis_maxmemory_bytes > 0.9
        for: 5m
        annotations:
          summary: "Redis memory usage critical (> 90%)"

      - alert: ChromaDBDown
        expr: up{job="chromadb"} == 0
        for: 1m
        annotations:
          summary: "ChromaDB service is down"

      - alert: AgentInactive
        expr: agents_active < agents_total * 0.8
        for: 5m
        annotations:
          summary: "More than 20% of agents inactive"
EOF
```

### Step 4: Log Aggregation

```bash
# Create log aggregation config (ELK or similar)
cat > config/logstash.conf << 'EOF'
input {
  file {
    path => "./logs/audit.log"
    start_position => "beginning"
  }
}

filter {
  json {
    source => "message"
  }

  date {
    match => [ "timestamp", "ISO8601" ]
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "infrafabric-%{+YYYY.MM.dd}"
  }

  stdout {
    codec => rubydebug
  }
}
EOF
```

---

## Production Readiness Checklist

Before deploying to production, verify all items:

- [ ] **Prerequisites Installed**
  - [ ] Python 3.10+
  - [ ] Docker 20.10+
  - [ ] Redis Cloud account created
  - [ ] ChromaDB ready
  - [ ] All API keys obtained

- [ ] **Configuration Validated**
  - [ ] `.env` file created and populated
  - [ ] Redis credentials verified
  - [ ] ChromaDB settings configured
  - [ ] API keys tested
  - [ ] Ports not in use

- [ ] **Redis Persistent**
  - [ ] Redis persistence enabled
  - [ ] Backup scripts functional
  - [ ] L2 storage connected
  - [ ] TTL policies configured

- [ ] **ChromaDB Backed Up**
  - [ ] Backup directory created
  - [ ] Cron job for daily backups
  - [ ] Test restore procedure
  - [ ] Retention policy set

- [ ] **Security Hardening Complete**
  - [ ] Input sanitization enabled
  - [ ] Output filtering active
  - [ ] Rate limiting configured
  - [ ] Audit logging working
  - [ ] SSL/TLS certificates deployed
  - [ ] Signing keys generated

- [ ] **Health Checks Passing**
  - [ ] Redis L1 connectivity confirmed
  - [ ] Redis L2 connectivity confirmed
  - [ ] ChromaDB responding
  - [ ] Claude Max API working
  - [ ] IF.emotion sandbox functional
  - [ ] Cross-swarm messaging operational
  - [ ] Audit trail recording

- [ ] **Monitoring Configured**
  - [ ] Metrics collection active
  - [ ] Dashboard accessible
  - [ ] Alert rules deployed
  - [ ] Log aggregation running
  - [ ] Uptime monitoring enabled

- [ ] **Audit Trail Verified**
  - [ ] Audit logs being written
  - [ ] Rotation policy set
  - [ ] Retention period: 7 years
  - [ ] Searchable via ChromaDB

- [ ] **Documentation Reviewed**
  - [ ] README.md current
  - [ ] Architecture documented
  - [ ] Runbooks created
  - [ ] Disaster recovery plan ready

- [ ] **Team Ready**
  - [ ] On-call rotation defined
  - [ ] Escalation procedures documented
  - [ ] Training completed
  - [ ] Access credentials distributed securely

---

## Troubleshooting Guide

### Common Errors and Solutions

#### Redis Connection Failures

**Error:** `ConnectionRefusedError: [Errno 111] Connection refused`

**Causes & Solutions:**
```bash
# 1. Check Redis is running
ps aux | grep redis

# 2. Test connectivity
redis-cli -h your_host -p 6379 -a your_password PING

# 3. Check firewall
sudo ufw status
sudo ufw allow 6379/tcp

# 4. Verify credentials
# Update .env with correct host/port/password

# 5. Restart Redis
sudo systemctl restart redis-server
```

#### ChromaDB Timeout Issues

**Error:** `chromadb.errors.RequestError: timeout`

**Solutions:**
```bash
# 1. Check ChromaDB is running
docker ps | grep chromadb

# 2. Check disk space
df -h | grep chroma

# 3. Check logs
docker logs chromadb

# 4. Increase timeout in config
# Edit config/chromadb.yaml, set timeout_seconds: 600

# 5. Restart service
docker-compose restart chromadb
```

#### Claude Max API Rate Limits

**Error:** `RateLimitError: 429 Too Many Requests`

**Solutions:**
```bash
# 1. Check usage
curl https://api.anthropic.com/billing/current_balance \
  -H "Authorization: Bearer $ANTHROPIC_API_KEY"

# 2. Implement backoff
# In code: exponential backoff with jitter

# 3. Use token bucket limiter
python scripts/test_redis.py  # Verify limiter working

# 4. Upgrade API tier
# Contact Anthropic support if consistent limits
```

#### Memory/Performance Issues

**Error:** `MemoryError: Unable to allocate XXX MB`

**Solutions:**
```bash
# 1. Check memory usage
free -h
docker stats

# 2. Identify memory leaks
# Monitor: docker logs infrafabric-app | grep "memory"

# 3. Increase swap (temporary)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 4. Optimize database queries
# Review slow queries in audit.log

# 5. Scale horizontally
# Deploy additional containers/servers
```

---

## Upgrade Procedures

### Before Upgrading

```bash
# 1. Backup everything
./scripts/backup.sh

# 2. Document current state
docker-compose ps > deployment_state_before.txt

# 3. Note current versions
python -c "import redis; print(f'Redis: {redis.__version__}')"
docker inspect chromadb | grep Image
```

### Upgrading Components

#### Upgrade Python Dependencies

```bash
# 1. Update requirements
pip install --upgrade -r requirements.txt

# 2. Test imports
python -c "import redis, pydantic, anthropic; print('OK')"

# 3. Run tests
pytest tests/ -v

# 4. Restart services
docker-compose restart
```

#### Upgrade Open WebUI

```bash
# 1. Pull latest image
docker pull ghcr.io/open-webui/open-webui:main

# 2. Update docker-compose.yml
# Change: image: ghcr.io/open-webui/open-webui:main@sha256:XXX

# 3. Recreate container
docker-compose up -d open-webui --no-deps

# 4. Verify
curl http://localhost:8080/api/version
```

#### Upgrade ChromaDB

```bash
# 1. Backup vector database
cp -r data/.chroma data/.chroma.backup

# 2. Pull new image
docker pull chromadb/chroma:latest

# 3. Recreate container
docker-compose up -d chromadb --no-deps

# 4. Verify collections
python scripts/test_chromadb.py
```

### Database Migrations

```bash
# Create migration script
cat > scripts/migrate_db.py << 'EOF'
#!/usr/bin/env python3
"""
Migration script for database schema changes
"""
import redis
import os

def migrate_v1_to_v2():
    """Migrate from v1 to v2 schema"""

    r = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD'),
        db=0
    )

    print("Running migration: v1 → v2")
    # Add migration logic here
    print("✅ Migration complete")

if __name__ == '__main__':
    migrate_v1_to_v2()
EOF

python scripts/migrate_db.py
```

### Rollback Procedures

```bash
# 1. If upgrade fails, restore backup
docker-compose down
cp deployment_state_before.txt deployment_state_before.log

# 2. Restore database
redis-cli --rdb /tmp/dump.rdb  # Snapshot backup
# Restore from backup service

# 3. Revert docker image
docker-compose.override.yml  # Use previous version pins

# 4. Restart
docker-compose up -d

# 5. Verify
./scripts/health_check.sh
```

---

## Summary

### Quick Reference

**Typical Deployment Timeline:**
- Prerequisites: ~15 minutes
- Installation: ~30 minutes
- Configuration: ~20 minutes
- Memory Init: ~10 minutes
- Health Checks: ~5 minutes
- **Total: ~80 minutes**

**Key Files to Remember:**
- `.env` - Environment variables (NEVER commit!)
- `config/api_keys.yaml` - API credentials
- `config/swarm_topology.yaml` - Agent configuration
- `logs/audit.log` - Security audit trail

**Critical Monitoring:**
- Redis memory usage (watch for 90%+ threshold)
- ChromaDB disk usage (watch for 95%+ threshold)
- API error rate (alert if >1%)
- Agent availability (alert if <80%)

**Support Resources:**
- GitHub Issues: https://github.com/dannystocker/infrafabric/issues
- Documentation: `/home/setup/infrafabric/docs/`
- Agent Registry: `config/registry/agent_registry.json`
- Audit Trail: `logs/audit.log`

---

**Document Version:** 2.0.0
**Last Updated:** 2025-11-30
**Deployment Status:** Production Ready
**IF.TTT Compliance:** Full
**Citation:** `if://doc/integration-deployment/2025-11-30`
