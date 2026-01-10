# Proposal: Remediate Phase 7 Technical Debt

## Meta
- **Change ID**: remediate-phase7-technical-debt
- **Status**: Proposed
- **Created**: 2026-01-01
- **Priority**: High (阻塞生产部署)

## Problem Statement

Phase 7 完成后累积了多项技术债务，影响代码质量和E2E测试通过率：

### 高优先级问题 (本周完成)

1. **Ruff代码质量问题** (2-3小时)
   - 6个undefined name错误
   - `version_manager.py`: `ContractValidation`, `ContractDiff` 未定义
   - `exception_handler.py`: 4处 `request_id` 变量未定义

2. **CSRF认证阻塞E2E测试** (1-2小时)
   - 140+个E2E测试被CSRF保护阻塞
   - 前端登录后CSRF token未正确传递
   - 需要在测试环境中禁用CSRF或自动获取token

3. **MyPy类型注解问题** (4-6小时)
   - `cache_manager.py`: 38个类型注解错误
   - `tdengine_pool.py`: 3个类型注解缺失
   - `tdengine_manager.py`: 3个类型不匹配问题

### 中优先级问题 (下周完成)

4. **Session持久化问题** (2-3小时)
   - 登录状态在页面刷新后丢失
   - 需要实现session持久化到localStorage

5. **策略管理UI缺失** (3-4小时)
   - 策略管理页面功能不完整
   - 缺少策略创建/编辑/删除UI

6. **剩余E2E模块验证** (4-6小时)
   - 部分业务场景E2E覆盖不完整
   - 需要补充测试用例

## Why

现在必须修复这些技术债务，原因是：

1. **阻塞生产部署**: 代码质量检查不通过无法部署到生产环境
2. **E2E测试未达标**: 通过率85.7%低于目标95%，影响质量保证
3. **开发效率下降**: 持续绕过pre-commit hooks降低了代码质量标准
4. **技术债务累积**: 不及时修复会引入更多bug和维护成本

## Impact

- **代码质量**: Pre-commit hooks持续失败，阻塞开发流程
- **测试通过率**: E2E测试通过率仅85.7%，未达标95%
- **类型安全**: MyPy错误可能导致运行时类型错误
- **开发效率**: 手动绕过pre-commit hooks，降低代码质量保证

## Proposed Solution

### 1. 修复Ruff代码质量问题

**策略**: 添加缺失的导入和变量定义

- `version_manager.py`: 导入 `from .validation import ContractValidation` 和 `from .diff import ContractDiff`
- `exception_handler.py`: 在函数签名中添加 `request_id` 参数，或从 `request.state` 获取

**验证**: `ruff check` 通过，0个错误

### 2. 解决CSRF认证阻塞

**策略**: 测试环境禁用CSRF + 测试工具函数

- 在 `web/backend/app/core/config.py` 添加 `TESTING` 环境变量
- 测试环境中设置 `csrf_enabled=False`
- 创建E2E测试工具函数 `login_and_get_csrf_token()`
- 更新所有E2E测试使用新的认证流程

**验证**: E2E测试通过率 ≥95%

### 3. 修复MyPy类型注解问题

**策略**: 添加完整的类型注解和Optional处理

- `cache_manager.py`: 为 `_memory_cache`, `_cache_ttl`, `_access_patterns` 添加类型注解
- `tdengine_pool.py`: 添加类变量类型注解
- `tdengine_manager.py`: 修复 `str | None` 类型检查，使用 `.unwrap()` 或显式None检查

**验证**: `mypy web/backend/` 通过，0个错误

### 4. 完善Session持久化

**策略**: localStorage + 自动恢复

- 修改 `auth.js` store，在token变化时自动保存到localStorage
- 应用启动时从localStorage恢复session
- 处理token过期场景（清除本地storage）

**验证**: 页面刷新后登录状态保持

### 5. 完善策略管理UI

**策略**: 基于现有CRUD模式扩展

- 参考其他管理页面（如 `StockManagement.vue`）的设计模式
- 实现策略列表、创建表单、编辑对话框
- 连接后端策略API (`/api/strategy/`)

**验证**: 策略CRUD操作完整可用

### 6. 验证剩余E2E模块

**策略**: 逐模块补充测试用例

- 识别未覆盖的业务场景（通过代码覆盖率工具）
- 添加缺失的E2E测试用例
- 确保所有核心路径都被覆盖

**验证**: E2E覆盖率 ≥90%，通过率 ≥95%

## Affected Capabilities

- **code-quality**: Python代码质量标准（Ruff, MyPy）
- **csrf-protection**: API CSRF保护机制
- **type-safety**: Python类型注解完整性
- **session-management**: 前端session持久化
- **strategy-ui**: 策略管理用户界面
- **e2e-testing**: E2E测试覆盖率

## Success Criteria

1. ✅ Ruff检查通过（0个错误）
2. ✅ MyPy检查通过（0个错误）
3. ✅ E2E测试通过率 ≥95%
4. ✅ Session持久化正常工作
5. ✅ 策略管理UI功能完整
6. ✅ Pre-commit hooks全部通过
7. ✅ 代码提交不需要SKIP任何hook

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| CSRF修复影响生产安全 | Low | High | 仅在测试环境禁用，生产环境保持启用 |
| 类型注解修改引入新bug | Medium | Medium | 逐文件修改，每文件修改后运行测试 |
| Session持久化引入安全漏洞 | Low | High | 使用httpOnly cookie + localStorage混合方案 |
| E2E测试修复工作量超预期 | Medium | Low | 优先修复高频路径，低频场景可延后 |

## Timeline

- **Week 1**: 高优先级问题（Ruff, CSRF, MyPy）
- **Week 2**: 中优先级问题（Session, UI, E2E）

## Dependencies

- 后端开发环境（FastAPI运行）
- 前端开发环境（Vue dev server）
- 测试数据库（PostgreSQL, TDengine）

## Alternatives Considered

### 1. 暂时禁用所有pre-commit hooks
**优点**: 快速解除阻塞
**缺点**: 失去代码质量保证，技术债务累积
**结论**: ❌ 不推荐

### 2. 仅修复高优先级问题，延后中优先级
**优点**: 快速提升测试通过率
**缺点**: 技术债务未完全解决
**结论**: ✅ 采用（分两阶段完成）

### 3. 完全重写问题模块
**优点**: 代码更清晰
**缺点**: 工作量大，风险高
**结论**: ❌ 不推荐（渐进式修复更安全）

## Open Questions

1. CSRF在测试环境完全禁用，还是使用测试专用token？
   - **建议**: 完全禁用（简化测试流程）

2. MyPy类型注解错误是否允许部分忽略（使用 `# type: ignore`）？
   - **建议**: 不允许，必须正确修复

3. E2E测试覆盖目标是否需要达到100%？
   - **建议**: 不需要，90%覆盖率 + 95%通过率即可

## Related Changes

- Phase 7 Backend CLI: 双数据库连接配置修复
- Phase 7 Frontend CLI: TypeScript修复 (262→0 errors)
- Phase 7 Test CLI: E2E测试框架建立
