#!/usr/bin/env python3
"""自动拆分 Python 大文件

基于 AST 分析自动将超标 Python 文件拆分为子模块包。
分组策略：
  - 单个大类(>800行): 按方法分组拆分为 mixin
  - 多个类: 每个类一个文件，小类合并
  - 小节点(dataclass/函数<50行): 合并到同一文件
"""

import argparse
import ast
import os
import re
from pathlib import Path
from typing import List


MIN_GROUP_LINES = 100
MAX_FILE_LINES = 750


def get_import_end(source: str) -> int:
    tree = ast.parse(source)
    last_import_line = 0
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.Expr)):
            end = getattr(node, "end_lineno", node.lineno)
            last_import_line = max(last_import_line, end)
        elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            break
    return last_import_line


def get_top_nodes(source: str) -> List[dict]:
    tree = ast.parse(source)
    nodes = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno)
            is_dataclass = any(
                (isinstance(d, ast.Name) and d.id == "dataclass")
                or (isinstance(d, ast.Attribute) and d.attr == "dataclass")
                for d in getattr(node, "decorator_list", [])
            )
            nodes.append(
                {
                    "name": node.name,
                    "kind": type(node).__name__,
                    "start": node.lineno,
                    "end": end,
                    "size": end - node.lineno + 1,
                    "is_dataclass": is_dataclass,
                },
            )
    return nodes


def group_nodes(nodes: List[dict], threshold: int) -> List[dict]:
    if not nodes:
        return []

    # Single large class — split by methods
    big_classes = [n for n in nodes if n["kind"] == "ClassDef" and n["size"] > threshold]
    if len(big_classes) == 1 and big_classes[0]["size"] > threshold:
        return _split_single_class_strategy(nodes, big_classes[0], threshold)

    # Multiple nodes — group small ones together
    groups = []
    current = {"nodes": [], "size": 0, "label": ""}

    for node in nodes:
        if node["size"] > threshold:
            if current["nodes"]:
                groups.append(current)
            groups.append({"nodes": [node], "size": node["size"], "label": node["name"]})
            current = {"nodes": [], "size": 0, "label": ""}
        elif current["size"] + node["size"] > MAX_FILE_LINES:
            if current["nodes"]:
                groups.append(current)
            current = {"nodes": [node], "size": node["size"], "label": node["name"]}
        else:
            current["nodes"].append(node)
            current["size"] += node["size"]
            if not current["label"]:
                current["label"] = node["name"]
    if current["nodes"]:
        groups.append(current)

    return groups


def _split_single_class_strategy(all_nodes: List[dict], big_class: dict, threshold: int) -> List[dict]:
    groups = []

    # Small nodes before/after the big class go into a "helpers" group
    small_before = [n for n in all_nodes if n["end"] < big_class["start"]]
    small_after = [n for n in all_nodes if n["start"] > big_class["end"]]

    if small_before:
        groups.append(
            {
                "nodes": small_before,
                "size": sum(n["size"] for n in small_before),
                "label": "helpers",
            },
        )

    # The big class itself — split into method groups
    groups.append(
        {
            "nodes": [big_class],
            "size": big_class["size"],
            "label": big_class["name"],
            "needs_method_split": True,
        },
    )

    if small_after:
        groups.append(
            {
                "nodes": small_after,
                "size": sum(n["size"] for n in small_after),
                "label": "utils",
            },
        )

    return groups


def to_snake(name: str) -> str:
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def plan_split(filepath: str, threshold: int = 800, dry_run: bool = True) -> dict:
    with open(filepath) as f:
        source = f.read()
    lines = source.splitlines(keepends=True)

    try:
        ast.parse(source)
    except SyntaxError:
        return {"status": "skip", "reason": "syntax error"}

    import_end = get_import_end(source)
    nodes = get_top_nodes(source)

    if not nodes:
        return {"status": "skip", "reason": "no classes/functions"}

    # Check if file actually needs splitting
    total_lines = len(lines)
    if total_lines <= threshold:
        return {"status": "skip", "reason": f"only {total_lines} lines"}

    groups = group_nodes(nodes, threshold)

    if len(groups) <= 1 and not any(g.get("needs_method_split") for g in groups):
        return {"status": "skip", "reason": "cannot split further"}

    # Generate file plan
    p = Path(filepath)
    pkg_name = to_snake(p.stem)
    pkg_dir = p.parent / pkg_name

    file_plan = []
    for g in groups:
        fname = to_snake(g["label"]) + ".py"
        node_names = [n["name"] for n in g["nodes"]]
        file_plan.append(
            {
                "filename": fname,
                "nodes": node_names,
                "lines": g["size"],
                "needs_method_split": g.get("needs_method_split", False),
            },
        )

    result = {
        "status": "split",
        "original": filepath,
        "original_lines": total_lines,
        "package_dir": str(pkg_dir),
        "import_end": import_end,
        "files": file_plan,
        "file_count": len(file_plan) + 2,  # +__init__.py +wrapper
    }

    if not dry_run:
        execute_split(filepath, lines, import_end, groups, pkg_dir)

    return result


