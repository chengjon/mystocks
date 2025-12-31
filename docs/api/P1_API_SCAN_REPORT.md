# P1 API端点扫描报告

**扫描日期**: 2025-12-31
**扫描范围**: `/opt/claude/mystocks_phase7_backend/web/backend/app/api/`
**扫描结果**: 134个P1级别API端点

---

## 📊 扫描统计总览

| 模块分类 | API端点数量 | 主要功能 |
|---------|-------------|---------|
| **Backtest API** | 14 | 策略管理、模型训练、回测执行 |
| **Risk API** | 12 | 风险指标计算、风险管理、预警通知 |
| **User API** | 7 | 用户认证、权限管理、会话管理 |
| **Trade API** | 6 | 交易执行、持仓管理、统计分析 |
| **Market API** | 25 | 市场数据获取、ETF、龙虎榜、资金流向 |
| **Technical Analysis API** | 17 | 技术指标计算、形态识别、信号生成 |
| **Dashboard API** | 3 | 仪表盘数据聚合、汇总展示 |
| **Data API** | 16 | 基础数据服务、股票信息、财务数据 |
| **Monitoring API** | 15 | 系统监控、告警管理、实时数据 |
| **其他模块** | 19 | 搜索、任务管理、SSE推送等 |
| **总计** | **134** | **涵盖核心业务功能** |

---

## 🎯 核心P1模块详细清单

### 1. Backtest API (14个端点)

**文件**: `strategy_management.py`, `backtest_ws.py`

| 序号 | HTTP方法 | 路径 | 描述 |
|------|----------|------|------|
| 1 | GET | `/api/v1/strategy/strategies` | 获取策略列表 |
| 2 | POST | `/api/v1/strategy/strategies` | 创建新策略 |
| 3 | GET | `/api/v1/strategy/strategies/{strategy_id}` | 获取策略详情 |
| 4 | PUT | `/api/v1/strategy/strategies/{strategy_id}` | 更新策略 |
| 5 | DELETE | `/api/v1/strategy/strategies/{strategy_id}` | 删除策略 |
| 6 | POST | `/api/v1/strategy/models/train` | 启动模型训练 |
| 7 | GET | `/api/v1/strategy/models/training/{task_id}/status` | 查询训练状态 |
| 8 | GET | `/api/v1/strategy/models` | 获取模型列表 |
| 9 | POST | `/api/v1/strategy/backtest/run` | 执行回测 |
| 10 | GET | `/api/v1/strategy/backtest/results` | 获取回测结果列表 |
| 11 | GET | `/api/v1/strategy/backtest/results/{backtest_id}` | 获取回测详细结果 |
| 12 | GET | `/api/v1/strategy/backtest/results/{backtest_id}/chart-data` | 获取回测图表数据 |
| 13 | WS | `/ws/backtest/{backtest_id}` | 回测进度WebSocket推送 |
| 14 | GET | `/ws/status` | 获取WebSocket连接状态 |

---

### 2. Risk API (12个端点)

**文件**: `risk_management.py`

| 序号 | HTTP方法 | 路径 | 描述 |
|------|----------|------|------|
| 1 | POST | `/api/v1/risk/var-cvar` | 计算VaR和CVaR |
| 2 | POST | `/api/v1/risk/beta` | 计算Beta系数 |
| 3 | GET | `/api/v1/risk/dashboard` | 获取风险仪表盘数据 |
| 4 | GET | `/api/v1/risk/metrics/history` | 获取风险指标历史 |
| 5 | GET | `/api/v1/risk/alerts` | 获取风险预警规则 |
| 6 | POST | `/api/v1/risk/alerts` | 创建风险预警规则 |
| 7 | PUT | `/api/v1/risk/alerts/{alert_id}` | 更新风险预警规则 |
| 8 | DELETE | `/api/v1/risk/alerts/{alert_id}` | 删除风险预警规则 |
| 9 | POST | `/api/v1/risk/notifications/test` | 发送测试通知 |
| 10 | POST | `/api/v1/risk/metrics/calculate` | 计算完整风险指标 |
| 11 | POST | `/api/v1/risk/position/assess` | 评估仓位风险 |
| 12 | POST | `/api/v1/risk/alerts/generate` | 生成风险告警 |

---

### 3. User API (7个端点)

**文件**: `auth.py`

| 序号 | HTTP方法 | 路径 | 描述 |
|------|----------|------|------|
| 1 | POST | `/api/v1/auth/login` | 用户登录获取访问令牌 |
| 2 | POST | `/api/v1/auth/logout` | 用户登出 |
| 3 | GET | `/api/v1/auth/me` | 获取当前用户信息 |
| 4 | POST | `/api/v1/auth/refresh` | 刷新访问令牌 |
| 5 | GET | `/api/v1/auth/users` | 获取用户列表（仅管理员） |
| 6 | GET | `/api/v1/auth/csrf/token` | 获取CSRF保护令牌 |

---

### 4. Trade API (6个端点)

**文件**: `trade/routes.py`

| 序号 | HTTP方法 | 路径 | 描述 |
|------|----------|------|------|
| 1 | GET | `/trade/health` | 健康检查 |
| 2 | GET | `/trade/portfolio` | 获取投资组合概览 |
| 3 | GET | `/trade/positions` | 获取持仓列表 |
| 4 | GET | `/trade/trades` | 获取交易记录列表 |
| 5 | GET | `/trade/statistics` | 获取交易统计数据 |
| 6 | POST | `/trade/execute` | 执行买卖交易 |

