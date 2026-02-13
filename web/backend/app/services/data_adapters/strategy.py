"""
策略管理数据源适配器
"""
import time
import logging
from datetime import datetime
from typing import Any, Dict

from app.services.data_source_interface import (
    HealthStatus,
    HealthStatusEnum,
    IDataSource,
)
from .base import DataSourceMetrics

logger = logging.getLogger(__name__)

class StrategyDataSourceAdapter(IDataSource):
    """策略管理数据源适配器 - 集成现有策略服务到数据源工厂模式"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_type = "strategy"
        self.name = config.get("name", "Strategy Management Source")

        # Initialize services lazily (only when needed)
        self._strategy_service = None
        self._mock_manager = None

        self.metrics = DataSourceMetrics()
        self._cache = {}
        self._cache_ttl = config.get("cache_ttl", 300)  # 5分钟缓存

    def _get_strategy_service(self):
        """Lazy initialization of strategy service"""
        if self._strategy_service is None:
            try:
                from app.services.strategy_service import get_strategy_service

                self._strategy_service = get_strategy_service()
            except Exception as e:
                self._strategy_service = None
                raise RuntimeError(f"Failed to initialize strategy service: {e}")
        return self._strategy_service

    def _get_mock_manager(self):
        """Lazy initialization of mock data manager"""
        if self._mock_manager is None:
            try:
                from app.mock.unified_mock_data import get_mock_data_manager

                self._mock_manager = get_mock_data_manager()
            except Exception as e:
                self._mock_manager = None
                raise RuntimeError(f"Failed to initialize mock data manager: {e}")
        return self._mock_manager

    async def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """获取策略管理数据"""
        start_time = time.time()
        params = params or {}

        try:
            # 检查缓存
            cache_key = f"{endpoint}:{hash(str(sorted(params.items())))}"
            if cache_key in self._cache:
                cached_item = self._cache[cache_key]
                if time.time() - cached_item["timestamp"] < self._cache_ttl:
                    self.metrics.record_success(time.time() - start_time)
                    return cached_item["data"]
                else:
                    del self._cache[cache_key]

            # 获取数据
            data = await self._fetch_strategy_data(endpoint, params)

            # 缓存结果
            self._cache[cache_key] = {"data": data, "timestamp": time.time()}

            self.metrics.record_success(time.time() - start_time)
            return data

        except Exception as e:
            self.metrics.record_error(time.time() - start_time, str(e))
            logger.error(f"Strategy data fetch error: {e}")
            raise

    async def _fetch_strategy_data(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """从策略服务获取数据"""
        try:
            service_available = self._get_strategy_service() is not None
        except Exception:
            service_available = False

        if not service_available and self._get_mock_manager():
            # 使用Mock数据
            return self._get_mock_strategy_data(endpoint, params)

        try:
            # 解析endpoint路径
            path_parts = endpoint.strip("/").split("/")

            if endpoint == "definitions" or endpoint == "/definitions":
                # 获取策略定义列表
                definitions = self._get_strategy_service().get_strategy_definitions()
                return {
                    "success": True,
                    "data": definitions,
                    "total": len(definitions),
                    "message": "获取策略定义成功",
                }

            elif endpoint.startswith("run/"):
                # 策略执行相关
                if len(path_parts) >= 3 and path_parts[1] == "single":
                    # 单股策略执行 run/single/{strategy_code}/{symbol}
                    strategy_code = path_parts[2] if len(path_parts) > 2 else params.get("strategy_code")
                    symbol = path_parts[3] if len(path_parts) > 3 else params.get("symbol")

                    if strategy_code and symbol:
                        result = self._get_strategy_service().run_strategy_for_stock(
                            strategy_code=strategy_code,
                            symbol=symbol,
                            stock_name=params.get("stock_name"),
                            check_date=params.get("check_date"),
                        )
                        return result

                elif len(path_parts) >= 3 and path_parts[1] == "batch":
                    # 批量策略执行 run/batch/{strategy_code}
                    strategy_code = path_parts[2]
                    symbols = params.get("symbols", [])

                    if strategy_code and symbols:
                        results = []
                        for symbol in symbols:
                            try:
                                result = self._get_strategy_service().run_strategy_for_stock(
                                    strategy_code=strategy_code, symbol=symbol
                                )
                                results.append({"symbol": symbol, "success": True, "data": result})
                            except Exception as e:
                                results.append(
                                    {
                                        "symbol": symbol,
                                        "success": False,
                                        "error": str(e),
                                    }
                                )

                        return {
                            "success": True,
                            "strategy_code": strategy_code,
                            "total_symbols": len(symbols),
                            "results": results,
                            "message": (
                                f"批量策略执行完成: {len([r for r in results if r['success']])}/{len(symbols)} 成功"
                            ),
                        }

            elif endpoint.startswith("results/"):
                # 策略结果查询
                if len(path_parts) >= 3:
                    strategy_code = path_parts[2]
                    symbol = params.get("symbol")
                    limit = params.get("limit", 50)

                    results = self._get_strategy_service().get_strategy_results(
                        strategy_code=strategy_code, symbol=symbol, limit=limit
                    )
                    return {
                        "success": True,
                        "strategy_code": strategy_code,
                        "data": results,
                        "total": len(results),
                        "message": "获取策略结果成功",
                    }

            # 如果没有匹配的endpoint，返回默认数据
            return self._get_mock_strategy_data(endpoint, params)

        except Exception as e:
            logger.error(f"Strategy service error: {e}")
            # 降级到Mock数据
            if self._get_mock_manager():
                return self._get_mock_strategy_data(endpoint, params)
            raise

    def _get_mock_strategy_data(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """获取Mock策略数据"""
        mock_manager = self._get_mock_manager()
        if not mock_manager:
            return {"success": False, "error": "No mock data available"}

        try:
            # 生成Mock策略定义
            if endpoint == "definitions" or endpoint == "/definitions":
                definitions = [
                    {
                        "code": "volume_surge",
                        "name": "成交量突增策略",
                        "description": "检测成交量异常放大",
                        "category": "技术指标",
                        "risk_level": "中等",
                    },
                    {
                        "code": "price_breakout",
                        "name": "价格突破策略",
                        "description": "检测价格关键位突破",
                        "category": "技术指标",
                        "risk_level": "高",
                    },
                    {
                        "code": "rsi_oversold",
                        "name": "RSI超卖反弹策略",
                        "description": "RSI超卖区域的反弹机会",
                        "category": "技术指标",
                        "risk_level": "中等",
                    },
                    {
                        "code": "ma_golden_cross",
                        "name": "均线金叉策略",
                        "description": "短期均线上穿长期均线",
                        "category": "技术指标",
                        "risk_level": "低",
                    },
                ]

                return {
                    "success": True,
                    "data": definitions,
                    "total": len(definitions),
                    "message": "获取策略定义成功",
                }

            # Mock策略执行结果
            elif endpoint.startswith("run/"):
                strategy_code = params.get("strategy_code", "volume_surge")
                symbol = params.get("symbol", "000001")

                # 生成Mock执行结果
                import random

                base_price = random.uniform(10, 100)
                change_percent = random.uniform(-5, 10)
                volume_ratio = random.uniform(0.5, 5.0)

                mock_result = {
                    "success": True,
                    "strategy_code": strategy_code,
                    "symbol": symbol,
                    "check_date": params.get("check_date", "2025-12-01"),
                    "result": {
                        "signal": random.choice(["BUY", "SELL", "HOLD"]),
                        "confidence": random.uniform(0.6, 0.95),
                        "price": round(base_price, 2),
                        "change_percent": round(change_percent, 2),
                        "volume_ratio": round(volume_ratio, 2),
                        "indicators": {
                            "rsi": round(random.uniform(20, 80), 2),
                            "macd": round(random.uniform(-2, 2), 4),
                            "ma5": round(base_price * random.uniform(0.98, 1.02), 2),
                            "ma20": round(base_price * random.uniform(0.95, 1.05), 2),
                        },
                    },
                    "message": f"策略{strategy_code}对{symbol}执行完成",
                }

                return mock_result

            # Mock策略结果列表
            elif endpoint.startswith("results/"):
                strategy_code = params.get("strategy_code", "volume_surge")

                # 生成多个Mock结果
                mock_results = []
                symbols = ["000001", "000002", "600519", "600036", "000858"]

                for symbol in symbols:
                    mock_results.append(
                        {
                            "symbol": symbol,
                            "strategy_code": strategy_code,
                            "check_date": "2025-12-01",
                            "signal": random.choice(["BUY", "SELL", "HOLD"]),
                            "confidence": round(random.uniform(0.6, 0.95), 2),
                            "price": round(random.uniform(10, 200), 2),
                            "change_percent": round(random.uniform(-5, 10), 2),
                        }
                    )

                return {
                    "success": True,
                    "strategy_code": strategy_code,
                    "data": mock_results,
                    "total": len(mock_results),
                    "message": "获取策略结果成功",
                }

            # 默认Mock响应
            return {
                "success": True,
                "data": {},
                "message": f"Strategy mock data for {endpoint}",
            }

        except Exception as e:
            logger.error(f"Mock strategy data generation error: {e}")
            return {"success": False, "error": str(e)}

    async def health_check(self) -> HealthStatus:
        """健康检查"""
        try:
            start_time = time.time()

            # 检查策略服务可用性
            service_available = self._get_strategy_service() is not None
            mock_available = self._get_mock_manager() is not None

            # 基础健康检查
            basic_healthy = service_available or mock_available

            # 简单连接测试
            connection_test = False
            if basic_healthy:
                try:
                    # 尝试获取策略定义作为连接测试
                    if service_available:
                        self._get_strategy_service().get_strategy_definitions()
                    connection_test = True
                except Exception:
                    if mock_available:
                        connection_test = True

            status = HealthStatusEnum.HEALTHY if (basic_healthy and connection_test) else HealthStatusEnum.FAILED

            return HealthStatus(
                status=status,
                response_time=(time.time() - start_time) * 1000,
                message=f"Strategy data source is {status.value}",
                timestamp=datetime.now(),
            )

        except Exception as e:
            return HealthStatus(
                status=HealthStatusEnum.FAILED,
                response_time=0.0,
                message=f"Strategy health check failed: {str(e)}",
                timestamp=datetime.now(),
            )

    def get_metrics(self) -> DataSourceMetrics:
        """获取监控指标"""
        return self.metrics

    async def close(self):
        """关闭连接和清理资源"""
        pass
