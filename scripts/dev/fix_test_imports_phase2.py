#!/usr/bin/env python3
"""Phase 2: 修复剩余的导入路径错误

针对特定的模块路径问题:
- src.adapters.tdx_adapter → src.adapters.tdx.tdx_adapter
- 其他特定的模块路径修正

创建日期: 2026-01-03
"""

import re
from pathlib import Path


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent


def fix_specific_imports():
    """修复特定的导入路径问题"""
    print("修复特定的导入路径问题...")

    # 特定的导入路径修正规则
    specific_fixes = [
        # TDX适配器路径修正
        (r"from src\.adapters\.tdx_adapter import", "from src.adapters.tdx.tdx_adapter import"),
        (r"from src\.adapters\.tdx_connection_manager import", "from src.adapters.tdx.tdx_connection_manager import"),
        (r"from src\.adapters\.tdx_block_reader import", "from src.adapters.tdx.tdx_block_reader import"),
        # 其他可能的问题路径
        (r"from src\.db_manager\.database_manager import", "from src.storage.database import"),
    ]

    # 扫描所有测试文件
    test_dirs = [
        PROJECT_ROOT / "tests",
        PROJECT_ROOT / "scripts" / "tests",
        PROJECT_ROOT / "smart_ai_tests",
    ]

    fixed_count = 0

    for test_dir in test_dirs:
        if not test_dir.exists():
            continue

        for test_file in test_dir.rglob("test_*.py"):
            try:
                content = test_file.read_text(encoding="utf-8")
                original_content = content

                # 应用所有修正规则
                for pattern, replacement in specific_fixes:
                    content = re.sub(pattern, replacement, content)

                if content != original_content:
                    test_file.write_text(content, encoding="utf-8")
                    fixed_count += 1
                    print(f"  ✅ {test_file.relative_to(PROJECT_ROOT)}")

            except Exception as e:
                print(f"  ❌ {test_file.relative_to(PROJECT_ROOT)} - {e}")

    print(f"\n总共修复了 {fixed_count} 个文件")
    return fixed_count


def check_remaining_errors():
    """检查剩余错误"""
    import subprocess

    print("\n检查剩余错误...")
    result = subprocess.run(
        ["pytest", "--collect-only", "-q", "2>&1", "|", "grep", "ERROR collecting", "|", "wc", "-l"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        shell=True,
    )

    # 不使用shell，直接运行pytest
    result = subprocess.run(
        ["pytest", "--collect-only", "-q"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )

    error_count = result.stderr.count("ERROR collecting")
    print(f"剩余错误数: {error_count}")

    return error_count


def generate_summary(fixed_count, before_errors, after_errors):
    """生成修复摘要"""
    summary = f"""
# 测试错误修复摘要 (Phase 2)

**日期**: 2026-01-03
**修复文件数**: {fixed_count}

---

## 修复内容

### 导入路径修正

**规则**:
- `from src.adapters.tdx_adapter import` → `from src.adapters.tdx.tdx_adapter import`
- `from src.adapters.tdx_connection_manager import` → `from src.adapters.tdx.tdx_connection_manager import`
- `from src.adapters.tdx_block_reader import` → `from src.adapters.tdx.tdx_block_reader import`
- 其他特定的模块路径修正

### 修复效果

| 指标 | 数值 |
|------|------|
| 修复前错误数 | {before_errors} |
| 修复后错误数 | {after_errors} |
| 已修复错误 | {before_errors - after_errors} |
| 修复率 | {((before_errors - after_errors) / before_errors * 100):.1f}% |

---

## 下一步

剩余{after_errors}个错误需要:
1. 逐个检查错误详情
2. 分类处理 (导入问题/环境问题/依赖问题)
3. 或考虑跳过这些测试文件（标记为待修复）

---

**生成时间**: 自动化测试修复工具
"""

    summary_path = PROJECT_ROOT / "docs" / "reports" / "TEST_FIX_PHASE2_SUMMARY.md"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(summary, encoding="utf-8")

    print(f"\n📄 摘要已生成: {summary_path}")


def main():
    """主函数"""
    print("=" * 80)
    print("Phase 2: 测试导入路径精确修复")
    print("=" * 80)
    print()

    # 获取修复前的错误数
    before_errors = 83  # 已知

    # 执行修复
    fixed_count = fix_specific_imports()

    # 检查剩余错误
    after_errors = check_remaining_errors()

    # 生成摘要
    generate_summary(fixed_count, before_errors, after_errors)

    print()
    print("=" * 80)
    print("Phase 2 完成")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    exit(main())
