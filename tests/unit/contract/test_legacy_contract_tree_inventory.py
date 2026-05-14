from __future__ import annotations

import ast
from pathlib import Path


LEGACY_CONTRACT_ROOT = Path(__file__).resolve().parents[2] / "contract"

ALLOWED_LEGACY_WRAPPERS = {
    "__init__.py",
    "contract_engine.py",
    "contract_generator.py",
    "contract_test_executor.py",
    "contract_validator.py",
    "executor.py",
    "models.py",
    "report_generator.py",
    "reverse_contract_generator.py",
    "test_contract_validator/__init__.py",
    "test_contract_validator/contract_validator.py",
    "test_contract_validator/contract_violation_type.py",
}

_WRAPPER_NODE_TYPES = (
    ast.Expr,
    ast.Import,
    ast.ImportFrom,
    ast.Assign,
    ast.AnnAssign,
    ast.If,
)


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


def _is_thin_wrapper(path: Path) -> bool:
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    for node in module.body:
        if isinstance(node, _WRAPPER_NODE_TYPES):
            continue
        if path.name == "__init__.py" and isinstance(node, ast.FunctionDef) and node.name == "__getattr__":
            continue
        return False

    return True


def test_legacy_contract_tree_keeps_only_support_modules() -> None:
    legacy_python_files = sorted(
        str(path.relative_to(LEGACY_CONTRACT_ROOT)) for path in LEGACY_CONTRACT_ROOT.rglob("*.py")
    )
    legacy_pytest_named_files = sorted(
        str(path.relative_to(LEGACY_CONTRACT_ROOT)) for path in LEGACY_CONTRACT_ROOT.rglob("test_*.py")
    )
    legacy_pytest_files = sorted(
        str(path.relative_to(LEGACY_CONTRACT_ROOT))
        for path in LEGACY_CONTRACT_ROOT.rglob("test_*.py")
        if _contains_pytest_cases(path)
    )

    assert legacy_python_files == sorted(ALLOWED_LEGACY_WRAPPERS)
    assert all(_is_thin_wrapper(LEGACY_CONTRACT_ROOT / path) for path in legacy_python_files)
    assert legacy_pytest_named_files == []
    assert legacy_pytest_files == []
