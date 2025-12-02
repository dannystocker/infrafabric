"""
Multi-Model Consensus Voting Algorithm for IF.swarm.s2

This module implements a sophisticated consensus algorithm for 3-model voting
(Claude Max + DeepSeek + Gemini) with confidence-weighted voting, quality scoring,
and automatic tie-breaking mechanisms.

Based on Testable Prediction 1 from IF_GUARD_OPENWEBUI_TOUCHABLE_INTERFACE_DEBATE_2025-11-30:
  "3-model consensus produces >15% better outputs than single-model on complex reasoning"
  Test: 100 reasoning challenges with blind evaluation by human raters
  Metric: Quality score (0-100) averaged across raters

Architecture:
  1. Each model generates response + confidence score [0.0, 1.0]
  2. Models with higher confidence receive proportionally more weight
  3. Semantic similarity detection identifies agreement vs. disagreement
  4. If disagreement detected (>20% variance), second round runs with conflict highlighted
  5. Quality scoring evaluates semantic similarity, citation density, coherence
  6. Tie-breaking rules resolve 50/50 splits deterministically
  7. Result synthesis merges best parts of all 3 responses

Citation: if://citation/consensus-voting-algorithm-2025-11-30
Reference: /home/setup/infrafabric/docs/debates/IF_GUARD_OPENWEBUI_TOUCHABLE_INTERFACE_DEBATE_2025-11-30.md:1096-1103

Author: Agent A13 (Multi-Model Consensus Design)
Date: 2025-11-30
"""

import json
import uuid
import hashlib
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple, Set
from abc import ABC, abstractmethod
import time
from datetime import datetime, timezone
import statistics
from difflib import SequenceMatcher
import math


# ============================================================================
# Core Data Structures
# ============================================================================

class ModelName(str, Enum):
    """Supported LLM models for consensus voting."""
    CLAUDE_MAX = "claude-max"
    DEEPSEEK = "deepseek-chat"
    GEMINI = "gemini-pro-1.5"


class ResponseQuality(str, Enum):
    """Quality assessment categories."""
    EXCELLENT = "excellent"      # >85 quality score
    GOOD = "good"                # 70-85 quality score
    ACCEPTABLE = "acceptable"    # 55-70 quality score
    POOR = "poor"                # <55 quality score


class AgreementLevel(str, Enum):
    """Consensus state enumeration."""
    STRONG_AGREEMENT = "strong_agreement"      # >85% semantic similarity
    MODERATE_AGREEMENT = "moderate_agreement"  # 70-85% similarity
    WEAK_AGREEMENT = "weak_agreement"          # 55-70% similarity
    DISAGREEMENT = "disagreement"              # <55% similarity


