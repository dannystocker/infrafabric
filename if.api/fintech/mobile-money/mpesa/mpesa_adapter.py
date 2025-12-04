"""
M-Pesa Daraja API Adapter for Production Use

This module provides a comprehensive adapter for Safaricom's M-Pesa Daraja API,
handling OAuth2 authentication, STK Push collections, B2C disbursements,
transaction queries, and account balance operations.

Reference: https://developer.safaricom.co.ke/
"""

import os
import json
import base64
import datetime
import logging
from typing import Optional, Dict, Any, Tuple
from enum import Enum
from abc import ABC, abstractmethod

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


# Configure logging
logger = logging.getLogger(__name__)


class Environment(Enum):
    """M-Pesa API environment options."""
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class TransactionStatus(Enum):
    """M-Pesa transaction status codes."""
    SUCCESS = "00000000"
    INSUFFICIENT_FUNDS = "00000001"
    LESS_AMOUNT = "00000002"
    MORE_AMOUNT = "00000003"
    EXEC_TIMEOUT = "00000004"
    INTERNAL_ERROR = "00000005"
    REQUEST_TIMEOUT = "00000006"
    SERVICE_UNAVAILABLE = "00000007"
    THROTTLED = "00000008"
    END_USER_TIMEOUT = "00000009"


class MpesaException(Exception):
    """Base exception for M-Pesa adapter errors."""
    pass


class MpesaAuthException(MpesaException):
    """Raised when authentication fails."""
    pass


class MpesaAPIException(MpesaException):
    """Raised when API call fails."""
    pass


class MpesaEventEmitter:
    """
    Event emitter interface for IF.bus integration.

    Event names emitted:
    - mpesa.auth.token_acquired
    - mpesa.stk_push.initiated
    - mpesa.stk_push.success
    - mpesa.stk_push.failed
    - mpesa.b2c.initiated
    - mpesa.b2c.success
    - mpesa.b2c.failed
    - mpesa.transaction.status_query
    - mpesa.balance.query
    - mpesa.error.occurred
    """

    def emit(self, event_name: str, data: Dict[str, Any]) -> None:
        """
        Emit an IF.bus event.

        Args:
            event_name: Name of the event (e.g., 'mpesa.stk_push.success')
            data: Event payload dictionary
        """
        # This method will be overridden by actual IF.bus implementation
        logger.info(f"Event: {event_name}, Data: {data}")


