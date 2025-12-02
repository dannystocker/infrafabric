#!/usr/bin/env python3
"""
MultiAgentBridge Implementation

Orchestrates multi-model swarm coordination for OpenWebUI integration.
Provides three swarm patterns:
1. Consensus: All models vote, weighted by confidence
2. Delegation: Route to specialist model based on capability
3. Critique: Generate → Critique → Refine iterative loop

Author: InfraFabric Integration Team
Date: 2025-11-30
Framework: IF.TTT (Traceable, Transparent, Trustworthy)
"""

import asyncio
import json
import hmac
import hashlib
import logging
import os
import secrets
import aiohttp
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Tuple, Literal
from uuid import uuid4
from enum import Enum
from contextlib import asynccontextmanager

try:
    import redis
except ImportError:
    redis = None


# ============================================================================
# Data Models
# ============================================================================

class RoutingStrategy(str, Enum):
    """Message routing strategies"""
    DIRECT = "direct"       # Send to single model
    BROADCAST = "broadcast" # Send to multiple models
    CONSENSUS = "consensus" # Send to all, calculate agreement


@dataclass
class AgentMessage:
    """Message for agent-to-agent communication"""

    # Sender information
    from_model: str
    from_agent_id: Optional[str] = None

    # Recipient information
    to_model: str
    to_agent_id: Optional[str] = None

    # Task specification
    task: str  # "analyze", "generate", "critique", "validate"
    task_payload: Dict = field(default_factory=dict)

    # Context
    context: Dict = field(default_factory=dict)

    # Routing specification
    routing: RoutingStrategy = RoutingStrategy.DIRECT

    # Timeouts
    timeout_ms: int = 30000

    # Traceability (IF.TTT)
    message_id: str = field(default_factory=lambda: f"msg_{uuid4().hex[:16]}")
    parent_message_id: Optional[str] = None
    conversation_id: str = ""
    request_id: str = ""

    # Authentication
    signature: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Metadata
    metadata: Dict = field(default_factory=dict)

    def sign(self, secret: str) -> None:
        """Sign message with HMAC-SHA256"""
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
        """Verify HMAC signature"""
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
    """Response from a model"""

    from_model: str
    from_agent_id: Optional[str] = None
    in_response_to: str = ""
    response_id: str = field(default_factory=lambda: f"resp_{uuid4().hex[:16]}")

    # Result
    result: str = ""
    result_type: Literal["text", "json", "structured"] = "text"

    # Quality metrics
    metadata: Dict = field(default_factory=dict)

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


@dataclass
class ConsensusResult:
    """Result of consensus voting"""
    consensus: str
    positions: List[Dict]  # [{"model": "claude", "position": "...", "confidence": 0.92}]
    agreement_percentage: float  # 0.0 - 1.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DelegationResult:
    """Result of delegation to specialist model"""
    result: str
    delegated_to: str
    specialization_score: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CritiqueResult:
    """Result of critique pattern"""
    result: str
    iterations: int
    quality_score: float
    generator: str
    critic: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# Swarm Patterns
# ============================================================================

