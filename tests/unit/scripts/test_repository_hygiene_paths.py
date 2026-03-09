from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_pytest_coverage_json_is_configured_under_reports_coverage() -> None:
    pytest_ini = (PROJECT_ROOT / "pytest.ini").read_text(encoding="utf-8")

    assert "--cov-report=json:reports/coverage/coverage.json" in pytest_ini


def test_backup_related_defaults_point_to_var_backups() -> None:
    backup_manager = (PROJECT_ROOT / "src" / "infrastructure" / "backup_recovery" / "backup_manager.py").read_text(
        encoding="utf-8"
    )
    backup_scheduler = (
        PROJECT_ROOT / "src" / "infrastructure" / "backup_recovery" / "backup_scheduler.py"
    ).read_text(encoding="utf-8")
    sync_sources = (PROJECT_ROOT / "scripts" / "sync_sources.py").read_text(encoding="utf-8")
    migration_script = (PROJECT_ROOT / "scripts" / "migrations" / "migrate_watchlist_to_monitoring.py").read_text(
        encoding="utf-8"
    )

    assert 'backup_base_path: str = "var/backups"' in backup_manager
    assert 'backup_base_path: str = "var/backups"' in backup_scheduler
    assert 'Path("var/backups/data_source_registry")' in sync_sources
    assert 'backup_dir: str = "var/backups"' in migration_script
    assert 'default="var/backups"' in migration_script


def test_review_artifacts_are_converged_under_reports_reviews() -> None:
    assert not (PROJECT_ROOT / "reviews").exists()
    assert (PROJECT_ROOT / "reports" / "reviews").is_dir()


def test_archived_materials_are_converged_under_archive_root() -> None:
    assert not (PROJECT_ROOT / "archived").exists()
    assert (PROJECT_ROOT / "archive" / "legacy-root-archived").is_dir()


def test_docs_report_sprawl_directories_are_converged_under_reports() -> None:
    assert not (PROJECT_ROOT / "docs" / "completion_reports").exists()
    assert not (PROJECT_ROOT / "docs" / "monitoring_reports").exists()
    assert not (PROJECT_ROOT / "docs" / "phase_reports").exists()
    assert not (PROJECT_ROOT / "docs" / "test_reports").exists()

    assert (PROJECT_ROOT / "reports" / "completion").is_dir()
    assert (PROJECT_ROOT / "reports" / "monitoring").is_dir()
    assert (PROJECT_ROOT / "reports" / "phase").is_dir()
    assert (PROJECT_ROOT / "reports" / "tests").is_dir()


def test_docs_archive_and_legacy_are_converged_under_archive_root() -> None:
    assert not (PROJECT_ROOT / "docs" / "archive").exists()
    assert not (PROJECT_ROOT / "docs" / "legacy").exists()

    assert (PROJECT_ROOT / "archive" / "docs").is_dir()
    assert (PROJECT_ROOT / "archive" / "legacy-docs").is_dir()
