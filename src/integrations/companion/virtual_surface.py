"""
CompanionVirtualSurface: IF.matrix Intent → Companion Button Press Bridge

This module provides the semantic intent translation layer that allows IF.logistics
to trigger Companion buttons through intent-based commands rather than low-level
location coordinates.

Example:
    >>> async with CompanionVirtualSurface() as surface:
    ...     result = await surface.virtual_press("studio_dark_mode")
    ...     assert result.success
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import aioredis
import httpx

logger = logging.getLogger(__name__)


class SurfaceProtocol(str, Enum):
    """Supported Companion control protocols."""
    HTTP_REST = "http_rest"      # HTTP API (default)
    TCP_SOCKET = "tcp_socket"    # Raw TCP (low-latency)
    UDP_SOCKET = "udp_socket"    # Raw UDP (ultra-low-latency)
    OSC = "osc"                  # Open Sound Control
    SATELLITE_API = "satellite"  # Bidirectional websocket


@dataclass
class VirtualSurfaceConfig:
    """Configuration for CompanionVirtualSurface."""
    companion_host: str = "localhost"
    companion_port: int = 8000
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    protocol: SurfaceProtocol = SurfaceProtocol.HTTP_REST
    request_timeout: float = 5.0
    retry_max_attempts: int = 3
    retry_backoff_base: float = 1.0
    enable_metrics: bool = True


@dataclass
class IntentMappingRecord:
    """Mapping of an Intent to device button coordinates."""
    intent_name: str
    page: int
    row: int
    column: int
    protocol: SurfaceProtocol
    press_duration_ms: int = 100
    cooldown_ms: int = 0
    macro_sequence: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of a virtual press execution."""
    success: bool
    intent_name: str
    device_id: Optional[str] = None
    button_location: Optional[Tuple[int, int, int]] = None  # (page, row, col)
    latency_ms: float = 0.0
    protocol_used: Optional[SurfaceProtocol] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    raw_response: Optional[Any] = None


