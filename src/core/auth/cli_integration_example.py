#!/usr/bin/env python3
# if://code/oauth-pkce-cli-integration/2025-11-30
"""
OAuth2 PKCE CLI Integration Example

This module demonstrates how to integrate OAuth2 PKCE authentication
into a CLI application. It includes:

1. Argument parsing for auth subcommands
2. Secure token storage and retrieval
3. Automatic token refresh
4. Authenticated API requests
5. Login/logout workflow
6. Error handling and user feedback
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Note: This is a demonstration - adjust imports for your CLI structure
from oauth_pkce import (
    OAuthPKCEClient,
    TokenResponse,
    save_token,
    load_token,
    AuthorizationDenied,
    CallbackTimeout,
    TokenExchangeError,
)


# ============================================================================
# Configuration
# ============================================================================

# OAuth Configuration
OAUTH_CONFIG = {
    'client_id': 'infrafabric-cli',
    'authorization_endpoint': 'https://accounts.google.com/o/oauth2/v2/auth',
    'token_endpoint': 'https://oauth2.googleapis.com/token',
    'redirect_uri': 'http://localhost:8080/callback',
}

# Token storage location
TOKEN_DIR = Path.home() / '.infrafabric'
TOKEN_FILE = TOKEN_DIR / 'token.json'

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Utility Functions
# ============================================================================

def ensure_token_dir() -> None:
    """Create token directory if it doesn't exist"""
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    # Restrict permissions to owner only
    TOKEN_DIR.chmod(0o700)


def is_authenticated() -> bool:
    """Check if user has valid authentication token"""
    token = load_token(str(TOKEN_FILE))
    return token is not None and not token.is_expired()


def get_valid_token() -> Optional[TokenResponse]:
    """
    Get a valid authentication token.

    If token is expired, attempt refresh. If refresh fails,
    return None (user needs to re-authenticate).
    """
    token = load_token(str(TOKEN_FILE))

    if token is None:
        return None

    if token.is_expired():
        logger.info("Token expired - attempting refresh...")
        try:
            client = OAuthPKCEClient(**OAUTH_CONFIG)
            if token.refresh_token:
                token = client.refresh_token(token.refresh_token)
                save_token(token, str(TOKEN_FILE))
                logger.info("Token refreshed successfully")
                return token
            else:
                logger.warning("No refresh token available")
                return None
        except TokenExchangeError as e:
            logger.error(f"Token refresh failed: {e}")
            return None

    return token


# ============================================================================
# Command Handlers
# ============================================================================

def handle_login(args) -> int:
    """
    Handle login command - initiate OAuth flow

    Returns:
        0 on success, 1 on failure
    """
    ensure_token_dir()

    # Check if already authenticated
    if is_authenticated():
        print("Already authenticated! Use 'logout' to sign out.")
        return 0

    print("Initiating authentication...")
    print("A browser window will open for you to authorize access.")

    try:
        # Create OAuth client
        client = OAuthPKCEClient(**OAUTH_CONFIG)

        # Initiate PKCE flow
        token = client.initiate_flow(
            scopes=['openid', 'profile', 'email']
        )

        # Save token
        save_token(token, str(TOKEN_FILE))

        print("\n✓ Authentication successful!")
        print(f"  Token expires in {token.expires_in} seconds")
        print(f"  Refresh token available: {bool(token.refresh_token)}")

        return 0

    except AuthorizationDenied as e:
        print(f"✗ Authorization denied: {e}")
        return 1

    except CallbackTimeout as e:
        print(f"✗ Authentication timeout: {e}")
        print("  Please try again.")
        return 1

    except TokenExchangeError as e:
        print(f"✗ Token exchange failed: {e}")
        print("  Please check your credentials and try again.")
        return 1

    except Exception as e:
        logger.error(f"Unexpected error during login: {e}", exc_info=True)
        print(f"✗ Unexpected error: {e}")
        return 1


def handle_logout(args) -> int:
    """
    Handle logout command - remove saved token

    Returns:
        0 on success, 1 on failure
    """
    try:
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
            print("✓ Logged out successfully")
        else:
            print("Not currently authenticated")
        return 0

    except Exception as e:
        print(f"✗ Error during logout: {e}")
        return 1


