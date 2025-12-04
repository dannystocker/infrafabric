"""
OBS Studio Production Adapter - IF.bus Integration

This module provides a complete adapter for OBS Studio (Open Broadcaster Software)
via the obs-websocket v5.x protocol.

Protocol: OBS WebSocket v5.x (JSON-RPC over WebSocket)
Port: 4455 (default)
Discovery: Network port scanning
Authentication: SHA256 challenge/response
Events: Real-time WebSocket subscriptions

Philosophy: Confucian Wu Lun (五伦) relationship mapping for instance hierarchy.
Protocol: IF.TTT (Traceable/Transparent/Trustworthy) compliance.
Logging: IF.witness integration for audit trails.
Metrics: IF.optimise integration for performance optimization.

Author: Agent 8 (IF.bus architecture)
Version: 1.0.0
Date: 2025-11-12
"""

import base64
import hashlib
import json
import logging
import socket
import threading
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
import queue

try:
    import websocket
except ImportError:
    raise ImportError(
        "websocket-client library required. Install with: pip install websocket-client"
    )

from production_adapter_base import (
    ProductionAdapterBase,
    InstanceState,
    CommandType,
    HealthStatus,
    ErrorSeverity,
    ConfigurationError,
    ConnectionError,
    InstanceError,
    CommandExecutionError,
    TimeoutError,
    DiscoveryError,
)


# ============================================================================
# OBS-Specific Constants
# ============================================================================

OBS_DEFAULT_PORT = 4455
OBS_PROTOCOL_VERSION = "5.0.0"
OBS_REQUEST_TIMEOUT = 30.0  # seconds
OBS_CONNECTION_TIMEOUT = 10.0  # seconds
OBS_DISCOVERY_TIMEOUT = 2.0  # seconds per host


# OBS Request Types (v5.x)
class OBSRequestType:
    """Standard OBS WebSocket v5 request types."""
    # General
    GET_VERSION = "GetVersion"
    GET_STATS = "GetStats"

    # Scenes
    GET_SCENE_LIST = "GetSceneList"
    GET_CURRENT_PROGRAM_SCENE = "GetCurrentProgramScene"
    SET_CURRENT_PROGRAM_SCENE = "SetCurrentProgramScene"
    GET_CURRENT_PREVIEW_SCENE = "GetCurrentPreviewScene"
    SET_CURRENT_PREVIEW_SCENE = "SetCurrentPreviewScene"

    # Streaming
    GET_STREAM_STATUS = "GetStreamStatus"
    START_STREAM = "StartStream"
    STOP_STREAM = "StopStream"
    TOGGLE_STREAM = "ToggleStream"

    # Recording
    GET_RECORD_STATUS = "GetRecordStatus"
    START_RECORD = "StartRecord"
    STOP_RECORD = "StopRecord"
    TOGGLE_RECORD = "ToggleRecord"
    PAUSE_RECORD = "PauseRecord"
    RESUME_RECORD = "ResumeRecord"

    # Virtual Camera
    GET_VIRTUAL_CAM_STATUS = "GetVirtualCamStatus"
    START_VIRTUAL_CAM = "StartVirtualCam"
    STOP_VIRTUAL_CAM = "StopVirtualCam"
    TOGGLE_VIRTUAL_CAM = "ToggleVirtualCam"

    # Inputs
    GET_INPUT_LIST = "GetInputList"
    GET_INPUT_SETTINGS = "GetInputSettings"
    SET_INPUT_SETTINGS = "SetInputSettings"
    GET_INPUT_MUTE = "GetInputMute"
    SET_INPUT_MUTE = "SetInputMute"
    TOGGLE_INPUT_MUTE = "ToggleInputMute"

    # Transitions
    GET_CURRENT_SCENE_TRANSITION = "GetCurrentSceneTransition"
    SET_CURRENT_SCENE_TRANSITION = "SetCurrentSceneTransition"


class OBSEventType:
    """OBS WebSocket v5 event types."""
    # General
    EXIT_STARTED = "ExitStarted"

    # Scenes
    CURRENT_PROGRAM_SCENE_CHANGED = "CurrentProgramSceneChanged"
    SCENE_CREATED = "SceneCreated"
    SCENE_REMOVED = "SceneRemoved"

    # Streaming
    STREAM_STATE_CHANGED = "StreamStateChanged"

    # Recording
    RECORD_STATE_CHANGED = "RecordStateChanged"

    # Virtual Camera
    VIRTUAL_CAM_STATE_CHANGED = "VirtualcamStateChanged"


