#!/usr/bin/env python3
"""TypeScript 文件自动拆分工具

按 export 声明边界拆分 TS 文件为多个子模块。
支持类型定义文件、composable、工具函数、测试文件。
"""

import argparse
import os
import re


def find_export_blocks(lines):
    """识别 export 声明块的边界"""
    blocks = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("//"):
            i += 1
            continue

        # Detect block start patterns
        is_export = stripped.startswith("export ")
        is_describe = stripped.startswith("describe(") or stripped.startswith("describe('")
        is_block_comment = stripped.startswith("/*")

        if is_export or is_describe:
            block_start = i

            # Handle JSDoc comment before export
            if i > 0 and lines[i - 1].strip().startswith("*/"):
                j = i - 1
                while j >= 0 and not lines[j].strip().startswith("/*"):
                    j -= 1
                if j >= 0:
                    block_start = j
            elif i > 0 and lines[i - 1].strip().startswith("//"):
                j = i - 1
                while j >= 0 and lines[j].strip().startswith("//"):
                    j -= 1
                block_start = j + 1

            # Find block end by tracking braces
            brace_depth = 0
            paren_depth = 0
            block_end = i
            found_open = False

            for j in range(i, n):
                for ch in lines[j]:
                    if ch == "{":
                        brace_depth += 1
                        found_open = True
                    elif ch == "}":
                        brace_depth -= 1
                    elif ch == "(":
                        paren_depth += 1
                    elif ch == ")":
                        paren_depth -= 1

                block_end = j
                # Single-line export (type alias, const without braces)
                if not found_open and lines[j].rstrip().endswith(";"):
                    break
                # Multi-line block closed
                if found_open and brace_depth == 0:
                    break

            # Extract name
            name = "unknown"
            m = re.search(
                r"export\s+(?:default\s+)?(?:interface|type|enum|class|function|const|let|async\s+function)\s+(\w+)",
                lines[i],
            )
            if m:
                name = m.group(1)
            elif is_describe:
                m = re.search(r"describe\(['\"](.+?)['\"]", lines[i])
                if m:
                    name = m.group(1).replace(" ", "_")

            kind = "unknown"
            if "interface " in lines[i]:
                kind = "interface"
            elif "type " in lines[i]:
                kind = "type"
            elif "enum " in lines[i]:
                kind = "enum"
            elif "class " in lines[i]:
                kind = "class"
            elif "function " in lines[i] or "async function" in lines[i]:
                kind = "function"
            elif "const " in lines[i]:
                kind = "const"
            elif is_describe:
                kind = "describe"

            size = block_end - block_start + 1
            blocks.append(
                {
                    "name": name,
                    "kind": kind,
                    "start": block_start,
                    "end": block_end,
                    "size": size,
                },
            )
            i = block_end + 1
        else:
            i += 1

    return blocks


def get_imports_section(lines):
    """提取 import 语句区域"""
    import_end = 0
    i = 0
    n = len(lines)

    while i < n:
        stripped = lines[i].strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            # Multi-line import
            while (
                i < n
                and not lines[i].rstrip().endswith(";")
                and not lines[i].rstrip().endswith("'")
                and not lines[i].rstrip().endswith('"')
            ):
                i += 1
            import_end = i + 1
            i += 1
        elif stripped == "" or stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            if import_end > 0:
                i += 1
                continue
            i += 1
        elif (
            stripped.startswith("export")
            or stripped.startswith("describe")
            or stripped.startswith("const")
            or stripped.startswith("interface")
            or stripped.startswith("type ")
            or stripped.startswith("enum ")
        ):
            break
        else:
            i += 1

    return import_end


def group_blocks(blocks, threshold):
    """将小块合并为不超过阈值的分组"""
    groups = []
    current_group = []
    current_size = 0

    for block in blocks:
        if block["size"] > threshold:
            if current_group:
                groups.append(current_group)
                current_group = []
                current_size = 0
            groups.append([block])
        elif current_size + block["size"] > threshold:
            if current_group:
                groups.append(current_group)
            current_group = [block]
            current_size = block["size"]
        else:
            current_group.append(block)
            current_size += block["size"]

    if current_group:
        groups.append(current_group)

    return groups


