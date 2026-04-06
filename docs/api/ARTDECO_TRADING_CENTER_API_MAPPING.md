# ArtDeco 量化交易管理中心 - API端点映射表

> **设计方案说明**:
> 本文件是 API 相关的设计稿、映射文档或方案说明，不是当前 API 契约、当前实现基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁、当前执行口径或 API 契约事实源，请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，以及实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json`。
>
> 文内结构设计、端点规划、映射关系和实施建议应结合当前代码与主线文档复核；若未落地，不得直接当作当前标准。


**版本**: 3.0.0
**文档日期**: 2026-01-22
**总计**: 5大模块 × 16个子模块 × 48个功能节点 = **48个API端点**

---

## 📊 API端点映射总览

| 模块 | 子模块数 | 功能节点数 | API端点数 |
|------|---------|-----------|----------|
| 市场总览 | 3 | 9 | 9 |
| 交易管理 | 4 | 12 | 12 |
| 策略中心 | 3 | 9 | 9 |
| 风险控制 | 3 | 9 | 9 |
| 系统管理 | 3 | 9 | 9 |
| **总计** | **16** | **48** | **48** |

---

## 🌳 市场总览模块 API映射

### 实时行情监控 (3个API端点)

| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 市场指数 | `GET /api/market/realtime/indices` | TDengine → SSE推送 | `ArtDecoMarketIndices.vue` |
| 股票排行 | `GET /api/market/rankings/stocks` | PostgreSQL查询 | `ArtDecoStockRankings.vue` |
| 成交统计 | `GET /api/market/statistics/volume` | TDengine聚合 | `ArtDecoVolumeStats.vue` |

**实时数据流**:
- WebSocket频道: `market:realtime`
- SSE端点: `/api/market/realtime/kline/{symbol}`
- 推送频率: 1000ms (可配置)

---

### 市场数据分析 (3个API端点)

| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 技术指标 | `GET /api/indicators/calculate` | 实时计算 → Redis缓存 | `ArtDecoTechnicalIndicators.vue` |
| 资金流向 | `GET /api/market/capital-flow` | TDengine时序数据 | `ArtDecoCapitalFlow.vue` |
| 龙虎榜 | `GET /api/market/longhubang` | PostgreSQL事务数据 | `ArtDecoLongHuBang.vue` |

**技术指标支持**:
- MA (移动平均线): MA5, MA10, MA20, MA60
- MACD (指数平滑异同移动平均线)
- KDJ (随机指标)
- BOLL (布林带)
- RSI (相对强弱指数)

---

### 行业概念分析 (3个API端点)

| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 行业板块 | `GET /api/market/industries` | PostgreSQL参考数据 | `ArtDecoIndustryAnalysis.vue` |
| 概念板块 | `GET /api/market/concepts` | PostgreSQL参考数据 | `ArtDecoConceptAnalysis.vue` |
| 板块对比 | `POST /api/analysis/compare-sectors` | 多表关联查询 | `ArtDecoSectorComparison.vue` |

**板块分类**:
- 行业板块: 28个申万一级行业
- 概念板块: 150+热门概念题材
- 地域板块: 各省市区域分类

---

## 💼 交易管理模块 API映射

### 交易信号 (3个API端点)

| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 信号概览 | `GET /api/signals/overview` | PostgreSQL聚合 | `ArtDecoSignalOverview.vue` |
| 信号详情 | `GET /api/signals/{id}/details` | PostgreSQL详情查询 | `ArtDecoSignalDetails.vue` |
| 历史信号 | `GET /api/signals/history` | TDengine时序数据 | `ArtDecoSignalHistory.vue` |

**AI信号生成**:
- 机器学习模型: LSTM/Transformer
- 信号类型: 买入/卖出/持有
- 置信度: 0.0 ~ 1.0
- 徽章标记: `AI`

---

### 交易历史 (3个API端点)

| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 订单记录 | `GET /api/trade/orders` | PostgreSQL事务表 | `ArtDecoOrderRecords.vue` |
| 成交记录 | `GET /api/trade/trades` | PostgreSQL事务表 | `ArtDecoTradeRecords.vue` |
| 交易统计 | `GET /api/trade/statistics` | PostgreSQL聚合查询 | `ArtDecoTradeStats.vue` |

**订单状态**:
- 待成交 (Pending)
- 部分成交 (Partial)
- 全部成交 (Filled)
- 已撤销 (Cancelled)
- 拒绝 (Rejected)

---

### 持仓监控 (3个API端点)

| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 当前持仓 | `GET /api/trade/positions` | PostgreSQL持仓表 | `ArtDecoCurrentPositions.vue` |
| 盈亏分析 | `GET /api/trade/pnl-analysis` | 实时计算引擎 | `ArtDecoPnLAnalysis.vue` |
| 风险指标 | `GET /api/risk/position-metrics` | 风险计算引擎 | `ArtDecoPositionRisk.vue` |

**实时数据流**:
- WebSocket频道: `position:updates`
- 推送频率: 500ms (持仓变化时)
- 数据范围: 当前账户所有持仓

---

### 绩效分析 (3个API端点)

| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 收益曲线 | `GET /api/performance/returns` | TDengine时序数据 | `ArtDecoReturnCurve.vue` |
| 归因分析 | `POST /api/analysis/attribution` | 多因子模型计算 | `ArtDecoAttributionAnalysis.vue` |
| 绩效指标 | `GET /api/performance/metrics` | 标准指标计算 | `ArtDecoPerformanceMetrics.vue` |

**绩效指标**:
- 总收益率 (Total Return)
- 年化收益率 (Annualized Return)
- 夏普比率 (Sharpe Ratio)
- 最大回撤 (Max Drawdown)
- 胜率 (Win Rate)
- 盈亏比 (Profit/Loss Ratio)

---

## 🧠 策略中心模块 API映射

### 策略管理 (3个API端点)

| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 策略列表 | `GET /api/strategy/list` | PostgreSQL策略表 | `ArtDecoStrategyList.vue` |
| 创建策略 | `POST /api/strategy/create` | 策略模板引擎 | `ArtDecoStrategyCreation.vue` |
| 策略配置 | `PUT /api/strategy/{id}/config` | 参数验证存储 | `ArtDecoStrategyConfig.vue` |

**策略类型**:
- 趋势跟踪 (Trend Following)
- 均值回归 (Mean Reversion)
- 动量策略 (Momentum)
- 统计套利 (Statistical Arbitrage)
- 机器学习 (Machine Learning)

---

### 回测分析 (3个API端点)

| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 回测设置 | `POST /api/backtest/setup` | 参数验证存储 | `ArtDecoBacktestSetup.vue` |
| 回测结果 | `GET /api/backtest/{id}/results` | GPU加速计算结果 | `ArtDecoBacktestResults.vue` |
| 回测报告 | `GET /api/backtest/{id}/report` | HTML/PDF报告生成 | `ArtDecoBacktestReport.vue` |

**回测引擎**:
- GPU加速: CUDA/cuDF集成
- 回测速度: 68.58x性能提升
- 数据范围: TDengine历史数据
- 支持频率: Tick/分钟/日线

**徽章标记**: `GPU`

---

### 策略优化 (3个API端点)

| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 参数优化 | `POST /api/optimization/parameters` | 遗传算法优化 | `ArtDecoParameterOptimization.vue` |
| 风险调整 | `POST /api/optimization/risk-adjust` | 风险模型调整 | `ArtDecoRiskAdjustment.vue` |
| 性能评估 | `GET /api/optimization/performance` | 多维度评估 | `ArtDecoPerformanceEvaluation.vue` |

**优化算法**:
- 网格搜索 (Grid Search)
- 遗传算法 (Genetic Algorithm)
- 贝叶斯优化 (Bayesian Optimization)
- 粒子群优化 (PSO)

---

## 🛡️ 风险控制模块 API映射

### 风险监控 (3个API端点)

| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 风险概览 | `GET /api/risk/overview` | 综合风险指标 | `ArtDecoRiskOverview.vue` |
| 风险趋势 | `GET /api/risk/trends` | TDengine时序数据 | `ArtDecoRiskTrends.vue` |
| 风险预警 | `GET /api/risk/alerts` | 实时告警数据 | `ArtDecoRiskAlerts.vue` |

**实时数据流**:
- WebSocket频道: `risk:alerts`
- 告警级别: 严重/高/中/低
- 推送频率: 实时（触发时）

---

### 公告监控 (3个API端点)

| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 公告列表 | `GET /api/announcements/list` | PostgreSQL公告表 | `ArtDecoAnnouncementList.vue` |
| 公告筛选 | `POST /api/announcements/filter` | 智能筛选引擎 | `ArtDecoAnnouncementFilter.vue` |
| 公告分析 | `POST /api/analysis/announcements` | NLP情感分析 | `ArtDecoAnnouncementAnalysis.vue` |

**NLP分析**:
- 情感分析: 积极/中性/消极
- 关键实体提取: 公司名称/股票代码
- 事件分类: 业绩/并购/重组/分红
- 徽章标记: `NLP`

---

### 风险告警 (3个API端点)

| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 告警中心 | `GET /api/risk/alerts/center` | 实时告警聚合 | `ArtDecoAlertCenter.vue` |
| 告警规则 | `GET /api/risk/alerts/rules` | 规则配置管理 | `ArtDecoAlertRules.vue` |
| 告警历史 | `GET /api/risk/alerts/history` | PostgreSQL历史记录 | `ArtDecoAlertHistory.vue` |

**告警类型**:
- 持仓风险 (Position Risk)
- 市场风险 (Market Risk)
- 流动性风险 (Liquidity Risk)
- 信用风险 (Credit Risk)
- 操作风险 (Operational Risk)

---

## ⚙️ 系统管理模块 API映射

### 监控面板 (3个API端点)

| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 系统状态 | `GET /api/monitoring/system-status` | 健康检查数据 | `ArtDecoSystemStatus.vue` |
| 性能指标 | `GET /api/monitoring/performance` | Prometheus指标 | `ArtDecoPerformanceMetrics.vue` |
| 数据质量 | `GET /api/monitoring/data-quality` | 质量检查结果 | `ArtDecoDataQuality.vue` |

**监控指标**:
- CPU使用率: < 80%
- 内存使用率: < 85%
- 磁盘使用率: < 90%
- API响应时间: < 100ms
- 数据库连接池: < 80%占用

---

### 数据管理 (3个API端点)

| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 数据导入 | `POST /api/data/import` | 文件上传处理 | `ArtDecoDataImport.vue` |
| 数据导出 | `POST /api/data/export` | 多格式导出 | `ArtDecoDataExport.vue` |
| 数据清理 | `POST /api/data/cleanup` | 数据清理任务 | `ArtDecoDataCleanup.vue` |

**支持格式**:
- 导入: CSV, Excel, JSON, Parquet
- 导出: CSV, Excel, JSON, Parquet, PDF
- 清理: 去重/补全/标准化

---

### 系统设置 (分段契约，非单体统一API)

| 功能节点 | 当前真实接口/行为 | 数据流向 | Vue组件映射 |
|---------|------------------|---------|-------------|
| System-Config 页面 | `GET/PUT /api/v1/system/settings/general` + `GET /api/health/detailed` + `GET /api/health` | 系统通用配置读写 + 健康监控读取 | `views/system/Settings.vue` |
| System-Config section owner | `GET/PUT /api/v1/system/settings/security` + `GET/POST /api/v1/data-sources/config/*` + `GET/PUT /api/notification/preferences` | security/system、datasource/system、notification/user 各自归属 | `TradingApiManager.ts` 分段组合 |
| 数据源配置写回 | `GET/POST /api/v1/data-sources/config/*` | 数据源配置管理 | `ArtDecoDataManagement.vue` |

**设置范围**:
- 通用系统参数: `backend_url`、`max_backtest_jobs`、`default_slippage_percent`、`fee_rate_bps`
- 安全参数: `session_timeout_minutes`、`mfa_required`、`ip_allowlist_enabled`、`password_policy_level`
- 数据源配置: 保持由 `System-Data` 与 `/api/v1/data-sources/config/*` 管理
- 通知偏好: 保持由 `/api/notification/preferences` 管理
- 说明: 当前活跃代码路径采用受治理的 sectioned contract，而不是补出一个单体统一 `/api/system/settings/*` 真相层；`general/security` 由 PostgreSQL `system_config` 驱动，datasource 与 notification 保持各自 owner 契约

---

## 🔄 数据流转架构

### US3架构集成

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway Layer                       │
│                  (FastAPI + CORS + JWT)                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ 市场数据API  │  │ 交易API     │  │ 策略API      │       │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│         │                │                │               │
│  ┌──────▼────────────────▼────────────────▼──────┐       │
│  │         Unified Manager (路由层)               │       │
│  └──────┬─────────────────────────────────────┬──┘       │
│         │                                     │           │
│  ┌──────▼──────┐  ┌─────────────┐  ┌────────▼────┐     │
│  │  TDengine   │  │ PostgreSQL  │  │   Redis     │     │
│  │ 高频时序数据 │  │ 所有其他数据 │  │ L2缓存+消息 │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 数据分类路由

| 数据分类 | 主要API前缀 | 存储数据库 | 缓存策略 |
|---------|------------|-----------|---------|
| Tick数据 | `/api/market/realtime/tick` | TDengine | Redis (1秒TTL) |
| 分钟K线 | `/api/market/kline/{period}` | TDengine | Redis (5分钟TTL) |
| 日线数据 | `/api/market/daily` | PostgreSQL TimescaleDB | Redis (1小时TTL) |
| 参考数据 | `/api/market/reference` | PostgreSQL | Redis (24小时TTL) |
| 交易数据 | `/api/trade/*` | PostgreSQL | Redis (5分钟TTL) |
| 策略数据 | `/api/strategy/*` | PostgreSQL | Redis (30分钟TTL) |
| 风险数据 | `/api/risk/*` | PostgreSQL | Redis (10分钟TTL) |

---

## 📊 实时数据推送架构

### WebSocket频道映射

| 频道名称 | 订阅端点 | 推送频率 | 数据类型 |
|---------|---------|---------|---------|
| `market:realtime` | `/ws/market/realtime` | 1000ms | 市场指数/股票排行 |
| `market:kline` | `/ws/market/kline/{symbol}` | 5000ms | K线数据更新 |
| `position:updates` | `/ws/position/updates` | 实时 | 持仓变化 |
| `risk:alerts` | `/ws/risk/alerts` | 实时 | 风险告警 |
| `strategy:signals` | `/ws/strategy/signals` | 实时 | 交易信号 |

### SSE端点映射

| SSE端点 | 数据内容 | 重连策略 |
|---------|---------|---------|
| `/api/market/realtime/indices` | 市场指数推送 | 自动重连(3秒间隔) |
| `/api/market/realtime/kline/{symbol}` | 个股K线推送 | 自动重连(5秒间隔) |
| `/api/signals/stream` | 交易信号流 | 手动重连 |

---

## 🔐 认证与权限

### JWT认证流程

```
1. 用户登录 → POST /api/auth/login
2. 返回JWT Token (有效期: 24小时)
3. 前端存储Token (localStorage + Pinia)
4. 每次请求附加: Authorization: Bearer {token}
5. Token过期 → 401响应 → 刷新Token
```

### API权限等级

| 权限等级 | 可访问API | 说明 |
|---------|---------|------|
| `guest` | 市场数据(只读) | 游客访问 |
| `user` | 市场数据 + 个人交易 | 普通用户 |
| `trader` | 所有交易API | 交易员 |
| `admin` | 所有API + 系统管理 | 管理员 |

---

## 📈 性能优化策略

### 缓存策略

| 数据类型 | 缓存层级 | TTL | 缓存键模式 |
|---------|---------|-----|-----------|
| 市场指数 | L1(内存) + L2(Redis) | 5秒 | `market:indices:{code}` |
| 股票排行 | L2(Redis) | 30秒 | `market:rankings:{type}` |
| K线数据 | L2(Redis) | 1分钟 | `kline:{symbol}:{period}` |
| 技术指标 | L2(Redis) | 5分钟 | `indicator:{symbol}:{name}:{params}` |
| 参考数据 | L2(Redis) | 24小时 | `reference:{type}:{id}` |

### 批量操作优化

```typescript
// 批量获取股票行情
POST /api/market/batch/quotes
Body: {
  symbols: string[]  // 最多100个股票
}
Response: {
  quotes: Map<symbol, Quote>
  timestamp: number
}
```

---

## 🚀 API版本管理

### 当前版本

| 版本号 | 发布日期 | 状态 | 说明 |
|-------|---------|------|------|
| v3.0.0 | 2026-01-22 | ✅ 稳定 | ArtDeco优化版本 |

### 版本策略

- **URL版本**: `/api/v3//*` (当前版本)
- **向后兼容**: 保留v1、v2端点（标记为deprecated）
- **弃用通知**: 响应头`X-API-Deprecated: true`
- **迁移指南**: `/docs/api/migration-v2-to-v3.md`

---

## 📝 API响应格式

### 成功响应

```json
{
  "success": true,
  "data": {
    // 业务数据
  },
  "timestamp": 1705891200000,
  "requestId": "uuid"
}
```

### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "人类可读的错误信息",
    "details": {}
  },
  "timestamp": 1705891200000,
  "requestId": "uuid"
}
```

### 错误码映射

| 错误码 | HTTP状态 | 说明 |
|-------|---------|------|
| `INVALID_PARAMS` | 400 | 参数验证失败 |
| `UNAUTHORIZED` | 401 | 未授权访问 |
| `FORBIDDEN` | 403 | 权限不足 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |

---

## 📚 相关文档

- **设计方案**: `ARTDECO_TRADING_CENTER_OPTIMIZED_V3.md`
- **组件文档**: `web/frontend/src/components/artdeco/docs/`
- **API文档**: `http://localhost:8020/docs` (Swagger UI)
- **性能报告**: `docs/reports/API_PERFORMANCE_REPORT.md`

---

**文档版本**: 3.0.0
**最后更新**: 2026-01-22
**维护者**: Backend Team + Frontend Team
**审核状态**: ✅ 已审核
