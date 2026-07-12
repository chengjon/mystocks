# MyStocks 数据源检查报告（修复后状态）

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


> **生成时间**: 2026-03-12
> **说明**: 本文件基于 `reports/DATA_SOURCE_INSPECTION_REPORT.md` 之后的实际修复结果生成，用于覆盖已变化的运行时事实。
> **适用范围**: 当前 WSL2 + Docker 本地环境

---

## 一、已完成修复

### 1.1 Redis

- 发现原 `mystocks-redis` 是孤儿容器，状态为 `Created`。
- 根因是历史创建时 `6379` 端口绑定失败，容器从未真正启动。
- 已删除旧容器并重建为可运行状态。

当前状态：

| 项 | 结果 |
|----|------|
| 容器名 | `mystocks-redis` |
| 镜像 | `redis:latest` |
| 端口 | `6379:6379` |
| 容器状态 | `Up` |
| 业务验证 | `redis.ping() == True` |

### 1.2 MongoDB

- 发现本地原先没有运行中的 `mystocks-mongodb` 容器。
- 仓库中的 Mongo compose 配置当前不能直接复用：
  - 默认映射端口是 `27018`
  - 但 `.env` 当前配置是 `MONGODB_IP=localhost:27017`
  - compose 解析出的 `mongod.conf` 挂载路径不存在
- 已按 `.env` 当前口径手工启动 Mongo 容器，避免继续依赖失配的 compose 配置。

当前状态：

| 项 | 结果 |
|----|------|
| 容器名 | `mystocks-mongodb` |
| 镜像 | `mongo:latest` |
| 端口 | `27017:27017` |
| 容器状态 | `Up` |
| 用户 | `.env` 中 `USERNAME` |
| 业务验证 | `db.admin.command('ping') == 1.0` |

---

## 二、修复后基础设施结论

当前基础设施连通性如下：

| 目标 | 结果 | 验证方式 |
|------|------|----------|
| PostgreSQL | OK | `select 1` |
| TDengine | OK | `select server_version()` |
| Redis | OK | `redis.ping()` |
| MongoDB | OK | `db.admin.command('ping')` |
| TDX 节点 | OK | `pytdx` 取实时报价 |

结论：

> **当前环境的基础设施层已恢复，不再是数据源排障的首要阻塞项。**

---

## 三、当前仍未解决的问题

以下问题在本次修复后仍然存在：

| 优先级 | 问题 | 当前状态 |
|--------|------|----------|
| P0 | Byapi 授权 / 鉴权失败 | `403 Forbidden` |
| P0 | Tushare 缺少 `TUSHARE_TOKEN` | 适配器初始化失败 |
| P0 | `DataSourceManagerV2.health_check()` 逻辑错误 | 全量误判 unhealthy |
| P0 | `TdxDataSource` 仍是抽象类 | 缺少 `get_market_calendar` |
| P0 | `FinancialDataSource` 状态位被重置 | 运行状态报告错误 |
| P1 | YAML key 与 `endpoint_name` 不一致 | 运行时重复注册 |
| P1 | WebData 最小探针无结果 | 待确认 |
| P2 | Redis / Mongo 启动方式未沉淀到可复用配置 | 当前依赖手工恢复 |

---

## 四、对原报告的覆盖说明

以下旧结论已失效，不应继续使用：

- “Redis 当前不可连”
- “MongoDB 当前不可连”
- “基础设施并不完整：Redis、MongoDB 当前不可连”
- 把 Redis / MongoDB 故障列为当前首要运行时阻塞项的部分

以下旧结论仍然有效：

- Byapi 当前不可用
- Tushare 当前不可用
- WebData 仍待确认
- `DataSourceManagerV2`、`TdxDataSource`、`FinancialDataSource` 仍有代码级缺陷
- YAML / PostgreSQL / 运行时注册表口径不一致

---

## 五、建议的下一步

按当前实际状态，后续修复顺序建议调整为：

1. 补 `TUSHARE_TOKEN`，验证 Tushare 最小探针。
2. 修复 Byapi `403`。
3. 修复 `DataSourceManagerV2.health_check()`。
4. 修复 `TdxDataSource` 缺失抽象方法实现。
5. 修复 `FinancialDataSource` 初始化状态位覆盖问题。
6. 统一 YAML key 与 `endpoint_name`。
7. 把 Redis / Mongo 当前手工恢复方式沉淀为可复用脚本或 compose 配置。

---

## 六、当前容器状态快照

修复完成后，关键容器状态如下：

| 容器 | 镜像 | 状态 | 端口 |
|------|------|------|------|
| `mystocks-redis` | `redis:latest` | `Up` | `6379->6379` |
| `mystocks-mongodb` | `mongo:latest` | `Up` | `27017->27017` |

