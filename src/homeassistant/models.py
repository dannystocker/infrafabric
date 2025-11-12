"""
IF.homeassistant Data Models

Data classes for Home Assistant entities and responses.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class HAInstance:
    """Home Assistant instance configuration"""
    name: str
    url: str
    token: str
    added_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'url': self.url,
            'token': self.token[:20] + '...' if self.token else None,  # Mask token
            'added_at': self.added_at
        }


@dataclass
class HAEntity:
    """Home Assistant entity state"""
    entity_id: str
    state: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    last_changed: Optional[str] = None
    last_updated: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HAEntity':
        """Create entity from API response"""
        return cls(
            entity_id=data.get('entity_id', ''),
            state=data.get('state', 'unknown'),
            attributes=data.get('attributes', {}),
            last_changed=data.get('last_changed'),
            last_updated=data.get('last_updated')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'entity_id': self.entity_id,
            'state': self.state,
            'attributes': self.attributes,
            'last_changed': self.last_changed,
            'last_updated': self.last_updated
        }

    @property
    def domain(self) -> str:
        """Get entity domain (e.g., 'light' from 'light.living_room')"""
        return self.entity_id.split('.')[0] if '.' in self.entity_id else ''

    @property
    def name(self) -> str:
        """Get friendly name from attributes"""
        return self.attributes.get('friendly_name', self.entity_id)


@dataclass
class HAService:
    """Home Assistant service"""
    domain: str
    service: str
    fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, domain: str, service: str, data: Dict[str, Any]) -> 'HAService':
        """Create service from API response"""
        return cls(
            domain=domain,
            service=service,
            fields=data.get('fields', {})
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'domain': self.domain,
            'service': self.service,
            'fields': self.fields
        }


@dataclass
class HAConfig:
    """Home Assistant configuration"""
    version: str
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation: Optional[int] = None
    unit_system: Optional[str] = None
    time_zone: Optional[str] = None
    components: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HAConfig':
        """Create config from API response"""
        return cls(
            version=data.get('version', 'unknown'),
            location_name=data.get('location_name', 'Home'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            elevation=data.get('elevation'),
            unit_system=data.get('unit_system', {}).get('name'),
            time_zone=data.get('time_zone'),
            components=data.get('components', [])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'version': self.version,
            'location_name': self.location_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'elevation': self.elevation,
            'unit_system': self.unit_system,
            'time_zone': self.time_zone,
            'components': self.components
        }


@dataclass
class HAAutomation:
    """Home Assistant automation"""
    entity_id: str
    name: str
    state: str
    last_triggered: Optional[str] = None

    @classmethod
    def from_entity(cls, entity: HAEntity) -> 'HAAutomation':
        """Create automation from entity"""
        return cls(
            entity_id=entity.entity_id,
            name=entity.name,
            state=entity.state,
            last_triggered=entity.attributes.get('last_triggered')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'entity_id': self.entity_id,
            'name': self.name,
            'state': self.state,
            'last_triggered': self.last_triggered
        }


@dataclass
class HAScript:
    """Home Assistant script"""
    entity_id: str
    name: str
    last_triggered: Optional[str] = None

    @classmethod
    def from_entity(cls, entity: HAEntity) -> 'HAScript':
        """Create script from entity"""
        return cls(
            entity_id=entity.entity_id,
            name=entity.name,
            last_triggered=entity.attributes.get('last_triggered')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'entity_id': self.entity_id,
            'name': self.name,
            'last_triggered': self.last_triggered
        }


@dataclass
class HAScene:
    """Home Assistant scene"""
    entity_id: str
    name: str

    @classmethod
    def from_entity(cls, entity: HAEntity) -> 'HAScene':
        """Create scene from entity"""
        return cls(
            entity_id=entity.entity_id,
            name=entity.name
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'entity_id': self.entity_id,
            'name': self.name
        }


@dataclass
class HACamera:
    """Home Assistant camera"""
    entity_id: str
    name: str
    state: str
    stream_source: Optional[str] = None

    @classmethod
    def from_entity(cls, entity: HAEntity) -> 'HACamera':
        """Create camera from entity"""
        return cls(
            entity_id=entity.entity_id,
            name=entity.name,
            state=entity.state,
            stream_source=entity.attributes.get('entity_picture')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'entity_id': self.entity_id,
            'name': self.name,
            'state': self.state,
            'stream_source': self.stream_source
        }


@dataclass
class HAMediaPlayer:
    """Home Assistant media player"""
    entity_id: str
    name: str
    state: str
    volume_level: Optional[float] = None
    media_title: Optional[str] = None
    supported_features: int = 0

    @classmethod
    def from_entity(cls, entity: HAEntity) -> 'HAMediaPlayer':
        """Create media player from entity"""
        return cls(
            entity_id=entity.entity_id,
            name=entity.name,
            state=entity.state,
            volume_level=entity.attributes.get('volume_level'),
            media_title=entity.attributes.get('media_title'),
            supported_features=entity.attributes.get('supported_features', 0)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'entity_id': self.entity_id,
            'name': self.name,
            'state': self.state,
            'volume_level': self.volume_level,
            'media_title': self.media_title,
            'supported_features': self.supported_features
        }


@dataclass
class HAEvent:
    """Home Assistant event"""
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    origin: str = 'LOCAL'
    time_fired: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'event_type': self.event_type,
            'data': self.data,
            'origin': self.origin,
            'time_fired': self.time_fired
        }
