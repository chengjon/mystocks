#!/usr/bin/env python3
"""CI 脚本:检查 ExtraSource registry snapshot 中 TEMP_OVERRIDE adapter
是否过期或即将过期。

数据来源:FastAPI lifespan 启动期调用 dump_registered_snapshot() 写入的
``.extra-source-snapshot.json`` JSON 文件,格式::

    {
      "adapters": [
        {"name": "...", "category": "...", "expires_on": "YYYY-MM-DD" | null},
        ...
      ]
    }

退出码:

* 0 — 无 TEMP_OVERRIDE,或所有 TEMP_OVERRIDE 都未过期
* 1 — 至少一个 TEMP_OVERRIDE 已过期(``expires_on < today``)

警告(``expires_on - today < 7 天``)输出到 stderr,但 exit 0。

使用方式 (CI)::

    python scripts/dev/check_temp_override_expiration.py
    python scripts/dev/check_temp_override_expiration.py --snapshot-path .extra-source-snapshot.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

# 警告阈值:过期前 N 天开始 stderr warn
WARN_DAYS_THRESHOLD = 7

# 默认 snapshot 路径 (lifespan 写入位置)
DEFAULT_SNAPSHOT_PATH = ".extra-source-snapshot.json"


def _parse_iso_date(value: str) -> date:
    """Parse 'YYYY-MM-DD' to date object. Raise ValueError on malformed input."""
    return datetime.strptime(value, "%Y-%m-%d").date()


def check_snapshot(snapshot_path: Path, today: date | None = None) -> int:
    """读 snapshot,对每个 expires_on 不为 null 的 adapter:

    * 已过期 (expires_on < today) → return 1
    * 7 天内过期 (today <= expires_on < today + 7d) → stderr warn

    Returns 0 if no expiration, 1 if any expired.
    """
    today = today or date.today()

    if not snapshot_path.exists():
        # Snapshot 不存在 = 没有 ExtraSource 注册 (lifespan 未运行 / 空 registry)
        # 不是错误,CI 视为通过。
        print(
            f"[temp-override] snapshot 文件不存在 ({snapshot_path});" " 视为无 TEMP_OVERRIDE 注册,exit 0",
            file=sys.stderr,
        )
        return 0

    try:
        payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(
            f"[temp-override] snapshot JSON 解析失败 ({snapshot_path}): {e}",
            file=sys.stderr,
        )
        return 1

    adapters = payload.get("adapters", [])
    if not adapters:
        print(
            "[temp-override] snapshot 中无 adapter;exit 0",
            file=sys.stderr,
        )
        return 0

    expired: list[str] = []
    warning: list[str] = []

    for adapter in adapters:
        name = adapter.get("name", "<unknown>")
        expires_on_raw = adapter.get("expires_on")

        # 常规 ExtraSource (expires_on 为 null) — 跳过
        if not expires_on_raw:
            continue

        try:
            expires_on = _parse_iso_date(expires_on_raw)
        except ValueError as e:
            print(
                f"[temp-override] adapter '{name}' expires_on 格式错误:" f" '{expires_on_raw}' (期望 YYYY-MM-DD): {e}",
                file=sys.stderr,
            )
            expired.append(name)
            continue

        days_remaining = (expires_on - today).days

        if days_remaining < 0:
            print(
                f"[temp-override] FAIL adapter '{name}' 已过期:"
                f" expires_on={expires_on_raw} (today={today.isoformat()},"
                f" 超期 {-days_remaining} 天)",
                file=sys.stderr,
            )
            expired.append(name)
        elif days_remaining < WARN_DAYS_THRESHOLD:
            print(
                f"[temp-override] WARN adapter '{name}' {days_remaining} 天后过期:"
                f" expires_on={expires_on_raw} (today={today.isoformat()})",
                file=sys.stderr,
            )
            warning.append(name)

    if expired:
        print(
            f"[temp-override] {len(expired)} 个 adapter 已过期: {expired}",
            file=sys.stderr,
        )
        return 1

    if warning:
        print(
            f"[temp-override] {len(warning)} 个 adapter 7 天内将过期 (warn only):" f" {warning}",
            file=sys.stderr,
        )

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check ExtraSource TEMP_OVERRIDE adapter expiration against today."
            " Exit 1 if any expired; exit 0 with stderr warning if expiring within"
            f" {WARN_DAYS_THRESHOLD} days."
        )
    )
    parser.add_argument(
        "--snapshot-path",
        default=DEFAULT_SNAPSHOT_PATH,
        help=f"Path to .extra-source-snapshot.json (default: {DEFAULT_SNAPSHOT_PATH})",
    )
    parser.add_argument(
        "--today",
        default=None,
        help="Override today's date (YYYY-MM-DD) for testing. Default: date.today().",
    )
    args = parser.parse_args(argv)

    snapshot_path = Path(args.snapshot_path)
    today = _parse_iso_date(args.today) if args.today else None

    return check_snapshot(snapshot_path, today=today)


if __name__ == "__main__":
    sys.exit(main())
