"""
InfraFabric Security Module - Ed25519 Agent Identity System

Provides cryptographic identity management for multi-agent swarm coordination.

Modules:
    ed25519_identity: Ed25519 keypair generation, storage, signing, and verification

Usage:
    from src.core.security.ed25519_identity import AgentIdentity

    # Generate and save keypair
    identity = AgentIdentity("haiku_worker_a1b2c3d4")
    priv_key, pub_key = identity.generate_keypair()
    identity.save_private_key(priv_key, "passphrase")

    # Sign and verify messages
    signature = identity.sign_message(b"message content")
    is_valid = AgentIdentity.verify_signature(pub_key, signature, b"message content")

Security Compliance:
    - IF.TTT: All operations logged with cryptographic signatures
    - THREAT 6 mitigation: Ed25519 digital signatures prevent identity spoofing
    - P0 priority: Required for production deployment
"""

from .ed25519_identity import AgentIdentity, KeyMetadata, create_agent_identity_for_registration

__all__ = [
    "AgentIdentity",
    "KeyMetadata",
    "create_agent_identity_for_registration",
]

__version__ = "1.0.0"
__author__ = "InfraFabric Security Team"
__status__ = "Production"
