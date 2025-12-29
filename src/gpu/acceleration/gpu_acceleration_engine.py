#!/usr/bin/env python3
"""
# 功能：GPU加速引擎 - 统一入口点
# 作者：MyStocks AI开发团队
# 创建日期：2025-12-20
# 版本：2.0.0 (重构版本)
# 说明：GPU加速引擎的统一管理和调度接口
"""

import time
import logging
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np

# 导入模块化组件
from .backtest_engine_gpu import BacktestEngineGPU
from .ml_training_gpu import MLTrainingGPU
from .feature_calculation_gpu import FeatureCalculationGPU
from .optimization_gpu import OptimizationGPU

# 导入GPU管理器
try:
    from src.gpu.core.hardware_abstraction.resource_manager import GPUResourceManager

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

logger = logging.getLogger(__name__)


class GPUAccelerationEngine:
    """GPU加速引擎 - 统一管理接口

    重构改进:
    ✅ 原文件1,220行 → 模块化为4个专门模块
    ✅ 功能分离：回测引擎、ML训练、特征计算、参数优化
    ✅ 统一的资源管理和性能监控
    ✅ 完整的向后兼容性
    ✅ 增强的错误处理和回退机制
    """

    def __init__(self, enable_gpu: bool = True, config: Optional[Dict[str, Any]] = None):
        """初始化GPU加速引擎

        Args:
            enable_gpu: 是否启用GPU加速
            config: 配置参数字典
        """
        self.config = config or self._get_default_config()
        self.enable_gpu = enable_gpu and GPU_AVAILABLE

        # 初始化GPU资源管理器
        self.gpu_manager = None
        if self.enable_gpu:
            try:
                self.gpu_manager = GPUResourceManager()
                logger.info("✅ GPU资源管理器初始化成功")
            except Exception as e:
                logger.warning("GPU资源管理器初始化失败，将使用CPU模式: %s", e)
                self.enable_gpu = False
                self.gpu_manager = None
        else:
            logger.info("使用CPU模式")

        # 初始化子引擎
        self._initialize_sub_engines()

        # 性能监控
        self.performance_metrics = {
            "total_operations": 0,
            "gpu_operations": 0,
            "cpu_operations": 0,
            "total_gpu_time": 0.0,
            "total_cpu_time": 0.0,
            "gpu_memory_peak": 0.0,
        }

        logger.info("✅ GPU加速引擎初始化完成 (GPU模式: %s)", self.enable_gpu)

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "memory_threshold_mb": 8192,  # 8GB
            "max_concurrent_operations": 4,
            "enable_cache": True,
            "cache_size_limit": 1000,
            "fallback_to_cpu": True,
            "performance_monitoring": True,
            "log_level": "INFO",
        }

    def _initialize_sub_engines(self) -> None:
        """初始化子引擎"""
        try:
            # 回测引擎
            self.backtest_engine = BacktestEngineGPU(self.gpu_manager)

            # ML训练引擎
            self.ml_engine = MLTrainingGPU(self.gpu_manager)

            # 特征计算引擎
            self.feature_engine = FeatureCalculationGPU(self.gpu_manager)

            # 优化引擎
            self.optimization_engine = OptimizationGPU(self.gpu_manager)

            logger.info("✅ 所有子引擎初始化完成")

        except Exception as e:
            logger.error("子引擎初始化失败: %s", e)
            raise

    # 回测相关方法
    def run_backtest_gpu(
        self,
        data: pd.DataFrame,
        strategy_config: Dict[str, Any],
        initial_capital: float = 1000000,
        benchmark_data: Optional[pd.DataFrame] = None,
    ) -> Dict[str, Any]:
        """运行GPU加速回测

        Args:
            data: 包含OHLCV数据的DataFrame
            strategy_config: 策略配置
            initial_capital: 初始资金
            benchmark_data: 基准数据

        Returns:
            回测结果字典
        """
        operation_start = time.time()
        self.performance_metrics["total_operations"] += 1

        try:
            if self.enable_gpu:
                self.performance_metrics["gpu_operations"] += 1
                logger.info("开始GPU加速回测...")
            else:
                self.performance_metrics["cpu_operations"] += 1
                logger.info("开始CPU回测...")

            result = self.backtest_engine.run_backtest_gpu(data, strategy_config, initial_capital, benchmark_data)

            # 添加引擎级别信息
            result["engine_info"] = {
                "gpu_mode": self.enable_gpu,
                "computation_time": time.time() - operation_start,
                "gpu_memory_used": self.gpu_manager.get_gpu_memory_usage() if self.gpu_manager else 0,
            }

            # 更新性能指标
            if self.enable_gpu:
                self.performance_metrics["total_gpu_time"] += time.time() - operation_start

            logger.info("回测完成，总收益: %s", result.get("total_return", 0))
            return result

        except Exception as e:
            logger.error("回测执行失败: %s", e)
            return {
                "error": str(e),
                "status": "failed",
                "engine_info": {
                    "gpu_mode": self.enable_gpu,
                    "computation_time": time.time() - operation_start,
                },
            }

    # ML训练相关方法
    def train_model_gpu(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        model_type: str = "random_forest",
        params: Dict = None,
        validation_split: float = 0.2,
    ) -> Dict[str, Any]:
        """训练GPU加速模型

        Args:
            X_train: 训练特征数据
            y_train: 训练目标数据
            model_type: 模型类型
            params: 模型参数
            validation_split: 验证集比例

        Returns:
            训练结果字典
        """
        operation_start = time.time()
        self.performance_metrics["total_operations"] += 1

        try:
            if self.enable_gpu:
                self.performance_metrics["gpu_operations"] += 1
            else:
                self.performance_metrics["cpu_operations"] += 1

            result = self.ml_engine.train_model_gpu(X_train, y_train, model_type, params, validation_split)

            # 添加引擎级别信息
            result["engine_info"] = {
                "gpu_mode": self.enable_gpu,
                "computation_time": time.time() - operation_start,
                "gpu_memory_used": self.gpu_manager.get_gpu_memory_usage() if self.gpu_manager else 0,
            }

            # 更新性能指标
            if self.enable_gpu:
                self.performance_metrics["total_gpu_time"] += time.time() - operation_start

            logger.info("模型训练完成，验证得分: %s", result.get("val_score", 0))
            return result

        except Exception as e:
            logger.error("模型训练失败: %s", e)
            return {
                "error": str(e),
                "status": "failed",
                "engine_info": {
                    "gpu_mode": self.enable_gpu,
                    "computation_time": time.time() - operation_start,
                },
            }

    def predict_gpu(self, model_id: str, X_test: pd.DataFrame) -> np.ndarray:
        """GPU加速预测"""
        try:
            return self.ml_engine.predict_gpu(model_id, X_test)
        except Exception as e:
            logger.error("预测失败: %s", e)
            raise

    def evaluate_model_gpu(self, model_id: str, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        """评估GPU模型"""
        try:
            return self.ml_engine.evaluate_model_gpu(model_id, X_test, y_test)
        except Exception as e:
            logger.error("模型评估失败: %s", e)
            raise

    # 特征计算相关方法
    def calculate_features_gpu(self, data: pd.DataFrame, feature_types: List[str] = None) -> Dict[str, Any]:
        """GPU加速特征计算

        Args:
            data: 包含OHLCV数据的DataFrame
            feature_types: 要计算的特征类型列表

        Returns:
            特征计算结果字典
        """
        operation_start = time.time()
        self.performance_metrics["total_operations"] += 1

        try:
            if self.enable_gpu:
                self.performance_metrics["gpu_operations"] += 1
            else:
                self.performance_metrics["cpu_operations"] += 1

            result = self.feature_engine.calculate_features_gpu(data, feature_types)

            # 添加引擎级别信息
            if "metadata" in result:
                result["metadata"]["engine_gpu_mode"] = self.enable_gpu
                result["metadata"]["engine_computation_time"] = time.time() - operation_start

            # 更新性能指标
            if self.enable_gpu:
                self.performance_metrics["total_gpu_time"] += time.time() - operation_start

            logger.info("特征计算完成，%s 类特征", len(result.get("metadata", {}).get("feature_types", [])))
            return result

        except Exception as e:
            logger.error("特征计算失败: %s", e)
            return {
                "error": str(e),
                "engine_info": {
                    "gpu_mode": self.enable_gpu,
                    "computation_time": time.time() - operation_start,
                },
            }

    # 优化相关方法
    def optimize_parameters_gpu(
        self,
        objective_func,
        param_space: Dict,
        method: str = "grid_search",
        n_trials: int = 100,
        maximize: bool = True,
    ) -> Dict[str, Any]:
        """GPU加速参数优化

        Args:
            objective_func: 目标函数
            param_space: 参数空间
            method: 优化方法
            n_trials: 试验次数
            maximize: 是否最大化

        Returns:
            优化结果字典
        """
        operation_start = time.time()
        self.performance_metrics["total_operations"] += 1

        try:
            if self.enable_gpu:
                self.performance_metrics["gpu_operations"] += 1
            else:
                self.performance_metrics["cpu_operations"] += 1

            result = self.optimization_engine.optimize_parameters_gpu(
                objective_func, param_space, method, n_trials, maximize
            )

            # 添加引擎级别信息
            result["engine_info"] = {
                "gpu_mode": self.enable_gpu,
                "computation_time": time.time() - operation_start,
                "gpu_memory_used": self.gpu_manager.get_gpu_memory_usage() if self.gpu_manager else 0,
            }

            # 更新性能指标
            if self.enable_gpu:
                self.performance_metrics["total_gpu_time"] += time.time() - operation_start

            logger.info("参数优化完成，最佳得分: %s", result.get("best_score", 0))
            return result

        except Exception as e:
            logger.error("参数优化失败: %s", e)
            return {
                "error": str(e),
                "status": "failed",
                "engine_info": {
                    "gpu_mode": self.enable_gpu,
                    "computation_time": time.time() - operation_start,
                },
            }

    def optimize_portfolio_weights(
        self,
        returns: pd.DataFrame,
        method: str = "mean_variance",
        risk_free_rate: float = 0.02,
    ) -> Dict[str, Any]:
        """GPU加速投资组合优化"""
        try:
            result = self.optimization_engine.optimize_portfolio_weights(returns, method, risk_free_rate)
            result["engine_gpu_mode"] = self.enable_gpu
            return result
        except Exception as e:
            logger.error("投资组合优化失败: %s", e)
            return {"error": str(e), "method": method}

    # 综合分析方法
    def comprehensive_analysis_gpu(
        self,
        data: pd.DataFrame,
        strategy_config: Dict[str, Any],
        feature_types: List[str] = None,
        optimize_strategy: bool = True,
    ) -> Dict[str, Any]:
        """GPU加速综合分析

        Args:
            data: 市场数据
            strategy_config: 策略配置
            feature_types: 特征类型
            optimize_strategy: 是否优化策略参数

        Returns:
            综合分析结果
        """
        analysis_start = time.time()
        logger.info("开始GPU加速综合分析...")

        try:
            results = {}

            # 1. 特征计算
            if feature_types:
                logger.info("计算技术特征...")
                results["features"] = self.calculate_features_gpu(data, feature_types)

            # 2. 策略参数优化
            if optimize_strategy and "parameters" in strategy_config:
                logger.info("优化策略参数...")
                param_space = strategy_config["parameters"]

                def objective_func(params):
                    test_config = strategy_config.copy()
                    test_config["parameters"] = params
                    backtest_result = self.run_backtest_gpu(data, test_config)
                    return backtest_result.get("sharpe_ratio", -999)

                optimization_result = self.optimize_parameters_gpu(
                    objective_func, param_space, method="bayesian", n_trials=50
                )

                if "best_params" in optimization_result:
                    strategy_config["parameters"] = optimization_result["best_params"]
                    results["optimization"] = optimization_result

            # 3. 回测分析
            logger.info("执行回测分析...")
            results["backtest"] = self.run_backtest_gpu(data, strategy_config)

            # 4. 性能对比
            if "optimization" in results and "backtest" in results:
                results["performance_comparison"] = {
                    "optimization_improvement": (
                        results["backtest"]["sharpe_ratio"] - results["optimization"].get("best_score", 0)
                    ),
                    "total_analysis_time": time.time() - analysis_start,
                    "gpu_utilization": self.get_gpu_utilization(),
                }

            results["analysis_summary"] = {
                "total_time": time.time() - analysis_start,
                "gpu_mode": self.enable_gpu,
                "steps_completed": len(results),
                "success": True,
            }

            logger.info("综合分析完成，耗时: %ss", time.time() - analysis_start)
            return results

        except Exception as e:
            logger.error("综合分析失败: %s", e)
            return {
                "error": str(e),
                "analysis_summary": {
                    "total_time": time.time() - analysis_start,
                    "gpu_mode": self.enable_gpu,
                    "success": False,
                },
            }

    # 性能监控和状态查询
    def get_engine_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        try:
            gpu_memory = 0
            gpu_utilization = 0
            if self.gpu_manager:
                gpu_memory = self.gpu_manager.get_gpu_memory_usage()
                gpu_utilization = self.gpu_manager.get_gpu_utilization()

            return {
                "gpu_enabled": self.enable_gpu,
                "gpu_manager_available": self.gpu_manager is not None,
                "gpu_memory_used_mb": gpu_memory,
                "gpu_utilization_percent": gpu_utilization,
                "performance_metrics": self.performance_metrics.copy(),
                "sub_engines": {
                    "backtest_engine": self.backtest_engine is not None,
                    "ml_engine": self.ml_engine is not None,
                    "feature_engine": self.feature_engine is not None,
                    "optimization_engine": self.optimization_engine is not None,
                },
                "cache_info": self._get_cache_info(),
                "config": self.config,
            }

        except Exception as e:
            logger.error("获取引擎状态失败: %s", e)
            return {"error": str(e), "gpu_enabled": self.enable_gpu}

    def get_gpu_utilization(self) -> Dict[str, Any]:
        """获取GPU利用率信息"""
        if not self.gpu_manager:
            return {"available": False, "message": "GPU管理器不可用"}

        try:
            return {
                "available": True,
                "memory_used_mb": self.gpu_manager.get_gpu_memory_usage(),
                "utilization_percent": self.gpu_manager.get_gpu_utilization(),
                "temperature": getattr(self.gpu_manager, "get_gpu_temperature", lambda: 0)(),
                "power_usage": getattr(self.gpu_manager, "get_gpu_power_usage", lambda: 0)(),
            }
        except Exception as e:
            return {"available": True, "error": str(e)}

    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        gpu_time = self.performance_metrics["total_gpu_time"]
        cpu_time = self.performance_metrics["total_cpu_time"]
        total_time = gpu_time + cpu_time

        efficiency = 0
        if total_time > 0:
            efficiency = gpu_time / total_time * 100

        return {
            "total_operations": self.performance_metrics["total_operations"],
            "gpu_operations": self.performance_metrics["gpu_operations"],
            "cpu_operations": self.performance_metrics["cpu_operations"],
            "total_gpu_time": gpu_time,
            "total_cpu_time": cpu_time,
            "gpu_efficiency_percent": efficiency,
            "average_gpu_operation_time": (
                gpu_time / self.performance_metrics["gpu_operations"]
                if self.performance_metrics["gpu_operations"] > 0
                else 0
            ),
            "average_cpu_operation_time": (
                cpu_time / self.performance_metrics["cpu_operations"]
                if self.performance_metrics["cpu_operations"] > 0
                else 0
            ),
        }

    def _get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        try:
            cache_info = {}
            if hasattr(self.feature_engine, "get_cache_info"):
                cache_info["feature_engine"] = self.feature_engine.get_cache_info()
            if hasattr(self.optimization_engine, "get_cache_info"):
                cache_info["optimization_engine"] = self.optimization_engine.get_cache_info()
            if hasattr(self.ml_engine, "list_models"):
                cache_info["ml_engine"] = {"models_count": len(self.ml_engine.list_models())}

            return cache_info
        except Exception as e:
            logger.error("获取缓存信息失败: %s", e)
            return {"error": str(e)}

    # 缓存管理
    def clear_all_caches(self) -> None:
        """清除所有缓存"""
        try:
            if hasattr(self.feature_engine, "clear_cache"):
                self.feature_engine.clear_cache()
            if hasattr(self.optimization_engine, "clear_cache"):
                self.optimization_engine.clear_cache()

            logger.info("所有缓存已清除")

        except Exception as e:
            logger.error("清除缓存失败: %s", e)

    def reset_performance_metrics(self) -> None:
        """重置性能指标"""
        self.performance_metrics = {
            "total_operations": 0,
            "gpu_operations": 0,
            "cpu_operations": 0,
            "total_gpu_time": 0.0,
            "total_cpu_time": 0.0,
            "gpu_memory_peak": 0.0,
        }
        logger.info("性能指标已重置")

    # 资源管理
    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()

    def cleanup(self) -> None:
        """清理资源"""
        try:
            if self.gpu_manager:
                # 清理GPU资源
                self.gpu_manager.cleanup()
                logger.info("GPU资源已清理")

            # 清理缓存
            self.clear_all_caches()

            # 重置性能指标
            self.reset_performance_metrics()

        except Exception as e:
            logger.error("资源清理失败: %s", e)

    # 兼容性方法（保持向后兼容）
    def run_ml_training(self, *args, **kwargs):
        """向后兼容的ML训练方法"""
        return self.train_model_gpu(*args, **kwargs)

    def calculate_features(self, *args, **kwargs):
        """向后兼容的特征计算方法"""
        return self.calculate_features_gpu(*args, **kwargs)

    def run_optimization(self, *args, **kwargs):
        """向后兼容的优化方法"""
        return self.optimize_parameters_gpu(*args, **kwargs)

    def run_backtest(self, *args, **kwargs):
        """向后兼容的回测方法"""
        return self.run_backtest_gpu(*args, **kwargs)