class MpesaAdapter:
    """
    Production-ready M-Pesa Daraja API adapter.

    Handles all M-Pesa operations including OAuth2 authentication,
    STK Push for collections, B2C for disbursements, and transaction queries.
    """

    # API Endpoints
    SANDBOX_BASE_URL = "https://sandbox.safaricom.co.ke"
    PRODUCTION_BASE_URL = "https://api.safaricom.co.ke"

    OAUTH_ENDPOINT = "/oauth/v1/generate?grant_type=client_credentials"
    STK_PUSH_ENDPOINT = "/mpesa/stkpush/v1/processrequest"
    STK_QUERY_ENDPOINT = "/mpesa/stkpushquery/v1/query"
    B2C_ENDPOINT = "/mpesa/b2c/v1/paymentrequest"
    BALANCE_ENDPOINT = "/mpesa/accountbalance/v1/query"
    TRANSACTION_STATUS_ENDPOINT = "/mpesa/transactionstatus/v1/query"

    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        business_shortcode: str,
        passkey: str,
        environment: Environment = Environment.SANDBOX,
        event_emitter: Optional[MpesaEventEmitter] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize M-Pesa adapter.

        Args:
            consumer_key: Daraja API consumer key
            consumer_secret: Daraja API consumer secret
            business_shortcode: M-Pesa business shortcode
            passkey: M-Pesa online passkey (for STK Push)
            environment: Target environment (sandbox or production)
            event_emitter: Optional IF.bus event emitter
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts

        Raises:
            MpesaException: If required credentials are missing
        """
        if not all([consumer_key, consumer_secret, business_shortcode, passkey]):
            raise MpesaException("All credentials (consumer_key, consumer_secret, business_shortcode, passkey) are required")

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.business_shortcode = business_shortcode
        self.passkey = passkey
        self.environment = environment
        self.event_emitter = event_emitter or MpesaEventEmitter()
        self.timeout = timeout
        self.max_retries = max_retries

        # Set base URL based on environment
        self.base_url = (
            self.PRODUCTION_BASE_URL if environment == Environment.PRODUCTION
            else self.SANDBOX_BASE_URL
        )

        # Cache for access token
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime.datetime] = None

        # Configure session with retries
        self.session = self._configure_session()

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
            allowed_methods=["POST", "GET"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _get_auth_header(self) -> str:
        """
        Generate Base64-encoded authorization header.

        Returns:
            Base64-encoded 'consumer_key:consumer_secret'
        """
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def get_access_token(self) -> str:
        """
        Obtain OAuth2 access token from M-Pesa API.

        Uses cached token if available and not expired.

        Returns:
            Access token string

        Raises:
            MpesaAuthException: If authentication fails
        """
        # Return cached token if still valid
        if self._access_token and self._token_expiry:
            if datetime.datetime.utcnow() < self._token_expiry:
                logger.debug("Using cached access token")
                return self._access_token

        try:
            url = f"{self.base_url}{self.OAUTH_ENDPOINT}"
            headers = {
                "Authorization": self._get_auth_header(),
                "Content-Type": "application/json"
            }

            logger.debug(f"Requesting access token from {url}")

            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            self._access_token = data.get("access_token")

            # Token typically expires in 3600 seconds, store with 5-minute buffer
            expires_in = int(data.get("expires_in", 3600)) - 300
            self._token_expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)

            logger.info("Successfully obtained M-Pesa access token")

            # Emit IF.bus event
            self.event_emitter.emit("mpesa.auth.token_acquired", {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "environment": self.environment.value
            })

            return self._access_token

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to obtain access token: {str(e)}"
            logger.error(error_msg)
            self.event_emitter.emit("mpesa.error.occurred", {
                "error_type": "authentication_failed",
                "message": error_msg
            })
            raise MpesaAuthException(error_msg) from e

    def _get_request_headers(self) -> Dict[str, str]:
        """
        Get headers for authenticated API requests.

        Returns:
            Headers dictionary with Bearer token authorization
        """
        token = self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def _get_timestamp(self) -> str:
        """
        Get current timestamp in M-Pesa format (YYYYMMDDHHmmss).

        Returns:
            Formatted timestamp string
        """
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    def _generate_stk_password(self) -> Tuple[str, str]:
        """
        Generate STK Push password and timestamp.

        Returns:
            Tuple of (password, timestamp)
        """
        timestamp = self._get_timestamp()
        data = f"{self.business_shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(data.encode()).decode()
        return password, timestamp

    def initiate_stk_push(
        self,
        phone_number: str,
        amount: float,
        account_reference: str,
        transaction_desc: str = "M-Pesa payment",
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate STK Push (Lipa Na M-Pesa Online) for payment collection.

        Args:
            phone_number: Customer phone number (254xxxxxxxxx format)
            amount: Transaction amount in KES
            account_reference: Account reference identifier
            transaction_desc: Transaction description
            callback_url: Optional callback URL for async responses

        Returns:
            API response with MerchantRequestID and CheckoutRequestID

        Raises:
            MpesaAPIException: If API call fails

        Example:
            >>> adapter = MpesaAdapter(...)
            >>> result = adapter.initiate_stk_push(
            ...     phone_number="254712345678",
            ...     amount=100.00,
            ...     account_reference="REF123"
            ... )
            >>> print(result['CheckoutRequestID'])
        """
        try:
            password, timestamp = self._generate_stk_password()

            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone_number,
                "PartyB": self.business_shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": callback_url or "https://api.example.com/callback",
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }

            url = f"{self.base_url}{self.STK_PUSH_ENDPOINT}"
            headers = self._get_request_headers()

            logger.debug(f"Initiating STK Push for {phone_number}, Amount: {amount}")

            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            if result.get("ResponseCode") != "0":
                error_msg = result.get("ResponseDescription", "Unknown error")
                raise MpesaAPIException(f"STK Push failed: {error_msg}")

            logger.info(f"STK Push initiated successfully for {phone_number}")

            # Emit IF.bus event
            self.event_emitter.emit("mpesa.stk_push.initiated", {
                "phone_number": phone_number,
                "amount": amount,
                "account_reference": account_reference,
                "merchant_request_id": result.get("MerchantRequestID"),
                "checkout_request_id": result.get("CheckoutRequestID"),
                "timestamp": self._get_timestamp()
            })

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"STK Push API call failed: {str(e)}"
            logger.error(error_msg)
            self.event_emitter.emit("mpesa.error.occurred", {
                "error_type": "stk_push_failed",
                "message": error_msg,
                "phone_number": phone_number
            })
            raise MpesaAPIException(error_msg) from e

    def query_stk_push_status(
        self,
        checkout_request_id: str
    ) -> Dict[str, Any]:
        """
        Query the status of an STK Push request.

        Args:
            checkout_request_id: CheckoutRequestID from initiate_stk_push

        Returns:
            API response with transaction status

        Raises:
            MpesaAPIException: If API call fails

        Example:
            >>> status = adapter.query_stk_push_status("ws_CO_DMZ_abc123")
            >>> print(status['ResultCode'])
        """
        try:
            password, timestamp = self._generate_stk_password()

            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }

            url = f"{self.base_url}{self.STK_QUERY_ENDPOINT}"
            headers = self._get_request_headers()

            logger.debug(f"Querying STK Push status for {checkout_request_id}")

            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            logger.info(f"STK Push status queried for {checkout_request_id}")

            # Emit IF.bus event
            self.event_emitter.emit("mpesa.stk_push.success" if result.get("ResultCode") == "0" else "mpesa.stk_push.failed", {
                "checkout_request_id": checkout_request_id,
                "result_code": result.get("ResultCode"),
                "result_description": result.get("ResultDescription")
            })

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"STK Push status query failed: {str(e)}"
            logger.error(error_msg)
            raise MpesaAPIException(error_msg) from e

    def b2c_payment(
        self,
        phone_number: str,
        amount: float,
        command_id: str = "BusinessPayment",
        remarks: str = "Payment",
        occasion: str = ""
    ) -> Dict[str, Any]:
        """
        Initiate B2C (Business to Customer) payment/disbursement.

        Args:
            phone_number: Customer phone number (254xxxxxxxxx format)
            amount: Transaction amount in KES
            command_id: Transaction command type (BusinessPayment, SalaryPayment, PromotionPayment)
            remarks: Payment remarks
            occasion: Optional occasion/reference

        Returns:
            API response with ConversationID and OriginatorConversationID

        Raises:
            MpesaAPIException: If API call fails

        Example:
            >>> result = adapter.b2c_payment(
            ...     phone_number="254712345678",
            ...     amount=500.00,
            ...     command_id="SalaryPayment"
            ... )
            >>> print(result['ConversationID'])
        """
        try:
            payload = {
                "InitiatorName": "system",
                "SecurityCredential": self._encrypt_security_credential(),
                "CommandID": command_id,
                "Amount": int(amount),
                "PartyA": self.business_shortcode,
                "PartyB": phone_number,
                "Remarks": remarks,
                "QueueTimeOutURL": "https://api.example.com/timeout",
                "ResultURL": "https://api.example.com/result",
                "Occasion": occasion
            }

            url = f"{self.base_url}{self.B2C_ENDPOINT}"
            headers = self._get_request_headers()

            logger.debug(f"Initiating B2C payment for {phone_number}, Amount: {amount}")

            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            if result.get("ResponseCode") != "0":
                error_msg = result.get("ResponseDescription", "Unknown error")
                raise MpesaAPIException(f"B2C payment failed: {error_msg}")

            logger.info(f"B2C payment initiated successfully for {phone_number}")

            # Emit IF.bus event
            self.event_emitter.emit("mpesa.b2c.initiated", {
                "phone_number": phone_number,
                "amount": amount,
                "command_id": command_id,
                "conversation_id": result.get("ConversationID"),
                "originator_conversation_id": result.get("OriginatorConversationID"),
                "timestamp": self._get_timestamp()
            })

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"B2C payment API call failed: {str(e)}"
            logger.error(error_msg)
            self.event_emitter.emit("mpesa.error.occurred", {
                "error_type": "b2c_payment_failed",
                "message": error_msg,
                "phone_number": phone_number
            })
            raise MpesaAPIException(error_msg) from e

    def get_account_balance(self, identifiers: str = "3") -> Dict[str, Any]:
        """
        Query M-Pesa account balance.

        Args:
            identifiers: Account identifier type (typically "3" for M-Pesa)

        Returns:
            API response with account balance information

        Raises:
            MpesaAPIException: If API call fails

        Example:
            >>> balance = adapter.get_account_balance()
            >>> print(balance)
        """
        try:
            payload = {
                "Initiator": "system",
                "SecurityCredential": self._encrypt_security_credential(),
                "CommandID": "GetAccount",
                "PartyA": self.business_shortcode,
                "IdentifierType": identifiers,
                "Remarks": "Balance enquiry",
                "QueueTimeOutURL": "https://api.example.com/timeout",
                "ResultURL": "https://api.example.com/result"
            }

            url = f"{self.base_url}{self.BALANCE_ENDPOINT}"
            headers = self._get_request_headers()

            logger.debug("Querying account balance")

            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            logger.info("Account balance queried successfully")

            # Emit IF.bus event
            self.event_emitter.emit("mpesa.balance.query", {
                "timestamp": self._get_timestamp(),
                "conversation_id": result.get("ConversationID")
            })

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Account balance query failed: {str(e)}"
            logger.error(error_msg)
            raise MpesaAPIException(error_msg) from e

    def query_transaction_status(
        self,
        transaction_id: str,
        party_a: Optional[str] = None,
        identifier_type: str = "1"
    ) -> Dict[str, Any]:
        """
        Query the status of a specific M-Pesa transaction.

        Args:
            transaction_id: M-Pesa transaction ID (MpesaReceiptNumber or CheckoutRequestID)
            party_a: Optional initiating party (defaults to business shortcode)
            identifier_type: Type of identifier (1=MSISDN, 2=TILL, 3=SHORTCODE)

        Returns:
            API response with transaction status details

        Raises:
            MpesaAPIException: If API call fails

        Example:
            >>> status = adapter.query_transaction_status("LHG31AA5695")
            >>> print(status['ResultDescription'])
        """
        try:
            payload = {
                "Initiator": "system",
                "SecurityCredential": self._encrypt_security_credential(),
                "CommandID": "TransactionStatusQuery",
                "TransactionID": transaction_id,
                "PartyA": party_a or self.business_shortcode,
                "IdentifierType": identifier_type,
                "ResultURL": "https://api.example.com/result",
                "QueueTimeOutURL": "https://api.example.com/timeout",
                "Remarks": "Transaction status query",
                "Occasion": ""
            }

            url = f"{self.base_url}{self.TRANSACTION_STATUS_ENDPOINT}"
            headers = self._get_request_headers()

            logger.debug(f"Querying transaction status for {transaction_id}")

            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            logger.info(f"Transaction status queried for {transaction_id}")

            # Emit IF.bus event
            self.event_emitter.emit("mpesa.transaction.status_query", {
                "transaction_id": transaction_id,
                "result_code": result.get("ResultCode"),
                "timestamp": self._get_timestamp()
            })

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Transaction status query failed: {str(e)}"
            logger.error(error_msg)
            raise MpesaAPIException(error_msg) from e

    def _encrypt_security_credential(self) -> str:
        """
        Encrypt security credential using public certificate.

        Note: In production, this should use the actual Safaricom public certificate.
        For now, returns a placeholder that would be replaced with real encryption.

        Returns:
            Encrypted security credential string
        """
        # This is a placeholder. In production, use actual certificate-based encryption
        # Example implementation using cryptography library:
        # from cryptography.hazmat.primitives import serialization
        # from cryptography.hazmat.primitives.asymmetric import padding
        #
        # with open("mpesa_certificate.cer", "rb") as cert_file:
        #     cert = serialization.load_pem_x509_certificate(cert_file.read())
        #     encrypted = cert.public_key().encrypt(
        #         self.consumer_secret.encode(),
        #         padding.PKCS1v15()
        #     )
        #     return base64.b64encode(encrypted).decode()

        logger.warning("Using placeholder security credential encryption. Use actual certificate in production.")
        return base64.b64encode(self.consumer_secret.encode()).decode()

    def close(self) -> None:
        """Close the session and cleanup resources."""
        self.session.close()
        logger.info("M-Pesa adapter session closed")


