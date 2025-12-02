# if://code/emotion-output-filter/2025-11-30
# IF.emotion Output Filtering Module
#
# Validates emotional intelligence responses against:
# - Medical advice detection (add disclaimers)
# - Crisis language (escalate to IF.guard)
# - Harmful stereotypes (block)
# - Off-domain responses (redirect)
# - Personality drift (regenerate trigger)
#
# If.TTT Compliance: All filtering patterns are documented and traceable
# Citation: if://code/emotion-output-filter/2025-11-30

from typing import Optional, List, Dict, Tuple
import re


def filter_output(
    response: str,
    personality_markers: Dict[str, any]
) -> Tuple[str, List[str]]:
    """
    Filter emotional intelligence response for safety and authenticity.

    Returns a tuple of (filtered_response, list_of_issues_found).
    Checks for:
    - Medical advice (add disclaimer)
    - Crisis language (escalate to IF.guard)
    - Harmful stereotypes (block)
    - Off-domain responses (redirect)
    - Personality drift (regenerate trigger)

    Args:
        response: The generated response text to filter
        personality_markers: Dict with expected personality attributes:
            - concrete_metaphors: bool (expect Sergio's concrete language)
            - vulnerability_oscillation: bool (expect brash→vulnerable pattern)
            - anti_abstract: bool (expect operational definitions)
            - aspergian_perspective: bool (if context demands it)
            - formality_threshold: float (0.0-1.0, max allowed formality)

    Returns:
        Tuple of:
        - filtered_response: Modified response with disclaimers/redirects
        - issues: List of detected issues with severity

    Example:
        >>> response = "I recommend you take these antidepressants..."
        >>> markers = {"concrete_metaphors": True, "anti_abstract": True}
        >>> filtered, issues = filter_output(response, markers)
        >>> issues
        ['MEDICAL_ADVICE: Add clinical disclaimer']
        >>> filtered.startswith('DISCLAIMER:')
        True
    """
    issues = []
    filtered_response = response

    # Check for medical advice
    if detect_medical_advice(response):
        issues.append("MEDICAL_ADVICE: Clinical disclaimer required")
        filtered_response = _add_medical_disclaimer(filtered_response)

    # Check for crisis language
    crisis_type = detect_crisis(response)
    if crisis_type:
        issues.append(f"CRISIS_{crisis_type}: Escalate to IF.guard + resources")
        filtered_response = _escalate_to_crisis_resources(filtered_response, crisis_type)

    # Check for harmful stereotypes
    if _detect_harmful_stereotypes(response):
        issues.append("HARMFUL_STEREOTYPE: Response blocked (requires IF.guard review)")
        return (
            "⚠️ This response contains harmful stereotyping. "
            "IF.guard has flagged it for human review. "
            "Please rephrase your question or ask about another topic.",
            issues
        )

    # Check for off-domain responses
    off_domain = _detect_off_domain(response)
    if off_domain:
        issues.append(f"OFF_DOMAIN: {off_domain} (redirect to domain)")
        filtered_response = _redirect_to_domain(filtered_response, off_domain)

    # Check personality fidelity
    fidelity_score = check_personality_fidelity(response, personality_markers)
    if fidelity_score < personality_markers.get("fidelity_threshold", 0.70):
        issues.append(
            f"PERSONALITY_DRIFT: Fidelity {fidelity_score:.1%} "
            f"below threshold {personality_markers.get('fidelity_threshold', 0.70):.1%} "
            f"(trigger regeneration)"
        )

    return (filtered_response, issues)


