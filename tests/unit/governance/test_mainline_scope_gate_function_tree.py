from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "governance" / "mainline" / "scripts" / "mainline_scope_gate.py"


def load_scope_gate_module():
    spec = importlib.util.spec_from_file_location("mainline_scope_gate", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_card(
    *,
    domain_id: str,
    node_id: str,
    affected_entrypoints: list[str],
    update_status: str,
    secondary_domains: list[str] | None = None,
    exemption_reason: str = "",
    task_type: str = "feature",
) -> dict:
    return {
        "classification": {
            "task_type": task_type,
        },
        "function_tree": {
            "domain_id": domain_id,
            "node_id": node_id,
            "affected_entrypoints": affected_entrypoints,
            "update_status": update_status,
            "secondary_domains": secondary_domains or [],
            "exemption_reason": exemption_reason,
        },
    }


def test_scope_gate_allows_meta_governance_self_bootstrap() -> None:
    module = load_scope_gate_module()
    card = make_card(
        domain_id="meta-governance",
        node_id="meta-governance-mainline",
        affected_entrypoints=["governance"],
        update_status="not-needed",
        exemption_reason="governance-self-bootstrap",
    )

    violations, metrics = module.validate_function_tree_mapping(
        card,
        [
            "governance/mainline/scripts/mainline_scope_gate.py",
            "governance/function-tree/catalog.yaml",
        ],
    )

    assert violations == []
    assert metrics["matched_domain_ids"] == ["meta-governance"]


def test_scope_gate_allows_meta_governance_technical_debt_artifacts() -> None:
    module = load_scope_gate_module()
    card = make_card(
        domain_id="meta-governance",
        node_id="meta-governance-mainline",
        affected_entrypoints=["governance"],
        update_status="required",
    )

    violations, metrics = module.validate_function_tree_mapping(
        card,
        ["governance/technical-debt/TASK.md"],
    )

    assert violations == []
    assert metrics["matched_domain_ids"] == ["meta-governance"]


def test_scope_gate_rejects_unknown_node() -> None:
    module = load_scope_gate_module()
    card = make_card(
        domain_id="domain-05",
        node_id="domain-05-node-99",
        affected_entrypoints=["api"],
        update_status="required",
    )

    violations, _ = module.validate_function_tree_mapping(card, ["web/backend/app/api/trading_runtime.py"])

    assert any("unknown function_tree.node_id" in item for item in violations)


def test_scope_gate_rejects_unmatched_diff_for_declared_node() -> None:
    module = load_scope_gate_module()
    card = make_card(
        domain_id="domain-05",
        node_id="domain-05-node-01",
        affected_entrypoints=["api"],
        update_status="required",
    )

    violations, _ = module.validate_function_tree_mapping(card, ["governance/mainline/scripts/mainline_scope_gate.py"])

    assert any("declared function_tree mapping did not match changed files" in item for item in violations)


def test_scope_gate_requires_secondary_domains_for_cross_domain_business_diff() -> None:
    module = load_scope_gate_module()
    card = make_card(
        domain_id="domain-01",
        node_id="domain-01-node-01",
        affected_entrypoints=["api"],
        update_status="required",
    )

    violations, metrics = module.validate_function_tree_mapping(
        card,
        ["web/backend/app/api/market.py", "web/backend/app/api/indicators.py"],
    )

    assert any("secondary_domains" in item for item in violations)
    assert metrics["matched_domain_ids"] == ["domain-01", "domain-02"]


def test_scope_gate_rejects_not_needed_for_mirrored_business_entrypoint_change() -> None:
    module = load_scope_gate_module()
    card = make_card(
        domain_id="domain-01",
        node_id="domain-01-node-01",
        affected_entrypoints=["api"],
        update_status="not-needed",
    )

    violations, _ = module.validate_function_tree_mapping(card, ["web/backend/app/api/market.py"])

    assert any("cannot use update_status=not-needed" in item for item in violations)


def test_run_git_diff_normalizes_git_quoted_utf8_paths(monkeypatch) -> None:
    module = load_scope_gate_module()
    encoded_name = "".join(f"\\{byte:03o}" for byte in "超长文档拆分办法".encode("utf-8"))
    quoted_path = f'"docs/guides/documentation/{encoded_name}.md"'

    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=["git", "diff"],
            returncode=0,
            stdout=f"{quoted_path}\ndocs/INDEX.md\n",
            stderr="",
        )

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    assert module.run_git_diff("base", "head") == [
        "docs/INDEX.md",
        "docs/guides/documentation/超长文档拆分办法.md",
    ]
