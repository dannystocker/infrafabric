"""
M-Pesa Adapter Configuration Module

Provides configuration management, validation, and utilities for M-Pesa adapter setup.
"""

import os
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class Environment(Enum):
    """M-Pesa API environments."""
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class PaymentType(Enum):
    """Payment types supported by B2C endpoint."""
    BUSINESS_PAYMENT = "BusinessPayment"
    SALARY_PAYMENT = "SalaryPayment"
    PROMOTION_PAYMENT = "PromotionPayment"


class CommandID(Enum):
    """M-Pesa transaction command types."""
    # STK Push
    CUSTOMER_PAY_BILL_ONLINE = "CustomerPayBillOnline"

    # B2C
    BUSINESS_PAYMENT = "BusinessPayment"
    SALARY_PAYMENT = "SalaryPayment"
    PROMOTION_PAYMENT = "PromotionPayment"

    # Account operations
    GET_ACCOUNT = "GetAccount"
    TRANSACTION_STATUS_QUERY = "TransactionStatusQuery"


class IdentifierType(Enum):
    """Transaction party identifier types."""
    MSISDN = "1"           # Phone number
    TILL_NUMBER = "2"      # Till number
    SHORTCODE = "3"        # Business shortcode


@dataclass
class MpesaConfig:
    """
    M-Pesa adapter configuration.

    Attributes:
        consumer_key: Daraja API consumer key
        consumer_secret: Daraja API consumer secret
        business_shortcode: M-Pesa business shortcode
        passkey: M-Pesa online passkey
        environment: Target environment (sandbox or production)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        enable_logging: Enable debug logging
    """

    consumer_key: str
    consumer_secret: str
    business_shortcode: str
    passkey: str
    environment: Environment = Environment.SANDBOX
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

        if not self.consumer_key or not isinstance(self.consumer_key, str):
            errors.append("consumer_key: Required and must be string")

        if not self.consumer_secret or not isinstance(self.consumer_secret, str):
            errors.append("consumer_secret: Required and must be string")

        if not self.business_shortcode or not isinstance(self.business_shortcode, str):
            errors.append("business_shortcode: Required and must be string")

        if not self.passkey or not isinstance(self.passkey, str):
            errors.append("passkey: Required and must be string")

        if not isinstance(self.environment, Environment):
            errors.append("environment: Must be Environment enum value")

        if not isinstance(self.timeout, int) or self.timeout <= 0:
            errors.append("timeout: Must be positive integer")

        if not isinstance(self.max_retries, int) or self.max_retries < 0:
            errors.append("max_retries: Must be non-negative integer")

        if errors:
            raise ValueError("Configuration validation errors:\n" + "\n".join(errors))

        return True

    @staticmethod
    def from_env() -> "MpesaConfig":
        """
        Load configuration from environment variables.

        Environment variables:
        - MPESA_CONSUMER_KEY: Required
        - MPESA_CONSUMER_SECRET: Required
        - MPESA_BUSINESS_SHORTCODE: Required
        - MPESA_PASSKEY: Required
        - MPESA_ENVIRONMENT: Optional (default: sandbox)
        - MPESA_TIMEOUT: Optional (default: 30)
        - MPESA_MAX_RETRIES: Optional (default: 3)
        - MPESA_ENABLE_LOGGING: Optional (default: true)

        Returns:
            Configured MpesaConfig instance

        Raises:
            ValueError: If required environment variables are missing
        """
        consumer_key = os.getenv("MPESA_CONSUMER_KEY")
        consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")
        business_shortcode = os.getenv("MPESA_BUSINESS_SHORTCODE")
        passkey = os.getenv("MPESA_PASSKEY")

        if not all([consumer_key, consumer_secret, business_shortcode, passkey]):
            missing = [
                name for name, value in [
                    ("MPESA_CONSUMER_KEY", consumer_key),
                    ("MPESA_CONSUMER_SECRET", consumer_secret),
                    ("MPESA_BUSINESS_SHORTCODE", business_shortcode),
                    ("MPESA_PASSKEY", passkey)
                ] if not value
            ]
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        env_str = os.getenv("MPESA_ENVIRONMENT", "sandbox").lower()
        environment = Environment.PRODUCTION if env_str == "production" else Environment.SANDBOX

        timeout = int(os.getenv("MPESA_TIMEOUT", "30"))
        max_retries = int(os.getenv("MPESA_MAX_RETRIES", "3"))
        enable_logging = os.getenv("MPESA_ENABLE_LOGGING", "true").lower() == "true"

        return MpesaConfig(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            business_shortcode=business_shortcode,
            passkey=passkey,
            environment=environment,
            timeout=timeout,
            max_retries=max_retries,
            enable_logging=enable_logging
        )


