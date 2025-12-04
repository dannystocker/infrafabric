"""
vMix Streaming Integration for InfraFabric
==========================================

Provides comprehensive control over vMix streaming outputs:
- RTMP streaming (Twitch, YouTube, Facebook Live, custom servers)
- SRT streaming (low-latency, secure reliable transport)
- Recording control (MP4, AVI, MOV, MKV formats)
- Stream health monitoring
- IF.witness integration for provenance tracking

vMix API Documentation:
- https://www.vmix.com/help25/index.htm?DeveloperAPI.html
- HTTP API: http://vmix-host:8088/api
- XML Status API: http://vmix-host:8088/api

Author: IF.Session2 (WebRTC) - vMix Streaming Integration
Date: 2025-11-12
"""

import requests
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List, Any
import asyncio
from datetime import datetime
import json
import hashlib
from urllib.parse import urlencode, quote


class VMixAPIError(Exception):
    """Raised when vMix API returns an error"""
    pass


class VMixConnectionError(Exception):
    """Raised when unable to connect to vMix instance"""
    pass


class VMixStreamingController:
    """
    Control vMix streaming outputs (RTMP, SRT, recording)
    Integrates with IF.witness for provenance tracking

    vMix API Functions:
    - StartStreaming / StopStreaming (RTMP/RTMPS)
    - StartRecording / StopRecording
    - SetOutput (configure streaming destinations)

    XML Status API provides:
    - Streaming status (active/inactive)
    - Recording status
    - Duration counters
    - Stream health metrics
    """

    def __init__(self, vmix_host: str = "localhost", vmix_port: int = 8088):
        """
        Initialize vMix streaming controller

        Args:
            vmix_host: vMix instance hostname/IP (default: localhost)
            vmix_port: vMix HTTP API port (default: 8088)
        """
        self.host = vmix_host
        self.port = vmix_port
        self.base_url = f"http://{vmix_host}:{vmix_port}/api"
        self.xml_url = f"http://{vmix_host}:{vmix_port}/api"

        # Witness event log for provenance tracking
        self.witness_log: List[Dict] = []
        self.last_hash = self._genesis_hash()

    def _genesis_hash(self) -> str:
        """Generate genesis hash for witness chain"""
        return hashlib.sha256(
            f"vmix-witness-genesis-{self.host}:{self.port}".encode()
        ).hexdigest()

    def _check_connection(self) -> bool:
        """
        Verify vMix instance is reachable

        Returns:
            bool: True if vMix is responding

        Raises:
            VMixConnectionError: If unable to connect
        """
        try:
            response = requests.get(self.xml_url, timeout=5)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            raise VMixConnectionError(
                f"Cannot connect to vMix at {self.host}:{self.port}. "
                f"Ensure vMix is running and Web Controller is enabled. "
                f"Error: {str(e)}"
            )

    def _send_function(self, function: str, **params) -> Dict:
        """
        Send vMix Function API command

        vMix Function API format:
        http://vmix-host:8088/api/?Function=FunctionName&Value=param

        Args:
            function: vMix function name (e.g., 'StartStreaming', 'StopStreaming')
            **params: Function parameters (e.g., Value=0 for channel 0)

        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Build query string
            query_params = {'Function': function}
            query_params.update(params)

            url = f"{self.base_url}/?{urlencode(query_params)}"

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            return {
                'success': True,
                'message': f'{function} executed successfully',
                'url': url,
                'status_code': response.status_code
            }

        except requests.RequestException as e:
            return {
                'success': False,
                'message': f'Failed to execute {function}: {str(e)}',
                'error': str(e)
            }

    def _get_xml_status(self) -> ET.Element:
        """
        Fetch vMix XML status

        Returns:
            ET.Element: Root XML element containing vMix state

        Raises:
            VMixAPIError: If XML parsing fails
        """
        try:
            response = requests.get(self.xml_url, timeout=5)
            response.raise_for_status()
            return ET.fromstring(response.text)
        except (requests.RequestException, ET.ParseError) as e:
            raise VMixAPIError(f"Failed to fetch vMix status: {str(e)}")

    def start_rtmp_stream(
        self,
        rtmp_url: str,
        stream_key: str,
        channel: int = 0,
        configure_first: bool = True
    ) -> Dict:
        """
        Start RTMP stream to destination

        vMix supports 3 simultaneous streaming channels (0, 1, 2)
        Common destinations:
        - Twitch: rtmp://live.twitch.tv/app/
        - YouTube: rtmp://a.rtmp.youtube.com/live2/
        - Facebook: rtmps://live-api-s.facebook.com:443/rtmp/
        - Custom RTMP server: rtmp://your-server.com/live/

        Args:
            rtmp_url: RTMP server URL (e.g., rtmp://live.twitch.tv/app/)
            stream_key: Stream key/password
            channel: Stream channel (0-2, default: 0)
            configure_first: Configure stream destination before starting

        Returns:
            dict: {
                'success': bool,
                'message': str,
                'channel': int,
                'destination': str (redacted stream key)
            }

        Example:
            >>> controller.start_rtmp_stream(
            ...     rtmp_url="rtmp://live.twitch.tv/app/",
            ...     stream_key="live_123456789_abc",
            ...     channel=0
            ... )
            {'success': True, 'message': 'RTMP stream started', 'channel': 0}
        """
        # Validate inputs
        if not rtmp_url.startswith(('rtmp://', 'rtmps://')):
            return {
                'success': False,
                'message': 'Invalid RTMP URL. Must start with rtmp:// or rtmps://',
                'error': 'validation_error'
            }

        if channel not in [0, 1, 2]:
            return {
                'success': False,
                'message': 'Invalid channel. Must be 0, 1, or 2',
                'error': 'validation_error'
            }

        if not stream_key:
            return {
                'success': False,
                'message': 'Stream key cannot be empty',
                'error': 'validation_error'
            }

        # Check connection first
        try:
            self._check_connection()
        except VMixConnectionError as e:
            return {
                'success': False,
                'message': str(e),
                'error': 'connection_error'
            }

        # Configure stream destination if requested
        if configure_first:
            # vMix SetOutput function configures streaming destination
            # Format: SetOutput, Value=channel, Output=External2, etc.
            full_url = f"{rtmp_url}{stream_key}"
            config_result = self._send_function(
                'SetOutput',
                Value=str(channel),
                **{'Output': 'External2', 'URL': full_url}
            )

            if not config_result['success']:
                return {
                    'success': False,
                    'message': f"Failed to configure stream destination: {config_result['message']}",
                    'error': 'configuration_error'
                }

        # Start streaming on specified channel
        result = self._send_function('StartStreaming', Value=str(channel))

        if result['success']:
            # Log to IF.witness
            event = {
                'event_type': 'stream_started',
                'timestamp': datetime.utcnow().isoformat(),
                'params': {
                    'protocol': 'RTMP',
                    'destination': rtmp_url,  # Don't log stream key
                    'channel': channel
                },
                'result': result
            }
            asyncio.create_task(self.log_to_witness(event))

            return {
                'success': True,
                'message': f'RTMP stream started on channel {channel}',
                'channel': channel,
                'destination': rtmp_url  # Redacted
            }

        return result

    def start_srt_stream(
        self,
        srt_address: str,
        mode: str = "caller",
        latency_ms: int = 120,
        channel: int = 0
    ) -> Dict:
        """
        Start SRT stream (Secure Reliable Transport)

        SRT provides low-latency streaming with error recovery:
        - Sub-second latency (default 120ms)
        - Packet retransmission for reliability
        - AES encryption support
        - Firewall traversal

        Modes:
        - caller: vMix initiates connection (client mode)
        - listener: vMix waits for connection (server mode)

        Args:
            srt_address: SRT address (e.g., srt://192.168.1.100:9000)
            mode: 'caller' or 'listener' (default: caller)
            latency_ms: SRT latency in milliseconds (default: 120ms)
            channel: Stream channel (0-2, default: 0)

        Returns:
            dict: {
                'success': bool,
                'message': str,
                'protocol': 'SRT',
                'mode': str,
                'latency_ms': int
            }

        Example:
            >>> controller.start_srt_stream(
            ...     srt_address="srt://192.168.1.100:9000",
            ...     mode="caller",
            ...     latency_ms=120
            ... )
        """
        # Validate inputs
        if not srt_address.startswith('srt://'):
            return {
                'success': False,
                'message': 'Invalid SRT address. Must start with srt://',
                'error': 'validation_error'
            }

        if mode not in ['caller', 'listener']:
            return {
                'success': False,
                'message': "Invalid mode. Must be 'caller' or 'listener'",
                'error': 'validation_error'
            }

        if latency_ms < 20 or latency_ms > 8000:
            return {
                'success': False,
                'message': 'Invalid latency. Must be between 20-8000ms',
                'error': 'validation_error'
            }

        # Check connection
        try:
            self._check_connection()
        except VMixConnectionError as e:
            return {
                'success': False,
                'message': str(e),
                'error': 'connection_error'
            }

        # Configure SRT output
        # vMix SRT configuration via SetOutput
        srt_params = f"{srt_address}?mode={mode}&latency={latency_ms}"
        config_result = self._send_function(
            'SetOutput',
            Value=str(channel),
            **{'Output': 'External2', 'URL': srt_params}
        )

        if not config_result['success']:
            return {
                'success': False,
                'message': f"Failed to configure SRT: {config_result['message']}",
                'error': 'configuration_error'
            }

        # Start streaming
        result = self._send_function('StartStreaming', Value=str(channel))

        if result['success']:
            # Log to IF.witness
            event = {
                'event_type': 'srt_stream_started',
                'timestamp': datetime.utcnow().isoformat(),
                'params': {
                    'protocol': 'SRT',
                    'address': srt_address,
                    'mode': mode,
                    'latency_ms': latency_ms,
                    'channel': channel
                },
                'result': result
            }
            asyncio.create_task(self.log_to_witness(event))

            return {
                'success': True,
                'message': f'SRT stream started ({mode} mode, {latency_ms}ms latency)',
                'protocol': 'SRT',
                'mode': mode,
                'latency_ms': latency_ms,
                'channel': channel
            }

        return result

    def start_recording(
        self,
        filename: Optional[str] = None,
        format: str = "MP4",
        quality: str = "high"
    ) -> Dict:
        """
        Start local recording

        vMix Recording Features:
        - Multiple formats: MP4, AVI, MOV, MKV
        - Quality presets: low, medium, high, custom
        - Multi-track audio recording
        - Automatic filename generation

        Args:
            filename: Output filename (optional, vMix auto-generates if None)
                     Examples: "production_2025-11-12.mp4", "show_episode_01"
            format: Recording format (MP4, AVI, MOV, MKV) - default: MP4
            quality: Recording quality (low, medium, high, custom) - default: high

        Returns:
            dict: {
                'success': bool,
                'message': str,
                'filename': str (if specified),
                'format': str,
                'quality': str
            }

        Example:
            >>> controller.start_recording(
            ...     filename="production_2025-11-12.mp4",
            ...     format="MP4",
            ...     quality="high"
            ... )
        """
        # Validate format
        valid_formats = ['MP4', 'AVI', 'MOV', 'MKV']
        if format.upper() not in valid_formats:
            return {
                'success': False,
                'message': f"Invalid format. Must be one of: {', '.join(valid_formats)}",
                'error': 'validation_error'
            }

        valid_qualities = ['low', 'medium', 'high', 'custom']
        if quality.lower() not in valid_qualities:
            return {
                'success': False,
                'message': f"Invalid quality. Must be one of: {', '.join(valid_qualities)}",
                'error': 'validation_error'
            }

        # Check connection
        try:
            self._check_connection()
        except VMixConnectionError as e:
            return {
                'success': False,
                'message': str(e),
                'error': 'connection_error'
            }

        # Start recording
        # If filename is provided, use SetRecordingFilename first
        if filename:
            filename_result = self._send_function(
                'SetRecordingFilename',
                Value=filename
            )
            if not filename_result['success']:
                return {
                    'success': False,
                    'message': f"Failed to set filename: {filename_result['message']}",
                    'error': 'configuration_error'
                }

        # Start recording
        result = self._send_function('StartRecording')

        if result['success']:
            # Log to IF.witness
            event = {
                'event_type': 'recording_started',
                'timestamp': datetime.utcnow().isoformat(),
                'params': {
                    'filename': filename or 'auto-generated',
                    'format': format,
                    'quality': quality
                },
                'result': result
            }
            asyncio.create_task(self.log_to_witness(event))

            return {
                'success': True,
                'message': 'Recording started',
                'filename': filename or 'auto-generated',
                'format': format,
                'quality': quality
            }

        return result

    def stop_stream(self, channel: int = 0) -> Dict:
        """
        Stop RTMP/SRT streaming on specified channel

        Args:
            channel: Stream channel to stop (0-2, default: 0)

        Returns:
            dict: {'success': bool, 'message': str, 'channel': int}

        Example:
            >>> controller.stop_stream(channel=0)
            {'success': True, 'message': 'Stream stopped', 'channel': 0}
        """
        if channel not in [0, 1, 2]:
            return {
                'success': False,
                'message': 'Invalid channel. Must be 0, 1, or 2',
                'error': 'validation_error'
            }

        result = self._send_function('StopStreaming', Value=str(channel))

        if result['success']:
            # Log to IF.witness
            event = {
                'event_type': 'stream_stopped',
                'timestamp': datetime.utcnow().isoformat(),
                'params': {'channel': channel},
                'result': result
            }
            asyncio.create_task(self.log_to_witness(event))

            return {
                'success': True,
                'message': f'Stream stopped on channel {channel}',
                'channel': channel
            }

        return result

    def stop_recording(self) -> Dict:
        """
        Stop active recording

        Returns:
            dict: {
                'success': bool,
                'message': str,
                'duration': str (if available from status)
            }

        Example:
            >>> controller.stop_recording()
            {'success': True, 'message': 'Recording stopped', 'duration': '00:15:32'}
        """
        # Get duration before stopping
        try:
            status = self.get_stream_status()
            duration = status.get('record_time', 'unknown')
        except:
            duration = 'unknown'

        result = self._send_function('StopRecording')

        if result['success']:
            # Log to IF.witness
            event = {
                'event_type': 'recording_stopped',
                'timestamp': datetime.utcnow().isoformat(),
                'params': {'duration': duration},
                'result': result
            }
            asyncio.create_task(self.log_to_witness(event))

            return {
                'success': True,
                'message': 'Recording stopped',
                'duration': duration
            }

        return result

    def get_stream_status(self) -> Dict:
        """
        Get streaming/recording status from vMix XML API

        Parses vMix XML status for:
        - Streaming state (active channels)
        - Recording state
        - Duration counters
        - Stream destinations

        Returns:
            dict: {
                'streaming': bool,
                'recording': bool,
                'stream_time': str,  # HH:MM:SS
                'record_time': str,
                'stream_channels': List[int],  # Active channels
                'version': str,
                'edition': str
            }

        Example:
            >>> status = controller.get_stream_status()
            >>> print(status['streaming'])
            True
            >>> print(status['stream_channels'])
            [0, 1]
        """
        try:
            xml_root = self._get_xml_status()

            # Parse streaming status
            streaming_elem = xml_root.find('streaming')
            streaming = streaming_elem.text.lower() == 'true' if streaming_elem is not None else False

            # Parse recording status
            recording_elem = xml_root.find('recording')
            recording = recording_elem.text.lower() == 'true' if recording_elem is not None else False

            # Parse durations
            stream_time_elem = xml_root.find('duration')
            stream_time = stream_time_elem.text if stream_time_elem is not None else '00:00:00'

            record_time_elem = xml_root.find('recordingDuration')
            record_time = record_time_elem.text if record_time_elem is not None else '00:00:00'

            # Parse active stream channels
            stream_channels = []
            for i in range(3):
                channel_elem = xml_root.find(f'streaming{i}')
                if channel_elem is not None and channel_elem.text.lower() == 'true':
                    stream_channels.append(i)

            # Parse version info
            version_elem = xml_root.find('version')
            version = version_elem.text if version_elem is not None else 'unknown'

            edition_elem = xml_root.find('edition')
            edition = edition_elem.text if edition_elem is not None else 'unknown'

            return {
                'streaming': streaming,
                'recording': recording,
                'stream_time': stream_time,
                'record_time': record_time,
                'stream_channels': stream_channels,
                'version': version,
                'edition': edition,
                'timestamp': datetime.utcnow().isoformat()
            }

        except VMixAPIError as e:
            return {
                'success': False,
                'message': str(e),
                'error': 'api_error'
            }

    def get_stream_health(self) -> Dict:
        """
        Get stream health metrics from vMix XML

        Monitors:
        - Output bitrate (kbps)
        - Dropped frames
        - Frame rate (FPS)
        - Uptime

        Returns:
            dict: {
                'bitrate_kbps': float,
                'dropped_frames': int,
                'fps': float,
                'uptime_seconds': int,
                'health_status': str ('healthy', 'warning', 'critical')
            }

        Health Status Criteria:
        - healthy: fps >= 29, dropped_frames < 100
        - warning: fps >= 25, dropped_frames < 500
        - critical: fps < 25 or dropped_frames >= 500
        """
        try:
            xml_root = self._get_xml_status()

            # Parse bitrate (from output element)
            outputs = xml_root.findall('.//output')
            bitrate_kbps = 0.0
            for output in outputs:
                bitrate_elem = output.find('bitrate')
                if bitrate_elem is not None:
                    try:
                        bitrate_kbps += float(bitrate_elem.text)
                    except (ValueError, TypeError):
                        pass

            # Parse dropped frames
            dropped_elem = xml_root.find('.//droppedFrames')
            dropped_frames = int(dropped_elem.text) if dropped_elem is not None else 0

            # Parse FPS
            fps_elem = xml_root.find('.//frameRate')
            fps = float(fps_elem.text) if fps_elem is not None else 0.0

            # Parse uptime (from duration)
            duration_elem = xml_root.find('duration')
            uptime_seconds = 0
            if duration_elem is not None:
                # Parse HH:MM:SS format
                try:
                    time_parts = duration_elem.text.split(':')
                    uptime_seconds = (
                        int(time_parts[0]) * 3600 +
                        int(time_parts[1]) * 60 +
                        int(time_parts[2])
                    )
                except (ValueError, IndexError):
                    pass

            # Determine health status
            if fps >= 29 and dropped_frames < 100:
                health_status = 'healthy'
            elif fps >= 25 and dropped_frames < 500:
                health_status = 'warning'
            else:
                health_status = 'critical'

            return {
                'bitrate_kbps': bitrate_kbps,
                'dropped_frames': dropped_frames,
                'fps': fps,
                'uptime_seconds': uptime_seconds,
                'health_status': health_status,
                'timestamp': datetime.utcnow().isoformat()
            }

        except VMixAPIError as e:
            return {
                'success': False,
                'message': str(e),
                'error': 'api_error'
            }

    async def log_to_witness(self, event: Dict):
        """
        Log streaming operations to IF.witness

        Implements hash chain for provenance tracking:
        - Each event is hashed with previous hash
        - Creates tamper-evident audit trail
        - Enables meta-validation of streaming operations

        Args:
            event: Event dictionary containing:
                - event_type: 'stream_started', 'stream_stopped', 'recording_started', etc.
                - timestamp: ISO 8601 timestamp
                - params: Operation parameters
                - result: Operation result

        Example event structure:
            {
                'event_type': 'stream_started',
                'timestamp': '2025-11-12T10:30:00.000Z',
                'params': {
                    'protocol': 'RTMP',
                    'destination': 'rtmp://live.twitch.tv/app/',
                    'channel': 0
                },
                'result': {'success': True}
            }
        """
        # Create hash chain entry
        event_data = json.dumps(event, sort_keys=True)
        current_hash = hashlib.sha256(
            f"{self.last_hash}{event_data}".encode()
        ).hexdigest()

        witness_entry = {
            'event': event,
            'previous_hash': self.last_hash,
            'current_hash': current_hash,
            'witness_timestamp': datetime.utcnow().isoformat()
        }

        # Append to witness log
        self.witness_log.append(witness_entry)
        self.last_hash = current_hash

        # TODO: Persist to IF.witness backend
        # This would integrate with the full IF.witness infrastructure
        # For now, maintaining in-memory log

        return witness_entry

    def get_witness_log(self, event_type: Optional[str] = None) -> List[Dict]:
        """
        Retrieve IF.witness provenance log

        Args:
            event_type: Filter by event type (optional)
                       Options: 'stream_started', 'stream_stopped',
                                'recording_started', 'recording_stopped'

        Returns:
            List of witness entries with hash chain

        Example:
            >>> log = controller.get_witness_log(event_type='stream_started')
            >>> for entry in log:
            ...     print(f"{entry['event']['timestamp']}: {entry['event']['event_type']}")
        """
        if event_type:
            return [
                entry for entry in self.witness_log
                if entry['event']['event_type'] == event_type
            ]
        return self.witness_log

    def verify_witness_chain(self) -> Dict:
        """
        Verify integrity of IF.witness hash chain

        Returns:
            dict: {
                'valid': bool,
                'total_events': int,
                'first_hash': str,
                'last_hash': str,
                'broken_at': int (index if chain is broken, else None)
            }

        Example:
            >>> verification = controller.verify_witness_chain()
            >>> if verification['valid']:
            ...     print("Witness chain is intact")
        """
        if not self.witness_log:
            return {
                'valid': True,
                'total_events': 0,
                'first_hash': self._genesis_hash(),
                'last_hash': self.last_hash,
                'broken_at': None
            }

        # Verify chain continuity
        expected_hash = self._genesis_hash()
        for i, entry in enumerate(self.witness_log):
            if entry['previous_hash'] != expected_hash:
                return {
                    'valid': False,
                    'total_events': len(self.witness_log),
                    'first_hash': self.witness_log[0]['previous_hash'],
                    'last_hash': self.last_hash,
                    'broken_at': i
                }

            # Recompute hash
            event_data = json.dumps(entry['event'], sort_keys=True)
            computed_hash = hashlib.sha256(
                f"{expected_hash}{event_data}".encode()
            ).hexdigest()

            if computed_hash != entry['current_hash']:
                return {
                    'valid': False,
                    'total_events': len(self.witness_log),
                    'first_hash': self.witness_log[0]['previous_hash'],
                    'last_hash': self.last_hash,
                    'broken_at': i
                }

            expected_hash = computed_hash

        return {
            'valid': True,
            'total_events': len(self.witness_log),
            'first_hash': self.witness_log[0]['previous_hash'],
            'last_hash': self.last_hash,
            'broken_at': None
        }


# Convenience functions for common streaming destinations
class StreamingDestinations:
    """
    Pre-configured streaming destinations for popular platforms

    Usage:
        >>> from vmix_streaming import StreamingDestinations
        >>> twitch = StreamingDestinations.twitch("your_stream_key")
        >>> controller.start_rtmp_stream(**twitch)
    """

    @staticmethod
    def twitch(stream_key: str) -> Dict:
        """Twitch streaming configuration"""
        return {
            'rtmp_url': 'rtmp://live.twitch.tv/app/',
            'stream_key': stream_key
        }

    @staticmethod
    def youtube(stream_key: str) -> Dict:
        """YouTube Live streaming configuration"""
        return {
            'rtmp_url': 'rtmp://a.rtmp.youtube.com/live2/',
            'stream_key': stream_key
        }

    @staticmethod
    def facebook(stream_key: str) -> Dict:
        """Facebook Live streaming configuration (secure RTMPS)"""
        return {
            'rtmp_url': 'rtmps://live-api-s.facebook.com:443/rtmp/',
            'stream_key': stream_key
        }

    @staticmethod
    def custom_rtmp(server_url: str, stream_key: str) -> Dict:
        """Custom RTMP server configuration"""
        if not server_url.endswith('/'):
            server_url += '/'
        return {
            'rtmp_url': server_url,
            'stream_key': stream_key
        }


if __name__ == '__main__':
    # Example usage
    print("vMix Streaming Controller - Example Usage")
    print("=" * 50)

    # Initialize controller
    controller = VMixStreamingController(vmix_host='localhost', vmix_port=8088)

    # Example 1: Start Twitch stream
    print("\n1. Start Twitch stream:")
    twitch_config = StreamingDestinations.twitch("your_stream_key_here")
    result = controller.start_rtmp_stream(**twitch_config, channel=0)
    print(f"   Result: {result}")

    # Example 2: Start SRT stream
    print("\n2. Start SRT stream (low latency):")
    result = controller.start_srt_stream(
        srt_address="srt://192.168.1.100:9000",
        mode="caller",
        latency_ms=120
    )
    print(f"   Result: {result}")

    # Example 3: Start recording
    print("\n3. Start recording:")
    result = controller.start_recording(
        filename="production_2025-11-12.mp4",
        format="MP4",
        quality="high"
    )
    print(f"   Result: {result}")

    # Example 4: Get status
    print("\n4. Get stream status:")
    status = controller.get_stream_status()
    print(f"   Streaming: {status.get('streaming')}")
    print(f"   Recording: {status.get('recording')}")
    print(f"   Active channels: {status.get('stream_channels')}")

    # Example 5: Get health metrics
    print("\n5. Get stream health:")
    health = controller.get_stream_health()
    print(f"   Health status: {health.get('health_status')}")
    print(f"   FPS: {health.get('fps')}")
    print(f"   Bitrate: {health.get('bitrate_kbps')} kbps")

    # Example 6: Verify witness chain
    print("\n6. Verify IF.witness chain:")
    verification = controller.verify_witness_chain()
    print(f"   Valid: {verification['valid']}")
    print(f"   Total events: {verification['total_events']}")
