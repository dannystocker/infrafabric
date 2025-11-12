"""
Unit tests for Home Assistant Notifications Integration

Tests all functionality of the HomeAssistantNotifications class including:
- Connection validation and authentication
- Notifications (standard, persistent, mobile)
- Webhook triggers
- Event firing
- Service calls
- Helper methods
- Error handling
- IF.witness integration

Author: InfraFabric Team
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import requests
from datetime import datetime

# Import the module to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from integrations.ha_notifications import (
    HomeAssistantNotifications,
    HomeAssistantError,
    HomeAssistantConnectionError,
    HomeAssistantAuthError
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_ha_response():
    """Mock successful Home Assistant API response"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "success"}
    mock_response.content = b'{"message": "success"}'
    return mock_response


@pytest.fixture
def mock_ha_error_response():
    """Mock error Home Assistant API response"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"message": "Not found"}
    mock_response.text = "Not found"
    return mock_response


@pytest.fixture
def mock_ha_auth_error():
    """Mock authentication error response"""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"message": "Unauthorized"}
    return mock_response


@pytest.fixture
def ha_config():
    """Home Assistant configuration for testing"""
    return {
        "url": "http://homeassistant.local:8123",
        "token": "test_token_12345"
    }


@pytest.fixture
def ha_instance(ha_config, mock_ha_response):
    """Create HomeAssistantNotifications instance with mocked connection"""
    with patch('requests.get', return_value=mock_ha_response):
        return HomeAssistantNotifications(
            ha_url=ha_config["url"],
            ha_token=ha_config["token"],
            witness_enabled=False  # Disable for most tests
        )


# ============================================================================
# Connection and Authentication Tests
# ============================================================================

class TestConnectionAndAuth:
    """Test connection validation and authentication"""

    def test_successful_initialization(self, ha_config, mock_ha_response):
        """Test successful connection to Home Assistant"""
        with patch('requests.get', return_value=mock_ha_response):
            ha = HomeAssistantNotifications(
                ha_url=ha_config["url"],
                ha_token=ha_config["token"]
            )
            assert ha.base_url == "http://homeassistant.local:8123"
            assert ha.token == "test_token_12345"

    def test_url_trailing_slash_removed(self, ha_config, mock_ha_response):
        """Test that trailing slash is removed from URL"""
        with patch('requests.get', return_value=mock_ha_response):
            ha = HomeAssistantNotifications(
                ha_url="http://homeassistant.local:8123/",
                ha_token=ha_config["token"]
            )
            assert ha.base_url == "http://homeassistant.local:8123"

    def test_auth_error_on_init(self, ha_config, mock_ha_auth_error):
        """Test authentication error during initialization"""
        with patch('requests.get', return_value=mock_ha_auth_error):
            with pytest.raises(HomeAssistantAuthError):
                HomeAssistantNotifications(
                    ha_url=ha_config["url"],
                    ha_token="invalid_token"
                )

    def test_connection_error_on_init(self, ha_config):
        """Test connection error during initialization"""
        with patch('requests.get', side_effect=requests.exceptions.ConnectionError("Connection refused")):
            with pytest.raises(HomeAssistantConnectionError) as exc_info:
                HomeAssistantNotifications(
                    ha_url=ha_config["url"],
                    ha_token=ha_config["token"]
                )
            assert "Cannot reach Home Assistant" in str(exc_info.value)

    def test_timeout_error_on_init(self, ha_config):
        """Test timeout error during initialization"""
        with patch('requests.get', side_effect=requests.exceptions.Timeout()):
            with pytest.raises(HomeAssistantConnectionError) as exc_info:
                HomeAssistantNotifications(
                    ha_url=ha_config["url"],
                    ha_token=ha_config["token"]
                )
            assert "Timeout" in str(exc_info.value)

    def test_health_check_success(self, ha_instance, mock_ha_response):
        """Test health check returns True when healthy"""
        with patch('requests.get', return_value=mock_ha_response):
            assert ha_instance.health_check() is True

    def test_health_check_failure(self, ha_instance):
        """Test health check returns False when unhealthy"""
        with patch('requests.get', side_effect=requests.exceptions.ConnectionError()):
            assert ha_instance.health_check() is False


# ============================================================================
# Notification Tests
# ============================================================================

class TestNotifications:
    """Test notification sending functionality"""

    def test_send_simple_notification(self, ha_instance, mock_ha_response):
        """Test sending a simple notification"""
        with patch('requests.request', return_value=mock_ha_response):
            result = ha_instance.send_notification(
                message="Test message",
                title="Test title"
            )
            assert result["message"] == "success"

    def test_send_notification_with_target(self, ha_instance, mock_ha_response):
        """Test sending notification to specific targets"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            ha_instance.send_notification(
                message="Test message",
                target=["mobile_app_iphone"],
                service="mobile_app_iphone"
            )

            # Verify the request payload
            call_args = mock_req.call_args
            assert call_args[1]['json']['target'] == ["mobile_app_iphone"]

    def test_send_notification_with_data(self, ha_instance, mock_ha_response):
        """Test sending notification with additional data"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            ha_instance.send_notification(
                message="Test message",
                data={
                    "actions": [{"action": "TEST", "title": "Test Action"}],
                    "image": "/local/test.jpg"
                }
            )

            call_args = mock_req.call_args
            assert "actions" in call_args[1]['json']['data']

    def test_send_notification_custom_service(self, ha_instance, mock_ha_response):
        """Test sending notification to custom service"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            ha_instance.send_notification(
                message="Test",
                service="mobile_app_android"
            )

            # Verify endpoint
            call_args = mock_req.call_args
            url = call_args[1]['url']
            assert "mobile_app_android" in url

    def test_send_persistent_notification(self, ha_instance, mock_ha_response):
        """Test sending persistent notification"""
        with patch('requests.request', return_value=mock_ha_response):
            result = ha_instance.send_persistent_notification(
                message="Persistent message",
                title="Persistent title",
                notification_id="test_id"
            )
            assert result["message"] == "success"

    def test_send_persistent_notification_update(self, ha_instance, mock_ha_response):
        """Test updating existing persistent notification"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            # Send same ID twice to update
            ha_instance.send_persistent_notification(
                message="Message 1",
                notification_id="test_id"
            )
            ha_instance.send_persistent_notification(
                message="Message 2",
                notification_id="test_id"
            )

            # Both should use same notification_id
            calls = mock_req.call_args_list
            assert calls[0][1]['json']['notification_id'] == "test_id"
            assert calls[1][1]['json']['notification_id'] == "test_id"

    def test_dismiss_persistent_notification(self, ha_instance, mock_ha_response):
        """Test dismissing persistent notification"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            result = ha_instance.dismiss_persistent_notification("test_id")

            call_args = mock_req.call_args
            assert call_args[1]['json']['notification_id'] == "test_id"
            assert "dismiss" in call_args[1]['url']


