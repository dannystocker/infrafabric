"""
Airtel Money API Configuration

Configuration management for Airtel Money adapter including:
- Environment variables
- Country-specific settings
- Currency mappings
- API endpoint configurations
- Credentials management

Author: InfraFabric Finance Team
Version: 1.0.0
Date: 2025-12-04
"""

import os
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# Environment Variables
# ============================================================================

def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable with optional default.

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value or default
    """
    return os.getenv(key, default)


# ============================================================================
# Configuration Classes
# ============================================================================

@dataclass
class AirtelMoneyConfig:
    """
    Airtel Money configuration.

    Environment Variables:
        AIRTEL_CLIENT_ID: OAuth2 client ID
        AIRTEL_CLIENT_SECRET: OAuth2 client secret
        AIRTEL_COUNTRY: Country code (KE, UG, TZ, etc.)
        AIRTEL_ENVIRONMENT: Environment (production or sandbox)
        AIRTEL_PIN: Optional PIN for disbursements
        AIRTEL_CALLBACK_URL: Callback URL for webhooks
        AIRTEL_TIMEOUT: Request timeout in seconds (default: 30)
        AIRTEL_MAX_RETRIES: Maximum retry attempts (default: 3)
    """

    client_id: str
    client_secret: str
    country: str = "KE"
    environment: str = "production"
    pin: Optional[str] = None
    callback_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> "AirtelMoneyConfig":
        """
        Create configuration from environment variables.

        Returns:
            AirtelMoneyConfig instance

        Raises:
            ValueError: If required environment variables are missing
        """
        client_id = get_env_var("AIRTEL_CLIENT_ID")
        client_secret = get_env_var("AIRTEL_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(
                "AIRTEL_CLIENT_ID and AIRTEL_CLIENT_SECRET environment variables are required"
            )

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            country=get_env_var("AIRTEL_COUNTRY", "KE"),
            environment=get_env_var("AIRTEL_ENVIRONMENT", "production"),
            pin=get_env_var("AIRTEL_PIN"),
            callback_url=get_env_var("AIRTEL_CALLBACK_URL"),
            timeout=int(get_env_var("AIRTEL_TIMEOUT", "30")),
            max_retries=int(get_env_var("AIRTEL_MAX_RETRIES", "3")),
        )

    def to_dict(self) -> Dict[str, any]:
        """Convert configuration to dictionary."""
        return {
            "client_id": self.client_id,
            "client_secret": "***REDACTED***",  # Never expose secret
            "country": self.country,
            "environment": self.environment,
            "pin": "***REDACTED***" if self.pin else None,
            "callback_url": self.callback_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
        }


# ============================================================================
# Country Configurations
# ============================================================================

class CountryConfig:
    """Country-specific configuration."""

    def __init__(
        self,
        code: str,
        name: str,
        currency: str,
        phone_prefix: str,
        phone_length: int,
        min_transaction_amount: float,
        max_transaction_amount: float,
    ):
        """
        Initialize country configuration.

        Args:
            code: ISO 3166-1 alpha-2 country code
            name: Country name
            currency: ISO 4217 currency code
            phone_prefix: International dialing prefix
            phone_length: Standard phone number length (without prefix)
            min_transaction_amount: Minimum transaction amount
            max_transaction_amount: Maximum transaction amount
        """
        self.code = code
        self.name = name
        self.currency = currency
        self.phone_prefix = phone_prefix
        self.phone_length = phone_length
        self.min_transaction_amount = min_transaction_amount
        self.max_transaction_amount = max_transaction_amount

    def __repr__(self) -> str:
        return (
            f"CountryConfig(code={self.code}, name={self.name}, "
            f"currency={self.currency}, prefix={self.phone_prefix})"
        )


# ============================================================================
# Country Definitions
# ============================================================================

# East Africa
KENYA = CountryConfig(
    code="KE",
    name="Kenya",
    currency="KES",
    phone_prefix="254",
    phone_length=9,
    min_transaction_amount=10.0,
    max_transaction_amount=150000.0,
)

UGANDA = CountryConfig(
    code="UG",
    name="Uganda",
    currency="UGX",
    phone_prefix="256",
    phone_length=9,
    min_transaction_amount=1000.0,
    max_transaction_amount=5000000.0,
)

TANZANIA = CountryConfig(
    code="TZ",
    name="Tanzania",
    currency="TZS",
    phone_prefix="255",
    phone_length=9,
    min_transaction_amount=1000.0,
    max_transaction_amount=10000000.0,
)

RWANDA = CountryConfig(
    code="RW",
    name="Rwanda",
    currency="RWF",
    phone_prefix="250",
    phone_length=9,
    min_transaction_amount=100.0,
    max_transaction_amount=5000000.0,
)

# Southern Africa
ZAMBIA = CountryConfig(
    code="ZM",
    name="Zambia",
    currency="ZMW",
    phone_prefix="260",
    phone_length=9,
    min_transaction_amount=10.0,
    max_transaction_amount=50000.0,
)

MALAWI = CountryConfig(
    code="MW",
    name="Malawi",
    currency="MWK",
    phone_prefix="265",
    phone_length=9,
    min_transaction_amount=500.0,
    max_transaction_amount=2000000.0,
)

# West Africa
NIGERIA = CountryConfig(
    code="NG",
    name="Nigeria",
    currency="NGN",
    phone_prefix="234",
    phone_length=10,
    min_transaction_amount=100.0,
    max_transaction_amount=1000000.0,
)

NIGER = CountryConfig(
    code="NE",
    name="Niger",
    currency="XOF",
    phone_prefix="227",
    phone_length=8,
    min_transaction_amount=500.0,
    max_transaction_amount=5000000.0,
)

# Central Africa
DRC = CountryConfig(
    code="CD",
    name="Democratic Republic of Congo",
    currency="CDF",
    phone_prefix="243",
    phone_length=9,
    min_transaction_amount=1000.0,
    max_transaction_amount=10000000.0,
)

CHAD = CountryConfig(
    code="TD",
    name="Chad",
    currency="XAF",
    phone_prefix="235",
    phone_length=8,
    min_transaction_amount=500.0,
    max_transaction_amount=5000000.0,
)

GABON = CountryConfig(
    code="GA",
    name="Gabon",
    currency="XAF",
    phone_prefix="241",
    phone_length=7,
    min_transaction_amount=500.0,
    max_transaction_amount=5000000.0,
)

CONGO_BRAZZAVILLE = CountryConfig(
    code="CG",
    name="Republic of Congo",
    currency="XAF",
    phone_prefix="242",
    phone_length=9,
    min_transaction_amount=500.0,
    max_transaction_amount=5000000.0,
)

# Indian Ocean
MADAGASCAR = CountryConfig(
    code="MG",
    name="Madagascar",
    currency="MGA",
    phone_prefix="261",
    phone_length=9,
    min_transaction_amount=1000.0,
    max_transaction_amount=10000000.0,
)

SEYCHELLES = CountryConfig(
    code="SC",
    name="Seychelles",
    currency="SCR",
    phone_prefix="248",
    phone_length=7,
    min_transaction_amount=10.0,
    max_transaction_amount=50000.0,
)


# ============================================================================
# Country Registry
# ============================================================================

COUNTRIES: Dict[str, CountryConfig] = {
    "KE": KENYA,
    "UG": UGANDA,
    "TZ": TANZANIA,
    "RW": RWANDA,
    "ZM": ZAMBIA,
    "MW": MALAWI,
    "NG": NIGERIA,
    "NE": NIGER,
    "CD": DRC,
    "TD": CHAD,
    "GA": GABON,
    "CG": CONGO_BRAZZAVILLE,
    "MG": MADAGASCAR,
    "SC": SEYCHELLES,
}


def get_country_config(country_code: str) -> Optional[CountryConfig]:
    """
    Get country configuration by code.

    Args:
        country_code: ISO 3166-1 alpha-2 country code

    Returns:
        CountryConfig instance or None if not found

    Example:
        >>> config = get_country_config("KE")
        >>> print(config.currency)  # KES
    """
    return COUNTRIES.get(country_code.upper())


def list_supported_countries() -> list[CountryConfig]:
    """
    Get list of all supported countries.

    Returns:
        List of CountryConfig instances

    Example:
        >>> countries = list_supported_countries()
        >>> for country in countries:
        ...     print(f"{country.name} ({country.code}): {country.currency}")
    """
    return list(COUNTRIES.values())


# ============================================================================
# API Endpoint Configuration
# ============================================================================

class APIEndpoints:
    """API endpoint configuration."""

    # Base URLs
    SANDBOX_BASE_URL = "https://openapiuat.airtel.africa"
    PRODUCTION_BASE_URL = "https://openapi.airtel.africa"

    # Endpoint paths
    OAUTH_PATH = "/auth/oauth2/token"
    COLLECTION_PATH = "/merchant/v1/payments"
    DISBURSEMENT_PATH = "/standard/v1/disbursements"
    TRANSACTION_STATUS_PATH = "/standard/v1/payments"
    BALANCE_PATH = "/standard/v1/users/balance"
    KYC_PATH = "/standard/v1/users"
    REFUND_PATH = "/standard/v1/payments/refund"

    @classmethod
    def get_base_url(cls, environment: str) -> str:
        """
        Get base URL for environment.

        Args:
            environment: "production" or "sandbox"

        Returns:
            Base URL string
        """
        if environment.lower() == "sandbox":
            return cls.SANDBOX_BASE_URL
        return cls.PRODUCTION_BASE_URL

    @classmethod
    def get_oauth_url(cls, environment: str) -> str:
        """Get OAuth token endpoint URL."""
        return f"{cls.get_base_url(environment)}{cls.OAUTH_PATH}"

    @classmethod
    def get_collection_url(cls, environment: str) -> str:
        """Get collection endpoint URL."""
        return f"{cls.get_base_url(environment)}{cls.COLLECTION_PATH}"

    @classmethod
    def get_disbursement_url(cls, environment: str) -> str:
        """Get disbursement endpoint URL."""
        return f"{cls.get_base_url(environment)}{cls.DISBURSEMENT_PATH}"

    @classmethod
    def get_balance_url(cls, environment: str) -> str:
        """Get balance endpoint URL."""
        return f"{cls.get_base_url(environment)}{cls.BALANCE_PATH}"


# ============================================================================
# Transaction Limits
# ============================================================================

@dataclass
class TransactionLimits:
    """Transaction limits configuration."""

    min_collection: float
    max_collection: float
    min_disbursement: float
    max_disbursement: float
    daily_limit: float
    monthly_limit: float

    @classmethod
    def for_country(cls, country_code: str) -> "TransactionLimits":
        """
        Get transaction limits for country.

        Args:
            country_code: ISO 3166-1 alpha-2 country code

        Returns:
            TransactionLimits instance
        """
        country = get_country_config(country_code)

        if not country:
            # Default limits
            return cls(
                min_collection=10.0,
                max_collection=100000.0,
                min_disbursement=10.0,
                max_disbursement=100000.0,
                daily_limit=500000.0,
                monthly_limit=5000000.0,
            )

        # Country-specific limits
        return cls(
            min_collection=country.min_transaction_amount,
            max_collection=country.max_transaction_amount,
            min_disbursement=country.min_transaction_amount,
            max_disbursement=country.max_transaction_amount,
            daily_limit=country.max_transaction_amount * 10,
            monthly_limit=country.max_transaction_amount * 100,
        )


# ============================================================================
# Validation Helpers
# ============================================================================

def validate_phone_number(phone: str, country_code: str) -> Tuple[bool, str]:
    """
    Validate phone number format for country.

    Args:
        phone: Phone number to validate
        country_code: ISO 3166-1 alpha-2 country code

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> valid, msg = validate_phone_number("254712345678", "KE")
        >>> print(valid)  # True
    """
    country = get_country_config(country_code)

    if not country:
        return False, f"Unsupported country: {country_code}"

    # Remove spaces, dashes, plus
    phone = phone.replace(" ", "").replace("-", "").replace("+", "")

    # Check if starts with country prefix
    if not phone.startswith(country.phone_prefix):
        return False, f"Phone number must start with {country.phone_prefix}"

    # Check length
    expected_length = len(country.phone_prefix) + country.phone_length
    if len(phone) != expected_length:
        return (
            False,
            f"Phone number must be {expected_length} digits for {country.name}",
        )

    # Check if all digits
    if not phone.isdigit():
        return False, "Phone number must contain only digits"

    return True, ""


def validate_amount(
    amount: float, transaction_type: str, country_code: str
) -> Tuple[bool, str]:
    """
    Validate transaction amount.

    Args:
        amount: Transaction amount
        transaction_type: "collection" or "disbursement"
        country_code: ISO 3166-1 alpha-2 country code

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> valid, msg = validate_amount(1000.0, "collection", "KE")
        >>> print(valid)  # True
    """
    if amount <= 0:
        return False, "Amount must be greater than 0"

    limits = TransactionLimits.for_country(country_code)

    if transaction_type == "collection":
        if amount < limits.min_collection:
            return False, f"Minimum collection amount is {limits.min_collection}"
        if amount > limits.max_collection:
            return False, f"Maximum collection amount is {limits.max_collection}"
    elif transaction_type == "disbursement":
        if amount < limits.min_disbursement:
            return False, f"Minimum disbursement amount is {limits.min_disbursement}"
        if amount > limits.max_disbursement:
            return False, f"Maximum disbursement amount is {limits.max_disbursement}"
    else:
        return False, f"Unknown transaction type: {transaction_type}"

    return True, ""


# ============================================================================
# Example Configuration
# ============================================================================

if __name__ == "__main__":
    # Example: Load configuration from environment
    try:
        config = AirtelMoneyConfig.from_env()
        print("Configuration loaded successfully:")
        print(config.to_dict())
    except ValueError as e:
        print(f"Configuration error: {e}")

    # Example: Get country configuration
    kenya = get_country_config("KE")
    print(f"\nKenya Configuration: {kenya}")
    print(f"Currency: {kenya.currency}")
    print(f"Phone prefix: +{kenya.phone_prefix}")
    print(f"Transaction limits: {kenya.min_transaction_amount} - {kenya.max_transaction_amount}")

    # Example: List all supported countries
    print("\nSupported Countries:")
    for country in list_supported_countries():
        print(f"- {country.name} ({country.code}): {country.currency}")

    # Example: Validate phone number
    phone = "254712345678"
    is_valid, error = validate_phone_number(phone, "KE")
    print(f"\nPhone validation for {phone}: {is_valid}")
    if not is_valid:
        print(f"Error: {error}")

    # Example: Validate amount
    amount = 1000.0
    is_valid, error = validate_amount(amount, "collection", "KE")
    print(f"\nAmount validation for {amount} KES: {is_valid}")
    if not is_valid:
        print(f"Error: {error}")
