# Type Safety Capability Spec (Delta)

## MODIFIED Requirements

### Requirement: Python代码MUST通过MyPy类型检查 (MUST)

**ID**: RQ-TYPESAFE-001
**Priority**: High
**Status**: Modified

**Description**:
所有Python代码MUST添加完整的类型注解，通过MyPy类型检查。不允许长期SKIP MyPy检查。

**Rationale**:
Phase 7遗留了38+个MyPy类型注解错误，这些错误可能导致运行时类型错误。MUST修复以保证类型安全。

**Original Requirement**:
Python代码应该添加类型注解，通过MyPy检查。

**Modified Requirement**:
Python代码MUST添加完整的类型注解，MyPy检查MUST通过（0个错误）。业务代码不允许使用 `# type: ignore`（第三方库问题除外）。

#### Scenario: 修复cache_manager.py类型注解错误

**Given**:
- `web/backend/app/core/cache_manager.py` 存在38个MyPy错误
- 主要错误: 缺少类型注解、类型不匹配

**When**:
- 开发者为类变量添加类型注解:
  ```python
  _memory_cache: dict[str, Any] = {}
  _cache_ttl: dict[str, float] = {}
  _access_patterns: dict[str, list[str]] = {}
  ```
- 开发者修复 `str | None` 类型不匹配:
  ```python
  # Before (错误)
  def _add_to_memory_cache(self, key: str, value: Any, ttl: str | None):
      if ttl:
          self._cache_ttl[key] = ttl  # str | None 不能赋值给 str

  # After (修复)
  def _add_to_memory_cache(self, key: str, value: Any, ttl: Optional[str]):
      if ttl:
          self._cache_ttl[key] = ttl
  ```

**Then**:
- MyPy检查通过，输出0个错误
- 代码类型安全，IDE能正确提供类型提示

**Verification Steps**:
1. 运行 `mypy web/backend/app/core/cache_manager.py`
2. 验证输出包含0个错误
3. 检查所有类变量和函数都有类型注解
4. 运行单元测试验证功能正常

---

### Requirement: 使用Optional代替裸None类型 (MUST)

**ID**: RQ-TYPESAFE-002
**Priority**: Medium
**Status**: Added

**Description**:
所有可能为None的参数和返回值MUST使用 `Optional[T]` 或 `T | None` 注解，禁止使用裸类型。

**Rationale**:
裸类型不包含None信息，MyPy无法检查None相关错误。使用Optional明确标注None可能性。

#### Scenario: 函数返回值可能为None

**Given**:
- 函数可能返回None值:
  ```python
  def get_cache(key: str):  # 缺少返回值类型
      if key in self._cache:
          return self._cache[key]
      return None
  ```

**When**:
- 开发者添加返回值类型注解:
  ```python
  from typing import Optional

  def get_cache(self, key: str) -> Optional[Any]:
      if key in self._cache:
          return self._cache[key]
      return None
  ```

**Then**:
- MyPy能正确检查返回值使用
- 调用者知道需要处理None情况

**Verification Steps**:
1. 检查函数签名包含 `-> Optional[<type>]`
2. 运行MyPy检查，验证无类型错误
3. 检查调用者正确处理了None情况（if value: ...）

---

### Requirement: 处理union-attr错误 (MUST)

**ID**: RQ-TYPESAFE-003
**Priority**: Medium
**Status**: Added

**Description**:
访问Optional类型的属性时，MUST先检查None，或使用类型守卫。

**Rationale**:
`Item "None" of "X | None" has no attribute "y"` 是常见MyPy错误，MUST显式处理None情况。

#### Scenario: 访问Optional对象的属性

**Given**:
- 代码直接访问Optional对象的属性:
  ```python
  tdengine_manager: TDengineManager | None = get_manager()
  data = tdengine_manager.read_cache(key)  # union-attr错误
  ```

**When**:
- 开发者添加None检查:
  ```python
  tdengine_manager: Optional[TDengineManager] = get_manager()
  if tdengine_manager is None:
      raise RuntimeError("TDengine manager not initialized")
  data = tdengine_manager.read_cache(key)  # MyPy知道tdengine_manager不是None
  ```

**Then**:
- MyPy检查通过，无union-attr错误
- 代码正确处理了None情况

**Verification Steps**:
1. 检查代码在访问Optional对象属性前有None检查
2. 运行MyPy检查，验证无union-attr错误
3. 运行集成测试验证None情况被正确处理

---

## Related Capabilities

- **code-quality**: Ruff和MyPy相互补充，Ruff检查undefined name，MyPy检查类型正确性
- **session-management**: Session管理相关代码需要严格的类型检查
