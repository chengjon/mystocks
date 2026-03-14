from __future__ import annotations

from .config import TrackerConfig
from .errors import ConfigurationValidationError
from .linear_client import LinearIssueTrackerClient
from .local_tracker import LocalIssueTrackerClient
from .mongo_tracker import MongoWorkItemTrackerClient
from pymongo import MongoClient


def create_tracker_client(tracker: TrackerConfig):
    if tracker.kind == "linear":
        return LinearIssueTrackerClient(tracker)
    if tracker.kind == "local":
        return LocalIssueTrackerClient(tracker)
    if tracker.kind == "mongo":
        mongo_client = MongoClient(tracker.mongo_uri)
        return MongoWorkItemTrackerClient(tracker, mongo_client[tracker.mongo_db], mongo_client=mongo_client)
    raise ConfigurationValidationError("Unsupported tracker kind.", code="unsupported_tracker_kind")
