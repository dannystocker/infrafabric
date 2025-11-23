#!/usr/bin/env python3
"""
Test Harness for Semantic Search
Simulates bridge.php search functionality locally
"""
import json
from typing import List, Dict, Any

def load_tags():
    """Load semantic tags"""
    with open('/tmp/redis-semantic-tags-bridge.json', 'r') as f:
        return json.load(f)

def load_data():
    """Load Redis data"""
    with open('/tmp/redis-all-keys.json', 'r') as f:
        return json.load(f)

def semantic_search(tags_dict: Dict, query: str, limit: int = 20) -> List[Dict]:
    """Semantic search implementation matching bridge.php"""
    query = query.lower().strip()
    results = []

    for key, tag in tags_dict['tags'].items():
        score = 0

        # Check topics
        for topic in tag.get('topics', []):
            if query in topic.lower():
                score += 5

        # Check agents
        for agent in tag.get('agents', []):
            if query in agent.lower():
                score += 3

        # Check content type
        if query in tag.get('content_type', '').lower():
            score += 4

        # Check status
        if query in tag.get('status', '').lower():
            score += 2

        # Check key
        if query in key.lower():
            score += 10

        if score > 0:
            results.append({
                'key': key,
                'score': score,
                'tags': {
                    'topics': tag.get('topics', []),
                    'agents': tag.get('agents', []),
                    'type': tag.get('content_type'),
                    'status': tag.get('status')
                }
            })

    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:limit]

def run_test_queries():
    """Run comprehensive test queries"""
    print("🧪 Semantic Search Test Harness")
    print("=" * 60)

    tags = load_tags()
    data = load_data()

    print(f"📊 Loaded {tags['total_keys']} tags")
    print()

    test_queries = [
        ("partnership", "Find partnership-related keys"),
        ("deployment", "Find deployment infrastructure"),
        ("redis", "Find Redis-related content"),
        ("sonnet", "Find Sonnet agent work"),
        ("haiku", "Find Haiku worker output"),
        ("completed", "Find completed work"),
        ("testing", "Find test-related keys"),
        ("logistics", "Find logistics/GEDIMAT work"),
        ("instance:12", "Find Instance #12 keys"),
        ("finding", "Find worker discoveries"),
    ]

    for query, description in test_queries:
        print(f"🔍 Query: '{query}' - {description}")
        results = semantic_search(tags, query, limit=5)

        print(f"   Results: {len(results)}")
        if results:
            print(f"   Top 3:")
            for i, result in enumerate(results[:3], 1):
                key_short = result['key'][:60] + '...' if len(result['key']) > 60 else result['key']
                print(f"     {i}. [{result['score']}] {key_short}")
                if result['tags']['topics']:
                    print(f"        Topics: {', '.join(result['tags']['topics'][:3])}")
        print()

    # Test quality metrics
    print("📈 Quality Metrics:")
    print()

    # Coverage test
    all_results = []
    for query, _ in test_queries:
        results = semantic_search(tags, query, limit=100)
        all_results.extend([r['key'] for r in results])

    unique_keys_found = len(set(all_results))
    coverage = (unique_keys_found / tags['total_keys']) * 100

    print(f"   Coverage: {unique_keys_found}/{tags['total_keys']} keys ({coverage:.1f}%)")
    print(f"   Average Results per Query: {len(all_results) / len(test_queries):.1f}")
    print()

    # Precision test (manual spot-check)
    print("🎯 Precision Spot-Checks:")
    precision_tests = [
        ("partnership", "instance:12:strategy:partnership"),
        ("deployment", "instance:11:deployment"),
        ("redis", "finding:finding_3c7f9b2"),
    ]

    for query, expected_key in precision_tests:
        results = semantic_search(tags, query, limit=20)
        found = any(r['key'].strip() == expected_key for r in results)
        status = "✅" if found else "❌"
        print(f"   {status} '{query}' → '{expected_key}' {'FOUND' if found else 'NOT FOUND'}")

    print()
    print("✅ Test harness complete")

if __name__ == '__main__':
    run_test_queries()
