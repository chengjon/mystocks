# MyStocks 数据源扩展计划 - 基于量化交易价值原则

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## 🎯 核心原则：高价值数据驱动

基于您的专业意见，我们重新梳理数据源扩展计划。核心原则是**围绕能产生显著alpha（超额收益）、控制风险、或解锁新策略的"高价值数据"**。

## 🔥 P0级 - 必须立即补充 (量化交易核心数据)

### 1. **融资融券数据** ⭐⭐⭐⭐⭐

**战略价值**: A股独有的市场情绪和杠杆资金风向标

**具体实现**:
```yaml
# 数据源配置扩展
margin_trading_balance:    # 融资融券余额
  endpoint_name: margin_trading_balance
  source_name: tushare
  data_category: LEVERAGE_DATA
  parameters:
    - symbol: 股票代码
    - start_date: 开始日期
    - end_date: 结束日期
  target_db: postgresql
  table_name: margin_trading_data

margin_buy_sell_detail:    # 融资买入/融券卖出明细
margin_liability_change:   # 融资融券负债变化
```

**量化应用**:
- **反转因子**: `融资余额占比 = 融资余额 / 流通市值`
- **杠杆风险**: `融资买入比 = 融资买入额 / 总成交额`
- **情绪指标**: `融资偿还率 = 融资偿还额 / 融资余额`

### 2. **龙虎榜数据 (含大宗交易)** ⭐⭐⭐⭐⭐

**战略价值**: 观察机构资金和顶级游资动向的唯一公开窗口

**具体实现**:
```yaml
dragon_tiger_list:         # 龙虎榜单
  endpoint_name: dragon_tiger_list
  source_name: akshare
  data_category: INSTITUTIONAL_DATA
  parameters:
    - date: 交易日期
    - market: 市场类型
  target_db: postgresql
  table_name: dragon_tiger_data

institutional_trading:     # 机构买卖明细
block_trading:             # 大宗交易数据
```

**量化应用**:
- **席位联动策略**: 跟踪知名游资营业部的净买入额
- **机构占比因子**: `机构专用席位占比 = 机构席位买入额 / 总买入额`
- **大宗折溢价**: `折溢价率 = 成交价 / 收盘价 - 1`

### 3. **股指期货数据 (IH、IF、IC、IM)** ⭐⭐⭐⭐⭐

**战略价值**: A股系统性风险的"温度计"和最重要的对冲工具

**具体实现**:
```yaml
futures_realtime:          # 股指期货实时行情
  endpoint_name: futures_realtime
  source_name: tdx
  data_category: FUTURES_DATA
  target_db: tdengine
  table_name: futures_tick

futures_daily_kline:       # 期货日线数据
futures_basis_analysis:    # 期现基差分析
futures_position_data:     # 期货持仓数据
```

**量化应用**:
- **Beta对冲**: `对冲比例 = 组合Beta × 组合市值 / 期货合约价值`
- **基差分析**: `基差 = 期货价格 - 现货指数`
- **跨期套利**: 不同合约月份的价差交易

## 📈 P1级 - 强烈建议中期补充 (策略完善)

### 4. **宏观经济与利率数据** ⭐⭐⭐⭐

**具体实现**:
```yaml
macro_economic_indicators: # 宏观经济指标
  endpoint_name: macro_economic_indicators
  source_name: wind_api  # 或其他专业数据源
  data_category: MACRO_DATA
  parameters:
    - indicator: 指标名称 (PMI/CPI/PPI/M1/M2/社融等)
    - start_date: 开始日期
    - freq: 频率 (月度/季度)
  target_db: postgresql
  table_name: macro_economic_data

interest_rate_data:        # 利率数据
yield_curve_data:          # 收益率曲线
```

### 5. **港股通数据 (北向资金)** ⭐⭐⭐⭐

**具体实现**:
```yaml
northbound_flow:           # 北向资金流向
  endpoint_name: northbound_flow
  source_name: akshare
  data_category: CROSS_MARKET_DATA
  target_db: postgresql
  table_name: northbound_flow

hk_stock_daily:            # 港股日线数据
ah_premium_index:          # AH股溢价指数
```

### 6. **行业与概念板块指数数据** ⭐⭐⭐⭐

**具体实现**:
```yaml
industry_index:            # 中信/申万行业指数
  endpoint_name: industry_index
  source_name: baostock
  data_category: SECTOR_DATA
  parameters:
    - industry_level: 行业级别 (1/2/3级)
    - industry_code: 行业代码
  target_db: postgresql
  table_name: industry_index_data

concept_index:             # 概念板块指数
sector_fund_flow:          # 板块资金流向
```

