# MCP Multiagent Bridge Integration: Model Swarm Coordination for OpenWebUI

**Document Version:** 1.0
**Date:** 2025-11-30
**Framework:** IF.TTT (Traceable, Transparent, Trustworthy)
**Citation:** `if://doc/mcp-multiagent-bridge-integration/2025-11-30`

---

## Executive Summary

This document designs the integration of mcp-multiagent-bridge into OpenWebUI's architecture to enable multi-model swarm coordination patterns. The integration allows multiple LLM models (Claude Max, DeepSeek, Gemini, etc.) to collaborate through three proven swarm patterns:

1. **Consensus Mode:** All models vote on decisions, weighted by confidence scores
2. **Delegation Mode:** Route tasks to specialist models based on capability registry
3. **Critique Mode:** Model A generates, Model B validates, Model A refines

**Key Design Principles:**
- Secure agent-to-agent communication via HMAC-SHA256 authentication
- Zero trust architecture with automatic secret redaction
- Production-ready with 1.7ms average latency benchmark
- Extensible plugin architecture for future swarm patterns
- IF.guard veto layer prevents harmful outputs before reaching users

**Integration Complexity:** Medium (3-4 weeks development)
**Token Efficiency:** High (delegates model coordination to cheaper Haiku agents)
**Risk Level:** Low (mcp-multiagent-bridge production-validated Nov 2025)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Three Swarm Patterns](#three-swarm-patterns)
3. [AgentMessage Interface](#agentmessage-interface)
4. [MultiAgentBridge Implementation](#multiagentbridge-implementation)
5. [OpenWebUI Integration](#openwebui-integration)
6. [Error Handling & Recovery](#error-handling--recovery)
7. [Security Considerations](#security-considerations)
8. [Testing & Validation](#testing--validation)
9. [Implementation Checklist](#implementation-checklist)
10. [IF.TTT Citations](#iftt-citations)

---

## Architecture Overview

### Current State: Single-Model OpenWebUI

```
User (OpenWebUI Chat)
    │
    ├─→ Claude Max (via Function)
    ├─→ DeepSeek Chat
    └─→ Gemini API

Problem: Each model operates independently. No coordination, no consensus, no delegation.
```

### Target State: Multi-Model Swarm Coordination

```
┌─────────────────────────────────────────────────────────────┐
│             OpenWebUI Interface                              │
│  (User submits: "Analyze this code for security issues")    │
└────────────────────┬────────────────────────────────────────┘
                     │
            ┌────────▼────────┐
            │ MultiAgentBridge │ ← New orchestration layer
            │ (this integration)
            └────────┬────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
   ┌──▼──┐      ┌───▼────┐    ┌───▼────┐
   │Phase│      │Phase   │    │Phase   │
   │ 1   │      │ 2      │    │ 3      │
   │─────│      │────────│    │────────│
   │Deli-│      │Concur- │    │Result  │
   │ver  │      │rent    │    │Synth.  │
   └──┬──┘      └───┬────┘    └───┬────┘
      │             │            │
   Claude Max   DeepSeek      Gemini
   (Analysis)   (Validation) (Synthesis)
      │             │            │
      └─────────────┼────────────┘
                    │
         ┌──────────▼───────────┐
         │   Redis Bus          │
         │ (Message Queue)      │
         └──────────┬───────────┘
                    │
      ┌─────────────▼─────────────┐
      │  IF.guard Veto Layer      │
      │ (Safety checks before UX) │
      └─────────────┬─────────────┘
                    │
            OpenWebUI Chat UI
          (Displays consensus
           synthesis result)
```

### Component Stack

```
┌─────────────────────────────────────────┐
│ OpenWebUI Frontend (Chat UI)            │
├─────────────────────────────────────────┤
│ OpenWebUI Backend API                   │
├─────────────────────────────────────────┤
│ MultiAgentBridge (New)                  │  ← This integration
│ - Routing engine                        │
│ - Model registry                        │
│ - Consensus algorithm                   │
├─────────────────────────────────────────┤
│ MCP Multiagent Bridge                   │  ← Existing library
│ - HMAC authentication                   │
│ - Message queuing                       │
│ - Audit logging                         │
├─────────────────────────────────────────┤
│ Agent Communication Layer                │
│ - Model A (Claude Max)                  │
│ - Model B (DeepSeek)                    │
│ - Model C (Gemini)                      │
├─────────────────────────────────────────┤
│ Shared Memory Substrate                  │
│ - Redis (L2 Cache, conversation state)  │
│ - ChromaDB (RAG, personality DNA)       │
├─────────────────────────────────────────┤
│ IF.guard Veto Layer                      │
│ - Safety validation                      │
│ - Harmful output prevention              │
└─────────────────────────────────────────┘
```

---

## Three Swarm Patterns

### Pattern 1: Consensus Mode

**Use Case:** Complex decisions requiring multiple perspectives (security review, ethical evaluation, architectural decisions)

**Workflow:**

```
User Query: "Is this code safe for production?"
    │
    ├─→ Claude Max: Generate security analysis
    │   └─→ Result: "Risk: Medium (3 SQL injection vectors)"
    │       Confidence: 0.92
    │
    ├─→ DeepSeek: Validate findings
    │   └─→ Result: "Confirms 2 of 3 vectors, disagrees on 1"
    │       Confidence: 0.78
    │
    └─→ Gemini: Synthesize recommendations
        └─→ Result: "Risk: Medium-High (2 confirmed vectors)"
            Confidence: 0.85

CONSENSUS ALGORITHM:
- Weight each response by confidence
- Consensus threshold: 75% agreement
- If no consensus: Return all positions with confidence scores
- Output: "CONSENSUS: Medium-High Risk (2 vectors confirmed)
           Recommendation: Fix identified SQL injection patterns"
```

**Implementation:**

```python
class ConsensusPattern:
    """
    All models vote, weighted by confidence.
    Consensus = majority agreement within confidence threshold.
    """

    def __init__(self, models: List[str], threshold: float = 0.75):
        self.models = models
        self.threshold = threshold
        self.bridge = MultiAgentBridge()

    async def execute(self, query: str, context: dict) -> ConsensusResult:
        """
        Execute consensus pattern:
        1. Send query to all models in parallel
        2. Collect responses with confidence scores
        3. Calculate weighted consensus
        4. Return result with agreement metrics
        """
        # Phase 1: Parallel analysis
        tasks = []
        for model in self.models:
            task = self.bridge.route_message(
                AgentMessage(
                    from_model="openwebui",
                    to_model=model,
                    task="analyze",
                    context=context,
                    routing="broadcast"
                )
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        # Phase 2: Extract confidence scores
        scored_responses = [
            {
                "model": r.from_model,
                "position": r.result,
                "confidence": r.metadata.get("confidence", 0.5)
            }
            for r in responses
        ]

        # Phase 3: Calculate consensus
        consensus = self._calculate_weighted_consensus(scored_responses)

        # Phase 4: Apply IF.guard veto
        safe_result = await self.guard.validate(consensus)

        return ConsensusResult(
            consensus=safe_result,
            positions=scored_responses,
            agreement_percentage=consensus["agreement_score"],
            timestamp=datetime.now()
        )

    def _calculate_weighted_consensus(self, responses: list) -> dict:
        """
        Weight votes by confidence score.
        Calculate agreement percentage.
        """
        if not responses:
            return {"consensus": None, "agreement_score": 0.0}

        # Group by position
        positions = {}
        total_confidence = 0

        for r in responses:
            pos = r["position"]
            conf = r["confidence"]

            if pos not in positions:
                positions[pos] = {"weight": 0, "count": 0}

            positions[pos]["weight"] += conf
            positions[pos]["count"] += 1
            total_confidence += conf

        # Calculate agreement score
        winner = max(positions.items(), key=lambda x: x[1]["weight"])
        agreement = winner[1]["weight"] / total_confidence

        return {
            "consensus": winner[0],
            "agreement_score": agreement,
            "positions": positions,
            "confidence_threshold": self.threshold
        }
```

### Pattern 2: Delegation Mode

**Use Case:** Route task to specialist model based on capability registry

**Workflow:**

```
User Query: "Generate code to parse XML with error handling"
    │
    ├─→ Query Model Registry: "Who can do code_generation?"
    │   Response: [Claude Max (0.95), DeepSeek (0.78), Gemini (0.88)]
    │
    └─→ Route to top candidate (Claude Max with 0.95 confidence)
        └─→ Claude Max: "Here's the code..."

DELEGATION ALGORITHM:
- Query capability registry
- Rank by confidence/specialization score
- Route to highest-ranked available model
- Fallback to next-ranked if first unavailable
- Load-balance across equally-ranked models
```

**Implementation:**

```python
class DelegationPattern:
    """
    Route tasks to specialist models based on capability registry.
    Enables specialization without requiring all models for every task.
    """

    def __init__(self):
        self.bridge = MultiAgentBridge()
        self.registry = ModelRegistry()

    async def execute(self, query: str, required_capability: str,
                     context: dict) -> TaskResult:
        """
        Execute delegation pattern:
        1. Query registry for capable models
        2. Rank by specialization score
        3. Route to best-ranked model
        4. Handle unavailability with fallback
        """
        # Phase 1: Discovery
        candidates = self.registry.find_models_with_capability(
            required_capability
        )

        if not candidates:
            raise CapabilityNotFound(f"No model has {required_capability}")

        # Phase 2: Ranking (by specialization score)
        ranked = sorted(
            candidates,
            key=lambda x: x.specialization_score,
            reverse=True
        )

        # Phase 3: Routing with fallback
        for candidate in ranked:
            try:
                result = await self.bridge.route_message(
                    AgentMessage(
                        from_model="openwebui",
                        to_model=candidate.model_id,
                        task=required_capability,
                        context=context,
                        routing="direct",
                        timeout_ms=30000
                    )
                )

                # Phase 4: Apply IF.guard veto
                safe_result = await self.guard.validate(result)

                return TaskResult(
                    result=safe_result,
                    delegated_to=candidate.model_id,
                    specialization_score=candidate.specialization_score,
                    timestamp=datetime.now()
                )

            except TimeoutError:
                # Try next candidate
                continue
            except Exception as e:
                logger.warning(f"Delegation to {candidate.model_id} failed: {e}")
                continue

        # All candidates failed
        raise DelegationFailed(f"All models failed for {required_capability}")
```

**Model Registry Schema:**

```python
class ModelCapability:
    """Capability descriptor for a model"""
    model_id: str           # "claude_max" or "deepseek" or "gemini"
    capability: str         # "code_generation", "analysis", "synthesis"
    specialization_score: float  # 0.0 - 1.0 (how good is this model at this task)
    latency_ms: int        # Average response time
    error_rate: float      # 0.0 - 1.0 (recent error rate)
    availability: bool     # Is model currently online
    updated_at: datetime   # Last updated timestamp


EXAMPLE REGISTRY:
{
  "code_generation": [
    {"model_id": "claude_max", "score": 0.95, "latency": 2500, "availability": true},
    {"model_id": "gemini", "score": 0.88, "latency": 1800, "availability": true},
    {"model_id": "deepseek", "score": 0.78, "latency": 1200, "availability": true}
  ],
  "security_analysis": [
    {"model_id": "claude_max", "score": 0.92, "latency": 3200, "availability": true},
    {"model_id": "deepseek", "score": 0.85, "latency": 2100, "availability": true},
    {"model_id": "gemini", "score": 0.80, "latency": 1900, "availability": true}
  ],
  "creative_writing": [
    {"model_id": "claude_max", "score": 0.89, "latency": 2800, "availability": true},
    {"model_id": "gemini", "score": 0.91, "latency": 2000, "availability": true},
    {"model_id": "deepseek", "score": 0.72, "latency": 1500, "availability": true}
  ]
}
```

### Pattern 3: Critique Mode

**Use Case:** Quality control workflow (Model A generates, Model B critiques, Model A refines)

**Workflow:**

```
User Query: "Write a technical blog post about async/await"
    │
    ├─→ Phase 1: Generation
    │   Claude Max: "Here's a blog post..."
    │   Output: 1200 word draft
    │
    ├─→ Phase 2: Critique
    │   DeepSeek: Reviews for:
    │   - Technical accuracy ✓
    │   - Clarity for audience ⚠️ (too advanced)
    │   - Grammar/style ✓
    │   Feedback: "Needs simpler explanation of event loop"
    │
    ├─→ Phase 3: Refinement
    │   Claude Max: Incorporates feedback
    │   Output: Revised blog post with simpler event loop explanation
    │
    └─→ Phase 4: Final Validation
        DeepSeek: Confirms improvements
        Output: APPROVED with quality score 0.94
```

**Implementation:**

```python
class CritiquePattern:
    """
    Quality control workflow: Generate → Critique → Refine → Validate
    Enables iterative improvement through multi-agent feedback loops.
    """

    def __init__(self, generator_model: str, critic_model: str,
                 max_iterations: int = 3):
        self.generator = generator_model
        self.critic = critic_model
        self.max_iterations = max_iterations
        self.bridge = MultiAgentBridge()

    async def execute(self, query: str, context: dict,
                     quality_threshold: float = 0.90) -> CritiqueResult:
        """
        Execute critique pattern with iterative refinement.
        """
        current_draft = None
        iteration = 0
        quality_score = 0.0

        while iteration < self.max_iterations and quality_score < quality_threshold:
            iteration += 1
            logger.info(f"Critique iteration {iteration}/{self.max_iterations}")

            # Phase 1: Generation or refinement
            if current_draft is None:
                # Initial generation
                current_draft = await self.bridge.route_message(
                    AgentMessage(
                        from_model="openwebui",
                        to_model=self.generator,
                        task="generate",
                        context=context,
                        routing="direct"
                    )
                )

            # Phase 2: Critique
            critique = await self.bridge.route_message(
                AgentMessage(
                    from_model="openwebui",
                    to_model=self.critic,
                    task="critique",
                    context={
                        **context,
                        "draft": current_draft.result,
                        "iteration": iteration
                    },
                    routing="direct"
                )
            )

            # Extract quality score and issues
            quality_score = critique.metadata.get("quality_score", 0.0)
            issues = critique.metadata.get("issues", [])

            if quality_score >= quality_threshold:
                logger.info(f"Quality threshold reached: {quality_score}")
                break

            if not issues or iteration >= self.max_iterations:
                logger.warning(f"Max iterations reached or no issues found")
                break

            # Phase 3: Refinement
            refinement = await self.bridge.route_message(
                AgentMessage(
                    from_model="openwebui",
                    to_model=self.generator,
                    task="refine",
                    context={
                        **context,
                        "draft": current_draft.result,
                        "critique": critique.result,
                        "issues": issues
                    },
                    routing="direct"
                )
            )

            current_draft = refinement

        # Phase 4: Final validation with IF.guard
        safe_result = await self.guard.validate(current_draft)

        return CritiqueResult(
            result=safe_result,
            iterations=iteration,
            quality_score=quality_score,
            generator=self.generator,
            critic=self.critic,
            timestamp=datetime.now()
        )
```

---

## AgentMessage Interface

**Core messaging structure for all swarm patterns:**

```python
@dataclass
class AgentMessage:
    """
    Message format for agent-to-agent communication.
    Follows IF.TTT (Traceable, Transparent, Trustworthy) standards.
    """
    # Sender information
    from_model: str                    # "claude_max", "deepseek", "gemini", "openwebui"
    from_agent_id: Optional[str] = None  # For swarm coordination (e.g., "haiku_worker_15")

    # Recipient information
    to_model: str                      # Target model
    to_agent_id: Optional[str] = None  # Target agent (for direct routing)

    # Task specification
    task: str                          # "analyze", "generate", "critique", "validate"
    task_payload: dict = field(default_factory=dict)  # Task-specific data

    # Context
    context: dict = field(default_factory=dict)  # User query, conversation history, etc.

    # Routing specification
    routing: Literal["direct", "broadcast", "consensus"] = "direct"
    #   - "direct": Send to single target model
    #   - "broadcast": Send to multiple models (consensus pattern)
    #   - "consensus": Send to all, wait for agreement

    # Timeouts and deadlines
    timeout_ms: int = 30000            # Max wait time in milliseconds

    # Traceability (IF.TTT)
    message_id: str = field(default_factory=lambda: str(uuid4()))
    parent_message_id: Optional[str] = None  # For threading
    conversation_id: str = ""          # Links to OpenWebUI conversation
    request_id: str = ""               # Links to original user request

    # Authentication
    signature: Optional[str] = None    # HMAC-SHA256 signature
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Metadata
    metadata: dict = field(default_factory=dict)
    #   - "confidence": float (0.0-1.0) - model's confidence in response
    #   - "model_version": str - version of model used
    #   - "latency_ms": int - time to generate response
    #   - "token_count": int - tokens consumed

    def sign(self, secret: str) -> None:
        """
        Sign message with HMAC-SHA256 for authentication.
        Required before sending through bridge.
        """
        message_bytes = json.dumps({
            "from_model": self.from_model,
            "to_model": self.to_model,
            "task": self.task,
            "timestamp": self.timestamp,
            "message_id": self.message_id
        }, sort_keys=True).encode()

        secret_bytes = secret.encode()
        self.signature = hmac.new(
            secret_bytes,
            message_bytes,
            hashlib.sha256
        ).hexdigest()

    def validate_signature(self, secret: str) -> bool:
        """Verify HMAC signature on received message"""
        if not self.signature:
            return False

        message_bytes = json.dumps({
            "from_model": self.from_model,
            "to_model": self.to_model,
            "task": self.task,
            "timestamp": self.timestamp,
            "message_id": self.message_id
        }, sort_keys=True).encode()

        secret_bytes = secret.encode()
        expected_sig = hmac.new(
            secret_bytes,
            message_bytes,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(self.signature, expected_sig)


@dataclass
class AgentResponse:
    """Response from a model to an AgentMessage"""

    # Sender identification
    from_model: str
    from_agent_id: Optional[str] = None

    # Message linking
    in_response_to: str                # message_id of original request
    response_id: str = field(default_factory=lambda: str(uuid4()))

    # Result
    result: str                        # The actual response/output
    result_type: Literal["text", "json", "structured"] = "text"

    # Quality metrics
    metadata: dict = field(default_factory=dict)
    #   - "confidence": float (0.0-1.0)
    #   - "latency_ms": int
    #   - "token_count": int
    #   - "model_version": str
    #   - "quality_score": float (for critique patterns)

    # Traceability
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    signature: Optional[str] = None

    def sign(self, secret: str) -> None:
        """Sign response with HMAC-SHA256"""
        message_bytes = json.dumps({
            "from_model": self.from_model,
            "in_response_to": self.in_response_to,
            "response_id": self.response_id,
            "timestamp": self.timestamp
        }, sort_keys=True).encode()

        secret_bytes = secret.encode()
        self.signature = hmac.new(
            secret_bytes,
            message_bytes,
            hashlib.sha256
        ).hexdigest()
```

---

## MultiAgentBridge Implementation

**Core orchestration class that manages routing, consensus, and error handling:**

```python
class MultiAgentBridge:
    """
    Orchestrates multi-model swarm coordination.

    Responsibilities:
    1. Route messages to target models via mcp-multiagent-bridge
    2. Manage consensus patterns (voting with confidence weighting)
    3. Handle delegation to specialist models
    4. Execute critique loops with iterative refinement
    5. Apply IF.guard veto layer before returning results
    """

    def __init__(self, bridge_url: str = "http://localhost:8001",
                 bridge_secret: str = "",
                 redis_client: Optional[redis.Redis] = None,
                 chromadb_client: Optional[chromadb.Client] = None):
        """
        Initialize MultiAgentBridge.

        Args:
            bridge_url: URL of mcp-multiagent-bridge server
            bridge_secret: HMAC secret for signing messages
            redis_client: Redis client for caching & state
            chromadb_client: ChromaDB client for RAG
        """
        self.bridge_url = bridge_url
        self.bridge_secret = bridge_secret
        self.redis = redis_client or redis.Redis(host='localhost', port=6379)
        self.chromadb = chromadb_client
        self.logger = logging.getLogger(__name__)

        # Model registry (maps capability -> models)
        self.registry = self._load_registry()

        # Pattern implementations
        self.consensus = ConsensusPattern()
        self.delegation = DelegationPattern()
        self.critique = CritiquePattern()

        # IF.guard veto layer
        self.guard = IFGuardValidator()

    async def route_message(self, message: AgentMessage) -> AgentResponse:
        """
        Route message based on routing strategy.

        Strategies:
        - "direct": Send to single model, wait for response
        - "broadcast": Send to multiple models in parallel
        - "consensus": Send to all, calculate weighted consensus

        Returns:
            AgentResponse with result and metadata
        """
        # Validate message format
        if not self._validate_message(message):
            raise ValueError("Invalid message format")

        # Sign message
        message.sign(self.bridge_secret)

        # Route based on strategy
        if message.routing == "direct":
            return await self._route_direct(message)
        elif message.routing == "broadcast":
            return await self._route_broadcast(message)
        elif message.routing == "consensus":
            return await self.consensus.execute(
                message.context.get("query", ""),
                message.context,
                models=[message.to_model]  # or list of models from registry
            )
        else:
            raise ValueError(f"Unknown routing strategy: {message.routing}")

    async def _route_direct(self, message: AgentMessage) -> AgentResponse:
        """
        Direct routing: Send to single model, wait for response.
        """
        try:
            # Send message to mcp-multiagent-bridge
            response = await self._send_to_bridge(message)

            # Verify signature
            if not self._verify_response(response):
                raise SecurityError("Response signature verification failed")

            # Apply IF.guard veto
            safe_response = await self.guard.validate(response)

            # Cache in Redis (for consistency across models)
            self._cache_response(message.message_id, safe_response)

            return safe_response

        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout routing to {message.to_model}")
            raise TimeoutError(f"No response from {message.to_model} within {message.timeout_ms}ms")
        except Exception as e:
            self.logger.error(f"Error routing message: {e}")
            raise

    async def _route_broadcast(self, message: AgentMessage) -> dict:
        """
        Broadcast routing: Send to multiple models in parallel.
        Returns all responses (used by consensus pattern).
        """
        # Get all models if not specified
        if not message.to_model:
            models = self._get_all_models()
        else:
            models = [message.to_model]

        # Send to all models in parallel
        tasks = [
            self._route_direct(
                AgentMessage(
                    from_model=message.from_model,
                    to_model=model,
                    task=message.task,
                    context=message.context,
                    routing="direct",
                    timeout_ms=message.timeout_ms,
                    conversation_id=message.conversation_id
                )
            )
            for model in models
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out errors, keep valid responses
        valid_responses = [
            r for r in responses
            if not isinstance(r, Exception)
        ]

        return {
            "responses": valid_responses,
            "total": len(models),
            "successful": len(valid_responses),
            "failed": len(models) - len(valid_responses)
        }

    async def _send_to_bridge(self, message: AgentMessage) -> AgentResponse:
        """
        Send message to mcp-multiagent-bridge via HTTP.
        """
        async with aiohttp.ClientSession() as session:
            payload = {
                "from_model": message.from_model,
                "to_model": message.to_model,
                "task": message.task,
                "context": message.context,
                "message_id": message.message_id,
                "signature": message.signature,
                "timestamp": message.timestamp
            }

            try:
                async with session.post(
                    f"{self.bridge_url}/route",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(milliseconds=message.timeout_ms)
                ) as resp:
                    if resp.status != 200:
                        raise HTTPError(f"Bridge returned {resp.status}")

                    data = await resp.json()
                    return AgentResponse(
                        from_model=data["from_model"],
                        in_response_to=message.message_id,
                        result=data["result"],
                        metadata=data.get("metadata", {})
                    )

            except asyncio.TimeoutError:
                raise TimeoutError(f"Bridge timeout after {message.timeout_ms}ms")

    def _validate_message(self, message: AgentMessage) -> bool:
        """Validate message format and required fields"""
        required = ["from_model", "to_model", "task", "routing"]
        return all(getattr(message, field, None) for field in required)

    def _verify_response(self, response: AgentResponse) -> bool:
        """Verify response signature"""
        if not response.signature:
            return False
        return response.signature == self._compute_signature(response)

    def _compute_signature(self, response: AgentResponse) -> str:
        """Compute expected signature for response"""
        message_bytes = json.dumps({
            "from_model": response.from_model,
            "in_response_to": response.in_response_to,
            "response_id": response.response_id,
            "timestamp": response.timestamp
        }, sort_keys=True).encode()

        secret_bytes = self.bridge_secret.encode()
        return hmac.new(secret_bytes, message_bytes, hashlib.sha256).hexdigest()

    def _cache_response(self, message_id: str, response: AgentResponse):
        """Cache response in Redis for consistency"""
        key = f"agent_response:{message_id}"
        self.redis.setex(
            key,
            3600,  # 1 hour TTL
            json.dumps(asdict(response), default=str)
        )

    def _load_registry(self) -> dict:
        """Load model capability registry from Redis or file"""
        # Try Redis first
        cached = self.redis.get("model_registry")
        if cached:
            return json.loads(cached)

        # Fall back to default registry
        return self._default_registry()

    def _default_registry(self) -> dict:
        """Default model capability registry"""
        return {
            "code_generation": [
                {"model": "claude_max", "score": 0.95},
                {"model": "gemini", "score": 0.88},
                {"model": "deepseek", "score": 0.78}
            ],
            "analysis": [
                {"model": "claude_max", "score": 0.92},
                {"model": "deepseek", "score": 0.85},
                {"model": "gemini", "score": 0.80}
            ],
            "synthesis": [
                {"model": "claude_max", "score": 0.89},
                {"model": "gemini", "score": 0.91},
                {"model": "deepseek", "score": 0.72}
            ]
        }

    def _get_all_models(self) -> List[str]:
        """Get list of all available models"""
        models = set()
        for capability_models in self.registry.values():
            for model_info in capability_models:
                models.add(model_info["model"])
        return sorted(list(models))
```

---

## OpenWebUI Integration

**How to integrate MultiAgentBridge into OpenWebUI:**

### Option 1: OpenWebUI Function (Recommended)

```python
# openwebui_multiagent_function.py
# Install as OpenWebUI Function plugin

from typing import Optional
import json
from multiagent_bridge import MultiAgentBridge, AgentMessage

class Pipe:
    """
    OpenWebUI Function for multi-model swarm coordination.

    Usage in chat:
    ```
    @multiagent-consensus: "Analyze this code for security issues"
    @multiagent-delegate: code_generation "Write async/await example"
    @multiagent-critique: "Write a blog post about X"
    ```
    """

    def __init__(self):
        self.bridge = MultiAgentBridge(
            bridge_url="http://localhost:8001",
            bridge_secret=os.getenv("BRIDGE_SECRET")
        )
        self.patterns = {
            "consensus": self.bridge.consensus,
            "delegate": self.bridge.delegation,
            "critique": self.bridge.critique
        }

    def pipe(self, body: dict) -> str:
        """
        Process message through OpenWebUI.

        body:
        {
            "messages": [...],
            "model": "gpt-4",
            "stream": false
        }
        """

        # Extract pattern from special marker
        last_message = body["messages"][-1]["content"]
        pattern = self._extract_pattern(last_message)

        if pattern in self.patterns:
            # Extract query (remove pattern marker)
            query = self._extract_query(last_message, pattern)

            # Execute swarm pattern
            result = asyncio.run(
                self.patterns[pattern].execute(query, {})
            )

            # Format response
            if pattern == "consensus":
                return self._format_consensus(result)
            elif pattern == "delegate":
                return self._format_delegation(result)
            elif pattern == "critique":
                return self._format_critique(result)

        # Fall back to single-model response
        return self._single_model_response(body)

    def _extract_pattern(self, message: str) -> Optional[str]:
        """Extract pattern from message"""
        patterns = ["consensus", "delegate", "critique"]
        for p in patterns:
            if f"@multiagent-{p}" in message:
                return p
        return None

    def _extract_query(self, message: str, pattern: str) -> str:
        """Remove pattern marker from message"""
        marker = f"@multiagent-{pattern}:"
        return message.replace(marker, "").strip()

    def _format_consensus(self, result) -> str:
        """Format consensus result for OpenWebUI display"""
        return f"""
MULTI-MODEL CONSENSUS

**Consensus Result:**
{result.consensus}

**Agreement Score:** {result.agreement_score:.1%}

**Individual Positions:**
{json.dumps(result.positions, indent=2)}

**Models:** Claude Max, DeepSeek, Gemini
"""

    def _format_delegation(self, result) -> str:
        """Format delegation result"""
        return f"""
DELEGATED TO SPECIALIST: {result.delegated_to.upper()}

{result.result}

*(Routed to {result.delegated_to} - specialization: {result.specialization_score:.1%})*
"""

    def _format_critique(self, result) -> str:
        """Format critique result"""
        return f"""
ITERATIVELY REFINED OUTPUT

{result.result}

*(Quality Score: {result.quality_score:.1%}, Iterations: {result.iterations})*
"""
```

### Option 2: OpenWebUI Middleware

```python
# openwebui_multiagent_middleware.py
# Install as OpenWebUI middleware plugin

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class MultiAgentMiddleware(BaseHTTPMiddleware):
    """
    Middleware that intercepts OpenWebUI chat requests
    and routes through MultiAgentBridge if needed.
    """

    def __init__(self, app):
        super().__init__(app)
        self.bridge = MultiAgentBridge()

    async def dispatch(self, request: Request, call_next):
        # Only intercept chat API calls
        if "/api/chat/completions" not in request.url.path:
            return await call_next(request)

        # Parse request body
        body = await request.json()

        # Check for swarm pattern markers
        if self._should_use_swarm(body):
            # Extract pattern and execute
            result = await self._execute_swarm(body)

            # Return swarm result
            return JSONResponse(content=result)

        # Otherwise proceed normally
        return await call_next(request)

    def _should_use_swarm(self, body: dict) -> bool:
        """Check if request should use swarm coordination"""
        # Check for special markers in system prompt or messages
        system = body.get("system", "")
        return any(marker in system for marker in ["consensus", "delegate", "critique"])

    async def _execute_swarm(self, body: dict) -> dict:
        """Execute swarm pattern and return OpenAI-compatible response"""
        # Implementation similar to Function approach above
        pass
```

### Option 3: Standalone REST API

```python
# multiagent_api.py
# Deploy as separate microservice integrated with OpenWebUI

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
bridge = MultiAgentBridge()

class SwarmRequest(BaseModel):
    pattern: str  # "consensus" | "delegate" | "critique"
    query: str
    models: Optional[List[str]] = None
    context: Optional[dict] = None

@app.post("/swarm/execute")
async def execute_swarm(request: SwarmRequest):
    """Execute swarm pattern and return result"""

    if request.pattern == "consensus":
        result = await bridge.consensus.execute(request.query, request.context or {})
        return {"status": "success", "result": asdict(result)}

    elif request.pattern == "delegate":
        capability = request.context.get("capability", "")
        result = await bridge.delegation.execute(request.query, capability, request.context or {})
        return {"status": "success", "result": asdict(result)}

    elif request.pattern == "critique":
        result = await bridge.critique.execute(request.query, request.context or {})
        return {"status": "success", "result": asdict(result)}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown pattern: {request.pattern}")

@app.get("/models/registry")
async def get_registry():
    """Return model capability registry"""
    return bridge.registry

@app.put("/models/registry")
async def update_registry(registry: dict):
    """Update model capability registry"""
    bridge.redis.set("model_registry", json.dumps(registry))
    return {"status": "success"}
```

---

## Error Handling & Recovery

### Error Classes

```python
class SwarmException(Exception):
    """Base class for all swarm-related errors"""
    pass

class CapabilityNotFound(SwarmException):
    """No model has required capability"""
    pass

class DelegationFailed(SwarmException):
    """All delegation candidates failed"""
    pass

class ConsensusTimeout(SwarmException):
    """Models failed to reach consensus within timeout"""
    pass

class SecurityError(SwarmException):
    """Message signature verification failed"""
    pass

class ModelUnavailable(SwarmException):
    """Target model is offline or unreachable"""
    pass
```

### Graceful Degradation

```python
class ErrorRecovery:
    """Handles errors with graceful degradation"""

    @staticmethod
    async def handle_model_timeout(original_message: AgentMessage) -> Optional[AgentResponse]:
        """
        When model times out:
        1. Try next-ranked model (if delegation)
        2. Fall back to single-model response
        3. Return cached previous response
        """

        # Try fallback models
        fallback_models = ["claude_max", "gemini", "deepseek"]
        for model in fallback_models:
            if model != original_message.to_model:
                try:
                    fallback_msg = AgentMessage(
                        from_model=original_message.from_model,
                        to_model=model,
                        task=original_message.task,
                        context=original_message.context,
                        routing="direct",
                        timeout_ms=20000  # Shorter timeout for fallback
                    )
                    return await bridge.route_message(fallback_msg)
                except Exception:
                    continue

        # If all fallbacks fail, return cached response
        cached = redis.get(f"agent_response:{original_message.message_id}")
        if cached:
            return json.loads(cached)

        # Final fallback: single-model response
        return None

    @staticmethod
    async def handle_consensus_failure(responses: List[AgentResponse]) -> dict:
        """
        When consensus fails (no agreement):
        Return all positions with confidence scores
        Let user decide
        """
        return {
            "consensus": "NO_AGREEMENT",
            "message": "Models disagreed - presenting all positions",
            "positions": [asdict(r) for r in responses],
            "recommendation": "Review all positions and choose manually"
        }

    @staticmethod
    async def handle_guard_rejection(result: AgentResponse) -> str:
        """
        When IF.guard veto rejects output:
        Return sanitized version or explanation
        """
        return f"""
⚠️ Safety Check Failed

The model's response was blocked by IF.guard safety validation.

**Reason:** {result.metadata.get("guard_reason", "Content policy violation")}

**Recommendation:**
- Rephrase your question
- Ask the model to avoid problematic content
- Request a different perspective on the topic
"""
```

---

## Security Considerations

### Authentication & Authorization

1. **HMAC-SHA256 Signing**
   - All messages signed with shared secret
   - Prevents message tampering
   - Timestamps prevent replay attacks

2. **Secret Redaction**
   - Automatic detection of API keys, passwords, tokens
   - Redacted before logging or caching
   - Patterns: AWS keys, private keys, Bearer tokens, passwords, API keys

3. **Rate Limiting**
   - 10 requests/minute per model
   - 100 requests/hour per conversation
   - 500 requests/day per user
   - Prevents abuse and accidental loops

### IF.Guard Integration

```python
class IFGuardValidator:
    """
    IF.guard veto layer prevents harmful outputs.
    Runs AFTER model generation, BEFORE user display.
    """

    async def validate(self, response: AgentResponse) -> AgentResponse:
        """
        Check response against safety policies:
        - No hate speech
        - No violence encouragement
        - No personal data exposure
        - No illegal content
        """

        result = response.result

        # Policy checks
        checks = [
            self._check_hate_speech(result),
            self._check_violence(result),
            self._check_personal_data(result),
            self._check_illegal_content(result)
        ]

        for passed, reason in checks:
            if not passed:
                response.metadata["guard_reason"] = reason
                response.result = f"[Safety blocked: {reason}]"
                return response

        # If all checks pass, approve
        response.metadata["guard_approved"] = True
        return response
```

---

## Testing & Validation

### Unit Tests

```python
import pytest

class TestMultiAgentBridge:

    @pytest.mark.asyncio
    async def test_direct_routing(self):
        """Test direct message routing"""
        bridge = MultiAgentBridge()
        msg = AgentMessage(
            from_model="openwebui",
            to_model="claude_max",
            task="analyze",
            context={"query": "Test message"},
            routing="direct"
        )
        response = await bridge.route_message(msg)
        assert response.from_model == "claude_max"
        assert response.result is not None

    @pytest.mark.asyncio
    async def test_consensus_pattern(self):
        """Test consensus voting with confidence weighting"""
        pattern = ConsensusPattern(
            models=["claude_max", "deepseek", "gemini"]
        )
        result = await pattern.execute(
            "Is this code secure?",
            context={"code": "SELECT * FROM users"}
        )
        assert hasattr(result, 'consensus')
        assert 0 <= result.agreement_percentage <= 1

    @pytest.mark.asyncio
    async def test_delegation_pattern(self):
        """Test capability-based delegation"""
        pattern = DelegationPattern()
        result = await pattern.execute(
            "Write Python code for async/await",
            "code_generation",
            context={}
        )
        assert result.delegated_to in ["claude_max", "gemini", "deepseek"]

    @pytest.mark.asyncio
    async def test_critique_pattern(self):
        """Test iterative refinement"""
        pattern = CritiquePattern(
            generator_model="claude_max",
            critic_model="deepseek"
        )
        result = await pattern.execute(
            "Write a blog post about async/await",
            context={}
        )
        assert result.iterations >= 1
        assert result.quality_score >= 0.8

    def test_message_signing(self):
        """Test HMAC signature generation"""
        msg = AgentMessage(
            from_model="openwebui",
            to_model="claude_max",
            task="test",
            context={},
            routing="direct"
        )
        msg.sign("secret_key")
        assert msg.signature is not None
        assert len(msg.signature) == 64  # SHA256 hex

    def test_message_signature_validation(self):
        """Test signature verification"""
        msg = AgentMessage(
            from_model="openwebui",
            to_model="claude_max",
            task="test",
            context={},
            routing="direct"
        )
        msg.sign("secret_key")
        assert msg.validate_signature("secret_key") == True
        assert msg.validate_signature("wrong_key") == False
```

### Integration Tests

```python
class TestOpenWebUIIntegration:

    @pytest.mark.asyncio
    async def test_openwebui_function_consensus(self):
        """Test OpenWebUI Function executing consensus pattern"""
        pipe = Pipe()

        body = {
            "messages": [
                {"role": "user", "content": '@multiagent-consensus: "Analyze code for bugs"'}
            ],
            "model": "gpt-4"
        }

        response = pipe.pipe(body)
        assert "CONSENSUS" in response
        assert "Agreement Score" in response

    @pytest.mark.asyncio
    async def test_redis_caching(self):
        """Test response caching in Redis"""
        bridge = MultiAgentBridge()
        msg = AgentMessage(
            from_model="openwebui",
            to_model="claude_max",
            task="test",
            context={},
            routing="direct",
            message_id="test_msg_001"
        )

        response = await bridge.route_message(msg)
        cached = bridge.redis.get("agent_response:test_msg_001")

        assert cached is not None
        assert json.loads(cached)["result"] == response.result
```

### Load Testing

```python
import asyncio
import time

async def load_test_consensus():
    """Stress test: 100 concurrent consensus requests"""
    bridge = MultiAgentBridge()

    async def single_request():
        msg = AgentMessage(
            from_model="openwebui",
            to_model="claude_max",
            task="analyze",
            context={"query": "Test code analysis"},
            routing="consensus"
        )
        return await bridge.route_message(msg)

    start = time.time()
    tasks = [single_request() for _ in range(100)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    elapsed = time.time() - start

    successful = sum(1 for r in results if not isinstance(r, Exception))
    failed = sum(1 for r in results if isinstance(r, Exception))

    print(f"Consensus Load Test Results:")
    print(f"  Total: 100 requests")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Average latency: {(elapsed/100)*1000:.1f}ms")
```

---

## Implementation Checklist

### Phase 1: Foundation (Week 1-2)

- [ ] Set up mcp-multiagent-bridge server on localhost:8001
- [ ] Generate BRIDGE_SECRET with `openssl rand -hex 32`
- [ ] Test bridge connectivity with `bridge_cli.py show`
- [ ] Implement AgentMessage and AgentResponse dataclasses
- [ ] Implement MultiAgentBridge core routing logic
- [ ] Write unit tests for message signing/validation
- [ ] Deploy Redis client with L1/L2 caching
- [ ] Set up audit logging to JSONL format

### Phase 2: Swarm Patterns (Week 2-3)

- [ ] Implement ConsensusPattern (voting with confidence weighting)
- [ ] Implement DelegationPattern (capability-based routing)
- [ ] Implement CritiquePattern (iterative refinement)
- [ ] Test all patterns with single model first
- [ ] Test consensus with 3 models (Claude, DeepSeek, Gemini)
- [ ] Test delegation to specialist models
- [ ] Test critique loop convergence (max 3 iterations)
- [ ] Write integration tests for each pattern

### Phase 3: OpenWebUI Integration (Week 3-4)

- [ ] Create openwebui_multiagent_function.py
- [ ] Register function in OpenWebUI admin panel
- [ ] Test function with @multiagent-consensus marker
- [ ] Test function with @multiagent-delegate marker
- [ ] Test function with @multiagent-critique marker
- [ ] Add response formatting (consensus, delegation, critique)
- [ ] Write OpenWebUI integration tests
- [ ] Document usage examples in OpenWebUI help

### Phase 4: Security & Error Handling (Week 4)

- [ ] Implement IF.guard veto layer
- [ ] Add secret redaction patterns (API keys, passwords, tokens)
- [ ] Implement rate limiting (10 req/min, 100 req/hr, 500 req/day)
- [ ] Implement graceful degradation (fallback models)
- [ ] Add error recovery for timeouts and unavailability
- [ ] Write security tests for authentication and authorization
- [ ] Create error handling documentation
- [ ] Test all error paths with chaos testing

### Phase 5: Performance & Production (Week 5+)

- [ ] Load test with 100+ concurrent requests
- [ ] Benchmark consensus pattern (target: <100ms)
- [ ] Benchmark delegation pattern (target: <50ms)
- [ ] Benchmark critique pattern (target: <5s per iteration)
- [ ] Profile Redis caching efficiency
- [ ] Monitor latency with prometheus metrics
- [ ] Set up alerting for failures
- [ ] Document production deployment guide

---

## IF.TTT Citations

**Empiricist Guardian Validation** (from OpenWebUI debate):
- mcp-multiagent-bridge is production-validated (10-agent stress test, Nov 2025)
- ChromaDB + Redis backends confirmed working
- Consensus pattern experimentally viable (70% confidence in swarm validation)
- **Citation:** `if://conversation/openwebui-touchable-interface-2025-11-30` (line 374)

**Philosopher Guardian Perspective** (Heidegger Tool Analysis):
- OpenWebUI as "ready-to-hand" invisible substrate (backend infrastructure)
- if.emotion React frontend as phenomenological interface (user-facing UX)
- Recommendation: Dual-stack architecture (line 398)
- **Citation:** `if://conversation/openwebui-touchable-interface-2025-11-30` (line 390)

**IF.guard Integration**:
- Safety veto layer prevents harmful outputs before display
- Automatic secret redaction for API keys, passwords, tokens
- Rate limiting prevents abuse and accidental loops
- **Citation:** `if://doc/IF-SWARM-S2-COMMS/2025-11-18` (security layer)

**Cross-Swarm Coordination**:
- Direct Haiku-to-Haiku messaging via Redis Bus (50ms latency vs 200ms coordinator routing)
- Capability-based routing enables agent specialization
- Audit trails for IF.TTT compliance
- **Citation:** `if://doc/cross-swarm-coordination/2025-11-30` (line 105)

---

## Appendix A: Example Workflow

```python
# Example: Code security review using consensus pattern

from multiagent_bridge import MultiAgentBridge, AgentMessage

async def review_code_security(code_snippet: str):
    """
    Review code for security issues using 3-model consensus.
    """
    bridge = MultiAgentBridge(
        bridge_secret=os.getenv("BRIDGE_SECRET")
    )

    # Execute consensus pattern
    result = await bridge.consensus.execute(
        query="Analyze this code for security issues",
        context={
            "code": code_snippet,
            "language": "python"
        },
        models=["claude_max", "deepseek", "gemini"]
    )

    # Display results
    print(f"\n🔒 Security Review Results\n")
    print(f"Consensus: {result.consensus}")
    print(f"Agreement: {result.agreement_percentage:.1%}\n")

    print("Individual Assessments:")
    for position, details in result.positions.items():
        print(f"  {position}: {details['count']} model(s) (weight: {details['weight']:.2f})")

    return result
```

---

**End of Document**

Version: 1.0
Last Updated: 2025-11-30
Status: Ready for Implementation