# ============================================================================
# OBS WebSocket Client
# ============================================================================

class OBSWebSocketClient:
    """
    OBS WebSocket v5.x client implementation.

    Features:
    - Automatic authentication via SHA256 challenge/response
    - Request/response handling with unique message IDs
    - Event subscription and callback handling
    - Background thread for receiving messages
    - Thread-safe request queue
    """

    def __init__(
        self,
        host: str,
        port: int = OBS_DEFAULT_PORT,
        password: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.host = host
        self.port = port
        self.password = password
        self.logger = logger or logging.getLogger(__name__)

        # WebSocket connection
        self.ws: Optional[websocket.WebSocketApp] = None
        self.ws_thread: Optional[threading.Thread] = None
        self.connected = False
        self.authenticated = False

        # Request/response handling
        self._request_id_counter = 0
        self._pending_requests: Dict[str, queue.Queue] = {}
        self._request_lock = threading.Lock()

        # Event handling
        self._event_callbacks: Dict[str, List[callable]] = {}
        self._event_lock = threading.Lock()

        # Connection state
        self._connect_event = threading.Event()
        self._disconnect_event = threading.Event()
        self._running = False

    def connect(self, timeout: float = OBS_CONNECTION_TIMEOUT) -> bool:
        """
        Connect to OBS WebSocket server.

        Args:
            timeout: Connection timeout in seconds

        Returns:
            True if connected and authenticated

        Raises:
            ConnectionError: If connection fails
        """
        if self.connected:
            self.logger.warning("Already connected to OBS")
            return True

        url = f"ws://{self.host}:{self.port}"
        self.logger.info(f"Connecting to OBS WebSocket: {url}")

        self._running = True
        self._connect_event.clear()

        # Create WebSocketApp
        self.ws = websocket.WebSocketApp(
            url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )

        # Start WebSocket thread
        self.ws_thread = threading.Thread(
            target=self.ws.run_forever,
            daemon=True
        )
        self.ws_thread.start()

        # Wait for connection
        if not self._connect_event.wait(timeout):
            self._running = False
            raise ConnectionError(
                f"Connection to OBS at {self.host}:{self.port} timed out",
                retryable=True
            )

        self.logger.info(f"Connected to OBS at {self.host}:{self.port}")
        return True

    def disconnect(self) -> None:
        """Gracefully disconnect from OBS WebSocket."""
        if not self.connected:
            return

        self.logger.info("Disconnecting from OBS")
        self._running = False

        if self.ws:
            self.ws.close()

        if self.ws_thread and self.ws_thread.is_alive():
            self._disconnect_event.wait(timeout=5.0)

        self.connected = False
        self.authenticated = False

    def send_request(
        self,
        request_type: str,
        request_data: Optional[Dict[str, Any]] = None,
        timeout: float = OBS_REQUEST_TIMEOUT
    ) -> Dict[str, Any]:
        """
        Send request to OBS and wait for response.

        Args:
            request_type: OBS request type
            request_data: Optional request parameters
            timeout: Response timeout in seconds

        Returns:
            Response data dictionary

        Raises:
            CommandExecutionError: If request fails
            TimeoutError: If request times out
        """
        if not self.connected or not self.authenticated:
            raise ConnectionError("Not connected to OBS", retryable=True)

        # Generate unique request ID
        with self._request_lock:
            self._request_id_counter += 1
            request_id = str(self._request_id_counter)

        # Create response queue
        response_queue = queue.Queue()
        with self._request_lock:
            self._pending_requests[request_id] = response_queue

        try:
            # Build request message
            message = {
                "op": 6,  # Request opcode
                "d": {
                    "requestType": request_type,
                    "requestId": request_id,
                }
            }

            if request_data:
                message["d"]["requestData"] = request_data

            # Send request
            self.ws.send(json.dumps(message))
            self.logger.debug(f"Sent OBS request: {request_type} (id={request_id})")

            # Wait for response
            try:
                response = response_queue.get(timeout=timeout)
            except queue.Empty:
                raise TimeoutError(
                    f"OBS request {request_type} timed out after {timeout}s",
                    retryable=True
                )

            # Check for errors
            if not response.get("requestStatus", {}).get("result", False):
                error_code = response.get("requestStatus", {}).get("code", -1)
                error_comment = response.get("requestStatus", {}).get("comment", "Unknown error")
                raise CommandExecutionError(
                    f"OBS request failed: {error_comment} (code={error_code})",
                    code=error_code
                )

            return response.get("responseData", {})

        finally:
            # Clean up pending request
            with self._request_lock:
                self._pending_requests.pop(request_id, None)

    def subscribe_event(self, event_type: str, callback: callable) -> None:
        """
        Subscribe to OBS event.

        Args:
            event_type: Event type to subscribe to
            callback: Callback function(event_data)
        """
        with self._event_lock:
            if event_type not in self._event_callbacks:
                self._event_callbacks[event_type] = []
            self._event_callbacks[event_type].append(callback)

    def unsubscribe_event(self, event_type: str, callback: callable) -> None:
        """Unsubscribe from OBS event."""
        with self._event_lock:
            if event_type in self._event_callbacks:
                try:
                    self._event_callbacks[event_type].remove(callback)
                except ValueError:
                    pass

    # ========================================================================
    # WebSocket Callbacks
    # ========================================================================

    def _on_open(self, ws):
        """Handle WebSocket connection opened."""
        self.logger.debug("OBS WebSocket connection opened")

    def _on_message(self, ws, message: str):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            op = data.get("op")

            if op == 0:  # Hello
                self._handle_hello(data.get("d", {}))
            elif op == 2:  # Identified
                self._handle_identified(data.get("d", {}))
            elif op == 5:  # Event
                self._handle_event(data.get("d", {}))
            elif op == 7:  # RequestResponse
                self._handle_request_response(data.get("d", {}))
            else:
                self.logger.warning(f"Unknown OBS opcode: {op}")

        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON from OBS: {message}")
        except Exception as e:
            self.logger.exception(f"Error handling OBS message: {e}")

    def _on_error(self, ws, error):
        """Handle WebSocket error."""
        self.logger.error(f"OBS WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection closed."""
        self.logger.info(f"OBS WebSocket closed: {close_status_code} - {close_msg}")
        self.connected = False
        self.authenticated = False
        self._disconnect_event.set()

    # ========================================================================
    # OBS Protocol Handlers
    # ========================================================================

    def _handle_hello(self, data: Dict[str, Any]) -> None:
        """
        Handle Hello message (opcode 0).
        Authenticate if password required.
        """
        self.logger.debug(f"Received Hello from OBS: {data}")

        auth_info = data.get("authentication")

        if auth_info:
            # Authentication required
            if not self.password:
                self.logger.error("OBS requires authentication but no password provided")
                self.ws.close()
                return

            challenge = auth_info.get("challenge")
            salt = auth_info.get("salt")

            # Generate authentication string
            # auth = base64(sha256(base64(sha256(password + salt)) + challenge))
            secret = base64.b64encode(
                hashlib.sha256((self.password + salt).encode()).digest()
            ).decode()
            auth = base64.b64encode(
                hashlib.sha256((secret + challenge).encode()).digest()
            ).decode()

            # Send Identify message with authentication
            identify = {
                "op": 1,  # Identify opcode
                "d": {
                    "rpcVersion": 1,
                    "authentication": auth,
                    "eventSubscriptions": 33  # Subscribe to all events (bitmask)
                }
            }
        else:
            # No authentication required
            identify = {
                "op": 1,  # Identify opcode
                "d": {
                    "rpcVersion": 1,
                    "eventSubscriptions": 33  # Subscribe to all events
                }
            }

        self.ws.send(json.dumps(identify))
        self.logger.debug("Sent Identify message to OBS")

    def _handle_identified(self, data: Dict[str, Any]) -> None:
        """
        Handle Identified message (opcode 2).
        Connection authenticated successfully.
        """
        self.logger.info(f"Authenticated with OBS: {data}")
        self.connected = True
        self.authenticated = True
        self._connect_event.set()

    def _handle_event(self, data: Dict[str, Any]) -> None:
        """
        Handle Event message (opcode 5).
        Dispatch to registered callbacks.
        """
        event_type = data.get("eventType")
        event_data = data.get("eventData", {})

        self.logger.debug(f"Received OBS event: {event_type}")

        # Dispatch to callbacks
        with self._event_lock:
            callbacks = self._event_callbacks.get(event_type, []).copy()

        for callback in callbacks:
            try:
                callback(event_data)
            except Exception as e:
                self.logger.exception(f"Error in event callback for {event_type}: {e}")

    def _handle_request_response(self, data: Dict[str, Any]) -> None:
        """
        Handle RequestResponse message (opcode 7).
        Match to pending request and deliver response.
        """
        request_id = data.get("requestId")

        with self._request_lock:
            response_queue = self._pending_requests.get(request_id)

        if response_queue:
            response_queue.put(data)
        else:
            self.logger.warning(f"Received response for unknown request: {request_id}")


# ============================================================================
# OBS Adapter
# ============================================================================

class OBSAdapter(ProductionAdapterBase):
    """
    OBS Studio Production Adapter.

    Implements IF.bus integration for OBS Studio via obs-websocket v5.x protocol.

    Features:
    - Auto-discovery via network port scanning
    - WebSocket-based communication
    - Real-time event subscriptions
    - Thread-safe instance management
    - Comprehensive error handling and retry logic
    """

    adapter_type = "obs"
    SUPPORTED_VERSIONS = {
        "obs_websocket": ["5.0.0", "5.0.1", "5.1.0", "5.2.0", "5.3.0"],
        "obs_studio": ["28.0.0", "29.0.0", "30.0.0"]
    }

    def __init__(
        self,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None,
        event_emitter=None,
        metrics_collector=None,
    ):
        """
        Initialize OBS adapter.

        Args:
            config: Configuration dictionary
            logger: Optional logger instance
            event_emitter: Optional event emitter
            metrics_collector: Optional metrics collector
        """
        super().__init__(config, logger, event_emitter, metrics_collector)

        # OBS-specific state
        self._clients: Dict[str, OBSWebSocketClient] = {}
        self._instance_metadata: Dict[str, Dict[str, Any]] = {}
        self._client_lock = threading.Lock()

        self.logger.info(f"OBS Adapter initialized: {self.adapter_type}")

    # ========================================================================
    # Abstract Method Implementations
    # ========================================================================

    def discover_instances(
        self,
        network_config: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Discover OBS instances on network via port scanning.

        Args:
            network_config: {
                "network": "192.168.1.0/24",  # CIDR notation
                "hosts": ["192.168.1.100", "192.168.1.101"],  # Explicit hosts
                "port": 4455,  # Override default port
                "timeout": 2.0  # Scan timeout per host
            }

        Returns:
            List of discovered instance identifiers

        Raises:
            DiscoveryError: If discovery fails
        """
        self.logger.info("Starting OBS instance discovery")

        network_config = network_config or {}
        port = network_config.get("port", OBS_DEFAULT_PORT)
        timeout = network_config.get("timeout", OBS_DISCOVERY_TIMEOUT)

        # Determine hosts to scan
        hosts = []

        if "hosts" in network_config:
            hosts = network_config["hosts"]
        elif "network" in network_config:
            # Parse CIDR and generate host list
            hosts = self._parse_cidr(network_config["network"])
        else:
            # Default: scan local network
            hosts = self._get_local_network_hosts()

        discovered = []

        for host in hosts:
            try:
                # Try to connect to port
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                sock.close()

                if result == 0:
                    # Port is open, verify it's OBS
                    if self._verify_obs_instance(host, port):
                        instance_id = f"obs://{host}:{port}"
                        discovered.append(instance_id)
                        self.logger.info(f"Discovered OBS instance: {instance_id}")

            except Exception as e:
                self.logger.debug(f"Error scanning {host}:{port}: {e}")
                continue

        self.logger.info(f"Discovery complete: found {len(discovered)} OBS instances")

        # Emit discovery event
        current_names = list(self._instances.keys())
        new_instances = [d for d in discovered if d not in current_names]
        removed_instances = [c for c in current_names if c not in discovered]

        self.emit_discovery(
            instance_count=len(discovered),
            new_instances=new_instances,
            removed_instances=removed_instances
        )

        return discovered

    def add_instance(self, name: str, config: Dict[str, Any]) -> str:
        """
        Add OBS instance to registry.

        Args:
            name: Friendly instance name
            config: {
                "host": "192.168.1.100",
                "port": 4455,
                "password": "secret123",  # Optional
                "auto_reconnect": True,  # Optional
                "timeout": 30.0  # Optional
            }

        Returns:
            instance_id: Unique instance identifier

        Raises:
            ConfigurationError: If config invalid
            InstanceError: If instance cannot be added
        """
        self.logger.info(f"Adding OBS instance: {name}")

        # Validate config
        if "host" not in config:
            raise ConfigurationError("Missing required field: host")

        host = config["host"]
        port = config.get("port", OBS_DEFAULT_PORT)
        password = config.get("password")
        timeout = config.get("timeout", OBS_CONNECTION_TIMEOUT)

        # Generate instance ID
        instance_id = self.generate_instance_id()

        # Create WebSocket client
        try:
            client = OBSWebSocketClient(
                host=host,
                port=port,
                password=password,
                logger=self.logger
            )

            # Connect to OBS
            start_time = time.time()
            client.connect(timeout=timeout)
            duration_ms = (time.time() - start_time) * 1000

            # Get OBS version info
            version_info = client.send_request(OBSRequestType.GET_VERSION)

            # Store client and metadata
            with self._client_lock:
                self._clients[name] = client
                self._instance_metadata[name] = {
                    "instance_id": instance_id,
                    "name": name,
                    "host": host,
                    "port": port,
                    "version": version_info,
                    "created_at": time.time(),
                    "connection_count": 1,
                    "command_count": 0,
                    "error_count": 0,
                }

            # Register instance
            instance_data = {
                "instance_id": instance_id,
                "name": name,
                "config": config,
                "client": client,
                "metadata": self._instance_metadata[name],
            }
            self._add_instance(instance_id, instance_data)

            # Subscribe to key events
            self._subscribe_instance_events(name, client)

            # Update state
            self._update_instance_state(instance_id, InstanceState.CONNECTED)

            self.logger.info(
                f"Added OBS instance '{name}' at {host}:{port} "
                f"(version: {version_info.get('obsVersion', 'unknown')}, "
                f"connect_time: {duration_ms:.1f}ms)"
            )

            # Emit state change event
            self.emit_instance_state_changed(
                instance_name=name,
                instance_id=instance_id,
                state=InstanceState.CONNECTED,
                details={"version": version_info, "duration_ms": duration_ms}
            )

            # Update metrics
            self.metrics.record_command(success=True, duration_ms=duration_ms)
            self._update_metrics()

            return instance_id

        except Exception as e:
            self.logger.exception(f"Failed to add OBS instance '{name}': {e}")

            # Clean up on failure
            with self._client_lock:
                if name in self._clients:
                    try:
                        self._clients[name].disconnect()
                    except:
                        pass
                    del self._clients[name]
                self._instance_metadata.pop(name, None)

            self.metrics.record_command(success=False)

            raise InstanceError(
                f"Failed to add OBS instance '{name}': {e}",
                retryable=True
            )

    def remove_instance(self, name: str) -> bool:
        """
        Remove OBS instance from registry.

        Args:
            name: Instance name to remove

        Returns:
            True if successful

        Raises:
            InstanceError: If instance not found or removal fails
        """
        self.logger.info(f"Removing OBS instance: {name}")

        with self._client_lock:
            if name not in self._clients:
                raise InstanceError(f"Instance not found: {name}")

            client = self._clients[name]
            metadata = self._instance_metadata.get(name, {})
            instance_id = metadata.get("instance_id")

            # Disconnect client
            try:
                client.disconnect()
            except Exception as e:
                self.logger.warning(f"Error disconnecting OBS instance '{name}': {e}")

            # Remove from registries
            del self._clients[name]
            self._instance_metadata.pop(name, None)

            if instance_id:
                self._remove_instance(instance_id)

                # Emit state change
                self.emit_instance_state_changed(
                    instance_name=name,
                    instance_id=instance_id,
                    state=InstanceState.DISCONNECTED,
                    details={"reason": "removed"}
                )

        self.logger.info(f"Removed OBS instance: {name}")
        self._update_metrics()

        return True

    def get_instance_status(self, name: str) -> Dict[str, Any]:
        """
        Get OBS instance health/status.

        Args:
            name: Instance name

        Returns:
            Status dictionary with OBS-specific details

        Raises:
            InstanceError: If instance not found
        """
        with self._client_lock:
            if name not in self._clients:
                raise InstanceError(f"Instance not found: {name}")

            client = self._clients[name]
            metadata = self._instance_metadata[name]

        instance_id = metadata["instance_id"]

        try:
            # Query OBS status
            version = client.send_request(OBSRequestType.GET_VERSION)
            stats = client.send_request(OBSRequestType.GET_STATS)
            stream_status = client.send_request(OBSRequestType.GET_STREAM_STATUS)
            record_status = client.send_request(OBSRequestType.GET_RECORD_STATUS)

            uptime = time.time() - metadata["created_at"]

            return {
                "instance_id": instance_id,
                "name": name,
                "state": InstanceState.CONNECTED.value,
                "connected": client.connected and client.authenticated,
                "last_seen": datetime.now().isoformat(),
                "uptime_seconds": uptime,
                "command_count": metadata["command_count"],
                "error_count": metadata["error_count"],
                "details": {
                    "obs_version": version.get("obsVersion"),
                    "obs_websocket_version": version.get("obsWebSocketVersion"),
                    "platform": version.get("platform"),
                    "platform_description": version.get("platformDescription"),
                    "streaming": stream_status.get("outputActive", False),
                    "recording": record_status.get("outputActive", False),
                    "fps": stats.get("activeFps"),
                    "cpu_usage": stats.get("cpuUsage"),
                    "memory_usage_mb": stats.get("memoryUsage"),
                    "render_total_frames": stats.get("renderTotalFrames"),
                    "render_skipped_frames": stats.get("renderSkippedFrames"),
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting status for instance '{name}': {e}")

            return {
                "instance_id": instance_id,
                "name": name,
                "state": InstanceState.ERROR.value,
                "connected": False,
                "last_seen": datetime.now().isoformat(),
                "uptime_seconds": time.time() - metadata["created_at"],
                "command_count": metadata["command_count"],
                "error_count": metadata["error_count"],
                "details": {"error": str(e)}
            }

    def execute_command(
        self,
        name: str,
        command: str,
        command_type: CommandType = CommandType.CUSTOM,
        **params
    ) -> Dict[str, Any]:
        """
        Execute command on OBS instance.

        Args:
            name: Instance name
            command: OBS request type (e.g., "GetSceneList", "StartStream")
            command_type: Command classification
            params: Command-specific parameters

        Returns:
            Command result dictionary

        Raises:
            CommandExecutionError: If command fails
            InstanceError: If instance not found
            TimeoutError: If command times out
        """
        with self._client_lock:
            if name not in self._clients:
                raise InstanceError(f"Instance not found: {name}")

            client = self._clients[name]
            metadata = self._instance_metadata[name]

        self.logger.info(f"Executing OBS command '{command}' on instance '{name}'")

        start_time = time.time()
        success = False
        result = {}
        error = None

        try:
            # Execute request
            timeout = params.pop("timeout", OBS_REQUEST_TIMEOUT)
            result = client.send_request(command, params, timeout=timeout)

            success = True
            duration_ms = (time.time() - start_time) * 1000

            # Update metadata
            with self._client_lock:
                metadata["command_count"] += 1

            self.logger.info(
                f"Command '{command}' completed on '{name}' "
                f"({duration_ms:.1f}ms)"
            )

            # Record metrics
            self.metrics.record_command(success=True, duration_ms=duration_ms)

            # Emit event
            self.emit_command_execution(
                instance_name=name,
                command=command,
                command_type=command_type,
                success=True,
                duration_ms=duration_ms,
                result=result
            )

            return {
                "success": True,
                "result": result,
                "duration_ms": duration_ms
            }

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error = str(e)

            # Update metadata
            with self._client_lock:
                metadata["command_count"] += 1
                metadata["error_count"] += 1

            self.logger.error(
                f"Command '{command}' failed on '{name}': {error} "
                f"({duration_ms:.1f}ms)"
            )

            # Record metrics
            self.metrics.record_command(success=False, duration_ms=duration_ms)

            # Emit event
            self.emit_command_execution(
                instance_name=name,
                command=command,
                command_type=command_type,
                success=False,
                duration_ms=duration_ms,
                error=error
            )

            # Re-raise appropriate exception type
            if isinstance(e, (CommandExecutionError, TimeoutError)):
                raise
            else:
                raise CommandExecutionError(
                    f"OBS command '{command}' failed: {error}",
                    retryable=True
                )

    def health_check(self) -> Dict[str, Any]:
        """
        Return comprehensive health metrics for OBS adapter.

        Returns:
            Health status dictionary
        """
        metrics = self.metrics.get_metrics()

        # Count instance states
        total_instances = 0
        connected_instances = 0
        error_instances = 0

        with self._client_lock:
            total_instances = len(self._clients)
            for name, client in self._clients.items():
                if client.connected and client.authenticated:
                    connected_instances += 1
                else:
                    error_instances += 1

        # Determine overall health status
        if connected_instances == total_instances and total_instances > 0:
            status = HealthStatus.HEALTHY
        elif connected_instances > 0:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.CRITICAL

        return {
            "adapter": self.adapter_type,
            "connected": self.is_connected(),
            "uptime_seconds": metrics["uptime_seconds"],
            "instances": {
                "total": total_instances,
                "connected": connected_instances,
                "errors": error_instances
            },
            "metrics": {
                "command_attempts": metrics["command_attempts"],
                "command_success_rate": metrics["command_success_rate"],
                "failed_commands": metrics["failed_commands"],
                "avg_command_duration_ms": metrics["avg_command_duration_ms"],
                "connection_failures": metrics["connection_failures"],
                "last_error": metrics["last_error"],
            },
            "latency": metrics["latency"],
            "last_check": datetime.now().isoformat(),
            "status": status.value
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate OBS adapter configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if valid

        Raises:
            ConfigurationError: If validation fails
        """
        # Check required fields
        if "type" not in config:
            raise ConfigurationError("Missing required field: type")

        if config["type"].lower() != "obs":
            raise ConfigurationError(f"Invalid adapter type: {config['type']}")

        # Validate optional fields
        if "port" in config:
            port = config["port"]
            if not isinstance(port, int) or port < 1 or port > 65535:
                raise ConfigurationError(f"Invalid port number: {port}")

        if "timeout" in config:
            timeout = config["timeout"]
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                raise ConfigurationError(f"Invalid timeout: {timeout}")

        return True

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _verify_obs_instance(self, host: str, port: int) -> bool:
        """
        Verify that the service at host:port is actually OBS.

        Args:
            host: Host address
            port: Port number

        Returns:
            True if OBS WebSocket detected
        """
        try:
            client = OBSWebSocketClient(host=host, port=port, logger=self.logger)
            client.connect(timeout=OBS_DISCOVERY_TIMEOUT)

            # Try to get version - confirms it's OBS
            version = client.send_request(OBSRequestType.GET_VERSION, timeout=2.0)
            client.disconnect()

            return "obsVersion" in version

        except Exception as e:
            self.logger.debug(f"Not OBS at {host}:{port}: {e}")
            return False

    def _subscribe_instance_events(
        self,
        name: str,
        client: OBSWebSocketClient
    ) -> None:
        """
        Subscribe to OBS events for instance.

        Args:
            name: Instance name
            client: WebSocket client
        """
        # Subscribe to state change events
        def on_scene_changed(event_data):
            self.logger.info(f"OBS instance '{name}' scene changed: {event_data}")

        def on_stream_state_changed(event_data):
            self.logger.info(f"OBS instance '{name}' stream state: {event_data}")

        def on_record_state_changed(event_data):
            self.logger.info(f"OBS instance '{name}' record state: {event_data}")

        client.subscribe_event(
            OBSEventType.CURRENT_PROGRAM_SCENE_CHANGED,
            on_scene_changed
        )
        client.subscribe_event(
            OBSEventType.STREAM_STATE_CHANGED,
            on_stream_state_changed
        )
        client.subscribe_event(
            OBSEventType.RECORD_STATE_CHANGED,
            on_record_state_changed
        )

    def _parse_cidr(self, cidr: str) -> List[str]:
        """
        Parse CIDR notation into list of host addresses.

        Args:
            cidr: CIDR notation (e.g., "192.168.1.0/24")

        Returns:
            List of IP addresses
        """
        # Simple implementation for /24 networks
        # For production, use ipaddress module
        if not cidr.endswith("/24"):
            self.logger.warning(f"Only /24 networks supported, got: {cidr}")
            return []

        base = cidr.split("/")[0]
        parts = base.split(".")
        network = ".".join(parts[:3])

        # Scan typical range (skip .0 and .255)
        return [f"{network}.{i}" for i in range(1, 255)]

    def _get_local_network_hosts(self) -> List[str]:
        """
        Get list of hosts on local network.

        Returns:
            List of IP addresses to scan
        """
        # Get local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()

            # Assume /24 network
            parts = local_ip.split(".")
            network = ".".join(parts[:3])

            return [f"{network}.{i}" for i in range(1, 255)]

        except Exception as e:
            self.logger.warning(f"Could not determine local network: {e}")
            return ["localhost", "127.0.0.1"]

    def _update_metrics(self) -> None:
        """Update adapter metrics."""
        with self._client_lock:
            total = len(self._clients)
            connected = sum(
                1 for c in self._clients.values()
                if c.connected and c.authenticated
            )
            errors = total - connected

        self.metrics.update_instance_count(total, connected, errors)


# ============================================================================
# Convenience Functions
# ============================================================================

def create_obs_adapter(
    host: str = "localhost",
    port: int = OBS_DEFAULT_PORT,
    password: Optional[str] = None,
    logger: Optional[logging.Logger] = None
) -> OBSAdapter:
    """
    Create OBS adapter with simple configuration.

    Args:
        host: OBS host address
        port: OBS WebSocket port
        password: OBS WebSocket password (if required)
        logger: Optional logger instance

    Returns:
        Configured OBS adapter
    """
    config = {
        "type": "obs",
        "host": host,
        "port": port,
        "password": password
    }

    return OBSAdapter(config, logger=logger)


# ============================================================================
# Main (Testing)
# ============================================================================

if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger("OBSAdapter")

    # Create adapter
    config = {
        "type": "obs",
        "timeout": 30,
    }

    adapter = OBSAdapter(config, logger=logger)

    print("=" * 80)
    print("OBS Adapter Example Usage")
    print("=" * 80)

    # Add instance
    try:
        print("\n1. Adding OBS instance...")
        instance_id = adapter.add_instance(
            name="main_obs",
            config={
                "host": "localhost",
                "port": 4455,
                "password": None,  # Set if OBS requires auth
            }
        )
        print(f"   Instance added: {instance_id}")

        # Get status
        print("\n2. Getting instance status...")
        status = adapter.get_instance_status("main_obs")
        print(f"   Status: {json.dumps(status, indent=2)}")

        # Execute commands
        print("\n3. Executing OBS commands...")

        # Get scene list
        result = adapter.execute_command(
            "main_obs",
            OBSRequestType.GET_SCENE_LIST
        )
        print(f"   Scene list: {json.dumps(result, indent=2)}")

        # Get current scene
        result = adapter.execute_command(
            "main_obs",
            OBSRequestType.GET_CURRENT_PROGRAM_SCENE
        )
        print(f"   Current scene: {json.dumps(result, indent=2)}")

        # Get stream status
        result = adapter.execute_command(
            "main_obs",
            OBSRequestType.GET_STREAM_STATUS
        )
        print(f"   Stream status: {json.dumps(result, indent=2)}")

        # Health check
        print("\n4. Health check...")
        health = adapter.health_check()
        print(f"   Health: {json.dumps(health, indent=2)}")

        # Remove instance
        print("\n5. Removing instance...")
        adapter.remove_instance("main_obs")
        print("   Instance removed")

    except Exception as e:
        logger.exception(f"Error in example: {e}")

    print("\n" + "=" * 80)
    print("Example complete")
    print("=" * 80)
