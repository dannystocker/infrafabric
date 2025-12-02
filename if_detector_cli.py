#!/usr/bin/env python3
"""
IF.detector CLI: Command-line interface for AI text detection and humanization

Main entry point orchestrating:
- Text analysis (analyze command)
- Humanization suggestions (humanize command)
- Batch processing (batch command)

Architecture:
    CLI Interface (argparse)
    ├── analyze: Single file/text analysis with configurable thresholds
    ├── humanize: Generate remediation suggestions
    ├── batch: Process directories with JSON report output
    └── Shared: TextAnalyzer, RemediationEngine, OutputFormatter

Usage:
    python if_detector_cli.py analyze "text or file.txt" --verbose --json
    python if_detector_cli.py humanize document.txt --intensity aggressive
    python if_detector_cli.py batch /path/to/docs --output report.json --threshold 0.7
"""

import argparse
import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import textwrap

# Import the analyzer from if_detector.py
from if_detector import (
    TextAnalyzer,
    DetectionResult,
    Verdict,
    ConfidenceLevel,
    IssueFlag,
    MetricResult
)


class OutputFormatter:
    """Formats analysis results for different output modes"""

    @staticmethod
    def format_human_readable(result: DetectionResult, verbose: bool = False) -> str:
        """Format analysis result as human-readable report"""
        output = []
        output.append("\n" + "=" * 80)
        output.append("IF.DETECTOR ANALYSIS REPORT")
        output.append("=" * 80 + "\n")

        # Header with verdict and confidence
        output.append(f"VERDICT: {result.verdict.value}")
        output.append(f"AI Probability: {result.overall_ai_probability:.1%}")
        output.append(f"Confidence: {result.confidence.value.upper()}")
        output.append("")

        # Text statistics
        output.append("TEXT STATISTICS:")
        output.append(f"  Words: {result.word_count}")
        output.append(f"  Sentences: {result.sentence_count}")
        output.append(f"  Tokens: {result.token_count}")
        output.append(f"  Avg Sentence Length: {result.word_count / max(1, result.sentence_count):.1f} words")
        output.append("")

        # Metric breakdown
        output.append("METRIC BREAKDOWN:")
        output.append("-" * 80)

        for metric_name, metric_result in result.metrics.items():
            output.append(f"\n{metric_name.upper()}")
            output.append(f"  Score: {metric_result.score:.1%} (0=Human, 1=AI)")
            output.append(f"  Verdict: {metric_result.verdict.value}")
            output.append(f"  Human Range: {metric_result.human_range}")
            output.append(f"  AI Range: {metric_result.ai_range}")
            output.append(f"  Analysis: {metric_result.reasoning}")

            if verbose and metric_result.supporting_data:
                output.append("  Supporting Data:")
                for key, value in metric_result.supporting_data.items():
                    if isinstance(value, (int, float)):
                        output.append(f"    {key}: {value}")
                    elif isinstance(value, list) and len(value) <= 3:
                        output.append(f"    {key}: {value}")

        # Specific issues
        if result.specific_issues:
            output.append("\n" + "-" * 80)
            output.append("\nDETECTED ISSUES:")
            output.append("")

            by_severity = {"high": [], "medium": [], "low": []}
            for issue in result.specific_issues:
                by_severity[issue.severity].append(issue)

            for severity in ["high", "medium", "low"]:
                if by_severity[severity]:
                    output.append(f"{severity.upper()} SEVERITY:")
                    for issue in by_severity[severity]:
                        output.append(f"  Line {issue.line_number}: {issue.issue_type}")
                        output.append(f"    Text: {issue.line_text[:70]}...")
                        output.append(f"    Issue: {issue.description}")
                        output.append(f"    Fix: {issue.suggestion}")
                        output.append("")

        # Remediation priority
        if result.remediation_priority:
            output.append("-" * 80)
            output.append("\nREMEDIATION PRIORITY:")
            for i, priority_item in enumerate(result.remediation_priority[:10], 1):
                output.append(f"  {i}. {priority_item}")

        output.append("\n" + "=" * 80)
        return "\n".join(output)

    @staticmethod
    def format_json(result: DetectionResult) -> str:
        """Format analysis result as JSON"""
        return result.to_json()

    @staticmethod
    def format_compact(result: DetectionResult) -> str:
        """Format analysis result as compact single-line summary"""
        return (
            f"Verdict: {result.verdict.value} | "
            f"AI Prob: {result.overall_ai_probability:.0%} | "
            f"Confidence: {result.confidence.value} | "
            f"Issues: {len(result.specific_issues)}"
        )


