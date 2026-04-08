# Legacy Router Asset Status

> **使用说明**:
> 本文件用于补完 2026-04-07 Phase 3 前端结构审计中的 Batch A，专门判定历史路由资产状态。
> 当前共享规则、删除门禁与迁移收口口径仍以 `architecture/STANDARDS.md` 为准；本文件只提供 repo-truth 分类，不构成删除批准。

**Generated:** 2026-04-07  
**Branch observed:** `wip/root-dirty-20260403`

---

## 1. Scope

本次只判断以下 4 个历史路由文件当前属于什么状态：

- `web/frontend/src/router/index.js`
- `web/frontend/src/router/index.js.clean`
- `web/frontend/src/router/index.js.backup-phase2.3`
- `web/frontend/src/router/phase4.routes.js`

目标不是立即删除，而是先给出后续批次可以直接引用的状态标签：

- `current truth`
- `historical backup`
- `stale route asset`
- `test-guarded artifact`

---

## 2. Locked Runtime Truth

当前前端运行链已可明确锁定为：

```text
web/frontend/index.html -> /src/main-standard.ts -> /src/router/index.ts
```

关键证据：

- `web/frontend/src/router/index.ts:22-240` 是当前现役路由定义
- `web/frontend/src/router/index.ts:49-52` 把 technical canonical page 指向 `@/views/market/Technical.vue`
- `web/frontend/tests/unit/config/market-route-canonical-paths.spec.ts:5-18` 直接守护 `src/router/index.ts`
- `web/frontend/tests/unit/config/domain-body-migration-ownership.spec.ts:20-28` 直接把 `src/views/market/Technical.vue` 约束为 canonical page body

因此，下面 4 个文件都不是当前 runtime truth。

---

## 3. Status Table

| File | Current Status | Key Evidence | Current Judgment |
|---|---|---|---|
| `src/router/index.js` | 不在当前 HTML -> runtime 主链中，但仍保存一整套旧版路由结构 | `index.ts` 已取代其成为现役真相；`index.js:71-74` 仍指向 root `TechnicalAnalysis.vue`；`index.js:288-294` 仍指向 `views/monitoring/*`；大量历史文档仍把它写成“路由配置” | `historical legacy router asset` |
| `src/router/index.js.clean` | 不是现役路由，且文件本身存在结构损坏 | `index.js.clean:153-169` 出现重复嵌套对象，已不是可靠可运行路由文件 | `historical broken backup / stale working copy` |
| `src/router/index.js.backup-phase2.3` | 明确备份文件 | 文件名自带 `backup-phase2.3`；内容与旧版 `index.js` 同型；仍保留 root `TechnicalAnalysis.vue` 与旧 monitoring 路径 | `historical backup` |
| `src/router/phase4.routes.js` | 独立旧路由残留，未接入当前主链 | `phase4.routes.js:7-30` 仅导出 2 条 Phase 4 路由；当前未发现任何现役路由聚合导入；`phase4.routes.js:19-21` 仍引用缺失的 `StrategyMgmtPhase4.vue` | `stale route asset` |

---

## 4. File-by-File Notes

### 4.1 `src/router/index.js`

当前判定：

- 不是现役 runtime truth
- 也不能简化写成“纯死文件”
- 更准确地说，它是 `历史 legacy router 资产`

证据：

- `web/frontend/src/router/index.ts:22-240` 已承接现役路由职责
- `web/frontend/src/router/index.js:71-74` 仍把 `/technical` 指向 `@/views/TechnicalAnalysis.vue`
- `web/frontend/src/router/index.js:236-294` 仍保留旧版 risk/monitoring 路由结构，其中：
  - `@/views/announcement/AnnouncementMonitor.vue`
  - `@/views/monitoring/WatchlistManagement.vue`
  - `@/views/monitoring/RiskDashboard.vue`
- `web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts:11-16`
- `web/frontend/tests/unit/config/monitoring-style-sources.spec.ts:11-14`
- `web/frontend/tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts:11-14`

这些监控类页面虽已不在 `index.ts` 主链中，但仍被测试和历史路由形态共同保留。

附加观察：

- 仓库内仍有大量历史文档把 `src/router/index.js` 记录为“路由配置”
- 这说明它在文档层仍是高频历史真相源，直接删除会扩大“文档真相落后于运行真相”的偏差

当前建议标签：

- `historical legacy router asset`

退场条件：

- 必须先完成历史文档去真相化
- 必须先确认 `views/monitoring/*` 的功能树状态与测试守护策略
- 必须先确认不存在任何脚本/构建/人工流程仍要求查看该文件

### 4.2 `src/router/index.js.clean`

当前判定：

- 不是当前真相
- 也不是可继续信赖的“干净备份”
- 更接近 `损坏的历史工作副本`

关键证据：

- `web/frontend/src/router/index.js.clean:153-169` 出现重复插入的对象片段：
  - `smart-data-test` 路由对象被打断
  - `artdeco-test` 对象被重复嵌入
  - 语法结构已经失衡

这意味着：

- 即便只作为参考，它也不是一个稳定、可运行、可迁移的历史路由样本
- 后续若做归档，优先级应高于 `index.js` 与 `index.js.backup-phase2.3`

当前建议标签：

- `historical broken backup / stale working copy`

退场条件：

- 只需确认没有测试、脚本或人工流程把它当成有效模板
- 确认后可进入“归档候选”而非“主路由治理对象”

### 4.3 `src/router/index.js.backup-phase2.3`

当前判定：

- 这是最明确的一份 `historical backup`

关键证据：

