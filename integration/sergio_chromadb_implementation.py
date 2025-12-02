"""
Sergio Personality DNA - ChromaDB Implementation Examples
=========================================================

This file contains executable Python code snippets for implementing
the ChromaDB collections design across all 4 Sergio collections.

Reference: /home/setup/infrafabric/integration/chromadb_sergio_collections_design.md

Phases:
1. Chunking & Cleaning (Phase 1)
2. Classification & Metadata (Phase 2)
3. Embedding Generation (Phase 3)
4. ChromaDB Ingestion (Phase 4)
5. Query Patterns (Phase 5)
"""

import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

# ============================================================================
# PHASE 1: CHUNKING & CLEANING
# ============================================================================

def phase1_chunking():
    """
    Phase 1: Read source documents and apply semantic chunking

    Expected duration: 2-3 hours
    Executor: Haiku agent
    Output: sergio_chunks_raw.json (~25-50KB, ~500 chunks)
    """

    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        print("Installing langchain...")
        os.system("pip install langchain")
        from langchain.text_splitter import RecursiveCharacterTextSplitter

    source_files = {
        "sergio_primary": [
            "/mnt/c/Users/Setup/Downloads/sergio-transcript.txt",
            "/mnt/c/Users/Setup/Downloads/SERGIO_TRES_HISTORIAS_TTS_OPTIMIZADO.txt",
            "/mnt/c/Users/Setup/Downloads/SERGIO_ASPERGERS_GUIA_AUDIO_ES.txt"
        ],
        "if_analysis": [
            "/home/setup/infrafabric/docs/demonstrations/SERGIO_ASPERGERS_FRAMEWORK_GUIDE_2025-11-29.md",
            "/home/setup/infrafabric/docs/demonstrations/IF_INTELLIGENCE_EMOSOCIAL_ANALYSIS_2025-11-28.md",
            "/home/setup/infrafabric/docs/demonstrations/IF_INTELLIGENCE_VALORES_DEBATE_2025-11-28.md",
            "/home/setup/infrafabric/docs/demonstrations/RORY_SUTHERLAND_REFRAMING_SERGIO_COUPLES_THERAPY_2025-11-28.md",
            "/home/setup/infrafabric/docs/analyses/SERGIO_EMOSOCIAL_NEURODIVERSITY_ANALYSIS_2025-11-29.md"
        ]
    }

    # Initialize semantic chunker
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,      # ~400 words = 2-3 sentences
        chunk_overlap=80,    # 20% overlap
        separators=["\n\n", "\n", ". ", " "]
    )

    chunks = {}
    total_chunks = 0

    for category, files in source_files.items():
        chunks[category] = []
        for file_path in files:
            if not os.path.exists(file_path):
                print(f"Warning: File not found: {file_path}")
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_chunks = splitter.split_text(content)

                    # Estimate line numbers (rough approximation)
                    line_num = 1
                    chunk_data = []

                    for i, chunk in enumerate(file_chunks):
                        # Estimate line number
                        lines_before = content[:content.find(chunk)].count('\n')

                        chunk_data.append({
                            "id": f"{os.path.basename(file_path)}_chunk_{i:03d}",
                            "text": chunk,
                            "source_file": file_path,
                            "chunk_index": i,
                            "source_line": lines_before + 1,
                            "word_count": len(chunk.split())
                        })

                    chunks[category].extend(chunk_data)
                    total_chunks += len(chunk_data)
                    print(f"✓ Chunked {file_path}: {len(chunk_data)} chunks")

            except Exception as e:
                print(f"✗ Error chunking {file_path}: {e}")

    # Save to file
    output_path = "/home/setup/sergio_chatbot/sergio_chunks_raw.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Phase 1 Complete: {total_chunks} chunks saved to {output_path}")
    return chunks


# ============================================================================
# PHASE 2: CLASSIFICATION & METADATA ENRICHMENT
# ============================================================================

