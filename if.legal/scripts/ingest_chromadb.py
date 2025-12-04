"""ChromaDB ingestion for the legal corpus with IF.TTT citation metadata."""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import List, Dict, Optional

import chromadb
from bs4 import BeautifulSoup
from chromadb.config import Settings
from pypdf import PdfReader


def read_manifest(manifest_path: str) -> List[dict]:
    with open(manifest_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_citations(citations_path: str) -> Dict[str, dict]:
    """Load citations file and create lookup by local_path."""
    citations_map = {}
    try:
        with open(citations_path, 'r', encoding='utf-8') as f:
            citations_list = json.load(f)
            for citation in citations_list:
                local_path = citation['local_verification']['local_path']
                citations_map[local_path] = citation
    except (FileNotFoundError, json.JSONDecodeError):
        # Citations file not available, continue without it
        pass
    return citations_map


def extract_text(path: Path) -> str:
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


def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> List[str]:
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        start += max(1, chunk_size - overlap)
    return chunks


def ingest(manifest_path: str, db_dir: str, citations_path: Optional[str] = None) -> None:
    """Ingest corpus into ChromaDB with optional IF.TTT citation metadata."""
    records = read_manifest(manifest_path)

    # Load citations if available
    citations_map = {}
    if citations_path:
        citations_map = load_citations(citations_path)
    else:
        # Try default location
        default_citations = Path(manifest_path).parent.parent / 'citations' / 'legal-corpus-citations-2025-11-28.json'
        if default_citations.exists():
            citations_map = load_citations(str(default_citations))

    os.makedirs(db_dir, exist_ok=True)
    client = chromadb.PersistentClient(
        path=db_dir,
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection("if_legal_corpus")

    ingested_count = 0
    skipped_count = 0
    success_docs = 0

    for record in records:
        # Normalize status - accept both "success" and "SUCCESS"
        status = record.get("status", "").lower()
        if status not in ["success", "✓ downloaded"]:
            skipped_count += 1
            continue

        local_path = record.get("local_path")
        if not local_path or not os.path.exists(local_path):
            skipped_count += 1
            continue

        try:
            text = extract_text(Path(local_path))
        except Exception as e:
            print(f"Warning: Failed to extract text from {local_path}: {e}")
            skipped_count += 1
            continue

        # Look up citation metadata if available
        citation = citations_map.get(local_path)
        success_docs += 1

        for idx, chunk in enumerate(chunk_text(text)):
            doc_id = f"{record.get('document_name')}-{record.get('sha256', 'unknown')}-{idx}"

            # Base metadata from manifest
            metadata = {
                "document_name": record.get("document_name", ""),
                "local_path": local_path,
                "sha256": record.get("sha256", ""),
                "jurisdiction": record.get("jurisdiction", ""),
                "legal_vertical": record.get("legal_vertical", ""),
                "url": record.get("url", ""),
                "priority": record.get("priority", "P1"),
            }

            # Add IF.TTT citation metadata if available
            if citation:
                metadata.update({
                    "citation_id": citation.get("citation_id", ""),
                    "citation_type": citation.get("citation_type", ""),
                    "citation_status": citation.get("citation_status", "unverified"),
                    "authoritative_source_url": citation.get("authoritative_source", {}).get("url", ""),
                    "verification_method": citation.get("authoritative_source", {}).get("verification_method", ""),
                    "git_commit": citation.get("local_verification", {}).get("git_commit", ""),
                })

            collection.upsert(ids=[doc_id], documents=[chunk], metadatas=[metadata])
            ingested_count += 1

    # PersistentClient flushes automatically; nothing to do here.
    print(f"\nIngestion Complete:")
    print(f"  - Ingested {ingested_count} chunks from {success_docs} documents")
    print(f"  - Skipped {skipped_count} records (missing files or failed status)")
    print(f"  - Enhanced metadata from {len(citations_map)} IF.TTT citations")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest downloaded corpus into ChromaDB with IF.TTT citation metadata"
    )
    parser.add_argument(
        "--manifest",
        default="manifests/MASTER_MANIFEST_2025-11-28.csv",
        help="Path to manifest CSV",
    )
    parser.add_argument(
        "--db-dir",
        default="indexes/chromadb",
        help="ChromaDB directory",
    )
    parser.add_argument(
        "--citations",
        default=None,
        help="Path to citations JSON file (optional, auto-detects if not provided)",
    )
    args = parser.parse_args()
    ingest(args.manifest, args.db_dir, args.citations)


if __name__ == "__main__":
    main()
