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


class OrchestrationMixin:
    """验证编排：单项验证、全量验证"""

    def run_single_validation(self, validation_type: str) -> Dict[str, Any]:
        """运行单一验证类型"""
        print(f"🚀 开始单一验证: {validation_type}")
        start_time = time.time()

        results = {
            "timestamp": time.time(),
            "validation_type": validation_type,
            "checks": {},
            "summary": {"total_checks": 0, "passed_checks": 0, "failed_checks": 0},
            "errors": [],
            "warnings": [],
        }

        # 映射验证类型到对应的方法
        validation_map = {
            "syntax": (
                "syntax_validation",
                "策略语法验证",
                self.validate_strategy_syntax,
            ),
            "imports": (
                "import_validation",
                "策略导入验证",
                self.validate_strategy_imports,
            ),
            "backtest_engine": (
                "backtest_engine_validation",
                "回测引擎验证",
                self.validate_backtest_engine,
            ),
            "security": ("security_validation", "安全验证", self.validate_security),
            "code_quality": (
                "code_quality_validation",
                "代码质量验证",
                self.validate_code_quality,
            ),
            "integration_testing": (
                "integration_testing_validation",
                "集成测试验证",
                self.validate_integration_testing,
            ),
            "performance_regression": (
                "performance_regression_validation",
                "性能回归验证",
                self.validate_performance_regression,
            ),
            "ai_enhanced": (
                "ai_enhanced_validation",
                "AI增强验证",
                self.validate_ai_enhanced,
            ),
            "correctness": (
                "strategy_correctness_validation",
                "策略正确性验证",
                self.validate_strategy_correctness,
            ),
        }

        if validation_type not in validation_map:
            error_msg = f"未知的验证类型: {validation_type}"
            results["errors"].append(error_msg)
            results["summary"]["failed_checks"] = 1
            return results

        check_id, check_name, check_func = validation_map[validation_type]

        print(f"\n📋 执行检查: {check_name}")
        try:
            passed = check_func()
            results["checks"][check_id] = {
                "name": check_name,
                "passed": passed,
                "duration": 0,
            }

            results["summary"]["total_checks"] = 1
            if passed:
                results["summary"]["passed_checks"] = 1
            else:
                results["summary"]["failed_checks"] = 1

        except Exception as e:
            error_msg = f"{check_name} 执行异常: {e}"
            results["checks"][check_id] = {
                "name": check_name,
                "passed": False,
                "error": str(e),
            }
            results["errors"].append(error_msg)
            results["summary"]["failed_checks"] = 1
            results["summary"]["total_checks"] = 1

        # 计算总体结果
        results["summary"]["success_rate"] = (
            results["summary"]["passed_checks"] / results["summary"]["total_checks"]
        ) * 100
        results["summary"]["overall_passed"] = results["summary"]["failed_checks"] == 0

        # 添加执行时间
        results["execution_time"] = time.time() - start_time

        # 添加错误和警告信息
        results["errors"].extend(self.errors)
        results["warnings"].extend(self.warnings)

        print(f"\n📊 验证完成，耗时: {results['execution_time']:.2f}秒")
        print(
            f"✅ 通过: {results['summary']['passed_checks']}/{results['summary']['total_checks']}"
        )
        print(f"🏆 结果: {'通过' if results['summary']['overall_passed'] else '失败'}")

        return results

    def run_full_validation(self) -> Dict[str, Any]:
        """运行完整的策略验证"""
        print("🚀 开始量化策略正确性校验...")
        start_time = time.time()

        results = {
            "timestamp": time.time(),
            "checks": {},
            "summary": {"total_checks": 0, "passed_checks": 0, "failed_checks": 0},
            "errors": [],
            "warnings": [],
        }

        # 执行各项检查
        checks = [
            ("syntax_validation", "策略语法验证", self.validate_strategy_syntax),
            ("import_validation", "策略导入验证", self.validate_strategy_imports),
            (
                "backtest_engine_validation",
                "回测引擎验证",
                self.validate_backtest_engine,
            ),
            ("security_validation", "安全验证", self.validate_security),
            ("code_quality_validation", "代码质量验证", self.validate_code_quality),
            (
                "integration_testing_validation",
                "集成测试验证",
                self.validate_integration_testing,
            ),
            (
                "performance_regression_validation",
                "性能回归验证",
                self.validate_performance_regression,
            ),
            ("ai_enhanced_validation", "AI增强验证", self.validate_ai_enhanced),
            (
                "strategy_correctness_validation",
                "策略正确性验证",
                self.validate_strategy_correctness,
            ),
        ]

        for check_id, check_name, check_func in checks:
            print(f"\n📋 执行检查: {check_name}")
            try:
                passed = check_func()
                results["checks"][check_id] = {
                    "name": check_name,
                    "passed": passed,
                    "duration": 0,  # 可以后续添加时间统计
                }

                results["summary"]["total_checks"] += 1
                if passed:
                    results["summary"]["passed_checks"] += 1
                else:
                    results["summary"]["failed_checks"] += 1

            except Exception as e:
                error_msg = f"{check_name} 执行异常: {e}"
                results["checks"][check_id] = {
                    "name": check_name,
                    "passed": False,
                    "error": str(e),
                }
                results["errors"].append(error_msg)
                results["summary"]["failed_checks"] += 1
                results["summary"]["total_checks"] += 1

        # 计算总体结果
        results["summary"]["success_rate"] = (
            results["summary"]["passed_checks"] / results["summary"]["total_checks"]
        ) * 100

        results["summary"]["overall_passed"] = results["summary"]["failed_checks"] == 0

        # 添加执行时间
        results["execution_time"] = time.time() - start_time

        # 添加错误和警告信息
        results["errors"].extend(self.errors)
        results["warnings"].extend(self.warnings)

        print(f"\n📊 校验完成，耗时: {results['execution_time']:.2f}秒")
        print(
            f"✅ 通过: {results['summary']['passed_checks']}/{results['summary']['total_checks']}"
        )
        print(
            f"🏆 总体结果: {'通过' if results['summary']['overall_passed'] else '失败'}"
        )

        return results


