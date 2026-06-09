# MyStocks 后端开发审计报告

> **权威来源声明**:
> 本文件是后端质量审计快照，不是仓库共享规则的唯一事实来源。
> 涉及迁移收口、删除判定、指标口径和审批门禁时，以 `architecture/STANDARDS.md`、`openspec/AGENTS.md`、`docs/standards/technical-debt-governance-charter-v1.md` 与当前代码为准。
> 本文件的优先级建议必须先经过对应子文档复核、双判定表和必要的 OpenSpec 审批后才能执行。

> **审计入口**: `docs/FUNCTION_TREE.md` → 10 个业务域 → 六类入口 → 实际代码
> **规范基准**: `architecture/STANDARDS.md`
> **审计日期**: 2026-05-14
> **审计范围**: `web/backend/` + `src/` 核心模块

---

## 子文档索引与执行状态

| 编号 | 子文档 | 主题 | 当前状态 |
|------|--------|------|----------|
| A | `docs/reports/quality/backend-logging-fix-2026-05-14.md` | 日志整改 | 已完成关键事实修正，`print()` 门禁复核为 0 |
| B | `docs/reports/quality/backend-residual-files-inventory-2026-05-14.md` | 残留文件清册 | 已重扫当前工作树，剩余候选需双判定 |
| C | `docs/reports/quality/api-flat-to-package-migration-2026-05-14.md` | API flat 到 package 迁移 | 已复核当前事实，只能作为 OpenSpec 输入 |
| E | `docs/reports/quality/backend-singleton-to-di-2026-05-14.md` | Singleton 到 DI | 已补生命周期分类，只能作为 OpenSpec 输入 |
| F | `docs/reports/quality/backend-core-split-plan-2026-05-14.md` | Core 拆分 | 已补 wrapper/OpenSpec 边界，只能作为 OpenSpec 输入 |
| G | `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md` | 健康端点收敛 | 已补 route table/OpenAPI/OpenSpec 边界，只能作为 OpenSpec 输入 |
| H | `docs/reports/quality/backend-strategy-domain-governance-2026-05-14.md` | 策略域治理 | 已补当前注册/消费者/OpenSpec 边界，只能作为 OpenSpec 输入 |
| I | `docs/reports/quality/backend-risk-domain-governance-2026-05-14.md` | 风控域治理 | 已补当前注册/消费者/OpenSpec 边界，只能作为 OpenSpec 输入 |

复核报告: `docs/reports/quality/backend-audit-documents-review-2026-05-15.md`。

---

## 一、总体评估

项目后端整体架构意识良好 — 响应标准化、健康探针、Prometheus 指标、Request ID 全链路追踪、API 版本化管理等关键能力已建立。但在 **迁移收口、代码清洁度、日志规范化、核心目录治理** 四个维度存在显著技术债，与 STANDARDS.md 的要求有差距。

---

## 二、红线合规检查

### 2.1 响应标准化 ✅ 已基本达标，但未完全收口

`app/core/responses.py` 提供了完善的 `UnifiedResponse` 模型，含 `success` / `code` / `message` / `data` / `request_id` / `errors` 字段。快捷函数 `ok()`、`not_found()`、`server_error()` 等覆盖了主要错误场景。

**问题**：并非所有端点都使用统一响应。部分旧端点直接返回 `{"status": "ok", "service": "xxx"}`，未包装为 `UnifiedResponse`：

| 文件 | 问题 |
|---|---|
| `api/monitoring_old/routes.py` | `return {"status": "ok", "service": "monitoring"}` |
| `api/technical/routes.py` | `return {"status": "ok", "service": "technical"}` |
| `api/announcement/routes.py` | `return {"status": "ok", "service": "announcement"}` |

ResponseFormatMiddleware 会自动包装这些裸响应，但依赖中间件不如显式使用 `UnifiedResponse` 可靠。

### 2.2 日志规范化 ❌ 未达标

STANDARDS.md 明确规定：

> 严禁使用 `print`，必须统一使用 `from app.core.logger import logger`

