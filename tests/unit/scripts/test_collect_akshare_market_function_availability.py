import json
import subprocess
from pathlib import Path

from scripts.dev.quality_gate.collect_akshare_market_function_availability import collect_availability


def test_collect_akshare_market_function_availability_writes_snapshot(tmp_path: Path):
    output_path = tmp_path / "akshare-market-availability.json"

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/collect_akshare_market_function_availability.py",
            "--module",
            "json",
            "--function",
            "dumps",
            "--function",
            "loads",
            "--function",
            "not_real",
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[3],
        check=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["module"] == "json"
    assert payload["import_ok"] is True
    assert payload["summary"]["available_count"] == 2
    assert payload["summary"]["missing_count"] == 1
    assert payload["summary"]["missing_functions"] == ["not_real"]


def test_collect_akshare_market_function_availability_fails_when_module_is_missing(tmp_path: Path):
    output_path = tmp_path / "akshare-market-availability.json"

    proc = subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/collect_akshare_market_function_availability.py",
            "--module",
            "module_that_does_not_exist",
            "--function",
            "anything",
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[3],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 1
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["import_ok"] is False
    assert payload["module"] == "module_that_does_not_exist"
    assert "No module named" in payload["import_error"]


def test_collect_akshare_market_function_availability_surfaces_help_candidates(monkeypatch):
    class FakeModule:
        __version__ = "test-version"

        @staticmethod
        def stock_news_main_cx():
            return None

        @staticmethod
        def stock_zt_pool_dtgc_em(date: str = "20241011"):
            return None

        @staticmethod
        def stock_zh_a_new_em():
            return None

        @staticmethod
        def stock_zt_pool_sub_new_em():
            return None

    def fake_import(name: str):
        assert name == "fake_akshare"
        return FakeModule

    monkeypatch.setattr("scripts.dev.quality_gate.collect_akshare_market_function_availability.importlib.import_module", fake_import)

    payload, exit_code = collect_availability(
        module_name="fake_akshare",
        function_names=["stock_news_main_em", "stock_dt_pool_em", "stock_new_em"],
    )

    assert exit_code == 0
    rows = {row["name"]: row for row in payload["functions"]}
    assert rows["stock_news_main_em"]["available"] is False
    assert rows["stock_news_main_em"]["help_candidates"] == ["stock_news_main_cx"]
    assert rows["stock_dt_pool_em"]["available"] is True
    assert rows["stock_dt_pool_em"]["target_available"] is False
    assert rows["stock_dt_pool_em"]["resolution_status"] == "mapped"
    assert rows["stock_dt_pool_em"]["resolved_function"] == "stock_zt_pool_dtgc_em"
    assert rows["stock_new_em"]["help_candidates"] == ["stock_zt_pool_sub_new_em"]
    assert payload["summary"]["help_candidate_functions"] == {
        "stock_news_main_em": ["stock_news_main_cx"],
        "stock_new_em": ["stock_zt_pool_sub_new_em"],
    }


def test_collect_akshare_market_function_availability_marks_dt_pool_as_mapped(monkeypatch):
    class FakeModule:
        __version__ = "test-version"

        @staticmethod
        def stock_zt_pool_dtgc_em(date: str = "20241011"):
            return None

    def fake_import(name: str):
        assert name == "fake_akshare"
        return FakeModule

    monkeypatch.setattr("scripts.dev.quality_gate.collect_akshare_market_function_availability.importlib.import_module", fake_import)

    payload, exit_code = collect_availability(
        module_name="fake_akshare",
        function_names=["stock_dt_pool_em"],
    )

    assert exit_code == 0
    row = payload["functions"][0]
    assert row["name"] == "stock_dt_pool_em"
    assert row["available"] is True
    assert row["target_available"] is False
    assert row["resolution_status"] == "mapped"
    assert row["resolved_function"] == "stock_zt_pool_dtgc_em"
    assert payload["summary"]["available_count"] == 1
    assert payload["summary"]["missing_count"] == 0


def test_collect_akshare_market_function_availability_marks_strong_pool_as_mapped(monkeypatch):
    class FakeModule:
        __version__ = "test-version"

        @staticmethod
        def stock_zt_pool_strong_em(date: str = "20241011"):
            return None

    def fake_import(name: str):
        assert name == "fake_akshare"
        return FakeModule

    monkeypatch.setattr("scripts.dev.quality_gate.collect_akshare_market_function_availability.importlib.import_module", fake_import)

    payload, exit_code = collect_availability(
        module_name="fake_akshare",
        function_names=["stock_strong_pool_em"],
    )

    assert exit_code == 0
    row = payload["functions"][0]
    assert row["name"] == "stock_strong_pool_em"
    assert row["available"] is True
    assert row["target_available"] is False
    assert row["resolution_status"] == "mapped"
    assert row["resolved_function"] == "stock_zt_pool_strong_em"
    assert payload["summary"]["available_count"] == 1
    assert payload["summary"]["missing_count"] == 0
