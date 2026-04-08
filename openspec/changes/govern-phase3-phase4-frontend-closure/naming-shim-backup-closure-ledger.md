# Naming / Shim / Backup Closure Ledger

> **历史文档说明**:
> 本文档用于完成 `govern-phase3-phase4-frontend-closure` 的任务 `3.3`。
> 本批次按照 `architecture/STANDARDS.md` 与当前 OpenSpec 的 governance-first 口径执行：
> 对命名 / shim / backup 对象逐类给出 `keep / deprecate / archive-candidate / blocked-remove` 决策、
> 迁移前提与验证命令，而不是在状态不明时直接删除。

**Generated:** 2026-04-08  
**Change:** `govern-phase3-phase4-frontend-closure`  
**Task:** `3.3 Execute naming / shim / backup closure batch E6 only after upstream structural convergence is complete`

## 1. E6 Execution Verdict

E6 在本 change 中已按“收口台账”完成，而不是按“大规模删除/迁移”完成。

原因：

- 当前 change 的主轴仍是 frontend structural closure governance，而不是一次性清空所有历史文件
- `directory-governance` 明确要求：若 legacy asset 仍被 tests / historical routes / tooling 引用，应记录退场门禁，而不是立即删除
- 经过 E1-E5，当前已具备对 naming / shim / backup 对象做分桶决策的条件

因此，本批次的完成标准定义为：

1. 每类对象都获得明确 lifecycle / decision
2. 每类对象都写清 migration gate
3. 必要的保留对象有 caller / test / doc 证据
4. 不明状态对象不被误删

## 2. Decision Matrix

### 2.1 Active / Compatibility Entry Objects

| Object | Decision | Why | Next Gate |
|---|---|---|---|
| `web/frontend/src/main-standard.ts` | `keep-canonical` | 当前 runtime truth：`index.html -> main-standard.ts -> router/index.ts` | 无 |
| `web/frontend/src/main.js` | `blocked-remove` | `verify-mount.js` 仍直接读取；`scripts/debug_vite.js` 仍把 `/src/main.js` 作为调试目标 | 先改 `verify-mount.js` / `scripts/debug_vite.js` 的 consumer truth，再决定归档 |
| `web/frontend/verify-mount.js` | `keep-tooling` | 当前仍承担 legacy boot 校验脚本职责；`node web/frontend/verify-mount.js` 实测通过 | 若后续改为校验 `main-standard.ts`，可再判定是否退役 |
| `scripts/debug_vite.js` | `keep-tooling` | 仍把 `/src/main.js` 作为 Vite 调试探测目标 | 需先决定该调试脚本是否仍有效 |
| `web/frontend/src/_entry-archive/*` | `keep-archived` | 已有 archive README 且 caller matrix 认定为 zero-consumer archived variants | 保持归档，不回流运行链 |

### 2.2 Legacy Router History Objects

| Object | Decision | Why | Next Gate |
|---|---|---|---|
| `web/frontend/src/router/index.js.clean` | `archive-candidate` | 已定性为 `historical broken backup / stale working copy` | 文档入口改写与 router history 分层目录到位后再迁移 |
| `web/frontend/src/router/index.js.backup-phase2.3` | `archive-candidate` | 已定性为 `historical backup`，需与 `index.js` 成组处理 | E4 相关历史页面语义收口后再迁移 |
| `web/frontend/src/router/phase4.routes.js` | `blocked-remove` | 仍承担 `Phase4Dashboard` 历史独立入口证据 | 先完成 duplicate-page / missing page 去向判定 |
| `web/frontend/src/router/index.js.backup` | `archive-candidate` | 当前未发现活跃 caller，表现为未治理的历史路由备份 | 纳入后续 router history 成组编目 |
| `web/frontend/src/router/index.ts.backup` | `archive-candidate` | 当前未发现活跃 caller，表现为 TS 路由备份样本 | 纳入后续 router history 成组编目 |

### 2.3 Zero-Caller Frontend Backup Files

以下对象在当前代码 / 测试 / OpenSpec / 规划检索中未发现活跃消费者，判定为 `archive-candidate`，默认不再作为 active truth：

