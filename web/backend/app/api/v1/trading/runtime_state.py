from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


@dataclass
class SessionState:
    session_id: str
    symbol: str
    strategy_id: Optional[str]
    status: str
    initial_capital: float
    current_capital: float
    position_size: float
    risk_threshold: float
    current_positions: int = 0
    daily_pnl: float = 0.0
    total_pnl: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PositionState:
    position_id: str
    session_id: str
    symbol: str
    name: str
    quantity: int
    average_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float
    weight: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TradingRuntimeStore:
    def __init__(self) -> None:
        self.sessions: dict[str, SessionState] = {}
        self.positions: dict[str, PositionState] = {}
        self.current_session_id: Optional[str] = None

    def reset(self) -> None:
        self.sessions.clear()
        self.positions.clear()
        self.current_session_id = None

    def create_session(
        self,
        *,
        symbol: str,
        strategy_id: Optional[str],
        initial_capital: float,
        position_size: float,
        risk_threshold: float,
    ) -> SessionState:
        session_id = f"session_{uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        session = SessionState(
            session_id=session_id,
            symbol=symbol,
            strategy_id=strategy_id,
            status="active",
            initial_capital=initial_capital,
            current_capital=initial_capital,
            position_size=position_size,
            risk_threshold=risk_threshold,
            created_at=now,
            updated_at=now,
        )
        self.sessions[session_id] = session
        self.current_session_id = session_id
        return session

    def list_sessions(self, *, symbol: Optional[str] = None, status: Optional[str] = None) -> list[SessionState]:
        sessions = list(self.sessions.values())
        if symbol:
            sessions = [item for item in sessions if item.symbol == symbol]
        if status:
            sessions = [item for item in sessions if item.status == status]
        return sorted(sessions, key=lambda item: item.created_at, reverse=True)

    def get_session(self, session_id: str) -> Optional[SessionState]:
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, action: str) -> Optional[SessionState]:
        session = self.sessions.get(session_id)
        if session is None:
            return None
        action_map = {"start": "active", "pause": "paused", "stop": "stopped"}
        session.status = action_map.get(action, session.status)
        session.updated_at = datetime.now(timezone.utc)
        if session.status == "active":
            self.current_session_id = session_id
        return session

    def delete_session(self, session_id: str) -> bool:
        session = self.sessions.pop(session_id, None)
        if session is None:
            return False
        position_ids = [pid for pid, position in self.positions.items() if position.session_id == session_id]
        for pid in position_ids:
            self.positions.pop(pid, None)
        if self.current_session_id == session_id:
            self.current_session_id = None
        return True

    def _resolve_session(self, session_id: Optional[str] = None) -> Optional[SessionState]:
        if session_id:
            return self.sessions.get(session_id)
        if self.current_session_id:
            session = self.sessions.get(self.current_session_id)
            if session and session.status == "active":
                return session
        active_sessions = [item for item in self.sessions.values() if item.status == "active"]
        if active_sessions:
            active_sessions.sort(key=lambda item: item.updated_at, reverse=True)
            session = active_sessions[0]
            self.current_session_id = session.session_id
            return session
        return None

    def list_positions(self, *, symbol: Optional[str] = None, session_id: Optional[str] = None) -> list[PositionState]:
        positions = list(self.positions.values())
        if symbol:
            positions = [item for item in positions if item.symbol == symbol]
        if session_id:
            positions = [item for item in positions if item.session_id == session_id]
        return sorted(positions, key=lambda item: item.created_at, reverse=True)

    def get_position(self, position_id: str) -> Optional[PositionState]:
        return self.positions.get(position_id)

    def create_position(self, *, symbol: str, quantity: int, price: float, session_id: Optional[str] = None) -> PositionState:
        session = self._resolve_session(session_id)
        if session is None:
            raise ValueError('No active trading session available for position creation')
        now = datetime.now(timezone.utc)
        position_id = f"pos_{uuid4().hex[:12]}"
        market_value = round(quantity * price, 4)
        position = PositionState(
            position_id=position_id,
            session_id=session.session_id,
            symbol=symbol,
            name=symbol,
            quantity=quantity,
            average_cost=price,
            current_price=price,
            market_value=market_value,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            weight=0.0,
            created_at=now,
            updated_at=now,
        )
        self.positions[position_id] = position
        session.current_capital = round(session.current_capital - market_value, 4)
        self._recalculate_session(session.session_id)
        return position

    def update_position(
        self,
        position_id: str,
        *,
        quantity: Optional[int] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> Optional[PositionState]:
        position = self.positions.get(position_id)
        if position is None:
            return None
        session = self.sessions.get(position.session_id)
        if session is None:
            return None

        old_market_value = position.market_value
        if quantity is not None:
            position.quantity = quantity
            position.market_value = round(position.quantity * position.current_price, 4)
            position.unrealized_pnl = round((position.current_price - position.average_cost) * position.quantity, 4)
            session.current_capital = round(session.current_capital + old_market_value - position.market_value, 4)
        if stop_loss is not None:
            position.stop_loss = stop_loss
        if take_profit is not None:
            position.take_profit = take_profit
        position.updated_at = datetime.now(timezone.utc)
        self._recalculate_session(session.session_id)
        return position

    def delete_position(self, position_id: str) -> bool:
        position = self.positions.pop(position_id, None)
        if position is None:
            return False
        session = self.sessions.get(position.session_id)
        if session:
            session.current_capital = round(session.current_capital + position.market_value, 4)
            session.total_pnl = round(session.total_pnl + position.realized_pnl + position.unrealized_pnl, 4)
            self._recalculate_session(session.session_id)
        return True

    def _recalculate_session(self, session_id: str) -> None:
        session = self.sessions[session_id]
        session_positions = [item for item in self.positions.values() if item.session_id == session_id]
        total_value = sum(item.market_value for item in session_positions)
        total_unrealized = sum(item.unrealized_pnl for item in session_positions)
        denominator = total_value if total_value > 0 else 1.0
        for item in session_positions:
            item.weight = round(item.market_value / denominator, 4)
        session.current_positions = len(session_positions)
        session.daily_pnl = round(total_unrealized, 4)
        session.updated_at = datetime.now(timezone.utc)


runtime_store = TradingRuntimeStore()
