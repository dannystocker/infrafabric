"""
End-to-end smoke test for S2 wiring:
- Guardian approves a broadcast packet
- Coordinator routes through CommunicationCascade
- vMix offline forces SIP fallback
"""

import importlib.util
import os
from collections import defaultdict

import pytest


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader  # type: ignore
    spec.loader.exec_module(module)  # type: ignore
    return module


coord_mod = _load_module(
    "redis_swarm_coordinator",
    os.path.join(PROJECT_ROOT, "restored_s2", "src", "core", "logistics", "redis_swarm_coordinator.py"),
)
packet_mod = _load_module(
    "packet",
    os.path.join(PROJECT_ROOT, "restored_s2", "src", "core", "logistics", "packet.py"),
)
cascade_mod = _load_module(
    "sip_h323_gateway",
    os.path.join(PROJECT_ROOT, "src", "integrations", "broadcast", "sip_h323_gateway.py"),
)


class DummyRedis:
    """Minimal in-memory stand-in to avoid real Redis in tests."""

    def __init__(self):
        self.store = {}
        self.lists = defaultdict(list)
        self.sets = defaultdict(set)
        self.sorted = defaultdict(list)

    def ping(self):
        return True

    def hset(self, key, mapping=None, **kwargs):
        mapping = mapping or kwargs
        self.store[key] = dict(mapping)
        return True

    def set(self, key, value, ex=None, nx=False):
        if nx and key in self.store:
            return False
        self.store[key] = value
        return True

    def sadd(self, key, value):
        self.sets[key].add(value)
        return 1

    def publish(self, *args, **kwargs):
        return 1

    def zadd(self, key, mapping):
        for task, score in mapping.items():
            self.sorted[key].append((task, score))
        self.sorted[key].sort(key=lambda item: item[1])
        return True

    def zrange(self, key, start, end):
        return [task for task, _ in self.sorted.get(key, [])[start : end + 1]]

    def zrem(self, key, member):
        self.sorted[key] = [(task, score) for task, score in self.sorted.get(key, []) if task != member]

    def hgetall(self, key):
        return self.store.get(key, {})

    def delete(self, key):
        self.store.pop(key, None)

    def smembers(self, key):
        return self.sets.get(key, set())

    def get(self, key):
        return self.store.get(key)

    def rpush(self, key, value):
        self.lists[key].append(value)

    def lpop(self, key):
        if self.lists.get(key):
            return self.lists[key].pop(0)
        return None


class OfflineVmix:
    def is_online(self):
        return False


class OnlineSip:
    def __init__(self):
        self.dialed = None

    def is_online(self):
        return True

    def dial(self, target):
        self.dialed = target


@pytest.fixture()
def coordinator(monkeypatch):
    dummy = DummyRedis()
    monkeypatch.setattr(coord_mod.redis, "Redis", lambda *args, **kwargs: dummy)
    coord = coord_mod.RedisSwarmCoordinator()
    coord.agent_id = "agent-test"
    coord.communication_cascade = cascade_mod.CommunicationCascade(
        vmix_client=OfflineVmix(), sip_client=OnlineSip(), pstn_client=None
    )
    return coord


def test_broadcast_cascade_falls_back_to_sip(coordinator):
    packet = packet_mod.Packet(
        origin="council",
        contents={
            "primitive": "IF.matrix.route",
            "vertical": "broadcast",
            "intent": "connect",
            "target": "danny_remote",
            "target_id": "danny_remote",
            "source": "studio_a",
            "destination": "guest_room",
            "entropy": 0.1,
        },
    )

    result = coordinator.dispatch_parcel(packet)

    assert result["route"] == "sip"
    assert coordinator.communication_cascade.sip.dialed == "danny_remote@zoomcrc.com"


# ============================================================================
# GOLDEN RUN: Drone RTL End-to-End Test
# ============================================================================

class MockDroneClient:
    """Mock MAVLink drone client with action.return_to_launch()"""
    def __init__(self):
        self.rtl_triggered = False
        self.action = self  # self-reference for action.return_to_launch()

    def return_to_launch(self):
        print("\n[MAVLINK] >>> EXECUTING RTL via MAVSDK... <<<")
        self.rtl_triggered = True


class MockRosClient:
    """Mock ROS2 client with publish_cmd_vel()"""
    def __init__(self):
        self.estop_triggered = False
        self.last_cmd_vel = None

    def publish_cmd_vel(self, x, y, z):
        print(f"\n[ROS2] >>> EXECUTING E-STOP: cmd_vel({x}, {y}, {z}) <<<")
        self.last_cmd_vel = (x, y, z)
        self.estop_triggered = True


ros2_mod = _load_module(
    "ros2_bridge",
    os.path.join(PROJECT_ROOT, "src", "integrations", "physical", "ros2_bridge.py"),
)


