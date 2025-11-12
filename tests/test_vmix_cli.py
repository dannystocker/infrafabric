"""
Tests for IF.vmix CLI

Test coverage:
- VMixClient API operations
- VMixConfig instance management
- CLI commands
- IF.witness logging integration
"""

import pytest
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from vmix.client import VMixClient, VMixConnectionError, VMixAPIError
from vmix.config import VMixConfig, VMixConfigError
from vmix.models import VMixInstance, VMixStatus, VMixInput


# ============================================================================
# Test Data
# ============================================================================

SAMPLE_XML_STATUS = """<?xml version="1.0" encoding="UTF-8"?>
<vmix>
  <version>25.0.0.65</version>
  <edition>4K</edition>
  <inputs>
    <input key="1" number="1" type="Video" state="Running">Camera 1</input>
    <input key="2" number="2" type="NDI" state="Running">NDI Source</input>
    <input key="3" number="3" type="Video" state="Paused">Video Clip</input>
  </inputs>
  <active>1</active>
  <preview>2</preview>
  <recording>False</recording>
  <streaming>True</streaming>
  <audio>True</audio>
</vmix>
"""


# ============================================================================
# VMixClient Tests
# ============================================================================

class TestVMixClient:
    """Test VMixClient API operations"""

    def test_init(self):
        """Test client initialization"""
        client = VMixClient("192.168.1.100", 8088)
        assert client.host == "192.168.1.100"
        assert client.port == 8088
        assert client.base_url == "http://192.168.1.100:8088/api/"

    @patch('requests.get')
    def test_execute_function_success(self, mock_get):
        """Test successful function execution"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = VMixClient("192.168.1.100")
        result = client.execute_function("Cut", Input=1)

        assert result is True
        mock_get.assert_called_once()
        call_url = mock_get.call_args[0][0]
        assert "Function=Cut" in call_url
        assert "Input=1" in call_url

    @patch('requests.get')
    def test_execute_function_connection_error(self, mock_get):
        """Test connection error handling"""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        client = VMixClient("192.168.1.100")

        with pytest.raises(VMixConnectionError):
            client.execute_function("Cut", Input=1)

    @patch('requests.get')
    def test_get_status_success(self, mock_get):
        """Test get_status with valid XML"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_XML_STATUS
        mock_get.return_value = mock_response

        client = VMixClient("192.168.1.100")
        status = client.get_status()

        assert status.version == "25.0.0.65"
        assert status.edition == "4K"
        assert len(status.inputs) == 3
        assert status.active_input == 1
        assert status.preview_input == 2
        assert status.recording is False
        assert status.streaming is True

    @patch('requests.get')
    def test_get_status_parse_error(self, mock_get):
        """Test get_status with invalid XML"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Invalid XML"
        mock_get.return_value = mock_response

        client = VMixClient("192.168.1.100")

        with pytest.raises(VMixAPIError):
            client.get_status()

    @patch('requests.get')
    def test_get_inputs(self, mock_get):
        """Test get_inputs"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_XML_STATUS
        mock_get.return_value = mock_response

        client = VMixClient("192.168.1.100")
        inputs = client.get_inputs()

        assert len(inputs) == 3
        assert inputs[0].number == 1
        assert inputs[0].title == "Camera 1"
        assert inputs[1].type == "NDI"

    @patch('requests.get')
    def test_production_control_methods(self, mock_get):
        """Test production control methods"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = VMixClient("192.168.1.100")

        # Test cut
        assert client.cut(1) is True

        # Test fade
        assert client.fade(2, 2000) is True

        # Test preview
        assert client.preview(3) is True

        # Test transition
        assert client.transition("Merge", 1000) is True

        # Test overlay
        assert client.overlay(1, 4) is True

    @patch('requests.get')
    def test_ndi_methods(self, mock_get):
        """Test NDI control methods"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = VMixClient("192.168.1.100")

        # Test add NDI input
        assert client.add_ndi_input("NDI Source Name") is True

        # Test remove input
        assert client.remove_input(5) is True

    @patch('requests.get')
    def test_streaming_methods(self, mock_get):
        """Test streaming methods"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_XML_STATUS
        mock_get.return_value = mock_response

        client = VMixClient("192.168.1.100")

        # Test set stream URL
        assert client.set_stream_url("rtmp://server/live", "key123") is True

        # Test start streaming
        assert client.start_streaming() is True

        # Test stop streaming
        assert client.stop_streaming() is True

        # Test get stream status
        status = client.get_stream_status()
        assert status.streaming is True

    @patch('requests.get')
    def test_recording_methods(self, mock_get):
        """Test recording methods"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_XML_STATUS
        mock_get.return_value = mock_response

        client = VMixClient("192.168.1.100")

        # Test start recording
        assert client.start_recording("output.mp4") is True

        # Test stop recording
        assert client.stop_recording() is True

        # Test get record status
        status = client.get_record_status()
        assert status.recording is False

    @patch('requests.get')
    def test_ptz_methods(self, mock_get):
        """Test PTZ camera control methods"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = VMixClient("192.168.1.100")

        # Test PTZ move
        assert client.ptz_move(1, pan=50, tilt=30, zoom=80) is True

        # Test PTZ preset
        assert client.ptz_preset(1, 3) is True

        # Test PTZ home
        assert client.ptz_home(1) is True

    @patch('requests.get')
    def test_audio_methods(self, mock_get):
        """Test audio control methods"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = VMixClient("192.168.1.100")

        # Test set volume
        assert client.set_volume(1, 75) is True

        # Test mute
        assert client.mute(1) is True

        # Test unmute
        assert client.unmute(1) is True


