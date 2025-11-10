# Security Policy

## Intentional Test Secrets (Not Vulnerabilities)

This repository contains **intentional test secrets** in the following locations:

### `code/yologuard/benchmarks/leaky-repo/**`
- **Source:** Public benchmark corpus from [Plazmaz/leaky-repo](https://github.com/Plazmaz/leaky-repo)
- **Purpose:** Yologuard secret detection validation and testing
- **Status:** ✅ Safe - These are publicly known test secrets, not real credentials
- **GitHub Scanning:** Allowlisted in `.github/secret_scanning.yml`

### `code/yologuard/tests/fixtures/**`
- **Purpose:** Synthetic test secrets for unit tests
- **Status:** ✅ Safe - Not real credentials

**If you receive GitHub secret scanning alerts for these paths, they are false positives and can be safely dismissed.**

---

## Real Secret Protection

- ✅ `.env` files are gitignored (never commit real credentials)
- ✅ Production API keys stored locally only
- ✅ No live validation of secrets; no network exfiltration
- ✅ Always redact detected secrets in outputs

## Reporting Real Vulnerabilities

- Report vulnerabilities via GitHub Issues with `security` label (redact sensitive details)
- For responsible disclosure, email the maintainer listed in README

## Recent Security Incidents

**2025-11-10:** Google Cloud API key accidentally committed to git history
- **Resolution:** Key revoked, git history rewritten, `.env` added to `.gitignore`
- **Commits:** 876c45f (gitignore), c409c74 (secret scanning config)
- **Exposure:** ~1 hour on GitHub before removal
- **Impact:** Minimal (key revoked within 2 hours)
