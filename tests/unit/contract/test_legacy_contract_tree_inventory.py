from __future__ import annotations

import ast
from pathlib import Path


LEGACY_CONTRACT_ROOT = Path(__file__).resolve().parents[2] / "contract"


def _contains_pytest_cases(path: Path) -> bool:
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            return True

        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name.startswith("test_"):
                    return True

    return False


def test_legacy_contract_tree_keeps_only_support_modules() -> None:
    legacy_pytest_files = sorted(
        str(path.relative_to(LEGACY_CONTRACT_ROOT))
        for path in LEGACY_CONTRACT_ROOT.rglob("test_*.py")
        if _contains_pytest_cases(path)
    )

    assert legacy_pytest_files == []
