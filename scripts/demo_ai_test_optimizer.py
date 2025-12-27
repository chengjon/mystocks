#!/usr/bin/env python3
"""
AI测试优化器使用示例
演示如何使用现有的测试基础设施进行智能测试优化

使用场景:
1. 单个文件优化
2. 批量目录优化
3. 基于现有工具的增强分析
4. 集成CI/CD流程
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def demo_single_file_optimization():
    """演示单个文件优化"""
    print("🎯 演示1: 单个文件智能优化")
    print("=" * 50)

    try:
        from ai_test_optimizer import AITestOptimizer

        # 选择一个代表性模块进行优化
        target_file = "src/adapters/data_validator.py"

        if not Path(target_file).exists():
            print(f"❌ 目标文件不存在: {target_file}")
            return

        optimizer = AITestOptimizer("config/ai_test_optimizer_config.json")
        result = optimizer.analyze_module_for_optimization(target_file)

        print(f"📊 模块: {result.module_name}")
        print(f"📈 当前覆盖率: {result.current_coverage:.1f}%")
        print(f"🎯 目标覆盖率: {result.target_coverage:.1f}%")
        print(f"⭐ 质量评分: {result.quality_score:.1f}/100")

        print("\n💡 优化建议:")
        for i, suggestion in enumerate(result.optimization_suggestions, 1):
            print(f"  {i}. {suggestion}")

        print(f"\n📝 生成测试数: {len(result.generated_tests)}")

        if result.generated_tests:
            print("\n🔧 示例生成的测试代码:")
            print(result.generated_tests[0][:200] + "...")

    except Exception as e:
        print(f"❌ 演示失败: {e}")


def demo_batch_optimization():
    """演示批量优化"""
    print("\n🚀 演示2: 批量目录智能优化")
    print("=" * 50)

    try:
        from ai_test_optimizer import AITestOptimizer

        # 选择核心目录进行批量优化
        target_files = [
            "src/adapters/data_validator.py",
            "src/adapters/base_adapter.py",
            "src/core/exceptions.py",
        ]

        # 过滤存在的文件
        existing_files = [f for f in target_files if Path(f).exists()]

        if not existing_files:
            print("❌ 没有找到可优化的文件")
            return

        optimizer = AITestOptimizer("config/ai_test_optimizer_config.json")
        results = optimizer.optimize_batch_modules(existing_files)

        print(f"📁 优化文件数: {len(results)}")

        # 排序并显示结果
        sorted_results = sorted(results, key=lambda r: r.current_coverage)

        print("\n📊 优化结果排序（按覆盖率升序）:")
        for i, result in enumerate(sorted_results, 1):
            status = (
                "✅"
                if result.current_coverage >= optimizer.config["coverage_target"]
                else "⚠️"
            )
            print(
                f"  {i}. {status} {result.module_name}: {result.current_coverage:.1f}% (质量: {result.quality_score:.1f})"
            )

        # 生成报告
        report = optimizer.generate_optimization_report(results)
        report_file = "batch_optimization_report.md"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n📄 批量优化报告已生成: {report_file}")

    except Exception as e:
        print(f"❌ 演示失败: {e}")


def demo_integration_with_existing_tools():
    """演示与现有工具的集成"""
    print("\n🔗 演示3: 现有工具集成")
    print("=" * 50)

    try:
        # 集成现有的测试生成器
        print("1. 集成测试生成器 (generate_tests.py):")
        try:
            from scripts.dev.generate_tests import TestGenerator

            target_file = "src/adapters/data_validator.py"
            if Path(target_file).exists():
                generator = TestGenerator(target_file)
                items = generator.extract_classes_and_functions()

                print(f"   📋 发现 {len(items)} 个类/函数")
                for name, item_type, signatures in items[:3]:
                    icon = "🏗️" if item_type == "class" else "⚡"
                    print(f"   {icon} {item_type}: {name}")

        except Exception as e:
            print(f"   ⚠️  测试生成器集成失败: {e}")

        # 集成模块分类器
        print("\n2. 集成模块分类器 (classifier.py):")
        try:
            from scripts.analysis.classifier import ModuleClassifier

            classifier = ModuleClassifier()
            print("   📊 可用分类规则:")
            print(f"      - 核心功能指标: {len(classifier.core_indicators)} 条规则")
            print(
                f"      - 辅助功能指标: {len(classifier.auxiliary_indicators)} 条规则"
            )
            print(
                f"      - 基础设施指标: {len(classifier.infrastructure_indicators)} 条规则"
            )
            print(
                f"      - 监控功能指标: {len(classifier.monitoring_indicators)} 条规则"
            )
            print(f"      - 工具功能指标: {len(classifier.utility_indicators)} 条规则")

        except Exception as e:
            print(f"   ⚠️  模块分类器集成失败: {e}")

        # 集成AI工作流
        print("\n3. 集成AI自动化工作流:")
        try:
            from scripts.ai_automation_workflow import AIAutomationWorkflow

            workflow = AIAutomationWorkflow()
            print("   🤖 AI工作流组件:")
            print("      - 数据获取: ✅")
            print("      - AI分析: ✅")
            print("      - 策略决策: ✅")
            print("      - 性能监控: ✅")

        except Exception as e:
            print(f"   ⚠️  AI工作流集成失败: {e}")

    except Exception as e:
        print(f"❌ 集成演示失败: {e}")


def demo_ci_cd_integration():
    """演示CI/CD集成"""
    print("\n🔄 演示4: CI/CD集成建议")
    print("=" * 50)

    ci_cd_recommendations = [
        {
            "stage": "代码检查",
            "tool": "AI测试优化器",
            "command": "python scripts/ai_test_optimizer.py src/core/*.py --batch --generate-tests",
            "purpose": "在PR中自动生成测试优化建议",
        },
        {
            "stage": "测试执行",
            "tool": "增强的测试套件",
            "command": "pytest ai_generated_tests/ --cov=src --cov-fail-under=90",
            "purpose": "运行AI优化的测试套件",
        },
        {
            "stage": "质量门禁",
            "tool": "质量评分",
            "command": "python scripts/ai_test_optimizer.py src/ --quality-gate",
            "purpose": "基于AI评分的质量门禁",
        },
        {
            "stage": "性能监控",
            "tool": "性能基准",
            "command": "python scripts/performance/regression_test.py --ai-optimized",
            "purpose": "AI驱动的性能回归检测",
        },
    ]

    print("💡 CI/CD集成建议:")
    for i, rec in enumerate(ci_cd_recommendations, 1):
        print(f"\n{i}. {rec['stage']}:")
        print(f"   工具: {rec['tool']}")
        print(f"   命令: {rec['command']}")
        print(f"   目的: {rec['purpose']}")

    print("\n📋 GitHub Actions 工作流示例:")
    print("""
