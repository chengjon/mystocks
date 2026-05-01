"""
治理层数据获取桥接器

该模块负责将治理引擎的数据需求转换为对 DataSourceManagerV2 的调用。
实现了从"治理视角"到"数据源视角"的转换，屏蔽了具体的适配器细节。

Design Pattern: Bridge / Facade
"""

import logging
from enum import Enum
from typing import Dict, List, Optional

import pandas as pd

# 尝试导入 DataSourceManagerV2
try:
    from src.core.data_source.batch_processor import BatchProcessor
    from src.core.data_source_manager_v2 import DataSourceManagerV2
except ImportError:
    # Fallback or error handling if the module is not found
    # This might happen during partial refactoring
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).parent.parent.parent.parent))
    from src.core.data_source.batch_processor import BatchProcessor
    from src.core.data_source_manager_v2 import DataSourceManagerV2

logger = logging.getLogger(__name__)


class RoutePolicy(Enum):
    """路由策略枚举"""

    SMART_ROUTING = "smart"  # 综合最优（优先级 + 质量评分）
    FASTEST = "fastest"  # 响应最快
    STABLE = "stable"  # 成功率最高
    SPECIFIC_SOURCE = "specific"  # 指定源（用于交叉验证）


class TimeFrame(Enum):
    """时间周期枚举"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MINUTE = "minute"


class GovernanceDataFetcher:
    """
    治理数据获取器

    职责：
    1. 接收治理任务的数据请求（股票列表、时间范围）
    2. 根据策略（RoutePolicy）选择合适的数据源路由
    3. 调用 DataSourceManagerV2 获取数据
    4. 统一返回格式，处理异常
    """

    def __init__(self):
        self.manager = self._get_manager_instance()
        self.batch_processor = BatchProcessor()

    def _get_manager_instance(self) -> DataSourceManagerV2:
        """获取 DataSourceManagerV2 单例"""
        # 这里可以使用依赖注入或单例模式
        return DataSourceManagerV2()

    def fetch_batch_kline(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        period: TimeFrame = TimeFrame.DAILY,
        policy: RoutePolicy = RoutePolicy.SMART_ROUTING,
        source_id: Optional[str] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        批量获取K线数据

        Args:
            symbols: 股票代码列表
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            period: 时间周期
            policy: 路由策略
            source_id: 指定的数据源ID（当 policy=SPECIFIC_SOURCE 时必填）

        Returns:
            Dict[symbol, DataFrame]: 成功获取的数据字典
        """
        results = {}

        # 转换时间周期到数据分类
        category_map = {
            TimeFrame.DAILY: "DAILY_KLINE",
            TimeFrame.WEEKLY: "WEEKLY_KLINE",
            TimeFrame.MONTHLY: "MONTHLY_KLINE",
            TimeFrame.MINUTE: "MINUTE_KLINE",
        }
        data_category = category_map.get(period, "DAILY_KLINE")

        if len(symbols) > 1:
            batch_result = self.batch_processor.fetch_batch_kline(
                self,
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq",
                data_category=data_category,
                policy=policy,
                source_id=source_id,
            )

            for symbol, error in batch_result.get("errors", {}).items():
                logger.error("批量获取数据失败: %s, 错误: %s", symbol, error)

            return batch_result.get("data", {})

        for symbol in symbols:
            try:
                df = self._fetch_single_symbol(symbol, start_date, end_date, data_category, policy, source_id)
                if df is not None and not df.empty:
                    results[symbol] = df
                else:
                    logger.warning("获取数据为空: %s", symbol)

            except Exception as exc:
                logger.error("获取数据失败: %s, 错误: %s", symbol, exc)
                # 记录失败，但不中断批量过程
                continue

        return results

    def fetch_kline(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        adjust: str = "qfq",
        data_category: str = "DAILY_KLINE",
        policy: RoutePolicy = RoutePolicy.SMART_ROUTING,
        source_id: Optional[str] = None,
        endpoint_info: Optional[Dict] = None,
    ) -> Optional[pd.DataFrame]:
        """供 BatchProcessor 调用的单标的 K 线抓取包装。"""
        return self._fetch_single_symbol(
            symbol,
            start_date,
            end_date,
            data_category,
            policy,
            source_id,
            endpoint_info=endpoint_info,
        )

    def shutdown(self, wait: bool = True):
        """释放批处理线程池资源。"""
        self.batch_processor.shutdown(wait=wait)

    def resolve_endpoint(
        self,
        data_category: str,
        policy: RoutePolicy = RoutePolicy.SMART_ROUTING,
        source_id: Optional[str] = None,
        symbol: Optional[str] = None,
    ) -> Optional[Dict]:
        """解析当前批量请求应使用的数据端点。"""
        if policy == RoutePolicy.SMART_ROUTING:
            return self.manager.get_best_endpoint(data_category)

        if policy == RoutePolicy.SPECIFIC_SOURCE:
            if not source_id:
                raise ValueError("指定源策略必须提供 source_id")

            endpoints = self.manager.find_endpoints(data_category=data_category, source_type=source_id)
            return endpoints[0] if endpoints else None

        if policy == RoutePolicy.FASTEST:
            endpoints = self.manager.find_endpoints(data_category=data_category, only_healthy=True)
            if endpoints:
                endpoints.sort(key=lambda item: item.get("avg_response_time", 999))
                return endpoints[0]
            return None

        if policy == RoutePolicy.STABLE:
            endpoints = self.manager.find_endpoints(data_category=data_category, only_healthy=True)
            if endpoints:
                endpoints.sort(key=lambda item: -item.get("success_rate", 0))
                return endpoints[0]
            return None

        return None

    def _fetch_single_symbol(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        data_category: str,
        policy: RoutePolicy,
        source_id: Optional[str],
        endpoint_info: Optional[Dict] = None,
    ) -> Optional[pd.DataFrame]:
        """获取单个股票数据"""
        endpoint = endpoint_info or self.resolve_endpoint(
            data_category=data_category,
            policy=policy,
            source_id=source_id,
            symbol=symbol,
        )

        if not endpoint:
            logger.warning("未找到可用的数据端点: category=%s, policy=%s", data_category, policy)
            return None

        # 调用 V2 的内部方法 _call_endpoint
        # 注意：这里我们访问了 protected method，这是为了实现高级路由
        # 在未来的重构中，应该在 DataSourceManagerV2 中暴露更灵活的接口
        logger.info("使用端点: %s 获取 %s", endpoint.get("endpoint_name"), symbol)

        try:
            return self.manager._call_endpoint(
                endpoint, symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq"
            )
        except AttributeError:
            # 如果 manager 没有 _call_endpoint (可能是接口变了)，尝试回退到高层接口
            # 仅当 Smart Routing 时安全
            if policy == RoutePolicy.SMART_ROUTING and data_category == "DAILY_KLINE":
                return self.manager.get_stock_daily(symbol, start_date, end_date)
            else:
                raise
