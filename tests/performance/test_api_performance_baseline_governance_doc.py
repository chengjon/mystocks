from pathlib import Path


def test_api_performance_baseline_governance_doc_is_linked_from_governance_readme():
    readme = Path("reports/governance/README.md").read_text(encoding="utf-8")
    assert "reports/governance/2026-04-22-api-performance-baseline-governance.md" in readme
    assert "Mongo / Graphiti Truth Boundary" in readme
    assert "API Performance Baseline Refresh Audit Example" in readme
    assert "Markdown 文件骨架" in readme
    assert "scripts/run_containerized_runtime_smoke.sh" in readme
    assert "scripts/run_full_runtime_delivery_gate.sh" in readme
    assert "8021/3021" in readme
    assert "8020/3020" in readme


def test_api_performance_baseline_governance_doc_is_linked_from_governance_sot():
    sot = Path("reports/governance/2026-04-10-tech-debt-governance-sot.md").read_text(encoding="utf-8")

    assert "reports/analysis/runtime-observability-baseline.json" in sot
    assert "reports/analysis/api-performance-baseline.json" in sot
    assert "reports/governance/2026-04-22-api-performance-baseline-governance.md" in sot


def test_api_performance_baseline_governance_doc_locks_formal_scope_and_commands():
    doc = Path("reports/governance/2026-04-22-api-performance-baseline-governance.md").read_text(encoding="utf-8")

    assert "reports/analysis/api-performance-baseline.json" in doc
    assert "http://localhost:8020" in doc
    assert "http://localhost:8021" in doc
    assert "tests/performance/api_smoke_endpoints.json" in doc
    assert "bash scripts/run_api_performance_baseline.sh" in doc
    assert "python scripts/dev/quality_gate/validate_api_performance_drift.py" in doc
    assert "python scripts/dev/quality_gate/collect_api_performance_baseline.py" in doc
    assert "Mongo 导出 / 导入后的 Markdown 投影" in doc
    assert "API Performance Baseline Refresh Audit" in doc


def test_weekly_governance_template_surfaces_containerized_deployment_entrypoints():
    template = Path("reports/governance/_TEMPLATE.WEEKLY-GOVERNANCE-REPORT.md").read_text(encoding="utf-8")

    assert "Container deployment contract pass" in template
    assert "Deployment env contract pass" in template
    assert "Docker runtime service role" in template
    assert "Canonical PM2 ports" in template
    assert "Backup smoke ports" in template
    assert "POSTGRES_PASSWORD=postgres TDENGINE_PASSWORD=taosdata bash scripts/run_containerized_runtime_smoke.sh" in template
    assert "bash scripts/run_full_runtime_delivery_gate.sh" in template


def test_scripts_readme_surfaces_containerized_runtime_delivery_entrypoints():
    readme = Path("scripts/README.md").read_text(encoding="utf-8")

    assert "## Runtime Delivery Entry Points" in readme
    assert "POSTGRES_PASSWORD=postgres TDENGINE_PASSWORD=taosdata bash scripts/run_containerized_runtime_smoke.sh" in readme
    assert "bash scripts/run_full_runtime_delivery_gate.sh" in readme
    assert "http://localhost:8020" in readme
    assert "http://localhost:3020" in readme
    assert "http://localhost:8021" in readme
    assert "http://localhost:3021" in readme
