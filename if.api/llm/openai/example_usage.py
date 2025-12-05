"""
OpenAIChatAdapter - Usage Example

Demonstrates:
- Initializing the OpenAIChatAdapter
- Sending a simple chat completion request

CLI flags:
    -d, -v, --debug, --verbose  Enable LLM debug logging for OpenAI
    -h, --help                  Show this help message

Requires:
    OPENAI_API_KEY environment variable (or pass api_key explicitly).
"""

import argparse
import logging
import os

from openai_adapter import OpenAIChatAdapter, ChatMessage, OpenAIError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Example usage of OpenAIChatAdapter for InfraFabric."
    )
    parser.add_argument(
        "-d",
        "-v",
        "--debug",
        "--verbose",
        dest="debug",
        action="store_true",
        help="Enable LLM debug logging for OpenAI (sets IF_LLM_DEBUG_OPENAI=1).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.debug:
        os.environ["IF_LLM_DEBUG_OPENAI"] = "1"

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    try:
        adapter = OpenAIChatAdapter(model=model)
    except OpenAIError as exc:
        logger.error("Failed to initialize OpenAIChatAdapter: %s", exc)
        return

    messages = [
        ChatMessage(role="system", content="You are an assistant helping with InfraFabric."),
        ChatMessage(role="user", content="Give me a one-sentence description of InfraFabric."),
    ]

    try:
        response = adapter.chat_completion(messages=messages, temperature=0.4)
    except OpenAIError as exc:
        logger.error("OpenAI API call failed: %s", exc)
        return

    content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
    logger.info("Model response:\n%s", content)


if __name__ == "__main__":
    main()
