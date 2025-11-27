"""
InfraFabric Series 2: Air Vertical - Unified Drone Fleet Adapter
OPERATION SKYNET: Multi-protocol drone control system

Maps InfraFabric primitives to physical drone hardware:
- IF.logistics.spawn() → Takeoff, Land, Mission Start
- IF.matrix.route() → Waypoint navigation, Deconfliction
- IF.process.kill() → Emergency Kill Switch
- IF.signal.ingest() → Telemetry streaming
- IF.context.update() → Mode changes, Arm/Disarm

Supported Protocols:
1. MAVLINK - PX4/ArduPilot (90% of commercial drones)
2. COT - Cursor-on-Target (Military/ATAK)
3. DJI - DJI Enterprise MQTT (Matrice/Mavic/Dock)
"""

from __future__ import annotations
import asyncio
import logging
import json
import uuid
import time
from typing import Optional, Dict, Any, Literal
from abc import ABC, abstractmethod
from datetime import datetime

# MAVLink imports
try:
    from mavsdk import System
    from mavsdk.action import ActionError
    from mavsdk.offboard import OffboardError, PositionNedYaw
    MAVSDK_AVAILABLE = True
except ImportError:
    MAVSDK_AVAILABLE = False
    logging.warning("MAVSDK not available. Install with: pip install mavsdk")

# CoT imports
try:
    import requests
    from xml.etree.ElementTree import Element, SubElement, tostring
    from xml.dom import minidom
    COT_AVAILABLE = True
except ImportError:
    COT_AVAILABLE = False
    logging.warning("CoT dependencies not available. Install with: pip install requests")

# DJI MQTT imports
try:
    import paho.mqtt.client as mqtt
    DJI_AVAILABLE = True
except ImportError:
    DJI_AVAILABLE = False
    logging.warning("DJI MQTT not available. Install with: pip install paho-mqtt")

from infrafabric.state.air_schema import (
    DroneStateSchema,
    DronePosition,
    DroneAttitude,
    DroneBattery,
    DroneHealth,
    MissionWaypoint,
    DroneMissionSchema
)

logger = logging.getLogger(__name__)


# ============================================================================
# ABSTRACT BASE CLASS
# ============================================================================

class DroneBridgeProtocol(ABC):
    """Abstract interface all drone bridges must implement"""

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to drone/fleet"""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Gracefully disconnect"""
        pass

    @abstractmethod
    async def spawn_takeoff(self, altitude_m: Optional[float] = None) -> bool:
        """IF.logistics.spawn('takeoff') → Initiate takeoff"""
        pass

    @abstractmethod
    async def spawn_land(self) -> bool:
        """IF.logistics.spawn('land') → Initiate landing"""
        pass

    @abstractmethod
    async def spawn_rtl(self) -> bool:
        """IF.logistics.spawn('rtl') → Return to launch"""
        pass

    @abstractmethod
    async def route_goto(self, latitude: float, longitude: float, altitude_m: float, yaw: float = 0.0) -> bool:
        """IF.matrix.route(target) → Navigate to waypoint"""
        pass

    @abstractmethod
    async def kill_emergency(self) -> bool:
        """IF.process.kill() → EMERGENCY KILL SWITCH - drone will fall!"""
        pass

    @abstractmethod
    async def ingest_telemetry(self) -> Optional[DroneStateSchema]:
        """IF.signal.ingest() → Read current drone state"""
        pass

    @abstractmethod
    async def update_context_arm(self) -> bool:
        """IF.context.update('arm') → Arm motors"""
        pass

    @abstractmethod
    async def update_context_disarm(self) -> bool:
        """IF.context.update('disarm') → Disarm motors"""
        pass


# ============================================================================
# MAVLINK BRIDGE (Civil/Commercial Drones)
# ============================================================================

