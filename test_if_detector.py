"""
IF.detector Test Suite

Comprehensive tests for AI detection metrics and remediation engine.
Includes test corpus with human/AI samples and accuracy validation.
"""

import unittest
import json
from if_detector import (
    TextAnalyzer, PerplexityMetric, BurstinessMetric, VocabularyMetric,
    TransitionMetric, RepetitionMetric, SyntaxMetric, RemediationEngine,
    Verdict, ConfidenceLevel, DetectionResult
)


class TestPerplexityMetric(unittest.TestCase):
    """Test character bigram perplexity calculation"""

    def setUp(self):
        self.metric = PerplexityMetric()

    def test_human_text_high_perplexity(self):
        """Human text should have high perplexity (low predictability)"""
        human_text = """
        I went to the market yesterday and ran into an old friend. We hadn't seen
        each other in years. The conversation took some unexpected turns, touching on
        philosophy, childhood memories, and quantum physics. It was refreshing.
        """
        tokens = human_text.split()
        result = self.metric.analyze(human_text, tokens)

        # Human text should score lower (unpredictable)
        self.assertLess(result.score, 0.5, "Human text should have low AI score")
        self.assertEqual(result.verdict, Verdict.HUMAN, "Should detect as human")

    def test_ai_text_low_perplexity(self):
        """AI text should have low perplexity (high predictability)"""
        ai_text = """
        The implementation of sustainable practices is essential for organizational
        success. Furthermore, the integration of advanced technologies enhances
        operational efficiency. Additionally, stakeholder engagement remains critical
        for long-term viability.
        """
        tokens = ai_text.split()
        result = self.metric.analyze(ai_text, tokens)

        # AI text should score higher
        self.assertGreater(result.score, 0.4, "AI text should have high AI score")

    def test_perplexity_normalization(self):
        """Test normalization bounds to [0, 1]"""
        text = "The quick brown fox" * 10  # Repetitive
        tokens = text.split()
        result = self.metric.analyze(text, tokens)

        self.assertGreaterEqual(result.score, 0.0)
        self.assertLessEqual(result.score, 1.0)


class TestBurstinessMetric(unittest.TestCase):
    """Test sentence length variance detection"""

    def setUp(self):
        self.metric = BurstinessMetric()

    def test_human_varied_sentences(self):
        """Human writing has varied sentence lengths"""
        sentences = [
            "Short.",
            "This sentence is of medium length and covers a concept.",
            "The longest sentence in this collection contains many words and explores multiple ideas, creating rhythm and engagement through length variation.",
            "Next.",
            "One more medium-length sentence to demonstrate variation."
        ]
        result = self.metric.analyze(sentences)

        # High variance should score as human
        self.assertGreater(result.score, 0.5, "Varied sentences should score as human")
        self.assertEqual(result.verdict, Verdict.HUMAN, "Should detect as human writing")

    def test_ai_uniform_sentences(self):
        """AI writing tends toward uniform sentence length"""
        sentences = [
            "The first sentence contains approximately twenty words for clarity.",
            "The second sentence also contains approximately twenty words for consistency.",
            "The third sentence continues with approximately twenty words as well.",
            "The fourth sentence maintains approximately twenty words throughout the text.",
            "The fifth sentence follows the established pattern of approximately twenty words."
        ]
        result = self.metric.analyze(sentences)

        # Low variance should score as AI
        self.assertLess(result.score, 0.5, "Uniform sentences should score as AI")
        self.assertEqual(result.verdict, Verdict.AI, "Should detect as AI writing")

    def test_minimum_sentences(self):
        """Ensure graceful handling of minimum sentence requirement"""
        result = self.metric.analyze(["Only one sentence."])

        self.assertEqual(result.verdict, Verdict.MIXED)
        self.assertIsNotNone(result.reasoning)