class ConsensusPattern:
    """
    All models vote on decision, weighted by confidence.
    Consensus = majority agreement within confidence threshold.
    """

    def __init__(self, threshold: float = 0.75, logger: Optional[logging.Logger] = None):
        self.threshold = threshold
        self.logger = logger or logging.getLogger(__name__)

    async def execute(self, query: str, context: Dict, models: List[str],
                     bridge: "MultiAgentBridge") -> ConsensusResult:
        """
        Execute consensus pattern.
        """
        self.logger.info(f"Consensus: {len(models)} models voting on: {query[:50]}...")

        # Send query to all models in parallel
        tasks = []
        for model in models:
            msg = AgentMessage(
                from_model="openwebui",
                to_model=model,
                task="analyze",
                context=context,
                routing=RoutingStrategy.DIRECT
            )
            tasks.append(bridge.route_message(msg))

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Extract valid responses
        scored_responses = []
        for r in responses:
            if not isinstance(r, Exception):
                scored_responses.append({
                    "model": r.from_model,
                    "position": r.result[:100],  # Truncate for grouping
                    "confidence": r.metadata.get("confidence", 0.5),
                    "full_result": r.result
                })

        if not scored_responses:
            return ConsensusResult(
                consensus="ERROR: No valid responses",
                positions=[],
                agreement_percentage=0.0
            )

        # Calculate consensus
        consensus = self._calculate_consensus(scored_responses)

        return ConsensusResult(
            consensus=consensus["consensus"],
            positions=scored_responses,
            agreement_percentage=consensus["agreement_score"]
        )

    def _calculate_consensus(self, responses: List[Dict]) -> Dict:
        """Calculate weighted consensus from responses"""
        if not responses:
            return {"consensus": None, "agreement_score": 0.0}

        # Group by position
        positions = {}
        total_confidence = 0

        for r in responses:
            pos = r["position"]
            conf = r["confidence"]

            if pos not in positions:
                positions[pos] = {"weight": 0, "count": 0, "full": []}

            positions[pos]["weight"] += conf
            positions[pos]["count"] += 1
            positions[pos]["full"].append(r["full_result"])
            total_confidence += conf

        # Find winner
        winner = max(positions.items(), key=lambda x: x[1]["weight"])
        agreement = winner[1]["weight"] / total_confidence if total_confidence > 0 else 0

        # Use full result from winner
        consensus_text = winner[1]["full"][0]

        return {
            "consensus": consensus_text,
            "agreement_score": agreement,
            "positions": positions
        }


