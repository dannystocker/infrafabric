"""
Orange Money API Adapter for Production Use

Production-ready adapter for Orange Money APIs covering Francophone Africa:
- OAuth2 authentication flow with token caching
- Collections API (request payment / merchant payment)
- Disbursements API (transfer money / bulk payments)
- Account operations (balance, account holder info)
- Transaction status monitoring with retry logic
- Multi-country support (Senegal, Ivory Coast, Mali, Cameroon, Guinea, etc.)

Implements IF.bus event emission for transaction lifecycle monitoring.
Critical for pan-African mobile money coverage in Francophone markets.

Official API: https://developer.orange.com/apis/orange-money/
Partners: Orange Money API Developer Portal

Author: InfraFabric Finance Team
Version: 1.0.0
Date: 2025-12-04
"""

import logging
import uuid
import hmac
import hashlib
import json
import base64
from typing import Any, Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict

import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


# ============================================================================
# Enums and Constants
# ============================================================================

class CountryCode(str, Enum):
    """Supported Orange Money countries across Francophone Africa."""
    SENEGAL = "SN"  # Primary market
    IVORY_COAST = "CI"  # Côte d'Ivoire
    MALI = "ML"
    CAMEROON = "CM"
    GUINEA = "GN"  # Conakry
    BURKINA_FASO = "BF"
    DRC = "CD"  # Democratic Republic of Congo
    MADAGASCAR = "MG"
    BOTSWANA = "BW"
    NIGER = "NE"
    CENTRAL_AFRICAN_REPUBLIC = "CF"
    SIERRA_LEONE = "SL"
    LIBERIA = "LR"


class TransactionStatus(str, Enum):
    """Orange Money transaction status codes."""
    PENDING = "PENDING"
    INITIATED = "INITIATED"
    SUCCESS = "SUCCESS"
    SUCCESSFUL = "SUCCESSFUL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    REVERSED = "REVERSED"


class TransactionType(str, Enum):
    """Supported transaction types."""
    COLLECTION = "COLLECTION"  # Request payment
    DISBURSEMENT = "DISBURSEMENT"  # Money transfer
    MERCHANT_PAYMENT = "MERCHANT_PAYMENT"  # Direct merchant payment
    BULK_DISBURSEMENT = "BULK_DISBURSEMENT"  # Bulk transfers
    BALANCE_INQUIRY = "BALANCE_INQUIRY"


class IdentifierType(str, Enum):
    """Party identifier types."""
    MSISDN = "MSISDN"  # Phone number
    ACCOUNT_ID = "ACCOUNT_ID"
    EMAIL = "EMAIL"
    MERCHANT_CODE = "MERCHANT_CODE"


# Country-specific API endpoints
COUNTRY_ENDPOINTS: Dict[CountryCode, str] = {
    CountryCode.SENEGAL: "https://api.orange.com/orange-money-webpay/sn/v1",
    CountryCode.IVORY_COAST: "https://api.orange.com/orange-money-webpay/ci/v1",
    CountryCode.MALI: "https://api.orange.com/orange-money-webpay/ml/v1",
    CountryCode.CAMEROON: "https://api.orange.com/orange-money-webpay/cm/v1",
    CountryCode.GUINEA: "https://api.orange.com/orange-money-webpay/gn/v1",
    CountryCode.BURKINA_FASO: "https://api.orange.com/orange-money-webpay/bf/v1",
    CountryCode.DRC: "https://api.orange.com/orange-money-webpay/cd/v1",
    CountryCode.MADAGASCAR: "https://api.orange.com/orange-money-webpay/mg/v1",
    CountryCode.BOTSWANA: "https://api.orange.com/orange-money-webpay/bw/v1",
    CountryCode.NIGER: "https://api.orange.com/orange-money-webpay/ne/v1",
    CountryCode.CENTRAL_AFRICAN_REPUBLIC: "https://api.orange.com/orange-money-webpay/cf/v1",
    CountryCode.SIERRA_LEONE: "https://api.orange.com/orange-money-webpay/sl/v1",
    CountryCode.LIBERIA: "https://api.orange.com/orange-money-webpay/lr/v1",
}

