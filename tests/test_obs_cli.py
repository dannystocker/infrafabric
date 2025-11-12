"""
Unit tests for IF.obs CLI

Tests for OBS WebSocket client, config management, and CLI commands.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from obs.models import (
    OBSInstance, OBSScene, OBSSource, OBSStreamStatus,
    OBSRecordStatus, OBSStats, OBSVersion, OBSFilter
)
from obs.config import OBSConfig, OBSConfigError
from obs.client import OBSClient, OBSError, OBSConnectionError, OBSAPIError


# ============================================================================
# Model Tests
# ============================================================================

class TestOBSModels:
    """Test OBS data models"""

    def test_obs_instance_creation(self):
        """Test OBSInstance creation"""
        instance = OBSInstance(
            name="test",
            host="localhost",
            port=4455,
            password="secret"
        )

        assert instance.name == "test"
        assert instance.host == "localhost"
        assert instance.port == 4455
        assert instance.password == "secret"
        assert instance.added_at is not None
        assert instance.url == "ws://localhost:4455"

    def test_obs_instance_to_dict(self):
        """Test OBSInstance serialization"""
        instance = OBSInstance(
            name="test",
            host="localhost",
            port=4455,
            password="secret"
        )

        data = instance.to_dict()
        assert data['name'] == "test"
        assert data['host'] == "localhost"
        assert data['port'] == 4455
        assert data['password'] == "***"  # Password should be masked

    def test_obs_scene_creation(self):
        """Test OBSScene creation"""
        scene = OBSScene(
            name="Gaming Scene",
            index=0,
            is_current=True
        )

        assert scene.name == "Gaming Scene"
        assert scene.index == 0
        assert scene.is_current is True
        assert len(scene.sources) == 0

    def test_obs_source_creation(self):
        """Test OBSSource creation"""
        source = OBSSource(
            name="Webcam",
            type="v4l2_input",
            scene_item_id=1,
            scene_item_enabled=True
        )

        assert source.name == "Webcam"
        assert source.type == "v4l2_input"
        assert source.scene_item_id == 1
        assert source.scene_item_enabled is True

    def test_obs_stats_creation(self):
        """Test OBSStats creation"""
        stats = OBSStats(
            cpu_usage=25.5,
            memory_usage=512.0,
            available_disk_space=10000.0,
            active_fps=60.0,
            average_frame_render_time=16.7,
            render_skipped_frames=0,
            render_total_frames=3600,
            output_skipped_frames=0,
            output_total_frames=3600
        )

        assert stats.cpu_usage == 25.5
        assert stats.active_fps == 60.0
        assert stats.render_total_frames == 3600


# ============================================================================
# Config Tests
# ============================================================================

class TestOBSConfig:
    """Test OBS configuration management"""

    def test_create_config(self):
        """Test config file creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'obs' / 'instances.yaml'
            config = OBSConfig(config_path=config_path)

            assert config_path.exists()

    def test_add_instance(self):
        """Test adding an instance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'obs' / 'instances.yaml'
            config = OBSConfig(config_path=config_path)

            instance = config.add_instance(
                name="test",
                host="localhost",
                port=4455,
                password="secret123"
            )

            assert instance.name == "test"
            assert instance.host == "localhost"
            assert instance.port == 4455
            assert instance.password == "secret123"

    def test_add_duplicate_instance(self):
        """Test adding duplicate instance raises error"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'obs' / 'instances.yaml'
            config = OBSConfig(config_path=config_path)

            config.add_instance("test", "localhost", 4455)

            with pytest.raises(OBSConfigError, match="already exists"):
                config.add_instance("test", "localhost", 4455)

    def test_get_instance(self):
        """Test getting an instance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'obs' / 'instances.yaml'
            config = OBSConfig(config_path=config_path)

            config.add_instance("test", "localhost", 4455, "secret123")
            instance = config.get_instance("test")

            assert instance is not None
            assert instance.name == "test"
            assert instance.host == "localhost"
            assert instance.password == "secret123"

    def test_get_nonexistent_instance(self):
        """Test getting nonexistent instance returns None"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'obs' / 'instances.yaml'
            config = OBSConfig(config_path=config_path)

            instance = config.get_instance("nonexistent")
            assert instance is None

    def test_list_instances(self):
        """Test listing instances"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'obs' / 'instances.yaml'
            config = OBSConfig(config_path=config_path)

            config.add_instance("test1", "localhost", 4455)
            config.add_instance("test2", "192.168.1.100", 4455)

            instances = config.list_instances()

            assert len(instances) == 2
            assert instances[0].name == "test1"
            assert instances[1].name == "test2"

    def test_remove_instance(self):
        """Test removing an instance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'obs' / 'instances.yaml'
            config = OBSConfig(config_path=config_path)

            config.add_instance("test", "localhost", 4455)
            result = config.remove_instance("test")

            assert result is True
            assert config.get_instance("test") is None

    def test_remove_nonexistent_instance(self):
        """Test removing nonexistent instance returns False"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'obs' / 'instances.yaml'
            config = OBSConfig(config_path=config_path)

            result = config.remove_instance("nonexistent")
            assert result is False

    def test_update_instance(self):
        """Test updating an instance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'obs' / 'instances.yaml'
            config = OBSConfig(config_path=config_path)

            config.add_instance("test", "localhost", 4455)
            updated = config.update_instance("test", host="192.168.1.100", port=4456)

            assert updated is not None
            assert updated.host == "192.168.1.100"
            assert updated.port == 4456

    def test_password_encoding(self):
        """Test password encoding/decoding"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'obs' / 'instances.yaml'
            config = OBSConfig(config_path=config_path)

            config.add_instance("test", "localhost", 4455, "secret123")

            # Read raw config to verify encoding
            with open(config_path, 'r') as f:
                raw_config = yaml.safe_load(f)

            # Password should be encoded in file
            assert raw_config['instances']['test']['password'] != "secret123"

            # But should decode correctly when retrieved
            instance = config.get_instance("test")
            assert instance.password == "secret123"


# ============================================================================
# Client Tests
# ============================================================================

class TestOBSClient:
    """Test OBS WebSocket client"""

    @patch('obs.client.HAS_OBS_WEBSOCKET', True)
    @patch('obs.client.obsws')
    def test_client_creation(self, mock_obsws):
        """Test OBSClient creation"""
        client = OBSClient("localhost", 4455, "password")

        assert client.host == "localhost"
        assert client.port == 4455
        assert client.password == "password"
        assert client._connected is False

    @patch('obs.client.HAS_OBS_WEBSOCKET', False)
    def test_client_requires_library(self):
        """Test client raises error if library not installed"""
        with pytest.raises(OBSError, match="obs-websocket-py is not installed"):
            client = OBSClient("localhost", 4455)

    @patch('obs.client.HAS_OBS_WEBSOCKET', True)
    @patch('obs.client.obsws')
    def test_connect(self, mock_obsws):
        """Test connecting to OBS"""
        mock_ws = Mock()
        mock_obsws.return_value = mock_ws

        client = OBSClient("localhost", 4455)
        client.connect()

        mock_obsws.assert_called_once_with("localhost", 4455, "", timeout=5)
        mock_ws.connect.assert_called_once()
        assert client._connected is True

    @patch('obs.client.HAS_OBS_WEBSOCKET', True)
    @patch('obs.client.obsws')
    def test_disconnect(self, mock_obsws):
        """Test disconnecting from OBS"""
        mock_ws = Mock()
        mock_obsws.return_value = mock_ws

        client = OBSClient("localhost", 4455)
        client.connect()
        client.disconnect()

        mock_ws.disconnect.assert_called_once()
        assert client._connected is False

    @patch('obs.client.HAS_OBS_WEBSOCKET', True)
    @patch('obs.client.obsws')
    def test_context_manager(self, mock_obsws):
        """Test using client as context manager"""
        mock_ws = Mock()
        mock_obsws.return_value = mock_ws

        with OBSClient("localhost", 4455) as client:
            assert client._connected is True

        mock_ws.connect.assert_called_once()
        mock_ws.disconnect.assert_called_once()

    @patch('obs.client.HAS_OBS_WEBSOCKET', True)
    @patch('obs.client.obsws')
    @patch('obs.client.obs_requests')
    def test_get_version(self, mock_requests, mock_obsws):
        """Test getting OBS version"""
        mock_ws = Mock()
        mock_obsws.return_value = mock_ws

        # Mock response
        mock_response = Mock()
        mock_response.datain = {
            'obsVersion': '30.0.0',
            'obsWebSocketVersion': '5.0.0',
            'rpcVersion': 1,
            'availableRequests': [],
            'supportedImageFormats': [],
            'platform': 'linux',
            'platformDescription': 'Linux'
        }
        mock_ws.call.return_value = mock_response

        client = OBSClient("localhost", 4455)
        client.connect()

        version = client.get_version()

        assert version.obs_version == '30.0.0'
        assert version.obs_web_socket_version == '5.0.0'
        assert version.platform == 'linux'

    @patch('obs.client.HAS_OBS_WEBSOCKET', True)
    @patch('obs.client.obsws')
    @patch('obs.client.obs_requests')
    def test_get_stats(self, mock_requests, mock_obsws):
        """Test getting OBS stats"""
        mock_ws = Mock()
        mock_obsws.return_value = mock_ws

        # Mock response
        mock_response = Mock()
        mock_response.datain = {
            'cpuUsage': 25.5,
            'memoryUsage': 512.0,
            'availableDiskSpace': 10000.0,
            'activeFps': 60.0,
            'averageFrameRenderTime': 16.7,
            'renderSkippedFrames': 0,
            'renderTotalFrames': 3600,
            'outputSkippedFrames': 0,
            'outputTotalFrames': 3600
        }
        mock_ws.call.return_value = mock_response

        client = OBSClient("localhost", 4455)
        client.connect()

        stats = client.get_stats()

        assert stats.cpu_usage == 25.5
        assert stats.active_fps == 60.0
        assert stats.render_total_frames == 3600

    @patch('obs.client.HAS_OBS_WEBSOCKET', True)
    @patch('obs.client.obsws')
    @patch('obs.client.obs_requests')
    def test_get_scene_list(self, mock_requests, mock_obsws):
        """Test getting scene list"""
        mock_ws = Mock()
        mock_obsws.return_value = mock_ws

        # Mock response
        mock_response = Mock()
        mock_response.datain = {
            'currentProgramSceneName': 'Gaming Scene',
            'scenes': [
                {'sceneName': 'Gaming Scene'},
                {'sceneName': 'BRB Scene'},
                {'sceneName': 'Ending Scene'}
            ]
        }
        mock_ws.call.return_value = mock_response

        client = OBSClient("localhost", 4455)
        client.connect()

        scenes = client.get_scene_list()

        assert len(scenes) == 3
        assert scenes[0].name == 'Gaming Scene'
        assert scenes[0].is_current is True
        assert scenes[1].is_current is False

    @patch('obs.client.HAS_OBS_WEBSOCKET', True)
    @patch('obs.client.obsws')
    @patch('obs.client.obs_requests')
    def test_get_stream_status(self, mock_requests, mock_obsws):
        """Test getting stream status"""
        mock_ws = Mock()
        mock_obsws.return_value = mock_ws

        # Mock response
        mock_response = Mock()
        mock_response.datain = {
            'outputActive': True,
            'outputReconnecting': False,
            'outputTimecode': '00:15:30',
            'outputDuration': 930000,
            'outputBytes': 1024000
        }
        mock_ws.call.return_value = mock_response

        client = OBSClient("localhost", 4455)
        client.connect()

        status = client.get_stream_status()

        assert status.active is True
        assert status.reconnecting is False
        assert status.timecode == '00:15:30'


# ============================================================================
# CLI Tests
# ============================================================================

class TestOBSCLI:
    """Test OBS CLI commands"""

    @patch('cli.obs_commands.OBSConfig')
    def test_add_instance_command(self, mock_config_class):
        """Test 'add' command"""
        from click.testing import CliRunner
        from cli.obs_commands import obs

        # Mock config
        mock_config = Mock()
        mock_instance = OBSInstance("test", "localhost", 4455)
        mock_config.add_instance.return_value = mock_instance
        mock_config_class.return_value = mock_config

        runner = CliRunner()
        result = runner.invoke(obs, ['add', 'test', '--host', 'localhost', '--port', '4455'])

        # Check command executed
        mock_config.add_instance.assert_called_once_with('test', 'localhost', 4455, None)

    @patch('cli.obs_commands.OBSConfig')
    def test_list_instances_command(self, mock_config_class):
        """Test 'list' command"""
        from click.testing import CliRunner
        from cli.obs_commands import obs

        # Mock config
        mock_config = Mock()
        mock_instances = [
            OBSInstance("test1", "localhost", 4455, added_at="2025-11-12T00:00:00Z"),
            OBSInstance("test2", "192.168.1.100", 4455, added_at="2025-11-12T01:00:00Z")
        ]
        mock_config.list_instances.return_value = mock_instances
        mock_config_class.return_value = mock_config

        runner = CliRunner()
        result = runner.invoke(obs, ['list'])

        assert result.exit_code == 0
        assert 'test1' in result.output
        assert 'test2' in result.output


# ============================================================================
# Integration Tests
# ============================================================================

class TestOBSIntegration:
    """Integration tests for complete workflows"""

    def test_full_config_workflow(self):
        """Test complete config management workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'obs' / 'instances.yaml'
            config = OBSConfig(config_path=config_path)

            # Add instance
            instance = config.add_instance("test", "localhost", 4455, "secret")
            assert instance.name == "test"

            # Get instance
            retrieved = config.get_instance("test")
            assert retrieved is not None
            assert retrieved.password == "secret"

            # List instances
            instances = config.list_instances()
            assert len(instances) == 1

            # Update instance
            updated = config.update_instance("test", host="192.168.1.100")
            assert updated.host == "192.168.1.100"

            # Remove instance
            result = config.remove_instance("test")
            assert result is True

            # Verify removal
            instances = config.list_instances()
            assert len(instances) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