class PhoneNumberValidator:
    """Utilities for validating and formatting phone numbers."""

    @staticmethod
    def format_international(phone: str, country_code: str = "254") -> str:
        """
        Convert phone number to international format.

        Args:
            phone: Phone number to format
            country_code: Country code (default: 254 for Kenya)

        Returns:
            International format phone number

        Raises:
            ValueError: If phone number is invalid
        """
        # Remove common formatting
        phone = phone.replace(" ", "").replace("-", "").replace("+", "")

        # Handle different input formats
        if phone.startswith("0"):
            # Local format: 0712345678 -> 254712345678
            phone = country_code + phone[1:]
        elif not phone.startswith(country_code):
            # Assume missing country code
            phone = country_code + phone

        return phone

    @staticmethod
    def validate(phone: str) -> bool:
        """
        Validate phone number format.

        Args:
            phone: Phone number to validate (should be international format)

        Returns:
            True if valid, False otherwise
        """
        # Remove any formatting
        phone = phone.replace(" ", "").replace("-", "").replace("+", "")

        # Check if numeric and correct length for Kenya
        if not phone.isdigit():
            return False

        if not (len(phone) == 12 and phone.startswith("254")):
            return False

        return True

    @staticmethod
    def clean(phone: str) -> str:
        """
        Clean and validate phone number.

        Args:
            phone: Phone number to clean

        Returns:
            Cleaned international format phone number

        Raises:
            ValueError: If phone number is invalid
        """
        formatted = PhoneNumberValidator.format_international(phone)

        if not PhoneNumberValidator.validate(formatted):
            raise ValueError(f"Invalid phone number format: {phone}")

        return formatted


class AmountValidator:
    """Utilities for validating transaction amounts."""

    # M-Pesa transaction limits
    MIN_AMOUNT = 1.0
    MAX_AMOUNT = 150000.0

    @staticmethod
    def validate(amount: float) -> bool:
        """
        Validate transaction amount.

        Args:
            amount: Amount to validate (in KES)

        Returns:
            True if amount is valid, False otherwise
        """
        if not isinstance(amount, (int, float)):
            return False

        if amount < AmountValidator.MIN_AMOUNT or amount > AmountValidator.MAX_AMOUNT:
            return False

        return True

    @staticmethod
    def validate_strict(amount: float) -> None:
        """
        Validate amount and raise exception if invalid.

        Args:
            amount: Amount to validate

        Raises:
            ValueError: If amount is invalid
        """
        if not isinstance(amount, (int, float)):
            raise ValueError(f"Amount must be numeric, got {type(amount)}")

        if amount < AmountValidator.MIN_AMOUNT:
            raise ValueError(
                f"Amount must be at least {AmountValidator.MIN_AMOUNT} KES, got {amount}"
            )

        if amount > AmountValidator.MAX_AMOUNT:
            raise ValueError(
                f"Amount must not exceed {AmountValidator.MAX_AMOUNT} KES, got {amount}"
            )


