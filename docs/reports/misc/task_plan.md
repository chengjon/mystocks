# Task Plan: Security and Data-Access Remediation

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## Goal
Implement and verify the non-large-file code-review fixes for security and data-access issues using minimal, targeted code changes.

## Phases
- [x] Phase 1: Plan and setup
- [x] Phase 2: Research/gather information (12 issues mapped with file:line precision)
- [x] Phase 3: Execute/build
  - [x] 3A: Quick wins — sensitive logs, dead code, CORS (issues #1,7,8,9,10) ✅
  - [x] 3B: SQL injection hardening (issues #2,3,4,11) ✅
  - [x] 3C: Redis migration — revoked tokens + CSRF (issues #5,6,12) ✅
- [x] Phase 4: Review and deliver

## Key Questions
1. ~~Which high-risk issues are currently present?~~ → 12 issues mapped in notes.md
2. ~~Which existing secure patterns should be reused?~~ → PostgreSQL parameterized queries, Redis singleton, config-driven CORS
3. ~~Which tests must be updated?~~ → test_csrf_protection.py updated with Redis-aware helper

## Decisions Made
- Use planning-with-files workflow: task_plan.md + notes.md + deliverable markdown.
- Prioritize security-critical fixes first.
- Keep patch scope minimal and localized.
- Execute in 3 sub-phases: quick wins → SQL hardening → Redis migration.
- TDengine SQL: use input validation/sanitization (not parameterization) due to driver limitations.
- CSRF Redis migration: keep same public API, update tests to use public API instead of internal dict.
- Redis migrations use graceful fallback to in-memory when Redis unavailable.

## Errors Encountered
- Explore subagent call failed with provider/model routing error: worked around by reading files directly.

## Status
**COMPLETED** - All 12 issues remediated. Deliverable report generated.