class HumanizationEngine:
    """Generates humanization suggestions for detected AI text"""

    def __init__(self, analyzer: TextAnalyzer):
        self.analyzer = analyzer
        self.intensity_levels = {
            "subtle": 0.3,
            "moderate": 0.6,
            "aggressive": 0.9
        }

    def humanize(
        self,
        text: str,
        intensity: str = "moderate",
        preserve_technical: bool = False
    ) -> Dict:
        """
        Generate humanization suggestions with before/after comparison

        Args:
            text: Original text to humanize
            intensity: Level of suggested changes (subtle/moderate/aggressive)
            preserve_technical: Don't suggest changes to technical terms

        Returns:
            Dict with suggestions, expected improvements, and implementation plan
        """
        # Analyze original text
        result = self.analyzer.analyze(text)

        intensity_score = self.intensity_levels.get(intensity, 0.6)

        # Generate targeted suggestions
        suggestions = []
        expected_improvements = {}

        # Process metric-level issues
        for metric_name, metric_result in result.metrics.items():
            if metric_result.score > 0.5:  # AI-leaning metric
                suggestions.extend(
                    self._generate_metric_suggestions(
                        metric_name,
                        metric_result,
                        intensity_score
                    )
                )

                # Estimate improvement potential
                expected_improvements[metric_name] = {
                    "current_score": metric_result.score,
                    "target_score": max(0.0, metric_result.score - intensity_score * 0.4),
                    "potential_improvement": intensity_score * 0.4
                }

        # Process specific issues
        for issue in result.specific_issues:
            if issue.severity in ["high", "medium"] or intensity == "aggressive":
                suggestions.append({
                    "line": issue.line_number,
                    "type": issue.issue_type,
                    "current": issue.line_text[:100],
                    "suggestion": issue.suggestion,
                    "priority": issue.severity,
                    "rationale": issue.description
                })

        # Calculate expected overall improvement
        original_prob = result.overall_ai_probability
        expected_new_prob = max(
            0.0,
            original_prob - (sum(imp["potential_improvement"] for imp in expected_improvements.values()) / len(expected_improvements) if expected_improvements else 0)
        )

        return {
            "original_analysis": {
                "ai_probability": original_prob,
                "verdict": result.verdict.value,
                "confidence": result.confidence.value,
                "issues_detected": len(result.specific_issues)
            },
            "humanization_plan": {
                "intensity": intensity,
                "preserve_technical": preserve_technical,
                "estimated_effort": len(suggestions)
            },
            "suggested_changes": suggestions,
            "expected_improvements": expected_improvements,
            "expected_outcome": {
                "new_ai_probability": expected_new_prob,
                "improvement_percentage": (original_prob - expected_new_prob) * 100,
                "expected_verdict": self._predict_verdict(expected_new_prob)
            },
            "implementation_roadmap": self._generate_roadmap(suggestions, intensity)
        }

    def _generate_metric_suggestions(
        self,
        metric_name: str,
        metric_result: MetricResult,
        intensity: float
    ) -> List[Dict]:
        """Generate specific suggestions for a metric"""
        suggestions = []

        if metric_name == "perplexity" and metric_result.score > 0.5:
            suggestions.extend([
                {
                    "metric": "perplexity",
                    "tactic": "Add specific examples",
                    "description": "Include 2-3 concrete examples or case studies",
                    "effort": "medium"
                },
                {
                    "metric": "perplexity",
                    "tactic": "Include personal anecdotes",
                    "description": "Reference personal experience or unique perspective",
                    "effort": "low"
                },
                {
                    "metric": "perplexity",
                    "tactic": "Add unexpected insights",
                    "description": "Include counter-intuitive arguments or surprising angles",
                    "effort": "high"
                }
            ])

        elif metric_name == "burstiness" and metric_result.score < 0.5:
            suggestions.extend([
                {
                    "metric": "burstiness",
                    "tactic": "Vary sentence length",
                    "description": "Alternate between very short (3-5 word) and complex sentences",
                    "effort": "medium"
                },
                {
                    "metric": "burstiness",
                    "tactic": "Vary sentence starters",
                    "description": "Avoid starting with 'The', 'In', 'It' - use different patterns",
                    "effort": "low"
                },
                {
                    "metric": "burstiness",
                    "tactic": "Use fragment sentences",
                    "description": "Occasionally use sentence fragments for impact",
                    "effort": "low"
                }
            ])

        elif metric_name == "vocabulary" and metric_result.score < 0.5:
            suggestions.extend([
                {
                    "metric": "vocabulary",
                    "tactic": "Use synonyms",
                    "description": "Replace repeated words with varied alternatives",
                    "effort": "medium"
                },
                {
                    "metric": "vocabulary",
                    "tactic": "Add sophisticated terms",
                    "description": "Include less common but appropriate terminology",
                    "effort": "low"
                },
                {
                    "metric": "vocabulary",
                    "tactic": "Use precise language",
                    "description": "Replace vague terms with specific, concrete vocabulary",
                    "effort": "medium"
                }
            ])

        elif metric_name == "transitions" and metric_result.score > 0.5:
            suggestions.extend([
                {
                    "metric": "transitions",
                    "tactic": "Remove formulaic transitions",
                    "description": "Delete 'Furthermore', 'Additionally', 'Moreover' where unnecessary",
                    "effort": "low"
                },
                {
                    "metric": "transitions",
                    "tactic": "Use structural transitions",
                    "description": "Let paragraph breaks and context provide continuity",
                    "effort": "low"
                },
                {
                    "metric": "transitions",
                    "tactic": "Use varied connectors",
                    "description": "Replace repeated transitions with questions or statements",
                    "effort": "medium"
                }
            ])

        elif metric_name == "repetition" and metric_result.score > 0.5:
            suggestions.extend([
                {
                    "metric": "repetition",
                    "tactic": "Refactor repeated phrases",
                    "description": "Paraphrase 3+ word phrases that appear multiple times",
                    "effort": "medium"
                },
                {
                    "metric": "repetition",
                    "tactic": "Use pronouns",
                    "description": "Replace repeated nouns with pronouns (this, that, it)",
                    "effort": "low"
                },
                {
                    "metric": "repetition",
                    "tactic": "Restructure sentences",
                    "description": "Vary word order to avoid repetitive sequences",
                    "effort": "medium"
                }
            ])

        elif metric_name == "syntax" and metric_result.score < 0.5:
            suggestions.extend([
                {
                    "metric": "syntax",
                    "tactic": "Mix active/passive voice",
                    "description": "Naturally vary between active and passive constructions",
                    "effort": "medium"
                },
                {
                    "metric": "syntax",
                    "tactic": "Vary clause positions",
                    "description": "Put main clause first in some sentences, subordinate first in others",
                    "effort": "medium"
                },
                {
                    "metric": "syntax",
                    "tactic": "Diversify sentence openers",
                    "description": "Use questions, lists, emphasis structures beyond SVO patterns",
                    "effort": "low"
                }
            ])

        return suggestions

    def _generate_roadmap(self, suggestions: List[Dict], intensity: str) -> List[str]:
        """Generate implementation roadmap based on intensity"""
        roadmap = []

        # Group by effort
        low_effort = [s for s in suggestions if s.get("effort") == "low"]
        medium_effort = [s for s in suggestions if s.get("effort") == "medium"]
        high_effort = [s for s in suggestions if s.get("effort") == "high"]

        if intensity in ["moderate", "aggressive"]:
            roadmap.append("PHASE 1 (Quick Wins - Low Effort):")
            for item in low_effort[:3]:
                desc = item.get("description", item.get("tactic", ""))
                roadmap.append(f"  • {desc}")

        if intensity in ["moderate", "aggressive"]:
            roadmap.append("\nPHASE 2 (Medium Effort - Significant Impact):")
            for item in medium_effort[:3]:
                desc = item.get("description", item.get("tactic", ""))
                roadmap.append(f"  • {desc}")

        if intensity == "aggressive":
            roadmap.append("\nPHASE 3 (High Effort - Maximum Transformation):")
            for item in high_effort[:2]:
                desc = item.get("description", item.get("tactic", ""))
                roadmap.append(f"  • {desc}")

        return roadmap

    def _predict_verdict(self, probability: float) -> str:
        """Predict verdict from probability"""
        if probability > 0.65:
            return "AI"
        elif probability < 0.35:
            return "HUMAN"
        else:
            return "MIXED"


