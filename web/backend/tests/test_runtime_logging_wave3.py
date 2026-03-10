from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path

import pytest

SOURCE_FILES = [
    "web/backend/app/core/data_source_manager.py",
    "web/backend/app/core/incremental_snapshot.py",
    "web/backend/app/core/strategy_validator.py",
]


def _load_module(module_path: str, module_name: str):
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, Path(module_path))
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("module_path", SOURCE_FILES)
def test_runtime_core_modules_source_contains_no_print_statements(module_path: str):
    source = Path(module_path).read_text(encoding="utf-8")

    assert "print(" not in source


def test_data_source_manager_logs_default_config_saved(caplog, tmp_path):
    module = _load_module(
        "web/backend/app/core/data_source_manager.py",
        "test_data_source_manager_logging_wave3_module",
    )
    config_path = tmp_path / "config" / "data_sources.json"

    with caplog.at_level(logging.INFO, logger=module.__name__):
        module.init_default_config(str(config_path))

    assert config_path.exists()
    assert any("Default data source config saved" in record.getMessage() for record in caplog.records)


def test_incremental_snapshot_logs_create_base_failures(caplog, monkeypatch, tmp_path):
    module = _load_module(
        "web/backend/app/core/incremental_snapshot.py",
        "test_incremental_snapshot_logging_wave3_module",
    )
    manager = module.IncrementalDataManager(base_dir=str(tmp_path))

    def raise_dump_error(*_args, **_kwargs):
        raise RuntimeError("disk full")

    monkeypatch.setattr(module.pickle, "dump", raise_dump_error)

    with caplog.at_level(logging.ERROR, logger=module.__name__):
        result = manager.create_base_snapshot("prices", {"600519": {"close": 1234}})

    assert result is False
    assert any("Failed to create base snapshot" in record.getMessage() for record in caplog.records)


def test_strategy_validator_logs_benchmark_registration(caplog):
    module = _load_module(
        "web/backend/app/core/strategy_validator.py",
        "test_strategy_validator_logging_wave3_module",
    )
    validator = module.StrategyValidator()
    benchmark = module.BenchmarkResult(
        strategy_name="demo",
        total_return=0.1,
        annualized_return=0.1,
        max_drawdown=0.05,
        sharpe_ratio=1.2,
        win_rate=0.55,
        total_trades=12,
        avg_profit_per_trade=0.02,
        hash="abc",
    )

    with caplog.at_level(logging.INFO, logger=module.__name__):
        validator.register_benchmark("demo", benchmark)

    assert any("已注册策略" in record.getMessage() for record in caplog.records)
