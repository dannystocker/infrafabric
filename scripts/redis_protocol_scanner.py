#!/usr/bin/env python3
"""
Comprehensive Redis Protocol Scanner
Scans ALL Redis keys and extracts EVERY mention of IF protocols and components.
"""

import redis
import re
import json
from collections import defaultdict
from datetime import datetime

# Redis connection details
REDIS_CONFIG = {
    'host': 'redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com',
    'port': 19956,
    'password': 'zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8',
    'decode_responses': True,
    'socket_timeout': 30,
    'socket_connect_timeout': 30
}

# Search patterns
PATTERNS = [
    r'\bif\.',  # if. (lowercase)
    r'\bIF\.',  # IF. (uppercase)
    r'\bif:',   # if: (with colon)
    r'\bIF:',   # IF: (with colon)
    r'\binfrafabric\b',
    r'\binstance:',
    r'\bsession:',
    r'\bcontext:',
    r'\bfinding:',
    r'\bcouncil\b',
    r'\byologuard\b',
    r'\blibrarian\b',
    r'\bvesicle\b',  # Legacy term
    r'\bparcel\b',    # Current civic term
    r'\blogistics\b', # Current department name
    r'\barbitrate\b',
    r'\bttt\b',
    r'\bguard\b',
    r'\bcitate\b',
    r'\boptimise\b',
    r'\bsam\b',
]

# Protocol extraction pattern - more comprehensive
PROTOCOL_PATTERN = r'(?i)\b(if[.:][\w\-]+|infrafabric[\w\-]*)\b'