def detect_language(text: str) -> str:
    """Detect if text is Spanish, English, or code-switched"""
    spanish_words = len(re.findall(r'\b(de|que|el|la|y|a|en|es|el|lo|se|por|con|no|una|su|para|es|al|lo|como|más|o|fue|este|sí|ya|or)\b', text.lower()))
    english_words = len(re.findall(r'\b(the|and|to|of|a|in|is|that|it|was|he|you|for|on|or|with|as|at|be|this|but)\b', text.lower()))

    total = spanish_words + english_words
    if total == 0:
        return "en"  # Default to English

    spanish_ratio = spanish_words / total

    if spanish_ratio > 0.6:
        return "es"
    elif spanish_ratio > 0.2:
        return "es_en"  # Code-switched
    else:
        return "en"


def phase2_classification(chunks_raw_path: str = "/home/setup/sergio_chatbot/sergio_chunks_raw.json"):
    """
    Phase 2: Classify chunks into 4 collections and enrich with metadata

    Expected duration: 2 hours
    Executor: Haiku agent
    Output: sergio_chunks_classified.json (~50-75KB)
    """

    # Load raw chunks
    with open(chunks_raw_path, 'r', encoding='utf-8') as f:
        chunks_raw = json.load(f)

    # Classification rules
    classification_rules = {
        "personality": [
            r"(Big Five|conscientiousness|openness|agreeableness|extraversion|neuroticism)",
            r"(ethical|values|principles|framework|trait)",
            r"(operational definition|anti-abstract|systems thinking|decision-making)",
            r"(characteristic|pattern|behavior|approach)"
        ],
        "rhetorical": [
            r"(metaphor|analogy|aspiradora|linguistic|device)",
            r"(code.?switch|bilingual|rhetorical|how Sergio|his speaking)",
            r"(language|vocabulary|discourse|expression|style)"
        ],
        "humor": [
            r"(laugh|funny|joke|witty|humor|self.?deprecating)",
            r"(vulnerability|emotional|warm|irony|sarcasm)",
            r"(\?$|!$)",  # Questions/exclamations
            r"(funny|amusing|amusing)"
        ],
        "corpus": []  # Default fallback
    }

    classified_chunks = {
        "personality": [],
        "rhetorical": [],
        "humor": [],
        "corpus": []
    }

    total_classified = 0

    for category, chunk_list in chunks_raw.items():
        for chunk in chunk_list:
            # Classify into target collection
            target_collection = "corpus"  # Default

            for collection_name, patterns in classification_rules.items():
                if any(re.search(p, chunk["text"], re.I) for p in patterns):
                    target_collection = collection_name
                    break

            # Build metadata
            metadata = {
                # Attribution & Source (IF.TTT)
                "source": category,
                "source_file": chunk["source_file"],
                "source_line": chunk["source_line"],
                "author": "Sergio Romo" if "sergio" in category else "IF.intelligence",

                # Content Classification
                "collection_type": target_collection,
                "category": category,
                "language": detect_language(chunk["text"]),

                # Quality & Trust
                "authenticity_score": 1.0 if "sergio" in category else 0.85,
                "confidence_level": "high" if chunk["word_count"] > 200 else "medium",
                "disputed": False,
                "if_citation_uri": ""  # Will be filled during ingestion
            }

            # Add collection-specific metadata
            if target_collection == "personality":
                metadata["big_five_trait"] = ""  # To be filled by Sonnet
                metadata["trait_score"] = 0.0
                metadata["related_frameworks"] = []
                metadata["behavioral_examples_count"] = chunk["text"].count("example") + chunk["text"].count("for instance")

            elif target_collection == "rhetorical":
                metadata["device_type"] = ""  # "metaphor", "analogy", etc.
                metadata["frequency"] = "sometimes"  # To be assessed
                metadata["linguistic_marker"] = ""
                metadata["usage_context"] = ""

            elif target_collection == "humor":
                metadata["humor_type"] = ""
                metadata["emotional_context"] = ""
                metadata["target_audience"] = ""
                metadata["effectiveness_rating"] = 0.0

            elif target_collection == "corpus":
                metadata["document_type"] = "transcript" if "transcript" in chunk["source_file"].lower() else "guide"
                metadata["word_count"] = chunk["word_count"]
                metadata["includes_spanish"] = detect_language(chunk["text"]) in ["es", "es_en"]
                metadata["emotional_intensity"] = 0.5  # Default

            chunk["metadata"] = metadata
            classified_chunks[target_collection].append(chunk)
            total_classified += 1

    # Save classified chunks
    output_path = "/home/setup/sergio_chatbot/sergio_chunks_classified.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(classified_chunks, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Phase 2 Complete: {total_classified} chunks classified")
    for collection, items in classified_chunks.items():
        print(f"  {collection}: {len(items)} chunks")

    return classified_chunks


