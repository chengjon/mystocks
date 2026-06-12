# P3-C5: 核心异常统一迁移 — 阶段性进度报告

> **任务 ID**: #28 | **状态**: 进行中 | **分支**: `wip/root-dirty-20260403` | **日期**: 2026-05-18
>
> **⚠️ 本文档为阶段性进度报告，非完成报告。** 截至 2026-05-18，静态扫描仍有 ~100 处 `raise HTTPException`、~26 处 `except HTTPException`、4 处 `response_model=APIResponse`、8 处 `return APIResponse(...)` 残留。详见第三节"剩余工作"。

## 一、任务目标

将 `web/backend/app/api/` 下所有裸 `HTTPException` 调用迁移到 `app/core/exceptions.py` 定义的规范异常层级（`BusinessException` 及其子类），同时修复阻碍提交的 `response_model=UnifiedResponse` 契约守卫违规。

**FUNCTION_TREE 对齐位置**: 该任务横跨所有 10 个功能域的后端 API 层，不改变功能边界，仅统一异常和响应格式。主要涉及：
- {#domain-03} 策略管理与回测（batch 1）
- {#domain-04} 风险管理与监控（stop_loss、monitoring）
- {#domain-05} 投资组合与交易（trade、trading_runtime）
- {#domain-07} 高级分析与 AI（ml、algorithms）
- {#domain-08} 系统管理与配置（system）
- {#domain-09} 数据存储与管理（data_source、cache）
- {#domain-02} 技术分析与指标（indicator_registry）
- {#domain-01} 市场数据与行情（market_v2、tdx、tradingview）

## 二、已完成工作

### 已提交批次

| 批次 | Commit | 文件数 | 内容 |
|------|--------|--------|------|
| 1 | `1a60d3c7f` | 5 | strategy_management 包（已使用 UnifiedResponse） |
| 2 | `cd43f3fcf` | 14 | _technical_patterns、algorithms、backup、contract、dashboard_data_source、notification、trade/execution_tracking、v1/strategy/*、v1/system/*、v1/trading |
| 3 | `dc21371ba` | 7 | _monitoring_portfolio、algorithms/get_algorithms_module、contract/routes、trade/reconciliation、v1/analysis/backtest、v1/strategy/indicators、v1/strategy/ml_workbench |
| 4 | `8cd5097d0` | 5 | indicator_registry、stock_search/get_rate_limits_status、tradingview、trading_runtime、system/get_system_architecture（**含 UnifiedResponse 契约修复**） |

**合计已提交**: 31 个文件，30 个文件涉及异常迁移，其中 5 个额外完成了 `APIResponse→UnifiedResponse` 契约对齐。

### 迁移模式

1. **异常迁移**: `raise HTTPException(status_code=N, detail=X)` → `raise BusinessException(detail=X, status_code=N)` + `except HTTPException:` → `except BusinessException:`
2. **响应契约修复**（batch 4 新增）: `response_model=APIResponse` → `response_model=UnifiedResponse`；`return APIResponse(...)` → `return create_unified_success_response(...)`；裸 `return {...}` → `return create_unified_success_response(data=...)`

## 三、剩余工作

### 3.1 已编辑但未提交（9 文件，< 700 行）

需完成与 batch 4 相同的 **组合修复**（异常 + UnifiedResponse 契约）：

| 文件 | 行数 | 领域 | 说明 |
|------|------|------|------|
| `dashboard.py` | 435 | 通用 | 34 个路由，工作量最大 |
| `risk/stop_loss.py` | 647 | {#domain-04} | 13 个路由 `response_model=Dict` |
| `v1/pool_monitoring.py` | 468 | {#domain-05} | 无 response_model |
| `wencai.py` | 630 | {#domain-01} | 部分有 response_model |
| `tdx.py` | 538 | {#domain-01} | 部分有 response_model |
| `industry_concept_analysis.py` | 543 | {#domain-02} | 部分有 response_model |
| `market_v2.py` | 562 | {#domain-01} | 无 response_model |
| `realtime_market.py` | 684 | {#domain-01} | 无 response_model |
| `signal_monitoring/get_signal_statistics.py` | 512 | {#domain-06} | 部分有 response_model |

### 3.2 已编辑但未提交（8 文件，≥ 700 行）

受 **700 行红线**阻塞，需先做文件拆分/瘦身：

| 文件 | 行数 | 超出 |
|------|------|------|
| `data_lineage.py` | 954 | +254 |
| `data_source_config.py` | 1030 | +330 |
| `market/market_data_request.py` | 985 | +285 |
| `monitoring_analysis.py` | 749 | +49 |
| `signal_monitoring/signal_history_response.py` | 786 | +86 |
| `stock_search/stock_search_result.py` | 722 | +22 |
| `system/system_health.py` | 854 | +154 |
| `technical_analysis.py` | 1004 | +304 |

## 四、下一步计划

### Phase A: 完成剩余 < 700 行文件（优先级高）

1. 逐文件完成 **组合修复**（异常 + UnifiedResponse）
2. 按领域分批提交，每批 2-3 个文件
3. 预计新增 **2-3 个 commit**

### Phase B: ≥ 700 行文件拆分（独立任务）

1. 先对 8 个超限文件做行数瘦身（提取 helper、拆分路由等）
2. 瘦身后再应用异常迁移
3. 建议拆分为独立 task card

### Phase C: 收尾验证

1. 运行全量路由表生成脚本，确认 0 个 `HTTPException` 残留
2. 更新 FUNCTION_TREE.md 中受影响域的入口说明（如有必要）
3. 关闭 Issue #77 / Task #28

## 五、风险与注意事项

1. **前端兼容性**: `APIResponse→UnifiedResponse` 增加了 `code` 字段、`errors` 字段，前端消费方需确认是否解析这些新字段（当前前端多通过 `response.data` 读取，影响较小）
2. **response_model 过滤**: FastAPI 的 `response_model` 会过滤返回值中不在模型中的字段。所有迁移后的路由返回 `create_unified_success_response(data=...)` 格式，确保与 `UnifiedResponse` 模型匹配
3. **组合修复范围**: 不做未请求的重构，仅修复阻碍异常迁移提交的 response_model 问题
