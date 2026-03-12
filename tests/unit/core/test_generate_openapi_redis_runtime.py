from pathlib import Path


def test_generate_openapi_uses_role_aware_redis_defaults() -> None:
    text = Path('/opt/claude/mystocks_spec/scripts/generate_openapi.py').read_text(encoding='utf-8')

    assert 'REDIS_URL' not in text
    assert 'redis://localhost:6379/0' not in text
    assert 'REDIS_HOST' in text
    assert 'REDIS_PORT' in text
    assert 'REDIS_APP_CACHE_DB' in text
    assert 'REDIS_CELERY_BROKER_DB' in text
    assert 'REDIS_CELERY_RESULT_DB' in text
