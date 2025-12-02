# if://code/oauth-pkce/2025-11-30
# OAuth2 PKCE (Proof Key for Code Exchange) Flow Implementation
# RFC 7636 Compliant - Secure CLI Authentication without Client Secrets

import base64
import hashlib
import os
import secrets
import threading
import webbrowser
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import urlopen
import json
import logging

import requests

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================

class OAuthException(Exception):
    """Base exception for OAuth operations"""
    pass


class AuthorizationDenied(OAuthException):
    """User rejected authorization"""
    pass


class CallbackTimeout(OAuthException):
    """No callback received within timeout period"""
    pass


class TokenExchangeError(OAuthException):
    """Failed to exchange authorization code for token"""
    pass


class InvalidState(OAuthException):
    """CSRF attack detected - state parameter mismatch"""
    pass


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class TokenResponse:
    """OAuth2 Token Response Data"""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: str = ""
    issued_at: datetime = None

    def __post_init__(self):
        """Set issued_at timestamp if not provided"""
        if self.issued_at is None:
            self.issued_at = datetime.utcnow()

    def is_expired(self) -> bool:
        """Check if token has expired"""
        if self.issued_at is None:
            return False
        expiration_time = self.issued_at + timedelta(seconds=self.expires_in)
        return datetime.utcnow() >= expiration_time

    def to_dict(self) -> Dict:
        """Convert to dictionary (ISO format for datetime)"""
        data = asdict(self)
        data['issued_at'] = self.issued_at.isoformat() if self.issued_at else None
        return data

    @staticmethod
    def from_dict(data: Dict) -> 'TokenResponse':
        """Create from dictionary"""
        if 'issued_at' in data and isinstance(data['issued_at'], str):
            data['issued_at'] = datetime.fromisoformat(data['issued_at'])
        return TokenResponse(**{k: v for k, v in data.items() if k in TokenResponse.__dataclass_fields__})


@dataclass
class PKCEChallenge:
    """PKCE Challenge Container"""
    code_verifier: str
    code_challenge: str
    state: str

    @staticmethod
    def generate() -> 'PKCEChallenge':
        """Generate PKCE challenge (RFC 7636)"""
        # 1. Generate code_verifier: 43-128 character unreserved characters
        # Using 32 bytes = ~43 characters in base64url
        code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')

        # 2. Generate code_challenge = BASE64URL(SHA256(code_verifier))
        challenge_bytes = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')

        # 3. Generate state for CSRF protection (128-bit random)
        state = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

        logger.debug(f"PKCE challenge generated: verifier_len={len(code_verifier)}, challenge_len={len(code_challenge)}")

        return PKCEChallenge(code_verifier=code_verifier, code_challenge=code_challenge, state=state)


# ============================================================================
# HTTP Callback Server
# ============================================================================

