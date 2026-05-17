# ADR-0002: API Flat→Package 迁移策略

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **Status**: Proposed
> **Date**: 2026-05-16
> **Decision makers**: Backend team

## Context

`app/api/` 下存在 64 个 flat `.py` 文件和 20 个 package 目录，其中 10 个功能域同时存在两种形态。`router_registry.py` 中出现了双注册 bug（`announcement` 被注册两次：第 78 行 via VERSION_MAPPING + 第 96 行直接注册）。

当前重叠域：

| 域 | Flat 文件 | Package 目录 | 复杂度 |
|----|----------|-------------|--------|
| announcement | `announcement.py` | `announcement/` | 低（1+2） |
| market | `market.py` + `market_v2.py` | `market/` | 中（2+5） |
| algorithms | `algorithms.py` | `algorithms/` | 低（1+5） |
| indicators | `indicators.py` | `indicators/` | 低（1+4） |
| multi_source | `multi_source.py` | `multi_source/` | 低（1+2） |
| signal_monitoring | `signal_monitoring.py` | `signal_monitoring/` | 低（1+4） |
| stock_search | `stock_search.py` | `stock_search/` | 低（1+6） |
| strategy_management | `strategy.py` + `strategy_management.py` + `strategy_mgmt.py` | `strategy_management/` | 高（3+6） |
| system | `system.py` | `system/` | 低（1+4） |
| backup_recovery_secure | `backup_recovery_secure.py` | `backup_recovery_secure/` | 低（1+4） |

另外，策略域和风控域存在额外的 flat 文件：
- 策略: `strategy.py`, `strategy_management.py`, `strategy_mgmt.py` + `strategy_management/` package
- 风控: `risk_management.py`, `risk_management_core.py`, `risk_management_v31.py` + `risk/`, `risk_v31/` packages

## Decision

**原则**: Package 目录是 canonical 目标形态。Flat 文件作为过渡 shim 保留，直到 package 功能完整覆盖。

**迁移优先级**（按复杂度递增）:

1. **立即修复**: 移除 `announcement` 双注册 bug（删除 `router_registry.py:96` 的重复注册）
2. **低复杂度收口** (1-2 周): announcement, algorithms, indicators, multi_source, stock_search, system, backup_recovery_secure
3. **中复杂度收口** (2-4 周): market, signal_monitoring
4. **高复杂度收口** (需 OpenSpec): strategy_management (3 flat → 1 package), risk (3 flat → 2 package)

**退出条件**（每个域必须满足）:
- package 目录覆盖 flat 文件的所有路由
- flat 文件无 import 引用（通过 `grep -r "from.*import" app/ --include="*.py"` 确认）
- FUNCTION_TREE.md 标记域为 migrated
- 删除 flat 文件并更新 `router_registry.py`

## Consequences

**Positive**:
- 消除双注册和路由冲突风险
- 目录结构清晰，每个功能域一个入口
- 符合 STANDARDS.md §三.2"没有退出条件的迁移禁止启动"

**Negative**:
- 前端和测试可能引用旧路由路径
- 迁移过程中需要并行维护两种入口
- 高复杂度域（策略/风控）需要更长的兼容期
