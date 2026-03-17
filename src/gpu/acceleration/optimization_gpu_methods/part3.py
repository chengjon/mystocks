#!/usr/bin/env python3
"""
# 功能：GPU加速优化引擎补充分片
"""

import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd

try:
    import cupy as cp
except ImportError:
    cp = None

logger = logging.getLogger(__name__)


class OptimizationGPUPortfolioMixin:
    """OptimizationGPU 投资组合与收敛方法集"""

    def _estimate_param_space_size(self, param_space: Dict) -> int:
        """估计参数空间大小"""
        size = 1
        for param_range in param_space.values():
            if isinstance(param_range, list):
                size *= len(param_range)
            elif isinstance(param_range, tuple):
                size *= 100
        return size

    def _get_convergence_curve(self) -> List[float]:
        """获取收敛曲线"""
        if not self.optimization_history:
            return []
        return [record["best_score"] for record in self.optimization_history[-10:]]

    def _mean_variance_optimization_gpu(self, returns: pd.DataFrame, risk_free_rate: float) -> Dict[str, Any]:
        """GPU加速均值-方差优化"""
        try:
            if self.gpu_available:
                returns_gpu = cp.array(returns.values)
                mean_returns = cp.mean(returns_gpu, axis=0)
                cov_matrix = cp.cov(returns_gpu, rowvar=False)
                cov_matrix += cp.eye(cov_matrix.shape[0]) * 1e-6
            else:
                mean_returns = returns.mean().values
                cov_matrix = returns.cov().values
                cov_matrix += np.eye(cov_matrix.shape[0]) * 1e-6

            n_assets = len(mean_returns)
            weights = np.ones(n_assets) / n_assets

            if self.gpu_available:
                portfolio_return = float(cp.dot(weights, mean_returns))
                portfolio_variance = float(cp.dot(cp.dot(weights, cov_matrix), weights))
            else:
                portfolio_return = np.dot(weights, mean_returns)
                portfolio_variance = np.dot(np.dot(weights, cov_matrix), weights)

            portfolio_std = np.sqrt(portfolio_variance)
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std if portfolio_std > 0 else 0

            return {
                "weights": weights.tolist(),
                "expected_return": portfolio_return,
                "volatility": portfolio_std,
                "sharpe_ratio": sharpe_ratio,
                "method": "mean_variance",
            }
        except Exception as error:
            logger.error("均值-方差优化失败: %s", error)
            return {"error": str(error)}
