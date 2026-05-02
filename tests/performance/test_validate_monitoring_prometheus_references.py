import json
import subprocess
from pathlib import Path


def test_validate_monitoring_prometheus_references_accepts_runtime_backed_rules(tmp_path: Path):
    metrics_path = tmp_path / "metrics.raw.txt"
    rule_path = tmp_path / "rules.yml"
    output_path = tmp_path / "report.json"

    metrics_path.write_text(
        "\n".join(
            [
                '# HELP http_requests_total HTTP requests',
                'http_requests_total{endpoint="/health",method="GET",status_code="200"} 10',
                '# HELP http_request_duration_seconds HTTP latency',
                'http_request_duration_seconds_bucket{le="0.5"} 3',
                'slow_http_requests_total{endpoint="/api/v1/monitoring/alert-rules",method="GET"} 0',
                "mystocks_cache_hits_total 12",
                "mystocks_cache_misses_total 3",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    rule_path.write_text(
        "\n".join(
            [
                "groups:",
                "  - name: mystocks-api-alerts",
                "    rules:",
                "      - alert: HighLatency",
                "        expr: |",
                "          histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 0.3",
                "      - alert: HighCacheMissRate",
                "        expr: |",
                "          sum(mystocks_cache_misses_total)",
                "          / (sum(mystocks_cache_hits_total) + sum(mystocks_cache_misses_total)) > 0.5",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/validate_monitoring_prometheus_references.py",
            "--metrics-file",
            str(metrics_path),
            "--rule-file",
            str(rule_path),
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["pass"] is True
    assert payload["violations"] == []


def test_validate_monitoring_prometheus_references_reports_missing_metrics(tmp_path: Path):
    metrics_path = tmp_path / "metrics.raw.txt"
    rule_path = tmp_path / "rules.yml"
    output_path = tmp_path / "report.json"

    metrics_path.write_text("http_requests_total 10\n", encoding="utf-8")
    rule_path.write_text(
        "\n".join(
            [
                "slos:",
                '  - name: "cache-hit-rate"',
                "    measurement: |",
                "      sum(mystocks_cache_hits_total) / (sum(mystocks_cache_hits_total) + sum(mystocks_cache_misses_total)) * 100",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/validate_monitoring_prometheus_references.py",
            "--metrics-file",
            str(metrics_path),
            "--rule-file",
            str(rule_path),
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert proc.returncode == 1
    assert payload["pass"] is False
    assert payload["violations"][0]["rule_name"] == "cache-hit-rate"
    assert payload["violations"][0]["missing_metrics"] == [
        "mystocks_cache_hits_total",
        "mystocks_cache_misses_total",
    ]


def test_validate_monitoring_prometheus_references_supports_dashboard_targets(tmp_path: Path):
    metrics_path = tmp_path / "metrics.raw.txt"
    rule_path = tmp_path / "rules.yml"
    dashboard_path = tmp_path / "dashboard.json"
    declared_metrics_path = tmp_path / "declared_metrics.py"
    output_path = tmp_path / "report.json"

    metrics_path.write_text(
        "\n".join(
            [
                'http_requests_total{endpoint="/health",method="GET",status_code="200"} 10',
                'http_request_duration_seconds_bucket{le="0.5"} 3',
                "mystocks_cache_hits_total 12",
                "mystocks_cache_misses_total 3",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    rule_path.write_text(
        "\n".join(
            [
                "groups:",
                "  - name: mystocks-api-alerts",
                "    rules:",
                "      - alert: HighLatency",
                "        expr: |",
                "          histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 0.3",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    dashboard_path.write_text(
        json.dumps(
            {
                "dashboard": {
                    "title": "API Overview",
                    "panels": [
                        {
                            "id": 1,
                            "title": "Cache Evictions",
                            "targets": [
                                {
                                    "expr": "sum by (cache_type) (mystocks_cache_evictions_total)"
                                }
                            ],
                        }
                    ],
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    declared_metrics_path.write_text(
        "\n".join(
            [
                "from prometheus_client import Counter",
                "",
                'CACHE_EVICTIONS = Counter("mystocks_cache_evictions_total", "cache evictions", ["cache_type", "reason"])',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/validate_monitoring_prometheus_references.py",
            "--metrics-file",
            str(metrics_path),
            "--rule-file",
            str(rule_path),
            "--dashboard-file",
            str(dashboard_path),
            "--declared-metrics-python-file",
            str(declared_metrics_path),
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["pass"] is True
    assert payload["dashboard_files"] == [str(dashboard_path.resolve())]
    assert payload["declared_metric_python_files"] == [str(declared_metrics_path.resolve())]


def test_datasource_monitoring_assets_reference_declared_datasource_metrics(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[2]
    metrics_path = tmp_path / "metrics.raw.txt"
    output_path = tmp_path / "report.json"

    metrics_path.write_text(
        "\n".join(
            [
                'datasource_api_latency_seconds_bucket{endpoint="akshare.stock_zh_a_hist",data_category="DAILY_KLINE",le="0.5"} 3',
                'datasource_api_latency_seconds_bucket{endpoint="akshare.stock_zh_a_hist",data_category="DAILY_KLINE",le="+Inf"} 3',
                'datasource_api_calls_total{endpoint="akshare.stock_zh_a_hist",data_category="DAILY_KLINE",status="success"} 10',
                'datasource_cache_hits_total{endpoint="akshare.stock_zh_a_hist"} 8',
                'datasource_cache_misses_total{endpoint="akshare.stock_zh_a_hist"} 2',
                'datasource_circuit_breaker_state{endpoint="akshare.stock_zh_a_hist"} 0',
                'datasource_api_cost_estimated{endpoint="akshare.stock_zh_a_hist"} 0.12',
                'datasource_data_quality{endpoint="akshare.stock_zh_a_hist",check_type="logic_check"} 100',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/validate_monitoring_prometheus_references.py",
            "--metrics-file",
            str(metrics_path),
            "--rule-file",
            str(repo_root / "config/monitoring-stack/config/rules/data-source-alerts.yml"),
            "--dashboard-file",
            str(repo_root / "config/monitoring-stack/grafana-dashboards/data_source_monitoring.json"),
            "--declared-metrics-python-file",
            str(repo_root / "src/core/data_source/metrics.py"),
            "--output",
            str(output_path),
        ],
        cwd=repo_root,
        check=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["pass"] is True
    assert payload["violations"] == []
