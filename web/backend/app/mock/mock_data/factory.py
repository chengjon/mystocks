"""Mock 数据子模块"""

import logging
import random
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from typing import Callable, TYPE_CHECKING

def get_mock_data_manager() -> 'UnifiedMockDataManager':
    """获取Mock数据管理器实例"""
    try:
        from app.mock.mock_data import UnifiedMockDataManager
        # 尝试从全局获取实例，如果不存在则创建
        import sys
        main_module = sys.modules.get('app.mock.mock_data')
        if main_module and hasattr(main_module, 'mock_data_manager'):
            return main_module.mock_data_manager
        return UnifiedMockDataManager()
    except Exception:
        # 兜底返回一个带有 get_data 方法的对象，避免崩溃
        class Fallback:
            def get_data(self, *args, **kwargs): return {}
        return Fallback()


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
