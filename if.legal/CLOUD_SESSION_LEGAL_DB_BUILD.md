# CLOUD SESSION: Legal Document Database Build
## Handoff Plan for Claude Code Cloud Execution

**Mission:** Download legal documents from official sources and integrate into self-hosted local vector database.

**Constraints:**
- Using Claude Code CLI (not SDK)
- Self-hosted vector DB (Chroma - Pinecone has no local option)
- Target: Contract analysis reference corpus

---

## PHASE 1: ENVIRONMENT SETUP

### 1.1 Create Project Structure
```bash
mkdir -p ~/legal-corpus/{raw,processed,embeddings,scripts}
cd ~/legal-corpus
```

### 1.2 Install Dependencies
```bash
# Python environment
python3 -m venv venv
source venv/bin/activate

# Core dependencies
pip install chromadb sentence-transformers requests beautifulsoup4 \
    pypdf2 python-docx lxml tqdm pandas httpx aiohttp

# Legal-specific embedding model
pip install voyageai  # For voyage-law-2 (best for legal)
# OR use free alternative:
pip install -U sentence-transformers  # For legal-bert
```

### 1.3 Initialize Chroma (Local Vector DB)
```python
# scripts/init_chroma.py
import chromadb
from chromadb.config import Settings

# Persistent local storage
client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)

# Create collections for each jurisdiction
collections = [
    "us_federal_law",
    "us_case_law",
    "eu_directives",
    "eu_regulations",
    "canada_federal",
    "australia_federal",
    "contract_clauses"  # From CUAD dataset
]

for name in collections:
    client.get_or_create_collection(
        name=name,
        metadata={"description": f"Legal corpus: {name}"}
    )

print("Chroma initialized with collections:", collections)
```

---

## PHASE 2: DOWNLOAD LEGAL DOCUMENTS

### 2.1 US Federal Law (GovInfo API)

**API Endpoint:** https://api.govinfo.gov/
**API Key:** Free, get from https://api.data.gov/signup/

```python
# scripts/download_us_federal.py
import httpx
import json
import os
from tqdm import tqdm

API_KEY = os.environ.get("GOVINFO_API_KEY", "DEMO_KEY")
BASE_URL = "https://api.govinfo.gov"

# Collections to download
COLLECTIONS = [
    "USCODE",      # US Code (statutes)
    "CFR",         # Code of Federal Regulations
    "BILLS",       # Congressional Bills
]

def get_collection_packages(collection, page_size=100, max_pages=10):
    """Fetch package list from a collection"""
    packages = []
    offset = 0

    for page in range(max_pages):
        url = f"{BASE_URL}/collections/{collection}/{offset}?pageSize={page_size}&api_key={API_KEY}"
        resp = httpx.get(url, timeout=30)

        if resp.status_code != 200:
            print(f"Error: {resp.status_code}")
            break

        data = resp.json()
        packages.extend(data.get("packages", []))

        if len(data.get("packages", [])) < page_size:
            break
        offset += page_size

    return packages

def download_package_content(package_id, output_dir):
    """Download package summary and full text"""
    # Get package summary
    url = f"{BASE_URL}/packages/{package_id}/summary?api_key={API_KEY}"
    resp = httpx.get(url, timeout=30)

    if resp.status_code == 200:
        summary = resp.json()

        # Save summary
        with open(f"{output_dir}/{package_id}_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        # Get granules (sections) if available
        granules_url = f"{BASE_URL}/packages/{package_id}/granules?api_key={API_KEY}"
        granules_resp = httpx.get(granules_url, timeout=30)

        if granules_resp.status_code == 200:
            granules = granules_resp.json()
            with open(f"{output_dir}/{package_id}_granules.json", "w") as f:
                json.dump(granules, f, indent=2)

if __name__ == "__main__":
    for collection in COLLECTIONS:
        output_dir = f"raw/us_federal/{collection}"
        os.makedirs(output_dir, exist_ok=True)

        print(f"Fetching {collection}...")
        packages = get_collection_packages(collection)

        print(f"Downloading {len(packages)} packages...")
        for pkg in tqdm(packages[:100]):  # Limit for initial test
            download_package_content(pkg["packageId"], output_dir)
```

### 2.2 US Case Law (CourtListener/Free Law Project)

