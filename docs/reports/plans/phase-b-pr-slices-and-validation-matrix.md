# Phase B PR 拆分与验证矩阵（可直接执行）

## 目标
把 `phase-b-execution-checklist.md` 落到可提交的 PR 粒度，确保每个 PR 都有明确范围、验证项与回滚动作。

## PR-1（Batch 1A）：收敛 `httpClient` 到 canonical client

### 变更范围（仅限）
- `web/frontend/src/services/httpClient.js`

### 必做动作
1. 清理分叉请求路径，仅保留到 `web/frontend/src/api/apiClient` 的桥接。
2. 保留兼容导出接口（不做删除）。
3. 不改变函数签名与对外错误类型。

### 验证用例
- 启动应用后首屏请求正常。
- 登录态请求头（含鉴权/CSRF）与基线一致。
- 错误场景（401/403/5xx）提示文案与包装结构不变。

### 命令门禁
```bash
cd web/frontend
npm run type-check
npm run test
npm run test:e2e:chromium
npm run pm2:start && npm run pm2:status && npm run pm2:logs && npm run pm2:stop
```

### 回滚
```bash
git revert <PR-1-merge-commit>
```

---

## PR-2（Batch 1B）：收敛 `unifiedApiClient` 到 canonical client

### 变更范围（仅限）
- `web/frontend/src/api/unifiedApiClient.ts`

### 必做动作
1. 保持 `unifiedApiClient` 兼容导出存在。
2. 所有内部实现明确绑定 canonical client。
3. 不改动外部调用约定（导出名、异常类型、返回结构）。

### 验证用例
- 依赖 `unifiedApiClient` 的调用方行为等价。
- 合同错误（ContractValidationError）链路不回归。

### 命令门禁
```bash
cd web/frontend
npm run type-check
npm run test
npm run test:e2e:chromium
npm run pm2:start && npm run pm2:status && npm run pm2:logs && npm run pm2:stop
```

### 回滚
```bash
git revert <PR-2-merge-commit>
```

---

## PR-3（Batch 2A）：迁移 `WencaiQueryEngine` 入口依赖

### 变更范围（仅限）
- `web/frontend/src/services/WencaiQueryEngine.ts`

### 必做动作
1. 移除对 `@/services/api-client` 的直接耦合。
2. 迁移到 canonical client 或统一 API 门面。
3. 保持查询参数、分页和异常处理语义不变。

### 验证用例
- 问财查询成功/失败路径一致。
- 分页与筛选结果与基线一致。

### 命令门禁
同 PR-1。

### 回滚
```bash
git revert <PR-3-merge-commit>
```

---

## PR-4（Batch 2B）：迁移 `TradingApiManager` + `useStrategy`

### 变更范围（仅限）
- `web/frontend/src/services/TradingApiManager.ts`
- `web/frontend/src/composables/useStrategy.ts`

### 必做动作
1. 收敛 `@/api` barrel 过度依赖。
2. 统一请求入口，避免新增并行 client。
3. 保持策略相关接口行为与提示逻辑不变。

### 验证用例
- 策略页面核心流程可用。
- 策略新增/编辑/查询（若适用）无回归。

### 命令门禁
同 PR-1。

### 回滚
```bash
git revert <PR-4-merge-commit>
```

---

## PR-5..N（Batch 3）：`@/api` 广覆盖拆模块迁移

### 拆分原则
- 每个 PR 只覆盖一个业务域（如 user/trade/strategy/market）。
- 单 PR 目标：可审阅、可回滚、可独立验证。

### 验证最小集
- `npm run type-check`
- `npm run test`
- `npm run test:e2e:chromium`

涉及样式时额外执行：
```bash
cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"
```

---

## Backend legacy 清理 PR（单独批次）

### 变更范围
- 仅 `compatibility-inventory.md` 列出的 `.old/.new/.bak/.backup*` 文件。

### 删除前证据（必须写入 PR）
1. 引用扫描结果（backend/scripts/.github）。
2. 路由注册/动态导入复核结果。
3. backend smoke 结果。

### 命令门禁
```bash
pytest -m "not slow"
```

### 回滚
```bash
git revert <backend-legacy-cleanup-merge-commit>
```

---

## 统一完成定义（DoD）
每个 PR 合并前必须满足：
1. 范围文件与本矩阵一致（无外溢改动）；
2. 门禁命令全部通过并附关键输出；
3. 回滚命令已验证可执行；
4. 未新增任何 API client 并行入口。
