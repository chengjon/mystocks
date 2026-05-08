from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any

from app.models.strategy_schemas import BacktestResult, TradeRecord

from ..errors import AttributionDependencyError
from ..market_data_dependencies import AttributionMarketDataDependencies, normalize_baostock_symbol
from ..models import (
    BenchmarkConstituentSnapshot,
    FactorExposureSnapshot,
    PortfolioConstituentSnapshot,
)


@dataclass(slots=True)
class BacktestAttributionSnapshot:
    analysis_date: str
    portfolio: list[PortfolioConstituentSnapshot]
    benchmark: list[BenchmarkConstituentSnapshot]
    factors: FactorExposureSnapshot


def _field(payload: BacktestResult | dict[str, Any], name: str, default: Any = None) -> Any:
    if isinstance(payload, dict):
        return payload.get(name, default)
    return getattr(payload, name, default)


def _trade_field(trade: TradeRecord | dict[str, Any], name: str, default: Any = None) -> Any:
    if isinstance(trade, dict):
        return trade.get(name, default)
    return getattr(trade, name, default)


def _normalize_trade_date(value: date | datetime) -> date:
    if isinstance(value, datetime):
        return value.date()
    return value


def _resolve_analysis_date(backtest_result: BacktestResult | dict[str, Any]) -> str:
    trades = _field(backtest_result, "trades", [])
    trade_dates = [_normalize_trade_date(_trade_field(trade, "trade_date")) for trade in trades if _trade_field(trade, "trade_date")]
    if trade_dates:
        return max(trade_dates).isoformat()
    end_date = _field(backtest_result, "end_date")
    if isinstance(end_date, date):
        return end_date.isoformat()
    raise AttributionDependencyError("unable to resolve backtest analysis date")


def _direction_sign(value: str) -> int:
    direction = str(value or "").strip().lower()
    if direction in {"buy", "long"}:
        return 1
    if direction in {"sell", "short"}:
        return -1
    raise AttributionDependencyError(f"unsupported trade direction: {value}")


def _project_trade_positions(trades: list[TradeRecord | dict[str, Any]]) -> list[dict[str, Any]]:
    positions: dict[str, dict[str, Any]] = defaultdict(lambda: {"symbol": "", "quantity": 0, "cost_basis": 0.0, "last_price": 0.0})

    for trade in trades:
        symbol = str(_trade_field(trade, "symbol")).upper()
        quantity = int(_trade_field(trade, "quantity", _trade_field(trade, "amount", 0)) or 0)
        if quantity <= 0:
            continue
        price = float(_trade_field(trade, "price", 0.0) or 0.0)
        sign = _direction_sign(_trade_field(trade, "direction", _trade_field(trade, "action", "buy")))
        entry = positions[symbol]
        entry["symbol"] = symbol
        entry["quantity"] += sign * quantity
        if sign > 0:
            entry["cost_basis"] += quantity * price
        else:
            entry["cost_basis"] = max(entry["cost_basis"] - (quantity * price), 0.0)
        entry["last_price"] = price

    projected = [entry for entry in positions.values() if entry["quantity"] > 0]
    if not projected:
        raise AttributionDependencyError("backtest has no open positions for attribution")
    return projected


def _aggregate_weighted_factor_exposures(
    *,
    symbols: list[str],
    weights: dict[str, float],
    exposure_map: dict[str, dict[str, float]],
) -> dict[str, float]:
    aggregated = {factor: 0.0 for factor in ["size", "value", "momentum", "volatility", "quality"]}
    for symbol in symbols:
        exposures = exposure_map.get(symbol)
        if exposures is None:
            raise AttributionDependencyError(f"missing factor exposures for {symbol}")
        for factor_name in aggregated:
            aggregated[factor_name] += weights[symbol] * float(exposures.get(factor_name, 0.0))
    return {factor_name: round(value, 10) for factor_name, value in aggregated.items()}


def _build_portfolio_snapshots(
    *,
    projected_positions: list[dict[str, Any]],
    analysis_date: str,
    start_date: datetime,
    end_date: datetime,
    dependencies: AttributionMarketDataDependencies,
) -> list[PortfolioConstituentSnapshot]:
    symbols = [entry["symbol"] for entry in projected_positions]
    industries = dependencies.load_industry_classification(symbols, analysis_date)
    market_values = {entry["symbol"]: round(entry["quantity"] * entry["last_price"], 10) for entry in projected_positions}
    total_market_value = sum(market_values.values())
    if total_market_value <= 0:
        raise AttributionDependencyError("invalid projected market value for backtest attribution")

    return [
        PortfolioConstituentSnapshot(
            analysis_date=analysis_date,
            symbol=symbol,
            weight=round(market_values[symbol] / total_market_value, 10),
            market_value=market_values[symbol],
            return_rate=dependencies.load_return_rate(symbol, start_date, end_date),
            industry=industries[symbol],
        )
        for symbol in symbols
    ]


