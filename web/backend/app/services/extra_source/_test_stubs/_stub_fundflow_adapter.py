"""Stub adapter that conflicts with FUND_FLOW (a static OpenStock category).

Used to verify Layer 1's static-category guard rejects registration at
lifespan startup, causing the app to fail fast.
"""

from __future__ import annotations

from typing import Any

from app.services.extra_source import ExtraSourceMeta, ExtraSourceResult


class FundFlowOverlapAdapter:
    """Adapter that intentionally conflicts with the FUND_FLOW static
    category — registration MUST raise ExtraSourceCategoryConflictError.
    """

    def __init__(self) -> None:
        self._meta = ExtraSourceMeta(
            name="fundflow-bad",
            category="FUND_FLOW",  # overlaps OpenStock static inventory
        )

    def get_meta(self) -> ExtraSourceMeta:
        return self._meta

    def fetch(self, params: dict[str, Any]) -> ExtraSourceResult:
        return ExtraSourceResult(data={}, provider_used="fundflow-bad")
