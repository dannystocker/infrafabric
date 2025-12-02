# OAuth Relay Server Implementation Guide

# if://code/oauth-relay-guide/2025-11-30

## Overview

The OAuth Relay Server enables OAuth PKCE authentication flow in headless environments (like StackCP SSH deployments) where browser access is not available. It acts as a bridge between a CLI on a headless server and an OAuth provider on a workstation.

### Problem Solved

**Challenge:** OAuth PKCE flow requires browser callback on the same machine initiating authorization. On headless StackCP deployments, the CLI runs on a server without browser access.

**Solution:** Relay server receives the OAuth callback on a publicly accessible URL, stores the token, and the CLI polls for it.

## Architecture

```
┌─────────────────┐              ┌──────────────────┐
│  StackCP Server │              │   Workstation    │
│  (Headless)     │              │  (Has Browser)   │
│                 │              │                  │
│  ┌───────────┐  │              │  ┌────────────┐  │
│  │   CLI     │  │              │  │  Browser   │  │
│  └─────┬─────┘  │              │  └──────┬─────┘  │
│        │ 1      │              │         │ 2      │
│        │        │              │         │        │
│        ▼        │              │         ▼        │
│  ┌─────────────┐│              │  ┌──────────────┐│
│  │  Request    ││──────┐       │  │   OAuth      ││
│  │Device Code  ││      │       │  │   Provider   ││
│  └─────────────┘│      │       │  └──────────────┘│
│                 │      │       │                  │
│  ┌─────────────┐│      │       │  ┌──────────────┐│
│  │  Poll for   ││      │  ┌────────▶  Authorize  ││
│  │   Token     ││      │  │   3     ├────────────┤│
│  └─────┬───────┘│      │  │   ┌─────▶  Redirect  ││
│        ▲        │      │  │   │ 4     to Relay   ││
│        │        │      │  │   │                  │
└─────────────────┘      │  │   └──────────────────┘
         ▲               │  │           │
         │               │  │           ▼
         │ 5             │  │    ┌─────────────────┐
         └────────────────┐ └───▶│  Relay Server   │
                          │      │                 │
                          │      │  • Recv callback│
                          │      │  • Store token  │
                          │      │  • Serve UI     │
                          │      │                 │
                          └─────▶│ /device/code    │
                                 │ /activate       │
                                 │ /callback       │
                                 │ /device/token   │
                                 └─────────────────┘
```

## Flow Sequence

### 1. Device Code Request
```bash
# CLI on StackCP server requests device code
POST /device/code
{
    "client_id": "infrafabric-cli",
    "scope": "openid profile email"
}

# Relay responds with registration
{
    "device_code": "base64_encoded_32_bytes",
    "user_code": "AB12-CD34",
    "verification_uri": "https://relay.infrafabric.io/activate?code=AB12-CD34",
    "interval": 5,
    "expires_in": 600
}
```

### 2. User Activation on Workstation
- User opens browser and visits `verification_uri`
- Enters `user_code`: `AB12-CD34`
- Relay redirects to OAuth provider

### 3. OAuth Authorization
- User authorizes with OAuth provider
- Provider redirects to `relay/callback?code=xyz&state=abc`
- Relay exchanges code for token and stores it

### 4. CLI Polls for Token
```bash
# CLI polls every 5 seconds
GET /device/token?device_code=base64_encoded_32_bytes

# Pending response (HTTP 202)
{
    "status": "pending"
}

# Token available (HTTP 200)
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "refresh_token_value",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "openid profile email",
    "status": "success"
}
```

## Implementation Details

### Security Features

1. **Device Code Entropy**: 32 bytes (256 bits) of random data, base64 encoded
2. **User Code Format**: XXXX-XXXX (8 alphanumeric characters)
3. **State Parameter**: CSRF protection with random state in OAuth flow
4. **HTTPS/TLS 1.3**: All communication encrypted
5. **Token Expiry**: 5-minute window for token retrieval
6. **Rate Limiting**: 10 requests/minute per IP address
7. **CORS**: Restricted to CLI origins only
8. **Redis TTL**: Device registrations expire after 10 minutes

