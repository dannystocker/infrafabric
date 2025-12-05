"""
DeepSeek Chat Completions Adapter

Minimal adapter for DeepSeek's chat completions API. This uses `requests`
and an OpenAI-style interface so it can slot into InfraFabric's LLM layer
without extra dependencies.

For exact API details, refer to DeepSeek's official documentation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Union

import os
import requests

from llm_debug_utils import debug_log_request, debug_log_response


class DeepSeekError(Exception):
    """Base exception for DeepSeek adapter."""


class AuthenticationError(DeepSeekError):
    """Authentication or authorization failure."""


class APIError(DeepSeekError):
    """Non-success HTTP response from DeepSeek."""

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


class DeepSeekChatAdapter:
    """
    Adapter for DeepSeek chat completions.

    Example:
        adapter = DeepSeekChatAdapter(model="deepseek-chat")
        response = adapter.chat_completion(
            messages=[ChatMessage(role="user", content="Hello, DeepSeek!")],
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com/v1",
        model: str = "deepseek-chat",
        timeout: int = 60,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise AuthenticationError("DEEPSEEK_API_KEY not set and no api_key provided")

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
        Call DeepSeek's chat completions endpoint.

        Args:
            messages: List of ChatMessage or raw dicts with role/content.
            model: Optional override for model name.
            temperature: Sampling temperature.
            max_tokens: Optional max_tokens parameter.
            extra_params: Additional JSON fields for the request body.
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
        debug_log_request(self.logger, "deepseek", url, payload)

        try:
            response = self.session.post(
                url,
                headers=self._headers(),
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise DeepSeekError(f"Failed to reach DeepSeek API: {exc}") from exc

        debug_log_response(self.logger, "deepseek", response.status_code, response.text)

        if response.status_code == 401:
            raise AuthenticationError("Invalid DeepSeek API key or unauthorized request")

        if not (200 <= response.status_code < 300):
            try:
                body = response.json()
            except ValueError:
                body = {"raw": response.text}
            raise APIError(
                f"DeepSeek API error {response.status_code}",
                status_code=response.status_code,
                response_body=body,
            )

        try:
            return response.json()
        except ValueError as exc:
            raise APIError("DeepSeek API returned non-JSON response") from exc
