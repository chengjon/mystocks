from decimal import Decimal

from app.models.market_data import LongHuBangData
from app.services.indicators.smart_scheduler import CalculationMode, SmartScheduler, create_scheduler


def test_long_hu_bang_to_dict_sanitizes_non_finite_numbers():
    record = LongHuBangData(
        symbol="600519",
        name="贵州茅台",
        reason="涨幅偏离值达7%",
        buy_amount=Decimal("NaN"),
        sell_amount=Decimal("Infinity"),
        net_amount=Decimal("-Infinity"),
        turnover_rate=Decimal("8.6"),
        institution_buy=Decimal("0"),
        institution_sell=None,
    )

    payload = record.to_dict()

    assert payload["buy_amount"] is None
    assert payload["sell_amount"] is None
    assert payload["net_amount"] is None
    assert payload["turnover_rate"] == 8.6
    assert payload["institution_buy"] == 0
    assert payload["institution_sell"] == 0


def test_create_scheduler_remains_available_on_legacy_module_path():
    scheduler = create_scheduler(max_workers=2, mode=CalculationMode.SYNC)

    assert isinstance(scheduler, SmartScheduler)
    assert scheduler.max_workers == 2
    assert scheduler.mode == CalculationMode.SYNC
