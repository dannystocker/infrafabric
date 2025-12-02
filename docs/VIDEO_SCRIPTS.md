# InfraFabric Video Script Outlines

**Document ID:** if://doc/video-scripts/2025-11-30
**Created:** 2025-11-30
**Purpose:** Video content strategy for quickstart and deep dive educational series
**Target Audience:** New users (quickstart), advanced users (deep dive)
**Status:** Production-ready outlines

---

## 1. Quickstart Video (5 minutes)

### Video 1: InfraFabric Quickstart (5 min)

**Target Audience:** New users, CLI users, developers unfamiliar with multi-agent systems
**Goal:** Get user authenticated and making first API call in 5 minutes
**Learning Objectives:**
- Install InfraFabric CLI
- Authenticate securely with OAuth
- Execute first API call
- Understand basic capabilities

---

### **[0:00-0:30] Introduction**

**Narration:**
"InfraFabric is a multi-agent AI coordination platform that makes it easy to build, secure, and scale AI applications. In the next five minutes, you'll install the CLI, authenticate securely, and make your first API call. Let's get started."

**Visual Elements:**
- InfraFabric logo animation (2 seconds)
- Platform capabilities montage (feature highlights)
- Key benefits callout (3 bullets)

**Key Points:**
- What is InfraFabric?
  - Multi-agent AI coordination platform
  - Secure authentication (OAuth + Ed25519)
  - Swarm communication (Redis-based)
- What you'll learn:
  - Install CLI
  - Authenticate with OAuth
  - Make your first API call

---

### **[0:30-1:30] Installation (60 seconds)**

**Narration:**
"Installing InfraFabric is straightforward using pip. Just one command gets you started. [pause 2s] Let's check that it installed correctly."

**Screen Recording:**
```bash
# Install InfraFabric CLI
$ pip install infrafabric-cli
Collecting infrafabric-cli
  Downloading infrafabric-cli-1.0.0-py3-none-any.whl
Installing collected packages: infrafabric-cli
Successfully installed infrafabric-cli-1.0.0

# Verify installation
$ infrafabric --version
infrafabric-cli v1.0.0

# Check help
$ infrafabric --help
Usage: infrafabric [OPTIONS] COMMAND [ARGS]...
  InfraFabric CLI v1.0.0
...
```

**Timing Markers:**
- 0:30 - Command typed
- 0:35 - Output shows
- 0:45 - Version check
- 1:00 - Help displayed
- 1:30 - Section complete

**Visual Notes:**
- Large terminal font (18pt)
- High contrast background
- Pause 2 seconds after each command
- Highlight the version number

---

### **[1:30-3:00] Authentication - OAuth PKCE (90 seconds)**

**Narration:**
"Now let's authenticate. [pause] InfraFabric uses OAuth PKCE flow for secure authentication. This means no passwords are stored locally—just secure tokens. Your browser will open automatically."

**Screen Recording:**
```bash
# Login with Google OAuth
$ infrafabric auth login --provider google

[PAUSE 2 SECONDS]

# [Browser opens automatically]
# [Shows Google login page]
# [User clicks "Authorize"]
# [Browser shows success message: "Authorization successful. You can close this window."]

[PAUSE 3 SECONDS]

# Back in terminal
$ Authorization successful. You are logged in as: user@example.com

# Verify authentication status
$ infrafabric auth status

Authenticated: YES
User: user@example.com
Provider: google
Token Issued: 2025-11-30T10:15:30Z
Token Expires: 2025-11-30T11:15:30Z (1 hour)
Key Pair Status: Generated and secured
```

**Timing Markers:**
- 1:30 - Login command typed
- 1:35 - Command executed
- 1:40 - Browser opens (show browser window overlay)
- 1:50 - Google login page visible
- 2:00 - User clicks authorize
- 2:10 - Success page shown
- 2:15 - Return to terminal
- 2:20 - Status check
- 2:45 - Full output visible
- 3:00 - Section complete

**Visual Notes:**
- Show both terminal and browser windows
- Cursor highlighting for "Authorize" button
- Emphasis on "no passwords stored"
- Highlight token expiration (security detail)

---

### **[3:00-4:00] First API Call (60 seconds)**

**Narration:**
"You're now authenticated. Let's explore the available models and send your first API call. [pause] You can query Claude Opus, Sonnet, or Haiku models."

**Screen Recording:**
```bash
# List available models
$ infrafabric models list

Available Models:
  ✓ claude-opus-4.5     (200K context, $15/1M tokens)
  ✓ claude-sonnet-4.5   (200K context, $3/1M tokens)
  ✓ claude-haiku-4.5    (200K context, $0.80/1M tokens)

# Send a message to default model (Sonnet)
$ infrafabric chat "What is InfraFabric and how does it differ from other AI platforms?"

[PAUSE 2 SECONDS - simulating API latency]

Response:
"InfraFabric is a multi-agent AI coordination platform designed for
production deployments. Key differences:

1. **Security First**: Built-in OAuth PKCE, Ed25519 signing, encrypted
   context sharing
2. **Multi-Agent Swarms**: Coordinate hundreds of agents (Sonnet
   coordinators + Haiku workers)
3. **Traceability**: IF.TTT framework (Traceable, Transparent, Trustworthy)
   for audit trails
4. **Production-Ready**: Includes rate limiting, input sanitization,
   crisis detection

Unlike ChatGPT or general APIs, InfraFabric handles complex multi-agent
workflows with cryptographic verification."

# Try another query
$ infrafabric chat "Show me a code example" --model haiku-4.5

[Quick response from Haiku]

Response:
"Here's a Python example of multi-agent coordination..."
[code block shown]
```

**Timing Markers:**
- 3:00 - Models list command
- 3:10 - Output visible
- 3:20 - Chat command typed
- 3:25 - Command executed
- 3:35 - API latency pause
- 3:45 - Response begins streaming
- 4:00 - Response complete

**Visual Notes:**
- Show checkmarks for available models
- Highlight cost differences (Haiku cheaper)
- Streaming response animation
- Show response formatting with bold, indentation