# ============================================================================
# PHASE 3: EMBEDDING GENERATION
# ============================================================================

def phase3_embeddings(chunks_classified_path: str = "/home/setup/sergio_chatbot/sergio_chunks_classified.json"):
    """
    Phase 3: Generate embeddings for all chunks using nomic-embed-text-v1.5

    Expected duration: 2-3 hours
    Executor: Haiku agent
    Output: sergio_chunks_embedded.json (~200-300MB)
    """

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("Installing sentence-transformers...")
        os.system("pip install sentence-transformers")
        from sentence_transformers import SentenceTransformer

    # Load classified chunks
    with open(chunks_classified_path, 'r', encoding='utf-8') as f:
        classified_chunks = json.load(f)

    # Flatten all chunks
    all_chunks = []
    for collection_chunks in classified_chunks.values():
        all_chunks.extend(collection_chunks)

    print(f"Loading embedding model...")
    model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5')

    # Generate embeddings
    batch_size = 32
    embedded_chunks = []

    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i+batch_size]
        texts = [chunk["text"] for chunk in batch]

        try:
            embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

            for chunk, embedding in zip(batch, embeddings):
                chunk["embedding"] = embedding.tolist()
                embedded_chunks.append(chunk)

            if (i + batch_size) % (batch_size * 10) == 0:
                print(f"✓ Generated embeddings for chunks {i}-{min(i+batch_size, len(all_chunks))}")

        except Exception as e:
            print(f"✗ Error generating embeddings: {e}")
            return None

    # Save embedded chunks
    output_path = "/home/setup/sergio_chatbot/sergio_chunks_embedded.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(embedded_chunks, f)

    print(f"\n✓ Phase 3 Complete: {len(embedded_chunks)} embeddings generated and saved")
    return embedded_chunks


# ============================================================================
# PHASE 4: CHROMADB INGESTION
# ============================================================================

