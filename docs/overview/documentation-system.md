# Documentation System

> **权威来源声明**:
> 本文件描述仓库文档系统的 canonical trunk、优先级、生命周期分类与 reader routing 规则。
> 它服务于 `govern-documentation-truth-lifecycle`，是当前文档治理的主干说明文档。

## 1. Why This Exists

仓库文档面已经出现多种并存角色：

- canonical guidance and rules
- active implementation guides
- approved change proposals
- historical reports and verification evidence
- stale snapshots that仍然长得像“当前真相”

如果没有 trunk map，人和 AI 都容易把历史报告、旧规划、过期 API 说明误读为 current truth。

这个文件的作用就是把文档系统从“看起来都像活文档”改为“先看 trunk，再看 supporting/report”。

## 2. Canonical Trunk Map

| Concern | Canonical trunk | Precedence rule |
|---|---|---|
| 仓库级共享规则 | [`architecture/STANDARDS.md`](../../architecture/STANDARDS.md) | 高于 `AGENTS.md`、`CLAUDE.md`、普通文档说明 |
| 当前 capability truth | [`openspec/specs/`](../../openspec/specs) | 作为当前已建成/已治理能力的正式要求 |
| Approved pending change truth | [`openspec/changes/<change-id>/`](../../openspec/changes) | 在能力正式归档前，proposal/design/tasks/deltas 以该 change 为准 |
| API contract truth | `FastAPI routes + Pydantic Schema + /openapi.json` | Markdown API 文档不得覆盖真实契约 |
| Operations / runbooks | [`docs/operations/`](../operations) | 当前运行、部署、值班资料从此处进入 |
| Testing guidance | [`docs/testing/`](../testing) | 当前测试策略、E2E、质量门禁从此处进入 |
| Historical evidence | [`docs/reports/`](../reports) 或 `archive/docs/` | 仅作历史证据，不作 current truth |

说明：

- `docs/README.md` 是导航入口，不是并行真相层
- 子树 README / INDEX 只能帮助读者进入 trunk，不应自我提升为 parallel truth

## 3. Lifecycle Classes

每个保留的文档家族都应落入以下类别之一：

- `canonical`: authoritative active trunk
- `supporting`: active helper below a canonical trunk
- `report`: historical evidence or verification output
- `plan`: future-facing planning material
- `generated_reference`: generated export/listing/reference artifact
- `archive_candidate`: historical material that should leave active trees
- `delete_candidate`: redundant material removable after gates pass

只有 `canonical` 允许承担 current truth 语义。

## 4. Four Governance Principles

### 4.1 Trunk-first, not leaf-first

先定义 concern 的 canonical trunk，再处理具体 stale leaf。

禁止一上来就逐份修改旧文档措辞，而不先声明“这个 concern 现在到底以什么为准”。

### 4.2 Delete invalid/stale docs aggressively

一旦 canonical replacement 存在且 link / retention gate 已满足，默认策略是移除历史噪音，而不是无限补免责声明。

### 4.3 Keep only current, architecturally truthful docs

同一 concern 只允许一个 active truth source。

report、plan、legacy guide、历史快照都不能继续与 canonical trunk 并列表达“当前状态”。

### 4.4 AI-friendly hierarchy

文档结构必须让 AI 和人都能快速判断：

- 这是 canonical 还是 supporting
- 这是 current truth 还是 historical evidence
- 这是应保留、应归档，还是应删除

## 5. Reader Routing Rules

### 5.1 When You Need Governance Truth

优先去 [`architecture/STANDARDS.md`](../../architecture/STANDARDS.md)。

### 5.2 When You Need Current Feature Truth

优先去 [`openspec/specs/`](../../openspec/specs)。

### 5.3 When You Need Approved In-Flight Change Truth

优先去对应的 [`openspec/changes/<change-id>/`](../../openspec/changes)。

### 5.4 When You Need API Truth

优先回到 FastAPI routes、Pydantic schema、导出的 OpenAPI。

`docs/api/README.md` 只是导航中心，不是契约源。

### 5.5 When You Need Historical Evidence

进入 [`docs/reports/README.md`](../reports/README.md) 或 archive 区域，并明确按历史快照使用。

## 6. Trunk-First Decision Workflow

对任意文档 cluster，先做这四步：

1. 识别 canonical trunk
2. 把 branch documents 映射回该 trunk
3. 赋予决策状态
4. 再执行迁移、归档或删除

允许的决策状态：

- `keep-canonical`
- `keep-supporting`
- `merge-into-trunk`
- `archive`
- `delete`
- `needs-replacement`

## 7. Delete Gate

一个文档或文档家族只有在以下条件全部满足时，才允许删除：

- canonical replacement / canonical trunk 已明确存在
- inbound references / indexes / README links 已更新或显式退役
- 该文档不再承担 audit retention、active migration 或 compatibility communication
- decision register 明确标记为 `delete`

否则，一律不删。

## 8. Default Action Bias

当 stale 文档已经有 canonical replacement 且没有保留义务时，默认动作偏向：

```text
delete/archive > rewrite
```

`rewrite` 只应作为短期过渡手段，而不是长期治理方式。

## 8.1 Default Remediation Order

当问题是“存在 stale 文档或重复入口”时，默认执行顺序是：

1. 先识别 canonical trunk
2. 先修 root routing 与 active links
3. 再执行 bounded archive/delete batch
4. 只有过渡期确实需要 reader routing 时，才保留 rewrite

这意味着文档治理默认不再采用“逐份补免责声明”作为主策略。

## 9. Recommended Execution Order

当前文档治理按以下顺序推进：

1. canonical documentation system
2. documentation taxonomy / audit tooling
3. inventory / decision register
4. bounded cleanup waves

建议 wave 顺序：

1. `docs/api/`
2. `docs/reports/`
3. `docs/guides/`
4. `docs/overview/`, `docs/operations/`, `docs/testing/`

## 10. Related Files

- [`docs/README.md`](../README.md)
- [`architecture/STANDARDS.md`](../../architecture/STANDARDS.md)
- [`openspec/project.md`](../../openspec/project.md)
- [`docs/guides/documentation/CANONICAL_TRUNK_ADMISSION_GUIDE.md`](../guides/documentation/CANONICAL_TRUNK_ADMISSION_GUIDE.md)
- [`openspec/changes/govern-documentation-truth-lifecycle/`](../../openspec/changes/govern-documentation-truth-lifecycle)
