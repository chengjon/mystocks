import sys
from pathlib import Path
import csv

# ArtDeco 3.1 Engineering Red Lines
LIMITS = {
    ".py": 800,
    ".ts": 500,
    ".vue": 500,
    ".js": 800,
    ".spec.ts": 1000,
    ".spec.js": 1000,
}

# Explicitly tracked targets for governance
TOP_TARGETS = [
    "web/frontend/src/api/types/common.ts",
    "web/backend/app/api/data.py",
    "web/frontend/tests/api-automation.spec.js",
    "scripts/tests/web-usability-runner.js",
    "scripts/tests/web-usability/runner-core.js",
    "src/core/unified_manager.py",
]

# File-specific hard limits.
FILE_LIMIT_OVERRIDES = {
    # This core runner is now governed by frontend/js module split threshold.
    "scripts/tests/web-usability/runner-core.js": 500,
}


def _resolve_limit(rel_path: str) -> int:
    if rel_path in FILE_LIMIT_OVERRIDES:
        return FILE_LIMIT_OVERRIDES[rel_path]

    if rel_path.endswith(".spec.js") or rel_path.endswith(".spec.ts"):
        return 1000

    ext = Path(rel_path).suffix
    return LIMITS.get(ext, 800)


def check_governance_compliance() -> list[str]:
    violations: list[str] = []
    print("🔍 [Guardrail] Monitoring large-file governance targets...")

    for rel_path in TOP_TARGETS:
        abs_path = Path(rel_path)
        if not abs_path.exists():
            print(f"  ⚪ {rel_path} not found (may have been renamed or moved)")
            continue

        limit = _resolve_limit(rel_path)

        with open(abs_path, "r", encoding="utf-8", errors="ignore") as file:
            lines = sum(1 for _ in file)

        if lines > limit:
            violations.append(f"🚩 {rel_path}: {lines} lines (Limit: {limit})")
        else:
            print(f"  ✅ {rel_path}: {lines} lines (OK)")

    return violations


def test_governance_targets_comply_with_size_limits() -> None:
    violations = check_governance_compliance()
    assert not violations, "\n" + "\n".join(violations)


def test_converted_archive_large_files_are_governed() -> None:
    archive_root = Path("web/frontend/src/views/converted.archive")
    backlog_path = Path("reports/plans/large_file_splitting_backlog.tsv")
    exceptions_path = Path("reports/compliance/exceptions/large_files.md")

    oversized_archive_files = []
    for file_path in sorted(archive_root.glob("*.vue")):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            lines = sum(1 for _ in file)
        if lines > _resolve_limit(str(file_path)):
            oversized_archive_files.append((str(file_path), lines))

    assert oversized_archive_files, "Expected at least one oversized archived Vue file"

    with open(backlog_path, "r", encoding="utf-8", errors="ignore") as file:
        backlog_rows = list(csv.DictReader(file, delimiter="\t"))

    backlog_map = {
        row["path"].lstrip("./"): row
        for row in backlog_rows
        if row.get("path")
    }
    exceptions_content = exceptions_path.read_text(encoding="utf-8", errors="ignore")

    missing_in_backlog: list[str] = []
    missing_in_exceptions: list[str] = []

    for rel_path, _lines in oversized_archive_files:
        normalized = rel_path.lstrip("./")
        row = backlog_map.get(normalized)
        if not row or row.get("status") != "EXCLUDED":
            missing_in_backlog.append(normalized)
        if normalized not in exceptions_content:
            missing_in_exceptions.append(normalized)

    assert not missing_in_backlog, f"Archive oversized files missing EXCLUDED backlog entries: {missing_in_backlog}"
    assert not missing_in_exceptions, f"Archive oversized files missing exception registry entries: {missing_in_exceptions}"


if __name__ == "__main__":
    v = check_governance_compliance()
    if v:
        print("\n❌ [Violation] Large files detected in governed targets:")
        print("\n".join(v))
        sys.exit(1)
    print("\n✅ All governance targets comply with size limits.")
