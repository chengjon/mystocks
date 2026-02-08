"""
自选股管理数据源适配器
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

class WatchlistDataSourceAdapter(IDataSource):
    """自选股管理数据源适配器 - 集成现有自选股服务到数据源工厂模式"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_type = "watchlist"
        self.name = config.get("name", "Watchlist Management Source")
        self.mode = config.get("mode", "mock")

        # Lazy initialization of services (only when needed)
        self._watchlist_service = None
        self._mock_manager = None

        self.metrics = DataSourceMetrics()
        self._cache = {}
        self._cache_ttl = config.get("cache_ttl", 300)  # 5分钟缓存

    def _get_watchlist_service(self):
        """Lazy initialization of watchlist service"""
        if self._watchlist_service is None and self.mode != "mock":
            try:
                from app.services.watchlist_service import get_watchlist_service

                self._watchlist_service = get_watchlist_service()
            except Exception as e:
                self._watchlist_service = None
                raise RuntimeError(f"Failed to initialize watchlist service: {e}")
        return self._watchlist_service

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

    async def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """获取自选股管理数据"""
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
            data = await self._fetch_watchlist_data(endpoint, params)

            # 缓存结果
            self._cache[cache_key] = {"data": data, "timestamp": time.time()}

            self.metrics.record_success(time.time() - start_time)
            return data

        except Exception as e:
            self.metrics.record_error(time.time() - start_time, str(e))
            logger.error(f"Watchlist data fetch error: {e}")
            raise

    async def _fetch_watchlist_data(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """从自选股服务获取数据"""
        if self.mode == "mock":
            # 使用Mock数据
            return self._get_mock_watchlist_data(endpoint, params)

        try:
            # 解析endpoint路径
            path_parts = endpoint.strip("/").split("/")

            # 注意：watchlist服务通常需要用户ID，这里使用默认用户ID
            user_id = params.get("user_id", 1)

            if endpoint == "list" or endpoint == "/list":
                # 获取用户自选股列表
                watchlist_service = self._get_watchlist_service()
                watchlist = watchlist_service.get_user_watchlist(user_id)
                return {
                    "success": True,
                    "data": watchlist,
                    "total": len(watchlist),
                    "message": "获取自选股列表成功",
                }

            elif endpoint == "symbols" or endpoint == "/symbols":
                # 获取自选股代码列表
                watchlist_service = self._get_watchlist_service()
                symbols = watchlist_service.get_watchlist_symbols(user_id)
                return {
                    "success": True,
                    "data": symbols,
                    "total": len(symbols),
                    "message": "获取自选股代码列表成功",
                }

            elif endpoint.startswith("add/"):
                # 添加自选股 add/{symbol}
                if len(path_parts) >= 2:
                    symbol = path_parts[1]
                    display_name = params.get("display_name", symbol)
                    exchange = params.get("exchange", "SZSE")
                    market = params.get("market", "CN")
                    notes = params.get("notes", "")
                    group_id = params.get("group_id")
                    group_name = params.get("group_name")

                    try:
                        watchlist_item = self._get_watchlist_service().add_stock_to_watchlist(
                            user_id=user_id,
                            symbol=symbol,
                            display_name=display_name,
                            exchange=exchange,
                            market=market,
                            notes=notes,
                            group_id=group_id,
                            group_name=group_name,
                        )
                        return {
                            "success": True,
                            "data": watchlist_item,
                            "message": f"成功添加 {symbol} 到自选股",
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": str(e),
                            "message": f"添加 {symbol} 到自选股失败",
                        }

            elif endpoint.startswith("remove/"):
                # 移除自选股 remove/{symbol}
                if len(path_parts) >= 2:
                    symbol = path_parts[1]

                    try:
                        self._get_watchlist_service().remove_stock_from_watchlist(user_id=user_id, symbol=symbol)
                        return {
                            "success": True,
                            "message": f"成功从自选股中移除 {symbol}",
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": str(e),
                            "message": f"移除 {symbol} 从自选股失败",
                        }

            elif endpoint.startswith("groups/"):
                # 分组管理相关
                if path_parts[1] == "list":
                    # 获取分组列表 groups/list
                    groups = self._get_watchlist_service().get_user_groups(user_id)
                    return {
                        "success": True,
                        "data": groups,
                        "total": len(groups),
                        "message": "获取自选股分组列表成功",
                    }

                elif path_parts[1] == "create":
                    # 创建分组 groups/create
                    group_name = params.get("group_name", "默认分组")

                    try:
                        group = self._get_watchlist_service().create_group(user_id=user_id, group_name=group_name)
                        return {
                            "success": True,
                            "data": group,
                            "message": f"成功创建分组: {group_name}",
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": str(e),
                            "message": f"创建分组失败: {group_name}",
                        }

            # 如果没有匹配的endpoint，返回默认数据
            return self._get_mock_watchlist_data(endpoint, params)

        except Exception as e:
            logger.error(f"Watchlist service error: {e}")
            # 降级到Mock数据
            if self._get_mock_manager():
                return self._get_mock_watchlist_data(endpoint, params)
            raise

    def _get_mock_watchlist_data(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """获取Mock自选股数据"""
        mock_manager = self._get_mock_manager()
        if not mock_manager:
            return {"success": False, "error": "No mock data available"}

        try:
            # 使用统一mock数据管理器
            return mock_manager.get_data("watchlist", endpoint=endpoint, **params)

        except Exception as e:
            logger.error(f"Mock watchlist data fetch failed for {endpoint}: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch mock watchlist data: {str(e)}",
                "data": None,
            }

    async def health_check(self) -> HealthStatus:
        """健康检查"""
        try:
            start_time = time.time()

            # 检查自选股服务可用性
            service_available = self._get_watchlist_service() is not None
            mock_available = self._get_mock_manager() is not None

            # 基础健康检查
            basic_healthy = service_available or mock_available

            # 简单连接测试
            connection_test = False
            if basic_healthy:
                try:
                    # 尝试获取自选股列表作为连接测试
                    if self.mode != "mock" and service_available:
                        self._get_watchlist_service().get_user_watchlist(1)
                    connection_test = True
                except Exception:
                    if mock_available:
                        connection_test = True

            status = HealthStatusEnum.HEALTHY if (basic_healthy and connection_test) else HealthStatusEnum.FAILED

            return HealthStatus(
                status=status,
                response_time=(time.time() - start_time) * 1000,
                message=f"Watchlist data source is {status.value}",
                timestamp=datetime.now(),
            )

        except Exception as e:
            return HealthStatus(
                status=HealthStatusEnum.FAILED,
                response_time=0.0,
                message=f"Watchlist health check failed: {str(e)}",
                timestamp=datetime.now(),
            )

    def get_metrics(self) -> DataSourceMetrics:
        """获取监控指标"""
        return self.metrics

    async def close(self):
        """关闭连接和清理资源"""
        pass