# ============================================================================
# Webhook Tests
# ============================================================================

class TestWebhooks:
    """Test webhook trigger functionality"""

    def test_trigger_webhook_success(self, ha_instance):
        """Test successful webhook trigger"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b''

        with patch('requests.post', return_value=mock_response):
            result = ha_instance.trigger_webhook(
                webhook_id="test_webhook",
                data={"key": "value"}
            )
            assert result["success"] is True
            assert result["webhook_id"] == "test_webhook"

    def test_trigger_webhook_with_custom_url(self, ha_instance):
        """Test webhook trigger with custom URL"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b''

        with patch('requests.post', return_value=mock_response) as mock_post:
            ha_instance.trigger_webhook(
                webhook_id="test_webhook",
                data={"test": "data"},
                ha_url="http://external.example.com:8123"
            )

            call_args = mock_post.call_args
            assert "external.example.com" in call_args[0][0]

    def test_trigger_webhook_complex_data(self, ha_instance):
        """Test webhook with complex payload"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b''

        complex_data = {
            "action": "stream_started",
            "metadata": {
                "platform": "vmix",
                "destination": "twitch",
                "bitrate": 6000
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }

        with patch('requests.post', return_value=mock_response) as mock_post:
            ha_instance.trigger_webhook(
                webhook_id="if_stream_control",
                data=complex_data
            )

            call_args = mock_post.call_args
            assert call_args[1]['json'] == complex_data

    def test_trigger_webhook_error(self, ha_instance):
        """Test webhook trigger error handling"""
        mock_response = Mock()
        mock_response.status_code = 404

        with patch('requests.post', return_value=mock_response):
            with pytest.raises(HomeAssistantError) as exc_info:
                ha_instance.trigger_webhook(
                    webhook_id="nonexistent",
                    data={}
                )
            assert "Webhook trigger failed" in str(exc_info.value)


# ============================================================================
# Event Tests
# ============================================================================

class TestEvents:
    """Test event firing functionality"""

    def test_fire_event_simple(self, ha_instance, mock_ha_response):
        """Test firing simple event"""
        with patch('requests.request', return_value=mock_ha_response):
            result = ha_instance.fire_event("if_test_event")
            assert result["message"] == "success"

    def test_fire_event_with_data(self, ha_instance, mock_ha_response):
        """Test firing event with data"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            event_data = {
                "peer_id": "agent-test",
                "latency_ms": 42,
                "connection_type": "p2p"
            }

            ha_instance.fire_event(
                event_type="if_webrtc_peer_connected",
                event_data=event_data
            )

            call_args = mock_req.call_args
            assert call_args[1]['json'] == event_data
            assert "if_webrtc_peer_connected" in call_args[1]['url']

    def test_fire_event_empty_data(self, ha_instance, mock_ha_response):
        """Test firing event with no data"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            ha_instance.fire_event("if_test_event", event_data=None)

            call_args = mock_req.call_args
            assert call_args[1]['json'] == {}


# ============================================================================
# Service Call Tests
# ============================================================================

class TestServiceCalls:
    """Test generic service call functionality"""

    def test_call_service_simple(self, ha_instance, mock_ha_response):
        """Test simple service call"""
        with patch('requests.request', return_value=mock_ha_response):
            result = ha_instance.call_service(
                domain="light",
                service="turn_on"
            )
            assert result["message"] == "success"

    def test_call_service_with_target(self, ha_instance, mock_ha_response):
        """Test service call with target"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            ha_instance.call_service(
                domain="light",
                service="turn_on",
                target={"entity_id": "light.studio"}
            )

            call_args = mock_req.call_args
            assert call_args[1]['json']['target']['entity_id'] == "light.studio"

    def test_call_service_with_data(self, ha_instance, mock_ha_response):
        """Test service call with data"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            ha_instance.call_service(
                domain="light",
                service="turn_on",
                service_data={"brightness": 255, "rgb_color": [255, 0, 0]}
            )

            call_args = mock_req.call_args
            assert call_args[1]['json']['brightness'] == 255
            assert call_args[1]['json']['rgb_color'] == [255, 0, 0]

    def test_call_service_full(self, ha_instance, mock_ha_response):
        """Test service call with all parameters"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            ha_instance.call_service(
                domain="light",
                service="turn_on",
                target={"entity_id": "light.studio"},
                service_data={"brightness": 200}
            )

            call_args = mock_req.call_args
            payload = call_args[1]['json']
            assert payload['target']['entity_id'] == "light.studio"
            assert payload['brightness'] == 200

    def test_get_services(self, ha_instance):
        """Test getting available services"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "light": {"turn_on": {}, "turn_off": {}},
            "automation": {"trigger": {}}
        }
        mock_response.content = b'{"light": {}}'

        with patch('requests.request', return_value=mock_response):
            services = ha_instance.get_services()
            assert "light" in services
            assert "automation" in services


# ============================================================================
# Helper Method Tests
# ============================================================================

class TestHelperMethods:
    """Test convenience helper methods"""

    def test_notify_stream_started(self, ha_instance, mock_ha_response):
        """Test stream started notification helper"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            ha_instance.notify_stream_started(
                platform="vmix",
                destination="twitch"
            )

            call_args = mock_req.call_args
            payload = call_args[1]['json']
            assert "vmix" in payload['message']
            assert "twitch" in payload['message']

    def test_notify_stream_stopped(self, ha_instance, mock_ha_response):
        """Test stream stopped notification helper"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            ha_instance.notify_stream_stopped(
                platform="obs",
                destination="youtube",
                duration_minutes=120
            )

            call_args = mock_req.call_args
            payload = call_args[1]['json']
            assert "120m" in payload['message']

    def test_notify_webrtc_mesh_status(self, ha_instance, mock_ha_response):
        """Test WebRTC mesh status notification helper"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            ha_instance.notify_webrtc_mesh_status(
                peer_count=5,
                quality="excellent",
                latency_avg=25.3
            )

            call_args = mock_req.call_args
            payload = call_args[1]['json']
            assert "5 peers" in payload['message']
            assert "excellent" in payload['message']
            assert "25.3ms" in payload['message']

    def test_notify_webrtc_quality_alert(self, ha_instance, mock_ha_response):
        """Test WebRTC quality alert helper"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            ha_instance.notify_webrtc_quality_alert(
                peer_id="agent-test",
                issue="high_latency",
                latency=250.5,
                packet_loss=5.2
            )

            call_args = mock_req.call_args
            payload = call_args[1]['json']
            assert "agent-test" in payload['message']
            assert "high_latency" in payload['message']

    def test_trigger_production_automation(self, ha_instance):
        """Test production automation trigger helper"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b''

        with patch('requests.post', return_value=mock_response) as mock_post:
            ha_instance.trigger_production_automation(
                action="start",
                params={"scene": "main"}
            )

            call_args = mock_post.call_args
            payload = call_args[1]['json']
            assert payload['action'] == "start"
            assert payload['params']['scene'] == "main"
            assert payload['source'] == "infrafabric"

    def test_control_studio_lights_on(self, ha_instance, mock_ha_response):
        """Test studio lights control helper - turn on"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            ha_instance.control_studio_lights(
                state="on",
                brightness=255,
                color=[255, 255, 255]
            )

            call_args = mock_req.call_args
            assert "turn_on" in call_args[1]['url']
            assert call_args[1]['json']['brightness'] == 255
            assert call_args[1]['json']['rgb_color'] == [255, 255, 255]

    def test_control_studio_lights_off(self, ha_instance, mock_ha_response):
        """Test studio lights control helper - turn off"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            ha_instance.control_studio_lights(state="off")

            call_args = mock_req.call_args
            assert "turn_off" in call_args[1]['url']

    def test_set_on_air_status_on(self, ha_instance, mock_ha_response):
        """Test ON AIR status - turn on"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            ha_instance.set_on_air_status(True)

            call_args = mock_req.call_args
            assert "turn_on" in call_args[1]['url']
            assert call_args[1]['json']['rgb_color'] == [255, 0, 0]

    def test_set_on_air_status_off(self, ha_instance, mock_ha_response):
        """Test ON AIR status - turn off"""
        with patch('requests.request', return_value=mock_ha_response) as mock_req:
            ha_instance.set_on_air_status(False)

            call_args = mock_req.call_args
            assert "turn_off" in call_args[1]['url']


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_handle_404_error(self, ha_instance):
        """Test handling of 404 error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not found"}

        with patch('requests.request', return_value=mock_response):
            with pytest.raises(HomeAssistantError) as exc_info:
                ha_instance.send_notification("test")
            assert "404" in str(exc_info.value)

    def test_handle_500_error(self, ha_instance):
        """Test handling of 500 server error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal error"}

        with patch('requests.request', return_value=mock_response):
            with pytest.raises(HomeAssistantError):
                ha_instance.send_notification("test")

    def test_handle_auth_error_in_request(self, ha_instance):
        """Test handling of auth error during request"""
        mock_response = Mock()
        mock_response.status_code = 401

        with patch('requests.request', return_value=mock_response):
            with pytest.raises(HomeAssistantAuthError):
                ha_instance.send_notification("test")

    def test_handle_network_error(self, ha_instance):
        """Test handling of network errors"""
        with patch('requests.request', side_effect=requests.exceptions.ConnectionError()):
            with pytest.raises(HomeAssistantError):
                ha_instance.send_notification("test")

    def test_handle_timeout(self, ha_instance):
        """Test handling of timeout errors"""
        with patch('requests.request', side_effect=requests.exceptions.Timeout()):
            with pytest.raises(HomeAssistantError):
                ha_instance.send_notification("test")

    def test_handle_invalid_json_response(self, ha_instance):
        """Test handling of invalid JSON in response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("error", "", 0)
        mock_response.content = b''

        with patch('requests.request', return_value=mock_response):
            # Should not raise, returns success dict
            result = ha_instance.send_notification("test")
            assert result["success"] is True


