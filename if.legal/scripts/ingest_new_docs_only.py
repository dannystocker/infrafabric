"""Ingest only new documents not already in ChromaDB."""
import csv
from pathlib import Path
import chromadb
from chromadb.config import Settings
from pypdf import PdfReader
from bs4 import BeautifulSoup
import json

def extract_text(path: Path) -> str:
    """Extract text from various file formats."""
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data)
    if path.suffix.lower() in {".html", ".xml", ".htm"}:
        with path.open("r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        return soup.get_text("\n")
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> list:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        start += max(1, chunk_size - overlap)
    return chunks

# Initialize ChromaDB
client = chromadb.PersistentClient(
    path="indexes/chromadb",
    settings=Settings(anonymized_telemetry=False),
)
collection = client.get_or_create_collection("if_legal_corpus")

# Get already indexed documents
print("Fetching currently indexed documents...")
results = collection.get(include=["metadatas"])
indexed_docs = set(meta.get('document_name', '') for meta in results['metadatas'])
print(f"Found {len(indexed_docs)} unique documents already indexed")

# Load corrected manifest
print("\nLoading manifest...")
with open('manifests/MASTER_MANIFEST_2025-11-28_CORRECTED.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    records = list(reader)

# Find new documents to ingest
new_docs = []
for record in records:
    if record.get('status', '').lower() == 'success':
        doc_name = record.get('document_name', '')
        if doc_name not in indexed_docs:
            local_path = record.get('local_path', '').strip().strip('"')
            if local_path and Path(local_path).exists():
                new_docs.append(record)

print(f"\nFound {len(new_docs)} NEW documents to ingest:")
for i, doc in enumerate(new_docs[:20], 1):
    print(f"{i:2}. {doc['document_name']} ({doc.get('jurisdiction', 'unknown')})")
if len(new_docs) > 20:
    print(f"... and {len(new_docs) - 20} more")

# Ingest new documents
if new_docs:
    print(f"\nStarting ingestion of {len(new_docs)} documents...")
    ingested_chunks = 0

    for i, record in enumerate(new_docs, 1):
        doc_name = record.get('document_name', '')
        local_path = record.get('local_path', '')

        try:
            print(f"\n[{i}/{len(new_docs)}] Processing: {doc_name}...")
            text = extract_text(Path(local_path))
            chunks = chunk_text(text)

            for idx, chunk in enumerate(chunks):
                doc_id = f"{doc_name}-{record.get('sha256', 'unknown')}-{idx}"
                metadata = {
                    "document_name": doc_name,
                    "local_path": local_path,
                    "sha256": record.get("sha256", ""),
                    "jurisdiction": record.get("jurisdiction", ""),
                    "legal_vertical": record.get("legal_vertical", ""),
                    "url": record.get("url", ""),
                    "priority": record.get("priority", "P1"),
                }
                collection.upsert(ids=[doc_id], documents=[chunk], metadatas=[metadata])
                ingested_chunks += 1

            print(f"  ✓ Ingested {len(chunks)} chunks")

        except Exception as e:
            print(f"  ✗ Error processing {doc_name}: {e}")

    print(f"\n✅ Ingestion complete!")
    print(f"  - New chunks added: {ingested_chunks}")
    print(f"  - Total collection size: {collection.count():,}")
else:
    print("\nNo new documents to ingest - all up to date!")
