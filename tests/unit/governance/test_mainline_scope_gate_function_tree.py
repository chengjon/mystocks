from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace


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


def test_scope_gate_requires_function_tree_sync_for_mirrored_business_entrypoint_change() -> None:
    module = load_scope_gate_module()
    card = make_card(
        domain_id="domain-01",
        node_id="domain-01-node-01",
        affected_entrypoints=["api"],
        update_status="required",
    )

    violations, metrics = module.validate_function_tree_mapping(
        card,
        ["web/backend/app/api/market/market_data_request.py"],
    )

    assert any("require docs/FUNCTION_TREE.md synchronization" in item for item in violations)
    assert metrics["function_tree_shared_sync_hits"] == []


def test_scope_gate_accepts_function_tree_sync_for_mirrored_business_entrypoint_change() -> None:
    module = load_scope_gate_module()
    card = make_card(
        domain_id="domain-01",
        node_id="domain-01-node-01",
        affected_entrypoints=["api"],
        update_status="required",
    )

    violations, metrics = module.validate_function_tree_mapping(
        card,
        ["web/backend/app/api/market/market_data_request.py", "docs/FUNCTION_TREE.md"],
    )

    assert violations == []
    assert metrics["function_tree_shared_sync_hits"] == ["docs/FUNCTION_TREE.md"]
    assert metrics["function_tree_mirrored_entrypoint_hits"] == ["web/backend/app/api/market/market_data_request.py"]
    assert metrics["function_tree_compatibility_entrypoint_hits"] == []
    assert metrics["function_tree_exemption_reason_required"] is False
    assert metrics["function_tree_exemption_reason_present"] is False


def test_scope_gate_requires_exemption_reason_for_parallel_root_api_entrypoint_change() -> None:
    module = load_scope_gate_module()
    card = make_card(
        domain_id="domain-01",
        node_id="domain-01-node-01",
        affected_entrypoints=["api"],
        update_status="required",
    )

    violations, metrics = module.validate_function_tree_mapping(
        card,
        ["web/backend/app/api/market.py", "docs/FUNCTION_TREE.md"],
    )

    assert any("compatibility-style root API entrypoint changes require function_tree.exemption_reason" in item for item in violations)
    assert metrics["function_tree_mirrored_entrypoint_hits"] == ["web/backend/app/api/market.py"]
    assert metrics["function_tree_compatibility_entrypoint_hits"] == ["web/backend/app/api/market.py"]
    assert metrics["function_tree_exemption_reason_required"] is True
    assert metrics["function_tree_exemption_reason_present"] is False
    assert metrics["function_tree_exemption_reason"] == ""


def test_scope_gate_accepts_exemption_reason_for_parallel_root_api_entrypoint_change() -> None:
    module = load_scope_gate_module()
    card = make_card(
        domain_id="domain-01",
        node_id="domain-01-node-01",
        affected_entrypoints=["api"],
        update_status="required",
        exemption_reason="successor:web/backend/app/api/market/**; compatibility-retained:legacy root route",
    )

    violations, metrics = module.validate_function_tree_mapping(
        card,
        ["web/backend/app/api/market.py", "docs/FUNCTION_TREE.md"],
    )

    assert violations == []
    assert metrics["function_tree_compatibility_entrypoint_hits"] == ["web/backend/app/api/market.py"]
    assert metrics["function_tree_exemption_reason_required"] is True
    assert metrics["function_tree_exemption_reason_present"] is True
    assert metrics["function_tree_exemption_reason"] == "successor:web/backend/app/api/market/**; compatibility-retained:legacy root route"


def test_main_writes_function_tree_compatibility_note_to_report_and_stdout(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    module = load_scope_gate_module()
    report_path = tmp_path / "mainline-governance-report.json"
    task_card_path = tmp_path / "task-card.yaml"
    schema_path = tmp_path / "schema.json"
    schema_path.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(
        module,
        "parse_args",
        lambda: SimpleNamespace(
            task_card=str(task_card_path),
            schema=str(schema_path),
            base_sha="base",
            head_sha="head",
            report=str(report_path),
            max_secondary_budget=20.0,
            fail_on_empty_diff=False,
        ),
    )
    monkeypatch.setattr(module, "resolve_task_card_path", lambda _arg: task_card_path)
    monkeypatch.setattr(
        module,
        "load_yaml",
        lambda _path: make_card(
            domain_id="domain-01",
            node_id="domain-01-node-01",
            affected_entrypoints=["api"],
            update_status="required",
            exemption_reason="successor:web/backend/app/api/market/**; compatibility-retained:legacy root route",
        ),
    )
    monkeypatch.setattr(module, "load_json", lambda _path: {})
    monkeypatch.setattr(module, "validate_schema", lambda _card, _schema: [])
    monkeypatch.setattr(module, "resolve_base_head", lambda _base, _head: ("base", "head"))
    monkeypatch.setattr(
        module,
        "run_git_diff",
        lambda _base, _head: ["web/backend/app/api/market.py", "docs/FUNCTION_TREE.md"],
    )
    monkeypatch.setattr(module, "filter_effective_changed_files", lambda paths: paths)
    monkeypatch.setattr(module, "check_feature_openspec", lambda _card: [])
    monkeypatch.setattr(module, "check_summary", lambda _card: [])
    monkeypatch.setattr(module, "check_phase_threshold", lambda _card: [])
    monkeypatch.setattr(module, "load_function_tree_catalog", lambda: {})
    monkeypatch.setattr(
        module,
        "validate_function_tree_mapping",
        lambda _card, _changed_files, catalog=None: (
            [],
            {
                "function_tree_compatibility_entrypoint_hits": ["web/backend/app/api/market.py"],
                "function_tree_exemption_reason": "successor:web/backend/app/api/market/**; compatibility-retained:legacy root route",
                "function_tree_exemption_reason_present": True,
                "function_tree_exemption_reason_required": True,
            },
        ),
    )
    monkeypatch.setattr(module, "check_scope_and_drift", lambda _card, _files, _task_rel: ([], {}))
    monkeypatch.setattr(module, "check_secondary_budget", lambda _card, _files, _budget: ([], {}))

    assert module.main() == 0

    captured = capsys.readouterr().out
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["pass"] is True
    assert report["function_tree_compatibility_entrypoint_hits"] == ["web/backend/app/api/market.py"]
    assert report["function_tree_exemption_reason_required"] is True
    assert "function_tree compatibility-note" in captured
    assert "compatibility-retained:legacy root route" in captured


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
