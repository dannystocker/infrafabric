from datetime import datetime

import redis
from rich.console import Console
from rich.prompt import Confirm

from infrafabric.state.schema import ContextSchema


console = Console()


def migrate(host: str = "localhost", port: int = 6379) -> None:
    """Convert legacy context lists to ContextSchema JSON strings."""
    console.rule("[bold magenta]Legacy Context Migration[/]")
    r = redis.Redis(host=host, port=port, decode_responses=True)

    legacy_keys = [k for k in r.keys("context:*") if r.type(k) == "list"]
    if not legacy_keys:
        console.print("[green]No legacy context lists found. State is clean.[/]")
        return

    console.print(f"[yellow]Found {len(legacy_keys)} legacy context lists to migrate.[/]")

    for key in legacy_keys:
        items = r.lrange(key, 0, -1)
        summary_text = "\n".join(items)
        tokens_est = max(1, len(summary_text) // 4)
        new_state = ContextSchema(
            instance_id="legacy_migration",
            tokens_used=tokens_est,
            summary=f"MIGRATED FROM LIST AT {datetime.now().isoformat()}:\n{summary_text[:4000]}",
        )

        console.print(f"\n[yellow]Key:[/] {key}")
        console.print(f"[dim]Items: {len(items)}. Will overwrite as ContextSchema string.[/]")

        if Confirm.ask(f"Overwrite {key} (list) with ContextSchema JSON?"):
            r.delete(key)
            r.set(key, new_state.to_redis())
            console.print("[green]Migrated.[/]")
        else:
            console.print("[red]Skipped.[/]")


if __name__ == "__main__":
    migrate()
