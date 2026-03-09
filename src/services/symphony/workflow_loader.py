from __future__ import annotations

from pathlib import Path

import yaml

from .errors import MissingWorkflowFileError, WorkflowFrontMatterNotAMapError, WorkflowParseError
from .models import WorkflowDefinition


def load_workflow_definition(workflow_path: str | Path) -> WorkflowDefinition:
    """Load and parse a Symphony workflow file."""

    path = Path(workflow_path)
    if not path.exists():
        raise MissingWorkflowFileError(f"Workflow file does not exist: {path}")

    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return WorkflowDefinition(config={}, prompt_template=content.strip())

    lines = content.splitlines()
    closing_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break

    if closing_index is None:
        raise WorkflowParseError("Workflow front matter is missing a closing delimiter.")

    front_matter = "\n".join(lines[1:closing_index])
    prompt_template = "\n".join(lines[closing_index + 1 :]).strip()

    try:
        loaded = yaml.safe_load(front_matter) if front_matter.strip() else {}
    except yaml.YAMLError as exc:
        raise WorkflowParseError("Workflow front matter is invalid YAML.") from exc

    if loaded is None:
        loaded = {}

    if not isinstance(loaded, dict):
        raise WorkflowFrontMatterNotAMapError("Workflow front matter must decode to a mapping.")

    return WorkflowDefinition(config=loaded, prompt_template=prompt_template)