# ============================================================================
# IF.witness Integration Tests
# ============================================================================

class TestWitnessIntegration:
    """Test IF.witness logging integration"""

    @pytest.mark.asyncio
    async def test_witness_logging_notification(self, ha_config, mock_ha_response):
        """Test witness logging for notifications"""
        with patch('requests.get', return_value=mock_ha_response):
            ha = HomeAssistantNotifications(
                ha_url=ha_config["url"],
                ha_token=ha_config["token"],
                witness_enabled=True
            )

        with patch('requests.request', return_value=mock_ha_response):
            with patch('asyncio.create_task') as mock_task:
                ha.send_notification("test message")
                # Verify witness logging was called
                assert mock_task.called

    @pytest.mark.asyncio
    async def test_witness_logging_webhook(self, ha_config, mock_ha_response):
        """Test witness logging for webhooks"""
        with patch('requests.get', return_value=mock_ha_response):
            ha = HomeAssistantNotifications(
                ha_url=ha_config["url"],
                ha_token=ha_config["token"],
                witness_enabled=True
            )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b''

        with patch('requests.post', return_value=mock_response):
            with patch('asyncio.create_task') as mock_task:
                ha.trigger_webhook("test_webhook", {"data": "value"})
                assert mock_task.called

    @pytest.mark.asyncio
    async def test_witness_disabled(self, ha_config, mock_ha_response):
        """Test that witness logging is disabled when configured"""
        with patch('requests.get', return_value=mock_ha_response):
            ha = HomeAssistantNotifications(
                ha_url=ha_config["url"],
                ha_token=ha_config["token"],
                witness_enabled=False
            )

        with patch('requests.request', return_value=mock_ha_response):
            with patch('asyncio.create_task') as mock_task:
                ha.send_notification("test")
                # Witness should not be called
                assert not mock_task.called


