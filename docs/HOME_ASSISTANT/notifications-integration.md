# Home Assistant Notifications Integration for InfraFabric

Complete guide to integrating Home Assistant notifications, webhooks, and automation triggers with InfraFabric for real-time alerting and production control.

**Part of:** MASTER INTEGRATION SPRINT - Session 2 (WebRTC)
**Status:** Production Ready
**Version:** 1.0.0

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Authentication Setup](#authentication-setup)
5. [Quick Start](#quick-start)
6. [Features](#features)
7. [Usage Examples](#usage-examples)
8. [Home Assistant Automations](#home-assistant-automations)
9. [Use Cases](#use-cases)
10. [Troubleshooting](#troubleshooting)
11. [API Reference](#api-reference)
12. [Best Practices](#best-practices)

---

## Overview

The Home Assistant Notifications integration enables InfraFabric to:

- **Send Notifications**: Mobile, browser, and persistent notifications
- **Trigger Webhooks**: Activate Home Assistant automations from InfraFabric events
- **Fire Events**: Create custom events in the Home Assistant event bus
- **Control Devices**: Call any Home Assistant service (lights, switches, locks, etc.)
- **Track Provenance**: Log all operations to IF.witness for audit trails

### Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  InfraFabric    │         │  Home Assistant  │         │  Mobile Apps    │
│                 │────────>│                  │────────>│  & Devices      │
│  ha_notifications│  REST   │  REST API        │  Push   │                 │
│                 │<────────│                  │<────────│                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
         │                           │
         │                           │
         v                           v
┌─────────────────┐         ┌──────────────────┐
│  IF.witness     │         │  Automations     │
│  (Logging)      │         │  & Actions       │
└─────────────────┘         └──────────────────┘
```

---

## Prerequisites

### Home Assistant Requirements

- **Home Assistant Core**: Version 2023.1 or later
- **Network Access**: InfraFabric must be able to reach Home Assistant's REST API
- **Long-Lived Access Token**: Required for authentication

### Python Requirements

```bash
pip install requests asyncio
```

Or add to your `requirements.txt`:
```
requests>=2.31.0
```

---

## Installation

### 1. Install the Integration

The integration is part of the InfraFabric `src/integrations` package:

```bash
# Already included in InfraFabric
# No additional installation needed
```

### 2. Import the Module

```python
from src.integrations.ha_notifications import HomeAssistantNotifications
```

---

## Authentication Setup

### Creating a Long-Lived Access Token

1. **Log into Home Assistant** in your web browser
2. **Click on your profile** (bottom left, your name/icon)
3. **Scroll down to "Long-Lived Access Tokens"**
4. **Click "Create Token"**
5. **Give it a name**: e.g., "InfraFabric Integration"
6. **Copy the token** immediately (you won't see it again!)

### Token Format

The token will look like:
```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI4ZjJhNmM0...
```

### Store Securely

**IMPORTANT**: Never commit tokens to git!

```bash
# Use environment variables
export HA_URL="http://homeassistant.local:8123"
export HA_TOKEN="your_long_lived_token_here"
```

Or use a config file (add to .gitignore):
```python
# config.py (NEVER commit this file!)
HA_CONFIG = {
    "url": "http://192.168.1.50:8123",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Quick Start

### Basic Initialization

```python
from src.integrations.ha_notifications import HomeAssistantNotifications
import os

# Initialize with environment variables
ha = HomeAssistantNotifications(
    ha_url=os.getenv("HA_URL", "http://homeassistant.local:8123"),
    ha_token=os.getenv("HA_TOKEN")
)

# Send your first notification!
ha.send_notification(
    message="InfraFabric is now connected!",
    title="Integration Active"
)
```

### Verify Connection

```python
# Check if Home Assistant is reachable
if ha.health_check():
    print("✓ Connected to Home Assistant")
    status = ha.get_status()
    print(f"HA Version: {status.get('version')}")
else:
    print("✗ Cannot reach Home Assistant")
```

---

## Features

### 1. Standard Notifications

Send notifications to all configured services:

```python
ha.send_notification(
    message="WebRTC mesh connection established",
    title="InfraFabric Alert"
)
```

### 2. Mobile Notifications with Actions

Interactive notifications with action buttons:

```python
ha.send_notification(
    message="Stream started to Twitch",
    title="Streaming Alert",
    service="mobile_app_iphone",  # Or mobile_app_android
    data={
        "actions": [
            {"action": "STOP_STREAM", "title": "Stop Stream"},
            {"action": "VIEW_STATS", "title": "View Stats"}
        ],
        "group": "streaming"
    }
)
```

### 3. Persistent Notifications

Notifications that stay in the Home Assistant UI:

```python
ha.send_persistent_notification(
    message="InfraFabric is monitoring 5 WebRTC connections",
    title="IF.swarm Status",
    notification_id="if_swarm_status"
)

# Update the same notification
ha.send_persistent_notification(
    message="InfraFabric is monitoring 8 WebRTC connections",
    title="IF.swarm Status",
    notification_id="if_swarm_status"  # Same ID updates existing
)

# Dismiss when done
ha.dismiss_persistent_notification("if_swarm_status")
```

### 4. Webhook Triggers

Trigger Home Assistant automations:

```python
ha.trigger_webhook(
    webhook_id="if_stream_started",
    data={
        "platform": "vmix",
        "destination": "twitch",
        "bitrate": 6000,
        "timestamp": "2024-01-15T10:30:00Z"
    }
)
```

### 5. Custom Events

Fire events in Home Assistant's event bus:

```python
ha.fire_event(
    event_type="if_webrtc_peer_connected",
    event_data={
        "peer_id": "agent-finance",
        "latency_ms": 45,
        "connection_type": "p2p"
    }
)
```

### 6. Service Calls

Control any Home Assistant device or service:

```python
# Turn on lights
ha.call_service(
    domain="light",
    service="turn_on",
    target={"entity_id": "light.studio_key_light"},
    service_data={"brightness": 255, "rgb_color": [255, 255, 255]}
)

# Lock door
ha.call_service(
    domain="lock",
    service="lock",
    target={"entity_id": "lock.studio_door"}
)

# Trigger automation
ha.call_service(
    domain="automation",
    service="trigger",
    target={"entity_id": "automation.start_production"}
)
```

---

## Usage Examples

### Example 1: Streaming Workflow

```python
from src.integrations.ha_notifications import HomeAssistantNotifications

ha = HomeAssistantNotifications(
    ha_url="http://192.168.1.50:8123",
    ha_token="your_token_here"
)

# Stream starting
def start_streaming(platform, destination):
    # Notify via mobile app
    ha.notify_stream_started(platform, destination)

    # Turn on ON AIR light (red)
    ha.set_on_air_status(True)

    # Trigger webhook for additional automations
    ha.trigger_production_automation(
        action="stream_started",
        params={"platform": platform, "dest": destination}
    )

    # Fire event for logging
    ha.fire_event(
        event_type="if_stream_active",
        event_data={"platform": platform, "destination": destination}
    )

# Stream ending
def stop_streaming(platform, destination, duration_minutes):
    # Notify stream stopped
    ha.notify_stream_stopped(platform, destination, duration_minutes)

    # Turn off ON AIR light
    ha.set_on_air_status(False)

    # Trigger webhook
    ha.trigger_production_automation(
        action="stream_stopped",
        params={"duration": duration_minutes}
    )

# Usage
start_streaming("vmix", "twitch")
# ... streaming ...
stop_streaming("vmix", "twitch", 120)
```

### Example 2: WebRTC Monitoring

```python
# Monitor WebRTC mesh health
def monitor_webrtc_mesh(peers):
    # Calculate metrics
    peer_count = len(peers)
    avg_latency = sum(p['latency'] for p in peers) / peer_count

    # Determine quality
    if avg_latency < 50:
        quality = "excellent"
    elif avg_latency < 100:
        quality = "good"
    elif avg_latency < 200:
        quality = "fair"
    else:
        quality = "poor"

    # Update persistent notification
    ha.notify_webrtc_mesh_status(
        peer_count=peer_count,
        quality=quality,
        latency_avg=avg_latency
    )

    # Alert if quality degrades
    if quality in ["fair", "poor"]:
        ha.notify_webrtc_quality_alert(
            peer_id="mesh",
            issue=f"Average latency: {avg_latency:.1f}ms",
            latency=avg_latency
        )

# Usage
peers = [
    {"id": "agent-1", "latency": 45.2},
    {"id": "agent-2", "latency": 52.1},
    {"id": "agent-3", "latency": 38.7}
]
monitor_webrtc_mesh(peers)
```

### Example 3: Production Environment Control

```python
# Complete production setup
def setup_production_environment():
    """Set up studio for production"""

    # 1. Turn on studio lights (bright white)
    ha.control_studio_lights(
        state="on",
        brightness=255,
        color=[255, 255, 255]
    )

    # 2. Lock studio door
    ha.call_service(
        domain="lock",
        service="lock",
        target={"entity_id": "lock.studio_door"}
    )

    # 3. Turn on ON AIR light
    ha.set_on_air_status(True)

    # 4. Send notification
    ha.send_notification(
        message="Production environment is ready",
        title="Studio Setup Complete",
        data={"priority": "high"}
    )

    # 5. Fire event
    ha.fire_event(
        event_type="if_production_started",
        event_data={"timestamp": datetime.utcnow().isoformat()}
    )

    print("✓ Production environment ready")

# Teardown
def teardown_production_environment():
    """Restore studio after production"""

    ha.set_on_air_status(False)
    ha.control_studio_lights(state="off")
    ha.call_service(
        domain="lock",
        service="unlock",
        target={"entity_id": "lock.studio_door"}
    )
    ha.fire_event(event_type="if_production_stopped")

    print("✓ Production environment restored")
```

### Example 4: Error Handling

```python
from src.integrations.ha_notifications import (
    HomeAssistantNotifications,
    HomeAssistantError,
    HomeAssistantConnectionError,
    HomeAssistantAuthError
)

try:
    ha = HomeAssistantNotifications(
        ha_url="http://homeassistant.local:8123",
        ha_token="your_token"
    )

    ha.send_notification(
        message="Test notification",
        title="Test"
    )

except HomeAssistantAuthError as e:
    print(f"Authentication failed: {e}")
    print("Check your access token!")

except HomeAssistantConnectionError as e:
    print(f"Cannot reach Home Assistant: {e}")
    print("Is Home Assistant running?")

except HomeAssistantError as e:
    print(f"Home Assistant error: {e}")
```

---

## Home Assistant Automations

### Automation 1: Turn On ON AIR Light

```yaml
# configuration.yaml or automations.yaml

automation:
  - alias: "Turn on ON AIR light when streaming"
    trigger:
      - platform: webhook
        webhook_id: "if_stream_started"
    action:
      - service: light.turn_on
        target:
          entity_id: light.on_air_sign
        data:
          rgb_color: [255, 0, 0]
          brightness: 255
```

### Automation 2: Log WebRTC Events

```yaml
automation:
  - alias: "Log WebRTC peer connections"
    trigger:
      - platform: event
        event_type: if_webrtc_peer_connected
    action:
      - service: logbook.log
        data:
          name: "InfraFabric WebRTC"
          message: >
            Peer {{ trigger.event.data.peer_id }} connected
            (latency: {{ trigger.event.data.latency_ms }}ms)
```

### Automation 3: Production Lighting

```yaml
automation:
  - alias: "Adjust lighting for production"
    trigger:
      - platform: webhook
        webhook_id: "if_production_control"
    condition:
      - condition: template
        value_template: "{{ trigger.json.action == 'start' }}"
    action:
      # Turn on key light
      - service: light.turn_on
        target:
          entity_id: light.studio_key_light
        data:
          brightness: 255
          kelvin: 5500

      # Turn on fill light
      - service: light.turn_on
        target:
          entity_id: light.studio_fill_light
        data:
          brightness: 180
          kelvin: 5500

      # Lock studio door
      - service: lock.lock
        target:
          entity_id: lock.studio_door
```

### Automation 4: Alert on Quality Issues

```yaml
automation:
  - alias: "Alert on WebRTC quality issues"
    trigger:
      - platform: event
        event_type: if_webrtc_quality_alert
    action:
      # Send critical notification
      - service: notify.mobile_app_admin
        data:
          title: "WebRTC Quality Alert"
          message: >
            Connection issue: {{ trigger.event.data.issue }}
          data:
            priority: high
            tag: webrtc_alert
            group: infrafabric

      # Flash warning light
      - service: light.turn_on
        target:
          entity_id: light.warning_indicator
        data:
          effect: flash
          rgb_color: [255, 165, 0]
```

### Automation 5: Scheduled Status Updates

```yaml
automation:
  - alias: "Daily InfraFabric status report"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      # Request status via webhook
      - service: rest_command.if_status_check

      # Send summary notification
      - service: notify.mobile_app_admin
        data:
          title: "InfraFabric Daily Status"
          message: "Mesh health check complete"
```

---

## Use Cases

### Use Case 1: Live Production Alert System

**Scenario**: Notify production team when streaming starts, control studio environment

**Implementation**:
```python
class ProductionController:
    def __init__(self, ha):
        self.ha = ha

    def start_production(self, platform, destination):
        # Physical environment
        self.ha.set_on_air_status(True)
        self.ha.control_studio_lights(state="on", brightness=255)

        # Notifications
        self.ha.send_notification(
            message=f"LIVE: {platform} → {destination}",
            title="Production Started",
            service="mobile_app_director",
            data={
                "actions": [
                    {"action": "STOP", "title": "Emergency Stop"},
                    {"action": "MUTE", "title": "Mute Audio"}
                ],
                "priority": "high"
            }
        )

        # Webhook trigger
        self.ha.trigger_webhook(
            webhook_id="if_production_control",
            data={"action": "start", "platform": platform}
        )
```

### Use Case 2: WebRTC Mesh Health Monitoring

**Scenario**: Continuous monitoring of WebRTC connections with automatic alerts

**Implementation**:
```python
class MeshHealthMonitor:
    def __init__(self, ha):
        self.ha = ha
        self.alert_threshold_latency = 200  # ms
        self.alert_threshold_packet_loss = 5.0  # percent

    def check_peer_health(self, peer_id, metrics):
        issues = []

        if metrics['latency'] > self.alert_threshold_latency:
            issues.append("high_latency")

        if metrics['packet_loss'] > self.alert_threshold_packet_loss:
            issues.append("packet_loss")

        if issues:
            self.ha.notify_webrtc_quality_alert(
                peer_id=peer_id,
                issue=", ".join(issues),
                latency=metrics['latency'],
                packet_loss=metrics['packet_loss']
            )

            # Fire event for automation
            self.ha.fire_event(
                event_type="if_webrtc_quality_alert",
                event_data={
                    "peer_id": peer_id,
                    "issues": issues,
                    "metrics": metrics
                }
            )

    def update_mesh_status(self, peers):
        peer_count = len(peers)
        avg_latency = sum(p['latency'] for p in peers) / peer_count
        quality = self._calculate_quality(avg_latency)

        self.ha.notify_webrtc_mesh_status(
            peer_count=peer_count,
            quality=quality,
            latency_avg=avg_latency
        )
```

### Use Case 3: Studio Access Control

**Scenario**: Automated studio access based on production status

**Implementation**:
```python
class StudioAccessControl:
    def __init__(self, ha):
        self.ha = ha

    def lock_studio(self, reason="production"):
        self.ha.call_service(
            domain="lock",
            service="lock",
            target={"entity_id": "lock.studio_door"}
        )

        self.ha.send_notification(
            message=f"Studio locked: {reason}",
            title="Access Control",
            service="notify"
        )

        # Fire event
        self.ha.fire_event(
            event_type="if_studio_locked",
            event_data={"reason": reason}
        )

    def unlock_studio(self):
        self.ha.call_service(
            domain="lock",
            service="unlock",
            target={"entity_id": "lock.studio_door"}
        )

        self.ha.fire_event(event_type="if_studio_unlocked")
```

---

## Troubleshooting

### Connection Issues

**Problem**: `HomeAssistantConnectionError: Cannot reach Home Assistant`

**Solutions**:
1. Verify Home Assistant is running
2. Check network connectivity
3. Verify URL format (include http:// or https://)
4. Check firewall rules

```python
# Test basic connectivity
import requests
try:
    response = requests.get("http://homeassistant.local:8123/api/", timeout=5)
    print(f"Status: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
```

### Authentication Issues

**Problem**: `HomeAssistantAuthError: Authentication failed`

**Solutions**:
1. Verify token is valid (not expired or deleted)
2. Check token format (should start with "eyJ")
3. Ensure token has correct permissions
4. Regenerate token if necessary

```python
# Test authentication
ha = HomeAssistantNotifications(
    ha_url="http://homeassistant.local:8123",
    ha_token="your_token"
)
try:
    status = ha.get_status()
    print(f"✓ Authentication successful: {status}")
except HomeAssistantAuthError:
    print("✗ Authentication failed - check your token")
```

### Webhook Not Triggering

**Problem**: Webhook triggers but automation doesn't fire

**Solutions**:
1. Verify webhook_id matches in both code and HA automation
2. Check Home Assistant logs: Settings → System → Logs
3. Test webhook manually:

```bash
curl -X POST \
  http://homeassistant.local:8123/api/webhook/if_test_webhook \
  -H 'Content-Type: application/json' \
  -d '{"test": "data"}'
```

4. Enable automation debug:
```yaml
# configuration.yaml
logger:
  default: info
  logs:
    homeassistant.components.automation: debug
```

### Events Not Firing

**Problem**: Custom events not appearing in Home Assistant

**Solutions**:
1. Check event type name (no spaces, lowercase recommended)
2. Listen for events in Developer Tools → Events
3. Verify event data format (must be JSON-serializable)

Test in HA Developer Tools:
```yaml
# Developer Tools → Events → Listen to events
# Event type: if_test_event
```

### Notification Not Received

**Problem**: Notifications sent but not received on mobile device

**Solutions**:
1. Verify mobile app is configured and logged in
2. Check notification service name matches your app:
   - iOS: `mobile_app_<device_name>`
   - Android: `mobile_app_<device_name>`
3. Test with `notify.notify` (sends to all services)
4. Check mobile app notification settings
5. Verify Home Assistant companion app has notification permissions

### Service Call Fails

**Problem**: `HomeAssistantError: Home Assistant API error: HTTP 404`

**Solutions**:
1. Verify service exists: `ha.get_services()`
2. Check entity_id exists in Home Assistant
3. Verify domain and service names are correct
4. Check service data format

```python
# List available services
services = ha.get_services()
print(services.get('light', {}))
```

### IF.witness Logging Issues

**Problem**: Operations not logged to IF.witness

**Solutions**:
1. Verify `witness_enabled=True`
2. Check IF.witness implementation is available
3. Review async task creation
4. Check for silent exceptions in log_to_witness()

---

## API Reference

### Class: HomeAssistantNotifications

```python
class HomeAssistantNotifications:
    """Main integration class for Home Assistant"""

    def __init__(
        self,
        ha_url: str,
        ha_token: str,
        witness_enabled: bool = True
    ) -> None:
        """Initialize Home Assistant connection"""
```

### Core Methods

#### send_notification()
```python
def send_notification(
    self,
    message: str,
    title: Optional[str] = None,
    target: Optional[List[str]] = None,
    service: str = "notify",
    data: Optional[Dict] = None
) -> Dict:
    """Send notification via Home Assistant"""
```

#### send_persistent_notification()
```python
def send_persistent_notification(
    self,
    message: str,
    title: Optional[str] = None,
    notification_id: Optional[str] = None
) -> Dict:
    """Send persistent notification to HA UI"""
```

#### trigger_webhook()
```python
def trigger_webhook(
    self,
    webhook_id: str,
    data: Dict,
    ha_url: Optional[str] = None
) -> Dict:
    """Trigger Home Assistant webhook automation"""
```

#### fire_event()
```python
def fire_event(
    self,
    event_type: str,
    event_data: Optional[Dict] = None
) -> Dict:
    """Fire custom event in Home Assistant"""
```

#### call_service()
```python
def call_service(
    self,
    domain: str,
    service: str,
    service_data: Optional[Dict] = None,
    target: Optional[Dict] = None
) -> Dict:
    """Call any Home Assistant service"""
```

### Helper Methods

See implementation for full list of helper methods:
- `notify_stream_started()`
- `notify_stream_stopped()`
- `notify_webrtc_mesh_status()`
- `notify_webrtc_quality_alert()`
- `trigger_production_automation()`
- `control_studio_lights()`
- `set_on_air_status()`

### Utility Methods

```python
def get_status() -> Dict:
    """Get Home Assistant status"""

def get_config() -> Dict:
    """Get Home Assistant configuration"""

def get_services() -> Dict:
    """Get all available services"""

def health_check() -> bool:
    """Check if HA is reachable"""
```

---

## Best Practices

### 1. Error Handling

Always wrap HA operations in try-except blocks:

```python
try:
    ha.send_notification("message")
except HomeAssistantError as e:
    logger.error(f"HA notification failed: {e}")
    # Fallback action
```

### 2. Token Security

- Never commit tokens to version control
- Use environment variables or secure vaults
- Rotate tokens periodically
- Use separate tokens for different environments

### 3. Connection Pooling

For high-frequency operations, consider connection pooling:

```python
# Create one instance and reuse
ha = HomeAssistantNotifications(ha_url, ha_token)

# Reuse for multiple operations
ha.send_notification("msg1")
ha.send_notification("msg2")
ha.fire_event("event1")
```

### 4. Webhook Security

- Use unique, random webhook IDs
- Don't expose webhook IDs publicly
- Validate webhook payloads in Home Assistant automations

```yaml
automation:
  - alias: "Secure webhook handler"
    trigger:
      - platform: webhook
        webhook_id: "random_uuid_here_abc123"
    condition:
      - condition: template
        value_template: "{{ trigger.json.source == 'infrafabric' }}"
    action:
      # Your actions here
```

### 5. Rate Limiting

Be mindful of Home Assistant's rate limits:

```python
import time

# Batch notifications
notifications = [...]
for notif in notifications:
    ha.send_notification(notif['message'], notif['title'])
    time.sleep(0.1)  # Small delay between notifications
```

### 6. Logging

Enable comprehensive logging for debugging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Operations will log to IF.witness automatically
```

### 7. Health Monitoring

Regularly check HA health:

```python
import schedule

def check_ha_health():
    if not ha.health_check():
        logger.error("Home Assistant is unreachable!")
        # Send alert via alternative channel

schedule.every(5).minutes.do(check_ha_health)
```

---

## Additional Resources

### Home Assistant Documentation
- [REST API](https://developers.home-assistant.io/docs/api/rest/)
- [Webhooks](https://www.home-assistant.io/docs/automation/trigger/#webhook-trigger)
- [Events](https://www.home-assistant.io/docs/configuration/events/)
- [Mobile App](https://companion.home-assistant.io/)

### InfraFabric Documentation
- [WEBRTC-README.md](../../WEBRTC-README.md)
- [STATUS.md](../../STATUS.md)
- [IF.witness Documentation](../IF-BUS/witness.md)

### Community
- Home Assistant Forum: https://community.home-assistant.io/
- InfraFabric Issues: [GitHub Issues](https://github.com/your-org/infrafabric/issues)

---

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial release
- Full REST API integration
- Notifications, webhooks, events
- Service calls
- Helper methods for common scenarios
- IF.witness integration
- Comprehensive error handling
- Full test coverage

---

## License

See [LICENSE-CODE](../../LICENSE-CODE) for details.

---

## Support

For issues or questions:
1. Check this documentation
2. Review [Troubleshooting](#troubleshooting)
3. Check Home Assistant logs
4. Open an issue on GitHub

---

**Built with care for the InfraFabric community**
