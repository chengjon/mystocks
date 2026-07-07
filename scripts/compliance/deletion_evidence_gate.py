from __future__ import annotations

import argparse
import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENT_EXTENSIONS = {".md", ".txt", ".rst", ".adoc", ".org"}
EVIDENCE_REGISTRY_PATH = "governance/deletion-evidence.yaml"
WAIVER_REGISTRY_PATH = "governance/waivers/deletion-evidence-waivers.yaml"
SAFE_CODE_PATH_VERDICT = "safe_to_delete"
ALLOWED_FUNCTION_TREE_VERDICTS = {"重复冗余", "正式下线"}
GLOB_MARKERS = ("*", "?", "[", "]")
SUPPORTED_KINDS = {"directory", "document"}


def normalize_relative_path(raw_path: str) -> str:
    value = raw_path.strip().replace("\\", "/")
    if not value:
        return ""
    if value.startswith("./"):
        value = value[2:]
    return Path(value).as_posix().strip("/")


def normalize_relative_paths(paths: list[str] | None) -> list[str]:
    if not paths:
        return []

    normalized: set[str] = set()
    for raw_path in paths:
        path_value = normalize_relative_path(raw_path)
        if path_value:
            normalized.add(path_value)
    return sorted(normalized)


def contains_glob(path_value: str) -> bool:
    return any(marker in path_value for marker in GLOB_MARKERS)


def run_git_command(root_dir: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root_dir), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def load_yaml_from_ref(root_dir: Path, ref: str, path_value: str) -> tuple[dict[str, Any], str | None]:
    completed = run_git_command(root_dir, ["show", f"{ref}:{path_value}"])
    if completed.returncode != 0:
        return {}, None

    try:
        payload = yaml.safe_load(completed.stdout) or {}
    except yaml.YAMLError as exc:
        return {}, f"{path_value} at {ref} is not valid YAML: {exc}"

    if not isinstance(payload, dict):
        return {}, f"{path_value} at {ref} must decode to a mapping"
    return payload, None


def list_tracked_files(root_dir: Path, ref: str) -> tuple[set[str], str | None]:
    completed = run_git_command(root_dir, ["ls-tree", "-r", "--name-only", ref])
    if completed.returncode != 0:
        return set(), completed.stderr.strip() or f"Unable to list tracked files at {ref}"

    tracked = {normalize_relative_path(line) for line in completed.stdout.splitlines() if line.strip()}
    tracked.discard("")
    return tracked, None


def discover_deleted_paths(root_dir: Path, scope: str, paths: list[str] | None = None) -> tuple[list[str], str | None]:
    explicit_paths = normalize_relative_paths(paths)
    if explicit_paths:
        return explicit_paths, None

    if scope == "staged":
        completed = run_git_command(root_dir, ["diff", "--cached", "--name-only", "--diff-filter=D"])
        if completed.returncode != 0:
            return [], completed.stderr.strip() or "Unable to inspect staged deletions"
        return normalize_relative_paths(completed.stdout.splitlines()), None

    if scope == "worktree":
        staged = run_git_command(root_dir, ["diff", "--cached", "--name-only", "--diff-filter=D"])
        unstaged = run_git_command(root_dir, ["diff", "--name-only", "--diff-filter=D"])
        if staged.returncode != 0:
            return [], staged.stderr.strip() or "Unable to inspect staged deletions"
        if unstaged.returncode != 0:
            return [], unstaged.stderr.strip() or "Unable to inspect worktree deletions"
        combined = [*staged.stdout.splitlines(), *unstaged.stdout.splitlines()]
        return normalize_relative_paths(combined), None

    return [], f"Unsupported scope: {scope}"


def build_candidate_directories(paths: list[str]) -> list[str]:
    candidates: set[str] = set()
    for path_value in paths:
        current = Path(path_value)
        for parent in current.parents:
            if parent == Path("."):
                break
            candidates.add(parent.as_posix())
    return sorted(candidates, key=lambda item: (item.count("/"), item))


