# MyStocks Core 目录拆分方案

> **历史文档说明**:
> 本文件是 Core 目录拆分治理草案，不是当前可直接执行的移动/删除/重命名指令。
> 若需确认共享规则、审批门禁和实现状态，请优先以 `architecture/STANDARDS.md`、`openspec/AGENTS.md`、当前代码与最近一次验证结果为准。

> **来源**: `docs/reports/quality/backend-audit-2026-05-14.md` §五.3 深化
> **审计日期**: 2026-05-14
> **复核日期**: 2026-05-17
> **当前状态**: `web/backend/app/core/` 仍以顶层模块为主，但已存在 `cache/`、`logging/`、`middleware/` 子目录。
> **执行门禁**: Core 目录拆分、canonical import 变更、模块移动、兼容 wrapper 退役和 logger 入口变化均属于架构级变更，实施前必须创建并通过 OpenSpec proposal/design/tasks 审批。

2026-05-17 复核摘要：

| 扫描项 | 当前数量 / 结论 |
|--------|------------------|
| `core/` 顶层 `.py` 文件 | 65 |
| `core/` 功能子目录 | 3，`cache/`、`logging/`、`middleware/` |
| `core/` 全部 `.py` 文件 | 77 |
| `app.core.cache_manager` 代码/测试/脚本文本引用 | 10 |
| `app.core.database` 代码/测试/脚本文本引用 | 91 |
| `app.core.security` 代码/测试/脚本文本引用 | 54 |
| `app.core.logger` 代码/测试/脚本文本引用 | 5 |
| `app.core.socketio_manager` 代码/测试/脚本文本引用 | 2 |

结论：拆分风险不只在文件移动，还在旧模块路径、标准 logger 入口、FastAPI dependency、测试 monkeypatch 路径和运行时 import 解析。后续只能把本文作为 OpenSpec design 输入，不能按下文阶段表直接移动文件。

---

## 一、当前结构总览

`web/backend/app/core/` 当前包含：

```
core/
├── config.py                          # Pydantic Settings
├── database.py                        # PG engine + DataService + retry decorator
├── database_factory.py                # PG/MySQL engine factory
├── database_connection_pool.py        # 连接池优化器
├── database_performance.py            # 性能管理器（聚合池+批处理+监控）
├── database_performance_monitor.py    # 查询性能监控
├── database_metrics.py                # Prometheus 指标
├── database_query_batch.py            # 查询批处理
├── tdengine_manager.py                # TDengine 连接
├── tdengine_pool.py                   # TDengine 连接池
├── sync_db_manager.py                 # 同步DB管理器
├── cache_manager.py                   # 核心 CacheManager + AsyncCacheManager
├── cache_eviction.py                  # 淘汰策略 + 调度器
├── cache_integration.py               # Cache-Aside 模式
├── cache_prewarming.py                # 预热策略 + 监控
├── cache_utils.py                     # API 缓存装饰器 ⚠️ 与 cache_manager 职责重叠
├── cache/                             # 缓存子目录
├── redis_client.py                    # Redis 客户端
├── security.py                        # JWT + 密码哈希 + OAuth2
├── encryption.py                      # AES-256-GCM + 密钥轮换
├── password_policy.py                 # 密码策略校验
├── casbin_manager.py                  # Casbin RBAC
├── casbin_middleware.py               # Casbin 中间件
├── secure_config.py                   # 安全配置
├── _socketio_manager_singleton.py     # Socket.IO 单例
├── socketio_manager.py                # Socket.IO 管理器
├── socketio_connection_pool.py        # 连接池
├── socketio_memory_optimizer.py       # 内存优化
├── socketio_message_batch.py          # 消息批处理
├── socketio_performance.py            # 性能追踪
├── room_manager.py                    # 房间管理
├── connection_lifecycle.py            # WebSocket 连接生命周期
├── reconnection_manager.py            # 重连逻辑
├── adapter_factory.py                 # AdapterRegistry + AdapterFactory
├── adapter_loader.py                  # AdapterLoader (AkShare/TDX/Financial)
├── api_monitoring.py                  # API 指标收集
├── user_experience_monitor.py         # UX 监控
├── data_source_manager.py             # 数据源管理
├── celery_app.py                      # Celery 配置
├── circuit_breaker_manager.py         # 熔断器管理器
├── event_bus.py                       # 事件总线
├── incremental_snapshot.py            # 增量快照
├── sync_processor.py                  # 同步处理器
├── sse_manager.py                     # SSE 管理
├── sse_performance_optimizer.py       # SSE 性能
├── readiness.py                       # 就绪探针
├── service_factory.py                 # 服务工厂
├── unified_market_data_service.py     # 统一市场数据服务
├── unified_email_service.py           # 统一邮件服务
├── rate_limit.py                      # 速率限制
├── exceptions.py                      # 业务异常类 ✅ canonical
├── exception_handler.py               # 全局异常处理器（ErrorCode 体系）
├── exception_handlers.py              # 装饰器模式 @handle_exceptions ⚠️ 重叠
├── global_exception_handlers.py       # UnifiedResponse 格式异常处理 ⚠️ 重叠
├── error_handling.py                  # CircuitBreaker + Fallback + Retry
├── error_codes.py                     # ErrorCode 枚举
├── validation.py                      # 校验工具
├── validators.py                      # 校验器 ⚠️ 重叠
├── validation_messages.py             # 校验消息
├── data_validator.py                  # 数据校验
├── data_formats.py                    # 数据格式
├── responses.py                       # UnifiedResponse 响应模型
├── response_schemas.py                # 响应 Schema
├── strategy_validator.py              # 策略校验
├── middleware/                         # 性能中间件
│   └── performance.py
├── logging/                           # 日志子目录
└── cache/                             # 缓存子目录
```

