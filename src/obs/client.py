"""
IF.obs WebSocket Client

WebSocket client for OBS Studio control via obs-websocket v5.x protocol.
"""

from typing import Dict, Any, Optional, List
import json

try:
    from obswebsocket import obsws, requests as obs_requests
    from obswebsocket.exceptions import ConnectionFailure, MessageTimeout
    HAS_OBS_WEBSOCKET = True
except ImportError:
    HAS_OBS_WEBSOCKET = False
    obsws = None
    obs_requests = None
    ConnectionFailure = Exception
    MessageTimeout = Exception

from .models import (
    OBSScene, OBSSource, OBSStreamStatus, OBSRecordStatus,
    OBSStats, OBSVersion, OBSFilter
)


class OBSError(Exception):
    """Base exception for OBS errors"""
    pass


class OBSConnectionError(OBSError):
    """Connection error to OBS"""
    pass


class OBSAPIError(OBSError):
    """OBS API error"""
    pass


class OBSClient:
    """
    OBS WebSocket API client.

    Philosophy: Simple, synchronous client for production control.
    Every operation is a WebSocket RPC call to obs-websocket.

    API Reference: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md
    """

    def __init__(self, host: str, port: int = 4455, password: Optional[str] = None, timeout: int = 5):
        """
        Initialize OBS client.

        Args:
            host: OBS host IP or hostname
            port: OBS WebSocket port (default: 4455)
            password: WebSocket password (optional)
            timeout: Request timeout in seconds

        Raises:
            OBSError: If obs-websocket-py is not installed
        """
        if not HAS_OBS_WEBSOCKET:
            raise OBSError(
                "obs-websocket-py is not installed. "
                "Install with: pip install obs-websocket-py"
            )

        self.host = host
        self.port = port
        self.password = password or ""
        self.timeout = timeout
        self.ws = None
        self._connected = False

    def connect(self):
        """
        Connect to OBS WebSocket.

        Raises:
            OBSConnectionError: If connection fails
        """
        try:
            self.ws = obsws(self.host, self.port, self.password, timeout=self.timeout)
            self.ws.connect()
            self._connected = True
        except ConnectionFailure as e:
            raise OBSConnectionError(
                f"Cannot connect to OBS at {self.host}:{self.port}: {e}"
            )
        except Exception as e:
            raise OBSConnectionError(f"Connection error: {e}")

    def disconnect(self):
        """Disconnect from OBS WebSocket"""
        if self.ws and self._connected:
            try:
                self.ws.disconnect()
            except Exception:
                pass
            finally:
                self._connected = False

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

    def _call(self, request):
        """
        Execute OBS WebSocket request.

        Args:
            request: obs-websocket request object

        Returns:
            Response data

        Raises:
            OBSConnectionError: If not connected
            OBSAPIError: If request fails
        """
        if not self._connected:
            self.connect()

        try:
            response = self.ws.call(request)
            return response
        except MessageTimeout:
            raise OBSAPIError("Request timeout")
        except Exception as e:
            raise OBSAPIError(f"Request failed: {e}")

    # ============================================================================
    # Version & Status
    # ============================================================================

    def get_version(self) -> OBSVersion:
        """
        Get OBS and WebSocket version information.

        Returns:
            OBSVersion object
        """
        response = self._call(obs_requests.GetVersion())

        return OBSVersion(
            obs_version=response.datain.get('obsVersion', 'unknown'),
            obs_web_socket_version=response.datain.get('obsWebSocketVersion', 'unknown'),
            rpc_version=response.datain.get('rpcVersion', 1),
            available_requests=response.datain.get('availableRequests', []),
            supported_image_formats=response.datain.get('supportedImageFormats', []),
            platform=response.datain.get('platform'),
            platform_description=response.datain.get('platformDescription')
        )

    def get_stats(self) -> OBSStats:
        """
        Get OBS statistics (CPU, memory, FPS, dropped frames, etc.).

        Returns:
            OBSStats object
        """
        response = self._call(obs_requests.GetStats())
        data = response.datain

        return OBSStats(
            cpu_usage=data.get('cpuUsage', 0.0),
            memory_usage=data.get('memoryUsage', 0.0),
            available_disk_space=data.get('availableDiskSpace', 0.0),
            active_fps=data.get('activeFps', 0.0),
            average_frame_render_time=data.get('averageFrameRenderTime', 0.0),
            render_skipped_frames=data.get('renderSkippedFrames', 0),
            render_total_frames=data.get('renderTotalFrames', 0),
            output_skipped_frames=data.get('outputSkippedFrames', 0),
            output_total_frames=data.get('outputTotalFrames', 0),
            web_socket_session_incoming_messages=data.get('webSocketSessionIncomingMessages'),
            web_socket_session_outgoing_messages=data.get('webSocketSessionOutgoingMessages')
        )

    # ============================================================================
    # Scene Management
    # ============================================================================

    def get_scene_list(self) -> List[OBSScene]:
        """
        Get list of all scenes.

        Returns:
            List of OBSScene objects
        """
        response = self._call(obs_requests.GetSceneList())
        current_scene = response.datain.get('currentProgramSceneName')
        scenes = []

        for idx, scene_data in enumerate(response.datain.get('scenes', [])):
            scene_name = scene_data.get('sceneName', scene_data.get('name', ''))
            scenes.append(OBSScene(
                name=scene_name,
                index=idx,
                is_current=(scene_name == current_scene)
            ))

        return scenes

    def get_current_scene(self) -> str:
        """
        Get current program scene name.

        Returns:
            Scene name
        """
        response = self._call(obs_requests.GetCurrentProgramScene())
        return response.datain.get('currentProgramSceneName', '')

    def set_current_scene(self, scene_name: str):
        """
        Switch to a different scene.

        Args:
            scene_name: Name of scene to switch to
        """
        self._call(obs_requests.SetCurrentProgramScene(sceneName=scene_name))

    def create_scene(self, scene_name: str):
        """
        Create a new scene.

        Args:
            scene_name: Name for the new scene
        """
        self._call(obs_requests.CreateScene(sceneName=scene_name))

    def remove_scene(self, scene_name: str):
        """
        Remove a scene.

        Args:
            scene_name: Name of scene to remove
        """
        self._call(obs_requests.RemoveScene(sceneName=scene_name))

    # ============================================================================
    # Source Management
    # ============================================================================

    def get_scene_items(self, scene_name: str) -> List[OBSSource]:
        """
        Get all sources (scene items) in a scene.

        Args:
            scene_name: Scene name

        Returns:
            List of OBSSource objects
        """
        response = self._call(obs_requests.GetSceneItemList(sceneName=scene_name))
        sources = []

        for item in response.datain.get('sceneItems', []):
            sources.append(OBSSource(
                name=item.get('sourceName', ''),
                type=item.get('sourceType', ''),
                scene_item_id=item.get('sceneItemId'),
                scene_item_enabled=item.get('sceneItemEnabled', True)
            ))

        return sources

    def create_input(self, scene_name: str, input_name: str, input_kind: str,
                    input_settings: Optional[Dict[str, Any]] = None):
        """
        Create a new input source and add to scene.

        Args:
            scene_name: Scene to add source to
            input_name: Name for the input
            input_kind: Input kind (e.g., 'browser_source', 'ffmpeg_source', 'v4l2_input')
            input_settings: Input-specific settings
        """
        # Create the input
        self._call(obs_requests.CreateInput(
            sceneName=scene_name,
            inputName=input_name,
            inputKind=input_kind,
            inputSettings=input_settings or {}
        ))

    def remove_input(self, input_name: str):
        """
        Remove an input source.

        Args:
            input_name: Name of input to remove
        """
        self._call(obs_requests.RemoveInput(inputName=input_name))

    def set_scene_item_enabled(self, scene_name: str, item_id: int, enabled: bool):
        """
        Show or hide a source in a scene.

        Args:
            scene_name: Scene name
            item_id: Scene item ID
            enabled: True to show, False to hide
        """
        self._call(obs_requests.SetSceneItemEnabled(
            sceneName=scene_name,
            sceneItemId=item_id,
            sceneItemEnabled=enabled
        ))

    def get_input_settings(self, input_name: str) -> Dict[str, Any]:
        """
        Get input source settings.

        Args:
            input_name: Input name

        Returns:
            Settings dictionary
        """
        response = self._call(obs_requests.GetInputSettings(inputName=input_name))
        return response.datain.get('inputSettings', {})

    def set_input_settings(self, input_name: str, settings: Dict[str, Any]):
        """
        Update input source settings.

        Args:
            input_name: Input name
            settings: Settings to update
        """
        self._call(obs_requests.SetInputSettings(
            inputName=input_name,
            inputSettings=settings
        ))

    # ============================================================================
    # Streaming
    # ============================================================================

    def start_stream(self):
        """Start streaming"""
        self._call(obs_requests.StartStream())

    def stop_stream(self):
        """Stop streaming"""
        self._call(obs_requests.StopStream())

    def get_stream_status(self) -> OBSStreamStatus:
        """
        Get streaming status.

        Returns:
            OBSStreamStatus object
        """
        response = self._call(obs_requests.GetStreamStatus())
        data = response.datain

        return OBSStreamStatus(
            active=data.get('outputActive', False),
            reconnecting=data.get('outputReconnecting', False),
            timecode=data.get('outputTimecode'),
            duration=data.get('outputDuration'),
            congestion=data.get('outputCongestion'),
            bytes_sent=data.get('outputBytes'),
            total_frames=data.get('outputTotalFrames')
        )

    # ============================================================================
    # Recording
    # ============================================================================

    def start_record(self):
        """Start recording"""
        self._call(obs_requests.StartRecord())

    def stop_record(self):
        """Stop recording"""
        self._call(obs_requests.StopRecord())

    def pause_record(self):
        """Pause recording"""
        self._call(obs_requests.PauseRecord())

    def resume_record(self):
        """Resume recording"""
        self._call(obs_requests.ResumeRecord())

    def get_record_status(self) -> OBSRecordStatus:
        """
        Get recording status.

        Returns:
            OBSRecordStatus object
        """
        response = self._call(obs_requests.GetRecordStatus())
        data = response.datain

        return OBSRecordStatus(
            active=data.get('outputActive', False),
            paused=data.get('outputPaused', False),
            timecode=data.get('outputTimecode'),
            duration=data.get('outputDuration'),
            bytes=data.get('outputBytes')
        )

    # ============================================================================
    # Virtual Camera
    # ============================================================================

    def start_virtual_cam(self):
        """Start virtual camera"""
        self._call(obs_requests.StartVirtualCam())

    def stop_virtual_cam(self):
        """Stop virtual camera"""
        self._call(obs_requests.StopVirtualCam())

    def get_virtual_cam_status(self) -> bool:
        """
        Get virtual camera status.

        Returns:
            True if active, False otherwise
        """
        response = self._call(obs_requests.GetVirtualCamStatus())
        return response.datain.get('outputActive', False)

    # ============================================================================
    # Filters
    # ============================================================================

    def get_source_filters(self, source_name: str) -> List[OBSFilter]:
        """
        Get all filters on a source.

        Args:
            source_name: Source name

        Returns:
            List of OBSFilter objects
        """
        response = self._call(obs_requests.GetSourceFilterList(sourceName=source_name))
        filters = []

        for filter_data in response.datain.get('filters', []):
            filters.append(OBSFilter(
                name=filter_data.get('filterName', ''),
                type=filter_data.get('filterKind', ''),
                enabled=filter_data.get('filterEnabled', True),
                settings=filter_data.get('filterSettings', {})
            ))

        return filters

    def create_source_filter(self, source_name: str, filter_name: str,
                            filter_kind: str, filter_settings: Optional[Dict[str, Any]] = None):
        """
        Create a filter on a source.

        Args:
            source_name: Source to add filter to
            filter_name: Name for the filter
            filter_kind: Filter type (e.g., 'chroma_key_filter', 'color_correction_filter')
            filter_settings: Filter-specific settings
        """
        self._call(obs_requests.CreateSourceFilter(
            sourceName=source_name,
            filterName=filter_name,
            filterKind=filter_kind,
            filterSettings=filter_settings or {}
        ))

    def remove_source_filter(self, source_name: str, filter_name: str):
        """
        Remove a filter from a source.

        Args:
            source_name: Source name
            filter_name: Filter name
        """
        self._call(obs_requests.RemoveSourceFilter(
            sourceName=source_name,
            filterName=filter_name
        ))

    def set_source_filter_enabled(self, source_name: str, filter_name: str, enabled: bool):
        """
        Enable or disable a filter.

        Args:
            source_name: Source name
            filter_name: Filter name
            enabled: True to enable, False to disable
        """
        self._call(obs_requests.SetSourceFilterEnabled(
            sourceName=source_name,
            filterName=filter_name,
            filterEnabled=enabled
        ))

    # ============================================================================
    # Media Control
    # ============================================================================

    def trigger_media_input_action(self, input_name: str, action: str):
        """
        Control media playback (play, pause, stop, restart, next, previous).

        Args:
            input_name: Media input name
            action: Action to trigger (OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PLAY, etc.)
        """
        self._call(obs_requests.TriggerMediaInputAction(
            inputName=input_name,
            mediaAction=action
        ))

    def play_media(self, input_name: str):
        """Play media input"""
        self.trigger_media_input_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PLAY")

    def pause_media(self, input_name: str):
        """Pause media input"""
        self.trigger_media_input_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PAUSE")

    def stop_media(self, input_name: str):
        """Stop media input"""
        self.trigger_media_input_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_STOP")

    def restart_media(self, input_name: str):
        """Restart media input from beginning"""
        self.trigger_media_input_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART")
