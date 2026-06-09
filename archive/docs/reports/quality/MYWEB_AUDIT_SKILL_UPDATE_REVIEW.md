# MyWeb Audit Skill 更新审核报告

> **审核日期**: 2026-04-25
> **审核对象**: 基于前次审核建议 `MYWEB_AUDIT_SKILL_REVIEW.md` 所做的修改
> **审核文件**:
> - `references/audit-checklist.md`
> - `references/manifest-template.md`
> - `references/findings-schema-example.md`
> - `references/closeout-checklist.md`
> - `agents/myweb-audit-functional-audit.md`
> - `agents/myweb-audit-data-state-audit.md`
> - `agents/myweb-audit-visual-artdeco-audit.md`
> - `agents/myweb-audit-responsive-a11y-audit.md`

---

## 总体评价

8 个文件的修改方向正确，与审核建议高度对齐。核心结构性问题（执行模型、工具声明、Output Contract 统一、桌面端断点）均已解决。以下按文件逐一审核，标注 **通过** / **建议调整** / **残留问题**。

---

## 1. audit-checklist.md — 通过

**变更点**: Section 5 Responsive 断点调整为桌面端范围，Section 6/8 注释强化桌面端定位。

**审核结论**: 变更完整、无矛盾。

- 断点从 `1440, 1280, 1024, 768, 390` 收窄为 `1920, 1440, 1280` — 正确
- `1024` 标记为 optional informational — 正确
- 底部 Note 明确 "widths below 1280 should not be treated as required responsive targets" — 正确
- Section 6 Accessibility 和 Section 8 Required States 未受影响 — 无副作用

**无需进一步修改。**

---

## 2. manifest-template.md — 通过，有两个小建议

**变更点**: 新增 `browser_tool`、`execution_surface`、`verification_strategy`、`repair_approval` 字段。

**审核结论**: 核心结构正确，解决了执行策略声明和修复审批门禁两个关键问题。

### 通过项

- `execution_surface: live-audit | code-review-only` — 与 Agent 的 `verification_surface` 字段对齐，逻辑一致
- `verification_strategy: full | chromium-only | code-review-only` — 回答了 OpenSpec 的 Open Question，按批次覆盖
- `repair_approval` 包含 `status`、`approved_findings`、`deferred_findings` — 实现了修复前用户确认门禁
- Field Notes 补充了新字段的说明 — 文档自洽

### 建议调整（非阻塞）

**S1. `repair_approval.status` 初始值建议改为 `not_requested`**

当前初始值为 `pending`，但 `pending` 语义模糊——可能是"等待审批中"也可能是"尚未发起审批"。建议初始值用 `not_requested`，在 merge findings 完成后变更为 `pending`，用户确认后变更为 `approved` 或 `partial`。这让状态流转更清晰。

**S2. 缺少 `resume_rules` / `storage_path`**

前次审核建议 C3 提到 manifest 应包含恢复语义和存储路径。当前模板未包含。这是一个**低优先级**建议——如果目前不打算支持跨会话恢复，可以先不加，但建议在 Field Notes 中加一行说明 manifest 当前仅用于会话内生命周期，跨会话恢复暂不支持。

---

## 3. findings-schema-example.md — 通过，有一个建议

**变更点**: 新增 `shared_impact_candidate`、`cross_page_impact`、`dedupe_key` 字段；Normalization Rules 增加 `verification_surface` 和统一字段说明。

**审核结论**: 结构扩展合理，与 Agent Output Contract 的 `verification_surface` 字段对齐。

### 通过项

- `shared_impact_candidate: false` + `cross_page_impact: []` — 解决了 Shared Impact 前置判定问题
- `dedupe_key` 格式 `/market/overview:interaction:useMarketFilters` — 可用于结构化去重
- Merge Example 的 breakpoints 已同步更新为桌面端范围 — 一致
- Normalization Rules 补充了 `verification_surface` 枚举和跨角色统一字段说明 — 完整

### 建议调整（非阻塞）

**S3. Normalization Rules 缺少 `dedupe_key` 的计算规则定义**

示例中 `dedupe_key` 是 `/market/overview:interaction:useMarketFilters`，但未说明构造规则。建议在 Normalization Rules 中增加一条：

```
- `dedupe_key` must be constructed as `{route}:{issue_type}:{primary_repair_target_component_or_file}` (omit file extension). Two findings with the same dedupe_key from different roles describe the same underlying issue and must be consolidated.
```

这将让去重逻辑可编程化，而不依赖人工判断。

---

## 4. closeout-checklist.md — 通过

**变更点**: Fix Accounting 增加用户审批记录检查项。

**审核结论**: 变更正确且最小化。

