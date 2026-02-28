#!/usr/bin/env python3
"""
# 功能：GPU加速优化引擎
# 作者：MyStocks AI开发团队
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：GPU加速的参数优化和超参数调优引擎
"""

import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd

try:
    import cupy as cp

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    from src.gpu.core.hardware_abstraction.resource_manager import GPUResourceManager
except ImportError:
    GPUResourceManager = Any

logger = logging.getLogger(__name__)


class OptimizationGPURiskParityOptimizationMixin:
    """OptimizationGPU 方法集 Part 2"""

    def _risk_parity_optimization_gpu(self, returns: pd.DataFrame) -> Dict[str, Any]:
        """GPU加速风险平价优化"""
        try:
            # 计算资产协方差矩阵
            if self.gpu_available:
                returns_gpu = cp.array(returns.values)
                cov_matrix = cp.cov(returns_gpu, rowvar=False)
            else:
                cov_matrix = returns.cov().values

            # 简化的风险平价：基于波动率的倒数
            if self.gpu_available:
                volatilities = cp.sqrt(cp.diag(cov_matrix))
            else:
                volatilities = np.sqrt(np.diag(cov_matrix))

            # 风险平价权重
            inv_vols = 1.0 / (volatilities.get() if self.gpu_available else volatilities)
            weights = inv_vols / np.sum(inv_vols)

            # 计算组合统计量
            if self.gpu_available:
                portfolio_variance = float(cp.dot(cp.dot(weights, cov_matrix), weights))
            else:
                portfolio_variance = np.dot(np.dot(weights, cov_matrix), weights)

            portfolio_std = np.sqrt(portfolio_variance)
            expected_return = float(returns.mean().dot(weights))

            return {
                "weights": weights.tolist(),
                "expected_return": expected_return,
                "volatility": portfolio_std,
                "method": "risk_parity",
            }

        except Exception as e:
            logger.error("风险平价优化失败: %s", e)
            return {"error": str(e)}

    def _max_sharpe_optimization_gpu(self, returns: pd.DataFrame, risk_free_rate: float) -> Dict[str, Any]:
        """GPU加速最大夏普比率优化"""
        # 简化实现：使用均值-方差结果
        result = self._mean_variance_optimization_gpu(returns, risk_free_rate)
        result["method"] = "max_sharpe"
        return result

    def _min_variance_optimization_gpu(self, returns: pd.DataFrame) -> Dict[str, Any]:
        """GPU加速最小方差优化"""
        # 简化实现：使用全局最小方差组合
        result = self._mean_variance_optimization_gpu(returns, 0.0)
        result["method"] = "min_variance"
        return result

    def clear_cache(self) -> None:
        """清除优化缓存"""
        self.optimization_cache.clear()
        logger.info("优化缓存已清除")

    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """获取优化历史"""
        return self.optimization_history.copy()

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        return {
            "cache_size": len(self.optimization_cache),
            "cached_params": list(self.optimization_cache.keys()),
            "history_size": len(self.optimization_history),
        }