**API Endpoint:** https://www.courtlistener.com/api/rest/v4/
**Note:** Free tier has rate limits; paid for commercial use

```python
# scripts/download_us_caselaw.py
import httpx
import json
import os
from tqdm import tqdm
import time

BASE_URL = "https://www.courtlistener.com/api/rest/v4"

# Focus on contract-related cases
SEARCH_QUERIES = [
    "non-compete agreement",
    "intellectual property assignment",
    "work for hire",
    "indemnification clause",
    "arbitration clause",
    "confidentiality agreement",
    "breach of contract freelance",
]

def search_opinions(query, max_results=50):
    """Search for case opinions"""
    results = []
    url = f"{BASE_URL}/search/"

    params = {
        "q": query,
        "type": "o",  # opinions
        "order_by": "score desc",
    }

    resp = httpx.get(url, params=params, timeout=30)

    if resp.status_code == 200:
        data = resp.json()
        results = data.get("results", [])[:max_results]

    return results

def download_opinion(opinion_id, output_dir):
    """Download full opinion text"""
    url = f"{BASE_URL}/opinions/{opinion_id}/"
    resp = httpx.get(url, timeout=30)

    if resp.status_code == 200:
        opinion = resp.json()
        with open(f"{output_dir}/{opinion_id}.json", "w") as f:
            json.dump(opinion, f, indent=2)
        return True
    return False

if __name__ == "__main__":
    output_dir = "raw/us_caselaw"
    os.makedirs(output_dir, exist_ok=True)

    all_opinions = []
    for query in SEARCH_QUERIES:
        print(f"Searching: {query}")
        opinions = search_opinions(query)
        all_opinions.extend(opinions)
        time.sleep(1)  # Rate limiting

    # Deduplicate
    seen_ids = set()
    unique_opinions = []
    for op in all_opinions:
        if op["id"] not in seen_ids:
            seen_ids.add(op["id"])
            unique_opinions.append(op)

    print(f"Downloading {len(unique_opinions)} unique opinions...")
    for op in tqdm(unique_opinions):
        download_opinion(op["id"], output_dir)
        time.sleep(0.5)  # Rate limiting
```

### 2.3 EU Law (EUR-Lex via SPARQL)

**Endpoint:** https://publications.europa.eu/webapi/rdf/sparql
**Note:** REST API is limited; SPARQL gives better access

```python
# scripts/download_eu_law.py
import httpx
import json
import os
from tqdm import tqdm

SPARQL_ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"

# SPARQL query for directives and regulations related to contracts/employment
SPARQL_QUERY = """
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?work ?title ?celex ?date
WHERE {
    ?work cdm:work_has_resource-type <http://publications.europa.eu/resource/authority/resource-type/DIR> .
    ?work cdm:work_date_document ?date .
    ?work cdm:resource_legal_id_celex ?celex .

    OPTIONAL { ?work cdm:work_title ?title }

    FILTER(YEAR(?date) >= 2010)
}
ORDER BY DESC(?date)
LIMIT 500
"""

def query_eurlex(sparql_query):
    """Execute SPARQL query against EUR-Lex"""
    headers = {
        "Accept": "application/sparql-results+json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"query": sparql_query}

    resp = httpx.post(SPARQL_ENDPOINT, headers=headers, data=data, timeout=60)

    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"Error: {resp.status_code} - {resp.text}")
        return None

def download_celex_document(celex_id, output_dir):
    """Download document by CELEX ID"""
    # EUR-Lex document URL pattern
    url = f"https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{celex_id}"

    # For machine-readable, use the REST API
    api_url = f"https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:{celex_id}"

    resp = httpx.get(api_url, timeout=30, follow_redirects=True)

    if resp.status_code == 200:
        with open(f"{output_dir}/{celex_id.replace(':', '_')}.html", "w") as f:
            f.write(resp.text)
        return True
    return False

if __name__ == "__main__":
    output_dir = "raw/eu_law"
    os.makedirs(output_dir, exist_ok=True)

    print("Querying EUR-Lex SPARQL endpoint...")
    results = query_eurlex(SPARQL_QUERY)

    if results:
        bindings = results.get("results", {}).get("bindings", [])
        print(f"Found {len(bindings)} documents")

        # Save metadata
        with open(f"{output_dir}/metadata.json", "w") as f:
            json.dump(bindings, f, indent=2)

        # Download documents
        for item in tqdm(bindings[:100]):  # Limit for test
            celex = item.get("celex", {}).get("value", "")
            if celex:
                download_celex_document(celex, output_dir)
```

