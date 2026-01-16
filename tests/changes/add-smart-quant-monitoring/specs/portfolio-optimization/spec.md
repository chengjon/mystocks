# 投资组合优化 - Spec Delta

**能力**: 投资组合优化 (Portfolio Optimization)
**变更ID**: add-smart-quant-monitoring
**状态**: 待审核

---

## ADDED Requirements

### Requirement: 组合整体健康度分析

The system MUST analyze overall portfolio health including weighted average scores, risk distribution, and industry concentration.

#### Scenario: 计算组合加权平均健康度

**GIVEN** 用户清单包含5只股票：
  - 贵州茅台（权重30%）：健康度85分
  - 腾讯控股（权重25%）：健康度82分
  - 阿里巴巴（权重20%）：健康度78分
  - 平安银行（权重15%）：健康度75分
  - 招商银行（权重10%）：健康度80分
**WHEN** 用户请求组合分析
**THEN** 系统计算加权平均健康度：
  ```
  组合健康度 = 85×0.30 + 82×0.25 + 78×0.20 + 75×0.15 + 80×0.10 = 80.95分
  ```
**AND** 返回组合整体评分和风险分布

#### Scenario: 分析组合风险分布

**GIVEN** 用户清单包含10只股票
**WHEN** 用户请求组合风险分析
**THEN** 系统计算：
  - 高风险股票（风险评分<60分）：2只（占比20%）
  - 中风险股票（60-80分）：5只（占比50%）
  - 低风险股票（>80分）：3只（占比30%）
**AND** 生成风险分布饼图数据

#### Scenario: 分析行业集中度

**GIVEN** 用户清单包含股票行业分布：
  - 金融：4只股票（权重60%）
  - 科技：3只股票（权重30%）
  - 消费：2只股票（权重10%）
**WHEN** 用户请求行业集中度分析
**THEN** 系统检测金融行业占比 >50%
**AND** 返回警告："行业集中度过高，建议分散投资"

---

### Requirement: 个股详情和排序

The system MUST display detailed information for each stock in the portfolio with sorting support by health score, return rate, and other dimensions.

#### Scenario: 展示个股详情列表

**GIVEN** 用户清单包含10只股票
**WHEN** 用户请求组合分析
**THEN** 系统返回每只股票的详情：
  - stock_code, stock_name
  - weight, entry_price, current_price
  - total_score, radar_scores
  - profit_loss_amount, profit_loss_percent
  - stop_loss_price, target_price
  - 优先级建议（1=高优先，2=中优先，3=低优先）

#### Scenario: 按健康度降序排序

**GIVEN** 用户清单包含10只股票
**WHEN** 用户请求按健康度排序
**THEN** 系统返回排序后的列表：
  1. 贵州茅台：85分
  2. 腾讯控股：82分
  3. 阿里巴巴：78分
  ...
**AND** 最低健康度股票排在最后（需要关注）

#### Scenario: 按收益率降序排序

**GIVEN** 用户清单包含10只股票
**WHEN** 用户请求按收益率排序
**THEN** 系统计算每只股票收益率：
  ```
  收益率 = (current_price - entry_price) / entry_price
  ```
**AND** 按收益率降序返回列表
**AND** 盈利最多的股票排在前面

---

### Requirement: 再平衡建议（REBALANCE/HOLD）

The system MUST provide rebalancing recommendations (REBALANCE or HOLD) based on health scores and return rate changes.

#### Scenario: 推荐REBALANCE（高优先级）

**GIVEN** 股票 "600519.SH"：
  - 健康度评分：55分（低于60分阈值）
  - 当前收益率：-15%（亏损）
  - 入库理由：macd_gold_cross
**WHEN** 系统生成再平衡建议
**THEN** 系统推荐：REBALANCE（高优先级）
**AND** 理由："健康度评分低于60分，且亏损15%，建议调仓"
**AND** 建议操作：
  - 止损：价格已跌破止损价-5%
  - 或减仓：降低权重从20% → 10%

#### Scenario: 推荐HOLD（低风险）

**GIVEN** 股票 "000001.SZ"：
  - 健康度评分：85分（高于80分阈值）
  - 当前收益率：+25%（盈利）
  - 入库理由：manual_pick
**WHEN** 系统生成再平衡建议
**THEN** 系统推荐：HOLD
**AND** 理由："健康度评分优秀，且盈利良好，建议持有"
**AND** 无需操作

#### Scenario: 推荐REBALANCE（触发止盈）

**GIVEN** 股票 "000002.SZ"：
  - 健康度评分：70分（中等）
  - 当前收益率：+45%（超过止盈价+10%）
  - target_price: 100元，current_price: 110元
**WHEN** 系统生成再平衡建议
**THEN** 系统推荐：REBALANCE（中优先级）
**AND** 理由："价格已超过止盈价10%，建议部分止盈"
**AND** 建议操作：
  - 卖出30%仓位锁定利润
  - 或上调止损价至成本价

#### Scenario: 推荐HOLD（再平衡阈值未触发）

**GIVEN** 股票 "600000.SH"：
  - 健康度评分：75分（中等）
  - 当前收益率：+5%（小幅盈利）
  - 权重：15%，目标权重：15%
**WHEN** 系统生成再平衡建议
**THEN** 系统推荐：HOLD
**AND** 理由："权重平衡，健康度中等，建议继续持有观察"
**AND** 再平衡阈值（5%）未触发

---

### Requirement: 风险预警（止损/止盈）

The system MUST monitor price movements of stocks in watchlists and trigger timely alerts when stop loss or take profit conditions are met.

#### Scenario: 触发止损预警

**GIVEN** 股票 "600519.SH"：
  - entry_price: 1850元
  - stop_loss_price: 1750元（止损线-5.4%）
  - current_price: 1730元（跌破止损价）
