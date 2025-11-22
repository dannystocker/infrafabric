#!/usr/bin/env python3
"""
FILE: ~/infrafabric/copilot_shard.py
PURPOSE: Headless Interface to Windows Copilot / Bing Chat
DEPENDENCIES: pip install sydney-py
USAGE: python3 copilot_shard.py "Your prompt here"

ARCHITECTURE CONTEXT:
- This is "Tool A: The Thinking Shard" from the distributed memory system
- Uses reverse-engineered Bing Chat API (sydney-py, successor to EdgeGPT)
- Outputs pure JSON for MCP bridge integration
- Bypasses Windows Copilot sidebar UI entirely (headless operation)

COOKIE REQUIREMENT:
- Must have cookies.json in same directory
- Extract from bing.com/chat using browser console snippet
- Format: JSON array of cookie objects
- Note: sydney-py expects cookies as formatted string, not JSON

CHANGELOG:
- 2025-11-20: Migrated from EdgeGPT to sydney-py (EdgeGPT unmaintained)
"""

import asyncio
import sys
import json
from pathlib import Path
from sydney import SydneyClient

# Path to cookies file (MUST EXIST)
COOKIES_FILE = Path(__file__).parent / "cookies.json"


def cookies_json_to_string(cookies_list: list) -> str:
    """
    Convert cookies.json format to sydney-py expected format.

    Sydney expects: "name1=value1; name2=value2; ..."

    Note: Includes ALL cookies regardless of domain to maximize compatibility
    """
    cookie_pairs = []
    for c in cookies_list:
        # Skip empty values
        if c.get('value'):
            cookie_pairs.append(f"{c['name']}={c['value']}")
    return "; ".join(cookie_pairs)


async def query_copilot(prompt: str) -> dict:
    """
    Query Windows Copilot backend (Bing Chat) with a prompt.

    Args:
        prompt: The question or instruction to send

    Returns:
        dict: Response from Copilot in structured format
    """
    try:
        # Load cookies
        if not COOKIES_FILE.exists():
            return {
                "error": "cookies.json not found",
                "help": "Extract cookies from bing.com/chat using browser console snippet",
                "path": str(COOKIES_FILE)
            }

        with open(COOKIES_FILE, 'r') as f:
            cookies_json = json.load(f)

        # Convert to sydney-py format (all cookies from copilot.microsoft.com)
        cookies_string = cookies_json_to_string(cookies_json)

        # Diagnostic: check what we're sending
        has_u_cookie = any(c.get('name') == '_U' for c in cookies_json)
        if not has_u_cookie:
            # Log warning but continue (copilot.microsoft.com might not need _U)
            print(f"WARNING: No _U cookie found. Cookies: {[c.get('name') for c in cookies_json]}", file=sys.stderr)

        # Initialize Sydney client (creative style for best reasoning)
        async with SydneyClient(style="creative", bing_cookies=cookies_string) as client:
            # Ask question
            response = await client.ask(prompt=prompt, citations=True)

            # Return structured response
            return {
                "status": "success",
                "prompt": prompt,
                "response": response,
                "model": "copilot-creative",
                "library": "sydney-py"
            }

    except Exception as e:
        return {
            "status": "error",
            "prompt": prompt,
            "error": str(e),
            "error_type": type(e).__name__
        }


async def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        error_response = {
            "error": "No prompt provided",
            "usage": "python3 copilot_shard.py \"Your prompt here\"",
            "example": "python3 copilot_shard.py \"What is 2+2?\""
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)

    # Get prompt from command line args
    prompt = " ".join(sys.argv[1:])

    # Query Copilot
    result = await query_copilot(prompt)

    # Output pure JSON to stdout
    print(json.dumps(result, indent=2))

    # Exit with error code if query failed
    if result.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
