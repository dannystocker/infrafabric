"""
Main bridge implementation for Companion MCR

CompanionVirtualSurface: Core bridge class
CompanionBridge: Context manager wrapper
"""

import asyncio
import aiohttp
import redis.asyncio as aioredis
import re
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .models import (
    CompanionBridgeConfig,
    ProtocolTemplate,
    CompanionDevice,
    IntentMapping,
    ButtonAction,
    CompanionMacro,
    ButtonState,
    ExecutionResult,
)
from .errors import CompanionError, CompanionErrorType, MacroAbortError
from .retry import RetryPolicy, retry_with_backoff

logger = logging.getLogger(__name__)


class VariableSubstitution:
    """Variable substitution engine for protocol templates"""

    @staticmethod
    def substitute(template: str, variables: Dict[str, Any]) -> str:
        """
        Substitute variables in template.

        Supports both {var} and $var syntax.

        Args:
            template: Template string with placeholders
            variables: Variable values

        Returns:
            Substituted string

        Raises:
            ValueError: If variables are missing
        """
        result = template

        # Substitute {var} style
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))

        # Substitute $var style (for OSC)
        for key, value in variables.items():
            result = result.replace(f"${key}", str(value))

        # Check for unsubstituted variables
        remaining = re.findall(r"\{(\w+)\}|\$(\w+)", result)
        if remaining:
            missing = [m[0] or m[1] for m in remaining]
            raise ValueError(f"Missing variables: {missing}")

        return result


