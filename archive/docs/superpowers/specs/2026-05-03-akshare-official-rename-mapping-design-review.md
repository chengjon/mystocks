# Review: AkShare Official Rename Mapping Design

**审阅对象**: `docs/superpowers/specs/2026-05-03-akshare-official-rename-mapping-design.md`
**审阅日期**: 2026-05-04
**审阅范围**: 文档准确性、内部一致性、与现有仓库状态的对齐、缺失项

---

## 总评

设计文档结构清晰、边界纪律良好（仅接受 4 个映射、显式拒绝列表、无第三方来源）。
主要问题集中在：(1) `stock_news_main_cx` 接受与现有 tasks.md 排除立场之间的未解释反转；(2) 缺少响应 schema 契约说明。解决这两点后，设计即可进入采纳阶段。

---

## CRITICAL (1)

### C1. `stock_news_main_cx` 映射被接受，但现有 tasks.md 明确排除

**位置**: Section 1 第 67 行（接受映射） vs `openspec/changes/expand-akshare-data-sources/tasks.md` 第 92 行

**现状**: tasks.md:92 当前记录为：
> `stock_news_main_em -> stock_news_main_cx` **明确排除**

设计文档将其列为四个正式接受映射之一，但未承认或解释这一立场反转。

**建议**: 增加明确的 Decision Record 条目，说明：
- 什么新信息导致排除立场被推翻
- em→cx 跨 provider family 变更（东方财富 → 财联社）是否已验证返回语义等价数据
- 最初排除的原因是什么，为何该原因不再适用

---

## HIGH (2)

### H1. 响应 Schema 契约未覆盖

**位置**: Section 4.2（映射元数据）与 Section 4.3（池族归一化）

**问题**: 设计指定了在 route payload 中增加映射元数据，并提到 "pool family normalization"，但从未确认：重命名后的函数是否返回与原函数相同的 schema？例如 `stock_zt_pool_dtgc_em` 与原 `stock_dt_pool_em` 的返回列是否一致？若不一致，adapter 归一化工作量会显著增加。

**建议**: 增加一个子节，记录每个映射函数的预期 schema 差异：
- 若已验证无差异，明确写 "无预期差异"
- 若存在差异，列出具体的列映射表
- 这可以防止实现阶段的歧义和返工

### H2. `stock_news_main_cx` 的 provider drift 风险被低估

**位置**: Section 8.1 第 247 行

**问题**: `em→cx` 不是简单重命名，而是 provider family 变更（东方财富 → 财联社）。数据内容、更新频率、覆盖范围可能不同。Section 8.1 仅提到 canonical-plus-alias 路由作为缓解措施，但这只解决路由兼容性，不解决语义漂移。

**建议**: 升级风险处理，明确指定：
- (a) 需要对齐哪些数据质量门禁（字段覆盖率、空值率、时效性）
- (b) 是否需要 schema reconciliation layer
- (c) 用户可见行为是否可能不同（若不同，前端是否需要同步调整）

---

## MEDIUM (3)

### M1. Pool Family Normalization (Section 4.3) 缺乏规格

**问题**: "按业务目标语义而非原始上游命名归一化输出列" 的方向正确，但缺少具体内容。哪些列？什么映射关系？没有明确的列映射表，实现者只能猜测。

**建议**: 提供一张表，定义 `zt_pool` 系列函数的预期归一化输出列集合，或引用一份单独定义该映射的 spec 文档。

### M2. 现有 `PREFERRED_HELP_CANDIDATES` 未被确认为前置基础

**位置**: `scripts/dev/quality_gate/collect_akshare_market_function_availability.py` 第 27-31 行

**发现**: 该脚本已定义 `PREFERRED_HELP_CANDIDATES`，内容与设计的四个映射完全一致：

