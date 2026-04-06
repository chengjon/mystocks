from __future__ import annotations

import os
import sys
import types
from pathlib import Path

import yaml


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../web/backend"))

from tests.contract.contract_engine import ContractTestEngine
from tests.contract.models import ContractTestConfig


def test_contract_test_engine_defaults_to_runtime_openapi(monkeypatch, tmp_path: Path) -> None:
    runtime_spec = {
        "openapi": "3.1.0",
        "paths": {
            "/api/runtime": {
                "get": {
                    "description": "Runtime-generated endpoint",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"status": {"type": "string"}},
                                    }
                                }
                            }
                        }
                    },
                }
            }
        },
    }

    monkeypatch.setitem(sys.modules, "app.main", types.SimpleNamespace(app=types.SimpleNamespace(openapi=lambda: runtime_spec)))

    engine = ContractTestEngine(
        ContractTestConfig(
            test_data_path=str(tmp_path / "test-data"),
            report_output_path=str(tmp_path / "reports"),
        )
    )

    assert engine.openapi_spec == runtime_spec
    assert engine.openapi_spec_source == "runtime"
    assert engine.openapi_spec_error is None
    discovered = engine.discover_tests_from_openapi()
    assert [case.name for case in discovered] == ["GET /api/runtime"]


def test_contract_test_engine_allows_explicit_openapi_file_override(monkeypatch, tmp_path: Path) -> None:
    spec_path = tmp_path / "explicit-openapi.yaml"
    explicit_spec = {
        "openapi": "3.1.0",
        "paths": {
            "/api/override": {
                "post": {
                    "description": "Explicit file override",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"ok": {"type": "boolean"}},
                                    }
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    spec_path.write_text(yaml.safe_dump(explicit_spec, sort_keys=False), encoding="utf-8")
    monkeypatch.setitem(
        sys.modules,
        "app.main",
        types.SimpleNamespace(app=types.SimpleNamespace(openapi=lambda: (_ for _ in ()).throw(AssertionError("runtime app should not be used")))),
    )

    engine = ContractTestEngine(
        ContractTestConfig(
            openapi_spec_path=str(spec_path),
            test_data_path=str(tmp_path / "test-data"),
            report_output_path=str(tmp_path / "reports"),
        )
    )

    assert engine.openapi_spec == explicit_spec
    assert engine.openapi_spec_source == "explicit_file"
    assert engine.openapi_spec_error is None
    discovered = engine.discover_tests_from_openapi()
    assert [case.name for case in discovered] == ["POST /api/override"]


def test_contract_test_engine_marks_unavailable_when_runtime_openapi_cannot_load(tmp_path: Path) -> None:
    engine = ContractTestEngine(
        ContractTestConfig(
            test_data_path=str(tmp_path / "test-data"),
            report_output_path=str(tmp_path / "reports"),
        )
    )

    assert engine.openapi_spec_source == "unavailable"
    assert engine.openapi_spec_error
    assert engine.discover_tests_from_openapi() == []
