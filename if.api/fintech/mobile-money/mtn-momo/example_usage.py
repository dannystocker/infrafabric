"""
MTN MoMo Adapter - Example Usage

Minimal example showing how to initialize the MTNMoMoAdapter and
perform a simple health check (access token retrieval).

CLI flags:
    -d, -v, --debug, --verbose  Enable fintech debug logging for MTN MoMo
    -h, --help                  Show this help message
"""

import argparse
import logging
import os

from mtn_momo_adapter import (
    MTNMoMoAdapter,
    CountryCode,
    AuthenticationError,
    APIError,
    ValidationError,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MTN MoMo adapter example usage for InfraFabric."
    )
    parser.add_argument(
        "-d",
        "-v",
        "--debug",
        "--verbose",
        dest="debug",
        action="store_true",
        help="Enable fintech debug logging for MTN MoMo (sets IF_FINTECH_DEBUG_MTN_MOMO=1).",
    )
    return parser.parse_args()


def main() -> None:
    subscription_key = os.getenv("MTN_MOMO_SUBSCRIPTION_KEY", "your-subscription-key")
    api_user = os.getenv("MTN_MOMO_API_USER", "your-api-user")
    api_key = os.getenv("MTN_MOMO_API_KEY", "your-api-key")
    country_code = os.getenv("MTN_MOMO_COUNTRY", "UG")

    try:
        country = CountryCode(country_code)
    except ValueError:
        logger.error("Unsupported MTN MoMo country code: %s", country_code)
        return

    adapter = MTNMoMoAdapter(
        subscription_key=subscription_key,
        api_user=api_user,
        api_key=api_key,
        country=country,
        environment=os.getenv("MTN_MOMO_ENVIRONMENT", "sandbox"),
        timeout=30,
    )

    logger.info("Initialized MTN MoMo adapter for %s", country.value)

    try:
        token = adapter._get_access_token()  # Health-check style call
        logger.info("Access token retrieved (prefix): %s...", token[:8])
    except AuthenticationError as exc:
        logger.error("Authentication failed: %s", exc)
    except APIError as exc:
        logger.error("API error while fetching token: %s", exc)
    except ValidationError as exc:
        logger.error("Validation error: %s", exc)
    finally:
        adapter.close()


if __name__ == "__main__":
    args = parse_args()
    if args.debug:
        os.environ["IF_FINTECH_DEBUG_MTN_MOMO"] = "1"

    main()

