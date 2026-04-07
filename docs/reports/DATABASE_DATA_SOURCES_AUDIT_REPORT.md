# MyStocks 数据库与数据源配置审计报告

> **历史分析说明**:
> 本文件是阶段性分析、审计、评估或复盘材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内问题分级、差距判断、风险结论、审阅意见和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。


> 审计日期: 2026-03-12
> 审计分支: `main`
> 审计范围: 数据库连接配置、数据源注册表、运行时配置入口、当前环境可用性
> 审计方式: 仓库静态核对 + 当前 `.env` 环境实测
> 审计结论: 报告口径已修正为“仓库事实”和“当前环境实测”分离；截至 2026-03-12 当前会话，`CFG-001`、`CFG-002`、访问层导入问题、旧 JSON 结构兼容问题与后端重复配置副本已完成第一轮整改，剩余重点为 Redis 用途矩阵治理与 JSON/YAML 配置职责边界收敛

---

## 一、执行摘要

本次复核后，可以确认以下事实：

1. 当前环境下，`PostgreSQL`、`TimescaleDB` 扩展、`TDengine` 可连接；`Redis` 已由用户确认可连接。
2. `src/storage/database/connection_manager.py` 的 PostgreSQL 回退端口已统一为 `5432`，并已与模板 `config/.env.data_sources.example` 同步。
3. 根目录 `config/data_sources.json` 不是可直接删除的冗余文件，后端 `DataSourceFactory` 仍直接依赖它。
4. `web/backend/config/data_sources.json` 重复副本已删除；当前仅保留根目录 `config/data_sources.json` 作为运行时 JSON 配置入口。
5. `config/data_sources_registry.yaml` 当前不是“100+ 数据源”，实际仅有 `20` 条数据源定义，其中 `19` 条为 `active`，`1` 条缺失 `status`。
6. Redis 配置在仓库内存在多套约定，不能直接用“统一成 `REDIS_DB=1`”解决，必须先按用途拆分。
7. `src.data_access_pkg` 访问层文件的缺失导入问题已修复，相关模块现可正常导入。

---

## 二、审计依据

本次审计核对了以下文件和入口：

| 路径 | 角色 | 结论 |
|------|------|------|
| `config/.env.example` | 主环境变量模板 | 活跃 |
| `config/.env.data_sources.example` | 数据源示例模板 | 历史/分歧来源 |
| `web/backend/app/core/config.py` | FastAPI 主配置入口 | 活跃 |
| `src/core/config.py` | `DB_*` 命名空间数据库配置类 | 历史/兼容入口 |
| `src/storage/database/connection_manager.py` | 数据库连接管理器 | 活跃，端口默认值已修复 |
| `config/data_sources_registry.yaml` | YAML 数据源注册表 | 活跃 |
| `config/data_sources.json` | 后端数据源工厂运行时配置 | 活跃，不可直接删除 |
| `src/data_access_pkg/postgresql_access.py` | PostgreSQL 访问层 | 已修复导入问题 |
| `src/data_access_pkg/tdengine_access.py` | TDengine 访问层 | 已修复导入问题 |

---

## 三、当前配置入口与职责

### 3.1 数据库配置入口

| 文件 | 当前职责 | 说明 |
|------|----------|------|
| `config/.env.example` | 本地开发主模板 | 定义 `TDENGINE_*`、`POSTGRESQL_*`、JWT、端口等 |
| `web/backend/app/core/config.py` | Web 后端主配置 | 使用 `POSTGRESQL_*`、`REDIS_*`、`MONITOR_DB_URL` |
| `src/storage/database/connection_manager.py` | 连接池/连接获取 | 使用 `POSTGRESQL_*`、`TDENGINE_*`、`REDIS_*` |
| `src/core/config.py` | 历史数据库配置类 | 使用 `DB_POSTGRESQL_*` / `DB_TDENGINE_*` 命名空间 |

### 3.2 数据源配置入口

