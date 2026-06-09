# P3 Commits 分析与下一步工作建议

> **生成日期**: 2026-05-18
> **分析范围**: 5 个最新 commits（含 untracked 路由表扫描器修复）
> **git branch**: `wip/root-dirty-20260403`

---

## 一、Commits 总览

| # | Commit | 类型 | 说明 |
|---|--------|------|------|
| 1 | `5717635` | 治理/文档 | P3 进度报告 v2 + 跨线对齐文档（解决 6 项 Codex review findings） |
| 2 | `d582f77` | 基础设施 | CI 验证 dry run 稳定化 |
| 3 | `1d0abcf` | 基础设施 | CI 验证文档门禁收口 |
| 4 | `ecf9224` | 实现 | P3-D 删除 4 个真孤立 API 文件 + 7 个死代码测试（-3,352 行） |
| 5 | untracked | 工具改进 | 路由表扫描器 include_router 链追踪修复 + artifact 重新生成 |

---

## 二、逐 Commit 分析

### 2.1 5717635 — P3 进度报告 v2 + 跨线对齐

**做了什么**：

- 更新 P3 实现进度报告，吸收 Codex review 的 6 项 findings：
  - F1: 删除台账不完整（遗漏 `announcement.py`、`backup_recovery.py`、`technical/__init__.py` 等对象）
  - F2: OpenSpec governance evidence 不足（task checklist 0/31，缺少 approval 证据）
  - F3: `strategy_mgmt.py` 兼容行为描述不准确
  - F4: P3-C7 health/status `54` 路由计数不可复现
  - F5: 前端 quality gate 证据太粗糙
  - F6: 多处数字和措辞精度问题
- 完成**跨线对齐**：将 P3 实现线（router 收口、文件删除）与 OpenSpec 治理线（4 个 proposal、13 个候选 issue）之间的重叠做出显式对齐：
  - `openspec/changes/consolidate-backend-api-domain-routers/tasks.md`：标注 announcement/strategy/risk 决策已完成
  - `openspec/changes/consolidate-backend-health-endpoints/tasks.md`：标注 P3-A5 已提出 taxonomy
  - `openspec/changes/migrate-backend-singletons-to-lifecycle-di/tasks.md`：标注 P3-A4 已生成 inventory

**评价**：正确的治理动作。避免了两条线重复执行或互相覆盖。跨线对齐文档为后续执行提供了清晰的分工边界。

---

### 2.2 d582f77 + 1d0abcf — CI 验证文档门禁

**做了什么**：CI 验证 documentation gate 的 dry run 稳定化和最终收口。

**评价**：基础设施微调，不影响主逻辑。两个 commit 可以合并理解。

---

### 2.3 ecf9224 — P3-D 删除孤立文件 + 死代码测试

**做了什么**：

基于路由表扫描证据，执行机械清理：

- 4 个确认未注册且无 `include_router` 引用的 API 文件
- 7 个针对已删除功能的死代码测试
- 合计 **-3,352 行**

**评价**：

- 这是已验证的机械清理，不是随机删除。路由表扫描确认这些文件没有活跃消费者后执行。
- 符合 `architecture/STANDARDS.md` 的清理/删除判定标准。
- 建议在后续 commit 中附带一个删除台账（deletion ledger），记录每个删除对象的 functional node、状态判定、证据来源，便于审计闭环。

---

### 2.4 Untracked — 路由表扫描器 include_router 链追踪修复

**改了什么**：

在 `scripts/dev/backend_audit_fullpath_routes.py` 中新增了从 `router_registry.py` 注册文件出发的 **BFS include_router 链追踪**（第 333–401 行）。具体逻辑：

1. 从已注册文件集合出发，用 AST 解析每个文件中的 `router.include_router(xxx_router, ...)` 调用
2. 解析 import 语句，将 import name 映射到文件系统路径（支持相对 import 层级回退和绝对 import 点号转换）
3. BFS 遍历所有 reachable 文件，标记为非 orphan
4. 未通过任何链到达的文件才标记为 orphan

