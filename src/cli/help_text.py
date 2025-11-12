"""
IF CLI Enhanced Help Text Module

Provides rich help text with examples, common use cases, and workflows.

Philosophy: IF.ground Principle 8 - Observability without fragility
Help text should guide users toward success, not just document flags.
"""

from typing import Dict, List


# Enhanced command descriptions with examples
WITNESS_COMMANDS_HELP = {
    "log": {
        "short": "Create new witness entry with provenance",
        "long": """
Create a new witness entry in the provenance log.

Each entry is cryptographically signed and chained to previous entries,
creating a tamper-proof audit trail. Entries include event type, component,
trace ID for cross-operation linking, and optional cost tracking.
        """,
        "examples": [
            {
                "description": "Log a simple event",
                "command": """if witness log \\
  --event scan_complete \\
  --component IF.yologuard \\
  --trace-id scan-2025-001 \\
  --payload '{"files": 42, "secrets": 0}'"""
            },
            {
                "description": "Log with cost tracking",
                "command": """if witness log \\
  --event llm_analysis \\
  --component IF.swarm \\
  --trace-id task-456 \\
  --payload '{"analysis": "safe"}' \\
  --tokens-in 1000 \\
  --tokens-out 200 \\
  --cost 0.005 \\
  --model claude-sonnet-4.5"""
            }
        ],
        "tips": [
            "Use consistent trace-id across related operations for tracing",
            "Always use single quotes around JSON payload to avoid shell escaping",
            "Cost tracking is optional but recommended for budget monitoring"
        ]
    },

    "query": {
        "short": "Search witness log with flexible filters",
        "long": """
Search witness entries using various filters: component, event type,
trace ID, date range, and result limit. Supports both text and JSON output.

Perfect for finding specific operations, debugging issues, or analyzing
patterns across multiple events.
        """,
        "examples": [
            {
                "description": "Find all entries for a component",
                "command": "if witness query --component IF.coordinator --limit 10"
            },
            {
                "description": "Find events by type",
                "command": "if witness query --event task_claimed --format json"
            },
            {
                "description": "Find all operations in a trace",
                "command": "if witness query --trace-id trace-abc123"
            },
            {
                "description": "Date range search",
                "command": """if witness query \\
  --start-date 2025-11-01 \\
  --end-date 2025-11-30 \\
  --component IF.governor"""
            },
            {
                "description": "Combined filters",
                "command": """if witness query \\
  --component IF.swarm \\
  --event task_complete \\
  --start-date 2025-11-12 \\
  --limit 5"""
            }
        ],
        "tips": [
            "Use --format json for programmatic processing",
            "Default limit is 50 results, increase if needed",
            "Combine multiple filters for precise searching",
            "Date format is YYYY-MM-DD (ISO 8601)"
        ]
    },

    "verify": {
        "short": "Verify hash chain integrity and signatures",
        "long": """
Verify the complete witness log for tampering.

Checks:
1. Hash chain integrity (each entry links to previous)
2. Ed25519 signature validity for all entries
3. Content hash matches for tamper detection

Returns success (exit 0) if valid, error (exit 1) if compromised.
        """,
        "examples": [
            {
                "description": "Verify entire witness log",
                "command": "if witness verify"
            },
            {
                "description": "Verify and show count",
                "command": "if witness verify && echo 'Log is valid!'"
            }
        ],
        "tips": [
            "Run verify before critical operations",
            "Verification failure indicates tampering - preserve evidence",
            "Export audit trail immediately if verification fails",
            "All entries are verified, not just recent ones"
        ]
    },

    "trace": {
        "short": "Follow complete trace chain across operations",
        "long": """
Retrieve all witness entries sharing a trace ID, showing the complete
operational flow across components.

Displays entries in chronological order with timestamps, payloads, and
cost information. Perfect for debugging multi-component workflows.
        """,
        "examples": [
            {
                "description": "Trace a task workflow",
                "command": "if witness trace task-2025-001"
            },
            {
                "description": "Trace with JSON output",
                "command": "if witness trace task-abc123 --format json"
            },
            {
                "description": "Trace and export to file",
                "command": "if witness trace task-456 --format json > trace_report.json"
            }
        ],
        "tips": [
            "Use consistent trace IDs across related operations",
            "Traces show full operational history",
            "JSON format useful for automated analysis",
            "Shows total duration and cost at end"
        ]
    },

    "cost": {
        "short": "Analyze token usage and costs",
        "long": """
Show cost breakdown by component, trace ID, or date range.

Useful for:
- Budget monitoring
- Cost optimization
- Component cost analysis
- Model selection decisions
        """,
        "examples": [
            {
                "description": "Cost for specific trace",
                "command": "if witness cost --trace-id task-123"
            },
            {
                "description": "Cost by component",
                "command": "if witness cost --component IF.swarm"
            },
            {
                "description": "Cost for date range",
                "command": """if witness cost \\
  --start-date 2025-11-01 \\
  --end-date 2025-11-30 \\
  --format json"""
            },
            {
                "description": "Monthly cost summary",
                "command": "if witness cost --start-date 2025-11-01"
            }
        ],
        "tips": [
            "Use JSON format for automated cost tracking",
            "Group by component to find expensive operations",
            "Set up budget alerts based on cost trends",
            "Cost tracking requires --tokens-in/out/cost on log"
        ]
    },

    "export": {
        "short": "Export audit trail in multiple formats",
        "long": """
Export witness log for compliance, archival, or analysis.

Formats:
- JSON: Full structured data, programmatic access
- CSV: Spreadsheet-compatible, reporting
- PDF: Human-readable compliance reports

Supports date range filtering for targeted exports.
        """,
        "examples": [
            {
                "description": "Export to JSON",
                "command": "if witness export --format json --output audit.json"
            },
            {
                "description": "Export to CSV for Excel",
                "command": "if witness export --format csv --output report.csv"
            },
            {
                "description": "Generate PDF compliance report",
                "command": """if witness export \\
  --format pdf \\
  --output compliance_report.pdf \\
  --date-range 2025-11-01:2025-11-30"""
            },
            {
                "description": "Export to stdout (pipeable)",
                "command": "if witness export --format json | jq '.[] | .event'"
            }
        ],
        "tips": [
            "PDF format requires reportlab: pip install reportlab",
            "Date range format: YYYY-MM-DD or YYYY-MM-DD:YYYY-MM-DD",
            "JSON export is most flexible for automation",
            "CSV export excludes nested payload data"
        ]
    }
}


