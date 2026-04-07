# TASK-REPORT

> **历史任务说明**:
> 本文件是历史任务单、历史任务汇报或归档任务工件，不是当前任务系统、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前主线任务系统及验证结果一并核对。
>
> 文内范围、完成状态、负责人、验证命令和下一步如未重新复核，应视为当时任务快照，不得直接当作当前事实。


> Exported from Mongo control plane. Human notes may be appended, but active state lives in Mongo.

- Issue Identifier: `2026-03-12-data-db-runtime-audit-dev-data-db-audit-claude`
- Issue Title: `Data And DB Runtime Audit Convergence`
- Assigned Worker CLI: `dev-data-db-audit-claude`
- Current Status: `verified`
- Latest Progress: Split Commit Playbook
- Pending Request: `False`

## Updates
- `2026-03-12T00:00:25` [in_progress] dev-data-db-audit-claude: Round 1 Data/DB Runtime Audit
- `2026-03-12T00:00:26` [in_progress] dev-data-db-audit-claude: Round 2 Runtime Entry Convergence
- `2026-03-12T00:00:27` [in_progress] dev-data-db-audit-claude: Round 3 Route-Level Ownership Check
- `2026-03-12T00:00:28` [in_progress] dev-data-db-audit-claude: Round 4 Runtime Config Drift Fixes
- `2026-03-12T00:00:29` [in_progress] dev-data-db-audit-claude: Round 5 Env And PM2 Drift Fixes
- `2026-03-13T00:00:30` [in_progress] dev-data-db-audit-claude: Round 6 Monitoring And PM2 Production Convergence
- `2026-03-13T00:00:31` [in_progress] dev-data-db-audit-claude: Round 7 Active Monitoring Docs Sweep
- `2026-03-13T00:00:32` [in_progress] dev-data-db-audit-claude: Round 8 PM2 Worktree Decoupling Sweep
- `2026-03-13T00:00:33` [in_progress] dev-data-db-audit-claude: Round 9 Active Deployment Docs Port Convergence
- `2026-03-13T00:00:34` [in_progress] dev-data-db-audit-claude: Round 10 Conservative Deletion Candidates Inventory
- `2026-03-13T00:00:35` [in_progress] dev-data-db-audit-claude: Round 11 First Conservative Cleanup Execution
- `2026-03-13T00:00:36` [in_progress] dev-data-db-audit-claude: Round 12 Misleading Example Rename
- `2026-03-13T00:00:37` [in_progress] dev-data-db-audit-claude: Round 13 Legacy Compatibility Fix
- `2026-03-13T00:00:38` [in_progress] dev-data-db-audit-claude: Round 14 Remaining Candidate Closure
- `2026-03-13T00:00:39` [in_progress] dev-data-db-audit-claude: Compatibility Retention Archival Plan
- `2026-03-13T00:00:40` [in_progress] dev-data-db-audit-claude: Round 15 Compatibility Isolation Execution
- `2026-03-13T00:00:41` [in_progress] dev-data-db-audit-claude: Round 16 Compatibility Config Relocation
- `2026-03-13T00:00:42` [in_progress] dev-data-db-audit-claude: Final Change Classification
- `2026-03-13T00:00:43` [verified] dev-data-db-audit-claude: Final Verification Snapshot
- `2026-03-13T00:00:44` [verified] dev-data-db-audit-claude: Split Commit Playbook

## Requests
- (none)

## Graphiti

- server_status: `(none)`
- ingest_status: `(none)`
- search_summary: `(none)`

## Detailed Updates

### `2026-03-12T00:00:25` [in_progress] dev-data-db-audit-claude
- Summary: Round 1 Data/DB Runtime Audit

#### Scope
- 按任务要求先做资产盘点，不做删除或行为改动。
- 已阅读：`TASK.md`、`openspec/AGENTS.md`、`openspec/changes/audit-data-db-runtime/{proposal,design,tasks}.md`
- 已补充门禁阅读：`architecture/STANDARDS.md`、`docs/FUNCTION_TREE.md`、`docs/guides/ai-tools/AI_QUICK_START.md`、`docs/architecture/README.md`、`docs/deployment/README.md`、`docs/operations/README.md`

#### Verification Evidence
- `git branch --show-current`
- `openspec list`
- `openspec list --specs`
- `python` 统计 `config/data_sources_registry.yaml` 条目分布
- `python` 统计 `config/table_config.yaml` 表定义分布

