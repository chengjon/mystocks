# E2E Testing Capability Spec (Delta)

## MODIFIED Requirements

### Requirement: E2E测试通过率MUST达到95% (MUST)

**ID**: RQ-E2E-001
**Priority**: High
**Status**: Modified

**Description**:
所有E2E测试MUST通过，通过率 ≥95%。允许少量flaky测试，但MUST在5%以内。

**Rationale**:
Phase 7结束时E2E测试通过率仅85.7%，未达标95%。MUST修复失败的测试用例。

**Original Requirement**:
E2E测试应该尽量通过，目标通过率95%。

**Modified Requirement**:
E2E测试MUST通过，通过率 ≥95% 为硬性要求。失败的测试MUST是flaky测试（间歇性失败），不能是功能缺陷。

#### Scenario: 运行全量E2E测试

**Given**:
- E2E测试框架已配置（Playwright）
- 测试数据库已准备
- 后端服务运行中

**When**:
- 开发者运行 `npx playwright test`
- 或CI/CD流水线执行E2E测试

**Then**:
- 所有测试文件被执行
- 测试报告显示通过率 ≥95%
- 失败的测试 ≤5%
- 失败测试都是flaky测试（非功能缺陷）

**Verification Steps**:
1. 运行 `npx playwright test`
2. 检查测试输出: "X passed, Y failed (≥95% passed)"
3. 打开HTML测试报告（`npx playwright show-report`）
4. 分析失败测试，确认都是flaky测试（网络超时、渲染延迟等）
5. 如果失败测试是功能缺陷，MUST修复后重新运行

---

### Requirement: E2E测试MUST覆盖核心业务场景 (MUST)

**ID**: RQ-E2E-002
**Priority**: High
**Status**: Modified

**Description**:
E2E测试MUST覆盖所有核心业务场景，覆盖率 ≥90%。

**Rationale**:
Phase 7遗留部分业务场景E2E覆盖不完整，MUST补充测试用例。

**Original Requirement**:
E2E测试应该覆盖主要业务流程。

**Modified Requirement**:
E2E测试MUST覆盖所有核心业务场景（覆盖率 ≥90%），包括正常流程和异常流程。

#### Scenario: 核心业务场景覆盖检查

**Given**:
- 系统有15+个核心业务场景:
  1. 用户登录/登出
  2. 股票查询和详情查看
  3. 技术分析指标展示
  4. 策略管理（CRUD）
  5. 回测分析
  6. 市场数据监控
  7. 资金流向分析
  8. 风险监控
  9. 公告监控
  10. 任务管理
  11. 系统设置
  12. 数据库监控
  13. OpenStock集成
  14. Freqtrade集成
  15. Stock-Analysis集成

**When**:
- 开发者分析E2E测试覆盖率
- 使用代码覆盖率工具或手动分析

**Then**:
- 至少13个核心场景有E2E测试覆盖（≥90%）
- 每个场景包含正常流程测试
- 每个场景包含异常流程测试（如网络错误、权限不足）

**Verification Steps**:
1. 列出所有核心业务场景
2. 检查 `tests/e2e/` 目录，每个场景对应至少一个测试文件
3. 检查测试文件包含正常和异常流程测试
4. 运行覆盖率工具: `npx playwright test --coverage`
5. 验证覆盖率 ≥90%

#### Scenario: 补充缺失的E2E测试用例

**Given**:
- 识别出未覆盖的业务场景（如策略管理CRUD）

**When**:
- 开发者编写新的E2E测试用例
- 测试文件命名规范: `<feature>.spec.ts`
- 测试用例包含:
  - 测试描述（test.describe）
  - 测试步骤（test步骤）
  - 断言验证（expect）

**Then**:
- 新测试用例覆盖缺失的业务场景
- 测试能正常运行并断言
- 测试通过率达到100%（新测试）

**Verification Steps**:
1. 创建新测试文件 `tests/e2e/strategy.spec.ts`
2. 编写测试用例:
   ```typescript
   test.describe('Strategy Management', () => {
     test.beforeEach(async ({ page }) => {
       await loginAndGetCsrfToken(page, 'admin', 'admin123')
     })

     test('should create strategy', async ({ page }) => {
       await page.goto('/strategy-hub/management')
       await page.click('[data-testid="create-strategy-button"]')
       await page.fill('[data-testid="strategy-name"]', '测试策略')
       await page.click('[data-testid="submit-button"]')
       await expect(page.locator('.success-message')).toBeVisible()
     })
   })
   ```
