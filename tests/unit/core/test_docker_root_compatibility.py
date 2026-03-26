from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path("/opt/claude/mystocks_spec")


def test_root_docker_directory_exists_with_expected_assets() -> None:
    docker_root = REPO_ROOT / "docker"
    assert docker_root.is_dir()

    expected_files = [
        "README.md",
        "QUICK_REFERENCE.md",
        "SECURITY_GUIDE.md",
        "docker-compose.prod.yml",
        "docker-compose.test.yml",
        "monitoring-stack.yml",
        "mongodb.yml",
        "grafana.yml",
        "prometheus.yml",
        "scripts/start-all.sh",
        "scripts/stop-all.sh",
    ]

    for rel in expected_files:
        assert (docker_root / rel).exists(), f"docker root asset missing: {rel}"


def test_config_docker_paths_are_compatibility_symlinks() -> None:
    compat_paths = [
        REPO_ROOT / "config" / "docker",
        REPO_ROOT / "config" / "docker-infra",
    ]

    for path in compat_paths:
        assert path.is_symlink(), f"{path} should be a symlink"
        assert path.resolve() == (REPO_ROOT / "docker").resolve()


def test_root_compose_entrypoints_are_symlinks_into_root_docker() -> None:
    expected = {
        "docker-compose.prod.yml": "docker/docker-compose.prod.yml",
        "docker-compose.test.yml": "docker/docker-compose.test.yml",
        "monitoring-stack.yml": "docker/monitoring-stack.yml",
    }

    for rel, target in expected.items():
        path = REPO_ROOT / rel
        assert path.is_symlink(), f"{rel} should be a symlink"
        assert path.resolve() == (REPO_ROOT / target).resolve()
