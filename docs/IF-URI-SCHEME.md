# InfraFabric URI Scheme (`if://`) Specification

**Version:** 2.0
**Status:** Active (replaces `agent://` and other ad-hoc schemes)
**Last Updated:** 2025-11-10

**Purpose:** Unified addressing scheme for all InfraFabric resources (agents, topics, conversations, citations, DIDs)

---

## URI Scheme Overview

InfraFabric uses `if://` as the **single namespace** for all addressable resources. This provides:
- **Unified addressing** across all components
- **Transport independence** (DDS, ZeroMQ, HTTP - hidden behind `if://`)
- **Cryptographic verification** (DIDs resolve to public keys)
- **Immutable references** (content-addressed citations)

---

## URI Format

```
if://<resource-type>/<path>[#<fragment>][@<version>]
```

**Components:**
- `resource-type`: agent | topic | conversation | citation | did | claim | decision
- `path`: Resource-specific identifier (can be hierarchical with `/`)
- `fragment` (optional): Sub-resource or message ID
- `version` (optional): Semantic version (e.g., `@1.2.0`)

---

## Resource Types

### 1. Agents (`if://agent/...`)

**Format:** `if://agent/<domain>/<name>[@<version>]`

**Examples:**
```
if://agent/swarm/legal-1@1.2.0          # Specific version of legal agent
if://agent/swarm/financial/*            # Wildcard: all financial agents
if://agent/guard/technical-01           # Guardian Council member
if://agent/witness/validator            # IF.witness validation agent
```

**Resolution:**
- Maps to DID in registry: `if://did/agent/swarm/legal-1`
- DID resolves to public key for signature verification
- Version allows pinning to specific agent capabilities

---

### 2. Topics (`if://topic/...`)

**Format:** `if://topic/<domain>/<channel>`

**Examples:**
```
if://topic/mission/legal/findings       # Legal findings channel
if://topic/tracks/uav                   # UAV tracking data (C-UAS)
if://topic/effects/requests             # Effector requests (C-UAS)
if://topic/mission/coverage             # Domain coverage progress
if://topic/witness/citations            # Proof summaries
```

**Transport Binding:**
```yaml
# ifconnect/bindings.yaml
"if://topic/tracks/uav":
  transport: dds
  physical: "/tracks/uav"
  qos: { reliability: reliable, durability: transient_local, history: {keep_last: 10} }

"if://topic/mission/coverage":
  transport: dds
  physical: "/mission/coverage"
  qos: { reliability: best_effort, durability: volatile }
```

**Key Point:** Applications use `if://topic/...` URIs. `IF.connect` handles transport mapping.

---

### 3. Conversations (`if://conversation/...`)

**Format:** `if://conversation/<mission-id>`

**Examples:**
```
if://conversation/epic-2025-11-10-xyz
if://conversation/mission-2025-11-10-XYZ
```

**Purpose:**
- Groups related messages into coordination sessions
- Enables conversation replay for governance
- Provides context for IF.guard deliberations

---

### 4. Citations (`if://citation/...`)

**Format:** `if://citation/<uuid>`

**Examples:**
```
if://citation/9f2b3a1e-4d8a-4c7d-bf2c-e7a3d0a1b5f2
if://citation/swarm-comm-security-2025-11-10
```

**Properties:**
- **Content-addressed:** Citation stored as `citations/<sha256-of-citation>.json`
- **Immutable:** Hash changes if content modified
- **Signed:** Ed25519 signature proves issuer identity
- **Anchored:** Merkle root anchored to public ledger (OpenTimestamps/Bitcoin)

**Resolution:**
```bash
# Retrieve citation
ifcite get if://citation/9f2b3a1e-4d8a-4c7d-bf2c-e7a3d0a1b5f2

# Returns:
{
  "citation_id": "if://citation/9f2b3a1e-...",
  "claim_id": "if://claim/epic-antitrust-settlement",
  "sources": [...],
  "content_hash": "sha256:5a3d2f8c...",
  "issuer": "if://did/agent/swarm-legal-1",
  "sig": "ed25519:...",
  "merkle_proof": [...],
  "anchor_receipt": {"ots": "..."}
}
```

