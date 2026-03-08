from __future__ import annotations

import argparse
import json
import subprocess
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_PATH = PROJECT_ROOT / "governance" / "mainline" / "policies" / "directory-structure.yaml"
SEVERITY_TO_BUCKET = {"error": "errors", "warning": "warnings", "info": "infos"}


def load_policy(policy_path: str | Path) -> dict[str, Any]:
    resolved_path = Path(policy_path).resolve()
    if not resolved_path.exists():
        raise FileNotFoundError(f"治理策略文件不存在: {resolved_path}")

    with resolved_path.open("r", encoding="utf-8") as file:
        policy = yaml.safe_load(file) or {}

    if not isinstance(policy, dict):
        raise ValueError("目录治理策略必须是 YAML 映射对象")

    return policy


def normalize_entries(entries: list[Any] | None) -> dict[str, dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}
    for entry in entries or []:
        if isinstance(entry, str):
            normalized[entry] = {}
            continue
        if not isinstance(entry, dict) or "path" not in entry:
            raise ValueError("tolerated entry 必须是字符串或包含 path 的对象")
        normalized[entry["path"]] = {key: value for key, value in entry.items() if key != "path"}
    return normalized


def matches_any(path_value: str, patterns: list[str] | None) -> bool:
    return any(fnmatch(path_value, pattern) for pattern in patterns or [])


def pattern_anchor(pattern: str) -> str:
    wildcard_positions = [
        position for position, character in enumerate(pattern) if character in {"*", "?", "["}
    ]
    if not wildcard_positions:
        return pattern.rstrip("/")

    anchor = pattern[: min(wildcard_positions)].rstrip("/")
    return anchor


