# 08 风险监控中心 (Risk Center)

## 1. 页面概览
**功能定位**: 系统的安全气囊。全天候监控账户风控指标、系统运行状态及合规性。
**视觉焦点**: 醒目的状态指示灯与报警日志流。

## 2. 布局结构

### 2.1 风险仪表盘 (Risk Dashboard - Top)
*   **组件**: `RiskGauge`
*   **指标**:
    *   **VaR (在险价值)**: 95% 置信度下的预期最大单日亏损。
    *   **仓位集中度**: 单一个股/行业最大持仓占比。
    *   **杠杆率**: 当前账户实际杠杆 (如有融资).
    *   **流动性评分**: 持仓变现的难易程度。
*   **API**: `GET /api/v1/risk/metrics` (假设存在，或由 monitoring 提供)

### 2.2 预警规则配置 (Alert Rules - Middle Left)
*   **组件**: `RuleManager`
*   **功能**:
    *   设置价格预警 (突破/跌破)。
    *   设置止损止盈预警 (跌幅>X%)。
    *   设置系统预警 (行情延迟>3s, 接口报错)。
*   **API**: `GET/POST /api/v1/monitoring/alert-rules`

### 2.3 预警日志流 (Alert Log - Middle Right)
*   **组件**: `AlertHistory`
*   **内容**:
    *   历史触发的所有预警记录。
    *   支持按 严重程度 (Info/Warning/Critical) 筛选。
*   **API**: `GET /api/v1/monitoring/alerts`

### 2.4 系统健康状态 (System Health - Bottom)
*   **组件**: `ServiceStatus`
*   **监控项**:
    *   **行情源**: 延迟 (ms), 丢包率.
    *   **数据库**: TDengine 写入速度, PostgreSQL 连接数.
    *   **API服务**: 响应时间, 错误率 (5xx).
*   **API**: `GET /api/v1/system/status` (假设存在)

## 3. 交互设计
*   **通知测试**: 提供按钮发送测试通知 (邮件/微信/钉钉)，验证触达链路。
*   **一键熔断**: 紧急按钮 "停止所有策略交易"，用于极端行情或系统故障。

## 4. API 映射汇总
| 组件区域 | 核心 API 端点 | 请求方式 | 备注 |
| :--- | :--- | :--- | :--- |
| 预警规则 | `/api/v1/monitoring/alert-rules` | GET/POST | |
| 预警记录 | `/api/v1/monitoring/alerts` | GET | |
| 实时状态 | `/api/v1/monitoring/realtime` | WS | |