- `web/frontend/src/App.vue.backup`
- `web/frontend/src/api/types/common.ts.bak`
- `web/frontend/src/config/pageConfig.ts.bak`
- `web/frontend/src/stores/baseStore.ts.bak`
- `web/frontend/src/types/backend_types.ts.bak`
- `web/frontend/src/components/layout/Breadcrumb.vue.backup`
- `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue.bak`
- `web/frontend/src/layouts/archive/MainLayout.vue.artdeco.backup`
- `web/frontend/src/views/PortfolioManagement.vue.artdeco.backup`
- `web/frontend/src/views/announcement/AnnouncementMonitor.vue.backup`
- `web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue.backup`
- `web/frontend/src/main.js.backup`

这些对象的当前口径：

- `decision`: `archive-candidate`
- `default bias`: `archive/delete > rewrite`
- `mutation gate`: 应等待 documentation-governance taxonomy / inventory / decision register wave 接管文档侧路径更新，避免在历史文档仍引用原路径时制造无解释漂移

### 2.4 Compatibility Shim Objects

| Object | Decision | Why | Evidence | Next Gate |
|---|---|---|---|---|
| `web/frontend/src/utils/useWebSocketWithConfig.ts` | `keep-compat` | 当前是薄兼容 shim，主动把 legacy import path 转发到 canonical composable | `tests/unit/use-websocket-with-config.spec.ts` 明确要求 legacy path 与 canonical path 等价，且本次实测 `3/3` 通过 | 只有在 legacy import path 迁移完成且兼容测试退役后，才允许删除 |

### 2.5 Root Shim Objects

| Object | Decision | Why | Next Gate |
|---|---|---|---|
| `core.py` | `blocked-remove` | 仓库 README / docs / tests 快照仍大量使用 `from core import ...` 语义 | 需由 documentation-governance 与 import migration 一起治理 |
| `data_access.py` | `blocked-remove` | root-level compatibility entry 仍存在 | 需确认无 legacy import consumer |
| `monitoring.py` | `blocked-remove` | root-level compatibility entry 仍存在 | 需确认无 legacy import consumer |
| `src/core.py` | `blocked-remove` | 当前仍形成 shim chain：`src/core.py -> core.py` | 不属于本轮 frontend-only runtime mutation，需单独治理 |

## 3. Verification Evidence

### 3.1 Legacy Entry Tooling Still Active

执行：

```bash
node web/frontend/verify-mount.js
```

结果：

- `index.html` 包含 `#app` = `true`
- `main.js` 包含 `app.mount` = `true`
- `app.mount` 不在 `.then()` 中 = `true`

结论：

- `main.js` / `verify-mount.js` 当前仍构成有效 tooling relationship
- 在该关系收口前，不应把 `main.js` 列为可删文件

### 3.2 Compatibility Shim Still Guarded

执行：

```bash
cd web/frontend && npx vitest run tests/unit/use-websocket-with-config.spec.ts
```

结果：

- `1` test file passed
- `3` tests passed

结论：

- `src/utils/useWebSocketWithConfig.ts` 不是“无人使用的死 shim”
- 当前它仍被明确测试为 legacy import compatibility surface

### 3.3 Structural Safety Baseline

本批次未引入新的 frontend runtime mutation。

沿用 E5 收口后的验证基线：

- `npx vue-tsc --noEmit --pretty false` = pass
- `npm run build` = pass
- E5 scoped stylelint = pass
- `npm run test:e2e:stable` = `10 passed`

因此，本批次的 ledger 更新不会反向破坏已完成的 E5 门禁。

## 4. Completion Marker For E6

当前 E6 可判定为已完成，理由不是“所有 shim / backup 都已删除”，而是：

1. 命名 / shim / backup 对象已完成 change-scoped lifecycle 决策
2. 每类对象都具备：
   - `keep / archive-candidate / blocked-remove`
   - migration gate
   - evidence / verification command
3. 高风险对象未被误删
4. 低风险对象已被明确降级为非 active truth

这符合 `docs/reports/2026-04-07-phase3-4-execution-matrix.md` 对 E6 的完成标志要求。

## 5. Recommended Next Step

后续若要继续做真实迁移或删除，应分成两个 follow-up 方向：

1. **Frontend history relocation wave**
   - 为 `router/*.backup*`、`*.bak`、`*.backup` 建立统一 history/archive subtree
   - 配套 history README / taxonomy / decision register

2. **Shim retirement wave**
   - 优先处理 `verify-mount.js` / `scripts/debug_vite.js` 与 `main.js` 的 caller 收口
   - 之后再处理 `src/utils/useWebSocketWithConfig.ts`
   - root shim chain (`core.py` / `data_access.py` / `monitoring.py`) 应在独立变更中与 import migration 一起治理
