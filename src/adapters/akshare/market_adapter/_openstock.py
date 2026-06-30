"""
OpenStock client factory for AkshareMarketDataAdapter.

Provides ``_build_default_openstock_client()`` so the adapter can construct
an ``OpenStockClient`` from environment variables when none is injected.
Reuses the Phase 1.1 endpoint-layer factory logic previously in
``web/backend/app/api/akshare_market/fund_flow.py:_build_openstock_client()``.

Once all Mixins migrate (Wave 3 closeout), the endpoint-layer copy can be
removed and this becomes the single canonical factory.
"""

from __future__ import annotations

import os

from app.services.openstock_client import OpenStockClient, OpenStockClientConfig

# Default base URL matches Phase 1.1 endpoint layer convention
# (fund_flow.py:18, market_data_request.py:46).
_DEFAULT_OPENSTOCK_BASE_URL = "http://192.168.123.104:8040"


def _build_default_openstock_client() -> OpenStockClient:
    """Build an ``OpenStockClient`` from environment variables.

    Environment variables read:
    - ``OPENSTOCK_BASE_URL``: optional override of ``DEFAULT_OPENSTOCK_BASE_URL``
    - ``OPENSTOCK_TIMEOUT_SECONDS``: float, default 5.0
    - ``OPENSTOCK_API_KEY``: optional API key (stripped, ``None`` if empty)
    """
    base_url = os.getenv("OPENSTOCK_BASE_URL") or _DEFAULT_OPENSTOCK_BASE_URL
    try:
        timeout_seconds = float(os.getenv("OPENSTOCK_TIMEOUT_SECONDS", "5.0"))
    except ValueError:
        timeout_seconds = 5.0
    api_key = os.getenv("OPENSTOCK_API_KEY", "").strip() or None

    return OpenStockClient(
        OpenStockClientConfig(
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            api_key=api_key,
        )
    )