---

## 二、职责分类

按职责将 68 个文件分为 12 个领域：

| # | 领域 | 文件数 | 当前分布 |
|---|------|--------|----------|
| 1 | **数据库** | 11 | `database*.py` ×7 + `tdengine*.py` ×2 + `sync_db_manager.py` + `redis_client.py` |
| 2 | **缓存** | 8 | `cache*.py` ×5 + `cache/` 子目录 + `redis_client.py`（共用） |
| 3 | **安全认证** | 6 | `security.py` + `encryption.py` + `password_policy.py` + `casbin*.py` ×2 + `secure_config.py` |
| 4 | **WebSocket/Socket.IO** | 9 | `socketio*.py` ×5 + `_socketio_manager_singleton.py` + `room_manager.py` + `connection_lifecycle.py` + `reconnection_manager.py` |
| 5 | **异常处理** | 6 | `exceptions.py` + `exception_handler.py` + `exception_handlers.py` + `global_exception_handlers.py` + `error_handling.py` + `error_codes.py` |
| 6 | **适配器** | 2 | `adapter_factory.py` + `adapter_loader.py` |
| 7 | **监控可观测** | 3 | `api_monitoring.py` + `user_experience_monitor.py` + `data_source_manager.py` |
| 8 | **基础设施** | 5 | `celery_app.py` + `circuit_breaker_manager.py` + `event_bus.py` + `incremental_snapshot.py` + `sync_processor.py` |
| 9 | **SSE/流** | 2 | `sse_manager.py` + `sse_performance_optimizer.py` |
| 10 | **校验** | 4 | `validation.py` + `validators.py` + `validation_messages.py` + `data_validator.py` |
| 11 | **配置与启动** | 3 | `config.py` + `readiness.py` + `service_factory.py` |
| 12 | **响应与格式** | 5 | `responses.py` + `response_schemas.py` + `data_formats.py` + `strategy_validator.py` + `rate_limit.py` |
| 13 | **业务服务（错放）** | 2 | `unified_market_data_service.py` + `unified_email_service.py` |

---

## 三、目标目录结构

