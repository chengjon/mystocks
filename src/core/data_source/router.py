from typing import List, Dict, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def find_endpoints(self, **kwargs) -> List[Dict]:
    """
    查找满足条件的数据端点

    Args:
        **kwargs: 筛选条件
            - data_category: 数据分类
            - source_name: 数据源名称
            - target_db: 目标数据库
            - only_healthy: 只返回健康的端点

    Returns:
        端点列表，按优先级和质量评分排序
    """
    data_category = kwargs.get("data_category")
    source_name = kwargs.get("source_name")
    target_db = kwargs.get("target_db")
    only_healthy = kwargs.get("only_healthy", True)

    results = []
    for endpoint_name, source in self.registry.items():
        config = source["config"]

        # 数据分类筛选
        if data_category and config.get("data_category") != data_category:
            continue

        # 数据源筛选
        if source_name and config.get("source_name") != source_name:
            continue

        # 目标数据库筛选
        if target_db and config.get("target_db") != target_db:
            continue

        # 健康状态筛选
        if only_healthy:
            health_status = config.get("health_status", "unknown")
            if health_status == "failed":
                continue

        results.append({"endpoint_name": endpoint_name, "config": config})

    # 排序：优先级升序，质量评分降序
    results.sort(key=lambda x: (x["config"].get("priority", 999), -x["config"].get("data_quality_score", 0)))

    return results


def get_best_endpoint(self, data_category: str) -> Optional[Dict]:
    """
    获取最佳数据端点（智能路由）

    Args:
        data_category: 数据分类（如 DAILY_KLINE）

    Returns:
        最佳端点配置，如果没有可用端点则返回None
    """
    endpoints = self.find_endpoints(data_category=data_category, only_healthy=True)
    return endpoints[0] if endpoints else None


def list_all_endpoints(self) -> pd.DataFrame:
    """
    列出所有已注册的数据端点

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
