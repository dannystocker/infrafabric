"""
Airtel Money Africa API Adapter Package

Production-ready adapter for Airtel Money APIs covering 14 African countries.

Author: InfraFabric Finance Team
Version: 1.0.0
Date: 2025-12-04
"""

from .airtel_money_adapter import (
    AirtelMoneyAdapter,
    CountryCode,
    Currency,
    TransactionStatus,
    TransactionType,
    SubscriberInfo,
    TransactionMetadata,
    KYCInfo,
    AirtelMoneyError,
    AuthenticationError,
    APIError,
    ValidationError,
    CallbackError,
    InsufficientBalanceError,
)

from .config import (
    AirtelMoneyConfig,
    CountryConfig,
    APIEndpoints,
    TransactionLimits,
    get_country_config,
    list_supported_countries,
    validate_phone_number,
    validate_amount,
    COUNTRIES,
)

__version__ = "1.0.0"
__author__ = "InfraFabric Finance Team"
__all__ = [
    # Adapter
    "AirtelMoneyAdapter",

    # Enums
    "CountryCode",
    "Currency",
    "TransactionStatus",
    "TransactionType",

    # Data Classes
    "SubscriberInfo",
    "TransactionMetadata",
    "KYCInfo",

    # Exceptions
    "AirtelMoneyError",
    "AuthenticationError",
    "APIError",
    "ValidationError",
    "CallbackError",
    "InsufficientBalanceError",

    # Configuration
    "AirtelMoneyConfig",
    "CountryConfig",
    "APIEndpoints",
    "TransactionLimits",
    "get_country_config",
    "list_supported_countries",
    "validate_phone_number",
    "validate_amount",
    "COUNTRIES",
]