| 文件 | 当前职责 | 说明 |
|------|----------|------|
| `config/data_sources_registry.yaml` | YAML 注册表 | 供 `src.core.data_source.*` 与配置 CRUD API 使用 |
| `config/data_sources.json` | JSON 工厂配置 | 供 `web/backend/app/services/data_source_factory/data_source_factory.py` 使用 |
### 3.3 关键判断

`config/data_sources_registry.yaml` 与 `config/data_sources.json` 当前承担的不是同一职责：

- YAML 注册表用于“端点级注册和元数据管理”。
- JSON 配置用于“后端数据源工厂的模块/服务运行模式”。

因此，不能把根目录 `config/data_sources.json` 直接定性为“冗余后可删除”。如果要合并，必须先设计兼容层或迁移路径。

---

## 四、当前环境可用性实测

### 4.1 实测方法

基于当前工作目录下的 `.env` 进行连接验证，使用以下命令类别：

- PostgreSQL: `psql ... -Atqc 'select 1'`
- TimescaleDB: `psql ... -Atqc "select extversion from pg_extension where extname='timescaledb'"`
- TDengine: `taos ... -s 'select 1;'`
- Redis: `redis-cli ... PING`

### 4.2 实测结果

| 组件 | 结果 | 备注 |
|------|------|------|
| PostgreSQL | ✅ 可连接 | `select 1` 成功 |
| TimescaleDB | ✅ 可用 | 扩展版本 `2.22.0` |
| TDengine | ✅ 可连接 | `select 1` 成功 |
| Redis | ✅ 可连接 | 用户确认 `redis.ping() == True` |

### 4.3 本机端口监听观察

本机监听到：

- `http://localhost:8020`
- `http://localhost:3020`

未观察到本机监听：

- `5432`
- `5438`
- `6030`
- `6041`
- `6379`

这说明：

1. 当前前后端服务处于运行中。
2. 数据库服务不一定在本机监听，可能通过远端主机、容器网络或其他方式接入。
3. “数据库状态 = 活跃” 只能在“按当前 `.env` 可连接”的意义上成立，不能仅凭架构图下结论。

---

## 五、数据源注册表事实核对

通过实际解析 `config/data_sources_registry.yaml`，得到如下统计：

| 指标 | 实际值 |
|------|--------|
| 数据源总数 | `20` |
| `status=active` | `19` |
| `status` 缺失 | `1` |
| `status=deprecated` | `0` |
| `status=testing` | `0` |
| `target_db=postgresql` | `17` |
| `target_db=tdengine` | `3` |
| 缺失或空 `test_parameters` | `4` |

### 5.1 前缀分布

| 前缀 | 数量 |
|------|------|
| `akshare_*` | `18` |
| `mock_*` | `1` |
| `windows_*` | `1` |

### 5.2 已确认的数据质量问题

| 编号 | 问题 | 说明 |
|------|------|------|
| `DATA-001` | `windows_distributed_bridge` 缺失 `status` | 配置完整性问题 |
| `DATA-002` | 4 条记录缺失或空 `test_parameters` | 不利于自动验证 |

缺失或空 `test_parameters` 的数据源如下：

- `akshare_futures_basis_analysis`
- `akshare_margin_account_info`
- `akshare_sse_market_summary`
- `windows_distributed_bridge`

---

## 六、已确认问题与整改状态

### 6.1 已完成整改

#### CFG-001 PostgreSQL 回退端口不一致

**位置**:

- `src/storage/database/connection_manager.py`
- `config/.env.example`
- `web/backend/app/core/config.py`
- `config/.env.data_sources.example`

**整改前现状**:

- `src/storage/database/connection_manager.py` 回退值为 `5438`
- `config/.env.example` 为 `5432`
- `web/backend/app/core/config.py` 默认值为 `5432`
- `config/.env.data_sources.example` 仍为 `5438`

**影响**:

- 未设置 `POSTGRESQL_PORT` 时，不同入口会走向不同端口。
- 仅修一处不能根治，必须统一“默认端口”和“示例模板”。

**当前状态**:

