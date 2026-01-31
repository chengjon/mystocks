# Mock数据到真实数据迁移实施报告

**生成日期**: 2026-01-20
**实施范围**: 前端核心仪表盘及基础服务API调用
**目标**: 将前端Mock数据调用切换为通过 `apiClient` 的真实API调用，并实现 `USE_MOCK_DATA` 开关。

---

## 📊 执行摘要

本次迁移成功在前端引入了 `USE_MOCK_DATA` 环境开关，并重构了核心仪表盘视图的API调用，使其能够根据配置动态切换使用Mock数据或真实API。

### 关键成果

- ✅ **`USE_MOCK_DATA` 环境开关实现**: 前端现在通过 `.env` 中的 `VITE_USE_MOCK_DATA` 变量控制数据源。
- ✅ **`apiClient` 集成 Mock/Real 切换**: 所有通过 `apiClient` 发起的请求都将根据 `VITE_USE_MOCK_DATA` 的值自动路由到 `mockApiClient` 或真实的后端 API。
- ✅ **仪表盘视图API重构**: `EnhancedDashboard.vue` 和 `Phase4Dashboard.vue` 已更新，使用新的服务层 (`dashboardService`) 来统一获取数据。
- ✅ **系统状态API集成**: `tradingStore` 已更新，通过后端API获取系统状态，并提供给 `ArtDecoTradingCenter.vue`。

### 遗留问题与缺失API

尽管前端调用逻辑已准备就绪，但有部分后端API仍处于缺失或未实现状态。这些API在 `MOCK_TO_REAL_DATA_MIGRATION_ANALYSIS.md` 中已被识别并再次确认。

## 🔍 详细实施步骤与修改

### 1. `USE_MOCK_DATA` 环境开关实现

- **文件修改**:
    - `web/frontend/.env.example`: 添加 `VITE_USE_MOCK_DATA=false` 和 `VITE_API_BASE_URL=http://localhost:8000/api`。
    - `web/frontend/vite.config.ts`: 在 `define` 配置中暴露 `import.meta.env.VITE_USE_MOCK_DATA` 和 `import.meta.env.VITE_API_BASE_URL` 到客户端代码。
    - `web/frontend/src/api/mockApiClient.ts`: 创建一个包含占位符mock函数的 `mockApiClient`，用于模拟API响应。
    - `web/frontend/src/api/apiClient.ts`: 修改 `apiClient` 的 `get`, `post`, `put`, `patch`, `delete` 方法，使其根据 `import.meta.env.VITE_USE_MOCK_DATA` 的值有条件地调用 `mockApiClient` 或真实 `axios` 实例。

- **实现目标**: 前端现在具备了通过环境变量控制使用Mock或真实API的能力。

### 2. `httpClient.js` 重构以使用 `apiClient`

- **文件修改**: `web/frontend/src/services/httpClient.js`
- **修改内容**: 将 `httpClient` 从直接使用 `fetch` 切换为使用 `apiClient`。
    - 移除了冗余的CSRF token处理逻辑（现在由 `apiClient` 的 `axios` 拦截器处理）。
    - 移除了 `baseURL` 的管理。
    - `request` 方法及所有HTTP动词方法现在直接调用 `apiClient` 对应的 `get`, `post`, `put`, `patch`, `delete` 方法。
    - 移除了 `initializeSecurity` 函数，因其功能已被 `apiClient` 内部处理。
- **实现目标**: 确保所有通过 `httpClient` 发起的底层请求都能享受到 `apiClient` 带来的Mock/Real数据切换能力和统一的认证/安全处理。

### 3. `dashboardService.ts` 服务层创建

- **文件创建**: `web/frontend/src/services/dashboardService.ts`
- **内容**: 封装了 `EnhancedDashboard.vue` 和 `Phase4Dashboard.vue` 中使用的所有仪表盘相关API调用，包括：
    - `getMarketOverview()`
    - `getPriceDistribution()`
    - `getHotIndustries()`
    - `getHotConcepts()`
    - `getMarketHeatChartData()`
    - `getLeadingSectorChartData()`
    - `getCapitalFlowChartData()`
    - `getIndustryCapitalFlowChartData()`
    - `getDashboardSummary()` (用于 `Phase4Dashboard.vue`)
- **实现目标**: 提供一个统一的、高内聚的仪表盘数据获取服务层，简化视图组件的逻辑。

### 4. `EnhancedDashboard.vue` 迁移

- **文件修改**: `web/frontend/src/views/EnhancedDashboard.vue`
- **修改内容**:
    - 移除了直接的 `dataApi` 导入。
    - 导入并使用 `dashboardService` 来替代所有原先硬编码的Mock数据逻辑和 `dataApi.getMarketOverview()` 调用。
    - 更新了Element Plus图标的导入方式，以实现更好的tree-shaking和一致性。
