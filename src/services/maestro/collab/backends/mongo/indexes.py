from __future__ import annotations

from pymongo import ASCENDING, DESCENDING, IndexModel


def build_collaboration_index_models() -> dict[str, list[IndexModel]]:
    return {
        "work_items": [
            IndexModel(
                [("work_item_id", ASCENDING)],
                name="ux_work_items_work_item_id",
                unique=True,
            ),
            IndexModel(
                [("branch", ASCENDING), ("task_key", ASCENDING)],
                name="ux_work_items_branch_task_key",
                unique=True,
            ),
            IndexModel(
                [("owner_cli", ASCENDING), ("status", ASCENDING)],
                name="ix_work_items_owner_cli_status",
            ),
        ],
        "work_updates": [
            IndexModel(
                [("work_item_id", ASCENDING), ("update_id", ASCENDING)],
                name="ux_work_updates_work_item_id_update_id",
                unique=True,
            ),
            IndexModel(
                [("work_item_id", ASCENDING), ("created_at", DESCENDING)],
                name="ix_work_updates_work_item_id_created_at",
            ),
        ],
        "work_requests": [
            IndexModel(
                [("work_item_id", ASCENDING), ("request_id", ASCENDING)],
                name="ux_work_requests_work_item_id_request_id",
                unique=True,
            ),
            IndexModel(
                [("work_item_id", ASCENDING), ("status", ASCENDING), ("created_at", DESCENDING)],
                name="ix_work_requests_work_item_id_status_created_at",
            ),
        ],
        "work_events": [
            IndexModel(
                [("work_item_id", ASCENDING), ("event_id", ASCENDING)],
                name="ux_work_events_work_item_id_event_id",
                unique=True,
            ),
            IndexModel(
                [("work_item_id", ASCENDING), ("created_at", ASCENDING)],
                name="ix_work_events_work_item_id_created_at",
            ),
        ],
        "worker_status_views": [
            IndexModel(
                [("work_item_id", ASCENDING)],
                name="ux_worker_status_views_work_item_id",
                unique=True,
            ),
            IndexModel(
                [("branch", ASCENDING)],
                name="ix_worker_status_views_branch",
            ),
        ],
        "transcript_sessions": [
            IndexModel(
                [("session_id", ASCENDING)],
                name="ux_transcript_sessions_session_id",
                unique=True,
            ),
            IndexModel(
                [("work_item_id", ASCENDING), ("started_at", DESCENDING)],
                name="ix_transcript_sessions_work_item_id_started_at",
            ),
        ],
        "transcript_events": [
            IndexModel(
                [("session_id", ASCENDING), ("event_id", ASCENDING)],
                name="ux_transcript_events_session_id_event_id",
                unique=True,
            ),
            IndexModel(
                [("session_id", ASCENDING), ("sequence_no", ASCENDING), ("occurred_at", ASCENDING)],
                name="ix_transcript_events_session_id_sequence_no_occurred_at",
            ),
            IndexModel(
                [("work_item_id", ASCENDING), ("occurred_at", ASCENDING)],
                name="ix_transcript_events_work_item_id_occurred_at",
            ),
        ],
        "transcript_hot_bodies": [
            IndexModel(
                [("session_id", ASCENDING)],
                name="ux_transcript_hot_bodies_session_id",
                unique=True,
            ),
            IndexModel(
                [("available_until", ASCENDING)],
                name="ix_transcript_hot_bodies_available_until",
            ),
            IndexModel(
                [("purge_after", ASCENDING)],
                name="ix_transcript_hot_bodies_purge_after",
                expireAfterSeconds=0,
            ),
        ],
        "transcript_legacy_indexes": [
            IndexModel(
                [("legacy_index_id", ASCENDING)],
                name="ux_transcript_legacy_indexes_legacy_index_id",
                unique=True,
            ),
            IndexModel(
                [("work_item_id", ASCENDING), ("captured_at", ASCENDING)],
                name="ix_transcript_legacy_indexes_work_item_id_captured_at",
            ),
        ],
    }
