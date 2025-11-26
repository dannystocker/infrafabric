# Contributing to InfraFabric

Thank you for considering contributing to InfraFabric! This document outlines the processes and standards for contributing to this autonomous infrastructure system.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, dependencies)
- **Relevant logs or error messages**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- Use a clear and descriptive title
- Provide a detailed description of the proposed functionality
- Explain why this enhancement would be useful
- Include examples of how it would work

### Pull Requests

1. **Fork the repository** and create your branch from `master`
2. **Follow the coding standards** (see below)
3. **Write or update tests** for your changes
4. **Ensure the test suite passes** (`just check`)
5. **Update documentation** as needed
6. **Submit a pull request** with a clear description

## Development Setup

InfraFabric uses `uv` for fast, hermetic dependency management:

```bash
# Clone the repository
git clone https://github.com/dannystocker/infrafabric.git
cd infrafabric

# Setup development environment
just setup

# Run the test suite
just check

# Audit the database schema
just audit-db
```

## Coding Standards

### Python Style

- **Formatter**: We use `ruff format` for consistent code formatting
- **Linter**: We use `ruff check` for linting
- **Type Checker**: We use `mypy` for static type checking
- **Line Length**: Maximum 100 characters
- **Imports**: Organized by standard library, third-party, and local imports

Run all checks before submitting:

```bash
just check  # Runs ruff, mypy, and pytest
```

### Code Organization

- **Functional Core**: Pure functions in `src/infrafabric/core/` (JAX-compatible)
- **State Layer**: Pydantic models in `src/infrafabric/state/`
- **Security**: YoloGuard implementations in `src/infrafabric/core/security/`
- **Tests**: Mirror source structure in `tests/`

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(librarian): Add semantic search caching layer

Implements Redis-backed caching for embedding queries to reduce
OpenAI API costs by ~$43k/year.

Closes #123
```

## IF.TTT Compliance (Traceable, Transparent, Trustworthy)

All contributions must adhere to the IF.TTT protocol:

### Traceability Requirements

1. **Citations**: Link claims to observable sources using the `if://citation/` URI scheme
2. **Decision Tracking**: Significant architectural decisions require Guardian Council review
3. **State Transitions**: All state changes must be validated against `src/infrafabric/state/schema.py`

### Transparency Requirements

1. **Observable Behavior**: All side effects must be tracked
2. **Audit Trails**: State mutations must be logged
3. **Documentation**: Complex logic requires inline comments explaining the "why"

### Trustworthiness Requirements

1. **Test Coverage**: Minimum 80% coverage for new code
2. **Type Safety**: All functions must have type annotations
3. **Schema Validation**: State objects must validate against Pydantic schemas

## Guardian Council Review

Significant changes (architecture, security, state schema) require Guardian Council review:

1. **Submit Proposal**: Create a debate document in `docs/debates/`
2. **Council Evaluation**: The 20-voice council evaluates the proposal
3. **Consensus Threshold**: Requires >95% approval or addresses all concerns
4. **Implementation**: Approved changes can proceed to PR

## Testing Guidelines

### Unit Tests

- Located in `tests/unit/`
- Test pure functions in isolation
- Use `pytest` fixtures for setup
- Mock external dependencies (Redis, OpenAI API)

### Integration Tests

- Located in `tests/integration/`
- Test component interactions
- Use Docker containers for external services
- Clean up resources in teardown

### Property-Based Tests

- Use `hypothesis` for property-based testing
- Focus on state machine invariants
- Test edge cases automatically

Example:
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1))
def test_embedding_roundtrip(text: str):
    """Embedding retrieval should return same text."""
    embedding = librarian.embed(text)
    result = librarian.retrieve(embedding)
    assert result == text
```

## Documentation

### Code Documentation

- **Docstrings**: Use Google-style docstrings for all public functions
- **Type Hints**: All function signatures must include types
- **Inline Comments**: Explain complex logic or non-obvious decisions

Example:
```python
def embed_text(text: str, model: str = "text-embedding-3-small") -> np.ndarray:
    """Generate semantic embedding for text using OpenAI API.

    Args:
        text: Input text to embed
        model: OpenAI embedding model name

    Returns:
        Numpy array of shape (1536,) containing the embedding

    Raises:
        ValueError: If text is empty or exceeds token limit

    Example:
        >>> embedding = embed_text("Hello world")
        >>> embedding.shape
        (1536,)
    """
```

### Architecture Documentation

- Update relevant docs in `docs/` for architectural changes
- Add decision records to `docs/debates/` for significant choices
- Update `docs/narratives/` for system evolution stories

## Performance Considerations

- **JAX Compatibility**: Core functions should be JAX-compatible (pure, no side effects)
- **Caching**: Use Redis for expensive computations (embeddings, API calls)
- **Batch Operations**: Prefer batch operations over loops where possible
- **Profiling**: Use `pytest-benchmark` for performance-critical code

## Security

- **No Hardcoded Secrets**: Use environment variables or secure vaults
- **YoloGuard Integration**: Security-critical paths must use YoloGuard validation
- **Input Validation**: Validate all external inputs against schemas
- **Audit Logging**: Log security-relevant events

## Release Process

1. **Version Bump**: Update version in `pyproject.toml`
2. **Changelog**: Update `CHANGELOG.md` with changes
3. **Tag Release**: Create git tag following semver (e.g., `v2.0.0`)
4. **GitHub Release**: Create release with notes
5. **CI/CD**: Automated deployment via GitHub Actions

## Getting Help

- **Documentation**: Check `docs/` for guides
- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Contact**: Reach out to maintainers via email

## License

By contributing to InfraFabric, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to InfraFabric!**

For questions about the Guardian Council process or IF.TTT compliance, see:
- [IF Protocol Registry](docs/IF_PROTOCOL_REGISTRY.md)
- [IF.TTT Framework](docs/IF_TTT_TRACEABILITY.md)
- [Guardian Council Structure](docs/debates/001_genesis_structure.md)
