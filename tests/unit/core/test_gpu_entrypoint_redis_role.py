from pathlib import Path


def test_gpu_entrypoint_uses_role_aware_redis_healthcheck():
    text = Path('/opt/claude/mystocks_spec/src/gpu/api_system/deployment/entrypoint.sh').read_text(encoding='utf-8')

    assert "REDIS_TOOLING_DB" in text
    assert "REDIS_HOST" in text
    assert "REDIS_PORT" in text
