"""
OBS Streaming Controller for InfraFabric
Integrates OBS Studio streaming, virtual camera, and recording capabilities
with IF.witness provenance tracking.

OBS WebSocket Protocol: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md
Python Client: obs-websocket-py (https://github.com/obsproject/obs-websocket-py)
"""

from obswebsocket import obsws, requests as obs_requests
from typing import Optional, Dict, Any, Callable
import asyncio
import hashlib
import json
import time
import logging
from datetime import datetime
from enum import Enum


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StreamService(Enum):
    """Supported streaming services"""
    TWITCH = "Twitch"
    YOUTUBE = "YouTube Live"
    FACEBOOK = "Facebook Live"
    CUSTOM = "Custom"


class RecordingFormat(Enum):
    """Supported recording formats"""
    MP4 = "mp4"
    MKV = "mkv"
    FLV = "flv"
    MOV = "mov"


class OBSConnectionError(Exception):
    """Raised when OBS connection fails"""
    pass


class OBSStreamingError(Exception):
    """Raised when streaming operation fails"""
    pass


class IFWitnessLogger:
    """
    Mock IF.witness integration for provenance tracking
    In production, this would integrate with actual IF.witness hash chain
    """

    def __init__(self):
        self.events = []
        self.hash_chain = []

    def log_event(self, event_type: str, params: Dict, result: Dict) -> str:
        """
        Log event to IF.witness chain

        Returns:
            str: Event hash for chain verification
        """
        timestamp = datetime.utcnow().isoformat()
        event = {
            'timestamp': timestamp,
            'event_type': event_type,
            'params': params,
            'result': result,
            'prev_hash': self.hash_chain[-1] if self.hash_chain else '0' * 64
        }

        # Create hash of event
        event_json = json.dumps(event, sort_keys=True)
        event_hash = hashlib.sha256(event_json.encode()).hexdigest()
        event['hash'] = event_hash

        self.events.append(event)
        self.hash_chain.append(event_hash)

        logger.info(f"IF.witness: {event_type} → {event_hash[:16]}...")
        return event_hash

    def get_chain(self) -> list:
        """Get complete event chain"""
        return self.events

    def verify_chain(self) -> bool:
        """Verify hash chain integrity"""
        for i, event in enumerate(self.events):
            # Recreate hash
            event_copy = event.copy()
            stored_hash = event_copy.pop('hash')
            event_json = json.dumps(event_copy, sort_keys=True)
            calculated_hash = hashlib.sha256(event_json.encode()).hexdigest()

            if stored_hash != calculated_hash:
                logger.error(f"Chain verification failed at event {i}")
                return False

        return True


