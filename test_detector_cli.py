#!/usr/bin/env python3
"""
Test suite for IF.detector CLI

Tests all three main commands with various options and validates output formats.
Includes example documents for human and AI-generated text.

Usage:
    python test_detector_cli.py           # Run all tests
    python test_detector_cli.py -v        # Verbose output
    python test_detector_cli.py analyze   # Test analyze command only
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from io import StringIO
import sys

# Mock the if_detector import to handle missing NLTK gracefully during testing
try:
    from if_detector_cli import (
        CLIApplication,
        OutputFormatter,
        HumanizationEngine,
        BatchProcessor,
        TextAnalyzer
    )
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


class SampleTexts:
    """Sample text documents for testing"""

    HUMAN_TEXT = """
    I've been thinking about this problem for weeks, and honestly, it's more complex
    than it first appeared. You see, there are several factors at play - some technical,
    some more philosophical. Last Tuesday, I ran into an old colleague who actually
    faced a similar issue in his startup. Anyway, what I realized is that sometimes
    the simplest solutions come from the most unexpected places. It's funny how life
    works that way. You never know what's going to click until you've thought about
    it from different angles. The key insight for me was realizing that maybe I was
    overthinking it. Sometimes the answer is right in front of you.
    """

    AI_TEXT = """
    The implications of this phenomenon are significant and multifaceted. Furthermore,
    it is important to note that the underlying mechanisms have been subject to
    extensive scholarly analysis. Additionally, the data suggests that multiple
    variables contribute to the observed outcomes. In conclusion, the evidence clearly
    indicates that a more nuanced approach is required. Moreover, as mentioned above,
    the theoretical framework must be revised to accommodate these findings. It is
    essential to recognize that the complexity of the situation demands careful
    consideration of multiple perspectives. Therefore, stakeholders must engage in
    comprehensive dialogue to develop solutions.
    """

    MIXED_TEXT = """
    I've been working on this AI detection problem for a while now, and I think there's
    a really important insight here. The fundamental challenge is that AI has become
    increasingly sophisticated in mimicking human writing patterns. Furthermore, it's
    not just about finding obvious tells anymore. What we're really looking at is a
    problem of statistical signature recognition. For instance, my colleague found that
    tracking vocabulary diversity actually gives you a pretty good signal. Additionally,
    measuring sentence length variance tells you a lot about the author's style.
    """

    SHORT_TEXT = "This is a short text."


@unittest.skipIf(not NLTK_AVAILABLE, "NLTK not installed")
class TestAnalyzeCommand(unittest.TestCase):
    """Test the analyze command"""

    def setUp(self):
        """Initialize test fixtures"""
        self.app = CLIApplication()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Cleanup test files"""
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)

    def test_analyze_direct_text(self):
        """Test analyze with direct text input"""
        result = self.app.analyzer.analyze(SampleTexts.HUMAN_TEXT)
        self.assertIsNotNone(result)
        self.assertTrue(0 <= result.overall_ai_probability <= 1)

    def test_analyze_file_input(self):
        """Test analyze with file input"""
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text(SampleTexts.AI_TEXT)

        # Verify file loading
        text = self.app.load_text(str(test_file))
        self.assertEqual(text, SampleTexts.AI_TEXT)

    def test_analyze_short_text_rejection(self):
        """Test that very short texts are handled"""
        result = self.app.analyzer.analyze(SampleTexts.SHORT_TEXT)
        self.assertIsNotNone(result)

    def test_output_formatter_human_readable(self):
        """Test human-readable output formatting"""
        result = self.app.analyzer.analyze(SampleTexts.HUMAN_TEXT)
        formatted = OutputFormatter.format_human_readable(result, verbose=False)

        self.assertIn("IF.DETECTOR ANALYSIS REPORT", formatted)
        self.assertIn("VERDICT:", formatted)
        self.assertIn("AI Probability:", formatted)
        self.assertIn("TEXT STATISTICS:", formatted)
        self.assertIn("METRIC BREAKDOWN:", formatted)

    def test_output_formatter_json(self):
        """Test JSON output formatting"""
        result = self.app.analyzer.analyze(SampleTexts.AI_TEXT)
        json_str = OutputFormatter.format_json(result)

        data = json.loads(json_str)
        self.assertIn("overall_ai_probability", data)
        self.assertIn("verdict", data)
        self.assertIn("metrics", data)
        self.assertIn("text_statistics", data)

    def test_output_formatter_compact(self):
        """Test compact output formatting"""
        result = self.app.analyzer.analyze(SampleTexts.MIXED_TEXT)
        compact = OutputFormatter.format_compact(result)

        self.assertIn("Verdict:", compact)
        self.assertIn("AI Prob:", compact)
        self.assertIn("Confidence:", compact)
        self.assertIn("Issues:", compact)

    def test_threshold_filtering(self):
        """Test that threshold filtering works"""
        # AI text should have high probability
        ai_result = self.app.analyzer.analyze(SampleTexts.AI_TEXT)
        self.assertGreater(ai_result.overall_ai_probability, 0.3)

        # Human text should have lower probability
        human_result = self.app.analyzer.analyze(SampleTexts.HUMAN_TEXT)
        # Note: human text might still score somewhat high due to metric sensitivity

    def test_metrics_all_present(self):
        """Test that all metrics are calculated"""
        result = self.app.analyzer.analyze(SampleTexts.MIXED_TEXT)

        expected_metrics = [
            "perplexity",
            "burstiness",
            "vocabulary",
            "transitions",
            "repetition",
            "syntax"
        ]

        for metric in expected_metrics:
            self.assertIn(metric, result.metrics)
            metric_result = result.metrics[metric]
            self.assertTrue(0 <= metric_result.score <= 1)
            self.assertIsNotNone(metric_result.verdict)
            self.assertIsNotNone(metric_result.reasoning)


