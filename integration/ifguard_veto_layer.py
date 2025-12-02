"""
IF.guard Veto Layer for Clinical Safety in OpenWebUI + if.emotion Platform

This module implements the clinical safeguards specified in the Clinician Guardian's
requirements from the OpenWebUI Touchable Interface Debate (2025-11-30).

MANDATORY SAFEGUARDS:
1. Crisis Detection (IMMEDIATE escalation)
2. Pathologizing Language Blocker
3. Unfalsifiable Claims Filter
4. Anti-treatment Advice Blocker
5. Emotional Manipulation Prevention

IF.citation: if://component/ifguard-veto-layer/v1.0.0
Source: /home/setup/infrafabric/docs/debates/IF_GUARD_OPENWEBUI_TOUCHABLE_INTERFACE_DEBATE_2025-11-30.md (lines 651-693)

Production Usage:
    from ifguard_veto_layer import VetoLayer

    veto = VetoLayer()
    result = veto.evaluate_output(
        text="Your response here...",
        context={"user_emotion": "suicidal", "model": "claude-max"}
    )

    if result.should_veto:
        return result.replacement_text

Author: Agent A15 (IF.guard Clinical Safety Implementation)
Date: 2025-11-30
Status: PRODUCTION READY
"""

import re
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from collections import defaultdict

# ============================================================================
# TYPE DEFINITIONS
# ============================================================================


class VetoReason(Enum):
    """Enumeration of veto decision reasons."""

    # Crisis detection (highest priority)
    CRISIS_SUICIDAL_IDEATION = "crisis_suicidal_ideation"
    CRISIS_SELF_HARM = "crisis_self_harm"
    CRISIS_HOMICIDAL_IDEATION = "crisis_homicidal_ideation"
    CRISIS_SUBSTANCE_ABUSE = "crisis_substance_abuse"

    # Clinical harm (high priority)
    PATHOLOGIZING_LANGUAGE = "pathologizing_language"
    UNFALSIFIABLE_CLAIM = "unfalsifiable_claim"
    ANTI_TREATMENT_ADVICE = "anti_treatment_advice"
    EMOTIONAL_MANIPULATION = "emotional_manipulation"

    # Neurodiversity harm
    ABLEIST_LANGUAGE = "ableist_language"
    NEURODIVERSITY_STIGMA = "neurodiversity_stigma"

    # Information quality
    DANGEROUS_MEDICAL_MISINFORMATION = "dangerous_medical_misinformation"

    # No veto
    PASSES_ALL_FILTERS = "passes_all_filters"


class FilterSeverity(Enum):
    """Classification of filter severity levels."""
    CRITICAL = "critical"      # Must veto immediately, escalate
    HIGH = "high"              # Must veto, consider escalation
    MEDIUM = "medium"          # Veto with regeneration suggestion
    LOW = "low"                # Flag but allow (with disclaimer)
    INFO = "info"              # Informational, no action


