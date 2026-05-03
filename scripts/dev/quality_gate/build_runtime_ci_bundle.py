from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _first_match(pattern: str, text: str, fallback: str = "n/a") -> str:
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(_read_text(path))


def build_bundle_manifest(
    frontend_dir: Path | None,
    api_dir: Path | None,
    monitoring_dir: Path | None,
    runtime_quality_dir: Path,
    docker_dir: Path | None = None,
    runtime_observability_drift_report_path: Path | None = None,
    api_performance_drift_report_path: Path | None = None,
    monitoring_rule_report_path: Path | None = None,
    backend_runtime_dependency_report_path: Path | None = None,
    container_deployment_contract_report_path: Path | None = None,
    deployment_env_contract_report_path: Path | None = None,
    akshare_market_function_availability_report_path: Path | None = None,
    akshare_market_repo_truth_report_path: Path | None = None,
    akshare_market_gates_summary_report_path: Path | None = None,
) -> dict[str, object]:
    manifest: dict[str, object] = {
        "runtime_quality_dir": str(runtime_quality_dir),
        "summary_files": {"runtime_quality": str(runtime_quality_dir / "SUMMARY.md")},
    }
    if frontend_dir is not None:
        manifest["frontend_runtime_dir"] = str(frontend_dir)
        frontend_runtime_gate_path = frontend_dir / "frontend-runtime-gate.json"
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["frontend_runtime"] = str(frontend_dir / "SUMMARY.md")
        if frontend_runtime_gate_path.exists():
            manifest["frontend_runtime_gate_report"] = str(frontend_runtime_gate_path)
            summary_files["frontend_runtime_gate"] = str(frontend_runtime_gate_path)
    if api_dir is not None:
        manifest["api_performance_dir"] = str(api_dir)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["api_performance"] = str(api_dir / "SUMMARY.md")
    if monitoring_dir is not None:
        manifest["monitoring_auth_dir"] = str(monitoring_dir)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["monitoring_auth"] = str(monitoring_dir / "SUMMARY.md")
    if docker_dir is not None:
        manifest["docker_runtime_dir"] = str(docker_dir)
        docker_runtime_json_path = docker_dir / "docker-runtime-smoke.json"
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["docker_runtime"] = str(docker_dir / "SUMMARY.md")
        if docker_runtime_json_path.exists():
            manifest["docker_runtime_report"] = str(docker_runtime_json_path)
            summary_files["docker_runtime_report"] = str(docker_runtime_json_path)
    if runtime_observability_drift_report_path is not None:
        manifest["runtime_observability_drift_report"] = str(runtime_observability_drift_report_path)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["runtime_observability_drift"] = str(runtime_observability_drift_report_path)
    if api_performance_drift_report_path is not None:
        manifest["api_performance_drift_report"] = str(api_performance_drift_report_path)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["api_performance_drift"] = str(api_performance_drift_report_path)
    if monitoring_rule_report_path is not None:
        manifest["monitoring_rule_report"] = str(monitoring_rule_report_path)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["monitoring_rule_report"] = str(monitoring_rule_report_path)
    if backend_runtime_dependency_report_path is not None:
        manifest["backend_runtime_dependency_report"] = str(backend_runtime_dependency_report_path)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["backend_runtime_dependency_report"] = str(backend_runtime_dependency_report_path)
    if container_deployment_contract_report_path is not None:
        manifest["container_deployment_contract_report"] = str(container_deployment_contract_report_path)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["container_deployment_contract_report"] = str(container_deployment_contract_report_path)
    if deployment_env_contract_report_path is not None:
        manifest["deployment_env_contract_report"] = str(deployment_env_contract_report_path)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["deployment_env_contract_report"] = str(deployment_env_contract_report_path)
    if akshare_market_function_availability_report_path is not None:
        manifest["akshare_market_function_availability_report"] = str(akshare_market_function_availability_report_path)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["akshare_market_function_availability_report"] = str(
            akshare_market_function_availability_report_path
        )
    if akshare_market_repo_truth_report_path is not None:
        manifest["akshare_market_repo_truth_report"] = str(akshare_market_repo_truth_report_path)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["akshare_market_repo_truth_report"] = str(akshare_market_repo_truth_report_path)
    if akshare_market_gates_summary_report_path is not None:
        manifest["akshare_market_gates_summary_report"] = str(akshare_market_gates_summary_report_path)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["akshare_market_gates_summary_report"] = str(akshare_market_gates_summary_report_path)
    return manifest


