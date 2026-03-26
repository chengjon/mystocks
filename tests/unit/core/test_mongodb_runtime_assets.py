from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_mongodb_runtime_assets_use_27017_and_mongosh() -> None:
    for rel in ['docker/mongodb.yml', 'config/docker/mongodb.yml', 'config/docker-infra/mongodb.yml']:
        text = (REPO_ROOT / rel).read_text()
        assert '${MONGODB_PORT:-27017}:27017' in text
        assert 'mongosh' in text
        assert 'mongo", "--eval"' not in text


def test_mongodb_compose_assets_pin_supported_image_version() -> None:
    for rel in [
        'docker/mongodb.yml',
        'docker/monitoring-stack.yml',
        'config/docker/mongodb.yml',
        'config/docker/monitoring-stack.yml',
        'config/docker-infra/mongodb.yml',
        'config/docker-infra/monitoring-stack.yml',
    ]:
        text = (REPO_ROOT / rel).read_text()
        assert 'image: mongo:7.0.5' in text
        assert 'image: mongo:latest' not in text


def test_mongodb_compose_assets_mount_repo_level_config_directory() -> None:
    for rel in [
        'docker/mongodb.yml',
        'docker/monitoring-stack.yml',
        'config/docker/mongodb.yml',
        'config/docker/monitoring-stack.yml',
        'config/docker-infra/mongodb.yml',
        'config/docker-infra/monitoring-stack.yml',
    ]:
        text = (REPO_ROOT / rel).read_text()
        assert '${MONGODB_CONFIG_PATH:-../mongodb}/mongod.conf:/etc/mongod.conf' in text
        assert '${MONGODB_CONFIG_PATH:-./config/mongodb}/mongod.conf:/etc/mongod.conf' not in text


def test_mongodb_runtime_config_file_exists_with_expected_basics() -> None:
    text = (REPO_ROOT / 'config/mongodb/mongod.conf').read_text()
    assert 'dbPath: /data/db' in text
    assert 'port: 27017' in text
    assert 'authorization: enabled' in text
    assert 'journal:' not in text


def test_mongodb_bootstrap_scripts_do_not_emit_deprecated_journal_option() -> None:
    for rel in [
        'docker/scripts/start-all.sh',
        'config/docker/scripts/start-all.sh',
        'config/docker-infra/scripts/start-all.sh',
    ]:
        text = (REPO_ROOT / rel).read_text()
        assert 'journal:' not in text


def test_mongodb_docs_reference_runtime_baseline() -> None:
    for rel in [
        'docker/README.md',
        'docker/QUICK_REFERENCE.md',
        'config/docker/README.md',
        'config/docker/QUICK_REFERENCE.md',
        'config/docker-infra/README.md',
        'config/docker-infra/QUICK_REFERENCE.md',
    ]:
        text = (REPO_ROOT / rel).read_text()
        assert 'MongoDB | localhost:27017' in text or 'MongoDB | localhost:27017 |' in text
        assert 'mongosh' in text
