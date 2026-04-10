## Context

> **设计方案说明**:
> 本文件用于记录某项变更的设计思路、结构拆分、实现取舍或技术路径，属于方案设计层材料。
> 它不是共享规则正文，也不直接代表当前仓库已落地状态；落地判断应结合 `architecture/STANDARDS.md`、对应 proposal/tasks、审批结果与实际代码验证。

本任务聚焦底层资产真值，不负责页面实现和 API 可用性映射。

## Goals / Non-Goals
- Goals: 盘点、清理、优化、说明保留理由
- Non-Goals: 页面重构、API 前端映射治理

## Decisions
- 先盘点再清理
- 所有删除动作必须说明功能树状态和删除依据
- 运行配置以实际使用情况为准

## Risks / Trade-offs
- 误删兼容资产风险高，必须保守
- 清理收益和验证成本需要权衡

## Migration Plan
先形成矩阵，再做小步修复。

## Open Questions
- Redis、Mongo、历史兼容配置的真实使用边界
