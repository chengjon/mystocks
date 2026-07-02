"""Stub ExtraSource adapter for integration tests.

Synthetic test fixture — returns canned data for MARKET_BIG_DEAL
category. NOT real historical data.
"""

from __future__ import annotations

from typing import Any

from app.services.extra_source import ExtraSourceMeta, ExtraSourceResult


class BigDealAdapter:
    """Stub adapter — mimics what a real MARKET_BIG_DEAL ExtraSource
    would do (until OpenStock registers that category natively).
    """

    def __init__(self) -> None:
        self._meta = ExtraSourceMeta(
            name="big-deal-stub",
            category="MARKET_BIG_DEAL",
            expires_on=None,  # 常规 ExtraSource, 非 TEMP_OVERRIDE
        )

    def get_meta(self) -> ExtraSourceMeta:
        return self._meta

    def fetch(self, params: dict[str, Any]) -> ExtraSourceResult:
        # Synthetic data — NOT historical market data
        return ExtraSourceResult(
            data={"rows": [{"deal": "stubbed"}]},
            provider_used="big-deal-stub",
        )