def _resolve_benchmark_rows(
    *,
    analysis_date: str,
    start_date: datetime,
    end_date: datetime,
    dependencies: AttributionMarketDataDependencies,
) -> list[BenchmarkConstituentSnapshot]:
    frame = dependencies.load_benchmark_constituents(analysis_date)
    symbol_column = "code" if "code" in frame.columns else frame.columns[0]
    benchmark_symbols = [normalize_baostock_symbol(value) for value in frame[symbol_column].tolist()]
    industries = dependencies.load_industry_classification(benchmark_symbols, analysis_date)
    raw_weights = [float(value or 0.0) for value in frame["weight"].tolist()] if "weight" in frame.columns else []
    if raw_weights:
        weight_total = sum(raw_weights)
        normalized_weights = [weight / weight_total if weight_total > 0 else 0.0 for weight in raw_weights]
    else:
        normalized_weights = [1.0 / len(benchmark_symbols)] * len(benchmark_symbols)

    benchmark_rows: list[BenchmarkConstituentSnapshot] = []
    for symbol, weight in zip(benchmark_symbols, normalized_weights, strict=True):
        benchmark_rows.append(
            BenchmarkConstituentSnapshot(
                analysis_date=analysis_date,
                symbol=symbol,
                weight=round(weight, 10),
                return_rate=dependencies.load_return_rate(symbol, start_date, end_date),
                industry=industries[symbol],
            )
        )
    return benchmark_rows


def _to_snapshot_result(
    *,
    analysis_date: str,
    portfolio: list[PortfolioConstituentSnapshot],
    benchmark: list[BenchmarkConstituentSnapshot],
    dependencies: AttributionMarketDataDependencies,
) -> BacktestAttributionSnapshot:
    portfolio_symbols = [row.symbol for row in portfolio]
    benchmark_symbols = [row.symbol for row in benchmark]
    portfolio_weights = {row.symbol: row.weight for row in portfolio}
    benchmark_weights = {row.symbol: row.weight for row in benchmark}

    portfolio_exposure_map = dependencies.load_factor_exposure_map(portfolio_symbols, analysis_date)
    benchmark_exposure_map = dependencies.load_factor_exposure_map(benchmark_symbols, analysis_date)

    return BacktestAttributionSnapshot(
        analysis_date=analysis_date,
        portfolio=portfolio,
        benchmark=benchmark,
        factors=FactorExposureSnapshot(
            analysis_date=analysis_date,
            portfolio=_aggregate_weighted_factor_exposures(
                symbols=portfolio_symbols,
                weights=portfolio_weights,
                exposure_map=portfolio_exposure_map,
            ),
            benchmark=_aggregate_weighted_factor_exposures(
                symbols=benchmark_symbols,
                weights=benchmark_weights,
                exposure_map=benchmark_exposure_map,
            ),
        ),
    )


def build_backtest_attribution_snapshot(
    *,
    backtest_result: BacktestResult | dict[str, Any],
    dependencies: AttributionMarketDataDependencies,
) -> BacktestAttributionSnapshot:
    analysis_date = _resolve_analysis_date(backtest_result)
    start_value = _field(backtest_result, "start_date")
    if not isinstance(start_value, date):
        raise AttributionDependencyError("backtest start_date is required for attribution")

    start_date = datetime.combine(start_value, time.min)
    end_date = datetime.combine(date.fromisoformat(analysis_date), time.min) + timedelta(days=1)
    projected_positions = _project_trade_positions(_field(backtest_result, "trades", []))
    portfolio = _build_portfolio_snapshots(
        projected_positions=projected_positions,
        analysis_date=analysis_date,
        start_date=start_date,
        end_date=end_date,
        dependencies=dependencies,
    )
    benchmark = _resolve_benchmark_rows(
        analysis_date=analysis_date,
        start_date=start_date,
        end_date=end_date,
        dependencies=dependencies,
    )
    return _to_snapshot_result(
        analysis_date=analysis_date,
        portfolio=portfolio,
        benchmark=benchmark,
        dependencies=dependencies,
    )


def _from_trade_projection_for_test(
    *,
    backtest_result: BacktestResult | dict[str, Any],
    analysis_date: str,
) -> BacktestAttributionSnapshot:
    projected_positions = _project_trade_positions(_field(backtest_result, "trades", []))
    total_market_value = sum(entry["quantity"] * entry["last_price"] for entry in projected_positions)
    portfolio = [
        PortfolioConstituentSnapshot(
            analysis_date=analysis_date,
            symbol=entry["symbol"],
            weight=round((entry["quantity"] * entry["last_price"]) / total_market_value, 10),
            market_value=round(entry["quantity"] * entry["last_price"], 10),
            return_rate=0.0,
            industry="UNKNOWN",
        )
        for entry in projected_positions
    ]
    return BacktestAttributionSnapshot(
        analysis_date=analysis_date,
        portfolio=portfolio,
        benchmark=[],
        factors=FactorExposureSnapshot(analysis_date=analysis_date, portfolio={}, benchmark={}),
    )


build_backtest_attribution_snapshot._from_trade_projection_for_test = _from_trade_projection_for_test
