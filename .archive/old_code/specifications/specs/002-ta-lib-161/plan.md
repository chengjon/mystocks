# Implementation Plan: Technical Analysis with 161 Indicators

**Branch**: `002-ta-lib-161` | **Date**: 2025-10-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-ta-lib-161/spec.md`

## Summary

This feature implements a comprehensive technical analysis system with 161 indicators from TA-Lib, organized in 5 categories (Trend, Momentum, Volatility, Volume, Candlestick Patterns). Users can search stocks, select date ranges, apply multiple indicators to K-line charts, and visualize results through interactive charts with overlay and oscillator panels. The system integrates with existing OHLCV data endpoints and provides indicator parameter customization, configuration persistence, and chart export capabilities.

## Technical Context

**Language/Version**: Python 3.11 (backend), Node.js 18+ with bun (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.104+, TA-Lib 0.6.7, NumPy, Pandas
- Frontend: Vue 3.4+, Element Plus 2.4+, klinecharts 9.8+, axios
**Storage**:
- Historical OHLCV data: PostgreSQL+TimescaleDB (existing, via `/api/data/stocks/daily`)
- Indicator configurations: MySQL/MariaDB (new, user preferences)
- Cache layer: Redis (optional, response caching)
**Testing**:
- Backend: pytest with FastAPI test client
- Frontend: Vitest + Vue Test Utils
**Target Platform**: Web application (desktop browsers: Chrome/Firefox/Safari/Edge last 2 versions)
**Project Type**: Web (backend + frontend)
**Performance Goals**:
- Chart render with 10 indicators: <100ms interaction response
- Indicator calculation for 1 year data: <2 seconds
- API response time: <500ms for standard requests
**Constraints**:
- Maximum 10 concurrent indicators per chart
- Support up to 10 years (2500 data points) of daily data
- Chart export minimum resolution: 1200x800
**Scale/Scope**:
- 161 TA-Lib indicators across 5 categories
- Expected 100+ concurrent users
- ~2MB payload for 1 year OHLCV data + 10 indicators

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. 5层数据分类体系 - ✅ COMPLIANT

**数据分类映射**:

1. **第3类: 衍生数据 (Derived Data)** - 技术指标计算结果
   - 161个技术指标的计算值 → PostgreSQL+TimescaleDB
   - 原理: 指标是基于OHLCV数据的计算分析结果,属于衍生数据范畴
   - 存储策略: 时序存储,支持历史回溯和趋势分析

2. **第5类: 元数据 (Meta Data)** - 用户指标配置
   - 用户保存的指标配置(指标组合、参数设置) → MySQL/MariaDB
   - 原理: 用户个性化配置属于元数据-用户配置子类
   - 存储策略: 关系型存储,支持版本管理和用户关联

**合规说明**:
- 技术指标结果作为衍生数据存储在PostgreSQL中,符合宪法第3类定义
- 用户指标配置作为元数据存储在MySQL中,符合宪法第5类用户配置子类
- 原始OHLCV数据使用现有数据接口,不引入新的市场数据存储

### II. 配置驱动设计 - ✅ COMPLIANT

**遵循方式**:
- 新增表结构将通过 `table_config.yaml` 定义:
  - `indicator_configurations` 表: 用户保存的指标配置
  - `indicator_cache` 表: 计算结果缓存(可选)
- 通过 `ConfigDrivenTableManager` 自动创建表结构
- 所有配置变更进行版本控制

**合规说明**: 本功能遵循配置驱动原则,所有新表通过YAML定义,不手动修改数据库架构

### III. 智能自动路由 - ✅ COMPLIANT

**路由策略**:
- 指标计算结果通过 `save_data_by_classification(DataClassification.TECHNICAL_INDICATORS, ...)`
- 用户配置通过 `save_data_by_classification(DataClassification.USER_CONFIG, ...)`
- 系统自动路由到对应数据库,无需应用代码指定

**合规说明**: 使用统一管理器的分类方法,由系统自动路由,不在应用层硬编码数据库选择

### IV. 多数据库协同 - ✅ COMPLIANT

**数据库使用策略**:
- PostgreSQL: 存储指标计算结果(衍生数据,时序特性)
- MySQL: 存储用户指标配置(元数据,关系型)
- Redis: 可选响应缓存(热数据,高频访问)
- 不引入新数据库类型,使用现有基础设施

**合规说明**: 基于数据特性选择数据库,PostgreSQL用于时序衍生数据,MySQL用于关系型元数据,Redis用于热数据缓存

### V. 完整可观测性 - ✅ COMPLIANT

**监控集成**:
- 所有指标计算操作记录到 `MonitoringDatabase`
- `PerformanceMonitor` 跟踪API响应时间和指标计算耗时
- `DataQualityMonitor` 验证OHLCV数据完整性(计算前置条件)
- 慢查询告警(>5秒的复杂指标计算)

**合规说明**: 所有数据操作记录到独立监控数据库,性能和质量指标自动采集

### VI. 统一访问接口 - ✅ COMPLIANT

**访问模式**:
- 后端API通过 `MyStocksUnifiedManager` 访问所有数据
- 指标计算服务使用统一接口加载OHLCV数据
- 不直接操作数据库连接,通过管理器抽象层

**合规说明**: 所有数据操作通过 `MyStocksUnifiedManager` 进行,遵循统一接口原则

### VII. 安全优先 - ✅ COMPLIANT

**安全实践**:
- 数据库凭证使用环境变量(`.env` 文件)
- API认证复用现有JWT机制
- 用户配置数据隔离(user_id关联)
- `.env` 文件已在 `.gitignore` 中排除

**合规说明**: 无硬编码凭证,使用环境变量管理敏感配置,遵循安全优先原则

### Constitution Check Summary

✅ **ALL GATES PASSED** - No violations, no complexity justification needed.

本功能完全符合MyStocks项目宪法的所有核心原则:
1. 数据正确分类为衍生数据和元数据
2. 新表通过配置文件定义
3. 使用自动路由而非硬编码数据库
4. 基于数据特性选择PostgreSQL和MySQL
5. 集成完整监控和质量检查
6. 通过统一管理器访问数据
7. 环境变量管理敏感配置

## Project Structure

### Documentation (this feature)

```
specs/002-ta-lib-161/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Technology research and decisions
├── data-model.md        # Phase 1: Data entities and relationships
├── quickstart.md        # Phase 1: Developer onboarding guide
├── contracts/           # Phase 1: API contracts
│   ├── indicators.yaml  # Indicator calculation API
│   └── config.yaml      # Configuration management API
└── tasks.md             # Phase 2: Implementation tasks (created by /speckit.tasks)
```

### Source Code (repository root)

```
web/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── indicators.py          # NEW: Indicator calculation endpoints
│   │   │   ├── indicator_config.py    # NEW: Configuration CRUD endpoints
│   │   │   └── data.py                # EXISTING: Stock data endpoints
│   │   ├── services/
│   │   │   ├── indicator_calculator.py    # NEW: TA-Lib wrapper service
│   │   │   ├── indicator_registry.py      # NEW: 161 indicators registry
│   │   │   └── indicator_cache.py         # NEW: Result caching service
│   │   ├── models/
│   │   │   ├── indicator_config.py        # NEW: Configuration model
│   │   │   └── indicator_result.py        # NEW: Calculation result model
│   │   └── schemas/
│   │       ├── indicator_request.py       # NEW: Request DTOs
│   │       └── indicator_response.py      # NEW: Response DTOs
│   └── tests/
│       ├── test_indicators.py             # NEW: Indicator calculation tests
│       ├── test_indicator_config.py       # NEW: Configuration tests
│       └── test_indicator_performance.py  # NEW: Performance tests
│
└── frontend/
    ├── src/
    │   ├── views/
    │   │   └── TechnicalAnalysis.vue     # MODIFY: Main feature page
    │   ├── components/
    │   │   ├── chart/
    │   │   │   ├── KLineChart.vue        # NEW: K-line chart component
    │   │   │   ├── IndicatorPanel.vue    # NEW: Indicator panel component
    │   │   │   └── ChartToolbar.vue      # NEW: Chart controls toolbar
    │   │   ├── indicators/
    │   │   │   ├── IndicatorSelector.vue     # NEW: Indicator selection UI
    │   │   │   ├── IndicatorParameters.vue   # NEW: Parameter config UI
    │   │   │   └── IndicatorLegend.vue       # NEW: Legend component
    │   │   └── config/
    │   │       ├── ConfigSaver.vue           # NEW: Save configuration dialog
    │   │       └── ConfigLoader.vue          # NEW: Load configuration dialog
    │   ├── services/
    │   │   ├── indicatorService.ts       # NEW: API client for indicators
    │   │   └── chartService.ts           # NEW: Chart management service
    │   ├── composables/
    │   │   ├── useIndicators.ts          # NEW: Indicator state management
    │   │   ├── useChart.ts               # NEW: Chart state management
    │   │   └── useIndicatorConfig.ts     # NEW: Config persistence
    │   └── types/
    │       ├── indicator.ts              # NEW: Indicator type definitions
    │       └── chart.ts                  # NEW: Chart type definitions
    └── tests/
        ├── components/
        │   └── chart/
        │       ├── KLineChart.spec.ts        # NEW: Chart component tests
        │       └── IndicatorSelector.spec.ts # NEW: Selector tests
        └── services/
            └── indicatorService.spec.ts      # NEW: Service tests
```

**Structure Decision**:

本项目使用 **Option 2: Web application** 结构,因为功能包含FastAPI后端和Vue3前端。

- **后端** (`web/backend/`): 新增指标计算API、TA-Lib封装服务、配置管理
- **前端** (`web/frontend/`): 新增技术分析页面、图表组件、指标选择UI
- **分离原则**: 后端专注数据计算和存储,前端专注交互和可视化
- **集成点**: 通过RESTful API通信,前端调用后端指标计算服务

## Complexity Tracking

*No violations detected - this section is intentionally empty.*

本功能完全符合项目宪法,无需复杂性论证。
