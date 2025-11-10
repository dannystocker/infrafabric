#!/usr/bin/env python3
"""
IF Message Control - Philosophy-enforced message validation

Implements IF.ground principles as auto-enforced lint rules:
- Empiricism: Every claim must include evidence[]
- Verificationism: Every message must include content_hash
- Falsifiability: Every message must be signed
- Pragmatism: Use valid performative
- Coherentism: Set conversation_id + sequence_num
- Stoic Prudence: Include retry/backoff meta if request
"""

import sys
import json
from typing import List, Dict, Any
from hashlib import sha256


class IFMessageValidator:
    """Validates IFMessage against IF.ground philosophy principles"""

    VALID_PERFORMATIVES = {
        "request", "inform", "agree", "query-if", "refuse",
        "propose", "accept-proposal", "reject-proposal"
    }

    @classmethod
    def validate(cls, msg: Dict[str, Any]) -> List[str]:
        """
        Validate IFMessage against philosophy lint rules

        Returns: List of errors (empty = valid)
        """
        errors = []

        # Basic structure
        if "performative" not in msg:
            errors.append("missing 'performative'")
        elif msg["performative"] not in cls.VALID_PERFORMATIVES:
            errors.append(
                f"invalid performative '{msg['performative']}' "
                f"(must be one of {cls.VALID_PERFORMATIVES})"
            )

        if "conversation_id" not in msg:
            errors.append("missing 'conversation_id' (IF.ground:principle_5_coherentism)")

        if "content" not in msg:
            errors.append("missing 'content'")

        # IF.ground:principle_1 (Empiricism) - Evidence required
        content = msg.get("content", {})
        if isinstance(content, dict) and "claim" in content:
            if not content.get("evidence"):
                errors.append(
                    "missing 'evidence' for claim "
                    "(IF.ground:principle_1_observable_artifacts - Empiricism)"
                )

        # IF.ground:principle_2 (Verificationism) - Content-addressed
        if "content_hash" not in msg:
            errors.append(
                "missing 'content_hash' "
                "(IF.ground:principle_2_verificationism - Vienna Circle)"
            )
        else:
            # Verify content hash is correct
            canonical = json.dumps(content, sort_keys=True)
            expected_hash = f"sha256:{sha256(canonical.encode()).hexdigest()}"
            if msg["content_hash"] != expected_hash:
                errors.append(
                    f"content_hash mismatch: expected {expected_hash}, "
                    f"got {msg['content_hash']}"
                )

        # IF.ground:principle_7 (Falsifiability) - Signed
        if "signature" not in msg and "sig" not in msg:
            errors.append(
                "missing 'signature' or 'sig' "
                "(IF.ground:principle_7_falsifiability - Popper)"
            )

        # IF.ground:principle_5 (Coherentism) - Message ordering
        if "sequence_num" not in msg:
            errors.append(
                "missing 'sequence_num' "
                "(IF.ground:principle_5_coherentism - Neurath's Boat)"
            )

        # IF.ground:principle_8 (Stoic Prudence) - Retry logic for requests
        if msg.get("performative") == "request":
            if "stoic_resilience" not in msg.get("philosophy_metadata", {}):
                errors.append(
                    "missing 'philosophy_metadata.stoic_resilience' for request "
                    "(IF.ground:principle_8_stoic_prudence - Epictetus)"
                )

        return errors

    @classmethod
    def validate_and_report(cls, msg: Dict[str, Any], strict: bool = True) -> bool:
        """
        Validate message and print errors

        Args:
            msg: IFMessage to validate
            strict: If True, any error = invalid; if False, warnings only

        Returns: True if valid (or warnings only in non-strict mode)
        """
        errors = cls.validate(msg)

        if not errors:
            print("✓ Message valid (IF.TTT compliant)")
            return True

        print("✗ Message validation failed:")
        for error in errors:
            print(f"  - {error}")

        return not strict  # In strict mode, errors = invalid


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: ifctl.py <message.json> [--strict]")
        print("\nValidates IFMessage against IF.ground philosophy principles")
        print("\nExample:")
        print('  echo \'{"performative":"inform","content":{}}\' | python ifctl.py -')
        sys.exit(1)

    strict = "--strict" in sys.argv
    filepath = sys.argv[1]

    # Read message
    if filepath == "-":
        msg = json.load(sys.stdin)
    else:
        with open(filepath) as f:
            msg = json.load(f)

    # Validate
    valid = IFMessageValidator.validate_and_report(msg, strict=strict)
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
