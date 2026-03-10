from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path

import pytest

SOURCE_FILES = [
    "web/backend/app/core/config.py",
    "web/backend/app/services/tdx_parser_service.py",
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
def test_runtime_modules_source_contains_no_print_statements(module_path: str):
    source = Path(module_path).read_text(encoding="utf-8")

    assert "print(" not in source


def test_tdx_parser_service_logs_read_failures(caplog, tmp_path):
    module = _load_module(
        "web/backend/app/services/tdx_parser_service.py",
        "test_tdx_parser_service_logging_wave4_module",
    )
    service = module.TdxDataService(data_dir=str(tmp_path))

    target_file = tmp_path / "sh" / "lday" / "sh600519.day"
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_bytes(b"dummy")

    def raise_parse_error(*_args, **_kwargs):
        raise RuntimeError("parse failed")

    service.parser.read_tdx_day_file = raise_parse_error

    with caplog.at_level(logging.ERROR, logger=module.__name__):
        result = service.get_stock_data("600519", market="sh")

    assert result is None
    assert any("读取股票数据失败" in record.getMessage() for record in caplog.records)
