## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

本项目的前端页面审查已经从单页修修补补，演变为以 route truth 为核心、按批次执行、带验证与风险收口的工程流程。实战表明，`myweb-audit` 的核心价值并不只是“如何看页面”，而是“如何让多角色审计、局部修复、验证收口在脏仓库与真实运行时中可持续执行”。

当前痛点主要有三类：

1. 状态管理缺失
- 审查是批次化进行的，但没有标准 batch manifest
- 已修复项、待验证项、Shared Impact、staged scope 都依赖主 agent 的上下文记忆

2. 角色输出缺少结构
- 五类固定审计角色边界清楚
- 但 findings 产出缺少 schema，无法稳定去重、聚合、排序

3. 真实环境分支未被设计
- Playwright 报告目录权限、PM2 端口冲突、dirty worktree、agent thread limit 都是常见现实问题
- 当前 Skill 对这些情况没有显式 fallback 流程

## Goals / Non-Goals

- Goals:
  - 定义 page-audit workflow 的状态机与输出契约
  - 明确 agent 与主编排器的职责边界
  - 把 compatibility redirect 纳入同一套审计模型
  - 把验证策略和环境异常处理做成显式规则
- Non-Goals:
  - 重新设计具体页面的视觉或交互
  - 让 agents 完全替代主编排器
  - 重构 Playwright/GitNexus 自身能力

## Decisions

### Decision: Introduce a dedicated `frontend-audit-orchestration` capability

Why:
- 该能力不属于单纯的 `frontend-routing` 或 `accessibility`
- 它描述的是“页面审计如何组织和关闭”的工作流，而不是某一页面功能

Alternatives considered:
- 修改 `frontend-routing`
  - rejected: 会把工作流能力和业务路由语义混在一起
- 修改 `code-quality`
  - rejected: 过于宽泛，无法承载 page-audit 特有的 route/model/redirect 规则

### Decision: Treat audit batches as first-class state

Required fields:
- scope
- batch id / route set
- completed pages
- pending pages
- fixed files
- validation status
- staged scope
- shared impact

Why:
- 页面审计天然是批次化工作
- manifest 是跨会话恢复和多 agent 协作的基础

### Decision: Make role findings structured, not purely narrative

Required structure:
- role
- route
- canonical entry
- severity
- finding
- evidence
- can fix frontend
- shared impact candidate
- dedupe key

Why:
- 多角色 findings 的主成本不在“发现”，而在“去重与归并”
- 结构化输出可以让主 agent 只专注决策与修复

### Decision: Keep agents as audit workers, not closeout orchestrators

Agents SHOULD:
- produce read-only route/page findings
- collect evidence
- suggest repair targets

Main orchestrator MUST:
- merge and dedupe findings
- decide Shared Impact
- edit files
- run validation
- manage staged scope
- run GitNexus closeout checks

Why:
- dirty worktree、staged detect、Playwright fallback、权限提权都要求主流程集中控制

### Decision: Add explicit environment fallback branches

Fallback categories:
- Playwright artifact permission failure
- existing PM2/frontend port conflict
- dirty worktree + staged-scope switching
- agent capacity exhaustion

Why:
- 这些不是偶发噪音，而是高频现实环境
- 不设计 fallback，Skill 会在真实仓库里频繁断流

### Decision: Model compatibility redirects separately from canonical pages

Route classes:
- canonical pages
- detail pages
- compatibility redirects / aliases

Redirect audits MUST cover:
- canonical target
- query preservation
- hash preservation
- auth guard interaction
- post-login destination correctness

Why:
- `/dealing-room`、`/qm` 这类入口不是页面，但它们决定 route truth 是否真正闭环

## Risks / Trade-offs

- 风险：规范过重，导致简单页面修复也需要额外填充结构化状态
  - 缓解：manifest 与 schema 可以最小集实现，先覆盖关键字段

- 风险：把 Skill 写得过强，误导使用者以为 agents 可以替代主收口
  - 缓解：在 spec 中明确主编排器责任不可下放

- 风险：compatibility redirect 审计增加了验证成本
  - 缓解：只对 alias/legacy route 批次启用专项检查

## Migration Plan

1. 先发布 workflow spec 与模板
2. 再更新 `myweb-audit` Skill 文本与示例
3. 最后视需要补最小 manifest/sample schema 文件

## Open Questions

- manifest 是否必须落盘，还是允许会话内临时态
- structured findings 应该用 JSON schema、Markdown frontmatter，还是双格式并存
- Chromium-only / external-frontend reuse 是否作为全局默认，还是按批次覆盖
