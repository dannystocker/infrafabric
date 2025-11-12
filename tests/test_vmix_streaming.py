"""
Unit Tests for vMix Streaming Controller
========================================

Tests all vMix streaming functionality with mocked API responses:
- RTMP streaming (Twitch, YouTube, Facebook, custom)
- SRT streaming (caller/listener modes)
- Recording control
- Status queries and health monitoring
- IF.witness integration and hash chain verification

Author: IF.Session2 (WebRTC) - vMix Streaming Integration
Date: 2025-11-12
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from integrations.vmix_streaming import (
    VMixStreamingController,
    VMixAPIError,
    VMixConnectionError,
    StreamingDestinations
)


class TestVMixStreamingController(unittest.TestCase):
    """Test suite for VMixStreamingController"""

    def setUp(self):
        """Set up test fixtures"""
        self.controller = VMixStreamingController(
            vmix_host='localhost',
            vmix_port=8088
        )

    def tearDown(self):
        """Clean up after tests"""
        self.controller = None

    # ===========================
    # Connection Tests
    # ===========================

    @patch('integrations.vmix_streaming.requests.get')
    def test_check_connection_success(self, mock_get):
        """Test successful connection to vMix"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<vmix><version>25.0.0.0</version></vmix>'
        mock_get.return_value = mock_response

        result = self.controller._check_connection()
        self.assertTrue(result)

    @patch('integrations.vmix_streaming.requests.get')
    def test_check_connection_failure(self, mock_get):
        """Test connection failure to vMix"""
        mock_get.side_effect = Exception("Connection refused")

        with self.assertRaises(VMixConnectionError):
            self.controller._check_connection()

    # ===========================
    # RTMP Streaming Tests
    # ===========================

    @patch('integrations.vmix_streaming.requests.get')
    def test_start_rtmp_stream_success(self, mock_get):
        """Test successful RTMP stream start"""
        # Mock connection check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<vmix></vmix>'
        mock_get.return_value = mock_response

        result = self.controller.start_rtmp_stream(
            rtmp_url='rtmp://live.twitch.tv/app/',
            stream_key='test_key_12345',
            channel=0
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['channel'], 0)
        self.assertIn('rtmp://live.twitch.tv/app/', result['destination'])

    def test_start_rtmp_stream_invalid_url(self):
        """Test RTMP stream with invalid URL"""
        result = self.controller.start_rtmp_stream(
            rtmp_url='http://invalid.com',  # Not RTMP
            stream_key='test_key',
            channel=0
        )

        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'validation_error')
        self.assertIn('Invalid RTMP URL', result['message'])

    def test_start_rtmp_stream_invalid_channel(self):
        """Test RTMP stream with invalid channel"""
        result = self.controller.start_rtmp_stream(
            rtmp_url='rtmp://live.twitch.tv/app/',
            stream_key='test_key',
            channel=5  # Invalid (must be 0-2)
        )

        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'validation_error')
        self.assertIn('Invalid channel', result['message'])

    def test_start_rtmp_stream_empty_key(self):
        """Test RTMP stream with empty stream key"""
        result = self.controller.start_rtmp_stream(
            rtmp_url='rtmp://live.twitch.tv/app/',
            stream_key='',  # Empty
            channel=0
        )

        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'validation_error')
        self.assertIn('Stream key cannot be empty', result['message'])

    @patch('integrations.vmix_streaming.requests.get')
    def test_start_rtmp_stream_twitch(self, mock_get):
        """Test starting Twitch stream"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<vmix></vmix>'
        mock_get.return_value = mock_response

        twitch_config = StreamingDestinations.twitch('test_key')
        result = self.controller.start_rtmp_stream(**twitch_config, channel=0)

        self.assertTrue(result['success'])
        self.assertIn('twitch', result['destination'].lower())

    @patch('integrations.vmix_streaming.requests.get')
    def test_start_rtmp_stream_youtube(self, mock_get):
        """Test starting YouTube stream"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<vmix></vmix>'
        mock_get.return_value = mock_response

        youtube_config = StreamingDestinations.youtube('test_key')
        result = self.controller.start_rtmp_stream(**youtube_config, channel=1)

        self.assertTrue(result['success'])
        self.assertEqual(result['channel'], 1)

    # ===========================
    # SRT Streaming Tests
    # ===========================

    @patch('integrations.vmix_streaming.requests.get')
    def test_start_srt_stream_caller_mode(self, mock_get):
        """Test SRT stream in caller mode"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<vmix></vmix>'
        mock_get.return_value = mock_response

        result = self.controller.start_srt_stream(
            srt_address='srt://192.168.1.100:9000',
            mode='caller',
            latency_ms=120,
            channel=0
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['protocol'], 'SRT')
        self.assertEqual(result['mode'], 'caller')
        self.assertEqual(result['latency_ms'], 120)

    @patch('integrations.vmix_streaming.requests.get')
    def test_start_srt_stream_listener_mode(self, mock_get):
        """Test SRT stream in listener mode"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<vmix></vmix>'
        mock_get.return_value = mock_response

        result = self.controller.start_srt_stream(
            srt_address='srt://0.0.0.0:9000',
            mode='listener',
            latency_ms=200,
            channel=1
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['mode'], 'listener')

    def test_start_srt_stream_invalid_address(self):
        """Test SRT stream with invalid address"""
        result = self.controller.start_srt_stream(
            srt_address='rtmp://wrong.com',  # Not SRT
            mode='caller',
            latency_ms=120
        )

        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'validation_error')
        self.assertIn('Invalid SRT address', result['message'])

    def test_start_srt_stream_invalid_mode(self):
        """Test SRT stream with invalid mode"""
        result = self.controller.start_srt_stream(
            srt_address='srt://192.168.1.100:9000',
            mode='invalid_mode',
            latency_ms=120
        )

        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'validation_error')
        self.assertIn('Invalid mode', result['message'])

    def test_start_srt_stream_invalid_latency(self):
        """Test SRT stream with invalid latency"""
        result = self.controller.start_srt_stream(
            srt_address='srt://192.168.1.100:9000',
            mode='caller',
            latency_ms=10000  # Too high (max 8000ms)
        )

        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'validation_error')
        self.assertIn('Invalid latency', result['message'])

    # ===========================
    # Recording Tests
    # ===========================

    @patch('integrations.vmix_streaming.requests.get')
    def test_start_recording_with_filename(self, mock_get):
        """Test starting recording with custom filename"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<vmix></vmix>'
        mock_get.return_value = mock_response

        result = self.controller.start_recording(
            filename='production_2025-11-12.mp4',
            format='MP4',
            quality='high'
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['filename'], 'production_2025-11-12.mp4')
        self.assertEqual(result['format'], 'MP4')
        self.assertEqual(result['quality'], 'high')

    @patch('integrations.vmix_streaming.requests.get')
    def test_start_recording_auto_filename(self, mock_get):
        """Test starting recording with auto-generated filename"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<vmix></vmix>'
        mock_get.return_value = mock_response

        result = self.controller.start_recording(
            filename=None,
            format='MP4',
            quality='high'
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['filename'], 'auto-generated')

    def test_start_recording_invalid_format(self):
        """Test recording with invalid format"""
        result = self.controller.start_recording(
            filename='test.xyz',
            format='XYZ',  # Invalid format
            quality='high'
        )

        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'validation_error')
        self.assertIn('Invalid format', result['message'])

    def test_start_recording_invalid_quality(self):
        """Test recording with invalid quality"""
        result = self.controller.start_recording(
            filename='test.mp4',
            format='MP4',
            quality='ultra'  # Invalid quality
        )

        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'validation_error')
        self.assertIn('Invalid quality', result['message'])

    @patch('integrations.vmix_streaming.requests.get')
    def test_stop_recording(self, mock_get):
        """Test stopping recording"""
        # Mock XML status response with recording duration
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <vmix>
                <recording>True</recording>
                <recordingDuration>00:15:32</recordingDuration>
            </vmix>
        '''
        mock_get.return_value = mock_response

        result = self.controller.stop_recording()

        self.assertTrue(result['success'])
        self.assertEqual(result['duration'], '00:15:32')

    # ===========================
    # Stop Stream Tests
    # ===========================

    @patch('integrations.vmix_streaming.requests.get')
    def test_stop_stream_channel_0(self, mock_get):
        """Test stopping stream on channel 0"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<vmix></vmix>'
        mock_get.return_value = mock_response

        result = self.controller.stop_stream(channel=0)

        self.assertTrue(result['success'])
        self.assertEqual(result['channel'], 0)

    def test_stop_stream_invalid_channel(self):
        """Test stopping stream with invalid channel"""
        result = self.controller.stop_stream(channel=9)

        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'validation_error')

    # ===========================
    # Status Query Tests
    # ===========================

    @patch('integrations.vmix_streaming.requests.get')
    def test_get_stream_status_streaming_active(self, mock_get):
        """Test getting stream status when streaming is active"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <vmix>
                <version>25.0.0.0</version>
                <edition>Pro</edition>
                <streaming>True</streaming>
                <recording>False</recording>
                <streaming0>True</streaming0>
                <streaming1>True</streaming1>
                <streaming2>False</streaming2>
                <duration>00:10:30</duration>
                <recordingDuration>00:00:00</recordingDuration>
            </vmix>
        '''
        mock_get.return_value = mock_response

        status = self.controller.get_stream_status()

        self.assertTrue(status['streaming'])
        self.assertFalse(status['recording'])
        self.assertEqual(status['stream_time'], '00:10:30')
        self.assertEqual(len(status['stream_channels']), 2)
        self.assertIn(0, status['stream_channels'])
        self.assertIn(1, status['stream_channels'])
        self.assertEqual(status['version'], '25.0.0.0')
        self.assertEqual(status['edition'], 'Pro')

    @patch('integrations.vmix_streaming.requests.get')
    def test_get_stream_status_recording_active(self, mock_get):
        """Test getting stream status when recording is active"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <vmix>
                <streaming>False</streaming>
                <recording>True</recording>
                <duration>00:00:00</duration>
                <recordingDuration>00:25:15</recordingDuration>
            </vmix>
        '''
        mock_get.return_value = mock_response

        status = self.controller.get_stream_status()

        self.assertFalse(status['streaming'])
        self.assertTrue(status['recording'])
        self.assertEqual(status['record_time'], '00:25:15')

    # ===========================
    # Health Monitoring Tests
    # ===========================

    @patch('integrations.vmix_streaming.requests.get')
    def test_get_stream_health_healthy(self, mock_get):
        """Test stream health with healthy metrics"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <vmix>
                <output>
                    <bitrate>5000</bitrate>
                </output>
                <droppedFrames>50</droppedFrames>
                <frameRate>30</frameRate>
                <duration>00:30:00</duration>
            </vmix>
        '''
        mock_get.return_value = mock_response

        health = self.controller.get_stream_health()

        self.assertEqual(health['health_status'], 'healthy')
        self.assertEqual(health['bitrate_kbps'], 5000.0)
        self.assertEqual(health['dropped_frames'], 50)
        self.assertEqual(health['fps'], 30.0)
        self.assertEqual(health['uptime_seconds'], 1800)  # 30 minutes

    @patch('integrations.vmix_streaming.requests.get')
    def test_get_stream_health_warning(self, mock_get):
        """Test stream health with warning metrics"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <vmix>
                <output>
                    <bitrate>3000</bitrate>
                </output>
                <droppedFrames>300</droppedFrames>
                <frameRate>26</frameRate>
                <duration>00:15:00</duration>
            </vmix>
        '''
        mock_get.return_value = mock_response

        health = self.controller.get_stream_health()

        self.assertEqual(health['health_status'], 'warning')
        self.assertEqual(health['fps'], 26.0)
        self.assertEqual(health['dropped_frames'], 300)

    @patch('integrations.vmix_streaming.requests.get')
    def test_get_stream_health_critical(self, mock_get):
        """Test stream health with critical metrics"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <vmix>
                <output>
                    <bitrate>2000</bitrate>
                </output>
                <droppedFrames>1000</droppedFrames>
                <frameRate>20</frameRate>
                <duration>00:05:00</duration>
            </vmix>
        '''
        mock_get.return_value = mock_response

        health = self.controller.get_stream_health()

        self.assertEqual(health['health_status'], 'critical')
        self.assertLess(health['fps'], 25)
        self.assertGreaterEqual(health['dropped_frames'], 500)

    # ===========================
    # IF.witness Integration Tests
    # ===========================

    @patch('integrations.vmix_streaming.requests.get')
    def test_witness_log_creation(self, mock_get):
        """Test IF.witness log entry creation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<vmix></vmix>'
        mock_get.return_value = mock_response

        # Start a stream to generate witness log entry
        self.controller.start_rtmp_stream(
            rtmp_url='rtmp://test.com/live/',
            stream_key='test_key',
            channel=0
        )

        # Allow async task to complete (simplified for testing)
        import time
        time.sleep(0.1)

        # Check witness log
        log = self.controller.get_witness_log()
        self.assertGreater(len(log), 0)

    def test_witness_chain_verification_valid(self):
        """Test IF.witness hash chain verification (valid chain)"""
        # Create some test events
        test_events = [
            {'event_type': 'stream_started', 'timestamp': '2025-11-12T10:00:00Z'},
            {'event_type': 'recording_started', 'timestamp': '2025-11-12T10:01:00Z'},
            {'event_type': 'stream_stopped', 'timestamp': '2025-11-12T10:30:00Z'}
        ]

        for event in test_events:
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                self.controller.log_to_witness(event)
            )

        # Verify chain
        verification = self.controller.verify_witness_chain()

        self.assertTrue(verification['valid'])
        self.assertEqual(verification['total_events'], len(test_events))
        self.assertIsNone(verification['broken_at'])

    def test_witness_log_filtering(self):
        """Test IF.witness log filtering by event type"""
        # Create mixed event types
        events = [
            {'event_type': 'stream_started', 'timestamp': '2025-11-12T10:00:00Z'},
            {'event_type': 'recording_started', 'timestamp': '2025-11-12T10:01:00Z'},
            {'event_type': 'stream_started', 'timestamp': '2025-11-12T10:02:00Z'},
            {'event_type': 'stream_stopped', 'timestamp': '2025-11-12T10:30:00Z'}
        ]

        for event in events:
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                self.controller.log_to_witness(event)
            )

        # Filter for stream_started events
        filtered = self.controller.get_witness_log(event_type='stream_started')

        self.assertEqual(len(filtered), 2)
        for entry in filtered:
            self.assertEqual(entry['event']['event_type'], 'stream_started')

    # ===========================
    # Streaming Destinations Tests
    # ===========================

    def test_streaming_destinations_twitch(self):
        """Test Twitch streaming destination configuration"""
        config = StreamingDestinations.twitch('test_key_12345')

        self.assertEqual(config['rtmp_url'], 'rtmp://live.twitch.tv/app/')
        self.assertEqual(config['stream_key'], 'test_key_12345')

    def test_streaming_destinations_youtube(self):
        """Test YouTube streaming destination configuration"""
        config = StreamingDestinations.youtube('yt_key_67890')

        self.assertEqual(config['rtmp_url'], 'rtmp://a.rtmp.youtube.com/live2/')
        self.assertEqual(config['stream_key'], 'yt_key_67890')

    def test_streaming_destinations_facebook(self):
        """Test Facebook streaming destination configuration"""
        config = StreamingDestinations.facebook('fb_key_abcdef')

        self.assertIn('rtmps://', config['rtmp_url'])
        self.assertIn('facebook.com', config['rtmp_url'])
        self.assertEqual(config['stream_key'], 'fb_key_abcdef')

    def test_streaming_destinations_custom(self):
        """Test custom RTMP server configuration"""
        config = StreamingDestinations.custom_rtmp(
            'rtmp://custom-server.example.com/live',
            'custom_key_xyz'
        )

        self.assertEqual(
            config['rtmp_url'],
            'rtmp://custom-server.example.com/live/'
        )
        self.assertEqual(config['stream_key'], 'custom_key_xyz')

    def test_streaming_destinations_custom_trailing_slash(self):
        """Test custom RTMP server adds trailing slash"""
        config = StreamingDestinations.custom_rtmp(
            'rtmp://custom-server.example.com/live/',  # Already has slash
            'key'
        )

        # Should not double the slash
        self.assertEqual(
            config['rtmp_url'],
            'rtmp://custom-server.example.com/live/'
        )


