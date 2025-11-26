import glob
import json
import os
import re
from typing import Any, Dict, List, Optional

import redis


def _slugify(value: str) -> str:
    """Convert a term to a safe Redis key fragment."""
    return re.sub(r"[^a-z0-9\-]+", "-", value.strip().lower()).strip("-")


def load_lexicon_files(path: str = "src/config/lexicons/*.json") -> List[str]:
    """Locate all lexicon JSON files."""
    return glob.glob(path)


def seed_lexicons(redis_client: Optional[redis.Redis] = None) -> None:
    """
    Seed lexicon configs into Redis.

    Keys:
    - mcr:vertical:{id} -> metadata (hset)
    - mcr:lexicon:{id}:{term_slug} -> serialized lexicon entry (set)
    """
    r = redis_client or redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    files = load_lexicon_files()
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        industry_id = data.get("industry_id")
        if not industry_id:
            continue

        # Store industry metadata
        r.hset(
            f"mcr:vertical:{industry_id}",
            mapping={
                "industry_name": data.get("industry_name", ""),
                "cluster": data.get("cluster", ""),
                "schema_version": data.get("schema_version", ""),
                "protocols": ",".join(p.get("name", "") for p in data.get("protocols", [])),
            },
        )

        # Store lexicon terms
        for term in data.get("lexicon", []):
            term_name = term.get("term", "unknown")
            term_slug = _slugify(term_name)
            payload: Dict[str, Any] = {
                "industry_id": industry_id,
                "term": term_name,
                "context": term.get("context", ""),
                "primitive": term.get("primitive", ""),
                "severity": term.get("severity", "info"),
                "requires": term.get("requires", []),
                "args_template": term.get("args_template", {}),
                "guardrails": term.get("guardrails", {}),
            }
            r.set(f"mcr:lexicon:{industry_id}:{term_slug}", json.dumps(payload))


if __name__ == "__main__":
    seed_lexicons()
