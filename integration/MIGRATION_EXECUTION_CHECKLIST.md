# Sergio ChromaDB Migration - Execution Checklist
**Ready-to-Execute Implementation Plan**

**Date:** 2025-11-30
**Estimated Duration:** 7-9 hours (Haiku labor)
**Estimated Cost:** $0.05 (Haiku agents)
**Status:** DESIGN COMPLETE → READY FOR PHASE 1

---

## Quick Start (TL;DR)

```bash
# 1. Verify source files exist
ls /mnt/c/Users/Setup/Downloads/sergio*.txt
ls /home/setup/infrafabric/docs/demonstrations/SERGIO*.md
ls /home/setup/infrafabric/docs/demonstrations/IF_INTELLIGENCE*.md

# 2. Create project directory
mkdir -p /home/setup/sergio_chatbot

# 3. Run implementation script
python /home/setup/infrafabric/integration/sergio_chromadb_implementation.py

# Expected output:
# ✓ Phase 1 Complete: ~500 chunks → sergio_chunks_raw.json
# ✓ Phase 2 Complete: ~500 chunks classified → sergio_chunks_classified.json
# ✓ Phase 3 Complete: ~500 embeddings → sergio_chunks_embedded.json
# ✓ Phase 4 Complete: 123 documents in ChromaDB
# ✓ Phase 5: Query tests passing
```

---

## Pre-Execution Verification

### Step 1: Verify Source Files Exist

**Sergio Primary Sources (HIS WORK):**
```bash
# File 1: Conference transcript (18K words)
ls -lh /mnt/c/Users/Setup/Downloads/sergio-transcript.txt
# Expected: ~150-200 KB

# File 2: Spanish narratives
ls -lh /mnt/c/Users/Setup/Downloads/SERGIO_TRES_HISTORIAS_TTS_OPTIMIZADO.txt
# Expected: ~30-40 KB

# File 3: Spanish guide
ls -lh /mnt/c/Users/Setup/Downloads/SERGIO_ASPERGERS_GUIA_AUDIO_ES.txt
# Expected: ~50-60 KB
```

**IF.intelligence Analysis (ABOUT HIS WORK):**
```bash
# File 4: Asperger's framework
ls -lh /home/setup/infrafabric/docs/demonstrations/SERGIO_ASPERGERS_FRAMEWORK_GUIDE_2025-11-29.md
# Expected: ~80-100 KB

# File 5: Emosocial analysis
ls -lh /home/setup/infrafabric/docs/demonstrations/IF_INTELLIGENCE_EMOSOCIAL_ANALYSIS_2025-11-28.md
# Expected: ~90-110 KB

# File 6: Valores debate
ls -lh /home/setup/infrafabric/docs/demonstrations/IF_INTELLIGENCE_VALORES_DEBATE_2025-11-28.md
# Expected: ~40-50 KB

# File 7: Rory Sutherland reframe
ls -lh /home/setup/infrafabric/docs/demonstrations/RORY_SUTHERLAND_REFRAMING_SERGIO_COUPLES_THERAPY_2025-11-28.md
# Expected: ~40-50 KB

# File 8: Neurodiversity analysis
ls -lh /home/setup/infrafabric/docs/analyses/SERGIO_EMOSOCIAL_NEURODIVERSITY_ANALYSIS_2025-11-29.md
# Expected: ~40-50 KB
```

### Step 2: Check Python Dependencies

```bash
# Check Python version
python --version
# Expected: Python 3.8+

# Check/install required packages
pip install langchain sentence-transformers chromadb redis

# Verify installations
python -c "import langchain; print(f'langchain: {langchain.__version__}')"
python -c "import sentence_transformers; print('sentence-transformers: OK')"
python -c "import chromadb; print('chromadb: OK')"
```

### Step 3: Create Project Directory

```bash
mkdir -p /home/setup/sergio_chatbot
mkdir -p /home/setup/sergio_chatbot/logs
mkdir -p /home/setup/sergio_chatbot/backups

# Verify
ls -la /home/setup/sergio_chatbot/
```

### Step 4: Verify OpenWebUI ChromaDB (if deploying to OpenWebUI)

