# 新增数据源/API 接口开发指引

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


本文档用于指导当前仓库新增数据源接口、数据源配置接口和通用后端 API 的接入方式。本文档已按 `2026-04-24` 当前实现重新核对。

## 1. 接入前先判断 API 归属

新增 API 前先决定它属于哪一类：

| 类别 | 典型路径 | 注册方式 |
|------|----------|----------|
| 版本化业务 API | `/api/v1/*`、`/api/v2/*` | `VERSION_MAPPING.py` + `router_registry.py` |
| registry-managed v1 业务域 | `/api/v1/auth/*`、`/api/v1/market/*` 等 | canonical router + `VERSION_MAPPING.py` |
| `api/v1` 聚合域 | `/api/v1/system/*`、`/api/v1/analysis/*` 等 | `web/backend/app/api/v1/router.py` |
| 非版本化系统 API | `/api/contracts/*`、`/api/health/*`、`/api/multi-source/*` | `router_registry.py` 直接注册 |
| 数据源管理 API | `/api/v1/data-sources/*` | `data_source_registry.py` / `data_source_config.py` |

关键规则：

- 不是所有新接口都必须更新 `VERSION_MAPPING.py`
- 只有“走 registry-managed versioned prefix”的 router 才需要进入 `VERSION_MAPPING.py`
- 无论是否版本化，最终都要回到 `router_registry.py` 核对运行时挂载

## 2. 强制约束

### 2.1 契约先行

新增或修改接口时，必须保证：

1. FastAPI 路由与 Pydantic Schema 已更新
2. `python scripts/generate_openapi.py --output /tmp/mystocks_openapi_current.json` 可重新导出
3. `docs/api/openapi.json` 与当前导出结果同步

### 2.2 响应规范

依据 `architecture/STANDARDS.md`，新增 API 默认必须返回 `UnifiedResponse` 包装结构。

若接入现有历史路由族，不能擅自引入第二套返回格式；必须先核对该路由当前 OpenAPI、调用方和兼容面，再决定是否做兼容层收口。

### 2.3 数据落点

- Tick / 分钟级时序数据：优先 TDengine
- 元数据、配置、管理信息：优先 PostgreSQL
- 热点读取、跨系统消息、分布式锁：Redis

## 3. 推荐实施步骤

### 3.1 新增数据源注册能力

1. 在 `web/backend/app/api/data_source_registry.py` 或相关模块增加 endpoint 定义
2. 若涉及配置持久化，同时更新 `web/backend/app/api/data_source_config.py`
3. 为新数据源准备可执行的 `test_parameters`
4. 确保 `/api/v1/data-sources/{endpoint_name}/test` 和 `/health-check` 可覆盖它

### 3.2 新增普通业务 API

1. 在对应业务 router 中实现 endpoint
2. 补充 request / response schema
3. 按归属决定是否更新 `VERSION_MAPPING.py`
4. 确认 `router_registry.py` 或 `api/v1/router.py` 已挂载
5. 导出 OpenAPI 并更新前端类型

## 4. 提交前验证

建议至少执行：

```bash
python scripts/generate_openapi.py --output /tmp/mystocks_openapi_current.json
cp /tmp/mystocks_openapi_current.json docs/api/openapi.json
python scripts/generate_frontend_types.py --openapi-spec docs/api/openapi.json
pytest --no-cov web/backend/tests/test_route_governance_static.py
```

若本次修改涉及数据源管理，还应补充：

```bash
curl -s http://localhost:8020/api/v1/data-sources/ | python -m json.tool
curl -s http://localhost:8020/api/v1/data-sources/config/ | python -m json.tool
```

## 5. 常见误区

- 误区 1：只改了 Markdown，不改 OpenAPI 导出
- 误区 2：只加了 router 文件，没有进入运行时注册链路
- 误区 3：把 `VERSION_MAPPING.py` 当成全部 API 的唯一入口
- 误区 4：前端继续调用旧路径，后端已切到新路径

## 6. 本轮 API 管理补充

在 `2026-04-24` 的复核中，已确认一类典型阻塞：

- 前端技术分析兼容层仍调用旧路径
- 当前真实技术分析路径应以以下 OpenAPI 路径为准：
  - `/api/v1/technical/{symbol}/indicators`
  - `/api/v1/technical/{symbol}/signals`
  - `/api/v1/technical/batch/indicators`
