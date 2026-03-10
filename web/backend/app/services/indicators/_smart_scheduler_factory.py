"""Factory helper for `SmartScheduler`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .smart_scheduler import CalculationMode, SmartScheduler


def create_scheduler(
    max_workers: int = 4,
    mode: "CalculationMode" = None,
    enable_cache: bool = True,
    enable_distributed_lock: bool = True,
) -> "SmartScheduler":
    """创建调度器。"""
    from .smart_scheduler import CalculationMode, SmartScheduler

    if mode is None:
        mode = CalculationMode.ASYNC_PARALLEL

    return SmartScheduler(
        max_workers=max_workers,
        mode=mode,
        enable_cache=enable_cache,
        enable_distributed_lock=enable_distributed_lock,
    )
