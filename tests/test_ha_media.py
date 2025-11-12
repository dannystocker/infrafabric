"""
Comprehensive test suite for Home Assistant Media Integration

Tests cover:
- Connection and authentication
- Media player state management
- Playback control (play, pause, stop, navigation)
- Volume control
- TTS services (multiple providers)
- Media source browsing
- Multi-room audio grouping
- IF.witness audit logging
- Error handling and edge cases

Author: InfraFabric Project
License: CC BY 4.0
Last Updated: 2025-11-12
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

# Import module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from integrations.ha_media import (
    HAMediaIntegration,
    HAConnection,
    HARestClient,
    MediaPlayerState,
    MediaPlayerAttributes,
    TTSRequest,
    MediaPlayRequest,
    TTSProvider,
    WitnessLogger,
    create_connection,
    create_tts_request,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_connection():
    """Mock Home Assistant connection"""
    return HAConnection(
        base_url="http://homeassistant.local:8123",
        access_token="test_token_123",
        verify_ssl=False
    )


@pytest.fixture
def temp_log_dir():
    """Temporary directory for test logs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_requests():
    """Mock requests library"""
    with patch('integrations.ha_media.requests') as mock_req:
        yield mock_req


@pytest.fixture
def ha_integration(mock_connection, temp_log_dir):
    """HAMediaIntegration instance with mocked dependencies"""
    with patch('integrations.ha_media.REQUESTS_AVAILABLE', True):
        integration = HAMediaIntegration(mock_connection, temp_log_dir)
        return integration


# ============================================================================
# Connection Tests
# ============================================================================

class TestHAConnection:
    """Test Home Assistant connection configuration"""

    def test_create_connection(self):
        """Test connection creation helper"""
        conn = create_connection(
            "http://homeassistant.local:8123",
            "my_token",
            verify_ssl=True
        )

        assert conn.base_url == "http://homeassistant.local:8123"
        assert conn.access_token == "my_token"
        assert conn.verify_ssl is True
        assert conn.timeout == 10

    def test_connection_defaults(self):
        """Test connection default values"""
        conn = HAConnection(
            base_url="http://ha.local",
            access_token="token"
        )

        assert conn.verify_ssl is True
        assert conn.timeout == 10


# ============================================================================
# REST Client Tests
# ============================================================================

class TestHARestClient:
    """Test REST API client"""

    def test_get_state_success(self, mock_connection, mock_requests):
        """Test successful state retrieval"""
        with patch('integrations.ha_media.REQUESTS_AVAILABLE', True):
            client = HARestClient(mock_connection)

            # Mock response
            mock_response = Mock()
            mock_response.json.return_value = {
                "entity_id": "media_player.test",
                "state": "playing",
                "attributes": {"volume_level": 0.5}
            }
            mock_response.raise_for_status = Mock()
            mock_requests.get.return_value = mock_response

            # Test
            state = client.get_state("media_player.test")

            assert state["entity_id"] == "media_player.test"
            assert state["state"] == "playing"
            mock_requests.get.assert_called_once()

    def test_call_service_success(self, mock_connection, mock_requests):
        """Test successful service call"""
        with patch('integrations.ha_media.REQUESTS_AVAILABLE', True):
            client = HARestClient(mock_connection)

            # Mock response
            mock_response = Mock()
            mock_response.json.return_value = [{"state": "ok"}]
            mock_response.raise_for_status = Mock()
            mock_requests.post.return_value = mock_response

            # Test
            data = {"entity_id": "media_player.test"}
            result = client.call_service("media_player", "play", data)

            assert result == [{"state": "ok"}]
            mock_requests.post.assert_called_once()

    def test_authentication_headers(self, mock_connection):
        """Test authentication headers are set correctly"""
        with patch('integrations.ha_media.REQUESTS_AVAILABLE', True):
            client = HARestClient(mock_connection)

            assert "Authorization" in client.headers
            assert client.headers["Authorization"] == "Bearer test_token_123"
            assert client.headers["Content-Type"] == "application/json"


# ============================================================================
# Media Player State Tests
# ============================================================================

