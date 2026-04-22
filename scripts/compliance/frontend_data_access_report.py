from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VIEW_ROOT = REPO_ROOT / "web" / "frontend" / "src" / "views"
FRONTEND_ROOT = REPO_ROOT / "web" / "frontend" / "src"
DIRECT_API_CLIENT_RE = re.compile(r"import\s+\{?\s*apiClient\s*\}?\s+from\s+['\"].*apiClient")
EMPTY_CATCH_RE = re.compile(r"\.catch\(\s*\(\)\s*=>\s*\{\s*\}\s*\)")


def iter_files(root: Path, suffix: str) -> list[Path]:
    return sorted(path for path in root.rglob(f"*{suffix}") if path.is_file())


def build_report() -> dict[str, object]:
    direct_view_imports: list[str] = []
    empty_catches: list[str] = []

    for file_path in iter_files(VIEW_ROOT, ".vue") + iter_files(VIEW_ROOT, ".ts"):
        content = file_path.read_text(encoding="utf-8")
        if DIRECT_API_CLIENT_RE.search(content):
            direct_view_imports.append(str(file_path.relative_to(REPO_ROOT)))

    for file_path in (
        iter_files(FRONTEND_ROOT, ".ts")
        + iter_files(FRONTEND_ROOT, ".vue")
        + iter_files(FRONTEND_ROOT, ".js")
    ):
        content = file_path.read_text(encoding="utf-8")
        if EMPTY_CATCH_RE.search(content):
            empty_catches.append(str(file_path.relative_to(REPO_ROOT)))

    return {
        "summary": {
            "direct_api_client_imports_in_views": len(direct_view_imports),
            "empty_catch_handlers": len(empty_catches),
        },
        "findings": {
            "direct_api_client_imports_in_views": direct_view_imports,
            "empty_catch_handlers": empty_catches,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Report frontend data-access governance findings.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when findings exist.")
    args = parser.parse_args()

    report = build_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))

    has_findings = any(report["summary"].values())
    if args.strict and has_findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