- `src/storage/database/connection_manager.py` 已统一为 `5432`
- `config/.env.data_sources.example` 已同步为 `5432`

**状态**: 已修复

#### CFG-002 数据库环境变量命名空间分裂

**位置**:

- `src/core/config.py`
- `web/backend/app/core/config.py`
- `src/storage/database/connection_manager.py`

**整改前现状**:

- `src/core/config.py` 使用 `DB_POSTGRESQL_*` / `DB_TDENGINE_*`
- Web 后端和连接管理器使用 `POSTGRESQL_*` / `TDENGINE_*`

**影响**:

- 容易造成同一环境下两套配置源并存。
- 对新环境接入不友好。

**当前状态**:

- `src/core/config.py` 已支持标准变量 `POSTGRESQL_*` / `TDENGINE_*`
- 旧 `DB_*` 变量仍保留为 fallback，兼容历史调用方
- 已补充针对标准变量优先级与旧变量回退的回归测试

**状态**: 已修复

### 6.2 仍需处理的问题

#### CFG-003 Redis DB 号存在多套约定

**位置**:

- `web/backend/app/core/config.py`
- `src/storage/database/connection_manager.py`
- `src/monitoring/async_monitoring.py`
- `src/storage/database/db_utils.py`
- Celery 默认 URL

**现状**:

- 一般 Redis 连接默认走 `DB=1`
- 监控、工具类和部分旧逻辑默认走 `DB=0`
- Celery 默认也使用 `/0` 与 `/1` 分库

**影响**:

- 直接“一刀切成 `REDIS_DB=1`”会破坏现有按用途分库的逻辑。

**结论**:

应先整理 Redis 用途矩阵，再决定标准化策略。

### 6.3 配置副本问题

#### DUP-001 `web/backend/config/data_sources.json` 是重复副本

**现状**:

- 与根目录 `config/data_sources.json` 内容一致
- 仓库内未发现运行时代码直接读取 `web/backend/config/data_sources.json`

**当前状态**:

- 已完成删除
- 仓库内仍未发现运行时代码直接读取该路径

**状态**: 已清理

#### DUP-002 根目录 `config/data_sources.json` 仍是运行时依赖

**整改前现状**:

- `web/backend/app/services/data_source_factory/data_source_factory.py` 默认直接读取 `config/data_sources.json`
- 多个后端 API 通过 `DataSourceFactory` 访问数据源配置

**结论**:

不能把该文件作为“冗余配置”直接删除。若要并入 YAML，必须先设计迁移方案。

### 6.4 访问层代码问题

#### CODE-001 访问层文件存在未导入即使用的符号

**文件**:

- `src/data_access_pkg/postgresql_access.py`
- `src/data_access_pkg/tdengine_access.py`

**现状**:

两文件都直接使用以下符号，但文件头部未导入：

- `MonitoringDatabase`
- `DatabaseTableManager`
- `DatabaseType`
- `DataClassification`
- `_get_database_name_from_classification`

**影响**:

- 取决于模块加载路径和运行方式，可能导致类型检查失败或运行期错误。

**当前状态**:

- `src/data_access_pkg/postgresql_access.py` 已补齐关键导入
- `src/data_access_pkg/tdengine_access.py` 已补齐关键导入
- `src.data_access_pkg.interface`、`src.data_access_pkg.postgresql_access`、`src.data_access_pkg.tdengine_access` 已可正常导入

**状态**: 已修复

### 6.5 兼容性风险

#### RISK-001 `web/backend/app/core/data_source_manager.py` 与当前 JSON 结构不一致

**整改前现状**:

- 该模块读取 `modules`
- 当前 `config/data_sources.json` 实际结构是 `data_sources`

**影响**:

- 如果该旧模块被重新接入运行路径，会读到空配置。

**当前状态**:

- 已兼容 `modules` 和 `data_sources` 两种 JSON 结构
- 当前使用根目录 `config/data_sources.json` 实例化时，可正确读出 `market/data/dashboard/technical_analysis/watchlist/strategy`

**状态**: 已修复

