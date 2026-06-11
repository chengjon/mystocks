from __future__ import annotations

from pathlib import Path


def test_runtime_smoke_accepts_primary_or_fallback_quote_provider() -> None:
    script = Path("scripts/run_data_source_runtime_smoke.sh").read_text(encoding="utf-8")

    assert 'payload["source"] in {"eltdx", "akshare"}' in script
    assert '"eltdx.tdx_7709"' in script
    assert '"akshare.stock_zh_a_spot"' in script
    assert '"akshare.stock_info_a_code_name"' in script


def test_runtime_smoke_uses_provider_neutral_skip_setting() -> None:
    script = Path("scripts/run_data_source_runtime_smoke.sh").read_text(encoding="utf-8")
    env_example = Path("config/.env.data_sources.example").read_text(encoding="utf-8")

    assert "OPENSTOCK_SKIP_REALTIME_PROVIDER_SMOKE" in script
    assert "OPENSTOCK_SKIP_AKSHARE_REAL_SMOKE" in script
    assert '"request_id": "smoke-realtime-provider"' in script
    assert "OPENSTOCK_SKIP_REALTIME_PROVIDER_SMOKE=0" in env_example
