# Mock/Real 数据切换指南

> **参考指南说明**:
> 本文件是 Mock/Real 数据切换专题的当前主指南，不是仓库共享规则的唯一事实来源。
> 若涉及审批门禁、共享工程规则或删除判定，请优先遵循 [`architecture/STANDARDS.md`](../../../architecture/STANDARDS.md)；若涉及页面级 API 行为边界，请回到 [`openspec/specs/api-integration/spec.md`](../../../openspec/specs/api-integration/spec.md)。

## 先说结论

本项目当前的 Mock/Real 切换，不应理解为“任何页面都可以在 mock 和 real 间自由等价切换”。

更准确的理解是：

- Mock 用于开发解耦、测试稳定性和显式 mock 验收
- Real 用于真实接口联调、页面主链验证和生产运行
- 对已进入 `verified` 主线的页面，真实接口优先，失败时显式暴露状态，而不是静默切回 mock

## 常见运行模式

### 1. 显式 Mock 验收模式

适用场景：

- 前端开发早期
- UI/UX 视觉验收
- sandbox-safe 或隔离式自动化验证

常见信号：

- 前端显式启用 `VITE_USE_MOCK_DATA=true`
- 后端按需启用 `USE_MOCK_DATA=true`
- 请求链路可走 mock client、mock API 或 mock fallback

### 2. Real 联调模式

适用场景：

- 页面真实接口消费验证
- smoke / E2E 主链验证
- 生产或准生产联调

常见信号：

- 前端 `VITE_USE_MOCK_DATA=false`
- 后端 `USE_MOCK_DATA=false`
- readiness 探针要求真实后端可达
- 页面读链、写链和字段映射以真实接口为准

### 3. 自动化 fallback 模式

适用场景：

- 自动化浏览器在后端暂不可达时仍需完成非阻塞验收

说明：

- 这类 fallback 是自动化或显式 mock 模式下的受控降级。
- 它不等同于“真实链路已经验证成功”。

## 当前主要开关

### 后端

后端通过 `USE_MOCK_DATA` 控制是否启用 mock API 注册或 mock 相关分支：

```bash
USE_MOCK_DATA=true
USE_MOCK_DATA=false
```

当前代码入口可见于：

- [`web/backend/app/core/config.py`](../../../web/backend/app/core/config.py)

### 前端

前端当前更直接的开关是 `VITE_USE_MOCK_DATA`：

```bash
VITE_USE_MOCK_DATA=true
VITE_USE_MOCK_DATA=false
```

当前代码入口可见于：

- [`web/frontend/src/api/apiClient.ts`](../../../web/frontend/src/api/apiClient.ts)
- [`web/frontend/src/composables/useBackendReadiness.ts`](../../../web/frontend/src/composables/useBackendReadiness.ts)

补充说明：

- 仓库中仍存在一些更早的 `VITE_APP_MODE` 文档口径。
- 实际执行时，应优先相信当前代码和当前脚本，而不是更早的环境变量说明。

## 前端切换要点

### API client

- 当 `VITE_USE_MOCK_DATA=true` 时，前端 `apiClient` 会短路到 mock client。
- 当 `VITE_USE_MOCK_DATA=false` 时，前端请求真实 `/api` 后端。

### readiness

- 前端启动时会进行 `/health/ready` 探针检查。
- 若显式处于 mock 模式，或处于自动化浏览器会话，探针失败时允许进入“mock 验收模式”。
- 若不处于这些受控场景，探针失败应让页面进入阻塞错误态，而不是假装正常运行。

## 推荐切换方式

### 进行真实联调

1. 设置前端 `VITE_USE_MOCK_DATA=false`
2. 设置后端 `USE_MOCK_DATA=false`
3. 启动或确认后端可用
4. 校验 readiness、真实请求、字段映射和页面状态
5. 对 `verified` 页面，确认不存在静默 mock fallback

### 进行显式 Mock 验收

1. 设置前端 `VITE_USE_MOCK_DATA=true`
2. 如需后端 mock 路由，设置 `USE_MOCK_DATA=true`
3. 明确说明当前是 mock 验收，不把结果写成真实联调闭环
4. 如果只是测试壳层和交互，不需要强行伪造真实契约字段

## 如何判断当前是不是“真实通过”

只有满足以下条件，才应表述为真实主链已验证：

- 前端未启用 `VITE_USE_MOCK_DATA`
- 页面请求到真实 API
- 页面消费的字段来自真实响应
- 错误态、空态、request id 状态已正确接通
- 没有对同一路径静默回退 mock

如果缺其中任何一项，默认都不应表述成“真实主链已通过”。

## 与页面 `verified/pending` 的关系

### `verified`

- 主数据源必须是真实 API
- 不得静默 mock fallback
- 必须显式展现状态和 request id

### `pending`

- 路由可保持可达
- 允许壳层、加载态、错误态、空态
- 允许显式 mock 验收
- 不得臆造真实契约字段

## 文档阅读顺序

建议按下面顺序阅读：

1. [`MOCK_DATA_USAGE_RULES.md`](./MOCK_DATA_USAGE_RULES.md)
2. [`web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md`](../../../web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md)
3. [`INDEX.md`](./INDEX.md)

若需要了解历史方案、旧切换设计或更早的架构设想，再进入历史文档。

## 历史口径提醒

以下说法在仓库里仍可能作为历史痕迹存在，但阅读时必须降级理解：

- “三层数据源设计”是全部读者的第一入口
- `VITE_APP_MODE` 是唯一前端切换方式
- 页面可以在 mock 和 real 之间无成本等价切换
- 真实接口失败后继续返回 mock 数据也可视为成功

这些说法不再代表当前主线执行口径。

## 相关文档

- [`MOCK_DATA_USAGE_RULES.md`](./MOCK_DATA_USAGE_RULES.md)
- [`MOCK_REAL_DATA_INDEX.md`](./MOCK_REAL_DATA_INDEX.md)
- [`INDEX.md`](./INDEX.md)
- [`web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md`](../../../web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md)
- [`architecture/STANDARDS.md`](../../architecture/STANDARDS.md)
- [`openspec/specs/api-integration/spec.md`](../../../openspec/specs/api-integration/spec.md)