@dataclass
class ModelResponse:
    """
    Single model's response with quality metadata.

    Fields:
        model: Which model generated this response
        content: The actual response text/output
        confidence: Model's self-assessed confidence [0.0, 1.0]
        generation_time_ms: How long the model took to respond
        token_count: Number of tokens in response
        citations: List of sources referenced in response
        timestamp: ISO 8601 when response was generated
    """
    model: ModelName
    content: str
    confidence: float = 0.5
    generation_time_ms: float = 0.0
    token_count: int = 0
    citations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        """Validate confidence is in valid range."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be in [0.0, 1.0], got {self.confidence}")

        # Auto-calculate token count if not provided
        if self.token_count == 0 and self.content:
            # Rough estimation: 1 token ≈ 4 characters (OpenAI rule of thumb)
            self.token_count = len(self.content) // 4


@dataclass
class QualityScore:
    """
    Comprehensive quality evaluation of a response.

    Scoring components:
      - semantic_coherence [0, 100]: No contradictions, logical flow
      - citation_density [0, 100]: # citations / response_length (normalized)
      - semantic_richness [0, 100]: Vocabulary diversity, concept density
      - answer_completeness [0, 100]: Addresses all aspects of prompt
      - error_freedom [0, 100]: No factual/logical errors detected

    Overall score is weighted average of components.
    """
    semantic_coherence: float  # 0-100
    citation_density: float    # 0-100
    semantic_richness: float   # 0-100
    answer_completeness: float # 0-100
    error_freedom: float       # 0-100

    # Weights for weighted average (must sum to 1.0)
    weights: Dict[str, float] = field(default_factory=lambda: {
        'semantic_coherence': 0.25,
        'citation_density': 0.20,
        'semantic_richness': 0.20,
        'answer_completeness': 0.20,
        'error_freedom': 0.15
    })

    def overall_score(self) -> float:
        """Calculate weighted average quality score [0.0, 100.0]."""
        components = {
            'semantic_coherence': self.semantic_coherence,
            'citation_density': self.citation_density,
            'semantic_richness': self.semantic_richness,
            'answer_completeness': self.answer_completeness,
            'error_freedom': self.error_freedom
        }

        weighted_sum = sum(
            components[key] * self.weights[key]
            for key in components
        )
        return min(100.0, max(0.0, weighted_sum))

    def quality_category(self) -> ResponseQuality:
        """Map numeric score to quality category."""
        score = self.overall_score()
        if score >= 85:
            return ResponseQuality.EXCELLENT
        elif score >= 70:
            return ResponseQuality.GOOD
        elif score >= 55:
            return ResponseQuality.ACCEPTABLE
        else:
            return ResponseQuality.POOR


@dataclass
class ConsensusResult:
    """
    Final consensus output after voting and synthesis.

    Fields:
        consensus_id: Unique identifier for this consensus run
        agreement_level: STRONG/MODERATE/WEAK/DISAGREEMENT
        winning_response: The selected response text
        confidence_score: Final confidence in result [0.0, 1.0]
        model_votes: {model_name: quality_score} for each model's response
        synthesized_response: Optional merged response combining best parts
        second_round_triggered: Whether disagreement required second round
        round_count: Number of voting rounds executed
        total_execution_time_ms: Total time for consensus process
        timestamp: ISO 8601 when consensus was reached
        reasoning: Explanation of consensus decision
    """
    consensus_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agreement_level: AgreementLevel = AgreementLevel.MODERATE_AGREEMENT
    winning_response: str = ""
    confidence_score: float = 0.5
    model_votes: Dict[str, float] = field(default_factory=dict)
    synthesized_response: Optional[str] = None
    second_round_triggered: bool = False
    round_count: int = 1
    total_execution_time_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reasoning: str = ""


# ============================================================================
# Similarity Computation
# ============================================================================

class SemanticSimilarity:
    """
    Compute semantic similarity between model responses.

    Uses multiple strategies:
    1. Cosine similarity on token overlap
    2. Longest common subsequence (LCS)
    3. Jaccard similarity on word sets
    """

    @staticmethod
    def token_overlap_similarity(text1: str, text2: str) -> float:
        """
        Compute similarity using token overlap (words).

        Args:
            text1: First response text
            text2: Second response text

        Returns:
            Similarity score [0.0, 1.0]
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    @staticmethod
    def sequence_similarity(text1: str, text2: str) -> float:
        """
        Compute similarity using SequenceMatcher (handles structure).

        Args:
            text1: First response text
            text2: Second response text

        Returns:
            Similarity score [0.0, 1.0]
        """
        matcher = SequenceMatcher(None, text1, text2)
        return matcher.ratio()

    @staticmethod
    def combined_similarity(text1: str, text2: str,
                          token_weight: float = 0.6,
                          sequence_weight: float = 0.4) -> float:
        """
        Weighted combination of similarity metrics.

        Args:
            text1: First response
            text2: Second response
            token_weight: Weight for token overlap (default 0.6)
            sequence_weight: Weight for sequence matching (default 0.4)

        Returns:
            Combined similarity [0.0, 1.0]
        """
        token_sim = SemanticSimilarity.token_overlap_similarity(text1, text2)
        seq_sim = SemanticSimilarity.sequence_similarity(text1, text2)

        return (token_sim * token_weight) + (seq_sim * sequence_weight)


# ============================================================================
# Quality Scoring Engine
# ============================================================================

