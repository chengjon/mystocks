"""
API Version Mapping Configuration
This file serves as the Single Source of Truth for API versioning.
"""

VERSION_MAPPING = {
    # Authentication (Existing v1)
    "auth": {
        "prefix": "/api/v1/auth",
        "version": "1.0.0",
        "tags": ["auth"],
        "endpoints": {"login": "/login", "logout": "/logout", "me": "/me", "refresh": "/refresh", "csrf": "/csrf"},
    },
    # Market Data (Upgrading to v1)
    "market": {
        "prefix": "/api/v1/market",
        "version": "1.0.0",
        "tags": ["market-v1"],
        "endpoints": {
            "kline": "/kline",
            "quotes": "/quotes",
            "fund_flow": "/fund-flow",
            "fund_flow_refresh": "/fund-flow/refresh",
            "etf": "/etf",
            "chip_race": "/chip-race",
            "lhb": "/lhb",
        },
    },
    # Market V2 (Newer market data API)
    "market_v2": {
        "prefix": "/api/v2/market",
        "version": "2.0.0",
        "tags": ["market-v2"],
    },
    # Strategy Management (Upgrading to v1)
    "strategy": {
        "prefix": "/api/v1/strategy",
        "version": "1.0.0",
        "tags": ["strategy-v1"],
        "endpoints": {
            "strategies": "/strategies",
            "models": "/models",
            "backtest": "/backtest",
            "definitions": "/definitions",
            "run_single": "/run/single",
            "run_batch": "/run/batch",
            "results": "/results",
        },
    },
    # Monitoring (Upgrading to v1)
    "monitoring": {
        "prefix": "/api/v1/monitoring",
        "version": "1.0.0",
        "tags": ["monitoring-v1"],
        "endpoints": {
            "alert_rules": "/alert-rules",
            "alerts": "/alerts",
            "realtime": "/realtime",
            "dragon_tiger": "/dragon-tiger",
        },
    },
    # Trading (Upgrading to v1)
    "trade": {
        "prefix": "/api/v1/trade",
        "version": "1.0.0",
        "tags": ["trade-v1"],
    },
    # Technical Analysis (Upgrading to v1)
    "technical": {
        "prefix": "/api/v1/technical",
        "version": "1.0.0",
        "tags": ["technical-v1"],
    },
    # Data Management (Upgrading to v1)
    "data": {
        "prefix": "/api/v1/data",
        "version": "1.0.0",
        "tags": ["data-v1"],
    },
    # System (Upgrading to v1)
    "system": {
        "prefix": "/api/v1/system",
        "version": "1.0.0",
        "tags": ["system-v1"],
    },
    # Indicators (Upgrading to v1)
    "indicators": {
        "prefix": "/api/v1/indicators",
        "version": "1.0.0",
        "tags": ["indicators-v1"],
    },
    # TDX (Upgrading to v1)
    "tdx": {
        "prefix": "/api/v1/tdx",
        "version": "1.0.0",
        "tags": ["tdx-v1"],
    },
    # Announcement (Upgrading to v1)
    "announcement": {
        "prefix": "/api/v1/announcement",
        "version": "1.0.0",
        "tags": ["announcement-v1"],
    },
}
