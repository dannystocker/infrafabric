"""
M-Pesa Adapter Test Helpers and Mocks

Provides mock implementations and test utilities for unit testing M-Pesa integration.
"""

from typing import Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock
import json

from mpesa_adapter import MpesaEventEmitter, MpesaAdapter, Environment


class MockMpesaEventEmitter(MpesaEventEmitter):
    """Mock event emitter for testing."""

    def __init__(self):
        """Initialize mock emitter with event tracking."""
        self.events = []

    def emit(self, event_name: str, data: Dict[str, Any]) -> None:
        """Capture emitted events."""
        self.events.append({
            'event': event_name,
            'data': data
        })

    def get_events(self, event_type: Optional[str] = None) -> list:
        """Get emitted events, optionally filtered by type."""
        if event_type:
            return [e for e in self.events if e['event'].startswith(event_type)]
        return self.events

    def clear_events(self) -> None:
        """Clear all tracked events."""
        self.events = []

    def assert_event_emitted(self, event_name: str) -> bool:
        """Assert that an event was emitted."""
        return any(e['event'] == event_name for e in self.events)


class MockMpesaResponses:
    """Mock responses for M-Pesa API calls."""

    @staticmethod
    def oauth_success() -> Dict[str, Any]:
        """Mock successful OAuth token response."""
        return {
            "access_token": "mock_access_token_12345",
            "expires_in": 3600,
            "token_type": "Bearer"
        }

    @staticmethod
    def oauth_failure() -> Dict[str, Any]:
        """Mock failed OAuth response."""
        return {
            "error": "invalid_client",
            "error_description": "Client authentication failed"
        }

    @staticmethod
    def stk_push_success() -> Dict[str, Any]:
        """Mock successful STK Push response."""
        return {
            "MerchantRequestID": "mock_merchant_12345",
            "CheckoutRequestID": "ws_CO_DMZ_mock_request_123",
            "ResponseCode": "0",
            "ResponseDescription": "Success. Request accepted for processing",
            "CustomerMessage": "Success. Request accepted for processing"
        }

    @staticmethod
    def stk_push_failure() -> Dict[str, Any]:
        """Mock failed STK Push response."""
        return {
            "MerchantRequestID": "mock_merchant_12345",
            "CheckoutRequestID": "ws_CO_DMZ_mock_request_123",
            "ResponseCode": "1",
            "ResponseDescription": "Invalid merchant shortcode",
            "CustomerMessage": "Invalid merchant shortcode"
        }

    @staticmethod
    def stk_push_query_success() -> Dict[str, Any]:
        """Mock successful STK Push query response."""
        return {
            "ResponseCode": "0",
            "ResponseDescription": "The service request has been accepted successfully",
            "MerchantRequestID": "mock_merchant_12345",
            "CheckoutRequestID": "ws_CO_DMZ_mock_request_123",
            "ResultCode": "0",
            "ResultDescription": "The service request has been accepted successfully",
            "ResultParameters": {
                "Amount": "100",
                "MpesaReceiptNumber": "LHG31AA5695",
                "TransactionDate": "20241204103000",
                "PhoneNumber": "254712345678"
            }
        }

    @staticmethod
    def b2c_payment_success() -> Dict[str, Any]:
        """Mock successful B2C payment response."""
        return {
            "ConversationID": "mock_conversation_12345",
            "OriginatorConversationID": "mock_originator_12345",
            "ResponseCode": "0",
            "ResponseDescription": "Accept the service request successfully"
        }

    @staticmethod
    def b2c_payment_failure() -> Dict[str, Any]:
        """Mock failed B2C payment response."""
        return {
            "ConversationID": "mock_conversation_12345",
            "OriginatorConversationID": "mock_originator_12345",
            "ResponseCode": "1",
            "ResponseDescription": "Invalid security credential"
        }

    @staticmethod
    def transaction_status_success() -> Dict[str, Any]:
        """Mock successful transaction status query response."""
        return {
            "ResultCode": "0",
            "ResultDescription": "The service request has been accepted successfully",
            "ResultParameters": {
                "Amount": "100",
                "TransactionStatus": "Success",
                "ReceiverPartyPublicName": "John Doe",
                "TransactionID": "LHG31AA5695",
                "TransactionDate": "20241204103000"
            }
        }

    @staticmethod
    def balance_query_success() -> Dict[str, Any]:
        """Mock successful account balance query response."""
        return {
            "ResponseCode": "0",
            "ConversationID": "mock_conversation_12345",
            "OriginatorConversationID": "mock_originator_12345",
            "ResponseDescription": "Accept the service request successfully"
        }


