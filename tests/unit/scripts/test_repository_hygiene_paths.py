from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_docs_root_entrypoints_are_frozen_to_index_and_function_tree() -> None:
    docs_root_files = sorted(path.name for path in (PROJECT_ROOT / "docs").iterdir() if path.is_file())

    assert docs_root_files == [
        "FUNCTION_TREE.md",
        "INDEX.md",
    ]


def test_pytest_coverage_json_is_configured_under_reports_coverage() -> None:
    pytest_ini = (PROJECT_ROOT / "pytest.ini").read_text(encoding="utf-8")

    assert "--cov-report=json:reports/coverage/coverage.json" in pytest_ini


def test_mypy_cache_dir_is_configured_under_var_cache() -> None:
    mypy_ini = (PROJECT_ROOT / "mypy.ini").read_text(encoding="utf-8")

    assert "cache_dir = var/cache/mypy" in mypy_ini


def test_root_runtime_coverage_and_cache_artifacts_are_absent() -> None:
    assert not (PROJECT_ROOT / ".coverage").exists()
    assert not (PROJECT_ROOT / "coverage.xml").exists()
    assert not (PROJECT_ROOT / "htmlcov").exists()
    assert not (PROJECT_ROOT / ".pytest_cache").exists()
    assert not (PROJECT_ROOT / ".mypy_cache").exists()


def test_retired_root_aider_files_are_absent() -> None:
    assert not (PROJECT_ROOT / ".aider.conf.yml").exists()
    assert not (PROJECT_ROOT / ".aider.model.metadata.json").exists()
    assert not (PROJECT_ROOT / ".aider.model.settings.yml").exists()
    assert not (PROJECT_ROOT / ".aiderignore").exists()


def test_root_tui_config_is_not_versioned_as_repo_entrypoint() -> None:
    assert not (PROJECT_ROOT / "tui.json").exists()


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


