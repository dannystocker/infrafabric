"""
TransUnion Adapter - Example Usage

Demonstrates all major adapter functionality with proper error handling
and IF.bus event integration.

This example covers:
1. Authentication with OAuth2
2. Credit report queries
3. Credit score retrieval
4. ID verification
5. Fraud detection
6. Loan performance reporting
7. Event handling
8. Health checks

CLI flags:
    -d, -v, --debug, --verbose  Enable fintech debug logging for TransUnion
    -h, --help                  Show this help message

Requirements:
- TransUnion API credentials (update in code or use environment variables)
- Python 3.7+
"""

import argparse
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Optional

from transunion_adapter import (
    TransUnionAdapter,
    CreditReport,
    CreditScore,
    VerificationResult,
    FraudCheckResult,
    AuthenticationError,
    ConnectionError,
    APIError,
    ValidationError,
    TimeoutError,
)


# ============================================================================
# Setup
# ============================================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Event Handlers (IF.bus Integration)
# ============================================================================

def on_authenticated(event: dict) -> None:
    """Handle authentication success."""
    logger.info(f"✓ Authenticated with {event['auth_type']}")


def on_credit_report_retrieved(event: dict) -> None:
    """Handle credit report retrieval."""
    logger.info(
        f"✓ Credit report retrieved: query_id={event['query_id']}, "
        f"score={event['score']}, status={event['status']}"
    )


def on_score_retrieved(event: dict) -> None:
    """Handle score retrieval."""
    logger.info(
        f"✓ Score retrieved: {event['score']} ({event['rating']}), "
        f"confidence={event['confidence']:.1%}"
    )


def on_id_verified(event: dict) -> None:
    """Handle ID verification."""
    logger.info(
        f"✓ ID verified: status={event['status']}, "
        f"match={event['name_match']}, confidence={event['confidence']:.1%}"
    )


def on_fraud_check_completed(event: dict) -> None:
    """Handle fraud check completion."""
    logger.info(
        f"✓ Fraud check completed: risk_level={event['risk_level']}, "
        f"risk_score={event['risk_score']:.1%}, alerts={event['alert_count']}"
    )


def on_data_submitted(event: dict) -> None:
    """Handle data submission."""
    logger.info(
        f"✓ Data submitted: loan_id={event['loan_id']}, "
        f"success={event['success']}"
    )


def on_error(event: dict) -> None:
    """Handle errors."""
    logger.error(
        f"✗ Error [{event['error_type']}] in {event.get('context', 'unknown')}: "
        f"{event['error']}"
    )


def on_connection_state_changed(event: dict) -> None:
    """Handle connection state changes."""
    logger.info(f"→ Connection state: {event['state']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="TransUnion Africa credit bureau adapter examples."
    )
    parser.add_argument(
        "-d",
        "-v",
        "--debug",
        "--verbose",
        dest="debug",
        action="store_true",
        help="Enable fintech debug logging for TransUnion (sets IF_FINTECH_DEBUG_TRANSUNION=1).",
    )
    return parser.parse_args()


# ============================================================================
# Example: Basic Connection
# ============================================================================

def example_basic_connection() -> Optional[TransUnionAdapter]:
    """Initialize and connect to TransUnion API."""
    logger.info("\n" + "=" * 70)
    logger.info("EXAMPLE 1: Basic Connection")
    logger.info("=" * 70)

    # Get credentials from environment or use defaults
    client_id = os.getenv("TRANSUNION_CLIENT_ID", "test_client_id")
    client_secret = os.getenv("TRANSUNION_CLIENT_SECRET", "test_client_secret")
    api_key = os.getenv("TRANSUNION_API_KEY", "test_api_key")
    market = os.getenv("TRANSUNION_MARKET", "ke")
    environment = os.getenv("TRANSUNION_ENVIRONMENT", "sandbox")

    adapter = TransUnionAdapter(
        auth_type="oauth2",  # or "api_key" or "certificate"
        client_id=client_id,
        client_secret=client_secret,
        # api_key=api_key,  # For API key auth
        market=market,
        environment=environment,
        timeout=30,
        max_retries=3,
        logger=logger
    )

    # Register event handlers
    adapter.on("authenticated", on_authenticated)
    adapter.on("error", on_error)
    adapter.on("connection_state_changed", on_connection_state_changed)

    # Connect
    try:
        adapter.connect()
        logger.info(f"Connection state: {adapter.get_connection_state()}")
        return adapter
    except ConnectionError as e:
        logger.error(f"Failed to connect: {e}")
        return None
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        return None


# ============================================================================
# Example: Credit Report Query
# ============================================================================

