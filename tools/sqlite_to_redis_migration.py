#!/usr/bin/env python3
"""
SQLite to Redis Cloud Migration Tool
Migrates IF.* components from SQLite to Redis Cloud

Usage:
    python sqlite_to_redis_migration.py \
      --sqlite-db /tmp/infrafabric-sqlite/infrafabric_knowledge.db \
      --redis-host redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com \
      --redis-port 19956 \
      --redis-password <password> \
      --redis-db 0
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List

import redis
import yaml


class SQLiteToRedismigrator:
    """Migrate components from SQLite to Redis Cloud."""

    def __init__(
        self,
        sqlite_path: str,
        redis_host: str,
        redis_port: int,
        redis_password: str | None = None,
        redis_db: int = 0,
    ):
        self.sqlite_path = sqlite_path
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.redis_db = redis_db

        self.components: List[Dict[str, Any]] = []
        self.categories: set[str] = set()
        self.errors: List[str] = []
        self.pushed_count = 0

    def init_sqlite(self) -> None:
        """Initialize SQLite database with components table if it doesn't exist."""
        Path(self.sqlite_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()

        # Create components table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                status TEXT,
                category TEXT,
                source_file_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create file index table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                component_count INTEGER DEFAULT 0
            )
        """
        )

        conn.commit()
        conn.close()

    def load_components_from_yaml(self, yaml_path: str) -> None:
        """Load components from YAML inventory."""
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        for component in data.get("components", {}).get("implemented", []):
            self._add_component(component, "implemented")

        for component in data.get("components", {}).get("partial", []):
            self._add_component(component, "partial")

        for component in data.get("components", {}).get("vaporware", []):
            self._add_component(component, "vaporware")

    def _add_component(self, component: Dict[str, Any], status: str) -> None:
        """Add component to list."""
        name = component.get("name", "")
        description = component.get("status", "")
        source_files = component.get("evidence", [])
        source_file_id = source_files[0] if source_files else None

        self.components.append({
            "name": name,
            "description": description,
            "status": status,
            "category": self._infer_category(name),
            "source_file_id": source_file_id,
        })

        self.categories.add(self._infer_category(name))

    def _infer_category(self, component_name: str) -> str:
        """Infer category from component name."""
        if "guard" in component_name.lower():
            return "governance"
        elif "security" in component_name.lower() or "yolo" in component_name.lower():
            return "security"
        elif "memory" in component_name.lower() or "trace" in component_name.lower():
            return "state"
        elif "optimize" in component_name.lower():
            return "optimization"
        elif "search" in component_name.lower():
            return "discovery"
        elif "ground" in component_name.lower():
            return "foundations"
        else:
            return "general"

    def populate_sqlite(self) -> None:
        """Populate SQLite with components."""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()

        for comp in self.components:
            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO components
                    (name, description, status, category, source_file_id)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        comp["name"],
                        comp["description"],
                        comp["status"],
                        comp["category"],
                        comp["source_file_id"],
                    ),
                )
            except sqlite3.IntegrityError as e:
                self.errors.append(f"SQLite insert error for {comp['name']}: {e}")

        conn.commit()
        conn.close()

    def connect_redis(self) -> redis.Redis:
        """Connect to Redis Cloud."""
        try:
            r = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                db=self.redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            r.ping()
            return r
        except Exception as e:
            self.errors.append(f"Redis connection failed: {e}")
            raise

    def migrate_to_redis(self) -> None:
        """Migrate components from SQLite to Redis."""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()

        # Fetch all components
        cursor.execute("SELECT name, description, status, category, source_file_id FROM components")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.errors.append("No components found in SQLite")
            return

        try:
            r = self.connect_redis()
        except Exception as e:
            self.errors.append(f"Failed to connect to Redis: {e}")
            return

        file_components: Dict[str, set] = {}

        for name, description, status, category, source_file_id in rows:
            try:
                # Create component hash
                component_key = f"if:component:{name}"
                component_data = {
                    "name": name,
                    "description": description,
                    "status": status,
                    "category": category,
                    "source_file_id": source_file_id or "",
                }

                # Set component hash
                r.hset(component_key, mapping=component_data)

                # Track file index
                if source_file_id:
                    if source_file_id not in file_components:
                        file_components[source_file_id] = set()
                    file_components[source_file_id].add(name)

                self.pushed_count += 1

            except Exception as e:
                self.errors.append(f"Failed to push {name} to Redis: {e}")

        # Create reverse indexes
        try:
            # All components index
            all_components = [row[0] for row in rows]
            if all_components:
                r.sadd("if:components:all", *all_components)

            # Category indexes
            for category in self.categories:
                category_key = f"if:components:category:{category}"
                category_components = [
                    row[0] for row in rows if row[3] == category
                ]
                if category_components:
                    r.sadd(category_key, *category_components)

            # File indexes
            for source_file_id, components in file_components.items():
                file_key = f"if:file:{source_file_id}:components"
                if components:
                    r.sadd(file_key, *components)

        except Exception as e:
            self.errors.append(f"Failed to create indexes: {e}")

    def generate_summary(self) -> Dict[str, Any]:
        """Generate migration summary."""
        indexes = [
            "if:components:all",
            *[f"if:components:category:{cat}" for cat in sorted(self.categories)],
        ]
        return {
            "components_pushed": self.pushed_count,
            "categories": sorted(self.categories),
            "errors": self.errors,
            "sample_keys": [
                "if:component:IF.guard",
                "if:component:IF.ceo",
                "if:component:IF.yologuard",
                "if:components:all",
                "if:components:category:governance",
            ],
            "indexes_created": indexes,
        }


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate IF components to Redis Cloud")
    parser.add_argument("--sqlite-db", required=True, help="Path to SQLite database")
    parser.add_argument("--redis-host", required=True, help="Redis host")
    parser.add_argument("--redis-port", type=int, default=19956, help="Redis port")
    parser.add_argument("--redis-password", help="Redis password")
    parser.add_argument("--redis-db", type=int, default=0, help="Redis database")
    parser.add_argument("--yaml-inventory", help="YAML component inventory file")

    args = parser.parse_args()

    # Create migrator
    migrator = SQLiteToRedismigrator(
        sqlite_path=args.sqlite_db,
        redis_host=args.redis_host,
        redis_port=args.redis_port,
        redis_password=args.redis_password,
        redis_db=args.redis_db,
    )

    # Initialize SQLite
    print("Initializing SQLite database...")
    migrator.init_sqlite()

    # Load components from YAML
    if args.yaml_inventory:
        print(f"Loading components from {args.yaml_inventory}...")
        migrator.load_components_from_yaml(args.yaml_inventory)

        # Populate SQLite
        print("Populating SQLite...")
        migrator.populate_sqlite()

    # Migrate to Redis
    print("Migrating to Redis Cloud...")
    migrator.migrate_to_redis()

    # Generate and print summary
    summary = migrator.generate_summary()
    print("\nMigration Summary:")
    print(json.dumps(summary, indent=2))

    # Exit with error code if there were errors
    if migrator.errors:
        print("\nErrors encountered:")
        for error in migrator.errors:
            print(f"  - {error}")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
