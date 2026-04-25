# MyWeb Audit Changelog

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## v1.4 - 2026-04-25

- Added dedicated agent specs for all fixed audit roles
- Added environment prerequisites, execution surfaces, and environment fallback rules
- Added Quick Mode guidance for single-page checks
- Added explicit repair approval gate before fixes
- Aligned responsive checks to desktop-supported widths: `1920`, `1440`, `1280`
- Added structured manifest fields for execution surface, verification strategy, and repair approval
- Added shared-impact fields and `dedupe_key` guidance to the findings schema example
- Added formal `findings-schema.json` for machine validation
- Added closeout severity-resolution note and approval-record check
- Added artifact output conventions for file-based audit runs
