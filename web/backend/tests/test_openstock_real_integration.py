"""真实 OpenStock 集成测试(B4.014-M1n / 发现 #1-#5 复验)。

默认 skip,需通过环境变量激活:
    OPENSTOCK_BASE_URL=http://192.168.123.104:8040 \
    python -m pytest tests/test_openstock_real_integration.py \
                     -p no:libtmux --no-cov -n 0 -m integration

复验 B4_014_OPENSTOCK_PROD_AUDIT_2026-07-01.md §七 的 5 个 probe 矩阵。

pytest.mark.integration marker 在 pytest.ini / pyproject.toml 注册。
"""
from __future__ import annotations

import os
from typing import Any

import pytest
import urllib.request
import json

OPENSTOCK_BASE_URL = os.environ.get("OPENSTOCK_BASE_URL", "").rstrip("/")
pytestmark = pytest.mark.skipif(
    not OPENSTOCK_BASE_URL,
    reason="set OPENSTOCK_BASE_URL env to run real OpenStock integration tests",
)

pytest_plugins: list[str] = []


def _post(path: str, body: dict[str, Any]) -> dict[str, Any]:
    req = urllib.request.Request(
        OPENSTOCK_BASE_URL + path,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


@pytest.mark.integration
class TestOpenStockRealBehavior:
    """验证 OpenStock 真实行为契约(用对参数名之后)。"""

    def test_probe1_quotes_single_symbol_returns_one_row(self):
        """发现 #1:用 params.symbol(单数)查 000001 → 1 条 sz000001,不是 50 条热点。"""
        body = _post(
            "/data/fetch",
            {"data_category": "REALTIME_QUOTES", "params": {"symbol": "000001"}},
        )
        data = body.get("data")
        assert isinstance(data, list), f"data should be list, got {type(data)}"
        assert len(data) == 1, f"expected 1 row for sz000001, got {len(data)}"
        assert data[0]["symbol"] == "sz000001"

    def test_probe2_quotes_returns_pct_chg_field(self):
        """发现 #2:OpenStock 真实返 pct_chg 字段(待 adapter 映射到 change_percent)。"""
        body = _post(
            "/data/fetch",
            {"data_category": "REALTIME_QUOTES", "params": {"symbol": "000001"}},
        )
        row = body["data"][0]
        assert "pct_chg" in row, f"OpenStock should return pct_chg, got keys={list(row.keys())}"

    def test_probe3_klines_returns_iso8601_timestamp(self):
        """发现 #3:OpenStock /data/bars 返 time 字段是 ISO8601 全时间戳。"""
        body = _post(
            "/data/bars",
            {"symbol": "000001", "period": "day", "count": 2},
        )
        data = body.get("data")
        assert isinstance(data, list) and len(data) >= 1
        time_str = data[0]["time"]
        # ISO8601 长度 > 10 (date 截断后是 10)
        assert len(time_str) > 10, f"expected ISO8601 full timestamp, got {time_str!r}"
        # 应能被 Python datetime.fromisoformat 解析(Python 3.11+ 支持 +08:00)
        from datetime import datetime
        dt = datetime.fromisoformat(time_str)
        assert dt.year >= 2026

    def test_probe4_invalid_symbol_returns_503(self):
        """发现 #4 更正:错 symbol 不是静默 fallback,而是 503 provider_unavailable。"""
        import urllib.error
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            _post(
                "/data/fetch",
                {"data_category": "REALTIME_QUOTES", "params": {"symbol": "999999"}},
            )
        assert exc_info.value.code == 503
        body_text = exc_info.value.read().decode("utf-8", errors="ignore")
        assert "provider_unavailable" in body_text or "invalid code" in body_text

    def test_probe5_klines_symbol_has_sz_prefix(self):
        """发现 #5:OpenStock /data/bars 返 symbol 带 sz/sh/bj 前缀(待 adapter 剥)。"""
        body = _post(
            "/data/bars",
            {"symbol": "000001", "period": "day", "count": 1},
        )
        row = body["data"][0]
        sym = row["symbol"]
        assert sym.startswith(("sz", "sh", "bj")), f"expected prefix, got {sym!r}"

    def test_probe_multi_symbol_comma_string_rejected(self):
        """决策点 #4 验证:逗号分隔多 symbol 被 provider 拒绝(503)。"""
        import urllib.error
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            _post(
                "/data/fetch",
                {"data_category": "REALTIME_QUOTES",
                 "params": {"symbol": "000001,600519"}},
            )
        assert exc_info.value.code == 503

    def test_probe_empty_params_returns_default_hots(self):
        """发现 #4 配套:无 symbol 参数 → OpenStock 返默认 50 条市场热点(不是空列表)。

        这是 OpenStock provider 的"未指定 symbol 时返热点榜"行为。
        adapter 修复后路由层显式传 symbol,不会触发此分支。
        若误用 `symbols`(复数) 参数,也会被忽略 → 触发此分支(见 test_probe_legacy_symbols_plural_ignored_returns_hot)。
        """
        body = _post(
            "/data/fetch",
            {"data_category": "REALTIME_QUOTES", "params": {}},
        )
        data = body.get("data")
        assert isinstance(data, list)
        # OpenStock 默认行为:无 symbol filter 时返 50 条热点榜
        assert len(data) > 0, "expected default hot list when no symbol filter"
        # 返回的应该是市场热点代码(非空 name 或非指定 sz000001)
        assert data[0]["symbol"] != "sz000001"

    def test_probe_legacy_symbols_plural_ignored_returns_hot(self):
        """发现 #1 根因:复数 symbols 参数被忽略 → 返 50 条默认热点。
        此 probe 用于证明为何 adapter 必须用单数 symbol。"""
        body = _post(
            "/data/fetch",
            {"data_category": "REALTIME_QUOTES",
             "params": {"symbols": "000001"}},
        )
        data = body.get("data")
        assert isinstance(data, list)
        # 复数被忽略 → 默认热点 50 条
        assert len(data) >= 10, "plural 'symbols' should be ignored, returning default hots"
        # 返回的应该是热点代码(sh689009 等),不是 sz000001
        assert data[0]["symbol"] != "sz000001", \
            "plural 'symbols' should NOT filter — if it does, adapter fix is broken"
