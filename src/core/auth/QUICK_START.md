# OAuth Relay Server - Quick Start Guide

# if://code/oauth-relay-quickstart/2025-11-30

## 5-Minute Setup

### Prerequisites
- Python 3.11+
- Redis server
- Docker & Docker Compose (optional)

### Option 1: Local Development (5 minutes)

```bash
# 1. Install dependencies
cd /home/setup/infrafabric/src/core/auth
pip install -r requirements-relay.txt

# 2. Start Redis (in another terminal)
redis-server

# 3. Configure OAuth provider
cp .env.example .env
# Edit .env with your OAuth client ID, secret, and endpoints

# 4. Start relay server
export $(cat .env | xargs)
python -m oauth_relay_server
```

Server runs at: https://localhost:8443

### Option 2: Docker Compose (5 minutes)

```bash
# 1. Configure environment
cd /home/setup/infrafabric/src/core/auth
cp .env.example .env
# Edit .env with your OAuth configuration

# 2. Start all services
docker-compose up -d

# 3. Check health
curl -k https://localhost:8443/health
```

Services running:
- Relay Server: https://localhost:8443
- Redis: localhost:6379
- Caddy Reverse Proxy: https://relay.local

## Testing the Flow (10 minutes)

### 1. Request Device Code

```bash
curl -X POST https://localhost:8443/device/code \
  -H "Content-Type: application/json" \
  -d '{"client_id": "infrafabric-cli", "scope": "openid profile email"}' \
  -k
```

Response:
```json
{
  "device_code": "base64_encoded_32_bytes",
  "user_code": "AB12-CD34",
  "verification_uri": "https://localhost:8443/activate?code=AB12-CD34",
  "interval": 5,
  "expires_in": 600
}
```

### 2. Visit Activation URL

Open browser to: `https://localhost:8443/activate?code=AB12-CD34`

Enter the user code: `AB12-CD34`

(In testing without real OAuth, you'll see an error - that's OK)

### 3. Poll for Token

```bash
curl -X GET "https://localhost:8443/device/token?device_code=BASE64_CODE" -k
```

Response when pending:
```json
{
  "status": "pending"
}
```

Response when token available:
```json
{
  "access_token": "token_value",
  "refresh_token": "refresh_token_value",
  "token_type": "Bearer",
  "expires_in": 3600,
  "status": "success"
}
```

## CLI Integration

### Python Client Example

```python
from infrafabric.auth import OAuthRelayClient

# Initialize
client = OAuthRelayClient(relay_url="https://relay.infrafabric.io")

# Request authorization
reg = client.request_device_code(
    client_id="infrafabric-cli",
    scope="openid profile email"
)

# Display to user
print(f"Visit: {reg['verification_uri']}")
print(f"Code: {reg['user_code']}")

# Poll for token
token = client.poll_for_token(reg['device_code'])

if token:
    print(f"Access Token: {token['access_token']}")
```

### Command-Line Usage

```bash
# Run as CLI client
python oauth_relay_server.py client infrafabric-cli "openid profile email"

# Output:
# Requesting authorization...
# Visit: https://relay.infrafabric.io/activate?code=AB12-CD34
# Enter code: AB12-CD34
#
# Waiting for authorization...
# Authorization complete!
# Access Token: eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Headless StackCP Integration

### SSH to StackCP Server

```bash
ssh user@stackcp.hosting.stackcp.net

# Run CLI with OAuth relay
infrafabric auth login \
  --relay-url https://relay.infrafabric.io \
  --client-id infrafabric-cli
```

Output on server:
```
Authorize at: https://relay.infrafabric.io/activate?code=AB12-CD34
Enter code when prompted on your local machine
Waiting for authorization... (press Ctrl+C to cancel)
```

On your local workstation:
1. Open browser to: https://relay.infrafabric.io/activate?code=AB12-CD34
2. Click "Authorize"
3. Server automatically completes authentication

## Configuration Quick Reference

### Environment Variables

```bash
# OAuth Configuration
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_AUTH_URL=https://oauth.provider.com/authorize
OAUTH_TOKEN_URL=https://oauth.provider.com/token

