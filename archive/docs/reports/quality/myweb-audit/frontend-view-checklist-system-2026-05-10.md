# Frontend View Checklist: `views/system/*`

日期：2026-05-10

范围：`web/frontend/src/views/system/*`

本批次目的：复核系统设置域目录中当前活跃路由页、view-local 支持资产、legacy static shell 的边界，避免把仍在 router truth 内的系统页误归档，也避免把历史 `menu.config.js` 旧路径当作当前菜单真相。

## 1. Truth Inputs

菜单 / 路由真相：

- `web/frontend/src/layouts/MenuConfig.ts` 当前系统设置菜单包含 `/system/config`、`/system/health`、`/system/api`、`/system/resources`、`/system/data`。
- `web/frontend/src/router/index.ts` 当前动态导入：
- `/system/config` -> `@/views/system/Settings.vue`。
- `/system/health` -> `@/views/system/Health.vue`。
- `/system/api` -> `@/views/system/API.vue`。
- `/system/resources` -> `@/views/system/Resources.vue`。
- `/system/data` -> `@/views/system/DataSource.vue`。

配置 / 历史迁移证据：

- `web/frontend/src/config/pageConfig.ts` 仍登记 `system-config`、`system-health`、`system-api`、`system-resources`、`system-data`。
- `openspec/changes/restructure-frontend-directory/tasks.md` 明确 `Settings.vue`、`Health.vue`、`API.vue`、`DataSource.vue` 已迁入 `views/system/*` canonical route entries，并保留 ArtDeco legacy wrapper。
- `docs/FUNCTION_TREE.md` 将 `system/API.vue`、`system/Resources.vue`、`system/Settings.vue`、`system/DataSource.vue` 等列为系统管理、监控、配置、数据源治理入口。
- `web/frontend/src/config/menu.config.js` 中仍可见 `/system/architecture`、`/system/database-monitor`、`/system/monitoring` 等旧路径，但当前治理口径以 `layouts/MenuConfig.ts` + `router/index.ts` 为准，这些旧路径不能覆盖当前 route truth。

直接测试守护：

- `web/frontend/src/views/system/__tests__/Settings.spec.ts`
- `web/frontend/src/views/system/__tests__/Health.spec.ts`
- `web/frontend/src/views/system/__tests__/API.spec.ts`
- `web/frontend/src/views/system/__tests__/Resources.spec.ts`
- `web/frontend/src/views/system/__tests__/DataSource.spec.ts`
- `web/frontend/src/views/system/__tests__/Architecture.spec.ts`
- `web/frontend/src/views/system/__tests__/DatabaseMonitor.spec.ts`
- `web/frontend/src/views/system/__tests__/PerformanceMonitor.spec.ts`

## 2. Page Classification

