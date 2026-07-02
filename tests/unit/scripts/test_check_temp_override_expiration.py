"""Unit tests for scripts/dev/check_temp_override_expiration.py (Phase 3.3).

Covers the five scenarios from tasks.md Phase 3.3:

* 无 ExtraSource → exit 0
* 常规 ExtraSource (expires_on=null) → exit 0
* TEMP_OVERRIDE 未过期 → exit 0
* TEMP_OVERRIDE 过期 → exit 1
* TEMP_OVERRIDE 提前 7 天 → exit 0 + stderr 包含 warning
"""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

# scripts/dev 不在 sys.path 默认搜索路径中; 手动添加
_SCRIPTS_DEV = Path(__file__).resolve().parents[3] / "scripts" / "dev"
sys.path.insert(0, str(_SCRIPTS_DEV))

import check_temp_override_expiration as checker  # noqa: E402


@pytest.fixture
def snapshot_file(tmp_path: Path) -> Path:
    """Return path to a snapshot file. Tests write JSON content before invocation."""
    return tmp_path / ".extra-source-snapshot.json"


def _write_snapshot(path: Path, adapters: list[dict]) -> None:
    path.write_text(json.dumps({"adapters": adapters}, indent=2), encoding="utf-8")


class TestNoSnapshot:
    def test_missing_snapshot_returns_zero(self, snapshot_file: Path) -> None:
        # snapshot 文件不存在 = lifespan 未运行 (无 ExtraSource 注册)
        today = date(2026, 7, 2)
        rc = checker.check_snapshot(snapshot_file, today=today)
        assert rc == 0


class TestEmptySnapshot:
    def test_empty_adapters_returns_zero(self, snapshot_file: Path) -> None:
        _write_snapshot(snapshot_file, [])
        today = date(2026, 7, 2)
        rc = checker.check_snapshot(snapshot_file, today=today)
        assert rc == 0


class TestRegularExtraSource:
    def test_expires_on_null_skipped(self, snapshot_file: Path, capsys: pytest.CaptureFixture) -> None:
        # 常规 ExtraSource, expires_on 为 null — 不应触发任何检查
        _write_snapshot(
            snapshot_file,
            [{"name": "big-deal", "category": "MARKET_BIG_DEAL", "expires_on": None}],
        )
        today = date(2026, 7, 2)
        rc = checker.check_snapshot(snapshot_file, today=today)
        assert rc == 0
        # stderr 不应包含 WARN 或 FAIL
        stderr = capsys.readouterr().err
        assert "FAIL" not in stderr
        assert "WARN" not in stderr


class TestTempOverrideNotExpired:
    def test_far_future_expiration_returns_zero(self, snapshot_file: Path, capsys: pytest.CaptureFixture) -> None:
        # expires_on 30 天后 — 未过期且不在 warning 窗口
        future = (date(2026, 7, 2) + timedelta(days=30)).isoformat()
        _write_snapshot(
            snapshot_file,
            [{"name": "temp", "category": "TEMP_CAT", "expires_on": future}],
        )
        rc = checker.check_snapshot(snapshot_file, today=date(2026, 7, 2))
        assert rc == 0
        stderr = capsys.readouterr().err
        assert "WARN" not in stderr


class TestTempOverrideExpired:
    def test_past_expiration_returns_one(self, snapshot_file: Path, capsys: pytest.CaptureFixture) -> None:
        # expires_on 昨天 — 已过期
        past = (date(2026, 7, 2) - timedelta(days=1)).isoformat()
        _write_snapshot(
            snapshot_file,
            [{"name": "expired", "category": "EX_CAT", "expires_on": past}],
        )
        rc = checker.check_snapshot(snapshot_file, today=date(2026, 7, 2))
        assert rc == 1
        stderr = capsys.readouterr().err
        assert "FAIL" in stderr
        assert "expired" in stderr

    def test_expires_today_not_expired(self, snapshot_file: Path) -> None:
        # expires_on 等于 today — 边界情况,days_remaining=0, 未过期
        today_str = date(2026, 7, 2).isoformat()
        _write_snapshot(
            snapshot_file,
            [{"name": "boundary", "category": "EX_CAT", "expires_on": today_str}],
        )
        rc = checker.check_snapshot(snapshot_file, today=date(2026, 7, 2))
        # days_remaining=0 < 7 → WARN, 但 rc 仍为 0
        assert rc == 0

    def test_one_expired_one_ok_returns_one(self, snapshot_file: Path) -> None:
        future = (date(2026, 7, 2) + timedelta(days=30)).isoformat()
        past = (date(2026, 7, 2) - timedelta(days=5)).isoformat()
        _write_snapshot(
            snapshot_file,
            [
                {"name": "ok", "category": "C1", "expires_on": future},
                {"name": "expired", "category": "C2", "expires_on": past},
            ],
        )
        rc = checker.check_snapshot(snapshot_file, today=date(2026, 7, 2))
        assert rc == 1


class TestTempOverrideWarning:
    def test_within_7_days_warns_exit_zero(self, snapshot_file: Path, capsys: pytest.CaptureFixture) -> None:
        # expires_on 5 天后 — 在 warning 窗口,未过期
        soon = (date(2026, 7, 2) + timedelta(days=5)).isoformat()
        _write_snapshot(
            snapshot_file,
            [{"name": "soon", "category": "EX_CAT", "expires_on": soon}],
        )
        rc = checker.check_snapshot(snapshot_file, today=date(2026, 7, 2))
        assert rc == 0
        stderr = capsys.readouterr().err
        assert "WARN" in stderr
        assert "soon" in stderr
        assert "5" in stderr


class TestMalformedSnapshot:
    def test_invalid_json_returns_one(self, snapshot_file: Path) -> None:
        snapshot_file.write_text("{not valid json", encoding="utf-8")
        rc = checker.check_snapshot(snapshot_file, today=date(2026, 7, 2))
        assert rc == 1

    def test_malformed_expires_on_date_returns_one(self, snapshot_file: Path, capsys: pytest.CaptureFixture) -> None:
        # expires_on 非 YYYY-MM-DD 格式 — 视为过期(fail fast)
        _write_snapshot(
            snapshot_file,
            [{"name": "bad", "category": "C", "expires_on": "2026/07/02"}],
        )
        rc = checker.check_snapshot(snapshot_file, today=date(2026, 7, 2))
        assert rc == 1
        stderr = capsys.readouterr().err
        assert "格式错误" in stderr or "FAIL" in stderr


class TestCliMain:
    def test_main_with_today_override(self, snapshot_file: Path) -> None:
        # 验证 --today CLI 参数传递正确
        future = (date(2026, 7, 2) + timedelta(days=30)).isoformat()
        _write_snapshot(
            snapshot_file,
            [{"name": "temp", "category": "C", "expires_on": future}],
        )
        rc = checker.main(["--snapshot-path", str(snapshot_file), "--today", "2026-07-02"])
        assert rc == 0
