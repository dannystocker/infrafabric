# Pull Request

## Description

Provide a clear and concise description of the changes in this PR.

Fixes #(issue)

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test coverage improvement

## Changes Made

- Change 1
- Change 2
- Change 3

## Testing

Describe the tests you ran to verify your changes:

- [ ] `just check` passes (ruff, mypy, pytest)
- [ ] `just audit-db` passes (state schema validation)
- [ ] Added new tests for new functionality
- [ ] Existing tests pass
- [ ] Manual testing performed

### Test Coverage

- **Unit Tests**: [Describe unit tests added/modified]
- **Integration Tests**: [Describe integration tests added/modified]
- **Test Coverage %**: [If applicable]

## IF.TTT Compliance

- [ ] **Traceability**: Changes are linked to observable sources (citations, commits)
- [ ] **Transparency**: Side effects are documented and logged
- [ ] **Trustworthiness**: State changes validated against schemas, types annotated

### Specific Compliance Items

- [ ] Citations added for external sources using `if://citation/` URIs
- [ ] State transitions validated against `src/infrafabric/state/schema.py`
- [ ] Security changes reviewed with YoloGuard integration
- [ ] Audit trail maintained for state mutations

## Guardian Council Review

Does this PR require Guardian Council review?

- [ ] No (minor changes, no architectural impact)
- [ ] Yes (check all that apply):
  - [ ] Architectural change (affects Core, State, or Security)
  - [ ] State schema modification (requires migration)
  - [ ] Security-critical change (YoloGuard, authentication, authorization)
  - [ ] Breaking API changes
  - [ ] New external dependencies

If yes, debate document created: `docs/debates/XXX_description.md`

## Documentation

- [ ] Code comments added/updated for complex logic
- [ ] Docstrings added/updated (Google style)
- [ ] Architecture docs updated (`docs/`)
- [ ] Changelog updated (`CHANGELOG.md`)
- [ ] README updated (if applicable)

## Performance Impact

Describe any performance implications:

- **Benchmarks**: [Results from `pytest-benchmark` if applicable]
- **Memory Usage**: [Expected impact]
- **API Latency**: [Expected impact]
- **Redis Operations**: [Expected impact]

## Breaking Changes

If this is a breaking change:

- [ ] Migration guide provided
- [ ] Deprecation warnings added
- [ ] Version bump planned (major version)
- [ ] Downstream impacts assessed

## Screenshots/Recordings

If applicable, add screenshots or recordings to demonstrate the changes.

## Checklist

- [ ] My code follows the project's coding standards
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Additional Notes

Add any additional notes for reviewers here.

## Rollback Plan

If this PR introduces risk, describe the rollback plan:

1. [Step 1 to rollback]
2. [Step 2 to rollback]

## Related PRs/Issues

- Related to #
- Depends on #
- Blocks #