def test_phase1_governance_approval_doc_is_converged_under_reports_reviews() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    reviews_index = (PROJECT_ROOT / "docs" / "reports" / "reviews" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    unified_execution_plan = (
        PROJECT_ROOT / "openspec" / "changes" / "restructure-frontend-directory" / "UNIFIED_EXECUTION_PLAN.md"
    ).read_text(encoding="utf-8")

    name = "PHASE1_GOVERNANCE_APPROVAL.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "reports" / "reviews" / name).is_file()
    assert name.removesuffix(".md") not in guides_index
    assert f"reviews/{name}" in reports_index
    assert name.removesuffix(".md") in reviews_index
    assert f"reports/reviews/{name}" in cleanup_index_root or f"reviews/{name}" in cleanup_index_root
    assert "docs/reports/reviews/PHASE1_GOVERNANCE_APPROVAL.md" in unified_execution_plan


def test_directory_organization_review_doc_is_converged_under_reports_reviews() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    reviews_index = (PROJECT_ROOT / "docs" / "reports" / "reviews" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    directory_review = (
        PROJECT_ROOT / "docs" / "reports" / "reviews" / "DIRECTORY_ORGANIZATION_REVIEW.md"
    ).read_text(encoding="utf-8")

    name = "DIRECTORY_ORGANIZATION_REVIEW.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "reports" / "reviews" / name).is_file()
    assert name.removesuffix(".md") not in guides_index
    assert f"reviews/{name}" in reports_index
    assert name.removesuffix(".md") in reviews_index
    assert f"reports/reviews/{name}" in cleanup_index_root or f"reviews/{name}" in cleanup_index_root
    assert "../cleanup/directory-organization/DIRECTORY_ORGANIZATION_PLAN.md" in directory_review


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


def test_reports_readme_remains_canonical_historical_evidence_trunk() -> None:
    docs_readme = (PROJECT_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    reports_readme = (PROJECT_ROOT / "docs" / "reports" / "README.md").read_text(encoding="utf-8")

    assert "/opt/claude/mystocks_spec/docs/reports/README.md" in docs_readme
    assert "Historical Evidence Trunk" in reports_readme
    assert "/opt/claude/mystocks_spec/architecture/STANDARDS.md" in reports_readme
    assert "/opt/claude/mystocks_spec/docs/reports/documentation-governance/" in reports_readme


def test_docs_archive_and_legacy_are_converged_under_archive_root() -> None:
    assert not (PROJECT_ROOT / "docs" / "archive").exists()
    assert not (PROJECT_ROOT / "docs" / "legacy").exists()

    assert (PROJECT_ROOT / "archive" / "docs").is_dir()
    assert (PROJECT_ROOT / "archive" / "legacy-docs").is_dir()


def test_duplicate_docs_entrypoints_are_archived_out_of_docs_root() -> None:
    assert not (PROJECT_ROOT / "docs" / "AGENTS_1.md").exists()
    assert not (PROJECT_ROOT / "docs" / "CLAUDE_1.md").exists()
    assert not (PROJECT_ROOT / "docs" / "IFLOW_1.md").exists()

    assert (PROJECT_ROOT / "archive" / "docs" / "duplicate-entrypoints" / "AGENTS_1.md").exists()
    assert (PROJECT_ROOT / "archive" / "docs" / "duplicate-entrypoints" / "CLAUDE_1.md").exists()
    assert (PROJECT_ROOT / "archive" / "docs" / "duplicate-entrypoints" / "IFLOW_1.md").exists()


def test_next_steps_governance_doc_is_converged_under_docs_architecture_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    architecture_index = (PROJECT_ROOT / "docs" / "architecture" / "INDEX.md").read_text(encoding="utf-8")
    docs_index = (PROJECT_ROOT / "docs" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    name = "NEXT_STEPS_GOVERNANCE.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "architecture" / name).is_file()
    assert name.removesuffix(".md") not in guides_index
    assert f"architecture/{name}" in docs_index
    assert name.removesuffix(".md") in architecture_index
    assert f"architecture/{name}" in cleanup_index_root


def test_config_splitting_guide_is_converged_under_docs_architecture_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    architecture_index = (PROJECT_ROOT / "docs" / "architecture" / "INDEX.md").read_text(encoding="utf-8")
    docs_index = (PROJECT_ROOT / "docs" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    name = "CONFIG_SPLITTING_GUIDE.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "architecture" / name).is_file()
    assert name.removesuffix(".md") not in guides_index
    assert f"architecture/{name}" in docs_index
    assert name.removesuffix(".md") in architecture_index
    assert f"architecture/{name}" in cleanup_index_root


def test_page_config_usage_guide_is_converged_under_docs_architecture_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    architecture_index = (PROJECT_ROOT / "docs" / "architecture" / "INDEX.md").read_text(encoding="utf-8")
    docs_index = (PROJECT_ROOT / "docs" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    page_config_model = (PROJECT_ROOT / "docs" / "architecture" / "PAGE_CONFIG_MODEL.md").read_text(
        encoding="utf-8"
    )
    openspec_audit_summary = (PROJECT_ROOT / "docs" / "reports" / "openspec_audit_summary.md").read_text(
        encoding="utf-8"
    )
    openspec_tasks = (
        PROJECT_ROOT / "openspec" / "changes" / "extend-frontend-config-model" / "tasks.md"
    ).read_text(encoding="utf-8")

    name = "PAGE_CONFIG_USAGE_GUIDE.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "architecture" / name).is_file()
    assert name.removesuffix(".md") not in guides_index
    assert f"architecture/{name}" in docs_index
    assert name.removesuffix(".md") in architecture_index
    assert f"architecture/{name}" in cleanup_index_root
    assert "./PAGE_CONFIG_USAGE_GUIDE.md" in page_config_model
    assert "docs/architecture/PAGE_CONFIG_USAGE_GUIDE.md" in openspec_audit_summary
    assert "docs/architecture/PAGE_CONFIG_USAGE_GUIDE.md" in openspec_tasks


def test_docs_claude_doc_is_converged_under_overview_family() -> None:
    docs_index = (PROJECT_ROOT / "docs" / "INDEX.md").read_text(encoding="utf-8")
    overview_index = (PROJECT_ROOT / "docs" / "overview" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    overview_claude = (PROJECT_ROOT / "docs" / "overview" / "claude.md").read_text(encoding="utf-8")
    redis_report = (
        PROJECT_ROOT / "docs" / "reports" / "REDIS_THREE_DATABASE_ARCHITECTURE_INTEGRATION_REPORT.md"
    ).read_text(encoding="utf-8")
    saga_fullstack = (
        PROJECT_ROOT / "docs" / "reports" / "PHASE2_3_SAGA_FULLSTACK_COMPLETION_REPORT.md"
    ).read_text(encoding="utf-8")
    saga_migration = (
        PROJECT_ROOT / "docs" / "reports" / "PHASE2_3_SAGA_MIGRATION_COMPLETION_REPORT.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "CLAUDE.md").exists()
    assert (PROJECT_ROOT / "docs" / "overview" / "claude.md").is_file()
    assert "- 📄 [CLAUDE](CLAUDE.md)" not in docs_index
    assert "overview/claude.md" in docs_index
    assert "claude" in overview_index
    assert "overview/claude.md" in cleanup_index_root
    assert "Three-Database Architecture" in overview_claude
    assert "docs/overview/claude.md" in redis_report
    assert "/docs/overview/claude.md" in saga_fullstack
    assert "/docs/overview/claude.md" in saga_migration


def test_docs_iflow_doc_is_converged_under_overview_family() -> None:
    docs_index = (PROJECT_ROOT / "docs" / "INDEX.md").read_text(encoding="utf-8")
    overview_index = (PROJECT_ROOT / "docs" / "overview" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    readme_root = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    guides_readme = (PROJECT_ROOT / "docs" / "guides" / "README.md").read_text(encoding="utf-8")
    doc_management = (
        PROJECT_ROOT / "docs" / "guides" / "documentation" / "文档管理指南.md"
    ).read_text(encoding="utf-8")
    leak_report = (
        PROJECT_ROOT / "docs" / "reports" / "analysis" / "CONNECTION_LEAK_VERIFICATION_REPORT.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "IFLOW.md").exists()
    assert (PROJECT_ROOT / "docs" / "overview" / "IFLOW.md").is_file()
    assert "- 📄 [IFLOW](IFLOW.md)" not in docs_index
    assert "overview/IFLOW.md" in docs_index
    assert "IFLOW" in overview_index
    assert "overview/IFLOW.md" in cleanup_index_root
    assert "docs/overview/IFLOW.md" in readme_root
    assert "docs/overview/IFLOW.md" in guides_readme
    assert "../../overview/IFLOW.md" in doc_management
    assert "../../overview/IFLOW.md" in leak_report


def test_active_documentation_entry_guides_no_longer_point_to_removed_quickstart_and_start_here_files() -> None:
    guides_readme = (PROJECT_ROOT / "docs" / "guides" / "README.md").read_text(encoding="utf-8")
    doc_management = (
        PROJECT_ROOT / "docs" / "guides" / "documentation" / "文档管理指南.md"
    ).read_text(encoding="utf-8")
    doc_structure = (
        PROJECT_ROOT / "docs" / "guides" / "documentation" / "文档结构说明.md"
    ).read_text(encoding="utf-8")
    documentation_summary = (
        PROJECT_ROOT / "docs" / "reports" / "DOCUMENTATION_ORGANIZATION_SUMMARY.md"
    ).read_text(encoding="utf-8")

    assert "/opt/claude/mystocks_spec/docs/README.md" in guides_readme
    assert "/opt/claude/mystocks_spec/docs/guides/documentation/" in guides_readme
    assert "/opt/claude/mystocks_spec/docs/guides/governance/" in guides_readme
    assert "docs/guides/QUICKSTART.md" not in guides_readme
    assert "quick-start.md" not in guides_readme
    assert "START_HERE.md" not in guides_readme

    assert "../../../README.md" in doc_management
    assert "../../INDEX.md" in doc_management
    assert "../../operations/quick-start.md" in doc_management
    assert "../../overview/IFLOW.md" in doc_management
    assert ".taskmaster/CLAUDE.md" in doc_management
    assert "../START_HERE.md" not in doc_management
    assert "../QUICKSTART.md" not in doc_management

    assert "docs/operations/quick-start.md" in doc_structure
    assert "docs/overview/IFLOW.md" in doc_structure
    assert "docs/guides/QUICKSTART.md" not in doc_structure

    assert "../operations/quick-start.md" in documentation_summary
    assert "./QUICKSTART.md" not in documentation_summary


def test_guides_readme_navigation_links_use_current_canonical_paths() -> None:
    guides_readme = (PROJECT_ROOT / "docs" / "guides" / "README.md").read_text(encoding="utf-8")

    assert "/opt/claude/mystocks_spec/docs/README.md" in guides_readme
    assert "/opt/claude/mystocks_spec/docs/guides/ai-tools/" in guides_readme
    assert "/opt/claude/mystocks_spec/docs/guides/frontend/" in guides_readme
    assert "/opt/claude/mystocks_spec/docs/guides/web/" in guides_readme
    assert "/opt/claude/mystocks_spec/docs/guides/typescript/" in guides_readme
    assert "/opt/claude/mystocks_spec/docs/guides/pm2/" in guides_readme
    assert "/opt/claude/mystocks_spec/docs/guides/openspec-cmd/" in guides_readme
    assert "/opt/claude/mystocks_spec/docs/guides/multi-cli-tasks/" in guides_readme
    assert "/opt/claude/mystocks_spec/docs/guides/onboarding/" in guides_readme

    assert "../standards/PROJECT_MODULES.md" not in guides_readme
    assert "../architecture/README.md" not in guides_readme
    assert "../api/README.md" not in guides_readme
    assert "../reports/INDEX.md" not in guides_readme
    assert "./data-source/DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md" not in guides_readme
    assert "./data-source/DATA_SOURCE_TOOLS_QUICK_REFERENCE.md" not in guides_readme
    assert "../architecture/DATA_SOURCE_MANAGEMENT_V2.md" not in guides_readme
    assert "../reports/DATA_SOURCE_V2_FINAL_VERIFICATION_REPORT.md" not in guides_readme
    assert "../reports/DATA_SOURCE_V2_ENHANCEMENT_PROPOSAL.md" not in guides_readme
    assert "../reports/REORGANIZATION_COMPLETION_REPORT.md" not in guides_readme
    assert "./PROJECT_MODULES.md" not in guides_readme
    assert "./docs/architecture/README.md" not in guides_readme
    assert "./docs/guides/" not in guides_readme
    assert "./docs/api/" not in guides_readme
    assert "./docs/reports/" not in guides_readme
    assert "./docs/guides/data-source/DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md" not in guides_readme
    assert "./docs/guides/data-source/DATA_SOURCE_TOOLS_QUICK_REFERENCE.md" not in guides_readme
    assert "./docs/architecture/DATA_SOURCE_MANAGEMENT_V2.md" not in guides_readme
    assert "./docs/reports/DATA_SOURCE_V2_FINAL_VERIFICATION_REPORT.md" not in guides_readme
    assert "./docs/reports/DATA_SOURCE_V2_ENHANCEMENT_PROPOSAL.md" not in guides_readme
    assert "./REORGANIZATION_COMPLETION_REPORT.md" not in guides_readme


def test_active_architecture_and_standards_docs_point_to_current_canonical_guides() -> None:
    page_config_model = (PROJECT_ROOT / "docs" / "architecture" / "PAGE_CONFIG_MODEL.md").read_text(
        encoding="utf-8"
    )
    standards_readme = (PROJECT_ROOT / "docs" / "standards" / "README.md").read_text(encoding="utf-8")
    ui_design_system = (PROJECT_ROOT / "docs" / "standards" / "UI_DESIGN_SYSTEM.md").read_text(encoding="utf-8")
    design_overview = (PROJECT_ROOT / "docs" / "standards" / "00-DESIGN_OVERVIEW.md").read_text(
        encoding="utf-8"
    )

    assert "./ROUTER_SIMPLIFICATION_EXPLANATION.md" in page_config_model
    assert "../guides/ROUTER_SIMPLIFICATION_EXPLANATION.md" not in page_config_model

    assert "../guides/onboarding/DEVELOPER_GUIDE.md" in standards_readme
    assert "../../web/frontend/docs/DEVELOPER_GUIDE.md" not in standards_readme

    assert "../guides/onboarding/DEVELOPER_GUIDE.md" in ui_design_system
    assert "../../web/frontend/docs/DEVELOPER_GUIDE.md" not in ui_design_system

    assert "../guides/onboarding/DEVELOPER_GUIDE.md" in design_overview
    assert "../../web/frontend/docs/DEVELOPER_GUIDE.md" not in design_overview


def test_typescript_architecture_docs_point_to_current_typescript_and_report_families() -> None:
    typescript_doc = (PROJECT_ROOT / "docs" / "architecture" / "typescript_documentation.md").read_text(
        encoding="utf-8"
    )
    typescript_quality_readme = (
        PROJECT_ROOT / "docs" / "architecture" / "README_TypeScript_Quality_System.md"
    ).read_text(encoding="utf-8")

    assert "../guides/typescript/Typescript_QUICKSTART.md" in typescript_doc
    assert "../guides/typescript/Typescript_USER_GUIDE.md" in typescript_doc
    assert "../guides/typescript/Typescript_CONFIG_REFERENCE.md" in typescript_doc
    assert "../guides/typescript/Typescript_BEST_PRACTICES.md" in typescript_doc
    assert "../guides/typescript/Typescript_TRAINING_BEGINNER.md" in typescript_doc
    assert "../guides/typescript/Typescript_TRAINING_ADVANCED.md" in typescript_doc
    assert "../guides/typescript/Typescript_TROUBLESHOOTING.md" in typescript_doc
    assert "../guides/typescript/Typescript_API_REFERENCE.md" in typescript_doc
    assert "./QUICKSTART.md" not in typescript_doc
    assert "./USER_GUIDE.md" not in typescript_doc
    assert "./CONFIG_REFERENCE.md" not in typescript_doc
    assert "./BEST_PRACTICES.md" not in typescript_doc
    assert "./TRAINING_BEGINNER.md" not in typescript_doc
    assert "./TRAINING_ADVANCED.md" not in typescript_doc
    assert "./TROUBLESHOOTING.md" not in typescript_doc
    assert "./API_REFERENCE.md" not in typescript_doc

    assert "../reports/TYPESCRIPT_FIX_BEST_PRACTICES.md" in typescript_quality_readme
    assert "../reports/TYPESCRIPT_TECHNICAL_DEBT_MANAGEMENT.md" in typescript_quality_readme
    assert "../reports/TYPESCRIPT_TECHNICAL_DEBTS.md" in typescript_quality_readme
    assert "../reports/TYPESCRIPT_FIX_REFLECTION.md" in typescript_quality_readme
    assert "./../../../reports/TYPESCRIPT_FIX_BEST_PRACTICES.md" not in typescript_quality_readme
    assert "./../../../reports/TYPESCRIPT_TECHNICAL_DEBT_MANAGEMENT.md" not in typescript_quality_readme
    assert "./../../../reports/TYPESCRIPT_TECHNICAL_DEBTS.md" not in typescript_quality_readme
    assert "./../../../reports/TYPESCRIPT_FIX_REFLECTION.md" not in typescript_quality_readme


def test_active_log_path_defaults_are_converged_under_var_log() -> None:
    monitor_script = (PROJECT_ROOT / "scripts" / "dev" / "tools" / "monitor-database-server.sh").read_text(
        encoding="utf-8"
    )
    pm2_script = (PROJECT_ROOT / "scripts" / "dev" / "tools" / "pm2-integration.sh").read_text(encoding="utf-8")
    run_test_script = (PROJECT_ROOT / "scripts" / "run_test.sh").read_text(encoding="utf-8")
    lnav_guide = (PROJECT_ROOT / "docs" / "operations" / "LNAV_INTEGRATION_GUIDE.md").read_text(encoding="utf-8")
    rotation_config = (PROJECT_ROOT / "config" / "logging_rotation_config.yaml").read_text(encoding="utf-8")

    assert 'PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"' in monitor_script
    assert 'LOG_DIR="${PROJECT_ROOT}/var/log"' in monitor_script
    assert 'RECOVERY_FLAG_FILE="${LOG_DIR}/server_recovered.flag"' in monitor_script

    assert 'PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"' in pm2_script
    assert "./var/log/pm2-mystocks-backend-error.log" in pm2_script
    assert "./var/log/pm2-mystocks-frontend-error.log" in pm2_script
    assert 'LOG_FILE="${PROJECT_ROOT}/var/log/pm2-deploy-' in pm2_script
    assert "日志: var/log/pm2-*.log" in pm2_script

    assert 'mkdir -p "${PROJECT_ROOT}/var/log"' in run_test_script
    assert 'lnav var/log/*.log ${LOG_DIR}/playwright-*.log ${LOG_DIR}/e2e-*.log' in run_test_script
    assert '服务日志: ${PROJECT_ROOT}/var/log/' in run_test_script

    assert "var/log/" in lnav_guide
    assert "./scripts/tests/run-api-tests.sh all" in lnav_guide
    assert "var/log/tests/" in lnav_guide
    assert "tail -f var/log/api/*.log" in lnav_guide

    assert "log_directory: /opt/claude/mystocks_spec/var/log/app" in rotation_config
    assert "final_archive_directory: /opt/claude/mystocks_spec/archive/logs/app" in rotation_config


def test_active_guides_no_longer_point_runtime_logs_to_repo_root_logs_directory() -> None:
    e2e_quick_ref = (PROJECT_ROOT / "docs" / "testing" / "WEB_E2E_TEST_QUICK_REFERENCE.md").read_text(
        encoding="utf-8"
    )
    monitoring_guide = (
        PROJECT_ROOT / "docs" / "guides" / "data-source" / "DATA_SOURCE_MONITORING_GUIDE.md"
    ).read_text(encoding="utf-8")
    quick_start = (PROJECT_ROOT / "docs" / "operations" / "quick-start.md").read_text(encoding="utf-8")
    production_info = (PROJECT_ROOT / "docs" / "operations" / "PRODUCTION_INFO.md").read_text(encoding="utf-8")
    operation_plan = (
        PROJECT_ROOT / "docs" / "guides" / "web" / "WEB_CLIENT_OPERATION_PLAN.md"
    ).read_text(encoding="utf-8")
    data_cleaning = (PROJECT_ROOT / "docs" / "guides" / "data-source" / "DATA_CLEANING_QUICK_START.md").read_text(
        encoding="utf-8"
    )
    testing_faq = (PROJECT_ROOT / "docs" / "testing" / "常见测试问题与解决方案.md").read_text(encoding="utf-8")
    backup_guide = (PROJECT_ROOT / "docs" / "operations" / "BACKUP_GUIDE.md").read_text(encoding="utf-8")
    pm2_quick_start = (PROJECT_ROOT / "docs" / "guides" / "pm2" / "PM2_QUICK_START_GUIDE.md").read_text(
        encoding="utf-8"
    )
    deployment_guide = (
        PROJECT_ROOT / "docs" / "operations" / "deployment" / "DEPLOYMENT.md"
    ).read_text(encoding="utf-8")
    config_splitting = (PROJECT_ROOT / "docs" / "architecture" / "CONFIG_SPLITTING_GUIDE.md").read_text(
        encoding="utf-8"
    )
    openspec_cmd = (PROJECT_ROOT / "docs" / "guides" / "openspec-cmd" / "README.md").read_text(encoding="utf-8")
    amp_config = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "AMP配置.md").read_text(encoding="utf-8")
    project_overview = (PROJECT_ROOT / "docs" / "overview" / "项目总览.md").read_text(encoding="utf-8")
    guides_readme = (PROJECT_ROOT / "docs" / "guides" / "README.md").read_text(encoding="utf-8")
    data_source_tools = (
        PROJECT_ROOT / "docs" / "guides" / "data-source" / "DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md"
    ).read_text(encoding="utf-8")
    pm2_playwright = (PROJECT_ROOT / "docs" / "guides" / "pm2" / "PM2_PLAYWRIGHT_TESTING_GUIDE.md").read_text(
        encoding="utf-8"
    )
    project_dir_plan = (
        PROJECT_ROOT
        / "docs"
        / "reports"
        / "cleanup"
        / "directory-organization"
        / "legacy"
        / "PROJECT_DIRECTORY_MANAGEMENT_PLAN.md"
    ).read_text(encoding="utf-8")
    deliverable = (
        PROJECT_ROOT
        / "docs"
        / "reports"
        / "cleanup"
        / "directory-organization"
        / "legacy"
        / "deliverable.md"
    ).read_text(encoding="utf-8")
    pm2_tmux_lnav = (PROJECT_ROOT / "docs" / "guides" / "pm2" / "PM2_TMUX_LNV_COLLABORATION_GUIDE.md").read_text(
        encoding="utf-8"
    )
    recovery_procedure = (
        PROJECT_ROOT / "docs" / "operations" / "PHASE6_SERVER_RECOVERY_TEST_PROCEDURE.md"
    ).read_text(encoding="utf-8")
    frontend_backend_plan = (
        PROJECT_ROOT / "docs" / "api" / "guides" / "integration" / "前后端整合与部署完整方案.md"
    ).read_text(encoding="utf-8")
    tmux_lnav_adapter = (
        PROJECT_ROOT / "docs" / "operations" / "monitoring" / "TMUX_LNAV_ADAPTER_MONITORING.md"
    ).read_text(encoding="utf-8")
    directory_methodology = (
        PROJECT_ROOT / "docs" / "guides" / "documentation" / "文件目录整理方法论指南.md"
    ).read_text(encoding="utf-8")
    iflow_root = (PROJECT_ROOT / "IFLOW.md").read_text(encoding="utf-8")
    iflow_docs = (PROJECT_ROOT / "docs" / "overview" / "IFLOW.md").read_text(encoding="utf-8")
    websocket_basic = (PROJECT_ROOT / "scripts" / "tests" / "simple_websocket_test.py").read_text(encoding="utf-8")
    websocket_stress = (PROJECT_ROOT / "scripts" / "tests" / "websocket_stress_test.py").read_text(
        encoding="utf-8"
    )
    websocket_report = (
        PROJECT_ROOT / "docs" / "reports" / "performance" / "websocket_optimization_report.md"
    ).read_text(encoding="utf-8")
    run_platform = (PROJECT_ROOT / "scripts" / "runtime" / "run_platform.sh").read_text(encoding="utf-8")
    check_system_status = (PROJECT_ROOT / "scripts" / "dev" / "检查系统状态.py").read_text(encoding="utf-8")
    stocks_spec = (PROJECT_ROOT / "scripts" / "stocks_spec.sh").read_text(encoding="utf-8")
    ecosystem_config = (PROJECT_ROOT / "config" / "ecosystem.config.js").read_text(encoding="utf-8")
    web_ecosystem_dev = (PROJECT_ROOT / "web" / "ecosystem.dev.config.js").read_text(encoding="utf-8")
    frontend_ecosystem = (PROJECT_ROOT / "web" / "frontend" / "ecosystem.config.js").read_text(encoding="utf-8")
    frontend_ecosystem_prod = (
        PROJECT_ROOT / "web" / "frontend" / "ecosystem.prod.config.js"
    ).read_text(encoding="utf-8")
    start_system = (PROJECT_ROOT / "scripts" / "start-system.sh").read_text(encoding="utf-8")
    start_metrics = (PROJECT_ROOT / "scripts" / "runtime" / "start_metrics_server.py").read_text(encoding="utf-8")
    tmux_test_conf = (PROJECT_ROOT / "scripts" / "dev" / "tmux" / "mystocks-test.conf").read_text(encoding="utf-8")
    stocks_spec_guide = (PROJECT_ROOT / "docs" / "operations" / "STOCKS_SPEC_COMMAND_GUIDE.md").read_text(
        encoding="utf-8"
    )
    frontend_pm2_test = (PROJECT_ROOT / "web" / "frontend" / "tests" / "pm2-deployment.test.ts").read_text(
        encoding="utf-8"
    )
    frontend_testing_guide = (PROJECT_ROOT / "web" / "frontend" / "测试指南.md").read_text(encoding="utf-8")
    frontend_failure_plan = (PROJECT_ROOT / "web" / "frontend" / "失败预案.md").read_text(encoding="utf-8")
    web_readme = (PROJECT_ROOT / "web" / "README.md").read_text(encoding="utf-8")
    vue_debug = (PROJECT_ROOT / "web" / "frontend" / "VUE_DEBUGGING_GUIDE.md").read_text(encoding="utf-8")
    readme_debug = (PROJECT_ROOT / "web" / "frontend" / "README_DEBUGGING.md").read_text(encoding="utf-8")
    wencai_test = (PROJECT_ROOT / "web" / "frontend" / "WENCAI_TEST_GUIDE.md").read_text(encoding="utf-8")
    wencai_v2_summary = (PROJECT_ROOT / "web" / "frontend" / "WENCAI_V2_SUMMARY.md").read_text(encoding="utf-8")
    wencai_v2_test = (PROJECT_ROOT / "web" / "frontend" / "WENCAI_V2_TEST_GUIDE.md").read_text(encoding="utf-8")
    frontend_quick_ref = (PROJECT_ROOT / "web" / "frontend" / "QUICK_REFERENCE.md").read_text(encoding="utf-8")
    frontend_quick_debug = (PROJECT_ROOT / "web" / "frontend" / "quick-debug.sh").read_text(encoding="utf-8")
    web_task_management = (PROJECT_ROOT / "web" / "TASK_MANAGEMENT.md").read_text(encoding="utf-8")
    web_wencai_integration = (PROJECT_ROOT / "web" / "WENCAI_FRONTEND_INTEGRATION.md").read_text(
        encoding="utf-8"
    )
    web_access_guide = (PROJECT_ROOT / "docs" / "api" / "Web访问指南.md").read_text(encoding="utf-8")
    improvement_executor = (PROJECT_ROOT / "docs" / "api" / "IMPROVEMENT_PLAN_EXECUTOR.md").read_text(
        encoding="utf-8"
    )
    swagger_guide = (PROJECT_ROOT / "docs" / "api" / "SWAGGER_UI_GUIDE.md").read_text(encoding="utf-8")
    mock_data_arch = (PROJECT_ROOT / "docs" / "architecture" / "Mock数据系统指南.md").read_text(
        encoding="utf-8"
    )
    backend_impl_guide = (PROJECT_ROOT / "web" / "backend" / "IMPLEMENTATION_GUIDE.md").read_text(
        encoding="utf-8"
    )
    ecosystem_enhanced = (PROJECT_ROOT / "config" / "pm2" / "ecosystem.enhanced.config.js").read_text(
        encoding="utf-8"
    )
    ecosystem_production = (PROJECT_ROOT / "config" / "ecosystem.production.config.js").read_text(
        encoding="utf-8"
    )
    ecosystem_pm2_production = (PROJECT_ROOT / "config" / "pm2" / "ecosystem.production.config.js").read_text(
        encoding="utf-8"
    )
    backend_pm2_js = (PROJECT_ROOT / "web" / "backend" / "web" / "backend" / "pm2.config.js").read_text(
        encoding="utf-8"
    )
    backend_pm2_json_nested = (
        PROJECT_ROOT / "web" / "backend" / "web" / "backend" / "pm2.config.json"
    ).read_text(encoding="utf-8")
    backend_pm2_json = (PROJECT_ROOT / "web" / "backend" / "pm2.config.json").read_text(encoding="utf-8")
    sync_stock_basic = (
        PROJECT_ROOT / "scripts" / "maintenance" / "data_sync" / "sync_stock_basic.py"
    ).read_text(encoding="utf-8")
    sync_stock_kline = (
        PROJECT_ROOT / "scripts" / "maintenance" / "data_sync" / "sync_stock_kline.py"
    ).read_text(encoding="utf-8")
    sync_minute_kline = (
        PROJECT_ROOT / "scripts" / "maintenance" / "data_sync" / "sync_minute_kline.py"
    ).read_text(encoding="utf-8")
    sync_industry = (
        PROJECT_ROOT / "scripts" / "maintenance" / "data_sync" / "sync_industry_classify.py"
    ).read_text(encoding="utf-8")
    sync_concept = (
        PROJECT_ROOT / "scripts" / "maintenance" / "data_sync" / "sync_concept_classify.py"
    ).read_text(encoding="utf-8")
    sync_stock_industry_concept = (
        PROJECT_ROOT / "scripts" / "maintenance" / "data_sync" / "sync_stock_industry_concept.py"
    ).read_text(encoding="utf-8")
    data_sync_ops = (PROJECT_ROOT / "docs" / "operations" / "数据同步故障排除.md").read_text(encoding="utf-8")
    health_check = (PROJECT_ROOT / "scripts" / "dev" / "automation" / "health_check.sh").read_text(encoding="utf-8")
    health_check_simple = (
        PROJECT_ROOT / "scripts" / "dev" / "automation" / "health_check_simple.sh"
    ).read_text(encoding="utf-8")
    health_check_v2 = (PROJECT_ROOT / "scripts" / "dev" / "automation" / "health_check_v2.sh").read_text(
        encoding="utf-8"
    )
    automation_monitor = (PROJECT_ROOT / "scripts" / "dev" / "automation" / "monitor.sh").read_text(
        encoding="utf-8"
    )
    automation_deploy = (PROJECT_ROOT / "scripts" / "dev" / "automation" / "deploy.sh").read_text(
        encoding="utf-8"
    )
    backend_health_api = (PROJECT_ROOT / "web" / "backend" / "app" / "api" / "health.py").read_text(
        encoding="utf-8"
    )

    assert "../var/log/backend-access.log" in e2e_quick_ref
    assert "var/log/metrics_server.log" in monitoring_guide
    assert "var/log/data_sync/stock_basic_sync.log" in quick_start
    assert "/opt/claude/mystocks_spec/var/log/backend.log" in production_info
    assert "pm2 logs --nostream > var/log/pm2-" in operation_plan
    assert "var/log/auto_clean.log" in data_cleaning
    assert "tail -f var/log/tests/test.log" in testing_faq
    assert "var/log/" in backup_guide
    assert "lnav var/log/backend-error.log" in pm2_quick_start
    assert "--access-logfile var/log/access.log" in deployment_guide
    assert "${LOG_PATH:var/log/app.log}" in config_splitting
    assert "tail -f var/log/openspec.log" in openspec_cmd
    assert "tail -f var/log/requests.log" in amp_config
    assert "tail -f var/log/data_sync/stock_basic_sync.log" in project_overview
    assert "├── var/log/" in guides_readme
    assert "/path/to/backend/var/log/backend-access.log" in data_source_tools
    assert "./var/log/pm2-error.log" in pm2_playwright
    assert "../var/log/backend-access.log" in pm2_playwright
    assert "📂 var/log/" in project_dir_plan
    assert "mkdir -p temp/cache var/log/app" in project_dir_plan
    assert "var/log/" in deliverable
    assert "var/log/backend-access.log" in pm2_tmux_lnav
    assert "tail -f var/log/backend*.log" in recovery_procedure
    assert "nohup python3 -m app.main > var/log/app.log 2>&1 &" in frontend_backend_plan
    assert "cd /opt/claude/mystocks_spec/var/log" in tmux_lnav_adapter
    assert "lnav backend-access.log" in tmux_lnav_adapter
    assert "/opt/claude/mystocks_spec/var/log/adapter.log" in tmux_lnav_adapter
    assert "生成物（var/log/reports/cache）" in directory_methodology
    assert "reports/ 或 var/log/" in directory_methodology
    assert "`var/log/`（应 .gitignore）" in directory_methodology
    assert "├── 📝 var/log/" in iflow_root
    assert "**Web 日志**: `var/log/`" in iflow_root
    assert "├── 📝 var/log/" in iflow_docs
    assert "**适配器日志**: `var/log/adapter.log`" in iflow_docs
    assert "/opt/claude/mystocks_spec/var/log/tests" in websocket_basic
    assert "/opt/claude/mystocks_spec/var/log/tests" in websocket_stress
    assert "/opt/claude/mystocks_spec/var/log/tests/websocket_stress_test_report_" in websocket_report
    assert 'LOG_DIR="${PROJECT_ROOT}/var/log"' in run_platform
    assert 'BACKEND_LOG="${LOG_DIR}/backend.log"' in run_platform
    assert 'FRONTEND_LOG="${LOG_DIR}/frontend.log"' in run_platform
    assert 'nohup python -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > "${BACKEND_LOG}" 2>&1 &' in run_platform
    assert '"/opt/claude/mystocks_spec/var/log"' in check_system_status
    assert '"/opt/claude/mystocks_spec/var/log/tests"' in check_system_status
    assert 'LOG_DIR="$PROJECT_ROOT/var/log"' in stocks_spec
    assert 'BACKEND_LOG="$LOG_DIR/backend.log"' in stocks_spec
    assert 'FRONTEND_LOG="$LOG_DIR/frontend.log"' in stocks_spec
    assert "path.join('/opt/claude/mystocks_spec/var/log', 'backend.log')" in ecosystem_config
    assert 'const runtimeLogDir = "/opt/claude/mystocks_spec/var/log"' in web_ecosystem_dev
    assert 'path.join(runtimeLogDir, "backend-error.log")' in web_ecosystem_dev
    assert 'path.join(runtimeLogDir, "frontend-dev-error.log")' in web_ecosystem_dev
    assert 'const runtimeLogDir = "/opt/claude/mystocks_spec/var/log"' in frontend_ecosystem
    assert 'path.join(runtimeLogDir, "frontend-error.log")' in frontend_ecosystem
    assert "const runtimeLogDir = '/opt/claude/mystocks_spec/var/log';" in frontend_ecosystem_prod
    assert "path.join(runtimeLogDir, 'pm2-error.log')" in frontend_ecosystem_prod
    assert 'LOG_DIR="$PROJECT_ROOT/var/log"' in start_system
    assert 'mkdir -p var/log' in start_system
    assert 'LOG_DIR = project_root / "var" / "log"' in start_metrics
    assert "nohup python scripts/runtime/start_metrics_server.py > var/log/metrics_server.log 2>&1 &" in start_metrics
    assert "const RUNTIME_LOG_DIR = join(PROJECT_ROOT, 'var', 'log');" in frontend_pm2_test
    assert "join(RUNTIME_LOG_DIR, 'pm2-error.log')" in frontend_pm2_test
    assert 'echo "- 后端日志: var/log/backend*.log"' in tmux_test_conf
    assert 'echo "- 前端日志: var/log/frontend*.log, var/log/pm2-*.log"' in tmux_test_conf
    assert "/opt/claude/mystocks_spec/var/log/backend.log" in stocks_spec_guide
    assert "/opt/claude/mystocks_spec/var/log/frontend.log" in stocks_spec_guide
    assert "/opt/claude/mystocks_spec/var/log/pm2-error.log" in frontend_testing_guide
    assert "/opt/claude/mystocks_spec/var/log/pm2-error.log" in frontend_failure_plan
    assert "/opt/claude/mystocks_spec/var/log/backend.log" in web_readme
    assert "/opt/claude/mystocks_spec/var/log/frontend.log" in web_readme
    assert "/opt/claude/mystocks_spec/var/log/frontend.log" in vue_debug
    assert "/opt/claude/mystocks_spec/var/log/frontend.log" in readme_debug
    assert "/opt/claude/mystocks_spec/var/log/backend.log" in readme_debug
    assert "/opt/claude/mystocks_spec/var/log/frontend.log" in wencai_test
    assert "/opt/claude/mystocks_spec/var/log/backend.log" in wencai_test
    assert "/opt/claude/mystocks_spec/var/log/backend.log" in wencai_v2_summary
    assert "/opt/claude/mystocks_spec/var/log/backend.log" in wencai_v2_test
    assert "/opt/claude/mystocks_spec/var/log/frontend.log" in frontend_quick_ref
    assert "/opt/claude/mystocks_spec/var/log/backend.log" in frontend_quick_ref
    assert "/opt/claude/mystocks_spec/var/log/frontend.log" in frontend_quick_debug
    assert "/opt/claude/mystocks_spec/var/log/backend.log" in web_task_management
    assert "/opt/claude/mystocks_spec/var/log/backend.log" in web_wencai_integration
    assert "/opt/claude/mystocks_spec/var/log/frontend.log" in web_access_guide
    assert "/opt/claude/mystocks_spec/var/log/backend.log" in web_access_guide
    assert "`var/log/backend.log`" in improvement_executor
    assert "/opt/claude/mystocks_spec/var/log/backend*.log" in swagger_guide
    assert "tail -f var/log/backend-access.log" in mock_data_arch
    assert "/opt/claude/mystocks_spec/var/log/" in backend_impl_guide
    assert "/opt/claude/mystocks_spec/var/log/backend-access.log" in backend_impl_guide
    assert "/opt/claude/mystocks_spec/var/log/backend-error.log" in backend_impl_guide
    assert "const runtimeLogDir = '/opt/claude/mystocks_spec/var/log';" in ecosystem_enhanced
    assert "const dataSyncLogDir = path.join(runtimeLogDir, 'data_sync');" in ecosystem_enhanced
    assert "path.join(runtimeLogDir, 'pm2-mystocks-backend.log')" in ecosystem_enhanced
    assert "path.join(dataSyncLogDir, 'stock_basic_sync.log')" in ecosystem_enhanced
    assert "const runtimeLogDir = '/var/log/mystocks';" in ecosystem_production
    assert "path.join(runtimeLogDir, 'backend.log')" in ecosystem_production
    assert "const runtimeLogDir = '/var/log/mystocks';" in ecosystem_pm2_production
    assert "path.join(runtimeLogDir, 'backend.log')" in ecosystem_pm2_production
    assert '"/opt/claude/mystocks_spec/var/log/backend-pm2.log"' in backend_pm2_js
    assert '"/opt/claude/mystocks_spec/var/log/backend-pm2.log"' in backend_pm2_json_nested
    assert '"/opt/claude/mystocks_spec/var/log/backend-pm2.log"' in backend_pm2_json
    assert 'LOG_DIR = Path(__file__).resolve().parents[3] / "var" / "log" / "data_sync"' in sync_stock_basic
    assert 'logging.FileHandler(LOG_DIR / "stock_basic_sync.log")' in sync_stock_basic
    assert 'logging.FileHandler(LOG_DIR / "stock_kline_sync.log")' in sync_stock_kline
    assert 'logging.FileHandler(LOG_DIR / "minute_kline_sync.log")' in sync_minute_kline
    assert 'logging.FileHandler(LOG_DIR / "industry_classify_sync.log")' in sync_industry
    assert 'logging.FileHandler(LOG_DIR / "concept_classify_sync.log")' in sync_concept
    assert 'logging.FileHandler(LOG_DIR / "stock_industry_concept_sync.log")' in sync_stock_industry_concept
    assert "var/log/data_sync/minute_kline_sync.log" in data_sync_ops
    assert "var/log/data_sync/stock_industry_concept_sync.log" in data_sync_ops
    assert 'LOG_DIR="/var/log/mystocks"' in health_check
    assert 'LOG_DIR="/var/log/mystocks"' in health_check_simple
    assert 'LOG_DIR="/var/log/mystocks"' in health_check_v2
    assert 'LOG_DIR="/var/log/mystocks"' in automation_monitor
    assert 'LOG_DIR="/var/log/mystocks"' in automation_deploy
    assert '"/var/log/mystocks/health_reports"' in backend_health_api


def test_web_dev_tracking_runtime_artifacts_are_converged_under_var_log() -> None:
    tracker_hook = (PROJECT_ROOT / ".claude" / "hooks" / "post-tool-use-web-dev-file-tracker.sh").read_text(
        encoding="utf-8"
    )
    web_dev_hooks_guide = (PROJECT_ROOT / "docs" / "guides" / "hooks" / "web-dev-hooks-guide.md").read_text(
        encoding="utf-8"
    )
    web_dev_hooks_guide_cn = (PROJECT_ROOT / "docs" / "guides" / "hooks" / "WEB_DEV_HOOKS_GUIDE.md").read_text(
        encoding="utf-8"
    )
    directory_plan = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "directory-organization" / "DIRECTORY_ORGANIZATION_PLAN.md"
    ).read_text(encoding="utf-8")
    directory_review = (PROJECT_ROOT / "docs" / "reports" / "reviews" / "DIRECTORY_ORGANIZATION_REVIEW.md").read_text(
        encoding="utf-8"
    )

    assert 'WEB_DEV_LOG="${PROJECT_ROOT}/var/log/web-dev/tracing/web-edit-tracker.jsonl"' in tracker_hook
    assert "var/log/web-dev/tracing/web-edit-tracker.jsonl" in web_dev_hooks_guide
    assert "var/log/web-dev/tracing/web-edit-tracker.jsonl" in web_dev_hooks_guide_cn
    assert "var/log/web-dev/tracing/" in directory_plan
    assert "var/log/web-dev/tracing/web-edit-tracker.jsonl" in directory_review
    assert not (PROJECT_ROOT / "docs" / "web-dev").exists()


def test_hook_guides_are_converged_under_guides_hooks_family() -> None:
    final_execution_summary = (PROJECT_ROOT / "docs" / "reports" / "final_execution_summary.md").read_text(
        encoding="utf-8"
    )
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    hooks_index = (PROJECT_ROOT / "docs" / "guides" / "hooks" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    hook_docs = [
        "WEB_DEV_HOOKS_GUIDE.md",
        "web-dev-hooks-guide.md",
        "hook-analysis-report.md",
        "hook-optimization-summary.md",
        "hooks使用指南.md",
        "hooks详细说明.md",
        "hooks错误处理方法.md",
        "post_tool_use_hook_error_diagnosis.md",
        "pre_commit_hook_setup_guide.md",
    ]

    for name in hook_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "hooks" / name).is_file()
        assert f"hooks/{name}" in cleanup_index_root

    assert not (PROJECT_ROOT / "docs" / "web-dev").exists()
    assert "[`hooks/`]" in guides_index
    assert "docs/guides/hooks/pre_commit_hook_setup_guide.md" in final_execution_summary
    assert "WEB_DEV_HOOKS_GUIDE" in hooks_index
    assert "web-dev-hooks-guide" in hooks_index
    assert "pre_commit_hook_setup_guide" in hooks_index


def test_superpowers_docs_are_converged_under_guides_family() -> None:
    directory_plan = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "directory-organization" / "DIRECTORY_ORGANIZATION_PLAN.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "superpowers").exists()
    assert (PROJECT_ROOT / "docs" / "guides" / "superpowers" / "plans" / "2026-03-23-frontend-test-gates.md").is_file()
    assert "docs/guides/superpowers/" in directory_plan


def test_openspec_command_template_is_converged_under_guides_openspec_cmd_family() -> None:
    openspec_cmd_readme = (
        PROJECT_ROOT / "docs" / "guides" / "openspec-cmd" / "README.md"
    ).read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    openspec_cmd_index = (
        PROJECT_ROOT / "docs" / "guides" / "openspec-cmd" / "INDEX.md"
    ).read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "guides" / "command-template.md").exists()
    assert (PROJECT_ROOT / "docs" / "guides" / "openspec-cmd" / "command-template.md").is_file()

    assert "./command-template.md" in openspec_cmd_readme
    assert "openspec-cmd/command-template.md" in guides_index
    assert "command-template" in openspec_cmd_index
    assert "openspec-cmd/command-template.md" in cleanup_index_root


def test_active_workflow_docs_no_longer_point_to_removed_docs_top_level_families() -> None:
    guides_readme = (PROJECT_ROOT / "docs" / "guides" / "README.md").read_text(encoding="utf-8")
    uiux_readme = (PROJECT_ROOT / "docs" / "guides" / "ui-ux-pro-max" / "README.md").read_text(encoding="utf-8")
    uiux_report = (
        PROJECT_ROOT / "docs" / "guides" / "ui-ux-pro-max" / "PROJECT_COMPLETION_REPORT.md"
    ).read_text(encoding="utf-8")
    web_task = (PROJECT_ROOT / "scripts" / "cli" / "web" / "TASK.md").read_text(encoding="utf-8")
    web_rules = (PROJECT_ROOT / "scripts" / "cli" / "web" / "RULES.md").read_text(encoding="utf-8")
    openspec_plan = (
        PROJECT_ROOT / "openspec" / "changes" / "frontend-optimization-six-phase" / "implementation-plan.md"
    ).read_text(encoding="utf-8")
    tests_plan = (
        PROJECT_ROOT / "tests" / "changes" / "frontend-optimization-six-phase" / "implementation-plan.md"
    ).read_text(encoding="utf-8")

    assert "`docs/guides/features/`" in guides_readme
    assert "`docs/features/`" not in guides_readme

    assert "docs/guides/ui-ux-pro-max/" in uiux_readme
    assert "docs/ui-ux-pro-max/" not in uiux_readme
    assert "docs/guides/ui-ux-pro-max/" in uiux_report
    assert "docs/ui-ux-pro-max/" not in uiux_report

    assert "docs/guides/frontend/INDEX.md" in web_task
    assert "docs/guides/web/ART_DECO_COMPONENTS_CATALOG.md" in web_task
    assert "docs/guides/web/FRONTEND_IMPROVEMENT_GUIDE.md" in web_task
    assert "docs/frontend/" not in web_task

    assert "docs/guides/frontend/INDEX.md" in web_rules
    assert "docs/guides/web/ART_DECO_COMPONENTS_CATALOG.md" in web_rules
    assert "docs/guides/web/FRONTEND_IMPROVEMENT_GUIDE.md" in web_rules
    assert "docs/guides/frontend/DASHBOARD_API_INTEGRATION_GUIDE.md" in web_rules
    assert "docs/frontend/" not in web_rules

    assert "docs/guides/web/WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md" in openspec_plan
    assert "docs/frontend/KLINE_COMPONENT_GUIDE.md" not in openspec_plan
    assert "docs/guides/web/WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md" in tests_plan
    assert "docs/frontend/KLINE_COMPONENT_GUIDE.md" not in tests_plan


def test_legacy_directory_organization_drafts_are_converged_under_reports_cleanup() -> None:
    docs_index = (PROJECT_ROOT / "docs" / "INDEX.md").read_text(encoding="utf-8")
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index = (PROJECT_ROOT / "docs" / "reports" / "cleanup" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_dir_index = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "directory-organization" / "INDEX.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "guides" / "DIRECTORY_ORGANIZATION_PLAN_OPTIMIZED.md").exists()
    assert not (PROJECT_ROOT / "docs" / "guides" / "DIRECTORY_ORGANIZATION_PLAN_REVIEW_SUGGESTIONS.md").exists()

    assert (
        PROJECT_ROOT
        / "docs"
        / "reports"
        / "cleanup"
        / "directory-organization"
        / "legacy"
        / "DIRECTORY_ORGANIZATION_PLAN_OPTIMIZED.md"
    ).is_file()
    assert (
        PROJECT_ROOT
        / "docs"
        / "reports"
        / "cleanup"
        / "directory-organization"
        / "legacy"
        / "DIRECTORY_ORGANIZATION_PLAN_REVIEW_SUGGESTIONS.md"
    ).is_file()

    assert "reports/cleanup/directory-organization/legacy/DIRECTORY_ORGANIZATION_PLAN_OPTIMIZED.md" in docs_index
    assert "cleanup/directory-organization/legacy/DIRECTORY_ORGANIZATION_PLAN_OPTIMIZED.md" in reports_index
    assert "directory-organization/legacy" in cleanup_index
    assert "legacy/INDEX.md" in cleanup_dir_index
    assert "DIRECTORY_ORGANIZATION_PLAN_OPTIMIZED" in cleanup_index
    assert "DIRECTORY_ORGANIZATION_PLAN_REVIEW_SUGGESTIONS" in cleanup_index


def test_directory_management_analysis_artifacts_are_converged_under_reports_cleanup_directory_organization() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index = (PROJECT_ROOT / "docs" / "reports" / "cleanup" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    directory_plan = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "directory-organization" / "legacy" / "PROJECT_DIRECTORY_MANAGEMENT_PLAN.md"
    ).read_text(encoding="utf-8")
    openspec_audit_summary = (PROJECT_ROOT / "docs" / "reports" / "openspec_audit_summary.md").read_text(
        encoding="utf-8"
    )

    docs = [
        "deliverable.md",
        "task_plan.md",
        "PROJECT_DIRECTORY_MANAGEMENT_PLAN.md",
    ]

    for name in docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (
            PROJECT_ROOT / "docs" / "reports" / "cleanup" / "directory-organization" / "legacy" / name
        ).is_file()
        assert name.removesuffix(".md") not in guides_index
        assert f"cleanup/directory-organization/legacy/{name}" in reports_index
        assert "directory-organization/legacy" in cleanup_index
        assert f"cleanup/directory-organization/legacy/{name}" in cleanup_index_root or (
            f"directory-organization/legacy/{name}" in cleanup_index_root
        )

    assert "docs/reports/cleanup/directory-organization/legacy/task_plan.md" in directory_plan
    assert "docs/guides/documentation/文件目录管理方案.md" in directory_plan
    assert "docs/reports/cleanup/directory-organization/legacy/task_plan.md" in openspec_audit_summary


def test_guides_index_root_is_converged_under_reports_cleanup() -> None:
    task_report = (PROJECT_ROOT / "TASK-REPORT.md").read_text(encoding="utf-8")
    root_doc_inventory = (
        PROJECT_ROOT / "reports" / "governance" / "2026-03-09-batch-3-root-doc-inventory.md"
    ).read_text(encoding="utf-8")
    cleanup_task = (PROJECT_ROOT / "docs" / "reports" / "cleanup" / "FILE_CLEANUP_TASK.md").read_text(
        encoding="utf-8"
    )

    assert not (PROJECT_ROOT / "docs" / "guides" / "INDEX_root.md").exists()
    assert (PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md").is_file()

    assert "docs/reports/cleanup/index-artifacts/INDEX_root.md" in task_report
    assert "docs/reports/cleanup/index-artifacts/INDEX_root.md" in root_doc_inventory
    assert "docs/reports/cleanup/index-artifacts/INDEX_root.md" in cleanup_task


def test_selected_completion_reports_are_converged_under_reports_completion_reports() -> None:
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    completion_index = (PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "guides" / "P1_TESTING_COMPLETION_REPORT.md").exists()
    assert not (PROJECT_ROOT / "docs" / "guides" / "PHASE1_UI_UX_FOUNDATION_COMPLETION_REPORT.md").exists()
    assert not (PROJECT_ROOT / "docs" / "guides" / "PHASE4_API_INTEGRATION_REPORT.md").exists()

    assert (PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "P1_TESTING_COMPLETION_REPORT.md").is_file()
    assert (
        PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "PHASE1_UI_UX_FOUNDATION_COMPLETION_REPORT.md"
    ).is_file()
    assert (PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "PHASE4_API_INTEGRATION_REPORT.md").is_file()

    assert "completion_reports/P1_TESTING_COMPLETION_REPORT.md" in reports_index
    assert "completion_reports/PHASE1_UI_UX_FOUNDATION_COMPLETION_REPORT.md" in reports_index
    assert "completion_reports/PHASE4_API_INTEGRATION_REPORT.md" in reports_index
    assert "P1_TESTING_COMPLETION_REPORT" in completion_index
    assert "PHASE1_UI_UX_FOUNDATION_COMPLETION_REPORT" in completion_index
    assert "PHASE4_API_INTEGRATION_REPORT" in completion_index
    assert "completion_reports/P1_TESTING_COMPLETION_REPORT.md" in cleanup_index_root
    assert "completion_reports/PHASE1_UI_UX_FOUNDATION_COMPLETION_REPORT.md" in cleanup_index_root
    assert "completion_reports/PHASE4_API_INTEGRATION_REPORT.md" in cleanup_index_root


def test_phase6_e2e_reports_are_converged_under_reports_completion_reports() -> None:
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    completion_index = (PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    cli_guidance = (PROJECT_ROOT / "docs" / "reports" / "cli_reports" / "CLI_2_WORK_GUIDANCE.md").read_text(
        encoding="utf-8"
    )
    cli_guidance_updated = (
        PROJECT_ROOT / "docs" / "reports" / "cli_reports" / "CLI_2_WORK_GUIDANCE_UPDATED.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "guides" / "PHASE6_E2E_STATUS_SUMMARY.md").exists()
    assert not (PROJECT_ROOT / "docs" / "guides" / "PHASE6_E2E_TEST_TASK_COMPLETION.md").exists()

    assert (PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "PHASE6_E2E_STATUS_SUMMARY.md").is_file()
    assert (PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "PHASE6_E2E_TEST_TASK_COMPLETION.md").is_file()

    assert "completion_reports/PHASE6_E2E_STATUS_SUMMARY.md" in reports_index
    assert "completion_reports/PHASE6_E2E_TEST_TASK_COMPLETION.md" in reports_index
    assert "PHASE6_E2E_STATUS_SUMMARY" in completion_index
    assert "PHASE6_E2E_TEST_TASK_COMPLETION" in completion_index
    assert "completion_reports/PHASE6_E2E_STATUS_SUMMARY.md" in cleanup_index_root
    assert "completion_reports/PHASE6_E2E_TEST_TASK_COMPLETION.md" in cleanup_index_root
    assert "docs/reports/completion_reports/PHASE6_E2E_STATUS_SUMMARY.md" in cli_guidance
    assert "docs/reports/completion_reports/PHASE6_E2E_STATUS_SUMMARY.md" in cli_guidance_updated


def test_low_reference_status_and_summary_reports_are_converged_under_reports_completion_reports() -> None:
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    completion_index = (PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "guides" / "MYSTOCKS_HTML_VUE_CONVERSION_SUMMARY.md").exists()
    assert not (PROJECT_ROOT / "docs" / "guides" / "REAL_STATUS_REPORT.md").exists()

    assert (
        PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "MYSTOCKS_HTML_VUE_CONVERSION_SUMMARY.md"
    ).is_file()
    assert (PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "REAL_STATUS_REPORT.md").is_file()

    assert "completion_reports/MYSTOCKS_HTML_VUE_CONVERSION_SUMMARY.md" in reports_index
    assert "completion_reports/REAL_STATUS_REPORT.md" in reports_index
    assert "MYSTOCKS_HTML_VUE_CONVERSION_SUMMARY" in completion_index
    assert "REAL_STATUS_REPORT" in completion_index
    assert "completion_reports/MYSTOCKS_HTML_VUE_CONVERSION_SUMMARY.md" in cleanup_index_root
    assert "completion_reports/REAL_STATUS_REPORT.md" in cleanup_index_root


def test_next_work_tasks_doc_is_converged_under_reports_tasks() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    tasks_index = (PROJECT_ROOT / "docs" / "reports" / "tasks" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    p0_report = (PROJECT_ROOT / "docs" / "reports" / "P0_TASK_COMPLETION_REPORT.md").read_text(encoding="utf-8")
    p1_report = (PROJECT_ROOT / "docs" / "reports" / "P1_DIAGNOSTIC_REPORT.md").read_text(encoding="utf-8")

    name = "NEXT_WORK_TASKS.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "reports" / "tasks" / name).is_file()
    assert name.removesuffix(".md") not in guides_index
    assert f"tasks/{name}" in reports_index
    assert name.removesuffix(".md") in tasks_index
    assert f"reports/tasks/{name}" in cleanup_index_root or f"tasks/{name}" in cleanup_index_root
    assert "docs/reports/tasks/NEXT_WORK_TASKS.md" in p0_report
    assert "docs/reports/tasks/NEXT_WORK_TASKS.md" in p1_report


def test_handover_task_doc_is_converged_under_reports_tasks() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    tasks_index = (PROJECT_ROOT / "docs" / "reports" / "tasks" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    cleanup_guide = (PROJECT_ROOT / "docs" / "reports" / "DOC_CLEANUP_EXECUTION_GUIDE.md").read_text(
        encoding="utf-8"
    )
    optimized_plan = (
        PROJECT_ROOT
        / "docs"
        / "reports"
        / "cleanup"
        / "directory-organization"
        / "legacy"
        / "DIRECTORY_ORGANIZATION_PLAN_OPTIMIZED.md"
    ).read_text(encoding="utf-8")
    organization_review = (
        PROJECT_ROOT / "docs" / "reports" / "DOCUMENT_ORGANIZATION_PLAN_REVIEW.md"
    ).read_text(encoding="utf-8")

    name = "HANDOVER_TASK.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "reports" / "tasks" / name).is_file()
    assert name.removesuffix(".md") not in guides_index
    assert f"tasks/{name}" in reports_index
    assert name.removesuffix(".md") in tasks_index
    assert f"reports/tasks/{name}" in cleanup_index_root or f"tasks/{name}" in cleanup_index_root
    assert "reports/tasks/HANDOVER_TASK.md" in cleanup_guide
    assert "docs/reports/tasks/HANDOVER_TASK.md" in optimized_plan
    assert "docs/reports/tasks/HANDOVER_TASK.md" in organization_review


def test_test_cli_task_doc_is_converged_under_reports_tasks_legacy() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    tasks_index = (PROJECT_ROOT / "docs" / "reports" / "tasks" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    task_doc = (
        PROJECT_ROOT / "docs" / "reports" / "tasks" / "legacy" / "TEST_CLI_TASK.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "guides" / "TASK.md").exists()
    assert (PROJECT_ROOT / "docs" / "reports" / "tasks" / "legacy" / "TEST_CLI_TASK.md").is_file()
    assert "- [TASK](TASK.md)" not in guides_index
    assert "legacy/TEST_CLI_TASK.md" in tasks_index
    assert "tasks/legacy/TEST_CLI_TASK.md" in reports_index or "reports/tasks/legacy/TEST_CLI_TASK.md" in reports_index
    assert "reports/tasks/legacy/TEST_CLI_TASK.md" in cleanup_index_root or "tasks/legacy/TEST_CLI_TASK.md" in cleanup_index_root
    assert "Test CLI 任务文档" in task_doc
    assert "phase7-test-contracts-automation" in task_doc


def test_low_reference_tdd_and_debt_reports_are_converged_under_reports_completion_reports() -> None:
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    completion_index = (PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "guides" / "DATABASE_SERVICE_TDD_REFACTORING_REPORT.md").exists()
    assert not (PROJECT_ROOT / "docs" / "guides" / "TDD_REFACTORING_COMPLETION_REPORT.md").exists()
    assert not (PROJECT_ROOT / "docs" / "guides" / "TECHNICAL_DEBT_PHASE_3_COMPLETION_REPORT.md").exists()

    assert (
        PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "DATABASE_SERVICE_TDD_REFACTORING_REPORT.md"
    ).is_file()
    assert (PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "TDD_REFACTORING_COMPLETION_REPORT.md").is_file()
    assert (
        PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "TECHNICAL_DEBT_PHASE_3_COMPLETION_REPORT.md"
    ).is_file()

    assert "completion_reports/DATABASE_SERVICE_TDD_REFACTORING_REPORT.md" in reports_index
    assert "completion_reports/TDD_REFACTORING_COMPLETION_REPORT.md" in reports_index
    assert "completion_reports/TECHNICAL_DEBT_PHASE_3_COMPLETION_REPORT.md" in reports_index
    assert "DATABASE_SERVICE_TDD_REFACTORING_REPORT" in completion_index
    assert "TDD_REFACTORING_COMPLETION_REPORT" in completion_index
    assert "TECHNICAL_DEBT_PHASE_3_COMPLETION_REPORT" in completion_index
    assert "completion_reports/DATABASE_SERVICE_TDD_REFACTORING_REPORT.md" in cleanup_index_root
    assert "completion_reports/TDD_REFACTORING_COMPLETION_REPORT.md" in cleanup_index_root
    assert "completion_reports/TECHNICAL_DEBT_PHASE_3_COMPLETION_REPORT.md" in cleanup_index_root


def test_quality_implementation_and_typescript_fix_reports_are_converged_under_reports_code_quality() -> None:
    guides_claude = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "CLAUDE.md").read_text(encoding="utf-8")
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    code_quality_index = (PROJECT_ROOT / "docs" / "reports" / "code_quality" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "guides" / "PYTHON_QUALITY_TOOLS_IMPLEMENTATION_SUMMARY.md").exists()
    assert not (PROJECT_ROOT / "docs" / "guides" / "TYPESCRIPT_ERROR_FIX_REPORT.md").exists()
    assert not (PROJECT_ROOT / "docs" / "guides" / "TYPESCRIPT_FIX_FINAL_REPORT.md").exists()
    assert not (PROJECT_ROOT / "docs" / "guides" / "TYPESCRIPT_QUALITY_GATE_FIX_REPORT.md").exists()

    assert (
        PROJECT_ROOT / "docs" / "reports" / "code_quality" / "PYTHON_QUALITY_TOOLS_IMPLEMENTATION_SUMMARY.md"
    ).is_file()
    assert (PROJECT_ROOT / "docs" / "reports" / "code_quality" / "TYPESCRIPT_ERROR_FIX_REPORT.md").is_file()
    assert (PROJECT_ROOT / "docs" / "reports" / "code_quality" / "TYPESCRIPT_FIX_FINAL_REPORT.md").is_file()
    assert (PROJECT_ROOT / "docs" / "reports" / "code_quality" / "TYPESCRIPT_QUALITY_GATE_FIX_REPORT.md").is_file()

    assert "code_quality/PYTHON_QUALITY_TOOLS_IMPLEMENTATION_SUMMARY.md" in reports_index
    assert "code_quality/TYPESCRIPT_ERROR_FIX_REPORT.md" in reports_index
    assert "code_quality/TYPESCRIPT_FIX_FINAL_REPORT.md" in reports_index
    assert "code_quality/TYPESCRIPT_QUALITY_GATE_FIX_REPORT.md" in reports_index
    assert "PYTHON_QUALITY_TOOLS_IMPLEMENTATION_SUMMARY" in code_quality_index
    assert "TYPESCRIPT_ERROR_FIX_REPORT" in code_quality_index
    assert "TYPESCRIPT_FIX_FINAL_REPORT" in code_quality_index
    assert "TYPESCRIPT_QUALITY_GATE_FIX_REPORT" in code_quality_index
    assert "code_quality/PYTHON_QUALITY_TOOLS_IMPLEMENTATION_SUMMARY.md" in cleanup_index_root
    assert "code_quality/TYPESCRIPT_ERROR_FIX_REPORT.md" in cleanup_index_root
    assert "code_quality/TYPESCRIPT_FIX_FINAL_REPORT.md" in cleanup_index_root
    assert "code_quality/TYPESCRIPT_QUALITY_GATE_FIX_REPORT.md" in cleanup_index_root
    assert "./docs/reports/code_quality/PYTHON_QUALITY_TOOLS_IMPLEMENTATION_SUMMARY.md" in guides_claude


def test_bug_lessons_learned_index_is_converged_under_reports_quality() -> None:
    root_claude = (PROJECT_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    guides_claude = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "CLAUDE.md").read_text(encoding="utf-8")
    quality_readme = (PROJECT_ROOT / "docs" / "reports" / "quality" / "README.md").read_text(encoding="utf-8")
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "guides" / "BUG_LESSONS_LEARNED.md").exists()
    assert (PROJECT_ROOT / "docs" / "reports" / "quality" / "BUG_LESSONS_LEARNED.md").is_file()

    assert "docs/reports/quality/BUG_LESSONS_LEARNED.md" in root_claude
    assert "docs/reports/quality/BUG_LESSONS_LEARNED.md" in guides_claude
    assert "docs/reports/quality/BUG_LESSONS_LEARNED.md" in quality_readme
    assert "quality/BUG_LESSONS_LEARNED.md" in reports_index
    assert "quality/BUG_LESSONS_LEARNED.md" in cleanup_index_root


def test_agents_cleanup_completion_docs_are_converged_under_reports_completion_reports() -> None:
    agents_index = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "AGENTS_DOCUMENTATION_INDEX.md").read_text(
        encoding="utf-8"
    )
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    completion_index = (PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "guides" / "AGENTS_CLEANUP_COMPLETION_SUMMARY.md").exists()
    assert not (PROJECT_ROOT / "docs" / "guides" / "AGENTS_CLEANUP_FINAL_STATUS.md").exists()
    assert (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "CLAUDE_AGENTS_SUMMARY.md").is_file()

    assert (
        PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "AGENTS_CLEANUP_COMPLETION_SUMMARY.md"
    ).is_file()
    assert (PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "AGENTS_CLEANUP_FINAL_STATUS.md").is_file()

    assert "../reports/completion_reports/AGENTS_CLEANUP_FINAL_STATUS.md" in agents_index
    assert "../reports/completion_reports/AGENTS_CLEANUP_COMPLETION_SUMMARY.md" in agents_index
    assert "./CLAUDE_AGENTS_SUMMARY.md" in agents_index
    assert "completion_reports/AGENTS_CLEANUP_COMPLETION_SUMMARY.md" in reports_index
    assert "completion_reports/AGENTS_CLEANUP_FINAL_STATUS.md" in reports_index
    assert "AGENTS_CLEANUP_COMPLETION_SUMMARY" in completion_index
    assert "AGENTS_CLEANUP_FINAL_STATUS" in completion_index
    assert "completion_reports/AGENTS_CLEANUP_COMPLETION_SUMMARY.md" in cleanup_index_root
    assert "completion_reports/AGENTS_CLEANUP_FINAL_STATUS.md" in cleanup_index_root


def test_multi_cli_main_cli_lessons_learned_is_converged_under_reports_worklogs() -> None:
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    phase7_proposal = (
        PROJECT_ROOT / "docs" / "reports" / "phase7_worktree_collaboration_proposal.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "guides" / "MULTI_CLI_MAIN_CLI_LESSONS_LEARNED.md").exists()
    assert (PROJECT_ROOT / "docs" / "reports" / "worklogs" / "MULTI_CLI_MAIN_CLI_LESSONS_LEARNED.md").is_file()

    assert "worklogs/MULTI_CLI_MAIN_CLI_LESSONS_LEARNED.md" in reports_index
    assert "worklogs/MULTI_CLI_MAIN_CLI_LESSONS_LEARNED.md" in cleanup_index_root
    assert "../reports/worklogs/MULTI_CLI_MAIN_CLI_LESSONS_LEARNED.md" in phase7_proposal


def test_api_endpoints_statistics_report_is_converged_under_docs_api_family() -> None:
    api_readme = (PROJECT_ROOT / "docs" / "api" / "README.md").read_text(encoding="utf-8")
    guides_readme_integration = (
        PROJECT_ROOT / "docs" / "api" / "guides" / "integration" / "README_INTEGRATION.md"
    ).read_text(encoding="utf-8")
    frontend_backend_plan = (
        PROJECT_ROOT / "docs" / "api" / "guides" / "integration" / "前后端整合与部署完整方案.md"
    ).read_text(encoding="utf-8")
    reports_review = (
        PROJECT_ROOT / "docs" / "reports" / "ARTDECO_MENU_FRONTEND_DESIGN_REVIEW.md"
    ).read_text(encoding="utf-8")
    reports_analysis = (
        PROJECT_ROOT / "docs" / "reports" / "MOCK_TO_REAL_DATA_MIGRATION_ANALYSIS.md"
    ).read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "guides" / "API_ENDPOINTS_STATISTICS_REPORT.md").exists()
    assert (PROJECT_ROOT / "docs" / "api" / "API_ENDPOINTS_STATISTICS_REPORT.md").is_file()

    assert "docs/api/API_ENDPOINTS_STATISTICS_REPORT.md" in api_readme
    assert "docs/api/API_ENDPOINTS_STATISTICS_REPORT.md" in guides_readme_integration
    assert "docs/api/API_ENDPOINTS_STATISTICS_REPORT.md" in frontend_backend_plan
    assert "docs/api/API_ENDPOINTS_STATISTICS_REPORT.md" in reports_review
    assert "docs/api/API_ENDPOINTS_STATISTICS_REPORT.md" in reports_analysis
    assert "api/API_ENDPOINTS_STATISTICS_REPORT.md" in cleanup_index_root


def test_api_validation_and_error_guides_are_converged_under_docs_api_family() -> None:
    api_readme = (PROJECT_ROOT / "docs" / "api" / "README.md").read_text(encoding="utf-8")
    api_index = (PROJECT_ROOT / "docs" / "api" / "INDEX.md").read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    api_contract_report = (PROJECT_ROOT / "docs" / "reports" / "README_API_CONTRACT.md").read_text(
        encoding="utf-8"
    )
    error_code_guide = (PROJECT_ROOT / "docs" / "api" / "ERROR_CODE_GUIDE.md").read_text(encoding="utf-8")
    exception_handler_guide = (
        PROJECT_ROOT / "docs" / "api" / "EXCEPTION_HANDLER_GUIDE.md"
    ).read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    api_support_docs = [
        "VALIDATION_GUIDE.md",
        "ERROR_CODE_GUIDE.md",
        "EXCEPTION_HANDLER_GUIDE.md",
    ]

    for name in api_support_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "api" / name).is_file()
        assert name.removesuffix(".md") not in guides_index
        assert f"api/{name}" in cleanup_index_root

    assert "/opt/claude/mystocks_spec/docs/api/README.md" in api_index
    assert "/opt/claude/mystocks_spec/docs/api/guides/development/" in api_index
    assert "/opt/claude/mystocks_spec/docs/api/guides/integration/INDEX.md" in api_index
    assert "/opt/claude/mystocks_spec/docs/api/specifications/INDEX.md" in api_index
    assert "/opt/claude/mystocks_spec/docs/api/testing/INDEX.md" in api_index
    assert "VALIDATION_GUIDE.md" not in api_index
    assert "ERROR_CODE_GUIDE.md" not in api_index
    assert "EXCEPTION_HANDLER_GUIDE.md" not in api_index

    assert "docs/api/ERROR_CODE_GUIDE.md" in api_contract_report
    assert "docs/api/EXCEPTION_HANDLER_GUIDE.md" in api_contract_report
    assert "docs/api/VALIDATION_GUIDE.md" in api_contract_report
    assert "docs/api/VALIDATION_GUIDE.md" in error_code_guide
    assert "docs/api/ERROR_CODE_GUIDE.md" in exception_handler_guide
    assert "docs/api/VALIDATION_GUIDE.md" in exception_handler_guide
    assert "/opt/claude/mystocks_spec/docs/api/ERROR_CODE_GUIDE.md" in api_readme
    assert "/opt/claude/mystocks_spec/docs/api/EXCEPTION_HANDLER_GUIDE.md" in api_readme
    assert "/opt/claude/mystocks_spec/docs/api/VALIDATION_GUIDE.md" in api_readme


def test_api_alignment_and_contract_plan_guides_are_converged_under_docs_api_guides_integration() -> None:
    api_readme = (PROJECT_ROOT / "docs" / "api" / "README.md").read_text(encoding="utf-8")
    api_guides_index = (PROJECT_ROOT / "docs" / "api" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    integration_status = (
        PROJECT_ROOT / "docs" / "api" / "guides" / "integration" / "api_integration_implementation_status.md"
    ).read_text(encoding="utf-8")
    readme_integration = (
        PROJECT_ROOT / "docs" / "api" / "guides" / "integration" / "README_INTEGRATION.md"
    ).read_text(encoding="utf-8")
    frontend_backend_plan = (
        PROJECT_ROOT / "docs" / "api" / "guides" / "integration" / "前后端整合与部署完整方案.md"
    ).read_text(encoding="utf-8")
    routing_solution = (PROJECT_ROOT / "docs" / "api" / "ROUTING_OPTIMIZATION_SOLUTION.md").read_text(
        encoding="utf-8"
    )
    deployment_checklist = (
        PROJECT_ROOT / "docs" / "reports" / "API_DEPLOYMENT_VERIFICATION_CHECKLIST.md"
    ).read_text(encoding="utf-8")
    standardization_e2e = (
        PROJECT_ROOT / "docs" / "reports" / "API_STANDARDIZATION_E2E_VERIFICATION_REPORT_2026-01-01.md"
    ).read_text(encoding="utf-8")
    victory_lap = (PROJECT_ROOT / "docs" / "reports" / "VICTORY_LAP_STATUS_REPORT.md").read_text(
        encoding="utf-8"
    )
    standardization_plan = (
        PROJECT_ROOT / "docs" / "api" / "guides" / "integration" / "API_STANDARDIZATION_MASTER_PLAN.md"
    ).read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    integration_docs = [
        "API_CONTRACT_VERIFICATION_PLAN.md",
        "API_STANDARDIZATION_MASTER_PLAN.md",
        "API_VERIFICATION_EXECUTION_PLAN.md",
        "README_INTEGRATION.md",
        "API对齐方案.md",
        "API对齐核心流程.md",
        "前后端整合与部署完整方案.md",
    ]

    for name in integration_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "api" / "guides" / "integration" / name).is_file()
        assert name.removesuffix(".md") not in guides_index
        assert name.removesuffix(".md") in api_guides_index
        assert f"guides/integration/{name}" in cleanup_index_root

    assert "/opt/claude/mystocks_spec/docs/api/guides/development/api_development_guidelines.md" in api_readme
    assert "/opt/claude/mystocks_spec/docs/api/guides/integration/INDEX.md" in api_readme
    assert "/opt/claude/mystocks_spec/docs/api/testing/compliance/api_acceptance_standards.md" in api_readme
    assert "/opt/claude/mystocks_spec/docs/api/specifications/core/api_specification.md" in api_readme
    assert "docs/api/guides/integration/API对齐核心流程.md" in integration_status
    assert "docs/api/guides/integration/API对齐方案.md" in integration_status
    assert "docs/api/guides/integration/前后端整合与部署完整方案.md" in readme_integration
    assert "docs/api/API_ENDPOINTS_STATISTICS_REPORT.md" in readme_integration
    assert "docs/api/API_ENDPOINTS_STATISTICS_REPORT.md" in frontend_backend_plan
    assert "docs/api/guides/integration/API对齐核心流程.md" in routing_solution
    assert "docs/api/guides/integration/API_STANDARDIZATION_MASTER_PLAN.md" in deployment_checklist
    assert "docs/api/guides/integration/API_STANDARDIZATION_MASTER_PLAN.md" in standardization_e2e
    assert "docs/api/guides/integration/API_STANDARDIZATION_MASTER_PLAN.md" in victory_lap
    assert "docs/api/guides/integration/API对齐核心流程.md" in standardization_plan or (
        "./API对齐核心流程.md" in standardization_plan
    )


def test_api_fix_implementation_guide_is_converged_under_docs_api_guides_integration() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    api_index = (PROJECT_ROOT / "docs" / "api" / "INDEX.md").read_text(encoding="utf-8")
    integration_index = (
        PROJECT_ROOT / "docs" / "api" / "guides" / "integration" / "INDEX.md"
    ).read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    guides_claude = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "CLAUDE.md").read_text(encoding="utf-8")
    documentation_guide = (
        PROJECT_ROOT / "docs" / "guides" / "documentation" / "DOCUMENTATION_WORKFLOW_GUIDE.md"
    ).read_text(encoding="utf-8")
    migration_script = (
        PROJECT_ROOT / "scripts" / "dev" / "tools" / "migrate_docs_structure.py"
    ).read_text(encoding="utf-8")

    name = "implementation-guide.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "api" / "guides" / "integration" / name).is_file()
    assert name.removesuffix(".md") not in guides_index
    assert f"guides/integration/{name}" in api_index
    assert name.removesuffix(".md") in integration_index
    assert f"api/guides/integration/{name}" in cleanup_index_root
    assert "frontend/enhanced-ui-ux-guide.md" in guides_claude
    assert "api/guides/integration/implementation-guide.md" in documentation_guide
    assert '\"IMPLEMENTATION_GUIDE.md\": \"api/guides/integration/implementation-guide.md\"' in migration_script


def test_api_index_root_is_converged_under_reports_cleanup_index_artifacts() -> None:
    api_index = (PROJECT_ROOT / "docs" / "api" / "INDEX.md").read_text(encoding="utf-8")
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index = (PROJECT_ROOT / "docs" / "reports" / "cleanup" / "INDEX.md").read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "api" / "INDEX_root.md").exists()
    assert (PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "api" / "INDEX_root.md").is_file()

    assert "cleanup/index-artifacts/api/INDEX_root.md" in reports_index
    assert "index-artifacts/api/INDEX_root.md" in cleanup_index
    assert "INDEX_root.md" not in api_index


def test_standards_index_root_is_converged_under_reports_cleanup_index_artifacts() -> None:
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index = (PROJECT_ROOT / "docs" / "reports" / "cleanup" / "INDEX.md").read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "standards" / "INDEX_root.md").exists()
    assert (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "standards" / "INDEX_root.md"
    ).is_file()

    assert "cleanup/index-artifacts/standards/INDEX_root.md" in reports_index
    assert "index-artifacts/standards/INDEX_root.md" in cleanup_index


def test_ai_tooling_guides_are_converged_under_guides_ai_tools_family() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    agents_skills_report = (
        PROJECT_ROOT / "docs" / "api" / "AGENTS_SKILLS_AVAILABILITY_REPORT.md"
    ).read_text(encoding="utf-8")
    apifox_mcp_guide = (PROJECT_ROOT / "docs" / "api" / "apifox_mcp_playwright使用.md").read_text(
        encoding="utf-8"
    )
    agents_doc_index = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "AGENTS_DOCUMENTATION_INDEX.md").read_text(
        encoding="utf-8"
    )
    mongo_coordination = (
        PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "MONGO_MULTICLI_COORDINATION_GUIDE.md"
    ).read_text(encoding="utf-8")
    cli_workflow_guide = (
        PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "CLI_WORKFLOW_GUIDE.md"
    ).read_text(encoding="utf-8")
    main_cli_standards = (
        PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "MAIN_CLI_WORKFLOW_STANDARDS.md"
    ).read_text(encoding="utf-8")
    mongo_checklist = (
        PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "MONGO_MULTICLI_OPERATION_CHECKLIST.md"
    ).read_text(encoding="utf-8")
    update_mydoc_opencode_guides = (
        PROJECT_ROOT / "scripts" / "opencode" / "update_mydoc_opencode_guides.sh"
    ).read_text(encoding="utf-8")
    migrate_opencode_assets = (
        PROJECT_ROOT / "scripts" / "opencode" / "migrate_opencode_assets_to_mydoc.sh"
    ).read_text(encoding="utf-8")
    task_report = (PROJECT_ROOT / "TASK-REPORT.md").read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    ai_tools_index = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    ai_tool_docs = [
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
        "AGENTS_DOCUMENTATION_INDEX.md",
        "CLAUDE_AGENTS_SUMMARY.md",
        "CLAUDE_CODE_AGENTS_MANAGEMENT_GUIDE.md",
        "GRAPHITI_MCP_WORKFLOW.md",
        "OMC_WORKFLOW_GUIDE.md",
        "OMO_SETUP_GUIDE.md",
        "OpenCode生产级配置与固化指南.md",
        "claude_code_lsp_guide.md",
        "claude_code_plugin_marketplace_fix.md",
        "AMP配置.md",
        "amp-help.md",
        "aider-local-maintenance.md",
        "GEMINI_PROXY_CONFIGURATION_GUIDE.md",
    ]

    for name in ai_tool_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / name).is_file()
        assert f"ai-tools/{name}" in guides_index
        assert f"ai-tools/{name}" in cleanup_index_root

    assert "docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md" in readme
    assert "docs/guides/ai-tools/CLAUDE_AGENTS_SUMMARY.md" in agents_skills_report
    assert "docs/guides/ai-tools/CLAUDE_CODE_AGENTS_MANAGEMENT_GUIDE.md" in agents_skills_report
    assert "docs/guides/ai-tools/GRAPHITI_MCP_WORKFLOW.md" in apifox_mcp_guide
    assert "./CLAUDE_CODE_AGENTS_MANAGEMENT_GUIDE.md" in agents_doc_index
    assert "docs/guides/ai-tools/GRAPHITI_MCP_WORKFLOW.md" in mongo_coordination
    assert "docs/guides/ai-tools/GRAPHITI_MCP_WORKFLOW.md" in cli_workflow_guide
    assert "docs/guides/ai-tools/GRAPHITI_MCP_WORKFLOW.md" in main_cli_standards
    assert "docs/guides/ai-tools/GRAPHITI_MCP_WORKFLOW.md" in mongo_checklist
    assert 'SRC_PROD_GUIDE="$SRC_ROOT/ai-tools/OpenCode生产级配置与固化指南.md"' in update_mydoc_opencode_guides
    assert 'SRC_OMO_GUIDE="$SRC_ROOT/ai-tools/OMO_SETUP_GUIDE.md"' in update_mydoc_opencode_guides
    assert 'SRC_GUIDE="$SRC_ROOT/docs/guides/ai-tools/OMO_SETUP_GUIDE.md"' in migrate_opencode_assets
    assert "docs/guides/ai-tools/GEMINI_PROXY_CONFIGURATION_GUIDE.md" in task_report
    assert "AMP配置" in ai_tools_index
    assert "amp-help" in ai_tools_index
    assert "aider-local-maintenance" in ai_tools_index
    assert "AGENTS" in ai_tools_index
    assert "CLAUDE" in ai_tools_index
    assert "GEMINI_PROXY_CONFIGURATION_GUIDE" in ai_tools_index
    assert "GEMINI" in ai_tools_index
    assert "CLAUDE_CODE_AGENTS_MANAGEMENT_GUIDE" in ai_tools_index
    assert "GRAPHITI_MCP_WORKFLOW" in ai_tools_index
    assert "OMC_WORKFLOW_GUIDE" in ai_tools_index
    assert "OMO_SETUP_GUIDE" in ai_tools_index
    assert "OpenCode生产级配置与固化指南" in ai_tools_index
    assert "claude_code_lsp_guide" in ai_tools_index
    assert "claude_code_plugin_marketplace_fix" in ai_tools_index
    omo_setup_guide = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "OMO_SETUP_GUIDE.md").read_text(
        encoding="utf-8"
    )
    opencode_prod_guide = (
        PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "OpenCode生产级配置与固化指南.md"
    ).read_text(encoding="utf-8")

    assert "local-only" in omo_setup_guide
    assert ".gitignore" in omo_setup_guide
    assert "local-only" in opencode_prod_guide
    assert ".gitignore" in opencode_prod_guide


def test_ai_quick_start_is_converged_under_guides_ai_tools_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    ai_tools_index = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    ai_quick_start = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "AI_QUICK_START.md").read_text(
        encoding="utf-8"
    )
    function_tree = (PROJECT_ROOT / "docs" / "FUNCTION_TREE.md").read_text(encoding="utf-8")
    feature_workflow = (
        PROJECT_ROOT / "docs" / "guides" / "governance" / "FEATURE_MANAGEMENT_WORKFLOW.md"
    ).read_text(encoding="utf-8")
    routing_impl = (
        PROJECT_ROOT / "docs" / "plans" / "2026-03-12-function-tree-doc-routing-implementation-plan.md"
    ).read_text(encoding="utf-8")
    routing_design = (
        PROJECT_ROOT / "docs" / "plans" / "2026-03-12-function-tree-doc-routing-design.md"
    ).read_text(encoding="utf-8")
    backlog_priorities = (
        PROJECT_ROOT / "docs" / "plans" / "2026-03-13-future-backlog-priorities.md"
    ).read_text(encoding="utf-8")
    openspec_tasks = (
        PROJECT_ROOT / "openspec" / "changes" / "govern-function-tree-as-code" / "tasks.md"
    ).read_text(encoding="utf-8")
    openspec_proposal = (
        PROJECT_ROOT / "openspec" / "changes" / "govern-function-tree-as-code" / "proposal.md"
    ).read_text(encoding="utf-8")
    task_report = (PROJECT_ROOT / "TASK-REPORT.md").read_text(encoding="utf-8")

    name = "AI_QUICK_START.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / name).is_file()
    assert f"ai-tools/{name}" in guides_index
    assert name.removesuffix(".md") in ai_tools_index
    assert f"guides/ai-tools/{name}" in cleanup_index_root
    assert "./guides/ai-tools/AI_QUICK_START.md" in function_tree
    assert "docs/guides/ai-tools/AI_QUICK_START.md" in feature_workflow
    assert "docs/guides/ai-tools/AI_QUICK_START.md" in routing_impl
    assert "docs/guides/ai-tools/AI_QUICK_START.md" in routing_design
    assert "../guides/ai-tools/AI_QUICK_START.md" in backlog_priorities
    assert "docs/guides/ai-tools/AI_QUICK_START.md" in openspec_tasks
    assert "docs/guides/ai-tools/AI_QUICK_START.md" in openspec_proposal
    assert "docs/guides/ai-tools/AI_QUICK_START.md" in task_report
    assert "../../../architecture/STANDARDS.md" in ai_quick_start
    assert "../../../openspec/AGENTS.md" in ai_quick_start
    assert "../../INDEX.md" in ai_quick_start
    assert "../../FUNCTION_TREE.md" in ai_quick_start
    assert "../governance/FEATURE_MANAGEMENT_WORKFLOW.md" in ai_quick_start
    assert "../../operations/README.md" in ai_quick_start


def test_governance_guides_are_converged_under_guides_governance_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    governance_index = (PROJECT_ROOT / "docs" / "guides" / "governance" / "INDEX.md").read_text(encoding="utf-8")

    governance_docs = [
        "FEATURE_MANAGEMENT_WORKFLOW.md",
        "TECHNICAL_DEBT_MANAGEMENT.md",
    ]

    for name in governance_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "governance" / name).is_file()
        assert f"guides/governance/{name}" in cleanup_index_root
        assert name.removesuffix(".md") in governance_index

    assert "[`governance/`]" in guides_index
    assert "/opt/claude/mystocks_spec/architecture/STANDARDS.md" in governance_index
    assert "/opt/claude/mystocks_spec/docs/overview/documentation-system.md" in governance_index


def test_onboarding_guides_are_converged_under_guides_onboarding_family() -> None:
    docs_index = (PROJECT_ROOT / "docs" / "INDEX.md").read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    onboarding_index = (PROJECT_ROOT / "docs" / "guides" / "onboarding" / "INDEX.md").read_text(encoding="utf-8")

    onboarding_docs = [
        "DEVELOPER_GUIDE.md",
        "USER_GUIDE.md",
    ]

    for name in onboarding_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "onboarding" / name).is_file()
        assert f"- [{name.removesuffix('.md')}]({name})" not in guides_index
        assert f"onboarding/{name}" in guides_index
        assert f"guides/onboarding/{name}" in docs_index
        assert f"guides/onboarding/{name}" in cleanup_index_root
        assert name.removesuffix(".md") in onboarding_index


def test_ai_test_optimizer_guides_are_converged_under_guides_ai_tools_family() -> None:
    optimizer_user_guide = (
        PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "AI_TEST_OPTIMIZER_USER_GUIDE.md"
    ).read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    ai_tools_index = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    optimizer_docs = [
        "AI_TEST_OPTIMIZER_TRAINING.md",
        "AI_TEST_OPTIMIZER_USER_GUIDE.md",
    ]

    for name in optimizer_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / name).is_file()
        assert f"ai-tools/{name}" in guides_index
        assert f"ai-tools/{name}" in cleanup_index_root

    assert "docs/guides/ai-tools/AI_TEST_OPTIMIZER_USER_GUIDE.md" in optimizer_user_guide
    assert "AI_TEST_OPTIMIZER_TRAINING" in ai_tools_index
    assert "AI_TEST_OPTIMIZER_USER_GUIDE" in ai_tools_index


def test_maestro_and_multicli_runtime_docs_are_converged_under_guides_multicli_tasks() -> None:
    task_md = (PROJECT_ROOT / "TASK.md").read_text(encoding="utf-8")
    maestro_readme = (PROJECT_ROOT / "src" / "services" / "maestro" / "README.md").read_text(encoding="utf-8")
    maestro_quick_start = (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "MAESTRO_QUICK_START.md").read_text(
        encoding="utf-8"
    ) if (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "MAESTRO_QUICK_START.md").exists() else ""
    mongodb_impl_plan = (
        PROJECT_ROOT / "docs" / "plans" / "2026-03-13-mongodb-multicli-coordination-implementation-plan.md"
    ).read_text(encoding="utf-8")
    mongodb_design = (
        PROJECT_ROOT / "docs" / "plans" / "2026-03-13-mongodb-multicli-coordination-design.md"
    ).read_text(encoding="utf-8")
    phase7_proposal = (
        PROJECT_ROOT / "docs" / "reports" / "phase7_worktree_collaboration_proposal.md"
    ).read_text(encoding="utf-8")
    reports_cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    multicli_index = (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "INDEX.md").read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "guides" / "MAESTRO_SUMMARY.md").exists()
    assert not (PROJECT_ROOT / "docs" / "guides" / "MAESTRO_QUICK_START.md").exists()
    assert not (PROJECT_ROOT / "docs" / "guides" / "SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md").exists()
    assert not (PROJECT_ROOT / "docs" / "guides" / "MULTI_CLI_PROMPT_STRATEGIES.md").exists()

    assert (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "MAESTRO_SUMMARY.md").is_file()
    assert (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "MAESTRO_QUICK_START.md").is_file()
    assert (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md").is_file()
    assert (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "MULTI_CLI_PROMPT_STRATEGIES.md").is_file()

    assert "docs/guides/multi-cli-tasks/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md" in task_md
    assert "docs/guides/multi-cli-tasks/MULTI_CLI_PROMPT_STRATEGIES.md" in task_md
    assert "docs/guides/multi-cli-tasks/MAESTRO_SUMMARY.md" in maestro_readme
    assert "docs/guides/multi-cli-tasks/MAESTRO_QUICK_START.md" in maestro_readme
    assert "docs/guides/multi-cli-tasks/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md" in maestro_readme
    assert "docs/guides/multi-cli-tasks/MAESTRO_SUMMARY.md" in mongodb_impl_plan
    assert "docs/guides/multi-cli-tasks/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md" in mongodb_impl_plan
    assert "docs/guides/multi-cli-tasks/MAESTRO_SUMMARY.md" in mongodb_design
    assert "../docs/guides/multi-cli-tasks/MULTI_CLI_PROMPT_STRATEGIES.md" in phase7_proposal
    assert "../docs/guides/multi-cli-tasks/MULTI_CLI_WORKTREE_MANAGEMENT.md" in phase7_proposal
    assert "multi-cli-tasks/MAESTRO_SUMMARY.md" in reports_cleanup_index_root
    assert "multi-cli-tasks/MAESTRO_QUICK_START.md" in reports_cleanup_index_root
    assert "multi-cli-tasks/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md" in reports_cleanup_index_root
    assert "multi-cli-tasks/MULTI_CLI_PROMPT_STRATEGIES.md" in reports_cleanup_index_root
    assert "multi-cli-tasks/MAESTRO_SUMMARY.md" in guides_index
    assert "multi-cli-tasks/MAESTRO_QUICK_START.md" in guides_index
    assert "multi-cli-tasks/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md" in guides_index
    assert "multi-cli-tasks/MULTI_CLI_PROMPT_STRATEGIES.md" in guides_index
    assert "MAESTRO_SUMMARY" in multicli_index
    assert "MAESTRO_QUICK_START" in multicli_index
    assert "SYMPHONY_LOCAL_MULTICLI_WORKFLOW" in multicli_index
    assert "MULTI_CLI_PROMPT_STRATEGIES" in multicli_index


def test_selected_web_guides_are_converged_under_guides_web_family() -> None:
    web_access_standard = (
        PROJECT_ROOT / "docs" / "guides" / "web" / "WEB_ACCESS_VERIFICATION_STANDARD.md"
    ).read_text(encoding="utf-8")
    html_sample_readme = (PROJECT_ROOT / "docs" / "design" / "html_sample" / "README.md").read_text(
        encoding="utf-8"
    )
    phase1_completion = (
        PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "PHASE1_UI_UX_FOUNDATION_COMPLETION_REPORT.md"
    ).read_text(encoding="utf-8")
    e2e_issues = (PROJECT_ROOT / "docs" / "reports" / "E2E_TEST_ISSUES_REPORT_2026-01-27.md").read_text(
        encoding="utf-8"
    )
    frontend_port_fix = (
        PROJECT_ROOT / "docs" / "reports" / "FRONTEND_PORT_FIX_COMPLETION_REPORT.md"
    ).read_text(encoding="utf-8")
    frontend_nav_status = (
        PROJECT_ROOT / "docs" / "reports" / "IMPLEMENT_WEB_FRONTEND_V2_NAVIGATION_STATUS_REPORT.md"
    ).read_text(encoding="utf-8")
    pm2_frontend_report = (
        PROJECT_ROOT / "docs" / "reports" / "PM2_FRONTEND_TEST_COMPLETION_REPORT.md"
    ).read_text(encoding="utf-8")
    ralph_summary = (PROJECT_ROOT / "docs" / "reports" / "RALPH_LOOP_COMPLETION_SUMMARY.md").read_text(
        encoding="utf-8"
    )
    architecture_readme = (PROJECT_ROOT / "docs" / "architecture" / "README.md").read_text(encoding="utf-8")
    openspec_tasks = (
        PROJECT_ROOT / "openspec" / "changes" / "frontend-optimization-six-phase" / "tasks.md"
    ).read_text(encoding="utf-8")
    tests_tasks = (
        PROJECT_ROOT / "tests" / "changes" / "frontend-optimization-six-phase" / "tasks.md"
    ).read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    web_index = (PROJECT_ROOT / "docs" / "guides" / "web" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    moved_names = [
        "WEB_FRAMEWORK_INTEGRATION_PLAN.md",
        "WEB_FRONTEND_STARTUP_GUIDE.md",
        "WEB_HTML_SAMPLES_GUIDE.md",
        "WEB_ROUTER_MIGRATION_RECORD.md",
    ]

    for name in moved_names:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "web" / name).is_file()

    assert "./web/WEB_FRONTEND_STARTUP_GUIDE.md" in web_access_standard
    assert "../../guides/web/WEB_HTML_SAMPLES_GUIDE.md" in html_sample_readme
    assert "/docs/guides/web/WEB_ROUTER_MIGRATION_RECORD.md" in phase1_completion
    assert "docs/guides/web/WEB_FRONTEND_STARTUP_GUIDE.md" in e2e_issues
    assert "docs/guides/web/WEB_FRONTEND_STARTUP_GUIDE.md" in frontend_port_fix
    assert "docs/guides/web/WEB_FRONTEND_STARTUP_GUIDE.md" in frontend_nav_status
    assert "docs/guides/web/WEB_FRONTEND_STARTUP_GUIDE.md" in pm2_frontend_report
    assert "docs/guides/web/WEB_FRONTEND_STARTUP_GUIDE.md" in ralph_summary
    assert "docs/guides/web/WEB_FRONTEND_STARTUP_GUIDE.md" in architecture_readme
    assert "docs/guides/web/WEB_ROUTER_MIGRATION_RECORD.md" in openspec_tasks
    assert "docs/guides/web/WEB_ROUTER_MIGRATION_RECORD.md" in tests_tasks
    assert "web/WEB_FRAMEWORK_INTEGRATION_PLAN.md" in guides_index
    assert "web/WEB_FRONTEND_STARTUP_GUIDE.md" in guides_index
    assert "web/WEB_HTML_SAMPLES_GUIDE.md" in guides_index
    assert "web/WEB_ROUTER_MIGRATION_RECORD.md" in guides_index
    assert "WEB_FRAMEWORK_INTEGRATION_PLAN" in web_index
    assert "WEB_FRONTEND_STARTUP_GUIDE" in web_index
    assert "WEB_HTML_SAMPLES_GUIDE" in web_index
    assert "WEB_ROUTER_MIGRATION_RECORD" in web_index
    assert "web/WEB_FRAMEWORK_INTEGRATION_PLAN.md" in cleanup_index_root
    assert "web/WEB_FRONTEND_STARTUP_GUIDE.md" in cleanup_index_root
    assert "web/WEB_HTML_SAMPLES_GUIDE.md" in cleanup_index_root
    assert "web/WEB_ROUTER_MIGRATION_RECORD.md" in cleanup_index_root


def test_html5_migration_experience_doc_is_converged_under_guides_web_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    web_index = (PROJECT_ROOT / "docs" / "guides" / "web" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    name = "2026-01-23-html5-migration-experience-optimization.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "guides" / "web" / name).is_file()
    assert f"web/{name}" in guides_index
    assert name.removesuffix(".md") in web_index
    assert f"guides/web/{name}" in cleanup_index_root or f"web/{name}" in cleanup_index_root


def test_theme_guides_are_converged_under_guides_web_family() -> None:
    linear_completion_report = (
        PROJECT_ROOT / "docs" / "guides" / "web" / "LINEAR_THEME_COMPLETION_REPORT.md"
    ).read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    web_index = (PROJECT_ROOT / "docs" / "guides" / "web" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    theme_docs = [
        "LINEAR_THEME_GUIDE.md",
        "TECHSTYLE_THEME_GUIDE.md",
    ]

    for name in theme_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "web" / name).is_file()
        assert f"web/{name}" in guides_index
        assert f"web/{name}" in cleanup_index_root

    assert "/docs/guides/web/LINEAR_THEME_GUIDE.md" in linear_completion_report
    assert "LINEAR_THEME_GUIDE" in web_index
    assert "TECHSTYLE_THEME_GUIDE" in web_index


def test_additional_web_runtime_and_planning_guides_are_converged_under_guides_web_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    web_index = (PROJECT_ROOT / "docs" / "guides" / "web" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    verify_web_access_js = (PROJECT_ROOT / "scripts" / "verify_web_access.js").read_text(encoding="utf-8")
    verify_web_access_mjs = (PROJECT_ROOT / "scripts" / "dev" / "verify_web_access.mjs").read_text(
        encoding="utf-8"
    )
    p0_report = (PROJECT_ROOT / "docs" / "reports" / "P0_TASK_COMPLETION_REPORT.md").read_text(encoding="utf-8")
    testing_upgrade = (PROJECT_ROOT / "web" / "frontend" / "TESTING-UPGRADE-COMMIT-GROUPS.md").read_text(
        encoding="utf-8"
    )
    frontend_task_report = (PROJECT_ROOT / "web" / "frontend" / "TASK-REPORT.md").read_text(encoding="utf-8")
    openspec_impl = (
        PROJECT_ROOT / "openspec" / "changes" / "frontend-optimization-six-phase" / "implementation-plan.md"
    ).read_text(encoding="utf-8")
    openspec_readme = (
        PROJECT_ROOT / "openspec" / "changes" / "frontend-optimization-six-phase" / "README.md"
    ).read_text(encoding="utf-8")
    openspec_proposal = (
        PROJECT_ROOT / "openspec" / "changes" / "frontend-optimization-six-phase" / "proposal.md"
    ).read_text(encoding="utf-8")
    openspec_design = (
        PROJECT_ROOT / "openspec" / "changes" / "frontend-optimization-six-phase" / "design.md"
    ).read_text(encoding="utf-8")
    tests_impl = (
        PROJECT_ROOT / "tests" / "changes" / "frontend-optimization-six-phase" / "implementation-plan.md"
    ).read_text(encoding="utf-8")
    tests_readme = (
        PROJECT_ROOT / "tests" / "changes" / "frontend-optimization-six-phase" / "README.md"
    ).read_text(encoding="utf-8")
    tests_proposal = (
        PROJECT_ROOT / "tests" / "changes" / "frontend-optimization-six-phase" / "proposal.md"
    ).read_text(encoding="utf-8")
    tests_design = (
        PROJECT_ROOT / "tests" / "changes" / "frontend-optimization-six-phase" / "design.md"
    ).read_text(encoding="utf-8")

    web_docs = [
        "MYSTOCKS_WEB_STARTUP_EXPERIENCE.md",
        "WEB_ACCESS_VERIFICATION_STANDARD.md",
        "WEB_CLIENT_OPERATION_PLAN.md",
        "WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md",
        "WEB_TESTING_TOOLS_SETUP.md",
    ]

    for name in web_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "web" / name).is_file()
        assert f"web/{name}" in guides_index
        assert f"web/{name}" in cleanup_index_root
        assert name.removesuffix(".md") in web_index

    assert "docs/guides/web/WEB_ACCESS_VERIFICATION_STANDARD.md" in verify_web_access_js
    assert "docs/guides/web/WEB_ACCESS_VERIFICATION_STANDARD.md" in verify_web_access_mjs
    assert "docs/guides/web/WEB_CLIENT_OPERATION_PLAN.md" in p0_report
    assert "docs/guides/web/WEB_TESTING_TOOLS_SETUP.md" in testing_upgrade
    assert "docs/guides/web/WEB_TESTING_TOOLS_SETUP.md" in frontend_task_report
    assert "docs/guides/web/WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md" in openspec_impl
    assert "docs/guides/web/WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md" in openspec_readme
    assert "docs/guides/web/WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md" in openspec_proposal
    assert "docs/guides/web/WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md" in openspec_design
    assert "docs/guides/web/WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md" in tests_impl
    assert "docs/guides/web/WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md" in tests_readme
    assert "docs/guides/web/WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md" in tests_proposal
    assert "docs/guides/web/WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md" in tests_design


def test_realtime_integration_guide_is_converged_under_guides_web_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    web_index = (PROJECT_ROOT / "docs" / "guides" / "web" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    name = "PHASE12_3_REALTIME_INTEGRATION.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "guides" / "web" / name).is_file()
    assert f"web/{name}" in guides_index
    assert name.removesuffix(".md") in web_index
    assert f"guides/web/{name}" in cleanup_index_root or f"web/{name}" in cleanup_index_root


def test_websocket_performance_guide_is_converged_under_guides_web_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    web_index = (PROJECT_ROOT / "docs" / "guides" / "web" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    pm2_guide = (PROJECT_ROOT / "docs" / "guides" / "pm2" / "PM2_PLAYWRIGHT_TESTING_GUIDE.md").read_text(
        encoding="utf-8"
    )

    name = "WEBSOCKET_PERFORMANCE_OPTIMIZATION_GUIDE.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "guides" / "web" / name).is_file()
    assert f"web/{name}" in guides_index
    assert name.removesuffix(".md") in web_index
    assert f"guides/web/{name}" in cleanup_index_root or f"web/{name}" in cleanup_index_root
    assert "../web/WEBSOCKET_PERFORMANCE_OPTIMIZATION_GUIDE.md" in pm2_guide


def test_html_to_vue_conversion_guides_are_converged_under_guides_web_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    web_index = (PROJECT_ROOT / "docs" / "guides" / "web" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    conversion_summary = (
        PROJECT_ROOT / "docs" / "reports" / "completion_reports" / "MYSTOCKS_HTML_VUE_CONVERSION_SUMMARY.md"
    ).read_text(encoding="utf-8")
    openspec_audit = (PROJECT_ROOT / "docs" / "reports" / "openspec_audit_summary.md").read_text(
        encoding="utf-8"
    )
    artdeco_proposal = (
        PROJECT_ROOT / "docs" / "design" / "ARTDECO_CONVERSION_OPTIMIZATION_PROPOSAL.md"
    ).read_text(encoding="utf-8")
    optimized_plan = (
        PROJECT_ROOT / "docs" / "guides" / "web" / "HTML_TO_ARTDECO_VUE_CONVERSION_OPTIMIZED_PLAN.md"
    ).read_text(encoding="utf-8")

    docs = [
        "HTML_TO_ARTDECO_VUE_CONVERSION_OPTIMIZED_PLAN.md",
        "MYSTOCKS_HTML_TO_VUE_CONVERSION_STRATEGY.md",
    ]

    for name in docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "web" / name).is_file()
        assert f"web/{name}" in guides_index
        assert name.removesuffix(".md") in web_index
        assert f"guides/web/{name}" in cleanup_index_root or f"web/{name}" in cleanup_index_root

    assert "docs/guides/web/MYSTOCKS_HTML_TO_VUE_CONVERSION_STRATEGY.md" in conversion_summary
    assert "docs/guides/web/MYSTOCKS_HTML_TO_VUE_CONVERSION_STRATEGY.md" in openspec_audit
    assert "docs/guides/web/MYSTOCKS_HTML_TO_VUE_CONVERSION_STRATEGY.md" in artdeco_proposal
    assert "docs/guides/web/HTML_TO_ARTDECO_VUE_CONVERSION_OPTIMIZED_PLAN.md" in optimized_plan


def test_artdeco_guides_are_converged_under_guides_web_family() -> None:
    task_report = (PROJECT_ROOT / "TASK-REPORT.md").read_text(encoding="utf-8")
    frontend_package = (PROJECT_ROOT / "web" / "frontend" / "package.json").read_text(encoding="utf-8")
    artdeco_spec = (PROJECT_ROOT / "docs" / "api" / "ARTDECO_TRADING_CENTER_OPTIMIZED_V3.1.md").read_text(
        encoding="utf-8"
    )
    web_e2e_ref = (PROJECT_ROOT / "docs" / "testing" / "WEB_E2E_TEST_QUICK_REFERENCE.md").read_text(
        encoding="utf-8"
    )
    web_client_plan = (
        PROJECT_ROOT / "docs" / "guides" / "web" / "WEB_CLIENT_OPERATION_PLAN.md"
    ).read_text(encoding="utf-8")
    websocket_perf = (
        PROJECT_ROOT / "docs" / "guides" / "web" / "WEBSOCKET_PERFORMANCE_OPTIMIZATION_GUIDE.md"
    ).read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    web_index = (PROJECT_ROOT / "docs" / "guides" / "web" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    artdeco_docs = [
        "ARTDECO_COMPONENT_GUIDE.md",
        "ARTDECO_GRID_QUICK_REFERENCE.md",
        "ARTDECO_GRID_QUICK_START.md",
        "ARTDECO_MASTER_INDEX.md",
        "ARTDECO_MENU_API_MAPPING.md",
        "ARTDECO_MENU_DATA_FETCHING_IMPLEMENTATION_GUIDE.md",
        "ARTDECO_MENU_STRUCTURE_REFACTOR_PLAN.md",
        "ARTDECO_MENU_USER_TESTING_GUIDE.md",
        "ARTDECO_PAGE_TEMPLATE_GUIDE.md",
        "ARTDECO_SCSS_GOVERNANCE_BASELINE.md",
        "ARTDECO_UI_UX_FUNCTIONALITY_GUIDE.md",
    ]

    for name in artdeco_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "web" / name).is_file()
        assert f"web/{name}" in guides_index
        assert f"web/{name}" in cleanup_index_root

    assert "docs/guides/web/ARTDECO_MASTER_INDEX.md" in task_report
    assert "../../docs/guides/web/ARTDECO_MASTER_INDEX.md" in frontend_package
    assert "../../docs/guides/web/ARTDECO_GRID_QUICK_REFERENCE.md" in frontend_package
    assert "../../docs/guides/web/ARTDECO_UI_UX_FUNCTIONALITY_GUIDE.md" in frontend_package
    assert "docs/guides/web/ARTDECO_GRID_QUICK_REFERENCE.md" in artdeco_spec
    assert "docs/guides/web/ARTDECO_MENU_DATA_FETCHING_IMPLEMENTATION_GUIDE.md" in web_e2e_ref
    assert "./web/ARTDECO_MENU_STRUCTURE_REFACTOR_PLAN.md" in web_client_plan
    assert "./web/ARTDECO_MENU_DATA_FETCHING_IMPLEMENTATION_GUIDE.md" in websocket_perf
    assert "./web/ARTDECO_MENU_API_MAPPING.md" in websocket_perf
    assert "ARTDECO_MASTER_INDEX" in web_index
    assert "ARTDECO_SCSS_GOVERNANCE_BASELINE" in web_index
    assert "ARTDECO_MENU_API_MAPPING" in web_index


def test_additional_ui_and_visualization_guides_are_converged_under_guides_web_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    web_index = (PROJECT_ROOT / "docs" / "guides" / "web" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    bloomberg_summary = (
        PROJECT_ROOT / "docs" / "reports" / "BLOOMBERG_TERMINAL_PROJECT_SUMMARY.md"
    ).read_text(encoding="utf-8")
    bloomberg_testing = (
        PROJECT_ROOT / "docs" / "reports" / "BLOOMBERG_TESTING_COMPLETION_REPORT.md"
    ).read_text(encoding="utf-8")
    a_stock_guide = (PROJECT_ROOT / "docs" / "guides" / "web" / "A_STOCK_DASHBOARD_USER_GUIDE.md").read_text(
        encoding="utf-8"
    )

    ui_docs = [
        "A_STOCK_DASHBOARD_USER_GUIDE.md",
        "BLOOMBERG_TERMINAL_COMPONENT_GUIDE.md",
        "CHART_SYSTEM_USER_GUIDE.md",
        "VUE_TAB_DESIGN_GUIDELINES.md",
        "mystocks-artdeco-available-components.md",
    ]

    for name in ui_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "web" / name).is_file()
        assert f"web/{name}" in guides_index
        assert f"web/{name}" in cleanup_index_root
        assert name.removesuffix(".md") in web_index

    assert "docs/guides/web/BLOOMBERG_TERMINAL_COMPONENT_GUIDE.md" in bloomberg_summary
    assert "docs/guides/web/BLOOMBERG_TERMINAL_COMPONENT_GUIDE.md" in bloomberg_testing
    assert "docs/guides/web/A_STOCK_DASHBOARD_USER_GUIDE.md" in a_stock_guide


def test_typescript_document_cluster_is_converged_under_guides_typescript_family() -> None:
    typescript_files = [
        "TYPESCRIPT_ERROR_FIXING_GUIDE.md",
        "TYPESCRIPT_EXTENSION_SYSTEM_BALANCED_PLAN.md",
        "TYPESCRIPT_EXTENSION_SYSTEM_IMPLEMENTATION_PLAN.md",
        "TYPESCRIPT_EXTENSION_SYSTEM_IMPLEMENTATION_PLAN_V3.md",
        "TYPESCRIPT_SOURCE_FIX_GUIDE.md",
        "TYPEScript_EXTENSION_SYSTEM_PROPOSAL.md",
        "TYPE_CHECKING_INTEGRATION.md",
        "TypeScript_优化修复方案.md",
        "TypeScript_快速修复指南.md",
        "Typescript_API_REFERENCE.md",
        "Typescript_BEST_PRACTICES.md",
        "Typescript_CONFIG_REFERENCE.md",
        "Typescript_QUICKSTART.md",
        "Typescript_TRAINING_ADVANCED.md",
        "Typescript_TRAINING_BEGINNER.md",
        "Typescript_TROUBLESHOOTING.md",
        "Typescript_USER_GUIDE.md",
    ]

    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    typescript_report = (
        PROJECT_ROOT / "docs" / "reports" / "TypeScript_Documentation_Project_Complete_2026-01-20.md"
    ).read_text(encoding="utf-8")
    typescript_inventory = (
        PROJECT_ROOT / "docs" / "reports" / "Typescript文档整理_完整清单_2026-01-20.md"
    ).read_text(encoding="utf-8")

    for name in typescript_files:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "typescript" / name).is_file()
        assert f"typescript/{name}" in guides_index
        assert f"typescript/{name}" in cleanup_index_root

    assert "docs/guides/typescript/Typescript_QUICKSTART.md" in typescript_report
    assert "docs/guides/typescript/Typescript_BEST_PRACTICES.md" in typescript_report
    assert "docs/guides/typescript/TYPESCRIPT_ERROR_FIXING_GUIDE.md" in typescript_inventory
    assert "docs/guides/typescript/TYPESCRIPT_SOURCE_FIX_GUIDE.md" in typescript_inventory


def test_chrome_devtools_guides_are_converged_under_guides_chrome_devtools_family() -> None:
    web_startup_guide = (PROJECT_ROOT / "docs" / "guides" / "web" / "WEB_FRONTEND_STARTUP_GUIDE.md").read_text(
        encoding="utf-8"
    )
    web_access_standard = (
        PROJECT_ROOT / "docs" / "guides" / "web" / "WEB_ACCESS_VERIFICATION_STANDARD.md"
    ).read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    chrome_index = (PROJECT_ROOT / "docs" / "guides" / "chrome-devtools" / "INDEX.md").read_text(
        encoding="utf-8"
    ) if (PROJECT_ROOT / "docs" / "guides" / "chrome-devtools" / "INDEX.md").exists() else ""
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    chrome_docs = [
        "CHROME_DEVTOOLS_MCP_FIX_GUIDE.md",
        "CHROME_DEVTOOLS_MCP_GUIDE.md",
        "CHROME_DEVTOOLS_MCP_SOLUTION.md",
        "chrome-devtools-wsl2-guide.md",
        "mystocks-chromedevtools-testing-guide.md",
    ]

    for name in chrome_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "chrome-devtools" / name).is_file()
        assert f"chrome-devtools/{name}" in guides_index
        assert f"chrome-devtools/{name}" in cleanup_index_root

    assert "docs/guides/chrome-devtools/mystocks-chromedevtools-testing-guide.md" in web_startup_guide
    assert "./chrome-devtools/mystocks-chromedevtools-testing-guide.md" in web_access_standard
    assert "CHROME_DEVTOOLS_MCP_FIX_GUIDE" in chrome_index
    assert "CHROME_DEVTOOLS_MCP_GUIDE" in chrome_index
    assert "CHROME_DEVTOOLS_MCP_SOLUTION" in chrome_index
    assert "chrome-devtools-wsl2-guide" in chrome_index
    assert "mystocks-chromedevtools-testing-guide" in chrome_index


def test_mock_real_data_docs_are_converged_under_guides_mock_data_family() -> None:
    guides_claude = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "CLAUDE.md").read_text(encoding="utf-8")
    overview_claude = (PROJECT_ROOT / "docs" / "overview" / "claude.md").read_text(encoding="utf-8")
    iflow_root = (PROJECT_ROOT / "IFLOW.md").read_text(encoding="utf-8")
    iflow_docs = (PROJECT_ROOT / "docs" / "overview" / "IFLOW.md").read_text(encoding="utf-8")
    knowledge_base = (PROJECT_ROOT / "scripts" / "cli" / "SHARED" / "KNOWLEDGE_BASE.md").read_text(
        encoding="utf-8"
    )
    frontend_env_switch = (PROJECT_ROOT / "web" / "frontend" / "ENVIRONMENT_SWITCHING_GUIDE.md").read_text(
        encoding="utf-8"
    )
    env_switch_report = (
        PROJECT_ROOT / "docs" / "reports" / "ENVIRONMENT_SWITCHING_IMPLEMENTATION_REPORT.md"
    ).read_text(encoding="utf-8")
    migration_analysis = (
        PROJECT_ROOT / "docs" / "reports" / "MOCK_TO_REAL_DATA_MIGRATION_ANALYSIS.md"
    ).read_text(encoding="utf-8")
    cleanup_completion = (
        PROJECT_ROOT / "docs" / "reports" / "MOCK_REAL_DOCS_CLEANUP_COMPLETION_REPORT.md"
    ).read_text(encoding="utf-8")
    cleanup_plan = (PROJECT_ROOT / "docs" / "reports" / "MOCK_REAL_DOCS_CLEANUP_PLAN.md").read_text(
        encoding="utf-8"
    )
    phase2_review = (PROJECT_ROOT / "docs" / "reports" / "reviews" / "PHASE_2_PLAN_REVIEW.md").read_text(
        encoding="utf-8"
    )
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    mock_index = (PROJECT_ROOT / "docs" / "guides" / "mock-data" / "INDEX.md").read_text(
        encoding="utf-8"
    ) if (PROJECT_ROOT / "docs" / "guides" / "mock-data" / "INDEX.md").exists() else ""
    mock_real_index_doc = (
        PROJECT_ROOT / "docs" / "guides" / "mock-data" / "MOCK_REAL_DATA_INDEX.md"
    ).read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    mock_docs = [
        "MOCK_DATA_USAGE_RULES.md",
        "MOCK_REAL_DATA_INDEX.md",
        "MOCK_REAL_DATA_SWITCHING_GUIDE.md",
        "PHASE_2_REAL_DATA_INTEGRATION_PLAN.md",
        "REAL_DATA_INTEGRATION_PRINCIPLES.md",
        "REAL_DATA_INTEGRATION_ROADMAP.md",
        "README_MOCK_DATA.md",
    ]

    for name in mock_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "mock-data" / name).is_file()
        assert f"mock-data/{name}" in guides_index
        assert f"mock-data/{name}" in cleanup_index_root

    assert "docs/guides/mock-data/MOCK_DATA_USAGE_RULES.md" in guides_claude
    assert "docs/guides/mock-data/MOCK_REAL_DATA_SWITCHING_GUIDE.md" in guides_claude
    assert "docs/guides/mock-data/MOCK_DATA_USAGE_RULES.md" in overview_claude
    assert "docs/guides/mock-data/MOCK_DATA_USAGE_RULES.md" in iflow_root
    assert "docs/guides/mock-data/MOCK_DATA_USAGE_RULES.md" in iflow_docs
    assert "docs/guides/mock-data/MOCK_REAL_DATA_SWITCHING_GUIDE.md" in knowledge_base
    assert "../../guides/mock-data/MOCK_REAL_DATA_SWITCHING_GUIDE.md" in frontend_env_switch
    assert "../../guides/mock-data/MOCK_DATA_USAGE_RULES.md" in frontend_env_switch
    assert "../guides/mock-data/MOCK_REAL_DATA_SWITCHING_GUIDE.md" in env_switch_report
    assert "../guides/mock-data/MOCK_DATA_USAGE_RULES.md" in env_switch_report
    assert "docs/guides/mock-data/MOCK_DATA_USAGE_RULES.md" in migration_analysis
    assert "docs/guides/mock-data/MOCK_REAL_DATA_INDEX.md" in cleanup_completion
    assert "docs/guides/mock-data/MOCK_REAL_DATA_SWITCHING_GUIDE.md" in cleanup_completion
    assert "docs/guides/mock-data/REAL_DATA_INTEGRATION_PRINCIPLES.md" in cleanup_completion
    assert "docs/guides/mock-data/REAL_DATA_INTEGRATION_PRINCIPLES.md" in cleanup_plan
    assert "docs/guides/mock-data/REAL_DATA_INTEGRATION_ROADMAP.md" in cleanup_plan
    assert "docs/guides/mock-data/PHASE_2_REAL_DATA_INTEGRATION_PLAN.md" in phase2_review
    assert "docs/guides/mock-data/REAL_DATA_INTEGRATION_PRINCIPLES.md" in mock_real_index_doc
    assert "./REAL_DATA_INTEGRATION_PRINCIPLES.md" in mock_real_index_doc
    assert "MOCK_DATA_USAGE_RULES" in mock_index
    assert "MOCK_REAL_DATA_INDEX" in mock_index
    assert "MOCK_REAL_DATA_SWITCHING_GUIDE" in mock_index
    assert "PHASE_2_REAL_DATA_INTEGRATION_PLAN" in mock_index
    assert "REAL_DATA_INTEGRATION_PRINCIPLES" in mock_index
    assert "REAL_DATA_INTEGRATION_ROADMAP" in mock_index
    assert "README_MOCK_DATA" in mock_index


