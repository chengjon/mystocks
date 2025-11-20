"""
Mock数据模块 - MyStocks Web Backend

提供基于环境变量的Mock数据系统，支持开发、测试和演示需求。
通过统一Mock数据管理器提供数据源切换功能。

作者: Claude Code
生成时间: 2025-11-13
"""

# 导入统一Mock数据管理器
from .unified_mock_data import (
    UnifiedMockDataManager,
    get_mock_data_manager,
    get_dashboard_data,
    get_stocks_data,
    get_technical_data,
    get_wencai_data,
    get_strategy_data,
    get_monitoring_data,
    data_source_toggle,
)

# 便利导出
__all__ = [
    'UnifiedMockDataManager',
    'get_mock_data_manager',
    'get_dashboard_data',
    'get_stocks_data',
    'get_technical_data',
    'get_wencai_data',
    'get_strategy_data',
    'get_monitoring_data',
    'data_source_toggle',
]