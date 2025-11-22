# MyStocks 架构文档索引

本目录包含MyStocks项目的完整架构设计文档，涵盖数据源架构、数据库设计、系统架构评审等内容。

---

## 快速导航

### 🎯 Phase 实施报告 (按时间顺序)

| Phase | 主题 | 文档 | 状态 | 完成日期 |
|-------|------|------|------|---------|
| **Phase 1** | 接口设计与架构规划 | [Phase1_完成报告.md](./Phase1_完成报告.md) | ✅ 完成 | 2025-11-21 |
| **Phase 2** | Mock数据源实现 | [Phase2_完成报告.md](./Phase2_完成报告.md) | ✅ 完成 | 2025-11-21 |
| **Phase 2 Day 1** | Mock数据源初版 | [Phase2_Day1_完成报告.md](./Phase2_Day1_完成报告.md) | ✅ 完成 | 2025-11-21 |
| **Phase 3** | Real数据源实现 | [Phase3_完成报告.md](./Phase3_完成报告.md) | ✅ 完成 | 2025-11-21 |
| **Phase 3 Day 1** | TDengine时序数据源 | [Phase3_Day1_完成报告.md](./Phase3_Day1_完成报告.md) | ✅ 完成 | 2025-11-21 |
| **Phase 3 验证** | 三层架构验证总结 | [Phase3_验证总结.md](./Phase3_验证总结.md) | ✅ 完成 | 2025-11-21 |
| **Phase 4 Day 1** | Dashboard API实现 | [Phase4_Day1_Dashboard_API完成报告.md](./Phase4_Day1_Dashboard_API完成报告.md) | ✅ 完成 | 2025-11-21 |
| **Phase 4 Day 2** | Strategy Management API | [Phase4_Day2_Strategy_Management_API完成报告.md](./Phase4_Day2_Strategy_Management_API完成报告.md) | ✅ 完成 | 2025-11-21 |
| **Phase 4 Day 3** | Frontend Integration | [Phase4_Day3_Frontend_Integration完成报告.md](./Phase4_Day3_Frontend_Integration完成报告.md) | ✅ 完成 | 2025-11-21 |
| **Phase 4 Day 4-5** | Database Persistence | [Phase4_Day4-5_Database_Persistence完成报告.md](./Phase4_Day4-5_Database_Persistence完成报告.md) | ✅ 完成 | 2025-11-21 |
| **Phase 4 Day 6-7** | Backtest Engine | [Phase4_Day6-7_BacktestEngine_Completion.md](./Phase4_Day6-7_BacktestEngine_Completion.md) | ✅ 完成 | 2025-11-22 |

---

## 🎯 策略模板系统 (Strategy Templates)

Phase 4 实现的完整策略回测系统，包含8个预置交易策略:

- [Strategy_Templates_Completion.md](./Strategy_Templates_Completion.md) - 策略模板系统完成报告 (原始4个策略)
  - 动量策略 (Momentum)
  - 均值回归 (Mean Reversion)
  - 突破策略 (Breakout)
  - 网格策略 (Grid)

- [Strategy_Templates_Expansion.md](./Strategy_Templates_Expansion.md) - 策略模板扩展报告 (新增4个策略)
  - 双均线策略 (Dual MA) - 金叉死叉，经典趋势跟踪
  - 海龟策略 (Turtle) - 唐奇安突破 + ATR仓位管理 + 金字塔加仓
  - MACD策略 - 趋势动量双重确认
  - 布林带突破 (Bollinger Breakout) - 波动率自适应交易

**代码统计**: 2,740+ 行策略代码 + 1,420+ 行演示脚本
**演示脚本**: `scripts/tests/demo_all_strategies.py`

---

## 📚 核心架构文档

### 数据源架构 (Data Source Architecture)

#### 第一原则分析
- [DATASOURCE_ARCHITECTURE_FIRST_PRINCIPLES_ANALYSIS.md](./DATASOURCE_ARCHITECTURE_FIRST_PRINCIPLES_ANALYSIS.md) - 数据源架构第一原则分析 (118KB)
- [FIRST_PRINCIPLES_ARCHITECTURE_REVIEW.md](./FIRST_PRINCIPLES_ARCHITECTURE_REVIEW.md) - 第一原则架构评审 (29KB)
- [ARCHITECTURE_REVIEW_FIRST_PRINCIPLES.md](./ARCHITECTURE_REVIEW_FIRST_PRINCIPLES.md) - 架构评审第一原则 (27KB)

