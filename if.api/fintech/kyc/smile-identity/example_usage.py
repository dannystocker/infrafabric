"""
Smile Identity REST API Adapter - Usage Example

Demonstrates how to:
- Initialize the SmileIdentityAdapter
- Submit a basic ID verification job
- Poll job status

CLI flags:
    -d, -v, --debug, --verbose  Enable fintech debug logging for Smile Identity
    -h, --help                  Show this help message

This script is meant as a reference; consult Smile Identity documentation for
the exact fields and job types you should use for production.
"""

import argparse
import os
import logging
from time import sleep

from smile_identity_adapter import (
    SmileIdentityAdapter,
    JobType,
    IDInfo,
    BiometricInfo,
    AuthenticationError,
    APIError,
    SmileIdentityError,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Smile Identity REST API adapter example."
    )
    parser.add_argument(
        "-d",
        "-v",
        "--debug",
        "--verbose",
        dest="debug",
        action="store_true",
        help="Enable fintech debug logging for Smile Identity (sets IF_FINTECH_DEBUG_SMILE_IDENTITY=1).",
    )
    return parser.parse_args()


def create_adapter() -> SmileIdentityAdapter:
    """
    Initialize SmileIdentityAdapter from environment variables.

    Expected variables:
        SMILE_PARTNER_ID
        SMILE_API_KEY
        SMILE_BASE_URL (optional, defaults to test URL)
    """
    partner_id = os.getenv("SMILE_PARTNER_ID", "your_partner_id")
    api_key = os.getenv("SMILE_API_KEY", "your_api_key")
    base_url = os.getenv("SMILE_BASE_URL", "https://testapi.smileidentity.com")

    adapter = SmileIdentityAdapter(
        partner_id=partner_id,
        api_key=api_key,
        base_url=base_url,
        timeout=60,
        logger=logger,
    )
    return adapter


def example_id_verification() -> None:
    """Submit an ID verification job and poll status."""
    logger.info("=" * 70)
    logger.info("EXAMPLE: Smile Identity ID Verification")
    logger.info("=" * 70)

    try:
        adapter = create_adapter()
    except AuthenticationError as exc:
        logger.error("Adapter initialization failed: %s", exc)
        return

    # Basic ID info (adjust these values to match your integration)
    id_info = IDInfo(
        country="NG",
        id_type="BVN",
        id_number="12345678901",
        first_name="Jane",
        last_name="Doe",
    )

    # Optional biometric payload (selfie image etc.); left empty here
    biometric = BiometricInfo()

    user_id = "user-123"

    try:
        response = adapter.submit_id_verification(
            job_type=JobType.BASIC_KYC,
            user_id=user_id,
            id_info=id_info,
            biometric_info=biometric,
            callback_url=os.getenv("SMILE_CALLBACK_URL"),
        )
    except (AuthenticationError, APIError, SmileIdentityError) as exc:
        logger.error("Failed to submit ID verification job: %s", exc)
        return

    job_id = response.get("job_id") or response.get("jobId") or "unknown"
    logger.info("✓ Job submitted: job_id=%s", job_id)

    # Simple status poll (for demo only; in production rely on callbacks/webhooks)
    for attempt in range(3):
        logger.info("Polling job status (attempt %s)...", attempt + 1)
        try:
            status = adapter.get_job_status(job_id=job_id, user_id=user_id)
        except (AuthenticationError, APIError, SmileIdentityError) as exc:
            logger.error("Failed to get job status: %s", exc)
            break

        logger.info("Job status response: %s", status)
        sleep(2)


if __name__ == "__main__":
    args = parse_args()
    if args.debug:
        os.environ["IF_FINTECH_DEBUG_SMILE_IDENTITY"] = "1"

    example_id_verification()