---

### **[4:00-4:45] Next Steps & Capabilities (45 seconds)**

**Narration:**
"Now you've made your first API call. But InfraFabric does much more. [pause] You can build multi-agent swarms for complex tasks, sign messages with Ed25519 for identity verification, and coordinate workflows across teams."

**Visual Elements:**
- Capabilities grid (6 boxes):
  1. Multi-Swarm Coordination
  2. Cryptographic Signing
  3. Context Sharing
  4. Rate Limiting
  5. Audit Trails
  6. Production Deployment

**Narration - Exploration Path:**
"Explore advanced features:
- **Multi-Swarm Coordination**: Deploy 40+ agents working in parallel
- **Ed25519 Signing**: Cryptographically verify agent identity
- **Context Sharing**: Pass state between agents securely
- **Rate Limiting**: Protect your APIs from abuse
- **Audit Trails**: Track every action with IF.TTT framework
- **Production Deployment**: Docker, Kubernetes, Vault integration"

**Call-to-Action Options:**
- "Read the full documentation at docs.infrafabric.io"
- "Join our community: discord.gg/infrafabric"
- "Try the examples: github.com/infrafabric/examples"

**Timing Markers:**
- 4:00 - Narration starts
- 4:10 - Capabilities grid appears
- 4:30 - Call-to-action links shown
- 4:45 - Section complete

---

### **[4:45-5:00] Outro (15 seconds)**

**Narration:**
"That's the quickstart. You now have everything you need to start building with InfraFabric. Try it yourself, and we'll see you in the next video. [pause] Thanks for watching!"

**Visual Elements:**
- InfraFabric logo (centered)
- Subscribe/Like/Comment cards
- Next video recommendation (if part of series)
- Links overlay (3 seconds):
  - docs.infrafabric.io
  - github.com/infrafabric
  - discord.gg/infrafabric

---

## 2. Deep Dive Series (6 Videos)

### Video 2: OAuth PKCE Flow Explained (10 minutes)

**Target Audience:** Security-conscious developers, compliance teams
**Goal:** Understand why PKCE matters and how to implement it
**Prerequisites:** Understanding of OAuth 2.0 basics

**[0:00-0:45] Introduction**

**Narration:**
"Authorization Code Interception Attack. It sounds scary, but it's a real threat. [pause] In this video, we'll explore PKCE—Proof Key for Public Clients—and how InfraFabric uses it to protect your authentication tokens. By the end, you'll understand every step of the flow and why it matters."

**Visual:**
- Attack diagram animation (authorization code being intercepted)
- PKCE shield animation (protection)

**[0:45-2:30] The Problem: Authorization Code Interception (105 seconds)**

**Narration:**
"Let's start with the problem. [pause] In traditional OAuth 2.0, your CLI application receives an authorization code. An attacker on your network could intercept that code and use it to get your access token. [pause] Even worse, they could use it before you do. This is the authorization code interception attack.

With PKCE, we solve this by adding a cryptographic proof. [pause] You create a random string called the 'code verifier,' hash it to create a 'code challenge,' and send that challenge when requesting the authorization code. [pause] Later, you prove you have the verifier by sending it back. Only the legitimate client has the verifier, so the attacker can't complete the attack."

**Visual Elements:**
- Diagram 1: Traditional OAuth (attacker intercepts code)
  - 1. Client requests code → 2. Attacker intercepts code → 3. Attacker exchanges code for token
  - Impact: Attacker has token, can impersonate user
- Diagram 2: OAuth with PKCE (attacker blocked)
  - 1. Client creates verifier and challenge
  - 2. Client requests code with challenge
  - 3. Attacker intercepts code (useless without verifier)
  - 4. Client proves possession of verifier
  - 5. Only legitimate client gets token

**Timing:**
- 0:45 - Problem introduction
- 1:15 - Attack scenario begins
- 1:45 - PKCE solution intro
- 2:15 - Verifier/challenge concept
- 2:30 - Diagram comparison complete

**[2:30-4:45] PKCE Step-by-Step (135 seconds)**

**Narration:**
"Let's walk through every step of the PKCE flow. [pause]

**Step 1: Generate Code Verifier**
The client generates a cryptographically random string, 43-128 characters long. This stays secret on your machine.

**Step 2: Create Code Challenge**
Take that verifier and hash it using SHA-256. This creates the code challenge. You send the challenge to the authorization server—not the verifier.

**Step 3: Request Authorization Code**
Your browser opens, and you send the code challenge as part of the OAuth request. The authorization server stores this challenge.

**Step 4: User Authorizes**
You see the login page, authenticate, and click 'Authorize.'

**Step 5: Get Authorization Code**
The server returns an authorization code. If an attacker intercepts this, they can't use it without the verifier.

**Step 6: Exchange Code for Token**
Here's the critical step: you send the authorization code AND the code verifier back to the server. The server hashes the verifier and compares it to the challenge it stored. They match? [pause] You get the token. They don't match? The attacker is rejected."

**Visual Flow Diagram:**
```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT (Your CLI)                    │
│  1. Generate Verifier: a1b2c3d4e5f6...z9y8 (random)         │
│  2. Create Challenge: SHA256(Verifier) = x9y8z7w6...        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    AUTHORIZATION SERVER                      │
│  3. Receives Challenge: x9y8z7w6... (stored)                │
│  4. User Authenticates & Authorizes                         │
│  5. Returns: auth_code = abc123xyz                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT (Terminal)                         │
│  6. Exchange:                                               │
│     - Send: code=abc123xyz, verifier=a1b2c3d4e5f6...z9y8   │
│     - Server verifies: SHA256(verifier) == stored challenge │
│  7. Receive: access_token = token123456                    │
└─────────────────────────────────────────────────────────────┘
```

**Code Examples:**

