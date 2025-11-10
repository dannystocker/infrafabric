# Naming Inconsistencies Analysis

**Date:** 2025-11-10
**Purpose:** Document naming inconsistencies in InfraFabric component catalog
**Status:** Analysis Complete, Remediation Pending
**Citation:** if://doc/naming-inconsistencies-2025-11-10

---

## Executive Summary

Systematic analysis identified 70+ references to 4 naming inconsistencies across codebase:
- **IF.ceo vs IF.ceo_:** 20 underscore variant references
- **IF.citation vs IF.citations:** 11 plural variant references (IF.citate deprecated in ANNEX-Q)
- **IF.optimise variants:** 13 references to IF.optimise_engine / IF.optimised
- **IF.persona vs IF.personality:** 26 personality variant references

**Recommendation:** Standardize on canonical forms (IF.ceo, IF.citation, IF.optimise, IF.persona) and deprecate variants.

---

## Analysis Results

### 1. IF.ceo vs IF.ceo_ (Underscore Variant)

**Canonical Form:** IF.ceo
**Variant:** IF.ceo_ (underscore suffix)

**Usage Count:**
```bash
grep -r "IF\.ceo_" --include='*.md' --include='*.py' . | wc -l
→ 20 references
```

**Status in COMPONENT-INDEX.md:**
```
| IF.ceo | Component | ✅ Documented | papers/IF-vision.md | 16 Sam Altman facets |
| IF.ceo_ | ⚠️ Duplicate | Internal | Multiple files | Underscore variant (naming inconsistency) |
```

**Root Cause:** Likely Python variable naming convention (trailing underscore to avoid keyword conflicts).

**Recommendation:**
- **Action:** Standardize on IF.ceo (documented component)
- **Migration:** Find/replace IF.ceo_ → IF.ceo in all files
- **Timeline:** Non-breaking change, can be done incrementally

---

### 2. IF.citation vs IF.citations (Plural Variant)

**Canonical Form:** IF.citation
**Variants:**
- IF.citations (plural)
- IF.citate (verb form - ALREADY DEPRECATED in ANNEX-Q)

**Usage Count:**
```bash
grep -r "IF\.citations" --include='*.md' --include='*.py' . | wc -l
→ 11 references
```

**Status in COMPONENT-INDEX.md:**
```
| IF.citation | Component | ✅ Documented | papers/IF-witness.md | Cryptographic provenance |
| IF.citations | ⚠️ Duplicate | Internal | Multiple files | Plural variant (naming inconsistency) |
| IF.citate | Component | 📚 Deprecated | COMPONENT-INDEX.md | Verb variant (deprecated) |
```

**Root Cause:** Inconsistent usage of singular vs plural form (e.g., "IF.citations database" vs "IF.citation system").

**Recommendation:**
- **Action:** Standardize on IF.citation (singular, noun form)
- **Rationale:** Component name should be singular (IF.guard, not IF.guards; IF.swarm, not IF.swarms)
- **Migration:** Replace "IF.citations database" → "IF.citation database"
- **Timeline:** Low risk, 11 references to update

---

### 3. IF.optimise vs IF.optimise_engine vs IF.optimised (Variants)

**Canonical Form:** IF.optimise
**Variants:**
- IF.optimise_engine (suffixed variant)
- IF.optimised (past tense variant)

**Usage Count:**
```bash
grep -r "IF\.optimise_engine\|IF\.optimised" --include='*.md' --include='*.py' . | wc -l
→ 13 references
```

**Status in COMPONENT-INDEX.md:**
```
| IF.optimise | Component | ✅ Documented | annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md | Token cost management |
| IF.optimise_engine | ⚠️ Duplicate | Internal | Multiple files | Engine variant (naming inconsistency) |
| IF.optimised | ⚠️ Duplicate | Internal | Multiple files | Past tense variant (naming inconsistency) |
```

**Root Cause:**
- IF.optimise_engine: Likely refers to implementation class/module
- IF.optimised: Past tense used in narrative ("IF.optimised delegation")

**Recommendation:**
- **IF.optimise_engine:** Keep as internal implementation detail (class name), not public API
- **IF.optimised:** Replace with "IF.optimise" in all public documentation
- **Timeline:** Medium priority (13 references)

---

### 4. IF.persona vs IF.personality (Synonym Variant)

**Canonical Form:** IF.persona
**Variant:** IF.personality

**Usage Count:**
```bash
grep -r "IF\.personality" --include='*.md' --include='*.py' . | wc -l
→ 26 references (highest count!)
```

