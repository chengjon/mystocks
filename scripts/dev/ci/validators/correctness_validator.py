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


class CorrectnessValidatorMixin:
    """回测引擎与策略正确性验证"""

    def validate_backtest_engine(self) -> bool:
        """验证回测引擎功能"""
        print("🔍 验证回测引擎功能...")

        try:
            # 导入多个回测引擎进行验证
            from src.backtesting.advanced_backtest_engine import AdvancedBacktestEngine
            from src.ml_strategy.backtest.backtest_engine import BacktestEngine
            from src.ml_strategy.backtest.performance_metrics import PerformanceMetrics
            from src.ml_strategy.backtest.risk_metrics import RiskMetrics

            # 创建测试数据
            dates = pd.date_range("2023-01-01", periods=100, freq="D")
            test_data = pd.DataFrame(
                {
                    "close": np.random.randn(100).cumsum() + 100,
                    "high": np.random.randn(100).cumsum() + 102,
                    "low": np.random.randn(100).cumsum() + 98,
                    "open": np.random.randn(100).cumsum() + 100,
                    "volume": np.random.randint(1000, 10000, 100),
                },
                index=dates,
            )

            # 测试高级回测引擎
            advanced_engine = AdvancedBacktestEngine()
            print("✅ 高级回测引擎初始化成功")

            # 测试ML策略回测引擎
            ml_engine = BacktestEngine()
            print("✅ ML策略回测引擎初始化成功")

            # 测试性能指标计算
            metrics = PerformanceMetrics()
            sample_returns = pd.Series(np.random.randn(100) * 0.02)

            sharpe = metrics.sharpe_ratio(sample_returns)
            max_dd = metrics.max_drawdown(sample_returns)
            total_return = metrics.total_return(sample_returns)

            print(
                f"✅ 性能指标计算正常 - Sharpe: {sharpe:.2f}, MaxDD: {max_dd:.2f}, Total Return: {total_return:.2%}"
            )

            # 测试风险指标计算
            risk_metrics = RiskMetrics()
            var_95 = risk_metrics.value_at_risk(sample_returns, confidence_level=0.95)
            cvar_95 = risk_metrics.conditional_value_at_risk(
                sample_returns, confidence_level=0.95
            )

            print(
                f"✅ 风险指标计算正常 - VaR(95%): {var_95:.2%}, CVaR(95%): {cvar_95:.2%}"
            )

            return True

        except Exception as e:
            error_msg = f"回测引擎验证失败: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return False

    def validate_strategy_correctness(self) -> bool:
        """验证策略正确性（使用基准数据）"""
        print("🔍 验证策略正确性...")

        # 创建测试市场数据
        test_data = self._create_test_market_data()

        validation_passed = True

        for strategy_name, benchmark in self.benchmarks.items():
            try:
                print(f"  验证策略: {strategy_name}")

                # 运行策略回测
                result = self._run_strategy_backtest(strategy_name, test_data)

                if result:
                    # 对比基准数据
                    if self._compare_with_benchmark(strategy_name, result, benchmark):
                        print(f"    ✅ {strategy_name} 验证通过")
                    else:
                        print(f"    ❌ {strategy_name} 结果偏离基准")
                        validation_passed = False
                else:
                    error_detail = result.get("error", "未知错误")
                    print(f"    ❌ {check_name} 失败: {error_detail}")
                    security_passed = False

            except Exception as e:
                error_msg = f"{check_name} 异常: {e}"
                self.errors.append(error_msg)
                security_results[check_name] = {"passed": False, "error": str(e)}
                print(f"    ❌ {error_msg}")
                print(f"       异常详情: {type(e).__name__}: {e}")
                import traceback

                print(f"       堆栈跟踪: {traceback.format_exc()}")
                security_passed = False

            except Exception as e:
                error_msg = f"{check_name} 异常: {e}"
                self.errors.append(error_msg)
                security_results[check_name] = {"passed": False, "error": str(e)}
                print(f"    ❌ {error_msg}")
                security_passed = False

        # 存储安全验证结果用于报告
        self._security_validation_results = security_results

        return security_passed