def discover_deleted_directories(deleted_paths: list[str], tracked_files: set[str]) -> list[str]:
    deleted_set = set(deleted_paths)
    qualifying: list[str] = []
    tracked_map: dict[str, set[str]] = {}

    for directory in build_candidate_directories(deleted_paths):
        directory_prefix = f"{directory}/"
        tracked_under_directory = {
            tracked_path for tracked_path in tracked_files if tracked_path == directory or tracked_path.startswith(directory_prefix)
        }
        if tracked_under_directory and tracked_under_directory.issubset(deleted_set):
            qualifying.append(directory)
            tracked_map[directory] = tracked_under_directory

    qualifying_set = set(qualifying)

    def immediate_children(path_value: str) -> list[str]:
        descendants = [
            candidate
            for candidate in qualifying_set
            if candidate != path_value and candidate.startswith(f"{path_value}/")
        ]
        children: list[str] = []
        for descendant in sorted(descendants, key=lambda item: (item.count("/"), item)):
            if any(descendant.startswith(f"{existing}/") for existing in children):
                continue
            children.append(descendant)
        return children

    def is_redundant_parent(path_value: str) -> bool:
        children = immediate_children(path_value)
        if len(children) != 1:
            return False
        child = children[0]
        return tracked_map.get(path_value, set()) == tracked_map.get(child, set())

    selected: list[str] = []
    for directory in sorted(qualifying_set, key=lambda item: (item.count("/"), item)):
        if is_redundant_parent(directory):
            continue
        if any(directory.startswith(f"{existing}/") for existing in selected):
            continue
        selected.append(directory)
    return selected


def is_document_path(path_value: str) -> bool:
    return Path(path_value).suffix.lower() in DOCUMENT_EXTENSIONS


def path_is_inside_directory(path_value: str, directory: str) -> bool:
    normalized_directory = directory.rstrip("/")
    return path_value == normalized_directory or path_value.startswith(f"{normalized_directory}/")


def discover_document_targets(deleted_paths: list[str], deleted_directories: list[str]) -> list[str]:
    documents = [path_value for path_value in deleted_paths if is_document_path(path_value)]
    uncovered_documents = [
        path_value
        for path_value in documents
        if not any(path_is_inside_directory(path_value, directory) for directory in deleted_directories)
    ]
    if len(uncovered_documents) < 3:
        return []
    return sorted(uncovered_documents)


OPENSPEC_CHANGES_PREFIX = "openspec/changes/"
OPENSPEC_ARCHIVE_PREFIX = "openspec/changes/archive/"


def detect_openspec_archive_moves(
    root_dir: Path, deleted_directories: list[str]
) -> tuple[list[str], list[dict[str, Any]]]:
    """Identify directories that were moved by ``openspec archive`` rather than deleted.

    Standard archive moves follow the pattern:
        openspec/changes/<change-id>/  ->  openspec/changes/archive/<date>-<change-id>/

    Returns a tuple ``(exempt_directories, move_records)`` where ``exempt_directories``
    is the subset of ``deleted_directories`` that should be skipped by the gate, and
    ``move_records`` carries structured details for telemetry / audit logging.
    """
    if not deleted_directories:
        return [], []

    candidates: dict[str, str] = {}
    for directory in deleted_directories:
        normalized = directory.rstrip("/")
        if not normalized.startswith(OPENSPEC_CHANGES_PREFIX):
            continue
        if normalized.startswith(OPENSPEC_ARCHIVE_PREFIX):
            continue
        change_id = normalized[len(OPENSPEC_CHANGES_PREFIX):]
        if "/" in change_id or not change_id:
            continue
        candidates[normalized] = change_id
    if not candidates:
        return [], []

    archive_root = root_dir / OPENSPEC_ARCHIVE_PREFIX.rstrip("/")
    if not archive_root.is_dir():
        return [], []

    existing_archive_dirs = {entry.name: entry for entry in archive_root.iterdir() if entry.is_dir()}
    exempt: list[str] = []
    records: list[dict[str, Any]] = []
    for directory, change_id in candidates.items():
        match = next(
            (
                name
                for name in existing_archive_dirs
                if name == change_id or name.endswith(f"-{change_id}")
            ),
            None,
        )
        if match is None:
            continue
        exempt.append(directory)
        records.append(
            {
                "kind": "openspec_archive_move",
                "source_directory": directory,
                "archive_directory": f"{OPENSPEC_ARCHIVE_PREFIX}{match}",
                "change_id": change_id,
            }
        )
    return exempt, records


