import json
import subprocess
from pathlib import Path


def test_build_runtime_ci_bundle_writes_manifest_and_index(tmp_path: Path):
    frontend_dir = tmp_path / "frontend-runtime"
    api_dir = tmp_path / "api-performance"
    monitoring_dir = tmp_path / "monitoring-auth"
    runtime_quality_dir = tmp_path / "runtime-quality"
    docker_dir = tmp_path / "docker-runtime"
    drift_report_path = tmp_path / "runtime-observability-drift-report.json"

    frontend_dir.mkdir()
    api_dir.mkdir()
    monitoring_dir.mkdir()
    runtime_quality_dir.mkdir()
    docker_dir.mkdir()

    (frontend_dir / "SUMMARY.md").write_text("# Frontend Runtime\n", encoding="utf-8")
    (api_dir / "SUMMARY.md").write_text(
        "\n".join(
            [
                "# API Summary",
                "- Overall average response time: `18.47ms`",
                "- Overall average P95 response time: `22.94ms`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (monitoring_dir / "SUMMARY.md").write_text(
        "- `GET /api/v1/monitoring/alert-rules`: avg=117.01ms p95=271.53ms error=0.0%\n",
        encoding="utf-8",
    )
    (runtime_quality_dir / "SUMMARY.md").write_text(
        "\n".join(
            [
                "# Runtime Quality Summary",
                "- Overall gate status: `PASS`",
                "- Structural syntax / PM2 navigation gate: `14 passed (4.9s)`",
                "- Frontend type errors vs baseline: `0` current vs `0` baseline",
                "- Regression E2E actual result: `E2E Summary: passed=44 failed=0 skipped=0`",
                "- Anonymous API baseline: `COMPLIANT`",
                "- Monitoring auth baseline: `COMPLIANT`",
                "- Prometheus `slow_http_requests_total` delta during run: `0`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (docker_dir / "SUMMARY.md").write_text(
        "\n".join(
            [
                "# Docker Runtime Smoke",
                "- Backend health: `PASS`",
                "- Backend readiness: `PASS`",
                "- Frontend index: `PASS`",
                "- `/api/metrics/health`: `healthy`",
                "- Prometheus `http_requests_total` delta during run: `3.0`",
                "- Prometheus `slow_http_requests_total` delta during run: `0.0`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    drift_report_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-21T08:00:00+00:00",
                "metric_version": "v1",
                "baseline_generated_at": "2026-04-20T10:24:00+00:00",
                "current_generated_at": "2026-04-21T08:00:00+00:00",
                "pass": True,
                "violations": [],
                "not_measured": [],
                "checks": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    manifest_path = tmp_path / "bundle" / "runtime-artifact-manifest.json"
    index_path = tmp_path / "bundle" / "runtime-artifact-index.md"

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/build_runtime_ci_bundle.py",
            "--frontend-dir",
            str(frontend_dir),
            "--api-dir",
            str(api_dir),
            "--monitoring-dir",
            str(monitoring_dir),
            "--runtime-quality-dir",
            str(runtime_quality_dir),
            "--docker-dir",
            str(docker_dir),
            "--runtime-observability-drift-report",
            str(drift_report_path),
            "--output-manifest",
            str(manifest_path),
            "--output-index",
            str(index_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
    )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    index_text = index_path.read_text(encoding="utf-8")

    assert manifest["frontend_runtime_dir"] == str(frontend_dir.resolve())
    assert manifest["api_performance_dir"] == str(api_dir.resolve())
    assert manifest["monitoring_auth_dir"] == str(monitoring_dir.resolve())
    assert manifest["runtime_quality_dir"] == str(runtime_quality_dir.resolve())
    assert manifest["docker_runtime_dir"] == str(docker_dir.resolve())
    assert manifest["runtime_observability_drift_report"] == str(drift_report_path.resolve())
    assert manifest["summary_files"]["runtime_quality"] == str((runtime_quality_dir / "SUMMARY.md").resolve())
    assert manifest["summary_files"]["docker_runtime"] == str((docker_dir / "SUMMARY.md").resolve())
    assert manifest["summary_files"]["runtime_observability_drift"] == str(drift_report_path.resolve())

    assert "# Runtime Artifact Index" in index_text
    assert "## Key Gates" in index_text
    assert "## Report Entry Points" in index_text
    assert "## Performance Snapshot" in index_text
    assert "Overall gate status: `PASS`" in index_text
    assert "Structural syntax / PM2 navigation gate: `14 passed (4.9s)`" in index_text
    assert "Frontend type errors vs baseline: `0`" in index_text
    assert "Regression E2E: `E2E Summary: passed=44 failed=0 skipped=0`" in index_text
    assert "Anonymous API overall avg / P95: `18.47ms / 22.94ms`" in index_text
    assert "Monitoring auth key endpoint P95: `271.53ms`" in index_text
    assert "Runtime summary slow-request delta: `0`" in index_text
    assert "## Drift Gate" in index_text
    assert "Drift gate pass: `True`" in index_text
    assert "Drift gate violations: `0`" in index_text
    assert "Drift gate not_measured: `0`" in index_text
    assert "Docker runtime smoke: `PASS` / `PASS` / `PASS`" in index_text
    assert f"Docker runtime summary: `{docker_dir / 'SUMMARY.md'}`" in index_text
    assert "Docker metrics health: `healthy`" in index_text
    assert "Docker metrics http / slow delta: `3.0 / 0.0`" in index_text


def test_build_runtime_ci_bundle_supports_docker_only_runtime_summary(tmp_path: Path):
    runtime_quality_dir = tmp_path / "runtime-quality"
    docker_dir = tmp_path / "docker-runtime"
    drift_report_path = tmp_path / "runtime-observability-drift-report.json"

    runtime_quality_dir.mkdir()
    docker_dir.mkdir()

    (runtime_quality_dir / "SUMMARY.md").write_text(
        "\n".join(
            [
                "# Runtime Quality Summary",
                "- Overall gate status: `PASS`",
                "- Anonymous API baseline: `n/a`",
                "- Monitoring auth baseline: `n/a`",
                "- Prometheus `slow_http_requests_total` delta during run: `n/a`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (docker_dir / "SUMMARY.md").write_text(
        "\n".join(
            [
                "# Docker Runtime Smoke",
                "- Backend health: `PASS`",
                "- Backend readiness: `PASS`",
                "- Frontend index: `PASS`",
                "- `/api/metrics/health`: `healthy`",
                "- Prometheus `http_requests_total` delta during run: `5.0`",
                "- Prometheus `slow_http_requests_total` delta during run: `0.0`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    drift_report_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-21T08:00:00+00:00",
                "metric_version": "v1",
                "baseline_generated_at": "2026-04-20T10:24:00+00:00",
                "current_generated_at": "2026-04-21T08:00:00+00:00",
                "pass": True,
                "violations": [],
                "not_measured": [{"path": "api_performance.overall_p95_ms"}],
                "checks": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    manifest_path = tmp_path / "bundle" / "runtime-artifact-manifest.json"
    index_path = tmp_path / "bundle" / "runtime-artifact-index.md"

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/build_runtime_ci_bundle.py",
            "--runtime-quality-dir",
            str(runtime_quality_dir),
            "--docker-dir",
            str(docker_dir),
            "--runtime-observability-drift-report",
            str(drift_report_path),
            "--output-manifest",
            str(manifest_path),
            "--output-index",
            str(index_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
    )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    index_text = index_path.read_text(encoding="utf-8")

    assert "frontend_runtime_dir" not in manifest
    assert "api_performance_dir" not in manifest
    assert "monitoring_auth_dir" not in manifest
    assert manifest["docker_runtime_dir"] == str(docker_dir.resolve())
    assert manifest["runtime_observability_drift_report"] == str(drift_report_path.resolve())
    assert "Frontend runtime summary" not in index_text
    assert "API performance summary" not in index_text
    assert "Monitoring auth summary" not in index_text
    assert "Runtime observability drift report" in index_text
    assert "Drift gate not_measured: `1`" in index_text
    assert "Docker runtime smoke: `PASS` / `PASS` / `PASS`" in index_text
    assert "Docker metrics http / slow delta: `5.0 / 0.0`" in index_text
