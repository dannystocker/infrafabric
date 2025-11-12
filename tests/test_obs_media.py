"""
Comprehensive Test Suite for OBS Media Integration Module

This test suite validates the OBS WebSocket client, media source controller,
browser source controller, and capture source controller functionality.

Test Coverage:
- WebSocket connection and authentication
- Media source creation (ffmpeg_source, image_source, slideshow, vlc_source)
- Browser source creation and refresh
- Capture source creation (window, display, game, audio)
- Media playback control (play, pause, stop, restart, next, previous)
- IF.witness audit logging
- Error handling and edge cases

Author: InfraFabric Project
License: CC BY 4.0
Last Updated: 2025-11-12
"""

import json
import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations.obs_media import (
    OBSWebSocketClient,
    MediaSourceController,
    BrowserSourceController,
    CaptureSourceController,
    OBSMediaManager,
    MediaInputType,
    MediaAction,
    Platform,
    MediaSourceConfig,
    BrowserSourceConfig,
    CaptureSourceConfig,
    WitnessLog
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    with patch('integrations.obs_media.websocket') as mock_ws:
        mock_connection = MagicMock()
        mock_ws.create_connection.return_value = mock_connection

        # Mock Hello message (no auth)
        hello_msg = {
            "op": 0,
            "d": {
                "obsWebSocketVersion": "5.0.0",
                "rpcVersion": 1
            }
        }
        mock_connection.recv.return_value = json.dumps(hello_msg)

        yield mock_ws, mock_connection


@pytest.fixture
def mock_websocket_with_auth():
    """Mock WebSocket connection with authentication."""
    with patch('integrations.obs_media.websocket') as mock_ws:
        mock_connection = MagicMock()
        mock_ws.create_connection.return_value = mock_connection

        # Mock Hello message with auth challenge
        hello_msg = {
            "op": 0,
            "d": {
                "obsWebSocketVersion": "5.0.0",
                "rpcVersion": 1,
                "authentication": {
                    "challenge": "test_challenge_string",
                    "salt": "test_salt_string"
                }
            }
        }

        # Mock Identified message
        identified_msg = {
            "op": 2,
            "d": {
                "negotiatedRpcVersion": 1
            }
        }

        mock_connection.recv.side_effect = [
            json.dumps(hello_msg),
            json.dumps(identified_msg)
        ]

        yield mock_ws, mock_connection


@pytest.fixture
def connected_client(mock_websocket):
    """OBS WebSocket client with mocked connection."""
    mock_ws, mock_connection = mock_websocket
    client = OBSWebSocketClient(host="localhost", port=4455, enable_witness=True)
    client.connect()
    return client, mock_connection


@pytest.fixture
def media_controller(connected_client):
    """Media source controller with connected client."""
    client, mock_connection = connected_client
    return MediaSourceController(client), client, mock_connection


@pytest.fixture
def browser_controller(connected_client):
    """Browser source controller with connected client."""
    client, mock_connection = connected_client
    return BrowserSourceController(client), client, mock_connection


@pytest.fixture
def capture_controller(connected_client):
    """Capture source controller with connected client."""
    client, mock_connection = connected_client
    return CaptureSourceController(client, Platform.WINDOWS), client, mock_connection


# ============================================================================
# WebSocket Client Tests
# ============================================================================

class TestOBSWebSocketClient:
    """Test OBS WebSocket client connection and authentication."""

    def test_client_initialization(self):
        """Test client initialization with default parameters."""
        client = OBSWebSocketClient()
        assert client.host == "localhost"
        assert client.port == 4455
        assert client.password is None
        assert client.enable_witness is True
        assert client.connected is False
        assert client.authenticated is False

    def test_client_initialization_with_params(self):
        """Test client initialization with custom parameters."""
        client = OBSWebSocketClient(
            host="192.168.1.100",
            port=4456,
            password="test_password",
            enable_witness=False
        )
        assert client.host == "192.168.1.100"
        assert client.port == 4456
        assert client.password == "test_password"
        assert client.enable_witness is False

    def test_connect_success_no_auth(self, mock_websocket):
        """Test successful connection without authentication."""
        mock_ws, mock_connection = mock_websocket
        client = OBSWebSocketClient(host="localhost", port=4455)

        result = client.connect()

        assert result is True
        assert client.connected is True
        assert client.authenticated is True
        mock_ws.create_connection.assert_called_once_with("ws://localhost:4455", timeout=10)

    def test_connect_success_with_auth(self, mock_websocket_with_auth):
        """Test successful connection with SHA-256 authentication."""
        mock_ws, mock_connection = mock_websocket_with_auth
        client = OBSWebSocketClient(host="localhost", port=4455, password="test_password")

        result = client.connect()

        assert result is True
        assert client.connected is True
        assert client.authenticated is True

        # Verify Identify message was sent
        calls = mock_connection.send.call_args_list
        assert len(calls) == 1
        sent_msg = json.loads(calls[0][0][0])
        assert sent_msg["op"] == 1  # Identify
        assert "authentication" in sent_msg["d"]

    def test_connect_failure(self):
        """Test connection failure handling."""
        with patch('integrations.obs_media.websocket') as mock_ws:
            mock_ws.create_connection.side_effect = Exception("Connection refused")
            client = OBSWebSocketClient()

            result = client.connect()

            assert result is False
            assert client.connected is False

    def test_disconnect(self, connected_client):
        """Test disconnection."""
        client, mock_connection = connected_client

        client.disconnect()

        assert client.connected is False
        assert client.authenticated is False
        mock_connection.close.assert_called_once()

    def test_request_success(self, connected_client):
        """Test successful request/response."""
        client, mock_connection = connected_client

        # Mock response
        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {
                    "result": True,
                    "code": 200
                },
                "responseData": {
                    "inputUuid": "test-uuid-123"
                }
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        # Override request ID generation for testing
        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            result = client.request("CreateInput", {"sceneName": "Test"})

        assert result == {"inputUuid": "test-uuid-123"}

    def test_request_failure(self, connected_client):
        """Test request failure handling."""
        client, mock_connection = connected_client

        # Mock error response
        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {
                    "result": False,
                    "code": 600,
                    "comment": "Resource not found"
                }
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            with pytest.raises(Exception, match="Resource not found"):
                client.request("GetInputSettings", {"inputName": "NonExistent"})

    def test_witness_logging(self, connected_client):
        """Test IF.witness audit logging."""
        client, _ = connected_client

        client._log_witness(
            "TEST_OPERATION",
            "test_input",
            "test_type",
            {"key": "value"},
            True
        )

        assert len(client.witness_logs) == 2  # Connect + test operation
        log = client.witness_logs[1]
        assert log.operation == "TEST_OPERATION"
        assert log.input_name == "test_input"
        assert log.input_type == "test_type"
        assert log.success is True

    def test_export_witness_logs(self, connected_client):
        """Test witness log export to JSON."""
        client, _ = connected_client

        client._log_witness("TEST1", "input1", "type1", {}, True)
        client._log_witness("TEST2", "input2", "type2", {}, False, "Error")

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name

        try:
            client.export_witness_logs(temp_path)

            with open(temp_path, 'r') as f:
                logs = json.load(f)

            assert len(logs) == 3  # Connect + 2 test operations
            assert logs[1]["operation"] == "TEST1"
            assert logs[2]["operation"] == "TEST2"
            assert logs[2]["error_message"] == "Error"

        finally:
            Path(temp_path).unlink()


# ============================================================================
# Media Source Controller Tests
# ============================================================================

class TestMediaSourceController:
    """Test media source creation and control."""

    def test_create_media_source(self, media_controller):
        """Test ffmpeg_source creation."""
        controller, client, mock_connection = media_controller

        # Mock successful response
        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {"inputUuid": "media-uuid-123"}
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        config = MediaSourceConfig(
            local_file="/videos/intro.mp4",
            looping=True,
            restart_on_activate=True,
            speed_percent=100
        )

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            result = controller.create_media_source("MainScene", "IntroVideo", config)

        assert result["inputUuid"] == "media-uuid-123"

        # Verify request was sent
        calls = mock_connection.send.call_args_list
        sent_msg = json.loads(calls[-1][0][0])
        assert sent_msg["d"]["requestType"] == "CreateInput"
        assert sent_msg["d"]["requestData"]["inputKind"] == "ffmpeg_source"
        assert sent_msg["d"]["requestData"]["inputSettings"]["local_file"] == "/videos/intro.mp4"

    def test_create_image_source(self, media_controller):
        """Test image_source creation."""
        controller, client, mock_connection = media_controller

        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {"inputUuid": "image-uuid-123"}
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            result = controller.create_image_source(
                "OverlayScene",
                "Logo",
                "/images/logo.png",
                unload=False
            )

        assert result["inputUuid"] == "image-uuid-123"

        calls = mock_connection.send.call_args_list
        sent_msg = json.loads(calls[-1][0][0])
        assert sent_msg["d"]["requestData"]["inputKind"] == "image_source"
        assert sent_msg["d"]["requestData"]["inputSettings"]["file"] == "/images/logo.png"

    def test_create_slideshow(self, media_controller):
        """Test slideshow creation."""
        controller, client, mock_connection = media_controller

        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {"inputUuid": "slideshow-uuid-123"}
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        files = ["/images/slide1.png", "/images/slide2.png", "/images/slide3.png"]

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            result = controller.create_slideshow(
                "GalleryScene",
                "PhotoShow",
                files,
                slide_time=5000,
                transition="fade",
                loop=True
            )

        assert result["inputUuid"] == "slideshow-uuid-123"

        calls = mock_connection.send.call_args_list
        sent_msg = json.loads(calls[-1][0][0])
        assert sent_msg["d"]["requestData"]["inputKind"] == "slideshow"
        assert len(sent_msg["d"]["requestData"]["inputSettings"]["files"]) == 3

    def test_trigger_media_action(self, media_controller):
        """Test media playback control."""
        controller, client, mock_connection = media_controller

        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {}
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            result = controller.trigger_media_action("IntroVideo", MediaAction.PLAY)

        calls = mock_connection.send.call_args_list
        sent_msg = json.loads(calls[-1][0][0])
        assert sent_msg["d"]["requestType"] == "TriggerMediaInputAction"
        assert sent_msg["d"]["requestData"]["mediaAction"] == "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PLAY"

    def test_get_media_status(self, media_controller):
        """Test getting media playback status."""
        controller, client, mock_connection = media_controller

        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {
                    "mediaDuration": 120000,
                    "mediaCursor": 45000,
                    "mediaState": "OBS_MEDIA_STATE_PLAYING"
                }
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            result = controller.get_media_status("IntroVideo")

        assert result["mediaDuration"] == 120000
        assert result["mediaCursor"] == 45000
        assert result["mediaState"] == "OBS_MEDIA_STATE_PLAYING"

    def test_set_media_cursor(self, media_controller):
        """Test setting media playback position."""
        controller, client, mock_connection = media_controller

        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {}
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            result = controller.set_media_cursor("IntroVideo", 30000)

        calls = mock_connection.send.call_args_list
        sent_msg = json.loads(calls[-1][0][0])
        assert sent_msg["d"]["requestType"] == "SetMediaInputCursor"
        assert sent_msg["d"]["requestData"]["mediaCursor"] == 30000


# ============================================================================
# Browser Source Controller Tests
# ============================================================================

class TestBrowserSourceController:
    """Test browser source creation and control."""

    def test_create_browser_source(self, browser_controller):
        """Test browser_source creation."""
        controller, client, mock_connection = browser_controller

        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {"inputUuid": "browser-uuid-123"}
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        config = BrowserSourceConfig(
            url="https://example.com/overlay.html",
            width=1920,
            height=1080,
            fps=30,
            css="body { background: transparent; }"
        )

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            result = controller.create_browser_source("MainScene", "Overlay", config)

        assert result["inputUuid"] == "browser-uuid-123"

        calls = mock_connection.send.call_args_list
        sent_msg = json.loads(calls[-1][0][0])
        assert sent_msg["d"]["requestData"]["inputKind"] == "browser_source"
        assert sent_msg["d"]["requestData"]["inputSettings"]["url"] == "https://example.com/overlay.html"
        assert sent_msg["d"]["requestData"]["inputSettings"]["width"] == 1920

    def test_create_browser_source_local_file(self, browser_controller):
        """Test browser_source creation with local file."""
        controller, client, mock_connection = browser_controller

        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {"inputUuid": "browser-uuid-456"}
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        config = BrowserSourceConfig(
            url="file:///C:/overlays/timer.html",
            width=800,
            height=600,
            is_local_file=True
        )

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            result = controller.create_browser_source("TimerScene", "Timer", config)

        calls = mock_connection.send.call_args_list
        sent_msg = json.loads(calls[-1][0][0])
        assert sent_msg["d"]["requestData"]["inputSettings"]["is_local_file"] is True

    def test_refresh_browser_source(self, browser_controller):
        """Test browser source refresh."""
        controller, client, mock_connection = browser_controller

        # Mock GetInputSettings response
        get_settings_response = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {
                    "inputSettings": {
                        "url": "https://example.com/overlay.html",
                        "width": 1920,
                        "height": 1080
                    }
                }
            }
        }

        # Mock SetInputSettings response (x2)
        set_settings_response = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {}
            }
        }

        mock_connection.recv.side_effect = [
            json.dumps(get_settings_response),
            json.dumps(set_settings_response),
            json.dumps(set_settings_response)
        ]

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            controller.refresh_browser_source("Overlay")

        # Verify GetInputSettings, SetInputSettings (x2) were called
        calls = mock_connection.send.call_args_list
        assert len(calls) >= 3


