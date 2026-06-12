# 工作区清理方案

> **日期**: 2026-05-14
> **分支**: `wip/root-dirty-20260403`
> **目标**: 将 1039 个未提交变更整理为有意义的原子提交，使工作区变干净，为后续架构治理铺路

---

## 一、现状概览

| 类型 | 数量 | 说明 |
|------|------|------|
| 已修改（未暂存） | 500 | 跨 web/docs/tests/src 等 |
| 未跟踪 | 425 | 大量新增文件 |
| 已删除（未暂存） | 109 | 主要是 openspec 变更 |
| 已暂存 | 5 | 混合（治理文档 + 代码） |
| **合计** | **1039** | 净变化 +22062 / -41404 行 |

### 按目录分布

| 目录 | 已修改 | 未跟踪 | 已删除 |
|------|--------|--------|--------|
| web/ | 287 | 76 | 28 |
| docs/ | 53 | 193 | 1 |
| tests/ | 72 | 11 | 2 |
| .claude/ | 11 | 64 | — |
| src/ | 32 | 1 | — |
| openspec/ | 11 | 16 | 76 |
| scripts/ | 10 | 17 | 1 |
| reports/ | 6 | 38 | — |
| 其他根文件 | ~18 | ~9 | 1 |

### 关键发现

1. **嵌套 `.claude/` 目录泛滥**: 至少 20+ 个子目录下有 Claude Code 自动生成的 `.claude/` 目录（如 `web/backend/.claude/`、`scripts/dev/a-stock-backtest/.claude/`），全部未跟踪
2. **治理文档重复链**: `reports/governance/` 中存在大量链式审阅文件（如 `*-review-review.md`、`*-disposition-review-disposition.md`），属于过程产物
3. **109 个已删除文件**: 主要是 `openspec/changes/` 下的已完成/废弃变更提案，已从磁盘删除但未暂存
4. **5 个已暂存文件**: 混合了治理文档和代码变更，应拆分

---

## 二、清理策略

### 原则

- **先减后加**: 先清理垃圾、确认删除，再做有价值的提交
- **按关注点分批**: 同一主题的变更归入同一提交
- **不丢数据**: 所有有价值的变更都保留，只清理明确的垃圾
- **每批可独立回滚**: 保持提交粒度合理

### 执行顺序

```
批次 0: .gitignore 补丁 + 垃圾清理
   ↓
批次 1: 确认删除（109 个已删除文件）
   ↓
批次 2: 治理文档
   ↓
批次 3: 配置与基础设施
   ↓
批次 4: 文档更新
   ↓
批次 5: 代码变更（src + tests）
   ↓
批次 6: 前端与后端代码（web/）
```

---

## 三、分批详情

### 批次 0: 垃圾清理 + .gitignore 补丁

**目标**: 消除噪音，防止垃圾再生

**操作**:

1. 在 `.gitignore` 添加规则排除嵌套 `.claude/` 目录:
   ```
   # Claude Code auto-generated (project root .claude/ is tracked)
   /*/.claude/
   /*/*/.claude/
   /*/*/*/.claude/
   ```

2. 删除 `reports/governance/` 中的重复链式文件（约 15-20 个），保留最终版本:
   - `2026-05-04-tech-debt-audit-review-review.md` → 删除（保留 `review.md`）
   - `2026-05-04-tech-debt-audit-review-disposition-review-disposition.md` → 删除
   - 同类模式的链式文件全部清理

3. 清理 `web/backend/web/backend/.claude/` 这种异常嵌套路径

**提交消息**: `chore: add .gitignore rules and remove generated clutter`

**风险**: 低 — 只删除自动生成和过程产物

---

### 批次 1: 确认删除

**目标**: 正式提交 109 个已删除文件

**操作**:
- 暂存并提交所有 `D`（已删除）状态的文件
- 主要是 `openspec/changes/` 下的已完成/废弃提案（76 个）
- 少量 `web/frontend/` 和 `tests/` 中确认删除的文件

**提交消息**: `chore: remove completed/obsolete openspec changes and deprecated files`

**风险**: 低 — 文件已从磁盘删除，只是正式记录

**审核要点**: 建议逐目录确认删除意图，特别是：
- `openspec/changes/add-broker-acknowledgement-reconciliation-contract/` — 是否已完成？
- `openspec/changes/add-broker-channel-topology-for-miniqmt-and-tdx/` — 是否已废弃？

---

### 批次 2: 治理文档

**目标**: 提交治理审阅和决策记录

**文件范围**:
- `reports/governance/` 中保留的有价值治理文档（约 20 个）
- `docs/reports/architecture-governance/` 审查报告
- `governance/function-tree/catalog.yaml` 变更

