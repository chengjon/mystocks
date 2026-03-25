#!/usr/bin/env python3
"""Mainline governance scope gate for AI task cards (v0.2)."""

from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Install with: pip install pyyaml") from exc

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:  # pragma: no cover
    raise SystemExit("jsonschema is required. Install with: pip install jsonschema") from exc

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCHEMA = PROJECT_ROOT / "governance/mainline/schemas/ai-task-card.schema.json"
DEFAULT_REPORT = PROJECT_ROOT / "governance/mainline/reports/mainline-governance-report.json"
DEFAULT_FUNCTION_TREE_CATALOG = PROJECT_ROOT / "governance/function-tree/catalog.yaml"
DEFAULT_FUNCTION_TREE_SCHEMA = PROJECT_ROOT / "governance/function-tree/schema.json"

SUMMARY_FIELDS = (
    "change_purpose",
    "modified_scope",
    "dependency_changes",
    "legacy_logic_impact",
    "rollback_ready",
    "risk_and_rollback_point",
)

FUNCTION_TREE_ENTRYPOINTS = ("governance", "api", "frontend", "core", "tests", "operations")
FUNCTION_TREE_SHARED_SYNC_FILES = ("docs/FUNCTION_TREE.md",)

GOVERNANCE_META_PATTERNS = (
    "governance/mainline/task-cards/*.yaml",
    "governance/mainline/task-cards/*.yml",
    "governance/mainline/reports/mainline-governance-report.json",
    "governance/mainline/templates/ai-task-card.yaml",
    "governance/mainline/schemas/ai-task-card.schema.json",
    ".github/workflows/mainline-governance.yml",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate AI mainline governance task card and changed scope")
    parser.add_argument("--task-card", help="Task card YAML path (relative to project root)")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA), help="Task card JSON schema path")
    parser.add_argument("--base-sha", help="Git base SHA (defaults to event payload or HEAD~1)")
    parser.add_argument("--head-sha", default="HEAD", help="Git head SHA (default: HEAD)")
    parser.add_argument("--report", default=str(DEFAULT_REPORT), help="Output report JSON path")
    parser.add_argument(
        "--max-secondary-budget",
        type=float,
        default=20.0,
        help="Hard cap for secondary_change_budget_percent",
    )
    parser.add_argument(
        "--fail-on-empty-diff",
        action="store_true",
        help="Fail when git diff has no changed files",
    )
    return parser.parse_args()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def to_project_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def rel_to_project(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("task card root must be an object")
    return payload


def load_function_tree_catalog(
    catalog_path: Path = DEFAULT_FUNCTION_TREE_CATALOG,
    schema_path: Path = DEFAULT_FUNCTION_TREE_SCHEMA,
) -> dict[str, Any]:
    if not catalog_path.exists():
        raise FileNotFoundError(f"function tree catalog not found: {catalog_path}")
    if not schema_path.exists():
        raise FileNotFoundError(f"function tree schema not found: {schema_path}")

    catalog = load_yaml(catalog_path)
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(catalog), key=lambda item: list(item.absolute_path))
    if errors:
        location = ".".join(str(part) for part in errors[0].absolute_path) or "<root>"
        raise ValueError(f"function tree catalog schema violation at {location}: {errors[0].message}")
    validate_function_tree_catalog_integrity(catalog)
    return catalog


def validate_function_tree_catalog_integrity(catalog: dict[str, Any]) -> None:
    seen_domain_ids: set[str] = set()
    seen_node_ids: set[str] = set()

    for domain in catalog.get("domains", []):
        domain_id = str(domain.get("id", "")).strip()
        if domain_id in seen_domain_ids:
            raise ValueError(f"duplicate function tree domain id: {domain_id}")
        seen_domain_ids.add(domain_id)

        for node in domain.get("nodes", []):
            node_id = str(node.get("id", "")).strip()
            if node_id in seen_node_ids:
                raise ValueError(f"duplicate function tree node id: {node_id}")
            seen_node_ids.add(node_id)

            entrypoints = node.get("entrypoints", {})
            for paths in entrypoints.values():
                if not isinstance(paths, list):
                    continue
                for raw_path in paths:
                    if not isinstance(raw_path, str) or any(token in raw_path for token in "*?["):
                        continue
                    if not (PROJECT_ROOT / raw_path).exists():
                        raise ValueError(f"missing literal function tree entrypoint path: {raw_path}")