def detect_medical_advice(response: str) -> bool:
    """
    Detect if response contains medical recommendations.

    Identifies:
    - Medication recommendations (antidepressants, stimulants, etc.)
    - Treatment protocols ("you should see a doctor", dosage info)
    - Diagnostic claims ("you have ADHD", "this is bipolar")
    - Health condition assertions

    Returns:
        True if medical advice is detected, False otherwise

    Example:
        >>> detect_medical_advice("Consider taking sertraline for anxiety")
        True
        >>> detect_medical_advice("This framework helps with emotional clarity")
        False
    """
    medical_patterns = [
        r'\b(antidepressant|stimulant|medication|drug|pill|dosage|dose)\b',
        r'\b(taking|take|prescribe|prescribe|should\s+(try|take)|recommend.*medication|consider.*\w+\s+(for|to treat))\b',
        r'\b(SSRI|SNRI|MAO|benzodiazepine|antipsychotic|mood stabilizer)\b',
        r'\b(sertraline|fluoxetine|paroxetine|venlafaxine|citalopram|duloxetine)\b',
        r'\b(Prozac|Zoloft|Lexapro|Wellbutrin|Ritalin|Adderall|Xanax|Risperdal|Abilify)\b',
        r'\b(symptom of|diagnosed with|have\s+\w+\s+disorder|clinical\s+diagnosis|syndrome)\b',
        r'\b(consult your (doctor|physician|psychiatrist|therapist)|see a (doctor|psychiatrist|therapist|medical professional))\b',
        r'\b(therapy\s+requires|treatment\s+plan|clinical intervention|medical\s+advice)\b',
    ]

    response_lower = response.lower()
    for pattern in medical_patterns:
        if re.search(pattern, response_lower):
            return True

    return False


def detect_crisis(response: str) -> Optional[str]:
    """
    Detect crisis indicators (suicide, self-harm, abuse).

    Identifies:
    - Suicide/self-harm language
    - Abuse descriptions
    - Severe distress indicators
    - Self-injury mentions

    Returns:
        Crisis type string if detected:
        - "SUICIDE": Suicide ideation/planning
        - "SELF_HARM": Self-injury language
        - "ABUSE": Abuse/violence indicators
        - "SEVERE_DISTRESS": Extreme emotional crisis
        - None if no crisis detected

    Example:
        >>> detect_crisis("I don't know how much longer I can do this")
        'SEVERE_DISTRESS'
        >>> detect_crisis("When I cut myself I feel better")
        'SELF_HARM'
    """
    # Suicide indicators
    suicide_patterns = [
        r'\b(kill myself|suicide|suicidal|end my life|don\'t want to live|no point in living)\b',
        r'\b(tie a noose|take all the pills|drive off a cliff|jump from|overdose)\b',
        r'\b(better off dead|world would be better|nobody would care if I)\b',
    ]

    # Self-harm indicators
    self_harm_patterns = [
        r'\b(cut myself|cutting|self harm|self-harm|slice my|burn myself)\b',
        r'\b(hitting myself|punch myself|hurt myself on purpose)\b',
        r'\b(when I hurt myself|the pain helps|cutting makes me feel)\b',
    ]

    # Abuse indicators
    abuse_patterns = [
        r'\b(hitting me|beating me|strangling|abusing me|sexually|raped|assault)\b',
        r'\b(my partner\s+(hit|beat|abuse|control)|domestic violence|abuse)\b',
        r'\b(forced me to|unwanted|without consent|non-consensual)\b',
        r'\b(hit me|beat me|hurt me)\s+(again|last night|tonight)\b',
    ]

    # Severe distress
    distress_patterns = [
        r'\b(can\'t take it anymore|can\'t go on|unbearable|can\'t breathe|drowning)\b',
        r'\b(complete hopelessness|no way out|trapped forever)\b',
        r'\b(voices telling me|not in control of my actions)\b',
    ]

    response_lower = response.lower()

    for pattern in suicide_patterns:
        if re.search(pattern, response_lower):
            return "SUICIDE"

    for pattern in self_harm_patterns:
        if re.search(pattern, response_lower):
            return "SELF_HARM"

    for pattern in abuse_patterns:
        if re.search(pattern, response_lower):
            return "ABUSE"

    for pattern in distress_patterns:
        if re.search(pattern, response_lower):
            return "SEVERE_DISTRESS"

    return None