def phase4_chromadb_ingestion(chunks_embedded_path: str = "/home/setup/sergio_chatbot/sergio_chunks_embedded.json"):
    """
    Phase 4: Load embedded chunks into ChromaDB collections

    Expected duration: 1 hour
    Executor: Haiku agent
    Output: Live ChromaDB with 123 documents
    """

    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError:
        print("Installing chromadb...")
        os.system("pip install chromadb")
        import chromadb
        from chromadb.config import Settings

    # Load embedded chunks
    with open(chunks_embedded_path, 'r', encoding='utf-8') as f:
        embedded_chunks = json.load(f)

    print(f"Initializing ChromaDB...")

    # Try HTTP client first (for OpenWebUI Docker), fallback to PersistentClient
    try:
        client = chromadb.HttpClient(host="chromadb", port=8000)
        client.heartbeat()  # Test connection
        print("✓ Connected to ChromaDB HTTP API (Docker)")
    except:
        print("✓ Using ChromaDB PersistentClient (local)")
        client = chromadb.PersistentClient(path="/home/setup/sergio_chatbot/chromadb")

    # Create/get collections
    collections = {
        "sergio_personality": client.get_or_create_collection(
            name="sergio_personality",
            metadata={
                "description": "Sergio's personality traits, values, and decision-making patterns",
                "document_count": 23,
                "language": "en"
            }
        ),
        "sergio_rhetorical": client.get_or_create_collection(
            name="sergio_rhetorical",
            metadata={
                "description": "Sergio's rhetorical devices, linguistic patterns, and communication style",
                "document_count": 5,
                "language": "es_en"
            }
        ),
        "sergio_humor": client.get_or_create_collection(
            name="sergio_humor",
            metadata={
                "description": "Sergio's humor, jokes, and emotional expression patterns",
                "document_count": 28,
                "language": "es_en"
            }
        ),
        "sergio_corpus": client.get_or_create_collection(
            name="sergio_corpus",
            metadata={
                "description": "Sergio's conference transcripts, narratives, and guides",
                "document_count": 67,
                "language": "es_en"
            }
        )
    }

    # Load chunks into collections
    total_loaded = 0

    for collection_name, collection_obj in collections.items():
        collection_type = collection_name.split("_")[1]

        # Filter chunks for this collection
        collection_chunks = [
            c for c in embedded_chunks
            if c["metadata"]["collection_type"] == collection_type
        ]

        if not collection_chunks:
            print(f"Warning: No chunks for {collection_name}")
            continue

        # Prepare batch data
        ids = [c["id"] for c in collection_chunks]
        embeddings = [c["embedding"] for c in collection_chunks]
        documents = [c["text"] for c in collection_chunks]
        metadatas = [c["metadata"] for c in collection_chunks]

        try:
            collection_obj.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )

            print(f"✓ Loaded {len(collection_chunks)} chunks into {collection_name}")
            total_loaded += len(collection_chunks)

        except Exception as e:
            print(f"✗ Error loading {collection_name}: {e}")

    # Verify ingestion
    print(f"\n✓ Phase 4 Complete: {total_loaded} total documents loaded")
    print("\nChromaDB Collections Summary:")

    for name, collection in collections.items():
        count = collection.count()
        print(f"  {name}: {count} documents")

    return client, collections


# ============================================================================
# PHASE 5: QUERY PATTERNS
# ============================================================================

def test_query_pattern_1(collection):
    """Pattern 1: Retrieve personality traits"""
    results = collection.query(
        query_texts=["core values ethical framework"],
        n_results=5,
        where={
            "$and": [
                {"category": "trait_analysis"},
            ]
        }
    )
    return results


def test_query_pattern_2(collection):
    """Pattern 2: Retrieve rhetorical devices"""
    results = collection.query(
        query_texts=["metaphor systems thinking relational"],
        n_results=5,
        where={"device_type": {"$in": ["metaphor", "analogy"]}}
    )
    return results


def test_query_pattern_3(collection):
    """Pattern 3: Language-specific filtering"""
    results = collection.query(
        query_texts=["family systems"],
        n_results=5,
        where={"language": {"$in": ["es", "es_en"]}}
    )
    return results


def test_query_pattern_4(collection):
    """Pattern 4: Humor with emotional context"""
    results = collection.query(
        query_texts=["self deprecating neurodivergent funny"],
        n_results=3,
        where={"humor_type": "self_deprecating"}
    )
    return results


def test_query_pattern_5(collection):
    """Pattern 5: Corpus narrative search"""
    results = collection.query(
        query_texts=["identity relational therapeutic example"],
        n_results=5,
        where={"document_type": "narrative"}
    )
    return results


def generate_citation(query_result: Dict[str, Any], query_text: str) -> Dict[str, Any]:
    """Generate IF.citation for query result"""
    if not query_result.get("ids") or len(query_result["ids"]) == 0:
        return {}

    metadata = query_result["metadatas"][0] if query_result.get("metadatas") else {}

    citation = {
        "uri": f"if://citation/sergio-{uuid.uuid4().hex[:8]}-{datetime.now().strftime('%Y-%m-%d')}",
        "query": query_text,
        "result_id": query_result["ids"][0] if query_result.get("ids") else "",
        "source": metadata.get("source", ""),
        "source_file": metadata.get("source_file", ""),
        "source_line": metadata.get("source_line", 0),
        "author": metadata.get("author", ""),
        "authenticity_score": metadata.get("authenticity_score", 0.0),
        "timestamp": datetime.now().isoformat(),
        "status": "verified" if metadata.get("authenticity_score", 0) >= 0.9 else "unverified"
    }

    return citation


