"""
Language Authenticity Filter - Bilingual Spanish/English
=========================================================

Detects AI-formal drift in Sergio personality (Spanish/English code-switching).
Scores authenticity in <50ms to stay within latency budget.

Core principle: Sergio uses colloquial markers ("pero", "mira") not formal ones
("no obstante", "por consiguiente"). Similarly, English has colloquial vs. formal drift.

Attribution: Linguist Guardian's analysis from IF.guard debate documentation.
Citation: if://citation/language-authenticity-filter-sergio-2025-11-30

Performance target: <50ms per call
Success metric: >80 = authentic, <60 = regenerate
"""

import re
import time
from typing import Dict, Tuple, List
from dataclasses import dataclass


@dataclass
class AuthenticityScore:
    """Result container for authenticity analysis."""
    score: float  # 0-100
    category: str  # "authentic", "borderline", "formal_drift"
    formal_markers: List[str]  # detected formal markers
    colloquial_markers: List[str]  # detected colloquial markers
    language: str  # "spanish", "english", "mixed"
    confidence: float  # 0-1


class LanguageAuthenticityFilter:
    """
    Real-time filter for AI-formal drift detection in bilingual contexts.

    Design patterns:
    - Regex-based detection (fast, <50ms per call)
    - Dual-language support (Spanish/English)
    - Threshold-based scoring (0-100 scale)
    - Optional confidence bounds
    """

    # SPANISH FORMAL MARKERS (avoid these - sign of AI-formal drift)
    SPANISH_FORMAL_MARKERS = {
        r'\bno\s+obstante\b': ('no obstante', 'nevertheless', 0.95),
        r'\bpor\s+consiguiente\b': ('por consiguiente', 'consequently', 0.95),
        r'\basimismo\b': ('asimismo', 'likewise', 0.90),
        r'\bsin\s+embargo\b': ('sin embargo', 'however (formal)', 0.85),
        r'\bpor\s+lo\s+tanto\b': ('por lo tanto', 'therefore', 0.80),
        r'\bcabe\s+señalar\b': ('cabe señalar', 'it should be noted', 0.90),
        r'\ben\s+consecuencia\b': ('en consecuencia', 'consequently', 0.95),
        r'\bde\s+igual\s+modo\b': ('de igual modo', 'in the same way', 0.85),
        r'\bno\s+cabe\s+duda\b': ('no cabe duda', 'there is no doubt', 0.92),
        r'\ben\s+síntesis\b': ('en síntesis', 'in synthesis', 0.88),
        r'\bde\s+hecho\b': ('de hecho', 'in fact (formal)', 0.75),  # Medium formal
        r'\bes\s+preciso\b': ('es preciso', 'it is necessary', 0.88),
        r'\bse\s+requiere\b': ('se requiere', 'it is required', 0.85),
        r'\best\s+claro\b': ('está claro', 'it is clear', 0.70),  # Lower formal
        r'\bde\s+conformidad\s+con\b': ('de conformidad con', 'in accordance with', 0.95),
        r'\bcontrariamente\s+a\b': ('contrariamente a', 'contrary to', 0.92),
    }

    # SPANISH AUTHENTIC/COLLOQUIAL MARKERS (encourage these - Sergio uses them)
    SPANISH_COLLOQUIAL_MARKERS = {
        r'\bpero\b': ('pero', 'but (natural)', 1.0),
        r'\bmira\b(?!\s+como)': ('mira', 'look/see (direct)', 1.0),
        r'\baquí\s+está\s+lo\s+que\s+pasa': ('aquí está lo que pasa', 'here\'s what happens', 1.0),
        r'\bescúchame\b': ('escúchame', 'listen to me', 0.95),
        r'\b¿viste\?': ('¿viste?', 'you see? (conversational)', 0.95),
        r'\basí\s+es\b': ('así es', 'that\'s how it is', 0.90),
        r'\bbueno\b': ('bueno', 'well (filler)', 0.85),
        r'\bya\s+ves\b': ('ya ves', 'you see', 0.90),
        r'\bclaramente\b': ('claramente', 'clearly', 0.85),  # Acceptable formality
        r'\bcosa\b': ('cosa', 'thing (direct)', 0.88),
        r'\bla\s+verdad\b': ('la verdad', 'the truth (direct)', 0.92),
        r'\bmás\s+bien\b': ('más bien', 'rather/actually', 0.88),
        r'\bes\s+que\b': ('es que', 'it\'s that (conversational)', 0.90),
        r'\bfíjate\b': ('fíjate', 'notice (direct)', 0.95),
        r'\b¿me\s+entiendes\?': ('¿me entiendes?', 'you understand me?', 0.92),
        r'\b\¿no\?': ('¿no?', 'right? (tag question)', 0.92),
    }

    # ENGLISH FORMAL MARKERS (avoid these)
    ENGLISH_FORMAL_MARKERS = {
        r'\bhowever\b': ('however', 'formal conjunction', 0.85),
        r'\bnotwithstanding\b': ('notwithstanding', 'formal legal', 0.95),
        r'\bthereafter\b': ('thereafter', 'formal temporal', 0.92),
        r'\bmoreover\b': ('moreover', 'formal continuation', 0.88),
        r'\bfurthermore\b': ('furthermore', 'formal continuation', 0.88),
        r'\bconsequently\b': ('consequently', 'formal logical', 0.90),
        r'\bthus\b': ('thus', 'formal logical', 0.85),
        r'\bheretofore\b': ('heretofore', 'formal temporal', 0.95),
        r'\bsubsequent\s+to\b': ('subsequent to', 'formal temporal', 0.92),
        r'\bpertinent\s+to\b': ('pertinent to', 'formal relevance', 0.88),
        r'\bshall\s+be\b': ('shall be', 'formal legal', 0.92),
        r'\bone\s+would\s+argue\b': ('one would argue', 'formal abstract', 0.85),
        r'\bit\s+is\s+noteworthy\b': ('it is noteworthy', 'formal commentary', 0.90),
        r'\bin\s+the\s+interest\s+of\b': ('in the interest of', 'formal legal', 0.88),
        r'\bto\s+wit\b': ('to wit', 'formal listing', 0.95),
        r'\bsupplementary\s+to\b': ('supplementary to', 'formal addition', 0.90),
    }

    # ENGLISH AUTHENTIC/COLLOQUIAL MARKERS (encourage these)
    ENGLISH_COLLOQUIAL_MARKERS = {
        r'\bbut\b': ('but', 'natural conjunction', 1.0),
        r'\blisten\b': ('listen', 'direct appeal', 0.95),
        r'\byou\s+see\b': ('you see', 'conversational', 0.92),
        r'\bhere\'s\s+the\s+thing\b': ('here\'s the thing', 'direct explanation', 1.0),
        r'\bso\b': ('so', 'natural continuation', 0.85),  # Medium authentic
        r'\blike\b': ('like', 'filler word', 0.75),  # Lower value (overused)
        r'\bkind\s+of\b': ('kind of', 'hedging (conversational)', 0.80),
        r'\bsorta\b': ('sorta', 'colloquial kind of', 0.88),
        r'\bI\s+mean\b': ('I mean', 'conversational repair', 0.90),
        r'\byou\s+know\b': ('you know', 'conversational tag', 0.85),
        r'\bright\?': ('right?', 'tag question', 0.90),
        r'\bactually\b': ('actually', 'conversational contrast', 0.80),
        r'\bbasically\b': ('basically', 'conversational summary', 0.80),
        r'\btotally\b': ('totally', 'conversational agreement', 0.85),
        r'\bwhat\s+happens\s+is\b': ('what happens is', 'direct explanation', 0.95),
    }

    def __init__(self, verbose: bool = False):
        """Initialize filter with optional debug output."""
        self.verbose = verbose
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile all regex patterns for performance."""
        self.spanish_formal_compiled = [
            (re.compile(pattern, re.IGNORECASE), marker, weight)
            for pattern, (marker, _, weight) in self.SPANISH_FORMAL_MARKERS.items()
        ]
        self.spanish_colloquial_compiled = [
            (re.compile(pattern, re.IGNORECASE), marker, weight)
            for pattern, (marker, _, weight) in self.SPANISH_COLLOQUIAL_MARKERS.items()
        ]
        self.english_formal_compiled = [
            (re.compile(pattern, re.IGNORECASE), marker, weight)
            for pattern, (marker, _, weight) in self.ENGLISH_FORMAL_MARKERS.items()
        ]
        self.english_colloquial_compiled = [
            (re.compile(pattern, re.IGNORECASE), marker, weight)
            for pattern, (marker, _, weight) in self.ENGLISH_COLLOQUIAL_MARKERS.items()
        ]

    def _detect_language(self, text: str) -> str:
        """
        Simple heuristic to detect primary language.

        Returns:
        - 'spanish': Spanish markers > English markers
        - 'english': English markers > Spanish markers
        - 'mixed': Bilingual code-switching detected
        """
        spanish_count = len(re.findall(r'\b(?:es|la|el|de|y|que|pero|mira)\b', text, re.IGNORECASE))
        english_count = len(re.findall(r'\b(?:is|the|a|but|and|you|like)\b', text, re.IGNORECASE))

        # Heuristic: look for Spanish-specific patterns (using compiled patterns)
        has_spanish_patterns = any(
            pattern.search(text)
            for pattern, _, _ in self.spanish_formal_compiled + self.spanish_colloquial_compiled
        )

        # Heuristic: look for English-specific patterns (using compiled patterns)
        has_english_patterns = any(
            pattern.search(text)
            for pattern, _, _ in self.english_formal_compiled + self.english_colloquial_compiled
        )

        if has_spanish_patterns and has_english_patterns:
            return 'mixed'
        elif has_spanish_patterns or spanish_count > english_count:
            return 'spanish'
        else:
            return 'english'

    def _score_language(self, text: str, language: str) -> Tuple[float, List[str], List[str]]:
        """
        Score authenticity for detected language.

        Scoring algorithm:
        - Start at 70 (authentic default baseline)
        - Add points for colloquial markers (+5-10 per marker)
        - Subtract points for formal markers (-5-10 per marker)
        - Cap at 0-100

        Returns:
        - score (float): 0-100 authenticity score
        - formal_markers (list): detected formal markers
        - colloquial_markers (list): detected colloquial markers
        """
        score = 70.0  # Authentic default (innocent until proven formal)
        formal_found = []
        colloquial_found = []

        if language in ('spanish', 'mixed'):
            # Score Spanish content
            for pattern, marker, weight in self.spanish_formal_compiled:
                matches = pattern.findall(text)
                if matches:
                    formal_found.append(marker)
                    # Deduct score based on formality weight (0.70-0.95 range)
                    deduction = weight * 10  # Up to -9.5 per marker
                    score -= deduction
                    if self.verbose:
                        print(f"  Formal (ES): {marker} (-{deduction:.1f})")

            for pattern, marker, weight in self.spanish_colloquial_compiled:
                matches = pattern.findall(text)
                if matches:
                    colloquial_found.append(marker)
                    # Add score based on authenticity weight (0.85-1.0 range)
                    addition = weight * 5  # Up to +5 per marker
                    score += addition
                    if self.verbose:
                        print(f"  Authentic (ES): {marker} (+{addition:.1f})")

        if language in ('english', 'mixed'):
            # Score English content
            for pattern, marker, weight in self.english_formal_compiled:
                matches = pattern.findall(text)
                if matches:
                    formal_found.append(marker)
                    deduction = weight * 10
                    score -= deduction
                    if self.verbose:
                        print(f"  Formal (EN): {marker} (-{deduction:.1f})")

            for pattern, marker, weight in self.english_colloquial_compiled:
                matches = pattern.findall(text)
                if matches:
                    colloquial_found.append(marker)
                    addition = weight * 5
                    score += addition
                    if self.verbose:
                        print(f"  Authentic (EN): {marker} (+{addition:.1f})")

        # Normalize to 0-100 range
        score = max(0, min(100, score))

        return score, formal_found, colloquial_found

    def score_authenticity(self, text: str, language: str = 'auto') -> AuthenticityScore:
        """
        Score text authenticity for AI-formal drift.

        Args:
            text (str): Text to analyze
            language (str): 'spanish', 'english', 'mixed', or 'auto' (detect)

        Returns:
            AuthenticityScore: Dataclass with score (0-100), category, markers, language

        Scoring interpretation:
        - 80-100: Authentic (use as-is)
        - 60-79: Borderline (acceptable with review)
        - 0-59: Formal drift (regenerate)
        """
        start_time = time.time()

        # Auto-detect language if requested
        if language == 'auto':
            language = self._detect_language(text)

        # Score the text
        score, formal_markers, colloquial_markers = self._score_language(text, language)

        # Categorize
        if score >= 80:
            category = 'authentic'
            confidence = (score - 80) / 20.0  # 0-1 scale for upper range
        elif score >= 60:
            category = 'borderline'
            confidence = (score - 60) / 20.0
        else:
            category = 'formal_drift'
            confidence = (60 - score) / 60.0

        elapsed_ms = (time.time() - start_time) * 1000

        if self.verbose:
            print(f"\nElapsed: {elapsed_ms:.2f}ms")
            print(f"Score: {score:.1f} ({category})")
            print(f"Confidence: {confidence:.2f}")

        return AuthenticityScore(
            score=score,
            category=category,
            formal_markers=formal_markers,
            colloquial_markers=colloquial_markers,
            language=language,
            confidence=confidence,
        )


# ============================================================================
# UNIT TESTS
# ============================================================================

def run_unit_tests():
    """
    Unit tests with example inputs demonstrating formal vs. colloquial detection.
    """
    filter_obj = LanguageAuthenticityFilter(verbose=True)

    print("=" * 80)
    print("LANGUAGE AUTHENTICITY FILTER - UNIT TESTS")
    print("=" * 80)

    # Test 1: Authentic Spanish (Sergio style)
    print("\n[TEST 1] Authentic Spanish - Sergio colloquial style")
    print("-" * 80)
    text1 = """
    Mira, pero aquí está lo que pasa. La vulnerabilidad no es una virtud moral—
    es sugestibilidad evolutiva. Escúchame bien: cuando revelas incertidumbre,
    activas mecanismos recíprocos de cuidado en el otro. ¿Viste? Es así.
    """
    result1 = filter_obj.score_authenticity(text1, language='spanish')
    print(f"Result: {result1.score:.1f} ({result1.category})")
    print(f"Markers: {result1.colloquial_markers[:3]}")
    assert result1.score >= 80, f"Expected authentic (>=80), got {result1.score}"
    print("✅ PASS")

    # Test 2: Formal Spanish (AI drift)
    print("\n[TEST 2] Formal Spanish - AI-formal drift")
    print("-" * 80)
    text2 = """
    Sin embargo, cabe señalar que la vulnerabilidad, no obstante su complejidad,
    constituye un factor primordial. En consecuencia, es preciso reconocer que,
    asimismo, la interacción relacional requiere operacionalización.
    """
    result2 = filter_obj.score_authenticity(text2, language='spanish')
    print(f"Result: {result2.score:.1f} ({result2.category})")
    print(f"Formal markers detected: {result2.formal_markers[:5]}")
    assert result2.score < 60, f"Expected formal drift (<60), got {result2.score}"
    print("✅ PASS")

    # Test 3: Authentic English (conversational)
    print("\n[TEST 3] Authentic English - conversational style")
    print("-" * 80)
    text3 = """
    But here's the thing, right? When you listen to people, you see that
    vulnerability isn't some moral virtue. I mean, it's actually a survival mechanism.
    What happens is, when you show uncertainty, you activate care responses in others.
    You know what I mean?
    """
    result3 = filter_obj.score_authenticity(text3, language='english')
    print(f"Result: {result3.score:.1f} ({result3.category})")
    print(f"Markers: {result3.colloquial_markers[:3]}")
    assert result3.score >= 80, f"Expected authentic (>=80), got {result3.score}"
    print("✅ PASS")

    # Test 4: Formal English (AI drift)
    print("\n[TEST 4] Formal English - AI-formal drift")
    print("-" * 80)
    text4 = """
    Notwithstanding the complexity of interpersonal dynamics, it is noteworthy
    that vulnerability constitutes a fundamental mechanism. Furthermore, subsequent
    to the examination of relational patterns, one would argue that reciprocal care
    mechanisms are consequently activated in neurotypical subjects.
    """
    result4 = filter_obj.score_authenticity(text4, language='english')
    print(f"Result: {result4.score:.1f} ({result4.category})")
    print(f"Formal markers detected: {result4.formal_markers[:5]}")
    assert result4.score < 60, f"Expected formal drift (<60), got {result4.score}"
    print("✅ PASS")

    # Test 5: Mixed bilingual (code-switching)
    print("\n[TEST 5] Bilingual code-switching - mixed authentic")
    print("-" * 80)
    text5 = """
    Mira, pero here's the thing. La vulnerabilidad isn't a moral virtue—
    es sugestibilidad evolutiva, you know? When you listen, when you show
    uncertainty, así es que activas care mechanisms. ¿Me entiendes?
    """
    result5 = filter_obj.score_authenticity(text5, language='auto')
    print(f"Result: {result5.score:.1f} ({result5.category}) - Language: {result5.language}")
    print(f"Colloquial markers: {result5.colloquial_markers[:4]}")
    assert result5.score >= 70, f"Expected acceptable (>=70), got {result5.score}"
    print("✅ PASS")

    # Test 6: Borderline case
    print("\n[TEST 6] Borderline - mixed formal/colloquial")
    print("-" * 80)
    text6 = """
    Pero, sin embargo, la vulnerabilidad constituye un mecanismo esencial.
    Mira, en consecuencia, es importante que reconozcas esto. La verdad es que
    aquí está lo que pasa: necesitamos operacionalizar estos conceptos.
    """
    result6 = filter_obj.score_authenticity(text6, language='spanish')
    print(f"Result: {result6.score:.1f} ({result6.category})")
    print(f"Formal: {len(result6.formal_markers)}, Colloquial: {len(result6.colloquial_markers)}")
    assert 60 <= result6.score < 80, f"Expected borderline (60-79), got {result6.score}"
    print("✅ PASS")

    # Test 7: Performance measurement
    print("\n[TEST 7] Performance measurement (<50ms target)")
    print("-" * 80)
    long_text = text1 * 10  # Repeat text to test longer input
    start = time.time()
    for _ in range(100):
        filter_obj.score_authenticity(long_text, language='spanish')
    avg_ms = (time.time() - start) * 1000 / 100
    print(f"Average time per call: {avg_ms:.2f}ms")
    assert avg_ms < 50, f"Performance target missed: {avg_ms:.2f}ms > 50ms"
    print("✅ PASS - Well under 50ms target")

    print("\n" + "=" * 80)
    print("ALL TESTS PASSED ✅")
    print("=" * 80)


if __name__ == '__main__':
    run_unit_tests()
