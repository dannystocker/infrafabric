# OAuth2 PKCE Implementation Guide

**Citation:** `if://code/oauth-pkce/2025-11-30`

## Overview

This document describes the OAuth2 PKCE (Proof Key for Code Exchange) implementation for CLI authentication. The implementation is RFC 7636 compliant and designed to securely authenticate CLI applications without requiring client secrets.

## Architecture

### Components

1. **OAuthPKCEClient** - Main client class managing the OAuth flow
2. **PKCEChallenge** - Container for PKCE parameters (verifier, challenge, state)
3. **CallbackServer** - Local HTTP server for receiving OAuth callback
4. **TokenResponse** - Data class for OAuth tokens with expiration tracking
5. **Utility Functions** - Token storage and retrieval helpers

### Security Features

- **PKCE Challenge** (RFC 7636 S256): Prevents authorization code interception attacks
- **State Parameter**: Protects against CSRF attacks
- **Localhost Callback**: No public endpoint exposure
- **Timeout Protection**: 5-minute callback timeout prevents indefinite blocking
- **Token Encryption**: Recommended encrypted storage at rest (Fernet)
- **Secure Defaults**: No insecure parameters or debugging in production

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. CLI Application Initiates Flow                               │
│    - Generates PKCE challenge (code_verifier + code_challenge)  │
│    - Generates state parameter for CSRF protection             │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. Start Local Callback Server                                  │
│    - HTTP server on localhost:8080                              │
│    - Waits for OAuth callback with authorization code          │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. Open Browser to Authorization Endpoint                       │
│    - User sees OAuth provider login/consent screen              │
│    - User authorizes application                                │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. OAuth Provider Redirects to Callback                         │
│    - Provides authorization code                                │
│    - Callback server extracts code                              │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. Exchange Code for Token                                      │
│    - Send code + code_verifier to token endpoint                │
│    - Server verifies: SHA256(code_verifier) == code_challenge  │
│    - Prevents interception (attacker would need code_verifier)  │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. Return Access Token                                          │
│    - Store token securely                                       │
│    - Use for authenticated API requests                         │
└─────────────────────────────────────────────────────────────────┘
```

## Usage Examples

### Basic OAuth Flow

```python
from src.core.auth import OAuthPKCEClient, save_token, load_token

# Initialize client
client = OAuthPKCEClient(
    client_id='infrafabric-cli',
    authorization_endpoint='https://accounts.example.com/oauth2/v2/authorize',
    token_endpoint='https://accounts.example.com/oauth2/v2/token'
)

# Initiate complete OAuth flow
try:
    token = client.initiate_flow(scopes=['profile', 'email', 'openid'])
    print(f"Authentication successful!")
    print(f"Token expires in {token.expires_in} seconds")

    # Save token for later use
    save_token(token, '/home/user/.infrafabric/token.json')

except AuthorizationDenied as e:
    print(f"User denied authorization: {e}")
except CallbackTimeout as e:
    print(f"Authorization timeout: {e}")
except TokenExchangeError as e:
    print(f"Token exchange failed: {e}")
```

### Using Saved Tokens

```python
from src.core.auth import load_token

# Load previously saved token
token = load_token('/home/user/.infrafabric/token.json')

if token and not token.is_expired():
    # Token is valid - use it
    headers = {
        'Authorization': f'Bearer {token.access_token}'
    }
    # Make authenticated requests...
else:
    # Token expired or missing - need new authentication
    # Trigger OAuth flow again...
    pass
```

### Token Refresh

```python
from src.core.auth import OAuthPKCEClient

client = OAuthPKCEClient(
    client_id='infrafabric-cli',
    authorization_endpoint='https://accounts.example.com/oauth2/v2/authorize',
    token_endpoint='https://accounts.example.com/oauth2/v2/token'
)

# Refresh expired token
if token.refresh_token:
    try:
        new_token = client.refresh_token(token.refresh_token)
        save_token(new_token, '/home/user/.infrafabric/token.json')
    except TokenExchangeError as e:
        print(f"Token refresh failed: {e}")
        # Fall back to full OAuth flow
        new_token = client.initiate_flow()
