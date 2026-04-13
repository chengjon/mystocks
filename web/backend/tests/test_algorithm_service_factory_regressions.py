from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path


def _import_algorithm_service_module():
    backend_root = Path("web/backend").resolve()
    backend_root_str = str(backend_root)
    if backend_root_str not in sys.path:
        sys.path.insert(0, backend_root_str)

    sys.modules.pop("app.services.algorithm_service", None)
    return importlib.import_module("app.services.algorithm_service")


def test_algorithm_service_module_imports_with_framework_enabled():
    module = _import_algorithm_service_module()

    assert module.ALGORITHMS_AVAILABLE is True
    assert module.AlgorithmFactory is not None


def test_algorithm_factory_resolves_split_algorithm_classes():
    module = _import_algorithm_service_module()
    factory = module.AlgorithmFactory()

    resolved_classes = {
        module.AlgorithmType.SVM: asyncio.run(factory._get_algorithm_class(module.AlgorithmType.SVM)),
        module.AlgorithmType.KNUTH_MORRIS_PRATT: asyncio.run(
            factory._get_algorithm_class(module.AlgorithmType.KNUTH_MORRIS_PRATT)
        ),
        module.AlgorithmType.BOYER_MOORE_HORSPOOL: asyncio.run(
            factory._get_algorithm_class(module.AlgorithmType.BOYER_MOORE_HORSPOOL)
        ),
        module.AlgorithmType.AHO_CORASICK: asyncio.run(factory._get_algorithm_class(module.AlgorithmType.AHO_CORASICK)),
    }

    assert resolved_classes[module.AlgorithmType.SVM].__name__ == "SVMAlgorithm"
    assert resolved_classes[module.AlgorithmType.KNUTH_MORRIS_PRATT].__name__ == "KMPAlgorithm"
    assert resolved_classes[module.AlgorithmType.BOYER_MOORE_HORSPOOL].__name__ == "BMHAlgorithm"
    assert resolved_classes[module.AlgorithmType.AHO_CORASICK].__name__ == "AhoCorasickAlgorithm"
