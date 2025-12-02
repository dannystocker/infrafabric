"""
IF.detector: In-house GPTZero Alternative for AI Text Detection

Analyzes text for AI tells and provides specific remediation advice through:
- Perplexity scoring (log-likelihood of token sequences)
- Burstiness index (sentence length variance)
- Vocabulary richness metrics (TTR, hapax legomenon)
- Transition word density analysis
- N-gram repetition detection
- Syntactic pattern uniformity assessment

Architecture:
  TextAnalyzer (main orchestrator)
    ├── PerplexityMetric (token sequence analysis)
    ├── BurstinessMetric (sentence variation)
    ├── VocabularyMetric (lexical diversity)
    ├── TransitionMetric (connector frequency)
    ├── RepetitionMetric (n-gram analysis)
    ├── SyntaxMetric (structure uniformity)
    └── RemediationEngine (fix suggestions)
"""

import re
import math
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
from enum import Enum
import statistics
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
# parse_cfg and ChartParser removed - unused and deprecated in modern NLTK


class Verdict(Enum):
    """Detection confidence verdict"""
    HUMAN = "HUMAN"
    MIXED = "MIXED"
    AI = "AI"


class ConfidenceLevel(Enum):
    """Confidence in detection result"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class MetricResult:
    """Individual metric analysis result"""
    score: float  # 0.0-1.0 (0=human, 1=AI)
    human_range: str
    ai_range: str
    verdict: Verdict
    reasoning: str
    supporting_data: Dict[str, Any]


@dataclass
class IssueFlag:
    """Specific text issue identified"""
    line_number: int
    line_text: str
    issue_type: str
    description: str
    suggestion: str
    severity: str  # "low", "medium", "high"
    evidence: Dict[str, Any]


@dataclass
class DetectionResult:
    """Complete IF.detector analysis output"""
    overall_ai_probability: float
    confidence: ConfidenceLevel
    verdict: Verdict
    metrics: Dict[str, MetricResult]
    specific_issues: List[IssueFlag]
    remediation_priority: List[str]
    token_count: int
    sentence_count: int
    word_count: int
    analysis_timestamp: str

    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary"""
        return {
            "overall_ai_probability": self.overall_ai_probability,
            "confidence": self.confidence.value,
            "verdict": self.verdict.value,
            "metrics": {
                name: {
                    "score": result.score,
                    "human_range": result.human_range,
                    "ai_range": result.ai_range,
                    "verdict": result.verdict.value,
                    "reasoning": result.reasoning,
                    "supporting_data": result.supporting_data
                }
                for name, result in self.metrics.items()
            },
            "specific_issues": [
                {
                    "line": issue.line_number,
                    "line_text": issue.line_text[:100] + "..." if len(issue.line_text) > 100 else issue.line_text,
                    "issue_type": issue.issue_type,
                    "description": issue.description,
                    "suggestion": issue.suggestion,
                    "severity": issue.severity,
                    "evidence": issue.evidence
                }
                for issue in self.specific_issues
            ],
            "remediation_priority": self.remediation_priority,
            "text_statistics": {
                "token_count": self.token_count,
                "sentence_count": self.sentence_count,
                "word_count": self.word_count,
                "avg_sentence_length": self.word_count / max(1, self.sentence_count)
            }
        }

    def to_json(self) -> str:
        """Serialize to JSON with formatting"""
        return json.dumps(self.to_dict(), indent=2)


