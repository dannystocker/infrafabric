"""
MistralChatAdapter - Usage Example

Demonstrates:
- Initializing the MistralChatAdapter
- Sending a simple chat completion request

CLI flags:
    -d, -v, --debug, --verbose  Enable LLM debug logging for Mistral
    -h, --help                  Show this help message

Requires:
    MISTRAL_API_KEY environment variable (or pass api_key explicitly).
"""

import argparse
import logging
import os

from mistral_adapter import MistralChatAdapter, ChatMessage, MistralError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Example usage of MistralChatAdapter for InfraFabric."
    )
    parser.add_argument(
        "-d",
        "-v",
        "--debug",
        "--verbose",
        dest="debug",
        action="store_true",
        help="Enable LLM debug logging for Mistral (sets IF_LLM_DEBUG_MISTRAL=1).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.debug:
        os.environ["IF_LLM_DEBUG_MISTRAL"] = "1"

    model = os.getenv("MISTRAL_MODEL", "mistral-large-latest")

    try:
        adapter = MistralChatAdapter(model=model)
    except MistralError as exc:
        logger.error("Failed to initialize MistralChatAdapter: %s", exc)
        return

    messages = [
        ChatMessage(role="system", content="You are an assistant helping with InfraFabric."),
        ChatMessage(role="user", content="Summarize the InfraFabric API layer in one paragraph."),
    ]

    try:
        response = adapter.chat_completion(messages=messages, temperature=0.5)
    except MistralError as exc:
        logger.error("Mistral API call failed: %s", exc)
        return

    content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
    logger.info("Model response:\n%s", content)


if __name__ == "__main__":
    main()