## ⚖️ P2级 - 可选择性补充 (期权调整后)

### 7. **期权PCR指标 (50ETF期权 + 沪深300期权)** ⭐⭐⭐

**调整说明**: 将期权数据从P0降至P2，但保留高价值PCR指标

```yaml
option_pcr_ratio:          # 期权PCR值 (沽购比)
  endpoint_name: option_pcr_ratio
  source_name: akshare
  data_category: DERIVATIVES_DATA
  target_db: postgresql
  table_name: option_pcr_data
```

**量化应用**: 极佳的市场恐慌指数，用于大盘择时

## 🛠️ 技术实施方案

### **数据源适配器扩展**

```python
# 新增适配器类
class MarginTradingAdapter(IDataSource):      # 融资融券适配器
class InstitutionalAdapter(IDataSource):       # 机构数据适配器
class FuturesAdapter(IDataSource):             # 期货数据适配器
class MacroDataAdapter(IDataSource):          # 宏观数据适配器
class CrossMarketAdapter(IDataSource):        # 跨市场数据适配器
class SectorDataAdapter(IDataSource):         # 板块数据适配器

# 注册到数据源管理器
data_source_manager.register_adapter(MarginTradingAdapter())
data_source_manager.register_adapter(FuturesAdapter())
# ... 其他适配器
```

### **数据库存储策略**

```yaml
# 扩展数据分类
data_classifications:
  LEVERAGE_DATA:           # 杠杆数据 → PostgreSQL (复杂分析)
  INSTITUTIONAL_DATA:      # 机构数据 → PostgreSQL (关系查询)
  FUTURES_DATA:            # 期货数据 → TDengine (高频时序)
  MACRO_DATA:              # 宏观数据 → PostgreSQL (历史分析)
  CROSS_MARKET_DATA:       # 跨市场数据 → PostgreSQL (关联分析)
  SECTOR_DATA:             # 板块数据 → PostgreSQL (聚合分析)
  DERIVATIVES_DATA:        # 衍生品数据 → PostgreSQL (期权分析)
```

### **GPU加速因子计算**

```python
# 利用现有GPU加速引擎
class QuantFactorEngine:
    def calculate_margin_factors(self, margin_data: pd.DataFrame):
        """融资融券因子计算 (GPU加速)"""
        # 反转因子: 融资余额变化率
        # 杠杆因子: 融资买入比
        # 风险因子: 融资偿还率
        
    def calculate_institutional_factors(self, institutional_data: pd.DataFrame):
        """机构因子计算"""
        # 席位联动因子
        # 机构占比因子
        
    def calculate_futures_factors(self, futures_data: pd.DataFrame):
        """期货因子计算"""
        # 基差因子
        # 跨期价差因子
```

## 📋 实施优先级与时间表

### **Phase 1: P0核心数据 (1个月内完成)**
1. **Week 1**: 融资融券数据接入
   - 适配器开发
   - 数据表结构设计
   - 基础因子计算
2. **Week 2**: 龙虎榜数据接入
   - 机构数据清洗
   - 席位识别算法
3. **Week 3**: 股指期货数据接入
   - 实时数据接入
   - 基差分析功能
4. **Week 4**: 集成测试与优化

### **Phase 2: P1策略完善 (2-3个月)**
1. **Month 2**: 宏观经济数据
2. **Month 3**: 港股通 + 板块指数数据

### **Phase 3: P2扩展探索 (3-6个月)**
1. **Month 4-6**: 期权PCR + 其他全球数据 (视需求)

## 🎯 预期量化收益

### **策略增强**
- **中性策略**: 股指期货对冲，提高夏普比率20-50%
- **事件驱动**: 龙虎榜信号，超额收益15-25%
- **杠杆择时**: 融资融券指标，降低回撤10-20%

### **风险控制**
- **系统性风险**: 宏观数据预警，减少极端事件损失
- **流动性风险**: 融资数据监控，避免杠杆踩踏
- **机构动向**: 龙虎榜提前感知市场转折

### **新策略解锁**
- **AH套利**: 港股通数据支持
- **行业轮动**: 板块指数量化
- **跨市场对冲**: 期货数据支持

这个扩展计划完全遵循您的"高价值数据"原则，将MyStocks从基础数据平台升级为专业量化交易的利器。建议按照P0→P1→P2的顺序实施，确保每一步都能带来显著的alpha提升。