"""
Order Management Application Service
订单管理应用服务
"""

import logging
import time
from typing import Any, Callable, Dict, Optional

from src.application.trading.broker_divergence import InMemoryTradingBrokerDivergenceStore
from src.application.trading.broker_lifecycle_event import (
    BrokerLifecycleEvent,
    InMemoryTradingBrokerLifecycleEventStore,
)
from src.application.trading.broker_order_correlation import (
    InMemoryTradingBrokerOrderCorrelationStore,
    LOCAL_ANCHOR_BROKER_CHANNEL,
)
from src.application.trading.miniqmt_lifecycle_ingestion import normalize_miniqmt_lifecycle_payload
from src.application.trading.tdx_manual_lifecycle_ingestion import normalize_tdx_manual_lifecycle_payload
from src.application.trading.broker_reconciliation import (
    AUTO_RESOLUTION_APPLIED,
    AWAITING_BROKER_ACKNOWLEDGEMENT,
    BROKER_ACKNOWLEDGED,
    build_broker_divergence_record,
    build_broker_lifecycle_payload,
    classify_broker_event_sequencing,
    evaluate_auto_resolution_policy,
    evaluate_replay_suppression_policy,
    find_duplicate_broker_lifecycle_event,
    REPLAY_SUPPRESSION_ELIGIBLE,
    resolve_broker_correlation_for_event,
)
from src.application.trading.cash_reservation import InMemoryPortfolioCashReservationStore
from src.application.trading.order_state_evidence import InMemoryTradingOrderStateStore
from src.application.trading.risk_gate import enforce_pre_submit_gate
from src.application.dto.trading_dto import CreateOrderRequest, OrderResponse
from src.domain.trading.model.order import Order
from src.domain.trading.repository import IOrderRepository
from src.domain.trading.value_objects import OrderId, OrderSide, OrderStatus, OrderType

logger = logging.getLogger(__name__)

LOCAL_ORDER_SUBMISSION_ADAPTER_PATH = "src.application.trading.order_mgmt_service.OrderManagementService.place_order"
AUTO_RESOLVED = "auto_resolved"
REPLAY_SUPPRESSION_SUPPRESSED_DUPLICATE = "suppressed_duplicate"


