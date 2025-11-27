# InfraFabric Series 2: Air Vertical 🚁

**OPERATION SKYNET** - Unified Drone Fleet Integration

---

## Overview

The **Air Vertical** enables InfraFabric to control physical drone hardware across multiple protocols and manufacturers. It provides a unified API that maps high-level AI intents to low-level drone commands.

### Supported Drone Platforms

| Protocol | Target Systems | Use Case | Support Level |
|----------|----------------|----------|---------------|
| **MAVLink** | PX4, ArduPilot, Pixhawk | Commercial/Civil drones (90% market share) | ✅ Full |
| **CoT** | ATAK, FreeTAKServer, TAK | Military/First Responder coordination | ✅ Full |
| **DJI MQTT** | Matrice 300/350, Mavic 3 Enterprise, DJI Dock | Enterprise fleet management | ✅ Full |

---

## Architecture

### The 5 InfraFabric Primitives

All drone operations map to InfraFabric's core primitives:

```python
# 1. IF.logistics.spawn() - Lifecycle operations
await adapter.execute_intent({"primitive": "IF.logistics.spawn", "action": "takeoff", "params": {"altitude_m": 50}})
await adapter.execute_intent({"primitive": "IF.logistics.spawn", "action": "land"})
await adapter.execute_intent({"primitive": "IF.logistics.spawn", "action": "rtl"})  # Return to launch

# 2. IF.matrix.route() - Waypoint navigation
await adapter.execute_intent({
    "primitive": "IF.matrix.route",
    "action": "goto",
    "params": {"latitude": 37.7749, "longitude": -122.4194, "altitude_m": 100, "yaw": 0.0}
})

# 3. IF.process.kill() - Emergency kill switch
await adapter.execute_intent({"primitive": "IF.process.kill"})  # ⚠️ DRONE WILL FALL!

# 4. IF.signal.ingest() - Telemetry streaming
await adapter.execute_intent({"primitive": "IF.signal.ingest"})
state = await adapter.get_state()  # Returns DroneStateSchema

# 5. IF.context.update() - Mode changes, Arm/Disarm
await adapter.execute_intent({"primitive": "IF.context.update", "action": "arm"})
await adapter.execute_intent({"primitive": "IF.context.update", "action": "disarm"})
```

---

## Installation

### 1. Install Dependencies

```bash
cd src/infrafabric/verticals/air
pip install -r requirements.txt
```

**Core dependencies:**
- `mavsdk>=2.10.0` - MAVLink protocol
- `paho-mqtt>=2.1.0` - DJI MQTT protocol
- `requests>=2.31.0` - CoT HTTP API
- `pydantic>=2.5.0` - Schema validation (S2 requirement)

### 2. Hardware Setup

**For MAVLink (PX4/ArduPilot):**
```bash
# Simulation (no hardware needed)
git clone https://github.com/PX4/PX4-Autopilot.git
cd PX4-Autopilot
make px4_sitl gazebo
# Drone available at udpin://0.0.0.0:14540
```

**For CoT (ATAK):**
```bash
# Install FreeTAKServer
docker run -d -p 8087:8087 -p 8088:8088 -p 19023:19023 \
  freetakteam/freetakserver:latest
```

