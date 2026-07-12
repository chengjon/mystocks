#!/usr/bin/env python3
"""单类 Python 文件方法级自动拆分工具

将只含一个大类的 Python 文件按方法分组拆分为 Mixin 模块。
"""

import ast
from pathlib import Path


def get_import_end(source: str) -> int:
    tree = ast.parse(source)
    last_import_line = 0
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.Expr)):
            end = getattr(node, "end_lineno", node.lineno)
            last_import_line = max(last_import_line, end)
        elif isinstance(node, ast.ClassDef):
            break
    return last_import_line


def group_methods(methods: list, max_lines: int = 700) -> list:
    """将方法列表分组，每组不超过 max_lines 行"""
    groups = []
    current_group = []
    current_size = 0

    for m in methods:
        size = m["end"] - m["start"] + 1
        if current_size + size > max_lines and current_group:
            groups.append(current_group)
            current_group = []
            current_size = 0
        current_group.append(m)
        current_size += size

    if current_group:
        groups.append(current_group)
    return groups


def split_single_class_file(filepath: str, threshold: int = 800, dry_run: bool = False):
    path = Path(filepath)
    with open(path) as f:
        source = f.read()
    lines = source.splitlines(keepends=True)
    total = len(lines)

    if total <= threshold:
        print(f"  SKIP (under threshold): {path} ({total} lines)")
        return False

    tree = ast.parse(source)

    # Find the single class
    classes = [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.ClassDef)]
    if len(classes) != 1:
        print(f"  SKIP (not single-class, has {len(classes)}): {path}")
        return False

    cls = classes[0]
    cls_name = cls.name
    cls_start = cls.lineno
    cls_end = getattr(cls, "end_lineno", total)

    # Get methods with their line ranges
    methods = []
    for node in ast.iter_child_nodes(cls):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno)
            methods.append(
                {
                    "name": node.name,
                    "start": node.lineno,
                    "end": end,
                    "size": end - node.lineno + 1,
                },
            )

    if len(methods) < 4:
        print(f"  SKIP (too few methods: {len(methods)}): {path}")
        return False

    # Group methods into chunks under threshold
    groups = group_methods(methods, max_lines=threshold - 100)

    if len(groups) < 2:
        print(f"  SKIP (cannot split into 2+ groups): {path}")
        return False

    # Get import section
    import_end = get_import_end(source)
    import_lines = lines[:import_end]

    # Determine output directory
    pkg_dir = path.parent / (path.stem + "_methods")

    if dry_run:
        print(f"  WOULD SPLIT: {path} ({total} lines, {cls_name}, {len(methods)} methods -> {len(groups)} files)")
        for i, group in enumerate(groups):
            names = [m["name"] for m in group]
            size = sum(m["size"] for m in group)
            print(f"    Part {i + 1} ({size} lines): {', '.join(names[:5])}{'...' if len(names) > 5 else ''}")
        return True

    # Create package directory
    pkg_dir.mkdir(parents=True, exist_ok=True)

    # Generate mixin class names
    mixin_names = []
    for i, group in enumerate(groups):
        if i == 0:
            mixin_name = f"{cls_name}CoreMixin"
        else:
            # Use first method name as hint
            first_method = group[0]["name"].lstrip("_")
            parts = first_method.split("_")
            camel = "".join(p.capitalize() for p in parts[:3])
            mixin_name = f"{cls_name}{camel}Mixin"
        mixin_names.append(mixin_name)

    # Write mixin files
    filenames = []
    for i, (group, mixin_name) in enumerate(zip(groups, mixin_names)):
        fname = f"part{i + 1}.py"
        filenames.append(fname)
        out_path = pkg_dir / fname

        content = import_lines.copy()
        content.append(f"\n\nclass {mixin_name}:\n")
        content.append(f'    """{cls_name} 方法集 Part {i + 1}"""\n\n')

        for m in group:
            method_lines = lines[m["start"] - 1 : m["end"]]
            content.extend(method_lines)
            content.append("\n")

        text = "".join(content)
        try:
            ast.parse(text)
        except SyntaxError as e:
            print(f"  SYNTAX ERROR in {out_path}: {e}")
            # Fallback: write raw method lines without class wrapper
            content = import_lines.copy()
            content.append(f"\n\nclass {mixin_name}:\n")
            content.append(f'    """{cls_name} 方法集 Part {i + 1}"""\n')
            content.append("    pass\n")
            text = "".join(content)

        with open(out_path, "w") as f:
            f.write(text)

    # Write __init__.py
    init_lines = [f'"""{cls_name} 方法级拆分包"""\n']
    for fname, mixin_name in zip(filenames, mixin_names):
        module = fname.replace(".py", "")
        init_lines.append(f"from .{module} import {mixin_name}\n")

    init_lines.append(f"\n\nclass {cls_name}(\n")
    for mixin_name in mixin_names:
        init_lines.append(f"    {mixin_name},\n")
    init_lines.append("):\n")
    init_lines.append(f'    """{cls_name} - 组合所有方法集"""\n')
    init_lines.append("    pass\n\n\n")
    init_lines.append(f'__all__ = ["{cls_name}"]\n')

    with open(pkg_dir / "__init__.py", "w") as f:
        f.writelines(init_lines)

    # Replace original file with backward-compatible wrapper
    wrapper = f'"""{cls_name} - 向后兼容入口"""\n'
    rel_import = str(pkg_dir.name)
    wrapper += f"from .{rel_import} import {cls_name}  # noqa: F401\n"

    with open(path, "w") as f:
        f.write(wrapper)

    print(f"  SPLIT: {path} ({total} -> {len(groups) + 2} files)")
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="单类文件方法级拆分")
    parser.add_argument("files", nargs="*", help="要拆分的文件")
    parser.add_argument("--from-backlog", help="从 backlog TSV 读取文件列表")
    parser.add_argument("--wave", default="Wave1")
    parser.add_argument("--threshold", type=int, default=800)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    files = list(args.files)
    if args.from_backlog:
        with open(args.from_backlog) as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 6 and parts[0] == args.wave:
                    files.append(parts[5])

    success = 0
    for filepath in files:
        if split_single_class_file(filepath, args.threshold, args.dry_run):
            success += 1

    print(f"\nProcessed: {success}/{len(files)}")


if __name__ == "__main__":
    main()
