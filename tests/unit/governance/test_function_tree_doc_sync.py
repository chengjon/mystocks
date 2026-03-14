from __future__ import annotations

from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = PROJECT_ROOT / "governance" / "function-tree" / "catalog.yaml"
FUNCTION_TREE_DOC = PROJECT_ROOT / "docs" / "FUNCTION_TREE.md"
WORKFLOW_DOC = PROJECT_ROOT / "docs" / "guides" / "FEATURE_MANAGEMENT_WORKFLOW.md"
PR_TEMPLATE = PROJECT_ROOT / ".github" / "pull_request_template.md"


def load_catalog() -> dict:
    payload = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_function_tree_doc_contains_all_mirrored_catalog_ids() -> None:
    catalog = load_catalog()
    doc_text = FUNCTION_TREE_DOC.read_text(encoding="utf-8")

    mirrored_domains = [domain for domain in catalog["domains"] if domain["mirror_to_function_tree"]]

    for domain in mirrored_domains:
        assert f"{{#{domain['id']}}}" in doc_text
        for node in domain["nodes"]:
            assert f"{{#{node['id']}}}" in doc_text


def test_feature_management_workflow_mentions_task_card_function_tree_contract() -> None:
    workflow = WORKFLOW_DOC.read_text(encoding="utf-8")

    assert "task card" in workflow.lower()
    assert "function_tree" in workflow
    assert "唯一机器事实源" in workflow


def test_pr_template_mirrors_task_card_function_tree_fields() -> None:
    template = PR_TEMPLATE.read_text(encoding="utf-8")

    assert "task_card_path" in template
    assert "task card" in template.lower()
    assert "function_tree_domain_id" in template
    assert "function_tree_node_id" in template
    assert "task card 是唯一机器事实源" in template
