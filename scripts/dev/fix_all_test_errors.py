#!/usr/bin/env python3
"""分析和修复所有测试错误

步骤:
1. 收集所有测试错误
2. 按错误类型分类
3. 批量修复常见问题

创建日期: 2026-01-03
用途: 修复剩余83个测试错误
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent


def collect_test_errors() -> List[Dict]:
    """收集所有测试错误

    Returns:
        错误信息列表

    """
    print("正在收集测试错误...")

    result = subprocess.run(
        ["pytest", "--collect-only", "-q"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )

    errors = []
    current_file = None
    current_error = None

    for line in result.stderr.split("\n"):
        if "ERROR collecting" in line:
            # 提取文件名
            match = re.search(r"ERROR collecting (.+?) _(.*?)_", line)
            if match:
                current_file = match.group(1)
                current_error = {"file": current_file, "type": "unknown", "details": []}
                errors.append(current_error)
        elif current_error and line.strip():
            current_error["details"].append(line.strip())

    return errors


def categorize_errors(errors: List[Dict]) -> Dict[str, List[Dict]]:
    """按类型分类错误

    Args:
        errors: 错误列表

    Returns:
        分类后的错误字典

    """
    categories = {
        "import_error": [],  # 导入错误 (ModuleNotFoundError)
        "attribute_error": [],  # 属性错误 (API变更)
        "file_not_found": [],  # 文件不存在
        "syntax_error": [],  # 语法错误
        "other": [],  # 其他错误
    }

    for error in errors:
        details = "\n".join(error["details"])

        if "ModuleNotFoundError" in details:
            error["type"] = "import_error"
            categories["import_error"].append(error)
        elif "AttributeError" in details:
            error["type"] = "attribute_error"
            categories["attribute_error"].append(error)
        elif "FileNotFoundError" in details:
            error["type"] = "file_not_found"
            categories["file_not_found"].append(error)
        elif "SyntaxError" in details:
            error["type"] = "syntax_error"
            categories["syntax_error"].append(error)
        else:
            error["type"] = "other"
            categories["other"].append(error)

    return categories


def fix_scripts_tests_imports():
    """修复 scripts/tests/ 目录下文件的 sys.path 问题"""
    print("\n修复 scripts/tests/ 导入路径...")

    scripts_tests_dir = PROJECT_ROOT / "scripts" / "tests"
    if not scripts_tests_dir.exists():
        print("  ✅ scripts/tests/ 目录不存在，跳过")
        return

    test_files = list(scripts_tests_dir.rglob("test_*.py"))

    for test_file in test_files:
        try:
            content = test_file.read_text(encoding="utf-8")

            # 检查是否已经有 sys.path 设置
            if "sys.path.insert" in content:
                print(f"  ⏭️  {test_file.relative_to(PROJECT_ROOT)} - 已有sys.path设置")
                continue

            # 检查是否使用 from src. 导入
            if "from src." in content:
                # 在第一个导入前添加 sys.path 设置
                lines = content.split("\n")
                insert_pos = 0

                # 找到第一个导入语句的位置
                for i, line in enumerate(lines):
                    if line.strip().startswith("import ") or line.strip().startswith("from "):
                        insert_pos = i
                        break

                # 添加 sys.path 设置
                sys_path_insert = [
                    "",
                    "import sys",
                    "import os",
                    "",
                    "# 添加项目根目录到路径",
                    "project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))",
                    "sys.path.insert(0, project_root)",
                    "",
                ]

                # 插入到导入语句之前
                lines[insert_pos:insert_pos] = sys_path_insert

                # 写回文件
                test_file.write_text("\n".join(lines), encoding="utf-8")
                print(f"  ✅ {test_file.relative_to(PROJECT_ROOT)} - 已添加sys.path设置")

        except Exception as e:
            print(f"  ❌ {test_file.relative_to(PROJECT_ROOT)} - 错误: {e}")


def fix_api_compatibility():
    """修复API兼容性问题"""
    print("\n修复API兼容性问题...")

    # 常见的API变更映射
    api_replacements = [
        # ConfigDrivenTableManager API变更
        (r"\.initialize_all_tables\(", ".initialize_tables("),
    ]

    # 扫描所有测试文件
    test_dirs = [
        PROJECT_ROOT / "tests",
        PROJECT_ROOT / "scripts" / "tests",
    ]

    for test_dir in test_dirs:
        if not test_dir.exists():
            continue

        for test_file in test_dir.rglob("test_*.py"):
            try:
                content = test_file.read_text(encoding="utf-8")
                original_content = content

                for pattern, replacement in api_replacements:
                    content = re.sub(pattern, replacement, content)

                if content != original_content:
                    test_file.write_text(content, encoding="utf-8")
                    print(f"  ✅ {test_file.relative_to(PROJECT_ROOT)} - API兼容性已修复")

            except Exception as e:
                print(f"  ❌ {test_file.relative_to(PROJECT_ROOT)} - 错误: {e}")


def generate_error_report(errors: List[Dict], categories: Dict[str, List[Dict]]):
    """生成错误报告

    Args:
        errors: 所有错误
        categories: 分类后的错误

    """
    report_path = PROJECT_ROOT / "docs" / "reports" / "TEST_ERRORS_ANALYSIS.md"

    report_content = f"""# 测试错误分析报告