### 2.4 Canada (CanLII)

**Note:** CanLII API requires registration; use web scraping for initial corpus

```python
# scripts/download_canada_law.py
import httpx
from bs4 import BeautifulSoup
import json
import os
from tqdm import tqdm
import time

BASE_URL = "https://www.canlii.org"

# Key federal statutes for contracts
STATUTES = [
    "/en/ca/laws/stat/rsc-1985-c-c-46/latest/rsc-1985-c-c-46.html",  # Criminal Code
    "/en/ca/laws/stat/rsc-1985-c-l-2/latest/rsc-1985-c-l-2.html",    # Canada Labour Code
    "/en/ca/laws/stat/sc-2000-c-5/latest/sc-2000-c-5.html",          # PIPEDA
]

def download_statute(path, output_dir):
    """Download statute HTML"""
    url = f"{BASE_URL}{path}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Legal Research Bot)"
    }

    resp = httpx.get(url, headers=headers, timeout=30)

    if resp.status_code == 200:
        filename = path.split("/")[-1]
        with open(f"{output_dir}/{filename}", "w") as f:
            f.write(resp.text)
        return True
    return False

if __name__ == "__main__":
    output_dir = "raw/canada_law"
    os.makedirs(output_dir, exist_ok=True)

    for statute in tqdm(STATUTES):
        download_statute(statute, output_dir)
        time.sleep(2)  # Respectful rate limiting
```

### 2.5 Australia (AustLII)

```python
# scripts/download_australia_law.py
import httpx
from bs4 import BeautifulSoup
import json
import os
from tqdm import tqdm
import time

BASE_URL = "https://www.austlii.edu.au"

# Key federal acts
ACTS = [
    "/au/legis/cth/consol_act/fwa2009114/",           # Fair Work Act
    "/au/legis/cth/consol_act/caca2010265/",          # Competition and Consumer Act
    "/au/legis/cth/consol_act/pa1990109/",            # Privacy Act
    "/au/legis/cth/consol_act/ca1968133/",            # Copyright Act
]

def download_act(path, output_dir):
    """Download act HTML"""
    url = f"{BASE_URL}{path}"

    resp = httpx.get(url, timeout=30)

    if resp.status_code == 200:
        filename = path.replace("/", "_").strip("_") + ".html"
        with open(f"{output_dir}/{filename}", "w") as f:
            f.write(resp.text)
        return True
    return False

if __name__ == "__main__":
    output_dir = "raw/australia_law"
    os.makedirs(output_dir, exist_ok=True)

    for act in tqdm(ACTS):
        download_act(act, output_dir)
        time.sleep(2)
```

### 2.6 CUAD Dataset (Pre-labeled Contracts)

**This is the most valuable dataset - 13K+ labeled contract clauses**

```python
# scripts/download_cuad.py
import httpx
import zipfile
import os

CUAD_URL = "https://github.com/TheAtticusProject/cuad/archive/refs/heads/main.zip"

def download_cuad(output_dir):
    """Download CUAD dataset from GitHub"""
    os.makedirs(output_dir, exist_ok=True)

    print("Downloading CUAD dataset...")
    resp = httpx.get(CUAD_URL, follow_redirects=True, timeout=120)

    if resp.status_code == 200:
        zip_path = f"{output_dir}/cuad.zip"
        with open(zip_path, "wb") as f:
            f.write(resp.content)

        print("Extracting...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)

        os.remove(zip_path)
        print("CUAD downloaded and extracted!")
        return True

    return False

if __name__ == "__main__":
    download_cuad("raw/cuad")
```

---

## PHASE 3: PROCESS AND CHUNK DOCUMENTS

### 3.1 Document Processing Pipeline

