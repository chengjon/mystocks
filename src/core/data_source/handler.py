import logging
import time
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def get_best_endpoint(self, data_category: str, exclude_failed: bool = True) -> Optional[Dict]:
    """
    获取最佳数据端点（智能路由）

    选择标准：
    1. 状态为active
    2. 健康状态为healthy或degraded（可选排除failed）
    3. 按优先级排序
    4. 同优先级按质量评分排序

    Args:
        data_category: 数据分类（如 DAILY_KLINE）
        exclude_failed: 是否排除失败状态的接口

    Returns:
        最佳端点配置，如果没有可用端点则返回None

    示例:
        best = manager.get_best_endpoint("DAILY_KLINE")
        if best:
            print(f"最佳接口: {best['endpoint_name']}, 评分: {best['quality_score']}")
    """
    endpoints = self.find_endpoints(data_category=data_category, only_healthy=exclude_failed)

    return endpoints[0] if endpoints else None


def list_all_endpoints(self) -> pd.DataFrame:
    """
    列出所有已注册的数据端点（便于查看和管理）

    Returns:
        包含所有端点信息的DataFrame
    """
    data = []

    for endpoint_name, source in self.registry.items():
        config = source["config"]

        data.append(
            {
                "数据源": config.get("source_name"),
                "端点名称": endpoint_name,
                "数据分类": config.get("data_category"),
                "分类层级": config.get("classification_level"),
                "目标数据库": config.get("target_db"),
                "目标表": config.get("table_name"),
                "更新频率": config.get("update_frequency", ""),
                "质量评分": config.get("data_quality_score"),
                "优先级": config.get("priority"),
                "状态": config.get("status"),
                "健康状态": config.get("health_status"),
                "成功率": f"{config.get('success_rate', 100):.1f}%",
                "平均响应时间": f"{config.get('avg_response_time', 0):.2f}s",
                "调用次数": config.get("total_calls", 0),
                "失败次数": config.get("failed_calls", 0),
                "连续失败": config.get("consecutive_failures", 0),
                "最后成功": config.get("last_success_time"),
                "版本": config.get("version", ""),
                "标签": ",".join(config.get("tags", [])),
            }
        )

    return pd.DataFrame(data)


# ==========================================================================
# 高层业务接口（向后兼容）
# ==========================================================================


def get_stock_daily(
    self, symbol: str, start_date: str = None, end_date: str = None, adjust: str = "qfq"
) -> pd.DataFrame:
    """
    获取日线数据（高层业务接口）

    内部逻辑：
    1. 查询DAILY_KLINE分类下的最佳接口
    2. 调用该接口
    3. 如果失败，按优先级尝试备用接口
    4. 记录调用历史

    Args:
        symbol: 股票代码
        start_date: 开始日期（YYYYMMDD）
        end_date: 结束日期（YYYYMMDD）
        adjust: 复权类型（qfq=前复权, hfq=后复权）

    Returns:
        日线数据DataFrame

    示例:
        manager = DataSourceManagerV2()
        data = manager.get_stock_daily(symbol="000001", start_date="20240101")
    """
    # 获取最佳接口
    best_endpoint = self.get_best_endpoint("DAILY_KLINE")

    if not best_endpoint:
        raise ValueError("没有可用的日线数据接口")

    logger.info("使用接口: %s", best_endpoint.get('name', 'unknown'))

    # 调用接口（根据数据源类型适配参数）
    return self._call_endpoint(best_endpoint, symbol=symbol, start_date=start_date, end_date=end_date, adjust=adjust)


def get_stock_realtime(self, symbols: List[str]) -> pd.DataFrame:
    """获取实时行情（高层业务接口）"""
    best_endpoint = self.get_best_endpoint("REALTIME_QUOTE")

    if not best_endpoint:
        raise ValueError("没有可用的实时行情接口")

    return self._call_endpoint(best_endpoint, symbols=symbols)


def get_stock_symbols(self) -> pd.DataFrame:
    """获取股票代码列表（高层业务接口）"""
    best_endpoint = self.get_best_endpoint("SYMBOLS_INFO")

    if not best_endpoint:
        raise ValueError("没有可用的股票代码接口")

    return self._call_endpoint(best_endpoint)


# ==========================================================================
# 内部调用方法
# ==========================================================================


def _call_endpoint(self, endpoint_info: Dict, **kwargs) -> pd.DataFrame:
    """
    调用具体的数据端点

    Args:
        endpoint_info: 端点信息（从find_endpoints或get_best_endpoint获取）
        **kwargs: 调用参数

    Returns:
        数据DataFrame
    """
    endpoint_name = endpoint_info["endpoint_name"]
    endpoint_info["source_type"]

    # 获取或创建handler
    source = self.registry.get(endpoint_name)
    if not source:
        raise ValueError(f"端点 {endpoint_name} 未注册")

    # 延迟创建handler
    if source["handler"] is None:
        source["handler"] = self._create_handler(endpoint_info)

    handler = source["handler"]

    # 记录调用开始时间
    start_time = time.time()
    caller = self._identify_caller()

    try:
        # 调用handler
        data = handler.fetch(**kwargs)

        # 记录成功
        response_time = time.time() - start_time
        self._record_success(endpoint_name, response_time, len(data), caller)

        return data

    except Exception as e:
        # 记录失败
        response_time = time.time() - start_time
        error_msg = str(e)
        self._record_failure(endpoint_name, response_time, error_msg, caller)

        logger.error("调用接口失败: %(endpoint_name)s, 错误: %(error_msg)s")
        raise
