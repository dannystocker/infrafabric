"""
vMix Production Infrastructure Adapter - IF.bus Implementation

This module provides the vMix adapter for IF.bus production infrastructure control.
vMix is a live video production software with TCP and HTTP REST API support.

Protocol: IF.TTT (Traceable/Transparent/Trustworthy) compliance
Philosophy: Confucian Wu Lun (五伦) relationship mapping for instance hierarchy
Logging: IF.witness integration for comprehensive audit trails
Metrics: IF.optimise integration for performance optimization

Author: Agent 8 (IF.bus architecture)
Version: 1.0.0
Date: 2025-11-12
"""

import socket
import time
import threading
import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin
import requests

from .production_adapter_base import (
    ProductionAdapterBase,
    InstanceState,
    AdapterConnectionState,
    HealthStatus,
    ErrorSeverity,
    CommandType,
    ConfigurationError,
    ConnectionError,
    InstanceError,
    CommandExecutionError,
    TimeoutError,
    DiscoveryError,
)

# Try to import zeroconf for mDNS discovery
try:
    from zeroconf import Zeroconf, ServiceBrowser, ServiceListener
    ZEROCONF_AVAILABLE = True
except ImportError:
    ZEROCONF_AVAILABLE = False


class VMixServiceListener(ServiceListener):
    """
    mDNS service listener for vMix instance discovery.
    Implements zeroconf ServiceListener interface.
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.discovered_services: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def add_service(self, zeroconf: Zeroconf, service_type: str, name: str) -> None:
        """Called when a vMix service is discovered."""
        info = zeroconf.get_service_info(service_type, name)
        if info:
            with self._lock:
                addresses = [socket.inet_ntoa(addr) for addr in info.addresses]
                self.discovered_services[name] = {
                    "name": name,
                    "addresses": addresses,
                    "port": info.port,
                    "properties": info.properties,
                    "server": info.server,
                }
                self.logger.info(f"Discovered vMix instance: {name} at {addresses}:{info.port}")

    def remove_service(self, zeroconf: Zeroconf, service_type: str, name: str) -> None:
        """Called when a vMix service disappears."""
        with self._lock:
            if name in self.discovered_services:
                del self.discovered_services[name]
                self.logger.info(f"vMix instance removed: {name}")

    def update_service(self, zeroconf: Zeroconf, service_type: str, name: str) -> None:
        """Called when service info is updated."""
        self.add_service(zeroconf, service_type, name)

    def get_discovered_services(self) -> Dict[str, Dict[str, Any]]:
        """Thread-safe retrieval of discovered services."""
        with self._lock:
            return self.discovered_services.copy()


class VMixAdapter(ProductionAdapterBase):
    """
    vMix Production Infrastructure Adapter.

    Supports:
    - TCP command interface (port 8099)
    - HTTP REST API (port 8088)
    - mDNS discovery (_vmix._tcp.local)
    - Real-time status monitoring
    - Full command execution (recording, streaming, transitions, etc.)

    Thread Safety: All public methods are thread-safe.
    """

    adapter_type = "vmix"
    SUPPORTED_VERSIONS = {
        "vmix": ["24", "25", "26", "27"],  # vMix versions
    }

    # Default configuration
    DEFAULT_TCP_PORT = 8099
    DEFAULT_HTTP_PORT = 8088
    DEFAULT_TIMEOUT = 10
    MDNS_SERVICE_TYPE = "_vmix._tcp.local."

    # vMix command mappings
    VMIX_COMMANDS = {
        # Text commands
        "SetText": {"required": ["Input", "Value"]},
        "SetImageFromFile": {"required": ["Input", "Value"]},

        # Camera control
        "SetPanX": {"required": ["Input", "Value"]},
        "SetPanY": {"required": ["Input", "Value"]},
        "SetZoom": {"required": ["Input", "Value"]},

        # Switching/transitions
        "Cut": {"required": ["Input"]},
        "Fade": {"required": ["Duration"]},
        "Transition": {"required": ["Duration", "Mix"]},
        "PreviewInput": {"required": ["Input"]},
        "ActiveInput": {"required": ["Input"]},

        # Overlays
        "OverlayInput1": {"required": ["Input"]},
        "OverlayInput1On": {"required": []},
        "OverlayInput1Off": {"required": []},
        "OverlayInput2": {"required": ["Input"]},
        "OverlayInput2On": {"required": []},
        "OverlayInput2Off": {"required": []},

        # Recording/streaming
        "StartRecording": {"required": []},
        "StopRecording": {"required": []},
        "StartStreaming": {"required": []},
        "StopStreaming": {"required": []},
        "StartMultiCorder": {"required": []},
        "StopMultiCorder": {"required": []},

        # Audio
        "SetVolume": {"required": ["Input", "Value"]},
        "AudioOn": {"required": ["Input"]},
        "AudioOff": {"required": ["Input"]},

        # Playback
        "Play": {"required": ["Input"]},
        "Pause": {"required": ["Input"]},
        "Stop": {"required": ["Input"]},
    }

    def __init__(
        self,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None,
        event_emitter: Optional[Any] = None,
        metrics_collector: Optional[Any] = None,
    ):
        """
        Initialize vMix adapter.

        Args:
            config: Configuration dictionary
            logger: Optional logger instance
            event_emitter: Optional event emitter
            metrics_collector: Optional metrics collector
        """
        super().__init__(config, logger, event_emitter, metrics_collector)

        # vMix-specific state
        self._tcp_connections: Dict[str, socket.socket] = {}
        self._instance_configs: Dict[str, Dict[str, Any]] = {}
        self._instance_health: Dict[str, Dict[str, Any]] = {}
        self._last_status_check: Dict[str, float] = {}

        # Discovery state
        self._zeroconf: Optional[Zeroconf] = None
        self._service_listener: Optional[VMixServiceListener] = None

        self.logger.info(f"Initialized vMix adapter (type={self.adapter_type})")

    # ========================================================================
    # Abstract Method Implementations
    # ========================================================================

    def discover_instances(self, network_config: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Auto-discover vMix instances on network using mDNS and port scanning.

        Args:
            network_config: Optional network discovery configuration
                {
                    "timeout": 5,  # Discovery timeout in seconds
                    "scan_ports": [8088, 8099],  # Ports to scan
                    "scan_subnet": "192.168.1.0/24",  # Optional subnet
                }

        Returns:
            List of discovered instance names

        Raises:
            DiscoveryError: If discovery fails
        """
        self.logger.info("Starting vMix instance discovery")
        discovered_names = []

        try:
            # Method 1: mDNS discovery (preferred)
            if ZEROCONF_AVAILABLE:
                discovered_names.extend(self._discover_via_mdns(network_config))
            else:
                self.logger.warning("Zeroconf not available, skipping mDNS discovery")

            # Method 2: Port scanning (fallback)
            if network_config and network_config.get("scan_subnet"):
                discovered_names.extend(self._discover_via_port_scan(network_config))

            # Emit discovery event
            self.emit_discovery(
                instance_count=len(discovered_names),
                new_instances=discovered_names,
                removed_instances=[],
                details={"method": "mdns+port_scan"}
            )

            self.logger.info(f"Discovered {len(discovered_names)} vMix instances")
            return discovered_names

        except Exception as e:
            self.logger.exception(f"Discovery failed: {e}")
            raise DiscoveryError(f"Failed to discover vMix instances: {e}")

    def _discover_via_mdns(self, network_config: Optional[Dict[str, Any]] = None) -> List[str]:
        """Discover vMix instances via mDNS."""
        timeout = (network_config or {}).get("timeout", 5)
        discovered = []

        try:
            self._zeroconf = Zeroconf()
            self._service_listener = VMixServiceListener(self.logger)

            browser = ServiceBrowser(
                self._zeroconf,
                self.MDNS_SERVICE_TYPE,
                self._service_listener
            )

            # Wait for discovery
            time.sleep(timeout)

            # Process discovered services
            services = self._service_listener.get_discovered_services()
            for service_name, service_info in services.items():
                if service_info["addresses"]:
                    instance_name = service_name.replace(f".{self.MDNS_SERVICE_TYPE}", "")

                    # Auto-add discovered instance
                    config = {
                        "host": service_info["addresses"][0],
                        "tcp_port": self.DEFAULT_TCP_PORT,
                        "http_port": service_info.get("port", self.DEFAULT_HTTP_PORT),
                        "discovered": True,
                    }

                    try:
                        self.add_instance(instance_name, config)
                        discovered.append(instance_name)
                    except Exception as e:
                        self.logger.error(f"Failed to add discovered instance {instance_name}: {e}")

            browser.cancel()

        except Exception as e:
            self.logger.error(f"mDNS discovery failed: {e}")
        finally:
            if self._zeroconf:
                self._zeroconf.close()
                self._zeroconf = None

        return discovered

    def _discover_via_port_scan(self, network_config: Dict[str, Any]) -> List[str]:
        """Discover vMix instances via port scanning."""
        # Placeholder for port scanning implementation
        # In production, this would scan the specified subnet
        self.logger.info("Port scanning not yet implemented")
        return []

    def add_instance(self, name: str, config: Dict[str, Any]) -> str:
        """
        Add vMix instance to registry.

        Args:
            name: Friendly instance name
            config: Instance configuration
                {
                    "host": "192.168.1.100",  # Required
                    "tcp_port": 8099,  # Optional, default 8099
                    "http_port": 8088,  # Optional, default 8088
                    "api_key": "secret",  # Optional
                    "timeout": 10,  # Optional
                }

        Returns:
            instance_id: Unique instance identifier

        Raises:
            ConfigurationError: If config invalid
            InstanceError: If instance cannot be added
        """
        self.logger.info(f"Adding vMix instance: {name}")

        # Validate config
        if not config.get("host"):
            raise ConfigurationError("Missing required field: host")

        # Set defaults
        config.setdefault("tcp_port", self.DEFAULT_TCP_PORT)
        config.setdefault("http_port", self.DEFAULT_HTTP_PORT)
        config.setdefault("timeout", self.DEFAULT_TIMEOUT)

        # Generate instance ID
        instance_id = self.generate_instance_id()

        # Create instance data
        instance_data = {
            "instance_id": instance_id,
            "name": name,
            "config": config,
            "created_at": time.time(),
            "command_count": 0,
            "error_count": 0,
        }

        # Store instance
        with self._lock:
            self._add_instance(instance_id, instance_data)
            self._instance_configs[name] = config
            self._instance_health[name] = {
                "state": InstanceState.CREATED,
                "last_seen": time.time(),
                "uptime_seconds": 0,
            }

        # Test connection
        try:
            self._test_instance_connection(name, config)
            self._update_instance_state(instance_id, InstanceState.CONNECTED)

            self.emit_instance_state_changed(
                instance_name=name,
                instance_id=instance_id,
                state=InstanceState.CONNECTED,
                details={"host": config["host"]}
            )

        except Exception as e:
            self.logger.warning(f"Instance added but connection test failed: {e}")
            self._update_instance_state(instance_id, InstanceState.ERROR)

            self.emit_instance_state_changed(
                instance_name=name,
                instance_id=instance_id,
                state=InstanceState.ERROR,
                details={"error": str(e)}
            )

        self.logger.info(f"Added vMix instance {name} with ID {instance_id}")
        return instance_id

    def _test_instance_connection(self, name: str, config: Dict[str, Any]) -> bool:
        """Test connection to vMix instance."""
        try:
            # Test HTTP API
            url = f"http://{config['host']}:{config['http_port']}/api"
            response = requests.get(url, timeout=config.get("timeout", 5))
            response.raise_for_status()

            # Test TCP connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(config.get("timeout", 5))
            sock.connect((config["host"], config["tcp_port"]))
            sock.close()

            return True

        except Exception as e:
            raise ConnectionError(f"Connection test failed: {e}")

    def remove_instance(self, name: str) -> bool:
        """
        Remove vMix instance from registry.

        Args:
            name: Instance name to remove

        Returns:
            True if successful

        Raises:
            InstanceError: If instance not found
        """
        self.logger.info(f"Removing vMix instance: {name}")

        with self._lock:
            if name not in self._instance_configs:
                raise InstanceError(f"Instance not found: {name}")

            # Find instance ID
            instance_id = None
            for iid, idata in self._instances.items():
                if idata.get("name") == name:
                    instance_id = iid
                    break

            if not instance_id:
                raise InstanceError(f"Instance ID not found for: {name}")

            # Close TCP connection if exists
            if name in self._tcp_connections:
                try:
                    self._tcp_connections[name].close()
                except Exception:
                    pass
                del self._tcp_connections[name]

            # Remove from registries
            self._remove_instance(instance_id)
            del self._instance_configs[name]
            del self._instance_health[name]
            if name in self._last_status_check:
                del self._last_status_check[name]

        self.emit_instance_state_changed(
            instance_name=name,
            instance_id=instance_id,
            state=InstanceState.DISCONNECTED,
            details={"reason": "removed"}
        )

        self.logger.info(f"Removed vMix instance: {name}")
        return True

    def get_instance_status(self, name: str) -> Dict[str, Any]:
        """
        Get vMix instance health/status by querying /api XML endpoint.

        Args:
            name: Instance name

        Returns:
            Status dictionary with instance details

        Raises:
            InstanceError: If instance not found
        """
        with self._lock:
            if name not in self._instance_configs:
                raise InstanceError(f"Instance not found: {name}")

            config = self._instance_configs[name]

            # Find instance data
            instance_id = None
            instance_data = None
            for iid, idata in self._instances.items():
                if idata.get("name") == name:
                    instance_id = iid
                    instance_data = idata
                    break

        if not instance_id or not instance_data:
            raise InstanceError(f"Instance data not found: {name}")

        # Query vMix API
        try:
            url = f"http://{config['host']}:{config['http_port']}/api"
            response = requests.get(url, timeout=config.get("timeout", 5))
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            # Extract status information
            version = root.get("version", "unknown")
            edition = root.get("edition", "unknown")
            recording = root.findtext("recording", "False") == "True"
            streaming = root.findtext("streaming", "False") == "True"

            inputs = []
            for input_elem in root.findall("input"):
                inputs.append({
                    "key": input_elem.get("key"),
                    "number": input_elem.get("number"),
                    "type": input_elem.get("type"),
                    "title": input_elem.get("title"),
                    "state": input_elem.get("state"),
                })

            # Update health tracking
            with self._lock:
                self._instance_health[name] = {
                    "state": InstanceState.CONNECTED,
                    "last_seen": time.time(),
                    "uptime_seconds": time.time() - instance_data.get("created_at", time.time()),
                }
                self._last_status_check[name] = time.time()

            status = {
                "instance_id": instance_id,
                "name": name,
                "state": InstanceState.CONNECTED.value,
                "connected": True,
                "last_seen": time.time(),
                "uptime_seconds": time.time() - instance_data.get("created_at", time.time()),
                "command_count": instance_data.get("command_count", 0),
                "error_count": instance_data.get("error_count", 0),
                "details": {
                    "version": version,
                    "edition": edition,
                    "recording": recording,
                    "streaming": streaming,
                    "input_count": len(inputs),
                    "inputs": inputs[:5],  # First 5 inputs
                }
            }

            return status

        except Exception as e:
            self.logger.error(f"Failed to get status for {name}: {e}")

            # Update error state
            with self._lock:
                if name in self._instance_health:
                    self._instance_health[name]["state"] = InstanceState.ERROR

            raise InstanceError(f"Failed to get instance status: {e}")

    def execute_command(
        self,
        name: str,
        command: str,
        command_type: CommandType = CommandType.CUSTOM,
        **params
    ) -> Dict[str, Any]:
        """
        Execute vMix FUNCTION command via TCP interface.

        Args:
            name: Instance name
            command: vMix function name (e.g., "Cut", "Fade", "SetText")
            command_type: Type of command
            params: Command parameters (e.g., Input="1", Value="Hello")

        Returns:
            Command execution result

        Raises:
            CommandExecutionError: If command fails
            InstanceError: If instance not found
            TimeoutError: If command times out
        """
        start_time = time.time()

        with self._lock:
            if name not in self._instance_configs:
                raise InstanceError(f"Instance not found: {name}")
            config = self._instance_configs[name]

        self.logger.info(f"Executing command on {name}: {command} {params}")

        try:
            # Build vMix command string
            # Format: FUNCTION FunctionName Input=value Parameter=value
            cmd_parts = ["FUNCTION", command]

            for key, value in params.items():
                # Capitalize first letter to match vMix convention
                param_name = key[0].upper() + key[1:] if key else key
                cmd_parts.append(f"{param_name}={value}")

            command_str = " ".join(cmd_parts)

            # Send via TCP
            result = self._send_tcp_command(name, config, command_str)

            duration_ms = (time.time() - start_time) * 1000

            # Update metrics
            with self._lock:
                for iid, idata in self._instances.items():
                    if idata.get("name") == name:
                        idata["command_count"] = idata.get("command_count", 0) + 1
                        break

            self.metrics.record_command(success=True, duration_ms=duration_ms)

            # Emit command execution event
            self.emit_command_execution(
                instance_name=name,
                command=command,
                command_type=command_type,
                success=True,
                duration_ms=duration_ms,
                result={"response": result}
            )

            return {
                "success": True,
                "result": {"response": result},
                "duration_ms": duration_ms
            }

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # Update error count
            with self._lock:
                for iid, idata in self._instances.items():
                    if idata.get("name") == name:
                        idata["error_count"] = idata.get("error_count", 0) + 1
                        break

            self.metrics.record_command(success=False, duration_ms=duration_ms)

            # Emit error event
            self.emit_command_execution(
                instance_name=name,
                command=command,
                command_type=command_type,
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )

            self.logger.error(f"Command execution failed: {e}")
            raise CommandExecutionError(f"Failed to execute command: {e}")

    def _send_tcp_command(self, name: str, config: Dict[str, Any], command: str) -> str:
        """Send command via TCP and return response."""
        try:
            # Create or reuse TCP connection
            if name not in self._tcp_connections:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(config.get("timeout", self.DEFAULT_TIMEOUT))
                sock.connect((config["host"], config["tcp_port"]))
                with self._lock:
                    self._tcp_connections[name] = sock
            else:
                sock = self._tcp_connections[name]

            # Send command (must end with \r\n)
            command_bytes = f"{command}\r\n".encode("utf-8")
            sock.sendall(command_bytes)

            # vMix typically responds quickly or not at all
            # Read response (if any)
            try:
                sock.settimeout(0.5)  # Short timeout for response
                response = sock.recv(1024).decode("utf-8").strip()
                return response if response else "OK"
            except socket.timeout:
                # No response is normal for many vMix commands
                return "OK"

        except Exception as e:
            # Connection failed, remove from pool
            if name in self._tcp_connections:
                try:
                    self._tcp_connections[name].close()
                except Exception:
                    pass
                with self._lock:
                    del self._tcp_connections[name]

            raise ConnectionError(f"TCP command failed: {e}")

    def health_check(self) -> Dict[str, Any]:
        """
        Return comprehensive health metrics for vMix adapter.

        Returns:
            Health status dictionary
        """
        with self._lock:
            instance_count = len(self._instance_configs)
            connected_count = sum(
                1 for h in self._instance_health.values()
                if h.get("state") == InstanceState.CONNECTED
            )
            error_count = sum(
                1 for h in self._instance_health.values()
                if h.get("state") == InstanceState.ERROR
            )

        # Update metrics
        self.metrics.update_instance_count(
            total=instance_count,
            connected=connected_count,
            errors=error_count
        )

        # Determine overall health status
        if error_count == 0 and connected_count == instance_count:
            status = HealthStatus.HEALTHY
        elif error_count > 0 and connected_count > 0:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.CRITICAL

        metrics = self.metrics.get_metrics()

        return {
            "adapter": self.adapter_type,
            "connected": self.connected,
            "uptime_seconds": metrics["uptime_seconds"],
            "instances": {
                "total": instance_count,
                "connected": connected_count,
                "errors": error_count,
            },
            "metrics": {
                "command_attempts": metrics["command_attempts"],
                "command_success_rate": metrics["command_success_rate"],
                "avg_command_duration_ms": metrics["avg_command_duration_ms"],
                "connection_failures": metrics["connection_failures"],
                "last_error": metrics["last_error"],
            },
            "latency": metrics["latency"],
            "last_check": time.time(),
            "status": status.value,
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate vMix adapter configuration.

        Required fields:
        - type: "vmix"

        Optional fields:
        - timeout: integer > 0
        - discovery_timeout: integer > 0

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if valid

        Raises:
            ConfigurationError: If validation fails
        """
        # Check adapter type
        if config.get("type") != "vmix":
            raise ConfigurationError(f"Invalid adapter type: {config.get('type')}")

        # Validate timeout if present
        if "timeout" in config:
            timeout = config["timeout"]
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                raise ConfigurationError(f"Invalid timeout: {timeout}")

        # Validate discovery_timeout if present
        if "discovery_timeout" in config:
            discovery_timeout = config["discovery_timeout"]
            if not isinstance(discovery_timeout, (int, float)) or discovery_timeout <= 0:
                raise ConfigurationError(f"Invalid discovery_timeout: {discovery_timeout}")

        return True

    # ========================================================================
    # Optional Method Overrides
    # ========================================================================

    def connect(self, host: str, port: int, auth_config: Dict[str, Any]) -> bool:
        """
        Establish connection to vMix instance.

        Args:
            host: vMix host address
            port: TCP port (typically 8099)
            auth_config: Authentication config (api_key if needed)

        Returns:
            True if connection successful

        Raises:
            ConnectionError: If connection fails
        """
        self.logger.info(f"Connecting to vMix at {host}:{port}")

        try:
            # Test TCP connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.DEFAULT_TIMEOUT)
            sock.connect((host, port))
            sock.close()

            # Update connection state
            self._update_connection_state(
                AdapterConnectionState.CONNECTED,
                reason=f"Connected to {host}:{port}"
            )

            self.logger.info("vMix connection established")
            return True

        except Exception as e:
            self._update_connection_state(
                AdapterConnectionState.ERROR,
                reason=f"Connection failed: {e}"
            )
            raise ConnectionError(f"Failed to connect to vMix: {e}")

    def disconnect(self) -> bool:
        """
        Gracefully disconnect from all vMix instances.

        Returns:
            True if successful
        """
        self.logger.info("Disconnecting from vMix instances")

        with self._lock:
            # Close all TCP connections
            for name, sock in list(self._tcp_connections.items()):
                try:
                    sock.close()
                except Exception as e:
                    self.logger.error(f"Error closing connection to {name}: {e}")

            self._tcp_connections.clear()

        # Update connection state
        self._update_connection_state(
            AdapterConnectionState.DISCONNECTED,
            reason="Manual disconnect"
        )

        self.logger.info("Disconnected from all vMix instances")
        return True

    # ========================================================================
    # vMix-Specific Utility Methods
    # ========================================================================

    def get_vmix_xml_status(self, name: str) -> ET.Element:
        """
        Get full XML status from vMix instance.

        Args:
            name: Instance name

        Returns:
            XML root element

        Raises:
            InstanceError: If request fails
        """
        with self._lock:
            if name not in self._instance_configs:
                raise InstanceError(f"Instance not found: {name}")
            config = self._instance_configs[name]

        try:
            url = f"http://{config['host']}:{config['http_port']}/api"
            response = requests.get(url, timeout=config.get("timeout", 5))
            response.raise_for_status()

            return ET.fromstring(response.content)

        except Exception as e:
            raise InstanceError(f"Failed to get XML status: {e}")

    def get_supported_commands(self) -> List[str]:
        """Get list of supported vMix commands."""
        return list(self.VMIX_COMMANDS.keys())

    def validate_command(self, command: str, params: Dict[str, Any]) -> bool:
        """
        Validate command and parameters.

        Args:
            command: vMix function name
            params: Command parameters

        Returns:
            True if valid

        Raises:
            ConfigurationError: If command or params invalid
        """
        if command not in self.VMIX_COMMANDS:
            raise ConfigurationError(f"Unknown vMix command: {command}")

        required_params = self.VMIX_COMMANDS[command]["required"]

        for param in required_params:
            if param not in params:
                raise ConfigurationError(
                    f"Missing required parameter '{param}' for command '{command}'"
                )

        return True

    # ========================================================================
    # Convenience Methods for Common Operations
    # ========================================================================

    def start_recording(self, name: str) -> Dict[str, Any]:
        """Start recording on vMix instance."""
        return self.execute_command(name, "StartRecording", CommandType.START)

    def stop_recording(self, name: str) -> Dict[str, Any]:
        """Stop recording on vMix instance."""
        return self.execute_command(name, "StopRecording", CommandType.STOP)

    def start_streaming(self, name: str) -> Dict[str, Any]:
        """Start streaming on vMix instance."""
        return self.execute_command(name, "StartStreaming", CommandType.START)

    def stop_streaming(self, name: str) -> Dict[str, Any]:
        """Stop streaming on vMix instance."""
        return self.execute_command(name, "StopStreaming", CommandType.STOP)

    def cut_to_input(self, name: str, input_number: str) -> Dict[str, Any]:
        """Cut to specified input."""
        return self.execute_command(name, "Cut", CommandType.CUSTOM, Input=input_number)

    def fade_to_input(self, name: str, duration_ms: int) -> Dict[str, Any]:
        """Fade to next input with specified duration."""
        return self.execute_command(name, "Fade", CommandType.CUSTOM, Duration=duration_ms)

    def set_text(self, name: str, input_number: str, text: str) -> Dict[str, Any]:
        """Set text on specified input."""
        return self.execute_command(
            name, "SetText", CommandType.CONFIGURE,
            Input=input_number, Value=text
        )

    def overlay_on(self, name: str, overlay_number: int, input_number: str) -> Dict[str, Any]:
        """Turn on overlay with specified input."""
        return self.execute_command(
            name, f"OverlayInput{overlay_number}", CommandType.CUSTOM,
            Input=input_number
        )

    def overlay_off(self, name: str, overlay_number: int) -> Dict[str, Any]:
        """Turn off overlay."""
        return self.execute_command(
            name, f"OverlayInput{overlay_number}Off", CommandType.CUSTOM
        )


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create vMix adapter
    config = {
        "type": "vmix",
        "timeout": 10,
        "discovery_timeout": 5,
    }

    adapter = VMixAdapter(config)

    # Example: Discover instances
    print("\n=== Discovering vMix Instances ===")
    try:
        instances = adapter.discover_instances({"timeout": 5})
        print(f"Discovered: {instances}")
    except Exception as e:
        print(f"Discovery failed: {e}")

    # Example: Manually add instance
    print("\n=== Adding vMix Instance ===")
    try:
        instance_config = {
            "host": "192.168.1.100",
            "tcp_port": 8099,
            "http_port": 8088,
        }
        instance_id = adapter.add_instance("Studio-1", instance_config)
        print(f"Added instance: {instance_id}")
    except Exception as e:
        print(f"Failed to add instance: {e}")

    # Example: Get status
    print("\n=== Getting Instance Status ===")
    try:
        status = adapter.get_instance_status("Studio-1")
        print(f"Status: {status}")
    except Exception as e:
        print(f"Failed to get status: {e}")

    # Example: Execute commands
    print("\n=== Executing Commands ===")
    try:
        # Start recording
        result = adapter.start_recording("Studio-1")
        print(f"Start recording: {result}")

        # Cut to input 1
        result = adapter.cut_to_input("Studio-1", "1")
        print(f"Cut to input: {result}")

        # Set text
        result = adapter.set_text("Studio-1", "1", "Hello, IF.bus!")
        print(f"Set text: {result}")

    except Exception as e:
        print(f"Command failed: {e}")

    # Example: Health check
    print("\n=== Health Check ===")
    health = adapter.health_check()
    print(f"Health: {health}")

    # Cleanup
    print("\n=== Cleanup ===")
    adapter.disconnect()
    print("Disconnected")