**Status in COMPONENT-INDEX.md:**
```
| IF.persona | Component | ✅ Documented | papers/IF-foundations.md | Agent characterization (Bloom patterns) |
| IF.personality | ⚠️ Duplicate | Internal | Multiple files | May be alias for IF.persona (needs consolidation) |
```

**Root Cause:** Synonym usage - "personality" and "persona" mean similar things, used interchangeably.

**Semantic Analysis:**
- **IF.persona:** More precise (refers to external characterization, agent role)
- **IF.personality:** More generic (could mean internal traits, behavior)

**Recommendation:**
- **Action:** Standardize on IF.persona (documented component)
- **Rationale:** "Persona" is more specific to multi-agent systems (agent roles, characterization patterns)
- **Migration:** 26 references to update (highest priority)
- **Timeline:** Low risk, purely documentary change

---

## Summary Statistics

| Variant Type | Canonical Form | Variant | References | Priority |
|--------------|----------------|---------|------------|----------|
| Underscore suffix | IF.ceo | IF.ceo_ | 20 | Medium |
| Plural form | IF.citation | IF.citations | 11 | Low |
| Engine/tense | IF.optimise | IF.optimise_engine / IF.optimised | 13 | Medium |
| Synonym | IF.persona | IF.personality | 26 | **High** |

**Total:** 70+ references to variant forms across codebase

---

## Remediation Plan

### Phase 1: Documentation Updates (Low Risk)

**Immediate Actions:**
1. Update COMPONENT-INDEX.md to clarify canonical forms (DONE)
2. Document naming policy in this file (DONE)
3. Mark variants as internal/deprecated in index (DONE)

**Timeline:** Completed 2025-11-10

---

### Phase 2: Mechanical Find/Replace (Medium Risk)

**Priority Order:**
1. **IF.personality → IF.persona** (26 refs, highest count)
2. **IF.ceo_ → IF.ceo** (20 refs)
3. **IF.optimised → IF.optimise** (13 refs, narrative only)
4. **IF.citations → IF.citation** (11 refs)

**Method:**
```bash
# Example for IF.personality → IF.persona
grep -rl "IF\.personality" --include='*.md' --include='*.py' . | \
  xargs sed -i 's/IF\.personality/IF.persona/g'

# Verify no breaking changes
git diff
git add .
git commit -m "Standardize naming: IF.personality → IF.persona"
```

**Timeline:** 1-2 hours (with testing)

---

### Phase 3: Code Review (High Risk)

**Components requiring manual review:**
- **IF.optimise_engine:** May be valid class name (e.g., `class IFOptimiseEngine`)
- **IF.ceo_:** May be Python variable name to avoid keyword conflict

**Action Required:**
1. Grep for `class.*IF.*optimise.*engine` to find implementation classes
2. Grep for Python variable assignments: `IF\.ceo_ =`
3. Decide: Keep as internal implementation OR refactor to canonical form

**Timeline:** Requires code inspection, 2-3 hours

---

## Naming Policy (Going Forward)

**Established 2025-11-10:**

### 1. Component Naming Convention

**Rule:** Use `IF.{component}` (dot notation, singular noun)

**Examples:**
- ✅ Good: IF.guard, IF.swarm, IF.citation, IF.persona
- ❌ Bad: IF.guards (plural), IF.citations (plural), IF.citate (verb)

**Rationale:** Consistency with namespace convention (like Java packages, Python modules).

### 2. Singular vs Plural

**Rule:** Component names are SINGULAR

**Examples:**
- ✅ IF.guard (refers to the guardian system, not individual guardians)
- ✅ IF.citation (refers to citation system, not individual citations)
- ❌ IF.guardians (use IF.guard)
- ❌ IF.citations (use IF.citation)

**Exception:** Implementation modules may use plural (e.g., `infrafabric/guardians.py`)

### 3. Noun vs Verb Forms

**Rule:** Component names are NOUNS

**Examples:**
- ✅ IF.citation (noun: the citation system)
- ❌ IF.citate (verb: to cite something)
- ✅ IF.search (noun: the search system, not verb "to search")

### 4. Underscore Suffix (`_`)

**Rule:** No trailing underscores in component names

**Exception:** Python variables may use trailing underscore to avoid keyword conflicts:
```python
# ✅ Acceptable in Python code
from infrafabric import guard as guard_  # Avoid 'guard' builtin
if_ = IFConditional()  # Avoid 'if' keyword

# ❌ Not acceptable in documentation
"See IF.guard_ for details"  # Should be IF.guard
```

### 5. Past Tense / Adjective Forms

**Rule:** Component names are PRESENT TENSE nouns

