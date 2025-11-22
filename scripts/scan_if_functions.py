#!/usr/bin/env python3
"""AST-based scanner for InfraFabric functions and attribute calls."""
import argparse
import ast
import json
from collections import defaultdict
from pathlib import Path


def collect_if_functions(root):
    functions = defaultdict(lambda: {"definitions": [], "calls": defaultdict(int), "called_by": defaultdict(int)})
    attributes = defaultdict(list)
    call_graph = defaultdict(lambda: defaultdict(int))
    scanned_files = 0

    def resolve_name(node):
        parts = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
        return ".".join(reversed(parts)) if parts else None

    class IFVisitor(ast.NodeVisitor):
        def __init__(self, file_path):
            self.file_path = file_path
            self._stack = []

        def _current_function(self):
            return self._stack[-1] if self._stack else "<module>"

        def visit_FunctionDef(self, node):
            self._handle_function(node)

        def visit_AsyncFunctionDef(self, node):
            self._handle_function(node)

        def _handle_function(self, node):
            name = node.name
            if name.startswith("if_"):
                functions[name]["definitions"].append({
                    "file": str(self.file_path),
                    "line": node.lineno,
                })
            self._stack.append(name)
            self.generic_visit(node)
            self._stack.pop()

        def visit_Call(self, node):
            callee = resolve_name(node.func)
            if callee and callee.startswith("if_"):
                caller = self._current_function()
                functions[caller]["calls"][callee] += 1
                functions[callee]["called_by"][caller] += 1
                call_graph[caller][callee] += 1
            self.generic_visit(node)

        def visit_Attribute(self, node):
            if isinstance(node.value, ast.Name) and node.value.id == "if" and node.attr:
                attributes[f"if.{node.attr}"].append({
                    "file": str(self.file_path),
                    "line": node.lineno,
                })
            self.generic_visit(node)

    root_path = Path(root).resolve()
    for path in root_path.rglob("*.py"):
        if "site-packages" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError:
            continue
        visitor = IFVisitor(path.relative_to(root_path))
        visitor.visit(tree)
        scanned_files += 1

    return {
        "root": str(root_path),
        "files_scanned": scanned_files,
        "functions": {
            name: {
                "definitions": data["definitions"],
                "calls": dict(data["calls"]),
                "called_by": dict(data["called_by"]),
            }
            for name, data in functions.items()
        },
        "attributes": dict(attributes),
        "call_graph": {
            caller: dict(callees) for caller, callees in call_graph.items()
        },
    }


def write_dot(call_graph, out_path):
    lines = ["digraph IFGraph {", "  rankdir=LR;"]
    for caller, targets in call_graph.items():
        for callee, count in targets.items():
            lines.append(f"  \"{caller}\" -> \"{callee}\" [label=\"{count}\"];")
    lines.append("}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Scan Infrafabric IF functions and call graph.")
    parser.add_argument("--root", default=".", help="Root directory to scan")
    parser.add_argument("--out-dir", default=".", help="Output directory for index/graphs")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    index = collect_if_functions(args.root)
    index_path = out_dir / "if_index.json"
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

    graph_path = out_dir / "if_graph.json"
    graph_path.write_text(
        json.dumps(index.get("call_graph", {}), indent=2), encoding="utf-8"
    )

    dot_path = out_dir / "if_graph.dot"
    write_dot(index.get("call_graph", {}), dot_path)


if __name__ == "__main__":
    main()
