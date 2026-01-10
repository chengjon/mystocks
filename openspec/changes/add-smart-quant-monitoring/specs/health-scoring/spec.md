# 动态健康度评分 - Spec Delta

**能力**: 动态健康度评分 (Dynamic Health Scoring)
**变更ID**: add-smart-quant-monitoring
**状态**: 待审核

---

## ADDED Requirements

### Requirement: 计算股票综合健康度评分

The system MUST calculate comprehensive stock health scores (0-100) based on five dimensions (trend, technical, momentum, volatility, risk) with dynamic weight adjustment based on market regime.

#### Scenario: 计算牛市市场中的股票健康度

**GIVEN** 当前市场体制为 BULL（牛市）
**AND** 股票 "600519.SH" 满足：
  - 趋势评分：85分
  - 技术评分：80分
  - 动量评分：75分
  - 波动评分：90分
  - 风险评分：82分
**WHEN** 用户请求计算该股票健康度
**THEN** 系统使用牛市权重矩阵：
  - trend: 35%, technical: 30%, momentum: 25%, volatility: 5%, risk: 5%
**AND** 综合评分 = 85×0.35 + 80×0.30 + 75×0.25 + 90×0.05 + 82×0.05 = 81.35分
**AND** 返回评分和五维雷达图数据

#### Scenario: 计算熊市市场中的股票健康度

**GIVEN** 当前市场体制为 BEAR（熊市）
**AND** 同一股票的五维评分
**WHEN** 用户请求计算该股票健康度
**THEN** 系统使用熊市权重矩阵：
  - trend: 15%, technical: 20%, momentum: 10%, volatility: 30%, risk: 25%
**AND** 综合评分 = 85×0.15 + 80×0.20 + 75×0.10 + 90×0.30 + 82×0.25 = 83.95分
**AND** 低波动和高风险权重的股票得分更高

#### Scenario: 计算震荡市中的股票健康度

**GIVEN** 当前市场体制为 CHOPPY（震荡）
**AND** 同一股票的五维评分
**WHEN** 用户请求计算该股票健康度
**THEN** 系统使用震荡市权重矩阵：
  - trend: 20%, technical: 35%, momentum: 15%, volatility: 15%, risk: 15%
**AND** 技术指标（超买超卖）权重最高

---

### Requirement: 识别市场体制

The system MUST automatically identify current market regime (bull/bear/choppy) based on index data (Shanghai Composite Index / Shenzhen Component Index).

#### Scenario: 识别牛市市场

**GIVEN** 上证指数最近20个交易日数据：
  - MA斜率：+0.8（强势上涨）
  - 市场广度：0.75（75%股票上涨）
  - 波动率：0.15（低波动）
**WHEN** 系统执行市场体制识别
**THEN** 综合评分 = 0.8×0.4 + 0.75×0.3 + (1-0.15)×0.3 = 0.785
**AND** 评分 > 0.6，识别为 BULL 市场
**AND** 返回市场体制和置信度

#### Scenario: 识别熊市市场

**GIVEN** 上证指数最近20个交易日数据：
  - MA斜率：-0.6（下跌）
  - 市场广度：0.25（25%股票上涨）
  - 波动率：0.35（高波动）
**WHEN** 系统执行市场体制识别
**THEN** 综合评分 = -0.6×0.4 + 0.25×0.3 + (1-0.35)×0.3 = 0.045
**AND** 评分 < 0.4，识别为 BEAR 市场

#### Scenario: 识别震荡市场

**GIVEN** 上证指数最近20个交易日数据：
  - MA斜率：+0.1（横盘）
  - 市场广度：0.52（涨跌互现）
  - 波动率：0.20（中等波动）
**WHEN** 系统执行市场体制识别
**THEN** 综合评分 = 0.1×0.4 + 0.52×0.3 + (1-0.20)×0.3 = 0.416
**AND** 0.4 ≤ 评分 ≤ 0.6，识别为 CHOPPY 市场

---

### Requirement: 计算高级风险指标

The system MUST calculate quantitative professional advanced risk metrics: Sortino ratio, Calmar ratio, maximum drawdown duration, downside deviation.

#### Scenario: 计算Sortino比率

**GIVEN** 股票 "600519.SH" 最近1年日收益率数据
**WHEN** 系统计算Sortino比率
**THEN** 系统执行：
  1. 计算下行偏差（仅考虑负收益率）
  2. Sortino = (年化收益率 - 无风险利率) / 下行标准差
**AND** 返回 Sortino比率（如：1.45）

#### Scenario: 计算Calmar比率

**GIVEN** 股票 "600519.SH" 最近3年数据
**WHEN** 系统计算Calmar比率
**THEN** 系统执行：
  1. 计算年化收益率
  2. 计算最大回撤
  3. Calmar = 年化收益率 / abs(最大回撤)
