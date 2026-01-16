#!/usr/bin/env python3
"""
AI Test Optimizer 健康检查
验证工具包安装和配置
"""

import sys
from pathlib import Path


def check_installation():
    """检查工具包安装状态"""
    print("🔍 AI Test Optimizer 健康检查")
    print("=" * 40)

    # 检查核心组件
    components = {
        "Smart AI Analyzer": "bin/smart_ai_analyzer.py",
        "AI Test Optimizer": "bin/ai_test_optimizer.py",
        "Simple Optimizer": "bin/ai_test_optimizer_simple.py",
        "Monitor": "plugins/monitoring/ai_optimizer_monitor.py",
        "Analyzer": "plugins/analysis/usage_feedback_analyzer.py",
    }

    toolkit_root = Path(__file__).parent
    all_ok = True

    for name, path in components.items():
        component_path = toolkit_root / path
        if component_path.exists():
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - 缺少: {path}")
            all_ok = False

    # 检查配置
    config_path = toolkit_root / "config" / "ai_toolkit_config.yaml"
    if config_path.exists():
        print("✅ 配置文件")
    else:
        print("❌ 配置文件 - 缺少: config/ai_toolkit_config.yaml")
        all_ok = False

    print("=" * 40)

    if all_ok:
        print("🎉 工具包安装完成!")
        return True
    else:
        print("⚠️ 工具包安装不完整，请重新安装")
        return False


if __name__ == "__main__":
    success = check_installation()
    sys.exit(0 if success else 1)
