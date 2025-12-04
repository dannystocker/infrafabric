#!/usr/bin/env python3
"""
Validate legal citations against schema and verify file integrity.

This tool performs comprehensive validation of citation metadata and
underlying document files to ensure IF.TTT compliance.
"""

import json
import hashlib
import os
import sys
from pathlib import Path
from datetime import datetime
import jsonschema

def calculate_sha256(file_path):
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def load_schema(schema_path):
    """Load JSON schema for validation."""
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_citations(citations_dir):
    """Load all citation files from directory."""
    citations = []
    for citation_file in Path(citations_dir).glob('legal-corpus-citations-*.json'):
        with open(citation_file, 'r', encoding='utf-8') as f:
            citations.extend(json.load(f))
    return citations

def validate_citation_schema(citation, schema):
    """Validate citation against JSON schema."""
    try:
        jsonschema.validate(instance=citation, schema=schema)
        return True, "Schema valid"
    except jsonschema.ValidationError as e:
        return False, f"Schema validation failed: {e.message}"
    except jsonschema.SchemaError as e:
        return False, f"Schema error: {e.message}"

def validate_file_existence(citation, corpus_root):
    """Check if file exists at local_path."""
    local_path = citation['local_verification']['local_path']
    full_path = corpus_root / local_path

    if full_path.exists():
        return True, "File exists"
    else:
        return False, f"File not found: {full_path}"

def validate_hash(citation, corpus_root):
    """Verify SHA-256 hash of file."""
    local_path = citation['local_verification']['local_path']
    full_path = corpus_root / local_path
    expected_hash = citation['local_verification']['sha256']

    if not full_path.exists():
        return False, "File not found (cannot verify hash)"

    try:
        actual_hash = calculate_sha256(full_path)
        if actual_hash == expected_hash:
            return True, f"Hash matches: {actual_hash[:16]}..."
        else:
            return False, f"Hash mismatch! Expected: {expected_hash[:16]}... Got: {actual_hash[:16]}..."
    except Exception as e:
        return False, f"Error calculating hash: {str(e)}"

def validate_file_size(citation, corpus_root):
    """Verify file size matches metadata."""
    local_path = citation['local_verification']['local_path']
    full_path = corpus_root / local_path
    expected_size = citation['local_verification']['file_size_bytes']

    if not full_path.exists():
        return False, "File not found (cannot verify size)"

    actual_size = full_path.stat().st_size
    if actual_size == expected_size:
        return True, f"Size matches: {actual_size} bytes"
    else:
        return False, f"Size mismatch! Expected: {expected_size} bytes, Got: {actual_size} bytes"

def validate_git_commit(citation, corpus_root):
    """Check if git commit exists in repository."""
    commit_hash = citation['local_verification']['git_commit']

    # Try to verify git commit exists
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'cat-file', '-t', commit_hash],
            cwd=corpus_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, f"Git commit verified: {commit_hash[:7]}"
        else:
            return False, f"Git commit not found: {commit_hash}"
    except Exception as e:
        return False, f"Error verifying git commit: {str(e)}"

def validate_provenance_chain(citation):
    """Verify provenance chain structure and completeness."""
    chain = citation.get('provenance_chain', [])

    if not isinstance(chain, list) or len(chain) < 3:
        return False, f"Provenance chain incomplete: {len(chain)} steps (minimum 3 required)"

    required_steps = {'download', 'validation', 'ingestion'}
    found_steps = {step['step'] for step in chain}

    missing = required_steps - found_steps
    if missing:
        return False, f"Missing provenance steps: {', '.join(missing)}"

    # Check all steps have timestamps
    for step in chain:
        if 'timestamp' not in step:
            return False, f"Step {step['step']} missing timestamp"

    return True, f"Provenance chain complete: {len(chain)} steps"

def validate_citation_id_format(citation):
    """Verify citation_id format matches if://citation/[uuid]."""
    citation_id = citation.get('citation_id', '')

    if not citation_id.startswith('if://citation/'):
        return False, "Invalid citation_id format (must start with if://citation/)"

    uuid_part = citation_id[len('if://citation/'):]
    if len(uuid_part) != 36 or uuid_part.count('-') != 4:
        return False, f"Invalid UUID format: {uuid_part}"

    return True, f"Citation ID format valid: {citation_id}"

def validate_timestamps(citation):
    """Verify all timestamps are valid ISO 8601."""
    timestamp_fields = [
        'verification_date',
        'local_verification.ingested_date',
        'authoritative_source.accessed_date'
    ]

    for field in timestamp_fields:
        parts = field.split('.')
        obj = citation
        for part in parts[:-1]:
            obj = obj.get(part, {})

        value = obj.get(parts[-1]) if isinstance(obj, dict) else None

        if value:
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
            except:
                return False, f"Invalid timestamp in {field}: {value}"

    return True, "All timestamps valid"

