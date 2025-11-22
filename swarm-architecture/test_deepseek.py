#!/usr/bin/env python3
"""
Test DeepSeek V3 API credentials
Email: dstocker.ca@gmail.com
"""
import requests
import json

API_KEY = "sk-bca3dd2e420f428495f65915701b0244"
MASKED_KEY = f"{API_KEY[:15]}...{API_KEY[-4:]}"

print("=" * 60)
print("DEEPSEEK V3 API TEST")
print("=" * 60)
print()
print(f"API Key: {MASKED_KEY}")
print(f"Email: dstocker.ca@gmail.com")
print(f"Purpose: Redis swarm worker shard")
print()

# Test with simple query
print("Testing DeepSeek V3...")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "deepseek-chat",
    "messages": [{
        "role": "user",
        "content": "Say 'DeepSeek test successful' and nothing else."
    }],
    "max_tokens": 50
}

try:
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=15
    )

    if response.status_code == 200:
        result = response.json()
        message = result['choices'][0]['message']['content']
        usage = result.get('usage', {})

        print(f"✅ SUCCESS")
        print(f"   Status: {response.status_code}")
        print(f"   Model: {result.get('model', 'unknown')}")
        print(f"   Response: {message}")
        print(f"   Usage:")
        print(f"     Prompt tokens: {usage.get('prompt_tokens', 0)}")
        print(f"     Completion tokens: {usage.get('completion_tokens', 0)}")
        print(f"     Total tokens: {usage.get('total_tokens', 0)}")
        print()

        # Calculate cost
        prompt_cost = usage.get('prompt_tokens', 0) * 0.60 / 1_000_000
        completion_cost = usage.get('completion_tokens', 0) * 1.70 / 1_000_000
        total_cost = prompt_cost + completion_cost

        print(f"   Cost for this query:")
        print(f"     Input: ${prompt_cost:.6f}")
        print(f"     Output: ${completion_cost:.6f}")
        print(f"     Total: ${total_cost:.6f}")
        print()
        print("DeepSeek V3 credentials are VALID and working!")

    else:
        print(f"❌ FAILED")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {response.text}")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print()
print("=" * 60)
