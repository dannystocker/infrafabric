#!/usr/bin/env python3
"""
Sync Open WebUI conversations to Redis L2 for permanent archival

This script:
1. Connects to Open WebUI's SQLite database
2. Exports all conversations with metadata
3. Archives to Redis L2 (permanent, no TTL)
4. Creates searchable indexes by folder, tag, date
5. Generates conversation summaries for quick reference

Usage:
    python3 openwebui_redis_sync.py [--backup-path /path/to/backup]
"""

import json
import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import hashlib

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.redis_cache_manager import get_redis


class OpenWebUIBackup:
    def __init__(self, webui_data_path: str = None):
        """
        Initialize backup manager

        Args:
            webui_data_path: Path to Open WebUI data directory
                           (default: auto-detect from docker volume)
        """
        self.redis = get_redis()

        # Try to find Open WebUI database
        if webui_data_path:
            self.db_path = Path(webui_data_path) / "webui.db"
        else:
            # Try common locations
            possible_paths = [
                "/var/lib/docker/volumes/open-webui/_data/webui.db",
                "/home/setup/.local/share/open-webui/webui.db",
                Path.home() / ".local/share/open-webui/webui.db"
            ]

            for path in possible_paths:
                if Path(path).exists():
                    self.db_path = Path(path)
                    break
            else:
                raise FileNotFoundError(
                    "Could not find Open WebUI database. "
                    "Please specify --db-path"
                )

        print(f"📂 Using database: {self.db_path}")

    def get_conversations(self) -> List[Dict[str, Any]]:
        """Fetch all conversations from Open WebUI database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()

        # Get all chats
        cursor.execute("""
            SELECT
                id,
                user_id,
                title,
                chat as messages_json,
                created_at,
                updated_at,
                share_id,
                archived
            FROM chat
            ORDER BY updated_at DESC
        """)

        conversations = []
        for row in cursor.fetchall():
            chat_data = {
                'id': row['id'],
                'user_id': row['user_id'],
                'title': row['title'],
                'messages': json.loads(row['messages_json']) if row['messages_json'] else [],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'share_id': row['share_id'],
                'archived': bool(row['archived']),
            }

            # Get tags for this chat
            cursor.execute("""
                SELECT tag_name
                FROM chattag
                WHERE chat_id = ?
            """, (row['id'],))
            chat_data['tags'] = [t['tag_name'] for t in cursor.fetchall()]

            # Extract metadata from messages
            chat_data['metadata'] = self._extract_metadata(chat_data['messages'])

            conversations.append(chat_data)

        conn.close()
        return conversations

    def _extract_metadata(self, messages: List[Dict]) -> Dict[str, Any]:
        """Extract useful metadata from conversation messages"""
        if not messages:
            return {
                'message_count': 0,
                'models_used': [],
                'has_code': False,
                'has_files': False,
                'total_tokens': 0
            }

        models_used = set()
        has_code = False
        has_files = False
        total_tokens = 0

        for msg in messages:
            # Extract model info
            if msg.get('role') == 'assistant' and msg.get('model'):
                models_used.add(msg['model'])

            # Check for code blocks
            if '```' in msg.get('content', ''):
                has_code = True

            # Check for file attachments
            if msg.get('files') or msg.get('attachments'):
                has_files = True

            # Sum tokens if available
            if msg.get('token_count'):
                total_tokens += msg['token_count']

        return {
            'message_count': len(messages),
            'models_used': list(models_used),
            'has_code': has_code,
            'has_files': has_files,
            'total_tokens': total_tokens,
            'first_message_at': messages[0].get('timestamp') if messages else None,
            'last_message_at': messages[-1].get('timestamp') if messages else None
        }

    def backup_to_redis(self, conversations: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Archive conversations to Redis L2

        Returns:
            Statistics about the backup
        """
        stats = {
            'total': len(conversations),
            'backed_up': 0,
            'skipped': 0,
            'errors': 0
        }

        for chat in conversations:
            try:
                chat_id = chat['id']

                # Store full conversation in Redis L2 (permanent, no TTL)
                redis_key = f"openwebui:conversation:{chat_id}"
                self.redis.set(redis_key, json.dumps(chat))

                # Store lightweight metadata for fast queries
                meta_key = f"openwebui:meta:{chat_id}"
                metadata = {
                    'id': chat_id,
                    'title': chat['title'],
                    'tags': chat['tags'],
                    'created_at': chat['created_at'],
                    'updated_at': chat['updated_at'],
                    'archived': chat['archived'],
                    'message_count': chat['metadata']['message_count'],
                    'models_used': chat['metadata']['models_used'],
                    'has_code': chat['metadata']['has_code'],
                    'has_files': chat['metadata']['has_files']
                }
                self.redis.set(meta_key, json.dumps(metadata))

                # Add to indexes for fast searching
                # Index by date (YYYY-MM-DD)
                created_date = chat['created_at'][:10] if chat['created_at'] else 'unknown'
                self.redis.sadd(f"openwebui:index:date:{created_date}", chat_id)

                # Index by tags
                for tag in chat['tags']:
                    self.redis.sadd(f"openwebui:index:tag:{tag}", chat_id)

                # Index by model
                for model in chat['metadata']['models_used']:
                    self.redis.sadd(f"openwebui:index:model:{model}", chat_id)

                # Add to global conversation list
                self.redis.sadd("openwebui:conversations:all", chat_id)

                print(f"✓ Backed up: {chat['title'][:60]}")
                stats['backed_up'] += 1

            except Exception as e:
                print(f"✗ Error backing up conversation {chat.get('id')}: {e}")
                stats['errors'] += 1

        # Store backup timestamp
        backup_meta = {
            'timestamp': datetime.now().isoformat(),
            'total_conversations': stats['total'],
            'backed_up': stats['backed_up'],
            'errors': stats['errors']
        }
        self.redis.set("openwebui:backup:last", json.dumps(backup_meta))

        return stats

    def export_to_files(self, conversations: List[Dict[str, Any]], export_dir: str):
        """
        Export conversations to JSON and Markdown files

        Args:
            conversations: List of conversations to export
            export_dir: Directory to export to
        """
        export_path = Path(export_dir)
        json_dir = export_path / "json"
        md_dir = export_path / "markdown"

        json_dir.mkdir(parents=True, exist_ok=True)
        md_dir.mkdir(parents=True, exist_ok=True)

        for chat in conversations:
            chat_id = chat['id']
            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_'
                                for c in chat['title'])[:100]

            # Export as JSON
            json_file = json_dir / f"{chat_id}_{safe_title}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(chat, f, indent=2, ensure_ascii=False)

            # Export as Markdown
            md_file = md_dir / f"{chat_id}_{safe_title}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(self._conversation_to_markdown(chat))

            print(f"📄 Exported: {safe_title[:60]}")

    def _conversation_to_markdown(self, chat: Dict[str, Any]) -> str:
        """Convert conversation to Markdown format"""
        md = []

        # Header
        md.append(f"# {chat['title']}\n")
        md.append(f"**ID:** {chat['id']}  ")
        md.append(f"**Created:** {chat['created_at']}  ")
        md.append(f"**Updated:** {chat['updated_at']}  ")
        if chat['tags']:
            md.append(f"**Tags:** {', '.join(f'#{tag}' for tag in chat['tags'])}  ")
        md.append(f"**Messages:** {chat['metadata']['message_count']}  ")
        if chat['metadata']['models_used']:
            md.append(f"**Models:** {', '.join(chat['metadata']['models_used'])}  ")
        md.append("\n---\n\n")

        # Messages
        for msg in chat['messages']:
            role = msg.get('role', 'unknown').title()
            timestamp = msg.get('timestamp', 'unknown')
            content = msg.get('content', '')

            md.append(f"## {role} ({timestamp})\n\n")
            md.append(f"{content}\n\n")

            # Add file info if present
            if msg.get('files'):
                md.append("**Attachments:**\n")
                for file in msg['files']:
                    md.append(f"- 📎 {file.get('name', 'unknown')}\n")
                md.append("\n")

            md.append("---\n\n")

        # Footer metadata
        md.append("## Metadata\n\n")
        md.append(f"- **Total Messages:** {chat['metadata']['message_count']}\n")
        md.append(f"- **Models Used:** {', '.join(chat['metadata']['models_used']) if chat['metadata']['models_used'] else 'None'}\n")
        md.append(f"- **Contains Code:** {'Yes' if chat['metadata']['has_code'] else 'No'}\n")
        md.append(f"- **Has Files:** {'Yes' if chat['metadata']['has_files'] else 'No'}\n")
        if chat['metadata']['total_tokens'] > 0:
            md.append(f"- **Total Tokens:** {chat['metadata']['total_tokens']:,}\n")

        return ''.join(md)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Backup Open WebUI conversations to Redis L2 and files"
    )
    parser.add_argument(
        '--db-path',
        help="Path to Open WebUI database directory (auto-detected if not specified)"
    )
    parser.add_argument(
        '--export-dir',
        default="/home/setup/conversation-archives/daily-backups",
        help="Directory to export conversations (default: %(default)s)"
    )
    parser.add_argument(
        '--redis-only',
        action='store_true',
        help="Only backup to Redis, skip file export"
    )
    parser.add_argument(
        '--files-only',
        action='store_true',
        help="Only export files, skip Redis backup"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("OPEN WEBUI BACKUP TO REDIS L2")
    print("=" * 70)
    print()

    try:
        backup = OpenWebUIBackup(webui_data_path=args.db_path)

        # Fetch all conversations
        print("📥 Fetching conversations from Open WebUI database...")
        conversations = backup.get_conversations()
        print(f"✓ Found {len(conversations)} conversations\n")

        if not conversations:
            print("⚠️  No conversations to backup")
            return

        # Backup to Redis L2
        if not args.files_only:
            print("💾 Backing up to Redis L2 (permanent storage)...")
            stats = backup.backup_to_redis(conversations)
            print()
            print(f"✅ Redis L2 Backup Complete:")
            print(f"   Total: {stats['total']}")
            print(f"   Backed up: {stats['backed_up']}")
            print(f"   Errors: {stats['errors']}")
            print()

        # Export to files
        if not args.redis_only:
            print(f"📤 Exporting to {args.export_dir}...")
            backup.export_to_files(conversations, args.export_dir)
            print()
            print(f"✅ File Export Complete:")
            print(f"   JSON files: {args.export_dir}/json/")
            print(f"   Markdown files: {args.export_dir}/markdown/")
            print()

        print("=" * 70)
        print("BACKUP COMPLETE")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
