"""
Comprehensive tests for OBS Streaming Controller
Tests all streaming, virtual camera, and recording functionality
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from integrations.obs_streaming import (
    OBSStreamingController,
    OBSConnectionError,
    OBSStreamingError,
    IFWitnessLogger,
    OBSStreamingContext,
    create_obs_controller
)


class MockOBSResponse:
    """Mock OBS WebSocket response"""

    def __init__(self, **kwargs):
        self.data = kwargs

    def getObsVersion(self):
        return self.data.get('obs_version', '28.0.0')

    def getWebsocketVersion(self):
        return self.data.get('websocket_version', '5.0.0')

    def getOutputActive(self):
        return self.data.get('output_active', False)

    def getOutputReconnecting(self):
        return self.data.get('output_reconnecting', False)

    def getOutputBytes(self):
        return self.data.get('output_bytes', 1024000)

    def getOutputDuration(self):
        return self.data.get('output_duration', 60000)

    def getOutputCongestion(self):
        return self.data.get('output_congestion', 0.0)

    def getOutputSkippedFrames(self):
        return self.data.get('output_skipped_frames', 0)

    def getOutputTotalFrames(self):
        return self.data.get('output_total_frames', 1800)

    def getOutputPaused(self):
        return self.data.get('output_paused', False)

    def getCpuUsage(self):
        return self.data.get('cpu_usage', 15.5)

    def getMemoryUsage(self):
        return self.data.get('memory_usage', 512.0)

    def getActiveFps(self):
        return self.data.get('active_fps', 30.0)

    def getAvailableDiskSpace(self):
        return self.data.get('available_disk_space', 50000)

    def getOutputPath(self):
        return self.data.get('output_path', '/recordings/test.mp4')


class TestIFWitnessLogger(unittest.TestCase):
    """Test IF.witness provenance logging"""

    def setUp(self):
        self.witness = IFWitnessLogger()

    def test_log_event(self):
        """Test logging an event"""
        event_hash = self.witness.log_event(
            'test_event',
            {'param1': 'value1'},
            {'result': 'success'}
        )

        self.assertIsNotNone(event_hash)
        self.assertEqual(len(event_hash), 64)  # SHA256 hex
        self.assertEqual(len(self.witness.events), 1)
        self.assertEqual(self.witness.events[0]['event_type'], 'test_event')

    def test_hash_chain(self):
        """Test hash chain creation"""
        hash1 = self.witness.log_event('event1', {}, {})
        hash2 = self.witness.log_event('event2', {}, {})
        hash3 = self.witness.log_event('event3', {}, {})

        # Check chain links
        self.assertEqual(self.witness.events[0]['prev_hash'], '0' * 64)
        self.assertEqual(self.witness.events[1]['prev_hash'], hash1)
        self.assertEqual(self.witness.events[2]['prev_hash'], hash2)

    def test_verify_chain(self):
        """Test chain verification"""
        self.witness.log_event('event1', {'a': 1}, {'b': 2})
        self.witness.log_event('event2', {'c': 3}, {'d': 4})
        self.witness.log_event('event3', {'e': 5}, {'f': 6})

        self.assertTrue(self.witness.verify_chain())

    def test_verify_chain_tampered(self):
        """Test chain verification detects tampering"""
        self.witness.log_event('event1', {'a': 1}, {'b': 2})
        self.witness.log_event('event2', {'c': 3}, {'d': 4})

        # Tamper with event
        self.witness.events[0]['params']['a'] = 999

        self.assertFalse(self.witness.verify_chain())


class TestOBSStreamingController(unittest.TestCase):
    """Test OBS Streaming Controller"""

    def setUp(self):
        """Set up test fixtures"""
        self.controller = OBSStreamingController(
            obs_host="localhost",
            obs_port=4455,
            obs_password="test_password"
        )

    @patch('integrations.obs_streaming.obsws')
    def test_connect_success(self, mock_obsws):
        """Test successful connection to OBS"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws

        mock_version_response = MockOBSResponse(
            obs_version='28.0.0',
            websocket_version='5.0.0'
        )
        mock_ws.call.return_value = mock_version_response

        result = self.controller.connect()

        self.assertTrue(self.controller.connected)
        self.assertEqual(result['status'], 'connected')
        self.assertEqual(result['obs_version'], '28.0.0')
        mock_ws.connect.assert_called_once()

    @patch('integrations.obs_streaming.obsws')
    def test_connect_failure(self, mock_obsws):
        """Test connection failure"""
        mock_obsws.side_effect = Exception("Connection refused")

        with self.assertRaises(OBSConnectionError):
            self.controller.connect()

        self.assertFalse(self.controller.connected)

    @patch('integrations.obs_streaming.obsws')
    def test_disconnect(self, mock_obsws):
        """Test disconnection"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse()

        self.controller.connect()
        result = self.controller.disconnect()

        self.assertEqual(result['status'], 'disconnected')
        self.assertFalse(self.controller.connected)
        mock_ws.disconnect.assert_called_once()

    @patch('integrations.obs_streaming.obsws')
    def test_start_stream(self, mock_obsws):
        """Test starting stream"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse(
            output_active=True,
            output_bytes=1024000,
            output_duration=60000
        )

        self.controller.connect()
        result = self.controller.start_stream(
            service="Twitch",
            key="test_key"
        )

        self.assertEqual(result['status'], 'started')
        self.assertTrue(result['streaming'])
        self.assertIn('timestamp', result)

    @patch('integrations.obs_streaming.obsws')
    def test_start_stream_custom_rtmp(self, mock_obsws):
        """Test starting stream with custom RTMP"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse(output_active=True)

        self.controller.connect()
        result = self.controller.start_stream(
            service="Custom",
            server="rtmp://custom.server.com/live",
            key="secret_key"
        )

        self.assertEqual(result['status'], 'started')

    @patch('integrations.obs_streaming.obsws')
    def test_stop_stream(self, mock_obsws):
        """Test stopping stream"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse(output_active=False)

        self.controller.connect()
        result = self.controller.stop_stream()

        self.assertEqual(result['status'], 'stopped')
        self.assertFalse(result['streaming'])

    @patch('integrations.obs_streaming.obsws')
    def test_get_stream_status(self, mock_obsws):
        """Test getting stream status"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse(
            output_active=True,
            output_bytes=2048000,
            output_duration=120000,
            output_skipped_frames=5,
            output_total_frames=3600
        )

        self.controller.connect()
        status = self.controller.get_stream_status()

        self.assertTrue(status['streaming'])
        self.assertEqual(status['bytes_sent'], 2048000)
        self.assertEqual(status['duration_ms'], 120000)
        self.assertGreater(status['kbits_per_sec'], 0)

    @patch('integrations.obs_streaming.obsws')
    def test_start_virtual_camera(self, mock_obsws):
        """Test starting virtual camera"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse(output_active=True)

        self.controller.connect()
        result = self.controller.start_virtual_camera()

        self.assertEqual(result['status'], 'started')
        self.assertTrue(result['active'])

    @patch('integrations.obs_streaming.obsws')
    def test_stop_virtual_camera(self, mock_obsws):
        """Test stopping virtual camera"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse(output_active=False)

        self.controller.connect()
        result = self.controller.stop_virtual_camera()

        self.assertEqual(result['status'], 'stopped')
        self.assertFalse(result['active'])

    @patch('integrations.obs_streaming.obsws')
    def test_get_virtual_camera_status(self, mock_obsws):
        """Test getting virtual camera status"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse(output_active=True)

        self.controller.connect()
        status = self.controller.get_virtual_camera_status()

        self.assertTrue(status['active'])

    @patch('integrations.obs_streaming.obsws')
    def test_start_recording(self, mock_obsws):
        """Test starting recording"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse(
            output_active=True,
            output_bytes=0,
            output_duration=0
        )

        self.controller.connect()
        result = self.controller.start_recording(
            filename="test_recording.mp4",
            format="mp4"
        )

        self.assertEqual(result['status'], 'started')
        self.assertTrue(result['recording'])
        self.assertEqual(result['format'], 'mp4')

    @patch('integrations.obs_streaming.obsws')
    def test_stop_recording(self, mock_obsws):
        """Test stopping recording"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws

        mock_record_response = MockOBSResponse(
            output_active=False,
            output_bytes=1024000000,
            output_duration=600000,
            output_path='/recordings/test.mp4'
        )
        mock_ws.call.return_value = mock_record_response

        self.controller.connect()
        result = self.controller.stop_recording()

        self.assertEqual(result['status'], 'stopped')
        self.assertFalse(result['recording'])
        self.assertIn('output_path', result)

    @patch('integrations.obs_streaming.obsws')
    def test_pause_resume_recording(self, mock_obsws):
        """Test pausing and resuming recording"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse()

        self.controller.connect()

        # Pause
        pause_result = self.controller.pause_recording()
        self.assertEqual(pause_result['status'], 'paused')

        # Resume
        resume_result = self.controller.resume_recording()
        self.assertEqual(resume_result['status'], 'resumed')

    @patch('integrations.obs_streaming.obsws')
    def test_get_record_status(self, mock_obsws):
        """Test getting record status"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse(
            output_active=True,
            output_paused=False,
            output_bytes=512000000,
            output_duration=180000  # 3 minutes
        )

        self.controller.connect()
        status = self.controller.get_record_status()

        self.assertTrue(status['recording'])
        self.assertFalse(status['paused'])
        self.assertEqual(status['duration_ms'], 180000)
        self.assertEqual(status['timecode'], '00:03:00.000')

    @patch('integrations.obs_streaming.obsws')
    def test_get_stats(self, mock_obsws):
        """Test getting OBS stats"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse(
            cpu_usage=25.5,
            memory_usage=768.0,
            active_fps=30.0,
            available_disk_space=100000
        )

        self.controller.connect()
        stats = self.controller.get_stats()

        self.assertEqual(stats['cpu_usage'], 25.5)
        self.assertEqual(stats['memory_usage_mb'], 768.0)
        self.assertEqual(stats['render_fps'], 30.0)

    @patch('integrations.obs_streaming.obsws')
    def test_stop_all(self, mock_obsws):
        """Test emergency stop all"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse(output_active=False)

        self.controller.connect()
        results = self.controller.stop_all()

        self.assertIn('stream', results)
        self.assertIn('virtualcam', results)
        self.assertIn('recording', results)

    def test_not_connected_error(self):
        """Test operations fail when not connected"""
        with self.assertRaises(OBSConnectionError):
            self.controller.start_stream()

        with self.assertRaises(OBSConnectionError):
            self.controller.start_virtual_camera()

        with self.assertRaises(OBSConnectionError):
            self.controller.start_recording()

    @patch('integrations.obs_streaming.obsws')
    def test_witness_logging(self, mock_obsws):
        """Test IF.witness event logging"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse(output_active=True)

        self.controller.connect()
        self.controller.start_stream()

        # Check witness events
        chain = self.controller.get_witness_chain()
        self.assertGreater(len(chain), 0)

        # Verify chain
        self.assertTrue(self.controller.verify_witness_chain())

    @patch('integrations.obs_streaming.obsws')
    def test_callbacks(self, mock_obsws):
        """Test event callbacks"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse(output_active=True)

        stream_started_called = False
        recording_started_called = False

        def on_stream_started(result):
            nonlocal stream_started_called
            stream_started_called = True

        def on_recording_started(result):
            nonlocal recording_started_called
            recording_started_called = True

        self.controller.on_stream_started(on_stream_started)
        self.controller.on_recording_started(on_recording_started)

        self.controller.connect()
        self.controller.start_stream()
        self.controller.start_recording()

        self.assertTrue(stream_started_called)
        self.assertTrue(recording_started_called)

    @patch('integrations.obs_streaming.obsws')
    def test_context_manager(self, mock_obsws):
        """Test context manager usage"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse()

        with OBSStreamingContext(self.controller) as obs:
            self.assertTrue(obs.connected)

        mock_ws.disconnect.assert_called_once()

    def test_create_obs_controller(self):
        """Test factory function"""
        controller = create_obs_controller(
            host="192.168.1.100",
            port=4455,
            password="test123"
        )

        self.assertIsInstance(controller, OBSStreamingController)
        self.assertEqual(controller.host, "192.168.1.100")
        self.assertEqual(controller.port, 4455)
        self.assertEqual(controller.password, "test123")

    @patch('integrations.obs_streaming.obsws')
    def test_export_witness_report(self, mock_obsws):
        """Test exporting witness report"""
        import tempfile

        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws
        mock_ws.call.return_value = MockOBSResponse(output_active=True)

        self.controller.connect()
        self.controller.start_stream()

        # Export report
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            report_path = f.name

        try:
            self.controller.export_witness_report(report_path)

            # Verify file exists and contains data
            import json
            with open(report_path, 'r') as f:
                report = json.load(f)

            self.assertIn('chain', report)
            self.assertIn('verified', report)
            self.assertTrue(report['verified'])
        finally:
            if os.path.exists(report_path):
                os.unlink(report_path)


class TestIntegrationScenarios(unittest.TestCase):
    """Test complete integration scenarios"""

    @patch('integrations.obs_streaming.obsws')
    def test_streaming_workflow(self, mock_obsws):
        """Test complete streaming workflow"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws

        # Setup responses
        def call_side_effect(request):
            request_name = request.__class__.__name__
            if 'Stream' in request_name:
                return MockOBSResponse(
                    output_active='Start' in request_name,
                    output_bytes=2048000,
                    output_duration=120000
                )
            return MockOBSResponse()

        mock_ws.call.side_effect = call_side_effect

        controller = OBSStreamingController()

        # Connect
        controller.connect()
        self.assertTrue(controller.connected)

        # Start stream
        result = controller.start_stream(service="Twitch", key="test_key")
        self.assertEqual(result['status'], 'started')

        # Get status
        status = controller.get_stream_status()
        self.assertTrue(status['streaming'])

        # Stop stream
        result = controller.stop_stream()
        self.assertEqual(result['status'], 'stopped')

        # Disconnect
        controller.disconnect()
        self.assertFalse(controller.connected)

    @patch('integrations.obs_streaming.obsws')
    def test_recording_workflow(self, mock_obsws):
        """Test complete recording workflow"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws

        def call_side_effect(request):
            request_name = request.__class__.__name__
            if 'Record' in request_name:
                if 'Stop' in request_name:
                    return MockOBSResponse(
                        output_active=False,
                        output_path='/recordings/test.mp4'
                    )
                return MockOBSResponse(
                    output_active=True,
                    output_paused='Pause' in request_name,
                    output_bytes=512000000,
                    output_duration=300000
                )
            return MockOBSResponse()

        mock_ws.call.side_effect = call_side_effect

        controller = OBSStreamingController()
        controller.connect()

        # Start recording
        result = controller.start_recording(filename="test.mp4", format="mp4")
        self.assertTrue(result['recording'])

        # Pause recording
        result = controller.pause_recording()
        self.assertEqual(result['status'], 'paused')

        # Resume recording
        result = controller.resume_recording()
        self.assertEqual(result['status'], 'resumed')

        # Stop recording
        result = controller.stop_recording()
        self.assertEqual(result['status'], 'stopped')
        self.assertIn('output_path', result)

    @patch('integrations.obs_streaming.obsws')
    def test_virtual_camera_workflow(self, mock_obsws):
        """Test complete virtual camera workflow"""
        mock_ws = MagicMock()
        mock_obsws.return_value = mock_ws

        def call_side_effect(request):
            request_name = request.__class__.__name__
            if 'VirtualCam' in request_name:
                return MockOBSResponse(
                    output_active='Start' in request_name
                )
            return MockOBSResponse()

        mock_ws.call.side_effect = call_side_effect

        controller = OBSStreamingController()
        controller.connect()

        # Start virtual camera
        result = controller.start_virtual_camera()
        self.assertTrue(result['active'])

        # Get status
        status = controller.get_virtual_camera_status()
        self.assertTrue(status['active'])

        # Stop virtual camera
        result = controller.stop_virtual_camera()
        self.assertFalse(result['active'])


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    run_tests()
