# Frontend View Checklist: `views/announcement/*`

日期：2026-05-10

范围：`web/frontend/src/views/announcement/*`

本批次目的：复核公告工作台目录中详情路由 owner、view-local composable、样式资产和历史备份文件的边界。该目录不是主菜单业务域，但当前仍承载 `/detail/news/:symbol` 特殊详情路由，不能按“未进入侧栏菜单”归档。

## 1. Truth Inputs

路由 / 菜单真相：

- `web/frontend/src/router/index.ts` 当前在 ArtDeco layout children 下注册 `detail` 路由组。
- `/detail/news/:symbol` -> `@/views/announcement/AnnouncementMonitor.vue`，route name 为 `stock-news`。
- `web/frontend/src/layouts/MenuConfig.ts` 不包含 `/detail/news/:symbol`；这是预期行为，详情页不进入两层主菜单。
- `docs/reports/quality/myweb-audit/frontend-menu-view-structure-audit-2026-05-10.md` 已将 `/detail/news/:symbol` 归为特殊详情页，建议保持详情页、不进入主菜单。

功能树 / 历史修复证据：

- `docs/FUNCTION_TREE.md` 将 `views/announcement/` 标记为公告工作台目录，并说明其偏详情 / 规则工作台。
- `docs/FUNCTION_TREE.md` 将公告搜索、订阅管理与运行排障入口关联到 `AnnouncementMonitor.vue` 与 `useAnnouncementMonitor.ts`。
- `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/detail-batch-05-manifest.yaml`、`detail-batch-09-manifest.yaml`、`detail-batch-11-manifest.yaml` 均记录 `/detail/news/:symbol` canonical owner 为 `web/frontend/src/views/announcement/AnnouncementMonitor.vue`。
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/detail-news-stats-refresh-truth-audit.md` 记录当前页面已修复 stats slice refresh truth，保留 verified announcement rows 并清理失败 stats 卡。

测试 / E2E 守护：

- `web/frontend/src/views/announcement/__tests__/AnnouncementMonitor.spec.ts`
- `web/frontend/src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts`
- `web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts` 覆盖 `/detail/news/:symbol` 的 stats、announcement rows、monitor rules、triggered records 以及同实例 symbol 切换。
- `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts` 包含 announcement monitor selector 覆盖。

Guard 口径修正：

- `docs/reports/quality/myweb-audit/frontend-view-guard-map-2026-05-10-review.md` 曾记录“current router has no `/detail` routes”的问题判断；按当前代码复核，该判断已经不成立。
- 当前 `router/index.ts` 明确存在 `/detail/graphics/:symbol` 与 `/detail/news/:symbol`，因此 `/detail/news/:symbol` 相关引用应按 active detail route 处理，不应视为历史文档死链。

## 2. Page Classification

| 页面 / 资产 | 当前分类 | 路由状态 | 资产状态 | 守护状态 | 结论 |
| --- | --- | --- | --- | --- | --- |
| `views/announcement/AnnouncementMonitor.vue` | `special-detail-active` | `/detail/news/:symbol` | 公告详情 / 规则工作台 route owner | direct spec + E2E detail matrix | 排除归档审核 |
| `views/announcement/composables/useAnnouncementMonitor.ts` | `canonical-support-asset` | helper | `AnnouncementMonitor.vue` view-local composable | direct spec + detail manifests | 非 view，排除归档审核 |
| `views/announcement/styles/AnnouncementMonitor.scss` | `canonical-support-asset` | style | `AnnouncementMonitor.vue` 页面样式资产 | style import | 非 view，排除归档审核 |
| `views/announcement/AnnouncementMonitor.vue.backup` | `candidate-review/temp-backup` | dead route | 旧实现备份，含旧统计兜底和内联实现 | 无 active route / 无 direct spec | 不直接删除；后续按 backup 治理比对后归档 |

## 3. Redundant-Page Checklist

本批次未发现可直接归档页面。

必须保留的 active detail route：

- `AnnouncementMonitor.vue` 是当前 `/detail/news/:symbol` 的 route owner，属于特殊详情页，不进入主菜单但仍可访问。
- `useAnnouncementMonitor.ts` 负责公告列表、stats、monitor rules、triggered records 的 selector-local snapshot 与 stale/unavailable 状态，属于页面私有 canonical support asset。
- `AnnouncementMonitor.scss` 随 active detail route owner 保留。

候选待审的备份文件：

- `AnnouncementMonitor.vue.backup` 与当前 `AnnouncementMonitor.vue` 差异显著，保留了旧的单文件实现、内联样式、直接 `stats.total_count || 0` 等兜底口径。
- 该备份文件当前没有路由、菜单、测试或运行时引用，符合 `candidate-review/temp-backup` 信号。
- 但根据 `architecture/STANDARDS.md`，`.backup` 文件不能仅凭“未引用”直接删除；必须先确认它不承担回滚、审计、历史迁移或文档约定职责，并记录 successor / no-successor-needed 结论后，才能进入后续 archive move。

禁止误判项：

- 不能把 `/detail/news/:symbol` 因不在 `MenuConfig.ts` 中而判定为冗余；详情页本就不进入两层主菜单。
- 不能把 `/risk/news` 与 `/detail/news/:symbol` 混为同一 owner：`risk/News.vue` 是风险域主菜单页，`announcement/AnnouncementMonitor.vue` 是详情 / 规则工作台特殊页。
- 不能用旧 `frontend-view-guard-map-2026-05-10-review.md` 中“router 无 `/detail`”的结论继续指导当前批次；当前 router 已存在 detail group。

## 4. Batch Conclusion

`views/announcement/*` 当前应拆成三类治理：

- `special-detail-active`：`AnnouncementMonitor.vue`，作为 `/detail/news/:symbol` 特殊详情 route owner 保留。
- `canonical-support-asset`：`useAnnouncementMonitor.ts`、`AnnouncementMonitor.scss`，随详情 route owner 保留。
- `candidate-review/temp-backup`：`AnnouncementMonitor.vue.backup`，暂不直接删除，后续单独进入 backup 文件治理批次。

本批次没有 `archive-approved` 页面。下一步若处理 `.backup`，应作为 mutation 批次执行：先给出 successor 为 `AnnouncementMonitor.vue` 的证据、确认无运行/文档回滚职责，再移动到受控 archive 区，而不是物理删除。
