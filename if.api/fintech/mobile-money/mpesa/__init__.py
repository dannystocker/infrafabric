"""
M-Pesa Daraja API Adapter

Production-ready Python adapter for Safaricom's M-Pesa Daraja API v1.
Provides functionality for payment collections, disbursements, and transaction queries
with built-in IF.bus event integration.

Usage:
    from if.api.fintech.mobile_money.mpesa import MpesaAdapter, Environment

    adapter = MpesaAdapter(
        consumer_key="your_key",
        consumer_secret="your_secret",
        business_shortcode="123456",
        passkey="your_passkey",
        environment=Environment.SANDBOX
    )

    result = adapter.initiate_stk_push(
        phone_number="254712345678",
        amount=100.0,
        account_reference="INV001"
    )
"""

from .mpesa_adapter import (
    MpesaAdapter,
    MpesaException,
    MpesaAuthException,
    MpesaAPIException,
    MpesaEventEmitter,
    Environment,
    TransactionStatus,
    create_mpesa_adapter
)

from .config import (
    MpesaConfig,
    PaymentType,
    CommandID,
    IdentifierType,
    PhoneNumberValidator,
    AmountValidator,
    TransactionCodec,
    EventNameConstants,
    APIEndpointConstants,
    ResultCodes
)

__version__ = "1.0.0"
__author__ = "InfraFabric Team"
__license__ = "Proprietary"

__all__ = [
    # Main adapter
    "MpesaAdapter",
    "create_mpesa_adapter",

    # Exceptions
    "MpesaException",
    "MpesaAuthException",
    "MpesaAPIException",

    # Events
    "MpesaEventEmitter",

    # Enums
    "Environment",
    "TransactionStatus",
    "PaymentType",
    "CommandID",
    "IdentifierType",

    # Configuration
    "MpesaConfig",

    # Utilities
    "PhoneNumberValidator",
    "AmountValidator",
    "TransactionCodec",
    "EventNameConstants",
    "APIEndpointConstants",
    "ResultCodes"
]