```python
# scripts/process_documents.py
import os
import json
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
import hashlib

def clean_html(html_content):
    """Extract text from HTML"""
    soup = BeautifulSoup(html_content, "lxml")

    # Remove scripts and styles
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    return soup.get_text(separator="\n", strip=True)

def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks"""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind(". ")
            if last_period > chunk_size * 0.5:
                end = start + last_period + 1
                chunk = text[start:end]

        chunks.append({
            "text": chunk.strip(),
            "start": start,
            "end": end,
            "hash": hashlib.md5(chunk.encode()).hexdigest()[:12]
        })

        start = end - overlap

    return chunks

def process_jurisdiction(input_dir, output_dir, jurisdiction):
    """Process all documents for a jurisdiction"""
    os.makedirs(output_dir, exist_ok=True)

    all_chunks = []

    for filename in tqdm(os.listdir(input_dir)):
        filepath = os.path.join(input_dir, filename)

        if filename.endswith(".html"):
            with open(filepath, "r", errors="ignore") as f:
                content = clean_html(f.read())
        elif filename.endswith(".json"):
            with open(filepath, "r") as f:
                data = json.load(f)
                content = json.dumps(data, indent=2)
        else:
            continue

        if len(content) < 100:
            continue

        chunks = chunk_text(content)

        for i, chunk in enumerate(chunks):
            chunk["source_file"] = filename
            chunk["jurisdiction"] = jurisdiction
            chunk["chunk_index"] = i
            chunk["total_chunks"] = len(chunks)
            all_chunks.append(chunk)

    # Save processed chunks
    output_file = os.path.join(output_dir, f"{jurisdiction}_chunks.json")
    with open(output_file, "w") as f:
        json.dump(all_chunks, f, indent=2)

    print(f"{jurisdiction}: {len(all_chunks)} chunks from {len(os.listdir(input_dir))} files")
    return all_chunks

if __name__ == "__main__":
    jurisdictions = [
        ("raw/us_federal", "processed", "us_federal"),
        ("raw/us_caselaw", "processed", "us_caselaw"),
        ("raw/eu_law", "processed", "eu_law"),
        ("raw/canada_law", "processed", "canada_law"),
        ("raw/australia_law", "processed", "australia_law"),
    ]

    for input_dir, output_dir, name in jurisdictions:
        if os.path.exists(input_dir):
            process_jurisdiction(input_dir, output_dir, name)
```

### 3.2 CUAD-Specific Processing

```python
# scripts/process_cuad.py
import os
import json
import pandas as pd
from tqdm import tqdm

CUAD_PATH = "raw/cuad/cuad-main"

# CUAD has 41 clause types - these are the key ones for freelancers
KEY_CLAUSES = [
    "Governing Law",
    "Non-Compete",
    "Exclusivity",
    "No-Solicit Of Employees",
    "IP Ownership Assignment",
    "License Grant",
    "Non-Disparagement",
    "Termination For Convenience",
    "Limitation Of Liability",
    "Indemnification",
    "Insurance",
    "Cap On Liability",
    "Audit Rights",
    "Uncapped Liability",
    "Warranty Duration",
    "Post-Termination Services",
    "Covenant Not To Sue",
    "Third Party Beneficiary"
]

def process_cuad():
    """Process CUAD dataset into chunks"""

    # Load CUAD annotations
    train_file = os.path.join(CUAD_PATH, "CUADv1.json")

    if not os.path.exists(train_file):
        print(f"CUAD not found at {train_file}")
        print("Run download_cuad.py first")
        return

    with open(train_file) as f:
        cuad_data = json.load(f)

    processed = []

    for item in tqdm(cuad_data["data"]):
        title = item["title"]

        for para in item["paragraphs"]:
            context = para["context"]

            for qa in para["qas"]:
                question = qa["question"]
                clause_type = question  # CUAD questions = clause types

                if qa["answers"]:
                    for answer in qa["answers"]:
                        processed.append({
                            "contract_title": title,
                            "clause_type": clause_type,
                            "clause_text": answer["text"],
                            "start_pos": answer["answer_start"],
                            "context_snippet": context[max(0, answer["answer_start"]-100):answer["answer_start"]+len(answer["text"])+100],
                            "is_key_clause": clause_type in KEY_CLAUSES
                        })

    # Save processed
    os.makedirs("processed", exist_ok=True)
    with open("processed/cuad_clauses.json", "w") as f:
        json.dump(processed, f, indent=2)

    print(f"Processed {len(processed)} clause annotations")

    # Summary stats
    df = pd.DataFrame(processed)
    print("\nClause type distribution:")
    print(df["clause_type"].value_counts().head(20))

if __name__ == "__main__":
    process_cuad()
```