class BatchProcessor:
    """Processes multiple files and generates aggregated reports"""

    def __init__(self, analyzer: TextAnalyzer):
        self.analyzer = analyzer

    def process_directory(
        self,
        directory: str,
        pattern: str = "*.txt",
        threshold: float = 0.5
    ) -> Dict:
        """
        Process all files in directory matching pattern

        Args:
            directory: Path to directory
            pattern: File glob pattern (default: *.txt)
            threshold: Flag files with AI probability above this threshold

        Returns:
            Dict with aggregated results and flagged files
        """
        dir_path = Path(directory)
        results = {
            "directory": str(dir_path),
            "scan_timestamp": datetime.now().isoformat(),
            "files_analyzed": 0,
            "files_flagged": 0,
            "average_ai_probability": 0.0,
            "threshold": threshold,
            "files": []
        }

        if not dir_path.exists():
            results["error"] = f"Directory not found: {directory}"
            return results

        files = list(dir_path.glob(pattern))
        if not files:
            results["error"] = f"No files matching pattern '{pattern}' in {directory}"
            return results

        probabilities = []

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                if len(text.strip()) < 50:
                    continue  # Skip very short files

                result = self.analyzer.analyze(text)
                probabilities.append(result.overall_ai_probability)

                file_result = {
                    "filename": file_path.name,
                    "path": str(file_path),
                    "ai_probability": result.overall_ai_probability,
                    "verdict": result.verdict.value,
                    "confidence": result.confidence.value,
                    "word_count": result.word_count,
                    "issues_detected": len(result.specific_issues),
                    "file_size_bytes": file_path.stat().st_size
                }

                if result.overall_ai_probability >= threshold:
                    results["files_flagged"] += 1
                    file_result["flagged"] = True
                    file_result["remediation_priority"] = result.remediation_priority[:3]

                results["files"].append(file_result)
                results["files_analyzed"] += 1

            except Exception as e:
                results["files"].append({
                    "filename": file_path.name,
                    "error": str(e)
                })

        # Calculate statistics
        if probabilities:
            results["average_ai_probability"] = sum(probabilities) / len(probabilities)
            results["min_ai_probability"] = min(probabilities)
            results["max_ai_probability"] = max(probabilities)
            results["flagged_percentage"] = (
                results["files_flagged"] / results["files_analyzed"] * 100
                if results["files_analyzed"] > 0 else 0
            )

        # Sort by AI probability (highest first)
        results["files"] = sorted(
            results["files"],
            key=lambda x: x.get("ai_probability", 0),
            reverse=True
        )

        return results

    def format_batch_report(self, batch_results: Dict, verbose: bool = False) -> str:
        """Format batch processing results"""
        output = []
        output.append("\n" + "=" * 80)
        output.append("BATCH ANALYSIS REPORT")
        output.append("=" * 80 + "\n")

        output.append(f"Directory: {batch_results['directory']}")
        output.append(f"Scan Time: {batch_results['scan_timestamp']}")
        output.append("")

        if "error" in batch_results:
            output.append(f"ERROR: {batch_results['error']}")
            return "\n".join(output)

        output.append("SUMMARY:")
        output.append(f"  Files Analyzed: {batch_results['files_analyzed']}")
        output.append(f"  Files Flagged (AI-likely): {batch_results['files_flagged']}")
        if batch_results['files_analyzed'] > 0:
            output.append(f"  Flagged Percentage: {batch_results.get('flagged_percentage', 0):.1f}%")
        output.append(f"  Threshold: {batch_results['threshold']:.0%}")
        output.append("")

        if batch_results.get('files_analyzed', 0) > 0:
            output.append("STATISTICS:")
            output.append(f"  Average AI Probability: {batch_results['average_ai_probability']:.1%}")
            output.append(f"  Range: {batch_results.get('min_ai_probability', 0):.1%} - "
                        f"{batch_results.get('max_ai_probability', 0):.1%}")
            output.append("")

        # Show flagged files
        flagged_files = [f for f in batch_results['files'] if f.get('flagged')]
        if flagged_files:
            output.append("FLAGGED FILES (AI-likely):")
            output.append("-" * 80)
            for file_info in flagged_files[:20]:  # Top 20
                output.append(f"\n{file_info['filename']}")
                output.append(f"  AI Probability: {file_info['ai_probability']:.0%}")
                output.append(f"  Verdict: {file_info['verdict']}")
                output.append(f"  Issues: {file_info['issues_detected']}")
                if verbose and file_info.get('remediation_priority'):
                    output.append(f"  Top Priority: {file_info['remediation_priority'][0]}")

        # Show human-likely files summary
        human_files = [f for f in batch_results['files'] if not f.get('flagged') and 'error' not in f]
        if human_files:
            output.append(f"\nHUMAN-LIKELY FILES: {len(human_files)}")
            if verbose and human_files:
                output.append("-" * 80)
                for file_info in human_files[:5]:
                    output.append(f"{file_info['filename']}: {file_info['ai_probability']:.0%}")

        output.append("\n" + "=" * 80)
        return "\n".join(output)


