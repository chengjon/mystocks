from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path('/opt/claude/mystocks_spec')


def test_redis_runtime_assets_expose_role_aware_contract() -> None:
    text = (REPO_ROOT / 'config/docker/docker-compose.prod.yml').read_text()
    assert '127.0.0.1:6379:6379' in text
    assert 'redis-cli' in text
    assert 'REDIS_PASSWORD' in text
    assert 'REDIS_CELERY_BROKER_DB' in text
    assert 'REDIS_CELERY_RESULT_DB' in text


def test_redis_runtime_config_file_exists_with_expected_basics() -> None:
    text = (REPO_ROOT / 'config/redis/redis.conf').read_text()
    assert 'bind 0.0.0.0' in text
    assert 'port 6379' in text
    assert 'appendonly yes' in text


def test_redis_docs_reference_role_aware_runtime_baseline() -> None:
    for rel in [
        'config/docker/README.md',
        'config/docker/QUICK_REFERENCE.md',
        'config/docker-infra/README.md',
        'config/docker-infra/QUICK_REFERENCE.md',
    ]:
        text = (REPO_ROOT / rel).read_text()
        assert 'Redis' in text
        assert '6379' in text
        assert 'REDIS_APP_CACHE_DB' in text
        assert 'REDIS_CELERY_BROKER_DB' in text
        assert 'check_redis_runtime_health.sh' in text
