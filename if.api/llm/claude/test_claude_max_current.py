#!/usr/bin/env python3
"""
Test Claude Max credentials from /home/setup/.claude/.credentials.json
"""
import json
import requests
from datetime import datetime

# Load credentials
creds_path = "/home/setup/.claude/.credentials.json"
with open(creds_path, 'r') as f:
    creds = json.load(f)

oauth = creds['claudeAiOauth']
access_token = oauth['accessToken']
expires_at = oauth['expiresAt']
subscription = oauth['subscriptionType']
rate_limit = oauth['rateLimitTier']

# Mask token for display
masked_token = f"{access_token[:15]}...{access_token[-4:]}"

print("=" * 60)
print("CLAUDE MAX API CREDENTIAL TEST")
print("=" * 60)
print()
print(f"Token: {masked_token}")
print(f"Subscription: {subscription}")
print(f"Rate Limit: {rate_limit}")
print()

# Check expiry
expires_dt = datetime.fromtimestamp(expires_at / 1000)
now = datetime.now()
is_expired = now > expires_dt

print(f"Expires: {expires_dt.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Status: {'✅ VALID' if not is_expired else '❌ EXPIRED'}")
print()

if is_expired:
    print("⚠️  Token expired. Cannot test.")
    exit(1)

# Test with Haiku 4.5
print("Testing Claude Haiku 4.5...")

headers = {
    "anthropic-version": "2023-06-01",
    "x-api-key": access_token,
    "content-type": "application/json"
}

payload = {
    "model": "claude-haiku-4.5",
    "max_tokens": 50,
    "messages": [{
        "role": "user",
        "content": "Say 'Claude Max test successful' and nothing else."
    }]
}

try:
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=payload,
        timeout=15
    )

    if response.status_code == 200:
        result = response.json()
        message = result.get('content', [{}])[0].get('text', '')
        usage = result.get('usage', {})

        print(f"✅ SUCCESS")
        print(f"   Status: {response.status_code}")
        print(f"   Model: {result.get('model', 'unknown')}")
        print(f"   Response: {message}")
        print()
        print(f"   Usage:")
        print(f"     Input tokens: {usage.get('input_tokens', 0)}")
        print(f"     Output tokens: {usage.get('output_tokens', 0)}")
        print(f"     Total tokens: {usage.get('input_tokens', 0) + usage.get('output_tokens', 0)}")
        print()
        print(f"   Cost via Max Plan: $0 (included in subscription)")
        print(f"   Cost via API (if paying): ${usage.get('input_tokens', 0) * 1.00 / 1_000_000 + usage.get('output_tokens', 0) * 5.00 / 1_000_000:.6f}")
        print()
        print("🎉 Claude Max credentials are VALID and working!")

    else:
        print(f"❌ FAILED")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {response.text}")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print()
print("=" * 60)
