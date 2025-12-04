"""
Africa's Talking API Adapter for Production Use

This module provides a comprehensive adapter for Africa's Talking API,
handling SMS, USSD, Voice, Airtime, and Payments operations across multiple
African countries.

Reference: https://developers.africastalking.com/
"""

import os
import json
import logging
import hashlib
import hmac
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from abc import ABC, abstractmethod
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


# Configure logging
logger = logging.getLogger(__name__)


class Environment(Enum):
    """Africa's Talking API environment options."""
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class DeliveryStatus(Enum):
    """SMS delivery status codes."""
    SUCCESS = "Success"
    SENT = "Sent"
    SUBMITTED = "Submitted"
    BUFFERED = "Buffered"
    REJECTED = "Rejected"
    FAILED = "Failed"


class USSDSessionStatus(Enum):
    """USSD session status."""
    CONTINUE = "CON"  # Continue session
    END = "END"       # End session


class CallStatus(Enum):
    """Voice call status codes."""
    QUEUED = "Queued"
    ANSWERED = "Answered"
    RINGING = "Ringing"
    NOT_ANSWERED = "NotAnswered"
    COMPLETED = "Completed"
    BUSY = "Busy"
    FAILED = "Failed"


class AirtimeStatus(Enum):
    """Airtime transaction status."""
    SENT = "Sent"
    QUEUED = "Queued"
    FAILED = "Failed"
    INVALID_RECIPIENT = "InvalidPhoneNumber"
    INSUFFICIENT_BALANCE = "InsufficientBalance"


class AfricasTalkingException(Exception):
    """Base exception for Africa's Talking adapter errors."""
    pass


class AfricasTalkingAuthException(AfricasTalkingException):
    """Raised when authentication fails."""
    pass


class AfricasTalkingAPIException(AfricasTalkingException):
    """Raised when API call fails."""
    pass


class AfricasTalkingEventEmitter:
    """
    Event emitter interface for IF.bus integration.

    Event names emitted:
    - at.sms.sent
    - at.sms.delivered
    - at.sms.failed
    - at.sms.bulk.sent
    - at.sms.incoming
    - at.ussd.session.started
    - at.ussd.session.continued
    - at.ussd.session.ended
    - at.voice.call.initiated
    - at.voice.call.answered
    - at.voice.call.completed
    - at.voice.call.failed
    - at.airtime.sent
    - at.airtime.failed
    - at.payment.checkout.initiated
    - at.payment.checkout.success
    - at.payment.checkout.failed
    - at.payment.b2c.initiated
    - at.payment.b2c.success
    - at.payment.b2c.failed
    - at.error.occurred
    """

    def emit(self, event_name: str, data: Dict[str, Any]) -> None:
        """
        Emit an IF.bus event.

        Args:
            event_name: Name of the event (e.g., 'at.sms.sent')
            data: Event payload dictionary
        """
        # This method will be overridden by actual IF.bus implementation
        logger.info(f"Event: {event_name}, Data: {data}")


