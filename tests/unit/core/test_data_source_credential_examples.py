from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path('/opt/claude/mystocks_spec')


def test_versioned_data_source_credential_example_exists() -> None:
    text = (REPO_ROOT / 'docker/data-source-credentials.env.example').read_text()
    assert 'BYAPI_KEY=' in text
    assert 'BYAPI_BASE_URL=https://api.biyingapi.com' in text
    assert 'TUSHARE_TOKEN=' in text


def test_docker_docs_reference_copying_local_data_source_env_file() -> None:
    for rel in [
        'docker/README.md',
        'docker/QUICK_REFERENCE.md',
    ]:
        text = (REPO_ROOT / rel).read_text()
        assert 'data-source-credentials.env.example' in text
        assert '.env.data-sources.local' in text
