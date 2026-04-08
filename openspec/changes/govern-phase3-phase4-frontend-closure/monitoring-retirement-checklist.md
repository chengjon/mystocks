# Monitoring Retirement Checklist

> **历史文档说明**:
> 本文档用于完成 `govern-phase3-phase4-frontend-closure` 的任务 `2.3`，
> 对齐 `views/monitoring/*` 的历史路由、Vitest 守护和 Playwright 覆盖，形成退场前置条件。
> 本文档不是删除批准，也不代表当前已经完成目录收口。

**Generated:** 2026-04-07  
**Change:** `govern-phase3-phase4-frontend-closure`  
**Task:** `2.3 Produce and approve the monitoring retirement checklist aligning historical routes, Vitest guards, and Playwright coverage`

## 1. Locked Judgment

`web/frontend/src/views/monitoring/` 当前目录级状态是：

```text
historical router targets + test-guarded monitoring assets
```

因此，它不属于“当前主路由真相源”，但也绝不是“可直接删除目录”。

## 2. Why Retirement Is Blocked

### 2.1 Historical Route Targets Still Exist

`web/frontend/src/router/index.js:280-297` 仍定义：

- `/monitoring/watchlists` -> `@/views/monitoring/WatchlistManagement.vue`
- `/monitoring/risk` -> `@/views/monitoring/RiskDashboard.vue`

这意味着至少以下两个页面仍有历史路由目标角色：

- `WatchlistManagement.vue`
- `RiskDashboard.vue`

### 2.2 Vitest Still Guards Monitoring Assets

当前仍有 3 组配置型单测直接守护 monitoring 页面或样式：

| Test File | Guarded Asset |
|---|---|
| `tests/unit/config/monitoring-style-sources.spec.ts` | `AlertRulesManagement.scss`, `MonitoringDashboard.scss` |
| `tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts` | `RiskDashboard.scss`, `WatchlistManagement.scss` |
| `tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts` | 4 个 monitoring 页面入口 `.vue` |

### 2.3 Playwright Still Uses Monitoring Routes

当前仍有 2 组 Playwright 脚本直接访问历史 monitoring 路径：

| Test File | Covered Path | Covered Page |
|---|---|---|
| `tests/monitoring-redesign-verification.spec.ts` | `/monitoring/watchlists` | `WatchlistManagement.vue` |
| `tests/monitoring-redesign-verification.spec.ts` | `/monitoring/risk` | `RiskDashboard.vue` |
| `tests/redesign-monitoring.spec.ts` | `/monitoring/watchlists` | `WatchlistManagement.vue` |
| `tests/redesign-monitoring.spec.ts` | `/monitoring/risk` | `RiskDashboard.vue` |

## 3. Asset Checklist

| Asset | Current Role | Retirement Blocker | Required Resolution |
|---|---|---|---|
| `src/views/monitoring/WatchlistManagement.vue` | 历史路由目标 + 测试守护对象 | 历史 `index.js` 路由 + 双 Playwright 脚本 + 样式单测 | 先迁移或下线 `/monitoring/watchlists` 的脚本与说明 |
| `src/views/monitoring/RiskDashboard.vue` | 历史路由目标 + 测试守护对象 | 历史 `index.js` 路由 + 双 Playwright 脚本 + 样式单测 | 先迁移或下线 `/monitoring/risk` 的脚本与说明 |
| `src/views/monitoring/AlertRulesManagement.vue` | 测试守护对象，待判定 | 页面入口仍被 Vitest 守护 | 先明确它是兼容保留、迁移中资产还是正式下线 |
| `src/views/monitoring/MonitoringDashboard.vue` | 测试守护对象，待判定 | 页面入口仍被 Vitest 守护 | 先明确它是兼容保留、迁移中资产还是正式下线 |
| `src/views/monitoring/composables/useAlertRulesManagement.ts` | support module | 依附于 `AlertRulesManagement.vue` | 跟随页面归类 |
| `src/views/monitoring/composables/useRiskDashboard.ts` | support module | 依附于 `RiskDashboard.vue` | 跟随页面归类 |
| `src/views/monitoring/composables/useWatchlistManagement.ts` | support module | 依附于 `WatchlistManagement.vue` | 跟随页面归类 |

## 4. Retirement Checklist

只有全部满足后，`views/monitoring/` 才能进入归档/迁移讨论：

- [ ] 4.1 历史 `router/index.js` 中 `/monitoring/watchlists` 与 `/monitoring/risk` 的角色已在历史路由策略中完成去真相化
- [ ] 4.2 `tests/monitoring-redesign-verification.spec.ts` 已迁移、删除，或在历史测试资产中完成保留说明
- [ ] 4.3 `tests/redesign-monitoring.spec.ts` 已迁移、删除，或在历史测试资产中完成保留说明
- [ ] 4.4 `tests/unit/config/monitoring-style-sources.spec.ts` 的守护对象已迁移到新 canonical 页面，或完成正式下线说明
- [ ] 4.5 `tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts` 的守护对象已迁移到新 canonical 页面，或完成正式下线说明
- [ ] 4.6 `tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts` 中 4 个 monitoring 页面入口的职责已改写或下线
- [ ] 4.7 `AlertRulesManagement.vue` 已被归类为 `兼容保留`、`迁移中测试资产` 或 `正式下线`
- [ ] 4.8 `MonitoringDashboard.vue` 已被归类为 `兼容保留`、`迁移中测试资产` 或 `正式下线`
- [ ] 4.9 若存在新的 canonical 风险/监控页面，Playwright 与 Vitest 已完成守护切换

## 5. Do-Not-Do Rules

在完成上面的 checklist 之前，禁止：

1. 仅凭 `router/index.ts` 未引用就删除 `views/monitoring/`
2. 只迁移 `.vue` 文件而不处理对应测试
3. 只改测试路径而不说明历史 `/monitoring/*` 路由为何退场
4. 把 `AlertRulesManagement.vue` 和 `MonitoringDashboard.vue` 机械归为“未使用”

## 6. Recommended Retirement Sequence

推荐顺序如下：

1. 先完成 `E2` 历史路由去真相化
2. 再确定 `/monitoring/watchlists` 与 `/monitoring/risk` 是否仍保留历史访问价值
3. 然后处理两组 Playwright 脚本
4. 再处理 3 组 Vitest config 守护
5. 最后才讨论 `views/monitoring/` 目录级归档或拆分

## 7. Decision Output for Batch E3

本批次产出如下：

- `WatchlistManagement.vue` 与 `RiskDashboard.vue` 继续按“历史路由目标 + 测试守护对象”保留
- `AlertRulesManagement.vue` 与 `MonitoringDashboard.vue` 继续按“测试守护对象，待判定”保留
- `views/monitoring/` 当前不能进入目录级删除或机械搬迁
- 后续如要收口，必须先把路由、Vitest、Playwright 三层一起迁移或下线
