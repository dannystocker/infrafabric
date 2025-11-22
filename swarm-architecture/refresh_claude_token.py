#!/usr/bin/env python3
"""
Refresh Claude OAuth Token and Test with Haiku
"""
import json
import requests
from datetime import datetime

# Load credentials
creds_path = "/mnt/c/users/setup/downloads/.credentials.json"
with open(creds_path, 'r') as f:
    creds = json.load(f)

oauth = creds['claudeAiOauth']
refresh_token = oauth['refreshToken']

print("=" * 60)
print("CLAUDE OAUTH TOKEN REFRESH")
print("=" * 60)
print()

# Refresh the token
print("Refreshing access token...")

refresh_payload = {
    "grant_type": "refresh_token",
    "refresh_token": refresh_token
}

try:
    # OAuth refresh endpoint
    refresh_response = requests.post(
        "https://api.anthropic.com/v1/oauth/token",
        json=refresh_payload,
        timeout=10
    )

    if refresh_response.status_code == 200:
        new_oauth = refresh_response.json()

        # Update credentials
        creds['claudeAiOauth']['accessToken'] = new_oauth['access_token']
        creds['claudeAiOauth']['refreshToken'] = new_oauth.get('refresh_token', refresh_token)
        creds['claudeAiOauth']['expiresAt'] = new_oauth['expires_at']

        # Save updated credentials
        with open(creds_path, 'w') as f:
            json.dump(creds, f, indent=2)

        new_token = new_oauth['access_token']
        masked = f"{new_token[:15]}...{new_token[-4:]}"
        expires_dt = datetime.fromtimestamp(new_oauth['expires_at'] / 1000)

        print(f"✅ Token refreshed successfully!")
        print(f"   New Token: {masked}")
        print(f"   Expires: {expires_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Test with Haiku
        print("Testing with Claude Haiku 4.5...")

        headers = {
            "anthropic-version": "2023-06-01",
            "x-api-key": new_token,
            "content-type": "application/json"
        }

        payload = {
            "model": "claude-haiku-4.5",
            "max_tokens": 50,
            "messages": [{
                "role": "user",
                "content": "Say 'Haiku test successful' and nothing else."
            }]
        }

        test_response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=10
        )

        if test_response.status_code == 200:
            result = test_response.json()
            message = result.get('content', [{}])[0].get('text', '')

            print(f"✅ HAIKU TEST SUCCESS")
            print(f"   Model: {result.get('model', 'unknown')}")
            print(f"   Response: {message}")
            print(f"   Usage: {result.get('usage', {})}")
            print()
            print("Credentials refreshed and working with Haiku!")
        else:
            print(f"❌ Haiku test failed: {test_response.status_code}")
            print(f"   {test_response.text}")

    else:
        print(f"❌ Refresh failed: {refresh_response.status_code}")
        print(f"   {refresh_response.text}")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print()
print("=" * 60)