def parse_iso_date(raw_value: Any) -> date | None:
    if not isinstance(raw_value, str) or not raw_value.strip():
        return None
    try:
        return date.fromisoformat(raw_value.strip())
    except ValueError:
        return None


def load_registry_entries(root_dir: Path, ref: str) -> tuple[list[dict[str, Any]], list[str]]:
    payload, error = load_yaml_from_ref(root_dir, ref, EVIDENCE_REGISTRY_PATH)
    if error:
        return [], [error]

    entries = payload.get("entries", [])
    if entries in (None, ""):
        entries = []
    if not isinstance(entries, list):
        return [], [f"{EVIDENCE_REGISTRY_PATH} entries must be a list"]
    typed_entries = [entry for entry in entries if isinstance(entry, dict)]
    if len(typed_entries) != len(entries):
        return [], [f"{EVIDENCE_REGISTRY_PATH} entries must contain mappings only"]
    return typed_entries, []


def load_waiver_entries(root_dir: Path, ref: str) -> tuple[list[dict[str, Any]], list[str]]:
    payload, error = load_yaml_from_ref(root_dir, ref, WAIVER_REGISTRY_PATH)
    if error:
        return [], [error]

    waivers = payload.get("waivers", [])
    if waivers in (None, ""):
        waivers = []
    if not isinstance(waivers, list):
        return [], [f"{WAIVER_REGISTRY_PATH} waivers must be a list"]
    typed_waivers = [waiver for waiver in waivers if isinstance(waiver, dict)]
    if len(typed_waivers) != len(waivers):
        return [], [f"{WAIVER_REGISTRY_PATH} waivers must contain mappings only"]
    return typed_waivers, []


