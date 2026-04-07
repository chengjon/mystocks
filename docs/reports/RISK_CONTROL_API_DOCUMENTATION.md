# A股风险控制API文档

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## 概述

这是一个**复用主项目风险指标计算模块**的REST API服务器，提供专业的量化交易风险分析和控制服务。

**特点**:
- ✅ 复用主项目RiskMetrics类（13种专业风险指标）
- ✅ 仓位风险评估（集中度、行业分布）
- ✅ 实时风险告警（回撤超限、单日亏损）
- ✅ 智能风控建议（减仓、平仓、暂停新开仓）
- ✅ Herfindahl指数计算（持仓集中度）
- ✅ 备用实现（主模块不可用时自动降级）

**服务器地址**: `http://localhost:8003`

**API文档**: `http://localhost:8003/docs` (Swagger UI)

---

## 快速开始

### 1. 安装依赖

```bash
cd /tmp/a-stock-risk-api
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python3 risk_control_api_server.py
```

输出示例:
```
======================================================================
🛡️  A股风险控制API服务器
======================================================================
📡 API地址: http://localhost:8003
🏥 健康检查: http://localhost:8003/health
📚 API文档: http://localhost:8003/docs
🎯 风险指标: ✅ 主模块已加载  或  ⚠️  使用备用实现
======================================================================
```

### 3. 测试API

```bash
# 健康检查
curl http://localhost:8003/health

# 计算风险指标
curl -X POST http://localhost:8003/api/risk/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "equity_curve": [100000, 102000, 101000, 103000, 105000],
    "returns": [0.02, -0.01, 0.02, 0.02],
    "total_return": 0.05,
    "max_drawdown": -0.02
  }'
```

---

## API端点

### 1. 根路径 - 服务信息

**请求**:
```http
GET /
```

**响应**:
```json
{
  "service": "A股风险控制API",
  "version": "1.0.0",
  "risk_metrics_available": true,
  "endpoints": {
    "POST /api/risk/metrics": "计算风险指标",
    "POST /api/risk/position": "评估仓位风险",
    "POST /api/risk/alerts": "生成风险告警",
    "GET /api/risk/alerts/list": "列出所有告警",
    "GET /health": "健康检查"
  }
}
```

---

### 2. 健康检查

**请求**:
```http
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-26T11:44:42.224883",
  "risk_metrics_available": true,
  "active_alerts": 0
}
```

---

### 3. 计算风险指标

**请求**:
```http
POST /api/risk/metrics
Content-Type: application/json
```

**请求体**:
```json
{
  "equity_curve": [100000, 102000, 101000, 103000, 105000, 104000, 106000, 108000, 107000, 110000],
  "returns": [0.02, -0.01, 0.02, 0.02, -0.01, 0.02, 0.02, -0.01, 0.03],
  "trades": [],
  "total_return": 0.10,
  "max_drawdown": -0.02,
  "risk_free_rate": 0.03
}
```

**参数说明**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `equity_curve` | float[] | ✅ | 权益曲线数据（每个时间点的总资产） |
| `returns` | float[] | ✅ | 收益率序列（日收益率） |
| `trades` | Dict[] | ❌ | 交易记录列表（用于计算交易风险） |
| `total_return` | float | ✅ | 总收益率 |
| `max_drawdown` | float | ✅ | 最大回撤（负数） |
| `risk_free_rate` | float | ❌ | 无风险利率，默认0.0 |

**响应**:
```json
{
  "status": "success",
  "metrics": {
    "downside_deviation": 0.0,
    "ulcer_index": 0.522,
    "pain_index": 0.0029,
    "skewness": -0.565,
    "kurtosis": -1.444,
    "tail_ratio": 2.6,
    "omega_ratio": 4.333,
    "burke_ratio": 890.619,
    "recovery_factor": -5.0
  },
  "calculated_at": "2025-12-26T11:44:46.416633"
}
```

**风险指标说明**:

