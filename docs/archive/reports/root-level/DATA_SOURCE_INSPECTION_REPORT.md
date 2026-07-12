# MyStocks 数据源真实检查报告

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


> **检查日期**: 2026-03-12
> **检查环境**: `/opt/claude/mystocks_spec` 本地工作区，`main` 分支
> **检查原则**: 只记录已验证事实；区分静态配置、数据库注册表、运行时行为三种口径
> **总体结论**: `部分可用，未达到“整体健康”`

---

## 一、执行摘要

### 1.1 最终判断

- PostgreSQL、TDengine、TDX、AKShare、BaoStock、EFinance、SinaFinance 当前可用。
- Redis、MongoDB 当前不可连。
- Byapi 当前返回 `403 Forbidden`，不可用。
- Tushare 包已安装，但缺少 `TUSHARE_TOKEN`，当前不可用。
- WebData 适配器可初始化，但最小业务探针未返回结果，当前应视为待确认。
- `DataSourceManagerV2` 当前运行时注册了 61 个数据源项，但其 `health_check()` 实现会把全部项判为 unhealthy，不能作为真实健康结论。

### 1.2 关键数字

| 维度 | 结果 | 说明 |
|------|------|------|
| YAML 注册表项数 | 20 | `config/data_sources_registry.yaml` 直接解析结果 |
| PostgreSQL 注册表项数 | 42 active | `data_source_registry` 实表查询结果 |
| `DataSourceManagerV2` 运行时项数 | 61 | 数据库 + YAML 合并后结果 |
| 基础设施连通 | 3/5 OK | PostgreSQL、TDengine、TDX OK；Redis、MongoDB FAIL |
| 外部源最小业务探针 | 5/8 OK | TDX、AKShare、EFinance、BaoStock、SinaFinance OK |
| 明确阻塞项 | 7 | 见第七章 |

### 1.3 当前修复优先级

| 优先级 | 事项 |
|--------|------|
| P0 | 修复 Redis / MongoDB 不可连、补 Tushare Token、处理 Byapi 403 |
| P0 | 修复 `DataSourceManagerV2.health_check()` 误判问题 |
| P0 | 修复 `TdxDataSource` 抽象类不可实例化 |
| P0 | 修复 `FinancialDataSource` 初始化后状态位被重置 |
| P1 | 统一 YAML 键名与 `endpoint_name`，消除运行时重复注册 |
| P1 | 为各数据源建立统一 smoke test，而不是只看 import/init |
| P2 | 排查 WebData 空结果、SinaFinance 质量检查/监控告警噪声 |

---

## 二、检查方法与证据来源

本报告基于以下实际动作生成：

1. 读取配置文件：
   - `config/data_sources_registry.yaml`
   - `config/adapter_priority_config.yaml`
   - `config/tdx_servers.yaml`
   - `config/data_sources.json`
   - `.env`
   - `config/.env.data_sources.example`
2. 查询 PostgreSQL 中 `data_source_registry` 实表。
3. 实例化 `DataSourceManagerV2`，观察运行时注册项数量。
4. 验证基础设施连通性：
   - PostgreSQL
   - TDengine
   - Redis
   - MongoDB
   - TDX 节点
5. 验证适配器初始化状态。
6. 对主要外部数据源执行最小业务探针，而不是只做 import。

说明：

- 本报告不复用旧报告里的任何数量或结论。
- 本报告不把“环境变量存在”视为“服务可用”。
- 本报告不把“适配器能 import”视为“数据源可用”。

---

## 三、三套事实口径

### 3.1 YAML 配置口径

`config/data_sources_registry.yaml` 当前只有 20 项，来源分布如下：

| 来源 | 数量 |
|------|------|
| akshare | 18 |
| system_mock | 1 |
| windows_nodes | 1 |

分类分布如下：

| 分类 | 数量 |
|------|------|
| INSTITUTIONAL_DATA | 4 |
| FUTURES_DATA | 4 |
| LEVERAGE_DATA | 5 |
| MARKET_DATA | 6 |
| DAILY_KLINE | 1 |

注意：

- 这 20 项不是“全部运行时数据源”，只是当前 YAML 文件内容。
- YAML 键名与内部 `endpoint_name` 并不一致，例如：
  - `akshare_dragon_tiger_detail`
  - `endpoint_name: akshare.stock_lhb_detail_em`

### 3.2 PostgreSQL 注册表口径

从 PostgreSQL 的 `data_source_registry` 查询结果：

| 指标 | 数值 |
|------|------|
| 总行数 | 42 |
| active 行数 | 42 |

