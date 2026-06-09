# 审核意见: ArtDeco Impeccable Line Summary And Next Plan

> 审核对象: `docs/reports/tasks/2026-05-29-artdeco-impeccable-line-summary-and-next-plan.md`
> 审核日期: 2026-05-29
> 审核方法: 逐节证据核验 + git log / git status / grep / file_search 交叉比对
> 总体结论: 结构清晰、证据链完整，建议按以下 6 条修改后通过。

---

## 总体评价

这是一份结构清晰的阶段性总结文档。Line goal 明确，三阶段试点 (Market Realtime → Risk Alerts → Trade Positions) 的证据引用均可追溯，Phase 0–4 的下一步序列务实合理。

核验情况:
- 两个已提交 commit 哈希 (`de0c5b8c9`, `8ed6c91d0`) 均已确认存在
- Trade Positions 对应文件当前处于 modified/untracked 状态，与 "Not committed yet" 一致
- OpenSpec change 目录、tasks.md (全部 `[x]`)、`artdeco-design-governance` spec 均存在
- 所有引用的 critique / shape brief / implementation report 文件均存在
- `phase3-mainline-matrix.spec.ts` 确认处于 modified 状态

---

## 逐节发现

### 1. §2.1 — PRODUCT.md / DESIGN.md 刷新时间线不明确

文档说 "were refreshed for Web ArtDeco and page-design governance"，但这两个文件的上一次 commit 是 `93f6d69` (5月10日)，当前处于 `M` (dirty) 状态。是 5月10日 commit 完成的刷新，还是当前 worktree dirty 即为刷新结果？建议补充一句时间线说明。

### 2. §2.1 — OpenSpec 归档判据分散

文档说 "should be archived only after the current uncommitted trade positions slice is either committed…or explicitly excluded"，这个判断标准在 §5 Phase 1 的 decision point 中才展开。建议在 §2.1 直接交叉引用 §5 Phase 1，减少读者翻找。

### 3. §4 — "29 error references" 计数方法未定义

对 `trade/Signals.vue` 用 `grep error|Error|ERROR` 命中 **20 个不同行**。若按标识符出现次数计 (`routeError` × 5 + `staleError` × 7 + `effectiveError` × 3 + …)，29 可能成立，但文档没有声明计数口径，读者无法复现。

- **建议**: 改为 `~20 error-tagged lines` 或明确标注计数方法。

### 4. §4 — "4 native title attributes" 用词不够精确

4 个 `title="..."` 匹配中，1 个是 `ArtDecoHeader` 的 prop，3 个是 `ArtDecoCard` 的 prop——这些是 Vue 组件 prop 绑定而非 HTML native `title` 属性。

- **建议**: 改为 `4 title prop bindings`。

### 5. §2.4 + §5 Phase 0 — 验证命令缺少工作目录说明

所有 `npm` / `npx` / `node` 命令实际需要在 `web/frontend/` 下执行:
- `node scripts/check-artdeco-tokens.js` → `web/frontend/scripts/check-artdeco-tokens.js`
- `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts` → `web/frontend/tests/e2e/…`

- **建议**: 在验证命令代码块前加一行 `# 在 web/frontend/ 目录下执行`。

### 6. §5 Phase 2 与 §3 的措辞隐含矛盾

§3 item 7 说 "Shared extraction should wait until repeated page patterns are compared side-by-side"，而 Phase 2 要做的是 "documentation-only extraction analysis"——本质上就是 side-by-side comparison。逻辑一致，但措辞容易让读者误以为两处矛盾。

- **建议**: Phase 2 开头显式引用 §3 item 7，例如: "Phase 2 正是 §3.7 要求的 side-by-side comparison，产出为分析文档而非共享组件代码。"

---

## 补充建议 (非阻塞)

- **§6**: 当前 worktree 有大量脏文件 (467 commits behind origin，trade/ 目录下 4 个 modified + 3 个 untracked)。建议在 §6 加一句当前脏文件范围提示，避免实际提交时误包含非目标文件。
- **Trade Positions 实施报告** (独立文件 `2026-05-29-artdeco-trade-positions-implementation-report.md`) 的验证命令同样缺少 `cd web/frontend` 说明。

---

## 建议修改清单 (摘要)

| # | 位置 | 修改项 |
|---|------|--------|
| 1 | §2.1 | 补充 PRODUCT.md / DESIGN.md 刷新时间线 |
| 2 | §2.1 | 交叉引用 §5 Phase 1 归档判据 |
| 3 | §4 | "29 error references" → `~20 error-tagged lines` 或明确计数方法 |
| 4 | §4 | "4 native title attributes" → `4 title prop bindings` |
| 5 | §2.4 + §5 Phase 0 | 验证命令块前加 `cd web/frontend` 说明 |
| 6 | §5 Phase 2 | 显式引用 §3 item 7，澄清一致性 |
