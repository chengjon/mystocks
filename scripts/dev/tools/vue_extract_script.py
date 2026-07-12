#!/usr/bin/env python3
"""Vue script 提取工具 - 将 <script setup> 内容提取到 composable 文件"""

import argparse
import os
import re


def parse_vue_file(path):
    """解析 Vue 文件，返回各区块内容和行号"""
    with open(path) as f:
        lines = f.readlines()

    sections = []
    current_type = None
    current_start = None
    current_attrs = ""

    for i, line in enumerate(lines):
        m = re.match(r"^<(template|script|style)(.*)>", line)
        if m:
            current_type = m.group(1)
            current_attrs = m.group(2).strip()
            current_start = i
            continue

        m_end = re.match(r"^</(template|script|style)>", line)
        if m_end and current_type == m_end.group(1):
            sections.append(
                {
                    "type": current_type,
                    "attrs": current_attrs,
                    "start": current_start,
                    "end": i,
                    "content": lines[current_start + 1 : i],
                },
            )
            current_type = None

    return lines, sections


def extract_script_to_composable(path, dry_run=False):
    """提取 script setup 内容到 composable 文件"""
    lines, sections = parse_vue_file(path)
    total = len(lines)

    script_section = None
    for s in sections:
        if s["type"] == "script" and "setup" in s["attrs"]:
            script_section = s
            break

    if not script_section:
        return None, "no <script setup> found"

    script_lines = script_section["content"]
    script_size = len(script_lines)

    if script_size < 50:
        return None, f"script too small ({script_size} lines)"

    remaining = total - script_size + 15  # ~15 lines for composable import
    if remaining > 500:
        return None, f"still {remaining} lines after extraction"

    # Parse script content
    imports = []
    body = []
    vue_imports = []

    for line in script_lines:
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from ") or re.match(r"^(type|interface)\s", stripped):
            imports.append(line)
        else:
            body.append(line)

    # Separate Vue imports from other imports
    for imp in imports:
        if "'vue'" in imp or '"vue"' in imp:
            vue_imports.append(imp)

    if not body or len(body) < 30:
        return None, f"body too small ({len(body)} lines)"

    # Generate composable name
    basename = os.path.splitext(os.path.basename(path))[0]
    composable_name = f"use{basename}"
    composable_dir = os.path.join(os.path.dirname(path), "composables")
    composable_path = os.path.join(composable_dir, f"{composable_name}.ts")

    # Find all top-level const/let/function declarations for return statement
    exports = []
    for line in body:
        m = re.match(r"^(?:const|let|var)\s+(\w+)", line.strip())
        if m:
            exports.append(m.group(1))
        m = re.match(r"^(?:async\s+)?function\s+(\w+)", line.strip())
        if m:
            exports.append(m.group(1))

    # Build composable file content
    composable_content = []
    composable_content.extend(imports)
    composable_content.append("\n")
    composable_content.append(f"export function {composable_name}() {{\n")
    composable_content.extend(body)
    if exports:
        composable_content.append("\n")
        composable_content.append("  return {\n")
        for exp in exports:
            composable_content.append(f"    {exp},\n")
        composable_content.append("  }\n")
    composable_content.append("}\n")

    # Build new script section
    new_script = []
    # Keep non-Vue imports
    for imp in imports:
        if "'vue'" not in imp and '"vue"' not in imp:
            # Only keep component imports
            if "import " in imp and (".vue" in imp or "components" in imp):
                new_script.append(imp)
    new_script.append(f"import {{ {composable_name} }} from './composables/{composable_name}'\n")
    new_script.append("\n")
    if exports:
        destructure = ", ".join(exports)
        new_script.append(f"const {{ {destructure} }} = {composable_name}()\n")

    # Rebuild Vue file
    new_lines = []
    new_lines.extend(lines[: script_section["start"]])
    new_lines.append(
        f"<script setup{' ' + script_section['attrs'] if script_section['attrs'] != 'setup' else ' setup'}>\n"
        if "lang" in script_section["attrs"]
        else "<script setup>\n",
    )
    # Preserve lang="ts" if present
    if "lang" in script_section["attrs"]:
        tag = f"<script {script_section['attrs']}>\n"
    else:
        tag = "<script setup>\n"
    new_lines[-1] = tag
    new_lines.extend(new_script)
    new_lines.append("</script>\n")
    new_lines.extend(lines[script_section["end"] + 1 :])

    result = {
        "original": total,
        "new_vue": len(new_lines),
        "composable": len(composable_content),
        "composable_path": composable_path,
        "script_extracted": script_size,
    }

    if not dry_run:
        os.makedirs(composable_dir, exist_ok=True)
        with open(composable_path, "w") as f:
            f.writelines(composable_content)
        with open(path, "w") as f:
            f.writelines(new_lines)

    return result, None


def main():
    parser = argparse.ArgumentParser(description="Vue script 提取工具")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--from-backlog", help="Backlog TSV file")
    parser.add_argument("--wave", default="Wave2")
    parser.add_argument("--files", nargs="*", help="Specific files")
    parser.add_argument("--min-script", type=int, default=50)
    args = parser.parse_args()

    files = []
    if args.from_backlog:
        with open(args.from_backlog) as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 6 and parts[0] == args.wave:
                    files.append(parts[5])
    elif args.files:
        files = args.files

    # Filter to only existing Vue files still over 500 lines
    targets = []
    for f in files:
        if os.path.exists(f) and f.endswith(".vue"):
            with open(f) as fh:
                lc = sum(1 for _ in fh)
            if lc > 500:
                targets.append((lc, f))

    targets.sort(reverse=True)

    extracted = 0
    fixed = 0
    skipped = 0

    prefix = "[DRY RUN] " if args.dry_run else ""

    for lc, path in targets:
        result, err = extract_script_to_composable(path, dry_run=args.dry_run)
        name = os.path.basename(path)
        if err:
            print(f"  SKIP {name} ({lc} lines): {err}")
            skipped += 1
        else:
            marker = "✅" if result["new_vue"] <= 500 else "⚠️"
            print(
                f"  {prefix}{marker} {name}: {result['original']} -> {result['new_vue']} lines "
                f"(extracted {result['script_extracted']} lines to composable)",
            )
            extracted += 1
            if result["new_vue"] <= 500:
                fixed += 1

    print(f"\n{prefix}Summary: {extracted} extracted, {fixed} fixed (<=500), {skipped} skipped")


if __name__ == "__main__":
    main()
