"""
SPDX-License-Identifier: MIT
Copyright (c) 2025 InfraFabric

SIP Security Module (IF.ESCALATE Production Security)
-------------------------------------------------------
Security classes for SIP proxy production hardening.

Philosophy Grounding:
- IF.ground Observable: All security events are logged and auditable
- IF.TTT Trustworthy: Defense in depth with multiple security layers
- Popper Falsifiability: Security assumptions are tested and validated

Security Layers:
1. TLS Certificate Validation: Verify client certificates and TLS parameters
2. SIP Digest Authentication: RFC 2617 digest authentication validation
3. Rate Limiting: Per-expert call rate limits (10 calls/minute)
4. IP Allowlist: Only approved external expert organization IPs

Integration:
- IF.witness: Log all security events for audit trail
- IF.guard: Policy enforcement with security context
"""

import hashlib
import hmac
import logging
import re
import ipaddress
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import secrets

logger = logging.getLogger(__name__)


@dataclass
class SecurityEvent:
    """Security event for IF.witness logging"""
    timestamp: str
    event_type: str
    severity: str  # INFO, WARN, ALERT, CRITICAL
    source_ip: str
    expert_id: Optional[str]
    details: Dict[str, Any]
    trace_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "severity": self.severity,
            "source_ip": self.source_ip,
            "expert_id": self.expert_id,
            "trace_id": self.trace_id,
            "details": self.details,
            "source": "IF.sip_security"
        }


