# P3-C5 异常整合 & 大文件拆分：最终状态

> 状态：**P3-C5 核心工作完成**
> 日期：2026-05-19

---

## 一、已完成工作

### 异常迁移（静态扫描归零）

`app/api/` 范围内，以下迁移全部完成，零残留：

| 模式 | 迁移目标 | 结果 |
|------|---------|------|
| `raise HTTPException(...)` | `raise BusinessException(...)` | **0 残留** |
| `except HTTPException:` | `except BusinessException:` | **0 残留** |
| `response_model=APIResponse` | `response_model=UnifiedResponse` | **0 残留** |
| `return APIResponse(...)` | `return create_unified_success_response(...)` | **0 残留** |

### 大文件拆分（15 个文件 → 700 行以下）

| 文件 | 原始行数 | 拆分后 | 伴生文件 |
|------|---------|--------|---------|
| stock_search/stock_search_result.py | 721 | 650 | stock_search_support.py |
| trade/routes.py | 828 | 615 | trade/_responses.py |
| ml.py | 849 | 498 | _ml_responses.py |
| strategy_mgmt.py | 864 | 677 | _strategy_mgmt_responses.py |
| announcement/routes.py | 923 | 594 | announcement/_responses.py |
| tasks.py | 936 | 597 | _task_responses.py |
| notification.py | 942 | 644 | _notification_responses.py |
| monitoring_analysis.py | 749 | 524 | _monitoring_analysis_responses.py |
| signal_monitoring/signal_history_response.py | 786 | 669 | signal_monitoring/_signal_history_responses.py |
| data_quality.py | 811 | 546 | _data_quality_responses.py |
| system/system_health.py | 854 | 689 | system/_system_health_responses.py |
| data_lineage.py | 954 | 569 | _data_lineage_responses.py |
| data_source_config.py | 1030 | 673 | _data_source_config_responses.py |
| technical_analysis.py | 1004 | 570 | _technical_analysis_responses.py + _technical_analysis_models.py |
| market/market_data_request.py | 985 | 646 | market/_market_data_request_responses.py |

### 提交记录

| Commit | 内容 |
|--------|------|
| `1a60d3c7f` | strategy_management package exception migration |
| `cd43f3fcf` | batch 2 exception migration |
| `dc21371ba` | batch 3 exception migration |
| `8cd5097d0` | batch 4 exception + response contract migration |
| `344af1810` | metrics.py APIResponse → UnifiedResponse |
| `9f74c8481` | data_source_registry.py exception canonicalization |
| `ca4e80e25` | split 8 large files under 700-line guardrail |
| `ed723bb22` | complete P3-C5 exception migration in system_health.py |

### 范围外残留（非 P3-C5 范围）

以下 `HTTPException` 位于 `app/api/` 之外，属于基础设施层或遗留路由层，**保留不改**：

| 文件 | 数量 | 原因 |
|------|------|------|
| `app/core/security.py` | 2 | FastAPI auth 依赖 HTTPException |
| `app/core/validation.py` | 12 | 输入验证，FastAPI 4xx 流程 |
| `app/core/exception_handlers.py` | 2 | 异常处理器，必须 catch HTTPException |
| `app/services/algorithm_service.py` | 6 | Service 层，非 API 路由 |
| `app/routes/sse_monitoring.py` | 8 | 遗留路由，不在 app/api/ 范围 |

---

## 二、后续独立事项：UnifiedResponse 契约守卫

Pre-commit hook 中的 `unified_response_contract_guard` 要求所有 HTTP 路由声明 `response_model=UnifiedResponse[...]`。

**当前状态**：全仓库 266 个路由未通过此守卫。这些路由是历史遗留，非本次引入。

### 处理选项

1. **渐进迁移**（推荐）：后续迭代中逐步将 266 个路由迁移到 UnifiedResponse
2. **守卫豁免**：修改守卫脚本，对 pre-existing non-compliant routes 放行
3. **降级为 WARNING**：将守卫从 FAILURE 改为 WARNING，不阻塞提交

此项独立于 P3-C5，建议作为单独任务跟踪。