#### Notes
- Judgment Legend:
- `有效`：当前代码主链路或运行入口明确使用。
- `兼容保留`：仍被脚本/测试/兼容包装引用，当前不能安全删除。
- `待判定`：仓库中存在，但运行入口、部署入口或主链路不够清晰。
- Snapshot:
- `config/data_sources_registry.yaml`：20 个数据源条目，`17` 个目标 `postgresql`，`3` 个目标 `tdengine`；来源分布为 `akshare=18`、`system_mock=1`、`windows_nodes=1`。
- `config/data_sources.json`：当前 Web 数据源工厂模块配置为 `market/data/dashboard/technical_analysis/watchlist/strategy` 共 6 个模块。
- `config/table_config.yaml`：29 个表定义，其中 `PostgreSQL=21`、`TDengine=8`、`Redis=0`。
- `src/adapters/`：顶层 28 个 `.py` 文件，子目录中 `akshare/31`、`tdx/16`、`financial/14`、`efinance_adapter/5`、`akshare_modules/5`、`baostock/1`、`webdata/1`。
- 数据源现状矩阵:
- | 对象 | 事实源 | 现状 | 判断 |
- | --- | --- | --- | --- |
- | Core 双库数据协调主线 | `src/core/data_manager.py`、`src/core/infrastructure/data_router.py`、`src/data_access/{postgresql_access,tdengine_access}.py` | `DataManager` 通过 `DataRouter` 按 `DataClassification` 在 `PostgreSQL/TDengine` 间路由；这是核心持久化主链路。 | `有效` |
- | YAML 数据源注册表 + Config CRUD | `config/data_sources_registry.yaml`、`src/core/data_source/config_manager.py`、`web/backend/app/api/data_source_config.py` | `ConfigManager` 以 YAML 为主配置源，并挂有版本/审计/回滚能力；GitNexus 显示其被 `/api/v1/data-sources/config` 直接调用，风险为 `CRITICAL`，不能轻删。 | `有效` |
- | Web 运行时数据源工厂（JSON） | `config/data_sources.json`、`web/backend/app/services/data_source_factory/*.py`、`web/backend/app/api/data/*`、`web/backend/app/api/market/market_data_request.py` | Web API 仍广泛通过 `get_data_source_factory()` 读取 JSON 配置；这是另一条正在工作的运行时数据源主线。 | `有效` |
- | 适配器管理器 V1/V2 | `src/adapters/data_source_manager.py`、`src/core/data_source/base.py` | V1 `DataSourceManager` 在脚本和单测中被大量直接调用；V2 `DataSourceManagerV2` 提供 YAML + 智能路由 + SmartCache，但没有完全取代 V1。 | `兼容保留` |
- | MultiSourceManager 局部链路 | `web/backend/app/services/multi_source_manager.py`、`web/backend/app/api/multi_source.py` | 这是独立于上面两套之外的第三条局部链路，当前仅看见 `EastMoney/Cninfo` 适配器和本地字典缓存。 | `有效（局部）` |
- | 环境变量驱动数据源工厂 | `src/data_sources/factory.py`、`scripts/switch_data_mode.py` | 依赖 `TIMESERIES_DATA_SOURCE/RELATIONAL_DATA_SOURCE/BUSINESS_DATA_SOURCE`；当前主要被脚本和测试引用，不是 Web 后端主配置入口。 | `兼容保留` |
- | 拆分式 YAML Loader | `config/data_sources_loader.py`、`config/data_sources/sina_finance.yaml` | Loader 依赖主配置中的 `load_sources`/`aliases`，但当前 `config/data_sources_registry.yaml` 仅有 `version/last_updated/data_sources`，未启用拆分加载；`sina_finance.yaml` 目前不会进入主运行配置。 | `待判定` |
- | Redis DataSourceRegistry 示例栈 | `src/core/datasource/registry.py`、`config/datasource.yaml.example` | 存在 Redis 驱动的注册表/健康状态模型，但未发现它接入当前应用启动流程或 Web 配置。 | `待判定` |
- | 顶层适配器资产池 | `src/adapters/` | 代码资产明显多于 YAML/JSON 运行配置暴露的对象；例如 registry YAML 只有 20 个条目且几乎都是 AKShare，但适配器目录包含 TDX、BaoStock、Tushare、EFinance、Sina、Byapi 等多条实现。 | `兼容保留` |
- 数据库现状矩阵:
- | 对象 | 事实源 | 现状 | 判断 |
- | --- | --- | --- | --- |
- | PostgreSQL 主业务库 | `web/backend/app/core/config.py`、`web/backend/app/core/database.py`、`src/data_access/postgresql_access.py` | 后端启动必需项；`readiness` 探针校验它；核心查询、监控库回退、DataManager 路由均依赖它。 | `有效` |
- | PostgreSQL 监控/审计库 | `web/backend/app/core/config.py`、`src/storage/database/database_manager/_build_monitor_db_url.py` | 当前口径是与主库同实例/同数据库复用，必要时单独 URL；表创建/验证/操作日志均写这里。 | `有效` |
- | TDengine 时序库 | `src/data_access/tdengine_access.py`、`web/backend/app/core/tdengine_manager.py`、`config/docker-compose.tdengine.yml` | 高频时序路径明确存在；`table_config.yaml` 中有 8 个 TDengine 表定义，`data_sources_registry.yaml` 里也有 3 个条目直接标到 `tdengine`。 | `有效` |
- | Redis 运行时基础设施 | `web/backend/app/core/config.py`、`web/backend/app/core/redis_client.py`、`web/backend/app/core/readiness.py`、`web/backend/app/core/celery_app.py`、`web/backend/app/services/redis/*` | Redis 已不是“可有可无”的旁路：就绪探针、缓存、锁、Pub/Sub、JWT 黑名单、CSRF token 以及 Celery broker/result backend 都在使用它。 | `有效` |
- | MongoDB | `config/docker-infra/monitoring-stack.yml`、`config/docker/mongodb.yml`、`tests/unit/core/test_web_backend_runtime_settings.py` | 仓库中有 Docker/README/测试口径，但未找到 Web 后端对应的运行时配置字段、访问层或工厂实现；`IDataAccess` 也没有 Mongo 实现。 | `待判定` |
- | MongoDB 抽象枚举 | `src/data_access/interfaces/i_data_access.py` | `DatabaseType` 仍包含 `MONGODB`，但 `DataAccessFactory` 只支持 `TDENGINE/POSTGRESQL`。接口层与实现层口径未对齐。 | `兼容保留` |
- | Redis 作为“表型数据库” | `config/table_config.yaml`、`src/core/config_driven_table_manager.py`、`src/storage/database/database_manager/database_table_manager_methods/part1.py` | `table_config.yaml` 仍声明 Redis 连接信息，但表定义数为 0；表管理器也保留 `DatabaseType.REDIS`，并在代码中写明“项目当前未使用”。 | `兼容保留` |
- 缓存现状矩阵:
- | 对象 | 事实源 | 现状 | 判断 |
- | --- | --- | --- | --- |
- | L1/L2 多级缓存组件 | `src/core/cache/multi_level.py` | 明确实现 `Memory + Redis` 两级缓存、熔断器和 Prometheus 指标，是共享缓存能力本体。 | `有效` |
- | Web RedisManager / RedisCacheService | `web/backend/app/core/redis_client.py`、`web/backend/app/services/redis/redis_cache.py` | Web 运行时的 Redis 接入主线，封装了连接池、set/get、批量操作。 | `有效` |
- | Web CacheManager 三级缓存框架 | `web/backend/app/core/cache/core.py`、`web/backend/app/core/cache_integration.py` | 代码层设计为 `L1 memory -> L2 Redis -> L3 TDengine`，但当前文件里 `REDIS_CACHE_AVAILABLE = False`，表现为“框架在、启用条件未完全收口”。 | `兼容保留` |
- | 安全相关缓存/状态 | `web/backend/app/main.py`、`web/backend/app/core/security.py` | CSRF token 与 JWT 黑名单均为 `Redis 优先，内存回退`，说明 Redis 是安全路径依赖。 | `有效` |
- | MultiSourceManager 本地缓存 | `web/backend/app/services/multi_source_manager.py` | 单独维护 `_cache` + `TTL=300` 的局部内存缓存，不复用共享缓存栈。 | `有效（局部）` |
- | `config/.env.example` 的“应用层缓存替代 Redis”口径 | `config/.env.example` | 该文案与当前实现冲突：代码明确依赖 Redis 作为缓存/消息/锁/Celery 设施。 | `待判定（文档失真）` |
- 运行依赖现状矩阵:
- | 对象 | 事实源 | 现状 | 判断 |
- | --- | --- | --- | --- |
- | 根 `.env.example` | `.env.example` | 与当前 Web 后端必需项更接近：包含 `POSTGRESQL_*`、`REDIS_*`、`JWT_SECRET_KEY`、`3020/8020` 端口。 | `有效` |
- | `config/.env.example` | `config/.env.example` | 仍写有 “Week 3 简化”“应用层缓存替代 Redis” 等旧口径，且与当前 Redis/Celery/Readiness 实现不一致。 | `兼容保留` |
- | 本地测试基础设施 | `config/docker-compose.test.yml` | 明确同时拉起 `postgres-test`、`redis-test`、`tdengine-test`、`backend-test`，说明测试口径是三设施并存。 | `有效` |
- | 双库开发基础设施 | `config/docker-compose.tdengine.yml` | 提供 `TDengine + PostgreSQL` 开发/验证环境。 | `有效` |
- | 生产基础设施 | `config/docker/docker-compose.prod.yml` | 生产口径明确包含 `PostgreSQL + Redis + TDengine + backend + frontend + nginx + prometheus + grafana + backup-service`。 | `有效` |
- | 监控栈 Docker | `config/docker-infra/monitoring-stack.yml` | 监控栈包含 `Prometheus/Grafana/MongoDB/AlertManager`，其中 Mongo 更像监控/文档库旁路而非主业务库。 | `待判定` |
- | 根 `docker-compose.prod.yml` | `docker-compose.prod.yml` | 当前不是 compose 文件本体，而是仅写了一个路径字符串 `config/docker/docker-compose.prod.yml` 的跳转壳。 | `兼容保留` |
- | PM2 配置 | `config/pm2/ecosystem.config.js` | 仍指向旧路径 `/opt/claude/mystocks_spec`，默认端口是 `3002/8000`，与当前门禁口径 `3020/8020` 以及当前 worktree 路径不一致。 | `待判定` |
- | 运行时依赖包 | `requirements.txt`、`pyproject.toml` | 依赖仍包含 `redis`、`celery`、`psycopg2-binary`、`taospy`、`asyncpg`，同时保留 `pymongo` 可选依赖；与“Mongo 未接主链”现状形成偏差。 | `兼容保留` |
- 关键结论（第一轮）:
- 1. 当前仓库不是单一数据源/数据库运行栈，而是至少并行存在三套数据源管理路径：
- Core 双库持久化主线：`DataManager + DataRouter + TDengine/PostgreSQLDataAccess`
- Web 运行时模块工厂：`config/data_sources.json + web/backend/app/services/data_source_factory`
- YAML 配置治理主线：`config/data_sources_registry.yaml + ConfigManager + /api/v1/data-sources/config`
- 2. Redis 不是“未来规划项”或“已被应用层缓存替代”的历史配置，而是当前运行时依赖：
- readiness probe
- cache / pubsub / distributed lock
- JWT blacklist
- CSRF token 持久化
- Celery broker / result backend
- 3. MongoDB 当前更像“基础设施/测试/文档口径遗留项”：
- Docker 和测试里有明确存在感
- 但应用运行配置、数据访问层、工厂实现未形成闭环
- 本轮不能判定可删
- 4. 数据源拆分治理未真正落地：
- `config/data_sources_loader.py` 已存在
- `config/data_sources/sina_finance.yaml` 已存在
- 但主 registry 未声明 `load_sources`
- 运行时仍只吃单文件 `config/data_sources_registry.yaml`
- 5. 当前最明显的“先别删”区域：
- `src/adapters/data_source_manager.py` / `DataSourceManagerV2`
- `src/data_sources/factory.py`
- `src/core/datasource/registry.py`
- `config/pm2/ecosystem.config.js`
- Mongo 相关 Docker / 测试口径
- 建议的第二轮核查方向:
- 1. 先做“入口收口”，确认生产/PM2/测试究竟以哪套数据源配置为准：
- `data_sources_registry.yaml`
- `data_sources.json`
- `TIMESERIES/RELATIONAL/BUSINESS_DATA_SOURCE`
- 2. 逐条核对 Redis 的真实职责边界：
- 业务缓存
- 安全状态
- Celery
- 监控事件
- 工具维护 DB
- 3. 单独核定 Mongo：
- 是否仅保留给监控/文档/实验用途
- 是否缺失运行时配置模块
- 是否只是测试/文档债务
- 4. 再决定哪些能标为：
- `可删`
- `兼容保留`
- `待判定`
- `rg`/`sed` 核对以下事实源:
- `src/core/data_manager.py`
- `src/core/infrastructure/data_router.py`
- `src/data_access/{factory,postgresql_access,tdengine_access}.py`
- `src/core/data_source/config_manager.py`
- `web/backend/app/services/data_source_factory/data_source_factory.py`
- `web/backend/app/core/{config,database,redis_client,readiness}.py`
- `web/backend/app/main.py`
- `config/{data_sources_registry.yaml,data_sources.json,table_config.yaml}`
- `config/docker-compose.tdengine.yml`
- `config/docker-compose.test.yml`
- `config/docker/docker-compose.prod.yml`
- `config/docker-infra/monitoring-stack.yml`

