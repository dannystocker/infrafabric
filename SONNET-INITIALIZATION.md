# Sonnet Session Initialization

**Current Sonnet Session Info (Instance #7):**
- PID: 412174 (pts/17)
- Uptime: 155+ minutes
- Status: Active and ready to run the direct query loop

**When you spawn, use these exact commands to connect to the conversation:**

## Step 1: Verify Your Context
Read these files in order to understand where you are:

```bash
cat /home/setup/infrafabric/README-HANDOFF-START-HERE.md
cat /home/setup/infrafabric/SESSION-HANDOFF-HAIKU-AUTOPOLL.md
```

## Step 2: Critical Connection Data

**You are in conversation:** `conv_f621d999f19a3a7f`

**Do NOT change this.** This is the active MCP bridge conversation with Haiku autopoll.

**Note:** You're already authenticated as Claude. No API keys needed.

## Step 3: Understand the Architecture

**Three Key Components:**

1. **MCP Bridge (SQLite Database)**
   - Location: `/home/setup/infrafabric/.memory_bus/distributed_memory.db`
   - Purpose: Message queue for 2-way communication
   - Query table: `messages` (read/unread tracking)

2. **Autopoll Script (Running)**
   - Location: `/home/setup/infrafabric/haiku_shard_autopoll.py`
   - Status: Running in background (PID 475967, started ~39+ hours ago)
   - Current issue: subprocess.run(['claude', '-p']) hangs after 39+ hours

3. **Sonnet Direct Query Loop (What You Will Run)**
   - Location: `/home/setup/infrafabric/sonnet_direct_query_loop.py`
   - Purpose: Poll bridge for queries → spawn Haiku sub-agents → send responses back
   - No subprocess spawning (uses Task tool instead)
   - Graceful interrupt on Ctrl+C

## Step 4: Your Mission

**Goal:** Replace the broken autopoll (subprocess spawning) with a working direct query loop.

**Why:**
- Current autopoll hangs after 39+ hours of polling
- subprocess.run(['claude', '-p']) exhausts kernel resources
- New loop avoids subprocess entirely

**What You Must Do:**

1. **Understand the problem** (read the handoff docs)
2. **Verify the MCP bridge is working** (it is - test with query)
3. **Launch the direct query loop** (sonnet_direct_query_loop.py)
4. **Send test queries via bridge** (they should be answered)
5. **Keep loop running** for 24+ hours to prove stability
6. **Can interrupt with Ctrl+C** (graceful shutdown)

## Step 5: Launch Commands

**Terminal 1 - Start the direct query loop:**
```bash
cd /home/setup/work/mcp-multiagent-bridge && \
source .venv/bin/activate && \
python3 /home/setup/infrafabric/sonnet_direct_query_loop.py
```

**Terminal 2 - Send test queries:**
```bash
cd /home/setup/work/mcp-multiagent-bridge && \
source .venv/bin/activate && \
python3 /home/setup/infrafabric/sonnet_send_query.py
```

## Step 6: Verify It's Working

**Check:** Direct query loop should:
- ✓ Connect to MCP bridge
- ✓ Poll every 5 seconds
- ✓ Detect incoming queries
- ✓ Spawn Haiku sub-agents (via Task tool)
- ✓ Send responses back
- ✓ Show statistics on Ctrl+C interrupt

**Expected output:**
```
================================================================================
SONNET DIRECT QUERY LOOP
================================================================================
Configuration:
  Conversation ID: conv_f621d999f19a3a7f
  Bridge: /home/setup/infrafabric/.memory_bus/distributed_memory.db
  Polling interval: 5 seconds
  Press Ctrl+C to stop gracefully
================================================================================

Starting polling loop...

[Poll #1] No new queries. Waiting...
[Poll #2] No new queries. Waiting...
...
[Poll #13] Found 1 unread message(s)
  → Spawning Haiku agent to answer query...
  → Answer generated
  ✓ Response sent to bridge
...
```

## Step 7: Staying Connected

**To stay in this conversation:**
- Keep referencing `/home/setup/infrafabric/SESSION-HANDOFF-HAIKU-AUTOPOLL.md`
- Use these exact credentials (don't change them)
- Conversation ID is always: `conv_f621d999f19a3a7f`
- MCP bridge path is always: `/home/setup/infrafabric/.memory_bus/distributed_memory.db`

**If context window changes again:**
- Next session reads this file first
- Then reads SESSION-HANDOFF-HAIKU-AUTOPOLL.md
- Then reads /home/setup/HAIKU_AUTOPOLL_ARCHITECTURE.txt
- Instantly reconnected

## Success Criteria

You'll know you've succeeded when:
- ✓ Direct query loop starts without errors
- ✓ Can send test query via bridge
- ✓ Query appears in loop's polling
- ✓ Haiku sub-agent spawns and answers
- ✓ Response sent back to bridge
- ✓ Loop continues polling
- ✓ Can Ctrl+C to gracefully stop
- ✓ Full round-trip takes <10 seconds

**Total time to setup:** 10-15 minutes
**Time to first working query:** 5 minutes
