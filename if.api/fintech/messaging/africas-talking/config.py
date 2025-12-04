"""
Africa's Talking Adapter Configuration Module

Provides configuration management, validation, and utilities for Africa's Talking adapter setup.
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, List
from enum import Enum


class Environment(Enum):
    """Africa's Talking API environments."""
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class Country(Enum):
    """Supported African countries."""
    KENYA = "KE"
    UGANDA = "UG"
    TANZANIA = "TZ"
    RWANDA = "RW"
    MALAWI = "MW"
    NIGERIA = "NG"
    ETHIOPIA = "ET"


class SMSEncodingType(Enum):
    """SMS encoding types."""
    GSM_7BIT = "gsm7bit"
    UNICODE = "unicode"


class VoiceCallReason(Enum):
    """Voice call reasons/purposes."""
    DEBT_REMINDER = "debt_reminder"
    PAYMENT_CONFIRMATION = "payment_confirmation"
    LOAN_APPROVED = "loan_approved"
    ACCOUNT_VERIFICATION = "account_verification"
    CUSTOMER_SUPPORT = "customer_support"


class PaymentProvider(Enum):
    """Mobile payment providers."""
    MPESA = "Mpesa"
    MPESA_B2C = "MpesaB2C"
    MPESA_B2B = "MpesaB2B"
    TIGO_TANZANIA = "TigoTanzania"
    AIRTEL_UGANDA = "AirtelUganda"
    AIRTEL_KENYA = "AirtelKenya"
    ATHENA = "Athena"


class PaymentReason(Enum):
    """Payment transaction reasons."""
    SALARY = "SalaryPayment"
    SALARY_WITH_CHARGE = "SalaryPaymentWithWithdrawalChargePaid"
    BUSINESS = "BusinessPayment"
    BUSINESS_WITH_CHARGE = "BusinessPaymentWithWithdrawalChargePaid"
    PROMOTION = "PromotionPayment"


@dataclass
class CountryConfig:
    """
    Configuration for a specific country.

    Attributes:
        name: Country name
        code: ISO country code
        country_code: Phone country code (e.g., '254' for Kenya)
        currency: Currency code (e.g., 'KES')
        sms_sender_id_max_length: Maximum SMS sender ID length
        supports_ussd: Whether USSD is supported
        supports_voice: Whether voice calls are supported
        supports_airtime: Whether airtime is supported
        supports_payments: Whether payments are supported
    """
    name: str
    code: Country
    country_code: str
    currency: str
    sms_sender_id_max_length: int = 11
    supports_ussd: bool = True
    supports_voice: bool = True
    supports_airtime: bool = True
    supports_payments: bool = True


# Country-specific configurations
COUNTRY_CONFIGS: Dict[Country, CountryConfig] = {
    Country.KENYA: CountryConfig(
        name="Kenya",
        code=Country.KENYA,
        country_code="254",
        currency="KES",
        sms_sender_id_max_length=11,
        supports_ussd=True,
        supports_voice=True,
        supports_airtime=True,
        supports_payments=True
    ),
    Country.UGANDA: CountryConfig(
        name="Uganda",
        code=Country.UGANDA,
        country_code="256",
        currency="UGX",
        sms_sender_id_max_length=11,
        supports_ussd=True,
        supports_voice=True,
        supports_airtime=True,
        supports_payments=True
    ),
    Country.TANZANIA: CountryConfig(
        name="Tanzania",
        code=Country.TANZANIA,
        country_code="255",
        currency="TZS",
        sms_sender_id_max_length=11,
        supports_ussd=True,
        supports_voice=True,
        supports_airtime=True,
        supports_payments=True
    ),
    Country.RWANDA: CountryConfig(
        name="Rwanda",
        code=Country.RWANDA,
        country_code="250",
        currency="RWF",
        sms_sender_id_max_length=11,
        supports_ussd=True,
        supports_voice=True,
        supports_airtime=True,
        supports_payments=False
    ),
    Country.MALAWI: CountryConfig(
        name="Malawi",
        code=Country.MALAWI,
        country_code="265",
        currency="MWK",
        sms_sender_id_max_length=11,
        supports_ussd=True,
        supports_voice=False,
        supports_airtime=True,
        supports_payments=False
    ),
    Country.NIGERIA: CountryConfig(
        name="Nigeria",
        code=Country.NIGERIA,
        country_code="234",
        currency="NGN",
        sms_sender_id_max_length=11,
        supports_ussd=True,
        supports_voice=True,
        supports_airtime=True,
        supports_payments=False
    ),
    Country.ETHIOPIA: CountryConfig(
        name="Ethiopia",
        code=Country.ETHIOPIA,
        country_code="251",
        currency="ETB",
        sms_sender_id_max_length=11,
        supports_ussd=False,
        supports_voice=False,
        supports_airtime=True,
        supports_payments=False
    ),
}


