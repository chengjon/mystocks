"""
市场数据源适配器
将现有的 MarketDataService 集成到数据源工厂模式中
"""

import time
from datetime import datetime
from typing import Any, Dict, Optional

from app.services.data_quality_monitor import get_data_quality_monitor
from app.services.data_source_interface import (
    HealthStatus,
    HealthStatusEnum,
    IDataSource,
)

logger = __import__("logging").getLogger(__name__)


class DataSourceMetrics:
    """数据源监控指标"""

    def __init__(self):
        self.availability: float = 0.0  # 可用性百分比 (0-100)
        self.response_time: float = 0.0  # 平均响应时间 (ms)
        self.success_rate: float = 0.0  # 成功率百分比 (0-100)
        self.error_count: int = 0  # 错误次数
        self.last_error = None  # 最后错误信息
        self.last_check = None  # 最后检查时间
        self.total_requests: int = 0  # 总请求数
        self.data_delay = None  # 数据延迟 (秒)


class MarketDataSourceAdapter(IDataSource):
    """市场数据源适配器 - 集成现有 MarketDataService 到数据源工厂模式"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_type = "market"
        self.name = config.get("name", "Market Data Source")
        self.mode = config.get("mode", "mock")

        # Lazy initialization of services (only when needed)
        self._market_service = None
        self._mock_manager = None

        # 初始化缓存
        self.cache_enabled = config.get("cache_enabled", True)
        self.cache_ttl = config.get("cache_ttl", 300)  # 5分钟默认缓存

        # 初始化监控指标 (兼容数据源工厂)
        self.metrics = DataSourceMetrics()

        # 性能指标
        self.total_requests = 0
        self.successful_requests = 0
        self.error_count = 0
        self.last_response_time = 0.0

    def _get_market_service(self):
        """Lazy initialization of market service"""
        if self._market_service is None and self.mode != "mock":
            try:
                from app.services.market_data_service import get_market_data_service

                self._market_service = get_market_data_service()
            except Exception as e:
                self._market_service = None
                raise RuntimeError(f"Failed to initialize market service: {e}")
        return self._market_service

    def _get_mock_manager(self):
        """Lazy initialization of mock manager"""
        if self._mock_manager is None and self.mode == "mock":
            try:
                from app.mock.unified_mock_data import get_mock_data_manager

                self._mock_manager = get_mock_data_manager()
            except Exception as e:
                self._mock_manager = None
                raise RuntimeError(f"Failed to initialize mock manager: {e}")
        return self._mock_manager

    async def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取市场数据

        Args:
            endpoint: 数据端点 (fund-flow, etf/list, lhb, quotes, etc.)
            params: 请求参数

        Returns:
            格式化的市场数据响应
        """
        start_time = time.time()
        self.total_requests += 1

        try:
            params = params or {}
            result = await self._fetch_data(endpoint, params)

            # 记录成功指标
            response_time = time.time() - start_time
            self.last_response_time = response_time * 1000  # 转换为毫秒
            self.successful_requests += 1

            # 更新监控指标
            self._update_metrics(success=True, response_time=response_time * 1000)

            # 触发数据质量监控
            await self._trigger_quality_monitoring(endpoint, result, response_time * 1000)

            return result

        except Exception as e:
            self.error_count += 1
            response_time = time.time() - start_time
            logger.error("Market data fetch failed for %(endpoint)s: {str(e)}")

            # 更新监控指标
            self._update_metrics(success=False, response_time=response_time * 1000, error=str(e))

            # 记录失败的质量监控
            await self._trigger_quality_monitoring(endpoint, None, response_time * 1000, success=False)

            # 返回错误响应格式
            return {
                "status": "error",
                "message": f"Failed to fetch market data: {str(e)}",
                "data": None,
                "timestamp": datetime.now().isoformat(),
                "source": self.source_type,
                "endpoint": endpoint,
            }

    async def _fetch_data(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        实际的数据获取逻辑
        """
        if self.mode == "mock":
            return await self._fetch_mock_data(endpoint, params)
        else:
            # 根据端点类型调用相应的 MarketDataService 方法
            if endpoint == "fund-flow":
                return await self._fetch_fund_flow(params)
            elif endpoint == "etf/list":
                return await self._fetch_etf_list(params)
            elif endpoint == "lhb":
                return await self._fetch_long_hu_bang(params)
            elif endpoint == "quotes":
                return await self._fetch_quotes(params)
            elif endpoint == "chip-race":
                return await self._fetch_chip_race(params)
            else:
                raise ValueError(f"Unsupported market endpoint: {endpoint}")

    async def _fetch_mock_data(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取mock数据"""
        try:
            mock_manager = self._get_mock_manager()

            # 使用统一的get_data方法
            result = mock_manager.get_data(endpoint, **params)

            return {
                "status": "success",
                "data": result,
                "message": f"Mock data for {endpoint}",
                "timestamp": datetime.now().isoformat(),
                "source": self.source_type,
                "mode": "mock",
            }

        except Exception as e:
            logger.error("Mock data fetch failed for %(endpoint)s: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to fetch mock data: {str(e)}",
                "data": None,
                "timestamp": datetime.now().isoformat(),
                "source": self.source_type,
                "mode": "mock",
            }

    async def _fetch_fund_flow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取资金流向数据"""
        symbol = params.get("symbol")
        timeframe = params.get("timeframe", "1")
        start_date = params.get("start_date")
        end_date = params.get("end_date")

        try:
            market_service = self._get_market_service()
            results = market_service.query_fund_flow(symbol, timeframe, start_date, end_date)

            return {
                "status": "success",
                "data": [self._serialize_fund_flow(r) for r in results],
                "timestamp": datetime.now().isoformat(),
                "source": self.source_type,
                "endpoint": "fund-flow",
                "parameters": {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "start_date": str(start_date) if start_date else None,
                    "end_date": str(end_date) if end_date else None,
                },
            }
        except Exception as e:
            raise RuntimeError(f"Failed to fetch fund flow data: {str(e)}")

    async def _fetch_etf_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取ETF列表数据"""
        symbol = params.get("symbol")
        keyword = params.get("keyword")
        limit = params.get("limit", 50)

        try:
            market_service = self._get_market_service()
            results = market_service.query_etf_spot(symbol, limit=limit)

            return {
                "status": "success",
                "data": [self._serialize_etf_data(r) for r in results],
                "timestamp": datetime.now().isoformat(),
                "source": self.source_type,
                "endpoint": "etf/list",
                "parameters": {"symbol": symbol, "keyword": keyword, "limit": limit},
            }
        except Exception as e:
            raise RuntimeError(f"Failed to fetch ETF data: {str(e)}")

    async def _fetch_long_hu_bang(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取龙虎榜数据"""
        trade_date = params.get("trade_date")
        limit = params.get("limit", 50)

        try:
            market_service = self._get_market_service()
            results = market_service.query_lhb_detail(trade_date=trade_date, limit=limit)

            return {
                "status": "success",
                "data": [self._serialize_long_hu_bang(r) for r in results],
                "timestamp": datetime.now().isoformat(),
                "source": self.source_type,
                "endpoint": "lhb",
                "parameters": {
                    "trade_date": str(trade_date) if trade_date else None,
                    "limit": limit,
                },
            }
        except Exception as e:
            raise RuntimeError(f"Failed to fetch LongHuBang data: {str(e)}")

    async def _fetch_quotes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取实时行情数据 (暂时实现为模拟数据)"""
        symbols = params.get("symbols", [])

        try:
            # 由于MarketDataService没有实时行情接口，暂时返回模拟数据
            # 后续可以集成真实的实时行情数据源
            import random

            results = []
            for symbol in symbols:
                price = round(random.uniform(10, 100), 2)
                change = round(random.uniform(-5, 5), 2)
                change_percent = round(change / price * 100, 2)

                results.append(
                    {
                        "symbol": symbol,
                        "name": f"股票{symbol}",
                        "price": price,
                        "change": change,
                        "change_percent": change_percent,
                        "volume": random.randint(1000000, 50000000),
                        "amount": random.randint(10000000, 500000000),
                        "update_time": datetime.now().isoformat(),
                    }
                )

            return {
                "status": "success",
                "data": results,
                "timestamp": datetime.now().isoformat(),
                "source": self.source_type,
                "endpoint": "quotes",
                "parameters": {"symbols": symbols},
                "note": "Currently using simulated data - real-time quotes integration needed",
            }
        except Exception as e:
            raise RuntimeError(f"Failed to fetch quotes data: {str(e)}")

    async def _fetch_chip_race(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取竞价抢筹数据"""
        trade_date = params.get("trade_date")
        limit = params.get("limit", 50)

        try:
            market_service = self._get_market_service()
            results = market_service.query_chip_race(trade_date, limit)

            return {
                "status": "success",
                "data": [self._serialize_chip_race(r) for r in results],
                "timestamp": datetime.now().isoformat(),
                "source": self.source_type,
                "endpoint": "chip-race",
                "parameters": {
                    "trade_date": str(trade_date) if trade_date else None,
                    "limit": limit,
                },
            }
        except Exception as e:
            raise RuntimeError(f"Failed to fetch chip race data: {str(e)}")

    async def _trigger_quality_monitoring(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]],
        response_time: float,
        success: bool = True,
    ) -> None:
        """触发数据质量监控"""
        try:
            monitor = get_data_quality_monitor()
            await monitor.evaluate_data_quality(
                data=data or {},
                source=f"{self.source_type}:{endpoint}",
                response_time=response_time,
                success=success,
            )
        except Exception:
            logger.warning("Failed to trigger quality monitoring: {str(e)}")

    def _serialize_fund_flow(self, fund_flow) -> Dict[str, Any]:
        """序列化资金流向数据"""
        if hasattr(fund_flow, "to_dict"):
            return fund_flow.to_dict()
        elif hasattr(fund_flow, "__dict__"):
            return fund_flow.__dict__
        else:
            return {
                "symbol": getattr(fund_flow, "symbol", ""),
                "net_inflow": getattr(fund_flow, "net_inflow", 0),
                "main_inflow": getattr(fund_flow, "main_inflow", 0),
                "retail_inflow": getattr(fund_flow, "retail_inflow", 0),
                "super_large_inflow": getattr(fund_flow, "super_large_inflow", 0),
                "large_inflow": getattr(fund_flow, "large_inflow", 0),
                "medium_inflow": getattr(fund_flow, "medium_inflow", 0),
                "small_inflow": getattr(fund_flow, "small_inflow", 0),
                "date": getattr(fund_flow, "date", ""),
                "update_time": getattr(fund_flow, "update_time", datetime.now()),
            }

    def _serialize_etf_data(self, etf_data) -> Dict[str, Any]:
        """序列化ETF数据"""
        if hasattr(etf_data, "to_dict"):
            return etf_data.to_dict()
        elif hasattr(etf_data, "__dict__"):
            return etf_data.__dict__
        else:
            return {
                "symbol": getattr(etf_data, "symbol", ""),
                "name": getattr(etf_data, "name", ""),
                "price": getattr(etf_data, "price", 0),
                "change": getattr(etf_data, "change", 0),
                "change_percent": getattr(etf_data, "change_percent", 0),
                "volume": getattr(etf_data, "volume", 0),
                "amount": getattr(etf_data, "amount", 0),
                "update_time": getattr(etf_data, "update_time", datetime.now()),
            }

    def _serialize_long_hu_bang(self, lhb_data) -> Dict[str, Any]:
        """序列化龙虎榜数据"""
        if hasattr(lhb_data, "to_dict"):
            return lhb_data.to_dict()
        elif hasattr(lhb_data, "__dict__"):
            return lhb_data.__dict__
        else:
            return {
                "symbol": getattr(lhb_data, "symbol", ""),
                "name": getattr(lhb_data, "name", ""),
                "close_price": getattr(lhb_data, "close_price", 0),
                "change_percent": getattr(lhb_data, "change_percent", 0),
                "buy_amount": getattr(lhb_data, "buy_amount", 0),
                "sell_amount": getattr(lhb_data, "sell_amount", 0),
                "net_amount": getattr(lhb_data, "net_amount", 0),
                "trade_date": getattr(lhb_data, "trade_date", ""),
                "reason": getattr(lhb_data, "reason", ""),
                "update_time": getattr(lhb_data, "update_time", datetime.now()),
            }

    def _serialize_chip_race(self, chip_data) -> Dict[str, Any]:
        """序列化竞价抢筹数据"""
        if hasattr(chip_data, "to_dict"):
            return chip_data.to_dict()
        elif hasattr(chip_data, "__dict__"):
            return chip_data.__dict__
        else:
            return {
                "symbol": getattr(chip_data, "symbol", ""),
                "name": getattr(chip_data, "name", ""),
                "open_price": getattr(chip_data, "open_price", 0),
                "close_price": getattr(chip_data, "close_price", 0),
                "change_percent": getattr(chip_data, "change_percent", 0),
                "volume": getattr(chip_data, "volume", 0),
                "amount": getattr(chip_data, "amount", 0),
                "chip_ratio": getattr(chip_data, "chip_ratio", 0),
                "trade_date": getattr(chip_data, "trade_date", ""),
                "update_time": getattr(chip_data, "update_time", datetime.now()),
            }

    async def health_check(self) -> HealthStatus:
        """健康检查"""
        start_time = time.time()

        try:
            # 测试一个简单的数据获取操作
            await self._fetch_quotes({"symbols": ["000001.SZ"]})

            response_time = time.time() - start_time

            return HealthStatus(
                status=HealthStatusEnum.HEALTHY,
                response_time=response_time * 1000,  # 转换为毫秒
                message="Market data source is healthy",
                timestamp=datetime.now(),
            )

        except Exception as e:
            response_time = time.time() - start_time
            return HealthStatus(
                status=HealthStatusEnum.FAILED,
                response_time=response_time * 1000,
                message=f"Market data source health check failed: {str(e)}",
                timestamp=datetime.now(),
            )

    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0

        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "error_count": self.error_count,
            "success_rate": success_rate,
            "last_response_time_ms": self.last_response_time,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "source_type": self.source_type,
            "name": self.name,
        }

    def _update_metrics(self, success: bool, response_time: float, error: str = None):
        """更新监控指标 (兼容数据源工厂)"""
        self.metrics.total_requests += 1
        self.metrics.last_check = datetime.now()

        if success:
            # 更新响应时间 (使用指数移动平均)
            if self.metrics.response_time == 0:
                self.metrics.response_time = response_time
            else:
                alpha = 0.3  # 平滑因子
                self.metrics.response_time = alpha * response_time + (1 - alpha) * self.metrics.response_time
        else:
            self.metrics.error_count += 1
            self.metrics.last_error = error

        # 计算成功率
        if self.metrics.total_requests > 0:
            self.metrics.success_rate = (
                (self.metrics.total_requests - self.metrics.error_count) / self.metrics.total_requests * 100
            )

        # 计算可用性 (基于最近的成功率)
        self.metrics.availability = self.metrics.success_rate
