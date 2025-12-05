"""
M-Pesa Adapter Examples

Practical examples demonstrating common use cases and patterns for the M-Pesa adapter.

CLI flags:
    -d, -v, --debug, --verbose  Enable fintech debug logging for M-Pesa
    -h, --help                  Show this help message
"""

import argparse
import logging
import os
import time
from typing import Optional

from mpesa_adapter import (
    MpesaAdapter,
    MpesaEventEmitter,
    Environment,
    MpesaException,
    MpesaAuthException,
    MpesaAPIException,
    create_mpesa_adapter
)

from config import (
    MpesaConfig,
    PhoneNumberValidator,
    AmountValidator,
    EventNameConstants,
    ResultCodes
)


# Configure logging for examples
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IFBusEventEmitter(MpesaEventEmitter):
    """Custom event emitter that logs events (placeholder for real IF.bus)."""

    def emit(self, event_name: str, data: dict) -> None:
        """
        Emit event to IF.bus.

        In production, this would integrate with the actual IF.bus infrastructure.

        Args:
            event_name: Name of the event
            data: Event data payload
        """
        logger.info(f"[IF.bus Event] {event_name}")
        logger.debug(f"  Data: {data}")

        # TODO: Integrate with actual IF.bus
        # Example:
        # from if.bus import Bus
        # bus = Bus()
        # bus.emit(event_name, data)


# ============================================================================
# Example 1: Basic STK Push Payment Collection
# ============================================================================