```

### Custom Redirect URI

```python
# Use custom port for callback
client = OAuthPKCEClient(
    client_id='infrafabric-cli',
    authorization_endpoint='https://accounts.example.com/oauth2/v2/authorize',
    token_endpoint='https://accounts.example.com/oauth2/v2/token',
    redirect_uri='http://localhost:9090/callback'  # Custom port
)
```

## PKCE Challenge Details (RFC 7636)

### Code Verifier Generation

```
code_verifier = base64url(random(32 bytes))
Length: 43-128 characters
Characters: [A-Z] [a-z] [0-9] - . _ ~
```

### Code Challenge Generation

```
code_challenge = base64url(sha256(code_verifier))
Challenge Method: S256 (SHA256)
```

### Verification (Server-side)

```
if sha256(code_verifier) == base64url_decode(code_challenge):
    # Authorization code is valid - issue token
else:
    # Authorization code is forged - reject
```

## Error Handling

### Exception Types

| Exception | Cause | Recovery |
|-----------|-------|----------|
| `AuthorizationDenied` | User rejected authorization | Inform user and offer retry |
| `CallbackTimeout` | No callback within 5 minutes | Timeout UI indicator, retry |
| `TokenExchangeError` | Token endpoint error | Log details, retry or re-auth |
| `InvalidState` | CSRF attack detected | Reject and force re-auth |

### Example Error Handling

```python
try:
    token = client.initiate_flow()
except AuthorizationDenied:
    # User denied access
    sys.exit("Authorization denied by user")
except CallbackTimeout:
    # User didn't complete auth in time
    sys.exit("Authorization timeout - please try again")
except TokenExchangeError as e:
    # Token server error
    logger.error(f"Token exchange error: {e}")
    sys.exit("Failed to obtain access token")
```

## Security Considerations

### What PKCE Protects Against

1. **Authorization Code Interception** - Even if intercepted, authorization code is useless without code_verifier
2. **Malicious App Attacks** - Malicious app cannot forge valid code_verifier
3. **Man-in-the-Middle** - Each request includes unique PKCE challenge

### What PKCE Does NOT Protect Against

1. **Compromised Token** - If access token is stolen, bearer token can be used
2. **Compromised Device** - Code verifier stored in memory can be extracted
3. **Phishing** - Fake OAuth screen can capture credentials

### Best Practices

1. **Always use HTTPS** - Prevent token interception in transit
2. **Secure Token Storage** - Use OS credential storage or encryption
3. **Short Expiration** - Minimize impact of token theft
4. **Refresh Tokens** - Enable token rotation without re-authentication
5. **Scope Limitation** - Request minimum necessary scopes
6. **Audit Logging** - Log all authentication events
7. **HTTPS Redirect** - Use HTTPS for OAuth callback in production

## Configuration

### Authorization Endpoint URLs

**Google OAuth2:**
```
authorization_endpoint = https://accounts.google.com/o/oauth2/v2/auth
token_endpoint = https://oauth2.googleapis.com/token
```

**GitHub OAuth2:**
```
authorization_endpoint = https://github.com/login/oauth/authorize
token_endpoint = https://github.com/login/oauth/access_token
```

**Microsoft:**
```
authorization_endpoint = https://login.microsoftonline.com/common/oauth2/v2.0/authorize
token_endpoint = https://login.microsoftonline.com/common/oauth2/v2.0/token
```

### Scopes

| Provider | Scope | Description |
|----------|-------|-------------|
| Google | `openid` | OpenID Connect identifier |
| Google | `profile` | User name, picture, etc. |
| Google | `email` | Email address |
| GitHub | `user:email` | User email access |
| GitHub | `read:user` | User profile data |
| Microsoft | `User.Read` | Read user profile |
| Microsoft | `Mail.Read` | Read user mailbox |

## Testing

### Unit Testing

```python
def test_pkce_challenge_generation():
    """Test PKCE challenge generation"""
    challenge = PKCEChallenge.generate()

    assert len(challenge.code_verifier) == 43
    assert len(challenge.code_challenge) == 43
    assert len(challenge.state) == 43

    # Verify SHA256 relationship
    verifier_hash = hashlib.sha256(challenge.code_verifier.encode()).digest()
    expected_challenge = base64.urlsafe_b64encode(verifier_hash).decode().rstrip('=')
    assert challenge.code_challenge == expected_challenge