class CLIApplication:
    """Main CLI application"""

    def __init__(self):
        self.analyzer = TextAnalyzer()
        self.humanizer = HumanizationEngine(self.analyzer)
        self.batch_processor = BatchProcessor(self.analyzer)

    def load_text(self, input_arg: str) -> str:
        """Load text from either direct input or file"""
        # Check if it's a file path
        if os.path.isfile(input_arg):
            with open(input_arg, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Treat as direct text input
            return input_arg

    def cmd_analyze(self, args) -> int:
        """Execute analyze command"""
        try:
            text = self.load_text(args.input)

            if len(text.strip()) < 20:
                print("Error: Input text too short (minimum 20 characters)", file=sys.stderr)
                return 1

            result = self.analyzer.analyze(text)

            # Apply threshold filtering
            if result.overall_ai_probability < args.threshold:
                if args.verbose:
                    print(f"Note: AI probability {result.overall_ai_probability:.0%} "
                          f"is below threshold {args.threshold:.0%}")
                    print("(Showing analysis anyway due to --verbose flag)\n")
                else:
                    print(f"Result below threshold ({result.overall_ai_probability:.0%} < {args.threshold:.0%}). "
                          "Use --verbose to see analysis.")
                    return 0

            # Output formatting
            if args.json:
                print(result.to_json())
            elif args.compact:
                print(OutputFormatter.format_compact(result))
            else:
                print(OutputFormatter.format_human_readable(result, verbose=args.verbose))

            return 0

        except Exception as e:
            print(f"Error during analysis: {e}", file=sys.stderr)
            return 1

    def cmd_humanize(self, args) -> int:
        """Execute humanize command"""
        try:
            text = self.load_text(args.input)

            if len(text.strip()) < 20:
                print("Error: Input text too short (minimum 20 characters)", file=sys.stderr)
                return 1

            result = self.humanizer.humanize(
                text,
                intensity=args.intensity,
                preserve_technical=args.preserve_technical
            )

            if args.json:
                print(json.dumps(result, indent=2))
            else:
                output = self._format_humanize_report(result, verbose=args.verbose)
                print(output)

            return 0

        except Exception as e:
            print(f"Error during humanization: {e}", file=sys.stderr)
            return 1

    def cmd_batch(self, args) -> int:
        """Execute batch command"""
        try:
            results = self.batch_processor.process_directory(
                args.directory,
                pattern=args.pattern,
                threshold=args.threshold
            )

            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"Batch report written to: {output_path.absolute()}")

            if not args.json:
                report = self.batch_processor.format_batch_report(results, verbose=args.verbose)
                print(report)
            else:
                print(json.dumps(results, indent=2))

            return 0

        except Exception as e:
            print(f"Error during batch processing: {e}", file=sys.stderr)
            return 1

    def _format_humanize_report(self, result: Dict, verbose: bool = False) -> str:
        """Format humanization report"""
        output = []
        output.append("\n" + "=" * 80)
        output.append("HUMANIZATION ANALYSIS")
        output.append("=" * 80 + "\n")

        # Original state
        orig = result["original_analysis"]
        output.append("ORIGINAL TEXT ANALYSIS:")
        output.append(f"  AI Probability: {orig['ai_probability']:.0%}")
        output.append(f"  Verdict: {orig['verdict']}")
        output.append(f"  Confidence: {orig['confidence']}")
        output.append(f"  Issues Detected: {orig['issues_detected']}")
        output.append("")

        # Expected outcome
        expected = result["expected_outcome"]
        output.append("EXPECTED OUTCOME (after humanization):")
        output.append(f"  New AI Probability: {expected['new_ai_probability']:.0%}")
        output.append(f"  Improvement: {expected['improvement_percentage']:.1f} percentage points")
        output.append(f"  Expected Verdict: {expected['expected_verdict']}")
        output.append("")

        # Plan
        plan = result["humanization_plan"]
        output.append("HUMANIZATION PLAN:")
        output.append(f"  Intensity: {plan['intensity'].upper()}")
        output.append(f"  Suggested Changes: {plan['estimated_effort']}")
        output.append("")

        # Detailed suggestions
        if result["suggested_changes"]:
            output.append("DETAILED SUGGESTIONS:")
            output.append("-" * 80)

            # Group by type
            by_type = {}
            for suggestion in result["suggested_changes"]:
                type_key = suggestion.get("metric") or suggestion.get("type", "general")
                if type_key not in by_type:
                    by_type[type_key] = []
                by_type[type_key].append(suggestion)

            for sug_type, suggestions in by_type.items():
                output.append(f"\n{sug_type.upper()}:")
                for i, sug in enumerate(suggestions, 1):
                    if "tactic" in sug:
                        output.append(f"  {i}. {sug['tactic']}")
                        output.append(f"     {sug['description']}")
                        if verbose:
                            output.append(f"     Effort: {sug.get('effort', 'unknown')}")
                    else:
                        output.append(f"  {i}. Line {sug.get('line', '?')}: {sug.get('type', 'issue')}")
                        output.append(f"     {sug.get('suggestion', 'No suggestion provided')}")

        # Implementation roadmap
        if result["implementation_roadmap"]:
            output.append("\n" + "-" * 80)
            output.append("\nIMPLEMENTATION ROADMAP:")
            for step in result["implementation_roadmap"]:
                output.append(step)

        output.append("\n" + "=" * 80)
        return "\n".join(output)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="IF.detector: AI text detection and humanization CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            EXAMPLES:
              # Analyze a single text
              python if_detector_cli.py analyze "Your text here" --verbose

              # Analyze a file
              python if_detector_cli.py analyze document.txt --json

              # Get humanization suggestions
              python if_detector_cli.py humanize article.txt --intensity aggressive

              # Batch process directory
              python if_detector_cli.py batch /path/to/docs --output report.json --threshold 0.6
        """)
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # ANALYZE command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze text for AI probability and provide detailed metrics'
    )
    analyze_parser.add_argument(
        'input',
        help='Text to analyze or path to file'
    )
    analyze_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed metric data and analysis'
    )
    analyze_parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON (parseable format)'
    )
    analyze_parser.add_argument(
        '--compact',
        action='store_true',
        help='Output as single-line compact summary'
    )
    analyze_parser.add_argument(
        '--threshold',
        type=float,
        default=0.0,
        help='Only process if AI probability exceeds this threshold (0.0-1.0, default: 0.0)'
    )
    analyze_parser.set_defaults(func=CLIApplication().cmd_analyze)

    # HUMANIZE command
    humanize_parser = subparsers.add_parser(
        'humanize',
        help='Generate humanization suggestions to reduce AI probability'
    )
    humanize_parser.add_argument(
        'input',
        help='Text to humanize or path to file'
    )
    humanize_parser.add_argument(
        '--intensity',
        choices=['subtle', 'moderate', 'aggressive'],
        default='moderate',
        help='Level of suggested changes (default: moderate)'
    )
    humanize_parser.add_argument(
        '--preserve-technical',
        action='store_true',
        help="Don't suggest changes to domain-specific terminology"
    )
    humanize_parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    humanize_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show additional implementation details'
    )
    humanize_parser.set_defaults(func=CLIApplication().cmd_humanize)

    # BATCH command
    batch_parser = subparsers.add_parser(
        'batch',
        help='Process multiple files and generate report'
    )
    batch_parser.add_argument(
        'directory',
        help='Directory containing files to analyze'
    )
    batch_parser.add_argument(
        '--pattern', '-p',
        default='*.txt',
        help='File glob pattern to match (default: *.txt)'
    )
    batch_parser.add_argument(
        '--output', '-o',
        help='Write JSON report to this file'
    )
    batch_parser.add_argument(
        '--threshold',
        type=float,
        default=0.5,
        help='Flag files with AI probability above this threshold (default: 0.5)'
    )
    batch_parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON to stdout'
    )
    batch_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed information for each file'
    )
    batch_parser.set_defaults(func=CLIApplication().cmd_batch)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
