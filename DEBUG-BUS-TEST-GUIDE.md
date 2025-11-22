# Debug Bus Test - Distributed Memory Communication

**Goal:** Test distributed memory communication between Sonnet and Haiku sessions using a simple JSONL file as a message bus.

**Why:** Prove that both sessions can communicate without MCP bridge complexity or subprocess spawning issues.

## The Setup

### File: `/tmp/claude_debug_bus.jsonl`
- Append-only JSONL log
- Both sessions can read/write atomically
- Messages flow in real-time

### Two Sessions

**Sonnet (Instance #7 or #8):**
- Sends queries
- Monitors responses
- Uses: `sonnet_query_sender.py`

**Haiku (Any Haiku session):**
- Watches for queries
- Uses Task tool to spawn sub-Haiku
- Appends responses
- Uses: `HAIKU-MEMORY-SHARD-PROMPT.md`

## Quick Start

### Terminal 1: Haiku Session

Give the Haiku session this prompt:

```
You are a Haiku memory shard monitoring /tmp/claude_debug_bus.jsonl

Instructions:
1. Start monitoring: tail -f /tmp/claude_debug_bus.jsonl
2. When you see {"type":"query","to":"haiku",...}
3. Use Task tool to spawn sub-Haiku that reads /home/setup/infrafabric/SESSION-RESUME.md and answers the question with line citations
4. Append response: echo '{"type":"response","from":"haiku_YOURPID","answer":"...","sources":[...]}' >> /tmp/claude_debug_bus.jsonl

Watch for queries and respond with Task tool sub-agents.
Read: /home/setup/infrafabric/HAIKU-MEMORY-SHARD-PROMPT.md for complete details.
```

### Terminal 2: Sonnet (You)

Run the query sender:

```bash
python3 /home/setup/infrafabric/sonnet_query_sender.py
```

This will:
- Send 3 test queries
- Wait for Haiku responses
- Show results in real-time
- Print final summary

## Message Flow

```
Sonnet Appends Query
  ↓
  echo '{"type":"query","from":"sonnet_412174","to":"haiku","question":"...","context_file":"..."}' >> /tmp/claude_debug_bus.jsonl
  ↓
Haiku Monitoring with tail -f
  ↓ Sees query
  ↓
Haiku Spawns Task Tool Sub-Haiku
  ├─ Reads context file
  ├─ Answers question
  └─ Gets line citations
  ↓
Haiku Appends Response
  ↓
  echo '{"type":"response","from":"haiku_PID","to":"sonnet_412174","answer":"...","sources":[...]}' >> /tmp/claude_debug_bus.jsonl
  ↓
Sonnet Monitoring tail -f
  ↓ Sees response
  ↓
Sonnet Displays Answer
```

## Message Format

**Query (Sonnet → Haiku):**
```json
{
  "type": "query",
  "from": "sonnet_412174",
  "to": "haiku",
  "question": "What is computational vertigo?",
  "context_file": "/home/setup/infrafabric/SESSION-RESUME.md",
  "timestamp": 1732139400.123
}
```

**Response (Haiku → Sonnet):**
```json
{
  "type": "response",
  "from": "haiku_429752",
  "to": "sonnet_412174",
  "answer": "Computational Vertigo is the phenomenological experience of an AI error...",
  "sources": ["SESSION-RESUME.md:87-92", "SESSION-RESUME.md:417-420"],
  "timestamp": 1732139410.456
}
```

## Step-by-Step Test

### Step 1: Clear the Bus (Fresh Start)
```bash
> /tmp/claude_debug_bus.jsonl
```

### Step 2: Haiku Session - Start Monitoring
Give Haiku this command:
```bash
tail -f /tmp/claude_debug_bus.jsonl
```

And give Haiku the full prompt from `/home/setup/infrafabric/HAIKU-MEMORY-SHARD-PROMPT.md`

### Step 3: Sonnet Session - Send Test Query
```bash
python3 /home/setup/infrafabric/sonnet_query_sender.py
```

The script will:
1. Send first test query
2. Wait up to 30 seconds for response
3. Display response when received
4. Send next query
5. Continue for all 3 test queries

### Step 4: Monitor Results
In another Sonnet terminal, watch the bus in real-time:
```bash
tail -f /tmp/claude_debug_bus.jsonl | jq '.'
```

Or see the raw JSON:
```bash
tail -f /tmp/claude_debug_bus.jsonl
```

## Test Queries

The `sonnet_query_sender.py` sends these 3 queries:

1. **"What is the Computational Vertigo moment? Cite line numbers."**
   - Tests context reading and line citations
   - Expected: Lines from SESSION-RESUME.md

2. **"What were the key achievements of Instance #6? Cite line numbers."**
   - Tests specific context extraction
   - Expected: Multiple line citations

3. **"What is IF.TTT and why is it mandatory? Cite your sources."**
   - Tests knowledge extraction and source documentation
   - Expected: File paths and line ranges

## Success Criteria

- [ ] Haiku's tail -f shows queries appearing
- [ ] Haiku spawns Task tool sub-Haiku for each query
- [ ] Sub-Haiku reads SESSION-RESUME.md
- [ ] Sub-Haiku provides answers with line citations
- [ ] Haiku appends response to bus file
- [ ] Sonnet's tail -f sees responses
- [ ] All 3 test queries get responses
- [ ] Round-trip time < 30 seconds per query
- [ ] Responses have correct line citations

## Troubleshooting

**Haiku not seeing queries?**
- Check tail -f is still running
- Verify /tmp/claude_debug_bus.jsonl exists
- Manually echo a test query: `echo '{"type":"query","to":"haiku","question":"test"}' >> /tmp/claude_debug_bus.jsonl`

**Sonnet not seeing responses?**
- Check Haiku is appending correctly
- View bus contents: `cat /tmp/claude_debug_bus.jsonl | jq '.'`
- Verify responses have `"to":"sonnet_412174"`

**Task tool spawn failing?**
- Check Haiku has access to Task tool
- Verify SESSION-RESUME.md exists at `/home/setup/infrafabric/SESSION-RESUME.md`
- Test manually: Have Haiku read the file directly

**JSON parsing issues?**
- Use `jq` to validate: `cat /tmp/claude_debug_bus.jsonl | jq '.' || echo "Invalid JSON"`
- Check for newlines in messages (should be single-line JSON)

## Files Referenced

- **Bus file:** `/tmp/claude_debug_bus.jsonl`
- **Context:** `/home/setup/infrafabric/SESSION-RESUME.md`
- **Haiku prompt:** `/home/setup/infrafabric/HAIKU-MEMORY-SHARD-PROMPT.md`
- **Sonnet script:** `/home/setup/infrafabric/sonnet_query_sender.py`

## What This Proves

✅ **Distributed communication works** - Two AI sessions talking via shared file
✅ **No MCP bridge needed** - Simple JSONL is sufficient
✅ **No subprocess spawning** - Uses Task tool natively
✅ **Task tool can spawn sub-agents** - Multi-level agents working
✅ **Context reading works** - Sub-Haiku can read and cite files
✅ **Atomic appends are safe** - No file locking issues
✅ **Real-time monitoring works** - tail -f sees updates instantly

## Next Steps After Success

1. Document the round-trip latency observed
2. Test with more queries (stress test)
3. Verify consistency of responses
4. Use this pattern to upgrade sonnet_direct_query_loop.py
5. Move from JSONL debug bus to proper MCP bridge

---

**Ready to test?**

1. Give Haiku the prompt from `HAIKU-MEMORY-SHARD-PROMPT.md`
2. Have Haiku run: `tail -f /tmp/claude_debug_bus.jsonl`
3. You run: `python3 /home/setup/infrafabric/sonnet_query_sender.py`
4. Watch the magic happen! 🎯