@pytest.fixture()
def drone_coordinator(monkeypatch):
    """Coordinator configured with DroneFleetAdapter stub for drone operations."""
    dummy = DummyRedis()
    monkeypatch.setattr(coord_mod.redis, "Redis", lambda *args, **kwargs: dummy)

    class DummyDroneFleetAdapter:
        last_instance = None

        def __init__(self, *args, **kwargs):
            self.executed = False
            self.payload = None
            DummyDroneFleetAdapter.last_instance = self

        async def execute_intent(self, payload):
            self.executed = True
            self.payload = payload
            return True

    # Monkeypatch the coordinator module to use the stub adapter
    monkeypatch.setattr(coord_mod, "DroneFleetAdapter", DummyDroneFleetAdapter)

    coord = coord_mod.RedisSwarmCoordinator()
    coord.agent_id = "agent-drone-test"
    coord._dummy_adapter_cls = DummyDroneFleetAdapter  # for assertions

    return coord


@pytest.fixture()
def robotics_coordinator(monkeypatch):
    """Coordinator configured with ROS2 bridge for robotics operations."""
    dummy = DummyRedis()
    monkeypatch.setattr(coord_mod.redis, "Redis", lambda *args, **kwargs: dummy)

    mock_ros = MockRosClient()

    coord = coord_mod.RedisSwarmCoordinator()
    coord.agent_id = "agent-robotics-test"
    coord.ros2_bridge = ros2_mod.ROS2Bridge(mock_ros)
    coord._mock_ros = mock_ros  # Store reference for assertions

    return coord


def test_drone_rtl_golden_run(drone_coordinator):
    """
    GOLDEN RUN: End-to-end drone Return-To-Launch

    Flow:
    1. User sends IF.packet(intent="rtl", vertical="drones")
    2. Guardian Council reviews → APPROVES (low entropy)
    3. Coordinator routes to DroneFleetAdapter
    4. Adapter triggers RTL via MAVSDK (stubbed in test)
    """
    print("\n" + "="*70)
    print("GOLDEN RUN: DRONE RTL END-TO-END TEST")
    print("="*70)

    # Step 1: Create packet
    print("\n[STEP 1] Creating IF.packet(intent='rtl', vertical='drones')...")
    packet = packet_mod.Packet(
        origin="user_command",
        contents={
            "primitive": "IF.logistics.spawn",
            "vertical": "drones",
            "intent": "rtl",
            "entropy": 0.05,  # Low risk
            "actor": "pilot_danny",
        },
    )
    print(f"         Packet ID: {packet.tracking_id}")

    # Step 2-4: Dispatch (governance + routing + execution)
    print("\n[STEP 2] Submitting to Guardian Council for review...")
    print("[STEP 3] Routing through RedisSwarmCoordinator...")
    print("[STEP 4] Executing via DroneFleetAdapter...")

    result = drone_coordinator.dispatch_parcel(packet)

    # Verify
    print("\n" + "-"*70)
    print("RESULT:")
    print(f"  Status: {result['status']}")
    print(f"  Adapter: {result['adapter']}")
    print(f"  Intent: {result['intent']}")
    print("-"*70)

    assert result["status"] == "executed"
    assert result["adapter"] == "drone_fleet"
    assert result["intent"] == "rtl"
    # Ensure stub adapter executed
    assert drone_coordinator._dummy_adapter_cls.last_instance is not None
    assert drone_coordinator._dummy_adapter_cls.last_instance.executed is True

    print("\n✅ GOLDEN RUN PASSED: Drone RTL executed successfully!")
    print("="*70 + "\n")


def test_robotics_estop_golden_run(robotics_coordinator):
    """
    GOLDEN RUN: End-to-end robotics E-Stop

    Flow:
    1. User sends IF.packet(intent="estop", vertical="robotics")
    2. Guardian Council reviews → APPROVES (emergency stop = low entropy)
    3. Coordinator routes to ROS2Bridge
    4. Bridge publishes cmd_vel(0,0,0) for safety stop
    """
    print("\n" + "="*70)
    print("GOLDEN RUN: ROBOTICS E-STOP END-TO-END TEST")
    print("="*70)

    # Step 1: Create packet
    print("\n[STEP 1] Creating IF.packet(intent='estop', vertical='robotics')...")
    packet = packet_mod.Packet(
        origin="safety_system",
        contents={
            "primitive": "IF.logistics.spawn",
            "vertical": "robotics",
            "intent": "estop",
            "entropy": 0.01,  # Emergency = very low risk
            "actor": "safety_monitor",
        },
    )
    print(f"         Packet ID: {packet.tracking_id}")

    # Step 2-4: Dispatch
    print("\n[STEP 2] Submitting to Guardian Council for review...")
    print("[STEP 3] Routing through RedisSwarmCoordinator...")
    print("[STEP 4] Executing via ROS2Bridge...")

    result = robotics_coordinator.dispatch_parcel(packet)

    # Verify
    print("\n" + "-"*70)
    print("RESULT:")
    print(f"  Status: {result['status']}")
    print(f"  Adapter: {result['adapter']}")
    print(f"  Intent: {result['intent']}")
    print("-"*70)

    assert result["status"] == "executed"
    assert result["adapter"] == "ros2"
    assert result["intent"] == "estop"
    assert robotics_coordinator._mock_ros.estop_triggered is True
    assert robotics_coordinator._mock_ros.last_cmd_vel == (0.0, 0.0, 0.0)

    print("\n✅ GOLDEN RUN PASSED: Robotics E-Stop executed successfully!")
    print("="*70 + "\n")