- **实现目标**: `EnhancedDashboard.vue` 现在完全通过 `dashboardService` 获取数据，并间接支持Mock/Real切换。

### 5. `tradingStore.ts` 系统状态API集成

- **文件修改**: `web/frontend/src/stores/trading.ts`
- **修改内容**:
    - 引入 `apiGet` 进行API调用。
    - 增加了 `systemStatus`, `apiStatus`, `dataQualityStatus`, `systemLoadStatus`, `version`, `lastUpdateTime` 等状态变量。
    - 实现了 `fetchSystemStatus` action，通过调用 `/api/health` 和 `/api/system/info` (假设存在) 来获取并更新系统状态。
    - 将 `fetchSystemStatus` 集成到 `refreshAllData` 中，并设置了每分钟定时更新。
- **实现目标**: 为 `ArtDecoTradingCenter.vue` 提供动态的、来自真实API的系统状态信息。

### 6. `ArtDecoTradingCenter.vue` 状态集成

- **文件修改**: `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue`
- **修改内容**: 将原先本地定义的 `systemStatus`、`apiStatus` 等状态变量替换为 `computed` 属性，直接映射到 `tradingStore` 中的相应状态。
- **实现目标**: `ArtDecoTradingCenter.vue` 现在展示的是通过 `tradingStore` 从后端获取的实时系统状态。

### 7. `Phase4Dashboard.vue` 迁移

- **文件修改**: `web/frontend/src/views/demo/Phase4Dashboard.vue`
- **修改内容**:
    - 移除了直接的 `axios` 导入和使用。
    - 导入并使用 `dashboardService.getDashboardSummary()` 来获取仪表盘汇总数据。
    - 适配了数据处理逻辑以正确解封装 `UnifiedResponse`。
- **实现目标**: `Phase4Dashboard.vue` 现在通过 `dashboardService` 获取其所有数据，并间接支持Mock/Real切换。

---

## 🚨 缺失的API端点清单 (再次确认，需要后端补充或实现)

此清单与 `MOCK_TO_REAL_DATA_MIGRATION_ANALYSIS.md` 中的清单一致，并经过 `API_ENDPOINTS_STATISTICS_REPORT.md` 交叉验证后确认。前端调用已准备就绪，但后端仍需提供以下API的实际数据：

**🔴 P0 - 最高优先级（Dashboard必需）**
1.  **指数列表API**
    *   路径: `/api/market/v2/indices/list`
    *   功能: 获取主要指数列表
    *   **状态:** 后端实现必需。
2.  **市场统计API**
    *   路径: `/api/market/v2/market-stats`
    *   功能: 获取市场统计数据
    *   **状态:** 后端实现必需。
3.  **用户持仓API**
    *   路径: `/api/v1/portfolio/{user_id}`
    *   功能: 获取用户持仓数据
    *   **状态:** 后端实现必需或明确列出现有端点。

**🟡 P1 - 高优先级（功能增强）**
4.  **行业列表API验证**
    *   路径: `/api/analysis/industry/list`
    *   当前状态: 端点存在但返回空数据
    *   **状态:** 后端数据源/实现修复必需。
5.  **概念列表API验证**
    *   路径: `/api/analysis/concept/list`
    *   当前状态: 端点存在但返回空数据
    *   **状态:** 后端数据源/实现修复必需。

**🟢 P2 - 中等优先级（锦上添花）**
6.  **策略列表API**
    *   路径: `/api/strategy/{user_id}/active`
    *   功能: 返回用户活跃策略
    *   **状态:** 后端实现必需（或对现有策略列表端点进行过滤）。
7.  **股票搜索API**
    *   路径: `/api/stock/search`
    *   功能: 股票搜索
    *   **状态:** 端点可能存在（`stock_search.py`）但需要迁移到真实数据。

---

## 🎯 结论

前端已完成对指定视图 (`EnhancedDashboard.vue`, `ArtDecoTradingCenter.vue`, `Phase4Dashboard.vue`) 的Mock数据调用到真实API调用的切换准备。核心的 `USE_MOCK_DATA` 开关也已全面集成到 `apiClient` 层。当前，前端将根据 `.env` 配置调用Mock数据或等待后端提供实际数据。

要实现完整的真实数据流，后端团队需要优先实现上述缺失的API端点，并确保现有被Mock的API端点能返回真实数据。

---

**报告生成**: 2026-01-20
**报告版本**: v1.0
**实施状态**: ✅ 前端核心仪表盘API调用已迁移
**下一步**: 后端团队实现缺失API并迁移Mocked API
