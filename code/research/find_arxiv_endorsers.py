#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IF.mission.arxiv - Endorser Discovery
Find potential arXiv cs.AI endorsers from recent papers.

Focus: Authors with publications in topics relevant to InfraFabric
(multi-agent systems, AI safety, coordination, verification)
"""

import feedparser
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Set
from collections import Counter

# Keywords aligned with InfraFabric
IF_ENDORSER_KEYWORDS = {
    # High priority (core to InfraFabric)
    "multi-agent": 5,
    "coordination": 5,
    "safety": 4,
    "verification": 4,
    "alignment": 4,

    # Medium priority (systems/methods)
    "distributed": 3,
    "orchestration": 3,
    "protocol": 3,
    "governance": 3,
    "audit": 3,

    # Related (broader relevance)
    "reasoning": 2,
    "planning": 2,
    "reinforcement learning": 2,
    "llm": 2,
    "agent": 2,
}

@dataclass
class Author:
    name: str
    papers: List[str]  # paper titles
    urls: List[str]    # arXiv URLs
    relevance_score: float
    keywords_found: Set[str]

def fetch_recent_cs_ai(days: int = 7, limit: int = 100) -> List[Dict]:
    """Fetch recent cs.AI papers from arXiv RSS"""
    print(f"Fetching arXiv cs.AI papers (limit={limit})...")
    feed = feedparser.parse("https://export.arxiv.org/rss/cs.AI")

    papers = []
    for entry in feed.entries[:limit]:
        # Extract authors (feedparser provides this in entry.authors)
        authors = []
        if hasattr(entry, 'authors'):
            authors = [a.get('name', '') for a in entry.authors]
        elif hasattr(entry, 'author'):
            authors = [entry.author]

        papers.append({
            "title": entry.get("title", "").strip(),
            "summary": entry.get("summary", "").strip(),
            "link": entry.get("link", ""),
            "authors": authors,
            "published": entry.get("published", "")
        })

    print(f"Fetched {len(papers)} papers")
    return papers

def score_paper_relevance(paper: Dict) -> tuple[float, Set[str]]:
    """Score paper relevance to InfraFabric and return matching keywords"""
    text = f"{paper['title']} {paper['summary']}".lower()
    score = 0
    matches = set()

    for keyword, weight in IF_ENDORSER_KEYWORDS.items():
        if keyword in text:
            score += weight
            matches.add(keyword)

    return score, matches

def find_potential_endorsers(papers: List[Dict], min_score: float = 3.0) -> List[Author]:
    """Extract and rank potential endorsers by relevance"""
    author_data: Dict[str, Dict] = {}

    for paper in papers:
        relevance, keywords = score_paper_relevance(paper)

        if relevance < min_score:
            continue

        for author_name in paper["authors"]:
            if not author_name:
                continue

            if author_name not in author_data:
                author_data[author_name] = {
                    "papers": [],
                    "urls": [],
                    "total_score": 0.0,
                    "keywords": set()
                }

            author_data[author_name]["papers"].append(paper["title"])
            author_data[author_name]["urls"].append(paper["link"])
            author_data[author_name]["total_score"] += relevance
            author_data[author_name]["keywords"].update(keywords)

    # Convert to Author objects and sort by relevance
    authors = []
    for name, data in author_data.items():
        authors.append(Author(
            name=name,
            papers=data["papers"],
            urls=data["urls"],
            relevance_score=data["total_score"],
            keywords_found=data["keywords"]
        ))

    return sorted(authors, key=lambda a: a.relevance_score, reverse=True)

def generate_endorser_report(authors: List[Author], output_path: str):
    """Generate markdown report of potential endorsers"""
    lines = []
    lines.append("# Potential arXiv cs.AI Endorsers for InfraFabric\n")
    lines.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"**Candidates Found:** {len(authors)}\n")

    lines.append("## Top Candidates (by relevance to InfraFabric)\n")

    for i, author in enumerate(authors[:20], 1):  # Top 20
        lines.append(f"### {i}. {author.name}")
        lines.append(f"**Relevance Score:** {author.relevance_score:.1f}")
        lines.append(f"**Matching Topics:** {', '.join(sorted(author.keywords_found))}")
        lines.append(f"**Paper Count:** {len(author.papers)}")
        lines.append("\n**Recent Papers:**")
        for paper, url in zip(author.papers[:3], author.urls[:3]):
            lines.append(f"- [{paper[:80]}...]({url})")
        lines.append("")

        # Contact suggestion
        if author.relevance_score >= 10:
            lines.append("🎯 **HIGH PRIORITY** - Strong alignment with InfraFabric themes")
        elif author.relevance_score >= 6:
            lines.append("✅ **GOOD MATCH** - Relevant research area")
        lines.append("\n---\n")

    # Summary statistics
    lines.append("## Summary Statistics\n")
    all_keywords = Counter()
    for author in authors:
        all_keywords.update(author.keywords_found)

    lines.append("**Most Common Topics:**")
    for keyword, count in all_keywords.most_common(10):
        lines.append(f"- {keyword}: {count} authors")

    lines.append("\n## How to Request Endorsement\n")
    lines.append("1. **Email Template:** Use arXiv's endorsement request format")
    lines.append("2. **Introduce InfraFabric:** Multi-agent coordination infrastructure")
    lines.append("3. **Highlight Alignment:** Reference their work on [matching topics]")
    lines.append("4. **Paper Category:** cs.AI (Artificial Intelligence)")
    lines.append("5. **Link to GitHub:** https://github.com/dannystocker/infrafabric")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path

def save_json_export(authors: List[Author], output_path: str):
    """Export structured data for further analysis"""
    data = []
    for author in authors:
        data.append({
            "name": author.name,
            "relevance_score": author.relevance_score,
            "paper_count": len(author.papers),
            "papers": author.papers,
            "urls": author.urls,
            "keywords": list(author.keywords_found)
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return output_path

if __name__ == "__main__":
    print("=" * 70)
    print("IF.mission.arxiv - Endorser Discovery")
    print("Finding potential arXiv cs.AI endorsers for InfraFabric")
    print("=" * 70)
    print()

    # Fetch papers
    papers = fetch_recent_cs_ai(limit=100)

    # Find endorsers
    print("\nAnalyzing authors and relevance...")
    endorsers = find_potential_endorsers(papers, min_score=3.0)

    print(f"Found {len(endorsers)} potential endorsers")
    print(f"Top candidate: {endorsers[0].name} (score: {endorsers[0].relevance_score:.1f})")

    # Generate reports
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    report_path = f"ARXIV_ENDORSERS.{timestamp}.md"
    json_path = f"arxiv_endorsers.{timestamp}.json"

    generate_endorser_report(endorsers, report_path)
    save_json_export(endorsers, json_path)

    print(f"\n✅ Reports generated:")
    print(f"   - {report_path}")
    print(f"   - {json_path}")
    print("\nNext steps:")
    print("1. Review top candidates in the report")
    print("2. Check their recent papers for alignment")
    print("3. Draft personalized endorsement request emails")
