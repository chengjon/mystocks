# Change: Add Page-Audit Orchestration Governance

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why

当前仓库已经形成了基于 `myweb-audit` Skill + Agents 的前端逐页审查实践，但这套能力在真实执行中仍主要依赖主 agent 的人工编排与上下文记忆：

- batch 边界、已审页面、staged scope、验证状态缺少统一 manifest
- 五类审计角色有清晰职责，但缺少结构化产出 schema，去重与合并仍依赖人工整理
- agents 适合只读审查，不适合直接承担 dirty worktree、Playwright 环境冲突、GitNexus staged closeout 等收口动作，但当前规范未显式区分
- 兼容重定向入口（如 `/dealing-room`、`/qm`）不属于普通页面，却在实际路由审计里占据重要位置，现有审计模型未把这类入口单独建模
- Playwright 权限、PM2 端口冲突、agent thread limit 等环境异常在真实执行中频繁出现，但 Skill 设计里没有标准降级分支

如果不把这些经验固化为可审计能力，`myweb-audit` 将继续停留在“方法说明书”层，而不是可重复、可跨会话、可恢复的前端审计编排规范。

## What Changes

- 为页面审计工作流增加 batch manifest 与 closeout 状态模型
- 为 `route-inventory`、`functional-audit`、`data-state-audit`、`visual-artdeco-audit`、`responsive-a11y-audit` 定义统一结构化输出 schema
- 明确主 agent 与 sub-agent 的职责边界，防止 agents 越界承担 staged/git/验证收口
- 为环境异常增加标准 fallback 分支，包括 Playwright 权限、PM2 端口冲突、dirty worktree staged 切换、agent 容量耗尽
- 将 `Shared Impact` 升级为前置判定，而不是报告尾部补充项
- 将 compatibility redirect/alias 路由纳入专门的审计模型
- 为 Chromium-only、targeted/full verification、复用现有前端服务等策略提供可声明的执行参数

## Scope Boundary

This proposal governs the page-audit workflow itself, not any single routed page implementation.

In scope:

- `myweb-audit` 这类前端页面审计 Skill 的流程设计
- agent 角色与主编排器的协作契约
- 审计批次状态、结构化 findings、closeout 证据、redirect 审计模型
- 页面审计所需的运行时异常处理与验证策略开关

Out of scope:

- 具体业务页面的新增 UI 设计或重构
- 后端 API 契约变更
- GitNexus 能力本身的设计变更
- Playwright 框架级配置重构
- 对现有 page audit 结果的追溯性重跑

## Impact

- Affected specs:
  - `frontend-audit-orchestration` (new)
- Affected code / docs:
  - `.claude/skills/myweb-audit/`
  - 审计状态模板、输出 schema 示例、closeout 模板
  - 可能触及的辅助脚本或文档说明
- Risk:
  - medium
  - 原因是该变更会影响后续前端页面审计的操作方式与 agent 分工，但不直接改业务运行时

## Success Criteria

- 页面审计批次具备可恢复的 manifest 与 closeout 状态模型
- 五类审计角色的 findings 可以结构化去重，而不是仅依赖自由文本合并
- 主 agent / sub-agent 的收口责任边界被明确规定
- 环境异常有标准降级分支，避免审计流程因权限/端口/容量问题中断
- compatibility redirect/alias 路由被纳入显式审计对象
- Chromium-only 和复用现有前端服务等验证策略能被声明化管理
