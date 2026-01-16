# Spec: Python Code Quality

**Capability**: python-code-quality
**Change**: improve-backend-code-quality
**Status**: Proposed

---

## ADDED Requirements

### Requirement: Ruff代码质量标准

Python代码MUST通过Ruff代码质量检查，确保代码风格统一和最佳实践遵循。系统SHOULD自动修复可修复的问题，并MUST验证修复后的代码通过所有测试。

#### Scenario: 自动修复Ruff问题

**Given** 项目有1,540个Ruff问题
**When** 开发者运行 `ruff check --fix .`
**Then** 应该自动修复至少904个问题 (58.7%)
**And** Ruff问题总数应降至700以下
**And** 所有现有测试应该继续通过

#### Scenario: 手动修复剩余Ruff问题

**Given** 自动修复后仍有636个Ruff问题
**When** 开发者手动修复这些问题
**Then** Ruff问题总数应降至100以下
**And** 每个修复的文件应该通过代码审查
**And** 所有测试应该通过

---

### Requirement: Python测试覆盖率标准

Python代码MUST有充分的测试覆盖，确保代码质量和功能正确性。核心模块(data_access, adapters, core)MUST达到≥60%的测试覆盖率，整体项目SHOULD最终达到≥80%的覆盖率。

#### Scenario: 核心模块测试覆盖

**Given** data_access层测试覆盖率为0%
**When** 开发者为data_access层编写单元测试
**Then** data_access层测试覆盖率应该≥70%
**And** 应该有至少3个测试文件 (base, tdengine, postgresql)
**And** 所有测试应该通过

#### Scenario: Adapters层测试覆盖

**Given** adapters层测试覆盖率为0%
**When** 开发者为7个数据源适配器编写单元测试
**Then** adapters层测试覆盖率应该≥60%
**And** 应该有至少7个测试文件 (每个适配器一个)
**And** 所有测试应该通过

#### Scenario: Core层测试覆盖

**Given** core层测试覆盖率为0%
**When** 开发者为core层编写单元测试
**Then** core层测试覆盖率应该≥70%
**And** 应该有至少3个测试文件 (classification, storage_strategy, table_manager)
**And** 所有测试应该通过

#### Scenario: 整体测试覆盖率达标

**Given** 项目整体测试覆盖率为0.16%
**When** 开发者完成所有核心模块测试编写
**Then** 项目整体测试覆盖率应该≥40% (阶段2目标)
**And** 最终应该达到≥80% (阶段4目标)
**And** 覆盖率报告应该生成 (HTML和JSON格式)

---

### Requirement: 代码文件大小限制

Python文件MUST受限在合理大小范围内，确保代码可读性和可维护性。单个Python文件SHOULD不超过1000行，如果超过则MUST拆分为多个更小的模块。

#### Scenario: 拆分超长文件

**Given** 项目有4个文件超过1000行
  - data_access.py (1,357行)
  - tdx_adapter.py (1,058行)
  - financial_adapter.py (1,078行)
  - unified_manager.py (792行)
**When** 开发者拆分这些文件
**Then** 所有Python文件应该<1000行
**And** 每个新文件应该有明确的职责
**And** 导入应该保持向后兼容
**And** 所有测试应该通过

#### Scenario: 拆分data_access.py

**Given** data_access.py有1,357行代码
**When** 开发者将其拆分为3个模块 (base, tdengine, postgresql)
**Then** 每个新文件应该<600行
**And** 应该创建 `src/data_access/__init__.py` 导出接口
**And** 旧导入 `from src.data_access import TDengineDataAccess` 应该继续有效
**And** 所有data_access测试应该通过

#### Scenario: 拆分tdx_adapter.py

**Given** tdx_adapter.py有1,058行代码
**When** 开发者将其拆分为3个模块 (base, market, kline)
**Then** 每个新文件应该<500行
**And** 应该创建 `src/adapters/tdx/__init__.py` 导出接口
**And** 主类应该委托给子模块
**And** 所有TDX适配器测试应该通过

---

### Requirement: TODO注释管理

项目中的TODO和FIXME注释MUST定期清理和分类管理。已完成功能的TODO标记SHOULD删除，未实现功能MUST转为Issue跟踪，设计说明SHOULD转为文档注释。

#### Scenario: 清理TODO注释

**Given** 项目有266个TODO/FIXME注释
**When** 开发者清理这些注释
**Then** TODO注释数量应该<50
**And** 已完成功能的TODO应该删除
**And** 未实现功能应该转为Issue跟踪
**And** 设计说明应该转为文档注释