class TestMediaPlayerState:
    """Test media player state management"""

    def test_get_media_player_state(self, ha_integration, mock_requests):
        """Test retrieving media player state"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "entity_id": "media_player.living_room",
            "state": "playing",
            "attributes": {
                "volume_level": 0.5,
                "is_volume_muted": False,
                "media_title": "Test Song",
                "media_artist": "Test Artist",
                "media_duration": 240,
                "media_position": 60,
                "supported_features": 720429
            }
        }
        mock_response.raise_for_status = Mock()
        mock_requests.get.return_value = mock_response

        # Test
        state = ha_integration.get_media_player_state("media_player.living_room")

        assert state.entity_id == "media_player.living_room"
        assert state.state == MediaPlayerState.PLAYING
        assert state.volume_level == 0.5
        assert state.media_title == "Test Song"
        assert state.media_artist == "Test Artist"
        assert state.media_duration == 240

    def test_get_all_media_players(self, ha_integration, mock_requests):
        """Test retrieving all media player entities"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"entity_id": "media_player.living_room", "state": "playing"},
            {"entity_id": "media_player.bedroom", "state": "idle"},
            {"entity_id": "light.kitchen", "state": "on"},  # Not a media player
        ]
        mock_response.raise_for_status = Mock()
        mock_requests.get.return_value = mock_response

        # Test
        players = ha_integration.get_all_media_players()

        assert len(players) == 2
        assert "media_player.living_room" in players
        assert "media_player.bedroom" in players
        assert "light.kitchen" not in players


# ============================================================================
# Playback Control Tests
# ============================================================================

class TestPlaybackControl:
    """Test media playback control"""

    def test_play_media(self, ha_integration, mock_requests):
        """Test playing media"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        request = MediaPlayRequest(
            entity_id="media_player.test",
            media_content_id="spotify:track:123",
            media_content_type="music"
        )

        result = ha_integration.play_media(request)
        assert result is True

    def test_play_media_with_enqueue(self, ha_integration, mock_requests):
        """Test queueing media"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        request = MediaPlayRequest(
            entity_id="media_player.test",
            media_content_id="spotify:track:123",
            media_content_type="music",
            enqueue=True
        )

        result = ha_integration.play_media(request)
        assert result is True

    def test_pause(self, ha_integration, mock_requests):
        """Test pausing playback"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.pause("media_player.test")
        assert result is True

    def test_play(self, ha_integration, mock_requests):
        """Test resuming playback"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.play("media_player.test")
        assert result is True

    def test_stop(self, ha_integration, mock_requests):
        """Test stopping playback"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.stop("media_player.test")
        assert result is True

    def test_play_pause_toggle(self, ha_integration, mock_requests):
        """Test play/pause toggle"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.play_pause("media_player.test")
        assert result is True


# ============================================================================
# Volume Control Tests
# ============================================================================

class TestVolumeControl:
    """Test volume control"""

    def test_volume_set(self, ha_integration, mock_requests):
        """Test setting volume level"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.volume_set("media_player.test", 0.75)
        assert result is True

    def test_volume_set_invalid_range(self, ha_integration):
        """Test volume validation"""
        with pytest.raises(ValueError, match="volume_level must be between"):
            ha_integration.volume_set("media_player.test", 1.5)

        with pytest.raises(ValueError, match="volume_level must be between"):
            ha_integration.volume_set("media_player.test", -0.1)

    def test_volume_up(self, ha_integration, mock_requests):
        """Test increasing volume"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.volume_up("media_player.test")
        assert result is True

    def test_volume_down(self, ha_integration, mock_requests):
        """Test decreasing volume"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.volume_down("media_player.test")
        assert result is True

    def test_volume_mute(self, ha_integration, mock_requests):
        """Test muting volume"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.volume_mute("media_player.test", True)
        assert result is True


# ============================================================================
# Track Navigation Tests
# ============================================================================

class TestTrackNavigation:
    """Test track navigation"""

    def test_next_track(self, ha_integration, mock_requests):
        """Test skipping to next track"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.next_track("media_player.test")
        assert result is True

    def test_previous_track(self, ha_integration, mock_requests):
        """Test skipping to previous track"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.previous_track("media_player.test")
        assert result is True


# ============================================================================
# Source & Mode Tests
# ============================================================================

