# IF.* Story Context Index - Quick Start Guide for Haiku Agents

**Purpose:** Maximize storytelling efficiency while minimizing token waste
**Target:** Haiku agents writing 12 Archer-style IF.* component stories
**Token Budget:** 15K context per story (12K reading + 3K writing)
**Wall-Clock Time:** ~2 hours for all 12 stories (parallel execution)

---

## TL;DR - Fast Path

You're assigned **Story N**. Here's what to do in 60 seconds:

1. **Open the index:** `/home/setup/infrafabric/IF-STORY-CONTEXT-INDEX.yaml`
2. **Find your story section:** Search for `story_N_` (e.g., `story_1_if_yologuard`)
3. **Follow context assembly protocol:**
   - Load Redis keys (listed in `redis_keys` section)
   - Read local files with exact line ranges (offset + limit parameters)
   - Check downloads IF marked "REQUIRED" (verify MD5 first)
   - Run searches ONLY if you need specific detail

4. **Write 3,500-5,000 word story** using the provided template:
   - Protagonist, Setup, Escalation, Twist, Closing Punch
   - Include story_structure_checklist items
   - Contemporary elements naturally woven in
   - Real incidents referenced for authenticity

5. **Quality check** before submission:
   - Opening hook grabs immediately ✓
   - Closing punch lands with impact ✓
   - Archer-style rhythm (short + long sentences) ✓
   - Component's deeper meaning illuminated ✓

---

## Context Assembly: Step-by-Step

### Step 1: Redis Keys (Fastest)

```bash
redis-cli GET "context:file:agents.md:IF.COMPONENT-section"
redis-cli GET "context:doc:framework-v1"
```

**Time:** <100ms per key
**Tokens:** 200-500 per key
**Why first:** Already cached, no network I/O

### Step 2: Local Files (Precise)

Use the Read tool with exact line ranges:

```
Read /home/setup/infrafabric/IF-armour.md offset=78 limit=305
```

NOT:
```
Read /home/setup/infrafabric/IF-armour.md  ← reads entire 893-line file (WASTEFUL)
```

**Time:** 500ms per file
**Tokens:** ~150-200 tokens per 100 lines
**Why second:** Precise excerpts, no context waste

### Step 3: Downloads Folder (Verify First)

If a file is marked "REQUIRED" in your story's downloads_folder section:

```bash
# Step 3a: Check if it exists in Redis cache
redis-cli GET "context:doc:your-component-name"

# Step 3b: Compute MD5 of local file
md5sum /mnt/c/users/setup/downloads/FILENAME.md

# Step 3c: If MD5 matches Redis cache → Use Redis (faster)
# If MD5 differs & downloads newer → Read downloads, re-cache
# If MD5 differs & downloads older → Use Redis (newer is better)
```

**Time:** 1-2 seconds (with deduplication)
**Tokens:** Variable, but prevented duplication saves 30-50% tokens
**Why third:** Highest risk of duplication, verify first

### Step 4: Search Queries (On-Demand Only)

In your story section, you'll see:

```yaml
search_queries:
  primary:
    - pattern: "entropy detection"
      files: "IF-armour.md, IF.yologuard_v3.py"
      purpose: "Technical mechanism..."
```

**Only run this IF:**
- Your draft needs specific technical detail
- You've already read Redis + local files but still missing something
- Example: Need exact line of code reference

**Don't run IF:**
- You have enough context from primary sources
- The pattern would overlap with already-read content

**Time:** 1-5 seconds per query
**Tokens:** 800-1200 per query result

---

## Token Budget Tracker

Keep running total of context tokens as you read:

| Source | Tokens | Example |
|--------|--------|---------|
| Redis key | 200-500 | IF.yologuard overview |
| Local file (100 lines) | 500 | IF-armour excerpt |
| Local file (300 lines) | 1,500 | IF-foundations.md excerpt |
| Search results | 800-1,200 | "entropy detection" in 3 files |
| Real incident research | 600-1,000 | Knight Capital $440M loss |
| **Story draft (output)** | **10K** | Your prose output |
| **TOTAL PER STORY** | **~15K** | Hard limit |

