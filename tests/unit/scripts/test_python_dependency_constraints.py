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


def test_runtime_requirements_explicitly_declare_pyjwt_for_backend_auth() -> None:
    runtime_requirements = [
        PROJECT_ROOT / "requirements.txt",
        PROJECT_ROOT / "web" / "backend" / "requirements.txt",
    ]

    for requirement_path in runtime_requirements:
        _extract_requirement(requirement_path, "PyJWT")


def test_backend_runtime_requirements_declare_apscheduler_for_cache_eviction() -> None:
    backend_requirements = PROJECT_ROOT / "web" / "backend" / "requirements.txt"

    _extract_requirement(backend_requirements, "APScheduler")


def test_runtime_requirements_explicitly_declare_aiohttp_for_backend_startup() -> None:
    runtime_requirements = [
        PROJECT_ROOT / "requirements.txt",
        PROJECT_ROOT / "config" / "requirements.txt",
        PROJECT_ROOT / "web" / "backend" / "requirements.txt",
    ]

    for requirement_path in runtime_requirements:
        _extract_requirement(requirement_path, "aiohttp")


def test_runtime_requirements_raise_requests_to_safe_floor() -> None:
    runtime_requirements = [
        PROJECT_ROOT / "requirements.txt",
        PROJECT_ROOT / "config" / "requirements.txt",
        PROJECT_ROOT / "web" / "backend" / "requirements.txt",
    ]

    for requirement_path in runtime_requirements:
        requests_line = _extract_requirement(requirement_path, "requests")
        assert requests_line in {"requests>=2.32.4", "requests==2.32.4"}


def test_runtime_requirements_raise_python_multipart_to_safe_floor() -> None:
    runtime_requirements = [
        PROJECT_ROOT / "requirements.txt",
        PROJECT_ROOT / "config" / "requirements.txt",
        PROJECT_ROOT / "web" / "backend" / "requirements.txt",
    ]

    for requirement_path in runtime_requirements:
        multipart_line = _extract_requirement(requirement_path, "python-multipart")
        assert multipart_line in {"python-multipart>=0.0.22", "python-multipart==0.0.22"}
