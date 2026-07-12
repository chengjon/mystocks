#!/usr/bin/env python3
"""数据访问层测试覆盖率分析脚本
分析 PostgreSQL 和 TDengine 访问层的测试覆盖率现状
"""

import subprocess
from pathlib import Path


def run_command(cmd, description=""):
    """运行命令并返回结果"""
    print(f"\n🔍 {description}")
    print(f"执行: {cmd}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"
    except Exception as e:
        return False, "", f"执行错误: {e!s}"


def analyze_file_structure():
    """分析数据访问层文件结构"""
    print("📁 数据访问层文件结构分析:")

    data_access_dir = Path("src/data_access")
    if not data_access_dir.exists():
        print("❌ src/data_access 目录不存在")
        return

    # 列出所有Python文件
    py_files = list(data_access_dir.glob("**/*.py"))
    print(f"📋 找到 {len(py_files)} 个Python文件:")

    for file in sorted(py_files):
        relative_path = file.relative_to(data_access_dir)
        size = file.stat().st_size
        print(f"  📄 {relative_path} ({size:,} bytes)")


def analyze_existing_tests():
    """分析现有测试文件"""
    print("\n📋 现有测试文件分析:")

    test_patterns = [
        "tests/**/*postgresql*.py",
        "tests/**/*tdengine*.py",
        "tests/**/*data_access*.py",
    ]

    for pattern in test_patterns:
        success, output, error = run_command(
            f"find tests -name '{pattern.split('/')[-1]}' 2>/dev/null",
            f"查找测试模式: {pattern}",
        )
        if success and output.strip():
            print(f"  ✅ {pattern}:")
            for line in output.strip().split("\n"):
                print(f"    📄 {line}")
        else:
            print(f"  ❌ {pattern}: 未找到相关测试")


def calculate_test_coverage(module_path):
    """计算指定模块的测试覆盖率"""
    print(f"\n📊 计算 {module_path} 的测试覆盖率:")

    # 检查模块是否存在
    module_file = Path(module_path)
    if not module_file.exists():
        print(f"❌ 模块文件不存在: {module_path}")
        return 0, []

    # 构建测试命令
    module_name = module_path.replace(".py", "").replace("/", ".")

    success, output, error = run_command(
        f"python -c \"import {module_name}; print('Module imported successfully')\"",
        f"测试模块导入: {module_name}",
    )

    if not success:
        print(f"❌ 模块导入失败: {error}")
        return 0, []

    # 运行覆盖率测试（仅针对该模块）
    cmd = f"""coverage run --source={module_path} -m pytest tests/unit/ -k "{Path(module_path).stem}" -v --tb=no --disable-warnings 2>/dev/null || true"""
    success, output, error = run_command(cmd, "运行测试")

    if success:
        # 生成覆盖率报告
        success, coverage_output, coverage_error = run_command(
            f"coverage report --include={module_path}",
            "生成覆盖率报告",
        )

        if success and coverage_output:
            lines = coverage_output.split("\n")
            for line in lines:
                if module_path in line and "%" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            coverage_pct = int(parts[-1].replace("%", ""))
                            print(f"📊 当前覆盖率: {coverage_pct}%")
                            return coverage_pct, []
                        except ValueError:
                            pass

        print("⚠️ 无法解析覆盖率报告")
        return 0, []
    print(f"❌ 测试执行失败: {error}")
    return 0, []


def identify_test_gaps(module_path, current_coverage, target_coverage):
    """识别测试覆盖率缺口"""
    print(f"\n🔍 识别测试缺口 (目标: {target_coverage}%):")

    gap = target_coverage - current_coverage
    if gap <= 0:
        print("✅ 已达到目标覆盖率")
        return []

    print(f"📈 需要提升 {gap}% 的覆盖率")

    # 分析模块内容，建议测试覆盖的功能
    module_file = Path(module_path)
    if not module_file.exists():
        return []

    suggestions = []

    try:
        with open(module_file, encoding="utf-8") as f:
            content = f.read()

        # 分析类和方法
        lines = content.split("\n")
        classes = []
        methods = []
        functions = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("class "):
                class_name = stripped.split("(")[0].replace("class ", "").strip(":")
                classes.append((class_name, i + 1))
            elif stripped.startswith("def ") and "def __init__" not in stripped:
                if "self" in stripped:  # 方法
                    method_name = stripped.split("(")[0].replace("def ", "").strip()
                    methods.append((method_name, i + 1))
                else:  # 函数
                    func_name = stripped.split("(")[0].replace("def ", "").strip()
                    functions.append((func_name, i + 1))

        print(
            f"📋 发现 {len(classes)} 个类, {len(methods)} 个方法, {len(functions)} 个函数",
        )

        # 建议测试项目
        if classes:
            suggestions.append(f"添加 {len(classes)} 个类的单元测试")
        if methods:
            suggestions.append(f"添加 {len(methods)} 个方法的单元测试")
        if functions:
            suggestions.append(f"添加 {len(functions)} 个函数的单元测试")

        # 建议测试场景
        suggestions.extend(
            [
                "添加错误处理和异常情况的测试",
                "添加边界条件测试",
                "添加集成测试场景",
                "添加性能测试用例",
            ],
        )

    except Exception as e:
        print(f"❌ 分析模块失败: {e}")
        suggestions.append("分析模块代码结构")

    return suggestions


def generate_test_plan(postgresql_coverage, tdengine_coverage):
    """生成测试改进计划"""
    print("\n📋 测试覆盖率改进计划:")
    print(f"🔹 PostgreSQL Access: {postgresql_coverage}% (目标: 67%)")
    print(f"🔹 TDengine Access: {tdengine_coverage}% (目标: 56%)")

    plan = []

    if postgresql_coverage < 67:
        plan.append(
            {
                "module": "PostgreSQL Access",
                "current": postgresql_coverage,
                "target": 67,
                "priority": "HIGH" if postgresql_coverage < 50 else "MEDIUM",
            },
        )

    if tdengine_coverage < 56:
        plan.append(
            {
                "module": "TDengine Access",
                "current": tdengine_coverage,
                "target": 56,
                "priority": "HIGH" if tdengine_coverage < 40 else "MEDIUM",
            },
        )

    # 按优先级排序
    plan.sort(key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x["priority"]])

    return plan