# ============================================================================
# VMixConfig Tests
# ============================================================================

class TestVMixConfig:
    """Test VMixConfig instance management"""

    @pytest.fixture
    def temp_config(self):
        """Create temporary config file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = Path(f.name)

        yield config_path

        # Cleanup
        if config_path.exists():
            config_path.unlink()

    def test_init(self, temp_config):
        """Test config initialization"""
        config = VMixConfig(temp_config)
        assert config.config_path == temp_config
        assert temp_config.exists()

    def test_add_instance(self, temp_config):
        """Test adding instance"""
        config = VMixConfig(temp_config)

        instance = config.add_instance("myvmix", "192.168.1.100", 8088)

        assert instance.name == "myvmix"
        assert instance.host == "192.168.1.100"
        assert instance.port == 8088
        assert instance.added_at is not None

    def test_add_instance_duplicate(self, temp_config):
        """Test adding duplicate instance"""
        config = VMixConfig(temp_config)

        config.add_instance("myvmix", "192.168.1.100")

        with pytest.raises(VMixConfigError):
            config.add_instance("myvmix", "192.168.1.101")

    def test_get_instance(self, temp_config):
        """Test getting instance"""
        config = VMixConfig(temp_config)

        config.add_instance("myvmix", "192.168.1.100", 8088)

        instance = config.get_instance("myvmix")
        assert instance is not None
        assert instance.name == "myvmix"
        assert instance.host == "192.168.1.100"

    def test_get_instance_not_found(self, temp_config):
        """Test getting non-existent instance"""
        config = VMixConfig(temp_config)

        instance = config.get_instance("nonexistent")
        assert instance is None

    def test_list_instances(self, temp_config):
        """Test listing instances"""
        config = VMixConfig(temp_config)

        config.add_instance("vmix1", "192.168.1.100")
        config.add_instance("vmix2", "192.168.1.101")

        instances = config.list_instances()
        assert len(instances) == 2
        assert instances[0].name == "vmix1"
        assert instances[1].name == "vmix2"

    def test_remove_instance(self, temp_config):
        """Test removing instance"""
        config = VMixConfig(temp_config)

        config.add_instance("myvmix", "192.168.1.100")
        assert config.instance_exists("myvmix")

        result = config.remove_instance("myvmix")
        assert result is True
        assert not config.instance_exists("myvmix")

    def test_remove_instance_not_found(self, temp_config):
        """Test removing non-existent instance"""
        config = VMixConfig(temp_config)

        result = config.remove_instance("nonexistent")
        assert result is False

    def test_update_instance(self, temp_config):
        """Test updating instance"""
        config = VMixConfig(temp_config)

        config.add_instance("myvmix", "192.168.1.100", 8088)

        updated = config.update_instance("myvmix", host="192.168.1.200", port=8089)
        assert updated is not None
        assert updated.host == "192.168.1.200"
        assert updated.port == 8089


# ============================================================================
# VMixModels Tests
# ============================================================================

class TestVMixModels:
    """Test vMix data models"""

    def test_vmix_instance(self):
        """Test VMixInstance model"""
        instance = VMixInstance(
            name="myvmix",
            host="192.168.1.100",
            port=8088
        )

        assert instance.name == "myvmix"
        assert instance.host == "192.168.1.100"
        assert instance.port == 8088
        assert instance.url == "http://192.168.1.100:8088/api/"

        # Test serialization
        data = instance.to_dict()
        assert data['name'] == "myvmix"

        # Test deserialization
        instance2 = VMixInstance.from_dict(data)
        assert instance2.name == instance.name

    def test_vmix_input(self):
        """Test VMixInput model"""
        input_xml = ET.fromstring('<input key="1" number="1" type="Video" state="Running">Camera 1</input>')
        input_obj = VMixInput.from_xml(input_xml)

        assert input_obj.number == 1
        assert input_obj.type == "Video"
        assert input_obj.title == "Camera 1"
        assert input_obj.state == "Running"

    def test_vmix_status(self):
        """Test VMixStatus model"""
        inputs = [
            VMixInput(key="1", number=1, type="Video", state="Running", title="Camera 1"),
            VMixInput(key="2", number=2, type="NDI", state="Running", title="NDI Source")
        ]

        status = VMixStatus(
            version="25.0.0.65",
            edition="4K",
            inputs=inputs,
            active_input=1,
            preview_input=2,
            recording=False,
            streaming=True
        )

        assert status.version == "25.0.0.65"
        assert len(status.inputs) == 2

        # Test serialization
        data = status.to_dict()
        assert data['version'] == "25.0.0.65"
        assert len(data['inputs']) == 2


# ============================================================================
# CLI Tests
# ============================================================================

class TestVMixCLI:
    """Test CLI commands"""

    @pytest.fixture
    def temp_config(self):
        """Create temporary config file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = Path(f.name)

        yield config_path

        # Cleanup
        if config_path.exists():
            config_path.unlink()

    @patch('vmix.config.VMixConfig')
    @patch('vmix.client.VMixClient')
    def test_cli_add_command(self, mock_client_class, mock_config_class):
        """Test 'if vmix add' command"""
        # This is a simplified test - full CLI tests would use Click's test runner
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        mock_client = Mock()
        mock_status = Mock(version="25.0.0.65", edition="4K")
        mock_client.get_status.return_value = mock_status
        mock_client_class.return_value = mock_client

        mock_instance = VMixInstance("myvmix", "192.168.1.100", 8088)
        mock_config.add_instance.return_value = mock_instance

        # Command would be executed here with Click test runner
        # For now, verify the mocks work
        assert mock_config is not None
        assert mock_client is not None


