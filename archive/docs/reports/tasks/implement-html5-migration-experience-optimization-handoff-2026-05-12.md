# implement-html5-migration-experience-optimization 交接文档

> **历史文档说明**:
> 本文件是历史快照、阶段总结和后续交接材料，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、当前 OpenSpec change、当前代码与最近一次实际验证结果为准。

> **交接目的**:
> 本文档面向后续接手 `implement-html5-migration-experience-optimization` 的执行者。
> 它不替代 OpenSpec、运行时代码或真实验收记录；当前任务状态仍以 `openspec/changes/implement-html5-migration-experience-optimization/tasks.md` 和实际执行结果为准。

**最后更新**: 2026-05-12
**对应 OpenSpec change**: `implement-html5-migration-experience-optimization`
**当前进度**: `openspec list` 显示 `63/111 tasks`

---

## 1. 当前状态概览

这条线当前处于 **repo-local 文档和部分技术验证已收口，但完整能力与外部验收未完成** 的混合状态。

当前已经明确的边界：

- 产品范围固定为 **Desktop-only**
- 菜单事实为 `MenuConfig.ts` 的 7 个业务域，不是原始 proposal 中的 6 域
- `proposal.md` 和 `design.md` 保留历史目标，不能直接读取为当前实现状态
- `tasks.md`、change-wide ledger、section ledgers 和 success-metrics audit 是当前阅读入口
- 文档-only 工作已经足够支撑 reader routing；后续不能再通过补文字关闭需要真实实现或真实验收的开放项

---

## 2. 已完成事实

截至 2026-05-12，下面这些 repo-local 事实已经成立：

- `openspec validate implement-html5-migration-experience-optimization --strict` 通过
- `git diff --check` 对本批文档范围通过
- Phase 1 / 2 / 3 均已补齐总账型 ledger
- Success Metrics 已补齐混合状态审计
- Change-wide ledger 已补齐，作为当前 change 的总阅读入口
- Desktop-only 去作用域边界已经写入 tasks 与相关审计
- 当前未勾选任务没有被文档补写伪闭合

关键真相源：

- [tasks.md](/opt/claude/mystocks_spec/openspec/changes/implement-html5-migration-experience-optimization/tasks.md)
- [proposal.md](/opt/claude/mystocks_spec/openspec/changes/implement-html5-migration-experience-optimization/proposal.md)
- [design.md](/opt/claude/mystocks_spec/openspec/changes/implement-html5-migration-experience-optimization/design.md)
- [html5-migration-change-wide-ledger-audit-2026-05-12.md](/opt/claude/mystocks_spec/docs/reports/quality/html5-migration-change-wide-ledger-audit-2026-05-12.md)
- [html5-migration-section1-total-ledger-audit-2026-05-12.md](/opt/claude/mystocks_spec/docs/reports/quality/html5-migration-section1-total-ledger-audit-2026-05-12.md)
- [html5-migration-section2-total-ledger-audit-2026-05-12.md](/opt/claude/mystocks_spec/docs/reports/quality/html5-migration-section2-total-ledger-audit-2026-05-12.md)
- [html5-migration-section3-total-ledger-audit-2026-05-12.md](/opt/claude/mystocks_spec/docs/reports/quality/html5-migration-section3-total-ledger-audit-2026-05-12.md)
- [html5-migration-success-metrics-audit-2026-05-12.md](/opt/claude/mystocks_spec/docs/reports/quality/html5-migration-success-metrics-audit-2026-05-12.md)
- [html5-migration-evidence-index-2026-05-12.md](/opt/claude/mystocks_spec/docs/reports/quality/html5-migration-evidence-index-2026-05-12.md)

---

## 3. 剩余开放项分类

### 3.1 需要真实实现或审批的开放项

- `vite-plugin-pwa` active build process 启用
- Background sync 的客户端注册与失败请求入队链路
- Push permission / subscription backend / alert integration / settings UI
- Worker K 线处理主链路和 worker lifecycle / error recovery
- Web Vitals、cache-hit、PWA usage、RUM、performance dashboard
- Bundle target、依赖清理、运行时性能优化等仍未达成项

### 3.2 需要真实浏览器验收的开放项

- 11 条桌面路由 PWA 离线矩阵
- Cross-browser PWA 验收
- Worker 性能提升量化
- Accessibility ARIA / keyboard / screen-reader / WAVE + axe 全域验收

### 3.3 需要外部流程或执行记录的开放项

- 渐进式部署策略执行
- 回滚演练和监控告警闭环
- 团队培训和技术分享执行记录
- Success Metrics 中的 UX / business impact / post-launch 指标

---

## 4. 当前环境约束

接手前必须知道：

1. 当前工作树很脏，且包含其他条线和其他 agent 的变更。不要回滚无关文件。

2. 本条线近期批次是 docs-only，不涉及代码符号修改，因此没有为本批次运行 GitNexus symbol impact。

3. 若后续要编辑函数、类、方法或前端运行时代码，必须先按 GitNexus 规则做 impact analysis。

4. 若后续要关闭未勾选实现项，必须拿到真实实现与验证结果，不能继续通过补文档收口。

5. 若后续仅允许 repo-local docs-only 工作，合理范围只剩 reader-routing、handoff、final evidence index；不要继续 leaf-by-leaf 改写历史文档。

---

## 5. 推荐下一步

### 路径 A: 继续 docs-only

只允许做下面几类：

- 更新 reader routing
- 补最终 evidence index
- 汇总 handoff / closeout
- 检查并修复明显断链

不建议再逐项补新的免责声明，因为 section ledger 和 change-wide ledger 已经足够表达当前状态。

### 路径 B: 进入真实验收

优先顺序：

1. 建立稳定的 service-worker-controlled offline route matrix harness
2. 跑 11 条 Desktop route 离线矩阵
3. 跑 cross-browser PWA 验收
4. 明确 worker orchestration 是否进入审批实现
5. 重新测量 bundle / Lighthouse / coverage / Web Vitals 目标

### 路径 C: 进入实现工作

必须先做审批和 impact：

- Worker orchestration
- Push subscription backend
- PWA plugin enablement
- Performance dashboard / telemetry
- Dependency removal / retained assets cleanup

---

## 6. 现场命令入口

```bash
openspec validate implement-html5-migration-experience-optimization --strict
openspec list | rg "implement-html5-migration-experience-optimization"
git diff --check -- openspec/changes/implement-html5-migration-experience-optimization/tasks.md docs/reports/quality/html5-migration-*.md docs/reports/tasks/implement-html5-migration-experience-optimization-handoff-2026-05-12.md
```

如果进入前端运行验收，再按具体任务选择 Playwright / Lighthouse / build 命令，并记录实际项目、浏览器、通过/失败/跳过数量。
