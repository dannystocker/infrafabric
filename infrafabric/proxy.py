"""
IF.proxy - Policy-Governed External API Proxy Service

Provides secure, audited HTTP proxy for calling external APIs from sandboxed
environments. Abstracts network locations and enforces allow-lists for API endpoints.

**Problem Solved**: Sandboxed adapters need to call external APIs (Meilisearch,
Home Assistant, vMix, OBS) but shouldn't have direct network access or know
internal network topology.

**Impact**: Enables Phase 1-6 provider integrations with strong network security
boundaries and abstracted service discovery.

Example:
    ```python
    from infrafabric.event_bus import EventBus
    from infrafabric.proxy import IFProxy

    bus = await EventBus().connect()
    proxy = IFProxy(bus, registry_path='/etc/infrafabric/proxy_registry.json')
    await proxy.start()

    # Swarm makes request via IF.bus
    await bus.publish('if.command.network.proxy', {
        'trace_id': 'trace-123',
        'swarm_id': 'navidocs-adapter',
        'target_alias': 'meilisearch_api',
        'method': 'POST',
        'path': '/indexes/navidocs/documents',
        'headers': {'Content-Type': 'application/json'},
        'body': '{"id": 1, "title": "Doc 1"}',
        'timeout_ms': 10000
    })

    # IF.proxy validates, proxies request, and returns result
    # Result published to: if.event.network.proxy.result
    ```

Architecture:
    IF.proxy subscribes to IF.bus command topic, validates requests against
    per-swarm target alias registry, proxies HTTP requests with timeout enforcement,
    and logs all operations to IF.witness for audit trail.

Security:
    - Target alias registry maps alias → base URL + allowed paths per swarm
    - IF.governor capability check required: 'network.http.proxy.external'
    - All proxy requests logged to IF.witness (audit trail)
    - Timeout enforcement (default 10000ms)
    - Path allow-list per swarm (regex patterns)
    - No direct network access from adapters
"""

import asyncio
import aiohttp
import json
import time
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from infrafabric.event_bus import EventBus

logger = logging.getLogger(__name__)


class ProxyError(Exception):
    """Base exception for proxy errors"""
    pass


class TargetNotFoundError(ProxyError):
    """Target alias not found in registry"""
    pass


class PathNotAllowedError(ProxyError):
    """Request path not allowed by policy"""
    pass


class TimeoutError(ProxyError):
    """Request exceeded timeout"""
    pass


@dataclass
class ProxyResult:
    """Result of HTTP proxy request"""
    success: bool
    status_code: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    body: Optional[str] = None
    error: Optional[str] = None
    request_time_ms: Optional[float] = None


@dataclass
class SwarmPathPolicy:
    """Per-swarm path allow-list"""
    swarm_id: str
    paths: List[str]  # Regex patterns


@dataclass
class TargetConfig:
    """Target service configuration"""
    alias: str
    base_url: str
    allowed_swarms: Dict[str, SwarmPathPolicy]
    default_timeout_ms: int = 10000
    max_timeout_ms: int = 60000


