from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
from typing import Any


RULE_ID = "pm2-first-class-orchestration"
SCOPE_PATTERNS = (
    ".github/workflows/*.yml",
    ".github/workflows/*.yaml",
    "scripts/*.sh",
    "scripts/*.py",
    "scripts/**/*.sh",
    "scripts/**/*.py",
    "config/**/*.js",
    "config/**/*.json",
    "ecosystem.test.config.js",
    "web/backend/ecosystem.config.js",
    "web/frontend/ecosystem.config.js",
    "web/backend/pm2.config.json",
)
ACCEPTANCE_MARKERS = (
    "playwright test",
    "npx playwright test",
    "npm run test:e2e",
    "npm run test:e2e:stable",
    "npm run test:e2e:nightly",
    "scripts/run_e2e_pm2.sh",
)
RAW_STARTUP_MARKERS = (
    "python -m uvicorn",
    "uvicorn ",
    "npm run dev",
    "vite preview",
    "npm run preview",
    "nohup npm run dev",
)
CANONICAL_PM2_MARKERS = (
    "scripts/run_e2e_pm2.sh",
    "bash scripts/run_e2e_pm2.sh",
)
PM2_START_MARKERS = ("pm2 start",)
PM2_STATUS_MARKERS = ("pm2 list", "pm2 status", "pm2 monit")
PM2_SERVICE_MARKERS = ("mystocks-backend", "mystocks-frontend", "localhost:8020", "localhost:3020")


def normalize_relative_paths(paths: list[str] | None) -> list[str]:
    if not paths:
        return []

    normalized: set[str] = set()
    for raw_path in paths:
        path_value = raw_path.strip().replace("\\", "/")
        if not path_value:
            continue
        if path_value.startswith("./"):
            path_value = path_value[2:]
        normalized_path = Path(path_value).as_posix().strip("/")
        if normalized_path:
            normalized.add(normalized_path)
    return sorted(normalized)


def is_scoped_path(path_value: str) -> bool:
    pure_path = PurePosixPath(path_value)
    return any(pure_path.match(pattern) for pattern in SCOPE_PATTERNS)


def discover_candidate_files(project_root: Path, scoped_paths: list[str]) -> list[Path]:
    candidates: list[Path] = []
    for relative_path in scoped_paths:
        if not is_scoped_path(relative_path):
            continue
        candidate = project_root / relative_path
        if candidate.is_file():
            candidates.append(candidate)
    return sorted(set(candidates))


def matched_markers(content: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if marker in content]


def has_explicit_pm2_orchestration(content: str) -> bool:
    pm2_start = bool(matched_markers(content, PM2_START_MARKERS))
    pm2_status = bool(matched_markers(content, PM2_STATUS_MARKERS))
    pm2_service = bool(matched_markers(content, PM2_SERVICE_MARKERS))
    return pm2_start and (pm2_status or pm2_service)


def evaluate_file(path_value: str, project_root: Path) -> dict[str, Any]:
    file_path = project_root / path_value
    if not file_path.exists():
        return {
            "path": path_value,
            "passed": False,
            "mode": "missing",
            "message": "Target file does not exist",
        }

    content = file_path.read_text(encoding="utf-8", errors="ignore")
    acceptance_hits = matched_markers(content, ACCEPTANCE_MARKERS)
    raw_startup_hits = matched_markers(content, RAW_STARTUP_MARKERS)
    canonical_pm2_hits = matched_markers(content, CANONICAL_PM2_MARKERS)
    explicit_pm2 = has_explicit_pm2_orchestration(content)
    is_canonical_runner_file = path_value == "scripts/run_e2e_pm2.sh" and "pm2 start" in content and "playwright test" in content

    if not acceptance_hits:
        return {
            "path": path_value,
            "passed": True,
            "mode": "not-applicable",
            "message": "No critical acceptance orchestration markers detected",
        }

    if canonical_pm2_hits or is_canonical_runner_file:
        return {
            "path": path_value,
            "passed": True,
            "mode": "canonical-pm2-runner",
            "message": "Uses canonical PM2 acceptance runner",
            "markers": canonical_pm2_hits or ["scripts/run_e2e_pm2.sh"],
        }

    if explicit_pm2:
        return {
            "path": path_value,
            "passed": True,
            "mode": "explicit-pm2-orchestration",
            "message": "Uses explicit PM2 orchestration for acceptance runtime",
        }

    if raw_startup_hits:
        return {
            "path": path_value,
            "passed": False,
            "mode": "raw-startup-without-pm2",
            "message": "Critical acceptance orchestration must use PM2 or scripts/run_e2e_pm2.sh",
            "raw_startup_markers": raw_startup_hits,
            "acceptance_markers": acceptance_hits,
        }

    return {
        "path": path_value,
        "passed": True,
        "mode": "acceptance-without-local-orchestration",
        "message": "Acceptance markers detected without local startup orchestration; PM2 gate not required",
        "acceptance_markers": acceptance_hits,
    }


def build_report(project_root: Path, paths: list[str] | None = None) -> dict[str, Any]:
    normalized_paths = normalize_relative_paths(paths)
    candidate_files = discover_candidate_files(project_root, normalized_paths)

    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for file_path in candidate_files:
        relative_path = file_path.relative_to(project_root).as_posix()
        result = evaluate_file(relative_path, project_root)
        results.append(result)
        if not result["passed"]:
            errors.append(
                {
                    "path": relative_path,
                    "rule_id": RULE_ID,
                    "message": result["message"],
                    "mode": result["mode"],
                    "raw_startup_markers": result.get("raw_startup_markers", []),
                    "acceptance_markers": result.get("acceptance_markers", []),
                }
            )

    return {
        "project_root": str(project_root),
        "paths": normalized_paths,
        "checked_files": len(candidate_files),
        "results": results,
        "errors": errors,
        "summary": {
            "errors": len(errors),
            "checked_files": len(candidate_files),
        },
        "scope_patterns": list(SCOPE_PATTERNS),
    }


def print_report(report: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print("PM2 First-Class Gate")
    print("====================")
    print(f"checked_files: {report['checked_files']}")
    print(f"errors: {report['summary']['errors']}")

    if report["results"]:
        print("\nFile results:")
        for item in report["results"]:
            status = "PASS" if item["passed"] else "FAIL"
            print(f"  - {item['path']}: {status} — {item['message']}")
    else:
        print("\nNo changed orchestration files detected for PM2 first-class gate.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate critical acceptance orchestration uses PM2 first-class runtime")
    parser.add_argument("filenames", nargs="*")
    parser.add_argument("--root-dir", default=".")
    parser.add_argument("--path", action="append")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    merged_paths = [*(args.path or []), *args.filenames]
    report = build_report(Path(args.root_dir).resolve(), merged_paths)
    print_report(report, args.format)
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