class CompanionVirtualSurface:
    """
    Main bridge interface for Companion MCR control.

    Architecture:
        - Async/await for all I/O operations
        - Redis for configuration and state
        - Pydantic for schema validation
        - Exponential backoff retry

    Usage:
        surface = CompanionVirtualSurface()
        await surface.async_init()
        result = await surface.execute_intent("studio_dark_mode")
        await surface.close()
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        config_key: str = "mcr:bridge:companion:config",
    ):
        self.redis_url = redis_url
        self.config_key = config_key

        # Will be initialized in async_init()
        self.redis: Optional[aioredis.Redis] = None
        self.http_session: Optional[aiohttp.ClientSession] = None
        self.config: Optional[CompanionBridgeConfig] = None

    async def async_init(self):
        """
        Async initialization (call after __init__).

        Connects to Redis and initializes HTTP session.
        """
        # Connect to Redis
        self.redis = await aioredis.from_url(
            self.redis_url, encoding="utf-8", decode_responses=True
        )

        # Load configuration
        config_json = await self.redis.get(self.config_key)
        if not config_json:
            # Create default config
            self.config = CompanionBridgeConfig()
            await self.redis.set(self.config_key, self.config.to_redis())
        else:
            self.config = CompanionBridgeConfig.from_redis(config_json)

        # Initialize HTTP session
        timeout = aiohttp.ClientTimeout(total=self.config.timeout_ms / 1000.0)
        self.http_session = aiohttp.ClientSession(
            base_url=self.config.base_url, timeout=timeout
        )

        logger.info(f"CompanionVirtualSurface initialized: {self.config.base_url}")

    async def close(self):
        """Cleanup resources"""
        if self.http_session:
            await self.http_session.close()
        if self.redis:
            await self.redis.close()

    # ========================================================================
    # Intent Execution
    # ========================================================================

    async def execute_intent(
        self,
        intent_name: str,
        context: Dict[str, Any] = None,
        timeout_ms: Optional[int] = None,
    ) -> ExecutionResult:
        """
        Execute a high-level intent.

        Args:
            intent_name: Intent identifier (e.g., "studio_dark_mode")
            context: Optional execution context
            timeout_ms: Override default timeout

        Returns:
            ExecutionResult with success status and metadata

        Example:
            result = await bridge.execute_intent("studio_dark_mode")
            if result.success:
                print(f"Executed in {result.latency_ms}ms")
        """
        start_time = asyncio.get_event_loop().time()
        context = context or {}

        try:
            # 1. Lookup intent mapping
            mapping = await self._get_intent_mapping(intent_name)
            if not mapping:
                raise CompanionError(
                    CompanionErrorType.INTENT_NOT_FOUND,
                    f"Intent not found: {intent_name}",
                )

            # 2. Execute all actions in sequence
            executed_count = 0

            for action in mapping.actions:
                # Apply delay if specified
                if action.delay_ms > 0:
                    await asyncio.sleep(action.delay_ms / 1000.0)

                # Execute action
                await self._execute_action(action, context)
                executed_count += 1

            # 3. Calculate latency
            end_time = asyncio.get_event_loop().time()
            latency_ms = (end_time - start_time) * 1000

            return ExecutionResult(
                success=True,
                intent_name=intent_name,
                actions_executed=executed_count,
                latency_ms=latency_ms,
            )

        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            latency_ms = (end_time - start_time) * 1000

            logger.error(f"Intent execution failed: {intent_name}, error: {e}")

            return ExecutionResult(
                success=False,
                intent_name=intent_name,
                latency_ms=latency_ms,
                error=e
                if isinstance(e, CompanionError)
                else CompanionError(CompanionErrorType.PROTOCOL_ERROR, str(e)),
            )

    async def _get_intent_mapping(self, intent_name: str) -> Optional[IntentMapping]:
        """Retrieve intent mapping from Redis"""
        key = f"mcr:mapping:companion:intent:{intent_name}"
        data = await self.redis.get(key)

        if not data:
            return None

        return IntentMapping.from_redis(data)

    async def _execute_action(
        self, action: ButtonAction, context: Dict[str, Any]
    ) -> None:
        """Execute a single button action"""

        # 1. Load protocol template
        protocol = await self._get_protocol(action.protocol_name)
        if not protocol:
            raise CompanionError(
                CompanionErrorType.PROTOCOL_ERROR,
                f"Protocol not found: {action.protocol_name}",
            )

        # 2. Load device config
        device = await self._get_device(action.device_id)
        if not device:
            raise CompanionError(
                CompanionErrorType.DEVICE_NOT_FOUND,
                f"Device not found: {action.device_id}",
            )

        # 3. Merge variables (action vars + context vars)
        variables = {**action.variables, **context}

        # 4. Substitute variables into template
        command = VariableSubstitution.substitute(protocol.template, variables)

        # 5. Execute protocol-specific command
        if protocol.protocol_type == "http":
            await self._execute_http(command, protocol, variables)
        elif protocol.protocol_type == "osc":
            await self._execute_osc(command, protocol, variables)
        elif protocol.protocol_type == "tcp":
            await self._execute_tcp(command, protocol)
        elif protocol.protocol_type == "udp":
            await self._execute_udp(command, protocol)
        else:
            raise CompanionError(
                CompanionErrorType.PROTOCOL_ERROR,
                f"Unsupported protocol type: {protocol.protocol_type}",
            )

        # 6. Update button state if tracking enabled
        if self.config.enable_state_tracking:
            await self._update_button_state(device.device_id, action, variables)

    # ========================================================================
    # Protocol Execution Methods
    # ========================================================================

    async def _execute_http(
        self, command: str, protocol: ProtocolTemplate, variables: Dict[str, Any]
    ) -> None:
        """Execute HTTP/REST command"""

        async def _do_request():
            method = protocol.method or "POST"
            headers = protocol.headers or {}

            # Build request body if variables contain 'body'
            body = None
            if "body" in variables:
                body = variables["body"]

            async with self.http_session.request(
                method, command, headers=headers, json=body
            ) as response:
                if response.status not in (200, 201, 204):
                    raise CompanionError(
                        CompanionErrorType.PROTOCOL_ERROR,
                        f"HTTP {response.status}: {await response.text()}",
                    )

                return await response.text()

        # Execute with retry
        policy = RetryPolicy(
            max_attempts=self.config.retry_attempts,
            initial_backoff_ms=self.config.retry_backoff_ms,
        )

        await retry_with_backoff(_do_request, policy=policy)

    async def _execute_osc(
        self, command: str, protocol: ProtocolTemplate, variables: Dict[str, Any]
    ) -> None:
        """Execute OSC command (stub - requires python-osc)"""
        logger.warning("OSC execution not implemented (requires python-osc)")
        # TODO: Implement OSC client

    async def _execute_tcp(self, command: str, protocol: ProtocolTemplate) -> None:
        """Execute TCP raw command"""
        tcp_host = protocol.tcp_host or self.config.host
        tcp_port = protocol.tcp_port or 9999

        reader, writer = await asyncio.open_connection(tcp_host, tcp_port)

        try:
            # Send command
            writer.write(command.encode("utf-8"))
            await writer.drain()

            # Read response (if any)
            response = await reader.read(1024)
            logger.debug(f"TCP response: {response.decode('utf-8', errors='ignore')}")

        finally:
            writer.close()
            await writer.wait_closed()

    async def _execute_udp(self, command: str, protocol: ProtocolTemplate) -> None:
        """Execute UDP raw command (stub)"""
        logger.warning("UDP execution not implemented")
        # TODO: Implement UDP client

    # ========================================================================
    # State Management
    # ========================================================================

    async def _update_button_state(
        self, device_id: str, action: ButtonAction, variables: Dict[str, Any]
    ) -> None:
        """Update button state in Redis"""

        # Build button ID
        page = variables.get("page", 0)
        row = variables.get("row", 0)
        col = variables.get("col", 0)
        button_id = f"{page}_{row}_{col}"

        # Get existing state or create new
        state_key = f"mcr:companion:state:{device_id}:{button_id}"
        state_json = await self.redis.get(state_key)

        if state_json:
            state = ButtonState.from_redis(state_json)
        else:
            state = ButtonState(device_id=device_id, button_id=button_id)

        # Update state based on action type
        if action.action_type == "press":
            state.state = "pressed"
            state.last_pressed = datetime.utcnow().isoformat()
            state.press_count += 1
        elif action.action_type == "set_text":
            state.text = variables.get("text")
        elif action.action_type == "set_color":
            state.color = variables.get("color")

        state.updated_at = datetime.utcnow().isoformat()

        # Write back to Redis
        await self.redis.set(state_key, state.to_redis())

    # ========================================================================
    # Macro Execution
    # ========================================================================

    async def execute_macro(self, macro_id: str) -> ExecutionResult:
        """Execute a macro (sequence of intents)"""

        if not self.config.enable_macros:
            raise CompanionError(
                CompanionErrorType.VALIDATION_ERROR,
                "Macros are disabled in configuration",
            )

        # Load macro
        macro_key = f"mcr:companion:macro:{macro_id}"
        macro_json = await self.redis.get(macro_key)

        if not macro_json:
            raise CompanionError(
                CompanionErrorType.INTENT_NOT_FOUND, f"Macro not found: {macro_id}"
            )

        macro = CompanionMacro.from_redis(macro_json)

        # Execute steps
        results = []

        for step in sorted(macro.steps, key=lambda s: s.step_number):
            try:
                result = await self.execute_intent(
                    intent_name=step.intent_name, timeout_ms=step.timeout_ms
                )

                results.append(result)

                if not result.success and step.on_failure == "abort":
                    break

                if step.on_failure == "retry" and not result.success:
                    # Retry once
                    result = await self.execute_intent(
                        intent_name=step.intent_name, timeout_ms=step.timeout_ms
                    )
                    results.append(result)

            except Exception as e:
                logger.error(f"Macro step {step.step_number} failed: {e}")

                if step.on_failure == "abort":
                    break

        # Calculate summary
        total_executed = len(results)
        total_failed = sum(1 for r in results if not r.success)

        return ExecutionResult(
            success=(total_failed == 0),
            intent_name=f"macro:{macro_id}",
            actions_executed=total_executed,
            metadata={
                "macro_id": macro_id,
                "steps_completed": total_executed,
                "steps_failed": total_failed,
            },
        )

    # ========================================================================
    # Device/Protocol Management
    # ========================================================================

    async def _get_protocol(self, protocol_name: str) -> Optional[ProtocolTemplate]:
        """Load protocol template from Redis"""
        key = f"mcr:protocol:companion:{protocol_name}"
        data = await self.redis.get(key)

        if not data:
            return None

        return ProtocolTemplate.from_redis(data)

    async def _get_device(self, device_id: str) -> Optional[CompanionDevice]:
        """Load device configuration from Redis"""
        key = f"mcr:catalog:companion:device:{device_id}"
        data = await self.redis.get(key)

        if not data:
            return None

        return CompanionDevice.from_redis(data)

    async def register_device(self, device: CompanionDevice) -> None:
        """Register a new device in the catalog"""
        key = f"mcr:catalog:companion:device:{device.device_id}"
        await self.redis.set(key, device.to_redis())
        logger.info(f"Device registered: {device.device_id}")

    async def register_intent(self, mapping: IntentMapping) -> None:
        """Register a new intent mapping"""
        key = f"mcr:mapping:companion:intent:{mapping.intent_name}"
        await self.redis.set(key, mapping.to_redis())
        logger.info(f"Intent registered: {mapping.intent_name}")

    async def register_protocol(self, protocol: ProtocolTemplate) -> None:
        """Register a new protocol template"""
        key = f"mcr:protocol:companion:{protocol.protocol_name}"
        await self.redis.set(key, protocol.to_redis())
        logger.info(f"Protocol registered: {protocol.protocol_name}")


# ============================================================================
# Context Manager Wrapper
# ============================================================================


class CompanionBridge:
    """
    Context manager wrapper for CompanionVirtualSurface.

    Usage:
        async with CompanionBridge() as bridge:
            result = await bridge.execute_intent("studio_dark_mode")
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.surface: Optional[CompanionVirtualSurface] = None

    async def __aenter__(self) -> CompanionVirtualSurface:
        self.surface = CompanionVirtualSurface(redis_url=self.redis_url)
        await self.surface.async_init()
        return self.surface

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.surface:
            await self.surface.close()