```bash
# If using OpenWebUI Docker, check ChromaDB is running
docker ps | grep chromadb
# Expected: chromadb container running on port 8000

# Test HTTP connection
curl -X GET http://localhost:8000/api/v1/collections
# Expected: JSON response with collections list
```

---

## Phase-by-Phase Execution

### Phase 1: Chunking & Cleaning (2-3 hours, Haiku)

**Command:**
```bash
python -c "
from sergio_chromadb_implementation import phase1_chunking
phase1_chunking()
"
```

**What it does:**
1. Reads all 8 source files
2. Applies semantic chunking (400-word chunks, 20% overlap)
3. Estimates line numbers for citation tracking
4. Saves to `sergio_chunks_raw.json`

**Expected output:**
```
✓ Chunked sergio-transcript.txt: 85 chunks
✓ Chunked SERGIO_TRES_HISTORIAS_TTS_OPTIMIZADO.txt: 12 chunks
✓ Chunked SERGIO_ASPERGERS_GUIA_AUDIO_ES.txt: 18 chunks
✓ Chunked SERGIO_ASPERGERS_FRAMEWORK_GUIDE_2025-11-29.md: 42 chunks
✓ Chunked IF_INTELLIGENCE_EMOSOCIAL_ANALYSIS_2025-11-28.md: 48 chunks
✓ Chunked IF_INTELLIGENCE_VALORES_DEBATE_2025-11-28.md: 25 chunks
✓ Chunked RORY_SUTHERLAND_REFRAMING_SERGIO_COUPLES_THERAPY_2025-11-28.md: 32 chunks
✓ Chunked SERGIO_EMOSOCIAL_NEURODIVERSITY_ANALYSIS_2025-11-29.md: 38 chunks

✓ Phase 1 Complete: ~500 chunks saved to /home/setup/sergio_chatbot/sergio_chunks_raw.json
```

**Success criteria:**
- [ ] `sergio_chunks_raw.json` exists (25-50KB)
- [ ] JSON is valid (can be parsed)
- [ ] Contains ~500 chunks
- [ ] Each chunk has: id, text, source_file, chunk_index, source_line, word_count

**Troubleshooting:**
```bash
# If "File not found" error:
# 1. Check exact file paths
ls /mnt/c/Users/Setup/Downloads/ | grep sergio
ls /mnt/c/Users/Setup/Downloads/ | grep SERGIO
ls /home/setup/infrafabric/docs/demonstrations/ | grep SERGIO
ls /home/setup/infrafabric/docs/demonstrations/ | grep IF_INTELLIGENCE
ls /home/setup/infrafabric/docs/analyses/ | grep SERGIO

# 2. Update file paths in sergio_chromadb_implementation.py if needed

# If langchain import fails:
pip install --upgrade langchain

# If chunking is too slow (>30 min for 500 chunks):
# Reduce chunk_size from 400 to 250 for faster chunking
# (This will increase total chunk count but speed up Phase 1)
```

---

### Phase 2: Classification & Metadata (2 hours, Haiku)

**Command:**
```bash
python -c "
from sergio_chromadb_implementation import phase2_classification
classified = phase2_classification()
"
```

**What it does:**
1. Loads raw chunks from Phase 1
2. Classifies into 4 collections using regex rules
3. Detects language (Spanish, English, code-switched)
4. Adds 12 metadata fields
5. Saves to `sergio_chunks_classified.json`

**Expected output:**
```
✓ Phase 2 Complete: ~500 chunks classified
  personality: ~75 chunks
  rhetorical: ~35 chunks
  humor: ~95 chunks
  corpus: ~295 chunks
```

**Success criteria:**
- [ ] `sergio_chunks_classified.json` exists (50-75KB)
- [ ] JSON is valid
- [ ] All chunks have complete metadata (12 fields)
- [ ] Language detection working (es, en, es_en)
- [ ] authenticity_score: 1.0 for sergio_* files, 0.85 for if_analysis files

