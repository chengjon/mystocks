from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path('/opt/claude/mystocks_spec')


def test_backend_compose_exposes_data_source_credential_placeholders() -> None:
    text = (REPO_ROOT / 'config/docker/docker-compose.prod.yml').read_text()
    assert 'BYAPI_KEY' in text
    assert 'BYAPI_BASE_URL' in text
    assert 'TUSHARE_TOKEN' in text


def test_docker_docs_describe_non_git_credential_runtime_contract() -> None:
    for rel in [
        'config/docker/README.md',
        'config/docker/QUICK_REFERENCE.md',
        'config/docker-infra/README.md',
        'config/docker-infra/QUICK_REFERENCE.md',
    ]:
        text = (REPO_ROOT / rel).read_text()
        assert 'BYAPI_KEY' in text
        assert 'TUSHARE_TOKEN' in text
        assert '不提交' in text or '不要提交' in text or 'not commit' in text.lower()
