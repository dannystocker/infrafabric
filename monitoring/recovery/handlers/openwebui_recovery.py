#!/usr/bin/env python3
"""
OpenWebUI Recovery Handler

Implements recovery strategies for OpenWebUI API issues, authentication failures,
and model unavailability.

Citation: if://agent/A35_openwebui_recovery_handler
Author: Agent A35
Date: 2025-11-30
"""

import logging
import time
import requests
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


def handle_openwebui_recovery(strategy: str, context: Dict[str, Any],
                             orchestrator: Any) -> bool:
    """
    Execute OpenWebUI recovery strategy.

    Args:
        strategy: Recovery strategy name
        context: Context with additional parameters
        orchestrator: Parent recovery orchestrator

    Returns:
        True if recovery successful, False otherwise
    """
    if strategy == 'token_refresh':
        return _handle_token_refresh(context)
    elif strategy == 'model_failover':
        return _handle_model_failover(context, orchestrator)
    elif strategy == 'graceful_degradation':
        return _handle_graceful_degradation(context, orchestrator)
    else:
        logger.warning(f"Unknown OpenWebUI recovery strategy: {strategy}")
        return False


def _handle_token_refresh(context: Dict[str, Any]) -> bool:
    """Refresh expired authentication token."""
    try:
        base_url = context.get('base_url', 'http://localhost:8000')
        username = context.get('username', 'admin')
        password = context.get('password')
        max_retries = context.get('max_retries', 2)

        if not password:
            logger.error("Token refresh: password not provided")
            return False

        logger.info(f"OpenWebUI token refresh: Refreshing token for {username}")

        for attempt in range(max_retries):
            try:
                # OpenWebUI token endpoint
                auth_url = f"{base_url}/api/v1/auth/login"

                response = requests.post(
                    auth_url,
                    json={"email": username, "password": password},
                    timeout=10
                )

                if response.status_code == 200:
                    token = response.json().get('token')
                    if token:
                        logger.info("OpenWebUI token refresh: Token refreshed successfully")
                        # Store token in context for future use
                        context['token'] = token
                        return True
                    else:
                        logger.error("Token refresh: No token in response")
                        return False

                elif response.status_code == 401:
                    logger.warning("Token refresh: Invalid credentials")
                    return False

                else:
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Token refresh: Attempt {attempt + 1}/{max_retries} failed "
                        f"(status {response.status_code}), waiting {wait_time}s"
                    )
                    time.sleep(wait_time)

            except requests.RequestException as e:
                wait_time = 2 ** attempt
                logger.warning(
                    f"Token refresh: Attempt {attempt + 1}/{max_retries} failed "
                    f"(request error), waiting {wait_time}s: {e}"
                )
                time.sleep(wait_time)

        logger.error("Token refresh: All retry attempts failed")
        return False

    except Exception as e:
        logger.error(f"Token refresh handler error: {e}", exc_info=True)
        return False


def _handle_model_failover(context: Dict[str, Any],
                          orchestrator: Any) -> bool:
    """Failover to alternative model when primary is unavailable."""
    try:
        base_url = context.get('base_url', 'http://localhost:8000')
        token = context.get('token')
        current_model = context.get('current_model')
        fallback_models = context.get('fallback_models', ['deepseek-chat', 'gemini-pro'])

        logger.info(
            f"OpenWebUI model failover: Switching from {current_model} "
            f"to alternatives"
        )

        if not token:
            logger.error("Model failover: No authentication token")
            return False

        # Get available models
        try:
            models_url = f"{base_url}/api/v1/models"
            headers = {'Authorization': f'Bearer {token}'}

            response = requests.get(models_url, headers=headers, timeout=10)

            if response.status_code == 200:
                available = response.json().get('models', [])
                model_names = [m.get('name') for m in available]

                logger.info(f"Available models: {model_names}")

                # Find first available fallback
                for fallback in fallback_models:
                    if fallback in model_names:
                        logger.info(
                            f"OpenWebUI model failover: Using fallback model {fallback}"
                        )
                        context['current_model'] = fallback

                        # Activate degraded mode
                        if orchestrator:
                            orchestrator.activate_degraded_mode(
                                'openwebui_model_failover',
                                f'Using fallback model {fallback}'
                            )

                        return True

                logger.warning(
                    f"Model failover: No fallback models available from {fallback_models}"
                )
                return False

            else:
                logger.error(f"Model failover: Failed to get models (status {response.status_code})")
                return False

        except requests.RequestException as e:
            logger.error(f"Model failover request error: {e}")
            return False

    except Exception as e:
        logger.error(f"Model failover handler error: {e}", exc_info=True)
        return False


def _handle_graceful_degradation(context: Dict[str, Any],
                                orchestrator: Any) -> bool:
    """Enable graceful degradation mode due to rate limiting or availability issues."""
    try:
        logger.warning("OpenWebUI graceful degradation: Activating degraded mode")

        # Activate degraded mode
        if orchestrator:
            orchestrator.activate_degraded_mode(
                'openwebui_unavailable',
                'Rate limiting or service unavailable - using direct API'
            )

        # Configure fallback to direct API
        context['use_direct_api'] = True
        context['direct_api_model'] = context.get('direct_api_model', 'claude-3-sonnet')

        logger.info(
            "OpenWebUI graceful degradation: Using direct API "
            f"with model {context.get('direct_api_model')}"
        )

        return True

    except Exception as e:
        logger.error(
            f"Graceful degradation handler error: {e}",
            exc_info=True
        )
        return False