### `2026-03-12T00:00:26` [in_progress] dev-data-db-audit-claude
- Summary: Round 2 Runtime Entry Convergence

#### Scope
- 在第一轮矩阵基础上，继续收口“真实入口”和“兼容层边界”。
- 仍然不做删除，不改业务行为，只补事实源和验证证据。

#### Notes
- 入口收口结果:
- | 入口/链路 | 实际注册或调用证据 | 第二轮判断 |
- | --- | --- | --- |
- | YAML 配置治理入口 | `web/backend/app/router_registry.py` 注册了 `data_source_config.router` 与 `data_source_registry.router`；前者直连 `ConfigManager(yaml_config_path=\"config/data_sources_registry.yaml\")`，后者直连 `DataSourceManagerV2()` | `有效（治理入口）` |
- | JSON Web 运行时数据源入口 | `web/backend/app/router_registry.py` 注册 `data.router`、`data_quality.router`、`market.router`；全仓统计 `get_data_source_factory()` 在 `web/backend/app` 内出现 `22` 次，其中 `/api/data/*` 13 次 | `有效（主运行入口）` |
- | `multi_source` 局部运行入口 | `web/backend/app/router_registry.py` 注册 `multi_source.router`；`get_multi_source_manager()` 在 `web/backend/app` 内出现 `10` 次（`api/multi_source.py` 8 次、`announcement_service.py` 1 次、manager 自身单例 1 次） | `有效（局部运行入口）` |
- | `src.data_sources` 工厂入口 | `web/backend/app/api/strategy_mgmt.py` 直接 `from src.data_sources import get_business_source`；`web/backend/app/api/v1/risk/core.py`、`web/backend/app/api/risk/metrics.py` 等直接调用 `src.data_sources.factory.get_timeseries_source` | `兼容保留（局部运行链路）` |
- 第二轮判断更新:
- 1. `config/data_sources.json` 已可明确认定为当前 Web 后端最广泛的数据获取配置入口。
- 证据：`web/backend/app/api/data/*.py`、`web/backend/app/api/data_quality.py`、`web/backend/app/api/market/market_data_request.py` 直接走 `get_data_source_factory()`
- 结论：它不是测试壳，而是活跃运行主线
- 2. `config/data_sources_registry.yaml` 已可明确认定为“治理/盘点/配置 CRUD 入口”，不是主要的数据获取运行入口。
- 证据：`data_source_config.py` 负责 CRUD / 版本 / 回滚
- 证据：`data_source_registry.py` 负责搜索 / 分类统计 / 测试 / 健康检查
- 结论：YAML 线是 active，但职责偏治理，不是 Web API 的主取数路径
- 3. `src.data_sources.factory` 不能再简单视为“只剩脚本兼容”。
- 它已进入已注册的 `strategy_mgmt` 与 `api/v1/risk/*` 运行路径
- 但不是全局默认入口，也不主导 `/api/data/*`
- 当前应归类为 `兼容保留（局部运行链路）`
- 4. `ConfigManager` 与 `DataSourceManagerV2` 的边界已清晰：
- `ConfigManager`：面向配置变更治理、版本化、审计、回滚
- `DataSourceManagerV2`：面向数据源注册表搜索、分类统计、测试与健康检查
- 两者都吃 `config/data_sources_registry.yaml`，但用途不同
- 5. `config/data_sources_loader.py` / `config/data_sources/*.yaml` 仍未进入已验证主链路。
- 当前主 registry 不包含 `load_sources` / `aliases`
- `config/data_sources/sina_finance.yaml` 不会自动被主 registry 合并
- 本轮保持 `待判定`
- Mongo / Redis 边界收口:
- | 对象 | 第二轮证据 | 第二轮判断 |
- | --- | --- | --- |
- | MongoDB 运行时配置 | `web/backend/app/core/config.py` 中不存在 `mongodb_host` / `mongodb_runtime_host` / `mongodb_connection_kwargs` 等字段；仓库中也不存在 `src/utils/mongo_runtime_config.py` | `兼容保留（主应用未接入，测试/容器口径仍在）` |
- | MongoDB 测试口径 | `tests/unit/core/test_web_backend_runtime_settings.py`、`tests/unit/core/test_runtime_config_governance.py` 仍断言 Mongo runtime 配置存在 | `兼容保留（测试漂移）` |
- | Redis 角色化配置 | `src/utils/redis_runtime_config.py` 存在按 role 分库实现；相关治理测试大部分通过 | `有效` |
- | Celery Redis 默认值 | `web/backend/app/core/config.py` 中 `celery_broker_url` / `celery_result_backend` 字段默认值仍写死 `redis://localhost:6379/0|1`；只有 `default_celery_*` property 才使用 role-aware DB | `待判定（配置行为漂移）` |
- 定向验证结果:
- `pytest tests/unit/core/test_web_backend_runtime_settings.py -q -o addopts=''`
- 结果：`3 failed, 2 passed`
- 失败原因：
- `Settings` 缺少 `mongodb_host`
- `Settings` 缺少 `mongodb_runtime_host`
- `celery_broker_url` 未按 `REDIS_CELERY_BROKER_DB` 自动回落到 role-specific URL
- `pytest tests/unit/core/test_runtime_config_governance.py -q -o addopts=''`
- 结果：`2 failed, 8 passed`
- 失败原因：
- `ModuleNotFoundError: No module named 'src.utils.mongo_runtime_config'`
- 已确认通过的部分：
- Redis role-aware kwargs
- Redis manager 使用 role-aware kwargs
- 若显式设置 Redis role DB，相关运行时治理逻辑成立
- 第二轮结论:
- 1. 当前至少有 4 条并存的数据源入口，不宜直接做删除判断：
- `data_sources.json` Web 运行时主线
- `data_sources_registry.yaml + ConfigManager` 治理主线
- `data_sources_registry.yaml + DataSourceManagerV2` 注册表/测试主线
- `src.data_sources.factory` 局部业务主线
- 2. Mongo 相关资产已从“纯待判定”收口到更窄的状态：
- 主应用运行时未接入
- 但 Docker / README / 测试仍明确保留
- 因此当前更接近 `兼容保留（周边基础设施/测试口径）`，不是 `有效`
- 3. Redis 相关资产已可明确分成两类：
- `有效`：缓存、安全状态、Celery、readiness
- `待判定/配置漂移`：Celery URL 默认值与 role-aware 设计不完全一致
- 4. 到第二轮为止，仍然没有形成“可以立即安全删除”的对象名单。
- 当前最合理动作仍是继续收口入口与文档/测试漂移
- 而不是直接删除代码或基础设施文件
- 建议的第三轮方向:
- 1. 以“主应用实际注册的 API 路径”为索引，逐条列出：
- 使用 `data_sources.json` 的路由
- 使用 `data_sources_registry.yaml` 的路由
- 使用 `src.data_sources.factory` 的路由
- 2. 单独建立“漂移清单”：
- Mongo runtime tests 与现实现脱节
- `config/.env.example` 与 Redis 现实脱节
- PM2 端口/路径与当前门禁脱节
- Celery URL 默认值与 role-aware 设计脱节
- 3. 在第三轮再判断是否能产出首批低风险修复：
- 文档校正
- 测试校正
- 默认配置校正
- 仍然先不删运行资产

