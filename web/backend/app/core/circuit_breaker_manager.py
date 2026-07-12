"""P0 Task 3: CircuitBreaker管理器

统一管理所有外部API调用的熔断器实例
遵循单例模式，确保全局唯一的熔断器实例
"""

import logging
from typing import Dict, Optional

from app.core.error_handling import CircuitBreaker


logger = logging.getLogger(__name__)


class CircuitBreakerManager:
    """熔断器管理器 - 单例模式

    管理所有外部API服务的熔断器实例：
    - market_data: 市场数据API
    - technical_analysis: 技术分析API
    - stock_search: 股票搜索API
    - data_source_factory: 数据源工厂
    - external_api: 其他外部API
    """

    _instance: Optional["CircuitBreakerManager"] = None
    _circuit_breakers: Dict[str, CircuitBreaker] = {}

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化熔断器管理器"""
        if self._initialized:
            return

        logger.info("🔧 Initializing CircuitBreaker Manager")

        # 初始化核心API的熔断器
        # 参数: 名称, 失败阈值, 恢复超时(秒), 成功阈值
        self._circuit_breakers = {
            # 市场数据API - 高频调用，失败阈值5次，60秒恢复超时
            "market_data": CircuitBreaker(
                "market_data",
                failure_threshold=5,
                recovery_timeout=60,
                success_threshold=2,
            ),
            # 技术分析API - 计算密集，失败阈值10次，90秒恢复超时
            "technical_analysis": CircuitBreaker(
                "technical_analysis",
                failure_threshold=10,
                recovery_timeout=90,
                success_threshold=2,
            ),
            # 股票搜索API - 索引查询，失败阈值8次，45秒恢复超时
            "stock_search": CircuitBreaker(
                "stock_search",
                failure_threshold=8,
                recovery_timeout=45,
                success_threshold=2,
            ),
            # 数据源工厂 - 数据适配器，失败阈值7次，60秒恢复超时
            "data_source_factory": CircuitBreaker(
                "data_source_factory",
                failure_threshold=7,
                recovery_timeout=60,
                success_threshold=2,
            ),
            # 备用外部API - 通用熔断器
            "external_api": CircuitBreaker(
                "external_api",
                failure_threshold=5,
                recovery_timeout=120,
                success_threshold=2,
            ),
        }

        self._initialized = True
        logger.info("✅ CircuitBreaker Manager initialized with 5 circuit breakers")

    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """获取指定服务的熔断器

        Args:
            service_name: 服务名称
                - 'market_data': 市场数据
                - 'technical_analysis': 技术分析
                - 'stock_search': 股票搜索
                - 'data_source_factory': 数据源工厂
                - 'external_api': 其他外部API

        Returns:
            CircuitBreaker实例

        Raises:
            ValueError: 如果服务名称不存在

        """
        if service_name not in self._circuit_breakers:
            logger.warning("⚠️ Circuit breaker for '%(service_name)s' not found, using external_api")
            return self._circuit_breakers["external_api"]

        return self._circuit_breakers[service_name]

    def get_all_statuses(self) -> dict:
        """获取所有熔断器的状态

        Returns:
            {service_name: {state, failure_count, ...}, ...}

        """
        return {name: cb.get_status() for name, cb in self._circuit_breakers.items()}

    def reset_circuit_breaker(self, service_name: str) -> bool:
        """手动重置指定服务的熔断器

        Args:
            service_name: 服务名称

        Returns:
            是否成功重置

        """
        if service_name in self._circuit_breakers:
            cb = self._circuit_breakers[service_name]
            cb.failure_count = 0
            cb.success_count = 0
            cb.state = cb.state.__class__.CLOSED
            logger.info("🔄 Circuit breaker '%(service_name)s' reset to CLOSED")
            return True

        logger.warning("⚠️ Circuit breaker '%(service_name)s' not found")
        return False

    def reset_all_circuit_breakers(self) -> int:
        """重置所有熔断器

        Returns:
            重置的熔断器数量

        """
        count = 0
        for service_name in self._circuit_breakers:
            if self.reset_circuit_breaker(service_name):
                count += 1

        logger.info("🔄 Reset %(count)s circuit breakers")
        return count


# 全局单例实例
_circuit_breaker_manager: Optional[CircuitBreakerManager] = None


def get_circuit_breaker_manager() -> CircuitBreakerManager:
    """获取全局CircuitBreaker管理器实例"""
    global _circuit_breaker_manager
    if _circuit_breaker_manager is None:
        _circuit_breaker_manager = CircuitBreakerManager()
    return _circuit_breaker_manager


def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """便捷函数：获取指定服务的熔断器"""
    manager = get_circuit_breaker_manager()
    return manager.get_circuit_breaker(service_name)
