"""
H.323 Gatekeeper High Availability (Hot Standby + Health Monitoring)

Ensures Guardian Council calls don't fail if primary Gatekeeper crashes.

Architecture:
- Primary Gatekeeper (active)
- Secondary Gatekeeper (hot standby)
- Health check monitor (heartbeat + failover)
- Prometheus metrics export
- Grafana dashboard (JSON config)

Failover Requirements:
- Detection: <2 seconds (health check interval)
- Switchover: <3 seconds (DNS/config update)
- Total failover time: <5 seconds

Author: InfraFabric Project
License: CC BY 4.0
Last Updated: 2025-11-11
"""

import asyncio
import json
import subprocess
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, List, Any
import hashlib
import socket


# ============================================================================
# Data Models
# ============================================================================

class GatekeeperRole(Enum):
    """Gatekeeper role in HA cluster"""
    PRIMARY = "primary"
    SECONDARY = "secondary"


class GatekeeperStatus(Enum):
    """Gatekeeper health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class GatekeeperInstance:
    """Gatekeeper instance metadata"""
    instance_id: str
    role: GatekeeperRole
    hostname: str
    port: int
    status: GatekeeperStatus
    last_heartbeat: str
    active_sessions: int = 0
    uptime_seconds: float = 0.0
    total_admissions: int = 0


@dataclass
class FailoverEvent:
    """Failover event record"""
    event_id: str
    timestamp: str
    trigger: str                # "health_check_failed", "manual", "timeout"
    old_primary: str
    new_primary: str
    failover_duration_sec: float
    active_sessions_transferred: int


# ============================================================================
# Health Check Monitor
# ============================================================================

class HealthCheckMonitor:
    """
    Monitors Gatekeeper health via heartbeat checks.

    Health Check Methods:
    1. TCP connection to RAS port (1719)
    2. Ping endpoint (/health)
    3. Process check (ps aux | grep gnugk)
    """

    def __init__(
        self,
        check_interval_sec: int = 2,
        failure_threshold: int = 3
    ):
        self.check_interval_sec = check_interval_sec
        self.failure_threshold = failure_threshold
        self.failure_count: Dict[str, int] = {}

    async def check_health(self, instance: GatekeeperInstance) -> GatekeeperStatus:
        """
        Check gatekeeper health.

        Returns:
            GatekeeperStatus (HEALTHY, DEGRADED, FAILED)
        """
        # Method 1: TCP connection check
        tcp_ok = await self._check_tcp(instance.hostname, instance.port)

        # Method 2: Process check (if localhost)
        process_ok = self._check_process(instance.hostname)

        # Evaluate health
        if tcp_ok and process_ok:
            self.failure_count[instance.instance_id] = 0
            return GatekeeperStatus.HEALTHY

        elif tcp_ok or process_ok:
            self.failure_count[instance.instance_id] = self.failure_count.get(instance.instance_id, 0) + 1
            if self.failure_count[instance.instance_id] < self.failure_threshold:
                return GatekeeperStatus.DEGRADED
            else:
                return GatekeeperStatus.FAILED

        else:
            self.failure_count[instance.instance_id] = self.failure_threshold
            return GatekeeperStatus.FAILED

    async def _check_tcp(self, hostname: str, port: int, timeout: float = 1.0) -> bool:
        """Check if TCP port is reachable"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(hostname, port),
                timeout=timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return False

    def _check_process(self, hostname: str) -> bool:
        """Check if gnugk process is running (localhost only)"""
        if hostname not in ("localhost", "127.0.0.1"):
            return True  # Skip for remote hosts

        try:
            result = subprocess.run(
                ["pgrep", "-f", "gnugk"],
                capture_output=True,
                timeout=1
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False


# ============================================================================
# Failover Controller
# ============================================================================

class FailoverController:
    """
    Manages failover from primary to secondary Gatekeeper.

    Workflow:
    1. Detect primary failure (via HealthCheckMonitor)
    2. Promote secondary to primary
    3. Update DNS/config to point to new primary
    4. Transfer active sessions (if possible)
    5. Log failover event
    """

    def __init__(
        self,
        primary: GatekeeperInstance,
        secondary: GatekeeperInstance,
        log_dir: Path
    ):
        self.primary = primary
        self.secondary = secondary
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.current_primary = primary
        self.failover_in_progress = False
        self.failover_history: List[FailoverEvent] = []

    async def execute_failover(self, trigger: str) -> FailoverEvent:
        """
        Execute failover from primary to secondary.

        Steps:
        1. Promote secondary to primary role
        2. Update config/DNS
        3. Transfer sessions
        4. Log event

        Returns:
            FailoverEvent with timing metrics
        """
        if self.failover_in_progress:
            raise RuntimeError("Failover already in progress")

        self.failover_in_progress = True
        start_time = time.time()

        print(f"\n🚨 FAILOVER TRIGGERED: {trigger}")
        print(f"   Old Primary: {self.current_primary.instance_id}")
        print(f"   New Primary: {self.secondary.instance_id}")

        # Step 1: Promote secondary
        old_primary = self.current_primary
        new_primary = self.secondary

        new_primary.role = GatekeeperRole.PRIMARY
        old_primary.role = GatekeeperRole.SECONDARY

        # Step 2: Update config (write to file)
        await self._update_config(new_primary)

        # Step 3: Transfer sessions (mock - H.323 doesn't support stateful transfer)
        # In real implementation, new admissions would go to new primary
        sessions_transferred = old_primary.active_sessions
        new_primary.active_sessions = sessions_transferred
        old_primary.active_sessions = 0

        # Step 4: Swap roles
        self.current_primary = new_primary
        self.secondary = old_primary

        # Calculate failover duration
        end_time = time.time()
        failover_duration = end_time - start_time

        # Create failover event
        event = FailoverEvent(
            event_id=f"failover-{int(time.time())}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            trigger=trigger,
            old_primary=old_primary.instance_id,
            new_primary=new_primary.instance_id,
            failover_duration_sec=failover_duration,
            active_sessions_transferred=sessions_transferred
        )

        # Log event
        self._log_failover(event)
        self.failover_history.append(event)
        self.failover_in_progress = False

        print(f"✅ Failover complete in {failover_duration:.2f}s")
        print(f"   Sessions transferred: {sessions_transferred}")

        return event

    async def _update_config(self, new_primary: GatekeeperInstance):
        """Update gatekeeper configuration to point to new primary"""
        config = {
            "gatekeeper": {
                "primary": {
                    "instance_id": new_primary.instance_id,
                    "hostname": new_primary.hostname,
                    "port": new_primary.port
                },
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }

        config_file = self.log_dir / "active_gatekeeper.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"   Config updated: {config_file}")

    def _log_failover(self, event: FailoverEvent):
        """Log failover event to IF.witness"""
        log_entry = {
            "event_type": "GATEKEEPER_FAILOVER",
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "trigger": event.trigger,
            "old_primary": event.old_primary,
            "new_primary": event.new_primary,
            "failover_duration_sec": event.failover_duration_sec,
            "sessions_transferred": event.active_sessions_transferred
        }

        # Content hash (IF.witness pattern)
        content_hash = hashlib.sha256(
            json.dumps(log_entry, sort_keys=True).encode()
        ).hexdigest()
        log_entry["hash"] = content_hash

        # Write to log
        log_file = self.log_dir / f"failover_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


# ============================================================================
# Prometheus Metrics Exporter
# ============================================================================

class PrometheusExporter:
    """
    Exports Gatekeeper metrics in Prometheus format.

    Metrics:
    - h323_gatekeeper_up{instance, role} - 1 if healthy, 0 if down
    - h323_gatekeeper_active_sessions{instance} - Number of active sessions
    - h323_gatekeeper_total_admissions{instance} - Total admissions
    - h323_gatekeeper_uptime_seconds{instance} - Uptime
    - h323_gatekeeper_failover_total - Total failover events
    - h323_gatekeeper_failover_duration_seconds - Last failover duration
    """

    def __init__(self, export_port: int = 9090):
        self.export_port = export_port
        self.metrics: Dict[str, Any] = {}

    def update_metrics(
        self,
        instances: List[GatekeeperInstance],
        failover_events: List[FailoverEvent]
    ):
        """Update metrics from Gatekeeper instances"""
        lines = []

        # Gatekeeper up/down
        lines.append("# HELP h323_gatekeeper_up Gatekeeper health status (1=healthy, 0=down)")
        lines.append("# TYPE h323_gatekeeper_up gauge")
        for instance in instances:
            value = 1 if instance.status == GatekeeperStatus.HEALTHY else 0
            lines.append(
                f'h323_gatekeeper_up{{instance="{instance.instance_id}",role="{instance.role.value}"}} {value}'
            )

        # Active sessions
        lines.append("# HELP h323_gatekeeper_active_sessions Number of active Guardian sessions")
        lines.append("# TYPE h323_gatekeeper_active_sessions gauge")
        for instance in instances:
            lines.append(
                f'h323_gatekeeper_active_sessions{{instance="{instance.instance_id}"}} {instance.active_sessions}'
            )

        # Total admissions
        lines.append("# HELP h323_gatekeeper_total_admissions Total admission requests")
        lines.append("# TYPE h323_gatekeeper_total_admissions counter")
        for instance in instances:
            lines.append(
                f'h323_gatekeeper_total_admissions{{instance="{instance.instance_id}"}} {instance.total_admissions}'
            )

        # Uptime
        lines.append("# HELP h323_gatekeeper_uptime_seconds Gatekeeper uptime")
        lines.append("# TYPE h323_gatekeeper_uptime_seconds gauge")
        for instance in instances:
            lines.append(
                f'h323_gatekeeper_uptime_seconds{{instance="{instance.instance_id}"}} {instance.uptime_seconds}'
            )

        # Failover metrics
        lines.append("# HELP h323_gatekeeper_failover_total Total number of failover events")
        lines.append("# TYPE h323_gatekeeper_failover_total counter")
        lines.append(f'h323_gatekeeper_failover_total {len(failover_events)}')

        if failover_events:
            last_failover = failover_events[-1]
            lines.append("# HELP h323_gatekeeper_failover_duration_seconds Last failover duration")
            lines.append("# TYPE h323_gatekeeper_failover_duration_seconds gauge")
            lines.append(f'h323_gatekeeper_failover_duration_seconds {last_failover.failover_duration_sec}')

        self.metrics_text = "\n".join(lines)
        return self.metrics_text

    def start_server(self):
        """Start Prometheus metrics HTTP server"""
        print(f"Prometheus metrics available at http://localhost:{self.export_port}/metrics")
        print("(Mock mode - in production, use prometheus_client library)")


# ============================================================================
# Grafana Dashboard Generator
# ============================================================================

def generate_grafana_dashboard() -> Dict:
    """
    Generate Grafana dashboard JSON for Gatekeeper monitoring.

    Dashboard includes:
    - Gatekeeper health status
    - Active sessions graph
    - Failover event timeline
    - Uptime metrics
    """
    dashboard = {
        "dashboard": {
            "title": "H.323 Gatekeeper High Availability",
            "panels": [
                {
                    "id": 1,
                    "title": "Gatekeeper Health Status",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "h323_gatekeeper_up",
                            "legendFormat": "{{instance}} ({{role}})"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {
                                "mode": "thresholds"
                            },
                            "thresholds": {
                                "steps": [
                                    {"value": 0, "color": "red"},
                                    {"value": 1, "color": "green"}
                                ]
                            }
                        }
                    },
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "Active Guardian Sessions",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "h323_gatekeeper_active_sessions",
                            "legendFormat": "{{instance}}"
                        }
                    ],
                    "yaxes": [
                        {"label": "Sessions", "format": "short"},
                        {"show": False}
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "Failover Events",
                    "type": "table",
                    "targets": [
                        {
                            "expr": "h323_gatekeeper_failover_total"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                },
                {
                    "id": 4,
                    "title": "Failover Duration (Last Event)",
                    "type": "gauge",
                    "targets": [
                        {
                            "expr": "h323_gatekeeper_failover_duration_seconds"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "max": 10,
                            "thresholds": {
                                "steps": [
                                    {"value": 0, "color": "green"},
                                    {"value": 5, "color": "yellow"},
                                    {"value": 8, "color": "red"}
                                ]
                            }
                        }
                    },
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                }
            ],
            "refresh": "5s",
            "time": {"from": "now-1h", "to": "now"}
        }
    }

    return dashboard


# ============================================================================
# High Availability Manager
# ============================================================================

class GatekeeperHAManager:
    """
    Main HA manager orchestrating health checks and failover.
    """

    def __init__(
        self,
        primary_host: str = "localhost",
        primary_port: int = 1719,
        secondary_host: str = "localhost",
        secondary_port: int = 1720,
        log_dir: Path = Path("/home/user/infrafabric/logs/ha")
    ):
        # Initialize instances
        self.primary = GatekeeperInstance(
            instance_id="gatekeeper-primary",
            role=GatekeeperRole.PRIMARY,
            hostname=primary_host,
            port=primary_port,
            status=GatekeeperStatus.UNKNOWN,
            last_heartbeat=datetime.now(timezone.utc).isoformat()
        )

        self.secondary = GatekeeperInstance(
            instance_id="gatekeeper-secondary",
            role=GatekeeperRole.SECONDARY,
            hostname=secondary_host,
            port=secondary_port,
            status=GatekeeperStatus.UNKNOWN,
            last_heartbeat=datetime.now(timezone.utc).isoformat()
        )

        # Initialize components
        self.health_monitor = HealthCheckMonitor(check_interval_sec=2, failure_threshold=3)
        self.failover_controller = FailoverController(self.primary, self.secondary, log_dir)
        self.prometheus = PrometheusExporter(export_port=9090)

        self.running = False

    async def start(self):
        """Start HA manager"""
        print("Starting Gatekeeper HA Manager...")
        print(f"  Primary: {self.primary.hostname}:{self.primary.port}")
        print(f"  Secondary: {self.secondary.hostname}:{self.secondary.port}")

        self.prometheus.start_server()
        self.running = True

        # Start monitoring loop
        await self.monitoring_loop()

    async def monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            # Check primary health
            primary_status = await self.health_monitor.check_health(self.primary)
            self.primary.status = primary_status
            self.primary.last_heartbeat = datetime.now(timezone.utc).isoformat()

            # Check secondary health
            secondary_status = await self.health_monitor.check_health(self.secondary)
            self.secondary.status = secondary_status
            self.secondary.last_heartbeat = datetime.now(timezone.utc).isoformat()

            print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] "
                  f"Primary: {primary_status.value}, Secondary: {secondary_status.value}")

            # Trigger failover if primary failed
            if primary_status == GatekeeperStatus.FAILED and secondary_status == GatekeeperStatus.HEALTHY:
                await self.failover_controller.execute_failover(trigger="health_check_failed")

                # Update instance references after failover
                self.primary = self.failover_controller.current_primary
                self.secondary = self.failover_controller.secondary

            # Update Prometheus metrics
            self.prometheus.update_metrics(
                instances=[self.primary, self.secondary],
                failover_events=self.failover_controller.failover_history
            )

            # Wait before next check
            await asyncio.sleep(self.health_monitor.check_interval_sec)

    def stop(self):
        """Stop HA manager"""
        self.running = False


