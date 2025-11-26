from typing import Any, Dict, Literal

from pydantic import BaseModel, ValidationError


class RedisModel(BaseModel):
    """Base model for all Redis-stored entities."""

    def to_redis(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_redis(cls, data: str) -> "RedisModel":
        return cls.model_validate_json(data)


class TaskSchema(RedisModel):
    id: str
    status: Literal["pending", "running", "failed", "complete"]
    priority: int = 0
    payload: Dict[str, Any]
    result: Dict[str, Any] | None = None


class ContextSchema(RedisModel):
    """Schema for instance context (lightweight to avoid giant blobs)."""

    instance_id: str
    tokens_used: int
    summary: str
    # pointer_to_file: str  # optional reference if needed


def validate_key_type(key: str, data: str) -> None:
    """Gatekeeper: raise on invalid state before writing to Redis."""
    try:
        if key.startswith("task:"):
            TaskSchema.from_redis(data)
        elif key.startswith("context:"):
            ContextSchema.from_redis(data)
    except ValidationError as exc:  # noqa: BLE001
        raise ValueError(f"CRITICAL: Attempted to write INVALID STATE to {key}: {exc}") from exc