### `2026-03-12T00:00:27` [in_progress] dev-data-db-audit-claude
- Summary: Round 3 Route-Level Ownership Check

#### Scope
- 继续把“文件存在”与“路由已注册并真实调用”分开。
- 重点复核 `src.data_sources.factory`、风险路由和 dashboard 数据源归属，避免误把死路径算进运行面。

#### Notes
- 路由级修正:
- 1. `strategy_mgmt` 并不把 `src.data_sources` 用在核心 CRUD / 回测流程中。
- `web/backend/app/api/strategy_mgmt.py` 中 `get_business_source()` 只被 `/api/strategy-mgmt/health` 的 `Depends(get_data_source)` 使用
- 结论：这是 `局部健康检查依赖`，不是该模块的主业务数据入口
- 2. `api/risk/metrics.py` 是已注册活路径，且明确使用 `src.data_sources.factory.get_timeseries_source(source_type=\"mock\")`。
- `web/backend/app/api/risk/__init__.py` 已把 `metrics_router` 纳入 `router`
- `web/backend/app/api/risk_management.py` 只是兼容 shim，但 `router_registry.py` 注册的是这个 shim 导出的 `app.api.risk.router`
- 结论：`src.data_sources.factory` 在风险指标路径上是 `有效的局部运行依赖`
- 3. `web/backend/app/api/v1/risk/core.py` 当前不是主应用已注册路径。
- 虽然 `web/backend/app/api/v1/risk/__init__.py` 有聚合 router
- 但当前 `web/backend/app/api/v1/router.py` 并未 include `v1.risk.router`
- 结论：`api/v1/risk/*` 目前应视为 `未接主路由的存量资产`
- 4. `dashboard` 不走 `src.data_sources.factory`，而是走专用适配层。
- `web/backend/app/api/dashboard.py` 依赖 `app.api.dashboard_data_source.get_data_source`
- `web/backend/app/api/dashboard_data_source.py` 的主实现是 `RealBusinessDataSource`
- 结论：dashboard 是第四类独立数据接入面，和 `data_sources.json` / `data_sources_registry.yaml` / `src.data_sources.factory` 都不同
- 第三轮结论:
- 1. `src.data_sources.factory` 的运行面比第二轮判断更窄：
- 活路径主要是 `api/risk/metrics.py`
- `strategy_mgmt` 仅 `/health` 使用
- `api/v1/risk/core.py` 当前未接主路由
- 2. 主应用当前至少存在 4 类数据接入面：
- `config/data_sources.json` 驱动的 Web 数据源工厂
- `config/data_sources_registry.yaml` 驱动的治理/注册表入口
- `multi_source` 局部聚合入口
- `dashboard_data_source.RealBusinessDataSource` 专用入口
- 3. 到第三轮为止，`src.data_sources.factory` 仍不能删，但已可从“大面积运行主线”降到“窄面兼容/局部运行链路”。

### `2026-03-12T00:00:28` [in_progress] dev-data-db-audit-claude
- Summary: Round 4 Runtime Config Drift Fixes

#### Scope
- 依据第二轮、第三轮已确认的低风险漂移点，先修复 runtime config 兼容层与 `.env` 文档口径。
- 不做资产删除，不改业务路由。

#### Completed
- | 类型 | 文件 | 修复内容 |
- | --- | --- | --- |
- | 运行时配置兼容 | `web/backend/app/core/config.py` | 为 `Settings` 补充 Mongo 兼容字段：`mongodb_host`、`mongodb_port`、`mongodb_root_username`、`mongodb_root_password`、`mongodb_database`、`mongodb_auth_source`，以及兼容属性 `mongodb_runtime_host`、`mongodb_runtime_port`、`mongodb_connection_kwargs` |
- | Celery 默认值收口 | `web/backend/app/core/config.py` | 将 `celery_broker_url` / `celery_result_backend` 改为“空值时按 role-aware Redis DB 自动回落”，修复默认值与 `REDIS_CELERY_*_DB` 脱节 |
- | Mongo helper 补全 | `src/utils/mongo_runtime_config.py` | 新增 Mongo runtime helper，支持标准环境变量与 legacy `MONGODB_IP` / `USERNAME` / `PASSWORD` 回落 |
- | 文档口径修正 | `config/.env.example` | 删除“应用层缓存替代 Redis”的旧说法，改为当前 `TDengine + PostgreSQL + Redis` 运行口径，并补充 Redis role DB 与 Mongo 兼容环境变量说明 |

#### Verification Evidence
- `pytest tests/unit/core/test_web_backend_runtime_settings.py -q -o addopts=''`
- 结果：`5 passed`
- `pytest tests/unit/core/test_runtime_config_governance.py -q -o addopts=''`
- 结果：`10 passed`
- `pytest tests/unit/core/test_web_backend_runtime_settings.py tests/unit/core/test_runtime_config_governance.py -q -o addopts=''`
- 结果：`15 passed`
- 备注：存在 6 条 warning，均为仓库既有第三方/历史 Pydantic 与 taos 依赖告警，不是本次回归

#### Current Status
- 1. 第二轮确认的两类 runtime 漂移已修复：
- Mongo compatibility helper / Settings 字段缺失
- Celery URL 默认回落未使用 role-aware Redis DB
- 2. 文档漂移已开始收口，但只修了 `config/.env.example`。
- 根 `.env.example`
- PM2 配置
- 其他 README / Docker 文档
- 仍需后续继续对齐
- 3. 当前仍未产生“可删资产”清单。
- 本轮修复强化了兼容层证据
- 删除动作仍应延后到入口、文档、测试完全收口之后

#### Notes
- Impact Note:
- 修改前已对 `web/backend/app/core/config.py:Settings` 做 GitNexus impact 分析。
- 风险级别：`HIGH`
- 采取的控制策略：
- 不删除现有字段
- 仅补兼容属性
- 仅在 Celery URL 未显式配置时做默认回落

### `2026-03-12T00:00:29` [in_progress] dev-data-db-audit-claude
- Summary: Round 5 Env And PM2 Drift Fixes

#### Scope
- 继续处理低风险漂移，目标是补齐根 `.env.example` 与 PM2 默认开发配置的当前口径。
- 不改业务代码，不删资产。

#### Completed
- | 类型 | 文件 | 修复内容 |
- | --- | --- | --- |
- | 根环境模板收口 | `.env.example` | 补充 Redis role DB、Celery URL、Mongo 兼容环境变量，使根模板与当前 runtime config 兼容层保持一致 |
- | PM2 路径/端口收口 | `config/pm2/ecosystem.config.js` | 移除对 `/opt/claude/mystocks_spec` 的硬编码，改为基于 `__dirname` 动态解析项目根；默认端口调整为 `frontend=3020/3021`、`backend=8020/8021`；前后端 cwd、PYTHONPATH 与健康检查地址均改为相对当前仓库根生成 |
- | PM2 前端启动方式修正 | `config/pm2/ecosystem.config.js` | 将前端从依赖 `PORT=3002` 的不稳定方式改为显式 `npm run dev -- --host 0.0.0.0 --port <FRONTEND_PORT>` |

#### Verification Evidence
- `node -c config/pm2/ecosystem.config.js`
- 结果：通过
- `node -e "const cfg=require('./config/pm2/ecosystem.config.js'); console.log(cfg.apps.map(a=>a.name+':' + a.cwd).join('\\n'))"`
- 结果：输出的 `cwd` 已指向当前 worktree：
- `mystocks-frontend:/opt/claude/mystocks_spec-data-db-audit/web/frontend`
- `mystocks-backend:/opt/claude/mystocks_spec-data-db-audit/web/backend`
- 各数据同步任务指向 `/opt/claude/mystocks_spec-data-db-audit`

