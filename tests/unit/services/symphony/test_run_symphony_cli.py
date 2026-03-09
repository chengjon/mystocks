from __future__ import annotations

import importlib


def test_run_symphony_module_imports_without_circular_dependency() -> None:
    module = importlib.import_module("scripts.runtime.run_symphony")

    assert hasattr(module, "build_parser")


def test_run_symphony_cli_defaults_to_root_workflow() -> None:
    module = importlib.import_module("scripts.runtime.run_symphony")
    parser = module.build_parser()
    args = parser.parse_args([])

    assert args.workflow_path == "WORKFLOW.md"
    assert args.port is None


def test_run_symphony_cli_accepts_explicit_path_and_port() -> None:
    module = importlib.import_module("scripts.runtime.run_symphony")
    parser = module.build_parser()
    args = parser.parse_args(["custom/WORKFLOW.md", "--port", "9030"])

    assert args.workflow_path == "custom/WORKFLOW.md"
    assert args.port == 9030
