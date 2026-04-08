# Views Composables Status

> **使用说明**:
> 本文件用于补完 2026-04-07 Phase 3 结构审计中的 Batch B，专门记录 `web/frontend/src/views/composables/` 的文件级状态。
> 当前共享规则、迁移收口门禁与删除判定仍以 `architecture/STANDARDS.md` 为准；本文件不构成删除批准。

**Generated:** 2026-04-07  
**Branch observed:** `wip/root-dirty-20260403`

---

## 1. Scope

本次只回答三个问题：

1. `src/views/composables/*.ts` 目前主要服务谁
2. 哪些属于 root-level legacy page support
3. 哪些已经具备 `duplicate-candidate` 特征

---

## 2. Top-Level Conclusion

当前 `web/frontend/src/views/composables/` 不是“可直接迁移到 `src/composables/` 的普通工具目录”。

更准确的 repo-truth 是：

- 大多数文件仍直接服务 root-level legacy views
- 少量文件同时被测试守护
- 两组文件已经形成大体量分叉实现，不适合机械合并

当前最合理的目录级标签应为：

```text
root-level legacy view support + partial test guards + duplicate-candidates
```

---

## 3. File Status Table

| File | Primary Consumer | Evidence Summary | Current Judgment |
|---|---|---|---|
| `tradingDashboardActions.ts` | `useTradingDashboard.ts` | 由 `useTradingDashboard.ts` 调用；`__node_tests__/tradingDashboardActions.test.ts` 直接覆盖 | `support module + test-guarded` |
| `useAdvancedAnalysis.ts` | `src/views/AdvancedAnalysis.vue` | root-level 页面相对引用 | `legacy page support` |
| `useAnalysis.ts` | `src/views/Analysis.vue` | root-level 页面相对引用；`console-log-cleanup-batch-29.spec.ts` 直接读取源码 | `legacy page support + test-guarded` |
| `useBacktestWizard.ts` | `src/views/BacktestWizard.vue` | root-level 页面相对引用 | `legacy page support` |
| `useEnhancedDashboard.ts` | `src/views/EnhancedDashboard.vue` | root-level 页面相对引用 | `legacy page support` |
| `useIndustryConceptAnalysis.ts` | `src/views/IndustryConceptAnalysis.vue` | root-level 页面相对引用 | `legacy page support` |
| `usePhase4Dashboard.ts` | `src/views/Phase4Dashboard.vue` | root 版与 demo 版并存，且两份文件均为大体量实现 | `duplicate-candidate` |
| `usePortfolioManagement.ts` | `src/views/PortfolioManagement.vue` | root-level 页面相对引用 | `legacy page support` |
| `usePyprofilingDemo.ts` | `src/views/PyprofilingDemo.vue` | root-level demo shell 相对引用 | `legacy/demo support` |
| `useSettings.ts` | `src/views/Settings.vue` | root-level 页面相对引用 | `legacy page support` |
| `useTechnicalAnalysis.shortcuts.ts` | `useTechnicalAnalysis.ts` | 仅作为 legacy technical composable 的辅助模块 | `support module` |
| `useTechnicalAnalysis.ts` | `src/views/TechnicalAnalysis.vue` | root 版 technical 页面相对引用；与 `views/technical/` 版并存；有单独类型清理 spec | `duplicate-candidate + test-guarded` |
| `useTechnicalAnalysis.types.ts` | `useTechnicalAnalysis.ts` | 仅作为 legacy technical composable 的类型模块 | `support module` |
| `useTradingDashboard.ts` | `src/views/TradingDashboard.vue` | root-level 页面相对引用；存在 `__tests__/useTradingDashboard.spec.ts` | `legacy page support + test-guarded` |
| `usemonitor.ts` | `src/views/monitor.vue` | root-level legacy monitor 页面相对引用 | `legacy page support` |

---

## 4. Duplicate Candidates

### 4.1 `usePhase4Dashboard`

证据：

- `web/frontend/src/views/composables/usePhase4Dashboard.ts`: `380` 行
- `web/frontend/src/views/demo/composables/usePhase4Dashboard.ts`: `355` 行
- `src/views/Phase4Dashboard.vue` 使用 root 版
- `src/views/demo/Phase4Dashboard.vue` 使用 demo 版

当前判断：

- 这不是“同文件被不同页面复用”
- 也不是“薄 wrapper + canonical body”
- 而是 `历史 root 页面实现` 与 `demo 页面实现` 的并存

当前标签：

- `duplicate-candidate`

后续治理重点：