---

### 5. DIDs (`if://did/...`)

**Format:** `if://did/<resource-type>/<id>`

**Examples:**
```
if://did/agent/swarm-legal-1            # Agent identity
if://did/agent/guard-technical-01       # Guardian identity
if://did/council/if-guard               # Council collective identity
```

**DID Registry:**
```json
{
  "if://did/agent/swarm-legal-1": {
    "alg": "ed25519",
    "pubkey_hex": "AAAC3NzaC1lZDI1NTE5AAAAIOMq...",
    "created_at": "2025-11-08T00:00:00Z",
    "revoked": false
  },
  "if://did/agent/swarm-ew-1": {
    "alg": "ed25519",
    "pubkey_hex": "BBBD4OzaC2lZDI1NTE5AAAAJPNr...",
    "created_at": "2025-11-09T00:00:00Z",
    "revoked": false
  }
}
```

**Key Management:**
- Private keys stored in HSM/KMS (YubiHSM, Azure Key Vault, AWS KMS)
- Public keys in DID registry (content-addressed, anchored)
- Revocation list append-only, itself anchored

---

### 6. Claims (`if://claim/...`)

**Format:** `if://claim/<domain>/<id>` or `if://claim/<doc>/<section>`

**Examples:**
```
if://claim/epic-antitrust-settlement
if://claim/doc/IF-vision.md/§Abstract
if://claim/civilizational-collapse-patterns
```

**Purpose:**
- Unique identifier for testable assertions
- Links to supporting citations via `citation_ids`
- Enables structured evidence graphs

---

### 7. Decisions (`if://decision/...`)

**Format:** `if://decision/<decision-id>`

**Examples:**
```
if://decision/philosophy-expansion-2025-11-09
if://decision/v3.2.1-upgrade-approval
if://decision/publish-epic-brief
```

**Decision Schema:**
```json
{
  "decision_id": "if://decision/publish-epic-brief",
  "claim_id": "if://claim/epic-research-complete",
  "council_vote": {
    "total": 20,
    "approved": 19,
    "dissent": ["if://did/agent/guard-contrarian-01"]
  },
  "citation_ids": ["if://citation/9f2b3a1e", "if://citation/4d8a7c2d"],
  "rationale": "Coverage met (87%), ROE satisfied, evidence verified",
  "status": "approved",
  "created_at": "2025-11-10T14:30:00Z",
  "signatures": {
    "if://did/agent/guard-technical-01": "ed25519:...",
    "if://did/agent/guard-ethical-01": "ed25519:..."
  }
}
```

---

## Message Fragments

### Fragment Syntax: `if://<resource>#<fragment>`

**Examples:**
```
if://topic/tracks/uav#msg-000123                   # Specific message in topic
if://conversation/epic-xyz#seq-42                  # Message by sequence number
if://citation/9f2b3a1e#source-2                    # Specific source within citation
```

**Usage:**
- Precise references within resources
- Enables inline citations in documents
- Supports partial verification (verify one source without loading entire citation)

---

## Versioning

### Version Syntax: `if://<resource>@<version>`

**Semantic Versioning:**
```
if://agent/swarm/legal-1@1.2.0          # MAJOR.MINOR.PATCH
if://agent/swarm/legal-1@1.*            # Any MINOR/PATCH in v1
if://agent/swarm/legal-1@latest         # Latest version
```

**Purpose:**
- Pin to specific agent capabilities
- Reproducibility (mission can specify exact agent versions)
- Deprecation management (old versions can be retired)

---

## Wildcards

### Wildcard Patterns

**Supported:**
```
if://agent/swarm/*                      # All swarm agents
if://topic/mission/*/findings           # All mission domains' findings
if://did/agent/guard-*                  # All Guardian agents
```

**NOT Supported (Security Risk):**
```
if://*                                  # Too broad
if://topic/*/*/                         # Ambiguous depth
```