class PerplexityMetric:
    """
    Perplexity Score: Measures unpredictability of token sequences

    Lower perplexity = more predictable (more AI-like)
    Higher perplexity = more varied (more human-like)

    Algorithm:
    1. Build character n-gram distribution from reference corpus
    2. Calculate cross-entropy of input text against distribution
    3. Convert to perplexity (2^cross_entropy)
    4. Normalize: human_range 60-100, AI_range 20-50
    """

    def __init__(self):
        self.human_reference_perplexity = (60, 100)  # Empirical ranges
        self.ai_reference_perplexity = (20, 50)

    def analyze(self, text: str, tokens: List[str]) -> MetricResult:
        """
        Calculate perplexity using character-level n-gram model

        Args:
            text: Full input text
            tokens: Pre-tokenized words

        Returns:
            MetricResult with perplexity score and verdict
        """
        # Build character bigram distribution
        char_bigrams = self._extract_char_bigrams(text)

        # Calculate cross-entropy
        cross_entropy = self._calculate_cross_entropy(text, char_bigrams)

        # Convert to perplexity
        perplexity = 2 ** cross_entropy

        # Normalize to 0-1 scale
        # Lower perplexity (more predictable) -> higher AI score
        normalized_score = self._normalize_perplexity(perplexity)

        # Determine verdict
        if perplexity > 85:
            verdict = Verdict.HUMAN
        elif perplexity < 35:
            verdict = Verdict.AI
        else:
            verdict = Verdict.MIXED

        return MetricResult(
            score=normalized_score,
            human_range="60-100",
            ai_range="20-50",
            verdict=verdict,
            reasoning=f"Text perplexity: {perplexity:.2f}. " +
                     ("Unpredictable token sequences suggest human writing" if perplexity > 85
                      else "Highly predictable sequences characteristic of AI models" if perplexity < 35
                      else "Mixed predictability patterns"),
            supporting_data={
                "perplexity_raw": round(perplexity, 2),
                "cross_entropy": round(cross_entropy, 3),
                "char_bigram_count": len(char_bigrams),
                "unique_bigrams": len(set(char_bigrams.elements()))
            }
        )

    def _extract_char_bigrams(self, text: str) -> Counter:
        """Extract character bigram distribution"""
        text = text.lower()
        bigrams = [text[i:i+2] for i in range(len(text)-1)]
        return Counter(bigrams)

    def _calculate_cross_entropy(self, text: str, bigram_dist: Counter) -> float:
        """
        Calculate cross-entropy of text against bigram distribution

        CE = -sum(P(bigram) * log2(P(bigram)))
        """
        total_bigrams = sum(bigram_dist.values())
        text_lower = text.lower()

        cross_entropy = 0.0
        bigram_count = 0

        for i in range(len(text_lower) - 1):
            bigram = text_lower[i:i+2]
            if bigram in bigram_dist:
                prob = bigram_dist[bigram] / total_bigrams
                cross_entropy -= math.log2(prob + 1e-10)
                bigram_count += 1

        return cross_entropy / max(1, bigram_count) if bigram_count > 0 else 5.0

    def _normalize_perplexity(self, perplexity: float) -> float:
        """Normalize perplexity to 0-1 scale (0=human, 1=AI)"""
        # Invert: low perplexity (AI) = high score, high perplexity (human) = low score
        if perplexity > 100:
            return 0.0  # Definitely human
        elif perplexity < 20:
            return 1.0  # Definitely AI
        else:
            # Linear interpolation
            return (100 - perplexity) / 80


class BurstinessMetric:
    """
    Burstiness Index: Measures variance in sentence length distribution

    Formula: (std_dev / mean_length) of sentence lengths

    Low burstiness = uniform sentences (AI-like)
    High burstiness = varied sentences (human-like)

    Algorithm:
    1. Tokenize into sentences
    2. Calculate length of each sentence in words
    3. Compute std deviation and mean
    4. Burstiness = std_dev / mean
    5. Normalize: human_range 1.2-2.5, AI_range 0.3-0.8
    """

    def __init__(self):
        self.human_range = (1.2, 2.5)
        self.ai_range = (0.3, 0.8)

    def analyze(self, sentences: List[str]) -> MetricResult:
        """
        Calculate burstiness index from sentence length variance

        Args:
            sentences: Pre-tokenized sentences

        Returns:
            MetricResult with burstiness verdict
        """
        # Calculate sentence lengths in words
        sentence_lengths = [len(sent.split()) for sent in sentences]

        if len(sentence_lengths) < 2:
            return MetricResult(
                score=0.5,
                human_range="1.2-2.5",
                ai_range="0.3-0.8",
                verdict=Verdict.MIXED,
                reasoning="Insufficient sentences for burstiness analysis",
                supporting_data={"sentence_count": len(sentence_lengths)}
            )

        # Calculate statistics
        mean_length = statistics.mean(sentence_lengths)
        std_dev = statistics.stdev(sentence_lengths)
        burstiness = std_dev / mean_length if mean_length > 0 else 0

        # Normalize to 0-1
        normalized_score = self._normalize_burstiness(burstiness)

        # Determine verdict
        if burstiness >= self.human_range[0]:
            verdict = Verdict.HUMAN
        elif burstiness <= self.ai_range[1]:
            verdict = Verdict.AI
        else:
            verdict = Verdict.MIXED

        return MetricResult(
            score=normalized_score,
            human_range="1.2-2.5",
            ai_range="0.3-0.8",
            verdict=verdict,
            reasoning=f"Sentence burstiness: {burstiness:.3f}. " +
                     ("Natural variation in sentence length" if burstiness >= 1.2
                      else "Artificially uniform sentence structure" if burstiness <= 0.8
                      else "Mixed sentence length patterns"),
            supporting_data={
                "burstiness_raw": round(burstiness, 3),
                "mean_sentence_length": round(mean_length, 2),
                "std_dev": round(std_dev, 2),
                "min_length": min(sentence_lengths),
                "max_length": max(sentence_lengths),
                "sentence_count": len(sentence_lengths)
            }
        )

    def _normalize_burstiness(self, burstiness: float) -> float:
        """Normalize burstiness to 0-1 scale (0=AI, 1=human)"""
        # High burstiness (human) = high score, low burstiness (AI) = low score
        if burstiness > 2.5:
            return 1.0
        elif burstiness < 0.3:
            return 0.0
        else:
            # Linear interpolation
            return (burstiness - 0.3) / 2.2