class TestSourceAndMode:
    """Test source and mode selection"""

    def test_select_source(self, ha_integration, mock_requests):
        """Test selecting input source"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.select_source("media_player.test", "Spotify")
        assert result is True

    def test_shuffle_set(self, ha_integration, mock_requests):
        """Test setting shuffle mode"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.shuffle_set("media_player.test", True)
        assert result is True

    def test_repeat_set(self, ha_integration, mock_requests):
        """Test setting repeat mode"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.repeat_set("media_player.test", "all")
        assert result is True

    def test_repeat_set_invalid(self, ha_integration):
        """Test invalid repeat mode"""
        with pytest.raises(ValueError, match="repeat must be"):
            ha_integration.repeat_set("media_player.test", "invalid")


# ============================================================================
# Multi-room Audio Tests
# ============================================================================

class TestMultiRoomAudio:
    """Test multi-room audio grouping"""

    def test_join_players(self, ha_integration, mock_requests):
        """Test grouping media players"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.join_players(
            "media_player.living_room",
            ["media_player.kitchen", "media_player.bedroom"]
        )
        assert result is True

    def test_unjoin_player(self, ha_integration, mock_requests):
        """Test ungrouping media player"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.unjoin_player("media_player.bedroom")
        assert result is True


# ============================================================================
# TTS Tests
# ============================================================================

class TestTTS:
    """Test text-to-speech services"""

    def test_tts_speak_basic(self, ha_integration, mock_requests):
        """Test basic TTS speak"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        request = TTSRequest(
            message="Hello world",
            entity_id="tts.google_cloud",
            media_player_entity_id="media_player.test",
            language="en-US"
        )

        result = ha_integration.tts_speak(request)
        assert result is True

    def test_tts_speak_with_options(self, ha_integration, mock_requests):
        """Test TTS with provider options"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        request = TTSRequest(
            message="Hello world",
            entity_id="tts.google_cloud",
            media_player_entity_id="media_player.test",
            language="en-US",
            cache=True,
            options={
                "voice": "en-US-Wavenet-F",
                "speed": 0.95,
                "pitch": 0.0
            }
        )

        result = ha_integration.tts_speak(request)
        assert result is True

    def test_tts_google_translate(self, ha_integration, mock_requests):
        """Test legacy Google Translate TTS"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.tts_google_translate(
            "media_player.test",
            "Hello world",
            "en"
        )
        assert result is True

    def test_tts_multiple_speakers(self, ha_integration, mock_requests):
        """Test TTS to multiple speakers"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        request = TTSRequest(
            message="Announcement",
            entity_id="tts.google_cloud",
            media_player_entity_id=[
                "media_player.living_room",
                "media_player.kitchen"
            ],
            language="en-US"
        )

        result = ha_integration.tts_speak(request)
        assert result is True

    def test_create_tts_request_helper(self):
        """Test TTS request creation helper"""
        request = create_tts_request(
            message="Test message",
            tts_entity="tts.google_cloud",
            speaker="media_player.test",
            language="fr-FR",
            provider=TTSProvider.GOOGLE_CLOUD,
            voice="fr-FR-Wavenet-A",
            speed=1.0
        )

        assert request.message == "Test message"
        assert request.entity_id == "tts.google_cloud"
        assert request.language == "fr-FR"
        assert request.options["voice"] == "fr-FR-Wavenet-A"


# ============================================================================
# Media Source Tests
# ============================================================================

class TestMediaSource:
    """Test media source and streaming"""

    def test_play_url(self, ha_integration, mock_requests):
        """Test playing URL stream"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.play_url(
            "media_player.test",
            "http://stream.example.com/radio.mp3"
        )
        assert result is True

    def test_play_local_media(self, ha_integration, mock_requests):
        """Test playing local media file"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.play_local_media(
            "media_player.test",
            "Music/Artist/song.mp3"
        )
        assert result is True

    def test_play_radio_station(self, ha_integration, mock_requests):
        """Test playing radio station"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.play_radio_station(
            "media_player.test",
            "BBC Radio 1"
        )
        assert result is True


# ============================================================================
# Power Control Tests
# ============================================================================

class TestPowerControl:
    """Test power control"""

    def test_turn_on(self, ha_integration, mock_requests):
        """Test turning on media player"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.turn_on("media_player.test")
        assert result is True

    def test_turn_off(self, ha_integration, mock_requests):
        """Test turning off media player"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        result = ha_integration.turn_off("media_player.test")
        assert result is True


# ============================================================================
# IF.witness Logging Tests
# ============================================================================

