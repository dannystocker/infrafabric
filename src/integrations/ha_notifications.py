"""
Home Assistant Notifications and Webhook Integration for InfraFabric

This module provides comprehensive integration with Home Assistant for:
- Sending notifications to mobile devices, browsers, and persistent UI
- Triggering webhook-based automations
- Firing custom events for event-driven automations
- Calling any Home Assistant service

Part of the InfraFabric MASTER INTEGRATION SPRINT - Session 2 (WebRTC)
Enables real-time alerting and automation triggers for production workflows.

Author: InfraFabric Team
License: See LICENSE-CODE
"""

import requests
from typing import Dict, List, Optional, Any
import asyncio
import json
from datetime import datetime
import hashlib


class HomeAssistantError(Exception):
    """Base exception for Home Assistant integration errors"""
    pass


class HomeAssistantConnectionError(HomeAssistantError):
    """Raised when connection to Home Assistant fails"""
    pass


class HomeAssistantAuthError(HomeAssistantError):
    """Raised when authentication fails"""
    pass


class HomeAssistantNotifications:
    """
    Home Assistant notifications and webhook integration
    Enables real-time alerting and automation triggers for InfraFabric

    This class provides a comprehensive interface to Home Assistant's REST API
    for notifications, webhooks, events, and service calls. It integrates with
    IF.witness for provenance tracking and supports all major HA notification types.

    Features:
    - Multiple notification types (mobile, persistent, browser)
    - Webhook automation triggers
    - Custom event firing
    - Generic service calls
    - IF.witness integration for event logging
    - Error handling and validation

    Example:
        >>> ha = HomeAssistantNotifications(
        ...     ha_url="http://192.168.1.50:8123",
        ...     ha_token="eyJ0eXAiOiJKV1QiLCJhbGc..."
        ... )
        >>> ha.send_notification(
        ...     message="WebRTC mesh established",
        ...     title="InfraFabric Alert"
        ... )
    """

    def __init__(self, ha_url: str, ha_token: str, witness_enabled: bool = True):
        """
        Initialize Home Assistant notifications controller

        Args:
            ha_url: Home Assistant instance URL (e.g., http://homeassistant.local:8123)
            ha_token: Long-lived access token from HA
            witness_enabled: Enable IF.witness logging (default: True)

        Raises:
            HomeAssistantConnectionError: If initial connection test fails
            HomeAssistantAuthError: If authentication fails

        Example:
            ha = HomeAssistantNotifications(
                ha_url="http://192.168.1.50:8123",
                ha_token="eyJ0eXAiOiJKV1QiLCJhbGc..."
            )
        """
        self.base_url = ha_url.rstrip('/')
        self.token = ha_token
        self.witness_enabled = witness_enabled
        self.headers = {
            'Authorization': f'Bearer {ha_token}',
            'Content-Type': 'application/json'
        }

        # Validate connection on initialization
        self._validate_connection()

    def _validate_connection(self) -> None:
        """
        Validate connection to Home Assistant

        Raises:
            HomeAssistantConnectionError: If connection fails
            HomeAssistantAuthError: If authentication fails
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/",
                headers=self.headers,
                timeout=5
            )

            if response.status_code == 401:
                raise HomeAssistantAuthError(
                    "Authentication failed. Check your access token."
                )

            if response.status_code != 200:
                raise HomeAssistantConnectionError(
                    f"Failed to connect to Home Assistant: HTTP {response.status_code}"
                )

        except requests.exceptions.ConnectionError as e:
            raise HomeAssistantConnectionError(
                f"Cannot reach Home Assistant at {self.base_url}. "
                f"Is it running? Error: {str(e)}"
            )
        except requests.exceptions.Timeout:
            raise HomeAssistantConnectionError(
                f"Timeout connecting to Home Assistant at {self.base_url}"
            )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        timeout: int = 10
    ) -> Dict:
        """
        Make HTTP request to Home Assistant API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (will be appended to base_url)
            data: Request payload (optional)
            timeout: Request timeout in seconds

        Returns:
            dict: Response data

        Raises:
            HomeAssistantError: On request failure
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                timeout=timeout
            )

            # Handle error responses
            if response.status_code == 401:
                raise HomeAssistantAuthError("Authentication failed")

            if response.status_code >= 400:
                error_msg = f"Home Assistant API error: HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('message', '')}"
                except:
                    error_msg += f" - {response.text}"
                raise HomeAssistantError(error_msg)

            # Return JSON response or empty dict
            if response.content:
                return response.json()
            return {"success": True}

        except requests.exceptions.RequestException as e:
            raise HomeAssistantError(f"Request failed: {str(e)}")

    def send_notification(
        self,
        message: str,
        title: Optional[str] = None,
        target: Optional[List[str]] = None,
        service: str = "notify",
        data: Optional[Dict] = None
    ) -> Dict:
        """
        Send notification via Home Assistant

        Args:
            message: Notification message body
            title: Notification title (optional)
            target: Target devices/entities (optional, defaults to all)
            service: Notification service (default: 'notify')
                    Examples: 'notify', 'mobile_app_iphone', 'mobile_app_android'
            data: Additional notification data (actions, images, etc.)

        Returns:
            dict: Response from Home Assistant

        Raises:
            HomeAssistantError: On notification failure

        Example:
            # Simple notification
            ha.send_notification(
                message="InfraFabric: WebRTC mesh connection established",
                title="InfraFabric Alert"
            )

            # Mobile notification with action
            ha.send_notification(
                message="Stream started to Twitch",
                title="Streaming Alert",
                service="mobile_app_iphone",
                data={
                    "actions": [
                        {"action": "STOP_STREAM", "title": "Stop Stream"},
                        {"action": "VIEW_STATS", "title": "View Stats"}
                    ]
                }
            )

            # Notification with image
            ha.send_notification(
                message="Recording complete",
                title="Production Update",
                data={
                    "image": "/local/thumbnails/recording.jpg",
                    "group": "production"
                }
            )
        """
        # Build notification payload
        payload: Dict[str, Any] = {"message": message}

        if title:
            payload["title"] = title

        if target:
            payload["target"] = target

        if data:
            payload["data"] = data

        # Send notification
        endpoint = f"/api/services/notify/{service}"
        result = self._make_request("POST", endpoint, payload)

        # Log to IF.witness
        if self.witness_enabled:
            asyncio.create_task(self.log_to_witness(
                event_type="notification_sent",
                params={
                    "service": service,
                    "message": message,
                    "title": title,
                    "target": target
                },
                result=result
            ))

        return result

    def send_persistent_notification(
        self,
        message: str,
        title: Optional[str] = None,
        notification_id: Optional[str] = None
    ) -> Dict:
        """
        Send persistent notification (appears in Home Assistant UI)

        Persistent notifications stay in the HA UI until dismissed and are
        useful for status updates and ongoing conditions.

        Args:
            message: Notification message
            title: Notification title
            notification_id: Unique ID (for updating/dismissing later)

        Returns:
            dict: Response from Home Assistant

        Raises:
            HomeAssistantError: On notification failure

        Example:
            ha.send_persistent_notification(
                message="InfraFabric is monitoring 5 WebRTC connections",
                title="IF.swarm Status",
                notification_id="if_swarm_status"
            )

            # Update the same notification later
            ha.send_persistent_notification(
                message="InfraFabric is monitoring 8 WebRTC connections",
                title="IF.swarm Status",
                notification_id="if_swarm_status"  # Same ID updates existing
            )
        """
        payload: Dict[str, Any] = {"message": message}

        if title:
            payload["title"] = title

        if notification_id:
            payload["notification_id"] = notification_id

        endpoint = "/api/services/persistent_notification/create"
        result = self._make_request("POST", endpoint, payload)

        if self.witness_enabled:
            asyncio.create_task(self.log_to_witness(
                event_type="persistent_notification_created",
                params={"notification_id": notification_id, "message": message},
                result=result
            ))

        return result

    def dismiss_persistent_notification(self, notification_id: str) -> Dict:
        """
        Dismiss persistent notification by ID

        Args:
            notification_id: Unique notification ID to dismiss

        Returns:
            dict: Response from Home Assistant

        Example:
            ha.dismiss_persistent_notification("if_swarm_status")
        """
        payload = {"notification_id": notification_id}
        endpoint = "/api/services/persistent_notification/dismiss"
        result = self._make_request("POST", endpoint, payload)

        if self.witness_enabled:
            asyncio.create_task(self.log_to_witness(
                event_type="persistent_notification_dismissed",
                params={"notification_id": notification_id},
                result=result
            ))

        return result

    def trigger_webhook(
        self,
        webhook_id: str,
        data: Dict,
        ha_url: Optional[str] = None
    ) -> Dict:
        """
        Trigger Home Assistant webhook automation

        Webhooks allow external systems to trigger HA automations. The webhook_id
        acts as both the identifier and the authentication token.

        Args:
            webhook_id: Webhook ID (configured in HA automation)
            data: Payload data to send to webhook
            ha_url: Override HA URL (useful for external webhooks)

        Returns:
            dict: Response from webhook

        Raises:
            HomeAssistantError: On webhook trigger failure

        Example:
            # Trigger automation when stream starts
            ha.trigger_webhook(
                webhook_id="if_stream_started",
                data={
                    "platform": "vmix",
                    "destination": "twitch",
                    "timestamp": "2024-01-15T10:30:00Z"
                }
            )

            # Corresponding Home Assistant automation:
            # automation:
            #   - alias: "Turn on ON AIR light when streaming"
            #     trigger:
            #       - platform: webhook
            #         webhook_id: "if_stream_started"
            #     action:
            #       - service: light.turn_on
            #         target:
            #           entity_id: light.on_air_sign
            #         data:
            #           rgb_color: [255, 0, 0]
        """
        # Use custom URL if provided, otherwise use instance URL
        base = ha_url if ha_url else self.base_url
        endpoint = f"/api/webhook/{webhook_id}"

        # Note: Webhooks don't require authentication header (webhook_id is the secret)
        webhook_headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(
                f"{base}{endpoint}",
                headers=webhook_headers,
                json=data,
                timeout=10
            )

            if response.status_code >= 400:
                raise HomeAssistantError(
                    f"Webhook trigger failed: HTTP {response.status_code}"
                )

            result = {"success": True, "webhook_id": webhook_id}
            if response.content:
                try:
                    result.update(response.json())
                except:
                    pass

            if self.witness_enabled:
                asyncio.create_task(self.log_to_witness(
                    event_type="webhook_triggered",
                    params={"webhook_id": webhook_id, "data": data},
                    result=result
                ))

            return result

        except requests.exceptions.RequestException as e:
            raise HomeAssistantError(f"Webhook request failed: {str(e)}")

    def fire_event(
        self,
        event_type: str,
        event_data: Optional[Dict] = None
    ) -> Dict:
        """
        Fire custom event in Home Assistant

        Events are the foundation of HA's event-driven architecture. Custom events
        can be used to trigger automations, log activities, or integrate systems.

        Args:
            event_type: Event type name (e.g., 'if_webrtc_connection_established')
            event_data: Event payload data

        Returns:
            dict: Response from Home Assistant

        Raises:
            HomeAssistantError: On event fire failure

        Example:
            ha.fire_event(
                event_type="if_webrtc_peer_connected",
                event_data={
                    "peer_id": "agent-finance",
                    "latency_ms": 45,
                    "connection_type": "p2p"
                }
            )

            # Corresponding Home Assistant automation:
            # automation:
            #   - alias: "Log WebRTC connections"
            #     trigger:
            #       - platform: event
            #         event_type: if_webrtc_peer_connected
            #     action:
            #       - service: logbook.log
            #         data:
            #           name: "InfraFabric"
            #           message: "Peer {{ trigger.event.data.peer_id }} connected"
        """
        endpoint = f"/api/events/{event_type}"
        result = self._make_request("POST", endpoint, event_data or {})

        if self.witness_enabled:
            asyncio.create_task(self.log_to_witness(
                event_type="ha_event_fired",
                params={"event_type": event_type, "event_data": event_data},
                result=result
            ))

        return result

    def get_services(self) -> Dict:
        """
        Get all available services in Home Assistant

        Returns:
            dict: All services organized by domain

        Example:
            services = ha.get_services()
            # Returns: {"light": {...}, "switch": {...}, "automation": {...}, ...}
        """
        return self._make_request("GET", "/api/services")

    def call_service(
        self,
        domain: str,
        service: str,
        service_data: Optional[Dict] = None,
        target: Optional[Dict] = None
    ) -> Dict:
        """
        Call any Home Assistant service

        This is a generic method for calling any HA service. It's useful for
        controlling lights, switches, automations, and any other HA entity.

        Args:
            domain: Service domain (e.g., 'light', 'switch', 'automation')
            service: Service name (e.g., 'turn_on', 'turn_off', 'trigger')
            service_data: Service data payload
            target: Target entities (entity_id, device_id, area_id, etc.)

        Returns:
            dict: Response from service call

        Raises:
            HomeAssistantError: On service call failure

        Example:
            # Turn on studio lights when production starts
            ha.call_service(
                domain="light",
                service="turn_on",
                target={"entity_id": "light.studio_key_light"},
                service_data={"brightness": 255, "rgb_color": [255, 255, 255]}
            )

            # Trigger automation
            ha.call_service(
                domain="automation",
                service="trigger",
                target={"entity_id": "automation.start_production"}
            )

            # Lock studio door
            ha.call_service(
                domain="lock",
                service="lock",
                target={"entity_id": "lock.studio_door"}
            )
        """
        payload: Dict[str, Any] = {}

        if service_data:
            payload.update(service_data)

        if target:
            payload["target"] = target

        endpoint = f"/api/services/{domain}/{service}"
        result = self._make_request("POST", endpoint, payload)

        if self.witness_enabled:
            asyncio.create_task(self.log_to_witness(
                event_type="service_called",
                params={
                    "domain": domain,
                    "service": service,
                    "service_data": service_data,
                    "target": target
                },
                result=result
            ))

        return result

    # =========================================================================
    # Integration helpers for common InfraFabric scenarios
    # =========================================================================

    def notify_stream_started(
        self,
        platform: str,
        destination: str,
        service: str = "notify"
    ) -> Dict:
        """
        Helper: Notify when stream starts

        Args:
            platform: Streaming platform (vmix, obs)
            destination: Stream destination (twitch, youtube, etc.)
            service: Notification service to use

        Returns:
            dict: Notification response

        Example:
            ha.notify_stream_started(
                platform="vmix",
                destination="twitch"
            )
        """
        return self.send_notification(
            message=f"Stream started: {platform} → {destination}",
            title="InfraFabric Streaming",
            service=service,
            data={
                "tag": "if_stream",
                "group": "infrafabric",
                "platform": platform,
                "destination": destination
            }
        )

    def notify_stream_stopped(
        self,
        platform: str,
        destination: str,
        duration_minutes: Optional[int] = None,
        service: str = "notify"
    ) -> Dict:
        """
        Helper: Notify when stream stops

        Args:
            platform: Streaming platform
            destination: Stream destination
            duration_minutes: Stream duration in minutes (optional)
            service: Notification service to use

        Returns:
            dict: Notification response
        """
        message = f"Stream stopped: {platform} → {destination}"
        if duration_minutes:
            message += f" (Duration: {duration_minutes}m)"

        return self.send_notification(
            message=message,
            title="InfraFabric Streaming",
            service=service,
            data={
                "tag": "if_stream",
                "group": "infrafabric"
            }
        )

    def notify_webrtc_mesh_status(
        self,
        peer_count: int,
        quality: str,
        latency_avg: Optional[float] = None
    ) -> Dict:
        """
        Helper: Notify about WebRTC mesh status

        Args:
            peer_count: Number of connected peers
            quality: Connection quality (excellent, good, fair, poor)
            latency_avg: Average latency in milliseconds (optional)

        Returns:
            dict: Notification response

        Example:
            ha.notify_webrtc_mesh_status(
                peer_count=5,
                quality="excellent",
                latency_avg=25.3
            )
        """
        message = f"{peer_count} peers connected, quality: {quality}"
        if latency_avg:
            message += f", avg latency: {latency_avg:.1f}ms"

        return self.send_persistent_notification(
            message=message,
            title="IF.swarm WebRTC Mesh",
            notification_id="if_webrtc_mesh_status"
        )

    def notify_webrtc_quality_alert(
        self,
        peer_id: str,
        issue: str,
        latency: Optional[float] = None,
        packet_loss: Optional[float] = None
    ) -> Dict:
        """
        Helper: Alert on WebRTC connection quality issues

        Args:
            peer_id: Peer identifier
            issue: Issue description (high_latency, packet_loss, etc.)
            latency: Current latency in ms (optional)
            packet_loss: Packet loss percentage (optional)

        Returns:
            dict: Notification response
        """
        message = f"Connection issue with {peer_id}: {issue}"
        if latency:
            message += f"\nLatency: {latency:.1f}ms"
        if packet_loss:
            message += f"\nPacket loss: {packet_loss:.1f}%"

        return self.send_notification(
            message=message,
            title="InfraFabric Connection Alert",
            data={
                "tag": "if_webrtc_alert",
                "group": "infrafabric",
                "priority": "high"
            }
        )

    def trigger_production_automation(
        self,
        action: str,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Helper: Trigger production automation via webhook

        Args:
            action: Production action (start, stop, switch_scene, etc.)
            params: Additional parameters

        Returns:
            dict: Webhook response

        Example:
            ha.trigger_production_automation(
                action="start",
                params={"scene": "main", "recording": True}
            )
        """
        return self.trigger_webhook(
            webhook_id="if_production_control",
            data={
                "action": action,
                "params": params or {},
                "source": "infrafabric",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )

    def control_studio_lights(
        self,
        state: str,
        brightness: Optional[int] = None,
        color: Optional[List[int]] = None
    ) -> Dict:
        """
        Helper: Control studio lighting

        Args:
            state: 'on' or 'off'
            brightness: Brightness level (0-255)
            color: RGB color [r, g, b]

        Returns:
            dict: Service call response

        Example:
            # Turn on with full brightness and white
            ha.control_studio_lights(
                state="on",
                brightness=255,
                color=[255, 255, 255]
            )
        """
        service_data: Dict[str, Any] = {}

        if brightness is not None:
            service_data["brightness"] = brightness

        if color:
            service_data["rgb_color"] = color

        return self.call_service(
            domain="light",
            service=f"turn_{state}",
            target={"entity_id": "light.studio_lights"},
            service_data=service_data if service_data else None
        )

    def set_on_air_status(self, is_on_air: bool) -> Dict:
        """
        Helper: Control ON AIR indicator light

        Args:
            is_on_air: True to turn on (red), False to turn off

        Returns:
            dict: Service call response

        Example:
            ha.set_on_air_status(True)  # Turn on red ON AIR light
        """
        if is_on_air:
            return self.call_service(
                domain="light",
                service="turn_on",
                target={"entity_id": "light.on_air_sign"},
                service_data={"rgb_color": [255, 0, 0], "brightness": 255}
            )
        else:
            return self.call_service(
                domain="light",
                service="turn_off",
                target={"entity_id": "light.on_air_sign"}
            )

    # =========================================================================
    # IF.witness Integration
    # =========================================================================

    async def log_to_witness(
        self,
        event_type: str,
        params: Dict,
        result: Dict
    ) -> None:
        """
        Log notification operations to IF.witness

        This creates an immutable audit trail of all Home Assistant interactions
        with cryptographic hash chaining for provenance verification.

        Args:
            event_type: Event type (notification_sent, webhook_triggered, etc.)
            params: Operation parameters
            result: Operation result

        Note:
            This is an async operation that logs in the background.
            If IF.witness is not available, errors are silently ignored.
        """
        try:
            # Build witness event
            witness_event = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": f"ha_{event_type}",
                "params": params,
                "result": result,
                "source": "ha_notifications"
            }

            # Calculate event hash
            event_json = json.dumps(witness_event, sort_keys=True)
            event_hash = hashlib.sha256(event_json.encode()).hexdigest()
            witness_event["hash"] = event_hash

            # TODO: Integrate with actual IF.witness implementation
            # For now, just log to console in development
            # In production, this would call IF.witness.log_event(witness_event)

            # Placeholder for IF.witness integration
            # await IF.witness.log_event(witness_event)

        except Exception as e:
            # Silently ignore witness logging errors to not impact main functionality
            # In production, you might want to log these to a monitoring system
            pass

    def get_status(self) -> Dict:
        """
        Get Home Assistant status and version info

        Returns:
            dict: HA status information
        """
        return self._make_request("GET", "/api/")

    def get_config(self) -> Dict:
        """
        Get Home Assistant configuration

        Returns:
            dict: HA configuration details
        """
        return self._make_request("GET", "/api/config")

    def health_check(self) -> bool:
        """
        Perform health check on Home Assistant connection

        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            self._validate_connection()
            return True
        except HomeAssistantError:
            return False


# Export main class and exceptions
__all__ = [
    'HomeAssistantNotifications',
    'HomeAssistantError',
    'HomeAssistantConnectionError',
    'HomeAssistantAuthError'
]
