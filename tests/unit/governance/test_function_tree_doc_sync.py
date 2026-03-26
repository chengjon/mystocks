from __future__ import annotations

from pathlib import Path
import fnmatch
import re

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = PROJECT_ROOT / "governance" / "function-tree" / "catalog.yaml"
FUNCTION_TREE_DOC = PROJECT_ROOT / "docs" / "FUNCTION_TREE.md"
WORKFLOW_DOC = PROJECT_ROOT / "docs" / "guides" / "governance" / "FEATURE_MANAGEMENT_WORKFLOW.md"
PR_TEMPLATE = PROJECT_ROOT / ".github" / "pull_request_template.md"


def load_catalog() -> dict:
    payload = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _match_catalog_pattern(target: str, pattern: str) -> bool:
    if fnmatch.fnmatch(target, pattern):
        return True
    if pattern.endswith("/**"):
        prefix = pattern[:-3].rstrip("/")
        return target == prefix or target.startswith(prefix + "/")
    if pattern.endswith("/"):
        prefix = pattern.rstrip("/")
        return target == prefix or target.startswith(prefix + "/")
    return False


def test_function_tree_doc_contains_all_mirrored_catalog_ids() -> None:
    catalog = load_catalog()
    doc_text = FUNCTION_TREE_DOC.read_text(encoding="utf-8")

    mirrored_domains = [domain for domain in catalog["domains"] if domain["mirror_to_function_tree"]]

    for domain in mirrored_domains:
        assert f"{{#{domain['id']}}}" in doc_text
        for node in domain["nodes"]:
            assert f"{{#{node['id']}}}" in doc_text


def test_function_tree_doc_mirrored_domain_and_node_labels_match_catalog_exactly() -> None:
    catalog = load_catalog()
    doc_text = FUNCTION_TREE_DOC.read_text(encoding="utf-8")

    mirrored_domains = [domain for domain in catalog["domains"] if domain["mirror_to_function_tree"]]

    for domain in mirrored_domains:
        assert f"## {domain['label']} {{#{domain['id']}}}" in doc_text
        for node in domain["nodes"]:
            assert f"### {node['label']} {{#{node['id']}}}" in doc_text


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


def test_function_tree_doc_relative_links_resolve() -> None:
    doc_text = FUNCTION_TREE_DOC.read_text(encoding="utf-8")
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)")

    missing_targets: list[str] = []

    for target in link_pattern.findall(doc_text):
        if target.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
            continue

        resolved = (FUNCTION_TREE_DOC.parent / target).resolve()
        if not resolved.exists():
            missing_targets.append(target)

    assert missing_targets == []


def test_function_tree_doc_code_paths_resolve() -> None:
    doc_text = FUNCTION_TREE_DOC.read_text(encoding="utf-8")
    code_path_pattern = re.compile(r"`((?:\.{1,2}/|src/|web/|tests/|docs/|governance/|scripts/)[^`]+)`")

    missing_paths: list[str] = []

    for target in code_path_pattern.findall(doc_text):
        resolved = (FUNCTION_TREE_DOC.parent / target).resolve() if target.startswith(".") else (PROJECT_ROOT / target).resolve()
        if not resolved.exists():
            missing_paths.append(target)

    assert missing_paths == []


def test_function_tree_domains_expose_metadata_before_entry_table() -> None:
    doc_text = FUNCTION_TREE_DOC.read_text(encoding="utf-8")
    domain_sections = re.split(r"^##\s+(\d{2}-[^\n]+\{#domain-\d{2}\})\s*$", doc_text, flags=re.M)

    expected_prefix_lines = [
        "**模块路径**:",
        "**API前缀**:",
        "**完成度**:",
        "### 领域入口",
    ]

    for index in range(1, len(domain_sections), 2):
        heading = domain_sections[index]
        body = domain_sections[index + 1]
        meaningful_lines = [line.strip() for line in body.splitlines() if line.strip()]
        assert len(meaningful_lines) >= 4, heading
        for line, expected_prefix in zip(meaningful_lines[:4], expected_prefix_lines):
            assert line.startswith(expected_prefix), heading


