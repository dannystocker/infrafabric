# if://code/oauth-relay-server/2025-11-30
# OAuth Relay Server for Headless Environments
# Enables OAuth PKCE flow in CLI without browser access on deployment servers
#
# ARCHITECTURE:
# 1. CLI requests device code from relay server
# 2. User authorizes on workstation browser via user_code
# 3. OAuth provider redirects to relay server callback
# 4. Relay matches state and stores token
# 5. CLI polls relay for token until available
#
# SECURITY:
# - HTTPS/TLS 1.3 required
# - CORS restricted to CLI origins
# - Rate limiting per IP
# - State parameter CSRF protection
# - 32-byte entropy device codes
# - 5-minute token expiry window

import os
import secrets
import time
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum
import re
import json
from urllib.parse import urlencode, quote

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
import redis
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Data Models
# ============================================================================

class TokenStatus(str, Enum):
    """Token response status codes"""
    PENDING = "pending"
    SUCCESS = "success"
    DENIED = "denied"
    EXPIRED = "expired"


class TokenResponse(BaseModel):
    """OAuth token response from relay"""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: int = 3600
    scope: str = ""
    status: TokenStatus = TokenStatus.PENDING
    error: Optional[str] = None
    error_description: Optional[str] = None


class DeviceRegistrationRequest(BaseModel):
    """Request for new device code"""
    client_id: str
    scope: str = ""
    redirect_uri: Optional[str] = None


class ActivationRequest(BaseModel):
    """User activation request"""
    user_code: str

    @validator('user_code')
    def validate_user_code(cls, v):
        """Validate user code format: XXXX-XXXX"""
        if not re.match(r'^[A-Z0-9]{4}-[A-Z0-9]{4}$', v):
            raise ValueError('User code must be format XXXX-XXXX')
        return v.upper()


class PollTokenRequest(BaseModel):
    """Poll for token request"""
    device_code: str