#### Current Status
- 1. `config/pm2/ecosystem.config.js` 已不再绑定旧仓库绝对路径和旧端口。
- 2. 根 `.env.example` 与 `config/.env.example` 的 Redis/Celery/Mongo 兼容字段口径已基本对齐。
- 3. 仍待后续收口的 PM2 / 运维漂移：
- `web/backend/ecosystem.config.js`
- `config/pm2/ecosystem.production.config.js`
- 监控栈文档中的 `8000` 端口口径

### `2026-03-13T00:00:30` [in_progress] dev-data-db-audit-claude
- Summary: Round 6 Monitoring And PM2 Production Convergence

#### Scope
- 继续收口 `config/**` 范围内的生产/测试 PM2 配置与监控栈配置、文档口径。
- 仍然不做删除。

#### Completed
- | 类型 | 文件 | 修复内容 |
- | --- | --- | --- |
- | 生产 PM2 配置收口 | `config/pm2/ecosystem.production.config.js` | 改为基于 `__dirname` 解析当前仓库根；默认前后端端口收口到 `3020/8020`；去除旧 `/opt/claude/mystocks_spec` 依赖；`post-deploy` 指向 `config/pm2/ecosystem.production.config.js` |
- | 测试 PM2 配置收口 | `config/pm2/pm2.config.js` | 改为动态仓库根、`3020/8020` 端口、当前 worktree 路径；前端 `VITE_API_BASE_URL` / `VITE_WS_URL` 与后端口径对齐 |
- | Prometheus 抓取端口收口 | `config/monitoring-stack/config/prometheus.yml` | 将残余 `host.docker.internal:8000` / `localhost:8000` 抓取目标统一改为 `8020` |
- | AlertManager 注释口径收口 | `config/monitoring-stack/config/alertmanager.yml` | webhook 示例地址从 `8000` 改为 `8020` |
- | 监控栈文档收口 | `config/monitoring-stack/{README,DEPLOYMENT,MONITORING_VERIFICATION_COMPLETE_REPORT}.md` | 收口旧 `8000` 端口与旧 `/opt/claude/mystocks_spec/monitoring-stack` 路径引用 |

#### Verification Evidence
- `node -c config/pm2/ecosystem.production.config.js`
- 结果：通过
- `node -c config/pm2/pm2.config.js`
- 结果：通过

#### Current Status
- 1. `config/pm2` 下三份主配置已部分收口：
- `ecosystem.config.js`
- `ecosystem.production.config.js`
- `pm2.config.js`
- 2. `config/monitoring-stack` 的主配置和主要活跃文档已从 `8000` 切换到 `8020`。
- 3. 仍然残留的配置债务主要集中在：
- `config/pm2/ecosystem.enhanced.config.js`
- `config/pm2/ecosystem.playwright*.js`
- `config/monitoring-stack/MONITORING_STATUS.md`
- `config/monitoring-stack/DEPLOYMENT_NOTES.md`

#### Notes
- `python` 解析 YAML:
- `config/monitoring-stack/config/prometheus.yml`
- `config/monitoring-stack/config/alertmanager.yml`
- 结果：均通过 `yaml.safe_load`
- `python` 扫描活跃监控配置/文档:
- 未发现 `localhost:8000`
- 未发现 `host.docker.internal:8000`
- 未发现旧路径 `/opt/claude/mystocks_spec/monitoring-stack`

### `2026-03-13T00:00:31` [in_progress] dev-data-db-audit-claude
- Summary: Round 7 Active Monitoring Docs Sweep

#### Scope
- 继续在 `config/**` 范围内做活跃配置/文档的端口与路径收口。
- 本轮刻意不继续扩到 `ecosystem.enhanced.config.js` 与 Playwright PM2 配置，避免把范围拉散。

#### Completed
- | 类型 | 文件 | 修复内容 |
- | --- | --- | --- |
- | Prometheus 补漏 | `config/monitoring-stack/config/prometheus.yml` | 将 `wencai/tasks/multi-source` 三个残余 job 的 `8000` target 统一改为 `8020` |
- | AlertManager 注释补漏 | `config/monitoring-stack/config/alertmanager.yml` | 统一 webhook 示例端口到 `8020` |
- | 活跃状态文档收口 | `config/monitoring-stack/MONITORING_STATUS.md` | 修复旧 `monitoring-stack` 仓库路径引用 |
- | 活跃监控文档收口 | `config/monitoring-stack/{README,DEPLOYMENT,MONITORING_VERIFICATION_COMPLETE_REPORT}.md` | 复核并确保已改文件中不再残留 `8000` 或旧 `monitoring-stack` 路径 |

#### Verification Evidence
- `node -c config/pm2/ecosystem.production.config.js && node -c config/pm2/pm2.config.js`
- 结果：通过

#### Current Status
- 1. 活跃的 PM2 主配置和监控栈主配置/主文档已经基本对齐到：
- 后端：`8020`
- 前端：`3020`
- 当前 worktree 路径
- 2. 仍待后续处理的主要配置债务：
- `config/pm2/ecosystem.enhanced.config.js`
- `config/pm2/ecosystem.playwright*.js`
- `config/monitoring-stack/DEPLOYMENT_NOTES.md`
- 3. 到目前为止，本分支仍没有形成“可以立即删除”的资产列表；
- 现阶段更适合继续做配置/文档/测试口径收口，再进入删除判定。

#### Notes
- `python` 解析 YAML:
- `config/monitoring-stack/config/prometheus.yml`
- `config/monitoring-stack/config/alertmanager.yml`
- 结果：通过
- `python` 扫描以下活跃文件:
- `config/monitoring-stack/config/prometheus.yml`
- `config/monitoring-stack/config/alertmanager.yml`
- `config/monitoring-stack/README.md`
- `config/monitoring-stack/DEPLOYMENT.md`
- `config/monitoring-stack/MONITORING_STATUS.md`
- `config/monitoring-stack/MONITORING_VERIFICATION_COMPLETE_REPORT.md`
- `config/pm2/ecosystem.config.js`
- `config/pm2/ecosystem.production.config.js`
- `config/pm2/pm2.config.js`
- 结果：未发现以下残留模式：
- `localhost:8000`
- `host.docker.internal:8000`
- `/opt/claude/mystocks_spec/monitoring-stack`
- `/opt/claude/mystocks_spec/web/backend`
- `/opt/claude/mystocks_spec/web/frontend`

### `2026-03-13T00:00:32` [in_progress] dev-data-db-audit-claude
- Summary: Round 8 PM2 Worktree Decoupling Sweep

#### Scope
- 收口剩余 `config/pm2` 中仍绑定旧 worktree 绝对路径的配置文件。
- 本轮只改路径与默认端口口径，不改 Playwright 或增强版配置的业务语义。

#### Completed
- | 类型 | 文件 | 修复内容 |
- | --- | --- | --- |
- | 增强 PM2 配置 | `config/pm2/ecosystem.enhanced.config.js` | 新增 `projectRoot/frontendCwd/backendCwd/gpuApiCwd` 与 `frontendPort/backendPort` 常量；去除旧 `/opt/claude/mystocks_spec`、`3002`、`8000`、`3000` 绑定 |
- | Playwright PM2 配置 | `config/pm2/ecosystem.playwright*.js` | 为所有活跃 Playwright PM2 配置新增动态 `projectRoot`，统一替换旧 `cwd: '/opt/claude/mystocks_spec'` |

#### Current Status
- 1. `config/pm2` 下当前活跃的主配置与测试配置已基本完成 worktree 解耦。
- 2. 仍可继续处理但优先级更低的项：
- `config/monitoring-stack/DEPLOYMENT_NOTES.md`
- 其他历史报告/说明文档中的旧端口口径
- 3. 到目前为止，数据源/数据库/缓存治理阶段已从“纯盘点”推进到“配置与文档漂移修复”，但仍未进入删除动作。

#### Notes
- `node -c` 通过:
- `config/pm2/ecosystem.enhanced.config.js`
- `config/pm2/ecosystem.playwright.config.js`
- `config/pm2/ecosystem.playwright.p0.config.js`
- `config/pm2/ecosystem.playwright.p1.config.js`
- `config/pm2/ecosystem.playwright.p1.fixed.config.js`
- `config/pm2/ecosystem.playwright.p2.config.js`
- `python` 文本扫描:
- 未发现上述文件中残留 `/opt/claude/mystocks_spec`