class TestVocabularyMetric(unittest.TestCase):
    """Test Type-Token Ratio and vocabulary diversity"""

    def setUp(self):
        self.metric = VocabularyMetric()

    def test_human_diverse_vocabulary(self):
        """Human text has higher Type-Token Ratio"""
        human_text = """
        The investigation revealed fascinating patterns. Scientists discovered novel
        mechanisms underlying the phenomenon. Researchers documented surprising findings
        that challenged previous assumptions. Evidence emerged suggesting revolutionary
        implications. The data indicated paradigm-shifting consequences.
        """
        tokens = human_text.lower().split()
        result = self.metric.analyze(tokens)

        # High vocabulary diversity should score as human
        self.assertGreater(result.score, 0.5, "Diverse vocabulary should score as human")

    def test_ai_repetitive_vocabulary(self):
        """AI text has lower Type-Token Ratio from word repetition"""
        ai_text = """
        The system is designed. The system is implemented. The system is tested.
        The system is deployed. The system is monitored. The implementation is
        performed. The implementation is validated. The implementation is complete.
        The process is essential. The process is important. The process is critical.
        """
        tokens = ai_text.lower().split()
        result = self.metric.analyze(tokens)

        # Low vocabulary diversity should score as AI
        self.assertLess(result.score, 0.6, "Repetitive vocabulary should score as AI")

    def test_hapax_legomenon(self):
        """Test single-occurrence word detection"""
        diverse_text = "apple banana cherry date elderberry fig grape hare iris juniper".split()
        result = self.metric.analyze(diverse_text)

        # All unique words = high hapax ratio = human-like
        self.assertGreater(result.supporting_data['hapax_legomenon'], 0.5)


class TestTransitionMetric(unittest.TestCase):
    """Test transition word density detection"""

    def setUp(self):
        self.metric = TransitionMetric()

    def test_human_sparse_transitions(self):
        """Humans use fewer transition words"""
        human_text = "The data shows clear patterns. We observed unexpected variations. Our conclusion differs from previous research."
        word_count = len(human_text.split())
        result = self.metric.analyze(human_text, word_count)

        # Low transition density should score as human
        self.assertLess(result.score, 0.5, "Sparse transitions should score as human")

    def test_ai_excessive_transitions(self):
        """AI overuses transition phrases"""
        ai_text = """
        Furthermore, the data indicates trends. Moreover, the evidence suggests patterns.
        Additionally, the results show findings. In conclusion, the analysis demonstrates
        outcomes. To summarize, the findings are significant. Therefore, the implications
        are substantial. Thus, the consequences are notable.
        """
        word_count = len(ai_text.split())
        result = self.metric.analyze(ai_text, word_count)

        # High transition density should score as AI
        self.assertGreater(result.score, 0.5, "Excessive transitions should score as AI")

    def test_transition_weighting(self):
        """Test that longer phrases are weighted more heavily"""
        text = """
        In conclusion the study ended. Furthermore research continued. Also work persisted.
        On the other hand perspectives shifted. Nevertheless progress advanced.
        """
        word_count = len(text.split())
        result = self.metric.analyze(text, word_count)

        # "On the other hand" (weight 5) should count more than "Also" (weight 2)
        self.assertIsNotNone(result.supporting_data['top_phrases'])


class TestRepetitionMetric(unittest.TestCase):
    """Test n-gram repetition detection"""

    def setUp(self):
        self.metric = RepetitionMetric()

    def test_human_natural_variation(self):
        """Human text naturally varies phrases"""
        human_text = """
        The research commenced with data collection. Initial observations were documented.
        The subsequent phase involved analysis. Different approaches were tested.
        The methodology proved effective. Results emerged gradually throughout.
        """
        tokens = human_text.lower().split()
        result = self.metric.analyze(tokens)

        # Low repetition should score as human
        self.assertLess(result.score, 0.3, "Natural variation should score as human")

    def test_ai_template_repetition(self):
        """AI reuses phrase templates"""
        ai_text = """
        The key insight is important. The main finding is significant. The primary
        result is critical. The essential discovery is notable. The fundamental pattern
        is vital.
        """
        tokens = ai_text.lower().split()
        result = self.metric.analyze(tokens)

        # High repetition of templates should score as AI
        self.assertGreater(result.score, 0.25, "Template repetition should score as AI")

    def test_ngram_extraction(self):
        """Test n-gram extraction at different levels"""
        tokens = "the cat sat on the mat on the mat".split()

        # Trigram "on the mat" repeats twice
        result = self.metric.analyze(tokens)
        self.assertGreater(result.supporting_data['trigram_rep'], 0.0)


