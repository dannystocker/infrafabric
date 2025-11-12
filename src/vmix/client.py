"""
IF.vmix API Client

REST API client for vMix control and status queries.
Supports both Function API calls and XML status parsing.
"""

import requests
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode

from .models import VMixStatus, VMixInput, VMixStreamStatus, VMixRecordStatus


class VMixError(Exception):
    """Base exception for vMix errors"""
    pass


class VMixConnectionError(VMixError):
    """Connection error to vMix"""
    pass


class VMixAPIError(VMixError):
    """vMix API error"""
    pass


class VMixClient:
    """
    vMix API client for REST + XML status.

    Philosophy: Simple, synchronous client for production control.
    Every operation is a single HTTP GET request.

    API Reference: https://www.vmix.com/help25/index.htm?DeveloperAPI.html
    """

    def __init__(self, host: str, port: int = 8088, timeout: int = 5):
        """
        Initialize vMix client.

        Args:
            host: vMix host IP or hostname
            port: vMix API port (default: 8088)
            timeout: Request timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}/api/"

    def execute_function(self, function: str, **params) -> bool:
        """
        Execute vMix Function API call.

        Args:
            function: vMix function name (e.g., "Cut", "Fade", "PreviewInput")
            **params: Function parameters (e.g., Input=1, Duration=2000)

        Returns:
            True if successful

        Raises:
            VMixConnectionError: If unable to connect
            VMixAPIError: If API returns error

        Example:
            client.execute_function("Cut", Input=1)
            client.execute_function("Fade", Input=2, Duration=2000)
        """
        try:
            # Build URL with function and parameters
            query_params = {'Function': function, **params}
            url = f"{self.base_url}?{urlencode(query_params)}"

            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            return True

        except requests.exceptions.ConnectionError as e:
            raise VMixConnectionError(f"Cannot connect to vMix at {self.host}:{self.port}: {e}")
        except requests.exceptions.Timeout:
            raise VMixConnectionError(f"Timeout connecting to vMix at {self.host}:{self.port}")
        except requests.exceptions.HTTPError as e:
            raise VMixAPIError(f"vMix API error: {e}")
        except Exception as e:
            raise VMixError(f"Unexpected error: {e}")

    def get_status(self) -> VMixStatus:
        """
        Get vMix status (XML format).

        Returns:
            VMixStatus with current system state

        Raises:
            VMixConnectionError: If unable to connect
            VMixAPIError: If XML parsing fails

        Example XML:
            <vmix>
              <version>25.0.0.65</version>
              <edition>4K</edition>
              <inputs>
                <input key="1" number="1" type="Video" state="Running">Camera 1</input>
                <input key="2" number="2" type="NDI" state="Running">NDI Source</input>
              </inputs>
              <active>1</active>
              <preview>2</preview>
              <recording>False</recording>
              <streaming>False</streaming>
              <audio>True</audio>
            </vmix>
        """
        try:
            response = requests.get(self.base_url, timeout=self.timeout)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.text)

            # Extract basic info
            version = root.find('version').text if root.find('version') is not None else 'unknown'
            edition = root.find('edition').text if root.find('edition') is not None else 'unknown'

            # Parse inputs
            inputs = []
            inputs_elem = root.find('inputs')
            if inputs_elem is not None:
                for input_elem in inputs_elem.findall('input'):
                    inputs.append(VMixInput.from_xml(input_elem))

            # Get active/preview inputs
            active_elem = root.find('active')
            active_input = int(active_elem.text) if active_elem is not None and active_elem.text else None

            preview_elem = root.find('preview')
            preview_input = int(preview_elem.text) if preview_elem is not None and preview_elem.text else None

            # Get recording/streaming status
            recording_elem = root.find('recording')
            recording = recording_elem.text == 'True' if recording_elem is not None else False

            streaming_elem = root.find('streaming')
            streaming = streaming_elem.text == 'True' if streaming_elem is not None else False

            audio_elem = root.find('audio')
            audio = audio_elem.text == 'True' if audio_elem is not None else True

            return VMixStatus(
                version=version,
                edition=edition,
                inputs=inputs,
                active_input=active_input,
                preview_input=preview_input,
                recording=recording,
                streaming=streaming,
                audio=audio
            )

        except requests.exceptions.ConnectionError as e:
            raise VMixConnectionError(f"Cannot connect to vMix at {self.host}:{self.port}: {e}")
        except requests.exceptions.Timeout:
            raise VMixConnectionError(f"Timeout connecting to vMix at {self.host}:{self.port}")
        except ET.ParseError as e:
            raise VMixAPIError(f"Failed to parse vMix XML status: {e}")
        except Exception as e:
            raise VMixError(f"Unexpected error: {e}")

    def get_inputs(self) -> List[VMixInput]:
        """Get all inputs from vMix status"""
        status = self.get_status()
        return status.inputs

    def get_active_input(self) -> Optional[int]:
        """Get currently active (program) input number"""
        status = self.get_status()
        return status.active_input

    def get_preview_input(self) -> Optional[int]:
        """Get currently previewed input number"""
        status = self.get_status()
        return status.preview_input

    def test_connection(self) -> bool:
        """
        Test connection to vMix.

        Returns:
            True if connection successful

        Raises:
            VMixConnectionError: If connection fails
        """
        try:
            self.get_status()
            return True
        except VMixError:
            raise

    # Production Control Methods

    def cut(self, input_num: int) -> bool:
        """Cut to input (instant transition)"""
        return self.execute_function("Cut", Input=input_num)

    def fade(self, input_num: int, duration: int = 1000) -> bool:
        """Fade to input"""
        return self.execute_function("Fade", Input=input_num, Duration=duration)

    def preview(self, input_num: int) -> bool:
        """Set preview input"""
        return self.execute_function("PreviewInput", Input=input_num)

    def transition(self, transition_type: str, duration: int = 1000, input_num: Optional[int] = None) -> bool:
        """
        Execute custom transition.

        Args:
            transition_type: Transition type (Fade, Merge, Wipe, etc.)
            duration: Transition duration in milliseconds
            input_num: Optional input number (if not specified, uses preview)
        """
        params = {'Mix': transition_type, 'Duration': duration}
        if input_num:
            params['Input'] = input_num
        return self.execute_function("Transition", **params)

    def overlay(self, overlay_num: int, input_num: int, action: str = "OverlayInput") -> bool:
        """
        Set overlay input.

        Args:
            overlay_num: Overlay number (1-4)
            input_num: Input to set as overlay
            action: Overlay action (OverlayInput, OverlayInputIn, OverlayInputOut)
        """
        return self.execute_function(action + str(overlay_num), Input=input_num)

    # NDI Control Methods

    def add_ndi_input(self, source_name: str) -> bool:
        """Add NDI input source"""
        return self.execute_function("AddInput", Value=f"NDI|{source_name}")

    def remove_input(self, input_num: int) -> bool:
        """Remove input"""
        return self.execute_function("RemoveInput", Input=input_num)

    # Streaming Methods

    def start_streaming(self, channel: int = 0) -> bool:
        """Start streaming (channel 0-2)"""
        return self.execute_function("StartStreaming", Value=channel)

    def stop_streaming(self, channel: int = 0) -> bool:
        """Stop streaming"""
        return self.execute_function("StopStreaming", Value=channel)

    def set_stream_url(self, url: str, key: str, channel: int = 0) -> bool:
        """
        Set streaming URL and key.

        Args:
            url: RTMP URL (e.g., rtmp://server/live)
            key: Stream key
            channel: Streaming channel (0-2)
        """
        # Set URL
        self.execute_function("SetStreamURL", Value=url, Stream=channel)
        # Set key
        self.execute_function("SetStreamKey", Value=key, Stream=channel)
        return True

    def get_stream_status(self) -> VMixStreamStatus:
        """Get streaming status"""
        status = self.get_status()
        return VMixStreamStatus(streaming=status.streaming)

    # Recording Methods

    def start_recording(self, filename: Optional[str] = None) -> bool:
        """
        Start recording.

        Args:
            filename: Optional filename (if not specified, vMix uses default)
        """
        if filename:
            return self.execute_function("StartRecording", Filename=filename)
        return self.execute_function("StartRecording")

    def stop_recording(self) -> bool:
        """Stop recording"""
        return self.execute_function("StopRecording")

    def get_record_status(self) -> VMixRecordStatus:
        """Get recording status"""
        status = self.get_status()
        return VMixRecordStatus(recording=status.recording)

    # PTZ Camera Control

    def ptz_move(self, input_num: int, pan: Optional[int] = None,
                 tilt: Optional[int] = None, zoom: Optional[int] = None) -> bool:
        """
        Control PTZ camera.

        Args:
            input_num: Input number
            pan: Pan value (-100 to 100, or None to keep current)
            tilt: Tilt value (-100 to 100, or None to keep current)
            zoom: Zoom value (0 to 100, or None to keep current)
        """
        params = {'Input': input_num}
        if pan is not None:
            params['Pan'] = pan
        if tilt is not None:
            params['Tilt'] = tilt
        if zoom is not None:
            params['Zoom'] = zoom
        return self.execute_function("PTZ", **params)

    def ptz_preset(self, input_num: int, preset: int) -> bool:
        """Recall PTZ preset"""
        return self.execute_function("PTZPreset", Input=input_num, Value=preset)

    def ptz_home(self, input_num: int) -> bool:
        """Move PTZ to home position"""
        return self.execute_function("PTZHome", Input=input_num)

    # Audio Control

    def set_volume(self, input_num: int, volume: int) -> bool:
        """
        Set input volume.

        Args:
            input_num: Input number
            volume: Volume level (0-100)
        """
        return self.execute_function("SetVolume", Input=input_num, Value=volume)

    def mute(self, input_num: int) -> bool:
        """Mute input audio"""
        return self.execute_function("AudioOff", Input=input_num)

    def unmute(self, input_num: int) -> bool:
        """Unmute input audio"""
        return self.execute_function("AudioOn", Input=input_num)