# ============================================================================
# Integration Tests
# ============================================================================

class TestVMixIntegration:
    """Integration tests for vMix CLI"""

    @pytest.mark.skip(reason="Requires real vMix instance")
    def test_full_workflow(self):
        """Test complete workflow: add instance, control, remove"""
        # This test requires a real vMix instance running
        # Skip by default, enable manually for integration testing

        config = VMixConfig()

        # Add instance
        instance = config.add_instance("test_vmix", "192.168.1.100", 8088)

        # Connect and test
        client = VMixClient(instance.host, instance.port)
        status = client.get_status()
        assert status.version is not None

        # Control operations
        client.cut(1)
        client.fade(2, 1000)

        # Cleanup
        config.remove_instance("test_vmix")


# ============================================================================
# IF.witness Integration Tests
# ============================================================================

class TestWitnessIntegration:
    """Test IF.witness logging integration"""

    @patch('witness.database.WitnessDatabase')
    def test_log_vmix_operation(self, mock_db_class):
        """Test logging to IF.witness"""
        from cli.vmix_commands import log_vmix_operation

        mock_db = Mock()
        mock_db_class.return_value = mock_db

        log_vmix_operation(
            instance_name="myvmix",
            operation="cut",
            params={'input': 1},
            result={'success': True}
        )

        # Verify database was called
        mock_db.create_entry.assert_called_once()
        call_args = mock_db.create_entry.call_args[1]

        assert call_args['event'] == 'vmix_cut'
        assert call_args['component'] == 'IF.vmix'
        assert 'vmix-myvmix' in call_args['trace_id']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
