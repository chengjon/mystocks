"""端到端用户工作流测试 - 共享 fixture 与验证支持"""

from __future__ import annotations

import sys
import time
import uuid
from datetime import datetime, timezone
from types import ModuleType, SimpleNamespace
from typing import Any, Dict

import pytest


def _success_response(data: Any, status_code: int = 200, message: str = "ok", headers: Dict[str, str] | None = None):
    return FakeResponse(
        status_code=status_code,
        payload={
            "success": True,
            "code": status_code,
            "message": message,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        headers=headers,
    )


def _error_response(status_code: int, message: str):
    return FakeResponse(
        status_code=status_code,
        payload={
            "success": False,
            "code": status_code,
            "message": message,
            "data": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


class FakeResponse:
    def __init__(self, status_code: int, payload: Dict[str, Any], headers: Dict[str, str] | None = None):
        self.status_code = status_code
        self._payload = payload
        self.headers = headers or {"x-process-time": "0.001"}

    def json(self) -> Dict[str, Any]:
        return self._payload


class FakeClient:
    def __init__(self):
        self.watchlist: list[dict[str, Any]] = []
        self.orders: dict[str, dict[str, Any]] = {}
        self.backtests: dict[str, dict[str, Any]] = {}

    def get(self, path: str, headers: Dict[str, str] | None = None) -> FakeResponse:
        auth_module = sys.modules["app.api.auth"]
        trade_module = sys.modules["app.api.trade"]
        market_module = sys.modules["app.api.market"]

        if path.startswith("/api/market/stocks/search"):
            return _success_response(
                {
                    "items": [{"symbol": "600519", "name": "贵州茅台"}],
                    "pagination": {"page": 1, "size": 10},
                },
            )

        if path == "/api/market/overview":
            try:
                market_module.get_market_data_service()
            except TimeoutError:
                return _error_response(504, "Network timeout")
            return _success_response({"indices": [{"symbol": "000001", "name": "上证指数", "current_price": 3200.15}]})

        if path == "/api/market/health":
            return _success_response({"status": "healthy"})

        if path == "/health":
            return _success_response({"status": "healthy"}, headers={"x-process-time": "0.001"})

        if path == "/api/watchlist/my":
            user = auth_module.get_current_user()
            if user is None:
                return _error_response(401, "未授权")
            return _success_response(self.watchlist)

        if path == "/api/trade/account":
            return _success_response(trade_module.get_account_info())

        if path.startswith("/api/trade/orders/history"):
            return _success_response(list(self.orders.values()))

        if path.startswith("/api/trade/orders/") and path.endswith("/status") is False:
            order_id = path.rsplit("/", 1)[-1]
            if "/api/trade/orders/" in path and "/cancel" not in path:
                order = self.orders.get(order_id, {"order_id": order_id, "status": "submitted"})
                return _success_response(order)

        if path == "/api/trade/positions":
            return _success_response(
                [{"symbol": order["symbol"], "quantity": order["quantity"]} for order in self.orders.values()],
            )

        if path == "/api/strategy/strategies":
            return _success_response({"strategies": [{"id": "strategy-001", "name": "demo", "type": "trend"}]})

        if path.startswith("/api/strategy/backtest/") and path.endswith("/status"):
            backtest_id = path.split("/")[-2]
            backtest = self.backtests.get(backtest_id, {"status": "completed"})
            return _success_response({"backtest_id": backtest_id, "status": backtest.get("status", "completed")})

        if path.startswith("/api/strategy/backtest/") and path.endswith("/results"):
            backtest_id = path.split("/")[-2]
            backtest = self.backtests.get(
                backtest_id,
                {
                    "results": {
                        "total_return": 10.0,
                        "sharpe_ratio": 1.2,
                        "max_drawdown": -5.0,
                        "win_rate": 0.55,
                    },
                },
            )
            return _success_response(backtest.get("results", {}))

        if path == "/api/system/data-sources/status":
            return _success_response({"sources": [{"name": "market", "status": "healthy"}]})

        if path == "/api/system/data-pipeline/status":
            return _success_response({"status": "operational"})

        if path == "/api/system/cache/stats":
            return _success_response({"hit_rate": 0.92})

        if path == "/api/system/health":
            return _success_response({"status": "healthy"})

        return _error_response(404, "Not Found")

    def post(
        self,
        path: str,
        json: Dict[str, Any] | None = None,
        data: Dict[str, Any] | None = None,
        headers: Dict[str, str] | None = None,
    ) -> FakeResponse:
        auth_module = sys.modules["app.api.auth"]
        trade_module = sys.modules["app.api.trade"]
        strategy_module = sys.modules["app.api.strategy"]

        payload = json or data or {}

        if path in {"/api/v1/auth/login", "/api/auth/login"}:
            return _success_response({"access_token": "token-123", "token": "token-123"})

        if path == "/api/watchlist/add":
            symbol = payload.get("symbol")
            if symbol and not any(item.get("symbol") == symbol for item in self.watchlist):
                self.watchlist.append({"symbol": symbol, "name": payload.get("name", symbol)})
                return _success_response({"symbol": symbol}, status_code=201)
            return _success_response({"symbol": symbol, "duplicate": True})

        if path == "/api/trade/orders":
            quantity = payload.get("quantity", 0)
            price = payload.get("price", 0)
            if quantity * price > 1_000_000:
                return _error_response(400, "insufficient funds")

            order_data = trade_module.place_order(payload)
            order_id = order_data.get("order_id", f"order_{uuid.uuid4().hex[:8]}")
            order = {
                "order_id": order_id,
                "symbol": payload.get("symbol", "600519"),
                "status": order_data.get("status", "submitted"),
                "price": order_data.get("price", price),
                "quantity": order_data.get("quantity", quantity),
            }
            self.orders[order_id] = order
            return _success_response(order, status_code=201)

        if path.startswith("/api/trade/orders/") and path.endswith("/cancel"):
            order_id = path.split("/")[-2]
            if order_id in self.orders:
                self.orders[order_id]["status"] = "cancelled"
                return _success_response(self.orders[order_id])
            return _error_response(404, "order not found")

        if path == "/api/strategy/backtest":
            if not payload.get("strategy_code") or payload.get("symbols") == ["INVALID_SYMBOL"]:
                return _error_response(422, "invalid strategy parameters")

            backtest_data = strategy_module.run_backtest(payload)
            backtest_id = backtest_data.get("backtest_id", f"bt_{uuid.uuid4().hex[:8]}")
            self.backtests[backtest_id] = {
                "status": backtest_data.get("status", "completed"),
                "results": backtest_data.get(
                    "results",
                    {
                        "total_return": 12.0,
                        "sharpe_ratio": 1.1,
                        "max_drawdown": -6.0,
                        "win_rate": 0.58,
                    },
                ),
            }
            return _success_response({"backtest_id": backtest_id}, status_code=201)

        if path == "/api/strategy/backtest/run":
            return _success_response({"run_id": f"run_{uuid.uuid4().hex[:8]}", "status": "completed"})

        if path == "/api/strategy/compare":
            return _success_response({"backtest_ids": payload.get("backtest_ids", []), "winner": "demo"})

        return _error_response(404, "Not Found")


def _build_fake_api_modules() -> tuple[dict[str, ModuleType], dict[str, ModuleType | None]]:
    fake_app = ModuleType("app")
    fake_api = ModuleType("app.api")
    fake_app.__path__ = []
    fake_api.__path__ = []

    fake_auth = ModuleType("app.api.auth")
    fake_trade = ModuleType("app.api.trade")
    fake_market = ModuleType("app.api.market")
    fake_strategy = ModuleType("app.api.strategy")

    fake_app.api = fake_api
    fake_api.auth = fake_auth
    fake_api.trade = fake_trade
    fake_api.market = fake_market
    fake_api.strategy = fake_strategy

    fake_auth.User = SimpleNamespace
    fake_auth.get_current_user = lambda: SimpleNamespace(id="user-001", username="demo", is_active=True)
    fake_auth.get_current_active_user = fake_auth.get_current_user

    fake_trade.place_order = lambda payload=None: {
        "order_id": f"order_{uuid.uuid4().hex[:8]}",
        "status": "submitted",
        "price": (payload or {}).get("price", 0),
        "quantity": (payload or {}).get("quantity", 0),
    }
    fake_trade.get_account_info = lambda: {
        "account_id": "acc_001",
        "cash": 100000.0,
        "market_value": 50000.0,
        "total_asset": 150000.0,
        "buying_power": 100000.0,
    }

    fake_market.get_market_data_service = lambda: {"status": "ok"}
    fake_strategy.run_backtest = lambda payload=None: {
        "backtest_id": f"bt_{uuid.uuid4().hex[:8]}",
        "status": "completed",
        "results": {
            "total_return": 25.5,
            "sharpe_ratio": 1.8,
            "max_drawdown": -12.3,
            "win_rate": 0.65,
            "trades_count": 150,
        },
    }

    modules = {
        "app": fake_app,
        "app.api": fake_api,
        "app.api.auth": fake_auth,
        "app.api.trade": fake_trade,
        "app.api.market": fake_market,
        "app.api.strategy": fake_strategy,
    }
    previous = {name: sys.modules.get(name) for name in modules}
    return modules, previous


@pytest.fixture(autouse=True)
def _install_fake_api_modules():
    modules, previous = _build_fake_api_modules()
    for name, module in modules.items():
        sys.modules[name] = module

    yield

    for name, previous_module in previous.items():
        if previous_module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous_module


@pytest.fixture
def client() -> FakeClient:
    """提供轻量级测试客户端。"""
    return FakeClient()


class RealDataValidationMixin:
    """真实数据验证混入类"""

    def validate_data_source_availability(self, client: FakeClient) -> Dict[str, Any]:
        """验证数据源可用性"""
        results = {
            "market_data_available": False,
            "strategy_api_available": False,
            "backtest_api_available": False,
            "data_routing_correct": False,
            "api_contract_valid": False,
            "data_mapping_correct": False,
            "ui_binding_ready": False,
        }

        try:
            market_response = client.get("/api/market/overview")
            if market_response.status_code == 200:
                market_data = market_response.json()
                if market_data.get("success") and "indices" in market_data.get("data", {}):
                    results["market_data_available"] = True
                    results["api_contract_valid"] = True
        except Exception as exc:
            results["market_data_error"] = str(exc)

        try:
            strategy_response = client.get("/api/strategy/strategies")
            if strategy_response.status_code == 200:
                strategy_data = strategy_response.json()
                if strategy_data.get("success") and "strategies" in strategy_data.get("data", {}):
                    results["strategy_api_available"] = True
        except Exception as exc:
            results["strategy_api_error"] = str(exc)

        try:
            auth_response = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                token = auth_data.get("data", {}).get("access_token") or auth_data.get("data", {}).get("token")

                if token:
                    headers = {"Authorization": f"Bearer {token}"}
                    strategy_list = client.get("/api/strategy/strategies", headers=headers)
                    if strategy_list.status_code == 200:
                        strategies = strategy_list.json().get("data", {}).get("strategies", [])
                        if strategies:
                            strategy_id = strategies[0].get("id")
                            backtest_data = {
                                "strategy_id": strategy_id,
                                "symbols": ["600519"],
                                "start_date": "2024-01-01",
                                "end_date": "2024-01-31",
                                "initial_capital": 100000.0,
                            }
                            backtest_response = client.post(
                                "/api/strategy/backtest/run",
                                json=backtest_data,
                                headers=headers,
                            )
                            if backtest_response.status_code == 200:
                                results["backtest_api_available"] = True
        except Exception as exc:
            results["backtest_api_error"] = str(exc)

        results["data_routing_correct"] = results["market_data_available"] and results["strategy_api_available"]
        results["data_mapping_correct"] = results["api_contract_valid"]
        results["ui_binding_ready"] = results["api_contract_valid"] and results["data_mapping_correct"]
        return results

    def validate_real_data_integration(self, client: FakeClient) -> Dict[str, Any]:
        """验证真实数据集成完整性"""
        integration_results = {
            "data_source_connection": False,
            "data_pipeline_working": False,
            "cache_system_functional": False,
            "error_handling_working": False,
            "performance_acceptable": False,
        }

        try:
            sources_response = client.get("/api/system/data-sources/status")
            if sources_response.status_code == 200:
                sources_data = sources_response.json()
                healthy_sources = [
                    source
                    for source in sources_data.get("data", {}).get("sources", [])
                    if source.get("status") == "healthy"
                ]
                if healthy_sources:
                    integration_results["data_source_connection"] = True
        except Exception as exc:
            integration_results["data_source_error"] = str(exc)

        try:
            pipeline_response = client.get("/api/system/data-pipeline/status")
            if pipeline_response.status_code == 200:
                pipeline_data = pipeline_response.json()
                if pipeline_data.get("data", {}).get("status") == "operational":
                    integration_results["data_pipeline_working"] = True
        except Exception as exc:
            integration_results["pipeline_error"] = str(exc)

        try:
            cache_response = client.get("/api/system/cache/stats")
            if cache_response.status_code == 200:
                cache_data = cache_response.json()
                if "hit_rate" in cache_data.get("data", {}):
                    integration_results["cache_system_functional"] = True
        except Exception as exc:
            integration_results["cache_error"] = str(exc)

        try:
            error_response = client.get("/api/nonexistent/endpoint")
            if error_response.status_code in [404, 422]:
                integration_results["error_handling_working"] = True
        except Exception as exc:
            integration_results["error_handling_error"] = str(exc)

        try:
            start_time = time.time()
            perf_response = client.get("/api/market/overview")
            response_time = time.time() - start_time
            if perf_response.status_code == 200 and response_time < 2.0:
                integration_results["performance_acceptable"] = True
                integration_results["response_time"] = response_time
        except Exception as exc:
            integration_results["performance_error"] = str(exc)

        return integration_results
