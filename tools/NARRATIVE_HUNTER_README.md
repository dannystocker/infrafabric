# Operation Narrative Dragnet - User Guide

## Overview

`narrative_hunter.py` is a production-ready, multi-threaded narrative extraction system designed to recover lost InfraFabric stories, episodes, and chronicles from various sources across your filesystem and Redis databases.

### Swarm Architecture

The tool deploys **HaikuWorker threads** that process files in parallel, implementing intelligent extraction, deduplication, and classification of narrative content.

---

## Quick Start

###Basic Usage

```bash
cd /home/setup/infrafabric

# Standard scan with 8 workers
python3 tools/narrative_hunter.py --workers 8

# Quick scan (skip archives)
python3 tools/narrative_hunter.py --quick-scan

# Disable Redis scanning
python3 tools/narrative_hunter.py --no-redis

# Custom output directory
python3 tools/narrative_hunter.py --output-dir /tmp/recovered
```

---

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--workers N` | 8 | Number of parallel worker threads |
| `--output-dir PATH` | `docs/narratives/staging` | Output directory for recovered narratives |
| `--redis-scan` | enabled | Scan Redis databases for narratives |
| `--no-redis` | - | Disable Redis scanning |
| `--quick-scan` | - | Skip archive processing (faster) |
| `--report-only` | - | Generate report from existing staging files |

---

## What It Hunts

### Target Keywords

The system searches for content containing:

- **Episodes**: `Episode 1`, `Ep. 17`, `EP09`
- **Narratives**: `Narration`, `Chronicle`, `Medium Article`
- **InfraFabric Terms**: `The Council`, `Guardian`, `Instance #42`
- **Components**: `IF.witness`, `IF.guard`, `IF.ceo`
- **Story Markers**: `Chapter 1`, `Once upon a time`

### File Types Scanned

- **Text Files**: `.md`, `.txt`, `.log`
- **Structured Data**: `.json`, `.yaml`, `.yml`
- **Archives**: `.zip`, `.tar.gz`, `.tgz` (peek inside without extracting)

### Search Locations

1. `/mnt/c/Users/Setup/Downloads/` (Windows downloads folder)
2. `/home/setup/` (Linux workspace)
3. Redis DB0 and DB1 (session contexts)

---

## Swarm Components

### 1. HaikuWorker (Thread Class)

Parallel file processors that:
- Extract narratives from text/JSON/archives
- Calculate confidence scores
- Handle encoding errors gracefully
- Respect file size limits (50MB max)

### 2. DeduplicationEngine

Smart duplicate detection:
- SHA256 content hashing
- Fuzzy similarity matching
- Source priority (`.md` > `.txt` > `.json` > `.log`)
- Automatic best-version selection

### 3. NarrativeExtractor

Intelligent content extraction:
- Keyword density analysis
- Fragment classification (episode, medium, chronicle, log)
- JSON recursive parsing
- Confidence scoring

### 4. RedisArchaeologist

Redis database scanner:
- Scans DB0 and DB1
- Extracts narrative-containing keys
- Preserves source metadata
- Graceful fallback if Redis unavailable

---

## Output Structure

All recovered narratives are written to:

```
docs/narratives/staging/
├── recovered_episode_a3f2b1c8_20251127_023000.md
├── recovered_medium_d9e4f5a2_20251127_023015.md
├── recovered_chronicle_1c2d3e4f_20251127_023030.md
└── NARRATIVE_RECOVERY_REPORT.md
```

### Narrative File Format

Each recovered file includes:

```markdown
# Recovered Narrative: Episode

**Source:** `/path/to/original/file.txt`
**Discovered:** 2025-11-27T02:30:00Z
**Keywords Matched:** Episode, Guardian, Council
**Confidence:** 0.87
**Content Hash:** a3f2b1c8
**Size:** 12,450 bytes

---

[Original narrative content here]
```

---

## Recovery Report

After each run, a comprehensive report is generated:

### NARRATIVE_RECOVERY_REPORT.md Contents

1. **Executive Summary**
   - Files scanned
   - Archives processed
   - Redis keys checked
   - Narratives found
   - Duplicates removed

2. **Recovered Narratives by Type**
   - Episodes (with numbers)
   - Medium articles
   - Chronicles
   - Session logs
   - Unknown fragments

3. **Next Steps**
   - Validation checklist
   - Merge recommendations

---

## Examples

### Example 1: Full System Scan

```bash
python3 tools/narrative_hunter.py --workers 16 --redis-scan
```

