# Phase B 执行清单（入口收敛 -> 调用迁移 -> 冗余删除）

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## 0. 执行目标
在不改变业务行为与对外契约的前提下，按批次完成前端 API 入口收敛与后端 legacy 文件下线，并通过统一门禁（baseline + PM2 + E2E）证明“等价可用”。

## 1. 执行假设与前置条件

### 1.1 Canonical 假设（本批次执行口径）
- Frontend canonical client：`web/frontend/src/api/apiClient`
- 过渡兼容层：`web/frontend/src/services/api-client`、`web/frontend/src/services/httpClient.js`、`web/frontend/src/api/unifiedApiClient.ts`

> 若后续架构评审改为 `services/api-client`，需整体反向调整迁移方向（本清单作废重排）。

### 1.2 开工前必须满足
1. 冻结新增 API client 入口（禁止新增并行入口）。
2. 在 PR 描述中声明“仅做入口收敛，不做业务逻辑扩展”。
3. 准备基线记录（认证链路、核心页面加载、关键查询链路）。

---

## 2. Batch 执行计划（按风险）

## Batch 1（高风险，先行）
**范围文件**
- `web/frontend/src/services/httpClient.js`
- `web/frontend/src/api/unifiedApiClient.ts`

**目标**
- 只保留必要桥接语义；所有真实请求路径统一转向 canonical client。
- 不删除兼容导出，只做“去分叉”。

**验收点**
- 鉴权头/CSRF/错误包装行为与基线一致。
- 关键入口（应用启动、登录态请求）无回归。

**PR 退出条件**
- 下面第 4 节门禁全部通过。
- 兼容层仍可用（不提前硬删除）。

---

## Batch 2（中风险，业务调用迁移）
**范围文件**
- `web/frontend/src/services/WencaiQueryEngine.ts`
- `web/frontend/src/services/TradingApiManager.ts`
- `web/frontend/src/composables/useStrategy.ts`

**目标**
- 移除对 `services/api-client` 与不必要 `@/api` barrel 路径耦合。
- 业务服务统一通过 canonical client 或统一 API 门面调用。

**验收点**
- 问财查询、策略链路、分页/筛选与异常提示行为等价。
- 相关页面交互无功能退化。

**PR 退出条件**
- 第 4 节门禁全部通过。
- 新增路径不引入新的兼容入口。

---

## Batch 3（广覆盖，收尾）
**范围文件**
- `@/api` barrel 广覆盖调用方（按模块拆多个 PR）
- Backend legacy 文件（`.old/.new/.bak/.backup*`）

**目标**
- 逐模块削减 `@/api` 广域导入，改为稳定入口或按域 API。
- 删除已确认零引用的 backend legacy 文件。

**验收点**
- 每个模块 PR 均通过第 4 节门禁。
- 删除动作有“零引用证据 + 回滚说明”。

**PR 退出条件**
- 兼容层引用显著下降（可量化对比）。
- backend legacy 清单项逐个闭环。

---

## 3. 后端 legacy 删除执行规范

### 3.1 删除前检查（每个文件都必须做）
1. 代码级引用扫描（backend/scripts/.github）。
2. 路由注册与动态导入复核。
3. 运行时 smoke（服务可启动、关键路由可访问）。

### 3.2 删除范围（当前候选）
- `web/backend/app/api/data_source_config.old.py`
- `web/backend/app/api/technical_analysis.py.new`
- `web/backend/app/api/mystocks_complete.py.bak`
- `web/backend/app/api/risk_management.py.bak`
- `web/backend/app/api/strategy_management.py.backup`
- `web/backend/app/api/data_source_config.py.backup`
- `web/backend/app/api/data.py.backup.20260130`
- `web/backend/app/services/data_adapter.py.backup.20260130`
- `web/backend/app/api/risk_management.py.backup.20260130`

---

## 4. 统一验收门禁（每个 Batch 必跑）

## 4.1 Frontend baseline / quality
在 `web/frontend` 目录：
```bash
npm run type-check
npm run test
npm run test:e2e:chromium
```

## 4.2 PM2 运行态验证
在 `web/frontend` 目录：
```bash
npm run pm2:start
npm run pm2:status
npm run pm2:logs
npm run pm2:stop
```

## 4.3 Backend smoke
在仓库根目录（或 backend 对应目录）至少执行：
```bash
pytest -m "not slow"
```

## 4.4 Stylelint 口径
- 当前为**条件性门禁**：当本批次涉及样式文件或 `.vue` 样式块时执行：
```bash
cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"
```
- 待脚本统一后再升级为硬门禁。

---

## 5. 回滚策略（分层）

## Level 1：单 PR 回滚（首选）
- 使用 git revert 回滚当前 PR，不影响其他批次。
- 适用：单批次引入回归。

## Level 2：批次回滚
- 回滚整个 Batch 的 PR 集合。
- 保留上一批稳定版本。

## Level 3：兼容层紧急恢复
- 临时恢复 `httpClient` / `unifiedApiClient` 桥接导出。
- 用于线上紧急止血，随后进入根因修复。

---

## 6. PR 模板（执行时复制）

## Scope
- 本 PR 仅处理：`[Batch-X + 模块名]`
- 不包含：新功能、新接口、新状态管理方案

## Risk
- 影响链路：`[auth/csrf/error-wrapper/query-flow/route-load]`
- 风险等级：`[high|medium|low]`

## Validation
- [ ] type-check 通过
- [ ] unit/vitest 通过
- [ ] e2e chromium 通过
- [ ] PM2 启停与日志检查通过
- [ ] （如涉及样式）stylelint 通过

## Rollback
- 回滚命令与影响面说明已附

---

## 7. 兼容层 sunset 退出判定
仅当以下条件全部满足，才允许删除过渡入口：
1. 目标兼容入口引用数归零；
2. baseline + PM2 + E2E 连续通过；
3. 至少一个发布窗口观测无关键回归。
