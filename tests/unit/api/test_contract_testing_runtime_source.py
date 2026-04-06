from __future__ import annotations

import os
import sys
import types
from pathlib import Path

import yaml


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../web/backend"))

from app.api.contract.services import contract_testing


def test_contract_validator_fixture_uses_runtime_openapi(monkeypatch) -> None:
    runtime_spec = {"openapi": "3.1.0", "paths": {"/api/runtime": {"get": {"responses": {"200": {}}}}}}
    captured: dict[str, object] = {}

    def _build_validator(spec):
        captured["spec"] = spec
        return types.SimpleNamespace(spec=spec)

    def _unexpected_open(*args, **kwargs):
        raise AssertionError("contract_validator should not read static OpenAPI files by default")

    monkeypatch.setitem(sys.modules, "app.main", types.SimpleNamespace(app=types.SimpleNamespace(openapi=lambda: runtime_spec)))
    monkeypatch.setattr(contract_testing, "ContractValidator", _build_validator)
    monkeypatch.setattr("builtins.open", _unexpected_open)

    generator = contract_testing.contract_validator.__wrapped__()

    assert next(generator).spec == runtime_spec
    assert captured["spec"] == runtime_spec


def test_generate_contract_tests_uses_runtime_openapi_by_default(monkeypatch) -> None:
    runtime_spec = {"openapi": "3.1.0", "paths": {"/api/runtime": {"get": {"responses": {"200": {}}}}}}
    captured: dict[str, object] = {}

    class _FakeValidator:
        def __init__(self, spec):
            captured["spec"] = spec

        def get_endpoint_schema_paths(self):
            return [
                {
                    "path": "/api/runtime",
                    "method": "GET",
                    "responses": {"200": {"type": "object"}},
                    "description": "Runtime contract",
                    "summary": "Runtime",
                }
            ]

    def _unexpected_open(*args, **kwargs):
        raise AssertionError("generate_contract_tests should not read static OpenAPI files by default")

    monkeypatch.setitem(sys.modules, "app.main", types.SimpleNamespace(app=types.SimpleNamespace(openapi=lambda: runtime_spec)))
    monkeypatch.setattr(contract_testing, "ContractValidator", _FakeValidator)
    monkeypatch.setattr("builtins.open", _unexpected_open)

    test_cases = contract_testing.generate_contract_tests()

    assert captured["spec"] == runtime_spec
    assert test_cases == [
        {
            "test_name": "test_get__api_runtime_200_conforms",
            "parametrize": ["/api/runtime", "GET", "200"],
            "description": "Runtime contract",
            "summary": "Runtime",
        }
    ]


def test_generate_contract_tests_allows_explicit_spec_path_override(monkeypatch, tmp_path: Path) -> None:
    spec_path = tmp_path / "openapi.yaml"
    explicit_spec = {
        "openapi": "3.1.0",
        "paths": {
            "/api/override": {
                "post": {
                    "responses": {
                        "201": {
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            }
                        }
                    }
                }
            }
        },
    }
    spec_path.write_text(yaml.safe_dump(explicit_spec, sort_keys=False), encoding="utf-8")
    captured: dict[str, object] = {}

    class _FakeValidator:
        def __init__(self, spec):
            captured["spec"] = spec

        def get_endpoint_schema_paths(self):
            return [
                {
                    "path": "/api/override",
                    "method": "POST",
                    "responses": {"201": {"type": "object"}},
                    "description": "Explicit override",
                    "summary": "Explicit",
                }
            ]

    monkeypatch.setitem(
        sys.modules,
        "app.main",
        types.SimpleNamespace(app=types.SimpleNamespace(openapi=lambda: (_ for _ in ()).throw(AssertionError("runtime app should not be used")))),
    )
    monkeypatch.setattr(contract_testing, "ContractValidator", _FakeValidator)

    test_cases = contract_testing.generate_contract_tests(spec_path=str(spec_path))

    assert captured["spec"] == explicit_spec
    assert test_cases == [
        {
            "test_name": "test_post__api_override_201_conforms",
            "parametrize": ["/api/override", "POST", "201"],
            "description": "Explicit override",
            "summary": "Explicit",
        }
    ]
