# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | :white_check_mark: |
| 1.x     | :x:                |

## Reporting a Vulnerability

We take security seriously in InfraFabric. If you discover a security vulnerability, please follow these steps:

### 1. Do Not Create a Public Issue

Security vulnerabilities should **not** be reported via GitHub issues, discussions, or pull requests.

### 2. Contact Us Privately

Send an email to: **security@infrafabric.dev** (or dannystocker@proton.me)

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Any suggested fixes (optional)

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution Target**: Within 30 days for critical issues

### 4. What to Expect

1. Acknowledgment of your report
2. Assessment of severity and impact
3. Development of a fix
4. Coordinated disclosure (if applicable)
5. Credit in the security advisory (if desired)

## Security Measures

### IF.yologuard Integration

InfraFabric includes IF.yologuard (680 lines), our security immune system:

- Input validation and sanitization
- Rate limiting and abuse prevention
- Credential rotation support
- Audit logging for security events

### Credential Handling

- No hardcoded secrets in source code
- Environment variable configuration
- Support for secret managers (HashiCorp Vault, AWS Secrets Manager)
- Automatic credential rotation via IF.yologuard

### Redis State Security

- TLS connections required for production
- Authentication enforced
- Key prefix isolation per tenant
- Corruption detection and recovery

### API Security

- Authentication required for all endpoints
- CORS configured restrictively
- Rate limiting enabled
- Input validation via Pydantic schemas

## Known Security Considerations

### Ghost Protocols

Some protocols (IF.synthesis, IF.veil) are documented but not fully implemented. These are marked as CONCEPT in the protocol registry and should not be relied upon for security functions.

### Council Deliberation

Security-related changes require Guardian Council review with the Security Auditor guardian having elevated weight in decisions.

## Dependency Security

We use:
- `uv` for dependency management with lockfile verification
- Regular dependency audits via `pip-audit`
- Automated updates via Dependabot (when enabled)

## Security-Related Files

| File | Purpose |
|------|---------|
| `src/infrafabric/core/security/yologuard.py` | Security immune system |
| `src/infrafabric/core/governance/arbitrate.py` | Access control arbitration |
| `.env.example` | Template for secure configuration |

## Acknowledgments

We thank the following for responsible disclosure:
- (No disclosures yet - be the first!)

---

*"Security through transparency, not obscurity."* - IF.TTT Principle