def make_finding(
    severity: str,
    path_value: str,
    message: str,
    *,
    rule_id: str,
    recommendation: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    finding = {
        "severity": severity,
        "path": path_value,
        "rule_id": rule_id,
        "message": message,
    }
    if recommendation:
        finding["recommendation"] = recommendation
    if reason:
        finding["reason"] = reason
    return finding


def create_empty_result(project_root: Path, policy_path: str | Path | None = None) -> dict[str, Any]:
    return {
        "project_root": str(project_root.resolve()),
        "policy_path": str(Path(policy_path).resolve()) if policy_path else None,
        "errors": [],
        "warnings": [],
        "infos": [],
        "summary": {"errors": 0, "warnings": 0, "infos": 0},
    }


def normalize_scope_paths(paths: list[str] | None) -> list[str] | None:
    if paths is None:
        return None

    normalized: set[str] = set()
    for raw_path in paths:
        path_value = raw_path.strip()
        if not path_value:
            continue
        if path_value.startswith("./"):
            path_value = path_value[2:]
        normalized_path = Path(path_value).as_posix().strip("/")
        if normalized_path:
            normalized.add(normalized_path)

    return sorted(normalized)


def current_scope_root_entries(paths: list[str] | None) -> set[str] | None:
    normalized_paths = normalize_scope_paths(paths)
    if normalized_paths is None:
        return None

    root_entries: set[str] = set()
    for path_value in normalized_paths:
        root_entries.add(path_value.split("/", 1)[0])
    return root_entries


def filter_scannable_paths(scannable_paths: list[str], paths: list[str] | None) -> list[str]:
    normalized_paths = normalize_scope_paths(paths)
    if normalized_paths is None:
        return scannable_paths

    allowed_paths: set[str] = set()
    for path_value in normalized_paths:
        parts = Path(path_value).parts
        prefix = []
        for part in parts:
            prefix.append(part)
            allowed_paths.add(Path(*prefix).as_posix())

    return [path_value for path_value in scannable_paths if path_value in allowed_paths]


def staged_paths(project_root: Path) -> list[str]:
    command = [
        "git",
        "-C",
        str(project_root),
        "diff",
        "--cached",
        "--name-only",
        "--diff-filter=ACMR",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "无法读取 staged 文件列表")

    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def append_finding(result: dict[str, Any], finding: dict[str, Any]) -> None:
    bucket = SEVERITY_TO_BUCKET[finding["severity"]]
    result[bucket].append(finding)
    result["summary"][bucket] += 1


def analyze_root_entries(
    project_root: Path,
    policy: dict[str, Any],
    result: dict[str, Any],
    *,
    paths: list[str] | None = None,
) -> None:
    root_policy = policy.get("root", {})
    allowed_files = set(root_policy.get("allowed_files", []))
    allowed_directories = set(root_policy.get("allowed_directories", []))
    tolerated_files = normalize_entries(root_policy.get("tolerated_files"))
    tolerated_directories = normalize_entries(root_policy.get("tolerated_directories"))
    forbidden_file_patterns = root_policy.get("forbidden_file_patterns", [])
    forbidden_directory_patterns = root_policy.get("forbidden_directory_patterns", [])
    scoped_root_entries = current_scope_root_entries(paths)

    for entry in sorted(project_root.iterdir(), key=lambda item: item.name):
        if entry.name.startswith("."):
            continue
        if scoped_root_entries is not None and entry.name not in scoped_root_entries:
            continue

        if entry.is_dir():
            matched_rule = next(
                (rule for rule in forbidden_directory_patterns if fnmatch(entry.name, rule["pattern"])),
                None,
            )
            if matched_rule:
                append_finding(
                    result,
                    make_finding(
                        "error",
                        entry.name,
                        matched_rule["message"],
                        rule_id="root-forbidden-directory",
                        recommendation=matched_rule.get("recommendation"),
                    ),
                )
                continue

            if entry.name in allowed_directories:
                continue

            tolerated = tolerated_directories.get(entry.name)
            if tolerated is not None:
                append_finding(
                    result,
                    make_finding(
                        "warning",
                        entry.name,
                        "legacy root directory should be converged",
                        rule_id="root-tolerated-directory",
                        recommendation=tolerated.get("recommendation"),
                        reason=tolerated.get("reason"),
                    ),
                )
                continue

            append_finding(
                result,
                make_finding(
                    "error",
                    entry.name,
                    "unexpected root directory",
                    rule_id="root-unexpected-directory",
                ),
            )
            continue

        matched_rule = next(
            (rule for rule in forbidden_file_patterns if fnmatch(entry.name, rule["pattern"])),
            None,
        )
        if matched_rule:
            append_finding(
                result,
                make_finding(
                    "error",
                    entry.name,
                    matched_rule["message"],
                    rule_id="root-forbidden-file",
                    recommendation=matched_rule.get("recommendation"),
                ),
            )
            continue

        if entry.name in allowed_files:
            continue

        tolerated = tolerated_files.get(entry.name)
        if tolerated is not None:
            append_finding(
                result,
                make_finding(
                    "warning",
                    entry.name,
                    "legacy root file should be converged",
                    rule_id="root-tolerated-file",
                    recommendation=tolerated.get("recommendation"),
                    reason=tolerated.get("reason"),
                ),
            )
            continue

        append_finding(
            result,
            make_finding(
                "error",
                entry.name,
                "unexpected root file",
                rule_id="root-unexpected-file",
            ),
        )


def iter_scannable_paths(project_root: Path, policy: dict[str, Any]) -> list[str]:
    ignore_names = set(policy.get("scan", {}).get("ignore_directory_names", []))
    discovered_paths: list[str] = []

    for current_root, dir_names, file_names in project_root.walk(top_down=True):
        dir_names[:] = [
            name for name in dir_names if not name.startswith(".") and name not in ignore_names
        ]

        current_path = Path(current_root)
        if current_path != project_root:
            discovered_paths.append(current_path.relative_to(project_root).as_posix())

        for file_name in file_names:
            if file_name.startswith("."):
                continue
            discovered_paths.append((current_path / file_name).relative_to(project_root).as_posix())

    return sorted(set(discovered_paths))


def apply_recursive_rules(
    project_root: Path,
    policy: dict[str, Any],
    result: dict[str, Any],
    *,
    paths: list[str] | None = None,
) -> None:
    rules = policy.get("rules", [])
    scannable_paths = iter_scannable_paths(project_root, policy)
    scoped_paths = filter_scannable_paths(scannable_paths, paths)

    for path_value in scoped_paths:
        for rule in rules:
            if rule.get("report_once"):
                continue
            if not matches_any(path_value, rule.get("match_any")):
                continue

            severity = rule.get("severity", "warning")
            append_finding(
                result,
                make_finding(
                    severity,
                    path_value,
                    rule["message"],
                    rule_id=rule["id"],
                    recommendation=rule.get("recommendation"),
                ),
            )

    for rule in rules:
        if not rule.get("report_once"):
            continue

        matched_anchors: set[str] = set()
        for pattern in rule.get("match_any", []):
            anchor = pattern_anchor(pattern)
            if not anchor:
                continue
            if any(fnmatch(path_value, pattern) for path_value in scoped_paths):
                matched_anchors.add(anchor)

        for anchor in sorted(matched_anchors):
            severity = rule.get("severity", "warning")
            append_finding(
                result,
                make_finding(
                    severity,
                    anchor,
                    rule["message"],
                    rule_id=rule["id"],
                    recommendation=rule.get("recommendation"),
                ),
            )


def analyze_project(
    project_root: str | Path,
    policy: dict[str, Any],
    *,
    policy_path: str | Path | None = None,
    paths: list[str] | None = None,
) -> dict[str, Any]:
    resolved_root = Path(project_root).resolve()
    result = create_empty_result(resolved_root, policy_path)
    analyze_root_entries(resolved_root, policy, result, paths=paths)
    apply_recursive_rules(resolved_root, policy, result, paths=paths)
    return result


def build_text_report(result: dict[str, Any]) -> str:
    lines = [
        "Directory governance report",
        f"project_root: {result['project_root']}",
        f"policy_path: {result['policy_path']}",
        f"errors: {result['summary']['errors']}",
        f"warnings: {result['summary']['warnings']}",
        f"infos: {result['summary']['infos']}",
    ]

    for bucket_name in ("errors", "warnings", "infos"):
        findings = result[bucket_name]
        if not findings:
            continue
        lines.append(f"{bucket_name}:")
        for finding in findings:
            line = f"- [{finding['rule_id']}] {finding['path']}: {finding['message']}"
            if finding.get("recommendation"):
                line += f" | recommendation: {finding['recommendation']}"
            if finding.get("reason"):
                line += f" | reason: {finding['reason']}"
            lines.append(line)

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="策略清单驱动的目录治理检查器")
    parser.add_argument("project_root", nargs="?", default=str(PROJECT_ROOT))
    parser.add_argument("--policy", default=str(DEFAULT_POLICY_PATH))
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--path", action="append", dest="paths", default=[])
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    policy = load_policy(args.policy)
    path_scope = args.paths
    if args.staged:
        path_scope = staged_paths(Path(args.project_root))
    result = analyze_project(args.project_root, policy, policy_path=args.policy, paths=path_scope)

    if args.format == "json":
        if not args.quiet:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if not args.quiet:
            print(build_text_report(result))

    if result["summary"]["errors"] > 0:
        return 1
    if args.strict and result["summary"]["warnings"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
