"""
OpenRouterChatAdapter - Usage Example

Demonstrates:
- Initializing the OpenRouterChatAdapter
- Sending a simple chat completion request through OpenRouter

CLI flags:
    -d, -v, --debug, --verbose  Enable LLM debug logging for OpenRouter
    -h, --help                  Show this help message

Requires:
    OPENROUTER_API_KEY environment variable (or pass api_key explicitly).
"""

import argparse
import logging
import os

from openrouter_adapter import (
    OpenRouterChatAdapter,
    ChatMessage,
    OpenRouterError,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Example usage of OpenRouterChatAdapter for InfraFabric."
    )
    parser.add_argument(
        "-d",
        "-v",
        "--debug",
        "--verbose",
        dest="debug",
        action="store_true",
        help="Enable LLM debug logging for OpenRouter (sets IF_LLM_DEBUG_OPENROUTER=1).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.debug:
        os.environ["IF_LLM_DEBUG_OPENROUTER"] = "1"

    model = os.getenv("OPENROUTER_MODEL", "openrouter/auto")
    site_url = os.getenv("OPENROUTER_SITE_URL", "https://infra.example.com")
    app_name = os.getenv("OPENROUTER_APP_NAME", "InfraFabric LLM Demo")

    try:
        adapter = OpenRouterChatAdapter(
            model=model,
            site_url=site_url,
            app_name=app_name,
        )
    except OpenRouterError as exc:
        logger.error("Failed to initialize OpenRouterChatAdapter: %s", exc)
        return

    messages = [
        ChatMessage(role="system", content="You are an assistant helping with InfraFabric."),
        ChatMessage(role="user", content="Give me a concise InfraFabric value proposition."),
    ]

    try:
        response = adapter.chat_completion(messages=messages, temperature=0.7)
    except OpenRouterError as exc:
        logger.error("OpenRouter API call failed: %s", exc)
        return

    content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
    logger.info("Model response:\n%s", content)


if __name__ == "__main__":
    main()