```python
# Step 1-2: Generate verifier and challenge (Python)
import secrets
import hashlib
import base64

# Generate random verifier
code_verifier = base64.urlsafe_b64encode(
    secrets.token_bytes(32)
).decode('utf-8').rstrip('=')
# Result: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t (43 chars)

# Create challenge
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).decode('utf-8').rstrip('=')
# Result: x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g
```

**Timing:**
- 2:30 - Step 1 introduction
- 2:50 - Step 2 explanation
- 3:10 - Step 3: Request code
- 3:30 - Step 4: User authorizes
- 3:50 - Step 5: Code returned
- 4:15 - Step 6: Exchange code (critical step)
- 4:45 - Diagram complete

**[4:45-6:15] InfraFabric Implementation (90 seconds)**

**Narration:**
"Now let's see how InfraFabric implements PKCE in the CLI. [pause]

When you run `infrafabric auth login`, here's what happens behind the scenes:

[Screen recording showing logs]

The CLI:
1. Generates a 32-byte random verifier
2. Creates the SHA-256 challenge
3. Starts a local HTTP server on port 8888 to receive the callback
4. Opens your browser with the authorization request, including the challenge
5. You authorize in the browser
6. The server receives the authorization code
7. The CLI exchanges the code for a token, proving it has the verifier
8. Your token is stored securely in ~/.infrafabric/credentials.json

The entire flow takes about 10 seconds. From the user's perspective, they just see a browser popup. [pause] But cryptographically, we've proven that only your CLI can use that authorization code."

**Screen Recording - CLI Logs:**
```
$ infrafabric auth login --provider google --verbose

[2025-11-30T10:15:30Z] Generating code verifier (32 bytes)...
[2025-11-30T10:15:30Z] Code Verifier: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t
[2025-11-30T10:15:31Z] Creating code challenge (SHA-256)...
[2025-11-30T10:15:31Z] Code Challenge: x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g
[2025-11-30T10:15:31Z] Starting callback server on http://localhost:8888
[2025-11-30T10:15:32Z] Opening browser for authorization...
[2025-11-30T10:15:33Z] Authorization URL:
https://accounts.google.com/o/oauth2/v2/auth?
  client_id=YOUR_CLIENT_ID
  redirect_uri=http://localhost:8888/callback
  response_type=code
  scope=openid+profile+email
  code_challenge=x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g
  code_challenge_method=S256

[User authorizes in browser]

[2025-11-30T10:15:45Z] Received authorization code: abc123xyz
[2025-11-30T10:15:45Z] Exchanging code for token...
[2025-11-30T10:15:46Z] POST /token
  code=abc123xyz
  code_verifier=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t
  client_id=YOUR_CLIENT_ID
[2025-11-30T10:15:48Z] ✓ Token received and verified
[2025-11-30T10:15:48Z] Storing credentials securely...
[2025-11-30T10:15:48Z] ✓ Authentication successful
User: user@example.com
Token Expires: 2025-11-30T11:15:48Z
```

**Timing:**
- 4:45 - CLI implementation intro
- 5:15 - Log output visible
- 5:45 - Authorization URL explained
- 6:00 - User authorization step
- 6:10 - Code exchange section
- 6:15 - Success complete

**[6:15-7:30] Headless Environment Solution (75 seconds)**

**Narration:**
"But what if you don't have a GUI? What if you're on a headless server or in a Docker container? [pause] InfraFabric provides an OAuth relay server that works anywhere.

Instead of opening a browser, you get a device code. You enter that code on any device with a browser, authorize there, and your headless environment receives the token. [pause] It's the same PKCE flow, just without needing a local browser."

**Screen Recording - Headless Flow:**
```bash
# SSH into headless server
$ ssh user@headless-server.example.com

# Try to authenticate (no GUI available)
$ infrafabric auth login --provider google

Device Code Authorization Flow:
┌─────────────────────────────────────┐
│ Device Code: GX-4829-KDLM          │
│                                     │
│ Go to: https://infrafabric.io/auth │
│ Enter code: GX-4829-KDLM           │
│                                     │
│ Waiting for authorization...       │
│ (expires in 15 minutes)             │
└─────────────────────────────────────┘

# [On local machine with browser]
$ curl https://infrafabric.io/auth
# Enter code: GX-4829-KDLM
# Click Authorize
# Browser shows: "Authorization successful. You can close this window."

# [Back on headless server]
[2025-11-30T10:20:15Z] ✓ Device authorized
[2025-11-30T10:20:16Z] Exchanging device code for token...
[2025-11-30T10:20:18Z] ✓ Token received
User: user@example.com
Token Expires: 2025-11-30T11:20:18Z

$ infrafabric auth status
Authenticated: YES
```

**Timing:**
- 6:15 - Headless problem stated
- 6:30 - Device code flow explained
- 6:45 - Device code displayed
- 7:10 - Authorization step (on another machine)
- 7:25 - Token received
- 7:30 - Verification complete

**[7:30-8:45] Security Guarantees (75 seconds)**

**Narration:**
"So what are the security guarantees PKCE provides? [pause]

**Guarantee 1: Authorization Code is Worthless Without Verifier**
Even if an attacker intercepts your authorization code, they can't exchange it for a token. The server will ask for the code verifier, which only your client has. [pause] Attack fails.

**Guarantee 2: Replay Attacks are Impossible**
Once a code is used, it's invalidated. If an attacker tries to replay it, the server rejects it. [pause] Defense intact.

**Guarantee 3: Man-in-the-Middle on Token Exchange**
PKCE doesn't prevent HTTPS downgrade attacks. Always use HTTPS for the token exchange. InfraFabric enforces this—you can't authenticate over HTTP.

**Guarantee 4: Verifier is Never Logged or Stored**
The server only stores the challenge (hash of verifier). Even if the server is compromised, the attacker doesn't have your verifier. They'd need to reverse the SHA-256 hash, which is computationally infeasible.

**Guarantee 5: Works with Public Clients**
PKCE is designed for public clients (CLIs, native apps, SPAs) that can't safely store secrets. InfraFabric has no client secret—just PKCE. Simpler, more secure."