---

### 5. Technical Analysis API (17个端点)

**文件**: `technical_analysis.py`, `indicators.py`

| 序号 | HTTP方法 | 路径 | 描述 |
|------|----------|------|------|
| 1 | POST | `/api/technical/indicators/trend` | 计算趋势指标 |
| 2 | POST | `/api/technical/indicators/momentum` | 计算动量指标 |
| 3 | POST | `/api/technical/indicators/volatility` | 计算波动性指标 |
| 4 | POST | `/api/technical/indicators/volume` | 计算成交量指标 |
| 5 | POST | `/api/technical/indicators/all` | 计算所有技术指标 |
| 6 | GET | `/api/technical/analysis/signals` | 获取技术分析信号 |
| 7 | GET | `/api/technical/analysis/patterns` | 识别技术形态 |

注：indicators.py的11个端点已在P2 API契约中完成。

---

### 6. Dashboard API (3个端点)

**文件**: `dashboard.py`

| 序号 | HTTP方法 | 路径 | 描述 |
|------|----------|------|------|
| 1 | GET | `/api/dashboard/summary` | 获取仪表盘汇总数据 |
| 2 | GET | `/api/dashboard/market-overview` | 获取市场概览 |
| 3 | GET | `/api/dashboard/health` | 仪表盘健康检查 |

---

### 7. Data API (16个端点)

**文件**: `data.py`

| 序号 | HTTP方法 | 路径 | 描述 |
|------|----------|------|------|
| 1 | GET | `/api/data/stocks/basic` | 获取股票基本信息 |
| 2 | GET | `/api/data/stocks/industries` | 获取股票行业分类 |
| 3 | GET | `/api/data/stocks/concepts` | 获取股票概念分类 |
| 4 | GET | `/api/data/stocks/daily` | 获取股票日线数据 |
| 5 | GET | `/api/data/markets/overview` | 获取市场概览数据 |
| 6 | GET | `/api/data/stocks/search` | 股票搜索功能 |
| 7 | GET | `/api/data/kline` | 获取K线数据 |
| 8 | GET | `/api/data/stocks/kline` | 获取股票K线 |
| 9 | GET | `/api/data/financial` | 获取财务数据 |
| 10 | GET | `/api/data/markets/price-distribution` | 获取价格分布 |
| 11 | GET | `/api/data/markets/hot-industries` | 获取热门行业 |
| 12 | GET | `/api/data/markets/hot-concepts` | 获取热门概念 |
| 13 | GET | `/api/data/stocks/intraday` | 获取日内数据 |
| 14 | GET | `/api/data/stocks/{symbol}/detail` | 获取股票详情 |
| 15 | GET | `/api/data/stocks/{symbol}/trading-summary` | 获取交易汇总 |
| 16 | GET | `/api/data/test/factory` | 测试数据源工厂 |

---

### 8. SSE Endpoints API (5个端点)

**文件**: `endpoints/sse.py`

| 序号 | HTTP方法 | 路径 | 描述 |
|------|----------|------|------|
| 1 | GET | `/sse/training` | 训练进度推送 |
| 2 | GET | `/sse/backtest` | 回测进度推送 |
| 3 | GET | `/sse/alerts` | 告警推送 |
| 4 | GET | `/sse/dashboard` | 仪表盘数据推送 |
| 5 | GET | `/sse/status` | SSE服务状态 |

---

### 9. Task Management API (15个端点)

**文件**: `endpoints/tasks.py`

| 序号 | HTTP方法 | 路径 | 描述 |
|------|----------|------|------|
| 1 | POST | `/api/tasks/register` | 注册任务 |
| 2 | DELETE | `/api/tasks/{task_id}` | 删除任务 |
| 3 | GET | `/api/tasks/` | 获取任务列表 |
| 4 | GET | `/api/tasks/{task_id}` | 获取任务详情 |
| 5 | POST | `/api/tasks/{task_id}/start` | 启动任务 |
| 6 | POST | `/api/tasks/{task_id}/stop` | 停止任务 |
| 7 | GET | `/api/tasks/executions/` | 获取执行记录 |
| 8 | GET | `/api/tasks/executions/{execution_id}` | 获取执行详情 |
| 9 | GET | `/api/tasks/statistics/` | 获取任务统计 |
| 10 | POST | `/api/tasks/import` | 导入任务 |
| 11 | POST | `/api/tasks/export` | 导出任务 |
| 12 | DELETE | `/api/tasks/executions/cleanup` | 清理执行记录 |
| 13 | GET | `/api/tasks/health` | 任务管理健康检查 |
| 14 | GET | `/api/tasks/audit/logs` | 获取审计日志 |
| 15 | POST | `/api/tasks/cleanup/audit` | 清理审计日志 |

---

## 📝 说明

### 优先级分类

- **P0 API**: 核心业务API（47个）- 已在阶段3完成
- **P1 API**: 重要功能API（134个）- 本次扫描范围
- **P2 API**: 辅助功能API（53个）- 已在T4.1完成

### P1 API核心模块

根据TASK.md要求，本次P1 API契约注册将重点创建以下模块的契约：

1. **Backtest API** (14个) - 回测相关
2. **Risk API** (12个) - 风险管理相关
3. **User API** (7个) - 用户管理相关

其他模块（Trade, Technical, Dashboard, Data, SSE, Tasks等）的API将根据时间和优先级逐步补充。

---

**报告版本**: v1.0
**最后更新**: 2025-12-31
**生成者**: Backend CLI (Explore Agent)