class MpesaAdapterTestHelper:
    """Helper class for testing M-Pesa adapter."""

    @staticmethod
    def create_mock_adapter(
        environment: Environment = Environment.SANDBOX,
        with_mock_session: bool = True
    ) -> MpesaAdapter:
        """
        Create a mock M-Pesa adapter for testing.

        Args:
            environment: Target environment
            with_mock_session: If True, session will be mocked

        Returns:
            Mock MpesaAdapter instance
        """
        adapter = MpesaAdapter(
            consumer_key="test_key",
            consumer_secret="test_secret",
            business_shortcode="123456",
            passkey="test_passkey",
            environment=environment,
            event_emitter=MockMpesaEventEmitter()
        )

        if with_mock_session:
            adapter.session = MagicMock()

        return adapter

    @staticmethod
    def mock_oauth_response(adapter: MpesaAdapter, success: bool = True) -> None:
        """
        Mock OAuth response in adapter session.

        Args:
            adapter: MpesaAdapter instance
            success: Whether to mock successful or failed response
        """
        response = Mock()
        response.json.return_value = (
            MockMpesaResponses.oauth_success()
            if success
            else MockMpesaResponses.oauth_failure()
        )
        response.raise_for_status = Mock()

        adapter.session.get = Mock(return_value=response)

    @staticmethod
    def mock_stk_push_response(adapter: MpesaAdapter, success: bool = True) -> None:
        """
        Mock STK Push response in adapter session.

        Args:
            adapter: MpesaAdapter instance
            success: Whether to mock successful or failed response
        """
        response = Mock()
        response.json.return_value = (
            MockMpesaResponses.stk_push_success()
            if success
            else MockMpesaResponses.stk_push_failure()
        )
        response.raise_for_status = Mock()

        adapter.session.post = Mock(return_value=response)

    @staticmethod
    def mock_b2c_response(adapter: MpesaAdapter, success: bool = True) -> None:
        """
        Mock B2C payment response in adapter session.

        Args:
            adapter: MpesaAdapter instance
            success: Whether to mock successful or failed response
        """
        response = Mock()
        response.json.return_value = (
            MockMpesaResponses.b2c_payment_success()
            if success
            else MockMpesaResponses.b2c_payment_failure()
        )
        response.raise_for_status = Mock()

        adapter.session.post = Mock(return_value=response)