**Fanout Example:**
```yaml
# One message to multiple receivers
sender: "if://agent/coordinator"
receiver: ["if://agent/swarm/effector-*"]  # Fanout to all effectors
```

---

## URI Binding Table

### How `if://` URIs Map to Physical Transport

```yaml
# ifconnect/bindings.yaml
bindings:
  # Topics
  "if://topic/tracks/uav":
    transport: dds
    physical: "/tracks/uav"
    qos: { reliability: reliable, durability: transient_local, history: {keep_last: 10} }

  "if://topic/effects/requests":
    transport: dds
    physical: "/effects/requests"
    qos: { reliability: reliable, durability: transient_local }

  "if://topic/mission/coverage":
    transport: dds
    physical: "/mission/coverage"
    qos: { reliability: best_effort, durability: volatile }

  # Agents (discovery)
  "if://agent/*":
    transport: dds
    discovery: participant

  # Citations (CAS)
  "if://citation/*":
    storage: cas
    index: "citations/index.json"
    anchor_service: "opentimestamps"  # or "btc"

  # DIDs (registry)
  "if://did/*":
    storage: file
    path: "dids/agents.json"
    anchored: true
```

**Key Insight:** Agents never see DDS topics, CAS paths, or registry files. They use `if://` URIs exclusively. `IF.connect` handles all mappings.

---

## Verification Protocol

### How to Verify Any `if://` Resource

```bash
ifcite verify --uri <if://...>
```

**Verification Steps:**

1. **Parse URI** → Extract resource type, path, fragment
2. **Resolve Resource** → Load from CAS, DID registry, or topic log
3. **Verify Content Hash** → `sha256(bytes) == content_cid`
4. **Verify Signature** → `ed25519_verify(pubkey, canonical_msg, sig)`
5. **Check Revocation** → Issuer DID not in revocation list
6. **Verify Merkle Proof** → Leaf → Root → Anchored
7. **Check Anchor** → OpenTimestamps proof or Bitcoin tx exists
8. **Emit Verdict** → PASS/FAIL with reasons

**Example:**
```
$ ifcite verify --uri if://citation/9f2b3a1e-4d8a-4c7d-bf2c-e7a3d0a1b5f2

✓ Content hash matches CID (sha256:5a3d2f8c...)
✓ Signature valid (if://did/agent/swarm-legal-1)
✓ DID not revoked
✓ Merkle proof OK (block 42 → root sha256:8c5d4e3f...)
✓ Anchor OK (OTS proof verified; timestamp 2025-11-10T14:25:00Z)
= VERIFIED
```

---

## Blockchain-Style Anchoring

### OpenTimestamps (Recommended for MVP)

**Advantages:**
- Near-zero cost (free)
- Bitcoin-secured timestamp
- Simple integration
- Offline-verifiable proofs

**Process:**
1. Compute Merkle root of citation batch
2. Submit to OpenTimestamps API
3. Store OTS receipt in log index
4. Verifier validates receipt against Bitcoin blockchain

**Implementation:**
```python
import opentimestamps as ots

# Anchor
merkle_root = compute_merkle_root(citation_batch)
ots_receipt = ots.timestamp(merkle_root)
store_receipt(ots_receipt, batch_index)

# Verify
assert ots.verify(ots_receipt, merkle_root, bitcoin_rpc)
```

---

### Bitcoin OP_RETURN (Higher Assurance)

**Advantages:**
- Direct blockchain commitment
- No third-party service dependency
- Publicly auditable forever

**Costs:**
- ~$5-20 per anchor (depends on fee market)
- Batching reduces cost (one tx per day = $5/day)

**Process:**
```python
# Anchor (daily batch)
merkle_root = compute_merkle_root(daily_citations)
tx = bitcoin_tx_create(OP_RETURN=merkle_root)
txid = bitcoin_broadcast(tx)
store_anchor({
  "merkle_root": merkle_root,
  "btc_txid": txid,
  "timestamp": "2025-11-10T23:59:59Z"
})

# Verify
tx_data = bitcoin_get_tx(txid)
assert extract_op_return(tx_data) == merkle_root
assert tx_confirmed(txid)  # 6+ confirmations
```

