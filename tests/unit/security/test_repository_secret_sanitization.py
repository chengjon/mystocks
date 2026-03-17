from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
ALLOWLIST_PATH_FRAGMENTS = (
    "tests/security/test_security_vulnerabilities/",
)

# Keep these patterns generic enough to avoid reintroducing leaked values.
BANNED_PATTERNS = {
    "provider_api_keys": r"sk-[A-Za-z0-9]{20,}",
    "real_bearer_tokens": r"Bearer (?!dev-mock-token-for-development\b)[A-Za-z0-9._-]{20,}",
    "private_lan_hosts": r"192\.168\.\d{1,3}\.\d{1,3}",
}


def _git_grep(pattern: str) -> list[str]:
    completed = subprocess.run(
        ["git", "grep", "-nI", "-P", pattern, "--", "."],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    if completed.returncode == 1:
        return []
    if completed.returncode != 0:
        raise AssertionError(f"git grep failed for pattern {pattern!r}: {completed.stderr.strip()}")

    findings = []
    for line in completed.stdout.splitlines():
        if not line.strip():
            continue
        if any(fragment in line for fragment in ALLOWLIST_PATH_FRAGMENTS):
            continue
        findings.append(line)

    return findings


def test_repository_does_not_contain_known_secret_leak_shapes() -> None:
    findings: list[str] = []
    for label, pattern in BANNED_PATTERNS.items():
        for line in _git_grep(pattern):
            findings.append(f"[{label}] {line}")

    assert not findings, "仓库仍包含敏感硬编码痕迹:\n" + "\n".join(findings[:200])