### Data Models

#### DeviceRegistration
```python
@dataclass
class DeviceRegistration:
    device_code: str           # Random code for polling
    user_code: str             # Human-friendly code (XXXX-XXXX)
    verification_uri: str      # URL user visits
    client_id: str             # OAuth client identifier
    scope: str                 # OAuth scopes
    state: str                 # CSRF protection state
    authorized: bool           # Authorization status
    token_response: Dict       # OAuth token response
    created_at: datetime       # Registration timestamp
    expires_in: int            # 10 minutes default
    interval: int              # Poll interval (5 seconds)
```

#### TokenResponse
```python
class TokenResponse(BaseModel):
    access_token: Optional[str]
    refresh_token: Optional[str]
    token_type: str = "Bearer"
    expires_in: int = 3600
    scope: str = ""
    status: TokenStatus  # pending, success, denied, expired
    error: Optional[str]
    error_description: Optional[str]
```

### Redis State Management

```
device:{device_code}           → DeviceRegistration JSON (TTL: 10 min)
device:{device_code}:token     → TokenResponse JSON (TTL: 5 min)
user_code:{user_code}          → device_code mapping (TTL: 10 min)
state:{state}                  → device_code mapping (TTL: 10 min)
rate_limit:{ip_address}        → Request counter (TTL: 1 min)
```

### API Endpoints

#### POST /device/code
Request device code for headless CLI

**Request:**
```json
{
    "client_id": "infrafabric-cli",
    "scope": "openid profile email",
    "redirect_uri": "https://custom-relay.example.com/callback"  // optional
}
```

**Response (200):**
```json
{
    "device_code": "...",
    "user_code": "AB12-CD34",
    "verification_uri": "https://relay.infrafabric.io/activate?code=AB12-CD34",
    "interval": 5,
    "expires_in": 600,
    "created_at": "2025-11-30T12:00:00"
}
```

#### GET /activate
Activation page for user to enter code

**Query Parameters:**
- `code`: Pre-fill user code (optional)

**Response (200):**
HTML form for activation

#### POST /activate
Process activation and redirect to OAuth

**Request:**
```json
{
    "user_code": "AB12-CD34"
}
```

**Response (302):**
Redirect to OAuth provider authorization endpoint

#### GET /callback
Receive OAuth provider callback

**Query Parameters:**
- `code`: Authorization code from provider
- `state`: State parameter (CSRF protection)
- `error`: Error code (if denied)
- `error_description`: Error description

**Response (200):**
Success HTML page, or error page

#### GET /device/token
Poll for access token

**Query Parameters:**
- `device_code`: Device code from initial request

**Response (200):**
```json
{
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "status": "success"
}
```

**Response (202):**
```json
{
    "status": "pending"
}
```

**Response (400):**
Invalid device code

**Response (410):**
Device code expired

#### GET /health
Health check

**Response (200):**
```json
{
    "status": "healthy",
    "timestamp": "2025-11-30T12:00:00"
}
```

#### GET /metrics
Prometheus metrics

**Response (200):**
```json
{
    "pending_authorizations": 5,
    "timestamp": "2025-11-30T12:00:00"
}
```

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements-relay.txt

# Start Redis (required)
redis-server

# Set environment variables
export OAUTH_CLIENT_ID="your-client-id"
export OAUTH_CLIENT_SECRET="your-client-secret"
export OAUTH_AUTH_URL="https://oauth.provider.com/authorize"
export OAUTH_TOKEN_URL="https://oauth.provider.com/token"
export RELAY_BASE_URL="https://relay.infrafabric.io"

# Start relay server
python -m oauth_relay_server
```

### Docker Deployment

```bash
# Build image
docker build -f Dockerfile -t infrafabric/oauth-relay:1.0.0 .

