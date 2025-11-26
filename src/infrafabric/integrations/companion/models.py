"""
Pydantic models for Companion MCR Bridge

All models inherit from RedisModel for automatic JSON serialization/deserialization.
These models enforce strict schema validation before Redis writes.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class RedisModel(BaseModel):
    """Base model for all Redis-stored entities."""

    def to_redis(self) -> str:
        """Serialize to JSON for Redis storage"""
        return self.model_dump_json()

    @classmethod
    def from_redis(cls, data: str) -> "RedisModel":
        """Deserialize from Redis JSON"""
        return cls.model_validate_json(data)


# ============================================================================
# Bridge Configuration
# ============================================================================


class CompanionBridgeConfig(RedisModel):
    """
    Bridge configuration stored at: mcr:bridge:companion:config

    Defines connection parameters and operational settings.
    """

    host: str = Field(default="localhost", description="Companion host")
    port: int = Field(default=8888, description="Companion API port")
    protocol: Literal["http", "https"] = "http"
    timeout_ms: int = Field(default=5000, description="Request timeout")
    retry_attempts: int = Field(default=3, description="Retry count")
    retry_backoff_ms: int = Field(default=1000, description="Backoff between retries")
    enable_state_tracking: bool = Field(default=True, description="Track button states")
    enable_macros: bool = Field(default=True, description="Enable macro execution")

    @property
    def base_url(self) -> str:
        """Construct base URL from host/port/protocol"""
        return f"{self.protocol}://{self.host}:{self.port}"


# ============================================================================
# Protocol Templates
# ============================================================================


class ProtocolTemplate(RedisModel):
    """
    Protocol command template stored at: mcr:protocol:companion:{protocol_name}

    Defines how to execute a specific protocol command with variable substitution.
    """

    protocol_name: str = Field(description="Unique protocol identifier")
    protocol_type: Literal["http", "osc", "tcp", "udp"] = "http"
    template: str = Field(description="Command template with {var} placeholders")
    method: Optional[str] = Field(default="POST", description="HTTP method")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    variables: List[str] = Field(default_factory=list, description="Required variables")
    description: str = Field(default="", description="Human-readable description")

    # Protocol-specific fields
    osc_port: Optional[int] = Field(default=None, description="OSC port")
    osc_type: Optional[str] = Field(default=None, description="OSC argument type")
    tcp_host: Optional[str] = Field(default=None, description="TCP host override")
    tcp_port: Optional[int] = Field(default=None, description="TCP port")
    udp_host: Optional[str] = Field(default=None, description="UDP host override")
    udp_port: Optional[int] = Field(default=None, description="UDP port")

    @validator("variables")
    def validate_variables_in_template(cls, v, values):
        """Ensure all variables are referenced in template"""
        template = values.get("template", "")
        for var in v:
            if f"{{{var}}}" not in template and f"${var}" not in template:
                raise ValueError(f"Variable '{var}' not found in template")
        return v


# ============================================================================
# Device Catalog
# ============================================================================


class CompanionDevice(RedisModel):
    """
    Device entry stored at: mcr:catalog:companion:device:{device_id}

    Represents a physical or virtual control surface.
    """

    device_id: str = Field(description="Unique device identifier")
    device_type: str = Field(description="e.g., 'streamdeck_xl', 'virtual_surface'")
    page_count: int = Field(default=10, description="Number of pages")
    rows: int = Field(default=8, description="Buttons per row")
    cols: int = Field(default=8, description="Buttons per column")
    connection_url: Optional[str] = Field(default=None, description="Override connection")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_seen: Optional[str] = None


# ============================================================================
# Intent Mappings
# ============================================================================


class ButtonAction(RedisModel):
    """
    Single button action within an intent mapping.
    """

    action_type: Literal["press", "set_text", "set_color", "custom"] = "press"
    protocol_name: str = Field(description="Protocol template to use")
    device_id: str = Field(description="Target device")
    variables: Dict[str, Any] = Field(description="Variable substitution values")
    delay_ms: int = Field(default=0, description="Delay before execution")


class IntentMapping(RedisModel):
    """
    Intent mapping stored at: mcr:mapping:companion:intent:{intent_name}

    Maps a semantic intent to a sequence of button actions.

    Example:
        "studio_dark_mode" -> [press button, set text]
    """

    intent_name: str = Field(description="Semantic intent identifier")
    description: str = Field(description="Human-readable purpose")
    actions: List[ButtonAction] = Field(description="Sequence of actions")
    conditions: Optional[Dict[str, Any]] = Field(default=None, description="Conditional execution")
    priority: int = Field(default=0, description="Execution priority")
    created_by: str = Field(description="Agent/user that created mapping")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================================================
# Macros
# ============================================================================


class MacroStep(RedisModel):
    """Single step in a macro sequence"""

    step_number: int
    intent_name: str = Field(description="Intent to execute")
    wait_for_completion: bool = Field(default=True)
    timeout_ms: int = Field(default=10000)
    on_failure: Literal["abort", "continue", "retry"] = "abort"


class CompanionMacro(RedisModel):
    """
    Macro stored at: mcr:companion:macro:{macro_id}

    Defines a sequence of intents to execute in order.
    """

    macro_id: str = Field(description="Unique macro identifier")
    macro_name: str = Field(description="Human-readable name")
    description: str = Field(description="Macro purpose")
    steps: List[MacroStep] = Field(description="Ordered execution steps")
    created_by: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================================================
# State Tracking
# ============================================================================


class ButtonState(RedisModel):
    """
    Button state stored at: mcr:companion:state:{device_id}:{button_id}

    Tracks current state of a button on a device.
    """

    device_id: str
    button_id: str  # Format: "{page}_{row}_{col}"
    state: Literal["idle", "pressed", "active", "disabled"] = "idle"
    text: Optional[str] = None
    color: Optional[str] = None
    last_pressed: Optional[str] = None
    press_count: int = 0
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================================================
# Session Management
# ============================================================================


class CompanionSession(RedisModel):
    """
    Active session stored at: mcr:companion:session:{session_id}

    Tracks an active agent session controlling devices.
    """

    session_id: str
    agent_id: str = Field(description="IF agent controlling session")
    device_ids: List[str] = Field(description="Devices in this session")
    started_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_activity: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    commands_executed: int = 0
    errors_count: int = 0
    status: Literal["active", "paused", "terminated"] = "active"


# ============================================================================
# Execution Results
# ============================================================================


class ExecutionResult(BaseModel):
    """
    Result of intent/action/macro execution.

    Not stored in Redis, used for return values.
    """

    success: bool
    intent_name: Optional[str] = None
    actions_executed: int = 0
    latency_ms: float = 0.0
    error: Optional[Any] = None  # CompanionError (circular import)
    metadata: Dict[str, Any] = Field(default_factory=dict)