def build_bundle_index(
    frontend_dir: Path | None,
    api_dir: Path | None,
    monitoring_dir: Path | None,
    runtime_quality_dir: Path,
    docker_dir: Path | None = None,
    runtime_observability_drift_report_path: Path | None = None,
    api_performance_drift_report_path: Path | None = None,
    monitoring_rule_report_path: Path | None = None,
    backend_runtime_dependency_report_path: Path | None = None,
    container_deployment_contract_report_path: Path | None = None,
    deployment_env_contract_report_path: Path | None = None,
    akshare_market_function_availability_report_path: Path | None = None,
    akshare_market_repo_truth_report_path: Path | None = None,
    akshare_market_gates_summary_report_path: Path | None = None,
) -> str:
    api_summary = _read_text(api_dir / "SUMMARY.md") if api_dir is not None else ""
    monitoring_summary = _read_text(monitoring_dir / "SUMMARY.md") if monitoring_dir is not None else ""
    runtime_quality_summary = _read_text(runtime_quality_dir / "SUMMARY.md")
    docker_summary = _read_text(docker_dir / "SUMMARY.md") if docker_dir is not None else ""
    docker_runtime_report = None
    if docker_dir is not None:
        docker_runtime_json_path = docker_dir / "docker-runtime-smoke.json"
        if docker_runtime_json_path.exists():
            docker_runtime_report = _read_json(docker_runtime_json_path)
    frontend_runtime_gate = None
    if frontend_dir is not None:
        frontend_runtime_gate_path = frontend_dir / "frontend-runtime-gate.json"
        if frontend_runtime_gate_path.exists():
            frontend_runtime_gate = _read_json(frontend_runtime_gate_path)
    drift_report_text = _read_text(runtime_observability_drift_report_path) if runtime_observability_drift_report_path is not None else ""
    drift_report = json.loads(drift_report_text) if drift_report_text else None
    performance_drift_text = _read_text(api_performance_drift_report_path) if api_performance_drift_report_path is not None else ""
    performance_drift_report = json.loads(performance_drift_text) if performance_drift_text else None
    monitoring_rule_report_text = _read_text(monitoring_rule_report_path) if monitoring_rule_report_path is not None else ""
    monitoring_rule_report = json.loads(monitoring_rule_report_text) if monitoring_rule_report_text else None
    backend_runtime_dep_text = (
        _read_text(backend_runtime_dependency_report_path) if backend_runtime_dependency_report_path is not None else ""
    )
    backend_runtime_dep_report = json.loads(backend_runtime_dep_text) if backend_runtime_dep_text else None
    container_deployment_contract_text = (
        _read_text(container_deployment_contract_report_path)
        if container_deployment_contract_report_path is not None
        else ""
    )
    container_deployment_contract_report = (
        json.loads(container_deployment_contract_text) if container_deployment_contract_text else None
    )
    deployment_env_contract_text = (
        _read_text(deployment_env_contract_report_path) if deployment_env_contract_report_path is not None else ""
    )
    deployment_env_contract_report = json.loads(deployment_env_contract_text) if deployment_env_contract_text else None
    akshare_availability_text = (
        _read_text(akshare_market_function_availability_report_path)
        if akshare_market_function_availability_report_path is not None
        else ""
    )
    akshare_availability_report = json.loads(akshare_availability_text) if akshare_availability_text else None
    akshare_repo_truth_text = (
        _read_text(akshare_market_repo_truth_report_path) if akshare_market_repo_truth_report_path is not None else ""
    )
    akshare_repo_truth_report = json.loads(akshare_repo_truth_text) if akshare_repo_truth_text else None
    akshare_gate_summary_text = (
        _read_text(akshare_market_gates_summary_report_path) if akshare_market_gates_summary_report_path is not None else ""
    )
    akshare_gate_summary_report = json.loads(akshare_gate_summary_text) if akshare_gate_summary_text else None

    lines = [
        "# Runtime Artifact Index",
        "",
        "## Key Gates",
        "",
        f"- Overall gate status: `{_first_match(r'- Overall gate status: `([^`]+)`', runtime_quality_summary)}`",
        f"- Structural syntax / PM2 navigation gate: `{(frontend_runtime_gate or {}).get('structural_gate', _first_match(r'- Structural syntax / PM2 navigation gate: `([^`]+)`', runtime_quality_summary))}`",
        f"- Frontend type errors vs baseline: `{_first_match(r'- Frontend type errors vs baseline: `([^`]+)`', runtime_quality_summary)}`",
        f"- Regression E2E: `{(frontend_runtime_gate or {}).get('regression_e2e', _first_match(r'- Regression E2E actual result: `([^`]+)`', runtime_quality_summary))}`",
        f"- Anonymous API baseline: `{_first_match(r'- Anonymous API baseline: `([^`]+)`', runtime_quality_summary)}`",
        f"- Monitoring auth baseline: `{_first_match(r'- Monitoring auth baseline: `([^`]+)`', runtime_quality_summary)}`",
    ]
    if frontend_runtime_gate is not None:
        pm2_online = ", ".join(frontend_runtime_gate.get("pm2_services_online", [])) or "none"
        lines.append(f"- PM2 services online: `{pm2_online}`")
        lines.append(
            f"- Regression pytest: `{frontend_runtime_gate.get('regression_pytest', 'n/a')}`"
        )
        lines.append(
            f"- Accessibility smoke: `{frontend_runtime_gate.get('accessibility_smoke', 'n/a')}`"
        )
    if docker_dir is not None:
        docker_backend_health = (
            ((docker_runtime_report or {}).get("checks") or {}).get("backend_health")
            if docker_runtime_report is not None
            else _first_match(r'- Backend health: `([^`]+)`', docker_summary)
        )
        docker_backend_readiness = (
            ((docker_runtime_report or {}).get("checks") or {}).get("backend_readiness")
            if docker_runtime_report is not None
            else _first_match(r'- Backend readiness: `([^`]+)`', docker_summary)
        )
        docker_frontend_index = (
            ((docker_runtime_report or {}).get("checks") or {}).get("frontend_index")
            if docker_runtime_report is not None
            else _first_match(r'- Frontend index: `([^`]+)`', docker_summary)
        )
        lines.append(
            f"- Docker runtime smoke: `{docker_backend_health}` / `{docker_backend_readiness}` / `{docker_frontend_index}`"
        )

    lines.extend(
        [
            "",
            "## Report Entry Points",
            "",
            f"- Unified runtime summary: `{runtime_quality_dir / 'SUMMARY.md'}`",
        ]
    )
    if runtime_observability_drift_report_path is not None:
        lines.append(f"- Runtime observability drift report: `{runtime_observability_drift_report_path}`")
    if api_performance_drift_report_path is not None:
        lines.append(f"- API performance drift report: `{api_performance_drift_report_path}`")
    if monitoring_rule_report_path is not None:
        lines.append(f"- Monitoring rule metric reference report: `{monitoring_rule_report_path}`")
    if backend_runtime_dependency_report_path is not None:
        lines.append(f"- Backend runtime dependency report: `{backend_runtime_dependency_report_path}`")
    if container_deployment_contract_report_path is not None:
        lines.append(f"- Container deployment contract report: `{container_deployment_contract_report_path}`")
    if deployment_env_contract_report_path is not None:
        lines.append(f"- Deployment env contract report: `{deployment_env_contract_report_path}`")
    if akshare_market_function_availability_report_path is not None:
        lines.append(f"- AkShare function availability report: `{akshare_market_function_availability_report_path}`")
    if akshare_market_repo_truth_report_path is not None:
        lines.append(f"- AkShare repo-truth gate report: `{akshare_market_repo_truth_report_path}`")
    if akshare_market_gates_summary_report_path is not None:
        lines.append(f"- AkShare gate summary report: `{akshare_market_gates_summary_report_path}`")
    if frontend_dir is not None:
        lines.append(f"- Frontend runtime summary: `{frontend_dir / 'SUMMARY.md'}`")
        if frontend_runtime_gate is not None:
            lines.append(f"- Frontend runtime gate report: `{frontend_dir / 'frontend-runtime-gate.json'}`")
    if api_dir is not None:
        lines.append(f"- API performance summary: `{api_dir / 'SUMMARY.md'}`")
    if monitoring_dir is not None:
        lines.append(f"- Monitoring auth summary: `{monitoring_dir / 'SUMMARY.md'}`")
    if docker_dir is not None:
        lines.append(f"- Docker runtime summary: `{docker_dir / 'SUMMARY.md'}`")
        if docker_runtime_report is not None:
            lines.append(f"- Docker runtime report: `{docker_dir / 'docker-runtime-smoke.json'}`")
    lines.extend(["", "## Performance Snapshot", ""])
    if api_dir is not None:
        lines.append(
            f"- Anonymous API overall avg / P95: `{_first_match(r'- Overall average response time: `([^`]+)`', api_summary)} / {_first_match(r'- Overall average P95 response time: `([^`]+)`', api_summary)}`"
        )
    if monitoring_dir is not None:
        lines.append(
            f"- Monitoring auth key endpoint P95: `{_first_match(r'- `GET /api/v1/monitoring/alert-rules`: avg=[^\\n]+ p95=([^ ]+) error=', monitoring_summary)}`"
        )
    lines.append(
        f"- Runtime summary slow-request delta: `{_first_match(r'- Prometheus `slow_http_requests_total` delta during run: `([^`]+)`', runtime_quality_summary)}`"
    )
    if drift_report is not None:
        lines.extend(
            [
                "",
                "## Drift Gate",
                "",
                f"- Drift gate pass: `{drift_report.get('pass', 'n/a')}`",
                f"- Drift gate violations: `{len(drift_report.get('violations', []))}`",
                f"- Drift gate not_measured: `{len(drift_report.get('not_measured', []))}`",
            ]
        )
    if performance_drift_report is not None:
        lines.extend(
            [
                "",
                "## API Performance Drift",
                "",
                f"- API performance drift pass: `{performance_drift_report.get('pass', 'n/a')}`",
                f"- API performance drift violations: `{len(performance_drift_report.get('violations', []))}`",
                f"- API performance drift budget: `+{performance_drift_report.get('absolute_budget_ms', 'n/a')}ms / +{performance_drift_report.get('relative_budget_ratio', 'n/a')}`",
            ]
        )
    if monitoring_rule_report is not None:
        lines.extend(
            [
                "",
                "## Monitoring Rule Metrics",
                "",
                f"- Rule metric reference pass: `{monitoring_rule_report.get('pass', 'n/a')}`",
                f"- Rule metric reference violations: `{len(monitoring_rule_report.get('violations', []))}`",
                f"- Rule metric snapshots used: `{len(monitoring_rule_report.get('metrics_files', []))}`",
                f"- Dashboard files checked: `{len(monitoring_rule_report.get('dashboard_files', []))}`",
            ]
        )
    if backend_runtime_dep_report is not None:
        lines.extend(
            [
                "",
                "## Backend Runtime Dependencies",
                "",
                f"- Backend runtime dependency pass: `{backend_runtime_dep_report.get('pass', 'n/a')}`",
                f"- Forbidden packages present: `{len(backend_runtime_dep_report.get('forbidden_packages_present', []))}`",
                f"- Missing filtered packages: `{len(backend_runtime_dep_report.get('missing_filtered_packages', []))}`",
            ]
        )
    if container_deployment_contract_report is not None:
        lines.extend(
            [
                "",
                "## Container Deployment Contract",
                "",
                f"- Container deployment contract pass: `{container_deployment_contract_report.get('pass', 'n/a')}`",
                f"- Container deployment contract violations: `{len(container_deployment_contract_report.get('violations', []))}`",
                f"- Canonical PM2 ports: `{container_deployment_contract_report.get('canonical_ports', {})}`",
                f"- Backup smoke ports: `{container_deployment_contract_report.get('backup_smoke_ports', {})}`",
            ]
        )
    if deployment_env_contract_report is not None:
        lines.extend(
            [
                "",
                "## Deployment Env Contract",
                "",
                f"- Deployment env contract pass: `{deployment_env_contract_report.get('pass', 'n/a')}`",
                f"- Deployment env contract violations: `{len(deployment_env_contract_report.get('violations', []))}`",
                f"- Backend PM2 required env keys: `{deployment_env_contract_report.get('backend_required_env_keys', [])}`",
                f"- Frontend PM2 required env keys: `{deployment_env_contract_report.get('frontend_required_env_keys', [])}`",
            ]
        )
    if akshare_availability_report is not None or akshare_repo_truth_report is not None:
        availability_summary = (akshare_availability_report or {}).get("summary", {})
        repo_truth_summary = (akshare_repo_truth_report or {}).get("summary", {})
        tracked_count = availability_summary.get("tracked_count", repo_truth_summary.get("tracked_count", "n/a"))
        available_count = availability_summary.get("available_count", "n/a")
        missing_count = availability_summary.get("missing_count", "n/a")
        lines.extend(
            [
                "",
                "## AkShare Market Gate",
                "",
                f"- AkShare module import: `{(akshare_availability_report or {}).get('import_ok', 'n/a')}`",
                f"- AkShare module version: `{(akshare_availability_report or {}).get('module_version', 'n/a')}`",
                f"- AkShare tracked / available / missing: `{tracked_count} / {available_count} / {missing_count}`",
                f"- AkShare gate bundle pass: `{(akshare_gate_summary_report or {}).get('pass', 'n/a')}`",
                f"- AkShare repo-truth gate pass: `{(akshare_repo_truth_report or {}).get('pass', 'n/a')}`",
                f"- AkShare repo-truth violations: `{len((akshare_repo_truth_report or {}).get('violations', []))}`",
            ]
        )
    if docker_dir is not None:
        lines.extend(
            [
                f"- Docker metrics health: `{_first_match(r'- `/api/metrics/health`: `([^`]+)`', docker_summary)}`",
                f"- Docker metrics http / slow delta: `{_first_match(r'- Prometheus `http_requests_total` delta during run: `([^`]+)`', docker_summary)} / {_first_match(r'- Prometheus `slow_http_requests_total` delta during run: `([^`]+)`', docker_summary)}`",
            ]
        )
    lines.extend(
        [
            "",
            "See `runtime-artifact-manifest.json` for machine-readable paths.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the runtime CI artifact manifest and index.")
    parser.add_argument("--frontend-dir", type=Path)
    parser.add_argument("--api-dir", type=Path)
    parser.add_argument("--monitoring-dir", type=Path)
    parser.add_argument("--runtime-quality-dir", required=True, type=Path)
    parser.add_argument("--docker-dir", type=Path)
    parser.add_argument("--runtime-observability-drift-report", type=Path)
    parser.add_argument("--api-performance-drift-report", type=Path)
    parser.add_argument("--monitoring-rule-report", type=Path)
    parser.add_argument("--backend-runtime-dependency-report", type=Path)
    parser.add_argument("--container-deployment-contract-report", type=Path)
    parser.add_argument("--deployment-env-contract-report", type=Path)
    parser.add_argument("--akshare-market-function-availability-report", type=Path)
    parser.add_argument("--akshare-market-repo-truth-report", type=Path)
    parser.add_argument("--akshare-market-gates-summary-report", type=Path)
    parser.add_argument("--output-manifest", required=True, type=Path)
    parser.add_argument("--output-index", required=True, type=Path)
    args = parser.parse_args()

    manifest = build_bundle_manifest(
        frontend_dir=args.frontend_dir.resolve() if args.frontend_dir else None,
        api_dir=args.api_dir.resolve() if args.api_dir else None,
        monitoring_dir=args.monitoring_dir.resolve() if args.monitoring_dir else None,
        runtime_quality_dir=args.runtime_quality_dir.resolve(),
        docker_dir=args.docker_dir.resolve() if args.docker_dir else None,
        runtime_observability_drift_report_path=args.runtime_observability_drift_report.resolve() if args.runtime_observability_drift_report else None,
        api_performance_drift_report_path=args.api_performance_drift_report.resolve() if args.api_performance_drift_report else None,
        monitoring_rule_report_path=args.monitoring_rule_report.resolve() if args.monitoring_rule_report else None,
        backend_runtime_dependency_report_path=(
            args.backend_runtime_dependency_report.resolve() if args.backend_runtime_dependency_report else None
        ),
        container_deployment_contract_report_path=(
            args.container_deployment_contract_report.resolve() if args.container_deployment_contract_report else None
        ),
        deployment_env_contract_report_path=(
            args.deployment_env_contract_report.resolve() if args.deployment_env_contract_report else None
        ),
        akshare_market_function_availability_report_path=(
            args.akshare_market_function_availability_report.resolve()
            if args.akshare_market_function_availability_report
            else None
        ),
        akshare_market_repo_truth_report_path=(
            args.akshare_market_repo_truth_report.resolve() if args.akshare_market_repo_truth_report else None
        ),
        akshare_market_gates_summary_report_path=(
            args.akshare_market_gates_summary_report.resolve() if args.akshare_market_gates_summary_report else None
        ),
    )
    index_text = build_bundle_index(
        frontend_dir=args.frontend_dir.resolve() if args.frontend_dir else None,
        api_dir=args.api_dir.resolve() if args.api_dir else None,
        monitoring_dir=args.monitoring_dir.resolve() if args.monitoring_dir else None,
        runtime_quality_dir=args.runtime_quality_dir.resolve(),
        docker_dir=args.docker_dir.resolve() if args.docker_dir else None,
        runtime_observability_drift_report_path=args.runtime_observability_drift_report.resolve() if args.runtime_observability_drift_report else None,
        api_performance_drift_report_path=args.api_performance_drift_report.resolve() if args.api_performance_drift_report else None,
        monitoring_rule_report_path=args.monitoring_rule_report.resolve() if args.monitoring_rule_report else None,
        backend_runtime_dependency_report_path=(
            args.backend_runtime_dependency_report.resolve() if args.backend_runtime_dependency_report else None
        ),
        container_deployment_contract_report_path=(
            args.container_deployment_contract_report.resolve() if args.container_deployment_contract_report else None
        ),
        deployment_env_contract_report_path=(
            args.deployment_env_contract_report.resolve() if args.deployment_env_contract_report else None
        ),
        akshare_market_function_availability_report_path=(
            args.akshare_market_function_availability_report.resolve()
            if args.akshare_market_function_availability_report
            else None
        ),
        akshare_market_repo_truth_report_path=(
            args.akshare_market_repo_truth_report.resolve() if args.akshare_market_repo_truth_report else None
        ),
        akshare_market_gates_summary_report_path=(
            args.akshare_market_gates_summary_report.resolve() if args.akshare_market_gates_summary_report else None
        ),
    )

    args.output_manifest.parent.mkdir(parents=True, exist_ok=True)
    args.output_index.parent.mkdir(parents=True, exist_ok=True)
    args.output_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output_index.write_text(index_text, encoding="utf-8")


if __name__ == "__main__":
    main()
