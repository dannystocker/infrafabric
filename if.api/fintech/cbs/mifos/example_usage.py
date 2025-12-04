"""
Apache Fineract/Mifos API Adapter - Complete Usage Examples

This file demonstrates all major features of the Mifos adapter:
- Client lifecycle management
- Loan application and disbursement
- Loan repayments
- Savings accounts
- Group lending models
- IF.bus event integration

Run these examples in a live Fineract environment.
"""

import os
import logging
from datetime import datetime, timedelta
from mifos_adapter import (
    MifosAdapter,
    ClientData,
    LoanApplicationData,
    RepaymentData,
    SavingsAccountData,
    GroupData,
    GroupType,
    PaginationParams,
    MifosEnvironment,
    EventEmitter,
    MifosEvent,
)

# ============================================================================
# Configure Logging
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Custom Event Emitter (Optional)
# ============================================================================

class ConsoleEventEmitter(EventEmitter):
    """Simple event emitter that logs to console."""

    def emit(self, event: MifosEvent) -> None:
        """Log event to console."""
        logger.info(f"EVENT: {event.event_type} | {event.entity_type}:{event.entity_id}")
        logger.info(f"  Status: {event.status}")
        logger.info(f"  Data: {event.data}")


# ============================================================================
# Example 1: Basic Connection
# ============================================================================

def example_01_connection():
    """Verify connection to Fineract server."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Verify Connection to Fineract")
    print("="*70)

    adapter = MifosAdapter(
        base_url=os.getenv("FINERACT_URL", "http://localhost:8080/fineract-provider"),
        username=os.getenv("FINERACT_USERNAME", "mifos"),
        password=os.getenv("FINERACT_PASSWORD", "password"),
        timeout=30,
        verify_ssl=False,
        environment=MifosEnvironment.DEVELOPMENT
    )

    try:
        if adapter.verify_connection():
            print("✓ Connection successful!")

            # Get server info
            info = adapter.get_server_info()
            print(f"  Server: {info.get('name')}")
            print(f"  Version: {info.get('version')}")

    except Exception as e:
        print(f"✗ Connection failed: {e}")
    finally:
        adapter.close()


# ============================================================================
# Example 2: Client Management
# ============================================================================

def example_02_client_management():
    """Create, search, and manage clients."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Client Management")
    print("="*70)

    emitter = ConsoleEventEmitter()
    adapter = MifosAdapter(
        base_url=os.getenv("FINERACT_URL", "http://localhost:8080/fineract-provider"),
        username=os.getenv("FINERACT_USERNAME", "mifos"),
        password=os.getenv("FINERACT_PASSWORD", "password"),
        event_emitter=emitter
    )

    with adapter:
        # Create new client
        print("\n1. Creating new client...")
        client = ClientData(
            first_name="Alice",
            last_name="Kipchoge",
            external_id=f"EXT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            email="alice@example.com",
            phone_number="+254712345678",
            date_of_birth="1995-03-20",
            gender="f",
            national_id="KE987654321"
        )

        result = adapter.create_client(client)
        client_id = result["client_id"]
        print(f"✓ Client created: {client_id}")

        # Activate client
        print("\n2. Activating client...")
        adapter.activate_client(client_id)
        print(f"✓ Client {client_id} activated")

        # Search clients
        print("\n3. Searching clients...")
        search_results = adapter.search_clients(
            search_term="Alice",
            pagination=PaginationParams(limit=10)
        )
        print(f"✓ Found {search_results['totalFilteredRecords']} clients")
        for c in search_results["pageItems"][:3]:
            print(f"  - {c['id']}: {c['displayName']}")

        # Get client details
        print("\n4. Retrieving client details...")
        client_details = adapter.get_client(client_id)
        print(f"✓ Client details retrieved")
        print(f"  Name: {client_details['displayName']}")
        print(f"  Status: {client_details['status']['value']}")
        print(f"  Activation Date: {client_details.get('activationDate')}")

        # Update client
        print("\n5. Updating client information...")
        updated_client = ClientData(
            first_name="Alice",
            last_name="Kipchoge",
            email="alice.kipchoge@example.com",
            phone_number="+254712345679"
        )
        adapter.update_client(client_id, updated_client)
        print(f"✓ Client {client_id} updated")

        return client_id


# ============================================================================
# Example 3: Loan Products and Submission
# ============================================================================