**Visual Elements:**
- Security guarantee icons (5 total)
- Threat model diagram (attacker positions and defenses)
- Timeline showing attack attempts being blocked

**Threat Model Visualization:**
```
┌─────────────────┐
│   Attacker      │
│ (network snoop) │
└────────┬────────┘
         │ intercepts
         ↓
┌─────────────────────────┐
│ Authorization Code      │  ← USELESS without verifier
│ abc123xyz               │
└────────┬────────────────┘
         │ tries to exchange
         ↓
┌──────────────────────────────┐
│ Server checks:               │
│ code = abc123xyz ✓           │
│ verifier = ????? ✗           │
│                              │
│ Result: REJECTED             │
└──────────────────────────────┘
         │ attacker fails
         ↓
     [No token granted]
     [Attack prevented]
```

**Timing:**
- 7:30 - Guarantee intro
- 7:45 - Guarantee 1: Code worthless
- 8:00 - Guarantee 2: Replay attacks
- 8:15 - Guarantee 3: HTTPS enforcement
- 8:30 - Guarantee 4: Verifier never logged
- 8:45 - Guarantee 5: Public clients

**[8:45-9:45] Manual PKCE with curl (60 seconds)**

**Narration:**
"Now let's do it manually. I'll show you a PKCE flow using curl so you can see exactly how it works. [pause]

Step 1: Generate verifier and challenge"

**Screen Recording - Manual PKCE:**
```bash
#!/bin/bash
# PKCE flow with curl

# Step 1: Generate verifier
CODE_VERIFIER=$(python3 -c "
import secrets
import base64
verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
print(verifier)
")
echo "CODE_VERIFIER: $CODE_VERIFIER"
# Output: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t

# Step 2: Create challenge
CODE_CHALLENGE=$(echo -n "$CODE_VERIFIER" | sha256sum | xxd -r -p | base64 | tr '+/' '-_' | tr -d '=')
echo "CODE_CHALLENGE: $CODE_CHALLENGE"
# Output: x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g

# Step 3: Create authorization URL
AUTH_URL="https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8888/callback&response_type=code&scope=openid%20profile%20email&code_challenge=$CODE_CHALLENGE&code_challenge_method=S256"

echo "Open this URL in your browser:"
echo "$AUTH_URL"

# Step 4: Listen for callback (simulated)
# Authorization code received: abc123xyz

# Step 5: Exchange code for token
curl -X POST https://oauth2.googleapis.com/token \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "code=abc123xyz" \
  -d "code_verifier=$CODE_VERIFIER" \
  -d "grant_type=authorization_code" \
  -d "redirect_uri=http://localhost:8888/callback"

# Response:
# {
#   "access_token": "ya29.a0AfH6SMBx...",
#   "expires_in": 3599,
#   "token_type": "Bearer"
# }
```

**Narration continuation:**
"As you can see, PKCE is straightforward cryptography. [pause] Generate a random verifier, hash it, send the hash upfront, then prove possession of the verifier later. [pause] Elegant, and it closes a real security hole."

**Timing:**
- 8:45 - Narration intro
- 9:00 - Step 1: Generate verifier
- 9:15 - Step 2: Create challenge
- 9:30 - Step 3: Build auth URL
- 9:45 - Step 5: Exchange code

**[9:45-10:00] Summary & Next Steps (15 seconds)**

**Narration:**
"PKCE protects your authentication tokens by proving that only your client can use the authorization code. [pause] InfraFabric uses PKCE by default, which means your credentials are secure from day one. [pause] In the next video, we'll explore Ed25519 signing for message verification. See you then!"

**Visual:**
- Key takeaways (3-4 bullets)
- Next video teaser

---

### Video 3: Ed25519 Message Signing (12 minutes)

**Target Audience:** Security-conscious developers, multi-agent coordination teams
**Goal:** Understand asymmetric cryptography and how signing prevents spoofing
**Prerequisites:** Basic understanding of public/private key cryptography

**[0:00-1:00] Introduction**

**Narration:**
"Imagine you're running a swarm of 40 agents. [pause] They're all sending messages to a shared bus, claiming to be from different agents. [pause] How do you know which message is really from Agent 17 and not an imposter? [pause] The answer: digital signatures. Ed25519 is a modern cryptographic signing algorithm that proves message authenticity without storing any secrets on the server. In the next 12 minutes, you'll understand how it works and why it matters for multi-agent systems."

**Visual Elements:**
- Swarm of agents (40 dots moving)
- Messages flowing between agents
- Spoofed message appears (red warning)
- Ed25519 signature verification (green check)

**[1:00-3:30] Asymmetric Cryptography Overview (150 seconds)**

**Narration:**
"Let's start with the basics. Traditional cryptography uses one key to encrypt and decrypt. We call this symmetric cryptography. [pause] But for message signing, we need asymmetric cryptography, which uses two keys: a public key and a private key.

**The Public Key:** This is like your email address. You can share it with anyone. People use it to verify that messages came from you.

**The Private Key:** This is like your password. You never share it. You use it to sign messages.

Here's the magic: If a message is signed with your private key, anyone can verify it with your public key. [pause] But they can't forge your signature without having your private key.

**Ed25519 specifically:** It's an elliptic curve algorithm that's faster and more secure than older methods like RSA. [pause] It's what modern cryptography uses—Bitcoin, Tor, Signal, and now InfraFabric."

**Diagram 1: Symmetric vs. Asymmetric Cryptography**
```
SYMMETRIC (One Key):
┌─────────────────────┐
│   Shared Key: X     │
└─────────────────────┘
   ↙                    ↖
Alice                    Bob
Encrypt with X        Decrypt with X
   (Only if both       (Only if both
    have key!)         have key!)

ASYMMETRIC (Two Keys):
┌──────────────────────────────────┐
│  Alice's Key Pair                │
│  - Private Key: Secret           │
│  - Public Key: Published         │
└──────────────────────────────────┘
          │                    │
       Sign                Verify
        with               with
      Private            Public
       Key                 Key
          │                    │
          ↓                    ↓
    ┌──────────────┐    ┌──────────────┐
    │ Message +    │    │ Authentic?   │
    │ Signature    │    │ YES ✓        │
    └──────────────┘    └──────────────┘
         Bob receives      Bob verifies
```