# Start with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f relay

# Stop
docker-compose down
```

### Environment Variables

```bash
# OAuth Configuration
OAUTH_CLIENT_ID              # OAuth provider client ID
OAUTH_CLIENT_SECRET          # OAuth provider client secret
OAUTH_AUTH_URL               # OAuth authorization endpoint
OAUTH_TOKEN_URL              # OAuth token endpoint

# Relay Configuration
RELAY_BASE_URL               # Base URL of relay (https://relay.infrafabric.io)
SERVER_HOST                  # Bind address (default: 0.0.0.0)
SERVER_PORT                  # Bind port (default: 8443)

# TLS
SSL_CERT_PATH                # Path to SSL certificate
SSL_KEY_PATH                 # Path to SSL private key

# Redis
REDIS_HOST                   # Redis hostname (default: localhost)
REDIS_PORT                   # Redis port (default: 6379)
REDIS_DB                     # Redis database (default: 0)

# Logging
LOG_LEVEL                    # Log level (default: info)
```

## CLI Usage

### Python Client Library

```python
from infrafabric.auth import OAuthRelayClient

# Initialize client
client = OAuthRelayClient(relay_url="https://relay.infrafabric.io")

# Request device code
reg = client.request_device_code(
    client_id="infrafabric-cli",
    scope="openid profile email"
)

# Display to user
print(f"Visit: {reg['verification_uri']}")
print(f"Code: {reg['user_code']}")

# Poll for token
token = client.poll_for_token(
    device_code=reg['device_code'],
    max_wait=600,          # 10 minute timeout
    check_interval=5       # Check every 5 seconds
)

if token:
    print(f"Access Token: {token['access_token']}")
    print(f"Expires In: {token['expires_in']} seconds")
```

### Command-Line Usage

```bash
# Run as CLI client
python oauth_relay_server.py client infrafabric-cli "openid profile email" "https://relay.infrafabric.io"

# Output:
# Requesting authorization...
# Visit: https://relay.infrafabric.io/activate?code=AB12-CD34
# Enter code: AB12-CD34
#
# Waiting for authorization...
# Authorization complete!
# Access Token: eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Headless SSH CLI Flow

```bash
# On StackCP headless server
ssh user@stackcp.hosting.stackcp.net

# Run CLI with OAuth relay
infrafabric auth login \
  --relay-url https://relay.infrafabric.io \
  --client-id infrafabric-cli \
  --scope "openid profile email"

# Output:
# Authorize at: https://relay.infrafabric.io/activate?code=AB12-CD34
# Enter code when prompted on your local machine
#
# Waiting for authorization... (ctrl+c to cancel)
```

## Error Handling

### Device Code Errors

| Status | Code | Meaning | Resolution |
|--------|------|---------|-----------|
| 400 | INVALID_REQUEST | Missing required parameter | Check client_id parameter |
| 400 | INVALID_CLIENT | Unknown client ID | Verify client_id is correct |
| 410 | EXPIRED_TOKEN | Device code expired | Request new device code |

### Token Poll Errors

| Status | Code | Meaning | Resolution |
|--------|------|---------|-----------|
| 202 | PENDING | Authorization not yet granted | Continue polling |
| 400 | INVALID_DEVICE | Device code invalid/not found | Use correct device code |
| 401 | DENIED | User denied authorization | Try again with new code |
| 410 | EXPIRED_TOKEN | Device code expired | Request new device code |
| 429 | RATE_LIMITED | Too many requests | Wait before retrying |

### OAuth Provider Errors

| Error | Meaning | Resolution |
|-------|---------|-----------|
| invalid_grant | Authorization code invalid or expired | Authorize again |
| invalid_scope | Requested scope not available | Check scope parameter |
| access_denied | User denied permission | User must authorize |
| server_error | Provider server error | Retry later |

## Security Considerations

### HTTPS/TLS Requirement

