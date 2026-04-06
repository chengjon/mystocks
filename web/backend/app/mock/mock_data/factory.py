"""Mock 数据子模块"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)



class _FallbackMockDataManager:
    """兜底 Mock 管理器，确保存在 get_data 接口。"""

    def __init__(self, reason: str = ""):
        self.reason = reason
        logger.warning("使用 FallbackMockDataManager，原因: %s", reason)

    def get_data(self, *args, **kwargs):
        return {}


def _is_valid_manager(manager: Any) -> bool:
    """校验管理器是否具备可调用的 get_data 接口。"""
    return callable(getattr(manager, "get_data", None))


def get_mock_data_manager() -> 'UnifiedMockDataManager':
    """获取Mock数据管理器实例"""
    try:
        from app.mock.mock_data import UnifiedMockDataManager

        # 尝试从全局模块缓存获取实例
        import sys

        main_module = sys.modules.get('app.mock.mock_data')
        if main_module and hasattr(main_module, 'mock_data_manager'):
            cached_manager = getattr(main_module, 'mock_data_manager')
            logger.info(
                "使用缓存 mock_data_manager: type=%s module=%s",
                type(cached_manager).__name__,
                getattr(type(cached_manager), "__module__", "unknown"),
            )
            if _is_valid_manager(cached_manager):
                return cached_manager
            logger.error(
                "缓存 mock_data_manager 无有效 get_data: type=%s module=%s",
                type(cached_manager).__name__,
                getattr(type(cached_manager), "__module__", "unknown"),
            )

        # 创建新实例
        manager = UnifiedMockDataManager()
        logger.info(
            "创建 UnifiedMockDataManager: type=%s module=%s",
            type(manager).__name__,
            getattr(type(manager), "__module__", "unknown"),
        )
        if _is_valid_manager(manager):
            return manager

        logger.error(
            "UnifiedMockDataManager 缺少有效 get_data: type=%s module=%s",
            type(manager).__name__,
            getattr(type(manager), "__module__", "unknown"),
        )
    except Exception as e:
        logger.exception("获取 Mock 数据管理器失败，将使用 fallback: %s", e)
        return _FallbackMockDataManager(reason=str(e))

    return _FallbackMockDataManager(reason="invalid manager without callable get_data")


# 便利函数
def get_dashboard_data() -> Dict[str, Any]:
    """获取Dashboard数据"""
    manager = get_mock_data_manager()
    return manager.get_data("dashboard") if hasattr(manager, 'get_data') else {}


def get_stocks_data(page: int = 1, page_size: int = 20, exchange: str = "all") -> Dict[str, Any]:
    """获取股票数据"""
    manager = get_mock_data_manager()
    return manager.get_data("stocks", page=page, page_size=page_size, exchange=exchange) if hasattr(manager, 'get_data') else {}


def get_technical_data(symbol: str = None, symbols: List[str] = None) -> Dict[str, Any]:
    """获取技术指标数据"""
    manager = get_mock_data_manager()
    return manager.get_data("technical", symbol=symbol, symbols=symbols) if hasattr(manager, 'get_data') else {}


def get_wencai_data(query_name: str = "all") -> Dict[str, Any]:
    """获取问财数据"""
    manager = get_mock_data_manager()
    return manager.get_data("wencai", query_name=query_name) if hasattr(manager, 'get_data') else {}


def get_strategy_data(action: str = "list", **kwargs) -> Dict[str, Any]:
    """获取策略数据"""
    manager = get_mock_data_manager()
    return manager.get_data("strategy", action=action, **kwargs) if hasattr(manager, 'get_data') else {}


def get_monitoring_data(alert_type: str = "all") -> Dict[str, Any]:
    """获取监控数据"""
    manager = get_mock_data_manager()
    return manager.get_data("monitoring", alert_type=alert_type) if hasattr(manager, 'get_data') else {}


def get_backtest_data(**kwargs) -> Dict[str, Any]:
    """Get mock backtest data"""
    manager = get_mock_data_manager()
    return manager.get_data("backtest", **kwargs) if hasattr(manager, 'get_data') else {}


# 数据源切换装饰器
def data_source_toggle(func):
    """数据源切换装饰器"""

    def wrapper(*args, **kwargs):
        try:
            # 尝试使用真实数据
            return func(*args, **kwargs)
        except NotImplementedError:
            # 如果真实数据不可用，降级到Mock数据
            logger.warning("数据源切换: {func.__name__} 降级到Mock数据")
            mock_manager = get_mock_data_manager()
            mock_manager.set_mock_mode(True)

            # 重新尝试调用原始函数
            return func(*args, **kwargs)

    return wrapper


if __name__ == "__main__":
    # 测试代码
    manager = UnifiedMockDataManager(use_mock_data=True)

    # 测试获取Dashboard数据
    dashboard_data = manager.get_data("dashboard")
    print("Dashboard数据测试:")
    print(f"市场概览: {dashboard_data['market_overview']['indices_count']} 个指数")
    print(f"市场统计: {dashboard_data['market_stats']['total_market_cap']}")

    # 测试获取股票数据
    stocks_data = manager.get_data("stocks", page=1, page_size=5)
    print(f"\n股票数据测试: 页面 {stocks_data['page']}, 总计 {stocks_data['total']} 条记录")

    # 测试获取自选股数据
    watchlist_data = manager.get_data("watchlist", user_id=1)
    print(f"\n自选股数据测试: {len(watchlist_data)} 只股票")

    # 获取缓存信息
    cache_info = manager.get_cache_info()
    print(f"\n缓存信息: {cache_info}")
