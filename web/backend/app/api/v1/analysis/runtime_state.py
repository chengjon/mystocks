from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
from uuid import uuid4


@dataclass
class StressHistoryEntry:
    test_id: str
    portfolio_id: str
    scenario: str
    impact: float
    passed: bool
    projected_value: float
    drawdown: float
    run_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AnalysisRuntimeStore:
    def __init__(self) -> None:
        self.stress_test_history: List[StressHistoryEntry] = []

    def reset(self) -> None:
        self.stress_test_history.clear()

    def record_stress_test(
        self,
        *,
        portfolio_id: str,
        scenario: str,
        impact: float,
        passed: bool,
        projected_value: float,
        drawdown: float,
    ) -> StressHistoryEntry:
        entry = StressHistoryEntry(
            test_id=f"stress_{uuid4().hex[:12]}",
            portfolio_id=portfolio_id,
            scenario=scenario,
            impact=impact,
            passed=passed,
            projected_value=projected_value,
            drawdown=drawdown,
        )
        self.stress_test_history.append(entry)
        return entry

    def get_stress_history(self, *, portfolio_id: str, limit: int) -> List[StressHistoryEntry]:
        items = [item for item in self.stress_test_history if item.portfolio_id == portfolio_id]
        items.sort(key=lambda item: item.run_at, reverse=True)
        return items[:limit]


runtime_store = AnalysisRuntimeStore()