**Examples:**
- ✅ IF.optimise (the optimization system)
- ❌ IF.optimised (past tense adjective)
- ✅ IF.collapse (the collapse analysis system)
- ❌ IF.collapsed (past tense)

**Exception:** Narrative text may use past tense to describe actions:
```markdown
✅ "The system was IF.optimised using Haiku delegation"
→ Should be: "The system used IF.optimise with Haiku delegation"
```

---

## Migration Examples

### Example 1: IF.personality → IF.persona

**Before:**
```markdown
IF.personality allows agents to exhibit Bloom patterns (Early/Late/Steady).
```

**After:**
```markdown
IF.persona allows agents to exhibit Bloom patterns (Early/Late/Steady).
```

### Example 2: IF.citations → IF.citation

**Before:**
```markdown
IF.citations database contains 500+ cryptographically signed references.
```

**After:**
```markdown
IF.citation database contains 500+ cryptographically signed references.
```

### Example 3: IF.optimised → IF.optimise

**Before:**
```markdown
Token costs were IF.optimised via Haiku delegation.
```

**After:**
```markdown
Token costs were reduced via IF.optimise Haiku delegation.
```

### Example 4: IF.ceo_ → IF.ceo (Python variable)

**Before:**
```python
from infrafabric import ceo as ceo_  # Avoid name collision
facets = ceo_.get_sam_altman_spectrum()
```

**After:**
```python
from infrafabric import ceo as if_ceo  # More descriptive
facets = if_ceo.get_sam_altman_spectrum()
```

---

## Impact Analysis

**Pros of Standardization:**
- ✅ Clearer documentation (one canonical name per component)
- ✅ Easier grep searches (`grep "IF\.citation"` finds all, no need for `IF\.citation[s]*`)
- ✅ Reduced cognitive load (developers don't wonder: "Is it persona or personality?")
- ✅ Professional appearance (consistency signals quality)

**Cons / Risks:**
- ⚠️ Breaking changes if external projects reference variant names
- ⚠️ Git history grep becomes harder (need to search both old and new names)
- ⚠️ Documentation rewrites take time (70+ references)

**Mitigation:**
- Add aliases in documentation: "IF.persona (formerly IF.personality)" for 3 months
- Update external-facing docs first (papers/, README.md)
- Internal code can migrate gradually (no external API breakage)

---

## Testing Strategy

**Before Mass Find/Replace:**

1. **Verify no hardcoded string literals:**
   ```bash
   grep -r '"IF\.personality"' --include='*.py'
   # Should return 0 (use constants, not string literals)
   ```

2. **Check for programmatic name generation:**
   ```bash
   grep -r 'f"IF\.{' --include='*.py'
   # Ensure no f-string template uses variant names
   ```

3. **Validate no broken links:**
   ```bash
   grep -r '\[IF\.personality\]' --include='*.md'
   # Check markdown links don't reference old names
   ```

**After Mass Find/Replace:**

1. **Git diff review:**
   ```bash
   git diff --stat  # Verify only doc files changed, not code logic
   ```

2. **Build/Test suite:**
   ```bash
   python -m pytest  # Ensure no test failures
   ```

3. **Documentation build:**
   ```bash
   # If using doc generator, ensure no broken internal links
   ```

---

## Recommended Actions (User Decision Required)

**Option 1: Immediate Remediation (2-3 hours)**
- Run mechanical find/replace for all 4 variants
- Review git diff for correctness
- Commit with IF.TTT metadata

**Option 2: Gradual Migration (Low Risk)**
- Update new documentation to use canonical forms
- Leave existing references as-is (mark as "legacy naming")
- Deprecate variants over 3-6 months

**Option 3: Defer (Lowest Priority)**
- Mark as "known issue" in COMPONENT-INDEX.md
- Address during next major version (v4.0.0)
- Focus on higher-priority tasks

**Recommendation:** Option 1 (Immediate) for **IF.personality → IF.persona** (26 refs, highest impact)
**Recommendation:** Option 2 (Gradual) for other variants (lower priority)

---

## IF.TTT Compliance

**Traceable:**
- Grep commands documented for reproducibility
- Variant counts verified across codebase
- Root cause analysis for each inconsistency

**Transparent:**
- Full remediation plan provided
- Pros/cons of standardization documented
- Migration examples given for each case

**Trustworthy:**
- Conservative approach (user approval required)
- Testing strategy specified
- Risk mitigation addressed

---

**Citation:** if://doc/naming-inconsistencies-2025-11-10
**Status:** Analysis Complete, Awaiting User Decision
**Next Steps:** User selects Option 1, 2, or 3 for remediation

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
