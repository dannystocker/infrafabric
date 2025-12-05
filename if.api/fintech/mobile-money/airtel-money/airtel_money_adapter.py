"""
Airtel Money Africa API Adapter

Production-ready adapter for Airtel Money APIs covering 14 African countries:
- Collections API (USSD Push payment)
- Disbursements API (money transfer)
- Account API (balance, KYC inquiry)
- Transaction status monitoring
- Multi-country support across Africa

Implements OAuth2 client credentials authentication with token caching.
Emits IF.bus events for transaction lifecycle monitoring.

Official API: https://developers.airtel.africa/

Author: InfraFabric Finance Team
Version: 1.0.0
Date: 2025-12-04
"""

import logging
import uuid
import hmac
import hashlib
import json
from typing import Any, Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import time

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from fintech_debug_utils import ft_debug_log_request, ft_debug_log_response


# ============================================================================
# Enums and Constants
# ============================================================================

class CountryCode(str, Enum):
    """Supported Airtel Money countries with API configurations."""
    KENYA = "KE"
    UGANDA = "UG"
    TANZANIA = "TZ"
    RWANDA = "RW"
    ZAMBIA = "ZM"
    MALAWI = "MW"
    NIGERIA = "NG"
    DRC = "CD"
    MADAGASCAR = "MG"
    SEYCHELLES = "SC"
    CHAD = "TD"
    GABON = "GA"
    NIGER = "NE"
    CONGO_BRAZZAVILLE = "CG"


class TransactionStatus(str, Enum):
    """Airtel Money transaction status codes."""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    PROCESSING = "PROCESSING"
    AMBIGUOUS = "AMBIGUOUS"


class TransactionType(str, Enum):
    """Supported transaction types."""
    COLLECTION = "COLLECTION"  # USSD Push
    DISBURSEMENT = "DISBURSEMENT"  # Money transfer
    REFUND = "REFUND"  # Refund transaction
    KYC = "KYC"  # KYC verification


class Currency(str, Enum):
    """Currency codes for Airtel Money countries."""
    KES = "KES"  # Kenya Shilling
    UGX = "UGX"  # Uganda Shilling
    TZS = "TZS"  # Tanzania Shilling
    RWF = "RWF"  # Rwanda Franc
    ZMW = "ZMW"  # Zambia Kwacha
    MWK = "MWK"  # Malawi Kwacha
    NGN = "NGN"  # Nigeria Naira
    CDF = "CDF"  # DRC Franc
    MGA = "MGA"  # Madagascar Ariary
    SCR = "SCR"  # Seychelles Rupee
    XAF = "XAF"  # Central African CFA Franc (Chad, Gabon, Congo-Brazzaville)
    XOF = "XOF"  # West African CFA Franc (Niger)


# Country to currency mapping
COUNTRY_CURRENCY_MAP: Dict[CountryCode, Currency] = {
    CountryCode.KENYA: Currency.KES,
    CountryCode.UGANDA: Currency.UGX,
    CountryCode.TANZANIA: Currency.TZS,
    CountryCode.RWANDA: Currency.RWF,
    CountryCode.ZAMBIA: Currency.ZMW,
    CountryCode.MALAWI: Currency.MWK,
    CountryCode.NIGERIA: Currency.NGN,
    CountryCode.DRC: Currency.CDF,
    CountryCode.MADAGASCAR: Currency.MGA,
    CountryCode.SEYCHELLES: Currency.SCR,
    CountryCode.CHAD: Currency.XAF,
    CountryCode.GABON: Currency.XAF,
    CountryCode.NIGER: Currency.XOF,
    CountryCode.CONGO_BRAZZAVILLE: Currency.XAF,
}