def test_pm2_guides_are_converged_under_guides_pm2_family() -> None:
    testing_guide = (PROJECT_ROOT / "docs" / "testing" / "TESTING_GUIDE.md").read_text(encoding="utf-8")
    web_e2e_quick_ref = (PROJECT_ROOT / "docs" / "testing" / "WEB_E2E_TEST_QUICK_REFERENCE.md").read_text(
        encoding="utf-8"
    )
    web_e2e_quick_ref_v2 = (
        PROJECT_ROOT / "docs" / "testing" / "WEB_E2E_TEST_QUICK_REFERENCE_V2.md"
    ).read_text(encoding="utf-8")
    frontend_runner = (
        PROJECT_ROOT / "web" / "frontend" / "scripts" / "test-runner" / "run-quick-e2e.sh"
    ).read_text(encoding="utf-8")
    frontend_deploy = (PROJECT_ROOT / "web" / "frontend" / "deploy-and-test.sh").read_text(encoding="utf-8")
    optimization_report = (
        PROJECT_ROOT / "docs" / "reports" / "E2E_TESTING_OPTIMIZATION_IMPLEMENTATION_REPORT.md"
    ).read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    pm2_index = (PROJECT_ROOT / "docs" / "guides" / "pm2" / "INDEX.md").read_text(
        encoding="utf-8"
    ) if (PROJECT_ROOT / "docs" / "guides" / "pm2" / "INDEX.md").exists() else ""

    pm2_docs = [
        "PM2_PLAYWRIGHT_TESTING_GUIDE.md",
        "PM2_PLAYWRIGHT_TESTING_GUIDE_REVIEW.md",
        "PM2_QUICK_START_GUIDE.md",
        "PM2_TMUX_LNV_COLLABORATION_GUIDE.md",
    ]

    for name in pm2_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "pm2" / name).is_file()
        assert f"pm2/{name}" in guides_index
        assert f"pm2/{name}" in cleanup_index_root

    assert "docs/guides/pm2/PM2_PLAYWRIGHT_TESTING_GUIDE.md" in testing_guide
    assert "docs/guides/pm2/PM2_PLAYWRIGHT_TESTING_GUIDE.md" in web_e2e_quick_ref
    assert "docs/guides/pm2/PM2_PLAYWRIGHT_TESTING_GUIDE.md" in web_e2e_quick_ref_v2
    assert "docs/guides/pm2/PM2_PLAYWRIGHT_TESTING_GUIDE.md" in frontend_runner
    assert "docs/guides/pm2/PM2_PLAYWRIGHT_TESTING_GUIDE.md" in frontend_deploy
    assert "docs/guides/pm2/PM2_PLAYWRIGHT_TESTING_GUIDE.md" in optimization_report
    assert "docs/guides/pm2/PM2_PLAYWRIGHT_TESTING_GUIDE_REVIEW.md" in optimization_report
    assert "PM2_PLAYWRIGHT_TESTING_GUIDE" in pm2_index
    assert "PM2_PLAYWRIGHT_TESTING_GUIDE_REVIEW" in pm2_index
    assert "PM2_QUICK_START_GUIDE" in pm2_index
    assert "PM2_TMUX_LNV_COLLABORATION_GUIDE" in pm2_index


