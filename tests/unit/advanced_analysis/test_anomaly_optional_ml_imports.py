from __future__ import annotations

import builtins
import importlib.util
from pathlib import Path


def test_anomaly_dataclasses_exports_isolation_forest_when_ml_libraries_are_missing(monkeypatch):
    real_import = builtins.__import__

    def block_ml_imports(name, *args, **kwargs):
        if name.startswith(("cuml", "sklearn")):
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", block_ml_imports)

    module_path = Path("src/advanced_analysis/anomaly/dataclasses.py")
    spec = importlib.util.spec_from_file_location("anomaly_dataclasses_without_ml", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    assert module.GPU_AVAILABLE is False
    assert module.IsolationForest is None
