from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _import_modules(path: str) -> list[str]:
    tree = ast.parse((PROJECT_ROOT / path).read_text(encoding="utf-8"))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.append(node.module)
    return modules


def test_active_validation_consumers_use_canonical_validation_package() -> None:
    checked_paths = [
        "web/backend/app/core/validators.py",
        "web/backend/app/core/error_codes.py",
    ]

    legacy_imports = {
        path: [module for module in _import_modules(path) if module == "app.core.validation_messages"]
        for path in checked_paths
    }

    assert legacy_imports == {path: [] for path in checked_paths}