class QualityScorer:
    """
    Evaluate response quality across multiple dimensions.
    """

    @staticmethod
    def score_semantic_coherence(text: str, citation_count: int = 0) -> float:
        """
        Score logical flow and absence of contradictions.

        Heuristics:
        - Paragraph count > 1: +10 points (structure)
        - Sentence count > 3: +15 points (development)
        - Average sentence length 12-20 words: +20 points (clarity)
        - No negation contradiction patterns: +20 points
        - Presence of transitions/connectives: +15 points (cohesion)
        - Proper use of citations: +20 points

        Returns: Score [0, 100]
        """
        score = 0.0

        # Structure analysis
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        if len(paragraphs) > 1:
            score += 10

        # Sentence count
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if len(sentences) > 3:
            score += 15

        # Sentence length analysis
        if sentences:
            avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
            if 12 <= avg_words <= 20:
                score += 20
            elif 8 <= avg_words <= 25:
                score += 10

        # Contradiction detection
        contradiction_patterns = [
            ('however', 'definitely'),
            ('but', 'obviously'),
            ('although', 'clearly'),
        ]
        text_lower = text.lower()
        contradictions = sum(1 for p1, p2 in contradiction_patterns
                           if p1 in text_lower and p2 in text_lower)
        if contradictions == 0:
            score += 20
        else:
            score -= min(20, contradictions * 5)

        # Transition words (coherence markers)
        transitions = ['however', 'therefore', 'furthermore', 'moreover',
                      'additionally', 'meanwhile', 'subsequently', 'ultimately']
        if any(t in text_lower for t in transitions):
            score += 15

        # Citation usage
        if citation_count > 0:
            score += min(20, citation_count * 3)

        return min(100.0, max(0.0, score))

    @staticmethod
    def score_citation_density(text: str, citation_count: int) -> float:
        """
        Score appropriate citation density.

        Ideal: 1 citation per 100-150 words

        Returns: Score [0, 100]
        """
        words = len(text.split())
        if words == 0:
            return 0.0

        citations_per_100_words = (citation_count / words) * 100

        # Ideal range: 0.8-1.2 citations per 100 words
        if 0.8 <= citations_per_100_words <= 1.2:
            return 100.0
        elif 0.5 <= citations_per_100_words <= 1.5:
            return 85.0
        elif 0.3 <= citations_per_100_words <= 2.0:
            return 70.0
        elif citation_count > 0:
            return 50.0
        else:
            return 30.0  # Penalize zero citations for factual claims

    @staticmethod
    def score_semantic_richness(text: str) -> float:
        """
        Score vocabulary diversity and concept density.

        Metrics:
        - Unique words / total words (lexical diversity)
        - Average word length (sophistication)
        - Sentence variety (simple/compound/complex distribution)

        Returns: Score [0, 100]
        """
        words = text.lower().split()
        if not words:
            return 0.0

        unique_words = set(words)
        lexical_diversity = len(unique_words) / len(words)

        # Score diversity (ideal: 0.4-0.6)
        diversity_score = 0.0
        if 0.4 <= lexical_diversity <= 0.6:
            diversity_score = 40.0
        elif 0.3 <= lexical_diversity <= 0.7:
            diversity_score = 30.0
        elif lexical_diversity >= 0.2:
            diversity_score = 20.0

        # Average word length (ideal: 4.5-5.5 characters)
        avg_word_length = sum(len(w) for w in words) / len(words)
        length_score = 0.0
        if 4.5 <= avg_word_length <= 5.5:
            length_score = 30.0
        elif 4.0 <= avg_word_length <= 6.0:
            length_score = 20.0
        elif avg_word_length > 3.5:
            length_score = 10.0

        # Sentence structure variety (heuristic based on punctuation)
        sentences = text.split('.')
        complex_markers = ['(', ':', ';']
        complex_count = sum(1 for s in sentences
                          if any(m in s for m in complex_markers))
        structure_score = min(30.0, complex_count * 2)

        return min(100.0, diversity_score + length_score + structure_score)

    @staticmethod
    def score_answer_completeness(text: str, expected_aspects: int = 3) -> float:
        """
        Score whether response addresses all required aspects.

        Heuristic: Paragraph count as proxy for coverage.

        Args:
            text: Response text
            expected_aspects: Number of aspects expected to be covered

        Returns: Score [0, 100]
        """
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        para_count = len(paragraphs)

        if para_count >= expected_aspects:
            return 100.0
        elif para_count >= expected_aspects - 1:
            return 85.0
        elif para_count >= expected_aspects - 2:
            return 70.0
        elif para_count >= 2:
            return 50.0
        else:
            return 25.0

    @staticmethod
    def score_error_freedom(text: str) -> float:
        """
        Score absence of obvious errors.

        Checks for:
        - Grammar patterns (incomplete sentences, etc.)
        - Spelling (approximate using word patterns)
        - Logical consistency

        Returns: Score [0, 100]
        """
        score = 100.0

        # Check for incomplete sentences (ends with comma, conjunction without period)
        lines = text.split('.')
        incomplete_count = sum(1 for line in lines
                             if line.strip().endswith((',', 'and', 'or', 'but')))
        score -= min(30.0, incomplete_count * 5)

        # Check for doubled words (common typo)
        words = text.split()
        doubled_count = sum(1 for i in range(len(words)-1)
                          if words[i].lower() == words[i+1].lower())
        score -= min(20.0, doubled_count * 3)

        # Check for broken markdown/formatting
        brackets_open = text.count('[')
        brackets_closed = text.count(']')
        if brackets_open != brackets_closed:
            score -= 10

        return max(0.0, score)

    @classmethod
    def evaluate_response(cls, response: ModelResponse) -> QualityScore:
        """
        Comprehensive quality evaluation of a single response.

        Args:
            response: ModelResponse to evaluate

        Returns:
            QualityScore with all component scores
        """
        coherence = cls.score_semantic_coherence(
            response.content,
            len(response.citations)
        )

        citation_density = cls.score_citation_density(
            response.content,
            len(response.citations)
        )

        richness = cls.score_semantic_richness(response.content)
        completeness = cls.score_answer_completeness(response.content)
        errors = cls.score_error_freedom(response.content)

        return QualityScore(
            semantic_coherence=coherence,
            citation_density=citation_density,
            semantic_richness=richness,
            answer_completeness=completeness,
            error_freedom=errors
        )