**Diagram 2: Ed25519 Properties**
```
┌─────────────────────────────────────┐
│   Ed25519 Signing Algorithm         │
├─────────────────────────────────────┤
│ Input:                              │
│ - Message (any length)              │
│ - Private Key (32 bytes, secret)    │
│                                     │
│ Process:                            │
│ - Hash message (SHA-512)            │
│ - Sign with elliptic curve math     │
│ - Create signature (64 bytes)       │
│                                     │
│ Output:                             │
│ - Signature (64 bytes)              │
│                                     │
│ Verification:                       │
│ - Input: Message + Signature +      │
│          Public Key                 │
│ - Math check: Signature is valid    │
│ - Result: VALID ✓ or INVALID ✗     │
└─────────────────────────────────────┘
```

**Timing:**
- 1:00 - Asymmetric intro
- 1:30 - Public key explained
- 1:50 - Private key explained
- 2:15 - Signing magic explained
- 2:45 - Ed25519 introduction
- 3:30 - Diagrams complete

**[3:30-5:45] Key Generation and Storage (135 seconds)**

**Narration:**
"First, you need to generate a key pair. [pause] This happens once, and you keep the private key secret forever.

Let's generate a key pair with InfraFabric."

**Screen Recording - Key Generation:**
```bash
# Generate a new Ed25519 key pair
$ infrafabric auth keygen --algorithm ed25519

Generating Ed25519 key pair...
[████████████████████] 100%

Key Pair Generated:
Private Key (32 bytes):
  a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t (hex: a1b2c3...)
  [NEVER SHARE THIS KEY]

Public Key (32 bytes):
  x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g (hex: x9y8z7...)
  [OK to share freely]

Saving private key to: ~/.infrafabric/private_key.ed25519
Saving public key to: ~/.infrafabric/public_key.ed25519

Key ID (fingerprint): 5d8f9a2c4e1b3a7f
Created: 2025-11-30T10:30:00Z
Algorithm: Ed25519

✓ Key pair generated successfully
```

**Narration continuation:**
"The private key is saved in a secure location on your machine. [pause] On Linux and macOS, it's in ~/.infrafabric/ with 600 permissions—only you can read it. [pause] The public key can be shared with the world.

When you authenticate with InfraFabric, your public key is registered with the server. [pause] From that moment on, any message you sign can be verified as coming from you."

**Diagram 3: Key Storage**
```
Your Machine:
┌────────────────────────────────────┐
│ ~/.infrafabric/                    │
│ ├─ private_key.ed25519 (600)       │
│ │  [Only you can read]             │
│ │  Never transmitted               │
│ │  Never logged                    │
│ │                                  │
│ ├─ public_key.ed25519 (644)        │
│ │  [Can be shared]                 │
│ │  Registered on server            │
│ │                                  │
│ └─ credentials.json                │
│    [OAuth token + key metadata]    │
└────────────────────────────────────┘

Server (InfraFabric):
┌────────────────────────────────────┐
│ User Database                      │
│ ├─ user_id: user@example.com      │
│ ├─ public_key: x9y8z7w6...        │
│ ├─ key_id: 5d8f9a2c4e1b3a7f       │
│ └─ created: 2025-11-30T10:30:00Z  │
│                                    │
│ NO PRIVATE KEYS STORED             │
│ [Server can't forge signatures]    │
└────────────────────────────────────┘
```

**Narration:**
"This is crucial: The server never stores your private key. [pause] Even if the server is hacked, your private key is safe on your machine. [pause] No one can forge your signature."

**Timing:**
- 3:30 - Key generation intro
- 3:50 - Command shown
- 4:15 - Key output explained
- 4:40 - Storage location
- 5:00 - Public key registration
- 5:20 - Key storage diagram
- 5:45 - Security guarantee

**[5:45-7:45] Signing and Verification (120 seconds)**

**Narration:**
"Now let's sign a message and verify it. [pause]

When you send a message through InfraFabric, the client automatically signs it with your private key. The signature is sent along with the message. [pause] The server verifies the signature using your public key. If it's valid, the message is trusted. If it's not, the message is rejected."

**Screen Recording - Signing and Verification:**
```bash
# Sign a message (typically done automatically by the client)
$ MESSAGE="Send 1000 tokens to Agent 17"

$ infrafabric sign "$MESSAGE"

Signing message with Ed25519...

Original Message:
  "Send 1000 tokens to Agent 17"

Message Hash (SHA-512):
  a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0a1b2c3d4e5f6g7h8i9j0k

Signature (64 bytes):
  x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g5d8f9a2c4e1b3a7f9d8f9a2c
  4e1b3a7f9d8f9a2c4e1b3a7f9d8f9a2c4e1b3a7f

Key ID: 5d8f9a2c4e1b3a7f

✓ Signature created

# Now verify it
$ infrafabric verify \
    --message "$MESSAGE" \
    --signature "x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g..." \
    --public-key "x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g"

Verifying signature...
┌──────────────────────────────┐
│ Verification Result          │
│ ✓ VALID                      │
│                              │
│ Message: "Send 1000 tokens   │
│           to Agent 17"       │
│ Signer: Agent17              │
│ Created: 2025-11-30T10:35:00Z│
│ Key ID: 5d8f9a2c4e1b3a7f     │
└──────────────────────────────┘

# Try with altered message (will fail)
$ infrafabric verify \
    --message "Send 2000 tokens to Agent 17" \
    --signature "x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g..." \
    --public-key "x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g"

Verifying signature...
┌──────────────────────────────┐
│ Verification Result          │
│ ✗ INVALID                    │
│                              │
│ Error: Signature does not    │
│        match message         │
│                              │
│ Original Message:            │
│   "Send 1000 tokens..."      │
│ Claimed Message:             │
│   "Send 2000 tokens..."      │
│                              │
│ Attacker attempted to        │
│ modify signed message!       │
└──────────────────────────────┘
```

