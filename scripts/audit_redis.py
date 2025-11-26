from typing import List, Tuple

import redis
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def audit(host: str = "localhost", port: int = 6379) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
    """
    Scan Redis for obvious corruption:
    - Literal WRONGTYPE error strings stored as values.
    - Suspicious short error-looking strings.
    """
    r = redis.Redis(host=host, port=port, decode_responses=True)
    console.print(Panel.fit("[bold red]InfraFabric Redis Integrity Scan[/]", subtitle="Checking for 'WRONGTYPE' and corruption"))

    corrupted: List[Tuple[str, str, str]] = []
    suspicious: List[Tuple[str, str, str]] = []

    cursor = 0
    while True:
        cursor, keys = r.scan(cursor=cursor, count=1000)
        for key in keys:
            try:
                dtype = r.type(key)

                # Check 1: literal error strings stored as data
                if dtype == "string":
                    val = r.get(key)
                    if val and "WRONGTYPE" in val:
                        corrupted.append((key, "Stored error message", val[:120]))
                    elif val and "Error" in val and len(val) < 200:
                        suspicious.append((key, "Possible error logged", val[:120]))

                # Check 2: type mismatch flags (extend as schemas are formalized)
                if key.startswith("task:") and dtype not in {"hash", "string"}:
                    suspicious.append((key, f"Unexpected type for task:* ({dtype})", ""))
                if key.startswith("context:"):
                    if dtype == "list":
                        len_list = r.llen(key)
                        suspicious.append((key, f"Legacy Context Log (List, n={len_list})", "Migration required"))
                    elif dtype not in {"string", "hash"}:
                        suspicious.append((key, f"Unexpected type for context:* ({dtype})", ""))

            except Exception as exc:  # noqa: BLE001
                corrupted.append((key, "Read exception", str(exc)))

        if cursor == 0:
            break

    if corrupted:
        table = Table(title="🚨 CORRUPTED KEYS (Must Delete)")
        table.add_column("Key", style="cyan")
        table.add_column("Issue", style="red")
        table.add_column("Content Snippet", style="dim")
        for key, issue, snippet in corrupted:
            table.add_row(key, issue, snippet)
        console.print(table)
        console.print(f"\n[bold red]Action Required:[/] Run `redis-cli DEL {' '.join([k for k, _, _ in corrupted])}`")
    else:
        console.print("[green]No literal 'WRONGTYPE' corruption found.[/]")

    if suspicious:
        table = Table(title=f"⚠️ Suspicious keys ({len(suspicious)})")
        table.add_column("Key", style="yellow")
        table.add_column("Issue", style="yellow")
        table.add_column("Content Snippet", style="dim")
        for key, issue, snippet in suspicious:
            table.add_row(key, issue, snippet)
        console.print(table)
    else:
        console.print("[green]No suspicious keys flagged beyond corruption scan.[/]")

    return corrupted, suspicious


if __name__ == "__main__":
    audit()