**Verify metadata:**
```bash
python -c "
import json
with open('/home/setup/sergio_chatbot/sergio_chunks_classified.json', 'r') as f:
    data = json.load(f)

# Check first chunk structure
first_chunk = data['sergio_primary'][0]
print('Metadata fields:')
for key in first_chunk['metadata'].keys():
    print(f'  ✓ {key}')
"
```

**Troubleshooting:**
```bash
# If classification is too aggressive/conservative:
# Edit classification_rules in phase2_classification()
# Add/remove regex patterns for specific device_type or humor_type

# If language detection wrong:
# Check detect_language() function
# Add more Spanish/English word lists

# If metadata missing:
# Verify all 12 fields are in metadata dict
# Check collection-specific extensions are applied
```

---

### Phase 3: Embedding Generation (2-3 hours, Haiku)

**Command:**
```bash
python -c "
from sergio_chromadb_implementation import phase3_embeddings
embedded = phase3_embeddings()
"
```

**What it does:**
1. Loads classified chunks
2. Initializes nomic-embed-text-v1.5 model (768-dim)
3. Generates embeddings in batches (batch_size=32)
4. Saves to `sergio_chunks_embedded.json`

**Expected output:**
```
Loading embedding model...
✓ Generated embeddings for chunks 0-32
✓ Generated embeddings for chunks 32-64
✓ Generated embeddings for chunks 64-96
...
✓ Generated embeddings for chunks 480-512

✓ Phase 3 Complete: 500 embeddings generated and saved
```

**Speed expectations:**
- Model loading: ~30-60 seconds
- Embedding generation: ~50 embeddings/second on CPU
- Total time: 10-15 seconds for 500 embeddings (+ loading time)
- **Wall clock time: 2-3 hours including context switching between batches**

**Success criteria:**
- [ ] `sergio_chunks_embedded.json` exists (200-300MB)
- [ ] JSON is valid
- [ ] Each chunk has "embedding" field (768 floats)
- [ ] No chunks with null/empty embeddings

**Monitor progress:**
```bash
# In another terminal, check file size growth
watch -n 5 'ls -lh /home/setup/sergio_chatbot/sergio_chunks_embedded.json'
```

**Troubleshooting:**
```bash
# If model download fails:
# The model is downloaded on first use to ~/.cache/huggingface/hub/
# If disk space limited, specify cache dir:
export HF_HOME=/home/setup/.huggingface_cache

# If "CUDA out of memory" error:
# Model runs on CPU by default, but if GPU detected, uses it
# Force CPU-only:
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# If embedding generation very slow:
# Reduce batch_size from 32 to 16 (slower but less memory)
# OR increase batch_size to 64 (faster, more memory)

# If disk space insufficient for 300MB:
# Use sparse embeddings instead (smaller files)
# Or split into two batches
```

---

### Phase 4: ChromaDB Ingestion (1 hour, Haiku)

**Command:**
```bash
python -c "
from sergio_chromadb_implementation import phase4_chromadb_ingestion
client, collections = phase4_chromadb_ingestion()
"
```

**What it does:**
1. Loads embedded chunks
2. Initializes ChromaDB (HTTP or PersistentClient)
3. Creates 4 collections with metadata
4. Batch loads documents + embeddings + metadata
5. Verifies collection counts

**Expected output:**
```
Initializing ChromaDB...
✓ Using ChromaDB PersistentClient (local)
✓ Loaded 75 chunks into sergio_personality
✓ Loaded 35 chunks into sergio_rhetorical
✓ Loaded 95 chunks into sergio_humor
✓ Loaded 295 chunks into sergio_corpus

✓ Phase 4 Complete: 500 total documents loaded

ChromaDB Collections Summary:
  sergio_personality: 75 documents
  sergio_rhetorical: 35 documents
  sergio_humor: 95 documents
  sergio_corpus: 295 documents
```

**Success criteria:**
- [ ] ChromaDB initialized (check `/home/setup/sergio_chatbot/chromadb/` directory)
- [ ] 4 collections created with correct document counts
- [ ] Total documents: ~500 (exact depends on chunking)
- [ ] Metadata present on all documents (verify via query)