class TestWitnessLogging:
    """Test IF.witness audit logging"""

    def test_witness_logger_creation(self, temp_log_dir):
        """Test witness logger initialization"""
        logger = WitnessLogger(temp_log_dir)
        assert logger.log_dir == temp_log_dir
        assert logger.log_dir.exists()

    def test_command_logging(self, ha_integration, mock_requests, temp_log_dir):
        """Test command logging to witness log"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        # Execute command
        ha_integration.play("media_player.test")

        # Check log file created
        log_files = list(temp_log_dir.glob("ha_media_*.jsonl"))
        assert len(log_files) == 1

        # Verify log content
        with open(log_files[0], 'r') as f:
            log_entry = json.loads(f.readline())

        assert log_entry["operation"] == "play"
        assert log_entry["entity_id"] == "media_player.test"
        assert log_entry["success"] is True
        assert "witness_hash" in log_entry
        assert "command_hash" in log_entry

    def test_error_logging(self, ha_integration, mock_requests, temp_log_dir):
        """Test error logging to witness log"""
        mock_requests.post.side_effect = Exception("Connection error")

        # Execute command (should fail)
        with pytest.raises(Exception):
            ha_integration.play("media_player.test")

        # Check error logged
        log_files = list(temp_log_dir.glob("ha_media_*.jsonl"))
        assert len(log_files) == 1

        with open(log_files[0], 'r') as f:
            log_entry = json.loads(f.readline())

        assert log_entry["success"] is False
        assert "error" in log_entry
        assert "Connection error" in log_entry["error"]

    def test_get_witness_logs(self, ha_integration, mock_requests):
        """Test retrieving witness logs"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        # Create some log entries
        ha_integration.play("media_player.test")
        ha_integration.pause("media_player.test")

        # Retrieve logs
        logs = ha_integration.get_witness_logs()

        assert len(logs) == 2
        assert logs[0]["operation"] == "play"
        assert logs[1]["operation"] == "pause"

    def test_verify_command_integrity(self, ha_integration, mock_requests):
        """Test command integrity verification"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        # Create log entry
        ha_integration.play("media_player.test")

        # Retrieve and verify
        logs = ha_integration.get_witness_logs()
        assert len(logs) == 1

        # Should verify successfully
        is_valid = ha_integration.verify_command_integrity(logs[0].copy())
        assert is_valid is True

    def test_tampered_log_detection(self, ha_integration, mock_requests):
        """Test detection of tampered logs"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        # Create log entry
        ha_integration.play("media_player.test")

        # Retrieve and tamper
        logs = ha_integration.get_witness_logs()
        tampered_log = logs[0].copy()
        tampered_log["entity_id"] = "media_player.hacked"

        # Should fail verification
        is_valid = ha_integration.verify_command_integrity(tampered_log)
        assert is_valid is False


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling"""

    def test_invalid_entity_id(self, ha_integration, mock_requests):
        """Test handling of invalid entity ID"""
        mock_requests.get.side_effect = Exception("404 Not Found")

        with pytest.raises(Exception):
            ha_integration.get_media_player_state("media_player.invalid")

    def test_network_error(self, ha_integration, mock_requests):
        """Test handling of network errors"""
        mock_requests.post.side_effect = Exception("Connection timeout")

        with pytest.raises(Exception):
            ha_integration.play("media_player.test")

    def test_authentication_error(self, mock_connection, mock_requests):
        """Test handling of authentication errors"""
        mock_requests.get.side_effect = Exception("401 Unauthorized")

        with patch('integrations.ha_media.REQUESTS_AVAILABLE', True):
            client = HARestClient(mock_connection)

            with pytest.raises(Exception):
                client.get_state("media_player.test")


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegrationScenarios:
    """Test complete integration scenarios"""

    def test_morning_routine(self, ha_integration, mock_requests):
        """Test morning routine scenario: TTS + Radio"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        # Turn on speaker
        ha_integration.turn_on("media_player.bedroom")

        # Set volume
        ha_integration.volume_set("media_player.bedroom", 0.3)

        # TTS announcement
        tts_request = TTSRequest(
            message="Good morning, it's 7 AM",
            entity_id="tts.google_cloud",
            media_player_entity_id="media_player.bedroom",
            language="en-US"
        )
        ha_integration.tts_speak(tts_request)

        # Play radio after announcement
        ha_integration.play_radio_station("media_player.bedroom", "BBC Radio 1")

        # Verify all commands logged
        logs = ha_integration.get_witness_logs()
        assert len(logs) == 4

    def test_multi_room_party_mode(self, ha_integration, mock_requests):
        """Test multi-room party mode scenario"""
        mock_response = Mock()
        mock_response.json.return_value = [{"state": "ok"}]
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        # Group speakers
        ha_integration.join_players(
            "media_player.living_room",
            ["media_player.kitchen", "media_player.bedroom"]
        )

        # Set volume on all
        ha_integration.volume_set("media_player.living_room", 0.6)

        # Enable shuffle
        ha_integration.shuffle_set("media_player.living_room", True)

        # Play playlist
        request = MediaPlayRequest(
            entity_id="media_player.living_room",
            media_content_id="spotify:playlist:party_mix",
            media_content_type="playlist"
        )
        ha_integration.play_media(request)

        logs = ha_integration.get_witness_logs()
        assert len(logs) == 4


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
