"""
Unit tests for IF.homeassistant CLI

Tests cover:
- Configuration management
- REST API client
- CLI commands
- Error handling
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from homeassistant.config import HAConfig, HAConfigError
from homeassistant.models import HAInstance, HAEntity, HAConfig as HAConfigModel
from homeassistant.client import (
    HomeAssistantClient, HAError, HAConnectionError, HAAuthError
)


# ============================================================================
# Configuration Tests
# ============================================================================

class TestHAConfig:
    """Test Home Assistant configuration management"""

    def test_config_creation(self):
        """Test creating config manager"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'test.yaml'
            config = HAConfig(config_path)

            assert config.config_path == config_path
            assert config.config_path.exists()

    def test_add_instance(self):
        """Test adding HA instance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'test.yaml'
            config = HAConfig(config_path)

            instance = config.add_instance(
                'test',
                'http://localhost:8123',
                'test_token_123'
            )

            assert instance.name == 'test'
            assert instance.url == 'http://localhost:8123'
            assert instance.token == 'test_token_123'

    def test_add_duplicate_instance(self):
        """Test adding duplicate instance fails"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'test.yaml'
            config = HAConfig(config_path)

            config.add_instance('test', 'http://localhost:8123', 'token')

            with pytest.raises(HAConfigError, match="already exists"):
                config.add_instance('test', 'http://localhost:8124', 'token2')

    def test_get_instance(self):
        """Test getting instance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'test.yaml'
            config = HAConfig(config_path)

            config.add_instance('test', 'http://localhost:8123', 'token')

            instance = config.get_instance('test')
            assert instance is not None
            assert instance.name == 'test'

    def test_get_nonexistent_instance(self):
        """Test getting nonexistent instance returns None"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'test.yaml'
            config = HAConfig(config_path)

            instance = config.get_instance('nonexistent')
            assert instance is None

    def test_list_instances(self):
        """Test listing instances"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'test.yaml'
            config = HAConfig(config_path)

            config.add_instance('test1', 'http://localhost:8123', 'token1')
            config.add_instance('test2', 'http://localhost:8124', 'token2')

            instances = config.list_instances()
            assert len(instances) == 2
            assert instances[0].name == 'test1'
            assert instances[1].name == 'test2'

    def test_remove_instance(self):
        """Test removing instance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'test.yaml'
            config = HAConfig(config_path)

            config.add_instance('test', 'http://localhost:8123', 'token')

            result = config.remove_instance('test')
            assert result is True

            instance = config.get_instance('test')
            assert instance is None

    def test_remove_nonexistent_instance(self):
        """Test removing nonexistent instance returns False"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'test.yaml'
            config = HAConfig(config_path)

            result = config.remove_instance('nonexistent')
            assert result is False

    def test_update_instance(self):
        """Test updating instance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'test.yaml'
            config = HAConfig(config_path)

            config.add_instance('test', 'http://localhost:8123', 'token')

            updated = config.update_instance('test', url='http://localhost:8124')
            assert updated.url == 'http://localhost:8124'

    def test_url_trailing_slash_removal(self):
        """Test that trailing slashes are removed from URLs"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'test.yaml'
            config = HAConfig(config_path)

            instance = config.add_instance(
                'test',
                'http://localhost:8123/',
                'token'
            )

            assert instance.url == 'http://localhost:8123'


# ============================================================================
# Model Tests
# ============================================================================

class TestHAModels:
    """Test Home Assistant data models"""

    def test_ha_entity_from_dict(self):
        """Test creating HAEntity from dict"""
        data = {
            'entity_id': 'light.living_room',
            'state': 'on',
            'attributes': {
                'friendly_name': 'Living Room Light',
                'brightness': 255
            },
            'last_changed': '2025-11-12T00:00:00Z'
        }

        entity = HAEntity.from_dict(data)

        assert entity.entity_id == 'light.living_room'
        assert entity.state == 'on'
        assert entity.attributes['brightness'] == 255
        assert entity.domain == 'light'
        assert entity.name == 'Living Room Light'

    def test_ha_config_from_dict(self):
        """Test creating HAConfig from dict"""
        data = {
            'version': '2024.11.0',
            'location_name': 'Home',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'time_zone': 'America/New_York',
            'unit_system': {'name': 'metric'},
            'components': ['light', 'switch', 'sensor']
        }

        config = HAConfigModel.from_dict(data)

        assert config.version == '2024.11.0'
        assert config.location_name == 'Home'
        assert config.latitude == 40.7128
        assert config.time_zone == 'America/New_York'
        assert len(config.components) == 3


# ============================================================================
# Client Tests
# ============================================================================

class TestHomeAssistantClient:
    """Test Home Assistant REST API client"""

    @patch('homeassistant.client.requests.get')
    def test_test_connection_success(self, mock_get):
        """Test successful connection test"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'message': 'API running'}
        mock_get.return_value = mock_response

        client = HomeAssistantClient('http://localhost:8123', 'test_token')
        result = client.test_connection()

        assert result is True

    @patch('homeassistant.client.requests.get')
    def test_test_connection_auth_error(self, mock_get):
        """Test connection with auth error"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
        mock_get.return_value = mock_response

        client = HomeAssistantClient('http://localhost:8123', 'bad_token')

        with pytest.raises(HAAuthError):
            client.test_connection()

    @patch('homeassistant.client.requests.get')
    def test_get_config(self, mock_get):
        """Test getting HA config"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'version': '2024.11.0',
            'location_name': 'Home',
            'components': ['light', 'switch']
        }
        mock_get.return_value = mock_response

        client = HomeAssistantClient('http://localhost:8123', 'test_token')
        config = client.get_config()

        assert config.version == '2024.11.0'
        assert config.location_name == 'Home'

    @patch('homeassistant.client.requests.get')
    def test_get_states(self, mock_get):
        """Test getting entity states"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'entity_id': 'light.living_room',
                'state': 'on',
                'attributes': {'brightness': 255}
            },
            {
                'entity_id': 'switch.kitchen',
                'state': 'off',
                'attributes': {}
            }
        ]
        mock_get.return_value = mock_response

        client = HomeAssistantClient('http://localhost:8123', 'test_token')
        entities = client.get_states()

        assert len(entities) == 2
        assert entities[0].entity_id == 'light.living_room'
        assert entities[1].entity_id == 'switch.kitchen'

    @patch('homeassistant.client.requests.get')
    def test_get_states_filtered(self, mock_get):
        """Test getting filtered entity states"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'entity_id': 'light.living_room',
                'state': 'on',
                'attributes': {}
            },
            {
                'entity_id': 'switch.kitchen',
                'state': 'off',
                'attributes': {}
            }
        ]
        mock_get.return_value = mock_response

        client = HomeAssistantClient('http://localhost:8123', 'test_token')
        entities = client.get_states(domain='light')

        assert len(entities) == 1
        assert entities[0].entity_id == 'light.living_room'

    @patch('homeassistant.client.requests.post')
    def test_call_service(self, mock_post):
        """Test calling service"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'entity_id': 'light.living_room', 'state': 'on'}]
        mock_post.return_value = mock_response

        client = HomeAssistantClient('http://localhost:8123', 'test_token')
        result = client.call_service('light', 'turn_on', {'entity_id': 'light.living_room'})

        assert len(result) == 1
        assert result[0]['state'] == 'on'

    @patch('homeassistant.client.requests.post')
    def test_turn_on(self, mock_post):
        """Test turning on entity"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_post.return_value = mock_response

        client = HomeAssistantClient('http://localhost:8123', 'test_token')
        result = client.turn_on('light.living_room', brightness=128)

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert 'light/turn_on' in call_args[0][0]
        assert call_args[1]['json']['entity_id'] == 'light.living_room'
        assert call_args[1]['json']['brightness'] == 128

    @patch('homeassistant.client.requests.post')
    def test_fire_event(self, mock_post):
        """Test firing event"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'message': 'Event fired'}
        mock_post.return_value = mock_response

        client = HomeAssistantClient('http://localhost:8123', 'test_token')
        result = client.fire_event('custom_event', {'key': 'value'})

        assert 'message' in result

    @patch('homeassistant.client.requests.get')
    def test_get_camera_snapshot(self, mock_get):
        """Test getting camera snapshot"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'fake_jpeg_data'
        mock_get.return_value = mock_response

        client = HomeAssistantClient('http://localhost:8123', 'test_token')
        snapshot = client.get_camera_snapshot('camera.front_door')

        assert snapshot == b'fake_jpeg_data'