# Common workflows showing how commands work together
COMMON_WORKFLOWS = [
    {
        "name": "Basic Logging and Verification",
        "description": "Log an event and verify integrity",
        "steps": [
            "if witness log --event test --component IF.test --trace-id test-1 --payload '{\"status\": \"ok\"}'",
            "if witness verify",
            "if witness query --trace-id test-1"
        ]
    },
    {
        "name": "Full Task Tracing",
        "description": "Trace a task across multiple components",
        "steps": [
            "# Component 1 logs start",
            "if witness log --event task_start --component IF.coordinator --trace-id task-123 --payload '{\"task\": \"analysis\"}'",
            "",
            "# Component 2 logs progress",
            "if witness log --event task_executing --component IF.swarm --trace-id task-123 --payload '{\"progress\": 50}'",
            "",
            "# Component 3 logs completion",
            "if witness log --event task_complete --component IF.swarm --trace-id task-123 --payload '{\"result\": \"success\"}'",
            "",
            "# View full trace",
            "if witness trace task-123"
        ]
    },
    {
        "name": "Cost Analysis Workflow",
        "description": "Track and analyze costs",
        "steps": [
            "# Log with cost",
            "if witness log --event analysis --component IF.swarm --trace-id cost-1 --payload '{\"data\": \"test\"}' --tokens-in 1000 --tokens-out 200 --cost 0.005 --model haiku",
            "",
            "# View cost for trace",
            "if witness cost --trace-id cost-1",
            "",
            "# View cost by component",
            "if witness cost --component IF.swarm",
            "",
            "# Export cost data",
            "if witness cost --format json > costs.json"
        ]
    },
    {
        "name": "Compliance Audit Workflow",
        "description": "Generate audit reports",
        "steps": [
            "# Verify integrity first",
            "if witness verify",
            "",
            "# Export full audit trail",
            "if witness export --format json --output full_audit.json",
            "",
            "# Generate PDF report for stakeholders",
            "if witness export --format pdf --output audit_report_$(date +%Y%m%d).pdf",
            "",
            "# Export specific date range",
            "if witness export --format csv --date-range 2025-11-01:2025-11-30 --output november_audit.csv"
        ]
    }
]