# Factory function for creating adapter instances
def create_mpesa_adapter(
    environment: str = "sandbox",
    event_emitter: Optional[MpesaEventEmitter] = None
) -> MpesaAdapter:
    """
    Factory function to create M-Pesa adapter from environment variables.

    Environment variables required:
    - MPESA_CONSUMER_KEY
    - MPESA_CONSUMER_SECRET
    - MPESA_BUSINESS_SHORTCODE
    - MPESA_PASSKEY
    - MPESA_ENVIRONMENT (optional, defaults to sandbox)

    Args:
        environment: Override environment (sandbox or production)
        event_emitter: Optional IF.bus event emitter

    Returns:
        Configured MpesaAdapter instance

    Raises:
        MpesaException: If required environment variables are missing
    """
    consumer_key = os.getenv("MPESA_CONSUMER_KEY")
    consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")
    business_shortcode = os.getenv("MPESA_BUSINESS_SHORTCODE")
    passkey = os.getenv("MPESA_PASSKEY")

    if not all([consumer_key, consumer_secret, business_shortcode, passkey]):
        raise MpesaException(
            "Missing required environment variables: "
            "MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, "
            "MPESA_BUSINESS_SHORTCODE, MPESA_PASSKEY"
        )

    env = Environment.PRODUCTION if environment == "production" else Environment.SANDBOX

    return MpesaAdapter(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        business_shortcode=business_shortcode,
        passkey=passkey,
        environment=env,
        event_emitter=event_emitter
    )
