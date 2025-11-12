"""
Unit Tests for vMix PTZ and Call Control Integration

Tests comprehensive functionality:
1. PTZ Control (SetPanX, SetPanY, SetZoom, continuous movement)
2. vMix Call Control (audio/video routing)
3. Input Switching (transitions, preview)
4. IF.witness Audit Logging
5. Error Handling and Retry Logic
6. Command Hashing and Integrity

Author: InfraFabric Project
License: CC BY 4.0
Last Updated: 2025-11-12
"""

import sys
import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations.vmix_ptz_call import (
    VMixController,
    VMixCommand,
    VMixResponse,
    VMixWitnessLogger,
    VMixHTTPClient,
    PTZPosition,
    TransitionType,
    AudioSource,
    VideoSource,
    CallState,
    PTZProtocol,
    create_vmix_controller,
)


class TestPTZPosition(unittest.TestCase):
    """Test PTZ position coordinate validation"""

    def test_valid_position(self):
        """✅ Valid PTZ position should be accepted"""
        pos = PTZPosition(pan_x=0, pan_y=0, zoom=1.0)
        self.assertEqual(pos.pan_x, 0)
        self.assertEqual(pos.pan_y, 0)
        self.assertEqual(pos.zoom, 1.0)

    def test_pan_x_out_of_range_low(self):
        """❌ pan_x < -2 should raise ValueError"""
        with self.assertRaises(ValueError):
            PTZPosition(pan_x=-3, pan_y=0, zoom=1.0)

    def test_pan_x_out_of_range_high(self):
        """❌ pan_x > 2 should raise ValueError"""
        with self.assertRaises(ValueError):
            PTZPosition(pan_x=3, pan_y=0, zoom=1.0)

    def test_pan_y_out_of_range_low(self):
        """❌ pan_y < -2 should raise ValueError"""
        with self.assertRaises(ValueError):
            PTZPosition(pan_x=0, pan_y=-3, zoom=1.0)

    def test_pan_y_out_of_range_high(self):
        """❌ pan_y > 2 should raise ValueError"""
        with self.assertRaises(ValueError):
            PTZPosition(pan_x=0, pan_y=3, zoom=1.0)

    def test_zoom_out_of_range_low(self):
        """❌ zoom < 0 should raise ValueError"""
        with self.assertRaises(ValueError):
            PTZPosition(pan_x=0, pan_y=0, zoom=-1)

    def test_zoom_out_of_range_high(self):
        """❌ zoom > 5 should raise ValueError"""
        with self.assertRaises(ValueError):
            PTZPosition(pan_x=0, pan_y=0, zoom=6)

    def test_boundary_values(self):
        """✅ Boundary values should be accepted"""
        pos_min = PTZPosition(pan_x=-2, pan_y=-2, zoom=0)
        pos_max = PTZPosition(pan_x=2, pan_y=2, zoom=5)

        self.assertEqual(pos_min.pan_x, -2)
        self.assertEqual(pos_max.zoom, 5)


class TestVMixCommand(unittest.TestCase):
    """Test vMix command construction and serialization"""

    def test_basic_command_creation(self):
        """✅ Basic command should be created correctly"""
        cmd = VMixCommand(function="Cut", input_ref=1)
        self.assertEqual(cmd.function, "Cut")
        self.assertEqual(cmd.input_ref, 1)
        self.assertIsNotNone(cmd.timestamp)

    def test_command_to_url_params(self):
        """✅ Command should convert to URL parameters correctly"""
        cmd = VMixCommand(
            function="Fade",
            input_ref=3,
            duration=1000,
            mix=0
        )
        params = cmd.to_url_params()

        self.assertEqual(params["Function"], "Fade")
        self.assertEqual(params["Input"], "3")
        self.assertEqual(params["Duration"], "1000")
        self.assertEqual(params["Mix"], "0")

    def test_command_canonical_representation(self):
        """✅ Canonical representation should be deterministic"""
        cmd1 = VMixCommand(function="Cut", input_ref=1, value=0.5)
        cmd2 = VMixCommand(function="Cut", input_ref=1, value=0.5)

        # Set same timestamp
        cmd1.timestamp = "2025-11-12T00:00:00Z"
        cmd2.timestamp = "2025-11-12T00:00:00Z"

        canonical1 = cmd1.to_canonical()
        canonical2 = cmd2.to_canonical()

        self.assertEqual(canonical1, canonical2, "Canonical representation should be deterministic")

    def test_command_with_selected_name(self):
        """✅ Command with SelectedName should serialize correctly"""
        cmd = VMixCommand(
            function="SetText",
            input_ref="Title1",
            selected_name="Headline",
            value="Breaking News"
        )
        params = cmd.to_url_params()

        self.assertEqual(params["SelectedName"], "Headline")
        self.assertEqual(params["Value"], "Breaking News")


