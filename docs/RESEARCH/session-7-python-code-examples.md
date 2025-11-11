# Session 7: SIP Server API - Python Code Examples
## Agent 1-7 Code Deliverables | IF.search Swarm

---

## Agent 1: Asterisk AMI Example

```python
import socket
import asyncio

class AsteriskAdapter:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.creds = f"{username}:{password}"
        self.sock = None

    async def originate(self, destination: str, caller_id: str, timeout: int = 30):
        """Originate call via AMI"""
        try:
            cmd = f"Action: Originate\r\nChannel: SIP/{destination}\r\n"
            cmd += f"Callerid: {caller_id}\r\nContext: from-internal\r\n"
            cmd += f"Exten: {destination}\r\nPriority: 1\r\nTimeout: {timeout*1000}\r\n\r\n"
            await self._send_ami(cmd)
            return {"status": "queued", "destination": destination}
        except Exception as e:
            raise AsteriskError(f"Originate failed: {str(e)}")

    async def hangup(self, call_id: str):
        """Hangup call"""
        try:
            cmd = f"Action: Hangup\r\nChannel: {call_id}\r\n\r\n"
            await self._send_ami(cmd)
            return {"status": "hangup_sent"}
        except Exception as e:
            raise AsteriskError(f"Hangup failed: {str(e)}")

    async def _send_ami(self, cmd: str):
        """Send AMI command"""
        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            await asyncio.get_event_loop().run_in_executor(
                None, self.sock.connect, (self.host, self.port)
            )
        await asyncio.get_event_loop().run_in_executor(
            None, self.sock.send, cmd.encode()
        )
```

---

## Agent 5: Elastix REST Example

```python
import aiohttp
import json

class ElastixAdapter:
    def __init__(self, host: str, api_key: str):
        self.base_url = f"https://{host}/api"
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def originate(self, destination: str, caller_id: str, timeout: int = 30):
        """Originate call via REST"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "destination": destination,
                "caller_id": caller_id,
                "timeout": timeout
            }
            try:
                async with session.post(
                    f"{self.base_url}/calls",
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {"status": "created", "call_id": data.get("id")}
                    elif resp.status == 401:
                        raise ElastixAuthError("Invalid API key")
                    elif resp.status == 400:
                        raise ElastixError(f"Bad request: {await resp.text()}")
            except asyncio.TimeoutError:
                raise ElastixError(f"Request timeout after {timeout}s")

    async def transfer(self, call_id: str, target: str):
        """Transfer call"""
        async with aiohttp.ClientSession() as session:
            payload = {"target": target}
            async with session.post(
                f"{self.base_url}/calls/{call_id}/transfer",
                json=payload,
                headers=self.headers
            ) as resp:
                if resp.status == 200:
                    return {"status": "transfer_initiated"}
                raise ElastixError(f"Transfer failed: {resp.status}")
```

---

## Agent 7: Flexisip WebSocket + JWT Example

```python
import websockets
import jwt
import json
from datetime import datetime, timedelta

class FlexisipAdapter:
    def __init__(self, host: str, secret_key: str, api_key: str):
        self.ws_url = f"wss://{host}/ws"
        self.rest_url = f"https://{host}/api"
        self.secret = secret_key
        self.api_key = api_key

    def _generate_jwt(self):
        """Generate JWT token"""
        payload = {
            "iss": "sip-integrator",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "api_key": self.api_key
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    async def originate(self, destination: str, caller_id: str):
        """Originate via REST"""
        import aiohttp
        headers = {
            "Authorization": f"Bearer {self._generate_jwt()}",
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            payload = {
                "destination": destination,
                "caller_id": caller_id
            }
            try:
                async with session.post(
                    f"{self.rest_url}/calls/originate",
                    json=payload,
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    elif resp.status == 422:
                        raise FlexisipValidationError("Invalid call params")
            except Exception as e:
                raise FlexisipError(f"Originate error: {str(e)}")

    async def hangup_ws(self, call_uuid: str):
        """Hangup via WebSocket"""
        try:
            async with websockets.connect(
                f"{self.ws_url}?token={self._generate_jwt()}"
            ) as ws:
                await ws.send(json.dumps({
                    "action": "hangup",
                    "uuid": call_uuid
                }))
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                return json.loads(response)
        except asyncio.TimeoutError:
            raise FlexisipError("WebSocket timeout")
```

---

## Agent 8: Unified Adapter Base Class

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class CallState(Enum):
    CREATED = "created"
    RINGING = "ringing"
    CONNECTED = "connected"
    HELD = "held"
    TRANSFERRED = "transferred"
    ENDED = "ended"

@dataclass
class CallInfo:
    call_id: str
    state: CallState
    caller_id: str
    destination: str
    duration: int

class SIPAdapter(ABC):
    """Base adapter for all SIP servers"""

    @abstractmethod
    async def originate(self, destination: str, caller_id: str, **kwargs) -> dict:
        """Originate a call"""
        pass

    @abstractmethod
    async def hangup(self, call_id: str) -> dict:
        """Hangup a call"""
        pass

    @abstractmethod
    async def transfer(self, call_id: str, target: str) -> dict:
        """Transfer a call"""
        pass

    @abstractmethod
    async def conference(self, call_ids: list, room_name: str) -> str:
        """Create conference"""
        pass

    @abstractmethod
    async def get_call_status(self, call_id: str) -> CallInfo:
        """Get call status"""
        pass

class SIPError(Exception):
    """Base SIP error"""
    pass

class SIPAuthError(SIPError):
    """Authentication error"""
    pass

class SIPTimeoutError(SIPError):
    """Timeout error"""
    pass
```

---

## Error Handling Patterns (All Agents)

```python
async def with_retry(coro, max_retries=3, backoff=1.0):
    """Retry wrapper with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return await coro
        except SIPTimeoutError:
            if attempt == max_retries - 1:
                raise
            wait_time = backoff ** attempt
            await asyncio.sleep(wait_time)
        except (SIPAuthError, SIPValidationError) as e:
            raise  # Don't retry auth/validation errors

# Usage:
result = await with_retry(
    adapter.originate("sip:1234@example.com", "1000"),
    max_retries=3,
    backoff=2.0
)
```

---
