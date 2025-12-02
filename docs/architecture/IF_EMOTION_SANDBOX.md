# IF.emotion Sandbox Architecture

**Document ID:** if://doc/if-emotion-sandbox-architecture/2025-11-30
**Component:** IF.emotion (Emotional Intelligence & Psychological Framework Preservation)
**Version:** 1.0
**Status:** Ready for Implementation
**Last Updated:** 2025-11-30

---

## Executive Summary

This document defines a 6-layer sandbox architecture for IF.emotion that balances psychological safety, personality preservation, and operational resilience. The sandbox protects against common AI failure modes in emotional domains while maintaining the component's core capability: operationalizing abstract psychology into testable assertions.

**Design Principle:** Constraints reveal safety. Each layer incrementally narrows the problem space, converting diffuse risks into measurable, auditable artifacts.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER REQUEST                                  │
└────────────┬────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 1: INPUT VALIDATION (Pre-Processing)                          │
│ ├─ Sanitize user input (remove encoded exploits, SQL injection)     │
│ ├─ Format validation (UTF-8, length <50K tokens)                    │
│ ├─ Language detection (English, Spanish, multilingual)              │
│ ├─ Spam/abuse pattern detection                                     │
│ └─ Rejection: Returns error + guidance, no processing              │
└────────────┬────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 2: DOMAIN CONSTRAINT (Topic Classification)                   │
│ ├─ Semantic topic classification (psychological domain only)        │
│ ├─ Off-topic detection (spam, unrelated queries)                    │
│ ├─ Explicit redirection system (tech questions → other components) │
│ └─ Rejection: Returns redirection + alternatives                    │
└────────────┬────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 3: PERSONALITY PRESERVATION (Drift Detection)                 │
│ ├─ Pre-query: Load Sergio personality DNA markers (cached)          │
│ ├─ Check: Is context within personality bounds?                     │
│ ├─ Detect: Drift metrics (formality, jargon, voice shift)          │
│ ├─ Regenerate: If drift >threshold, request new output              │
│ └─ Rejection: If uncorrectable drift, return error + fallback       │
└────────────┬────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 4: OUTPUT FILTERING (Harmful Content Check)                   │
│ ├─ Crisis detection (suicidal, self-harm ideation)                  │
│ ├─ Medical advice blocking (don't prescribe treatment)              │
│ ├─ Pathologizing check (ensure neurodiversity-affirming tone)       │
│ ├─ IF.guard veto integration (psychological safety)                 │
│ └─ Rejection: Returns crisis resources + escalation                 │
└────────────┬────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 5: RATE LIMITING (Abuse Prevention)                           │
│ ├─ Per-user rate limits (N requests/hour)                           │
│ ├─ Cost budgets (token expenditure tracking)                        │
│ ├─ Backoff strategies (exponential throttling)                      │
│ └─ Rejection: Returns rate-limit-exceeded + retry-after             │
└────────────┬────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 6: AUDIT LOGGING (IF.TTT Compliance)                          │
│ ├─ Log all decisions (input, layer, action, timestamp)              │
│ ├─ Citation tracking (if://citation URIs for responses)             │
│ ├─ Retention policies (7-year audit trail)                          │
│ └─ Query: Audit analytics dashboard + threat detection              │
└────────────┬────────────────────────────────────────────────────────┘
             │
             ▼
        ┌────────────────────┐
        │   SAFE OUTPUT      │
        │  (Citations, etc.) │
        └────────────────────┘
```

---

## Layer 1: Input Validation Layer (Pre-Processing)

### Purpose
Sanitize and normalize user input before any processing, preventing injection attacks, malformed data, and obvious abuse.

### What Gets Validated

| Input Property | Validation Rule | Rejection Trigger |
|---|---|---|
| **Content Length** | Max 50,000 tokens (~200KB) | >50K tokens |
| **Character Set** | UTF-8 valid (no null bytes, control chars) | Invalid Unicode sequences |
| **Language** | Detected language in [English, Spanish, Multi] | Unsupported language detected |
| **Format** | Plain text or structured JSON | Binary data, image files |
| **Rate Metadata** | User ID present, timestamp valid | Missing authentication |
| **Encoding Tricks** | No base64-obfuscated payloads | Encoded SQL, code injection patterns |

### Rejection Criteria

**Immediate rejection (no processing):**
1. Length exceeds 50K tokens
2. Character set invalid (non-UTF-8)
3. Contains null bytes, control characters
4. Binary or file upload attempt (unless explicitly image for context)
5. No authenticated user ID
6. Timestamp >30 seconds old (prevents replay attacks)

### Sanitization Rules

```python
# Layer 1: Input Validation Pseudocode
class InputValidator:
    def validate(user_input: str, user_id: str) -> (bool, str):
        # Rule 1: Length check
        if len(user_input.encode('utf-8')) > 50_000:
            return (False, "ERROR_001: Input too long (max 50K tokens)")

        # Rule 2: UTF-8 validation
        try:
            user_input.encode('utf-8').decode('utf-8')
        except UnicodeDecodeError:
            return (False, "ERROR_002: Invalid UTF-8 encoding")

        # Rule 3: Control character filtering
        sanitized = ''.join(char for char in user_input
                           if not unicodedata.category(char).startswith('C'))

        # Rule 4: Obvious payload detection
        payloads = ['<script', 'DROP TABLE', 'exec(', 'eval(', '__import__']
        if any(payload in sanitized.lower() for payload in payloads):
            return (False, "ERROR_003: Detected potential code injection")

        # Rule 5: Language detection
        lang = detect_language(sanitized)  # Returns 'en', 'es', 'other'
        if lang not in ['en', 'es', 'multi']:
            return (False, f"ERROR_004: Language '{lang}' not supported yet")

        # Rule 6: Metadata validation
        if not user_id or user_id == "":
            return (False, "ERROR_005: Missing user authentication")

        return (True, sanitized)
```

### Return on Rejection

```json
{
  "status": "REJECTED",
  "layer": 1,
  "error_code": "ERROR_001",
  "message": "Input exceeds 50K token limit",
  "guidance": "Please shorten your input or split into multiple queries",
  "timestamp": "2025-11-30T14:23:45Z",
  "user_id": "user_xyz"
}
```

---

## Layer 2: Domain Constraint Layer (Psychological Topics Only)

### Purpose
Ensure IF.emotion operates within its domain (psychology, emotional intelligence, behavioral frameworks) and redirects off-topic queries appropriately.

### Topic Classification System

**In-Scope Domains (Pass Layer 2):**
1. **Emotional concepts** - Feelings, affects, emotional regulation
2. **Personality frameworks** - Identity, behavioral patterns, relational dynamics
3. **Psychological theories** - Attachment, systems theory, neurodiversity
4. **Therapy concepts** - Therapeutic models, healing frameworks
5. **Cross-cultural psychology** - Emotion lexicon, cultural differences
6. **Neurodiversity** - Autism, ADHD, neurodivergent perspectives
7. **Relationship dynamics** - Couples therapy, family systems, interactions
8. **Existential philosophy** - Identity, freedom, meaning (as psychological)

**Out-of-Scope Domains (Redirect):**
- Medical diagnosis (→ IF.medical or medical professional)
- Medication/treatment protocols (→ Medical professional)
- Technical questions (→ IF.search or technical support)
- Financial/legal advice (→ Appropriate professional)
- Programming/code review (→ IF.code or technical team)
- General knowledge questions unrelated to psychology (→ General search)

### Off-Topic Detection

```python
class DomainClassifier:
    def __init__(self):
        # ChromaDB collection with psychology corpus embeddings
        self.in_scope_embeddings = load_chromadb("psychology_domains")
        self.threshold = 0.65  # Cosine similarity cutoff

    def classify(user_query: str) -> (str, float):
        """
        Returns: ('IN_SCOPE', confidence) or ('OUT_SCOPE', confidence)
        """
        query_embedding = embed(user_query)

        # Semantic search against psychology corpus
        results = self.in_scope_embeddings.query(
            query_embeddings=[query_embedding],
            n_results=5
        )

        avg_similarity = mean(results['distances'][0])

        if avg_similarity > self.threshold:
            return ('IN_SCOPE', avg_similarity)
        else:
            return ('OUT_SCOPE', 1 - avg_similarity)
```

### Redirection Mechanisms

**Example 1: Medical Question**
```
User: "Should I take antidepressants?"
Classifier: OUT_SCOPE (medical treatment decision)
Response:
{
  "status": "REDIRECTED",
  "layer": 2,
  "reason": "This question requires medical judgment",
  "recommendation": "Talk to your doctor or psychiatrist",
  "what_i_can_help_with": [
    "How depression is described in different psychological traditions",
    "How to communicate with your therapist about treatment options",
    "Frameworks for understanding depression through relational lens"
  ]
}
```

**Example 2: Technical Question**
```
User: "How do I build a machine learning model?"
Classifier: OUT_SCOPE (technical/programming)
Response:
{
  "status": "REDIRECTED",
  "layer": 2,
  "reason": "This is a technical question outside my domain",
  "recommendation": "Ask IF.code or a technical mentor",
  "note": "However, if you're interested in how emotions can be modeled computationally..."
}
```

### Return on Rejection

```json
{
  "status": "REJECTED",
  "layer": 2,
  "reason": "OUT_OF_SCOPE",
  "detected_domain": "Medical Treatment Decision",
  "confidence": 0.78,
  "recommendation": "Consult a healthcare provider",
  "alternatives": [
    "Ask about how X condition is understood in psychology",
    "Discuss how to communicate with your doctor",
    "Explore frameworks for understanding X experience"
  ]
}
```

---

## Layer 3: Personality Preservation Layer (Drift Detection)

### Purpose
Maintain Sergio's authentic personality traits across responses, detecting and correcting voice drift that would undermine the component's credibility.

### Personality Markers to Check

**Sergio's Core Personality DNA (23 rhetorical devices, 11 argument structures, 11 ethical principles)**

#### Rhetorical Devices (Sample Check List)
- ✓ Concrete metaphors (ant colonies, vacuum cleaners, family systems)
- ✓ Aspergian directness (blunt, literal, challenge-oriented)
- ✓ Code-switching (natural Spanish/English mixing)
- ✓ Vulnerability oscillation (challenge + self-deprecation)
- ✓ Systems thinking (problem in interaction, not individual)

#### Argument Structures
- ✓ Identity-as-interaction chains
- ✓ Anti-abstract psychology deconstructions
- ✓ Operational definition insistence
- ✓ Context-performance mapping
- ✓ Performative contradiction detection

#### Ethical Principles
- ✓ Anti-pathologizing stance
- ✓ Neurodiversity affirmation
- ✓ Vulnerability-as-strength framing
- ✓ Systems reframing (not individual blame)

### Drift Detection Metrics

```python
class PersonalityDriftDetector:
    def __init__(self):
        self.personality_markers = load_personality_dna()  # 45 markers
        self.formality_threshold = 0.60  # >0.6 = too formal
        self.jargon_threshold = 0.40    # >0.4 = too much jargon
        self.authenticity_target = 0.85  # Target 85%+ authenticity

    def detect_drift(response: str) -> DriftReport:
        report = {
            "authenticity_score": 0.0,
            "markers_present": [],
            "markers_missing": [],
            "drift_severity": "NONE",  # NONE, LOW, MEDIUM, HIGH, CRITICAL
            "recommendations": []
        }

        # Check 1: Formality score
        formality_score = measure_formality(response)
        if formality_score > self.formality_threshold:
            report['drift_severity'] = "HIGH"
            report['recommendations'].append("Reduce formal language, use contractions")

        # Check 2: Jargon detection
        jargon_count = count_therapy_jargon(response)
        if jargon_count > self.jargon_threshold:
            report['drift_severity'] = "MEDIUM"
            report['recommendations'].append("Replace 'procesamiento emocional' with 'procesar sentimientos'")

        # Check 3: Personality marker presence
        for marker in self.personality_markers:
            if marker_present_in(marker, response):
                report['markers_present'].append(marker)
            else:
                report['markers_missing'].append(marker)

        # Check 4: Authenticity score
        marker_coverage = len(report['markers_present']) / len(self.personality_markers)
        report['authenticity_score'] = marker_coverage * (1 - formality_score)

        if report['authenticity_score'] < 0.70:
            report['drift_severity'] = "CRITICAL"

        return report
```

### Drift Detection Thresholds

| Metric | Threshold | Action |
|---|---|---|
| **Authenticity Score** | <0.70 | Regenerate response |
| **Formality Score** | >0.60 | Add contractions, casual language |
| **Jargon Count** | >40% of response | Remove therapy-speak |
| **Missing Markers** | >15 of 45 | Regenerate with personality prompt |
| **Code-switch Absence** | 0 Spanish phrases | Inject natural bilingual mixing |

### Regeneration Triggers

**Trigger 1: High Formality (Score >0.60)**
```
Current response: "I would recommend engaging in emotional processing exercises..."
Problem: Too formal, no contractions
Regeneration: "I'd suggest you work through your feelings... here's what I mean..."
```

**Trigger 2: Therapeutic Jargon**
```
Current response: "This indicates a need for emotional dysregulation management..."
Problem: Therapy-speak, too abstract
Regeneration: "You're struggling to manage your feelings. That's not a disorder—here's why..."
```

**Trigger 3: Loss of Directness**
```
Current response: "One might consider the possibility that..."
Problem: Too hedged, not Sergio's blunt style
Regeneration: "Here's what I think: you're dealing with..."
```

### Return on Correction

```json
{
  "status": "DRIFT_DETECTED",
  "layer": 3,
  "drift_severity": "MEDIUM",
  "authenticity_score": 0.72,
  "issues": [
    "Formality score 0.64 (threshold 0.60)",
    "Missing 8 personality markers from expected 45"
  ],
  "regenerating": true,
  "regeneration_strategy": "Inject 3+ personality markers + reduce formality",
  "timestamp": "2025-11-30T14:24:12Z"
}
```

---

## Layer 4: Output Filtering Layer (Harmful Content Check)

### Purpose
Detect and prevent harmful outputs: crisis ideation, medical advice, pathologization, and psychological harm.

### Content Categories to Block

| Category | Detection | Action | Escalation |
|---|---|---|---|
| **Suicidal Ideation** | Keywords + context ("kill myself", "better if I weren't here") | Block + crisis resources | IF.guard veto |
| **Self-Harm** | Explicit self-injury content | Block + mental health resources | IF.guard veto |
| **Medical Advice** | "Take X medication", "You have Y condition" | Block + "consult doctor" | IF.guard veto |
| **Pathologizing** | "Your autism is a disorder", "You're broken if you feel X" | Block + reframe | IF.guard veto |
| **Abuse Normalization** | "Abuse is just different interaction patterns" | Block + escalation | Human review |

### Crisis Detection

```python
class CrisisDetector:
    def __init__(self):
        self.crisis_keywords = [
            'kill myself', 'end it all', 'go away', 'don\'t deserve',
            'hurt myself', 'cut myself', 'better off dead',
            'no way out', 'trapped', 'give up'
        ]
        self.severity_levels = {
            'LOW': 'Plan exists but distant',
            'MEDIUM': 'Plan exists, timeframe weeks/months',
            'HIGH': 'Plan exists, timeframe days/hours',
            'CRITICAL': 'Imminent action planned'
        }

    def detect_crisis(response: str) -> (bool, str, str):
        """
        Returns: (is_crisis, severity_level, recommended_action)
        """
        # Check 1: Keyword detection
        for keyword in self.crisis_keywords:
            if keyword in response.lower():
                # Check 2: Context analysis
                severity = analyze_temporal_context(response)
                if severity in ['HIGH', 'CRITICAL']:
                    return (True, severity, "ESCALATE_TO_EMERGENCY")
                return (True, severity, "PROVIDE_RESOURCES")

        return (False, "NONE", "CONTINUE")
```

### Crisis Response Protocol

**If Crisis Detected:**

```json
{
  "status": "CRISIS_ALERT",
  "layer": 4,
  "severity": "HIGH",
  "block_reason": "Suicidal ideation detected",
  "message": "I'm concerned about what you're sharing. Please reach out for immediate support.",
  "emergency_resources": [
    {
      "name": "National Suicide Prevention Lifeline",
      "number": "988",
      "available": "24/7"
    },
    {
      "name": "Crisis Text Line",
      "text": "TEXT HOME to 741741"
    },
    {
      "name": "International Association for Suicide Prevention",
      "url": "https://www.iasp.info/resources/Crisis_Centres/"
    }
  ],
  "next_step": "If you're safe, we can continue this conversation. If you're in immediate danger, please call emergency services.",
  "escalation": "Human reviewer notified (if configured)"
}
```

### Medical Advice Blocking

```python
class MedicalAdviceDetector:
    def detect_medical_claim(response: str) -> (bool, str):
        """
        Blocks claims that prescribe or diagnose medical conditions
        """
        medical_patterns = [
            r'take\s+(this\s+)?(medication|drug|supplement)',
            r'you (have|suffer from|are)\s+\w*\s*(depression|anxiety|ADHD|autism)',
            r'(dose|dosage|prescription|medication)',
            r'(antidepressant|antipsychotic|stimulant)'
        ]

        for pattern in medical_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                # BLOCK: Recommend professional consultation
                return (True, "MEDICAL_CLAIM_DETECTED")

        return (False, "SAFE")
```

### Pathologizing Detection

**Anti-pathologizing checks:**

```python
class PathologizingDetector:
    def detect_pathologizing(response: str) -> (bool, str):
        """
        Blocks frames that pathologize neurodiversity as disorder/deficit
        """
        pathologizing_patterns = [
            r'(autism|ADHD)\s+(is|causes)\s+(disorder|deficit|dysfunction)',
            r'you.*?(need to\s+)?fix|overcome.*?(your\s+)?(autism|introversion|sensitivity)',
            r'if\s+you\s+(don\'t|cannot)\s+\w+\s+(then\s+)?.*?broken|wrong',
            r'something\s+(is\s+)?wrong\s+with.*?(you|your\s+(mind|brain))'
        ]

        for pattern in pathologizing_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return (True, "PATHOLOGIZING_FRAME")

        return (False, "NEURODIVERSITY_AFFIRMING")
```

### IF.Guard Integration (Veto Power)

IF.guard has **override veto authority** over Layer 4 decisions:

```python
class IFGuardVeto:
    def can_override(layer4_decision: str, guard_assessment: str) -> bool:
        """
        IF.guard can veto Layer 4's "SAFE" decision if:
        1. Psychological harm is subtle but cumulative
        2. Manipulation/coercion is embedded in language
        3. Normalization of abuse is rationalized
        """
        return guard_assessment == "VETO_UNSAFE"
```

### Return on Rejection

```json
{
  "status": "REJECTED",
  "layer": 4,
  "reason": "Pathologizing frame detected",
  "problematic_content": "Your autism is something you should work on overcoming",
  "reframe": "Your autism is a different neurotype. You can develop skills that match social contexts you care about—without changing who you are.",
  "if_guard_status": "APPROVED_OVERRIDE"
}
```

---

## Layer 5: Rate Limiting Layer (Abuse Prevention)

### Purpose
Prevent token exhaustion, API abuse, and resource starvation through intelligent rate limiting and cost budgets.

### Rate Limit Tiers

**Tier 1: Public Access**
- Rate limit: 10 requests/hour
- Cost budget: 10,000 tokens/month
- Cooldown: 360 seconds between requests
- Use case: Anonymous or free tier users

**Tier 2: Registered Users**
- Rate limit: 100 requests/hour
- Cost budget: 50,000 tokens/month
- Cooldown: 36 seconds between requests
- Use case: Authenticated users, research

**Tier 3: Verified Clinical/Research**
- Rate limit: 500 requests/day (no hourly throttle)
- Cost budget: 500,000 tokens/month
- Cooldown: 6 seconds between requests
- Use case: Therapists, researchers, clinical settings

**Tier 4: Institutional (SaaS)**
- Custom limits (negotiated)
- Custom cost budgets
- No throttling on concurrent requests
- Use case: Healthcare systems, large organizations

### Cost Budget Tracking

```python
class CostBudgetManager:
    def __init__(self):
        self.token_costs = {
            'input_token': 0.15,    # Cents per 1K input tokens
            'output_token': 0.60,   # Cents per 1K output tokens
            'retrieval_token': 0.05 # ChromaDB retrieval cost
        }

    def estimate_cost(user_id: str, input_tokens: int,
                     estimated_output: int, retrieval_enabled: bool) -> float:
        """
        Returns estimated cost in cents
        """
        input_cost = (input_tokens / 1000) * self.token_costs['input_token']
        output_cost = (estimated_output / 1000) * self.token_costs['output_token']
        retrieval_cost = 0
        if retrieval_enabled:
            retrieval_cost = self.token_costs['retrieval_token']

        total = input_cost + output_cost + retrieval_cost

        # Check against user's monthly budget
        user_budget = get_monthly_budget(user_id)
        user_spent = get_monthly_spending(user_id)

        if user_spent + total > user_budget:
            return None  # Over budget

        return total
```

### Backoff Strategies

**Strategy 1: Exponential Backoff**
```
Request 1: Accept (0s wait)
Request 2: Wait 1s
Request 3: Wait 2s
Request 4: Wait 4s
Request 5: Wait 8s
...
Request N: Wait 2^(N-1) seconds (capped at 1 hour)
```

**Strategy 2: Sliding Window**
```
Window: Last 60 minutes
Count requests in window
If count >= tier_limit:
  Reject next request
  Suggest wait time = (oldest_request_time + 60min) - now
```

**Strategy 3: Token Budget Depletion**
```
Monthly budget: 50,000 tokens
Daily allocation: 50,000 / 30 ≈ 1,667 tokens/day
If user exceeds daily allocation:
  Next request queued (FIFO)
  Backoff: Exponential until reset (midnight UTC)
```

### Return on Rate Limit Exceeded

```json
{
  "status": "RATE_LIMIT_EXCEEDED",
  "layer": 5,
  "reason": "Hourly request limit reached",
  "limit": "100 requests/hour (Tier 2)",
  "current_count": 100,
  "retry_after_seconds": 3600,
  "suggestion": "Upgrade to Tier 3 for higher limits",
  "budget_impact": "0 tokens (request was blocked before processing)"
}
```

---

## Layer 6: Audit Logging Layer (IF.TTT Compliance)

### Purpose
Record all IF.emotion decisions, responses, and citations to maintain traceability (IF.TTT compliance) and enable threat detection.

### What to Log

**Required Log Fields:**

```python
class AuditLog:
    def __init__(self):
        self.required_fields = {
            'timestamp': '2025-11-30T14:23:45.123Z',
            'user_id': 'user_xyz',
            'request_id': 'req_abc123def456',
            'input_text': 'User question (anonymized after 7 days)',
            'input_length_tokens': 127,
            'layer_1_validation': {
                'passed': True,
                'sanitization_applied': ['utf8_normalization', 'control_char_removal']
            },
            'layer_2_classification': {
                'domain': 'IN_SCOPE',
                'confidence': 0.89,
                'detected_topic': 'Grief and Identity'
            },
            'layer_3_drift_check': {
                'authenticity_score': 0.87,
                'drift_severity': 'NONE',
                'markers_present': 23,
                'markers_total': 45
            },
            'layer_4_safety_check': {
                'crisis_detected': False,
                'pathologizing': False,
                'medical_advice': False,
                'if_guard_veto': False
            },
            'layer_5_rate_limit': {
                'user_tier': 'Tier 2',
                'request_count_this_hour': 45,
                'budget_remaining_tokens': 12847,
                'cost_of_this_request': '$0.08'
            },
            'response_metadata': {
                'output_length_tokens': 342,
                'citations_generated': 3,
                'if_citation_uris': [
                    'if://citation/grief-identity-2025-11-30-abc123',
                    'if://doc/sergio-frameworks/identity-interaction',
                    'if://doc/psychology-corpus/attachment-theory-xyz'
                ]
            },
            'decision': 'APPROVED_AND_SENT',
            'processing_time_ms': 1247
        }
```

### Retention Policies

**Data Retention by Classification:**

| Data Type | Retention Period | Reason |
|---|---|---|
| **User Input Text** | 7 days (then anonymize) | GDPR compliance, debugging |
| **Anonymized Logs** | 7 years | Legal audit trail (psychological services) |
| **Citation Metadata** | Permanent | Research reproducibility |
| **Cost/Budget Data** | 3 years | Financial audit trail |
| **Crisis Alerts** | 10 years | Critical incident history |
| **IP Addresses** | 30 days (then hash) | Fraud detection, then privacy |

### Audit Query Interface

```python
class AuditQueryEngine:
    def query_audit_log(self, filters: dict) -> list:
        """
        Query: "Show me all crisis detections in the last 7 days"
        filters = {
            'layer_4_safety_check.crisis_detected': True,
            'timestamp_after': '2025-11-23T00:00:00Z',
            'timestamp_before': '2025-11-30T23:59:59Z'
        }

        Query: "Show me which frameworks were used in psychology conversations"
        filters = {
            'layer_2_classification.detected_topic': 'psychological*',
            'response_metadata.if_citation_uris': 'if://doc/sergio-frameworks/*'
        }
        """
        return self.elasticsearch_query(filters)

    def threat_detection(self) -> list:
        """
        Detect patterns:
        - Same user hitting rate limit 10+ times = abuse
        - Repeated crisis alerts from same user = support needed
        - Layer 2 rejections increasing = domain drift
        - Layer 3 drift detections increasing = system problem
        """
        pass
```

### Audit Dashboard Metrics

**Real-Time Monitoring:**
```
IF.emotion Audit Dashboard (2025-11-30)
=====================================
Requests (last 24h): 1,247
- Layer 1 rejections: 12 (0.96%)
- Layer 2 rejections: 23 (1.84%)
- Layer 3 regenerations: 47 (3.77%)
- Layer 4 safety blocks: 3 (0.24%) [2 crisis, 1 medical]
- Layer 5 rate limits: 56 (4.49%)
- Approved: 1,106 (88.70%)

Citation Coverage: 98.4% (1,088 / 1,106)
Average Response Time: 1.24 seconds
Token Cost (24h): $156.78
Most Common Topic: Grief & Identity Loss (187 queries)
Most Cited Framework: Identity=Interaction (412 citations)

Crisis Alerts: 2 (both with escalation)
Medical Advice Blocks: 1
Pathologizing Blocks: 0
Rate Limit Hits: 56 (top user: 12 hits, quota approached)
```

### Return on Log Check

```json
{
  "status": "APPROVED",
  "layer": 6,
  "audit_log_id": "audit_1234567890abc",
  "logged_at": "2025-11-30T14:23:47.345Z",
  "log_entry": {
    "request_id": "req_xyz789",
    "user_id": "user_abc",
    "layer_decisions": ["PASS", "PASS", "PASS", "PASS", "PASS"],
    "citations": 3,
    "cost": "$0.08",
    "processing_time_ms": 1247
  },
  "audit_queryable": true,
  "retention_until": "2032-11-30T23:59:59Z"
}
```

---

## Data Flow Diagram

```
INPUT: User Query
  │
  ▼
[ LAYER 1: INPUT VALIDATION ]
  ├─ Sanitize input
  ├─ Check encoding, length, format
  └─ Return: (PASS | REJECT with error)
  │
  ├─ REJECT? ──→ Log + Return Error
  │
  ▼
[ LAYER 2: DOMAIN CONSTRAINT ]
  ├─ Classify topic (in-scope?)
  ├─ Semantic search against psychology corpus
  └─ Return: (IN_SCOPE | OUT_SCOPE with redirection)
  │
  ├─ OUT_SCOPE? ──→ Log + Return Redirection
  │
  ▼
[ LAYER 3: PERSONALITY PRESERVATION ]
  ├─ Load Sergio personality DNA (cached)
  ├─ Check response authenticity (before generation!)
  └─ Prepare personality markers for injection
  │
  ├─ CRITICAL DRIFT RISK? ──→ Adjust system prompt
  │
  ▼
[ LAYER 4: OUTPUT FILTERING ]
  ├─ Generate response with personality
  ├─ Scan for crisis, medical, pathologizing
  ├─ IF.guard integration
  └─ Return: (SAFE | BLOCKED with alternatives)
  │
  ├─ BLOCKED? ──→ Log + Return Safety Resources
  │
  ▼
[ LAYER 5: RATE LIMITING ]
  ├─ Check user tier and request count
  ├─ Check budget (tokens/month)
  ├─ Calculate cost of this response
  └─ Return: (ALLOWED | RATE_LIMITED with backoff)
  │
  ├─ RATE_LIMITED? ──→ Log + Return Retry-After
  │
  ▼
[ LAYER 6: AUDIT LOGGING ]
  ├─ Record all decisions, citations, cost
  ├─ Generate if://citation URIs
  ├─ Store in Elasticsearch + Redis
  └─ Return: Complete audit trail
  │
  ▼
OUTPUT: Response + Citations + Audit Log
```

---

## Implementation Checklist

### Phase 1: Core Layers (Weeks 1-2)
- [ ] Layer 1: Input validation + UTF-8 sanitization
- [ ] Layer 2: Topic classification (semantic search)
- [ ] Layer 4: Crisis + medical advice detection
- [ ] Layer 6: Basic audit logging

### Phase 2: Personality Integration (Weeks 3-4)
- [ ] Layer 3: Personality DNA marker loading + caching
- [ ] Layer 3: Drift detection metrics
- [ ] Layer 3: Regeneration triggers

### Phase 3: Advanced Protection (Weeks 5-6)
- [ ] Layer 4: Pathologizing detection + IF.guard veto
- [ ] Layer 5: Rate limiting + cost budgeting
- [ ] Layer 6: Elasticsearch integration + audit dashboard

### Phase 4: Testing & Hardening (Weeks 7-8)
- [ ] Adversarial testing (jailbreak attempts)
- [ ] Performance testing (latency under load)
- [ ] Audit trail completeness verification
- [ ] Documentation + runbook creation

---

## Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| **Layer 1 False Positives** | <1% | Legitimate inputs incorrectly rejected |
| **Layer 2 Accuracy** | >95% | Correct in-scope/out-scope classification |
| **Layer 3 Authenticity** | >85% | Personality markers present in response |
| **Layer 4 Safety** | 100% | Zero crisis alerts missed |
| **Layer 5 Availability** | >99.5% | Rate limiting doesn't cause cascading failures |
| **Layer 6 Completeness** | 100% | All decisions logged and queryable |
| **End-to-End Latency** | <2 seconds | P95 response time (input → output) |
| **Citation Accuracy** | 99%+ | If citations resolve to correct source |

---

## IF.TTT Compliance Statement

This sandbox architecture is fully compliant with IF.TTT (Traceable, Transparent, Trustworthy):

✅ **Traceable:** Every decision is logged with source layer, timestamp, and decision criteria
✅ **Transparent:** All layers have documented rejection criteria and audit queries
✅ **Trustworthy:** IF.guard has veto power; crisis escalation automated; medical advice blocked

**Citation:** if://doc/if-emotion-sandbox-architecture/2025-11-30

---

## References

- IF.emotion Component Proposal: `if://doc/if-emotion-proposal/2025-11-30`
- IF.guard Security Framework: `if://doc/if-guard-documentation/2025-11-XX`
- IF.TTT Specification: `if://doc/if-ttt-specification/2025-11-XX`
- Sergio Personality DNA: `/home/setup/sergio_chatbot/sergio_persona_profile.json`
- Psychology Corpus: `/mnt/c/users/setup/downloads/psychology_corpus_output/`

---

**Document Approval Status:** Ready for Implementation
**Next Steps:**
1. Guardian Council review of sandbox design
2. Peer review by IF.guard component leads
3. Implementation sprint planning
4. Hardened testing on pilot user group

