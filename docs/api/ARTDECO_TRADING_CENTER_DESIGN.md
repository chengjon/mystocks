# ArtDeco 量化交易管理中心 - 菜单功能树设计

**版本**: 2.0.0
**设计日期**: 2025-01-14
**ArtDeco主题**: 金色主色调 (#D4AF37)，几何装饰设计

---

## 🎯 设计理念

### 核心目标
- **功能树导航**: 将21个现有Vue页面重新组织成逻辑清晰的功能树结构
- **API充分利用**: 基于571个API端点的完整功能映射
- **ArtDeco美学**: 统一的金色装饰主题和几何设计元素
- **US3架构支持**: 充分利用5层数据分类和自动路由机制

### 设计原则
- **树形导航**: 3级菜单结构，最深不超过3层
- **功能聚合**: 相关功能集中，避免页面碎片化
- **渐进展开**: 大功能区折叠展示，减少视觉干扰
- **状态保持**: 记住用户的展开/折叠偏好

---

## 🌳 菜单功能树结构

```tree
📊 量化交易管理中心
├── 🎯 市场总览 (Market Overview)
│   ├── 📈 实时行情监控 (Realtime Monitor)
│   │   ├── 市场指数 (Market Indices)
│   │   ├── 股票排行 (Stock Rankings)
│   │   └── 成交统计 (Trading Volume)
│   ├── 📊 市场数据分析 (Market Data Analysis)
│   │   ├── 技术指标 (Technical Indicators)
│   │   ├── 资金流向 (Capital Flow)
│   │   └── 龙虎榜 (LongHu Bang)
│   └── 🏭 行业概念分析 (Industry & Concept Analysis)
│       ├── 行业板块 (Industry Sectors)
│       ├── 概念板块 (Concept Themes)
│       └── 板块对比 (Sector Comparison)
├── 💼 交易管理 (Trading Management)
│   ├── 📡 交易信号 (Trading Signals)
│   │   ├── 信号概览 (Signal Overview)
│   │   ├── 信号详情 (Signal Details)
│   │   └── 信号历史 (Signal History)
│   ├── 📋 交易历史 (Trading History)
│   │   ├── 订单记录 (Order Records)
│   │   ├── 成交记录 (Trade Records)
│   │   └── 历史统计 (Historical Stats)
│   ├── 📊 持仓监控 (Position Monitor)
│   │   ├── 当前持仓 (Current Positions)
│   │   ├── 盈亏分析 (P&L Analysis)
│   │   └── 风险指标 (Risk Metrics)
│   └── 📈 绩效分析 (Performance Analysis)
│       ├── 收益曲线 (Return Curve)
│       ├── 归因分析 (Attribution Analysis)
│       └── 绩效指标 (Performance Metrics)
├── 🧠 策略中心 (Strategy Center)
│   ├── ⚙️ 策略管理 (Strategy Management)
│   │   ├── 策略列表 (Strategy List)
│   │   ├── 策略创建 (Strategy Creation)
│   │   └── 策略配置 (Strategy Config)
│   ├── 🔬 回测分析 (Backtest Analysis)
│   │   ├── 回测设置 (Backtest Setup)
│   │   ├── 回测结果 (Backtest Results)
│   │   └── 回测报告 (Backtest Reports)
│   └── 🎯 策略优化 (Strategy Optimization)
│       ├── 参数优化 (Parameter Optimization)
│       ├── 风险调整 (Risk Adjustment)
│       └── 性能评估 (Performance Evaluation)
├── 🛡️ 风险控制 (Risk Control)
│   ├── 📊 风险监控 (Risk Monitor)
│   │   ├── 风险概览 (Risk Overview)
│   │   ├── 风险趋势 (Risk Trends)
│   │   └── 风险预警 (Risk Alerts)
│   ├── 📢 公告监控 (Announcement Monitor)
│   │   ├── 公告列表 (Announcement List)
│   │   ├── 公告筛选 (Announcement Filter)
│   │   └── 公告分析 (Announcement Analysis)
│   └── 🚨 风险告警 (Risk Alerts)
│       ├── 告警中心 (Alert Center)
│       ├── 告警规则 (Alert Rules)
│       └── 告警历史 (Alert History)
└── ⚙️ 系统管理 (System Management)
    ├── 📊 监控面板 (Monitoring Dashboard)
    │   ├── 系统状态 (System Status)
    │   ├── 性能指标 (Performance Metrics)
    │   └── 数据质量 (Data Quality)
    ├── 💾 数据管理 (Data Management)
    │   ├── 数据导入 (Data Import)
    │   ├── 数据导出 (Data Export)
    │   └── 数据清理 (Data Cleanup)
    └── 🔧 系统设置 (System Settings)
        ├── 通用设置 (General Settings)
        ├── 界面设置 (UI Settings)
        └── 安全设置 (Security Settings)
```

---

## 🔗 API端点映射表

### 市场总览模块 API映射

#### 实时行情监控 (95个API端点)
| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 市场指数 | `GET /api/market/realtime/indices` | TDengine → SSE推送 | `ArtDecoMarketIndices.vue` |
| 股票排行 | `GET /api/market/rankings/stocks` | PostgreSQL查询 | `ArtDecoStockRankings.vue` |
| 成交统计 | `GET /api/market/statistics/volume` | TDengine聚合 | `ArtDecoVolumeStats.vue` |

#### 市场数据分析 (45个API端点)
| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 技术指标 | `GET /api/indicators/calculate` | 实时计算 → 缓存 | `ArtDecoTechnicalIndicators.vue` |
| 资金流向 | `GET /api/market/capital-flow` | TDengine时序数据 | `ArtDecoCapitalFlow.vue` |
| 龙虎榜 | `GET /api/market/longhubang` | PostgreSQL事务数据 | `ArtDecoLongHuBang.vue` |

#### 行业概念分析 (35个API端点)
| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 行业板块 | `GET /api/market/industries` | PostgreSQL参考数据 | `ArtDecoIndustryAnalysis.vue` |
| 概念板块 | `GET /api/market/concepts` | PostgreSQL参考数据 | `ArtDecoConceptAnalysis.vue` |
| 板块对比 | `POST /api/analysis/compare-sectors` | 多表关联查询 | `ArtDecoSectorComparison.vue` |

### 交易管理模块 API映射

#### 交易信号 (65个API端点)
| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 信号概览 | `GET /api/signals/overview` | PostgreSQL聚合 | `ArtDecoSignalOverview.vue` |
| 信号详情 | `GET /api/signals/{id}/details` | PostgreSQL详情查询 | `ArtDecoSignalDetails.vue` |
| 信号历史 | `GET /api/signals/history` | TDengine时序数据 | `ArtDecoSignalHistory.vue` |

#### 交易历史 (30个API端点)
| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 订单记录 | `GET /api/trade/orders` | PostgreSQL事务表 | `ArtDecoOrderRecords.vue` |
| 成交记录 | `GET /api/trade/trades` | PostgreSQL事务表 | `ArtDecoTradeRecords.vue` |
| 历史统计 | `GET /api/trade/statistics` | PostgreSQL聚合查询 | `ArtDecoTradeStats.vue` |

#### 持仓监控 (25个API端点)
| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 当前持仓 | `GET /api/trade/positions` | PostgreSQL持仓表 | `ArtDecoCurrentPositions.vue` |
| 盈亏分析 | `GET /api/trade/pnl-analysis` | 实时计算 | `ArtDecoPnLAnalysis.vue` |
| 风险指标 | `GET /api/risk/position-metrics` | 风险计算引擎 | `ArtDecoPositionRisk.vue` |

#### 绩效分析 (20个API端点)
| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 收益曲线 | `GET /api/performance/returns` | TDengine时序数据 | `ArtDecoReturnCurve.vue` |
| 归因分析 | `POST /api/analysis/attribution` | 多因子模型计算 | `ArtDecoAttributionAnalysis.vue` |
| 绩效指标 | `GET /api/performance/metrics` | 标准指标计算 | `ArtDecoPerformanceMetrics.vue` |

### 策略中心模块 API映射

#### 策略管理 (65个API端点)
| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 策略列表 | `GET /api/strategy/list` | PostgreSQL策略表 | `ArtDecoStrategyList.vue` |
| 策略创建 | `POST /api/strategy/create` | 策略模板引擎 | `ArtDecoStrategyCreation.vue` |
| 策略配置 | `PUT /api/strategy/{id}/config` | 参数验证存储 | `ArtDecoStrategyConfig.vue` |

#### 回测分析 (45个API端点)
| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 回测设置 | `POST /api/backtest/setup` | 参数验证存储 | `ArtDecoBacktestSetup.vue` |
| 回测结果 | `GET /api/backtest/{id}/results` | GPU加速计算结果 | `ArtDecoBacktestResults.vue` |
| 回测报告 | `GET /api/backtest/{id}/report` | HTML/PDF报告生成 | `ArtDecoBacktestReport.vue` |

#### 策略优化 (25个API端点)
| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 参数优化 | `POST /api/optimization/parameters` | 遗传算法优化 | `ArtDecoParameterOptimization.vue` |
| 风险调整 | `POST /api/optimization/risk-adjust` | 风险模型调整 | `ArtDecoRiskAdjustment.vue` |
| 性能评估 | `GET /api/optimization/performance` | 多维度评估 | `ArtDecoPerformanceEvaluation.vue` |

### 风险控制模块 API映射

#### 风险监控 (35个API端点)
| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 风险概览 | `GET /api/risk/overview` | 综合风险指标 | `ArtDecoRiskOverview.vue` |
| 风险趋势 | `GET /api/risk/trends` | TDengine时序数据 | `ArtDecoRiskTrends.vue` |
| 风险预警 | `GET /api/risk/alerts` | 实时告警数据 | `ArtDecoRiskAlerts.vue` |

#### 公告监控 (15个API端点)
| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 公告列表 | `GET /api/announcements/list` | PostgreSQL公告表 | `ArtDecoAnnouncementList.vue` |
| 公告筛选 | `POST /api/announcements/filter` | 智能筛选引擎 | `ArtDecoAnnouncementFilter.vue` |
| 公告分析 | `POST /api/analysis/announcements` | NLP情感分析 | `ArtDecoAnnouncementAnalysis.vue` |

### 系统管理模块 API映射

#### 监控面板 (50个API端点)
| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 系统状态 | `GET /api/monitoring/system-status` | 健康检查数据 | `ArtDecoSystemStatus.vue` |
| 性能指标 | `GET /api/monitoring/performance` | Prometheus指标 | `ArtDecoPerformanceMetrics.vue` |
| 数据质量 | `GET /api/monitoring/data-quality` | 质量检查结果 | `ArtDecoDataQuality.vue` |

#### 数据管理 (30个API端点)
| 功能节点 | 主要API端点 | 数据流向 | Vue组件映射 |
|---------|-------------|---------|-------------|
| 数据导入 | `POST /api/data/import` | 文件上传处理 | `ArtDecoDataImport.vue` |
| 数据导出 | `POST /api/data/export` | 多格式导出 | `ArtDecoDataExport.vue` |
| 数据清理 | `POST /api/data/cleanup` | 数据清理任务 | `ArtDecoDataCleanup.vue` |

---

## 🎨 ArtDeco设计系统实现

### 视觉设计规范

#### 颜色系统
```scss
// ArtDeco主色调
--artdeco-gold-primary: #D4AF37;
--artdeco-gold-secondary: #B8860B;
--artdeco-gold-accent: #FFD700;

// 功能色
--artdeco-rise: #FF5252;    // 红色上涨
--artdeco-fall: #00E676;    // 绿色下跌
--artdeco-neutral: #888888; // 中性灰色

// 背景色
--artdeco-bg-primary: #0A0A0B;     // 深色背景
--artdeco-bg-secondary: #141414;   // 卡片背景
--artdeco-bg-tertiary: #1A1A1A;    // 边框背景
```

#### 几何装饰元素
```scss
// 金色装饰边框
.artdeco-geometric-border {
  position: relative;
  border: 2px solid var(--artdeco-gold-primary);
  border-radius: 16px;

  &::before {
    content: '';
    position: absolute;
    top: -4px;
    left: -4px;
    right: -4px;
    bottom: -4px;
    border: 1px solid var(--artdeco-gold-secondary);
    border-radius: 20px;
    pointer-events: none;
  }
}

// 角点装饰
.artdeco-corner-decoration {
  position: relative;

  &::after {
    content: '';
    position: absolute;
    top: 8px;
    right: 8px;
    width: 12px;
    height: 12px;
    background: var(--artdeco-gold-accent);
    clip-path: polygon(0 0, 100% 0, 0 100%);
  }
}
```

### 组件库设计

#### ArtDecoFunctionTree 组件
```vue
<template>
  <div class="artdeco-function-tree">
    <div class="tree-header">
      <ArtDecoTitle>量化交易管理中心</ArtDecoTitle>
    </div>

    <div class="tree-navigation">
      <ArtDecoTreeNode
        v-for="node in treeData"
        :key="node.key"
        :node="node"
        :level="1"
        v-model:expanded="expandedNodes"
        @select="handleNodeSelect"
      />
    </div>
  </div>
</template>
```

#### ArtDecoTreeNode 组件
```vue
<template>
  <div class="artdeco-tree-node" :class="{ expanded, active }">
    <div class="node-header" @click="toggleExpand">
      <ArtDecoIcon :name="node.icon" class="node-icon" />
      <span class="node-label">{{ node.label }}</span>
      <ArtDecoIcon
        name="chevron-right"
        class="expand-icon"
        :class="{ rotated: expanded }"
      />
    </div>

    <transition name="slide">
      <div v-if="expanded && node.children" class="node-children">
        <ArtDecoTreeNode
          v-for="child in node.children"
          :key="child.key"
          :node="child"
          :level="level + 1"
          @select="$emit('select', $event)"
        />
      </div>
    </transition>
  </div>
</template>
```

### 响应式设计

#### 移动端适配
```scss
// 移动端菜单折叠
@media (max-width: 768px) {
  .artdeco-function-tree {
    position: fixed;
    left: -280px;
    top: 0;
    bottom: 0;
    width: 280px;
    background: var(--artdeco-bg-primary);
    z-index: 1000;
    transition: left 0.3s ease;

    &.open {
      left: 0;
    }
  }
}

// 平板端优化
@media (max-width: 1024px) {
  .tree-navigation {
    max-height: 60vh;
    overflow-y: auto;
  }
}
```

---

## 🔧 技术实现架构

### 组件层级结构
```
ArtDecoTradingManagement.vue (主容器)
├── ArtDecoHeader.vue (页面头部)
├── ArtDecoFunctionTree.vue (功能树导航)
│   └── ArtDecoTreeNode.vue (树节点组件)
├── ArtDecoContentArea.vue (内容区域)
│   ├── 动态组件加载 (基于选择的功能)
│   └── ArtDecoBreadcrumb.vue (面包屑导航)
└── ArtDecoFooter.vue (页脚状态栏)
```

### API集成层
```typescript
// 统一API管理器
class TradingApiManager {
  private marketApi: MarketApi
  private strategyApi: StrategyApi
  private riskApi: RiskApi
  private monitoringApi: MonitoringApi

  // 市场数据集成
  async getMarketOverview(): Promise<MarketOverview> {
    const [indices, rankings, volume] = await Promise.all([
      this.marketApi.getIndices(),
      this.marketApi.getRankings(),
      this.marketApi.getVolumeStats()
    ])
    return { indices, rankings, volume }
  }

  // 策略数据集成
  async getStrategyCenterData(): Promise<StrategyCenterData> {
    const [strategies, backtests, optimizations] = await Promise.all([
      this.strategyApi.getStrategies(),
      this.strategyApi.getBacktestHistory(),
      this.strategyApi.getOptimizationTasks()
    ])
    return { strategies, backtests, optimizations }
  }

  // 风险数据集成
  async getRiskControlData(): Promise<RiskControlData> {
    const [overview, announcements, alerts] = await Promise.all([
      this.riskApi.getRiskOverview(),
      this.riskApi.getAnnouncements(),
      this.riskApi.getAlerts()
    ])
    return { overview, announcements, alerts }
  }
}
```

### 状态管理
```typescript
// Pinia Store 架构
interface TradingState {
  activeFunction: string
  expandedNodes: Set<string>
  loadingStates: Record<string, boolean>
  cache: Map<string, any>
}

const useTradingStore = defineStore('trading', {
  state: (): TradingState => ({
    activeFunction: 'market-overview',
    expandedNodes: new Set(['market-overview']),
    loadingStates: {},
    cache: new Map()
  }),

  actions: {
    // 功能切换
    switchFunction(functionKey: string) {
      this.activeFunction = functionKey
      this.updateExpandedNodes(functionKey)
    },

    // 节点展开/折叠
    toggleNode(nodeKey: string) {
      if (this.expandedNodes.has(nodeKey)) {
        this.expandedNodes.delete(nodeKey)
      } else {
        this.expandedNodes.add(nodeKey)
      }
    },

    // 缓存管理
    setCache(key: string, data: any, ttl: number = 300000) { // 5分钟TTL
      this.cache.set(key, { data, timestamp: Date.now(), ttl })
    },

    getCache(key: string): any | null {
      const cached = this.cache.get(key)
      if (cached && (Date.now() - cached.timestamp) < cached.ttl) {
        return cached.data
      }
      this.cache.delete(key)
      return null
    }
  }
})
```

### 路由配置
```typescript
// 功能树路由映射
const functionRoutes: Record<string, Component> = {
  // 市场总览
  'market-overview': () => import('@/views/trading-center/market/MarketOverview.vue'),
  'realtime-monitor': () => import('@/views/trading-center/market/RealtimeMonitor.vue'),
  'market-analysis': () => import('@/views/trading-center/market/MarketAnalysis.vue'),
  'industry-analysis': () => import('@/views/trading-center/market/IndustryAnalysis.vue'),

  // 交易管理
  'trading-signals': () => import('@/views/trading-center/trading/SignalsView.vue'),
  'trading-history': () => import('@/views/trading-center/trading/HistoryView.vue'),
  'position-monitor': () => import('@/views/trading-center/trading/PositionMonitor.vue'),
  'performance-analysis': () => import('@/views/trading-center/trading/PerformanceAnalysis.vue'),

  // 策略中心
  'strategy-management': () => import('@/views/trading-center/strategy/StrategyManagement.vue'),
  'backtest-analysis': () => import('@/views/trading-center/strategy/BacktestAnalysis.vue'),
  'strategy-optimization': () => import('@/views/trading-center/strategy/StrategyOptimization.vue'),

  // 风险控制
  'risk-monitor': () => import('@/views/trading-center/risk/RiskMonitor.vue'),
  'announcement-monitor': () => import('@/views/trading-center/risk/AnnouncementMonitor.vue'),
  'risk-alerts': () => import('@/views/trading-center/risk/RiskAlerts.vue'),

  // 系统管理
  'monitoring-dashboard': () => import('@/views/trading-center/system/MonitoringDashboard.vue'),
  'data-management': () => import('@/views/trading-center/system/DataManagement.vue'),
  'system-settings': () => import('@/views/trading-center/system/SystemSettings.vue')
}
```

---

## 📊 数据流转优化

### US3架构集成
```typescript
// 数据分类自动路由
class DataFlowManager {
  // 市场数据 → TDengine
  async saveMarketData(data: MarketData, type: MarketDataType) {
    const classification = this.getMarketClassification(type)
    return await dataManager.saveDataByClassification(classification, data)
  }

  // 策略数据 → PostgreSQL
  async saveStrategyData(data: StrategyData, type: StrategyDataType) {
    const classification = this.getStrategyClassification(type)
    return await dataManager.saveDataByClassification(classification, data)
  }

  // 交易数据 → PostgreSQL (事务性)
  async saveTradingData(data: TradingData, type: TradingDataType) {
    const classification = this.getTradingClassification(type)
    return await dataManager.saveDataByClassification(classification, data)
  }

  // 分类映射
  private getMarketClassification(type: MarketDataType): DataClassification {
    const mapping = {
      [MarketDataType.TICK]: DataClassification.TICK_DATA,
      [MarketDataType.KLINE]: DataClassification.MINUTE_KLINE,
      [MarketDataType.FUND_FLOW]: DataClassification.FUND_FLOW
    }
    return mapping[type] || DataClassification.MARKET_DATA
  }
}
```

### 批量操作优化
```typescript
// 批量数据处理
class BatchProcessor {
  async processBatchData(items: any[], operation: BatchOperation) {
    // 分批处理，避免内存溢出
    const batchSize = 1000
    const results = []

    for (let i = 0; i < items.length; i += batchSize) {
      const batch = items.slice(i, i + batchSize)
      const batchResult = await this.processSingleBatch(batch, operation)
      results.push(batchResult)
    }

    return results
  }

  private async processSingleBatch(batch: any[], operation: BatchOperation) {
    // 使用execute_values进行批量插入
    return await database.executeBatch(operation, batch)
  }
}
```

### 缓存策略
```typescript
// 多级缓存管理
class CacheManager {
  private memoryCache = new Map<string, CachedItem>()
  private redisCache: RedisCache

  async get(key: string): Promise<any | null> {
    // L1: 内存缓存
    const memoryItem = this.memoryCache.get(key)
    if (memoryItem && !this.isExpired(memoryItem)) {
      return memoryItem.data
    }

    // L2: Redis缓存
    const redisItem = await this.redisCache.get(key)
    if (redisItem) {
      // 提升到内存缓存
      this.memoryCache.set(key, redisItem)
      return redisItem.data
    }

    return null
  }

  async set(key: string, data: any, ttl: number = 300000) {
    const item: CachedItem = {
      data,
      timestamp: Date.now(),
      ttl
    }

    // 双写策略
    this.memoryCache.set(key, item)
    await this.redisCache.set(key, item)
  }
}
```

---

## ✅ CI/CD符合性保证

### 安全验证扩展
- [x] **代码安全扫描**: 危险函数检测 (exec, eval, os.system)
- [x] **依赖包安全检查**: Safety工具扫描第三方依赖
- [x] **敏感信息检测**: API密钥、密码、数据库连接串检测
- [x] **SQL注入防护**: 参数化查询验证

### 代码质量验证扩展
- [x] **代码复杂度分析**: 函数圈复杂度 < 8
- [x] **代码覆盖率检查**: 单元测试覆盖率 > 75%
- [x] **静态代码分析**: Ruff + MyPy 严格检查
- [x] **代码风格检查**: Black 120字符行长格式化

### 集成测试验证扩展
- [x] **数据库连接测试**: PostgreSQL + TDengine 连接验证
- [x] **API端点测试**: 571个端点的可用性测试
- [x] **服务集成测试**: 微服务间通信测试
- [x] **外部依赖测试**: AkShare等外部服务可用性

### 性能回归测试扩展
- [x] **响应时间回归**: API响应时间 < 100ms
- [x] **内存泄漏检测**: 内存增长 < 50MB
- [x] **并发性能测试**: 支持1000+并发连接
- [x] **资源使用监控**: CPU/内存/磁盘使用率监控

### AI增强验证扩展
- [x] **代码智能审查**: 自动检测代码异味
- [x] **自动化修复建议**: 提供具体的改进方案
- [x] **性能优化分析**: 识别性能瓶颈
- [x] **最佳实践建议**: 遵循行业标准和最佳实践

---

## 🚀 部署和维护

### 环境要求
- **Node.js**: 16.0+
- **Vue**: 3.4+
- **TypeScript**: 5.3+
- **Element Plus**: 2.13+

### 构建命令
```bash
# 安装依赖
npm install

# 开发环境
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint
npm run type-check

# 测试
npm run test
npm run test:e2e
```

### 性能监控
- **Lighthouse**: 性能评分 > 90
- **Bundle分析**: 包大小 < 2MB (gzip后)
- **Core Web Vitals**: 满足Google标准

---

*本文档定义了ArtDeco量化交易管理中心的完整设计方案，包括菜单功能树结构、API端点映射、UI设计规范、技术实现架构和CI/CD符合性保证。*