@dataclass
class AfricasTalkingConfig:
    """
    Africa's Talking adapter configuration.

    Attributes:
        username: Africa's Talking username (sandbox or your username)
        api_key: Africa's Talking API key
        environment: Target environment (sandbox or production)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        enable_logging: Enable debug logging
        default_country: Default country for operations
    """

    username: str
    api_key: str
    environment: Environment = Environment.SANDBOX
    timeout: int = 30
    max_retries: int = 3
    enable_logging: bool = True
    default_country: Country = Country.KENYA

    def validate(self) -> bool:
        """
        Validate configuration completeness.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If any required field is missing or invalid
        """
        errors = []

        if not self.username or not isinstance(self.username, str):
            errors.append("username: Required and must be string")

        if not self.api_key or not isinstance(self.api_key, str):
            errors.append("api_key: Required and must be string")

        if not isinstance(self.environment, Environment):
            errors.append("environment: Must be Environment enum value")

        if not isinstance(self.timeout, int) or self.timeout <= 0:
            errors.append("timeout: Must be positive integer")

        if not isinstance(self.max_retries, int) or self.max_retries < 0:
            errors.append("max_retries: Must be non-negative integer")

        if not isinstance(self.default_country, Country):
            errors.append("default_country: Must be Country enum value")

        if errors:
            raise ValueError("Configuration validation errors:\n" + "\n".join(errors))

        return True

    @staticmethod
    def from_env() -> "AfricasTalkingConfig":
        """
        Load configuration from environment variables.

        Environment variables:
        - AT_USERNAME or AFRICASTALKING_USERNAME: Required
        - AT_API_KEY or AFRICASTALKING_API_KEY: Required
        - AT_ENVIRONMENT: Optional (default: sandbox)
        - AT_TIMEOUT: Optional (default: 30)
        - AT_MAX_RETRIES: Optional (default: 3)
        - AT_ENABLE_LOGGING: Optional (default: true)
        - AT_DEFAULT_COUNTRY: Optional (default: KE)

        Returns:
            Configured AfricasTalkingConfig instance

        Raises:
            ValueError: If required environment variables are missing
        """
        username = os.getenv("AT_USERNAME") or os.getenv("AFRICASTALKING_USERNAME")
        api_key = os.getenv("AT_API_KEY") or os.getenv("AFRICASTALKING_API_KEY")

        if not all([username, api_key]):
            missing = []
            if not username:
                missing.append("AT_USERNAME or AFRICASTALKING_USERNAME")
            if not api_key:
                missing.append("AT_API_KEY or AFRICASTALKING_API_KEY")
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        env_str = os.getenv("AT_ENVIRONMENT", "sandbox").lower()
        environment = Environment.PRODUCTION if env_str == "production" else Environment.SANDBOX

        timeout = int(os.getenv("AT_TIMEOUT", "30"))
        max_retries = int(os.getenv("AT_MAX_RETRIES", "3"))
        enable_logging = os.getenv("AT_ENABLE_LOGGING", "true").lower() == "true"

        country_str = os.getenv("AT_DEFAULT_COUNTRY", "KE").upper()
        default_country = Country[country_str] if country_str in Country.__members__ else Country.KENYA

        return AfricasTalkingConfig(
            username=username,
            api_key=api_key,
            environment=environment,
            timeout=timeout,
            max_retries=max_retries,
            enable_logging=enable_logging,
            default_country=default_country
        )


