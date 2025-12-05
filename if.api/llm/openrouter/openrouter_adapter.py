"""
OpenRouter Chat Completions Adapter

Minimal adapter for the OpenRouter API. OpenRouter exposes many upstream
models behind a single /chat/completions interface, with some additional
headers for attribution.

For full details see OpenRouter's official documentation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Union

import os
import requests

from llm_debug_utils import debug_log_request, debug_log_response


class OpenRouterError(Exception):
    """Base exception for OpenRouter adapter."""


class AuthenticationError(OpenRouterError):
    """Authentication or authorization failure."""


class APIError(OpenRouterError):
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


class OpenRouterChatAdapter:
    """
    Adapter for the OpenRouter chat completions API.

    Example:
        adapter = OpenRouterChatAdapter(model="openrouter/auto")
        response = adapter.chat_completion(
            messages=[ChatMessage(role="user", content="Hello, OpenRouter!")],
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
        model: str = "openrouter/auto",
        timeout: int = 60,
        site_url: Optional[str] = None,
        app_name: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "OPENROUTER_API_KEY not set and no api_key provided"
            )

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.site_url = site_url
        self.app_name = app_name
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        # Recommended attribution headers for OpenRouter
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.app_name:
            headers["X-Title"] = self.app_name
        return headers

    def chat_completion(
        self,
        messages: Sequence[Union[ChatMessage, Dict[str, str]]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Call OpenRouter's /chat/completions endpoint.

        Args:
            messages: List of ChatMessage or raw dicts with role/content.
            model: Optional override for model name (OpenRouter model slug).
            temperature: Sampling temperature.
            max_tokens: Optional max_tokens parameter.
            extra_params: Additional JSON fields to send.
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
        debug_log_request(self.logger, "openrouter", url, payload)

        try:
            response = self.session.post(
                url,
                headers=self._headers(),
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise OpenRouterError(f"Failed to reach OpenRouter API: {exc}") from exc

        debug_log_response(self.logger, "openrouter", response.status_code, response.text)

        if response.status_code == 401:
            raise AuthenticationError(
                "Invalid OpenRouter API key or unauthorized request"
            )

        if not (200 <= response.status_code < 300):
            try:
                body = response.json()
            except ValueError:
                body = {"raw": response.text}
            raise APIError(
                f"OpenRouter API error {response.status_code}",
                status_code=response.status_code,
                response_body=body,
            )

        try:
            return response.json()
        except ValueError as exc:
            raise APIError("OpenRouter API returned non-JSON response") from exc