来源分布：

| 来源 | 数量 |
|------|------|
| akshare | 20 |
| webdata | 12 |
| baostock | 5 |
| tushare | 2 |
| system_mock | 1 |
| tdx | 1 |
| windows_nodes | 1 |

### 3.3 `DataSourceManagerV2` 运行时口径

`DataSourceManagerV2(use_smart_cache=False)` 实例化后结果：

| 指标 | 数值 |
|------|------|
| 运行时注册项总数 | 61 |
| 来自数据库 | 42 |
| 来自 YAML | 19 |

来源分布：

| 来源 | 数量 |
|------|------|
| akshare | 38 |
| webdata | 12 |
| baostock | 5 |
| tushare | 2 |
| system_mock | 2 |
| tdx | 1 |
| windows_nodes | 1 |

结论：

- 运行时比数据库多 19 项，不是因为发现了新源，而是因为 YAML 项被按外层键再次注册。
- 当前运行时注册表存在“数据库 endpoint_name”和“YAML 外层 key”同时存在的重复命名空间问题。

---

## 四、环境配置快照

以下为当前 `.env` 中与数据源相关的非敏感配置事实：

| 项 | 当前值 |
|----|--------|
| `POSTGRESQL_HOST` | `192.168.123.104` |
| `POSTGRESQL_PORT` | `5438` |
| `TDENGINE_HOST` | `192.168.123.104` |
| `TDENGINE_PORT` | `6030` |
| `TDENGINE_REST_PORT` | `6041` |
| `REDIS_HOST` | `localhost` |
| `REDIS_PORT` | `6379` |
| `MONGODB_IP` | `localhost:27017` |
| `BACKEND_PORT` | `8020` |
| `FRONTEND_PORT` | `3020` |
| `TIMESERIES_DATA_SOURCE` | `tdengine` |
| `RELATIONAL_DATA_SOURCE` | `postgresql` |
| `BUSINESS_DATA_SOURCE` | `composite` |
| `DATA_SOURCE_MODE` | `real` |
| `USE_MOCK_DATA` | `false` |

`config/data_sources.json` 当前模式：

| 数据源工厂项 | mode | enabled |
|--------------|------|---------|
| market | real | true |
| data | real | true |
| dashboard | mock | true |
| technical_analysis | real | true |
| watchlist | mock | true |
| strategy | mock | true |

结论：

- 当前环境是“真实数据模式”，不是 mock 模式。
- 但 `dashboard`、`watchlist`、`strategy` 仍显式配置为 `mock`。

---

## 五、基础设施连通性检查

### 5.1 实测结果

| 目标 | 结果 | 证据 |
|------|------|------|
| PostgreSQL | OK | `select 1` 返回成功 |
| TDengine | OK | `select server_version()` 返回 `3.3.6.13` |
| Redis | FAIL | `localhost:6379` 连接被拒绝 |
| MongoDB | FAIL | `localhost:27017` 连接被拒绝 |
| TDX 节点 | OK | `180.153.18.170:7709` 可连接且可取 1 条报价 |

### 5.2 结论

- 数据库主链路当前可用：PostgreSQL + TDengine。
- 缓存与 Mongo 监控链路当前不可用。
- 如果系统运行依赖 Redis 或 MongoDB，则当前环境不能视为“生产可运行”。

---

## 六、主要数据源家族实测结果

### 6.1 外部与存储数据源

| 数据源 | 依赖状态 | 适配器初始化 | 最小业务探针 | 当前判断 | 备注 |
|--------|----------|--------------|--------------|----------|------|
| TDX | `pytdx` 可用 | `TdxDataSource` 失败 | OK | 可用但适配器有实现缺口 | 直接 `pytdx` 连通正常；类本身仍是抽象类 |
| AKShare | 可用 | OK | OK | 可用 | `stock_info_a_code_name()` 返回 5489 行 |
| EFinance | 可用 | 通过 `CustomerDataSource` 间接可用 | OK | 可用 | `get_quote_history` 和 `get_base_info` 可返回数据 |
| BaoStock | 可用 | OK | OK | 可用 | `get_stock_basic('600000')` 返回 1 行 |
| SinaFinance | 内置依赖齐全 | OK | OK | 可用但有质量告警 | 可抓到 60 行评级数据 |
| Byapi | 代码可初始化 | OK | FAIL | 不可用 | API 返回 `403 Forbidden` |
| WebData | 本地适配器可初始化 | OK | FAIL | 待确认 / 降级 | `get_sina_keyword_search('平安银行')` 返回空 |
| Tushare | 包已安装 | FAIL | 未执行 | 不可用 | 缺少 `TUSHARE_TOKEN` |
| PostgreSQL | 驱动可用 | - | OK | 可用 | 主存储链路正常 |
| TDengine | 驱动可用 | - | OK | 可用 | 主时序链路正常 |
| Redis | 驱动可用 | - | FAIL | 不可用 | 服务未监听 |
| MongoDB | 驱动可用 | - | FAIL | 不可用 | 服务未监听 |