**生成日期**: 2026-01-03
**错误总数**: {len(errors)}

---

## 错误分类

### 1. 导入错误 (ModuleNotFoundError)
**数量**: {len(categories["import_error"])}
**状态**: 需要修复

**文件列表**:
"""

    for error in categories["import_error"][:10]:  # 只显示前10个
        report_content += f"- `{error['file']}`\n"

    if len(categories["import_error"]) > 10:
        report_content += f"- ... 还有 {len(categories['import_error']) - 10} 个文件\n"

    report_content += f"""
### 2. 属性错误 (AttributeError - API变更)
**数量**: {len(categories["attribute_error"])}
**状态**: 需要修复

**文件列表**:
"""

    for error in categories["attribute_error"][:10]:
        report_content += f"- `{error['file']}`\n"

    if len(categories["attribute_error"]) > 10:
        report_content += f"- ... 还有 {len(categories['attribute_error']) - 10} 个文件\n"

    report_content += f"""
### 3. 文件不存在错误 (FileNotFoundError)
**数量**: {len(categories["file_not_found"])}
**状态**: 需要修复

**文件列表**:
"""

    for error in categories["file_not_found"][:10]:
        report_content += f"- `{error['file']}`\n"

    report_content += f"""
### 4. 语法错误 (SyntaxError)
**数量**: {len(categories["syntax_error"])}
**状态**: 需要修复

**文件列表**:
"""

    for error in categories["syntax_error"]:
        report_content += f"- `{error['file']}`\n"

    report_content += f"""
### 5. 其他错误
**数量**: {len(categories["other"])}
**状态**: 需要逐个检查

---

## 修复建议

1. **导入错误**: 添加 sys.path 设置或修正导入路径
2. **属性错误**: 更新API调用以匹配当前实现
3. **文件不存在**: 创建缺失的文件或更新导入路径
4. **语法错误**: 修复Python语法问题

---

**报告生成**: 自动化测试错误分析工具
"""

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_content, encoding="utf-8")
    print(f"\n📄 错误报告已生成: {report_path}")


def main():
    """主函数"""
    print("=" * 80)
    print("测试错误自动修复工具")
    print("=" * 80)
    print()

    # 步骤1: 收集错误
    errors = collect_test_errors()
    print(f"✅ 收集到 {len(errors)} 个错误")

    # 步骤2: 分类错误
    categories = categorize_errors(errors)
    print("✅ 错误分类完成:")
    print(f"   - 导入错误: {len(categories['import_error'])}")
    print(f"   - 属性错误: {len(categories['attribute_error'])}")
    print(f"   - 文件不存在: {len(categories['file_not_found'])}")
    print(f"   - 语法错误: {len(categories['syntax_error'])}")
    print(f"   - 其他错误: {len(categories['other'])}")

    # 步骤3: 生成报告
    generate_error_report(errors, categories)

    # 步骤4: 执行修复
    print("\n开始自动修复...")
    fix_scripts_tests_imports()
    fix_api_compatibility()

    # 步骤5: 验证修复
    print("\n验证修复结果...")
    result = subprocess.run(
        ["pytest", "--collect-only", "-q"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )

    # 统计修复后的错误数
    remaining_errors = result.stderr.count("ERROR collecting")
    fixed_errors = len(errors) - remaining_errors

    print()
    print("=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"修复前错误数: {len(errors)}")
    print(f"修复后错误数: {remaining_errors}")
    print(f"已修复错误数: {fixed_errors}")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