def example_03_loan_management(client_id: int):
    """Query loan products and submit application."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Loan Products and Application")
    print("="*70)

    emitter = ConsoleEventEmitter()
    adapter = MifosAdapter(
        base_url=os.getenv("FINERACT_URL", "http://localhost:8080/fineract-provider"),
        username=os.getenv("FINERACT_USERNAME", "mifos"),
        password=os.getenv("FINERACT_PASSWORD", "password"),
        event_emitter=emitter
    )

    with adapter:
        # Get loan products
        print("\n1. Retrieving available loan products...")
        products = adapter.get_loan_products(
            pagination=PaginationParams(limit=10)
        )
        print(f"✓ Found {products['totalFilteredRecords']} loan products")

        if not products["pageItems"]:
            print("  No products available. Create one in Fineract UI first.")
            return

        product_id = products["pageItems"][0]["id"]
        product = products["pageItems"][0]
        print(f"  Using product: {product['id']} - {product['name']}")
        print(f"    Interest Rate: {product.get('interestRatePerPeriod')}%")
        print(f"    Frequency: {product.get('repaymentFrequency')}")

        # Submit loan application
        print("\n2. Submitting loan application...")
        loan = LoanApplicationData(
            client_id=client_id,
            product_id=product_id,
            principal_amount=50000.0,
            number_of_repayments=24,
            repayment_every=1,
            repayment_frequency_id=2,  # Monthly
            interest_rate_per_period=2.5,
            submission_on_date=datetime.utcnow().strftime("%Y-%m-%d"),
            expected_disbursement_date=(datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
            external_id=f"LOAN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        )

        submission_result = adapter.submit_loan_application(loan)
        loan_id = submission_result["loan_id"]
        print(f"✓ Loan application submitted: {loan_id}")

        # Approve loan
        print("\n3. Approving loan...")
        adapter.approve_loan(
            loan_id=loan_id,
            approval_date=datetime.utcnow().strftime("%Y-%m-%d"),
            approval_amount=50000.0
        )
        print(f"✓ Loan {loan_id} approved")

        # Disburse loan
        print("\n4. Disbursing loan...")
        adapter.disburse_loan(
            loan_id=loan_id,
            disbursal_date=(datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
            disbursal_amount=50000.0
        )
        print(f"✓ Loan {loan_id} disbursed")

        # Get loan details
        print("\n5. Retrieving loan details...")
        loan_details = adapter.get_loan(loan_id)
        print(f"✓ Loan details retrieved")
        print(f"  Status: {loan_details.get('status', 'Unknown')}")
        print(f"  Principal: {loan_details.get('principal')}")
        print(f"  Outstanding Balance: {loan_details.get('summary', {}).get('principalOutstanding')}")

        # Get repayment schedule
        print("\n6. Retrieving repayment schedule...")
        schedule = adapter.get_loan_schedule(loan_id)
        if schedule.get("periods"):
            print(f"✓ Schedule retrieved ({len(schedule['periods'])} periods)")
            for i, period in enumerate(schedule["periods"][:3]):
                print(f"  Period {period.get('period')}: "
                      f"Due {period.get('dueDate')} - "
                      f"Amount: {period.get('totalDueForPeriod')}")
        else:
            print("  No schedule periods available")

        return loan_id


# ============================================================================
# Example 4: Loan Repayments
# ============================================================================

def example_04_loan_repayment(loan_id: int):
    """Post loan repayments."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Loan Repayment")
    print("="*70)

    emitter = ConsoleEventEmitter()
    adapter = MifosAdapter(
        base_url=os.getenv("FINERACT_URL", "http://localhost:8080/fineract-provider"),
        username=os.getenv("FINERACT_USERNAME", "mifos"),
        password=os.getenv("FINERACT_PASSWORD", "password"),
        event_emitter=emitter
    )

    with adapter:
        print("\n1. Posting loan repayment...")
        repayment = RepaymentData(
            loan_id=loan_id,
            transaction_date=datetime.utcnow().strftime("%Y-%m-%d"),
            amount=5000.0,
            payment_type_id=1,
            receipt_number=f"RCP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        )

        try:
            result = adapter.post_loan_repayment(repayment)
            print(f"✓ Repayment posted successfully")
            print(f"  Transaction ID: {result.get('resourceId')}")
        except Exception as e:
            print(f"✗ Repayment failed: {e}")


# ============================================================================
# Example 5: Savings Accounts
# ============================================================================

def example_05_savings_accounts(client_id: int):
    """Create and manage savings accounts."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Savings Accounts")
    print("="*70)

    emitter = ConsoleEventEmitter()
    adapter = MifosAdapter(
        base_url=os.getenv("FINERACT_URL", "http://localhost:8080/fineract-provider"),
        username=os.getenv("FINERACT_USERNAME", "mifos"),
        password=os.getenv("FINERACT_PASSWORD", "password"),
        event_emitter=emitter
    )

    with adapter:
        # Get savings products
        print("\n1. Retrieving savings products...")
        products = adapter.get_loan_products(pagination=PaginationParams(limit=10))

        if not products["pageItems"]:
            print("  No savings products available")
            return

        product_id = products["pageItems"][0]["id"]

        # Create savings account
        print("\n2. Creating savings account...")
        savings = SavingsAccountData(
            client_id=client_id,
            product_id=product_id,
            nominal_annual_interest_rate=2.5,
            submission_on_date=datetime.utcnow().strftime("%Y-%m-%d"),
            external_id=f"SAV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        )

        try:
            result = adapter.create_savings_account(savings)
            account_id = result["savings_account_id"]
            print(f"✓ Savings account created: {account_id}")

            # Activate savings account
            print("\n3. Activating savings account...")
            adapter.activate_savings_account(
                account_id=account_id,
                activation_date=datetime.utcnow().strftime("%Y-%m-%d")
            )
            print(f"✓ Savings account {account_id} activated")

            # Get account details
            print("\n4. Retrieving account details...")
            account = adapter.get_savings_account(account_id)
            print(f"✓ Account details retrieved")
            print(f"  Account Number: {account.get('accountNumber')}")
            print(f"  Status: {account.get('status')}")

        except Exception as e:
            print(f"✗ Savings operation failed: {e}")


# ============================================================================
# Example 6: Group Lending
# ============================================================================

def example_06_group_lending():
    """Create and manage groups for group lending model."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Group Lending (Centers & Groups)")
    print("="*70)

    emitter = ConsoleEventEmitter()
    adapter = MifosAdapter(
        base_url=os.getenv("FINERACT_URL", "http://localhost:8080/fineract-provider"),
        username=os.getenv("FINERACT_USERNAME", "mifos"),
        password=os.getenv("FINERACT_PASSWORD", "password"),
        event_emitter=emitter
    )

    with adapter:
        # Create center
        print("\n1. Creating center...")
        center = GroupData(
            group_name=f"Nairobi Center {datetime.utcnow().strftime('%H%M%S')}",
            office_id=1,
            group_type=GroupType.CENTER,
            activation_date=datetime.utcnow().strftime("%Y-%m-%d"),
            external_id=f"CTR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        )

        try:
            center_result = adapter.create_group(center)
            center_id = center_result["group_id"]
            print(f"✓ Center created: {center_id}")

            # Create group
            print("\n2. Creating group...")
            group = GroupData(
                group_name=f"Jamii Group {datetime.utcnow().strftime('%H%M%S')}",
                office_id=1,
                center_id=center_id,
                group_type=GroupType.SELF_HELP_GROUP,
                activation_date=datetime.utcnow().strftime("%Y-%m-%d"),
                external_id=f"GRP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            )

            group_result = adapter.create_group(group)
            group_id = group_result["group_id"]
            print(f"✓ Group created: {group_id}")

            # Get group details
            print("\n3. Retrieving group details...")
            group_details = adapter.get_group(group_id)
            print(f"✓ Group details retrieved")
            print(f"  Name: {group_details.get('name')}")
            print(f"  Status: {group_details.get('status')}")

        except Exception as e:
            print(f"✗ Group operation failed: {e}")


# ============================================================================
# Main - Run All Examples
# ============================================================================

def main():
    """Run all examples in sequence."""
    print("\n" + "="*70)
    print("APACHE FINERACT/MIFOS API ADAPTER - COMPLETE EXAMPLES")
    print("="*70)

    try:
        # Test connection first
        example_01_connection()

        # Client management
        client_id = example_02_client_management()

        # Loan management
        if client_id:
            loan_id = example_03_loan_management(client_id)

            # Loan repayment
            if loan_id:
                example_04_loan_repayment(loan_id)

            # Savings accounts
            example_05_savings_accounts(client_id)

        # Group lending
        example_06_group_lending()

        print("\n" + "="*70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*70)

    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)


if __name__ == "__main__":
    main()