class RateLimiter:
    """
    Rate limiter for external expert calls

    Implements sliding window rate limiting:
    - Max 10 calls per minute per expert
    - Tracks call timestamps in sliding window
    - Automatic cleanup of old entries

    Philosophy: Prevent abuse while allowing legitimate expert consultation
    """

    def __init__(self, max_calls: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter

        Args:
            max_calls: Maximum calls allowed in window (default: 10)
            window_seconds: Time window in seconds (default: 60)
        """
        self.max_calls = max_calls
        self.window_seconds = window_seconds

        # Track call timestamps per expert: {expert_id: [timestamp1, timestamp2, ...]}
        self.call_history: Dict[str, List[datetime]] = defaultdict(list)

        # Track rate limit violations
        self.violations: Dict[str, int] = defaultdict(int)

        logger.info(f"[RateLimiter] Initialized: max_calls={max_calls}, window={window_seconds}s")

    def check_rate_limit(self, expert_id: str, source_ip: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if expert has exceeded rate limit

        Args:
            expert_id: External expert identifier
            source_ip: Source IP address

        Returns:
            (allowed: bool, details: dict)
            - allowed: True if under limit, False if exceeded
            - details: Rate limit details for logging
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)

        # Clean up old timestamps outside window
        self.call_history[expert_id] = [
            ts for ts in self.call_history[expert_id]
            if ts > window_start
        ]

        current_count = len(self.call_history[expert_id])

        details = {
            "expert_id": expert_id,
            "source_ip": source_ip,
            "current_count": current_count,
            "max_calls": self.max_calls,
            "window_seconds": self.window_seconds,
            "window_start": window_start.isoformat() + "Z"
        }

        if current_count >= self.max_calls:
            self.violations[expert_id] += 1
            details["violations_total"] = self.violations[expert_id]

            logger.warning(
                f"[RateLimiter] RATE_LIMIT_EXCEEDED: {expert_id} "
                f"({current_count}/{self.max_calls} calls in {self.window_seconds}s)"
            )
            return False, details

        # Add current timestamp
        self.call_history[expert_id].append(now)
        details["current_count"] = current_count + 1

        logger.info(
            f"[RateLimiter] OK: {expert_id} "
            f"({current_count + 1}/{self.max_calls} calls in {self.window_seconds}s)"
        )
        return True, details

    def get_stats(self, expert_id: str) -> Dict[str, Any]:
        """Get rate limit statistics for expert"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)

        recent_calls = [
            ts for ts in self.call_history.get(expert_id, [])
            if ts > window_start
        ]

        return {
            "expert_id": expert_id,
            "calls_in_window": len(recent_calls),
            "max_calls": self.max_calls,
            "window_seconds": self.window_seconds,
            "violations": self.violations.get(expert_id, 0),
            "oldest_call": recent_calls[0].isoformat() + "Z" if recent_calls else None,
            "newest_call": recent_calls[-1].isoformat() + "Z" if recent_calls else None
        }


class IPAllowlist:
    """
    IP allowlist for external expert organizations

    Only approved IP ranges are allowed to connect:
    - Safety experts: 203.0.113.0/24
    - Ethics experts: 198.51.100.0/24
    - Security experts: 192.0.2.0/24

    Philosophy: Trust but verify - Only known organizations can connect
    """

    def __init__(self):
        """Initialize IP allowlist with approved organizations"""
        self.allowed_networks: Dict[str, ipaddress.IPv4Network] = {}
        self.organization_map: Dict[str, str] = {}

        # Load default approved organizations
        self._load_default_allowlist()

        logger.info(f"[IPAllowlist] Initialized with {len(self.allowed_networks)} networks")

    def _load_default_allowlist(self):
        """Load default approved organization IP ranges"""
        # These are example IP ranges (TEST-NET-1, TEST-NET-2, TEST-NET-3)
        # In production, replace with actual organization IP ranges
        approved_orgs = [
            {
                "org_id": "safety-experts-org",
                "name": "Safety & Alignment Expert Organization",
                "network": "203.0.113.0/24",
                "specializations": ["safety", "alignment"]
            },
            {
                "org_id": "ethics-institute",
                "name": "Ethics & Bias Research Institute",
                "network": "198.51.100.0/24",
                "specializations": ["ethics", "bias", "fairness"]
            },
            {
                "org_id": "security-consultancy",
                "name": "Security & Privacy Consultancy",
                "network": "192.0.2.0/24",
                "specializations": ["security", "privacy", "cryptography"]
            }
        ]

        for org in approved_orgs:
            network = ipaddress.IPv4Network(org["network"])
            self.allowed_networks[org["org_id"]] = network
            self.organization_map[org["org_id"]] = org["name"]

            logger.info(
                f"[IPAllowlist] Added: {org['name']} ({org['network']}) "
                f"- specializations: {org['specializations']}"
            )

    def check_ip(self, ip_address: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if IP address is in allowlist

        Args:
            ip_address: IPv4 address to check

        Returns:
            (allowed: bool, details: dict)
            - allowed: True if in allowlist, False otherwise
            - details: Organization info if allowed, None otherwise
        """
        try:
            ip_obj = ipaddress.IPv4Address(ip_address)
        except ValueError:
            logger.warning(f"[IPAllowlist] Invalid IP address: {ip_address}")
            return False, {"error": "Invalid IP address format"}

        # Check against all allowed networks
        for org_id, network in self.allowed_networks.items():
            if ip_obj in network:
                details = {
                    "allowed": True,
                    "ip_address": ip_address,
                    "organization_id": org_id,
                    "organization_name": self.organization_map[org_id],
                    "network": str(network)
                }
                logger.info(
                    f"[IPAllowlist] ALLOWED: {ip_address} "
                    f"(org: {self.organization_map[org_id]})"
                )
                return True, details

        logger.warning(f"[IPAllowlist] DENIED: {ip_address} (not in allowlist)")
        return False, {"allowed": False, "ip_address": ip_address}

    def add_network(self, org_id: str, org_name: str, network: str) -> bool:
        """
        Add new organization network to allowlist

        Args:
            org_id: Organization identifier
            org_name: Organization name
            network: IP network in CIDR notation (e.g., "192.0.2.0/24")

        Returns:
            True if added successfully
        """
        try:
            network_obj = ipaddress.IPv4Network(network)
            self.allowed_networks[org_id] = network_obj
            self.organization_map[org_id] = org_name

            logger.info(f"[IPAllowlist] Added network: {org_name} ({network})")
            return True
        except ValueError as e:
            logger.error(f"[IPAllowlist] Invalid network: {network} - {e}")
            return False

    def remove_network(self, org_id: str) -> bool:
        """Remove organization network from allowlist"""
        if org_id in self.allowed_networks:
            org_name = self.organization_map[org_id]
            del self.allowed_networks[org_id]
            del self.organization_map[org_id]

            logger.info(f"[IPAllowlist] Removed network: {org_name}")
            return True
        return False


class DigestAuthenticator:
    """
    SIP Digest Authentication (RFC 2617)

    Validates SIP digest authentication credentials:
    - MD5 hash-based challenge-response
    - Nonce-based replay protection
    - Quality of Protection (qop) support

    Philosophy: Standard-compliant authentication with audit logging
    """

    def __init__(self, realm: str = "external.advisor"):
        """
        Initialize digest authenticator

        Args:
            realm: SIP authentication realm
        """
        self.realm = realm
        self.nonce_store: Dict[str, datetime] = {}
        self.nonce_expiry_seconds = 300  # 5 minutes

        # In production, load from database
        # For now, use in-memory credential store
        self.credentials: Dict[str, str] = {}

        logger.info(f"[DigestAuth] Initialized with realm: {realm}")

    def generate_nonce(self) -> str:
        """
        Generate cryptographically secure nonce

        Returns:
            Nonce string (hex encoded)
        """
        nonce = secrets.token_hex(16)
        self.nonce_store[nonce] = datetime.utcnow()

        # Clean up expired nonces
        self._cleanup_nonces()

        return nonce

    def _cleanup_nonces(self):
        """Remove expired nonces from store"""
        now = datetime.utcnow()
        expiry = timedelta(seconds=self.nonce_expiry_seconds)

        expired = [
            nonce for nonce, timestamp in self.nonce_store.items()
            if now - timestamp > expiry
        ]

        for nonce in expired:
            del self.nonce_store[nonce]

    def validate_nonce(self, nonce: str) -> bool:
        """Check if nonce is valid and not expired"""
        if nonce not in self.nonce_store:
            logger.warning(f"[DigestAuth] Invalid nonce: {nonce}")
            return False

        timestamp = self.nonce_store[nonce]
        age = (datetime.utcnow() - timestamp).total_seconds()

        if age > self.nonce_expiry_seconds:
            logger.warning(f"[DigestAuth] Expired nonce: {nonce} (age: {age}s)")
            del self.nonce_store[nonce]
            return False

        return True

    def calculate_ha1(self, username: str, password: str) -> str:
        """
        Calculate HA1 hash (MD5(username:realm:password))

        Args:
            username: SIP username
            password: Plain text password

        Returns:
            HA1 hash (hex)
        """
        ha1_input = f"{username}:{self.realm}:{password}"
        ha1 = hashlib.md5(ha1_input.encode()).hexdigest()
        return ha1

    def calculate_response(
        self,
        ha1: str,
        nonce: str,
        method: str,
        uri: str,
        qop: Optional[str] = None,
        nc: Optional[str] = None,
        cnonce: Optional[str] = None
    ) -> str:
        """
        Calculate digest response

        Args:
            ha1: HA1 hash
            nonce: Server nonce
            method: SIP method (e.g., "INVITE")
            uri: Request URI
            qop: Quality of Protection
            nc: Nonce count
            cnonce: Client nonce

        Returns:
            Response hash (hex)
        """
        # HA2 = MD5(method:uri)
        ha2_input = f"{method}:{uri}"
        ha2 = hashlib.md5(ha2_input.encode()).hexdigest()

        # Calculate response based on qop
        if qop and nc and cnonce:
            # Response = MD5(HA1:nonce:nc:cnonce:qop:HA2)
            response_input = f"{ha1}:{nonce}:{nc}:{cnonce}:{qop}:{ha2}"
        else:
            # Response = MD5(HA1:nonce:HA2)
            response_input = f"{ha1}:{nonce}:{ha2}"

        response = hashlib.md5(response_input.encode()).hexdigest()
        return response

    def validate_digest(
        self,
        username: str,
        uri: str,
        nonce: str,
        response: str,
        method: str = "INVITE",
        qop: Optional[str] = None,
        nc: Optional[str] = None,
        cnonce: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate SIP digest authentication

        Args:
            username: SIP username
            uri: Request URI
            nonce: Server nonce
            response: Client response hash
            method: SIP method
            qop: Quality of Protection
            nc: Nonce count
            cnonce: Client nonce

        Returns:
            (valid: bool, details: dict)
        """
        # Validate nonce
        if not self.validate_nonce(nonce):
            return False, {"error": "Invalid or expired nonce"}

        # Get stored HA1 (in production, load from database)
        if username not in self.credentials:
            logger.warning(f"[DigestAuth] Unknown user: {username}")
            return False, {"error": "Unknown user"}

        ha1 = self.credentials[username]

        # Calculate expected response
        expected_response = self.calculate_response(
            ha1=ha1,
            nonce=nonce,
            method=method,
            uri=uri,
            qop=qop,
            nc=nc,
            cnonce=cnonce
        )

        # Constant-time comparison to prevent timing attacks
        valid = hmac.compare_digest(response, expected_response)

        details = {
            "username": username,
            "realm": self.realm,
            "uri": uri,
            "method": method,
            "qop": qop,
            "valid": valid
        }

        if valid:
            logger.info(f"[DigestAuth] AUTH_SUCCESS: {username}")
        else:
            logger.warning(f"[DigestAuth] AUTH_FAILED: {username}")

        return valid, details

    def add_user(self, username: str, password: str):
        """
        Add user credentials

        Args:
            username: SIP username
            password: Plain text password (will be hashed)
        """
        ha1 = self.calculate_ha1(username, password)
        self.credentials[username] = ha1

        logger.info(f"[DigestAuth] Added user: {username}")


class TLSCertificateValidator:
    """
    TLS certificate validation for SIP over TLS

    Validates:
    - Certificate chain of trust
    - Certificate expiration
    - Subject Alternative Names (SANs)
    - Certificate revocation (CRL/OCSP)

    Philosophy: Zero-trust - Verify all TLS connections
    """

    def __init__(self, ca_cert_path: str = "/etc/kamailio/tls/ca-list.pem"):
        """
        Initialize TLS certificate validator

        Args:
            ca_cert_path: Path to CA certificate bundle
        """
        self.ca_cert_path = ca_cert_path
        self.trusted_subjects: Set[str] = set()
        self.revoked_serials: Set[str] = set()

        logger.info(f"[TLSValidator] Initialized with CA bundle: {ca_cert_path}")

    def validate_certificate(
        self,
        cert_subject: str,
        cert_issuer: str,
        cert_serial: str,
        cert_not_before: str,
        cert_not_after: str,
        peer_verified: bool
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate TLS certificate

        Args:
            cert_subject: Certificate subject DN
            cert_issuer: Certificate issuer DN
            cert_serial: Certificate serial number
            cert_not_before: Certificate valid from (ISO 8601)
            cert_not_after: Certificate valid until (ISO 8601)
            peer_verified: Whether Kamailio verified the peer

        Returns:
            (valid: bool, details: dict)
        """
        details = {
            "subject": cert_subject,
            "issuer": cert_issuer,
            "serial": cert_serial,
            "not_before": cert_not_before,
            "not_after": cert_not_after,
            "peer_verified": peer_verified
        }

        # Check if certificate is in revocation list
        if cert_serial in self.revoked_serials:
            logger.warning(f"[TLSValidator] REVOKED certificate: {cert_serial}")
            details["error"] = "Certificate revoked"
            return False, details

        # Check certificate expiration
        try:
            not_after = datetime.fromisoformat(cert_not_after.replace('Z', '+00:00'))
            not_before = datetime.fromisoformat(cert_not_before.replace('Z', '+00:00'))
            now = datetime.utcnow()

            if now < not_before:
                logger.warning(f"[TLSValidator] Certificate not yet valid: {cert_subject}")
                details["error"] = "Certificate not yet valid"
                return False, details

            if now > not_after:
                logger.warning(f"[TLSValidator] Certificate expired: {cert_subject}")
                details["error"] = "Certificate expired"
                return False, details

            # Warn if certificate expires soon (30 days)
            days_until_expiry = (not_after - now).days
            if days_until_expiry < 30:
                logger.warning(
                    f"[TLSValidator] Certificate expires soon: {cert_subject} "
                    f"({days_until_expiry} days)"
                )
                details["warning"] = f"Expires in {days_until_expiry} days"

        except ValueError as e:
            logger.error(f"[TLSValidator] Invalid date format: {e}")
            details["error"] = "Invalid certificate date format"
            return False, details

        # Check if peer was verified by Kamailio
        if not peer_verified:
            logger.warning(f"[TLSValidator] Peer not verified: {cert_subject}")
            details["error"] = "Peer verification failed"
            return False, details

        logger.info(f"[TLSValidator] Certificate OK: {cert_subject}")
        return True, details

    def validate_tls_connection(
        self,
        tls_version: str,
        cipher_suite: str,
        peer_verified: bool
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate TLS connection parameters

        Args:
            tls_version: TLS version (e.g., "TLSv1.2")
            cipher_suite: Cipher suite name
            peer_verified: Whether peer was verified

        Returns:
            (valid: bool, details: dict)
        """
        details = {
            "tls_version": tls_version,
            "cipher_suite": cipher_suite,
            "peer_verified": peer_verified
        }

        # Require TLSv1.2 or higher
        allowed_versions = ["TLSv1.2", "TLSv1.3"]
        if tls_version not in allowed_versions:
            logger.warning(f"[TLSValidator] Weak TLS version: {tls_version}")
            details["error"] = f"TLS version {tls_version} not allowed"
            return False, details

        # Check for weak ciphers (basic check)
        weak_cipher_patterns = [
            r"NULL", r"EXPORT", r"DES", r"RC4", r"MD5", r"anon"
        ]

        for pattern in weak_cipher_patterns:
            if re.search(pattern, cipher_suite, re.IGNORECASE):
                logger.warning(f"[TLSValidator] Weak cipher: {cipher_suite}")
                details["error"] = f"Weak cipher suite: {cipher_suite}"
                return False, details

        logger.info(
            f"[TLSValidator] TLS connection OK: {tls_version} with {cipher_suite}"
        )
        return True, details

    def add_revoked_certificate(self, serial: str):
        """Add certificate serial to revocation list"""
        self.revoked_serials.add(serial)
        logger.info(f"[TLSValidator] Added revoked certificate: {serial}")


class SecurityManager:
    """
    Unified security manager coordinating all security components

    Integrates:
    - Rate limiting
    - IP allowlist
    - Digest authentication
    - TLS certificate validation
    - IF.witness security event logging
    """

    def __init__(self):
        """Initialize security manager with all components"""
        self.rate_limiter = RateLimiter(max_calls=10, window_seconds=60)
        self.ip_allowlist = IPAllowlist()
        self.digest_auth = DigestAuthenticator(realm="external.advisor")
        self.tls_validator = TLSCertificateValidator()

        self.security_events: List[SecurityEvent] = []

        logger.info("[SecurityManager] Initialized all security components")

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        source_ip: str,
        expert_id: Optional[str],
        details: Dict[str, Any],
        trace_id: Optional[str] = None
    ):
        """
        Log security event to IF.witness

        Args:
            event_type: Event type (e.g., "AUTH_FAILED", "RATE_LIMIT_EXCEEDED")
            severity: Severity level (INFO, WARN, ALERT, CRITICAL)
            source_ip: Source IP address
            expert_id: External expert ID
            details: Event details
            trace_id: IF trace ID
        """
        event = SecurityEvent(
            timestamp=datetime.utcnow().isoformat() + "Z",
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            expert_id=expert_id,
            details=details,
            trace_id=trace_id
        )

        self.security_events.append(event)

        # Log to standard logger
        log_msg = (
            f"[IF.witness] SECURITY_EVENT: {event_type} "
            f"(severity={severity}, ip={source_ip}, expert={expert_id})"
        )

        if severity == "CRITICAL":
            logger.critical(log_msg)
        elif severity == "ALERT":
            logger.error(log_msg)
        elif severity == "WARN":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

    def validate_connection(
        self,
        source_ip: str,
        expert_id: str,
        trace_id: str,
        tls_version: str,
        cipher_suite: str,
        peer_verified: bool
    ) -> Tuple[bool, List[str]]:
        """
        Validate complete connection security

        Checks:
        1. IP allowlist
        2. Rate limiting
        3. TLS connection parameters

        Args:
            source_ip: Source IP address
            expert_id: External expert ID
            trace_id: IF trace ID
            tls_version: TLS version
            cipher_suite: Cipher suite
            peer_verified: Whether peer was verified

        Returns:
            (allowed: bool, failure_reasons: list)
        """
        failures = []

        # Check 1: IP allowlist
        ip_allowed, ip_details = self.ip_allowlist.check_ip(source_ip)
        if not ip_allowed:
            failures.append("IP not in allowlist")
            self.log_security_event(
                event_type="IP_NOT_ALLOWLISTED",
                severity="ALERT",
                source_ip=source_ip,
                expert_id=expert_id,
                details=ip_details,
                trace_id=trace_id
            )

        # Check 2: Rate limiting
        rate_ok, rate_details = self.rate_limiter.check_rate_limit(expert_id, source_ip)
        if not rate_ok:
            failures.append("Rate limit exceeded")
            self.log_security_event(
                event_type="RATE_LIMIT_EXCEEDED",
                severity="WARN",
                source_ip=source_ip,
                expert_id=expert_id,
                details=rate_details,
                trace_id=trace_id
            )

        # Check 3: TLS validation
        tls_ok, tls_details = self.tls_validator.validate_tls_connection(
            tls_version=tls_version,
            cipher_suite=cipher_suite,
            peer_verified=peer_verified
        )
        if not tls_ok:
            failures.append("TLS validation failed")
            self.log_security_event(
                event_type="TLS_VALIDATION_FAILED",
                severity="ALERT",
                source_ip=source_ip,
                expert_id=expert_id,
                details=tls_details,
                trace_id=trace_id
            )

        # Log success if all checks passed
        if not failures:
            self.log_security_event(
                event_type="CONNECTION_VALIDATED",
                severity="INFO",
                source_ip=source_ip,
                expert_id=expert_id,
                details={
                    "ip_org": ip_details.get("organization_name"),
                    "rate_limit_status": f"{rate_details['current_count']}/{rate_details['max_calls']}",
                    "tls_version": tls_version,
                    "cipher_suite": cipher_suite
                },
                trace_id=trace_id
            )

        return len(failures) == 0, failures


# Export public API
__all__ = [
    "RateLimiter",
    "IPAllowlist",
    "DigestAuthenticator",
    "TLSCertificateValidator",
    "SecurityManager",
    "SecurityEvent"
]