class TransactionCodec:
    """Utilities for encoding/decoding transaction data."""

    @staticmethod
    def parse_result_parameters(result_params: str) -> dict:
        """
        Parse M-Pesa result parameters string.

        Result parameters are comma-separated key-value pairs.

        Args:
            result_params: Raw result parameters string

        Returns:
            Dictionary of parsed parameters

        Example:
            >>> params = "Amount|100|Balance|900"
            >>> TransactionCodec.parse_result_parameters(params)
            {'Amount': '100', 'Balance': '900'}
        """
        parsed = {}

        if not result_params:
            return parsed

        parts = result_params.split("|")

        for i in range(0, len(parts) - 1, 2):
            key = parts[i]
            value = parts[i + 1]
            parsed[key] = value

        return parsed

    @staticmethod
    def format_result_parameters(params: dict) -> str:
        """
        Format transaction parameters to M-Pesa format.

        Args:
            params: Parameters dictionary

        Returns:
            Formatted parameters string

        Example:
            >>> params = {'Amount': '100', 'Balance': '900'}
            >>> TransactionCodec.format_result_parameters(params)
            'Amount|100|Balance|900'
        """
        parts = []

        for key, value in params.items():
            parts.append(str(key))
            parts.append(str(value))

        return "|".join(parts)


class EventNameConstants:
    """IF.bus event name constants."""

    # Authentication events
    AUTH_TOKEN_ACQUIRED = "mpesa.auth.token_acquired"

    # STK Push events
    STK_PUSH_INITIATED = "mpesa.stk_push.initiated"
    STK_PUSH_SUCCESS = "mpesa.stk_push.success"
    STK_PUSH_FAILED = "mpesa.stk_push.failed"

    # B2C events
    B2C_INITIATED = "mpesa.b2c.initiated"
    B2C_SUCCESS = "mpesa.b2c.success"
    B2C_FAILED = "mpesa.b2c.failed"

    # Query events
    TRANSACTION_STATUS_QUERY = "mpesa.transaction.status_query"
    BALANCE_QUERY = "mpesa.balance.query"

    # Error events
    ERROR_OCCURRED = "mpesa.error.occurred"


class APIEndpointConstants:
    """M-Pesa API endpoint constants."""

    SANDBOX_BASE_URL = "https://sandbox.safaricom.co.ke"
    PRODUCTION_BASE_URL = "https://api.safaricom.co.ke"

    OAUTH_ENDPOINT = "/oauth/v1/generate"
    STK_PUSH_ENDPOINT = "/mpesa/stkpush/v1/processrequest"
    STK_QUERY_ENDPOINT = "/mpesa/stkpushquery/v1/query"
    B2C_ENDPOINT = "/mpesa/b2c/v1/paymentrequest"
    BALANCE_ENDPOINT = "/mpesa/accountbalance/v1/query"
    TRANSACTION_STATUS_ENDPOINT = "/mpesa/transactionstatus/v1/query"


class ResultCodes:
    """M-Pesa API result codes."""

    SUCCESS = "0"
    INSUFFICIENT_FUNDS = "1"
    LESS_AMOUNT = "2"
    MORE_AMOUNT = "3"
    EXEC_TIMEOUT = "4"
    INTERNAL_ERROR = "5"
    REQUEST_TIMEOUT = "6"
    SERVICE_UNAVAILABLE = "7"
    THROTTLED = "8"
    END_USER_TIMEOUT = "9"

    # Mapping
    CODES = {
        "0": "Success",
        "1": "Insufficient funds",
        "2": "Less amount",
        "3": "More amount",
        "4": "Execution timeout",
        "5": "Internal error",
        "6": "Request timeout",
        "7": "Service unavailable",
        "8": "Request throttled",
        "9": "End user timeout"
    }

    @classmethod
    def get_description(cls, code: str) -> str:
        """Get human-readable description for result code."""
        return cls.CODES.get(code, "Unknown result code")


# Default configuration for development
DEFAULT_SANDBOX_CONFIG = MpesaConfig(
    consumer_key="",
    consumer_secret="",
    business_shortcode="174379",  # Safaricom test shortcode
    passkey="bfb279f9aa9bdbcf158e97dd1a503b6055c2f8e3c36a6e0c",  # Safaricom test passkey
    environment=Environment.SANDBOX,
    timeout=30,
    max_retries=3
)