# Relay Server
RELAY_BASE_URL=https://relay.infrafabric.io
SERVER_HOST=0.0.0.0
SERVER_PORT=8443

# TLS/SSL
SSL_CERT_PATH=/etc/relay/certs/cert.pem
SSL_KEY_PATH=/etc/relay/certs/key.pem

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### OAuth Provider Examples

#### Google OAuth
```bash
OAUTH_CLIENT_ID=xxxxx-yyyyy.apps.googleusercontent.com
OAUTH_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxx
OAUTH_AUTH_URL=https://accounts.google.com/o/oauth2/v2/auth
OAUTH_TOKEN_URL=https://oauth2.googleapis.com/token
```

#### GitHub OAuth
```bash
OAUTH_CLIENT_ID=Iv1.xxxxxxxxxx
OAUTH_CLIENT_SECRET=xxxxxxxxxxxxxxxx
OAUTH_AUTH_URL=https://github.com/login/oauth/authorize
OAUTH_TOKEN_URL=https://github.com/login/oauth/access_token
```

#### Azure AD
```bash
OAUTH_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
OAUTH_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxx
OAUTH_AUTH_URL=https://login.microsoftonline.com/common/oauth2/v2.0/authorize
OAUTH_TOKEN_URL=https://login.microsoftonline.com/common/oauth2/v2.0/token
```

## Health Checks

### Server Health
```bash
curl -k https://localhost:8443/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-30T12:00:00"
}
```

### Metrics
```bash
curl -k https://localhost:8443/metrics
```

Response:
```json
{
  "pending_authorizations": 3,
  "timestamp": "2025-11-30T12:00:00"
}
```

### Docker Logs
```bash
# View relay server logs
docker-compose logs -f relay

# View all services
docker-compose logs -f

# View specific service
docker-compose logs -f redis
```

## Common Issues

### Issue: "Connection refused"
```bash
# Make sure Redis is running
redis-cli ping
# Should respond with "PONG"

# Check relay server is running
curl -k https://localhost:8443/health
```

### Issue: "SSL certificate verify failed"
```bash
# For local testing, use -k flag with curl
curl -k https://localhost:8443/health

# For production, ensure proper certificates are installed
```

### Issue: "Rate limit exceeded"
```bash
# Wait 1 minute for rate limit window to reset
# Default: 10 requests per minute per IP

# To increase limit, edit RateLimiter in oauth_relay_server.py
```

### Issue: "Device code expired"
```bash
# Device codes expire after 10 minutes
# Request a new device code
POST /device/code
```

## Security Checklist

- [ ] HTTPS/TLS enabled (not HTTP)
- [ ] OAUTH_CLIENT_SECRET not committed to git
- [ ] .env file in .gitignore
- [ ] Redis protected with password
- [ ] Rate limiting enabled
- [ ] CORS origins restricted
- [ ] Security headers configured
- [ ] Logs don't contain tokens
- [ ] Non-root Docker user

## Next Steps

1. Configure OAuth provider credentials
2. Deploy relay server (local or Docker)
3. Test health endpoints
4. Integrate with CLI
5. Deploy to StackCP
6. Monitor with /metrics endpoint

## More Information

See `/home/setup/infrafabric/src/core/auth/OAUTH_RELAY_GUIDE.md` for:
- Complete API reference
- Deployment guide
- Troubleshooting
- Testing procedures
- Security considerations

## Support Resources

- OAuth 2.0: https://tools.ietf.org/html/rfc6749
- Device Flow: https://tools.ietf.org/html/rfc8628
- PKCE: https://tools.ietf.org/html/rfc7636
- FastAPI: https://fastapi.tiangolo.com/
- Redis: https://redis.io/documentation

## Citation

```
if://code/oauth-relay-quickstart/2025-11-30
```
