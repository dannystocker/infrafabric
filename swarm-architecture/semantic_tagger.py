#!/usr/bin/env python3
"""
Semantic Tagger for Redis Memory Exoskeleton
Analyzes all Redis keys and generates semantic tags for context-aware search
"""
import json
import re
from typing import Dict, List, Any
from collections import Counter

def extract_instance_number(key: str) -> int:
    """Extract instance number from key if present"""
    match = re.search(r'instance:(\d+)', key)
    return int(match.group(1)) if match else None

def classify_content_type(key: str, content: str) -> str:
    """Determine content type based on key and content"""
    if 'finding:' in key:
        return 'discovery'
    elif 'task:' in key:
        return 'work_item'
    elif ':context:' in key:
        return 'session_context'
    elif ':deployment' in key or ':transfer:' in key:
        return 'infrastructure'
    elif ':decision' in key or ':strategy' in key:
        return 'strategic'
    elif 'bull:' in key or 'queue:' in key:
        return 'job_queue'
    elif 'librarian:' in key or 'shard:' in key:
        return 'swarm_coordination'
    elif 'synthesis:' in key:
        return 'analysis'
    else:
        return 'metadata'

def extract_topics(content: str) -> List[str]:
    """Extract semantic topics from content"""
    topics = []
    content_lower = content.lower()

    # Topic detection patterns
    topic_patterns = {
        'partnership': r'\b(partnership|collaboration|partner|georges)\b',
        'deployment': r'\b(deploy|production|stackcp|live)\b',
        'redis': r'\b(redis|cache|keys|findings)\b',
        'testing': r'\b(test|validation|verify|check)\b',
        'documentation': r'\b(document|handover|session|summary)\b',
        'swarm': r'\b(swarm|worker|haiku|gemini|librarian)\b',
        'cost': r'\b(cost|pricing|savings|budget)\b',
        'demo': r'\b(demo|presentation|guardian council)\b',
        'logistics': r'\b(gedimat|logistics|transport|mediafret)\b',
        'architecture': r'\b(architecture|framework|infrastructure|pattern)\b',
    }

    for topic, pattern in topic_patterns.items():
        if re.search(pattern, content_lower):
            topics.append(topic)

    return topics

def extract_agents(content: str) -> List[str]:
    """Extract agent references from content"""
    agents = []

    # Known agent patterns
    agent_patterns = {
        'sonnet': r'\b(sonnet|claude sonnet)\b',
        'haiku': r'\b(haiku|haiku worker)\b',
        'gemini': r'\b(gemini|gemini flash|gemini pro)\b',
        'guardian_council': r'\b(guardian council|guardians)\b',
        'if.ceo': r'\b(if\.ceo|executive decision)\b',
    }

    content_lower = content.lower()
    for agent, pattern in agent_patterns.items():
        if re.search(pattern, content_lower):
            agents.append(agent)

    return agents

def determine_status(key: str, content: str) -> str:
    """Determine status/state of the entry"""
    content_lower = content.lower()

    if re.search(r'\b(complete|completed|done|finished|passed)\b', content_lower):
        return 'completed'
    elif re.search(r'\b(in progress|ongoing|running|active)\b', content_lower):
        return 'active'
    elif re.search(r'\b(pending|queued|scheduled|waiting)\b', content_lower):
        return 'pending'
    elif re.search(r'\b(failed|error|blocked)\b', content_lower):
        return 'failed'
    elif re.search(r'\b(ready|prepared|available)\b', content_lower):
        return 'ready'
    else:
        return 'archived'

def estimate_importance(key: str, content: str) -> str:
    """Estimate importance level"""
    content_lower = content.lower()

    # Critical indicators
    if re.search(r'\b(critical|urgent|p0|blocker|production)\b', content_lower):
        return 'high'
    elif re.search(r'\b(important|significant|key|major)\b', content_lower):
        return 'medium'
    else:
        return 'normal'

