from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path('/opt/claude/mystocks_spec')


def test_start_scripts_load_local_data_source_env_file() -> None:
    for rel in [
        'config/docker/scripts/start-all.sh',
        'config/docker-infra/scripts/start-all.sh',
    ]:
        text = (REPO_ROOT / rel).read_text()
        assert '.env.data-sources.local' in text
        assert 'BYAPI_KEY' in text
        assert 'TUSHARE_TOKEN' in text