**修复效果**：

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| 孤立文件 | 8（全部假阳性） | 2（边缘情况） |
| 注册路由 | 522 | 522 |
| include_router 链可达 | 0（未追踪） | 16 |
| 有效路由 | 522 | 538 |
| 总计 | 558 | 558 |
| 剩余 20 条 | — | `get_monitoring_db.py`（strategy_management 聚合器下） |

**当前状态**：

- 扫描器代码已修改但**未 commit**
- 生成的 artifact（`docs/reports/quality/generated/backend-fullpath-route-table.json`）仍显示旧版数据（8 orphans、522 registered、36 orphan_routes）
- 需要重新运行扫描器生成新 artifact 后一并提交

**建议 commit**：
```
fix(audit): trace include_router chains in fullpath route scanner,
             reduce false orphan positives 8→2
```

---

## 三、当前整体状态

两条并行但有交集的线当前停在同一个点——**需要人工审批后才能真正进入实现**：

```
P3 实现线                          OpenSpec 治理线
├── P3-B: router 收口 ✓           ├── 4 个 proposal (C/E/F/G) ✓
├── P3-C: strategy/health 收敛     ├── 13 个候选 issue ✓
├── P3-D: 孤立文件删除 ✓           ├── approval packet ✓
├── 路由表扫描器增强 (untracked)    ├── issue 草稿包 ✓
└── P3-C1/C6/C7 待执行             ├── 跨 proposal orchestration ✓
        ↑                              ↑
   等待 OpenSpec approval        等待人工审批 gate
```

**跨线对齐已完成的收口**：

- announcement / strategy / risk canonical router 决策 → 标记为 `audit-only`（不再发布重复 issue）
- singleton lifecycle inventory → OpenSpec E change 直接复用
- health/status taxonomy → 已加入 P3-A5 提案引用

**Matt Pocock review 的关键结论**（参见 `backend-route-table-duplicate-routes-mattpocock-review-2026-05-18.md`）：

> 路由表扫描揭示的问题比 Phase 3 修订计划中的 P3-B/P3-C 颗粒度更严重。它不再只是"几个 flat/package 目录要收口"的问题，而是 API 路由契约缺少 single source of truth。

> 按 Matt Pocock `to-issues` 标准，这些问题目前不应直接拆成 `ready-for-agent` 修复单。

---

## 四、下一步建议（按优先级排序）

### 🔴 优先级 1：提交路由表扫描器修复 + 重新生成 artifact

**当前阻塞**：扫描器代码已改但未 commit，artifact 仍是旧数据。

**需要做的**：

1. 确认 `scripts/dev/backend_audit_fullpath_routes.py` 的 BFS include_router 链追踪代码已保存
2. 重新运行扫描器：
   ```bash
   cd web/backend && python3 ../../scripts/dev/backend_audit_fullpath_routes.py
   ```
3. 验证新 artifact：
   - `orphan_files` 从 8 → 2
   - `registered_routes` 应更新（522 → 538，通过链可达的 16 条不应计入 orphan）
4. 更新所有引用旧 route table 数字的文档（至少 `backend-openspec-line-summary-and-next-plan-2026-05-18.md`）
5. 一并 commit（扫描器代码 + 重新生成的 artifact + 文档更新）

**建议 commit message**：
```
fix(audit): trace include_router chains in fullpath route scanner

- BFS from registered files through include_router calls
- reduce orphan files from 8 (all false positives) to 2 (edge cases)
- 522 registered + 16 chain-reachable = 538 effective routes
- remaining 20 routes from get_monitoring_db.py under strategy_management
```

---

### 🟠 优先级 2：清理临时产物路径

**问题**：`web/backend/--output-dir/backend-audit-baseline.json` — 这个路径是一个 bug（`--output-dir` 命令行参数被当成目录名写入 active backend tree）。

