"""
Mistral Chat Completions Adapter

Minimal adapter for the Mistral AI chat completions API. This intentionally
avoids pulling in an SDK and instead uses `requests` so it can run inside
the broader InfraFabric environment without extra dependencies.

For full API details, consult Mistral's official documentation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Union

import os
import requests

from llm_debug_utils import debug_log_request, debug_log_response


class MistralError(Exception):
    """Base exception for Mistral adapter."""


class AuthenticationError(MistralError):
    """Authentication or authorization failure."""


class APIError(MistralError):
    """Non-success HTTP response."""

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


@dataclass
class ChatMessage:
    """Simple chat message structure."""

    role: str
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class MistralChatAdapter:
    """
    Adapter for Mistral AI chat completions.

    Example:
        adapter = MistralChatAdapter(model="mistral-large-latest")
        response = adapter.chat_completion(
            messages=[ChatMessage(role="user", content="Hello, Mistral!")],
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.mistral.ai/v1",
        model: str = "mistral-large-latest",
        timeout: int = 60,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise AuthenticationError("MISTRAL_API_KEY not set and no api_key provided")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat_completion(
        self,
        messages: Sequence[Union[ChatMessage, Dict[str, str]]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Call Mistral's /chat/completions endpoint.

        Args:
            messages: List of ChatMessage or raw dicts with role/content.
            model: Optional override for model name.
            temperature: Sampling temperature.
            max_tokens: Optional max_tokens parameter.
            extra_params: Additional fields to include in the JSON payload.
        """
        model_name = model or self.model
        payload: Dict[str, Any] = {
            "model": model_name,
            "messages": [
                m.to_dict() if isinstance(m, ChatMessage) else m for m in messages
            ],
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if extra_params:
            payload.update(extra_params)

        url = f"{self.base_url}/chat/completions"
        debug_log_request(self.logger, "mistral", url, payload)

        try:
            response = self.session.post(
                url,
                headers=self._headers(),
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise MistralError(f"Failed to reach Mistral API: {exc}") from exc

        debug_log_response(self.logger, "mistral", response.status_code, response.text)

        if response.status_code == 401:
            raise AuthenticationError("Invalid Mistral API key or unauthorized request")

        if not (200 <= response.status_code < 300):
            try:
                body = response.json()
            except ValueError:
                body = {"raw": response.text}
            raise APIError(
                f"Mistral API error {response.status_code}",
                status_code=response.status_code,
                response_body=body,
            )

        try:
            return response.json()
        except ValueError as exc:
            raise APIError("Mistral API returned non-JSON response") from exc
