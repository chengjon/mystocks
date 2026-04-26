from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = PROJECT_ROOT / "governance" / "mainline" / "schemas" / "ai-task-card.schema.json"
TEMPLATE_PATH = PROJECT_ROOT / "governance" / "mainline" / "templates" / "ai-task-card.yaml"
SPEC_PATH = PROJECT_ROOT / "governance" / "mainline" / "spec" / "ai-development-mainline-governance-spec.md"
OPENSPEC_FUNCTION_TREE_SPEC_PATH = PROJECT_ROOT / "openspec" / "specs" / "function-tree-governance" / "spec.md"
TASK_CARD_DIR = PROJECT_ROOT / "governance" / "mainline" / "task-cards"
FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "governance" / "function-tree-governance-sample-card.yaml"


def load_schema() -> dict:
    payload = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def make_feature_card() -> dict:
    return {
        "version": "v0.2",
        "task": {
            "id": "pr-9999",
            "title": "govern function tree as code",
            "owner": "mystocks_spec5",
            "created_at": "2026-03-14",
        },
        "mainline": {
            "id": "L1-governance",
            "objective": "keep governance machine-readable",
            "milestone_id": "L2-governance",
            "slice_id": "L3-function-tree",
        },
        "classification": {
            "task_type": "feature",
            "secondary_type": "none",
            "secondary_change_budget_percent": 0,
            "secondary_allowed_paths": [],
        },
        "openspec": {
            "change_id": "govern-function-tree-as-code",
            "approval_status": "approved",
        },
        "scope": {
            "allowed_paths": ["governance/**", "docs/**"],
            "forbidden_paths": ["web/frontend/src/App.vue"],
        },
        "non_goals": ["no unrelated business fixes"],
        "acceptance": {
            "checks": [
                {
                    "id": "tests",
                    "command": "pytest --no-cov tests/unit/governance -q",
                    "required": True,
                }
            ]
        },
        "risk_and_rollback": {
            "risks": ["scope gate may over-match"],
            "rollback_plan": "git revert <sha>",
        },
        "delivery": {
            "six_line_summary_required": True,
            "six_line_summary": {
                "change_purpose": "machine-readable function tree governance",
                "modified_scope": "governance/mainline and docs",
                "dependency_changes": "none",
                "legacy_logic_impact": "none",
                "rollback_ready": "yes",
                "risk_and_rollback_point": "revert governance-only diff",
            },
        },
        "governance": {
            "phase": "phase_a_pr_hard_gate",
            "mainline_drift_threshold_percent": 5,
            "stop_rule_owner": "mystocks_spec5",
            "stop_rule_sla_hours": 24,
            "approval": {
                "required": False,
                "approved_by": "main",
                "approved_at": "2026-03-14T00:00:00Z",
                "approval_note": "approved",
                "secondary_approved": False,
            },
        },
    }


def validate(card: dict) -> list[str]:
    schema = load_schema()
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(card), key=lambda item: list(item.absolute_path))
    return [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}" for error in errors
    ]


def test_feature_task_requires_function_tree_block() -> None:
    card = make_feature_card()

    errors = validate(card)

    assert any("function_tree" in error for error in errors)


def test_function_tree_requires_supported_entrypoints_and_update_status() -> None:
    card = make_feature_card()
    card["function_tree"] = {
        "domain_id": "domain-05",
        "node_id": "domain-05-node-01",
        "affected_entrypoints": ["api", "unsupported"],
        "update_status": "later",
        "secondary_domains": [],
        "exemption_reason": "",
    }

    errors = validate(card)

    assert any("affected_entrypoints" in error for error in errors)
    assert any("update_status" in error for error in errors)


def test_valid_feature_function_tree_passes_schema() -> None:
    card = copy.deepcopy(make_feature_card())
    card["function_tree"] = {
        "domain_id": "meta-governance",
        "node_id": "meta-governance-mainline",
        "affected_entrypoints": ["governance", "tests"],
        "update_status": "not-needed",
        "secondary_domains": [],
        "exemption_reason": "governance-self-bootstrap",
    }

    errors = validate(card)

    assert errors == []


def test_task_card_template_includes_function_tree_example() -> None:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert "function_tree:" in template
    assert "domain_id:" in template
    assert "node_id:" in template
    assert "affected_entrypoints:" in template
    assert "update_status:" in template


def test_mainline_governance_spec_mentions_function_tree_compatibility_contract() -> None:
    spec_text = SPEC_PATH.read_text(encoding="utf-8")

    assert "function_tree.exemption_reason" in spec_text
    assert "不得写 `not-needed`" in spec_text
    assert "compatibility-retained" in spec_text
    assert "继任入口" in spec_text


def test_openspec_function_tree_spec_mentions_reviewer_visible_gate_contract() -> None:
    spec_text = OPENSPEC_FUNCTION_TREE_SPEC_PATH.read_text(encoding="utf-8")

    assert "docs/FUNCTION_TREE.md" in spec_text
    assert "function_tree_mirrored_entrypoint_hits" in spec_text
    assert "function_tree_shared_sync_hits" in spec_text
    assert "function_tree_compatibility_entrypoint_hits" in spec_text
    assert "function_tree_exemption_reason_required=true" in spec_text
    assert "function_tree_exemption_reason" in spec_text
    assert "function_tree compatibility-note" in spec_text
    assert "compatibility-retained" in spec_text


def test_function_tree_sample_cards_pass_schema() -> None:
    import yaml

    fixture = yaml.safe_load(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert validate(fixture["business_feature_card"]) == []
    assert validate(fixture["meta_governance_cleanup_card"]) == []


def test_sample_and_committed_task_cards_fill_function_tree_exemption_reason() -> None:
    import yaml

    fixture = yaml.safe_load(FIXTURE_PATH.read_text(encoding="utf-8"))
    fixture_cards = list(fixture.values())
    committed_cards = [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(TASK_CARD_DIR.glob("*.yaml"))
    ]

    for card in fixture_cards + committed_cards:
        function_tree = card.get("function_tree", {})
        assert str(function_tree.get("exemption_reason", "")).strip() != ""
