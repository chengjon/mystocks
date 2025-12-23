"""
# GPU加速引擎模块
# 作者：MyStocks AI开发团队
# 创建日期：2025-12-20
# 版本：2.0.0
# 说明：模块化的GPU加速管理系统
"""

from .backtest_engine_gpu import BacktestEngineGPU
from .ml_training_gpu import MLTrainingGPU
from .feature_calculation_gpu import FeatureCalculationGPU
from .optimization_gpu import OptimizationGPU
from .gpu_acceleration_engine import GPUAccelerationEngine

__all__ = [
    "BacktestEngineGPU",
    "MLTrainingGPU",
    "FeatureCalculationGPU",
    "OptimizationGPU",
    "GPUAccelerationEngine",
]

# 版本信息
__version__ = "2.0.0"
__author__ = "MyStocks AI开发团队"


# 模块级别的便捷函数
def create_backtest_engine(gpu_manager=None):
    """创建回测引擎的便捷函数"""
    return BacktestEngineGPU(gpu_manager)


def create_ml_engine(gpu_manager=None):
    """创建ML训练引擎的便捷函数"""
    return MLTrainingGPU(gpu_manager)


def create_feature_engine(gpu_manager=None):
    """创建特征计算引擎的便捷函数"""
    return FeatureCalculationGPU(gpu_manager)


def create_optimization_engine(gpu_manager=None):
    """创建优化引擎的便捷函数"""
    return OptimizationGPU(gpu_manager)


def create_gpu_acceleration_engine(enable_gpu=True, config=None):
    """创建GPU加速引擎的便捷函数"""
    return GPUAccelerationEngine(enable_gpu, config)
