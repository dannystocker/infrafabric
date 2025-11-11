#!/usr/bin/env python3
"""
IF.swarm Parallel Session Orchestrator

Automates launching multiple Claude sessions in parallel using:
- Git worktrees (separate working directories)
- Claude API (concurrent execution)
- Session starters (automated prompt injection)

Requirements:
    pip install anthropic gitpython pyyaml

Usage:
    export ANTHROPIC_API_KEY="your-key"
    python tools/parallel-session-orchestrator.py --phase 1
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import json
import yaml
from datetime import datetime

try:
    import anthropic
    from anthropic import AsyncAnthropic
except ImportError:
    print("ERROR: anthropic library not installed")
    print("Install: pip install anthropic")
    sys.exit(1)

try:
    import git
except ImportError:
    print("ERROR: gitpython not installed")
    print("Install: pip install gitpython")
    sys.exit(1)


class SessionOrchestrator:
    """Orchestrates parallel Claude Code sessions using API"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.repo = git.Repo(repo_path)
        self.base_branch = "claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy"
        self.worktree_dir = self.repo_path / ".worktrees"
        self.progress_file = self.repo_path / "progress.yaml"

        # Initialize API client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = AsyncAnthropic(api_key=api_key)

    def create_worktree(self, session_name: str, branch_name: str) -> Path:
        """Create git worktree for parallel session"""
        worktree_path = self.worktree_dir / session_name

        if worktree_path.exists():
            print(f"  Worktree already exists: {worktree_path}")
            return worktree_path

        # Create worktree from base branch
        print(f"  Creating worktree: {worktree_path}")
        subprocess.run([
            "git", "worktree", "add",
            "-b", branch_name,
            str(worktree_path),
            self.base_branch
        ], cwd=self.repo_path, check=True)

        return worktree_path

    def load_session_config(self) -> Dict:
        """Load session configuration from YAML"""
        config = {
            "phase1": [
                {
                    "name": "session-1-ndi",
                    "file": "docs/SESSION-STARTERS/session-1-ndi-witness.md",
                    "branch": "claude/realtime-workstream-1-ndi",
                    "model": "claude-sonnet-4-20250514",
                    "budget": 20,
                    "hours": 14,
                },
                {
                    "name": "session-2-webrtc",
                    "file": "docs/SESSION-STARTERS/session-2-webrtc-swarm.md",
                    "branch": "claude/realtime-workstream-2-webrtc",
                    "model": "claude-sonnet-4-20250514",  # GPT-5 not available via API
                    "budget": 12,
                    "hours": 12,
                },
                {
                    "name": "session-3-h323",
                    "file": "docs/SESSION-STARTERS/session-3-h323-guard.md",
                    "branch": "claude/realtime-workstream-3-h323",
                    "model": "claude-sonnet-4-20250514",  # Gemini not available
                    "budget": 30,
                    "hours": 24,
                },
                {
                    "name": "session-cli",
                    "file": "docs/SESSION-STARTERS/session-parallel-cli-witness.md",
                    "branch": "claude/cli-witness-optimise",
                    "model": "claude-sonnet-4-20250514",
                    "budget": 20,
                    "hours": 16,
                },
            ],
            "phase2": [
                {
                    "name": "session-4-sip",
                    "file": "docs/SESSION-STARTERS/session-4-sip-escalate.md",
                    "branch": "claude/realtime-workstream-4-sip",
                    "model": "claude-sonnet-4-20250514",
                    "budget": 25,
                    "hours": 20,
                    "depends_on": ["session-2-webrtc", "session-3-h323"],
                },
            ],
        }
        return config

    def extract_session_prompt(self, session_file: Path) -> str:
        """Extract 'Copy-Paste This' prompt from session starter"""
        content = session_file.read_text()

        # Find the code block with the prompt
        start_marker = "```\n"  # After "Copy-Paste This Into New Claude Code Session"
        end_marker = "\n```"

        start_idx = content.find(start_marker)
        if start_idx == -1:
            raise ValueError(f"Could not find prompt in {session_file}")

        start_idx += len(start_marker)
        end_idx = content.find(end_marker, start_idx)

        if end_idx == -1:
            raise ValueError(f"Could not find end of prompt in {session_file}")

        prompt = content[start_idx:end_idx].strip()
        return prompt

    async def run_session(self, session: Dict, worktree_path: Path) -> Dict:
        """Run a single session using Claude API"""
        session_name = session["name"]
        print(f"\n{'='*60}")
        print(f"Starting: {session_name}")
        print(f"Worktree: {worktree_path}")
        print(f"Model: {session['model']}")
        print(f"{'='*60}\n")

        # Load session prompt
        session_file = self.repo_path / session["file"]
        prompt = self.extract_session_prompt(session_file)

        # Add context about worktree
        full_prompt = f"""
WORKTREE: {worktree_path}
BRANCH: {session['branch']}

{prompt}

IMPORTANT: You are running in a git worktree at {worktree_path}.
All file operations should be relative to this directory.
When you commit, you're committing to branch {session['branch']}.
"""

        messages = [{"role": "user", "content": full_prompt}]

        # Track conversation
        conversation = []
        max_turns = 50  # Safety limit
        turn = 0

        start_time = datetime.now()
        total_tokens = 0

        try:
            while turn < max_turns:
                turn += 1
                print(f"\n[{session_name}] Turn {turn}")

                # Call Claude API
                response = await self.client.messages.create(
                    model=session["model"],
                    max_tokens=8000,
                    messages=messages,
                    temperature=0.0,
                )

                # Track tokens
                total_tokens += response.usage.input_tokens + response.usage.output_tokens

                # Get assistant response
                assistant_message = response.content[0].text
                conversation.append({
                    "turn": turn,
                    "role": "assistant",
                    "content": assistant_message[:500] + "..." if len(assistant_message) > 500 else assistant_message,
                })

                print(f"[{session_name}] Assistant: {assistant_message[:200]}...")

                # Check if session is complete
                if "workstream" in assistant_message.lower() and "complete" in assistant_message.lower():
                    print(f"\n✅ [{session_name}] Session complete!")
                    break

                if "pushed to" in assistant_message.lower() or "push successful" in assistant_message.lower():
                    print(f"\n✅ [{session_name}] Push detected, session likely complete!")
                    break

                # TODO: Check for tool use and execute (not supported in simple API)
                # For now, we'll just log that this is a limitation
                print(f"⚠️  [{session_name}] Note: Tool execution not automated in this version")
                print(f"    Session will need manual completion or Claude Code CLI")
                break

        except Exception as e:
            print(f"\n❌ [{session_name}] Error: {e}")
            return {
                "session": session_name,
                "status": "error",
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds(),
                "tokens": total_tokens,
            }

        duration = (datetime.now() - start_time).total_seconds()

        return {
            "session": session_name,
            "status": "complete",
            "duration": duration,
            "tokens": total_tokens,
            "turns": turn,
            "conversation": conversation,
        }

    async def run_phase(self, phase: int):
        """Run all sessions in a phase concurrently"""
        config = self.load_session_config()
        phase_key = f"phase{phase}"

        if phase_key not in config:
            print(f"❌ Phase {phase} not found in config")
            return

        sessions = config[phase_key]
        print(f"\n🚀 Launching Phase {phase}: {len(sessions)} sessions")

        # Create worktrees
        worktrees = {}
        for session in sessions:
            worktree_path = self.create_worktree(session["name"], session["branch"])
            worktrees[session["name"]] = worktree_path

        # Run sessions concurrently
        tasks = [
            self.run_session(session, worktrees[session["name"]])
            for session in sessions
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Print summary
        print("\n" + "="*60)
        print("PHASE SUMMARY")
        print("="*60)

        for result in results:
            if isinstance(result, Exception):
                print(f"❌ Error: {result}")
            else:
                status_icon = "✅" if result["status"] == "complete" else "❌"
                print(f"{status_icon} {result['session']}: {result['status']}")
                print(f"   Duration: {result['duration']:.1f}s")
                print(f"   Tokens: {result.get('tokens', 0):,}")

        # Save results
        results_file = self.repo_path / f"phase{phase}-results.json"
        with open(results_file, "w") as f:
            json.dump([r for r in results if not isinstance(r, Exception)], f, indent=2, default=str)
        print(f"\n📊 Results saved to: {results_file}")

    def cleanup_worktrees(self):
        """Remove all worktrees"""
        if not self.worktree_dir.exists():
            print("No worktrees to clean up")
            return

        print(f"Cleaning up worktrees in {self.worktree_dir}")
        subprocess.run(["git", "worktree", "prune"], cwd=self.repo_path)

        for worktree in self.worktree_dir.iterdir():
            if worktree.is_dir():
                subprocess.run(["git", "worktree", "remove", str(worktree)], cwd=self.repo_path)

        self.worktree_dir.rmdir()
        print("✅ Worktrees cleaned up")


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="IF.swarm Parallel Session Orchestrator")
    parser.add_argument("--phase", type=int, choices=[1, 2], help="Phase to run (1 or 2)")
    parser.add_argument("--cleanup", action="store_true", help="Clean up worktrees")
    parser.add_argument("--repo", default=".", help="Repository path")

    args = parser.parse_args()

    orchestrator = SessionOrchestrator(repo_path=args.repo)

    if args.cleanup:
        orchestrator.cleanup_worktrees()
        return

    if args.phase:
        await orchestrator.run_phase(args.phase)
    else:
        print("Usage: python parallel-session-orchestrator.py --phase 1")
        print("       python parallel-session-orchestrator.py --phase 2")
        print("       python parallel-session-orchestrator.py --cleanup")


if __name__ == "__main__":
    asyncio.run(main())
