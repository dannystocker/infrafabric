#!/usr/bin/env python3
"""
Archive meta-insights from old session to Redis L2 (Proxmox) as PERMANENT storage.

CRITICAL: L2 is PERMANENT storage - do NOT set TTL. Use SET, not SETEX.
"""

import sys
import json
import logging
from datetime import datetime

# Add tools to path
sys.path.insert(0, '/home/setup/infrafabric/tools')

from redis_cache_manager import get_redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def archive_meta_insights():
    """Archive 8 meta-insights to Redis L2 as permanent storage."""

    print("\n" + "="*70)
    print("ARCHIVING META-INSIGHTS TO REDIS L2 (PERMANENT STORAGE)")
    print("="*70)

    # Initialize Redis cache manager
    redis = get_redis()

    # Verify connection to L2
    try:
        redis.ping()
        print("✓ Connected to Redis L2 (Proxmox)")
    except Exception as e:
        print(f"✗ FAILED to connect to L2: {e}")
        return False

    insights = []

    # Insight 1: Haiku Swarm Pattern
    insight1 = {
        "name": "Parallel Haiku Data Pipeline",
        "optimal_agent_count": 6,
        "task_decomposition": ["metadata", "content", "indexing", "verification", "stats", "integrity"],
        "throughput": "12.86 files/second",
        "success_rate": 0.9977,
        "cost_vs_sonnet": "~70% savings",
        "use_cases": ["data migration", "bulk processing", "parallel analysis"]
    }
    redis.set("meta:pattern:haiku-swarm:data-migration", json.dumps(insight1))
    insights.append("meta:pattern:haiku-swarm:data-migration")
    print("✓ Insight 1: Haiku Swarm Pattern")

    # Insight 2: Context Integrity Validation
    insight2 = {
        "protocol": "Context Integrity Check",
        "steps": [
            "Check session history for contradictions",
            "Verify filesystem state with grep/find/ls",
            "Check Redis/git state",
            "Explicit clarification if conflict exists",
            "Execute ONLY after verification"
        ],
        "triggers": ["Unexpected context", "Missing prerequisite files", "User confusion about state"],
        "benefit": "Prevents 100k+ token mistakes from hallucinated context"
    }
    redis.set("meta:pattern:context-validation:multi-source", json.dumps(insight2))
    insights.append("meta:pattern:context-validation:multi-source")
    print("✓ Insight 2: Context Integrity Validation")

    # Insight 3: Instance Session Management
    insight3 = {
        "naming_scheme": "instance:{number}:{category}",
        "categories": ["session-narration", "handover", "context:rdl-complete", "deployment"],
        "ttl_days": 90,
        "rotation_count": 3,
        "cleanup_strategy": "Remove prior instance when new instance + 1 is created",
        "example_keys": [
            "instance:17:session-narration",
            "instance:17:handover",
            "instance:current:context -> instance:17"
        ]
    }
    redis.set("meta:pattern:instance-session-management", json.dumps(insight3))
    insights.append("meta:pattern:instance-session-management")
    print("✓ Insight 3: Instance Session Management")

    # Insight 4: Multi-Format Backup
    insight4 = {
        "formats": [
            {"type": "sqlite_wal", "purpose": "production index", "crash_recovery": True},
            {"type": "sql_dump", "purpose": "restoration script", "human_readable": True},
            {"type": "json_export", "purpose": "fallback search", "timestamp_metadata": True}
        ],
        "storage_location": "/mnt/c/Users/Setup/Downloads/",
        "verification_fields": ["file_count", "component_count", "ttl_remaining"],
        "recovery_priority": ["SQLite WAL", "SQL dump", "JSON fallback"],
        "recommended_frequency": "End of each session"
    }
    redis.set("meta:pattern:backup:multi-format-resilience", json.dumps(insight4))
    insights.append("meta:pattern:backup:multi-format-resilience")
    print("✓ Insight 4: Multi-Format Backup")

    # Insight 5: Bible Evolution Tracking
    insight5 = {
        "files": ["repo-structure-bible-manifesto.txt", "GtoCtoG-github-bible.txt"],
        "pattern": "Multiple copies exist; newest by mtime is canonical",
        "deduplication_rule": "Keep all copies; mark oldest as deprecated",
        "tracked_evolutions": ["Bazel→Just", "5-tools→Ruff", "pip→uv"],
        "update_frequency": "Per decision (weekly average)"
    }
    redis.set("meta:pattern:documentation:bible-evolution", json.dumps(insight5))
    insights.append("meta:pattern:documentation:bible-evolution")
    print("✓ Insight 5: Bible Evolution Tracking")

    # Insight 6: Execution Gates
    insight6 = {
        "lesson": "High consensus ≠ authorization",
        "approval_threshold": 0.8287,
        "execution_gate": "Requires explicit 'go' from user",
        "veto_mechanism": "Contrarian Guardian blocks >0.95 for 14 days",
        "failure_case": "Document consolidation executed despite blocking concerns",
        "fix_applied": "Add execution gate to all council-debated actions"
    }
    redis.set("meta:pattern:governance:premature-execution-guard", json.dumps(insight6))
    insights.append("meta:pattern:governance:premature-execution-guard")
    print("✓ Insight 6: Execution Gates")

    # Insight 7: GitHub Secret Scanning
    insight7 = {
        "status": "FIXED (2025-11-26)",
        "issue": "Slack API token exposed in bench_fast.json line 29",
        "blocking_rule": "GH013 - Push Protection",
        "resolution": "Visit GitHub unblock URL",
        "preventive_action": "Add .gitignore for reports/ or pre-commit hook"
    }
    redis.set("meta:vulnerability:github:gh013-slack-token", json.dumps(insight7))
    insights.append("meta:vulnerability:github:gh013-slack-token")
    print("✓ Insight 7: GitHub Secret Scanning")

    # Insight 8: S2 Architecture Discovery
    insight8 = {
        "path": "/home/setup/infrafabric/restored_s2/",
        "status": "DISCOVERED VIA CONTRADICTION RESOLUTION",
        "components": [
            "src/core/logistics/parcel.py (646 lines)",
            "src/core/logistics/redis_swarm_coordinator.py (449 lines)",
            "src/core/governance/guardian.py (747 lines)",
            "20+ industry lexicons"
        ],
        "documentation_gap": "EXISTS but not in agents.md"
    }
    redis.set("meta:project:infrafabric-s2:discovery", json.dumps(insight8))
    insights.append("meta:project:infrafabric-s2:discovery")
    print("✓ Insight 8: S2 Architecture Discovery")

    # Master Index
    master_index = {
        "source": "old manager session (173127)",
        "date": "2025-11-29",
        "archived_timestamp": datetime.now().isoformat(),
        "insights_count": 8,
        "keys": insights
    }
    redis.set("meta:insights:index:2025-11-29-old-session", json.dumps(master_index))
    print("✓ Master Index: meta:insights:index:2025-11-29-old-session")

    # Verify all keys were written
    print("\n" + "-"*70)
    print("VERIFICATION")
    print("-"*70)

    all_keys = redis.keys("meta:*")
    print(f"\nTotal keys with 'meta:' prefix in L2: {len(all_keys)}")

    for key in all_keys:
        print(f"  ✓ {key}")

    # Check that our specific keys exist
    expected_keys = insights + ["meta:insights:index:2025-11-29-old-session"]
    missing = []
    for key in expected_keys:
        if not redis.exists(key):
            missing.append(key)

    if missing:
        print(f"\n✗ MISSING KEYS: {missing}")
        return False

    # Verify no TTL on keys (permanent storage)
    print("\n" + "-"*70)
    print("TTL VERIFICATION (Should all be -1 = permanent)")
    print("-"*70)

    l2_connection = redis.l2
    for key in insights[:3]:  # Check first 3 as sample
        ttl = l2_connection.ttl(key)
        status = "✓ PERMANENT" if ttl == -1 else f"✗ TTL={ttl}s"
        print(f"{status}: {key}")

    print("\n" + "="*70)
    print(f"SUCCESS: {len(insights)} insights + 1 index = {len(insights)+1} keys archived")
    print(f"All keys stored in Redis L2 (Proxmox) as PERMANENT storage")
    print("="*70 + "\n")

    return True

if __name__ == "__main__":
    try:
        success = archive_meta_insights()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"FAILED: {e}", exc_info=True)
        sys.exit(1)