### 6.2 复合适配器 / 门面适配器

| 适配器 | 结果 | 说明 |
|--------|------|------|
| `CustomerDataSource` | 可初始化，降级运行 | `efinance` 可用，`easyquotation` 缺失 |
| `FinancialDataSource` | 可初始化，但状态报告错误 | 实际依赖检查通过，但内部可用性标志被重置 |
| `DataSourceManagerV2` | 可初始化，但健康检查结果不可用 | 实际加载 61 项，`health_check()` 全部判 unhealthy |

---

## 七、代码级阻塞项

### 7.1 `TdxDataSource` 不能实例化

现象：

- `src.adapters.tdx.tdx_data_source.TdxDataSource()` 实例化失败。
- 抽象方法缺口：`get_market_calendar`。

影响：

- 代码层声明 TDX 是主数据源，但统一适配器入口本身不可实例化。
- 这会阻断依赖统一 `IDataSource` 语义的调用方。

### 7.2 `FinancialDataSource` 初始化后把状态位重置为 `False`

现象：

- `__init__()` 先调用 `_check_dependency_availability()`。
- `_check_dependency_availability()` 内把 `_stock_daily_available` / `_financial_reports_available` 设为 `True`。
- 紧接着在 `__init__()` 里又把两个值重新赋为 `False`。

影响：

- `get_data_source_status()` 会报告两个子适配器不可用。
- 会误导监控、健康检查和后续路由判断。

### 7.3 `DataSourceManagerV2.health_check()` 逻辑错误

现象：

- 运行时 registry 结构是：
  - `config`
  - `handler`
  - `cache`
  - `last_call`
  - `call_count`
- 但 `health_check()` 读取的是顶层 `enabled` 和 `health_score`。

影响：

- 所有项都会被判为 unhealthy。
- 因此当前 `health_check()` 结果不能用于报告“系统健康”。

### 7.4 YAML 键名与 `endpoint_name` 不一致导致运行时重复注册

现象：

- YAML 外层 key 例如 `akshare_dragon_tiger_detail`
- 内部 `endpoint_name` 为 `akshare.stock_lhb_detail_em`

影响：

- 与数据库表合并时按 key 而非 `endpoint_name` 合并。
- 运行时出现同一业务源的双命名空间注册。

### 7.5 Byapi 当前鉴权或授权不可用

现象：

- `get_stock_list()` 返回 `403 Forbidden`。

影响：

- 当前不能把 Byapi 视为备用或生产可用数据源。

### 7.6 Tushare 当前缺 Token

现象：

- 包已安装，但 `TUSHARE_TOKEN` 未设置。
- `TushareDataSource()` 直接抛出 `ImportError`。

影响：

- `financial_data` 优先级链中的 `tushare` 当前不可作为 fallback。

### 7.7 Redis / MongoDB 服务当前未运行

现象：

- Redis `localhost:6379` 连接被拒绝。
- MongoDB `localhost:27017` 连接被拒绝。

影响：

- 缓存、消息、监控或文档库相关流程若依赖两者，将直接失败。

---

## 八、建议的修复顺序

### 8.1 P0：必须先修

1. 启动并验证 Redis。
2. 启动并验证 MongoDB，确认它是否仍属于本项目正式功能树。
3. 为 Tushare 配置有效 `TUSHARE_TOKEN`，并做最小业务探针。
4. 修复 Byapi 鉴权 / license / IP 白名单问题。
5. 修复 `TdxDataSource` 缺失 `get_market_calendar` 的问题。
6. 修复 `FinancialDataSource` 初始化后状态位被覆盖的问题。
7. 修复 `DataSourceManagerV2.health_check()` 对 registry 结构读取错误的问题。

### 8.2 P1：随后处理

1. 统一 `config/data_sources_registry.yaml` 外层 key 与 `endpoint_name`。
2. 定义唯一事实来源：
   - 配置事实源
   - 注册事实源
   - 运行事实源
3. 清理重复注册项，确保运行时总数可解释。
4. 把最小业务探针固化为脚本，避免再次出现“只看配置不看运行”的报告。