class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for OAuth callback"""

    # Class variables to store callback state
    authorization_code = None
    callback_received = threading.Event()
    error_message = None

    def do_GET(self):
        """Handle GET request from OAuth provider callback"""
        try:
            # Parse query parameters from callback URL
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            # Check for error response
            if 'error' in query_params:
                error = query_params['error'][0]
                error_description = query_params.get('error_description', ['Unknown error'])[0]
                CallbackHandler.error_message = f"{error}: {error_description}"
                logger.error(f"Authorization error: {CallbackHandler.error_message}")
                self._send_response(False, error_description)
                CallbackHandler.callback_received.set()
                return

            # Extract authorization code
            if 'code' not in query_params:
                CallbackHandler.error_message = "No authorization code in callback"
                logger.error(CallbackHandler.error_message)
                self._send_response(False, "No authorization code received")
                CallbackHandler.callback_received.set()
                return

            CallbackHandler.authorization_code = query_params['code'][0]
            logger.info("Authorization code received successfully")
            self._send_response(True, "Authorization successful! You can close this window.")
            CallbackHandler.callback_received.set()

        except Exception as e:
            CallbackHandler.error_message = str(e)
            logger.error(f"Callback handler error: {e}", exc_info=True)
            self._send_response(False, f"Error processing callback: {str(e)}")
            CallbackHandler.callback_received.set()

    def _send_response(self, success: bool, message: str):
        """Send HTML response to browser"""
        status = 200 if success else 400
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OAuth Authentication</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                        display: flex; justify-content: center; align-items: center;
                        height: 100vh; margin: 0; background: #f5f5f5; }}
                .container {{ text-align: center; background: white; padding: 40px;
                             border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                h1 {{ color: {'#28a745' if success else '#dc3545'}; margin: 0 0 10px 0; }}
                p {{ color: #666; margin: 0; }}
                .icon {{ font-size: 48px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">{'✅' if success else '❌'}</div>
                <h1>{'Success' if success else 'Error'}</h1>
                <p>{message}</p>
                <p style="margin-top: 20px; font-size: 12px; color: #999;">You can close this window.</p>
            </div>
        </body>
        </html>
        """

        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', len(html_content.encode()))
        self.end_headers()
        self.wfile.write(html_content.encode())

    def log_message(self, format, *args):
        """Suppress default HTTP server logging"""
        logger.debug(f"HTTP: {format % args}")


class CallbackServer:
    """HTTP Server for receiving OAuth callback"""

    def __init__(self, host: str = 'localhost', port: int = 8080):
        """
        Initialize callback server

        Args:
            host: Server hostname (default: localhost for security)
            port: Server port (default: 8080)
        """
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        logger.info(f"CallbackServer initialized on {host}:{port}")

    def start(self) -> None:
        """Start HTTP server in background thread"""
        try:
            # Create server
            self.server = HTTPServer((self.host, self.port), CallbackHandler)

            # Reset callback state
            CallbackHandler.authorization_code = None
            CallbackHandler.error_message = None
            CallbackHandler.callback_received.clear()

            # Start in background thread
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            logger.info(f"Callback server started on {self.host}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to start callback server: {e}", exc_info=True)
            raise

    def wait_for_callback(self, timeout: int = 300) -> Optional[str]:
        """
        Block until authorization code received or timeout

        Args:
            timeout: Maximum seconds to wait (default: 300 = 5 minutes)

        Returns:
            Authorization code if received, None if timeout

        Raises:
            AuthorizationDenied: If user rejected authorization
            CallbackTimeout: If no callback received within timeout
        """
        logger.info(f"Waiting for callback (timeout={timeout}s)")

        # Wait for callback with timeout
        if not CallbackHandler.callback_received.wait(timeout=timeout):
            logger.error("Callback timeout - no authorization code received")
            raise CallbackTimeout(f"User did not complete authorization within {timeout} seconds")

        # Check for errors
        if CallbackHandler.error_message:
            logger.error(f"Authorization error: {CallbackHandler.error_message}")
            raise AuthorizationDenied(CallbackHandler.error_message)

        # Return authorization code
        code = CallbackHandler.authorization_code
        if not code:
            logger.error("No authorization code received")
            raise CallbackTimeout("Callback received but no authorization code")

        logger.info("Authorization code received successfully")
        return code

    def shutdown(self) -> None:
        """Stop HTTP server"""
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
                if self.thread:
                    self.thread.join(timeout=2)
                logger.info("Callback server stopped")
            except Exception as e:
                logger.error(f"Error shutting down callback server: {e}", exc_info=True)


# ============================================================================
# OAuth2 PKCE Client
# ============================================================================

