from __future__ import annotations

import ast
import json
import re
import subprocess
from fnmatch import fnmatch
from pathlib import Path

import yaml

from scripts.maintenance.check_structure import (
    analyze_project,
    build_text_report,
    load_policy,
    main,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROJECT_POLICY_PATH = PROJECT_ROOT / "governance" / "mainline" / "policies" / "directory-structure.yaml"
CHECK_DIRECTORY_STRUCTURE_PATH = PROJECT_ROOT / "scripts" / "hooks" / "check_directory_structure.py"
TREE_LINT_PATH = PROJECT_ROOT / "scripts" / "tree-lint.sh"


def load_literal_collection(module_path: Path, assignment_name: str) -> list[str]:
    tree = ast.parse(module_path.read_text(encoding="utf-8"))

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == assignment_name:
                return ast.literal_eval(node.value)

    raise AssertionError(f"{assignment_name} not found in {module_path}")


def load_literal_collection_or_default(
    module_path: Path, assignment_name: str, default: list[str] | None = None
) -> list[str]:
    try:
        return load_literal_collection(module_path, assignment_name)
    except AssertionError:
        return [] if default is None else default


def load_shell_array(script_path: Path, array_name: str) -> list[str]:
    text = script_path.read_text(encoding="utf-8")
    match = re.search(rf"{array_name}=\(\n(.*?)\n\)", text, re.DOTALL)
    if not match:
        raise AssertionError(f"{array_name} not found in {script_path}")

    return re.findall(r'"([^"]+)"', match.group(1))


def write_policy(path: Path) -> None:
    policy = {
        "root": {
            "allowed_files": ["README.md"],
            "allowed_directories": ["src", "docs"],
            "workflow_exception_files": [
                {
                    "path": "TASK.md",
                    "reason": "workflow-owned task contract remains in root",
                }
            ],
            "tolerated_files": [
                {
                    "path": "LEGACY_TASK.md",
                    "reason": "legacy workflow artifact",
                    "recommendation": "move into docs/reports/tasks/",
                }
            ],
            "tolerated_directories": [
                {
                    "path": "archived",
                    "reason": "legacy archive debt",
                    "recommendation": "consolidate into archive/",
                }
            ],
            "forbidden_file_patterns": [
                {
                    "pattern": "*.log",
                    "message": "runtime logs must not live in root",
                    "recommendation": "move to var/log/",
                },
                {
                    "pattern": ".coverage",
                    "message": "coverage files must not live in root",
                    "recommendation": "move to var/reports/coverage/",
                },
            ],
        },
        "scan": {"ignore_directory_names": ["node_modules", "__pycache__"]},
        "rules": [
            {
                "id": "reports-convergence",
                "severity": "warning",
                "match_any": ["docs/completion_reports/**", "reviews/**"],
                "message": "versioned evidence should converge under reports/",
                "recommendation": "move into reports/<domain>/",
            }
        ],
    }
    path.write_text(yaml.safe_dump(policy, sort_keys=False), encoding="utf-8")


def test_load_policy_reads_yaml(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.yaml"
    write_policy(policy_path)

    policy = load_policy(policy_path)

    assert policy["root"]["allowed_files"] == ["README.md"]
    assert policy["rules"][0]["id"] == "reports-convergence"


def test_analyze_project_reports_unexpected_root_file_as_error(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.yaml"
    project_root = tmp_path / "repo"
    project_root.mkdir()
    write_policy(policy_path)
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "src").mkdir()
    (project_root / "rogue.txt").write_text("oops", encoding="utf-8")

    result = analyze_project(project_root, load_policy(policy_path))

    assert result["summary"]["errors"] == 1
    assert result["errors"][0]["path"] == "rogue.txt"
    assert "unexpected root file" in result["errors"][0]["message"]


def test_analyze_project_reports_tolerated_root_entries_as_warning(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.yaml"
    project_root = tmp_path / "repo"
    project_root.mkdir()
    write_policy(policy_path)
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "src").mkdir()
    (project_root / "LEGACY_TASK.md").write_text("legacy", encoding="utf-8")
    (project_root / "archived").mkdir()

    result = analyze_project(project_root, load_policy(policy_path))

    assert result["summary"]["errors"] == 0
    assert result["summary"]["warnings"] == 2
    warning_paths = {item["path"] for item in result["warnings"]}
    assert warning_paths == {"LEGACY_TASK.md", "archived"}


def test_analyze_project_skips_workflow_exception_files_without_warning(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.yaml"
    project_root = tmp_path / "repo"
    project_root.mkdir()
    write_policy(policy_path)
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "src").mkdir()
    (project_root / "TASK.md").write_text("workflow contract", encoding="utf-8")

    result = analyze_project(project_root, load_policy(policy_path))

    assert result["summary"]["errors"] == 0
    assert result["summary"]["warnings"] == 0


def test_project_policy_allows_canonical_lifecycle_directories(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    project_root.mkdir()
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "docs").mkdir()
    (project_root / "reports").mkdir()
    (project_root / "archive").mkdir()
    (project_root / "var").mkdir()

    result = analyze_project(project_root, load_policy(PROJECT_POLICY_PATH))

    assert result["summary"]["errors"] == 0
    assert result["summary"]["warnings"] == 0


def test_project_policy_treats_task_artifacts_as_workflow_exceptions(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    project_root.mkdir()
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "docs").mkdir()
    (project_root / "TASK.md").write_text("workflow task", encoding="utf-8")
    (project_root / "TASK-REPORT.md").write_text("workflow report", encoding="utf-8")

    result = analyze_project(project_root, load_policy(PROJECT_POLICY_PATH))

    assert result["summary"]["errors"] == 0
    assert result["summary"]["warnings"] == 0


def test_project_policy_treats_hidden_workflow_exception_files_as_allowed(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    project_root.mkdir()
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "docs").mkdir()
    (project_root / ".FILE_OWNERSHIP").write_text("main", encoding="utf-8")

    result = analyze_project(project_root, load_policy(PROJECT_POLICY_PATH))

    assert result["summary"]["errors"] == 0
    assert result["summary"]["warnings"] == 0


def test_check_directory_structure_root_allowlist_covers_all_governed_explicit_root_entries() -> None:
    policy = load_policy(PROJECT_POLICY_PATH)
    hook_allowed_files = set(load_literal_collection(CHECK_DIRECTORY_STRUCTURE_PATH, "ALLOWED_ROOT_FILES"))
    hook_allowed_patterns = load_literal_collection_or_default(CHECK_DIRECTORY_STRUCTURE_PATH, "ALLOWED_ROOT_PATTERNS")

    governed_explicit_root_entries = set(policy["root"]["allowed_files"]) | {
        item["path"] for item in policy["root"].get("workflow_exception_files", [])
    }

    missing = sorted(
        entry
        for entry in governed_explicit_root_entries
        if entry not in hook_allowed_files and not any(fnmatch(entry, pattern) for pattern in hook_allowed_patterns)
    )

    assert missing == []


def test_project_policy_explicitly_governs_tracked_root_hidden_files() -> None:
    policy = load_policy(PROJECT_POLICY_PATH)

    completed = __import__("subprocess").run(
        ["git", "-C", str(PROJECT_ROOT), "ls-files", "--stage"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0

    tracked_root_hidden_files = {
        line.split("\t", 1)[1]
        for line in completed.stdout.splitlines()
        if "\t" in line
        and "/" not in line.split("\t", 1)[1]
        and line.split("\t", 1)[1].startswith(".")
    }

    explicitly_governed = set(policy["root"]["allowed_files"]) | {
        item["path"] for item in policy["root"].get("workflow_exception_files", [])
    } | {
        item["path"] for item in policy["root"].get("tolerated_files", [])
    }

    missing = sorted(tracked_root_hidden_files - explicitly_governed)

    assert missing == []


def test_tree_lint_allowlist_covers_governed_root_entries_relevant_to_runtime_scan() -> None:
    policy = load_policy(PROJECT_POLICY_PATH)
    tree_lint_allowed_files = set(load_shell_array(TREE_LINT_PATH, "ALLOWED_ROOT_FILES"))
    tree_lint_allowed_patterns = load_shell_array(TREE_LINT_PATH, "ALLOWED_ROOT_PATTERNS")

    governed_runtime_scanned_entries = (
        set(policy["root"]["allowed_files"])
        | {item["path"] for item in policy["root"].get("workflow_exception_files", [])}
    ) - {".gitignore", ".gitattributes"}

    missing = sorted(
        entry
        for entry in governed_runtime_scanned_entries
        if entry not in tree_lint_allowed_files and not any(fnmatch(entry, pattern) for pattern in tree_lint_allowed_patterns)
    )

    assert missing == []


def test_tree_lint_has_no_root_warnings_in_current_repo() -> None:
    completed = subprocess.run(
        ["bash", str(TREE_LINT_PATH)],
        check=False,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )

    assert completed.returncode == 0
    assert "[WARN] Root file" not in completed.stdout
    assert "[tree-lint] No violations detected." in completed.stdout


def test_gitignored_local_only_root_files_stay_outside_explicit_policy_governance() -> None:
    policy = load_policy(PROJECT_POLICY_PATH)
    hook_allowed_files = set(load_literal_collection(CHECK_DIRECTORY_STRUCTURE_PATH, "ALLOWED_ROOT_FILES"))
    tree_lint_allowed_files = set(load_shell_array(TREE_LINT_PATH, "ALLOWED_ROOT_FILES"))
    gitignore_text = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
    explicitly_governed = set(policy["root"]["allowed_files"]) | {
        item["path"] for item in policy["root"].get("workflow_exception_files", [])
    } | {
        item["path"] for item in policy["root"].get("tolerated_files", [])
    }

    local_only_root_files = {
        ".aider.conf.yml": ".aider*",
        ".aider.model.metadata.json": ".aider*",
        ".aider.model.settings.yml": ".aider*",
        ".aiderignore": ".aider*",
        ".env.async_monitoring": ".env.*",
        ".env.data-sources.local": ".env.*.local",
        "opencode.json": "opencode.json",
        "tui.json": "tui.json",
    }

    for rel, ignore_pattern in local_only_root_files.items():
        local_path = PROJECT_ROOT / rel
        if local_path.exists():
            completed = subprocess.run(
                ["git", "-C", str(PROJECT_ROOT), "check-ignore", "-q", rel],
                check=False,
            )
            assert completed.returncode == 0, f"{rel} should stay gitignored as a local-only root file"
        else:
            assert ignore_pattern in gitignore_text, f"{rel} should keep a matching .gitignore rule"
        assert rel not in explicitly_governed, f"{rel} should not enter explicit root policy governance"
        assert rel not in hook_allowed_files, f"{rel} should not enter hook root allowlist"
        assert rel not in tree_lint_allowed_files, f"{rel} should not enter tree-lint root allowlist"


def test_analyze_project_skips_gitignored_root_local_only_file(tmp_path: Path) -> None:
    policy = load_policy(PROJECT_POLICY_PATH)
    project_root = tmp_path / "repo"
    project_root.mkdir()
    (project_root / ".git").mkdir()
    (project_root / ".gitignore").write_text("opencode.json\n", encoding="utf-8")
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "docs").mkdir()
    (project_root / "opencode.json").write_text('{"local": true}\n', encoding="utf-8")

    subprocess.run(["git", "init"], cwd=project_root, check=False, capture_output=True, text=True)

    result = analyze_project(project_root, policy)

    assert result["summary"]["errors"] == 0
    assert result["summary"]["warnings"] == 0


def test_analyze_project_reports_root_runtime_artifact_as_error(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.yaml"
    project_root = tmp_path / "repo"
    project_root.mkdir()
    write_policy(policy_path)
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "src").mkdir()
    (project_root / "server.log").write_text("log", encoding="utf-8")

    result = analyze_project(project_root, load_policy(policy_path))

    assert result["summary"]["errors"] == 1
    assert result["errors"][0]["path"] == "server.log"
    assert result["errors"][0]["recommendation"] == "move to var/log/"


def test_analyze_project_reports_hidden_root_runtime_artifact_as_error(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    project_root.mkdir()
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "docs").mkdir()
    (project_root / ".coverage").write_text("coverage", encoding="utf-8")

    result = analyze_project(project_root, load_policy(PROJECT_POLICY_PATH))

    assert result["summary"]["errors"] == 1
    assert result["errors"][0]["path"] == ".coverage"
    assert result["errors"][0]["rule_id"] == "root-forbidden-file"


def test_analyze_project_applies_recursive_rules(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.yaml"
    project_root = tmp_path / "repo"
    project_root.mkdir()
    write_policy(policy_path)
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "src").mkdir()
    report_dir = project_root / "docs" / "completion_reports"
    report_dir.mkdir(parents=True)
    (report_dir / "summary.md").write_text("report", encoding="utf-8")

    result = analyze_project(project_root, load_policy(policy_path))

    assert result["summary"]["errors"] == 0
    assert result["summary"]["warnings"] == 1
    assert result["warnings"][0]["rule_id"] == "reports-convergence"
    assert result["warnings"][0]["path"] == "docs/completion_reports/summary.md"


def test_build_text_report_contains_summary_counts(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.yaml"
    project_root = tmp_path / "repo"
    project_root.mkdir()
    write_policy(policy_path)
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "src").mkdir()
    (project_root / "LEGACY_TASK.md").write_text("legacy", encoding="utf-8")

    result = analyze_project(project_root, load_policy(policy_path))
    report = build_text_report(result)

    assert "errors: 0" in report
    assert "warnings: 1" in report


def test_analysis_result_is_json_serializable(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.yaml"
    project_root = tmp_path / "repo"
    project_root.mkdir()
    write_policy(policy_path)
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "src").mkdir()

    result = analyze_project(project_root, load_policy(policy_path))

    payload = json.dumps(result, ensure_ascii=False)
    assert "\"summary\"" in payload


def test_scope_paths_ignore_unrelated_existing_root_errors(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.yaml"
    project_root = tmp_path / "repo"
    project_root.mkdir()
    write_policy(policy_path)
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "src").mkdir()
    (project_root / "rogue.txt").write_text("old debt", encoding="utf-8")
    (project_root / "docs").mkdir()
    (project_root / "docs" / "guide.md").write_text("edited", encoding="utf-8")

    result = analyze_project(project_root, load_policy(policy_path), paths=["docs/guide.md"])

    assert result["summary"]["errors"] == 0
    assert result["summary"]["warnings"] == 0


def test_scope_paths_report_new_root_file_error(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.yaml"
    project_root = tmp_path / "repo"
    project_root.mkdir()
    write_policy(policy_path)
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "src").mkdir()
    (project_root / "new-note.txt").write_text("new", encoding="utf-8")

    result = analyze_project(project_root, load_policy(policy_path), paths=["new-note.txt"])

    assert result["summary"]["errors"] == 1
    assert result["errors"][0]["path"] == "new-note.txt"


def test_scope_paths_report_recursive_rule_matches_only_for_changed_paths(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.yaml"
    project_root = tmp_path / "repo"
    project_root.mkdir()
    write_policy(policy_path)
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "src").mkdir()

    report_dir = project_root / "docs" / "completion_reports"
    report_dir.mkdir(parents=True)
    report_file = report_dir / "summary.md"
    report_file.write_text("report", encoding="utf-8")

    policy = load_policy(policy_path)
    policy["rules"][0]["report_once"] = True

    result = analyze_project(project_root, policy, paths=["docs/completion_reports/summary.md"])

    assert result["summary"]["errors"] == 0
    assert result["summary"]["warnings"] == 1
    assert result["warnings"][0]["path"] == "docs/completion_reports"


def test_empty_scope_paths_produce_no_findings(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.yaml"
    project_root = tmp_path / "repo"
    project_root.mkdir()
    write_policy(policy_path)
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "src").mkdir()
    (project_root / "rogue.txt").write_text("old debt", encoding="utf-8")

    result = analyze_project(project_root, load_policy(policy_path), paths=[])

    assert result["summary"]["errors"] == 0
    assert result["summary"]["warnings"] == 0


def test_main_without_path_scope_runs_full_scan(tmp_path: Path, monkeypatch, capsys) -> None:
    policy_path = tmp_path / "policy.yaml"
    project_root = tmp_path / "repo"
    project_root.mkdir()
    write_policy(policy_path)
    (project_root / "README.md").write_text("ok", encoding="utf-8")
    (project_root / "src").mkdir()
    (project_root / "rogue.txt").write_text("oops", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "check_structure.py",
            str(project_root),
            "--policy",
            str(policy_path),
            "--format",
            "json",
        ],
    )

    exit_code = main()
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert exit_code == 1
    assert payload["summary"]["errors"] == 1
    assert payload["errors"][0]["path"] == "rogue.txt"