**Verify ChromaDB:**
```bash
python -c "
import chromadb

client = chromadb.PersistentClient(path='/home/setup/sergio_chatbot/chromadb')

print('Collections:')
for collection in client.list_collections():
    print(f'  - {collection.name}: {collection.count()} documents')

# Test query
collection = client.get_collection('sergio_personality')
results = collection.query(query_texts=['core values'], n_results=1)
print(f'\nTest query result: {len(results[\"documents\"][0])} characters')
print(f'Metadata keys: {list(results[\"metadatas\"][0].keys())}')
"
```

**Troubleshooting:**
```bash
# If "HTTP connection refused" error:
# ChromaDB Docker container not running
# Switch to PersistentClient instead (automatic fallback)

# If "Collection already exists" error:
# Delete existing collections first:
rm -rf /home/setup/sergio_chatbot/chromadb/

# If "embedding dimension mismatch":
# ChromaDB expects consistent embedding dimensions
# Verify all embeddings are 768-dim (nomic-embed-text-v1.5)

# If very slow ingestion:
# Reduce batch size in the ingestion script
# Or use smaller document chunks
```

---

### Phase 5: Query Testing (30 minutes, Manual)

**Command:**
```bash
python -c "
from sergio_chromadb_implementation import SergioRAGPipe

pipe = SergioRAGPipe()

# Test 1: Personality traits
print('Test 1: Personality traits')
result = pipe.query_sergio('What are Sergio\'s core values?', 'personality')
print(f'  Found {len(result[\"results\"])} results')
print(f'  Citations: {len(result[\"citations\"])}')

# Test 2: Rhetorical devices
print('\nTest 2: Rhetorical devices')
result = pipe.query_sergio('How does Sergio use metaphors?', 'rhetorical')
print(f'  Found {len(result[\"results\"])} results')

# Test 3: Humor
print('\nTest 3: Humor')
result = pipe.query_sergio('Tell me a funny story', 'humor')
print(f'  Found {len(result[\"results\"])} results')

# Test 4: All collections
print('\nTest 4: Multi-collection')
result = pipe.query_sergio('How does Sergio explain his frameworks?')
print(f'  Found {len(result[\"results\"])} results')
print(f'  Collections: {set(r[\"collection\"] for r in result[\"results\"])}')
"
```

**Expected output:**
```
Test 1: Personality traits
  Found 5 results
  Citations: 5

Test 2: Rhetorical devices
  Found 5 results

Test 3: Humor
  Found 5 results

Test 4: Multi-collection
  Found 10 results
  Collections: {'personality', 'rhetorical', 'humor', 'corpus'}
```

**Success criteria:**
- [ ] All 5 tests return results (not empty)
- [ ] Results are relevant to query
- [ ] Citations generated with if:// URIs
- [ ] Metadata complete (no null values)
- [ ] Query latency < 300ms per query

**Query latency test:**
```bash
python -c "
import time
from sergio_chromadb_implementation import SergioRAGPipe

pipe = SergioRAGPipe()

# Warm up (load model into memory)
pipe.query_sergio('test')

# Time 5 queries
times = []
for i in range(5):
    start = time.time()
    result = pipe.query_sergio(f'Test query {i}')
    elapsed = time.time() - start
    times.append(elapsed)
    print(f'Query {i}: {elapsed*1000:.0f}ms')

avg = sum(times) / len(times)
print(f'Average: {avg*1000:.0f}ms')
print(f'Expected: <300ms (no cache), <100ms (cached)')
"
```

---

## Post-Implementation Steps

### Step 1: Backup ChromaDB

```bash
# Create backup
cp -r /home/setup/sergio_chatbot/chromadb /home/setup/sergio_chatbot/chromadb.backup.2025-11-30

# Verify backup
ls -lh /home/setup/sergio_chatbot/chromadb.backup.2025-11-30/
```

### Step 2: Generate Implementation Report