class VocabularyMetric:
    """
    Vocabulary Richness: Measures lexical diversity

    Metrics:
    1. Type-Token Ratio (TTR): unique_words / total_words
    2. Hapax Legomenon: percentage of words appearing only once
    3. Vocabulary sophistication: %age of sophisticated vs. common words

    High TTR + high hapax = human writing
    Low TTR + low hapax = AI repetition

    Algorithm:
    1. Extract all words (lowercase, no punctuation)
    2. Count unique vs. total
    3. Count single-occurrence words
    4. Compare against sophistication lexicon
    5. Normalize: human_range 0.60-0.85, AI_range 0.35-0.55
    """

    def __init__(self):
        self.common_words = set(stopwords.words('english'))
        self.human_ttr_range = (0.60, 0.85)
        self.ai_ttr_range = (0.35, 0.55)

    def analyze(self, tokens: List[str]) -> MetricResult:
        """
        Calculate vocabulary richness metrics

        Args:
            tokens: Pre-tokenized words (lowercase, cleaned)

        Returns:
            MetricResult with vocabulary verdict
        """
        # Clean and normalize tokens
        clean_tokens = [t.lower() for t in tokens if t.isalpha()]

        if len(clean_tokens) < 10:
            return MetricResult(
                score=0.5,
                human_range="0.60-0.85",
                ai_range="0.35-0.55",
                verdict=Verdict.MIXED,
                reasoning="Insufficient tokens for vocabulary analysis",
                supporting_data={"token_count": len(clean_tokens)}
            )

        # Calculate Type-Token Ratio
        unique_words = set(clean_tokens)
        ttr = len(unique_words) / len(clean_tokens)

        # Calculate Hapax Legomenon
        word_freq = Counter(clean_tokens)
        hapax_count = sum(1 for count in word_freq.values() if count == 1)
        hapax_ratio = hapax_count / len(unique_words) if unique_words else 0

        # Vocabulary sophistication
        sophisticated = sum(1 for word in unique_words if word not in self.common_words)
        sophistication_ratio = sophisticated / len(unique_words) if unique_words else 0

        # Combined score
        combined_score = (ttr * 0.5) + (hapax_ratio * 0.3) + (sophistication_ratio * 0.2)

        # Determine verdict
        if ttr >= self.human_ttr_range[0]:
            verdict = Verdict.HUMAN
        elif ttr <= self.ai_ttr_range[1]:
            verdict = Verdict.AI
        else:
            verdict = Verdict.MIXED

        return MetricResult(
            score=combined_score,
            human_range="0.60-0.85",
            ai_range="0.35-0.55",
            verdict=verdict,
            reasoning=f"TTR: {ttr:.3f}, Hapax: {hapax_ratio:.1%}. " +
                     ("Rich, diverse vocabulary characteristic of human writing" if ttr > 0.65
                      else "Limited vocabulary with heavy repetition (AI-like)" if ttr < 0.50
                      else "Moderate vocabulary diversity"),
            supporting_data={
                "type_token_ratio": round(ttr, 3),
                "hapax_legomenon": round(hapax_ratio, 3),
                "sophistication_ratio": round(sophistication_ratio, 3),
                "unique_words": len(unique_words),
                "total_words": len(clean_tokens),
                "word_freq_distribution": {
                    "count_1": hapax_count,
                    "count_2_5": sum(1 for c in word_freq.values() if 2 <= c <= 5),
                    "count_6_plus": sum(1 for c in word_freq.values() if c > 5)
                }
            }
        )


