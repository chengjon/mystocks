"""量化策略验证器子模块"""

import ast
import json
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class BaseValidatorMixin:
    """基础验证器：初始化与基准加载"""

class QuantStrategyValidator:
    """量化策略校验器"""

    def __init__(self):
        self.project_root = project_root
        self.benchmarks = self._load_benchmarks()
        self.validation_results: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def _load_benchmarks(self) -> Dict[str, Dict[str, Any]]:
        """加载策略基准数据"""
        benchmarks = {}

        # 检查pandas可用性，如果不可用则跳过pandas相关的验证
        if not PANDAS_AVAILABLE:
            print("⚠️ pandas/numpy不可用，跳过相关验证")
            return benchmarks

        # 基础策略基准数据
        benchmarks.update(
            {
                "momentum_strategy": {
                    "expected_sharpe_ratio": 1.2,
                    "expected_max_drawdown": -0.15,
                    "expected_total_return": 0.25,
                    "tolerance": 0.05,  # 5%容差
                },
                "mean_reversion_strategy": {
                    "expected_sharpe_ratio": 0.8,
                    "expected_max_drawdown": -0.12,
                    "expected_total_return": 0.18,
                    "tolerance": 0.05,
                },
                "trend_following_strategy": {
                    "expected_sharpe_ratio": 1.5,
                    "expected_max_drawdown": -0.20,
                    "expected_total_return": 0.35,
                    "tolerance": 0.05,
                },
            }
        )

        # ML策略基准
        ml_strategies = ["decision_tree", "svm", "naive_bayes", "lstm", "transformer"]

        for strategy in ml_strategies:
            benchmarks[f"ml_{strategy}_strategy"] = {
                "expected_sharpe_ratio": 1.0,
                "expected_max_drawdown": -0.18,
                "expected_total_return": 0.22,
                "min_accuracy": 0.55,  # ML策略的最低准确率要求
                "tolerance": 0.08,  # ML策略更大的容差
            }

        return benchmarks