### 8.3 P2：质量与维护性改进

1. 排查 WebData 空结果是接口变化、依赖路径问题还是关键词接口失效。
2. 排查 SinaFinance 质量校验规则过严还是字段映射有误。
3. 为每个外部源维护一条稳定的 smoke case。
4. 报告口径改为固定模板：
   - 配置
   - 依赖
   - 初始化
   - 探针
   - 健康结论

---

## 九、推荐的后续检查命令

以下命令比旧报告中的命令更贴近当前仓库结构：

### 9.1 基础设施

```bash
python - <<'PY'
from dotenv import dotenv_values
import psycopg2
cfg = dotenv_values('.env')
conn = psycopg2.connect(
    host=cfg['POSTGRESQL_HOST'],
    port=cfg['POSTGRESQL_PORT'],
    user=cfg['POSTGRESQL_USER'],
    password=cfg['POSTGRESQL_PASSWORD'],
    dbname=cfg['POSTGRESQL_DATABASE'],
)
cur = conn.cursor()
cur.execute('select 1')
print(cur.fetchone())
cur.close()
conn.close()
PY
```

```bash
python - <<'PY'
from dotenv import dotenv_values
import taos
cfg = dotenv_values('.env')
conn = taos.connect(
    host=cfg['TDENGINE_HOST'],
    port=int(cfg['TDENGINE_PORT']),
    user=cfg['TDENGINE_USER'],
    password=cfg['TDENGINE_PASSWORD'],
    database=cfg['TDENGINE_DATABASE'],
)
cur = conn.cursor()
cur.execute('select server_version()')
print(cur.fetchone())
cur.close()
conn.close()
PY
```

```bash
python - <<'PY'
import redis
from dotenv import dotenv_values
cfg = dotenv_values('.env')
r = redis.Redis(
    host=cfg['REDIS_HOST'],
    port=int(cfg['REDIS_PORT']),
    password=cfg.get('REDIS_PASSWORD') or None,
    db=int(cfg.get('REDIS_DB') or 0),
)
print(r.ping())
PY
```

```bash
python - <<'PY'
from pymongo import MongoClient
from dotenv import dotenv_values
cfg = dotenv_values('.env')
client = MongoClient(
    host=cfg['MONGODB_IP'],
    username=cfg.get('USERNAME') or None,
    password=cfg.get('PASSWORD') or None,
    serverSelectionTimeoutMS=5000,
)
print(client.admin.command('ping'))
client.close()
PY
```

### 9.2 外部源最小探针

```bash
python - <<'PY'
from pytdx.hq import TdxHq_API
api = TdxHq_API()
ok = api.connect('180.153.18.170', 7709, time_out=5)
print('connect=', ok)
if ok:
    print(api.get_security_quotes([(1, '000001')]))
    api.disconnect()
PY
```

```bash
python - <<'PY'
import akshare as ak
df = ak.stock_info_a_code_name()
print(df.head())
print('rows=', len(df))
PY
```

```bash
python - <<'PY'
import efinance as ef
df = ef.stock.get_quote_history('000001', beg='20260301', end='20260312', klt=101)
print(df.head())
print('rows=', len(df))
PY
```

```bash
python - <<'PY'
from src.adapters.baostock.baostock_adapter import BaoStockAdapter
df = BaoStockAdapter().get_stock_basic('600000')
print(df.head())
print('rows=', len(df))
PY
```

### 9.3 当前真实可用的测试路径

```bash
pytest tests/adapters/test_tdx_adapter.py -v
pytest tests/adapters/test_akshare_adapter.py -v
pytest tests/adapters/test_financial_adapter.py -v
pytest tests/unit/adapters/test_data_source_manager.py -v
pytest tests/unit/adapters/test_tushare_adapter_basic.py -v
```

---

## 十、结论

当前项目的数据源体系不能再用“48/48 active，整体健康”这样的说法概括。更真实的结论是：

- **核心数据库链路可用**：PostgreSQL、TDengine 正常。
- **核心行情链路部分可用**：TDX、AKShare、EFinance、BaoStock、SinaFinance 可用。
- **备用链路存在明显缺口**：Byapi、Tushare、WebData 目前都不能被视为稳定可用。
- **基础设施并不完整**：Redis、MongoDB 当前不可连。
- **代码层存在阻塞性实现问题**：TDX 统一适配器、FinancialDataSource 状态位、DataSourceManagerV2 健康检查均需修正。

因此，当前最合理的状态标签是：

> **数据源体系已具备可修复基础，但尚未完成“全量可用、配置正确、健康可信”的验收。**