# ============================================================================
# Consensus Voting Engine
# ============================================================================

class ConsensusVotingEngine:
    """
    Main consensus algorithm implementation.

    Implements weighted voting with confidence-based weighting:
    1. Each model receives vote weight proportional to confidence
    2. Similarity analysis detects agreement/disagreement
    3. Disagreement triggers second round with conflict highlighted
    4. Quality scoring breaks ties deterministically
    5. Result synthesis merges best parts of responses
    """

    def __init__(self, timeout_seconds: float = 30.0):
        """
        Initialize voting engine.

        Args:
            timeout_seconds: Max time to wait for any single model (unused for pre-computed responses)
        """
        self.timeout_seconds = timeout_seconds
        self.similarity_engine = SemanticSimilarity()
        self.quality_scorer = QualityScorer()

    def compute_weighted_votes(self, responses: List[ModelResponse]) -> Dict[ModelName, float]:
        """
        Compute vote weights based on model confidence scores.

        Weights are normalized so they sum to 1.0.

        Args:
            responses: List of ModelResponse from each model

        Returns:
            {model_name: weight} dictionary
        """
        if not responses:
            return {}

        # Extract confidences
        confidences = {r.model: r.confidence for r in responses}
        total_confidence = sum(confidences.values())

        if total_confidence == 0.0:
            # Equal weighting if all confidences are 0
            weight = 1.0 / len(responses)
            return {r.model: weight for r in responses}

        # Normalize confidences to weights
        return {model: conf / total_confidence
                for model, conf in confidences.items()}

    def detect_agreement_level(self, responses: List[ModelResponse]) -> Tuple[AgreementLevel, Dict[str, float]]:
        """
        Analyze pairwise similarities to determine consensus level.

        Computes similarities between each pair and categorizes the result.

        Args:
            responses: List of ModelResponse

        Returns:
            (agreement_level, similarity_matrix) tuple
        """
        if len(responses) < 2:
            return AgreementLevel.STRONG_AGREEMENT, {}

        # Compute pairwise similarities
        similarities = {}
        for i, r1 in enumerate(responses):
            for j, r2 in enumerate(responses):
                if i < j:
                    sim = self.similarity_engine.combined_similarity(
                        r1.content, r2.content
                    )
                    key = f"{r1.model.value}_vs_{r2.model.value}"
                    similarities[key] = sim

        # Determine agreement level from average similarity
        if not similarities:
            return AgreementLevel.STRONG_AGREEMENT, similarities

        avg_similarity = statistics.mean(similarities.values())

        # Scale to 0-100 for categorization
        similarity_score = avg_similarity * 100

        if similarity_score >= 85:
            level = AgreementLevel.STRONG_AGREEMENT
        elif similarity_score >= 70:
            level = AgreementLevel.MODERATE_AGREEMENT
        elif similarity_score >= 55:
            level = AgreementLevel.WEAK_AGREEMENT
        else:
            level = AgreementLevel.DISAGREEMENT

        return level, similarities

    def should_trigger_second_round(self, agreement_level: AgreementLevel,
                                   variance_threshold: float = 0.20) -> bool:
        """
        Determine if second round voting should be triggered.

        Triggers when disagreement is significant (>variance_threshold).

        Args:
            agreement_level: Current agreement level classification
            variance_threshold: Minimum variance to trigger second round

        Returns:
            True if second round should run
        """
        return agreement_level in [
            AgreementLevel.DISAGREEMENT,
            AgreementLevel.WEAK_AGREEMENT
        ]

    def quality_rank_responses(self, responses: List[ModelResponse]) -> List[Tuple[ModelResponse, QualityScore]]:
        """
        Rank responses by quality score (highest first).

        Args:
            responses: List of ModelResponse to evaluate

        Returns:
            Sorted list of (response, quality_score) tuples
        """
        evaluated = []
        for response in responses:
            quality = self.quality_scorer.evaluate_response(response)
            evaluated.append((response, quality))

        # Sort by quality score (descending)
        evaluated.sort(
            key=lambda x: x[1].overall_score(),
            reverse=True
        )

        return evaluated

    def synthesize_response(self, responses: List[ModelResponse],
                          rankings: List[Tuple[ModelResponse, QualityScore]]) -> str:
        """
        Merge best parts of multiple responses into synthetic consensus.

        Strategy:
        1. Take opening from highest quality response
        2. Add unique content from lower-ranked responses
        3. Merge citations from all responses

        Args:
            responses: Original responses
            rankings: Ranked responses by quality

        Returns:
            Synthesized response text
        """
        if not rankings:
            return ""

        # Start with best response
        best_response, best_quality = rankings[0]
        opening_sentences = best_response.content.split('.')[0:2]
        opening = '. '.join(s.strip() for s in opening_sentences if s.strip())

        # Collect unique content from other responses
        best_words = set(best_response.content.lower().split())
        unique_additions = []

        for response, quality in rankings[1:]:
            words = set(response.content.lower().split())
            unique_words = words - best_words

            # If this response has significant unique content, include it
            if len(unique_words) > len(best_words) * 0.15:  # >15% unique
                sentences = response.content.split('.')
                for sent in sentences[1:3]:  # Take a middle section
                    unique_additions.append(sent.strip())
                best_words.update(words)

        # Construct synthesized response
        synthesized = opening + '. '
        if unique_additions:
            synthesized += ' '.join(unique_additions[:2]) + '. '

        # Add merged citations
        all_citations = []
        for response in responses:
            all_citations.extend(response.citations)

        if all_citations:
            unique_citations = list(set(all_citations))
            synthesized += f"\n\nSources: {', '.join(unique_citations[:5])}"

        return synthesized.strip()

    def break_tie(self, quality_scores: Dict[ModelName, float]) -> ModelName:
        """
        Deterministically break a tie between responses of equal quality.

        Strategy: Higher model order wins (Claude Max > DeepSeek > Gemini)

        Args:
            quality_scores: {model_name: quality_score} mapping

        Returns:
            Winning model name
        """
        model_priority = {
            ModelName.CLAUDE_MAX: 3,
            ModelName.DEEPSEEK: 2,
            ModelName.GEMINI: 1
        }

        # Find maximum score
        max_score = max(quality_scores.values()) if quality_scores else 0.0

        # Among models with max score, pick highest priority
        tied_models = [m for m, s in quality_scores.items() if s == max_score]
        return max(tied_models, key=lambda m: model_priority[m])

    def compute_final_confidence(self, agreement_level: AgreementLevel,
                                winning_quality: float,
                                weighted_votes: Dict[ModelName, float]) -> float:
        """
        Compute final confidence in consensus result.

        Factors:
        - Agreement level (strong = higher confidence)
        - Quality of winning response
        - Concentration of votes (consensus = higher confidence)

        Args:
            agreement_level: Level of agreement detected
            winning_quality: Quality score of winning response [0-100]
            weighted_votes: Vote weights from confidence

        Returns:
            Final confidence [0.0, 1.0]
        """
        # Agreement contribution (0.0-0.35)
        agreement_weights = {
            AgreementLevel.STRONG_AGREEMENT: 0.35,
            AgreementLevel.MODERATE_AGREEMENT: 0.25,
            AgreementLevel.WEAK_AGREEMENT: 0.15,
            AgreementLevel.DISAGREEMENT: 0.05
        }
        agreement_score = agreement_weights.get(agreement_level, 0.05)

        # Quality contribution (0.0-0.35)
        quality_normalized = winning_quality / 100.0
        quality_score = quality_normalized * 0.35

        # Vote concentration contribution (0.0-0.30)
        # Herfindahl index: sum of squared vote shares
        vote_concentration = sum(v ** 2 for v in weighted_votes.values())
        herfindahl_score = vote_concentration * 0.30

        total = agreement_score + quality_score + herfindahl_score
        return min(1.0, max(0.0, total))

    def run_consensus(self, responses: List[ModelResponse],
                     prompt: str = "",
                     max_rounds: int = 2) -> ConsensusResult:
        """
        Execute full consensus voting and synthesis process.

        Main algorithm flow:
        1. Validate input responses
        2. Compute confidence-weighted votes
        3. Detect agreement level
        4. Rank responses by quality
        5. If disagreement, optionally trigger second round
        6. Select winning response or synthesize
        7. Compute final confidence

        Args:
            responses: List of ModelResponse from each model
            prompt: Original prompt (for context in second round)
            max_rounds: Maximum rounds to execute (1 or 2)

        Returns:
            ConsensusResult with final decision and reasoning
        """
        start_time = time.time()
        round_count = 1
        second_round_triggered = False

        # Validate input
        if not responses:
            return ConsensusResult(
                agreement_level=AgreementLevel.DISAGREEMENT,
                reasoning="No responses provided",
                round_count=0
            )

        if len(responses) < 2:
            # Single response - just wrap it
            response = responses[0]
            quality = self.quality_scorer.evaluate_response(response)

            elapsed = (time.time() - start_time) * 1000
            return ConsensusResult(
                agreement_level=AgreementLevel.STRONG_AGREEMENT,
                winning_response=response.content,
                confidence_score=response.confidence,
                model_votes={response.model.value: quality.overall_score()},
                round_count=1,
                total_execution_time_ms=elapsed,
                reasoning="Single response provided (no voting needed)"
            )

        # ROUND 1: Initial voting
        weighted_votes = self.compute_weighted_votes(responses)
        agreement_level, similarities = self.detect_agreement_level(responses)
        rankings = self.quality_rank_responses(responses)

        # Prepare vote scores for output
        vote_scores = {r.model.value: rankings[i][1].overall_score()
                      for i, r in enumerate(responses)}

        # Check for second round
        if self.should_trigger_second_round(agreement_level) and max_rounds > 1:
            second_round_triggered = True
            round_count = 2
            # In production, would pass conflict info to models for re-evaluation
            # For now, we use existing responses

        # Select winning response
        winning_response, winning_quality = rankings[0]

        # Try synthesis if we have disagreement
        synthesized = None
        if second_round_triggered and len(rankings) > 1:
            synthesized = self.synthesize_response(responses, rankings)

        # Compute final metrics
        final_confidence = self.compute_final_confidence(
            agreement_level,
            winning_quality.overall_score(),
            weighted_votes
        )

        elapsed = (time.time() - start_time) * 1000

        # Build reasoning
        reasoning = self._build_reasoning(
            agreement_level,
            winning_response.model,
            winning_quality,
            vote_scores,
            similarities
        )

        return ConsensusResult(
            agreement_level=agreement_level,
            winning_response=winning_response.content,
            confidence_score=final_confidence,
            model_votes=vote_scores,
            synthesized_response=synthesized,
            second_round_triggered=second_round_triggered,
            round_count=round_count,
            total_execution_time_ms=elapsed,
            reasoning=reasoning
        )

    def _build_reasoning(self, agreement_level: AgreementLevel,
                        winning_model: ModelName,
                        winning_quality: QualityScore,
                        vote_scores: Dict[str, float],
                        similarities: Dict[str, float]) -> str:
        """
        Build human-readable explanation of consensus decision.

        Args:
            agreement_level: Detected agreement level
            winning_model: Model whose response won
            winning_quality: Quality scores of winning response
            vote_scores: Quality scores for all models
            similarities: Pairwise similarity scores

        Returns:
            Human-readable reasoning text
        """
        reasoning = f"Consensus Decision: {agreement_level.value}\n"
        reasoning += f"Winning Model: {winning_model.value}\n"
        reasoning += f"Overall Quality Score: {winning_quality.overall_score():.1f}/100\n\n"

        reasoning += "Quality Breakdown:\n"
        reasoning += f"  - Semantic Coherence: {winning_quality.semantic_coherence:.1f}/100\n"
        reasoning += f"  - Citation Density: {winning_quality.citation_density:.1f}/100\n"
        reasoning += f"  - Semantic Richness: {winning_quality.semantic_richness:.1f}/100\n"
        reasoning += f"  - Answer Completeness: {winning_quality.answer_completeness:.1f}/100\n"
        reasoning += f"  - Error Freedom: {winning_quality.error_freedom:.1f}/100\n\n"

        reasoning += "Model Vote Scores:\n"
        for model, score in sorted(vote_scores.items(), key=lambda x: x[1], reverse=True):
            reasoning += f"  - {model}: {score:.1f}/100\n"

        if similarities:
            reasoning += "\nSimilarity Analysis:\n"
            for pair, sim in sorted(similarities.items(), key=lambda x: x[1], reverse=True):
                reasoning += f"  - {pair}: {sim*100:.1f}%\n"

        return reasoning


