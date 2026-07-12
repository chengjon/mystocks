#!/usr/bin/env python3
"""性能回归测试脚本
为核心功能建立性能基准和回归检测
确保代码修改不会导致性能下降
"""

import statistics
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class PerformanceRegressionTester:
    """性能回归测试器"""

    def __init__(self):
        self.baseline_file = project_root / "scripts" / "performance" / "baseline.json"
        self.baseline_data = {}
        self.test_results = {}

    def run_all_tests(self) -> Dict[str, Dict]:
        """运行所有性能测试"""
        print("🚀 开始运行性能回归测试...")

        tests = [
            (
                "data_validator_symbol_validation",
                self.test_data_validator_symbol_validation,
            ),
            (
                "data_validator_date_validation",
                self.test_data_validator_date_validation,
            ),
            (
                "data_validator_price_validation",
                self.test_data_validator_price_validation,
            ),
            ("dataframe_operations", self.test_dataframe_operations),
            ("exception_creation", self.test_exception_creation),
            ("exception_serialization", self.test_exception_serialization),
        ]

        results = {}

        for test_name, test_func in tests:
            print(f"\n📊 运行测试: {test_name}")
            try:
                results[test_name] = test_func()
                print(f"✅ {test_name}: 测试通过")
            except Exception as e:
                print(f"❌ {test_name}: 测试失败 - {e}")
                results[test_name] = {"error": str(e)}

        self.test_results = results
        return results

    def test_data_validator_symbol_validation(self) -> Dict:
        """测试数据验证器的股票代码验证性能"""
        from src.adapters.data_validator import DataValidator

        validator = DataValidator()
        test_symbols = ["000001", "600000", "300001", "002415"] * 1000  # 4000个测试

        # 预热
        for symbol in test_symbols[:100]:
            validator.validate_stock_symbol(symbol)

        # 实际测试
        start_time = time.time()
        for symbol in test_symbols:
            validator.validate_stock_symbol(symbol)
        end_time = time.time()

        duration = end_time - start_time
        operations_per_second = len(test_symbols) / duration

        return {
            "duration": duration,
            "operations": len(test_symbols),
            "ops_per_second": operations_per_second,
            "avg_time_per_op": duration / len(test_symbols) * 1000,  # 转换为毫秒
        }

    def test_data_validator_date_validation(self) -> Dict:
        """测试数据验证器的日期验证性能"""
        from src.adapters.data_validator import DataValidator

        validator = DataValidator()
        test_dates = ["2024-01-01", "2024-06-15", "2024-12-31"] * 1000  # 3000个测试

        # 预热
        for date in test_dates[:100]:
            validator.validate_date_format(date)

        # 实际测试
        start_time = time.time()
        for date in test_dates:
            validator.validate_date_format(date)
        end_time = time.time()

        duration = end_time - start_time
        operations_per_second = len(test_dates) / duration

        return {
            "duration": duration,
            "operations": len(test_dates),
            "ops_per_second": operations_per_second,
            "avg_time_per_op": duration / len(test_dates) * 1000,
        }

    def test_data_validator_price_validation(self) -> Dict:
        """测试数据验证器的价格数据验证性能"""
        from src.adapters.data_validator import DataValidator

        validator = DataValidator()

        # 创建测试数据
        test_cases = []
        for i in range(100):  # 100个DataFrame
            df = pd.DataFrame(
                {
                    "open": [10.0 + i * 0.1] * 100,
                    "high": [10.5 + i * 0.1] * 100,
                    "low": [9.5 + i * 0.1] * 100,
                    "close": [10.2 + i * 0.1] * 100,
                    "volume": [1000 + i * 10] * 100,
                },
            )
            test_cases.append(df)

        # 预热
        for df in test_cases[:10]:
            validator.validate_price_data(df)

        # 实际测试
        start_time = time.time()
        for df in test_cases:
            validator.validate_price_data(df)
        end_time = time.time()

        duration = end_time - start_time
        total_rows = sum(len(df) for df in test_cases)

        return {
            "duration": duration,
            "dataframes": len(test_cases),
            "total_rows": total_rows,
            "rows_per_second": total_rows / duration,
            "avg_time_per_df": duration / len(test_cases) * 1000,
        }

    def test_dataframe_operations(self) -> Dict:
        """测试DataFrame操作性能"""
        # 创建大型DataFrame
        large_df = pd.DataFrame(
            {
                "date": pd.date_range("2020-01-01", periods=10000),
                "open": np.random.uniform(10, 100, 10000),
                "high": np.random.uniform(10, 100, 10000),
                "low": np.random.uniform(10, 100, 10000),
                "close": np.random.uniform(10, 100, 10000),
                "volume": np.random.randint(1000, 10000, 10000),
            },
        )

        operations = []

        # 测试基本操作
        start_time = time.time()

        # 1. 过滤操作
        filtered = large_df[large_df["close"] > 50]
        operations.append(time.time() - start_time)

        # 2. 分组操作
        start_time = time.time()
        grouped = large_df.groupby(large_df["date"].dt.month).mean()
        operations.append(time.time() - start_time)

        # 3. 排序操作
        start_time = time.time()
        sorted_df = large_df.sort_values("close")
        operations.append(time.time() - start_time)

        # 4. 聚合操作
        start_time = time.time()
        aggregated = large_df.agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            },
        )
        operations.append(time.time() - start_time)

        total_time = sum(operations)
        avg_time = statistics.mean(operations)

        return {
            "rows": len(large_df),
            "total_time": total_time,
            "avg_operation_time": avg_time * 1000,  # 转换为毫秒
            "operations": operations,
            "min_time": min(operations) * 1000,
            "max_time": max(operations) * 1000,
        }

    def test_exception_creation(self) -> Dict:
        """测试异常创建性能"""
        from src.core.exceptions import MyStocksException, NetworkError

        # 测试不同异常类型的创建时间
        exception_types = [
            MyStocksException,
            NetworkError,
        ]

        results = {}

        for exc_class in exception_types:
            # 预热
            for _ in range(100):
                exc_class("Warmup")

            # 实际测试
            start_time = time.time()
            for i in range(1000):
                exc = exc_class(f"Test message {i}", context={"index": i})
            end_time = time.time()

            duration = end_time - start_time
            class_name = exc_class.__name__

            results[class_name] = {
                "duration": duration,
                "ops_per_second": 1000 / duration,
                "avg_time_per_op": duration / 1000 * 1000,
            }

        return results

    def test_exception_serialization(self) -> Dict:
        """测试异常序列化性能"""
        from src.core.exceptions import MyStocksException

        # 创建测试异常
        exceptions = []
        for i in range(1000):
            exc = MyStocksException(
                f"Test message {i}",
                context={"index": i, "data": "x" * 50},  # 增加上下文大小
            )
            exceptions.append(exc)

        # 测试to_dict序列化
        start_time = time.time()
        for exc in exceptions:
            data = exc.to_dict()
        end_time = time.time()

        dict_serialization_time = end_time - start_time

        # 测试字符串序列化
        start_time = time.time()
        for exc in exceptions:
            str_repr = str(exc)
        end_time = time.time()

        str_serialization_time = end_time - start_time

        return {
            "exception_count": len(exceptions),
            "dict_serialization_time": dict_serialization_time,
            "dict_ops_per_second": len(exceptions) / dict_serialization_time,
            "str_serialization_time": str_serialization_time,
            "str_ops_per_second": len(exceptions) / str_serialization_time,
            "avg_dict_time": dict_serialization_time / len(exceptions) * 1000,
            "avg_str_time": str_serialization_time / len(exceptions) * 1000,
        }

    def load_baseline(self) -> bool:
        """加载基准数据"""
        if not self.baseline_file.exists():
            print(f"⚠️  基准文件不存在: {self.baseline_file}")
            return False

        try:
            import json

            with open(self.baseline_file) as f:
                self.baseline_data = json.load(f)
            print(f"✅ 加载基准数据: {len(self.baseline_data)} 个测试")
            return True
        except Exception as e:
            print(f"❌ 加载基准数据失败: {e}")
            return False

    def save_baseline(self):
        """保存当前测试结果作为基准"""
        try:
            self.baseline_file.parent.mkdir(parents=True, exist_ok=True)

            import json

            with open(self.baseline_file, "w") as f:
                json.dump(self.test_results, f, indent=2)
            print(f"✅ 保存基准数据到: {self.baseline_file}")
        except Exception as e:
            print(f"❌ 保存基准数据失败: {e}")

    def compare_with_baseline(self) -> Tuple[bool, List[str]]:
        """与基准数据比较"""
        if not self.baseline_data:
            return True, ["没有基准数据可供比较"]

        all_passed = True
        messages = []

        for test_name, current_result in self.test_results.items():
            if "error" in current_result:
                messages.append(f"⚠️  {test_name}: 当前测试失败，无法比较")
                continue

            if test_name not in self.baseline_data:
                messages.append(f"🆕 {test_name}: 新测试，建立基准")
                continue

            baseline_result = self.baseline_data[test_name]

            # 比较性能指标
            regression_detected = self._compare_performance(
                test_name,
                current_result,
                baseline_result,
            )

            if regression_detected:
                all_passed = False
                messages.append(f"📉 {test_name}: 检测到性能回归")
                messages.append(f"    当前: {self._format_performance(current_result)}")
                messages.append(
                    f"    基准: {self._format_performance(baseline_result)}",
                )
            else:
                messages.append(f"✅ {test_name}: 性能正常或改善")

        return all_passed, messages

    def _compare_performance(
        self,
        test_name: str,
        current: Dict,
        baseline: Dict,
    ) -> bool:
        """比较性能指标"""
        # 定义性能回归阈值（允许10%的性能下降）
        regression_threshold = 1.1  # 10%性能下降阈值

        if test_name == "exception_creation":
            # 异常创建测试
            for exc_class in current_result:
                if exc_class in baseline:
                    current_ops = current_result[exc_class]["ops_per_second"]
                    baseline_ops = baseline[exc_class]["ops_per_second"]

                    if current_ops < baseline_ops / regression_threshold:
                        return True

        elif "ops_per_second" in current:
            # 通用每秒操作数比较
            current_ops = current_result["ops_per_second"]
            baseline_ops = baseline.get("ops_per_second", 0)

            if baseline_ops > 0 and current_ops < baseline_ops / regression_threshold:
                return True

        elif "rows_per_second" in current:
            # DataFrame处理速度比较
            current_speed = current_result["rows_per_second"]
            baseline_speed = baseline.get("rows_per_second", 0)

            if baseline_speed > 0 and current_speed < baseline_speed / regression_threshold:
                return True

        return False

    def _format_performance(self, result: Dict) -> str:
        """格式化性能数据"""
        if "ops_per_second" in result:
            return f"{result['ops_per_second']:.1f} ops/s"
        if "rows_per_second" in result:
            return f"{result['rows_per_second']:.1f} rows/s"
        if "duration" in result:
            return f"{result['duration']:.3f}s"
        return str(result)

    def generate_report(self, comparison_passed: bool, messages: List[str]) -> str:
        """生成测试报告"""
        report = []
        report.append("=" * 60)
        report.append("⚡ 性能回归测试报告")
        report.append("=" * 60)
        report.append(f"测试时间: {self._get_current_time()}")
        report.append("")

        # 总体状态
        status = "✅ 通过" if comparison_passed else "❌ 检测到性能回归"
        report.append(f"总体状态: {status}")
        report.append("")

        # 测试结果
        report.append("📊 测试结果详情:")
        report.append("-" * 30)

        for test_name, result in self.test_results.items():
            if "error" in result:
                report.append(f"  ❌ {test_name}: 测试失败")
            else:
                report.append(f"  ✅ {test_name}: 测试通过")

        report.append("")
        report.append("📋 性能比较:")
        report.append("-" * 30)

        for message in messages:
            report.append(f"  {message}")

        # 建议
        report.append("")
        report.append("💡 建议:")
        if comparison_passed:
            report.append("  ✅ 所有性能测试正常")
            report.append("  ✅ 可以继续开发或重构")
        else:
            report.append("  ❌ 检测到性能回归")
            report.append("  ❌ 建议分析性能瓶颈")
            report.append("  ❌ 考虑优化后再提交代码")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run(self, save_baseline: bool = False) -> bool:
        """运行性能回归测试"""
        print("🚀 启动性能回归测试...")

        # 运行测试
        self.run_all_tests()

        if save_baseline:
            print("\n💾 保存基准数据...")
            self.save_baseline()
            return True

        # 加载基准并比较
        self.load_baseline()
        comparison_passed, messages = self.compare_with_baseline()

        # 生成报告
        report = self.generate_report(comparison_passed, messages)
        print("\n" + report)

        # 保存报告
        report_file = project_root / "performance_report.txt"
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\n📄 报告已保存到: {report_file}")
        except Exception as e:
            print(f"⚠️  保存报告失败: {e}")

        return comparison_passed


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="性能回归测试工具")
    parser.add_argument(
        "--save-baseline",
        action="store_true",
        help="保存当前测试结果作为基准数据",
    )
    parser.add_argument(
        "--baseline-only",
        action="store_true",
        help="只运行基准测试，不进行比较",
    )

    args = parser.parse_args()

    tester = PerformanceRegressionTester()

    try:
        if args.baseline_only:
            success = tester.run(save_baseline=True)
        else:
            success = tester.run(save_baseline=args.save_baseline)

        if success:
            print("\n🎉 性能回归测试通过!")
            sys.exit(0)
        else:
            print("\n⚠️  性能回归测试未通过，请检查性能瓶颈")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️  用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