def example_1_basic_stk_push():
    """
    Simple example of collecting payment via STK Push.

    This is the most common use case - initiating a payment prompt on customer's phone.
    """
    logger.info("=" * 60)
    logger.info("Example 1: Basic STK Push Payment Collection")
    logger.info("=" * 60)

    try:
        # Initialize adapter
        adapter = MpesaAdapter(
            consumer_key="YOUR_CONSUMER_KEY",
            consumer_secret="YOUR_CONSUMER_SECRET",
            business_shortcode="174379",
            passkey="bfb279f9aa9bdbcf158e97dd1a503b6055c2f8e3c36a6e0c",
            environment=Environment.SANDBOX,
            event_emitter=IFBusEventEmitter()
        )

        logger.info("Adapter initialized successfully")

        # Initiate STK Push
        result = adapter.initiate_stk_push(
            phone_number="254712345678",
            amount=100.00,
            account_reference="INVOICE_001",
            transaction_desc="Payment for Order #12345"
        )

        logger.info(f"STK Push initiated successfully")
        logger.info(f"Merchant Request ID: {result['MerchantRequestID']}")
        logger.info(f"Checkout Request ID: {result['CheckoutRequestID']}")

        # Store checkout ID for later status queries
        checkout_id = result['CheckoutRequestID']

        # Wait a bit for user to complete payment (5 seconds in sandbox)
        logger.info("Waiting for customer to enter PIN...")
        time.sleep(5)

        # Query status
        status = adapter.query_stk_push_status(checkout_id)
        logger.info(f"Transaction Status: {status.get('ResultDescription')}")
        logger.info(f"Result Code: {status.get('ResultCode')}")

        adapter.close()

    except MpesaAuthException as e:
        logger.error(f"Authentication failed: {e}")
    except MpesaAPIException as e:
        logger.error(f"API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


# ============================================================================
# Example 2: B2C Payment (Disbursement)
# ============================================================================

def example_2_b2c_disbursement():
    """
    Send money to customer via B2C endpoint.

    Use cases:
    - Salary payments
    - Refunds
    - Promotional payments
    - Cash withdrawal
    """
    logger.info("=" * 60)
    logger.info("Example 2: B2C Disbursement")
    logger.info("=" * 60)

    try:
        adapter = create_mpesa_adapter(environment="sandbox")

        # Salary payment
        result = adapter.b2c_payment(
            phone_number="254712345678",
            amount=5000.00,
            command_id="SalaryPayment",
            remarks="Monthly Salary - December 2024",
            occasion="December 2024"
        )

        logger.info("B2C Payment initiated successfully")
        logger.info(f"Conversation ID: {result['ConversationID']}")
        logger.info(f"Originator Conversation ID: {result['OriginatorConversationID']}")
        logger.info(f"Response: {result['ResponseDescription']}")

        adapter.close()

    except MpesaException as e:
        logger.error(f"Error: {e}")


# ============================================================================
# Example 3: Transaction Status Query
# ============================================================================

def example_3_transaction_status():
    """
    Query the status of a specific M-Pesa transaction.

    Useful for reconciliation and payment verification.
    """
    logger.info("=" * 60)
    logger.info("Example 3: Transaction Status Query")
    logger.info("=" * 60)

    try:
        adapter = create_mpesa_adapter(environment="sandbox")

        # Query transaction status
        status = adapter.query_transaction_status(
            transaction_id="LHG31AA5695"
        )

        result_code = status.get('ResultCode', '')
        result_description = status.get('ResultDescription', '')

        logger.info(f"Transaction Status Query Complete")
        logger.info(f"Result Code: {result_code}")
        logger.info(f"Description: {result_description}")

        if result_code == ResultCodes.SUCCESS:
            logger.info("Transaction successful!")
            if 'ResultParameters' in status:
                logger.info(f"Details: {status['ResultParameters']}")
        else:
            logger.info(f"Transaction failed: {ResultCodes.get_description(result_code)}")

        adapter.close()

    except MpesaException as e:
        logger.error(f"Error: {e}")


# ============================================================================
# Example 4: Account Balance Query
# ============================================================================

def example_4_account_balance():
    """
    Query business account balance.

    Note: Balance details are provided in async callback response.
    """
    logger.info("=" * 60)
    logger.info("Example 4: Account Balance Query")
    logger.info("=" * 60)

    try:
        adapter = create_mpesa_adapter(environment="sandbox")

        # Query balance
        result = adapter.get_account_balance()

        logger.info("Account balance query initiated")
        logger.info(f"Conversation ID: {result['ConversationID']}")
        logger.info(f"Response Code: {result['ResponseCode']}")
        logger.info("Balance details will be provided in callback response")

        adapter.close()

    except MpesaException as e:
        logger.error(f"Error: {e}")


# ============================================================================
# Example 5: Input Validation
# ============================================================================

def example_5_input_validation():
    """
    Demonstrate proper input validation before API calls.
    """
    logger.info("=" * 60)
    logger.info("Example 5: Input Validation")
    logger.info("=" * 60)

    # Phone number validation
    phone_numbers = [
        "254712345678",      # Valid
        "0712345678",        # Local format - needs conversion
        "+254712345678",     # With country code - needs conversion
        "712345678"          # Invalid
    ]

    logger.info("Phone Number Validation:")
    for phone in phone_numbers:
        try:
            cleaned = PhoneNumberValidator.clean(phone)
            logger.info(f"  {phone} -> {cleaned} (Valid)")
        except ValueError as e:
            logger.info(f"  {phone} -> Invalid: {e}")

    # Amount validation
    amounts = [
        100.0,      # Valid
        1.0,        # Minimum
        150000.0,   # Maximum
        0.5,        # Too small
        200000.0    # Too large
    ]

    logger.info("\nAmount Validation:")
    for amount in amounts:
        try:
            AmountValidator.validate_strict(amount)
            logger.info(f"  {amount} KES -> Valid")
        except ValueError as e:
            logger.info(f"  {amount} KES -> Invalid: {e}")


# ============================================================================
# Example 6: Error Handling
# ============================================================================

def example_6_error_handling():
    """
    Demonstrate comprehensive error handling patterns.
    """
    logger.info("=" * 60)
    logger.info("Example 6: Error Handling")
    logger.info("=" * 60)

    # Example 1: Missing credentials
    logger.info("Test 1: Missing credentials")
    try:
        adapter = MpesaAdapter(
            consumer_key="",  # Missing
            consumer_secret="secret",
            business_shortcode="123456",
            passkey="passkey"
        )
    except MpesaException as e:
        logger.info(f"  Caught: {e}")

    # Example 2: Invalid phone number
    logger.info("\nTest 2: Invalid phone number")
    try:
        adapter = create_mpesa_adapter(environment="sandbox")
        adapter.initiate_stk_push(
            phone_number="invalid",  # Will fail validation
            amount=100.0,
            account_reference="TEST"
        )
    except (ValueError, MpesaException) as e:
        logger.info(f"  Caught: {e}")

    # Example 3: Invalid amount
    logger.info("\nTest 3: Invalid amount")
    try:
        adapter = create_mpesa_adapter(environment="sandbox")
        adapter.initiate_stk_push(
            phone_number="254712345678",
            amount=0.5,  # Below minimum
            account_reference="TEST"
        )
    except (ValueError, MpesaException) as e:
        logger.info(f"  Caught: {e}")


# ============================================================================
# Example 7: Custom Event Handler
# ============================================================================

class CustomEventHandler(MpesaEventEmitter):
    """Custom event handler for tracking and logging."""

    def __init__(self):
        self.events = []

    def emit(self, event_name: str, data: dict) -> None:
        """Track all emitted events."""
        self.events.append({
            'event': event_name,
            'data': data,
            'timestamp': time.time()
        })
        logger.info(f"Event tracked: {event_name}")

    def get_events_by_type(self, event_type: str):
        """Get all events of a specific type."""
        return [e for e in self.events if e['event'].startswith(event_type)]

    def print_summary(self) -> None:
        """Print event summary."""
        logger.info("\nEvent Summary:")
        logger.info(f"Total events: {len(self.events)}")

        event_types = {}
        for event in self.events:
            event_name = event['event']
            event_types[event_name] = event_types.get(event_name, 0) + 1

        for event_name, count in event_types.items():
            logger.info(f"  {event_name}: {count}")


def example_7_custom_events():
    """
    Demonstrate custom event handling and tracking.
    """
    logger.info("=" * 60)
    logger.info("Example 7: Custom Event Handler")
    logger.info("=" * 60)

    # Create custom handler
    event_handler = CustomEventHandler()

    try:
        adapter = MpesaAdapter(
            consumer_key="YOUR_CONSUMER_KEY",
            consumer_secret="YOUR_CONSUMER_SECRET",
            business_shortcode="174379",
            passkey="bfb279f9aa9bdbcf158e97dd1a503b6055c2f8e3c36a6e0c",
            environment=Environment.SANDBOX,
            event_emitter=event_handler
        )

        # Get token (generates token_acquired event)
        token = adapter.get_access_token()
        logger.info(f"Got token: {token[:20]}...")

        # Print event summary
        event_handler.print_summary()

        adapter.close()

    except MpesaException as e:
        logger.error(f"Error: {e}")


# ============================================================================
# Example 8: Production Configuration
# ============================================================================

def example_8_production_setup():
    """
    Demonstrate production setup with configuration from environment.
    """
    logger.info("=" * 60)
    logger.info("Example 8: Production Configuration Setup")
    logger.info("=" * 60)

    logger.info("Expected environment variables:")
    logger.info("  MPESA_CONSUMER_KEY")
    logger.info("  MPESA_CONSUMER_SECRET")
    logger.info("  MPESA_BUSINESS_SHORTCODE")
    logger.info("  MPESA_PASSKEY")
    logger.info("  MPESA_ENVIRONMENT (optional, default: sandbox)")

    try:
        # Load config from environment
        config = MpesaConfig.from_env()
        config.validate()
        logger.info("Configuration validated successfully")

        # Create adapter with custom event emitter
        adapter = MpesaAdapter(
            consumer_key=config.consumer_key,
            consumer_secret=config.consumer_secret,
            business_shortcode=config.business_shortcode,
            passkey=config.passkey,
            environment=config.environment,
            timeout=config.timeout,
            max_retries=config.max_retries,
            event_emitter=IFBusEventEmitter()
        )

        logger.info(f"Production adapter initialized for {config.environment.value}")
        adapter.close()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
    except MpesaException as e:
        logger.error(f"Adapter error: {e}")


# ============================================================================
# Example 9: Retry and Timeout Configuration
# ============================================================================

def example_9_retry_configuration():
    """
    Demonstrate retry and timeout configurations.
    """
    logger.info("=" * 60)
    logger.info("Example 9: Retry and Timeout Configuration")
    logger.info("=" * 60)

    # Configuration 1: Aggressive retries
    logger.info("Configuration 1: Aggressive retries (5 attempts, 60s timeout)")
    adapter1 = MpesaAdapter(
        consumer_key="key",
        consumer_secret="secret",
        business_shortcode="123456",
        passkey="passkey",
        max_retries=5,
        timeout=60
    )
    logger.info(f"  Max retries: {adapter1.max_retries}")
    logger.info(f"  Timeout: {adapter1.timeout}s")
    adapter1.close()

    # Configuration 2: Conservative retries
    logger.info("\nConfiguration 2: Conservative retries (1 attempt, 15s timeout)")
    adapter2 = MpesaAdapter(
        consumer_key="key",
        consumer_secret="secret",
        business_shortcode="123456",
        passkey="passkey",
        max_retries=1,
        timeout=15
    )
    logger.info(f"  Max retries: {adapter2.max_retries}")
    logger.info(f"  Timeout: {adapter2.timeout}s")
    adapter2.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="M-Pesa adapter example suite for InfraFabric."
    )
    parser.add_argument(
        "-d",
        "-v",
        "--debug",
        "--verbose",
        dest="debug",
        action="store_true",
        help="Enable fintech debug logging for M-Pesa (sets IF_FINTECH_DEBUG_MPESA=1).",
    )
    return parser.parse_args()


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    args = parse_args()
    if args.debug:
        os.environ["IF_FINTECH_DEBUG_MPESA"] = "1"

    """Run all examples."""
    examples = [
        ("1", "Basic STK Push", example_1_basic_stk_push),
        ("2", "B2C Disbursement", example_2_b2c_disbursement),
        ("3", "Transaction Status", example_3_transaction_status),
        ("4", "Account Balance", example_4_account_balance),
        ("5", "Input Validation", example_5_input_validation),
        ("6", "Error Handling", example_6_error_handling),
        ("7", "Custom Events", example_7_custom_events),
        ("8", "Production Setup", example_8_production_setup),
        ("9", "Retry Configuration", example_9_retry_configuration),
    ]

    print("\nM-Pesa Adapter Examples")
    print("=" * 60)
    print("Available examples:")
    for num, name, _ in examples:
        print(f"  {num}. {name}")
    print("  all - Run all examples")
    print("=" * 60)

    choice = input("Select example to run (1-9, all, or q to quit): ").strip().lower()

    if choice == "q":
        print("Exiting...")
    elif choice == "all":
        for num, name, func in examples:
            try:
                print(f"\n\nRunning Example {num}...\n")
                func()
            except Exception as e:
                logger.error(f"Error in example {num}: {e}", exc_info=True)
    else:
        for num, name, func in examples:
            if num == choice:
                try:
                    func()
                except Exception as e:
                    logger.error(f"Error: {e}", exc_info=True)
                break
        else:
            print("Invalid selection")