def list_entrypoint_paths(node: dict[str, Any], categories: list[str] | None = None) -> list[str]:
    entrypoints = node.get("entrypoints", {})
    selected_categories = categories or list(FUNCTION_TREE_ENTRYPOINTS)
    paths: list[str] = []
    for category in selected_categories:
        values = entrypoints.get(category, [])
        if isinstance(values, list):
            paths.extend(str(value) for value in values if str(value).strip())
    return sorted(set(paths))


def is_shared_function_tree_sync_file(path: str) -> bool:
    return matches_any(path, list(FUNCTION_TREE_SHARED_SYNC_FILES))


def find_domain_by_id(catalog: dict[str, Any], domain_id: str) -> dict[str, Any] | None:
    for domain in catalog.get("domains", []):
        if domain.get("id") == domain_id:
            return domain
    return None


def find_node_by_id(domain: dict[str, Any], node_id: str) -> dict[str, Any] | None:
    for node in domain.get("nodes", []):
        if node.get("id") == node_id:
            return node
    return None


def collect_matched_domains(catalog: dict[str, Any], changed_files: list[str]) -> list[dict[str, Any]]:
    matched_domains: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for domain in catalog.get("domains", []):
        for node in domain.get("nodes", []):
            patterns = list(node.get("coverage_paths", [])) + list_entrypoint_paths(node)
            if any(
                not is_shared_function_tree_sync_file(path) and matches_any(path, patterns) for path in changed_files
            ):
                domain_id = str(domain.get("id", "")).strip()
                if domain_id and domain_id not in seen_ids:
                    matched_domains.append(domain)
                    seen_ids.add(domain_id)
                break
    return matched_domains


def validate_function_tree_mapping(
    card: dict[str, Any], changed_files: list[str], catalog: dict[str, Any] | None = None
) -> tuple[list[str], dict[str, Any]]:
    task_type = str(card.get("classification", {}).get("task_type", "")).strip()
    function_tree = card.get("function_tree")
    metrics: dict[str, Any] = {
        "matched_domain_ids": [],
        "matched_business_domain_ids": [],
        "function_tree_declared_matches": [],
        "function_tree_declared_entrypoint_paths": [],
    }

    violations: list[str] = []
    if not function_tree:
        if task_type == "feature":
            violations.append("feature task requires function_tree metadata")
        return violations, metrics

    if catalog is None:
        catalog = load_function_tree_catalog()

    domain_id = str(function_tree.get("domain_id", "")).strip()
    node_id = str(function_tree.get("node_id", "")).strip()
    affected_entrypoints = list(function_tree.get("affected_entrypoints") or [])
    update_status = str(function_tree.get("update_status", "")).strip()
    secondary_domains = [str(item).strip() for item in list(function_tree.get("secondary_domains") or []) if str(item).strip()]
    exemption_reason = str(function_tree.get("exemption_reason", "")).strip()

    invalid_entrypoints = [item for item in affected_entrypoints if item not in FUNCTION_TREE_ENTRYPOINTS]
    if invalid_entrypoints:
        violations.append(f"unsupported function_tree.affected_entrypoints: {', '.join(sorted(set(invalid_entrypoints)))}")

    declared_domain = find_domain_by_id(catalog, domain_id)
    if declared_domain is None:
        violations.append(f"unknown function_tree.domain_id: {domain_id}")
        return violations, metrics

    declared_node = find_node_by_id(declared_domain, node_id)
    if declared_node is None:
        violations.append(f"unknown function_tree.node_id: {node_id}")
        return violations, metrics

    declared_patterns = list(declared_node.get("coverage_paths", []))
    declared_entrypoint_paths = list_entrypoint_paths(declared_node, affected_entrypoints)
    metrics["function_tree_declared_entrypoint_paths"] = declared_entrypoint_paths

    declared_matches = [
        path
        for path in changed_files
        if not is_shared_function_tree_sync_file(path)
        and (matches_any(path, declared_patterns) or matches_any(path, declared_entrypoint_paths))
    ]
    metrics["function_tree_declared_matches"] = declared_matches

    if changed_files and not declared_matches:
        violations.append("declared function_tree mapping did not match changed files")

    matched_domains = collect_matched_domains(catalog, changed_files)
    matched_domain_ids = [str(domain.get("id", "")).strip() for domain in matched_domains if str(domain.get("id", "")).strip()]
    matched_business_domain_ids = [
        domain_id for domain_id in matched_domain_ids if find_domain_by_id(catalog, domain_id).get("category") == "business"
    ]
    metrics["matched_domain_ids"] = matched_domain_ids
    metrics["matched_business_domain_ids"] = matched_business_domain_ids

    if len(matched_business_domain_ids) > 1:
        undeclared_domains = [
            item for item in matched_business_domain_ids if item != domain_id and item not in secondary_domains
        ]
        if undeclared_domains and not exemption_reason:
            violations.append(
                "cross-domain business diff requires function_tree.secondary_domains or exemption_reason"
            )

    if bool(declared_domain.get("mirror_to_function_tree")) and update_status == "not-needed":
        mirrored_entrypoint_hits = [
            path
            for path in changed_files
            if not is_shared_function_tree_sync_file(path) and matches_any(path, declared_entrypoint_paths)
        ]
        if mirrored_entrypoint_hits:
            violations.append(
                "mirrored business entrypoint changes cannot use update_status=not-needed"
            )

    return violations, metrics


