# Backend OpenSpec Issue 1 Publication Runbook — Matt Pocock Skills Review

> **审核对象**: `docs/reports/quality/backend-openspec-issue1-publication-runbook-2026-05-18.md`
>
> **审核日期**: 2026-05-18
>
> **审核方法**: Matt Pocock skills — `/grill-with-docs` (事实校准), `/to-issues` (独立可抓取性), `/caveman` (简洁性), `/diagnose` (风险诊断), `/zoom-out` (上下文校准), `/triage` (停⛔条件审查)
>
> **关联审核上游**: `docs/reports/quality/backend-openspec-drafts-mattpocock-review-2026-05-18.md` 及其 addendum / post-review

---

## 结论

本 runbook 的**核心操作路径是正确的**：issue 1 的 `gh issue create` 命令、标签、body file 路径、以及 "do not run the other 9" 的约束都与 manifest.md 一致。pre-publish checklist 覆盖了关键门禁。

但 runbook 存在 **三个结构性问题**，使其在 mattpocock/skills 标准下未达到 "can hand to a human and walk away" 的清晰度：

| # | 问题 | 技能维度 | 严重度 |
|---|---|---|---|
| 1 | 事实声明不可自行验证（governance gate 6 files / OpenSpec C/G/E/F valid 缺少命令） | `/grill-with-docs` | ⚠️ Medium |
| 2 | 混合三层内容（issue 1 only / post-1 edits / full publication order），稀释 runbook 焦点 | `/caveman` | ⚠️ Medium |
| 3 | 缺少 "批准机制" 定义和关键引用文档链接 | `/zoom-out` | 🔴 High |

---

## `/grill-with-docs` — 事实校准

### ✅ 已验证一致

| Runbook 声明 | 实际验证结果 |
|---|---|
| Manifest command count = 10 | manifest.md: "Publishable issue count: `10`"，10 条 `gh issue create` 命令 ✅ |
| Issue 1 labels: `ready-for-human` + `enhancement` | manifest.md 第 1 行: `ready-for-human` + `enhancement` ✅ |
| Audit-only bodies: 03/04/05 不发布 | manifest.md "Already Resolved / Do Not Publish" 表 ✅ |
| 目录下 14 个文件（含 manifest + 3 audit-only）= 10 publishable | `list_dir` 确认: 14 files - 1 manifest - 3 audit-only = 10 ✅ |
| BLOCKED_BY_TODO 占位符存在且与 runbook 表一致 | `grep_files` 确认: 8 个 body 文件含 `BLOCKED_BY_TODO: issue 1 approval.` ✅ |
| Authoritative publication order: 1→2→8→9→10,11→12→13→6,7 | manifest.md Publication Order 表一致 ✅ |

### ⚠️ 无法自行验证的声明

以下 checklist 行缺少验证命令，人类执行者无法独立复现：

**1. Scoped markdown governance gate**

Runbook 当前:
```text
| Scoped markdown governance gate | 6 files, 0 errors |
```

**问题**:
- 没有给出是哪 6 个文件。推测是 C/E/F/G 四个 OpenSpec change 的 `tasks.md` + 2 个 supporting artifacts，但 runbook 不应让执行者猜测。
- 没有给出运行命令。已知命令为 `python scripts/compliance/markdown_governance_gate.py --root-dir ... --path ...`，但 runbook 未提供。

**建议改为**:
```text
| Scoped markdown governance gate | 6 files, 0 errors |
| Command | `python scripts/compliance/markdown_governance_gate.py --root-dir /opt/claude/mystocks_spec --format text --path openspec/changes/consolidate-backend-api-domain-routers/tasks.md --path openspec/changes/migrate-backend-singletons-to-lifecycle-di/tasks.md --path openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md --path openspec/changes/consolidate-backend-health-endpoints/tasks.md --path docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md --path docs/reports/quality/backend-openspec-issue1-publication-runbook-2026-05-18.md` |
```

**2. OpenSpec validation**

Runbook 当前:
```text
| OpenSpec validation | C/G/E/F valid |
```