```
core/
├── __init__.py                        # 重新导出所有公共 API（兼容层）
├── config.py                          # Pydantic Settings（保留顶层）
├── responses.py                       # UnifiedResponse（保留顶层）
├── exceptions.py                      # 业务异常类（保留顶层）
│
├── database/                          # 数据库领域（11 文件 → 合并精简）
│   ├── __init__.py
│   ├── engine.py                      # database.py（精简：仅 PG engine + session）
│   ├── factory.py                     # database_factory.py
│   ├── pool.py                        # database_connection_pool.py
│   ├── performance.py                 # database_performance.py + database_performance_monitor.py
│   ├── metrics.py                     # database_metrics.py
│   ├── batch.py                       # database_query_batch.py
│   ├── tdengine.py                    # tdengine_manager.py + tdengine_pool.py
│   └── sync.py                        # sync_db_manager.py
│
├── cache/                             # 缓存领域（8 文件 → 合并精简）
│   ├── __init__.py
│   ├── manager.py                     # cache_manager.py
│   ├── eviction.py                    # cache_eviction.py
│   ├── integration.py                 # cache_integration.py
│   ├── prewarming.py                  # cache_prewarming.py
│   └── utils.py                       # cache_utils.py（装饰器）
│
├── security/                          # 安全认证（6 文件）
│   ├── __init__.py
│   ├── auth.py                        # security.py（JWT + OAuth2）
│   ├── encryption.py                  # encryption.py
│   ├── password.py                    # password_policy.py
│   ├── rbac.py                        # casbin_manager.py + casbin_middleware.py
│   └── config.py                      # secure_config.py
│
├── websocket/                         # WebSocket/Socket.IO（9 文件 → 合并）
│   ├── __init__.py
│   ├── manager.py                     # socketio_manager.py + _socketio_manager_singleton.py
│   ├── pool.py                        # socketio_connection_pool.py
│   ├── optimizer.py                   # socketio_memory_optimizer.py
│   ├── batch.py                       # socketio_message_batch.py
│   ├── perf.py                        # socketio_performance.py
│   ├── rooms.py                       # room_manager.py
│   ├── lifecycle.py                   # connection_lifecycle.py
│   └── reconnect.py                   # reconnection_manager.py
│
├── errors/                            # 异常/错误处理（6 文件 → 归并）
│   ├── __init__.py
│   ├── codes.py                       # error_codes.py
│   ├── handler.py                     # exception_handler.py（canonical）← 保留
│   ├── decorators.py                  # exception_handlers.py（@handle_exceptions 装饰器）
│   ├── unified.py                     # global_exception_handlers.py
│   └── resilience.py                  # error_handling.py（熔断器+降级+重试）
│
├── adapters/                          # 适配器（2 文件）
│   ├── __init__.py
│   ├── factory.py                     # adapter_factory.py
│   └── loader.py                      # adapter_loader.py
│
├── monitoring/                        # 监控可观测（3 文件）
│   ├── __init__.py
│   ├── api.py                         # api_monitoring.py
│   ├── ux.py                          # user_experience_monitor.py
│   └── datasource.py                  # data_source_manager.py
│
├── infra/                             # 基础设施（5 文件）
│   ├── __init__.py
│   ├── celery.py                      # celery_app.py
│   ├── breaker.py                     # circuit_breaker_manager.py
│   ├── events.py                      # event_bus.py
│   ├── snapshot.py                    # incremental_snapshot.py
│   └── sync.py                        # sync_processor.py
│
├── streaming/                         # SSE/流（2 文件）
│   ├── __init__.py
│   ├── sse.py                         # sse_manager.py
│   └── sse_perf.py                    # sse_performance_optimizer.py
│
├── validation/                        # 校验（4 文件 → 合并）
│   ├── __init__.py
│   ├── core.py                        # validation.py + validators.py（合并）
│   ├── messages.py                    # validation_messages.py
│   └── data.py                        # data_validator.py
│
├── boot/                              # 配置与启动（3 文件）
│   ├── __init__.py
│   ├── settings.py                    # config.py
│   ├── readiness.py                   # readiness.py
│   └── services.py                    # service_factory.py
│
├── formats/                           # 格式与约束（5 文件）
│   ├── __init__.py
│   ├── data.py                        # data_formats.py
│   ├── response_schemas.py            # response_schemas.py
│   ├── strategy.py                    # strategy_validator.py
│   └── rate_limit.py                  # rate_limit.py
│
├── redis.py                           # redis_client.py（依赖面广，保留顶层）
├── middleware/                         # 中间件（已有子目录，不变）
│   └── performance.py
└── logging/                           # 日志（已有子目录，不变）
```

**精简结果**: 68 文件 → 50 文件（12 个合并），13 个子目录。

---

## 四、重复文件归并方案

### 4.1 异常处理 ×3 → 1 canonical + 1 装饰器 + 1 弹性

| 现有文件 | 行数 | 处理方式 | 继任路径 |
|---|---|---|---|
| `exceptions.py` | ~270 | **保留为 canonical** | `core/exceptions.py`（顶层） |
| `exception_handler.py` | ~340 | **保留** → `core/errors/handler.py` | 全局异常处理器 + `register_exception_handlers()` |
| `exception_handlers.py` | ~280 | **保留但降级** → `core/errors/decorators.py` | `@handle_exceptions` 装饰器，改名避免与 handler 混淆 |
| `global_exception_handlers.py` | ~320 | **废弃**，功能合并到 `handler.py` | UnifiedResponse 格式已在 handler.py 覆盖 |
| `error_handling.py` | ~430 | **保留** → `core/errors/resilience.py` | CircuitBreaker + RetryPolicy + Fallback |
| `error_codes.py` | ~200 | **保留** → `core/errors/codes.py` | ErrorCode 枚举 |

