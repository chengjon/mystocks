# MyStocks API 映射与依赖关系文档 (v3.1 核心对齐版)

本文档定义了前端 UI 组件与后端 API 端点之间的核心契约，所有路径均已对齐至 `/api/v1` 标准。

---

## 1. 认证与安全 (Authentication)
**前缀**: `/api/v1/auth`

| 逻辑功能 | 组件路径 | 对应 API | 方法 | 响应格式 |
| :--- | :--- | :--- | :--- | :--- |
| **登录** | `/src/views/Login.vue` | `/api/v1/auth/login` | `POST` | `UnifiedResponse<LoginToken>` |
| **用户信息** | `/src/stores/auth.ts` | `/api/v1/auth/me` | `GET` | `UnifiedResponse<User>` |
| **CSRF** | `/src/main.js` | `/api/v1/auth/csrf` | `GET` | `{"token": "..."}` |

## 2. 市场与数据中心 (Market & Data)
**前缀**: `/api/v1/market`, `/api/v1/data`

| 逻辑功能 | 视图组件路径 | 对应 API | 别名/Alias |
| :--- | :--- | :--- | :--- |
| **实时行情** | `views/artdeco-pages/market-tabs/MarketRealtimeTab.vue` | `/api/v1/market/quotes` | - |
| **K线分析** | `views/artdeco-pages/market-tabs/MarketKLineTab.vue` | `/api/v1/market/kline` | `/api/data/stocks/kline` |
| **资金流向** | `views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue` | `/api/v1/market/fund-flow` | - |
| **问财选股** | `views/artdeco-pages/ArtDecoMarketData.vue` | `/api/v1/market/wencai` | `/api/v1/data/stocks/search` |

## 3. 策略与交易 (Strategy & Trading)
**前缀**: `/api/v1/strategy`, `/api/v1/trade`

| 逻辑功能 | 视图组件路径 | 对应 API | 备注 |
| :--- | :--- | :--- | :--- |
| **策略管理** | `views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue` | `/api/v1/strategy/strategies` | - |
| **交易信号** | `views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue` | `/api/v1/trade/signals` | Alias: `/trading/signals` |
| **持仓监控** | `views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` | `/api/v1/trade/positions` | Alias: `/trading/positions` |

## 4. 响应规范 (Standard Response)
所有 API 必须遵循以下包装格式：
```json
{
  "success": true,
  "code": 200,
  "data": {},
  "message": "...",
  "request_id": "uuid-v4"
}
```

---
**更新日期**: 2026-02-16  
**版本**: v3.1.0 (ArtDeco Architecture)