def generate_tags(entry: Dict[str, str]) -> Dict[str, Any]:
    """Generate comprehensive semantic tags for a Redis entry"""
    key = entry['id'].strip()
    content = entry['content']

    # Parse key structure
    key_parts = key.split(':')
    prefix = key_parts[0]

    # Generate tags
    tags = {
        'key': key,
        'prefix': prefix,
        'instance': extract_instance_number(key),
        'content_type': classify_content_type(key, content),
        'topics': extract_topics(content),
        'agents': extract_agents(content),
        'status': determine_status(key, content),
        'importance': estimate_importance(key, content),
        'content_length': len(content),
        'has_json': content.strip().startswith('{') and content.strip().endswith('}'),
    }

    # Add specific metadata based on prefix
    if prefix == 'instance':
        tags['instance_specific'] = True
        if len(key_parts) > 2:
            tags['subsystem'] = key_parts[2]
    elif prefix == 'finding':
        tags['is_discovery'] = True
    elif prefix == 'task':
        tags['is_work_item'] = True
    elif prefix in ['bull', 'queue']:
        tags['is_queue'] = True
    elif prefix in ['librarian', 'shard']:
        tags['is_swarm_coordination'] = True

    return tags

def analyze_corpus(data: Dict) -> Dict[str, Any]:
    """Analyze entire corpus and generate statistics"""
    all_tags = []

    for entry in data['data']:
        tags = generate_tags(entry)
        all_tags.append(tags)

    # Compute statistics
    stats = {
        'total_keys': len(all_tags),
        'by_prefix': Counter(t['prefix'] for t in all_tags),
        'by_content_type': Counter(t['content_type'] for t in all_tags),
        'by_status': Counter(t['status'] for t in all_tags),
        'by_importance': Counter(t['importance'] for t in all_tags),
        'instances': sorted(set(t['instance'] for t in all_tags if t['instance'])),
        'all_topics': sorted(set(topic for t in all_tags for topic in t['topics'])),
        'all_agents': sorted(set(agent for t in all_tags for agent in t['agents'])),
    }

    return {
        'tags': all_tags,
        'statistics': stats,
        'summary': {
            'total_entries': stats['total_keys'],
            'unique_instances': len(stats['instances']),
            'unique_topics': len(stats['all_topics']),
            'unique_agents': len(stats['all_agents']),
        }
    }

def main():
    """Main execution"""
    print("🏷️  Semantic Tagger for Redis Memory Exoskeleton")
    print("=" * 60)

    # Load data
    with open('/tmp/redis-all-keys.json', 'r') as f:
        data = json.load(f)

    print(f"📊 Loaded {data['batch_size']} keys from bridge.php")
    print()

    # Analyze and tag
    print("🔍 Analyzing and generating semantic tags...")
    result = analyze_corpus(data)

    # Print statistics
    print(f"\n✅ Tagged {result['summary']['total_entries']} entries")
    print(f"   - Instances: {result['summary']['unique_instances']}")
    print(f"   - Topics: {result['summary']['unique_topics']}")
    print(f"   - Agents: {result['summary']['unique_agents']}")
    print()

    print("📈 Key Distribution:")
    for prefix, count in result['statistics']['by_prefix'].most_common():
        print(f"   {prefix:20s}: {count:3d} keys")
    print()

    print("🏷️  Content Types:")
    for ctype, count in result['statistics']['by_content_type'].most_common():
        print(f"   {ctype:20s}: {count:3d} entries")
    print()

    print("🔍 Topics Found:")
    for topic in result['statistics']['all_topics']:
        count = sum(1 for t in result['tags'] if topic in t['topics'])
        print(f"   {topic:20s}: {count:3d} occurrences")
    print()

    # Save results
    output_file = '/tmp/redis-semantic-tags.json'
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"💾 Saved semantic tags to: {output_file}")
    print(f"   File size: {len(json.dumps(result)) // 1024} KB")

    return result

if __name__ == '__main__':
    result = main()