**For DJI:**
- Deploy MQTT broker (EMQX, Mosquitto)
- Configure DJI Dock/drone with broker credentials
- See [DJI Cloud API docs](https://developer.dji.com/cloud-api/)

---

## Quick Start

### Example 1: MAVLink Takeoff and Land

```python
import asyncio
from infrafabric.verticals.air.drone_fleet_adapter import DroneFleetAdapter

async def mavlink_demo():
    # Connect to PX4 SITL
    adapter = DroneFleetAdapter(
        protocol="MAVLINK",
        connection_string="udpin://0.0.0.0:14540",
        drone_id="px4-alpha-01"
    )

    await adapter.connect()

    # Arm and takeoff
    await adapter.execute_intent({"primitive": "IF.context.update", "action": "arm"})
    await adapter.execute_intent({"primitive": "IF.logistics.spawn", "action": "takeoff", "params": {"altitude_m": 50}})

    # Hover for 10 seconds
    await asyncio.sleep(10)

    # Read telemetry
    state = await adapter.get_state()
    print(f"Position: {state.position.latitude}, {state.position.longitude}, {state.position.altitude_msl}m")
    print(f"Battery: {state.battery.percentage}%")

    # Land
    await adapter.execute_intent({"primitive": "IF.logistics.spawn", "action": "land"})

    await adapter.disconnect()

asyncio.run(mavlink_demo())
```

### Example 2: CoT Target Injection (ATAK)

```python
import asyncio
from infrafabric.verticals.air.drone_fleet_adapter import DroneFleetAdapter

async def cot_demo():
    # Connect to FreeTAKServer
    adapter = DroneFleetAdapter(
        protocol="COT",
        connection_string="http://localhost:19023",
        drone_id="reaper-21",
        username="admin",
        password="password"
    )

    await adapter.connect()

    # Inject waypoint target into ATAK map
    await adapter.execute_intent({
        "primitive": "IF.matrix.route",
        "action": "goto",
        "params": {
            "latitude": 35.2271,
            "longitude": -106.5733,
            "altitude_m": 2450.0,
            "yaw": 0.0
        }
    })

    print("✓ Waypoint injected into ATAK tactical map")

    # Send Position Location Information
    cot_bridge = adapter.driver
    await cot_bridge.send_pli(
        latitude=35.2271,
        longitude=-106.5733,
        altitude_m=2450.0,
        callsign="REAPER-21"
    )

    await adapter.disconnect()

asyncio.run(cot_demo())
```

### Example 3: DJI Dock Mission Execution

```python
import asyncio
from infrafabric.verticals.air.drone_fleet_adapter import DroneFleetAdapter

async def dji_demo():
    # Connect to DJI MQTT broker
    adapter = DroneFleetAdapter(
        protocol="DJI",
        connection_string="mqtt+tls://your-broker.com:8883",
        drone_id="matrice-300-01",
        gateway_sn="DOCK123456",
        username="dji_user",
        password="dji_password",
        ca_cert_path="/path/to/ca.crt"
    )

    await adapter.connect()

    # Wait for telemetry
    await asyncio.sleep(5)

    # Get drone state
    state = await adapter.get_state()
    if state:
        print(f"Drone: {state.callsign}")
        print(f"Battery: {state.battery.percentage}%" if state.battery else "N/A")

    # Execute pre-uploaded mission
    dji_bridge = adapter.driver
    await dji_bridge.execute_mission("waypoints_mission_001")

    # Return to dock
    await adapter.execute_intent({"primitive": "IF.logistics.spawn", "action": "rtl"})

    await adapter.disconnect()

asyncio.run(dji_demo())
```

---

## Schema Validation (S2 "No Schema, No Write" Policy)

All drone state is validated using Pydantic schemas before writing to Redis:

```python
from infrafabric.state.air_schema import DroneStateSchema, DronePosition, DroneBattery

# Valid state - will be accepted
state = DroneStateSchema(
    drone_id="alpha-01",
    callsign="ALPHA-01",
    protocol="MAVLINK",
    position=DronePosition(latitude=37.7749, longitude=-122.4194, altitude_msl=100.0, heading=45.0),
    battery=DroneBattery(percentage=75, voltage=24.3),
    connection_string="udpin://0.0.0.0:14540"
)

# Invalid state - will raise ValidationError
try:
    bad_state = DroneStateSchema(
        drone_id="alpha-01",
        latitude=200.0,  # ❌ Invalid! Latitude must be -90 to +90
        longitude=-122.4194
    )
except ValidationError as e:
    print(f"Schema validation failed: {e}")
```

**Redis Key Patterns:**
```
fleet:state:{drone_id}          # Current drone state
fleet:mission:{mission_id}      # Mission definitions
fleet:formation:{formation_id}  # Multi-drone formations
fleet:failure:{incident_id}     # Failure mode incidents
fleet:telemetry:{drone_id}      # Telemetry streams
```

---

## Failure Modes & Mitigations

The lexicon defines 8 critical failure modes with automated mitigations:

| Failure Mode | Detection | Mitigation | Severity |
|--------------|-----------|------------|----------|
| **GPS Spoofing** | Velocity jump >10 m/s, multi-constellation cross-check | Switch to optical flow, immediate land | Critical |
| **Battery Critical** | <20% remaining, voltage <3.3V/cell | Auto RTL at 25%, emergency land at 10% | Critical |
| **Signal Loss** | No heartbeat >3s, RSSI <-100 dBm | Failsafe RTL, continue mission, or land | High |
| **Motor Failure** | Current drop to zero, excessive attitude compensation | Emergency land degraded, deploy parachute | Emergency |
| **Sensor Malfunction** | IMU health fail, barometer impossible change | Switch to redundant sensor, limited RTL | High |
| **Collision Risk** | Proximity <5m, ADS-B traffic <500m horizontal | Auto climb, vector away, immediate hold | Critical |
| **Weather Abort** | Wind >15 m/s, temp <-10°C, visibility <3 mi | Abort and RTL, land nearest safe zone | High |
| **Geofence Breach** | Within 50m of boundary, heading crosses fence | Auto reverse, RTL, immediate land | High |

See `src/infrafabric/config/lexicons/drones.json` for full details.

---

## Industry Jargon Mapping

The lexicon translates drone industry terms to IF primitives:

| Term | Meaning | IF Primitive | Example |
|------|---------|--------------|---------|
| **RTL** | Return To Launch | `IF.logistics.spawn` | `{"action": "rtl"}` |
| **Loiter** | Hold position | `IF.context.update` | `{"mode": "LOITER"}` |
| **Orbit** | Circle POI | `IF.matrix.route` | `{"action": "orbit", "radius_m": 50}` |
| **Waypoints** | Autonomous mission | `IF.logistics.spawn` | `{"action": "execute_mission"}` |
| **Engage** | Target tracking | `IF.matrix.route` | `{"action": "point_gimbal"}` |
| **Geofence** | Virtual boundary | `IF.context.update` | `{"action": "set_geofence"}` |

---

## Testing

### Unit Tests

```bash
cd src/infrafabric/verticals/air
pytest tests/
```

### Integration Testing

**MAVLink with PX4 SITL:**
```bash
# Terminal 1: Start PX4 simulator
make px4_sitl gazebo

# Terminal 2: Run integration test
python -m pytest tests/test_mavlink_integration.py
```

**CoT with FreeTAKServer:**
```bash
# Terminal 1: Start FreeTAKServer
docker run -p 19023:19023 freetakteam/freetakserver

# Terminal 2: Run CoT test
python -m pytest tests/test_cot_integration.py
```

---

## Security Considerations

### MAVLink
- Use encrypted telemetry links (e.g., encrypted UDP/TCP tunnels)
- Validate all incoming commands
- Implement watchdog timers for connection loss

### CoT
- Use bearer token authentication with FreeTAKServer
- Validate XML against CoT schema
- Use TLS for REST API calls
- Sanitize all user-provided data before XML generation

### DJI MQTT
- **ALWAYS** use TLS (port 8883, not 1883)
- Use strong passwords (minimum 16 characters)
- Implement mutual TLS (mTLS) for high-security deployments
- Validate all JSON messages before publishing
- Use QoS 2 for mission-critical commands

**Certificate Management:**
```python
# Good: TLS with certificate validation
client.tls_set(
    ca_certs="/secure/path/ca.crt",
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLSv1_2
)
client.tls_insecure_set(False)  # Verify hostname

# Bad: Insecure connection
client.connect("broker.com", 1883)  # ❌ Unencrypted!
```

---

## Operational Contexts

### Civilian Commercial (FAA Part 107)
- Max altitude: 400 ft AGL
- VLOS required (unless waived)
- Remote pilot certificate mandatory
- Daylight operations only (unless waived)

### Military/Tactical
- CoT integration with ATAK
- Encrypted communications required
- IFF transponder
- BLOS operations authorized

### Public Safety (Fire/Police/SAR)
- COA (Certificate of Waiver) for operations over people
- ATAK coordination with ground units
- Thermal imaging for SAR
- Night operations authorized

---

## Roadmap

### Phase 1: Core Protocols (✅ Complete)
- [x] MAVLink/MAVSDK integration
- [x] CoT/FreeTAKServer integration
- [x] DJI MQTT integration
- [x] Unified DroneFleetAdapter
- [x] Pydantic state schemas
- [x] Lexicon with failure modes

### Phase 2: Advanced Features (🚧 In Progress)
- [ ] Mission planning API (waypoint upload, survey patterns)
- [ ] Multi-drone formation control
- [ ] Deconfliction algorithms
- [ ] Real-time video streaming (RTSP/WebRTC)
- [ ] Collision avoidance (ADS-B integration)

### Phase 3: Enterprise (📋 Planned)
- [ ] Fleet analytics dashboard
- [ ] Predictive maintenance (battery degradation, motor hours)
- [ ] Geofence management UI
- [ ] Regulatory compliance reporting
- [ ] Weather integration (abort on adverse conditions)

---

## Contributing

Follow InfraFabric S2 development patterns:

1. **Schema First**: Define Pydantic models before implementation
2. **Vesicle Transport**: Use `VesiclePayload` for Redis operations
3. **YoloGuard Security**: Scan for credentials in code/config
4. **Arbitrate Governance**: Critical decisions require multi-agent consensus
5. **Test Coverage**: Minimum 80% coverage for new code

---

## References

### MAVLink
- [MAVSDK Python Docs](https://mavsdk.mavlink.io/main/en/python/)
- [PX4 Autopilot](https://px4.io/)
- [ArduPilot](https://ardupilot.org/)

### Cursor-on-Target
- [FreeTAKServer Docs](https://freetakteam.github.io/FreeTAKServer-User-Docs/)
- [CoT Developer's Guide (PDF)](https://tutorials.techrad.co.za/wp-content/uploads/2021/06/The-Developers-Guide-to-Cursor-on-Target-1.pdf)
- [ATAK on Google Play](https://play.google.com/store/apps/details?id=com.atakmap.app.civ)

### DJI
- [DJI Cloud API](https://developer.dji.com/cloud-api/)
- [DJI FlightHub 2](https://www.dji.com/flighthub-2)
- [Paho MQTT Python](https://github.com/eclipse-paho/paho.mqtt.python)

---

## License

InfraFabric Series 2 - Air Vertical
Licensed under the same terms as the parent InfraFabric project.

---

**OPERATION SKYNET: The sky is no longer the limit. It's the beginning.**
