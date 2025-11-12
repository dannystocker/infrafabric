"""
IF.homeassistant API Client

REST API client for Home Assistant control and status queries.
"""

import requests
import json
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

from .models import (
    HAEntity, HAConfig, HAAutomation, HAScript, HAScene,
    HACamera, HAMediaPlayer, HAEvent
)


class HAError(Exception):
    """Base exception for Home Assistant errors"""
    pass


class HAConnectionError(HAError):
    """Connection error to Home Assistant"""
    pass


class HAAPIError(HAError):
    """Home Assistant API error"""
    pass


class HAAuthError(HAError):
    """Authentication error"""
    pass


class HomeAssistantClient:
    """
    Home Assistant REST API client.

    Philosophy: Simple, synchronous client for home automation control.
    Every operation is a single HTTP request.

    API Reference: https://developers.home-assistant.io/docs/api/rest/
    """

    def __init__(self, url: str, token: str, timeout: int = 10):
        """
        Initialize Home Assistant client.

        Args:
            url: Home Assistant URL (e.g., http://homeassistant.local:8123)
            token: Long-lived access token
            timeout: Request timeout in seconds
        """
        self.url = url.rstrip('/')
        self.token = token
        self.timeout = timeout
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def _get(self, endpoint: str) -> Any:
        """Execute GET request"""
        try:
            url = urljoin(self.url + '/', endpoint)
            response = requests.get(url, headers=self.headers, timeout=self.timeout)

            if response.status_code == 401:
                raise HAAuthError("Authentication failed. Check your access token.")

            response.raise_for_status()
            return response.json()

        except HAAuthError:
            # Re-raise auth errors
            raise
        except requests.exceptions.ConnectionError as e:
            raise HAConnectionError(f"Cannot connect to Home Assistant at {self.url}: {e}")
        except requests.exceptions.Timeout:
            raise HAConnectionError(f"Timeout connecting to Home Assistant at {self.url}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise HAAuthError("Authentication failed. Check your access token.")
            raise HAAPIError(f"Home Assistant API error: {e}")
        except json.JSONDecodeError as e:
            raise HAAPIError(f"Failed to parse JSON response: {e}")
        except Exception as e:
            raise HAError(f"Unexpected error: {e}")

    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Execute POST request"""
        try:
            url = urljoin(self.url + '/', endpoint)
            response = requests.post(
                url,
                headers=self.headers,
                json=data or {},
                timeout=self.timeout
            )

            if response.status_code == 401:
                raise HAAuthError("Authentication failed. Check your access token.")

            response.raise_for_status()

            # Some endpoints return empty responses
            if response.text:
                return response.json()
            return {}

        except HAAuthError:
            # Re-raise auth errors
            raise
        except requests.exceptions.ConnectionError as e:
            raise HAConnectionError(f"Cannot connect to Home Assistant at {self.url}: {e}")
        except requests.exceptions.Timeout:
            raise HAConnectionError(f"Timeout connecting to Home Assistant at {self.url}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise HAAuthError("Authentication failed. Check your access token.")
            raise HAAPIError(f"Home Assistant API error: {e}")
        except json.JSONDecodeError as e:
            raise HAAPIError(f"Failed to parse JSON response: {e}")
        except Exception as e:
            raise HAError(f"Unexpected error: {e}")

    def _download(self, endpoint: str) -> bytes:
        """Download binary content (e.g., camera snapshot)"""
        try:
            url = urljoin(self.url + '/', endpoint)
            response = requests.get(url, headers=self.headers, timeout=self.timeout)

            if response.status_code == 401:
                raise HAAuthError("Authentication failed. Check your access token.")

            response.raise_for_status()
            return response.content

        except requests.exceptions.ConnectionError as e:
            raise HAConnectionError(f"Cannot connect to Home Assistant at {self.url}: {e}")
        except requests.exceptions.Timeout:
            raise HAConnectionError(f"Timeout connecting to Home Assistant at {self.url}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise HAAuthError("Authentication failed. Check your access token.")
            raise HAAPIError(f"Home Assistant API error: {e}")
        except Exception as e:
            raise HAError(f"Unexpected error: {e}")

    # Connection & Status Methods

    def test_connection(self) -> bool:
        """
        Test connection to Home Assistant.

        Returns:
            True if connection successful

        Raises:
            HAConnectionError: If connection fails
            HAAuthError: If authentication fails
        """
        self._get('api/')
        return True

    def get_config(self) -> HAConfig:
        """
        Get Home Assistant configuration.

        Returns:
            HAConfig with system information
        """
        data = self._get('api/config')
        return HAConfig.from_dict(data)

    def get_status(self) -> Dict[str, Any]:
        """
        Get Home Assistant status.

        Returns:
            Status information including message
        """
        return self._get('api/')

    # Entity Methods

    def get_states(self, domain: Optional[str] = None) -> List[HAEntity]:
        """
        Get all entity states, optionally filtered by domain.

        Args:
            domain: Optional domain filter (e.g., 'light', 'switch')

        Returns:
            List of HAEntity objects
        """
        data = self._get('api/states')
        entities = [HAEntity.from_dict(item) for item in data]

        if domain:
            entities = [e for e in entities if e.domain == domain]

        return entities

    def get_state(self, entity_id: str) -> HAEntity:
        """
        Get specific entity state.

        Args:
            entity_id: Entity ID (e.g., 'light.living_room')

        Returns:
            HAEntity object
        """
        data = self._get(f'api/states/{entity_id}')
        return HAEntity.from_dict(data)

    def set_state(self, entity_id: str, state: str, attributes: Optional[Dict] = None) -> HAEntity:
        """
        Set entity state (this doesn't actually control the device, use call_service instead).

        Args:
            entity_id: Entity ID
            state: New state value
            attributes: Optional attributes

        Returns:
            Updated HAEntity
        """
        data = {
            'state': state,
            'attributes': attributes or {}
        }
        result = self._post(f'api/states/{entity_id}', data)
        return HAEntity.from_dict(result)

    # Service Methods

    def call_service(self, domain: str, service: str, service_data: Optional[Dict] = None) -> List[Dict]:
        """
        Call a Home Assistant service.

        Args:
            domain: Service domain (e.g., 'light', 'switch')
            service: Service name (e.g., 'turn_on', 'turn_off')
            service_data: Service data including entity_id and parameters

        Returns:
            List of affected states
        """
        return self._post(f'api/services/{domain}/{service}', service_data)

    def get_services(self) -> Dict[str, Any]:
        """
        Get all available services.

        Returns:
            Dictionary of services by domain
        """
        return self._get('api/services')

    # Entity Control Methods

    def turn_on(self, entity_id: str, **kwargs) -> List[Dict]:
        """
        Turn on an entity.

        Args:
            entity_id: Entity ID
            **kwargs: Additional parameters (e.g., brightness, temperature)

        Returns:
            List of affected states
        """
        domain = entity_id.split('.')[0]
        service_data = {'entity_id': entity_id, **kwargs}
        return self.call_service(domain, 'turn_on', service_data)

    def turn_off(self, entity_id: str, **kwargs) -> List[Dict]:
        """
        Turn off an entity.

        Args:
            entity_id: Entity ID
            **kwargs: Additional parameters

        Returns:
            List of affected states
        """
        domain = entity_id.split('.')[0]
        service_data = {'entity_id': entity_id, **kwargs}
        return self.call_service(domain, 'turn_off', service_data)

    def toggle(self, entity_id: str) -> List[Dict]:
        """
        Toggle an entity.

        Args:
            entity_id: Entity ID

        Returns:
            List of affected states
        """
        domain = entity_id.split('.')[0]
        service_data = {'entity_id': entity_id}
        return self.call_service(domain, 'toggle', service_data)

    # Automation Methods

    def get_automations(self) -> List[HAAutomation]:
        """
        Get all automations.

        Returns:
            List of HAAutomation objects
        """
        entities = self.get_states('automation')
        return [HAAutomation.from_entity(e) for e in entities]

    def trigger_automation(self, entity_id: str) -> List[Dict]:
        """
        Trigger an automation.

        Args:
            entity_id: Automation entity ID

        Returns:
            List of affected states
        """
        return self.call_service('automation', 'trigger', {'entity_id': entity_id})

    def enable_automation(self, entity_id: str) -> List[Dict]:
        """Enable an automation"""
        return self.call_service('automation', 'turn_on', {'entity_id': entity_id})

    def disable_automation(self, entity_id: str) -> List[Dict]:
        """Disable an automation"""
        return self.call_service('automation', 'turn_off', {'entity_id': entity_id})

    # Script Methods

    def get_scripts(self) -> List[HAScript]:
        """
        Get all scripts.

        Returns:
            List of HAScript objects
        """
        entities = self.get_states('script')
        return [HAScript.from_entity(e) for e in entities]

    def run_script(self, entity_id: str, variables: Optional[Dict] = None) -> List[Dict]:
        """
        Run a script.

        Args:
            entity_id: Script entity ID
            variables: Optional script variables

        Returns:
            List of affected states
        """
        script_name = entity_id.replace('script.', '')
        return self.call_service('script', script_name, variables or {})

    # Scene Methods

    def get_scenes(self) -> List[HAScene]:
        """
        Get all scenes.

        Returns:
            List of HAScene objects
        """
        entities = self.get_states('scene')
        return [HAScene.from_entity(e) for e in entities]

    def activate_scene(self, entity_id: str) -> List[Dict]:
        """
        Activate a scene.

        Args:
            entity_id: Scene entity ID

        Returns:
            List of affected states
        """
        return self.call_service('scene', 'turn_on', {'entity_id': entity_id})

    # Camera Methods

    def get_cameras(self) -> List[HACamera]:
        """
        Get all cameras.

        Returns:
            List of HACamera objects
        """
        entities = self.get_states('camera')
        return [HACamera.from_entity(e) for e in entities]

    def get_camera_snapshot(self, entity_id: str) -> bytes:
        """
        Get camera snapshot as JPEG bytes.

        Args:
            entity_id: Camera entity ID

        Returns:
            JPEG image bytes
        """
        # Try the proxy endpoint first
        try:
            return self._download(f'api/camera_proxy/{entity_id}')
        except:
            # Fallback to direct entity_picture if proxy fails
            state = self.get_state(entity_id)
            entity_picture = state.attributes.get('entity_picture')
            if entity_picture:
                return self._download(entity_picture)
            raise HAAPIError(f"Cannot get snapshot for {entity_id}")

    def get_camera_stream_source(self, entity_id: str) -> Optional[str]:
        """
        Get camera stream source URL (RTSP/HTTP).

        Args:
            entity_id: Camera entity ID

        Returns:
            Stream source URL or None
        """
        try:
            # Call camera.get_stream service to get stream URL
            result = self.call_service('camera', 'get_stream', {'entity_id': entity_id})
            if result and len(result) > 0:
                return result[0].get('url')
        except:
            pass

        # Fallback: check entity attributes
        state = self.get_state(entity_id)
        return state.attributes.get('stream_source')

    # Media Player Methods

    def get_media_players(self) -> List[HAMediaPlayer]:
        """
        Get all media players.

        Returns:
            List of HAMediaPlayer objects
        """
        entities = self.get_states('media_player')
        return [HAMediaPlayer.from_entity(e) for e in entities]

    def media_play(self, entity_id: str) -> List[Dict]:
        """Play media player"""
        return self.call_service('media_player', 'media_play', {'entity_id': entity_id})

    def media_pause(self, entity_id: str) -> List[Dict]:
        """Pause media player"""
        return self.call_service('media_player', 'media_pause', {'entity_id': entity_id})

    def media_stop(self, entity_id: str) -> List[Dict]:
        """Stop media player"""
        return self.call_service('media_player', 'media_stop', {'entity_id': entity_id})

    def media_play_url(self, entity_id: str, media_url: str) -> List[Dict]:
        """
        Play media from URL.

        Args:
            entity_id: Media player entity ID
            media_url: Media URL to play

        Returns:
            List of affected states
        """
        return self.call_service('media_player', 'play_media', {
            'entity_id': entity_id,
            'media_content_id': media_url,
            'media_content_type': 'music'
        })

    def tts_speak(self, entity_id: str, message: str, language: str = 'en') -> List[Dict]:
        """
        Speak text via TTS.

        Args:
            entity_id: Media player entity ID
            message: Text to speak
            language: Language code (default: 'en')

        Returns:
            List of affected states
        """
        return self.call_service('tts', 'google_translate_say', {
            'entity_id': entity_id,
            'message': message,
            'language': language
        })

    # Notification Methods

    def send_notification(self, message: str, title: Optional[str] = None,
                         service: str = 'persistent_notification') -> List[Dict]:
        """
        Send notification.

        Args:
            message: Notification message
            title: Optional title
            service: Notification service (default: 'persistent_notification')

        Returns:
            List of affected states
        """
        data = {'message': message}
        if title:
            data['title'] = title

        if service == 'persistent_notification':
            return self.call_service('persistent_notification', 'create', data)
        else:
            return self.call_service('notify', service, data)

    # Event Methods

    def fire_event(self, event_type: str, event_data: Optional[Dict] = None) -> Dict:
        """
        Fire an event.

        Args:
            event_type: Event type
            event_data: Optional event data

        Returns:
            Event result
        """
        return self._post(f'api/events/{event_type}', event_data)

    def get_events(self) -> List[Dict]:
        """
        Get list of event types.

        Returns:
            List of event type dictionaries
        """
        return self._get('api/events')

    # Error Log Methods

    def get_error_log(self) -> str:
        """
        Get Home Assistant error log.

        Returns:
            Error log text
        """
        try:
            url = urljoin(self.url + '/', 'api/error_log')
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise HAError(f"Failed to get error log: {e}")
