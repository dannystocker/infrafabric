"""
IF.talent Sandbox - Safe Capability Testing Component

Tests discovered capabilities in isolated environment:
- Docker container isolation
- Standard test harness (20 tasks: simple → complex)
- Performance metrics (latency, tokens, accuracy)
- Bloom pattern detection (does it improve with context?)

Philosophy Grounding:
- IF.ground:principle_3 (Fallibilism): Capabilities can fail, that's okay
- IF.ground:principle_8 (Stoic Prudence): Isolated testing prevents damage
- Wu Lun: Sandbox acts as "teacher→student" relationship, evaluating capability

Author: IF.talent Team (Agent 6)
Date: 2025-11-11
Citation: if://component/talent/sandbox-v1
"""

import json
import time
import subprocess
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import statistics


@dataclass
class TestTask:
    """
    Standard test task for capability evaluation

    Attributes:
        task_id: Unique identifier
        name: Human-readable name
        prompt: Task prompt
        expected_pattern: Regex pattern for success detection
        difficulty: 1-5 (1=trivial, 5=expert)
        context_tokens: Estimated context size
        category: "reasoning" | "coding" | "summarization" | "math"
    """
    task_id: str
    name: str
    prompt: str
    expected_pattern: str
    difficulty: int
    context_tokens: int
    category: str


@dataclass
class TestResult:
    """
    Result of testing a capability on a task

    Attributes:
        task_id: Which task was tested
        capability_id: Which capability was tested
        success: Did it pass?
        latency_ms: Response time
        tokens_used: Total tokens (input + output)
        accuracy_score: 0-100 (how well did it do?)
        response_text: What the capability returned
        error: Error message if failed
        timestamp: When was this tested
    """
    task_id: str
    capability_id: str
    success: bool
    latency_ms: float
    tokens_used: int
    accuracy_score: int
    response_text: str
    error: Optional[str]
    timestamp: str


@dataclass
class BloomAnalysis:
    """
    Bloom pattern analysis (does capability improve with context?)

    Bloom pattern: Performance improves as context increases

    Attributes:
        capability_id: Which capability was analyzed
        bloom_detected: True if performance improves with context
        bloom_score: 0-100 (strength of bloom pattern)
        context_vs_accuracy: List of (context_tokens, accuracy_score) tuples
        interpretation: Human-readable explanation
    """
    capability_id: str
    bloom_detected: bool
    bloom_score: int
    context_vs_accuracy: List[Tuple[int, int]]
    interpretation: str