def validate_citation(citation, schema, corpus_root):
    """Perform all validation checks on a single citation."""
    results = {
        'citation_id': citation.get('citation_id', 'UNKNOWN'),
        'document_name': citation.get('document_name', 'UNKNOWN'),
        'checks': {}
    }

    # Schema validation
    passed, msg = validate_citation_schema(citation, schema)
    results['checks']['schema'] = {'passed': passed, 'message': msg}

    # Citation ID format
    passed, msg = validate_citation_id_format(citation)
    results['checks']['citation_id_format'] = {'passed': passed, 'message': msg}

    # File existence
    passed, msg = validate_file_existence(citation, corpus_root)
    results['checks']['file_exists'] = {'passed': passed, 'message': msg}

    # File size
    passed, msg = validate_file_size(citation, corpus_root)
    results['checks']['file_size'] = {'passed': passed, 'message': msg}

    # SHA-256 hash
    passed, msg = validate_hash(citation, corpus_root)
    results['checks']['sha256_hash'] = {'passed': passed, 'message': msg}

    # Git commit
    passed, msg = validate_git_commit(citation, corpus_root)
    results['checks']['git_commit'] = {'passed': passed, 'message': msg}

    # Provenance chain
    passed, msg = validate_provenance_chain(citation)
    results['checks']['provenance_chain'] = {'passed': passed, 'message': msg}

    # Timestamps
    passed, msg = validate_timestamps(citation)
    results['checks']['timestamps'] = {'passed': passed, 'message': msg}

    # Overall status
    results['overall_status'] = all(
        check['passed'] for check in results['checks'].values()
    )

    return results

def print_validation_report(all_results):
    """Print human-readable validation report."""
    print("\n" + "="*80)
    print("IF.TTT LEGAL CITATION VALIDATION REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().isoformat()}")
    print(f"Total Citations: {len(all_results)}")

    # Summary statistics
    passed_count = sum(1 for r in all_results if r['overall_status'])
    failed_count = len(all_results) - passed_count

    print(f"\nSummary:")
    print(f"  ✓ Passed: {passed_count}/{len(all_results)}")
    print(f"  ✗ Failed: {failed_count}/{len(all_results)}")

    if failed_count == 0:
        print(f"\nRESULT: ALL CITATIONS VERIFIED")
        return 0

    # Details of failures
    print("\n" + "-"*80)
    print("FAILED CITATIONS:")
    print("-"*80)

    for result in all_results:
        if not result['overall_status']:
            print(f"\n{result['document_name']} ({result['citation_id'][-36:]})")
            for check_name, check_result in result['checks'].items():
                if not check_result['passed']:
                    print(f"  ✗ {check_name}: {check_result['message']}")

    # Summary by check type
    print("\n" + "-"*80)
    print("FAILURES BY CHECK TYPE:")
    print("-"*80)

    check_types = set()
    for result in all_results:
        check_types.update(result['checks'].keys())

    for check_type in sorted(check_types):
        failures = [
            r for r in all_results
            if not r['checks'][check_type]['passed']
        ]
        if failures:
            print(f"\n{check_type}: {len(failures)} failures")
            for failure in failures:
                msg = failure['checks'][check_type]['message']
                print(f"  - {failure['document_name']}: {msg}")

    return 1

def main():
    corpus_root = Path('/home/setup/if-legal-corpus')
    schema_path = corpus_root / 'schemas' / 'legal-citation-v1.0.json'
    citations_dir = corpus_root / 'citations'

    print("Loading schema...")
    try:
        schema = load_schema(schema_path)
    except Exception as e:
        print(f"ERROR: Failed to load schema: {e}")
        return 1

    print(f"Loading citations from {citations_dir}...")
    try:
        citations = load_citations(citations_dir)
        print(f"Loaded {len(citations)} citations")
    except Exception as e:
        print(f"ERROR: Failed to load citations: {e}")
        return 1

    if not citations:
        print("ERROR: No citations found")
        return 1

    print("\nValidating citations...")
    all_results = []

    for i, citation in enumerate(citations, 1):
        result = validate_citation(citation, schema, corpus_root)
        all_results.append(result)

        status = "✓" if result['overall_status'] else "✗"
        doc_name = result['document_name'][:40]
        print(f"  [{i:2}/{len(citations)}] {status} {doc_name:40}")

    # Print detailed report
    exit_code = print_validation_report(all_results)

    # Write JSON report
    report_file = corpus_root / 'audit' / f'validation-report-{datetime.now().strftime("%Y-%m-%d")}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nDetailed report written to: {report_file}")

    return exit_code

if __name__ == '__main__':
    sys.exit(main())