3. 运行新测试: `npx playwright test strategy.spec.ts`
4. 验证测试通过
5. 验证覆盖率提升

---

### Requirement: E2E测试MUST包含边界场景测试 (MUST)

**ID**: RQ-E2E-003
**Priority**: Medium
**Status**: Added

**Description**:
E2E测试不仅测试正常流程，还MUST测试边界场景（空数据、网络错误、权限不足、极端输入）。

**Rationale**:
仅测试正常流程无法保证系统健壮性，边界场景测试能发现潜在bug。

#### Scenario: 测试空数据场景

**Given**:
- 测试数据库为空（无股票数据、无策略）

**When**:
- 用户访问股票列表页面
- 用户访问策略管理页面

**Then**:
- 页面显示"暂无数据"提示
- 页面不崩溃，不显示加载状态
- 用户能理解当前状态

**Verification Steps**:
1. 清空测试数据库
2. 访问列表页面
3. 验证显示"暂无数据"或空状态图标
4. 验证页面无JavaScript错误（Console面板无错误）

#### Scenario: 测试网络错误场景

**Given**:
- 后端服务停止运行
- 或网络被模拟为离线状态

**When**:
- 用户执行任何需要API的操作（如查询股票）

**Then**:
- 显示友好的错误提示: "网络连接失败，请检查网络设置"
- 页面不崩溃
- 用户可以重试操作

**Verification Steps**:
1. 停止后端服务
2. 访问页面并执行操作
3. 验证显示错误提示（不是技术错误堆栈）
4. 验证错误提示包含重试按钮或建议

#### Scenario: 测试权限不足场景

**Given**:
- 普通用户登录（非管理员）
- 普通用户无删除策略权限

**When**:
- 用户尝试删除策略

**Then**:
- 显示权限不足提示: "您没有权限执行此操作"
- 不发送DELETE请求
- 或DELETE请求返回403，前端正确处理

**Verification Steps**:
1. 使用普通用户登录
2. 尝试访问管理员功能或执行删除操作
3. 验证显示权限不足提示
4. 验证网络请求返回403（如果发送了请求）

---

### Requirement: E2E测试MUST稳定可靠（无flaky测试） (MUST)

**ID**: RQ-E2E-004
**Priority**: Medium
**Status**: Added

**Description**:
E2E测试MUST稳定可靠，连续运行5次全部通过。不允许有间歇性失败的测试（flaky tests）。

**Rationale**:
Flaky测试会破坏CI/CD流水线，降低团队对测试的信任度。

#### Scenario: 验证测试稳定性

**Given**:
- E2E测试套件已编写完成

**When**:
- 开发者连续运行测试5次:
  ```bash
  for i in {1..5}; do
    npx playwright test || echo "Run $i failed"
  done
  ```

**Then**:
- 所有5次运行全部通过
- 无间歇性失败
- 测试执行时间稳定（差异 <10%）

**Verification Steps**:
1. 运行测试5次，记录每次结果
2. 检查所有运行都通过
3. 如果有失败，分析失败原因:
   - 如果是代码bug，修复代码
   - 如果是测试时序问题，添加 `waitFor` 或 `waitForSelector`
   - 如果是测试数据问题，使用固定测试数据
4. 重新运行5次验证修复

#### Scenario: 消除flaky测试的时序依赖

**Given**:
- 测试失败原因是"元素未找到"或"超时"

**When**:
- 开发者添加显式等待:
  ```typescript
  // Before (flaky)
  await page.click('.submit-button')

  // After (stable)
  await page.waitForSelector('.submit-button', { state: 'visible' })
  await page.click('.submit-button')
  ```

**Then**:
- 测试不再失败
- 测试能适应网络延迟
- 测试能适应不同性能的机器

**Verification Steps**:
1. 检查测试文件，所有元素选择器前都有 `waitForSelector`
2. 运行测试5次，验证全部通过
3. 在慢速网络下运行测试，验证仍通过

---

## Related Capabilities

- **csrf-protection**: E2E测试依赖认证工具函数才能稳定运行
- **session-management**: Session持久化MUST在E2E测试中验证
- **code-quality**: E2E测试代码也MUST通过Ruff检查（TypeScript文件）
- **strategy-ui**: 策略管理UIMUST有E2E测试覆盖