def find_matching_entries(entries: list[dict[str, Any]], path_value: str, kind: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for entry in entries:
        entry_path = normalize_relative_path(str(entry.get("path", "")))
        entry_kind = str(entry.get("kind", "")).strip()
        if entry_path == path_value and entry_kind == kind:
            matches.append(entry)
    return matches


def validate_evidence_entry(entry: dict[str, Any]) -> str | None:
    path_value = normalize_relative_path(str(entry.get("path", "")))
    kind = str(entry.get("kind", "")).strip()
    status = str(entry.get("status", "")).strip()
    owner = str(entry.get("owner", "")).strip()
    code_path_verdict = str(entry.get("code_path_verdict", "")).strip()
    function_tree_verdict = str(entry.get("function_tree_verdict", "")).strip()

    if not path_value:
        return "missing path"
    if contains_glob(path_value):
        return "path must be exact; wildcards are forbidden"
    if kind not in SUPPORTED_KINDS:
        return "kind must be directory or document"
    if status != "approved":
        return f"status must be approved (found: {status or 'missing'})"
    if code_path_verdict != SAFE_CODE_PATH_VERDICT:
        return f"code_path_verdict must be {SAFE_CODE_PATH_VERDICT} (found: {code_path_verdict or 'missing'})"
    if function_tree_verdict not in ALLOWED_FUNCTION_TREE_VERDICTS:
        allowed = ", ".join(sorted(ALLOWED_FUNCTION_TREE_VERDICTS))
        return f"function_tree_verdict must be one of {allowed} (found: {function_tree_verdict or 'missing'})"
    if not owner:
        return "owner is required"
    return None


def is_truthy_approval(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return bool(value.strip())
    return False


def validate_waiver_entry_structure(entry: dict[str, Any]) -> str | None:
    path_value = normalize_relative_path(str(entry.get("path", "")))
    kind = str(entry.get("kind", "")).strip()
    owner = str(entry.get("owner", "")).strip()
    reason = str(entry.get("reason", "")).strip()
    ticket_or_context = str(entry.get("ticket_or_context", "")).strip()
    approved_on = parse_iso_date(entry.get("approved_on"))
    expires_on = parse_iso_date(entry.get("expires_on"))

    if not path_value:
        return "missing path"
    if contains_glob(path_value):
        return "path must be exact; wildcards are forbidden"
    if kind not in SUPPORTED_KINDS:
        return "kind must be directory or document"
    if not owner:
        return "owner is required"
    if not reason:
        return "reason is required"
    if not ticket_or_context:
        return "ticket_or_context is required"
    if not is_truthy_approval(entry.get("approved_by_user")):
        return "approved_by_user is required"
    if approved_on is None:
        return "approved_on must be an ISO date"
    if expires_on is None:
        return "expires_on must be an ISO date"
    return None


def validate_waiver_entry(entry: dict[str, Any], today: date) -> str | None:
    structure_error = validate_waiver_entry_structure(entry)
    if structure_error is not None:
        return structure_error

    expires_on = parse_iso_date(entry.get("expires_on"))
    assert expires_on is not None
    if expires_on < today:
        return f"waiver expired on {expires_on.isoformat()}"
    return None


def classify_waiver_audit_status(expires_on: date, today: date, warning_window_days: int) -> tuple[str, int]:
    days_until_expiry = (expires_on - today).days
    if days_until_expiry < 0:
        return "expired", days_until_expiry
    if days_until_expiry <= warning_window_days:
        return "expiring_soon", days_until_expiry
    return "healthy", days_until_expiry


def build_waiver_audit_report(
    root_dir: str | Path = ".",
    *,
    ref: str = "HEAD",
    today: date | None = None,
    warning_window_days: int = 7,
) -> dict[str, Any]:
    root_path = Path(root_dir).resolve()
    today_value = today or date.today()
    waiver_entries, waiver_errors = load_waiver_entries(root_path, ref)

    findings: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = [
        {
            "path": "",
            "kind": "waiver",
            "owner": "",
            "expires_on": None,
            "days_until_expiry": None,
            "status": "invalid",
            "message": message,
        }
        for message in waiver_errors
    ]

    for entry in waiver_entries:
        path_value = normalize_relative_path(str(entry.get("path", "")))
        kind = str(entry.get("kind", "")).strip()
        owner = str(entry.get("owner", "")).strip()
        expires_on = parse_iso_date(entry.get("expires_on"))
        structure_error = validate_waiver_entry_structure(entry)

        if structure_error is not None:
            errors.append(
                {
                    "path": path_value,
                    "kind": kind,
                    "owner": owner,
                    "expires_on": entry.get("expires_on"),
                    "days_until_expiry": None,
                    "status": "invalid",
                    "message": structure_error,
                }
            )
            continue

        assert expires_on is not None
        status, days_until_expiry = classify_waiver_audit_status(expires_on, today_value, warning_window_days)
        if status == "expired":
            message = f"Waiver expired on {expires_on.isoformat()}"
        elif status == "expiring_soon":
            message = f"Waiver expires in {days_until_expiry} day(s)"
        else:
            message = f"Waiver remains valid for {days_until_expiry} day(s)"

        findings.append(
            {
                "path": path_value,
                "kind": kind,
                "owner": owner,
                "expires_on": expires_on.isoformat(),
                "days_until_expiry": days_until_expiry,
                "status": status,
                "message": message,
            }
        )

    sorted_findings = sorted(findings, key=lambda item: (item["expires_on"], item["path"]))

    return {
        "project_root": str(root_path),
        "mode": "waiver-audit",
        "evidence_ref": ref,
        "today": today_value.isoformat(),
        "warning_window_days": warning_window_days,
        "waiver_registry_path": WAIVER_REGISTRY_PATH,
        "findings": sorted_findings,
        "errors": errors,
        "summary": {
            "total": len(sorted_findings) + len(errors),
            "healthy": sum(1 for item in sorted_findings if item["status"] == "healthy"),
            "expiring_soon": sum(1 for item in sorted_findings if item["status"] == "expiring_soon"),
            "expired": sum(1 for item in sorted_findings if item["status"] == "expired"),
            "invalid": len(errors),
        },
        "policy": {
            "head_only_authorization": True,
            "warning_window_days": warning_window_days,
            "waiver_registry_path": WAIVER_REGISTRY_PATH,
        },
    }


def evaluate_target(
    *,
    path_value: str,
    kind: str,
    evidence_entries: list[dict[str, Any]],
    waiver_entries: list[dict[str, Any]],
    today: date,
) -> dict[str, Any]:
    matching_waivers = find_matching_entries(waiver_entries, path_value, kind)
    for waiver in matching_waivers:
        validation_error = validate_waiver_entry(waiver, today)
        if validation_error is None:
            return {
                "path": path_value,
                "kind": kind,
                "passed": True,
                "mode": "waiver",
                "message": "Deletion authorized by pre-existing emergency waiver",
                "registry_path": WAIVER_REGISTRY_PATH,
            }

    if matching_waivers:
        last_error = validate_waiver_entry(matching_waivers[-1], today)
        return {
            "path": path_value,
            "kind": kind,
            "passed": False,
            "mode": "invalid-waiver",
            "message": last_error or "Matching waiver is invalid",
            "registry_path": WAIVER_REGISTRY_PATH,
        }

    matching_evidence = find_matching_entries(evidence_entries, path_value, kind)
    for entry in matching_evidence:
        validation_error = validate_evidence_entry(entry)
        if validation_error is None:
            return {
                "path": path_value,
                "kind": kind,
                "passed": True,
                "mode": "evidence",
                "message": "Deletion authorized by pre-existing governance evidence",
                "registry_path": EVIDENCE_REGISTRY_PATH,
            }

    if matching_evidence:
        last_error = validate_evidence_entry(matching_evidence[-1])
        return {
            "path": path_value,
            "kind": kind,
            "passed": False,
            "mode": "invalid-evidence",
            "message": last_error or "Matching evidence entry is invalid",
            "registry_path": EVIDENCE_REGISTRY_PATH,
        }

    return {
        "path": path_value,
        "kind": kind,
        "passed": False,
        "mode": "missing-evidence",
        "message": "Missing pre-existing exact-path deletion authorization in governance registry",
        "registry_path": EVIDENCE_REGISTRY_PATH,
    }


def build_report(
    root_dir: str | Path = ".",
    *,
    scope: str,
    ref: str = "HEAD",
    paths: list[str] | None = None,
    today: date | None = None,
) -> dict[str, Any]:
    root_path = Path(root_dir).resolve()
    today_value = today or date.today()

    deleted_paths, deleted_error = discover_deleted_paths(root_path, scope, paths=paths)
    tracked_files: set[str] = set()
    internal_errors: list[str] = []

    if deleted_error:
        internal_errors.append(deleted_error)
    if deleted_paths:
        tracked_files, tracked_error = list_tracked_files(root_path, ref)
        if tracked_error:
            internal_errors.append(tracked_error)

    evidence_entries, evidence_errors = load_registry_entries(root_path, ref)
    waiver_entries, waiver_errors = load_waiver_entries(root_path, ref)
    internal_errors.extend(evidence_errors)
    internal_errors.extend(waiver_errors)

    deleted_directories = discover_deleted_directories(deleted_paths, tracked_files) if deleted_paths else []
    document_targets = discover_document_targets(deleted_paths, deleted_directories) if deleted_paths else []

    archive_exempt_directories, archive_move_records = detect_openspec_archive_moves(root_path, deleted_directories)
    archive_exempt_set = set(archive_exempt_directories)
    if archive_exempt_set:
        deleted_directories = [d for d in deleted_directories if d not in archive_exempt_set]
        document_targets = [
            d for d in document_targets if not any(path_is_inside_directory(d, exempt) for exempt in archive_exempt_set)
        ]

    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for directory in deleted_directories:
        result = evaluate_target(
            path_value=directory,
            kind="directory",
            evidence_entries=evidence_entries,
            waiver_entries=waiver_entries,
            today=today_value,
        )
        results.append(result)
        if not result["passed"]:
            errors.append(result)

    for exempt_directory in archive_exempt_directories:
        results.append(
            {
                "path": exempt_directory,
                "kind": "directory",
                "passed": True,
                "mode": "openspec_archive_move",
                "message": "Directory moved by `openspec archive` tooling; treated as lifecycle move, not deletion",
                "registry_path": "",
            }
        )

    for document_path in document_targets:
        result = evaluate_target(
            path_value=document_path,
            kind="document",
            evidence_entries=evidence_entries,
            waiver_entries=waiver_entries,
            today=today_value,
        )
        results.append(result)
        if not result["passed"]:
            errors.append(result)

    if internal_errors and (deleted_directories or document_targets):
        for message in internal_errors:
            errors.append(
                {
                    "path": "",
                    "kind": "internal",
                    "passed": False,
                    "mode": "internal-error",
                    "message": message,
                    "registry_path": "",
                }
            )

    return {
        "project_root": str(root_path),
        "scope": scope,
        "evidence_ref": ref,
        "today": today_value.isoformat(),
        "paths": normalize_relative_paths(paths),
        "deleted_paths": deleted_paths,
        "directory_targets": deleted_directories,
        "document_targets": document_targets,
        "openspec_archive_moves": archive_move_records,
        "results": results,
        "errors": errors,
        "summary": {
            "errors": len(errors),
            "checked_targets": len(results),
            "deleted_paths": len(deleted_paths),
            "deleted_directories": len(deleted_directories),
            "deleted_documents": len(document_targets),
            "openspec_archive_moves": len(archive_move_records),
        },
        "policy": {
            "evidence_registry_path": EVIDENCE_REGISTRY_PATH,
            "waiver_registry_path": WAIVER_REGISTRY_PATH,
            "document_threshold": 3,
            "supported_document_extensions": sorted(DOCUMENT_EXTENSIONS),
            "function_tree_verdicts_allowing_deletion": sorted(ALLOWED_FUNCTION_TREE_VERDICTS),
            "head_only_authorization": True,
        },
    }


def print_report(report: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    if report.get("mode") == "waiver-audit":
        print("Deletion Waiver Audit")
        print("=====================")
        print(f"waiver_registry_path: {report['waiver_registry_path']}")
        print(f"today: {report['today']}")
        print(f"warning_window_days: {report['warning_window_days']}")
        print(f"total: {report['summary']['total']}")
        print(f"healthy: {report['summary']['healthy']}")
        print(f"expiring_soon: {report['summary']['expiring_soon']}")
        print(f"expired: {report['summary']['expired']}")
        print(f"invalid: {report['summary']['invalid']}")

        if not report["findings"] and not report["errors"]:
            print("\nNo waiver findings detected.")
            return

        for item in report["findings"]:
            print(
                f"- {item['kind']} {item['path']}: {item['status']} "
                f"(expires_on={item['expires_on']}, days_until_expiry={item['days_until_expiry']})"
            )
        for item in report["errors"]:
            path_value = item.get("path", "")
            label = f"{item.get('kind', 'waiver')} {path_value}".strip()
            print(f"- {label}: invalid - {item['message']}")
        return

    print("Deletion Evidence Gate")
    print("======================")
    print(f"scope: {report['scope']}")
    print(f"deleted_paths: {report['summary']['deleted_paths']}")
    print(f"directory_targets: {report['summary']['deleted_directories']}")
    print(f"document_targets: {report['summary']['deleted_documents']}")
    print(f"errors: {report['summary']['errors']}")

    if not report["results"]:
        print("\nNo governed deletions detected.")
        return

    for item in report["results"]:
        status = "PASS" if item["passed"] else "FAIL"
        print(f"- {item['kind']} {item['path']}: {status} — {item['message']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Block tracked directory deletion and >=3 document deletion without pre-existing governance evidence"
    )
    parser.add_argument("--root-dir", default=".")
    parser.add_argument("--scope", choices=("staged", "worktree"), default="staged")
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--path", action="append")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--today", help="ISO date override for deterministic waiver validation")
    parser.add_argument("--audit-waivers", action="store_true")
    parser.add_argument("--warning-window-days", type=int, default=7)
    args = parser.parse_args(argv)

    today = parse_iso_date(args.today) if args.today else None
    if args.today and today is None:
        raise SystemExit("--today must be an ISO date")
    if args.warning_window_days < 0:
        raise SystemExit("--warning-window-days must be >= 0")

    if args.audit_waivers:
        report = build_waiver_audit_report(
            args.root_dir,
            ref=args.ref,
            today=today,
            warning_window_days=args.warning_window_days,
        )
        print_report(report, args.format)
        return 1 if report["errors"] else 0

    report = build_report(
        args.root_dir,
        scope=args.scope,
        ref=args.ref,
        paths=args.path,
        today=today,
    )
    print_report(report, args.format)
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