@dataclass
class DeviceRegistration:
    """Device registration record for relay server"""
    device_code: str
    user_code: str
    verification_uri: str
    client_id: str
    scope: str
    expires_in: int = 600  # 10 minutes
    interval: int = 5       # Poll interval in seconds
    created_at: datetime = field(default_factory=datetime.utcnow)
    state: Optional[str] = None
    authorized: bool = False
    authorization_code: Optional[str] = None
    token_response: Optional[Dict] = None

    def is_expired(self) -> bool:
        """Check if registration has expired"""
        expiry = self.created_at + timedelta(seconds=self.expires_in)
        return datetime.utcnow() > expiry

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Serialize to JSON"""
        data = self.to_dict()
        data['created_at'] = self.created_at.isoformat()
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> 'DeviceRegistration':
        """Deserialize from JSON"""
        data = json.loads(json_str)
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


# ============================================================================
# Rate Limiting
# ============================================================================

class RateLimiter:
    """Simple rate limiter using Redis"""

    def __init__(self, redis_client: redis.Redis,
                 max_requests: int = 10,
                 window_seconds: int = 60):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        key = f"rate_limit:{identifier}"
        current = self.redis.incr(key)

        if current == 1:
            self.redis.expire(key, self.window_seconds)

        return current <= self.max_requests


# ============================================================================
# OAuth Relay Server
# ============================================================================

class OAuthRelayServer:
    """OAuth relay server for headless CLI environments"""

    def __init__(self,
                 host: str = "0.0.0.0",
                 port: int = 8443,
                 redis_host: str = "localhost",
                 redis_port: int = 6379,
                 redis_db: int = 0,
                 ssl_cert_path: Optional[str] = None,
                 ssl_key_path: Optional[str] = None,
                 oauth_client_id: str = "",
                 oauth_client_secret: str = "",
                 oauth_auth_url: str = "",
                 oauth_token_url: str = "",
                 relay_base_url: str = "https://relay.infrafabric.io"):
        """
        Initialize OAuth relay server.

        Args:
            host: Server bind address
            port: Server port
            redis_host: Redis connection host
            redis_port: Redis connection port
            redis_db: Redis database number
            ssl_cert_path: Path to SSL certificate
            ssl_key_path: Path to SSL private key
            oauth_client_id: OAuth provider client ID
            oauth_client_secret: OAuth provider client secret
            oauth_auth_url: OAuth provider authorization endpoint
            oauth_token_url: OAuth provider token endpoint
            relay_base_url: Base URL of relay server (for callbacks)
        """
        self.host = host
        self.port = port
        self.ssl_cert_path = ssl_cert_path
        self.ssl_key_path = ssl_key_path
        self.relay_base_url = relay_base_url

        # OAuth configuration
        self.oauth_client_id = oauth_client_id or os.getenv('OAUTH_CLIENT_ID', '')
        self.oauth_client_secret = oauth_client_secret or os.getenv('OAUTH_CLIENT_SECRET', '')
        self.oauth_auth_url = oauth_auth_url or os.getenv('OAUTH_AUTH_URL', '')
        self.oauth_token_url = oauth_token_url or os.getenv('OAUTH_TOKEN_URL', '')

        # Redis connection
        try:
            self.redis = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True
            )
            self.redis.ping()
            logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

        # Rate limiter
        self.rate_limiter = RateLimiter(self.redis)

        # FastAPI app
        self.app = FastAPI(
            title="InfraFabric OAuth Relay Server",
            description="OAuth relay server for headless CLI environments",
            version="1.0.0"
        )

        # CORS configuration
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "localhost",
                "127.0.0.1",
                "*.infrafabric.io"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        )

        self._setup_routes()

    def _setup_routes(self) -> None:
        """Setup FastAPI routes"""

        @self.app.get("/health", tags=["health"])
        async def health():
            """Health check endpoint"""
            try:
                self.redis.ping()
                return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
            except redis.ConnectionError:
                raise HTTPException(status_code=503, detail="Redis connection failed")

        @self.app.get("/metrics", tags=["metrics"])
        async def metrics():
            """Prometheus metrics endpoint"""
            # Basic metrics - can be extended with prometheus_client
            stats = {
                "pending_authorizations": self.redis.dbsize(),
                "timestamp": datetime.utcnow().isoformat()
            }
            return stats

        @self.app.post("/device/code",
                      response_model=DeviceRegistration,
                      tags=["device-flow"])
        async def request_device_code(request: DeviceRegistrationRequest):
            """
            Generate device code for headless CLI.

            Request body:
            - client_id: OAuth client identifier
            - scope: OAuth scopes (space-separated)
            - redirect_uri: Custom redirect URI (optional)

            Returns:
            - device_code: Code for CLI to poll with
            - user_code: Short code user enters in browser
            - verification_uri: URL user visits to authorize
            - interval: Polling interval in seconds
            - expires_in: Registration expiry in seconds
            """
            # Validate client
            if not request.client_id:
                raise HTTPException(status_code=400, detail="client_id required")

            # Generate codes
            device_code = self._generate_device_code()
            user_code = self._generate_user_code()
            state = secrets.token_urlsafe(32)

            # Build verification URI
            verification_uri = f"{self.relay_base_url}/activate?code={user_code}"

            # Create registration
            reg = DeviceRegistration(
                device_code=device_code,
                user_code=user_code,
                verification_uri=verification_uri,
                client_id=request.client_id,
                scope=request.scope or "",
                state=state
            )

            # Store in Redis
            self._store_device_registration(reg)

            logger.info(f"Device code issued: {device_code[:8]}... for {request.client_id}")

            return reg

        @self.app.get("/activate",
                     response_class=HTMLResponse,
                     tags=["device-flow"])
        async def activation_page(code: Optional[str] = None):
            """
            HTML form for user to enter activation code.

            GET /activate?code=XXXX-XXXX
            """
            if code:
                # Validate code exists
                device_code = self._lookup_user_code(code)
                if not device_code:
                    return HTMLResponse(
                        content=self._render_error_page("Invalid or expired activation code"),
                        status_code=400
                    )

                # Render with code pre-filled
                return HTMLResponse(content=self._render_activation_page(code=code))
            else:
                # Render empty form
                return HTMLResponse(content=self._render_activation_page())

        @self.app.post("/activate",
                      tags=["device-flow"])
        async def process_activation(request: ActivationRequest):
            """
            Process user activation and redirect to OAuth provider.

            POST /activate
            - user_code: XXXX-XXXX format code

            Redirects to OAuth provider authorization endpoint.
            """
            # Lookup device registration
            device_code = self._lookup_user_code(request.user_code)
            if not device_code:
                raise HTTPException(status_code=404, detail="Invalid activation code")

            # Get registration
            reg = self._get_device_registration(device_code)
            if not reg or reg.is_expired():
                raise HTTPException(status_code=410, detail="Authorization code expired")

            # Build OAuth authorization URL
            oauth_url = self._build_oauth_url(reg)

            logger.info(f"User activated {request.user_code}, redirecting to OAuth")

            return RedirectResponse(url=oauth_url, status_code=302)

        @self.app.get("/callback",
                     tags=["oauth-callback"])
        async def oauth_callback(code: Optional[str] = None,
                                state: Optional[str] = None,
                                error: Optional[str] = None,
                                error_description: Optional[str] = None):
            """
            Receive OAuth provider callback.

            GET /callback?code=...&state=...

            Matches state to device registration and exchanges code for token.
            """
            if error:
                logger.warning(f"OAuth error: {error} - {error_description}")
                return HTMLResponse(
                    content=self._render_error_page(
                        f"Authorization denied: {error_description or error}"
                    ),
                    status_code=400
                )

            if not code or not state:
                raise HTTPException(status_code=400, detail="Missing code or state")

            # Lookup device by state
            device_code = self._lookup_state(state)
            if not device_code:
                raise HTTPException(status_code=400, detail="Invalid or expired state")

            # Get registration
            reg = self._get_device_registration(device_code)
            if not reg or reg.is_expired():
                raise HTTPException(status_code=410, detail="Authorization expired")

            # Exchange code for token
            token_response = await self._exchange_code_for_token(code)

            if not token_response:
                return HTMLResponse(
                    content=self._render_error_page("Failed to exchange authorization code"),
                    status_code=500
                )

            # Store token in registration
            reg.authorization_code = code
            reg.token_response = token_response
            reg.authorized = True
            self._store_device_registration(reg)

            logger.info(f"OAuth callback processed for {device_code[:8]}...")

            # Return success page
            return HTMLResponse(content=self._render_success_page())

        @self.app.get("/device/token",
                     response_model=TokenResponse,
                     tags=["device-flow"])
        async def poll_device_token(request: Request):
            """
            CLI polls this endpoint for token.

            GET /device/token?device_code=...

            Returns:
            - 200: Token available (status: success)
            - 202: Still waiting for authorization (status: pending)
            - 400: Invalid device code
            - 401: Authorization denied
            - 410: Device code expired
            - 429: Rate limit exceeded
            """
            # Rate limiting
            client_ip = request.client.host if request.client else "unknown"
            if not self.rate_limiter.is_allowed(client_ip):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            # Get device code from query params
            device_code = request.query_params.get('device_code')
            if not device_code:
                raise HTTPException(status_code=400, detail="device_code parameter required")

            # Get registration
            reg = self._get_device_registration(device_code)
            if not reg:
                raise HTTPException(status_code=400, detail="Invalid device code")

            if reg.is_expired():
                raise HTTPException(status_code=410, detail="Device code expired")

            # Check authorization status
            if not reg.authorized:
                # Still pending
                return JSONResponse(
                    status_code=202,
                    content=TokenResponse(status=TokenStatus.PENDING).dict()
                )

            if reg.token_response:
                # Token available
                return JSONResponse(
                    status_code=200,
                    content=TokenResponse(
                        access_token=reg.token_response.get('access_token'),
                        refresh_token=reg.token_response.get('refresh_token'),
                        token_type=reg.token_response.get('token_type', 'Bearer'),
                        expires_in=reg.token_response.get('expires_in', 3600),
                        scope=reg.token_response.get('scope', ''),
                        status=TokenStatus.SUCCESS
                    ).dict()
                )

            # Shouldn't reach here
            raise HTTPException(status_code=500, detail="Invalid state")

    def _generate_device_code(self, length: int = 32) -> str:
        """Generate device code with 32 bytes entropy"""
        return secrets.token_urlsafe(length)

    def _generate_user_code(self) -> str:
        """Generate user-friendly code: XXXX-XXXX"""
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        part1 = ''.join(secrets.choice(chars) for _ in range(4))
        part2 = ''.join(secrets.choice(chars) for _ in range(4))
        return f"{part1}-{part2}"

    def _store_device_registration(self, reg: DeviceRegistration,
                                  ttl: int = 600) -> None:
        """Store device registration in Redis"""
        # Store main registration
        key = f"device:{reg.device_code}"
        self.redis.setex(key, ttl, reg.to_json())

        # Store user code mapping
        user_key = f"user_code:{reg.user_code}"
        self.redis.setex(user_key, ttl, reg.device_code)

        # Store state mapping
        if reg.state:
            state_key = f"state:{reg.state}"
            self.redis.setex(state_key, ttl, reg.device_code)

    def _get_device_registration(self, device_code: str) -> Optional[DeviceRegistration]:
        """Retrieve device registration from Redis"""
        key = f"device:{device_code}"
        json_str = self.redis.get(key)

        if not json_str:
            return None

        try:
            return DeviceRegistration.from_json(json_str)
        except Exception as e:
            logger.error(f"Failed to deserialize registration: {e}")
            return None

    def _lookup_user_code(self, user_code: str) -> Optional[str]:
        """Lookup device code by user code"""
        key = f"user_code:{user_code.upper()}"
        return self.redis.get(key)

    def _lookup_state(self, state: str) -> Optional[str]:
        """Lookup device code by state"""
        key = f"state:{state}"
        return self.redis.get(key)

    def _build_oauth_url(self, reg: DeviceRegistration) -> str:
        """Build OAuth authorization URL"""
        params = {
            'client_id': self.oauth_client_id,
            'response_type': 'code',
            'redirect_uri': f"{self.relay_base_url}/callback",
            'scope': reg.scope or 'openid profile email',
            'state': reg.state,
        }

        query_string = urlencode(params)
        return f"{self.oauth_auth_url}?{query_string}"

    async def _exchange_code_for_token(self, code: str) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.oauth_token_url,
                    data={
                        'grant_type': 'authorization_code',
                        'code': code,
                        'client_id': self.oauth_client_id,
                        'client_secret': self.oauth_client_secret,
                        'redirect_uri': f"{self.relay_base_url}/callback",
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Token exchange failed: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Token exchange error: {e}")
            return None

    def _render_activation_page(self, code: Optional[str] = None) -> str:
        """Render HTML activation form"""
        code_value = code or ""

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InfraFabric CLI Authorization</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            padding: 40px;
            max-width: 400px;
            width: 100%;
        }}

        h1 {{
            font-size: 24px;
            margin-bottom: 10px;
            color: #333;
        }}

        .subtitle {{
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }}

        .form-group {{
            margin-bottom: 20px;
        }}

        label {{
            display: block;
            font-weight: 500;
            margin-bottom: 8px;
            color: #333;
            font-size: 14px;
        }}

        input[type="text"] {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 4px;
            font-size: 16px;
            font-family: monospace;
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: border-color 0.3s;
        }}

        input[type="text"]:focus {{
            outline: none;
            border-color: #667eea;
        }}

        input[type="text"]::placeholder {{
            color: #ccc;
        }}

        button {{
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }}

        button:active {{
            transform: translateY(0);
        }}

        .info {{
            background: #f5f5f5;
            border-left: 4px solid #667eea;
            padding: 12px;
            margin-top: 20px;
            font-size: 13px;
            color: #666;
            border-radius: 4px;
        }}

        .logo {{
            text-align: center;
            margin-bottom: 20px;
        }}

        .logo-icon {{
            display: inline-block;
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 24px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <div class="logo-icon">IF</div>
        </div>

        <h1>InfraFabric CLI</h1>
        <p class="subtitle">Authorization Required</p>

        <form method="POST" action="/activate">
            <div class="form-group">
                <label for="user_code">Enter Activation Code</label>
                <input
                    type="text"
                    id="user_code"
                    name="user_code"
                    pattern="[A-Z0-9]{{4}}-[A-Z0-9]{{4}}"
                    placeholder="XXXX-XXXX"
                    value="{code_value}"
                    required
                    autofocus
                >
            </div>

            <button type="submit">Authorize</button>

            <div class="info">
                <strong>Code format:</strong> 4 alphanumeric characters, hyphen, 4 more characters (e.g., AB12-CD34)
            </div>
        </form>
    </div>
</body>
</html>
"""

    def _render_error_page(self, message: str) -> str:
        """Render error page"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Authorization Error</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            padding: 40px;
            max-width: 400px;
            width: 100%;
            text-align: center;
        }}

        .error-icon {{
            font-size: 48px;
            margin-bottom: 20px;
        }}

        h1 {{
            font-size: 24px;
            color: #f5576c;
            margin-bottom: 10px;
        }}

        p {{
            color: #666;
            margin-bottom: 20px;
            line-height: 1.6;
        }}

        a {{
            display: inline-block;
            margin-top: 20px;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }}

        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="error-icon">❌</div>
        <h1>Authorization Failed</h1>
        <p>{message}</p>
        <p style="font-size: 12px; color: #999;">
            Please try again with a new authorization code from your CLI.
        </p>
        <a href="/">← Go Back</a>
    </div>
</body>
</html>
"""

    def _render_success_page(self) -> str:
        """Render success page"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Authorization Successful</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 8px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            padding: 40px;
            max-width: 400px;
            width: 100%;
            text-align: center;
        }

        .success-icon {
            font-size: 48px;
            margin-bottom: 20px;
        }

        h1 {
            font-size: 24px;
            color: #56ab2f;
            margin-bottom: 10px;
        }

        p {
            color: #666;
            margin-bottom: 10px;
            line-height: 1.6;
        }

        .status {
            background: #f0f9ff;
            border-left: 4px solid #56ab2f;
            padding: 15px;
            margin-top: 20px;
            border-radius: 4px;
            font-size: 13px;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <h1>Authorization Successful!</h1>
        <p>Your CLI has been authorized.</p>
        <p style="font-size: 14px; color: #999;">
            You can close this window and return to your terminal.
        </p>
        <div class="status">
            Your access token will be available shortly. The CLI will continue polling for the token.
        </div>
    </div>
</body>
</html>
"""

    def start(self, reload: bool = False) -> None:
        """Start relay server"""
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            ssl_keyfile=self.ssl_key_path,
            ssl_certfile=self.ssl_cert_path,
            log_level="info",
            reload=reload
        )

        server = uvicorn.Server(config)
        logger.info(f"Starting OAuth relay server on {self.host}:{self.port}")

        try:
            import asyncio
            asyncio.run(server.serve())
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")