**来源**：Matt Pocock review F6（`backend-route-table-duplicate-routes-mattpocock-review-2026-05-18.md` 第 125-137 行）

**建议**：
- 将产物迁移或重新生成到 `docs/reports/quality/generated/`
- 从 `web/backend/--output-dir/` 中删除旧文件
- 按 `architecture/STANDARDS.md` 临时产物治理规则处理
- 这个可以在优先 1 的 commit 中一并处理

---

### 🟡 优先级 3：推进 OpenSpec approval gate

**当前状态**：

- 4 个 OpenSpec proposal 已通过 `openspec validate --strict`：
  - `consolidate-backend-api-domain-routers` (C): 31 tasks, 0 checked
  - `consolidate-backend-health-endpoints` (G): 29 tasks, 0 checked
  - `migrate-backend-singletons-to-lifecycle-di` (E): 24 tasks, 0 checked
  - `split-backend-core-modules-with-compatibility-wrappers` (F): 24 tasks, 0 checked
- Approval packet: `backend-openspec-human-approval-packet-2026-05-18.md`
- Issue readiness blueprint: `backend-openspec-issue-readiness-blueprint-2026-05-18.md`
- 10 个 GitHub issue body 草稿已就绪，3 个标记为 audit-only

**需要做的**：

1. **人工审批** C/E/F/G 四个 proposal scope（参考 approval packet）
2. 审批通过后，发布 GitHub issues（已有 `gh issue create` 草稿命令）
3. 按以下顺序释放 `ready-for-agent` 候选：
   - Issue #2: Refresh shared route table and OpenAPI evidence
   - Issue #10: Build F Core import compatibility matrix
   - Issue #11: Build E singleton/getter lifecycle inventory
   - Issue #8: Build G health/status taxonomy（前提：不改 route，保持 evidence-only）

**执行顺序建议**（来自 orchestration 文档）：

```
approval/orchestration
  → route/OpenAPI evidence
  → C/G decisions
  → F import compatibility matrix
  → E singleton/getter inventory
  → E first pilot / F first low-risk split batch
```

---

### 🟢 优先级 4：P3-C 剩余项 — 补 domain-specific decision records

**当前阻塞**：P3-C1/C6/C7（strategy route 收敛、健康端点收敛）已被 route table audit 发现比预期更严重。

Matt Pocock review 明确建议：
- **暂停**创建 route 相关的 `ready-for-agent` issues
- 先产出 domain-specific decision records
- 每个域单独走 OpenSpec proposal

**需要补的决策项**：

| 域 | 问题 | 建议 decision |
|----|------|--------------|
| trading | `trading_runtime.py` vs `trading_monitor.py` 同路由重复 | P3-A6: trading canonical route owner |
| backup | `backup_recovery.py` vs `backup_recovery_secure/` 同路由 + 安全边界 | P3-A7: backup route owner + security boundary |
| health/status | 22 模块有 `GET /health`，13 模块有 `GET /status`，语义混乱 | P3-A5: health/status taxonomy（已在 G change 中覆盖） |

**当前 C change**（`consolidate-backend-api-domain-routers`）已覆盖 announcement/strategy/risk，trading 和 backup 被标记为 deferred。后续应：
- 创建 trading follow-up OpenSpec（已对应 issue #6）
- 创建 backup follow-up OpenSpec（已对应 issue #7）

---

### 🔵 优先级 5：`get_monitoring_db.py` 处置决策

**当前情况**：

- 文件路径：`web/backend/app/api/strategy_management/get_monitoring_db.py`
- 行数：1,584 行（含 20 条路由装饰器）
- 路由前缀：`/api/v1/strategy`（来自 `APIRouter(prefix="/api/v1/strategy")`）
- 路由表扫描状态：在 strategy_management 聚合器下贡献 20 条路由，当前被标记为 orphan edge case

**需要决策**：

