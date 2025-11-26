#!/usr/bin/env python3
"""
Context Indicator - Real-time swarm status for Sonnet coordinator
Shows Redis context, active workers, librarian status, and cost efficiency
"""
import redis
import json
import sys
from datetime import datetime, timedelta

def get_swarm_status():
    """Generate comprehensive swarm status"""
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)

        # Test connection
        r.ping()

    except redis.ConnectionError:
        return {
            'error': 'Redis not connected',
            'redis_running': False
        }

    # Count findings
    findings = r.keys('finding:*')
    finding_count = len(findings)

    # Estimate tokens (sample a few findings for average)
    token_estimate = 0
    if finding_count > 0:
        sample_size = min(5, finding_count)
        for key in findings[:sample_size]:
            try:
                finding_json = r.get(key)
                if finding_json:
                    finding = json.loads(finding_json)
                    token_estimate += finding.get('tokens_used', 100)
            except:
                token_estimate += 100  # Default estimate

        avg_tokens = token_estimate / sample_size
        token_estimate = int(avg_tokens * finding_count)

    # Count active workers (heartbeat within last 60 seconds)
    workers = r.keys('worker:status:*')
    active_workers = []
    now = datetime.now()

    for worker_key in workers:
        try:
            timestamp_str = r.get(worker_key)
            if timestamp_str:
                worker_timestamp = datetime.fromisoformat(timestamp_str)
                if now - worker_timestamp < timedelta(seconds=60):
                    worker_id = worker_key.replace('worker:status:', '')
                    active_workers.append(worker_id)
        except:
            pass

    # Check librarian shards quota
    shard_status = []
    for i in range(1, 6):
        quota_key = f'librarian:shard{i}:quota'
        quota = r.get(quota_key)

        if quota is None:
            # Initialize if not set (assume full quota)
            quota = 1500
            r.set(quota_key, quota)

        quota = int(quota)
        shard_status.append({
            'shard': i,
            'quota': quota,
            'available': quota > 0
        })

    # Calculate costs
    sonnet_cost = float(r.get('cost:sonnet') or 0)
    haiku_cost = float(r.get('cost:haiku') or 0)
    gemini_cost = float(r.get('cost:gemini') or 0)

    # Calculate efficiency
    total_cost = sonnet_cost + haiku_cost
    if total_cost > 0:
        haiku_pct = (haiku_cost / total_cost * 100)
        sonnet_pct = (sonnet_cost / total_cost * 100)
    else:
        haiku_pct = 0
        sonnet_pct = 0

    # Get task queue size
    tasks_queued = len(r.keys('task:*:claimed'))

    return {
        'redis_running': True,
        'findings': finding_count,
        'tokens': token_estimate,
        'workers': {
            'active': len(active_workers),
            'ids': active_workers
        },
        'shards': shard_status,
        'costs': {
            'sonnet': sonnet_cost,
            'haiku': haiku_cost,
            'gemini': gemini_cost,
            'total': sonnet_cost + haiku_cost + gemini_cost
        },
        'efficiency': {
            'haiku_pct': haiku_pct,
            'sonnet_pct': sonnet_pct,
            'target': 90  # Target 90% Haiku
        },
        'tasks_queued': tasks_queued
    }

def format_status(status):
    """Format status for display"""
    if not status.get('redis_running'):
        return """
❌ SWARM STATUS - REDIS NOT CONNECTED
   Start Redis: sudo service redis-server start
   Test: redis-cli PING
"""

    # Format shard status
    shard_display = []
    for shard in status['shards']:
        quota = shard['quota']
        available = '✅' if shard['available'] else '❌'
        shard_display.append(f"S{shard['shard']}:{quota}{available}")

    # Worker list
    worker_display = ', '.join(status['workers']['ids']) if status['workers']['ids'] else 'None'

    # Efficiency indicator
    haiku_pct = status['efficiency']['haiku_pct']
    target = status['efficiency']['target']
    efficiency_status = '✅' if haiku_pct >= target else '⚠️'

    output = f"""
📊 SWARM STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Redis Context:    {status['findings']} findings, ~{status['tokens']:,} tokens
Active Workers:   {status['workers']['active']} Haiku{'s' if status['workers']['active'] != 1 else ''} ({worker_display})
Librarians:       {' | '.join(shard_display)}
Tasks Queued:     {status['tasks_queued']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cost This Session:
  Sonnet:  ${status['costs']['sonnet']:.4f}
  Haiku:   ${status['costs']['haiku']:.4f}
  Gemini:  ${status['costs']['gemini']:.4f}
  Total:   ${status['costs']['total']:.4f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Token Efficiency: {efficiency_status}
  Haiku:   {haiku_pct:5.1f}% (target: {target}%+)
  Sonnet:  {status['efficiency']['sonnet_pct']:5.1f}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return output

def reset_costs():
    """Reset cost tracking (new session)"""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.set('cost:sonnet', 0)
    r.set('cost:haiku', 0)
    r.set('cost:gemini', 0)
    print("✅ Cost tracking reset")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Swarm Context Indicator')
    parser.add_argument('--reset', action='store_true', help='Reset cost tracking')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if args.reset:
        reset_costs()
        sys.exit(0)

    status = get_swarm_status()

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(format_status(status))
