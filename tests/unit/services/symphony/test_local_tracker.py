from pathlib import Path

from src.services.symphony.config import TrackerConfig
from src.services.symphony.local_tracker import LocalIssueTrackerClient
from src.services.symphony.models import BlockerRef


def _make_tracker_config(tmp_path: Path) -> TrackerConfig:
    return TrackerConfig(
        kind="local",
        endpoint="",
        api_key="",
        project_slug="",
        active_states=["todo", "in progress"],
        terminal_states=["done", "cancelled"],
        sqlite_path=tmp_path / "tracker.db",
        active_state_names=["Todo", "In Progress"],
        terminal_state_names=["Done", "Cancelled"],
    )


def test_local_tracker_bootstraps_database_and_persists_issue_events(tmp_path: Path) -> None:
    client = LocalIssueTrackerClient(_make_tracker_config(tmp_path))

    issue = client.create_issue(
        title="First local issue",
        description="Body",
        state="Todo",
        priority=2,
        labels=["ops", "backend"],
        blocked_by=[BlockerRef(id="b-1", identifier="LOCAL-9", state="Todo")],
    )
    issues = client.list_issues()
    events = client.list_events(issue.id)

    assert client.tracker.sqlite_path == tmp_path / "tracker.db"
    assert (tmp_path / "tracker.db").exists()
    assert issues[0].identifier == "LOCAL-1"
    assert issues[0].labels == ["ops", "backend"]
    assert issues[0].blocked_by[0].identifier == "LOCAL-9"
    assert [event["event_type"] for event in events] == ["issue_created"]


def test_local_tracker_fetches_candidates_and_issue_state_refreshes(tmp_path: Path) -> None:
    client = LocalIssueTrackerClient(_make_tracker_config(tmp_path))

    todo_issue = client.create_issue(title="Todo issue", state="Todo")
    done_issue = client.create_issue(title="Done issue", state="Done")
    client.update_issue_state(todo_issue.identifier, "In Progress")

    candidate_issues = client.fetch_candidate_issues()
    in_progress_issues = client.fetch_issues_by_states(["in progress"])
    refreshed_issues = client.fetch_issue_states_by_ids([todo_issue.id, done_issue.id])

    assert [issue.identifier for issue in candidate_issues] == [todo_issue.identifier]
    assert [issue.state for issue in in_progress_issues] == ["In Progress"]
    assert {issue.identifier: issue.state for issue in refreshed_issues} == {
        todo_issue.identifier: "In Progress",
        done_issue.identifier: "Done",
    }


def test_local_tracker_records_state_update_events(tmp_path: Path) -> None:
    client = LocalIssueTrackerClient(_make_tracker_config(tmp_path))

    issue = client.create_issue(title="Stateful issue", state="Todo")
    client.update_issue_state(issue.identifier, "Done")
    events = client.list_events(issue.id)

    assert [event["event_type"] for event in events] == ["issue_created", "issue_state_updated"]