1. 这个文件是否通过 strategy_management package 的 `include_router` 链可达？
   - 如果是：扫描器应进一步追踪 package 内 re-export 链
   - 如果不是：这 20 条路由是否应该被注册（或确实是 orphan）
2. 文件名 `get_monitoring_db.py` 与其他子模块命名风格不一致（其他为 `_strategy_execution_router.py`、`monitoring_adapter.py` 等），是否需要重命名统一？

**建议**：在优先 1（扫描器修复提交）之后，将其作为一个明确的 decision item 在 strategy domain governance 中处置。

---

## 五、风险评估

| 风险 | 级别 | 说明 |
|------|------|------|
| untracked 扫描器修复未提交 | 低 | 代码已在 working tree，不会丢失；但不 commit 则后续 AI session 可能无法感知改进 |
| route table 数字在文档中不一致 | 中 | artifact 显示 558/522/36/8，但改进后应是 558/538/20/2，引用旧数字的文档需同步更新 |
| OpenSpec approval 未推动 | 中 | 当前阻塞 P3-C 和 OpenSpec 线的所有实现工作 |
| trading/backup 域 deferred | 低 | 正确做法，但需确保有明确的 follow-up issue 不至于被遗忘 |
| `--output-dir/` 路径污染 | 低 | 不影响运行，但在下一次 backend 部署/扫描时可能触发困惑 |

---

## 六、建议的下一个 Session 启动顺序

**如果是 AI agent 继续执行**：

1. 第一件事：确认 `backend_audit_fullpath_routes.py` 的修改是否已保存为 commit
2. 如果未 commit → 执行优先 1（提交扫描器 + 重新生成 artifact）
3. 运行 `openspec validate --strict` 确认 4 个 proposal 仍有效
4. 根据优先 3 的状态，决定是继续 governance 工作还是进入实现

**如果是人工审核**：

1. 先审阅本文档
2. 重点审阅 `backend-openspec-human-approval-packet-2026-05-18.md`（approval gate）
3. 批准后标记 issue #1 为 resolved，释放后续 issue 执行

---

## 附录 A：关键文档索引

| 文档 | 用途 |
|------|------|
| `docs/reports/quality/backend-route-table-openapi-baseline-2026-05-18.md` | 路由表 baseline（664 decorators, 81 duplicate groups） |
| `docs/reports/quality/backend-route-table-duplicate-routes-mattpocock-review-2026-05-18.md` | Matt Pocock 风格 review，判定结论和 deepening opportunities |
| `docs/reports/quality/generated/backend-fullpath-route-table.md` | 展开后的 full-path route table（需重新生成） |
| `docs/reports/quality/backend-audit-P3-progress-report-review-2026-05-18.md` | Codex review（6 findings） |
| `docs/reports/quality/backend-openspec-line-summary-and-next-plan-2026-05-18.md` | OpenSpec 线阶段总结 |
| `docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md` | 人工审批入口 |
| `docs/reports/quality/backend-openspec-issue-readiness-blueprint-2026-05-18.md` | Issue 发布就绪蓝图 |
| `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md` | 跨 proposal 编排文档 |
| `docs/reports/quality/cross-line-alignment-P3-impl-openspec-2026-05-18.md` | P3 实现线与 OpenSpec 线的跨线对齐依据 |
| `docs/reports/quality/cross-line-alignment-P3-impl-openspec-response-2026-05-18.md` | 跨线对齐处理结果 |

## 附录 B：OpenSpec Changes 当前状态

| Change | 缩写 | 任务数 | 状态 |
|--------|------|-------|------|
| `consolidate-backend-api-domain-routers` | C | 31 | Valid, 0 checked |
| `consolidate-backend-health-endpoints` | G | 29 | Valid, 0 checked |
| `migrate-backend-singletons-to-lifecycle-di` | E | 24 | Valid, 0 checked |
| `split-backend-core-modules-with-compatibility-wrappers` | F | 24 | Valid, 0 checked |