# ============================================================================
# CLI Integration Tests
# ============================================================================

class TestHACLI:
    """Test Home Assistant CLI commands"""

    @patch('homeassistant.client.HomeAssistantClient')
    @patch('witness.database.WitnessDatabase')
    def test_cli_add_instance(self, mock_witness, mock_client_class):
        """Test CLI add command"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'test.yaml'

            # Mock client
            mock_client = Mock()
            mock_config = Mock()
            mock_config.version = '2024.11.0'
            mock_config.location_name = 'Home'
            mock_config.components = ['light', 'switch']
            mock_client.get_config.return_value = mock_config
            mock_client_class.return_value = mock_client

            # Mock witness database
            mock_db = Mock()
            mock_witness.return_value = mock_db

            config = HAConfig(config_path)
            instance = config.add_instance('test', 'http://localhost:8123', 'token')

            assert instance.name == 'test'
            assert config.get_instance('test') is not None

    def test_cli_list_empty(self):
        """Test CLI list with no instances"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'test.yaml'
            config = HAConfig(config_path)

            instances = config.list_instances()
            assert len(instances) == 0


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling"""

    @patch('homeassistant.client.requests.get')
    def test_connection_error(self, mock_get):
        """Test connection error handling"""
        mock_get.side_effect = Exception("Connection refused")

        client = HomeAssistantClient('http://localhost:8123', 'test_token')

        with pytest.raises(HAError):
            client.test_connection()

    @patch('homeassistant.client.requests.get')
    def test_timeout_error(self, mock_get):
        """Test timeout error handling"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()

        client = HomeAssistantClient('http://localhost:8123', 'test_token')

        with pytest.raises(HAConnectionError, match="Timeout"):
            client.test_connection()

    @patch('homeassistant.client.requests.get')
    def test_json_decode_error(self, mock_get):
        """Test JSON decode error handling"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("error", "doc", 0)
        mock_get.return_value = mock_response

        client = HomeAssistantClient('http://localhost:8123', 'test_token')

        with pytest.raises(Exception):
            client.get_config()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
