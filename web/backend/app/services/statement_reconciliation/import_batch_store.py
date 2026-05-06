from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


_IMPORT_BATCHES: dict[str, dict[str, object]] = {}


def _resolve_batch_account_id(
    rows: list[dict[str, str | int]],
    explicit_account_id: str | None,
) -> str | None:
    unique_accounts = {
        str(row["account_id"]).strip()
        for row in rows
        if str(row.get("account_id", "")).strip()
    }

    if explicit_account_id:
        if not unique_accounts or explicit_account_id in unique_accounts:
            return explicit_account_id
        if len(unique_accounts) == 1:
            return next(iter(unique_accounts))
        return None

    if len(unique_accounts) == 1:
        return next(iter(unique_accounts))
    return None


def create_import_batch(
    *,
    account_id: str | None,
    source_type: str,
    rows: list[dict[str, str | int]],
) -> dict[str, object]:
    import_batch_id = uuid4().hex
    batch_account_id = _resolve_batch_account_id(rows, account_id)
    batch = {
        "import_batch_id": import_batch_id,
        "account_id": batch_account_id,
        "source_type": source_type,
        "row_count": len(rows),
        "rows": rows,
        "created_at": datetime.now(timezone.utc),
    }
    _IMPORT_BATCHES[import_batch_id] = batch
    return batch


def get_import_batch(import_batch_id: str) -> dict[str, object]:
    return _IMPORT_BATCHES[import_batch_id]
