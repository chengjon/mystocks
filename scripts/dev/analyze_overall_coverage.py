#!/usr/bin/env python3
"""
整体测试覆盖率分析脚本
分析项目中所有模块的测试覆盖率，识别优先改进目标
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description=""):
    """运行命令并返回结果"""
    print(f"\n🔍 {description}")
    print(f"执行: {cmd}")

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=300
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"
    except Exception as e:
        return False, "", f"执行错误: {str(e)}"


def parse_coverage_report():
    """解析覆盖率报告"""
    success, output, error = run_command("coverage report", "生成覆盖率报告")

    if not success:
        print(f"❌ 无法生成覆盖率报告: {error}")
        return []

    lines = output.strip().split("\n")
    modules = []

    for line in lines:
        # 跳过标题和分隔线
        if (
            "Name" in line
            or "TOTAL" in line
            or "----------" in line
            or "-------------------------------------------------------------------------------"
            in line
        ):
            continue

        parts = line.split()
        if len(parts) >= 4 and parts[0].startswith("src/"):
            try:
                name = parts[0]
                stmts = int(parts[1])
                miss = int(parts[2])
                coverage_pct = int(parts[3].rstrip("%"))

                modules.append(
                    {
                        "name": name,
                        "statements": stmts,
                        "missing": miss,
                        "coverage": coverage_pct,
                    }
                )
            except (ValueError, IndexError):
                continue

    return modules


def categorize_modules(modules):
    """将模块按覆盖率分类"""
    categories = {
        "high_coverage": [],  # > 70%
        "medium_coverage": [],  # 30-70%
        "low_coverage": [],  # 10-30%
        "minimal_coverage": [],  # 1-10%
        "no_coverage": [],  # 0%
    }

    for module in modules:
        coverage = module["coverage"]
        if coverage > 70:
            categories["high_coverage"].append(module)
        elif 30 <= coverage <= 70:
            categories["medium_coverage"].append(module)
        elif 10 <= coverage < 30:
            categories["low_coverage"].append(module)
        elif 1 <= coverage < 10:
            categories["minimal_coverage"].append(module)
        else:
            categories["no_coverage"].append(module)

    return categories


def identify_priority_modules(modules, exclude_patterns=None):
    """识别优先改进的模块"""
    if exclude_patterns is None:
        exclude_patterns = ["data_access/", "test_", "__pycache__"]

    # 排除指定模式的模块
    filtered_modules = []
    for module in modules:
        should_exclude = False
        for pattern in exclude_patterns:
            if pattern in module["name"]:
                should_exclude = True
                break
        if not should_exclude:
            filtered_modules.append(module)

    # 按影响程度排序：语句数量多且覆盖率低的优先
    priority_modules = sorted(
        filtered_modules,
        key=lambda x: (x["statements"] * (100 - x["coverage"]), x["statements"]),
        reverse=True,
    )

    return priority_modules


def identify_high_value_targets(modules):
    """识别高价值改进目标"""
    # 高价值目标：语句数多、有一定覆盖率的模块
    high_value = [
        module
        for module in modules
        if module["statements"] > 50 and 10 < module["coverage"] < 50
    ]

    return sorted(high_value, key=lambda x: x["coverage"])


def generate_recommendations(categories, priority_modules):
    """生成改进建议"""
    recommendations = []

    # 优先级1: 低覆盖率但重要模块
    priority_1 = priority_modules[:5]
    if priority_1:
        recommendations.append(
            {
                "priority": 1,
                "title": "优先改进模块 (低覆盖率)",
                "modules": priority_1,
                "action": "立即添加单元测试，目标覆盖率80%",
            }
        )

    # 优先级2: 中等覆盖率模块
    medium_modules = [m for m in categories["medium_coverage"] if m["statements"] > 30][
        :5
    ]
    if medium_modules:
        recommendations.append(
            {
                "priority": 2,
                "title": "中等覆盖率模块优化",
                "modules": medium_modules,
                "action": "补充边界情况和错误处理测试，目标覆盖率85%",
            }
        )

    # 优先级3: 零覆盖率模块
    no_coverage_modules = [
        m for m in categories["no_coverage"] if m["statements"] > 20
    ][:5]
    if no_coverage_modules:
        recommendations.append(
            {
                "priority": 3,
                "title": "零覆盖率模块基础测试",
                "modules": no_coverage_modules,
                "action": "创建基础单元测试框架，目标覆盖率60%",
            }
        )

    return recommendations


def analyze_todo_comments():
    """分析TODO注释"""
    print("\n📋 分析TODO注释...")

    # 查找所有TODO注释
    success, output, error = run_command(
        "find src/ -name '*.py' -exec grep -Hn 'TODO\\|FIXME\\|XXX' {} \\;",
        "查找TODO注释",
    )

    todos = []
    if success and output:
        for line in output.strip().split("\n"):
            if "TODO" in line or "FIXME" in line or "XXX" in line:
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    todos.append(
                        {
                            "file": parts[0],
                            "line": parts[1],
                            "content": parts[2].strip(),
                        }
                    )

    print(f"📊 发现 {len(todos)} 个TODO/FIXME/XXX注释")

    # 按文件分组
    todo_by_file = {}
    for todo in todos:
        file_path = todo["file"]
        if file_path not in todo_by_file:
            todo_by_file[file_path] = []
        todo_by_file[file_path].append(todo)

    # 按TODO数量排序
    sorted_files = sorted(todo_by_file.items(), key=lambda x: len(x[1]), reverse=True)

    return todos, sorted_files[:10]  # 返回前10个TODO最多的文件


def main():
    """主函数"""
    print("🔍 MyStocks 整体测试覆盖率分析")
    print("=" * 50)

    # 1. 生成覆盖率报告
    print("\n📊 生成测试覆盖率报告...")
    modules = parse_coverage_report()
    print(f"📋 分析了 {len(modules)} 个模块")

    # 2. 分类分析
    categories = categorize_modules(modules)

    print(f"\n📈 覆盖率分类统计:")
    print(f"  🟢 高覆盖率 (>70%): {len(categories['high_coverage'])} 个模块")
    print(f"  🟡 中等覆盖率 (30-70%): {len(categories['medium_coverage'])} 个模块")
    print(f"  🟠 低覆盖率 (10-30%): {len(categories['low_coverage'])} 个模块")
    print(f"  🔴 极低覆盖率 (1-10%): {len(categories['minimal_coverage'])} 个模块")
    print(f"  ⚫ 零覆盖率 (0%): {len(categories['no_coverage'])} 个模块")

    # 3. 识别优先改进目标（排除data_access）
    print(f"\n🎯 识别优先改进目标（排除data_access）...")
    priority_modules = identify_priority_modules(modules)

    print(f"\n🔝 Top 10 优先改进模块:")
    for i, module in enumerate(priority_modules[:10], 1):
        print(f"  {i}. {module['name']}")
        print(f"     📊 覆盖率: {module['coverage']}% ({module['statements']} 行语句)")
        print(f"     🎯 影响: {module['missing']} 行未覆盖")

    # 4. 识别高价值目标
    high_value_targets = identify_high_value_targets(modules)

    print(f"\n💎 高价值改进目标（有基础但需提升）:")
    for i, module in enumerate(high_value_targets[:5], 1):
        print(f"  {i}. {module['name']}")
        print(f"     📊 当前覆盖率: {module['coverage']}%")
        print(f"     🎯 目标覆盖率: 85%")

    # 5. 生成改进建议
    recommendations = generate_recommendations(categories, priority_modules)

    print(f"\n📋 改进建议:")
    for rec in recommendations:
        print(f"\n  🎯 优先级 {rec['priority']}: {rec['title']}")
        print(f"     📋 模块: {len(rec['modules'])} 个")
        print(f"     🔧 行动: {rec['action']}")
        print(f"     📄 文件:")
        for module in rec["modules"][:3]:  # 显示前3个
            print(f"       - {module['name']} ({module['coverage']}%)")
        if len(rec["modules"]) > 3:
            print(f"       - ... 还有 {len(rec['modules']) - 3} 个")

    # 6. 分析TODO注释
    todos, todo_files = analyze_todo_comments()

    print(f"\n📝 TODO注释分析 (Top 10文件):")
    for i, (file_path, file_todos) in enumerate(todo_files, 1):
        print(f"  {i}. {file_path}")
        print(f"     📝 TODO数量: {len(file_todos)}")
        for todo in file_todos[:2]:  # 显示前2个
            print(f"     • L{todo['line']}: {todo['content'][:60]}...")

    # 7. 保存分析结果
    analysis_result = {
        "total_modules": len(modules),
        "categories": {k: len(v) for k, v in categories.items()},
        "priority_modules": priority_modules[:10],
        "high_value_targets": high_value_targets[:5],
        "recommendations": recommendations,
        "todo_count": len(todos),
        "todo_files": [{"file": f, "count": len(todos)} for f, todos in todo_files],
    }

    import json

    with open("overall_coverage_analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)

    print(f"\n💾 分析结果已保存到: overall_coverage_analysis.json")

    # 8. 生成下一步行动计划
    print(f"\n🚀 Phase 3 行动计划:")
    print(f"  1. 🎯 优先改进前5个低覆盖率模块")
    print(f"  2. 💎 为中等覆盖率模块补充测试")
    print(f"  3. 📝 处理高优先级TODO注释")
    print(f"  4. 📊 验证改进效果")


if __name__ == "__main__":
    main()