# Quick reference guide
QUICK_REFERENCE = {
    "Common Operations": {
        "Log event": "if witness log --event <event> --component <comp> --trace-id <id> --payload '{...}'",
        "Search logs": "if witness query --component <comp>",
        "Follow trace": "if witness trace <trace-id>",
        "Verify chain": "if witness verify",
        "Export data": "if witness export --format json"
    },
    "Filtering": {
        "By component": "--component IF.coordinator",
        "By event": "--event task_claimed",
        "By trace": "--trace-id task-123",
        "By date": "--start-date 2025-11-01 --end-date 2025-11-30",
        "Limit results": "--limit 10"
    },
    "Output Formats": {
        "Human readable": "--format text (default)",
        "JSON": "--format json",
        "CSV": "--format csv (export only)",
        "PDF": "--format pdf (export only)"
    },
    "Cost Tracking": {
        "With cost": "--tokens-in 1000 --tokens-out 200 --cost 0.005 --model haiku",
        "View costs": "if witness cost --trace-id <id>",
        "By component": "if witness cost --component <comp>"
    }
}


def format_command_help(command: str) -> str:
    """
    Format rich help text for a command.

    Args:
        command: Command name (log, query, verify, trace, cost, export)

    Returns:
        Formatted help text with examples and tips
    """
    if command not in WITNESS_COMMANDS_HELP:
        return f"No enhanced help available for '{command}'"

    help_data = WITNESS_COMMANDS_HELP[command]
    lines = []

    # Short description
    lines.append(f"📖 {help_data['short']}")
    lines.append("")

    # Long description
    lines.append(help_data['long'].strip())
    lines.append("")

    # Examples
    if help_data.get('examples'):
        lines.append("💡 Examples:")
        lines.append("")
        for ex in help_data['examples']:
            lines.append(f"  {ex['description']}:")
            for line in ex['command'].split('\n'):
                lines.append(f"    {line}")
            lines.append("")

    # Tips
    if help_data.get('tips'):
        lines.append("⚡ Tips:")
        for tip in help_data['tips']:
            lines.append(f"  • {tip}")
        lines.append("")

    return '\n'.join(lines)


def format_workflow_help(workflow_name: str = None) -> str:
    """
    Format help for common workflows.

    Args:
        workflow_name: Optional specific workflow name

    Returns:
        Formatted workflow help text
    """
    if workflow_name:
        workflow = next((w for w in COMMON_WORKFLOWS if w['name'].lower() == workflow_name.lower()), None)
        if not workflow:
            return f"No workflow found: {workflow_name}"

        lines = [
            f"🔧 Workflow: {workflow['name']}",
            f"📝 {workflow['description']}",
            ""
        ]
        for step in workflow['steps']:
            lines.append(f"  {step}")
        return '\n'.join(lines)

    # Show all workflows
    lines = ["🔧 Common Workflows", ""]
    for workflow in COMMON_WORKFLOWS:
        lines.append(f"• {workflow['name']}")
        lines.append(f"  {workflow['description']}")
        lines.append("")

    lines.append("💡 View specific workflow: if witness help --workflow <name>")
    return '\n'.join(lines)


def format_quick_reference() -> str:
    """Format quick reference guide"""
    lines = ["📋 Quick Reference", ""]

    for category, commands in QUICK_REFERENCE.items():
        lines.append(f"## {category}")
        lines.append("")
        max_len = max(len(name) for name in commands.keys())
        for name, cmd in commands.items():
            padding = " " * (max_len - len(name))
            lines.append(f"  {name}{padding}  {cmd}")
        lines.append("")

    return '\n'.join(lines)


# Command epilogs (shown after command help)
COMMAND_EPILOGS = {
    "log": "See also: if witness query, if witness trace, if witness verify",
    "query": "See also: if witness trace <trace-id>, if witness cost",
    "verify": "See also: if witness export --format pdf (for audit reports)",
    "trace": "See also: if witness query, if witness cost --trace-id <id>",
    "cost": "See also: if witness query --component <comp>",
    "export": "See also: if witness verify (run before export)"
}


def get_command_epilog(command: str) -> str:
    """Get epilog text for a command"""
    epilog = COMMAND_EPILOGS.get(command, "")
    if epilog:
        return f"\n💡 {epilog}\n"
    return ""