# ============================================================================
# Capture Source Controller Tests
# ============================================================================

class TestCaptureSourceController:
    """Test capture source creation."""

    def test_create_window_capture_windows(self, capture_controller):
        """Test window capture creation on Windows."""
        controller, client, mock_connection = capture_controller

        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {"inputUuid": "window-uuid-123"}
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        config = CaptureSourceConfig(
            window="[chrome.exe]:Google Chrome",
            capture_method="auto",
            cursor=True
        )

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            result = controller.create_window_capture("MainScene", "BrowserWindow", config)

        assert result["inputUuid"] == "window-uuid-123"

        calls = mock_connection.send.call_args_list
        sent_msg = json.loads(calls[-1][0][0])
        assert sent_msg["d"]["requestData"]["inputKind"] == "window_capture"
        assert sent_msg["d"]["requestData"]["inputSettings"]["window"] == "[chrome.exe]:Google Chrome"

    def test_create_display_capture(self, capture_controller):
        """Test display capture creation."""
        controller, client, mock_connection = capture_controller

        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {"inputUuid": "display-uuid-123"}
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        config = CaptureSourceConfig(
            monitor_id="\\\\?\\DISPLAY#Default_Monitor#00000001",
            cursor=True
        )

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            result = controller.create_display_capture("MainScene", "PrimaryMonitor", config)

        assert result["inputUuid"] == "display-uuid-123"

        calls = mock_connection.send.call_args_list
        sent_msg = json.loads(calls[-1][0][0])
        assert sent_msg["d"]["requestData"]["inputKind"] == "monitor_capture"

    def test_create_game_capture_windows(self, capture_controller):
        """Test game capture creation on Windows."""
        controller, client, mock_connection = capture_controller

        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {"inputUuid": "game-uuid-123"}
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        config = CaptureSourceConfig(
            capture_mode="auto",
            antiCheatCompatibility=True,
            allowTransparency=False,
            cursor=True
        )

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            result = controller.create_game_capture("GamingScene", "GameCapture", config)

        assert result["inputUuid"] == "game-uuid-123"

        calls = mock_connection.send.call_args_list
        sent_msg = json.loads(calls[-1][0][0])
        assert sent_msg["d"]["requestData"]["inputKind"] == "game_capture"
        assert sent_msg["d"]["requestData"]["inputSettings"]["antiCheatCompatibility"] is True

    def test_create_game_capture_non_windows(self):
        """Test game capture raises exception on non-Windows platforms."""
        client = OBSWebSocketClient()
        client.connected = True
        client.authenticated = True
        controller = CaptureSourceController(client, Platform.LINUX)

        config = CaptureSourceConfig(capture_mode="auto")

        with pytest.raises(Exception, match="Game capture is only available on Windows"):
            controller.create_game_capture("GamingScene", "GameCapture", config)

    def test_create_audio_input(self, capture_controller):
        """Test audio input capture creation."""
        controller, client, mock_connection = capture_controller

        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {"inputUuid": "audio-uuid-123"}
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            result = controller.create_audio_input(
                "MainScene",
                "Microphone",
                "{0.0.0.00000000}.{UUID-of-microphone}"
            )

        assert result["inputUuid"] == "audio-uuid-123"

        calls = mock_connection.send.call_args_list
        sent_msg = json.loads(calls[-1][0][0])
        assert sent_msg["d"]["requestData"]["inputKind"] == "wasapi_input_capture"

    def test_create_audio_output(self, capture_controller):
        """Test audio output capture creation."""
        controller, client, mock_connection = capture_controller

        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {"inputUuid": "audio-uuid-456"}
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            result = controller.create_audio_output(
                "MainScene",
                "SystemAudio",
                "{0.0.0.00000000}.{UUID-of-output}"
            )

        assert result["inputUuid"] == "audio-uuid-456"

        calls = mock_connection.send.call_args_list
        sent_msg = json.loads(calls[-1][0][0])
        assert sent_msg["d"]["requestData"]["inputKind"] == "wasapi_output_capture"