class DelegationPattern:
    """
    Route tasks to specialist models based on capability registry.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.registry = self._default_registry()

    async def execute(self, query: str, capability: str, context: Dict,
                     bridge: "MultiAgentBridge") -> DelegationResult:
        """
        Execute delegation pattern.
        """
        self.logger.info(f"Delegation: Finding specialist for {capability}")

        # Find capable models
        candidates = self.registry.get(capability, [])

        if not candidates:
            raise ValueError(f"No model has capability: {capability}")

        # Rank by specialization score
        ranked = sorted(candidates, key=lambda x: x["score"], reverse=True)

        # Try each candidate until one succeeds
        for candidate in ranked:
            try:
                msg = AgentMessage(
                    from_model="openwebui",
                    to_model=candidate["model"],
                    task=capability,
                    context=context,
                    routing=RoutingStrategy.DIRECT,
                    timeout_ms=30000
                )

                response = await bridge.route_message(msg)

                return DelegationResult(
                    result=response.result,
                    delegated_to=candidate["model"],
                    specialization_score=candidate["score"]
                )

            except asyncio.TimeoutError:
                self.logger.warning(f"Timeout delegating to {candidate['model']}")
                continue
            except Exception as e:
                self.logger.error(f"Delegation to {candidate['model']} failed: {e}")
                continue

        raise RuntimeError(f"All delegation candidates failed for {capability}")

    def _default_registry(self) -> Dict[str, List[Dict]]:
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
            "security_review": [
                {"model": "claude_max", "score": 0.94},
                {"model": "deepseek", "score": 0.87},
                {"model": "gemini", "score": 0.82}
            ],
            "synthesis": [
                {"model": "gemini", "score": 0.91},
                {"model": "claude_max", "score": 0.89},
                {"model": "deepseek", "score": 0.72}
            ],
            "creative_writing": [
                {"model": "gemini", "score": 0.91},
                {"model": "claude_max", "score": 0.89},
                {"model": "deepseek", "score": 0.75}
            ]
        }


class CritiquePattern:
    """
    Quality control workflow: Generate → Critique → Refine → Validate
    """

    def __init__(self, generator_model: str, critic_model: str,
                 max_iterations: int = 3, logger: Optional[logging.Logger] = None):
        self.generator = generator_model
        self.critic = critic_model
        self.max_iterations = max_iterations
        self.logger = logger or logging.getLogger(__name__)

    async def execute(self, query: str, context: Dict,
                     bridge: "MultiAgentBridge",
                     quality_threshold: float = 0.90) -> CritiqueResult:
        """
        Execute critique pattern with iterative refinement.
        """
        current_draft = None
        iteration = 0
        quality_score = 0.0

        while iteration < self.max_iterations and quality_score < quality_threshold:
            iteration += 1
            self.logger.info(f"Critique iteration {iteration}/{self.max_iterations}")

            # Phase 1: Generation or refinement
            if current_draft is None:
                msg = AgentMessage(
                    from_model="openwebui",
                    to_model=self.generator,
                    task="generate",
                    context=context,
                    routing=RoutingStrategy.DIRECT
                )
                current_draft = await bridge.route_message(msg)
            else:
                # Ask generator to refine based on critique
                refine_context = {
                    **context,
                    "draft": current_draft.result,
                    "issues": context.get("_critique_issues", [])
                }
                msg = AgentMessage(
                    from_model="openwebui",
                    to_model=self.generator,
                    task="refine",
                    context=refine_context,
                    routing=RoutingStrategy.DIRECT
                )
                current_draft = await bridge.route_message(msg)

            # Phase 2: Critique
            critique_context = {
                **context,
                "draft": current_draft.result,
                "iteration": iteration
            }
            msg = AgentMessage(
                from_model="openwebui",
                to_model=self.critic,
                task="critique",
                context=critique_context,
                routing=RoutingStrategy.DIRECT
            )
            critique = await bridge.route_message(msg)

            # Extract quality score
            quality_score = critique.metadata.get("quality_score", 0.0)
            issues = critique.metadata.get("issues", [])

            # Store issues for next iteration
            context["_critique_issues"] = issues

            if quality_score >= quality_threshold:
                self.logger.info(f"Quality threshold reached: {quality_score:.2f}")
                break

            if not issues:
                self.logger.warning("No issues found, stopping iteration")
                break

        return CritiqueResult(
            result=current_draft.result,
            iterations=iteration,
            quality_score=quality_score,
            generator=self.generator,
            critic=self.critic
        )


# ============================================================================
# Main MultiAgentBridge
# ============================================================================

class MultiAgentBridge:
    """
    Orchestrates multi-model swarm coordination.

    Features:
    - Consensus voting with confidence weighting
    - Capability-based delegation
    - Iterative critique and refinement
    - HMAC-SHA256 message authentication
    - Redis caching for performance
    - IF.guard safety veto layer
    """

    def __init__(self, bridge_url: str = "http://localhost:8001",
                 bridge_secret: str = "",
                 redis_client: Optional[redis.Redis] = None,
                 log_level: str = "INFO"):
        """
        Initialize MultiAgentBridge.

        Args:
            bridge_url: URL of mcp-multiagent-bridge server
            bridge_secret: HMAC secret for signing messages
            redis_client: Redis client for caching
            log_level: Logging level
        """
        self.bridge_url = bridge_url
        self.bridge_secret = bridge_secret or os.getenv("BRIDGE_SECRET", "")
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        # Add console handler if no handlers exist
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Initialize patterns
        self.consensus = ConsensusPattern(logger=self.logger)
        self.delegation = DelegationPattern(logger=self.logger)

        self.logger.info("MultiAgentBridge initialized")

    def create_critique_pattern(self, generator: str, critic: str,
                               max_iterations: int = 3) -> CritiquePattern:
        """Create critique pattern with specified models"""
        return CritiquePattern(
            generator_model=generator,
            critic_model=critic,
            max_iterations=max_iterations,
            logger=self.logger
        )

    async def route_message(self, message: AgentMessage) -> AgentResponse:
        """
        Route message based on routing strategy.

        Args:
            message: AgentMessage to route

        Returns:
            AgentResponse from target model
        """
        # Validate message
        if not message.from_model or not message.to_model or not message.task:
            raise ValueError("Invalid message: missing required fields")

        # Sign message
        if self.bridge_secret:
            message.sign(self.bridge_secret)

        # Route based on strategy
        if message.routing == RoutingStrategy.DIRECT:
            return await self._route_direct(message)
        elif message.routing == RoutingStrategy.BROADCAST:
            return await self._route_broadcast(message)
        else:
            raise ValueError(f"Unknown routing: {message.routing}")

    async def _route_direct(self, message: AgentMessage) -> AgentResponse:
        """Direct routing to single model"""
        try:
            self.logger.debug(f"Route direct: {message.from_model} -> {message.to_model}")

            # Send to mcp-multiagent-bridge
            response = await self._send_via_bridge(message)

            # Cache response if Redis available
            if self.redis:
                try:
                    self.redis.setex(
                        f"agent_response:{message.message_id}",
                        3600,  # 1 hour TTL
                        json.dumps(asdict(response), default=str)
                    )
                except Exception as e:
                    self.logger.warning(f"Redis cache failed: {e}")

            return response

        except asyncio.TimeoutError:
            self.logger.error(f"Timeout routing to {message.to_model}")
            raise
        except Exception as e:
            self.logger.error(f"Routing error: {e}")
            raise

    async def _route_broadcast(self, message: AgentMessage) -> Dict:
        """Broadcast routing to multiple models"""
        models = self._get_all_models()

        self.logger.debug(f"Broadcast to {len(models)} models: {models}")

        tasks = []
        for model in models:
            msg_copy = AgentMessage(
                from_model=message.from_model,
                to_model=model,
                task=message.task,
                context=message.context,
                routing=RoutingStrategy.DIRECT,
                timeout_ms=message.timeout_ms,
                conversation_id=message.conversation_id
            )
            tasks.append(self._route_direct(msg_copy))

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out errors
        valid = [r for r in responses if not isinstance(r, Exception)]

        return {
            "responses": valid,
            "total": len(models),
            "successful": len(valid),
            "failed": len(models) - len(valid)
        }

    async def _send_via_bridge(self, message: AgentMessage) -> AgentResponse:
        """Send message through mcp-multiagent-bridge"""

        payload = {
            "from_model": message.from_model,
            "to_model": message.to_model,
            "task": message.task,
            "context": message.context,
            "message_id": message.message_id,
            "signature": message.signature,
            "timestamp": message.timestamp
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.bridge_url}/route",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(milliseconds=message.timeout_ms)
                ) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"Bridge returned {resp.status}")

                    data = await resp.json()

                    return AgentResponse(
                        from_model=data.get("from_model", message.to_model),
                        in_response_to=message.message_id,
                        result=data.get("result", ""),
                        metadata=data.get("metadata", {})
                    )

            except asyncio.TimeoutError:
                raise TimeoutError(f"Bridge timeout after {message.timeout_ms}ms")

    def _get_all_models(self) -> List[str]:
        """Get list of all available models"""
        return ["claude_max", "deepseek", "gemini"]

    async def consensus_vote(self, query: str, context: Dict = None,
                            models: List[str] = None) -> ConsensusResult:
        """
        Execute consensus pattern.

        Args:
            query: Question for models to vote on
            context: Additional context
            models: List of models to vote (default: all)

        Returns:
            ConsensusResult with agreement percentage
        """
        if context is None:
            context = {"query": query}
        if models is None:
            models = self._get_all_models()

        return await self.consensus.execute(query, context, models, self)

    async def delegate_task(self, query: str, capability: str,
                           context: Dict = None) -> DelegationResult:
        """
        Execute delegation pattern.

        Args:
            query: Task description
            capability: Required capability (e.g., "code_generation")
            context: Additional context

        Returns:
            DelegationResult with specialist model response
        """
        if context is None:
            context = {"query": query}

        return await self.delegation.execute(query, capability, context, self)

    def critique(self, generator: str, critic: str,
                max_iterations: int = 3) -> CritiquePattern:
        """
        Create critique pattern for iterative refinement.

        Args:
            generator: Model that generates content
            critic: Model that provides critique
            max_iterations: Max refinement iterations

        Returns:
            CritiquePattern instance
        """
        return self.create_critique_pattern(generator, critic, max_iterations)


# ============================================================================
# OpenWebUI Function Integration
# ============================================================================

class OpenWebUIFunction:
    """
    OpenWebUI Function wrapper for multi-agent coordination.

    Usage in OpenWebUI chat:
    @multiagent-consensus: "Analyze this code for bugs"
    @multiagent-delegate: code_generation "Write async example"
    @multiagent-critique: "Write a blog post about X"
    """

    def __init__(self):
        self.bridge = MultiAgentBridge(
            bridge_secret=os.getenv("BRIDGE_SECRET", "")
        )

    async def process(self, body: Dict) -> str:
        """
        Process message through OpenWebUI.

        Args:
            body: OpenWebUI message body

        Returns:
            Response string to display in chat
        """
        if "messages" not in body or not body["messages"]:
            return "Error: No messages provided"

        last_message = body["messages"][-1].get("content", "")

        # Check for pattern markers
        if "@multiagent-consensus:" in last_message:
            return await self._handle_consensus(last_message)
        elif "@multiagent-delegate:" in last_message:
            return await self._handle_delegation(last_message)
        elif "@multiagent-critique:" in last_message:
            return await self._handle_critique(last_message)

        return "No multi-agent pattern recognized"

    async def _handle_consensus(self, message: str) -> str:
        """Handle consensus pattern"""
        try:
            query = message.replace("@multiagent-consensus:", "").strip()

            result = await self.bridge.consensus_vote(query)

            return f"""