def handle_status(args) -> int:
    """
    Handle status command - show authentication status

    Returns:
        0 if authenticated, 1 if not
    """
    token = load_token(str(TOKEN_FILE))

    if token is None:
        print("✗ Not authenticated")
        print("  Run 'login' to authenticate")
        return 1

    if token.is_expired():
        print("✗ Token expired")
        print("  Run 'login' to authenticate again")
        return 1

    print("✓ Authenticated")
    print(f"  Token type: {token.token_type}")
    print(f"  Scopes: {token.scope}")
    print(f"  Token expires in approximately {int(token.expires_in / 60)} minutes")
    print(f"  Refresh available: {bool(token.refresh_token)}")

    return 0


def handle_refresh(args) -> int:
    """
    Handle token refresh command

    Returns:
        0 on success, 1 on failure
    """
    token = load_token(str(TOKEN_FILE))

    if token is None:
        print("✗ Not authenticated - run 'login' first")
        return 1

    if not token.refresh_token:
        print("✗ No refresh token available")
        print("  Run 'login' to authenticate again")
        return 1

    print("Refreshing token...")

    try:
        client = OAuthPKCEClient(**OAUTH_CONFIG)
        new_token = client.refresh_token(token.refresh_token)
        save_token(new_token, str(TOKEN_FILE))

        print("✓ Token refreshed successfully")
        print(f"  New token expires in {new_token.expires_in} seconds")

        return 0

    except TokenExchangeError as e:
        print(f"✗ Token refresh failed: {e}")
        print("  Run 'login' to authenticate again")
        return 1

    except Exception as e:
        logger.error(f"Unexpected error during refresh: {e}", exc_info=True)
        print(f"✗ Unexpected error: {e}")
        return 1


def handle_token(args) -> int:
    """
    Handle token command - show access token (for debugging)

    Returns:
        0 on success, 1 on failure
    """
    token = get_valid_token()

    if token is None:
        print("✗ Not authenticated - run 'login' first")
        return 1

    if args.show_secret:
        print(f"Access Token: {token.access_token}")
    else:
        # Show partial token for security
        partial = f"{token.access_token[:20]}...{token.access_token[-10:]}"
        print(f"Access Token (partial): {partial}")
        print("  Use --show-secret to display full token (careful!)")

    return 0


# ============================================================================
# CLI Setup
# ============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser"""

    parser = argparse.ArgumentParser(
        prog='infrafabric',
        description='InfraFabric CLI - Secure Infrastructure Management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Authenticate with OAuth2
  %(prog)s auth login

  # Check authentication status
  %(prog)s auth status

  # Refresh authentication token
  %(prog)s auth refresh

  # Logout
  %(prog)s auth logout
        """
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    # Create subparsers for main commands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Main command'
    )

    # Auth subcommand group
    auth_parser = subparsers.add_parser(
        'auth',
        help='Authentication management'
    )

    auth_subparsers = auth_parser.add_subparsers(
        dest='subcommand',
        help='Auth subcommand',
        required=True
    )

    # Login subcommand
    login_cmd = auth_subparsers.add_parser(
        'login',
        help='Authenticate with OAuth2'
    )
    login_cmd.set_defaults(handler=handle_login)

    # Logout subcommand
    logout_cmd = auth_subparsers.add_parser(
        'logout',
        help='Sign out and remove token'
    )
    logout_cmd.set_defaults(handler=handle_logout)

    # Status subcommand
    status_cmd = auth_subparsers.add_parser(
        'status',
        help='Show authentication status'
    )
    status_cmd.set_defaults(handler=handle_status)

    # Refresh subcommand
    refresh_cmd = auth_subparsers.add_parser(
        'refresh',
        help='Refresh authentication token'
    )
    refresh_cmd.set_defaults(handler=handle_refresh)

    # Token subcommand
    token_cmd = auth_subparsers.add_parser(
        'token',
        help='Display current access token'
    )
    token_cmd.add_argument(
        '--show-secret',
        action='store_true',
        help='Display full token (use with caution)'
    )
    token_cmd.set_defaults(handler=handle_token)

    return parser


# ============================================================================
# Main Entry Point
# ============================================================================

def main() -> int:
    """Main CLI entry point"""

    parser = create_parser()
    args = parser.parse_args()

    # Enable verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle commands
    if hasattr(args, 'handler'):
        return args.handler(args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
