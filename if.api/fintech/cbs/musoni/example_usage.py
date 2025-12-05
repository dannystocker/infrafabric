"""
Musoni Core Banking API Adapter - Usage Examples

This file demonstrates basic usage of the Musoni adapter:
- Verifying connection to the Musoni/Fineract-style API
- Creating a client
- Submitting and approving/disbursing a loan

CLI flags:
    -d, -v, --debug, --verbose  Enable fintech debug logging for Musoni
    -h, --help                  Show this help message

Run these examples against a live Musoni environment or a local Fineract-style
test instance configured for Musoni.
"""

import argparse
import os
import logging
from datetime import datetime, timedelta

from musoni_adapter import (
    MusoniAdapter,
    MusoniClientData,
    MusoniLoanApplicationData,
    MusoniEnvironment,
    AuthenticationError,
    ConnectionError,
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
        description="Musoni Core Banking API adapter examples."
    )
    parser.add_argument(
        "-d",
        "-v",
        "--debug",
        "--verbose",
        dest="debug",
        action="store_true",
        help="Enable fintech debug logging for Musoni (sets IF_FINTECH_DEBUG_MUSONI=1).",
    )
    return parser.parse_args()


def create_adapter() -> MusoniAdapter:
    """
    Initialize MusoniAdapter from environment variables.

    Expected variables:
        MUSONI_BASE_URL
        MUSONI_USERNAME
        MUSONI_PASSWORD
        MUSONI_TENANT_ID (optional)
    """
    base_url = os.getenv("MUSONI_BASE_URL", "http://localhost:8080/musoni-provider")
    username = os.getenv("MUSONI_USERNAME", "musoni")
    password = os.getenv("MUSONI_PASSWORD", "password")
    tenant_id = os.getenv("MUSONI_TENANT_ID") or None

    adapter = MusoniAdapter(
        base_url=base_url,
        username=username,
        password=password,
        tenant_id=tenant_id,
        timeout=30,
        verify_ssl=False,
        environment=MusoniEnvironment.DEVELOPMENT,
    )
    return adapter


def example_connection() -> None:
    """Verify connection to Musoni API."""
    logger.info("=" * 70)
    logger.info("EXAMPLE 1: Verify Musoni Connection")
    logger.info("=" * 70)

    adapter = create_adapter()
    ok = adapter.verify_connection()
    if ok:
        logger.info("✓ Musoni connection successful")
    else:
        logger.error("✗ Musoni connection failed")


def example_client_and_loan() -> None:
    """
    Create a client and submit a basic loan application.
    """
    logger.info("=" * 70)
    logger.info("EXAMPLE 2: Client + Loan Workflow")
    logger.info("=" * 70)

    adapter = create_adapter()

    try:
        if not adapter.verify_connection():
            logger.error("Cannot proceed without a valid Musoni connection")
            return
    except (AuthenticationError, ConnectionError) as exc:
        logger.error("Connection/authentication error: %s", exc)
        return

    # Create client
    client_data = MusoniClientData(
        first_name="Jane",
        last_name="Kipchoge",
        phone_number="+254712345678",
        external_id=f"MUSONI-CLIENT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
    )

    try:
        client_result = adapter.create_client(client_data)
    except (ValidationError, APIError) as exc:
        logger.error("Failed to create client: %s", exc)
        return

    client_id = client_result["client_id"]
    logger.info("✓ Client created: %s", client_id)

    # Submit loan application
    today = datetime.utcnow().date()
    disbursement_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")

    loan_data = MusoniLoanApplicationData(
        client_id=client_id,
        product_id=1,
        principal_amount=50000.0,
        number_of_repayments=12,
        loan_term_frequency=12,
        loan_term_frequency_type=2,  # 2 = Monthly in many Fineract-style APIs
        interest_rate_per_period=2.5,
        expected_disbursement_date=disbursement_date,
        submitted_on_date=today.strftime("%Y-%m-%d"),
        external_id=f"MUSONI-LOAN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
    )

    try:
        loan_result = adapter.submit_loan_application(loan_data)
    except (ValidationError, APIError) as exc:
        logger.error("Failed to submit loan application: %s", exc)
        return

    loan_id = loan_result["loan_id"]
    logger.info("✓ Loan application submitted: %s", loan_id)

    # Approve loan
    try:
        adapter.approve_loan(
            loan_id=loan_id,
            note="Approved via Musoni adapter example script",
            approved_on_date=today.strftime("%Y-%m-%d"),
        )
        logger.info("✓ Loan approved: %s", loan_id)
    except APIError as exc:
        logger.error("Failed to approve loan: %s", exc)
        return

    # Disburse loan
    try:
        adapter.disburse_loan(
            loan_id=loan_id,
            transaction_amount=50000.0,
            actual_disbursement_date=disbursement_date,
            external_id=f"MUSONI-DISB-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        )
        logger.info("✓ Loan disbursed: %s", loan_id)
    except APIError as exc:
        logger.error("Failed to disburse loan: %s", exc)


if __name__ == "__main__":
    args = parse_args()
    if args.debug:
        os.environ["IF_FINTECH_DEBUG_MUSONI"] = "1"

    example_connection()
    example_client_and_loan()