class TransitionMetric:
    """
    Transition Word Density: Measures frequency of formulaic connectors

    AI often overuses transition phrases like:
    - "Furthermore", "Additionally", "Moreover"
    - "In conclusion", "As mentioned"
    - "It is important to note"
    - "To summarize", "In summary"

    Algorithm:
    1. Define list of common transition words/phrases
    2. Count occurrences in text
    3. Calculate density: transitions / total_words
    4. High density (>5%) = AI-like
    5. Normalize: human_range 0.5-2%, AI_range 4-8%
    """

    def __init__(self):
        self.transition_phrases = {
            # Additive
            'furthermore': 5, 'additionally': 5, 'moreover': 5, 'besides': 3,
            'in addition': 4, 'also': 2, 'as well as': 4,
            # Sequential
            'firstly': 3, 'secondly': 3, 'finally': 2, 'next': 2, 'then': 1,
            # Consequential
            'therefore': 4, 'thus': 3, 'as a result': 4, 'consequently': 4,
            'in conclusion': 4, 'to summarize': 4, 'in summary': 4,
            # Contrasting
            'however': 3, 'nevertheless': 3, 'yet': 1, 'on the other hand': 5,
            'in contrast': 4, 'conversely': 3,
            # Emphasizing
            'it is important to note': 6, 'notably': 2, 'particularly': 2,
            'indeed': 1, 'certainly': 2, 'obviously': 2,
            # Elaborating
            'that is': 2, 'namely': 2, 'for example': 3, 'such as': 2,
            'in other words': 4, 'specifically': 2
        }

        self.human_density_range = (0.005, 0.020)  # 0.5-2%
        self.ai_density_range = (0.040, 0.080)     # 4-8%

    def analyze(self, text: str, word_count: int) -> MetricResult:
        """
        Analyze transition word density

        Args:
            text: Full input text
            word_count: Total word count

        Returns:
            MetricResult with transition density verdict
        """
        text_lower = text.lower()

        # Count transition phrases (weighted by length)
        transition_score = 0
        matches_found = {}

        for phrase, weight in self.transition_phrases.items():
            count = text_lower.count(phrase)
            if count > 0:
                transition_score += count * weight
                matches_found[phrase] = count

        # Calculate density
        density = transition_score / max(1, word_count)

        # Normalize to 0-1
        normalized_score = self._normalize_density(density)

        # Determine verdict
        if density < 0.015:
            verdict = Verdict.HUMAN
        elif density > 0.060:
            verdict = Verdict.AI
        else:
            verdict = Verdict.MIXED

        return MetricResult(
            score=normalized_score,
            human_range="0.5-2.0%",
            ai_range="4.0-8.0%",
            verdict=verdict,
            reasoning=f"Transition density: {density*100:.2f}%. " +
                     ("Sparse connector usage typical of natural writing" if density < 0.020
                      else "Excessive formulaic transitions characteristic of AI" if density > 0.060
                      else "Moderate transition frequency"),
            supporting_data={
                "density_percentage": round(density * 100, 2),
                "transition_weighted_score": transition_score,
                "phrase_count": len(matches_found),
                "top_phrases": sorted(matches_found.items(), key=lambda x: x[1], reverse=True)[:5]
            }
        )

    def _normalize_density(self, density: float) -> float:
        """Normalize density to 0-1 scale (0=human, 1=AI)"""
        # High density (AI) = high score
        if density > 0.08:
            return 1.0
        elif density < 0.005:
            return 0.0
        else:
            return (density - 0.005) / 0.075