**Output:**
```
============================================================
OPERATION NARRATIVE DRAGNET - Commencing
============================================================
Phase 1: Filesystem discovery
Scanning: /mnt/c/Users/Setup/Downloads
Scanning: /home/setup
Discovered 3,456 files to scan

Phase 2: Launching 16 HaikuWorker threads
Worker 0 started
Worker 1 started
...

Phase 3: Redis archaeological scan
Connected to Redis, scanning databases...
Scanned 1,247 keys in Redis DB0
Scanned 892 keys in Redis DB1

Phase 4: Processing files...
Found narrative: episode_01_draft.md (type: episode)
Found in archive: old_backups.zip/chronicles.txt
Extracted from JSON: chat_export.json (medium)
...

Phase 5: Processing results and deduplicating
Duplicate removed: episode_01_copy.txt (Exact content hash match)
...

Phase 6: Writing recovered narratives
Written: recovered_episode_a3f2b1c8_20251127_023000.md
...

Phase 7: Generating recovery report
Report written: docs/narratives/staging/NARRATIVE_RECOVERY_REPORT.md

============================================================
OPERATION COMPLETE
Narratives recovered: 47
Duplicates removed: 23
Total bytes recovered: 2,341,056
Duration: 127.3s
============================================================
```

### Example 2: Quick Scan (Development)

```bash
python3 tools/narrative_hunter.py --quick-scan --workers 4
```

Skips archive processing for faster iteration during development.

### Example 3: Redis-Only Scan

```bash
python3 tools/narrative_hunter.py --no-redis
```

Disable filesystem scan, only check Redis databases.

---

## Performance Tuning

### Worker Count

- **Low CPU systems**: `--workers 2`
- **Standard systems**: `--workers 8` (default)
- **High-performance**: `--workers 16`

### Memory Usage

Each worker consumes ~50-100MB. Monitor with:

```bash
while true; do ps aux | grep narrative_hunter; sleep 2; done
```

### File Size Limits

Default max file size: **50MB**

Edit in code if needed:
```python
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
```

---

## Troubleshooting

### Issue: "Redis scanning skipped"

**Cause:** `redis-py` not installed

**Solution:**
```bash
pip install redis
```

### Issue: "Permission denied" errors

**Cause:** Insufficient file permissions

**Solution:**
```bash
# Run with appropriate permissions
sudo python3 tools/narrative_hunter.py
```

### Issue: High memory usage

**Cause:** Too many workers or large files

**Solution:**
```bash
# Reduce worker count
python3 tools/narrative_hunter.py --workers 2

# Or skip archives
python3 tools/narrative_hunter.py --quick-scan
```

### Issue: No narratives found

**Possible causes:**
1. Wrong search directories
2. Files already processed
3. Keywords too restrictive

**Debug:**
```bash
# Check if files exist
ls -la /mnt/c/Users/Setup/Downloads/ | grep -i episode

# Check narrative patterns in code
grep "NARRATIVE_KEYWORDS" tools/narrative_hunter.py
```

---

## Advanced Usage

### Custom Keyword Patterns

Edit `NARRATIVE_KEYWORDS` in the script:

```python
NARRATIVE_KEYWORDS = [
    r'\bEpisode\s+\d+\b',
    r'\bYour Custom Pattern\b',
    # Add more patterns
]
```

### Integration with CI/CD

```bash
# Run in cron job (daily at 2 AM)
0 2 * * * cd /home/setup/infrafabric && python3 tools/narrative_hunter.py --quick-scan >> /var/log/narrative_hunter.log 2>&1
```

### Export to Different Formats

Modify `_write_narratives()` method to output JSON, YAML, or other formats.

---

## Architecture Deep Dive

### Thread Safety

- **file_queue**: Thread-safe Queue for work distribution
- **result_queue**: Thread-safe Queue for results collection
- **stats_lock**: Threading.Lock for statistics updates
- **dedup_engine**: Not thread-safe, accessed only by main thread

### Deduplication Logic

1. **Exact Match**: SHA256 hash comparison
2. **Fuzzy Match**: Character bigram Jaccard similarity (>90%)
3. **Source Priority**: Markdown > Text > JSON > Log
4. **Best Version Selection**: Replace lower-priority duplicates

### Confidence Scoring

```
confidence = min(1.0, keyword_matches / 10.0)

Examples:
- 2 keywords → 0.2 confidence
- 5 keywords → 0.5 confidence
- 10+ keywords → 1.0 confidence
```

Minimum confidence threshold for JSON extraction: **0.3**

---

## License & Credits

Part of InfraFabric S2 - Universal Logistics Engine

**Author:** Guardian Council
**Version:** 1.0.0
**Last Updated:** 2025-11-27

---

## Next Steps After Recovery

1. **Review Recovered Files**
   ```bash
   ls -lh docs/narratives/staging/
   ```

2. **Read Recovery Report**
   ```bash
   cat docs/narratives/staging/NARRATIVE_RECOVERY_REPORT.md
   ```

3. **Validate Episodes**
   - Check episode numbering
   - Verify chronological order
   - Confirm authorship

4. **Merge into Main Collection**
   ```bash
   mv docs/narratives/staging/recovered_episode_*.md docs/narratives/episodes/
   ```

5. **Archive Low-Confidence Fragments**
   ```bash
   mkdir docs/narratives/archive
   mv docs/narratives/staging/*unknown*.md docs/narratives/archive/
   ```

---

## Support

For issues, improvements, or questions:

- Check logs in `/var/log/narrative_hunter.log`
- Review recovery report for diagnostic info
- Consult Guardian Council documentation

**Happy Hunting! 🔍📚**
