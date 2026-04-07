from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.markdown_governance import (
    BOUNDARY_NOTE_PATTERN,
    BOUNDARY_NOTE_PRESETS,
    BOUNDARY_NOTE_TITLES,
    recommend_boundary_note_preset,
)


def build_boundary_note(preset: str, title_override: str | None = None) -> str:
    config = BOUNDARY_NOTE_PRESETS[preset]
    title = title_override or config["title"]
    if title not in BOUNDARY_NOTE_TITLES:
        allowed_titles = ", ".join(BOUNDARY_NOTE_TITLES)
        raise ValueError(f"unsupported boundary note title: {title}. Allowed titles: {allowed_titles}")
    lines = [f"> **{title}**:"] + [f"> {line}" for line in config["body_lines"]]
    return "\n".join(lines)


def has_boundary_note(content: str) -> bool:
    return bool(BOUNDARY_NOTE_PATTERN.search(content))


def find_front_matter_end(lines: list[str]) -> int | None:
    if not lines or lines[0].strip() != "---":
        return None

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return index
    return None


def replace_existing_boundary_note(content: str, boundary_note: str) -> str:
    lines = content.splitlines()
    start_index = None

    for index, line in enumerate(lines):
        if BOUNDARY_NOTE_PATTERN.match(line):
            start_index = index
            break

    if start_index is None:
        return content

    end_index = start_index + 1
    while end_index < len(lines) and lines[end_index].startswith(">"):
        end_index += 1

    updated_lines = lines[:start_index] + boundary_note.splitlines() + lines[end_index:]
    return "\n".join(updated_lines) + ("\n" if content.endswith("\n") else "")


def insert_boundary_note(content: str, boundary_note: str) -> str:
    lines = content.splitlines()
    front_matter_end = find_front_matter_end(lines)
    search_start = (front_matter_end + 1) if front_matter_end is not None else 0
    insert_after = front_matter_end

    for index in range(search_start, len(lines)):
        line = lines[index]
        if line.startswith("#"):
            insert_after = index
            break

    if insert_after is None:
        prefix = boundary_note + "\n\n"
        return prefix + content.lstrip("\n")

    before = lines[: insert_after + 1]
    after = lines[insert_after + 1 :]
    inserted = before + ["", *boundary_note.splitlines(), ""]
    if after and after[0] == "":
        return "\n".join(inserted + after[1:]) + ("\n" if content.endswith("\n") else "")
    return "\n".join(inserted + after) + ("\n" if content.endswith("\n") else "")


def apply_boundary_note(file_path: Path, preset: str, title_override: str | None, replace_existing: bool) -> str:
    content = file_path.read_text(encoding="utf-8")
    resolved_preset = recommend_boundary_note_preset(file_path.as_posix()) if preset == "auto" else preset
    boundary_note = build_boundary_note(resolved_preset, title_override)

    if has_boundary_note(content):
        if not replace_existing:
            return "skipped"
        updated = replace_existing_boundary_note(content, boundary_note)
        file_path.write_text(updated, encoding="utf-8")
        return "replaced"

    updated = insert_boundary_note(content, boundary_note)
    file_path.write_text(updated, encoding="utf-8")
    return "inserted"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Insert or replace canonical markdown boundary notes")
    parser.add_argument("filenames", nargs="*")
    parser.add_argument("--path", action="append")
    parser.add_argument("--preset", choices=(*BOUNDARY_NOTE_PRESETS.keys(), "auto"), required=True)
    parser.add_argument("--title")
    parser.add_argument("--replace-existing", action="store_true")
    args = parser.parse_args(argv)

    target_paths = [*(args.path or []), *args.filenames]
    if not target_paths:
        parser.error("at least one markdown path is required")

    exit_code = 0
    for raw_path in target_paths:
        file_path = Path(raw_path)
        if not file_path.exists():
            print(f"ERROR {file_path}: file not found")
            exit_code = 1
            continue
        if file_path.suffix != ".md":
            print(f"ERROR {file_path}: expected a .md file")
            exit_code = 1
            continue

        try:
            result = apply_boundary_note(file_path, args.preset, args.title, args.replace_existing)
        except ValueError as exc:
            print(f"ERROR {file_path}: {exc}")
            exit_code = 1
            continue
        print(f"{result.upper()} {file_path}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