class PhoneNumberValidator:
    """Utilities for validating and formatting phone numbers."""

    @staticmethod
    def format_international(phone: str, country: Country = Country.KENYA) -> str:
        """
        Convert phone number to international format.

        Args:
            phone: Phone number to format
            country: Country for phone number

        Returns:
            International format phone number (e.g., +254712345678)

        Raises:
            ValueError: If phone number is invalid
        """
        # Get country config
        config = COUNTRY_CONFIGS.get(country)
        if not config:
            raise ValueError(f"Unsupported country: {country}")

        # Remove common formatting
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        # Handle different input formats
        if phone.startswith("+"):
            # Already international format
            return phone
        elif phone.startswith("0"):
            # Local format: 0712345678 -> +254712345678
            return f"+{config.country_code}{phone[1:]}"
        elif phone.startswith(config.country_code):
            # Missing plus: 254712345678 -> +254712345678
            return f"+{phone}"
        else:
            # Assume missing country code: 712345678 -> +254712345678
            return f"+{config.country_code}{phone}"

    @staticmethod
    def validate(phone: str, country: Country = Country.KENYA) -> bool:
        """
        Validate phone number format.

        Args:
            phone: Phone number to validate (should be international format)
            country: Country for validation

        Returns:
            True if valid, False otherwise
        """
        # Get country config
        config = COUNTRY_CONFIGS.get(country)
        if not config:
            return False

        # Remove formatting
        phone = phone.replace(" ", "").replace("-", "").replace("+", "")

        # Check if numeric
        if not phone.isdigit():
            return False

        # Check if starts with correct country code
        if not phone.startswith(config.country_code):
            return False

        # Check reasonable length (country code + 9-10 digits)
        expected_length = len(config.country_code) + 9
        if len(phone) < expected_length or len(phone) > expected_length + 1:
            return False

        return True

    @staticmethod
    def clean(phone: str, country: Country = Country.KENYA) -> str:
        """
        Clean and validate phone number.

        Args:
            phone: Phone number to clean
            country: Country for phone number

        Returns:
            Cleaned international format phone number

        Raises:
            ValueError: If phone number is invalid
        """
        formatted = PhoneNumberValidator.format_international(phone, country)

        if not PhoneNumberValidator.validate(formatted, country):
            raise ValueError(f"Invalid phone number format: {phone}")

        return formatted

    @staticmethod
    def detect_country(phone: str) -> Optional[Country]:
        """
        Detect country from phone number.

        Args:
            phone: Phone number (international format preferred)

        Returns:
            Detected Country enum or None if not detected
        """
        # Remove formatting
        phone = phone.replace(" ", "").replace("-", "").replace("+", "")

        # Try to match country code
        for country, config in COUNTRY_CONFIGS.items():
            if phone.startswith(config.country_code):
                return country

        return None