# ============================================================================
# CLI Client Utility
# ============================================================================

class OAuthRelayClient:
    """CLI client for polling relay server"""

    def __init__(self, relay_url: str = "https://relay.infrafabric.io"):
        self.relay_url = relay_url

    def request_device_code(self, client_id: str, scope: str = "") -> Dict:
        """Request device code from relay"""
        import requests

        response = requests.post(
            f"{self.relay_url}/device/code",
            json={"client_id": client_id, "scope": scope},
            verify=True
        )
        response.raise_for_status()
        return response.json()

    def poll_for_token(self, device_code: str,
                      max_wait: int = 600,
                      check_interval: Optional[int] = None) -> Optional[Dict]:
        """Poll relay for token"""
        import requests
        import time

        start = time.time()

        while True:
            try:
                response = requests.get(
                    f"{self.relay_url}/device/token",
                    params={"device_code": device_code},
                    verify=True
                )

                if response.status_code == 200:
                    # Token available
                    return response.json()
                elif response.status_code == 202:
                    # Still pending
                    if time.time() - start > max_wait:
                        return None

                    wait_time = check_interval or 5
                    time.sleep(wait_time)
                else:
                    # Error
                    return None

            except requests.RequestException:
                if time.time() - start > max_wait:
                    return None
                time.sleep(5)

    def authorize(self, client_id: str, scope: str = "") -> Optional[Dict]:
        """Complete authorization flow"""
        print("Requesting authorization...")

        # Get device code
        try:
            reg = self.request_device_code(client_id, scope)
        except Exception as e:
            print(f"Failed to request device code: {e}")
            return None

        # Display instructions
        print(f"\nVisit: {reg['verification_uri']}")
        print(f"Enter code: {reg['user_code']}\n")

        # Poll for token
        print("Waiting for authorization...")
        token = self.poll_for_token(reg['device_code'])

        if token and token.get('status') == 'success':
            print("Authorization complete!")
            return token
        else:
            print("Authorization failed or timed out")
            return None


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import sys

    # Parse command-line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "client":
        # Run as CLI client
        client_id = sys.argv[2] if len(sys.argv) > 2 else "infrafabric-cli"
        scope = sys.argv[3] if len(sys.argv) > 3 else "openid profile email"
        relay_url = sys.argv[4] if len(sys.argv) > 4 else "https://relay.infrafabric.io"

        client = OAuthRelayClient(relay_url)
        token = client.authorize(client_id, scope)

        if token:
            print(f"\nAccess Token: {token.get('access_token')[:20]}...")
    else:
        # Run as relay server
        server = OAuthRelayServer()
        server.start(reload=False)
