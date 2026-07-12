# MyStocks 数据源最终检查报告

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


> **检查日期**: 2026-03-12
> **检查环境**: `/opt/claude/mystocks_spec` 本地工作区，`main` 分支
> **检查原则**: 只记录本轮重新验证的事实；严格区分配置口径、运行时口径、真实业务探针
> **当前结论**: `主链路可用，仍有 2 个外部源阻塞项`

---

## 一、执行摘要

### 1.1 当前判断

- PostgreSQL、TDengine、Redis、MongoDB、TDX 当前均可连通。
- AKShare、BaoStock、EFinance、WebData(Tencent 日线入口) 当前有业务探针成功证据。
- Byapi 当前仍返回 `403 Forbidden`，不可用。
- Tushare 当前仍缺 `TUSHARE_TOKEN`，不可用。
- `DataSourceManagerV2` 当前运行时注册表已收敛到 `42` 项，不再出现 YAML alias 重复注册。
- `DataSourceManagerV2.health_check()` 已修正，不再把全部 active 端点误判为 unhealthy。
- `TdxDataSource` 抽象类问题已修复。
- `FinancialDataSource` 初始化状态位覆盖问题已修复。

### 1.2 关键数字

| 维度 | 结果 | 说明 |
|------|------|------|
| YAML 注册表项数 | 20 | `config/data_sources_registry.yaml:data_sources` |
| PostgreSQL active 注册表项数 | 42 | `data_source_registry` 实表查询 |
| `DataSourceManagerV2` 运行时项数 | 42 | 去重后与数据库口径对齐 |
| `health_check()` 返回 | `healthy=42, unhealthy=0` | 说明元数据口径已修复，不代表全部做过 live probe |
| 基础设施连通 | 5/5 OK | PostgreSQL、TDengine、Redis、MongoDB、TDX |
| 外部源业务探针 | 4/6 OK | AKShare、BaoStock、EFinance、WebData(Tencent) OK；Byapi、Tushare FAIL |
| 定向回归 | `43 passed` | 本轮 Redis/Mongo/runtime convergence 回归测试 |

### 1.3 当前剩余阻塞项

| 优先级 | 事项 | 当前状态 |
|--------|------|----------|
| P0 | Tushare Token 缺失 | `TUSHARE_TOKEN` 未设置，初始化失败 |
| P0 | Byapi 授权失败 | 业务探针返回 `403 Forbidden` |
| P1 | WebData Sina 关键字搜索空结果 | Tencent 入口可用，Sina 入口仍待确认是否退化 |
| P2 | `easyquotation` 未安装 | Financial fallback 缺失，但主路径未阻塞 |

---

## 二、验证证据

本报告基于以下 fresh evidence：

1. 基础设施直连探针
   - PostgreSQL: `select 1`
   - TDengine: `select server_version()`
   - Redis: `redis.ping()`
   - MongoDB: `db.admin.command('ping')`
   - TDX: `pytdx` 获取 1 条报价
2. 运行时注册表检查
   - 解析 `config/data_sources_registry.yaml`
   - 查询 PostgreSQL `data_source_registry`
   - 实例化 `DataSourceManagerV2(use_smart_cache=False)`
3. 数据源业务探针
   - AKShare: `stock_info_a_code_name()`
   - BaoStock: `login() + query_all_stock()`
   - EFinance: `get_quote_history()`
   - WebData: `get_tencent_daily_kline('sz000001')`
   - Byapi: `get_stock_list()`
   - Tushare: `TushareDataSource()` 初始化
4. 代码级回归验证
   - `pytest` 定向套件: `43 passed`
   - `scripts/dev/check_mongodb_runtime_health.sh` 返回 `{ ok: 1 }`
   - `scripts/dev/check_redis_runtime_health.sh` 返回两次 `PONG`
   - `python -m py_compile` 通过本轮相关 Python 文件

说明：

- 本报告不把“环境变量存在”视为“可用”。
- 本报告不把“适配器可 import”视为“可用”。
- `DataSourceManagerV2.health_check()` 目前是元数据健康度，不是 live 业务探针。

---

## 三、三套事实口径

### 3.1 YAML 配置口径

`config/data_sources_registry.yaml` 当前解析结果：

| 指标 | 数值 |
|------|------|
| YAML 总项数 | 20 |
| `akshare` | 18 |
| `system_mock` | 1 |
| `windows_nodes` | 1 |

说明：

- YAML 仍然只覆盖部分源，不是全量运行时注册表。
- YAML 外层 key 仍有 alias 形式，例如 `akshare_dragon_tiger_detail`。

### 3.2 PostgreSQL 注册表口径

`data_source_registry` 当前实测：

