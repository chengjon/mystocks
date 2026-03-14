from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = PROJECT_ROOT / "governance" / "function-tree" / "catalog.yaml"
SCHEMA_PATH = PROJECT_ROOT / "governance" / "function-tree" / "schema.json"
SCOPE_GATE_PATH = PROJECT_ROOT / "governance" / "mainline" / "scripts" / "mainline_scope_gate.py"


def load_catalog() -> dict:
    assert CATALOG_PATH.exists(), f"missing catalog: {CATALOG_PATH}"
    payload = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def load_schema() -> dict:
    assert SCHEMA_PATH.exists(), f"missing schema: {SCHEMA_PATH}"
    payload = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def load_scope_gate_module():
    spec = importlib.util.spec_from_file_location("mainline_scope_gate", SCOPE_GATE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_catalog_matches_schema() -> None:
    schema = load_schema()
    catalog = load_catalog()

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(catalog), key=lambda item: list(item.absolute_path))
    assert errors == []


def test_catalog_contains_business_and_meta_domains() -> None:
    catalog = load_catalog()

    domains = catalog["domains"]
    domain_ids = {domain["id"] for domain in domains}
    mirrored_domains = [domain for domain in domains if domain.get("mirror_to_function_tree")]

    assert "meta-governance" in domain_ids
    assert mirrored_domains
    assert any(domain["category"] == "business" for domain in mirrored_domains)
    assert any(domain["category"] == "meta" for domain in domains)


def test_catalog_nodes_define_coverage_paths_and_entrypoints() -> None:
    catalog = load_catalog()

    for domain in catalog["domains"]:
        for node in domain["nodes"]:
            assert node["coverage_paths"], f"node {node['id']} must declare coverage_paths"
            assert node["entrypoints"], f"node {node['id']} must declare entrypoints"


def test_load_function_tree_catalog_rejects_duplicate_domain_ids(tmp_path: Path) -> None:
    module = load_scope_gate_module()
    catalog = load_catalog()
    schema_path = tmp_path / "schema.json"
    catalog_path = tmp_path / "catalog.yaml"

    duplicated_domain = dict(catalog["domains"][0])
    catalog["domains"].append(duplicated_domain)
    schema_path.write_text(SCHEMA_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    catalog_path.write_text(yaml.safe_dump(catalog, sort_keys=False, allow_unicode=True), encoding="utf-8")

    try:
        module.load_function_tree_catalog(catalog_path=catalog_path, schema_path=schema_path)
    except ValueError as exc:
        assert "duplicate function tree domain id" in str(exc)
    else:
        raise AssertionError("duplicate domain ids must be rejected")


def test_load_function_tree_catalog_rejects_duplicate_node_ids(tmp_path: Path) -> None:
    module = load_scope_gate_module()
    catalog = load_catalog()
    schema_path = tmp_path / "schema.json"
    catalog_path = tmp_path / "catalog.yaml"

    duplicated_node = dict(catalog["domains"][0]["nodes"][0])
    catalog["domains"][1]["nodes"].append(duplicated_node)
    schema_path.write_text(SCHEMA_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    catalog_path.write_text(yaml.safe_dump(catalog, sort_keys=False, allow_unicode=True), encoding="utf-8")

    try:
        module.load_function_tree_catalog(catalog_path=catalog_path, schema_path=schema_path)
    except ValueError as exc:
        assert "duplicate function tree node id" in str(exc)
    else:
        raise AssertionError("duplicate node ids must be rejected")


def test_catalog_literal_entrypoint_paths_exist() -> None:
    catalog = load_catalog()

    for domain in catalog["domains"]:
        for node in domain["nodes"]:
            for entrypoint_paths in node["entrypoints"].values():
                for raw_path in entrypoint_paths:
                    if any(token in raw_path for token in "*?["):
                        continue
                    assert (PROJECT_ROOT / raw_path).exists(), f"missing literal entrypoint path: {raw_path}"