```python
PREFERRED_HELP_CANDIDATES = {
    "stock_news_main_em": ("stock_news_main_cx",),
    "stock_dt_pool_em": ("stock_zt_pool_dtgc_em",),
    "stock_strong_pool_em": ("stock_zt_pool_strong_em",),
    "stock_new_em": ("stock_zt_pool_sub_new_em",),
}
```

说明代码库已为此方向做了前置准备。设计文档未提及这一现有基础，可能会让后续审阅者误以为映射是从零开始定义的。

**建议**: 在 Section 1 或 Section 3 中确认 `PREFERRED_HELP_CANDIDATES` 已经对齐，并说明本 proposal 将其从 advisory 升级为 approved。这可以明确变更的增量性质。

### M3. `stock_weak_pool_em` 退役流程不完整

**位置**: Section 1 第 73-78 行

**问题**: 设计描述了 `stock_weak_pool_em` 的退役状态，但 tasks.md:84 仍为 `[ ] 6.7 实现弱势股池 (akshare.stock_weak_pool_em)`，无退役标注。设计未指明 tasks.md 中哪些条目需要更新以反映退役。

**建议**: 在 Section 7.6（文档更新顺序）中增加 tasks.md task 6.7 的更新步骤，明确 6.7 应标记为退役（如 `[~]` 或类似标记），而非 checked 或 unchecked。

---

## LOW (4)

### L1. `stock_zh_a_new_em` 拒绝理由仅隐含

**位置**: Non-Goals 第 45 行、Section 1 第 70 行

**问题**: 两处都拒绝了 `stock_new_em -> stock_zh_a_new_em`，但从未解释原因。作为主要拒绝边界之一，理由应可追溯。

**建议**: 增加一句解释，例如："`stock_zh_a_new_em` 覆盖的是 A 股新股上市而非次新股，语义不匹配。"

### L2. Section 2.1 测试文件列表可能有遗漏

**位置**: Section 2.1 第 98 行

**问题**: 列出了 3 个测试文件，但 `tests/unit/scripts/test_frontend_testing_akshare_runtime_gate.py` 也存在且与 gate 链路相关。根据范围决定是否纳入或显式排除。

### L3. Section 8.3 与 Section 2.3 交付顺序一致性

**位置**: Section 2.3 第 124-131 行 vs Section 8.3 第 475 行

两处一致（dt → strong → sub_new → news_main → weak retired），无矛盾。仅标注：Section 8.3 用箭头串联，Section 2.3 用编号列表，两者可以互相引用以减少维护负担。

### L4. `openspec validate --strict` 命令格式未验证

**位置**: Section 6.1 第 341 行

**问题**: `openspec validate expand-akshare-data-sources --strict` 是否为本项目可用的实际 CLI 命令未确认。若该命令不存在，验证章节将具有误导性。

**建议**: 执行一次命令验证，或标注为"待验证"。

---

## INFO (3)

### I1. 文件引用全部有效

Section 2 治理层 9/9 文件和运行时层 6/6 文件均已确认存在。

### I2. Task 编号引用全部有效

6.3, 6.5, 6.6, 6.9, 6.10, 6.11, 6.12, 7.2, 7.4, 7.5, 8.x 均存在于 `openspec/changes/expand-akshare-data-sources/tasks.md`。

### I3. 内部一致性良好

设计在所有章节间保持一致：Goals 与 Section 细节对齐、Non-Goals 在 Section 8 得到强化、交付顺序与风险排序匹配。

---

## 建议处置优先级

| 优先级 | 条目 | 行动 |
|--------|------|------|
| **阻塞采纳** | C1 | 补充 `stock_news_main_cx` 立场反转的 Decision Record |
| **阻塞采纳** | H1 | 补充响应 schema 契约说明 |
| **强烈建议** | H2 | 升级 provider drift 风险处理 |
| **建议采纳前完成** | M1-M3 | 补充归一化规格、确认前置基础、完善退役流程 |
| **可在实现阶段修复** | L1-L4 | 低优先级改进项 |

---

**审阅结论**: 解决 C1 和 H1 后可进入采纳阶段。