| 指标 | 数值 |
|------|------|
| active 行数 | 42 |

### 3.3 `DataSourceManagerV2` 运行时口径

当前运行时实测：

| 指标 | 数值 |
|------|------|
| 运行时注册项总数 | 42 |
| alias 键 `akshare_dragon_tiger_detail` | 不存在 |
| canonical 键 `akshare.stock_lhb_detail_em` | 存在 |

结论：

- 运行时口径已与数据库 active 口径对齐。
- YAML alias 导致的 61 项重复注册问题已经消除。

---

## 四、基础设施连通性

### 4.1 实测结果

| 目标 | 结果 | 证据 |
|------|------|------|
| PostgreSQL | OK | `select 1 -> 1` |
| TDengine | OK | `server_version() -> 3.3.6.13` |
| Redis | OK | `ping -> True` |
| MongoDB | OK | `ping -> 1.0` |
| TDX 节点 | OK | `records -> 1` |

### 4.2 结论

- 当前基础设施层不是数据源排障阻塞项。
- Redis / MongoDB 已恢复，并已纳入 runtime health / readiness 契约。

---

## 五、数据源家族实测结果

### 5.1 已验证业务探针

| 数据源 | 业务探针 | 结果 | 当前判断 |
|--------|----------|------|----------|
| AKShare | `stock_info_a_code_name()` | `5489` rows | OK |
| BaoStock | `login() + query_all_stock('2024-01-02')` | 登录成功，返回 `1` 行探针结果 | OK |
| EFinance | `get_quote_history('000001', beg='20260301', end='20260305')` | `4` rows | OK |
| WebData / Tencent | `get_tencent_daily_kline('sz000001')` | `100` rows | OK |
| Byapi | `get_stock_list()` | `403 Forbidden` | FAIL |
| Tushare | `TushareDataSource()` | `ImportError: 请设置环境变量 TUSHARE_TOKEN` | FAIL |

### 5.2 依赖 / 适配器状态补充

`FinancialDataSource.get_data_source_status()` 当前结果：

| 项 | 结果 |
|----|------|
| `financial_data_source.available` | `True` |
| `stock_daily_adapter.available` | `True` |
| `financial_report_adapter.available` | `True` |
| `efinance` | `True` |
| `akshare` | `True` |
| `tushare` Python 包 | `True` |
| `easyquotation` | `False` |

结论：

- `easyquotation` 仍未安装，但财务数据源主路径当前不是红灯。
- WebData 至少有一条 Tencent 业务入口可用。
- Sina 关键字搜索本轮返回 `0` 行，是否为接口退化仍需单独确认。

---

## 六、代码级修复验证

### 6.1 已确认修复

| 项 | 当前状态 | 验证方式 |
|----|----------|----------|
| `DataSourceManagerV2.health_check()` 误判 | 已修复 | `healthy=42, unhealthy=0` |
| YAML alias 重复注册 | 已修复 | 运行时 `42` 项，alias 不存在 |
| `TdxDataSource` 抽象类缺方法 | 已修复 | `__abstractmethods__ == frozenset()` |
| `FinancialDataSource` 状态位重置 | 已修复 | `get_data_source_status()` 返回 available `True` |

### 6.2 定向验证结果

| 检查项 | 结果 |
|--------|------|
| `pytest` 定向回归 | `43 passed in 1.68s` |
| Mongo runtime health script | `{ ok: 1 }` |
| Redis runtime health script | `PONG` / `PONG` |

---

## 七、当前结论与后续建议

### 7.1 当前结论

当前项目的数据源体系已经从“基础设施不完整 + 运行时重复注册 + 多个代码级误判”状态，收敛到：

- 基础设施主链路可用
- 运行时注册表口径一致
- Redis / Mongo runtime contract 已收敛
- 主要免费数据源中，AKShare、BaoStock、EFinance、TDX、WebData(Tencent) 可用
- 当前明确不可用的外部源只剩 2 个：Byapi、Tushare

### 7.2 建议执行顺序

1. 补 `TUSHARE_TOKEN` 并做最小业务探针。
2. 与 Byapi 提供方核对授权状态，处理 `403 Forbidden`。
3. 单独确认 WebData 中 Sina 关键字搜索空结果是否为接口退化或参数问题。
4. 若需要财务 fallback，安装并验证 `easyquotation`。

### 7.3 不应再沿用的旧结论

以下旧结论已失效，不应继续作为当前事实使用：

- “Redis 不可连”
- “MongoDB 不可连”
- “DataSourceManagerV2 运行时共有 61 项”
- “`health_check()` 会把全部项判为 unhealthy”
- “`TdxDataSource` 仍是抽象类”
- “`FinancialDataSource` 状态位仍被重置”