def test_cicd_guides_are_converged_under_operations_ci_cd_family() -> None:
    visual_regression_plan = (
        PROJECT_ROOT / "docs" / "testing" / "VISUAL_REGRESSION_TEST_PLAN.md"
    ).read_text(encoding="utf-8")
    typescript_inventory = (
        PROJECT_ROOT / "docs" / "reports" / "Typescript文档整理_完整清单_2026-01-20.md"
    ).read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    reports_cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    operations_readme = (PROJECT_ROOT / "docs" / "operations" / "README.md").read_text(encoding="utf-8")

    cicd_docs = [
        "CICD_CONTINUOUS_OPTIMIZATION.md",
        "CICD_TYPE_CHECK_INTEGRATION_GUIDE.md",
        "CICD_TYPE_CHECK_QUICK_REFERENCE.md",
    ]

    for name in cicd_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "operations" / "ci-cd" / name).is_file()
        assert f"ci-cd/{name}" in reports_cleanup_index_root or f"operations/ci-cd/{name}" in reports_cleanup_index_root

    assert "docs/operations/ci-cd/CICD_CONTINUOUS_OPTIMIZATION.md" in visual_regression_plan
    assert "docs/operations/ci-cd/CICD_TYPE_CHECK_INTEGRATION_GUIDE.md" in typescript_inventory
    assert "docs/operations/ci-cd/CICD_TYPE_CHECK_QUICK_REFERENCE.md" in typescript_inventory
    assert "CICD_CONTINUOUS_OPTIMIZATION" not in guides_index
    assert "CICD_TYPE_CHECK_INTEGRATION_GUIDE" not in guides_index
    assert "CICD_TYPE_CHECK_QUICK_REFERENCE" not in guides_index
    assert "ci-cd/CICD_CONTINUOUS_OPTIMIZATION.md" in operations_readme or "CICD_CONTINUOUS_OPTIMIZATION.md" in operations_readme


