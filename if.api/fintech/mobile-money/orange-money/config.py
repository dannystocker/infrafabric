"""
Orange Money Adapter Configuration Module

Provides configuration management, validation, and utilities for Orange Money adapter setup.
Supports multiple Francophone African countries with country-specific settings.
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, List
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class Environment(Enum):
    """Orange Money API environments."""
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class CountryCode(Enum):
    """Supported Orange Money countries."""
    SENEGAL = "SN"
    IVORY_COAST = "CI"
    MALI = "ML"
    CAMEROON = "CM"
    GUINEA = "GN"
    BURKINA_FASO = "BF"
    DRC = "CD"
    MADAGASCAR = "MG"
    BOTSWANA = "BW"
    NIGER = "NE"
    CENTRAL_AFRICAN_REPUBLIC = "CF"
    SIERRA_LEONE = "SL"
    LIBERIA = "LR"


class TransactionType(Enum):
    """Transaction types supported by Orange Money."""
    WEB_PAYMENT = "webpayment"
    CASHIN = "cashin"  # Disbursement
    CASHOUT = "cashout"  # Withdrawal
    MERCHANT_PAYMENT = "merchant_payment"
    BALANCE_INQUIRY = "balance"


# ============================================================================
# Country Configuration
# ============================================================================

@dataclass
class CountryConfig:
    """Country-specific configuration."""
    code: str
    name: str
    currency: str
    phone_code: str
    api_endpoint: str
    max_transaction: float
    min_transaction: float
    primary_language: str


# Country configurations
COUNTRY_CONFIGS: Dict[str, CountryConfig] = {
    "SN": CountryConfig(
        code="SN",
        name="Senegal",
        currency="XOF",
        phone_code="221",
        api_endpoint="https://api.orange.com/orange-money-webpay/sn/v1",
        max_transaction=1_000_000.0,
        min_transaction=100.0,
        primary_language="fr"
    ),
    "CI": CountryConfig(
        code="CI",
        name="Côte d'Ivoire (Ivory Coast)",
        currency="XOF",
        phone_code="225",
        api_endpoint="https://api.orange.com/orange-money-webpay/ci/v1",
        max_transaction=1_000_000.0,
        min_transaction=100.0,
        primary_language="fr"
    ),
    "ML": CountryConfig(
        code="ML",
        name="Mali",
        currency="XOF",
        phone_code="223",
        api_endpoint="https://api.orange.com/orange-money-webpay/ml/v1",
        max_transaction=1_000_000.0,
        min_transaction=100.0,
        primary_language="fr"
    ),
    "CM": CountryConfig(
        code="CM",
        name="Cameroon",
        currency="XAF",
        phone_code="237",
        api_endpoint="https://api.orange.com/orange-money-webpay/cm/v1",
        max_transaction=1_000_000.0,
        min_transaction=100.0,
        primary_language="fr"
    ),
    "GN": CountryConfig(
        code="GN",
        name="Guinea",
        currency="GNF",
        phone_code="224",
        api_endpoint="https://api.orange.com/orange-money-webpay/gn/v1",
        max_transaction=10_000_000.0,
        min_transaction=1000.0,
        primary_language="fr"
    ),
    "BF": CountryConfig(
        code="BF",
        name="Burkina Faso",
        currency="XOF",
        phone_code="226",
        api_endpoint="https://api.orange.com/orange-money-webpay/bf/v1",
        max_transaction=1_000_000.0,
        min_transaction=100.0,
        primary_language="fr"
    ),
    "CD": CountryConfig(
        code="CD",
        name="Democratic Republic of Congo",
        currency="CDF",
        phone_code="243",
        api_endpoint="https://api.orange.com/orange-money-webpay/cd/v1",
        max_transaction=2_000_000.0,
        min_transaction=500.0,
        primary_language="fr"
    ),
    "MG": CountryConfig(
        code="MG",
        name="Madagascar",
        currency="MGA",
        phone_code="261",
        api_endpoint="https://api.orange.com/orange-money-webpay/mg/v1",
        max_transaction=5_000_000.0,
        min_transaction=1000.0,
        primary_language="fr"
    ),
    "BW": CountryConfig(
        code="BW",
        name="Botswana",
        currency="BWP",
        phone_code="267",
        api_endpoint="https://api.orange.com/orange-money-webpay/bw/v1",
        max_transaction=50_000.0,
        min_transaction=10.0,
        primary_language="en"
    ),
    "NE": CountryConfig(
        code="NE",
        name="Niger",
        currency="XOF",
        phone_code="227",
        api_endpoint="https://api.orange.com/orange-money-webpay/ne/v1",
        max_transaction=1_000_000.0,
        min_transaction=100.0,
        primary_language="fr"
    ),
    "CF": CountryConfig(
        code="CF",
        name="Central African Republic",
        currency="XAF",
        phone_code="236",
        api_endpoint="https://api.orange.com/orange-money-webpay/cf/v1",
        max_transaction=1_000_000.0,
        min_transaction=100.0,
        primary_language="fr"
    ),
    "SL": CountryConfig(
        code="SL",
        name="Sierra Leone",
        currency="SLL",
        phone_code="232",
        api_endpoint="https://api.orange.com/orange-money-webpay/sl/v1",
        max_transaction=10_000_000.0,
        min_transaction=1000.0,
        primary_language="en"
    ),
    "LR": CountryConfig(
        code="LR",
        name="Liberia",
        currency="LRD",
        phone_code="231",
        api_endpoint="https://api.orange.com/orange-money-webpay/lr/v1",
        max_transaction=100_000.0,
        min_transaction=50.0,
        primary_language="en"
    ),
}


def get_country_config(country_code: str) -> CountryConfig:
    """
    Get configuration for specific country.

    Args:
        country_code: Two-letter country code (e.g., "SN", "CI")

    Returns:
        CountryConfig instance

    Raises:
        ValueError: If country code is not supported
    """
    config = COUNTRY_CONFIGS.get(country_code.upper())
    if not config:
        raise ValueError(f"Unsupported country code: {country_code}")
    return config


# ============================================================================
# Main Configuration
# ============================================================================

@dataclass
class OrangeMoneyConfig:
    """
    Orange Money adapter configuration.

    Attributes:
        client_id: Orange API client ID
        client_secret: Orange API client secret
        merchant_key: Orange Money merchant key
        country_code: Two-letter country code
        environment: Target environment (sandbox or production)
        callback_url: Base URL for webhooks/notifications
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        enable_logging: Enable debug logging
    """

    client_id: str
    client_secret: str
    merchant_key: str
    country_code: str = "SN"
    environment: Environment = Environment.PRODUCTION
    callback_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    enable_logging: bool = True

    def validate(self) -> bool:
        """
        Validate configuration completeness.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If any required field is missing or invalid
        """
        errors = []

        if not self.client_id or not isinstance(self.client_id, str):
            errors.append("client_id: Required and must be string")

        if not self.client_secret or not isinstance(self.client_secret, str):
            errors.append("client_secret: Required and must be string")

        if not self.merchant_key or not isinstance(self.merchant_key, str):
            errors.append("merchant_key: Required and must be string")

        if not self.country_code or not isinstance(self.country_code, str):
            errors.append("country_code: Required and must be string")
        elif self.country_code.upper() not in COUNTRY_CONFIGS:
            errors.append(f"country_code: Unsupported country '{self.country_code}'")

        if not isinstance(self.environment, Environment):
            errors.append("environment: Must be Environment enum value")

        if not isinstance(self.timeout, int) or self.timeout <= 0:
            errors.append("timeout: Must be positive integer")

        if not isinstance(self.max_retries, int) or self.max_retries < 0:
            errors.append("max_retries: Must be non-negative integer")

        if errors:
            raise ValueError("Configuration validation errors:\n" + "\n".join(errors))

        return True

    def get_country_config(self) -> CountryConfig:
        """Get country-specific configuration."""
        return get_country_config(self.country_code)

    @staticmethod
    def from_env() -> "OrangeMoneyConfig":
        """
        Load configuration from environment variables.

        Environment variables:
        - ORANGE_CLIENT_ID: Required
        - ORANGE_CLIENT_SECRET: Required
        - ORANGE_MERCHANT_KEY: Required
        - ORANGE_COUNTRY_CODE: Optional (default: SN)
        - ORANGE_ENVIRONMENT: Optional (default: production)
        - ORANGE_CALLBACK_URL: Optional
        - ORANGE_TIMEOUT: Optional (default: 30)
        - ORANGE_MAX_RETRIES: Optional (default: 3)
        - ORANGE_ENABLE_LOGGING: Optional (default: true)

        Returns:
            Configured OrangeMoneyConfig instance

        Raises:
            ValueError: If required environment variables are missing
        """
        client_id = os.getenv("ORANGE_CLIENT_ID")
        client_secret = os.getenv("ORANGE_CLIENT_SECRET")
        merchant_key = os.getenv("ORANGE_MERCHANT_KEY")

        if not all([client_id, client_secret, merchant_key]):
            missing = [
                name for name, value in [
                    ("ORANGE_CLIENT_ID", client_id),
                    ("ORANGE_CLIENT_SECRET", client_secret),
                    ("ORANGE_MERCHANT_KEY", merchant_key)
                ] if not value
            ]
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        country_code = os.getenv("ORANGE_COUNTRY_CODE", "SN").upper()
        env_str = os.getenv("ORANGE_ENVIRONMENT", "production").lower()
        environment = Environment.PRODUCTION if env_str == "production" else Environment.SANDBOX

        callback_url = os.getenv("ORANGE_CALLBACK_URL")
        timeout = int(os.getenv("ORANGE_TIMEOUT", "30"))
        max_retries = int(os.getenv("ORANGE_MAX_RETRIES", "3"))
        enable_logging = os.getenv("ORANGE_ENABLE_LOGGING", "true").lower() == "true"

        return OrangeMoneyConfig(
            client_id=client_id,
            client_secret=client_secret,
            merchant_key=merchant_key,
            country_code=country_code,
            environment=environment,
            callback_url=callback_url,
            timeout=timeout,
            max_retries=max_retries,
            enable_logging=enable_logging
        )


# ============================================================================
# Validation Utilities
# ============================================================================

class PhoneNumberValidator:
    """Utilities for validating and formatting phone numbers."""

    @staticmethod
    def format_international(phone: str, country_code: str = "221") -> str:
        """
        Convert phone number to international format.

        Args:
            phone: Phone number to format
            country_code: Country phone code (default: 221 for Senegal)

        Returns:
            International format phone number

        Raises:
            ValueError: If phone number is invalid
        """
        # Remove common formatting
        phone = phone.replace(" ", "").replace("-", "").replace("+", "")

        # Handle different input formats
        if phone.startswith("0"):
            # Local format: 0771234567 -> 221771234567
            phone = country_code + phone[1:]
        elif not phone.startswith(country_code):
            # Assume missing country code
            phone = country_code + phone

        return phone

    @staticmethod
    def validate(phone: str, country_code: str = "221") -> bool:
        """
        Validate phone number format.

        Args:
            phone: Phone number to validate (should be international format)
            country_code: Expected country code

        Returns:
            True if valid, False otherwise
        """
        # Remove any formatting
        phone = phone.replace(" ", "").replace("-", "").replace("+", "")

        # Check if numeric
        if not phone.isdigit():
            return False

        # Check if starts with country code
        if not phone.startswith(country_code):
            return False

        # Check length (typically 10-15 digits)
        if not (10 <= len(phone) <= 15):
            return False

        return True

    @staticmethod
    def clean(phone: str, country_code: str = "221") -> str:
        """
        Clean and validate phone number.

        Args:
            phone: Phone number to clean
            country_code: Country phone code

        Returns:
            Cleaned international format phone number

        Raises:
            ValueError: If phone number is invalid
        """
        formatted = PhoneNumberValidator.format_international(phone, country_code)

        if not PhoneNumberValidator.validate(formatted, country_code):
            raise ValueError(f"Invalid phone number format: {phone}")

        return formatted


class AmountValidator:
    """Utilities for validating transaction amounts."""

    @staticmethod
    def validate(amount: float, country_code: str = "SN") -> bool:
        """
        Validate transaction amount for specific country.

        Args:
            amount: Amount to validate
            country_code: Country code for limits

        Returns:
            True if amount is valid, False otherwise
        """
        if not isinstance(amount, (int, float)):
            return False

        try:
            country_config = get_country_config(country_code)
            if amount < country_config.min_transaction or amount > country_config.max_transaction:
                return False
        except ValueError:
            # Unknown country, use generic limits
            if amount < 1.0 or amount > 10_000_000.0:
                return False

        return True

    @staticmethod
    def validate_strict(amount: float, country_code: str = "SN") -> None:
        """
        Validate amount and raise exception if invalid.

        Args:
            amount: Amount to validate
            country_code: Country code for limits

        Raises:
            ValueError: If amount is invalid
        """
        if not isinstance(amount, (int, float)):
            raise ValueError(f"Amount must be numeric, got {type(amount)}")

        country_config = get_country_config(country_code)

        if amount < country_config.min_transaction:
            raise ValueError(
                f"Amount must be at least {country_config.min_transaction} {country_config.currency}, got {amount}"
            )

        if amount > country_config.max_transaction:
            raise ValueError(
                f"Amount must not exceed {country_config.max_transaction} {country_config.currency}, got {amount}"
            )


# ============================================================================
# Event Name Constants
# ============================================================================

class EventNameConstants:
    """IF.bus event name constants."""

    # Authentication events
    AUTH_TOKEN_ACQUIRED = "orange.auth.token_acquired"
    AUTH_TOKEN_FAILED = "orange.auth.token_failed"

    # Collection events
    COLLECTION_INITIATED = "orange.collection.initiated"
    COLLECTION_SUCCESS = "orange.collection.success"
    COLLECTION_FAILED = "orange.collection.failed"
    COLLECTION_STATUS_CHECKED = "orange.collection.status_checked"
    COLLECTION_NOTIFICATION_RECEIVED = "orange.collection.notification_received"

    # Disbursement events
    DISBURSEMENT_INITIATED = "orange.disbursement.initiated"
    DISBURSEMENT_SUCCESS = "orange.disbursement.success"
    DISBURSEMENT_FAILED = "orange.disbursement.failed"
    DISBURSEMENT_STATUS_CHECKED = "orange.disbursement.status_checked"
    DISBURSEMENT_NOTIFICATION_RECEIVED = "orange.disbursement.notification_received"

    # Merchant payment events
    MERCHANT_PAYMENT_INITIATED = "orange.merchant_payment.initiated"
    MERCHANT_PAYMENT_SUCCESS = "orange.merchant_payment.success"
    MERCHANT_PAYMENT_FAILED = "orange.merchant_payment.failed"

    # Account events
    BALANCE_QUERY = "orange.balance.query"
    ACCOUNT_INFO_QUERY = "orange.account.info_query"

    # Error events
    ERROR_OCCURRED = "orange.error.occurred"


# ============================================================================
# API Endpoint Constants
# ============================================================================

class APIEndpointConstants:
    """Orange Money API endpoint constants."""

    # OAuth2
    SANDBOX_AUTH_URL = "https://api.orange.com/oauth/v3"
    PRODUCTION_AUTH_URL = "https://api.orange.com/oauth/v3"

    # Token endpoint
    TOKEN_ENDPOINT = "/token"

    # API paths
    WEBPAYMENT_PATH = "/webpayment"
    CASHIN_PATH = "/cashin"
    BALANCE_PATH = "/account/balance"
    ACCOUNT_LOOKUP_PATH = "/account/lookup"
    MERCHANT_PAYMENT_PATH = "/merchant/payment"


# ============================================================================
# Result Codes
# ============================================================================

class ResultCodes:
    """Orange Money API result codes."""

    SUCCESS = "200"
    CREATED = "201"
    PENDING = "202"
    BAD_REQUEST = "400"
    UNAUTHORIZED = "401"
    FORBIDDEN = "403"
    NOT_FOUND = "404"
    CONFLICT = "409"
    INTERNAL_ERROR = "500"
    SERVICE_UNAVAILABLE = "503"

    # Custom transaction codes
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    INVALID_RECIPIENT = "INVALID_RECIPIENT"
    TRANSACTION_TIMEOUT = "TIMEOUT"
    DUPLICATE_TRANSACTION = "DUPLICATE"

    # Mapping
    CODES = {
        "200": "Success",
        "201": "Created",
        "202": "Pending",
        "400": "Bad request",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "Not found",
        "409": "Conflict/Duplicate",
        "500": "Internal server error",
        "503": "Service unavailable",
        "INSUFFICIENT_FUNDS": "Insufficient funds",
        "INVALID_RECIPIENT": "Invalid recipient",
        "TIMEOUT": "Transaction timeout",
        "DUPLICATE": "Duplicate transaction",
    }

    @classmethod
    def get_description(cls, code: str) -> str:
        """Get human-readable description for result code."""
        return cls.CODES.get(str(code), "Unknown result code")


# ============================================================================
# Default Configurations
# ============================================================================

# Default sandbox configuration for development
DEFAULT_SANDBOX_CONFIG = OrangeMoneyConfig(
    client_id="",  # Obtain from Orange Developer Portal
    client_secret="",  # Obtain from Orange Developer Portal
    merchant_key="",  # Obtain from Orange Money merchant account
    country_code="SN",
    environment=Environment.SANDBOX,
    timeout=30,
    max_retries=3
)


# ============================================================================
# Helper Functions
# ============================================================================

def format_currency(amount: float, country_code: str = "SN") -> str:
    """
    Format amount with currency symbol.

    Args:
        amount: Amount to format
        country_code: Country code

    Returns:
        Formatted string (e.g., "1,000 XOF")
    """
    try:
        country_config = get_country_config(country_code)
        return f"{amount:,.0f} {country_config.currency}"
    except ValueError:
        return f"{amount:,.2f}"


def get_supported_countries() -> List[Dict[str, str]]:
    """
    Get list of supported countries.

    Returns:
        List of country info dictionaries
    """
    return [
        {
            "code": config.code,
            "name": config.name,
            "currency": config.currency,
            "phone_code": config.phone_code,
        }
        for config in COUNTRY_CONFIGS.values()
    ]