class RepetitionMetric:
    """
    Repetition Score: Detects n-gram repetition patterns

    Algorithm:
    1. Extract bigrams, trigrams, 4-grams
    2. Calculate repetition frequency at each level
    3. Score = (repeated_bigrams + repeated_trigrams + repeated_4grams) / total_ngrams
    4. Humans repeat less, AI repeats more (especially 3-4 word phrases)
    5. Normalize: human_range 0.05-0.15, AI_range 0.25-0.45
    """

    def __init__(self):
        self.human_range = (0.05, 0.15)
        self.ai_range = (0.25, 0.45)

    def analyze(self, tokens: List[str]) -> MetricResult:
        """
        Analyze n-gram repetition patterns

        Args:
            tokens: Pre-tokenized words

        Returns:
            MetricResult with repetition verdict
        """
        if len(tokens) < 6:
            return MetricResult(
                score=0.5,
                human_range="5-15%",
                ai_range="25-45%",
                verdict=Verdict.MIXED,
                reasoning="Insufficient tokens for n-gram analysis",
                supporting_data={"token_count": len(tokens)}
            )

        # Extract n-grams at different levels
        bigrams = self._extract_ngrams(tokens, 2)
        trigrams = self._extract_ngrams(tokens, 3)
        fourgrams = self._extract_ngrams(tokens, 4)

        # Calculate repetition at each level
        bigram_rep = self._calculate_repetition(bigrams)
        trigram_rep = self._calculate_repetition(trigrams)
        fourgram_rep = self._calculate_repetition(fourgrams)

        # Weighted score (4-grams weighted more heavily as they're more significant)
        combined_rep = (bigram_rep * 0.2) + (trigram_rep * 0.3) + (fourgram_rep * 0.5)

        # Determine verdict
        if combined_rep < 0.15:
            verdict = Verdict.HUMAN
        elif combined_rep > 0.40:
            verdict = Verdict.AI
        else:
            verdict = Verdict.MIXED

        return MetricResult(
            score=combined_rep,
            human_range="5-15%",
            ai_range="25-45%",
            verdict=verdict,
            reasoning=f"N-gram repetition: {combined_rep*100:.1f}%. " +
                     ("Natural phrase variation" if combined_rep < 0.20
                      else "Excessive repetition of word sequences (AI-like)" if combined_rep > 0.35
                      else "Moderate phrase repetition"),
            supporting_data={
                "repetition_percentage": round(combined_rep * 100, 1),
                "bigram_rep": round(bigram_rep, 3),
                "trigram_rep": round(trigram_rep, 3),
                "fourgram_rep": round(fourgram_rep, 3),
                "total_bigrams": len(bigrams),
                "total_trigrams": len(trigrams),
                "total_fourgrams": len(fourgrams)
            }
        )

    def _extract_ngrams(self, tokens: List[str], n: int) -> Counter:
        """Extract n-grams from token list"""
        ngrams = [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
        return Counter(ngrams)

    def _calculate_repetition(self, ngram_counter: Counter) -> float:
        """Calculate percentage of repeated n-grams"""
        if not ngram_counter:
            return 0.0

        total_ngrams = sum(ngram_counter.values())
        repeated_ngrams = sum(count for count in ngram_counter.values() if count > 1)

        return repeated_ngrams / total_ngrams if total_ngrams > 0 else 0.0


class SyntaxMetric:
    """
    Sentence Structure Uniformity: Detects AI-like syntactic patterns

    Algorithm:
    1. POS-tag each sentence
    2. Extract POS pattern (sequence of tags) for each sentence
    3. Calculate entropy of POS pattern distribution
    4. Low entropy = uniform patterns (AI), high entropy = varied (human)
    5. Also detect common AI patterns:
       - Subject-Verb-Object rigidity
       - Consistent clause ordering
       - Formulaic openings (e.g., "The X is Y" pattern)
    6. Normalize: human_range 3.5-5.0, AI_range 1.5-3.0 (entropy)
    """

    def __init__(self):
        self.human_entropy_range = (3.5, 5.0)
        self.ai_entropy_range = (1.5, 3.0)

        # Common AI opening patterns
        self.ai_patterns = [
            r'^(the|this|in|to|understanding|exploring|examining)',  # Formulaic starts
            r'(have\s+been|has\s+been)',  # Passive voice preference
            r'(it\s+is\s+important|it\s+is\s+notable)',  # Formulaic phrases
        ]

    def analyze(self, sentences: List[str]) -> MetricResult:
        """
        Analyze syntactic uniformity

        Args:
            sentences: Pre-tokenized sentences

        Returns:
            MetricResult with syntax verdict
        """
        if len(sentences) < 3:
            return MetricResult(
                score=0.5,
                human_range="3.5-5.0",
                ai_range="1.5-3.0",
                verdict=Verdict.MIXED,
                reasoning="Insufficient sentences for syntax analysis",
                supporting_data={"sentence_count": len(sentences)}
            )

        # Extract POS patterns
        pos_patterns = []
        for sent in sentences:
            tokens = word_tokenize(sent)
            tags = pos_tag(tokens)
            pattern = ' '.join([tag for word, tag in tags])
            pos_patterns.append(pattern)

        # Calculate entropy of patterns
        pattern_freq = Counter(pos_patterns)
        entropy = self._calculate_entropy(pattern_freq)

        # Detect formulaic patterns
        formulaic_count = self._detect_formulaic_patterns(sentences)

        # Normalize entropy to 0-1 (high entropy = human, low entropy = AI)
        normalized_score = self._normalize_entropy(entropy)

        # Determine verdict
        if entropy > 4.0 and formulaic_count < 2:
            verdict = Verdict.HUMAN
        elif entropy < 2.5 or formulaic_count > 5:
            verdict = Verdict.AI
        else:
            verdict = Verdict.MIXED

        return MetricResult(
            score=normalized_score,
            human_range="3.5-5.0",
            ai_range="1.5-3.0",
            verdict=verdict,
            reasoning=f"Syntax entropy: {entropy:.2f}, Formulaic patterns: {formulaic_count}. " +
                     ("Diverse sentence structures" if entropy > 4.0
                      else "Repetitive syntactic patterns (AI-like)" if entropy < 2.5
                      else "Moderate syntactic variation"),
            supporting_data={
                "entropy": round(entropy, 3),
                "unique_patterns": len(pattern_freq),
                "most_common_pattern": pattern_freq.most_common(1)[0] if pattern_freq else None,
                "formulaic_pattern_count": formulaic_count,
                "pattern_diversity": len(pattern_freq) / len(sentences) if sentences else 0
            }
        )

    def _calculate_entropy(self, freq_counter: Counter) -> float:
        """Calculate Shannon entropy of pattern distribution"""
        total = sum(freq_counter.values())
        entropy = 0.0

        for count in freq_counter.values():
            if count > 0:
                prob = count / total
                entropy -= prob * math.log2(prob)

        return entropy

    def _detect_formulaic_patterns(self, sentences: List[str]) -> int:
        """Count sentences matching AI-formulaic patterns"""
        count = 0
        for sent in sentences:
            sent_lower = sent.lower()
            for pattern in self.ai_patterns:
                if re.search(pattern, sent_lower):
                    count += 1
                    break
        return count

    def _normalize_entropy(self, entropy: float) -> float:
        """Normalize entropy to 0-1 scale (0=AI, 1=human)"""
        if entropy > 5.0:
            return 1.0
        elif entropy < 1.5:
            return 0.0
        else:
            return (entropy - 1.5) / 3.5


class RemediationEngine:
    """
    Generates specific remediation advice for detected issues

    Maps detected AI tells to actionable fixes:
    - Low perplexity → add more specific examples, unexpected angles
    - Uniform sentences → vary opening structures, mix lengths
    - Low vocabulary → replace repeated terms, use synonyms
    - High transitions → remove formulaic connectors
    - High repetition → refactor repeated phrases
    - Uniform syntax → restructure sentences, vary clause order
    """

    def __init__(self):
        self.remediation_map = {
            "low_perplexity": {
                "severity": "high",
                "suggestion": "Add specific examples, personal anecdotes, or unexpected insights",
                "tactics": [
                    "Include concrete case studies or real-world examples",
                    "Add counter-intuitive arguments or surprising angles",
                    "Reference personal experience or unique perspective",
                    "Include specific data points or quotes"
                ]
            },
            "uniform_sentence_length": {
                "severity": "medium",
                "suggestion": "Vary sentence structure and length for natural rhythm",
                "tactics": [
                    "Use some very short sentences (3-5 words) for impact",
                    "Mix complex sentences with simple ones",
                    "Vary sentence starters (avoid beginning with 'The', 'In', 'It')",
                    "Use fragment sentences occasionally for effect"
                ]
            },
            "low_vocabulary": {
                "severity": "medium",
                "suggestion": "Expand vocabulary to show sophistication and reduce repetition",
                "tactics": [
                    "Replace repeated words with synonyms",
                    "Use more specific, precise terminology",
                    "Incorporate discipline-specific jargon appropriately",
                    "Use less common words to demonstrate vocabulary range"
                ]
            },
            "high_transitions": {
                "severity": "medium",
                "suggestion": "Reduce formulaic transition phrases",
                "tactics": [
                    "Remove 'Moreover', 'Furthermore', 'Additionally' (already clear from context)",
                    "Use structural transitions instead of phrases (new paragraph implies continuation)",
                    "Vary connector types - use questions or statements instead",
                    "Let ideas speak for themselves with fewer connectors"
                ]
            },
            "high_repetition": {
                "severity": "high",
                "suggestion": "Refactor repeated phrases and word sequences",
                "tactics": [
                    "Replace repeated 3+ word phrases with paraphrases",
                    "Use pronouns instead of repeating full terms",
                    "Restructure sentences to vary word order",
                    "Use synonyms for frequently repeated words"
                ]
            },
            "uniform_syntax": {
                "severity": "medium",
                "suggestion": "Diversify sentence structure and clause ordering",
                "tactics": [
                    "Mix active and passive voice naturally",
                    "Vary clause position (main clause first vs. subordinate first)",
                    "Use different sentence openers (not just SVO pattern)",
                    "Include rhetorical questions, lists, or emphasis structures"
                ]
            }
        }

    def generate_fixes(self, issues: List[IssueFlag], metrics: Dict[str, MetricResult]) -> Tuple[List[str], List[Dict]]:
        """
        Generate remediation suggestions ordered by priority

        Args:
            issues: Detected specific issues
            metrics: All metric results

        Returns:
            Tuple of (priority list, detailed fixes)
        """
        fixes = []
        priority = []

        # Process metric-level issues
        for metric_name, result in metrics.items():
            if result.verdict == Verdict.AI:
                issue_type = self._metric_to_issue_type(metric_name)

                if issue_type in self.remediation_map:
                    remediation = self.remediation_map[issue_type]
                    fixes.append({
                        "metric": metric_name,
                        "severity": remediation["severity"],
                        "suggestion": remediation["suggestion"],
                        "tactics": remediation["tactics"],
                        "evidence": result.supporting_data
                    })

                    # Add to priority if high severity
                    if remediation["severity"] == "high":
                        priority.append(f"{issue_type} ({metric_name})")

        # Process specific line issues
        for issue in issues:
            priority.append(f"{issue.issue_type} (line {issue.line_number})")

        return priority, fixes

    def _metric_to_issue_type(self, metric_name: str) -> str:
        """Convert metric name to remediation issue type"""
        mapping = {
            "perplexity": "low_perplexity",
            "burstiness": "uniform_sentence_length",
            "vocabulary": "low_vocabulary",
            "transitions": "high_transitions",
            "repetition": "high_repetition",
            "syntax": "uniform_syntax"
        }
        return mapping.get(metric_name, "unknown")


class TextAnalyzer:
    """
    Main IF.detector orchestrator

    Coordinates all metric analyses and generates comprehensive detection report

    Architecture:
        TextAnalyzer
        ├── PerplexityMetric
        ├── BurstinessMetric
        ├── VocabularyMetric
        ├── TransitionMetric
        ├── RepetitionMetric
        ├── SyntaxMetric
        └── RemediationEngine
    """

    def __init__(self):
        self.perplexity = PerplexityMetric()
        self.burstiness = BurstinessMetric()
        self.vocabulary = VocabularyMetric()
        self.transitions = TransitionMetric()
        self.repetition = RepetitionMetric()
        self.syntax = SyntaxMetric()
        self.remediation = RemediationEngine()

        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)

        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger', quiet=True)

    def analyze(self, text: str) -> DetectionResult:
        """
        Comprehensive AI detection analysis

        Args:
            text: Input text to analyze

        Returns:
            DetectionResult with complete analysis
        """
        from datetime import datetime

        # Preprocessing
        sentences = sent_tokenize(text)
        tokens = word_tokenize(text)

        # Calculate statistics
        word_count = len([t for t in tokens if t.isalpha()])
        sentence_count = len(sentences)
        token_count = len(tokens)

        # Run all metrics
        metrics = {
            "perplexity": self.perplexity.analyze(text, tokens),
            "burstiness": self.burstiness.analyze(sentences),
            "vocabulary": self.vocabulary.analyze(tokens),
            "transitions": self.transitions.analyze(text, word_count),
            "repetition": self.repetition.analyze(tokens),
            "syntax": self.syntax.analyze(sentences)
        }

        # Calculate overall probability
        overall_ai_prob = self._calculate_overall_probability(metrics)

        # Determine confidence level
        confidence = self._determine_confidence(metrics, overall_ai_prob)

        # Determine overall verdict
        verdict = self._determine_verdict(overall_ai_prob)

        # Detect specific issues in text
        specific_issues = self._detect_specific_issues(text, sentences, tokens, metrics)

        # Generate remediation advice
        remediation_priority, _ = self.remediation.generate_fixes(specific_issues, metrics)

        return DetectionResult(
            overall_ai_probability=overall_ai_prob,
            confidence=confidence,
            verdict=verdict,
            metrics=metrics,
            specific_issues=specific_issues,
            remediation_priority=remediation_priority,
            token_count=token_count,
            sentence_count=sentence_count,
            word_count=word_count,
            analysis_timestamp=datetime.now().isoformat()
        )

    def _calculate_overall_probability(self, metrics: Dict[str, MetricResult]) -> float:
        """
        Weighted average of all metrics

        Formula: weighted_avg of metric scores
        """
        weights = {
            "perplexity": 0.25,      # Most significant
            "repetition": 0.20,       # Unique to AI
            "vocabulary": 0.20,       # Clear indicator
            "transitions": 0.15,      # Formulaic patterns
            "syntax": 0.12,           # Structure patterns
            "burstiness": 0.08        # Less reliable alone
        }

        total_weight = 0
        weighted_sum = 0

        for metric_name, weight in weights.items():
            if metric_name in metrics:
                weighted_sum += metrics[metric_name].score * weight
                total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.5

    def _determine_confidence(self, metrics: Dict[str, MetricResult], overall_prob: float) -> ConfidenceLevel:
        """
        Determine confidence based on metric agreement

        High confidence: metrics agree (all AI or all human)
        Low confidence: metric disagreement
        """
        ai_count = sum(1 for m in metrics.values() if m.verdict == Verdict.AI)
        human_count = sum(1 for m in metrics.values() if m.verdict == Verdict.HUMAN)
        total = len(metrics)

        # Strong agreement on AI
        if ai_count >= total * 0.7:
            return ConfidenceLevel.HIGH

        # Strong agreement on human
        elif human_count >= total * 0.7:
            return ConfidenceLevel.HIGH

        # Moderate agreement
        elif max(ai_count, human_count) >= total * 0.5:
            return ConfidenceLevel.MEDIUM

        # Weak agreement
        else:
            return ConfidenceLevel.LOW

    def _determine_verdict(self, overall_prob: float) -> Verdict:
        """Determine final verdict from probability"""
        if overall_prob > 0.65:
            return Verdict.AI
        elif overall_prob < 0.35:
            return Verdict.HUMAN
        else:
            return Verdict.MIXED

    def _detect_specific_issues(self, text: str, sentences: List[str],
                                tokens: List[str], metrics: Dict[str, MetricResult]) -> List[IssueFlag]:
        """
        Detect specific problem areas in text

        Algorithm:
        1. Scan for formulaic phrases and patterns
        2. Identify unusually uniform sentences
        3. Find highly repetitive sections
        4. Detect passive voice clustering
        """
        issues = []

        # Formulaic phrase detection
        formulaic_phrases = {
            "it is important to note": "formulaic_opening",
            "in order to": "verbosity",
            "as mentioned above": "backref",
            "in conclusion": "formulaic_closing",
            "to summarize": "formulaic_closing"
        }

        text_lower = text.lower()
        for phrase, issue_type in formulaic_phrases.items():
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            for match in pattern.finditer(text):
                start_char = match.start()
                line_num = text[:start_char].count('\n') + 1
                line_start = text.rfind('\n', 0, start_char) + 1
                line_end = text.find('\n', start_char)
                if line_end == -1:
                    line_end = len(text)
                line_text = text[line_start:line_end]

                issues.append(IssueFlag(
                    line_number=line_num,
                    line_text=line_text,
                    issue_type=issue_type,
                    description=f"Formulaic phrase detected: '{phrase}'",
                    suggestion=f"Replace or remove '{phrase}' with more natural language",
                    severity="medium",
                    evidence={"phrase": phrase, "position": match.start()}
                ))

        # Detect passive voice clustering
        passive_pattern = r'\b\w+\s+(?:is|are|was|were|be|been)\s+\w+ed\b'
        passive_count = 0
        for i, sent in enumerate(sentences):
            if re.search(passive_pattern, sent):
                passive_count += 1
                if passive_count >= 3:  # More than 3 consecutive passive sentences
                    issues.append(IssueFlag(
                        line_number=i + 1,
                        line_text=sent[:100],
                        issue_type="passive_voice_clustering",
                        description="Multiple consecutive sentences in passive voice",
                        suggestion="Rewrite some sentences in active voice for clarity and engagement",
                        severity="medium",
                        evidence={"passive_sentences": passive_count}
                    ))
                    passive_count = 0

        return issues