class TestVMixWitnessLogger(unittest.TestCase):
    """Test IF.witness audit logging"""

    def setUp(self):
        """Setup witness logger"""
        self.temp_dir = tempfile.mkdtemp()
        self.witness_dir = Path(self.temp_dir) / "witness"
        self.witness = VMixWitnessLogger(self.witness_dir)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_log_command(self):
        """✅ Should log vMix command to witness"""
        cmd = VMixCommand(function="Cut", input_ref=1)
        self.witness.log_command(cmd)

        # Check log file created
        log_files = list(self.witness_dir.glob("vmix_api_*.jsonl"))
        self.assertEqual(len(log_files), 1, "Log file should be created")

        # Check log content
        with open(log_files[0], 'r') as f:
            log_entry = json.loads(f.read())

        self.assertEqual(log_entry["msg_type"], "VMIX_CMD")
        self.assertEqual(log_entry["data"]["function"], "Cut")
        self.assertIn("hash", log_entry, "Log should have content hash")

    def test_log_response(self):
        """✅ Should log vMix response to witness"""
        response = VMixResponse(
            success=True,
            status_code=200,
            response_data="OK"
        )
        self.witness.log_response(response)

        # Check log file
        log_files = list(self.witness_dir.glob("vmix_api_*.jsonl"))
        self.assertEqual(len(log_files), 1)

        with open(log_files[0], 'r') as f:
            log_entry = json.loads(f.read())

        self.assertEqual(log_entry["msg_type"], "VMIX_RESP")
        self.assertTrue(log_entry["data"]["success"])
        self.assertEqual(log_entry["data"]["status_code"], 200)

    def test_log_ptz_move(self):
        """✅ Should log PTZ movement to witness"""
        position = PTZPosition(pan_x=1.0, pan_y=-0.5, zoom=2.0)
        self.witness.log_ptz_move(input_ref=1, position=position)

        # Check log content
        log_files = list(self.witness_dir.glob("vmix_api_*.jsonl"))
        with open(log_files[0], 'r') as f:
            log_entry = json.loads(f.read())

        self.assertEqual(log_entry["msg_type"], "PTZ_MOVE")
        self.assertEqual(log_entry["data"]["pan_x"], 1.0)
        self.assertEqual(log_entry["data"]["pan_y"], -0.5)
        self.assertEqual(log_entry["data"]["zoom"], 2.0)

    def test_log_call_control(self):
        """✅ Should log vMix Call control to witness"""
        self.witness.log_call_control(
            input_ref=2,
            audio_source=AudioSource.MASTER,
            video_source=VideoSource.OUTPUT1
        )

        # Check log content
        log_files = list(self.witness_dir.glob("vmix_api_*.jsonl"))
        with open(log_files[0], 'r') as f:
            log_entry = json.loads(f.read())

        self.assertEqual(log_entry["msg_type"], "CALL_CTRL")
        self.assertEqual(log_entry["data"]["audio_source"], "Master")
        self.assertEqual(log_entry["data"]["video_source"], "Output1")

    def test_hash_integrity(self):
        """✅ Log entries should have SHA-256 hash"""
        cmd = VMixCommand(function="Fade", input_ref=3, duration=1000)
        self.witness.log_command(cmd)

        log_files = list(self.witness_dir.glob("vmix_api_*.jsonl"))
        with open(log_files[0], 'r') as f:
            log_entry = json.loads(f.read())

        # Verify hash is SHA-256 (64 hex characters)
        self.assertEqual(len(log_entry["hash"]), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in log_entry["hash"]))