#### 数据源与数据库架构
- [DATASOURCE_AND_DATABASE_ARCHITECTURE.md](./DATASOURCE_AND_DATABASE_ARCHITECTURE.md) - 数据源与数据库完整架构 (42KB)
- [DATABASE_ARCHITECTURE.md](./DATABASE_ARCHITECTURE.md) - 数据库架构设计 (17KB)

#### 架构评审与比较
- [ARCHITECTURE_EVALUATION_REPORT_2025.md](./ARCHITECTURE_EVALUATION_REPORT_2025.md) - 2025年架构评估报告 (42KB)
- [ARCHITECTURE_COMPARISON.md](./ARCHITECTURE_COMPARISON.md) - 架构对比分析 (20KB)
- [ARCHITECTURE_REVIEW_INDEX.md](./ARCHITECTURE_REVIEW_INDEX.md) - 架构评审索引 (12KB)
- [ARCHITECTURE_OPTIMIZATION_SUMMARY.md](./ARCHITECTURE_OPTIMIZATION_SUMMARY.md) - 架构优化总结 (8KB)

---

### Adapter 架构 (Adapter Architecture)

#### 评估与简化
- [ADAPTER_AND_DATABASE_ARCHITECTURE_EVALUATION.md](./ADAPTER_AND_DATABASE_ARCHITECTURE_EVALUATION.md) - Adapter与数据库架构评估 (15KB)
- [ADAPTER_SIMPLIFICATION_ANALYSIS.md](./ADAPTER_SIMPLIFICATION_ANALYSIS.md) - Adapter简化分析 (21KB)
- [ADAPTER_SIMPLIFICATION_COMPLETE_GUIDE.md](./ADAPTER_SIMPLIFICATION_COMPLETE_GUIDE.md) - Adapter简化完整指南 (16KB)
- [ADAPTER_SIMPLIFICATION_PRESENTATION.md](./ADAPTER_SIMPLIFICATION_PRESENTATION.md) - Adapter简化演示 (13KB)

#### 功能与扩展
- [ADAPTER_FUNCTION_SURVEY.md](./ADAPTER_FUNCTION_SURVEY.md) - Adapter功能调查 (11KB)
- [ADAPTER_EXTENSION_GUIDE.md](./ADAPTER_EXTENSION_GUIDE.md) - Adapter扩展指南 (39KB)
- [ADAPTER_ROUTING_GUIDE.md](./ADAPTER_ROUTING_GUIDE.md) - Adapter路由指南 (25KB)

---

### Mock 数据系统 (Mock Data System)

- [MOCK_DATA_COVERAGE_REPORT.md](./MOCK_DATA_COVERAGE_REPORT.md) - Mock数据覆盖率报告 (17KB)
- [MOCK_DATA_ENHANCEMENT_COMPLETION.md](./MOCK_DATA_ENHANCEMENT_COMPLETION.md) - Mock数据增强完成报告 (12KB)
- [MOCK_DATA_FINAL_SUMMARY.md](./MOCK_DATA_FINAL_SUMMARY.md) - Mock数据最终总结 (15KB)
- [MOCK_DATA_QUICK_REFERENCE.md](./MOCK_DATA_QUICK_REFERENCE.md) - Mock数据快速参考 (10KB)

---

### 数据库设计文档 (Database Design)

Phase 3中创建的数据库设计文档:

- [TDengine_Schema_Design.md](./TDengine_Schema_Design.md) - TDengine超级表设计 (650行)
  - 6个超级表: tick_data, minute_kline, daily_kline, fund_flow, index_realtime, market_snapshot
  - 存储估算、查询优化、数据保留策略

- [PostgreSQL_Schema_Design.md](./PostgreSQL_Schema_Design.md) - PostgreSQL表设计 (650行)
  - 10个业务表: users, watchlist, strategy_configs, risk_alerts, user_preferences等
  - 索引优化、外键约束、JSONB字段设计

---

## 🏗️ 三层数据源架构概览

MyStocks采用三层数据源架构设计:

