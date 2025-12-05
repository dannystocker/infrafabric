"""
MTN Mobile Money (MoMo) API Adapter

Production-ready adapter for MTN MoMo APIs covering:
- Collections API (request to pay / invoice)
- Disbursements API (money transfer)
- Remittances API (cross-border transfers)
- Transaction status callbacks
- Multi-country support (Uganda, Ghana, Cameroon, DRC, Benin, Guinea, etc.)

Implements OAuth2 authentication with API user creation and management.
Emits IF.bus events for transaction lifecycle monitoring.

Official API: https://momodeveloper.mtn.com/

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

import requests
from requests.auth import HTTPBasicAuth

from fintech_debug_utils import ft_debug_log_request, ft_debug_log_response


# ============================================================================
# Enums and Constants
# ============================================================================

class CountryCode(str, Enum):
    """Supported MTN MoMo countries with API endpoints."""
    UGANDA = "UG"
    GHANA = "GH"
    CAMEROON = "CM"
    IVORY_COAST = "CI"
    DRC = "CD"
    BENIN = "BJ"
    GUINEA = "GN"
    GUINEA_BISSAU = "GW"
    MOZAMBIQUE = "MZ"
    TANZANIA = "TZ"
    RWANDA = "RW"


class TransactionStatus(str, Enum):
    """MTN MoMo transaction status codes."""
    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    PROCESSING = "PROCESSING"


class TransactionType(str, Enum):
    """Supported transaction types."""
    COLLECTION = "COLLECTION"  # Request to pay
    DISBURSEMENT = "DISBURSEMENT"  # Money transfer
    REMITTANCE = "REMITTANCE"  # Cross-border
    DEPOSIT = "DEPOSIT"


class APIProductType(str, Enum):
    """MTN MoMo API products."""
    COLLECTIONS = "collection"
    DISBURSEMENTS = "disbursement"
    REMITTANCES = "remittance"


# Country-specific endpoint mapping
COUNTRY_ENDPOINTS: Dict[CountryCode, str] = {
    CountryCode.UGANDA: "https://openapi.mtn.com/collection/v1_0",
    CountryCode.GHANA: "https://openapi.mtn.com/collection/v1_0",
    CountryCode.CAMEROON: "https://openapi.mtn.com/collection/v1_0",
    CountryCode.IVORY_COAST: "https://openapi.mtn.com/collection/v1_0",
    CountryCode.DRC: "https://openapi.mtn.com/collection/v1_0",
    CountryCode.BENIN: "https://openapi.mtn.com/collection/v1_0",
    CountryCode.GUINEA: "https://openapi.mtn.com/collection/v1_0",
    CountryCode.GUINEA_BISSAU: "https://openapi.mtn.com/collection/v1_0",
    CountryCode.MOZAMBIQUE: "https://openapi.mtn.com/collection/v1_0",
    CountryCode.TANZANIA: "https://openapi.mtn.com/collection/v1_0",
    CountryCode.RWANDA: "https://openapi.mtn.com/collection/v1_0",
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class PartyInfo:
    """Party information for transactions."""
    party_id_type: str  # MSISDN, EMAIL, PARTY_CODE
    party_id: str  # Phone number, email, or party code

    def to_dict(self) -> Dict[str, str]:
        """Convert to API format."""
        return {
            "partyIdType": self.party_id_type,
            "partyId": self.party_id,
        }


@dataclass
class PaymentMetadata:
    """Transaction metadata for IF.bus events."""
    transaction_id: str
    external_id: str
    amount: float
    currency: str
    country: CountryCode
    transaction_type: TransactionType
    payer: PartyInfo
    payee: PartyInfo
    status: TransactionStatus
    description: str
    request_timestamp: datetime
    completion_timestamp: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["payer"] = self.payer.to_dict()
        data["payee"] = self.payee.to_dict()
        data["country"] = self.country.value
        data["transaction_type"] = self.transaction_type.value
        data["status"] = self.status.value
        data["request_timestamp"] = self.request_timestamp.isoformat()
        if self.completion_timestamp:
            data["completion_timestamp"] = self.completion_timestamp.isoformat()
        return data


# ============================================================================
# Custom Exceptions
# ============================================================================

class MTNMoMoError(Exception):
    """Base exception for MTN MoMo adapter."""
    pass


class AuthenticationError(MTNMoMoError):
    """Authentication/authorization error."""
    pass


class APIError(MTNMoMoError):
    """API request error."""
    pass


class ValidationError(MTNMoMoError):
    """Data validation error."""
    pass


class CallbackError(MTNMoMoError):
    """Callback processing error."""
    pass


# ============================================================================
# MTN MoMo Adapter
# ============================================================================

class MTNMoMoAdapter:
    """
    Production-ready adapter for MTN Mobile Money APIs.

    Implements:
    - OAuth2 authentication with token caching
    - Collections API (request to pay)
    - Disbursements API (money transfer)
    - Remittances API (cross-border)
    - Webhook callback handling with signature verification
    - IF.bus event emission

    Example:
        adapter = MTNMoMoAdapter(
            subscription_key="your-subscription-key",
            api_user="your-api-user",
            api_key="your-api-key",
            country=CountryCode.UGANDA
        )

        # Create request to pay
        result = adapter.request_to_pay(
            amount="100.00",
            payer_msisdn="256700123456",
            description="Payment for services"
        )
    """

    def __init__(
        self,
        subscription_key: str,
        api_user: str,
        api_key: str,
        country: CountryCode = CountryCode.UGANDA,
        environment: str = "production",
        callback_url: Optional[str] = None,
        timeout: int = 30,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize MTN MoMo adapter.

        Args:
            subscription_key: MTN subscription key (Ocp-Apim-Subscription-Key)
            api_user: API user identifier
            api_key: API user key
            country: CountryCode enum value
            environment: "production" or "sandbox"
            callback_url: Base URL for webhooks
            timeout: Request timeout in seconds
            logger: Optional logger instance
        """
        self.subscription_key = subscription_key
        self.api_user = api_user
        self.api_key = api_key
        self.country = country
        self.environment = environment
        self.callback_url = callback_url
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)

        # Determine base URL
        if environment == "sandbox":
            self.base_url = "https://sandbox.momodeveloper.mtn.com"
        else:
            self.base_url = COUNTRY_ENDPOINTS.get(country)
            if not self.base_url:
                raise ValidationError(f"Unsupported country: {country}")

        # Authentication state
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.session = requests.Session()

        self.logger.info(
            f"Initialized MTN MoMo adapter for {country.value} in {environment}"
        )

    # ========================================================================
    # Authentication
    # ========================================================================

    def _get_access_token(self) -> str:
        """
        Get valid OAuth2 access token.

        IF.bus event: mtn.momo.auth.token_requested

        Returns:
            Valid access token string

        Raises:
            AuthenticationError: If token acquisition fails
        """
        # Return cached token if still valid
        if self.access_token and self.token_expiry:
            if datetime.utcnow() < self.token_expiry - timedelta(seconds=60):
                return self.access_token

        url = f"{self.base_url}/oauth/v1_0/accesstoken"

        try:
            ft_debug_log_request(
                self.logger,
                "mtn_momo",
                url,
                {
                    "method": "GET",
                    "headers": {"Ocp-Apim-Subscription-Key": self.subscription_key},
                },
            )

            response = self.session.get(
                url,
                auth=HTTPBasicAuth(self.api_user, self.api_key),
                headers={"Ocp-Apim-Subscription-Key": self.subscription_key},
                timeout=self.timeout,
            )

            ft_debug_log_response(
                self.logger,
                "mtn_momo",
                response.status_code,
                response.text,
            )

            response.raise_for_status()

            data = response.json()
            self.access_token = data.get("access_token")

            # Set token expiry (typically 3600 seconds)
            expires_in = int(data.get("expires_in", 3600))
            self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)

            # Emit IF.bus event
            self._emit_event(
                event_name="mtn.momo.auth.token_requested",
                data={
                    "success": True,
                    "user": self.api_user,
                    "country": self.country.value,
                    "expires_in": expires_in,
                },
            )

            return self.access_token

        except requests.exceptions.RequestException as e:
            # Emit IF.bus event
            self._emit_event(
                event_name="mtn.momo.auth.token_failed",
                data={
                    "error": str(e),
                    "user": self.api_user,
                    "country": self.country.value,
                },
            )
            raise AuthenticationError(f"Failed to get access token: {e}") from e

    def create_api_user(self, provisioning_key: str, reference_id: Optional[str] = None) -> str:
        """
        Create API user (required for new integration).

        IF.bus event: mtn.momo.auth.api_user_created

        Args:
            provisioning_key: Provisioning key from MTN
            reference_id: Optional reference ID (generated if not provided)

        Returns:
            Created API user ID

        Raises:
            AuthenticationError: If user creation fails
        """
        if not reference_id:
            reference_id = str(uuid.uuid4())

        url = f"{self.base_url}/v1_0/apiuser"

        payload = {
            "provisioningServiceCallBackUrl": self.callback_url,
        }

        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "X-Reference-Id": reference_id,
            "Content-Type": "application/json",
        }

        try:
            ft_debug_log_request(
                self.logger,
                "mtn_momo",
                url,
                {
                    "method": "POST",
                    "headers": headers,
                    "body": payload,
                },
            )

            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                auth=HTTPBasicAuth(provisioning_key, provisioning_key),
                timeout=self.timeout,
            )

            ft_debug_log_response(
                self.logger,
                "mtn_momo",
                response.status_code,
                response.text,
            )

            response.raise_for_status()

            # Extract user ID from response (typically in location header or response)
            user_id = reference_id  # Use reference ID as user ID

            # Emit IF.bus event
            self._emit_event(
                event_name="mtn.momo.auth.api_user_created",
                data={
                    "user_id": user_id,
                    "reference_id": reference_id,
                    "country": self.country.value,
                    "callback_url": self.callback_url,
                },
            )

            return user_id

        except requests.exceptions.RequestException as e:
            # Emit IF.bus event
            self._emit_event(
                event_name="mtn.momo.auth.api_user_creation_failed",
                data={"error": str(e), "reference_id": reference_id},
            )
            raise AuthenticationError(f"Failed to create API user: {e}") from e

    # ========================================================================
    # Collections API (Request to Pay)
    # ========================================================================

    def request_to_pay(
        self,
        amount: str,
        payer_msisdn: str,
        description: str,
        external_id: Optional[str] = None,
        payee_note: Optional[str] = None,
        payer_note: Optional[str] = None,
        currency: str = "EUR",
    ) -> Dict[str, Any]:
        """
        Request payment from mobile subscriber (Collections API).

        IF.bus events:
        - mtn.momo.collection.request_initiated
        - mtn.momo.collection.request_sent

        Args:
            amount: Amount as string (e.g., "100.00")
            payer_msisdn: Payer phone number
            description: Transaction description
            external_id: Idempotency key (generated if not provided)
            payee_note: Note for payee
            payer_note: Note for payer
            currency: Currency code (default: EUR)

        Returns:
            Response with transaction ID

        Raises:
            ValidationError: If input validation fails
            APIError: If API request fails
        """
        if not external_id:
            external_id = str(uuid.uuid4())

        # Validate input
        try:
            float(amount)
        except ValueError:
            raise ValidationError(f"Invalid amount: {amount}")

        url = f"{self.base_url}/v1_0/requesttopay"

        payload = {
            "amount": amount,
            "currency": currency,
            "externalId": external_id,
            "payer": {"partyIdType": "MSISDN", "partyId": payer_msisdn},
            "payerMessage": payer_note or "Payment request",
            "payeeNote": payee_note or description,
            "description": description,
        }

        headers = self._get_auth_headers(external_id)

        # Emit IF.bus event
        self._emit_event(
            event_name="mtn.momo.collection.request_initiated",
            data={
                "external_id": external_id,
                "amount": amount,
                "currency": currency,
                "payer": payer_msisdn,
                "description": description,
            },
        )

        try:
            ft_debug_log_request(
                self.logger,
                "mtn_momo",
                url,
                {
                    "method": "POST",
                    "headers": headers,
                    "body": payload,
                },
            )

            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            ft_debug_log_response(
                self.logger,
                "mtn_momo",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

            # Extract transaction ID from response
            transaction_id = response.headers.get(
                "X-Reference-Id",
                external_id
            )

            result = {
                "transaction_id": transaction_id,
                "external_id": external_id,
                "status": "PENDING",
                "created_at": datetime.utcnow().isoformat(),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="mtn.momo.collection.request_sent",
                data=result,
            )

            self.logger.info(f"Collection request sent: {transaction_id}")
            return result

        except requests.exceptions.RequestException as e:
            # Emit IF.bus event
            self._emit_event(
                event_name="mtn.momo.collection.request_failed",
                data={
                    "external_id": external_id,
                    "error": str(e),
                },
            )
            raise APIError(f"Collection request failed: {e}") from e

    def check_collection_status(self, reference_id: str) -> Dict[str, Any]:
        """
        Check status of collection request.

        IF.bus event: mtn.momo.collection.status_checked

        Args:
            reference_id: Transaction reference ID

        Returns:
            Transaction status information

        Raises:
            APIError: If status check fails
        """
        url = f"{self.base_url}/v1_0/requesttopay/{reference_id}"

        headers = self._get_auth_headers()

        try:
            ft_debug_log_request(
                self.logger,
                "mtn_momo",
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
                "mtn_momo",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

            data = response.json()

            # Map API response to standard format
            result = {
                "transaction_id": reference_id,
                "status": data.get("status"),
                "amount": data.get("amount"),
                "currency": data.get("currency"),
                "payer": data.get("payer", {}).get("partyId"),
                "reason_code": data.get("reason", {}).get("code"),
                "reason_message": data.get("reason", {}).get("message"),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="mtn.momo.collection.status_checked",
                data=result,
            )

            return result

        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to check collection status: {e}") from e

    # ========================================================================
    # Disbursements API (Money Transfer)
    # ========================================================================

    def transfer_money(
        self,
        amount: str,
        recipient_msisdn: str,
        description: str,
        external_id: Optional[str] = None,
        payee_note: Optional[str] = None,
        payer_note: Optional[str] = None,
        currency: str = "EUR",
    ) -> Dict[str, Any]:
        """
        Transfer money to subscriber (Disbursements API).

        IF.bus events:
        - mtn.momo.disbursement.transfer_initiated
        - mtn.momo.disbursement.transfer_sent

        Args:
            amount: Transfer amount as string
            recipient_msisdn: Recipient phone number
            description: Transaction description
            external_id: Idempotency key (generated if not provided)
            payee_note: Note for payee
            payer_note: Note for payer
            currency: Currency code (default: EUR)

        Returns:
            Response with transaction ID

        Raises:
            ValidationError: If input validation fails
            APIError: If API request fails
        """
        if not external_id:
            external_id = str(uuid.uuid4())

        # Validate input
        try:
            float(amount)
        except ValueError:
            raise ValidationError(f"Invalid amount: {amount}")

        url = f"{self.base_url}/v1_0/transfer"

        payload = {
            "amount": amount,
            "currency": currency,
            "externalId": external_id,
            "payee": {"partyIdType": "MSISDN", "partyId": recipient_msisdn},
            "payerMessage": payer_note or "Money transfer",
            "payeeNote": payee_note or description,
            "description": description,
        }

        headers = self._get_auth_headers(external_id)

        # Emit IF.bus event
        self._emit_event(
            event_name="mtn.momo.disbursement.transfer_initiated",
            data={
                "external_id": external_id,
                "amount": amount,
                "currency": currency,
                "recipient": recipient_msisdn,
                "description": description,
            },
        )

        try:
            ft_debug_log_request(
                self.logger,
                "mtn_momo",
                url,
                {
                    "method": "POST",
                    "headers": headers,
                    "body": payload,
                },
            )

            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            ft_debug_log_response(
                self.logger,
                "mtn_momo",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

            transaction_id = response.headers.get(
                "X-Reference-Id",
                external_id
            )

            result = {
                "transaction_id": transaction_id,
                "external_id": external_id,
                "status": "PENDING",
                "created_at": datetime.utcnow().isoformat(),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="mtn.momo.disbursement.transfer_sent",
                data=result,
            )

            self.logger.info(f"Transfer initiated: {transaction_id}")
            return result

        except requests.exceptions.RequestException as e:
            # Emit IF.bus event
            self._emit_event(
                event_name="mtn.momo.disbursement.transfer_failed",
                data={
                    "external_id": external_id,
                    "error": str(e),
                },
            )
            raise APIError(f"Transfer failed: {e}") from e

    def check_transfer_status(self, reference_id: str) -> Dict[str, Any]:
        """
        Check status of disbursement transfer.

        IF.bus event: mtn.momo.disbursement.status_checked

        Args:
            reference_id: Transaction reference ID

        Returns:
            Transaction status information

        Raises:
            APIError: If status check fails
        """
        url = f"{self.base_url}/v1_0/transfer/{reference_id}"

        headers = self._get_auth_headers()

        try:
            ft_debug_log_request(
                self.logger,
                "mtn_momo",
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
                "mtn_momo",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

            data = response.json()

            result = {
                "transaction_id": reference_id,
                "status": data.get("status"),
                "amount": data.get("amount"),
                "currency": data.get("currency"),
                "payee": data.get("payee", {}).get("partyId"),
                "reason_code": data.get("reason", {}).get("code"),
                "reason_message": data.get("reason", {}).get("message"),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="mtn.momo.disbursement.status_checked",
                data=result,
            )

            return result

        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to check transfer status: {e}") from e

    # ========================================================================
    # Remittances API (Cross-border)
    # ========================================================================

    def send_remittance(
        self,
        amount: str,
        recipient_msisdn: str,
        recipient_country: CountryCode,
        description: str,
        external_id: Optional[str] = None,
        sender_currency: str = "EUR",
        recipient_currency: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send cross-border remittance (Remittances API).

        IF.bus events:
        - mtn.momo.remittance.transfer_initiated
        - mtn.momo.remittance.transfer_sent

        Args:
            amount: Remittance amount as string
            recipient_msisdn: Recipient phone number
            recipient_country: Destination country code
            description: Transaction description
            external_id: Idempotency key (generated if not provided)
            sender_currency: Currency of sender (default: EUR)
            recipient_currency: Currency at recipient (auto-detected if not provided)

        Returns:
            Response with transaction ID

        Raises:
            ValidationError: If input validation fails
            APIError: If API request fails
        """
        if not external_id:
            external_id = str(uuid.uuid4())

        # Validate input
        try:
            float(amount)
        except ValueError:
            raise ValidationError(f"Invalid amount: {amount}")

        if recipient_country == self.country:
            self.logger.warning(
                "Remittance to same country - consider using transfer instead"
            )

        url = f"{self.base_url}/v1_0/remittance"

        payload = {
            "amount": amount,
            "currency": sender_currency,
            "externalId": external_id,
            "payee": {"partyIdType": "MSISDN", "partyId": recipient_msisdn},
            "payeeNote": description,
            "description": description,
            "recipientCountry": recipient_country.value,
        }

        headers = self._get_auth_headers(external_id)

        # Emit IF.bus event
        self._emit_event(
            event_name="mtn.momo.remittance.transfer_initiated",
            data={
                "external_id": external_id,
                "amount": amount,
                "sender_currency": sender_currency,
                "recipient": recipient_msisdn,
                "recipient_country": recipient_country.value,
                "description": description,
            },
        )

        try:
            ft_debug_log_request(
                self.logger,
                "mtn_momo",
                url,
                {
                    "method": "POST",
                    "headers": headers,
                    "body": payload,
                },
            )

            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            ft_debug_log_response(
                self.logger,
                "mtn_momo",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

            transaction_id = response.headers.get(
                "X-Reference-Id",
                external_id
            )

            result = {
                "transaction_id": transaction_id,
                "external_id": external_id,
                "status": "PENDING",
                "recipient_country": recipient_country.value,
                "created_at": datetime.utcnow().isoformat(),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="mtn.momo.remittance.transfer_sent",
                data=result,
            )

            self.logger.info(f"Remittance sent: {transaction_id}")
            return result

        except requests.exceptions.RequestException as e:
            # Emit IF.bus event
            self._emit_event(
                event_name="mtn.momo.remittance.transfer_failed",
                data={
                    "external_id": external_id,
                    "error": str(e),
                },
            )
            raise APIError(f"Remittance failed: {e}") from e

    def check_remittance_status(self, reference_id: str) -> Dict[str, Any]:
        """
        Check status of remittance transfer.

        IF.bus event: mtn.momo.remittance.status_checked

        Args:
            reference_id: Transaction reference ID

        Returns:
            Transaction status information

        Raises:
            APIError: If status check fails
        """
        url = f"{self.base_url}/v1_0/remittance/{reference_id}"

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
                "transaction_id": reference_id,
                "status": data.get("status"),
                "amount": data.get("amount"),
                "currency": data.get("currency"),
                "payee": data.get("payee", {}).get("partyId"),
                "payee_country": data.get("recipientCountry"),
                "reason_code": data.get("reason", {}).get("code"),
                "reason_message": data.get("reason", {}).get("message"),
            }

            # Emit IF.bus event
            self._emit_event(
                event_name="mtn.momo.remittance.status_checked",
                data=result,
            )

            return result

        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to check remittance status: {e}") from e

    # ========================================================================
    # Callbacks and Webhooks
    # ========================================================================

    def verify_callback_signature(
        self,
        webhook_signature: str,
        request_body: str,
    ) -> bool:
        """
        Verify webhook callback signature.

        MTN uses HMAC-SHA256 signature verification.

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
                self.api_key.encode('utf-8'),
                request_body,
                hashlib.sha256,
            ).hexdigest()

            # Compare signatures (constant-time comparison)
            is_valid = hmac.compare_digest(webhook_signature, expected_signature)

            if not is_valid:
                self.logger.warning(f"Invalid callback signature received")

            return is_valid

        except Exception as e:
            raise CallbackError(f"Signature verification failed: {e}") from e

    def handle_collection_notification(self, callback_data: Dict[str, Any]) -> None:
        """
        Handle collection transaction notification callback.

        IF.bus event: mtn.momo.collection.notification_received

        Args:
            callback_data: Parsed callback payload

        Raises:
            CallbackError: If callback processing fails
        """
        try:
            transaction_id = callback_data.get("externalId")
            status = callback_data.get("status")

            # Map MTN status to standard format
            payment_metadata = PaymentMetadata(
                transaction_id=callback_data.get("transactionId", transaction_id),
                external_id=transaction_id,
                amount=float(callback_data.get("amount", 0)),
                currency=callback_data.get("currency", "EUR"),
                country=self.country,
                transaction_type=TransactionType.COLLECTION,
                payer=PartyInfo(
                    party_id_type="MSISDN",
                    party_id=callback_data.get("payer", {}).get("partyId", ""),
                ),
                payee=PartyInfo(
                    party_id_type="MSISDN",
                    party_id=callback_data.get("payee", {}).get("partyId", ""),
                ),
                status=TransactionStatus[status] if status in TransactionStatus.__members__ else TransactionStatus.PENDING,
                description=callback_data.get("description", ""),
                request_timestamp=datetime.utcnow(),
                completion_timestamp=datetime.utcnow() if status in ["SUCCESSFUL", "FAILED"] else None,
                error_code=callback_data.get("reason", {}).get("code"),
                error_message=callback_data.get("reason", {}).get("message"),
            )

            # Emit IF.bus event
            self._emit_event(
                event_name="mtn.momo.collection.notification_received",
                data=payment_metadata.to_dict(),
            )

            self.logger.info(f"Collection notification processed: {transaction_id} -> {status}")

        except Exception as e:
            raise CallbackError(f"Failed to handle collection notification: {e}") from e

    def handle_disbursement_notification(self, callback_data: Dict[str, Any]) -> None:
        """
        Handle disbursement transaction notification callback.

        IF.bus event: mtn.momo.disbursement.notification_received

        Args:
            callback_data: Parsed callback payload

        Raises:
            CallbackError: If callback processing fails
        """
        try:
            transaction_id = callback_data.get("externalId")
            status = callback_data.get("status")

            payment_metadata = PaymentMetadata(
                transaction_id=callback_data.get("transactionId", transaction_id),
                external_id=transaction_id,
                amount=float(callback_data.get("amount", 0)),
                currency=callback_data.get("currency", "EUR"),
                country=self.country,
                transaction_type=TransactionType.DISBURSEMENT,
                payer=PartyInfo(
                    party_id_type="MSISDN",
                    party_id=callback_data.get("payer", {}).get("partyId", ""),
                ),
                payee=PartyInfo(
                    party_id_type="MSISDN",
                    party_id=callback_data.get("payee", {}).get("partyId", ""),
                ),
                status=TransactionStatus[status] if status in TransactionStatus.__members__ else TransactionStatus.PENDING,
                description=callback_data.get("description", ""),
                request_timestamp=datetime.utcnow(),
                completion_timestamp=datetime.utcnow() if status in ["SUCCESSFUL", "FAILED"] else None,
                error_code=callback_data.get("reason", {}).get("code"),
                error_message=callback_data.get("reason", {}).get("message"),
            )

            # Emit IF.bus event
            self._emit_event(
                event_name="mtn.momo.disbursement.notification_received",
                data=payment_metadata.to_dict(),
            )

            self.logger.info(f"Disbursement notification processed: {transaction_id} -> {status}")

        except Exception as e:
            raise CallbackError(f"Failed to handle disbursement notification: {e}") from e

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _get_auth_headers(self, reference_id: Optional[str] = None) -> Dict[str, str]:
        """
        Build authorization headers for API requests.

        Args:
            reference_id: Optional request reference ID (generated if not provided)

        Returns:
            Headers dictionary

        Raises:
            AuthenticationError: If token retrieval fails
        """
        if not reference_id:
            reference_id = str(uuid.uuid4())

        access_token = self._get_access_token()

        return {
            "Authorization": f"Bearer {access_token}",
            "X-Reference-Id": reference_id,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json",
        }

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
            event_name: Event identifier (e.g., "mtn.momo.collection.request_sent")
            data: Event payload
        """
        event_payload = {
            "event_name": event_name,
            "timestamp": datetime.utcnow().isoformat(),
            "adapter": "mtn_momo",
            "country": self.country.value,
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
