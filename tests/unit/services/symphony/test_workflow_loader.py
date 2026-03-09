from pathlib import Path

import pytest

from src.services.symphony.errors import (
    MissingWorkflowFileError,
    WorkflowFrontMatterNotAMapError,
    WorkflowParseError,
)
from src.services.symphony.workflow_loader import load_workflow_definition


def test_load_workflow_definition_with_front_matter(tmp_path: Path) -> None:
    workflow_path = tmp_path / "WORKFLOW.md"
    workflow_path.write_text(
        """---
tracker:
  kind: linear
  project_slug: mystocks
polling:
  interval_ms: 15000
---

You are working on {{ issue.identifier }}.
""",
        encoding="utf-8",
    )

    definition = load_workflow_definition(workflow_path)

    assert definition.config["tracker"]["kind"] == "linear"
    assert definition.config["tracker"]["project_slug"] == "mystocks"
    assert definition.config["polling"]["interval_ms"] == 15000
    assert definition.prompt_template == "You are working on {{ issue.identifier }}."


def test_load_workflow_definition_without_front_matter(tmp_path: Path) -> None:
    workflow_path = tmp_path / "WORKFLOW.md"
    workflow_path.write_text("Hello {{ issue.title }}.", encoding="utf-8")

    definition = load_workflow_definition(workflow_path)

    assert definition.config == {}
    assert definition.prompt_template == "Hello {{ issue.title }}."


def test_load_workflow_definition_raises_typed_error_for_missing_file(tmp_path: Path) -> None:
    workflow_path = tmp_path / "WORKFLOW.md"

    with pytest.raises(MissingWorkflowFileError):
        load_workflow_definition(workflow_path)


def test_load_workflow_definition_raises_typed_error_for_invalid_yaml(tmp_path: Path) -> None:
    workflow_path = tmp_path / "WORKFLOW.md"
    workflow_path.write_text(
        """---
tracker:
  kind: linear
  project_slug: [unterminated
---
Prompt
""",
        encoding="utf-8",
    )

    with pytest.raises(WorkflowParseError):
        load_workflow_definition(workflow_path)


def test_load_workflow_definition_rejects_non_mapping_front_matter(tmp_path: Path) -> None:
    workflow_path = tmp_path / "WORKFLOW.md"
    workflow_path.write_text(
        """---
- linear
- mystocks
---
Prompt
""",
        encoding="utf-8",
    )

    with pytest.raises(WorkflowFrontMatterNotAMapError):
        load_workflow_definition(workflow_path)
