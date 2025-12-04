"""
Unit tests for Africa's Talking Adapter

Run with: python -m pytest test_adapter.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from africas_talking_adapter import (
    AfricasTalkingAdapter,
    AfricasTalkingEventEmitter,
    Environment,
    AfricasTalkingException,
    AfricasTalkingAuthException,
    AfricasTalkingAPIException,
    create_africas_talking_adapter
)

from config import (
    AfricasTalkingConfig,
    Country,
    PhoneNumberValidator,
    SMSValidator,
    AirtimeValidator,
    SMSTemplates,
    COUNTRY_CONFIGS
)


class TestAfricasTalkingAdapter:
    """Test cases for AfricasTalkingAdapter."""

    def test_adapter_initialization(self):
        """Test adapter initialization with valid credentials."""
        adapter = AfricasTalkingAdapter(
            username="sandbox",
            api_key="test_api_key",
            environment=Environment.SANDBOX
        )

        assert adapter.username == "sandbox"
        assert adapter.api_key == "test_api_key"
        assert adapter.environment == Environment.SANDBOX
        assert adapter.base_url == "https://api.sandbox.africastalking.com"

    def test_adapter_initialization_missing_credentials(self):
        """Test adapter initialization fails with missing credentials."""
        with pytest.raises(AfricasTalkingException):
            AfricasTalkingAdapter(
                username="",
                api_key="test_api_key"
            )

    def test_production_base_url(self):
        """Test production environment uses correct base URL."""
        adapter = AfricasTalkingAdapter(
            username="production",
            api_key="test_api_key",
            environment=Environment.PRODUCTION
        )

        assert adapter.base_url == "https://api.africastalking.com"

    @patch('africas_talking_adapter.requests.Session.post')
    def test_send_sms_success(self, mock_post):
        """Test successful SMS sending."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'SMSMessageData': {
                'Message': 'Sent to 1/1 Total Cost: KES 0.8000',
                'Recipients': [
                    {
                        'statusCode': 101,
                        'number': '+254712345678',
                        'status': 'Success',
                        'cost': 'KES 0.8000',
                        'messageId': 'ATXid_12345'
                    }
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        adapter = AfricasTalkingAdapter(
            username="sandbox",
            api_key="test_api_key"
        )

        result = adapter.send_sms(
            to="+254712345678",
            message="Test message"
        )

        assert 'SMSMessageData' in result
        assert len(result['SMSMessageData']['Recipients']) == 1
        assert result['SMSMessageData']['Recipients'][0]['status'] == 'Success'

    @patch('africas_talking_adapter.requests.Session.post')
    def test_send_bulk_sms(self, mock_post):
        """Test bulk SMS sending."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'SMSMessageData': {
                'Message': 'Sent to 2/2 Total Cost: KES 1.6000',
                'Recipients': [
                    {
                        'statusCode': 101,
                        'number': '+254712345678',
                        'status': 'Success',
                        'cost': 'KES 0.8000',
                        'messageId': 'ATXid_12345'
                    },
                    {
                        'statusCode': 101,
                        'number': '+254723456789',
                        'status': 'Success',
                        'cost': 'KES 0.8000',
                        'messageId': 'ATXid_12346'
                    }
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        adapter = AfricasTalkingAdapter(
            username="sandbox",
            api_key="test_api_key"
        )

        result = adapter.send_bulk_sms(
            recipients=["+254712345678", "+254723456789"],
            message="Bulk test message"
        )

        assert len(result['SMSMessageData']['Recipients']) == 2

    def test_ussd_session_handling(self):
        """Test USSD session handling."""
        adapter = AfricasTalkingAdapter(
            username="sandbox",
            api_key="test_api_key"
        )

        # Test main menu
        status, response = adapter.handle_ussd_session(
            session_id="ATUid_12345",
            phone_number="+254712345678",
            text="",
            service_code="*384*1234#"
        )

        assert status == "CON"
        assert "Welcome" in response

        # Test balance check
        status, response = adapter.handle_ussd_session(
            session_id="ATUid_12345",
            phone_number="+254712345678",
            text="1",
            service_code="*384*1234#"
        )

        assert status == "END"
        assert "balance" in response.lower()

    @patch('africas_talking_adapter.requests.Session.post')
    def test_make_call(self, mock_post):
        """Test voice call initiation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'entries': [
                {
                    'status': 'Queued',
                    'phoneNumber': '+254712345678',
                    'sessionId': 'ATVid_12345'
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        adapter = AfricasTalkingAdapter(
            username="sandbox",
            api_key="test_api_key"
        )

        result = adapter.make_call(
            to="+254712345678",
            from_="+254711000000"
        )

        assert 'entries' in result
        assert result['entries'][0]['status'] == 'Queued'

    @patch('africas_talking_adapter.requests.Session.post')
    def test_send_airtime(self, mock_post):
        """Test airtime sending."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'responses': [
                {
                    'phoneNumber': '+254712345678',
                    'amount': 'KES 50.0000',
                    'status': 'Sent',
                    'requestId': 'ATQid_12345'
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        adapter = AfricasTalkingAdapter(
            username="sandbox",
            api_key="test_api_key"
        )

        result = adapter.send_airtime(
            recipients=[
                {
                    "phoneNumber": "+254712345678",
                    "currencyCode": "KES",
                    "amount": "50"
                }
            ]
        )

        assert 'responses' in result
        assert result['responses'][0]['status'] == 'Sent'

    def test_event_emitter(self):
        """Test event emission."""
        mock_emitter = Mock(spec=AfricasTalkingEventEmitter)

        adapter = AfricasTalkingAdapter(
            username="sandbox",
            api_key="test_api_key",
            event_emitter=mock_emitter
        )

        # Events should be emitted during operations
        assert adapter.event_emitter == mock_emitter


class TestConfiguration:
    """Test cases for configuration module."""

    def test_config_from_env(self, monkeypatch):
        """Test configuration loading from environment variables."""
        monkeypatch.setenv("AT_USERNAME", "test_user")
        monkeypatch.setenv("AT_API_KEY", "test_key")
        monkeypatch.setenv("AT_ENVIRONMENT", "production")

        config = AfricasTalkingConfig.from_env()

        assert config.username == "test_user"
        assert config.api_key == "test_key"
        assert config.environment == Environment.PRODUCTION

    def test_config_validation(self):
        """Test configuration validation."""
        config = AfricasTalkingConfig(
            username="test_user",
            api_key="test_key",
            environment=Environment.SANDBOX
        )

        assert config.validate() is True

    def test_config_validation_failure(self):
        """Test configuration validation with invalid data."""
        config = AfricasTalkingConfig(
            username="",
            api_key="test_key",
            environment=Environment.SANDBOX
        )

        with pytest.raises(ValueError):
            config.validate()


class TestPhoneNumberValidator:
    """Test cases for phone number validation."""

    def test_format_international_kenya(self):
        """Test phone number formatting for Kenya."""
        # Local format
        assert PhoneNumberValidator.format_international("0712345678", Country.KENYA) == "+254712345678"

        # Already international
        assert PhoneNumberValidator.format_international("+254712345678", Country.KENYA) == "+254712345678"

        # Missing plus
        assert PhoneNumberValidator.format_international("254712345678", Country.KENYA) == "+254712345678"

    def test_format_international_uganda(self):
        """Test phone number formatting for Uganda."""
        assert PhoneNumberValidator.format_international("0712345678", Country.UGANDA) == "+256712345678"

    def test_validate_phone_number(self):
        """Test phone number validation."""
        assert PhoneNumberValidator.validate("+254712345678", Country.KENYA) is True
        assert PhoneNumberValidator.validate("+256712345678", Country.UGANDA) is True
        assert PhoneNumberValidator.validate("invalid", Country.KENYA) is False

    def test_clean_phone_number(self):
        """Test phone number cleaning."""
        cleaned = PhoneNumberValidator.clean("0712345678", Country.KENYA)
        assert cleaned == "+254712345678"

        with pytest.raises(ValueError):
            PhoneNumberValidator.clean("invalid", Country.KENYA)

    def test_detect_country(self):
        """Test country detection from phone number."""
        assert PhoneNumberValidator.detect_country("+254712345678") == Country.KENYA
        assert PhoneNumberValidator.detect_country("+256712345678") == Country.UGANDA
        assert PhoneNumberValidator.detect_country("+255712345678") == Country.TANZANIA
        assert PhoneNumberValidator.detect_country("+999999999999") is None


class TestSMSValidator:
    """Test cases for SMS validation."""

    def test_validate_message_length(self):
        """Test SMS message length validation."""
        # Single part SMS
        is_valid, num_parts = SMSValidator.validate_message_length("Short message")
        assert is_valid is True
        assert num_parts == 1

        # Exactly 160 chars
        is_valid, num_parts = SMSValidator.validate_message_length("A" * 160)
        assert is_valid is True
        assert num_parts == 1

        # Multi-part SMS
        is_valid, num_parts = SMSValidator.validate_message_length("A" * 320)
        assert is_valid is True
        assert num_parts > 1

    def test_validate_sender_id(self):
        """Test sender ID validation."""
        assert SMSValidator.validate_sender_id("MicroFin") is True
        assert SMSValidator.validate_sender_id("COMPANY123") is True
        assert SMSValidator.validate_sender_id("") is False
        assert SMSValidator.validate_sender_id("A" * 12) is False  # Too long


class TestAirtimeValidator:
    """Test cases for airtime validation."""

    def test_validate_amount(self):
        """Test airtime amount validation."""
        assert AirtimeValidator.validate_amount(50.0) is True
        assert AirtimeValidator.validate_amount(100.0) is True
        assert AirtimeValidator.validate_amount(5.0) is False  # Too low
        assert AirtimeValidator.validate_amount(20000.0) is False  # Too high

    def test_validate_currency(self):
        """Test currency validation."""
        assert AirtimeValidator.validate_currency("KES", Country.KENYA) is True
        assert AirtimeValidator.validate_currency("UGX", Country.UGANDA) is True
        assert AirtimeValidator.validate_currency("USD", Country.KENYA) is False


class TestSMSTemplates:
    """Test cases for SMS templates."""

    def test_loan_reminder_template(self):
        """Test loan reminder SMS template."""
        message = SMSTemplates.loan_reminder(
            customer_name="John Kamau",
            loan_amount=5000.00,
            due_date="2025-01-20",
            days_overdue=0
        )

        assert "John Kamau" in message
        assert "5000.00" in message
        assert "2025-01-20" in message

    def test_loan_reminder_overdue_template(self):
        """Test overdue loan reminder template."""
        message = SMSTemplates.loan_reminder(
            customer_name="John Kamau",
            loan_amount=5000.00,
            due_date="2025-01-15",
            days_overdue=3
        )

        assert "3 days overdue" in message

    def test_payment_confirmation_template(self):
        """Test payment confirmation template."""
        message = SMSTemplates.payment_confirmation(
            customer_name="John Kamau",
            amount=1500.00,
            transaction_id="PHG5JKL890",
            new_balance=3500.00
        )

        assert "John Kamau" in message
        assert "1500.00" in message
        assert "PHG5JKL890" in message
        assert "3500.00" in message

    def test_loan_approved_template(self):
        """Test loan approval template."""
        message = SMSTemplates.loan_approved(
            customer_name="John Kamau",
            loan_amount=10000.00,
            repayment_date="2025-02-20"
        )

        assert "Congratulations" in message
        assert "10000.00" in message

    def test_overdue_notice_template(self):
        """Test overdue notice template."""
        message = SMSTemplates.overdue_notice(
            customer_name="John Kamau",
            amount_due=5000.00,
            days_overdue=7,
            penalty=500.00
        )

        assert "URGENT" in message
        assert "7 days overdue" in message
        assert "500.00" in message


class TestCountryConfigs:
    """Test cases for country configurations."""

    def test_country_configs_exist(self):
        """Test that all country configs are defined."""
        assert Country.KENYA in COUNTRY_CONFIGS
        assert Country.UGANDA in COUNTRY_CONFIGS
        assert Country.TANZANIA in COUNTRY_CONFIGS
        assert Country.RWANDA in COUNTRY_CONFIGS
        assert Country.MALAWI in COUNTRY_CONFIGS
        assert Country.NIGERIA in COUNTRY_CONFIGS
        assert Country.ETHIOPIA in COUNTRY_CONFIGS

    def test_kenya_config(self):
        """Test Kenya country configuration."""
        config = COUNTRY_CONFIGS[Country.KENYA]

        assert config.name == "Kenya"
        assert config.country_code == "254"
        assert config.currency == "KES"
        assert config.supports_ussd is True
        assert config.supports_voice is True
        assert config.supports_payments is True

    def test_uganda_config(self):
        """Test Uganda country configuration."""
        config = COUNTRY_CONFIGS[Country.UGANDA]

        assert config.name == "Uganda"
        assert config.country_code == "256"
        assert config.currency == "UGX"

    def test_ethiopia_config(self):
        """Test Ethiopia country configuration (limited features)."""
        config = COUNTRY_CONFIGS[Country.ETHIOPIA]

        assert config.name == "Ethiopia"
        assert config.supports_ussd is False
        assert config.supports_voice is False


class TestFactoryFunction:
    """Test cases for factory function."""

    def test_create_adapter_from_env(self, monkeypatch):
        """Test adapter creation from environment variables."""
        monkeypatch.setenv("AT_USERNAME", "sandbox")
        monkeypatch.setenv("AT_API_KEY", "test_key")

        adapter = create_africas_talking_adapter(environment="sandbox")

        assert adapter.username == "sandbox"
        assert adapter.api_key == "test_key"
        assert adapter.environment == Environment.SANDBOX

    def test_create_adapter_missing_env(self, monkeypatch):
        """Test adapter creation fails with missing environment variables."""
        # Clear environment
        monkeypatch.delenv("AT_USERNAME", raising=False)
        monkeypatch.delenv("AT_API_KEY", raising=False)

        with pytest.raises(AfricasTalkingException):
            create_africas_talking_adapter()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