### `2026-03-13T00:00:33` [in_progress] dev-data-db-audit-claude
- Summary: Round 9 Active Deployment Docs Port Convergence

#### Scope
- 收口活跃部署/运维/README 文档中的旧固定端口与旧“端口范围”说法。
- 仅改文档，不改运行逻辑。

#### Completed
- | 类型 | 文件 | 修复内容 |
- | --- | --- | --- |
- | 部署文档收口 | `docs/deployment/README.md` | 将“8000-8010 / 3000-3010 自动选端口”改为固定 `8020/8021` 与 `3020/3021`；命令与访问地址同步更新 |
- | 运维部署文档收口 | `docs/operations/deployment-guide.md` | 同步改为固定 `8020/8021` 与 `3020/3021` 口径 |
- | Web README 收口 | `web/README.md` | 将旧 “固定端口 3000/8000” 全部改为当前 `3020/3021` 与 `8020/8021`，并同步启动命令与排障命令 |

#### Current Status
- 1. 活跃部署/运维说明文档已基本统一到：
- 前端：`3020`
- 后端：`8020`
- 备用端口：`3021/8021`
- 2. 当前剩余主要是历史/次级文档债务，而不是主入口文档债务。
- 3. 现阶段已具备进入“首批保守删除候选清单”的前提，但建议先单独整理候选项与删除依据，再决定是否执行删除。

#### Notes
- `python` 文本扫描:
- `docs/deployment/README.md`
- `docs/operations/deployment-guide.md`
- `web/README.md`
- 结果：未发现以下残留模式：
- `localhost:3000`
- `3000-3010`
- `8000-8010`
- `固定端口 8000`
- `固定端口 3000`

### `2026-03-13T00:00:34` [in_progress] dev-data-db-audit-claude
- Summary: Round 10 Conservative Deletion Candidates Inventory

#### Scope
- 生成首批“保守删除候选清单”，仍然只做清单，不执行删除。
- 候选对象限定在本任务 scope 内，且必须满足以下至少两项：
- 明确是时间戳备份副本
- 存在同名/同职责 canonical 文件
- 在 `src/config/scripts/tests/web/docs` 的活跃源码中无直接引用
- 与当前架构口径（如 MySQL 已移除）明显不一致

#### Notes
- 首批保守删除候选:
- | 对象 | 功能树状态 | 删除判断 | 依据 |
- | --- | --- | --- | --- |
- | `src/adapters/akshare_adapter.py.backup_1767777516` | `重复冗余` | `可删候选` | 时间戳备份副本；canonical 文件为 `src/adapters/akshare_adapter.py`；在活跃源码检索中未发现直接引用，只有报告/质量产物提及 |
- | `src/adapters/financial_adapter.py.backup_1767777515` | `重复冗余` | `可删候选` | 时间戳备份副本；canonical 文件为 `src/adapters/financial_adapter.py`；活跃源码无直接引用，仅报告/质量产物提及 |
- | `src/core/config_driven_table_manager.py.backup_20251108` | `重复冗余` | `可删候选` | 时间戳备份副本；canonical 文件为 `src/core/config_driven_table_manager.py`；当前主实现已存在且已被实际引用，备份副本未进入主链路 |
- | `src/core/data_source_manager_v2.py.backup_1767777516` | `重复冗余` | `可删候选` | 时间戳备份副本；canonical 对应能力已迁入 `src/core/data_source/base.py` / `src/core/data_source/config_manager.py` / 当前 V2 管理栈；活跃源码无直接引用 |
- 明确不删 / 暂不列入删除候选:
- | 对象 | 状态 | 保留原因 |
- | --- | --- | --- |
- | `src/storage/database/execute_example_mysql_only.py` | `待判定` | 文件名带 `mysql_only`，但内容实际在跑 PostgreSQL 示例；当前主要被历史文档/质量报告引用。它更像“误导性命名的示例脚本”，直接删除风险高，优先建议后续做“重命名或归档”判定 |
- | `src/adapters/legacy_adapter.py` | `兼容保留` | 仍被 `scripts/dev/examples/real_project_application/...` 指向，属于演示/重构样例链路，不满足“代码路径可安全移除” |
- | `src/adapters/akshare/legacy_market_data.py` | `兼容保留` | 文件头明确声明“保留用于向后兼容”；多份历史完成报告把它作为 legacy 同步函数模块记录，当前不能仅凭文件名删除 |
- | `config/sina_finance_only.yaml` | `兼容保留` | 被 `scripts/quick_health_check.sh` 与 `scripts/tests/legacy/test_sina_integration_final.py` 直接使用，是特化配置入口，不满足安全移除条件 |
- | `config/data_sources/sina_finance.yaml` | `待判定` | 当前主 registry 未加载它，但它属于拆分式 loader 计划的一部分；在拆分治理正式下线前不应删除 |
- | `config/datasource.yaml.example` | `兼容保留` | 仍有 archived OpenSpec 任务将其作为交付物记录；虽然主应用未直接接入，但尚不满足“正式下线”证据 |
- 当前建议:
- 1. 如果下一轮进入真正删除动作，优先只处理上面 4 个时间戳备份副本。
- 2. `execute_example_mysql_only.py` 不建议直接删，优先做：
- 是否改名为 PostgreSQL example
- 是否移入 `archive/` 或 `scripts/examples/`
- 3. `legacy_*` 与 `sina_finance*` 相关对象目前仍保持保守，不进入删除执行面。

### `2026-03-13T00:00:35` [in_progress] dev-data-db-audit-claude
- Summary: Round 11 First Conservative Cleanup Execution

#### Scope
- 执行首批真正删除动作，但仅限上一轮已确认的 4 个时间戳备份副本。
- 仍不触碰 `legacy_*`、`sina_finance*`、`execute_example_mysql_only.py`。

#### Current Status
- 1. 当前已完成首批低风险实际清理。
- 2. 仍未进入删除执行面的对象：
- `src/storage/database/execute_example_mysql_only.py`
- `src/adapters/legacy_adapter.py`
- `src/adapters/akshare/legacy_market_data.py`
- `config/sina_finance_only.yaml`
- `config/data_sources/sina_finance.yaml`
- `config/datasource.yaml.example`
- 3. 后续若继续删除，应先单独处理“命名误导示例脚本”和“legacy/拆分计划资产”的归档或重命名策略。

#### Notes
- Removed:
- `src/adapters/akshare_adapter.py.backup_1767777516`
- `src/adapters/financial_adapter.py.backup_1767777515`
- `src/core/config_driven_table_manager.py.backup_20251108`
- `src/core/data_source_manager_v2.py.backup_1767777516`
- Removal Basis:
- 1. 以上 4 个对象均为带时间戳的备份副本。
- 2. 均存在对应 canonical 主文件或主实现链路。
- 3. 在活跃源码范围检索中未发现直接引用，仅历史报告/质量产物提及。
- 4. 根据清理标准，可归入功能树状态 `重复冗余`。
- `python` 检查文件存在性:
- `src/adapters/akshare_adapter.py.backup_1767777516 -> False`
- `src/adapters/financial_adapter.py.backup_1767777515 -> False`
- `src/core/config_driven_table_manager.py.backup_20251108 -> False`
- `src/core/data_source_manager_v2.py.backup_1767777516 -> False`

### `2026-03-13T00:00:36` [in_progress] dev-data-db-audit-claude
- Summary: Round 12 Misleading Example Rename

#### Scope
- 处理命名误导但不适合直接删除的示例脚本。
- 当前只处理 `execute_example_mysql_only.py`。

