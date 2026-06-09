# Frontend View Checklist: Blank Layout And Error Views

日期：2026-05-10

范围：

- `web/frontend/src/views/Login.vue`
- `web/frontend/src/views/NotFound.vue`
- `web/frontend/src/views/errors/*`

本批次目的：复核 blank-layout 特殊路由和未路由错误页资产的边界，避免把 `/login`、404 误归档，也避免把 `views/errors/*` 在仍有 mainline/style guard 的情况下直接移动或删除。

## 1. Truth Inputs

路由 / 菜单真相：

- `web/frontend/src/router/index.ts` 当前注册 `/login` -> `@/views/Login.vue`，`meta.layout = Blank`。
- `web/frontend/src/router/index.ts` 当前注册 `/:pathMatch(.*)*` -> `@/views/NotFound.vue`，`meta.layout = Blank`。
- `web/frontend/src/router/index.ts` 当前没有导入 `@/views/errors/*`。
- `web/frontend/src/layouts/MenuConfig.ts` 不包含 `/login`、404 或 `views/errors/*`；这是预期行为，blank-layout 与错误页不进入两层主菜单。
- `openspec/changes/update-frontend-view-governance/specs/frontend-routing/spec.md` 要求 dashboard、blank-layout pages、not-found pages、detail routes 等特殊路由保持在两层主菜单之外，除非有单独审批的导航变更。

历史审计证据：

- `docs/reports/quality/myweb-audit/audit-20260426-02/batches/blank-batch-01-audit.md` 已覆盖 `/login` 与 catch-all 404，确认二者是 routed blank-layout shell pages。
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/blank-layout-login-and-404-shell-audit.md` 记录 `/login` 不需要代码修复，404 recovery 已改为使用 canonical `HOME_ROUTE_PATH`。
- `docs/reports/quality/myweb-audit/frontend-menu-view-structure-audit-2026-05-10.md` 将 `/login` 与 `/:pathMatch(.*)*` 标为 Blank layout 特殊页，不进入主菜单。

错误页库存 / guard 证据：

- `docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.md` 将 `views/errors/Forbidden.vue`、`NetworkError.vue`、`ServiceUnavailable.vue` 归入 Demo 废弃低优先级库存。
- `web/frontend/tests/unit/config/errors-mainline-gate.spec.ts` 仍要求 `lint:artdeco:changed` 覆盖 `--target-dir src/views/errors --changed-from-git`，并防止退回单文件 fallback。
- `web/frontend/tests/unit/config/errors-forbidden-style-source.spec.ts` 守护 `Forbidden.vue` 的 ArtDeco token 变量。
- `web/frontend/tests/unit/config/errors-network-style-source.spec.ts` 守护 `NetworkError.vue` 的 ArtDeco token 变量。
- `web/frontend/tests/unit/config/errors-service-unavailable-style-source.spec.ts` 守护 `styles/ServiceUnavailable.scss` 的 ArtDeco token 变量。

## 2. Page Classification

| 页面 / 资产 | 当前分类 | 路由状态 | 菜单状态 | 资产状态 | 守护状态 | 结论 |
| --- | --- | --- | --- | --- | --- | --- |
| `views/Login.vue` | `special-blank-active` | `/login` | 不进主菜单 | 登录 blank-layout route owner | blank-batch evidence | 排除归档审核 |
| `views/NotFound.vue` | `special-blank-active` | `/:pathMatch(.*)*` | 不进主菜单 | 404 blank-layout route owner | blank-batch evidence | 排除归档审核 |
| `views/errors/Forbidden.vue` | `candidate-review/demo-error-shell` | dead route | 不进主菜单 | 403 错误页演示/候选资产 | style guard | 不归档，需先退役 guard 或声明接入策略 |
| `views/errors/NetworkError.vue` | `candidate-review/demo-error-shell` | dead route | 不进主菜单 | 网络错误页演示/候选资产，依赖 `useNetworkStatus` | style guard | 不归档，需先退役 guard 或声明接入策略 |
| `views/errors/ServiceUnavailable.vue` | `candidate-review/demo-error-shell` | dead route | 不进主菜单 | 503 错误页演示/候选资产，含本地 health 检查逻辑 | style guard | 不归档，需先退役 guard 或声明接入策略 |
| `views/errors/styles/ServiceUnavailable.scss` | `candidate-support-asset` | style | n/a | `ServiceUnavailable.vue` 样式资产 | style guard | 随候选页处理 |

## 3. Redundant-Page Checklist

本批次未发现可直接归档页面。

必须保留的 active blank-layout 页面：

- `Login.vue` 是当前 `/login` route owner，负责 auth entry，不进入主菜单但必须保留。
- `NotFound.vue` 是当前 catch-all 404 route owner，属于 Blank layout 特殊页；其 recovery 行为已由历史 blank-batch 修复为 canonical home route truth。
- 二者都不应进入 redundant-page archive review，也不需要走业务页 36/42 family 全量回归口径。

候选待审的错误页资产：

- `Forbidden.vue`、`NetworkError.vue`、`ServiceUnavailable.vue` 当前没有路由、菜单或运行时 import，按 inventory 可视为 Demo / error-shell 候选。
- 这些文件仍被 mainline gate 和 style-source 单测覆盖，因此不能直接移动或删除。
- 若后续决定保留它们，应先补正式错误路由或错误处理接入策略，例如 403、network unavailable、service unavailable 的 route/guard contract。
- 若后续决定不保留它们，应先迁移或退役 `errors-*` guard，再记录 successor / no-successor-needed 后进入 archive move。

需要后续复核的质量风险：

- `Forbidden.vue` 仍把 `goHome()` 写成 `router.push('/')`，未对齐 `HOME_ROUTE_PATH`；若要复活为正式错误页，应复用 404 blank-batch 的 canonical home-route 规则。
- `Forbidden.vue` 包含 `/analysis`、`/settings` 等旧路径链接，和当前 `MenuConfig.ts` 路径不完全一致；若保留，应改为当前路由真相。
- `NetworkError.vue` 与 `ServiceUnavailable.vue` 都有本地定时/健康检查逻辑；若保留为正式页面，应先确认 `/health`、`/health/database`、`/health/cache` 等 endpoint truth，不能把探测失败误报为产品级不可用。

禁止误判项：

- 不能把 `views/errors/*` 和当前 404 route owner 混为一组；当前 404 truth 是 `views/NotFound.vue`。
- 不能用 `MenuConfig.ts` 不包含 `/login` 或 404 判定它们冗余；特殊 blank-layout 页面明确不进主菜单。
- 不能仅凭 `views/errors/*` 未路由直接删除；它们仍受 mainline/style guard 覆盖。

## 4. Batch Conclusion

Blank / errors 当前应拆成三类治理：

- `special-blank-active`：`Login.vue`、`NotFound.vue`，全部排除 archive flow。
- `candidate-review/demo-error-shell`：`Forbidden.vue`、`NetworkError.vue`、`ServiceUnavailable.vue`，未路由但仍有 guard，不能直接归档。
- `candidate-support-asset`：`ServiceUnavailable.scss`，随 `ServiceUnavailable.vue` 一起处理。

本批次没有 `archive-approved` 页面。后续若处理 `views/errors/*`，建议先二选一：要么正式接入错误路由/错误处理 contract；要么退役 guard 并把这些 demo error shells 移入受控 archive。