**WHEN** 系统执行风险检查
**THEN** 系统生成🔴止损预警：
  ```
  警告级别：🔴 紧急
  股票：600519.SH 贵州茅台
  当前价格：1730元，跌破止损价1750元
  亏损幅度：-6.5%
  建议：立即止损或大幅减仓
  ```
**AND** 预警标记为高优先级

#### Scenario: 触发止盈预警

**GIVEN** 股票 "000001.SZ"：
  - entry_price: 10元
  - target_price: 15元（止盈目标+50%）
  - current_price: 16元（超过止盈价）
**WHEN** 系统执行风险检查
**THEN** 系统生成🟢止盈预警：
  ```
  警告级别：🟢 提示
  股票：000001.SZ 平安银行
  当前价格：16元，超过止盈价15元
  盈利幅度：+60%
  建议：部分止盈锁定利润
  ```

#### Scenario: 接近止损线（提前预警）

**GIVEN** 股票 "000002.SZ"：
  - entry_price: 20元
  - stop_loss_price: 18元（止损线-10%）
  - current_price: 18.5元（接近止损线，跌幅-7.5%）
**WHEN** 系统执行风险检查
**THEN** 系统生成🟡接近止损预警：
  ```
  警告级别：🟡 提醒
  股票：000002.SZ 万科A
  当前价格：18.5元，接近止损价18元（仅差2.8%）
  亏损幅度：-7.5%
  建议：密切关注，考虑减仓
  ```

---

### Requirement: 约束优化算法

The system MUST provide constrained optimization algorithms that consider transaction costs and rebalancing thresholds to generate optimal weight configurations.

#### Scenario: 考虑交易成本的权重优化

**GIVEN** 用户清单包含5只股票
**AND** 当前权重配置：[30%, 25%, 20%, 15%, 10%]
**AND** 基于健康度的理想权重：[35%, 30%, 15%, 10%, 10%]
**AND** 交易成本：0.3%（双向）
**WHEN** 系统执行权重优化
**THEN** 系统计算净收益：
  ```
  预期收益提升 = 理想权重预期收益 - 当前权重预期收益 = 2.5%
  交易成本 = 0.3%
  净收益 = 2.5% - 0.3% = 2.2%
  ```
**AND** 净收益 > 0，推荐再平衡
**AND** 返回最优权重配置

#### Scenario: 再平衡阈值过滤（避免频繁交易）

**GIVEN** 用户清单包含5只股票
**AND** 当前权重：[30%, 25%, 20%, 15%, 10%]
**AND** 理想权重：[31%, 25%, 19%, 15%, 10%]
**AND** 再平衡阈值：5%
**WHEN** 系统执行权重优化
**THEN** 系统计算权重变化：
  - 股票1：30% → 31%（变化1%）
  - 股票2：25% → 25%（变化0%）
  - 股票3：20% → 19%（变化1%）
**AND** 所有变化 < 5%阈值
**AND** 系统推荐：HOLD（无需再平衡）
**AND** 理由："权重变化小于再平衡阈值5%，避免过度交易"

#### Scenario: 行业集中度约束

**GIVEN** 用户清单包含10只股票
**AND** 当前行业分布：
  - 金融：60%（超过集中度上限50%）
**WHEN** 系统执行权重优化
**AND** 启用行业集中度约束（≤50%）
**THEN** 系统调整权重：
  - 金融：60% → 50%（降低10%）
  - 科技：20% → 30%（增加10%）
  - 消费：20% → 20%（保持）
**AND** 满足行业集中度约束
**AND** 返回调整后的权重配置

---

## MODIFIED Requirements

*无修改现有需求*

---

## REMOVED Requirements

*无删除现有需求*

---

## Cross-References

- **依赖**: `health-scoring` - 健康度评分作为优化输入
- **依赖**: `watchlist-management` - 清单和权重作为优化对象
- **关联**: `calculation-engine` - 计算引擎提供评分和风险指标

---

## 数据模型

### 组合分析响应

```json
{
  "watchlist_id": 1,
  "watchlist_name": "核心科技股",
  "portfolio_health_score": 80.95,
  "risk_distribution": {
    "high_risk": 2,
    "medium_risk": 5,
    "low_risk": 3
  },
  "industry_concentration": {
    "warning": "金融行业占比过高(60%)",
    "distribution": {
      "金融": 60,
      "科技": 30,
      "消费": 10
    }
  },
  "stocks": [
    {
      "stock_code": "600519.SH",
      "stock_name": "贵州茅台",
      "weight": 0.30,
      "entry_price": 1850.00,
      "current_price": 1875.00,
      "total_score": 85,
      "radar_scores": {
        "trend": 88,
        "technical": 85,
        "momentum": 82,
        "volatility": 90,
        "risk": 80
      },
      "profit_loss_amount": 25.00,
      "profit_loss_percent": 0.0135,
      "recommendation": "HOLD",
      "priority": 3
    }
  ],
  "rebalance_suggestions": [
    {
      "stock_code": "000001.SZ",
      "action": "REBALANCE",
      "priority": 1,
      "reason": "健康度评分低于60分，且亏损15%",
      "suggestion": "止损或减仓"
    }
  ],
  "risk_alerts": [
    {
      "stock_code": "600519.SH",
      "alert_type": "stop_loss",
      "severity": "high",
      "message": "当前价格1730元，跌破止损价1750元"
    }
  ]
}
```

---

## 性能要求

- 组合分析响应时间 <500ms (P95)
- 权重优化计算时间 <2秒（10只股票）
- 风险预警实时监控（每次计算时触发）

---

**状态**: 待审核
**版本**: v1.0
