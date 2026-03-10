from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_VUE_PATH = PROJECT_ROOT / "web" / "frontend" / "src" / "App.vue"
READINESS_COMPOSABLE_PATH = PROJECT_ROOT / "web" / "frontend" / "src" / "composables" / "useBackendReadiness.ts"
BACKEND_ROOT = PROJECT_ROOT / "web" / "backend" / "app"

BACKEND_READY_ROUTE_MARKERS = (
    '@app.get("/health/ready")',
    "@app.get('/health/ready')",
    '@router.get("/health/ready")',
    "@router.get('/health/ready')",
)

APP_STARTUP_MARKERS = (
    "useBackendReadiness",
    "checkBackendReadiness",
    "onMounted(() =>",
    "void checkBackendReadiness()",
)

APP_FALLBACK_MARKERS = (
    'data-testid="app-readiness-checking"',
    'data-testid="app-readiness-error"',
    "usingMockFallback",
    "router-view",
)

COMPOSABLE_MARKERS = (
    "resolveReadinessEndpoint",
    "/api/health/ready",
    "Mock 验收模式",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_backend_ready_probe() -> dict[str, Any]:
    matches: list[str] = []

    for file_path in sorted(BACKEND_ROOT.rglob("*.py")):
        content = _read_text(file_path)
        if any(marker in content for marker in BACKEND_READY_ROUTE_MARKERS):
            matches.append(file_path.relative_to(PROJECT_ROOT).as_posix())

    passed = bool(matches)
    return {
        "passed": passed,
        "detail": "Detected /health/ready readiness probe" if passed else "Missing /health/ready readiness probe",
        "matches": matches,
    }


def check_app_startup_readiness() -> dict[str, Any]:
    if not APP_VUE_PATH.exists():
        return {
            "passed": False,
            "detail": "Missing App.vue",
            "matches": [],
        }

    matches: list[str] = []
    app_content = _read_text(APP_VUE_PATH)
    composable_content = _read_text(READINESS_COMPOSABLE_PATH) if READINESS_COMPOSABLE_PATH.exists() else ""

    app_markers_ok = all(marker in app_content for marker in APP_STARTUP_MARKERS)
    composable_markers_ok = all(marker in composable_content for marker in COMPOSABLE_MARKERS)

    if app_markers_ok:
        matches.append(APP_VUE_PATH.relative_to(PROJECT_ROOT).as_posix())
    if composable_markers_ok:
        matches.append(READINESS_COMPOSABLE_PATH.relative_to(PROJECT_ROOT).as_posix())

    passed = app_markers_ok and composable_markers_ok
    return {
        "passed": passed,
        "detail": "App startup readiness check detected" if passed else "Missing App startup readiness check",
        "matches": matches,
    }


def check_app_non_blank_fallback() -> dict[str, Any]:
    if not APP_VUE_PATH.exists():
        return {
            "passed": False,
            "detail": "Missing App.vue",
            "matches": [],
        }

    app_content = _read_text(APP_VUE_PATH)
    markers_ok = all(marker in app_content for marker in APP_FALLBACK_MARKERS)
    matches = [APP_VUE_PATH.relative_to(PROJECT_ROOT).as_posix()] if markers_ok else []

    return {
        "passed": markers_ok,
        "detail": "App non-blank fallback detected" if markers_ok else "Missing App non-blank fallback shell",
        "matches": matches,
    }


def build_report() -> dict[str, Any]:
    checks = {
        "backend_ready_probe": check_backend_ready_probe(),
        "app_startup_readiness": check_app_startup_readiness(),
        "app_non_blank_fallback": check_app_non_blank_fallback(),
    }

    errors = [
        {
            "check": check_name,
            "detail": payload["detail"],
        }
        for check_name, payload in checks.items()
        if not payload["passed"]
    ]

    return {
        "project_root": str(PROJECT_ROOT),
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

    print("Observability Readiness Gate")
    print("============================")
    print(f"errors: {report['summary']['errors']}")

    for check_name, payload in report["checks"].items():
        status = "PASS" if payload["passed"] else "FAIL"
        print(f"- {check_name}: {status} — {payload['detail']}")
        for matched_path in payload["matches"]:
            print(f"    {matched_path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate readiness probe and App startup observability contract")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    report = build_report()
    print_report(report, args.format)
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

