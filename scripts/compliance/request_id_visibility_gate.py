from __future__ import annotations

import argparse
import json
import re
from fnmatch import fnmatch
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCOPE_ROOT = "web/frontend/src/views/artdeco-pages/"
SCOPE_PATTERNS = ("web/frontend/src/views/artdeco-pages/*-tabs/*.vue",)

TEMPLATE_COMPONENT_MARKERS = ("ArtDecoPageTemplate",)
TRACE_SCRIPT_MARKERS = ("lastRequestId", "displayRequestId", "requestId", "traceId", "request_id")
TRACE_TEMPLATE_LABEL_MARKERS = ("REQ_ID", "TRACE_ID", "LAST_REQ", "Request ID", "REQUEST ID")
TRACE_TEMPLATE_CLASS_MARKERS = ("trace-id", "request-trace", "trace-info", "header-meta", "tabs-trace")

TEMPLATE_BLOCK_PATTERN = re.compile(r"<template\b[^>]*>(?P<content>.*?)</template>", re.DOTALL | re.IGNORECASE)
SCRIPT_BLOCK_PATTERN = re.compile(r"<script\b[^>]*>(?P<content>.*?)</script>", re.DOTALL | re.IGNORECASE)
TRACE_INTERPOLATION_PATTERN = re.compile(r"{{\s*(?:lastRequestId|displayRequestId|requestId|traceId)\b")


def normalize_input_path(raw_path: str) -> str:
    value = raw_path.strip().replace("\\", "/")
    if not value:
        return ""

    marker_index = value.find(SCOPE_ROOT)
    if marker_index >= 0:
        value = value[marker_index:]
    elif value.startswith("./"):
        value = value[2:]

    return Path(value).as_posix().strip("/")


def is_scoped_path(path_value: str) -> bool:
    return any(fnmatch(path_value, pattern) for pattern in SCOPE_PATTERNS)


def resolve_file_path(raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def extract_block(content: str, pattern: re.Pattern[str]) -> str:
    match = pattern.search(content)
    return match.group("content") if match else content


def evaluate_file(path_value: str, raw_path: str) -> dict[str, Any]:
    file_path = resolve_file_path(raw_path)
    if not file_path.exists():
        return {
            "path": path_value,
            "passed": False,
            "message": "Target file does not exist",
            "mode": "missing",
        }

    content = file_path.read_text(encoding="utf-8")
    template_content = extract_block(content, TEMPLATE_BLOCK_PATTERN)
    script_content = extract_block(content, SCRIPT_BLOCK_PATTERN)

    uses_template_component = any(marker in content for marker in TEMPLATE_COMPONENT_MARKERS)
    has_trace_variable = any(marker in content for marker in TRACE_SCRIPT_MARKERS)
    has_trace_label = any(marker in template_content for marker in TRACE_TEMPLATE_LABEL_MARKERS)
    has_trace_class = any(marker in template_content for marker in TRACE_TEMPLATE_CLASS_MARKERS)
    has_trace_interpolation = bool(TRACE_INTERPOLATION_PATTERN.search(template_content))
    has_explicit_trace_display = has_trace_variable and has_trace_interpolation and (has_trace_label or has_trace_class)

    passed = uses_template_component or has_explicit_trace_display
    if uses_template_component:
        mode = "template"
        message = "Uses ArtDecoPageTemplate with built-in REQ_ID slot"
    elif has_explicit_trace_display:
        mode = "explicit"
        message = "Has explicit Request ID / TRACE_ID display"
    else:
        mode = "missing-trace"
        message = "Missing Request ID / TRACE_ID display slot"

    return {
        "path": path_value,
        "passed": passed,
        "message": message,
        "mode": mode,
    }


def build_report(paths: list[str] | None = None) -> dict[str, Any]:
    normalized_inputs: list[str] = []
    errors: list[dict[str, str]] = []
    checked_files: list[dict[str, Any]] = []

    for raw_path in paths or []:
        normalized = normalize_input_path(raw_path)
        if not normalized or not is_scoped_path(normalized):
            continue
        normalized_inputs.append(normalized)
        result = evaluate_file(normalized, raw_path)
        checked_files.append(result)
        if not result["passed"]:
            errors.append({"path": normalized, "message": result["message"]})

    return {
        "paths": normalized_inputs,
        "checked_files": len(checked_files),
        "results": checked_files,
        "errors": errors,
        "summary": {
            "errors": len(errors),
            "checked_files": len(checked_files),
        },
    }


def print_report(report: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print("Request ID Visibility Gate")
    print("==========================")
    print(f"checked_files: {report['checked_files']}")
    print(f"errors: {report['summary']['errors']}")
    for item in report["results"]:
        status = "PASS" if item["passed"] else "FAIL"
        print(f"- {item['path']}: {status} — {item['message']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Request ID / TRACE_ID visibility for changed business tabs")
    parser.add_argument("--path", action="append")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    report = build_report(args.path)
    print_report(report, args.format)
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
