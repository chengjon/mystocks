"""Shared public contract for strategy backtest status routes."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BacktestStatusResponse(BaseModel):
    """Public v1/deprecated-compatible backtest status payload."""

    backtest_id: int = Field(..., description="回测ID", ge=1)
    status: str = Field(..., description="回测状态")
    created_at: datetime | None = Field(None, description="创建时间")
    started_at: datetime | None = Field(None, description="开始时间")
    completed_at: datetime | None = Field(None, description="完成时间")
    error_message: str | None = Field(None, description="错误信息")
    has_results: bool = Field(..., description="是否已生成回测结果")


def build_backtest_status_response(backtest_id: int, backtest: Any) -> BacktestStatusResponse:
    """Normalize repository backtest records into the public route contract."""
    return BacktestStatusResponse(
        backtest_id=backtest_id,
        status=backtest.status.value if hasattr(backtest.status, "value") else backtest.status,
        created_at=backtest.created_at,
        started_at=backtest.started_at,
        completed_at=backtest.completed_at,
        error_message=backtest.error_message,
        has_results=backtest.performance_metrics is not None,
    )