**Narration continuation:**
"Notice what happened. [pause] We signed the message, and the signature verified correctly. [pause] But when we tried to claim a different message had that signature, verification failed. [pause] This is the power of digital signatures: change even one character, and the signature becomes invalid."

**Diagram 4: Signing Process**
```
Message: "Send 1000 tokens to Agent 17"
   │
   ├─→ SHA-512 Hash
   │   Result: a1b2c3d4e5f6g7h8...
   │   │
   │   └─→ Ed25519 Sign (with Private Key)
   │       Result: x9y8z7w6v5u4t3s2r...
   │       │
   │       └─→ Signature: 64 bytes
   │           [Appended to message]
   │
   ↓
Message + Signature sent to server

Server receives:
   Message: "Send 1000 tokens to Agent 17"
   Signature: x9y8z7w6v5u4t3s2r...
   Public Key: x9y8z7w6v5u4t3s2r...
   │
   ├─→ SHA-512 Hash (same message)
   │   Result: a1b2c3d4e5f6g7h8...
   │   │
   │   └─→ Ed25519 Verify (with Public Key)
   │       Does signature match?
   │       YES ✓ → TRUST MESSAGE
   │       NO  ✗ → REJECT MESSAGE
```

**Timing:**
- 5:45 - Signing intro
- 6:00 - Sign command
- 6:25 - Signature output
- 6:50 - Verify command (valid)
- 7:10 - Verify command (invalid)
- 7:30 - Comparison explanation
- 7:45 - Diagram complete

**[7:45-9:30] Multi-Agent Spoofing Prevention (105 seconds)**

**Narration:**
"Here's where signatures matter most: in multi-agent swarms. [pause]

Imagine you have 40 agents running on a shared Redis bus. [pause] Agent 5 sends a message claiming to be Agent 17. [pause] The receiving agent should reject it. [pause] But how does it know?

**Without signatures:** Anyone can claim to be anyone. All messages look the same.

**With Ed25519 signatures:** Each agent has a unique public key. Every message is signed with the sender's private key. Recipients verify the signature with the sender's public key. [pause] Spoofing is impossible."

**Screen Recording - Multi-Agent Message Flow:**
```json
// Redis Message Bus (S2 Bus)

// Message 1: Agent 5 sends legitimate message
{
  "from": "agent_5",
  "to": "agent_12",
  "action": "execute_task",
  "payload": {
    "task_id": "task_abc123",
    "command": "process_data"
  },
  "signature": "x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g...",
  "timestamp": "2025-11-30T10:40:00Z",
  "key_id": "5d8f9a2c4e1b3a7f"
}

// Verification Process:
// Agent 12 receives message
// 1. Extract public_key for agent_5 from key registry
// 2. Verify signature using public_key
// 3. If valid: Process message ✓
// 4. If invalid: Log attack, reject message ✗

// Attack Attempt: Imposter claims to be Agent 5
{
  "from": "agent_5",
  "to": "agent_12",
  "action": "execute_task",
  "payload": {
    "task_id": "task_xyz789",
    "command": "delete_database"  // ← Malicious!
  },
  "signature": "forged_signature_1234567890abcdef...",
  "timestamp": "2025-11-30T10:41:00Z",
  "key_id": "attacker_key_id"
}

// Verification Process:
// Agent 12 receives message
// 1. Extract public_key for agent_5 from key registry
// 2. Verify signature using agent_5's public_key
// 3. Signature does not match! ✗
// 4. Log security alert: "Spoofing attempt from agent_5"
// 5. Reject message
// 6. Alert human operator

// Result: Attack prevented
```

**Narration:**
"Every agent in the swarm has a public key registered. [pause] When a message arrives, the recipient verifies the signature. [pause] Only the real agent has the private key to create a valid signature. [pause] An attacker claiming to be Agent 5 can't forge Agent 5's signature without the private key."

**Diagram 5: Swarm Security with Ed25519**
```
┌────────────────┐
│ Agent 5        │
│ Private Key: X │ ← Secret
│ Public Key: Y  │
└────────────────┘
     │ Signs message
     │ with X
     ↓
[Message + Signature]
     │
     ↓ (sent via Redis)
     │
┌────────────────┐
│ Agent 12       │
│ Verifies with  │
│ Agent 5's      │
│ Public Key: Y  │
└────────────────┘
     │ Signature valid?
     ├─ YES → Trust message ✓
     └─ NO → Reject message ✗

Attack Scenario:
┌────────────────┐
│ Attacker       │
│ No private key │
└────────────────┘
     │ Forges signature
     ↓
[Spoofed Message]
     │
     ↓ (sent via Redis)
     │
┌────────────────┐
│ Agent 12       │
│ Verifies with  │
│ Agent 5's      │
│ Public Key: Y  │
└────────────────┘
     │ Signature valid?
     └─ NO → Reject message ✗
         [Alert operator]
```

**Timing:**
- 7:45 - Multi-agent intro
- 8:00 - Problem stated (spoofing)
- 8:15 - Solution explained
- 8:30 - Message JSON (valid)
- 8:50 - Verification process
- 9:00 - Attack attempt (spoofed)
- 9:15 - Attack prevented
- 9:30 - Diagram complete

**[9:30-11:15] Integration with S2 Redis Bus (105 seconds)**

**Narration:**
"InfraFabric uses a system called the S2 Bus—Signed, Secure Redis Bus. [pause] This is how agents communicate in swarms. Every message on the S2 Bus is cryptographically signed and verified.

Let me show you how this works."