def main():
    """主函数"""
    print("🔍 MyStocks 数据访问层测试覆盖率分析")
    print("=" * 50)

    # 1. 分析文件结构
    analyze_file_structure()

    # 2. 分析现有测试
    analyze_existing_tests()

    # 3. 计算当前测试覆盖率
    pg_coverage, _ = calculate_test_coverage("src/data_access/postgresql_access.py")
    td_coverage, _ = calculate_test_coverage("src/data_access/tdengine_access.py")

    # 4. 识别测试缺口
    pg_suggestions = identify_test_gaps(
        "src/data_access/postgresql_access.py",
        pg_coverage,
        67,
    )
    td_suggestions = identify_test_gaps(
        "src/data_access/tdengine_access.py",
        td_coverage,
        56,
    )

    # 5. 生成改进计划
    plan = generate_test_plan(pg_coverage, td_coverage)

    print("\n📋 测试覆盖率改进计划:")
    for item in plan:
        print(
            f"  🎯 {item['module']}: {item['current']}% → {item['target']}% (优先级: {item['priority']})",
        )

    # 6. 保存分析结果
    result = {
        "postgresql_coverage": pg_coverage,
        "tdengine_coverage": td_coverage,
        "postgresql_target": 67,
        "tdengine_target": 56,
        "plan": plan,
        "postgresql_suggestions": pg_suggestions,
        "tdengine_suggestions": td_suggestions,
    }

    import json

    with open("data_access_coverage_analysis.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n💾 分析结果已保存到: data_access_coverage_analysis.json")

    # 7. 生成下一步行动计划
    print("\n🚀 下一步行动计划:")
    if pg_coverage < 67:
        print(f"  1. 为 PostgreSQL Access 创建单元测试 (需要提升 {67 - pg_coverage}%)")
    if td_coverage < 56:
        print(f"  2. 为 TDengine Access 创建单元测试 (需要提升 {56 - td_coverage}%)")
    print("  3. 运行覆盖率验证测试")
    print("  4. 更新技术债务修复计划")


if __name__ == "__main__":
    main()