def test_function_tree_entrypoint_purpose_column_uses_canonical_suffixes() -> None:
    doc_text = FUNCTION_TREE_DOC.read_text(encoding="utf-8")
    domain_sections = re.split(r"^##\s+(\d{2}-[^\n]+\{#domain-\d{2}\})\s*$", doc_text, flags=re.M)

    expected_suffixes = {
        "规范入口": "治理入口",
        "API/契约入口": "接口入口",
        "前端/交互入口": "交互入口",
        "核心代码入口": "实现入口",
        "测试与验证入口": "验证入口",
        "运行与排障入口": "排障入口",
    }

    for index in range(1, len(domain_sections), 2):
        heading = domain_sections[index]
        body = domain_sections[index + 1]
        lines = body.splitlines()
        start = next((idx for idx, line in enumerate(lines) if line.strip() == "### 领域入口"), None)
        assert start is not None, heading

        rows: list[str] = []
        for line in lines[start + 3 :]:
            if not line.startswith("| "):
                if rows:
                    break
                continue
            rows.append(line)

        assert len(rows) == 6, heading

        for row in rows:
            columns = [column.strip() for column in row.strip().strip("|").split("|")]
            entrypoint_type = columns[0]
            purpose = columns[2]
            assert purpose.endswith(expected_suffixes[entrypoint_type]), f"{heading}: {entrypoint_type} -> {purpose}"


def test_function_tree_doc_entrypoint_links_overlap_catalog_entrypoints() -> None:
    catalog = load_catalog()
    doc_text = FUNCTION_TREE_DOC.read_text(encoding="utf-8")
    domain_sections = re.split(r"^##\s+(\d{2}-[^\n]+\{#domain-\d{2}\})\s*$", doc_text, flags=re.M)
    category_mapping = {
        "API/契约入口": "api",
        "前端/交互入口": "frontend",
        "核心代码入口": "core",
        "测试与验证入口": "tests",
        "运行与排障入口": "operations",
    }

    parsed_doc_rows: dict[str, dict[str, list[str]]] = {}

    for index in range(1, len(domain_sections), 2):
        domain_id = re.search(r"\{#(domain-\d{2})\}", domain_sections[index]).group(1)
        body = domain_sections[index + 1]
        lines = body.splitlines()
        start = next((idx for idx, line in enumerate(lines) if line.strip() == "### 领域入口"), None)
        assert start is not None, domain_id

        rows: dict[str, list[str]] = {}
        for line in lines[start + 3 :]:
            if not line.startswith("| "):
                if rows:
                    break
                continue
            columns = [column.strip() for column in line.strip().strip("|").split("|")]
            links = re.findall(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)", columns[1])
            resolved_targets: list[str] = []
            for target in links:
                absolute = (FUNCTION_TREE_DOC.parent / target).resolve()
                resolved_targets.append(absolute.relative_to(PROJECT_ROOT).as_posix())
            rows[columns[0]] = resolved_targets
        parsed_doc_rows[domain_id] = rows

    for domain in catalog["domains"]:
        if not domain["mirror_to_function_tree"]:
            continue

        domain_row_map = parsed_doc_rows[domain["id"]]
        aggregated_catalog: dict[str, set[str]] = {value: set() for value in category_mapping.values()}

        for node in domain["nodes"]:
            for category in aggregated_catalog:
                aggregated_catalog[category].update(node.get("entrypoints", {}).get(category, []) or [])

        for doc_category, catalog_category in category_mapping.items():
            doc_targets = domain_row_map[doc_category]
            catalog_patterns = aggregated_catalog[catalog_category]
            assert any(
                any(_match_catalog_pattern(target, pattern) for pattern in catalog_patterns)
                for target in doc_targets
            ), f"{domain['id']} {doc_category}: no overlap between doc links and catalog entrypoints"


def test_function_tree_quick_nav_uses_canonical_status_vocabulary() -> None:
    doc_text = FUNCTION_TREE_DOC.read_text(encoding="utf-8")
    quick_nav_rows = re.findall(
        r"^\| \[(\d{2}-[^\]]+)\]\(#(domain-\d{2})\) \| ([^|]+) \| ([^|]+)\|$",
        doc_text,
        flags=re.M,
    )

    canonical_statuses = {
        "✅ 完成",
        "🚧 开发中",
        "📝 计划中",
        "⚠️ 需修复",
        "🔒 已废弃",
        "🧪 实验性",
    }

    assert len(quick_nav_rows) == 10

    for _, _, status, completion in quick_nav_rows:
        assert status.strip() in canonical_statuses
        assert re.fullmatch(r"\d+%", completion.strip())