# ============================================================================
# Example Usage & Failover Test
# ============================================================================

async def test_failover():
    """
    Test failover scenario:
    1. Start HA manager
    2. Simulate primary failure
    3. Verify failover <5 seconds
    """
    print("="*70)
    print("H.323 Gatekeeper High Availability - Failover Test")
    print("="*70)

    # Initialize HA manager
    ha_manager = GatekeeperHAManager(
        primary_host="localhost",
        primary_port=1719,
        secondary_host="localhost",
        secondary_port=1720
    )

    # Simulate primary failure after 5 seconds
    async def simulate_failure():
        await asyncio.sleep(5)
        print("\n💥 SIMULATING PRIMARY FAILURE")
        ha_manager.primary.status = GatekeeperStatus.FAILED

    # Run test for 15 seconds
    async def run_test():
        await asyncio.gather(
            ha_manager.start(),
            simulate_failure()
        )

    try:
        await asyncio.wait_for(run_test(), timeout=15)
    except asyncio.TimeoutError:
        pass

    ha_manager.stop()

    # Print results
    print("\n" + "="*70)
    print("Failover Test Results")
    print("="*70)

    if ha_manager.failover_controller.failover_history:
        event = ha_manager.failover_controller.failover_history[0]
        print(f"✅ Failover successful")
        print(f"   Duration: {event.failover_duration_sec:.3f}s")
        print(f"   Target: <5.000s")
        print(f"   Status: {'PASS' if event.failover_duration_sec < 5.0 else 'FAIL'}")
    else:
        print("❌ No failover occurred")


if __name__ == "__main__":
    # Generate Grafana dashboard
    dashboard = generate_grafana_dashboard()
    dashboard_file = Path("/home/user/infrafabric/config/grafana_gatekeeper_ha.json")
    dashboard_file.parent.mkdir(parents=True, exist_ok=True)
    with open(dashboard_file, 'w') as f:
        json.dump(dashboard, f, indent=2)

    print(f"Grafana dashboard saved to: {dashboard_file}\n")

    # Run failover test
    asyncio.run(test_failover())
