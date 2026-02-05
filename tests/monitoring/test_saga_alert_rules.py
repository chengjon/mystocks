from pathlib import Path


def test_saga_alert_rules_file_exists():
    rules_path = Path("monitoring-stack/config/rules/saga-alerts.yml")
    assert rules_path.exists()


def test_saga_alert_rules_has_expected_alerts():
    rules_path = Path("monitoring-stack/config/rules/saga-alerts.yml")
    content = rules_path.read_text(encoding="utf-8")
    assert "SagaRollbackRateHigh" in content
    assert "SagaLatencyP95High" in content
