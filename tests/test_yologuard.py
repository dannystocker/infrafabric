import pytest

from infrafabric.core.security.yologuard import SecretRedactorV3, shannon_entropy


@pytest.fixture
def guard():
    """Initialize the V3 Redactor."""
    return SecretRedactorV3()


# --- ENTROPY TESTS ---

def test_shannon_entropy_logic():
    """Verify entropy calculation for random vs structured data."""
    low = shannon_entropy(b"AAAAAAAA")
    assert low < 1.0

    high = shannon_entropy(b"sk-1234567890abcdef1234567890abcdef")
    assert high > 3.0


# --- PATTERN TESTS ---

def test_redact_standard_keys(guard):
    """Test standard regex patterns (AWS, Stripe, Private Keys)."""
    leaks = [
        ("AKIAIOSFODNN7EXAMPLE", "AWS Access Key"),
        ("sk_live_51Mz9...", "Stripe Secret"),
    ]

    for secret, name in leaks:
        content = f"My {name} is {secret}."
        redacted = guard.redact(content)
        # Redactor may replace with placeholder; ensure a change and a redaction marker
        assert redacted != content
        assert "REDACTED" in redacted


def test_wu_lun_relationship_validation(guard):
    """Confucian relationship logic (token + context)."""
    # Contextual leak (husband-wife: key + endpoint/header)
    contextual_leak = "Authorization: Bearer xy-12345-secret-token"
    redacted = guard.redact(contextual_leak)
    assert "xy-12345-secret-token" not in redacted


# --- EDGE CASES ---

def test_redaction_idempotency(guard):
    """Redacting an already redacted string should be stable."""
    original = "Key: AKIAIOSFODNN7EXAMPLE"
    once = guard.redact(original)
    twice = guard.redact(once)
    assert once == twice
    assert "AKIA" not in twice


def test_empty_input(guard):
    """Handle empty or None input gracefully."""
    assert guard.redact("") == ""
    assert guard.redact(None) is None