| 页面 | 当前分类 | 路由状态 | 资产状态 | 守护状态 | 结论 |
| --- | --- | --- | --- | --- | --- |
| `views/system/Settings.vue` | `canonical-active` | `/system/config` | 系统配置 active route | direct spec + system manifests | 排除归档审核 |
| `views/system/Health.vue` | `canonical-active` | `/system/health` | 健康矩阵 active route | direct spec + system manifests | 排除归档审核 |
| `views/system/API.vue` | `canonical-active` | `/system/api` | API/遥测 active route | direct spec + system manifests | 排除归档审核 |
| `views/system/Resources.vue` | `canonical-active` | `/system/resources` | 资源使用 active route | direct spec + system manifests | 排除归档审核 |
| `views/system/DataSource.vue` | `canonical-active` | `/system/data` | 数据源治理 active route | direct spec + system manifests | 排除归档审核 |
| `views/system/healthProbeContract.ts` | `canonical-support-asset` | helper | 健康探针响应归一化契约 | imported by active system health/API flow | 非 view，排除归档审核 |
| `views/system/composables/useSystemResourcesPage.ts` | `canonical-support-asset` | helper | `Resources.vue` view-local composable | `Resources.spec.ts` + system manifests | 非 view，排除归档审核 |
| `views/system/styles/API.scss` | `canonical-support-asset` | style | `API.vue` 页面样式资产 | page style import | 非 view，排除归档审核 |
| `views/system/styles/Resources.scss` | `canonical-support-asset` | style | `Resources.vue` 页面样式资产 | page style import | 非 view，排除归档审核 |
| `views/system/Architecture.vue` | `candidate-review` | dead route | honest static shell，无 verified architecture owner | direct spec + secondary manifest | 不归档，需先迁移/退役守护 |
| `views/system/DatabaseMonitor.vue` | `candidate-review` | dead route | honest static shell，无 verified database-monitor owner | direct spec + secondary manifest | 不归档，需先迁移/退役守护 |
| `views/system/PerformanceMonitor.vue` | `candidate-review` | dead route | honest static shell，无 verified performance-monitor owner | direct spec + secondary manifest | 不归档，需先迁移/退役守护 |
| `views/system/styles/Architecture.scss` | `candidate-support-asset` | style | `Architecture.vue` 静态壳样式 | tied to candidate static shell | 随候选页处理 |
| `views/system/styles/DatabaseMonitor.scss` | `candidate-support-asset` | style | `DatabaseMonitor.vue` 静态壳样式 | tied to candidate static shell | 随候选页处理 |
| `views/system/styles/PerformanceMonitor.css` | `candidate-support-asset` | style | `PerformanceMonitor.vue` 静态壳样式 | tied to candidate static shell | 随候选页处理 |

## 3. Redundant-Page Checklist

本批次未发现可直接归档页面。

必须保留的页面：

- `Settings.vue`、`Health.vue`、`API.vue`、`Resources.vue`、`DataSource.vue` 全部是当前 router truth，不能进入 archive flow。
- `Resources.vue` 使用 view-local composable `useSystemResourcesPage.ts`，符合单消费者 co-location 口径，不应为了“治理”提前下沉或机械拆分。
- `Health.vue`、`API.vue`、`DataSource.vue` 仍被 ArtDeco legacy wrapper 反向引用，属于当前兼容链路的一部分。

暂不归档的候选页面：

- `Architecture.vue`、`DatabaseMonitor.vue`、`PerformanceMonitor.vue` 当前不是 `router/index.ts` 的 active route owner，也不在当前 `layouts/MenuConfig.ts` 系统菜单内。
- 这 3 个页面已降级为 `legacy-static-shell`，不再展示伪架构、伪数据库健康、伪性能预算或本地运行态。
- 它们仍有直接 spec 和 secondary manifest 守护，因此只能标为 `candidate-review`，不能直接移动到 archive。

禁止误判项：

- `web/frontend/src/config/menu.config.js` 中的 `/system/architecture`、`/system/database-monitor`、`/system/monitoring` 是旧菜单配置痕迹，不是当前治理的唯一菜单真相。
- 历史文档中 `/system/architecture` 或 `/system/database-monitor` 曾被标记为 migrated，不代表当前 router truth 仍保留对应路径。
- `Architecture.vue` 等静态壳虽然可疑，但已有测试守护“不得展示伪实况”的边界；归档前必须先迁移或退役对应测试。

## 4. Batch Conclusion

`views/system/*` 当前应拆成四类治理：

- `canonical-active`：`Settings.vue`、`Health.vue`、`API.vue`、`Resources.vue`、`DataSource.vue`，全部直接排除 archive flow。
- `canonical-support-asset`：`healthProbeContract.ts`、`useSystemResourcesPage.ts`、active route 样式资产，保留为系统 active route 的本地支持层。
- `candidate-review`：`Architecture.vue`、`DatabaseMonitor.vue`、`PerformanceMonitor.vue`，仅登记为 legacy static shell 候选，不满足 archive-approved 条件。
- `candidate-support-asset`：与 3 个 static shell 绑定的样式文件，随对应候选页面一起治理。

本批次没有文件进入 `archive-approved`。后续若要处理 3 个 legacy static shell，应先决定旧 `menu.config.js` 路径是否需要正式下线/清理，并迁移或退役对应 direct specs。
