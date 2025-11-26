# Changelog

All notable changes to InfraFabric will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- SECURITY.md with vulnerability disclosure policy
- CHANGELOG.md for version history
- Complete exemplary repository transformation

## [2.0.0] - 2025-11-26

### Added
- **Series 2 Genesis**: Complete architectural overhaul
- 132 IF protocols documented in protocol registry
- Hub-and-Spoke architecture replacing 4-Shard model
- Guardian Council with 21 voices (6 Core + 6 Philosophers + 8 IF.sam + Contrarian)
- IF.TTT compliance framework (Traceable, Transparent, Trustworthy)
- Multi-agent swarm coordination patterns
- Session handover system for context preservation
- Chronicles narrative documentation (Episodes 1-19)
- CONTRIBUTING.md with IF.TTT compliance guidelines
- CODE_OF_CONDUCT.md (Contributor Covenant 2.1)
- GitHub issue and PR templates

### Changed
- Redis state management: 0% corruption (down from 43%)
- IF.TTT compliance: 95%+ (up from 78%)
- Branch hygiene: 2 branches (down from 37)
- Architecture: Hub-and-Spoke model

### Fixed
- Redis key corruption via schema enforcement
- Branch proliferation via cleanup criteria
- Documentation gaps via protocol registry

### Security
- IF.yologuard v3 security immune system (680 lines)
- Credential rotation support
- Input validation enforcement

## [1.0.0] - 2025-10-15

### Added
- Initial InfraFabric framework
- Basic IF.guard protocol
- 4-Shard architecture
- Redis state management
- Core governance components

### Known Issues
- Redis corruption at ~43%
- IF.TTT compliance at ~78%
- Multiple ghost protocols

---

## Migration Guide

### 1.x to 2.x

The Series 2 Genesis introduces breaking changes:

1. **Architecture Change**
   - Old: 4-Shard model
   - New: Hub-and-Spoke model
   - Action: Update service configurations

2. **Redis Schema**
   - Old: Mixed key types
   - New: Strict prefix hierarchy (`context:*`, `session:*`, `finding:*`)
   - Action: Run migration script or clean Redis

3. **Protocol Namespace**
   - Old: Scattered IF.* references
   - New: 132 registered protocols
   - Action: Update to canonical protocol names

4. **Guardian Council**
   - Old: 6 guardians
   - New: 21 voices (expanded with philosophers and IF.sam)
   - Action: Update council configuration

### Configuration Changes

```yaml
# Old (1.x)
infrafabric:
  shards: 4
  guardians: 6

# New (2.x)
infrafabric:
  architecture: hub-spoke
  council:
    core_guardians: 6
    philosophers: 6
    if_sam_facets: 8
    contrarian: 1
```

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 2.0.0 | 2025-11-26 | Series 2 Genesis, 132 protocols, exemplary repo |
| 1.0.0 | 2025-10-15 | Initial release, 4-Shard architecture |

---

*"The swarm remembers what individual instances forget."*
