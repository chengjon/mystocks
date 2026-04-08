# Phase 3-4 Execution Matrix

> **使用说明**:
> 本文件把 2026-04-07 的前端结构审计结论转换成可执行批次矩阵，供后续 Phase 3 / Phase 4 实施时直接引用。
> 当前共享规则、审批门禁、删除判定与迁移收口口径仍以 `architecture/STANDARDS.md` 为准；本文件不是删除批准，也不替代用户审批。

**Generated:** 2026-04-07  
**Branch observed:** `wip/root-dirty-20260403`

---

## 1. Purpose

本矩阵只做两件事：

1. 把现有审计报告收束成一条最小风险执行顺序
2. 明确每一批次的前置条件、禁止动作、完成标志

目标是避免后续执行时再次出现：

- 把历史资产误当现役真相
- 把测试守护对象误当可删死代码
- 在审批前先做结构性清理

---

## 2. Locked Inputs

本矩阵基于以下已锁定事实：

1. 前端现役入口：

```text
web/frontend/index.html -> /src/main-standard.ts -> /src/router/index.ts
```

2. 当前 technical canonical page：

```text
src/views/market/Technical.vue
```

3. 历史路由资产状态：

- `src/router/index.js` = `historical legacy router asset`
- `src/router/index.js.clean` = `historical broken backup / stale working copy`
- `src/router/index.js.backup-phase2.3` = `historical backup`
- `src/router/phase4.routes.js` = `stale route asset`

4. `views/composables/` 当前目录级判断：

```text
root-level legacy view support + partial test guards + duplicate-candidates
```

5. `views/monitoring/` 当前目录级判断：

```text
historical router targets + test-guarded monitoring assets
```

---

## 3. Execution Order

建议执行顺序固定为 6 个批次：

1. Batch E1: 入口变体 caller 分类
2. Batch E2: 历史路由文件归档策略
3. Batch E3: monitoring 页面目标退场条件对齐
4. Batch E4: duplicate page 退场条件对齐
5. Batch E5: case-conflict directory merge
6. Batch E6: 命名 / shim / 备份文件收尾

这里的核心原则是：

- 先补治理边界
- 再做结构迁移
- 最后才考虑归档或删除

---

## 4. Batch Matrix

| Batch | Scope | Primary Goal | Approval Need | Blockers | Output |
|---|---|---|---|---|---|
| E1 | `main-*.js/ts`, `verify-mount.js` | 明确哪些入口变体仍有 caller | 文档可先做；结构改动需审批 | `main.js` 仍被 `verify-mount.js` 读取 | 入口变体 caller matrix |
| E2 | `router/index.js*`, `phase4.routes.js` | 把历史路由资产从“疑似真相”降级为“可归档对象/历史说明对象” | 若移动/删除需审批 | 文档、脚本、历史报告仍频繁引用 `index.js` | 路由归档策略说明 |
| E3 | `views/monitoring/*` | 对齐历史路由目标、Vitest、Playwright 的退场条件 | 若动目录/测试需审批 | `/monitoring/*` 相关 Playwright 与 config spec 仍存在 | monitoring retirement checklist |
| E4 | `Phase4Dashboard` / `TechnicalAnalysis` | 对齐 root/demo/fork/canonical 四类角色 | 若删页面/改路由需审批 | 多组 spec 仍直接守护 | duplicate retirement checklist |
| E5 | `src/components/` case-conflict dirs | 解决大小写目录冲突 | 需要审批后实施 | 这是真实代码改动，且可能影响构建 | import inventory + merge plan |
| E6 | `*.bak`, `*_new.py`, root shims, naming cleanup | 做最终收尾 | 需要审批后实施 | 必须等前面结构收口完成 | naming/shim closure plan |

---

## 5. Per-Batch Guidance

### 5.1 Batch E1: Entry Variant Caller Matrix

范围：

- `web/frontend/src/main.js`
- `web/frontend/src/main-standard.ts`
- 其余 `main-*` 变体
- `web/frontend/verify-mount.js`

必须先做：

- 逐个确认 HTML / script / test / tooling caller
- 区分：
  - runtime truth
  - tooling consumer
  - historical debug entry

禁止动作：

- 在 `verify-mount.js` 未收口前删除 `main.js`
- 在 caller 未盘清前批量归档 `main-*`

完成标志：

- 每个入口变体都有 caller 状态标签
- 可以明确分出“可归档”与“必须保留”

### 5.2 Batch E2: Legacy Router Archive Strategy

范围：

- `src/router/index.js`
- `src/router/index.js.clean`
- `src/router/index.js.backup-phase2.3`
- `src/router/phase4.routes.js`

必须先做：

- 确认文档层是否仍把这些文件当现役真相
- 确认是否要保留其中一份作为历史说明样本