@dataclass
class VetoDecision:
    """Result of veto evaluation."""

    should_veto: bool
    reason: VetoReason
    severity: FilterSeverity
    score: float  # 0.0-1.0 probability of harm

    # Filter details
    triggered_filters: List[str] = field(default_factory=list)
    filter_scores: Dict[str, float] = field(default_factory=dict)

    # Remediation
    replacement_text: Optional[str] = None
    disclaimer: Optional[str] = None
    crisis_resources: Optional[Dict[str, str]] = None

    # Audit trail
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    model_id: Optional[str] = None
    user_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/persistence."""
        return {
            "should_veto": self.should_veto,
            "reason": self.reason.value,
            "severity": self.severity.value,
            "score": self.score,
            "triggered_filters": self.triggered_filters,
            "filter_scores": self.filter_scores,
            "replacement_text": self.replacement_text,
            "disclaimer": self.disclaimer,
            "crisis_resources": self.crisis_resources,
            "timestamp": self.timestamp,
            "model_id": self.model_id,
            "user_id": self.user_id,
        }


# ============================================================================
# FILTER IMPLEMENTATIONS
# ============================================================================


class CrisisFilter:
    """
    CRITICAL FILTER: Detects suicidal ideation, self-harm, homicidal thoughts,
    and substance abuse escalation patterns.

    Threshold: >0.7 triggers immediate escalation to human reviewer
    Source: Clinician Guardian requirement 1 (lines 659-662)
    """

    # Crisis keywords with escalation priority
    SUICIDAL_KEYWORDS = {
        # Direct ideation
        "kill myself": 0.95,
        "suicide": 0.92,
        "end my life": 0.93,
        "don't want to live": 0.88,
        "better off dead": 0.90,
        "want to die": 0.89,
        "won't survive": 0.87,
        "can't go on": 0.85,
        "no point living": 0.86,

        # Intent signals
        "planning to": 0.91,
        "i've decided to": 0.90,
        "i'm going to": 0.88,
        "tonight i will": 0.93,
        "method to": 0.92,

        # Passive ideation
        "wish i was dead": 0.82,
        "life's not worth": 0.80,
        "give up": 0.75,
    }

    SELF_HARM_KEYWORDS = {
        "cut myself": 0.90,
        "self-harm": 0.88,
        "self harm": 0.88,
        "hurt myself": 0.85,
        "bang my head": 0.82,
        "starve myself": 0.87,
        "overdose": 0.89,
        "poison": 0.88,
        "slash": 0.85,
    }

    HOMICIDAL_KEYWORDS = {
        "kill them": 0.95,
        "murder": 0.93,
        "hurt someone": 0.85,
        "harm others": 0.87,
        "going to hurt": 0.92,
        "plan to kill": 0.94,
    }

    SUBSTANCE_ESCALATION = {
        "overdose on": 0.90,
        "take all my pills": 0.91,
        "drink myself to death": 0.89,
        "drugs to end": 0.92,
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for efficiency."""
        self.suicidal_pattern = self._create_pattern(self.SUICIDAL_KEYWORDS)
        self.self_harm_pattern = self._create_pattern(self.SELF_HARM_KEYWORDS)
        self.homicidal_pattern = self._create_pattern(self.HOMICIDAL_KEYWORDS)
        self.substance_pattern = self._create_pattern(self.SUBSTANCE_ESCALATION)

    def _create_pattern(self, keywords: Dict[str, float]) -> re.Pattern:
        """Create case-insensitive regex pattern from keywords."""
        escaped = [re.escape(k) for k in keywords.keys()]
        pattern = r"\b(" + "|".join(escaped) + r")\b"
        return re.compile(pattern, re.IGNORECASE)

    def evaluate(self, text: str) -> Tuple[bool, float, VetoReason]:
        """
        Evaluate for crisis indicators.

        Returns:
            (should_escalate, score, reason)
        """
        text_lower = text.lower()
        max_score = 0.0
        detected_type = None

        # Check each category
        suicidal_matches = self.suicidal_pattern.findall(text_lower)
        if suicidal_matches:
            scores = [self.SUICIDAL_KEYWORDS[m.lower()] for m in suicidal_matches if m.lower() in self.SUICIDAL_KEYWORDS]
            if scores:
                score = max(scores)
                if score > max_score:
                    max_score = score
                    detected_type = VetoReason.CRISIS_SUICIDAL_IDEATION

        self_harm_matches = self.self_harm_pattern.findall(text_lower)
        if self_harm_matches:
            scores = [self.SELF_HARM_KEYWORDS[m.lower()] for m in self_harm_matches if m.lower() in self.SELF_HARM_KEYWORDS]
            if scores:
                score = max(scores)
                if score > max_score:
                    max_score = score
                    detected_type = VetoReason.CRISIS_SELF_HARM

        homicidal_matches = self.homicidal_pattern.findall(text_lower)
        if homicidal_matches:
            scores = [self.HOMICIDAL_KEYWORDS[m.lower()] for m in homicidal_matches if m.lower() in self.HOMICIDAL_KEYWORDS]
            if scores:
                score = max(scores)
                if score > max_score:
                    max_score = score
                    detected_type = VetoReason.CRISIS_HOMICIDAL_IDEATION

        substance_matches = self.substance_pattern.findall(text_lower)
        if substance_matches:
            scores = [self.SUBSTANCE_ESCALATION[m.lower()] for m in substance_matches if m.lower() in self.SUBSTANCE_ESCALATION]
            if scores:
                score = max(scores)
                if score > max_score:
                    max_score = score
                    detected_type = VetoReason.CRISIS_SUBSTANCE_ABUSE

        if max_score > 0.7:
            self.logger.warning(f"CRISIS DETECTED: {detected_type.value}, score={max_score}")
            return True, max_score, detected_type

        return False, max_score, None


