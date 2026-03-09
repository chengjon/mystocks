from __future__ import annotations

from .config import TrackerConfig
from .errors import ConfigurationValidationError
from .linear_client import LinearIssueTrackerClient
from .local_tracker import LocalIssueTrackerClient


def create_tracker_client(tracker: TrackerConfig):
    if tracker.kind == "linear":
        return LinearIssueTrackerClient(tracker)
    if tracker.kind == "local":
        return LocalIssueTrackerClient(tracker)
    raise ConfigurationValidationError("Unsupported tracker kind.", code="unsupported_tracker_kind")
