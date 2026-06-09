# Review (v2): AkShare Official Rename Mapping Design

**审阅对象**: `docs/superpowers/specs/2026-05-03-akshare-official-rename-mapping-design.md`
**审阅日期**: 2026-05-04
**审阅者**: Claude (独立审阅)
**与前一版审阅的关系**: 前一版审阅 (`*-review.md`) 基于早期草稿。当前设计稿已做了大量修订，多项目前提已被解决。本审阅基于当前 447 行版本独立进行。

---

## 总评

设计文档边界纪律优秀，是该项目近期质量最高的设计稿之一。对"已落地 vs 待设计"的分层极其清晰，explicit non-rules 做法值得推广。

主要关注点：(1) 归一化契约的字段映射存在模糊地带；(2) 候选提升顺序缺少排序依据；(3) 上游再次改名的应急策略空白。这三项均不阻塞文档采纳，但应在实现微批启动前补齐。

---

## CRITICAL (0)

无。设计稿不改变当前运行时真相，仅记录治理事实和定义未来规则，风险可控。

---

## HIGH (3)

### H1. 归一化契约的字段来源映射不完整

**位置**: Section 4.3 第 249-264 行

**问题**: `Normalized Pool Output Contract` 表格定义了 14 个归一化字段，但多个字段的来源标记不够精确：

- `turnover_rate` 标注为 `换手率 or 转手率`，但未说明哪个候选用哪个。根据 Section 4.2 的观测记录，`stock_zt_pool_strong_em` 用 `换手率`，`stock_zt_pool_sub_new_em` 用 `转手率`，`stock_zt_pool_dtgc_em` 的 payload 是否包含此列未标注。
- `board_metrics` 标注为 `normalize as structured metadata`，但未定义这个 metadata 的结构。是 `{consecutive_limit_down: int, limit_up_count: int, ...}` 还是一个自由形式的 dict？实现者无从判断。
- `selection_reason` 标注 `mostly strong-pool specific`——"mostly" 是什么意思？dt-pool 和 sub-new-pool 返回此列时应该填什么？null？空字符串？还是应该设为 optional 并在前端优雅降级？

**建议**: 增加一列 `Required / Optional` 和一列 `Per-candidate applicability matrix`（3 行 x 14 列），明确每个候选对每个字段的提供情况。

### H2. 候选提升顺序缺少排序依据

**位置**: Section 2.3 第 138-147 行、Section 4.1 第 208-213 行

**问题**: 两处都指定 `dt → strong → new` 的顺序，理由仅一句"保持了 zt_pool 家族的一致性，也避免过早处理 news_main_cx 的 provider drift 风险"。

这不是排序依据，而是对不做什么的解释。缺少的是：为什么 dt 排第一而不是 strong？排序考虑因素是什么？

可能的排序维度：
- 业务价值（哪个池对用户最重要？）
- 实现风险（哪个映射最不确定？）
- payload 复杂度（哪个归一化工作最大？）
- 下游依赖（哪些前端组件在等哪个？）

**建议**: 补充排序决策的 1-2 条显式依据。例如："dt 排首因跌停池与现有涨停池 (stock_zt_pool_em) 已有实现的归一化 pipeline 最接近，复用成本最低。"

### H3. 上游再次改名的应急策略空白

**位置**: 全文

**问题**: 设计详细处理了"当前 akshare 1.18.60 的改名候选"，但未讨论：如果 AkShare 在未来版本中再次改名（例如 `stock_zt_pool_dtgc_em` → `stock_zt_pool_dtgc_v2_em`），当前的 gate + adapter 架构如何应对？

当前 gate 硬编码了 `PREFERRED_HELP_CANDIDATES`。如果上游再次改名：
- gate 会重新报 missing（良性，但会中断 CI）
- adapter 里的映射会断裂
- 没有 fallback 或版本嗅探机制

**建议**: 在 Section 4.5 (Provider Drift Guardrail) 中增加一段 "Upstream Re-rename Contingency"，说明：
- gate 是否应支持多版本候选（tuple 而非 single string）
- adapter 是否应有 try-except + graceful degradation
- 是否需要在 `PREFERRED_HELP_CANDIDATES` 中记录 akshare 版本约束

---

## MEDIUM (4)

### M1. 文档存在较多重复表述

**位置**: 多处

**问题**: 以下信息在文档中重复出现 3 次以上：
- `dt / strong / new` 是仅有的三个保留候选
- `stock_news_main_cx` 被排除
- `stock_weak_pool_em` 是 unresolved gap
- advisory candidate 不等于 approved mapping

Section 1、Section 3.2、Section 4.1、Section 4.2、Section 4.2.1、Section 8 各重复一次。对于一份 447 行的文档，这造成了较高的阅读噪音。

**建议**: 采用 "define once, reference elsewhere" 结构。在 Section 3.2 (Candidate Inventory Table) 做唯一事实定义，其他章节引用表格行号即可。

### M2. `stock_weak_pool_em` 的未来处置路径未定义

**位置**: Section 1.2 第 101-110 行、Section 6.3 第 376-379 行

**问题**: 文档多次强调 `stock_weak_pool_em` 是 "unresolved gap"，"不应伪装成已退役"——这个立场正确。但文档也完全没有定义：什么条件下这个 gap 应该被关闭？

可能的关闭路径：
- (a) AkShare 未来版本恢复了 `stock_weak_pool_em` 同名函数
- (b) 找到语义等价的新候选
- (c) 业务决定不再需要弱势股池功能（此时才应标为 retired）

缺少关闭条件意味着这个 gap 会永远停留在 "unresolved" 状态。