- name: AI Test Optimization
  run: |
    python scripts/ai_test_optimizer.py src/core/*.py \\
      --batch --generate-tests --output optimization-report.md

- name: Run AI-Optimized Tests
  run: |
    pytest ai_generated_tests/ --cov=src --cov-report=xml

- name: Quality Gate Check
  run: |
    python scripts/ai_test_optimizer.py src/ --quality-gate
""")


def demo_advanced_features():
    """演示高级功能"""
    print("\n🧠 演示5: 高级功能")
    print("=" * 50)

    try:
        from ai_test_optimizer import AITestOptimizer

        optimizer = AITestOptimizer()

        print("🔧 高级优化策略:")
        strategies = optimizer.config.get("optimization_strategies", [])
        for i, strategy in enumerate(strategies, 1):
            print(f"  {i}. {strategy}")

        print("\n📊 质量门禁配置:")
        gates = optimizer.config.get("quality_gates", {})
        for gate, value in gates.items():
            print(f"  {gate}: {value}")

        print("\n🎯 测试模板:")
        templates = optimizer.config.get("test_templates", {})
        for template_type, template in templates.items():
            print(f"  {template_type}: {template}")

        # 演示配置自定义
        print("\n⚙️ 自定义配置示例:")
        custom_config = {
            "coverage_target": 98.0,  # 更严格的覆盖率目标
            "complexity_limit": 8,  # 更严格的复杂度限制
            "optimization_strategies": [
                "security_testing",
                "load_testing",
                "chaos_testing",
            ],
        }

        print("  可以通过配置文件自定义:")
        for key, value in custom_config.items():
            print(f"    {key}: {value}")

    except Exception as e:
        print(f"❌ 高级功能演示失败: {e}")


def main():
    """主演示函数"""
    print("🤖 AI测试优化器完整演示")
    print("基于现有测试基础设施的智能测试生成与优化")
    print("=" * 60)

    start_time = time.time()

    # 执行各个演示
    demo_single_file_optimization()
    demo_batch_optimization()
    demo_integration_with_existing_tools()
    demo_ci_cd_integration()
    demo_advanced_features()

    # 总结
    duration = time.time() - start_time
    print(f"\n✅ 演示完成！总用时: {duration:.2f}秒")

    print("\n📚 更多资源:")
    print("  - AI测试优化器: scripts/ai_test_optimizer.py")
    print("  - 配置文件: config/ai_test_optimizer_config.json")
    print("  - 现有测试生成器: scripts/dev/generate_tests.py")
    print("  - 模块分类器: scripts/analysis/classifier.py")
    print("  - AI工作流: scripts/ai_automation_workflow.py")

    print("\n🚀 快速开始:")
    print(
        "  python scripts/ai_test_optimizer.py src/adapters/*.py --batch --generate-tests"
    )


if __name__ == "__main__":
    main()