实际情况：

- **当前存在 `app/core/logger.py`**，作为 `STANDARDS.md` 要求的统一 facade
- `PerformanceMiddleware` 使用 `structlog`，与其他模块的 `logging` 不统一
- 2026-05-15 复核：`web/backend/app` 下 `print()` 扫描结果为 **0 处**，`mock/coverage_report.py` 不再保留 `print()` 调用

### 2.3 单例防御 ⚠️ 部分达标，但 singleton 泛滥

STANDARDS 要求：`所有 global 变量必须在模块顶层显式初始化为 None`

统计 20+ 个文件使用 `global` 实现单例模式，多数已在模块顶层初始化为 `None`，符合红线。但 pattern 本身存在风险：

- `app/adapters/` 下有 6 个 adapter 各自实现自己的 `get_xxx()` 单例
- `app/services/` 下有 15+ 个 service 各自维护单例
- 缺少统一的依赖注入或 service locator

### 2.4 导入安全性 ⚠️ 废弃模块残留（已重扫）

> **2026-05-15 更新**: 子文档 B 已重扫当前工作树。当前未发现 `.bak`、`.backup`、`.old.py`、`.before_*` 类备份文件；剩余候选为 4 个 `_new.py` 过渡文件和 1 个 `monitoring_old/` 旧目录，均需双判定后再决定后续动作。

**当前未发现**:
- 当前未发现：`api/strategy_management.py.backup`、`api/risk_management.py.bak`、`api/data_source_config.py.backup`
- 当前未发现：`api/mystocks_complete.py.bak`、`api/data_source_config.old.py`
- 当前未发现：`services/data_adapter.py.backup.20260130`、`services/watchlist_service.py.bak2/.bak3/.before_schema_update`

**仍需处理**:

| 路径 | 类型 | 状态 |
|---|---|---|
| `api/monitoring_old/` | 旧模块目录 | 待 G 方案判定后处理 |
| `api/auth_compat.py` | 兼容 shim | 功能性兼容面，不纳入残留删除候选 |
| `services/risk_management_new.py` | 无退出条件的新版 | 需迁移计划 |
| `services/data_adapter_new.py` | 无退出条件的新版 | 需迁移计划 |
| `services/data_api_new.py` | 无退出条件的新版 | 需迁移计划 |
| `api/data/data_api_new.py` | 无退出条件的新版 | 需迁移计划 |

---

## 三、架构分层检查

参照 STANDARDS.md 的分层约束（Core → Domain → Infra → Application → UI/API）：

| 层 | 实际情况 | 评价 |
|---|---|---|
| **API 层** (`app/api/`) | 100+ 文件，flat `.py` 与 package 目录混合 | ⚠️ 迁移中但未收口 |
| **Service 层** (`app/services/`) | 80+ 文件，含 `.bak`, `.backup`, `_new.py` | ❌ 技术债严重 |
| **Core 层** (`app/core/`) | 60+ 文件全平铺，`database_*.py` 类文件 7 个 | ⚠️ 目录膨胀 |
| **Models 层** (`app/models/`) | 22 个文件，结构相对整洁 | ✅ 基本健康 |
| **Schemas 层** | `app/schema/` + `app/schemas/` 双目录并存 | ❌ 重复真相源 |

---

## 四、迁移收口问题（与 STANDARDS.md §三直接冲突）

### 4.1 API 层：Flat 文件与 Package 目录并存

这是最突出的迁移债。VERSION_MAPPING 已定义了各模块的 canonical 路由，但目录结构反映迁移进度不一致：

| 功能域 | Package 目录 | 同层 flat 文件 | 状态 |
|---|---|---|---|
| 市场数据 | `market/` | `market.py`, `market_v2.py` | 未收口 |
| 公告 | `announcement/` | `announcement.py` | 未收口 |
| 策略管理 | `strategy_management/` | `strategy.py`, `strategy_management.py`, `strategy_mgmt.py` | 严重混乱 |
| 风控 | `risk/`, `risk_v31/` | `risk_management.py`, `risk_management_core.py`, `risk_management_v31.py` | 严重混乱 |
| 监控 | `monitoring_old/` | `monitoring.py`, `monitoring_analysis.py`, `monitoring_watchlists.py` | 未收口 |