class IFProxy:
    """
    Policy-governed external API proxy service for IF

    Provides:
    - Secure HTTP proxy from sandboxed environments
    - Per-swarm target alias registry (service discovery)
    - Path allow-list per swarm (security)
    - IF.witness audit logging (all requests)
    - Timeout enforcement (default 10000ms)
    - IF.governor capability integration

    Use Cases:
    - Call Meilisearch HTTP API (indexing, search)
    - Call Home Assistant API (device control)
    - Call vMix API (video switching)
    - Call OBS WebSocket API (scene management)
    - Enable provider integrations in Phases 1-6

    Security Model:
        1. Check IF.governor capability: 'network.http.proxy.external'
        2. Resolve target alias from registry
        3. Validate swarm has access to target
        4. Validate path against per-swarm allow-list
        5. Proxy HTTP request with timeout enforcement
        6. Log to IF.witness (audit trail)
    """

    def __init__(
        self,
        event_bus: EventBus,
        registry_path: str = '/etc/infrafabric/proxy_registry.json',
        witness_logger: Optional[Any] = None
    ):
        """
        Initialize IF.proxy

        Args:
            event_bus: EventBus for IF.bus communication
            registry_path: Path to target alias registry JSON file
            witness_logger: Optional IF.witness logger (for testing, can be mock)
        """
        self.bus = event_bus
        self.registry_path = Path(registry_path)
        self.witness_logger = witness_logger
        self._registry: Dict[str, TargetConfig] = {}
        self._watch_id: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        """
        Start IF.proxy service

        Subscribes to IF.bus command topic: if.command.network.proxy
        """
        logger.info("IF.proxy starting...")

        # Load target registry
        await self._load_registry()

        # Create HTTP client session
        self._session = aiohttp.ClientSession()

        # Subscribe to proxy requests
        self._watch_id = await self.bus.watch(
            'if.command.network.proxy',
            callback=self._handle_proxy_request
        )

        logger.info(f"IF.proxy started (watch_id: {self._watch_id})")

    async def stop(self):
        """Stop IF.proxy service"""
        if self._session:
            await self._session.close()

        if self._watch_id:
            logger.info("IF.proxy stopped")

    async def _handle_proxy_request(self, event):
        """
        Process HTTP proxy request from IF.bus

        Message format:
        {
            'trace_id': 'trace-123',
            'swarm_id': 'navidocs-adapter',
            'target_alias': 'meilisearch_api',
            'method': 'POST',
            'path': '/indexes/navidocs/documents',
            'headers': {'Content-Type': 'application/json'},
            'body': '{"id": 1, "title": "Doc 1"}',
            'timeout_ms': 10000
        }
        """
        try:
            if event.event_type != 'put':
                return

            msg = json.loads(event.value)

            trace_id = msg.get('trace_id')
            swarm_id = msg.get('swarm_id')
            target_alias = msg.get('target_alias')
            method = msg.get('method', 'GET')
            path = msg.get('path', '/')
            headers = msg.get('headers', {})
            body = msg.get('body')
            timeout_ms = msg.get('timeout_ms', 10000)

            # Validate required fields
            if not all([trace_id, swarm_id, target_alias]):
                await self._send_result(
                    trace_id or 'unknown',
                    success=False,
                    error='Missing required fields: trace_id, swarm_id, target_alias'
                )
                return

            # 1. Check IF.governor capability
            if not await self._check_capability(swarm_id, 'network.http.proxy.external'):
                await self._send_result(
                    trace_id,
                    success=False,
                    error=f'Swarm {swarm_id} lacks capability: network.http.proxy.external'
                )
                self._log_witness('request_denied_capability', swarm_id, target_alias, method, path)
                return

            # 2. Resolve target alias
            try:
                target = self._get_target(target_alias)
            except TargetNotFoundError as e:
                await self._send_result(
                    trace_id,
                    success=False,
                    error=str(e)
                )
                self._log_witness('request_denied_target_not_found', swarm_id, target_alias, method, path)
                return

            # 3. Validate swarm has access to target
            if swarm_id not in target.allowed_swarms:
                await self._send_result(
                    trace_id,
                    success=False,
                    error=f'Swarm {swarm_id} not allowed to access target: {target_alias}'
                )
                self._log_witness('request_denied_swarm_not_allowed', swarm_id, target_alias, method, path)
                return

            # 4. Validate path against swarm's allow-list
            swarm_policy = target.allowed_swarms[swarm_id]
            if not self._validate_path(swarm_policy, path):
                await self._send_result(
                    trace_id,
                    success=False,
                    error=f'Path not allowed: {path}'
                )
                self._log_witness('request_denied_path', swarm_id, target_alias, method, path)
                logger.warning(
                    f"Path violation: swarm={swarm_id} target={target_alias} path={path}"
                )
                return

            # 5. Proxy HTTP request with timeout
            timeout_ms = min(timeout_ms, target.max_timeout_ms)
            url = f"{target.base_url}{path}"

            try:
                result = await asyncio.wait_for(
                    self._make_request(method, url, headers, body),
                    timeout=timeout_ms / 1000
                )

                await self._send_result(trace_id, **asdict(result))

                self._log_witness(
                    'request_completed',
                    swarm_id,
                    target_alias,
                    method,
                    path,
                    {
                        'status_code': result.status_code,
                        'request_time_ms': result.request_time_ms,
                        'success': result.success
                    }
                )

                logger.info(
                    f"Proxied: swarm={swarm_id} target={target_alias} "
                    f"method={method} path={path} status={result.status_code} "
                    f"time={result.request_time_ms:.2f}ms"
                )

            except asyncio.TimeoutError:
                await self._send_result(
                    trace_id,
                    success=False,
                    error=f'Request timeout ({timeout_ms}ms exceeded)'
                )
                self._log_witness('request_timeout', swarm_id, target_alias, method, path,
                                {'timeout_ms': timeout_ms})
                logger.warning(
                    f"Timeout: swarm={swarm_id} target={target_alias} "
                    f"method={method} path={path} timeout={timeout_ms}ms"
                )

        except Exception as e:
            logger.error(f"Error handling proxy request: {e}", exc_info=True)
            if 'trace_id' in locals():
                await self._send_result(
                    trace_id,
                    success=False,
                    error=f'Internal error: {str(e)}'
                )

    async def _check_capability(self, swarm_id: str, capability: str) -> bool:
        """
        Check if swarm has required capability via IF.governor

        In production, this would query IF.governor. For now, checks etcd directly.
        """
        try:
            # Check if swarm has capability registered
            key = f'/swarms/{swarm_id}/capabilities'
            capabilities_json = await self.bus.get(key)

            if not capabilities_json:
                logger.warning(f"Swarm {swarm_id} not registered")
                return False

            capabilities = json.loads(capabilities_json)
            return capability in capabilities

        except Exception as e:
            logger.error(f"Capability check failed: {e}")
            return False

    async def _load_registry(self):
        """
        Load target alias registry from JSON file

        Format:
        {
          "meilisearch_api": {
            "alias": "meilisearch_api",
            "base_url": "http://127.0.0.1:7700",
            "allowed_swarms": {
              "navidocs-adapter": {
                "swarm_id": "navidocs-adapter",
                "paths": ["/indexes/navidocs/.*", "/health"]
              }
            },
            "default_timeout_ms": 10000,
            "max_timeout_ms": 60000
          },
          "home_assistant_api": {
            "alias": "home_assistant_api",
            "base_url": "http://homeassistant.local:8123",
            "allowed_swarms": {
              "ha-adapter": {
                "swarm_id": "ha-adapter",
                "paths": ["/api/.*"]
              }
            }
          }
        }
        """
        if not self.registry_path.exists():
            logger.warning(f"Registry file not found: {self.registry_path}")
            self._registry = {}
            return

        with open(self.registry_path, 'r') as f:
            registry_data = json.load(f)

        # Parse registry
        for alias, target_data in registry_data.items():
            allowed_swarms = {}
            for swarm_id, policy_data in target_data.get('allowed_swarms', {}).items():
                allowed_swarms[swarm_id] = SwarmPathPolicy(
                    swarm_id=policy_data['swarm_id'],
                    paths=policy_data['paths']
                )

            target = TargetConfig(
                alias=target_data['alias'],
                base_url=target_data['base_url'],
                allowed_swarms=allowed_swarms,
                default_timeout_ms=target_data.get('default_timeout_ms', 10000),
                max_timeout_ms=target_data.get('max_timeout_ms', 60000)
            )

            self._registry[alias] = target

        logger.info(f"Loaded {len(self._registry)} targets from registry")

    def _get_target(self, alias: str) -> TargetConfig:
        """
        Get target configuration by alias

        Raises TargetNotFoundError if alias not in registry
        """
        if alias not in self._registry:
            raise TargetNotFoundError(f"Unknown target alias: {alias}")

        return self._registry[alias]

    def _validate_path(self, policy: SwarmPathPolicy, path: str) -> bool:
        """
        Validate path against swarm's allow-list

        Returns True if path matches any allowed pattern, False otherwise
        """
        for pattern in policy.paths:
            if re.match(pattern, path):
                return True

        return False

    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: Optional[str]
    ) -> ProxyResult:
        """
        Make HTTP request to external API

        Uses aiohttp for async HTTP client
        """
        start_time = time.time()

        try:
            async with self._session.request(
                method,
                url,
                headers=headers,
                data=body
            ) as resp:
                response_body = await resp.text()
                request_time_ms = (time.time() - start_time) * 1000

                return ProxyResult(
                    success=(resp.status < 400),
                    status_code=resp.status,
                    headers=dict(resp.headers),
                    body=response_body if response_body else None,
                    request_time_ms=request_time_ms
                )

        except aiohttp.ClientError as e:
            return ProxyResult(
                success=False,
                error=f'HTTP client error: {str(e)}'
            )
        except Exception as e:
            return ProxyResult(
                success=False,
                error=f'Request failed: {str(e)}'
            )

    async def _send_result(self, trace_id: str, **kwargs):
        """
        Publish proxy result to IF.bus

        Topic: if.event.network.proxy.result

        Message format:
        {
            'trace_id': 'trace-123',
            'success': True,
            'status_code': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': '{"id": 1, "title": "Doc 1"}',
            'error': None,
            'request_time_ms': 123.4
        }
        """
        result = {
            'trace_id': trace_id,
            **kwargs
        }

        await self.bus.put(
            f'if.event.network.proxy.result/{trace_id}',
            json.dumps(result)
        )

    def _log_witness(
        self,
        operation: str,
        swarm_id: str,
        target_alias: str,
        method: str,
        path: str,
        extra: Optional[Dict] = None
    ):
        """
        Log operation to IF.witness for audit trail

        All proxy requests (allowed and denied) are logged
        """
        if not self.witness_logger:
            return

        log_entry = {
            'component': 'IF.proxy',
            'operation': operation,
            'timestamp': time.time(),
            'swarm_id': swarm_id,
            'target_alias': target_alias,
            'method': method,
            'path': path,
            **(extra or {})
        }

        # Support both callable and dict-based loggers
        if callable(self.witness_logger):
            self.witness_logger(log_entry)
        elif hasattr(self.witness_logger, 'log'):
            self.witness_logger.log(log_entry)
        elif hasattr(self.witness_logger, 'events'):
            self.witness_logger.events.append(log_entry)

    def add_target(
        self,
        alias: str,
        base_url: str,
        swarm_policies: Dict[str, List[str]],
        default_timeout_ms: int = 10000,
        max_timeout_ms: int = 60000
    ):
        """
        Add target to registry programmatically (for testing)

        Args:
            alias: Target alias (e.g., 'meilisearch_api')
            base_url: Base URL (e.g., 'http://127.0.0.1:7700')
            swarm_policies: Dict of swarm_id → allowed path patterns
            default_timeout_ms: Default request timeout
            max_timeout_ms: Maximum request timeout
        """
        allowed_swarms = {}
        for swarm_id, paths in swarm_policies.items():
            allowed_swarms[swarm_id] = SwarmPathPolicy(
                swarm_id=swarm_id,
                paths=paths
            )

        target = TargetConfig(
            alias=alias,
            base_url=base_url,
            allowed_swarms=allowed_swarms,
            default_timeout_ms=default_timeout_ms,
            max_timeout_ms=max_timeout_ms
        )

        self._registry[alias] = target
