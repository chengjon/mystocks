#!/usr/bin/env python3
"""Vue 组件 style 提取工具

将 Vue SFC 中的 <style> 块提取到独立 .scss/.css 文件，
并在原组件中用 @import 引用。
"""

import argparse
import os
import re


def parse_vue_sections(content):
    """解析 Vue SFC，返回各区块的行范围"""
    lines = content.split("\n")
    styles = []
    current_style = None

    for i, line in enumerate(lines):
        style_match = re.match(r"^<style\b([^>]*)>", line)
        if style_match:
            attrs = style_match.group(1)
            scoped = "scoped" in attrs
            lang_match = re.search(r'lang=["\'](\w+)["\']', attrs)
            lang = lang_match.group(1) if lang_match else "css"
            current_style = {"start": i, "scoped": scoped, "lang": lang, "attrs": attrs.strip()}
        elif re.match(r"^</style>", line) and current_style:
            current_style["end"] = i
            current_style["lines"] = i - current_style["start"] - 1
            styles.append(current_style)
            current_style = None

    return lines, styles


def extract_styles(vue_path, dry_run=False, min_lines=50):
    """提取 Vue 文件中的 style 到独立文件"""
    with open(vue_path) as f:
        content = f.read()

    lines, styles = parse_vue_sections(content)
    total = len(lines)

    if not styles:
        return None

    total_style_lines = sum(s["lines"] for s in styles)
    if total_style_lines < min_lines:
        return None

    base_name = os.path.splitext(os.path.basename(vue_path))[0]
    vue_dir = os.path.dirname(vue_path)
    styles_dir = os.path.join(vue_dir, "styles")

    results = []

    for idx, style in enumerate(styles):
        ext = style["lang"] if style["lang"] != "css" else "css"
        if ext == "scss" or ext == "less":
            pass
        else:
            ext = "css"

        suffix = f"_{idx}" if len(styles) > 1 else ""
        style_filename = f"{base_name}{suffix}.{ext}"
        style_path = os.path.join(styles_dir, style_filename)

        style_content = "\n".join(lines[style["start"] + 1 : style["end"]])

        scoped_tag = " scoped" if style["scoped"] else ""
        lang_tag = f' lang="{style["lang"]}"' if style["lang"] != "css" else ""
        import_path = f"./styles/{style_filename}"
        replacement = f'<style{scoped_tag}{lang_tag}>\n@import "{import_path}";\n</style>'

        results.append(
            {
                "style_path": style_path,
                "style_content": style_content,
                "original_start": style["start"],
                "original_end": style["end"],
                "replacement": replacement,
                "lines_saved": style["lines"] - 1,
            },
        )

    if dry_run:
        remaining = total - total_style_lines + len(styles)
        return {
            "file": vue_path,
            "total": total,
            "style_lines": total_style_lines,
            "remaining": remaining,
            "would_pass": remaining <= 500,
            "extractions": len(results),
        }

    # Execute extraction
    os.makedirs(styles_dir, exist_ok=True)

    # Write style files
    for r in results:
        with open(r["style_path"], "w") as f:
            f.write(r["style_content"] + "\n")

    # Rebuild Vue file with @import replacements (process from bottom to top)
    new_lines = lines[:]
    for r in sorted(results, key=lambda x: -x["original_start"]):
        new_lines[r["original_start"] : r["original_end"] + 1] = r["replacement"].split("\n")

    with open(vue_path, "w") as f:
        f.write("\n".join(new_lines))

    remaining = len(new_lines)
    return {
        "file": vue_path,
        "total": total,
        "style_lines": total_style_lines,
        "remaining": remaining,
        "would_pass": remaining <= 500,
        "extractions": len(results),
        "style_files": [r["style_path"] for r in results],
    }


def main():
    parser = argparse.ArgumentParser(description="Vue style 提取工具")
    parser.add_argument("files", nargs="*", help="Vue 文件路径")
    parser.add_argument("--from-backlog", help="从 backlog TSV 读取文件列表")
    parser.add_argument("--wave", default="Wave2")
    parser.add_argument("--min-lines", type=int, default=50, help="最小 style 行数")
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
    skipped = 0
    fixed = 0

    for vue_path in files:
        if not os.path.exists(vue_path):
            continue
        result = extract_styles(vue_path, dry_run=args.dry_run, min_lines=args.min_lines)
        if result is None:
            skipped += 1
            continue

        success += 1
        status = "✅" if result["would_pass"] else "⚠️"
        if result["would_pass"]:
            fixed += 1

        if args.dry_run:
            print(
                f"{status} {result['file']}: {result['total']} -> {result['remaining']} (-{result['style_lines']} style)",
            )
        else:
            print(
                f"{status} {result['file']}: {result['total']} -> {result['remaining']} ({result['extractions']} style files)",
            )

    print(f"\nTotal: {success} extracted, {skipped} skipped, {fixed} now under 500 lines")


if __name__ == "__main__":
    main()