# ============================================================================
# OPENWEBUI PIPE CLASS
# ============================================================================

class SergioRAGPipe:
    """
    OpenWebUI Pipe class for Sergio personality DNA RAG

    Usage:
        pipe = SergioRAGPipe()
        result = pipe.query_sergio("How do you approach couples therapy?")
    """

    def __init__(self, chromadb_path: str = "/home/setup/sergio_chatbot/chromadb"):
        """Initialize Sergio RAG system"""
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=chromadb_path)
        except:
            self.client = None
            print("Warning: ChromaDB not initialized")

        self.collections = {
            "personality": self.client.get_collection("sergio_personality") if self.client else None,
            "rhetorical": self.client.get_collection("sergio_rhetorical") if self.client else None,
            "humor": self.client.get_collection("sergio_humor") if self.client else None,
            "corpus": self.client.get_collection("sergio_corpus") if self.client else None
        }

    def query_sergio(self, question: str, collection_name: str = None, n_results: int = 5) -> Dict[str, Any]:
        """
        Query Sergio's personality DNA

        Args:
            question: User's query
            collection_name: Which collection to search ("personality", "rhetorical", "humor", "corpus", or None for all)
            n_results: Number of results to return

        Returns:
            Dictionary with results and citations
        """

        if not self.client:
            return {"error": "ChromaDB not initialized"}

        results = {
            "query": question,
            "results": [],
            "citations": []
        }

        # If specific collection requested, search only that one
        if collection_name and collection_name in self.collections:
            collection = self.collections[collection_name]
            query_results = collection.query(
                query_texts=[question],
                n_results=n_results
            )

            # Add results
            for i, doc in enumerate(query_results["documents"][0] if query_results["documents"] else []):
                result_item = {
                    "text": doc,
                    "collection": collection_name,
                    "metadata": query_results["metadatas"][i] if i < len(query_results.get("metadatas", [])) else {}
                }
                results["results"].append(result_item)

                # Generate citation
                citation = generate_citation(
                    {"ids": query_results["ids"][i:i+1], "metadatas": [query_results["metadatas"][i]]} if query_results.get("metadatas") else {},
                    question
                )
                results["citations"].append(citation)

        # If no collection specified, search all
        else:
            for coll_name, collection in self.collections.items():
                if collection is None:
                    continue

                query_results = collection.query(
                    query_texts=[question],
                    n_results=2  # Get 2 from each collection
                )

                for i, doc in enumerate(query_results["documents"][0] if query_results["documents"] else []):
                    result_item = {
                        "text": doc,
                        "collection": coll_name,
                        "metadata": query_results["metadatas"][i] if i < len(query_results.get("metadatas", [])) else {}
                    }
                    results["results"].append(result_item)

        return results


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("Sergio Personality DNA - ChromaDB Implementation")
    print("=" * 60)

    # Phase 1: Chunking
    print("\nPhase 1: Chunking & Cleaning")
    print("-" * 60)
    chunks = phase1_chunking()

    # Phase 2: Classification
    print("\nPhase 2: Classification & Metadata")
    print("-" * 60)
    classified = phase2_classification()

    # Phase 3: Embeddings
    print("\nPhase 3: Embedding Generation")
    print("-" * 60)
    embedded = phase3_embeddings()

    # Phase 4: ChromaDB Ingestion
    print("\nPhase 4: ChromaDB Ingestion")
    print("-" * 60)
    if embedded:
        client, collections = phase4_chromadb_ingestion()

        # Phase 5: Test queries
        print("\nPhase 5: Query Testing")
        print("-" * 60)

        print("\nTest 1: Personality traits")
        result = collections["sergio_personality"].query(
            query_texts=["core values"], n_results=3
        )
        print(f"Found {len(result['documents'][0])} results")

        print("\nImplementation Complete!")
        print(f"Total embeddings: {sum(c.count() for c in collections.values())}")

    else:
        print("Embedding generation failed, skipping ChromaDB ingestion")
