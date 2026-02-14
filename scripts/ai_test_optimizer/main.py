#!/usr/bin/env python3
"""
AI智能测试优化器
复用现有测试基础设施，提供智能测试生成和优化功能

核心功能:
1. 基于现有generate_tests.py的增强测试生成
2. 利用classifier.py的智能模块分析
3. 集成性能回归检测和覆盖率优化建议
4. 自动测试质量评估和改进建议

作者: MyStocks AI Team
版本: 1.0
日期: 2025-01-22
"""

import ast
import json
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import argparse
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI智能测试优化器 - 自动分析和改进测试覆盖率"
    )
    parser.add_argument(
        "source_files",
        nargs="+",
        help="源代码文件路径 (支持通配符，如: src/adapters/*.py)",
    )
    parser.add_argument("--config", "-c", help="配置文件路径 (JSON格式)")
    parser.add_argument(
        "--output", "-o", default="test_optimization_report.md", help="输出报告文件路径"
    )
    parser.add_argument(
        "--generate-tests", "-g", action="store_true", help="生成改进的测试代码文件"
    )
    parser.add_argument("--batch", "-b", action="store_true", help="批量处理模式")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出模式")

    args = parser.parse_args()

    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # 初始化优化器
        optimizer = AITestOptimizer(args.config)

        # 扩展文件列表
        source_files = []
        for pattern in args.source_files:
            if "*" in pattern or "?" in pattern:
                source_files.extend(Path().glob(pattern))
            else:
                source_files.append(Path(pattern))

        # 过滤Python文件
        source_files = [
            str(f) for f in source_files if f.suffix == ".py" and f.exists()
        ]

        if not source_files:
            print("❌ 未找到有效的Python文件")
            return 1

        logger.info(f"📁 找到 {len(source_files)} 个文件进行分析")

        # 执行优化分析
        if args.batch:
            results = optimizer.optimize_batch_modules(source_files)
        else:
            results = [
                optimizer.analyze_module_for_optimization(str(f)) for f in source_files
            ]

        # 生成报告
        report = optimizer.generate_optimization_report(results)

        # 保存报告
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ 优化报告已生成: {args.output}")

        # 生成测试文件（如果需要）
        if args.generate_tests:
            test_dir = Path("ai_generated_tests")
            test_dir.mkdir(exist_ok=True)

            for result in results:
                if result.generated_tests:
                    test_file = test_dir / f"test_{result.module_name}_optimized.py"
                    with open(test_file, "w", encoding="utf-8") as f:
                        f.write(f'''
"""
AI优化的测试套件: {result.module_name}
生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}
当前覆盖率: {result.current_coverage:.1f}%
目标覆盖率: {result.target_coverage:.1f}%
"""

import pytest
import time
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from {result.module_name} import *
except ImportError as e:
    pytest.skip(f"无法导入 {{result.module_name}}: {{e}}", allow_module_level=True)

class Test{result.module_name.title()}Optimized:
    """AI优化的测试套件"""

{"".join(result.generated_tests)}
''')
                    print(f"✅ 生成测试文件: {test_file}")

        # 输出摘要
        print("\n📊 优化摘要:")
        print(f"- 分析文件: {len(results)} 个")
        print(
            f"- 平均覆盖率: {sum(r.current_coverage for r in results) / len(results):.1f}%"
        )
        print(
            f"- 需要改进: {sum(1 for r in results if r.current_coverage < optimizer.config['coverage_target'])} 个"
        )

        return 0

    except KeyboardInterrupt:
        print("\n⏹️  用户中断操作")
        return 1
    except Exception as e:
        logger.error(f"💥 优化过程中发生异常: {e}")
        import traceback

        traceback.print_exc()
        return 1


