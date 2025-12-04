#!/usr/bin/env python3
"""
Secure Claude API Credential Tester
Tests OAuth credentials without exposing tokens in output
"""
import json
import requests
from datetime import datetime

# Load credentials
creds_path = "/mnt/c/users/setup/downloads/.credentials.json"
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
print("CLAUDE API CREDENTIAL TEST")
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
print(f"Status: {'EXPIRED' if is_expired else 'VALID'}")
print()

if is_expired:
    print("⚠️  Token expired. Needs refresh.")
    print()
else:
    # Test with simple API call
    print("Testing API call...")

    headers = {
        "anthropic-version": "2023-06-01",
        "x-api-key": access_token,
        "content-type": "application/json"
    }

    payload = {
        "model": "claude-sonnet-4.5",
        "max_tokens": 50,
        "messages": [{
            "role": "user",
            "content": "Say 'API test successful' and nothing else."
        }]
    }

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            message = result.get('content', [{}])[0].get('text', '')

            print(f"✅ SUCCESS")
            print(f"   Status: {response.status_code}")
            print(f"   Model: {result.get('model', 'unknown')}")
            print(f"   Response: {message}")
            print()
            print("Credentials are VALID and working!")

        else:
            print(f"❌ FAILED")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

print()
print("=" * 60)
