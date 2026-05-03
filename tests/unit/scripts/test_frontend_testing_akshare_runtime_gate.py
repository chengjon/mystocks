from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_frontend_testing_runtime_delivery_summary_runs_akshare_market_gates() -> None:
    workflow = (PROJECT_ROOT / ".github/workflows/frontend-testing.yml").read_text(encoding="utf-8")

    assert "scripts/dev/quality_gate/collect_akshare_market_function_availability.py" in workflow
    assert "scripts/dev/quality_gate/run_akshare_market_gates.py" in workflow
    assert "scripts/dev/quality_gate/validate_akshare_market_repo_truth.py" in workflow
    assert "tests/unit/scripts/test_collect_akshare_market_function_availability.py" in workflow
    assert "tests/unit/scripts/test_run_akshare_market_gates.py" in workflow
    assert "tests/unit/scripts/test_validate_akshare_market_repo_truth.py" in workflow

    runtime_delivery_section = workflow.split("runtime-delivery-summary:", 1)[1]

    assert "Generate AkShare market gate reports" in runtime_delivery_section
    assert "python scripts/dev/quality_gate/run_akshare_market_gates.py" in runtime_delivery_section
    assert "reports/analysis/runtime-quality-summary-ci/akshare-market-function-availability.json" in runtime_delivery_section
    assert "reports/analysis/runtime-quality-summary-ci/akshare-market-repo-truth-gate.json" in runtime_delivery_section
    assert "reports/analysis/runtime-quality-summary-ci/akshare-market-gates-summary.json" in runtime_delivery_section
    assert (
        "--akshare-market-function-availability-report "
        "reports/analysis/runtime-quality-summary-ci/akshare-market-function-availability.json"
    ) in runtime_delivery_section
    assert (
        "--akshare-market-repo-truth-report "
        "reports/analysis/runtime-quality-summary-ci/akshare-market-repo-truth-gate.json"
    ) in runtime_delivery_section
    assert (
        "--akshare-market-gates-summary-report "
        "reports/analysis/runtime-quality-summary-ci/akshare-market-gates-summary.json"
    ) in runtime_delivery_section