| 指标 | 说明 | 优秀值 |
|------|------|--------|
| `downside_deviation` | 下行偏差（仅考虑负收益波动） | < 10% |
| `ulcer_index` | 溃疡指数（回撤深度和持续时间） | < 5 |
| `pain_index` | 痛苦指数（平均回撤深度） | < 5% |
| `skewness` | 偏度（收益分布不对称性） | > 0（右偏） |
| `kurtosis` | 峰度（收益分布尖峭程度） | < 3（平坦） |
| `tail_ratio` | 尾部比率（95分位/5分位） | > 1 |
| `omega_ratio` | Omega比率（收益/损失比） | > 1 |
| `burke_ratio` | Burke比率（超额收益/回撤） | > 1 |
| `recovery_factor` | 恢复因子（总收益/最大回撤） | > 2 |

**如果有交易记录，还会计算**:
- `payoff_ratio` - 盈亏比（平均盈利/平均亏损）
- `trade_expectancy` - 交易期望值
- `max_consecutive_losses` - 最大连续亏损次数
- `max_consecutive_loss_amount` - 最大连续亏损金额

---

### 4. 评估仓位风险

**请求**:
```http
POST /api/risk/position
Content-Type: application/json
```

**请求体**:
```json
{
  "positions": [
    {"symbol": "sh600000", "value": 150000, "sector": "金融"},
    {"symbol": "sh600036", "value": 120000, "sector": "金融"},
    {"symbol": "sh600519", "value": 80000, "sector": "消费"}
  ],
  "total_capital": 1000000,
  "config": {
    "max_position_size": 0.10,
    "daily_loss_limit": 0.05
  }
}
```

**参数说明**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `positions` | Dict[] | ✅ | 持仓列表，每个包含symbol, value, sector |
| `total_capital` | float | ✅ | 总资金 |
| `config.max_position_size` | float | ❌ | 单股最大仓位（默认0.10） |
| `config.daily_loss_limit` | float | ❌ | 单日亏损限制（默认0.05） |
| `config.max_drawdown_threshold` | float | ❌ | 最大回撤阈值（默认0.30） |
| `config.stop_loss_pct` | float | ❌ | 止损百分比（可选） |
| `config.take_profit_pct` | float | ❌ | 止盈百分比（可选） |

**响应**:
```json
{
  "status": "success",
  "risk_assessment": {
    "total_position_value": 350000,
    "total_market_value": 350000,
    "position_ratio": 0.35,
    "cash_ratio": 0.65,
    "position_concentration": [
      {
        "symbol": "sh600000",
        "concentration": 0.15,
        "exceeds_limit": true
      },
      {
        "symbol": "sh600036",
        "concentration": 0.12,
        "exceeds_limit": true
      },
      {
        "symbol": "sh600519",
        "concentration": 0.08,
        "exceeds_limit": false
      }
    ],
    "exceeded_positions": [
      {
        "symbol": "sh600000",
        "concentration": 0.15,
        "exceeds_limit": true
      },
      {
        "symbol": "sh600036",
        "concentration": 0.12,
        "exceeds_limit": true
      }
    ],
    "high_concentration_risk": true,
    "sector_concentration": {
      "金融": 0.27,
      "消费": 0.08
    },
    "herfindahl_index": 0.0433,
    "risk_level": "HIGH"
  },
  "assessed_at": "2025-12-26T11:44:51.179286"
}
```

**风险评估指标说明**:

| 指标 | 说明 | 判断标准 |
|------|------|---------|
| `position_ratio` | 仓位占比（已用资金/总资金） | < 80%为宜 |
| `cash_ratio` | 现金比例（现金/总资金） | > 20%为宜 |
| `position_concentration` | 个股集中度（个股市值/总资金） | 不应超过max_position_size |
| `sector_concentration` | 行业集中度（行业市值/总资金） | 单行业 < 40%为宜 |
| `herfindahl_index` | Herfindahl指数（持仓集中度） | < 0.25低风险, 0.25-0.5中风险, > 0.5高风险 |
| `risk_level` | 风险等级（LOW/MEDIUM/HIGH） | 综合评估 |

---

### 5. 生成风险告警

**请求**:
```http
POST /api/risk/alerts
Content-Type: application/json
```

**请求体**:
```json
{
  "current_drawdown": -0.25,
  "daily_pnl": -60000,
  "total_capital": 1000000,
  "config": {
    "max_drawdown_threshold": 0.30,
    "daily_loss_limit": 0.05
  }
}
```