def test_testing_specialized_guides_are_converged_under_docs_testing_family() -> None:
    testing_readme = (PROJECT_ROOT / "docs" / "testing" / "README.md").read_text(encoding="utf-8")
    testing_index = (PROJECT_ROOT / "docs" / "testing" / "INDEX.md").read_text(encoding="utf-8")
    developer_guide = (PROJECT_ROOT / "docs" / "guides" / "onboarding" / "DEVELOPER_GUIDE.md").read_text(
        encoding="utf-8"
    )
    testing_guide = (PROJECT_ROOT / "docs" / "testing" / "TESTING_GUIDE.md").read_text(encoding="utf-8")
    compatibility_ref = (
        PROJECT_ROOT / "docs" / "testing" / "E2E_TEST_QUICK_REFERENCE_COMPATIBILITY.md"
    ).read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    testing_docs = [
        "TESTING_GUIDE.md",
        "TESTING_EXAMPLES.md",
        "E2E_TEST_DEBUG_METHODS.md",
        "E2E_TEST_QUICK_REFERENCE_COMPATIBILITY.md",
        "WEB_E2E_TEST_QUICK_REFERENCE.md",
        "WEB_E2E_TEST_QUICK_REFERENCE_V2.md",
        "VISUAL_REGRESSION_TEST_PLAN.md",
    ]

    for name in testing_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "testing" / name).is_file()
        assert f"- 📄 [{name.removesuffix('.md')}]({name})" not in guides_index
        assert f"testing/{name}" in cleanup_index_root or f"docs/testing/{name}" in cleanup_index_root

    assert "/opt/claude/mystocks_spec/docs/testing/README.md" in testing_index
    assert "/opt/claude/mystocks_spec/docs/testing/E2E_TEST_GUIDE.md" in testing_index
    assert "/opt/claude/mystocks_spec/docs/testing/E2E_TEST_DEBUG_METHODS.md" in testing_index
    assert "/opt/claude/mystocks_spec/docs/testing/TEST_ENVIRONMENT_REQUIREMENTS.md" in testing_index
    assert "/opt/claude/mystocks_spec/docs/testing/常见测试问题与解决方案.md" in testing_index
    assert "TESTING_GUIDE.md" not in testing_index
    assert "TESTING_EXAMPLES.md" not in testing_index
    assert "E2E_TEST_QUICK_REFERENCE_COMPATIBILITY.md" not in testing_index

    assert "/opt/claude/mystocks_spec/docs/testing/TESTING_GUIDE.md" in testing_readme
    assert "/opt/claude/mystocks_spec/docs/testing/TESTING_EXAMPLES.md" in testing_readme
    assert "/opt/claude/mystocks_spec/docs/testing/E2E_TEST_DEBUG_METHODS.md" in testing_readme
    assert "/opt/claude/mystocks_spec/docs/testing/E2E_TEST_QUICK_REFERENCE_COMPATIBILITY.md" in testing_readme
    assert "docs/testing/TESTING_GUIDE.md" in developer_guide
    assert "docs/testing/TESTING_EXAMPLES.md" in developer_guide
    assert "docs/testing/WEB_E2E_TEST_QUICK_REFERENCE_V2.md" in testing_guide
    assert "docs/testing/WEB_E2E_TEST_QUICK_REFERENCE.md" in testing_guide
    assert "docs/testing/TESTING_GUIDE.md" in compatibility_ref
    assert "docs/testing/TESTING_EXAMPLES.md" in compatibility_ref
    assert "docs/testing/WEB_E2E_TEST_QUICK_REFERENCE_V2.md" in compatibility_ref