class RedisProtocolScanner:
    def __init__(self):
        self.r = None
        self.protocols = defaultdict(lambda: {
            'keys': set(),
            'values': [],
            'descriptions': set(),
            'first_seen': None,
            'count': 0
        })
        self.stats = {
            'total_keys_scanned': 0,
            'total_protocols_found': 0,
            'keys_with_protocols': 0,
            'scan_timestamp': datetime.utcnow().isoformat()
        }

    def connect(self):
        """Connect to Redis"""
        print(f"Connecting to Redis at {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}...")
        try:
            self.r = redis.Redis(**REDIS_CONFIG)
            self.r.ping()
            print("✓ Connected successfully")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    def extract_protocols(self, text):
        """Extract all IF protocol mentions from text"""
        if not text:
            return set()

        text_str = str(text)
        matches = re.findall(PROTOCOL_PATTERN, text_str, re.IGNORECASE)

        # Normalize protocol names (uppercase IF.)
        normalized = set()
        for match in matches:
            # Convert to uppercase IF. format
            if match.lower().startswith('if.') or match.lower().startswith('if:'):
                normalized.add('IF.' + match[3:].upper() if '.' in match else 'IF:' + match[3:].upper())
            else:
                normalized.add(match.upper())

        return normalized

    def get_value_safely(self, key):
        """Get value from Redis key, handling different data types"""
        try:
            key_type = self.r.type(key)

            if key_type == 'string':
                return self.r.get(key)
            elif key_type == 'hash':
                return json.dumps(self.r.hgetall(key))
            elif key_type == 'list':
                return json.dumps(self.r.lrange(key, 0, -1))
            elif key_type == 'set':
                return json.dumps(list(self.r.smembers(key)))
            elif key_type == 'zset':
                return json.dumps(self.r.zrange(key, 0, -1, withscores=True))
            else:
                return f"<{key_type}>"
        except Exception as e:
            return f"<error: {e}>"

    def extract_description(self, context):
        """Extract description from context if available"""
        if not context:
            return None

        context_str = str(context)

        # Look for description patterns
        desc_patterns = [
            r'"description"\s*:\s*"([^"]+)"',
            r'"desc"\s*:\s*"([^"]+)"',
            r'description:\s*([^\n]+)',
            r'- ([^-\n]{20,100})',  # Bullet point descriptions
        ]

        for pattern in desc_patterns:
            match = re.search(pattern, context_str, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def scan_all_keys(self):
        """Scan all Redis keys comprehensively"""
        print("\nScanning all Redis keys...")

        cursor = 0
        key_count = 0

        while True:
            cursor, keys = self.r.scan(cursor, count=1000)

            for key in keys:
                key_count += 1
                if key_count % 100 == 0:
                    print(f"  Scanned {key_count} keys...", end='\r')

                self.stats['total_keys_scanned'] += 1

                # Extract protocols from key name
                key_protocols = self.extract_protocols(key)

                # Get value and extract protocols
                value = self.get_value_safely(key)
                value_protocols = self.extract_protocols(value)

                # Combine all protocols found
                all_protocols = key_protocols | value_protocols

                if all_protocols:
                    self.stats['keys_with_protocols'] += 1

                    for protocol in all_protocols:
                        self.protocols[protocol]['keys'].add(key)
                        self.protocols[protocol]['count'] += 1

                        # Store sample value
                        if len(self.protocols[protocol]['values']) < 5:
                            self.protocols[protocol]['values'].append({
                                'key': key,
                                'value_preview': value[:200] if value else ''
                            })

                        # Extract description
                        desc = self.extract_description(value)
                        if desc:
                            self.protocols[protocol]['descriptions'].add(desc)

            if cursor == 0:
                break

        print(f"\n✓ Scanned {key_count} keys total")
        self.stats['total_protocols_found'] = len(self.protocols)

    def generate_report(self, output_path):
        """Generate comprehensive markdown report"""
        print(f"\nGenerating report to {output_path}...")

        with open(output_path, 'w') as f:
            f.write("# IF Protocol Registry\n\n")
            f.write(f"**Generated:** {self.stats['scan_timestamp']}\n\n")
            f.write("**Scan Statistics:**\n")
            f.write(f"- Total Redis keys scanned: {self.stats['total_keys_scanned']}\n")
            f.write(f"- Keys containing IF protocols: {self.stats['keys_with_protocols']}\n")
            f.write(f"- Unique IF protocols found: {self.stats['total_protocols_found']}\n\n")

            f.write("---\n\n")
            f.write("## Protocol Registry\n\n")

            # Sort protocols alphabetically
            sorted_protocols = sorted(self.protocols.items())

            for protocol, data in sorted_protocols:
                f.write(f"### {protocol}\n\n")
                f.write(f"**Occurrences:** {data['count']}\n\n")
                f.write(f"**Found in {len(data['keys'])} Redis key(s):**\n")

                # List keys (limit to 20 for readability)
                for i, key in enumerate(sorted(data['keys'])):
                    if i < 20:
                        f.write(f"- `{key}`\n")
                    elif i == 20:
                        f.write(f"- ... and {len(data['keys']) - 20} more\n")
                        break

                f.write("\n")

                # Descriptions
                if data['descriptions']:
                    f.write("**Descriptions:**\n")
                    for desc in data['descriptions']:
                        f.write(f"- {desc}\n")
                    f.write("\n")

                # Sample values
                if data['values']:
                    f.write("**Sample Values:**\n")
                    for sample in data['values'][:3]:
                        f.write(f"- Key: `{sample['key']}`\n")
                        if sample['value_preview']:
                            f.write(f"  ```\n  {sample['value_preview']}\n  ```\n")
                    f.write("\n")

                # Implementation status (TBD - will be cross-referenced)
                f.write("**Implementation Status:** TBD (requires code cross-reference)\n\n")

                f.write("---\n\n")

            # Summary by category
            f.write("## Protocol Categories\n\n")

            categories = {
                'Core Infrastructure': [],
                'Agent/Council': [],
                'Security/Crypto': [],
                'Session Management': [],
                'Data/Context': [],
                'URI Scheme': [],
                'Other': []
            }

            for protocol in sorted_protocols:
                name = protocol[0].upper()
                if any(x in name for x in ['TTT', 'GUARD', 'CITATE', 'OPTIMISE']):
                    categories['Core Infrastructure'].append(protocol[0])
                elif any(x in name for x in ['SAM', 'COUNCIL', 'AGENT', 'GUARDIAN']):
                    categories['Agent/Council'].append(protocol[0])
                elif any(x in name for x in ['CRYPTO', 'SECURITY', 'AUTH', 'KEY']):
                    categories['Security/Crypto'].append(protocol[0])
                elif any(x in name for x in ['SESSION', 'INSTANCE', 'CONTEXT']):
                    categories['Session Management'].append(protocol[0])
                elif any(x in name for x in ['FINDING', 'DATA', 'VESICLE', 'PACKET', 'LOGISTICS']):
                    categories['Data/Context'].append(protocol[0])
                elif any(x in name for x in ['IF:', 'URI', 'DID']):
                    categories['URI Scheme'].append(protocol[0])
                else:
                    categories['Other'].append(protocol[0])

            for category, protocols in categories.items():
                if protocols:
                    f.write(f"### {category}\n")
                    for protocol in sorted(protocols):
                        count = self.protocols[protocol]['count']
                        f.write(f"- **{protocol}** ({count} occurrences)\n")
                    f.write("\n")

        print("✓ Report generated successfully")

    def run(self, output_path):
        """Main execution"""
        if not self.connect():
            return False

        self.scan_all_keys()
        self.generate_report(output_path)

        # Print summary
        print("\n" + "="*60)
        print("SCAN COMPLETE")
        print("="*60)
        print(f"Total keys scanned: {self.stats['total_keys_scanned']}")
        print(f"Keys with IF protocols: {self.stats['keys_with_protocols']}")
        print(f"Unique protocols found: {self.stats['total_protocols_found']}")
        print("\nTop 10 protocols by occurrence:")
        sorted_by_count = sorted(self.protocols.items(), key=lambda x: x[1]['count'], reverse=True)
        for i, (protocol, data) in enumerate(sorted_by_count[:10]):
            print(f"  {i+1:2}. {protocol:30} ({data['count']} occurrences)")
        print("="*60)

        return True

if __name__ == '__main__':
    scanner = RedisProtocolScanner()
    output_path = '/home/setup/infrafabric/docs/IF_PROTOCOL_REGISTRY.md'

    success = scanner.run(output_path)

    if success:
        print(f"\n✓ Full report available at: {output_path}")
    else:
        print("\n✗ Scan failed")
        exit(1)