**Screen Recording - S2 Bus with Signatures:**
```python
# Python client sending signed message via S2 Bus

import infrafabric
from infrafabric.s2_bus import S2Message

# Initialize client (your private key is loaded automatically)
client = infrafabric.Client()

# Create message
message = S2Message(
    sender_id="agent_5",
    recipient_id="agent_12",
    action="execute_task",
    payload={
        "task_id": "task_abc123",
        "command": "process_data"
    }
)

# Sign and send (signature added automatically)
client.s2_bus.send(message)
# Behind the scenes:
#   1. Message is serialized to JSON
#   2. Signature is created with sender's private key
#   3. Message + signature sent to Redis
#   4. Timestamp and key ID added

# Server-side: Message arrives
message = client.s2_bus.receive()
# Behind the scenes:
#   1. Message + signature extracted from Redis
#   2. Sender's public key looked up
#   3. Signature verified
#   4. If invalid, message rejected
#   5. If valid, message passed to handler

# Handler receives verified message
if message.verify():
    print(f"Trusted message from {message.sender_id}")
    print(f"Action: {message.action}")
    process_payload(message.payload)
else:
    print("Signature verification failed!")
    log_security_alert(message)
```

**Narration continuation:**
"The client automatically signs every message with the sender's private key. [pause] The receiver automatically verifies with the sender's public key. [pause] This happens transparently—you don't need to manually sign messages. [pause] It's built into the S2 Bus protocol."

**Diagram 6: S2 Bus Architecture**
```
┌─────────────────────────────────────────────────────┐
│              InfraFabric Client Library              │
│  ┌──────────────────────────────────────────────┐   │
│  │  S2 Bus (Signed, Secure Redis Bus)           │   │
│  │  ┌────────────────────────────────────────┐  │   │
│  │  │ Send Side:                             │  │   │
│  │  │  1. Message object                     │  │   │
│  │  │  2. Serialize to JSON                  │  │   │
│  │  │  3. Sign with private key (Ed25519)    │  │   │
│  │  │  4. Add timestamp + key ID             │  │   │
│  │  │  5. Publish to Redis channel           │  │   │
│  │  │  6. Return result                      │  │   │
│  │  └────────────────────────────────────────┘  │   │
│  │               ↓                               │   │
│  │  ┌─────────────────────────────────────────┐ │   │
│  │  │  Redis (S2 Bus Channel)                 │ │   │
│  │  │  [signed_message_1234567890...]        │ │   │
│  │  │  [signed_message_0987654321...]        │ │   │
│  │  │  [signed_message_abcdef...]            │ │   │
│  │  └─────────────────────────────────────────┘ │   │
│  │               ↓                               │   │
│  │  ┌────────────────────────────────────────┐  │   │
│  │  │ Receive Side:                          │  │   │
│  │  │  1. Subscribe to Redis channel         │  │   │
│  │  │  2. Extract message + signature        │  │   │
│  │  │  3. Look up sender's public key        │  │   │
│  │  │  4. Verify signature (Ed25519)         │  │   │
│  │  │  5. Check timestamp (replay attack?)   │  │   │
│  │  │  6. If valid: pass to handler ✓        │  │   │
│  │  │  7. If invalid: reject + alert ✗       │  │   │
│  │  └────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

**Timing:**
- 9:30 - S2 Bus intro
- 9:50 - Python code (send)
- 10:10 - Behind-the-scenes signing
- 10:30 - Receive code
- 10:50 - Signature verification
- 11:10 - Diagram complete
- 11:15 - Architecture shown

**[11:15-12:00] Summary & Applications (45 seconds)**

**Narration:**
"Ed25519 signatures provide three crucial guarantees for InfraFabric:

**1. Authentication:** You know messages come from who they claim to be. No spoofing.

**2. Integrity:** You know messages haven't been altered. Change one bit, and the signature fails.

**3. Non-repudiation:** The sender can't deny sending a message. Their private key was the only way to create that signature.

These properties make Ed25519 essential for:
- Multi-agent swarms (prevent spoofing)
- Audit trails (prove who did what)
- Compliance (cryptographic proof of actions)
- Decentralized systems (no trusted authority needed)

InfraFabric uses Ed25519 by default on the S2 Bus. You get security without any extra work. [pause] In the next video, we'll see Ed25519 in action with multi-agent swarms. Thanks for watching!"

**Visual:**
- Three guarantees (icons)
- Use case list
- Next video teaser

---

### Video 4: Multi-Agent Swarm Coordination (15 minutes)

[Outline follows similar structure to Videos 2 and 3, with screen recordings showing:
- 40-agent swarm deployment
- Task posting and claiming
- Cross-swarm messaging
- Performance metrics]

### Video 5: Security Sandbox Deep Dive (18 minutes)

[Outline covers:
- 6-layer IF.emotion sandbox
- 50+ attack pattern detection
- Crisis detection filters
- Rate limiting strategies
- Audit trail logging
- Live attack prevention demo]

### Video 6: Production Deployment (20 minutes)

[Outline covers:
- Infrastructure requirements (CPU, RAM, storage)
- Docker Compose setup
- TLS/SSL with Let's Encrypt
- Secrets management (Vault integration)
- Monitoring (Prometheus + Grafana)
- Backup and recovery procedures
- Multi-region deployment]

---

## 3. Screen Recording Guidelines

### Technical Requirements
- **Resolution:** 1920x1080 (Full HD)
- **Frame Rate:** 30 fps (standard for technical content)
- **Codec:** H.264 or VP9
- **Bit Rate:** 8-12 Mbps for clarity
- **Audio:** 44.1 kHz, stereo, -18 dBFS

### Terminal Appearance
- **Font:** Monospace (Monaco, Consolas, or Source Code Pro)
- **Font Size:** 18pt minimum (legible in 1080p)
- **Colors:** High contrast (dark background, light text)
- **Theme:** Use InfraFabric theme (custom colors for clarity)
- **Lines per screen:** ~30-35 lines visible

### Recording Best Practices
1. **Preparation:** Zoom to 125-150% for readable text
2. **Typing Speed:** Moderate pace (60-80 WPM) or use pre-typed commands
3. **Pauses:** 2-3 second pause after each command before output
4. **Cursor:** Enable cursor highlighting (2px glow)
5. **Mouse:** Minimize mouse movements; click quietly
6. **Output:** Wait for full output before continuing

### Browser Recording
- **Profile:** Fresh Chrome/Firefox profile, no extensions
- **Cache:** Clear between recordings
- **Viewport:** 1920x1080, no tabs visible
- **Zoom:** 100% (not user zoom)
- **DevTools:** Closed

### Cursor and Highlighting
- **Cursor glow:** 2px, yellow/white highlight
- **Code highlight:** Use subtle background color
- **Important text:** Bold or highlight in editor
- **Links:** Show URL in status bar or overlay

---

## 4. Narration Scripts

### Audio Specifications
- **Voice:** Clear, professional (consider voice actor for production)
- **Pace:** 140-160 WPM (conversational)
- **Tone:** Friendly, educational, confident
- **Emphasis:** Stress key concepts with slight volume increase
- **Pauses:** 1-2 second pauses before major points

### Script Format Template

```markdown
### [MM:SS-MM:SS] Section Title (Duration)