def test_phase6_methodology_guide_is_converged_under_docs_testing_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    testing_index = (PROJECT_ROOT / "docs" / "testing" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    name = "PHASE_6_METHODOLOGY_GUIDE.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "testing" / name).is_file()
    assert name.removesuffix(".md") not in guides_index
    assert name.removesuffix(".md") in testing_index
    assert f"testing/{name}" in cleanup_index_root


def test_web_testing_methodology_doc_is_converged_under_docs_testing_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    testing_index = (PROJECT_ROOT / "docs" / "testing" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    name = "web测试方法论.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "testing" / name).is_file()
    assert name.removesuffix(".md") not in guides_index
    assert name.removesuffix(".md") in testing_index
    assert f"testing/{name}" in cleanup_index_root


def test_additional_cicd_guides_are_converged_under_operations_ci_cd_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    operations_readme = (PROJECT_ROOT / "docs" / "operations" / "README.md").read_text(encoding="utf-8")
    operations_index = (PROJECT_ROOT / "docs" / "operations" / "INDEX.md").read_text(encoding="utf-8")
    cicd_index = (PROJECT_ROOT / "docs" / "operations" / "ci-cd" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    cicd_docs = [
        "LOCAL_CI_INTEGRATION.md",
        "MYSTOCKS_CI_CD_DAILY_APPLICATION.md",
        "QUALITY_GATE_MANAGEMENT.md",
    ]

    for name in cicd_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "operations" / "ci-cd" / name).is_file()
        assert name.removesuffix(".md") not in guides_index
        assert f"ci-cd/{name}" in operations_index
        assert name.removesuffix(".md") in cicd_index
        assert f"ci-cd/{name}" in operations_readme
        assert f"operations/ci-cd/{name}" in cleanup_index_root or f"ci-cd/{name}" in cleanup_index_root


def test_cicd_optimization_system_is_converged_under_operations_ci_cd_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    operations_index = (PROJECT_ROOT / "docs" / "operations" / "INDEX.md").read_text(encoding="utf-8")
    cicd_index = (PROJECT_ROOT / "docs" / "operations" / "ci-cd" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    type_checking_integration = (
        PROJECT_ROOT / "docs" / "guides" / "typescript" / "TYPE_CHECKING_INTEGRATION.md"
    ).read_text(encoding="utf-8")
    monitoring_overview = (
        PROJECT_ROOT / "docs" / "operations" / "MYSTOCKS_MONITORING_SYSTEM_OVERVIEW.md"
    ).read_text(encoding="utf-8")
    canonical_cicd_doc = (
        PROJECT_ROOT / "docs" / "operations" / "ci-cd" / "MYSTOCKS_CI_CD_OPTIMIZATION_SYSTEM.md"
    ).read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "guides" / "MYSTOCKS_CI_CD_OPTIMIZATION_SYSTEM.md").exists()
    assert (PROJECT_ROOT / "docs" / "operations" / "ci-cd" / "MYSTOCKS_CI_CD_OPTIMIZATION_SYSTEM.md").is_file()

    assert "MYSTOCKS_CI_CD_OPTIMIZATION_SYSTEM" not in guides_index
    assert "ci-cd/MYSTOCKS_CI_CD_OPTIMIZATION_SYSTEM.md" in operations_index
    assert "MYSTOCKS_CI_CD_OPTIMIZATION_SYSTEM" in cicd_index
    assert "operations/ci-cd/MYSTOCKS_CI_CD_OPTIMIZATION_SYSTEM.md" in cleanup_index_root or (
        "ci-cd/MYSTOCKS_CI_CD_OPTIMIZATION_SYSTEM.md" in cleanup_index_root
    )
    assert "../../operations/ci-cd/MYSTOCKS_CI_CD_OPTIMIZATION_SYSTEM.md" in type_checking_integration
    assert "docs/operations/ci-cd/MYSTOCKS_CI_CD_OPTIMIZATION_SYSTEM.md" in monitoring_overview
    assert "## 📋 实施计划" in canonical_cicd_doc
    assert "## 🎯 成功指标" in canonical_cicd_doc


def test_python_quality_guides_are_converged_under_operations_ci_cd_family() -> None:
    guides_claude = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "CLAUDE.md").read_text(encoding="utf-8")
    guides_gemini = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "GEMINI.md").read_text(encoding="utf-8")
    reports_gemini = (PROJECT_ROOT / "docs" / "reports" / "misc" / "GEMINI.md").read_text(encoding="utf-8")
    quality_summary = (
        PROJECT_ROOT / "docs" / "reports" / "code_quality" / "PYTHON_QUALITY_TOOLS_IMPLEMENTATION_SUMMARY.md"
    ).read_text(encoding="utf-8")
    worklog = (
        PROJECT_ROOT / "docs" / "reports" / "worklogs" / "MULTI_CLI_MAIN_CLI_LESSONS_LEARNED.md"
    ).read_text(encoding="utf-8")
    knowledge_base = (PROJECT_ROOT / "scripts" / "cli" / "SHARED" / "KNOWLEDGE_BASE.md").read_text(
        encoding="utf-8"
    )
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    operations_readme = (PROJECT_ROOT / "docs" / "operations" / "README.md").read_text(encoding="utf-8")
    operations_index = (PROJECT_ROOT / "docs" / "operations" / "INDEX.md").read_text(encoding="utf-8")
    cicd_index = (PROJECT_ROOT / "docs" / "operations" / "ci-cd" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    docs = [
        "PYTHON_QUALITY_ASSURANCE_WORKFLOW.md",
        "PYTHON_QUALITY_TOOLS_QUICK_REFERENCE.md",
    ]

    for name in docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "operations" / "ci-cd" / name).is_file()
        assert name.removesuffix(".md") not in guides_index
        assert f"ci-cd/{name}" in operations_index
        assert name.removesuffix(".md") in cicd_index
        assert f"ci-cd/{name}" in operations_readme
        assert f"operations/ci-cd/{name}" in cleanup_index_root or f"ci-cd/{name}" in cleanup_index_root

    assert "./docs/operations/ci-cd/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md" in guides_claude
    assert "./docs/operations/ci-cd/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md" in guides_claude
    assert "./docs/operations/ci-cd/PYTHON_QUALITY_TOOLS_QUICK_REFERENCE.md" in guides_claude
    assert "docs/operations/ci-cd/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md" in guides_gemini
    assert "docs/operations/ci-cd/PYTHON_QUALITY_TOOLS_QUICK_REFERENCE.md" in guides_gemini
    assert "docs/operations/ci-cd/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md" in reports_gemini
    assert "docs/operations/ci-cd/PYTHON_QUALITY_TOOLS_QUICK_REFERENCE.md" in reports_gemini
    assert "docs/operations/ci-cd/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md" in quality_summary
    assert "docs/operations/ci-cd/PYTHON_QUALITY_TOOLS_QUICK_REFERENCE.md" in quality_summary
    assert "../../operations/ci-cd/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md" in worklog
    assert "../../operations/ci-cd/PYTHON_QUALITY_TOOLS_QUICK_REFERENCE.md" in worklog
    assert "docs/operations/ci-cd/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md" in knowledge_base