---

## PHASE 4: EMBED AND INDEX INTO CHROMA

### 4.1 Embedding Configuration

```python
# scripts/config.py

# Option 1: Voyage AI (Best for legal, requires API key)
VOYAGE_CONFIG = {
    "model": "voyage-law-2",
    "api_key_env": "VOYAGE_API_KEY",
    "batch_size": 128,
    "dimensions": 1024
}

# Option 2: Free local model (Good enough for MVP)
LOCAL_CONFIG = {
    "model": "sentence-transformers/all-MiniLM-L6-v2",  # Fast, small
    # OR "nlpaueb/legal-bert-base-uncased"  # Legal-specific
    "batch_size": 32,
    "dimensions": 384  # or 768 for legal-bert
}

# Use local for cost-free operation
EMBEDDING_CONFIG = LOCAL_CONFIG
```

### 4.2 Embedding and Indexing Script

```python
# scripts/embed_and_index.py
import os
import json
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import hashlib

# Configuration
CHROMA_PATH = "./chroma_db"
PROCESSED_DIR = "./processed"
BATCH_SIZE = 100

def get_embedding_model():
    """Load embedding model"""
    print("Loading embedding model...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    # For legal-specific: model = SentenceTransformer("nlpaueb/legal-bert-base-uncased")
    return model

def init_chroma():
    """Initialize Chroma client"""
    return chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(anonymized_telemetry=False)
    )

def index_chunks(chunks, collection_name, model, client):
    """Embed and index chunks into Chroma"""

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    # Process in batches
    for i in tqdm(range(0, len(chunks), BATCH_SIZE)):
        batch = chunks[i:i+BATCH_SIZE]

        texts = [c["text"] for c in batch]
        ids = [f"{collection_name}_{c['hash']}_{j}" for j, c in enumerate(batch, start=i)]
        metadatas = [
            {
                "source_file": c.get("source_file", ""),
                "jurisdiction": c.get("jurisdiction", ""),
                "chunk_index": c.get("chunk_index", 0),
                "clause_type": c.get("clause_type", "general")
            }
            for c in batch
        ]

        # Generate embeddings
        embeddings = model.encode(texts, show_progress_bar=False).tolist()

        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    print(f"Indexed {len(chunks)} chunks into {collection_name}")

def main():
    model = get_embedding_model()
    client = init_chroma()

    # Index each jurisdiction
    jurisdiction_files = {
        "us_federal_law": "processed/us_federal_chunks.json",
        "us_case_law": "processed/us_caselaw_chunks.json",
        "eu_directives": "processed/eu_law_chunks.json",
        "canada_federal": "processed/canada_law_chunks.json",
        "australia_federal": "processed/australia_law_chunks.json",
    }

    for collection_name, filepath in jurisdiction_files.items():
        if os.path.exists(filepath):
            print(f"\nProcessing {collection_name}...")
            with open(filepath) as f:
                chunks = json.load(f)
            index_chunks(chunks, collection_name, model, client)
        else:
            print(f"Skipping {collection_name} - file not found")

    # Index CUAD clauses
    cuad_path = "processed/cuad_clauses.json"
    if os.path.exists(cuad_path):
        print("\nProcessing CUAD clauses...")
        with open(cuad_path) as f:
            cuad_data = json.load(f)

        # Convert to chunk format
        cuad_chunks = [
            {
                "text": item["clause_text"],
                "hash": hashlib.md5(item["clause_text"].encode()).hexdigest()[:12],
                "clause_type": item["clause_type"],
                "source_file": item["contract_title"],
                "jurisdiction": "cuad_reference"
            }
            for item in cuad_data
            if len(item["clause_text"]) > 20
        ]

        index_chunks(cuad_chunks, "contract_clauses", model, client)

    # Print stats
    print("\n" + "="*50)
    print("INDEXING COMPLETE")
    print("="*50)
    for coll in client.list_collections():
        count = coll.count()
        print(f"  {coll.name}: {count:,} vectors")

if __name__ == "__main__":
    main()
```