**提交消息**: `docs(governance): add tech-debt audit and architecture governance records`

**风险**: 低 — 纯文档

---

### 批次 3: 配置与基础设施

**目标**: 提交工具配置和脚本

**文件范围**:
- `.env.example` 新增 TDengine 配置
- `.claude/skills/` 技能更新（18 个）
- `.claude/hooks/` 钩子更新（22 个）
- `.claude/agents/` Agent 定义（7 个）
- `.claude/commands/openspec/` 命令
- `scripts/dev/` 新增脚本（含 quality_gate、websocket-server、a-stock-*）
- `.agent/` 审计清单
- `.planning/STATE.md`

**提交消息**: `chore: update claude skills/hooks/agents, scripts, and env config`

**风险**: 中 — 需确认 hooks 和 skills 变更的功能正确性

---

### 批次 4: 文档更新

**目标**: 提交所有文档变更

**文件范围**:
- `docs/` 下 53 个已修改 + 193 个新增文档
- `openspec/specs/` 新增 specs（15 个）
- `openspec/changes/` 剩余变更（11 个）
- 根目录 `DESIGN.md`、`PRODUCT.md`、`README.md`

**提交消息**: `docs: update guides, reports, specs, and project documentation`

**风险**: 低 — 纯文档

**注意**: 这批文件最多（约 250 个），如需细分可拆为:
- 4a: `docs/guides/` + `docs/api/`
- 4b: `docs/reports/`
- 4c: `openspec/`

---

### 批次 5: 代码变更（src + tests）

**目标**: 提交后端核心代码和测试

**文件范围**:
- `src/` 下 32 个已修改 + 1 个新增
  - `src/application/services/performance_optimizer.py`（已暂存）
  - `src/domain/portfolio/` 新增和修改（已暂存部分）
  - `src/infrastructure/persistence/exceptions.py`（已暂存）
  - 其他 src 变更
- `tests/` 下 72 个已修改 + 11 个新增
  - `tests/ddd/test_domain_layer_dependencies.py`（已暂存）
  - 其他测试文件

**提交消息**: `feat: portfolio valuation optimization, domain exceptions, and tests`

**风险**: 中 — 需运行 `pytest` 确认测试通过

**当前暂存区处理**: 已暂存的 5 个文件在此批次提交前需先 `git reset HEAD` 取消暂存，随对应批次重新暂存

---

### 批次 6: 前端与后端（web/）

**目标**: 提交 Web 层代码变更

**文件范围**:
- `web/frontend/` — 287 个已修改 + 76 个未跟踪（最大的单批）
- `web/backend/` — 39 个已修改 + 3 个新增
- 包含 `Settings.vue`（已暂存）和对应测试

**提交消息**: `feat(frontend): settings page overhaul and frontend updates`

**风险**: 中高 — 文件最多，建议拆分:
- 6a: `web/backend/` 后端 API 变更
- 6b: `web/frontend/src/` 前端源码
- 6c: `web/frontend/` 其他（配置、测试等）

---

## 四、执行前确认清单

| # | 确认项 | 状态 |
|---|--------|------|
| 1 | 当前 5 个已暂存文件是否取消暂存重新分配？ | 待确认 |
| 2 | `reports/governance/` 链式文件的最终版本是哪些？ | 待确认 |
| 3 | `openspec/changes/` 下的 76 个已删除变更是否全部确认删除？ | 待确认 |
| 4 | `scripts/dev/a-stock-*` 目录是临时实验还是正式工具？ | 待确认 |
| 5 | 是否需要先运行测试确认代码变更不引入回归？ | 建议: 是 |
| 6 | 6 个批次是否需要进一步细分或合并？ | 待确认 |

---

## 五、预估时间线

| 批次 | 预估文件数 | 风险 | 预估时间 |
|------|-----------|------|----------|
| 0 | ~30 | 低 | 5 min |
| 1 | ~109 | 低 | 5 min |
| 2 | ~25 | 低 | 3 min |
| 3 | ~70 | 中 | 10 min |
| 4 | ~250 | 低 | 10 min |
| 5 | ~105 | 中 | 10 min |
| 6 | ~365 | 中高 | 15 min |

**总计**: ~6 个提交，约 60 分钟

---

## 六、后续建议

清理完成后:
1. 确认 `wip/root-dirty-20260403` 分支是否可合并到 main，或应创建新的 PR
2. 运行完整质量门（pytest + vue-tsc + stylelint）
3. 开始架构治理工作

---

*本文档由 Claude 生成，待审核确认后执行。*