class AfricasTalkingAdapter:
    """
    Production-ready Africa's Talking API adapter.

    Handles all Africa's Talking operations including SMS, USSD, Voice,
    Airtime, and Mobile Payments across multiple African countries.
    """

    # API Endpoints
    SANDBOX_BASE_URL = "https://api.sandbox.africastalking.com"
    PRODUCTION_BASE_URL = "https://api.africastalking.com"

    # API Versions and Paths
    SMS_ENDPOINT = "/version1/messaging"
    VOICE_ENDPOINT = "/version1/call"
    AIRTIME_ENDPOINT = "/version1/airtime/send"
    PAYMENT_MOBILE_CHECKOUT_ENDPOINT = "/mobile/checkout/request"
    PAYMENT_MOBILE_B2C_ENDPOINT = "/mobile/b2c/request"
    PAYMENT_MOBILE_B2B_ENDPOINT = "/mobile/b2b/request"
    PAYMENT_BANK_CHECKOUT_ENDPOINT = "/bank/checkout/charge"
    PAYMENT_BANK_TRANSFER_ENDPOINT = "/bank/transfer"

    def __init__(
        self,
        username: str,
        api_key: str,
        environment: Environment = Environment.SANDBOX,
        event_emitter: Optional[AfricasTalkingEventEmitter] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize Africa's Talking adapter.

        Args:
            username: Africa's Talking username (e.g., 'sandbox' or your username)
            api_key: Africa's Talking API key
            environment: Target environment (sandbox or production)
            event_emitter: Optional IF.bus event emitter
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts

        Raises:
            AfricasTalkingException: If required credentials are missing
        """
        if not all([username, api_key]):
            raise AfricasTalkingException("Both username and api_key are required")

        self.username = username
        self.api_key = api_key
        self.environment = environment
        self.event_emitter = event_emitter or AfricasTalkingEventEmitter()
        self.timeout = timeout
        self.max_retries = max_retries

        # Set base URL based on environment
        self.base_url = (
            self.PRODUCTION_BASE_URL if environment == Environment.PRODUCTION
            else self.SANDBOX_BASE_URL
        )

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

    def _get_request_headers(self) -> Dict[str, str]:
        """
        Get headers for authenticated API requests.

        Returns:
            Headers dictionary with API key authorization
        """
        return {
            "apiKey": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }

    # ========================================================================
    # SMS OPERATIONS
    # ========================================================================

    def send_sms(
        self,
        to: str,
        message: str,
        sender_id: Optional[str] = None,
        enqueue: bool = True
    ) -> Dict[str, Any]:
        """
        Send SMS to a single recipient.

        Args:
            to: Recipient phone number in international format (e.g., +254712345678)
            message: SMS message content (max 160 chars for single SMS)
            sender_id: Optional sender ID/shortcode (alphanumeric, max 11 chars)
            enqueue: Queue message for delivery (default: True)

        Returns:
            API response with message status

        Raises:
            AfricasTalkingAPIException: If API call fails

        Example:
            >>> adapter = AfricasTalkingAdapter(...)
            >>> result = adapter.send_sms(
            ...     to="+254712345678",
            ...     message="Your loan payment is due tomorrow. Pay via M-Pesa.",
            ...     sender_id="MicroFin"
            ... )
            >>> print(result['SMSMessageData']['Recipients'][0]['status'])
        """
        return self.send_bulk_sms(
            recipients=[to],
            message=message,
            sender_id=sender_id,
            enqueue=enqueue
        )

    def send_bulk_sms(
        self,
        recipients: List[str],
        message: str,
        sender_id: Optional[str] = None,
        enqueue: bool = True,
        bulk_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Send SMS to multiple recipients.

        Args:
            recipients: List of phone numbers in international format
            message: SMS message content
            sender_id: Optional sender ID/shortcode
            enqueue: Queue messages for delivery
            bulk_mode: Send as bulk (one API call) vs individual

        Returns:
            API response with message status for each recipient

        Raises:
            AfricasTalkingAPIException: If API call fails

        Example:
            >>> result = adapter.send_bulk_sms(
            ...     recipients=["+254712345678", "+254723456789"],
            ...     message="Meeting reminder: Tomorrow at 10am",
            ...     sender_id="Company"
            ... )
        """
        try:
            payload = {
                "username": self.username,
                "to": ",".join(recipients),
                "message": message,
            }

            if sender_id:
                payload["from"] = sender_id

            if enqueue:
                payload["enqueue"] = "1"

            if bulk_mode:
                payload["bulkSMSMode"] = "1"

            url = f"{self.base_url}{self.SMS_ENDPOINT}"
            headers = self._get_request_headers()

            logger.debug(f"Sending SMS to {len(recipients)} recipient(s)")

            response = self.session.post(
                url,
                data=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            # Extract recipient details
            sms_data = result.get('SMSMessageData', {})
            recipients_data = sms_data.get('Recipients', [])

            logger.info(f"SMS sent to {len(recipients_data)} recipient(s)")

            # Emit IF.bus events for each recipient
            for recipient in recipients_data:
                status = recipient.get('status', '').lower()
                phone = recipient.get('number', '')
                message_id = recipient.get('messageId', '')

                if 'success' in status or status == 'sent':
                    self.event_emitter.emit("at.sms.sent", {
                        "phone_number": phone,
                        "message_id": message_id,
                        "status": recipient.get('status'),
                        "cost": recipient.get('cost', ''),
                        "message": message[:50] + "..." if len(message) > 50 else message
                    })
                else:
                    self.event_emitter.emit("at.sms.failed", {
                        "phone_number": phone,
                        "status": recipient.get('status'),
                        "message": message[:50] + "..." if len(message) > 50 else message
                    })

            # Emit bulk event
            if len(recipients) > 1:
                self.event_emitter.emit("at.sms.bulk.sent", {
                    "total_recipients": len(recipients),
                    "successful": len([r for r in recipients_data if 'success' in r.get('status', '').lower()]),
                    "failed": len([r for r in recipients_data if 'failed' in r.get('status', '').lower()])
                })

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"SMS send failed: {str(e)}"
            logger.error(error_msg)
            self.event_emitter.emit("at.error.occurred", {
                "error_type": "sms_send_failed",
                "message": error_msg,
                "recipients": recipients
            })
            raise AfricasTalkingAPIException(error_msg) from e

    def send_premium_sms(
        self,
        to: str,
        message: str,
        keyword: str,
        link_id: Optional[str] = None,
        retry_duration_in_hours: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send premium SMS (for subscription services).

        Args:
            to: Recipient phone number
            message: SMS content
            keyword: Premium SMS keyword
            link_id: Link ID for premium SMS
            retry_duration_in_hours: Retry duration if delivery fails

        Returns:
            API response with message status

        Raises:
            AfricasTalkingAPIException: If API call fails
        """
        try:
            payload = {
                "username": self.username,
                "to": to,
                "message": message,
                "keyword": keyword,
            }

            if link_id:
                payload["linkId"] = link_id

            if retry_duration_in_hours:
                payload["retryDurationInHours"] = str(retry_duration_in_hours)

            url = f"{self.base_url}{self.SMS_ENDPOINT}"
            headers = self._get_request_headers()

            logger.debug(f"Sending premium SMS to {to}")

            response = self.session.post(
                url,
                data=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"Premium SMS sent to {to}")

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Premium SMS send failed: {str(e)}"
            logger.error(error_msg)
            raise AfricasTalkingAPIException(error_msg) from e

    def fetch_messages(
        self,
        last_received_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch incoming SMS messages.

        Args:
            last_received_id: Optional last message ID to fetch messages after

        Returns:
            API response with messages

        Raises:
            AfricasTalkingAPIException: If API call fails

        Example:
            >>> messages = adapter.fetch_messages()
            >>> for msg in messages['SMSMessageData']['Messages']:
            ...     print(f"{msg['from']}: {msg['text']}")
        """
        try:
            payload = {
                "username": self.username
            }

            if last_received_id:
                payload["lastReceivedId"] = str(last_received_id)

            url = f"{self.base_url}{self.SMS_ENDPOINT}"
            headers = self._get_request_headers()

            logger.debug("Fetching incoming messages")

            response = self.session.get(
                url,
                params=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            # Emit events for incoming messages
            sms_data = result.get('SMSMessageData', {})
            messages = sms_data.get('Messages', [])

            logger.info(f"Fetched {len(messages)} incoming message(s)")

            for msg in messages:
                self.event_emitter.emit("at.sms.incoming", {
                    "from": msg.get('from'),
                    "to": msg.get('to'),
                    "text": msg.get('text'),
                    "date": msg.get('date'),
                    "id": msg.get('id'),
                    "link_id": msg.get('linkId')
                })

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Fetch messages failed: {str(e)}"
            logger.error(error_msg)
            raise AfricasTalkingAPIException(error_msg) from e

    def fetch_subscriptions(
        self,
        short_code: str,
        keyword: str,
        last_received_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch subscription data for premium SMS.

        Args:
            short_code: Premium SMS shortcode
            keyword: Premium SMS keyword
            last_received_id: Optional last subscription ID

        Returns:
            API response with subscription data

        Raises:
            AfricasTalkingAPIException: If API call fails
        """
        try:
            payload = {
                "username": self.username,
                "shortCode": short_code,
                "keyword": keyword
            }

            if last_received_id:
                payload["lastReceivedId"] = str(last_received_id)

            url = f"{self.base_url}/version1/subscription"
            headers = self._get_request_headers()

            logger.debug(f"Fetching subscriptions for keyword: {keyword}")

            response = self.session.get(
                url,
                params=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            logger.info("Subscriptions fetched successfully")

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Fetch subscriptions failed: {str(e)}"
            logger.error(error_msg)
            raise AfricasTalkingAPIException(error_msg) from e

    # ========================================================================
    # USSD OPERATIONS
    # ========================================================================

    def handle_ussd_session(
        self,
        session_id: str,
        phone_number: str,
        text: str,
        service_code: str,
        network_code: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Handle USSD session (to be called from webhook/callback).

        This is a helper method for processing USSD requests in your application.
        The actual USSD menu logic should be implemented in create_ussd_menu().

        Args:
            session_id: Unique session ID
            phone_number: User's phone number
            text: User input text
            service_code: USSD service code (e.g., *384*1234#)
            network_code: Network operator code

        Returns:
            Tuple of (status, response_message) where status is 'CON' or 'END'

        Example:
            >>> status, response = adapter.handle_ussd_session(
            ...     session_id="ATUid_12345",
            ...     phone_number="+254712345678",
            ...     text="1*2",
            ...     service_code="*384*1234#"
            ... )
            >>> print(f"{status} {response}")
        """
        logger.debug(f"USSD session: {session_id}, Phone: {phone_number}, Input: {text}")

        # Emit session event
        if not text:
            self.event_emitter.emit("at.ussd.session.started", {
                "session_id": session_id,
                "phone_number": phone_number,
                "service_code": service_code
            })
        else:
            self.event_emitter.emit("at.ussd.session.continued", {
                "session_id": session_id,
                "phone_number": phone_number,
                "input": text
            })

        # Delegate to menu handler
        status, response = self.create_ussd_menu(session_id, phone_number, text, service_code)

        # Emit end event if session ended
        if status == USSDSessionStatus.END.value:
            self.event_emitter.emit("at.ussd.session.ended", {
                "session_id": session_id,
                "phone_number": phone_number,
                "final_input": text
            })

        return status, response

    def create_ussd_menu(
        self,
        session_id: str,
        phone_number: str,
        text: str,
        service_code: str
    ) -> Tuple[str, str]:
        """
        Create USSD menu response based on user input.

        This is a sample implementation. Override this method in your application
        to implement your specific USSD menu logic.

        Args:
            session_id: Session ID
            phone_number: User's phone number
            text: User input
            service_code: USSD service code

        Returns:
            Tuple of (status, response) where status is 'CON' or 'END'

        Example Implementation:
            >>> def create_ussd_menu(self, session_id, phone_number, text, service_code):
            ...     if text == '':
            ...         return 'CON', 'Welcome to Microfinance\\n1. Check Balance\\n2. Apply for Loan'
            ...     elif text == '1':
            ...         balance = get_balance(phone_number)
            ...         return 'END', f'Your balance is KES {balance}'
            ...     elif text == '2':
            ...         return 'CON', 'Enter loan amount:'
            ...     else:
            ...         return 'END', 'Invalid selection'
        """
        # Sample menu - implement your own logic
        if text == '':
            # Main menu
            response = "CON Welcome to Microfinance\n"
            response += "1. Check Loan Balance\n"
            response += "2. Make Payment\n"
            response += "3. Loan Statement"
            return USSDSessionStatus.CONTINUE.value, response

        elif text == '1':
            # Check balance (sample)
            response = "END Your loan balance is KES 5,000\n"
            response += "Next payment due: 15th Jan 2025"
            return USSDSessionStatus.END.value, response

        elif text == '2':
            # Make payment
            response = "CON Enter amount to pay:"
            return USSDSessionStatus.CONTINUE.value, response

        elif text.startswith('2*'):
            # Payment amount entered
            amount = text.split('*')[1]
            response = f"END Payment of KES {amount} initiated.\n"
            response += "You will receive an M-Pesa prompt shortly."
            return USSDSessionStatus.END.value, response

        elif text == '3':
            # Loan statement
            response = "END Your statement has been sent to your phone via SMS."
            return USSDSessionStatus.END.value, response

        else:
            # Invalid selection
            response = "END Invalid selection. Please try again."
            return USSDSessionStatus.END.value, response

    # ========================================================================
    # VOICE OPERATIONS
    # ========================================================================

    def make_call(
        self,
        to: str,
        from_: str,
        call_actions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Initiate an outbound voice call.

        Args:
            to: Recipient phone number in international format
            from_: Caller ID (your registered phone number or voice number)
            call_actions: Optional list of call actions (say, play, getDigits, etc.)

        Returns:
            API response with call details

        Raises:
            AfricasTalkingAPIException: If API call fails

        Example:
            >>> result = adapter.make_call(
            ...     to="+254712345678",
            ...     from_="+254711000000",
            ...     call_actions=[
            ...         {
            ...             "say": "Hello, this is a payment reminder. "
            ...                    "Your loan payment is overdue."
            ...         }
            ...     ]
            ... )
        """
        try:
            payload = {
                "username": self.username,
                "to": to,
                "from": from_
            }

            if call_actions:
                payload["callActions"] = json.dumps(call_actions)

            url = f"{self.base_url}{self.VOICE_ENDPOINT}"
            headers = self._get_request_headers()

            logger.debug(f"Initiating call to {to}")

            response = self.session.post(
                url,
                data=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            # Extract call entries
            entries = result.get('entries', [])
            for entry in entries:
                status = entry.get('status', '').lower()

                if 'queued' in status:
                    self.event_emitter.emit("at.voice.call.initiated", {
                        "phone_number": to,
                        "status": entry.get('status'),
                        "call_session_id": entry.get('sessionId', '')
                    })

            logger.info(f"Call initiated to {to}")

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Voice call failed: {str(e)}"
            logger.error(error_msg)
            self.event_emitter.emit("at.error.occurred", {
                "error_type": "voice_call_failed",
                "message": error_msg,
                "phone_number": to
            })
            raise AfricasTalkingAPIException(error_msg) from e

    def fetch_queued_calls(
        self,
        phone_number: str
    ) -> Dict[str, Any]:
        """
        Fetch queued calls for a specific phone number.

        Args:
            phone_number: Phone number to check

        Returns:
            API response with queued calls

        Raises:
            AfricasTalkingAPIException: If API call fails
        """
        try:
            payload = {
                "username": self.username,
                "phoneNumbers": phone_number
            }

            url = f"{self.base_url}/version1/call/queueStatus"
            headers = self._get_request_headers()

            logger.debug(f"Fetching queued calls for {phone_number}")

            response = self.session.post(
                url,
                data=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            logger.info("Queued calls fetched successfully")

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Fetch queued calls failed: {str(e)}"
            logger.error(error_msg)
            raise AfricasTalkingAPIException(error_msg) from e

    def upload_media_file(
        self,
        url: str,
        phone_number: str
    ) -> Dict[str, Any]:
        """
        Upload media file for voice calls.

        Args:
            url: URL of media file
            phone_number: Phone number associated with the media

        Returns:
            API response

        Raises:
            AfricasTalkingAPIException: If API call fails
        """
        try:
            payload = {
                "username": self.username,
                "url": url,
                "phoneNumber": phone_number
            }

            api_url = f"{self.base_url}/version1/mediaUpload"
            headers = self._get_request_headers()

            logger.debug(f"Uploading media file: {url}")

            response = self.session.post(
                api_url,
                data=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            logger.info("Media file uploaded successfully")

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Media upload failed: {str(e)}"
            logger.error(error_msg)
            raise AfricasTalkingAPIException(error_msg) from e

    # ========================================================================
    # AIRTIME OPERATIONS
    # ========================================================================

    def send_airtime(
        self,
        recipients: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Send airtime to one or more recipients.

        Args:
            recipients: List of recipient dictionaries with 'phoneNumber',
                       'currencyCode', and 'amount' keys

        Returns:
            API response with airtime transaction details

        Raises:
            AfricasTalkingAPIException: If API call fails

        Example:
            >>> result = adapter.send_airtime(
            ...     recipients=[
            ...         {
            ...             "phoneNumber": "+254712345678",
            ...             "currencyCode": "KES",
            ...             "amount": "100"
            ...         }
            ...     ]
            ... )
        """
        try:
            payload = {
                "username": self.username,
                "recipients": json.dumps(recipients)
            }

            url = f"{self.base_url}{self.AIRTIME_ENDPOINT}"
            headers = self._get_request_headers()

            logger.debug(f"Sending airtime to {len(recipients)} recipient(s)")

            response = self.session.post(
                url,
                data=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            # Process responses
            responses = result.get('responses', [])
            for resp in responses:
                status = resp.get('status', '').lower()
                phone = resp.get('phoneNumber', '')
                amount = resp.get('amount', '')

                if 'sent' in status:
                    self.event_emitter.emit("at.airtime.sent", {
                        "phone_number": phone,
                        "amount": amount,
                        "status": resp.get('status'),
                        "request_id": resp.get('requestId', '')
                    })
                else:
                    self.event_emitter.emit("at.airtime.failed", {
                        "phone_number": phone,
                        "amount": amount,
                        "status": resp.get('status'),
                        "error_message": resp.get('errorMessage', '')
                    })

            logger.info(f"Airtime sent to {len(responses)} recipient(s)")

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Airtime send failed: {str(e)}"
            logger.error(error_msg)
            self.event_emitter.emit("at.error.occurred", {
                "error_type": "airtime_send_failed",
                "message": error_msg
            })
            raise AfricasTalkingAPIException(error_msg) from e

    def find_airtime_transaction(
        self,
        transaction_id: str
    ) -> Dict[str, Any]:
        """
        Find status of an airtime transaction.

        Args:
            transaction_id: Transaction ID from send_airtime response

        Returns:
            API response with transaction status

        Raises:
            AfricasTalkingAPIException: If API call fails
        """
        try:
            payload = {
                "username": self.username,
                "transactionId": transaction_id
            }

            url = f"{self.base_url}/version1/airtime/find"
            headers = self._get_request_headers()

            logger.debug(f"Finding airtime transaction: {transaction_id}")

            response = self.session.get(
                url,
                params=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"Airtime transaction status fetched: {transaction_id}")

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Find airtime transaction failed: {str(e)}"
            logger.error(error_msg)
            raise AfricasTalkingAPIException(error_msg) from e

    # ========================================================================
    # PAYMENT OPERATIONS (Optional - requires Payments product)
    # ========================================================================

    def mobile_checkout(
        self,
        product_name: str,
        phone_number: str,
        currency_code: str,
        amount: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initiate mobile checkout (customer pays merchant).

        Args:
            product_name: Your Africa's Talking payment product name
            phone_number: Customer phone number
            currency_code: Currency (e.g., 'KES', 'UGX')
            amount: Amount to charge
            metadata: Optional metadata dictionary

        Returns:
            API response with transaction details

        Raises:
            AfricasTalkingAPIException: If API call fails

        Example:
            >>> result = adapter.mobile_checkout(
            ...     product_name="MyProduct",
            ...     phone_number="+254712345678",
            ...     currency_code="KES",
            ...     amount=1000.00,
            ...     metadata={"loan_id": "LOAN_123"}
            ... )
        """
        try:
            payload = {
                "username": self.username,
                "productName": product_name,
                "phoneNumber": phone_number,
                "currencyCode": currency_code,
                "amount": amount
            }

            if metadata:
                payload["metadata"] = json.dumps(metadata)

            url = f"{self.base_url}{self.PAYMENT_MOBILE_CHECKOUT_ENDPOINT}"
            headers = self._get_request_headers()

            logger.debug(f"Initiating mobile checkout: {phone_number}, Amount: {amount}")

            response = self.session.post(
                url,
                data=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            status = result.get('status', '').lower()
            if 'pending' in status:
                self.event_emitter.emit("at.payment.checkout.initiated", {
                    "phone_number": phone_number,
                    "amount": amount,
                    "currency": currency_code,
                    "transaction_id": result.get('transactionId', ''),
                    "provider": result.get('provider', '')
                })

            logger.info(f"Mobile checkout initiated for {phone_number}")

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Mobile checkout failed: {str(e)}"
            logger.error(error_msg)
            self.event_emitter.emit("at.error.occurred", {
                "error_type": "mobile_checkout_failed",
                "message": error_msg,
                "phone_number": phone_number
            })
            raise AfricasTalkingAPIException(error_msg) from e

    def mobile_b2c(
        self,
        product_name: str,
        recipients: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Initiate mobile B2C payment (merchant pays customers).

        Args:
            product_name: Your Africa's Talking payment product name
            recipients: List of recipient dicts with phoneNumber, currencyCode,
                       amount, reason, and optional metadata

        Returns:
            API response with payment details

        Raises:
            AfricasTalkingAPIException: If API call fails

        Example:
            >>> result = adapter.mobile_b2c(
            ...     product_name="MyProduct",
            ...     recipients=[
            ...         {
            ...             "phoneNumber": "+254712345678",
            ...             "currencyCode": "KES",
            ...             "amount": 500.0,
            ...             "reason": "SalaryPayment",
            ...             "metadata": {"employee_id": "EMP_123"}
            ...         }
            ...     ]
            ... )
        """
        try:
            payload = {
                "username": self.username,
                "productName": product_name,
                "recipients": json.dumps(recipients)
            }

            url = f"{self.base_url}{self.PAYMENT_MOBILE_B2C_ENDPOINT}"
            headers = self._get_request_headers()

            logger.debug(f"Initiating mobile B2C for {len(recipients)} recipient(s)")

            response = self.session.post(
                url,
                data=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            # Process entries
            entries = result.get('entries', [])
            for entry in entries:
                status = entry.get('status', '').lower()
                phone = entry.get('phoneNumber', '')

                if 'queued' in status:
                    self.event_emitter.emit("at.payment.b2c.initiated", {
                        "phone_number": phone,
                        "amount": entry.get('value', ''),
                        "status": entry.get('status'),
                        "transaction_id": entry.get('transactionId', '')
                    })

            logger.info(f"Mobile B2C initiated for {len(entries)} recipient(s)")

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Mobile B2C failed: {str(e)}"
            logger.error(error_msg)
            self.event_emitter.emit("at.error.occurred", {
                "error_type": "mobile_b2c_failed",
                "message": error_msg
            })
            raise AfricasTalkingAPIException(error_msg) from e

    def mobile_b2b(
        self,
        product_name: str,
        provider: str,
        transfer_type: str,
        currency_code: str,
        amount: float,
        destination_channel: str,
        destination_account: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initiate mobile B2B payment (business to business).

        Args:
            product_name: Your Africa's Talking payment product name
            provider: Payment provider (e.g., 'Mpesa', 'TigoTanzania')
            transfer_type: Transfer type (e.g., 'BusinessToBusinessTransfer')
            currency_code: Currency code
            amount: Amount to transfer
            destination_channel: Destination channel
            destination_account: Destination account/till number
            metadata: Optional metadata

        Returns:
            API response with transfer details

        Raises:
            AfricasTalkingAPIException: If API call fails
        """
        try:
            payload = {
                "username": self.username,
                "productName": product_name,
                "provider": provider,
                "transferType": transfer_type,
                "currencyCode": currency_code,
                "amount": amount,
                "destinationChannel": destination_channel,
                "destinationAccount": destination_account
            }

            if metadata:
                payload["metadata"] = json.dumps(metadata)

            url = f"{self.base_url}{self.PAYMENT_MOBILE_B2B_ENDPOINT}"
            headers = self._get_request_headers()

            logger.debug(f"Initiating mobile B2B: {amount} {currency_code}")

            response = self.session.post(
                url,
                data=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            logger.info("Mobile B2B initiated successfully")

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Mobile B2B failed: {str(e)}"
            logger.error(error_msg)
            raise AfricasTalkingAPIException(error_msg) from e

    def bank_checkout(
        self,
        product_name: str,
        bank_account: Dict[str, str],
        currency_code: str,
        amount: float,
        narration: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initiate bank checkout (charge customer's bank account).

        Args:
            product_name: Your Africa's Talking payment product name
            bank_account: Bank account dict with accountName, accountNumber, bankCode
            currency_code: Currency code
            amount: Amount to charge
            narration: Transaction narration
            metadata: Optional metadata

        Returns:
            API response with transaction details

        Raises:
            AfricasTalkingAPIException: If API call fails
        """
        try:
            payload = {
                "username": self.username,
                "productName": product_name,
                "bankAccount": json.dumps(bank_account),
                "currencyCode": currency_code,
                "amount": amount,
                "narration": narration
            }

            if metadata:
                payload["metadata"] = json.dumps(metadata)

            url = f"{self.base_url}{self.PAYMENT_BANK_CHECKOUT_ENDPOINT}"
            headers = self._get_request_headers()

            logger.debug(f"Initiating bank checkout: {amount} {currency_code}")

            response = self.session.post(
                url,
                data=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            logger.info("Bank checkout initiated successfully")

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Bank checkout failed: {str(e)}"
            logger.error(error_msg)
            raise AfricasTalkingAPIException(error_msg) from e

    def bank_transfer(
        self,
        product_name: str,
        recipients: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Transfer money to bank accounts.

        Args:
            product_name: Your Africa's Talking payment product name
            recipients: List of recipient dicts with bankAccount, currencyCode,
                       amount, narration, and optional metadata

        Returns:
            API response with transfer details

        Raises:
            AfricasTalkingAPIException: If API call fails
        """
        try:
            payload = {
                "username": self.username,
                "productName": product_name,
                "recipients": json.dumps(recipients)
            }

            url = f"{self.base_url}{self.PAYMENT_BANK_TRANSFER_ENDPOINT}"
            headers = self._get_request_headers()

            logger.debug(f"Initiating bank transfer for {len(recipients)} recipient(s)")

            response = self.session.post(
                url,
                data=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"Bank transfer initiated for {len(recipients)} recipient(s)")

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Bank transfer failed: {str(e)}"
            logger.error(error_msg)
            raise AfricasTalkingAPIException(error_msg) from e

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def validate_signature(
        self,
        data: str,
        signature: str
    ) -> bool:
        """
        Validate webhook signature for security.

        Args:
            data: Request body data
            signature: X-AT-Signature header value

        Returns:
            True if signature is valid, False otherwise

        Example:
            >>> is_valid = adapter.validate_signature(
            ...     data=request.body,
            ...     signature=request.headers['X-AT-Signature']
            ... )
        """
        computed_signature = hmac.new(
            self.api_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed_signature, signature)

    def close(self) -> None:
        """Close the session and cleanup resources."""
        self.session.close()
        logger.info("Africa's Talking adapter session closed")


# Factory function for creating adapter instances
def create_africas_talking_adapter(
    environment: str = "sandbox",
    event_emitter: Optional[AfricasTalkingEventEmitter] = None
) -> AfricasTalkingAdapter:
    """
    Factory function to create Africa's Talking adapter from environment variables.

    Environment variables required:
    - AT_USERNAME (or AFRICASTALKING_USERNAME)
    - AT_API_KEY (or AFRICASTALKING_API_KEY)
    - AT_ENVIRONMENT (optional, defaults to sandbox)

    Args:
        environment: Override environment (sandbox or production)
        event_emitter: Optional IF.bus event emitter

    Returns:
        Configured AfricasTalkingAdapter instance

    Raises:
        AfricasTalkingException: If required environment variables are missing

    Example:
        >>> adapter = create_africas_talking_adapter(environment="production")
        >>> result = adapter.send_sms(to="+254712345678", message="Hello!")
    """
    username = os.getenv("AT_USERNAME") or os.getenv("AFRICASTALKING_USERNAME")
    api_key = os.getenv("AT_API_KEY") or os.getenv("AFRICASTALKING_API_KEY")

    if not all([username, api_key]):
        raise AfricasTalkingException(
            "Missing required environment variables: AT_USERNAME, AT_API_KEY"
        )

    env = Environment.PRODUCTION if environment == "production" else Environment.SANDBOX

    return AfricasTalkingAdapter(
        username=username,
        api_key=api_key,
        environment=env,
        event_emitter=event_emitter
    )