class TestVMixHTTPClient(unittest.TestCase):
    """Test HTTP client with retry logic"""

    @patch('requests.Session.get')
    def test_successful_request(self, mock_get):
        """✅ Successful request should return success response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<vmix>OK</vmix>"
        mock_get.return_value = mock_response

        client = VMixHTTPClient()
        cmd = VMixCommand(function="Cut", input_ref=1)
        response = client.send_command(cmd)

        self.assertTrue(response.success)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.response_data, "<vmix>OK</vmix>")

    @patch('requests.Session.get')
    def test_retry_on_server_error(self, mock_get):
        """✅ Should retry on 5xx server errors"""
        # First two calls fail with 500, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_fail.text = "Server Error"

        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.text = "OK"

        mock_get.side_effect = [
            mock_response_fail,
            mock_response_fail,
            mock_response_success
        ]

        client = VMixHTTPClient(backoff_factor=0.01)  # Fast retry for testing
        cmd = VMixCommand(function="Cut", input_ref=1)
        response = client.send_command(cmd)

        self.assertTrue(response.success)
        self.assertEqual(mock_get.call_count, 3)

    @patch('requests.Session.get')
    def test_no_retry_on_client_error(self, mock_get):
        """✅ Should NOT retry on 4xx client errors"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        client = VMixHTTPClient()
        cmd = VMixCommand(function="Cut", input_ref=999)
        response = client.send_command(cmd)

        self.assertFalse(response.success)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(mock_get.call_count, 1)  # No retry

    @patch('requests.Session.get')
    def test_max_retries_exceeded(self, mock_get):
        """❌ Should fail after max retries"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_get.return_value = mock_response

        client = VMixHTTPClient(max_retries=3, backoff_factor=0.01)
        cmd = VMixCommand(function="Cut", input_ref=1)
        response = client.send_command(cmd)

        self.assertFalse(response.success)
        self.assertEqual(mock_get.call_count, 3)


class TestVMixController(unittest.TestCase):
    """Test main vMix controller"""

    def setUp(self):
        """Setup controller with mock client"""
        self.temp_dir = tempfile.mkdtemp()
        self.witness_dir = Path(self.temp_dir) / "witness"
        self.controller = VMixController(
            witness_log_dir=self.witness_dir,
            timeout=5
        )

        # Mock the HTTP client
        self.controller.client.send_command = Mock(
            return_value=VMixResponse(success=True, status_code=200)
        )

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)
        self.controller.close()

    def test_set_ptz_position(self):
        """✅ Should send SetPanX, SetPanY, SetZoom commands"""
        position = PTZPosition(pan_x=1.0, pan_y=-0.5, zoom=2.0)
        response = self.controller.set_ptz_position(input_ref=1, position=position)

        # Should have called send_command 3 times (pan_x, pan_y, zoom)
        self.assertEqual(self.controller.client.send_command.call_count, 3)
        self.assertTrue(response.success)

        # Check witness log
        log_files = list(self.witness_dir.glob("vmix_api_*.jsonl"))
        self.assertEqual(len(log_files), 1)

    def test_ptz_move_continuous(self):
        """✅ Should send continuous PTZ movement command"""
        response = self.controller.ptz_move_continuous(
            input_ref=1,
            direction="up",
            speed=0.8
        )

        self.assertTrue(response.success)
        self.assertEqual(self.controller.client.send_command.call_count, 1)

        # Verify correct function was called
        call_args = self.controller.client.send_command.call_args[0][0]
        self.assertEqual(call_args.function, "PTZMoveUp")
        self.assertEqual(call_args.value, 0.8)

    def test_ptz_move_invalid_direction(self):
        """❌ Invalid direction should raise ValueError"""
        with self.assertRaises(ValueError):
            self.controller.ptz_move_continuous(
                input_ref=1,
                direction="invalid",
                speed=0.8
            )

    def test_ptz_move_invalid_speed(self):
        """❌ Invalid speed should raise ValueError"""
        with self.assertRaises(ValueError):
            self.controller.ptz_move_continuous(
                input_ref=1,
                direction="up",
                speed=1.5  # Out of range
            )

    def test_ptz_stop(self):
        """✅ Should send PTZMoveStop command"""
        response = self.controller.ptz_stop(input_ref=1)

        self.assertTrue(response.success)

        call_args = self.controller.client.send_command.call_args[0][0]
        self.assertEqual(call_args.function, "PTZMoveStop")

    def test_set_call_audio_source(self):
        """✅ Should send VideoCallAudioSource command"""
        response = self.controller.set_call_audio_source(
            input_ref=2,
            audio_source=AudioSource.MASTER
        )

        self.assertTrue(response.success)

        call_args = self.controller.client.send_command.call_args[0][0]
        self.assertEqual(call_args.function, "VideoCallAudioSource")
        self.assertEqual(call_args.value, "Master")

    def test_set_call_video_source(self):
        """✅ Should send VideoCallVideoSource command"""
        response = self.controller.set_call_video_source(
            input_ref=2,
            video_source=VideoSource.OUTPUT1
        )

        self.assertTrue(response.success)

        call_args = self.controller.client.send_command.call_args[0][0]
        self.assertEqual(call_args.function, "VideoCallVideoSource")
        self.assertEqual(call_args.value, "Output1")

    def test_switch_input_cut(self):
        """✅ Should switch input with cut transition"""
        response = self.controller.switch_input(
            input_ref=3,
            transition=TransitionType.CUT
        )

        self.assertTrue(response.success)

        call_args = self.controller.client.send_command.call_args[0][0]
        self.assertEqual(call_args.function, "Cut")
        self.assertEqual(call_args.input_ref, 3)

    def test_switch_input_fade_with_duration(self):
        """✅ Should switch input with fade transition and duration"""
        response = self.controller.switch_input(
            input_ref=4,
            transition=TransitionType.FADE,
            duration=1000
        )

        self.assertTrue(response.success)

        call_args = self.controller.client.send_command.call_args[0][0]
        self.assertEqual(call_args.function, "Fade")
        self.assertEqual(call_args.duration, 1000)

    def test_preview_input(self):
        """✅ Should set input to preview"""
        response = self.controller.preview_input(input_ref=5)

        self.assertTrue(response.success)

        call_args = self.controller.client.send_command.call_args[0][0]
        self.assertEqual(call_args.function, "PreviewInput")
        self.assertEqual(call_args.input_ref, 5)

    def test_context_manager(self):
        """✅ Controller should work as context manager"""
        with VMixController(witness_log_dir=self.witness_dir) as controller:
            controller.client.send_command = Mock(
                return_value=VMixResponse(success=True, status_code=200)
            )
            response = controller.ptz_stop(input_ref=1)
            self.assertTrue(response.success)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    def test_create_vmix_controller(self):
        """✅ Should create controller with default settings"""
        controller = create_vmix_controller()
        self.assertIsNotNone(controller)
        self.assertEqual(controller.client.base_url, "http://127.0.0.1:8088/API/")
        controller.close()

    def test_create_vmix_controller_with_witness(self):
        """✅ Should create controller with witness logging"""
        temp_dir = tempfile.mkdtemp()
        witness_dir = Path(temp_dir) / "witness"

        try:
            controller = create_vmix_controller(witness_log_dir=witness_dir)
            self.assertIsNotNone(controller.witness)
            controller.close()
        finally:
            shutil.rmtree(temp_dir)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for realistic production scenarios"""

    def setUp(self):
        """Setup controller with mocks"""
        self.temp_dir = tempfile.mkdtemp()
        self.witness_dir = Path(self.temp_dir) / "witness"
        self.controller = VMixController(witness_log_dir=self.witness_dir)
        self.controller.client.send_command = Mock(
            return_value=VMixResponse(success=True, status_code=200)
        )

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)
        self.controller.close()

    def test_multi_camera_ptz_preset_switch(self):
        """✅ Should switch between PTZ camera presets"""
        # Preset 1: Wide shot
        pos_wide = PTZPosition(pan_x=0, pan_y=0, zoom=1.0)
        self.controller.set_ptz_position(input_ref=1, position=pos_wide)

        # Preset 2: Close-up
        pos_closeup = PTZPosition(pan_x=1.5, pan_y=0.5, zoom=3.0)
        self.controller.set_ptz_position(input_ref=1, position=pos_closeup)

        # Should have executed 6 commands total (3 per position)
        self.assertEqual(self.controller.client.send_command.call_count, 6)

    def test_vmix_call_setup_workflow(self):
        """✅ Should configure vMix Call audio/video routing"""
        # Set audio to Bus A (virtual green room)
        self.controller.set_call_audio_source(
            input_ref=2,
            audio_source=AudioSource.BUS_A
        )

        # Set video to Output 1
        self.controller.set_call_video_source(
            input_ref=2,
            video_source=VideoSource.OUTPUT1
        )

        # Later switch to Master (live)
        self.controller.set_call_audio_source(
            input_ref=2,
            audio_source=AudioSource.MASTER
        )

        self.assertEqual(self.controller.client.send_command.call_count, 3)

    def test_production_switching_sequence(self):
        """✅ Should execute production switching sequence"""
        # Preview camera 2
        self.controller.preview_input(input_ref=2)

        # Fade to camera 2
        self.controller.switch_input(
            input_ref=2,
            transition=TransitionType.FADE,
            duration=1000
        )

        # Preview camera 3
        self.controller.preview_input(input_ref=3)

        # Cut to camera 3
        self.controller.switch_input(
            input_ref=3,
            transition=TransitionType.CUT
        )

        self.assertEqual(self.controller.client.send_command.call_count, 4)

        # Verify witness log has all commands
        log_files = list(self.witness_dir.glob("vmix_api_*.jsonl"))
        self.assertEqual(len(log_files), 1)


def run_tests():
    """Run all tests and print summary"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPTZPosition))
    suite.addTests(loader.loadTestsFromTestCase(TestVMixCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestVMixWitnessLogger))
    suite.addTests(loader.loadTestsFromTestCase(TestVMixHTTPClient))
    suite.addTests(loader.loadTestsFromTestCase(TestVMixController))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationScenarios))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("vMix PTZ and Call Control Integration Test Summary")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"❌ Errors: {len(result.errors)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
