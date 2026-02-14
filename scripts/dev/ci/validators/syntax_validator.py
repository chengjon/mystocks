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


class SyntaxValidatorMixin:
    """语法与导入验证"""

    def validate_strategy_syntax(self) -> bool:
        """验证策略文件语法"""
        print("🔍 验证策略文件语法...")

        strategy_files = [
            # 基础策略
            "src/ml_strategy/strategy/templates/momentum_template.py",
            "src/ml_strategy/strategy/templates/mean_reversion_template.py",
            "src/ml_strategy/strategy/templates/custom_template.py",
            # ML策略
            "src/ml_strategy/strategy/decision_tree_trading_strategy.py",
            "src/ml_strategy/strategy/svm_trading_strategy.py",
            "src/ml_strategy/strategy/naive_bayes_trading_strategy.py",
            "src/ml_strategy/strategy/lstm_trading_strategy.py",
            "src/ml_strategy/strategy/transformer_trading_strategy.py",
            # 基础策略类
            "src/ml_strategy/strategy/base_strategy.py",
            "src/ml_strategy/strategy/ml_strategy_base.py",
            # 回测引擎
            "src/backtesting/advanced_backtest_engine.py",
            "src/ml_strategy/backtest/backtest_engine.py",
            "src/ml_strategy/backtest/ml_strategy_backtester.py",
            # 性能指标
            "src/ml_strategy/backtest/performance_metrics.py",
        ]

        syntax_errors = []

        for file_path in strategy_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        compile(f.read(), str(full_path), "exec")
                    print(f"✅ {file_path}")
                except SyntaxError as e:
                    error_msg = f"{file_path}: {e}"
                    syntax_errors.append(error_msg)
                    print(f"❌ {error_msg}")
            else:
                print(f"⚠️ 文件不存在: {file_path}")

        if syntax_errors:
            self.errors.extend([f"语法错误: {err}" for err in syntax_errors])
            return False

        print(f"✅ 所有 {len(strategy_files)} 个策略文件语法检查通过")
        return True

    def validate_strategy_imports(self) -> bool:
        """验证策略模块导入"""
        print("🔍 验证策略模块导入...")

        import_tests = [
            (
                "基础策略导入",
                [
                    "from src.ml_strategy.strategy.templates.momentum_template import MomentumStrategy",
                    "from src.ml_strategy.strategy.templates.mean_reversion_template import MeanReversionStrategy",
                ],
            ),
            (
                "ML策略导入",
                [
                    "from src.ml_strategy.strategy.decision_tree_trading_strategy import DecisionTreeTradingStrategy",
                    "from src.ml_strategy.strategy.svm_trading_strategy import SVMTradingStrategy",
                ],
            ),
            (
                "回测引擎导入",
                [
                    "from src.backtesting.advanced_backtest_engine import AdvancedBacktestEngine",
                    "from src.ml_strategy.backtest.backtest_engine import BacktestEngine",
                    "from src.ml_strategy.backtest.performance_metrics import PerformanceMetrics",
                ],
            ),
        ]

        import_errors = []

        for test_name, imports in import_tests:
            print(f"  测试: {test_name}")
            for import_stmt in imports:
                try:
                    exec(import_stmt)
                    print(f"    ✅ {import_stmt.split()[-1]}")
                except ImportError as e:
                    error_msg = f"{test_name} - {import_stmt}: {e}"
                    import_errors.append(error_msg)
                    print(f"    ❌ {error_msg}")

        if import_errors:
            self.errors.extend([f"导入错误: {err}" for err in import_errors])
            return False

        print("✅ 所有策略模块导入成功")
        return True

