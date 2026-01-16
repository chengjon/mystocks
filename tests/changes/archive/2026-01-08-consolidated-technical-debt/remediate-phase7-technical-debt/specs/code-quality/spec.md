# Code Quality Capability Spec (Delta)

## MODIFIED Requirements

### Requirement: Python代码MUST通过Ruff Linter检查(MUST)

**ID**: RQ-CODEQUALITY-001
**Priority**: High
**Status**: Modified

**Description**:
所有Python代码MUST通过Ruff linter检查，确保代码质量符合项目规范。Ruff检查MUST在pre-commit hooks中自动执行，MUST NOT允许长期SKIP。

**Rationale**:
Phase 7遗留了6个Ruff undefined name错误，这些错误会导致代码在运行时失败。MUST修复这些错误以保证代码质量。

**Original Requirement**:
Python代码应该通过Ruff检查，但允许在紧急情况下SKIP。

**Modified Requirement**:
Python代码MUST通过Ruff检查，0个错误允许提交。Pre-commit hooks中的Ruff检查不允许长期SKIP。

#### Scenario: 修复undefined name错误

**Given**:
- `web/backend/app/api/contract/services/version_manager.py` 存在2个undefined name错误
- `web/backend/app/core/exception_handler.py` 存在4个undefined name错误

**When**:
- 开发者运行 `ruff check web/backend/`
- 或开发者执行 `git commit` 触发pre-commit hooks

**Then**:
- Ruff检查通过，输出0个错误
- 或Ruff报告具体的文件和行号，开发者修复后重新检查
- Pre-commit hooks不允许SKIP Ruff检查

**Verification Steps**:
1. 运行 `ruff check web/backend/app/api/contract/services/version_manager.py`
2. 验证输出包含0个F821错误
3. 运行 `ruff check web/backend/app/core/exception_handler.py`
4. 验证输出包含0个F821错误
5. 运行 `git commit` 验证pre-commit hooks通过

---

### Requirement: 新增代码MUST包含导入语句 (MUST)

**ID**: RQ-CODEQUALITY-002
**Priority**: High
**Status**: Added

**Description**:
所有使用的符号（类、函数、变量）MUST在文件顶部显式导入，不允许使用未定义的符号。

**Rationale**:
undefined name错误通常是因为使用了未导入的符号，MUST显式导入以提高代码可读性和可维护性。

#### Scenario: 导入缺失的类型定义

**Given**:
- `version_manager.py` 使用了 `ContractValidation` 和 `ContractDiff` 但未导入

**When**:
- 开发者在文件顶部添加导入语句:
  ```python
  from .validation import ContractValidation
  from .diff import ContractDiff
  ```

**Then**:
- Ruff检查不再报告undefined name错误
- 代码能正常运行

**Verification Steps**:
1. 检查 `version_manager.py` 顶部包含正确的导入语句
2. 运行 `ruff check version_manager.py` 验证0个F821错误
3. 运行单元测试验证功能正常

#### Scenario: 函数参数中使用未定义的变量

**Given**:
- `exception_handler.py` 在多个函数中使用了 `request_id` 变量但未定义

**When**:
- 开发者在函数签名中添加 `request_id` 参数
- 或从 `request.state.request_id` 获取值

**Then**:
- Ruff检查不再报告undefined name错误
- 函数能正确处理请求ID

**Verification Steps**:
1. 检查 `exception_handler.py` 中所有 `request_id` 引用都已定义
2. 运行 `ruff check exception_handler.py` 验证0个F821错误
3. 运行集成测试验证异常处理逻辑正常

---

## Related Capabilities

- **type-safety**: MyPy类型注解要求（相互补充，Ruff检查undefined name，MyPy检查类型正确性）
- **e2e-testing**: E2E测试需要代码质量保证才能稳定运行