```
┌─────────────────────────────────────────────────────────────┐
│                     业务层 (Layer 3)                         │
│  CompositeBusinessDataSource (11个业务方法)                  │
│  - 仪表盘汇总、板块表现、策略回测、风险管理、交易分析          │
└──────────────────┬───────────────────┬──────────────────────┘
                   │                   │
         ┌─────────▼────────┐  ┌──────▼──────────┐
         │  时序层 (Layer 1) │  │ 关系层 (Layer 2) │
         │  TDengine (11方法)│  │ PostgreSQL (23方法)│
         │  - 行情、K线      │  │  - 自选股、策略    │
         │  - 资金流向       │  │  - 风险、配置      │
         │  - 技术指标       │  │  - 板块、基础信息  │
         └──────────────────┘  └────────────────────┘
```

### 接口实现统计

| 接口类型 | 方法数 | Mock实现 | Real实现 | 覆盖率 |
|---------|-------|---------|---------|-------|
| **ITimeSeriesDataSource** | 11 | ✅ | ✅ TDengine | 100% |
| **IRelationalDataSource** | 23 | ✅ | ✅ PostgreSQL | 100% |
| **IBusinessDataSource** | 11 | ✅ | ✅ Composite | 100% |
| **总计** | 45 | ✅ | ✅ | 100% |

---

## 📖 文档阅读建议

### 新手入门路径
1. 先阅读 **Phase1_完成报告** 了解整体架构设计
2. 阅读 **Phase2_完成报告** 了解Mock数据源实现
3. 阅读 **Phase3_完成报告** 了解Real数据源实现
4. 参考 **Phase3_验证总结** 查看验证结果

### 深入学习路径
1. **数据源架构**:
   - DATASOURCE_ARCHITECTURE_FIRST_PRINCIPLES_ANALYSIS.md
   - DATASOURCE_AND_DATABASE_ARCHITECTURE.md

2. **数据库设计**:
   - TDengine_Schema_Design.md
   - PostgreSQL_Schema_Design.md

3. **架构评审**:
   - ARCHITECTURE_EVALUATION_REPORT_2025.md
   - FIRST_PRINCIPLES_ARCHITECTURE_REVIEW.md

### 实施指南路径
1. **Adapter系统**: ADAPTER_EXTENSION_GUIDE.md → ADAPTER_ROUTING_GUIDE.md
2. **Mock数据**: MOCK_DATA_QUICK_REFERENCE.md → MOCK_DATA_COVERAGE_REPORT.md
3. **架构优化**: ARCHITECTURE_OPTIMIZATION_SUMMARY.md

---

## 🎯 关键里程碑

| 里程碑 | 完成日期 | 核心交付物 |
|-------|---------|-----------|
| **接口设计** | 2025-11-21 | 3个数据源接口定义 (45个方法) |
| **Mock实现** | 2025-11-21 | 3个Mock数据源 + 测试套件 |
| **Real实现** | 2025-11-21 | TDengine + PostgreSQL + Composite |
| **架构验证** | 2025-11-21 | 13项验证测试 100%通过 |
| **回测引擎** | 2025-11-22 | 事件驱动回测引擎 + 性能指标 |
| **策略模板** | 2025-11-22 | 8个预置交易策略 + 策略工厂 |

---

## 📊 代码统计

### Phase 3 交付物统计
- **数据源实现**: 2,730 行代码 (TDengine 950 + PostgreSQL 1,100 + Composite 680)
- **接口定义**: 450 行代码
- **架构文档**: 2,300+ 行文档
- **测试套件**: 783 行测试代码
- **总计**: 6,263 行

### Phase 4 交付物统计
- **回测引擎**: 1,680 行代码 (引擎 + 性能指标 + 风险管理)
- **策略模板**: 2,740 行策略代码 (8个策略 + 基类 + 工厂)
- **API接口**: 800+ 行代码 (Dashboard + Strategy Management + WebSocket)
- **演示脚本**: 760 行代码 (功能演示 + 策略演示)
- **总计**: 5,980+ 行

---

## 🔗 相关文档

- **项目根目录**: [/opt/claude/mystocks_spec](../../)
- **开发指南**: [docs/guides/](../guides/)
- **API文档**: [docs/api/](../api/)
- **部署文档**: [docs/deployment/](../deployment/)

---

## 📝 文档维护

- **最后更新**: 2025-11-22
- **维护人**: Claude Code
- **更新频率**: 每个Phase完成后更新
- **最近更新**: 新增策略模板扩展报告 (8个策略)

---

**注意**: 所有架构文档都应保持与实际代码同步。如果代码有重大变更，请及时更新相关文档。