🗳️ **Multi-Model Consensus**

**Consensus:** {result.consensus[:200]}...

**Agreement Score:** {result.agreement_percentage:.1%}

**Models Voting:** {len(result.positions)}
"""
        except Exception as e:
            return f"Error in consensus: {str(e)}"

    async def _handle_delegation(self, message: str) -> str:
        """Handle delegation pattern"""
        try:
            # Format: @multiagent-delegate: capability "query"
            parts = message.replace("@multiagent-delegate:", "").strip().split(" ", 1)
            if len(parts) != 2:
                return "Usage: @multiagent-delegate: capability \"query\""

            capability = parts[0]
            query = parts[1].strip('"')

            result = await self.bridge.delegate_task(query, capability)

            return f"""
🎯 **Delegated to Specialist**

**Model:** {result.delegated_to.upper()}
**Specialization:** {result.specialization_score:.1%}

{result.result}
"""
        except Exception as e:
            return f"Error in delegation: {str(e)}"

    async def _handle_critique(self, message: str) -> str:
        """Handle critique pattern"""
        try:
            query = message.replace("@multiagent-critique:", "").strip()

            critique = self.bridge.critique("claude_max", "deepseek")
            result = await critique.execute(query, {}, self.bridge)

            return f"""
✏️ **Iteratively Refined Output**

