"""
Backtesting API Pydantic Models

Defines Pydantic models for backtesting related API requests and responses.
Uses centralized mock data for examples.

Version: 1.0.0
Date: 2025-12-26
"""

from typing import Dict, List, Optional, Any
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.mock.unified_mock_data import get_backtest_data


def _get_request_example():
    return {
        "strategy_name": "SimpleMovingAverage",
        "symbols": ["600000.SH", "000001.SZ"],
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "initial_capital": 100000.0,
        "parameters": {"short_window": 10, "long_window": 30},
    }


class BacktestRequest(BaseModel):
    """
    Request model for initiating a backtest.
    """

    strategy_name: str = Field(..., description="Name of the strategy to backtest")
    symbols: List[str] = Field(..., description="List of stock symbols to backtest")
    start_date: date = Field(..., description="Start date of the backtest")
    end_date: date = Field(..., description="End date of the backtest")
    initial_capital: float = Field(..., description="Initial capital for the backtest", gt=0)
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Strategy parameters")

    class Config:
        json_schema_extra = {"example": _get_request_example()}


class BacktestTrade(BaseModel):
    """
    Model representing a single trade in the backtest result.
    """

    symbol: str = Field(..., description="Stock symbol")
    entry_date: datetime = Field(..., description="Entry date and time")
    exit_date: datetime = Field(..., description="Exit date and time")
    entry_price: float = Field(..., description="Entry price")
    exit_price: float = Field(..., description="Exit price")
    quantity: int = Field(..., description="Quantity traded")
    pnl: float = Field(..., description="Profit and Loss")
    return_pct: float = Field(..., description="Return percentage")


class BacktestResultSummary(BaseModel):
    """
    Summary metrics of the backtest.
    """

    total_return: float = Field(..., description="Total return")
    annualized_return: float = Field(..., description="Annualized return")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    win_rate: float = Field(..., description="Win rate")
    total_trades: int = Field(..., description="Total number of trades")


class BacktestResponse(BaseModel):
    """
    Response model for backtest results.
    """

    task_id: str = Field(..., description="Unique ID of the backtest task")
    status: str = Field(..., description="Status of the backtest (e.g., 'completed', 'failed')")
    summary: Optional[BacktestResultSummary] = Field(None, description="Summary metrics")
    equity_curve: List[Dict[str, Any]] = Field(default_factory=list, description="Equity curve data points")
    trades: List[BacktestTrade] = Field(default_factory=list, description="List of trades executed")
    error_message: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {"example": get_backtest_data()}