**归并动作**:
1. `global_exception_handlers.py` 的 `register_global_exception_handlers()` 合并到 `exception_handler.py` 的 `register_exception_handlers()`
2. `exception_handlers.py` 重命名为 `decorators.py`，消除与 `exception_handler.py` 的命名混淆

### 4.2 校验 ×3 → 合并为 1 canonical

| 现有文件 | 行数 | 处理方式 |
|---|---|---|
| `validation.py` | ~150 | 合并到 `core/validation/core.py` |
| `validators.py` | ~120 | 合并到 `core/validation/core.py` |
| `validation_messages.py` | ~80 | → `core/validation/messages.py` |
| `data_validator.py` | ~200 | → `core/validation/data.py` |

### 4.3 缓存 ×6 → 保留分文件但集中目录

现有 6 个缓存文件职责不同，不合并文件，仅集中到 `core/cache/`：

| 现有文件 | 目标路径 | 说明 |
|---|---|---|
| `cache_manager.py` | `core/cache/manager.py` | CacheManager + AsyncCacheManager |
| `cache_eviction.py` | `core/cache/eviction.py` | 淘汰策略 + 调度器 |
| `cache_integration.py` | `core/cache/integration.py` | Cache-Aside 模式 |
| `cache_prewarming.py` | `core/cache/prewarming.py` | 预热策略 + 监控 |
| `cache_utils.py` | `core/cache/utils.py` | API 缓存装饰器 |
| `cache/` (子目录) | 合并到 `core/cache/` | 现有子目录内容融入 |

### 4.4 数据库 ×7 → 集中到 `core/database/`

不合并文件（各司其职），仅移动：

| 现有文件 | 目标路径 |
|---|---|
| `database.py` | `core/database/engine.py` |
| `database_factory.py` | `core/database/factory.py` |
| `database_connection_pool.py` | `core/database/pool.py` |
| `database_performance.py` + `database_performance_monitor.py` | `core/database/performance.py`（合并） |
| `database_metrics.py` | `core/database/metrics.py` |
| `database_query_batch.py` | `core/database/batch.py` |
| `tdengine_manager.py` + `tdengine_pool.py` | `core/database/tdengine.py`（合并） |
| `sync_db_manager.py` | `core/database/sync.py` |

---

## 五、导入兼容策略（OpenSpec 设计输入）

### 5.1 兼容原则

`core/__init__.py` 只能兼容 `from app.core import X` 形式，不能自动兼容 `from app.core.cache_manager import X` 这类旧模块路径。每个旧路径必须按模块形态分别设计：

| 旧路径类型 | 兼容方式 | 示例 |
|------------|----------|------|
| 旧文件名改成同名 package | 在同名 package 的 `__init__.py` 重导出 | `app.core.database`、`app.core.security` |
| 旧文件名迁到不同 package | 保留旧顶层 `.py` 薄 wrapper | `app.core.cache_manager`、`app.core.socketio_manager` |
| 仓库红线指定 canonical 入口 | 保留旧入口为 canonical，内部实现可下沉 | `app.core.logger` |
| 顶层聚合导入 | `core/__init__.py` 只用于聚合导出，不承担旧子模块兼容 | `from app.core import settings` |

`app.core.logger` 目前是 `architecture/STANDARDS.md` 和 A 文档确认的标准入口。即使内部实现继续放在 `core/logging/structured.py` 或其他子模块，也必须由 `app/core/logger.py` 作为 canonical wrapper 暴露，不得把全仓导入统一替换成 `app.core.logging.logger`。

### 5.2 当前高风险 import 面

| 旧路径 | 当前文本引用 | 设计要求 |
|--------|--------------|----------|
| `app.core.cache_manager` | 10 | 必须保留 `app/core/cache_manager.py` 薄 wrapper，除非 OpenSpec 批准一次性更新全部 importer |
| `app.core.database` | 91 | 若改为 package，`database/__init__.py` 必须重导出当前公开 API，并补 import smoke |
| `app.core.security` | 54 | 若改为 package，`security/__init__.py` 必须保留 auth 相关 API、测试 monkeypatch 路径和 FastAPI dependency 路径 |
| `app.core.logger` | 5 | 保留 canonical 入口，不把调用方改到内部 logging 子模块 |
| `app.core.socketio_manager` | 2 | 若迁到 websocket package，旧顶层模块需保留 wrapper 或同步修改调用方 |

### 5.3 wrapper 退场条件