---

## PHASE 5: QUERY INTERFACE

### 5.1 Search Function

```python
# scripts/search_legal.py
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "./chroma_db"

def init():
    client = chromadb.PersistentClient(path=CHROMA_PATH, settings=Settings(anonymized_telemetry=False))
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return client, model

def search(query, collection_name=None, n_results=5, client=None, model=None):
    """Search legal corpus"""
    if client is None or model is None:
        client, model = init()

    query_embedding = model.encode([query])[0].tolist()

    results = []

    if collection_name:
        collections = [client.get_collection(collection_name)]
    else:
        collections = client.list_collections()

    for coll in collections:
        try:
            res = coll.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )

            for i, doc in enumerate(res["documents"][0]):
                results.append({
                    "collection": coll.name,
                    "text": doc,
                    "metadata": res["metadatas"][0][i],
                    "distance": res["distances"][0][i]
                })
        except Exception as e:
            print(f"Error querying {coll.name}: {e}")

    # Sort by distance (lower = more similar)
    results.sort(key=lambda x: x["distance"])

    return results[:n_results]

# Example usage
if __name__ == "__main__":
    client, model = init()

    # Test queries
    queries = [
        "non-compete clause duration",
        "intellectual property assignment",
        "indemnification liability cap",
        "termination for convenience",
    ]

    for q in queries:
        print(f"\n{'='*50}")
        print(f"Query: {q}")
        print("="*50)

        results = search(q, n_results=3, client=client, model=model)

        for i, r in enumerate(results, 1):
            print(f"\n[{i}] {r['collection']} (dist: {r['distance']:.3f})")
            print(f"    {r['text'][:200]}...")
```

---

## PHASE 6: EXECUTION CHECKLIST

Run these commands in order:

```bash
# 1. Setup
cd ~/legal-corpus
python3 -m venv venv
source venv/bin/activate
pip install chromadb sentence-transformers requests beautifulsoup4 pypdf2 lxml tqdm pandas httpx aiohttp

# 2. Initialize Chroma
python scripts/init_chroma.py

# 3. Download data (run each, takes time)
export GOVINFO_API_KEY="your_key_here"  # Get from api.data.gov
python scripts/download_cuad.py          # Priority 1 - most valuable
python scripts/download_us_federal.py    # Priority 2
python scripts/download_us_caselaw.py    # Priority 3
python scripts/download_eu_law.py        # Priority 4
python scripts/download_canada_law.py    # Priority 5
python scripts/download_australia_law.py # Priority 6

# 4. Process documents
python scripts/process_cuad.py
python scripts/process_documents.py

# 5. Embed and index
python scripts/embed_and_index.py

# 6. Test search
python scripts/search_legal.py
```

---

## EXPECTED OUTPUT

After completion, you should have:

```
~/legal-corpus/
├── chroma_db/                    # Vector database (persistent)
│   ├── chroma.sqlite3
│   └── [collection folders]
├── raw/                          # Downloaded documents
│   ├── cuad/
│   ├── us_federal/
│   ├── us_caselaw/
│   ├── eu_law/
│   ├── canada_law/
│   └── australia_law/
├── processed/                    # Chunked JSON files
│   ├── cuad_clauses.json
│   ├── us_federal_chunks.json
│   └── ...
└── scripts/                      # All Python scripts
```

**Estimated sizes:**
- CUAD: ~500MB raw, ~50MB processed
- US Federal: ~2GB raw, ~200MB processed
- Total Chroma DB: ~500MB-1GB

**Estimated time:**
- Downloads: 2-4 hours (rate limited)
- Processing: 30-60 minutes
- Embedding: 1-2 hours (CPU) or 10-20 min (GPU)

---

## TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| Rate limited by APIs | Increase sleep delays, run overnight |
| Out of memory | Reduce batch size in embedding |
| CUAD not found | Check GitHub URL, download manually |
| Chroma errors | Delete chroma_db folder, reinitialize |
| Slow embedding | Use GPU or smaller model |

---

## NEXT SESSION HANDOFF

After this session completes, the next session should:
1. Verify Chroma collections populated
2. Test search accuracy on contract queries
3. Build contract analysis prompts using RAG results
4. Integrate with contract upload pipeline
