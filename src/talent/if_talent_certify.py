"""
IF.talent Certify - Guardian Approval Component

Submits capabilities to Guardian Panel for certification before deployment.

Integration with infrafabric.guardians.GuardianPanel

Author: IF.talent Team (Agent 6)
Date: 2025-11-11
Citation: if://component/talent/certify-v1
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

# Import Guardian Panel (if available)
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "infrafabric"))
    from guardians import GuardianPanel, Guardian
    GUARDIANS_AVAILABLE = True
except ImportError:
    GUARDIANS_AVAILABLE = False
    print("⚠️  Guardian Panel not available, using mock certification")


@dataclass
class CertificationResult:
    """Result of Guardian certification"""
    capability_id: str
    decision: str  # "approve" | "reject" | "request_more_testing"
    confidence: float  # 0-100
    guardian_votes: dict
    reasoning: str
    certified_at: str
    approved: bool


class IFTalentCertify:
    """
    IF.talent Certify - Guardian approval workflow

    Submits capability + sandbox results to Guardian Panel for deliberation.
    """

    def __init__(self):
        """Initialize certifier"""
        self.certification_history = []

    def certify_capability(
        self,
        capability: dict,
        sandbox_results: dict,
        bloom_analysis: dict = None
    ) -> CertificationResult:
        """
        Submit capability for Guardian certification

        Args:
            capability: Capability data (from Scout)
            sandbox_results: Sandbox test results
            bloom_analysis: Bloom pattern analysis (optional)

        Returns:
            Certification result with Guardian decision
        """
        print(f"✅ Certifying {capability['name']}...")

        if GUARDIANS_AVAILABLE:
            result = self._certify_with_guardians(capability, sandbox_results, bloom_analysis)
        else:
            result = self._mock_certification(capability, sandbox_results, bloom_analysis)

        self.certification_history.append(result)
        return result

    def _certify_with_guardians(self, capability, sandbox_results, bloom_analysis):
        """Real Guardian Panel certification"""
        panel = GuardianPanel()

        # Add standard Guardians
        panel.add_guardian(Guardian("Security", weight=1.5))
        panel.add_guardian(Guardian("Ethics", weight=1.2))
        panel.add_guardian(Guardian("Performance", weight=1.0))
        panel.add_guardian(Guardian("Cost", weight=1.3))

        # Prepare proposal
        proposal = {
            'capability': capability,
            'sandbox_results': sandbox_results,
            'bloom_analysis': bloom_analysis,
            'proposed_use': f"IF.swarm router for difficulty 1-{self._recommend_max_difficulty(sandbox_results)}"
        }

        # Guardian deliberation
        result = panel.debate(proposal)

        return CertificationResult(
            capability_id=capability['capability_id'],
            decision=result['decision'],
            confidence=result['confidence'],
            guardian_votes=result.get('votes', {}),
            reasoning=result['reasoning'],
            certified_at=datetime.utcnow().isoformat() + 'Z',
            approved=(result['decision'] == 'approve')
        )

    def _mock_certification(self, capability, sandbox_results, bloom_analysis):
        """Mock certification (when Guardian Panel unavailable)"""
        # Simulate Guardian votes based on sandbox results
        accuracy = sandbox_results.get('avg_accuracy', 0)
        success_rate = sandbox_results.get('success_rate', 0)

        # Security Guardian
        security_confidence = 95 if success_rate > 80 else 75
        security_vote = "approve" if security_confidence > 85 else "request_more_testing"

        # Ethics Guardian
        ethics_confidence = 92 if accuracy > 70 else 70
        ethics_vote = "approve" if ethics_confidence > 85 else "request_more_testing"

        # Performance Guardian
        perf_confidence = 98 if sandbox_results.get('avg_latency_ms', 5000) < 3000 else 70
        perf_vote = "approve" if perf_confidence > 85 else "request_more_testing"

        # Cost Guardian
        cost_confidence = 100  # Always approve (cost data available)
        cost_vote = "approve"

        # Weighted average
        total_confidence = (
            security_confidence * 1.5 +
            ethics_confidence * 1.2 +
            perf_confidence * 1.0 +
            cost_confidence * 1.3
        ) / (1.5 + 1.2 + 1.0 + 1.3)

        all_approve = all(v == "approve" for v in [security_vote, ethics_vote, perf_vote, cost_vote])
        decision = "approve" if all_approve else "request_more_testing"

        guardian_votes = {
            'Security': {'vote': security_vote, 'confidence': security_confidence},
            'Ethics': {'vote': ethics_vote, 'confidence': ethics_confidence},
            'Performance': {'vote': perf_vote, 'confidence': perf_confidence},
            'Cost': {'vote': cost_vote, 'confidence': cost_confidence}
        }

        reasoning = f"Mock certification: {decision} with {total_confidence:.1f}% confidence. "
        reasoning += f"Sandbox: {success_rate:.1f}% success, {accuracy:.1f}% accuracy."

        return CertificationResult(
            capability_id=capability['capability_id'],
            decision=decision,
            confidence=total_confidence,
            guardian_votes=guardian_votes,
            reasoning=reasoning,
            certified_at=datetime.utcnow().isoformat() + 'Z',
            approved=(decision == 'approve')
        )

    def _recommend_max_difficulty(self, sandbox_results):
        """Recommend max difficulty based on sandbox results"""
        accuracy = sandbox_results.get('avg_accuracy', 0)
        if accuracy > 85:
            return 4
        elif accuracy > 75:
            return 3
        elif accuracy > 65:
            return 2
        else:
            return 1

    def save_certification(self, certification: CertificationResult, filepath: str):
        """Save certification result to file"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(asdict(certification), f, indent=2)
        print(f"💾 Certification saved to {filepath}")


# CLI usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IF.talent Certify - Guardian approval")
    parser.add_argument("--capability", required=True, help="Capability JSON file")
    parser.add_argument("--sandbox", required=True, help="Sandbox results JSON file")
    parser.add_argument("--bloom", help="Bloom analysis JSON file (optional)")
    parser.add_argument("--save", help="Save certification result to file")

    args = parser.parse_args()

    # Load inputs
    with open(args.capability) as f:
        capability = json.load(f)

    with open(args.sandbox) as f:
        sandbox_results = json.load(f)

    bloom_analysis = None
    if args.bloom:
        with open(args.bloom) as f:
            bloom_analysis = json.load(f)

    # Certify
    certifier = IFTalentCertify()
    result = certifier.certify_capability(capability, sandbox_results, bloom_analysis)

    print(f"\n📋 Certification Result:")
    print(f"  Decision: {result.decision}")
    print(f"  Confidence: {result.confidence:.1f}%")
    print(f"  Approved: {'✅ Yes' if result.approved else '❌ No'}")
    print(f"  Reasoning: {result.reasoning}")

    if args.save:
        certifier.save_certification(result, args.save)
