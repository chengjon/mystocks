from __future__ import annotations

from jinja2 import Environment, StrictUndefined

from .models import Issue


def render_prompt(template: str, issue: Issue, attempt: int | None = None) -> str:
    """Render the workflow prompt in strict mode."""

    environment = Environment(undefined=StrictUndefined, autoescape=False)
    compiled = environment.from_string(template)
    return compiled.render(issue=issue, attempt=attempt).strip()


def build_continuation_prompt(issue: Issue, turn_number: int) -> str:
    """Build continuation guidance for later turns on the same thread."""

    return f"Continue working on {issue.identifier} ({issue.title}). " f"This is continuation turn {turn_number}."