def test_operational_guides_are_converged_under_docs_operations_families() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    operations_readme = (PROJECT_ROOT / "docs" / "operations" / "README.md").read_text(encoding="utf-8")
    operations_index = (PROJECT_ROOT / "docs" / "operations" / "INDEX.md").read_text(encoding="utf-8")
    deployment_index = (
        PROJECT_ROOT / "docs" / "operations" / "deployment" / "INDEX.md"
    ).read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    user_guide = (PROJECT_ROOT / "docs" / "guides" / "onboarding" / "USER_GUIDE.md").read_text(
        encoding="utf-8"
    )
    config_splitting = (PROJECT_ROOT / "docs" / "architecture" / "CONFIG_SPLITTING_GUIDE.md").read_text(
        encoding="utf-8"
    )
    stocks_spec_guide = (PROJECT_ROOT / "docs" / "operations" / "STOCKS_SPEC_COMMAND_GUIDE.md").read_text(
        encoding="utf-8"
    )
    phase6_completion = (PROJECT_ROOT / "docs" / "reports" / "PHASE6_COMPLETION_REPORT.md").read_text(
        encoding="utf-8"
    )
    phase6_final = (PROJECT_ROOT / "docs" / "reports" / "PHASE6_FINAL_COMPLETION_REPORT.md").read_text(
        encoding="utf-8"
    )
    phase6_status_t4 = (PROJECT_ROOT / "docs" / "reports" / "PHASE6_CLI_STATUS_T4H.md").read_text(
        encoding="utf-8"
    )
    phase6_status_t25 = (PROJECT_ROOT / "docs" / "reports" / "PHASE6_CLI_STATUS_T2.5H.md").read_text(
        encoding="utf-8"
    )
    technical_debt_guide = (
        PROJECT_ROOT / "docs" / "guides" / "governance" / "TECHNICAL_DEBT_MANAGEMENT.md"
    ).read_text(encoding="utf-8")
    deployment_guide = (
        PROJECT_ROOT / "docs" / "operations" / "deployment" / "DEPLOYMENT.md"
    ).read_text(encoding="utf-8")

    root_ops_docs = [
        "BACKUP_GUIDE.md",
        "INFRASTRUCTURE_CHECKLIST.md",
        "PHASE6_SERVER_RECOVERY_TEST_PROCEDURE.md",
        "quick-start.md",
        "STOCKS_SPEC_COMMAND_GUIDE.md",
        "TROUBLESHOOTING.md",
        "TROUBLESHOOTING_QUICK_REFERENCE.md",
    ]
    deployment_docs = [
        "DEPLOYMENT.md",
        "PORT_CONFIGURATION.md",
    ]

    for name in root_ops_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "operations" / name).is_file()
        assert f"- 📄 [{name.removesuffix('.md')}]({name})" not in guides_index
        assert f"operations/{name}" in cleanup_index_root

    for name in deployment_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "operations" / "deployment" / name).is_file()
        assert f"- 📄 [{name.removesuffix('.md')}]({name})" not in guides_index
        assert name.removesuffix(".md") in deployment_index
        assert f"operations/deployment/{name}" in cleanup_index_root or f"deployment/{name}" in cleanup_index_root

    assert "/opt/claude/mystocks_spec/docs/operations/README.md" in operations_index
    assert "/opt/claude/mystocks_spec/docs/operations/OPS_MANUAL.md" in operations_index
    assert "/opt/claude/mystocks_spec/docs/operations/PRODUCTION_INFO.md" in operations_index
    assert "/opt/claude/mystocks_spec/docs/operations/TROUBLESHOOTING.md" in operations_index
    assert "/opt/claude/mystocks_spec/docs/operations/deployment-guide.md" in operations_index
    assert "/opt/claude/mystocks_spec/docs/operations/quick-start.md" in operations_index
    assert "BACKUP_GUIDE.md" not in operations_index
    assert "INFRASTRUCTURE_CHECKLIST.md" not in operations_index
    assert "PHASE6_SERVER_RECOVERY_TEST_PROCEDURE.md" not in operations_index
    assert "STOCKS_SPEC_COMMAND_GUIDE.md" not in operations_index
    assert "TROUBLESHOOTING_QUICK_REFERENCE.md" not in operations_index

    assert "/opt/claude/mystocks_spec/docs/operations/BACKUP_GUIDE.md" in operations_readme
    assert "/opt/claude/mystocks_spec/docs/operations/INFRASTRUCTURE_CHECKLIST.md" in operations_readme
    assert "/opt/claude/mystocks_spec/docs/operations/STOCKS_SPEC_COMMAND_GUIDE.md" in operations_readme

    assert "../operations/deployment/DEPLOYMENT.md" in user_guide
    assert "../operations/INFRASTRUCTURE_CHECKLIST.md" in config_splitting
    assert "../operations/TROUBLESHOOTING.md" in user_guide
    assert "../operations/TROUBLESHOOTING.md" in config_splitting
    assert "../operations/TROUBLESHOOTING.md" in technical_debt_guide
    assert "../TROUBLESHOOTING.md" in deployment_guide
    assert "/opt/claude/mystocks_spec/docs/operations/deployment/PORT_CONFIGURATION.md" in stocks_spec_guide
    assert "docs/operations/PHASE6_SERVER_RECOVERY_TEST_PROCEDURE.md" in phase6_completion
    assert "docs/operations/TROUBLESHOOTING.md" in phase6_final
    assert "docs/operations/TROUBLESHOOTING.md" in phase6_status_t4
    assert "docs/operations/TROUBLESHOOTING.md" in phase6_status_t25


def test_quick_start_guide_is_converged_under_docs_operations_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    operations_index = (PROJECT_ROOT / "docs" / "operations" / "INDEX.md").read_text(encoding="utf-8")
    operations_readme = (PROJECT_ROOT / "docs" / "operations" / "README.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    migration_script = (
        PROJECT_ROOT / "scripts" / "dev" / "tools" / "migrate_docs_structure.py"
    ).read_text(encoding="utf-8")

    name = "quick-start.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "operations" / name).is_file()
    assert name.removesuffix(".md") not in guides_index
    assert name.removesuffix(".md") in operations_index
    assert f"operations/{name}" in cleanup_index_root or name in operations_readme
    assert "/opt/claude/mystocks_spec/docs/operations/quick-start.md" in operations_readme
    assert '\"QUICK_START.md\": \"operations/quick-start.md\"' in migration_script


def test_monitoring_guides_are_converged_under_operations_monitoring_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    operations_readme = (PROJECT_ROOT / "docs" / "operations" / "README.md").read_text(encoding="utf-8")
    operations_index = (PROJECT_ROOT / "docs" / "operations" / "INDEX.md").read_text(encoding="utf-8")
    monitoring_index = (
        PROJECT_ROOT / "docs" / "operations" / "monitoring" / "INDEX.md"
    ).read_text(encoding="utf-8")
    monitoring_overview = (
        PROJECT_ROOT / "docs" / "operations" / "MYSTOCKS_MONITORING_SYSTEM_OVERVIEW.md"
    ).read_text(encoding="utf-8")
    async_completion = (
        PROJECT_ROOT / "docs" / "reports" / "P0_TASK1_ASYNC_MONITORING_COMPLETION.md"
    ).read_text(encoding="utf-8")
    signal_phase2 = (
        PROJECT_ROOT / "docs" / "reports" / "SIGNAL_MONITORING_PHASE2_COMPLETION_REPORT.md"
    ).read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    monitoring_docs = [
        "ASYNC_MONITORING_GUIDE.md",
        "MYSTOCKS_MONITORING_OPTIMIZATION_DEPLOYMENT.md",
        "SIGNAL_MONITORING_METRICS_DESIGN.md",
        "TMUX_LNAV_ADAPTER_MONITORING.md",
        "告警规则设置方法.md",
    ]

    for name in monitoring_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "operations" / "monitoring" / name).is_file()
        assert name.removesuffix(".md") not in guides_index
        assert f"monitoring/{name}" in operations_index
        assert name.removesuffix(".md") in monitoring_index
        assert f"monitoring/{name}" in operations_readme
        assert f"operations/monitoring/{name}" in cleanup_index_root or f"monitoring/{name}" in cleanup_index_root

    assert "docs/operations/monitoring/MYSTOCKS_MONITORING_OPTIMIZATION_DEPLOYMENT.md" in monitoring_overview
    assert "docs/operations/monitoring/ASYNC_MONITORING_GUIDE.md" in async_completion
    assert "docs/operations/monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md" in signal_phase2


def test_data_source_guides_are_converged_under_guides_data_source_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    data_source_index = (
        PROJECT_ROOT / "docs" / "guides" / "data-source" / "INDEX.md"
    ).read_text(encoding="utf-8")
    readme_root = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    guides_readme = (PROJECT_ROOT / "docs" / "guides" / "README.md").read_text(encoding="utf-8")
    guides_claude = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "CLAUDE.md").read_text(encoding="utf-8")
    architecture_guide = (
        PROJECT_ROOT / "docs" / "architecture" / "STOCK_INDICATOR_CALCULATION_SYSTEM.md"
    ).read_text(encoding="utf-8")
    api_readme = (PROJECT_ROOT / "docs" / "api" / "README.md").read_text(encoding="utf-8")
    quant_api_spec = (
        PROJECT_ROOT / "docs" / "api" / "QUANTITATIVE_TRADING_ALGORITHMS_API_SPEC.md"
    ).read_text(encoding="utf-8")
    verify_data_source = (PROJECT_ROOT / "scripts" / "verify_data_source_integration.sh").read_text(
        encoding="utf-8"
    )
    api_source_report = (
        PROJECT_ROOT / "docs" / "reports" / "API_SOURCE_INTEGRATION_GUIDE_ENHANCEMENT_REPORT.md"
    ).read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    data_source_docs = [
        "DATA_CLEANING_QUICK_START.md",
        "NEW_API_SOURCE_INTEGRATION_GUIDE.md",
        "DATA_SOURCE_ENDPOINT_REGISTRATION_GUIDE.md",
        "DATA_SOURCE_EXPANSION_STRATEGY.md",
        "DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md",
        "DATA_SOURCE_MONITORING_GUIDE.md",
        "DATA_SOURCE_OPTIMIZATION_DEPLOYMENT_CHECKLIST.md",
        "DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md",
        "DATA_SOURCE_TOOLS_QUICK_REFERENCE.md",
    ]

    for name in data_source_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "data-source" / name).is_file()
        assert f"data-source/{name}" in guides_index
        assert f"data-source/{name}" in cleanup_index_root
        assert name.removesuffix(".md") in data_source_index

    assert "./docs/guides/data-source/DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md" in readme_root
    assert "./docs/guides/data-source/DATA_SOURCE_TOOLS_QUICK_REFERENCE.md" in readme_root
    assert "./data-source/DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md" in guides_readme
    assert "./data-source/DATA_SOURCE_TOOLS_QUICK_REFERENCE.md" in guides_readme
    assert "./docs/guides/data-source/DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md" in guides_claude
    assert "./docs/guides/data-source/DATA_SOURCE_TOOLS_QUICK_REFERENCE.md" in guides_claude
    assert "./docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md" in guides_claude
    assert "../guides/data-source/DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md" in architecture_guide
    assert "docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md" in api_readme
    assert "docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md" in quant_api_spec
    assert "docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md" in verify_data_source
    assert "docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md" in api_source_report


def test_refactoring_and_index_analysis_docs_are_converged_under_reports_analysis() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    reports_index = (PROJECT_ROOT / "docs" / "reports" / "INDEX.md").read_text(encoding="utf-8")
    analysis_index = (PROJECT_ROOT / "docs" / "reports" / "analysis" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    analysis_docs = [
        "database_indexes_report.md",
        "database_service_refactoring_analysis.md",
        "financial_adapter_method_analysis.md",
        "tdx_adapter_refactoring_analysis.md",
    ]

    for name in analysis_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "reports" / "analysis" / name).is_file()
        assert name.removesuffix(".md") not in guides_index
        assert f"analysis/{name}" in reports_index
        assert name.removesuffix(".md") in analysis_index
        assert f"analysis/{name}" in cleanup_index_root


def test_documentation_process_guides_are_converged_under_guides_documentation_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    documentation_index = (
        PROJECT_ROOT / "docs" / "guides" / "documentation" / "INDEX.md"
    ).read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    guides_claude = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "CLAUDE.md").read_text(encoding="utf-8")
    hygiene_plan = (
        PROJECT_ROOT / "docs" / "plans" / "2026-03-09-repository-hygiene-governance-implementation-plan.md"
    ).read_text(encoding="utf-8")
    refactoring_plan = (PROJECT_ROOT / "docs" / "plans" / "code_refactoring_plan.md").read_text(encoding="utf-8")

    documentation_docs = [
        "DOCUMENTATION_WORKFLOW_GUIDE.md",
        "文档管理指南.md",
        "文档结构说明.md",
        "文件目录管理方案.md",
        "文件目录整理方法论指南.md",
        "超长文档拆分办法.md",
    ]

    for name in documentation_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "documentation" / name).is_file()
        assert name.removesuffix(".md") in documentation_index
        assert f"guides/documentation/{name}" in cleanup_index_root

    assert "[`documentation/`]" in guides_index
    assert "docs/guides/documentation/DOCUMENTATION_WORKFLOW_GUIDE.md" in guides_claude
    assert "docs/guides/documentation/DOCUMENTATION_WORKFLOW_GUIDE.md" in hygiene_plan
    assert "/opt/claude/mystocks_spec/docs/guides/documentation/超长文档拆分办法.md" in refactoring_plan


