# if://code/oauth-relay-auth-init/2025-11-30
# Auth module initialization
# Exports OAuth relay server components, PKCE client, and token refresh automation

from .oauth_relay_server import (
    OAuthRelayServer,
    OAuthRelayClient,
    DeviceRegistration,
    TokenResponse as RelayTokenResponse,
    TokenStatus,
    DeviceRegistrationRequest,
    ActivationRequest,
    PollTokenRequest,
    RateLimiter,
)

from .oauth_pkce import (
    OAuthPKCEClient,
    TokenResponse,
    PKCEChallenge,
    CallbackServer,
    CallbackHandler,
    OAuthException,
    AuthorizationDenied,
    CallbackTimeout,
    TokenExchangeError,
    InvalidState,
    save_token,
    load_token,
)

from .token_refresh import (
    TokenRefreshManager,
    TokenResponse as RefreshTokenResponse,
    TokenStorage,
    FileTokenStorage,
    RefreshMetrics,
    NotAuthenticatedError,
    RefreshError,
    make_authenticated_request,
)

__all__ = [
    # OAuth Relay Server
    "OAuthRelayServer",
    "OAuthRelayClient",
    "DeviceRegistration",
    "RelayTokenResponse",
    "TokenStatus",
    "DeviceRegistrationRequest",
    "ActivationRequest",
    "PollTokenRequest",
    "RateLimiter",
    # OAuth PKCE Client
    "OAuthPKCEClient",
    "TokenResponse",
    "PKCEChallenge",
    "CallbackServer",
    "CallbackHandler",
    "OAuthException",
    "AuthorizationDenied",
    "CallbackTimeout",
    "TokenExchangeError",
    "InvalidState",
    "save_token",
    "load_token",
    # Token Refresh Automation
    "TokenRefreshManager",
    "RefreshTokenResponse",
    "TokenStorage",
    "FileTokenStorage",
    "RefreshMetrics",
    "NotAuthenticatedError",
    "RefreshError",
    "make_authenticated_request",
]

__version__ = "2.0.0"