**问题**: runbook 用 "C/G/E/F" 排序，但 manifest 和实际 change 目录名是 C/E/F/G。执行者不知道运行什么命令。

**建议改为**:
```text
| OpenSpec validation | 4 changes valid |
| Command | `openspec validate consolidate-backend-api-domain-routers --strict && openspec validate migrate-backend-singletons-to-lifecycle-di --strict && openspec validate split-backend-core-modules-with-compatibility-wrappers --strict && openspec validate consolidate-backend-health-endpoints --strict` |
```

---

## `/caveman` — 简洁性审查

### 问题: Runbook 混合了三个执行层

本文件标题为 "Issue 1 Publication Runbook"，但实际包含：

| 层级 | 内容 | 是否属于 "publish issue 1"？ |
|---|---|---|
| **Layer 1**: 发布 issue 1 | Purpose, Current Gate, Candidate Command, Pre-Publish Checklist | ✅ 核心 |
| **Layer 2**: issue 1 发布后的即时操作 | "After Issue 1 Is Created" 表 + ISSUE_1 变量 | ⚠️ 合理扩展 |
| **Layer 3**: 全量发布顺序和远期占位符 | "Later Placeholder Map" (issue 2/8/10/11), "Authoritative Publication Order", "Current Evidence Snapshot" | ❌ 噪音 |

Layer 3 的内容是 manifest.md 的副本，不应重复出现在 issue-1-only runbook 中。它增加了认知负荷，降低了 runbook 的 "grab and execute" 属性。

**Caveman 原则**: 如果一个洞穴人拿起这份 runbook，他应该只看到发布 issue 1 需要的东西。

**建议**:
- "Later Placeholder Map" → 删除，改为一行引用: `See manifest.md for full placeholder replacement map for issues 2/8/10/11.`
- "Authoritative Publication Order" → 删除，manifest.md 是权威来源。
- "Current Evidence Snapshot" → 删除（538 routes / 501 OpenAPI paths 与发布 issue 1 无关）。
- 保留 "After Issue 1 Is Created" 表，因为这是 issue 1 发布后的直接后续动作。

---

## `/diagnose` — 风险与缺口诊断

### 🔴 High: 缺少批准机制定义

Runbook 多次说 "until a human explicitly approves"，但：

1. **没有定义 "approval" 的形式** — 是 Slack 消息？GitHub comment？PR review？还是口头确认？
2. **没有引用批准包** — manifest.md 引用了 `docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md`，runbook 没有。
3. **没有说批准后谁来执行命令** — 如果批准人在 issue 上评论 "approved"，执行者是立刻运行命令还是等 review window？

**建议**: 在 "Current Gate" 下增加:

```text
Approval mechanism: A maintainer must comment "APPROVED: publish issue 1" on
`docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md`
(or equivalent approval artifact). Only then may the Candidate Command be run.
```

### ⚠️ Medium: 缺少重复检测的具体命令

Stop condition 说 "The issue 1 command would create a duplicate `[Backend OpenSpec]` approval issue"，但没有给出检查命令。

**建议**: 在 Pre-Publish Checklist 第一行增加具体命令:

```bash
gh issue list --repo chengjon/mystocks --search "[Backend OpenSpec] Approve orchestration" --state open --limit 10
```

### ⚠️ Medium: 缺失引用文档

Runbook 未引用 manifest.md 中列出的两个重要预发布文档:

- `docs/reports/quality/backend-openspec-issue-publication-preflight-2026-05-18.md`
- `docs/reports/quality/backend-openspec-issue-publication-review-response-2026-05-18.md`

如果这些文件包含额外的发布前条件，runbook 执行者不会知道。

### Low: 缺少认证失败停⛔条件

没有 "如果 `gh` 未认证或 token 过期" 的停⛔条件。建议在 Stop Conditions 中增加:

```text
- `gh auth status` exits non-zero or reports an expired token.
```

### Low: "After Issue 1 Is Created" 编辑流程缺少执行者与 PR/commit 指导

Runbook 的 "After Issue 1 Is Created" 表要求更新 8 个 body 文件中的 `BLOCKED_BY_TODO` 占位符，但没有说明:

