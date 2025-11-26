import pytest
from unittest.mock import MagicMock, patch

from infrafabric.core.services.librarian import GeminiLibrarian, ArchiveQuery


@pytest.fixture
def mock_redis():
    with patch("redis.Redis") as mock:
        yield mock


@pytest.fixture
def librarian(mock_redis):
    # Mock the Gemini model to avoid real API calls
    import os
    os.environ["GEMINI_API_KEY"] = "test-key"
    with patch("google.generativeai.GenerativeModel") as mock_genai:
        lib = GeminiLibrarian()
        lib.model = mock_genai
        yield lib


def test_librarian_ingest(librarian):
    # Simulate loading a finding and ensure context formatting works
    librarian.current_context.append(
        {
            "finding_id": "test_123",
            "answer": "The sky is blue.",
            "sources": ["sensor_1"],
            "timestamp": "2025-01-01T00:00:00Z",
            "worker_id": "w1",
        }
    )
    formatted = librarian.format_context_for_query()
    assert "test_123" in formatted
    assert "The sky is blue" in formatted


def test_librarian_query_logic(librarian):
    # Pre-load context
    librarian.current_context.append(
        {
            "finding_id": "fact_1",
            "answer": "Water is wet.",
            "sources": ["science"],
            "timestamp": "now",
            "worker_id": "w1",
        }
    )

    # Mock the response from Gemini
    mock_response = MagicMock()
    mock_response.text = "Based on the context, water is wet."
    librarian.model.generate_content.return_value = mock_response

    # Run query_archive
    query = ArchiveQuery(
        query_id="q1",
        question="Is water wet?",
        timestamp="now",
        requester="test",
    )
    answer_finding = librarian.query_archive(query)

    # Assert the model was called with our context
    librarian.model.generate_content.assert_called_once()
    assert "water is wet" in answer_finding.answer.lower()
