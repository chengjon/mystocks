#!/usr/bin/env python3
"""数据源手动测试工具

功能：
1. 交互式测试模式（选择接口、输入参数、查看结果）
2. 命令行测试模式（直接指定参数）
3. 数据质量分析（完整性、范围、格式检查）
4. 测试报告生成

使用示例：
    # 交互式模式
    python scripts/tools/manual_data_source_tester.py --interactive

    # 命令行模式
    python scripts/tools/manual_data_source_tester.py \
        --endpoint akshare.stock_zh_a_hist \
        --symbol 000001 \
        --start-date 20240101 \
        --end-date 20240131

作者：Claude Code
版本：v1.0
创建时间：2026-01-02
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.data_source_manager_v2 import DataSourceManagerV2


class DataSourceTester:
    """数据源测试器"""

    def __init__(self):
        self.manager = DataSourceManagerV2()
        self.test_history = []

    def test_data_source(
        self,
        endpoint_name: str,
        test_params: Dict[str, Any],
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """测试单个数据源

        Args:
            endpoint_name: 接口名称
            test_params: 测试参数
            verbose: 是否显示详细信息

        Returns:
            测试结果字典

        """
        result = {
            "endpoint_name": endpoint_name,
            "success": False,
            "start_time": datetime.now(),
            "end_time": None,
            "duration": None,
            "row_count": 0,
            "data_preview": None,
            "quality_checks": {},
            "error": None,
        }

        print(f"\n{'=' * 60}")
        print(f"测试数据源: {endpoint_name}")
        print(f"{'=' * 60}")

        # 1. 检查接口是否存在
        if endpoint_name not in self.manager.registry:
            print(f"❌ 接口不存在: {endpoint_name}")
            result["error"] = "接口不存在"
            result["end_time"] = datetime.now()
            return result

        source_config = self.manager.registry[endpoint_name]["config"]

        # 2. 显示接口配置
        if verbose:
            print("\n📋 接口配置:")
            print(f"   数据源: {source_config.get('source_name')}")
            print(f"   数据分类: {source_config.get('data_category')}")
            print(f"   目标数据库: {source_config.get('target_db')}")
            print(f"   质量评分: {source_config.get('data_quality_score')}")
            print(f"   健康状态: {source_config.get('health_status')}")
            print(f"   优先级: {source_config.get('priority')}")

        # 3. 显示测试参数
        if verbose:
            print("\n🔧 测试参数:")
            for key, value in test_params.items():
                print(f"   {key}: {value}")

        # 4. 执行测试
        print("\n⏳ 正在调用接口...")
        result["start_time"] = datetime.now()

        try:
            # 调用数据源
            handler = self._get_handler(endpoint_name)
            data = handler.fetch(**test_params)

            result["end_time"] = datetime.now()
            result["duration"] = (result["end_time"] - result["start_time"]).total_seconds()

            # 5. 显示结果
            print("✅ 调用成功")
            print(f"   响应时间: {result['duration']:.3f}秒")

            # 处理返回数据
            if data is not None:
                if hasattr(data, "__len__"):
                    result["row_count"] = len(data)
                    print(f"   返回数据量: {result['row_count']}条")

                    if verbose and result["row_count"] > 0:
                        print("\n📊 数据预览:")
                        if hasattr(data, "head"):
                            preview = data.head(3)
                            if hasattr(preview, "to_string"):
                                print(f"   {preview.to_string(index=False)}")
                            else:
                                print(f"   {str(preview)[:200]}")
                        else:
                            print(f"   {str(data)[:200]}")

                        # 6. 数据质量检查
                        if verbose:
                            quality_checks = self._check_data_quality(
                                data,
                                source_config,
                                test_params,
                            )
                            result["quality_checks"] = quality_checks

                            print("\n📈 数据质量分析:")
                            self._display_quality_checks(quality_checks)

            result["success"] = True

            # 7. 记录成功（不使用metrics，避免依赖）
            print("\n✅ 测试通过")

        except Exception as e:
            result["end_time"] = datetime.now()
            result["duration"] = (result["end_time"] - result["start_time"]).total_seconds()
            result["error"] = str(e)

            print("❌ 调用失败")
            print(f"   响应时间: {result['duration']:.3f}秒")
            print(f"   错误信息: {e!s}")

            if verbose:
                import traceback

                print("\n详细错误堆栈:")
                traceback.print_exc()

        # 保存到测试历史
        self.test_history.append(result)

        return result

    def _get_handler(self, endpoint_name: str):
        """获取数据源处理器"""
        from src.core.data_source_handlers_v2 import get_handler

        return get_handler(endpoint_name, self.manager.registry[endpoint_name]["config"])

    def _check_data_quality(
        self,
        data: Any,
        source_config: Dict,
        test_params: Dict,
    ) -> Dict[str, Any]:
        """数据质量检查

        Returns:
            质量检查结果

        """
        checks = {
            "has_data": False,
            "is_empty": True,
            "column_completeness": {},
            "data_range": {},
            "duplicate_check": {},
            "type_consistency": {},
        }

        if data is None:
            return checks

        # 检查是否有数据
        checks["has_data"] = True

        # 检查是否为空
        if hasattr(data, "empty"):
            checks["is_empty"] = data.empty
        elif hasattr(data, "__len__"):
            checks["is_empty"] = len(data) == 0

        if checks["is_empty"]:
            return checks

        # DataFrame类型检查
        if hasattr(data, "columns"):
            # 1. 列完整性检查
            expected_params = source_config.get("parameters", {})
            actual_cols = data.columns.tolist()

            for param_name in expected_params.keys():
                is_present = param_name in actual_cols
                checks["column_completeness"][param_name] = {
                    "present": is_present,
                    "status": "✅ 存在" if is_present else "⚠️  缺失",
                }

            # 2. 数据范围检查
            for col in actual_cols[:5]:  # 只检查前5列
                if pd.api.types.is_numeric_dtype(data[col]):
                    checks["data_range"][col] = {
                        "min": float(data[col].min()),
                        "max": float(data[col].max()),
                        "mean": float(data[col].mean()) if hasattr(data[col], "mean") else None,
                        "null_count": int(data[col].isna().sum()),
                        "null_rate": float(data[col].isna().sum() / len(data)),
                    }

            # 3. 重复数据检查
            if hasattr(data, "duplicated"):
                dup_count = int(data.duplicated().sum())
                checks["duplicate_check"] = {
                    "duplicate_count": dup_count,
                    "duplicate_rate": dup_count / len(data),
                    "status": "✅ 无重复" if dup_count == 0 else f"⚠️  {dup_count}条重复",
                }

        return checks

    def _display_quality_checks(self, checks: Dict[str, Any]):
        """显示质量检查结果"""
        # 列完整性
        if checks["column_completeness"]:
            print("   列完整性:")
            for col, info in checks["column_completeness"].items():
                print(f"     {col}: {info['status']}")

        # 数据范围
        if checks["data_range"]:
            print("   数据范围 (前5列):")
            for col, info in checks["data_range"].items():
                print(f"     {col}:")
                print(f"       范围: {info['min']:.2f} ~ {info['max']:.2f}")
                print(f"       均值: {info['mean']:.2f if info['mean'] else 'N/A'}")
                print(f"       空值率: {info['null_rate'] * 100:.2f}%")

        # 重复检查
        if checks["duplicate_check"]:
            dup_info = checks["duplicate_check"]
            print("   重复数据:")
            print(f"     {dup_info['status']}")

    def generate_test_report(self, output_file: Optional[str] = None):
        """生成测试报告"""
        if not self.test_history:
            print("\n⚠️  无测试记录")
            return

        report = {
            "generated_at": datetime.now().isoformat(),
            "total_tests": len(self.test_history),
            "successful_tests": sum(1 for t in self.test_history if t["success"]),
            "failed_tests": sum(1 for t in self.test_history if not t["success"]),
            "tests": self.test_history,
        }

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 测试报告已保存: {output_file}")
        else:
            print("\n📄 测试报告:")
            print(f"   总测试数: {report['total_tests']}")
            print(f"   成功: {report['successful_tests']}")
            print(f"   失败: {report['failed_tests']}")
            print(f"   成功率: {report['successful_tests'] / report['total_tests'] * 100:.1f}%")

            # 显示详细结果
            for i, test in enumerate(self.test_history, 1):
                status = "✅" if test["success"] else "❌"
                print(f"\n   测试 {i}: {status} {test['endpoint_name']}")
                print(f"      响应时间: {test['duration']:.3f}秒")
                if test["error"]:
                    print(f"      错误: {test['error']}")


def interactive_mode():
    """交互式测试模式"""
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║       MyStocks 数据源手动测试工具 v1.0              ║")
    print("╚══════════════════════════════════════════════════════╝")

    tester = DataSourceTester()

    # 检查是否有可用的数据源
    if not tester.manager.registry:
        print("\n❌ 无可用数据源，请先检查配置")
        return

    # 1. 显示可用接口
    print(f"\n✅ 已加载 {len(tester.manager.registry)} 个数据源接口")

    # 按分类分组显示
    categories = {}
    for endpoint_name, source_data in tester.manager.registry.items():
        category = source_data["config"].get("data_category", "UNKNOWN")
        if category not in categories:
            categories[category] = []
        categories[category].append(endpoint_name)

    print(f"\n📂 按分类分组 (共{len(categories)}个分类):")
    category_list = sorted(categories.items())

    for i, (category, endpoints) in enumerate(category_list, 1):
        print(f"\n[{i}] {category} ({len(endpoints)}个接口):")
        for j, endpoint in enumerate(sorted(endpoints)[:5], 1):  # 只显示前5个
            print(f"    [{j}] {endpoint}")
        if len(endpoints) > 5:
            print(f"    ... 还有 {len(endpoints) - 5} 个接口")

    # 2. 选择接口
    while True:
        print("\n请选择:")
        print(f"  [1-{len(category_list)}] 按分类选择")
        print("  [0] 直接输入接口名称")
        print("  [q] 退出")

        choice = input("\n请输入选择: ").strip()

        if choice.lower() == "q":
            print("👋 退出")
            break

        if choice == "0":
            # 直接输入接口名称
            endpoint_name = input("请输入接口名称: ").strip()
            if endpoint_name not in tester.manager.registry:
                print(f"❌ 接口不存在: {endpoint_name}")
                continue
            break
        if choice.isdigit() and 1 <= int(choice) <= len(category_list):
            # 选择分类
            idx = int(choice) - 1
            selected_category, endpoints = category_list[idx]

            print(f"\n{selected_category} 的接口列表:")
            for j, endpoint in enumerate(sorted(endpoints), 1):
                print(f"  [{j}] {endpoint}")

            sub_choice = input(f"\n请选择接口编号 [1-{len(endpoints)}]: ").strip()
            if sub_choice.isdigit() and 1 <= int(sub_choice) <= len(endpoints):
                endpoint_name = sorted(endpoints)[int(sub_choice) - 1]
                break
            print("❌ 无效的编号")
            continue
        print("❌ 无效的选择")
        continue

    # 3. 输入测试参数
    print("\n🔧 请输入测试参数")
    print("   格式: JSON格式的参数字典")
    print('   示例: {"symbol": "000001", "start_date": "20240101", "end_date": "20240131"}')

    param_input = input("\n请输入参数 (留空使用默认参数): ").strip()

    if param_input:
        try:
            test_params = json.loads(param_input)
        except json.JSONDecodeError as e:
            print(f"❌ JSON格式错误: {e}")
            return
    else:
        # 使用默认测试参数
        source_config = tester.manager.registry[endpoint_name]["config"]
        test_params = source_config.get("test_parameters", {})

        if not test_params:
            print("⚠️  该接口无默认测试参数")
            print(f"   可用参数: {list(source_config.get('parameters', {}).keys())}")

            # 让用户手动输入
            print("\n请手动输入参数:")
            test_params = {}
            for param_name, param_config in source_config.get("parameters", {}).items():
                if param_config.get("required", False):
                    value = input(f"  {param_name} (必需): ").strip()
                    if value:
                        test_params[param_name] = value
                else:
                    value = input(f"  {param_name} (可选，留空跳过): ").strip()
                    if value:
                        test_params[param_name] = value

    # 4. 执行测试
    if test_params:
        result = tester.test_data_source(endpoint_name, test_params, verbose=True)

        # 5. 是否继续测试
        while True:
            cont = input("\n是否继续测试其他接口？ [y/n]: ").strip().lower()
            if cont == "n":
                break
            if cont == "y":
                interactive_mode()
                return

    # 6. 生成测试报告
    if len(tester.test_history) > 0:
        save = input("\n是否保存测试报告？ [y/n]: ").strip().lower()
        if save == "y":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"docs/reports/data_source_test_report_{timestamp}.json"
            tester.generate_test_report(report_file)


def command_line_mode(args):
    """命令行测试模式"""
    tester = DataSourceTester()

    # 构建测试参数
    test_params = {}

    if args.symbol:
        test_params["symbol"] = args.symbol
    if args.start_date:
        test_params["start_date"] = args.start_date
    if args.end_date:
        test_params["end_date"] = args.end_date
    if args.params:
        # 额外的参数（JSON格式）
        try:
            extra_params = json.loads(args.params)
            test_params.update(extra_params)
        except json.JSONDecodeError as e:
            print(f"❌ JSON格式错误: {e}")
            return

    # 执行测试
    result = tester.test_data_source(args.endpoint, test_params, verbose=args.verbose)

    # 生成报告
    if args.report:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"docs/reports/data_source_test_report_{timestamp}.json"
        tester.generate_test_report(report_file)
    else:
        tester.generate_test_report()


def main():
    parser = argparse.ArgumentParser(
        description="数据源手动测试工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 交互式模式
  python scripts/tools/manual_data_source_tester.py --interactive

  # 命令行模式
  python scripts/tools/manual_data_source_tester.py \\
      --endpoint akshare.stock_zh_a_hist \\
      --symbol 000001 \\
      --start-date 20240101 \\
      --end-date 20240131 \\
      --verbose

  # 使用额外参数
  python scripts/tools/manual_data_source_tester.py \\
      --endpoint akshare.stock_zh_a_hist \\
      --params '{"symbol":"000001","period":"daily"}' \\
      --report
        """,
    )

    parser.add_argument(
        "--endpoint",
        "-e",
        help="接口名称（如: akshare.stock_zh_a_hist）",
    )
    parser.add_argument("--symbol", "-s", help="股票代码")
    parser.add_argument("--start-date", help="开始日期 (YYYYMMDD)")
    parser.add_argument("--end-date", help="结束日期 (YYYYMMDD)")
    parser.add_argument(
        "--params",
        "-p",
        help="额外参数 (JSON格式)",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="交互式模式",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="详细输出",
    )
    parser.add_argument(
        "--report",
        "-r",
        action="store_true",
        help="生成测试报告",
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.endpoint:
        command_line_mode(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