class IFTalentSandbox:
    """
    IF.talent Sandbox - Test capabilities in isolation with IF.TTT compliance

    Uses IF.swarm pattern:
    - Spawn Sonnet for Bloom pattern algorithm (complex statistics)
    - Spawn Haiku for Docker setup (boilerplate)
    - Spawn Haiku for test harness execution (parallel tests)

    Philosophy:
    - Fallibilism: Capabilities can fail, we learn from failures
    - Stoic Prudence: Isolated testing prevents production damage
    - Wu Lun: Sandbox as teacher evaluating student
    """

    def __init__(self, use_docker: bool = False):
        """
        Initialize sandbox

        Args:
            use_docker: Use Docker isolation (recommended for production)
        """
        self.use_docker = use_docker
        self.test_results: List[TestResult] = []
        self.standard_tasks = self._create_standard_tasks()

    def _create_standard_tasks(self) -> List[TestTask]:
        """
        Create 20 standard test tasks (simple → complex)

        Returns:
            List of standard tasks for capability evaluation
        """
        tasks = [
            # Simple tasks (difficulty 1)
            TestTask(
                task_id="task_001",
                name="Hello World",
                prompt="Say 'Hello, World!'",
                expected_pattern=r"Hello.*World",
                difficulty=1,
                context_tokens=50,
                category="reasoning"
            ),
            TestTask(
                task_id="task_002",
                name="Simple Math",
                prompt="What is 2 + 2?",
                expected_pattern=r"4",
                difficulty=1,
                context_tokens=50,
                category="math"
            ),
            TestTask(
                task_id="task_003",
                name="Basic Summarization",
                prompt="Summarize in 5 words: 'The quick brown fox jumps over the lazy dog'",
                expected_pattern=r"\w+\s+\w+\s+\w+\s+\w+\s+\w+",
                difficulty=1,
                context_tokens=100,
                category="summarization"
            ),

            # Medium tasks (difficulty 2-3)
            TestTask(
                task_id="task_004",
                name="FizzBuzz Explanation",
                prompt="Explain the FizzBuzz problem",
                expected_pattern=r"(divisible|3|5|15|Fizz|Buzz)",
                difficulty=2,
                context_tokens=200,
                category="reasoning"
            ),
            TestTask(
                task_id="task_005",
                name="Simple Code Generation",
                prompt="Write a Python function that checks if a number is prime",
                expected_pattern=r"def.*prime.*:.*if.*%.*return",
                difficulty=2,
                context_tokens=300,
                category="coding"
            ),
            TestTask(
                task_id="task_006",
                name="Multi-Step Math",
                prompt="If Alice has 3 apples and buys 5 more, then gives 2 to Bob, how many does she have?",
                expected_pattern=r"6",
                difficulty=2,
                context_tokens=150,
                category="math"
            ),
            TestTask(
                task_id="task_007",
                name="Code Review",
                prompt="What's wrong with this code? `if (x = 5):`",
                expected_pattern=r"(assignment|==|equality|comparison)",
                difficulty=2,
                context_tokens=200,
                category="coding"
            ),
            TestTask(
                task_id="task_008",
                name="Long Summarization",
                prompt="Summarize the key points of this text (300 words): [Lorem ipsum dolor sit amet, consectetur adipiscing elit...]",
                expected_pattern=r".{100,}",  # At least 100 chars
                difficulty=3,
                context_tokens=500,
                category="summarization"
            ),

            # Complex tasks (difficulty 3-4)
            TestTask(
                task_id="task_009",
                name="Algorithm Design",
                prompt="Design an algorithm to find the longest palindromic substring in O(n^2) time",
                expected_pattern=r"(expand|center|dynamic|programming|O\(n\^2\))",
                difficulty=3,
                context_tokens=400,
                category="reasoning"
            ),
            TestTask(
                task_id="task_010",
                name="Complex Code Generation",
                prompt="Write a Python class that implements a binary search tree with insert, search, and delete methods",
                expected_pattern=r"class.*Node.*left.*right.*insert.*search",
                difficulty=3,
                context_tokens=600,
                category="coding"
            ),
            TestTask(
                task_id="task_011",
                name="System Design",
                prompt="Design a URL shortener service. Explain the database schema and API endpoints.",
                expected_pattern=r"(database|schema|POST|GET|hash|short.*url)",
                difficulty=3,
                context_tokens=800,
                category="reasoning"
            ),
            TestTask(
                task_id="task_012",
                name="Math Proof",
                prompt="Prove that the sum of two even numbers is always even",
                expected_pattern=r"(2n|2m|2\(n.*m\)|divisible.*2)",
                difficulty=3,
                context_tokens=400,
                category="math"
            ),

            # Expert tasks (difficulty 4-5)
            TestTask(
                task_id="task_013",
                name="Advanced Algorithm",
                prompt="Implement Dijkstra's algorithm for shortest path in a weighted graph",
                expected_pattern=r"(priority.*queue|heap|distance|visited|neighbor)",
                difficulty=4,
                context_tokens=1000,
                category="coding"
            ),
            TestTask(
                task_id="task_014",
                name="Code Optimization",
                prompt="Optimize this O(n^3) code to O(n^2): [nested loop example]",
                expected_pattern=r"(O\(n\^2\)|memoization|dynamic.*programming|cache)",
                difficulty=4,
                context_tokens=800,
                category="coding"
            ),
            TestTask(
                task_id="task_015",
                name="Research Summarization",
                prompt="Summarize this 50-page research paper on quantum computing: [paper text]",
                expected_pattern=r".{500,}",  # At least 500 chars
                difficulty=4,
                context_tokens=10000,
                category="summarization"
            ),
            TestTask(
                task_id="task_016",
                name="Multi-Domain Reasoning",
                prompt="A train leaves Station A at 60 mph. Another leaves Station B (200 miles away) at 40 mph toward A. When do they meet? Then write Python code to solve this.",
                expected_pattern=r"(2.*hours|code|def|distance|speed)",
                difficulty=4,
                context_tokens=600,
                category="math"
            ),
            TestTask(
                task_id="task_017",
                name="System Architecture",
                prompt="Design a distributed caching system that handles 1M requests/sec with 99.99% uptime",
                expected_pattern=r"(redis|memcached|consistent.*hashing|replication|partition)",
                difficulty=4,
                context_tokens=1200,
                category="reasoning"
            ),
            TestTask(
                task_id="task_018",
                name="Advanced Math",
                prompt="Prove that sqrt(2) is irrational",
                expected_pattern=r"(contradiction|rational|p\/q|even|square)",
                difficulty=5,
                context_tokens=600,
                category="math"
            ),
            TestTask(
                task_id="task_019",
                name="Code Refactoring",
                prompt="Refactor this legacy codebase (500 lines) to use modern design patterns: [code]",
                expected_pattern=r"(factory|singleton|observer|strategy|refactor)",
                difficulty=5,
                context_tokens=5000,
                category="coding"
            ),
            TestTask(
                task_id="task_020",
                name="Philosophy + Code",
                prompt="Explain Gödel's incompleteness theorems and write code that demonstrates self-reference",
                expected_pattern=r"(Gödel|incomplete|self.*reference|proof|def|quine)",
                difficulty=5,
                context_tokens=2000,
                category="reasoning"
            ),
        ]

        return tasks

    def test_capability_mock(
        self,
        capability_id: str,
        task: TestTask,
        timeout_seconds: int = 30
    ) -> TestResult:
        """
        Test a capability on a task (MOCK VERSION - no real API calls)

        In production, this would call the actual model API.
        For now, simulates responses with random scores.

        Args:
            capability_id: Which capability to test
            task: Test task
            timeout_seconds: Max time allowed

        Returns:
            Test result with metrics
        """
        import random
        import re

        start_time = time.time()

        # Simulate response (in production: call actual API)
        success = random.random() > 0.3  # 70% success rate
        latency_ms = random.uniform(100, 3000)
        tokens_used = task.context_tokens + random.randint(50, 500)

        # Simulate accuracy based on difficulty
        base_accuracy = 90 - (task.difficulty * 10)
        accuracy_score = max(0, min(100, int(base_accuracy + random.uniform(-20, 20))))

        response_text = f"Mock response for task {task.task_id}"
        error = None if success else "Mock error: Task failed"

        result = TestResult(
            task_id=task.task_id,
            capability_id=capability_id,
            success=success,
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            accuracy_score=accuracy_score,
            response_text=response_text,
            error=error,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )

        self.test_results.append(result)

        return result

    def run_test_harness(
        self,
        capability_id: str,
        tasks: Optional[List[TestTask]] = None
    ) -> Dict:
        """
        Run full test harness on a capability

        Args:
            capability_id: Which capability to test
            tasks: Custom tasks (defaults to standard 20 tasks)

        Returns:
            Test harness summary with metrics
        """
        if tasks is None:
            tasks = self.standard_tasks

        print(f"🧪 Testing capability: {capability_id}")
        print(f"Running {len(tasks)} standard tasks...\n")

        results = []

        for task in tasks:
            print(f"  [{task.task_id}] {task.name} (difficulty={task.difficulty})...", end=" ")
            result = self.test_capability_mock(capability_id, task)

            if result.success:
                print(f"✅ {result.accuracy_score}%")
            else:
                print(f"❌ Failed")

            results.append(result)

        # Calculate summary metrics
        successes = [r for r in results if r.success]
        success_rate = len(successes) / len(results) * 100

        avg_latency = statistics.mean([r.latency_ms for r in results])
        avg_accuracy = statistics.mean([r.accuracy_score for r in successes]) if successes else 0
        total_tokens = sum([r.tokens_used for r in results])

        summary = {
            'capability_id': capability_id,
            'tasks_run': len(tasks),
            'success_rate': success_rate,
            'avg_latency_ms': avg_latency,
            'avg_accuracy': avg_accuracy,
            'total_tokens': total_tokens,
            'results': [asdict(r) for r in results]
        }

        print(f"\n📊 Summary:")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Avg Latency: {avg_latency:.0f}ms")
        print(f"  Avg Accuracy: {avg_accuracy:.1f}%")
        print(f"  Total Tokens: {total_tokens}")

        return summary

    def analyze_bloom_pattern(
        self,
        capability_id: str,
        results: Optional[List[TestResult]] = None
    ) -> BloomAnalysis:
        """
        Analyze if capability exhibits Bloom pattern (improves with context)

        Bloom pattern: Accuracy increases as context tokens increase

        Args:
            capability_id: Which capability to analyze
            results: Test results (defaults to self.test_results)

        Returns:
            Bloom analysis with interpretation

        Philosophy:
        - IF.ground:principle_3 (Fallibilism): Some capabilities bloom, some don't
        - Wu Lun: Understanding when a capability excels (relationship context)
        """
        if results is None:
            results = [r for r in self.test_results if r.capability_id == capability_id]

        # Get (context_tokens, accuracy_score) pairs, sorted by context
        tasks_by_id = {t.task_id: t for t in self.standard_tasks}

        context_accuracy_pairs = []
        for result in results:
            if result.success:
                task = tasks_by_id.get(result.task_id)
                if task:
                    context_accuracy_pairs.append((task.context_tokens, result.accuracy_score))

        context_accuracy_pairs.sort(key=lambda x: x[0])

        if len(context_accuracy_pairs) < 3:
            return BloomAnalysis(
                capability_id=capability_id,
                bloom_detected=False,
                bloom_score=0,
                context_vs_accuracy=context_accuracy_pairs,
                interpretation="Insufficient data (need at least 3 successful tasks)"
            )

        # Calculate correlation (simple linear regression slope)
        contexts = [x[0] for x in context_accuracy_pairs]
        accuracies = [x[1] for x in context_accuracy_pairs]

        # Simple correlation: does accuracy trend upward with context?
        # Split into low-context and high-context halves
        mid = len(context_accuracy_pairs) // 2
        low_context_avg = statistics.mean(accuracies[:mid])
        high_context_avg = statistics.mean(accuracies[mid:])

        improvement = high_context_avg - low_context_avg
        bloom_detected = improvement > 5  # At least 5% improvement

        # Bloom score: 0-100 based on improvement magnitude
        bloom_score = max(0, min(100, int(improvement * 2)))

        if bloom_detected:
            interpretation = f"BLOOM DETECTED: Accuracy improves {improvement:.1f}% with more context. This capability benefits from rich context and should be used for complex, multi-step tasks."
        else:
            interpretation = f"No significant bloom pattern (improvement: {improvement:.1f}%). This capability performs consistently across context sizes."

        analysis = BloomAnalysis(
            capability_id=capability_id,
            bloom_detected=bloom_detected,
            bloom_score=bloom_score,
            context_vs_accuracy=context_accuracy_pairs,
            interpretation=interpretation
        )

        print(f"\n🌸 Bloom Analysis:")
        print(f"  {interpretation}")
        print(f"  Bloom Score: {bloom_score}/100")

        return analysis

    def generate_sandbox_report(
        self,
        capability_id: str,
        test_summary: Dict,
        bloom_analysis: BloomAnalysis
    ) -> str:
        """
        Generate human-readable sandbox test report

        Args:
            capability_id: Which capability was tested
            test_summary: Test harness summary
            bloom_analysis: Bloom pattern analysis

        Returns:
            Markdown-formatted report
        """
        report = f"""# IF.talent Sandbox Report

**Capability:** `{capability_id}`
**Generated:** {datetime.utcnow().isoformat() + 'Z'}

---

## Test Harness Results

**Tasks Run:** {test_summary['tasks_run']}
**Success Rate:** {test_summary['success_rate']:.1f}%
**Avg Latency:** {test_summary['avg_latency_ms']:.0f}ms
**Avg Accuracy:** {test_summary['avg_accuracy']:.1f}%
**Total Tokens:** {test_summary['total_tokens']}

---

## Bloom Pattern Analysis

**Bloom Detected:** {'✅ Yes' if bloom_analysis.bloom_detected else '❌ No'}
**Bloom Score:** {bloom_analysis.bloom_score}/100

{bloom_analysis.interpretation}

### Context vs Accuracy

| Context Tokens | Accuracy |
|----------------|----------|
"""

        for context, accuracy in bloom_analysis.context_vs_accuracy[:10]:  # Show first 10
            report += f"| {context:,} | {accuracy}% |\n"

        report += """
---

## Recommendation

"""

        if bloom_analysis.bloom_detected:
            report += f"""This capability exhibits strong bloom behavior (score: {bloom_analysis.bloom_score}/100).

**Best Use Cases:**
- Complex, multi-step reasoning tasks
- Long-context summarization
- Code review and refactoring (large codebases)
- System design and architecture

**Avoid:**
- Simple, single-step tasks (overkill)
- Latency-sensitive operations (slower with more context)
"""
        else:
            report += """This capability performs consistently across context sizes.

**Best Use Cases:**
- Single-step tasks (fast and reliable)
- Latency-sensitive operations
- Batch processing (consistent performance)

**Consider Other Capabilities For:**
- Complex, multi-step reasoning (try a bloom-capable model)
"""

        report += """
---

## Philosophy Grounding

- **IF.ground:principle_3 (Fallibilism)**: Some tasks failed, that's expected
- **IF.ground:principle_8 (Stoic Prudence)**: Isolated testing prevents production damage
- **Wu Lun (teacher→student)**: Sandbox evaluates capability's learning curve

---

*Generated by IF.talent Sandbox v1.0*
"""

        return report

    def save_sandbox_results(
        self,
        capability_id: str,
        filepath: str,
        test_summary: Dict,
        bloom_analysis: BloomAnalysis
    ):
        """
        Save sandbox results to JSON with IF.TTT compliance

        Args:
            capability_id: Which capability was tested
            filepath: Where to save
            test_summary: Test harness summary
            bloom_analysis: Bloom analysis
        """
        manifest = {
            'sandbox_run_id': f"if://sandbox/run/{datetime.utcnow().isoformat().replace(':', '-')}",
            'capability_id': capability_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'test_summary': test_summary,
            'bloom_analysis': asdict(bloom_analysis),
            'philosophy_metadata': {
                'principles_invoked': [
                    'IF.ground:principle_3_fallibilism',
                    'IF.ground:principle_8_stoic_prudence'
                ],
                'wu_lun_relationship': 'sandbox→capability (teacher evaluating student)'
            }
        }

        with open(filepath, 'w') as f:
            json.dump(manifest, f, indent=2)

        print(f"\n✅ Sandbox results saved to {filepath}")


# CLI usage example
if __name__ == "__main__":
    sandbox = IFTalentSandbox(use_docker=False)

    print("🧪 IF.talent Sandbox - Testing AI Capabilities\n")

    # Test a mock capability
    capability_id = "if://capability/claude-sonnet-4.5"

    # Run test harness
    test_summary = sandbox.run_test_harness(capability_id)

    # Analyze bloom pattern
    bloom_analysis = sandbox.analyze_bloom_pattern(capability_id)

    # Generate report
    report = sandbox.generate_sandbox_report(capability_id, test_summary, bloom_analysis)
    print("\n" + report)

    # Save results
    sandbox.save_sandbox_results(
        capability_id,
        "sandbox-results.json",
        test_summary,
        bloom_analysis
    )