**参数说明**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `current_drawdown` | float | ✅ | 当前回撤（负数） |
| `daily_pnl` | float | ✅ | 当日盈亏（负数表示亏损） |
| `total_capital` | float | ✅ | 总资金 |
| `config.max_drawdown_threshold` | float | ❌ | 最大回撤阈值（默认0.30） |
| `config.daily_loss_limit` | float | ❌ | 单日亏损限制（默认0.05） |

**响应**:
```json
{
  "status": "success",
  "alert_id": "alert_20251226_114454_1",
  "alerts": [
    {
      "type": "daily_loss_limit_exceeded",
      "severity": "WARNING",
      "message": "单日亏损超限: -6.00% < -5.00%",
      "timestamp": "2025-12-26T11:44:54.735857",
      "suggestion": "暂停新开仓，评估当前持仓风险"
    }
  ],
  "alert_count": 1,
  "created_at": "2025-12-26T11:44:54.735907"
}
```

**告警类型说明**:

| 告警类型 | 严重程度 | 触发条件 | 建议 |
|---------|---------|---------|------|
| `max_drawdown_exceeded` | CRITICAL | 回撤 > max_drawdown_threshold | 立即减仓或平仓，控制风险敞口 |
| `daily_loss_limit_exceeded` | WARNING | 单日亏损 < -daily_loss_limit | 暂停新开仓，评估当前持仓风险 |

---

### 6. 列出所有告警

**请求**:
```http
GET /api/risk/alerts/list
```

**响应**:
```json
{
  "total": 1,
  "active": 1,
  "items": [
    {
      "alert_id": "alert_20251226_114454_1",
      "created_at": "2025-12-26T11:44:54.735902",
      "active": true,
      "alert_count": 1
    }
  ]
}
```

---

## 使用示例

### Python示例

```python
import requests

API_BASE = "http://localhost:8003"

# 1. 计算风险指标
response = requests.post(f"{API_BASE}/api/risk/metrics", json={
    "equity_curve": [100000, 102000, 101000, 103000, 105000],
    "returns": [0.02, -0.01, 0.02, 0.02],
    "total_return": 0.05,
    "max_drawdown": -0.02
})

metrics = response.json()["metrics"]
print(f"溃疡指数: {metrics['ulcer_index']:.3f}")
print(f"夏普比率: {metrics.get('sharpe_ratio', 'N/A')}")
print(f"下行偏差: {metrics['downside_deviation']:.2%}")

# 2. 评估仓位风险
response = requests.post(f"{API_BASE}/api/risk/position", json={
    "positions": [
        {"symbol": "sh600000", "value": 150000, "sector": "金融"},
        {"symbol": "sh600036", "value": 120000, "sector": "金融"}
    ],
    "total_capital": 1000000,
    "config": {"max_position_size": 0.10}
})

assessment = response.json()["risk_assessment"]
print(f"风险等级: {assessment['risk_level']}")
print(f"仓位占比: {assessment['position_ratio']:.2%}")
print(f"Herfindahl指数: {assessment['herfindahl_index']:.3f}")

if assessment["high_concentration_risk"]:
    print("⚠️  警告：发现超限仓位！")
    for pos in assessment["exceeded_positions"]:
        print(f"  - {pos['symbol']}: {pos['concentration']:.2%}")

# 3. 生成风险告警
response = requests.post(f"{API_BASE}/api/risk/alerts", json={
    "current_drawdown": -0.25,
    "daily_pnl": -60000,
    "total_capital": 1000000
})

result = response.json()
if result["alert_count"] > 0:
    print(f"🚨 触发 {result['alert_count']} 个告警：")
    for alert in result["alerts"]:
        print(f"  [{alert['severity']}] {alert['message']}")
        print(f"  建议: {alert['suggestion']}")
```

### JavaScript示例