class SMSValidator:
    """Utilities for validating SMS parameters."""

    MAX_SMS_LENGTH_GSM = 160
    MAX_SMS_LENGTH_UNICODE = 70
    MAX_SENDER_ID_LENGTH = 11

    @staticmethod
    def validate_message_length(message: str, encoding: SMSEncodingType = SMSEncodingType.GSM_7BIT) -> Tuple[bool, int]:
        """
        Validate SMS message length and calculate parts.

        Args:
            message: SMS message
            encoding: Encoding type

        Returns:
            Tuple of (is_valid, num_parts)
        """
        if encoding == SMSEncodingType.GSM_7BIT:
            max_length = SMSValidator.MAX_SMS_LENGTH_GSM
        else:
            max_length = SMSValidator.MAX_SMS_LENGTH_UNICODE

        # Calculate number of parts
        if len(message) <= max_length:
            num_parts = 1
        else:
            # Multi-part SMS has slightly lower limits
            part_length = 153 if encoding == SMSEncodingType.GSM_7BIT else 67
            num_parts = (len(message) + part_length - 1) // part_length

        return True, num_parts

    @staticmethod
    def validate_sender_id(sender_id: str) -> bool:
        """
        Validate SMS sender ID.

        Args:
            sender_id: Sender ID to validate

        Returns:
            True if valid, False otherwise
        """
        if not sender_id:
            return False

        # Check length
        if len(sender_id) > SMSValidator.MAX_SENDER_ID_LENGTH:
            return False

        # Should be alphanumeric
        if not sender_id.isalnum():
            return False

        return True


class AirtimeValidator:
    """Utilities for validating airtime parameters."""

    MIN_AIRTIME_AMOUNT = 10
    MAX_AIRTIME_AMOUNT = 10000

    @staticmethod
    def validate_amount(amount: float, currency: str = "KES") -> bool:
        """
        Validate airtime amount.

        Args:
            amount: Amount to validate
            currency: Currency code

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(amount, (int, float)):
            return False

        # Convert to float if int
        amount = float(amount)

        # Check range
        if amount < AirtimeValidator.MIN_AIRTIME_AMOUNT:
            return False

        if amount > AirtimeValidator.MAX_AIRTIME_AMOUNT:
            return False

        return True

    @staticmethod
    def validate_currency(currency: str, country: Country) -> bool:
        """
        Validate currency code for country.

        Args:
            currency: Currency code
            country: Country

        Returns:
            True if valid, False otherwise
        """
        config = COUNTRY_CONFIGS.get(country)
        if not config:
            return False

        return currency.upper() == config.currency


class EventNameConstants:
    """IF.bus event name constants."""

    # SMS events
    SMS_SENT = "at.sms.sent"
    SMS_DELIVERED = "at.sms.delivered"
    SMS_FAILED = "at.sms.failed"
    SMS_BULK_SENT = "at.sms.bulk.sent"
    SMS_INCOMING = "at.sms.incoming"

    # USSD events
    USSD_SESSION_STARTED = "at.ussd.session.started"
    USSD_SESSION_CONTINUED = "at.ussd.session.continued"
    USSD_SESSION_ENDED = "at.ussd.session.ended"

    # Voice events
    VOICE_CALL_INITIATED = "at.voice.call.initiated"
    VOICE_CALL_ANSWERED = "at.voice.call.answered"
    VOICE_CALL_COMPLETED = "at.voice.call.completed"
    VOICE_CALL_FAILED = "at.voice.call.failed"

    # Airtime events
    AIRTIME_SENT = "at.airtime.sent"
    AIRTIME_FAILED = "at.airtime.failed"

    # Payment events
    PAYMENT_CHECKOUT_INITIATED = "at.payment.checkout.initiated"
    PAYMENT_CHECKOUT_SUCCESS = "at.payment.checkout.success"
    PAYMENT_CHECKOUT_FAILED = "at.payment.checkout.failed"
    PAYMENT_B2C_INITIATED = "at.payment.b2c.initiated"
    PAYMENT_B2C_SUCCESS = "at.payment.b2c.success"
    PAYMENT_B2C_FAILED = "at.payment.b2c.failed"

    # Error events
    ERROR_OCCURRED = "at.error.occurred"


class APIEndpointConstants:
    """Africa's Talking API endpoint constants."""

    SANDBOX_BASE_URL = "https://api.sandbox.africastalking.com"
    PRODUCTION_BASE_URL = "https://api.africastalking.com"

    SMS_ENDPOINT = "/version1/messaging"
    VOICE_ENDPOINT = "/version1/call"
    AIRTIME_ENDPOINT = "/version1/airtime/send"
    PAYMENT_MOBILE_CHECKOUT_ENDPOINT = "/mobile/checkout/request"
    PAYMENT_MOBILE_B2C_ENDPOINT = "/mobile/b2c/request"


