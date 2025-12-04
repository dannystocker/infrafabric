"""Ingest all missing legal documents from disk."""
import chromadb
from chromadb.config import Settings
from pathlib import Path
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

def should_skip(path: Path) -> bool:
    """Determine if file should be skipped (documentation, logs, etc.)."""
    skip_patterns = [
        'README', 'INDEX', 'GUIDE', 'SUMMARY', 'LOG', 'MANIFEST',
        'QUICK', 'RECOVERY', 'DOWNLOAD', 'ACCESS'
    ]
    name_upper = path.stem.upper()
    return any(pattern in name_upper for pattern in skip_patterns)

# Initialize ChromaDB
client = chromadb.PersistentClient(
    path="indexes/chromadb",
    settings=Settings(anonymized_telemetry=False),
)
collection = client.get_or_create_collection("if_legal_corpus")

# Get already indexed documents
print("Fetching currently indexed documents...")
results = collection.get(include=["metadatas"])
indexed_paths = set(meta.get('local_path', '') for meta in results['metadatas'])
print(f"Found {len(indexed_paths)} files already indexed")

# Find all legal documents on disk
print("\nScanning /raw/ directory...")
all_files = []
for path in Path('raw').rglob('*'):
    if (path.is_file() and
        path.suffix.lower() in ['.md', '.txt', '.pdf', '.html', '.json'] and
        not should_skip(path)):
        all_files.append(path)

# Filter to only non-indexed files
missing_files = [f for f in all_files if str(f) not in indexed_paths]

print(f"\nFound {len(all_files)} legal documents on disk")
print(f"Already indexed: {len(all_files) - len(missing_files)}")
print(f"Need to ingest: {len(missing_files)}")

if not missing_files:
    print("\n✅ All documents already ingested!")
    exit(0)

# Group by jurisdiction
by_jurisdiction = {}
for f in missing_files:
    parts = f.parts
    jur = parts[1] if len(parts) > 1 else 'unknown'
    if jur not in by_jurisdiction:
        by_jurisdiction[jur] = []
    by_jurisdiction[jur].append(f)

print(f"\nMissing documents by jurisdiction:")
for jur, files in sorted(by_jurisdiction.items()):
    print(f"  {jur}: {len(files)}")

# Ingest missing files
print(f"\nStarting ingestion of {len(missing_files)} documents...")
ingested_chunks = 0
ingested_docs = 0
errors = 0

for i, file_path in enumerate(missing_files, 1):
    parts = file_path.parts
    jurisdiction = parts[1] if len(parts) > 1 else 'unknown'
    legal_vertical = parts[2] if len(parts) > 2 else 'general'
    doc_name = file_path.stem.replace('_', ' ').replace('-', ' ').title()

    try:
        if i % 10 == 0 or i == len(missing_files):
            print(f"\n[{i}/{len(missing_files)}] {doc_name[:50]}...")

        text = extract_text(file_path)
        chunks = chunk_text(text)

        for idx, chunk in enumerate(chunks):
            doc_id = f"{doc_name}-{hash(str(file_path))}-{idx}"
            metadata = {
                "document_name": doc_name,
                "local_path": str(file_path),
                "jurisdiction": jurisdiction,
                "legal_vertical": legal_vertical,
                "priority": "P1",
            }
            collection.upsert(ids=[doc_id], documents=[chunk], metadatas=[metadata])
            ingested_chunks += 1

        ingested_docs += 1

    except Exception as e:
        print(f"  ✗ Error: {e}")
        errors += 1

print(f"\n{'='*60}")
print(f"✅ Ingestion complete!")
print(f"  Documents ingested: {ingested_docs}")
print(f"  Chunks added: {ingested_chunks:,}")
print(f"  Errors: {errors}")
print(f"  Total collection size: {collection.count():,}")
print(f"{'='*60}")