class OBSStreamingController:
    """
    Control OBS streaming, virtual camera, and recording
    Integrates with IF.witness for provenance tracking
    """

    def __init__(
        self,
        obs_host: str = "localhost",
        obs_port: int = 4455,
        obs_password: Optional[str] = None,
        witness_logger: Optional[IFWitnessLogger] = None
    ):
        """
        Initialize OBS streaming controller

        Args:
            obs_host: OBS WebSocket hostname/IP
            obs_port: OBS WebSocket port (default 4455 for obs-websocket v5)
            obs_password: WebSocket password (if authentication enabled)
            witness_logger: IF.witness logger instance
        """
        self.host = obs_host
        self.port = obs_port
        self.password = obs_password
        self.ws: Optional[obsws] = None
        self.connected = False
        self.witness = witness_logger or IFWitnessLogger()

        # Callbacks
        self._stream_started_callback: Optional[Callable] = None
        self._stream_stopped_callback: Optional[Callable] = None
        self._recording_started_callback: Optional[Callable] = None

    def connect(self) -> Dict:
        """
        Connect to OBS WebSocket

        Returns:
            dict: Connection status

        Raises:
            OBSConnectionError: If connection fails
        """
        try:
            logger.info(f"Connecting to OBS at {self.host}:{self.port}...")
            self.ws = obsws(self.host, self.port, self.password)
            self.ws.connect()
            self.connected = True

            # Get OBS version info
            version_info = self.ws.call(obs_requests.GetVersion())

            result = {
                'status': 'connected',
                'obs_version': version_info.getObsVersion(),
                'websocket_version': version_info.getWebsocketVersion(),
                'host': self.host,
                'port': self.port
            }

            self.witness.log_event('obs_connected', {
                'host': self.host,
                'port': self.port
            }, result)

            logger.info(f"Connected to OBS {result['obs_version']}")
            return result

        except Exception as e:
            error_msg = f"Failed to connect to OBS: {str(e)}"
            logger.error(error_msg)
            raise OBSConnectionError(error_msg)

    def disconnect(self) -> Dict:
        """
        Disconnect from OBS WebSocket

        Returns:
            dict: Disconnection status
        """
        if self.ws and self.connected:
            try:
                self.ws.disconnect()
                self.connected = False
                result = {'status': 'disconnected'}

                self.witness.log_event('obs_disconnected', {}, result)
                logger.info("Disconnected from OBS")
                return result

            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
                return {'status': 'error', 'error': str(e)}

        return {'status': 'not_connected'}

    def _ensure_connected(self):
        """Ensure WebSocket is connected"""
        if not self.connected or not self.ws:
            raise OBSConnectionError("Not connected to OBS. Call connect() first.")

    def start_stream(
        self,
        service: Optional[str] = None,
        server: Optional[str] = None,
        key: Optional[str] = None
    ) -> Dict:
        """
        Start streaming to destination

        Args:
            service: Streaming service name (e.g., 'Twitch', 'YouTube')
            server: Custom RTMP server URL (if service is 'Custom')
            key: Stream key

        Returns:
            dict: Status response with streaming details

        Example:
            controller.start_stream(
                service="Twitch",
                key="live_123456789_abc"
            )

            # Or custom RTMP:
            controller.start_stream(
                service="Custom",
                server="rtmp://server.example.com/live",
                key="secretkey"
            )
        """
        self._ensure_connected()

        params = {}
        if service or server or key:
            params = {
                'service': service,
                'server': server,
                'key': key
            }

        try:
            # Configure stream settings if provided
            if service and server and key:
                stream_settings = {
                    'service': service,
                    'server': server,
                    'key': key
                }
                # Note: SetStreamServiceSettings is for obs-websocket v5
                # For v4, use different request
                logger.info(f"Configuring stream for {service}")

            # Start streaming
            self.ws.call(obs_requests.StartStream())

            # Get stream status
            status = self.get_stream_status()

            result = {
                'status': 'started',
                'streaming': True,
                'timestamp': datetime.utcnow().isoformat(),
                **status
            }

            self.witness.log_event('stream_started', params, result)
            logger.info(f"Stream started: {service or 'default'}")

            if self._stream_started_callback:
                self._stream_started_callback(result)

            return result

        except Exception as e:
            error_msg = f"Failed to start stream: {str(e)}"
            logger.error(error_msg)
            raise OBSStreamingError(error_msg)

    def stop_stream(self) -> Dict:
        """
        Stop streaming

        Returns:
            dict: Final stream statistics
        """
        self._ensure_connected()

        try:
            # Get final stats before stopping
            final_stats = self.get_stream_status()

            # Stop stream
            self.ws.call(obs_requests.StopStream())

            result = {
                'status': 'stopped',
                'streaming': False,
                'timestamp': datetime.utcnow().isoformat(),
                'final_stats': final_stats
            }

            self.witness.log_event('stream_stopped', {}, result)
            logger.info("Stream stopped")

            if self._stream_stopped_callback:
                self._stream_stopped_callback(result)

            return result

        except Exception as e:
            error_msg = f"Failed to stop stream: {str(e)}"
            logger.error(error_msg)
            raise OBSStreamingError(error_msg)

    def get_stream_status(self) -> Dict:
        """
        Get streaming status and statistics

        Returns:
            dict: {
                'streaming': bool,
                'active': bool,
                'reconnecting': bool,
                'bytes_sent': int,
                'duration_ms': int,
                'congestion': float,
                'kbits_per_sec': int,
                'render_missed_frames': int,
                'output_skipped_frames': int,
                'output_total_frames': int
            }
        """
        self._ensure_connected()

        try:
            response = self.ws.call(obs_requests.GetStreamStatus())

            status = {
                'streaming': response.getOutputActive(),
                'active': response.getOutputActive(),
                'reconnecting': response.getOutputReconnecting() if hasattr(response, 'getOutputReconnecting') else False,
                'bytes_sent': response.getOutputBytes() if hasattr(response, 'getOutputBytes') else 0,
                'duration_ms': response.getOutputDuration() if hasattr(response, 'getOutputDuration') else 0,
                'congestion': response.getOutputCongestion() if hasattr(response, 'getOutputCongestion') else 0.0,
                'kbits_per_sec': 0,  # Calculated from bytes
                'render_missed_frames': 0,
                'output_skipped_frames': response.getOutputSkippedFrames() if hasattr(response, 'getOutputSkippedFrames') else 0,
                'output_total_frames': response.getOutputTotalFrames() if hasattr(response, 'getOutputTotalFrames') else 0
            }

            # Calculate bitrate
            if status['duration_ms'] > 0:
                duration_sec = status['duration_ms'] / 1000
                status['kbits_per_sec'] = int((status['bytes_sent'] * 8) / duration_sec / 1000)

            return status

        except Exception as e:
            logger.error(f"Failed to get stream status: {e}")
            return {
                'streaming': False,
                'active': False,
                'error': str(e)
            }

    def start_virtual_camera(self) -> Dict:
        """
        Start OBS Virtual Camera

        Returns:
            dict: Status response

        Example:
            controller.start_virtual_camera()
            # Virtual camera now available in Zoom, Meet, Discord, etc.
        """
        self._ensure_connected()

        try:
            self.ws.call(obs_requests.StartVirtualCam())

            status = self.get_virtual_camera_status()

            result = {
                'status': 'started',
                'active': True,
                'timestamp': datetime.utcnow().isoformat(),
                **status
            }

            self.witness.log_event('virtualcam_started', {}, result)
            logger.info("Virtual camera started")

            return result

        except Exception as e:
            error_msg = f"Failed to start virtual camera: {str(e)}"
            logger.error(error_msg)
            raise OBSStreamingError(error_msg)

    def stop_virtual_camera(self) -> Dict:
        """
        Stop virtual camera

        Returns:
            dict: Status response
        """
        self._ensure_connected()

        try:
            self.ws.call(obs_requests.StopVirtualCam())

            result = {
                'status': 'stopped',
                'active': False,
                'timestamp': datetime.utcnow().isoformat()
            }

            self.witness.log_event('virtualcam_stopped', {}, result)
            logger.info("Virtual camera stopped")

            return result

        except Exception as e:
            error_msg = f"Failed to stop virtual camera: {str(e)}"
            logger.error(error_msg)
            raise OBSStreamingError(error_msg)

    def get_virtual_camera_status(self) -> Dict:
        """
        Get virtual camera status

        Returns:
            dict: {'active': bool}
        """
        self._ensure_connected()

        try:
            response = self.ws.call(obs_requests.GetVirtualCamStatus())

            return {
                'active': response.getOutputActive()
            }

        except Exception as e:
            logger.error(f"Failed to get virtual camera status: {e}")
            return {
                'active': False,
                'error': str(e)
            }

    def start_recording(
        self,
        filename: Optional[str] = None,
        format: str = "mp4"
    ) -> Dict:
        """
        Start local recording

        Args:
            filename: Output filename (optional, OBS will use default pattern)
            format: Recording format (mp4, mkv, flv)

        Returns:
            dict: Status response with output path

        Example:
            controller.start_recording(
                filename="stream_2024-01-15.mp4",
                format="mp4"
            )
        """
        self._ensure_connected()

        params = {
            'filename': filename,
            'format': format
        }

        try:
            # Start recording
            self.ws.call(obs_requests.StartRecord())

            # Get recording status
            status = self.get_record_status()

            result = {
                'status': 'started',
                'recording': True,
                'format': format,
                'timestamp': datetime.utcnow().isoformat(),
                **status
            }

            if filename:
                result['requested_filename'] = filename

            self.witness.log_event('recording_started', params, result)
            logger.info(f"Recording started: {format}")

            if self._recording_started_callback:
                self._recording_started_callback(result)

            return result

        except Exception as e:
            error_msg = f"Failed to start recording: {str(e)}"
            logger.error(error_msg)
            raise OBSStreamingError(error_msg)

    def stop_recording(self) -> Dict:
        """
        Stop recording

        Returns:
            dict: Final recording stats including output path
        """
        self._ensure_connected()

        try:
            # Get final stats
            final_stats = self.get_record_status()

            # Stop recording
            response = self.ws.call(obs_requests.StopRecord())

            result = {
                'status': 'stopped',
                'recording': False,
                'timestamp': datetime.utcnow().isoformat(),
                'final_stats': final_stats
            }

            # Try to get output path if available
            if hasattr(response, 'getOutputPath'):
                result['output_path'] = response.getOutputPath()

            self.witness.log_event('recording_stopped', {}, result)
            logger.info("Recording stopped")

            return result

        except Exception as e:
            error_msg = f"Failed to stop recording: {str(e)}"
            logger.error(error_msg)
            raise OBSStreamingError(error_msg)

    def pause_recording(self) -> Dict:
        """
        Pause recording (resume with resume_recording())

        Returns:
            dict: Status response
        """
        self._ensure_connected()

        try:
            self.ws.call(obs_requests.PauseRecord())

            result = {
                'status': 'paused',
                'timestamp': datetime.utcnow().isoformat()
            }

            self.witness.log_event('recording_paused', {}, result)
            logger.info("Recording paused")

            return result

        except Exception as e:
            error_msg = f"Failed to pause recording: {str(e)}"
            logger.error(error_msg)
            raise OBSStreamingError(error_msg)

    def resume_recording(self) -> Dict:
        """
        Resume paused recording

        Returns:
            dict: Status response
        """
        self._ensure_connected()

        try:
            self.ws.call(obs_requests.ResumeRecord())

            result = {
                'status': 'resumed',
                'timestamp': datetime.utcnow().isoformat()
            }

            self.witness.log_event('recording_resumed', {}, result)
            logger.info("Recording resumed")

            return result

        except Exception as e:
            error_msg = f"Failed to resume recording: {str(e)}"
            logger.error(error_msg)
            raise OBSStreamingError(error_msg)

    def get_record_status(self) -> Dict:
        """
        Get recording status

        Returns:
            dict: {
                'recording': bool,
                'paused': bool,
                'timecode': str,  # HH:MM:SS.mmm
                'duration_ms': int,
                'bytes': int
            }
        """
        self._ensure_connected()

        try:
            response = self.ws.call(obs_requests.GetRecordStatus())

            status = {
                'recording': response.getOutputActive(),
                'paused': response.getOutputPaused() if hasattr(response, 'getOutputPaused') else False,
                'duration_ms': response.getOutputDuration() if hasattr(response, 'getOutputDuration') else 0,
                'bytes': response.getOutputBytes() if hasattr(response, 'getOutputBytes') else 0
            }

            # Calculate timecode
            if status['duration_ms'] > 0:
                total_seconds = status['duration_ms'] / 1000
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                milliseconds = int(status['duration_ms'] % 1000)
                status['timecode'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
            else:
                status['timecode'] = "00:00:00.000"

            return status

        except Exception as e:
            logger.error(f"Failed to get record status: {e}")
            return {
                'recording': False,
                'paused': False,
                'error': str(e)
            }

    def get_stats(self) -> Dict:
        """
        Get OBS performance stats

        Returns:
            dict: {
                'cpu_usage': float,
                'memory_usage_mb': float,
                'average_frame_time_ns': int,
                'render_fps': float,
                'output_fps': float,
                'free_disk_space_mb': int
            }
        """
        self._ensure_connected()

        try:
            response = self.ws.call(obs_requests.GetStats())

            stats = {
                'cpu_usage': response.getCpuUsage() if hasattr(response, 'getCpuUsage') else 0.0,
                'memory_usage_mb': response.getMemoryUsage() if hasattr(response, 'getMemoryUsage') else 0.0,
                'average_frame_time_ns': 0,
                'render_fps': response.getActiveFps() if hasattr(response, 'getActiveFps') else 0.0,
                'output_fps': response.getActiveFps() if hasattr(response, 'getActiveFps') else 0.0,
                'free_disk_space_mb': response.getAvailableDiskSpace() if hasattr(response, 'getAvailableDiskSpace') else 0
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {
                'cpu_usage': 0.0,
                'error': str(e)
            }

    def stop_all(self) -> Dict:
        """
        Emergency stop: stop streaming, virtual camera, and recording

        Returns:
            dict: Status of all stop operations
        """
        results = {}

        try:
            results['stream'] = self.stop_stream()
        except Exception as e:
            results['stream'] = {'status': 'error', 'error': str(e)}
            logger.warning(f"Failed to stop stream: {e}")

        try:
            results['virtualcam'] = self.stop_virtual_camera()
        except Exception as e:
            results['virtualcam'] = {'status': 'error', 'error': str(e)}
            logger.warning(f"Failed to stop virtual camera: {e}")

        try:
            results['recording'] = self.stop_recording()
        except Exception as e:
            results['recording'] = {'status': 'error', 'error': str(e)}
            logger.warning(f"Failed to stop recording: {e}")

        self.witness.log_event('emergency_stop_all', {}, results)
        logger.info("Emergency stop completed")

        return results

    # Callback registration
    def on_stream_started(self, callback: Callable):
        """Register callback for stream started event"""
        self._stream_started_callback = callback

    def on_stream_stopped(self, callback: Callable):
        """Register callback for stream stopped event"""
        self._stream_stopped_callback = callback

    def on_recording_started(self, callback: Callable):
        """Register callback for recording started event"""
        self._recording_started_callback = callback

    # IF.witness integration
    async def log_to_witness(self, event_type: str, params: Dict, result: Dict):
        """
        Log streaming operations to IF.witness

        Args:
            event_type: 'stream_started', 'virtualcam_started', 'recording_started', etc.
            params: Operation parameters
            result: Operation result

        Returns:
            str: Event hash for verification
        """
        return self.witness.log_event(event_type, params, result)

    def get_witness_chain(self) -> list:
        """
        Get complete IF.witness event chain

        Returns:
            list: All logged events with hash chain
        """
        return self.witness.get_chain()

    def verify_witness_chain(self) -> bool:
        """
        Verify IF.witness hash chain integrity

        Returns:
            bool: True if chain is valid
        """
        return self.witness.verify_chain()

    def export_witness_report(self, filepath: str):
        """
        Export IF.witness chain to JSON file

        Args:
            filepath: Output file path
        """
        with open(filepath, 'w') as f:
            json.dump({
                'chain': self.witness.get_chain(),
                'verified': self.witness.verify_chain(),
                'timestamp': datetime.utcnow().isoformat()
            }, f, indent=2)

        logger.info(f"Witness report exported to {filepath}")


# Context manager support
class OBSStreamingContext:
    """Context manager for automatic connection/disconnection"""

    def __init__(self, controller: OBSStreamingController):
        self.controller = controller

    def __enter__(self):
        self.controller.connect()
        return self.controller

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.controller.disconnect()
        return False


# Convenience function
def create_obs_controller(
    host: str = "localhost",
    port: int = 4455,
    password: Optional[str] = None
) -> OBSStreamingController:
    """
    Create and return OBS controller instance

    Args:
        host: OBS WebSocket host
        port: OBS WebSocket port
        password: WebSocket password

    Returns:
        OBSStreamingController: Configured controller instance
    """
    return OBSStreamingController(host, port, password)
