# Contract: 测试文件命名规范

**Feature**: 系统规范化改进
**Branch**: 006-0-md-1
**Date**: 2025-10-16
**Type**: Testing Standards

## 目的

定义测试文件重命名的验证契约，确保所有测试文件遵循pytest命名约定，保证测试自动发现和CI/CD集成。

## 命名规范

### 标准规则

1. **文件命名**: 所有测试文件必须以`test_`开头
   - ✅ 正确: `test_simple.py`, `test_database_menu.py`, `test_tdengine.py`
   - ❌ 错误: `simple_test.py`, `database_test_menu.py`, `tdengine_test.py`

2. **目录结构**: 测试文件可以放置在任何目录，pytest会自动递归发现
   - ✅ 正确: `adapters/test_simple.py`, `db_manager/test_tdengine.py`
   - ✅ 正确: `tests/test_integration.py`, `tests/unit/test_model.py`

3. **测试类命名**: 测试类必须以`Test`开头 (大写T)
   - ✅ 正确: `class TestDatabaseConnection`
   - ❌ 错误: `class DatabaseConnectionTest`

4. **测试函数命名**: 测试函数必须以`test_`开头
   - ✅ 正确: `def test_connection()`, `def test_query_performance()`
   - ❌ 错误: `def connection_test()`, `def testConnection()`

## 重命名映射清单

基于Phase 0 R4研究结果:

| # | 原文件 | 新文件 | 优先级 | Import影响 |
|---|--------|--------|--------|-----------|
| 1 | adapters/simple_test.py | adapters/test_simple.py | P2 | 检查引用 |
| 2 | db_manager/simple_test.py | db_manager/test_simple.py | P2 | 检查引用 |
| 3 | db_manager/database_test_menu.py | db_manager/test_database_menu.py | P2 | 检查引用 |
| 4 | db_manager/tdengine_test.py | db_manager/test_tdengine.py | P2 | 检查引用 |
| 5 | temp/debug_test.py | temp/test_debug.py | P3 | 无需修复 |
| 6 | temp/architecture_test.py | temp/test_architecture.py | P3 | 无需修复 |

## Import路径修复策略

### Step 1: 搜索潜在引用

```bash
# 对于每个重命名的文件，搜索可能的引用
grep -r "simple_test" --include="*.py" .
grep -r "database_test_menu" --include="*.py" .
grep -r "tdengine_test" --include="*.py" .
```

### Step 2: 修复Import语句

**修复模式**:
```python
# 修复前
from adapters.simple_test import MyTestClass
import adapters.simple_test as st

# 修复后
from adapters.test_simple import MyTestClass
import adapters.test_simple as st
```

### Step 3: 修复相对导入

```python
# 修复前
from .simple_test import my_function

# 修复后
from .test_simple import my_function
```

## 验证命令

### 单个文件验证

```bash
# 验证单个测试文件
pytest adapters/test_simple.py -v

# 预期输出
============================= test session starts ==============================
collected X items

adapters/test_simple.py::test_xxx PASSED
adapters/test_simple.py::test_yyy PASSED
```

### 全部测试验证

```bash
# 验证所有测试文件
pytest test_*.py -v

# 或使用pytest自动发现
pytest -v

# 预期输出: 所有测试通过，无import错误
```

### 测试覆盖率检查 (可选)

```bash
# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

## 验收标准

### 必须满足 (P1)

- [ ] 所有测试文件以`test_`开头命名
- [ ] `pytest test_*.py -v` 100%通过
- [ ] 无ImportError或ModuleNotFoundError
- [ ] Git历史可追溯重命名 (`git log --follow test_xxx.py`)

### 建议满足 (P2)

- [ ] 所有测试类以`Test`开头
- [ ] 所有测试函数以`test_`开头
- [ ] 测试文件包含docstring说明测试范围
- [ ] 复杂测试有setup/teardown方法

### 可选满足 (P3)

- [ ] 测试文件包含pytest markers (@pytest.mark.slow, @pytest.mark.integration)
- [ ] 使用pytest fixtures优化测试代码
- [ ] 测试覆盖率 ≥ 80%

## 执行流程

### 重命名流程 (安全)

```bash
# 1. 使用git mv保留历史
git mv adapters/simple_test.py adapters/test_simple.py