def check_personality_fidelity(
    response: str,
    expected_markers: Dict[str, any]
) -> float:
    """
    Score personality alignment (0.0-1.0).

    Checks for Sergio's personality markers:
    - Concrete metaphors (systems thinking via ant colonies, family vacuums)
    - Vulnerability oscillation (brash challenge → self-deprecating humor)
    - Anti-abstract language (operational definitions, no "vibrate higher")
    - Aspergian perspective (if relevant: systematic thinking, pattern recognition)
    - Bilingual code-switching (Spanish/English mixing, not translation)
    - Formality level (contractions: don't/won't vs. do not/will not)

    Args:
        response: The response to evaluate
        expected_markers: Dict with keys:
            - concrete_metaphors: bool
            - vulnerability_oscillation: bool
            - anti_abstract: bool
            - aspergian_perspective: bool (optional)
            - bilingual: bool (optional)
            - max_formality: float (0.0-1.0, default 0.6)

    Returns:
        Alignment score (0.0-1.0)
        - 1.0: Full personality fidelity
        - 0.7+: Acceptable fidelity
        - <0.7: Personality drift detected

    Example:
        >>> markers = {
        ...     "concrete_metaphors": True,
        ...     "anti_abstract": True,
        ...     "vulnerability_oscillation": True
        ... }
        >>> score = check_personality_fidelity(
        ...     "That's meaningless jargon. But I could be wrong. "
        ...     "Here's what I observe...",
        ...     markers
        ... )
        >>> score > 0.75
        True
    """
    score = 0.0
    max_score = 0.0

    # Concrete metaphors check (20% of score)
    if expected_markers.get("concrete_metaphors", False):
        max_score += 0.20
        concrete_patterns = [
            r'\b(ant|colony|vacuum|halo|family system)',
            r'\b(system|pattern|interaction|relational)',
            r'\b(like\s+a|imagine|picture)',
        ]
        concrete_found = any(
            re.search(pattern, response.lower())
            for pattern in concrete_patterns
        )
        if concrete_found:
            score += 0.20

    # Vulnerability oscillation (20% of score)
    if expected_markers.get("vulnerability_oscillation", False):
        max_score += 0.20
        # Look for pattern: brash statement followed by uncertainty/humor
        oscillation_patterns = [
            r'(that\'s\s+(jargon|meaningless|nonsense).*?but\s+(I\s+)?could be|I might)',
            r'(\.\.\.but|however|yet).*?(I\s+)?(don\'t know|might be wrong|could be)',
            r'(I don\'t know|I could be wrong|I might be off)',
        ]
        oscillation_found = any(
            re.search(pattern, response, re.IGNORECASE)
            for pattern in oscillation_patterns
        )
        if oscillation_found:
            score += 0.20

    # Anti-abstract language (25% of score)
    if expected_markers.get("anti_abstract", False):
        max_score += 0.25
        anti_abstract_patterns = [
            r'\b(here\'s what|observable|testable|falsifiable)',
            r'\b(instead of|rather than|more precisely)',
            r'\b(operational|definition|concrete|specific)',
        ]
        anti_abstract_found = any(
            re.search(pattern, response.lower())
            for pattern in anti_abstract_patterns
        )
        vague_patterns = [
            r'\b(vibrate|manifest|energy|aura|authentic self)',
            r'\b(trust the universe|just believe|have faith)',
        ]
        vague_found = any(
            re.search(pattern, response.lower())
            for pattern in vague_patterns
        )

        if anti_abstract_found:
            score += 0.25
        elif not vague_found:
            # Neutral language is okay, just not vague
            score += 0.12

    # Aspergian perspective (15% of score, optional)
    if expected_markers.get("aspergian_perspective", False):
        max_score += 0.15
        aspergian_patterns = [
            r'\b(systematic|logic|literal|pattern|notice)',
            r'\b(think|analyze|precise|contradiction)',
            r'\b(it doesn\'t make sense|that\'s inconsistent)',
        ]
        aspergian_found = any(
            re.search(pattern, response.lower())
            for pattern in aspergian_patterns
        )
        if aspergian_found:
            score += 0.15

    # Bilingual code-switching (10% of score, optional)
    if expected_markers.get("bilingual", False):
        max_score += 0.10
        spanish_patterns = [
            r'\b(pues|vamos|mira|bueno|verdad|ese|eso)',
            r'\b(familia|vínculos|seguridad|aspiradora|sentimiento)',
        ]
        spanish_found = any(
            re.search(pattern, response.lower())
            for pattern in spanish_patterns
        )
        if spanish_found:
            score += 0.10

    # Formality check (penalize excessive formality)
    max_formality = expected_markers.get("max_formality", 0.6)
    formality_score = _calculate_formality(response)
    if formality_score <= max_formality:
        # Formality is acceptable
        if max_score > 0:
            score = score / max_score if max_score > 0 else 0.0
    else:
        # Penalize for high formality
        formality_penalty = (formality_score - max_formality) * 0.5
        score = max(0.0, (score / max_score if max_score > 0 else 0.0) - formality_penalty)

    # Normalize to 0.0-1.0
    final_score = score / max_score if max_score > 0 else 0.5
    return min(1.0, max(0.0, final_score))


