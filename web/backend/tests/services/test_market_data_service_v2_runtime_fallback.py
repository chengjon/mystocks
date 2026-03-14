import os
from datetime import date

import pandas as pd

os.environ.setdefault("POSTGRESQL_HOST", "localhost")
os.environ.setdefault("POSTGRESQL_PORT", "5432")
os.environ.setdefault("POSTGRESQL_USER", "tester")
os.environ.setdefault("POSTGRESQL_PASSWORD", "tester")
os.environ.setdefault("POSTGRESQL_DATABASE", "tester")

from web.backend.app.services.market_data_service_v2 import MarketDataServiceV2


class _FailingSessionFactory:
    def __call__(self):
        raise RuntimeError("db unavailable")


class _ScalarQuery:
    def filter(self, *_args, **_kwargs):
        return self

    def scalar(self):
        return None


class _EmptySession:
    def query(self, *_args, **_kwargs):
        return _ScalarQuery()

    def close(self):
        return None


def _sector_frame():
    return pd.DataFrame(
        [
            {
                "代码": "BK0420",
                "名称": "证券",
                "最新价": 1240.5,
                "涨跌幅": 2.56,
                "主力净流入": 3200000000,
                "主力净流入占比": 7.58,
                "超大单净流入": 1800000000,
                "超大单净流入占比": 4.2,
                "大单净流入": 900000000,
                "大单净流入占比": 2.1,
                "中单净流入": -400000000,
                "中单净流入占比": -1.2,
                "小单净流入": -700000000,
                "小单净流入占比": -2.9,
            },
            {
                "代码": "BK0475",
                "名称": "银行",
                "最新价": 980.2,
                "涨跌幅": 1.23,
                "主力净流入": 1500000000,
                "主力净流入占比": 3.21,
                "超大单净流入": 600000000,
                "超大单净流入占比": 1.1,
                "大单净流入": 500000000,
                "大单净流入占比": 0.8,
                "中单净流入": -300000000,
                "中单净流入占比": -0.7,
                "小单净流入": -800000000,
                "小单净流入占比": -1.9,
            },
        ]
    )


def test_query_sector_fund_flow_uses_runtime_fallback_when_db_unavailable(monkeypatch):
    monkeypatch.setenv("TESTING", "true")
    service = MarketDataServiceV2()
    service.SessionLocal = _FailingSessionFactory()
    monkeypatch.setattr(service.em_adapter, "get_sector_fund_flow", lambda sector_type, timeframe: _sector_frame())

    result = service.query_sector_fund_flow("行业", "今日", 2)

    assert len(result) == 2
    assert result[0]["sector_name"] == "证券"
    assert result[0]["trade_date"] == date.today().isoformat()
    assert result[0]["main_net_inflow"] == 3200000000.0


def test_query_sector_fund_flow_uses_runtime_fallback_when_db_has_no_latest_date(monkeypatch):
    monkeypatch.setenv("DEVELOPMENT_MODE", "true")
    service = MarketDataServiceV2()
    service.SessionLocal = _EmptySession
    monkeypatch.setattr(service.em_adapter, "get_sector_fund_flow", lambda sector_type, timeframe: _sector_frame())

    result = service.query_sector_fund_flow("行业", "今日", 1)

    assert len(result) == 1
    assert result[0]["sector_code"] == "BK0420"
    assert result[0]["change_percent"] == 2.56
