# API与Web组件对齐方案 (2025版)

> **版本**: 2.0
> **最后更新**: 2025-12-06
> **适用范围**: MyStocks Web 端开发 (FastAPI + Vue 3)

## 1. 核心理念：类型驱动与组件适配

本项目采用 **模块化单体 (Modular Monolith)** 架构，前端采用 **Vue 3 + TypeScript**，后端采用 **FastAPI**。为了实现 API 与 Web 组件的丝滑结合，我们遵循以下核心原则：

1.  **Schema First (契约优先)**: 后端 Pydantic 模型是单一数据源 (SSOT)，前端类型定义应与后端保持同步。
2.  **Adapter Pattern (适配器模式)**: 前端 Service 层负责将 API 响应转换为组件所需的 Props 格式，隔离后端数据结构变化对 UI 的影响。
3.  **Smart/Dumb Components (智能/哑组件分离)**:
    *   **智能组件 (Views/Containers)**: 负责调用 API、管理状态、处理业务逻辑。
    *   **哑组件 (UI Components)**: 只通过 Props 接收数据，通过 Events 抛出交互，不直接依赖 API。

---

## 2. 架构概览

### 2.1 后端结构 (FastAPI)
*   **入口**: `web/backend/app/main.py` (统一网关，处理 CORS, Auth, Exception)
*   **路由**: `web/backend/app/api/` (按业务子域拆分，如 `market.py`, `strategy.py`)
*   **响应标准**: 所有接口统一使用 `web/backend/app/core/responses.py` 定义的响应格式。

```python
# 统一响应结构
{
  "success": true,
  "code": 0,
  "message": "操作成功",
  "data": { ... }, # 业务数据
  "request_id": "req_uuid..."
}
```

### 2.2 前端结构 (Vue 3)
*   **路由**: `web/frontend/src/router/index.js` (按功能特性组织)
*   **API层**: `web/frontend/src/api/` (按模块封装 Axios 请求)
*   **视图层**: `web/frontend/src/views/` (智能组件)
*   **组件层**: `web/frontend/src/components/` (哑组件)

---

## 3. 开发落地指南

### 3.1 后端开发规范

1.  **定义 Pydantic 模型**:
    在 `web/backend/app/schemas/` 中定义请求和响应模型。务必使用 `Field` 添加描述，这将直接生成 Swagger 文档。

    ```python
    # 示例: app/schemas/market_schemas.py
    class KLineResponse(BaseModel):
        date: str = Field(..., description="交易日期 YYYY-MM-DD")
        open: float = Field(..., description="开盘价")
        close: float = Field(..., description="收盘价")
        # ...
    ```

2.  **编写路由处理函数**:
    使用 `response_model` 指定返回类型，FastAPI 会自动进行数据过滤和验证。

    ```python
    # 示例: app/api/market.py
    @router.get("/kline", response_model=APIResponse[List[KLineResponse]])
    async def get_kline(symbol: str):
        data = await service.get_kline(symbol)
        return create_success_response(data=data)
    ```

### 3.2 前端开发规范

1.  **API Client 封装**:
    在 `web/frontend/src/api/` 下创建对应模块的文件。使用拦截器统一处理 `success` 字段和错误提示。

    ```javascript
    // 示例: src/api/market.js
    import request from '@/utils/request'

    export function getKLineData(symbol, period) {
      return request({
        url: '/api/market/kline',
        method: 'get',
        params: { symbol, period }
      })
    }
    ```

2.  **组件适配 (The Adapter)**:
    **关键步骤**：不要让组件直接消费 API 的原始数据。在 View 层或专门的 Adapter 函数中转换数据。

    ```javascript
    // 示例: src/views/StockDetail.vue (智能组件)

    // 1. 调用 API
    const { data } = await getKLineData('600519', 'daily');

    // 2. 适配数据 (Adapter Logic)
    // 将后端字段 (date, open, close) 转换为图表库需要的格式 (timestamp, o, c)
    const chartData = data.map(item => ({
      timestamp: new Date(item.date).getTime(),
      o: item.open,
      c: item.close,
      // ...
    }));

    // 3. 传递给哑组件
    // <k-line-chart :data="chartData" />
    ```

---

## 4. 现有模块映射表

根据当前项目代码 (`web/backend/app/api/` 和 `web/frontend/src/views/`) 整理的核心业务映射：