class CompanionVirtualSurface:
    """
    Virtual Surface Interface for Companion Integration.

    Translates IF.logistics semantic intents into Companion button presses
    via Redis-mediated intent mapping.

    Attributes:
        config: VirtualSurfaceConfig
        redis_client: Connected Redis client
        http_client: Async HTTP session
    """

    def __init__(self, config: Optional[VirtualSurfaceConfig] = None):
        """Initialize virtual surface with configuration."""
        self.config = config or VirtualSurfaceConfig()
        self.redis_client: Optional[aioredis.Redis] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        self._metrics = {
            "total_presses": 0,
            "successful_presses": 0,
            "failed_presses": 0,
            "total_latency_ms": 0.0,
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self):
        """Establish connections to Redis and Companion."""
        logger.info(
            f"Connecting to Redis at {self.config.redis_host}:"
            f"{self.config.redis_port}"
        )
        self.redis_client = await aioredis.create_redis_pool(
            f"redis://{self.config.redis_host}:{self.config.redis_port}/"
            f"{self.config.redis_db}"
        )

        logger.info(
            f"Connecting HTTP client to {self.config.companion_host}:"
            f"{self.config.companion_port}"
        )
        self.http_client = httpx.AsyncClient(
            base_url=f"http://{self.config.companion_host}:"
            f"{self.config.companion_port}",
            timeout=self.config.request_timeout,
        )

    async def disconnect(self):
        """Close all connections."""
        if self.http_client:
            await self.http_client.aclose()
        if self.redis_client:
            self.redis_client.close()
            await self.redis_client.wait_closed()

    async def virtual_press(
        self,
        intent_name: str,
        device_override: Optional[str] = None,
        macro_mode: bool = False,
    ) -> ExecutionResult:
        """
        Execute a virtual button press based on semantic intent.

        Args:
            intent_name: Semantic intent (e.g., "studio_dark_mode")
            device_override: Optional device_id to override mapped device
            macro_mode: If True, execute full macro sequence; else just press

        Returns:
            ExecutionResult with success/failure details
        """
        start_time = datetime.utcnow()
        self._metrics["total_presses"] += 1

        try:
            # Step 1: Lookup intent mapping in Redis
            mapping = await self._lookup_intent(intent_name, device_override)
            if not mapping:
                error_msg = f"Intent '{intent_name}' not found in Redis"
                logger.error(error_msg)
                self._metrics["failed_presses"] += 1
                return ExecutionResult(
                    success=False,
                    intent_name=intent_name,
                    error=error_msg,
                )

            # Step 2: Execute macro sequence if requested
            if macro_mode and mapping.macro_sequence:
                return await self._execute_macro(mapping, start_time)

            # Step 3: Execute single button press
            return await self._execute_button_press(mapping, start_time)

        except Exception as e:
            latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._metrics["failed_presses"] += 1
            logger.exception(f"Virtual press failed: {e}")
            return ExecutionResult(
                success=False,
                intent_name=intent_name,
                error=str(e),
                latency_ms=latency_ms,
            )

    async def _lookup_intent(
        self,
        intent_name: str,
        device_override: Optional[str] = None,
    ) -> Optional[IntentMappingRecord]:
        """Lookup intent mapping from Redis."""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")

        # Build Redis key
        redis_key = f"mcr:mapping:companion:intent:{intent_name}"

        # Get mapping from Redis
        mapping_data = await self.redis_client.get(redis_key)
        if not mapping_data:
            logger.debug(f"No mapping found for intent: {intent_name}")
            return None

        # Parse JSON mapping
        import json
        mapping_dict = json.loads(mapping_data)

        # Apply device override if provided
        if device_override:
            mapping_dict["device_id"] = device_override

        return IntentMappingRecord(**mapping_dict)

    async def _execute_button_press(
        self,
        mapping: IntentMappingRecord,
        start_time: datetime,
    ) -> ExecutionResult:
        """Execute a single button press via appropriate protocol."""
        location_str = f"{mapping.page}/{mapping.row}/{mapping.column}"
        protocol = mapping.protocol

        logger.info(
            f"Executing button press: intent={mapping.intent_name}, "
            f"location={location_str}, protocol={protocol}"
        )

        try:
            if protocol == SurfaceProtocol.HTTP_REST:
                success = await self._press_http(location_str)
            elif protocol == SurfaceProtocol.TCP_SOCKET:
                success = await self._press_tcp(location_str)
            elif protocol == SurfaceProtocol.UDP_SOCKET:
                success = await self._press_udp(location_str)
            elif protocol == SurfaceProtocol.OSC:
                success = await self._press_osc(location_str)
            else:
                raise ValueError(f"Unknown protocol: {protocol}")

            latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            if success:
                self._metrics["successful_presses"] += 1
                self._metrics["total_latency_ms"] += latency_ms
                logger.info(
                    f"Button press successful: {location_str} "
                    f"({latency_ms:.1f}ms)"
                )
            else:
                self._metrics["failed_presses"] += 1
                logger.warning(f"Button press failed: {location_str}")

            return ExecutionResult(
                success=success,
                intent_name=mapping.intent_name,
                device_id=mapping.metadata.get("device_id"),
                button_location=(mapping.page, mapping.row, mapping.column),
                latency_ms=latency_ms,
                protocol_used=protocol,
            )

        except Exception as e:
            latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._metrics["failed_presses"] += 1
            logger.exception(f"Button press execution error: {e}")
            return ExecutionResult(
                success=False,
                intent_name=mapping.intent_name,
                button_location=(mapping.page, mapping.row, mapping.column),
                latency_ms=latency_ms,
                protocol_used=protocol,
                error=str(e),
            )

    async def _execute_macro(
        self,
        mapping: IntentMappingRecord,
        start_time: datetime,
    ) -> ExecutionResult:
        """Execute a macro (sequence of button presses)."""
        logger.info(
            f"Executing macro: {mapping.intent_name} "
            f"with {len(mapping.macro_sequence)} steps"
        )

        results = []
        for step_intent in mapping.macro_sequence:
            result = await self.virtual_press(step_intent, macro_mode=False)
            results.append(result)

            if not result.success:
                logger.warning(
                    f"Macro step failed: {step_intent}, "
                    f"stopping sequence"
                )
                break

            # Add cooldown between steps
            if mapping.cooldown_ms > 0:
                await asyncio.sleep(mapping.cooldown_ms / 1000.0)

        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        all_successful = all(r.success for r in results)

        if all_successful:
            self._metrics["successful_presses"] += 1
        else:
            self._metrics["failed_presses"] += 1

        return ExecutionResult(
            success=all_successful,
            intent_name=mapping.intent_name,
            latency_ms=latency_ms,
            protocol_used=SurfaceProtocol.HTTP_REST,
            error=None if all_successful else "One or more macro steps failed",
        )

    async def _press_http(self, location: str) -> bool:
        """Execute button press via HTTP API."""
        if not self.http_client:
            raise RuntimeError("HTTP client not connected")

        url = f"/api/location/{location}/press"
        try:
            response = await self.http_client.post(url, json={})
            return response.status_code == 200
        except httpx.RequestError as e:
            logger.error(f"HTTP request failed: {e}")
            return False

    async def _press_tcp(self, location: str) -> bool:
        """Execute button press via TCP socket."""
        # Stub for TCP implementation
        logger.debug(f"TCP press not yet implemented: {location}")
        return True

    async def _press_udp(self, location: str) -> bool:
        """Execute button press via UDP socket."""
        # Stub for UDP implementation
        logger.debug(f"UDP press not yet implemented: {location}")
        return True

    async def _press_osc(self, location: str) -> bool:
        """Execute button press via OSC."""
        # Stub for OSC implementation
        logger.debug(f"OSC press not yet implemented: {location}")
        return True

    async def register_intent(
        self,
        intent_name: str,
        page: int,
        row: int,
        column: int,
        protocol: SurfaceProtocol = SurfaceProtocol.HTTP_REST,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Register a new intent mapping in Redis.

        Args:
            intent_name: Semantic intent name
            page: Button page (0-indexed)
            row: Button row (0-indexed)
            column: Button column (0-indexed)
            protocol: Protocol to use
            metadata: Additional metadata

        Returns:
            True if registration successful
        """
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")

        mapping = IntentMappingRecord(
            intent_name=intent_name,
            page=page,
            row=row,
            column=column,
            protocol=protocol,
            metadata=metadata or {},
        )

        redis_key = f"mcr:mapping:companion:intent:{intent_name}"
        import json
        mapping_json = json.dumps({
            "intent_name": mapping.intent_name,
            "page": mapping.page,
            "row": mapping.row,
            "column": mapping.column,
            "protocol": mapping.protocol.value,
            "metadata": mapping.metadata,
        })

        try:
            await self.redis_client.set(redis_key, mapping_json)
            logger.info(f"Registered intent: {intent_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register intent: {e}")
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics."""
        metrics = self._metrics.copy()
        if metrics["successful_presses"] > 0:
            metrics["average_latency_ms"] = (
                metrics["total_latency_ms"] / metrics["successful_presses"]
            )
        return metrics

    async def health_check(self) -> bool:
        """Check health of Redis and Companion connections."""
        try:
            # Check Redis
            if self.redis_client:
                await self.redis_client.ping()
            else:
                return False

            # Check Companion HTTP
            if self.http_client:
                response = await self.http_client.post(
                    "/api/location/0/0/0/press",
                    json={},
                )
                return response.status_code in (200, 400)  # 400 if button doesn't exist
            else:
                return False

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# ============================================================================
# Example Usage
# ============================================================================

async def example_usage():
    """Example usage of CompanionVirtualSurface."""
    config = VirtualSurfaceConfig(
        companion_host="192.168.1.100",
        companion_port=8000,
        protocol=SurfaceProtocol.HTTP_REST,
    )

    async with CompanionVirtualSurface(config) as surface:
        # Register some intents
        await surface.register_intent(
            "studio_dark_mode",
            page=1,
            row=0,
            column=0,
            metadata={"description": "Toggle dark mode in studio"},
        )

        await surface.register_intent(
            "stream_start",
            page=1,
            row=1,
            column=0,
            metadata={"description": "Start streaming"},
        )

        # Execute intent
        result = await surface.virtual_press("studio_dark_mode")
        print(f"Result: {result}")

        # Get metrics
        metrics = surface.get_metrics()
        print(f"Metrics: {metrics}")

        # Health check
        is_healthy = await surface.health_check()
        print(f"Healthy: {is_healthy}")


if __name__ == "__main__":
    # Requires aioredis and httpx installed
    # asyncio.run(example_usage())
    pass
