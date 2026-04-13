from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class TrainedStrategyState:
    strategy_id: str
    strategy_type: str
    symbol: str
    parameters: dict[str, Any]
    trained: bool
    performance: dict[str, float]
    feature_importance: dict[str, float]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class StrategyRuntimeStore:
    def __init__(self) -> None:
        self.strategies: dict[str, TrainedStrategyState] = {}

    def reset(self) -> None:
        self.strategies.clear()

    def upsert(self, item: TrainedStrategyState) -> TrainedStrategyState:
        item.updated_at = datetime.now(timezone.utc)
        self.strategies[item.strategy_id] = item
        return item

    def get(self, strategy_id: str) -> TrainedStrategyState | None:
        return self.strategies.get(strategy_id)

    def list(self, *, strategy_type: str | None = None, trained_only: bool = False) -> list[TrainedStrategyState]:
        items = list(self.strategies.values())
        if strategy_type:
            items = [item for item in items if item.strategy_type == strategy_type]
        if trained_only:
            items = [item for item in items if item.trained]
        return sorted(items, key=lambda item: item.updated_at, reverse=True)


runtime_store = StrategyRuntimeStore()
