# Session Handover: Sergio Chatbot Clone Project
**Date:** 2025-11-29
**Session Type:** Context Transition (Sergio Chatbot Implementation)
**Next Session Priority:** Haiku-first workflow (80% token savings)
**IF.optimise:** ACTIVE ⚡

---

## 📋 QUICK CONTEXT (Read This First)

**What We're Building:**
AI chatbot clone of Sergio (psychologist, emosocial methodology specialist). The bot will:
1. Respond AS Sergio (personality, thinking patterns, frameworks)
2. Conduct research FOR Sergio (cross-reference psychology + Eastern philosophy)
3. Maintain IF.TTT compliance (zero mis-attributions, full citations)

**Current Status:** Phase 1 (Data Preparation) - 40% complete

**Immediate Next Steps:**
1. ChromaDB setup (Haiku agent)
2. Sergio corpus chunking and embedding (Haiku agent)
3. Psychology corpus ingestion when ready (Haiku agent)
4. Personality DNA extraction (Sonnet)

---

## 🎯 WHAT'S BEEN COMPLETED

### Research & Architecture (2025-11-29)
- ✅ Comprehensive chatbot personality cloning research
  - Best practices: RAG + fine-tuning hybrid
  - Pitfalls: Uncanny valley, hallucination, mis-attribution
  - Success examples: Replika, Character.AI
  - **Report location:** See conversation history

- ✅ Sergio data inventory (25,000+ words)
  - Conference transcript (18K words)
  - IF.intelligence analysis (5,149 lines across 5 documents)
  - **Locations:** See SERGIO_CHATBOT_ROADMAP.md

- ✅ ChromaDB architecture designed
  - 4 collections: sergio_primary, sergio_frameworks, psychology_corpus, eastern_philosophy
  - JSON schema for attribution tracking
  - **Schema:** See roadmap document

- ✅ Psychology corpus structure (10 verticals)
  - Tier 1: Existential, Systems, Relational, Neurodiversity
  - Tier 2: Critical Psychology
  - Tier 3: Eastern Philosophy (Buddhist, Taoist, Vedantic, Zen)
  - **Research prompt:** `/mnt/c/Users/Setup/Downloads/PSYCHOLOGY_CORPUS_RESEARCH_AGENT_PROMPT.md`

- ✅ Zero-context research agent prompt created
  - Comprehensive prompt for external agent (Google Colab)
  - Strict attribution rules (Sergio vs. corpus sources)
  - Expected output: 300-450 JSON citation records
  - **Status:** Running in parallel (external session)

---

## 📊 DATA INVENTORY

### Sergio Primary Sources (HIS WORK)

| File | Path | Size | Content |
|------|------|------|---------|
| Conference transcript | `/mnt/c/Users/Setup/Downloads/sergio-tanscript.txt` | 18K words | Methodology explanation |
| Three stories | `/mnt/c/Users/Setup/Downloads/SERGIO_TRES_HISTORIAS_TTS_OPTIMIZADO.txt` | 448 lines | Narrative examples |
| Asperger's guide (ES) | `/mnt/c/Users/Setup/Downloads/SERGIO_ASPERGERS_GUIA_AUDIO_ES.txt` | 836 lines | Spanish guidance |

### IF.intelligence Analysis (ABOUT HIS WORK)

| File | Path | Size | Content |
|------|------|------|---------|
| Asperger's Framework | `/home/setup/infrafabric/docs/demonstrations/SERGIO_ASPERGERS_FRAMEWORK_GUIDE_2025-11-29.md` | 1,505 lines | Bilingual framework |
| Emosocial Analysis | `/home/setup/infrafabric/docs/demonstrations/IF_INTELLIGENCE_EMOSOCIAL_ANALYSIS_2025-11-28.md` | 1,431 lines | Methodology breakdown |
| Valores Debate | `/home/setup/infrafabric/docs/demonstrations/IF_INTELLIGENCE_VALORES_DEBATE_2025-11-28.md` | 749 lines | Values discussion |
| Rory Sutherland Reframe | `/home/setup/infrafabric/docs/demonstrations/RORY_SUTHERLAND_REFRAMING_SERGIO_COUPLES_THERAPY_2025-11-28.md` | 747 lines | Behavioral economics |
| Neurodiversity Analysis | `/home/setup/infrafabric/docs/analyses/SERGIO_EMOSOCIAL_NEURODIVERSITY_ANALYSIS_2025-11-29.md` | 717 lines | Autism application |

**Total:** ~25,000 words ready for chunking and embedding

---

## 🚀 IMMEDIATE NEXT STEPS (Haiku-First)

### Task 1: ChromaDB Setup (HAIKU AGENT)
**Estimated tokens:** ~3K Haiku
**Estimated time:** 15-20 minutes

