"""
Home Assistant Infrastructure Adapter - IF.bus Protocol Implementation

This module provides the Home Assistant adapter for production infrastructure control
via REST API and WebSocket connections.

Features:
- mDNS discovery (homeassistant.local)
- REST API integration (/api/*)
- WebSocket real-time events
- Service calls (light, camera, automation, script)
- Entity state monitoring
- Event firing

Use Cases:
- Camera control (RTSP → NDI bridge)
- Studio lighting control
- Automation triggers (production events)
- Sensor monitoring (temperature, humidity)

Author: Agent 8 (IF.bus architecture)
Version: 1.0.0
Date: 2025-11-12
"""

import asyncio
import json
import logging
import socket
import ssl
import threading
import time
import websocket
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
    ZEROCONF_AVAILABLE = True
except ImportError:
    ZEROCONF_AVAILABLE = False
    ServiceListener = object  # Fallback for type hints

from .production_adapter_base import (
    ProductionAdapterBase,
    InstanceState,
    CommandType,
    HealthStatus,
    ErrorSeverity,
    ConnectionError,
    InstanceError,
    CommandExecutionError,
    ConfigurationError,
    TimeoutError,
    DiscoveryError,
)


# ============================================================================
# Constants
# ============================================================================

DEFAULT_PORT = 8123
DEFAULT_TIMEOUT = 30
DEFAULT_DISCOVERY_TIMEOUT = 5
MDNS_SERVICE_TYPE = "_home-assistant._tcp.local."
WEBSOCKET_RECONNECT_DELAY = 5
WEBSOCKET_PING_INTERVAL = 30
MAX_RECONNECT_ATTEMPTS = 10


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class HomeAssistantInstance:
    """Home Assistant instance configuration and state."""
    instance_id: str
    name: str
    host: str
    port: int
    token: str
    use_ssl: bool = False
    verify_ssl: bool = True

    # Connection state
    http_session: Optional[requests.Session] = None
    ws_connection: Optional[websocket.WebSocketApp] = None
    ws_thread: Optional[threading.Thread] = None
    ws_connected: bool = False
    ws_auth_id: Optional[int] = None

    # Metrics
    created_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    command_count: int = 0
    error_count: int = 0

    # State
    state: InstanceState = InstanceState.CREATED
    version: Optional[str] = None
    config_data: Optional[Dict[str, Any]] = None

    @property
    def base_url(self) -> str:
        """Get base URL for REST API."""
        protocol = "https" if self.use_ssl else "http"
        return f"{protocol}://{self.host}:{self.port}"

    @property
    def ws_url(self) -> str:
        """Get WebSocket URL."""
        protocol = "wss" if self.use_ssl else "ws"
        return f"{protocol}://{self.host}:{self.port}/api/websocket"

    @property
    def uptime_seconds(self) -> float:
        """Get instance uptime."""
        return time.time() - self.created_at


# ============================================================================
# mDNS Discovery Listener
# ============================================================================

if ZEROCONF_AVAILABLE:
    class HomeAssistantListener(ServiceListener):
        """mDNS service discovery listener for Home Assistant."""

        def __init__(self, logger: logging.Logger):
            self.logger = logger
            self.discovered: Dict[str, Dict[str, Any]] = {}
            self._lock = threading.Lock()

        def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
            """Called when a service is discovered."""
            info = zc.get_service_info(type_, name)
            if info:
                with self._lock:
                    # Extract host and port
                    addresses = [socket.inet_ntoa(addr) for addr in info.addresses]
                    host = addresses[0] if addresses else None
                    port = info.port

                    if host and port:
                        instance_key = f"{host}:{port}"
                        self.discovered[instance_key] = {
                            "name": name.replace(f".{type_}", ""),
                            "host": host,
                            "port": port,
                            "addresses": addresses,
                            "properties": {
                                k.decode() if isinstance(k, bytes) else k:
                                v.decode() if isinstance(v, bytes) else v
                                for k, v in info.properties.items()
                            }
                        }
                        self.logger.info(f"Discovered Home Assistant: {instance_key}")

        def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
            """Called when a service is removed."""
            self.logger.info(f"Home Assistant removed: {name}")

        def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
            """Called when a service is updated."""
            self.add_service(zc, type_, name)

        def get_discovered(self) -> Dict[str, Dict[str, Any]]:
            """Get all discovered instances."""
            with self._lock:
                return self.discovered.copy()