---

## Privacy & Redaction

### Dual-Artifact Pattern

**Problem:** Some evidence contains PII/secrets but must be verifiable.

**Solution:** Store two versions:
- **Public:** Redacted document (safe for publication)
- **Private:** Original encrypted document (restricted access)

Both hashed; only original's hash committed to Merkle log.

```json
{
  "citation_id": "if://citation/sensitive-evidence",
  "cid_public": "sha256:abc123...",      // Redacted version
  "cid_private": "sha256:def456...",     // Original (encrypted)
  "committed_cid": "sha256:def456...",   // Log commits to original
  "encryption": {
    "algorithm": "AES-256-GCM",
    "key_id": "if://vault/annex-key-07",
    "access_policy": "IF.guard approval required"
  }
}
```

**Verification:**
- Public: Anyone can verify redacted version exists
- Private: Only authorized parties can decrypt and verify original
- Commitment: Hash of original proves it existed at anchor time (no backdating)

---

### Salted Hashing for Small Secrets

**Problem:** Small secrets (passwords, API keys) can be brute-forced from hash.

**Solution:** Add random salt before hashing.

```python
import secrets

salt = secrets.token_hex(32)  # 256-bit salt
secret = "my-api-key-12345"
cid = sha256(salt.encode() + secret.encode()).hexdigest()

# Store salt in vault, CID in public log
vault.store("if://vault/salt-12345", salt)
log.append({"cid": cid, "salt_ref": "if://vault/salt-12345"})
```

**Verification:**
- Requester must have vault access to retrieve salt
- With salt, can verify `sha256(salt + secret) == cid`
- Without salt, brute-forcing is infeasible

---

## Governance Integration

### IF.guard Decision Citations

**Pattern:** Every Guardian Council decision references citation graph.

```json
{
  "decision_id": "if://decision/publish-epic-brief",
  "claim_id": "if://claim/epic-research-complete",
  "council_vote": {
    "total": 20,
    "approved": 19,
    "dissent": ["if://did/agent/guard-contrarian-01"],
    "dissent_rationale_cid": "sha256:9c0d1e2f..."
  },
  "evidence_graph": {
    "primary_citations": [
      "if://citation/epic-sec-filing",
      "if://citation/epic-reuters-article"
    ],
    "contradicting_citations": [],  // None found
    "unverified_citations": []      // All verified
  },
  "verification_status": {
    "all_citations_verified": true,
    "all_merkle_proofs_ok": true,
    "all_anchors_ok": true,
    "roe_satisfied": true,
    "pii_scrubbed": true
  },
  "threshold_signatures": {
    "required": 3,  // k-of-n
    "received": 5,
    "signers": [
      "if://did/agent/guard-technical-01",
      "if://did/agent/guard-ethical-01",
      "if://did/agent/guard-civic-01",
      "if://did/agent/guard-cultural-01",
      "if://did/agent/guard-meta-01"
    ]
  },
  "status": "approved",
  "anchored": true,
  "anchor_receipt": {"ots": "..."}
}
```

**Key Point:** Decision itself is content-addressed, signed, and anchored. Creates tamper-evident governance trail.

---

## Migration from Legacy Schemes

### From `agent://` to `if://`

**Old:**
```yaml
sender: "agent://if.search.legal/1.2.0"
receiver: ["agent://if.swarm.financial/*"]
```

**New:**
```yaml
sender: "if://agent/swarm/legal-1@1.2.0"
receiver: ["if://agent/swarm/financial/*"]
```

**Migration Strategy:**
1. Update `IF.connect` to accept both schemes (temporary)
2. Convert all messages to `if://` on ingress
3. Phase out `agent://` support after 60 days
4. Update all documentation and examples

---

## Tools & Utilities

### `ifuri` - URI Parser & Validator

