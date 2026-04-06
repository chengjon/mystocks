from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import yaml

from tests.api.file_tests import ContractValidator


def test_file_test_contract_validator_defaults_to_runtime_openapi(monkeypatch) -> None:
    runtime_spec = {
        "openapi": "3.1.0",
        "paths": {
            "/api/runtime": {
                "get": {
                    "responses": {
                        "200": {
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

    monkeypatch.setitem(sys.modules, "app.main", types.SimpleNamespace(app=types.SimpleNamespace(openapi=lambda: runtime_spec)))

    validator = ContractValidator()

    assert validator.load_contract_spec("tests/api/file_tests/test_market_api.py") == runtime_spec


def test_file_test_contract_validator_allows_explicit_spec_override(monkeypatch, tmp_path: Path) -> None:
    spec_path = tmp_path / "explicit-openapi.json"
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
    spec_path.write_text(json.dumps(explicit_spec), encoding="utf-8")
    monkeypatch.setitem(
        sys.modules,
        "app.main",
        types.SimpleNamespace(app=types.SimpleNamespace(openapi=lambda: (_ for _ in ()).throw(AssertionError("runtime app should not be used")))),
    )

    validator = ContractValidator()

    assert validator.load_contract_spec("tests/api/file_tests/test_market_api.py", spec_path=str(spec_path)) == explicit_spec


def test_file_test_contract_validator_supports_yaml_override(monkeypatch, tmp_path: Path) -> None:
    spec_path = tmp_path / "explicit-openapi.yaml"
    explicit_spec = {
        "openapi": "3.1.0",
        "paths": {
            "/api/yaml": {
                "get": {
                    "responses": {
                        "200": {
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
    monkeypatch.setitem(
        sys.modules,
        "app.main",
        types.SimpleNamespace(app=types.SimpleNamespace(openapi=lambda: (_ for _ in ()).throw(AssertionError("runtime app should not be used")))),
    )

    validator = ContractValidator()

    assert validator.load_contract_spec("tests/api/file_tests/test_market_api.py", spec_path=str(spec_path)) == explicit_spec
