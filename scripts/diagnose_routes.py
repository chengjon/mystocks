#!/usr/bin/env python3
"""
路由注册诊断脚本

诊断哪些路由模块成功导入，哪些失败

Author: Backend CLI (Claude Code)
Date: 2025-12-31
"""

import sys
import os
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path("/opt/claude/mystocks_phase7_backend/web/backend")
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent))

# 所有应该在main.py中注册的路由模块
ROUTE_MODULES = [
    # Standard API Routers
    ("data", "app.api.data"),
    ("data_quality", "app.api.data_quality"),
    ("auth", "app.api.auth"),
    ("system", "app.api.system"),
    ("indicators", "app.api.indicators"),
    ("market", "app.api.market"),
    ("market_v2", "app.api.market_v2"),
    ("tdx", "app.api.tdx"),
    ("metrics", "app.api.metrics"),
    ("pool_monitoring", "app.api.v1.pool_monitoring"),
    ("cache", "app.api.cache"),
    ("tasks", "app.api.tasks"),
    ("trade", "app.api.trade"),
    ("strategy", "app.api.strategy"),
    ("monitoring", "app.api.monitoring"),
    ("technical_analysis", "app.api.technical_analysis"),
    ("dashboard", "app.api.dashboard"),
    ("strategy_mgmt", "app.api.strategy_mgmt"),
    ("multi_source", "app.api.multi_source"),
    ("announcement", "app.api.announcement"),
    ("strategy_management", "app.api.strategy_management"),
    ("risk_management", "app.api.risk_management"),
    ("sse_endpoints", "app.api.sse_endpoints"),
    ("industry_concept_analysis", "app.api.industry_concept_analysis"),
    ("contract", "app.api.contract"),
    ("health", "app.api.health"),
]

print("=" * 70)
print("路由模块导入诊断")
print("=" * 70)
print()

# 测试结果
success_modules = []
failed_modules = []
errors = {}

for module_name, module_path in ROUTE_MODULES:
    try:
        print(f"[测试] 导入 {module_path}...", end=" ")

        # 尝试导入模块
        parts = module_path.split('.')
        module = __import__(module_path)

        # 获取最后的模块部分
        for part in parts[1:]:
            module = getattr(module, part)

        # 检查是否有router属性
        if hasattr(module, 'router'):
            router = module.router
            print(f"✓ (router存在)")
            success_modules.append((module_name, module_path))
        else:
            print(f"⚠ (没有router属性)")
            failed_modules.append((module_name, module_path, "No router attribute"))

    except ImportError as e:
        error_msg = f"ImportError: {str(e)}"
        print(f"✗ {error_msg}")
        failed_modules.append((module_name, module_path, error_msg))
        errors[module_name] = str(e)

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"✗ {error_msg}")
        failed_modules.append((module_name, module_path, error_msg))
        errors[module_name] = str(e)

print()
print("=" * 70)
print("诊断结果")
print("=" * 70)
print()

print(f"总计: {len(ROUTE_MODULES)} 个模块")
print(f"成功导入: {len(success_modules)} 个 ({len(success_modules)/len(ROUTE_MODULES)*100:.1f}%)")
print(f"导入失败: {len(failed_modules)} 个 ({len(failed_modules)/len(ROUTE_MODULES)*100:.1f}%)")
print()

if success_modules:
    print("✓ 成功导入的模块:")
    for module_name, module_path in success_modules:
        print(f"  - {module_name}: {module_path}")
    print()

if failed_modules:
    print("✗ 导入失败的模块:")
    for module_name, module_path, error in failed_modules:
        print(f"  - {module_name}: {error}")
        if len(error) > 80:
            print(f"    详细错误: {error[:80]}...")
    print()

# 分析错误类型
print("=" * 70)
print("错误分析")
print("=" * 70)
print()

error_types = {}
for module_name, error_msg in errors.items():
    error_type = error_msg.split(':')[0] if ':' in error_msg else 'Unknown'
    if error_type not in error_types:
        error_types[error_type] = []
    error_types[error_type].append(module_name)

if error_types:
    print("按错误类型分组:")
    for error_type, modules in sorted(error_types.items()):
        print(f"\n  {error_type} ({len(modules)} 个模块):")
        for module in modules:
            print(f"    - {module}")
    print()

# 修复建议
print("=" * 70)
print("修复建议")
print("=" * 70)
print()

# 根据错误类型提供修复建议
if 'No module named' in str(errors):
    missing_modules = set()
    for error in errors.values():
        if 'No module named' in error:
            # 提取缺失的模块名
            start = error.find("'") + 1
            end = error.find("'", start)
            if start > 0 and end > start:
                missing_modules.add(error[start:end])

    if missing_modules:
        print("发现缺失的Python模块:")
        for module in sorted(missing_modules):
            print(f"  - {module}")
        print()
        print("修复建议:")
        print("  1. 安装缺失的依赖: pip install <module>")
        print("  2. 检查requirements.txt是否包含所有依赖")
        print("  3. 确保虚拟环境激活")
        print()

if 'src' in str(errors):
    print("发现src模块导入问题:")
    print("  原因: 项目结构变更，src模块路径未正确配置")
    print()
    print("修复建议:")
    print("  1. 更新PYTHONPATH环境变量")
    print("  2. 使用相对导入而非绝对导入")
    print("  3. 检查模块导入路径配置")
    print()

print("=" * 70)
