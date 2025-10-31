#!/usr/bin/env python3
"""
Self-Documenting Weighted Coordinator - InfraFabric Philosophy

This coordinator doesn't just track metrics - it DEMONSTRATES InfraFabric principles
through its documentation:

1. RECIPROCITY: Metrics earned through contribution, not mandated
2. EVOLUTIONARY PATIENCE: Track agent maturation over time (late bloomers)
3. GRACEFUL DEGRADATION: Document how system continues when agents fail
4. ENCOURAGEMENT ARCHITECTURE: Show how 0.0 weight enables exploration
5. PHILOSOPHY INTEGRATION: Each metric has a "why" (philosophy paragraph)

The documentation IS the validation.

Author: InfraFabric Research
Date: November 1, 2025
Philosophy: "Truth rarely performs well in its early iterations"
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class SelfDocumentingMetric:
    """
    A metric that documents its own meaning and contribution.

    Philosophy: "Every measurement is a story waiting to be told"
    """

    def __init__(self, name: str, value: any, philosophy: str,
                 contribution_weight: float, story: str):
        self.name = name
        self.value = value
        self.philosophy = philosophy  # Why this metric matters
        self.contribution_weight = contribution_weight  # How much it influenced decision
        self.story = story  # What this metric revealed
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'value': self.value,
            'philosophy': self.philosophy,
            'contribution_weight': self.contribution_weight,
            'story': self.story,
            'timestamp': self.timestamp
        }


class AgentLifecycle:
    """
    Tracks an agent's journey from "bad branch" to "late bloomer" (or continued failure).

    Philosophy: "Survival isn't strength — it's stubbornness with structure"
    """

    def __init__(self, agent_name: str, agent_tier: str):
        self.agent_name = agent_name
        self.agent_tier = agent_tier
        self.attempts = []
        self.maturation_trajectory = []  # Track performance over time
        self.first_success = None
        self.success_count = 0
        self.failure_count = 0
        self.weight_earned_total = 0.0
        self.philosophy = self._get_philosophy(agent_tier)

    def _get_philosophy(self, tier: str) -> str:
        philosophies = {
            'baseline': '"The reliable are not spectacular, but they show up"',
            'specialist': '"Excellence in one domain is silence in others"',
            'exploratory': '"Most treasure is found by those who keep searching after others quit"'
        }
        return philosophies.get(tier, '"Every agent teaches the system something"')

    def record_attempt(self, confidence: int, weight: float, contact_name: str):
        """Record an attempt and track maturation"""
        attempt = {
            'attempt_number': len(self.attempts) + 1,
            'confidence': confidence,
            'weight': weight,
            'contact': contact_name,
            'timestamp': datetime.now().isoformat(),
            'succeeded': weight > 0.0
        }

        self.attempts.append(attempt)
        self.maturation_trajectory.append(confidence)

        if weight > 0.0:
            self.success_count += 1
            self.weight_earned_total += weight
            if self.first_success is None:
                self.first_success = attempt['attempt_number']
        else:
            self.failure_count += 1

    def get_maturation_story(self) -> str:
        """
        Generate narrative about agent's journey.

        Philosophy: "Every failure teaches; every success validates"
        """
        if len(self.attempts) == 0:
            return f"{self.agent_name} has not yet been tested"

        total = len(self.attempts)
        rate = (self.success_count / total * 100) if total > 0 else 0

        # Check for late bloomer pattern
        if len(self.maturation_trajectory) >= 3:
            early_avg = sum(self.maturation_trajectory[:2]) / 2
            late_avg = sum(self.maturation_trajectory[-2:]) / 2
            improvement = late_avg - early_avg

            if improvement > 20:
                return (f"{self.agent_name} is a LATE BLOOMER: Started at {early_avg:.0f} "
                       f"confidence, improved to {late_avg:.0f} (+{improvement:.0f} points). "
                       f"Weighted coordination kept exploring until maturation revealed itself. "
                       f"Success rate: {rate:.1f}%.")

        if rate == 0 and self.agent_tier == 'exploratory':
            return (f"{self.agent_name} has explored {total} contacts with 0% success, "
                   f"but remains at 0.0 weight (no system penalty). "
                   f"Continues searching for breakthrough discovery. "
                   f"Expected success rate: ~20%. Patience rewarded when successful.")

        if rate == 100 and self.agent_tier == 'baseline':
            return (f"{self.agent_name} provides reliable floor: {total}/{total} success. "
                   f"Consistent contribution ensures system never fails completely. "
                   f"Total weight contributed: {self.weight_earned_total:.1f}.")

        if rate > 0 and self.agent_tier == 'specialist':
            return (f"{self.agent_name} found its domain: {self.success_count}/{total} success "
                   f"({rate:.1f}%). Specialist agents are bimodal - silence when irrelevant, "
                   f"amplified when successful. Total weight earned: {self.weight_earned_total:.1f}.")

        return (f"{self.agent_name} [{self.agent_tier}]: {self.success_count}/{total} success "
               f"({rate:.1f}%). Weight earned: {self.weight_earned_total:.1f}. "
               f"Philosophy: {self.philosophy}")

    def to_dict(self) -> Dict:
        return {
            'agent_name': self.agent_name,
            'agent_tier': self.agent_tier,
            'philosophy': self.philosophy,
            'attempts': len(self.attempts),
            'successes': self.success_count,
            'failures': self.failure_count,
            'success_rate': (self.success_count / len(self.attempts) * 100) if self.attempts else 0,
            'first_success_attempt': self.first_success,
            'weight_earned_total': self.weight_earned_total,
            'maturation_trajectory': self.maturation_trajectory,
            'maturation_story': self.get_maturation_story(),
            'attempts_detail': self.attempts
        }


class SessionNarrative:
    """
    The session tells its own story through metrics that demonstrate principles.

    Philosophy: "The architecture demonstrates itself"
    """

    def __init__(self, session_name: str):
        self.session_name = session_name
        self.start_time = datetime.now()
        self.end_time = None
        self.contacts_processed = []
        self.agent_lifecycles = {}
        self.decision_stories = []
        self.cost_narrative = {
            'philosophy': '"Efficiency without waste, exploration without penalty"',
            'free_agent_successes': 0,
            'google_validations': 0,
            'cost_saved': 0.0,
            'cost_spent': 0.0
        }
        self.philosophical_insights = []

    def add_agent(self, agent_name: str, agent_tier: str):
        """Register an agent lifecycle tracker"""
        self.agent_lifecycles[agent_name] = AgentLifecycle(agent_name, agent_tier)

    def record_contact_result(self, contact: Dict, agent_results: List[Dict],
                             decision: Dict):
        """
        Record a contact discovery result with full narrative.

        Philosophy: "Every decision carries the weight of its contributors"
        """
        contact_name = f"{contact['first_name']} {contact['last_name']}"

        # Update agent lifecycles
        for agent_result in agent_results:
            agent_name = agent_result['agent']
            if agent_name in self.agent_lifecycles:
                self.agent_lifecycles[agent_name].record_attempt(
                    confidence=agent_result['confidence'],
                    weight=agent_result['weight'],
                    contact_name=contact_name
                )

        # Create decision story
        contributing_agents = [a for a in agent_results if a['weight'] > 0]
        silent_agents = [a for a in agent_results if a['weight'] == 0]

        decision_story = {
            'contact': contact_name,
            'weighted_confidence': decision['weighted_confidence'],
            'contributing_agents': len(contributing_agents),
            'silent_agents': len(silent_agents),
            'decision': decision['decision'],
            'cost': decision['cost'],
            'philosophy': self._get_decision_philosophy(contributing_agents, silent_agents),
            'story': self._generate_decision_story(contact_name, contributing_agents,
                                                   silent_agents, decision)
        }

        self.decision_stories.append(decision_story)
        self.contacts_processed.append(contact)

        # Update cost narrative
        if decision['cost'] == 0:
            self.cost_narrative['free_agent_successes'] += 1
            self.cost_narrative['cost_saved'] += 0.005
        else:
            self.cost_narrative['google_validations'] += 1
            self.cost_narrative['cost_spent'] += decision['cost']

    def _get_decision_philosophy(self, contributing: List, silent: List) -> str:
        """Philosophy that explains why this decision pattern matters"""
        if len(silent) > len(contributing):
            return '"Most exploration is silence; the valuable parts speak loudly"'
        elif len(contributing) == 1:
            return '"Sometimes one clear voice is enough"'
        else:
            return '"Consensus emerges from diverse contribution"'

    def _generate_decision_story(self, contact: str, contributing: List,
                                 silent: List, decision: Dict) -> str:
        """Generate narrative about this specific decision"""
        contrib_names = [a['agent'] for a in contributing]
        silent_names = [a['agent'] for a in silent]

        story = f"Contact: {contact}. "

        if contributing:
            story += f"Contributing agents: {', '.join(contrib_names)}. "

        if silent:
            story += f"Silent agents (no penalty): {', '.join(silent_names)}. "

        story += f"Weighted confidence: {decision['weighted_confidence']:.1f}. "
        story += decision['decision']

        return story

    def add_philosophical_insight(self, insight: str, evidence: Dict):
        """Record when the system learns something about itself"""
        self.philosophical_insights.append({
            'insight': insight,
            'evidence': evidence,
            'timestamp': datetime.now().isoformat()
        })

    def finalize_session(self):
        """Complete session and generate final narrative"""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        # Identify emergent patterns
        self._identify_late_bloomers()
        self._identify_cost_patterns()
        self._identify_specialist_domains()

    def _identify_late_bloomers(self):
        """Detect late bloomer patterns and document"""
        for agent_name, lifecycle in self.agent_lifecycles.items():
            if len(lifecycle.maturation_trajectory) >= 3:
                early = lifecycle.maturation_trajectory[0]
                late = lifecycle.maturation_trajectory[-1]
                improvement = late - early

                if improvement > 15:  # Significant improvement
                    self.add_philosophical_insight(
                        f"Late bloomer detected: {agent_name}",
                        {
                            'agent': agent_name,
                            'early_performance': early,
                            'late_performance': late,
                            'improvement': improvement,
                            'philosophy': '"Truth rarely performs well in its early iterations"',
                            'validation': 'Weighted coordination kept exploring until maturation'
                        }
                    )

    def _identify_cost_patterns(self):
        """Document cost efficiency patterns"""
        total = len(self.contacts_processed)
        if total == 0:
            return

        free_rate = self.cost_narrative['free_agent_successes'] / total * 100

        if free_rate == 100:
            self.add_philosophical_insight(
                "Free agents sufficient for all contacts",
                {
                    'free_agent_rate': f"{free_rate:.0f}%",
                    'cost_saved': f"${self.cost_narrative['cost_saved']:.4f}",
                    'philosophy': '"Infrastructure independence is achievable"',
                    'validation': 'System discovered cost-effective strategies'
                }
            )
        elif free_rate >= 80:
            self.add_philosophical_insight(
                "Targeted Google validation strategy",
                {
                    'free_agent_rate': f"{free_rate:.0f}%",
                    'google_rate': f"{100-free_rate:.0f}%",
                    'philosophy': '"Expensive validation only when needed"',
                    'validation': 'Weighted coordination optimizes resource allocation'
                }
            )

    def _identify_specialist_domains(self):
        """Document when specialists find their domain"""
        for agent_name, lifecycle in self.agent_lifecycles.items():
            if lifecycle.agent_tier == 'specialist' and lifecycle.success_count > 0:
                self.add_philosophical_insight(
                    f"Specialist domain identified: {agent_name}",
                    {
                        'agent': agent_name,
                        'success_count': lifecycle.success_count,
                        'total_attempts': len(lifecycle.attempts),
                        'philosophy': '"Excellence in one domain is silence in others"',
                        'validation': 'Bimodal performance demonstrates targeted value'
                    }
                )

    def generate_complete_narrative(self) -> Dict:
        """
        Generate complete self-documenting session narrative.

        This IS the validation - the documentation demonstrates the principles.
        """
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0

        narrative = {
            'session_name': self.session_name,
            'philosophy': {
                'opening': '"Truth rarely performs well in its early iterations"',
                'core': 'Weighted coordination keeps bad branches alive, discovers late bloomers',
                'closing': '"The architecture demonstrates itself"'
            },
            'session_summary': {
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'duration_seconds': duration,
                'contacts_processed': len(self.contacts_processed),
                'decisions_made': len(self.decision_stories)
            },
            'cost_narrative': self.cost_narrative,
            'agent_lifecycles': {
                name: lifecycle.to_dict()
                for name, lifecycle in self.agent_lifecycles.items()
            },
            'decision_stories': self.decision_stories,
            'philosophical_insights': self.philosophical_insights,
            'validation_summary': self._generate_validation_summary(),
            'metadata': {
                'generated_by': 'InfraFabric Self-Documenting Coordinator',
                'philosophy': 'Documentation through contribution, not mandate',
                'timestamp': datetime.now().isoformat()
            }
        }

        return narrative

    def _generate_validation_summary(self) -> Dict:
        """
        Summarize what this session proved about InfraFabric principles.

        Philosophy: "Every session is a proof"
        """
        total_agents = len(self.agent_lifecycles)
        active_agents = sum(1 for lc in self.agent_lifecycles.values() if lc.success_count > 0)
        silent_agents = total_agents - active_agents

        validations = {
            'reciprocity_validated': active_agents > 0,
            'reciprocity_evidence': f"{active_agents}/{total_agents} agents earned influence through contribution",

            'graceful_degradation_validated': silent_agents > 0,
            'graceful_degradation_evidence': f"{silent_agents} agents failed without penalizing system (0.0 weight)",

            'cost_optimization_validated': self.cost_narrative['free_agent_successes'] > 0,
            'cost_optimization_evidence': f"${self.cost_narrative['cost_saved']:.4f} saved through free agents",

            'late_bloomer_tracking': len(self.philosophical_insights) > 0,
            'late_bloomer_evidence': f"{len([i for i in self.philosophical_insights if 'Late bloomer' in i['insight']])} late bloomers detected",

            'philosophy': '"The architecture works because it IS the architecture"'
        }

        return validations


def save_self_documenting_narrative(narrative: Dict, output_dir: str = "."):
    """
    Save narrative in self-documenting format.

    The file itself demonstrates InfraFabric principles through its structure.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"infrafabric-self-documenting-{timestamp}.json"
    filepath = Path(output_dir) / filename

    with open(filepath, 'w') as f:
        json.dump(narrative, f, indent=2)

    # Also create human-readable markdown
    md_filename = f"infrafabric-narrative-{timestamp}.md"
    md_filepath = Path(output_dir) / md_filename

    with open(md_filepath, 'w') as f:
        f.write(f"# InfraFabric Session Narrative\n\n")
        f.write(f"**Session:** {narrative['session_name']}\n")
        f.write(f"**Philosophy:** {narrative['philosophy']['core']}\n\n")
        f.write(f"---\n\n")

        f.write(f"## Session Summary\n\n")
        f.write(f"- Contacts processed: {narrative['session_summary']['contacts_processed']}\n")
        f.write(f"- Duration: {narrative['session_summary']['duration_seconds']:.1f} seconds\n\n")

        f.write(f"## Agent Lifecycles\n\n")
        for agent_name, lifecycle in narrative['agent_lifecycles'].items():
            f.write(f"### {agent_name} [{lifecycle['agent_tier']}]\n\n")
            f.write(f"**Philosophy:** {lifecycle['philosophy']}\n\n")
            f.write(f"**Story:** {lifecycle['maturation_story']}\n\n")

        f.write(f"## Philosophical Insights\n\n")
        for insight in narrative['philosophical_insights']:
            f.write(f"### {insight['insight']}\n\n")
            f.write(f"**Evidence:** {json.dumps(insight['evidence'], indent=2)}\n\n")

        f.write(f"## Validation Summary\n\n")
        for key, value in narrative['validation_summary'].items():
            if not key.endswith('_evidence') and not key == 'philosophy':
                f.write(f"- **{key}**: {value}\n")

        f.write(f"\n---\n\n")
        f.write(f"*{narrative['philosophy']['closing']}*\n")

    print(f"\n✅ Self-documenting narrative saved:")
    print(f"   JSON: {filepath}")
    print(f"   Markdown: {md_filepath}")

    return filepath, md_filepath


if __name__ == "__main__":
    # Example usage
    print("="*80)
    print("SELF-DOCUMENTING COORDINATOR - InfraFabric Philosophy")
    print("="*80)
    print("\nPhilosophy:")
    print('  "Documentation through contribution, not mandate"')
    print('  - Every metric tells a story')
    print('  - Agent lifecycles track maturation')
    print('  - Philosophical insights emerge from data')
    print('  - The narrative validates the architecture')
    print("="*80)

    # This module is imported by weighted_multi_agent_finder.py
    # to provide self-documenting capabilities
    print("\nReady to document weighted coordination sessions.")
    print("Import this module to enable philosophical self-documentation.\n")
