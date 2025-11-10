#!/usr/bin/env python3
"""
IF.swarm - Gap Analysis Mode
Uses Haiku agents to find:
1. Patterns matching IF universe (integration opportunities)
2. Gaps in IF universe (what we're missing)
"""

import os, json, feedparser, time
from datetime import datetime
from typing import List, Dict

# IF Universe Components (what we have)
IF_COMPONENTS = [
    "IF.ground", "IF.guard", "IF.witness", "IF.citation", "IF.trace",
    "IF.optimise", "IF.swarm", "IF.search", "IF.forge", "IF.connect",
    "IF.router", "IF.armour", "IF.armour.yologuard", "IF.persona",
    "IF.vision", "IF.chase", "IF.collapse", "IF.garp", "IF.reflect",
    "IF.vesicle", "IF.ceo", "IF.TTT", "IF.mission", "IF.constitution"
]

# IF Themes (what we care about)
IF_THEMES = [
    "multi-agent coordination", "safety verification", "citation provenance",
    "token cost optimization", "graceful degradation", "Guardian Council",
    "philosophical foundations", "anti-hallucination", "epistemic agents",
    "trustless coordination", "falsifiability", "transparent metrics"
]

def llm_haiku(prompt: str) -> str:
    """Call Anthropic Haiku (fast + cheap)"""
    if not os.getenv("ANTHROPIC_API_KEY"):
        return "[STUB] Set ANTHROPIC_API_KEY to use real Haiku"
    
    try:
        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.1,
            messages=[{"role":"user","content":prompt}]
        )
        return resp.content[0].text
    except Exception as e:
        return f"[ERROR] {e}"

def analyze_paper_for_patterns(paper: Dict) -> Dict:
    """Haiku: Find IF patterns in paper"""
    prompt = f"""You are analyzing this arXiv paper for InfraFabric integration.

Paper: {paper['title']}
Abstract: {paper['summary'][:800]}

InfraFabric components: {', '.join(IF_COMPONENTS[:15])}...
InfraFabric themes: {', '.join(IF_THEMES[:8])}...

Task 1: Find matching patterns
- Which IF components could benefit from this paper's concepts?
- What specific techniques/approaches align with IF themes?

Task 2: Identify gaps
- What does this paper have that InfraFabric lacks?
- What capability/pattern would strengthen IF?

Format (4 bullets max per section):
PATTERNS:
- [component]: [technique from paper]

GAPS:
- [missing capability]: [why it matters]

INTEGRATION:
- [concrete 1-sentence proposal]
"""
    
    analysis = llm_haiku(prompt)
    return {
        "paper": paper['title'],
        "url": paper['link'],
        "analysis": analysis
    }

def run_gap_analysis(top_n: int = 5):
    """Main: Fetch papers, run Haiku gap analysis"""
    print("Fetching recent cs.AI papers...")
    feed = feedparser.parse("https://export.arxiv.org/rss/cs.AI")
    
    # Score by IF keywords
    papers = []
    for entry in feed.entries[:50]:
        text = f"{entry.get('title','')} {entry.get('summary','')}".lower()
        score = sum(
            3 if k in text else 0
            for k in ["multi-agent", "coordination", "safety", "verification"]
        )
        if score >= 3:
            papers.append({
                "title": entry.get("title", "").strip(),
                "summary": entry.get("summary", "").strip(),
                "link": entry.get("link", ""),
                "score": score
            })
    
    papers = sorted(papers, key=lambda p: p['score'], reverse=True)[:top_n]
    print(f"Analyzing top {len(papers)} papers with Haiku...\n")
    
    results = []
    for i, paper in enumerate(papers, 1):
        print(f"[{i}/{len(papers)}] {paper['title'][:60]}...")
        result = analyze_paper_for_patterns(paper)
        results.append(result)
        time.sleep(2)  # Rate limiting
    
    return results

def compile_gap_report(results: List[Dict], output_path: str):
    """Generate markdown gap analysis report"""
    lines = []
    lines.append("# InfraFabric Gap Analysis - arXiv cs.AI\n")
    lines.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"**Papers Analyzed:** {len(results)}\n")
    
    lines.append("## Executive Summary\n")
    lines.append("**Purpose:** Identify patterns matching IF universe + gaps to address\n")
    
    for i, result in enumerate(results, 1):
        lines.append(f"---\n## {i}. {result['paper']}\n")
        lines.append(f"**URL:** {result['url']}\n")
        lines.append(result['analysis'])
        lines.append("\n")
    
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    
    return output_path

if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Set ANTHROPIC_API_KEY to use Haiku")
        print("   export ANTHROPIC_API_KEY=sk-ant-...")
        print("\nRunning in STUB mode (no real analysis)\n")
    
    results = run_gap_analysis(top_n=5)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    report_path = f"IF_GAP_ANALYSIS.{timestamp}.md"
    compile_gap_report(results, report_path)
    
    print(f"\n✅ Gap analysis complete: {report_path}")
    print("\nNext steps:")
    print("1. Review PATTERNS section for integration opportunities")
    print("2. Review GAPS section for missing IF capabilities")
    print("3. Queue top integrations for IF.guard deliberation")