STANDARDS.md §三.2 要求：

> 没有退出条件的迁移禁止启动

上述场景中 flat `.py` 和 package 目录长期共存，未见明确的退出计划。

### 4.2 服务层：临时文件残留

违反了 §三.3「临时命名必须可追溯、可退场」：

| 文件 | 类型 |
|---|---|
| `risk_management_new.py` | 无退出条件的新版 |
| `risk_management_2.py` | 无退出条件的2版 |
| `data_adapter_new.py` | 标记为 `_new` 但无收口日期 |
| `data_api_new.py` | 标记为 `_new` 但无收口日期 |

### 4.3 Core 层：重复文件

违反了 §三.1「同一职责只允许一个主实现」：

| 文件组 | 重叠项 |
|---|---|
| `exception_handler.py` + `exception_handlers.py` + `global_exception_handlers.py` | 异常处理 ×3 |
| `validation.py` + `validators.py` + `validation_models.py` | 校验 ×3 |
| `cache.py` (api/) + `cache_manager.py` + `cache_utils.py` + `cache_integration.py` + `cache_eviction.py` + `cache_prewarming.py` | 缓存 ×6 |

---

## 五、最佳实践偏离项

### 5.1 依赖注入缺失

项目使用 FastAPI，也已有大量 `Depends()` 使用点，但 `global` singleton、getter、factory、lifespan 和 `app.state` 多种生命周期模型并存。治理重点不是把所有 `global` 单例机械改成 `Depends()`，而是先按生命周期分类：

```python
# 当前（反模式）
global _market_data_service
if _market_data_service is None:
    _market_data_service = MarketDataService()

# 推荐
def get_market_data_service() -> MarketDataService:
    ...
```

虽然形式上包装为函数，但内部仍是 `global` + lazy init。未使用 FastAPI 原生的依赖覆盖机制（`app.dependency_overrides`），导致测试时无法干净替换依赖。

### 5.2 错误处理不一致

- `app/core/exception_handler.py` 注册了全局异常处理器
- 但 `app/core/exception_handlers.py` 和 `app/core/global_exception_handlers.py` 也存在
- API 端点中同时使用 `BusinessException`、`NotFoundException`、直接 `raise HTTPException` 三种方式

### 5.3 Core 目录职责过载

`app/core/` 下 60+ 个文件，包含：

- 配置管理 (`config.py`)
- 数据库管理 (`database.py`, `database_factory.py`, `database_connection_pool.py`, `database_performance.py`, `database_metrics.py`, `database_performance_monitor.py`, `database_query_batch.py`)
- Socket.IO 管理 (`socketio_manager.py`, `socketio_connection_pool.py`, `socketio_memory_optimizer.py`, `socketio_message_batch.py`, `socketio_performance.py`)
- 缓存 (`cache_manager.py`, `cache_eviction.py`, `cache_prewarming.py`, `cache_integration.py`, `cache_utils.py`)
- 安全 (`security.py`, `encryption.py`, `password_policy.py`)
- 中间件 (`middleware/performance.py`)

建议按职责拆分子目录：

```
core/
├── config/
├── database/
├── cache/
├── security/
├── middleware/
├── websocket/
└── ...
```

### 5.4 Schema 双目录

`app/schema/` 和 `app/schemas/` 同时存在：

- `schema/` 仅含 `validation_models.py`
- `schemas/` 含 17 个业务 schema 文件（`market_schemas.py`, `trade_schemas.py`, `risk_schemas.py` 等）

按照 §三.1，应合并为单一真相源。

### 5.5 API 健康端点碎片化

> **事实校准**: 2026-05-17 基于代码扫描重验。详见子文档 G。

**Canonical 健康端点**（已确认，3 组 5 个端点）：

