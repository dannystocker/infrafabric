"""
IF.obs Data Models

Data structures for OBS instances, scenes, sources, and operations.
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class OBSInstance:
    """OBS instance configuration"""
    name: str
    host: str
    port: int = 4455
    password: Optional[str] = None
    added_at: str = None

    def __post_init__(self):
        if self.added_at is None:
            self.added_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        # Don't expose password in dict representation
        if 'password' in data and data['password']:
            data['password'] = '***'
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OBSInstance':
        return cls(**data)

    @property
    def url(self) -> str:
        """Get WebSocket URL for this instance"""
        return f"ws://{self.host}:{self.port}"


@dataclass
class OBSScene:
    """OBS scene"""
    name: str
    index: Optional[int] = None
    is_current: bool = False
    sources: List['OBSSource'] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'index': self.index,
            'is_current': self.is_current,
            'sources': [s.to_dict() for s in self.sources]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OBSScene':
        sources = [OBSSource.from_dict(s) for s in data.get('sources', [])]
        return cls(
            name=data['name'],
            index=data.get('index'),
            is_current=data.get('is_current', False),
            sources=sources
        )


@dataclass
class OBSSource:
    """OBS source (scene item)"""
    name: str
    type: str
    scene_item_id: Optional[int] = None
    scene_item_enabled: bool = True
    source_type: Optional[str] = None
    settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OBSSource':
        return cls(**data)


@dataclass
class OBSFilter:
    """OBS source filter"""
    name: str
    type: str
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OBSFilter':
        return cls(**data)


@dataclass
class OBSStreamStatus:
    """OBS streaming status"""
    active: bool
    reconnecting: bool = False
    timecode: Optional[str] = None
    duration: Optional[int] = None  # Duration in milliseconds
    congestion: Optional[float] = None
    bytes_sent: Optional[int] = None
    total_frames: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OBSRecordStatus:
    """OBS recording status"""
    active: bool
    paused: bool = False
    timecode: Optional[str] = None
    duration: Optional[int] = None  # Duration in milliseconds
    bytes: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OBSStats:
    """OBS performance statistics"""
    cpu_usage: float  # CPU usage percentage
    memory_usage: float  # Memory usage in MB
    available_disk_space: float  # Available disk space in MB
    active_fps: float  # Current FPS
    average_frame_render_time: float  # Average frame render time in ms
    render_skipped_frames: int  # Number of frames skipped due to rendering lag
    render_total_frames: int  # Total frames rendered
    output_skipped_frames: int  # Number of frames skipped due to encoding lag
    output_total_frames: int  # Total frames output
    web_socket_session_incoming_messages: Optional[int] = None
    web_socket_session_outgoing_messages: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OBSStats':
        return cls(**data)


@dataclass
class OBSVersion:
    """OBS version information"""
    obs_version: str
    obs_web_socket_version: str
    rpc_version: int
    available_requests: List[str] = field(default_factory=list)
    supported_image_formats: List[str] = field(default_factory=list)
    platform: Optional[str] = None
    platform_description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OBSVersion':
        return cls(**data)


@dataclass
class OBSInputSettings:
    """Settings for creating an input source"""
    input_name: str
    input_kind: str
    scene_name: Optional[str] = None
    input_settings: Dict[str, Any] = field(default_factory=dict)
    scale_filter: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
