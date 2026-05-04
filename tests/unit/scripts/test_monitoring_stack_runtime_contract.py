from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_monitoring_stack_compose_wires_linux_host_gateway_and_canonical_dashboard_mount():
    compose_text = (REPO_ROOT / "config/monitoring-stack/docker-compose.yml").read_text(encoding="utf-8")

    assert 'host.docker.internal:host-gateway' in compose_text
    assert './grafana-dashboards:/etc/grafana/grafana-dashboards:ro' in compose_text


def test_monitoring_stack_prometheus_targets_current_runtime_ports_only():
    prometheus_text = (REPO_ROOT / "config/monitoring-stack/config/prometheus.yml").read_text(encoding="utf-8")

    assert "host.docker.internal:8020" in prometheus_text
    assert "host.docker.internal:8001" in prometheus_text
    assert "host.docker.internal:8000" not in prometheus_text
    assert "job_name: 'mystocks-health'" not in prometheus_text
    assert "job_name: 'mystocks-components'" not in prometheus_text


def test_monitoring_stack_dashboard_provisioning_and_verifier_follow_canonical_datasource_dashboard():
    provider_text = (
        REPO_ROOT / "config/monitoring-stack/provisioning/dashboards/dashboard.yml"
    ).read_text(encoding="utf-8")
    verify_script = (REPO_ROOT / "config/monitoring-stack/verify_monitoring.sh").read_text(encoding="utf-8")

    assert "/etc/grafana/grafana-dashboards" in provider_text
    assert "DataSourceMonitoring" in provider_text
    assert "grafana-dashboards/data_source_monitoring.json" in verify_script
    assert "MyStocks 数据源监控仪表板" in verify_script
