"""
技术分析数据源适配器
"""
import time
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.data_source_interface import (
    HealthStatus,
    HealthStatusEnum,
    IDataSource,
)
from .base import DataSourceMetrics

logger = logging.getLogger(__name__)

class TechnicalAnalysisDataSourceAdapter(IDataSource):
    """技术分析数据源适配器 - 集成现有技术分析服务到数据源工厂模式"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_type = "technical_analysis"
        self.name = config.get("name", "Technical Analysis Source")

        # Initialize services lazily (only when needed)
        self._technical_service = None
        self._mock_manager = None
        self.metrics = DataSourceMetrics()
        self._cache = {}
        self._cache_ttl = config.get("cache_ttl", 300)

    def _get_technical_service(self):
        """Lazy initialization of technical analysis service"""
        if self._technical_service is None:
            try:
                from app.services.technical_analysis_service import (
                    technical_analysis_service,
                )

                self._technical_service = technical_analysis_service
            except Exception as e:
                self._technical_service = None
                raise RuntimeError(f"Failed to initialize technical analysis service: {e}")
        return self._technical_service

    def _get_mock_manager(self):
        """Lazy initialization of mock manager"""
        if self._mock_manager is None:
            try:
                from app.mock.unified_mock_data import get_mock_data_manager

                self._mock_manager = get_mock_data_manager()
            except Exception as e:
                self._mock_manager = None
                raise RuntimeError(f"Failed to initialize mock manager: {e}")
        return self._mock_manager

    async def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取技术分析数据"""
        params = params or {}
        start_time = time.time()

        # Ensure service is available
        service = self._get_technical_service()
        if not service:
            raise RuntimeError("Technical analysis service not available")

        try:
            # 解析端点路径
            path_parts = endpoint.strip("/").split("/")

            # 获取symbol参数
            symbol = params.get("symbol", "000001")

            # 使用 run_in_executor 执行同步计算任务，防止阻塞事件循环
            import asyncio

            asyncio.get_running_loop()

            if endpoint == "indicators" or (len(path_parts) >= 2 and path_parts[1] == "indicators"):
                # "indicators" or /{symbol}/indicators
                period = params.get("period", "daily")
                start_date = params.get("start_date")
                end_date = params.get("end_date")

                data = await self._get_all_indicators(symbol, period, start_date, end_date)

                # For indicators endpoint, return data directly without wrapping
                self.metrics.record_success((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "data": data,
                    "source": self.source_type,
                    "endpoint": endpoint,
                    "timestamp": datetime.now().isoformat(),
                }

            elif endpoint == "trend" or (len(path_parts) >= 2 and path_parts[1] == "trend"):
                # "trend" or /{symbol}/trend
                period = params.get("period", "daily")

                data = await self._get_trend_indicators(symbol, period)

                self.metrics.record_success((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "data": data,
                    "source": self.source_type,
                    "endpoint": endpoint,
                    "timestamp": datetime.now().isoformat(),
                }

            elif endpoint == "momentum" or (len(path_parts) >= 2 and path_parts[1] == "momentum"):
                # "momentum" or /{symbol}/momentum
                period = params.get("period", "daily")

                data = await self._get_momentum_indicators(symbol, period)

                self.metrics.record_success((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "data": data,
                    "source": self.source_type,
                    "endpoint": endpoint,
                    "timestamp": datetime.now().isoformat(),
                }

            elif endpoint == "volatility" or (len(path_parts) >= 2 and path_parts[1] == "volatility"):
                # "volatility" or /{symbol}/volatility
                period = params.get("period", "daily")

                data = await self._get_volatility_indicators(symbol, period)

                self.metrics.record_success((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "data": data,
                    "source": self.source_type,
                    "endpoint": endpoint,
                    "timestamp": datetime.now().isoformat(),
                }

            elif endpoint == "volume" or (len(path_parts) >= 2 and path_parts[1] == "volume"):
                # "volume" or /{symbol}/volume
                period = params.get("period", "daily")

                data = await self._get_volume_indicators(symbol, period)

                self.metrics.record_success((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "data": data,
                    "source": self.source_type,
                    "endpoint": endpoint,
                    "timestamp": datetime.now().isoformat(),
                }

            elif endpoint == "signals" or (len(path_parts) >= 2 and path_parts[1] == "signals"):
                # "signals" or /{symbol}/signals
                period = params.get("period", "daily")

                data = await self._get_trading_signals(symbol, period)

                logger.info(f"🔍 _get_trading_signals returned data: {data}, type={type(data)}")

                # For signals endpoint, return data directly without wrapping
                self.metrics.record_success((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "data": data,
                    "source": self.source_type,
                    "endpoint": endpoint,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            # 记录失败请求
            self.metrics.record_error((time.time() - start_time) * 1000, str(e))
            raise e

    async def _get_all_indicators(
        self,
        symbol: str,
        period: str = "1y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取所有技术指标 - 使用真实服务"""
        import asyncio

        service = self._get_technical_service()

        # 使用 run_in_executor 运行同步计算
        return await asyncio.to_thread(
            service.calculate_all_indicators, symbol=symbol, period=period, start_date=start_date, end_date=end_date
        )

    async def _get_trend_indicators(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """获取趋势指标 - 使用真实服务"""
        import asyncio

        service = self._get_technical_service()

        # 获取历史数据
        df = await asyncio.to_thread(service.get_stock_history, symbol=symbol, period=period)

        # 计算指标
        return await asyncio.to_thread(service.calculate_trend_indicators, df)

    async def _get_momentum_indicators(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """获取动量指标 - 使用真实服务"""
        import asyncio

        service = self._get_technical_service()

        # 获取历史数据
        df = await asyncio.to_thread(service.get_stock_history, symbol=symbol, period=period)

        # 计算指标
        return await asyncio.to_thread(service.calculate_momentum_indicators, df)

    async def _get_volatility_indicators(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """获取波动性指标 - 使用真实服务"""
        import asyncio

        service = self._get_technical_service()

        # 获取历史数据
        df = await asyncio.to_thread(service.get_stock_history, symbol=symbol, period=period)

        # 计算指标
        return await asyncio.to_thread(service.calculate_volatility_indicators, df)

    async def _get_volume_indicators(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """获取成交量指标 - 使用真实服务"""
        import asyncio

        service = self._get_technical_service()

        # 获取历史数据
        df = await asyncio.to_thread(service.get_stock_history, symbol=symbol, period=period)

        # 计算指标
        return await asyncio.to_thread(service.calculate_volume_indicators, df)

    async def _get_trading_signals(self, symbol: str, period: str = "daily") -> Dict[str, Any]:
        """获取交易信号 - 使用真实服务"""
        import asyncio

        service = self._get_technical_service()

        logger.info(f"🔍 _get_trading_signals called: symbol={symbol}, period={period}")

        # 获取历史数据
        df = await asyncio.to_thread(service.get_stock_history, symbol=symbol, period=period)

        logger.info(f"🔍 _get_trading_signals: got df with shape={df.shape}")

        # 生成信号
        result = await asyncio.to_thread(service.generate_trading_signals, df)

        logger.info(f"🔍 _get_trading_signals: result={result}, type={type(result)}")

        return result

    async def _get_stock_history(
        self,
        symbol: str,
        period: str = "1y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """获取历史行情数据 - 使用真实服务"""
        import asyncio

        service = self._get_technical_service()

        # 获取DataFrame
        df = await asyncio.to_thread(
            service.get_stock_history, symbol=symbol, period=period, start_date=start_date, end_date=end_date
        )

        if df.empty:
            return []

        # 限制返回数量
        if limit and len(df) > limit:
            df = df.iloc[-limit:]

        # 转换日期格式字符串
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")

        return df.to_dict("records")

    async def _get_batch_indicators(self, symbols: List[str], period: str = "1y") -> Dict[str, Any]:
        """批量获取指标 - 使用真实服务"""
        results = {}
        for symbol in symbols:
            try:
                # 复用 _get_all_indicators
                indicators = await self._get_all_indicators(symbol, period)
                results[symbol] = indicators
            except Exception as e:
                logger.error(f"Failed to get indicators for {symbol}: {e}")
                results[symbol] = {"error": str(e)}

        return results

    async def health_check(self) -> HealthStatus:
        """健康检查"""
        start_time = time.time()

        try:
            # 测试技术分析服务可用性
            test_symbol = "000001"
            await self._get_trend_indicators(test_symbol)

            response_time = (time.time() - start_time) * 1000

            return HealthStatus(
                status=HealthStatusEnum.HEALTHY,
                message="Technical analysis source is healthy",
                response_time=response_time,
                timestamp=datetime.now(),
            )

        except Exception as e:
            return HealthStatus(
                status=HealthStatusEnum.FAILED,
                message=f"Health check failed: {str(e)}",
                response_time=0,
                timestamp=datetime.now(),
            )

    def get_metrics(self) -> "DataSourceMetrics":
        """获取监控指标"""
        return self.metrics

    async def close(self):
        """关闭连接和清理资源"""
        # Technical Analysis适配器不需要清理特定资源
