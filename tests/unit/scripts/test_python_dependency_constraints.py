from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _extract_requirement(path: Path, package_name: str) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith(f"{package_name}>=") or stripped.startswith(f"{package_name}=="):
            return stripped
    raise AssertionError(f"missing requirement for {package_name} in {path}")


def test_baostock_runtime_requirement_does_not_exceed_frozen_baseline() -> None:
    runtime_requirements = [
        PROJECT_ROOT / "requirements.txt",
        PROJECT_ROOT / "config" / "requirements.txt",
    ]
    frozen_requirements = PROJECT_ROOT / "config" / "requirements_freeze.txt"

    frozen_line = _extract_requirement(frozen_requirements, "baostock")
    frozen_match = re.search(r"baostock==([0-9.]+)", frozen_line)
    assert frozen_match is not None
    frozen_version = frozen_match.group(1)

    for requirement_path in runtime_requirements:
        runtime_line = _extract_requirement(requirement_path, "baostock")
        assert runtime_line == f"baostock>={frozen_version}"


def test_runtime_requirements_use_installable_datamodel_code_generator_package() -> None:
    runtime_requirements = [
        PROJECT_ROOT / "requirements.txt",
        PROJECT_ROOT / "config" / "requirements.txt",
    ]

    for requirement_path in runtime_requirements:
        content = requirement_path.read_text(encoding="utf-8")
        assert "datamodel-codegen==0.0.1" not in content
        assert "datamodel-code-generator" in content


def test_ci_type_check_workflow_avoids_types_all_meta_package() -> None:
    workflow = PROJECT_ROOT / ".github" / "workflows" / "ci-cd-with-type-checking.yml"
    content = workflow.read_text(encoding="utf-8")

    assert "pip install mypy types-all" not in content
    assert "types-requests" in content
    assert "types-PyYAML" in content