def example_credit_report(adapter: TransUnionAdapter) -> Optional[CreditReport]:
    """Query credit report for an individual."""
    logger.info("\n" + "=" * 70)
    logger.info("EXAMPLE 2: Credit Report Query")
    logger.info("=" * 70)

    adapter.on("credit_report_retrieved", on_credit_report_retrieved)
    adapter.on("error", on_error)

    try:
        report = adapter.get_credit_report(
            id_type="national_id",
            id_number="12345678",
            first_name="John",
            last_name="Doe",
            query_type="full_report",
            include_history=True
        )

        # Display report information
        logger.info(f"\nCredit Report Details:")
        logger.info(f"  Subject ID: {report.subject_id}")
        logger.info(f"  Query ID: {report.query_id}")
        logger.info(f"  Score: {report.score.score} ({report.score.rating})")
        logger.info(f"  Status: {report.status}")
        logger.info(f"  Accounts: {report.accounts_count}")
        logger.info(f"  Total Debt: {report.total_debt:,.2f}")
        logger.info(f"  Delinquent Accounts: {report.delinquent_accounts}")
        logger.info(f"  Delinquency Status: {report.delinquency_status}")
        logger.info(f"  Retrieved: {report.retrieved_at}")

        return report

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
    except APIError as e:
        logger.error(f"API error: {e}")
    except TimeoutError as e:
        logger.error(f"Request timeout: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    return None


# ============================================================================
# Example: Quick Credit Score Check
# ============================================================================

def example_credit_score(adapter: TransUnionAdapter) -> Optional[CreditScore]:
    """Perform quick credit score check."""
    logger.info("\n" + "=" * 70)
    logger.info("EXAMPLE 3: Quick Credit Score Check")
    logger.info("=" * 70)

    adapter.on("score_retrieved", on_score_retrieved)
    adapter.on("error", on_error)

    try:
        score = adapter.get_credit_score(
            id_type="national_id",
            id_number="12345678",
            first_name="John",
            last_name="Doe"
        )

        logger.info(f"\nCredit Score Details:")
        logger.info(f"  Score: {score.score}")
        logger.info(f"  Range: {score.range_min}-{score.range_max}")
        logger.info(f"  Rating: {score.rating}")
        logger.info(f"  Confidence: {score.confidence:.1%}")
        logger.info(f"  Last Updated: {score.last_updated}")

        return score

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
    except APIError as e:
        logger.error(f"API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    return None


# ============================================================================
# Example: ID Verification
# ============================================================================

def example_id_verification(adapter: TransUnionAdapter) -> Optional[VerificationResult]:
    """Verify individual identity."""
    logger.info("\n" + "=" * 70)
    logger.info("EXAMPLE 4: ID Verification")
    logger.info("=" * 70)

    adapter.on("id_verified", on_id_verified)
    adapter.on("error", on_error)

    try:
        result = adapter.verify_id(
            id_type="national_id",
            id_number="12345678",
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-15",
            country_code="KE"
        )

        logger.info(f"\nVerification Result:")
        logger.info(f"  Verification ID: {result.verification_id}")
        logger.info(f"  Status: {result.status.value}")
        logger.info(f"  ID Type: {result.id_type}")
        logger.info(f"  Name Match: {result.name_match}")
        logger.info(f"  Confidence: {result.confidence:.1%}")
        logger.info(f"  Verified At: {result.verified_at}")

        if result.details:
            logger.info(f"  Details: {json.dumps(result.details, indent=2)}")

        return result

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
    except APIError as e:
        logger.error(f"API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    return None


# ============================================================================
# Example: Fraud Detection
# ============================================================================

def example_fraud_check(adapter: TransUnionAdapter) -> Optional[FraudCheckResult]:
    """Perform fraud check on individual."""
    logger.info("\n" + "=" * 70)
    logger.info("EXAMPLE 5: Fraud Detection Check")
    logger.info("=" * 70)

    adapter.on("fraud_check_completed", on_fraud_check_completed)
    adapter.on("error", on_error)

    try:
        result = adapter.check_fraud(
            id_type="national_id",
            id_number="12345678",
            first_name="John",
            last_name="Doe",
            phone="+254712345678",
            email="john.doe@example.com"
        )

        logger.info(f"\nFraud Check Result:")
        logger.info(f"  Check ID: {result.check_id}")
        logger.info(f"  Risk Level: {result.risk_level}")
        logger.info(f"  Risk Score: {result.risk_score:.1%}")
        logger.info(f"  Checked At: {result.checked_at}")

        if result.matched_patterns:
            logger.info(f"  Matched Patterns:")
            for pattern in result.matched_patterns:
                logger.info(f"    - {pattern}")

        if result.alerts:
            logger.info(f"  Alerts ({len(result.alerts)}):")
            for alert in result.alerts:
                logger.info(f"    - [{alert.get('type')}] {alert.get('message')}")

        return result

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
    except APIError as e:
        logger.error(f"API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    return None


# ============================================================================
# Example: Loan Performance Reporting
# ============================================================================

def example_loan_performance(adapter: TransUnionAdapter) -> bool:
    """Submit loan performance data to TransUnion."""
    logger.info("\n" + "=" * 70)
    logger.info("EXAMPLE 6: Loan Performance Data Submission")
    logger.info("=" * 70)

    adapter.on("data_submitted", on_data_submitted)
    adapter.on("error", on_error)

    try:
        # Simulated loan data
        success = adapter.submit_loan_performance(
            subject_id="SUBJ-123456789",
            loan_id="LOAN-2025-001",
            principal=500000.00,
            interest_rate=15.5,
            term_months=24,
            disbursement_date="2025-01-15",
            current_balance=450000.00,
            payment_status="current",
            delinquent_days=0,
            metadata={
                "lender_name": "Example Bank Limited",
                "product_type": "personal_loan",
                "currency": "KES",
                "disbursement_method": "bank_transfer"
            }
        )

        logger.info(f"\nLoan Performance Submission:")
        logger.info(f"  Success: {success}")

        return success

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
    except APIError as e:
        logger.error(f"API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    return False


# ============================================================================
# Example: Health Checks & Statistics
# ============================================================================

def example_health_check(adapter: TransUnionAdapter) -> None:
    """Perform health checks and display statistics."""
    logger.info("\n" + "=" * 70)
    logger.info("EXAMPLE 7: Health Checks & Statistics")
    logger.info("=" * 70)

    try:
        # Health check
        health = adapter.health_check()
        logger.info(f"\nAPI Health Check:")
        logger.info(f"  Status: {health.get('status')}")
        logger.info(f"  Timestamp: {health.get('timestamp')}")

    except Exception as e:
        logger.warning(f"Health check failed: {e}")

    # Adapter statistics
    stats = adapter.get_stats()
    logger.info(f"\nAdapter Statistics:")
    logger.info(f"  Connection State: {stats['connection_state']}")
    logger.info(f"  Health Status: {stats['health_status']}")
    logger.info(f"  Total Requests: {stats['request_count']}")
    logger.info(f"  Total Errors: {stats['error_count']}")
    logger.info(f"  Error Rate: {stats['error_rate']:.2%}")
    logger.info(f"  Market: {stats['market']}")
    logger.info(f"  Environment: {stats['environment']}")

    if stats['token_expiry']:
        logger.info(f"  Token Expires: {stats['token_expiry']}")


# ============================================================================
# Example: Configuration Variations
# ============================================================================

def example_different_markets(environment: str = "sandbox") -> None:
    """Show adapter initialization for different markets."""
    logger.info("\n" + "=" * 70)
    logger.info("EXAMPLE 8: Multi-Market Support")
    logger.info("=" * 70)

    markets = ["ke", "ug", "tz", "za", "rw"]

    for market in markets:
        logger.info(f"\nInitializing adapter for {market.upper()}...")

        try:
            adapter = TransUnionAdapter(
                auth_type="api_key",
                api_key="test_key",
                market=market,
                environment=environment
            )
            logger.info(f"  ✓ {market.upper()} adapter ready")
            logger.info(f"    Endpoint: {adapter.ENDPOINTS[market][environment]}")

        except Exception as e:
            logger.error(f"  ✗ Failed to initialize {market}: {e}")


# ============================================================================
# Example: Error Handling
# ============================================================================

def example_error_handling() -> None:
    """Demonstrate comprehensive error handling."""
    logger.info("\n" + "=" * 70)
    logger.info("EXAMPLE 9: Error Handling")
    logger.info("=" * 70)

    adapter = TransUnionAdapter(
        auth_type="api_key",
        api_key="invalid_key",
        market="ke",
        environment="sandbox"
    )

    adapter.on("error", on_error)

    # Test various error scenarios
    logger.info("\nTesting validation errors...")

    try:
        adapter.get_credit_report(
            id_type="national_id",
            id_number="",  # Empty ID - validation error
            first_name="John",
            last_name="Doe"
        )
    except ValidationError as e:
        logger.info(f"  ✓ Caught validation error: {e}")

    logger.info("\nTesting connection errors...")

    try:
        adapter.connect()  # Will fail with sandbox key
    except (AuthenticationError, ConnectionError) as e:
        logger.info(f"  ✓ Caught authentication/connection error: {e}")


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    """Run all examples."""
    logger.info("\n" + "#" * 70)
    logger.info("# TransUnion Adapter - Example Usage")
    logger.info("#" * 70)

    # Example 1: Basic connection
    adapter = example_basic_connection()

    if adapter is None:
        logger.error("Failed to connect. Check credentials and try again.")
        return

    try:
        # Example 2: Credit report
        report = example_credit_report(adapter)

        # Example 3: Credit score
        score = example_credit_score(adapter)

        # Example 4: ID verification
        verification = example_id_verification(adapter)

        # Example 5: Fraud check
        fraud = example_fraud_check(adapter)

        # Example 6: Loan performance
        submission = example_loan_performance(adapter)

        # Example 7: Health & stats
        example_health_check(adapter)

    finally:
        # Disconnect
        adapter.disconnect()

    # Example 8: Multi-market support
    example_different_markets()

    # Example 9: Error handling
    example_error_handling()

    logger.info("\n" + "#" * 70)
    logger.info("# Examples Completed")
    logger.info("#" * 70)


if __name__ == "__main__":
    args = parse_args()
    if args.debug:
        os.environ["IF_FINTECH_DEBUG_TRANSUNION"] = "1"

    main()