```bash
# Parse URI
$ ifuri parse if://citation/9f2b3a1e-4d8a-4c7d-bf2c-e7a3d0a1b5f2

Resource Type: citation
Path: 9f2b3a1e-4d8a-4c7d-bf2c-e7a3d0a1b5f2
Fragment: (none)
Version: (none)

# Validate URI
$ ifuri validate if://agent/swarm/legal-1@1.2.0

✓ Valid if:// URI
✓ Resource type 'agent' is recognized
✓ Version '1.2.0' follows semantic versioning
= OK
```

---

### `ifcite` - Citation Manager

```bash
# Add citation
$ ifcite add --claim if://claim/epic-settlement \
             --source https://sec.gov/... \
             --issuer if://did/agent/swarm-legal-1

Citation created: if://citation/9f2b3a1e-4d8a-4c7d-bf2c-e7a3d0a1b5f2

# Anchor batch
$ ifcite anchor --mode ots

Batch 42: 128 citations
Merkle root: sha256:8c5d4e3f...
OpenTimestamps receipt: /citations/anchors/batch-42.ots
= Anchored

# Verify
$ ifcite verify --uri if://citation/9f2b3a1e-4d8a-4c7d-bf2c-e7a3d0a1b5f2

✓ VERIFIED (see output above)
```

---

## Control Block in IF.brief

**Every published brief includes verification control block:**

```markdown
## Verification Control Block

**Claim:** Epic Games antitrust research complete
**URI:** if://claim/epic-research-complete
**Decision:** if://decision/publish-epic-brief

**Evidence Citations:**
- if://citation/epic-sec-filing (VERIFIED)
- if://citation/epic-reuters-article (VERIFIED)

**Merkle Proof:**
- Block: 42
- Root: sha256:8c5d4e3f2a1b0c9d...
- Proof: [sha256:1a2b3c4d..., sha256:5e6f7a8b..., sha256:9c0d1e2f...]

**Anchor:**
- Method: OpenTimestamps
- Receipt: /citations/anchors/batch-42.ots
- Bitcoin Block: 875432
- Timestamp: 2025-11-10T23:59:59Z

**Governance:**
- Council Vote: 19/20 approved
- Dissent: Guard-Contrarian-01 (rationale: if://citation/dissent-xyz)
- Threshold Signatures: 5/3 (Technical, Ethical, Civic, Cultural, Meta)

**IF.armour:**
- ROE: Satisfied (no violations)
- PII Scrub: Applied (3 redactions)
- Geofence: OK (no blue-force conflicts)

**Verdict:** VERIFIED - Brief publication authorized
```

---

## Summary

**`if://` URI Scheme Benefits:**
1. **Unified Namespace:** All resources use one addressing scheme
2. **Transport Independence:** Swap DDS/ZeroMQ/HTTP without changing agent code
3. **Cryptographic Verification:** DIDs → public keys, citations → Merkle proofs
4. **Immutable References:** Content-addressed citations can't be silently changed
5. **Governance Integration:** Decisions link to evidence via `if://` URIs
6. **Privacy-Preserving:** Dual artifacts, salted hashing, encrypted originals
7. **Blockchain-Secured:** OpenTimestamps or Bitcoin anchoring prevents backdating

**Next Steps:**
1. Review URI scheme with user (confirm `if://` is current standard)
2. Update all SWARM-COMMUNICATION-SECURITY.md examples to use `if://`
3. Create `ifuri` and `ifcite` CLI tools
4. Integrate with V3.2.1 bundle

---

**Citation for this document:**
```json
{
  "citation_id": "if://citation/uri-scheme-spec-2025-11-10",
  "claim_id": "if://claim/if-uri-scheme-standard",
  "sources": [
    {"type": "conversation", "ref": "gpt5chat-coms-ttt.txt", "hash": "sha256:PENDING"},
    {"type": "conversation", "ref": "Project evaluation and review_690fec28.json", "hash": "sha256:PENDING"}
  ],
  "rationale": "Unified URI scheme specification integrating GPT-5 blockchain architecture with existing IF.citation",
  "status": "unverified",
  "created_by": "if://did/agent/claude-sonnet-4.5",
  "created_at": "2025-11-10T00:00:00Z"
}
```

**Last Updated:** 2025-11-10