# ============================================================================
# Home Assistant Adapter
# ============================================================================

class HomeAssistantAdapter(ProductionAdapterBase):
    """
    Home Assistant production infrastructure adapter.

    Provides integration with Home Assistant for:
    - Camera control (RTSP → NDI bridge)
    - Studio lighting control
    - Automation triggers
    - Sensor monitoring

    Connection Methods:
    - REST API: HTTP/HTTPS for commands and queries
    - WebSocket: Real-time event streaming
    - mDNS: Auto-discovery on local network
    """

    adapter_type = "home_assistant"
    SUPPORTED_VERSIONS = {
        "home_assistant": ["2023.1", "2023.12", "2024.1", "2024.11", "2025.1"]
    }

    def __init__(self, config: Dict[str, Any], **kwargs):
        """
        Initialize Home Assistant adapter.

        Args:
            config: Configuration dictionary
                - type: "home_assistant"
                - timeout: Request timeout (default: 30s)
                - discovery_timeout: Discovery timeout (default: 5s)
                - enable_websocket: Enable WebSocket connections (default: True)
        """
        super().__init__(config, **kwargs)

        # Adapter configuration
        self.timeout = config.get("timeout", DEFAULT_TIMEOUT)
        self.discovery_timeout = config.get("discovery_timeout", DEFAULT_DISCOVERY_TIMEOUT)
        self.enable_websocket = config.get("enable_websocket", True)

        # Instance registry
        self._ha_instances: Dict[str, HomeAssistantInstance] = {}

        # WebSocket message counter
        self._ws_message_id = 0
        self._ws_message_lock = threading.Lock()

        self.logger.info(f"Home Assistant adapter initialized (WebSocket: {self.enable_websocket})")

    # ========================================================================
    # Abstract Method Implementations
    # ========================================================================

    def discover_instances(
        self,
        network_config: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Auto-discover Home Assistant instances via mDNS.

        Searches for _home-assistant._tcp.local. services and validates
        via REST API health check.

        Args:
            network_config: Optional configuration
                - timeout: Discovery timeout (default: 5s)
                - interfaces: Network interfaces to search

        Returns:
            List of discovered instance identifiers (host:port)

        Raises:
            DiscoveryError: If discovery fails
        """
        if not ZEROCONF_AVAILABLE:
            raise DiscoveryError(
                "mDNS discovery requires zeroconf library. Install: pip install zeroconf"
            )

        timeout = network_config.get("timeout", self.discovery_timeout) if network_config else self.discovery_timeout

        self.logger.info(f"Starting Home Assistant mDNS discovery (timeout: {timeout}s)")

        discovered_instances = []
        listener = HomeAssistantListener(self.logger)

        try:
            zeroconf = Zeroconf()
            browser = ServiceBrowser(zeroconf, MDNS_SERVICE_TYPE, listener)

            # Wait for discovery
            time.sleep(timeout)

            # Get discovered instances
            discovered = listener.get_discovered()

            # Validate each instance with health check
            for instance_key, info in discovered.items():
                try:
                    host = info["host"]
                    port = info["port"]

                    # Try to ping /api endpoint
                    url = f"http://{host}:{port}/api/"
                    response = requests.get(url, timeout=5)

                    if response.status_code == 200:
                        discovered_instances.append(instance_key)
                        self.logger.info(f"Validated Home Assistant instance: {instance_key}")
                    else:
                        self.logger.warning(f"Invalid response from {instance_key}: {response.status_code}")

                except Exception as e:
                    self.logger.warning(f"Failed to validate {instance_key}: {e}")

            browser.cancel()
            zeroconf.close()

            # Emit discovery event
            self.emit_discovery(
                instance_count=len(discovered_instances),
                new_instances=discovered_instances,
                removed_instances=[],
                details={"method": "mdns", "service_type": MDNS_SERVICE_TYPE}
            )

            self.logger.info(f"Discovered {len(discovered_instances)} Home Assistant instances")
            return discovered_instances

        except Exception as e:
            raise DiscoveryError(f"mDNS discovery failed: {e}")

    def add_instance(self, name: str, config: Dict[str, Any]) -> str:
        """
        Add Home Assistant instance to registry.

        Creates HTTP session and WebSocket connection for real-time events.

        Args:
            name: Friendly instance name
            config: Instance configuration
                - host: Hostname or IP address (required)
                - port: Port number (default: 8123)
                - token: Long-lived access token (required)
                - use_ssl: Use HTTPS/WSS (default: False)
                - verify_ssl: Verify SSL certificates (default: True)

        Returns:
            instance_id: Unique instance identifier

        Raises:
            ConfigurationError: If config invalid
            InstanceError: If instance cannot be added
        """
        self.logger.info(f"Adding Home Assistant instance: {name}")

        # Validate configuration
        if "host" not in config:
            raise ConfigurationError("Missing required field: host")
        if "token" not in config:
            raise ConfigurationError("Missing required field: token")

        host = config["host"]
        port = config.get("port", DEFAULT_PORT)
        token = config["token"]
        use_ssl = config.get("use_ssl", False)
        verify_ssl = config.get("verify_ssl", True)

        # Generate instance ID
        instance_id = self.generate_instance_id()

        # Create instance
        instance = HomeAssistantInstance(
            instance_id=instance_id,
            name=name,
            host=host,
            port=port,
            token=token,
            use_ssl=use_ssl,
            verify_ssl=verify_ssl,
        )

        try:
            # Create HTTP session with retry logic
            session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            session.headers.update({
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            })
            session.verify = verify_ssl
            instance.http_session = session

            # Validate connection
            response = session.get(
                urljoin(instance.base_url, "/api/"),
                timeout=self.timeout
            )
            response.raise_for_status()

            api_info = response.json()
            self.logger.info(f"Connected to Home Assistant API: {api_info.get('message', 'OK')}")

            # Get config information
            config_response = session.get(
                urljoin(instance.base_url, "/api/config"),
                timeout=self.timeout
            )
            config_response.raise_for_status()
            instance.config_data = config_response.json()
            instance.version = instance.config_data.get("version", "unknown")

            # Update state
            instance.state = InstanceState.CONNECTED
            instance.last_seen = time.time()

            # Store instance
            with self._lock:
                self._ha_instances[name] = instance
                self._add_instance(instance_id, {
                    "name": name,
                    "host": host,
                    "port": port,
                    "version": instance.version,
                })

            # Emit state change event
            self.emit_instance_state_changed(
                instance_name=name,
                instance_id=instance_id,
                state=InstanceState.CONNECTED,
                details={
                    "host": host,
                    "port": port,
                    "version": instance.version,
                }
            )

            # Start WebSocket connection if enabled
            if self.enable_websocket:
                self._start_websocket(instance)

            self.logger.info(f"Added Home Assistant instance: {name} (ID: {instance_id}, Version: {instance.version})")
            return instance_id

        except requests.exceptions.RequestException as e:
            raise InstanceError(f"Failed to connect to Home Assistant instance: {e}")
        except Exception as e:
            raise InstanceError(f"Failed to add instance: {e}")

    def remove_instance(self, name: str) -> bool:
        """
        Remove Home Assistant instance from registry.

        Closes HTTP session and WebSocket connection.

        Args:
            name: Instance name to remove

        Returns:
            True if successful

        Raises:
            InstanceError: If instance not found
        """
        self.logger.info(f"Removing Home Assistant instance: {name}")

        with self._lock:
            if name not in self._ha_instances:
                raise InstanceError(f"Instance not found: {name}")

            instance = self._ha_instances[name]

        try:
            # Stop WebSocket connection
            if instance.ws_connection:
                instance.ws_connection.close()
                instance.ws_connected = False

            if instance.ws_thread and instance.ws_thread.is_alive():
                instance.ws_thread.join(timeout=5)

            # Close HTTP session
            if instance.http_session:
                instance.http_session.close()

            # Update state
            instance.state = InstanceState.DISCONNECTED

            # Remove from registry
            with self._lock:
                del self._ha_instances[name]
                self._remove_instance(instance.instance_id)

            # Emit state change event
            self.emit_instance_state_changed(
                instance_name=name,
                instance_id=instance.instance_id,
                state=InstanceState.DISCONNECTED,
                details={"reason": "removed"}
            )

            self.logger.info(f"Removed Home Assistant instance: {name}")
            return True

        except Exception as e:
            raise InstanceError(f"Failed to remove instance: {e}")

    def get_instance_status(self, name: str) -> Dict[str, Any]:
        """
        Get Home Assistant instance health/status.

        Queries /api/config and /api/states for comprehensive status.

        Args:
            name: Instance name

        Returns:
            Status dictionary with instance details

        Raises:
            InstanceError: If instance not found
        """
        with self._lock:
            if name not in self._ha_instances:
                raise InstanceError(f"Instance not found: {name}")

            instance = self._ha_instances[name]

        try:
            # Get current config
            config_response = instance.http_session.get(
                urljoin(instance.base_url, "/api/config"),
                timeout=self.timeout
            )
            config_response.raise_for_status()
            config_data = config_response.json()

            # Get state count
            states_response = instance.http_session.get(
                urljoin(instance.base_url, "/api/states"),
                timeout=self.timeout
            )
            states_response.raise_for_status()
            states = states_response.json()

            instance.last_seen = time.time()
            instance.config_data = config_data

            return {
                "instance_id": instance.instance_id,
                "name": instance.name,
                "state": instance.state.value,
                "connected": instance.state == InstanceState.CONNECTED,
                "last_seen": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(instance.last_seen)),
                "uptime_seconds": instance.uptime_seconds,
                "command_count": instance.command_count,
                "error_count": instance.error_count,
                "details": {
                    "host": instance.host,
                    "port": instance.port,
                    "version": config_data.get("version"),
                    "location_name": config_data.get("location_name"),
                    "latitude": config_data.get("latitude"),
                    "longitude": config_data.get("longitude"),
                    "timezone": config_data.get("time_zone"),
                    "unit_system": config_data.get("unit_system"),
                    "entity_count": len(states),
                    "websocket_connected": instance.ws_connected,
                    "use_ssl": instance.use_ssl,
                }
            }

        except requests.exceptions.RequestException as e:
            instance.error_count += 1
            raise InstanceError(f"Failed to get instance status: {e}")

    def execute_command(
        self,
        name: str,
        command: str,
        command_type: CommandType = CommandType.CUSTOM,
        **params
    ) -> Dict[str, Any]:
        """
        Execute command on Home Assistant instance.

        Supported commands:
        - call_service: Call HA service (domain.service)
        - get_states: Get all entity states
        - get_state: Get single entity state
        - fire_event: Fire custom event

        Args:
            name: Instance name
            command: Command to execute
            command_type: Type of command
            params: Command-specific parameters

                For call_service:
                - domain: Service domain (e.g., "light", "camera")
                - service: Service name (e.g., "turn_on", "turn_off")
                - entity_id: Target entity (optional)
                - service_data: Additional service parameters

                For get_state:
                - entity_id: Entity to query

                For fire_event:
                - event_type: Event type name
                - event_data: Event data dictionary

        Returns:
            Command result dictionary

        Raises:
            CommandExecutionError: If command fails
            InstanceError: If instance not found
        """
        with self._lock:
            if name not in self._ha_instances:
                raise InstanceError(f"Instance not found: {name}")

            instance = self._ha_instances[name]

        start_time = time.time()

        try:
            result = {}

            if command == "call_service":
                result = self._call_service(instance, **params)

            elif command == "get_states":
                result = self._get_states(instance)

            elif command == "get_state":
                result = self._get_state(instance, **params)

            elif command == "fire_event":
                result = self._fire_event(instance, **params)

            else:
                raise CommandExecutionError(f"Unknown command: {command}")

            # Update metrics
            duration_ms = (time.time() - start_time) * 1000
            instance.command_count += 1
            instance.last_seen = time.time()
            self.metrics.record_command(success=True, duration_ms=duration_ms)

            # Emit command execution event
            self.emit_command_execution(
                instance_name=name,
                command=command,
                command_type=command_type,
                success=True,
                duration_ms=duration_ms,
                result=result,
            )

            return {
                "success": True,
                "result": result,
                "duration_ms": duration_ms,
            }

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            instance.error_count += 1
            self.metrics.record_command(success=False, duration_ms=duration_ms)

            # Emit command execution event
            self.emit_command_execution(
                instance_name=name,
                command=command,
                command_type=command_type,
                success=False,
                duration_ms=duration_ms,
                error=str(e),
            )

            raise CommandExecutionError(f"Command execution failed: {e}")

    def health_check(self) -> Dict[str, Any]:
        """
        Return comprehensive adapter health metrics.

        Returns:
            Health status dictionary with adapter and instance metrics
        """
        metrics = self.metrics.get_metrics()

        with self._lock:
            total_instances = len(self._ha_instances)
            connected_instances = sum(
                1 for inst in self._ha_instances.values()
                if inst.state == InstanceState.CONNECTED
            )
            error_instances = sum(
                1 for inst in self._ha_instances.values()
                if inst.state == InstanceState.ERROR
            )

        # Update metrics
        self.metrics.update_instance_count(
            total=total_instances,
            connected=connected_instances,
            errors=error_instances
        )

        # Determine health status
        if error_instances > 0 or metrics["connection_failures"] > 0:
            status = HealthStatus.DEGRADED
        elif connected_instances == total_instances and total_instances > 0:
            status = HealthStatus.HEALTHY
        elif connected_instances == 0 and total_instances > 0:
            status = HealthStatus.CRITICAL
        else:
            status = HealthStatus.HEALTHY

        return {
            "adapter": self.adapter_type,
            "connected": self.connected,
            "uptime_seconds": metrics["uptime_seconds"],
            "instances": {
                "total": total_instances,
                "connected": connected_instances,
                "errors": error_instances,
            },
            "metrics": {
                "command_attempts": metrics["command_attempts"],
                "command_success_rate": metrics["command_success_rate"],
                "avg_command_duration_ms": metrics["avg_command_duration_ms"],
                "connection_failures": metrics["connection_failures"],
                "last_error": metrics["last_error"],
            },
            "latency": metrics["latency"],
            "last_check": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": status.value,
            "websocket_enabled": self.enable_websocket,
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate Home Assistant configuration schema.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if valid

        Raises:
            ConfigurationError: If validation fails
        """
        # Check adapter type
        if config.get("type") != "home_assistant":
            raise ConfigurationError(f"Invalid adapter type: {config.get('type')}")

        # Validate timeout
        timeout = config.get("timeout", DEFAULT_TIMEOUT)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ConfigurationError(f"Invalid timeout: {timeout}")

        # Validate discovery timeout
        discovery_timeout = config.get("discovery_timeout", DEFAULT_DISCOVERY_TIMEOUT)
        if not isinstance(discovery_timeout, (int, float)) or discovery_timeout <= 0:
            raise ConfigurationError(f"Invalid discovery_timeout: {discovery_timeout}")

        return True

    # ========================================================================
    # Home Assistant Command Implementations
    # ========================================================================

    def _call_service(
        self,
        instance: HomeAssistantInstance,
        domain: str,
        service: str,
        entity_id: Optional[str] = None,
        service_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call Home Assistant service.

        Examples:
        - light.turn_on (entity_id="light.studio_main", brightness=255)
        - camera.enable_motion_detection (entity_id="camera.studio_cam_1")
        - automation.trigger (entity_id="automation.production_start")
        - script.run (entity_id="script.studio_setup")
        """
        if not domain or not service:
            raise CommandExecutionError("Missing required parameters: domain, service")

        # Build service data
        data = service_data or {}
        if entity_id:
            data["entity_id"] = entity_id

        # Merge additional kwargs
        data.update(kwargs)

        # Call service
        url = urljoin(instance.base_url, f"/api/services/{domain}/{service}")
        response = instance.http_session.post(
            url,
            json=data,
            timeout=self.timeout
        )
        response.raise_for_status()

        result = response.json()

        self.logger.info(f"Called service {domain}.{service} on {instance.name}")

        return {
            "domain": domain,
            "service": service,
            "entity_id": entity_id,
            "response": result,
        }

    def _get_states(self, instance: HomeAssistantInstance) -> Dict[str, Any]:
        """Get all entity states."""
        url = urljoin(instance.base_url, "/api/states")
        response = instance.http_session.get(url, timeout=self.timeout)
        response.raise_for_status()

        states = response.json()

        return {
            "entity_count": len(states),
            "states": states,
        }

    def _get_state(
        self,
        instance: HomeAssistantInstance,
        entity_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get single entity state."""
        if not entity_id:
            raise CommandExecutionError("Missing required parameter: entity_id")

        url = urljoin(instance.base_url, f"/api/states/{entity_id}")
        response = instance.http_session.get(url, timeout=self.timeout)
        response.raise_for_status()

        state = response.json()

        return {
            "entity_id": entity_id,
            "state": state,
        }

    def _fire_event(
        self,
        instance: HomeAssistantInstance,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Fire custom event."""
        if not event_type:
            raise CommandExecutionError("Missing required parameter: event_type")

        data = event_data or {}
        data.update(kwargs)

        url = urljoin(instance.base_url, f"/api/events/{event_type}")
        response = instance.http_session.post(
            url,
            json=data,
            timeout=self.timeout
        )
        response.raise_for_status()

        result = response.json()

        self.logger.info(f"Fired event {event_type} on {instance.name}")

        return {
            "event_type": event_type,
            "event_data": data,
            "response": result,
        }

    # ========================================================================
    # WebSocket Implementation
    # ========================================================================

    def _start_websocket(self, instance: HomeAssistantInstance) -> None:
        """Start WebSocket connection for real-time events."""
        if instance.ws_connected:
            self.logger.warning(f"WebSocket already connected for {instance.name}")
            return

        def on_message(ws, message):
            """Handle WebSocket message."""
            try:
                data = json.loads(message)
                msg_type = data.get("type")

                if msg_type == "auth_required":
                    # Send authentication
                    auth_msg = {
                        "type": "auth",
                        "access_token": instance.token,
                    }
                    ws.send(json.dumps(auth_msg))

                elif msg_type == "auth_ok":
                    instance.ws_connected = True
                    instance.ws_auth_id = data.get("ha_version")
                    self.logger.info(f"WebSocket authenticated for {instance.name}")

                    # Subscribe to state changes
                    subscribe_msg = {
                        "id": self._get_ws_message_id(),
                        "type": "subscribe_events",
                        "event_type": "state_changed",
                    }
                    ws.send(json.dumps(subscribe_msg))

                elif msg_type == "auth_invalid":
                    self.logger.error(f"WebSocket authentication failed for {instance.name}")
                    instance.ws_connected = False

                elif msg_type == "event":
                    # Handle state change event
                    event_data = data.get("event", {})
                    self._handle_state_change_event(instance, event_data)

                elif msg_type == "result":
                    # Command result
                    self.logger.debug(f"WebSocket result: {data}")

            except Exception as e:
                self.logger.error(f"WebSocket message error: {e}")

        def on_error(ws, error):
            """Handle WebSocket error."""
            self.logger.error(f"WebSocket error for {instance.name}: {error}")
            instance.ws_connected = False

        def on_close(ws, close_status_code, close_msg):
            """Handle WebSocket close."""
            self.logger.info(f"WebSocket closed for {instance.name}")
            instance.ws_connected = False

        def on_open(ws):
            """Handle WebSocket open."""
            self.logger.info(f"WebSocket opened for {instance.name}")

        # Create WebSocket connection
        ws = websocket.WebSocketApp(
            instance.ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
        )

        instance.ws_connection = ws

        # Start WebSocket thread
        ws_thread = threading.Thread(
            target=ws.run_forever,
            kwargs={"ping_interval": WEBSOCKET_PING_INTERVAL},
            daemon=True,
        )
        ws_thread.start()
        instance.ws_thread = ws_thread

        self.logger.info(f"WebSocket connection started for {instance.name}")

    def _get_ws_message_id(self) -> int:
        """Get unique WebSocket message ID."""
        with self._ws_message_lock:
            self._ws_message_id += 1
            return self._ws_message_id

    def _handle_state_change_event(
        self,
        instance: HomeAssistantInstance,
        event_data: Dict[str, Any]
    ) -> None:
        """Handle state change event from WebSocket."""
        entity_id = event_data.get("data", {}).get("entity_id")
        new_state = event_data.get("data", {}).get("new_state", {})

        self.logger.debug(
            f"State change for {instance.name}: {entity_id} -> {new_state.get('state')}"
        )

        # Could emit custom event here for state monitoring
        # self.event_emitter.emit("entity_state_changed", {...})

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def get_instance(self, name: str) -> Optional[HomeAssistantInstance]:
        """Get instance by name."""
        with self._lock:
            return self._ha_instances.get(name)

    def list_instances(self) -> List[str]:
        """Get list of all instance names."""
        with self._lock:
            return list(self._ha_instances.keys())

    def get_entity_domains(self, name: str) -> List[str]:
        """Get list of available entity domains."""
        instance = self.get_instance(name)
        if not instance:
            raise InstanceError(f"Instance not found: {name}")

        try:
            url = urljoin(instance.base_url, "/api/states")
            response = instance.http_session.get(url, timeout=self.timeout)
            response.raise_for_status()

            states = response.json()
            domains = set()

            for state in states:
                entity_id = state.get("entity_id", "")
                if "." in entity_id:
                    domain = entity_id.split(".")[0]
                    domains.add(domain)

            return sorted(list(domains))

        except Exception as e:
            raise CommandExecutionError(f"Failed to get entity domains: {e}")


# ============================================================================
# Convenience Functions
# ============================================================================

def create_home_assistant_adapter(
    timeout: int = DEFAULT_TIMEOUT,
    discovery_timeout: int = DEFAULT_DISCOVERY_TIMEOUT,
    enable_websocket: bool = True,
    **kwargs
) -> HomeAssistantAdapter:
    """
    Create Home Assistant adapter with common configuration.

    Args:
        timeout: Request timeout in seconds
        discovery_timeout: Discovery timeout in seconds
        enable_websocket: Enable WebSocket connections
        **kwargs: Additional configuration options

    Returns:
        Configured HomeAssistantAdapter instance
    """
    config = {
        "type": "home_assistant",
        "timeout": timeout,
        "discovery_timeout": discovery_timeout,
        "enable_websocket": enable_websocket,
    }
    config.update(kwargs)

    return HomeAssistantAdapter(config)


# ============================================================================
# Module Testing
# ============================================================================

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Create adapter
    adapter = create_home_assistant_adapter()

    print("Home Assistant Adapter created")
    print(f"Adapter type: {adapter.adapter_type}")
    print(f"Supported versions: {adapter.SUPPORTED_VERSIONS}")

    # Example: Add instance
    # instance_id = adapter.add_instance(
    #     name="studio_ha",
    #     config={
    #         "host": "192.168.1.100",
    #         "port": 8123,
    #         "token": "your_long_lived_access_token_here",
    #         "use_ssl": False,
    #     }
    # )

    # Example: Execute commands
    # adapter.execute_command(
    #     name="studio_ha",
    #     command="call_service",
    #     domain="light",
    #     service="turn_on",
    #     entity_id="light.studio_main",
    #     brightness=255
    # )

    # adapter.execute_command(
    #     name="studio_ha",
    #     command="call_service",
    #     domain="camera",
    #     service="enable_motion_detection",
    #     entity_id="camera.studio_cam_1"
    # )

    # Example: Get status
    # status = adapter.get_instance_status("studio_ha")
    # print(f"Instance status: {json.dumps(status, indent=2)}")

    # Example: Health check
    # health = adapter.health_check()
    # print(f"Adapter health: {json.dumps(health, indent=2)}")

    print("\nHome Assistant adapter ready for production use")