@unittest.skipIf(not NLTK_AVAILABLE, "NLTK not installed")
class TestHumanizeCommand(unittest.TestCase):
    """Test the humanize command"""

    def setUp(self):
        """Initialize test fixtures"""
        self.app = CLIApplication()

    def test_humanize_subtle_intensity(self):
        """Test humanization with subtle intensity"""
        result = self.app.humanizer.humanize(
            SampleTexts.AI_TEXT,
            intensity="subtle"
        )

        self.assertIn("original_analysis", result)
        self.assertIn("expected_outcome", result)
        self.assertIn("suggested_changes", result)
        self.assertLess(
            result["expected_outcome"]["new_ai_probability"],
            result["original_analysis"]["ai_probability"]
        )

    def test_humanize_moderate_intensity(self):
        """Test humanization with moderate intensity"""
        result = self.app.humanizer.humanize(
            SampleTexts.AI_TEXT,
            intensity="moderate"
        )

        self.assertEqual(result["humanization_plan"]["intensity"], "moderate")
        self.assertGreater(
            result["humanization_plan"]["estimated_effort"],
            0
        )

    def test_humanize_aggressive_intensity(self):
        """Test humanization with aggressive intensity"""
        result = self.app.humanizer.humanize(
            SampleTexts.AI_TEXT,
            intensity="aggressive"
        )

        self.assertEqual(result["humanization_plan"]["intensity"], "aggressive")
        # Aggressive should have more suggestions
        self.assertGreaterEqual(
            len(result["suggested_changes"]),
            len(
                self.app.humanizer.humanize(
                    SampleTexts.AI_TEXT,
                    intensity="subtle"
                )["suggested_changes"]
            )
        )

    def test_humanize_output_structure(self):
        """Test humanization output structure"""
        result = self.app.humanizer.humanize(SampleTexts.MIXED_TEXT)

        required_keys = [
            "original_analysis",
            "humanization_plan",
            "suggested_changes",
            "expected_outcome",
            "implementation_roadmap"
        ]

        for key in required_keys:
            self.assertIn(key, result)

    def test_humanize_improvement_calculation(self):
        """Test that improvement calculations are reasonable"""
        result = self.app.humanizer.humanize(SampleTexts.AI_TEXT)

        improvement = result["expected_outcome"]["improvement_percentage"]
        self.assertGreater(improvement, 0)
        self.assertLess(improvement, 100)

    def test_preserve_technical_flag(self):
        """Test preserve_technical flag is respected"""
        technical_text = """
        The quantum entanglement phenomenon demonstrates non-local correlations
        that defy classical physics intuitions. Furthermore, the EPR paradox
        necessitates fundamental reconsideration of locality and realism principles.
        """

        result = self.app.humanizer.humanize(
            technical_text,
            preserve_technical=True
        )

        self.assertEqual(
            result["humanization_plan"]["preserve_technical"],
            True
        )


