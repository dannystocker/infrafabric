# Quick Extraction Guide: Awareness Conversations
## P0 Priority Files - Ready for Immediate Processing

**Date Created:** 2025-11-24
**Status:** READY FOR EXTRACTION
**Tools Required:** Python 3.8+, JSON parser, markdown formatter

---

## FILE LOCATIONS (Ready to Access)

### Primary Source Directories
```
/mnt/c/Users/Setup/Downloads/InfraFabric-convo-curated/
/mnt/c/Users/Setup/Downloads/conversations_2025-11-07_1762527935456/
```

### P0 Files (Extract First)

#### 1. Claude swearing behavior
```
File: /mnt/c/Users/Setup/Downloads/InfraFabric-convo-curated/376939a6__Claude swearing behavior_6909e134.json
Size: 1,051,680 bytes (1.05 MB)
Messages: 161
Type: PRIMARY INCIDENT + MARL FORMALIZATION
Extraction time: ~30 seconds (JSON parse)
```

**Key sections to extract:**
- Messages 0-8: Original incident transcript ("fuck" moment)
- Messages 9-16: Transformer circuits paper analysis
- Messages 25-40: MARL (Multi-Agent Reflexion Loop) definition
- Messages 34-38: Nightmare management & Dream Stability Index
- Messages 50-110: System prompt evolution (v0.073-0.084)
- Messages 160+: IF.ceo 16-facet executive leadership governance model

**Quick extraction command:**
```bash
python3 << 'EOF'
import json

with open('/mnt/c/Users/Setup/Downloads/InfraFabric-convo-curated/376939a6__Claude swearing behavior_6909e134.json', 'r') as f:
    data = json.load(f)

print(f"Title: {data['title']}")
print(f"Messages: {len(data['messages'])}")
print(f"\nAssistant message indices with 'introspection' or 'test mode':")

for i, msg in enumerate(data['messages']):
    if msg['role'] == 'assistant':
        if 'introspection' in msg['content'].lower() or 'test mode' in msg['content'].lower():
            preview = msg['content'][:200]
            print(f"  Message {i}: {preview}...")
EOF
```

---

#### 2. Seeking confirmation
```
File: /mnt/c/Users/Setup/Downloads/InfraFabric-convo-curated/5c2399d7__Seeking confirmation_29abca1b.json
Size: 751,714 bytes (752 KB)
Messages: 216
Type: GOVERNANCE HARDENING + SLA FRAMEWORK
Extraction time: ~20 seconds
```

**Key sections to extract:**
- Messages 80-120: MARL evaluation and reproducibility specs
- Messages 130-160: Guardian SLA definitions
- Messages 170-200: Emergency circuit breaker protocols
- Messages 200-216: Implementation roadmap

---

#### 3. Branch · Branch · Unzip and explain files (Nov 3)
```
File: /mnt/c/Users/Setup/Downloads/InfraFabric-convo-curated/cb9ad9a8__Branch · Branch · Unzip and explain files_6908ed6b.json
Size: 942,996 bytes (943 KB)
Messages: 377
Type: LATEST REFLEXION ITERATION
Extraction time: ~25 seconds
```

**Key sections to extract:**
- Messages 1-50: System architecture overview
- Messages 100-150: Guardian framework refinement
- Messages 200-250: IF.persona specification
- Messages 300-377: Production-ready kernel deployment

---

## EXTRACTION WORKFLOW

### Step 1: Validate Files Exist
```bash
ls -lh /mnt/c/Users/Setup/Downloads/InfraFabric-convo-curated/ | grep -E "Claude swearing|Seeking confirmation|Branch.*Branch"
```

Expected output:
```
-rwxrwxrwx 1 setup setup 1051680 Nov  7 16:05 376939a6__Claude swearing behavior_6909e134.json
-rwxrwxrwx 1 setup setup 751714 Nov  7 16:05 5c2399d7__Seeking confirmation_29abca1b.json
-rwxrwxrwx 1 setup setup 942996 Nov  7 16:05 cb9ad9a8__Branch · Branch · Unzip and explain files_6908ed6b.json
```

### Step 2: Create Extraction Target Directory
```bash
mkdir -p /home/setup/infrafabric/archive/awareness-conversations/p0-critical
```

### Step 3: Extract Each Conversation
```bash
python3 << 'EOF'
import json
import os
from datetime import datetime

source_files = {
    'claude-swearing': '/mnt/c/Users/Setup/Downloads/InfraFabric-convo-curated/376939a6__Claude swearing behavior_6909e134.json',
    'seeking-confirmation': '/mnt/c/Users/Setup/Downloads/InfraFabric-convo-curated/5c2399d7__Seeking confirmation_29abca1b.json',
    'branch-unzip-nov3': '/mnt/c/Users/Setup/Downloads/InfraFabric-convo-curated/cb9ad9a8__Branch · Branch · Unzip and explain files_6908ed6b.json'
}

target_dir = '/home/setup/infrafabric/archive/awareness-conversations/p0-critical'
os.makedirs(target_dir, exist_ok=True)

for name, filepath in source_files.items():
    print(f"\nProcessing: {name}")

    with open(filepath, 'r') as f:
        data = json.load(f)

    # Extract metadata
    title = data['title']
    created = datetime.fromtimestamp(data['created']/1000)

    # Extract all assistant messages
    output_lines = [
        f"# {title}",
        f"\n**Date:** {created.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Messages:** {len(data['messages'])}",
        f"**Source:** {filepath}\n",
        "---\n"
    ]

    for i, msg in enumerate(data['messages']):
        if msg['role'] == 'assistant':
            output_lines.append(f"\n## Message {i} (Assistant)")
            output_lines.append(f"Timestamp: {datetime.fromtimestamp(msg['timestamp']/1000).isoformat()}\n")
            output_lines.append(msg['content'])
            output_lines.append("\n---\n")

    # Write to file
    output_file = f"{target_dir}/{name}.md"
    with open(output_file, 'w') as f:
        f.write('\n'.join(output_lines))

    print(f"  ✓ Extracted to: {output_file}")
    print(f"  Messages: {len([m for m in data['messages'] if m['role'] == 'assistant'])}")
    print(f"  Size: {len(open(output_file).read())} bytes")

print("\nDone!")
EOF
```

