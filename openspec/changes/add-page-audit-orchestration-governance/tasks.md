## 1. Specification

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [x] 1.1 Add a new `frontend-audit-orchestration` capability spec for page-audit workflow governance
- [x] 1.2 Define batch manifest requirements and closeout evidence requirements
- [x] 1.3 Define structured role-output requirements for the five fixed audit roles
- [x] 1.4 Define orchestrator vs sub-agent responsibility boundaries
- [x] 1.5 Define environment fallback requirements for Playwright, PM2 conflict, staged-scope switching, and agent-capacity exhaustion
- [x] 1.6 Define compatibility redirect audit requirements
- [x] 1.7 Define verification-policy parameters for Chromium-only and external frontend reuse

## 2. Skill Alignment
- [x] 2.1 Update `.claude/skills/myweb-audit/SKILL.md` to align with the approved workflow spec
- [x] 2.2 Add a minimal batch manifest template and structured findings example
- [x] 2.3 Add a closeout checklist template for syntax, type-check, PM2, Chromium E2E, and staged GitNexus detection

## 3. Validation
- [x] 3.1 Validate the OpenSpec change with `openspec validate add-page-audit-orchestration-governance --strict`
- [x] 3.2 Review the proposal with stakeholders before any implementation starts
