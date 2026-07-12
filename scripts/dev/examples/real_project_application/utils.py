#!/usr/bin/env python3
"""AI测试优化器真实项目应用示例
演示如何在MyStocks项目中实际应用AI测试优化器

应用场景:
1. 核心模块质量提升
2. 新功能开发测试指导
3. 代码重构支持
4. 团队质量监控
5. 持续改进循环

作者: MyStocks AI Team
版本: 1.0
日期: 2025-01-22
"""

import sys
from pathlib import Path


# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """主函数"""
    print("🚀 AI测试优化器真实项目应用演示")
    print("演示AI测试优化器在MyStocks项目中的实际应用")
    print("=" * 60)

    app = RealProjectApplication()

    try:
        # 场景1: 核心模块质量提升
        app.scenario_1_core_module_quality_improvement()

        # 场景2: 新功能开发测试指导
        app.scenario_2_new_feature_development()

        # 场景3: 代码重构支持
        app.scenario_3_code_refactoring_support()

        # 场景4: 团队质量监控
        app.scenario_4_team_quality_monitoring()

        # 场景5: 持续改进循环
        app.scenario_5_continuous_improvement_cycle()

        print("\n" + "=" * 60)
        print("🎉 真实项目应用演示完成！")
        print(f"📁 所有报告已保存到: {app.application_log.parent}")
        print(f"📋 应用日志: {app.application_log}")

    except KeyboardInterrupt:
        print("\n⏹️  演示已中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback

        traceback.print_exc()