# Default configuration for development
DEFAULT_SANDBOX_CONFIG = AfricasTalkingConfig(
    username="sandbox",
    api_key="",  # Set your sandbox API key
    environment=Environment.SANDBOX,
    timeout=30,
    max_retries=3,
    enable_logging=True,
    default_country=Country.KENYA
)


# SMS Templates for Microfinance
class SMSTemplates:
    """Pre-built SMS templates for microfinance use cases."""

    @staticmethod
    def loan_reminder(
        customer_name: str,
        loan_amount: float,
        due_date: str,
        days_overdue: int = 0
    ) -> str:
        """
        Generate loan payment reminder SMS.

        Args:
            customer_name: Customer's name
            loan_amount: Outstanding loan amount
            due_date: Payment due date
            days_overdue: Number of days overdue (0 if not overdue)

        Returns:
            SMS message text
        """
        if days_overdue > 0:
            return (
                f"Dear {customer_name}, your loan payment of KES {loan_amount:.2f} "
                f"was due on {due_date} ({days_overdue} days overdue). "
                f"Please pay via M-Pesa to avoid penalties."
            )
        else:
            return (
                f"Dear {customer_name}, reminder: your loan payment of KES {loan_amount:.2f} "
                f"is due on {due_date}. Pay via M-Pesa to our Till number."
            )

    @staticmethod
    def payment_confirmation(
        customer_name: str,
        amount: float,
        transaction_id: str,
        new_balance: float
    ) -> str:
        """
        Generate payment confirmation SMS.

        Args:
            customer_name: Customer's name
            amount: Payment amount
            transaction_id: Transaction reference
            new_balance: New outstanding balance

        Returns:
            SMS message text
        """
        return (
            f"Dear {customer_name}, we have received your payment of KES {amount:.2f}. "
            f"Ref: {transaction_id}. Your new balance is KES {new_balance:.2f}. Thank you!"
        )

    @staticmethod
    def loan_approved(
        customer_name: str,
        loan_amount: float,
        repayment_date: str
    ) -> str:
        """
        Generate loan approval SMS.

        Args:
            customer_name: Customer's name
            loan_amount: Approved loan amount
            repayment_date: Repayment due date

        Returns:
            SMS message text
        """
        return (
            f"Congratulations {customer_name}! Your loan of KES {loan_amount:.2f} "
            f"has been approved. Funds will be disbursed shortly. "
            f"Repayment due: {repayment_date}."
        )

    @staticmethod
    def overdue_notice(
        customer_name: str,
        amount_due: float,
        days_overdue: int,
        penalty: float
    ) -> str:
        """
        Generate overdue payment notice SMS.

        Args:
            customer_name: Customer's name
            amount_due: Amount due
            days_overdue: Number of days overdue
            penalty: Penalty amount

        Returns:
            SMS message text
        """
        return (
            f"URGENT: Dear {customer_name}, your loan payment of KES {amount_due:.2f} "
            f"is {days_overdue} days overdue. Penalty: KES {penalty:.2f}. "
            f"Please pay immediately to avoid further action."
        )


from typing import Tuple

# Export all
__all__ = [
    'Environment',
    'Country',
    'SMSEncodingType',
    'VoiceCallReason',
    'PaymentProvider',
    'PaymentReason',
    'CountryConfig',
    'COUNTRY_CONFIGS',
    'AfricasTalkingConfig',
    'PhoneNumberValidator',
    'SMSValidator',
    'AirtimeValidator',
    'EventNameConstants',
    'APIEndpointConstants',
    'DEFAULT_SANDBOX_CONFIG',
    'SMSTemplates',
]