# ===========================
# Integration Test Suite
# ===========================

class TestVMixIntegrationScenarios(unittest.TestCase):
    """Integration tests simulating real-world streaming scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        self.controller = VMixStreamingController()

    @patch('integrations.vmix_streaming.requests.get')
    def test_multi_channel_streaming(self, mock_get):
        """Test streaming to multiple channels simultaneously"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<vmix></vmix>'
        mock_get.return_value = mock_response

        # Start streams on channels 0 and 1
        result1 = self.controller.start_rtmp_stream(
            rtmp_url='rtmp://live.twitch.tv/app/',
            stream_key='twitch_key',
            channel=0
        )

        result2 = self.controller.start_rtmp_stream(
            rtmp_url='rtmp://a.rtmp.youtube.com/live2/',
            stream_key='youtube_key',
            channel=1
        )

        self.assertTrue(result1['success'])
        self.assertTrue(result2['success'])
        self.assertEqual(result1['channel'], 0)
        self.assertEqual(result2['channel'], 1)

    @patch('integrations.vmix_streaming.requests.get')
    def test_stream_and_record_simultaneously(self, mock_get):
        """Test streaming and recording at the same time"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<vmix></vmix>'
        mock_get.return_value = mock_response

        # Start streaming
        stream_result = self.controller.start_rtmp_stream(
            rtmp_url='rtmp://live.twitch.tv/app/',
            stream_key='test_key',
            channel=0
        )

        # Start recording
        record_result = self.controller.start_recording(
            filename='live_show_backup.mp4',
            format='MP4',
            quality='high'
        )

        self.assertTrue(stream_result['success'])
        self.assertTrue(record_result['success'])

    @patch('integrations.vmix_streaming.requests.get')
    def test_complete_streaming_workflow(self, mock_get):
        """Test complete workflow: start stream -> check status -> stop stream"""
        # Mock responses for different API calls
        def mock_response_factory(*args, **kwargs):
            response = Mock()
            response.status_code = 200

            # Return XML status if no params, otherwise success
            if 'Function' not in str(args):
                response.text = '''
                    <vmix>
                        <streaming>True</streaming>
                        <recording>False</recording>
                        <streaming0>True</streaming0>
                        <duration>00:15:30</duration>
                    </vmix>
                '''
            else:
                response.text = '<vmix></vmix>'

            return response

        mock_get.side_effect = mock_response_factory

        # Step 1: Start stream
        start_result = self.controller.start_rtmp_stream(
            rtmp_url='rtmp://live.twitch.tv/app/',
            stream_key='workflow_test',
            channel=0
        )
        self.assertTrue(start_result['success'])

        # Step 2: Check status
        status = self.controller.get_stream_status()
        self.assertTrue(status['streaming'])
        self.assertIn(0, status['stream_channels'])

        # Step 3: Stop stream
        stop_result = self.controller.stop_stream(channel=0)
        self.assertTrue(stop_result['success'])


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
