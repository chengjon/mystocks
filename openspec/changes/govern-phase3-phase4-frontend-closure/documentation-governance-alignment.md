# Documentation Governance Alignment

> **对齐记录说明**:
> 本文档用于记录 `govern-phase3-phase4-frontend-closure` 与已批准文档治理变更之间的执行对齐关系。
> 它不是把两个 OpenSpec 变更合并为一个变更，而是声明当前前端结构收口任务在文档治理口径上的上游依赖。

**Generated:** 2026-04-08  
**Current change:** `govern-phase3-phase4-frontend-closure`  
**Upstream approved change:** `govern-documentation-truth-lifecycle`

## 1. Alignment Decision

当前前端收口任务可以吸收以下内容作为执行口径，但不应把两个 OpenSpec change 目录直接合并：

- `govern-documentation-truth-lifecycle` 保持为独立的文档治理能力变更
- `govern-phase3-phase4-frontend-closure` 将其视为上游治理约束与后续执行顺序来源
- 当前前端任务中涉及的 repo-truth 报告、execution matrix、retirement checklist，应按 trunk-first 文档治理口径继续整理

## 2. Approved Governance Inputs To Carry Forward

以下内容已作为当前任务的上游已批准输入：

1. 已批准 `govern-documentation-truth-lifecycle`
2. 文档治理策略从“逐份修旧文档”切换为“主干优先、自上而下”
3. 四条核心原则：
   - trunk-first, not leaf-first
   - delete invalid/stale docs aggressively
   - keep only current, architecturally truthful docs
   - AI-friendly hierarchy
4. canonical truth trunks 已定义：
   - `architecture/STANDARDS.md`
   - `openspec/specs/`
   - `openspec/changes/<change-id>/`
   - `FastAPI routes + Pydantic Schema + /openapi.json`
   - `docs/operations/`
   - `docs/testing/`
   - `docs/reports/` / `archive/docs/` 仅作为 historical evidence
5. 默认 remediation bias 改为 `delete/archive > rewrite`
6. 推荐执行顺序：
   - 先 canonical trunk system
   - 再 documentation taxonomy / audit
   - 再 inventory / decision register
   - 最后按 wave 执行清理

## 3. How This Changes The Current Frontend Closure Work

这对当前前端收口任务的影响不是“立即多做一批前端代码改动”，而是：

- 当前任务产出的 repo-truth 报告继续保留为 `report/evidence` 角色，不冒充 canonical truth
- 涉及前端历史文档、旧 execution notes、legacy route说明的后续整理，默认不再走“逐份补免责声明”路线
- 若后续要清理 `docs/reports/2026-04-07-*`、旧前端 restructure 文档、历史 API / route notes，应先回到 `govern-documentation-truth-lifecycle` 的 trunk / taxonomy / decision register 流程
- 当前变更只记录这种依赖关系，不替代文档治理变更本身的任务执行

## 4. Graphiti Memory Status

用户提供的 Graphiti 记录状态如下，作为本轮执行上下文保留：

- group: `mystocks_spec`
- episode: `16801e38-bc4a-459b-8458-3db32e77962b`
- ingest: `processing`
- last_error: `null`

该状态属于上下文跟踪信息，不构成 OpenSpec 验证结果，也不替代仓库内正式治理产物。