- All traffic MUST use HTTPS/TLS 1.3
- Invalid/self-signed certificates will be rejected
- Let's Encrypt certificates via Caddy are recommended

### State Parameter Protection

- Each authorization request includes random 32-byte state
- State tied to device registration
- Prevents CSRF attacks on activation page

### Token Expiry

- Device codes expire after 10 minutes of inactivity
- Tokens are retrieved within 5-minute window
- Prevents token reuse/replay attacks

### Rate Limiting

- 10 requests per minute per IP address
- Protects against brute-force attacks
- Rate limit counter reset after 1 minute

### Redis Security

- Redis instance should NOT be publicly accessible
- Use password authentication in production
- Consider Redis Sentinel or Cluster for HA

## Monitoring

### Health Check

```bash
curl -k https://relay.infrafabric.io/health
```

Response:
```json
{
    "status": "healthy",
    "timestamp": "2025-11-30T12:00:00"
}
```

### Metrics Endpoint

```bash
curl -k https://relay.infrafabric.io/metrics
```

Response:
```json
{
    "pending_authorizations": 3,
    "timestamp": "2025-11-30T12:00:00"
}
```

### Logs

Docker:
```bash
docker-compose logs -f relay
```

Direct:
```bash
tail -f /var/log/infrafabric/oauth-relay.log
```

## Testing

### Unit Tests

```bash
pytest tests/auth/test_oauth_relay_server.py -v
```

### Integration Tests

```bash
# Start relay and redis
docker-compose up -d

# Run integration tests
pytest tests/auth/test_oauth_relay_integration.py -v

# Stop services
docker-compose down
```

### Manual Testing

```bash
# 1. Request device code
curl -X POST http://localhost:8443/device/code \
  -H "Content-Type: application/json" \
  -d '{"client_id": "test-client"}'

# 2. Check relay server health
curl -k https://localhost:8443/health

# 3. Poll for token (will be pending)
curl -k https://localhost:8443/device/token?device_code=YOUR_DEVICE_CODE
```

## Troubleshooting

### Redis Connection Error

```
redis.ConnectionError: Error 111 connecting to localhost:6379
```

**Solution:**
- Ensure Redis is running: `redis-server`
- Check Redis is accessible: `redis-cli ping`
- Verify REDIS_HOST and REDIS_PORT environment variables

### SSL Certificate Error

```
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solution:**
- For development, ensure certificates are properly generated
- For production, use Let's Encrypt via Caddy
- Check SSL_CERT_PATH and SSL_KEY_PATH environment variables

### Rate Limit Exceeded

```
HTTPException 429: Rate limit exceeded
```

**Solution:**
- Wait 1 minute for rate limit window to expire
- Check for polling loops that may be too aggressive
- Increase rate limit in RateLimiter configuration if needed

### State Parameter Mismatch

```
HTTPException 400: Invalid or expired state
```

**Solution:**
- Ensure authorization completes within 10 minute window
- Don't refresh page during activation flow
- Check device code hasn't expired

## Compliance & Standards

- **OAuth 2.0 Device Authorization Grant** (RFC 8628)
- **PKCE** (Proof Key for Public Clients, RFC 7636)
- **OpenID Connect** (Core 1.0)
- **CORS** (Cross-Origin Resource Sharing)
- **HTTPS/TLS 1.3** (Security)

## References

- [RFC 8628 - Device Authorization Grant](https://tools.ietf.org/html/rfc8628)
- [RFC 7636 - PKCE](https://tools.ietf.org/html/rfc7636)
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Documentation](https://redis.io/documentation)

## Citation

```
if://code/oauth-relay-server/2025-11-30
```

## Support

For issues or questions about the OAuth Relay Server:
1. Check the troubleshooting section above
2. Review logs with `docker-compose logs relay`
3. Test health endpoint: `curl -k https://relay.infrafabric.io/health`
4. File issue in InfraFabric repository
