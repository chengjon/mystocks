## Context

> **设计方案说明**:
> 本文件用于记录某项变更的设计思路、结构拆分、实现取舍或技术路径，属于方案设计层材料。
> 它不是共享规则正文，也不直接代表当前仓库已落地状态；落地判断应结合 `architecture/STANDARDS.md`、对应 proposal/tasks、审批结果与实际代码验证。

基于 frontend-page-optimization-list 的 34 页基线推进页面优化，不改后端契约真值。

## Goals / Non-Goals
- Goals: 页面优化、状态收口、前端测试补强
- Non-Goals: 后端 API 重构、数据库清理

## Decisions
- 以现有页面范围清单为真值
- API 真值依赖 API 分支提供结论
- 页面改动必须带验证证据

## Risks / Trade-offs
- API 真值未定会阻塞部分页面收口
- 大规模页面修改容易引入回归，必须依赖 E2E

## Migration Plan
按 P0/P1 页面优先推进，再逐步扩展到 P2。

## Open Questions
- 哪些 pending API 可以先用空态收口
