"""
Claude Max Audit System

if://code/claude-max-audit/2025-11-30

Comprehensive audit trail system for all Claude Max communications, context access,
security events, and decision logging with IF.TTT compliance.

Public API:
  - ClaudeMaxAuditor: Main audit class
  - AuditEntry: Audit entry dataclass
  - AuditEntryType: Entry type enum
  - MessageType: Message type enum
  - SecuritySeverity: Security severity enum
  - OperationType: Context operation enum
  - CitationGenerator: IF.citation URI generator
  - get_auditor(): Get/create global auditor instance
"""

from .claude_max_audit import (
    ClaudeMaxAuditor,
    AuditEntry,
    AuditEntryType,
    AuditQueryResult,
    MessageType,
    SecuritySeverity,
    OperationType,
    CitationGenerator,
    PerformanceMetrics,
    get_auditor
)

__all__ = [
    "ClaudeMaxAuditor",
    "AuditEntry",
    "AuditEntryType",
    "AuditQueryResult",
    "MessageType",
    "SecuritySeverity",
    "OperationType",
    "CitationGenerator",
    "PerformanceMetrics",
    "get_auditor"
]

__version__ = "1.0.0"
__author__ = "InfraFabric Haiku Agent B14"
__citation__ = "if://code/claude-max-audit/2025-11-30"