- 文件名直接包含 `backup-phase2.3`
- `web/frontend/src/router/index.js.backup-phase2.3:67-70` 仍将 technical 页面指向 root `TechnicalAnalysis.vue`
- `web/frontend/src/router/index.js.backup-phase2.3:232-240` 及后续仍保留旧 risk/monitoring 路由形态
- `docs/reports/PHASE2_MENU_REFACTORING_COMPLETION_REPORT.md` 仍把它明确记录为备份文件

当前建议标签：

- `historical backup`

退场条件：

- 若后续决定不再保留备份文件，先把与 Phase 2 菜单改造相关的文档证据收拢
- 然后与 `index.js` 一起做“历史路由资产归档”，而不是单独先删

### 4.4 `src/router/phase4.routes.js`

当前判定：

- 这是当前最明确的 `stale route asset`

关键证据：

- `web/frontend/src/router/phase4.routes.js:7-30` 只定义两条独立 Phase 4 路由
- 本次未发现 `index.ts`、`index.js` 或其他现役路由聚合文件导入它
- `web/frontend/src/router/phase4.routes.js:19-21` 仍引用不存在的 `@/views/StrategyMgmtPhase4.vue`
- `test -f web/frontend/src/views/StrategyMgmtPhase4.vue` 结果为 `missing`
- 仓库内对 `StrategyMgmtPhase4` 的可见证据只剩旧报告和该路由文件本身

这说明：

- 它既不是当前主链
- 也不是测试守护对象
- 更像“曾计划接入但未完成闭环的旧路由残留”

当前建议标签：

- `stale route asset`

退场条件：

- 先补一条文档说明：它为何退出主链、缺失页面对其可运行性的影响
- 若后续无人继续使用 Phase 4 root 页面资产，可把它与 root `Phase4Dashboard` 一起纳入历史资产归档评估

---

## 5. Cross-Cutting Conclusions

### 5.1 当前没有发现“仍受测试直接守护”的历史路由文件

本次在 `web/frontend/tests` 范围内未发现测试直接读取：

- `src/router/index.js`
- `src/router/index.js.clean`
- `src/router/index.js.backup-phase2.3`
- `src/router/phase4.routes.js`

因此它们当前更像：

- `历史路由资产`
- `历史备份`
- `过期残留路由文件`

而不是：

- `测试守护资产`

### 5.2 但它们对应的页面目标仍可能被测试守护

尤其是：

- `views/monitoring/*` 仍被多组 Vitest config spec 直接读取
- `src/views/Phase4Dashboard.vue` 与 `src/views/demo/Phase4Dashboard.vue` 仍被 `root-demo-style-entrypoints.spec.ts` 守护
- `src/views/technical/TechnicalAnalysis.vue` 仍被 `technical-web3-style-support.spec.ts` 守护

因此后续治理顺序必须是：

1. 先判定路由文件本身状态
2. 再判定其页面目标的功能树状态
3. 最后才讨论归档或删除

---

## 6. Recommended Use In Phase 3

对 Batch A，当前可直接落地的执行口径是：

1. `index.ts` 继续作为唯一当前路由真相源
2. `index.js` 记为 `historical legacy router asset`
3. `index.js.backup-phase2.3` 记为 `historical backup`
4. `index.js.clean` 记为 `historical broken backup / stale working copy`
5. `phase4.routes.js` 记为 `stale route asset`

这意味着下一批次不应该再问“它们是不是当前路由入口”，而应该只问：

- 哪些要补历史说明
- 哪些要归档
- 哪些仍牵连页面资产判定

---

## 7. Evidence

本次报告主要基于以下证据：

```bash
nl -ba web/frontend/src/router/index.ts | sed -n '1,240p'
nl -ba web/frontend/src/router/index.js | sed -n '1,240p'
nl -ba web/frontend/src/router/index.js.clean | sed -n '1,220p'
nl -ba web/frontend/src/router/index.js.backup-phase2.3 | sed -n '1,240p'
nl -ba web/frontend/src/router/phase4.routes.js | sed -n '1,220p'
nl -ba web/frontend/verify-mount.js | sed -n '1,120p'
nl -ba web/frontend/tests/unit/config/market-route-canonical-paths.spec.ts | sed -n '1,220p'
nl -ba web/frontend/tests/unit/config/domain-body-migration-ownership.spec.ts | sed -n '1,220p'
nl -ba web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts | sed -n '1,220p'
nl -ba web/frontend/tests/unit/config/technical-web3-style-support.spec.ts | sed -n '1,220p'
nl -ba web/frontend/tests/unit/config/monitoring-style-sources.spec.ts | sed -n '1,220p'
nl -ba web/frontend/tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts | sed -n '1,220p'
nl -ba web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts | sed -n '1,220p'
rg -n --no-messages "phase4\.routes\.js|router/index\.js(\.clean|\.backup-phase2\.3)?" web/frontend/tests web/frontend/src docs .planning -g '*.spec.ts' -g '*.ts' -g '*.js' -g '*.md'
rg -n --no-messages "StrategyMgmtPhase4" web/frontend/src web/frontend/tests docs .planning -g '*.ts' -g '*.js' -g '*.vue' -g '*.md'
test -f web/frontend/src/views/StrategyMgmtPhase4.vue && echo exists || echo missing
```

---

## 8. References

- `architecture/STANDARDS.md`
- `.planning/ROADMAP.md`
- `docs/reports/2026-04-07-frontend-structure-repo-truth-audit.md`
- `docs/reports/2026-04-07-phase3-execution-preconditions.md`
- `web/frontend/src/router/index.ts`
- `web/frontend/src/router/index.js`
- `web/frontend/src/router/index.js.clean`
- `web/frontend/src/router/index.js.backup-phase2.3`
- `web/frontend/src/router/phase4.routes.js`
- `web/frontend/tests/unit/config/market-route-canonical-paths.spec.ts`
- `web/frontend/tests/unit/config/domain-body-migration-ownership.spec.ts`
