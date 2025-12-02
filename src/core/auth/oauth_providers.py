"""
Multi-provider OAuth implementation supporting Google, GitHub, and Azure AD.

if://code/oauth-providers/2025-11-30

This module provides a unified interface for OAuth authentication across multiple
identity providers, abstracting provider-specific quirks and standardizing the
authentication flow through the PKCE OAuth pattern established in B31.

Architecture:
- OAuthProvider: Abstract base defining provider contract
- Concrete implementations: GoogleOAuthProvider, GitHubOAuthProvider, AzureADProvider
- ProviderRegistry: Factory for instantiating providers
- ProviderConfig: Configuration dataclass for provider setup
- MultiProviderOAuthClient: Unified client supporting all providers

Each provider handles its own:
- Authorization/token endpoints
- Default scopes
- Token response validation
- User information extraction
- Provider-specific quirks (response encoding, additional API calls, etc.)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Type, Any
import json
import requests
import jwt
from enum import Enum


class TokenResponse:
    """Standardized token response across all providers."""

    def __init__(
        self,
        access_token: str,
        token_type: str = "Bearer",
        expires_in: Optional[int] = None,
        refresh_token: Optional[str] = None,
        id_token: Optional[str] = None,
        user_email: Optional[str] = None,
        user_name: Optional[str] = None,
        user_id: Optional[str] = None,
        scope: Optional[str] = None,
    ):
        """
        Initialize token response.

        Args:
            access_token: The access token for API calls
            token_type: Token type (typically "Bearer")
            expires_in: Token expiration in seconds
            refresh_token: Refresh token (if supported by provider)
            id_token: ID token containing user claims (OIDC providers)
            user_email: User's email address
            user_name: User's display name or login
            user_id: Provider-specific user ID
            scope: Space-separated list of granted scopes
        """
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self.id_token = id_token
        self.user_email = user_email
        self.user_name = user_name
        self.user_id = user_id
        self.scope = scope

    def to_dict(self) -> Dict[str, Any]:
        """Convert token response to dictionary."""
        return {
            'access_token': self.access_token,
            'token_type': self.token_type,
            'expires_in': self.expires_in,
            'refresh_token': self.refresh_token,
            'id_token': self.id_token,
            'user_email': self.user_email,
            'user_name': self.user_name,
            'user_id': self.user_id,
            'scope': self.scope,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TokenResponse':
        """Create TokenResponse from dictionary."""
        return TokenResponse(
            access_token=data.get('access_token'),
            token_type=data.get('token_type', 'Bearer'),
            expires_in=data.get('expires_in'),
            refresh_token=data.get('refresh_token'),
            id_token=data.get('id_token'),
            user_email=data.get('user_email'),
            user_name=data.get('user_name'),
            user_id=data.get('user_id'),
            scope=data.get('scope'),
        )

    def __repr__(self) -> str:
        return (
            f"TokenResponse(user_email={self.user_email}, "
            f"token_type={self.token_type}, "
            f"expires_in={self.expires_in})"
        )


class OAuthProvider(ABC):
    """
    Abstract base class for OAuth providers.

    Defines the contract that all OAuth providers must implement,
    allowing for provider-agnostic authentication flows while supporting
    provider-specific quirks and requirements.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider identifier (e.g., 'google', 'github', 'azure')."""
        pass

    @property
    @abstractmethod
    def authorization_endpoint(self) -> str:
        """OAuth authorization endpoint URL."""
        pass

    @property
    @abstractmethod
    def token_endpoint(self) -> str:
        """OAuth token endpoint URL."""
        pass

    @abstractmethod
    def get_default_scopes(self) -> List[str]:
        """Get default OAuth scopes for this provider."""
        pass

    @abstractmethod
    def validate_token_response(self, response: Dict[str, Any]) -> TokenResponse:
        """
        Validate and normalize token response from provider.

        Each provider returns tokens in different formats and may require
        additional API calls to fetch user information. This method
        standardizes all responses into TokenResponse.

        Args:
            response: Raw response from token endpoint

        Returns:
            Normalized TokenResponse

        Raises:
            ValueError: If response is invalid or missing required fields
        """
        pass


class GoogleOAuthProvider(OAuthProvider):
    """
    Google OAuth provider.

    Google uses OpenID Connect and returns id_token with user claims.
    No separate API call needed for basic user info.

    Quirks:
    - Requires prompt=consent for refresh token on first auth
    - ID token contains user email and name
    - Refresh tokens don't expire
    - Returns JSON response (not form-encoded)
    """

    @property
    def provider_name(self) -> str:
        """Google provider identifier."""
        return "google"

    @property
    def authorization_endpoint(self) -> str:
        """Google authorization endpoint."""
        return "https://accounts.google.com/o/oauth2/v2/auth"

    @property
    def token_endpoint(self) -> str:
        """Google token endpoint."""
        return "https://oauth2.googleapis.com/token"

    def get_default_scopes(self) -> List[str]:
        """
        Google default scopes.

        Returns:
            List of default scopes: openid (required), profile, email
        """
        return ["openid", "profile", "email"]

    def validate_token_response(self, response: Dict[str, Any]) -> TokenResponse:
        """
        Validate Google token response.

        Google returns id_token as JWT with user claims. Decode it
        to extract user email and name without additional API call.

        Args:
            response: Response from Google token endpoint

        Returns:
            TokenResponse with user info extracted from id_token

        Raises:
            ValueError: If access_token or id_token missing
        """
        if 'access_token' not in response:
            raise ValueError("Missing access_token in Google response")

        token = TokenResponse(
            access_token=response['access_token'],
            token_type=response.get('token_type', 'Bearer'),
            expires_in=response.get('expires_in'),
            refresh_token=response.get('refresh_token'),
            id_token=response.get('id_token'),
            scope=response.get('scope'),
        )

        # Decode id_token to get user info
        if response.get('id_token'):
            try:
                # Don't verify signature here - token came from Google directly
                user_info = jwt.decode(
                    response['id_token'],
                    options={"verify_signature": False}
                )
                token.user_email = user_info.get('email')
                token.user_name = user_info.get('name')
                token.user_id = user_info.get('sub')
            except jwt.InvalidTokenError as e:
                raise ValueError(f"Invalid id_token from Google: {e}")

        return token


class GitHubOAuthProvider(OAuthProvider):
    """
    GitHub OAuth provider.

    GitHub uses traditional OAuth (not OIDC) and returns access token
    in form-encoded response. User info requires separate API call.

    Quirks:
    - Returns form-encoded response (not JSON)
    - No id_token (not OIDC compliant)
    - Requires separate /user API call for user info
    - No refresh tokens (access tokens don't expire)
    - Supports PAT (Personal Access Token) as fallback
    """

    @property
    def provider_name(self) -> str:
        """GitHub provider identifier."""
        return "github"

    @property
    def authorization_endpoint(self) -> str:
        """GitHub authorization endpoint."""
        return "https://github.com/login/oauth/authorize"

    @property
    def token_endpoint(self) -> str:
        """GitHub token endpoint."""
        return "https://github.com/login/oauth/access_token"

    def get_default_scopes(self) -> List[str]:
        """
        GitHub default scopes.

        Returns:
            List of default scopes: read:user (for profile), user:email
        """
        return ["read:user", "user:email"]

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Fetch user info from GitHub API.

        GitHub doesn't include user info in token response, so we need
        to make a separate API call to /user endpoint.

        Args:
            access_token: GitHub access token

        Returns:
            User info dictionary with login, email, id, etc.

        Raises:
            requests.RequestException: If API call fails
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        response = requests.get("https://api.github.com/user", headers=headers)
        response.raise_for_status()
        return response.json()

    def validate_token_response(self, response: Dict[str, Any]) -> TokenResponse:
        """
        Validate GitHub token response.

        GitHub returns form-encoded response (not JSON by default).
        This method expects response to already be parsed. It then
        fetches user info via API call.

        Args:
            response: Parsed response from GitHub token endpoint

        Returns:
            TokenResponse with user info from GitHub API

        Raises:
            ValueError: If access_token missing
            requests.RequestException: If user info API call fails
        """
        if 'access_token' not in response:
            raise ValueError("Missing access_token in GitHub response")

        token = TokenResponse(
            access_token=response['access_token'],
            token_type=response.get('token_type', 'Bearer'),
            scope=response.get('scope'),
            # GitHub tokens don't expire
            expires_in=None,
            refresh_token=None,  # GitHub doesn't support refresh tokens
        )

        # Fetch user info from GitHub API
        try:
            user_info = self.get_user_info(token.access_token)
            token.user_email = user_info.get('email')
            token.user_name = user_info.get('login')
            token.user_id = str(user_info.get('id'))
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch user info from GitHub: {e}")

        return token


class AzureADProvider(OAuthProvider):
    """
    Azure AD OAuth provider.

    Azure AD uses OAuth 2.0 and OpenID Connect. Supports both organizational
    and multi-tenant scenarios through tenant_id parameter.

    Quirks:
    - Tenant-specific endpoints (common, organizations, or specific GUID)
    - Requires 'offline_access' scope for refresh token
    - ID token is OIDC standard (JWT)
    - Supports refresh token rotation
    - Returns JSON response
    """

    def __init__(self, tenant_id: str = "common"):
        """
        Initialize Azure AD provider.

        Args:
            tenant_id: Azure AD tenant ID (default: 'common' for multi-tenant)
                      Can be: 'common', 'organizations', or specific GUID
        """
        self.tenant_id = tenant_id

    @property
    def provider_name(self) -> str:
        """Azure AD provider identifier."""
        return "azure"

    @property
    def authorization_endpoint(self) -> str:
        """Azure AD authorization endpoint (tenant-specific)."""
        return f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"

    @property
    def token_endpoint(self) -> str:
        """Azure AD token endpoint (tenant-specific)."""
        return f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

    def get_default_scopes(self) -> List[str]:
        """
        Azure AD default scopes.

        Returns:
            List of default scopes: openid, profile, email, offline_access
            (offline_access enables refresh token)
        """
        return ["openid", "profile", "email", "offline_access"]

    def validate_token_response(self, response: Dict[str, Any]) -> TokenResponse:
        """
        Validate Azure AD token response.

        Azure returns standard OIDC response with id_token JWT.
        Decode id_token to extract user claims.

        Args:
            response: Response from Azure AD token endpoint

        Returns:
            TokenResponse with user info from id_token

        Raises:
            ValueError: If required fields missing
        """
        if 'access_token' not in response:
            raise ValueError("Missing access_token in Azure AD response")

        token = TokenResponse(
            access_token=response['access_token'],
            token_type=response.get('token_type', 'Bearer'),
            expires_in=response.get('expires_in'),
            refresh_token=response.get('refresh_token'),
            id_token=response.get('id_token'),
            scope=response.get('scope'),
        )

        # Decode id_token for user info
        if response.get('id_token'):
            try:
                user_info = jwt.decode(
                    response['id_token'],
                    options={"verify_signature": False}
                )
                token.user_email = user_info.get('email')
                token.user_name = user_info.get('name')
                token.user_id = user_info.get('oid')  # Azure uses 'oid' for user ID
            except jwt.InvalidTokenError as e:
                raise ValueError(f"Invalid id_token from Azure AD: {e}")

        return token


@dataclass
class ProviderConfig:
    """
    Configuration for a specific OAuth provider instance.

    Stores provider credentials, endpoints, and customization options.
    Note: client_secret is optional since PKCE flow doesn't require it.
    """

    provider_name: str
    """Provider identifier (google, github, azure, etc.)"""

    client_id: str
    """OAuth application client ID"""

    redirect_uri: str
    """OAuth redirect URI (callback URL)"""

    client_secret: Optional[str] = None
    """OAuth client secret (optional for PKCE, required for traditional OAuth)"""

    additional_params: Dict[str, str] = field(default_factory=dict)
    """Provider-specific additional parameters"""

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            'provider_name': self.provider_name,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'additional_params': self.additional_params,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ProviderConfig':
        """
        Create configuration from dictionary.

        Args:
            data: Dictionary with configuration fields

        Returns:
            ProviderConfig instance
        """
        return ProviderConfig(
            provider_name=data['provider_name'],
            client_id=data['client_id'],
            redirect_uri=data['redirect_uri'],
            client_secret=data.get('client_secret'),
            additional_params=data.get('additional_params', {}),
        )


class ProviderRegistry:
    """
    Factory and registry for OAuth providers.

    Manages provider instantiation and allows dynamic provider registration.
    Implements the factory pattern for clean provider instantiation.
    """

    _providers: Dict[str, Type[OAuthProvider]] = {
        "google": GoogleOAuthProvider,
        "github": GitHubOAuthProvider,
        "azure": AzureADProvider,
    }

    @classmethod
    def get_provider(cls, provider_name: str, **kwargs) -> OAuthProvider:
        """
        Get provider instance by name.

        Factory method that instantiates the appropriate provider
        class with the given keyword arguments.

        Args:
            provider_name: Provider identifier (google, github, azure, etc.)
            **kwargs: Provider-specific initialization arguments

        Returns:
            OAuthProvider instance

        Raises:
            ValueError: If provider not found in registry
            TypeError: If provider instantiation fails
        """
        if provider_name not in cls._providers:
            available = ', '.join(cls.list_providers())
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available: {available}"
            )

        try:
            provider_class = cls._providers[provider_name]
            return provider_class(**kwargs)
        except TypeError as e:
            raise TypeError(
                f"Failed to instantiate {provider_name} provider: {e}"
            )

    @classmethod
    def list_providers(cls) -> List[str]:
        """
        List all registered provider names.

        Returns:
            List of provider identifiers
        """
        return list(cls._providers.keys())

    @classmethod
    def register_provider(
        cls,
        name: str,
        provider_class: Type[OAuthProvider]
    ) -> None:
        """
        Register a custom OAuth provider.

        Allows dynamic registration of additional providers beyond
        the built-in Google, GitHub, and Azure AD providers.

        Args:
            name: Provider identifier to use
            provider_class: OAuthProvider subclass

        Raises:
            TypeError: If provider_class is not an OAuthProvider subclass
        """
        if not issubclass(provider_class, OAuthProvider):
            raise TypeError(
                f"{provider_class} must be a subclass of OAuthProvider"
            )

        cls._providers[name] = provider_class


class MultiProviderOAuthClient:
    """
    Unified OAuth client supporting multiple providers.

    Integrates with OAuthPKCEClient to provide a unified authentication
    interface across different OAuth providers, handling provider-specific
    quirks transparently.
    """

    def __init__(
        self,
        provider: OAuthProvider,
        config: ProviderConfig,
        pkce_client=None,
    ):
        """
        Initialize multi-provider OAuth client.

        Args:
            provider: OAuthProvider instance
            config: ProviderConfig instance
            pkce_client: OAuthPKCEClient instance (for dependency injection in tests)
        """
        self.provider = provider
        self.config = config
        self.pkce_client = pkce_client

    def authenticate(self) -> TokenResponse:
        """
        Perform OAuth authentication flow.

        Initiates the OAuth flow with PKCE, then validates and normalizes
        the response through provider-specific validation logic.

        Returns:
            TokenResponse with authenticated user info

        Raises:
            ValueError: If authentication fails or response is invalid
        """
        if not self.pkce_client:
            raise RuntimeError(
                "PKCE client not initialized. "
                "Create with pkce_client parameter or use with_pkce_client()"
            )

        # Get default scopes from provider
        scopes = self.provider.get_default_scopes()

        # Add any additional params from config
        additional_params = dict(self.config.additional_params)
        if self.provider.provider_name == "google":
            additional_params.setdefault('prompt', 'consent')

        # Initiate PKCE flow
        token_dict = self.pkce_client.initiate_flow(scopes, **additional_params)

        # Provider-specific validation and normalization
        return self.provider.validate_token_response(token_dict)

    def with_pkce_client(self, pkce_client) -> 'MultiProviderOAuthClient':
        """
        Set PKCE client (builder pattern).

        Args:
            pkce_client: OAuthPKCEClient instance

        Returns:
            Self for method chaining
        """
        self.pkce_client = pkce_client
        return self


# CLI Usage example (not executed)
"""
from infrafabric.auth import ProviderRegistry, ProviderConfig, MultiProviderOAuthClient

# List available providers
providers = ProviderRegistry.list_providers()
print(f"Available providers: {', '.join(providers)}")

# User selects provider
selected = input("Select provider (google/github/azure): ").strip().lower()

# Get provider instance
provider = ProviderRegistry.get_provider(selected)
if selected == "azure":
    tenant_id = input("Azure tenant ID (default: common): ").strip() or "common"
    provider = ProviderRegistry.get_provider("azure", tenant_id=tenant_id)

# Configure
config = ProviderConfig(
    provider_name=selected,
    client_id="infrafabric-cli",
    redirect_uri="http://localhost:8080/callback",
    additional_params={
        "access_type": "offline" if selected == "google" else "",
    }
)

# Authenticate
client = MultiProviderOAuthClient(provider, config, pkce_client=pkce_client_instance)
token = client.authenticate()

print(f"Authenticated as {token.user_email}")
print(f"Token expires in {token.expires_in} seconds")
print(f"Refresh token available: {token.refresh_token is not None}")
"""