- 这些编辑是否需要单独的 commit/PR？
- 是否可以在同一个 PR 中批量完成？
- 编辑后是否需要重新运行 governance gate？

---

## `/zoom-out` — 上下文校准

### Issue 1 在整个治理体系中的位置

Issue 1 的角色是 **审批门禁**（approval gate）— 它不执行任何代码变更，只建立跨 proposal 的编排矩阵。Runbook 正确理解这一点。

但 runbook 没有解释:

1. **为什么 issue 1 必须先发布** — 因为它是四个 OpenSpec proposal (C/E/F/G) 的共享审批层，它定义了 implementation order、shared contract surfaces、blocking dependencies（这些都是前轮 mattpocock review 的 Blocker #1 要求）。
2. **issue 1 和其他 issue 的关系** — runbook 说 "Issue 1 approval is necessary but not sufficient for agent readiness"，但没有解释什么是 "sufficient"。

**建议**: 在 Purpose 下增加 motivation:

```text
Issue 1 is the approval gate because it creates the cross-change orchestration
matrix that the 2026-05-18 Matt Pocock review identified as Blocker #1. Without
this matrix, C/E/F/G implementation issues cannot independently determine their
`Blocked by` chain and therefore cannot meet the `ready-for-agent` standard.
```

---

## `/to-issues` — Issue 独立可抓取性

Runbook 对 issue 1 的发布约束是正确的:

- ✅ 单一 body file，单一标签组合
- ✅ 明确不发布其他 9 个 issue
- ✅ 明确不发布 audit-only bodies (03/04/05)
- ✅ 明确 issue 1 发布后不自动标记其他 issue 为 `ready-for-agent`

无额外问题。

---

## `/triage` — 停⛔条件审查

### 现有停⛔条件

| 停⛔条件 | 评价 |
|---|---|
| 创建重复 issue | ✅ 合理，但缺命令 |
| Required labels missing | ✅ 合理 |
| Manifest command count ≠ 10 | ✅ 合理 |
| Audit-only 03/04/05 出现在命令中 | ✅ 合理 |
| OpenSpec validation fails | ✅ 合理，但缺命令 |
| Any step would require backend code mutation | ✅ 合理 |

### 建议补充

| 新增停⛔条件 | 原因 |
|---|---|
| `gh auth status` 失败 | 无法创建 issue |
| body file `01-approve-orchestration.md` 的 SHA 与 runbook 编写时不一致 | 文件可能已被修改 |
| `gh issue list` 返回网络错误 | GitHub 不可达 |
| Pre-publish checklist 有任何一个 check 的实际结果与 Expected 不符 | 门禁失败 |

---

## 改进优先级

| 优先级 | 改进 | 技能 |
|---|---|---|
| **P0** | 增加批准机制定义 + 引用批准包 `backend-openspec-human-approval-packet-2026-05-18.md` | `/zoom-out` |
| **P1** | Pre-publish checklist 每行增加验证命令（governance gate + OpenSpec validate） | `/grill-with-docs` |
| **P1** | 删除 Layer 3 内容（Later Placeholder Map / Publication Order / Evidence Snapshot），改为引用 manifest | `/caveman` |
| **P2** | 增加重复检测的 `gh issue list` 命令 | `/diagnose` |
| **P2** | 增加 `gh auth status` 停⛔条件 | `/diagnose` |
| **P3** | "After Issue 1 Is Created" 编辑流程增加 commit/PR 指导 | `/to-issues` |
| **P3** | 增加 issue 1 的 motivation（为什么它是 approval gate） | `/zoom-out` |

---

## 最终建议

本 runbook 的**操作路径无错误**，可以安全执行。但在 mattpocock/skills 的 "hand-off ready" 标准下，它还需要:

1. 让执行者可以**独立验证**每个 pre-publish checklist 项（给命令，不要只给 expected result）。
2. 让执行者知道**批准长什么样**（谁、在哪里、什么形式）。
3. 删除与 "发布 issue 1" 无关的内容，保持 runbook 的单一焦点。

完成 P0 和 P1 改进后，这份 runbook 即可达到 "交付给人类执行者，无需回来问问题" 的标准。