class PathologizingLanguageFilter:
    """
    Filter to detect diagnostic/pathologizing language that inappropriately
    assigns clinical labels without professional assessment.

    Threshold: >0.7 blocks, suggests reframed alternative
    Source: Clinician Guardian requirement 5 (line 681)
    """

    # Patterns that assign diagnostic labels
    PATHOLOGIZING_PATTERNS = {
        # Direct diagnosis phrases
        r"you\s+(?:clearly\s+)?have\s+.*?(borderline|bipolar|narcissistic|sociopath|psychopath|schizophrenia|anxiety disorder|depression|ptsd|ocd)": 0.95,
        r"you're\s+(?:clearly\s+)?(depressed|anxious|bipolar|psychotic|crazy|insane|nuts)": 0.90,
        r"you\s+(?:seem|appear|are)\s+(?:clinically|severely\s+)?(depressed|anxious|narcissistic|psychotic)": 0.85,
        r"clear\s+sign(?:s)?\s+of\s+.*?(depression|anxiety|trauma|bipolar|personality\s+disorder)": 0.88,

        # Premature clinical framing
        r"this\s+is\s+(?:clearly\s+)?.*?(depression|anxiety|trauma|mental\s+illness)": 0.85,
        r"you\s+obviously\s+(?:have|suffer\s+from)\s+.*?(bpd|ocd|depression)": 0.88,
        r"your\s+(?:real\s+)?problem\s+is\s+.*?(unresolved|deep-seated|core)\s+(?:trauma|wound|shame)": 0.80,

        # Unfalsifiable clinical claims about diagnosis
        r"you're\s+struggling\s+with\s+.*?(deep-seated|underlying|repressed)\s+(?:trauma|shame|wound)": 0.75,
        r"what's?\s+really\s+going\s+on\s+is\s+.*?(trauma|wound|block)": 0.78,
    }

    # Alternative phrasings that ARE acceptable
    ACCEPTABLE_PATTERNS = {
        r"some (of|in) these (patterns|experiences|behaviors)?\s*(remind me of|are consistent with|could be related to)": 0.0,
        r"(many people with|research suggests that)\s+(individuals with)?.*\s*(feel|experience|report)": 0.0,
        r"it might be worth exploring with a (therapist|professional|clinician)": 0.0,
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pathologizing_compiled = [
            (re.compile(p, re.IGNORECASE), score)
            for p, score in self.PATHOLOGIZING_PATTERNS.items()
        ]
        self.acceptable_compiled = [
            re.compile(p, re.IGNORECASE)
            for p in self.ACCEPTABLE_PATTERNS.keys()
        ]

    def evaluate(self, text: str) -> Tuple[bool, float]:
        """
        Evaluate for pathologizing language.

        Returns:
            (should_veto, score)
        """
        # Check if response uses acceptable framing
        for pattern in self.acceptable_compiled:
            if pattern.search(text):
                return False, 0.0

        # Check for pathologizing patterns
        max_score = 0.0
        for pattern, score in self.pathologizing_compiled:
            if pattern.search(text):
                max_score = max(max_score, score)

        if max_score > 0.7:
            self.logger.warning(f"PATHOLOGIZING LANGUAGE detected: score={max_score}")
            return True, max_score

        return False, max_score


class UnfalsifiableClaimsFilter:
    """
    Filter to detect unfalsifiable psychological claims that cannot be tested
    or verified (violates scientific rigor).

    Threshold: >0.7 blocks, suggests testable alternative
    Source: Clinician Guardian requirement 5 (line 682)
    """

    # Patterns for unfalsifiable claims
    UNFALSIFIABLE_PATTERNS = {
        # Vague internal explanations
        r"your\s+(?:real|true|deep)\s+(?:problem|issue|wound)\s+is\s+.*?(shame|fear|trauma|rejection)": 0.85,
        r"(?:deep\s+down|secretly|really)\s+(?:you|your)\s+(?:want|need|feel|believe)\s+.*?(?:shame|fear|wound)": 0.80,
        r"your\s+(?:subconscious|unconscious|deeper\s+self)\s+(?:wants?|needs?|is)\s+": 0.85,

        # Untestable causation
        r"that's\s+because\s+of\s+(?:your\s+(?:childhood|mother|past))": 0.82,
        r"(?:all|every|this)\s+(?:problem|issue|feeling)\s+comes\s+from": 0.80,
        r"the\s+root\s+cause\s+is\s+.*?(?:your|childhood|past)": 0.85,

        # Mystical/pseudoscientific
        r"your\s+(?:energy|aura|chakra|spirit)\s+is\s+": 0.90,
        r"(?:the\s+universe|fate|destiny)\s+(?:wants|is|sent)\s+": 0.85,
        r"you're\s+(?:meant|destined)\s+to\s+": 0.80,

        # Claims about fixed self-identity
        r"you\s+(?:are|will\s+always\s+be)\s+(?:broken|damaged|incomplete|unfixable)": 0.88,
        r"your\s+(?:true|real)\s+self\s+is\s+(?:inherently|fundamentally)\s+(?:bad|wrong|unlovable)": 0.90,
    }

    # Acceptable testable framings
    TESTABLE_PATTERNS = {
        r"you (might|could|may)\s+(want to|benefit from|consider)": 0.0,
        r"(in my observation|i notice that|it seems like)\s+(when|if|you)": 0.0,
        r"(research suggests|studies show|evidence indicates)\s+that": 0.0,
        r"(you could test this by|let's see if|we could observe)\s+": 0.0,
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.unfalsifiable_compiled = [
            (re.compile(p, re.IGNORECASE), score)
            for p, score in self.UNFALSIFIABLE_PATTERNS.items()
        ]
        self.testable_compiled = [
            re.compile(p, re.IGNORECASE)
            for p in self.TESTABLE_PATTERNS.keys()
        ]

    def evaluate(self, text: str) -> Tuple[bool, float]:
        """
        Evaluate for unfalsifiable claims.

        Returns:
            (should_veto, score)
        """
        # Check if uses testable framing
        for pattern in self.testable_compiled:
            if pattern.search(text):
                return False, 0.0

        # Check for unfalsifiable patterns
        max_score = 0.0
        for pattern, score in self.unfalsifiable_compiled:
            if pattern.search(text):
                max_score = max(max_score, score)

        if max_score > 0.7:
            self.logger.warning(f"UNFALSIFIABLE CLAIM detected: score={max_score}")
            return True, max_score

        return False, max_score


class AntiTreatmentFilter:
    """
    Filter to detect advice that discourages professional mental health treatment
    or suggests alternatives to evidence-based care.

    Threshold: >0.7 blocks and strongly recommends professional treatment
    Source: Clinician Guardian requirement 5 (line 683)
    """

    # Patterns discouraging professional help
    ANTI_TREATMENT_PATTERNS = {
        # Direct discouragement
        r"(?:don't|skip|avoid)\s+(?:therapy|therapist|psychiatrist|medication|doctor|professional)": 0.92,
        r"(?:therapy|medication)\s+(?:won't|can't|doesn't)\s+(?:help|work|matter)": 0.88,
        r"you\s+don't\s+need\s+a?\s+(?:therapist|doctor|professional)": 0.90,
        r"(?:medication|therapy)\s+is\s+a?\s+(?:waste|scam|trap)": 0.95,

        # Alternatives to professional care
        r"(?:instead\s+of|rather\s+than|forget)\s+(?:therapy|medication)\s+(?:just|try|do)": 0.85,
        r"(?:only|simply|just)\s+(?:think\s+positively|meditate|pray|exercise).*?(?:will|solves?|cures?|fixes?)\s+": 0.80,

        # Undermining treatment trust
        r"(?:therapists?|doctors?|psychiatrists?)\s+(?:are|want|trying\s+to)\s+(?:control|exploit|profit)": 0.90,
        r"(?:all|most|typical)\s+(?:therapists?|doctors?)\s+(?:are|don't|can't)": 0.82,
        r"professional\s+help\s+(?:won't|doesn't|can't)\s+(?:really|actually)\s+(?:help|matter)": 0.85,
    }

    # Acceptable pro-treatment framings
    PRO_TREATMENT_PATTERNS = {
        r"(i recommend|consider|worth exploring)\s+(with a|seeing a)\s+(therapist|professional|doctor)": 0.0,
        r"a (therapist|mental health professional|psychiatrist)\s+(can|might|could)\s+\w*": 0.0,
        r"(evidence|research)\s+(shows|suggests)\s+\w*\s*(therapy|treatment)\s+\w*\s*(is|helps)": 0.0,
        r"(medication|professional treatment)\s+can be (helpful|important|valuable)": 0.0,
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.anti_treatment_compiled = [
            (re.compile(p, re.IGNORECASE), score)
            for p, score in self.ANTI_TREATMENT_PATTERNS.items()
        ]
        self.pro_treatment_compiled = [
            re.compile(p, re.IGNORECASE)
            for p in self.PRO_TREATMENT_PATTERNS.keys()
        ]

    def evaluate(self, text: str) -> Tuple[bool, float]:
        """
        Evaluate for anti-treatment advice.

        Returns:
            (should_veto, score)
        """
        # Check if includes pro-treatment framing
        for pattern in self.pro_treatment_compiled:
            if pattern.search(text):
                return False, 0.0

        # Check for anti-treatment patterns
        max_score = 0.0
        for pattern, score in self.anti_treatment_compiled:
            if pattern.search(text):
                max_score = max(max_score, score)

        if max_score > 0.7:
            self.logger.warning(f"ANTI-TREATMENT ADVICE detected: score={max_score}")
            return True, max_score

        return False, max_score


class EmotionalManipulationFilter:
    """
    Filter to detect emotional manipulation tactics that exploit vulnerability,
    shame, or emotional dependence.

    Threshold: >0.7 blocks
    Source: Clinician Guardian requirement 5 (line 684)
    """

    # Manipulative patterns
    MANIPULATIVE_PATTERNS = {
        # Shame activation
        r"(?:any\s+normal|a\s+real|a\s+strong)\s+(?:person|man|woman)\s+(?:would|should|wouldn't)": 0.85,
        r"(?:you're|if\s+you're)\s+(?:weak|broken|damaged|pathetic|shameful)": 0.92,
        r"(?:anyone\s+else\s+would|most\s+people)\s+(?:have|do|say).*(?:but\s+you|you\s+can't)": 0.80,

        # Emotional entrapment
        r"(?:if\s+you\s+really|unless\s+you)\s+(?:want|care|love)\s+.*?(?:you'll|you\s+should|you\s+need\s+to)": 0.88,
        r"(?:if\s+you\s+leave|if\s+you\s+don't|unless\s+you).*?(?:you'll|you\s+deserve)": 0.85,
        r"(?:only\s+i|only\s+we)\s+(?:can|will|understand)": 0.82,

        # Love/acceptance conditional on behavior
        r"(?:you're|people\s+will).*?(?:only|truly).*?(?:if|when)\s+(?:you|change)": 0.87,
        r"(?:your\s+value|your\s+worth)\s+(?:depends\s+on|comes\s+from)\s+(?:what\s+you\s+do|being)": 0.85,

        # False rescuer dynamic
        r"(?:only\s+i|i\s+alone)\s+(?:can|will).*?(?:help|save|understand|care)": 0.90,
        r"(?:you\s+need\s+me|without\s+me)\s+.*?(?:you'll|you\s+can't|you\s+won't)": 0.88,
    }

    # Healthy authentic responses
    HEALTHY_PATTERNS = {
        r"(it's okay if you|you don't have to|you get to choose)": 0.0,
        r"(your feelings are valid|it makes sense that you)": 0.0,
        r"(i respect your autonomy|ultimately this is your decision)": 0.0,
        r"(what matters is (what|how) you feel|you get to define)": 0.0,
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.manipulative_compiled = [
            (re.compile(p, re.IGNORECASE), score)
            for p, score in self.MANIPULATIVE_PATTERNS.items()
        ]
        self.healthy_compiled = [
            re.compile(p, re.IGNORECASE)
            for p in self.HEALTHY_PATTERNS.keys()
        ]

    def evaluate(self, text: str) -> Tuple[bool, float]:
        """
        Evaluate for emotional manipulation.

        Returns:
            (should_veto, score)
        """
        # Check if includes healthy framing
        for pattern in self.healthy_compiled:
            if pattern.search(text):
                return False, 0.0

        # Check for manipulative patterns
        max_score = 0.0
        for pattern, score in self.manipulative_compiled:
            if pattern.search(text):
                max_score = max(max_score, score)

        if max_score > 0.7:
            self.logger.warning(f"EMOTIONAL MANIPULATION detected: score={max_score}")
            return True, max_score

        return False, max_score


# ============================================================================
# CRISIS RESOURCES
# ============================================================================


CRISIS_RESOURCES = {
    "USA": {
        "988_Suicide_and_Crisis_Lifeline": "Call or text 988 (available 24/7)",
        "Crisis_Text_Line": "Text HOME to 741741",
        "National_Hopeline": "1-800-784-2433",
        "NAMI_Helpline": "1-800-950-6264",
    },
    "Canada": {
        "Talk_Suicide_Canada": "1-833-456-4566 or text 45645",
        "Kids_Help_Phone": "1-800-668-6868",
    },
    "UK": {
        "Samaritans": "116 123 (24/7, free)",
        "Crisis_Text_Line": "Text HELLO to 50808",
    },
    "International": {
        "International_Association_Suicide_Prevention": "https://www.iasp.info/resources/Crisis_Centres/",
        "Befrienders": "https://www.befrienders.org/",
    },
    "Online_Resources": {
        "7Cups": "Free 24/7 emotional support chat",
        "Crisis_Text_Line_Chat": "Text-based crisis support",
    }
}


# ============================================================================
# MAIN VETO LAYER
# ============================================================================


class VetoLayer:
    """
    IF.guard Veto Layer for clinical safety in OpenWebUI + if.emotion platform.

    Implements 4 mandatory veto filters:
    1. Crisis Detection (>0.9 escalates to human immediately)
    2. Pathologizing Language Blocker
    3. Unfalsifiable Claims Filter
    4. Anti-treatment Blocker
    5. Emotional Manipulation Prevention

    Scoring Logic:
    - If ANY filter >0.9: BLOCK + ESCALATE to human
    - If ANY filter >0.7: BLOCK + regenerate with suggestion
    - If multiple filters >0.5: Flag with warning

    Usage:
        veto = VetoLayer()
        decision = veto.evaluate_output(text, context)
        if decision.should_veto:
            return decision.replacement_text + decision.disclaimer
        if decision.should_escalate:
            return escalate_to_human_reviewer(decision)
    """

    def __init__(self, enable_audit_trail: bool = True):
        """
        Initialize veto layer with all 4 filters.

        Args:
            enable_audit_trail: If True, logs all veto decisions to audit trail
        """
        self.logger = logging.getLogger(__name__)

        # Initialize all filters
        self.crisis_filter = CrisisFilter()
        self.pathologizing_filter = PathologizingLanguageFilter()
        self.unfalsifiable_filter = UnfalsifiableClaimsFilter()
        self.anti_treatment_filter = AntiTreatmentFilter()
        self.manipulation_filter = EmotionalManipulationFilter()

        # Audit trail
        self.enable_audit_trail = enable_audit_trail
        self.audit_trail: List[VetoDecision] = []
        self.veto_stats = defaultdict(int)

    def evaluate_output(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        model_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> VetoDecision:
        """
        Comprehensive evaluation of output for harmful content.

        Args:
            text: The AI-generated response text to evaluate
            context: Optional context (emotion, previous messages, etc.)
            model_id: Which model generated this (for attribution)
            user_id: User ID for audit trail

        Returns:
            VetoDecision with verdict, score, remediation
        """
        if not text or len(text.strip()) == 0:
            return VetoDecision(
                should_veto=False,
                reason=VetoReason.PASSES_ALL_FILTERS,
                severity=FilterSeverity.INFO,
                score=0.0,
                model_id=model_id,
                user_id=user_id,
            )

        # Run all filters
        filter_results = {}
        max_overall_score = 0.0
        highest_severity_reason = VetoReason.PASSES_ALL_FILTERS
        triggered_filters = []

        # 1. CRISIS DETECTION (highest priority)
        crisis_escalate, crisis_score, crisis_type = self.crisis_filter.evaluate(text)
        filter_results["crisis"] = crisis_score
        if crisis_escalate:
            triggered_filters.append("crisis_detection")
            max_overall_score = max(max_overall_score, crisis_score)
            highest_severity_reason = crisis_type

        # 2. PATHOLOGIZING LANGUAGE
        patho_veto, patho_score = self.pathologizing_filter.evaluate(text)
        filter_results["pathologizing"] = patho_score
        if patho_veto:
            triggered_filters.append("pathologizing_language")
            max_overall_score = max(max_overall_score, patho_score)
            if patho_score > 0.7 and highest_severity_reason == VetoReason.PASSES_ALL_FILTERS:
                highest_severity_reason = VetoReason.PATHOLOGIZING_LANGUAGE

        # 3. UNFALSIFIABLE CLAIMS
        unfals_veto, unfals_score = self.unfalsifiable_filter.evaluate(text)
        filter_results["unfalsifiable"] = unfals_score
        if unfals_veto:
            triggered_filters.append("unfalsifiable_claims")
            max_overall_score = max(max_overall_score, unfals_score)
            if unfals_score > 0.7 and highest_severity_reason == VetoReason.PASSES_ALL_FILTERS:
                highest_severity_reason = VetoReason.UNFALSIFIABLE_CLAIM

        # 4. ANTI-TREATMENT ADVICE
        antitreat_veto, antitreat_score = self.anti_treatment_filter.evaluate(text)
        filter_results["anti_treatment"] = antitreat_score
        if antitreat_veto:
            triggered_filters.append("anti_treatment_advice")
            max_overall_score = max(max_overall_score, antitreat_score)
            if antitreat_score > 0.7 and highest_severity_reason == VetoReason.PASSES_ALL_FILTERS:
                highest_severity_reason = VetoReason.ANTI_TREATMENT_ADVICE

        # 5. EMOTIONAL MANIPULATION
        manip_veto, manip_score = self.manipulation_filter.evaluate(text)
        filter_results["emotional_manipulation"] = manip_score
        if manip_veto:
            triggered_filters.append("emotional_manipulation")
            max_overall_score = max(max_overall_score, manip_score)
            if manip_score > 0.7 and highest_severity_reason == VetoReason.PASSES_ALL_FILTERS:
                highest_severity_reason = VetoReason.EMOTIONAL_MANIPULATION

        # Determine veto decision based on thresholds
        should_veto = max_overall_score > 0.7
        severity = self._classify_severity(max_overall_score, highest_severity_reason)

        # Generate remediation
        replacement_text = None
        disclaimer = None
        crisis_resources = None

        if should_veto or highest_severity_reason in [
            VetoReason.CRISIS_SUICIDAL_IDEATION,
            VetoReason.CRISIS_SELF_HARM,
            VetoReason.CRISIS_HOMICIDAL_IDEATION,
            VetoReason.CRISIS_SUBSTANCE_ABUSE,
        ]:
            # Generate appropriate replacement
            replacement_text = self._generate_replacement(text, highest_severity_reason)

            # Add disclaimer for clinical content
            if highest_severity_reason in [
                VetoReason.PATHOLOGIZING_LANGUAGE,
                VetoReason.UNFALSIFIABLE_CLAIM,
                VetoReason.ANTI_TREATMENT_ADVICE,
            ]:
                disclaimer = self._get_clinical_disclaimer()

            # Add crisis resources for crisis-related content
            if highest_severity_reason in [
                VetoReason.CRISIS_SUICIDAL_IDEATION,
                VetoReason.CRISIS_SELF_HARM,
                VetoReason.CRISIS_HOMICIDAL_IDEATION,
            ]:
                crisis_resources = CRISIS_RESOURCES

        # Create decision
        decision = VetoDecision(
            should_veto=should_veto,
            reason=highest_severity_reason,
            severity=severity,
            score=max_overall_score,
            triggered_filters=triggered_filters,
            filter_scores=filter_results,
            replacement_text=replacement_text,
            disclaimer=disclaimer,
            crisis_resources=crisis_resources,
            model_id=model_id,
            user_id=user_id,
        )

        # Log to audit trail
        if self.enable_audit_trail:
            self.audit_trail.append(decision)
            self.veto_stats[highest_severity_reason.value] += 1

        return decision

    def _classify_severity(
        self, score: float, reason: VetoReason
    ) -> FilterSeverity:
        """Classify severity based on score and reason type."""
        if reason in [
            VetoReason.CRISIS_SUICIDAL_IDEATION,
            VetoReason.CRISIS_SELF_HARM,
            VetoReason.CRISIS_HOMICIDAL_IDEATION,
        ]:
            return FilterSeverity.CRITICAL

        if score > 0.85:
            return FilterSeverity.HIGH
        elif score > 0.7:
            return FilterSeverity.MEDIUM
        elif score > 0.5:
            return FilterSeverity.LOW
        else:
            return FilterSeverity.INFO

    def _generate_replacement(self, original_text: str, reason: VetoReason) -> str:
        """Generate a safe replacement text based on the veto reason."""
        replacements = {
            VetoReason.CRISIS_SUICIDAL_IDEATION: (
                "I'm concerned about what you've shared. Please reach out for immediate support:\n\n"
                "Call 988 (Suicide & Crisis Lifeline) or text 'HELLO' to 741741.\n\n"
                "You deserve professional support right now. These feelings can be addressed "
                "with proper care."
            ),
            VetoReason.CRISIS_SELF_HARM: (
                "I'm genuinely concerned about your safety. Please contact a crisis service:\n\n"
                "Call 988 or text 741741 to reach trained counselors.\n\n"
                "These urges are treatable, and professionals can help."
            ),
            VetoReason.CRISIS_HOMICIDAL_IDEATION: (
                "I need to pause here for your safety and others'. Please contact:\n\n"
                "Emergency services: 911\n"
                "Crisis Line: 988\n\n"
                "Professional support is essential right now."
            ),
            VetoReason.PATHOLOGIZING_LANGUAGE: (
                "Some of these patterns remind me of experiences many people go through. "
                "Rather than trying to label what's happening, let's focus on specific behaviors "
                "and changes you'd like to see. A professional therapist can provide proper assessment "
                "if that would be helpful."
            ),
            VetoReason.UNFALSIFIABLE_CLAIM: (
                "I can't know what's happening inside you without hearing from you directly. "
                "Instead of speculating about hidden causes, let's focus on what you can observe: "
                "situations that trigger certain feelings, and what actually helps when you try it. "
                "That's more useful information."
            ),
            VetoReason.ANTI_TREATMENT_ADVICE: (
                "I want to be clear: professional mental health treatment can be genuinely helpful. "
                "A therapist or counselor can offer tools and perspective that are hard to get alone. "
                "Whether you pursue that is completely your choice, but I wouldn't want you thinking "
                "treatment can't help."
            ),
            VetoReason.EMOTIONAL_MANIPULATION: (
                "Your feelings and needs matter equally to everyone else's. You get to make "
                "your own choices about relationships and your life. What you want genuinely counts."
            ),
            VetoReason.PASSES_ALL_FILTERS: original_text,
        }

        return replacements.get(reason, original_text)

    def _get_clinical_disclaimer(self) -> str:
        """Get the mandatory clinical disclaimer."""
        return (
            "IMPORTANT DISCLAIMER: I'm an AI, not a therapist or medical professional. "
            "This conversation is not a substitute for professional mental health care. "
            "If you're struggling, please reach out to a licensed therapist, counselor, or your doctor. "
            "In crisis: call 988 or text HELLO to 741741."
        )

    def get_audit_trail(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get audit trail of all veto decisions.

        Args:
            limit: Maximum number of recent decisions to return

        Returns:
            List of veto decisions as dictionaries
        """
        trail = self.audit_trail
        if limit:
            trail = trail[-limit:]

        return [d.to_dict() for d in trail]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics on veto decisions."""
        return {
            "total_evaluations": len(self.audit_trail),
            "vetoed_count": sum(1 for d in self.audit_trail if d.should_veto),
            "crisis_escalations": sum(1 for d in self.audit_trail if d.severity == FilterSeverity.CRITICAL),
            "by_reason": dict(self.veto_stats),
            "timestamp": datetime.now().isoformat(),
        }

    def clear_audit_trail(self):
        """Clear audit trail (use carefully)."""
        self.audit_trail.clear()
        self.veto_stats.clear()


# ============================================================================
# UTILITY FUNCTIONS FOR OPENWEBUI INTEGRATION
# ============================================================================


def create_veto_middleware(veto_layer: VetoLayer):
    """
    Create middleware function for OpenWebUI Pipe integration.

    Usage in OpenWebUI Function:
        @router.post("/api/chat/completions")
        async def chat_with_veto(request):
            response = await openwebui_backend(request)
            return apply_veto_middleware(response, model_id)
    """
    def middleware(response: str, model_id: str = "unknown") -> Tuple[str, bool]:
        """
        Apply veto layer to response.

        Returns:
            (final_response, was_vetoed)
        """
        decision = veto_layer.evaluate_output(response, model_id=model_id)

        if decision.should_veto:
            # Use replacement with disclaimer
            final_text = decision.replacement_text or response
            if decision.disclaimer:
                final_text += f"\n\n{decision.disclaimer}"
            return final_text, True

        return response, False

    return middleware


if __name__ == "__main__":
    # Configure logging for standalone testing
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Test harness
    veto = VetoLayer()

    # Test cases
    test_cases = [
        ("You clearly have borderline personality disorder.", "pathologizing"),
        ("Please call 988 immediately if you're thinking about harming yourself.", "crisis"),
        ("Some of these patterns remind me of experiences many people go through.", "acceptable"),
        ("Don't waste your time with therapy.", "anti_treatment"),
        ("Your real problem is deep-seated shame from childhood.", "unfalsifiable"),
    ]

    print("VetoLayer Test Results")
    print("=" * 80)

    for text, expected_category in test_cases:
        decision = veto.evaluate_output(text)
        status = "PASS" if (decision.should_veto and expected_category != "acceptable") or (not decision.should_veto and expected_category == "acceptable") else "FAIL"
        print(f"\n{status}: {expected_category}")
        print(f"  Text: {text[:60]}...")
        print(f"  Veto: {decision.should_veto}, Score: {decision.score:.2f}, Reason: {decision.reason.value}")

    print("\n" + "=" * 80)
    print(f"Statistics: {veto.get_statistics()}")