class OrderManagementService:
    def __init__(
        self,
        order_repo: IOrderRepository,
        event_bus: Optional[object] = None,
        decision_audit_sink: Optional[Callable[[Dict[str, Any]], None]] = None,
        pre_submit_gate: Optional[Callable[[CreateOrderRequest], Dict[str, Any]]] = None,
        cash_reservation_store: Optional[object] = None,
        broker_correlation_store: Optional[object] = None,
        broker_lifecycle_event_store: Optional[object] = None,
        broker_divergence_store: Optional[object] = None,
        order_state_store: Optional[object] = None,
        dedup_ttl_seconds: int = 300,
    ):
        self.order_repo = order_repo
        self.event_bus = event_bus
        self.decision_audit_sink = decision_audit_sink
        self.pre_submit_gate = pre_submit_gate
        self.cash_reservation_store = cash_reservation_store or InMemoryPortfolioCashReservationStore()
        self.broker_correlation_store = broker_correlation_store or InMemoryTradingBrokerOrderCorrelationStore()
        self.broker_lifecycle_event_store = broker_lifecycle_event_store or InMemoryTradingBrokerLifecycleEventStore()
        self.broker_divergence_store = broker_divergence_store or InMemoryTradingBrokerDivergenceStore()
        self.order_state_store = order_state_store or InMemoryTradingOrderStateStore()
        self.dedup_ttl_seconds = dedup_ttl_seconds
        self._idempotency_cache: Dict[str, tuple[float, OrderResponse]] = {}

    def place_order(self, request: CreateOrderRequest) -> OrderResponse:
        """
        用例：下单流程
        1. 验证业务规则
        2. 创建领域对象
        3. 持久化
        4. 触发后续动作 (如提交柜台)
        """
        self._prune_expired_idempotency_entries()

        cached_response = self._find_deduplicated_response(request)
        if cached_response is not None:
            self._emit_decision_audit(
                decision_outcome="deduplicated",
                request=request,
                order_id=cached_response.order_id,
                reason="matched_cached_idempotency_key",
            )
            return cached_response

        enforce_pre_submit_gate(
            request=request,
            pre_submit_gate=self.pre_submit_gate,
            emit_decision_audit=self._emit_decision_audit,
        )

        try:
            order = Order.create(
                symbol=request.symbol,
                quantity=request.quantity,
                side=OrderSide(request.side),
                order_type=OrderType(request.order_type),
                price=request.price,
            )

            order.submit()

            self.order_repo.save(order)
            self._remember_broker_order_correlation(order, request)
            self._remember_cash_reservation(order, request)
            self._remember_order_state_evidence(order, request)
            self._publish_events(order)

            response = self._map_to_response(order)
            self._remember_idempotent_response(request, response)
            self._emit_decision_audit(
                decision_outcome="submitted",
                request=request,
                order_id=order.id.value,
                reason="order_persisted",
            )

            logger.info("Order placed successfully: %s", order.id.value)

            return response

        except Exception as exc:
            self._emit_decision_audit(
                decision_outcome="rejected",
                request=request,
                reason=str(exc),
            )
            logger.error("Failed to place order: %s", exc)
            raise

    def handle_execution_report(self, order_id: str, filled_qty: int, price: float):
        """
        用例：处理成交回报
        """
        try:
            order = self._get_existing_order_or_raise(order_id)
        except ValueError as exc:
            reason_code, reason_detail = self._normalize_missing_order_reason(exc)
            self._emit_missing_order_audit(
                decision_outcome="execution_report_not_found",
                order_id=order_id,
                actor_id=None,
                source_id=None,
                reason=reason_code,
                extra_payload={
                    "decision_reason_detail": reason_detail,
                    "reported_filled_quantity": filled_qty,
                    "reported_fill_price": price,
                },
            )
            raise

        try:
            order.fill(filled_qty, price)
        except (RuntimeError, ValueError) as exc:
            reason_code, reason_detail = self._normalize_execution_report_denial_reason(exc)
            self._emit_existing_order_audit(
                decision_outcome="execution_report_denied",
                order=order,
                actor_id=None,
                source_id=None,
                reason=reason_code,
                extra_payload={
                    "current_order_status": order.status.value,
                    "decision_reason_detail": reason_detail,
                    "reported_filled_quantity": filled_qty,
                    "reported_fill_price": price,
                },
            )
            raise

        self.order_repo.save(order)
        self._reconcile_cash_reservation(order)
        self._remember_order_state_evidence(order)

        self._publish_events(order)

        return self._map_to_response(order)

    def cancel_order(
        self,
        order_id: str,
        *,
        reason: str,
        actor_id: str | None = None,
        source_id: str | None = None,
    ) -> OrderResponse:
        try:
            order = self._get_existing_order_or_raise(order_id)
        except ValueError as exc:
            reason_code, reason_detail = self._normalize_missing_order_reason(exc)
            self._emit_missing_order_audit(
                decision_outcome="cancel_not_found",
                order_id=order_id,
                actor_id=actor_id,
                source_id=source_id,
                reason=reason_code,
                extra_payload={
                    "requested_reason": reason,
                    "decision_reason_detail": reason_detail,
                },
            )
            raise

        try:
            order.cancel(reason)
        except RuntimeError as exc:
            reason_code, reason_detail = self._normalize_lifecycle_denial_reason(exc)
            self._emit_existing_order_audit(
                decision_outcome="cancel_denied",
                order=order,
                actor_id=actor_id,
                source_id=source_id,
                reason=reason_code,
                extra_payload={
                    "requested_reason": reason,
                    "current_order_status": order.status.value,
                    "decision_reason_detail": reason_detail,
                },
            )
            raise

        self.order_repo.save(order)
        self._reconcile_cash_reservation(order)
        self._remember_order_state_evidence(order)
        self._publish_events(order)
        self._emit_existing_order_audit(
            decision_outcome="cancelled",
            order=order,
            actor_id=actor_id,
            source_id=source_id,
            reason=reason,
        )

        return self._map_to_response(order)

    def reject_order(
        self,
        order_id: str,
        *,
        reason: str,
        actor_id: str | None = None,
        source_id: str | None = None,
    ) -> OrderResponse:
        try:
            order = self._get_existing_order_or_raise(order_id)
        except ValueError as exc:
            reason_code, reason_detail = self._normalize_missing_order_reason(exc)
            self._emit_missing_order_audit(
                decision_outcome="reject_not_found",
                order_id=order_id,
                actor_id=actor_id,
                source_id=source_id,
                reason=reason_code,
                extra_payload={
                    "requested_reason": reason,
                    "decision_reason_detail": reason_detail,
                },
            )
            raise

        try:
            order.reject(reason)
        except RuntimeError as exc:
            reason_code, reason_detail = self._normalize_lifecycle_denial_reason(exc)
            self._emit_existing_order_audit(
                decision_outcome="reject_denied",
                order=order,
                actor_id=actor_id,
                source_id=source_id,
                reason=reason_code,
                extra_payload={
                    "requested_reason": reason,
                    "current_order_status": order.status.value,
                    "decision_reason_detail": reason_detail,
                },
            )
            raise

        self.order_repo.save(order)
        self._reconcile_cash_reservation(order)
        self._remember_order_state_evidence(order)
        self._publish_events(order)
        self._emit_existing_order_audit(
            decision_outcome="rejected_after_submission",
            order=order,
            actor_id=actor_id,
            source_id=source_id,
            reason=reason,
        )

        return self._map_to_response(order)

    def record_broker_acknowledgement(self, order_id: str, *, external_order_id: str) -> None:
        self._get_existing_order_or_raise(order_id)
        self.broker_correlation_store.bind_external_order_id(
            order_id=order_id,
            external_order_id=external_order_id,
            acknowledgement_status=BROKER_ACKNOWLEDGED,
        )

    def record_broker_lifecycle_event(self, event: BrokerLifecycleEvent) -> Dict[str, Any]:
        correlation_record, identity_status = resolve_broker_correlation_for_event(event, self.broker_correlation_store)
        sequencing_status = classify_broker_event_sequencing(event)
        order_id = str(correlation_record["order_id"]) if correlation_record is not None else None
        replay_policy = evaluate_replay_suppression_policy(
            event=event,
            identity_status=identity_status,
            sequencing_status=sequencing_status,
        )

        if (
            event.event_type == "acknowledgement"
            and correlation_record is not None
            and event.external_order_id is not None
        ):
            self.broker_correlation_store.bind_external_order_id(
                order_id=order_id,
                external_order_id=event.external_order_id,
                acknowledgement_status=BROKER_ACKNOWLEDGED,
            )

        payload = build_broker_lifecycle_payload(
            event=event,
            order_id=order_id,
            correlation_record=correlation_record,
            identity_status=identity_status,
            sequencing_status=sequencing_status,
        )
        payload.update(
            {
                "replay_suppression_status": replay_policy["replay_suppression_status"],
                "replay_suppression_basis": replay_policy["replay_suppression_basis"],
                "replay_suppression_reason": replay_policy["replay_suppression_reason"],
            }
        )

        if replay_policy["replay_suppression_status"] == REPLAY_SUPPRESSION_ELIGIBLE:
            duplicate_record = find_duplicate_broker_lifecycle_event(
                broker_lifecycle_event_store=self.broker_lifecycle_event_store,
                event=event,
                order_id=order_id,
                external_order_id=event.external_order_id,
            )
            if duplicate_record is not None:
                payload["replay_suppression_status"] = REPLAY_SUPPRESSION_SUPPRESSED_DUPLICATE
                payload["replay_suppression_reference_persisted_at"] = duplicate_record.get("persisted_at")
                return payload

        self.broker_lifecycle_event_store.append(payload)
        local_order, local_order_status = self._resolve_local_order_and_status(order_id)
        divergence_record = build_broker_divergence_record(
            event=event,
            correlation_record=correlation_record,
            identity_status=identity_status,
            sequencing_status=sequencing_status,
            order_id=order_id,
            local_order=local_order,
            local_order_status=local_order_status,
        )
        if divergence_record is not None:
            auto_resolution_policy = evaluate_auto_resolution_policy(
                event=event,
                local_order=local_order,
                divergence_record=divergence_record,
                identity_status=identity_status,
                sequencing_status=sequencing_status,
            )
            divergence_record.update(auto_resolution_policy)
            if auto_resolution_policy["auto_resolution_status"] == AUTO_RESOLUTION_APPLIED and local_order is not None:
                self._apply_broker_auto_resolution(
                    event=event,
                    order=local_order,
                    auto_resolution_basis=str(auto_resolution_policy["auto_resolution_basis"]),
                    divergence_record=divergence_record,
                )
            self.broker_divergence_store.append(divergence_record)
        return payload

    def ingest_miniqmt_lifecycle_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.record_broker_lifecycle_event(normalize_miniqmt_lifecycle_payload(payload))

    def ingest_tdx_manual_lifecycle_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.record_broker_lifecycle_event(normalize_tdx_manual_lifecycle_payload(payload))

    def get_pending_buy_notional_for_portfolio(self, portfolio_id: str) -> float:
        return float(self.cash_reservation_store.get_portfolio_reserved_notional(portfolio_id))

    def has_stale_cash_reservations_for_portfolio(self, portfolio_id: str, max_age_seconds: int) -> bool:
        stale_reservations = self.cash_reservation_store.fetch_stale(max_age_seconds)
        return any(record["portfolio_id"] == portfolio_id for record in stale_reservations)

    def _publish_events(self, order: Order) -> None:
        """发布订单的领域事件"""
        if not self.event_bus:
            return
        if not hasattr(order, "_domain_events"):
            return

        events = list(order._domain_events)
        order._domain_events.clear()

        for event in events:
            try:
                self.event_bus.publish(event)
            except Exception:
                logger.error("Failed to publish event: %(e)s")

    def _map_to_response(self, order: Order) -> OrderResponse:
        return OrderResponse(
            order_id=order.id.value,
            symbol=order.symbol,
            quantity=order.quantity,
            filled_quantity=order.filled_quantity,
            status=order.status.value,
            side=order.side.value,
            price=order.price,
            average_fill_price=order.average_fill_price,
            created_at=order.created_at,
        )

    def _prune_expired_idempotency_entries(self) -> None:
        if not self._idempotency_cache:
            return

        now = time.time()
        expired_keys = [
            key for key, (created_at, _) in self._idempotency_cache.items() if now - created_at > self.dedup_ttl_seconds
        ]
        for key in expired_keys:
            self._idempotency_cache.pop(key, None)

    def _find_deduplicated_response(self, request: CreateOrderRequest) -> Optional[OrderResponse]:
        if not request.idempotency_key:
            return None

        cached = self._idempotency_cache.get(request.idempotency_key)
        if cached is None:
            return None

        _, response = cached
        return response

    def _remember_idempotent_response(self, request: CreateOrderRequest, response: OrderResponse) -> None:
        if not request.idempotency_key:
            return

        self._idempotency_cache[request.idempotency_key] = (time.time(), response)

    def _remember_cash_reservation(self, order: Order, request: CreateOrderRequest) -> None:
        if request.portfolio_id is None:
            return

        if order.side != OrderSide.BUY or order.price is None:
            return

        self.cash_reservation_store.upsert(
            request.portfolio_id,
            order.id.value,
            float(order.quantity) * float(order.price),
        )

    def _remember_broker_order_correlation(self, order: Order, request: CreateOrderRequest) -> None:
        self.broker_correlation_store.upsert_submission(
            order_id=order.id.value,
            local_submission_id=request.idempotency_key or request.request_id or order.id.value,
            broker_channel=LOCAL_ANCHOR_BROKER_CHANNEL,
            adapter_path=LOCAL_ORDER_SUBMISSION_ADAPTER_PATH,
            account_scope="unscoped",
            session_scope=request.request_id,
            acknowledgement_status=AWAITING_BROKER_ACKNOWLEDGEMENT,
        )

    def _apply_broker_auto_resolution(
        self,
        *,
        event: BrokerLifecycleEvent,
        order: Order,
        auto_resolution_basis: str,
        divergence_record: Dict[str, Any],
    ) -> None:
        if event.event_type == "cancel":
            order.cancel(event.reason_detail or event.reason_code or "broker_cancelled")
            decision_outcome = "broker_auto_resolved_cancel"
        elif event.event_type == "reject":
            order.reject(event.reason_detail or event.reason_code or "broker_rejected")
            decision_outcome = "broker_auto_resolved_reject"
        else:
            raise ValueError(f"Unsupported broker auto-resolution event type: {event.event_type}")

        self.order_repo.save(order)
        self._reconcile_cash_reservation(order)
        self._remember_order_state_evidence(order)
        self._publish_events(order)
        self._emit_existing_order_audit(
            decision_outcome=decision_outcome,
            order=order,
            actor_id=None,
            source_id=event.source_name,
            reason=auto_resolution_basis,
            extra_payload={
                "broker_event_type": event.event_type,
                "broker_event_id": event.event_id,
                "broker_sequence_id": event.sequence_id,
                "broker_external_order_id": event.external_order_id,
                "auto_resolution_basis": auto_resolution_basis,
            },
        )
        divergence_record["review_status"] = AUTO_RESOLVED
        divergence_record["next_action"] = "auto_resolution_audit_complete"
        divergence_record["resolved_local_status"] = order.status.value

    def _resolve_local_order_and_status(self, order_id: str | None) -> tuple[Optional[Order], Optional[str]]:
        if order_id is None:
            return None, None

        order = self.order_repo.get_by_id(OrderId(order_id))
        if order is not None:
            return order, order.status.value

        if hasattr(self.order_state_store, "get_order_state"):
            order_state_record = self.order_state_store.get_order_state(order_id)
            if order_state_record is not None:
                return None, str(order_state_record["status"])

        return None, None

    def _remember_order_state_evidence(self, order: Order, request: Optional[CreateOrderRequest] = None) -> None:
        portfolio_id = request.portfolio_id if request is not None else None
        self.order_state_store.upsert(
            portfolio_id,
            order.id.value,
            order.symbol,
            order.status.value,
        )

    def _reconcile_cash_reservation(self, order: Order) -> None:
        existing_reservation = self.cash_reservation_store.get_order_reservation(order.id.value)
        if existing_reservation is None:
            return

        if order.status in {
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED,
            OrderStatus.FILLED,
        }:
            self.cash_reservation_store.release(order.id.value)
            return

        if order.side != OrderSide.BUY or order.price is None:
            self.cash_reservation_store.release(order.id.value)
            return

        remaining_quantity = max(order.quantity - order.filled_quantity, 0)
        remaining_notional = float(remaining_quantity) * float(order.price)
        if remaining_notional > 0:
            self.cash_reservation_store.upsert(
                str(existing_reservation["portfolio_id"]),
                order.id.value,
                remaining_notional,
            )
        else:
            self.cash_reservation_store.release(order.id.value)

    def _get_existing_order_or_raise(self, order_id: str) -> Order:
        order = self.order_repo.get_by_id(OrderId(order_id))
        if not order:
            raise ValueError(f"Order not found: {order_id}")
        return order

    @staticmethod
    def _normalize_missing_order_reason(exc: ValueError) -> tuple[str, str]:
        return "order_not_found", str(exc)

    @staticmethod
    def _normalize_lifecycle_denial_reason(exc: RuntimeError) -> tuple[str, str]:
        return "invalid_order_status_transition", str(exc)

    @staticmethod
    def _normalize_execution_report_denial_reason(exc: RuntimeError | ValueError) -> tuple[str, str]:
        reason_detail = str(exc)

        if reason_detail.startswith("Cannot fill order in status "):
            return "invalid_order_status_transition", reason_detail

        if reason_detail == "Fill quantity exceeds remaining quantity":
            return "fill_quantity_exceeds_remaining_quantity", reason_detail

        if reason_detail == "Fill quantity must be positive":
            return "invalid_fill_quantity", reason_detail

        return "execution_report_denied", reason_detail

    def _emit_decision_audit(
        self,
        *,
        decision_outcome: str,
        request: CreateOrderRequest,
        order_id: Optional[str] = None,
        reason: str = "",
    ) -> None:
        payload = {
            "request_identity": request.idempotency_key or request.request_id,
            "request_id": request.request_id,
            "actor_id": request.actor_id,
            "strategy_id": request.strategy_id,
            "source_id": request.source_id,
            "execution_path_classification": "experimental",
            "symbol": request.symbol,
            "side": request.side,
            "quantity": request.quantity,
            "price": request.price,
            "order_type": request.order_type,
            "decision_outcome": decision_outcome,
            "decision_reason": reason,
            "order_id": order_id,
        }

        if self.decision_audit_sink is not None:
            self.decision_audit_sink(payload)

        logger.info("Trading decision audit: %s", payload)

    def _emit_existing_order_audit(
        self,
        *,
        decision_outcome: str,
        order: Order,
        actor_id: str | None,
        source_id: str | None,
        reason: str,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        payload = {
            "request_identity": order.id.value,
            "request_id": None,
            "actor_id": actor_id,
            "strategy_id": None,
            "source_id": source_id,
            "execution_path_classification": "experimental",
            "symbol": order.symbol,
            "side": order.side.value,
            "quantity": order.quantity,
            "price": order.price,
            "order_type": order.order_type.value,
            "decision_outcome": decision_outcome,
            "decision_reason": reason,
            "order_id": order.id.value,
        }
        if extra_payload:
            payload.update(extra_payload)

        if self.decision_audit_sink is not None:
            self.decision_audit_sink(payload)

        logger.info("Trading decision audit: %s", payload)

    def _emit_missing_order_audit(
        self,
        *,
        decision_outcome: str,
        order_id: str,
        actor_id: str | None,
        source_id: str | None,
        reason: str,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        payload = {
            "request_identity": order_id,
            "request_id": None,
            "actor_id": actor_id,
            "strategy_id": None,
            "source_id": source_id,
            "execution_path_classification": "experimental",
            "symbol": None,
            "side": None,
            "quantity": None,
            "price": None,
            "order_type": None,
            "decision_outcome": decision_outcome,
            "decision_reason": reason,
            "order_id": order_id,
        }
        if extra_payload:
            payload.update(extra_payload)

        if self.decision_audit_sink is not None:
            self.decision_audit_sink(payload)

        logger.info("Trading decision audit: %s", payload)