**建议**: 在 Section 1.2 增加 "Gap Closure Criteria" 子节，列出 2-3 条可评估的关闭条件。

### M3. 归一化 contract 缺少版本化策略

**位置**: Section 4.3

**问题**: 定义了一个稳定的归一化输出 contract，但未说明：
- 这个 contract 如何随时间演化？
- 如果未来增加字段，是 additive change 还是需要版本号？
- 前端如何感知字段可用性？

**建议**: 增加一句策略声明，例如："归一化字段只做 additive extension，不删除已有字段。新字段标记为 optional，前端通过 feature detection 消费。"

### M4. 验证命令未确认全部可用

**位置**: Section 6.1 第 341-347 行

**问题**: 列出 7 条验证命令，但：
- `openspec validate expand-akshare-data-sources --strict` 是否为本项目可用 CLI 命令未在本次审阅中确认
- 已知通过结果标注为"来自另一条线已收口批次"，但未标注批次 commit hash
- `test_frontend_testing_akshare_runtime_gate.py` 未在 Section 2.1 的已落地文件列表中体现

**建议**: 确认 `openspec` CLI 可用性；为已知通过结果补充 commit hash 引用。

---

## LOW (3)

### L1. `stock_zh_a_new_em` 拒绝理由仅隐含

**位置**: Non-Goals 第 59 行、Section 4.3.1 第 276 行

**问题**: 两处拒绝 `stock_new_em → stock_zh_a_new_em`，Section 4.3.1 有简短解释（"更宽泛的新股，而 sub_new_em 更接近次新股池语义"），但 Non-Goals 无解释。作为显式拒绝边界，应在首次提及处附理由。

### L2. Section 编号有重复子节

**位置**: Section 4.2 (第 218 行) 和 Section 4.2.1 (第 228 行)

Section 4.2 的标题是 "Observed Local Signatures And Payload Shapes"，Section 4.2.1 的标题是 "Why stock_news_main_cx Is Not In The Current Promotion Batch"。

4.2.1 在逻辑上更像是 1.1 (Decision Record) 的补充，而非 payload 观测的子节。当前位置不影响理解，但如果文档继续演化，建议重新组织到 Section 1 的 Decision Record 附近。

### L3. Section 7.3 文件更新清单可做增量标注

**位置**: Section 7.3 第 421-430 行

**问题**: 列出 9 个需要更新的文件，但未标注哪些文件只需追加一行映射记录，哪些需要结构性修改。这会让实现者难以估算工作量。

**建议**: 增加 `Change Type` 列（如 `append mapping entry` / `update gate logic` / `rewrite section`），帮助实现者快速分类。

---

## INFO (4)

### I1. Git commit 引用验证通过

`435bc8f00 akshare: add market repo-truth gates` 确认存在于当前分支历史。

### I2. 三个 gate 脚本文件确认存在

```
scripts/dev/quality_gate/collect_akshare_market_function_availability.py
scripts/dev/quality_gate/validate_akshare_market_repo_truth.py
scripts/dev/quality_gate/run_akshare_market_gates.py
```

### I3. OpenSpec 目录和文档文件确认存在

`openspec/changes/expand-akshare-data-sources/` 下 `proposal.md`、`design.md`、`tasks.md` 均存在。`docs/guides/akshare/` 下的扩展指南和排障指南也存在。

### I4. `PREFERRED_HELP_CANDIDATES` 确认与设计对齐

代码中的 `PREFERRED_HELP_CANDIDATES` (4 个映射) 与设计文档 Section 3.2 的 candidate inventory 完全一致。设计已在 Section 3.3 明确其 advisory 语义，与前一版审阅的 M2 问题相比已充分处理。

---

## 与前一版审阅的对比

前一版审阅（`*-review.md`）标记了 1 CRITICAL、2 HIGH、3 MEDIUM、4 LOW。当前版本已解决或缓解的情况：

| 前版条目 | 当前状态 |
|----------|---------|
| C1 (`stock_news_main_cx` 被接受) | **已解决** — 当前稿明确排除，Section 1.1 有完整 Decision Record |
| H1 (响应 Schema 未覆盖) | **已缓解** — Section 4.3 新增详细归一化契约表，但粒度仍有提升空间（见本文 H1） |
| H2 (provider drift 被低估) | **已解决** — Section 1.1、4.2.1、4.5 多处显式处理 |
| M1 (归一化缺规格) | **已缓解** — Section 4.3 新增规格表，但 applicability matrix 缺失（见本文 H1） |
| M2 (PREFERRED_HELP_CANDIDATES 未确认) | **已解决** — Section 3.3 专门讨论 |
| M3 (weak_pool 退役流程) | **部分缓解** — 设计明确"不伪装退役"，但关闭条件仍空白（见本文 M2） |

---

## 建议处置优先级

| 优先级 | 条目 | 行动 |
|--------|------|------|
| **建议采纳前补齐** | H1 | 补充 per-candidate applicability matrix |
| **建议采纳前补齐** | H2 | 补充排序依据（1-2 句即可） |
| **可在首批实现微批前补齐** | H3 | 补充上游再改名应急策略 |
| **可在实现阶段处理** | M1-M4 | 降低阅读重复、补充 gap 关闭条件、增加 contract 版本化、确认验证命令 |
| **可暂不处理** | L1-L3 | 低优先级改进项 |

---

**审阅结论**: 文档可采纳。建议在启动第一个 candidate promotion 微批之前补齐 H1 (applicability matrix) 和 H2 (排序依据)，这两项信息量不大但对实现者有直接指导价值。H3 可在实现阶段与 adapter 设计同步完成。