def make_group_filename(group, index):
    """生成分组文件名"""
    kinds = set(b["kind"] for b in group)
    names = [b["name"] for b in group]

    if len(group) == 1:
        name = names[0]
        kind = group[0]["kind"]
        # CamelCase -> kebab-case
        kebab = re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()
        return f"{kebab}.ts"

    if kinds == {"interface"} or kinds == {"type"} or kinds <= {"interface", "type"}:
        return f"types-{index}.ts"
    if kinds == {"function"} or kinds == {"const"} or kinds <= {"function", "const"}:
        return f"functions-{index}.ts"
    if "describe" in kinds:
        return f"tests-{index}.ts"
    return f"part-{index}.ts"


def split_ts_file(filepath, threshold=500, dry_run=False):
    """拆分单个 TS 文件"""
    with open(filepath) as f:
        lines = f.readlines()

    total = len(lines)
    if total <= threshold:
        return False, "under threshold"

    blocks = find_export_blocks(lines)
    if len(blocks) <= 1:
        return False, "single block, cannot split"

    import_end = get_imports_section(lines)
    imports = lines[:import_end]

    groups = group_blocks(blocks, threshold - len(imports) - 10)
    if len(groups) <= 1:
        return False, "all blocks fit in one group"

    basename = os.path.basename(filepath)
    stem = os.path.splitext(basename)[0]
    parent = os.path.dirname(filepath)
    pkg_dir = os.path.join(parent, stem)

    if dry_run:
        print(f"  WOULD split {basename} ({total} lines) into {len(groups)} files:")
        for i, group in enumerate(groups):
            gname = make_group_filename(group, i + 1)
            gsize = sum(b["size"] for b in group) + len(imports)
            names = [b["name"] for b in group[:3]]
            suffix = f" +{len(group) - 3} more" if len(group) > 3 else ""
            print(f"    {gname} (~{gsize} lines): {', '.join(names)}{suffix}")
        return True, "would split"

    os.makedirs(pkg_dir, exist_ok=True)

    # Write split files
    index_exports = []
    for i, group in enumerate(groups):
        gname = make_group_filename(group, i + 1)
        gpath = os.path.join(pkg_dir, gname)

        with open(gpath, "w") as f:
            f.writelines(imports)
            f.write("\n")
            for block in group:
                f.writelines(lines[block["start"] : block["end"] + 1])
                f.write("\n")

        # Collect exports for index
        for block in group:
            if block["kind"] in ("interface", "type", "enum", "class", "function", "const"):
                index_exports.append((gname, block["name"], block["kind"]))

    # Write index.ts
    index_path = os.path.join(pkg_dir, "index.ts")
    with open(index_path, "w") as f:
        seen_files = []
        for gname, name, kind in index_exports:
            if gname not in seen_files:
                seen_files.append(gname)
        for gname in seen_files:
            names = [n for g, n, k in index_exports if g == gname]
            gstem = os.path.splitext(gname)[0]
            f.write(f"export {{ {', '.join(names)} }} from './{gstem}';\n")

    # Replace original with re-export
    with open(filepath, "w") as f:
        f.write(f"// 向后兼容入口 - 实际实现已拆分至 ./{stem}/\n")
        f.write(f"export * from './{stem}';\n")

    return True, f"split into {len(groups)} files"


def main():
    parser = argparse.ArgumentParser(description="TypeScript 文件自动拆分")
    parser.add_argument("--from-backlog", help="从 backlog TSV 读取文件列表")
    parser.add_argument("--wave", default="Wave3", help="Wave 过滤")
    parser.add_argument("--threshold", type=int, default=500)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--files", nargs="*", help="直接指定文件")
    args = parser.parse_args()

    files = []
    if args.from_backlog:
        with open(args.from_backlog) as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 6 and parts[0] == args.wave:
                    files.append(parts[5])
    if args.files:
        files.extend(args.files)

    # Also add files from inventory
    inv_path = "reports/plans/inventory/ts_gt500.tsv"
    if os.path.exists(inv_path) and not args.files:
        with open(inv_path) as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    path = parts[1]
                    if path not in files:
                        files.append(path)

    split_count = 0
    skip_count = 0

    for filepath in files:
        if not os.path.exists(filepath):
            continue
        with open(filepath) as f:
            total = len(f.readlines())
        if total <= args.threshold:
            continue

        name = os.path.basename(filepath)
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Processing {name} ({total} lines):")

        ok, msg = split_ts_file(filepath, args.threshold, args.dry_run)
        if ok:
            split_count += 1
            if not args.dry_run:
                print(f"  ✅ {msg}")
        else:
            skip_count += 1
            print(f"  ⏭️ Skip: {msg}")

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Done: {split_count} split, {skip_count} skipped")


if __name__ == "__main__":
    main()
