"""
Airtel Money Adapter - Example Usage

Demonstrates common integration patterns for Airtel Money:
- Microfinance loan disbursement workflow
- Collection/repayment via USSD Push
- KYC verification for customer onboarding
- Balance management
- IF.bus event integration

Author: InfraFabric Finance Team
Version: 1.0.0
Date: 2025-12-04
"""

import os
import logging
import time
from typing import Dict, Any
from datetime import datetime

from airtel_money_adapter import (
    AirtelMoneyAdapter,
    CountryCode,
    TransactionStatus,
    AirtelMoneyError,
    AuthenticationError,
    APIError,
    ValidationError,
    InsufficientBalanceError,
)
from config import (
    AirtelMoneyConfig,
    get_country_config,
    validate_phone_number,
    validate_amount,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================================
# Example 1: Microfinance Loan Disbursement Workflow
# ============================================================================

def microfinance_loan_disbursement_workflow():
    """
    Complete microfinance loan disbursement workflow.

    Steps:
    1. Verify customer KYC
    2. Check lender balance
    3. Disburse loan to borrower
    4. Monitor transaction status
    5. Send confirmation
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Microfinance Loan Disbursement Workflow")
    print("=" * 80 + "\n")

    # Initialize adapter
    adapter = AirtelMoneyAdapter(
        client_id=os.getenv("AIRTEL_CLIENT_ID", "demo-client-id"),
        client_secret=os.getenv("AIRTEL_CLIENT_SECRET", "demo-client-secret"),
        country=CountryCode.KENYA,
        environment="sandbox",
        pin=os.getenv("AIRTEL_PIN", "1234"),
    )

    # Loan details
    borrower_phone = "254712345678"
    loan_amount = 5000.00
    loan_reference = f"LOAN-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    try:
        # Step 1: Verify borrower KYC
        print(f"Step 1: Verifying KYC for {borrower_phone}...")
        kyc_info = adapter.kyc_inquiry(borrower_phone)

        if not kyc_info.is_verified:
            raise ValidationError(f"Customer {borrower_phone} is not verified")

        print(f"✓ KYC Verified: {kyc_info.full_name}")
        print(f"  - Phone: {kyc_info.msisdn}")
        print(f"  - ID: {kyc_info.id_number}")
        print(f"  - Grade: {kyc_info.grade}")

        # Step 2: Check lender balance
        print(f"\nStep 2: Checking lender balance...")
        balance_info = adapter.get_balance()

        print(f"✓ Current Balance: {balance_info['balance']} {balance_info['currency']}")

        if balance_info["balance"] < loan_amount:
            raise InsufficientBalanceError(
                f"Insufficient balance. Required: {loan_amount}, Available: {balance_info['balance']}"
            )

        # Step 3: Disburse loan
        print(f"\nStep 3: Disbursing loan of {loan_amount} KES to {borrower_phone}...")
        disbursement_result = adapter.transfer(
            amount=loan_amount,
            msisdn=borrower_phone,
            reference=loan_reference,
            description=f"Loan disbursement for {kyc_info.full_name}",
        )

        print(f"✓ Disbursement Initiated")
        print(f"  - Transaction ID: {disbursement_result['transaction_id']}")
        print(f"  - Reference: {disbursement_result['reference']}")
        print(f"  - Status: {disbursement_result['status']}")

        # Step 4: Monitor transaction status
        print(f"\nStep 4: Monitoring transaction status...")
        transaction_id = disbursement_result["transaction_id"]

        # Poll for status (in production, use callbacks)
        max_attempts = 5
        for attempt in range(max_attempts):
            time.sleep(2)  # Wait 2 seconds between checks

            status_result = adapter.get_disbursement_status(transaction_id)

            print(f"  - Attempt {attempt + 1}: Status = {status_result['status']}")

            if status_result["status"] == TransactionStatus.SUCCESS.value:
                print(f"✓ Disbursement Successful!")
                print(f"  - Airtel Reference: {status_result['airtel_reference']}")
                break
            elif status_result["status"] == TransactionStatus.FAILED.value:
                print(f"✗ Disbursement Failed: {status_result['status_message']}")
                break

        # Step 5: Send confirmation (IF.bus event)
        print(f"\nStep 5: Loan disbursement workflow completed")
        print(f"  - Borrower: {kyc_info.full_name} ({borrower_phone})")
        print(f"  - Amount: {loan_amount} KES")
        print(f"  - Reference: {loan_reference}")
        print(f"  - Status: {status_result['status']}")

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
    except InsufficientBalanceError as e:
        logger.error(f"Insufficient balance: {e}")
    except APIError as e:
        logger.error(f"API error: {e}")
    except AirtelMoneyError as e:
        logger.error(f"Airtel Money error: {e}")
    finally:
        adapter.close()


# ============================================================================
# Example 2: Loan Repayment via USSD Push
# ============================================================================

def loan_repayment_collection_workflow():
    """
    Loan repayment collection via USSD Push.

    Steps:
    1. Calculate repayment amount
    2. Initiate USSD Push collection
    3. Wait for customer approval
    4. Monitor transaction status
    5. Update loan account
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Loan Repayment Collection Workflow")
    print("=" * 80 + "\n")

    # Initialize adapter
    adapter = AirtelMoneyAdapter(
        client_id=os.getenv("AIRTEL_CLIENT_ID", "demo-client-id"),
        client_secret=os.getenv("AIRTEL_CLIENT_SECRET", "demo-client-secret"),
        country=CountryCode.KENYA,
        environment="sandbox",
    )

    # Repayment details
    borrower_phone = "254712345678"
    repayment_amount = 5500.00  # Principal + interest
    repayment_reference = f"REPAY-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    try:
        # Step 1: Calculate repayment
        print(f"Step 1: Repayment calculation...")
        principal = 5000.00
        interest = 500.00
        total_repayment = principal + interest

        print(f"  - Principal: {principal} KES")
        print(f"  - Interest: {interest} KES")
        print(f"  - Total: {total_repayment} KES")

        # Step 2: Initiate USSD Push
        print(f"\nStep 2: Initiating USSD Push collection from {borrower_phone}...")
        collection_result = adapter.ussd_push(
            amount=repayment_amount,
            msisdn=borrower_phone,
            reference=repayment_reference,
            description=f"Loan repayment - Principal: {principal}, Interest: {interest}",
        )

        print(f"✓ USSD Push Sent")
        print(f"  - Transaction ID: {collection_result['transaction_id']}")
        print(f"  - Reference: {collection_result['reference']}")
        print(f"  - Customer will receive prompt on their phone")

        # Step 3: Wait for customer approval
        print(f"\nStep 3: Waiting for customer approval...")
        print(f"  - Customer must enter PIN on their phone to approve payment")

        # Step 4: Monitor transaction status
        print(f"\nStep 4: Monitoring transaction status...")
        transaction_id = collection_result["transaction_id"]

        # Poll for status (in production, use callbacks)
        max_attempts = 10
        for attempt in range(max_attempts):
            time.sleep(3)  # Wait 3 seconds between checks

            status_result = adapter.get_collection_status(transaction_id)

            print(f"  - Attempt {attempt + 1}: Status = {status_result['status']}")

            if status_result["status"] == TransactionStatus.SUCCESS.value:
                print(f"✓ Payment Received!")
                print(f"  - Amount: {status_result['amount']} {status_result['currency']}")
                print(f"  - Airtel Reference: {status_result['airtel_reference']}")
                break
            elif status_result["status"] == TransactionStatus.FAILED.value:
                print(f"✗ Payment Failed: {status_result['status_message']}")
                break

        # Step 5: Update loan account
        if status_result["status"] == TransactionStatus.SUCCESS.value:
            print(f"\nStep 5: Updating loan account...")
            print(f"  - Loan marked as PAID")
            print(f"  - Principal repaid: {principal} KES")
            print(f"  - Interest received: {interest} KES")
        else:
            print(f"\nStep 5: Payment not received - loan remains outstanding")

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
    except APIError as e:
        logger.error(f"API error: {e}")
    except AirtelMoneyError as e:
        logger.error(f"Airtel Money error: {e}")
    finally:
        adapter.close()


# ============================================================================
# Example 3: Bulk Customer KYC Verification
# ============================================================================

def bulk_kyc_verification():
    """
    Bulk KYC verification for customer onboarding.

    Verifies multiple customers and generates report.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Bulk Customer KYC Verification")
    print("=" * 80 + "\n")

    # Initialize adapter
    adapter = AirtelMoneyAdapter(
        client_id=os.getenv("AIRTEL_CLIENT_ID", "demo-client-id"),
        client_secret=os.getenv("AIRTEL_CLIENT_SECRET", "demo-client-secret"),
        country=CountryCode.KENYA,
        environment="sandbox",
    )

    # Customer list
    customers = [
        {"name": "John Doe", "phone": "254712345678"},
        {"name": "Jane Smith", "phone": "254723456789"},
        {"name": "Bob Johnson", "phone": "254734567890"},
        {"name": "Alice Williams", "phone": "254745678901"},
        {"name": "Charlie Brown", "phone": "254756789012"},
    ]

    verified_customers = []
    unverified_customers = []

    try:
        print(f"Verifying {len(customers)} customers...\n")

        for customer in customers:
            phone = customer["phone"]
            name = customer["name"]

            try:
                # Verify KYC
                kyc_info = adapter.kyc_inquiry(phone)

                if kyc_info.is_verified:
                    verified_customers.append({
                        "name": name,
                        "phone": phone,
                        "kyc_name": kyc_info.full_name,
                        "id_number": kyc_info.id_number,
                        "grade": kyc_info.grade,
                    })
                    print(f"✓ VERIFIED: {name} ({phone})")
                    print(f"  - KYC Name: {kyc_info.full_name}")
                    print(f"  - ID: {kyc_info.id_number}")
                    print(f"  - Grade: {kyc_info.grade}\n")
                else:
                    unverified_customers.append({"name": name, "phone": phone})
                    print(f"✗ NOT VERIFIED: {name} ({phone})\n")

                # Rate limiting
                time.sleep(1)

            except APIError as e:
                unverified_customers.append({"name": name, "phone": phone})
                print(f"✗ ERROR: {name} ({phone}) - {e}\n")

        # Summary report
        print("=" * 80)
        print("KYC VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Total Customers: {len(customers)}")
        print(f"Verified: {len(verified_customers)}")
        print(f"Unverified/Errors: {len(unverified_customers)}")
        print(f"Verification Rate: {len(verified_customers)/len(customers)*100:.1f}%")

        # Verified customers
        if verified_customers:
            print(f"\nVerified Customers ({len(verified_customers)}):")
            for customer in verified_customers:
                print(f"  - {customer['kyc_name']} ({customer['phone']}) - Grade: {customer['grade']}")

        # Unverified customers
        if unverified_customers:
            print(f"\nUnverified Customers ({len(unverified_customers)}):")
            for customer in unverified_customers:
                print(f"  - {customer['name']} ({customer['phone']})")

    except AirtelMoneyError as e:
        logger.error(f"Airtel Money error: {e}")
    finally:
        adapter.close()


# ============================================================================
# Example 4: Context Manager Usage
# ============================================================================

def context_manager_example():
    """
    Demonstrate context manager usage for automatic cleanup.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Context Manager Usage")
    print("=" * 80 + "\n")

    # Use adapter as context manager
    with AirtelMoneyAdapter(
        client_id=os.getenv("AIRTEL_CLIENT_ID", "demo-client-id"),
        client_secret=os.getenv("AIRTEL_CLIENT_SECRET", "demo-client-secret"),
        country=CountryCode.UGANDA,
        environment="sandbox",
    ) as adapter:
        try:
            # Check balance
            print("Checking balance...")
            balance = adapter.get_balance()
            print(f"Balance: {balance['balance']} {balance['currency']}")

            # Perform KYC
            print("\nPerforming KYC inquiry...")
            kyc = adapter.kyc_inquiry("256700123456")
            print(f"Customer: {kyc.full_name}")
            print(f"Verified: {kyc.is_verified}")

        except AirtelMoneyError as e:
            logger.error(f"Error: {e}")

    # Adapter automatically closed after context manager


# ============================================================================
# Example 5: Error Handling Best Practices
# ============================================================================

def error_handling_example():
    """
    Demonstrate comprehensive error handling.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Error Handling Best Practices")
    print("=" * 80 + "\n")

    adapter = AirtelMoneyAdapter(
        client_id=os.getenv("AIRTEL_CLIENT_ID", "demo-client-id"),
        client_secret=os.getenv("AIRTEL_CLIENT_SECRET", "demo-client-secret"),
        country=CountryCode.KENYA,
        environment="sandbox",
        pin="1234",
    )

    try:
        # Example 1: Validation error
        print("Test 1: Invalid amount...")
        try:
            adapter.transfer(
                amount=-100.00,  # Invalid: negative amount
                msisdn="254712345678",
                reference="TEST-001",
            )
        except ValidationError as e:
            print(f"✓ Caught ValidationError: {e}\n")

        # Example 2: Authentication error
        print("Test 2: Invalid credentials...")
        try:
            bad_adapter = AirtelMoneyAdapter(
                client_id="invalid-client-id",
                client_secret="invalid-client-secret",
                country=CountryCode.KENYA,
                environment="sandbox",
            )
            bad_adapter.get_balance()
        except AuthenticationError as e:
            print(f"✓ Caught AuthenticationError: {e}\n")

        # Example 3: Insufficient balance
        print("Test 3: Insufficient balance...")
        try:
            adapter.transfer(
                amount=999999999.00,  # Very large amount
                msisdn="254712345678",
                reference="TEST-002",
            )
        except InsufficientBalanceError as e:
            print(f"✓ Caught InsufficientBalanceError: {e}\n")

        # Example 4: API error
        print("Test 4: API error handling...")
        try:
            adapter.get_collection_status("INVALID-TRANSACTION-ID")
        except APIError as e:
            print(f"✓ Caught APIError: {e}\n")

        print("All error handling tests completed successfully!")

    except AirtelMoneyError as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        adapter.close()


# ============================================================================
# Example 6: IF.bus Event Integration
# ============================================================================

def ifbus_event_integration_example():
    """
    Demonstrate IF.bus event integration.

    Shows how to capture and process IF.bus events emitted by the adapter.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 6: IF.bus Event Integration")
    print("=" * 80 + "\n")

    # Custom event handler
    class EventLogger:
        """Simple event logger for demonstration."""

        def __init__(self):
            self.events = []

        def handle_event(self, event_name: str, data: Dict[str, Any]):
            """Handle IF.bus event."""
            self.events.append({
                "event": event_name,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data,
            })
            print(f"[EVENT] {event_name}")
            print(f"  Data: {data}\n")

    event_logger = EventLogger()

    # Initialize adapter
    adapter = AirtelMoneyAdapter(
        client_id=os.getenv("AIRTEL_CLIENT_ID", "demo-client-id"),
        client_secret=os.getenv("AIRTEL_CLIENT_SECRET", "demo-client-secret"),
        country=CountryCode.KENYA,
        environment="sandbox",
    )

    try:
        print("Performing operations with IF.bus event tracking...\n")

        # Operation 1: Get balance (emits airtel.account.balance_checked)
        print("1. Checking balance...")
        adapter.get_balance()

        # Operation 2: KYC inquiry (emits airtel.kyc.verified)
        print("2. Performing KYC...")
        adapter.kyc_inquiry("254712345678")

        # Operation 3: USSD Push (emits airtel.collection.initiated, airtel.collection.success)
        print("3. Initiating USSD Push...")
        adapter.ussd_push(
            amount=1000.00,
            msisdn="254712345678",
            reference="EVENT-TEST-001",
            description="Test payment",
        )

        print(f"\nTotal events captured: {len(event_logger.events)}")
        print("\nEvent Summary:")
        for event in event_logger.events:
            print(f"  - {event['event']} at {event['timestamp']}")

    except AirtelMoneyError as e:
        logger.error(f"Error: {e}")
    finally:
        adapter.close()


# ============================================================================
# Example 7: Multi-Country Operations
# ============================================================================

def multi_country_example():
    """
    Demonstrate operations across multiple countries.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Multi-Country Operations")
    print("=" * 80 + "\n")

    countries = [
        (CountryCode.KENYA, "254712345678"),
        (CountryCode.UGANDA, "256700123456"),
        (CountryCode.TANZANIA, "255712345678"),
    ]

    for country, phone in countries:
        print(f"\nCountry: {country.value}")
        print("-" * 40)

        try:
            with AirtelMoneyAdapter(
                client_id=os.getenv("AIRTEL_CLIENT_ID", "demo-client-id"),
                client_secret=os.getenv("AIRTEL_CLIENT_SECRET", "demo-client-secret"),
                country=country,
                environment="sandbox",
            ) as adapter:
                # Get country config
                country_config = get_country_config(country.value)
                print(f"Currency: {country_config.currency}")
                print(f"Phone prefix: +{country_config.phone_prefix}")

                # Check balance
                balance = adapter.get_balance()
                print(f"Balance: {balance['balance']} {balance['currency']}")

        except AirtelMoneyError as e:
            logger.error(f"Error for {country.value}: {e}")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run all examples."""
    print("\n")
    print("*" * 80)
    print("AIRTEL MONEY API ADAPTER - EXAMPLE USAGE")
    print("*" * 80)

    # Check for credentials
    if not os.getenv("AIRTEL_CLIENT_ID") or not os.getenv("AIRTEL_CLIENT_SECRET"):
        print("\n⚠ WARNING: AIRTEL_CLIENT_ID and AIRTEL_CLIENT_SECRET not set")
        print("Set environment variables to run examples with real API")
        print("\nExamples will run with demo credentials (may fail)\n")

    # Run examples
    examples = [
        ("Microfinance Loan Disbursement", microfinance_loan_disbursement_workflow),
        ("Loan Repayment Collection", loan_repayment_collection_workflow),
        ("Bulk KYC Verification", bulk_kyc_verification),
        ("Context Manager Usage", context_manager_example),
        ("Error Handling", error_handling_example),
        ("IF.bus Event Integration", ifbus_event_integration_example),
        ("Multi-Country Operations", multi_country_example),
    ]

    for i, (name, func) in enumerate(examples, 1):
        try:
            func()
        except Exception as e:
            logger.error(f"Example {i} ({name}) failed: {e}")

        # Pause between examples
        if i < len(examples):
            print("\n" + "." * 80)
            print("Press Enter to continue to next example...")
            # input()  # Uncomment to require user input between examples

    print("\n")
    print("*" * 80)
    print("ALL EXAMPLES COMPLETED")
    print("*" * 80)
    print("\n")


if __name__ == "__main__":
    main()