```python
# Deploy Haiku agent to execute:

import chromadb
from chromadb.config import Settings

# 1. Install ChromaDB if needed
!pip install chromadb

# 2. Initialize client
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="/home/setup/sergio_chatbot/chroma_db"
))

# 3. Create 4 collections
sergio_primary = client.create_collection(
    name="sergio_primary_sources",
    metadata={"description": "Sergio's original work"}
)

sergio_frameworks = client.create_collection(
    name="sergio_frameworks",
    metadata={"description": "IF.intelligence analysis of Sergio's frameworks"}
)

psychology_corpus = client.create_collection(
    name="psychology_corpus",
    metadata={"description": "External psychology texts aligned with Sergio"}
)

eastern_philosophy = client.create_collection(
    name="eastern_philosophy",
    metadata={"description": "Buddhist, Taoist, Vedantic, Zen texts"}
)

# 4. Verify collections created
print(f"Collections: {client.list_collections()}")
```

**Output:** ChromaDB initialized with 4 empty collections

---

### Task 2: Chunk Sergio Corpus (HAIKU AGENT)
**Estimated tokens:** ~5K Haiku
**Estimated time:** 20-30 minutes

```python
# Deploy Haiku agent to execute:

from langchain.text_splitter import RecursiveCharacterTextSplitter
import json

# 1. Read Sergio primary sources
files = [
    "/mnt/c/Users/Setup/Downloads/sergio-tanscript.txt",
    "/mnt/c/Users/Setup/Downloads/SERGIO_TRES_HISTORIAS_TTS_OPTIMIZADO.txt",
    "/mnt/c/Users/Setup/Downloads/SERGIO_ASPERGERS_GUIA_AUDIO_ES.txt"
]

# 2. Semantic chunking (not fixed-size)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # ~500 words per chunk
    chunk_overlap=100,  # Preserve context
    separators=["\n\n", "\n", ". ", " "]
)

chunks = []
for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        file_chunks = splitter.split_text(content)

        # Add metadata
        source_name = file_path.split('/')[-1]
        for i, chunk in enumerate(file_chunks):
            chunks.append({
                "id": f"{source_name}_chunk_{i:03d}",
                "text": chunk,
                "metadata": {
                    "source": source_name,
                    "chunk_index": i,
                    "is_sergio_original": True,
                    "language": "es" if "SERGIO" in source_name else "mixed"
                }
            })

# 3. Save chunks for embedding
with open('/home/setup/sergio_chatbot/sergio_chunks.json', 'w') as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print(f"Created {len(chunks)} chunks from Sergio's corpus")
```

**Output:** JSON file with ~50-80 semantically chunked passages

---

### Task 3: Generate Embeddings (HAIKU AGENT)
**Estimated tokens:** ~4K Haiku
**Estimated time:** 10-15 minutes

```python
# Deploy Haiku agent to execute:

import openai
import json

# 1. Load chunks
with open('/home/setup/sergio_chatbot/sergio_chunks.json', 'r') as f:
    chunks = json.load(f)

# 2. Generate embeddings (OpenAI ada-002)
openai.api_key = "YOUR_API_KEY"  # Use deepseek or OpenRouter

embedded_chunks = []
for chunk in chunks:
    response = openai.Embedding.create(
        input=chunk["text"],
        model="text-embedding-ada-002"
    )
    embedding = response['data'][0]['embedding']

    chunk["embedding"] = embedding
    embedded_chunks.append(chunk)

# 3. Save embedded chunks
with open('/home/setup/sergio_chatbot/sergio_chunks_embedded.json', 'w') as f:
    json.dump(embedded_chunks, f)

print(f"Generated embeddings for {len(embedded_chunks)} chunks")
```

**Output:** Embedded chunks ready for ChromaDB ingestion

---

### Task 4: Load into ChromaDB (HAIKU AGENT)
**Estimated tokens:** ~3K Haiku
**Estimated time:** 10 minutes

```python
# Deploy Haiku agent to execute:

import chromadb
import json

# 1. Load client
client = chromadb.Client(Settings(
    persist_directory="/home/setup/sergio_chatbot/chroma_db"
))

sergio_primary = client.get_collection("sergio_primary_sources")

# 2. Load embedded chunks
with open('/home/setup/sergio_chatbot/sergio_chunks_embedded.json', 'r') as f:
    chunks = json.load(f)

# 3. Add to ChromaDB
sergio_primary.add(
    ids=[c["id"] for c in chunks],
    embeddings=[c["embedding"] for c in chunks],
    documents=[c["text"] for c in chunks],
    metadatas=[c["metadata"] for c in chunks]
)

print(f"Loaded {len(chunks)} chunks into sergio_primary_sources collection")
```

**Output:** ChromaDB Collection 1 populated with Sergio's work

---