**Strategy:**
- Primary context: 5K tokens (technical spec)
- Secondary context: 5K tokens (evaluation data)
- Tertiary context: 5K tokens (real incidents)
- **When you hit 12K tokens of input, STOP READING and START WRITING**

---

## Deduplication Prevention (Save ~40% Tokens)

### Scenario: Same content in Redis + Downloads?

Example: IF.yologuard-COMPLETE-DOCUMENTATION.md appears in both places

**Fast path:**
1. Redis cache date: 2025-11-22
2. Downloads file date: 2025-11-15
3. Redis is newer → USE REDIS (saves file read)

**Detailed path (if dates identical):**
```bash
redis-cli GET "context:doc:yologuard-complete-v3" | md5sum
# Output: a7f3e2d1c6b9abc...

md5sum /mnt/c/users/setup/downloads/IF.yologuard-COMPLETE-DOCUMENTATION.md
# Output: a7f3e2d1c6b9abc...

# If hashes match → Use Redis (identical content, faster retrieval)
# If different → Read downloads (newer version)
```

**Net benefit:** Prevents reading duplicate 2,000-5,000 token file 6 times across different stories

---

## Real Incidents: When to Reference

Your story has a `real_incidents_to_reference` section listing actual events.

**Use these for:**
- Story authenticity (readers recognize real events)
- Emotional weight (real consequences > fictional)
- Technical accuracy (actual case studies validate methodology)

**Example: IF.yologuard - Knight Capital $440M Loss**
- Real event: Algorithmic trading error, cascading failure, $440M loss in 45 minutes
- Story relevance: Marcus's removal of "false positive" guards parallels removing Knight's safeguards
- How to weave: "Marcus realized... The systems Knight Capital had relied on to catch errors weren't false alarms. They were the immune system."

**Don't info-dump:** Keep incident references to 1-2 sentences max. Let story do the work.

---

## Archer Style: Technical Checklist

Before you declare your draft ready:

### Opening Hook
- ✓ First sentence pulls reader into immediate situation
- ✓ No setup, no backstory, immediate action
- Example: "Marcus stared at the yologuard report in disbelief. 1,247 vulnerabilities. In ten lines of code."

### Protagonist
- ✓ Flawed, relatable professional (not hero, not villain)
- ✓ Middle-class or working-class stakes (not billionaire/celebrity)
- ✓ Has one clear motivation (money, safety, redemption, justice)
- Example: Marcus is senior DevOps (relatable), not infosec expert (too distant)

