import json
import subprocess
from pathlib import Path


def _write_fixture_files(tmp_path: Path, repo_truth_hot_follow_status: str = "已实现", task_63_checked: bool = False) -> dict[str, Path]:
    manifest = [
        {
            "task_id": "6.1",
            "function_name": "stock_hot_follow_xq",
            "registry_key": "akshare_stock_hot_follow_xq",
            "adapter_method": "get_stock_hot_follow_xq",
            "route_fragment": "/stock/hot-follow/xq",
            "unit_test_token": "get_stock_hot_follow_xq",
            "backend_test_token": "/stock/hot-follow/xq",
            "api_test_token": "test_stock_hot_follow_xq_endpoint",
        },
        {
            "task_id": "6.3",
            "function_name": "stock_news_main_em",
            "registry_key": "akshare_stock_news_main_em",
            "adapter_method": "get_stock_news_main_em",
            "route_fragment": "/stock/news-main/em",
            "unit_test_token": "get_stock_news_main_em",
            "backend_test_token": "/stock/news-main/em",
            "api_test_token": "test_stock_news_main_em_endpoint",
        },
    ]
    availability = {
        "module": "akshare",
        "import_ok": True,
        "functions": [
            {"name": "stock_hot_follow_xq", "available": True},
            {"name": "stock_news_main_em", "available": False},
        ],
        "summary": {
            "tracked_count": 2,
            "available_count": 1,
            "missing_count": 1,
            "available_functions": ["stock_hot_follow_xq"],
            "missing_functions": ["stock_news_main_em"],
        },
    }

    checked_marker = "x" if task_63_checked else " "
    tasks_path = tmp_path / "tasks.md"
    tasks_path.write_text(
        "\n".join(
            [
                "- [x] 6.1 实现股票热度数据 (akshare.stock_hot_follow_xq)",
                f"- [{checked_marker}] 6.3 实现财经内容精选 (akshare.stock_news_main_em)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    repo_truth_path = tmp_path / "repo_truth.md"
    repo_truth_path.write_text(
        "\n".join(
            [
                "| 6.1 | `stock_hot_follow_xq` | `/api/akshare/market/stock/hot-follow/xq` | `get_stock_hot_follow_xq()` | 已实现 |",
                f"| 6.3 | `stock_news_main_em` | - | - | 本地 `akshare` 未检出同名函数 |",
            ]
        ).replace("本地 `akshare` 未检出同名函数", repo_truth_hot_follow_status if repo_truth_hot_follow_status != "已实现" else "本地 `akshare` 未检出同名函数")
        + "\n",
        encoding="utf-8",
    )
    if repo_truth_hot_follow_status != "已实现":
        repo_truth_path.write_text(
            "\n".join(
                [
                    f"| 6.1 | `stock_hot_follow_xq` | `/api/akshare/market/stock/hot-follow/xq` | `get_stock_hot_follow_xq()` | {repo_truth_hot_follow_status} |",
                    "| 6.3 | `stock_news_main_em` | - | - | 本地 `akshare` 未检出同名函数 |",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    registry_path = tmp_path / "registry.yaml"
    registry_path.write_text("akshare_stock_hot_follow_xq:\n  status: active\n", encoding="utf-8")

    adapter_path = tmp_path / "stock_sentiment.py"
    adapter_path.write_text("async def get_stock_hot_follow_xq(symbol='最热门'):\n    return None\n", encoding="utf-8")

    route_path = tmp_path / "sentiment_monitor.py"
    route_path.write_text('@router.get("/stock/hot-follow/xq")\nasync def get_stock_hot_follow_xq():\n    return {}\n', encoding="utf-8")

    unit_test_path = tmp_path / "unit_test.py"
    unit_test_path.write_text("def test_get_stock_hot_follow_xq():\n    assert True\n", encoding="utf-8")

    backend_test_path = tmp_path / "backend_test.py"
    backend_test_path.write_text('response = client.get("/api/akshare/market/stock/hot-follow/xq")\n', encoding="utf-8")

    api_test_path = tmp_path / "api_test.py"
    api_test_path.write_text("def test_stock_hot_follow_xq_endpoint():\n    assert True\n", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    availability_path = tmp_path / "availability.json"
    availability_path.write_text(json.dumps(availability, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "manifest": manifest_path,
        "availability": availability_path,
        "tasks": tasks_path,
        "repo_truth": repo_truth_path,
        "registry": registry_path,
        "adapter": adapter_path,
        "route": route_path,
        "unit_test": unit_test_path,
        "backend_test": backend_test_path,
        "api_test": api_test_path,
    }


def test_validate_akshare_market_repo_truth_passes_on_aligned_fixture(tmp_path: Path):
    fixture = _write_fixture_files(tmp_path)
    output_path = tmp_path / "repo_truth_gate.json"

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/validate_akshare_market_repo_truth.py",
            "--manifest-json",
            str(fixture["manifest"]),
            "--availability-report",
            str(fixture["availability"]),
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
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[3],
        check=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["pass"] is True
    assert payload["summary"]["tracked_count"] == 2
    assert payload["summary"]["violation_count"] == 0


def test_validate_akshare_market_repo_truth_fails_on_repo_truth_drift(tmp_path: Path):
    fixture = _write_fixture_files(tmp_path, repo_truth_hot_follow_status="本地 `akshare` 未检出同名函数", task_63_checked=True)
    output_path = tmp_path / "repo_truth_gate.json"

    proc = subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/validate_akshare_market_repo_truth.py",
            "--manifest-json",
            str(fixture["manifest"]),
            "--availability-report",
            str(fixture["availability"]),
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
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[3],
        check=False,
        capture_output=True,
        text=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert proc.returncode == 1
    assert payload["pass"] is False
    assert any(item["function_name"] == "stock_hot_follow_xq" for item in payload["violations"])
    assert any(item["function_name"] == "stock_news_main_em" for item in payload["violations"])


def test_validate_akshare_market_repo_truth_accepts_dt_pool_mapped_status(tmp_path: Path):
    manifest = [
        {
            "task_id": "6.5",
            "function_name": "stock_dt_pool_em",
            "registry_key": "akshare_stock_dt_pool_em",
            "adapter_method": "get_stock_dt_pool_em",
            "route_fragment": "/stock/dt-pool/em",
            "unit_test_token": "test_get_stock_dt_pool_em_normalizes_columns",
            "backend_test_token": "test_stock_dt_pool_em_route_returns_success_payload",
            "api_test_token": "test_stock_dt_pool_em_endpoint",
        }
    ]
    availability = {
        "module": "akshare",
        "import_ok": True,
        "functions": [
            {
                "name": "stock_dt_pool_em",
                "available": True,
                "target_available": False,
                "resolution_status": "mapped",
                "resolved_function": "stock_zt_pool_dtgc_em",
            }
        ],
        "summary": {
            "tracked_count": 1,
            "available_count": 1,
            "missing_count": 0,
            "available_functions": ["stock_dt_pool_em"],
            "missing_functions": [],
        },
    }

    tasks_path = tmp_path / "tasks.md"
    tasks_path.write_text("- [x] 6.5 实现跌停板行情 (akshare.stock_dt_pool_em)\n", encoding="utf-8")

    repo_truth_path = tmp_path / "repo_truth.md"
    repo_truth_path.write_text(
        "| 6.5 | `stock_dt_pool_em` | `/api/akshare/market/stock/dt-pool/em` | `get_stock_dt_pool_em()` | 已实现（官方改名映射：stock_zt_pool_dtgc_em） |\n",
        encoding="utf-8",
    )

    registry_path = tmp_path / "registry.yaml"
    registry_path.write_text("akshare_stock_dt_pool_em:\n  status: active\n", encoding="utf-8")

    adapter_path = tmp_path / "stock_sentiment.py"
    adapter_path.write_text("async def get_stock_dt_pool_em(date='20241011'):\n    return None\n", encoding="utf-8")

    route_path = tmp_path / "sentiment_monitor.py"
    route_path.write_text('@router.get("/stock/dt-pool/em")\nasync def get_stock_dt_pool_em():\n    return {}\n', encoding="utf-8")

    unit_test_path = tmp_path / "unit_test.py"
    unit_test_path.write_text("def test_get_stock_dt_pool_em_normalizes_columns():\n    assert True\n", encoding="utf-8")

    backend_test_path = tmp_path / "backend_test.py"
    backend_test_path.write_text("def test_stock_dt_pool_em_route_returns_success_payload():\n    assert True\n", encoding="utf-8")

    api_test_path = tmp_path / "api_test.py"
    api_test_path.write_text("def test_stock_dt_pool_em_endpoint():\n    assert True\n", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    availability_path = tmp_path / "availability.json"
    availability_path.write_text(json.dumps(availability, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    output_path = tmp_path / "repo_truth_gate.json"
    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/validate_akshare_market_repo_truth.py",
            "--manifest-json",
            str(manifest_path),
            "--availability-report",
            str(availability_path),
            "--tasks-path",
            str(tasks_path),
            "--repo-truth-path",
            str(repo_truth_path),
            "--registry-path",
            str(registry_path),
            "--adapter-path",
            str(adapter_path),
            "--route-path",
            str(route_path),
            "--unit-test-path",
            str(unit_test_path),
            "--backend-test-path",
            str(backend_test_path),
            "--api-file-test-path",
            str(api_test_path),
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[3],
        check=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["pass"] is True
    assert payload["summary"]["tracked_count"] == 1
    assert payload["summary"]["violation_count"] == 0
    assert payload["functions"][0]["function_name"] == "stock_dt_pool_em"
    assert payload["functions"][0]["available"] is True


def test_validate_akshare_market_repo_truth_accepts_new_pool_mapped_status(tmp_path: Path):
    manifest = [
        {
            "task_id": "6.9",
            "function_name": "stock_new_em",
            "registry_key": "akshare_stock_new_em",
            "adapter_method": "get_stock_new_em",
            "route_fragment": "/stock/new/em",
            "unit_test_token": "test_get_stock_new_em_normalizes_columns",
            "backend_test_token": "test_stock_new_em_route_returns_success_payload",
            "api_test_token": "test_stock_new_em_endpoint",
        }
    ]
    availability = {
        "module": "akshare",
        "import_ok": True,
        "functions": [
            {
                "name": "stock_new_em",
                "available": True,
                "target_available": False,
                "resolution_status": "mapped",
                "resolved_function": "stock_zt_pool_sub_new_em",
            }
        ],
        "summary": {
            "tracked_count": 1,
            "available_count": 1,
            "missing_count": 0,
            "available_functions": ["stock_new_em"],
            "missing_functions": [],
        },
    }

    tasks_path = tmp_path / "tasks.md"
    tasks_path.write_text("- [x] 6.9 实现次新股池 (akshare.stock_new_em)\n", encoding="utf-8")

    repo_truth_path = tmp_path / "repo_truth.md"
    repo_truth_path.write_text(
        "| 6.9 | `stock_new_em` | `/api/akshare/market/stock/new/em` | `get_stock_new_em()` | 已实现（官方改名映射：stock_zt_pool_sub_new_em） |\n",
        encoding="utf-8",
    )

    registry_path = tmp_path / "registry.yaml"
    registry_path.write_text("akshare_stock_new_em:\n  status: active\n", encoding="utf-8")

    adapter_path = tmp_path / "stock_sentiment.py"
    adapter_path.write_text("async def get_stock_new_em(date='20241011'):\n    return None\n", encoding="utf-8")

    route_path = tmp_path / "sentiment_monitor.py"
    route_path.write_text('@router.get("/stock/new/em")\nasync def get_stock_new_em():\n    return {}\n', encoding="utf-8")

    unit_test_path = tmp_path / "unit_test.py"
    unit_test_path.write_text("def test_get_stock_new_em_normalizes_columns():\n    assert True\n", encoding="utf-8")

    backend_test_path = tmp_path / "backend_test.py"
    backend_test_path.write_text("def test_stock_new_em_route_returns_success_payload():\n    assert True\n", encoding="utf-8")

    api_test_path = tmp_path / "api_test.py"
    api_test_path.write_text("def test_stock_new_em_endpoint():\n    assert True\n", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    availability_path = tmp_path / "availability.json"
    availability_path.write_text(json.dumps(availability, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    output_path = tmp_path / "repo_truth_gate.json"
    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/validate_akshare_market_repo_truth.py",
            "--manifest-json",
            str(manifest_path),
            "--availability-report",
            str(availability_path),
            "--tasks-path",
            str(tasks_path),
            "--repo-truth-path",
            str(repo_truth_path),
            "--registry-path",
            str(registry_path),
            "--adapter-path",
            str(adapter_path),
            "--route-path",
            str(route_path),
            "--unit-test-path",
            str(unit_test_path),
            "--backend-test-path",
            str(backend_test_path),
            "--api-file-test-path",
            str(api_test_path),
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[3],
        check=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["pass"] is True
    assert payload["summary"]["tracked_count"] == 1
    assert payload["summary"]["violation_count"] == 0
    assert payload["functions"][0]["function_name"] == "stock_new_em"
    assert payload["functions"][0]["available"] is True
