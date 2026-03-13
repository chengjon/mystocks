"""Frontend optimization plan audit helpers.

This module provides:
1) router -> component/api extraction (truth source from router/index.ts)
2) optimization plan table parsing
3) consistency validation for component mapping and API verification flags
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


def _find_balanced_segment(text: str, start_idx: int, open_char: str, close_char: str) -> tuple[int, int]:
    """Return (start, end_inclusive) for a balanced bracket segment."""
    if start_idx < 0 or start_idx >= len(text) or text[start_idx] != open_char:
        raise ValueError(f"Invalid segment start for {open_char}: {start_idx}")

    depth = 0
    in_string: str | None = None
    escaped = False

    for idx in range(start_idx, len(text)):
        ch = text[idx]
        if in_string:
            if escaped:
                escaped = False
                continue
            if ch == "\\":
                escaped = True
                continue
            if ch == in_string:
                in_string = None
            continue

        if ch in ("'", '"'):
            in_string = ch
            continue

        if ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:
                return start_idx, idx

    raise ValueError(f"Unbalanced segment for {open_char}{close_char} at index {start_idx}")


def _extract_routes_array(router_text: str) -> str:
    marker = "const routes"
    marker_idx = router_text.find(marker)
    if marker_idx < 0:
        raise ValueError("Cannot find `const routes` in router file")

    assign_idx = router_text.find("=", marker_idx)
    if assign_idx < 0:
        raise ValueError("Cannot find assignment for routes array")

    array_start = router_text.find("[", assign_idx)
    if array_start < 0:
        raise ValueError("Cannot find routes array start `[`")

    _, array_end = _find_balanced_segment(router_text, array_start, "[", "]")
    return router_text[array_start + 1 : array_end]


def _split_top_level_objects(array_content: str) -> list[str]:
    objects: list[str] = []
    depth = 0
    in_string: str | None = None
    escaped = False
    start_idx = -1

    for idx, ch in enumerate(array_content):
        if in_string:
            if escaped:
                escaped = False
                continue
            if ch == "\\":
                escaped = True
                continue
            if ch == in_string:
                in_string = None
            continue

        if ch in ("'", '"'):
            in_string = ch
            continue

        if ch == "{":
            if depth == 0:
                start_idx = idx
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start_idx >= 0:
                objects.append(array_content[start_idx : idx + 1])
                start_idx = -1

    return objects


def _extract_string_property(obj_text: str, prop: str) -> str | None:
    pattern = re.compile(rf"\b{re.escape(prop)}\s*:\s*'([^']*)'")
    match = pattern.search(obj_text)
    return match.group(1).strip() if match else None


def _extract_array_property(obj_text: str, prop: str) -> str | None:
    marker = re.search(rf"\b{re.escape(prop)}\s*:", obj_text)
    if not marker:
        return None

    arr_start = obj_text.find("[", marker.end())
    if arr_start < 0:
        return None

    _, arr_end = _find_balanced_segment(obj_text, arr_start, "[", "]")
    return obj_text[arr_start + 1 : arr_end]


def _extract_component_path(obj_text: str) -> str | None:
    match = re.search(r"component\s*:\s*\(\)\s*=>\s*import\(\s*'@/views/([^']+)'\s*\)", obj_text)
    return match.group(1).strip() if match else None


def _extract_meta_api(obj_text: str) -> str | None:
    # Meta block is not nested deeply in current router conventions.
    match = re.search(r"meta\s*:\s*\{[^}]*?\bapi\s*:\s*'([^']+)'", obj_text, flags=re.DOTALL)
    return match.group(1).strip() if match else None


def _join_paths(base_path: str, child_path: str) -> str:
    if child_path.startswith("/"):
        return child_path
    if not base_path or base_path == "/":
        return f"/{child_path}"
    return f"{base_path.rstrip('/')}/{child_path}"


def extract_router_page_map(router_text: str) -> dict[str, dict[str, str]]:
    """Extract a map: route_path -> {component_path, api?} from router/index.ts text."""
    routes_array = _extract_routes_array(router_text)
    result: dict[str, dict[str, str]] = {}

    def parse_array(array_content: str, base_path: str) -> None:
        for obj in _split_top_level_objects(array_content):
            path = _extract_string_property(obj, "path")
            if path is None:
                continue

            full_path = _join_paths(base_path, path)
            component_path = _extract_component_path(obj)
            api = _extract_meta_api(obj)

            if component_path:
                payload = {"component_path": component_path}
                if api:
                    payload["api"] = api
                result[full_path] = payload

            children = _extract_array_property(obj, "children")
            if children is not None:
                parse_array(children, full_path)

    parse_array(routes_array, "")
    return result


def extract_plan_rows(plan_markdown: str) -> list[dict[str, str]]:
    """Extract rows from the optimization markdown table."""
    lines = plan_markdown.splitlines()
    table_header_idx = -1
    for idx, line in enumerate(lines):
        if line.strip().startswith("| # | 页面 | 路径 |"):
            table_header_idx = idx
            break

    if table_header_idx < 0:
        raise ValueError("Cannot find optimization table header in plan markdown")

    def normalize_cell(value: str) -> str:
        return value.strip().strip("`").strip()

    rows: list[dict[str, str]] = []
    for line in lines[table_header_idx + 2 :]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            break
        cols = [normalize_cell(cell) for cell in stripped.strip("|").split("|")]
        if len(cols) < 9:
            continue
        row = {
            "index": cols[0],
            "page": cols[1],
            "path": cols[2],
            "component_path": cols[3],
            "priority": cols[4],
            "data_status": cols[5],
            "api": cols[6],
            "api_status": cols[7],
            "notes": cols[8],
        }
        rows.append(row)

    return rows


def validate_component_mapping(
    plan_rows: list[dict[str, str]],
    router_map: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    """Return component mapping issues for plan rows."""
    issues: list[dict[str, str]] = []
    for row in plan_rows:
        path = row["path"]
        expected_component = row["component_path"]
        route_info = router_map.get(path)

        if route_info is None:
            issues.append(
                {
                    "type": "route_missing",
                    "path": path,
                    "expected_component": expected_component,
                    "actual_component": "",
                }
            )
            continue

        actual_component = route_info.get("component_path", "")
        if actual_component != expected_component:
            issues.append(
                {
                    "type": "component_mismatch",
                    "path": path,
                    "expected_component": expected_component,
                    "actual_component": actual_component,
                }
            )

    return issues


def match_api_pattern(pattern: str, available_paths: set[str]) -> bool:
    """Match an API pattern against known backend paths."""
    normalized = pattern.strip().strip("`")
    if not normalized:
        return False

    normalized_available = {(item.rstrip("/") or "/") for item in available_paths if item}
    normalized_target = normalized.rstrip("/") or "/"

    if "*" in normalized:
        prefix = normalized_target.split("*", 1)[0].rstrip("/")
        if not prefix:
            return False
        return any(path == prefix or path.startswith(f"{prefix}/") for path in normalized_available)

    if normalized_target in normalized_available:
        return True

    if normalized_target != "/" and any(path.startswith(f"{normalized_target}/") for path in normalized_available):
        return True

    return False


def validate_api_verification(
    plan_rows: list[dict[str, str]],
    backend_paths: set[str],
) -> list[dict[str, str]]:
    """Validate only rows marked as verified."""
    issues: list[dict[str, str]] = []
    for row in plan_rows:
        if row.get("api_status", "").strip().lower() != "verified":
            continue

        pattern = row.get("api", "").strip()
        if not pattern:
            issues.append(
                {
                    "type": "verified_without_api",
                    "path": row.get("path", ""),
                    "api_pattern": "",
                }
            )
            continue

        if not match_api_pattern(pattern, backend_paths):
            issues.append(
                {
                    "type": "verified_api_not_found",
                    "path": row.get("path", ""),
                    "api_pattern": pattern,
                }
            )

    return issues


def load_backend_paths_from_app(repo_root: Path) -> set[str]:
    """Load backend API paths by importing FastAPI app and reading routes."""
    # Compatibility defaults: this project currently validates required settings
    # on attribute-like names in addition to .env names.
    defaults = {
        "DEVELOPMENT_MODE": "true",
        "BACKEND_PORT": "8020",
        "BACKEND_BACKUP_PORT": "8021",
        "POSTGRESQL_HOST": "localhost",
        "POSTGRESQL_PORT": "5432",
        "POSTGRESQL_USER": "postgres",
        "POSTGRESQL_PASSWORD": "postgres",
        "POSTGRESQL_DATABASE": "postgres",
        "TDENGINE_HOST": "localhost",
        "TDENGINE_PORT": "6030",
        "TDENGINE_USER": "root",
        "TDENGINE_PASSWORD": "dev-password",
        "TDENGINE_DATABASE": "market_data",
        "JWT_SECRET_KEY": "dev-key",
        "port": "8020",
        "port_range_end": "8021",
        "postgresql_host": "localhost",
        "postgresql_port": "5432",
        "postgresql_user": "postgres",
        "postgresql_password": "postgres",
        "postgresql_database": "postgres",
        "jwt_secret_key": "dev-key",
    }
    for key, value in defaults.items():
        os.environ.setdefault(key, value)

    backend_root = repo_root / "web" / "backend"
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

    from app.main import app  # pylint: disable=import-outside-toplevel

    return {route.path for route in app.routes if getattr(route, "path", None)}


def load_backend_paths_from_openapi(openapi_file: Path) -> set[str]:
    data = json.loads(openapi_file.read_text(encoding="utf-8"))
    paths = data.get("paths", {})
    if not isinstance(paths, dict):
        return set()
    return set(paths.keys())


def build_report_markdown(
    plan_rows: list[dict[str, str]],
    router_map: dict[str, dict[str, str]],
    component_issues: list[dict[str, str]],
    api_issues: list[dict[str, str]],
    backend_source: str,
) -> str:
    today = date.today().isoformat()
    lines: list[str] = []
    lines.append("# Frontend Optimization Audit Report")
    lines.append("")
    lines.append(f"- generated_at: {today}")
    lines.append(f"- plan_rows: {len(plan_rows)}")
    lines.append(f"- router_routes: {len(router_map)}")
    lines.append(f"- backend_source: {backend_source}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- component_issues: {len(component_issues)}")
    lines.append(f"- verified_api_issues: {len(api_issues)}")
    lines.append("")

    lines.append("## Component Issues")
    lines.append("")
    if not component_issues:
        lines.append("- none")
    else:
        for issue in component_issues:
            lines.append(
                f"- [{issue['type']}] {issue['path']}: expected `{issue['expected_component']}` actual `{issue['actual_component']}`"
            )
    lines.append("")

    lines.append("## Verified API Issues")
    lines.append("")
    if not api_issues:
        lines.append("- none")
    else:
        for issue in api_issues:
            lines.append(f"- [{issue['type']}] {issue['path']}: `{issue['api_pattern']}`")

    return "\n".join(lines) + "\n"


def run_audit(
    repo_root: Path,
    router_file: Path,
    plan_file: Path,
    openapi_fallback_file: Path,
) -> dict[str, Any]:
    router_map = extract_router_page_map(router_file.read_text(encoding="utf-8"))
    plan_rows = extract_plan_rows(plan_file.read_text(encoding="utf-8"))
    component_issues = validate_component_mapping(plan_rows, router_map)

    backend_source = "backend_app"
    try:
        backend_paths = load_backend_paths_from_app(repo_root)
    except Exception:  # pragma: no cover - runtime fallback path
        backend_source = "openapi_fallback"
        backend_paths = load_backend_paths_from_openapi(openapi_fallback_file)

    api_issues = validate_api_verification(plan_rows, backend_paths)

    return {
        "plan_rows": plan_rows,
        "router_map": router_map,
        "backend_paths": backend_paths,
        "backend_source": backend_source,
        "component_issues": component_issues,
        "api_issues": api_issues,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate frontend optimization list against router/backend routes.")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root (default: current directory).",
    )
    parser.add_argument(
        "--router-file",
        default="web/frontend/src/router/index.ts",
        help="Router file path.",
    )
    parser.add_argument(
        "--plan-file",
        default="docs/plans/frontend-page-optimization-list.md",
        help="Optimization plan markdown path.",
    )
    parser.add_argument(
        "--openapi-file",
        default="docs/api/openapi.json",
        help="OpenAPI fallback path when backend import fails.",
    )
    parser.add_argument(
        "--report-file",
        default="reports/analysis/frontend-page-optimization-audit-report.md",
        help="Output markdown report path.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when any issue exists.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    router_file = (repo_root / args.router_file).resolve()
    plan_file = (repo_root / args.plan_file).resolve()
    openapi_file = (repo_root / args.openapi_file).resolve()
    report_file = (repo_root / args.report_file).resolve()

    result = run_audit(
        repo_root=repo_root,
        router_file=router_file,
        plan_file=plan_file,
        openapi_fallback_file=openapi_file,
    )
    report_text = build_report_markdown(
        plan_rows=result["plan_rows"],
        router_map=result["router_map"],
        component_issues=result["component_issues"],
        api_issues=result["api_issues"],
        backend_source=result["backend_source"],
    )

    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(report_text, encoding="utf-8")

    component_count = len(result["component_issues"])
    api_count = len(result["api_issues"])
    print(f"[audit] plan_rows={len(result['plan_rows'])}")
    print(f"[audit] component_issues={component_count}")
    print(f"[audit] verified_api_issues={api_count}")
    print(f"[audit] backend_source={result['backend_source']}")
    print(f"[audit] report={report_file}")

    if args.strict and (component_count > 0 or api_count > 0):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
