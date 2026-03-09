from pathlib import Path

from src.services.symphony.config import ServiceConfig
from src.services.symphony.linear_client import LinearIssueTrackerClient
from src.services.symphony.local_tracker import LocalIssueTrackerClient
from src.services.symphony.models import WorkflowDefinition
from src.services.symphony.tracker_factory import create_tracker_client


def test_create_tracker_client_builds_linear_tracker() -> None:
    config = ServiceConfig.from_workflow_definition(
        WorkflowDefinition(
            config={
                "tracker": {
                    "kind": "linear",
                    "project_slug": "mystocks",
                    "api_key": "token",
                }
            },
            prompt_template="Prompt",
        )
    )

    tracker_client = create_tracker_client(config.tracker)
    try:
        assert isinstance(tracker_client, LinearIssueTrackerClient)
    finally:
        tracker_client.close()


def test_create_tracker_client_builds_local_tracker(tmp_path: Path) -> None:
    config = ServiceConfig.from_workflow_definition(
        WorkflowDefinition(
            config={
                "tracker": {
                    "kind": "local",
                    "sqlite_path": str(tmp_path / "tracker.db"),
                }
            },
            prompt_template="Prompt",
        )
    )

    tracker_client = create_tracker_client(config.tracker)
    try:
        assert isinstance(tracker_client, LocalIssueTrackerClient)
    finally:
        tracker_client.close()
