# Backend v1 Route Truth

## Purpose

这份说明只回答一个问题：当前后端 `v1` 路由的 runtime truth 在哪里。

## Canonical Layers

### 1. `web/backend/app/api/v1/router.py`

这是 `v1` 业务聚合面。

它负责聚合当前主动维护的这些领域路由：

- `system/*`
- `strategy/*`
- `trading/*`
- `admin/audit`
- `admin/optimization`
- `analysis/*`

它**不是**所有 `/api/v1/*` 路由的唯一来源。

### 2. `web/backend/app/api/VERSION_MAPPING.py`

这是版本化 prefix 的治理映射表。

它负责声明哪些 canonical router 需要以版本前缀挂载，例如：

- `auth -> /api/v1/auth`
- `market -> /api/v1/market`
- `strategy -> /api/v1/strategy`

这里的 truth 是“版本前缀和挂载约定”，不是业务聚合内容本身。

### 3. `web/backend/app/router_registry.py`

这是最终 runtime 注册入口。

它会：

- 读取 `VERSION_MAPPING`
- 选取对应 canonical router
- 把这些 router 挂载到 FastAPI app 上

因此，真正的运行时路径 truth 以 `router_registry.py` 的注册行为为准。

## Auth Special Case

`/api/v1/auth/*` 是当前最容易混淆的例外。

实际 runtime truth：

- implementation: `web/backend/app/api/auth.py`
- version prefix mapping: `web/backend/app/api/VERSION_MAPPING.py`
- registration: `web/backend/app/router_registry.py`

已退役的平行面：

- `web/backend/app/api/v1/admin/auth.py`

这个文件已从 active tree 删除，不应以任何形式重新并回 `api/v1/router.py` 或 `api/v1/admin/__init__.py`。

## Risk Special Case

`/api/v1/risk/*` 当前也不是由 `web/backend/app/api/v1/router.py` 聚合。

实际 runtime truth：

- implementation: `web/backend/app/api/risk/__init__.py`
- registration: `web/backend/app/router_registry.py`

已退役的平行面：

- `web/backend/app/api/v1/risk/__init__.py`
- `web/backend/app/api/v1/risk/core.py`
- `web/backend/app/api/v1/risk/position.py`
- `web/backend/app/api/v1/risk/alerts.py`
- `web/backend/app/api/v1/risk/rules.py`
- `web/backend/app/api/v1/risk/stop_loss.py`

这组文件已从 active tree 删除，不应重新作为 `/api/v1/risk/*` 的第二套实现保留在 `api/v1/` 目录下。

## Practical Rule

判断一个 `v1` 路由是否是 active runtime truth 时，按下面顺序检查：

1. 如果它是 `/api/v1/auth/*` 这一类版本映射路由，先看 `VERSION_MAPPING.py` 和 `router_registry.py`
2. 如果它是 `/api/v1/risk/*` 这一类 registry-managed canonical router，先看 `app/api/risk/__init__.py` 和 `router_registry.py`
3. 如果它是 `web/backend/app/api/v1/router.py` 已聚合的领域路由，优先看 `api/v1/router.py`
4. 如果某个平行文件既不在 `api/v1/router.py` 聚合，也不在 `router_registry.py` 运行时注册，就不能视为 active runtime truth

## Governance Rule

后续新增或收口 `v1` 路由时：

- 不要把平行兼容文件重新当作主实现
- 不要只看文件路径名判断 runtime truth
- 必须同时核对：
  - `api/v1/router.py`
  - `router_registry.py`
  - `VERSION_MAPPING.py`
