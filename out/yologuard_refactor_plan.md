# Yologuard Refactor Plan

## Proposed package layout (`src/infrafabric/yologuard/`)
1. `detector.py` – contains `SecretRedactorV3` (or renamed `YologuardScanner`). Responsibilities: orchestrate pattern scanning, entropy detection, relationship scoring, and public helpers (`scan_text`, `redact`, `scan_file`).
2. `patterns.py` – hosts the large `PATTERNS` list, optionally split into thematic groups (AWS, JWT, OAuth, SSH, config passwords). Expose helper functions/metadata for test discovery (e.g., mapping pattern names to regex).
3. `decoders.py` – publishes `shannon_entropy`, `looks_like_base64`, `try_decode_base64`, `try_decode_hex`, `extract_values_from_json`, `extract_values_from_xml`. These can be reused wherever encoded payloads need to be normalized.
4. `relationships.py` – isolates the Wu Lun heuristics (`find_nearby_tokens`, `detect_user_password_relationship`, `detect_key_endpoint_relationship`, `detect_token_session_relationship`, `detect_cert_authority_relationship`, `confucian_relationship_score`). Export `find_secret_relationships` for the detector and for standalone tests.
5. `cli.py` – thin wrapper that wires `SecretRedactorV3` into a CLI/entry point. Accepts flags such as `--dry-run`, `--dry-redact`, `--dirs`, and a `--skip` list for directories with synthetic secrets (tests, docs, `out/`).
6. `__init__.py` – re-export the public API, version info, and the `__all__` names.

## Target public API
- `SecretRedactorV3.scan_text(text: str) -> List[Tuple[str, str]]`: returns pattern matches with their replacement tokens.
- `SecretRedactorV3.predecode_and_rescan(text: str) -> List[Tuple[str, str]]`: public helper for the decoder/relationship pipeline.
- `SecretRedactorV3.redact(text: str) -> str`: safe redaction that respects Wu Lun scoring.
- `SecretRedactorV3.scan_file(path: Path) -> List[Dict]`: returns structured metadata for CLI reporting.
- `find_secret_relationships(token: str, text: str, position: int) -> List[Tuple[str, str, str]]`: exposed from `relationships.py` so callers can inspect relationships without instantiating the relator.
- `confucian_relationship_score(relationships: Iterable[Tuple]) -> float`: signature for scoring heuristics.
- `is_high_entropy(token: str, threshold: float) -> bool`: helper in `decoders.py` for unit tests to verify the entropy gate.

## Test structure expectations
- `tests/test_yologuard.py` (see `out/tests_test_yologuard.py`) should import the refactored classes/functions and run the scenarios from `out/yologuard_test_vectors.md`.
- Split tests into modules by feature (patterns vs decoding vs relationships): e.g., `tests/test_patterns.py` asserts that known patterns continue to match AWS keys, JWTs, and bcrypt hashes; `tests/test_decoders.py` drives the Base64/hex/JSON/XML helpers; `tests/test_relationships.py` drives Wu Lun scoring.
- Fixtures can be built from the vector list (password JSON, API key+endpoint, high-entropy noise, large config, hex secret, scattered relationship, JWT header, and the large config to guard against false positives).
- Add a smoke test that imports `SecretRedactorV3` and runs it against the repository (`code/`, `docs/`) in dry-run mode to ensure redaction remains deterministic (use the CLI wrapper once the `cli.py` module exists).
