"""
治理层数据获取桥接器

该模块负责将治理引擎的数据需求转换为对 DataSourceManagerV2 的调用。
实现了从"治理视角"到"数据源视角"的转换，屏蔽了具体的适配器细节。

Design Pattern: Bridge / Facade
"""

import logging
import pandas as pd
from typing import Dict, List, Optional, Union
from enum import Enum
from datetime import datetime

# 尝试导入 DataSourceManagerV2
try:
    from src.core.data_source_manager_v2 import DataSourceManagerV2
except ImportError:
    # Fallback or error handling if the module is not found
    # This might happen during partial refactoring
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).parent.parent.parent.parent))
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

        for symbol in symbols:
            try:
                df = self._fetch_single_symbol(symbol, start_date, end_date, data_category, policy, source_id)
                if df is not None and not df.empty:
                    results[symbol] = df
                else:
                    logger.warning(f"获取数据为空: {symbol}")

            except Exception as e:
                logger.error(f"获取数据失败: {symbol}, 错误: {str(e)}")
                # 记录失败，但不中断批量过程
                continue

        return results

    def _fetch_single_symbol(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        data_category: str,
        policy: RoutePolicy,
        source_id: Optional[str],
    ) -> Optional[pd.DataFrame]:
        """获取单个股票数据"""

        endpoint = None

        if policy == RoutePolicy.SMART_ROUTING:
            # 使用 V2 的智能路由（默认逻辑）
            endpoint = self.manager.get_best_endpoint(data_category)

        elif policy == RoutePolicy.SPECIFIC_SOURCE:
            if not source_id:
                raise ValueError("指定源策略必须提供 source_id")
            # 查找特定源
            endpoints = self.manager.find_endpoints(data_category=data_category, source_type=source_id)
            if endpoints:
                endpoint = endpoints[0]

        elif policy == RoutePolicy.FASTEST:
            # 自定义路由：找响应时间最短的
            endpoints = self.manager.find_endpoints(data_category=data_category, only_healthy=True)
            if endpoints:
                # 假设 endpoint 字典里有 avg_response_time
                endpoints.sort(key=lambda x: x.get("avg_response_time", 999))
                endpoint = endpoints[0]

        elif policy == RoutePolicy.STABLE:
            # 自定义路由：找成功率最高的
            endpoints = self.manager.find_endpoints(data_category=data_category, only_healthy=True)
            if endpoints:
                endpoints.sort(key=lambda x: -x.get("success_rate", 0))
                endpoint = endpoints[0]

        if not endpoint:
            logger.warning(f"未找到可用的数据端点: category={data_category}, policy={policy}")
            return None

        # 调用 V2 的内部方法 _call_endpoint
        # 注意：这里我们访问了 protected method，这是为了实现高级路由
        # 在未来的重构中，应该在 DataSourceManagerV2 中暴露更灵活的接口
        logger.info(f"使用端点: {endpoint['endpoint_name']} 获取 {symbol}")

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
