import json
import subprocess
from pathlib import Path


def _write_wrapper_fixture(tmp_path: Path, repo_truth_status: str = "已实现") -> dict[str, Path]:
    manifest = [
        {
            "task_id": "6.1",
            "function_name": "dumps",
            "registry_key": "akshare_json_dumps",
            "adapter_method": "get_json_dumps",
            "route_fragment": "/json/dumps",
            "unit_test_token": "test_get_json_dumps",
            "backend_test_token": "/json/dumps",
            "api_test_token": "test_json_dumps_endpoint",
        }
    ]

    tasks_path = tmp_path / "tasks.md"
    tasks_path.write_text("- [x] 6.1 实现 JSON dumps (akshare.dumps)\n", encoding="utf-8")

    repo_truth_path = tmp_path / "repo_truth.md"
    repo_truth_path.write_text(
        f"| 6.1 | `dumps` | `/api/json/dumps` | `get_json_dumps()` | {repo_truth_status} |\n",
        encoding="utf-8",
    )

    registry_path = tmp_path / "registry.yaml"
    registry_path.write_text("akshare_json_dumps:\n  status: active\n", encoding="utf-8")

    adapter_path = tmp_path / "adapter.py"
    adapter_path.write_text("async def get_json_dumps():\n    return None\n", encoding="utf-8")

    route_path = tmp_path / "route.py"
    route_path.write_text('@router.get("/json/dumps")\nasync def get_json_dumps():\n    return {}\n', encoding="utf-8")

    unit_test_path = tmp_path / "unit_test.py"
    unit_test_path.write_text("def test_get_json_dumps():\n    assert True\n", encoding="utf-8")

    backend_test_path = tmp_path / "backend_test.py"
    backend_test_path.write_text('response = client.get("/api/json/dumps")\n', encoding="utf-8")

    api_test_path = tmp_path / "api_test.py"
    api_test_path.write_text("def test_json_dumps_endpoint():\n    assert True\n", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "manifest": manifest_path,
        "tasks": tasks_path,
        "repo_truth": repo_truth_path,
        "registry": registry_path,
        "adapter": adapter_path,
        "route": route_path,
        "unit_test": unit_test_path,
        "backend_test": backend_test_path,
        "api_test": api_test_path,
    }


def test_run_akshare_market_gates_writes_all_reports(tmp_path: Path):
    fixture = _write_wrapper_fixture(tmp_path)
    output_dir = tmp_path / "reports"

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/run_akshare_market_gates.py",
            "--module",
            "json",
            "--function",
            "dumps",
            "--manifest-json",
            str(fixture["manifest"]),
            "--tasks-path",
            str(fixture["tasks"]),
            "--repo-truth-path",
            str(fixture["repo_truth"]),
            "--registry-path",
            str(fixture["registry"]),
            "--adapter-path",
            str(fixture["adapter"]),
            "--route-path",
            str(fixture["route"]),
            "--unit-test-path",
            str(fixture["unit_test"]),
            "--backend-test-path",
            str(fixture["backend_test"]),
            "--api-file-test-path",
            str(fixture["api_test"]),
            "--output-dir",
            str(output_dir),
        ],
        cwd=Path(__file__).resolve().parents[3],
        check=True,
    )

    availability_report = json.loads((output_dir / "akshare-market-function-availability.json").read_text(encoding="utf-8"))
    repo_truth_report = json.loads((output_dir / "akshare-market-repo-truth-gate.json").read_text(encoding="utf-8"))
    summary_report = json.loads((output_dir / "akshare-market-gates-summary.json").read_text(encoding="utf-8"))

    assert availability_report["import_ok"] is True
    assert availability_report["summary"]["available_count"] == 1
    assert availability_report["summary"]["missing_count"] == 0
    assert repo_truth_report["pass"] is True
    assert summary_report["pass"] is True
    assert summary_report["availability_exit_code"] == 0
    assert summary_report["repo_truth_exit_code"] == 0
    assert summary_report["summary"]["tracked_count"] == 1
    assert summary_report["summary"]["available_count"] == 1
    assert summary_report["summary"]["missing_count"] == 0
    assert summary_report["summary"]["retired_count"] == 0
    assert summary_report["summary"]["repo_truth_violation_count"] == 0


def test_run_akshare_market_gates_fails_when_repo_truth_drifts(tmp_path: Path):
    fixture = _write_wrapper_fixture(tmp_path, repo_truth_status="本地 `akshare` 未检出同名函数")
    output_dir = tmp_path / "reports"

    proc = subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/run_akshare_market_gates.py",
            "--module",
            "json",
            "--function",
            "dumps",
            "--manifest-json",
            str(fixture["manifest"]),
            "--tasks-path",
            str(fixture["tasks"]),
            "--repo-truth-path",
            str(fixture["repo_truth"]),
            "--registry-path",
            str(fixture["registry"]),
            "--adapter-path",
            str(fixture["adapter"]),
            "--route-path",
            str(fixture["route"]),
            "--unit-test-path",
            str(fixture["unit_test"]),
            "--backend-test-path",
            str(fixture["backend_test"]),
            "--api-file-test-path",
            str(fixture["api_test"]),
            "--output-dir",
            str(output_dir),
        ],
        cwd=Path(__file__).resolve().parents[3],
        check=False,
        capture_output=True,
        text=True,
    )

    summary_report = json.loads((output_dir / "akshare-market-gates-summary.json").read_text(encoding="utf-8"))

    assert proc.returncode == 1
    assert summary_report["pass"] is False
    assert summary_report["repo_truth_exit_code"] == 1
    assert summary_report["summary"]["repo_truth_violation_count"] == 1
