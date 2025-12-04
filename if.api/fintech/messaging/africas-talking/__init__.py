"""
Africa's Talking API Adapter for InfraFabric

Production-ready adapter for Africa's Talking services supporting SMS, USSD,
Voice, Airtime, and Payments across multiple African countries.
"""

from africas_talking_adapter import (
    AfricasTalkingAdapter,
    AfricasTalkingEventEmitter,
    AfricasTalkingException,
    AfricasTalkingAuthException,
    AfricasTalkingAPIException,
    Environment,
    DeliveryStatus,
    USSDSessionStatus,
    CallStatus,
    AirtimeStatus,
    create_africas_talking_adapter
)

from config import (
    AfricasTalkingConfig,
    Country,
    CountryConfig,
    COUNTRY_CONFIGS,
    SMSEncodingType,
    VoiceCallReason,
    PaymentProvider,
    PaymentReason,
    PhoneNumberValidator,
    SMSValidator,
    AirtimeValidator,
    EventNameConstants,
    APIEndpointConstants,
    SMSTemplates,
    DEFAULT_SANDBOX_CONFIG
)


__version__ = "1.0.0"
__author__ = "InfraFabric Team"
__all__ = [
    # Main adapter
    'AfricasTalkingAdapter',
    'create_africas_talking_adapter',

    # Event emitter
    'AfricasTalkingEventEmitter',

    # Exceptions
    'AfricasTalkingException',
    'AfricasTalkingAuthException',
    'AfricasTalkingAPIException',

    # Enums
    'Environment',
    'DeliveryStatus',
    'USSDSessionStatus',
    'CallStatus',
    'AirtimeStatus',
    'Country',
    'SMSEncodingType',
    'VoiceCallReason',
    'PaymentProvider',
    'PaymentReason',

    # Configuration
    'AfricasTalkingConfig',
    'CountryConfig',
    'COUNTRY_CONFIGS',
    'DEFAULT_SANDBOX_CONFIG',

    # Validators
    'PhoneNumberValidator',
    'SMSValidator',
    'AirtimeValidator',

    # Constants
    'EventNameConstants',
    'APIEndpointConstants',

    # Templates
    'SMSTemplates',
]
