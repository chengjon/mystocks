from __future__ import annotations

import importlib.util
import logging
import sys
from enum import Enum
from pathlib import Path
from types import ModuleType


def load_advanced_analysis_module():
    module_path = Path("web/backend/app/api/advanced_analysis.py")
    module_name = "test_advanced_analysis_logging_module"

    fake_src = ModuleType("src")
    fake_advanced = ModuleType("src.advanced_analysis")
    fake_core = ModuleType("src.core")
    fake_monitoring = ModuleType("src.monitoring")

    class FakeAnalysisType(str, Enum):
        TECHNICAL = "technical"

    class FakeAdvancedAnalysisEngine:
        def __init__(self, *_args, **_kwargs):
            pass

        def comprehensive_analysis(self, *_args, **_kwargs):
            return {}

    class FakeUnifiedManager:
        def __init__(self, *_args, **_kwargs):
            pass

    class FakeAlertManager:
        def __init__(self, *_args, **_kwargs):
            pass

    fake_advanced.AdvancedAnalysisEngine = FakeAdvancedAnalysisEngine
    fake_advanced.AnalysisType = FakeAnalysisType
    fake_core.MyStocksUnifiedManager = FakeUnifiedManager
    fake_monitoring.AlertManager = FakeAlertManager

    previous = {
        "src": sys.modules.get("src"),
        "src.advanced_analysis": sys.modules.get("src.advanced_analysis"),
        "src.core": sys.modules.get("src.core"),
        "src.monitoring": sys.modules.get("src.monitoring"),
        module_name: sys.modules.get(module_name),
    }

    sys.modules["src"] = fake_src
    sys.modules["src.advanced_analysis"] = fake_advanced
    sys.modules["src.core"] = fake_core
    sys.modules["src.monitoring"] = fake_monitoring

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    for name, previous_module in previous.items():
        if previous_module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous_module

    return module


def test_advanced_analysis_source_contains_no_print_statements():
    source = Path("web/backend/app/api/advanced_analysis.py").read_text(encoding="utf-8")

    assert "print(" not in source


async def test_comprehensive_background_task_logs_success(caplog):
    module = load_advanced_analysis_module()
    module.analysis_engine.comprehensive_analysis = lambda *_args, **_kwargs: {"technical": {}, "signals": {}}

    with caplog.at_level(logging.INFO, logger=module.__name__):
        await module._execute_comprehensive_analysis_async("600519", None, {})

    assert any("Comprehensive analysis completed" in record.getMessage() for record in caplog.records)


async def test_batch_background_task_logs_failures(caplog):
    module = load_advanced_analysis_module()

    def raise_error(*_args, **_kwargs):
        raise RuntimeError("engine down")

    module.analysis_engine.comprehensive_analysis = raise_error

    with caplog.at_level(logging.ERROR, logger=module.__name__):
        await module._execute_batch_analysis_async(["600519"], None, {}, "normal")

    assert any("Batch analysis failed for" in record.getMessage() for record in caplog.records)