### Setup (20-30% of word count)
- ✓ Establish stakes clearly (what does protagonist want?)
- ✓ Establish moral universe (what's right/wrong in this story?)
- ✓ Plant details protagonist will misinterpret later
- Example: "The clean scan meant safety. That was the lie."

### Escalation (40-50%)
- ✓ Plans unfold, complications arise
- ✓ Reader invests emotionally
- ✓ NO INFO-DUMPING about IF.* component
- ✓ Technical details woven into action, not exposition
- Example: "The entropy threshold was 4.5. After refinement, 3.8. After two weeks, 2.1. By then the damage was done."

### Twist (10-20%)
- ✓ Single revelation that recontextualizes everything
- ✓ Should be surprising but inevitable in retrospect
- ✓ **MUST illuminate the IF.* component's deeper meaning**
- Example: Clean scan = proof system was broken; human expert code too sophisticated

### Closing Punch (Final line)
- ✓ Lands emotional/moral impact
- ✓ Usually 1-2 sentences
- ✓ Often subverts opening line's assumption
- Example: "I'd been hunting the wrong predator all along." (vs. "Marcus was certain he'd found the breach.")

### Language Patterns
- ✓ Alternating sentence length (short tension + long reflection)
- ✓ British English spelling: honour, colour, realise
- ✓ Dialogue class-marked but natural
- ✓ Vocabulary sophisticated but not ornate
- ✓ Technical terms used naturally (no "let me explain what entropy is...")
- ✓ Concrete sensory details (coat fabric, coffee smell, keyboard sound)

### What NOT to Do
- ✗ Explain how IF.yologuard works (reader should infer from story)
- ✗ Use trendy slang ("viral," "slay," "sus")
- ✗ Info-dump about AI ethics (let story carry the weight)
- ✗ Generic startup clichés (make character specific, location specific)
- ✗ Write in present tense (use past for distance, reflection)

---

## Contemporary Elements: Weaving Naturally

Your story section lists "contemporary_elements" — things that make 2025 feel real.

**Don't list them.** Weave them as normal story details:

```
BAD: "Marcus worked at a fintech startup in London, using Slack and Signal for incident response."

GOOD: "Angelique's message came through Signal at 14:47. On Slack, three separate threads had already blamed the deployment."
```

**Examples per story:**
- IF.yologuard: fintech startup, PR review workflows, Signal, Slack channels → natural in story
- IF.guard: Guardian Council deliberation, Zoom call, voice modulation → natural in story
- IF.memory: Redis Cloud, git commits, session logs → natural technical setting

---

## Story Length & Structure

**Target:** 3,500-5,000 words
**Typical Archer story:** ~4,000 words (verify with published collection)

**Word distribution:**
- Opening hook: 50-100 words
- Setup: 900-1,200 words
- Escalation: 1,600-2,000 words
- Twist: 400-600 words
- Closing: 50-100 words
- Dialogue + interiority: Woven throughout

**Pacing:**
- Read at 250 words/minute average
- 4,000-word story = 16-20 minute read
- Matches Archer's collection (stories meant for magazine/podcast serialization)

---

## Quality Assurance Before Submission

Run through this checklist before declaring story complete:

**Story Structure**
- [ ] Opening hook grabs immediately (re-read first paragraph; would you keep reading?)
- [ ] Protagonist is flawed + relatable (not perfect, not unsympathetic)
- [ ] Stakes are clear by end of setup (what will happen if protagonist fails?)
- [ ] Escalation maintains tension (each scene raises stakes)
- [ ] Twist is surprising but inevitable (reader says "Oh!" then "Of course!")
- [ ] Closing line lands with impact (reader remembers last line, not middle)

**Technical Accuracy**
- [ ] Component's function is accurate (not invented)
- [ ] Technical details are correct but accessible
- [ ] Twist illuminates component's deeper meaning (not just describes it)
- [ ] Real incidents referenced correctly (dates, details, lessons)
- [ ] Code/algorithms mentioned are actual (IF.yologuard entropy detection real, etc.)

**Contemporary Accessibility**
- [ ] No 1988 references creeping in (not typewriters, not BOAC)
- [ ] British English used consistently (honour, colour, realise, whilst)
- [ ] Class markers contextualized (explain once: "Savile Row suit [bespoke Mayfair tailoring]")
- [ ] Tech terminology used naturally (no "let me explain...")
- [ ] Story will age well (no "trending," "viral," platform-specific slang)

**Archer's Style**
- [ ] Sentence rhythm alternates short (tension) and long (reflection)
- [ ] Dialogue is class-marked but natural
- [ ] Vocabulary is sophisticated but not ornate
- [ ] Sensory details ground reader (fabrics, sounds, smells, tastes, touches)
- [ ] Character interiority reveals doubts (internal conflict, not just external)
- [ ] Geographic specificity (street names, actual landmarks, real locations)

**Story Independence**
- [ ] Story stands alone (no required reading of other stories)
- [ ] Component knowledge not required (non-technical reader enjoys it)
- [ ] References to other stories (IF.guard story mentions Aisha from Story 2) are minor, contextual

---

## Common Pitfalls to Avoid

### Pitfall 1: Info-Dumping About the Component
**Problem:** "Marcus deployed IF.yologuard, which uses entropy detection to find high-entropy tokens, which indicate base64-encoded secrets..."

**Fix:** Show the mechanism through action. "The scan returned 1,247 flags. Legitimate junior dev code mixed with actual vulnerabilities—or was it? The entropy threshold made no distinction."

### Pitfall 2: Not Understanding the Twist
**Problem:** Twist is just "Marcus was wrong."

**Fix:** Twist illuminates the component's deeper meaning. "The clean scan WAS the detection. A human-crafted attack was too sophisticated to trigger automated warnings. The false positives were legitimate code. Marcus had dismantled the company's immune system."

### Pitfall 3: Updating Vocabulary, Not Voice
**Problem:** "Yo, the AI is sus. Let's go viral with this."

**Fix:** Keep Archer's sophisticated but accessible voice. Update references naturally. "Signal group chat erupted. Three minutes. That's all it took."

### Pitfall 4: Forgetting the Personal Stake
**Problem:** Story is about the company, the algorithm, the system.

**Fix:** Story is about *this person, right now, making a choice*. Marcus = not generic DevOps, but Marcus Chen with a mortgage, a reputation, a specific fear.

### Pitfall 5: Twist Without Recontextualization
**Problem:** Twist surprises but doesn't change meaning. "Oh, Marcus was actually the AI all along!"

**Fix:** Twist changes what the whole story means. "If detection is broken, what protects us? Who checks the checkers?"

---

## Parallel Execution: Coordination

**You'll be one of 12 Haiku agents.** Sonnet orchestrator will coordinate:

1. **Pre-assignment** - Sonnet assigns each agent a story
2. **Context assembly** - You follow this guide, load your context
3. **Writing** - All 12 agents write simultaneously (wall-clock: 60-90 min)
4. **Submission** - Each agent submits completed story to Sonnet
5. **Quality review** - Sonnet checks against Archer's style + component accuracy
6. **Assembly** - Sonnet stitches 12 stories into final collection

**You don't need to coordinate with other agents.** Your story is independent.

---

## Emergency: Stuck on Context?

If you run out of token budget before you have enough context:

**Option A: Reduce secondary context**
- Skip evaluation data (downloads folder files)
- Use Redis summary + local file excerpt
- Usually sufficient (80% of story comes from primary context)

**Option B: Reduce optional context**
- Real incidents are good-to-have, not required
- You can write story with just technical spec
- Real incident references add authenticity but aren't critical

**Option C: Ask Sonnet orchestrator**
- If you legitimately need more context, ask
- Sonnet can allocate extra budget
- But be specific: "Need COMPAS investigation details for Story 7"

**Option D (Last resort): Outline first**
- Draft story outline using context you have
- Run search queries targeted to outline gaps
- Write with complete context on second pass

---

## Submission Format

When you complete your story, submit as:

**File:** `/home/setup/infrafabric/stories/STORY_N_COMPONENT_TITLE.md`
**Format:** Markdown with Archer-style formatting

Example header:
```markdown
# Story 1: IF.yologuard - "The Perfect Detection"

*An Archer-style short story about the InfraFabric component*

---

Marcus Chen stared at the yologuard report in disbelief...

[4,000 words of story]

---

*[Optional] Author's Note on IF.yologuard: [1-2 sentences explaining real component]*
```

---

## Success Looks Like

You're done when:

1. **Story is 3,500-5,000 words** ✓
2. **Opening hook grabs immediately** ✓
3. **Closing punch lands with impact** ✓
4. **Twist illuminates component's deeper meaning** ✓
5. **Technical accuracy maintained without exposition** ✓
6. **Contemporary elements woven naturally** ✓
7. **Archer's rhythm + British English consistent** ✓
8. **Real incidents referenced authentically** ✓
9. **Story stands alone** ✓
10. **You'd want to read it again** ✓

---

## Timeline Estimate

**Per Haiku agent:**
- Context assembly: 15-20 minutes (read Redis + local files)
- Story draft: 45-60 minutes (3,500-5,000 words)
- Quality check: 10-15 minutes (verify checklist)
- Submission: 5 minutes
- **Total: ~75-100 minutes per agent**

**All 12 stories (parallel):**
- Start to finish: ~2 hours wall-clock
- With Sonnet review + assembly: ~2.5-3 hours total
- Publication ready: 3-4 hours from start

---

## Next Steps

1. **Get assigned a story** - Sonnet will tell you which story number
2. **Open this guide + the YAML index**
3. **Follow context assembly protocol** - 15 minutes
4. **Write your story** - 60 minutes
5. **Quality check** - 15 minutes
6. **Submit** - Sonnet handles coordination

You've got this. Write well.

---

**Questions?** Check the YAML index directly:
`/home/setup/infrafabric/IF-STORY-CONTEXT-INDEX.yaml`

**Questions about Archer's style?** Re-read story examples:
"The Perfect Murder," "Just Good Friends," "The Steal"
(From "A Twist in the Tale" collection, 1988)
