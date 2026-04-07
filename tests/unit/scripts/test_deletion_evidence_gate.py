from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "compliance" / "deletion_evidence_gate.py"


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def bootstrap_repo(
    tmp_path: Path,
    *,
    evidence_entries: list[dict[str, object]] | None = None,
    waiver_entries: list[dict[str, object]] | None = None,
) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()

    write_file(
        repo / "governance" / "deletion-evidence.yaml",
        yaml.safe_dump({"version": 1, "entries": evidence_entries or []}, allow_unicode=True, sort_keys=False),
    )
    write_file(
        repo / "governance" / "waivers" / "deletion-evidence-waivers.yaml",
        yaml.safe_dump({"version": 1, "waivers": waiver_entries or []}, allow_unicode=True, sort_keys=False),
    )

    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Test User")
    git(repo, "config", "user.email", "test@example.com")
    return repo


def commit_all(repo: Path, message: str) -> None:
    git(repo, "add", ".")
    git(repo, "commit", "-m", message)


def run_gate(repo: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    assert SCRIPT_PATH.exists(), f"missing script: {SCRIPT_PATH}"
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--root-dir", str(repo), "--format", "json", *extra_args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def test_blocks_directory_deletion_without_preexisting_evidence(tmp_path: Path) -> None:
    repo = bootstrap_repo(tmp_path)
    write_file(repo / "reports" / "legacy" / "one.md", "one\n")
    write_file(repo / "reports" / "legacy" / "two.md", "two\n")
    commit_all(repo, "bootstrap")

    git(repo, "rm", "-r", "reports/legacy")
    completed = run_gate(repo, "--scope", "staged")

    assert completed.returncode == 1, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["directory_targets"] == ["reports/legacy"]
    assert payload["errors"][0]["kind"] == "directory"
    assert payload["errors"][0]["path"] == "reports/legacy"
    assert payload["errors"][0]["mode"] == "missing-evidence"


def test_allows_directory_deletion_with_preexisting_evidence(tmp_path: Path) -> None:
    repo = bootstrap_repo(
        tmp_path,
        evidence_entries=[
            {
                "path": "reports/legacy",
                "kind": "directory",
                "status": "approved",
                "code_path_verdict": "safe_to_delete",
                "function_tree_verdict": "重复冗余",
                "owner": "repo-governance",
            }
        ],
    )
    write_file(repo / "reports" / "legacy" / "one.md", "one\n")
    write_file(repo / "reports" / "legacy" / "two.md", "two\n")
    commit_all(repo, "bootstrap")

    git(repo, "rm", "-r", "reports/legacy")
    completed = run_gate(repo, "--scope", "staged")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["results"][0]["mode"] == "evidence"
    assert payload["summary"]["errors"] == 0


def test_blocks_three_document_deletions_without_exact_evidence(tmp_path: Path) -> None:
    repo = bootstrap_repo(tmp_path)
    write_file(repo / "docs" / "keep.md", "keep\n")
    write_file(repo / "docs" / "old-a.md", "a\n")
    write_file(repo / "reports" / "keep.md", "keep\n")
    write_file(repo / "reports" / "old-b.md", "b\n")
    write_file(repo / "archive" / "keep.md", "keep\n")
    write_file(repo / "archive" / "old-c.md", "c\n")
    commit_all(repo, "bootstrap")

    git(repo, "rm", "docs/old-a.md", "reports/old-b.md", "archive/old-c.md")
    completed = run_gate(repo, "--scope", "staged")

    assert completed.returncode == 1, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["deleted_documents"] == 3
    assert sorted(payload["document_targets"]) == ["archive/old-c.md", "docs/old-a.md", "reports/old-b.md"]


def test_allows_three_document_deletions_with_exact_preexisting_evidence(tmp_path: Path) -> None:
    repo = bootstrap_repo(
        tmp_path,
        evidence_entries=[
            {
                "path": "docs/old-a.md",
                "kind": "document",
                "status": "approved",
                "code_path_verdict": "safe_to_delete",
                "function_tree_verdict": "正式下线",
                "owner": "docs",
            },
            {
                "path": "reports/old-b.md",
                "kind": "document",
                "status": "approved",
                "code_path_verdict": "safe_to_delete",
                "function_tree_verdict": "正式下线",
                "owner": "reports",
            },
            {
                "path": "archive/old-c.md",
                "kind": "document",
                "status": "approved",
                "code_path_verdict": "safe_to_delete",
                "function_tree_verdict": "正式下线",
                "owner": "archive",
            },
        ],
    )
    write_file(repo / "docs" / "keep.md", "keep\n")
    write_file(repo / "docs" / "old-a.md", "a\n")
    write_file(repo / "reports" / "keep.md", "keep\n")
    write_file(repo / "reports" / "old-b.md", "b\n")
    write_file(repo / "archive" / "keep.md", "keep\n")
    write_file(repo / "archive" / "old-c.md", "c\n")
    commit_all(repo, "bootstrap")

    git(repo, "rm", "docs/old-a.md", "reports/old-b.md", "archive/old-c.md")
    completed = run_gate(repo, "--scope", "staged")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert {item["mode"] for item in payload["results"]} == {"evidence"}


def test_rejects_in_commit_evidence_for_directory_deletion(tmp_path: Path) -> None:
    repo = bootstrap_repo(tmp_path)
    write_file(repo / "reports" / "legacy" / "one.md", "one\n")
    write_file(repo / "reports" / "legacy" / "two.md", "two\n")
    commit_all(repo, "bootstrap")

    write_file(
        repo / "governance" / "deletion-evidence.yaml",
        yaml.safe_dump(
            {
                "version": 1,
                "entries": [
                    {
                        "path": "reports/legacy",
                        "kind": "directory",
                        "status": "approved",
                        "code_path_verdict": "safe_to_delete",
                        "function_tree_verdict": "重复冗余",
                        "owner": "repo-governance",
                    }
                ],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
    )
    git(repo, "add", "governance/deletion-evidence.yaml")
    git(repo, "rm", "-r", "reports/legacy")

    completed = run_gate(repo, "--scope", "staged")

    assert completed.returncode == 1, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["errors"][0]["mode"] == "missing-evidence"


def test_allows_emergency_waiver_until_expiry(tmp_path: Path) -> None:
    repo = bootstrap_repo(
        tmp_path,
        waiver_entries=[
            {
                "path": "reports/legacy",
                "kind": "directory",
                "reason": "Emergency cleanup after explicit user approval",
                "owner": "repo-governance",
                "approved_by_user": "chat-approved",
                "approved_on": "2026-04-07",
                "expires_on": "2026-04-08",
                "ticket_or_context": "governance-emergency-1",
            }
        ],
    )
    write_file(repo / "reports" / "legacy" / "one.md", "one\n")
    write_file(repo / "reports" / "legacy" / "two.md", "two\n")
    commit_all(repo, "bootstrap")

    git(repo, "rm", "-r", "reports/legacy")
    completed = run_gate(repo, "--scope", "staged", "--today", "2026-04-07")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["results"][0]["mode"] == "waiver"


def test_rejects_expired_or_wildcard_waiver(tmp_path: Path) -> None:
    repo = bootstrap_repo(
        tmp_path,
        waiver_entries=[
            {
                "path": "reports/*",
                "kind": "directory",
                "reason": "Wildcard should not be accepted",
                "owner": "repo-governance",
                "approved_by_user": "chat-approved",
                "approved_on": "2026-04-07",
                "expires_on": "2026-04-08",
                "ticket_or_context": "bad-waiver",
            },
            {
                "path": "reports/legacy",
                "kind": "directory",
                "reason": "Expired emergency waiver",
                "owner": "repo-governance",
                "approved_by_user": "chat-approved",
                "approved_on": "2026-04-06",
                "expires_on": "2026-04-06",
                "ticket_or_context": "expired-waiver",
            },
        ],
    )
    write_file(repo / "reports" / "legacy" / "one.md", "one\n")
    write_file(repo / "reports" / "legacy" / "two.md", "two\n")
    commit_all(repo, "bootstrap")

    git(repo, "rm", "-r", "reports/legacy")
    completed = run_gate(repo, "--scope", "staged", "--today", "2026-04-07")

    assert completed.returncode == 1, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["errors"][0]["mode"] == "invalid-waiver"
    assert "expired" in payload["errors"][0]["message"]