# 2. 立即运行测试
pytest adapters/test_simple.py -v

# 3. 如果失败，搜索引用
if [ $? -ne 0 ]; then
    grep -r "simple_test" --include="*.py" .
    # 修复所有import引用
fi

# 4. 再次验证
pytest adapters/test_simple.py -v

# 5. 确认通过后提交
git add -A
git commit -m "test: rename simple_test.py to test_simple.py for pytest convention"
```

### 批量重命名脚本 (高级)

```bash
#!/bin/bash
# 批量重命名测试文件脚本

rename_and_test() {
    OLD_FILE=$1
    NEW_FILE=$2

    echo "=========================================="
    echo "重命名: $OLD_FILE -> $NEW_FILE"
    echo "=========================================="

    # 1. 检查源文件存在
    if [ ! -f "$OLD_FILE" ]; then
        echo "错误: $OLD_FILE 不存在"
        return 1
    fi

    # 2. 使用git mv
    git mv "$OLD_FILE" "$NEW_FILE"

    # 3. 立即测试
    pytest "$NEW_FILE" -v
    TEST_RESULT=$?

    # 4. 如果失败，搜索引用
    if [ $TEST_RESULT -ne 0 ]; then
        echo "测试失败，搜索可能的引用..."
        OLD_NAME=$(basename "$OLD_FILE" .py)
        grep -r "$OLD_NAME" --include="*.py" . | grep -v ".pyc"
        echo "请手动修复import后重新运行脚本"
        return 1
    fi

    echo "✅ $NEW_FILE 验证通过"
    return 0
}

# 执行重命名
rename_and_test "adapters/simple_test.py" "adapters/test_simple.py"
rename_and_test "db_manager/simple_test.py" "db_manager/test_simple.py"
rename_and_test "db_manager/database_test_menu.py" "db_manager/test_database_menu.py"
rename_and_test "db_manager/tdengine_test.py" "db_manager/test_tdengine.py"

# 运行完整测试套件
echo "=========================================="
echo "运行完整测试套件"
echo "=========================================="
pytest test_*.py -v

if [ $? -eq 0 ]; then
    echo "✅ 所有测试通过，可以提交"
    git status
else
    echo "❌ 部分测试失败，请修复后再提交"
fi
```

## 常见问题

### Q1: 重命名后测试无法发现

**原因**: pytest配置问题或文件未按规范命名

**解决**:
```bash
# 检查pytest配置
cat pytest.ini

# 确认文件名以test_开头
ls -la test_*.py

# 使用-v显示详细发现过程
pytest -v --collect-only
```

### Q2: Import错误但找不到引用

**原因**: 可能在__pycache__中有旧引用

**解决**:
```bash
# 清理所有缓存
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 重新测试
pytest test_*.py -v
```

### Q3: Git历史断裂

**原因**: 使用mv而非git mv

**解决**:
```bash
# 查看文件历史
git log --follow -- test_xxx.py

# 如果历史断裂，可以用blame追溯
git blame test_xxx.py
```

## 回滚方案

如果重命名后出现严重问题:

```bash
# 1. 查看最近提交
git log -3 --oneline

# 2. 回滚到重命名前
git revert <commit-hash>

# 或使用reset (谨慎使用)
git reset --hard HEAD~1

# 3. 恢复工作区
git restore .
```

---

**合规检查清单**:

- [ ] 所有测试文件以test_开头 (FR-015)
- [ ] pytest test_*.py 100%通过 (验收标准)
- [ ] 无import错误 (验收标准)
- [ ] Git历史可追溯 (验收标准)

**创建人**: Claude
**版本**: 1.0.0
**批准日期**: 待定
**最后修订**: 2025-10-16
**本次修订内容**: 初始创建测试文件命名规范契约