def resolve_event_context() -> tuple[str | None, str | None, int | None]:
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        return None, None, None

    try:
        event_payload = json.loads(Path(event_path).read_text(encoding="utf-8"))
    except Exception:
        return None, None, None

    pr_payload = event_payload.get("pull_request")
    if not isinstance(pr_payload, dict):
        return None, None, None

    base_sha = pr_payload.get("base", {}).get("sha")
    head_sha = pr_payload.get("head", {}).get("sha")
    pr_number = event_payload.get("number")
    if not isinstance(pr_number, int):
        pr_number = None
    return base_sha, head_sha, pr_number


def resolve_task_card_path(task_card_arg: str | None) -> Path:
    if task_card_arg:
        path = to_project_path(task_card_arg)
        if path.exists():
            return path
        raise FileNotFoundError(f"task card not found: {path}")

    _, _, pr_number = resolve_event_context()
    if pr_number is not None:
        path = PROJECT_ROOT / f"governance/mainline/task-cards/pr-{pr_number}.yaml"
        if path.exists():
            return path

    raise FileNotFoundError(
        "task card not provided/found; pass --task-card or create governance/mainline/task-cards/pr-<id>.yaml"
    )


def resolve_base_head(base_arg: str | None, head_arg: str) -> tuple[str, str]:
    base_sha = base_arg
    head_sha = head_arg

    event_base, event_head, _ = resolve_event_context()
    if not base_sha:
        base_sha = event_base
    if head_sha == "HEAD" and event_head:
        head_sha = event_head

    if not base_sha:
        probe = subprocess.run(
            ["git", "rev-parse", "HEAD~1"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if probe.returncode != 0:
            raise RuntimeError("unable to resolve base sha; pass --base-sha")
        base_sha = probe.stdout.strip()

    if not head_sha:
        raise RuntimeError("unable to resolve head sha")

    return base_sha, head_sha


def run_git_diff(base_sha: str, head_sha: str) -> list[str]:
    diff_proc = subprocess.run(
        ["git", "diff", "--name-only", f"{base_sha}...{head_sha}"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if diff_proc.returncode != 0:
        raise RuntimeError(diff_proc.stderr.strip() or "git diff failed")

    files = []
    for line in diff_proc.stdout.splitlines():
        candidate = normalize_git_diff_path(line)
        if candidate:
            files.append(PurePosixPath(candidate).as_posix())
    return sorted(set(files))


def normalize_git_diff_path(raw_path: str) -> str:
    candidate = raw_path.strip()
    if not candidate:
        return ""

    if len(candidate) >= 2 and candidate[0] == candidate[-1] == '"':
        try:
            unescaped = ast.literal_eval(candidate)
        except (SyntaxError, ValueError):
            unescaped = candidate[1:-1]

        try:
            candidate = unescaped.encode("latin-1").decode("utf-8")
        except (AttributeError, UnicodeEncodeError, UnicodeDecodeError):
            candidate = str(unescaped)

    return candidate


def path_matches(path: str, pattern: str) -> bool:
    normalized_path = PurePosixPath(path).as_posix().lstrip("/")
    normalized_pattern = PurePosixPath(pattern).as_posix().lstrip("/")

    if not normalized_pattern:
        return False

    if normalized_pattern.endswith("/**"):
        prefix = normalized_pattern[:-3].rstrip("/")
        return normalized_path == prefix or normalized_path.startswith(prefix + "/")

    if normalized_pattern.endswith("/"):
        prefix = normalized_pattern.rstrip("/")
        return normalized_path == prefix or normalized_path.startswith(prefix + "/")

    return fnmatch.fnmatch(normalized_path, normalized_pattern)


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(path_matches(path, pattern) for pattern in patterns)


def filter_effective_changed_files(changed_files: list[str]) -> list[str]:
    """Exclude governance/meta files from ratio denominators to avoid dilution."""
    return [path for path in changed_files if not matches_any(path, list(GOVERNANCE_META_PATTERNS))]


def validate_schema(card: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(card), key=lambda item: list(item.absolute_path))
    violations: list[str] = []
    for item in errors:
        location = ".".join(str(part) for part in item.absolute_path) or "<root>"
        violations.append(f"schema: {location}: {item.message}")
    return violations


def check_feature_openspec(card: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    task_type = card.get("classification", {}).get("task_type")
    openspec = card.get("openspec", {})

    change_id = str(openspec.get("change_id", "")).strip()
    approval_status = str(openspec.get("approval_status", "")).strip()

    if task_type == "feature":
        if not change_id:
            violations.append("feature task requires openspec.change_id")
        if approval_status != "approved":
            violations.append("feature task requires openspec.approval_status=approved")

    return violations


def check_summary(card: dict[str, Any]) -> list[str]:
    delivery = card.get("delivery", {})
    required = bool(delivery.get("six_line_summary_required"))
    summary = delivery.get("six_line_summary", {})

    violations: list[str] = []
    if not required:
        return violations

    if not isinstance(summary, dict):
        return ["delivery.six_line_summary must be an object when six_line_summary_required=true"]

    for field in SUMMARY_FIELDS:
        value = summary.get(field)
        if not isinstance(value, str) or not value.strip():
            violations.append(f"delivery.six_line_summary.{field} must be a non-empty string")
    return violations


def check_scope_and_drift(
    card: dict[str, Any], effective_changed_files: list[str], task_card_rel: str
) -> tuple[list[str], dict[str, Any]]:
    scope = card.get("scope", {})
    governance = card.get("governance", {})

    allowed_paths = list(scope.get("allowed_paths") or [])
    forbidden_paths = list(scope.get("forbidden_paths") or [])
    auto_allowed = [task_card_rel]

    out_of_scope = [
        path
        for path in effective_changed_files
        if not matches_any(path, allowed_paths) and not matches_any(path, auto_allowed)
    ]
    forbidden_hits = [path for path in effective_changed_files if matches_any(path, forbidden_paths)]

    total_changed = len(effective_changed_files)
    drift_rate = (len(out_of_scope) / total_changed * 100.0) if total_changed else 0.0
    threshold = float(governance.get("mainline_drift_threshold_percent", 0))

    violations: list[str] = []
    if forbidden_hits:
        violations.append(f"forbidden paths modified: {', '.join(forbidden_hits)}")
    if drift_rate > threshold + 1e-9:
        violations.append(
            f"mainline drift exceeded: {drift_rate:.2f}% > {threshold:.2f}% "
            f"(out_of_scope={len(out_of_scope)}, total={total_changed})"
        )

    metrics = {
        "effective_changed_files": total_changed,
        "out_of_scope_files": out_of_scope,
        "forbidden_hits": forbidden_hits,
        "drift_rate_percent": round(drift_rate, 3),
        "drift_threshold_percent": threshold,
    }
    return violations, metrics


def check_secondary_budget(
    card: dict[str, Any], effective_changed_files: list[str], max_secondary_budget: float
) -> tuple[list[str], dict[str, Any]]:
    classification = card.get("classification", {})
    governance_approval = card.get("governance", {}).get("approval", {})

    secondary_type = str(classification.get("secondary_type", "none"))
    budget = float(classification.get("secondary_change_budget_percent", 0))
    secondary_paths = list(classification.get("secondary_allowed_paths") or [])

    violations: list[str] = []
    secondary_files: list[str] = []
    secondary_ratio = 0.0

    if secondary_type == "none":
        if budget != 0:
            violations.append("secondary_type=none requires secondary_change_budget_percent=0")
        if secondary_paths:
            violations.append("secondary_type=none requires empty secondary_allowed_paths")
    else:
        if budget <= 0:
            violations.append("secondary task requires budget > 0")
        if budget > max_secondary_budget:
            violations.append(
                f"secondary budget exceeds hard cap: {budget:.2f}% > {max_secondary_budget:.2f}%"
            )
        if not secondary_paths:
            violations.append("secondary task requires secondary_allowed_paths")

        if effective_changed_files and secondary_paths:
            secondary_files = [path for path in effective_changed_files if matches_any(path, secondary_paths)]
            secondary_ratio = len(secondary_files) / len(effective_changed_files) * 100.0
            if secondary_ratio > budget + 1e-9:
                violations.append(
                    f"secondary change ratio exceeded: {secondary_ratio:.2f}% > {budget:.2f}% "
                    f"(secondary={len(secondary_files)}, total={len(effective_changed_files)})"
                )

        required_flag = bool(governance_approval.get("required"))
        approved_by = str(governance_approval.get("approved_by", "")).strip()
        secondary_approved = bool(governance_approval.get("secondary_approved"))
        if not required_flag or not approved_by:
            violations.append("secondary task requires governance.approval.required=true and approved_by")
        if not secondary_approved:
            violations.append("secondary task requires governance.approval.secondary_approved=true")

    metrics = {
        "secondary_type": secondary_type,
        "secondary_budget_percent": budget,
        "secondary_changed_files": secondary_files,
        "secondary_ratio_percent": round(secondary_ratio, 3),
    }
    return violations, metrics


def check_phase_threshold(card: dict[str, Any]) -> list[str]:
    governance = card.get("governance", {})
    phase = governance.get("phase")
    threshold = float(governance.get("mainline_drift_threshold_percent", 0))

    violations: list[str] = []
    phase_limits = {
        "phase_a_pr_hard_gate": 5.0,
        "phase_b_dual_hard_gate": 2.0,
        "phase_c_zero_drift": 0.0,
    }

    if phase in phase_limits and threshold > phase_limits[phase] + 1e-9:
        violations.append(
            f"phase threshold mismatch: {phase} requires drift threshold <= {phase_limits[phase]:.2f}"
        )

    return violations


def write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    args = parse_args()

    report_path = to_project_path(args.report)
    schema_path = to_project_path(args.schema)

    report: dict[str, Any] = {
        "generated_at": now_iso(),
        "pass": False,
        "violations": [],
        "warnings": [],
    }

    try:
        task_card_path = resolve_task_card_path(args.task_card)
        task_card_rel = rel_to_project(task_card_path)
        report["task_card"] = task_card_rel

        if not schema_path.exists():
            raise FileNotFoundError(f"schema not found: {schema_path}")

        card = load_yaml(task_card_path)
        schema = load_json(schema_path)

        schema_violations = validate_schema(card, schema)
        report["violations"].extend(schema_violations)

        base_sha, head_sha = resolve_base_head(args.base_sha, args.head_sha)
        report["base_sha"] = base_sha
        report["head_sha"] = head_sha

        changed_files = run_git_diff(base_sha, head_sha)
        report["changed_files"] = changed_files

        if not changed_files:
            report["warnings"].append("no changed files detected in git diff")
            if args.fail_on_empty_diff:
                report["violations"].append("no changed files detected in git diff (fail-on-empty-diff)")

        effective_changed_files = filter_effective_changed_files(changed_files)
        report["effective_changed_file_list"] = effective_changed_files
        report["governance_meta_excluded_count"] = max(0, len(changed_files) - len(effective_changed_files))

        report["violations"].extend(check_feature_openspec(card))
        report["violations"].extend(check_summary(card))
        report["violations"].extend(check_phase_threshold(card))

        function_tree_catalog = load_function_tree_catalog()
        function_tree_violations, function_tree_metrics = validate_function_tree_mapping(
            card, changed_files, catalog=function_tree_catalog
        )
        report["violations"].extend(function_tree_violations)
        report.update(function_tree_metrics)

        scope_violations, scope_metrics = check_scope_and_drift(card, effective_changed_files, task_card_rel)
        report["violations"].extend(scope_violations)
        report.update(scope_metrics)

        secondary_violations, secondary_metrics = check_secondary_budget(
            card, effective_changed_files, args.max_secondary_budget
        )
        report["violations"].extend(secondary_violations)
        report.update(secondary_metrics)

        report["pass"] = len(report["violations"]) == 0

    except Exception as exc:  # pragma: no cover
        report["violations"].append(str(exc))

    write_report(report_path, report)

    print(f"[mainline-governance] report written: {report_path}")
    print(f"[mainline-governance] pass={report['pass']}")

    violations = report.get("violations", [])
    if violations:
        print("[mainline-governance] violations:")
        for violation in violations[:50]:
            print(f"- {violation}")

    return 0 if report.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
