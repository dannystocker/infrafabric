"""
IF.vmix Data Models

Data structures for vMix instances, status, inputs, and operations.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class VMixInstance:
    """vMix instance configuration"""
    name: str
    host: str
    port: int = 8088
    added_at: str = None

    def __post_init__(self):
        if self.added_at is None:
            self.added_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VMixInstance':
        return cls(**data)

    @property
    def url(self) -> str:
        """Get base URL for this instance"""
        return f"http://{self.host}:{self.port}/api/"


@dataclass
class VMixInput:
    """vMix input (video source)"""
    key: str
    number: int
    type: str
    state: str
    title: str
    duration: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_xml(cls, element) -> 'VMixInput':
        """Create from XML element"""
        return cls(
            key=element.get('key', ''),
            number=int(element.get('number', 0)),
            type=element.get('type', ''),
            state=element.get('state', ''),
            title=element.text or '',
            duration=int(element.get('duration', 0)) if element.get('duration') else None
        )


@dataclass
class VMixTransition:
    """vMix transition configuration"""
    type: str  # Cut, Fade, Merge, Wipe, etc.
    duration: Optional[int] = None  # Duration in milliseconds

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VMixStatus:
    """vMix system status"""
    version: str
    edition: str
    inputs: List[VMixInput]
    active_input: Optional[int] = None
    preview_input: Optional[int] = None
    recording: bool = False
    streaming: bool = False
    audio: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'version': self.version,
            'edition': self.edition,
            'inputs': [inp.to_dict() for inp in self.inputs],
            'active_input': self.active_input,
            'preview_input': self.preview_input,
            'recording': self.recording,
            'streaming': self.streaming,
            'audio': self.audio
        }


@dataclass
class VMixStreamStatus:
    """Streaming status"""
    streaming: bool
    channel: Optional[int] = None
    duration: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VMixRecordStatus:
    """Recording status"""
    recording: bool
    duration: Optional[int] = None
    filename: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