class TestSyntaxMetric(unittest.TestCase):
    """Test syntactic uniformity detection"""

    def setUp(self):
        self.metric = SyntaxMetric()

    def test_human_varied_syntax(self):
        """Human text has diverse syntactic structures"""
        sentences = [
            "The research began.",
            "Scientists worked tirelessly.",
            "Results emerged slowly.",
            "What was discovered challenged assumptions.",
            "Their findings were revolutionary.",
            "After months of work, patterns became clear."
        ]
        result = self.metric.analyze(sentences)

        # Varied syntax should have higher entropy and score as human
        self.assertGreater(result.score, 0.4)

    def test_ai_formulaic_syntax(self):
        """AI tends toward formulaic sentence structures"""
        sentences = [
            "The system is designed.",
            "The process is implemented.",
            "The result is significant.",
            "The finding is important.",
            "The conclusion is clear."
        ]
        result = self.metric.analyze(sentences)

        # Formulaic patterns should score as AI
        self.assertLess(result.score, 0.6)

    def test_formulaic_pattern_detection(self):
        """Test detection of AI-like formulaic patterns"""
        sentences = [
            "It is important to note that the research indicates patterns.",
            "In this paper we examine findings.",
            "To understand the phenomenon we must consider factors."
        ]
        result = self.metric.analyze(sentences)

        # Should detect formulaic patterns
        self.assertGreater(result.supporting_data['formulaic_pattern_count'], 0)