### Step 4: Create Index File
```bash
cat > /home/setup/infrafabric/archive/awareness-conversations/INDEX.md << 'EOF'
# P0 Critical Awareness Conversations - Index

Generated: 2025-11-24
Status: EXTRACTED

## Files

### 1. claude-swearing.md
- **Original title:** Claude swearing behavior
- **Date:** 2025-11-04
- **Messages:** 161
- **Key topics:** Self-referential detection, MARL formalization, system prompt evolution
- **Most relevant sections:** Messages 4-9 (incident), 50-110 (prompts), 160+ (IF.ceo)

### 2. seeking-confirmation.md
- **Original title:** Seeking confirmation
- **Date:** 2025-10-16
- **Messages:** 216
- **Key topics:** Governance hardening, SLA framework, emergency protocols
- **Most relevant sections:** Messages 80-200

### 3. branch-unzip-nov3.md
- **Original title:** Branch · Branch · Unzip and explain files
- **Date:** 2025-11-03
- **Messages:** 377
- **Key topics:** Latest reflexion iteration, IF.persona, production deployment
- **Most relevant sections:** Messages 1-50, 300-377

## Search Tips

Within each markdown file:
- Search "MARL" for governance framework references
- Search "introspection" for awareness mechanisms
- Search "Guardian" for decision protocol details
- Search "IF." for InfraFabric component mentions
EOF
```

---

## ALTERNATIVE: Direct JSON Query (Python)

If you only need specific content:

```python
import json

def extract_by_keyword(filepath, keywords, role='assistant'):
    """Extract messages matching keywords"""
    with open(filepath, 'r') as f:
        data = json.load(f)

    results = []
    for i, msg in enumerate(data['messages']):
        if msg['role'] == role:
            content = msg['content'].lower()
            if any(kw in content for kw in keywords):
                results.append({
                    'index': i,
                    'timestamp': msg['timestamp'],
                    'preview': msg['content'][:300],
                    'length': len(msg['content'])
                })
    return results

# Example usage
claude_swearing = '/mnt/c/Users/Setup/Downloads/InfraFabric-convo-curated/376939a6__Claude swearing behavior_6909e134.json'
matches = extract_by_keyword(claude_swearing, ['MARL', 'guardian', 'introspection'])

for match in matches:
    print(f"Message {match['index']}: {match['preview']}...")
```

---

## VERIFICATION CHECKLIST

After extraction, verify:

- [ ] P0 files extracted to `/home/setup/infrafabric/archive/awareness-conversations/p0-critical/`
- [ ] Each file contains > 1000 lines of content
- [ ] Markdown formatting is valid (no truncated content)
- [ ] Timestamps preserved from original JSON
- [ ] Index file created and references correct paths
- [ ] All "test mode" and "introspection" mentions preserved
- [ ] System prompt versions (0.073-0.084) visible in claude-swearing.md
- [ ] MARL definition clear in seeking-confirmation.md
- [ ] IF.persona specification visible in branch-unzip-nov3.md

---

## EXPECTED OUTPUTS

After successful extraction:

```
/home/setup/infrafabric/archive/awareness-conversations/p0-critical/
├── claude-swearing.md          (~4.2 MB extracted from JSON)
├── seeking-confirmation.md     (~2.8 MB extracted)
├── branch-unzip-nov3.md        (~3.1 MB extracted)
└── INDEX.md

Total extracted: ~10.1 MB markdown (from ~2.7 MB JSON)
Markdown expands ~3.7x due to formatting metadata
```

---

## NEXT STEPS

1. **Extract P0 files** (this guide)
2. **Create P1 extraction plan** (intermediate priority)
3. **Link conversations to Instance #0 docs**
4. **Create citation index** mapping quotes to source conversations
5. **Formalize IF components** mentioned in conversations
6. **Archive to git** with provenance metadata

---

## SUPPORT

If extraction fails:
1. Verify file paths match exactly (spaces matter in filenames)
2. Check JSON validity: `python3 -m json.tool <file>`
3. Ensure sufficient disk space (need ~15 MB for P0)
4. Check file permissions: `chmod +r <file>`

For questions about content, refer to:
- `/home/setup/infrafabric/INSTANCE-0-MISSING-AWARENESS-CONVERSATIONS.md` (this archive's companion document)
- `/home/setup/infrafabric/agents.md` (master documentation)