| 条件 | 要求 |
|------|------|
| 引用清零 | `rg "app.core.<old_module>" web/backend/app tests scripts` 为 0，且文档引用不作为代码阻塞项 |
| import smoke | 旧路径和新路径在同一 Python 环境下都可导入，公开对象一致 |
| 功能 smoke | 涉及 FastAPI dependency、PM2 启动、健康端点和核心测试通过 |
| 回滚路径 | wrapper 保留到新路径稳定后再退役；退役失败时可恢复 wrapper 文件 |
| 审批记录 | OpenSpec tasks 明确 wrapper 保留期、退役触发器和验证命令 |

---

## 六、提案前拆分路线（不直接实施）

### Step 1: 重建当前事实清单

先重新生成当前 `core/` 文件树、import 引用、GitNexus 上游依赖、测试 monkeypatch 路径和 PM2 启动依赖。不得沿用“68 个文件 + 3 个子目录，全部平铺”的旧快照作为实施依据。

### Step 2: 按兼容模式分类

| 分类 | 处理方向 |
|------|----------|
| 可变成同名 package 的模块 | 设计 package `__init__.py` 重导出 |
| 必须保留旧模块名的模块 | 设计顶层 thin wrapper |
| 当前标准入口 | 保持 canonical 路径，内部实现下沉必须透明 |
| 真重复实现 | 先证明行为等价，再合并 |
| 业务服务错放 | 先确认服务所有权和调用链，再迁出 core |

### Step 3: OpenSpec 设计项

Core 拆分属于架构变更。proposal/design/tasks 至少要写清：

| 设计项 | 必填内容 |
|--------|----------|
| canonical import | 每个域的新旧路径、wrapper、package `__init__` 和退役条件 |
| compatibility matrix | `database`、`security`、`cache_manager`、`logger`、`socketio_manager` 等高风险路径 |
| import smoke | 旧路径、新路径、公开对象一致性和测试 monkeypatch 路径 |
| runtime smoke | PM2 后端、`/api/health/services`、`/health/ready`、`/api/health/ready` |
| rollback | wrapper 恢复、模块移动回滚和分批停止条件 |
| ownership | 每批文件 owner、reviewer 和预计工作量 |

### Step 4: 审批后按风险分批

审批通过后再按风险分批实施，不按目录一次性大搬迁：

| 批次 | 候选范围 | 验证 |
|------|----------|------|
| A | 无运行时状态的纯类型、schema、format helper | import smoke + unit |
| B | `logger` wrapper 和 logging 内部实现 | `app.core.logger` canonical smoke + 日志门禁 |
| C | `database` / `security` 同名 package 化 | FastAPI dependency smoke + monkeypatch smoke |
| D | `cache_manager` / `socketio_manager` 旧模块 wrapper | 旧路径和新路径对象一致性 smoke |
| E | 真重复实现归并 | 行为等价测试 + 回滚 wrapper |

---

## 七、风险与注意事项

1. **`cache_utils.py` 中的 `CacheManager` 与 `cache_manager.py` 中的 `CacheManager` 同名不同类** — 移动时必须确认所有调用方引用的是哪个类，避免导入冲突。

2. **`database.py` 中的 `get_db()` 是 FastAPI 依赖注入函数** — 移动后必须确保 `Depends(get_db)` 路径不变。

3. **`_socketio_manager_singleton.py` 是下划线前缀的"私有"单例** — 与 `socketio_manager.py` 的关系需要明确后再合并。

4. **`unified_market_data_service.py` 和 `unified_email_service.py` 本质是业务服务，不应放在 core** — 建议迁移到 `app/services/`。

5. **`adapter_factory.py` 和 `adapter_loader.py` 存在职责重叠** — 两者都管理适配器实例化，Phase 2 后应审视合并可能性。

6. **`redis_client.py` 被 cache、security、readiness 等多个模块依赖** — 保留在 `core/` 顶层避免循环导入。

---

## 八、拆分前后对比

| 维度 | 拆分前 | 拆分后 |
|---|---|---|
| 顶层 `.py` 文件数 | 65 | 待 OpenSpec 批准后按批下降，不预设一次降到 8 |
| 功能子目录数 | 3 | 目标子目录需由 design 决定，不直接按 13 个创建 |
| 最大目录深度 | 2 | 可提高到 3，但必须避免循环导入和隐藏 canonical 入口 |
| 重复文件 | 多组候选 | 先证明行为等价，再归并或明确分工 |
| 业务服务错放 | 候选需重测 | 先确认 owner 和调用链，再决定是否迁至 `services/` |
| 外部 import 兼容性 | 高风险 | 由旧模块 wrapper、同名 package `__init__`、import smoke 和退役条件共同保证 |

---

*前置文档: `docs/reports/quality/backend-audit-2026-05-14.md` §五.3*