| Canonical 端点 | 定义位置 | 功能 |
|---|---|---|
| `GET /health` | `main.py:637` @app.get | Liveness probe（存活探针） |
| `GET /health/ready` | `main.py:673` @app.get | Readiness probe（就绪探针） |
| `GET /api/health/ready` | `main.py:688` 同 handler | Readiness probe（兼容路径） |
| `GET /api/health/services` | `health.py` via router_registry | 服务依赖检查（PG/TD/Mongo/disk） |
| `GET /api/health/detailed` | `health.py` via router_registry | 详细健康检查（需认证） |

**碎片健康端点**（下表为历史样本；2026-05-17 装饰器级扫描发现 46 个 health-like route decorators，需先重导 route table / OpenAPI）：

| # | 文件 | 路由器内路径 | 实际 URL（含 prefix） |
|---|---|---|---|
| 1 | `routes/sse_monitoring.py` | `/health` + `/health/channel/{ch}` + `/health/system` | SSE 路由下 |
| 2 | `api/system/system_health.py` | `/health` + `/adapters/health` | `/api/v1/system/*` |
| 3 | `api/system/get_system_architecture.py` | `/database/health` | `/api/v1/system/database/health` |
| 4 | `api/monitoring_old/routes.py` | `/health` | 旧模块 |
| 5 | `api/technical/routes.py` | `/health` | `/api/v1/technical/health` |
| 6 | `api/risk_v31/system.py` | `/health` | risk_v31 路由下 |
| 7 | `api/advanced_analysis.py` | `/health` | flat 文件路由下 |
| 8 | `api/advanced_analysis_api.py` | `/health` | flat 文件路由下 |
| 9 | `api/stock_ratings_api.py` | `/health` | flat 文件路由下 |
| 10 | `api/algorithms/get_algorithms_module.py` | `/health` | algorithms 路由下 |
| 11 | `api/multi_source.py` | `/health` + `/health/{type}` | `/api/multi-source/health` |
| 12 | `api/signal_monitoring/get_signal_statistics.py` | `/strategies/{id}/health/detailed` | signal 路由下 |
| 13 | `api/backup_recovery_secure/cleanup_old_backups.py` | `/health` | backup 路由下 |
| 14 | `api/metrics.py` | `/health` | `/api/health`（与 canonical 重叠） |
| 15 | `api/market/health_check.py` | `/health` | market 路由下 |
| 16 | `models/base_example.py` | `/health` | 示例代码 |
| 17 | `api/wencai.py` | `/health` | wencai 路由下 |
| 18 | `api/announcement/routes.py` | `/health` | `/api/announcement/health` |

收敛方案见子文档 G，执行前需 OpenSpec 审批。

---

## 六、正面发现

以下实践值得保持：

- **VERSION_MAPPING**：集中式 API 版本管理，`web/backend/app/api/VERSION_MAPPING.py` 结构清晰
- **健康探针体系**：当前代码提供 `/api/health/services`、`/api/health/detailed`、`/health/ready`、`/api/health/ready` 等入口，覆盖 PostgreSQL / Redis / MongoDB / 磁盘 / 系统。是否统一收敛到单一 canonical router 需进入 G 子方案与 OpenSpec 判定。
- **README 缓存**：`readiness.py` 实现了 5 秒 TTL 的就绪状态缓存，避免每次请求都 ping 数据库
- **Request ID 全链路**：`PerformanceMiddleware` 注入 `x-request-id` header，`ResponseFormatMiddleware` 补发
- **Prometheus 指标**：latency histogram、request counter、active requests gauge、slow request counter
- **CSRF 保护**：Redis 优先 + 内存回退，支持多 worker 共享 token 状态
- **Pydantic v2 Settings**：`validation_alias` 管理环境变量映射，`AliasChoices` 处理端口兼容
- **统一异常类**：`BusinessException`、`NotFoundException`、`ValidationException`、`AuthenticationException`
- **CORS + GZip 中间件**：在 `main.py` 中正确配置
- **错误码标准化**：`ErrorCodes` 和 `BusinessCode` 常量类，语义清晰
- **安全配置启动校验**：`validate_required_settings()` 在启动时验证必需环境变量

