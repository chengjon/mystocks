## Context
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
