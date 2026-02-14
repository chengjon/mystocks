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


class QualityValidatorMixin:
    """代码质量与集成测试验证"""

    def validate_code_quality(self) -> bool:
        """验证代码质量"""
        print("📊 验证代码质量...")

        quality_checks = [
            ("代码复杂度分析", self._validate_code_complexity),
            ("代码覆盖率检查", self._validate_code_coverage),
            ("静态代码分析", self._validate_static_analysis),
            ("代码风格检查", self._validate_code_style),
            ("文档覆盖检查", self._validate_documentation),
        ]

        quality_passed = True
        quality_results = {}

        for check_name, validator_func in quality_checks:
            try:
                print(f"  检查: {check_name}")
                result = validator_func()
                quality_results[check_name] = result

                if result["passed"]:
                    print(f"    ✅ {check_name} 通过")
                    if "details" in result:
                        details = result["details"]
                        if "average_complexity" in details:
                            print(
                                f"       平均复杂度: {details['average_complexity']:.2f}"
                            )
                        if "coverage_percentage" in details:
                            print(
                                f"       覆盖率: {details['coverage_percentage']:.1f}%"
                            )
                else:
                    error_detail = result.get("error", "未知错误")
                    print(f"    ❌ {check_name} 失败: {error_detail}")
                    quality_passed = False

            except Exception as e:
                error_msg = f"{check_name} 异常: {e}"
                self.errors.append(error_msg)
                quality_results[check_name] = {"passed": False, "error": str(e)}
                print(f"    ❌ {error_msg}")
                quality_passed = False

        # 存储代码质量验证结果用于报告
        self._quality_validation_results = quality_results

        return quality_passed

    def validate_integration_testing(self) -> bool:
        """验证集成测试"""
        print("🔗 验证集成测试...")

        integration_checks = [
            ("数据库连接测试", self._validate_database_connection),
            ("API端点测试", self._validate_api_endpoints),
            ("服务集成测试", self._validate_service_integrations),
            ("外部依赖测试", self._validate_external_dependencies),
            ("消息队列测试", self._validate_message_queue),
        ]

        integration_passed = True
        integration_results = {}

        for check_name, validator_func in integration_checks:
            try:
                print(f"  检查: {check_name}")
                result = validator_func()
                integration_results[check_name] = result

                if result["passed"]:
                    print(f"    ✅ {check_name} 通过")
                    if "details" in result:
                        details = result["details"]
                        if "response_time" in details:
                            print(f"       响应时间: {details['response_time']:.2f}ms")
                        if "connections_established" in details:
                            print(
                                f"       连接数: {details['connections_established']}"
                            )
                else:
                    error_detail = result.get("error", "未知错误")
                    print(f"    ❌ {check_name} 失败: {error_detail}")
                    integration_passed = False

            except Exception as e:
                error_msg = f"{check_name} 异常: {e}"
                self.errors.append(error_msg)
                integration_results[check_name] = {"passed": False, "error": str(e)}
                print(f"    ❌ {error_msg}")
                integration_passed = False

        # 存储集成测试验证结果用于报告
        self._integration_validation_results = integration_results

        return integration_passed

    def validate_performance_regression(self) -> bool:
        """验证性能回归测试"""
        print("📈 验证性能回归测试...")

        regression_checks = [
            ("历史性能对比", self._validate_historical_performance),
            ("内存泄漏检测", self._validate_memory_leak_detection),
            ("响应时间回归", self._validate_response_time_regression),
            ("资源使用监控", self._validate_resource_usage_monitoring),
            ("性能基准测试", self._validate_performance_baselines),
        ]

        regression_passed = True
        regression_results = {}

        for check_name, validator_func in regression_checks:
            try:
                print(f"  检查: {check_name}")
                result = validator_func()
                regression_results[check_name] = result

                if result["passed"]:
                    print(f"    ✅ {check_name} 通过")
                    if "details" in result:
                        details = result["details"]
                        if "performance_change" in details:
                            change = details["performance_change"]
                            print(f"       性能变化: {change:+.1f}%")
                        if "memory_growth" in details:
                            growth = details["memory_growth"]
                            print(f"       内存增长: {growth:.1f}MB")
                else:
                    error_detail = result.get("error", "未知错误")
                    print(f"    ❌ {check_name} 失败: {error_detail}")
                    regression_passed = False

            except Exception as e:
                error_msg = f"{check_name} 异常: {e}"
                self.errors.append(error_msg)
                regression_results[check_name] = {"passed": False, "error": str(e)}
                print(f"    ❌ {error_msg}")
                regression_passed = False

        # 存储性能回归测试结果用于报告
        self._regression_validation_results = regression_results

        return regression_passed