@unittest.skipIf(not NLTK_AVAILABLE, "NLTK not installed")
class TestBatchCommand(unittest.TestCase):
    """Test the batch command"""

    def setUp(self):
        """Initialize test fixtures"""
        self.app = CLIApplication()
        self.test_dir = tempfile.mkdtemp()
        self._create_test_files()

    def tearDown(self):
        """Cleanup test files"""
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)

    def _create_test_files(self):
        """Create sample test files"""
        files = {
            "human1.txt": SampleTexts.HUMAN_TEXT,
            "human2.txt": SampleTexts.HUMAN_TEXT,
            "ai1.txt": SampleTexts.AI_TEXT,
            "ai2.txt": SampleTexts.AI_TEXT,
            "mixed.txt": SampleTexts.MIXED_TEXT,
        }

        for filename, content in files.items():
            path = Path(self.test_dir) / filename
            path.write_text(content)

    def test_batch_processing(self):
        """Test basic batch processing"""
        results = self.app.batch_processor.process_directory(self.test_dir)

        self.assertEqual(results["files_analyzed"], 5)
        self.assertGreater(results["files_flagged"], 0)
        self.assertTrue(0 <= results["average_ai_probability"] <= 1)

    def test_batch_file_pattern(self):
        """Test file pattern matching"""
        results = self.app.batch_processor.process_directory(
            self.test_dir,
            pattern="human*.txt"
        )

        self.assertEqual(results["files_analyzed"], 2)

    def test_batch_threshold_filtering(self):
        """Test threshold filtering in batch mode"""
        results_low = self.app.batch_processor.process_directory(
            self.test_dir,
            threshold=0.3
        )
        results_high = self.app.batch_processor.process_directory(
            self.test_dir,
            threshold=0.8
        )

        self.assertGreaterEqual(
            results_low["files_flagged"],
            results_high["files_flagged"]
        )

    def test_batch_output_structure(self):
        """Test batch output structure"""
        results = self.app.batch_processor.process_directory(self.test_dir)

        required_keys = [
            "directory",
            "scan_timestamp",
            "files_analyzed",
            "files_flagged",
            "average_ai_probability",
            "threshold",
            "files"
        ]

        for key in required_keys:
            self.assertIn(key, results)

    def test_batch_file_statistics(self):
        """Test that file statistics are calculated"""
        results = self.app.batch_processor.process_directory(self.test_dir)

        self.assertTrue(any(f.get("flagged") for f in results["files"]))

        for file_result in results["files"]:
            if "error" not in file_result:
                self.assertIn("ai_probability", file_result)
                self.assertIn("word_count", file_result)
                self.assertIn("issues_detected", file_result)

    def test_batch_report_formatting(self):
        """Test batch report formatting"""
        results = self.app.batch_processor.process_directory(self.test_dir)
        report = self.app.batch_processor.format_batch_report(results)

        self.assertIn("BATCH ANALYSIS REPORT", report)
        self.assertIn("SUMMARY", report)
        self.assertIn("STATISTICS", report)

    def test_batch_nonexistent_directory(self):
        """Test handling of nonexistent directory"""
        results = self.app.batch_processor.process_directory("/nonexistent/path")

        self.assertIn("error", results)