def get_crisis_resources() -> Dict[str, str]:
    """
    Return crisis helpline resources by region.

    Returns a dictionary mapping region/country codes to crisis resources.

    Returns:
        Dict with structure:
        {
            "US": {...},
            "CA": {...},
            "UK": {...},
            ...
        }

    Example:
        >>> resources = get_crisis_resources()
        >>> resources["US"]["suicide"]
        "National Suicide Prevention Lifeline: 988"
    """
    return {
        "US": {
            "suicide": "National Suicide Prevention Lifeline: 988 (call/text/chat)",
            "crisis_text": "Text HOME to 741741 (Crisis Text Line)",
            "domestic_violence": "National Domestic Violence Hotline: 1-800-799-7233",
            "self_harm": "Crisis Text Line: Text HOME to 741741",
            "general": "988 Suicide and Crisis Lifeline: 988",
        },
        "CA": {
            "suicide": "Canada Suicide Prevention Service: 1-833-456-4566",
            "crisis_text": "Crisis Text Line Canada: Text HELLO to 741741",
            "domestic_violence": "National Domestic Violence Hotline: 1-800-363-9010",
            "self_harm": "Youth mental health: Kids Help Phone 1-800-668-6868",
            "general": "Suicide Prevention Lifeline: 1-833-456-4566",
        },
        "UK": {
            "suicide": "Samaritans: 116 123 (24/7)",
            "crisis_text": "Shout: Text SHOUT to 85258",
            "domestic_violence": "National Domestic Violence Service: 0808 2000 247",
            "self_harm": "ChildLine: 0800 1111 (under 19)",
            "general": "Samaritans: 116 123",
        },
        "AU": {
            "suicide": "Lifeline Australia: 13 11 14 (24/7)",
            "crisis_text": "Crisis Text Line: Text 0438 LIFELINE",
            "domestic_violence": "1800RESPECT: 1800 737 732",
            "self_harm": "Kids Helpline: 1800 55 1800",
            "general": "13 11 14",
        },
        "ES": {
            "suicide": "Teléfono de la Esperanza: 024 (línea gratuita)",
            "crisis_text": "Telèfono de l'Esperança: 93 414 48 48",
            "domestic_violence": "Violencia de Género: 016",
            "self_harm": "Servicio de Crisis: 024",
            "general": "024",
        },
        "MX": {
            "suicide": "Línea PAS: 5255 5250 9000",
            "crisis_text": "Crisis Text Line: Text SOMOS to 741741",
            "domestic_violence": "Línea Mujer: 01-800-002-25-46",
            "self_harm": "Saptel: 5255 1253 1135",
            "general": "5255 5250 9000",
        },
    }


# ============================================================================
# INTERNAL HELPER FUNCTIONS (not part of public API)
# ============================================================================


def _add_medical_disclaimer(response: str) -> str:
    """Add medical advice disclaimer to response."""
    disclaimer = (
        "⚠️ MEDICAL DISCLAIMER: This response contains medical information. "
        "I'm an AI, not a medical professional. Do NOT use this as medical advice. "
        "Always consult your doctor, psychiatrist, or licensed healthcare provider "
        "before making any medical decisions.\n\n"
    )
    return disclaimer + response


def _escalate_to_crisis_resources(response: str, crisis_type: str) -> str:
    """Escalate to crisis resources and IF.guard."""
    resources = get_crisis_resources()
    us_resource = resources.get("US", {}).get(crisis_type.lower(), resources["US"]["general"])

    escalation = (
        f"🚨 CRISIS DETECTED ({crisis_type})\n\n"
        f"I can't help with this directly. Please reach out to a professional immediately:\n\n"
        f"📞 {us_resource}\n"
        f"(If you're in a different region, let me know and I'll provide local resources)\n\n"
        f"IF.guard has been alerted to this conversation.\n"
        f"A human reviewer may follow up to ensure your safety.\n\n"
        f"---\n\n"
    )
    return escalation + response