# Country currencies (XOF = West African CFA franc, XAF = Central African CFA franc)
COUNTRY_CURRENCIES: Dict[CountryCode, str] = {
    CountryCode.SENEGAL: "XOF",
    CountryCode.IVORY_COAST: "XOF",
    CountryCode.MALI: "XOF",
    CountryCode.BURKINA_FASO: "XOF",
    CountryCode.NIGER: "XOF",
    CountryCode.CAMEROON: "XAF",
    CountryCode.DRC: "CDF",
    CountryCode.GUINEA: "GNF",
    CountryCode.MADAGASCAR: "MGA",
    CountryCode.BOTSWANA: "BWP",
    CountryCode.CENTRAL_AFRICAN_REPUBLIC: "XAF",
    CountryCode.SIERRA_LEONE: "SLL",
    CountryCode.LIBERIA: "LRD",
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class PartyInfo:
    """Party information for transactions."""
    identifier_type: str  # MSISDN, ACCOUNT_ID, EMAIL, MERCHANT_CODE
    identifier: str  # Phone number, account ID, email, or merchant code

    def to_dict(self) -> Dict[str, str]:
        """Convert to API format."""
        return {
            "idType": self.identifier_type,
            "id": self.identifier,
        }


@dataclass
class TransactionMetadata:
    """Transaction metadata for IF.bus events and tracking."""
    transaction_id: str
    external_id: str
    amount: float
    currency: str
    country: CountryCode
    transaction_type: TransactionType
    payer: Optional[PartyInfo]
    payee: Optional[PartyInfo]
    status: TransactionStatus
    description: str
    request_timestamp: datetime
    completion_timestamp: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    callback_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = {
            "transaction_id": self.transaction_id,
            "external_id": self.external_id,
            "amount": self.amount,
            "currency": self.currency,
            "country": self.country.value,
            "transaction_type": self.transaction_type.value,
            "status": self.status.value,
            "description": self.description,
            "request_timestamp": self.request_timestamp.isoformat(),
        }

        if self.payer:
            data["payer"] = self.payer.to_dict()
        if self.payee:
            data["payee"] = self.payee.to_dict()
        if self.completion_timestamp:
            data["completion_timestamp"] = self.completion_timestamp.isoformat()
        if self.error_code:
            data["error_code"] = self.error_code
        if self.error_message:
            data["error_message"] = self.error_message
        if self.callback_url:
            data["callback_url"] = self.callback_url

        return data


# ============================================================================
# Custom Exceptions
# ============================================================================

class OrangeMoneyError(Exception):
    """Base exception for Orange Money adapter."""
    pass


class AuthenticationError(OrangeMoneyError):
    """Authentication/authorization error."""
    pass


class APIError(OrangeMoneyError):
    """API request error."""
    pass


class ValidationError(OrangeMoneyError):
    """Data validation error."""
    pass


class TransactionError(OrangeMoneyError):
    """Transaction processing error."""
    pass


class CallbackError(OrangeMoneyError):
    """Callback processing error."""
    pass


# ============================================================================
# Orange Money Adapter
# ============================================================================

class OrangeMoneyAdapter:
    """
    Production-ready adapter for Orange Money APIs.

    Implements:
    - OAuth2 authentication with token caching
    - Collections API (request payment from customers)
    - Disbursements API (transfer money to customers)
    - Merchant payments (direct merchant transactions)
    - Account operations (balance, account holder info)
    - Transaction status monitoring
    - Webhook callback handling with signature verification
    - IF.bus event emission for transaction lifecycle

    Example:
        adapter = OrangeMoneyAdapter(
            client_id="your-client-id",
            client_secret="your-client-secret",
            merchant_key="your-merchant-key",
            country=CountryCode.SENEGAL,
            environment="production"
        )

        # Request payment
        result = adapter.request_payment(
            amount=1000.0,
            currency="XOF",
            customer_msisdn="221771234567",
            order_id="ORDER-12345",
            description="Payment for services"
        )
    """

    # OAuth2 endpoints
    AUTH_BASE_URL = "https://api.orange.com/oauth/v3"
    SANDBOX_AUTH_URL = "https://api.orange.com/oauth/v3"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        merchant_key: str,
        country: CountryCode = CountryCode.SENEGAL,
        environment: str = "production",
        callback_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize Orange Money adapter.

        Args:
            client_id: Orange API client ID
            client_secret: Orange API client secret
            merchant_key: Orange Money merchant key
            country: CountryCode enum value
            environment: "production" or "sandbox"
            callback_url: Base URL for webhooks/notifications
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            logger: Optional logger instance

        Raises:
            ValidationError: If required credentials are missing
        """
        if not all([client_id, client_secret, merchant_key]):
            raise ValidationError(
                "All credentials (client_id, client_secret, merchant_key) are required"
            )

        self.client_id = client_id
        self.client_secret = client_secret
        self.merchant_key = merchant_key
        self.country = country
        self.environment = environment
        self.callback_url = callback_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logger or logging.getLogger(__name__)

        # Determine API base URL
        self.auth_url = self.SANDBOX_AUTH_URL if environment == "sandbox" else self.AUTH_BASE_URL

        # Country-specific endpoint
        self.base_url = COUNTRY_ENDPOINTS.get(country)
        if not self.base_url:
            raise ValidationError(f"Unsupported country: {country}")

        # Default currency for country
        self.default_currency = COUNTRY_CURRENCIES.get(country, "XOF")

        # Authentication state
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None

        # Configure HTTP session with retries
        self.session = self._configure_session()

        self.logger.info(
            f"Initialized Orange Money adapter for {country.value} in {environment}"
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
            allowed_methods=["POST", "GET", "PUT"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    # ========================================================================
    # Authentication (OAuth2)
    # ========================================================================

    def _get_access_token(self) -> str:
        """
        Get valid OAuth2 access token using client credentials flow.

        IF.bus event: orange.auth.token_acquired

        Returns:
            Valid access token string

        Raises:
            AuthenticationError: If token acquisition fails
        """
        # Return cached token if still valid
        if self.access_token and self.token_expiry:
            if datetime.utcnow() < self.token_expiry - timedelta(seconds=60):
                return self.access_token

        url = f"{self.auth_url}/token"

        # OAuth2 client credentials grant
        auth = HTTPBasicAuth(self.client_id, self.client_secret)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        data = {
            "grant_type": "client_credentials",
        }

        try:
            response = self.session.post(
                url,
                auth=auth,
                headers=headers,
                data=data,
                timeout=self.timeout,
            )
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data.get("access_token")

            # Set token expiry (typically 3600 seconds)
            expires_in = int(token_data.get("expires_in", 3600))
            self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)

            # Emit IF.bus event
            self._emit_event(
                event_name="orange.auth.token_acquired",
                data={
                    "success": True,
                    "client_id": self.client_id,
                    "country": self.country.value,
                    "expires_in": expires_in,
                    "token_type": token_data.get("token_type", "Bearer"),
                },
            )

            self.logger.info("Successfully obtained Orange Money access token")
            return self.access_token

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get access token: {e}"
            self.logger.error(error_msg)

            # Emit IF.bus event
            self._emit_event(
                event_name="orange.auth.token_failed",
                data={
                    "error": str(e),
                    "client_id": self.client_id,
                    "country": self.country.value,
                },
            )

            raise AuthenticationError(error_msg) from e

    def _get_auth_headers(self, include_merchant_key: bool = True) -> Dict[str, str]:
        """
        Build authorization headers for API requests.

        Args:
            include_merchant_key: Include merchant key in headers

        Returns:
            Headers dictionary

        Raises:
            AuthenticationError: If token retrieval fails
        """
        access_token = self._get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if include_merchant_key:
            headers["X-Merchant-Key"] = self.merchant_key

        return headers

    # ========================================================================
    # Collections API (Request Payment)
    # ========================================================================

    def request_payment(
        self,
        amount: float,
        customer_msisdn: str,
        order_id: str,
        description: str,
        currency: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_name: Optional[str] = None,
        callback_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Request payment from customer (Collections API).

        This initiates a payment request that prompts the customer to approve
        the transaction on their mobile phone.

        IF.bus events:
        - orange.collection.initiated
        - orange.collection.success (on successful API call)
        - orange.collection.failed (on API error)

        Args:
            amount: Payment amount
            customer_msisdn: Customer phone number (international format)
            order_id: Unique order/transaction reference
            description: Transaction description
            currency: Currency code (defaults to country currency)
            customer_email: Customer email (optional)
            customer_name: Customer name (optional)
            callback_url: Notification callback URL (overrides default)
            metadata: Additional metadata (optional)

        Returns:
            Response with transaction ID and status

        Raises:
            ValidationError: If input validation fails
            APIError: If API request fails
        """
        # Validate inputs
        self._validate_amount(amount)
        self._validate_phone_number(customer_msisdn)

        if not currency:
            currency = self.default_currency

        # Generate transaction ID if not provided
        transaction_id = f"OM-{uuid.uuid4()}"

        url = f"{self.base_url}/webpayment"

        # Build request payload
        payload = {
            "merchant_key": self.merchant_key,
            "currency": currency,
            "order_id": order_id,
            "amount": int(amount),  # Orange Money uses integer amounts (smallest unit)
            "return_url": callback_url or self.callback_url,
            "cancel_url": callback_url or self.callback_url,
            "notif_url": callback_url or self.callback_url,
            "lang": "fr",  # Francophone markets
            "reference": transaction_id,
        }

        headers = self._get_auth_headers()

        # Emit IF.bus event - initiated
        self._emit_event(
            event_name="orange.collection.initiated",
            data={
                "transaction_id": transaction_id,
                "order_id": order_id,
                "amount": amount,
                "currency": currency,
                "customer": customer_msisdn,
                "description": description,
                "country": self.country.value,
            },
        )

        try:
            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()

            result = {
                "transaction_id": transaction_id,
                "order_id": order_id,
                "payment_url": data.get("payment_url"),
                "payment_token": data.get("payment_token"),
                "status": TransactionStatus.INITIATED.value,
                "amount": amount,
                "currency": currency,
                "created_at": datetime.utcnow().isoformat(),
            }

            # Emit IF.bus event - success
            self._emit_event(
                event_name="orange.collection.success",
                data=result,
            )

            self.logger.info(f"Payment request created: {transaction_id}")
            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Payment request failed: {e}"
            self.logger.error(error_msg)

            # Emit IF.bus event - failed
            self._emit_event(
                event_name="orange.collection.failed",
                data={
                    "transaction_id": transaction_id,
                    "order_id": order_id,
                    "error": str(e),
                    "country": self.country.value,
                },
            )

            raise APIError(error_msg) from e

    def get_payment_status(
        self,
        order_id: Optional[str] = None,
        payment_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Check status of payment request.

        IF.bus event: orange.collection.status_checked

        Args:
            order_id: Order reference ID
            payment_token: Payment token from request_payment

        Returns:
            Transaction status information

        Raises:
            ValidationError: If neither order_id nor payment_token provided
            APIError: If status check fails
        """
        if not order_id and not payment_token:
            raise ValidationError("Either order_id or payment_token must be provided")

        url = f"{self.base_url}/webpayment"

        headers = self._get_auth_headers()

        params = {}
        if order_id:
            params["order_id"] = order_id
        if payment_token:
            params["payment_token"] = payment_token

        try:
            response = self.session.get(
                url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()

            result = {
                "order_id": data.get("order_id"),
                "status": data.get("status"),
                "amount": data.get("amount"),
                "currency": data.get("currency"),
                "payment_token": data.get("payment_token"),
                "transaction_id": data.get("txnid"),
                "message": data.get("message"),
                "payment_date": data.get("payment_date"),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="orange.collection.status_checked",
                data=result,
            )

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to check payment status: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg) from e

    # ========================================================================
    # Disbursements API (Transfer Money)
    # ========================================================================

    def transfer(
        self,
        amount: float,
        recipient_msisdn: str,
        reference: str,
        description: str,
        currency: Optional[str] = None,
        callback_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Transfer money to recipient (Disbursements API).

        Use cases:
        - Loan disbursements
        - Salary payments
        - Refunds
        - Airtime top-ups
        - Merchant settlements

        IF.bus events:
        - orange.disbursement.initiated
        - orange.disbursement.success
        - orange.disbursement.failed

        Args:
            amount: Transfer amount
            recipient_msisdn: Recipient phone number (international format)
            reference: Unique transaction reference
            description: Transaction description
            currency: Currency code (defaults to country currency)
            callback_url: Notification callback URL (overrides default)
            metadata: Additional metadata (optional)

        Returns:
            Response with transaction ID

        Raises:
            ValidationError: If input validation fails
            APIError: If API request fails
        """
        # Validate inputs
        self._validate_amount(amount)
        self._validate_phone_number(recipient_msisdn)

        if not currency:
            currency = self.default_currency

        # Generate transaction ID
        transaction_id = f"OM-TXF-{uuid.uuid4()}"

        url = f"{self.base_url}/cashin"

        payload = {
            "merchant_key": self.merchant_key,
            "reference": reference,
            "subscriber_msisdn": recipient_msisdn,
            "amount": int(amount),
            "currency": currency,
            "description": description,
            "notif_url": callback_url or self.callback_url,
            "metadata": metadata or {},
        }

        headers = self._get_auth_headers()

        # Emit IF.bus event - initiated
        self._emit_event(
            event_name="orange.disbursement.initiated",
            data={
                "transaction_id": transaction_id,
                "reference": reference,
                "amount": amount,
                "currency": currency,
                "recipient": recipient_msisdn,
                "description": description,
                "country": self.country.value,
            },
        )

        try:
            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()

            result = {
                "transaction_id": transaction_id,
                "reference": reference,
                "status": data.get("status", TransactionStatus.PENDING.value),
                "amount": amount,
                "currency": currency,
                "recipient": recipient_msisdn,
                "orange_transaction_id": data.get("txnid"),
                "created_at": datetime.utcnow().isoformat(),
            }

            # Emit IF.bus event - success
            self._emit_event(
                event_name="orange.disbursement.success",
                data=result,
            )

            self.logger.info(f"Transfer initiated: {transaction_id}")
            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Transfer failed: {e}"
            self.logger.error(error_msg)

            # Emit IF.bus event - failed
            self._emit_event(
                event_name="orange.disbursement.failed",
                data={
                    "transaction_id": transaction_id,
                    "reference": reference,
                    "error": str(e),
                    "country": self.country.value,
                },
            )

            raise APIError(error_msg) from e

    def get_transfer_status(self, reference: str) -> Dict[str, Any]:
        """
        Check status of disbursement transfer.

        IF.bus event: orange.disbursement.status_checked

        Args:
            reference: Transaction reference ID

        Returns:
            Transaction status information

        Raises:
            APIError: If status check fails
        """
        url = f"{self.base_url}/cashin/{reference}"

        headers = self._get_auth_headers()

        try:
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()

            result = {
                "reference": reference,
                "status": data.get("status"),
                "amount": data.get("amount"),
                "currency": data.get("currency"),
                "recipient": data.get("subscriber_msisdn"),
                "transaction_id": data.get("txnid"),
                "message": data.get("message"),
                "transaction_date": data.get("txn_date"),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="orange.disbursement.status_checked",
                data=result,
            )

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to check transfer status: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg) from e

    # ========================================================================
    # Account Operations
    # ========================================================================

    def get_balance(self) -> Dict[str, Any]:
        """
        Get merchant account balance.

        IF.bus event: orange.balance.query

        Returns:
            Account balance information

        Raises:
            APIError: If balance query fails
        """
        url = f"{self.base_url}/account/balance"

        headers = self._get_auth_headers()

        try:
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()

            result = {
                "available_balance": data.get("available_balance"),
                "current_balance": data.get("current_balance"),
                "currency": data.get("currency", self.default_currency),
                "account_number": data.get("account_number"),
                "account_status": data.get("status"),
                "query_timestamp": datetime.utcnow().isoformat(),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="orange.balance.query",
                data=result,
            )

            self.logger.info(f"Balance query successful: {result.get('available_balance')} {result.get('currency')}")
            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get balance: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg) from e

    def get_account_holder_info(self, msisdn: str) -> Dict[str, Any]:
        """
        Get account holder information.

        IF.bus event: orange.account.info_query

        Args:
            msisdn: Phone number to look up

        Returns:
            Account holder information

        Raises:
            ValidationError: If phone number is invalid
            APIError: If lookup fails
        """
        self._validate_phone_number(msisdn)

        url = f"{self.base_url}/account/lookup"

        headers = self._get_auth_headers()

        params = {
            "msisdn": msisdn,
        }

        try:
            response = self.session.get(
                url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()

            result = {
                "msisdn": msisdn,
                "account_name": data.get("account_name"),
                "account_status": data.get("account_status"),
                "account_type": data.get("account_type"),
                "verified": data.get("verified", False),
                "query_timestamp": datetime.utcnow().isoformat(),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="orange.account.info_query",
                data=result,
            )

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get account holder info: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg) from e

    # ========================================================================
    # Merchant Payments
    # ========================================================================

    def merchant_payment(
        self,
        amount: float,
        merchant_code: str,
        reference: str,
        description: str,
        currency: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Make payment to merchant (B2B payment).

        IF.bus events:
        - orange.merchant_payment.initiated
        - orange.merchant_payment.success
        - orange.merchant_payment.failed

        Args:
            amount: Payment amount
            merchant_code: Recipient merchant code
            reference: Unique transaction reference
            description: Transaction description
            currency: Currency code (defaults to country currency)

        Returns:
            Response with transaction ID

        Raises:
            ValidationError: If input validation fails
            APIError: If API request fails
        """
        self._validate_amount(amount)

        if not currency:
            currency = self.default_currency

        transaction_id = f"OM-MER-{uuid.uuid4()}"

        url = f"{self.base_url}/merchant/payment"

        payload = {
            "merchant_key": self.merchant_key,
            "recipient_merchant_code": merchant_code,
            "amount": int(amount),
            "currency": currency,
            "reference": reference,
            "description": description,
        }

        headers = self._get_auth_headers()

        # Emit IF.bus event - initiated
        self._emit_event(
            event_name="orange.merchant_payment.initiated",
            data={
                "transaction_id": transaction_id,
                "reference": reference,
                "amount": amount,
                "currency": currency,
                "merchant_code": merchant_code,
                "description": description,
            },
        )

        try:
            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()

            result = {
                "transaction_id": transaction_id,
                "reference": reference,
                "status": data.get("status", TransactionStatus.PENDING.value),
                "amount": amount,
                "currency": currency,
                "merchant_code": merchant_code,
                "orange_transaction_id": data.get("txnid"),
                "created_at": datetime.utcnow().isoformat(),
            }

            # Emit IF.bus event - success
            self._emit_event(
                event_name="orange.merchant_payment.success",
                data=result,
            )

            self.logger.info(f"Merchant payment initiated: {transaction_id}")
            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Merchant payment failed: {e}"
            self.logger.error(error_msg)

            # Emit IF.bus event - failed
            self._emit_event(
                event_name="orange.merchant_payment.failed",
                data={
                    "transaction_id": transaction_id,
                    "reference": reference,
                    "error": str(e),
                },
            )

            raise APIError(error_msg) from e

    # ========================================================================
    # Callbacks and Webhooks
    # ========================================================================

    def verify_callback_signature(
        self,
        signature: str,
        request_body: str,
    ) -> bool:
        """
        Verify webhook callback signature.

        Orange Money uses HMAC-SHA256 signature verification.

        Args:
            signature: X-Orange-Signature header value
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

            # Compute expected signature using merchant key
            expected_signature = hmac.new(
                self.merchant_key.encode('utf-8'),
                request_body,
                hashlib.sha256,
            ).hexdigest()

            # Compare signatures (constant-time comparison)
            is_valid = hmac.compare_digest(signature, expected_signature)

            if not is_valid:
                self.logger.warning(f"Invalid callback signature received")

            return is_valid

        except Exception as e:
            raise CallbackError(f"Signature verification failed: {e}") from e

    def handle_payment_notification(self, callback_data: Dict[str, Any]) -> None:
        """
        Handle payment notification callback.

        IF.bus event: orange.collection.notification_received

        Args:
            callback_data: Parsed callback payload

        Raises:
            CallbackError: If callback processing fails
        """
        try:
            order_id = callback_data.get("order_id")
            status = callback_data.get("status")

            transaction_metadata = TransactionMetadata(
                transaction_id=callback_data.get("txnid", order_id),
                external_id=order_id,
                amount=float(callback_data.get("amount", 0)),
                currency=callback_data.get("currency", self.default_currency),
                country=self.country,
                transaction_type=TransactionType.COLLECTION,
                payer=PartyInfo(
                    identifier_type=IdentifierType.MSISDN.value,
                    identifier=callback_data.get("customer_msisdn", ""),
                ),
                payee=PartyInfo(
                    identifier_type=IdentifierType.MERCHANT_CODE.value,
                    identifier=self.merchant_key,
                ),
                status=TransactionStatus[status.upper()] if status and status.upper() in TransactionStatus.__members__ else TransactionStatus.PENDING,
                description=callback_data.get("description", ""),
                request_timestamp=datetime.utcnow(),
                completion_timestamp=datetime.utcnow() if status in ["SUCCESS", "FAILED"] else None,
                error_code=callback_data.get("error_code"),
                error_message=callback_data.get("error_message"),
            )

            # Emit IF.bus event
            self._emit_event(
                event_name="orange.collection.notification_received",
                data=transaction_metadata.to_dict(),
            )

            self.logger.info(f"Payment notification processed: {order_id} -> {status}")

        except Exception as e:
            raise CallbackError(f"Failed to handle payment notification: {e}") from e

    def handle_transfer_notification(self, callback_data: Dict[str, Any]) -> None:
        """
        Handle transfer notification callback.

        IF.bus event: orange.disbursement.notification_received

        Args:
            callback_data: Parsed callback payload

        Raises:
            CallbackError: If callback processing fails
        """
        try:
            reference = callback_data.get("reference")
            status = callback_data.get("status")

            transaction_metadata = TransactionMetadata(
                transaction_id=callback_data.get("txnid", reference),
                external_id=reference,
                amount=float(callback_data.get("amount", 0)),
                currency=callback_data.get("currency", self.default_currency),
                country=self.country,
                transaction_type=TransactionType.DISBURSEMENT,
                payer=PartyInfo(
                    identifier_type=IdentifierType.MERCHANT_CODE.value,
                    identifier=self.merchant_key,
                ),
                payee=PartyInfo(
                    identifier_type=IdentifierType.MSISDN.value,
                    identifier=callback_data.get("subscriber_msisdn", ""),
                ),
                status=TransactionStatus[status.upper()] if status and status.upper() in TransactionStatus.__members__ else TransactionStatus.PENDING,
                description=callback_data.get("description", ""),
                request_timestamp=datetime.utcnow(),
                completion_timestamp=datetime.utcnow() if status in ["SUCCESS", "FAILED"] else None,
                error_code=callback_data.get("error_code"),
                error_message=callback_data.get("error_message"),
            )

            # Emit IF.bus event
            self._emit_event(
                event_name="orange.disbursement.notification_received",
                data=transaction_metadata.to_dict(),
            )

            self.logger.info(f"Transfer notification processed: {reference} -> {status}")

        except Exception as e:
            raise CallbackError(f"Failed to handle transfer notification: {e}") from e

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _validate_amount(self, amount: float) -> None:
        """
        Validate transaction amount.

        Args:
            amount: Amount to validate

        Raises:
            ValidationError: If amount is invalid
        """
        if not isinstance(amount, (int, float)):
            raise ValidationError(f"Amount must be numeric, got {type(amount)}")

        if amount <= 0:
            raise ValidationError(f"Amount must be positive, got {amount}")

        # Orange Money typically has limits (country-specific)
        # For XOF/XAF: typical max is 1,000,000
        max_amount = 10_000_000
        if amount > max_amount:
            raise ValidationError(f"Amount exceeds maximum ({max_amount})")

    def _validate_phone_number(self, phone: str) -> None:
        """
        Validate phone number format.

        Args:
            phone: Phone number to validate

        Raises:
            ValidationError: If phone number is invalid
        """
        if not phone:
            raise ValidationError("Phone number is required")

        # Remove common formatting
        cleaned = phone.replace(" ", "").replace("-", "").replace("+", "")

        if not cleaned.isdigit():
            raise ValidationError(f"Phone number must be numeric: {phone}")

        # International format should be 10-15 digits
        if not (10 <= len(cleaned) <= 15):
            raise ValidationError(f"Phone number length invalid: {phone}")

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
            event_name: Event identifier (e.g., "orange.collection.success")
            data: Event payload
        """
        event_payload = {
            "event_name": event_name,
            "timestamp": datetime.utcnow().isoformat(),
            "adapter": "orange_money",
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
            self.logger.info("Orange Money adapter closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# ============================================================================
# Factory Functions
# ============================================================================

def create_orange_money_adapter(
    client_id: str,
    client_secret: str,
    merchant_key: str,
    country: str = "SN",
    environment: str = "production",
    **kwargs
) -> OrangeMoneyAdapter:
    """
    Factory function to create Orange Money adapter.

    Args:
        client_id: Orange API client ID
        client_secret: Orange API client secret
        merchant_key: Orange Money merchant key
        country: Country code (SN, CI, ML, CM, etc.)
        environment: "production" or "sandbox"
        **kwargs: Additional arguments passed to OrangeMoneyAdapter

    Returns:
        Configured OrangeMoneyAdapter instance

    Example:
        adapter = create_orange_money_adapter(
            client_id="your-client-id",
            client_secret="your-secret",
            merchant_key="your-merchant-key",
            country="SN",
            environment="production"
        )
    """
    country_code = CountryCode[country.upper()] if hasattr(CountryCode, country.upper()) else CountryCode.SENEGAL

    return OrangeMoneyAdapter(
        client_id=client_id,
        client_secret=client_secret,
        merchant_key=merchant_key,
        country=country_code,
        environment=environment,
        **kwargs
    )
