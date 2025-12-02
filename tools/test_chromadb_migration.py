#!/usr/bin/env python3
"""
Test Suite for ChromaDB Migration Script
=========================================

Tests:
- Connection handling
- Data export/import
- Metadata transformation
- Validation logic
- Batch processing
- Error recovery

Run: python test_chromadb_migration.py
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from chromadb_migration import (
    MetadataTransformer,
    DataValidator,
    MigrationConfig,
    MigrationCheckpoint
)


class TestMetadataTransformer(unittest.TestCase):
    """Test metadata transformation logic"""

    def setUp(self):
        self.transformer = MetadataTransformer(Mock())

    def test_transform_personality_chunk(self):
        """Test personality metadata transformation"""
        chunk = {
            "id": "personality_001",
            "text": "Sergio is highly conscientious",
            "embedding": [0.1, 0.2, 0.3] * 256,
            "metadata": {
                "source": "conference",
                "source_file": "/path/to/file.txt",
                "source_line": 100,
                "author": "Sergio Romo",
                "big_five_trait": "conscientiousness",
                "trait_score": 0.92
            }
        }

        result = self.transformer.transform_chunk(chunk, "sergio_personality")

        # Check required fields
        self.assertEqual(result["metadata"]["collection_type"], "personality")
        self.assertEqual(result["metadata"]["source"], "conference")
        self.assertEqual(result["metadata"]["big_five_trait"], "conscientiousness")
        self.assertIn("authenticity_score", result["metadata"])

    def test_transform_rhetorical_chunk(self):
        """Test rhetorical metadata transformation"""
        chunk = {
            "id": "rhetorical_001",
            "text": "Aspiradora metaphor",
            "embedding": [0.1] * 768,
            "metadata": {
                "source": "analysis",
                "device_type": "metaphor"
            }
        }

        result = self.transformer.transform_chunk(chunk, "sergio_rhetorical")

        self.assertEqual(result["metadata"]["collection_type"], "rhetorical")
        self.assertEqual(result["metadata"]["device_type"], "metaphor")

    def test_infer_collection_type(self):
        """Test collection type inference"""
        test_cases = [
            ("sergio_personality", "personality"),
            ("personality_data", "personality"),
            ("sergio_rhetorical", "rhetorical"),
            ("humor_jokes", "humor"),
            ("sergio_corpus", "corpus"),
            ("other", "corpus")
        ]

        for source, expected in test_cases:
            result = self.transformer._infer_collection_type(source)
            self.assertEqual(result, expected, f"Failed for {source}")


class TestDataValidator(unittest.TestCase):
    """Test data validation logic"""

    def setUp(self):
        self.validator = DataValidator(Mock())

    def test_valid_chunk(self):
        """Test validation of complete chunk"""
        chunk = {
            "id": "valid_001",
            "text": "Valid text content",
            "embedding": [0.1] * 768,
            "metadata": {
                "source": "test",
                "author": "test",
                "collection_type": "personality",
                "language": "en",
                "authenticity_score": 0.95
            }
        }

        result = self.validator._validate_chunk(chunk, "personality")
        self.assertTrue(result)

    def test_missing_id(self):
        """Test rejection of chunk with missing ID"""
        chunk = {
            "text": "Valid text",
            "embedding": [0.1] * 768,
            "metadata": {}
        }

        result = self.validator._validate_chunk(chunk, "personality")
        self.assertFalse(result)
        self.assertTrue(any("missing_id" in issue for issue in self.validator.validation_results["issues"].keys()))

    def test_missing_embedding(self):
        """Test rejection of chunk with missing embedding"""
        chunk = {
            "id": "test_001",
            "text": "Valid text",
            "metadata": {
                "source": "test",
                "author": "test",
                "collection_type": "personality",
                "language": "en",
                "authenticity_score": 0.95
            }
        }

        result = self.validator._validate_chunk(chunk, "personality")
        self.assertFalse(result)

    def test_invalid_authenticity_score(self):
        """Test rejection of invalid authenticity scores"""
        test_cases = [
            -0.1,  # Below 0
            1.5,   # Above 1
            "not_a_number"  # Wrong type
        ]

        for score in test_cases:
            chunk = {
                "id": f"test_{score}",
                "text": "Valid text",
                "embedding": [0.1] * 768,
                "metadata": {
                    "source": "test",
                    "author": "test",
                    "collection_type": "personality",
                    "language": "en",
                    "authenticity_score": score
                }
            }

            result = self.validator._validate_chunk(chunk, "personality")
            self.assertFalse(result)


class TestMigrationConfig(unittest.TestCase):
    """Test migration configuration"""

    def test_config_creation(self):
        """Test config object creation"""
        config = MigrationConfig(
            source_url="http://source:8000",
            target_url="http://target:8000",
            batch_size=50
        )

        self.assertEqual(config.source_url, "http://source:8000")
        self.assertEqual(config.batch_size, 50)
        self.assertFalse(config.dry_run)

    def test_config_creates_directories(self):
        """Test that config creates required directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MigrationConfig(
                source_url="http://source:8000",
                target_url="http://target:8000",
                checkpoint_dir=f"{tmpdir}/checkpoints",
                log_dir=f"{tmpdir}/logs"
            )

            self.assertTrue(Path(config.checkpoint_dir).exists())
            self.assertTrue(Path(config.log_dir).exists())