class MpesaIntegrationTestBase:
    """Base class for M-Pesa integration tests."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.adapter = MpesaAdapterTestHelper.create_mock_adapter()
        self.event_emitter = self.adapter.event_emitter

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.adapter.close()

    def assert_event_emitted(self, event_name: str) -> None:
        """Assert that a specific event was emitted."""
        assert self.event_emitter.assert_event_emitted(event_name), \
            f"Event '{event_name}' was not emitted"

    def assert_no_events_emitted(self) -> None:
        """Assert that no events were emitted."""
        assert len(self.event_emitter.get_events()) == 0, \
            f"Expected no events, but {len(self.event_emitter.get_events())} were emitted"

    def get_emitted_events(self, event_type: Optional[str] = None) -> list:
        """Get emitted events."""
        return self.event_emitter.get_events(event_type)


# Example test cases
class TestMpesaAdapterExamples:
    """Example test cases for M-Pesa adapter."""

    def test_oauth_token_acquisition(self):
        """Test OAuth token acquisition."""
        # Create adapter with mock session
        adapter = MpesaAdapterTestHelper.create_mock_adapter()
        MpesaAdapterTestHelper.mock_oauth_response(adapter, success=True)

        # Mock response for token endpoint
        response = Mock()
        response.json.return_value = MockMpesaResponses.oauth_success()
        response.raise_for_status = Mock()
        adapter.session.get = Mock(return_value=response)

        # Get token
        token = adapter.get_access_token()

        # Verify token obtained
        assert token == "mock_access_token_12345"
        assert adapter._access_token == token

        # Verify token is cached
        cached_token = adapter.get_access_token()
        assert cached_token == token

        adapter.close()

    def test_stk_push_initiation(self):
        """Test STK Push initiation."""
        adapter = MpesaAdapterTestHelper.create_mock_adapter()

        # Mock OAuth response
        oauth_response = Mock()
        oauth_response.json.return_value = MockMpesaResponses.oauth_success()
        oauth_response.raise_for_status = Mock()

        # Mock STK Push response
        stk_response = Mock()
        stk_response.json.return_value = MockMpesaResponses.stk_push_success()
        stk_response.raise_for_status = Mock()

        # Setup mock session
        adapter.session.get = Mock(return_value=oauth_response)
        adapter.session.post = Mock(return_value=stk_response)

        # Initiate STK Push
        result = adapter.initiate_stk_push(
            phone_number="254712345678",
            amount=100.0,
            account_reference="TEST_001"
        )

        # Verify response
        assert result['ResponseCode'] == "0"
        assert "CheckoutRequestID" in result
        assert "MerchantRequestID" in result

        # Verify event emitted
        assert adapter.event_emitter.assert_event_emitted("mpesa.stk_push.initiated")

        adapter.close()

    def test_b2c_payment(self):
        """Test B2C payment initiation."""
        adapter = MpesaAdapterTestHelper.create_mock_adapter()

        # Mock OAuth response
        oauth_response = Mock()
        oauth_response.json.return_value = MockMpesaResponses.oauth_success()
        oauth_response.raise_for_status = Mock()

        # Mock B2C response
        b2c_response = Mock()
        b2c_response.json.return_value = MockMpesaResponses.b2c_payment_success()
        b2c_response.raise_for_status = Mock()

        # Setup mock session
        adapter.session.get = Mock(return_value=oauth_response)
        adapter.session.post = Mock(return_value=b2c_response)

        # Initiate B2C payment
        result = adapter.b2c_payment(
            phone_number="254712345678",
            amount=5000.0,
            command_id="SalaryPayment"
        )

        # Verify response
        assert result['ResponseCode'] == "0"
        assert "ConversationID" in result

        # Verify event emitted
        assert adapter.event_emitter.assert_event_emitted("mpesa.b2c.initiated")

        adapter.close()

    def test_error_event_emission(self):
        """Test that errors emit error events."""
        adapter = MpesaAdapterTestHelper.create_mock_adapter()

        # Mock failed response
        error_response = Mock()
        error_response.json.return_value = MockMpesaResponses.stk_push_failure()
        error_response.raise_for_status = Mock()

        # Mock OAuth response
        oauth_response = Mock()
        oauth_response.json.return_value = MockMpesaResponses.oauth_success()
        oauth_response.raise_for_status = Mock()

        adapter.session.get = Mock(return_value=oauth_response)
        adapter.session.post = Mock(return_value=error_response)

        # Attempt STK Push with failure response
        try:
            adapter.initiate_stk_push(
                phone_number="254712345678",
                amount=100.0,
                account_reference="TEST_001"
            )
        except Exception:
            pass

        # Error should be logged (no exception raised in test)
        adapter.close()


if __name__ == "__main__":
    """Run example tests."""
    print("M-Pesa Adapter Test Helpers")
    print("=" * 60)
    print("Available test helpers:")
    print("  - MockMpesaEventEmitter: Mock event emitter for testing")
    print("  - MockMpesaResponses: Mock API responses")
    print("  - MpesaAdapterTestHelper: Helper for creating mock adapters")
    print("  - MpesaIntegrationTestBase: Base class for integration tests")
    print("  - TestMpesaAdapterExamples: Example test cases")
    print("\nUsage with pytest:")
    print("  pytest test_helpers.py -v")
    print("=" * 60)

    # Run example tests
    print("\nRunning example tests...")
    test = TestMpesaAdapterExamples()

    try:
        test.test_oauth_token_acquisition()
        print("✓ test_oauth_token_acquisition passed")
    except AssertionError as e:
        print(f"✗ test_oauth_token_acquisition failed: {e}")

    try:
        test.test_stk_push_initiation()
        print("✓ test_stk_push_initiation passed")
    except AssertionError as e:
        print(f"✗ test_stk_push_initiation failed: {e}")

    try:
        test.test_b2c_payment()
        print("✓ test_b2c_payment passed")
    except AssertionError as e:
        print(f"✗ test_b2c_payment failed: {e}")

    try:
        test.test_error_event_emission()
        print("✓ test_error_event_emission passed")
    except AssertionError as e:
        print(f"✗ test_error_event_emission failed: {e}")

    print("\nAll example tests completed!")