### Task 5: Personality DNA Extraction (SONNET)
**Estimated tokens:** ~8K Sonnet
**Estimated time:** 30-45 minutes

**This requires Sonnet for complex linguistic analysis:**

1. **Read conference transcript** (full text)
2. **Extract personality markers:**
   - Big Five traits (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism)
   - Communication style (systematic, anti-abstract, uses analogies)
   - Distinctive vocabulary (frequent words, rare terms, Spanish fillers)
   - Sentence structures (length, complexity, punctuation patterns)
3. **Design system prompt:**
   - Encode 7 core frameworks
   - Bilingual capabilities
   - Guardrails (never use abstract vague language)
4. **Create decision trees:** When to apply each framework

**Deliverable:** `/home/setup/sergio_chatbot/personality_dna.json` + system prompt

---

## ⚡ IF.OPTIMISE: Haiku vs. Sonnet Allocation

**Use Haiku for (70-80% of work):**
- [ ] ChromaDB setup and operations
- [ ] File I/O, parsing, data transformation
- [ ] Embedding generation
- [ ] Metadata extraction
- [ ] Cross-reference generation
- [ ] Citation tracking
- [ ] Psychology corpus ingestion (when ready)

**Use Sonnet for (20-30% of work):**
- [ ] Linguistic analysis (personality traits)
- [ ] System prompt design
- [ ] IF.guard council deliberations
- [ ] Complex cross-domain reasoning
- [ ] Final synthesis and quality validation

**Estimated Token Budget for Next Session:**
- Haiku: ~15K tokens (~$0.02)
- Sonnet: ~8K tokens (~$2.40)
- **Total: ~$2.42** (vs. $12 Sonnet-only)
- **Savings: 80%**

---

## 🚨 CRITICAL REMINDERS

### 1. Attribution Tracking
**ALWAYS maintain clear boundary:**
- **Sergio's work** = Primary sources + his original frameworks
- **IF.intelligence analysis** = Our analysis OF Sergio's work
- **Psychology corpus** = External sources that align with Sergio

**Never conflate sources.** Every chunk must have `is_sergio_original` flag.

### 2. Zero Mis-Attributions
Use this check before any claim:
```python
if "author" in metadata and metadata["author"] != "Sergio":
    attribution = f"According to {metadata['author']} ({metadata['year']})"
else:
    attribution = "Sergio's framework states"
```

### 3. Bilingual Capability
Sergio code-switches Spanish/English:
- Spanish for emotional/personal concepts
- English for technical/systematic analysis
- Natural transitions (not forced)

---

## 📁 FILE LOCATIONS

**Project Root:** `/home/setup/sergio_chatbot/`

**Key Files:**
- Roadmap: `/home/setup/infrafabric/SERGIO_CHATBOT_ROADMAP.md`
- This handover: `/home/setup/infrafabric/SESSION_HANDOVER_SERGIO_2025-11-29.md`
- Research agent prompt: `/mnt/c/Users/Setup/Downloads/PSYCHOLOGY_CORPUS_RESEARCH_AGENT_PROMPT.md`
- Sergio data: See inventory above
- ChromaDB: `/home/setup/sergio_chatbot/chroma_db/` (will be created)

**Psychology Corpus (Pending):**
- Location: `/home/setup/psychology_corpus/` (when external agent completes)
- Format: JSON files organized by vertical
- Expected: 300-450 citation records

---

## 🎯 SUCCESS CRITERIA FOR NEXT SESSION

By end of next session, we should have:
- ✅ ChromaDB initialized with 4 collections
- ✅ Sergio's corpus chunked, embedded, loaded into Collection 1
- ✅ Personality DNA extracted (Big Five traits, communication style)
- ✅ System prompt designed (bilingual, 7 frameworks, guardrails)
- ✅ Test query executed ("Transpose Sergio using Buddhist emptiness")

**Token usage:** Target < $3 (80% Haiku, 20% Sonnet)

---

## 💡 IF YOU'RE STARTING THE NEXT SESSION

**Read these files in order:**
1. This handover (SESSION_HANDOVER_SERGIO_2025-11-29.md)
2. Roadmap (SERGIO_CHATBOT_ROADMAP.md)
3. Research agent prompt (PSYCHOLOGY_CORPUS_RESEARCH_AGENT_PROMPT.md)

**Then deploy Haiku agents for:**
1. ChromaDB setup
2. Sergio corpus chunking
3. Embedding generation
4. Collection loading

**Use Sonnet only for:**
1. Personality DNA extraction
2. System prompt design
3. Final validation

**Token target:** $2-3 total

---

**Last Updated:** 2025-11-29
**Next Session:** Haiku-first ChromaDB setup + Sergio corpus ingestion
**IF.optimise Status:** ACTIVE ⚡ (80% savings target)
