from __future__ import annotations

import csv
import io


SUPPORTED_MINIQMT_COLUMNS = {
    "证券代码",
    "买卖方向",
    "成交价格",
    "成交数量",
    "成交金额",
    "手续费",
    "委托编号",
    "成交编号",
    "成交时间",
}

MINIQMT_DIRECTION_MAP = {
    "买入": "buy",
    "卖出": "sell",
}


def _require_cell(row: dict[str, str | None], field_name: str, row_number: int) -> str:
    value = row.get(field_name)
    if value is None or not value.strip():
        raise ValueError(f"row {row_number} missing required value: {field_name}")
    return value.strip()


def parse_miniqmt_csv(csv_bytes: bytes, *, account_id: str) -> list[dict[str, str | int]]:
    text = csv_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    header = set(reader.fieldnames or [])
    missing = sorted(SUPPORTED_MINIQMT_COLUMNS - header)
    if missing:
        raise ValueError(f"missing supported miniQMT columns: {', '.join(missing)}")

    rows: list[dict[str, str | int]] = []
    for row_number, row in enumerate(reader, start=2):
        direction_value = _require_cell(row, "买卖方向", row_number)
        if direction_value not in MINIQMT_DIRECTION_MAP:
            raise ValueError(f"unsupported miniQMT direction: {direction_value}")

        rows.append(
            {
                "account_id": account_id,
                "trade_time": _require_cell(row, "成交时间", row_number),
                "symbol": _require_cell(row, "证券代码", row_number).upper(),
                "direction": MINIQMT_DIRECTION_MAP[direction_value],
                "price": _require_cell(row, "成交价格", row_number),
                "quantity": _require_cell(row, "成交数量", row_number),
                "amount": _require_cell(row, "成交金额", row_number),
                "commission": _require_cell(row, "手续费", row_number),
                "order_id": _require_cell(row, "委托编号", row_number),
                "trade_id": _require_cell(row, "成交编号", row_number),
                "source_type": "miniqmt",
                "raw_row_number": row_number,
            }
        )

    if not rows:
        raise ValueError("csv contains no data rows")

    return rows
