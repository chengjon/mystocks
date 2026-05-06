from __future__ import annotations

import csv
import io


REQUIRED_TEMPLATE_COLUMNS = {
    "account_id",
    "trade_date",
    "trade_time",
    "symbol",
    "direction",
    "price",
    "quantity",
    "amount",
    "commission",
    "order_id",
    "trade_id",
}


def _require_cell(row: dict[str, str | None], field_name: str, row_number: int) -> str:
    value = row.get(field_name)
    if value is None or not value.strip():
        raise ValueError(f"row {row_number} missing required value: {field_name}")
    return value.strip()


def parse_normalized_template_csv(csv_bytes: bytes) -> list[dict[str, str | int]]:
    text = csv_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    header = set(reader.fieldnames or [])
    missing = sorted(REQUIRED_TEMPLATE_COLUMNS - header)
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")

    rows: list[dict[str, str | int]] = []
    for row_number, row in enumerate(reader, start=2):
        rows.append(
            {
                "account_id": _require_cell(row, "account_id", row_number),
                "trade_time": (
                    f'{_require_cell(row, "trade_date", row_number)} '
                    f'{_require_cell(row, "trade_time", row_number)}'
                ),
                "symbol": _require_cell(row, "symbol", row_number).upper(),
                "direction": _require_cell(row, "direction", row_number).lower(),
                "price": _require_cell(row, "price", row_number),
                "quantity": _require_cell(row, "quantity", row_number),
                "amount": _require_cell(row, "amount", row_number),
                "commission": _require_cell(row, "commission", row_number),
                "order_id": _require_cell(row, "order_id", row_number),
                "trade_id": _require_cell(row, "trade_id", row_number),
                "source_type": "normalized_template",
                "raw_row_number": row_number,
            }
        )

    if not rows:
        raise ValueError("csv contains no data rows")

    return rows