#### Notes
- Impact Note:
- GitNexus upstream impact on file `src/storage/database/execute_example_mysql_only.py`
- 风险级别：`LOW`
- 结果：`impactedCount=0`
- Implemented Fix:
- `src/storage/database/execute_example_mysql_only.py`
- → `src/storage/database/execute_example_postgresql_only.py`
- Basis:
- 1. 文件内容实际是 PostgreSQL-only 示例，不再包含 MySQL-only 语义。
- 2. 活跃源码检索未发现上游引用。
- 3. 旧文件名主要只出现在历史报告、质量产物和代码盘点产物中。
- 4. 因此更适合改名，而不是保留误导性名称或直接删除。
- `python` 文件存在性检查:
- `src/storage/database/execute_example_mysql_only.py -> False`
- `src/storage/database/execute_example_postgresql_only.py -> True`
- `rg` 活跃源码范围检索:
- 未发现旧文件名在活跃源码中的直接引用
- 旧文件名仅残留于历史报告/质量产物
- Status Update:
- `src/storage/database/execute_example_mysql_only.py`
- 状态由 `待判定`
- 更新为 `已通过重命名收口`
- 仍保守保留:
- `src/adapters/legacy_adapter.py`
- `src/adapters/akshare/legacy_market_data.py`
- `config/sina_finance_only.yaml`
- `config/data_sources/sina_finance.yaml`
- `config/datasource.yaml.example`

### `2026-03-13T00:00:37` [in_progress] dev-data-db-audit-claude
- Summary: Round 13 Legacy Compatibility Fix

#### Scope
- 对已判定为“兼容保留”的 legacy 资产做最小必要修复，而不是删除。
- 当前只处理 `src/adapters/akshare/legacy_market_data.py`。

#### Notes
- Impact Note:
- `legacy_market_data.py` 的 GitNexus upstream impact 为 `LOW`，`impactedCount=0`
- 文件仍通过 `src/adapters/akshare/__init__.py` 对外暴露 legacy 函数，因此不适合删除
- Implemented Fix:
- | 文件 | 问题 | 修复 |
- | --- | --- | --- |
- | `src/adapters/akshare/legacy_market_data.py` | `_retry_api_call` 名义上是“同步版本”，实际返回 `async wrapper`，导致 legacy 同步函数会返回 coroutine | 改为真正的同步重试逻辑：`time.sleep` + 同步 `wrapper` + 直接 `func(*args, **kwargs)` |
- 最小化本地验证脚本执行结果:
- `result ok`
- `call_count 1`
- `is_coroutine False`
- Status Update:
- 1. `src/adapters/akshare/legacy_market_data.py` 继续保持 `兼容保留`。
- 2. 但它已不再是“坏掉的兼容层”，当前至少满足同步调用语义。
- 3. `src/adapters/legacy_adapter.py` 仍保持不动，继续视为示例/重构演示资产。

### `2026-03-13T00:00:38` [in_progress] dev-data-db-audit-claude
- Summary: Round 14 Remaining Candidate Closure

#### Scope
- 收口最后两类仍未最终定性的对象：
- `sina_finance*` 配置
- `config/datasource.yaml.example`
- 本轮只更新结论，不执行删除。

#### Current Status
- 1. 本轮之后，原先列出的高不确定对象已基本全部落入明确分类。
- 2. 当前若再继续推进，重点就不再是“盘点”，而是：
- 是否要对 `兼容保留` 项做归档/隔离
- 是否要继续统一历史报告中的旧文件名引用
- 是否要准备提交/分批提交

#### Notes
- 结论更新:
- | 对象 | 新结论 | 依据 |
- | --- | --- | --- |
- | `config/sina_finance_only.yaml` | `兼容保留` | 被 `scripts/quick_health_check.sh` 与 `scripts/tests/legacy/test_sina_integration_final.py` 直接使用；不是孤儿配置 |
- | `config/data_sources/sina_finance.yaml` | `兼容保留` | 由 `config/sina_finance_only.yaml` 的 `load_sources: [sina_finance]` 间接加载；因此不是无主拆分文件 |
- | `config/datasource.yaml.example` | `兼容保留` | 对应 `DataSourceRegistry` / `src/api/datasource/routes.py` 这条模板化管理链路；虽然不属当前 Web 主入口，但仍有真实 API/测试/模块存在 |
- Supporting Evidence:
- 1. `config/sina_finance_only.yaml`
- 含 `load_sources: [sina_finance]`
- 是 `config.data_sources_loader.DataSourcesLoader` 可直接消费的主配置文件
- 2. `config/data_sources/sina_finance.yaml`
- 包含 `sina_finance_stock_ratings` 数据源定义
- 被 `test_sina_integration_final.py` 通过 `loader.main_config_file = loader.config_dir / "sina_finance_only.yaml"` 的方式间接加载
- 3. `config/datasource.yaml.example`
- 对应 `src/core/datasource/registry.py:DataSourceRegistry`
- `src/api/datasource/routes.py` 存在完整 `/api/datasources` CRUD / health / metrics 路由
- 相关 `tests/unit/test_datasource/*` 和 `tests/api/file_tests/test_data_source_registry_api.py` 仍在
- Final Remaining Inventory Status:
- `可删/已执行`
- 4 个时间戳备份副本已删除
- `已通过重命名收口`
- `execute_example_mysql_only.py` → `execute_example_postgresql_only.py`
- `兼容保留`
- `src/adapters/legacy_adapter.py`
- `src/adapters/akshare/legacy_market_data.py`
- `config/sina_finance_only.yaml`
- `config/data_sources/sina_finance.yaml`
- `config/datasource.yaml.example`

### `2026-03-13T00:00:39` [in_progress] dev-data-db-audit-claude
- Summary: Compatibility Retention Archival Plan

#### Scope
- 将兼容保留资产的后续处理方式固化为可执行方案。
- 本轮只出方案，不执行新的迁移。

#### Current Status
- 1. “兼容保留资产的归档/隔离方案”已经独立成文，可按批次执行。
- 2. 当前可以选择进入下一轮实际迁移：
- 先迁 `legacy_adapter.py`
- 再做 `legacy_market_data.py` 的 `compat/` 隔离
- 3. `sina_finance*` 与 `datasource.yaml.example` 仍建议晚于代码兼容资产迁移。

#### Notes
- 新增方案文档:
- `reports/governance/2026-03-13-compatibility-retention-archival-plan.md`
- Plan Summary:
- 1. `src/adapters/legacy_adapter.py`
- 定位：`archive-ready`
- 建议目标：`archive/code-compatibility/examples/legacy_adapter.py`
- 2. `src/adapters/akshare/legacy_market_data.py`
- 定位：`in-source isolation`
- 建议目标：`src/adapters/akshare/compat/legacy_market_data.py`
- 3. `config/sina_finance_only.yaml`
- 定位：`config compatibility hold`
- 后续建议目标：`config/compatibility/sina_finance/main.yaml`
- 4. `config/data_sources/sina_finance.yaml`
- 定位：`config compatibility hold`
- 后续建议目标：`config/compatibility/sina_finance/source.yaml`
- 5. `config/datasource.yaml.example`
- 定位：`config compatibility hold`
- 后续建议目标：`config/templates/datasource-registry.yaml.example`

### `2026-03-13T00:00:40` [in_progress] dev-data-db-audit-claude
- Summary: Round 15 Compatibility Isolation Execution

#### Scope
- 执行归档/隔离方案中的前两步：
- `legacy_adapter.py` 归档
- `legacy_market_data.py` 隔离到 `compat/`

#### Notes
- Implemented Changes:
- | 类型 | 动作 |
- | --- | --- |
- | 归档 | `src/adapters/legacy_adapter.py` → `archive/code-compatibility/examples/legacy_adapter.py` |
- | 活跃引用收口 | `scripts/dev/examples/real_project_application/real_project_application_methods/part1.py` 中的 `refactor_module` 路径改为归档后的新位置 |
- | 兼容隔离 | `src/adapters/akshare/legacy_market_data.py` 的主实现移动到 `src/adapters/akshare/compat/legacy_market_data.py` |
- | 兼容壳 | 新增 `src/adapters/akshare/legacy_market_data.py` 作为薄兼容 shim，继续 re-export 原函数 |
- | 兼容导出 | 新增 `src/adapters/akshare/compat/__init__.py`，并将 `src/adapters/akshare/__init__.py` 改为从 `compat` 导出 legacy 函数 |
- 文件存在性检查:
- `src/adapters/legacy_adapter.py -> False`
- `archive/code-compatibility/examples/legacy_adapter.py -> True`
- `src/adapters/akshare/compat/legacy_market_data.py -> True`
- `src/adapters/akshare/legacy_market_data.py -> True`
- 活跃源码扫描结果:
- `archive/code-compatibility/examples/legacy_adapter.py` 已替换唯一活跃路径引用
- `src/adapters/akshare/legacy_market_data.py` 在活跃源码中仅作为兼容壳存在
- `src/adapters/akshare/__init__.py` 已切换到 `.compat`
- 语法验证:
- `python -m py_compile src/adapters/akshare/__init__.py`
- `python -m py_compile src/adapters/akshare/legacy_market_data.py`
- `python -m py_compile src/adapters/akshare/compat/__init__.py`
- `python -m py_compile src/adapters/akshare/compat/legacy_market_data.py`
- `python -m py_compile scripts/dev/examples/real_project_application/real_project_application_methods/part1.py`
- 结果：通过
- Status Update:
- 1. `legacy_adapter.py`
- 状态由 `兼容保留`
- 更新为 `已归档隔离`
- 2. `legacy_market_data.py`
- 状态仍为 `兼容保留`
- 但当前已完成 `in-source isolation`
- 3. 下一步若继续执行兼容资产方案，应轮到：
- `config/sina_finance_only.yaml`
- `config/data_sources/sina_finance.yaml`
- `config/datasource.yaml.example`