# Example usage and testing
if __name__ == "__main__":
    # Test with sample text
    human_sample = """
    I've been thinking about this problem for weeks, and honestly, it's more complex than
    it first appeared. You see, there are several factors at play - some technical, some
    more philosophical. Last Tuesday, I ran into an old colleague who actually faced a
    similar issue in his startup. Anyway, what I realized is that sometimes the simplest
    solutions come from the most unexpected places. It's funny how life works that way.
    """

    ai_sample = """
    The implications of this phenomenon are significant and multifaceted. Furthermore,
    it is important to note that the underlying mechanisms have been subject to extensive
    scholarly analysis. Additionally, the data suggests that multiple variables contribute
    to the observed outcomes. In conclusion, the evidence clearly indicates that a more
    nuanced approach is required. Moreover, as mentioned above, the theoretical framework
    must be revised to accommodate these findings.
    """

    analyzer = TextAnalyzer()

    print("=" * 80)
    print("HUMAN-WRITTEN TEXT ANALYSIS")
    print("=" * 80)
    result_human = analyzer.analyze(human_sample)
    print(result_human.to_json())

    print("\n" + "=" * 80)
    print("AI-GENERATED TEXT ANALYSIS")
    print("=" * 80)
    result_ai = analyzer.analyze(ai_sample)
    print(result_ai.to_json())
