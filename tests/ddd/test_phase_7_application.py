"""
Phase 7: Application Layer 验证测试
"""

import importlib
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from src.application.dto.trading_dto import CreateOrderRequest
from src.application.trading.cash_reservation import (
    SqlitePortfolioCashReservationStore,
    build_default_portfolio_cash_reservation_store,
)
from src.application.trading.decision_audit import (
    JsonlTradingDecisionAuditSink,
    SqliteTradingDecisionAuditSink,
    build_default_trading_decision_audit_sink,
)
from src.application.trading.order_mgmt_service import OrderManagementService
from src.application.trading.order_state_evidence import (
    SqliteTradingOrderStateStore,
    build_default_trading_order_state_store,
)
from src.application.trading.risk_gate import build_portfolio_pre_submit_gate
from src.domain.portfolio.model.portfolio import Portfolio
from src.domain.portfolio.value_objects import PositionInfo
from src.domain.trading.value_objects import OrderId, OrderSide, OrderStatus
from src.governance.risk_management.services.stop_loss_execution_service import StopLossExecutionService, StopLossPosition


class TestOrderManagementService:
    class InMemoryOrderRepository:
        def __init__(self):
            self._orders = {}

        def save(self, order):
            self._orders[order.id.value] = order

        def get_by_id(self, order_id):
            return self._orders.get(order_id.value)

        def get_by_symbol(self, symbol):
            return [order for order in self._orders.values() if order.symbol == symbol]

        def get_active_orders(self):
            return [order for order in self._orders.values() if order.status in {OrderStatus.SUBMITTED, OrderStatus.PARTIALLY_FILLED}]

    def test_place_order_flow(self):
        # Setup mocks
        mock_repo = MagicMock()
        audit_sink = MagicMock()
        service = OrderManagementService(order_repo=mock_repo, decision_audit_sink=audit_sink)

        request = CreateOrderRequest(symbol="000001", quantity=100, side="BUY", order_type="LIMIT", price=10.5)

        # Execute
        response = service.place_order(request)

        # Verify
        assert response.symbol == "000001"
        assert response.status == OrderStatus.SUBMITTED.value
        assert mock_repo.save.called
        audit_sink.assert_called_once()
        assert audit_sink.call_args.kwargs == {}
        assert audit_sink.call_args.args[0]["decision_outcome"] == "submitted"

    def test_place_order_deduplicates_by_idempotency_key(self):
        mock_repo = MagicMock()
        audit_sink = MagicMock()
        service = OrderManagementService(order_repo=mock_repo, decision_audit_sink=audit_sink)

        request = CreateOrderRequest(
            symbol="000001",
            quantity=100,
            side="BUY",
            order_type="LIMIT",
            price=10.5,
            idempotency_key="dedup-key-0001",
            request_id="request-0001",
            actor_id="tester",
            source_id="unit-test",
        )

        first_response = service.place_order(request)
        second_response = service.place_order(request)

        assert first_response.order_id == second_response.order_id
        assert mock_repo.save.call_count == 1
        assert audit_sink.call_count == 2
        assert audit_sink.call_args_list[0].args[0]["decision_outcome"] == "submitted"
        assert audit_sink.call_args_list[1].args[0]["decision_outcome"] == "deduplicated"

    def test_place_order_audits_rejected_decision(self):
        mock_repo = MagicMock()
        mock_repo.save.side_effect = RuntimeError("db unavailable")
        audit_sink = MagicMock()
        service = OrderManagementService(order_repo=mock_repo, decision_audit_sink=audit_sink)

        request = CreateOrderRequest(
            symbol="000001",
            quantity=100,
            side="BUY",
            order_type="LIMIT",
            price=10.5,
            idempotency_key="reject-key-0001",
        )

        with pytest.raises(RuntimeError, match="db unavailable"):
            service.place_order(request)

        assert audit_sink.call_count == 1
        assert audit_sink.call_args.args[0]["decision_outcome"] == "rejected"

    def test_place_order_blocks_when_pre_submit_gate_rejects(self):
        mock_repo = MagicMock()
        audit_sink = MagicMock()
        pre_submit_gate = MagicMock(return_value={"decision": "blocked", "reason": "max_position_size_exceeded"})
        service = OrderManagementService(
            order_repo=mock_repo,
            decision_audit_sink=audit_sink,
            pre_submit_gate=pre_submit_gate,
        )

        request = CreateOrderRequest(
            symbol="000001",
            quantity=100,
            side="BUY",
            order_type="LIMIT",
            price=10.5,
            idempotency_key="gate-block-0001",
        )

        with pytest.raises(PermissionError, match="max_position_size_exceeded"):
            service.place_order(request)

        assert mock_repo.save.call_count == 0
        assert audit_sink.call_args.args[0]["decision_outcome"] == "blocked_by_risk_gate"

    def test_place_order_requires_confirmation_before_submission(self):
        mock_repo = MagicMock()
        audit_sink = MagicMock()
        pre_submit_gate = MagicMock(return_value={"decision": "confirmation_required", "reason": "manual_approval_needed"})
        service = OrderManagementService(
            order_repo=mock_repo,
            decision_audit_sink=audit_sink,
            pre_submit_gate=pre_submit_gate,
        )

        request = CreateOrderRequest(
            symbol="000001",
            quantity=100,
            side="BUY",
            order_type="LIMIT",
            price=10.5,
            idempotency_key="confirm-wait-0001",
        )

        with pytest.raises(PermissionError, match="manual_approval_needed"):
            service.place_order(request)

        assert mock_repo.save.call_count == 0
        assert audit_sink.call_args.args[0]["decision_outcome"] == "awaiting_confirmation"

    def test_place_order_allows_approved_bypass(self):
        mock_repo = MagicMock()
        audit_sink = MagicMock()
        pre_submit_gate = MagicMock(return_value={"decision": "confirmation_required", "reason": "manual_approval_needed"})
        service = OrderManagementService(
            order_repo=mock_repo,
            decision_audit_sink=audit_sink,
            pre_submit_gate=pre_submit_gate,
        )

        request = CreateOrderRequest(
            symbol="000001",
            quantity=100,
            side="BUY",
            order_type="LIMIT",
            price=10.5,
            idempotency_key="confirm-bypass-0001",
            actor_id="ops-user",
            bypass_reason="approved_emergency_bypass",
        )

        response = service.place_order(request)

        assert response.status == OrderStatus.SUBMITTED.value
        assert mock_repo.save.call_count == 1
        assert audit_sink.call_args_list[0].args[0]["decision_outcome"] == "approved_bypass"
        assert audit_sink.call_args_list[1].args[0]["decision_outcome"] == "submitted"

    def test_jsonl_trading_decision_audit_sink_persists_records(self, tmp_path):
        audit_file = tmp_path / "trading-audit.jsonl"
        sink = JsonlTradingDecisionAuditSink(audit_file)
        mock_repo = MagicMock()
        service = OrderManagementService(order_repo=mock_repo, decision_audit_sink=sink)

        request = CreateOrderRequest(
            symbol="000001",
            quantity=100,
            side="BUY",
            order_type="LIMIT",
            price=10.5,
            idempotency_key="durable-audit-0001",
            actor_id="ops-user",
        )

        response = service.place_order(request)

        assert response.status == OrderStatus.SUBMITTED.value
        lines = audit_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        assert '"decision_outcome": "submitted"' in lines[0]
        assert '"request_identity": "durable-audit-0001"' in lines[0]

    def test_sqlite_trading_decision_audit_sink_persists_and_queries_records(self, tmp_path):
        audit_db = tmp_path / "trading-audit.sqlite3"
        sink = SqliteTradingDecisionAuditSink(audit_db)

        sink(
            {
                "request_identity": "sqlite-audit-0001",
                "request_id": "req-0001",
                "actor_id": "ops-user",
                "strategy_id": None,
                "source_id": "unit-test",
                "execution_path_classification": "experimental",
                "symbol": "000001",
                "side": "BUY",
                "quantity": 100,
                "price": 10.5,
                "order_type": "LIMIT",
                "decision_outcome": "submitted",
                "decision_reason": "order_persisted",
                "order_id": "order-0001",
            }
        )

        records = sink.fetch_recent(limit=10)

        assert len(records) == 1
        assert records[0]["request_identity"] == "sqlite-audit-0001"
        assert records[0]["decision_outcome"] == "submitted"
        assert records[0]["actor_id"] == "ops-user"

    def test_default_trading_decision_audit_sink_writes_jsonl_and_sqlite(self, tmp_path):
        audit_file = tmp_path / "trading-audit.jsonl"
        audit_db = tmp_path / "trading-audit.sqlite3"
        sink = build_default_trading_decision_audit_sink(path=audit_file, sqlite_path=audit_db)
        mock_repo = MagicMock()
        service = OrderManagementService(order_repo=mock_repo, decision_audit_sink=sink)

        request = CreateOrderRequest(
            symbol="000001",
            quantity=100,
            side="BUY",
            order_type="LIMIT",
            price=10.5,
            idempotency_key="default-dual-sink-0001",
            actor_id="ops-user",
        )

        response = service.place_order(request)

        assert response.status == OrderStatus.SUBMITTED.value
        assert audit_file.exists()
        assert audit_db.exists()

        lines = audit_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1

        sqlite_records = sink.fetch_recent(limit=10)
        assert len(sqlite_records) == 1
        assert sqlite_records[0]["request_identity"] == "default-dual-sink-0001"

    def test_place_order_blocks_when_portfolio_context_is_missing(self):
        mock_repo = MagicMock()
        audit_sink = MagicMock()
        service = OrderManagementService(
            order_repo=mock_repo,
            decision_audit_sink=audit_sink,
            pre_submit_gate=build_portfolio_pre_submit_gate(MagicMock()),
        )

        request = CreateOrderRequest(
            symbol="000001",
            quantity=100,
            side="BUY",
            order_type="LIMIT",
            price=10.5,
        )

        with pytest.raises(PermissionError, match="portfolio_context_required"):
            service.place_order(request)

        assert mock_repo.save.call_count == 0
        assert audit_sink.call_args.args[0]["decision_outcome"] == "blocked_by_risk_gate"

    def test_place_order_blocks_when_cash_is_insufficient_for_buy(self):
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=500.0)
        portfolio_repo = MagicMock()
        portfolio_repo.get_by_id.return_value = portfolio
        mock_repo = MagicMock()
        audit_sink = MagicMock()
        service = OrderManagementService(
            order_repo=mock_repo,
            decision_audit_sink=audit_sink,
            pre_submit_gate=build_portfolio_pre_submit_gate(portfolio_repo),
        )

        request = CreateOrderRequest(
            symbol="000001",
            quantity=100,
            side="BUY",
            order_type="LIMIT",
            price=10.5,
            portfolio_id=portfolio.id,
        )

        with pytest.raises(PermissionError, match="insufficient_cash"):
            service.place_order(request)

        assert mock_repo.save.call_count == 0
        assert audit_sink.call_args.args[0]["decision_reason"] == "insufficient_cash"

    def test_place_order_blocks_when_projected_symbol_weight_exceeds_limit(self):
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=100000.0)
        portfolio.cash = 50000.0
        portfolio.positions["600000"] = PositionInfo(
            symbol="600000",
            quantity=1000,
            average_cost=20.0,
            current_price=20.0,
        )
        portfolio_repo = MagicMock()
        portfolio_repo.get_by_id.return_value = portfolio
        mock_repo = MagicMock()
        audit_sink = MagicMock()
        service = OrderManagementService(
            order_repo=mock_repo,
            decision_audit_sink=audit_sink,
            pre_submit_gate=build_portfolio_pre_submit_gate(portfolio_repo, max_single_symbol_weight=0.20),
        )

        request = CreateOrderRequest(
            symbol="600000",
            quantity=2000,
            side="BUY",
            order_type="LIMIT",
            price=20.0,
            portfolio_id=portfolio.id,
        )

        with pytest.raises(PermissionError, match="max_symbol_weight_exceeded"):
            service.place_order(request)

        assert mock_repo.save.call_count == 0
        assert audit_sink.call_args.args[0]["decision_reason"] == "max_symbol_weight_exceeded"

    def test_place_order_blocks_when_sell_quantity_exceeds_portfolio_position(self):
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=100000.0)
        portfolio.positions["000001"] = PositionInfo(
            symbol="000001",
            quantity=100,
            average_cost=10.0,
            current_price=10.5,
        )
        portfolio_repo = MagicMock()
        portfolio_repo.get_by_id.return_value = portfolio
        mock_repo = MagicMock()
        audit_sink = MagicMock()
        service = OrderManagementService(
            order_repo=mock_repo,
            decision_audit_sink=audit_sink,
            pre_submit_gate=build_portfolio_pre_submit_gate(portfolio_repo),
        )

        request = CreateOrderRequest(
            symbol="000001",
            quantity=200,
            side="SELL",
            order_type="MARKET",
            price=None,
            portfolio_id=portfolio.id,
        )

        with pytest.raises(PermissionError, match="insufficient_position_quantity"):
            service.place_order(request)

        assert mock_repo.save.call_count == 0
        assert audit_sink.call_args.args[0]["decision_reason"] == "insufficient_position_quantity"

    def test_place_order_blocks_when_pending_buy_reservations_exhaust_available_cash(self):
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=5000.0)
        portfolio_repo = MagicMock()
        portfolio_repo.get_by_id.return_value = portfolio
        order_repo = self.InMemoryOrderRepository()
        audit_sink = MagicMock()
        service = OrderManagementService(order_repo=order_repo, decision_audit_sink=audit_sink)
        service.pre_submit_gate = build_portfolio_pre_submit_gate(
            portfolio_repo,
            max_single_symbol_weight=1.0,
            pending_buy_notional_getter=service.get_pending_buy_notional_for_portfolio,
        )

        first_request = CreateOrderRequest(
            symbol="000001",
            quantity=200,
            side="BUY",
            order_type="LIMIT",
            price=10.0,
            portfolio_id=portfolio.id,
            idempotency_key="reserved-cash-0001",
        )
        second_request = CreateOrderRequest(
            symbol="000002",
            quantity=350,
            side="BUY",
            order_type="LIMIT",
            price=10.0,
            portfolio_id=portfolio.id,
            idempotency_key="reserved-cash-0002",
        )

        first_response = service.place_order(first_request)

        assert first_response.status == OrderStatus.SUBMITTED.value
        assert service.get_pending_buy_notional_for_portfolio(portfolio.id) == 2000.0

        with pytest.raises(PermissionError, match="insufficient_available_cash_after_reservations"):
            service.place_order(second_request)

        assert audit_sink.call_args.args[0]["decision_reason"] == "insufficient_available_cash_after_reservations"

    def test_handle_execution_report_reconciles_pending_buy_reservations(self):
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=5000.0)
        portfolio_repo = MagicMock()
        portfolio_repo.get_by_id.return_value = portfolio
        order_repo = self.InMemoryOrderRepository()
        service = OrderManagementService(order_repo=order_repo)
        service.pre_submit_gate = build_portfolio_pre_submit_gate(
            portfolio_repo,
            max_single_symbol_weight=1.0,
            pending_buy_notional_getter=service.get_pending_buy_notional_for_portfolio,
        )

        request = CreateOrderRequest(
            symbol="000001",
            quantity=200,
            side="BUY",
            order_type="LIMIT",
            price=10.0,
            portfolio_id=portfolio.id,
            idempotency_key="reservation-release-0001",
        )

        response = service.place_order(request)
        assert service.get_pending_buy_notional_for_portfolio(portfolio.id) == 2000.0

        service.handle_execution_report(response.order_id, filled_qty=200, price=10.0)

        assert service.get_pending_buy_notional_for_portfolio(portfolio.id) == 0.0

    def test_sqlite_cash_reservation_store_recovers_pending_buy_reservations_across_service_restart(self, tmp_path):
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=5000.0)
        portfolio_repo = MagicMock()
        portfolio_repo.get_by_id.return_value = portfolio
        order_repo = self.InMemoryOrderRepository()
        reservation_db = tmp_path / "trading-cash-reservations.sqlite3"

        first_service = OrderManagementService(
            order_repo=order_repo,
            cash_reservation_store=SqlitePortfolioCashReservationStore(reservation_db),
        )
        first_service.pre_submit_gate = build_portfolio_pre_submit_gate(
            portfolio_repo,
            max_single_symbol_weight=1.0,
            pending_buy_notional_getter=first_service.get_pending_buy_notional_for_portfolio,
        )

        first_response = first_service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=200,
                side="BUY",
                order_type="LIMIT",
                price=10.0,
                portfolio_id=portfolio.id,
                idempotency_key="sqlite-reserved-cash-0001",
            )
        )

        restarted_service = OrderManagementService(
            order_repo=order_repo,
            cash_reservation_store=SqlitePortfolioCashReservationStore(reservation_db),
        )
        restarted_service.pre_submit_gate = build_portfolio_pre_submit_gate(
            portfolio_repo,
            max_single_symbol_weight=1.0,
            pending_buy_notional_getter=restarted_service.get_pending_buy_notional_for_portfolio,
        )

        assert restarted_service.get_pending_buy_notional_for_portfolio(portfolio.id) == 2000.0

        with pytest.raises(PermissionError, match="insufficient_available_cash_after_reservations"):
            restarted_service.place_order(
                CreateOrderRequest(
                    symbol="000002",
                    quantity=350,
                    side="BUY",
                    order_type="LIMIT",
                    price=10.0,
                    portfolio_id=portfolio.id,
                    idempotency_key="sqlite-reserved-cash-0002",
                )
            )

        restarted_service.handle_execution_report(first_response.order_id, filled_qty=200, price=10.0)
        assert restarted_service.get_pending_buy_notional_for_portfolio(portfolio.id) == 0.0

    def test_default_cash_reservation_store_uses_local_sqlite_ledger(self, tmp_path):
        reservation_db = tmp_path / "default-trading-cash-reservations.sqlite3"
        store = build_default_portfolio_cash_reservation_store(path=reservation_db)

        store.upsert("portfolio-0001", "order-0001", 1500.0)

        assert store.get_portfolio_reserved_notional("portfolio-0001") == 1500.0
        assert store.fetch_all()[0]["order_id"] == "order-0001"

    def test_default_order_state_store_uses_local_sqlite_ledger(self, tmp_path):
        order_state_db = tmp_path / "default-trading-order-state.sqlite3"
        store = build_default_trading_order_state_store(path=order_state_db)

        store.upsert("portfolio-0001", "order-0001", "000001", "SUBMITTED")

        record = store.get_order_state("order-0001")
        assert record is not None
        assert record["portfolio_id"] == "portfolio-0001"
        assert record["symbol"] == "000001"
        assert record["status"] == "SUBMITTED"

    def test_sqlite_broker_order_correlation_store_persists_submission_and_external_identity_binding(self, tmp_path):
        try:
            module = importlib.import_module("src.application.trading.broker_order_correlation")
        except ModuleNotFoundError as exc:
            pytest.fail(f"broker order correlation module missing: {exc}")

        correlation_db = tmp_path / "trading-broker-order-correlation.sqlite3"
        store = module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)

        store.upsert_submission(
            order_id="order-0001",
            local_submission_id="submission-0001",
            broker_channel=module.LOCAL_ANCHOR_BROKER_CHANNEL,
            adapter_path="src.application.trading.order_mgmt_service.OrderManagementService.place_order",
            account_scope="unscoped",
            session_scope="unit-session-0001",
            acknowledgement_status="awaiting_broker_acknowledgement",
        )

        pending_record = store.get_order_correlation("order-0001")
        assert pending_record is not None
        assert pending_record["order_id"] == "order-0001"
        assert pending_record["local_submission_id"] == "submission-0001"
        assert pending_record["broker_channel"] == module.LOCAL_ANCHOR_BROKER_CHANNEL
        assert pending_record["adapter_path"] == "src.application.trading.order_mgmt_service.OrderManagementService.place_order"
        assert pending_record["account_scope"] == "unscoped"
        assert pending_record["session_scope"] == "unit-session-0001"
        assert pending_record["acknowledgement_status"] == "awaiting_broker_acknowledgement"
        assert pending_record["external_order_id"] is None

        store.bind_external_order_id(
            order_id="order-0001",
            external_order_id="broker-order-0001",
            acknowledgement_status="acknowledged",
        )

        acknowledged_record = store.get_order_correlation("order-0001")
        assert acknowledged_record is not None
        assert acknowledged_record["external_order_id"] == "broker-order-0001"
        assert acknowledged_record["acknowledgement_status"] == "acknowledged"

        reverse_lookup_record = store.get_by_external_order_id("broker-order-0001")
        assert reverse_lookup_record is not None
        assert reverse_lookup_record["order_id"] == "order-0001"
        assert reverse_lookup_record["local_submission_id"] == "submission-0001"
        assert reverse_lookup_record["broker_channel"] == module.LOCAL_ANCHOR_BROKER_CHANNEL

    def test_sqlite_broker_order_correlation_store_blocks_ambiguous_cross_channel_identity_reuse(self, tmp_path):
        module = importlib.import_module("src.application.trading.broker_order_correlation")
        correlation_db = tmp_path / "channel-scoped-broker-correlation.sqlite3"
        store = module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)

        store.upsert_submission(
            order_id="order-miniqmt-0001",
            local_submission_id="submission-shared-0001",
            broker_channel=module.MINIQMT_BROKER_CHANNEL,
            adapter_path="web.backend.app.services.windows_bridge_adapter.qmt.submit",
            account_scope="sim-account-01",
            session_scope="miniqmt-session-0001",
            acknowledgement_status="awaiting_broker_acknowledgement",
        )
        store.upsert_submission(
            order_id="order-tdx-0001",
            local_submission_id="submission-shared-0001",
            broker_channel=module.TDX_MANUAL_BROKER_CHANNEL,
            adapter_path="operator.tdx.manual.submit",
            account_scope="sim-account-01",
            session_scope="tdx-session-0001",
            acknowledgement_status="awaiting_broker_acknowledgement",
        )

        store.bind_external_order_id(
            order_id="order-miniqmt-0001",
            external_order_id="external-shared-0001",
            acknowledgement_status="acknowledged",
        )
        store.bind_external_order_id(
            order_id="order-tdx-0001",
            external_order_id="external-shared-0001",
            acknowledgement_status="acknowledged",
        )

        assert store.get_by_local_submission_id("submission-shared-0001") is None
        assert store.get_by_external_order_id("external-shared-0001") is None

        miniqmt_submission_record = store.get_by_local_submission_id(
            "submission-shared-0001",
            broker_channel=module.MINIQMT_BROKER_CHANNEL,
        )
        assert miniqmt_submission_record is not None
        assert miniqmt_submission_record["order_id"] == "order-miniqmt-0001"
        assert miniqmt_submission_record["broker_channel"] == module.MINIQMT_BROKER_CHANNEL

        tdx_external_record = store.get_by_external_order_id(
            "external-shared-0001",
            broker_channel=module.TDX_MANUAL_BROKER_CHANNEL,
        )
        assert tdx_external_record is not None
        assert tdx_external_record["order_id"] == "order-tdx-0001"
        assert tdx_external_record["broker_channel"] == module.TDX_MANUAL_BROKER_CHANNEL

    def test_default_broker_order_correlation_store_uses_local_sqlite_ledger(self, tmp_path):
        module = importlib.import_module("src.application.trading.broker_order_correlation")
        correlation_db = tmp_path / "default-trading-broker-order-correlation.sqlite3"
        store = module.build_default_trading_broker_order_correlation_store(path=correlation_db)

        store.upsert_submission(
            order_id="order-0002",
            local_submission_id="submission-0002",
            adapter_path="src.application.trading.order_mgmt_service.OrderManagementService.place_order",
            account_scope="unscoped",
            session_scope=None,
            acknowledgement_status="awaiting_broker_acknowledgement",
        )

        record = store.get_order_correlation("order-0002")
        assert record is not None
        assert record["local_submission_id"] == "submission-0002"
        assert record["acknowledgement_status"] == "awaiting_broker_acknowledgement"

    def test_default_broker_submission_attempt_store_uses_local_sqlite_ledger(self, tmp_path):
        module = importlib.import_module("src.application.trading.broker_submission_attempt")
        attempt_db = tmp_path / "default-trading-broker-submission-attempt.sqlite3"
        store = module.build_default_trading_broker_submission_attempt_store(path=attempt_db)

        store.append(
            {
                "order_id": "order-0005",
                "local_submission_id": "submission-0005",
                "broker_channel": "miniqmt",
                "adapter_path": "web.backend.app.services.windows_bridge_adapter.qmt.submit",
                "account_scope": "sim-account-01",
                "session_scope": "session-0005",
                "submission_status": "bridge_task_accepted",
                "transport_status": "success",
                "bridge_task_id": "bridge-task-0005",
                "external_order_id": None,
                "source_name": "miniqmt/windows_bridge",
                "failure_reason": None,
                "handoff_status": None,
                "handoff_reason": None,
                "raw_response": {"status": "success", "task_id": "bridge-task-0005"},
            }
        )

        record = store.get_latest_for_order("order-0005", broker_channel="miniqmt")
        assert record is not None
        assert record["submission_status"] == "bridge_task_accepted"
        assert record["bridge_task_id"] == "bridge-task-0005"

    def test_place_order_with_miniqmt_primary_runtime_persists_bridge_task_submission_attempt(self, tmp_path):
        correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
        attempt_module = importlib.import_module("src.application.trading.broker_submission_attempt")
        runtime_module = importlib.import_module("src.application.trading.miniqmt_primary_runtime")

        class StubTransport:
            def __init__(self, response):
                self.response = response
                self.last_payload = None

            def submit_order(self, payload):
                self.last_payload = dict(payload)
                return dict(self.response)

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "miniqmt-primary-correlation.sqlite3"
        attempt_db = tmp_path / "miniqmt-primary-attempt.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        attempt_store = attempt_module.SqliteTradingBrokerSubmissionAttemptStore(attempt_db)
        audit_sink = MagicMock()
        transport = StubTransport({"status": "success", "task_id": "bridge-task-0001", "source": "qmt"})
        runtime = runtime_module.MiniQMTPrimaryBrokerRuntime(transport=transport, account_scope="sim-account-01")
        service = OrderManagementService(
            order_repo=order_repo,
            decision_audit_sink=audit_sink,
            broker_correlation_store=correlation_store,
            broker_submission_attempt_store=attempt_store,
            primary_broker_runtime=runtime,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="miniqmt-runtime-0001",
                request_id="miniqmt-runtime-session-0001",
            )
        )

        correlation_record = correlation_store.get_order_correlation(response.order_id)
        assert correlation_record is not None
        assert correlation_record["broker_channel"] == correlation_module.MINIQMT_BROKER_CHANNEL
        assert correlation_record["adapter_path"] == runtime_module.MINIQMT_PRIMARY_RUNTIME_ADAPTER_PATH
        assert correlation_record["account_scope"] == "sim-account-01"
        assert correlation_record["acknowledgement_status"] == "awaiting_broker_acknowledgement"
        assert correlation_record["external_order_id"] is None

        attempt_record = attempt_store.get_latest_for_order(
            response.order_id,
            broker_channel=correlation_module.MINIQMT_BROKER_CHANNEL,
        )
        assert attempt_record is not None
        assert attempt_record["submission_status"] == runtime_module.BRIDGE_TASK_ACCEPTED
        assert attempt_record["bridge_task_id"] == "bridge-task-0001"
        assert attempt_record["transport_status"] == "success"
        assert attempt_record["session_scope"] == "miniqmt-runtime-session-0001"

        assert transport.last_payload is not None
        assert transport.last_payload["client_order_id"] == "miniqmt-runtime-0001"
        assert transport.last_payload["order_id"] == response.order_id

        assert audit_sink.call_args_list[0].args[0]["decision_outcome"] == "broker_primary_submission_queued"
        assert audit_sink.call_args_list[-1].args[0]["decision_outcome"] == "submitted"

    def test_place_order_with_miniqmt_primary_runtime_immediate_ack_binds_external_identity(self, tmp_path):
        correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
        attempt_module = importlib.import_module("src.application.trading.broker_submission_attempt")
        runtime_module = importlib.import_module("src.application.trading.miniqmt_primary_runtime")

        class StubTransport:
            def submit_order(self, payload):
                return {
                    "status": "success",
                    "external_order_id": "miniqmt-broker-order-0002",
                    "task_id": "bridge-task-0002",
                }

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "miniqmt-ack-correlation.sqlite3"
        attempt_db = tmp_path / "miniqmt-ack-attempt.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        attempt_store = attempt_module.SqliteTradingBrokerSubmissionAttemptStore(attempt_db)
        audit_sink = MagicMock()
        runtime = runtime_module.MiniQMTPrimaryBrokerRuntime(transport=StubTransport(), account_scope="sim-account-02")
        service = OrderManagementService(
            order_repo=order_repo,
            decision_audit_sink=audit_sink,
            broker_correlation_store=correlation_store,
            broker_submission_attempt_store=attempt_store,
            primary_broker_runtime=runtime,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="miniqmt-runtime-ack-0002",
                request_id="miniqmt-runtime-session-0002",
            )
        )

        correlation_record = correlation_store.get_order_correlation(response.order_id)
        assert correlation_record is not None
        assert correlation_record["broker_channel"] == correlation_module.MINIQMT_BROKER_CHANNEL
        assert correlation_record["external_order_id"] == "miniqmt-broker-order-0002"
        assert correlation_record["acknowledgement_status"] == "acknowledged"

        attempt_record = attempt_store.get_latest_for_order(
            response.order_id,
            broker_channel=correlation_module.MINIQMT_BROKER_CHANNEL,
        )
        assert attempt_record is not None
        assert attempt_record["submission_status"] == runtime_module.BROKER_ACKNOWLEDGED_SUBMISSION
        assert attempt_record["external_order_id"] == "miniqmt-broker-order-0002"

        assert audit_sink.call_args_list[0].args[0]["decision_outcome"] == "broker_primary_acknowledged_immediately"
        assert audit_sink.call_args_list[-1].args[0]["decision_outcome"] == "submitted"

    def test_place_order_with_miniqmt_primary_runtime_persists_submission_failure_without_synthesizing_ack(self, tmp_path):
        correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
        attempt_module = importlib.import_module("src.application.trading.broker_submission_attempt")
        runtime_module = importlib.import_module("src.application.trading.miniqmt_primary_runtime")

        class FailingTransport:
            def submit_order(self, payload):
                raise RuntimeError("bridge offline")

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "miniqmt-failure-correlation.sqlite3"
        attempt_db = tmp_path / "miniqmt-failure-attempt.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        attempt_store = attempt_module.SqliteTradingBrokerSubmissionAttemptStore(attempt_db)
        audit_sink = MagicMock()
        runtime = runtime_module.MiniQMTPrimaryBrokerRuntime(transport=FailingTransport(), account_scope="sim-account-03")
        service = OrderManagementService(
            order_repo=order_repo,
            decision_audit_sink=audit_sink,
            broker_correlation_store=correlation_store,
            broker_submission_attempt_store=attempt_store,
            primary_broker_runtime=runtime,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="miniqmt-runtime-failure-0003",
                request_id="miniqmt-runtime-session-0003",
            )
        )

        correlation_record = correlation_store.get_order_correlation(response.order_id)
        assert correlation_record is not None
        assert correlation_record["broker_channel"] == correlation_module.MINIQMT_BROKER_CHANNEL
        assert correlation_record["external_order_id"] is None
        assert correlation_record["acknowledgement_status"] == "awaiting_broker_acknowledgement"

        attempt_record = attempt_store.get_latest_for_order(
            response.order_id,
            broker_channel=correlation_module.MINIQMT_BROKER_CHANNEL,
        )
        assert attempt_record is not None
        assert attempt_record["submission_status"] == runtime_module.SUBMISSION_FAILED
        assert attempt_record["failure_reason"] == "bridge offline"
        assert attempt_record["external_order_id"] is None

        assert audit_sink.call_args_list[0].args[0]["decision_outcome"] == "broker_primary_submission_failed"
        assert audit_sink.call_args_list[-1].args[0]["decision_outcome"] == "submitted"

    def test_ingest_miniqmt_bridge_result_payload_backfills_primary_submission_context(self, tmp_path):
        correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
        attempt_module = importlib.import_module("src.application.trading.broker_submission_attempt")
        event_module = importlib.import_module("src.application.trading.broker_lifecycle_event")
        runtime_module = importlib.import_module("src.application.trading.miniqmt_primary_runtime")

        class StubTransport:
            def submit_order(self, payload):
                return {"status": "success", "task_id": "bridge-task-0004", "source": "qmt"}

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "miniqmt-bridge-result-correlation.sqlite3"
        attempt_db = tmp_path / "miniqmt-bridge-result-attempt.sqlite3"
        event_db = tmp_path / "miniqmt-bridge-result-event.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        attempt_store = attempt_module.SqliteTradingBrokerSubmissionAttemptStore(attempt_db)
        event_store = event_module.SqliteTradingBrokerLifecycleEventStore(event_db)
        runtime = runtime_module.MiniQMTPrimaryBrokerRuntime(transport=StubTransport(), account_scope="sim-account-04")
        service = OrderManagementService(
            order_repo=order_repo,
            broker_correlation_store=correlation_store,
            broker_submission_attempt_store=attempt_store,
            broker_lifecycle_event_store=event_store,
            primary_broker_runtime=runtime,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="miniqmt-runtime-bridge-0004",
                request_id="miniqmt-runtime-session-0004",
            )
        )

        persisted_record = service.ingest_miniqmt_bridge_result_payload(
            {
                "task_id": "bridge-task-0004",
                "status": "accepted",
                "updated_at": "2026-04-28T05:20:00+00:00",
                "entrust_no": "miniqmt-broker-order-0004",
                "sequence_no": "miniqmt-seq-0004",
            }
        )

        assert persisted_record["event_type"] == "acknowledgement"
        assert persisted_record["order_id"] == response.order_id
        assert persisted_record["external_order_id"] == "miniqmt-broker-order-0004"
        assert persisted_record["identity_status"] == "matched_local_submission_id"
        assert persisted_record["sequence_id"] == "miniqmt-seq-0004"
        assert persisted_record["account_scope"] == "sim-account-04"
        assert persisted_record["session_scope"] == "miniqmt-runtime-session-0004"

        persisted_event = event_store.fetch_recent(limit=1)[0]
        assert persisted_event["local_submission_id"] == "miniqmt-runtime-bridge-0004"
        assert persisted_event["external_order_id"] == "miniqmt-broker-order-0004"

        correlation_record = correlation_store.get_order_correlation(response.order_id)
        assert correlation_record is not None
        assert correlation_record["broker_channel"] == correlation_module.MINIQMT_BROKER_CHANNEL
        assert correlation_record["external_order_id"] == "miniqmt-broker-order-0004"
        assert correlation_record["acknowledgement_status"] == "acknowledged"

    def test_record_tdx_supplemental_handoff_rotates_active_channel_and_preserves_primary_attempt(self, tmp_path):
        correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
        attempt_module = importlib.import_module("src.application.trading.broker_submission_attempt")
        runtime_module = importlib.import_module("src.application.trading.miniqmt_primary_runtime")
        followup_module = importlib.import_module("src.application.trading.primary_broker_followup")

        class StubTransport:
            def submit_order(self, payload):
                return {"status": "success", "task_id": "bridge-task-0005", "source": "qmt"}

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "tdx-handoff-correlation.sqlite3"
        attempt_db = tmp_path / "tdx-handoff-attempt.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        attempt_store = attempt_module.SqliteTradingBrokerSubmissionAttemptStore(attempt_db)
        audit_sink = MagicMock()
        runtime = runtime_module.MiniQMTPrimaryBrokerRuntime(transport=StubTransport(), account_scope="sim-account-05")
        service = OrderManagementService(
            order_repo=order_repo,
            decision_audit_sink=audit_sink,
            broker_correlation_store=correlation_store,
            broker_submission_attempt_store=attempt_store,
            primary_broker_runtime=runtime,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="miniqmt-runtime-handoff-0005",
                request_id="miniqmt-runtime-session-0005",
            )
        )

        handoff_record = service.record_tdx_supplemental_handoff(
            response.order_id,
            reason="miniqmt receipt requires operator-assisted continuation",
            actor_id="ops-01",
            source_id="manual-desk",
        )

        assert handoff_record["broker_channel"] == correlation_module.TDX_MANUAL_BROKER_CHANNEL
        assert handoff_record["submission_status"] == followup_module.SUPPLEMENTAL_HANDOFF_REQUESTED
        assert handoff_record["handoff_status"] == followup_module.SUPPLEMENTAL_HANDOFF_REVIEW_REQUIRED
        assert handoff_record["bridge_task_id"] == "bridge-task-0005"
        assert handoff_record["raw_response"]["prior_primary_submission_attempt"]["broker_channel"] == "miniqmt"

        correlation_record = correlation_store.get_order_correlation(response.order_id)
        assert correlation_record is not None
        assert correlation_record["broker_channel"] == correlation_module.TDX_MANUAL_BROKER_CHANNEL
        assert correlation_record["adapter_path"] == followup_module.TDX_SUPPLEMENTAL_HANDOFF_ADAPTER_PATH
        assert correlation_record["acknowledgement_status"] == "awaiting_broker_acknowledgement"
        assert correlation_record["external_order_id"] is None

        assert audit_sink.call_args_list[-1].args[0]["decision_outcome"] == "broker_supplemental_handoff_requested"

    def test_delayed_miniqmt_bridge_result_after_tdx_handoff_is_preserved_as_review_required(self, tmp_path):
        correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
        attempt_module = importlib.import_module("src.application.trading.broker_submission_attempt")
        divergence_module = importlib.import_module("src.application.trading.broker_divergence")
        event_module = importlib.import_module("src.application.trading.broker_lifecycle_event")
        runtime_module = importlib.import_module("src.application.trading.miniqmt_primary_runtime")
        followup_module = importlib.import_module("src.application.trading.primary_broker_followup")

        class StubTransport:
            def submit_order(self, payload):
                return {"status": "success", "task_id": "bridge-task-0006", "source": "qmt"}

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "late-miniqmt-after-handoff-correlation.sqlite3"
        attempt_db = tmp_path / "late-miniqmt-after-handoff-attempt.sqlite3"
        event_db = tmp_path / "late-miniqmt-after-handoff-event.sqlite3"
        divergence_db = tmp_path / "late-miniqmt-after-handoff-divergence.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        attempt_store = attempt_module.SqliteTradingBrokerSubmissionAttemptStore(attempt_db)
        event_store = event_module.SqliteTradingBrokerLifecycleEventStore(event_db)
        divergence_store = divergence_module.SqliteTradingBrokerDivergenceStore(divergence_db)
        runtime = runtime_module.MiniQMTPrimaryBrokerRuntime(transport=StubTransport(), account_scope="sim-account-06")
        service = OrderManagementService(
            order_repo=order_repo,
            broker_correlation_store=correlation_store,
            broker_submission_attempt_store=attempt_store,
            broker_lifecycle_event_store=event_store,
            broker_divergence_store=divergence_store,
            primary_broker_runtime=runtime,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="miniqmt-runtime-late-0006",
                request_id="miniqmt-runtime-session-0006",
            )
        )
        service.record_tdx_supplemental_handoff(
            response.order_id,
            reason="operator escalated to Tongdaxin after uncertain bridge receipt",
        )

        persisted_record = service.ingest_miniqmt_bridge_result_payload(
            {
                "task_id": "bridge-task-0006",
                "status": "accepted",
                "updated_at": "2026-04-28T05:25:00+00:00",
                "entrust_no": "late-miniqmt-order-0006",
                "sequence_no": "late-miniqmt-seq-0006",
            }
        )

        assert persisted_record["order_id"] is None
        assert persisted_record["identity_status"] == "unmatched_local_submission_id"
        assert persisted_record["external_order_id"] == "late-miniqmt-order-0006"

        divergence_record = divergence_store.fetch_recent(limit=1)[0]
        assert divergence_record["divergence_category"] == followup_module.UNMATCHED_DEFERRED_BRIDGE_RESULT
        assert divergence_record["review_status"] == "review_required"
        assert divergence_record["order_id"] == response.order_id
        assert divergence_record["local_submission_id"] == "miniqmt-runtime-late-0006"
        assert divergence_record["reason_code"] == "unmatched_deferred_bridge_result"

    def test_place_order_persists_awaiting_broker_acknowledgement_correlation_evidence(self, tmp_path):
        try:
            module = importlib.import_module("src.application.trading.broker_order_correlation")
        except ModuleNotFoundError as exc:
            pytest.fail(f"broker order correlation module missing: {exc}")

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "place-order-broker-correlation.sqlite3"
        correlation_store = module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)

        try:
            service = OrderManagementService(
                order_repo=order_repo,
                broker_correlation_store=correlation_store,
            )
        except TypeError as exc:
            pytest.fail(f"broker_correlation_store injection is missing: {exc}")

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="broker-correlation-key-0001",
                request_id="broker-correlation-request-0001",
            )
        )

        record = correlation_store.get_order_correlation(response.order_id)
        assert record is not None
        assert record["order_id"] == response.order_id
        assert record["local_submission_id"] == "broker-correlation-key-0001"
        assert record["broker_channel"] == module.LOCAL_ANCHOR_BROKER_CHANNEL
        assert record["adapter_path"] == "src.application.trading.order_mgmt_service.OrderManagementService.place_order"
        assert record["account_scope"] == "unscoped"
        assert record["acknowledgement_status"] == "awaiting_broker_acknowledgement"
        assert record["external_order_id"] is None

    def test_record_broker_acknowledgement_binds_external_identity_without_mutating_order_state(self, tmp_path):
        try:
            module = importlib.import_module("src.application.trading.broker_order_correlation")
        except ModuleNotFoundError as exc:
            pytest.fail(f"broker order correlation module missing: {exc}")

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "ack-broker-correlation.sqlite3"
        order_state_db = tmp_path / "ack-order-state.sqlite3"
        correlation_store = module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        order_state_store = SqliteTradingOrderStateStore(order_state_db)

        try:
            service = OrderManagementService(
                order_repo=order_repo,
                broker_correlation_store=correlation_store,
                order_state_store=order_state_store,
            )
        except TypeError as exc:
            pytest.fail(f"broker_correlation_store injection is missing: {exc}")

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="broker-ack-key-0001",
            )
        )

        if not hasattr(service, "record_broker_acknowledgement"):
            pytest.fail("record_broker_acknowledgement is missing")

        service.record_broker_acknowledgement(
            response.order_id,
            external_order_id="broker-order-ack-0001",
        )

        correlation_record = correlation_store.get_order_correlation(response.order_id)
        assert correlation_record is not None
        assert correlation_record["external_order_id"] == "broker-order-ack-0001"
        assert correlation_record["acknowledgement_status"] == "acknowledged"

        order_state_record = order_state_store.get_order_state(response.order_id)
        assert order_state_record is not None
        assert order_state_record["status"] == "SUBMITTED"

    def test_default_broker_lifecycle_event_store_uses_local_sqlite_ledger(self, tmp_path):
        try:
            module = importlib.import_module("src.application.trading.broker_lifecycle_event")
        except ModuleNotFoundError as exc:
            pytest.fail(f"broker lifecycle event module missing: {exc}")

        event_db = tmp_path / "default-trading-broker-lifecycle-event.sqlite3"
        store = module.build_default_trading_broker_lifecycle_event_store(path=event_db)

        store.append(
            {
                "event_type": "acknowledgement",
                "order_id": "order-0003",
                "external_order_id": "broker-order-0003",
                "local_submission_id": "submission-0003",
                "local_order_id": None,
                "source_timestamp": "2026-04-28T04:00:00+00:00",
                "source_name": "sim-broker",
                "event_id": "ack-event-0003",
                "sequence_id": None,
                "identity_status": "matched_local_submission_id",
                "sequencing_status": "sequencing_metadata_present",
                "fill_quantity": None,
                "fill_price": None,
                "reason_code": None,
                "reason_detail": None,
                "adapter_path": "src.application.trading.order_mgmt_service.OrderManagementService.place_order",
                "account_scope": "unscoped",
                "session_scope": "broker-session-0003",
            }
        )

        records = store.fetch_recent(limit=1)
        assert len(records) == 1
        assert records[0]["event_type"] == "acknowledgement"
        assert records[0]["external_order_id"] == "broker-order-0003"

    def test_record_broker_lifecycle_event_acknowledgement_binds_external_identity_and_preserves_metadata(self, tmp_path):
        try:
            correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
            event_module = importlib.import_module("src.application.trading.broker_lifecycle_event")
        except ModuleNotFoundError as exc:
            pytest.fail(f"broker lifecycle dependency missing: {exc}")

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "ack-event-correlation.sqlite3"
        event_db = tmp_path / "ack-event-ledger.sqlite3"
        order_state_db = tmp_path / "ack-event-order-state.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        event_store = event_module.SqliteTradingBrokerLifecycleEventStore(event_db)
        order_state_store = SqliteTradingOrderStateStore(order_state_db)

        try:
            service = OrderManagementService(
                order_repo=order_repo,
                broker_correlation_store=correlation_store,
                broker_lifecycle_event_store=event_store,
                order_state_store=order_state_store,
            )
        except TypeError as exc:
            pytest.fail(f"broker_lifecycle_event_store injection is missing: {exc}")

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="broker-lifecycle-ack-0001",
                request_id="broker-session-0001",
            )
        )

        lifecycle_event = event_module.BrokerLifecycleEvent(
            event_type="acknowledgement",
            external_order_id="broker-order-ack-0001",
            local_submission_id="broker-lifecycle-ack-0001",
            source_timestamp=datetime(2026, 4, 28, 4, 0, tzinfo=timezone.utc),
            source_name="sim-broker",
            event_id="ack-event-0001",
        )

        if not hasattr(service, "record_broker_lifecycle_event"):
            pytest.fail("record_broker_lifecycle_event is missing")

        persisted_record = service.record_broker_lifecycle_event(lifecycle_event)

        assert persisted_record["order_id"] == response.order_id
        assert persisted_record["external_order_id"] == "broker-order-ack-0001"
        assert persisted_record["identity_status"] == "matched_local_submission_id"
        assert persisted_record["sequencing_status"] == "sequencing_metadata_present"
        assert persisted_record["replay_suppression_status"] == "eligible"
        assert persisted_record["replay_suppression_basis"] == "event_id"

        correlation_record = correlation_store.get_order_correlation(response.order_id)
        assert correlation_record is not None
        assert correlation_record["external_order_id"] == "broker-order-ack-0001"
        assert correlation_record["acknowledgement_status"] == "acknowledged"

        recent_record = event_store.fetch_recent(limit=1)[0]
        assert recent_record["event_type"] == "acknowledgement"
        assert recent_record["event_id"] == "ack-event-0001"
        assert recent_record["source_timestamp"] == "2026-04-28T04:00:00+00:00"

        order_state_record = order_state_store.get_order_state(response.order_id)
        assert order_state_record is not None
        assert order_state_record["status"] == "SUBMITTED"

    def test_ingest_miniqmt_lifecycle_payload_normalizes_windows_bridge_acknowledgement(self, tmp_path):
        try:
            correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
            event_module = importlib.import_module("src.application.trading.broker_lifecycle_event")
            miniqmt_module = importlib.import_module("src.application.trading.miniqmt_lifecycle_ingestion")
        except ModuleNotFoundError as exc:
            pytest.fail(f"miniqmt lifecycle dependency missing: {exc}")

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "miniqmt-ack-correlation.sqlite3"
        event_db = tmp_path / "miniqmt-ack-event-ledger.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        event_store = event_module.SqliteTradingBrokerLifecycleEventStore(event_db)
        service = OrderManagementService(
            order_repo=order_repo,
            broker_correlation_store=correlation_store,
            broker_lifecycle_event_store=event_store,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="miniqmt-submission-0001",
                request_id="miniqmt-session-0001",
            )
        )
        correlation_store.upsert_submission(
            order_id=response.order_id,
            local_submission_id="miniqmt-submission-0001",
            broker_channel=correlation_module.MINIQMT_BROKER_CHANNEL,
            adapter_path="web.backend.app.services.windows_bridge_adapter.qmt.submit",
            account_scope="sim-account-01",
            session_scope="miniqmt-session-0001",
            acknowledgement_status="awaiting_broker_acknowledgement",
        )

        if not hasattr(service, "ingest_miniqmt_lifecycle_payload"):
            pytest.fail("ingest_miniqmt_lifecycle_payload is missing")

        persisted_record = service.ingest_miniqmt_lifecycle_payload(
            {
                "status": "accepted",
                "updated_at": "2026-04-28T05:00:00+00:00",
                "entrust_no": "miniqmt-broker-order-0001",
                "client_order_id": "miniqmt-submission-0001",
                "sequence_no": "miniqmt-seq-0001",
            }
        )

        assert persisted_record["event_type"] == "acknowledgement"
        assert persisted_record["order_id"] == response.order_id
        assert persisted_record["broker_channel"] == correlation_module.MINIQMT_BROKER_CHANNEL
        assert persisted_record["source_name"] == miniqmt_module.MINIQMT_WINDOWS_BRIDGE_SOURCE_NAME
        assert persisted_record["external_order_id"] == "miniqmt-broker-order-0001"
        assert persisted_record["identity_status"] == "matched_local_submission_id"
        assert persisted_record["sequencing_status"] == "sequencing_metadata_present"
        assert persisted_record["sequence_id"] == "miniqmt-seq-0001"
        assert persisted_record["adapter_path"] == "web.backend.app.services.windows_bridge_adapter.qmt.submit"
        assert persisted_record["account_scope"] == "sim-account-01"
        assert persisted_record["session_scope"] == "miniqmt-session-0001"

        persisted_event = event_store.fetch_recent(limit=1)[0]
        assert persisted_event["broker_channel"] == correlation_module.MINIQMT_BROKER_CHANNEL
        assert persisted_event["source_name"] == miniqmt_module.MINIQMT_WINDOWS_BRIDGE_SOURCE_NAME

        correlation_record = correlation_store.get_order_correlation(response.order_id)
        assert correlation_record is not None
        assert correlation_record["broker_channel"] == correlation_module.MINIQMT_BROKER_CHANNEL
        assert correlation_record["external_order_id"] == "miniqmt-broker-order-0001"
        assert correlation_record["acknowledgement_status"] == "acknowledged"

    def test_ingest_tdx_manual_lifecycle_payload_persists_review_required_supplemental_divergence(self, tmp_path):
        try:
            correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
            event_module = importlib.import_module("src.application.trading.broker_lifecycle_event")
            divergence_module = importlib.import_module("src.application.trading.broker_divergence")
            tdx_module = importlib.import_module("src.application.trading.tdx_manual_lifecycle_ingestion")
        except ModuleNotFoundError as exc:
            pytest.fail(f"tdx manual lifecycle dependency missing: {exc}")

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "tdx-manual-correlation.sqlite3"
        event_db = tmp_path / "tdx-manual-event-ledger.sqlite3"
        divergence_db = tmp_path / "tdx-manual-divergence.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        event_store = event_module.SqliteTradingBrokerLifecycleEventStore(event_db)
        divergence_store = divergence_module.SqliteTradingBrokerDivergenceStore(divergence_db)
        service = OrderManagementService(
            order_repo=order_repo,
            broker_correlation_store=correlation_store,
            broker_lifecycle_event_store=event_store,
            broker_divergence_store=divergence_store,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="tdx-manual-submission-0001",
                request_id="tdx-manual-session-0001",
            )
        )
        correlation_store.upsert_submission(
            order_id=response.order_id,
            local_submission_id="tdx-manual-submission-0001",
            broker_channel=correlation_module.TDX_MANUAL_BROKER_CHANNEL,
            adapter_path="operator.tdx.manual.submit",
            account_scope="sim-account-02",
            session_scope="tdx-manual-session-0001",
            acknowledgement_status="awaiting_broker_acknowledgement",
        )

        if not hasattr(service, "ingest_tdx_manual_lifecycle_payload"):
            pytest.fail("ingest_tdx_manual_lifecycle_payload is missing")

        persisted_record = service.ingest_tdx_manual_lifecycle_payload(
            {
                "status": "accepted",
                "captured_at": "2026-04-28T05:10:00+00:00",
                "external_order_id": "tdx-manual-order-0001",
                "client_order_id": "tdx-manual-submission-0001",
                "operator_note": "manual trading desk screenshot import",
            }
        )

        assert persisted_record["event_type"] == "acknowledgement"
        assert persisted_record["order_id"] == response.order_id
        assert persisted_record["broker_channel"] == correlation_module.TDX_MANUAL_BROKER_CHANNEL
        assert persisted_record["source_name"] == tdx_module.TDX_MANUAL_SOURCE_NAME
        assert persisted_record["external_order_id"] == "tdx-manual-order-0001"
        assert persisted_record["identity_status"] == "matched_local_submission_id"
        assert persisted_record["replay_suppression_status"] == "blocked"
        assert persisted_record["replay_suppression_reason"] == "broker_channel_not_replay_authorized"

        persisted_event = event_store.fetch_recent(limit=1)[0]
        assert persisted_event["broker_channel"] == correlation_module.TDX_MANUAL_BROKER_CHANNEL
        assert persisted_event["reason_detail"] == "manual trading desk screenshot import"

        divergence_record = divergence_store.fetch_recent(limit=1)[0]
        assert divergence_record["divergence_category"] == "supplemental_channel_review_required"
        assert divergence_record["review_status"] == "review_required"
        assert divergence_record["required_evidence"] == "operator_confirmation_and_broker_artifact"
        assert divergence_record["broker_channel"] == correlation_module.TDX_MANUAL_BROKER_CHANNEL

        correlation_record = correlation_store.get_order_correlation(response.order_id)
        assert correlation_record is not None
        assert correlation_record["broker_channel"] == correlation_module.TDX_MANUAL_BROKER_CHANNEL
        assert correlation_record["external_order_id"] == "tdx-manual-order-0001"
        assert correlation_record["acknowledgement_status"] == "acknowledged"

    def test_tdx_manual_channel_does_not_inherit_replay_suppression_authority(self, tmp_path):
        try:
            correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
            event_module = importlib.import_module("src.application.trading.broker_lifecycle_event")
            divergence_module = importlib.import_module("src.application.trading.broker_divergence")
        except ModuleNotFoundError as exc:
            pytest.fail(f"tdx manual replay suppression dependency missing: {exc}")

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "tdx-manual-duplicate-correlation.sqlite3"
        event_db = tmp_path / "tdx-manual-duplicate-event-ledger.sqlite3"
        divergence_db = tmp_path / "tdx-manual-duplicate-divergence.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        event_store = event_module.SqliteTradingBrokerLifecycleEventStore(event_db)
        divergence_store = divergence_module.SqliteTradingBrokerDivergenceStore(divergence_db)
        service = OrderManagementService(
            order_repo=order_repo,
            broker_correlation_store=correlation_store,
            broker_lifecycle_event_store=event_store,
            broker_divergence_store=divergence_store,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="tdx-manual-duplicate-0001",
                request_id="tdx-manual-duplicate-session-0001",
            )
        )
        correlation_store.upsert_submission(
            order_id=response.order_id,
            local_submission_id="tdx-manual-duplicate-0001",
            broker_channel=correlation_module.TDX_MANUAL_BROKER_CHANNEL,
            adapter_path="operator.tdx.manual.submit",
            account_scope="sim-account-03",
            session_scope="tdx-manual-duplicate-session-0001",
            acknowledgement_status="awaiting_broker_acknowledgement",
        )

        first_record = service.ingest_tdx_manual_lifecycle_payload(
            {
                "status": "accepted",
                "captured_at": "2026-04-28T05:20:00+00:00",
                "external_order_id": "tdx-manual-duplicate-order-0001",
                "client_order_id": "tdx-manual-duplicate-0001",
                "capture_sequence": "tdx-manual-dup-seq-0001",
            }
        )
        duplicate_record = service.ingest_tdx_manual_lifecycle_payload(
            {
                "status": "accepted",
                "captured_at": "2026-04-28T05:21:00+00:00",
                "external_order_id": "tdx-manual-duplicate-order-0001",
                "client_order_id": "tdx-manual-duplicate-0001",
                "capture_sequence": "tdx-manual-dup-seq-0001",
            }
        )

        assert first_record["replay_suppression_status"] == "blocked"
        assert first_record["replay_suppression_reason"] == "broker_channel_not_replay_authorized"
        assert duplicate_record["replay_suppression_status"] == "blocked"
        assert duplicate_record["replay_suppression_reason"] == "broker_channel_not_replay_authorized"

        recent_records = event_store.fetch_recent(limit=10)
        assert len(recent_records) == 2
        assert recent_records[0]["broker_channel"] == correlation_module.TDX_MANUAL_BROKER_CHANNEL
        assert recent_records[1]["broker_channel"] == correlation_module.TDX_MANUAL_BROKER_CHANNEL

    def test_tdx_manual_channel_does_not_inherit_auto_resolution_authority(self, tmp_path):
        try:
            correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
            event_module = importlib.import_module("src.application.trading.broker_lifecycle_event")
            divergence_module = importlib.import_module("src.application.trading.broker_divergence")
        except ModuleNotFoundError as exc:
            pytest.fail(f"tdx manual auto-resolution dependency missing: {exc}")

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "tdx-manual-auto-resolution-correlation.sqlite3"
        event_db = tmp_path / "tdx-manual-auto-resolution-event-ledger.sqlite3"
        divergence_db = tmp_path / "tdx-manual-auto-resolution-divergence.sqlite3"
        order_state_db = tmp_path / "tdx-manual-auto-resolution-order-state.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        event_store = event_module.SqliteTradingBrokerLifecycleEventStore(event_db)
        divergence_store = divergence_module.SqliteTradingBrokerDivergenceStore(divergence_db)
        order_state_store = SqliteTradingOrderStateStore(order_state_db)
        service = OrderManagementService(
            order_repo=order_repo,
            broker_correlation_store=correlation_store,
            broker_lifecycle_event_store=event_store,
            broker_divergence_store=divergence_store,
            order_state_store=order_state_store,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="tdx-manual-auto-resolution-0001",
                request_id="tdx-manual-auto-resolution-session-0001",
            )
        )
        correlation_store.upsert_submission(
            order_id=response.order_id,
            local_submission_id="tdx-manual-auto-resolution-0001",
            broker_channel=correlation_module.TDX_MANUAL_BROKER_CHANNEL,
            adapter_path="operator.tdx.manual.submit",
            account_scope="sim-account-04",
            session_scope="tdx-manual-auto-resolution-session-0001",
            acknowledgement_status="awaiting_broker_acknowledgement",
        )
        correlation_store.bind_external_order_id(
            order_id=response.order_id,
            external_order_id="tdx-manual-terminal-order-0001",
            acknowledgement_status="acknowledged",
        )

        persisted_record = service.ingest_tdx_manual_lifecycle_payload(
            {
                "status": "rejected",
                "captured_at": "2026-04-28T05:25:00+00:00",
                "external_order_id": "tdx-manual-terminal-order-0001",
                "client_order_id": "tdx-manual-auto-resolution-0001",
                "capture_sequence": "tdx-manual-auto-resolve-seq-0001",
                "operator_reason_code": "operator_reject_capture",
                "operator_note": "manual reject evidence from trading desk",
            }
        )

        assert persisted_record["replay_suppression_status"] == "blocked"
        assert persisted_record["replay_suppression_reason"] == "broker_channel_not_replay_authorized"

        divergence_record = divergence_store.fetch_recent(limit=1)[0]
        assert divergence_record["divergence_category"] == "externally_terminal_locally_open"
        assert divergence_record["review_status"] == "review_required"
        assert divergence_record["auto_resolution_status"] == "blocked"
        assert divergence_record["auto_resolution_reason"] == "broker_channel_not_auto_resolution_authorized"

        order_state_record = order_state_store.get_order_state(response.order_id)
        assert order_state_record is not None
        assert order_state_record["status"] == "SUBMITTED"
        assert order_repo.get_by_id(OrderId(response.order_id)).status == OrderStatus.SUBMITTED

    def test_record_broker_lifecycle_event_execution_matches_external_identity_and_preserves_sequence_metadata(self, tmp_path):
        try:
            correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
            event_module = importlib.import_module("src.application.trading.broker_lifecycle_event")
        except ModuleNotFoundError as exc:
            pytest.fail(f"broker lifecycle dependency missing: {exc}")

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "execution-event-correlation.sqlite3"
        event_db = tmp_path / "execution-event-ledger.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        event_store = event_module.SqliteTradingBrokerLifecycleEventStore(event_db)
        service = OrderManagementService(
            order_repo=order_repo,
            broker_correlation_store=correlation_store,
            broker_lifecycle_event_store=event_store,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="broker-lifecycle-execution-0001",
            )
        )
        service.record_broker_acknowledgement(
            response.order_id,
            external_order_id="broker-order-execution-0001",
        )

        lifecycle_event = event_module.BrokerLifecycleEvent(
            event_type="execution",
            external_order_id="broker-order-execution-0001",
            source_timestamp=datetime(2026, 4, 28, 4, 5, tzinfo=timezone.utc),
            source_name="sim-broker",
            sequence_id="exec-seq-0001",
            filled_quantity=50,
            fill_price=10.55,
        )

        persisted_record = service.record_broker_lifecycle_event(lifecycle_event)

        assert persisted_record["order_id"] == response.order_id
        assert persisted_record["identity_status"] == "matched_external_order_id"
        assert persisted_record["sequencing_status"] == "sequencing_metadata_present"
        assert persisted_record["sequence_id"] == "exec-seq-0001"
        assert persisted_record["fill_quantity"] == 50
        assert persisted_record["fill_price"] == 10.55
        assert persisted_record["replay_suppression_status"] == "eligible"
        assert persisted_record["replay_suppression_basis"] == "sequence_id"

        recent_record = event_store.fetch_recent(limit=1)[0]
        assert recent_record["event_type"] == "execution"
        assert recent_record["external_order_id"] == "broker-order-execution-0001"
        assert recent_record["sequence_id"] == "exec-seq-0001"

    def test_record_broker_lifecycle_event_classifies_missing_identity_and_missing_sequence_explicitly(self, tmp_path):
        try:
            event_module = importlib.import_module("src.application.trading.broker_lifecycle_event")
        except ModuleNotFoundError as exc:
            pytest.fail(f"broker lifecycle event module missing: {exc}")

        order_repo = self.InMemoryOrderRepository()
        event_db = tmp_path / "missing-identity-event-ledger.sqlite3"
        event_store = event_module.SqliteTradingBrokerLifecycleEventStore(event_db)
        service = OrderManagementService(
            order_repo=order_repo,
            broker_lifecycle_event_store=event_store,
        )

        lifecycle_event = event_module.BrokerLifecycleEvent(
            event_type="cancel",
            source_timestamp=datetime(2026, 4, 28, 4, 10, tzinfo=timezone.utc),
            source_name="sim-broker",
            reason_code="broker_cancelled_session",
        )

        persisted_record = service.record_broker_lifecycle_event(lifecycle_event)

        assert persisted_record["order_id"] is None
        assert persisted_record["identity_status"] == "missing_identity"
        assert persisted_record["sequencing_status"] == "sequencing_metadata_missing"
        assert persisted_record["replay_suppression_status"] == "blocked"
        assert persisted_record["replay_suppression_reason"] == "missing_matched_broker_identity"

        recent_record = event_store.fetch_recent(limit=1)[0]
        assert recent_record["event_type"] == "cancel"
        assert recent_record["reason_code"] == "broker_cancelled_session"
        assert recent_record["identity_status"] == "missing_identity"

    def test_default_broker_divergence_store_uses_local_sqlite_ledger(self, tmp_path):
        try:
            module = importlib.import_module("src.application.trading.broker_divergence")
        except ModuleNotFoundError as exc:
            pytest.fail(f"broker divergence module missing: {exc}")

        divergence_db = tmp_path / "default-trading-broker-divergence.sqlite3"
        store = module.build_default_trading_broker_divergence_store(path=divergence_db)

        store.append(
            {
                "divergence_category": "awaiting_broker_acknowledgement",
                "review_status": "review_required",
                "review_owner": "trading_operations",
                "next_action": "manual_reconciliation_required",
                "required_evidence": "broker_acknowledgement_or_terminal_fact",
                "order_id": "order-0004",
                "event_type": "cancel",
                "external_order_id": None,
                "local_submission_id": "submission-0004",
                "local_order_id": None,
                "local_order_status": "SUBMITTED",
                "identity_status": "matched_local_submission_id",
                "sequencing_status": "sequencing_metadata_missing",
                "reported_filled_quantity": None,
                "reported_fill_price": None,
                "reason_code": "pending_broker_identity",
                "reason_detail": "non-ack broker event arrived before external identity binding",
                "adapter_path": "src.application.trading.order_mgmt_service.OrderManagementService.place_order",
                "account_scope": "unscoped",
                "session_scope": "broker-session-0004",
            }
        )

        record = store.fetch_recent(limit=1)[0]
        assert record["divergence_category"] == "awaiting_broker_acknowledgement"
        assert record["review_status"] == "review_required"
        assert record["review_owner"] == "trading_operations"

    def test_record_broker_lifecycle_event_persists_unmatched_external_order_divergence(self, tmp_path):
        try:
            event_module = importlib.import_module("src.application.trading.broker_lifecycle_event")
            divergence_module = importlib.import_module("src.application.trading.broker_divergence")
        except ModuleNotFoundError as exc:
            pytest.fail(f"broker reconciliation dependency missing: {exc}")

        order_repo = self.InMemoryOrderRepository()
        event_db = tmp_path / "unmatched-external-event-ledger.sqlite3"
        divergence_db = tmp_path / "unmatched-external-divergence-ledger.sqlite3"
        event_store = event_module.SqliteTradingBrokerLifecycleEventStore(event_db)
        divergence_store = divergence_module.SqliteTradingBrokerDivergenceStore(divergence_db)

        try:
            service = OrderManagementService(
                order_repo=order_repo,
                broker_lifecycle_event_store=event_store,
                broker_divergence_store=divergence_store,
            )
        except TypeError as exc:
            pytest.fail(f"broker_divergence_store injection is missing: {exc}")

        persisted_record = service.record_broker_lifecycle_event(
            event_module.BrokerLifecycleEvent(
                event_type="execution",
                external_order_id="broker-order-unmatched-0001",
                source_timestamp=datetime(2026, 4, 28, 4, 15, tzinfo=timezone.utc),
                source_name="sim-broker",
                sequence_id="exec-seq-unmatched-0001",
                filled_quantity=100,
                fill_price=10.5,
            )
        )

        assert persisted_record["order_id"] is None
        assert persisted_record["identity_status"] == "unmatched_external_order_id"

        divergence_record = divergence_store.fetch_recent(limit=1)[0]
        assert divergence_record["divergence_category"] == "unmatched_external_order"
        assert divergence_record["review_status"] == "review_required"
        assert divergence_record["review_owner"] == "trading_operations"
        assert divergence_record["order_id"] is None
        assert divergence_record["external_order_id"] == "broker-order-unmatched-0001"
        assert divergence_record["local_order_status"] is None

    def test_record_broker_lifecycle_event_persists_locally_terminal_externally_open_divergence(self, tmp_path):
        try:
            correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
            event_module = importlib.import_module("src.application.trading.broker_lifecycle_event")
            divergence_module = importlib.import_module("src.application.trading.broker_divergence")
        except ModuleNotFoundError as exc:
            pytest.fail(f"broker reconciliation dependency missing: {exc}")

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "terminal-local-correlation.sqlite3"
        event_db = tmp_path / "terminal-local-event-ledger.sqlite3"
        divergence_db = tmp_path / "terminal-local-divergence-ledger.sqlite3"
        order_state_db = tmp_path / "terminal-local-order-state.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        event_store = event_module.SqliteTradingBrokerLifecycleEventStore(event_db)
        divergence_store = divergence_module.SqliteTradingBrokerDivergenceStore(divergence_db)
        order_state_store = SqliteTradingOrderStateStore(order_state_db)

        service = OrderManagementService(
            order_repo=order_repo,
            broker_correlation_store=correlation_store,
            broker_lifecycle_event_store=event_store,
            broker_divergence_store=divergence_store,
            order_state_store=order_state_store,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="terminal-local-0001",
            )
        )
        service.record_broker_acknowledgement(
            response.order_id,
            external_order_id="broker-order-terminal-local-0001",
        )
        cancelled_response = service.cancel_order(response.order_id, reason="operator_cancelled_submission")
        assert cancelled_response.status == OrderStatus.CANCELLED.value

        persisted_record = service.record_broker_lifecycle_event(
            event_module.BrokerLifecycleEvent(
                event_type="execution",
                external_order_id="broker-order-terminal-local-0001",
                source_timestamp=datetime(2026, 4, 28, 4, 20, tzinfo=timezone.utc),
                source_name="sim-broker",
                sequence_id="exec-seq-terminal-local-0001",
                filled_quantity=50,
                fill_price=10.45,
            )
        )

        assert persisted_record["order_id"] == response.order_id
        assert persisted_record["identity_status"] == "matched_external_order_id"

        divergence_record = divergence_store.fetch_recent(limit=1)[0]
        assert divergence_record["divergence_category"] == "locally_terminal_externally_open"
        assert divergence_record["review_status"] == "review_required"
        assert divergence_record["order_id"] == response.order_id
        assert divergence_record["local_order_status"] == "CANCELLED"

        order_state_record = order_state_store.get_order_state(response.order_id)
        assert order_state_record is not None
        assert order_state_record["status"] == "CANCELLED"
        assert order_repo.get_by_id(OrderId(response.order_id)).status == OrderStatus.CANCELLED

    def test_record_broker_lifecycle_event_persists_externally_terminal_locally_open_divergence(self, tmp_path):
        try:
            correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
            event_module = importlib.import_module("src.application.trading.broker_lifecycle_event")
            divergence_module = importlib.import_module("src.application.trading.broker_divergence")
        except ModuleNotFoundError as exc:
            pytest.fail(f"broker reconciliation dependency missing: {exc}")

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "terminal-external-correlation.sqlite3"
        event_db = tmp_path / "terminal-external-event-ledger.sqlite3"
        divergence_db = tmp_path / "terminal-external-divergence-ledger.sqlite3"
        order_state_db = tmp_path / "terminal-external-order-state.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        event_store = event_module.SqliteTradingBrokerLifecycleEventStore(event_db)
        divergence_store = divergence_module.SqliteTradingBrokerDivergenceStore(divergence_db)
        order_state_store = SqliteTradingOrderStateStore(order_state_db)

        service = OrderManagementService(
            order_repo=order_repo,
            broker_correlation_store=correlation_store,
            broker_lifecycle_event_store=event_store,
            broker_divergence_store=divergence_store,
            order_state_store=order_state_store,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="terminal-external-0001",
            )
        )
        service.record_broker_acknowledgement(
            response.order_id,
            external_order_id="broker-order-terminal-external-0001",
        )

        persisted_record = service.record_broker_lifecycle_event(
            event_module.BrokerLifecycleEvent(
                event_type="reject",
                external_order_id="broker-order-terminal-external-0001",
                source_timestamp=datetime(2026, 4, 28, 4, 25, tzinfo=timezone.utc),
                source_name="sim-broker",
                event_id="reject-event-terminal-external-0001",
                reason_code="broker_rejected",
                reason_detail="broker rejected after local submit",
            )
        )

        assert persisted_record["order_id"] == response.order_id
        assert persisted_record["identity_status"] == "matched_external_order_id"

        divergence_record = divergence_store.fetch_recent(limit=1)[0]
        assert divergence_record["divergence_category"] == "externally_terminal_locally_open"
        assert divergence_record["review_status"] == "review_required"
        assert divergence_record["auto_resolution_status"] == "blocked"
        assert divergence_record["auto_resolution_reason"] == "missing_broker_sequence_identity"
        assert divergence_record["order_id"] == response.order_id
        assert divergence_record["local_order_status"] == "SUBMITTED"
        assert divergence_record["reason_code"] == "broker_rejected"

        order_state_record = order_state_store.get_order_state(response.order_id)
        assert order_state_record is not None
        assert order_state_record["status"] == "SUBMITTED"
        assert order_repo.get_by_id(OrderId(response.order_id)).status == OrderStatus.SUBMITTED

    def test_record_broker_lifecycle_event_persists_quantity_or_fill_divergence_without_mutating_local_state(
        self,
        tmp_path,
    ):
        try:
            correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
            event_module = importlib.import_module("src.application.trading.broker_lifecycle_event")
            divergence_module = importlib.import_module("src.application.trading.broker_divergence")
        except ModuleNotFoundError as exc:
            pytest.fail(f"broker reconciliation dependency missing: {exc}")

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "quantity-divergence-correlation.sqlite3"
        event_db = tmp_path / "quantity-divergence-event-ledger.sqlite3"
        divergence_db = tmp_path / "quantity-divergence-ledger.sqlite3"
        order_state_db = tmp_path / "quantity-divergence-order-state.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        event_store = event_module.SqliteTradingBrokerLifecycleEventStore(event_db)
        divergence_store = divergence_module.SqliteTradingBrokerDivergenceStore(divergence_db)
        order_state_store = SqliteTradingOrderStateStore(order_state_db)

        service = OrderManagementService(
            order_repo=order_repo,
            broker_correlation_store=correlation_store,
            broker_lifecycle_event_store=event_store,
            broker_divergence_store=divergence_store,
            order_state_store=order_state_store,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=200,
                side="BUY",
                order_type="LIMIT",
                price=10.0,
                idempotency_key="quantity-divergence-0001",
            )
        )
        service.record_broker_acknowledgement(
            response.order_id,
            external_order_id="broker-order-quantity-divergence-0001",
        )

        local_fill_response = service.handle_execution_report(response.order_id, filled_qty=100, price=10.0)
        assert local_fill_response.status == OrderStatus.PARTIALLY_FILLED.value

        persisted_record = service.record_broker_lifecycle_event(
            event_module.BrokerLifecycleEvent(
                event_type="execution",
                external_order_id="broker-order-quantity-divergence-0001",
                source_timestamp=datetime(2026, 4, 28, 4, 30, tzinfo=timezone.utc),
                source_name="sim-broker",
                sequence_id="exec-seq-quantity-divergence-0001",
                filled_quantity=250,
                fill_price=10.2,
            )
        )

        assert persisted_record["order_id"] == response.order_id
        assert persisted_record["identity_status"] == "matched_external_order_id"

        divergence_record = divergence_store.fetch_recent(limit=1)[0]
        assert divergence_record["divergence_category"] == "quantity_or_fill_divergence"
        assert divergence_record["review_status"] == "review_required"
        assert divergence_record["order_id"] == response.order_id
        assert divergence_record["local_order_status"] == "PARTIALLY_FILLED"
        assert divergence_record["reported_filled_quantity"] == 250
        assert divergence_record["reported_fill_price"] == 10.2

        order_state_record = order_state_store.get_order_state(response.order_id)
        assert order_state_record is not None
        assert order_state_record["status"] == "PARTIALLY_FILLED"

        preserved_order = order_repo.get_by_id(OrderId(response.order_id))
        assert preserved_order.status == OrderStatus.PARTIALLY_FILLED
        assert preserved_order.filled_quantity == 100
        assert preserved_order.average_fill_price == 10.0

    def test_record_broker_lifecycle_event_suppresses_duplicate_execution_when_sequence_identity_matches(self, tmp_path):
        try:
            correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
            event_module = importlib.import_module("src.application.trading.broker_lifecycle_event")
        except ModuleNotFoundError as exc:
            pytest.fail(f"broker replay suppression dependency missing: {exc}")

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "duplicate-execution-correlation.sqlite3"
        event_db = tmp_path / "duplicate-execution-event-ledger.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        event_store = event_module.SqliteTradingBrokerLifecycleEventStore(event_db)

        service = OrderManagementService(
            order_repo=order_repo,
            broker_correlation_store=correlation_store,
            broker_lifecycle_event_store=event_store,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="duplicate-execution-0001",
            )
        )
        service.record_broker_acknowledgement(
            response.order_id,
            external_order_id="broker-order-duplicate-execution-0001",
        )

        lifecycle_event = event_module.BrokerLifecycleEvent(
            event_type="execution",
            external_order_id="broker-order-duplicate-execution-0001",
            source_timestamp=datetime(2026, 4, 28, 4, 35, tzinfo=timezone.utc),
            source_name="sim-broker",
            sequence_id="exec-seq-duplicate-0001",
            filled_quantity=25,
            fill_price=10.6,
        )

        first_record = service.record_broker_lifecycle_event(lifecycle_event)
        duplicate_record = service.record_broker_lifecycle_event(lifecycle_event)

        assert first_record["replay_suppression_status"] == "eligible"
        assert duplicate_record["replay_suppression_status"] == "suppressed_duplicate"
        assert duplicate_record["replay_suppression_basis"] == "sequence_id"

        recent_records = event_store.fetch_recent(limit=10)
        assert len(recent_records) == 1
        assert recent_records[0]["sequence_id"] == "exec-seq-duplicate-0001"

    def test_record_broker_lifecycle_event_auto_resolves_externally_terminal_reject_when_sequence_identity_is_explicit(
        self,
        tmp_path,
    ):
        try:
            correlation_module = importlib.import_module("src.application.trading.broker_order_correlation")
            event_module = importlib.import_module("src.application.trading.broker_lifecycle_event")
            divergence_module = importlib.import_module("src.application.trading.broker_divergence")
        except ModuleNotFoundError as exc:
            pytest.fail(f"broker auto-resolution dependency missing: {exc}")

        order_repo = self.InMemoryOrderRepository()
        correlation_db = tmp_path / "auto-resolve-reject-correlation.sqlite3"
        event_db = tmp_path / "auto-resolve-reject-event-ledger.sqlite3"
        divergence_db = tmp_path / "auto-resolve-reject-divergence-ledger.sqlite3"
        order_state_db = tmp_path / "auto-resolve-reject-order-state.sqlite3"
        correlation_store = correlation_module.SqliteTradingBrokerOrderCorrelationStore(correlation_db)
        event_store = event_module.SqliteTradingBrokerLifecycleEventStore(event_db)
        divergence_store = divergence_module.SqliteTradingBrokerDivergenceStore(divergence_db)
        order_state_store = SqliteTradingOrderStateStore(order_state_db)

        service = OrderManagementService(
            order_repo=order_repo,
            broker_correlation_store=correlation_store,
            broker_lifecycle_event_store=event_store,
            broker_divergence_store=divergence_store,
            order_state_store=order_state_store,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=100,
                side="BUY",
                order_type="LIMIT",
                price=10.5,
                idempotency_key="auto-resolve-reject-0001",
            )
        )
        service.record_broker_acknowledgement(
            response.order_id,
            external_order_id="broker-order-auto-resolve-reject-0001",
        )

        persisted_record = service.record_broker_lifecycle_event(
            event_module.BrokerLifecycleEvent(
                event_type="reject",
                external_order_id="broker-order-auto-resolve-reject-0001",
                source_timestamp=datetime(2026, 4, 28, 4, 40, tzinfo=timezone.utc),
                source_name="sim-broker",
                sequence_id="reject-seq-auto-resolve-0001",
                reason_code="broker_rejected",
                reason_detail="broker rejected after local submit",
            )
        )

        assert persisted_record["replay_suppression_status"] == "eligible"
        assert persisted_record["replay_suppression_basis"] == "sequence_id"

        divergence_record = divergence_store.fetch_recent(limit=1)[0]
        assert divergence_record["divergence_category"] == "externally_terminal_locally_open"
        assert divergence_record["review_status"] == "auto_resolved"
        assert divergence_record["auto_resolution_status"] == "applied"
        assert divergence_record["auto_resolution_basis"] == "matched_external_order_id+sequence_id"
        assert divergence_record["resolved_local_status"] == "REJECTED"

        order_state_record = order_state_store.get_order_state(response.order_id)
        assert order_state_record is not None
        assert order_state_record["status"] == "REJECTED"

        resolved_order = order_repo.get_by_id(OrderId(response.order_id))
        assert resolved_order.status == OrderStatus.REJECTED

    def test_place_order_and_execution_report_persist_order_state_evidence(self, tmp_path):
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=10000.0)
        portfolio_repo = MagicMock()
        portfolio_repo.get_by_id.return_value = portfolio
        order_repo = self.InMemoryOrderRepository()
        reservation_db = tmp_path / "order-state-reservations.sqlite3"
        order_state_db = tmp_path / "order-state-evidence.sqlite3"
        reservation_store = SqlitePortfolioCashReservationStore(reservation_db)
        order_state_store = SqliteTradingOrderStateStore(order_state_db)

        service = OrderManagementService(
            order_repo=order_repo,
            cash_reservation_store=reservation_store,
            order_state_store=order_state_store,
        )
        service.pre_submit_gate = build_portfolio_pre_submit_gate(
            portfolio_repo,
            max_single_symbol_weight=1.0,
            pending_buy_notional_getter=service.get_pending_buy_notional_for_portfolio,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=200,
                side="BUY",
                order_type="LIMIT",
                price=10.0,
                portfolio_id=portfolio.id,
                idempotency_key="order-state-0001",
            )
        )

        submitted_record = order_state_store.get_order_state(response.order_id)
        assert submitted_record is not None
        assert submitted_record["portfolio_id"] == portfolio.id
        assert submitted_record["status"] == "SUBMITTED"

        service.handle_execution_report(response.order_id, filled_qty=200, price=10.0)

        filled_record = order_state_store.get_order_state(response.order_id)
        assert filled_record is not None
        assert filled_record["portfolio_id"] == portfolio.id
        assert filled_record["status"] == "FILLED"

    def test_cancel_order_releases_reservation_and_persists_cancelled_state(self, tmp_path):
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=10000.0)
        portfolio_repo = MagicMock()
        portfolio_repo.get_by_id.return_value = portfolio
        order_repo = self.InMemoryOrderRepository()
        reservation_db = tmp_path / "cancel-order-reservations.sqlite3"
        order_state_db = tmp_path / "cancel-order-state.sqlite3"
        reservation_store = SqlitePortfolioCashReservationStore(reservation_db)
        order_state_store = SqliteTradingOrderStateStore(order_state_db)
        audit_sink = MagicMock()

        service = OrderManagementService(
            order_repo=order_repo,
            decision_audit_sink=audit_sink,
            cash_reservation_store=reservation_store,
            order_state_store=order_state_store,
        )
        service.pre_submit_gate = build_portfolio_pre_submit_gate(
            portfolio_repo,
            max_single_symbol_weight=1.0,
            pending_buy_notional_getter=service.get_pending_buy_notional_for_portfolio,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=200,
                side="BUY",
                order_type="LIMIT",
                price=10.0,
                portfolio_id=portfolio.id,
                idempotency_key="cancel-order-0001",
                actor_id="ops-user",
                source_id="unit-test",
            )
        )

        cancel_response = service.cancel_order(
            response.order_id,
            reason="operator_cancelled_stale_submission",
            actor_id="ops-user",
            source_id="unit-test",
        )

        assert cancel_response.status == OrderStatus.CANCELLED.value
        assert reservation_store.get_order_reservation(response.order_id) is None

        cancelled_record = order_state_store.get_order_state(response.order_id)
        assert cancelled_record is not None
        assert cancelled_record["portfolio_id"] == portfolio.id
        assert cancelled_record["status"] == "CANCELLED"

        assert audit_sink.call_args_list[-1].args[0]["decision_outcome"] == "cancelled"
        assert audit_sink.call_args_list[-1].args[0]["decision_reason"] == "operator_cancelled_stale_submission"
        assert audit_sink.call_args_list[-1].args[0]["actor_id"] == "ops-user"
        assert audit_sink.call_args_list[-1].args[0]["order_id"] == response.order_id

    def test_reject_order_releases_reservation_and_persists_rejected_state(self, tmp_path):
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=10000.0)
        portfolio_repo = MagicMock()
        portfolio_repo.get_by_id.return_value = portfolio
        order_repo = self.InMemoryOrderRepository()
        reservation_db = tmp_path / "reject-order-reservations.sqlite3"
        order_state_db = tmp_path / "reject-order-state.sqlite3"
        reservation_store = SqlitePortfolioCashReservationStore(reservation_db)
        order_state_store = SqliteTradingOrderStateStore(order_state_db)
        audit_sink = MagicMock()

        service = OrderManagementService(
            order_repo=order_repo,
            decision_audit_sink=audit_sink,
            cash_reservation_store=reservation_store,
            order_state_store=order_state_store,
        )
        service.pre_submit_gate = build_portfolio_pre_submit_gate(
            portfolio_repo,
            max_single_symbol_weight=1.0,
            pending_buy_notional_getter=service.get_pending_buy_notional_for_portfolio,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=200,
                side="BUY",
                order_type="LIMIT",
                price=10.0,
                portfolio_id=portfolio.id,
                idempotency_key="reject-order-0001",
                actor_id="risk-user",
                source_id="unit-test",
            )
        )

        reject_response = service.reject_order(
            response.order_id,
            reason="broker_rejected_submission",
            actor_id="risk-user",
            source_id="unit-test",
        )

        assert reject_response.status == OrderStatus.REJECTED.value
        assert reservation_store.get_order_reservation(response.order_id) is None

        rejected_record = order_state_store.get_order_state(response.order_id)
        assert rejected_record is not None
        assert rejected_record["portfolio_id"] == portfolio.id
        assert rejected_record["status"] == "REJECTED"

        assert audit_sink.call_args_list[-1].args[0]["decision_outcome"] == "rejected_after_submission"
        assert audit_sink.call_args_list[-1].args[0]["decision_reason"] == "broker_rejected_submission"
        assert audit_sink.call_args_list[-1].args[0]["actor_id"] == "risk-user"
        assert audit_sink.call_args_list[-1].args[0]["order_id"] == response.order_id

    def test_cancel_order_audits_not_found_lifecycle_attempt(self):
        order_repo = self.InMemoryOrderRepository()
        audit_sink = MagicMock()
        service = OrderManagementService(order_repo=order_repo, decision_audit_sink=audit_sink)

        with pytest.raises(ValueError, match="Order not found: missing-order-0001"):
            service.cancel_order(
                "missing-order-0001",
                reason="operator_cancel_missing_order",
                actor_id="ops-user",
                source_id="unit-test",
            )

        assert [call.args[0]["decision_outcome"] for call in audit_sink.call_args_list] == ["cancel_not_found"]
        assert audit_sink.call_args_list[-1].args[0]["decision_reason"] == "order_not_found"
        assert audit_sink.call_args_list[-1].args[0]["decision_reason_detail"] == "Order not found: missing-order-0001"
        assert audit_sink.call_args_list[-1].args[0]["request_identity"] == "missing-order-0001"
        assert audit_sink.call_args_list[-1].args[0]["order_id"] == "missing-order-0001"
        assert audit_sink.call_args_list[-1].args[0]["requested_reason"] == "operator_cancel_missing_order"

    def test_reject_order_audits_not_found_lifecycle_attempt(self):
        order_repo = self.InMemoryOrderRepository()
        audit_sink = MagicMock()
        service = OrderManagementService(order_repo=order_repo, decision_audit_sink=audit_sink)

        with pytest.raises(ValueError, match="Order not found: missing-order-0002"):
            service.reject_order(
                "missing-order-0002",
                reason="risk_reject_missing_order",
                actor_id="risk-user",
                source_id="unit-test",
            )

        assert [call.args[0]["decision_outcome"] for call in audit_sink.call_args_list] == ["reject_not_found"]
        assert audit_sink.call_args_list[-1].args[0]["decision_reason"] == "order_not_found"
        assert audit_sink.call_args_list[-1].args[0]["decision_reason_detail"] == "Order not found: missing-order-0002"
        assert audit_sink.call_args_list[-1].args[0]["request_identity"] == "missing-order-0002"
        assert audit_sink.call_args_list[-1].args[0]["order_id"] == "missing-order-0002"
        assert audit_sink.call_args_list[-1].args[0]["requested_reason"] == "risk_reject_missing_order"

    def test_reject_order_disallows_partial_fill_transition_and_preserves_local_state(self, tmp_path):
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=10000.0)
        portfolio_repo = MagicMock()
        portfolio_repo.get_by_id.return_value = portfolio
        order_repo = self.InMemoryOrderRepository()
        reservation_db = tmp_path / "reject-partial-fill-reservations.sqlite3"
        order_state_db = tmp_path / "reject-partial-fill-state.sqlite3"
        reservation_store = SqlitePortfolioCashReservationStore(reservation_db)
        order_state_store = SqliteTradingOrderStateStore(order_state_db)
        audit_sink = MagicMock()

        service = OrderManagementService(
            order_repo=order_repo,
            decision_audit_sink=audit_sink,
            cash_reservation_store=reservation_store,
            order_state_store=order_state_store,
        )
        service.pre_submit_gate = build_portfolio_pre_submit_gate(
            portfolio_repo,
            max_single_symbol_weight=1.0,
            pending_buy_notional_getter=service.get_pending_buy_notional_for_portfolio,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=200,
                side="BUY",
                order_type="LIMIT",
                price=10.0,
                portfolio_id=portfolio.id,
                idempotency_key="reject-partial-fill-0001",
                actor_id="risk-user",
                source_id="unit-test",
            )
        )

        partial_fill_response = service.handle_execution_report(response.order_id, filled_qty=100, price=10.0)
        assert partial_fill_response.status == OrderStatus.PARTIALLY_FILLED.value
        assert reservation_store.get_order_reservation(response.order_id)["reserved_notional"] == 1000.0

        with pytest.raises(RuntimeError, match="Cannot reject order in status"):
            service.reject_order(
                response.order_id,
                reason="invalid_reject_after_partial_fill",
                actor_id="risk-user",
                source_id="unit-test",
            )

        preserved_record = order_state_store.get_order_state(response.order_id)
        assert preserved_record is not None
        assert preserved_record["status"] == "PARTIALLY_FILLED"
        assert reservation_store.get_order_reservation(response.order_id)["reserved_notional"] == 1000.0
        assert [call.args[0]["decision_outcome"] for call in audit_sink.call_args_list] == ["submitted", "reject_denied"]
        assert audit_sink.call_args_list[-1].args[0]["decision_reason"] == "invalid_order_status_transition"
        assert audit_sink.call_args_list[-1].args[0]["decision_reason_detail"] == "Cannot reject order in status OrderStatus.PARTIALLY_FILLED"
        assert audit_sink.call_args_list[-1].args[0]["requested_reason"] == "invalid_reject_after_partial_fill"
        assert audit_sink.call_args_list[-1].args[0]["current_order_status"] == "PARTIALLY_FILLED"

    def test_reject_order_disallows_reject_after_cancelled_terminal_state(self, tmp_path):
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=10000.0)
        portfolio_repo = MagicMock()
        portfolio_repo.get_by_id.return_value = portfolio
        order_repo = self.InMemoryOrderRepository()
        reservation_db = tmp_path / "reject-after-cancel-reservations.sqlite3"
        order_state_db = tmp_path / "reject-after-cancel-state.sqlite3"
        reservation_store = SqlitePortfolioCashReservationStore(reservation_db)
        order_state_store = SqliteTradingOrderStateStore(order_state_db)
        audit_sink = MagicMock()

        service = OrderManagementService(
            order_repo=order_repo,
            decision_audit_sink=audit_sink,
            cash_reservation_store=reservation_store,
            order_state_store=order_state_store,
        )
        service.pre_submit_gate = build_portfolio_pre_submit_gate(
            portfolio_repo,
            max_single_symbol_weight=1.0,
            pending_buy_notional_getter=service.get_pending_buy_notional_for_portfolio,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=200,
                side="BUY",
                order_type="LIMIT",
                price=10.0,
                portfolio_id=portfolio.id,
                idempotency_key="reject-after-cancel-0001",
                actor_id="ops-user",
                source_id="unit-test",
            )
        )

        service.cancel_order(
            response.order_id,
            reason="operator_cancelled_submission",
            actor_id="ops-user",
            source_id="unit-test",
        )

        with pytest.raises(RuntimeError, match="Cannot reject order in status"):
            service.reject_order(
                response.order_id,
                reason="invalid_reject_after_cancel",
                actor_id="risk-user",
                source_id="unit-test",
            )

        preserved_record = order_state_store.get_order_state(response.order_id)
        assert preserved_record is not None
        assert preserved_record["status"] == "CANCELLED"
        assert reservation_store.get_order_reservation(response.order_id) is None
        assert [call.args[0]["decision_outcome"] for call in audit_sink.call_args_list] == [
            "submitted",
            "cancelled",
            "reject_denied",
        ]
        assert audit_sink.call_args_list[-1].args[0]["decision_reason"] == "invalid_order_status_transition"
        assert audit_sink.call_args_list[-1].args[0]["decision_reason_detail"] == "Cannot reject order in status OrderStatus.CANCELLED"
        assert audit_sink.call_args_list[-1].args[0]["requested_reason"] == "invalid_reject_after_cancel"
        assert audit_sink.call_args_list[-1].args[0]["current_order_status"] == "CANCELLED"

    def test_cancel_order_audits_denied_lifecycle_attempt_after_filled_state(self, tmp_path):
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=10000.0)
        portfolio_repo = MagicMock()
        portfolio_repo.get_by_id.return_value = portfolio
        order_repo = self.InMemoryOrderRepository()
        reservation_db = tmp_path / "cancel-after-filled-reservations.sqlite3"
        order_state_db = tmp_path / "cancel-after-filled-state.sqlite3"
        reservation_store = SqlitePortfolioCashReservationStore(reservation_db)
        order_state_store = SqliteTradingOrderStateStore(order_state_db)
        audit_sink = MagicMock()

        service = OrderManagementService(
            order_repo=order_repo,
            decision_audit_sink=audit_sink,
            cash_reservation_store=reservation_store,
            order_state_store=order_state_store,
        )
        service.pre_submit_gate = build_portfolio_pre_submit_gate(
            portfolio_repo,
            max_single_symbol_weight=1.0,
            pending_buy_notional_getter=service.get_pending_buy_notional_for_portfolio,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=200,
                side="BUY",
                order_type="LIMIT",
                price=10.0,
                portfolio_id=portfolio.id,
                idempotency_key="cancel-after-filled-0001",
                actor_id="ops-user",
                source_id="unit-test",
            )
        )

        filled_response = service.handle_execution_report(response.order_id, filled_qty=200, price=10.0)
        assert filled_response.status == OrderStatus.FILLED.value

        with pytest.raises(RuntimeError, match="Cannot cancel order in status"):
            service.cancel_order(
                response.order_id,
                reason="invalid_cancel_after_fill",
                actor_id="ops-user",
                source_id="unit-test",
            )

        preserved_record = order_state_store.get_order_state(response.order_id)
        assert preserved_record is not None
        assert preserved_record["status"] == "FILLED"
        assert reservation_store.get_order_reservation(response.order_id) is None
        assert [call.args[0]["decision_outcome"] for call in audit_sink.call_args_list] == ["submitted", "cancel_denied"]
        assert audit_sink.call_args_list[-1].args[0]["decision_reason"] == "invalid_order_status_transition"
        assert audit_sink.call_args_list[-1].args[0]["decision_reason_detail"] == "Cannot cancel order in status OrderStatus.FILLED"
        assert audit_sink.call_args_list[-1].args[0]["requested_reason"] == "invalid_cancel_after_fill"
        assert audit_sink.call_args_list[-1].args[0]["current_order_status"] == "FILLED"

    def test_place_order_blocks_when_stale_pending_buy_reservations_require_review(self, tmp_path):
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=10000.0)
        portfolio_repo = MagicMock()
        portfolio_repo.get_by_id.return_value = portfolio
        order_repo = self.InMemoryOrderRepository()
        reservation_db = tmp_path / "stale-trading-cash-reservations.sqlite3"
        store = SqlitePortfolioCashReservationStore(reservation_db)
        stale_updated_at = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        store.upsert(
            portfolio.id,
            "stale-order-0001",
            1000.0,
            updated_at=stale_updated_at,
        )

        service = OrderManagementService(order_repo=order_repo, cash_reservation_store=store)
        service.pre_submit_gate = build_portfolio_pre_submit_gate(
            portfolio_repo,
            max_single_symbol_weight=1.0,
            pending_buy_notional_getter=service.get_pending_buy_notional_for_portfolio,
            stale_buy_reservation_checker=lambda portfolio_id: service.has_stale_cash_reservations_for_portfolio(
                portfolio_id,
                max_age_seconds=86400,
            ),
        )

        with pytest.raises(PermissionError, match="stale_pending_buy_reservations_require_review"):
            service.place_order(
                CreateOrderRequest(
                    symbol="000002",
                    quantity=100,
                    side="BUY",
                    order_type="LIMIT",
                    price=10.0,
                    portfolio_id=portfolio.id,
                    idempotency_key="stale-cash-0001",
                )
            )

    def test_handle_execution_report(self):
        # Setup mocks
        mock_repo = MagicMock()

        # 构造一个真实的 Order 对象而不是 MagicMock，以满足 Pydantic 校验
        # 因为 Pydantic 期待属性是字符串/枚举/日期等，而不是 Mock 对象
        from src.domain.trading.model.order import Order
        from src.domain.trading.value_objects import OrderType

        order = Order.create(symbol="000001", quantity=100, side=OrderSide.BUY, order_type=OrderType.LIMIT, price=10.0)
        order.submit()

        mock_repo.get_by_id.return_value = order
        service = OrderManagementService(order_repo=mock_repo)

        # Execute
        response = service.handle_execution_report(order.id.value, 100, 10.6)

        # Verify
        assert order.status == OrderStatus.FILLED
        assert order.filled_quantity == 100
        assert mock_repo.save.called
        assert response.status == OrderStatus.FILLED.value
        assert response.symbol == "000001"

    def test_handle_execution_report_audits_missing_order_attempt(self):
        order_repo = self.InMemoryOrderRepository()
        audit_sink = MagicMock()
        service = OrderManagementService(order_repo=order_repo, decision_audit_sink=audit_sink)

        with pytest.raises(ValueError, match="Order not found: missing-order-report-0001"):
            service.handle_execution_report("missing-order-report-0001", 100, 10.6)

        assert [call.args[0]["decision_outcome"] for call in audit_sink.call_args_list] == ["execution_report_not_found"]
        assert audit_sink.call_args_list[-1].args[0]["decision_reason"] == "order_not_found"
        assert (
            audit_sink.call_args_list[-1].args[0]["decision_reason_detail"]
            == "Order not found: missing-order-report-0001"
        )
        assert audit_sink.call_args_list[-1].args[0]["request_identity"] == "missing-order-report-0001"
        assert audit_sink.call_args_list[-1].args[0]["order_id"] == "missing-order-report-0001"
        assert audit_sink.call_args_list[-1].args[0]["reported_filled_quantity"] == 100
        assert audit_sink.call_args_list[-1].args[0]["reported_fill_price"] == 10.6

    def test_handle_execution_report_audits_denied_fill_after_cancelled_terminal_state(self, tmp_path):
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=10000.0)
        portfolio_repo = MagicMock()
        portfolio_repo.get_by_id.return_value = portfolio
        order_repo = self.InMemoryOrderRepository()
        reservation_db = tmp_path / "fill-after-cancelled-terminal-reservations.sqlite3"
        order_state_db = tmp_path / "fill-after-cancelled-terminal-state.sqlite3"
        reservation_store = SqlitePortfolioCashReservationStore(reservation_db)
        order_state_store = SqliteTradingOrderStateStore(order_state_db)
        audit_sink = MagicMock()

        service = OrderManagementService(
            order_repo=order_repo,
            decision_audit_sink=audit_sink,
            cash_reservation_store=reservation_store,
            order_state_store=order_state_store,
        )
        service.pre_submit_gate = build_portfolio_pre_submit_gate(
            portfolio_repo,
            max_single_symbol_weight=1.0,
            pending_buy_notional_getter=service.get_pending_buy_notional_for_portfolio,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=200,
                side="BUY",
                order_type="LIMIT",
                price=10.0,
                portfolio_id=portfolio.id,
                idempotency_key="fill-after-cancelled-terminal-0001",
                actor_id="ops-user",
                source_id="unit-test",
            )
        )

        cancelled_response = service.cancel_order(
            response.order_id,
            reason="operator_cancelled_submission",
            actor_id="ops-user",
            source_id="unit-test",
        )
        assert cancelled_response.status == OrderStatus.CANCELLED.value

        with pytest.raises(RuntimeError, match="Cannot fill order in status"):
            service.handle_execution_report(response.order_id, filled_qty=50, price=10.0)

        preserved_record = order_state_store.get_order_state(response.order_id)
        assert preserved_record is not None
        assert preserved_record["status"] == "CANCELLED"
        assert reservation_store.get_order_reservation(response.order_id) is None
        assert [call.args[0]["decision_outcome"] for call in audit_sink.call_args_list] == [
            "submitted",
            "cancelled",
            "execution_report_denied",
        ]
        assert audit_sink.call_args_list[-1].args[0]["decision_reason"] == "invalid_order_status_transition"
        assert audit_sink.call_args_list[-1].args[0]["decision_reason_detail"] == "Cannot fill order in status OrderStatus.CANCELLED"
        assert audit_sink.call_args_list[-1].args[0]["current_order_status"] == "CANCELLED"
        assert audit_sink.call_args_list[-1].args[0]["reported_filled_quantity"] == 50
        assert audit_sink.call_args_list[-1].args[0]["reported_fill_price"] == 10.0

    def test_handle_execution_report_audits_denied_overfill_attempt_and_preserves_partial_state(self, tmp_path):
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=10000.0)
        portfolio_repo = MagicMock()
        portfolio_repo.get_by_id.return_value = portfolio
        order_repo = self.InMemoryOrderRepository()
        reservation_db = tmp_path / "overfill-execution-report-reservations.sqlite3"
        order_state_db = tmp_path / "overfill-execution-report-state.sqlite3"
        reservation_store = SqlitePortfolioCashReservationStore(reservation_db)
        order_state_store = SqliteTradingOrderStateStore(order_state_db)
        audit_sink = MagicMock()

        service = OrderManagementService(
            order_repo=order_repo,
            decision_audit_sink=audit_sink,
            cash_reservation_store=reservation_store,
            order_state_store=order_state_store,
        )
        service.pre_submit_gate = build_portfolio_pre_submit_gate(
            portfolio_repo,
            max_single_symbol_weight=1.0,
            pending_buy_notional_getter=service.get_pending_buy_notional_for_portfolio,
        )

        response = service.place_order(
            CreateOrderRequest(
                symbol="000001",
                quantity=200,
                side="BUY",
                order_type="LIMIT",
                price=10.0,
                portfolio_id=portfolio.id,
                idempotency_key="overfill-execution-report-0001",
                actor_id="broker-feed",
                source_id="unit-test",
            )
        )

        partial_fill_response = service.handle_execution_report(response.order_id, filled_qty=100, price=10.0)
        assert partial_fill_response.status == OrderStatus.PARTIALLY_FILLED.value
        assert reservation_store.get_order_reservation(response.order_id)["reserved_notional"] == 1000.0

        with pytest.raises(ValueError, match="Fill quantity exceeds remaining quantity"):
            service.handle_execution_report(response.order_id, filled_qty=150, price=10.0)

        preserved_record = order_state_store.get_order_state(response.order_id)
        assert preserved_record is not None
        assert preserved_record["status"] == "PARTIALLY_FILLED"
        assert reservation_store.get_order_reservation(response.order_id)["reserved_notional"] == 1000.0
        assert [call.args[0]["decision_outcome"] for call in audit_sink.call_args_list] == [
            "submitted",
            "execution_report_denied",
        ]
        assert audit_sink.call_args_list[-1].args[0]["decision_reason"] == "fill_quantity_exceeds_remaining_quantity"
        assert audit_sink.call_args_list[-1].args[0]["decision_reason_detail"] == "Fill quantity exceeds remaining quantity"
        assert audit_sink.call_args_list[-1].args[0]["current_order_status"] == "PARTIALLY_FILLED"
        assert audit_sink.call_args_list[-1].args[0]["reported_filled_quantity"] == 150
        assert audit_sink.call_args_list[-1].args[0]["reported_fill_price"] == 10.0

    @pytest.mark.asyncio
    async def test_stop_loss_execution_uses_portfolio_aware_sell_request(self):
        order_service = MagicMock()
        order_service.place_order.return_value = MagicMock(order_id="order-stop-loss-0001")
        service = StopLossExecutionService(order_service)

        position = StopLossPosition(
            symbol="000001",
            position_id="position-0001",
            portfolio_id="portfolio-0001",
            entry_price=10.0,
            current_quantity=100,
            stop_loss_price=9.5,
            stop_loss_type="volatility_adaptive",
        )

        result = await service._execute_stop_loss_order(position, current_price=9.4)

        assert result["success"] is True
        order_request = order_service.place_order.call_args.args[0]
        assert order_request.portfolio_id == "portfolio-0001"
        assert order_request.side == "SELL"
        assert order_request.order_type == "MARKET"


if __name__ == "__main__":
    pytest.main([__file__])
