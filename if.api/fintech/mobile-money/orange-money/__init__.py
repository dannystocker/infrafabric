"""
Orange Money API Adapter

Production-ready adapter for Orange Money APIs across Francophone Africa.
Provides seamless integration for collections, disbursements, and merchant payments.

Quick Start:
    from orange_money_adapter import OrangeMoneyAdapter, CountryCode

    adapter = OrangeMoneyAdapter(
        client_id="your-client-id",
        client_secret="your-client-secret",
        merchant_key="your-merchant-key",
        country=CountryCode.SENEGAL,
        environment="production"
    )

    # Disburse loan
    result = adapter.transfer(
        amount=50000.0,
        recipient_msisdn="221771234567",
        reference="LOAN-001",
        description="Loan disbursement"
    )

Author: InfraFabric Finance Team
Version: 1.0.0
"""

from .orange_money_adapter import (
    OrangeMoneyAdapter,
    CountryCode,
    TransactionStatus,
    TransactionType,
    IdentifierType,
    PartyInfo,
    TransactionMetadata,
    OrangeMoneyError,
    AuthenticationError,
    APIError,
    ValidationError,
    TransactionError,
    CallbackError,
    create_orange_money_adapter,
    COUNTRY_ENDPOINTS,
    COUNTRY_CURRENCIES,
)

from .config import (
    OrangeMoneyConfig,
    CountryConfig,
    Environment,
    PhoneNumberValidator,
    AmountValidator,
    EventNameConstants,
    APIEndpointConstants,
    ResultCodes,
    get_country_config,
    get_supported_countries,
    format_currency,
    COUNTRY_CONFIGS,
)

__version__ = "1.0.0"
__author__ = "InfraFabric Finance Team"
__email__ = "finance@infrafabric.com"

__all__ = [
    # Main adapter
    "OrangeMoneyAdapter",
    "create_orange_money_adapter",

    # Enums
    "CountryCode",
    "TransactionStatus",
    "TransactionType",
    "IdentifierType",
    "Environment",

    # Data classes
    "PartyInfo",
    "TransactionMetadata",
    "CountryConfig",

    # Exceptions
    "OrangeMoneyError",
    "AuthenticationError",
    "APIError",
    "ValidationError",
    "TransactionError",
    "CallbackError",

    # Configuration
    "OrangeMoneyConfig",
    "get_country_config",
    "get_supported_countries",

    # Validators
    "PhoneNumberValidator",
    "AmountValidator",

    # Constants
    "EventNameConstants",
    "APIEndpointConstants",
    "ResultCodes",
    "COUNTRY_ENDPOINTS",
    "COUNTRY_CURRENCIES",
    "COUNTRY_CONFIGS",

    # Utilities
    "format_currency",
]


def get_version() -> str:
    """Return the version of the Orange Money adapter."""
    return __version__


def get_supported_countries_list() -> list:
    """
    Get list of supported countries.

    Returns:
        List of dictionaries with country information
    """
    return get_supported_countries()


def quick_start_guide() -> str:
    """
    Display quick start guide.

    Returns:
        Quick start guide as string
    """
    guide = """
    Orange Money Adapter - Quick Start Guide
    ========================================

    1. Install Requirements:
       pip install requests

    2. Set Environment Variables:
       export ORANGE_CLIENT_ID="your-client-id"
       export ORANGE_CLIENT_SECRET="your-client-secret"
       export ORANGE_MERCHANT_KEY="your-merchant-key"
       export ORANGE_COUNTRY_CODE="SN"
       export ORANGE_ENVIRONMENT="production"

    3. Initialize Adapter:
       from orange_money_adapter import OrangeMoneyAdapter, CountryCode

       adapter = OrangeMoneyAdapter(
           client_id="your-client-id",
           client_secret="your-client-secret",
           merchant_key="your-merchant-key",
           country=CountryCode.SENEGAL,
           environment="production"
       )

    4. Disburse Loan:
       result = adapter.transfer(
           amount=50000.0,
           recipient_msisdn="221771234567",
           reference="LOAN-001",
           description="Loan disbursement",
           currency="XOF"
       )

    5. Request Payment:
       result = adapter.request_payment(
           amount=10000.0,
           customer_msisdn="221771234567",
           order_id="REPAY-001",
           description="Loan repayment",
           currency="XOF"
       )

    6. Check Status:
       status = adapter.get_transfer_status("LOAN-001")
       print(status['status'])

    For more examples, see example_usage.py
    For full documentation, see README.md
    """
    return guide


# Print quick info when imported
def _print_import_info():
    """Print information when module is imported."""
    import sys
    if sys.stdout.isatty():  # Only print if in interactive mode
        print(f"Orange Money Adapter v{__version__} loaded")
        print(f"Supported countries: {len(COUNTRY_CONFIGS)}")
        print("Run quick_start_guide() for usage information")


# Uncomment to enable import info
# _print_import_info()
