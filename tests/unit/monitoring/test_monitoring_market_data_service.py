from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.monitoring_market_data_service import MonitoringMarketDataService


class FakeQuery:
    def __init__(self, *, first_result=None, all_result=None):
        self.first_result = first_result
        self.all_result = list(all_result or [])
        self.filters = []
        self.order_calls = 0
        self.limit_value = None

    def filter(self, *criteria):
        self.filters.extend(criteria)
        return self

    def order_by(self, *criteria):
        self.order_calls += 1
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def first(self):
        return self.first_result

    def all(self):
        return self.all_result


class FakeSession:
    def __init__(self, query):
        self.query_object = query
        self.queried_models = []
        self.closed = False

    def query(self, model):
        self.queried_models.append(model.__name__)
        return self.query_object

    def close(self):
        self.closed = True


class FakeMonitoringSource:
    def __init__(self, session=None):
        self.session = session
        self.realtime_frame = None
        self.dragon_tiger_frame = None
        self.saved_realtime_count = 0
        self.saved_dragon_tiger_count = 0
        self.alerts = []
        self.calls = []

    def get_session(self):
        self.calls.append(("get_session",))
        return self.session

    def fetch_realtime_data(self, symbols):
        self.calls.append(("fetch_realtime_data", tuple(symbols)))
        return self.realtime_frame

    def save_realtime_data(self, frame):
        self.calls.append(("save_realtime_data", frame))
        return self.saved_realtime_count

    def evaluate_alert_rules(self, frame):
        self.calls.append(("evaluate_alert_rules", frame))
        return self.alerts

    def fetch_dragon_tiger_list(self, trade_date):
        self.calls.append(("fetch_dragon_tiger_list", trade_date))
        return self.dragon_tiger_frame

    def save_dragon_tiger_data(self, frame, trade_date):
        self.calls.append(("save_dragon_tiger_data", frame, trade_date))
        return self.saved_dragon_tiger_count


class FakeFrame:
    def __init__(self, *, rows=0):
        self._rows = rows

    @property
    def empty(self):
        return self._rows == 0

    def __len__(self):
        return self._rows


def realtime_record(**overrides):
    payload = {
        "id": 1,
        "symbol": "600519",
        "stock_name": "贵州茅台",
        "timestamp": datetime(2026, 5, 14, 10, 30),
        "trade_date": date(2026, 5, 14),
        "price": 1688.0,
        "change_percent": 1.25,
        "volume": 1000,
        "amount": 1688000.0,
        "indicators": {"rsi": 62},
        "market_strength": "strong",
        "is_limit_up": False,
        "is_limit_down": False,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def dragon_tiger_record(**overrides):
    payload = {
        "id": 9,
        "symbol": "000001",
        "stock_name": "平安银行",
        "trade_date": date(2026, 5, 14),
        "reason": "日涨幅偏离值达7%",
        "total_buy_amount": 32000000.0,
        "total_sell_amount": 12000000.0,
        "net_amount": 20000000.0,
        "institution_buy_count": 2,
        "institution_sell_count": 1,
        "institution_net_amount": 18000000.0,
        "detail_data": {"seats": []},
        "impact_score": 85,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def test_market_data_service_gets_latest_realtime_record_and_closes_session():
    query = FakeQuery(first_result=realtime_record())
    session = FakeSession(query)
    service = MonitoringMarketDataService(FakeMonitoringSource(session))

    result = service.get_realtime_monitoring("600519")

    assert result.symbol == "600519"
    assert result.stock_name == "贵州茅台"
    assert session.closed is True
    assert session.queried_models == ["RealtimeMonitoring"]
    assert query.order_calls == 1


def test_market_data_service_lists_today_realtime_records_with_filters_and_limit():
    query = FakeQuery(all_result=[realtime_record(symbol="600519"), realtime_record(symbol="000001")])
    session = FakeSession(query)
    service = MonitoringMarketDataService(FakeMonitoringSource(session))

    result = service.list_realtime_monitoring(
        symbols="600519,000001",
        limit=50,
        is_limit_up=True,
        is_limit_down=False,
    )

    assert [item.symbol for item in result] == ["600519", "000001"]
    assert session.closed is True
    assert session.queried_models == ["RealtimeMonitoring"]
    assert query.limit_value == 50
    assert len(query.filters) == 4


def test_market_data_service_fetches_saves_and_evaluates_realtime_data():
    source = FakeMonitoringSource()
    source.realtime_frame = FakeFrame(rows=3)
    source.saved_realtime_count = 3
    source.alerts = [object(), object()]
    service = MonitoringMarketDataService(source)

    result = service.fetch_realtime_data(["600519", "000001"])

    assert result == {"stocks_count": 3, "saved_count": 3, "alerts_triggered": 2}
    assert source.calls == [
        ("fetch_realtime_data", ("600519", "000001")),
        ("save_realtime_data", source.realtime_frame),
        ("evaluate_alert_rules", source.realtime_frame),
    ]


def test_market_data_service_returns_none_when_realtime_source_is_empty():
    source = FakeMonitoringSource()
    source.realtime_frame = FakeFrame(rows=0)
    service = MonitoringMarketDataService(source)

    assert service.fetch_realtime_data(["600519"]) is None
    assert source.calls == [("fetch_realtime_data", ("600519",))]


def test_market_data_service_lists_dragon_tiger_records_and_closes_session():
    query = FakeQuery(all_result=[dragon_tiger_record()])
    session = FakeSession(query)
    service = MonitoringMarketDataService(FakeMonitoringSource(session))

    result = service.list_dragon_tiger(
        trade_date=date(2026, 5, 14),
        symbol="000001",
        min_net_amount=10000000.0,
        limit=20,
    )

    assert result[0].symbol == "000001"
    assert result[0].net_amount == 20000000.0
    assert session.closed is True
    assert session.queried_models == ["DragonTigerList"]
    assert query.limit_value == 20
    assert len(query.filters) == 3


def test_market_data_service_fetches_and_saves_dragon_tiger_data():
    trade_date = date(2026, 5, 14)
    source = FakeMonitoringSource()
    source.dragon_tiger_frame = FakeFrame(rows=4)
    source.saved_dragon_tiger_count = 4
    service = MonitoringMarketDataService(source)

    result = service.fetch_dragon_tiger_data(trade_date)

    assert result == {"trade_date": "2026-05-14", "count": 4}
    assert source.calls == [
        ("fetch_dragon_tiger_list", trade_date),
        ("save_dragon_tiger_data", source.dragon_tiger_frame, trade_date),
    ]


def test_market_data_service_returns_none_when_dragon_tiger_source_is_empty():
    trade_date = date(2026, 5, 14)
    source = FakeMonitoringSource()
    source.dragon_tiger_frame = FakeFrame(rows=0)
    service = MonitoringMarketDataService(source)

    assert service.fetch_dragon_tiger_data(trade_date) is None
    assert source.calls == [("fetch_dragon_tiger_list", trade_date)]
