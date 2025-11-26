#!/usr/bin/env python3
"""
Redis Schema Validation Tool
=============================

Compares live (or simulated) Redis data against Pydantic schema definitions.
Validates:
  - Required fields presence
  - Field types
  - Legacy "List" types (should be Dict[str, Any])
  - Additional fields
  - Overall schema compliance

Reports:
  - Compliance rate
  - Specific violations
  - Recommendations
"""

import json
import sys
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

sys.path.insert(0, 'src')

from infrafabric.state.schema import TaskSchema, ContextSchema
from pydantic import ValidationError, BaseModel


@dataclass
class Violation:
    """Represents a single schema violation"""
    key: str
    violation_type: str  # "missing_field", "wrong_type", "legacy_list", "invalid_value", "extra_field"
    field_name: str
    expected: str
    actual: str
    details: str


@dataclass
class ValidationResult:
    """Result of validating a single Redis record"""
    redis_key: str
    schema_name: str
    is_valid: bool
    violations: List[Violation]
    data: Dict[str, Any]
    timestamp: str


class RedisSchemaValidator:
    """Validates Redis data against Pydantic schemas"""

    def __init__(self):
        self.schema_map = {
            "task:": TaskSchema,
            "context:": ContextSchema,
            "finding:": None,  # FindingSchema not yet defined in schema.py
        }
        self.results: List[ValidationResult] = []

    def detect_schema_type(self, key: str) -> Tuple[str, Any]:
        """Determine schema type from Redis key pattern"""
        for pattern, schema in self.schema_map.items():
            if key.startswith(pattern):
                return pattern, schema
        return "unknown", None

    def validate_single_record(self, redis_key: str, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate a single Redis record against its schema.

        Args:
            redis_key: Redis key (e.g., "task:123")
            data: Parsed JSON data from Redis

        Returns:
            ValidationResult with violations list
        """
        pattern, schema_class = self.detect_schema_type(redis_key)
        violations = []

        # Case 1: No schema defined for this key pattern
        if schema_class is None:
            return ValidationResult(
                redis_key=redis_key,
                schema_name=pattern,
                is_valid=False,
                violations=[
                    Violation(
                        key=redis_key,
                        violation_type="schema_not_defined",
                        field_name="",
                        expected="Schema defined",
                        actual="None",
                        details=f"No schema defined for key pattern: {pattern}"
                    )
                ],
                data=data,
                timestamp=datetime.utcnow().isoformat()
            )

        # Check for extra fields before validation
        schema_fields = set(schema_class.model_fields.keys())
        for data_field in data.keys():
            if data_field not in schema_fields:
                violations.append(
                    Violation(
                        key=redis_key,
                        violation_type="extra_field",
                        field_name=data_field,
                        expected="Field not in schema",
                        actual=str(data[data_field]),
                        details=f"Extra field not defined in schema: {data_field}"
                    )
                )

        # Case 2: Try to validate against schema
        try:
            schema_class.model_validate(data)
            # If extra fields exist but validation passed, still report as invalid
            if violations:
                return ValidationResult(
                    redis_key=redis_key,
                    schema_name=schema_class.__name__,
                    is_valid=False,
                    violations=violations,
                    data=data,
                    timestamp=datetime.utcnow().isoformat()
                )
            return ValidationResult(
                redis_key=redis_key,
                schema_name=schema_class.__name__,
                is_valid=True,
                violations=[],
                data=data,
                timestamp=datetime.utcnow().isoformat()
            )
        except ValidationError as e:
            # Extract violations from Pydantic errors
            for error in e.errors():
                loc = error['loc']
                field_name = str(loc[0]) if loc else "unknown"
                msg = error['msg']
                error_type = error['type']

                # Classify violation type
                if "missing" in msg.lower() or error_type == "missing":
                    violation_type = "missing_field"
                    expected = f"Required {error_type}"
                    actual = "Not provided"
                elif "type" in msg.lower() or error_type.startswith("type"):
                    violation_type = "wrong_type"
                    expected = self._get_expected_type(schema_class, field_name)
                    actual = str(type(data.get(field_name)).__name__)
                elif "list" in msg.lower():
                    violation_type = "legacy_list"
                    expected = "Dict[str, Any]"
                    actual = "List"
                else:
                    violation_type = "invalid_value"
                    expected = error_type
                    actual = str(data.get(field_name))

                violations.append(
                    Violation(
                        key=redis_key,
                        violation_type=violation_type,
                        field_name=field_name,
                        expected=expected,
                        actual=actual,
                        details=msg
                    )
                )

            return ValidationResult(
                redis_key=redis_key,
                schema_name=schema_class.__name__,
                is_valid=False,
                violations=violations,
                data=data,
                timestamp=datetime.utcnow().isoformat()
            )

    def _get_expected_type(self, schema_class: BaseModel, field_name: str) -> str:
        """Get expected type for a field"""
        if field_name in schema_class.model_fields:
            field_info = schema_class.model_fields[field_name]
            return str(field_info.annotation)
        return "unknown"

    def validate_redis_samples(self, samples: Dict[str, Dict]) -> List[ValidationResult]:
        """
        Validate multiple Redis samples.

        Args:
            samples: Dict of {redis_key: data}

        Returns:
            List of ValidationResults
        """
        results = []
        for key, data in samples.items():
            result = self.validate_single_record(key, data)
            results.append(result)
            self.results.append(result)

        return results

    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report from all validated records"""
        if not self.results:
            return {
                "total_records": 0,
                "valid_records": 0,
                "invalid_records": 0,
                "compliance_rate": 0.0,
                "violations": {}
            }

        total = len(self.results)
        valid = len([r for r in self.results if r.is_valid])
        invalid = total - valid

        # Aggregate violations
        violation_counts = {}
        all_violations = []

        for result in self.results:
            for violation in result.violations:
                vtype = violation.violation_type
                violation_counts[vtype] = violation_counts.get(vtype, 0) + 1
                all_violations.append({
                    "key": violation.key,
                    "type": vtype,
                    "field": violation.field_name,
                    "expected": violation.expected,
                    "actual": violation.actual,
                    "details": violation.details,
                })

        compliance_rate = (valid / total * 100) if total > 0 else 0.0

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_records": total,
            "valid_records": valid,
            "invalid_records": invalid,
            "compliance_rate": compliance_rate,
            "violation_summary": violation_counts,
            "violations_by_key": self._group_violations_by_key(),
            "all_violations": all_violations,
            "recommendations": self._generate_recommendations()
        }

    def _group_violations_by_key(self) -> Dict[str, List[Dict]]:
        """Group violations by Redis key"""
        grouped = {}
        for result in self.results:
            if result.violations:
                grouped[result.redis_key] = [
                    {
                        "type": v.violation_type,
                        "field": v.field_name,
                        "expected": v.expected,
                        "actual": v.actual,
                        "details": v.details,
                    }
                    for v in result.violations
                ]
        return grouped

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on violations found"""
        recommendations = []
        violation_types = set()

        for result in self.results:
            for v in result.violations:
                violation_types.add(v.violation_type)

        if "missing_field" in violation_types:
            recommendations.append(
                "ACTION: Ensure all required fields are populated before writing to Redis"
            )

        if "wrong_type" in violation_types:
            recommendations.append(
                "ACTION: Validate field types match schema definitions (str, int, Dict, etc.)"
            )

        if "legacy_list" in violation_types:
            recommendations.append(
                "ACTION: Replace legacy List types with Dict[str, Any] in Redis schema"
            )

        if "extra_field" in violation_types:
            recommendations.append(
                "ACTION: Remove extra fields not defined in schema or update schema"
            )

        if "schema_not_defined" in violation_types:
            recommendations.append(
                "ACTION: Define missing schemas (e.g., FindingSchema) in state/schema.py"
            )

        if not recommendations:
            recommendations.append(
                "✓ All validated records are compliant with schema definitions"
            )

        return recommendations


def create_test_samples() -> Dict[str, Dict[str, Any]]:
    """Create test Redis samples with various compliance scenarios"""

    samples = {
        # ========== VALID SAMPLES ==========
        "task:valid_001": {
            "id": "task_valid_001",
            "status": "running",
            "priority": 3,
            "payload": {"input": "process_data", "timeout": 30},
            "result": None
        },
        "task:valid_002": {
            "id": "task_valid_002",
            "status": "complete",
            "priority": 1,
            "payload": {"command": "analyze", "params": {}},
            "result": {"status": "success", "output": "analyzed"}
        },
        "context:valid_001": {
            "instance_id": "instance_abc123",
            "tokens_used": 2500,
            "summary": "Processed debate round 5"
        },

        # ========== MISSING REQUIRED FIELDS ==========
        "task:missing_id": {
            # Missing 'id' field
            "status": "pending",
            "priority": 2,
            "payload": {"data": "test"},
        },
        "task:missing_payload": {
            # Missing 'payload' field
            "id": "task_missing_payload",
            "status": "running",
            "priority": 5,
        },
        "context:missing_tokens": {
            # Missing 'tokens_used' field
            "instance_id": "instance_xyz",
            "summary": "Some summary"
        },

        # ========== WRONG TYPES ==========
        "task:wrong_type_status": {
            "id": "task_wrong_status",
            "status": "invalid_status",  # Should be Literal['pending', 'running', 'failed', 'complete']
            "priority": 1,
            "payload": {"data": "test"},
        },
        "task:wrong_type_priority": {
            "id": "task_wrong_priority",
            "status": "running",
            "priority": "high",  # Should be int
            "payload": {"data": "test"},
        },
        "context:wrong_type_tokens": {
            "instance_id": "instance_def",
            "tokens_used": "2500",  # Should be int
            "summary": "test summary"
        },

        # ========== LEGACY LIST TYPES ==========
        "task:legacy_list_payload": {
            "id": "task_legacy_list",
            "status": "pending",
            "priority": 2,
            "payload": ["item1", "item2", "item3"],  # Should be Dict[str, Any]
            "result": None
        },

        # ========== EXTRA FIELDS ==========
        "task:extra_fields": {
            "id": "task_extra",
            "status": "running",
            "priority": 2,
            "payload": {"data": "test"},
            "result": None,
            "extra_field_1": "should not exist",
            "extra_field_2": {"another": "field"}
        },
        "context:extra_field": {
            "instance_id": "instance_ghi",
            "tokens_used": 1500,
            "summary": "test",
            "extra_context_data": "this field is not in schema"
        },

        # ========== FINDING SCHEMA (NOT DEFINED) ==========
        "finding:undefined_schema": {
            "finding_id": "find_001",
            "timestamp": "2025-11-26T10:00:00Z",
            "content": "Sample finding",
            "worker_id": "worker_1"
        },

        # ========== EDGE CASES ==========
        "task:null_result": {
            "id": "task_null",
            "status": "complete",
            "priority": 0,
            "payload": {},
            "result": None  # Explicitly null is valid
        },
        "task:missing_result_ok": {
            # result is optional (not required)
            "id": "task_no_result",
            "status": "running",
            "priority": 1,
            "payload": {"test": True}
            # Missing result is OK - it's optional
        },
    }

    return samples


def print_report(report: Dict[str, Any]):
    """Pretty print the compliance report"""

    print("\n" + "=" * 100)
    print("REDIS SCHEMA VALIDATION REPORT")
    print("=" * 100)
    print(f"Timestamp: {report['timestamp']}")
    print(f"Total Records Validated: {report['total_records']}")
    print(f"Valid Records: {report['valid_records']}")
    print(f"Invalid Records: {report['invalid_records']}")
    print(f"Compliance Rate: {report['compliance_rate']:.1f}%")

    print("\n" + "-" * 100)
    print("VIOLATION SUMMARY")
    print("-" * 100)

    if report['violation_summary']:
        for vtype, count in sorted(report['violation_summary'].items()):
            print(f"  {vtype}: {count}")
    else:
        print("  ✓ No violations found")

    print("\n" + "-" * 100)
    print("VIOLATIONS BY KEY")
    print("-" * 100)

    if report['violations_by_key']:
        for key, violations in sorted(report['violations_by_key'].items()):
            print(f"\n  {key}")
            for v in violations:
                print(f"    - {v['type']}: {v['field']}")
                print(f"      Expected: {v['expected']}")
                print(f"      Actual: {v['actual']}")
                print(f"      Details: {v['details']}")
    else:
        print("  ✓ All keys are compliant")

    print("\n" + "-" * 100)
    print("RECOMMENDATIONS")
    print("-" * 100)
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")

    print("\n" + "=" * 100)


def main():
    """Run Redis schema validation"""

    print("\n" + "=" * 100)
    print("INFRAFABRIC REDIS SCHEMA VALIDATOR")
    print("=" * 100)

    # Create validator
    validator = RedisSchemaValidator()

    # Load test samples
    print("\nLoading test samples...")
    samples = create_test_samples()
    print(f"Loaded {len(samples)} test samples")

    # Validate samples
    print("\nValidating samples against schemas...")
    results = validator.validate_redis_samples(samples)

    # Generate report
    print("Generating compliance report...")
    report = validator.generate_compliance_report()

    # Print report
    print_report(report)

    # Save report to JSON
    report_file = "/tmp/redis_schema_validation_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n✓ Full report saved to: {report_file}")

    return report


if __name__ == "__main__":
    report = main()
    sys.exit(0 if report['compliance_rate'] == 100.0 else 1)
