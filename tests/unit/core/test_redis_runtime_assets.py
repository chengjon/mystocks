from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_monitoring_stack_assets_include_host_reachable_redis() -> None:
    for rel in [
        "docker/monitoring-stack.yml",
        "config/docker/monitoring-stack.yml",
        "config/docker-infra/monitoring-stack.yml",
    ]:
        text = (REPO_ROOT / rel).read_text()
        assert "container_name: mystocks-redis" in text
        assert "image: redis:7-alpine" in text
        assert '${REDIS_PORT:-6379}:6379' in text


def test_docker_start_scripts_wait_for_redis_runtime_health() -> None:
    for rel in [
        "docker/scripts/start-all.sh",
        "config/docker/scripts/start-all.sh",
        "config/docker-infra/scripts/start-all.sh",
    ]:
        text = (REPO_ROOT / rel).read_text()
        assert "check_redis_runtime_health.sh" in text
        assert "Redis" in text