def test_initialization_prompt_is_converged_under_guides_templates_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    templates_index = (PROJECT_ROOT / "docs" / "guides" / "templates" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    migration_script = (
        PROJECT_ROOT / "scripts" / "dev" / "tools" / "migrate_docs_structure.py"
    ).read_text(encoding="utf-8")

    name = "INITIALIZATION_PROMPT.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "guides" / "templates" / name).is_file()
    assert f"templates/{name}" in guides_index
    assert name.removesuffix(".md") in templates_index
    assert f"guides/templates/{name}" in cleanup_index_root
    assert '\"INITIALIZATION_PROMPT.md\": \"guides/templates/INITIALIZATION_PROMPT.md\"' in migration_script


def test_technical_debt_governance_charter_is_converged_under_docs_standards_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    standards_index = (PROJECT_ROOT / "docs" / "standards" / "INDEX.md").read_text(encoding="utf-8")
    docs_index = (PROJECT_ROOT / "docs" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    root_claude = (PROJECT_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    root_agents = (PROJECT_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    main_worklog = (
        PROJECT_ROOT / "docs" / "reports" / "worklogs" / "MULTI_CLI_MAIN_CLI_LESSONS_LEARNED.md"
    ).read_text(encoding="utf-8")
    auto_worklog = (
        PROJECT_ROOT / "docs" / "reports" / "worklogs" / "claude-auto" / "2026-03-08.md"
    ).read_text(encoding="utf-8")
    task_report = (PROJECT_ROOT / "TASK-REPORT.md").read_text(encoding="utf-8")

    name = "technical-debt-governance-charter-v1.md"

    assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
    assert (PROJECT_ROOT / "docs" / "standards" / name).is_file()
    assert name.removesuffix(".md") not in guides_index
    assert f"standards/{name}" in docs_index
    assert name.removesuffix(".md") in standards_index
    assert f"standards/{name}" in cleanup_index_root
    assert "docs/standards/technical-debt-governance-charter-v1.md" in root_claude
    assert "docs/standards/technical-debt-governance-charter-v1.md" in root_agents
    assert "docs/standards/technical-debt-governance-charter-v1.md" in main_worklog
    assert "docs/standards/technical-debt-governance-charter-v1.md" in auto_worklog
    assert "docs/standards/technical-debt-governance-charter-v1.md" in task_report


def test_data_interface_guides_are_converged_under_guides_data_interface_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    data_interface_index = (
        PROJECT_ROOT / "docs" / "guides" / "data-interface" / "INDEX.md"
    ).read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    unified_analysis_script = (
        PROJECT_ROOT / "scripts" / "dev" / "analysis" / "unified_interface_analysis.py"
    ).read_text(encoding="utf-8")
    api_usage_quick_script = (
        PROJECT_ROOT / "scripts" / "dev" / "analyze_api_data_usage_quick.sh"
    ).read_text(encoding="utf-8")
    unified_analysis_report = (
        PROJECT_ROOT / "docs" / "reports" / "unified_interface_analysis.json"
    ).read_text(encoding="utf-8")

    docs = [
        "DATA_INTERFACE_SCANNER_GUIDE.md",
        "UNIFIED_INTERFACE_GUIDE.md",
        "analyze_api_data_usage_README.md",
    ]

    for name in docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "data-interface" / name).is_file()
        assert f"data-interface/{name}" in guides_index
        assert name.removesuffix(".md") in data_interface_index

    assert "guides/data-interface/DATA_INTERFACE_SCANNER_GUIDE.md" in cleanup_index_root
    assert "guides/data-interface/UNIFIED_INTERFACE_GUIDE.md" in cleanup_index_root
    assert "docs/guides/data-interface/UNIFIED_INTERFACE_GUIDE.md" in unified_analysis_script
    assert "docs/guides/data-interface/UNIFIED_INTERFACE_GUIDE.md" in unified_analysis_report
    assert "docs/guides/data-interface/analyze_api_data_usage_README.md" in api_usage_quick_script


def test_quant_trading_guides_are_converged_under_guides_quant_trading_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    quant_index = (PROJECT_ROOT / "docs" / "guides" / "quant-trading" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    algorithm_usage = (
        PROJECT_ROOT / "docs" / "guides" / "quant-trading" / "algorithm_system_usage_guide.md"
    ).read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    quant_docs = [
        "advanced_algorithms_usage_guide.md",
        "algorithm_system_usage_guide.md",
        "neural_algorithms_usage_guide.md",
        "quantitative_trading_implementation.md",
        "risk_management_system_plan.md",
    ]

    for name in quant_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "quant-trading" / name).is_file()
        assert f"quant-trading/{name}" in guides_index
        assert f"quant-trading/{name}" in cleanup_index_root
        assert name.removesuffix(".md") in quant_index

    assert "./algorithm_system_usage_guide.md" in algorithm_usage


def test_security_guides_are_converged_under_standards_security_family() -> None:
    phase1_summary = (PROJECT_ROOT / "scripts" / "tests" / "phase1_completion_summary.py").read_text(
        encoding="utf-8"
    )
    phase0_rotation = (
        PROJECT_ROOT / "docs" / "standards" / "PHASE0_CREDENTIAL_ROTATION_GUIDE.md"
    ).read_text(encoding="utf-8")
    local_env_setup = (PROJECT_ROOT / "docs" / "standards" / "LOCAL_ENV_SETUP.md").read_text(encoding="utf-8")
    security_fix_summary = (PROJECT_ROOT / "docs" / "reports" / "SECURITY_FIX_SUMMARY.md").read_text(
        encoding="utf-8"
    )
    hardcoded_scan_report = (
        PROJECT_ROOT / "docs" / "reports" / "SECURITY_HARDcoded_PASSWORD_SCAN_REPORT.md"
    ).read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    standards_security_index = (
        PROJECT_ROOT / "docs" / "standards" / "security" / "INDEX.md"
    ).read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    security_docs = [
        "HARDCODING_GOVERNANCE_TIERING_GUIDE.md",
        "SECURE_CODING_QUICK_REFERENCE.md",
        "SECURITY_CI_CD_INTEGRATION.md",
        "SECURITY_CODING_STANDARDS.md",
        "SECURITY_TESTING_GUIDELINES.md",
    ]

    for name in security_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "standards" / "security" / name).is_file()
        assert f"security/{name}" in cleanup_index_root or f"standards/security/{name}" in cleanup_index_root

    assert "docs/standards/security/SECURITY_TESTING_GUIDELINES.md" in phase1_summary
    assert "docs/standards/security/SECURITY_CODING_STANDARDS.md" in phase1_summary
    assert "docs/standards/security/SECURITY_CI_CD_INTEGRATION.md" in phase1_summary
    assert "docs/standards/security/HARDCODING_GOVERNANCE_TIERING_GUIDE.md" in phase0_rotation
    assert "./security/HARDCODING_GOVERNANCE_TIERING_GUIDE.md" in local_env_setup
    assert "docs/standards/security/SECURE_CODING_QUICK_REFERENCE.md" in security_fix_summary
    assert "docs/standards/security/SECURE_CODING_QUICK_REFERENCE.md" in hardcoded_scan_report
    assert "HARDCODING_GOVERNANCE_TIERING_GUIDE" not in guides_index
    assert "SECURE_CODING_QUICK_REFERENCE" not in guides_index
    assert "SECURITY_CI_CD_INTEGRATION" not in guides_index
    assert "SECURITY_CODING_STANDARDS" not in guides_index
    assert "SECURITY_TESTING_GUIDELINES" not in guides_index
    assert "HARDCODING_GOVERNANCE_TIERING_GUIDE" in standards_security_index
    assert "SECURE_CODING_QUICK_REFERENCE" in standards_security_index
    assert "SECURITY_CI_CD_INTEGRATION" in standards_security_index
    assert "SECURITY_CODING_STANDARDS" in standards_security_index
    assert "SECURITY_TESTING_GUIDELINES" in standards_security_index


def test_frontend_topic_guides_are_converged_under_guides_frontend_family() -> None:
    root_claude = (PROJECT_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    agents_md = (PROJECT_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    frontend_status_report = (
        PROJECT_ROOT / "docs" / "reports" / "frontend-optimization-implementation-status-2026-01-27.md"
    ).read_text(encoding="utf-8")
    page_config_guide = (PROJECT_ROOT / "docs" / "architecture" / "PAGE_CONFIG_USAGE_GUIDE.md").read_text(
        encoding="utf-8"
    )
    pre_deploy_checklist = (
        PROJECT_ROOT / "web" / "frontend" / "scripts" / "PRE_DEPLOYMENT_CHECKLIST.md"
    ).read_text(encoding="utf-8")
    history_migration_report = (
        PROJECT_ROOT / "docs" / "reports" / "HTML5_HISTORY_MODE_MIGRATION_COMPLETION_REPORT.md"
    ).read_text(encoding="utf-8")
    history_migration_review = (
        PROJECT_ROOT / "docs" / "reports" / "CODE_REVIEW_HTML5_HISTORY_MIGRATION.md"
    ).read_text(encoding="utf-8")
    stage2_perf_report = (
        PROJECT_ROOT / "docs" / "reports" / "STAGE2_PERFORMANCE_OPTIMIZATION_COMPLETION_REPORT.md"
    ).read_text(encoding="utf-8")
    startup_warnings_fix = (PROJECT_ROOT / "docs" / "reports" / "STARTUP_WARNINGS_FIX.md").read_text(
        encoding="utf-8"
    )
    dashboard_api_report = (
        PROJECT_ROOT / "docs" / "reports" / "DASHBOARD_API_ENRICHMENT_COMPLETION_REPORT.md"
    ).read_text(encoding="utf-8")
    frontend_port_fix = (
        PROJECT_ROOT / "docs" / "reports" / "FRONTEND_PORT_FIX_COMPLETION_REPORT.md"
    ).read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    frontend_index = (PROJECT_ROOT / "docs" / "guides" / "frontend" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    frontend_docs = [
        "FRONTEND_ROUTING_OPTIMIZATION_GUIDE.md",
        "frontend-auth-guard-enablement-task.md",
        "frontend-change-hygiene-and-micro-commit-guide.md",
        "frontend-routing-history-migration-task.md",
        "frontend_optimization_next_steps.md",
        "css-scss-development-guide.md",
        "enhanced-ui-ux-guide.md",
        "history-mode-deployment-guide.md",
        "mystocks-artdeco-integration-fix.md",
        "SASS_DEPRECATION_FIX.md",
        "DASHBOARD_API_ENRICHMENT_GUIDE.md",
        "DASHBOARD_API_INTEGRATION_GUIDE.md",
        "api-data-fetching-pattern-standardization-task.md",
        "data-visualization-enhancement-task.md",
        "error-handling-implementation-task.md",
        "page-title-management-dynamic-options-task.md",
        "router_analysis_report_corrected.md",
    ]

    for name in frontend_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "frontend" / name).is_file()
        assert f"frontend/{name}" in guides_index
        assert f"frontend/{name}" in cleanup_index_root

    assert "docs/guides/frontend/frontend-change-hygiene-and-micro-commit-guide.md" in root_claude
    assert "docs/guides/frontend/frontend-change-hygiene-and-micro-commit-guide.md" in agents_md
    assert "docs/guides/frontend/css-scss-development-guide.md" in root_claude
    assert "docs/guides/frontend/frontend_optimization_next_steps.md" in frontend_status_report
    assert "docs/guides/frontend/SASS_DEPRECATION_FIX.md" in startup_warnings_fix
    assert "docs/guides/frontend/DASHBOARD_API_ENRICHMENT_GUIDE.md" in dashboard_api_report
    assert "docs/guides/frontend/DASHBOARD_API_INTEGRATION_GUIDE.md" in dashboard_api_report
    assert "docs/guides/frontend/DASHBOARD_API_INTEGRATION_GUIDE.md" in frontend_port_fix
    assert "../guides/frontend/mystocks-artdeco-integration-fix.md" in page_config_guide
    assert "docs/guides/frontend/history-mode-deployment-guide.md" in pre_deploy_checklist
    assert "docs/guides/frontend/history-mode-deployment-guide.md" in history_migration_report
    assert "docs/guides/frontend/history-mode-deployment-guide.md" in history_migration_review
    assert "docs/guides/frontend/history-mode-deployment-guide.md" in stage2_perf_report
    assert "DASHBOARD_API_ENRICHMENT_GUIDE" in frontend_index
    assert "DASHBOARD_API_INTEGRATION_GUIDE" in frontend_index
    assert "FRONTEND_ROUTING_OPTIMIZATION_GUIDE" in frontend_index
    assert "SASS_DEPRECATION_FIX" in frontend_index
    assert "api-data-fetching-pattern-standardization-task" in frontend_index
    assert "css-scss-development-guide" in frontend_index
    assert "data-visualization-enhancement-task" in frontend_index
    assert "enhanced-ui-ux-guide" in frontend_index
    assert "error-handling-implementation-task" in frontend_index
    assert "history-mode-deployment-guide" in frontend_index
    assert "frontend-auth-guard-enablement-task" in frontend_index
    assert "frontend-change-hygiene-and-micro-commit-guide" in frontend_index
    assert "frontend-routing-history-migration-task" in frontend_index
    assert "frontend_optimization_next_steps" in frontend_index
    assert "mystocks-artdeco-integration-fix" in frontend_index
    assert "page-title-management-dynamic-options-task" in frontend_index
    assert "router_analysis_report_corrected" in frontend_index


def test_mongo_multicli_guides_are_converged_under_guides_multicli_tasks() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    function_map = (PROJECT_ROOT / "docs" / "overview" / "FUNCTION_MAP.md").read_text(encoding="utf-8")
    function_catalog = (PROJECT_ROOT / "governance" / "function-tree" / "catalog.yaml").read_text(encoding="utf-8")
    cli_workflow_guide = (
        PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "CLI_WORKFLOW_GUIDE.md"
    ).read_text(encoding="utf-8")
    main_cli_standards = (
        PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "MAIN_CLI_WORKFLOW_STANDARDS.md"
    ).read_text(encoding="utf-8")
    task_report = (PROJECT_ROOT / "TASK-REPORT.md").read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    multicli_index = (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    mongo_docs = [
        "MONGO_MULTICLI_COORDINATION_GUIDE.md",
        "MONGO_MULTICLI_OPERATION_CHECKLIST.md",
    ]

    for name in mongo_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / name).is_file()
        assert f"multi-cli-tasks/{name}" in guides_index
        assert f"multi-cli-tasks/{name}" in cleanup_index_root

    assert "docs/guides/multi-cli-tasks/MONGO_MULTICLI_COORDINATION_GUIDE.md" in readme
    assert "docs/guides/multi-cli-tasks/MONGO_MULTICLI_COORDINATION_GUIDE.md" in function_map
    assert "docs/guides/multi-cli-tasks/MONGO_MULTICLI_COORDINATION_GUIDE.md" in function_catalog
    assert "docs/guides/multi-cli-tasks/MONGO_MULTICLI_OPERATION_CHECKLIST.md" in cli_workflow_guide
    assert "docs/guides/multi-cli-tasks/MONGO_MULTICLI_OPERATION_CHECKLIST.md" in main_cli_standards
    assert "docs/guides/multi-cli-tasks/MONGO_MULTICLI_OPERATION_CHECKLIST.md" in task_report
    assert "docs/guides/multi-cli-tasks/MONGO_MULTICLI_COORDINATION_GUIDE.md" in task_report
    assert "MONGO_MULTICLI_COORDINATION_GUIDE" in multicli_index
    assert "MONGO_MULTICLI_OPERATION_CHECKLIST" in multicli_index


def test_git_worktree_and_branch_strategy_guides_are_converged_under_guides_multicli_tasks() -> None:
    cicd_daily = (
        PROJECT_ROOT / "docs" / "operations" / "ci-cd" / "MYSTOCKS_CI_CD_DAILY_APPLICATION.md"
    ).read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    multicli_index = (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    docs = [
        "BRANCH_STRATEGY.md",
        "worktree.md",
    ]

    for name in docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / name).is_file()
        assert f"multi-cli-tasks/{name}" in guides_index
        assert f"multi-cli-tasks/{name}" in cleanup_index_root

    assert "docs/guides/multi-cli-tasks/BRANCH_STRATEGY.md" in cicd_daily
    assert "BRANCH_STRATEGY" in multicli_index
    assert "worktree" in multicli_index


def test_dayjs_guides_are_converged_under_guides_frontend_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    frontend_index = (PROJECT_ROOT / "docs" / "guides" / "frontend" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    for name in ["dayjs修复指南.md", "dayjs新手指南.md"]:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "frontend" / name).is_file()
        assert f"frontend/{name}" in guides_index
        assert f"frontend/{name}" in cleanup_index_root

    assert "dayjs修复指南" in frontend_index
    assert "dayjs新手指南" in frontend_index


def test_windows_tdx_bridge_setup_is_converged_under_guides_tdx_integration_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    tdx_index = (PROJECT_ROOT / "docs" / "guides" / "tdx-integration" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    tdx_readme = (PROJECT_ROOT / "docs" / "guides" / "tdx-integration" / "README.md").read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "docs" / "guides" / "WINDOWS_TDX_BRIDGE_SETUP.md").exists()
    assert (PROJECT_ROOT / "docs" / "guides" / "tdx-integration" / "WINDOWS_TDX_BRIDGE_SETUP.md").is_file()

    assert "tdx-integration/WINDOWS_TDX_BRIDGE_SETUP.md" in guides_index
    assert "WINDOWS_TDX_BRIDGE_SETUP" in tdx_index
    assert "./WINDOWS_TDX_BRIDGE_SETUP.md" in tdx_readme or "WINDOWS_TDX_BRIDGE_SETUP.md" in tdx_readme


def test_buger_client_guides_are_converged_under_guides_buger_family() -> None:
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    buger_index = (PROJECT_ROOT / "docs" / "guides" / "buger" / "INDEX.md").read_text(encoding="utf-8")
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")
    phase10_report = (PROJECT_ROOT / "docs" / "reports" / "PHASE10_BUG_REPORTING_INTEGRATION.md").read_text(
        encoding="utf-8"
    )

    buger_docs = [
        "B项目接入指南.md",
        "客户端连接指南.md",
        "客户端集成指南.md",
    ]

    for name in buger_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "buger" / name).is_file()
        assert f"buger/{name}" in guides_index
        assert f"buger/{name}" in cleanup_index_root

    assert "docs/guides/buger/B项目接入指南.md" in phase10_report
    assert "docs/guides/buger/客户端集成指南.md" in phase10_report
    assert "docs/guides/buger/客户端连接指南.md" in phase10_report
    assert "B项目接入指南" in buger_index
    assert "客户端连接指南" in buger_index
    assert "客户端集成指南" in buger_index


def test_cli_registration_and_roles_guides_are_converged_under_guides_multicli_tasks() -> None:
    cli_main_task = (PROJECT_ROOT / "scripts" / "cli" / "main" / "TASK.md").read_text(encoding="utf-8")
    cli_readme = (PROJECT_ROOT / "scripts" / "cli" / "README.md").read_text(encoding="utf-8")
    multicli_config_report = (
        PROJECT_ROOT / "docs" / "reports" / "MULTI_CLI_CONFIG_SYSTEM_COMPLETION.md"
    ).read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    multicli_index = (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    cli_docs = [
        "CLI_REGISTRATION_GUIDE.md",
        "CLI_ROLES_REFERENCE.md",
    ]

    for name in cli_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / name).is_file()
        assert f"multi-cli-tasks/{name}" in guides_index
        assert f"multi-cli-tasks/{name}" in cleanup_index_root

    assert "docs/guides/multi-cli-tasks/CLI_REGISTRATION_GUIDE.md" in cli_main_task
    assert "../docs/guides/multi-cli-tasks/CLI_REGISTRATION_GUIDE.md" in cli_readme
    assert "../docs/guides/multi-cli-tasks/CLI_REGISTRATION_GUIDE.md" in multicli_config_report
    assert "CLI_REGISTRATION_GUIDE" in multicli_index
    assert "CLI_ROLES_REFERENCE" in multicli_index


def test_multicli_coordination_guides_are_converged_under_guides_multicli_tasks() -> None:
    cli_main_task = (PROJECT_ROOT / "scripts" / "cli" / "main" / "TASK.md").read_text(encoding="utf-8")
    cli_readme = (PROJECT_ROOT / "scripts" / "cli" / "README.md").read_text(encoding="utf-8")
    multicli_config_report = (
        PROJECT_ROOT / "docs" / "reports" / "MULTI_CLI_CONFIG_SYSTEM_COMPLETION.md"
    ).read_text(encoding="utf-8")
    multicli_impl_report = (
        PROJECT_ROOT / "docs" / "reports" / "MULTI_CLI_IMPLEMENTATION_COMPLETION_REPORT.md"
    ).read_text(encoding="utf-8")
    multicli_comparison = (
        PROJECT_ROOT / "docs" / "reports" / "MULTI_CLI_V2_ARCHITECTURE_COMPARISON.md"
    ).read_text(encoding="utf-8")
    cli_roles_reference = (
        PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "CLI_ROLES_REFERENCE.md"
    ).read_text(encoding="utf-8")
    cli_registration_guide = (
        PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "CLI_REGISTRATION_GUIDE.md"
    ).read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    multicli_index = (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    cleanup_index_root = (
        PROJECT_ROOT / "docs" / "reports" / "cleanup" / "index-artifacts" / "INDEX_root.md"
    ).read_text(encoding="utf-8")

    multicli_docs = [
        "CONFIG_SYSTEM_GUIDE.md",
        "TASK_POOL_USAGE_GUIDE.md",
        "MULTI_CLI_COLLABORATION_METHOD.md",
        "MULTI_CLI_OPTIMIZATION_PROPOSAL.md",
    ]

    for name in multicli_docs:
        assert not (PROJECT_ROOT / "docs" / "guides" / name).exists()
        assert (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / name).is_file()
        assert f"multi-cli-tasks/{name}" in guides_index
        assert f"multi-cli-tasks/{name}" in cleanup_index_root

    assert "docs/guides/multi-cli-tasks/TASK_POOL_USAGE_GUIDE.md" in cli_main_task
    assert "../docs/guides/multi-cli-tasks/TASK_POOL_USAGE_GUIDE.md" in cli_readme
    assert "../docs/guides/multi-cli-tasks/MULTI_CLI_COLLABORATION_METHOD.md" in cli_readme
    assert "../docs/guides/multi-cli-tasks/CONFIG_SYSTEM_GUIDE.md" in multicli_config_report
    assert "../docs/guides/multi-cli-tasks/TASK_POOL_USAGE_GUIDE.md" in multicli_config_report
    assert "/opt/claude/mystocks_spec/docs/guides/multi-cli-tasks/MULTI_CLI_COLLABORATION_METHOD.md" in (
        multicli_impl_report
    )
    assert "docs/guides/multi-cli-tasks/MULTI_CLI_COLLABORATION_METHOD.md" in multicli_comparison
    assert "./CONFIG_SYSTEM_GUIDE.md" in cli_roles_reference
    assert "./TASK_POOL_USAGE_GUIDE.md" in cli_roles_reference
    assert "./MULTI_CLI_COLLABORATION_METHOD.md" in cli_registration_guide
    assert "CONFIG_SYSTEM_GUIDE" in multicli_index
    assert "TASK_POOL_USAGE_GUIDE" in multicli_index
    assert "MULTI_CLI_COLLABORATION_METHOD" in multicli_index
    assert "MULTI_CLI_OPTIMIZATION_PROPOSAL" in multicli_index


def test_root_agents_and_claude_document_gitnexus_staged_microbatch_rule() -> None:
    root_claude = (PROJECT_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    root_agents = (PROJECT_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    required_snippets = [
        'gitnexus_detect_changes({scope: "staged"})',
        'gitnexus_detect_changes({scope: "unstaged"})',
        "dirty worktree",
        "MUST NOT",
    ]

    for snippet in required_snippets:
        assert snippet in root_claude
        assert snippet in root_agents