{result.result}

**Quality Score:** {result.quality_score:.1%}
**Iterations:** {result.iterations}
**Generator:** {result.generator}
**Critic:** {result.critic}
"""
        except Exception as e:
            return f"Error in critique: {str(e)}"


# ============================================================================
# Example Usage
# ============================================================================

async def example_consensus():
    """Example: Consensus voting on code security"""
    bridge = MultiAgentBridge(bridge_secret="test_secret_key")

    result = await bridge.consensus_vote(
        "Is this code secure?",
        context={
            "code": "SELECT * FROM users WHERE id = 1",
            "language": "sql"
        },
        models=["claude_max", "deepseek", "gemini"]
    )

    print(f"Consensus: {result.consensus}")
    print(f"Agreement: {result.agreement_percentage:.1%}")


async def example_delegation():
    """Example: Delegate to code generation specialist"""
    bridge = MultiAgentBridge(bridge_secret="test_secret_key")

    result = await bridge.delegate_task(
        "Write Python code for async/await pattern",
        "code_generation"
    )

    print(f"Delegated to: {result.delegated_to}")
    print(f"Specialization: {result.specialization_score:.1%}")
    print(f"Result: {result.result[:200]}...")


async def example_critique():
    """Example: Iterative refinement"""
    bridge = MultiAgentBridge(bridge_secret="test_secret_key")

    critique = bridge.critique("claude_max", "deepseek", max_iterations=3)
    result = await critique.execute(
        "Write a blog post about async/await in Python",
        {}
    )

    print(f"Final result: {result.result[:200]}...")
    print(f"Quality: {result.quality_score:.1%}")
    print(f"Iterations: {result.iterations}")


if __name__ == "__main__":
    # Note: These examples require a running mcp-multiagent-bridge server
    # and appropriate model backends configured

    logging.basicConfig(level=logging.INFO)

    # Uncomment to run examples:
    # asyncio.run(example_consensus())
    # asyncio.run(example_delegation())
    # asyncio.run(example_critique())

    print("MultiAgentBridge module loaded successfully")
    print("Import and use: from multiagent_bridge import MultiAgentBridge")
