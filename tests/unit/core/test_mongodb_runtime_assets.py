from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path('/opt/claude/mystocks_spec')


def test_mongodb_runtime_assets_use_27017_and_mongosh() -> None:
    for rel in ['config/docker/mongodb.yml', 'config/docker-infra/mongodb.yml']:
        text = (REPO_ROOT / rel).read_text()
        assert '${MONGODB_PORT:-27017}:27017' in text
        assert 'mongosh' in text
        assert 'mongo", "--eval"' not in text


def test_mongodb_runtime_config_file_exists_with_expected_basics() -> None:
    text = (REPO_ROOT / 'config/mongodb/mongod.conf').read_text()
    assert 'dbPath: /data/db' in text
    assert 'port: 27017' in text
    assert 'authorization: enabled' in text


def test_mongodb_docs_reference_runtime_baseline() -> None:
    for rel in [
        'config/docker/README.md',
        'config/docker/QUICK_REFERENCE.md',
        'config/docker-infra/README.md',
        'config/docker-infra/QUICK_REFERENCE.md',
    ]:
        text = (REPO_ROOT / rel).read_text()
        assert 'MongoDB | localhost:27017' in text or 'MongoDB | localhost:27017 |' in text
        assert 'mongosh' in text