- `User approval for repaired findings was recorded` — 与 manifest 的 `repair_approval` 字段配合
- 其余检查项未受影响 — 无副作用

**前次审核建议 C4（severity 一致性检查）和 C5（环境 fallback 验证）未体现。** 如果暂不加入，建议在 Usage Notes 中标注一条：

```
- If the same issue was reported by multiple roles at different severities, the highest severity must be used after consolidation.
```

这是低优先级补充。

---

## 5. myweb-audit-functional-audit.md — 通过

**变更点**: tools 增加 `Playwright`；Required Inputs 增加 `execution surface from the manifest`；Workflow 增加双模式分支；Output Contract 统一化；Constraints 增加 `verification_surface` 降级说明。

**审核结论**: 变更完整，与建议 A1 + A2 + B5 完全对齐。

### 通过项

- `tools: Read, Bash, Playwright` — 正确声明了浏览器交互能力
- Workflow step 2/3 的 `execution_surface` 分支 — 正确处理了 live-audit vs code-review-only
- Output Contract 统一为 9 个标准字段（severity/title/trigger/expected/actual/evidence/repair_target/dependency/verification_surface）— 与其他 3 个 Agent 完全一致
- Constraint `If browser automation is unavailable, mark the finding verification_surface: code-review-only` — 降级策略明确

**无需进一步修改。**

---

## 6. myweb-audit-data-state-audit.md — 通过

**变更点**: 同 functional-audit — tools 增加 `Playwright`；增加 `execution surface` 输入；双模式 Workflow；统一 Output Contract；降级约束。

**审核结论**: 与 functional-audit 的修改模式一致，对齐正确。

- Workflow step 2/3 明确区分了 live 网络检查和代码推断 — 对 data-state 角色尤为重要
- Constraint `If browser tooling or network inspection is unavailable, mark the finding verification_surface: code-review-only` — 比 functional-audit 多提了 network inspection，更精确

**无需进一步修改。**

---

## 7. myweb-audit-visual-artdeco-audit.md — 通过

**变更点**: 同上模式。

**审核结论**: 正确。

- Workflow step 2 提到 `capture screenshots when needed` — 对视觉审计角色合理
- Constraint `If rendered inspection is unavailable, mark the finding verification_surface: code-review-only` — 用词 "rendered inspection" 比 "browser automation" 更贴切

**无需进一步修改。**

---

## 8. myweb-audit-responsive-a11y-audit.md — 通过

**变更点**: 同上模式；断点更新为桌面范围；增加 desktop-first 约束。

**审核结论**: 变更正确且一致。

- 断点从 `1440, 1280, 1024, 768, 390` 更新为 `1920, 1440, and 1280` — 与 audit-checklist.md 一致
- Constraint `Widths below 1280 are informational only unless the user explicitly asks for exploratory observation` — 与 audit-checklist.md 底部 Note 一致
- Output Contract 与其他 3 个 Agent 完全统一

**无需进一步修改。**

---

## 跨文件一致性检查

| 维度 | 状态 |
|------|------|
| 断点一致性（checklist / manifest / responsive-agent） | 1920, 1440, 1280 — 一致 |
| `execution_surface` / `verification_surface` 语义（manifest / agents / findings） | live-audit / code-review-only — 一致 |
| Output Contract 字段（4 个审计 Agent） | 9 个统一字段 — 一致 |
| `repair_approval` 门禁（manifest / closeout） | manifest 字段 + closeout 检查项 — 一致 |
| `shared_impact_candidate` / `cross_page_impact` / `dedupe_key`（findings schema） | 已新增，与 Agent 输出对齐 — 一致 |
| 桌面端定位声明（checklist / responsive-agent） | 明确，无矛盾 |

**无跨文件不一致。**

---

## 残留建议汇总（均非阻塞）

| 编号 | 建议 | 优先级 | 涉及文件 |
|------|------|--------|---------|
| S1 | `repair_approval.status` 初始值改为 `not_requested`，明确状态流转 | Low | manifest-template.md |
| S2 | 在 manifest Field Notes 中声明"当前仅用于会话内生命周期" | Low | manifest-template.md |
| S3 | 在 Normalization Rules 中增加 `dedupe_key` 构造规则 | Medium | findings-schema-example.md |
| S4 | 在 closeout Usage Notes 中增加 severity 冲突解决规则 | Low | closeout-checklist.md |

**以上 4 项可以在下次修订时处理，不影响当前版本的正确性和可用性。**

---

## 结论

**审核通过。** 8 个文件的修改完整解决了前次审核中的 A1（执行模型）、A2（工具声明）、A3（桌面端断点）、A4（修复审批门禁）、B3（Shared Impact 字段）、B5（Output Contract 统一）共 6 项建议。残留 4 项低优先级建议可后续迭代。