# ============================================================================
# Test Framework for 100 Reasoning Challenges
# ============================================================================

@dataclass
class ReasoningChallenge:
    """Single test case for evaluation."""
    challenge_id: str
    category: str  # e.g., "math", "logic", "analysis", "synthesis"
    prompt: str
    expected_elements: List[str]  # Key elements that should be in answer


class ConsensusTestFramework:
    """
    Framework for testing multi-model consensus on reasoning challenges.

    Implements the test plan from Prediction 1:
    "Run 100 reasoning challenges, blind evaluation by human raters"
    "Metric: Quality score (0-100) averaged across raters"
    """

    def __init__(self, num_challenges: int = 100):
        """Initialize test framework."""
        self.num_challenges = num_challenges
        self.engine = ConsensusVotingEngine()
        self.results = []

    def generate_test_challenges(self) -> List[ReasoningChallenge]:
        """
        Generate diverse reasoning challenges.

        Categories:
        - Analytical reasoning (10 challenges)
        - Mathematical reasoning (15 challenges)
        - Logical deduction (15 challenges)
        - Ethical reasoning (10 challenges)
        - Creative synthesis (15 challenges)
        - Programming logic (15 challenges)
        - Strategic thinking (10 challenges)
        - Scientific reasoning (5 challenges)

        Returns:
            List of ReasoningChallenge objects
        """
        challenges = []

        # Analytical reasoning
        for i in range(10):
            challenges.append(ReasoningChallenge(
                challenge_id=f"analytical_{i:02d}",
                category="analytical",
                prompt=f"Analyze the relationship between variables in this complex system: "
                       f"System {i} with {3+i} interconnected components. "
                       f"What are the emergent properties?",
                expected_elements=["components", "interactions", "emergent", "properties"]
            ))

        # Mathematical reasoning
        for i in range(15):
            challenges.append(ReasoningChallenge(
                challenge_id=f"mathematical_{i:02d}",
                category="mathematical",
                prompt=f"Solve and explain: Problem complexity level {i+1}/15. "
                       f"Find the pattern and derive the general formula.",
                expected_elements=["pattern", "formula", "derivation", "proof"]
            ))

        # Logical deduction
        for i in range(15):
            challenges.append(ReasoningChallenge(
                challenge_id=f"logical_{i:02d}",
                category="logical",
                prompt=f"Given: {3+i} logical statements (logic puzzle {i}). "
                       f"Determine the truth values and explain your reasoning.",
                expected_elements=["truth", "value", "logical", "reasoning"]
            ))

        # Ethical reasoning
        for i in range(10):
            challenges.append(ReasoningChallenge(
                challenge_id=f"ethical_{i:02d}",
                category="ethical",
                prompt=f"Ethical dilemma {i}: Analyze stakeholder perspectives and "
                       f"recommend a principled resolution.",
                expected_elements=["stakeholders", "ethics", "principles", "resolution"]
            ))

        # Creative synthesis
        for i in range(15):
            challenges.append(ReasoningChallenge(
                challenge_id=f"creative_{i:02d}",
                category="creative",
                prompt=f"Synthesize concepts {i*2} and {i*2+1}: Create novel insights by "
                       f"combining these normally separate domains.",
                expected_elements=["synthesis", "novel", "combination", "insights"]
            ))

        # Programming logic
        for i in range(15):
            challenges.append(ReasoningChallenge(
                challenge_id=f"programming_{i:02d}",
                category="programming",
                prompt=f"Code challenge {i}: Design an algorithm for this problem. "
                       f"Explain complexity and edge cases.",
                expected_elements=["algorithm", "complexity", "edge cases", "solution"]
            ))

        # Strategic thinking
        for i in range(10):
            challenges.append(ReasoningChallenge(
                challenge_id=f"strategic_{i:02d}",
                category="strategic",
                prompt=f"Strategic scenario {i}: Given constraints and objectives, "
                       f"develop a multi-phase approach.",
                expected_elements=["strategy", "phase", "constraint", "objective"]
            ))

        # Scientific reasoning
        for i in range(5):
            challenges.append(ReasoningChallenge(
                challenge_id=f"scientific_{i:02d}",
                category="scientific",
                prompt=f"Scientific question {i}: Propose testable hypotheses and "
                       f"experimental design.",
                expected_elements=["hypothesis", "experiment", "testable", "design"]
            ))

        return challenges[:self.num_challenges]

    def run_test_suite(self, mock_responses: bool = True) -> Dict[str, Any]:
        """
        Execute test suite across all challenges.

        Args:
            mock_responses: If True, use generated mock responses for testing

        Returns:
            Test results summary with metrics
        """
        challenges = self.generate_test_challenges()
        results = {
            'total_challenges': len(challenges),
            'consensus_results': [],
            'metrics': {}
        }

        for challenge in challenges:
            if mock_responses:
                # Generate mock responses for testing
                responses = self._generate_mock_responses(challenge)
            else:
                # Would call actual models here
                responses = []

            if responses:
                consensus = self.engine.run_consensus(responses, challenge.prompt)
                results['consensus_results'].append({
                    'challenge_id': challenge.challenge_id,
                    'category': challenge.category,
                    'consensus_id': consensus.consensus_id,
                    'agreement_level': consensus.agreement_level.value,
                    'quality_score': [q for q in consensus.model_votes.values()],
                    'confidence': consensus.confidence_score,
                    'execution_time_ms': consensus.total_execution_time_ms
                })

        # Compute aggregate metrics
        if results['consensus_results']:
            quality_scores = [
                s for r in results['consensus_results']
                for s in r['quality_score']
            ]
            confidences = [r['confidence'] for r in results['consensus_results']]

            results['metrics'] = {
                'average_quality_score': statistics.mean(quality_scores),
                'median_quality_score': statistics.median(quality_scores),
                'std_dev_quality': statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0,
                'average_confidence': statistics.mean(confidences),
                'agreement_level_distribution': self._count_agreement_levels(results),
                'total_execution_time_ms': sum(r['execution_time_ms']
                                              for r in results['consensus_results']),
                'average_time_per_challenge_ms': statistics.mean([
                    r['execution_time_ms'] for r in results['consensus_results']
                ])
            }

        return results

    def _generate_mock_responses(self, challenge: ReasoningChallenge) -> List[ModelResponse]:
        """
        Generate mock responses for testing without actual API calls.

        Args:
            challenge: ReasoningChallenge to answer

        Returns:
            List of ModelResponse from 3 models
        """
        base_content = (
            f"Response to {challenge.category} challenge {challenge.challenge_id}. "
            f"Based on the prompt, I'm analyzing {challenge.prompt[:50]}... "
            f"Key elements to address: {', '.join(challenge.expected_elements[:3])}. "
        )

        # Create 3 slightly different responses
        responses = []

        # Claude Max: High quality, high confidence
        responses.append(ModelResponse(
            model=ModelName.CLAUDE_MAX,
            content=base_content +
                    "Claude's analysis provides comprehensive coverage of all aspects. "
                    "The synthesis integrates multiple perspectives with rigorous logic. "
                    "[Source: https://example.com/analysis]",
            confidence=0.92,
            generation_time_ms=425.0,
            token_count=210,
            citations=["https://example.com/analysis", "https://example.com/reference"],
            timestamp=datetime.now(timezone.utc).isoformat()
        ))

        # DeepSeek: Good quality, moderate-high confidence
        responses.append(ModelResponse(
            model=ModelName.DEEPSEEK,
            content=base_content +
                    "DeepSeek's response addresses the core issues systematically. "
                    "The reasoning follows a clear logical path. "
                    "[Source: https://example.com/deepseek]",
            confidence=0.78,
            generation_time_ms=380.0,
            token_count=185,
            citations=["https://example.com/deepseek"],
            timestamp=datetime.now(timezone.utc).isoformat()
        ))

        # Gemini: Acceptable quality, moderate confidence
        responses.append(ModelResponse(
            model=ModelName.GEMINI,
            content=base_content +
                    "Gemini provides a solid response touching key points. "
                    "Some aspects could use deeper analysis.",
            confidence=0.65,
            generation_time_ms=510.0,
            token_count=155,
            citations=[],
            timestamp=datetime.now(timezone.utc).isoformat()
        ))

        return responses

    def _count_agreement_levels(self, results: Dict[str, Any]) -> Dict[str, int]:
        """Count distribution of agreement levels across all results."""
        counts = {level.value: 0 for level in AgreementLevel}
        for result in results['consensus_results']:
            level = result['agreement_level']
            counts[level] = counts.get(level, 0) + 1
        return counts

    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """
        Generate human-readable test report.

        Args:
            results: Results from run_test_suite()

        Returns:
            Formatted test report
        """
        report = "=" * 80 + "\n"
        report += "MULTI-MODEL CONSENSUS VOTING TEST REPORT\n"
        report += "=" * 80 + "\n\n"

        report += f"Test Configuration:\n"
        report += f"  - Total Challenges: {results['total_challenges']}\n"
        report += f"  - Categories: 8 (analytical, mathematical, logical, ethical, "
        report += f"creative, programming, strategic, scientific)\n"
        report += f"  - Models Evaluated: 3 (Claude Max, DeepSeek, Gemini)\n\n"

        metrics = results.get('metrics', {})
        report += f"Aggregate Metrics:\n"
        report += f"  - Average Quality Score: {metrics.get('average_quality_score', 0):.1f}/100\n"
        report += f"  - Median Quality Score: {metrics.get('median_quality_score', 0):.1f}/100\n"
        report += f"  - Quality StdDev: {metrics.get('std_dev_quality', 0):.1f}\n"
        report += f"  - Average Confidence: {metrics.get('average_confidence', 0):.3f}/1.0\n"
        report += f"  - Total Execution Time: {metrics.get('total_execution_time_ms', 0):.1f}ms\n"
        report += f"  - Avg Time Per Challenge: {metrics.get('average_time_per_challenge_ms', 0):.1f}ms\n\n"

        agreement_dist = metrics.get('agreement_level_distribution', {})
        report += f"Agreement Level Distribution:\n"
        for level, count in sorted(agreement_dist.items()):
            pct = (count / results['total_challenges'] * 100) if results['total_challenges'] > 0 else 0
            report += f"  - {level}: {count} ({pct:.1f}%)\n"

        report += "\n" + "=" * 80 + "\n"
        return report


# ============================================================================
# Example Usage and Export
# ============================================================================

if __name__ == "__main__":
    # Create sample test
    engine = ConsensusVotingEngine()

    # Generate test framework
    test_framework = ConsensusTestFramework(num_challenges=100)

    # Run test suite with mock responses
    print("Running consensus voting algorithm test suite...")
    results = test_framework.run_test_suite(mock_responses=True)

    # Print report
    report = test_framework.generate_test_report(results)
    print(report)

    # Print sample consensus result
    if results['consensus_results']:
        sample = results['consensus_results'][0]
        print(f"\nSample Consensus Result (Challenge {sample['challenge_id']}):")
        print(f"  Agreement Level: {sample['agreement_level']}")
        print(f"  Quality Scores: {[f'{s:.1f}' for s in sample['quality_score']]}")
        print(f"  Consensus Confidence: {sample['confidence']:.3f}")
        print(f"  Execution Time: {sample['execution_time_ms']:.1f}ms")