# ============================================================================
# Status and Config Tests
# ============================================================================

class TestStatusAndConfig:
    """Test status and configuration methods"""

    def test_get_status(self, ha_instance):
        """Test getting HA status"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": "API running.",
            "version": "2024.1.0"
        }
        mock_response.content = b'{"message": "API running."}'

        with patch('requests.request', return_value=mock_response):
            status = ha_instance.get_status()
            assert "message" in status

    def test_get_config(self, ha_instance):
        """Test getting HA configuration"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "location_name": "Home",
            "version": "2024.1.0",
            "components": ["automation", "light"]
        }
        mock_response.content = b'{"location_name": "Home"}'

        with patch('requests.request', return_value=mock_response):
            config = ha_instance.get_config()
            assert "location_name" in config


# ============================================================================
# Integration Tests (with mock server)
# ============================================================================

class TestIntegration:
    """Integration tests simulating full workflows"""

    def test_complete_streaming_workflow(self, ha_instance, mock_ha_response):
        """Test complete streaming workflow"""
        with patch('requests.request', return_value=mock_ha_response):
            with patch('requests.post', return_value=Mock(status_code=200, content=b'')):
                # Start stream
                ha_instance.notify_stream_started("vmix", "twitch")

                # Turn on ON AIR light
                ha_instance.set_on_air_status(True)

                # Trigger production automation
                ha_instance.trigger_production_automation("stream_started")

                # Fire event
                ha_instance.fire_event("if_stream_active", {"platform": "vmix"})

                # All operations should succeed
                assert True

    def test_complete_production_workflow(self, ha_instance, mock_ha_response):
        """Test complete production workflow"""
        with patch('requests.request', return_value=mock_ha_response):
            # Turn on studio lights
            ha_instance.control_studio_lights(
                state="on",
                brightness=255,
                color=[255, 255, 255]
            )

            # Send persistent status
            ha_instance.send_persistent_notification(
                message="Production in progress",
                notification_id="prod_status"
            )

            # Update WebRTC status
            ha_instance.notify_webrtc_mesh_status(
                peer_count=3,
                quality="excellent"
            )

            # All operations should succeed
            assert True


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