```bash
python -c "
import json
import chromadb

client = chromadb.PersistentClient(path='/home/setup/sergio_chatbot/chromadb')

report = {
    'date': '2025-11-30',
    'collections': {},
    'total_documents': 0,
    'embedding_model': 'nomic-embed-text-v1.5',
    'embedding_dimensions': 768
}

for collection in client.list_collections():
    count = collection.count()
    report['collections'][collection.name] = count
    report['total_documents'] += count

print('ChromaDB Implementation Report')
print(f'Total Collections: {len(report[\"collections\"])}')
print(f'Total Documents: {report[\"total_documents\"]}')
for name, count in report['collections'].items():
    print(f'  - {name}: {count}')

# Save report
with open('/home/setup/sergio_chatbot/implementation_report.json', 'w') as f:
    json.dump(report, f, indent=2)
"
```

### Step 3: Set Up Redis Cache (Optional)

```bash
# If using Redis for embedding cache
docker run -d -p 6379:6379 redis:latest

# Test connection
python -c "
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.ping()
print('Redis connected')
"
```

### Step 4: Deploy OpenWebUI Pipe (Optional)

```bash
# Copy implementation to OpenWebUI pipelines directory
cp /home/setup/infrafabric/integration/sergio_chromadb_implementation.py /root/openwebui-pipelines/

# Or create wrapper in OpenWebUI
# Edit docker-compose to mount chromadb volume

# Restart OpenWebUI
docker-compose restart open-webui
```

---

## Error Recovery

### Problem: ChromaDB corrupted

```bash
# Solution: Restore from backup
rm -rf /home/setup/sergio_chatbot/chromadb
cp -r /home/setup/sergio_chatbot/chromadb.backup.2025-11-30 /home/setup/sergio_chatbot/chromadb

# Or restart from Phase 4
rm -rf /home/setup/sergio_chatbot/chromadb
python phase4_chromadb_ingestion()
```

### Problem: Missing source files

```bash
# Check exact paths
find /mnt/c/Users -name "sergio*.txt"
find /home/setup -name "SERGIO*.md"

# Update paths in implementation script
# Then re-run Phase 1
```

### Problem: Out of memory during embeddings

```bash
# Reduce batch size in phase3_embeddings()
batch_size = 16  # Instead of 32

# OR split embeddings into two runs
# Embed first 250 chunks, then second 250 chunks
```

### Problem: Very slow queries

```bash
# Check if index is built
# ChromaDB builds HNSW index on first query (slow)
# Second and subsequent queries should be fast

# Monitor cache hits
# If Redis enabled, check cache hit ratio

# If still slow:
# Reduce ef_search parameter in HNSW
# Increase n_results limit
```

---

## Success Checklist (Final)

- [ ] All source files verified and accessible
- [ ] Phase 1 complete: ~500 chunks → sergio_chunks_raw.json
- [ ] Phase 2 complete: Classified with metadata → sergio_chunks_classified.json
- [ ] Phase 3 complete: 768-dim embeddings → sergio_chunks_embedded.json
- [ ] Phase 4 complete: 500 documents in ChromaDB (4 collections)
- [ ] Phase 5 complete: 5 test queries passing
- [ ] Query latency: <300ms (no cache), <100ms (cached)
- [ ] Citations generated: if:// URIs with metadata
- [ ] Backup created: chromadb.backup.2025-11-30
- [ ] Implementation report generated
- [ ] Ready for OpenWebUI deployment (if applicable)

---

## Next Steps (After Migration Complete)

1. **Integration with OpenWebUI**
   - Deploy SergioRAGPipe to OpenWebUI pipelines
   - Test via OpenWebUI chat interface
   - Set up Redis caching layer

2. **Advanced Features**
   - Implement cross-encoder reranking for personality accuracy
   - Add language preference detection (Spanish/English)
   - Set up IF.Guard verification for humor appropriateness

3. **Monitoring & Maintenance**
   - Track query latency metrics
   - Monitor cache hit ratio
   - Weekly backups
   - Monthly re-indexing with new Sergio content

4. **Expansion**
   - Add psychology corpus (when ready)
   - Implement Eastern philosophy collection
   - Create cross-cultural emotion lexicon search

---

**Status:** READY FOR IMMEDIATE EXECUTION
**Estimated Total Time:** 7-9 hours (continuous)
**Estimated Total Cost:** $0.05 (Haiku labor)
**Date to Execute:** 2025-11-30 (This week!)