| 业务子域 | 后端路由文件 (`/api/`) | 前端视图路径 (`/views/`) | 核心组件 (`/components/`) | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| **市场行情** | `market.py`, `market_v2.py` | `Market.vue`, `TdxMarket.vue` | `MarketTable.vue`, `FundFlowPanel.vue` | 包含资金流向、ETF、K线 |
| **策略管理** | `strategy.py`, `strategy_mgmt.py` | `StrategyManagement.vue` | `StrategyForm.vue` | 涉及复杂表单提交 |
| **交易执行** | `trade/` | `TradeManagement.vue` | `TradePanel.vue` | 需严格 CSRF 保护 |
| **数据分析** | `technical_analysis.py` | `Analysis.vue`, `TechnicalAnalysis.vue` | `TechnicalIndicators.vue` | 图表密集型 |
| **自选股** | `watchlist.py` | `Watchlist.vue` | `StockGroup.vue` | 拖拽排序交互 |
| **系统监控** | `system.py`, `monitoring.py` | `SystemMonitor.vue` | `LogViewer.vue` | 包含 SSE 实时推送 |

---

## 5. 调试与验证工具

为了确保对齐方案的有效性，推荐使用以下工具链：

1.  **Swagger UI / OpenAPI**:
    *   地址: `http://localhost:8000/docs`
    *   用途: 后端开发完成后，前端直接通过 Swagger 查看字段定义，甚至可使用代码生成工具生成 TypeScript 类型定义。

2.  **FastAPI Pydantic 模型**:
    *   用途: 后端的强类型校验是前端数据质量的第一道防线。后端改动模型时，Swagger 文档会自动更新，提醒前端同步。

3.  **Playwright E2E 测试**:
    *   用途: 验证 "API -> 前端适配 -> 组件渲染" 整个链路是否通畅。
    *   命令: `npx playwright test` (需配置好 `playwright.config.ts`)

4.  **Mock 数据工厂**:
    *   用途: 在后端接口未就绪时，前端可参考 `docs/api/API_ENDPOINT_DOCUMENTATION.md` 使用 Mock 数据先行开发组件 UI。

---

## 6. 常见问题排查

*   **字段不匹配**: 检查后端 Pydantic 模型的 `alias` 配置是否影响了 JSON 序列化，或前端是否使用了错误的字段名（如 `snake_case` vs `camelCase`）。
*   **422 Validation Error**: 通常是前端发送的数据类型与后端 Pydantic 模型定义不一致（如字符串发成了数字）。检查 Swagger 文档中的 Schema 定义。
*   **CORS 错误**: 检查 `main.py` 中的 `CORSMiddleware` 配置，确保前端开发服务器的端口在允许列表中。

---

## 7. 实施路线图

### Phase 1: 基础对齐 (第1周)
1.  后端所有接口补充完整的 Pydantic 模型定义
2.  前端创建对应的 API Client 文件
3.  建立基础的错误处理和响应拦截

### Phase 2: 适配器模式落地 (第2周)
1.  在 Views 层实现数据转换逻辑
2.  Components 层保持纯净，只接收 Props
3.  建立 TypeScript 类型生成流程

### Phase 3: 测试与优化 (第3周)
1.  编写 E2E 测试用例验证关键流程
2.  性能优化：减少重复请求，实现智能缓存
3.  文档完善和团队培训

---

## 8. 最佳实践总结

### 后端最佳实践
1.  **始终使用 Pydantic 模型**，即使是对外暴露的简单接口
2.  **统一错误响应格式**，使用 `create_success_response` 和 `create_error_response`
3.  **保持 RESTful 风格**，GET 用于查询，POST 用于创建，PUT 用于更新，DELETE 用于删除
4.  **合理使用路由前缀**，按业务域组织 (`/api/market`, `/api/strategy`)

### 前端最佳实践
1.  **API 层与 UI 层分离**，组件不直接调用 HTTP 请求
2.  **使用 TypeScript 严格模式**，与后端 Pydantic 模型保持类型同步
3.  **实现统一的错误处理**，在 Axios 拦截器中处理 401/403/422/500
4.  **合理使用 Vuex/Pinia**，避免过度设计

### 协作最佳实践
1.  **先定接口再开发**，通过 Swagger UI 确认接口定义
2.  **保持文档同步**，接口变更及时更新 API_FRONTEND_MAPPING.md
3.  **代码审查重点**：检查类型匹配、错误处理、安全性
4.  **定期进行跨端联调**，确保约定得到遵守

---

**下一步建议**:
对于新功能的开发，建议优先更新 `web/backend/app/schemas` 定义数据结构，确认无误后再进行业务逻辑和 UI 开发。