# MyStocks API 开发指南

> **使用说明**:
> 本文档是开发规范摘要，不替代当前代码与 OpenAPI 契约真相。
> 共享规则以 `architecture/STANDARDS.md` 为准；API 契约以 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。

## 1. 当前开发基线

截至 `2026-04-24`：

- 当前 OpenAPI 统计为 `455 paths / 493 operations`
- 当前 API 文档不得再把“571 个端点”或“469 个端点”写成现状
- API 运行时注册链路必须同时核对：
  - `web/backend/app/api/VERSION_MAPPING.py`
  - `web/backend/app/router_registry.py`
  - `web/backend/app/api/v1/router.py`

## 2. 强制规则

### 2.1 契约先行

新增或修改 API 时，必须在同一提交内完成：

1. 更新 FastAPI 路由
2. 更新 Pydantic request / response schema
3. 重新导出 OpenAPI
4. 同步 `docs/api/openapi.json`
5. 如前端消费该接口，更新前端类型或调用层

禁止只改 Markdown，不改契约。

### 2.2 单一真相源

以下材料都是派生产物，不得与运行时契约并列为真相源：

- Markdown 统计文档
- 前端手写类型
- 临时 curl 样例
- 调试脚本中的示例 JSON

### 2.3 响应标准

依据仓库规则，新增 API 默认应遵循统一响应包装结构。若接手历史接口，不得擅自引入第三套返回格式，必须先核对兼容面。

### 2.4 版本与注册

不是所有新接口都需要写入 `VERSION_MAPPING.py`。

只有属于 registry-managed versioned prefix 的 router，才应进入该映射文件。最终是否可用，仍必须回到 `router_registry.py` 和运行时导出的 OpenAPI 验证。

## 3. 路径设计约束

- 资源路径优先使用名词
- 版本化业务 API 优先使用 `/api/v1/*`、`/api/v2/*`
- 非版本化系统能力按既有约定走：
  - `/api/contracts/*`
  - `/api/health/*`
  - `/health`
  - 其他已存在的系统级入口

## 4. 前后端协同要求

### 4.1 Frontend route meta.api

若接口对应某个前端活跃业务页，页面路由上的 `meta.api` 应表达首屏主 API，而不是整页所有接口的抽象合集。

正确做法：

- 选择“入页即请求”的主读接口
- 保持 `router/index.ts`、`pageConfig.ts`、E2E 页面契约一致

错误做法：

- 把用户点击后才触发的操作接口写成首屏主 API
- 路由已改，但页面契约和文档还停留在旧路径

### 4.2 当前已收正示例

- `/dashboard` -> `/api/v1/market/quotes`
- `/system/api` -> `/api/health`
- `/strategy/repo` -> `/api/v1/strategy/strategies`
- `/strategy/backtest` -> `/api/v1/strategy/strategies`
- `/data/industry` -> `/api/v2/market/sector/fund-flow?sector_type=行业`
- `/data/fund-flow` -> `/api/akshare/market/fund-flow/hsgt-summary`

## 5. 推荐开发流程

1. 先确认接口归属与挂载链路
2. 实现或修改 router 与 schema
3. 重新导出 OpenAPI
4. 生成前端类型
5. 更新调用方
6. 更新最小必要文档
7. 补充测试

## 6. 最低验证要求

建议至少执行：

```bash
python scripts/generate_openapi.py --output /tmp/mystocks_openapi_current.json
cp /tmp/mystocks_openapi_current.json docs/api/openapi.json
python scripts/generate_frontend_types.py --openapi-spec docs/api/openapi.json
pytest --no-cov web/backend/tests/test_route_governance_static.py
```

如改动了前端页面首屏主 API，还应至少核对对应页面契约测试。

## 7. 常见错误

- 只更新 Markdown，不更新 OpenAPI
- 只新增 router 文件，未接入运行时注册链路
- 把 `VERSION_MAPPING.py` 当成全部路由的唯一入口
- 文档还写旧路径，前端已切新路径
- 用“接口存在”误写成“该业务域功能已经完成”

## 8. 交易域特别说明

本条线当前对交易域只维护接口与契约口径，不推进交易功能实现。

因此文档中可以写：

- `/api/v1/trade/positions`
- `/api/v1/trade/signals`

但不能写成：

- 交易功能已完工
- 下单链路已完成验收
- 写操作已可用于生产
