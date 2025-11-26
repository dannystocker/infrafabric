# r5_philosophers - Quick Start Guide

## What You Have

The complete r5_philosophers system for live data integration and philosophical framework validation in InfraFabric dossiers.

## Key Files Location

```
/home/setup/infrafabric/philosophy/r5/
```

## Quick Access

### 1. View Philosophy Browser
```bash
# Open in browser:
open docs/philosophy-browser.html
# Or: firefox docs/philosophy-browser.html
```

### 2. Test Live APIs
```bash
# Node 18+ required
npm install  # if needed
node tools/live_apis.ts test wikipedia "Sam Altman"
node tools/live_apis.ts test yahoo "GOOGL"
node tools/live_apis.ts test sec "1652044"  # Google CIK
```

### 3. Run Metric Validation
```bash
# Python 3.11+ required
python tools/recalc_metrics.py

# Exit 0 = all metrics valid
# Exit 1 = violations found
```

### 4. Enable GitHub Actions
```bash
# Copy workflow to your repo:
cp .github/workflows/ifctl-metrics.yml /path/to/repo/.github/workflows/

# Will now run on every push/PR
```

## API Endpoints Available

| API | Keyless | Use Case |
|-----|---------|----------|
| Wikipedia | Yes | Quick facts, context |
| SEC | Yes | Company fundamentals |
| Yahoo Finance | Yes* | Stock prices (reference only) |
| YouTube | No** | Interview sourcing |

*Unofficial endpoint
**Requires YT_API_KEY environment variable

## Configuration

Edit `config/live_sources.yaml` to:
- Add/remove API endpoints
- Change method/URL templates
- Set rate-limit notes

## Documentation

- **LIVE-SOURCES.md** - How to integrate live data
- **PHILOSOPHER-COVERAGE.md** - 26-entry canon metadata
- **PHILOSOPHY-CODE-EXAMPLES.v2.md** - Full code examples
- **ERRATA.md** - Known issues and workarounds

## Diagrams

- `diagrams/philosophy-map.mmd` - Philosopher taxonomy
- `diagrams/if-guard-council.mmd` - Guardian council structure
- `diagrams/if-search-8-pass.mmd` - Search workflow

## Next Steps

1. Populate `build/philosophy.json` with full 26-entry database
2. Test live APIs in your environment
3. Deploy GitHub Actions workflow
4. Host `philosophy-browser.html` in documentation site
5. Integrate metric validation into CI/CD

## Support

- Check EXTRACTION_SUMMARY.md for full details
- See docs/ for complete documentation
- Review code examples in PHILOSOPHY-CODE-EXAMPLES.v2.md

---
**Version:** r5_philosophers  
**Date:** 2025-11-15  
**Status:** Ready for deployment