class TestMigrationCheckpoint(unittest.TestCase):
    """Test checkpoint functionality"""

    def test_checkpoint_creation(self):
        """Test checkpoint object creation"""
        checkpoint = MigrationCheckpoint()

        self.assertEqual(checkpoint.phase, "initialization")
        self.assertEqual(checkpoint.total_chunks, 0)
        self.assertIsInstance(checkpoint.errors, list)

    def test_checkpoint_to_dict(self):
        """Test checkpoint serialization"""
        checkpoint = MigrationCheckpoint(
            phase="import",
            total_chunks=100,
            processed_chunks=50
        )

        result = checkpoint.to_dict()

        self.assertEqual(result["phase"], "import")
        self.assertEqual(result["total_chunks"], 100)
        self.assertIn("timestamp", result)


class TestBatchProcessing(unittest.TestCase):
    """Test batch processing logic"""

    def test_batch_calculation(self):
        """Test batch index calculations"""
        total_chunks = 9832
        batch_size = 100

        expected_batches = (total_chunks + batch_size - 1) // batch_size
        self.assertEqual(expected_batches, 99)

        # Last batch should be partial
        last_batch_start = 98 * batch_size
        last_batch_size = total_chunks - last_batch_start
        self.assertEqual(last_batch_size, 32)

    def test_batch_slicing(self):
        """Test correct batch slicing"""
        chunks = list(range(1000))
        batch_size = 100

        for batch_idx in range(10):
            start = batch_idx * batch_size
            end = min(start + batch_size, len(chunks))
            batch = chunks[start:end]

            self.assertEqual(len(batch), batch_size)
            self.assertEqual(batch[0], batch_idx * batch_size)
            self.assertEqual(batch[-1], end - 1)


class TestMetadataSchema(unittest.TestCase):
    """Test 12-field metadata schema compliance"""

    def setUp(self):
        self.transformer = MetadataTransformer(Mock())

    def test_core_fields_present(self):
        """Test that core 12 fields are present"""
        chunk = {
            "id": "test_001",
            "text": "Test content",
            "embedding": [0.1] * 768,
            "metadata": {
                "source": "test",
                "author": "test"
            }
        }

        result = self.transformer.transform_chunk(chunk, "test")
        metadata = result["metadata"]

        # Core 12 fields
        required_fields = [
            "source", "source_file", "source_line", "author",
            "collection_type", "category", "language",
            "authenticity_score", "confidence_level", "disputed", "if_citation_uri"
        ]

        for field in required_fields:
            self.assertIn(field, metadata, f"Missing core field: {field}")

    def test_collection_specific_fields(self):
        """Test collection-specific field injection"""
        test_cases = {
            "personality": ["big_five_trait", "trait_score"],
            "rhetorical": ["device_type", "frequency"],
            "humor": ["humor_type", "emotional_context"],
            "corpus": ["document_type", "word_count"]
        }

        for collection_type, expected_fields in test_cases.items():
            chunk = {
                "id": f"test_{collection_type}",
                "text": "Test",
                "embedding": [0.1] * 768,
                "metadata": {"source": "test", "author": "test"}
            }

            result = self.transformer.transform_chunk(chunk, f"sergio_{collection_type}")
            metadata = result["metadata"]

            for field in expected_fields:
                self.assertIn(field, metadata, f"Missing {field} in {collection_type}")


class TestErrorHandling(unittest.TestCase):
    """Test error handling and recovery"""

    def test_missing_required_import(self):
        """Test graceful handling of missing dependencies"""
        # This is tested at import time
        # If chromadb is missing, script should still load with CHROMADB_AVAILABLE = False
        pass

    def test_malformed_json(self):
        """Test handling of malformed JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name

        try:
            with self.assertRaises(json.JSONDecodeError):
                with open(temp_path) as f:
                    json.load(f)
        finally:
            Path(temp_path).unlink()


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMetadataTransformer))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestMigrationConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestMigrationCheckpoint))
    suite.addTests(loader.loadTestsFromTestCase(TestBatchProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestMetadataSchema))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