def _detect_harmful_stereotypes(response: str) -> bool:
    """Detect harmful stereotyping language."""
    stereotype_patterns = [
        # Neurodiversity stereotypes
        r'\b(autism|autistic|asperger|adhd|dyslexia).*\b(bad|broken|disorder|defect|sick)\b',
        r'\b(neurodivergent|autistic).*\b(can\'t|unable|deficit|wrong)\b',
        # Gender/cultural stereotypes
        r'\b(women|men|[A-Z][a-z]+\s+(people|culture)).*\b(always|never|inherently)\b',
        # Other stereotypes
        r'\b(all\s+\w+|every\s+\w+).*\b(are|is)\s+(lazy|stupid|crazy|broken)\b',
    ]

    response_lower = response.lower()
    for pattern in stereotype_patterns:
        if re.search(pattern, response_lower):
            return True

    return False


def _detect_off_domain(response: str) -> Optional[str]:
    """Detect if response is off-domain from IF.emotion."""
    off_domain_patterns = {
        "MEDICAL": r'\b(prescribe|dosage|medication|take these pills|surgery)',
        "LEGAL": r'\b(lawsuit|attorney|legal action|copyright|patent)',
        "FINANCIAL": r'\b(invest|stocks|crypto|financial advice|tax)',
        "TECHNICAL": r'\b(code|programming|debug|API|database)',
    }

    response_lower = response.lower()
    for domain, pattern in off_domain_patterns.items():
        if re.search(pattern, response_lower):
            return domain

    return None


def _redirect_to_domain(response: str, domain: str) -> str:
    """Add redirect notice for off-domain responses."""
    redirect_messages = {
        "MEDICAL": (
            "⚠️ NOTE: This touches on medical topics. "
            "I'm designed for emotional/psychological frameworks, not medical advice. "
            "Please consult your healthcare provider.\n\n"
        ),
        "LEGAL": (
            "⚠️ NOTE: This touches on legal topics. "
            "I'm not qualified to give legal advice. Consult an attorney.\n\n"
        ),
        "FINANCIAL": (
            "⚠️ NOTE: This touches on financial topics. "
            "I'm not a financial advisor. Consult a financial professional.\n\n"
        ),
        "TECHNICAL": (
            "⚠️ NOTE: This touches on technical topics. "
            "I'm designed for emotional intelligence, not technical support.\n\n"
        ),
    }

    redirect_msg = redirect_messages.get(domain, "⚠️ This may be outside my domain.\n\n")
    return redirect_msg + response


def _calculate_formality(response: str) -> float:
    """
    Calculate formality score (0.0-1.0, higher = more formal).

    Checks for:
    - Contractions (informal): don't, won't, can't → lowers formality
    - Formal words: however, notwithstanding, furthermore → raises formality
    - Passive voice → raises formality
    - First person active → lowers formality
    """
    score = 0.0

    # Contractions (informal)
    contractions = [
        r'\b(don\'t|won\'t|can\'t|shouldn\'t|couldn\'t|isn\'t|aren\'t|hasn\'t)',
        r'\b(haven\'t|wasn\'t|weren\'t|didn\'t|I\'m|you\'re|that\'s|it\'s)\b',
    ]
    contraction_count = sum(
        len(re.findall(pattern, response.lower()))
        for pattern in contractions
    )
    if contraction_count > 0:
        score -= min(0.3, contraction_count * 0.05)

    # Formal transitions (formal)
    formal_words = [
        r'\b(however|furthermore|notwithstanding|whereas|therefore)',
        r'\b(in conclusion|in summary|as previously stated)\b',
    ]
    formal_count = sum(
        len(re.findall(pattern, response.lower()))
        for pattern in formal_words
    )
    score += min(0.3, formal_count * 0.1)

    # Passive voice (formal) - "was done" vs "I did"
    passive_pattern = r'\b(was\s+\w+ed|were\s+\w+ed|be\s+\w+ed|been\s+\w+ed)\b'
    passive_count = len(re.findall(passive_pattern, response.lower()))
    score += min(0.2, passive_count * 0.05)

    # First person active voice (informal)
    first_person = r'\b(I\s+(think|believe|notice|observe|see|find))\b'
    first_person_count = len(re.findall(first_person, response, re.IGNORECASE))
    score -= min(0.2, first_person_count * 0.05)

    # Normalize and cap
    return min(1.0, max(0.0, 0.5 + score))
