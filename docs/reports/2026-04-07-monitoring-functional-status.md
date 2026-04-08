# Monitoring Functional Status

> **使用说明**:
> 本文件用于补完 2026-04-07 Phase 3 前端结构审计中的 `views/monitoring` 功能树判定。
> 当前共享规则、删除门禁与迁移收口口径仍以 `architecture/STANDARDS.md` 为准；本文件不构成删除批准。

**Generated:** 2026-04-07  
**Branch observed:** `wip/root-dirty-20260403`

---

## 1. Scope

本次只判断 `web/frontend/src/views/monitoring/` 当前属于什么状态：

- 是不是现役主路由真相
- 哪些页面仍被历史路由保留
- 哪些页面主要由测试守护

---

## 2. Locked Truths

当前前端主路由真相源仍是：

```text
web/frontend/index.html -> /src/main-standard.ts -> /src/router/index.ts
```

在当前真相链中：

- `web/frontend/src/router/index.ts:213-289` 已使用 `views/risk/*` 页面承担风险域职责
- 本段未导入 `views/monitoring/*`

这意味着 `views/monitoring/` 不是当前主路由真相源。

---

## 3. Current Asset Inventory

当前目录中存在：

- `AlertRulesManagement.vue`
- `MonitoringDashboard.vue`
- `RiskDashboard.vue`
- `WatchlistManagement.vue`
- `composables/useAlertRulesManagement.ts`
- `composables/useRiskDashboard.ts`
- `composables/useWatchlistManagement.ts`
- 4 份对应样式文件

---

## 4. Route And Test Evidence

### 4.1 Historical Router Evidence

`web/frontend/src/router/index.js:278-297` 当前仍保留旧 monitoring layout：

- `/monitoring/watchlists` -> `@/views/monitoring/WatchlistManagement.vue`
- `/monitoring/risk` -> `@/views/monitoring/RiskDashboard.vue`

这说明：

- `WatchlistManagement.vue`
- `RiskDashboard.vue`

仍是 `historical router targets`。

### 4.2 Test Guard Evidence

以下测试仍直接守护 monitoring 页面或样式：

- `web/frontend/tests/unit/config/monitoring-style-sources.spec.ts:11-14`
  - 守护 `AlertRulesManagement.scss`
  - 守护 `MonitoringDashboard.scss`
- `web/frontend/tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts:11-14`
  - 守护 `RiskDashboard.scss`
  - 守护 `WatchlistManagement.scss`
- `web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts:11-15`
  - 守护 4 个 monitoring 页面入口
- `web/frontend/tests/monitoring-redesign-verification.spec.ts:18-170`
  - 通过 `/monitoring/watchlists`
  - 通过 `/monitoring/risk`
  - 对 watchlist/risk 页面做 Playwright 验证
- `web/frontend/tests/redesign-monitoring.spec.ts`
  - 也对 watchlist/risk 页面做 redesign 验证

因此，`views/monitoring/` 当前至少是：

- `historical router target`
- `test-guarded asset`

而不是：

- `可直接删除目录`

---

## 5. Functional Tree Judgment

| Object | Current Status | Reason |
|---|---|---|
| `WatchlistManagement.vue` | `历史路由目标 + 测试守护对象` | 历史 `index.js` 仍直接路由到它；Playwright 与 config spec 都继续守护 |
| `RiskDashboard.vue` | `历史路由目标 + 测试守护对象` | 历史 `index.js` 仍直接路由到它；Playwright 与 config spec 都继续守护 |
| `AlertRulesManagement.vue` | `测试守护对象，待判定` | 当前未见主路由导入，但入口与样式仍被 config spec 直接守护 |
| `MonitoringDashboard.vue` | `测试守护对象，待判定` | 当前未见主路由导入，但入口与样式仍被 config spec 直接守护 |
| `composables/useAlertRulesManagement.ts` | `support module` | 服务 `AlertRulesManagement.vue` |
| `composables/useRiskDashboard.ts` | `support module` | 服务 `RiskDashboard.vue` |
| `composables/useWatchlistManagement.ts` | `support module` | 服务 `WatchlistManagement.vue` |

目录级综合判断：

```text
historical router targets + test-guarded monitoring assets
```

---

## 6. Keep Rationale

当前更合理的保留理由是：

- `WatchlistManagement.vue` 与 `RiskDashboard.vue` 仍承接历史 `/monitoring/*` 路由证据
- `AlertRulesManagement.vue` 与 `MonitoringDashboard.vue` 虽未见现役主路由导入，但仍被样式与入口规范测试守护
- 两组 Playwright 监控页面验证脚本仍把 `/monitoring/watchlists` 与 `/monitoring/risk` 当成可访问目标

因此现阶段不应把 `views/monitoring/` 写成：

- `dead code`
- `unused directory`

---

## 7. Exit Conditions

若后续要推进 `views/monitoring/` 归档或收口，至少应满足：

1. 历史 `router/index.js` 的 monitoring layout 状态已完成归档说明
2. `/monitoring/watchlists` 与 `/monitoring/risk` 的 Playwright 验证脚本完成迁移、删除或归档说明
3. `monitoring-*.spec.ts` 的守护职责已迁移到新的 canonical 页面或完成下线说明
4. 明确 `AlertRulesManagement.vue` 与 `MonitoringDashboard.vue` 在功能树中属于：
   - 正式下线
   - 兼容保留
   - 或迁移中的测试资产

在此之前，不适合直接做：

- 整目录删除
- 机械搬迁
- 仅凭 `router/index.ts` 无引用就判定为可删

---

## 8. Recommended Next Step

下一步最合理的动作不是删文件，而是补两件事：

1. 给 `/monitoring/watchlists` 与 `/monitoring/risk` 写清“历史路由目标但非当前主路由真相”的说明
2. 给 `AlertRulesManagement.vue` 与 `MonitoringDashboard.vue` 补“为何仍受测试守护”的功能树口径

---

## 9. Evidence

本次报告主要基于以下证据：

```bash
find web/frontend/src/views/monitoring -maxdepth 2 -type f \( -name '*.vue' -o -name '*.scss' -o -name '*.ts' \) | sort
nl -ba web/frontend/src/router/index.js | sed -n '236,305p'
nl -ba web/frontend/src/router/index.ts | sed -n '213,300p'
nl -ba web/frontend/tests/unit/config/monitoring-style-sources.spec.ts | sed -n '1,120p'
nl -ba web/frontend/tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts | sed -n '1,120p'
nl -ba web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts | sed -n '1,120p'
nl -ba web/frontend/tests/monitoring-redesign-verification.spec.ts | sed -n '1,180p'
rg -n --no-messages "AlertRulesManagement|MonitoringDashboard|RiskDashboard|WatchlistManagement" web/frontend/src web/frontend/tests -g '*.vue' -g '*.ts' -g '*.spec.ts'
```

---

## 10. References

- `architecture/STANDARDS.md`
- `docs/reports/2026-04-07-legacy-router-asset-status.md`
- `docs/reports/2026-04-07-frontend-structure-repo-truth-audit.md`
- `docs/reports/2026-04-07-phase3-execution-preconditions.md`
- `web/frontend/src/router/index.ts`
- `web/frontend/src/router/index.js`
- `web/frontend/src/views/monitoring/`