```javascript
const API_BASE = 'http://localhost:8003';

async function checkRisk() {
  // 1. 计算风险指标
  const metricsResponse = await fetch(`${API_BASE}/api/risk/metrics`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      equity_curve: [100000, 102000, 101000, 103000, 105000],
      returns: [0.02, -0.01, 0.02, 0.02],
      total_return: 0.05,
      max_drawdown: -0.02
    })
  });

  const metricsData = await metricsResponse.json();
  const metrics = metricsData.metrics;

  console.log('溃疡指数:', metrics.ulcer_index.toFixed(3));
  console.log('痛苦指数:', (metrics.pain_index * 100).toFixed(2) + '%');
  console.log('偏度:', metrics.skewness.toFixed(3));

  // 2. 评估仓位风险
  const positionResponse = await fetch(`${API_BASE}/api/risk/position`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      positions: [
        {symbol: 'sh600000', value: 150000, sector: '金融'},
        {symbol: 'sh600036', value: 120000, sector: '金融'}
      ],
      total_capital: 1000000,
      config: {max_position_size: 0.10}
    })
  });

  const assessmentData = await positionResponse.json();
  const assessment = assessmentData.risk_assessment;

  console.log('风险等级:', assessment.risk_level);
  console.log('仓位占比:', (assessment.position_ratio * 100).toFixed(2) + '%');

  if (assessment.high_concentration_risk) {
    console.log('⚠️  警告：发现超限仓位！');
    assessment.exceeded_positions.forEach(pos => {
      console.log(`  - ${pos.symbol}: ${(pos.concentration * 100).toFixed(2)}%`);
    });
  }
}

checkRisk();
```

---

## 风险控制最佳实践

### 1. 仓位管理

- **单股仓位限制**: 不超过总资金的10-15%
- **行业集中度**: 单行业不超过30-40%
- **总仓位控制**: 保持20-30%现金储备
- **Herfindahl指数**: < 0.25表示持仓分散

### 2. 风险监控

- **每日检查**: 监控单日盈亏，超过-5%立即评估
- **回撤控制**: 最大回撤不应超过-20%到-30%
- **波动率监控**: 下行偏差应控制在10%以内
- **连续亏损**: 超过3-5次连续亏损应暂停交易

### 3. 告警响应

**CRITICAL级别**（立即行动）:
- 最大回撤超限
- 建议立即减仓50%或完全平仓
- 重新评估策略有效性

**WARNING级别**（谨慎操作）:
- 单日亏损超限
- 暂停新开仓
- 检查持仓集中度
- 评估是否需要止损

### 4. 指标解读

**优秀策略表现**:
- 夏普比率 > 1.5
- 溃疡指数 < 5
- 恢复因子 > 2
- 盈亏比 > 2
- Omega比率 > 1.5

**风险过高信号**:
- 溃疡指数 > 10
- 痛苦指数 > 10%
- 下行偏差 > 15%
- Herfindahl指数 > 0.5
- 连续亏损 > 5次

---

## 主项目模块复用

本API成功复用主项目的`RiskMetrics`类:
- **源文件**: `/opt/claude/mystocks_spec/src/ml_strategy/backtest/risk_metrics.py`
- **导入状态**: ✅ 已加载
- **复用方法**:
  ```python
  from src.ml_strategy.backtest.risk_metrics import RiskMetrics
  risk_calculator = RiskMetrics()
  metrics = risk_calculator.calculate_all_risk_metrics(...)
  ```

**备用实现**:
- 当主项目模块不可用时，自动使用内置的简化实现
- 确保API始终可用
- 指标计算略有差异但核心逻辑一致

---

## 注意事项

1. **数据准确性**: 权益曲线和收益率数据必须准确且对应
2. **交易记录**: 交易记录需包含pnl字段用于计算交易风险
3. **实时性**: 风险告警基于实时数据，需定期调用检查
4. **阈值设定**: 风险阈值应根据策略特性动态调整
5. **综合判断**: 不要依赖单一指标，应综合评估所有风险因素

---

## 下一步开发

计划中的功能:
- [ ] 风险仪表板（可视化展示）
- [ ] 历史风险趋势分析
- [ ] 压力测试功能
- [ ] VaR（在险价值）计算
- [ ] 相关性风险分析
- [ ] 动态止损止盈调整
- [ ] 风险归因分析

---

**创建时间**: 2025-12-26 11:44
**版本**: v1.0
**文件**: /tmp/a-stock-risk-api/risk_control_api_server.py
**文档**: /tmp/RISK_CONTROL_API_DOCUMENTATION.md