**Narration:**
"[Full script word-for-word]

[pause 1s]

[Next sentence with emphasis on KEY CONCEPT]

[pause 2s for effect]

[Explain concept]"

**Timing Markers:**
- MM:SS - Event 1
- MM:SS - Event 2

**Visual Cues:**
- Show [element]
- Highlight [text]
- Wait [time]
```

### Emphasis Guidelines
- **SHOUTED:** Use for important warnings (capital letters)
- **Stress:** Use [stress] marker for vocal emphasis
- **Technical terms:** Pause before and after (1 second)
- **Punchlines:** Let humor land with 2-second pause

---

## 5. Visual Assets Production

### Asset Inventory

**Logos & Branding**
- [ ] InfraFabric logo (main, animated, white/dark variants)
- [ ] Logo animation (3-second loop)
- [ ] Color palette (primary, secondary, accent)
- [ ] Typography guidelines

**Diagrams (SVG Format)**
1. Architecture overview
2. OAuth PKCE flow (step-by-step)
3. Ed25519 key pair generation
4. Multi-agent swarm topology
5. S2 Bus message flow
6. Security sandbox layers
7. Deployment architecture

**Flow Diagrams**
- [ ] User authentication flow
- [ ] Message signing and verification
- [ ] Swarm communication protocol
- [ ] Attack detection pipeline

**Screenshots**
- [ ] Terminal output examples (8+ screenshots)
- [ ] Browser OAuth flow (4+ screenshots)
- [ ] Dashboard/monitoring UI (5+ screenshots)
- [ ] Error states (3+ screenshots)

**Animations**
- [ ] Logo animation (0-3 seconds)
- [ ] Data flowing through system
- [ ] Agent communication indicators
- [ ] Success/failure state transitions

### Design System
- **Grid:** 8px baseline
- **Colors:** Primary: #00A0D2, Secondary: #FFD700, Accent: #E74C3C
- **Typography:** Headers: Bold, 24-28pt; Body: Regular, 14-16pt
- **Spacing:** Consistent 16px/24px/32px padding/margins

---

## 6. Post-Production Checklist

### Video Editing
- [ ] Raw footage compiled
- [ ] Audio track normalized (-18 dBFS)
- [ ] Narration recorded and synced
- [ ] Background music added (royalty-free)
- [ ] Sound effects added (keyboard clicks, notifications)
- [ ] Color grading applied (consistent brightness)
- [ ] Zoom/crop applied (readable on small screens)

### Accessibility & Captions
- [ ] Full captions (SRT format) generated
- [ ] Caption timing verified
- [ ] Technical terms spelled correctly
- [ ] Captions match narration word-for-word
- [ ] Audio descriptions added (optional for accessibility)

### Metadata & SEO
- [ ] Title: Concise, keyword-rich (60 char max)
- [ ] Description: 1-2 paragraphs with links
- [ ] Tags: 8-12 relevant tags (max 500 chars)
- [ ] Thumbnail: Custom, high-contrast, readable text
- [ ] Playlist: Assigned to correct series

### YouTube Upload
- [ ] Video file uploaded
- [ ] Metadata complete
- [ ] Captions uploaded (SRT)
- [ ] Chapters added (every 2-3 minutes)
- [ ] Cards/end screens added (cross-promotion)
- [ ] Visibility: Public or Unlisted (not private)

### Distribution
- [ ] Social media posts (Twitter, LinkedIn, Discord)
- [ ] Community post (YouTube Community tab)
- [ ] Blog post with transcript
- [ ] Email newsletter announcement
- [ ] Documentation linked

---

## 7. Series Overview & Progression

| Video | Duration | Audience | Prereq | Status |
|-------|----------|----------|--------|--------|
| Quickstart | 5 min | New users | None | Outlined |
| OAuth PKCE | 10 min | Developers | Quickstart | Outlined |
| Ed25519 | 12 min | Security-focused | OAuth PKCE | Outlined |
| Swarm Coord | 15 min | Advanced | Ed25519 | Template |
| Security Sandbox | 18 min | Enterprise | Swarm Coord | Template |
| Production Deploy | 20 min | DevOps | All prior | Template |

**Total Production Time:** ~80 minutes content
**Estimated Post-Production:** ~40-60 hours (scripting, recording, editing, captions)

---

## 8. IF.TTT Compliance

**Citation:** `if://doc/video-scripts/2025-11-30`
**Source Files:**
- Generated from InfraFabric specification (if://doc/specs/platform)
- Security guidelines from IF.emotion sandbox (if://doc/security)
- Deployment architecture from agents.md

**Verification:**
- [ ] All scripts reviewed for technical accuracy
- [ ] Code examples tested (verified functional)
- [ ] Security claims validated against specs
- [ ] Diagrams reviewed by architecture team

**Status:** Production-ready, awaiting review and recording schedule

---

**Document ID:** if://doc/video-scripts/2025-11-30
**Last Updated:** 2025-11-30
**Version:** 1.0
**Author:** Haiku Agent B44
**Review Status:** Awaiting content team approval
