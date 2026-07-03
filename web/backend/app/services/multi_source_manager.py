"""
Multi-source Data Manager
Multi-data Source Support

多数据源管理器：
- 优先级路由：根据优先级选择最佳数据源
- 健康监控：监控各数据源健康状态

.. deprecated::
    本模块作为 OpenStock 收编 PoC 后的退役候补,保留 facade 兼容遗留
    调用方。新代码禁止使用 ``MultiSourceManager`` —— 4 个业务方法
    (``fetch_realtime_quote`` / ``fetch_fund_flow`` / ``fetch_dragon_tiger``
    / ``fetch_announcements``) 已被删除,数据访问请改走:

    * OpenStock-owned category → ``OpenStockClient.fetch(category, ...)``
      (参见 ``web/backend/app/services/announcement_service.py`` 迁移示例)
    * OpenStock 永久无覆盖 category → ``ExtraSourceRouter.fetch(category, ...)``
      (参见 ``web/backend/app/services/extra_source/README.md``)

    完整契约: ``openspec/changes/add-extra-source-adapter-contract/design.md``。
    彻底退役跟踪: ``docs/guides/HANDOFF_C3_DIRECTION6_DONE.md``。
"""

import logging
from typing import Any, Dict, List, Optional

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

    .. deprecated::
        作为 OpenStock 收编 PoC 后的退役候补,保留 facade 仅作过渡期兼容。
        新代码必须使用 ``OpenStockClient`` (OpenStock-owned category)
        或 ``ExtraSourceRouter`` (永久无覆盖 category)。
    """

    def __init__(self):
        """初始化多数据源管理器"""
        logger.warning(
            "MultiSourceManager is deprecated (OpenStock 收编 PoC 后退役候补); "
            "new code must use OpenStockClient (OpenStock-owned category) "
            "or extra_source.ExtraSourceRouter (permanently-uncovered category). "
            "See openspec/changes/add-extra-source-adapter-contract/design.md."
        )
        self._adapters: Dict[DataSourceType, BaseDataSourceAdapter] = {}

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