def test_authorization_url():
    """Test authorization URL generation"""
    client = OAuthPKCEClient(
        client_id='test-client',
        authorization_endpoint='https://auth.example.com/authorize',
        token_endpoint='https://auth.example.com/token'
    )

    url = client.get_authorization_url(['profile', 'email'])

    assert 'client_id=test-client' in url
    assert 'response_type=code' in url
    assert 'code_challenge=' in url
    assert 'code_challenge_method=S256' in url
    assert 'state=' in url
    assert 'scope=profile+email' in url

def test_token_expiration():
    """Test token expiration detection"""
    token = TokenResponse(
        access_token='test_token',
        token_type='Bearer',
        expires_in=1,  # Expires in 1 second
        refresh_token='refresh_token'
    )

    assert not token.is_expired()

    # Simulate time passing
    import time
    time.sleep(2)
    assert token.is_expired()
```

### Integration Testing

```python
# Mock OAuth provider for testing
from unittest.mock import Mock, patch

def test_complete_flow():
    """Test complete OAuth flow"""

    client = OAuthPKCEClient(
        client_id='test-client',
        authorization_endpoint='https://mock.example.com/authorize',
        token_endpoint='https://mock.example.com/token'
    )

    # Mock the requests.post call
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {
            'access_token': 'test_access_token',
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': 'test_refresh_token'
        }

        # Note: Full flow test would need to mock webbrowser and callback
        # This is simplified for brevity
        pass
```

## Performance

### Typical Flow Timing

- PKCE Challenge Generation: ~1ms
- Browser Launch: ~100-500ms (OS dependent)
- User Authorization: 5-60s (user dependent)
- Token Exchange: ~200-500ms (network dependent)
- **Total**: 5-60+ seconds (user-driven)

### Callback Server

- Lightweight HTTP server using Python stdlib
- Single-threaded, handles single callback
- No external dependencies beyond `requests`
- Memory footprint: ~2-5MB

## Troubleshooting

### Browser Won't Open

```python
# Check if webbrowser.open() returns False
if not webbrowser.open(auth_url):
    print(f"Open this URL manually:\n{auth_url}")
```

### Callback Never Received

1. Check firewall allows localhost:8080
2. Verify redirect_uri matches OAuth provider settings
3. Check browser console for errors
4. Verify authorization endpoint URL is correct

### Token Exchange Fails

1. Verify token_endpoint URL is correct
2. Check client_id is valid
3. Ensure code_verifier matches challenge (automatic)
4. Check for OAuth provider service issues

### Token Always Expired

1. Verify system clock is accurate (NTP sync)
2. Check issued_at timestamp is being set
3. Verify expires_in value from provider

## References

- [RFC 7636 - Proof Key for Code Exchange (PKCE)](https://tools.ietf.org/html/rfc7636)
- [OAuth 2.0 Security Best Current Practice](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
- [Google OAuth 2.0 for Mobile & Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [GitHub OAuth Web Application Flow](https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps)

## Maintenance

### Code Review Checklist

- [ ] All PKCE parameters properly generated (43-128 chars)
- [ ] Code challenge uses S256 method
- [ ] State parameter used for CSRF protection
- [ ] Callback server only accepts localhost
- [ ] Timeout prevents indefinite blocking
- [ ] Token expiration properly tracked
- [ ] Errors properly logged and caught
- [ ] Documentation includes examples
- [ ] Tests cover happy path and error cases

### Version History

- v1.0.0 (2025-11-30): Initial PKCE implementation
  - RFC 7636 compliant
  - Callback server with timeout
  - Token refresh support
  - Comprehensive error handling

---

**IF.TTT Compliance:** This implementation is Traceable (if://code/oauth-pkce/2025-11-30), Transparent (RFC 7636 standard), and Trustworthy (security-focused design).