- 先判断 root `Phase4Dashboard` 是否仍需作为历史页面保留
- 再决定 demo 版是否是唯一应继续存在的展示资产

### 4.2 `useTechnicalAnalysis`

证据：

- `web/frontend/src/views/composables/useTechnicalAnalysis.ts`: `441` 行
- `web/frontend/src/views/technical/composables/useTechnicalAnalysis.ts`: `485` 行
- `src/views/TechnicalAnalysis.vue` 使用 root legacy 版
- `src/views/technical/TechnicalAnalysis.vue` 使用 technical 子目录版
- `web/frontend/tests/unit/config/use-technical-analysis-types-cleanup.spec.ts:5-14` 守护 root legacy 版
- `web/frontend/tests/unit/config/console-log-cleanup-batch-23.spec.ts:5-10` 守护 `views/technical/` 版

当前判断：

- 两份 composable 都不是简单兼容导出
- 两套 technical 页面实现仍被分开持有
- 当前主路由却已经改走 `src/views/market/Technical.vue`

当前标签：

- `duplicate-candidate`

后续治理重点：

- 先做功能树判定
- 再决定 root 版保留、`views/technical/` 版保留，还是两者一起退场

---

## 5. Support Modules

当前有 4 个文件不应被当作“独立业务 composable”处理：

- `tradingDashboardActions.ts`
- `useTechnicalAnalysis.shortcuts.ts`
- `useTechnicalAnalysis.types.ts`
- `useTechnicalAnalysis.types.ts` 的上游 `useTechnicalAnalysis.ts`

其中需要特别注意：

- `tradingDashboardActions.ts` 不是页面入口，而是 `useTradingDashboard.ts` 的支撑动作模块
- `useTechnicalAnalysis.shortcuts.ts` 与 `useTechnicalAnalysis.types.ts` 都只是 root legacy technical composable 的子模块

这类文件的治理前提不是目录搬迁，而是先确定其上游页面/主 composable 的命运。

---

## 6. Current Exit Conditions

在对 `views/composables/` 做任何移动、归档或删除前，至少应满足：

1. 每个文件都完成主消费者确认
2. 每个文件都完成功能树状态标签
3. 两组 duplicate-candidate 都完成保留理由或退场条件判定
4. root-level legacy pages 的路由资产状态已经收口

当前尚未满足的关键条件：

- `usePhase4Dashboard.ts` 所属的 root `Phase4Dashboard` 仍在历史资产判定链上
- `useTechnicalAnalysis.ts` 所属的 root `TechnicalAnalysis` 仍在历史 technical 页面判定链上
- `usemonitor.ts` 所属的 `monitor.vue` 仍属于 root-level legacy 页面

因此，当前不适合直接做：

- 目录整体迁移
- 机械 rename
- “搜不到现役 domain route import 就删”

---

## 7. Recommended Next Step

在 Batch B 之后，最自然的下一步是 Batch C：

1. 给 `Phase4Dashboard` root/demo 双分叉写出保留理由与退场条件
2. 给 `TechnicalAnalysis` root/technical 双分叉写出保留理由与退场条件
3. 把 duplicate-candidate judgement 与历史路由资产状态对齐

---

## 8. Evidence

本次报告主要基于以下证据：

```bash
find web/frontend/src/views/composables -maxdepth 1 -type f -name '*.ts' | sort
for f in web/frontend/src/views/composables/*.ts; do bn=$(basename "$f" .ts); echo "--- $bn"; rg -n --no-messages "$bn" web/frontend/src/views web/frontend/tests/unit/config -g '*.vue' -g '*.ts' -g '*.spec.ts'; done
wc -l web/frontend/src/views/composables/*.ts web/frontend/src/views/demo/composables/*.ts web/frontend/src/views/technical/composables/*.ts
nl -ba web/frontend/tests/unit/config/use-technical-analysis-types-cleanup.spec.ts | sed -n '1,220p'
nl -ba web/frontend/tests/unit/config/console-log-cleanup-batch-23.spec.ts | sed -n '1,220p'
```

---

## 9. References

- `architecture/STANDARDS.md`
- `docs/reports/2026-04-07-frontend-structure-repo-truth-audit.md`
- `docs/reports/2026-04-07-phase3-execution-preconditions.md`
- `docs/reports/2026-04-07-legacy-router-asset-status.md`
- `web/frontend/src/views/composables/`
- `web/frontend/src/views/demo/composables/usePhase4Dashboard.ts`
- `web/frontend/src/views/technical/composables/useTechnicalAnalysis.ts`