#### Scenario: TODO分类处理

**Given** 一个TODO注释标记了临时实现
**When** 功能已完整实现
**Then** TODO注释应该删除
**And** 不应该有其他遗留的临时实现标记

---

## MODIFIED Requirements

### Requirement: 代码质量检查流程

项目代码质量检查流程MUST包含Ruff检查、测试覆盖率验证、和代码审查。Pre-commit hooksMUST执行这些检查，CI/CD流程SHOULD生成质量指标报告。

#### Scenario: Pre-commit Hook检查

**Given** 开发者准备提交代码
**When** 运行pre-commit hooks
**Then** Ruff检查应该通过
**And** 测试应该通过
**And** 覆盖率应该满足要求 (≥40%阶段2, ≥80%阶段4)
**And** 代码审查应该批准

#### Scenario: CI/CD质量门禁

**Given** 代码推送到仓库
**When** CI/CD流程运行
**Then** Ruff检查应该通过
**And** 完整测试套件应该通过
**And** 覆盖率报告应该生成
**And** 质量指标应该记录

---

### Requirement: 后端代码组织规范

后端Python代码MUST按照单一职责原则组织，避免超长文件和过度复杂的模块。每个模块SHOULD有明确的单一职责，模块间依赖MUST通过接口抽象而非具体实现。

#### Scenario: 模块职责分离

**Given** 一个Python文件包含多个不相关的类或功能
**When** 开发者重构这个文件
**Then** 每个模块应该有单一明确的职责
**And** 相关功能应该组织在同一个模块中
**And** 模块间依赖应该通过接口抽象
**And** 导入应该清晰明确

---

## REMOVED Requirements

无移除的需求。

---

## Dependencies

- **依赖**: python-testing (测试基础设施)
- **影响**: frontend-code-quality (前端代码质量标准对齐)
- **冲突**: 无

---

## Success Metrics

| 指标 | 当前值 | 目标值 | 测量方法 |
|------|--------|--------|----------|
| Ruff问题数 | 1,540 | <100 | `ruff check . --statistics` |
| 测试覆盖率 | 0.16% | ≥80% | `coverage report` |
| 超长文件数 | 4 | 0 | `find src -name "*.py" -exec wc -l {} + \| sort -rn \| head -20` |
| TODO注释数 | 266 | <50 | `grep -r "TODO\|FIXME" src/ \| wc -l` |
| Pylint评级 | 9.32/10 | >9.5/10 | `pylint src/ --output-format=text` |

---

## Examples

### Example 1: Ruff自动修复流程

```bash
# 1. 备份当前状态
git add .
git commit -m "backup: before ruff auto-fix"

# 2. 运行自动修复
ruff check --fix .
ruff check --fix --unsafe-fixes .

# 3. 审查修改
git diff --stat

# 4. 运行测试验证
pytest tests/ -v

# 5. 提交修复
git add .
git commit -m "fix: auto-fix 904 ruff issues"
```

### Example 2: 拆分data_access.py

```python
# 旧结构
# src/data_access.py (1,357行)
class TDengineDataAccess:
    pass

class PostgreSQLDataAccess:
    pass

# 新结构
# src/data_access/__init__.py
from .base import DatabaseConnectionManager
from .tdengine import TDengineDataAccess
from .postgresql import PostgreSQLDataAccess

__all__ = ['TDengineDataAccess', 'PostgreSQLDataAccess', 'DatabaseConnectionManager']

# src/data_access/base.py (~400行)
class DatabaseConnectionManager:
    pass

# src/data_access/tdengine.py (~500行)
class TDengineDataAccess:
    pass

# src/data_access/postgresql.py (~500行)
class PostgreSQLDataAccess:
    pass

# 向后兼容的导入
from src.data_access import TDengineDataAccess  # 仍然有效
```

### Example 3: 测试文件结构

```python
# tests/data_access/test_tdengine.py
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_tdengine_connection():
    """Mock TDengine连接"""
    with patch('src.data_access.tdengine.taos_connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield mock_conn

def test_tdengine_query(mock_tdengine_connection):
    """测试TDengine查询"""
    from src.data_access.tdengine import TDengineDataAccess
    access = TDengineDataAccess()
    result = access.query("SELECT * FROM test_table")
    assert result is not None
    mock_tdengine_connection.cursor.assert_called_once()
```

---

**规格版本**: v1.0
**最后更新**: 2026-01-03
**状态**: Proposed