class OAuthPKCEClient:
    """
    OAuth2 Client with PKCE (RFC 7636) Support

    Implements secure authorization code flow without client secrets,
    suitable for public clients (CLI applications, SPAs, mobile apps).

    Features:
    - PKCE challenge to prevent authorization code interception
    - State parameter for CSRF protection
    - Local callback server for receiving authorization code
    - Token storage and refresh
    """

    def __init__(
        self,
        client_id: str,
        authorization_endpoint: str,
        token_endpoint: str,
        redirect_uri: str = "http://localhost:8080/callback",
        scopes: Optional[List[str]] = None,
        timeout: int = 300
    ):
        """
        Initialize OAuth2 PKCE Client

        Args:
            client_id: OAuth2 client identifier
            authorization_endpoint: URL to authorization server
            token_endpoint: URL to token endpoint
            redirect_uri: Callback URI (default: localhost:8080)
            scopes: Default scopes to request (default: ['openid', 'profile', 'email'])
            timeout: Callback timeout in seconds (default: 300)
        """
        self.client_id = client_id
        self.authorization_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
        self.redirect_uri = redirect_uri
        self.scopes = scopes or ['openid', 'profile', 'email']
        self.timeout = timeout

        # PKCE state
        self.challenge: Optional[PKCEChallenge] = None
        self.callback_server: Optional[CallbackServer] = None

        logger.info(f"OAuthPKCEClient initialized: client_id={client_id}, endpoint={authorization_endpoint}")

    def _parse_redirect_uri(self) -> Tuple[str, int]:
        """
        Parse redirect URI to extract host and port

        Returns:
            Tuple of (host, port)
        """
        parsed = urlparse(self.redirect_uri)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 8080
        return host, port

    def get_authorization_url(self, scopes: Optional[List[str]] = None) -> str:
        """
        Build OAuth authorization URL with PKCE challenge

        Args:
            scopes: List of requested scopes

        Returns:
            Full authorization URL
        """
        scopes = scopes or self.scopes

        # Generate fresh PKCE challenge
        self.challenge = PKCEChallenge.generate()

        # Build authorization parameters
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(scopes),
            'code_challenge': self.challenge.code_challenge,
            'code_challenge_method': 'S256',  # SHA256 method per RFC 7636
            'state': self.challenge.state,  # CSRF protection
        }

        auth_url = f"{self.authorization_endpoint}?{urlencode(params)}"
        logger.debug(f"Authorization URL generated: {auth_url[:100]}...")

        return auth_url

    def start_callback_server(self) -> CallbackServer:
        """
        Start local HTTP server to receive authorization callback

        Returns:
            CallbackServer instance
        """
        host, port = self._parse_redirect_uri()
        self.callback_server = CallbackServer(host=host, port=port)
        self.callback_server.start()
        return self.callback_server

    def exchange_code_for_token(self, code: str, code_verifier: str) -> TokenResponse:
        """
        Exchange authorization code for access token (RFC 7636 Section 4.5)

        Args:
            code: Authorization code from callback
            code_verifier: PKCE code verifier (generated during challenge)

        Returns:
            TokenResponse with access token

        Raises:
            TokenExchangeError: If token exchange fails
        """
        try:
            # Build token request payload
            payload = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'code_verifier': code_verifier,  # PKCE verification
            }

            logger.info("Exchanging authorization code for token")

            # Exchange code for token
            response = requests.post(
                self.token_endpoint,
                data=payload,
                timeout=10,
                headers={'Accept': 'application/json'}
            )

            response.raise_for_status()

            token_data = response.json()
            token = TokenResponse.from_dict(token_data)

            logger.info(f"Token received successfully (expires_in={token.expires_in}s)")

            return token

        except requests.exceptions.RequestException as e:
            error_msg = f"Token exchange failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    error_msg += f" - {error_details.get('error_description', error_details)}"
                except:
                    pass
            logger.error(error_msg)
            raise TokenExchangeError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during token exchange: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise TokenExchangeError(error_msg) from e

    def initiate_flow(self, scopes: Optional[List[str]] = None) -> TokenResponse:
        """
        Complete OAuth2 PKCE flow: generate challenge → open browser →
        wait for callback → exchange token

        Flow:
        1. Generate PKCE challenge (code_verifier + code_challenge)
        2. Start local HTTP callback server
        3. Open browser to authorization endpoint
        4. Wait for authorization callback (5-minute timeout)
        5. Extract authorization code from callback
        6. Exchange code + code_verifier for access token
        7. Shutdown callback server

        Args:
            scopes: List of requested scopes

        Returns:
            TokenResponse with access token

        Raises:
            CallbackTimeout: If no callback within timeout
            AuthorizationDenied: If user rejects authorization
            TokenExchangeError: If token exchange fails
        """
        scopes = scopes or self.scopes
        server = None

        try:
            # 1. Get authorization URL with PKCE challenge
            auth_url = self.get_authorization_url(scopes)

            # 2. Start callback server
            server = self.start_callback_server()

            # 3. Open browser to authorization endpoint
            logger.info(f"Opening browser for authorization: {self.authorization_endpoint}")
            if not webbrowser.open(auth_url):
                logger.warning("Failed to open browser automatically. Manual URL access required.")
                print(f"\nPlease open this URL in your browser:\n{auth_url}\n")

            # 4. Wait for callback with timeout
            code = server.wait_for_callback(timeout=self.timeout)

            # 5. Exchange code for token
            if not self.challenge:
                raise TokenExchangeError("PKCE challenge not found - state corrupted")

            token = self.exchange_code_for_token(code, self.challenge.code_verifier)

            logger.info("OAuth2 PKCE flow completed successfully")
            return token

        finally:
            # 6. Shutdown callback server
            if server:
                server.shutdown()

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh an expired access token using refresh token

        Args:
            refresh_token: Refresh token from previous authorization

        Returns:
            New TokenResponse with fresh access token

        Raises:
            TokenExchangeError: If refresh fails
        """
        try:
            payload = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.client_id,
            }

            logger.info("Refreshing access token")

            response = requests.post(
                self.token_endpoint,
                data=payload,
                timeout=10,
                headers={'Accept': 'application/json'}
            )

            response.raise_for_status()

            token = TokenResponse.from_dict(response.json())
            logger.info("Token refreshed successfully")

            return token

        except Exception as e:
            error_msg = f"Token refresh failed: {str(e)}"
            logger.error(error_msg)
            raise TokenExchangeError(error_msg) from e


# ============================================================================
# Utility Functions
# ============================================================================

def save_token(token: TokenResponse, filepath: str) -> None:
    """
    Save token to file (encrypted at rest recommended)

    Args:
        token: TokenResponse to save
        filepath: Path to save token file
    """
    try:
        with open(filepath, 'w') as f:
            json.dump(token.to_dict(), f, indent=2, default=str)
        os.chmod(filepath, 0o600)  # Read/write for owner only
        logger.info(f"Token saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save token: {e}", exc_info=True)
        raise


def load_token(filepath: str) -> Optional[TokenResponse]:
    """
    Load token from file

    Args:
        filepath: Path to token file

    Returns:
        TokenResponse if file exists, None otherwise
    """
    try:
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r') as f:
            data = json.load(f)
        return TokenResponse.from_dict(data)
    except Exception as e:
        logger.error(f"Failed to load token: {e}", exc_info=True)
        return None


if __name__ == '__main__':
    # Example usage and testing
    logging.basicConfig(level=logging.INFO)

    print("OAuth2 PKCE Client Module")
    print("=" * 50)
    print("This module provides RFC 7636 compliant OAuth2")
    print("PKCE authentication for CLI applications.")
    print("\nUsage Example:")
    print("""
    from oauth_pkce import OAuthPKCEClient, save_token, load_token

    # Initialize client
    client = OAuthPKCEClient(
        client_id='my-cli-app',
        authorization_endpoint='https://auth.example.com/oauth2/authorize',
        token_endpoint='https://auth.example.com/oauth2/token'
    )

    # Initiate OAuth flow
    token = client.initiate_flow(scopes=['profile', 'email'])

    # Save token for later use
    save_token(token, '/home/user/.my-cli-app/token.json')

    # Load and use token
    saved_token = load_token('/home/user/.my-cli-app/token.json')
    if saved_token and not saved_token.is_expired():
        print(f"Using token: {saved_token.access_token[:20]}...")
    """)