禁止动作：

- 直接删 `index.js`
- 把 `index.js.clean` 当作可靠模板继续引用

完成标志：

- 每个文件都有明确归档策略：
  - 保留为历史说明
  - 保留为备份
  - 可归档候选

### 5.3 Batch E3: Monitoring Retirement Alignment

范围：

- `views/monitoring/*`
- `monitoring-*.spec.ts`
- monitoring Playwright specs

必须先做：

- 对齐：
  - 历史 `/monitoring/*` 路由
  - Vitest config 守护
  - Playwright 页面验证

禁止动作：

- 只因 `router/index.ts` 无引用就删目录
- 跳过 Playwright / Vitest 守护直接做目录归档

完成标志：

- `WatchlistManagement.vue` / `RiskDashboard.vue` 的历史路由角色写清
- `AlertRulesManagement.vue` / `MonitoringDashboard.vue` 的测试守护角色写清
- 形成具体退场清单

### 5.4 Batch E4: Duplicate Page Retirement Alignment

范围：

- `Phase4Dashboard` root/demo
- `TechnicalAnalysis` root/technical/market

必须先做：

- 对齐：
  - route asset judgement
  - composable judgement
  - page-level spec guards

禁止动作：

- 把双分叉当普通 rename
- 在 spec 未治理前删 root/demo/fork 页面

完成标志：

- 每个对象都有：
  - 保留理由
  - 退场条件
  - 对应 spec 清单

### 5.5 Batch E5: Case-Conflict Directory Merge

范围：

- `src/components/` 大小写冲突目录

必须先做：

- 全量 import inventory
- 先产出 merge plan，再改代码

禁止动作：

- 在 import inventory 不完整时直接改目录名

完成标志：

- 形成可执行 merge plan
- 明确验证命令：
  - `npm run build`
  - `stylelint`
  - 必要时 E2E smoke

### 5.6 Batch E6: Naming / Shim / Backup Closure

范围：

- root shims
- `*.bak` / `*.backup`
- `*_new.py`
- 机械拆分类文件

必须先做：

- 依赖前面批次已经完成 canonical truth 收口

禁止动作：

- 在功能树状态不明时删 shim / backup
- 把“无引用”直接等同于“可删除”

完成标志：

- 每类对象都完成：
  - keep / deprecate / remove
  - 迁移前提
  - 验证命令

---

## 6. Approval Gates

按 `architecture/STANDARDS.md`，以下动作都不应在未审批时启动：

- 路由结构调整
- 目录收敛
- 页面归档或删除
- 兼容层下线
- case-conflict 目录合并

因此当前最稳妥的口径是：

- 文档审计与执行矩阵：可以继续
- 任何真实结构性改动：需要用户明确批准后再进实施批次

---

## 7. Minimum Safe Start Point

如果下一轮要真正开始实施，最安全的起点不是删文件，而是：

1. 先做 Batch E1
2. 再做 Batch E2/E3/E4 的“退场条件对齐”
3. 等这些边界都清楚后，再进入 E5/E6 的真实改动

换句话说，当前最接近“可直接执行”的不是删除任务，而是：

```text
入口 caller 盘点 -> 历史/测试资产退场条件对齐 -> 再进入目录/文件收口
```

---

## 8. Verification Notes

本文件是文档汇总，不代表已重新运行验证命令。

当前状态：

- 本轮未执行前端构建
- 本轮未执行类型检查
- 本轮未执行 E2E
- 本轮未修改业务代码

因此这里的“完成标志”是治理条件，不是已完成验证事实。

---

## 9. Source Reports

本矩阵主要汇总自：

- `docs/reports/2026-04-07-project-status-and-tech-debt-priorities.md`
- `docs/reports/2026-04-07-frontend-structure-repo-truth-audit.md`
- `docs/reports/2026-04-07-phase3-execution-preconditions.md`
- `docs/reports/2026-04-07-legacy-router-asset-status.md`
- `docs/reports/2026-04-07-monitoring-functional-status.md`
- `docs/reports/2026-04-07-views-composables-status.md`
- `docs/reports/2026-04-07-duplicate-page-functional-status.md`

---

## 10. References

- `architecture/STANDARDS.md`
- `.planning/ROADMAP.md`
- `docs/reports/2026-04-07-project-status-and-tech-debt-priorities.md`
- `docs/reports/2026-04-07-frontend-structure-repo-truth-audit.md`
- `docs/reports/2026-04-07-phase3-execution-preconditions.md`
- `docs/reports/2026-04-07-legacy-router-asset-status.md`
- `docs/reports/2026-04-07-monitoring-functional-status.md`
- `docs/reports/2026-04-07-views-composables-status.md`
- `docs/reports/2026-04-07-duplicate-page-functional-status.md`
