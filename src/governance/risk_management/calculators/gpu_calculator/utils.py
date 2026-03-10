"""
GPU加速风险计算器
GPU-Accelerated Risk Calculator

扩展现有的GPU引擎，支持风险指标的高性能计算。
复用现有的GPU基础设施和数据源。
"""

import logging


from .gpu_risk_calculator import GPURiskCalculator

# 复用现有的GPU基础设施
try:
    from src.gpu.data_processor_factory import get_processor
    from src.monitoring.async_monitoring import MonitoringEventPublisher

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    get_processor = None
    MonitoringEventPublisher = None

# 风险监控缓存系统
try:
    from src.utils.cache_optimization_enhanced import get_enhanced_cache_manager

    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    get_enhanced_cache_manager = None

logger = logging.getLogger(__name__)

_gpu_risk_calculator_instance = None

def get_gpu_risk_calculator() -> GPURiskCalculator:
    """获取GPU风险计算器实例（单例模式）"""
    global _gpu_risk_calculator_instance
    if _gpu_risk_calculator_instance is None:
        _gpu_risk_calculator_instance = GPURiskCalculator()
    return _gpu_risk_calculator_instance