**AND** 返回 Calmar比率（如：2.3）

#### Scenario: 计算最大回撤持续期

**GIVEN** 股票 "600519.SH" 价格历史数据
**WHEN** 系统计算最大回撤持续期
**THEN** 系统执行：
  1. 识别最大回撤区间
  2. 计算从回撤开始到恢复前高的天数
**AND** 返回持续天数（如：15天）

#### Scenario: 计算下行标准差

**GIVEN** 股票 "600519.SH" 最近1年日收益率数据
**WHEN** 系统计算下行标准差
**THEN** 系统执行：
  1. 筛选负收益率样本
  2. 计算这些样本的标准差
**AND** 返回下行标准差（如：0.08）

---

### Requirement: 异步批量保存健康度评分

The system MUST asynchronously batch save health scores to database via event bus to avoid blocking API responses.

#### Scenario: 计算完成后异步保存评分

**GIVEN** 用户请求计算100只股票的健康度
**WHEN** 计算引擎完成计算（耗时200ms）
**THEN** API立即返回结果给用户（不等待写库）
**AND** 系统发布 `metric_update` 事件到Redis
**AND** 后台Worker批量写入数据库（50条/批次）

#### Scenario: Worker消费事件并批量写入

**GIVEN** Redis队列中有100条 `metric_update` 事件
**WHEN** MonitoringEventWorker 轮询队列
**THEN** Worker批量拉取50条事件
**AND** 调用 `postgres_async.batch_save_health_scores()`
**AND** 写入成功后清空缓冲区
**AND** 继续处理剩余50条事件

---

### Requirement: 查询健康度历史曲线

The system MUST support querying historical health scores for stocks to enable trend analysis.

#### Scenario: 查询最近30天健康度历史

**GIVEN** 股票 "600519.SH" 有最近30天的评分记录
**WHEN** 用户发送 GET 请求到 `/api/v1/monitoring/analysis/results/600519.SH?start_date=2025-12-08&end_date=2026-01-07`
**THEN** 系统返回 200 OK
**AND** 响应体包含30条记录，每条包含：
  - score_date, total_score, radar_scores, market_regime

#### Scenario: 查询日期范围无数据

**GIVEN** 股票 "000001.SZ" 在指定日期范围无评分记录
**WHEN** 用户查询该股票健康度历史
**THEN** 系统返回 200 OK
**AND** 响应体为空数组 `[]`

---

### Requirement: 实时计算并立即返回结果

The system MUST support real-time health score calculation with API response time <500ms (P95).

#### Scenario: 实时计算50只股票健康度

**GIVEN** 用户的清单包含50只股票
**WHEN** 用户发送 POST 请求到 `/api/v1/monitoring/analysis/calculate?watchlist_id=1`
**THEN** 系统执行：
  1. 从数据库获取清单成员（10ms）
  2. 识别市场体制（20ms）
  3. 调用计算引擎（CPU模式，200ms）
  4. 立即返回结果（不等待写库）
**AND** API总响应时间 <250ms
**AND** 事件异步发布到Redis

#### Scenario: 大规模计算触发GPU模式

**GIVEN** 用户的清单包含500只股票
**WHEN** 用户请求计算健康度
**THEN** 系统自动选择GPU计算引擎
**AND** 计算耗时 <1秒
**AND** API总响应时间 <1.2秒

---

## MODIFIED Requirements

*无修改现有需求*

---

## REMOVED Requirements

*无删除现有需求*

---

## Cross-References

- **依赖**: `calculation-engine` - 计算引擎提供评分算法
- **依赖**: `watchlist-management` - 清单数据作为计算输入
- **关联**: `portfolio-optimization` - 健康度评分用于组合优化

---

## 数据模型

### monitoring_health_scores 表

```sql
CREATE TABLE monitoring_health_scores (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    score_date DATE NOT NULL,

    -- 综合评分
    total_score DECIMAL(5,2),

    -- 五维雷达分 (JSONB存储)
    radar_scores JSONB,  -- {trend: 80, technical: 70, momentum: 60, volatility: 50, risk: 90}

    -- 高级风险指标
    sortino_ratio DECIMAL(10,4),
    calmar_ratio DECIMAL(10,4),
    max_drawdown DECIMAL(5,4),
    max_drawdown_duration INTEGER,
    downside_deviation DECIMAL(10,4),

    -- 市场环境快照
    market_regime VARCHAR(20),  -- 'bull', 'bear', 'choppy'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, score_date)
);
```

---

## 性能要求

- API响应时间 <500ms (P95)
- CPU模式：100只股票 <5秒
- GPU模式：1000只股票 <2秒
- 事件写入成功率 >99%

---

**状态**: 待审核
**版本**: v1.0
