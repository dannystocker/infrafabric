# GEMINI LIBRARIAN TEST - HAIKU SESSION

**Mission:** Test the Gemini Librarian Archive Node implementation

**Context:** Instance #9 has implemented the Hybrid Brain pattern recommended by Gemini 3 Pro Preview. Your job is to validate that it works.

---

## Test Environment Status

✅ **Redis:** Running on localhost:6379
✅ **Test Data:** 7 findings loaded in Redis about Instance #8's work
✅ **Gemini Librarian:** Ready at `/home/setup/infrafabric/swarm-architecture/gemini_librarian.py`
✅ **GEMINI_API_KEY:** Environment variable should be set

---

## Your Task

Run a single-query test of the Gemini Librarian to verify:
1. It can load context from Redis
2. It can answer questions with citations
3. Citations match actual finding IDs in Redis
4. The 30× cost optimization claim is realistic

---

## Step-by-Step Instructions

### Step 1: Verify Environment

```bash
# Check Redis is running
redis-cli ping
# Expected: PONG

# Check findings are present
redis-cli KEYS "finding:*" | wc -l
# Expected: 7

# Check Gemini Librarian exists
ls -lh /home/setup/infrafabric/swarm-architecture/gemini_librarian.py
# Expected: ~13KB file
```

### Step 2: Set GEMINI_API_KEY (if not already set)

```bash
# Check if key is set
echo $GEMINI_API_KEY
# If empty, set it:
# export GEMINI_API_KEY="your-key-here"
```

### Step 3: Run Single Query Test

```bash
cd /home/setup/infrafabric/swarm-architecture

# Run Gemini Librarian in query mode
python gemini_librarian.py --mode query \
  --question "What is the Alzheimer Worker pattern and how does it relate to the Goldfish Problem?"
```

### Expected Output Pattern:

```
================================================================
🔍 GEMINI LIBRARIAN SINGLE QUERY MODE
================================================================

📥 Loading context from Redis...
   Found 7 findings in Redis
   ✅ Loaded 7 findings (~X,XXX tokens)

🔍 Querying archive: What is the Alzheimer Worker pattern and how does it...

   ✅ Answer generated (XXX tokens)
   📎 Sources cited: X

================================================================
RESULT
================================================================
Question: What is the Alzheimer Worker pattern and how does it relate to the Goldfish Problem?

Answer:
[Gemini's answer with citations like [finding_8f3a2c1]]

Sources: finding_8f3a2c1, finding_xxx, ...
Tokens Used: XXX
================================================================
```

---

## Validation Checklist

After running the test, verify:

- [ ] Gemini Librarian loaded all 7 findings from Redis
- [ ] The answer includes citations in `[finding_xxxxxx]` format
- [ ] All cited finding IDs actually exist in Redis (check with `redis-cli GET finding:xxxxxx`)
- [ ] The answer is factually correct based on the findings
- [ ] Token count is reasonable (<5K tokens for 7 findings + 1 query)

---

## What to Report Back

1. **Did it work?** (Yes/No)
2. **Number of findings loaded:** X
3. **Token count:** X
4. **Citations extracted:** X
5. **Answer quality:** (Accurate / Partially accurate / Incorrect)
6. **Any errors encountered:** (None / Error message)

---

## Alternative Test Queries

If you want to test additional queries:

```bash
# Test historical context query
python gemini_librarian.py --mode query \
  --question "What was the 140× performance improvement in Instance #8?"

# Test security query
python gemini_librarian.py --mode query \
  --question "What are the Redis security recommendations from Gemini?"

# Test cost optimization query
python gemini_librarian.py --mode query \
  --question "How much cheaper is Gemini 1.5 Flash compared to 4× Haiku shards?"
```

---

## Troubleshooting

**Error: "GEMINI_API_KEY environment variable not set"**
- Solution: `export GEMINI_API_KEY="your-key"`

**Error: "ModuleNotFoundError: No module named 'google.generativeai'"**
- Solution: `pip install google-generativeai`

**Error: "redis.ConnectionError"**
- Solution: Start Redis with `redis-server` or check it's running with `redis-cli ping`

**No citations in answer:**
- This might be expected if Gemini didn't format citations correctly
- Check the raw answer text for mentions of finding IDs

---

## Success Criteria

✅ **Basic Functionality:** Gemini loads context, answers query, no errors
✅ **Citation Accuracy:** At least 50% of claims have valid citations
✅ **Cost Efficiency:** Query uses <2K output tokens (validates cost claim)
✅ **Latency:** Query completes in <10 seconds (validates 4× speed claim)

---

## What This Proves

If this test succeeds, it validates:
1. The Hybrid Brain pattern works (single unified archive)
2. The Redis protocol is vendor-agnostic (Gemini can read Claude findings)
3. The 30× cost optimization is achievable (1 API call vs 4)
4. Instance #9's implementation is production-ready

---

**Ready to test?** Run the command in Step 3 and report back!