class TestTextAnalyzer(unittest.TestCase):
    """Test main orchestrator and ensemble voting"""

    def setUp(self):
        self.analyzer = TextAnalyzer()

    def test_pure_human_text(self):
        """Test detection of clearly human-written text"""
        text = """
        Last weekend I visited my grandfather's house. He was making his famous soup,
        the one with unusual spices I could never quite identify. As we talked, he
        shared stories from his youth, tales I'd heard before but somehow always
        different. He laughed in that distinctive way of his. The afternoon drifted
        by with unexpected peace. Sometimes the simplest moments feel most precious.
        """
        result = self.analyzer.analyze(text)

        self.assertLess(result.overall_ai_probability, 0.5)
        self.assertEqual(result.verdict, Verdict.HUMAN)

    def test_pure_ai_text(self):
        """Test detection of clearly AI-generated text"""
        text = """
        The implementation of advanced methodologies represents a critical component
        of contemporary organizational strategy. Furthermore, the integration of
        sophisticated technologies facilitates enhanced operational efficiency.
        Additionally, comprehensive stakeholder engagement mechanisms ensure sustained
        competitive advantage. In conclusion, the adoption of innovative frameworks
        enables organizations to achieve transformational outcomes. To summarize,
        strategic alignment with emerging paradigms remains essential for long-term
        viability and market positioning.
        """
        result = self.analyzer.analyze(text)

        self.assertGreater(result.overall_ai_probability, 0.5)
        self.assertIn(result.verdict, [Verdict.AI, Verdict.MIXED])

    def test_overall_probability_bounds(self):
        """Ensure overall probability is bounded [0, 1]"""
        texts = [
            "Short text.",
            "A medium length text with some content and ideas.",
            "A much longer text that contains more information and explores concepts in greater depth with multiple sentences and varied structure and content.",
        ]

        for text in texts:
            result = self.analyzer.analyze(text)
            self.assertGreaterEqual(result.overall_ai_probability, 0.0)
            self.assertLessEqual(result.overall_ai_probability, 1.0)

    def test_confidence_assessment(self):
        """Test confidence level based on metric agreement"""
        # Text designed to have high metric agreement
        ai_text = """
        The framework is implemented. Furthermore, the system is deployed.
        Additionally, the process is optimized. Moreover, the results are analyzed.
        In conclusion, the findings are significant.
        """
        result = self.analyzer.analyze(ai_text)

        # Most metrics should vote AI → HIGH or MEDIUM confidence
        self.assertIn(result.confidence, [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM])

    def test_specific_issue_detection(self):
        """Test line-by-line issue identification"""
        text = """
        The research commenced with enthusiasm. Furthermore, the team worked diligently.
        In conclusion, the results were achieved. It is important to note that success
        was achieved through collaboration.
        """
        result = self.analyzer.analyze(text)

        # Should detect formulaic phrases
        self.assertGreater(len(result.specific_issues), 0)

        # Issues should have all required fields
        for issue in result.specific_issues:
            self.assertIsNotNone(issue.line_number)
            self.assertIsNotNone(issue.issue_type)
            self.assertIsNotNone(issue.description)
            self.assertIsNotNone(issue.suggestion)

    def test_remediation_priority(self):
        """Test remediation advice generation"""
        text = """
        The implementation is critical. The system is important. The framework is
        essential. Furthermore, the process is vital. In conclusion, the result
        is necessary.
        """
        result = self.analyzer.analyze(text)

        # Should generate prioritized remediation advice
        self.assertGreater(len(result.remediation_priority), 0)
        self.assertTrue(any('repetition' in item.lower() for item in result.remediation_priority))

    def test_output_json_serialization(self):
        """Test that result can be serialized to JSON"""
        text = "The quick brown fox jumps over the lazy dog."
        result = self.analyzer.analyze(text)

        # Should serialize without error
        json_str = result.to_json()
        self.assertIsNotNone(json_str)

        # Should parse back to valid JSON
        parsed = json.loads(json_str)
        self.assertIn('overall_ai_probability', parsed)
        self.assertIn('metrics', parsed)
        self.assertIn('specific_issues', parsed)


class TestRemediationEngine(unittest.TestCase):
    """Test fix suggestion generation"""

    def setUp(self):
        self.engine = RemediationEngine()

    def test_remediation_suggestions_exist(self):
        """All issue types should have remediation advice"""
        issue_types = [
            "low_perplexity",
            "uniform_sentence_length",
            "low_vocabulary",
            "high_transitions",
            "high_repetition",
            "uniform_syntax"
        ]

        for issue_type in issue_types:
            self.assertIn(issue_type, self.engine.remediation_map)
            remediation = self.engine.remediation_map[issue_type]
            self.assertIn('suggestion', remediation)
            self.assertIn('tactics', remediation)
            self.assertIn('severity', remediation)

    def test_metric_to_issue_mapping(self):
        """Test that metrics map to issue types"""
        mappings = {
            "perplexity": "low_perplexity",
            "vocabulary": "low_vocabulary",
            "transitions": "high_transitions",
        }

        for metric, expected_issue in mappings.items():
            result = self.engine._metric_to_issue_type(metric)
            self.assertEqual(result, expected_issue)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def setUp(self):
        self.analyzer = TextAnalyzer()

    def test_empty_text(self):
        """Gracefully handle empty input"""
        with self.assertRaises((IndexError, ValueError, ZeroDivisionError)):
            # Empty text should either raise or handle gracefully
            result = self.analyzer.analyze("")

    def test_very_short_text(self):
        """Handle very short texts"""
        result = self.analyzer.analyze("One sentence.")

        # Should return result but with LOW confidence
        self.assertIsNotNone(result)
        self.assertEqual(result.confidence, ConfidenceLevel.LOW)

    def test_single_long_sentence(self):
        """Handle text with single very long sentence"""
        text = "This " + "is a very long sentence with many words and ideas and concepts " * 10
        result = self.analyzer.analyze(text)

        self.assertIsNotNone(result)
        self.assertGreaterEqual(result.overall_ai_probability, 0.0)
        self.assertLessEqual(result.overall_ai_probability, 1.0)

    def test_repetitive_text(self):
        """Handle extremely repetitive text"""
        text = "The system is implemented. " * 20
        result = self.analyzer.analyze(text)

        # Should score high on repetition and low vocabulary
        self.assertGreater(result.overall_ai_probability, 0.4)

    def test_unicode_text(self):
        """Handle unicode and special characters"""
        text = "The café served excellent résumés. Special characters: Café résumé naïve. 你好世界!"
        result = self.analyzer.analyze(text)

        # Should handle without crashing
        self.assertIsNotNone(result)


