"""
Smile Identity REST API Adapter

This module provides a small, focused adapter for Smile Identity's REST API.
It is intended as a starting point for integrating KYC workflows into
InfraFabric/IF.bus style systems.

Design goals:
- Do not hard-code environment-specific details that may change.
- Provide clear dataclasses and type hints for common KYC payloads.
- Keep the surface area small: submit job + get job status.

For full API details, always consult the official Smile Identity docs:
    https://docs.usesmileid.com/integration-options/rest-api
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import requests

from fintech_debug_utils import ft_debug_log_request, ft_debug_log_response


class SmileIdentityError(Exception):
    """Base exception for Smile Identity adapter."""


class AuthenticationError(SmileIdentityError):
    """Authentication or signing failure."""


class APIError(SmileIdentityError):
    """Non-success response from Smile Identity REST API."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.response_body = response_body or {}
        super().__init__(message)


class JobType(str, Enum):
    """
    Job types supported by Smile Identity REST API.

    The exact numeric/string mapping depends on your Smile Identity account
    configuration; use descriptive names here and map them in your integration.
    """

    BASIC_KYC = "basic_kyc"
    BIOMETRIC_KYC = "biometric_kyc"
    ENHANCED_KYC = "enhanced_kyc"


class JobStatus(str, Enum):
    """High-level job status values."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class IDInfo:
    """
    Core ID information for a KYC job.

    The exact fields you need depend on country and ID type; this dataclass
    intentionally keeps a small common subset and allows arbitrary extras.
    """

    country: str
    id_type: str
    id_number: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    date_of_birth: Optional[str] = None  # ISO yyyy-MM-dd
    extra_fields: Dict[str, Any] = None

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "country": self.country,
            "id_type": self.id_type,
            "id_number": self.id_number,
        }
        if self.first_name:
            payload["first_name"] = self.first_name
        if self.last_name:
            payload["last_name"] = self.last_name
        if self.middle_name:
            payload["middle_name"] = self.middle_name
        if self.date_of_birth:
            payload["date_of_birth"] = self.date_of_birth
        if self.extra_fields:
            payload.update(self.extra_fields)
        return payload


@dataclass
class BiometricInfo:
    """
    Biometric payload for Smile Identity jobs.

    For REST integrations this is typically a base64-encoded image or template.
    The exact structure should follow Smile Identity's documentation.
    """

    selfie_image_b64: Optional[str] = None
    id_image_b64: Optional[str] = None
    extra_fields: Dict[str, Any] = None

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if self.selfie_image_b64:
            payload["selfie_image"] = self.selfie_image_b64
        if self.id_image_b64:
            payload["id_image"] = self.id_image_b64
        if self.extra_fields:
            payload.update(self.extra_fields)
        return payload


class SmileIdentityAdapter:
    """
    Smile Identity REST API adapter.

    Example:
        adapter = SmileIdentityAdapter(
            partner_id="your_partner_id",
            api_key="your_api_key",
            base_url="https://testapi.smileidentity.com",
        )

        job = adapter.submit_id_verification(
            job_type=JobType.BASIC_KYC,
            user_id="user-123",
            id_info=IDInfo(
                country="NG",
                id_type="BVN",
                id_number="12345678901",
            ),
        )
    """

    def __init__(
        self,
        partner_id: str,
        api_key: str,
        base_url: str = "https://testapi.smileidentity.com",
        timeout: int = 60,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        if not partner_id or not api_key:
            raise AuthenticationError("partner_id and api_key are required")

        self.partner_id = partner_id
        self.api_key = api_key.encode("utf-8")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _build_url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def _sign_payload(self, payload: Dict[str, Any]) -> str:
        """
        Compute an HMAC signature for the payload.

        The exact signing scheme should match Smile Identity documentation.
        This implementation uses a simple HMAC-SHA256 over the JSON body.
        """
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        digest = hmac.new(self.api_key, body, hashlib.sha256).digest()
        return base64.b64encode(digest).decode("ascii")

    def _request(
        self,
        method: str,
        path: str,
        json_body: Dict[str, Any],
    ) -> Dict[str, Any]:
        url = self._build_url(path)

        # Attach partner ID and timestamp into the payload
        payload = dict(json_body)
        payload.setdefault("partner_id", self.partner_id)
        payload.setdefault("timestamp", datetime.utcnow().isoformat() + "Z")

        signature = self._sign_payload(payload)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            # Header name is intentionally generic; adjust to match Smile docs.
            "X-Smile-Signature": signature,
        }

        try:
            ft_debug_log_request(
                self.logger,
                "smile_identity",
                url,
                {"method": method, "body": payload},
            )

            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise SmileIdentityError(f"Failed to reach Smile Identity API: {exc}") from exc

        ft_debug_log_response(
            self.logger,
            "smile_identity",
            response.status_code,
            response.text,
        )

        if response.status_code == 401:
            raise AuthenticationError("Smile Identity authentication failed")

        if not (200 <= response.status_code < 300):
            try:
                body = response.json()
            except ValueError:
                body = {"raw": response.text}
            raise APIError(
                f"Smile Identity API error {response.status_code}",
                status_code=response.status_code,
                response_body=body,
            )

        try:
            return response.json()
        except ValueError as exc:
            raise APIError("Smile Identity API returned non-JSON response") from exc

    # ------------------------------------------------------------------ #
    # Public methods
    # ------------------------------------------------------------------ #

    def submit_id_verification(
        self,
        job_type: JobType,
        user_id: str,
        id_info: IDInfo,
        biometric_info: Optional[BiometricInfo] = None,
        callback_url: Optional[str] = None,
        job_endpoint: str = "/v1/id_verification",
    ) -> Dict[str, Any]:
        """
        Submit an ID verification job.

        Args:
            job_type: Logical job type (mapped by your integration).
            user_id: Unique user identifier in your system.
            id_info: Core ID information (country, id_type, id_number, etc.).
            biometric_info: Optional biometric payload (images/templates).
            callback_url: Optional webhook callback URL.
            job_endpoint: Relative API path; default is a common pattern
                but should be adjusted to match Smile Identity docs.
        """
        body: Dict[str, Any] = {
            "user_id": user_id,
            "job_type": job_type.value,
            "id_info": id_info.to_payload(),
        }
        if biometric_info:
            body["biometric"] = biometric_info.to_payload()
        if callback_url:
            body["callback_url"] = callback_url

        return self._request("POST", job_endpoint, json_body=body)

    def get_job_status(
        self,
        job_id: str,
        user_id: Optional[str] = None,
        status_endpoint: str = "/v1/job_status",
    ) -> Dict[str, Any]:
        """
        Retrieve status for a previously-submitted job.

        Args:
            job_id: Identifier returned when the job was created.
            user_id: Optional user identifier.
            status_endpoint: Relative API path; adjust as per Smile docs.
        """
        body: Dict[str, Any] = {
            "job_id": job_id,
        }
        if user_id:
            body["user_id"] = user_id

        return self._request("POST", status_endpoint, json_body=body)
