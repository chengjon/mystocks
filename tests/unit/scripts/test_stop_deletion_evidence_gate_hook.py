from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


HOOK_PATH = Path(__file__).resolve().parents[3] / ".claude" / "hooks" / "stop-deletion-evidence-gate.sh"


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def bootstrap_repo(tmp_path: Path, *, evidence_content: str | None = None) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    write_file(repo / "governance" / "deletion-evidence.yaml", evidence_content or "version: 1\nentries: []\n")
    write_file(repo / "governance" / "waivers" / "deletion-evidence-waivers.yaml", "version: 1\nwaivers: []\n")
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Test User")
    git(repo, "config", "user.email", "test@example.com")
    return repo


def run_hook(repo: Path, *, today: str | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(HOOK_PATH.parents[2])
    env["DELETION_EVIDENCE_GATE_ROOT_DIR"] = str(repo)
    if today:
        env["DELETION_EVIDENCE_GATE_TODAY"] = today

    return subprocess.run(
        [str(HOOK_PATH)],
        input=json.dumps({"session_id": "test-session"}),
        text=True,
        capture_output=True,
        cwd=repo,
        env=env,
        check=True,
    )


def test_stop_hook_returns_empty_json_when_no_governed_deletions(tmp_path: Path) -> None:
    repo = bootstrap_repo(tmp_path)
    write_file(repo / "docs" / "keep.md", "keep\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "bootstrap")

    completed = run_hook(repo)

    assert completed.stdout.strip() == "{}"


def test_stop_hook_blocks_directory_deletion_without_preexisting_evidence(tmp_path: Path) -> None:
    repo = bootstrap_repo(tmp_path)
    write_file(repo / "reports" / "legacy" / "one.md", "one\n")
    write_file(repo / "reports" / "legacy" / "two.md", "two\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "bootstrap")

    (repo / "reports" / "legacy" / "one.md").unlink()
    (repo / "reports" / "legacy" / "two.md").unlink()

    completed = run_hook(repo)

    payload = json.loads(completed.stdout)
    assert payload["decision"] == "block"
    assert "reports/legacy" in payload["reason"]


def test_stop_hook_allows_directory_deletion_with_preexisting_evidence(tmp_path: Path) -> None:
    repo = bootstrap_repo(
        tmp_path,
        evidence_content=(
            "version: 1\n"
            "entries:\n"
            "  - path: reports/legacy\n"
            "    kind: directory\n"
            "    status: approved\n"
            "    code_path_verdict: safe_to_delete\n"
            "    function_tree_verdict: 重复冗余\n"
            "    owner: repo-governance\n"
        ),
    )
    write_file(repo / "reports" / "legacy" / "one.md", "one\n")
    write_file(repo / "reports" / "legacy" / "two.md", "two\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "bootstrap")

    (repo / "reports" / "legacy" / "one.md").unlink()
    (repo / "reports" / "legacy" / "two.md").unlink()

    completed = run_hook(repo)

    assert completed.stdout.strip() == "{}"
