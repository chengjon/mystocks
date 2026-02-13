"""
Multi-source Data Manager
Multi-data Source Support

多数据源管理器：
- 优先级路由：根据优先级选择最佳数据源
- 自动故障转移：主数据源失败时自动切换到备用源
- 数据聚合：合并来自多个数据源的数据
- 健康监控：监控各数据源健康状态
- 智能缓存：减少重复请求
"""

import logging
import time
from datetime import date
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from app.adapters.base import (
    BaseDataSourceAdapter,
    DataCategory,
    DataSourceType,
)
from app.adapters.cninfo_adapter import get_cninfo_adapter
from app.adapters.eastmoney_enhanced import (
    get_eastmoney_enhanced_adapter,
)

logger = logging.getLogger(__name__)


class MultiSourceManager:
    """
    多数据源管理器

    负责协调多个数据源，提供统一的数据访问接口
    支持优先级路由和自动故障转移
    """

    def __init__(self):
        """初始化多数据源管理器"""
        self._adapters: Dict[DataSourceType, BaseDataSourceAdapter] = {}
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 缓存5分钟

        # 初始化数据源
        self._initialize_adapters()

        # 数据类别到数据源的映射
        self._category_sources: Dict[DataCategory, List[DataSourceType]] = {}
        self._build_category_mapping()

        logger.info("MultiSourceManager initialized with adapters: " f"{list(self._adapters.keys())}")

    def _initialize_adapters(self):
        """初始化所有数据源适配器"""
        try:
            # 初始化东方财富适配器
            eastmoney = get_eastmoney_enhanced_adapter()
            self._adapters[DataSourceType.EASTMONEY] = eastmoney
            logger.info("Initialized EastMoney adapter")

        except Exception:
            logger.error("Failed to initialize EastMoney adapter: %(e)s")

        try:
            # 初始化巨潮资讯适配器
            cninfo = get_cninfo_adapter()
            self._adapters[DataSourceType.CNINFO] = cninfo
            logger.info("Initialized Cninfo adapter")

        except Exception:
            logger.error("Failed to initialize Cninfo adapter: %(e)s")

    def _build_category_mapping(self):
        """
        构建数据类别到数据源的映射

        根据各数据源支持的类别和优先级构建映射表
        """
        # 收集所有适配器支持的类别
        for source_type, adapter in self._adapters.items():
            if not adapter.is_available():
                continue

            for category in adapter.get_supported_categories():
                if category not in self._category_sources:
                    self._category_sources[category] = []

                self._category_sources[category].append(source_type)

        # 按优先级排序
        for category in self._category_sources:
            self._category_sources[category].sort(key=lambda st: self._adapters[st].get_config().priority)

        logger.info("Built category mapping: {len(self._category_sources)} categories")

    def get_adapter(self, source_type: DataSourceType) -> Optional[BaseDataSourceAdapter]:
        """
        获取指定类型的适配器

        Args:
            source_type: 数据源类型

        Returns:
            Optional[BaseDataSourceAdapter]: 适配器实例
        """
        return self._adapters.get(source_type)

    def get_available_adapters(self) -> List[BaseDataSourceAdapter]:
        """
        获取所有可用的适配器

        Returns:
            List[BaseDataSourceAdapter]: 可用适配器列表
        """
        return [adapter for adapter in self._adapters.values() if adapter.is_available()]

    def get_sources_for_category(self, category: DataCategory) -> List[DataSourceType]:
        """
        获取支持指定数据类别的数据源（按优先级排序）

        Args:
            category: 数据类别

        Returns:
            List[DataSourceType]: 数据源列表
        """
        return self._category_sources.get(category, [])

    def fetch_with_fallback(
        self,
        category: DataCategory,
        fetch_func: Callable[[BaseDataSourceAdapter], pd.DataFrame],
        cache_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        使用故障转移机制获取数据

        Args:
            category: 数据类别
            fetch_func: 数据获取函数，接收adapter作为参数
            cache_key: 缓存键（可选）

        Returns:
            Dict: 包含数据和元信息的字典
        """
        # 检查缓存
        if cache_key and cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                logger.debug("Cache hit for %(cache_key)s")
                return {
                    "success": True,
                    "data": cached_data,
                    "source": "cache",
                    "cached": True,
                }

        # 获取支持该类别的数据源列表
        sources = self.get_sources_for_category(category)

        if not sources:
            logger.warning("No data source available for category {category.value}")
            return {
                "success": False,
                "error": f"No data source supports {category.value}",
                "source": None,
            }

        # 尝试从各个数据源获取数据（按优先级）
        errors = []

        for source_type in sources:
            adapter = self._adapters.get(source_type)

            if not adapter or not adapter.is_available():
                logger.debug("Skipping unavailable source: {source_type.value}")
                continue

            try:
                logger.info("Trying to fetch from {source_type.value}")
                start_time = time.time()

                # 调用数据获取函数
                data = fetch_func(adapter)

                response_time = time.time() - start_time

                if not data.empty:
                    # 成功获取数据
                    result = {
                        "success": True,
                        "data": data,
                        "source": source_type.value,
                        "response_time": round(response_time, 3),
                        "cached": False,
                    }

                    # 更新缓存
                    if cache_key:
                        self._cache[cache_key] = (data, time.time())

                    logger.info(
                        f"Successfully fetched from {source_type.value} " f"({len(data)} rows in {response_time:.3f}s)"
                    )

                    return result

                else:
                    logger.warning("{source_type.value} returned empty data")
                    errors.append(f"{source_type.value}: empty data")

            except Exception as e:
                error_msg = f"{source_type.value}: {str(e)}"
                logger.error("Failed to fetch from {source_type.value}: %(e)s")
                errors.append(error_msg)

        # 所有数据源都失败
        return {
            "success": False,
            "error": "All data sources failed",
            "errors": errors,
            "source": None,
        }

    def fetch_realtime_quote(
        self,
        symbols: Optional[List[str]] = None,
        source: Optional[DataSourceType] = None,
    ) -> Dict[str, Any]:
        """
        获取实时行情

        Args:
            symbols: 股票代码列表
            source: 指定数据源（可选）

        Returns:
            Dict: 行情数据和元信息
        """
        # 如果指定了数据源，直接使用
        if source:
            adapter = self._adapters.get(source)
            if adapter and adapter.is_available():
                try:
                    data = adapter.fetch_realtime_quote(symbols)
                    return {
                        "success": not data.empty,
                        "data": data,
                        "source": source.value,
                    }
                except Exception as e:
                    return {"success": False, "error": str(e), "source": source.value}

        # 使用故障转移机制
        cache_key = f"realtime_quote:{','.join(symbols) if symbols else 'all'}"

        return self.fetch_with_fallback(
            DataCategory.REALTIME_QUOTE,
            lambda adapter: adapter.fetch_realtime_quote(symbols),
            cache_key,
        )

    def fetch_fund_flow(
        self,
        symbol: Optional[str] = None,
        timeframe: str = "今日",
        source: Optional[DataSourceType] = None,
    ) -> Dict[str, Any]:
        """
        获取资金流向

        Args:
            symbol: 股票代码
            timeframe: 时间范围
            source: 指定数据源

        Returns:
            Dict: 资金流向数据和元信息
        """
        cache_key = f"fund_flow:{symbol}:{timeframe}"

        # 如果指定了数据源
        if source:
            adapter = self._adapters.get(source)
            if adapter and hasattr(adapter, "fetch_fund_flow"):
                try:
                    data = adapter.fetch_fund_flow(symbol, timeframe)
                    return {
                        "success": not data.empty,
                        "data": data,
                        "source": source.value,
                    }
                except Exception as e:
                    return {"success": False, "error": str(e), "source": source.value}

        return self.fetch_with_fallback(
            DataCategory.FUND_FLOW,
            lambda adapter: (
                adapter.fetch_fund_flow(symbol, timeframe) if hasattr(adapter, "fetch_fund_flow") else pd.DataFrame()
            ),
            cache_key,
        )

    def fetch_dragon_tiger(self, date_str: str, source: Optional[DataSourceType] = None) -> Dict[str, Any]:
        """
        获取龙虎榜

        Args:
            date_str: 日期
            source: 指定数据源

        Returns:
            Dict: 龙虎榜数据和元信息
        """
        cache_key = f"dragon_tiger:{date_str}"

        return self.fetch_with_fallback(
            DataCategory.DRAGON_TIGER,
            lambda adapter: (
                adapter.fetch_dragon_tiger(date_str) if hasattr(adapter, "fetch_dragon_tiger") else pd.DataFrame()
            ),
            cache_key,
        )

    def fetch_announcements(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[str] = None,
        source: Optional[DataSourceType] = None,
    ) -> Dict[str, Any]:
        """
        获取公告

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            category: 公告类别
            source: 指定数据源

        Returns:
            Dict: 公告数据和元信息
        """
        # 公告主要来自Cninfo
        if source is None:
            source = DataSourceType.CNINFO

        adapter = self._adapters.get(source)

        if not adapter or not adapter.is_available():
            return {
                "success": False,
                "error": f"Source {source.value} not available",
                "source": source.value,
            }

        try:
            if hasattr(adapter, "fetch_announcements"):
                data = adapter.fetch_announcements(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    category=category,
                )

                return {
                    "success": not data.empty,
                    "data": data,
                    "source": source.value,
                    "count": len(data) if not data.empty else 0,
                }
            else:
                return {
                    "success": False,
                    "error": "fetch_announcements not supported",
                    "source": source.value,
                }

        except Exception as e:
            logger.error("Failed to fetch announcements: %(e)s")
            return {"success": False, "error": str(e), "source": source.value}

    def get_all_health_status(self) -> List[Dict[str, Any]]:
        """
        获取所有数据源的健康状态

        Returns:
            List[Dict]: 健康状态列表
        """
        statuses = []

        for source_type, adapter in self._adapters.items():
            try:
                health = adapter.check_health()
                stats = adapter.get_statistics()

                statuses.append(
                    {
                        "source_type": source_type.value,
                        "status": health.status.value,
                        "enabled": adapter.get_config().enabled,
                        "priority": adapter.get_config().priority,
                        "success_rate": health.success_rate,
                        "avg_response_time": health.avg_response_time,
                        "error_count": health.error_count,
                        "last_check": health.last_check.isoformat(),
                        "supported_categories": [cat.value for cat in health.supported_categories],
                        **stats,
                    }
                )

            except Exception:
                logger.error("Failed to get health status for {source_type.value}: %(e)s")

        return statuses

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        logger.info("Cache cleared")

    def refresh_category_mapping(self):
        """刷新数据类别映射"""
        self._category_sources.clear()
        self._build_category_mapping()
        logger.info("Category mapping refreshed")


# 全局单例
_multi_source_manager = None


def get_multi_source_manager() -> MultiSourceManager:
    """获取多数据源管理器单例"""
    global _multi_source_manager
    if _multi_source_manager is None:
        _multi_source_manager = MultiSourceManager()
    return _multi_source_manager
