#!/usr/bin/env python3
"""
DEBUG v2: Test subprocess call directly without MCP bridge complexity
"""

import subprocess
import os
import sys

print("="*80)
print("DIRECT SUBPROCESS TEST - No MCP Bridge")
print("="*80)

# Simple test context
test_context = """
Session Resume:
- Instance #4: Infrastructure validation
- Instance #5: Security audit
- Instance #6: Real LLM testing

Key moment: The "Computational Vertigo" moment was when Instance #4
realized they were testing Python simulations, not real Haiku LLMs.
This was documented in SESSION-RESUME.md around line 156.
"""

test_question = "What was the Computational Vertigo moment?"

full_prompt = f"""You are a test memory shard.

Context:
{test_context}

Question: {test_question}

Answer in 1-2 sentences and cite the source."""

print(f"\nTest prompt length: {len(full_prompt)} chars")
print(f"\nEnvironment check:")
print(f"  ANTHROPIC_API_KEY: {'SET (len=' + str(len(os.environ.get('ANTHROPIC_API_KEY', ''))) + ')' if os.environ.get('ANTHROPIC_API_KEY') else 'NOT SET'}")
print(f"  HOME: {os.environ.get('HOME')}")

# Test 1: Try with -p flag
print(f"\n{'='*80}")
print(f"TEST 1: claude --model haiku -p '<prompt>'")
print(f"{'='*80}")

cmd1 = ["claude", "--model", "haiku", "-p", full_prompt]

try:
    print(f"Running command...")
    result1 = subprocess.run(
        cmd1,
        capture_output=True,
        text=True,
        env=os.environ,
        timeout=30
    )

    print(f"\nReturn code: {result1.returncode}")
    print(f"Stdout length: {len(result1.stdout)}")
    print(f"Stderr length: {len(result1.stderr)}")

    print(f"\nStdout:")
    print(result1.stdout if result1.stdout else "(EMPTY)")

    print(f"\nStderr:")
    print(result1.stderr if result1.stderr else "(EMPTY)")

except subprocess.TimeoutExpired:
    print("TIMEOUT!")
except Exception as e:
    print(f"ERROR: {e}")

# Test 2: Try with stdin
print(f"\n{'='*80}")
print(f"TEST 2: echo '<prompt>' | claude --model haiku")
print(f"{'='*80}")

cmd2 = ["claude", "--model", "haiku"]

try:
    print(f"Running command with stdin...")
    result2 = subprocess.run(
        cmd2,
        input=full_prompt,
        capture_output=True,
        text=True,
        env=os.environ,
        timeout=30
    )

    print(f"\nReturn code: {result2.returncode}")
    print(f"Stdout length: {len(result2.stdout)}")
    print(f"Stderr length: {len(result2.stderr)}")

    print(f"\nStdout:")
    print(result2.stdout if result2.stdout else "(EMPTY)")

    print(f"\nStderr:")
    print(result2.stderr if result2.stderr else "(EMPTY)")

except subprocess.TimeoutExpired:
    print("TIMEOUT!")
except Exception as e:
    print(f"ERROR: {e}")

# Test 3: Try checking if claude command exists
print(f"\n{'='*80}")
print(f"TEST 3: which claude")
print(f"{'='*80}")

try:
    result3 = subprocess.run(
        ["which", "claude"],
        capture_output=True,
        text=True
    )
    print(f"Claude location: {result3.stdout.strip()}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 4: Try claude --help
print(f"\n{'='*80}")
print(f"TEST 4: claude --help")
print(f"{'='*80}")

try:
    result4 = subprocess.run(
        ["claude", "--help"],
        capture_output=True,
        text=True,
        timeout=5
    )
    print(f"Help output (first 500 chars):")
    print(result4.stdout[:500] if result4.stdout else "(EMPTY)")
except Exception as e:
    print(f"ERROR: {e}")

print(f"\n{'='*80}")
print(f"DEBUGGING TESTS COMPLETE")
print(f"{'='*80}")