# Country phone prefixes
COUNTRY_PHONE_PREFIXES: Dict[CountryCode, str] = {
    CountryCode.KENYA: "254",
    CountryCode.UGANDA: "256",
    CountryCode.TANZANIA: "255",
    CountryCode.RWANDA: "250",
    CountryCode.ZAMBIA: "260",
    CountryCode.MALAWI: "265",
    CountryCode.NIGERIA: "234",
    CountryCode.DRC: "243",
    CountryCode.MADAGASCAR: "261",
    CountryCode.SEYCHELLES: "248",
    CountryCode.CHAD: "235",
    CountryCode.GABON: "241",
    CountryCode.NIGER: "227",
    CountryCode.CONGO_BRAZZAVILLE: "242",
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class SubscriberInfo:
    """Subscriber information for transactions."""
    msisdn: str  # Phone number in international format
    country_code: CountryCode

    def to_dict(self) -> Dict[str, str]:
        """Convert to API format."""
        return {
            "msisdn": self.msisdn,
            "country": self.country_code.value,
        }


@dataclass
class TransactionMetadata:
    """Transaction metadata for IF.bus events."""
    transaction_id: str
    reference_id: str
    amount: float
    currency: Currency
    country: CountryCode
    transaction_type: TransactionType
    subscriber: SubscriberInfo
    status: TransactionStatus
    description: str
    request_timestamp: datetime
    completion_timestamp: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["subscriber"] = self.subscriber.to_dict()
        data["country"] = self.country.value
        data["currency"] = self.currency.value
        data["transaction_type"] = self.transaction_type.value
        data["status"] = self.status.value
        data["request_timestamp"] = self.request_timestamp.isoformat()
        if self.completion_timestamp:
            data["completion_timestamp"] = self.completion_timestamp.isoformat()
        return data


@dataclass
class KYCInfo:
    """KYC (Know Your Customer) information."""
    msisdn: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    id_number: Optional[str] = None
    id_type: Optional[str] = None
    registration_date: Optional[str] = None
    is_verified: bool = False
    grade: Optional[str] = None  # Customer grade/tier

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


# ============================================================================
# Custom Exceptions
# ============================================================================

class AirtelMoneyError(Exception):
    """Base exception for Airtel Money adapter."""
    pass


class AuthenticationError(AirtelMoneyError):
    """Authentication/authorization error."""
    pass


class APIError(AirtelMoneyError):
    """API request error."""
    pass


class ValidationError(AirtelMoneyError):
    """Data validation error."""
    pass


class CallbackError(AirtelMoneyError):
    """Callback processing error."""
    pass


class InsufficientBalanceError(AirtelMoneyError):
    """Insufficient balance error."""
    pass


# ============================================================================
# Airtel Money Adapter
# ============================================================================

class AirtelMoneyAdapter:
    """
    Production-ready adapter for Airtel Money APIs.

    Implements:
    - OAuth2 client credentials authentication with token caching
    - Collections API (USSD Push payment)
    - Disbursements API (money transfer/payout)
    - Account API (balance inquiry, KYC verification)
    - Transaction status monitoring
    - IF.bus event emission
    - Comprehensive error handling with retry logic

    Example:
        adapter = AirtelMoneyAdapter(
            client_id="your-client-id",
            client_secret="your-client-secret",
            country=CountryCode.KENYA,
            environment="production"
        )

        # USSD Push collection
        result = adapter.ussd_push(
            amount=1000.00,
            msisdn="254712345678",
            reference="ORDER-123",
            description="Payment for Order #123"
        )
    """

    # API Endpoints
    SANDBOX_BASE_URL = "https://openapiuat.airtel.africa"
    PRODUCTION_BASE_URL = "https://openapi.airtel.africa"

    OAUTH_ENDPOINT = "/auth/oauth2/token"
    COLLECTION_ENDPOINT = "/merchant/v1/payments"
    DISBURSEMENT_ENDPOINT = "/standard/v1/disbursements"
    TRANSACTION_STATUS_ENDPOINT = "/standard/v1/payments"
    BALANCE_ENDPOINT = "/standard/v1/users/balance"
    KYC_ENDPOINT = "/standard/v1/users"
    REFUND_ENDPOINT = "/standard/v1/payments/refund"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        country: CountryCode = CountryCode.KENYA,
        environment: str = "production",
        pin: Optional[str] = None,
        callback_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize Airtel Money adapter.

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            country: CountryCode enum value
            environment: "production" or "sandbox"
            pin: Optional PIN for certain operations
            callback_url: Base URL for webhooks
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            logger: Optional logger instance

        Raises:
            ValidationError: If required credentials are missing
        """
        if not all([client_id, client_secret]):
            raise ValidationError("client_id and client_secret are required")

        self.client_id = client_id
        self.client_secret = client_secret
        self.country = country
        self.environment = environment
        self.pin = pin
        self.callback_url = callback_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logger or logging.getLogger(__name__)

        # Determine base URL
        if environment == "sandbox":
            self.base_url = self.SANDBOX_BASE_URL
        else:
            self.base_url = self.PRODUCTION_BASE_URL

        # Authentication state
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.session = self._configure_session()

        # Get default currency for country
        self.default_currency = COUNTRY_CURRENCY_MAP.get(country, Currency.KES)

        self.logger.info(
            f"Initialized Airtel Money adapter for {country.value} in {environment}"
        )

    def _configure_session(self) -> requests.Session:
        """
        Configure requests session with retry strategy.

        Returns:
            Configured requests.Session with automatic retries
        """
        session = requests.Session()

        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    # ========================================================================
    # Authentication
    # ========================================================================

    def _get_access_token(self) -> str:
        """
        Get valid OAuth2 access token using client credentials flow.

        IF.bus event: airtel.auth.token_acquired

        Returns:
            Valid access token string

        Raises:
            AuthenticationError: If token acquisition fails
        """
        # Return cached token if still valid
        if self.access_token and self.token_expiry:
            if datetime.utcnow() < self.token_expiry - timedelta(seconds=60):
                return self.access_token

        url = f"{self.base_url}{self.OAUTH_ENDPOINT}"

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
        }

        try:
            self.logger.debug(f"Requesting OAuth2 token from {url}")

            ft_debug_log_request(
                self.logger,
                "airtel_money",
                url,
                {"method": "POST", "headers": headers, "body": payload},
            )

            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            ft_debug_log_response(
                self.logger,
                "airtel_money",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

            data = response.json()

            # Check for error in response
            if "error" in data:
                raise AuthenticationError(
                    f"OAuth2 error: {data.get('error_description', data.get('error'))}"
                )

            self.access_token = data.get("access_token")

            if not self.access_token:
                raise AuthenticationError("No access token in response")

            # Set token expiry (typically 3600 seconds)
            expires_in = int(data.get("expires_in", 3600))
            self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)

            # Emit IF.bus event
            self._emit_event(
                event_name="airtel.auth.token_acquired",
                data={
                    "success": True,
                    "client_id": self.client_id,
                    "country": self.country.value,
                    "expires_in": expires_in,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            self.logger.info("Successfully obtained Airtel Money access token")
            return self.access_token

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get access token: {e}"
            self.logger.error(error_msg)

            # Emit IF.bus event
            self._emit_event(
                event_name="airtel.auth.token_failed",
                data={
                    "error": str(e),
                    "client_id": self.client_id,
                    "country": self.country.value,
                },
            )
            raise AuthenticationError(error_msg) from e

    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Build authorization headers for API requests.

        Returns:
            Headers dictionary

        Raises:
            AuthenticationError: If token retrieval fails
        """
        access_token = self._get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "X-Country": self.country.value,
            "X-Currency": self.default_currency.value,
        }

        return headers

    # ========================================================================
    # Collections API (USSD Push)
    # ========================================================================

    def ussd_push(
        self,
        amount: float,
        msisdn: str,
        reference: str,
        description: str = "Payment",
        callback_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Initiate USSD Push payment collection from subscriber.

        IF.bus events:
        - airtel.collection.initiated
        - airtel.collection.success / airtel.collection.failed

        Args:
            amount: Transaction amount
            msisdn: Subscriber phone number (international format)
            reference: Unique transaction reference
            description: Transaction description
            callback_url: Optional callback URL for async notification

        Returns:
            Response with transaction ID and status

        Raises:
            ValidationError: If input validation fails
            APIError: If API request fails

        Example:
            >>> result = adapter.ussd_push(
            ...     amount=1000.00,
            ...     msisdn="254712345678",
            ...     reference="ORDER-123",
            ...     description="Payment for Order #123"
            ... )
            >>> print(result['transaction_id'])
        """
        # Validate input
        if amount <= 0:
            raise ValidationError(f"Invalid amount: {amount}")

        if not msisdn:
            raise ValidationError("msisdn is required")

        if not reference:
            raise ValidationError("reference is required")

        # Normalize phone number
        msisdn = self._normalize_phone_number(msisdn)

        url = f"{self.base_url}{self.COLLECTION_ENDPOINT}"

        # Generate unique transaction ID
        transaction_id = str(uuid.uuid4())

        payload = {
            "reference": reference,
            "subscriber": {
                "country": self.country.value,
                "currency": self.default_currency.value,
                "msisdn": msisdn,
            },
            "transaction": {
                "amount": float(amount),
                "country": self.country.value,
                "currency": self.default_currency.value,
                "id": transaction_id,
            },
        }

        headers = self._get_auth_headers()

        # Emit IF.bus event
        self._emit_event(
            event_name="airtel.collection.initiated",
            data={
                "transaction_id": transaction_id,
                "reference": reference,
                "amount": amount,
                "currency": self.default_currency.value,
                "msisdn": msisdn,
                "description": description,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        try:
            self.logger.debug(f"Initiating USSD Push for {msisdn}, Amount: {amount}")

            ft_debug_log_request(
                self.logger,
                "airtel_money",
                url,
                {"method": "POST", "headers": headers, "body": payload},
            )

            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            ft_debug_log_response(
                self.logger,
                "airtel_money",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

            result = response.json()

            # Check for error in response
            if result.get("status", {}).get("code") != "200":
                error_msg = result.get("status", {}).get("message", "Unknown error")

                # Emit IF.bus event
                self._emit_event(
                    event_name="airtel.collection.failed",
                    data={
                        "transaction_id": transaction_id,
                        "reference": reference,
                        "error": error_msg,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

                raise APIError(f"USSD Push failed: {error_msg}")

            # Extract transaction data
            data = result.get("data", {})
            airtel_transaction_id = data.get("transaction", {}).get("id", transaction_id)

            response_data = {
                "transaction_id": airtel_transaction_id,
                "reference": reference,
                "status": TransactionStatus.PENDING.value,
                "amount": amount,
                "currency": self.default_currency.value,
                "msisdn": msisdn,
                "created_at": datetime.utcnow().isoformat(),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="airtel.collection.success",
                data=response_data,
            )

            self.logger.info(f"USSD Push initiated successfully: {airtel_transaction_id}")
            return response_data

        except requests.exceptions.RequestException as e:
            error_msg = f"USSD Push API call failed: {e}"
            self.logger.error(error_msg)

            # Emit IF.bus event
            self._emit_event(
                event_name="airtel.collection.failed",
                data={
                    "transaction_id": transaction_id,
                    "reference": reference,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            raise APIError(error_msg) from e

    def get_collection_status(self, transaction_id: str) -> Dict[str, Any]:
        """
        Check status of collection transaction.

        IF.bus event: airtel.collection.status_checked

        Args:
            transaction_id: Airtel Money transaction ID

        Returns:
            Transaction status information

        Raises:
            APIError: If status check fails

        Example:
            >>> status = adapter.get_collection_status("AM-12345-67890")
            >>> print(status['status'])
        """
        url = f"{self.base_url}{self.TRANSACTION_STATUS_ENDPOINT}/{transaction_id}"

        headers = self._get_auth_headers()

        try:
            self.logger.debug(f"Checking collection status for {transaction_id}")

            ft_debug_log_request(
                self.logger,
                "airtel_money",
                url,
                {"method": "GET", "headers": headers},
            )

            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
            )

            ft_debug_log_response(
                self.logger,
                "airtel_money",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

            result = response.json()

            # Parse response
            data = result.get("data", {})
            transaction = data.get("transaction", {})

            status_code = result.get("status", {}).get("code")
            status_message = result.get("status", {}).get("message", "")

            # Map Airtel status to standard format
            status = TransactionStatus.PENDING
            if status_code == "200":
                if "success" in status_message.lower():
                    status = TransactionStatus.SUCCESS
                elif "failed" in status_message.lower():
                    status = TransactionStatus.FAILED
            elif status_code in ["400", "404", "500"]:
                status = TransactionStatus.FAILED

            response_data = {
                "transaction_id": transaction_id,
                "status": status.value,
                "amount": transaction.get("amount"),
                "currency": transaction.get("currency"),
                "msisdn": transaction.get("msisdn"),
                "status_code": status_code,
                "status_message": status_message,
                "airtel_reference": transaction.get("airtel_money_id"),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="airtel.collection.status_checked",
                data=response_data,
            )

            return response_data

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to check collection status: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg) from e

    # ========================================================================
    # Disbursements API (Money Transfer)
    # ========================================================================

    def transfer(
        self,
        amount: float,
        msisdn: str,
        reference: str,
        description: str = "Transfer",
        pin: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transfer money to subscriber (Disbursement).

        IF.bus events:
        - airtel.disbursement.initiated
        - airtel.disbursement.success / airtel.disbursement.failed

        Args:
            amount: Transfer amount
            msisdn: Recipient phone number (international format)
            reference: Unique transaction reference
            description: Transfer description
            pin: Optional PIN for authorization (if not set in init)

        Returns:
            Response with transaction ID and status

        Raises:
            ValidationError: If input validation fails
            APIError: If API request fails

        Example:
            >>> result = adapter.transfer(
            ...     amount=5000.00,
            ...     msisdn="254712345678",
            ...     reference="LOAN-DISB-456",
            ...     description="Loan disbursement"
            ... )
            >>> print(result['transaction_id'])
        """
        # Validate input
        if amount <= 0:
            raise ValidationError(f"Invalid amount: {amount}")

        if not msisdn:
            raise ValidationError("msisdn is required")

        if not reference:
            raise ValidationError("reference is required")

        # Use provided PIN or instance PIN
        auth_pin = pin or self.pin
        if not auth_pin:
            raise ValidationError("PIN is required for disbursements")

        # Normalize phone number
        msisdn = self._normalize_phone_number(msisdn)

        url = f"{self.base_url}{self.DISBURSEMENT_ENDPOINT}"

        # Generate unique transaction ID
        transaction_id = str(uuid.uuid4())

        payload = {
            "payee": {
                "msisdn": msisdn,
            },
            "reference": reference,
            "pin": auth_pin,
            "transaction": {
                "amount": float(amount),
                "id": transaction_id,
            },
        }

        headers = self._get_auth_headers()

        # Emit IF.bus event
        self._emit_event(
            event_name="airtel.disbursement.initiated",
            data={
                "transaction_id": transaction_id,
                "reference": reference,
                "amount": amount,
                "currency": self.default_currency.value,
                "msisdn": msisdn,
                "description": description,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        try:
            self.logger.debug(f"Initiating disbursement to {msisdn}, Amount: {amount}")

            ft_debug_log_request(
                self.logger,
                "airtel_money",
                url,
                {"method": "POST", "headers": headers, "body": payload},
            )

            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            ft_debug_log_response(
                self.logger,
                "airtel_money",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

            result = response.json()

            # Check for error in response
            status_code = result.get("status", {}).get("code")
            status_message = result.get("status", {}).get("message", "Unknown error")

            if status_code != "200":
                # Emit IF.bus event
                self._emit_event(
                    event_name="airtel.disbursement.failed",
                    data={
                        "transaction_id": transaction_id,
                        "reference": reference,
                        "error": status_message,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

                # Check for specific error types
                if "insufficient" in status_message.lower():
                    raise InsufficientBalanceError(f"Disbursement failed: {status_message}")

                raise APIError(f"Disbursement failed: {status_message}")

            # Extract transaction data
            data = result.get("data", {})
            airtel_transaction_id = data.get("transaction", {}).get("id", transaction_id)

            response_data = {
                "transaction_id": airtel_transaction_id,
                "reference": reference,
                "status": TransactionStatus.SUCCESS.value,
                "amount": amount,
                "currency": self.default_currency.value,
                "msisdn": msisdn,
                "created_at": datetime.utcnow().isoformat(),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="airtel.disbursement.success",
                data=response_data,
            )

            self.logger.info(f"Disbursement completed successfully: {airtel_transaction_id}")
            return response_data

        except requests.exceptions.RequestException as e:
            error_msg = f"Disbursement API call failed: {e}"
            self.logger.error(error_msg)

            # Emit IF.bus event
            self._emit_event(
                event_name="airtel.disbursement.failed",
                data={
                    "transaction_id": transaction_id,
                    "reference": reference,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            raise APIError(error_msg) from e

    def get_disbursement_status(self, transaction_id: str) -> Dict[str, Any]:
        """
        Check status of disbursement transaction.

        IF.bus event: airtel.disbursement.status_checked

        Args:
            transaction_id: Airtel Money transaction ID

        Returns:
            Transaction status information

        Raises:
            APIError: If status check fails
        """
        url = f"{self.base_url}{self.TRANSACTION_STATUS_ENDPOINT}/{transaction_id}"

        headers = self._get_auth_headers()

        try:
            self.logger.debug(f"Checking disbursement status for {transaction_id}")

            ft_debug_log_request(
                self.logger,
                "airtel_money",
                url,
                {"method": "GET", "headers": headers},
            )

            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
            )

            ft_debug_log_response(
                self.logger,
                "airtel_money",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

            result = response.json()

            # Parse response
            data = result.get("data", {})
            transaction = data.get("transaction", {})

            status_code = result.get("status", {}).get("code")
            status_message = result.get("status", {}).get("message", "")

            # Map Airtel status
            status = TransactionStatus.PENDING
            if status_code == "200":
                status = TransactionStatus.SUCCESS
            elif status_code in ["400", "404", "500"]:
                status = TransactionStatus.FAILED

            response_data = {
                "transaction_id": transaction_id,
                "status": status.value,
                "amount": transaction.get("amount"),
                "currency": transaction.get("currency"),
                "msisdn": transaction.get("msisdn"),
                "status_code": status_code,
                "status_message": status_message,
                "airtel_reference": transaction.get("airtel_money_id"),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="airtel.disbursement.status_checked",
                data=response_data,
            )

            return response_data

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to check disbursement status: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg) from e

    # ========================================================================
    # Account API
    # ========================================================================

    def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance.

        IF.bus event: airtel.account.balance_checked

        Returns:
            Balance information

        Raises:
            APIError: If balance check fails

        Example:
            >>> balance = adapter.get_balance()
            >>> print(f"Balance: {balance['amount']} {balance['currency']}")
        """
        url = f"{self.base_url}{self.BALANCE_ENDPOINT}"

        headers = self._get_auth_headers()

        try:
            self.logger.debug("Checking account balance")

            ft_debug_log_request(
                self.logger,
                "airtel_money",
                url,
                {"method": "GET", "headers": headers},
            )

            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
            )

            ft_debug_log_response(
                self.logger,
                "airtel_money",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

            result = response.json()

            # Parse response
            data = result.get("data", {})

            response_data = {
                "balance": float(data.get("balance", 0)),
                "currency": self.default_currency.value,
                "country": self.country.value,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="airtel.account.balance_checked",
                data=response_data,
            )

            self.logger.info(f"Balance checked: {response_data['balance']} {response_data['currency']}")
            return response_data

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to check balance: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg) from e

    def kyc_inquiry(self, msisdn: str) -> KYCInfo:
        """
        Perform KYC inquiry for subscriber.

        IF.bus event: airtel.kyc.verified

        Args:
            msisdn: Subscriber phone number (international format)

        Returns:
            KYCInfo object with subscriber details

        Raises:
            APIError: If KYC inquiry fails

        Example:
            >>> kyc = adapter.kyc_inquiry("254712345678")
            >>> print(f"Name: {kyc.full_name}")
            >>> print(f"Verified: {kyc.is_verified}")
        """
        # Normalize phone number
        msisdn = self._normalize_phone_number(msisdn)

        url = f"{self.base_url}{self.KYC_ENDPOINT}/{msisdn}"

        headers = self._get_auth_headers()

        try:
            self.logger.debug(f"Performing KYC inquiry for {msisdn}")

            ft_debug_log_request(
                self.logger,
                "airtel_money",
                url,
                {"method": "GET", "headers": headers},
            )

            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
            )

            ft_debug_log_response(
                self.logger,
                "airtel_money",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

            result = response.json()

            # Parse response
            data = result.get("data", {})

            # Check if subscriber is registered
            is_registered = result.get("status", {}).get("code") == "200"

            kyc_info = KYCInfo(
                msisdn=msisdn,
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                full_name=data.get("full_name"),
                date_of_birth=data.get("dob"),
                id_number=data.get("id_number"),
                id_type=data.get("id_type"),
                registration_date=data.get("reg_date"),
                is_verified=is_registered,
                grade=data.get("grade"),
            )

            # Emit IF.bus event
            self._emit_event(
                event_name="airtel.kyc.verified",
                data={
                    "msisdn": msisdn,
                    "is_verified": kyc_info.is_verified,
                    "full_name": kyc_info.full_name,
                    "grade": kyc_info.grade,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            self.logger.info(f"KYC inquiry completed for {msisdn}: Verified={kyc_info.is_verified}")
            return kyc_info

        except requests.exceptions.RequestException as e:
            error_msg = f"KYC inquiry failed: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg) from e

    # ========================================================================
    # Refund API
    # ========================================================================

    def refund_transaction(
        self,
        transaction_id: str,
        reference: str,
    ) -> Dict[str, Any]:
        """
        Refund a transaction.

        IF.bus event: airtel.refund.initiated

        Args:
            transaction_id: Original transaction ID to refund
            reference: Unique refund reference

        Returns:
            Refund response

        Raises:
            APIError: If refund fails

        Example:
            >>> result = adapter.refund_transaction(
            ...     transaction_id="AM-12345-67890",
            ...     reference="REFUND-123"
            ... )
        """
        url = f"{self.base_url}{self.REFUND_ENDPOINT}"

        payload = {
            "transaction": {
                "airtel_money_id": transaction_id,
            },
            "reference": reference,
        }

        headers = self._get_auth_headers()

        try:
            self.logger.debug(f"Initiating refund for transaction {transaction_id}")

            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            result = response.json()

            # Check for error
            status_code = result.get("status", {}).get("code")
            status_message = result.get("status", {}).get("message", "Unknown error")

            if status_code != "200":
                raise APIError(f"Refund failed: {status_message}")

            response_data = {
                "transaction_id": transaction_id,
                "reference": reference,
                "status": "REFUNDED",
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="airtel.refund.initiated",
                data=response_data,
            )

            self.logger.info(f"Refund initiated for {transaction_id}")
            return response_data

        except requests.exceptions.RequestException as e:
            error_msg = f"Refund API call failed: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg) from e

    # ========================================================================
    # Callback Handling
    # ========================================================================

    def verify_callback_signature(
        self,
        webhook_signature: str,
        request_body: str,
    ) -> bool:
        """
        Verify webhook callback signature.

        Airtel Money uses HMAC-SHA256 signature verification.

        Args:
            webhook_signature: X-Signature header value
            request_body: Raw request body bytes/string

        Returns:
            True if signature is valid

        Raises:
            CallbackError: If verification fails
        """
        try:
            # Convert request body to bytes if string
            if isinstance(request_body, str):
                request_body = request_body.encode('utf-8')

            # Compute expected signature
            expected_signature = hmac.new(
                self.client_secret.encode('utf-8'),
                request_body,
                hashlib.sha256,
            ).hexdigest()

            # Compare signatures (constant-time comparison)
            is_valid = hmac.compare_digest(webhook_signature, expected_signature)

            if not is_valid:
                self.logger.warning("Invalid callback signature received")

            return is_valid

        except Exception as e:
            raise CallbackError(f"Signature verification failed: {e}") from e

    def handle_callback(self, callback_data: Dict[str, Any]) -> None:
        """
        Handle transaction notification callback.

        IF.bus event: airtel.callback.received

        Args:
            callback_data: Parsed callback payload

        Raises:
            CallbackError: If callback processing fails
        """
        try:
            transaction = callback_data.get("transaction", {})
            transaction_id = transaction.get("id")
            status = transaction.get("status", {}).get("code")

            # Map status
            if status == "200":
                transaction_status = TransactionStatus.SUCCESS
            elif status in ["400", "500"]:
                transaction_status = TransactionStatus.FAILED
            else:
                transaction_status = TransactionStatus.PENDING

            # Emit IF.bus event
            self._emit_event(
                event_name="airtel.callback.received",
                data={
                    "transaction_id": transaction_id,
                    "status": transaction_status.value,
                    "amount": transaction.get("amount"),
                    "currency": transaction.get("currency"),
                    "msisdn": transaction.get("msisdn"),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            self.logger.info(f"Callback processed: {transaction_id} -> {transaction_status.value}")

        except Exception as e:
            raise CallbackError(f"Failed to handle callback: {e}") from e

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _normalize_phone_number(self, msisdn: str) -> str:
        """
        Normalize phone number to international format.

        Args:
            msisdn: Phone number in various formats

        Returns:
            Normalized phone number

        Raises:
            ValidationError: If phone number is invalid
        """
        # Remove spaces, dashes, and plus sign
        msisdn = msisdn.replace(" ", "").replace("-", "").replace("+", "")

        # Get country prefix
        country_prefix = COUNTRY_PHONE_PREFIXES.get(self.country)

        if not country_prefix:
            return msisdn

        # If number doesn't start with country code, add it
        if not msisdn.startswith(country_prefix):
            # Remove leading zero if present
            if msisdn.startswith("0"):
                msisdn = msisdn[1:]
            msisdn = f"{country_prefix}{msisdn}"

        return msisdn

    def _emit_event(
        self,
        event_name: str,
        data: Dict[str, Any],
    ) -> None:
        """
        Emit IF.bus event.

        This method should be integrated with IF.bus event publishing system.
        In production, connect to actual message bus (Redis Pub/Sub, RabbitMQ, etc).

        Args:
            event_name: Event identifier (e.g., "airtel.collection.success")
            data: Event payload
        """
        event_payload = {
            "event_name": event_name,
            "timestamp": datetime.utcnow().isoformat(),
            "adapter": "airtel_money",
            "country": self.country.value,
            "environment": self.environment,
            "data": data,
        }

        # TODO: Connect to IF.bus event publisher
        # In production: event_bus.publish(event_name, event_payload)

        self.logger.debug(f"IF.bus event: {event_name}", extra={"payload": event_payload})

    def close(self) -> None:
        """Close HTTP session and cleanup resources."""
        if self.session:
            self.session.close()
            self.logger.info("Adapter closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
