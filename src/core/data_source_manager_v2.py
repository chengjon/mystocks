"""
# 功能：数据源管理器主文件（向后兼容）
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：2.0.0（重构版本）
# 说明：本文件提供向后兼容的导入接口，所有实现已拆分到data_source/子模块
#
# 重构说明：
#   - 原文件776行已拆分为8个子模块
#   - 最大子模块：176行
#   - 主文件：本文件（向后兼容层）
#
# 子模块：
#   - base.py: DataSourceManagerV2基类、初始化逻辑
#   - registry.py: 数据源注册（从数据库和YAML加载）
#   - router.py: 数据源路由（查找最佳endpoint）
#   - handler.py: 数据调用处理（各种API handler）
#   - monitoring.py: 监控记录（成功/失败记录、调用历史）
#   - health_check.py: 健康检查（单个和批量endpoint检查）
#   - validation.py: 数据验证
#   - cache.py: LRUCache类
#
# 向后兼容：
#   本文件从data_source/__init__.py导入并重新导出主类
#   确保旧代码可以继续使用：from src.core.data_source_manager_v2 import DataSourceManagerV2
"""

# 从子模块导入主类
from src.core.data_source import DataSourceManagerV2, LRUCache

# 向后兼容：重新导出所有旧接口
__all__ = [
    "DataSourceManagerV2",
    "LRUCache",
]
