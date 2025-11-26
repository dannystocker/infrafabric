import pytest

from infrafabric.core.services.librarian import GeminiLibrarian
from infrafabric.state.schema import ContextSchema


def test_imports():
    """Smoke Test: modules import without crashing."""
    assert GeminiLibrarian is not None
    assert ContextSchema is not None


def test_schema_validation():
    """Pydantic should enforce required fields."""
    with pytest.raises(Exception):
        ContextSchema(instance_id="test", tokens_used=10)
