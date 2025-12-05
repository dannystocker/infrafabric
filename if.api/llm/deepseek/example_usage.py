"""
DeepSeekChatAdapter - Usage Example

Demonstrates:
- Initializing the DeepSeekChatAdapter
- Sending a simple chat completion request

CLI flags:
    -d, -v, --debug, --verbose  Enable LLM debug logging for DeepSeek
    -h, --help                  Show this help message

Requires:
    DEEPSEEK_API_KEY environment variable (or pass api_key explicitly).
"""

import argparse
import logging
import os

from deepseek_adapter import DeepSeekChatAdapter, ChatMessage, DeepSeekError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Example usage of DeepSeekChatAdapter for InfraFabric."
    )
    parser.add_argument(
        "-d",
        "-v",
        "--debug",
        "--verbose",
        dest="debug",
        action="store_true",
        help="Enable LLM debug logging for DeepSeek (sets IF_LLM_DEBUG_DEEPSEEK=1).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.debug:
        os.environ["IF_LLM_DEBUG_DEEPSEEK"] = "1"

    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    try:
        adapter = DeepSeekChatAdapter(model=model)
    except DeepSeekError as exc:
        logger.error("Failed to initialize DeepSeekChatAdapter: %s", exc)
        return

    messages = [
        ChatMessage(role="system", content="You are an assistant helping with InfraFabric."),
        ChatMessage(role="user", content="Explain why DeepSeek is useful as a fallback model."),
    ]

    try:
        response = adapter.chat_completion(messages=messages, temperature=0.6)
    except DeepSeekError as exc:
        logger.error("DeepSeek API call failed: %s", exc)
        return

    content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
    logger.info("Model response:\n%s", content)


if __name__ == "__main__":
    main()
