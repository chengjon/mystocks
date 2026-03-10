from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_APP_FILE = PROJECT_ROOT / "web" / "frontend" / "src" / "App.vue"

HTML_TAGS = {
    "a",
    "article",
    "aside",
    "button",
    "div",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "img",
    "input",
    "label",
    "li",
    "main",
    "nav",
    "ol",
    "p",
    "section",
    "span",
    "strong",
    "table",
    "tbody",
    "td",
    "template",
    "textarea",
    "th",
    "thead",
    "tr",
    "ul",
}

ALLOWED_VUE_TAGS = {
    "component",
    "keep-alive",
    "router-view",
    "slot",
    "suspense",
    "teleport",
    "transition",
    "transition-group",
}

FORBIDDEN_IMPORT_MARKERS = (
    "/views/",
    "/components/",
    "/layouts/",
)

TAG_PATTERN = re.compile(r"<\s*([A-Za-z][\w-]*)\b")
IMPORT_PATTERN = re.compile(r"""from\s+['"]([^'"]+)['"]""")
TEMPLATE_BLOCK_PATTERN = re.compile(r"<template\b[^>]*>(?P<content>.*?)</template>", re.DOTALL | re.IGNORECASE)
SCRIPT_BLOCK_PATTERN = re.compile(r"<script\b[^>]*>(?P<content>.*?)</script>", re.DOTALL | re.IGNORECASE)


def _normalize_target(path_value: str | None) -> Path:
    if not path_value:
        return DEFAULT_APP_FILE

    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    return candidate.resolve()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_template_content(content: str) -> str:
    match = TEMPLATE_BLOCK_PATTERN.search(content)
    return match.group("content") if match else content


def _extract_script_content(content: str) -> str:
    match = SCRIPT_BLOCK_PATTERN.search(content)
    return match.group("content") if match else content


def _extract_custom_component_tags(content: str) -> list[str]:
    matches: list[str] = []

    for tag_name in TAG_PATTERN.findall(_extract_template_content(content)):
        normalized = tag_name.lower()
        if normalized in HTML_TAGS or normalized in ALLOWED_VUE_TAGS:
            continue

        if any(char.isupper() for char in tag_name) or normalized not in HTML_TAGS:
            if tag_name not in matches:
                matches.append(tag_name)

    return matches


def _extract_forbidden_imports(content: str) -> list[str]:
    matches: list[str] = []

    for import_path in IMPORT_PATTERN.findall(_extract_script_content(content)):
        normalized = import_path.strip()
        if normalized.endswith(".vue") or any(marker in normalized for marker in FORBIDDEN_IMPORT_MARKERS):
            if normalized not in matches:
                matches.append(normalized)

    return matches


def build_report(target_file: str | None = None) -> dict[str, Any]:
    app_file = _normalize_target(target_file)

    if not app_file.exists():
        checks = {
            "target_file_exists": {
                "passed": False,
                "detail": f"Missing target file: {app_file}",
                "matches": [],
            }
        }
        return {
            "target_file": str(app_file),
            "checks": checks,
            "errors": [{"check": "target_file_exists", "detail": checks["target_file_exists"]["detail"]}],
            "summary": {"errors": 1, "checks": 1},
        }

    content = _read_text(app_file)
    has_router_view = "<router-view" in content
    custom_component_tags = _extract_custom_component_tags(content)
    forbidden_imports = _extract_forbidden_imports(content)

    checks = {
        "router_view_required": {
            "passed": has_router_view,
            "detail": "Detected <router-view /> root outlet" if has_router_view else "Missing <router-view /> outlet",
            "matches": ["router-view"] if has_router_view else [],
        },
        "forbidden_component_tags": {
            "passed": not custom_component_tags,
            "detail": "No hard-coded business component tags detected"
            if not custom_component_tags
            else "Found hard-coded component tags in App.vue",
            "matches": custom_component_tags,
        },
        "forbidden_sfc_imports": {
            "passed": not forbidden_imports,
            "detail": "No forbidden SFC/view/component imports detected"
            if not forbidden_imports
            else "Found forbidden SFC/view/component imports in App.vue",
            "matches": forbidden_imports,
        },
    }

    errors = [
        {"check": check_name, "detail": payload["detail"]}
        for check_name, payload in checks.items()
        if not payload["passed"]
    ]

    return {
        "target_file": str(app_file),
        "checks": checks,
        "errors": errors,
        "summary": {
            "errors": len(errors),
            "checks": len(checks),
        },
    }


def print_report(report: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print("App Route Purity Gate")
    print("=====================")
    print(f"errors: {report['summary']['errors']}")

    for check_name, payload in report["checks"].items():
        status = "PASS" if payload["passed"] else "FAIL"
        print(f"- {check_name}: {status} — {payload['detail']}")
        for item in payload["matches"]:
            print(f"    {item}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate App.vue route purity and forbid hard-coded business components")
    parser.add_argument("--file", help="Target App.vue file path")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    report = build_report(args.file)
    print_report(report, args.format)
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
