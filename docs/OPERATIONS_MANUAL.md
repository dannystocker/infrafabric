# InfraFabric Operations Manual

**Citation:** `if://doc/operations-manual/2025-11-30`

**Version:** 1.0.0

**Date:** November 30, 2025

**Status:** Production Ready

**Target Audience:** Operations engineers, DevOps teams, system administrators, on-call engineers

**Document Purpose:** Comprehensive guide for deploying, scaling, monitoring, troubleshooting, and maintaining InfraFabric in production environments.

---

## TABLE OF CONTENTS

1. [Quick Reference](#quick-reference)
2. [Production Deployment](#production-deployment)
3. [Scaling Strategies](#scaling-strategies)
4. [Monitoring & Observability](#monitoring--observability)
5. [Backup & Recovery](#backup--recovery)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Security Operations](#security-operations)
8. [Performance Optimization](#performance-optimization)
9. [Capacity Planning](#capacity-planning)
10. [Maintenance Windows](#maintenance-windows)
11. [Runbooks](#runbooks)
12. [Incident Response](#incident-response)

---

## QUICK REFERENCE

### Architecture at a Glance

```
User → OpenWebUI/API → Input Sanitizer → Router → Model (Claude Max)
                          ↓
                    IF.emotion Sandbox
                    (personality injection)
                          ↓
                    Output Filters
                    (safety checks)
                          ↓
                    IF.guard Council
                    (final review)
                          ↓
                    Memory (Redis/ChromaDB)
                    ↓
                    User
```

### Critical Metrics (Alerting Thresholds)

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| **API Latency (p99)** | >200ms | >1000ms | Check model queue; scale horizontally |
| **Error Rate** | >0.5% | >2% | Review logs; check downstream services |
| **Redis Memory** | 70% | 90% | Increase Redis memory; check eviction policy |
| **ChromaDB Disk** | 75% | 95% | Archive old embeddings; expand storage |
| **Agent Availability** | <85% | <70% | Restart agents; check resource constraints |
| **Token Budget Usage** | 70%/week | 90%/week | Reduce query complexity; use Haiku model |

### Service Dependencies

```
┌─────────────────────────────────────────────────────┐
│ OpenWebUI (Web Interface)                           │
│ REST API / CLI Interface                            │
└────────────┬────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────┐
│ Security Layer (Input Sanitizer, Rate Limiter)     │
└────────────┬────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────┐
│ Claude Max Router (Model Selection)                 │
│ - Sonnet 4.5 (primary)                              │
│ - Haiku 4.5 (cost optimization)                     │
│ - Opus 4.1 (complex reasoning)                      │
└────────────┬────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────┐
│ IF.emotion Framework                                │
│ ├─ Personality DNA (ChromaDB)                       │
│ ├─ Output Filters                                   │
│ └─ Guardian Council                                 │
└────────────┬────────────────────────────────────────┘
             │
        ┌────┴────┐
        ↓         ↓
   ┌────────┐  ┌──────────┐
   │ Redis  │  │ ChromaDB  │
   │(Context)  │(Deep Store)
   └────────┘  └──────────┘
        ↑         ↑
        └────┬────┘
             │
       ┌─────┴──────┐
       ↓            ↓
    Redis L1     Redis L2
    (Cloud)      (Archive)
```

### Port Reference

| Port | Service | Access | Purpose |
|------|---------|--------|---------|
| **8080** | OpenWebUI | Internet | Web interface |
| **8000** | ChromaDB | Internal | Vector database |
| **6379** | Redis L1 | Internal | Context memory (hot cache) |
| **6379** | Redis L2 | Internal | Archive storage (if self-hosted) |
| **8081** | Redis Commander | Internal only | Debug tool (disable in production) |
| **9090** | Prometheus | Internal | Metrics scraping |
| **3000** | Grafana | Internet | Dashboards |

---

## PRODUCTION DEPLOYMENT

### Infrastructure Requirements

#### Minimum Production Setup

```yaml
Compute:
  CPU: 4 cores (Intel/AMD)
  RAM: 8GB minimum (16GB recommended)
  Disk: 50GB SSD (for ChromaDB + archives)
  Network: 50+ Mbps

Services:
  - Docker 20.10+
  - Python 3.10+ (if not using Docker)
  - Redis Cloud (or self-managed Redis 6.0+)
  - PostgreSQL 12+ (optional, for persistent storage)
```

#### Recommended Production Setup

```yaml
Compute:
  CPU: 8 cores
  RAM: 16GB+
  Disk: 100GB+ SSD
  Network: 1 Gbps

Load Balancing:
  - nginx or Caddy (reverse proxy)
  - SSL termination
  - gzip compression

Monitoring:
  - Prometheus (metrics collection)
  - Grafana (dashboards)
  - ELK Stack (log aggregation) - optional

Backup:
  - Daily Redis snapshots
  - Daily ChromaDB archives
  - 30-day hot retention + 365-day cold retention
```

### Docker Compose Deployment

#### Step 1: Create docker-compose.yml

```yaml
version: '3.8'

services:
  # Open WebUI
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: infrafabric-webui
    ports:
      - "8080:8080"
    environment:
      - WEBUI_AUTH=true
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}
      - OLLAMA_BASE_URL=http://localhost:11434
      - OPENAI_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_BASE_URL=https://api.anthropic.com/v1
    volumes:
      - ./data/webui:/app/backend/data
    networks:
      - infrafabric-net
    restart: unless-stopped

  # ChromaDB (Vector Database)
  chromadb:
    image: chromadb/chroma:latest
    container_name: infrafabric-chromadb
    ports:
      - "8000:8000"
    environment:
      - CHROMA_DB_IMPL=duckdb+parquet
      - PERSIST_DIRECTORY=/data/.chroma
    volumes:
      - ./data/.chroma:/data/.chroma
      - ./config/chromadb.yaml:/chroma_conf/config.yaml:ro
    networks:
      - infrafabric-net
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis Commander (Debug Tool - DISABLE in Production)
  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: infrafabric-redis-commander
    ports:
      - "8081:8081"
    environment:
      - REDIS_HOSTS=cache:${REDIS_HOST}:${REDIS_PORT}
    networks:
      - infrafabric-net
    profiles:
      - debug  # Only run with: docker-compose --profile debug up

networks:
  infrafabric-net:
    driver: bridge
```

#### Step 2: Environment Variables (.env)

```bash
# Redis Cloud L1 (Hot Cache)
REDIS_HOST=redis-xxxxx.c335.europe-west2-1.gce.cloud.redislabs.com
REDIS_PORT=19956
REDIS_PASSWORD=your_redis_password
REDIS_DB=0
REDIS_TTL=2592000  # 30 days

# Redis L2 (Archive - if self-hosted)
REDIS_L2_HOST=your-server-ip
REDIS_L2_PORT=6379
REDIS_L2_PASSWORD=your_redis_l2_password
REDIS_L2_DB=1

# ChromaDB
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
CHROMADB_PATH=./data/.chroma
CHROMADB_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# OpenWebUI
WEBUI_AUTH=true
WEBUI_SECRET_KEY=$(openssl rand -base64 32)

# Claude API Keys
ANTHROPIC_API_KEY=sk-ant-v0-xxxxx
OPENROUTER_API_KEY=sk-or-v1-xxxxx
DEEPSEEK_API_KEY=sk-xxxxx

# System
DEBUG=false
LOG_LEVEL=INFO
TIMEZONE=UTC
```

#### Step 3: Deploy

```bash
# Create required directories
mkdir -p data/{webui,.chroma,archives} config/ssl logs

# Set permissions
chmod 700 data

# Deploy with Docker Compose
docker-compose up -d

# Verify services
docker-compose ps
docker-compose logs -f

# Health check
curl http://localhost:8080/api/v1/status
curl http://localhost:8000/api/v1/heartbeat
```

### Kubernetes Deployment (Optional)

#### Step 1: Create Kubernetes Manifests

```yaml
# infrafabric-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: infrafabric

---
# infrafabric-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: infrafabric-config
  namespace: infrafabric
data:
  log_level: "INFO"
  debug_mode: "false"
  chromadb_host: "chromadb"
  chromadb_port: "8000"

---
# infrafabric-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: infrafabric-secrets
  namespace: infrafabric
type: Opaque
stringData:
  redis_password: "YOUR_REDIS_PASSWORD"
  anthropic_api_key: "sk-ant-v0-xxxxx"
  openrouter_api_key: "sk-or-v1-xxxxx"
  webui_secret_key: "$(openssl rand -base64 32)"

---
# chromadb-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chromadb
  namespace: infrafabric
spec:
  replicas: 1
  selector:
    matchLabels:
      app: chromadb
  template:
    metadata:
      labels:
        app: chromadb
    spec:
      containers:
      - name: chromadb
        image: chromadb/chroma:latest
        ports:
        - containerPort: 8000
        env:
        - name: CHROMA_DB_IMPL
          value: "duckdb+parquet"
        - name: PERSIST_DIRECTORY
          value: "/data/.chroma"
        volumeMounts:
        - name: chroma-data
          mountPath: /data/.chroma
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/v1/heartbeat
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: chroma-data
        persistentVolumeClaim:
          claimName: chroma-pvc

---
# open-webui-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: open-webui
  namespace: infrafabric
spec:
  replicas: 3  # Horizontal scaling
  selector:
    matchLabels:
      app: open-webui
  template:
    metadata:
      labels:
        app: open-webui
    spec:
      containers:
      - name: open-webui
        image: ghcr.io/open-webui/open-webui:main
        ports:
        - containerPort: 8080
        env:
        - name: WEBUI_AUTH
          value: "true"
        - name: WEBUI_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: infrafabric-secrets
              key: webui_secret_key
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: infrafabric-secrets
              key: anthropic_api_key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/v1/status
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10

---
# Service (ClusterIP for internal, LoadBalancer for external)
apiVersion: v1
kind: Service
metadata:
  name: open-webui-service
  namespace: infrafabric
spec:
  type: LoadBalancer
  selector:
    app: open-webui
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080

---
# PersistentVolumeClaim
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: chroma-pvc
  namespace: infrafabric
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
```

#### Step 2: Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f infrafabric-namespace.yaml
kubectl apply -f infrafabric-secret.yaml
kubectl apply -f infrafabric-configmap.yaml
kubectl apply -f chromadb-deployment.yaml
kubectl apply -f open-webui-deployment.yaml

# Verify deployment
kubectl get pods -n infrafabric
kubectl logs -n infrafabric -f deployment/open-webui

# Port forward for testing
kubectl port-forward -n infrafabric svc/open-webui-service 8080:80
```

### TLS/SSL Setup

#### Let's Encrypt (Recommended for Production)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx -y

# Obtain certificate (requires domain)
sudo certbot certonly --standalone \
  -d your-domain.com \
  -d www.your-domain.com \
  --agree-tos \
  -m admin@your-domain.com

# Verify certificate
sudo ls -la /etc/letsencrypt/live/your-domain.com/
```

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip Compression
    gzip on;
    gzip_types text/plain text/css text/javascript
               application/json application/javascript
               application/xml+rss application/atom+xml;

    # Proxy Settings
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket Support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
```

#### Deploy Nginx

```bash
# Create nginx config
sudo cp nginx.conf /etc/nginx/sites-available/infrafabric

# Enable site
sudo ln -s /etc/nginx/sites-available/infrafabric \
           /etc/nginx/sites-enabled/infrafabric

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# Auto-renewal for Let's Encrypt
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Secrets Management (HashiCorp Vault)

```bash
# Install Vault
wget https://releases.hashicorp.com/vault/1.15.0/vault_1.15.0_linux_amd64.zip
unzip vault_1.15.0_linux_amd64.zip
sudo mv vault /usr/local/bin/

# Initialize Vault
vault operator init \
  -key-shares=5 \
  -key-threshold=3 \
  -output-curl-format

# Unseal Vault (requires 3 keys from init output)
vault operator unseal [KEY_1]
vault operator unseal [KEY_2]
vault operator unseal [KEY_3]

# Authenticate
vault login [INITIAL_ROOT_TOKEN]

# Store API Keys
vault kv put secret/infrafabric/anthropic \
  api_key=sk-ant-v0-xxxxx

vault kv put secret/infrafabric/redis \
  password=your_redis_password \
  host=redis-xxxxx.c335.europe-west2-1.gce.cloud.redislabs.com \
  port=19956

# Retrieve secrets
vault kv get secret/infrafabric/anthropic
```

---

## SCALING STRATEGIES

### Horizontal Scaling (Adding More Servers)

#### Redis Cluster (For Context Memory)

```bash
# Create 3-node Redis Cluster (minimum for production)
redis-server --port 6379 --cluster-enabled yes --cluster-node-timeout 5000
redis-server --port 6380 --cluster-enabled yes --cluster-node-timeout 5000
redis-server --port 6381 --cluster-enabled yes --cluster-node-timeout 5000

# Initialize cluster
redis-cli --cluster create \
  127.0.0.1:6379 127.0.0.1:6380 127.0.0.1:6381 \
  --cluster-replicas 1

# Verify cluster
redis-cli -c cluster info
redis-cli -c cluster nodes
```

#### Multiple OpenWebUI Instances

```yaml
# docker-compose.yml with load balancing
version: '3.8'

services:
  webui-1:
    image: ghcr.io/open-webui/open-webui:main
    container_name: infrafabric-webui-1
    environment:
      - WEBUI_AUTH=true
    networks:
      - infrafabric-net

  webui-2:
    image: ghcr.io/open-webui/open-webui:main
    container_name: infrafabric-webui-2
    environment:
      - WEBUI_AUTH=true
    networks:
      - infrafabric-net

  webui-3:
    image: ghcr.io/open-webui/open-webui:main
    container_name: infrafabric-webui-3
    environment:
      - WEBUI_AUTH=true
    networks:
      - infrafabric-net

  nginx:
    image: nginx:latest
    container_name: infrafabric-nginx
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - webui-1
      - webui-2
      - webui-3
    networks:
      - infrafabric-net
```

#### Haiku Agent Pool Sizing

```bash
# Current configuration
MAX_CONCURRENT_AGENTS=40

# Scaling formula: 1 Sonnet coordinator per 20 agents
# If 40 agents: 2 Sonnet coordinators (already configured)
# If 80 agents: 4 Sonnet coordinators + additional hardware

# Hardware requirements per 20 agents
- CPU: +2 cores
- RAM: +4GB
- Network: +10 Mbps

# Deployment example for 80 agents
coordinators: 4
agents_per_coordinator: 20
total_cpu_cores: 8+ (minimum 2 per coordinator)
total_ram: 16GB+ (minimum 4GB per coordinator)
```

### Vertical Scaling (Increasing Server Resources)

#### Redis Memory Expansion

```bash
# Monitor current usage
redis-cli info memory

# Calculate new maxmemory
current_usage=$(redis-cli info memory | grep used_memory_human)
# If using 70%+ of current limit, increase by 50%

# Update configuration
redis-cli CONFIG SET maxmemory 16gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Verify change
redis-cli CONFIG GET maxmemory
redis-cli CONFIG GET maxmemory-policy

# Persist changes
redis-cli BGSAVE  # Create backup before changes
```

#### ChromaDB Storage Expansion

```bash
# Monitor disk usage
du -sh ./data/.chroma

# If >80% full, expand storage:
# Option 1: Cloud storage (recommended)
gsutil -m cp -r gs://backup-bucket/chroma-archive/* ./data/.chroma/

# Option 2: Attach additional volume (if using VM)
# 1. Create new volume (50GB)
# 2. Attach to instance
# 3. Mount: sudo mount /dev/sdb1 /mnt/chroma-extended
# 4. Move data: sudo mv ./data/.chroma/* /mnt/chroma-extended/
# 5. Update docker-compose volume mount

# Option 3: Implement TTL-based retention
# Archive old embeddings (>365 days) to cold storage
python scripts/archive_old_embeddings.py --older-than 365 --destination gs://cold-storage/chroma/
```

### Load Balancing

#### Caddy (Lightweight Alternative to Nginx)

```caddyfile
# Caddyfile
your-domain.com {
    reverse_proxy localhost:8080 localhost:8081 localhost:8082 {
        policy round_robin
        health_uri /api/v1/status
        health_interval 10s
        health_timeout 5s
    }

    encode gzip
    file_server

    # Compression headers
    header {
        -Server
        X-Content-Type-Options nosniff
        X-Frame-Options SAMEORIGIN
    }
}
```

### CDN Integration (For Static Assets)

```bash
# Upload static assets to CDN (Cloudflare, Bunny, etc.)
gsutil -m cp -r ./data/static/* gs://your-cdn-bucket/

# Update configuration to use CDN URLs
STATIC_CDN_URL=https://cdn.your-domain.com

# Example in OpenWebUI config:
# PROFILE_PICTURE_URL=https://cdn.your-domain.com/profiles/
```

---

## MONITORING & OBSERVABILITY

### Prometheus Metrics Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'infrafabric-prod'
    environment: 'production'

scrape_configs:
  # InfraFabric Application Metrics
  - job_name: 'infrafabric'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['localhost:9090']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance

  # Redis Metrics
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']
        labels:
          redis_instance: 'L1-cache'
      - targets: ['your-redis-l2-host:6379']
        labels:
          redis_instance: 'L2-archive'

  # ChromaDB Metrics
  - job_name: 'chromadb'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['localhost:8000']

  # Node Exporter (System Metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  # Docker Metrics
  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9323']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - localhost:9093

rule_files:
  - 'alert_rules.yml'
```

### Grafana Dashboards

#### Dashboard 1: System Health Overview

```json
{
  "dashboard": {
    "title": "InfraFabric System Health",
    "panels": [
      {
        "title": "API Response Time (p99)",
        "targets": [
          {"expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))"}
        ],
        "thresholds": [
          {"value": 200, "color": "green"},
          {"value": 1000, "color": "red"}
        ]
      },
      {
        "title": "Error Rate (%)",
        "targets": [
          {"expr": "rate(http_requests_total{status=~'5..'}[5m]) * 100"}
        ],
        "thresholds": [
          {"value": 1, "color": "yellow"},
          {"value": 5, "color": "red"}
        ]
      },
      {
        "title": "Redis Memory Usage (%)",
        "targets": [
          {"expr": "(redis_memory_used_bytes / redis_maxmemory_bytes) * 100"}
        ],
        "thresholds": [
          {"value": 70, "color": "yellow"},
          {"value": 90, "color": "red"}
        ]
      },
      {
        "title": "ChromaDB Disk Usage (%)",
        "targets": [
          {"expr": "(node_filesystem_size_bytes{mountpoint='/data'} - node_filesystem_avail_bytes{mountpoint='/data'}) / node_filesystem_size_bytes{mountpoint='/data'} * 100"}
        ]
      },
      {
        "title": "Active Agents",
        "targets": [
          {"expr": "agents_active"}
        ]
      },
      {
        "title": "Request Rate",
        "targets": [
          {"expr": "rate(http_requests_total[1m])"}
        ]
      }
    ]
  }
}
```

#### Dashboard 2: Security Events

```json
{
  "dashboard": {
    "title": "InfraFabric Security Events",
    "panels": [
      {
        "title": "Rate Limit Violations",
        "targets": [
          {"expr": "increase(rate_limit_exceeded_total[5m])"}
        ]
      },
      {
        "title": "Prompt Injection Attempts",
        "targets": [
          {"expr": "increase(prompt_injection_detected_total[5m])"}
        ]
      },
      {
        "title": "Invalid Signatures",
        "targets": [
          {"expr": "increase(signature_validation_failures_total[5m])"}
        ]
      },
      {
        "title": "IF.guard Veto Decisions",
        "targets": [
          {"expr": "increase(if_guard_veto_decisions_total[1h])"}
        ]
      }
    ]
  }
}
```

#### Dashboard 3: Performance Metrics

```json
{
  "dashboard": {
    "title": "InfraFabric Performance",
    "panels": [
      {
        "title": "Redis Latency",
        "targets": [
          {"expr": "histogram_quantile(0.99, rate(redis_command_duration_seconds_bucket[5m]))"}
        ]
      },
      {
        "title": "ChromaDB Query Latency",
        "targets": [
          {"expr": "histogram_quantile(0.99, rate(chromadb_query_duration_seconds_bucket[5m]))"}
        ]
      },
      {
        "title": "Model Inference Time",
        "targets": [
          {"expr": "histogram_quantile(0.99, rate(model_inference_duration_seconds_bucket[5m]))"}
        ]
      },
      {
        "title": "IF.emotion Processing Time",
        "targets": [
          {"expr": "histogram_quantile(0.99, rate(if_emotion_processing_duration_seconds_bucket[5m]))"}
        ]
      }
    ]
  }
}
```

### Alert Rules Configuration

```yaml
# alert_rules.yml
groups:
  - name: infrafabric_alerts
    interval: 1m
    rules:
      # P0 Alerts (Critical)
      - alert: HighAPILatency
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1.0
        for: 5m
        severity: critical
        annotations:
          summary: "API latency P99 > 1 second"
          description: "Current P99 latency: {{ $value }}s. Check model queue and downstream services."

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~'5..'}[5m]) > 0.02
        for: 5m
        severity: critical
        annotations:
          summary: "Error rate > 2%"
          description: "Current error rate: {{ $value | humanizePercentage }}. Review error logs immediately."

      - alert: RedisCriticalMemory
        expr: (redis_memory_used_bytes / redis_maxmemory_bytes) > 0.9
        for: 2m
        severity: critical
        annotations:
          summary: "Redis memory > 90%"
          description: "Current usage: {{ $value | humanizePercentage }}. Increase maxmemory immediately."

      - alert: ChromaDBDiskCritical
        expr: (node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes > 0.95
        for: 2m
        severity: critical
        annotations:
          summary: "ChromaDB disk > 95%"
          description: "Archive old embeddings and expand storage."

      # P1 Alerts (High)
      - alert: ModerateAPILatency
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 0.2
        for: 10m
        severity: warning
        annotations:
          summary: "API latency P99 > 200ms"
          description: "Current P99 latency: {{ $value }}s. Consider scaling."

      - alert: AgentAvailabilityLow
        expr: (agents_active / agents_total) < 0.85
        for: 5m
        severity: warning
        annotations:
          summary: "< 85% of agents available"
          description: "Only {{ $value | humanizePercentage }} agents active. Check agent logs."

      - alert: TokenBudgetWarning
        expr: (tokens_used_week / tokens_budget_week) > 0.8
        for: 1h
        severity: warning
        annotations:
          summary: "Token budget > 80% used"
          description: "Current usage: {{ $value | humanizePercentage }}. Consider optimization."

      # P2 Alerts (Medium)
      - alert: RedisHighMemory
        expr: (redis_memory_used_bytes / redis_maxmemory_bytes) > 0.7
        for: 15m
        severity: warning
        annotations:
          summary: "Redis memory > 70%"
          description: "Plan to increase maxmemory or implement eviction."

      - alert: ChromaDBDiskWarning
        expr: (node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes > 0.75
        for: 1h
        severity: warning
        annotations:
          summary: "ChromaDB disk > 75%"
          description: "Consider archiving old embeddings."

      - alert: HighRateLimitExceeded
        expr: increase(rate_limit_exceeded_total[5m]) > 10
        for: 5m
        severity: warning
        annotations:
          summary: "High rate limit violations"
          description: "{{ $value }} rate limit violations in last 5m. Check for DDoS or misbehaving clients."
```

### Log Aggregation (ELK Stack)

#### Filebeat Configuration

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - ./logs/audit.log
    - ./logs/error.log
    - ./logs/access.log
  fields:
    service: infrafabric
    environment: production

processors:
  - add_kubernetes_metadata:
      in_cluster: true
  - add_cloud_metadata: ~
  - add_host_metadata: ~

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "infrafabric-%{+yyyy.MM.dd}"

logging.level: info
logging.to_files: true
logging.files:
  path: ./logs/filebeat
  name: filebeat
  keepfiles: 7
  permissions: 0644
```

#### Elasticsearch Query Examples

```bash
# List recent errors
curl -X GET "localhost:9200/infrafabric-*/_search?pretty" -H 'Content-Type: application/json' -d'{
  "query": {
    "match": {
      "log.level": "ERROR"
    }
  },
  "size": 100,
  "sort": [{"@timestamp": {"order": "desc"}}]
}'

# Find rate limit violations
curl -X GET "localhost:9200/infrafabric-*/_search?pretty" -H 'Content-Type: application/json' -d'{
  "query": {
    "match": {
      "message": "rate_limit_exceeded"
    }
  }
}'

# Security events in last 24 hours
curl -X GET "localhost:9200/infrafabric-*/_search?pretty" -H 'Content-Type: application/json' -d'{
  "query": {
    "bool": {
      "must": [
        {"match": {"event_type": "security"}},
        {"range": {"@timestamp": {"gte": "now-24h"}}}
      ]
    }
  }
}'
```

---

## BACKUP & RECOVERY

### Backup Strategy

#### Daily Backup Schedule

```bash
#!/bin/bash
# backup.sh - Run daily via cron: 0 2 * * * /home/setup/infrafabric/scripts/backup.sh

BACKUP_DIR="/mnt/backups/infrafabric"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# 1. Redis L1 Snapshot
echo "Backing up Redis L1..."
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD BGSAVE
sleep 5  # Wait for BGSAVE to complete
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD --rdb $BACKUP_DIR/$DATE/redis-l1-dump.rdb

# 2. Redis L2 Snapshot (if self-hosted)
echo "Backing up Redis L2..."
redis-cli -h $REDIS_L2_HOST -p $REDIS_L2_PORT -a $REDIS_L2_PASSWORD BGSAVE
sleep 5
redis-cli -h $REDIS_L2_HOST -p $REDIS_L2_PORT -a $REDIS_L2_PASSWORD --rdb $BACKUP_DIR/$DATE/redis-l2-dump.rdb

# 3. ChromaDB Backup
echo "Backing up ChromaDB..."
cp -r ./data/.chroma $BACKUP_DIR/$DATE/chromadb-data

# 4. Configuration Backup
echo "Backing up configuration..."
cp .env $BACKUP_DIR/$DATE/.env.backup
cp config/infrafabric.schema.json $BACKUP_DIR/$DATE/
cp config/chromadb.yaml $BACKUP_DIR/$DATE/

# 5. Audit Logs Backup
echo "Backing up audit logs..."
cp logs/audit.log $BACKUP_DIR/$DATE/

# 6. Create tarball and compress
echo "Compressing backup..."
cd $BACKUP_DIR
tar -czf infrafabric-backup-$DATE.tar.gz $DATE/
rm -rf $DATE/

# 7. Upload to cloud storage (GCS example)
echo "Uploading to cloud storage..."
gsutil -m cp infrafabric-backup-$DATE.tar.gz gs://your-backup-bucket/daily/

# 8. Cleanup old backups (retention)
echo "Cleaning up old backups..."
find $BACKUP_DIR -name "infrafabric-backup-*.tar.gz" -mtime +$RETENTION_DAYS -delete
gsutil -m rm gs://your-backup-bucket/daily/infrafabric-backup-*.tar.gz # Cloud cleanup

echo "Backup complete: infrafabric-backup-$DATE.tar.gz"

# Send notification (optional)
echo "InfraFabric backup completed successfully on $(date)" | mail -s "Backup Report" ops@your-domain.com
```

#### Incremental Backup (Weekly)

```bash
#!/bin/bash
# incremental_backup.sh

BACKUP_DIR="/mnt/backups/infrafabric"
DATE=$(date +%Y%m%d_%H%M%S)

# Only backup changes since last full backup
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD BGREWRITEAOF

# Archive incremental changes
rsync -av --backup --backup-dir=$BACKUP_DIR/incremental-$DATE \
  ./data/.chroma $BACKUP_DIR/latest/

# Compress and upload
tar -czf infrafabric-incremental-$DATE.tar.gz $BACKUP_DIR/incremental-$DATE/
gsutil cp infrafabric-incremental-$DATE.tar.gz gs://your-backup-bucket/incremental/
```

### Disaster Recovery Procedures

#### Recovery Time Objective (RTO): 1 Hour
#### Recovery Point Objective (RPO): 5 Minutes

#### Full Recovery (From Most Recent Backup)

```bash
#!/bin/bash
# recover.sh - Full system recovery from backup

BACKUP_FILE=$1  # e.g., "infrafabric-backup-20251130_020000.tar.gz"

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: ./recover.sh <backup-file>"
  exit 1
fi

echo "Starting InfraFabric disaster recovery..."
echo "Backup file: $BACKUP_FILE"

# Step 1: Stop services
echo "Step 1: Stopping services..."
docker-compose down

# Step 2: Extract backup
echo "Step 2: Extracting backup..."
mkdir -p /tmp/recovery
cd /tmp/recovery
tar -xzf /path/to/$BACKUP_FILE

BACKUP_DATE=$(ls -d */ | head -1 | tr -d '/')

# Step 3: Restore Redis L1
echo "Step 3: Restoring Redis L1..."
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD SHUTDOWN NOSAVE
sleep 5

# Copy RDB file to Redis data directory
cp /tmp/recovery/$BACKUP_DATE/redis-l1-dump.rdb /var/lib/redis/dump.rdb
chmod 644 /var/lib/redis/dump.rdb

redis-server --port $REDIS_PORT --requirepass $REDIS_PASSWORD --appendonly yes

# Wait for Redis to load
sleep 10
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD PING

# Step 4: Restore Redis L2
echo "Step 4: Restoring Redis L2..."
if [ ! -z "$REDIS_L2_HOST" ]; then
  redis-cli -h $REDIS_L2_HOST -p $REDIS_L2_PORT -a $REDIS_L2_PASSWORD SHUTDOWN NOSAVE
  sleep 5
  cp /tmp/recovery/$BACKUP_DATE/redis-l2-dump.rdb /var/lib/redis-l2/dump.rdb
  redis-server --port $REDIS_L2_PORT --requirepass $REDIS_L2_PASSWORD --appendonly yes
  sleep 10
fi

# Step 5: Restore ChromaDB
echo "Step 5: Restoring ChromaDB..."
rm -rf ./data/.chroma
cp -r /tmp/recovery/$BACKUP_DATE/chromadb-data ./data/.chroma

# Step 6: Restore configuration
echo "Step 6: Restoring configuration..."
cp /tmp/recovery/$BACKUP_DATE/.env.backup .env
cp /tmp/recovery/$BACKUP_DATE/infrafabric.schema.json config/

# Step 7: Restore audit logs
echo "Step 7: Restoring audit logs..."
cp /tmp/recovery/$BACKUP_DATE/audit.log logs/audit.log.recovered
cat logs/audit.log.recovered >> logs/audit.log

# Step 8: Start services
echo "Step 8: Starting services..."
docker-compose up -d

# Step 9: Verify recovery
echo "Step 9: Verifying recovery..."
sleep 30

# Check Redis connectivity
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD PING
REDIS_STATUS=$?

# Check ChromaDB connectivity
curl http://localhost:8000/api/v1/heartbeat
CHROMADB_STATUS=$?

# Check OpenWebUI
curl http://localhost:8080/api/v1/status
WEBUI_STATUS=$?

if [ $REDIS_STATUS -eq 0 ] && [ $CHROMADB_STATUS -eq 0 ] && [ $WEBUI_STATUS -eq 0 ]; then
  echo "✅ Recovery successful!"
  echo "InfraFabric is operational. Recovery Time: ~$(date +%s) - $START_TIME seconds"
else
  echo "⚠️ Recovery completed with warnings. Please verify services manually."
  echo "Redis status: $REDIS_STATUS"
  echo "ChromaDB status: $CHROMADB_STATUS"
  echo "OpenWebUI status: $WEBUI_STATUS"
fi

# Cleanup
rm -rf /tmp/recovery
```

#### Point-in-Time Recovery (Audit Logs)

```bash
#!/bin/bash
# recover_to_point_in_time.sh

RECOVERY_TIME=$1  # e.g., "2025-11-30 14:30:00"

if [ -z "$RECOVERY_TIME" ]; then
  echo "Usage: ./recover_to_point_in_time.sh '2025-11-30 14:30:00'"
  exit 1
fi

echo "Recovering to point-in-time: $RECOVERY_TIME"

# Find relevant backups
grep "timestamp" logs/audit.log | grep "$RECOVERY_TIME"

# Restore from nearest full backup
BACKUP_DATE=$(date -d "$(date -d "$RECOVERY_TIME") - 1 day" +%Y%m%d)
BACKUP_FILE="infrafabric-backup-$BACKUP_DATE*.tar.gz"

echo "Using backup: $BACKUP_FILE"

# Execute full recovery
./recover.sh $BACKUP_FILE

# Replay audit events up to recovery time
echo "Replaying audit events up to $RECOVERY_TIME..."
grep "timestamp.*$RECOVERY_TIME" logs/audit.log | head -100 > /tmp/recovery-events.log

echo "Point-in-time recovery complete!"
```

---

## TROUBLESHOOTING GUIDE

### Common Issues & Solutions

#### Issue 1: Redis Connection Timeout

**Symptoms:**
- `ConnectionError: Redis timeout after 5s`
- OpenWebUI unable to reach Redis
- Chat responses slow or timing out

**Root Causes:**
1. Redis service down
2. Network connectivity issue
3. Firewall blocking port 6379
4. Redis port changed
5. Redis memory full (evicting keys)

**Diagnosis:**

```bash
# Step 1: Verify Redis is running
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD PING

# Step 2: Check network connectivity
ping $REDIS_HOST
telnet $REDIS_HOST $REDIS_PORT

# Step 3: Check firewall rules
sudo ufw status | grep 6379
sudo iptables -L | grep 6379

# Step 4: Monitor Redis
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD INFO server
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD INFO memory

# Step 5: Check Redis logs
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD MONITOR

# Step 6: Check connection pool usage
redis-cli CLIENT LIST | wc -l
redis-cli CONFIG GET maxclients
```

**Solutions:**

```bash
# Solution 1: Restart Redis
sudo systemctl restart redis-server

# Solution 2: Check and fix credentials
# Update .env file with correct password
source .env
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD PING

# Solution 3: Increase max clients
redis-cli CONFIG SET maxclients 10000

# Solution 4: Clear memory if full
redis-cli CONFIG GET maxmemory-policy
# If 'noeviction', switch to 'allkeys-lru':
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Solution 5: Check connection pool settings
# Adjust in code or docker-compose:
REDIS_POOL_SIZE=50
REDIS_SOCKET_TIMEOUT=10
REDIS_SOCKET_CONNECT_TIMEOUT=10

# Solution 6: Increase timeout in .env
REDIS_TIMEOUT=30000  # 30 seconds instead of default 5s
```

**Prevention:**
- Monitor Redis memory usage (alert at 70%)
- Implement connection pooling
- Regular Redis maintenance
- Set up Redis Cluster for high availability

#### Issue 2: Token Refresh Failures

**Symptoms:**
- `401 Unauthorized` after 1 hour
- User sessions expiring unexpectedly
- Claude API returning auth errors

**Root Causes:**
1. OAuth provider (Anthropic) unavailable
2. Refresh token invalid/expired
3. Network connectivity to Anthropic
4. Clock skew (server time mismatch)
5. API key quotas exceeded

**Diagnosis:**

```bash
# Step 1: Verify API key validity
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/models

# Step 2: Check token expiration
# In application logs:
grep "token_expiration" logs/audit.log

# Step 3: Monitor API calls
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/billing/current_balance

# Step 4: Check server time
date
# Should be within 1 minute of NTP server

# Step 5: Review API logs
journalctl -u infrafabric -n 100 | grep -i "token\|auth"
```

**Solutions:**

```bash
# Solution 1: Validate API key
python -c "
from anthropic import Anthropic
client = Anthropic(api_key='$ANTHROPIC_API_KEY')
print('API key valid!')
"

# Solution 2: Sync server time
sudo ntpdate -s time.nist.gov
# Or use timedatectl:
sudo timedatectl set-ntp on

# Solution 3: Refresh expired tokens
curl -X POST https://api.anthropic.com/v1/auth/token/refresh \
  -H "Authorization: Bearer $REFRESH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# Solution 4: Check API quotas
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/billing/usage

# Solution 5: Implement token refresh ahead of expiration
# In code: refresh tokens 15 minutes before expiry
def should_refresh_token(token_expiry):
    return datetime.utcnow() > token_expiry - timedelta(minutes=15)
```

**Prevention:**
- Monitor token expiration proactively
- Keep NTP synchronized
- Rotate API keys quarterly
- Set up API quota alerts

#### Issue 3: ChromaDB Query Timeout

**Symptoms:**
- `chromadb.errors.RequestError: timeout`
- Semantic search taking >5 seconds
- Memory exhaustion (100% disk I/O)

**Root Causes:**
1. ChromaDB index too large
2. Slow disk I/O
3. HNSW index not optimized
4. Insufficient RAM for index
5. Network latency (if remote ChromaDB)

**Diagnosis:**

```bash
# Step 1: Check ChromaDB service
curl http://localhost:8000/api/v1/heartbeat

# Step 2: Monitor disk I/O
iostat -x 1 5

# Step 3: Check ChromaDB logs
docker logs chromadb | tail -50

# Step 4: Measure query latency
python -c "
import time
import chromadb
client = chromadb.HttpClient(host='localhost', port=8000)
collection = client.get_collection('if_emotion_dna')

start = time.time()
results = collection.query(
    query_texts=['test query'],
    n_results=10
)
elapsed = time.time() - start
print(f'Query time: {elapsed:.2f}s')
"

# Step 5: Check index size
du -sh ./data/.chroma/

# Step 6: Check ChromaDB config
cat config/chromadb.yaml
```

**Solutions:**

```bash
# Solution 1: Optimize HNSW index
# In ChromaDB config:
# "hnsw": {
#   "space": "cosine",
#   "ef_construction": 200,
#   "max_m": 16
# }

# Solution 2: Restart ChromaDB
docker-compose restart chromadb
sleep 10

# Solution 3: Rebuild index
curl -X POST http://localhost:8000/api/v1/collections/if_emotion_dna/rebuild_index

# Solution 4: Archive old embeddings
python scripts/archive_old_embeddings.py \
  --older-than 90 \
  --destination gs://backup/chroma-archive/

# Solution 5: Increase ChromaDB resources
# In docker-compose.yml:
# resources:
#   limits:
#     memory: "4Gi"
#     cpus: "2"

# Solution 6: Use caching
# Enable ChromaDB query cache:
CHROMADB_CACHE_SIZE=1000  # Cache last 1000 queries

# Solution 7: Increase timeout
CHROMADB_TIMEOUT=30  # 30 seconds instead of 10s
```

**Prevention:**
- Monitor query latency (alert at 200ms)
- Archive embeddings >90 days old
- Keep index size <100GB
- Use SSD storage
- Set up monitoring for disk I/O

#### Issue 4: High Memory Usage

**Symptoms:**
- `MemoryError: Unable to allocate XXX MB`
- System swap usage > 0
- OOM (Out of Memory) killer triggered
- Application slowdown/freezing

**Root Causes:**
1. Memory leaks in application
2. Large conversation history in Redis
3. ChromaDB index too large in RAM
4. Too many concurrent agents
5. Caching configuration too aggressive

**Diagnosis:**

```bash
# Step 1: Check system memory
free -h
top -b -n 1 | head -20

# Step 2: Check Docker container memory
docker stats --no-stream

# Step 3: Check Redis memory usage
redis-cli INFO memory

# Step 4: Check ChromaDB memory
curl http://localhost:8000/api/v1/debug/memory

# Step 5: Check application memory
ps aux | grep python | grep infrafabric
# Check the RSS (resident set size) column

# Step 6: Find memory leaks
# Monitor over time:
watch -n 10 'free -h && echo "---" && docker stats --no-stream'

# Step 7: Check active sessions
redis-cli KEYS "memory:session:*" | wc -l
redis-cli KEYS "*" | wc -l  # Total keys
```

**Solutions:**

```bash
# Solution 1: Restart container
docker-compose restart open-webui

# Solution 2: Clear Redis cache (non-destructive)
redis-cli FLUSHDB  # Clear only current DB
redis-cli FLUSHALL  # Clear all DBs (risky!)

# Solution 3: Clean up sessions older than 1 hour
redis-cli KEYS "memory:session:*" | \
while read key; do
  TTL=$(redis-cli TTL "$key")
  if [ $TTL -lt 0 ]; then
    redis-cli DEL "$key"
  fi
done

# Solution 4: Reduce concurrent agents
# In config:
MAX_CONCURRENT_AGENTS=20  # Reduce from 40

# Solution 5: Increase available RAM
# VM: Add more RAM or use cloud instance with more memory
# Docker: Increase memory limit:
# docker update --memory 4g infrafabric-webui

# Solution 6: Implement memory profiling
python -m memory_profiler infrafabric/main.py

# Solution 7: Adjust garbage collection
python -c "
import gc
gc.collect()
print(f'Memory freed: {gc.get_stats()[-1]}')
"

# Solution 8: Monitor Redis eviction
redis-cli CONFIG GET maxmemory-policy
# If 'volatile-lru', enable LRU:
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Solution 9: Disable Redis persistence if not needed
redis-cli CONFIG SET save ""  # Disable RDB snapshots
redis-cli CONFIG SET appendonly no  # Disable AOF
```

**Prevention:**
- Monitor memory usage continuously
- Set resource limits in docker-compose
- Regular cleanup of old sessions (daily cron)
- Alert at 75% memory usage
- Implement connection pooling
- Use memory profiling tools regularly

#### Issue 5: Ed25519 Signature Verification Failures

**Symptoms:**
- `InvalidSignature` errors in logs
- `cryptography.exceptions.InvalidSignature`
- Messages being rejected

**Root Causes:**
1. Public key registry out of sync
2. Message tampering
3. Clock skew (timestamp validation)
4. Key rotation not properly distributed
5. Network packet corruption

**Diagnosis:**

```bash
# Step 1: Check signature errors
grep "InvalidSignature" logs/error.log

# Step 2: Verify public key registry
cat config/keys/verify_key.pem

# Step 3: Check message chain of custody
grep "chain_of_custody" logs/audit.log | head -5

# Step 4: Verify signing key
cat config/keys/signing_key.pem | head -3

# Step 5: Check key rotation schedule
grep "key_rotation" logs/audit.log

# Step 6: Test signature verification
python -c "
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

with open('config/keys/verify_key.pem', 'rb') as f:
    public_key = serialization.load_pem_public_key(
        f.read(),
        backend=default_backend()
    )
print('Public key loaded successfully')
"
```

**Solutions:**

```bash
# Solution 1: Resync public key registry
# Distribute new public key to all agents:
ansible all -m copy -a "src=config/keys/verify_key.pem dest=/etc/infrafabric/"

# Solution 2: Verify message integrity
# Check for network corruption:
tcpdump -i eth0 -w /tmp/capture.pcap port 6379
# Analyze with Wireshark: wireshark /tmp/capture.pcap

# Solution 3: Rotate signing keys
python scripts/rotate_signing_keys.py
# Backup old key:
cp config/keys/signing_key.pem config/keys/signing_key.pem.old-$(date +%Y%m%d)

# Solution 4: Regenerate signatures for audit messages
redis-cli KEYS "message:*" | \
while read key; do
  MESSAGE=$(redis-cli GET "$key")
  SIGNATURE=$(echo "$MESSAGE" | openssl dgst -sha256 -sign config/keys/signing_key.pem | base64)
  redis-cli HSET "$key" signature "$SIGNATURE"
done

# Solution 5: Sync server time
sudo ntpdate -s time.nist.gov

# Solution 6: Re-enable signature validation (if disabled)
# In code:
# if config.SIGNATURE_VALIDATION_ENABLED:
#   validate_signature(message)
```

**Prevention:**
- Monitor signature verification rates
- Alert on >1% failure rate
- Rotate keys quarterly
- Distribute public keys before key rotation
- Implement message timestamp validation
- Regular key backup and testing

---

## SECURITY OPERATIONS

### Security Event Monitoring

#### Rate Limit Breach Response

```bash
#!/bin/bash
# Handle rate limit breaches

# Trigger: rate_limit_exceeded_total > 50 in 5 minutes

echo "Rate limit breach detected!"

# Step 1: Identify source
SOURCE_IP=$(grep "rate_limit_exceeded" logs/audit.log | tail -10 | jq '.source_ip' | sort | uniq -c | sort -rn | head -1 | awk '{print $NF}')

echo "Primary source: $SOURCE_IP"

# Step 2: Analyze pattern
echo "Request pattern (last 10 violations):"
grep "rate_limit_exceeded" logs/audit.log | tail -10 | jq '{timestamp, source_ip, endpoint}'

# Step 3: Determine if DDoS or legitimate spike
REQUEST_COUNT=$(grep -c "source_ip=$SOURCE_IP" logs/access.log | tail -5m)
echo "Total requests from $SOURCE_IP (last 5m): $REQUEST_COUNT"

# Step 4: Take action based on severity
if [ $REQUEST_COUNT -gt 1000 ]; then
  echo "Likely DDoS attack - blocking IP"
  # Temporarily block IP
  sudo iptables -A INPUT -s $SOURCE_IP -j DROP
  # Log action
  echo "Blocked $SOURCE_IP at $(date)" >> logs/security.log
elif [ $REQUEST_COUNT -gt 500 ]; then
  echo "Suspicious activity - applying stricter rate limits"
  redis-cli SET "rate_limit:$SOURCE_IP:strict" 1 EX 3600
else
  echo "Likely legitimate spike - monitoring"
fi

# Step 5: Notify ops team
echo "Rate limit breach on $SOURCE_IP with $REQUEST_COUNT requests" | \
  mail -s "ALERT: Rate Limit Breach" ops@your-domain.com
```

#### Unauthorized Access Investigation

```bash
#!/bin/bash
# Investigate unauthorized access attempts

# Trigger: Multiple failed authentications from single IP

SUSPICIOUS_IP=$1

if [ -z "$SUSPICIOUS_IP" ]; then
  echo "Usage: ./investigate_unauthorized_access.sh <IP>"
  exit 1
fi

echo "Investigating unauthorized access from $SUSPICIOUS_IP..."

# Step 1: Get all access attempts
echo "=== Access attempts from $SUSPICIOUS_IP ==="
grep "source_ip=$SUSPICIOUS_IP" logs/audit.log | jq '{timestamp, endpoint, status, user_agent}'

# Step 2: Check failed auth attempts
echo "=== Failed authentications ==="
grep "source_ip=$SUSPICIOUS_IP" logs/audit.log | grep '"success": false' | wc -l

# Step 3: Check geolocation
echo "=== Geolocation lookup ==="
curl https://ipapi.co/$SUSPICIOUS_IP/json/ 2>/dev/null | jq '{country, city, org}'

# Step 4: Check for known bad IPs
echo "=== Checking threat databases ==="
curl https://api.abuseipdb.com/api/v2/check \
  --data-urlencode "ipAddress=$SUSPICIOUS_IP" \
  -H "Key: YOUR_ABUSEIPDB_API_KEY" -H "Accept: application/json" | jq '.abuseConfidenceScore'

# Step 5: Take action
read -p "Block this IP? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  sudo iptables -A INPUT -s $SUSPICIOUS_IP -j DROP
  echo "Blocked $SUSPICIOUS_IP" >> logs/security-actions.log

  # Send alert
  echo "Blocked unauthorized access from $SUSPICIOUS_IP" | \
    mail -s "ALERT: IP Blocked" ops@your-domain.com
fi
```

#### Prompt Injection Attack Response

```bash
#!/bin/bash
# Handle prompt injection attempt

# Trigger: prompt_injection_detected_total > 10 in 1 minute

echo "Prompt injection attack detected!"

# Step 1: Get attack details
echo "=== Attack details ==="
grep "prompt_injection_detected" logs/audit.log | tail -20 | jq '{timestamp, user_id, payload_snippet}'

# Step 2: Identify attacker
ATTACKER_ID=$(grep "prompt_injection_detected" logs/audit.log | tail -1 | jq -r '.user_id')
ATTACKER_IP=$(grep "prompt_injection_detected" logs/audit.log | tail -1 | jq -r '.source_ip')

echo "Attacker: $ATTACKER_ID ($ATTACKER_IP)"

# Step 3: Analyze attack pattern
echo "=== Attack pattern ==="
grep "user_id=$ATTACKER_ID" logs/audit.log | grep "prompt_injection_detected" | \
  jq '{timestamp, endpoint, injection_type}' | uniq -c | sort -rn

# Step 4: Block attacker account (if internal user)
if [ ! -z "$ATTACKER_ID" ]; then
  echo "Blocking user account: $ATTACKER_ID"
  redis-cli SET "user:$ATTACKER_ID:blocked" 1 EX 3600  # 1 hour block

  # Log action
  echo "Blocked $ATTACKER_ID due to prompt injection attack" >> logs/security-actions.log
fi

# Step 5: Block IP temporarily
echo "Blocking IP: $ATTACKER_IP"
redis-cli SET "ip:$ATTACKER_IP:rate-limit-strict" 10 EX 3600  # 10 req/hour for 1 hour

# Step 6: Escalate if severe
ATTACK_COUNT=$(grep "user_id=$ATTACKER_ID" logs/audit.log | grep -c "prompt_injection_detected")
if [ $ATTACK_COUNT -gt 50 ]; then
  echo "CRITICAL: Coordinated attack - escalating to incident response"

  # Trigger incident response
  ./scripts/incident_response.sh "CRITICAL" "Prompt injection attack" "$ATTACKER_ID/$ATTACKER_IP"
fi

# Step 7: Review payloads for new patterns
echo "=== Unique injection payloads ==="
grep "user_id=$ATTACKER_ID" logs/audit.log | grep "prompt_injection_detected" | \
  jq -r '.payload_snippet' | sort | uniq

echo "Review patterns and update input sanitizer if needed"
```

### Ed25519 Key Rotation Schedule

```bash
#!/bin/bash
# Rotate Ed25519 signing keys (quarterly)

# Schedule: 0 0 1 1,4,7,10 * (1st of every 3 months at midnight)

ROTATION_DATE=$(date +%Y%m%d)
KEY_ARCHIVE="/mnt/backups/keys/$ROTATION_DATE"

echo "Ed25519 Key Rotation - $ROTATION_DATE"

# Step 1: Backup existing keys
mkdir -p $KEY_ARCHIVE
cp config/keys/signing_key.pem $KEY_ARCHIVE/signing_key.pem
cp config/keys/verify_key.pem $KEY_ARCHIVE/verify_key.pem

echo "Backed up keys to: $KEY_ARCHIVE"

# Step 2: Generate new key pair
python << 'EOF'
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

# Generate new keys
private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Save keys
with open('config/keys/signing_key.pem', 'wb') as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

with open('config/keys/verify_key.pem', 'wb') as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

print("New keys generated successfully")
EOF

# Step 3: Distribute new public key to all agents/systems
echo "Distributing new public key..."
# Update agent registry
redis-cli SET "agent:verification_key:current" "$(cat config/keys/verify_key.pem)" EX 86400

# If using multiple servers, copy to all:
for server in $AGENT_SERVERS; do
  scp config/keys/verify_key.pem $server:/etc/infrafabric/keys/
done

# Step 4: Update audit trail
echo "Logging rotation..."
echo "{
  \"event_type\": \"key_rotation\",
  \"timestamp\": \"$(date -Iseconds)\",
  \"rotation_type\": \"quarterly\",
  \"old_key_backup\": \"$KEY_ARCHIVE\",
  \"new_key_active\": \"config/keys/signing_key.pem\"
}" | tee -a logs/security.log

# Step 5: Test new keys
echo "Testing new keys..."
python scripts/test_signing_keys.py

# Step 6: Monitor for issues
echo "Monitoring for signature failures..."
# Alert if signature failures > 5% in next hour
sleep 3600
SIGNATURE_FAILURES=$(grep "InvalidSignature" logs/error.log | wc -l)
if [ $SIGNATURE_FAILURES -gt 5 ]; then
  echo "WARNING: High signature failures after key rotation"
  echo "Key rotation may have failed. Check logs and consider rollback."

  # Rollback if needed
  # cp $KEY_ARCHIVE/signing_key.pem config/keys/signing_key.pem
  # cp $KEY_ARCHIVE/verify_key.pem config/keys/verify_key.pem
fi

echo "Key rotation complete!"
```

### Audit Log Review Procedures

```bash
#!/bin/bash
# Daily audit log review

# Schedule: 0 9 * * * (Every morning at 9 AM)

REVIEW_DATE=$(date +%Y-%m-%d)
REPORT_FILE="/tmp/audit-review-$REVIEW_DATE.txt"

echo "InfraFabric Audit Log Review - $REVIEW_DATE" > $REPORT_FILE
echo "Generated: $(date)" >> $REPORT_FILE
echo "---" >> $REPORT_FILE

# 1. Security events summary
echo "=== SECURITY EVENTS ===" >> $REPORT_FILE
echo "Rate limit violations: $(grep -c "rate_limit_exceeded" logs/audit.log)" >> $REPORT_FILE
echo "Prompt injection attempts: $(grep -c "prompt_injection_detected" logs/audit.log)" >> $REPORT_FILE
echo "Failed authentications: $(grep -c '"success": false' logs/audit.log)" >> $REPORT_FILE
echo "IF.guard veto decisions: $(grep -c '"event_type": "veto"' logs/audit.log)" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 2. Access patterns
echo "=== ACCESS PATTERNS ===" >> $REPORT_FILE
echo "Total requests: $(wc -l < logs/access.log)" >> $REPORT_FILE
echo "Unique IPs: $(awk '{print $1}' logs/access.log | sort | uniq | wc -l)" >> $REPORT_FILE
echo "Average response time: $(awk '{sum+=$NF; count++} END {print sum/count "ms"}' logs/access.log)" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 3. Top users
echo "=== TOP USERS ===" >> $REPORT_FILE
grep "user_id" logs/audit.log | jq -r '.user_id' | sort | uniq -c | sort -rn | head -10 >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 4. Suspicious activity
echo "=== SUSPICIOUS ACTIVITY ===" >> $REPORT_FILE
# Failed logins from multiple IPs
echo "Multiple failed logins:" >> $REPORT_FILE
grep '"success": false' logs/audit.log | jq -r '.user_id' | sort | uniq -c | awk '$1 > 5 {print}' >> $REPORT_FILE

# Rate limit violations
echo "Rate limit violations:" >> $REPORT_FILE
grep "rate_limit_exceeded" logs/audit.log | jq -r '.source_ip' | sort | uniq -c | sort -rn | head -5 >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 5. System health indicators
echo "=== SYSTEM HEALTH ===" >> $REPORT_FILE
echo "Redis connectivity: $(redis-cli -h $REDIS_HOST PING 2>/dev/null || echo 'FAILED')" >> $REPORT_FILE
echo "ChromaDB connectivity: $(curl -s http://localhost:8000/api/v1/heartbeat | jq '.status' 2>/dev/null || echo 'FAILED')" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 6. Recommendations
echo "=== RECOMMENDATIONS ===" >> $REPORT_FILE
if grep -q "rate_limit_exceeded" logs/audit.log; then
  echo "- Review rate limiting policy" >> $REPORT_FILE
fi
if grep -q "prompt_injection_detected" logs/audit.log; then
  echo "- Review input sanitization patterns" >> $REPORT_FILE
fi
if [ $(grep -c '"success": false' logs/audit.log) -gt 100 ]; then
  echo "- Investigate high authentication failure rate" >> $REPORT_FILE
fi

# Send report
echo ""
echo "Audit review report saved to: $REPORT_FILE"
echo ""
cat $REPORT_FILE

# Email report
mail -s "Daily Audit Report - $REVIEW_DATE" ops@your-domain.com < $REPORT_FILE

# Archive report
gzip $REPORT_FILE
gsutil cp ${REPORT_FILE}.gz gs://audit-reports/
```

---

## PERFORMANCE OPTIMIZATION

### Redis Tuning

```bash
# Optimize Redis configuration

# 1. Memory policy (LRU eviction)
redis-cli CONFIG SET maxmemory-policy allkeys-lru
redis-cli CONFIG SET maxmemory 8gb  # Adjust to your server RAM
redis-cli CONFIG REWRITE  # Persist changes

# 2. Persistence optimization
redis-cli CONFIG SET save "900 1 300 10 60 10000"  # RDB snapshot strategy
redis-cli CONFIG SET appendonly yes  # Enable AOF
redis-cli CONFIG SET appendfsync everysec  # Balance durability/performance

# 3. Connection pool tuning
redis-cli CONFIG SET maxclients 10000
redis-cli CONFIG SET tcp-keepalive 300

# 4. Replication (if using master-slave)
redis-cli CONFIG SET min-slaves-to-write 1
redis-cli CONFIG SET min-slaves-max-lag 10

# 5. Benchmark performance
redis-benchmark -h $REDIS_HOST -p $REDIS_PORT -c 50 -n 100000
# Expected: >50,000 operations/sec for basic operations

# 6. Monitor slow commands
redis-cli CONFIG SET slowlog-log-slower-than 10000  # Log commands >10ms
redis-cli SLOWLOG GET 20  # View slow commands

# 7. Clear evicted keys analysis
redis-cli INFO stats | grep evicted_keys  # Monitor evictions
# If high, increase maxmemory or reduce key TTL
```

### ChromaDB Tuning

```bash
# Optimize ChromaDB configuration in config/chromadb.yaml

persistent:
  provider: disk
  directory: /data/.chroma

server:
  host: 0.0.0.0
  port: 8000
  max_body_size_bytes: 41943040  # 40MB

embeddings:
  provider: sentence-transformers
  model: all-MiniLM-L6-v2

# HNSW Index optimization
hnsw:
  space: cosine
  ef_construction: 200  # Higher = slower indexing, better search
  ef_search: 100  # Search parameter
  max_m: 16
  seed: 42

# Batch settings
batch:
  size: 1000  # Process 1000 embeddings per batch

# Query caching
cache:
  enabled: true
  max_size: 10000

# Benchmarks:
# - Single query: <300ms first call, <50ms cached
# - Batch embeddings: 100 documents in <2 seconds
# - Rebuild index: Full scan in <10 minutes (if <10M embeddings)
```

### Token Refresh Optimization

```python
# Pre-emptive token refresh (before expiration)

import time
from datetime import datetime, timedelta

class TokenRefreshOptimizer:
    def __init__(self, token_expiry_seconds=3600):
        self.token_expiry = token_expiry_seconds
        self.refresh_threshold = 900  # Refresh 15 min before expiry
        self.last_refresh_time = None

    def should_refresh(self, current_time):
        """Check if token should be refreshed"""
        time_until_expiry = self.token_expiry - (current_time - self.last_refresh_time)
        return time_until_expiry < self.refresh_threshold

    def refresh_token_async(self):
        """Refresh token in background thread"""
        import threading
        thread = threading.Thread(target=self._do_refresh)
        thread.daemon = True
        thread.start()

    def _do_refresh(self):
        """Perform token refresh"""
        # Call OAuth provider
        new_token = self._call_refresh_endpoint()
        self.last_refresh_time = time.time()
        return new_token

# Example usage:
# optimizer = TokenRefreshOptimizer()
# if optimizer.should_refresh(current_time):
#     optimizer.refresh_token_async()  # Non-blocking refresh
```

---

## CAPACITY PLANNING

### Resource Scaling Thresholds

| Resource | Threshold | Action |
|----------|-----------|--------|
| **CPU Usage** | 70% | Add 2 cores |
| **Memory Usage** | 80% | Add 4GB RAM |
| **Redis Memory** | 80% | Increase maxmemory or clean old keys |
| **ChromaDB Disk** | 80% | Archive embeddings or expand storage |
| **Network Bandwidth** | 70% | Upgrade connection or implement caching |
| **Open Connections** | 80% | Increase maxclients or add server |

### Cost Estimation Model

```python
def estimate_monthly_cost(
    num_users=100,
    avg_requests_per_user_per_day=10,
    avg_tokens_per_request=2000,
    model_mix={'sonnet': 0.7, 'haiku': 0.2, 'opus': 0.1}
):
    """Estimate monthly InfraFabric costs"""

    # Claude Max API costs (as of Nov 2025)
    costs_per_million_tokens = {
        'sonnet': 3.00,  # Input
        'haiku': 0.08,
        'opus': 15.00,
    }

    daily_requests = num_users * avg_requests_per_user_per_day
    monthly_requests = daily_requests * 30
    monthly_tokens = monthly_requests * avg_tokens_per_request

    # Calculate cost by model
    total_cost = 0
    for model, proportion in model_mix.items():
        model_tokens = monthly_tokens * proportion
        model_cost = (model_tokens / 1_000_000) * costs_per_million_tokens[model]
        print(f"{model}: {model_tokens:,} tokens = ${model_cost:.2f}")
        total_cost += model_cost

    # Infrastructure costs
    infrastructure_cost = {
        'redis_cloud': 100,  # Monthly for 2GB cluster
        'chromadb_disk': 50,  # 100GB SSD
        'compute': 200,  # 4-core server
        'cdn': 50,  # Static assets
        'monitoring': 100,  # Prometheus/Grafana
    }

    total_infrastructure = sum(infrastructure_cost.values())

    print(f"\nClaude API Cost: ${total_cost:.2f}")
    print(f"Infrastructure Cost: ${total_infrastructure:.2f}")
    print(f"Total Monthly Cost: ${total_cost + total_infrastructure:.2f}")

    return {
        'api_cost': total_cost,
        'infrastructure_cost': total_infrastructure,
        'total': total_cost + total_infrastructure,
        'cost_per_user_per_month': (total_cost + total_infrastructure) / num_users
    }

# Example:
# cost = estimate_monthly_cost(
#     num_users=500,
#     avg_requests_per_user_per_day=20,
#     model_mix={'sonnet': 0.6, 'haiku': 0.3, 'opus': 0.1}
# )
```

### User Growth Projections

```
Month 1:   100 users   @ 50 req/day = 5,000 req/month
Month 3:   500 users   @ 60 req/day = 900,000 req/month
Month 6:   2,000 users @ 70 req/day = 4,200,000 req/month
Month 12:  5,000 users @ 80 req/day = 12,000,000 req/month

Scaling timeline:
- Month 0-2: Single server (2 cores, 8GB)
- Month 2-4: Horizontal scaling (3 servers, Redis cluster)
- Month 4-8: Multi-region (3 regions, 2 servers each)
- Month 8+: Full production setup (10+ servers, managed services)
```

---

## MAINTENANCE WINDOWS

### Scheduled Maintenance Procedures

#### Weekly Maintenance (Sunday 2:00 AM UTC)

```bash
#!/bin/bash
# weekly_maintenance.sh

START_TIME=$(date +%s)
MAINTENANCE_LOG="logs/maintenance-$(date +%Y%m%d).log"

{
  echo "=== Weekly Maintenance Start: $(date) ==="

  # Step 1: Health check
  echo "1. Running system health checks..."
  docker-compose exec redis redis-cli PING
  docker-compose exec chromadb curl http://localhost:8000/api/v1/heartbeat
  curl http://localhost:8080/api/v1/status

  # Step 2: Verify backups
  echo "2. Verifying backups..."
  gsutil ls gs://your-backup-bucket/daily/ | tail -7

  # Step 3: Check for errors
  echo "3. Reviewing error logs..."
  tail -100 logs/error.log | grep -i "error\|exception\|failed"

  # Step 4: Update dependencies (patch only)
  echo "4. Updating patch versions..."
  pip list --outdated | grep -E "redis|pydantic|anthropic" | awk '{print $1}' | xargs pip install --upgrade

  # Step 5: Rotate logs
  echo "5. Rotating logs..."
  logrotate /etc/logrotate.d/infrafabric.conf

  # Step 6: Cleanup old data
  echo "6. Cleaning up old temporary files..."
  find /tmp -name "infrafabric-*" -mtime +7 -delete

  # Step 7: Database maintenance
  echo "7. Running database maintenance..."
  redis-cli BGSAVE  # Create snapshot
  redis-cli BGREWRITEAOF  # Compress AOF

  # Step 8: Security audit
  echo "8. Running security audit..."
  grep "veto\|blocked\|failed" logs/audit.log | tail -10

  END_TIME=$(date +%s)
  DURATION=$((END_TIME - START_TIME))
  echo "=== Weekly Maintenance Complete (${DURATION}s) ==="

} | tee -a $MAINTENANCE_LOG

# Email report
mail -s "Weekly Maintenance Report" ops@your-domain.com < $MAINTENANCE_LOG
```

#### Monthly Maintenance (1st Sunday of month, 2:00 AM UTC)

```bash
#!/bin/bash
# monthly_maintenance.sh

{
  echo "=== Monthly Maintenance Start: $(date) ==="

  # Step 1: Security audit
  echo "1. Performing security audit..."
  ./scripts/audit_log_review.sh

  # Step 2: Check for vulnerabilities
  echo "2. Scanning for known vulnerabilities..."
  pip-audit  # Check Python packages
  docker images --digests | xargs trivy image  # Check container images

  # Step 3: Performance analysis
  echo "3. Analyzing performance trends..."
  prometheus-cli --query 'rate(http_request_duration_seconds_bucket[30d])' > /tmp/perf-report.txt

  # Step 4: Capacity planning
  echo "4. Reviewing capacity planning..."
  du -sh ./data/.chroma
  redis-cli INFO memory | grep used_memory_human
  df -h /data

  # Step 5: Ed25519 key check
  echo "5. Verifying signing keys..."
  ls -la config/keys/signing_key.pem
  # If key is >1 month old and next quarter rotation is approaching

  # Step 6: Major dependency updates
  echo "6. Checking for major updates..."
  pip list --outdated

  # Step 7: Disaster recovery drill
  echo "7. Testing disaster recovery procedures..."
  ./scripts/test_restore_procedures.sh

  # Step 8: Full system test
  echo "8. Running full system tests..."
  python -m pytest tests/integration/ -v

  echo "=== Monthly Maintenance Complete ==="

} | tee logs/monthly-maintenance-$(date +%Y%m%d).log
```

### Zero-Downtime Deployment

```bash
#!/bin/bash
# zero_downtime_deploy.sh <new-version>

NEW_VERSION=$1
CURRENT_VERSION=$(cat VERSION)

if [ -z "$NEW_VERSION" ]; then
  echo "Usage: ./zero_downtime_deploy.sh <version>"
  exit 1
fi

echo "Deploying $CURRENT_VERSION → $NEW_VERSION (zero-downtime)"

# Step 1: Create blue-green deployment
echo "Step 1: Creating new deployment (green)..."
docker-compose -f docker-compose.blue.yml up -d
# Blue is the current prod environment

docker-compose -f docker-compose.green.yml up -d
# Green is the new version
# Update image version in docker-compose.green.yml first

# Step 2: Run smoke tests on green
echo "Step 2: Testing green environment..."
for i in {1..5}; do
  curl -f http://localhost:8081/api/v1/status || exit 1
done

# Step 3: Warm up green (cache priming)
echo "Step 3: Warming up green environment..."
# Make sample requests to populate caches
python scripts/warmup_cache.py

# Step 4: Monitor green health
echo "Step 4: Monitoring green environment (10s)..."
sleep 10

# Step 5: Switch traffic (nginx)
echo "Step 5: Switching traffic to green..."
# Edit nginx config to point to new backend
sed -i 's/server localhost:8080;/server localhost:8081;/g' /etc/nginx/conf.d/infrafabric.conf
nginx -s reload

# Step 6: Verify traffic switch
echo "Step 6: Verifying traffic switched successfully..."
sleep 5
for i in {1..10}; do
  curl -f http://localhost:8080/api/v1/status || exit 1
done

# Step 7: Shutdown blue (old version)
echo "Step 7: Shutting down blue environment..."
sleep 60  # Wait for graceful drain
docker-compose -f docker-compose.blue.yml down

# Step 8: Update blue for next deployment
echo "Step 8: Preparing blue for next deployment..."
docker-compose -f docker-compose.blue.yml pull
# Update VERSION file
echo $NEW_VERSION > VERSION

echo "✅ Deployment complete! $NEW_VERSION is now live."
```

### Rolling Updates

```bash
#!/bin/bash
# rolling_update.sh (for Kubernetes)

DEPLOYMENT="open-webui"
NAMESPACE="infrafabric"
NEW_IMAGE="ghcr.io/open-webui/open-webui:v1.2.3"

echo "Starting rolling update of $DEPLOYMENT..."

# Set update strategy
kubectl patch deployment $DEPLOYMENT -n $NAMESPACE -p \
  '{"spec":{"strategy":{"type":"RollingUpdate","rollingUpdate":{"maxSurge":1,"maxUnavailable":0}}}}'

# Perform update
kubectl set image deployment/$DEPLOYMENT \
  $DEPLOYMENT=$NEW_IMAGE -n $NAMESPACE

# Monitor rollout
kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE

# Verify
echo "Verifying deployment..."
kubectl get pods -n $NAMESPACE | grep $DEPLOYMENT
```

### Rollback Procedures

```bash
#!/bin/bash
# rollback.sh - Rollback failed deployment

VERSION=$1

if [ -z "$VERSION" ]; then
  echo "Available versions:"
  ls -1 data/backups/deployments/
  exit 1
fi

echo "Rolling back to version: $VERSION"

# Step 1: Verify rollback point exists
if [ ! -d "data/backups/deployments/$VERSION" ]; then
  echo "ERROR: Version $VERSION not found"
  exit 1
fi

# Step 2: Stop current services
echo "Stopping current services..."
docker-compose down

# Step 3: Restore data (if needed)
echo "Restoring databases..."
docker-compose -f docker-compose.$VERSION.yml up -d redis chromadb

# Wait for services to be ready
sleep 10

# Step 4: Restore container images
echo "Restoring container images..."
docker-compose -f docker-compose.$VERSION.yml pull

# Step 5: Start previous version
echo "Starting previous version..."
docker-compose -f docker-compose.$VERSION.yml up -d

# Step 6: Verify rollback
echo "Verifying rollback..."
for i in {1..5}; do
  curl -f http://localhost:8080/api/v1/status && break
  sleep 2
done

# Step 7: Notify team
echo "Rollback to $VERSION complete at $(date)" | \
  mail -s "ALERT: Deployment Rolled Back" ops@your-domain.com

echo "✅ Rollback complete!"
```

---

## RUNBOOKS

### Runbook 1: Weekly Maintenance

**Time Required:** 30 minutes
**Frequency:** Every Sunday 2:00 AM UTC
**Owner:** DevOps Engineer

#### Pre-Maintenance Checklist
- [ ] Notify team of planned maintenance window
- [ ] Verify backup status (recent backup exists)
- [ ] Ensure on-call engineer is available

#### Steps

1. **Health Check (5 min)**
   ```bash
   docker-compose exec redis redis-cli PING
   docker-compose exec chromadb curl -s http://localhost:8000/api/v1/heartbeat
   curl -s http://localhost:8080/api/v1/status
   ```

2. **Backup Verification (5 min)**
   ```bash
   gsutil ls -h gs://your-backup-bucket/daily/ | tail -7
   ```

3. **Log Analysis (5 min)**
   ```bash
   tail -100 logs/error.log | wc -l  # Count errors
   tail -100 logs/audit.log | grep "veto\|blocked" | wc -l  # Security events
   ```

4. **Dependency Updates (5 min)**
   ```bash
   pip install --upgrade -U -r requirements.txt  # Patch versions only
   ```

5. **Database Optimization (5 min)**
   ```bash
   redis-cli BGSAVE
   redis-cli BGREWRITEAOF
   ```

#### Post-Maintenance
- [ ] Verify all services running
- [ ] Check error logs for new issues
- [ ] Send summary email to team

---

### Runbook 2: Redis Failure Recovery

**Time Required:** 5-15 minutes
**Severity:** P0 (Critical)
**Owner:** DevOps Engineer

#### Detection
- Alert: `RedisCriticalMemory` or `RedisConnectionFailure`
- Manual: `redis-cli PING` returns error

#### Immediate Response (< 2 min)

```bash
# 1. Verify Redis status
docker ps | grep redis
redis-cli -h $REDIS_HOST -p $REDIS_PORT PING

# 2. Check Redis logs
docker logs infrafabric-redis-l1 | tail -50

# 3. Check system resources
free -h
docker stats --no-stream
```

#### Recovery (< 10 min)

**Option A: Service Restart**
```bash
# If Redis is hung
docker-compose restart redis-l1
# Wait for healthcheck to pass
docker-compose logs redis-l1 | grep "healthcheck"
```

**Option B: Cluster Failover**
```bash
# If using Redis Cluster
redis-cli CLUSTER FAILOVER
# Wait for slaves to be promoted
redis-cli CLUSTER NODES
```

**Option C: Restore from Backup**
```bash
# If data corruption suspected
./scripts/recover.sh /path/to/latest/backup.tar.gz
```

#### Verification

```bash
# 1. Connectivity
redis-cli -h $REDIS_HOST PING

# 2. Data integrity
redis-cli DBSIZE  # Compare with pre-failure size

# 3. Application health
curl http://localhost:8080/api/v1/status
```

#### Post-Recovery
- [ ] Verify chat functionality works
- [ ] Check error logs
- [ ] Update incident ticket
- [ ] Review failure cause

---

### Runbook 3: Emergency DDoS Response

**Time Required:** 2-5 minutes
**Severity:** P1 (High)
**Owner:** Security Engineer / DevOps

#### Detection
- Alert: `HighErrorRate` > 5% or `RateLimitExceeded` > 100/min
- Sign: Spike in `source_ip` diversity in logs

#### Immediate Mitigation (< 1 min)

```bash
# 1. Enable aggressive rate limiting
redis-cli SET rate_limit:global:requests_per_minute 10
redis-cli SET rate_limit:global:per_ip 100

# 2. Identify attack source
grep "rate_limit_exceeded" logs/audit.log | tail -100 | \
  jq -r '.source_ip' | sort | uniq -c | sort -rn | head -10

# 3. Block top attack IPs (temporary)
for ip in 203.0.113.45 203.0.113.46; do
  sudo iptables -A INPUT -s $ip -j DROP
done
```

#### Enhanced Defense (< 5 min)

```bash
# 4. Limit concurrent connections
redis-cli CONFIG SET maxclients 100
redis-cli CONFIG SET slowlog-log-slower-than 100

# 5. Enable request caching
redis-cli SET cache:enable 1

# 6. Scale horizontally if available
docker-compose up -d --scale open-webui=3

# 7. Enable Cloudflare/DDoS service (if configured)
# Manually enable DDoS protection in cloud provider
```

#### Monitoring During Attack

```bash
# Watch error rate
watch 'curl -s http://localhost:8080/api/v1/metrics | grep http_requests_total'

# Monitor connections
watch 'netstat -an | grep ESTABLISHED | wc -l'

# Review attack pattern
tail -f logs/audit.log | grep rate_limit
```

#### Post-Attack Analysis

```bash
# 1. Document attack details
echo "Attack analysis" > /tmp/ddos-report-$(date +%Y%m%d-%H%M%S).txt
grep "rate_limit_exceeded" logs/audit.log | \
  jq '{timestamp, source_ip, endpoint}' >> /tmp/ddos-report-*.txt

# 2. Identify changes needed
# - Adjust rate limits
# - Update WAF rules
# - Consider DDoS service upgrade

# 3. Report to team
mail -s "DDoS Attack Report" security@your-domain.com < /tmp/ddos-report-*.txt
```

---

### Runbook 4: Security Incident Response

**Time Required:** 15-60 minutes
**Severity:** P0 (Critical)
**Owner:** Security Engineer / Incident Commander

#### Incident Types

1. **Prompt Injection Attack**
2. **Unauthorized Data Access**
3. **Service Compromise**
4. **Data Breach**

#### Initial Response (< 5 min)

```bash
# 1. Activate incident response team
# - Incident commander
# - Security engineer
# - DevOps engineer
# - Communications officer

# 2. Create incident channel (Slack/Teams)
# #incident-2025-11-30-security-breach

# 3. Begin logging
INCIDENT_ID="INC-$(date +%Y%m%d-%H%M%S)"
INCIDENT_LOG="/tmp/incident-$INCIDENT_ID.log"
echo "Incident ID: $INCIDENT_ID" > $INCIDENT_LOG

# 4. Preserve evidence
cp logs/* /tmp/incident-evidence-$INCIDENT_ID/
```

#### Containment (< 30 min)

```bash
# For Prompt Injection Attack:
./scripts/block_attacker.sh <user_id> <ip_address>
redis-cli SET "user:$user_id:blocked" 1 EX 86400

# For Unauthorized Access:
./scripts/revoke_all_sessions.sh
redis-cli FLUSHALL  # Force re-authentication

# For Suspected Breach:
# 1. Take server offline (optional, depends on severity)
# 2. Snapshot all data
# 3. Preserve audit logs
```

#### Investigation (30-60 min)

```bash
# 1. Timeline reconstruction
grep "timestamp" logs/audit.log | sort > /tmp/timeline.txt

# 2. Affected data identification
# - Check accessed resources
# - Identify exposed information

# 3. Attacker identification
# - IP address geolocation
# - Account investigation
# - Threat actor profiling

# 4. Impact assessment
# - Number of affected users
# - Data sensitivity
# - Regulatory implications
```

#### Recovery & Communication

```bash
# 1. Restore from clean backup
./scripts/recover.sh /path/to/clean-backup.tar.gz

# 2. Enhance security
# - Force password resets
# - Rotate API keys
# - Review access controls

# 3. Communicate incident
# - User notification (if applicable)
# - Regulatory reporting (if required)
# - Media response
```

#### Post-Incident

```bash
# 1. Complete incident report
./scripts/generate_incident_report.sh $INCIDENT_ID

# 2. Root cause analysis
# - Why did this happen?
# - What could have prevented it?

# 3. Implement improvements
# - New monitoring rules
# - Updated controls
# - Enhanced testing

# 4. Team debrief
# - What went well?
# - What could be improved?
```

---

## INCIDENT RESPONSE

### Incident Severity Levels

| Severity | Definition | Response Time | SLA |
|----------|-----------|---|---|
| **P0 - Critical** | Service down, data breach risk | < 5 min | < 1 hour |
| **P1 - High** | Significant impact, degradation | < 15 min | < 4 hours |
| **P2 - Medium** | Limited impact, workaround exists | < 1 hour | < 24 hours |
| **P3 - Low** | Minimal impact, can defer | < 8 hours | < 72 hours |

### On-Call Escalation

```
Primary (0-15 min) → Secondary (15-30 min) → Manager (30+ min)
```

### Incident Communication Template

```
INCIDENT NOTIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Incident ID:    INC-2025-11-30-001
Severity:       P1 (High)
Status:         INVESTIGATING
Detected:       2025-11-30 14:30 UTC
Duration:       15 minutes

Impact:
- Chat functionality unavailable
- Affects ~500 active users
- No data loss expected

Root Cause:
- Under investigation

Next Update:
2025-11-30 14:45 UTC
```

### Escalation Contacts

```
Tier 1 (DevOps Engineer):
  - Primary: john@your-domain.com
  - Secondary: jane@your-domain.com
  - On-call calendar: https://oncall.your-domain.com

Tier 2 (Engineering Manager):
  - Contact: manager@your-domain.com
  - Phone: +1-555-0100

Tier 3 (CTO):
  - Contact: cto@your-domain.com
  - Phone: +1-555-0101

External Contacts:
  - AWS Support: https://console.aws.amazon.com/support
  - Anthropic Support: support@anthropic.com
```

---

## APPENDIX: Quick Reference

### Critical Commands

```bash
# Service Control
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
docker-compose restart        # Restart services
docker-compose logs -f        # View logs

# Redis Management
redis-cli PING                # Test connection
redis-cli DBSIZE              # Check key count
redis-cli FLUSHDB             # Clear current DB (WARNING)
redis-cli MONITOR             # Watch all commands
redis-cli INFO                # System info

# ChromaDB Management
curl http://localhost:8000/api/v1/heartbeat  # Health check
curl http://localhost:8000/api/v1/collections  # List collections

# Backups
./scripts/backup.sh           # Create backup
./scripts/recover.sh backup-file.tar.gz  # Restore backup

# Monitoring
docker stats                  # Real-time stats
prometheus_cli query http_request_latency  # Query metrics
```

### Key Files

```
.env                          # Environment variables (NEVER commit!)
config/infrafabric.schema.json  # Configuration schema
docker-compose.yml            # Service definitions
logs/audit.log                # Security audit trail
logs/error.log                # Error log
data/.chroma/                 # ChromaDB storage
```

### Important URLs

```
OpenWebUI:      http://localhost:8080
Prometheus:     http://localhost:9090
Grafana:        http://localhost:3000
Redis Commander: http://localhost:8081 (debug only)
```

---

**Document Version:** 1.0.0

**Last Updated:** November 30, 2025

**Next Review:** May 30, 2026

**Owner:** DevOps / Operations Team

**Citation:** `if://doc/operations-manual/2025-11-30`

**Status:** APPROVED FOR PRODUCTION

---
