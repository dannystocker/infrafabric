"""
Reusable LLM debug utilities for InfraFabric adapters.

These helpers are designed so that all LLM adapters (OpenAI, Mistral,
DeepSeek, OpenRouter, etc.) can opt into consistent debug logging when a
flag is enabled, without duplicating logic.

Usage in an adapter:

    from llm_debug_utils import debug_log_request, debug_log_response

    debug_log_request(logger, "openai", url, payload)
    ...
    debug_log_response(logger, "openai", response.status_code, response.text)

Enable at runtime by setting:

    IF_LLM_DEBUG=1
    # or provider-specific:
    IF_LLM_DEBUG_OPENAI=1

IMPORTANT: This is intended for non-production debugging only, as it may log
request/response bodies (excluding API keys).
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

try:
    # Prefer the architectural alias; falls back gracefully if package
    # isn't installed in the current environment.
    from infrafabric.core.armour.secrets.detect import SecretRedactorV3  # type: ignore
except Exception:  # pragma: no cover - defensive import
    SecretRedactorV3 = None  # type: ignore


GLOBAL_FLAG = "IF_LLM_DEBUG"
PROVIDER_PREFIX = "IF_LLM_DEBUG_"

GLOBAL_REDACT_FLAG = "IF_DEBUG_REDACT"
LLM_REDACT_FLAG = "IF_LLM_DEBUG_REDACT"
LLM_REDACT_PREFIX = "IF_LLM_DEBUG_REDACT_"


def _flag_enabled(value: str) -> bool:
    value = value.strip().lower()
    return value in {"1", "true", "yes", "on"}


def _redact_flag_enabled(provider: Optional[str] = None) -> bool:
    """
    Return True if secret redaction via if.armour.secrets.detect
    should be applied to debug logs.
    """
    # Global redaction override
    if _flag_enabled(os.getenv(GLOBAL_REDACT_FLAG, "")):
        return True

    # LLM-wide redaction
    if _flag_enabled(os.getenv(LLM_REDACT_FLAG, "")):
        return True

    # Provider-specific redaction
    if provider:
        key = f"{LLM_REDACT_PREFIX}{provider.upper()}"
        if _flag_enabled(os.getenv(key, "")):
            return True

    return False


_REDACTOR = SecretRedactorV3() if SecretRedactorV3 is not None else None


def _redact_text(text: str, provider: Optional[str]) -> str:
    """
    Apply SecretRedactorV3 if redaction is enabled and the engine is available.
    """
    if not _redact_flag_enabled(provider):
        return text
    if _REDACTOR is None:
        return text
    try:
        return _REDACTOR.redact(text)
    except Exception:
        return text


def is_debug_enabled(provider: Optional[str] = None) -> bool:
    """
    Return True if LLM debug logging is enabled.

    Checks:
        IF_LLM_DEBUG
        IF_LLM_DEBUG_<PROVIDER>  (e.g. IF_LLM_DEBUG_OPENAI)
    """
    if _flag_enabled(os.getenv(GLOBAL_FLAG, "")):
        return True

    if provider:
        key = f"{PROVIDER_PREFIX}{provider.upper()}"
        if _flag_enabled(os.getenv(key, "")):
            return True

    return False


def _safe_json(payload: Dict[str, Any], limit: int = 2000) -> str:
    """
    JSON-dump payload and truncate to a reasonable length to avoid
    flooding logs.
    """
    try:
        text = json.dumps(payload, ensure_ascii=False, default=str)
    except TypeError:
        # Fallback: best-effort conversion
        text = str(payload)
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text


def debug_log_request(
    logger,
    provider: str,
    url: str,
    payload: Dict[str, Any],
) -> None:
    """
    Log outgoing LLM request if debug is enabled.
    """
    if not is_debug_enabled(provider):
        return

    safe_payload = _safe_json(payload)
    safe_payload = _redact_text(safe_payload, provider)
    logger.info("[LLM DEBUG][%s] Request %s payload=%s", provider, url, safe_payload)


def debug_log_response(
    logger,
    provider: str,
    status_code: int,
    body_text: str,
    limit: int = 2000,
) -> None:
    """
    Log incoming LLM response if debug is enabled.
    """
    if not is_debug_enabled(provider):
        return

    if len(body_text) > limit:
        body_preview = body_text[: limit - 3] + "..."
    else:
        body_preview = body_text

    body_preview = _redact_text(body_preview, provider)

    logger.info(
        "[LLM DEBUG][%s] Response status=%s body=%s",
        provider,
        status_code,
        body_preview,
    )
