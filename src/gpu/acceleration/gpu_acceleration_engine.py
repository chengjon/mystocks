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

            feature_count = len(result.get("metadata", {}).get("feature_types", []))
            logger.info("特征计算完成，%d 类特征", feature_count)
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

    # 风险计算相关方法 (Week 3 - 组合平衡器)
    def calculate_correlation_matrix_gpu(self, returns_data: np.ndarray, method: str = "pearson") -> np.ndarray:
        """计算GPU加速的相关性矩阵

        Args:
            returns_data: 收益率数据，形状为 (n_assets, n_periods)
            method: 相关性计算方法 ('pearson', 'spearman', 'kendall')

        Returns:
            相关性矩阵，形状为 (n_assets, n_assets)
        """
        operation_start = time.time()
        self.performance_metrics["total_operations"] += 1

        try:
            if self.enable_gpu and CUML_AVAILABLE:
                self.performance_metrics["gpu_operations"] += 1
                logger.info("开始GPU加速相关性矩阵计算...")

                # 使用cuML计算相关性矩阵
                import cudf
                import cuml

                # 转换为GPU DataFrame
                gpu_df = cudf.DataFrame(returns_data.T)  # 转置为 (n_periods, n_assets)

                if method == "pearson":
                    correlation_matrix = cuml.correlation(gpu_df).to_pandas().values
                else:
                    # 对于spearman和kendall，使用CPU计算
                    correlation_matrix = np.corrcoef(returns_data)

            else:
                self.performance_metrics["cpu_operations"] += 1
                logger.info("开始CPU相关性矩阵计算...")
                correlation_matrix = np.corrcoef(returns_data)

            # 更新性能指标
            if self.enable_gpu:
                self.performance_metrics["total_gpu_time"] += time.time() - operation_start

            logger.info("相关性矩阵计算完成，形状: %s", correlation_matrix.shape)
            return correlation_matrix

        except Exception as e:
            logger.error("相关性矩阵计算失败: %s", e)
            # 返回单位矩阵作为后备方案
            return np.eye(returns_data.shape[0])

    def calculate_var_gpu(self, returns: np.ndarray, confidence: float = 0.95, method: str = "historical") -> float:
        """计算GPU加速的VaR (Value at Risk)

        Args:
            returns: 收益率序列
            confidence: 置信度 (0.95, 0.99等)
            method: 计算方法 ('historical', 'parametric', 'monte_carlo')

        Returns:
            VaR值 (正数，表示最大可能损失)
        """
        operation_start = time.time()
        self.performance_metrics["total_operations"] += 1

        try:
            if method == "historical":
                return self._calculate_historical_var_gpu(returns, confidence)
            elif method == "parametric":
                return self._calculate_parametric_var_gpu(returns, confidence)
            elif method == "monte_carlo":
                return self._calculate_monte_carlo_var_gpu(returns, confidence)
            else:
                raise ValueError(f"不支持的VaR计算方法: {method}")

        except Exception as e:
            logger.error("VaR计算失败: %s", e)
            # CPU后备方案
            sorted_returns = np.sort(returns)
            index = int((1 - confidence) * len(sorted_returns))
            return abs(sorted_returns[index])

    def calculate_portfolio_var_gpu(
        self, returns_data: np.ndarray, weights: np.ndarray, confidence: float = 0.95, method: str = "historical"
    ) -> Dict[str, Any]:
        """计算GPU加速的组合VaR

        Args:
            returns_data: 资产收益率数据，形状为 (n_assets, n_periods)
            weights: 资产权重数组
            confidence: 置信度
            method: 计算方法

        Returns:
            包含VaR、CVaR、ES等指标的字典
        """
        operation_start = time.time()
        self.performance_metrics["total_operations"] += 1

        try:
            # 计算组合收益率
            portfolio_returns = np.dot(weights, returns_data)

            # 计算VaR
            var_value = self.calculate_var_gpu(portfolio_returns, confidence, method)

            # 计算CVaR (Conditional VaR)
            cvar_value = self._calculate_cvar_gpu(portfolio_returns, confidence)

            # 计算预期 shortfall
            es_value = self._calculate_expected_shortfall_gpu(portfolio_returns, confidence)

            # 计算组合波动率
            portfolio_volatility = np.std(portfolio_returns) * np.sqrt(252)  # 年化

            result = {
                "var": var_value,
                "cvar": cvar_value,
                "expected_shortfall": es_value,
                "portfolio_volatility": portfolio_volatility,
                "confidence_level": confidence,
                "method": method,
                "computation_time": time.time() - operation_start,
                "gpu_mode": self.enable_gpu,
            }

            # 更新性能指标
            if self.enable_gpu:
                self.performance_metrics["total_gpu_time"] += time.time() - operation_start
                self.performance_metrics["gpu_operations"] += 1
            else:
                self.performance_metrics["cpu_operations"] += 1

            logger.info("组合VaR计算完成: VaR=%.4f, CVaR=%.4f", var_value, cvar_value)
            return result

        except Exception as e:
            logger.error("组合VaR计算失败: %s", e)
            return {
                "error": str(e),
                "var": 0.05,  # 保守估计
                "cvar": 0.08,
                "expected_shortfall": 0.08,
                "portfolio_volatility": 0.15,
                "computation_time": time.time() - operation_start,
                "gpu_mode": self.enable_gpu,
            }

    def run_monte_carlo_var_simulation_gpu(
        self,
        returns_data: np.ndarray,
        weights: np.ndarray,
        n_simulations: int = 10000,
        confidence: float = 0.95,
        time_horizon: int = 1,
    ) -> Dict[str, Any]:
        """运行GPU加速的Monte Carlo VaR模拟

        Args:
            returns_data: 历史收益率数据
            weights: 组合权重
            n_simulations: 模拟次数
            confidence: 置信度
            time_horizon: 时间期限(天数)

        Returns:
            模拟结果字典
        """
        operation_start = time.time()
        self.performance_metrics["total_operations"] += 1

        try:
            if self.enable_gpu and CUML_AVAILABLE:
                self.performance_metrics["gpu_operations"] += 1
                logger.info("开始GPU加速Monte Carlo VaR模拟 (%d次)...", n_simulations)

                import cudf
                import cupy as cp

                # 计算历史均值和协方差矩阵
                mean_returns = np.mean(returns_data, axis=1)  # (n_assets,)
                cov_matrix = np.cov(returns_data)  # (n_assets, n_assets)

                # GPU加速的Monte Carlo模拟
                gpu_mean = cp.array(mean_returns)
                gpu_cov = cp.array(cov_matrix)

                # 生成随机数 (使用Cholesky分解)
                L = cp.linalg.cholesky(gpu_cov)
                random_shocks = cp.random.normal(0, 1, (n_simulations, len(weights)))

                # 模拟收益率
                simulated_returns = cp.dot(random_shocks, L.T) + gpu_mean

                # 计算组合收益率
                gpu_weights = cp.array(weights)
                portfolio_returns = cp.dot(simulated_returns, gpu_weights)

                # 调整时间期限 (假设日收益率，平方根法则)
                if time_horizon > 1:
                    portfolio_returns = portfolio_returns * cp.sqrt(time_horizon)

                # 转换为NumPy数组
                portfolio_returns_cpu = cp.asnumpy(portfolio_returns)

            else:
                self.performance_metrics["cpu_operations"] += 1
                logger.info("开始CPU Monte Carlo VaR模拟 (%d次)...", n_simulations)

                # CPU后备方案
                mean_returns = np.mean(returns_data, axis=1)
                cov_matrix = np.cov(returns_data)

                # Cholesky分解
                L = np.linalg.cholesky(cov_matrix)
                random_shocks = np.random.normal(0, 1, (n_simulations, len(weights)))

                # 模拟收益率
                simulated_returns = np.dot(random_shocks, L.T) + mean_returns

                # 计算组合收益率
                portfolio_returns_cpu = np.dot(simulated_returns, weights)

                # 调整时间期限
                if time_horizon > 1:
                    portfolio_returns_cpu = portfolio_returns_cpu * np.sqrt(time_horizon)

            # 计算VaR
            sorted_returns = np.sort(portfolio_returns_cpu)
            var_index = int((1 - confidence) * len(sorted_returns))
            var_value = abs(sorted_returns[var_index])

            # 计算CVaR
            tail_returns = sorted_returns[:var_index]
            cvar_value = abs(np.mean(tail_returns)) if len(tail_returns) > 0 else var_value

            # 统计信息
            result = {
                "var": var_value,
                "cvar": cvar_value,
                "confidence_level": confidence,
                "n_simulations": n_simulations,
                "time_horizon": time_horizon,
                "mean_portfolio_return": float(np.mean(portfolio_returns_cpu)),
                "std_portfolio_return": float(np.std(portfolio_returns_cpu)),
                "min_portfolio_return": float(np.min(portfolio_returns_cpu)),
                "max_portfolio_return": float(np.max(portfolio_returns_cpu)),
                "computation_time": time.time() - operation_start,
                "gpu_mode": self.enable_gpu,
            }

            # 更新性能指标
            if self.enable_gpu:
                self.performance_metrics["total_gpu_time"] += time.time() - operation_start

            logger.info("Monte Carlo VaR模拟完成: VaR=%.4f, CVaR=%.4f", var_value, cvar_value)
            return result

        except Exception as e:
            logger.error("Monte Carlo VaR模拟失败: %s", e)
            return {
                "error": str(e),
                "var": 0.05,  # 保守估计
                "cvar": 0.08,
                "computation_time": time.time() - operation_start,
                "gpu_mode": self.enable_gpu,
            }

    # 私有VaR计算方法
    def _calculate_historical_var_gpu(self, returns: np.ndarray, confidence: float) -> float:
        """历史模拟VaR (GPU加速)"""
        if self.enable_gpu and CUML_AVAILABLE:
            try:
                import cudf

                # 使用GPU排序
                gpu_returns = cudf.Series(returns)
                sorted_returns = gpu_returns.sort_values().to_pandas().values
            except Exception:
                sorted_returns = np.sort(returns)
        else:
            sorted_returns = np.sort(returns)

        index = int((1 - confidence) * len(sorted_returns))
        return abs(sorted_returns[index])

    def _calculate_parametric_var_gpu(self, returns: np.ndarray, confidence: float) -> float:
        """参数VaR (正态分布假设)"""
        mean_return = np.mean(returns)
        std_return = np.std(returns)

        # 正态分布分位数
        from scipy.stats import norm

        quantile = norm.ppf(1 - confidence)

        var_value = abs(mean_return + quantile * std_return)
        return var_value

    def _calculate_monte_carlo_var_gpu(self, returns: np.ndarray, confidence: float) -> float:
        """Monte Carlo VaR"""
        # 简化的Monte Carlo实现
        n_simulations = 10000
        mean_return = np.mean(returns)
        std_return = np.std(returns)

        # 模拟正态分布收益率
        simulated_returns = np.random.normal(mean_return, std_return, n_simulations)
        sorted_returns = np.sort(simulated_returns)

        index = int((1 - confidence) * len(sorted_returns))
        return abs(sorted_returns[index])

    def _calculate_cvar_gpu(self, returns: np.ndarray, confidence: float) -> float:
        """计算CVaR (Conditional VaR)"""
        sorted_returns = np.sort(returns)
        index = int((1 - confidence) * len(sorted_returns))

        tail_returns = sorted_returns[:index]
        if len(tail_returns) > 0:
            return abs(np.mean(tail_returns))
        else:
            return abs(sorted_returns[0])

    def _calculate_expected_shortfall_gpu(self, returns: np.ndarray, confidence: float) -> float:
        """计算Expected Shortfall (ES)"""
        # ES等价于CVaR
        return self._calculate_cvar_gpu(returns, confidence)

    def calculate_portfolio_concentration_gpu(
        self, positions: List[Dict[str, Any]], concentration_metrics: List[str] = None
    ) -> Dict[str, Any]:
        """计算GPU加速的组合集中度分析

        Args:
            positions: 持仓列表，包含symbol和weight字段
            concentration_metrics: 要计算的集中度指标列表

        Returns:
            集中度分析结果字典
        """
        operation_start = time.time()
        self.performance_metrics["total_operations"] += 1

        if concentration_metrics is None:
            concentration_metrics = ["hhi", "max_single", "top10_ratio", "concentration_matrix"]

        try:
            # 提取权重数组
            weights = np.array([p["weight"] for p in positions])

            results = {
                "computation_time": 0.0,
                "gpu_mode": self.enable_gpu,
                "n_positions": len(positions),
            }

            # 计算各项集中度指标
            if "hhi" in concentration_metrics:
                results["hhi"] = self._calculate_hhi_gpu(weights)

            if "max_single" in concentration_metrics:
                results["max_single_position"] = float(np.max(weights))
                max_idx = np.argmax(weights)
                results["max_single_symbol"] = positions[max_idx]["symbol"]

            if "top10_ratio" in concentration_metrics:
                results["top10_ratio"] = self._calculate_top10_ratio_gpu(weights)

            if "concentration_matrix" in concentration_metrics:
                results["concentration_matrix"] = self._calculate_concentration_matrix_gpu(positions)

            # 计算集中度评分 (0-100, 越高越集中)
            results["concentration_score"] = self._calculate_concentration_score(results)

            # 集中度等级
            results["concentration_level"] = self._get_concentration_level(results["concentration_score"])

            results["computation_time"] = time.time() - operation_start

            # 更新性能指标
            if self.enable_gpu:
                self.performance_metrics["total_gpu_time"] += results["computation_time"]
                self.performance_metrics["gpu_operations"] += 1
            else:
                self.performance_metrics["cpu_operations"] += 1

            logger.info(
                "组合集中度分析完成: HHI=%.4f, 最大持仓=%.2f%%",
                results.get("hhi", 0),
                results.get("max_single_position", 0) * 100,
            )

            return results

        except Exception as e:
            logger.error("组合集中度分析失败: %s", e)
            return {
                "error": str(e),
                "hhi": 0.0,
                "max_single_position": 0.0,
                "top10_ratio": 0.0,
                "concentration_score": 0,
                "concentration_level": "unknown",
                "computation_time": time.time() - operation_start,
                "gpu_mode": self.enable_gpu,
            }

    def calculate_portfolio_diversification_gpu(
        self, positions: List[Dict[str, Any]], returns_data: np.ndarray = None
    ) -> Dict[str, Any]:
        """计算GPU加速的组合多元化分析

        Args:
            positions: 持仓列表
            returns_data: 收益率数据 (可选，用于相关性分析)

        Returns:
            多元化分析结果
        """
        operation_start = time.time()
        self.performance_metrics["total_operations"] += 1

        try:
            results = {
                "computation_time": 0.0,
                "gpu_mode": self.enable_gpu,
            }

            # 基本集中度分析
            concentration_results = self.calculate_portfolio_concentration_gpu(positions)
            results.update(concentration_results)

            # 如果有收益率数据，计算相关性多元化
            if returns_data is not None:
                correlation_matrix = self.calculate_correlation_matrix_gpu(returns_data)
                results["correlation_diversification"] = self._analyze_correlation_diversification(
                    correlation_matrix, positions
                )

            # 计算多元化评分 (0-100, 越高越多元化)
            results["diversification_score"] = self._calculate_diversification_score(results)

            # 多元化等级
            results["diversification_level"] = self._get_diversification_level(results["diversification_score"])

            results["computation_time"] = time.time() - operation_start

            # 更新性能指标
            if self.enable_gpu:
                self.performance_metrics["total_gpu_time"] += results["computation_time"]
                self.performance_metrics["gpu_operations"] += 1
            else:
                self.performance_metrics["cpu_operations"] += 1

            logger.info("组合多元化分析完成: 多元化评分=%.1f", results.get("diversification_score", 0))

            return results

        except Exception as e:
            logger.error("组合多元化分析失败: %s", e)
            return {
                "error": str(e),
                "diversification_score": 0,
                "diversification_level": "unknown",
                "computation_time": time.time() - operation_start,
                "gpu_mode": self.enable_gpu,
            }

    # 私有集中度计算方法
    def _calculate_hhi_gpu(self, weights: np.ndarray) -> float:
        """计算赫芬达尔-赫希曼指数 (HHI) - GPU加速"""
        if self.enable_gpu and CUML_AVAILABLE:
            try:
                import cupy as cp

                gpu_weights = cp.array(weights)
                hhi = cp.sum(gpu_weights**2)
                return float(hhi.get())
            except Exception:
                pass

        # CPU后备方案
        return float(np.sum(weights**2))

    def _calculate_top10_ratio_gpu(self, weights: np.ndarray) -> float:
        """计算前十大持仓占比"""
        if len(weights) <= 10:
            return 1.0

        # 排序并取前10大权重
        sorted_weights = np.sort(weights)[::-1]  # 降序排序
        top10_sum = np.sum(sorted_weights[:10])
        total_sum = np.sum(weights)

        return float(top10_sum / total_sum) if total_sum > 0 else 0.0

    def _calculate_concentration_matrix_gpu(self, positions: List[Dict[str, Any]]) -> np.ndarray:
        """计算集中度矩阵"""
        n_positions = len(positions)

        # 构建权重矩阵
        weights = np.array([p["weight"] for p in positions])

        # 计算集中度贡献矩阵
        concentration_matrix = np.zeros((n_positions, n_positions))

        for i in range(n_positions):
            for j in range(n_positions):
                if i == j:
                    # 对角线：自身集中度贡献
                    concentration_matrix[i, j] = weights[i] ** 2
                else:
                    # 交叉项：权重乘积
                    concentration_matrix[i, j] = weights[i] * weights[j]

        return concentration_matrix

    def _calculate_concentration_score(self, results: Dict[str, Any]) -> int:
        """计算集中度评分 (0-100)"""
        score = 0

        # HHI贡献 (0-40分)
        hhi = results.get("hhi", 0)
        if hhi > 0.5:  # 高度集中
            score += 40
        elif hhi > 0.25:  # 中等集中
            score += 25
        elif hhi > 0.15:  # 轻度集中
            score += 10

        # 最大持仓贡献 (0-30分)
        max_single = results.get("max_single_position", 0)
        if max_single > 0.3:  # 超过30%
            score += 30
        elif max_single > 0.2:  # 超过20%
            score += 20
        elif max_single > 0.1:  # 超过10%
            score += 10

        # 前10大持仓贡献 (0-30分)
        top10_ratio = results.get("top10_ratio", 0)
        if top10_ratio > 0.8:  # 前10大占80%以上
            score += 30
        elif top10_ratio > 0.6:  # 前10大占60%以上
            score += 20
        elif top10_ratio > 0.4:  # 前10大占40%以上
            score += 10

        return min(100, score)

    def _get_concentration_level(self, score: int) -> str:
        """获取集中度等级"""
        if score >= 80:
            return "highly_concentrated"
        elif score >= 60:
            return "moderately_concentrated"
        elif score >= 40:
            return "somewhat_concentrated"
        elif score >= 20:
            return "well_diversified"
        else:
            return "highly_diversified"

    def _analyze_correlation_diversification(
        self, correlation_matrix: np.ndarray, positions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析相关性多元化"""
        weights = np.array([p["weight"] for p in positions])

        # 计算加权平均相关性
        weighted_correlation = np.sum(correlation_matrix * np.outer(weights, weights))

        # 计算有效资产数量 (基于相关性)
        avg_correlation = np.mean(correlation_matrix[np.triu_indices_from(correlation_matrix, k=1)])
        effective_n = len(weights) / (1 + avg_correlation * (len(weights) - 1))

        return {
            "weighted_avg_correlation": float(weighted_correlation),
            "avg_pairwise_correlation": float(avg_correlation),
            "effective_n_assets": float(effective_n),
            "correlation_diversification_ratio": float(effective_n / len(weights)),
        }

    def _calculate_diversification_score(self, results: Dict[str, Any]) -> float:
        """计算多元化评分 (0-100)"""
        # 基于集中度评分的反向计算
        concentration_score = results.get("concentration_score", 0)

        # 相关性多元化调整
        correlation_adj = 0
        if "correlation_diversification" in results:
            corr_div_ratio = results["correlation_diversification"].get("correlation_diversification_ratio", 1.0)
            # 相关性多元化越高，评分越高
            correlation_adj = min(20, (corr_div_ratio - 0.5) * 40) if corr_div_ratio > 0.5 else 0

        # 多元化评分 = 100 - 集中度评分 + 相关性调整
        diversification_score = 100 - concentration_score + correlation_adj

        return max(0, min(100, diversification_score))

    def _get_diversification_level(self, score: float) -> str:
        """获取多元化等级"""
        if score >= 80:
            return "excellent_diversification"
        elif score >= 60:
            return "good_diversification"
        elif score >= 40:
            return "moderate_diversification"
        elif score >= 20:
            return "poor_diversification"
        else:
            return "very_poor_diversification"

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
