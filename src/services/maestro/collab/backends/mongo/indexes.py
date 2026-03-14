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
    }