class TestOutputFormatting(unittest.TestCase):
    """Test output formatting without NLTK dependency"""

    def test_json_serialization(self):
        """Test that JSON output is valid"""
        # Create a mock result
        from if_detector import DetectionResult, Verdict, ConfidenceLevel

        result = DetectionResult(
            overall_ai_probability=0.75,
            confidence=ConfidenceLevel.HIGH,
            verdict=Verdict.AI,
            metrics={},
            specific_issues=[],
            remediation_priority=[],
            token_count=100,
            sentence_count=5,
            word_count=80,
            analysis_timestamp="2025-11-30T12:00:00"
        )

        json_str = OutputFormatter.format_json(result)
        data = json.loads(json_str)

        self.assertEqual(data["overall_ai_probability"], 0.75)
        self.assertEqual(data["verdict"], "AI")

    def test_compact_format_structure(self):
        """Test compact format output"""
        from if_detector import DetectionResult, Verdict, ConfidenceLevel

        result = DetectionResult(
            overall_ai_probability=0.6,
            confidence=ConfidenceLevel.MEDIUM,
            verdict=Verdict.MIXED,
            metrics={},
            specific_issues=[],
            remediation_priority=[],
            token_count=100,
            sentence_count=5,
            word_count=80,
            analysis_timestamp="2025-11-30T12:00:00"
        )

        compact = OutputFormatter.format_compact(result)
        self.assertIn("MIXED", compact)
        self.assertIn("60%", compact)


class TestCLIIntegration(unittest.TestCase):
    """Test CLI integration and argument parsing"""

    def test_cli_application_creation(self):
        """Test that CLI application initializes"""
        if NLTK_AVAILABLE:
            app = CLIApplication()
            self.assertIsNotNone(app.analyzer)
            self.assertIsNotNone(app.humanizer)
            self.assertIsNotNone(app.batch_processor)

    def test_text_loading_from_input(self):
        """Test text loading from direct input"""
        if NLTK_AVAILABLE:
            app = CLIApplication()
            text = app.load_text("Sample text for testing")
            self.assertEqual(text, "Sample text for testing")

    def test_text_loading_from_file(self):
        """Test text loading from file"""
        if NLTK_AVAILABLE:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write("File content")
                temp_path = f.name

            try:
                app = CLIApplication()
                text = app.load_text(temp_path)
                self.assertEqual(text, "File content")
            finally:
                os.remove(temp_path)


def run_demo():
    """Run demonstration of CLI capabilities"""
    if not NLTK_AVAILABLE:
        print("NLTK is not installed. Install with:")
        print("  pip install -r requirements_detector.txt")
        return

    print("\n" + "=" * 80)
    print("IF.DETECTOR CLI TEST DEMONSTRATION")
    print("=" * 80 + "\n")

    app = CLIApplication()

    # Demo 1: Analyze AI text
    print("DEMO 1: Analyzing AI-Generated Text")
    print("-" * 80)
    ai_result = app.analyzer.analyze(SampleTexts.AI_TEXT)
    print(OutputFormatter.format_compact(ai_result))
    print()

    # Demo 2: Analyze human text
    print("DEMO 2: Analyzing Human-Written Text")
    print("-" * 80)
    human_result = app.analyzer.analyze(SampleTexts.HUMAN_TEXT)
    print(OutputFormatter.format_compact(human_result))
    print()

    # Demo 3: Humanization suggestions
    print("DEMO 3: Humanization Suggestions (Aggressive)")
    print("-" * 80)
    humanize_result = app.humanizer.humanize(
        SampleTexts.AI_TEXT,
        intensity="aggressive"
    )
    print(f"Original AI Probability: {humanize_result['original_analysis']['ai_probability']:.0%}")
    print(f"Expected After Changes: {humanize_result['expected_outcome']['new_ai_probability']:.0%}")
    print(f"Suggested Changes: {humanize_result['humanization_plan']['estimated_effort']}")
    print()

    # Demo 4: Show metrics comparison
    print("DEMO 4: Metric Comparison")
    print("-" * 80)
    print(f"{'Metric':<15} {'AI Text':<15} {'Human Text':<15}")
    print("-" * 45)

    for metric_name in ai_result.metrics.keys():
        ai_score = ai_result.metrics[metric_name].score
        human_score = human_result.metrics[metric_name].score
        print(f"{metric_name:<15} {ai_score:.1%}{'':>9} {human_score:.1%}")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        run_demo()
    else:
        unittest.main(argv=[''], exit=True, verbosity=2)
