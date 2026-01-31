"""
风险管理初始化模块
Risk Management Initialization Module

将所有风险管理组件集成到统一的初始化系统中。
复用现有的异步事件总线和监控基础设施。
"""

import logging
from typing import Optional

from src.governance.risk_management.calculators.gpu_calculator import get_gpu_risk_calculator
from src.governance.risk_management.core import RiskManagementCore
from src.governance.risk_management.services.alert_service import get_risk_alert_service
from src.governance.risk_management.services.stop_loss_engine import get_stop_loss_engine

logger = logging.getLogger(__name__)


class RiskManagementInitializer:
    """
    风险管理初始化器

    负责初始化和协调所有风险管理组件。
    提供统一的启动和关闭接口。
    """

    def __init__(self):
        self.core = None
        self.is_initialized = False

    async def initialize(self) -> RiskManagementCore:
        """
        初始化风险管理系统

        按顺序初始化各个组件，确保依赖关系正确。
        """
        try:
            logger.info("🚀 开始初始化风险管理系统...")

            # 1. 创建核心实例
            self.core = RiskManagementCore()
            logger.info("✅ 风险管理核心创建成功")

            # 2. 初始化GPU计算器
            gpu_calculator = get_gpu_risk_calculator()
            logger.info("✅ GPU风险计算器初始化成功")

            # 3. 初始化止损引擎
            stop_loss_engine = get_stop_loss_engine()
            logger.info("✅ 止损引擎初始化成功")

            # 4. 初始化告警服务
            alert_service = get_risk_alert_service()
            logger.info("✅ 风险告警服务初始化成功")

            # 5. 组装核心系统
            await self.core.initialize()

            # 6. 设置组件依赖
            self.core.risk_calculator = gpu_calculator
            self.core.stop_loss_engine = stop_loss_engine
            self.core.alert_service = alert_service

            self.is_initialized = True
            logger.info("🎉 风险管理系统初始化完成！")

            return self.core

        except Exception as e:
            logger.error("❌ 风险管理系统初始化失败: %(e)s")
            self.is_initialized = False
            raise

    async def shutdown(self):
        """关闭风险管理系统"""
        try:
            logger.info("🔄 开始关闭风险管理系统...")

            # 这里可以添加清理逻辑
            # 比如停止监控任务、清理缓存等

            self.is_initialized = False
            logger.info("✅ 风险管理系统已关闭")

        except Exception as e:
            logger.error("❌ 关闭风险管理系统时出错: %(e)s")

    def get_core(self) -> Optional[RiskManagementCore]:
        """获取风险管理核心实例"""
        return self.core

    def is_ready(self) -> bool:
        """检查系统是否就绪"""
        return self.is_initialized and self.core is not None


# 全局初始化器实例
_initializer_instance: Optional[RiskManagementInitializer] = None


def get_risk_management_initializer() -> RiskManagementInitializer:
    """获取风险管理初始化器实例（单例模式）"""
    global _initializer_instance
    if _initializer_instance is None:
        _initializer_instance = RiskManagementInitializer()
    return _initializer_instance


async def initialize_risk_management_system() -> RiskManagementCore:
    """
    初始化风险管理系统 (便捷函数)

    这是外部调用的主要入口点。
    """
    initializer = get_risk_management_initializer()
    return await initializer.initialize()


async def shutdown_risk_management_system():
    """关闭风险管理系统 (便捷函数)"""
    initializer = get_risk_management_initializer()
    await initializer.shutdown()


def get_risk_management_core() -> Optional[RiskManagementCore]:
    """获取风险管理核心实例 (便捷函数)"""
    initializer = get_risk_management_initializer()
    return initializer.get_core()


def is_risk_management_ready() -> bool:
    """检查风险管理系统是否就绪 (便捷函数)"""
    initializer = get_risk_management_initializer()
    return initializer.is_ready()