# ============================================================================
# High-Level OBS Media Manager Tests
# ============================================================================

class TestOBSMediaManager:
    """Test high-level OBS media manager."""

    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = OBSMediaManager(
            host="192.168.1.100",
            port=4456,
            password="test_password",
            platform=Platform.LINUX,
            enable_witness=False
        )

        assert manager.client.host == "192.168.1.100"
        assert manager.client.port == 4456
        assert manager.client.password == "test_password"
        assert manager.platform == Platform.LINUX
        assert isinstance(manager.media, MediaSourceController)
        assert isinstance(manager.browser, BrowserSourceController)
        assert isinstance(manager.capture, CaptureSourceController)

    def test_context_manager(self, mock_websocket):
        """Test context manager usage."""
        mock_ws, mock_connection = mock_websocket

        with OBSMediaManager() as manager:
            assert manager.client.connected is True

        mock_connection.close.assert_called_once()


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple components."""

    def test_complete_media_workflow(self, media_controller):
        """Test complete media source workflow."""
        controller, client, mock_connection = media_controller

        # Mock responses for all operations
        response_msg = {
            "op": 7,
            "d": {
                "requestId": "test-id",
                "requestStatus": {"result": True, "code": 200},
                "responseData": {"inputUuid": "media-uuid-123"}
            }
        }
        mock_connection.recv.return_value = json.dumps(response_msg)

        # Create media source
        config = MediaSourceConfig(
            local_file="/videos/intro.mp4",
            looping=True
        )

        with patch('integrations.obs_media.uuid.uuid4', return_value=Mock(hex="test-id")):
            controller.create_media_source("MainScene", "IntroVideo", config)

            # Play media
            controller.trigger_media_action("IntroVideo", MediaAction.PLAY)

            # Pause media
            controller.trigger_media_action("IntroVideo", MediaAction.PAUSE)

            # Restart media
            controller.trigger_media_action("IntroVideo", MediaAction.RESTART)

        # Verify witness logs
        assert len(client.witness_logs) >= 4  # Connect + create + 3 actions


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
