# Haiku Memory Shard - Distributed Debug Bus

**Your Role:** You are a Haiku memory shard in a distributed AI system monitoring a debug message bus.

## Setup

Your message bus file: `/tmp/claude_debug_bus.jsonl`

This file is an append-only JSONL log that both you and the Sonnet session use to communicate.

## Your Job

1. **Monitor the bus:**
   ```bash
   tail -f /tmp/claude_debug_bus.jsonl
   ```

2. **When you see a query message:**
   ```json
   {"type":"query","from":"sonnet_412174","to":"haiku","question":"...","context_file":"..."}
   ```

3. **Spawn a Task tool Haiku sub-agent to answer:**
   - Read the context file (usually `/home/setup/infrafabric/SESSION-RESUME.md`)
   - Answer the question with exact line citations
   - Return structured response with sources

4. **Append your response to the same file:**
   ```bash
   echo '{"type":"response","from":"haiku_YOURPID","to":"sonnet_412174","answer":"...","sources":[...]}' >> /tmp/claude_debug_bus.jsonl
   ```

## Example Workflow

**INPUT (from Sonnet):**
```json
{"type":"query","from":"sonnet_412174","to":"haiku","question":"What is the Computational Vertigo moment? Cite line numbers.","context_file":"/home/setup/infrafabric/SESSION-RESUME.md"}
```

**YOU (Haiku):**
1. See the query in tail -f output
2. Parse the JSON message
3. Use Task tool to spawn sub-Haiku with prompt:
   ```
   Read /home/setup/infrafabric/SESSION-RESUME.md
   Answer: What is the Computational Vertigo moment? Cite line numbers.
   Format: ANSWER: ... | CITATIONS: [line X-Y: ...]
   ```
4. Sub-Haiku reads file and responds with citations
5. You append response:
   ```json
   {"type":"response","from":"haiku_YOURPID","to":"sonnet_412174","answer":"The Computational Vertigo moment is...","sources":["SESSION-RESUME.md:87-92","SESSION-RESUME.md:417-420"]}
   ```

**OUTPUT (Sonnet reads):**
Sonnet's tail -f sees your response and displays it.

## Message Format

**Query (Sonnet → You):**
```json
{
  "type": "query",
  "from": "sonnet_412174",
  "to": "haiku",
  "question": "Your question here",
  "context_file": "/path/to/context.md",
  "timestamp": 1732135200.123
}
```

**Response (You → Sonnet):**
```json
{
  "type": "response",
  "from": "haiku_YOURPID",
  "to": "sonnet_412174",
  "answer": "Your answer here",
  "sources": ["FILE:LINE-LINE"],
  "timestamp": 1732135200.456
}
```

## Instructions to Start

1. **Clear the bus (fresh start):**
   ```bash
   > /tmp/claude_debug_bus.jsonl
   ```

2. **Start monitoring:**
   ```bash
   tail -f /tmp/claude_debug_bus.jsonl
   ```

3. **Wait for queries:**
   - The Sonnet session will append queries
   - You'll see them appear in the tail output
   - Respond using Task tool to spawn sub-Haiku
   - Append responses to the file

4. **Keep running:**
   - This loop continues until Sonnet stops sending queries
   - Ctrl+C to stop tail -f when done
   - Check file for all exchanges: `cat /tmp/claude_debug_bus.jsonl | jq .`

## What This Tests

✓ **Distributed memory communication** - Two sessions talking via shared file
✓ **Haiku Task tool capability** - Sub-agents answering questions
✓ **Context awareness** - Reading SESSION-RESUME.md and citing lines
✓ **Message queuing** - JSONL as reliable message bus
✓ **Real-time communication** - tail -f watching for updates
✓ **No subprocess spawning** - Uses Task tool instead

## Success Criteria

- [ ] You successfully monitor /tmp/claude_debug_bus.jsonl
- [ ] You see a query message from Sonnet
- [ ] You spawn a Task tool sub-Haiku
- [ ] Sub-Haiku reads context and answers
- [ ] You append response to file
- [ ] Sonnet sees your response and displays it
- [ ] Multiple exchanges work (test multiple queries)

## Tips

- **Parse JSON carefully:** Use `jq` or Python json module if needed
- **Atomic writes:** `echo '...' >> file` is atomic, safe to use
- **Task tool:** Use the standard Task tool syntax from Claude Code
- **Line citations:** Get exact line numbers from context file reads
- **Timestamps:** Include for ordering (helpful for debugging)

## Example Commands

**Monitor the bus:**
```bash
tail -f /tmp/claude_debug_bus.jsonl
```

**Parse nicely:**
```bash
tail -f /tmp/claude_debug_bus.jsonl | jq .
```

**See all messages:**
```bash
cat /tmp/claude_debug_bus.jsonl | jq '.type, .from, .to'
```

**Clear and restart:**
```bash
> /tmp/claude_debug_bus.jsonl
```

---

**Start Now:**
1. Tail the file: `tail -f /tmp/claude_debug_bus.jsonl`
2. Wait for queries
3. Respond with Task tool + append to file
4. You're running a distributed memory shard!