def execute_split(filepath: str, lines: list, import_end: int, groups: list, pkg_dir: Path):
    pkg_dir.mkdir(parents=True, exist_ok=True)
    imports = lines[:import_end]

    created_files = []
    exports = []

    for g in groups:
        fname = to_snake(g["label"]) + ".py"
        fpath = pkg_dir / fname

        content = list(imports) + ["\n"]
        for node in g["nodes"]:
            start_idx = node["start"] - 1
            end_idx = node["end"]
            # Include decorators (lines before the node that start with @)
            while start_idx > 0 and lines[start_idx - 1].strip().startswith("@"):
                start_idx -= 1
            content.extend(lines[start_idx:end_idx])
            content.append("\n\n")

        text = "".join(content)
        try:
            ast.parse(text)
        except SyntaxError:
            print(f"  WARN: {fpath} has syntax error, writing anyway")

        with open(fpath, "w") as f:
            f.write(text)
        created_files.append(fname)

        for node in g["nodes"]:
            if node["kind"] == "ClassDef" or node["kind"] in ("FunctionDef", "AsyncFunctionDef"):
                exports.append((fname, node["name"]))

    # __init__.py
    init_lines = [f'"""{Path(filepath).stem} 拆分包"""\n']
    for fname, name in exports:
        module = fname.replace(".py", "")
        init_lines.append(f"from .{module} import {name}  # noqa: F401\n")
    init_lines.append(f"\n__all__ = {[name for _, name in exports]}\n")

    with open(pkg_dir / "__init__.py", "w") as f:
        f.writelines(init_lines)

    # Backward-compatible wrapper
    p = Path(filepath)
    rel_pkg = pkg_dir.name
    wrapper = f'"""{p.stem} - 向后兼容入口"""\nfrom {rel_pkg} import *  # noqa: F401, F403\n'
    with open(filepath, "w") as f:
        f.write(wrapper)

    print(f"  Split into {len(created_files)} files + __init__.py + wrapper")


def main():
    parser = argparse.ArgumentParser(description="自动拆分 Python 大文件")
    parser.add_argument("--from-backlog", help="从 backlog TSV 读取文件列表")
    parser.add_argument("--wave", default="Wave1")
    parser.add_argument("--priority", default="P2")
    parser.add_argument("--threshold", type=int, default=800)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--files", nargs="*", help="直接指定文件")
    args = parser.parse_args()

    files = []
    if args.from_backlog:
        with open(args.from_backlog) as f:
            for line in f:
                parts = line.strip().split("\t")
                if (
                    len(parts) >= 6
                    and parts[0] == args.wave
                    and parts[1] == "python_source"
                    and parts[2] == args.priority
                ):
                    files.append(parts[5])
    elif args.files:
        files = args.files

    print(f"{'DRY RUN: ' if args.dry_run else ''}Processing {len(files)} files (threshold={args.threshold})")
    print()

    split_count = 0
    skip_count = 0
    for filepath in files:
        if not os.path.exists(filepath):
            print(f"  SKIP: {filepath} (not found)")
            skip_count += 1
            continue

        result = plan_split(filepath, args.threshold, args.dry_run)
        if result["status"] == "skip":
            print(f"  SKIP: {filepath} ({result['reason']})")
            skip_count += 1
        else:
            action = "WOULD SPLIT" if args.dry_run else "SPLIT"
            print(f"  {action}: {filepath} ({result['original_lines']} lines -> {result['file_count']} files)")
            for fp in result["files"]:
                print(f"    {fp['filename']}: {fp['nodes']} ({fp['lines']} lines)")
            split_count += 1
        print()

    print(f"Total: {split_count} split, {skip_count} skipped")


if __name__ == "__main__":
    main()