class MavlinkBridge(DroneBridgeProtocol):
    """
    MAVLink/MAVSDK Bridge for PX4 and ArduPilot autopilots
    Supports 90% of commercial drones via UDP/TCP

    Connection strings:
    - udpin://0.0.0.0:14540  (SITL simulation)
    - tcpout://192.168.1.100:14550  (Remote GCS)
    - udpout://127.0.0.1:14551  (Local companion computer)
    """

    def __init__(self, connection_string: str = "udpin://0.0.0.0:14540", drone_id: str = "mavlink-drone-001"):
        if not MAVSDK_AVAILABLE:
            raise ImportError("MAVSDK not installed. Run: pip install mavsdk")

        self.connection_string = connection_string
        self.drone_id = drone_id
        self.drone = System()
        self.connected = False
        self._telemetry_task: Optional[asyncio.Task] = None
        self._latest_state: Optional[DroneStateSchema] = None

    async def connect(self) -> bool:
        """Connect to MAVLink drone"""
        try:
            logger.info(f"[MAVLink] Connecting to {self.connection_string}")
            await self.drone.connect(system_address=self.connection_string)

            # Wait for connection with timeout
            logger.info("[MAVLink] Waiting for drone connection...")
            async for state in self.drone.core.connection_state():
                if state.is_connected:
                    self.connected = True
                    logger.info("✓ [MAVLink] Connected to drone")

                    # Start background telemetry monitoring
                    self._telemetry_task = asyncio.create_task(self._monitor_telemetry())
                    return True

        except Exception as e:
            logger.error(f"✗ [MAVLink] Connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        """Disconnect from MAVLink drone"""
        try:
            if self._telemetry_task:
                self._telemetry_task.cancel()
            self.connected = False
            logger.info("✓ [MAVLink] Disconnected")
            return True
        except Exception as e:
            logger.error(f"✗ [MAVLink] Disconnect error: {e}")
            return False

    async def _monitor_telemetry(self):
        """Background task to monitor telemetry and update state"""
        try:
            async for position in self.drone.telemetry.position():
                # Update cached state
                self._latest_state = await self.ingest_telemetry()
        except asyncio.CancelledError:
            logger.debug("[MAVLink] Telemetry monitoring cancelled")

    async def _wait_for_health(self, timeout: int = 30) -> bool:
        """Wait for drone to be ready for flight"""
        logger.info("[MAVLink] Checking drone health...")
        try:
            async for health in self.drone.telemetry.health():
                if health.is_global_position_ok and health.is_home_position_ok:
                    logger.info("✓ [MAVLink] Drone healthy and ready")
                    return True
        except asyncio.TimeoutError:
            logger.error("✗ [MAVLink] Health check timeout")
            return False

    async def spawn_takeoff(self, altitude_m: Optional[float] = None) -> bool:
        """Takeoff to specified altitude"""
        try:
            if altitude_m:
                await self.drone.action.set_takeoff_altitude(altitude_m)

            logger.info(f"[MAVLink] Taking off to {altitude_m or 'default'} meters")
            await self.drone.action.takeoff()
            logger.info("✓ [MAVLink] Takeoff command sent")
            return True

        except ActionError as e:
            logger.error(f"✗ [MAVLink] Takeoff failed: {e}")
            return False

    async def spawn_land(self) -> bool:
        """Land the drone"""
        try:
            logger.info("[MAVLink] Landing...")
            await self.drone.action.land()
            logger.info("✓ [MAVLink] Landing command sent")
            return True

        except ActionError as e:
            logger.error(f"✗ [MAVLink] Landing failed: {e}")
            return False

    async def spawn_rtl(self) -> bool:
        """Return to launch position"""
        try:
            logger.info("[MAVLink] Returning to launch...")
            await self.drone.action.return_to_launch()
            logger.info("✓ [MAVLink] RTL command sent")
            return True

        except ActionError as e:
            logger.error(f"✗ [MAVLink] RTL failed: {e}")
            return False

    async def route_goto(self, latitude: float, longitude: float, altitude_m: float, yaw: float = 0.0) -> bool:
        """Navigate to GPS waypoint"""
        try:
            logger.info(f"[MAVLink] Going to: {latitude}, {longitude}, {altitude_m}m")
            await self.drone.action.goto_location(
                latitude_deg=latitude,
                longitude_deg=longitude,
                absolute_altitude_m=altitude_m,
                yaw_deg=yaw
            )
            logger.info("✓ [MAVLink] Waypoint command sent")
            return True

        except ActionError as e:
            logger.error(f"✗ [MAVLink] Goto failed: {e}")
            return False

    async def kill_emergency(self) -> bool:
        """
        EMERGENCY KILL SWITCH
        ⚠️  WARNING: Drone will fall immediately if in flight!
        ⚠️  Use only in true emergency situations!
        """
        try:
            logger.critical("⚠️  [MAVLink] EMERGENCY KILL - DRONE WILL FALL")
            await self.drone.action.kill()
            logger.critical("✓ [MAVLink] Kill command sent")
            return True

        except ActionError as e:
            logger.error(f"✗ [MAVLink] Kill command failed: {e}")
            return False

    async def ingest_telemetry(self) -> Optional[DroneStateSchema]:
        """Read current drone state"""
        try:
            # Gather telemetry data concurrently
            position_data = None
            attitude_data = None
            battery_data = None
            health_data = None
            flight_mode = "UNKNOWN"
            armed = False
            in_flight = False

            # Position
            async for position in self.drone.telemetry.position():
                position_data = DronePosition(
                    latitude=position.latitude_deg,
                    longitude=position.longitude_deg,
                    altitude_msl=position.absolute_altitude_m,
                    altitude_rel=position.relative_altitude_m,
                    heading=0.0  # Get from attitude
                )
                break

            # Attitude
            async for attitude in self.drone.telemetry.attitude_euler():
                attitude_data = DroneAttitude(
                    roll=attitude.roll_deg,
                    pitch=attitude.pitch_deg,
                    yaw=attitude.yaw_deg
                )
                if position_data:
                    position_data.heading = attitude.yaw_deg
                break

            # Battery
            async for battery in self.drone.telemetry.battery():
                battery_data = DroneBattery(
                    percentage=int(battery.remaining_percent * 100),
                    voltage=battery.voltage_v,
                    current=None  # Not provided by basic telemetry
                )
                break

            # Health
            async for health in self.drone.telemetry.health():
                health_data = DroneHealth(
                    is_armable=health.is_armable,
                    gps_fix_ok=health.is_global_position_ok,
                    home_position_ok=health.is_home_position_ok,
                    gyro_calibrated=health.is_gyrometer_calibration_ok,
                    accel_calibrated=health.is_accelerometer_calibration_ok,
                    mag_calibrated=health.is_magnetometer_calibration_ok,
                    num_satellites=0  # Get from GPS info
                )
                break

            # Flight mode
            async for mode in self.drone.telemetry.flight_mode():
                flight_mode = str(mode)
                break

            # Armed status
            async for armed_status in self.drone.telemetry.armed():
                armed = armed_status
                break

            # In-flight status
            async for flight_status in self.drone.telemetry.in_air():
                in_flight = flight_status
                break

            # GPS satellites
            async for gps_info in self.drone.telemetry.gps_info():
                if health_data:
                    health_data.num_satellites = gps_info.num_satellites
                break

            # Construct state
            state = DroneStateSchema(
                drone_id=self.drone_id,
                callsign=self.drone_id.upper(),
                protocol="MAVLINK",
                flight_mode=flight_mode,
                armed=armed,
                in_flight=in_flight,
                mission_status="flying" if in_flight else "idle",
                position=position_data,
                attitude=attitude_data,
                battery=battery_data,
                health=health_data,
                last_heartbeat=datetime.utcnow(),
                connection_string=self.connection_string,
                aircraft_type="PX4/ArduPilot"
            )

            return state

        except Exception as e:
            logger.error(f"✗ [MAVLink] Telemetry read failed: {e}")
            return None

    async def update_context_arm(self) -> bool:
        """Arm drone motors"""
        try:
            logger.info("[MAVLink] Arming...")
            await self.drone.action.arm()
            logger.info("✓ [MAVLink] Armed")
            return True

        except ActionError as e:
            logger.error(f"✗ [MAVLink] Arming failed: {e}")
            return False

    async def update_context_disarm(self) -> bool:
        """Disarm drone motors"""
        try:
            logger.info("[MAVLink] Disarming...")
            await self.drone.action.disarm()
            logger.info("✓ [MAVLink] Disarmed")
            return True

        except ActionError as e:
            logger.error(f"✗ [MAVLink] Disarm failed: {e}")
            return False


# ============================================================================
# CURSOR-ON-TARGET BRIDGE (Military/Tactical)
# ============================================================================

class CotBridge(DroneBridgeProtocol):
    """
    Cursor-on-Target (CoT) Bridge for ATAK/FreeTAKServer integration
    Used by military/first responders for tactical coordination

    Key Insight: We don't "fly" these drones directly - we inject
    targets/waypoints into the tactical map for human operators.

    Connection string format: http://freetakserver-host:19023
    """

    def __init__(self, connection_string: str, drone_id: str = "cot-drone-001",
                 username: Optional[str] = None, password: Optional[str] = None):
        if not COT_AVAILABLE:
            raise ImportError("CoT dependencies not installed. Run: pip install requests")

        self.base_url = connection_string.rstrip("/")
        self.drone_id = drone_id
        self.username = username
        self.password = password
        self.bearer_token: Optional[str] = None
        self.connected = False

    def _generate_cot_xml(
        self,
        uid: str,
        event_type: str,
        latitude: float,
        longitude: float,
        altitude_hae: float,
        remarks: str = "",
        callsign: Optional[str] = None
    ) -> str:
        """Generate CoT XML message"""

        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        stale = datetime.utcnow()
        stale = stale.replace(second=stale.second + 300)  # 5 minute stale time
        stale_str = stale.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        event = Element("event")
        event.set("version", "2.0")
        event.set("uid", uid)
        event.set("type", event_type)
        event.set("how", "m-g")  # Machine-generated
        event.set("time", now)
        event.set("start", now)
        event.set("stale", stale_str)

        point = SubElement(event, "point")
        point.set("lat", str(latitude))
        point.set("lon", str(longitude))
        point.set("hae", str(altitude_hae))
        point.set("ce", "5.0")  # Circular error
        point.set("le", "9999999.0")  # Linear error

        detail = SubElement(event, "detail")

        if remarks:
            remarks_elem = SubElement(detail, "remarks")
            remarks_elem.text = remarks

        if callsign:
            contact = SubElement(detail, "contact")
            contact.set("callsign", callsign)

        # Add UAV icon
        usericon = SubElement(detail, "usericon")
        usericon.set("iconsetpath", "Military/Aircraft/Drone")

        # Add color (blue for friendly)
        color = SubElement(detail, "color")
        color.set("value", "-16776961")  # Blue

        # Pretty print
        rough_string = tostring(event, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")

    async def connect(self) -> bool:
        """Authenticate with FreeTAKServer"""
        try:
            if not self.username or not self.password:
                logger.warning("[CoT] No credentials provided, skipping authentication")
                self.connected = True
                return True

            logger.info(f"[CoT] Authenticating with {self.base_url}")
            auth_url = f"{self.base_url}/AuthenticateUser"
            response = requests.post(
                auth_url,
                json={"username": self.username, "password": self.password},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.bearer_token = data.get("token")
                self.connected = True
                logger.info("✓ [CoT] Authenticated successfully")
                return True
            else:
                logger.error(f"✗ [CoT] Authentication failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"✗ [CoT] Connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        """Disconnect from FreeTAKServer"""
        self.connected = False
        self.bearer_token = None
        logger.info("✓ [CoT] Disconnected")
        return True

    def _post_cot(self, cot_xml: str) -> bool:
        """POST CoT XML to FreeTAKServer"""
        try:
            headers = {"Content-Type": "application/xml"}
            if self.bearer_token:
                headers["Authorization"] = f"Bearer {self.bearer_token}"

            post_url = f"{self.base_url}/ManageCoT/postCoT"
            response = requests.post(post_url, data=cot_xml, headers=headers, timeout=10)

            if response.status_code in [200, 201]:
                logger.debug("✓ [CoT] Message posted successfully")
                return True
            else:
                logger.error(f"✗ [CoT] POST failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"✗ [CoT] POST error: {e}")
            return False

    async def spawn_takeoff(self, altitude_m: Optional[float] = None) -> bool:
        """CoT doesn't support direct flight control - log informational event"""
        logger.info("[CoT] Takeoff is operator-controlled, posting PLI update")
        # Post PLI showing drone status
        return True

    async def spawn_land(self) -> bool:
        """CoT doesn't support direct flight control - log informational event"""
        logger.info("[CoT] Landing is operator-controlled, posting PLI update")
        return True

    async def spawn_rtl(self) -> bool:
        """CoT doesn't support direct flight control - log informational event"""
        logger.info("[CoT] RTL is operator-controlled, posting PLI update")
        return True

    async def route_goto(self, latitude: float, longitude: float, altitude_m: float, yaw: float = 0.0) -> bool:
        """Inject waypoint target into ATAK tactical map"""
        try:
            logger.info(f"[CoT] Injecting target waypoint: {latitude}, {longitude}, {altitude_m}m")

            # Create target marker
            cot_xml = self._generate_cot_xml(
                uid=f"WP-{self.drone_id}-{int(time.time())}",
                event_type="a-f-G-E-S",  # Friendly ground equipment sensor
                latitude=latitude,
                longitude=longitude,
                altitude_hae=altitude_m,
                remarks=f"Waypoint for {self.drone_id}",
                callsign=f"{self.drone_id}-WP"
            )

            success = self._post_cot(cot_xml)
            if success:
                logger.info("✓ [CoT] Target waypoint injected into ATAK")
            return success

        except Exception as e:
            logger.error(f"✗ [CoT] Waypoint injection failed: {e}")
            return False

    async def kill_emergency(self) -> bool:
        """Post emergency alert to ATAK"""
        try:
            logger.critical("⚠️  [CoT] EMERGENCY ALERT - Posting to ATAK")

            cot_xml = self._generate_cot_xml(
                uid=f"ALERT-{self.drone_id}-EMERGENCY",
                event_type="a-f-G-E-S",
                latitude=0.0,  # Use actual position if available
                longitude=0.0,
                altitude_hae=0.0,
                remarks=f"EMERGENCY: {self.drone_id} - KILL SWITCH ACTIVATED",
                callsign=f"{self.drone_id}-EMERGENCY"
            )

            return self._post_cot(cot_xml)

        except Exception as e:
            logger.error(f"✗ [CoT] Emergency alert failed: {e}")
            return False

    async def ingest_telemetry(self) -> Optional[DroneStateSchema]:
        """
        CoT systems don't provide bidirectional telemetry via REST
        For PLI ingestion, subscribe to TCP port 8088 or multicast
        """
        logger.debug("[CoT] Telemetry ingestion requires TCP/multicast listener (not implemented)")
        return None

    async def update_context_arm(self) -> bool:
        """CoT doesn't support direct control - informational only"""
        logger.info("[CoT] Arm command is operator-controlled")
        return True

    async def update_context_disarm(self) -> bool:
        """CoT doesn't support direct control - informational only"""
        logger.info("[CoT] Disarm command is operator-controlled")
        return True

    async def send_pli(self, latitude: float, longitude: float, altitude_m: float, callsign: str) -> bool:
        """Send Position Location Information to ATAK"""
        try:
            logger.debug(f"[CoT] Sending PLI for {callsign}")

            cot_xml = self._generate_cot_xml(
                uid=self.drone_id,
                event_type="a-f-A-M-F-Q",  # Friendly air military drone fixed-wing
                latitude=latitude,
                longitude=longitude,
                altitude_hae=altitude_m,
                remarks=f"UAV PLI: {callsign}",
                callsign=callsign
            )

            return self._post_cot(cot_xml)

        except Exception as e:
            logger.error(f"✗ [CoT] PLI send failed: {e}")
            return False


# ============================================================================
# DJI MQTT BRIDGE (Enterprise Drones)
# ============================================================================

class DjiMqttBridge(DroneBridgeProtocol):
    """
    DJI Cloud API MQTT Bridge for Enterprise drones
    Supports: Matrice 300/350, Mavic 3 Enterprise, DJI Dock

    Connection string format: mqtt+tls://broker-host:8883
    """

    def __init__(self, connection_string: str, drone_id: str = "dji-drone-001",
                 gateway_sn: str = "DOCK123456", username: Optional[str] = None,
                 password: Optional[str] = None, ca_cert_path: Optional[str] = None):
        if not DJI_AVAILABLE:
            raise ImportError("DJI MQTT not installed. Run: pip install paho-mqtt")

        # Parse connection string
        self.connection_string = connection_string
        self.gateway_sn = gateway_sn
        self.drone_id = drone_id

        # Parse broker info
        if "mqtt+tls://" in connection_string:
            self.use_tls = True
            broker_info = connection_string.replace("mqtt+tls://", "")
        elif "mqtt://" in connection_string:
            self.use_tls = False
            broker_info = connection_string.replace("mqtt://", "")
        else:
            self.use_tls = True
            broker_info = connection_string

        if ":" in broker_info:
            self.broker_host, port_str = broker_info.split(":")
            self.broker_port = int(port_str)
        else:
            self.broker_host = broker_info
            self.broker_port = 8883 if self.use_tls else 1883

        self.username = username
        self.password = password
        self.ca_cert_path = ca_cert_path

        # MQTT client
        try:
            from importlib.metadata import version
            paho_version = int(version("paho-mqtt").split(".")[0])
            if paho_version >= 2:
                self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                                        client_id=f"infrafabric-{drone_id}")
            else:
                self.client = mqtt.Client(client_id=f"infrafabric-{drone_id}")
        except:
            self.client = mqtt.Client(client_id=f"infrafabric-{drone_id}")

        self.connected = False
        self._latest_state: Optional[DroneStateSchema] = None

        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.connected = True
            logger.info("✓ [DJI] Connected to MQTT broker")

            # Subscribe to telemetry topics
            self.client.subscribe(f"thing/product/{self.gateway_sn}/osd", qos=0)
            self.client.subscribe(f"thing/product/{self.gateway_sn}/state", qos=1)
            self.client.subscribe(f"thing/product/{self.gateway_sn}/events", qos=1)
            self.client.subscribe(f"thing/product/{self.gateway_sn}/services_reply", qos=1)
            self.client.subscribe(f"sys/product/{self.gateway_sn}/status", qos=1)

            logger.info(f"✓ [DJI] Subscribed to telemetry topics for {self.gateway_sn}")
        else:
            logger.error(f"✗ [DJI] Connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.connected = False
        if rc != 0:
            logger.warning(f"[DJI] Unexpected disconnect: {rc}")

    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            logger.debug(f"[DJI] Received message on {msg.topic}")

            # Parse OSD (telemetry) data
            if "/osd" in msg.topic:
                self._parse_osd_data(payload)

            # Handle status replies
            elif "/status" in msg.topic:
                if payload.get("method") == "update_topo":
                    # Send acknowledgment
                    response = {
                        "tid": payload["tid"],
                        "bid": payload["bid"],
                        "timestamp": payload["timestamp"] + 2,
                        "data": {"result": 0}
                    }
                    reply_topic = msg.topic + "_reply"
                    self.client.publish(reply_topic, json.dumps(response), qos=1)

        except json.JSONDecodeError:
            logger.error(f"[DJI] Failed to decode message: {msg.payload}")
        except Exception as e:
            logger.error(f"[DJI] Message handling error: {e}")

    def _parse_osd_data(self, payload: Dict[str, Any]):
        """Parse OSD telemetry data"""
        try:
            data = payload.get("data", {})

            # Update cached state
            if self._latest_state is None:
                self._latest_state = DroneStateSchema(
                    drone_id=self.drone_id,
                    callsign=self.drone_id.upper(),
                    protocol="DJI",
                    connection_string=self.connection_string
                )

            # Update position if available
            if "latitude" in data and "longitude" in data:
                self._latest_state.position = DronePosition(
                    latitude=data.get("latitude", 0.0),
                    longitude=data.get("longitude", 0.0),
                    altitude_msl=data.get("height", 0.0),
                    heading=data.get("att_head", 0.0)
                )

            # Update attitude if available
            if "att_roll" in data:
                self._latest_state.attitude = DroneAttitude(
                    roll=data.get("att_roll", 0.0),
                    pitch=data.get("att_pitch", 0.0),
                    yaw=data.get("att_head", 0.0)
                )

            # Update battery if available
            if "battery_percentage" in data:
                self._latest_state.battery = DroneBattery(
                    percentage=data.get("battery_percentage", 0),
                    voltage=data.get("voltage", 0.0) / 1000.0,  # Convert mV to V
                    current=data.get("current", 0.0) / 1000.0  # Convert mA to A
                )

            self._latest_state.last_heartbeat = datetime.utcnow()

        except Exception as e:
            logger.error(f"[DJI] OSD parsing error: {e}")

    def _publish_command(self, method: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """Publish command to DJI MQTT broker"""
        try:
            message = {
                "tid": str(uuid.uuid4()),
                "bid": str(uuid.uuid4()),
                "timestamp": int(time.time() * 1000),
                "need_reply": 1,
                "gateway": self.gateway_sn,
                "method": method,
                "data": data or {}
            }

            topic = f"thing/product/{self.gateway_sn}/services"
            result = self.client.publish(topic, json.dumps(message), qos=2)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"✓ [DJI] Published command: {method}")
                return True
            else:
                logger.error(f"✗ [DJI] Publish failed: {result.rc}")
                return False

        except Exception as e:
            logger.error(f"✗ [DJI] Command publish error: {e}")
            return False

    async def connect(self) -> bool:
        """Connect to DJI MQTT broker"""
        try:
            logger.info(f"[DJI] Connecting to {self.broker_host}:{self.broker_port}")

            # Set credentials
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)

            # Set TLS if enabled
            if self.use_tls:
                import ssl
                if self.ca_cert_path:
                    self.client.tls_set(
                        ca_certs=self.ca_cert_path,
                        cert_reqs=ssl.CERT_REQUIRED,
                        tls_version=ssl.PROTOCOL_TLSv1_2
                    )
                else:
                    self.client.tls_set(
                        cert_reqs=ssl.CERT_NONE,
                        tls_version=ssl.PROTOCOL_TLSv1_2
                    )
                    self.client.tls_insecure_set(True)

            # Connect
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()

            # Wait for connection
            await asyncio.sleep(2)

            if self.connected:
                logger.info("✓ [DJI] Connected successfully")
                return True
            else:
                logger.error("✗ [DJI] Connection timeout")
                return False

        except Exception as e:
            logger.error(f"✗ [DJI] Connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        """Disconnect from DJI MQTT broker"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("✓ [DJI] Disconnected")
            return True
        except Exception as e:
            logger.error(f"✗ [DJI] Disconnect error: {e}")
            return False

    async def spawn_takeoff(self, altitude_m: Optional[float] = None) -> bool:
        """DJI docks use missions, not direct takeoff commands"""
        logger.info("[DJI] Takeoff via mission execution (use mission upload)")
        return True

    async def spawn_land(self) -> bool:
        """Return aircraft to dock"""
        logger.info("[DJI] Commanding aircraft to return to dock")
        return self._publish_command("dock_return_aircraft")

    async def spawn_rtl(self) -> bool:
        """Return to dock (RTL equivalent for DJI)"""
        return await self.spawn_land()

    async def route_goto(self, latitude: float, longitude: float, altitude_m: float, yaw: float = 0.0) -> bool:
        """DJI uses mission waypoints, not direct goto"""
        logger.info("[DJI] Waypoint navigation via mission upload (use mission system)")
        return True

    async def kill_emergency(self) -> bool:
        """Emergency procedure - return to dock immediately"""
        logger.critical("⚠️  [DJI] EMERGENCY - Commanding immediate dock return")
        return self._publish_command("dock_return_aircraft")

    async def ingest_telemetry(self) -> Optional[DroneStateSchema]:
        """Return cached telemetry state"""
        return self._latest_state

    async def update_context_arm(self) -> bool:
        """DJI docks auto-arm during mission execution"""
        logger.info("[DJI] Arming is automatic during mission execution")
        return True

    async def update_context_disarm(self) -> bool:
        """DJI docks auto-disarm after landing"""
        logger.info("[DJI] Disarming is automatic after landing")
        return True

    async def execute_mission(self, mission_file_id: str) -> bool:
        """Execute uploaded mission"""
        logger.info(f"[DJI] Executing mission: {mission_file_id}")
        return self._publish_command("flighttask_execute", {"file_id": mission_file_id})

    async def open_dock_cover(self) -> bool:
        """Open docking station cover"""
        logger.info("[DJI] Opening dock cover")
        return self._publish_command("dock_open_cover")


# ============================================================================
# UNIFIED DRONE FLEET ADAPTER
# ============================================================================

class DroneFleetAdapter:
    """
    Unified Drone Fleet Adapter - Factory for multi-protocol drone control

    Usage:
        adapter = DroneFleetAdapter(protocol="MAVLINK", connection_string="udpin://0.0.0.0:14540")
        await adapter.connect()
        await adapter.execute_intent({"primitive": "IF.logistics.spawn", "action": "takeoff", "params": {"altitude_m": 50}})
    """

    def __init__(
        self,
        protocol: Literal["MAVLINK", "COT", "DJI"],
        connection_string: str,
        drone_id: Optional[str] = None,
        **kwargs
    ):
        self.protocol = protocol
        self.drone_id = drone_id or f"{protocol.lower()}-drone-{int(time.time())}"

        # Instantiate appropriate bridge
        if protocol == "MAVLINK":
            self.driver = MavlinkBridge(connection_string, self.drone_id)

        elif protocol == "COT":
            username = kwargs.get("username")
            password = kwargs.get("password")
            self.driver = CotBridge(connection_string, self.drone_id, username, password)

        elif protocol == "DJI":
            gateway_sn = kwargs.get("gateway_sn", "DOCK123456")
            username = kwargs.get("username")
            password = kwargs.get("password")
            ca_cert_path = kwargs.get("ca_cert_path")
            self.driver = DjiMqttBridge(
                connection_string, self.drone_id, gateway_sn,
                username, password, ca_cert_path
            )

        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

        logger.info(f"[FleetAdapter] Initialized {protocol} adapter for {self.drone_id}")

    async def connect(self) -> bool:
        """Connect to drone"""
        return await self.driver.connect()

    async def disconnect(self) -> bool:
        """Disconnect from drone"""
        return await self.driver.disconnect()

    async def execute_intent(self, parcel: Dict[str, Any]) -> bool:
        """
        Execute an InfraFabric primitive intent

        Parcel structure:
        {
            "primitive": "IF.logistics.spawn" | "IF.matrix.route" | "IF.process.kill" | "IF.signal.ingest" | "IF.context.update",
            "action": "takeoff" | "land" | "rtl" | "goto" | "kill" | "telemetry" | "arm" | "disarm",
            "params": {...}
        }
        """
        primitive = parcel.get("primitive")
        action = parcel.get("action")
        params = parcel.get("params", {})

        logger.info(f"[FleetAdapter] Executing {primitive}.{action} with params: {params}")

        try:
            # IF.logistics.spawn
            if primitive == "IF.logistics.spawn":
                if action == "takeoff":
                    return await self.driver.spawn_takeoff(params.get("altitude_m"))
                elif action == "land":
                    return await self.driver.spawn_land()
                elif action == "rtl":
                    return await self.driver.spawn_rtl()

            # IF.matrix.route
            elif primitive == "IF.matrix.route":
                if action == "goto":
                    return await self.driver.route_goto(
                        params["latitude"],
                        params["longitude"],
                        params["altitude_m"],
                        params.get("yaw", 0.0)
                    )

            # IF.process.kill
            elif primitive == "IF.process.kill":
                return await self.driver.kill_emergency()

            # IF.signal.ingest
            elif primitive == "IF.signal.ingest":
                state = await self.driver.ingest_telemetry()
                return state is not None

            # IF.context.update
            elif primitive == "IF.context.update":
                if action == "arm":
                    return await self.driver.update_context_arm()
                elif action == "disarm":
                    return await self.driver.update_context_disarm()

            logger.error(f"[FleetAdapter] Unknown intent: {primitive}.{action}")
            return False

        except Exception as e:
            logger.error(f"[FleetAdapter] Intent execution failed: {e}")
            return False

    async def get_state(self) -> Optional[DroneStateSchema]:
        """Get current drone state"""
        return await self.driver.ingest_telemetry()
