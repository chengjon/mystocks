# 前端策略管理链路工作交接记录 - 2026-03-11

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## 1. 背景与当前目标

- 当前工作线的目标是继续清理 `main`，把前端活跃路由链整理成更适合后续多 CLI 分发的干净基线。
- 本轮聚焦对象是策略管理活跃链路：`/strategy/repo`。
- 本轮没有进入“大面积整理”或“全仓清理”，而是沿着既定微提交思路，只追一条活跃路由链的真实阻塞点。

## 2. 本轮实际完成的工作

### 2.1 已确认的源码状态

- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`
  - 已从内联逻辑重构为调用 view-model。
  - 关键修补已补上：模板里使用的 `isBacktestRunning` 已重新加入解构列表。
- 新增但尚未提交的相关文件：
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyManagementViewModel.ts`
  - `web/frontend/tests/unit/ArtDecoStrategyManagement.spec.ts`
- 相关联的工作区变更仍处于未提交状态：
  - `web/frontend/src/App.vue`
  - `web/frontend/src/composables/useStrategy.ts`
  - `web/frontend/tests/e2e/strategy-management-chain.spec.ts`
  - `web/frontend/src/composables/useBackendReadiness.ts`

### 2.2 已完成的验证与调查

- 已复跑失败用例：
  - `cd web/frontend && npx playwright test tests/e2e/strategy-management-chain.spec.ts --project=chromium`
  - 结果：`4/4` 失败，失败点都集中在 `/strategy/repo` 页面内容未正常呈现。
- 已确认 Playwright 不是在复用 PM2 旧预览构建：
  - `web/frontend/playwright.config.js:88`
  - 该配置会自启新的 Vite dev server，且 `reuseExistingServer: false`。
- 已做浏览器级探针验证：
  - 临时起本地 Vite 端口；
  - 使用 Playwright 手工拦截策略列表接口；
  - 观察 `console`、`pageerror`、`requestfailed`、DOM 内容。

## 3. 目前查明的根因

### 3.1 根因结论

当前 `/strategy/repo` E2E 失败的**首要根因，不是策略页 view-model 本身**，而是**全局 App 的“后端就绪门禁”先把主路由内容挡住了**。

### 3.2 证据链

1. `web/frontend/src/App.vue:3`
   - App 在渲染 `router-view` 之前，先检查后端 readiness。
2. `web/frontend/src/App.vue:16`
   - 当 `hasBlockingReadinessError` 为真时，直接渲染“后端暂未就绪”错误壳，而不是路由页面。
3. `web/frontend/src/App.vue:31`
   - 只有 readiness 通过后，才会进入真正的 `<router-view />`。
4. `web/frontend/src/App.vue:55`
   - 页面挂载时会自动执行 `checkBackendReadiness()`。
5. `web/frontend/src/composables/useBackendReadiness.ts:26`
   - readiness 探针会根据 `VITE_API_BASE_URL` 解析健康检查地址。
6. `web/frontend/src/composables/useBackendReadiness.ts:33`
   - 当 base 不是 `/api` 时，会拼出 `.../api/health/ready`。
7. `web/frontend/src/composables/useBackendReadiness.ts:80`
   - 一旦探针失败且未开启 mock 模式，会返回 `ready: false`，使 App 进入阻塞错误态。
8. 浏览器实测证据：
   - dev server 运行在 `http://127.0.0.1:<port>`
   - readiness 请求打到了 `http://localhost:8020/api/health/ready`
   - 浏览器报 CORS 错误，随后页面只显示“后端暂未就绪 / 重试检查”

### 3.3 为什么这点很关键

- 之前一度怀疑是 “PM2 preview 旧构建” 造成的假阴性；
- 这个怀疑已经被 `web/frontend/playwright.config.js:88` 的配置事实推翻；
- 因此，后续不要再沿着“重启 PM2 预览构建”这条线继续消耗时间。

## 4. 对策略页本身的当前判断

- 目前没有拿到“策略管理页 setup 直接抛错”的硬证据。
- 从已做的单测和当前数据看，`ArtDecoStrategyManagement.vue` → `strategyManagementViewModel.ts` 这条重构链**不再是第一优先级怀疑对象**。
- 更准确地说：
  - 策略页内容尚未来得及稳定进入 DOM；
  - 在它真正渲染前，App 级 readiness shell 已经先接管界面。

## 5. 当前未提交现场

截至交接时，相关文件状态如下：

- `web/frontend/src/App.vue`：modified
- `web/frontend/src/composables/useStrategy.ts`：modified
- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`：modified
- `web/frontend/tests/e2e/strategy-management-chain.spec.ts`：modified
- `web/frontend/src/composables/useBackendReadiness.ts`：untracked
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyManagementViewModel.ts`：untracked
- `web/frontend/tests/unit/ArtDecoStrategyManagement.spec.ts`：untracked

说明：

- 这些变更**尚未形成可提交闭环**；
- 由于你正在做主线架构重组，当前更适合先保留现场，不继续往下叠更多修复。

## 6. 建议的下一步任务

建议后续接手时按下面顺序推进：

### Step 1：先处理全局 readiness 策略，而不是继续盯策略页

优先审视以下两处：

- `web/frontend/src/App.vue:3`
- `web/frontend/src/composables/useBackendReadiness.ts:36`

要先决策本项目在“本地开发 / E2E / Mock 验收”场景下，readiness 是否应该：

- 阻塞整个 App；
- 允许 fallback 后继续渲染路由；
- 或改成同源 `/api/health/ready` 探针，避免 `127.0.0.1` vs `localhost` 的跨域问题。

### Step 2：根因修复后，再回到策略链验证

恢复后优先跑：

- `cd web/frontend && npx playwright test tests/e2e/strategy-management-chain.spec.ts --project=chromium`
- `cd web/frontend && npx playwright test tests/e2e/strategy-crud.spec.ts --project=chromium`

如果这两组通过，再决定是否把下面这一组整理成单独微提交：

- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyManagementViewModel.ts`
- `web/frontend/tests/unit/ArtDecoStrategyManagement.spec.ts`

### Step 3：提交边界建议

后续建议拆成两个提交，不要混在一起：

1. `fix(frontend): relax or align app readiness gating for local/e2e`
2. `refactor(frontend): delegate strategy management to view model`

这样做的好处：

- 容易判断是谁导致 E2E 恢复；
- 避免把“架构门禁修复”和“页面重构”缠在同一次回滚里；
- 更适合你后面按多 CLI 方式分发。

## 7. 交接提醒

- 不要因为 `ArtDecoStrategyManagement.vue` 当前 diff 很大，就直接回退它；
- 目前更像是“App 全局门禁先阻塞”，不是“策略页重构必然有问题”；
- 在你的主线架构重组完成前，建议把这条工作线视为“已定位根因、待恢复施工”的暂停状态。

## 8. 一句话总结

这条工作线已经从“怀疑策略页重构异常”推进到“确认全局 readiness gate 才是 `/strategy/repo` 当前 E2E 阻塞根因”；下一步不应继续盲修策略页，而应先处理 `App.vue + useBackendReadiness.ts` 的本地/E2E 兼容策略。
