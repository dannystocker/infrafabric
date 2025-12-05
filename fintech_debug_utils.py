"""
Reusable fintech debug utilities for InfraFabric adapters.

These helpers provide consistent, opt-in debug logging for all fintech
adapters (mobile money, CBS, KYC, messaging, etc.) without duplicating
logic in each module.

Usage in an adapter:

    from fintech_debug_utils import ft_debug_log_request, ft_debug_log_response

    ft_debug_log_request(logger, "mpesa", url, payload)
    ...
    ft_debug_log_response(logger, "mpesa", response.status_code, response.text)

Enable at runtime by setting:

    IF_FINTECH_DEBUG=1
    # or adapter-specific:
    IF_FINTECH_DEBUG_MPESA=1
    IF_FINTECH_DEBUG_MTN_MOMO=1
    IF_FINTECH_DEBUG_AIRTEL_MONEY=1
    IF_FINTECH_DEBUG_ORANGE_MONEY=1
    IF_FINTECH_DEBUG_MIFOS=1
    IF_FINTECH_DEBUG_MUSONI=1
    IF_FINTECH_DEBUG_TRANSUNION=1
    IF_FINTECH_DEBUG_SMILE_IDENTITY=1
    IF_FINTECH_DEBUG_AFRICAS_TALKING=1

IMPORTANT:
- Intended for controlled debugging environments, not general production use.
- Do not log raw secrets; combine with IF.yologuard / if.armour.secrets.detect
  when storing or shipping logs.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

try:
    # Prefer the architectural alias for secret detection.
    from infrafabric.core.armour.secrets.detect import SecretRedactorV3  # type: ignore
except Exception:  # pragma: no cover - defensive import
    SecretRedactorV3 = None  # type: ignore


GLOBAL_FLAG = "IF_FINTECH_DEBUG"
PROVIDER_PREFIX = "IF_FINTECH_DEBUG_"

GLOBAL_REDACT_FLAG = "IF_DEBUG_REDACT"
FINTECH_REDACT_FLAG = "IF_FINTECH_DEBUG_REDACT"
FINTECH_REDACT_PREFIX = "IF_FINTECH_DEBUG_REDACT_"


def _flag_enabled(value: str) -> bool:
    value = value.strip().lower()
    return value in {"1", "true", "yes", "on"}


def _redact_flag_enabled(provider: Optional[str] = None) -> bool:
    """
    Return True if secret redaction via if.armour.secrets.detect
    should be applied to fintech debug logs.
    """
    # Global redaction override
    if _flag_enabled(os.getenv(GLOBAL_REDACT_FLAG, "")):
        return True

    # Fintech-wide redaction
    if _flag_enabled(os.getenv(FINTECH_REDACT_FLAG, "")):
        return True

    # Provider-specific redaction
    if provider:
        key = f"{FINTECH_REDACT_PREFIX}{provider.upper()}"
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


def fintech_debug_enabled(provider: Optional[str] = None) -> bool:
    """
    Return True if fintech debug logging is enabled.

    Checks, in order:
        IF_FINTECH_DEBUG
        IF_FINTECH_DEBUG_<PROVIDER>  (e.g. IF_FINTECH_DEBUG_MPESA)
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
        text = str(payload)
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text


def ft_debug_log_request(
    logger,
    provider: str,
    url: str,
    payload: Dict[str, Any],
) -> None:
    """
    Log outgoing fintech request if debug is enabled.
    """
    if not fintech_debug_enabled(provider):
        return

    safe_payload = _safe_json(payload)
    safe_payload = _redact_text(safe_payload, provider)
    logger.info(
        "[FINTECH DEBUG][%s] Request %s payload=%s", provider, url, safe_payload
    )


def ft_debug_log_response(
    logger,
    provider: str,
    status_code: int,
    body_text: str,
    limit: int = 2000,
) -> None:
    """
    Log incoming fintech response if debug is enabled.
    """
    if not fintech_debug_enabled(provider):
        return

    if len(body_text) > limit:
        body_preview = body_text[: limit - 3] + "..."
    else:
        body_preview = body_text

    body_preview = _redact_text(body_preview, provider)

    logger.info(
        "[FINTECH DEBUG][%s] Response status=%s body=%s",
        provider,
        status_code,
        body_preview,
    )
