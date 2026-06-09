# MyStocks 基础设施检查手册

> **当前口径**:
> 本手册在 `2026-04-24` 依据当前仓库规则与后端实现重新核对，重点覆盖 API 管理链路需要的基础设施与契约检查。
> 仓库级规则仍以 `architecture/STANDARDS.md` 为准；API 契约真相源仍是 `FastAPI 路由 + Pydantic Schema + 导出的 /openapi.json`。

## 1. 先确认运行基线

```bash
git branch --show-current
python --version
node --version
pm2 list
```

当前默认访问地址：

| 服务 | 地址 | 用途 |
|------|------|------|
| Frontend | `http://localhost:3020` | 前端 UI / E2E 入口 |
| Backend | `http://localhost:8020` | FastAPI 主服务 |
| OpenAPI JSON | `http://localhost:8020/openapi.json` | 运行时契约导出 |
| Health | `http://localhost:8020/health` | 服务存活检查 |
| Detailed Health | `http://localhost:8020/api/health/detailed` | 详细巡检输出 |

## 2. API 管理任务的最小检查集

### 2.1 服务与端口

```bash
curl -s http://localhost:8020/health | python -m json.tool
curl -s http://localhost:8020/api/health/detailed | python -m json.tool
curl -I http://localhost:3020
```

预期：

- `mystocks-backend` 与 `mystocks-frontend` 在 `pm2 list` 中为 `online`
- `/health` 返回可解析 JSON
- `/api/health/detailed` 返回详细巡检输出或明确错误信息

### 2.2 数据库与缓存

```bash
env | rg 'POSTGRES|TDENGINE|REDIS|JWT'
PGPASSWORD="$POSTGRESQL_PASSWORD" psql -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" -c "SELECT 1;"
taos -h "$TDENGINE_HOST" -P "$TDENGINE_PORT" -u "$TDENGINE_USER" -p "$TDENGINE_PASSWORD" -c "SELECT 1;"
```

说明：

- PostgreSQL、TDengine、Redis 仍是当前 API 运行链路的关键基础设施
- 若某项不可用，必须在 API 可用性报告中明确标注为“运行时降级”或“真实阻塞”，不能笼统写“服务异常”

## 3. 契约导出与对表

### 3.1 重新生成当前 OpenAPI

```bash
python scripts/generate_openapi.py --output /tmp/mystocks_openapi_current.json
```

### 3.2 同步文档契约快照

```bash
cp /tmp/mystocks_openapi_current.json docs/api/openapi.json
python scripts/generate_frontend_types.py --openapi-spec docs/api/openapi.json
```

说明：

- `docs/api/openapi.json` 是文档侧保存的契约快照，不是独立真相源
- 每次 API 字段、路径、方法、认证或错误响应变更，都应在同一提交内更新该快照

## 4. API 管理相关重点端点

当前 API 管理与治理链路建议优先检查以下端点：

| 功能 | 端点 | 方法 |
|------|------|------|
| 契约版本列表 | `/api/contracts/versions` | `GET` |
| 契约校验 | `/api/contracts/validate` | `POST` |
| 契约同步 | `/api/contracts/sync` | `POST` |
| 数据源列表 | `/api/v1/data-sources/` | `GET` |
| 数据源配置列表 | `/api/v1/data-sources/config/` | `GET` |
| 数据源配置批量更新 | `/api/v1/data-sources/config/batch` | `POST` |
| 数据源连通性测试 | `/api/v1/data-sources/{endpoint_name}/test` | `POST` |
| 数据源健康检查 | `/api/v1/data-sources/{endpoint_name}/health-check` | `POST` |

## 5. 文档核对时必须避免的误判

- 不要把 `VERSION_MAPPING.py` 误判为全部 API 的唯一注册入口；运行时还要看 `router_registry.py` 和 `api/v1/router.py`
- 不要把旧 Markdown 里的端点统计直接当成当前值；必须重新生成 OpenAPI 后再写入文档
- 不要把前端相对路径（例如 `/v1/...`）和后端最终 HTTP 路径（例如 `/api/v1/...`）混为一谈

## 6. 交付前核对项

- 当前 OpenAPI 已重新生成
- `docs/api/openapi.json` 已同步
- 前端调用过的关键 API 已与 OpenAPI 对表
- 文档中所有“当前数量”“当前可用”“当前阻塞”均带日期或来源说明

