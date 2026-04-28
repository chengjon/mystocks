"""
Trading pre-submit risk gates.
"""

from __future__ import annotations

from typing import Any, Callable, Dict

from src.application.dto.trading_dto import CreateOrderRequest
from src.domain.portfolio.repository import IPortfolioRepository


def build_portfolio_pre_submit_gate(
    portfolio_repo: IPortfolioRepository,
    *,
    max_single_symbol_weight: float = 0.20,
    pending_buy_notional_getter: Callable[[str], float] | None = None,
    stale_buy_reservation_checker: Callable[[str], bool] | None = None,
) -> Callable[[CreateOrderRequest], Dict[str, Any]]:
    """
    Build a conservative portfolio-aware pre-submit gate.

    This gate intentionally enforces only hard blocking rules that can be
    evaluated synchronously from the current portfolio snapshot:
    - portfolio context must be present
    - BUY orders require an evaluable notional price
    - BUY orders must fit available cash
    - BUY orders must not exceed the configured per-symbol weight cap
    - SELL orders must not exceed currently held quantity
    """

    def evaluate(request: CreateOrderRequest) -> Dict[str, Any]:
        if not request.portfolio_id:
            return {"decision": "blocked", "reason": "portfolio_context_required"}

        portfolio = portfolio_repo.get_by_id(request.portfolio_id)
        if portfolio is None:
            return {"decision": "blocked", "reason": "portfolio_not_found"}

        if request.side == "BUY":
            if request.price is None:
                return {"decision": "blocked", "reason": "price_required_for_risk_evaluation"}

            if stale_buy_reservation_checker is not None and stale_buy_reservation_checker(request.portfolio_id):
                return {"decision": "blocked", "reason": "stale_pending_buy_reservations_require_review"}

            requested_notional = request.quantity * request.price
            if portfolio.cash < requested_notional:
                return {"decision": "blocked", "reason": "insufficient_cash"}

            pending_reserved_notional = (
                pending_buy_notional_getter(request.portfolio_id) if pending_buy_notional_getter is not None else 0.0
            )
            available_cash_after_reservations = float(portfolio.cash) - float(pending_reserved_notional)
            if pending_reserved_notional > 0 and available_cash_after_reservations < requested_notional:
                return {"decision": "blocked", "reason": "insufficient_available_cash_after_reservations"}

            current_symbol_value = _estimate_symbol_value(portfolio.positions.get(request.symbol))
            projected_symbol_value = current_symbol_value + requested_notional
            portfolio_total_value = _estimate_portfolio_total_value(portfolio)
            projected_weight = projected_symbol_value / portfolio_total_value if portfolio_total_value > 0 else 1.0
            if projected_weight > max_single_symbol_weight:
                return {"decision": "blocked", "reason": "max_symbol_weight_exceeded"}

            return {"decision": "allowed"}

        if request.side == "SELL":
            current_position = portfolio.positions.get(request.symbol)
            current_quantity = current_position.quantity if current_position is not None else 0
            if current_quantity < request.quantity:
                return {"decision": "blocked", "reason": "insufficient_position_quantity"}

            return {"decision": "allowed"}

        return {"decision": "allowed"}

    return evaluate


def _estimate_symbol_value(position: Any) -> float:
    if position is None:
        return 0.0

    if getattr(position, "current_price", 0.0):
        return float(position.quantity) * float(position.current_price)

    return float(position.quantity) * float(position.average_cost)


def _estimate_portfolio_total_value(portfolio: Any) -> float:
    holdings_value = sum(_estimate_symbol_value(position) for position in portfolio.positions.values())
    return float(portfolio.cash) + holdings_value


def enforce_pre_submit_gate(
    *,
    request: CreateOrderRequest,
    pre_submit_gate: Callable[[CreateOrderRequest], Dict[str, Any]] | None,
    emit_decision_audit: Callable[..., None],
) -> None:
    if pre_submit_gate is None:
        return

    gate_result = pre_submit_gate(request) or {}
    decision = gate_result.get("decision", "allowed")
    reason = gate_result.get("reason", "")

    if decision == "allowed":
        return

    if decision == "blocked":
        emit_decision_audit(
            decision_outcome="blocked_by_risk_gate",
            request=request,
            reason=reason or "pre_submit_gate_blocked_request",
        )
        raise PermissionError(reason or "Order blocked by pre-submit risk gate")

    if decision == "confirmation_required":
        if request.confirmation_token:
            return

        if request.bypass_reason and request.actor_id:
            emit_decision_audit(
                decision_outcome="approved_bypass",
                request=request,
                reason=request.bypass_reason,
            )
            return

        emit_decision_audit(
            decision_outcome="awaiting_confirmation",
            request=request,
            reason=reason or "confirmation_required",
        )
        raise PermissionError(reason or "Order requires confirmation before submission")

    raise ValueError(f"Unsupported pre-submit gate decision: {decision}")