### `2026-03-13T00:00:41` [in_progress] dev-data-db-audit-claude
- Summary: Round 16 Compatibility Config Relocation

#### Scope
- 执行兼容配置资产迁移：
- `sina_finance*`
- `datasource.yaml.example`
- 不修改 loader 主逻辑，只更新明确消费者。

#### Notes
- Implemented Changes:
- | 类型 | 动作 |
- | --- | --- |
- | 兼容配置迁移 | `config/sina_finance_only.yaml` → `config/compatibility/sina_finance/main.yaml` |
- | 子配置迁移 | `config/data_sources/sina_finance.yaml` → `config/compatibility/sina_finance/sina_finance.yaml` |
- | 模板迁移 | `config/datasource.yaml.example` → `config/templates/datasource-registry.yaml.example` |
- | 脚本消费者更新 | `scripts/quick_health_check.sh` 中的检查路径切换到 `config/compatibility/sina_finance/main.yaml` |
- | 测试消费者更新 | `scripts/tests/legacy/test_sina_integration_final.py` 同时更新 `main_config_file` 与 `sources_dir` 到 `config/compatibility/sina_finance/` |
- 文件存在性检查:
- `config/compatibility/sina_finance/main.yaml -> True`
- `config/compatibility/sina_finance/sina_finance.yaml -> True`
- `config/templates/datasource-registry.yaml.example -> True`
- `config/sina_finance_only.yaml -> False`
- `config/data_sources/sina_finance.yaml -> False`
- `config/datasource.yaml.example -> False`
- `DataSourcesLoader` 最小验证:
- `loader.main_config_file = config/compatibility/sina_finance/main.yaml`
- `loader.sources_dir = config/compatibility/sina_finance`
- 结果：成功加载 `sina_finance_stock_ratings`
- 活跃源码路径扫描:
- 未发现旧路径
- `config/sina_finance_only.yaml`
- `config/data_sources/sina_finance.yaml`
- `config/datasource.yaml.example`
- 唯一残留为 archived OpenSpec 任务记录，可接受
- 语法验证:
- `python -m py_compile scripts/tests/legacy/test_sina_integration_final.py`
- 结果：通过
- Status Update:
- 1. `sina_finance*` 兼容配置已完成物理隔离。
- 2. `datasource.yaml.example` 已完成模板目录收口。
- 3. 至此，原先列为“兼容保留”的配置资产已从散落状态收口到：
- `config/compatibility/`
- `config/templates/`

### `2026-03-13T00:00:42` [in_progress] dev-data-db-audit-claude
- Summary: Final Change Classification

#### Scope
- 将当前 worktree 的全部改动整理成提交/评审可直接使用的分类清单。
- 不新增行为改动。

#### Current Status
- 1. 当前分支已经具备“按分类准备提交”的条件。
- 2. 如需继续，下一步不再是盘点，而是：
- 提交前最终验证
- 或按分类拆分提交

#### Notes
- 新增分类清单:
- `reports/governance/2026-03-13-final-change-classification.md`
- Covered Buckets:
- Runtime compatibility fixes
- PM2 convergence
- Monitoring stack config/doc convergence
- Active deployment/operations docs convergence
- Low-risk redundant cleanup
- Example/compatibility path cleanup
- Compatibility isolation execution
- Compatibility config relocation
- Audit trail / reporting

### `2026-03-13T00:00:43` [verified] dev-data-db-audit-claude
- Summary: Final Verification Snapshot

#### Scope
- 对当前改动面执行提交前定向验证。
- 验证范围只覆盖本轮实际变更，不做全仓回归。

#### Current Status
- 1. 当前变更已达到“可进入提交前复核”的状态。
- 2. 尚未执行的项：
- 全仓回归测试
- PM2 实际启动验证
- Git 提交/拆分提交

#### Notes
- Verification Commands:
- `pytest tests/unit/core/test_web_backend_runtime_settings.py tests/unit/core/test_runtime_config_governance.py -q -o addopts=''`
- `python -m py_compile web/backend/app/core/config.py src/utils/mongo_runtime_config.py src/storage/database/execute_example_postgresql_only.py src/adapters/akshare/__init__.py src/adapters/akshare/legacy_market_data.py src/adapters/akshare/compat/__init__.py src/adapters/akshare/compat/legacy_market_data.py scripts/tests/legacy/test_sina_integration_final.py scripts/dev/examples/real_project_application/real_project_application_methods/part1.py archive/code-compatibility/examples/legacy_adapter.py`
- `node -c config/pm2/ecosystem.config.js`
- `node -c config/pm2/ecosystem.production.config.js`
- `node -c config/pm2/pm2.config.js`
- `node -c config/pm2/ecosystem.enhanced.config.js`
- `node -c config/pm2/ecosystem.playwright.config.js`
- `node -c config/pm2/ecosystem.playwright.p0.config.js`
- `node -c config/pm2/ecosystem.playwright.p1.config.js`
- `node -c config/pm2/ecosystem.playwright.p1.fixed.config.js`
- `node -c config/pm2/ecosystem.playwright.p2.config.js`
- `python` + `yaml.safe_load`:
- `config/monitoring-stack/config/prometheus.yml`
- `config/monitoring-stack/config/alertmanager.yml`
- `config/compatibility/sina_finance/main.yaml`
- `config/compatibility/sina_finance/sina_finance.yaml`
- `config/templates/datasource-registry.yaml.example`
- `.env` 模板格式检查（按 dotenv 语法，不按 YAML）:
- `.env.example`
- `config/.env.example`
- Verification Results:
- 1. Runtime config tests:
- `15 passed`
- warnings: `6`
- 说明：warning 为仓库既有 Pydantic / taos 依赖告警，不是本次回归
- 2. Python syntax checks:
- 通过
- 3. PM2 config syntax checks:
- 通过
- 4. YAML parse checks:
- 通过
- 5. `.env` template format checks:
- `.env.example -> valid`
- `config/.env.example -> valid`
- 6. Residual path / port / old-name scans:
- 活跃源码与活跃配置中未再发现：
- `localhost:8000`
- `host.docker.internal:8000`
- `/opt/claude/mystocks_spec/monitoring-stack`
- `/opt/claude/mystocks_spec/web/backend`
- `/opt/claude/mystocks_spec/web/frontend`
- `config/sina_finance_only.yaml`
- `config/data_sources/sina_finance.yaml`
- `config/datasource.yaml.example`
- `execute_example_mysql_only.py`

### `2026-03-13T00:00:44` [verified] dev-data-db-audit-claude
- Summary: Split Commit Playbook

#### Scope
- 由于当前沙箱无法写 worktree git metadata，无法直接完成 `git commit`。
- 改为输出可直接执行的拆分提交操作手册。

#### Notes
- 新增:
- `reports/governance/2026-03-13-split-commit-playbook.md`
- 1. 当前已 staged 的第一批文件：
- `.env.example`
- `config/.env.example`
- `web/backend/app/core/config.py`
- `src/utils/mongo_runtime_config.py`
- 2. playbook 已提供：
- 每批提交的文件边界
- `git restore --staged .` 重建 staging 的命令
- 推荐 commit message
- 3. 若在可写 git metadata 环境下执行，可直接按 playbook 顺序完成拆分提交。
