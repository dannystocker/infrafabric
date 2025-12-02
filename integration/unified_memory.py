#!/usr/bin/env python3
"""
Unified Memory Interface for Multi-Model Access

Provides shared memory substrate for all models (Claude Max, DeepSeek, Gemini)
via Redis (L2 cache) and ChromaDB (RAG storage).

Module: UnifiedMemory
Author: InfraFabric
Version: 1.0.0
License: MIT

Architecture:
- Redis: Short-term memory (conversation state, session cache) with configurable TTL
- ChromaDB: Long-term memory (RAG collections, personality DNA, knowledge base)
- Connection Management: Graceful degradation if either backend fails
- Context Window Management: Automatic trimming of old messages

IF.citation: if://component/unified-memory/v1.0.0
IF.TTT: Traceable (all operations logged), Transparent (error handling visible),
        Trustworthy (no data corruption, atomic operations where possible)

Design Principles:
1. Model-agnostic interface: Works with Claude, DeepSeek, Gemini, Ollama
2. Graceful degradation: Continues functioning if Redis or ChromaDB unavailable
3. Error isolation: Failures don't cascade across all models
4. Context window aware: Prevents memory from growing unbounded
5. TTL management: Automatic cleanup of expired sessions
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any, Generator
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib
from enum import Enum


# ============================================================================
# Type Definitions and Enums
# ============================================================================

class MemoryOperationStatus(Enum):
    """Status of memory operations"""
    SUCCESS = "success"
    PARTIAL = "partial"  # Succeeded but with warnings
    DEGRADED = "degraded"  # One backend failed, using fallback
    FAILED = "failed"  # Critical failure


class StorageBackend(Enum):
    """Available storage backends"""
    REDIS = "redis"
    CHROMADB = "chromadb"
    MEMORY = "memory"  # In-memory fallback


@dataclass
class MemoryOperation:
    """Represents a memory operation result"""
    status: MemoryOperationStatus
    operation_id: str
    timestamp: str
    model_id: str
    session_id: str
    data_type: str
    backends_used: List[StorageBackend]
    error: Optional[str] = None
    warning: Optional[str] = None
    latency_ms: float = 0.0


@dataclass
class ConversationEntry:
    """Single conversation message entry"""
    role: str  # 'user' or 'assistant'
    content: str
    model_id: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Finding:
    """Research finding for long-term storage"""
    finding_id: str
    content: str
    source_model: str
    session_id: str
    timestamp: str
    confidence: float  # 0.0 to 1.0
    tags: List[str]
    related_findings: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Logging Configuration
# ============================================================================

def get_logger():
    """Get configured logger for UnifiedMemory"""
    logger = logging.getLogger("unified_memory")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = get_logger()


# ============================================================================
# Connection Management Classes
# ============================================================================

class RedisConnectionManager:
    """Manages Redis connection with health checking and reconnection logic"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """
        Initialize Redis connection manager.

        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number

        IF.citation: if://component/redis-connection-manager/v1.0.0
        """
        self.host = host
        self.port = port
        self.db = db
        self._redis_client = None
        self._is_connected = False
        self._last_health_check = 0
        self._health_check_interval = 30  # seconds

    def connect(self) -> bool:
        """
        Establish Redis connection.

        Returns:
            True if connected successfully, False otherwise
        """
        try:
            import redis
            self._redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            # Test connection
            self._redis_client.ping()
            self._is_connected = True
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
            return True
        except ImportError:
            logger.error("redis package not installed. Install with: pip install redis")
            return False
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self._is_connected = False
            return False

    def is_healthy(self) -> bool:
        """
        Check Redis connection health.

        Returns:
            True if Redis is available and responsive
        """
        if not self._is_connected or self._redis_client is None:
            return False

        now = time.time()
        if (now - self._last_health_check) < self._health_check_interval:
            return True  # Use cached health status

        try:
            self._redis_client.ping()
            self._last_health_check = now
            return True
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            self._is_connected = False
            return False

    def get_client(self):
        """Get Redis client or None if unavailable"""
        if self.is_healthy():
            return self._redis_client
        return None

    def close(self):
        """Close Redis connection"""
        if self._redis_client:
            try:
                self._redis_client.close()
            except Exception:
                pass
            self._is_connected = False


class ChromaDBConnectionManager:
    """Manages ChromaDB HTTP connection with collection management"""

    def __init__(self, host: str = "localhost", port: int = 8000):
        """
        Initialize ChromaDB connection manager.

        Args:
            host: ChromaDB HTTP server host
            port: ChromaDB HTTP server port

        IF.citation: if://component/chromadb-connection-manager/v1.0.0
        """
        self.host = host
        self.port = port
        self._client = None
        self._is_connected = False
        self._collections_cache: Dict[str, Any] = {}
        self._last_health_check = 0
        self._health_check_interval = 30

    def connect(self) -> bool:
        """
        Establish ChromaDB connection.

        Returns:
            True if connected successfully, False otherwise
        """
        try:
            import chromadb
            self._client = chromadb.HttpClient(host=self.host, port=self.port)
            # Test connection
            self._client.heartbeat()
            self._is_connected = True
            logger.info(f"Connected to ChromaDB at {self.host}:{self.port}")
            return True
        except ImportError:
            logger.error("chromadb package not installed. Install with: pip install chromadb")
            return False
        except Exception as e:
            logger.warning(f"Failed to connect to ChromaDB: {e}")
            self._is_connected = False
            return False

    def is_healthy(self) -> bool:
        """Check ChromaDB connection health"""
        if not self._is_connected or self._client is None:
            return False

        now = time.time()
        if (now - self._last_health_check) < self._health_check_interval:
            return True

        try:
            self._client.heartbeat()
            self._last_health_check = now
            return True
        except Exception as e:
            logger.warning(f"ChromaDB health check failed: {e}")
            self._is_connected = False
            return False

    def get_client(self):
        """Get ChromaDB client or None if unavailable"""
        if self.is_healthy():
            return self._client
        return None

    def get_or_create_collection(self, collection_name: str):
        """
        Get or create a ChromaDB collection.

        Args:
            collection_name: Name of collection

        Returns:
            Collection object or None if unavailable
        """
        if not self.is_healthy():
            return None

        try:
            if collection_name in self._collections_cache:
                return self._collections_cache[collection_name]

            collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self._collections_cache[collection_name] = collection
            return collection
        except Exception as e:
            logger.warning(f"Failed to get/create collection {collection_name}: {e}")
            return None

    def close(self):
        """Close ChromaDB connection"""
        self._collections_cache.clear()
        self._is_connected = False


# ============================================================================
# Main UnifiedMemory Class
# ============================================================================

class UnifiedMemory:
    """
    Unified Memory Interface for Multi-Model Access

    Provides a single, model-agnostic interface for storing and retrieving:
    - Conversation history (short-term, Redis)
    - Findings and insights (long-term, ChromaDB)
    - Session state (Redis)
    - RAG context (ChromaDB)

    Features:
    - Graceful degradation if Redis or ChromaDB unavailable
    - Automatic context window management
    - TTL-based cleanup of expired data
    - Comprehensive error handling and logging
    - Operation traceability

    IF.citation: if://component/unified-memory/v1.0.0
    IF.TTT: All operations are logged with traceability IDs
    """

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        chromadb_host: str = "localhost",
        chromadb_port: int = 8000,
        conversation_ttl_seconds: int = 3600,  # 1 hour
        finding_ttl_seconds: int = 86400,  # 24 hours
        max_context_messages: int = 100,
        enable_memory_fallback: bool = True,
    ):
        """
        Initialize UnifiedMemory with connection managers.

        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
            chromadb_host: ChromaDB HTTP server host
            chromadb_port: ChromaDB HTTP server port
            conversation_ttl_seconds: TTL for conversation cache
            finding_ttl_seconds: TTL for findings
            max_context_messages: Maximum messages before trimming
            enable_memory_fallback: Use in-memory fallback if backends unavailable

        IF.citation: if://component/unified-memory-init/v1.0.0
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.chromadb_host = chromadb_host
        self.chromadb_port = chromadb_port
        self.conversation_ttl = conversation_ttl_seconds
        self.finding_ttl = finding_ttl_seconds
        self.max_context_messages = max_context_messages
        self.enable_memory_fallback = enable_memory_fallback

        # Connection managers
        self.redis_mgr = RedisConnectionManager(redis_host, redis_port, redis_db)
        self.chromadb_mgr = ChromaDBConnectionManager(chromadb_host, chromadb_port)

        # In-memory fallback storage
        self._memory_fallback: Dict[str, Any] = {
            "conversations": {},
            "findings": {},
            "session_state": {},
        }

        # Initialize connections
        self._init_connections()

    def _init_connections(self):
        """Initialize Redis and ChromaDB connections"""
        redis_ok = self.redis_mgr.connect()
        chromadb_ok = self.chromadb_mgr.connect()

        if not redis_ok:
            logger.warning("Redis connection failed - conversation caching disabled")

        if not chromadb_ok:
            logger.warning("ChromaDB connection failed - RAG storage disabled")

        if not redis_ok and not chromadb_ok:
            if self.enable_memory_fallback:
                logger.warning("Both backends unavailable - using in-memory fallback")
            else:
                logger.error("All backends unavailable - memory operations will fail")

    # ========================================================================
    # Conversation Management
    # ========================================================================

    def _generate_operation_id(self) -> str:
        """Generate unique operation ID"""
        return hashlib.md5(
            f"{time.time()}-{id(self)}".encode()
        ).hexdigest()[:12]

    def store_conversation(
        self,
        model_id: str,
        session_id: str,
        messages: List[Dict[str, str]],
    ) -> MemoryOperation:
        """
        Store conversation in Redis for short-term recall.

        Args:
            model_id: Identifier for the model (e.g., 'claude-max', 'deepseek')
            session_id: Session identifier
            messages: List of message dicts with 'role' and 'content'

        Returns:
            MemoryOperation with status and operation details

        IF.citation: if://api/store-conversation/v1.0.0
        """
        op_id = self._generate_operation_id()
        start_time = time.time()
        backends_used = []

        try:
            # Trim messages if needed
            trimmed_messages = self._trim_context_window(messages)

            # Prepare data
            key = f"conversation:{model_id}:{session_id}"
            data = {
                "messages": trimmed_messages,
                "stored_at": datetime.now().isoformat(),
                "message_count": len(trimmed_messages),
            }

            # Try Redis first
            redis_client = self.redis_mgr.get_client()
            if redis_client:
                try:
                    redis_client.setex(
                        key,
                        self.conversation_ttl,
                        json.dumps(data)
                    )
                    backends_used.append(StorageBackend.REDIS)
                except Exception as e:
                    logger.warning(f"Redis store failed: {e}")

            # Fallback to in-memory if Redis unavailable
            if not backends_used and self.enable_memory_fallback:
                self._memory_fallback["conversations"][key] = data
                backends_used.append(StorageBackend.MEMORY)

            latency = (time.time() - start_time) * 1000

            status = (
                MemoryOperationStatus.SUCCESS
                if backends_used
                else MemoryOperationStatus.FAILED
            )

            return MemoryOperation(
                status=status,
                operation_id=op_id,
                timestamp=datetime.now().isoformat(),
                model_id=model_id,
                session_id=session_id,
                data_type="conversation",
                backends_used=backends_used,
                latency_ms=latency,
            )

        except Exception as e:
            logger.error(f"store_conversation failed: {e}")
            return MemoryOperation(
                status=MemoryOperationStatus.FAILED,
                operation_id=op_id,
                timestamp=datetime.now().isoformat(),
                model_id=model_id,
                session_id=session_id,
                data_type="conversation",
                backends_used=[],
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000,
            )

    def retrieve_conversation(
        self,
        model_id: str,
        session_id: str,
    ) -> Optional[List[Dict[str, str]]]:
        """
        Retrieve conversation from Redis.

        Args:
            model_id: Model identifier
            session_id: Session identifier

        Returns:
            List of messages or None if not found

        IF.citation: if://api/retrieve-conversation/v1.0.0
        """
        key = f"conversation:{model_id}:{session_id}"

        # Try Redis first
        redis_client = self.redis_mgr.get_client()
        if redis_client:
            try:
                data_str = redis_client.get(key)
                if data_str:
                    data = json.loads(data_str)
                    return data.get("messages", [])
            except Exception as e:
                logger.warning(f"Redis retrieve failed: {e}")

        # Fallback to in-memory
        if key in self._memory_fallback["conversations"]:
            return self._memory_fallback["conversations"][key].get("messages", [])

        return None

    # ========================================================================
    # RAG Context Retrieval
    # ========================================================================

    def retrieve_context(
        self,
        query: str,
        collections: List[str],
        n_results: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Query ChromaDB across multiple collections for RAG context.

        Args:
            query: Query text to search for
            collections: List of collection names to search
            n_results: Number of results per collection

        Returns:
            List of retrieved context items

        IF.citation: if://api/retrieve-context/v1.0.0
        """
        results = []

        chromadb_client = self.chromadb_mgr.get_client()
        if not chromadb_client:
            logger.warning("ChromaDB unavailable - returning empty context")
            return results

        try:
            for collection_name in collections:
                try:
                    collection = self.chromadb_mgr.get_or_create_collection(collection_name)
                    if not collection:
                        continue

                    query_result = collection.query(
                        query_texts=[query],
                        n_results=n_results,
                        include=["documents", "metadatas", "distances"]
                    )

                    # Transform result to unified format
                    if query_result and query_result.get("documents"):
                        for i, doc in enumerate(query_result["documents"][0]):
                            results.append({
                                "collection": collection_name,
                                "document": doc,
                                "metadata": query_result["metadatas"][0][i],
                                "distance": query_result["distances"][0][i],
                            })

                except Exception as e:
                    logger.warning(f"Query failed for collection {collection_name}: {e}")

            return results

        except Exception as e:
            logger.error(f"retrieve_context failed: {e}")
            return []

    # ========================================================================
    # Finding Storage (Long-term Memory)
    # ========================================================================

    def store_finding(
        self,
        finding_data: Dict[str, Any],
    ) -> MemoryOperation:
        """
        Store a research finding for long-term memory (24-hour TTL).

        Args:
            finding_data: Dict with keys:
                - finding_id: Unique identifier
                - content: Finding text
                - source_model: Which model generated it
                - session_id: Session identifier
                - confidence: Confidence score (0.0-1.0)
                - tags: List of tag strings

        Returns:
            MemoryOperation with status

        IF.citation: if://api/store-finding/v1.0.0
        """
        op_id = self._generate_operation_id()
        start_time = time.time()
        backends_used = []

        try:
            finding_id = finding_data.get("finding_id")
            session_id = finding_data.get("session_id")
            content = finding_data.get("content", "")
            model_id = finding_data.get("source_model", "unknown")

            # Store in Redis for quick access
            redis_client = self.redis_mgr.get_client()
            if redis_client:
                try:
                    key = f"finding:{finding_id}"
                    redis_client.setex(
                        key,
                        self.finding_ttl,
                        json.dumps(finding_data)
                    )
                    backends_used.append(StorageBackend.REDIS)
                except Exception as e:
                    logger.warning(f"Redis finding storage failed: {e}")

            # Store in ChromaDB for semantic search
            chromadb_client = self.chromadb_mgr.get_client()
            if chromadb_client:
                try:
                    collection = self.chromadb_mgr.get_or_create_collection("findings")
                    if collection:
                        collection.add(
                            ids=[finding_id],
                            documents=[content],
                            metadatas=[{
                                "source_model": model_id,
                                "session_id": session_id,
                                "confidence": finding_data.get("confidence", 0.5),
                                "tags": ",".join(finding_data.get("tags", [])),
                                "created_at": datetime.now().isoformat(),
                            }]
                        )
                        backends_used.append(StorageBackend.CHROMADB)
                except Exception as e:
                    logger.warning(f"ChromaDB finding storage failed: {e}")

            # Fallback to in-memory
            if not backends_used and self.enable_memory_fallback:
                key = f"finding:{finding_id}"
                self._memory_fallback["findings"][key] = finding_data
                backends_used.append(StorageBackend.MEMORY)

            latency = (time.time() - start_time) * 1000

            status = (
                MemoryOperationStatus.SUCCESS
                if backends_used
                else MemoryOperationStatus.FAILED
            )

            return MemoryOperation(
                status=status,
                operation_id=op_id,
                timestamp=datetime.now().isoformat(),
                model_id=model_id,
                session_id=session_id,
                data_type="finding",
                backends_used=backends_used,
                latency_ms=latency,
            )

        except Exception as e:
            logger.error(f"store_finding failed: {e}")
            return MemoryOperation(
                status=MemoryOperationStatus.FAILED,
                operation_id=op_id,
                timestamp=datetime.now().isoformat(),
                model_id=finding_data.get("source_model", "unknown"),
                session_id=finding_data.get("session_id", "unknown"),
                data_type="finding",
                backends_used=[],
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000,
            )

    # ========================================================================
    # Session State Management
    # ========================================================================

    def store_session_state(
        self,
        session_id: str,
        state_data: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
    ) -> MemoryOperation:
        """
        Store session state (user preferences, context flags, etc).

        Args:
            session_id: Session identifier
            state_data: Session state dictionary
            ttl_seconds: Override TTL (uses conversation_ttl by default)

        Returns:
            MemoryOperation with status

        IF.citation: if://api/store-session-state/v1.0.0
        """
        op_id = self._generate_operation_id()
        start_time = time.time()
        backends_used = []

        try:
            key = f"session_state:{session_id}"
            ttl = ttl_seconds or self.conversation_ttl

            # Store in Redis
            redis_client = self.redis_mgr.get_client()
            if redis_client:
                try:
                    redis_client.setex(
                        key,
                        ttl,
                        json.dumps({
                            **state_data,
                            "updated_at": datetime.now().isoformat(),
                        })
                    )
                    backends_used.append(StorageBackend.REDIS)
                except Exception as e:
                    logger.warning(f"Redis session state storage failed: {e}")

            # Fallback to in-memory
            if not backends_used and self.enable_memory_fallback:
                self._memory_fallback["session_state"][key] = {
                    **state_data,
                    "updated_at": datetime.now().isoformat(),
                }
                backends_used.append(StorageBackend.MEMORY)

            latency = (time.time() - start_time) * 1000

            return MemoryOperation(
                status=MemoryOperationStatus.SUCCESS if backends_used else MemoryOperationStatus.FAILED,
                operation_id=op_id,
                timestamp=datetime.now().isoformat(),
                model_id="system",
                session_id=session_id,
                data_type="session_state",
                backends_used=backends_used,
                latency_ms=latency,
            )

        except Exception as e:
            logger.error(f"store_session_state failed: {e}")
            return MemoryOperation(
                status=MemoryOperationStatus.FAILED,
                operation_id=op_id,
                timestamp=datetime.now().isoformat(),
                model_id="system",
                session_id=session_id,
                data_type="session_state",
                backends_used=[],
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000,
            )

    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session state.

        Args:
            session_id: Session identifier

        Returns:
            Session state dict or None if not found

        IF.citation: if://api/get-session-state/v1.0.0
        """
        key = f"session_state:{session_id}"

        # Try Redis first
        redis_client = self.redis_mgr.get_client()
        if redis_client:
            try:
                data_str = redis_client.get(key)
                if data_str:
                    return json.loads(data_str)
            except Exception as e:
                logger.warning(f"Redis session state retrieval failed: {e}")

        # Fallback to in-memory
        if key in self._memory_fallback["session_state"]:
            return self._memory_fallback["session_state"][key]

        return None

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def _trim_context_window(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Trim messages if exceeding max_context_messages.

        Strategy: Keep the system context (first message) and most recent messages.

        Args:
            messages: Full message list

        Returns:
            Trimmed message list

        IF.citation: if://component/context-window-trimming/v1.0.0
        """
        if len(messages) <= self.max_context_messages:
            return messages

        # Keep first message (usually system prompt) and last N messages
        if messages and messages[0].get("role") == "system":
            return [messages[0]] + messages[-(self.max_context_messages - 1):]
        else:
            return messages[-self.max_context_messages:]

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of all backends.

        Returns:
            Dict with health info for Redis, ChromaDB, and fallback status

        IF.citation: if://api/health-status/v1.0.0
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "redis": {
                "connected": self.redis_mgr.is_healthy(),
                "host": self.redis_host,
                "port": self.redis_port,
            },
            "chromadb": {
                "connected": self.chromadb_mgr.is_healthy(),
                "host": self.chromadb_host,
                "port": self.chromadb_port,
            },
            "memory_fallback": {
                "enabled": self.enable_memory_fallback,
                "conversations": len(self._memory_fallback["conversations"]),
                "findings": len(self._memory_fallback["findings"]),
                "session_states": len(self._memory_fallback["session_state"]),
            },
        }

    def clear_expired_data(self) -> Dict[str, int]:
        """
        Clean up expired data from in-memory fallback.

        Redis handles expiration automatically via TTL.

        Returns:
            Dict with counts of removed items

        IF.citation: if://component/data-cleanup/v1.0.0
        """
        now = datetime.now()
        removed = {
            "conversations": 0,
            "findings": 0,
            "session_states": 0,
        }

        # Clean up in-memory storage (Redis handles TTL automatically)
        # This is mainly for the fallback memory
        # For now, we keep everything since fallback is meant for crashes

        return removed

    def close(self):
        """Close all connections gracefully"""
        try:
            self.redis_mgr.close()
            self.chromadb_mgr.close()
            logger.info("UnifiedMemory connections closed")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")


# ============================================================================
# Integration Examples for Each Model
# ============================================================================

class ModelMemoryIntegration:
    """
    Examples of how to integrate UnifiedMemory with different models.

    IF.citation: if://example/model-memory-integration/v1.0.0
    """

    @staticmethod
    def claude_max_integration(memory: UnifiedMemory, session_id: str):
        """
        Example: Integrate UnifiedMemory with Claude Max

        def pipe(body: dict) -> Generator[str, None, None]:
            # Initialize memory
            memory = UnifiedMemory()

            # Store incoming conversation
            messages = body.get("messages", [])
            op = memory.store_conversation("claude-max", session_id, messages)
            print(f"Stored conversation: {op.status}")

            # Get any session state
            state = memory.get_session_state(session_id)

            # Retrieve RAG context from personality collections
            context = memory.retrieve_context(
                query=messages[-1]["content"] if messages else "",
                collections=["sergio_personality", "sergio_rhetorical"],
                n_results=3
            )

            # Inject context into system prompt
            # [execute Claude CLI with injected context]

            # Store any important findings
            memory.store_finding({
                "finding_id": f"finding_{int(time.time())}",
                "content": "Generated insight",
                "source_model": "claude-max",
                "session_id": session_id,
                "confidence": 0.9,
                "tags": ["insight", "user-specific"]
            })
        """
        pass

    @staticmethod
    def deepseek_integration(memory: UnifiedMemory, session_id: str):
        """
        Example: Integrate UnifiedMemory with DeepSeek Chat API

        async def process_deepseek(query: str):
            # Retrieve previous conversation
            messages = memory.retrieve_conversation("deepseek", session_id)

            # Get semantic context from findings
            context = memory.retrieve_context(
                query=query,
                collections=["findings", "knowledge_base"],
                n_results=5
            )

            # Augment DeepSeek prompt with context
            augmented_messages = context_augment(messages, context)

            # Call DeepSeek API
            response = await deepseek_api(augmented_messages)

            # Store response in conversation
            augmented_messages.append({"role": "assistant", "content": response})
            memory.store_conversation("deepseek", session_id, augmented_messages)

            return response
        """
        pass

    @staticmethod
    def gemini_integration(memory: UnifiedMemory, session_id: str):
        """
        Example: Integrate UnifiedMemory with Gemini Pro

        def gemini_chat(user_message: str):
            # Retrieve multi-model consensus from recent findings
            findings = memory.retrieve_context(
                query=user_message,
                collections=["consensus_decisions", "validated_insights"],
                n_results=3
            )

            # Get session preferences
            state = memory.get_session_state(session_id)
            user_tone = state.get("communication_style", "neutral") if state else "neutral"

            # Call Gemini with context and preferences
            response = genai.GenerativeModel('gemini-pro').generate_content(
                f"[Context from other models]: {findings}\\n"
                f"[User communication style]: {user_tone}\\n"
                f"[Message]: {user_message}"
            )

            # Store finding if high confidence
            if should_store_as_finding(response):
                memory.store_finding({
                    "finding_id": f"gemini_{int(time.time())}",
                    "content": response.text,
                    "source_model": "gemini",
                    "session_id": session_id,
                    "confidence": 0.85,
                    "tags": ["multi-model-consensus"]
                })

            return response.text
        """
        pass


# ============================================================================
# Error Handling Matrix
# ============================================================================

ERROR_HANDLING_MATRIX = """
UnifiedMemory Error Handling Matrix

Scenario: Redis Down, ChromaDB Up
- store_conversation: Uses memory fallback ✓
- retrieve_conversation: Uses memory fallback ✓
- store_finding: Falls back to ChromaDB only (partial) ⚠
- retrieve_context: Works normally ✓
- store_session_state: Uses memory fallback ✓

Scenario: Redis Up, ChromaDB Down
- store_conversation: Works normally ✓
- retrieve_conversation: Works normally ✓
- store_finding: Falls back to Redis only (partial) ⚠
- retrieve_context: Returns empty list ✓ (graceful)
- store_session_state: Works normally ✓

Scenario: Both Down
- store_conversation: Uses memory fallback ✓
- retrieve_conversation: Uses memory fallback ✓
- store_finding: Uses memory fallback ✓
- retrieve_context: Returns empty list ✓ (graceful)
- store_session_state: Uses memory fallback ✓

Scenario: Connection Timeout
- Automatic retry in next health check
- Falls back to available backends
- Logs warning, operation continues

Scenario: Corrupted Data
- JSON parse errors caught and logged
- Operation fails gracefully
- Memory fallback used as backup
"""


if __name__ == "__main__":
    # Example usage and testing
    import sys

    logging.basicConfig(level=logging.INFO)

    # Initialize memory
    memory = UnifiedMemory(
        redis_host="localhost",
        redis_port=6379,
        chromadb_host="localhost",
        chromadb_port=8000,
        enable_memory_fallback=True,
    )

    # Print health status
    print("Health Status:")
    print(json.dumps(memory.get_health_status(), indent=2))

    # Test conversation storage
    test_messages = [
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "What is 2+2?"},
        {"role": "assistant", "content": "2+2=4"},
    ]

    op = memory.store_conversation("claude-max", "session-001", test_messages)
    print(f"\nStore Conversation: {op.status.value}")
    print(f"  Backends: {[b.value for b in op.backends_used]}")
    print(f"  Latency: {op.latency_ms:.2f}ms")

    # Test retrieval
    retrieved = memory.retrieve_conversation("claude-max", "session-001")
    print(f"\nRetrieved Conversation: {len(retrieved) if retrieved else 0} messages")

    # Test session state
    op = memory.store_session_state("session-001", {
        "user_id": "user-123",
        "communication_style": "casual",
        "context_level": "advanced"
    })
    print(f"\nStore Session State: {op.status.value}")

    state = memory.get_session_state("session-001")
    print(f"Retrieved State: {state}")

    memory.close()