---

## 七、优先级建议

### 🔴 立即处理（本周）

| 项 | 行动 | 影响范围 |
|---|---|---|
| 保留 `print()` 门禁 | 当前 `web/backend/app` 扫描为 0 结果；后续新增后端 Python 文件仍需通过该门禁 | 日志红线 |
| 补齐残留候选双判定 | 当前备份文件扫描为 0；对 4 个 `_new.py` 和 `monitoring_old/` 补代码路径判定与功能树判定 | 迁移收口 |
| 规划 Core 重复文件治理 | 确定 canonical 版本、兼容 wrapper 和退场条件，进入 OpenSpec 后再移动或删除 | 重复真相源 |
| 规划 `schema/` + `schemas/` 合并 | 先确认 import 面和功能树状态，再决定是否迁移 `validation_models.py` | 重复真相源 |

### 🟡 近期处理（2-4 周）

| 项 | 行动 | 影响范围 |
|---|---|---|
| 创建 `app/core/logger.py` | 统一日志入口，封装 `structlog` 或 `logging` | 日志红线 |
| 统一 `structlog` vs `logging` | 全模块统一使用一种（优先 `structlog`） | 日志一致性 |
| 健康端点标准化 | 各模块健康检查改为 `UnifiedResponse`，逐步收敛到 `health.py` | 响应红线 |
| 制定 API flat→package 迁移计划 | 对 `market.py`、`announcement.py`、`strategy*.py` 等 flat 文件明确退出时间 | 迁移收口 |

### 🟢 长期优化（1-3 月）

| 项 | 行动 | 影响范围 |
|---|---|---|
| Singleton → DI 重构 | 先按生命周期分类，再用 FastAPI `Depends()`、factory、lifespan、`app.state` 或兼容 wrapper 分流处理 | 架构优化 |
| Core 目录拆分 | 先补 canonical import、旧模块 wrapper、import smoke 和 OpenSpec 设计，再按风险拆分 `database/`、`cache/`、`security/`、`socketio/` 等 | 目录治理 |
| 服务层整理 | 先补 consumer 矩阵、service parity、import smoke 和 OpenSpec 设计，再判定 `risk_management_new.py` / `risk_management_2.py` 是否退役 | 迁移收口 |
| 统一错误响应路径 | 禁止端点直接 `raise HTTPException`，统一通过 `BusinessException` 体系 | 错误处理一致性 |

---

## 八、与 FUNCTION_TREE.md 对照

从功能树 10 个域中，后端相关域的状态汇总：

| 域 | FUNCTION_TREE 状态 | 审计结论 |
|---|---|---|
| 01-市场数据与行情 | ✅ 95% | API 覆盖良好，adapter 层成熟，但 flat/package 并存 |
| 02-技术分析与指标 | ✅ 90% | 指标引擎完整，健康端点未标准化 |
| 03-策略管理与回测 | ✅ 85% | 代码量大但目录结构混乱（3 个 flat 文件 + 1 个 package） |
| 04-风险管理与监控 | ✅ 80% | `risk/`、`risk_v31/`、flat `risk_*.py` 三套并存 |
| 05-投资组合与交易 | 🚧 70% | 交易链路正在开发，结构尚可 |
| 06-监控与告警 | ✅ 75% | `monitoring_old/` 仍存在，新旧监控混用 |
| 07-高级分析与AI | 🧪 50% | 实验性质，未要求生产就绪 |
| 08-系统管理与配置 | ✅ 85% | 健康探针、认证体系完整 |
| 09-数据存储与管理 | ✅ 90% | 双库架构、缓存体系完整，但 cache 文件散落 |
| 10-公告与信息 | ✅ 80% | `announcement.py` flat + `announcement/` package 并存 |

---

*审计工具: backend-dev-guidelines skill + 手动代码审查*
*事实源: `docs/FUNCTION_TREE.md` + `architecture/STANDARDS.md` + 实际代码*