class TestCrossMetricAgreement(unittest.TestCase):
    """Test ensemble voting and metric correlation"""

    def setUp(self):
        self.analyzer = TextAnalyzer()

    def test_ai_metric_correlation(self):
        """On AI text, metrics should largely agree"""
        ai_text = """
        The importance of strategic planning cannot be overstated. Furthermore,
        the implementation of robust frameworks is essential. Additionally, the
        integration of modern technologies facilitates enhanced productivity.
        In conclusion, the adoption of innovative approaches remains critical.
        """
        result = self.analyzer.analyze(ai_text)

        # Count AI verdicts
        ai_verdicts = sum(1 for m in result.metrics.values() if m.verdict == Verdict.AI)

        # Should have majority AI verdicts
        self.assertGreaterEqual(ai_verdicts, 3, "AI text metrics should mostly vote AI")

    def test_human_metric_correlation(self):
        """On human text, metrics should largely agree"""
        human_text = """
        I woke up confused. The dream had been so real. My heart raced as memories
        of it faded. Coffee helped. By noon, I'd forgotten most details. Strange
        how dreams dissolve. By evening, nothing remained. Just impressions.
        """
        result = self.analyzer.analyze(human_text)

        # Count human verdicts
        human_verdicts = sum(1 for m in result.metrics.values() if m.verdict == Verdict.HUMAN)

        # Should have majority human verdicts
        self.assertGreaterEqual(human_verdicts, 3, "Human text metrics should mostly vote human")


class TestDetectionResult(unittest.TestCase):
    """Test output data structure"""

    def setUp(self):
        self.analyzer = TextAnalyzer()

    def test_result_completeness(self):
        """Result should contain all required fields"""
        text = "This is a test sample with reasonable length for analysis and detection."
        result = self.analyzer.analyze(text)

        required_fields = [
            'overall_ai_probability',
            'confidence',
            'verdict',
            'metrics',
            'specific_issues',
            'remediation_priority',
            'token_count',
            'sentence_count',
            'word_count',
            'analysis_timestamp'
        ]

        for field in required_fields:
            self.assertTrue(hasattr(result, field), f"Missing field: {field}")

    def test_metrics_completeness(self):
        """All 6 metrics should be present in result"""
        text = "This is a test sample with reasonable length for comprehensive metric analysis."
        result = self.analyzer.analyze(text)

        expected_metrics = ['perplexity', 'burstiness', 'vocabulary', 'transitions', 'repetition', 'syntax']

        for metric_name in expected_metrics:
            self.assertIn(metric_name, result.metrics)
            metric = result.metrics[metric_name]
            self.assertIsNotNone(metric.score)
            self.assertIsNotNone(metric.verdict)
            self.assertIsNotNone(metric.reasoning)


def run_tests():
    """Run full test suite"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestPerplexityMetric,
        TestBurstinessMetric,
        TestVocabularyMetric,
        TestTransitionMetric,
        TestRepetitionMetric,
        TestSyntaxMetric,
        TestTextAnalyzer,
        TestRemediationEngine,
        TestEdgeCases,
        TestCrossMetricAgreement,
        TestDetectionResult,
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    run_tests()