---

## 七、不成立或需要修正的旧结论

以下结论已被本次复核否定或降级：

| 旧结论 | 修正后结论 |
|--------|------------|
| “数据源注册表 100+ 条” | 实际为 `20` 条 |
| “约 10 条 deprecated” | 当前文件中未发现 `deprecated` |
| “约 5 条 testing” | 当前文件中未发现 `testing` |
| “根目录 `config/data_sources.json` 冗余待删除” | 仍为运行时依赖，不可直接删除 |
| “`web/backend/config/data_sources.json` 仍待评估” | 已确认无运行时代码依赖并已删除 |
| “Redis 为后端必需且活跃” | 代码中存在 Redis 路径，但当前环境 Redis 不可连接，且主模板未将其作为基础启动必填项 |
| “统一 `REDIS_DB=1` 即可” | 需要按缓存、监控、Celery 等用途分开治理 |

---

## 八、建议行动项

### 8.1 立即执行

| 优先级 | 编号 | 行动项 | 说明 |
|--------|------|--------|------|
| `P0` | `VERIFY-001` | 保留并记录当前环境实测结果 | 当前已确认 PostgreSQL / TDengine / TimescaleDB 可用，Redis 也已由用户确认可用 |
| `P1` | `DUP-002` | 保持根目录 `config/data_sources.json` 为运行时入口 | 暂不删除，避免影响 `DataSourceFactory` |

### 8.2 需要方案后再做

| 优先级 | 编号 | 行动项 | 说明 |
|--------|------|--------|------|
| `P1` | `CFG-003` | 整理 Redis 用途矩阵 | 不建议直接统一到单一 DB 号 |
| `P2` | `DATA-001` | 补齐注册表缺失字段和测试参数 | 适合加自动校验 |
| `P3` | `MIG-001` | 设计 JSON 到 YAML 的迁移方案 | 先保证 `DataSourceFactory` 兼容 |

---

## 九、建议验证清单

### 9.1 数据库连接

```bash
psql -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" -Atqc 'select 1'
psql -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" -Atqc "select extversion from pg_extension where extname='timescaledb';"
taos -h "$TDENGINE_HOST" -P "$TDENGINE_PORT" -u "$TDENGINE_USER" -p"$TDENGINE_PASSWORD" -s 'select 1;'
redis-cli -h "${REDIS_HOST:-localhost}" -p "${REDIS_PORT:-6379}" -n "${REDIS_DB:-0}" PING
```

### 9.2 配置入口一致性

```bash
rg -n "POSTGRESQL_PORT|DB_POSTGRESQL_PORT|REDIS_DB|config/data_sources.json|data_sources_registry.yaml" config src web/backend
```

### 9.3 数据源注册表完整性

```bash
python - <<'PY'
import yaml
from collections import Counter
with open("config/data_sources_registry.yaml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f) or {}
sources = data.get("data_sources", {})
print("total", len(sources))
print("status", Counter((cfg or {}).get("status", "<missing>") for cfg in sources.values()))
print("target_db", Counter((cfg or {}).get("target_db", "<missing>") for cfg in sources.values()))
print("missing_test_parameters", [
    name for name, cfg in sources.items()
    if "test_parameters" not in (cfg or {}) or not cfg.get("test_parameters")
])
PY
```

---

## 十、最终结论

本项目当前不是“数据库配置整体混乱”，而是存在三类不同问题：

1. 已确认且应立即修复的配置缺陷。
2. 历史兼容入口并存导致的命名和职责分裂。
3. 文档和旧结论滞后于仓库现状。

本次审计后，建议按以下原则推进：

- 先修已确认缺陷，不先做大规模配置重构。
- 先区分“运行时依赖”与“历史副本”，不要误删根目录 `config/data_sources.json`。
- 先补实测结论，再下“活跃/必需/冗余”判断。

---

**报告状态**: 已复核并修正
**下一步建议**: 继续围绕 `CFG-003` 和 JSON/YAML 配置职责边界收敛，避免直接进入大范围重构
