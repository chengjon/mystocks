# Dashboard API丰富化指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**创建日期**: 2026-01-20
**目的**: 为ArtDeco Dashboard添加真实API数据，消除页面留空，提升专业度
**状态**: ✅ 颜色已修正（红涨绿跌）

---

## 📊 当前Dashboard分析

### 页面布局结构

| 区域 | 当前状态 | 数据来源 | 问题 |
|------|---------|---------|------|
| **页面头部** | 静态显示 | Mock数据 | 策略数、盈亏数据不真实 |
| **市场资金流向** | 静态显示 | Mock数据 | 沪股通、深股通、北向资金数据固定 |
| **主要市场指标** | 静态显示 | Mock数据 | 上证、深证、创业板指数硬编码 |
| **技术指标概览** | 静态显示 | Mock数据 | RSI、MACD、KDJ值硬编码 |
| **系统监控** | 静态显示 | Mock数据 | API响应时间、CPU、内存硬编码 |
| **市场热度板块** | 静态显示 | Mock数据 | 人工智能、新能源板块涨跌幅固定 |
| **资金流向排名** | 静态显示 | Mock数据 | 个股资金流向数据固定 |
| **股票池表现** | 静态显示 | Mock数据 | 持仓股票、收益率硬编码 |
| **快速导航** | ✅ 正常 | 路由配置 | 无需修改 |

**总结**: **9个区域中8个使用Mock数据**，仅1个真实功能。

---

## 🎯 API端点映射方案

### 优先级P0: 核心市场数据（立即实施）

#### 1. 主要市场指标（上证、深证、创业板）

**当前位置**: `market-indicators` 区域
**当前状态**: Mock数据
**建议API**:

```javascript
// 方案1: 使用market_v2.py的ETF list + 指数筛选
GET /api/market/v2/etf/list?limit=100
// 返回主要指数型ETF数据

// 方案2: 使用data.py的市场概览
GET /api/v1/data/market/overview
// 返回市场概览数据
```

**数据映射**:
```javascript
{
  "shanghai": {
    "index": 3128.45,      // ETF的latest_price
    "change": 0.85,         // ETF的change_percent
    "changePercent": "+0.03%"
  },
  "shenzhen": { ... },
  "chuangye": { ... }
}
```

**实施优先级**: 🔴 **最高** - 主要指数是Dashboard核心数据

---

#### 2. 市场资金流向（沪股通、深股通、北向资金）

**当前位置**: `enhanced-fund-flow` 区域
**当前状态**: Mock数据
**建议API**:

```javascript
// 方案1: 使用market.py的资金流向
GET /api/market/fund-flow
// 参数: date=2026-01-20

// 方案2: 使用market_v2.py的增强资金数据
GET /api/market/v2/fund-flow/detail
```

**数据映射**:
```javascript
{
  "fundFlow": {
    "hgt": {
      "amount": 28.6,      // 沪股通净流入(亿元)
      "change": 5.2        // 较昨日变化(亿元)
    },
    "sgt": { ... },
    "northTotal": {
      "amount": 58.8,
      "monthly": 1256      // 本月累计(亿元)
    },
    "mainForce": {
      "amount": 126.5,     // 主力净流入(亿元)
      "percentage": 68     // 占比(%)
    }
  }
}
```

**实施优先级**: 🔴 **最高** - 资金流向是专业量化交易核心关注点

---

#### 3. 市场热度板块（人工智能、新能源等）

**当前位置**: `heat-map-card` 区域
**当前状态**: Mock数据（6个板块固定）
**建议API**:

```javascript
// 方案1: 使用data.py的板块数据
GET /api/v1/data/sectors/performance?date=2026-01-20

// 方案2: 使用market.py的行业数据
GET /api/market/industry/flow?sort=change_percent&limit=10

// 方案3: 使用akshare_market.py
GET /api/akshare/sector/flow
```

**数据映射**:
```javascript
{
  "marketHeat": [
    { "name": "人工智能", "change": 3.2 },
    { "name": "新能源汽车", "change": 2.8 },
    { "name": "半导体", "change": -1.5 },
    // ... 动态从API获取前10个热门板块
  ]
}
```

**实施优先级**: 🟡 **高** - 板块热度数据直观反映市场热点

---

### 优先级P1: 专业交易数据（本周完成）

#### 4. 龙虎榜数据（市场活跃股票）

**新增区域**: 建议在Dashboard添加"龙虎榜"卡片
**建议API**:

```javascript
// 使用market.py的龙虎榜
GET /api/market/long-hu-bang?date=2026-01-20&limit=10
```

**显示内容**:
- 股票代码、名称
- 涨跌幅
- 龙虎榜原因（涨停、跌停、大宗交易等）
- 机构买卖金额

**UI组件建议**:
```vue
<ArtDecoCard title="龙虎榜" hoverable>
  <div class="long-hu-list">
    <div class="long-hu-item" v-for="item in longHuData" :key="item.code">
      <div class="stock-info">
        <div class="stock-name">{{ item.name }}</div>
        <div class="stock-code">{{ item.code }}</div>
      </div>
      <div class="long-hu-reason">{{ item.reason }}</div>
      <div class="long-hu-amount">{{ item.amount }}万</div>
    </div>
  </div>
</ArtDecoCard>
```

**实施优先级**: 🟡 **高** - 龙虎榜是专业交易者必看数据

---

#### 5. 大宗交易数据

**新增区域**: 建议在Dashboard添加"大宗交易"卡片
**建议API**:

```javascript
// 使用market_v2.py的大宗交易
GET /api/market/v2/block-trading?date=2026-01-20&limit=10
```

**显示内容**:
- 股票代码、名称
- 成交价格
- 成交金额（万元）
- 买方营业部、卖方营业部

**实施优先级**: 🟡 **高** - 大宗交易反映主力资金动向

---

#### 6. 资金流向持续排名

**当前位置**: `capital-flow-card` 区域
**当前状态**: Mock数据（5只股票固定）
**建议API**:

```javascript
// 方案1: 使用monitoring_analysis.py的个股资金流向
GET /api/monitoring/stock/flow/ranking?period=1day&limit=10

// 方案2: 使用market.py的个股资金流
GET /api/market/stock/flow?sort=net_inflow&limit=10
```

**数据映射**:
```javascript
{
  "capitalFlowData": [
    {
      "name": "贵州茅台",
      "code": "600519",
      "amount": 12.5,    // 净流入(亿元)
      "change": 2.1      // 涨跌幅(%)
    },
    // ... 动态获取前10名
  ]
}
```

**实施优先级**: 🟡 **高** - 资金流向排名是交易决策重要参考

---

#### 7. ETF数据

**新增区域**: 建议在Dashboard添加"ETF表现"卡片
**建议API**:

```javascript
// 使用market_v2.py的ETF list
GET /api/market/v2/etf/list?limit=20&sort=change_percent
```

**显示内容**:
- ETF代码、名称
- 最新价
- 涨跌幅
- 成交量

**实施优先级**: 🟢 **中** - ETF是被动投资重要工具

---

### 优先级P2: 技术分析与风险（下周完成）

#### 8. 技术指标概览（RSI、MACD、KDJ等）

**当前位置**: `indicators-section` 区域
**当前状态**: Mock数据（硬编码值）
**建议API**:

```javascript
// 使用technical_analysis.py的技术指标计算
GET /api/technical/indicators?symbol=000001&indicators=RSI,MACD,KDJ

// 或使用indicators.py的批量计算
GET /api/indicators/calculate/batch
Body: {
  "symbols": ["000001", "399001", "399006"],
  "indicators": ["RSI", "MACD", "KDJ", "BOLL", "WR"]
}
```

**数据映射**:
```javascript
{
  "indicators": [
    {
      "name": "RSI",
      "value": 67.8,
      "trend": "rise",      // rise/fall/neutral
      "signal": "多头"
    },
    {
      "name": "MACD",
      "value": 0.45,
      "trend": "rise",
      "signal": "金叉"
    },
    // ... 其他指标
  ]
}
```

**实施优先级**: 🟢 **中** - 技术指标需计算，可先展示主要指数的指标

---

#### 9. 自选股风险监控

**新增区域**: 建议在Dashboard添加"持仓风险"卡片
**建议API**:

```javascript
// 使用risk_management.py的风险评估
GET /api/v1/risk/position/assessment?user_id={user_id}
```

**显示内容**:
- 总持仓市值
- 总盈亏
- 最大回撤
- 风险等级（低/中/高）
- VaR（风险价值）

**UI组件建议**:
```vue
<ArtDecoCard title="持仓风险" hoverable>
  <div class="risk-metrics">
    <ArtDecoStatCard
      label="总市值"
      :value="riskData.totalValue + '万'"
      variant="gold"
      size="medium"
    />
    <ArtDecoStatCard
      label="总盈亏"
      :value="riskData.totalPnL + '万'"
      :change="riskData.pnlPercent"
      :variant="riskData.totalPnL > 0 ? 'rise' : 'fall'"
      change-percent
    />
    <ArtDecoStatCard
      label="最大回撤"
      :value="riskData.maxDrawdown + '%'"
      :variant="riskData.maxDrawdown < -3 ? 'fall' : 'gold'"
    />
    <div class="risk-level">
      <div class="level-label">风险等级</div>
      <div :class="['level-badge', riskData.riskLevel]">
        {{ riskData.riskLevelText }}
      </div>
    </div>
  </div>
</ArtDecoCard>
```

**实施优先级**: 🟢 **中** - 风险监控是量化交易必备功能

---

#### 10. 策略运行状态

**当前位置**: 页面头部的Badge组件
**当前状态**: Mock数据（硬编码"12策略运行中"）
**建议API**:

```javascript
// 使用strategy_mgmt.py的活跃策略
GET /api/strategy-mgmt/strategies?status=active&user_id={user_id}
```

**数据映射**:
```javascript
{
  "activeStrategies": 12,  // 实际活跃策略数量
  "todayPnL": "+8,450.20"  // 从用户持仓数据计算
}
```

**实施优先级**: 🟢 **中** - 策略状态显示真实数据

---

#### 11. 系统监控状态

**当前位置**: `monitoring-section` 区域
**当前状态**: Mock数据（硬编码系统指标）
**建议API**:

```javascript
// 使用system.py的系统健康检查
GET /api/system/health

// 使用prometheus_exporter.py的监控指标
GET /api/metrics/system
```

**数据映射**:
```javascript
{
  "monitoring": [
    {
      "label": "API响应时间",
      "value": "120ms",
      "status": "good"
    },
    {
      "label": "数据更新延迟",
      "value": "2.3s",
      "status": "warning"
    },
    {
      "label": "信号生成成功率",
      "value": "98.5%",
      "status": "good"
    },
    {
      "label": "系统CPU使用率",
      "value": "45%",
      "status": "good"
    },
    {
      "label": "内存使用率",
      "value": "67%",
      "status": "warning"
    },
    {
      "label": "数据库连接数",
      "value": "23/100",
      "status": "good"
    }
  ]
}
```

**实施优先级**: 🟢 **中** - 系统监控数据仅对开发者有用

---

### 优先级P3: 可选增强数据（未来迭代）

#### 12. 融资融券数据

**新增区域**: 建议添加"融资融券"卡片
**建议API**:

```javascript
// 使用data.py的融资融券数据
GET /api/v1/data/margin/trading?date=2026-01-20&limit=10
```

**实施优先级**: ⚪ **低** - 融资融券数据专业度较高，非必需

---

#### 13. 期货指数数据

**新增区域**: 建议添加"期货指数"卡片
**建议API**:

```javascript
// 使用data.py的期货数据
GET /api/v1/data/futures/index?limit=10
```

**实施优先级**: ⚪ **低** - 期货数据适合期货交易者

---

#### 14. 股票池表现

**当前位置**: `stock-pool-card` 区域
**当前状态**: Mock数据（自选股、策略选股）
**建议API**:

```javascript
// 方案1: 使用monitoring_watchlists.py的自选股
GET /api/monitoring/watchlist?user_id={user_id}&list=watchlist

// 方案2: 使用strategy_mgmt.py的策略选股
GET /api/strategy-mgmt/selections?strategy_id={strategy_id}
```

**实施优先级**: ⚪ **低** - 股票池数据依赖用户个人配置

---

## 🚀 实施建议

### 第一阶段: 核心市场数据（1-2天）

**目标**: 替换核心Mock数据为真实API

| 任务 | API端点 | 区域 | 优先级 |
|------|---------|------|--------|
| 主要市场指标 | `/api/market/v2/etf/list` | market-indicators | 🔴 P0 |
| 市场资金流向 | `/api/market/fund-flow` | enhanced-fund-flow | 🔴 P0 |
| 市场热度板块 | `/api/market/industry/flow` | heat-map-card | 🟡 P1 |

**预期成果**:
- ✅ 核心市场指数实时更新
- ✅ 资金流向数据真实可靠
- ✅ 板块热度动态变化

---

### 第二阶段: 交易数据增强（3-5天）

**目标**: 添加专业交易数据展示

| 任务 | API端点 | 新增区域 | 优先级 |
|------|---------|----------|--------|
| 龙虎榜数据 | `/api/market/long-hu-bang` | 龙虎榜卡片 | 🟡 P1 |
| 大宗交易 | `/api/market/v2/block-trading` | 大宗交易卡片 | 🟡 P1 |
| 资金流向排名 | `/api/monitoring/stock/flow/ranking` | capital-flow-card | 🟡 P1 |
| ETF表现 | `/api/market/v2/etf/list` | ETF表现卡片 | 🟢 P2 |

**预期成果**:
- ✅ 龙虎榜实时更新，显示活跃股票
- ✅ 大宗交易反映主力资金动向
- ✅ 资金流向排名动态刷新
- ✅ ETF数据覆盖被动投资工具

---

### 第三阶段: 技术分析与风险（1周）

**目标**: 添加技术指标和风险监控

| 任务 | API端点 | 区域 | 优先级 |
|------|---------|------|--------|
| 技术指标 | `/api/indicators/calculate/batch` | indicators-section | 🟢 P2 |
| 持仓风险 | `/api/v1/risk/position/assessment` | 持仓风险卡片 | 🟢 P2 |
| 策略状态 | `/api/strategy-mgmt/strategies` | 页面头部Badge | 🟢 P2 |
| 系统监控 | `/api/system/health` | monitoring-section | 🟢 P2 |

**预期成果**:
- ✅ 技术指标动态计算
- ✅ 持仓风险实时监控
- ✅ 策略状态真实显示
- ✅ 系统监控数据准确

---

## 📦 实施步骤

### Step 1: 创建API Service层

**文件**: `src/api/services/dashboardService.ts`

```typescript
import apiClient from '../apiClient'

/**
 * Dashboard API服务
 * 提供Dashboard页面所需的所有API端点调用
 */
export const dashboardService = {
  // 市场数据
  async getMarketOverview() {
    return apiClient.get('/api/market/v2/etf/list', {
      params: { limit: 100 }
    })
  },

  async getFundFlow(date: string) {
    return apiClient.get('/api/market/fund-flow', {
      params: { date }
    })
  },

  async getIndustryFlow(sort = 'change_percent', limit = 10) {
    return apiClient.get('/api/market/industry/flow', {
      params: { sort, limit }
    })
  },

  // 龙虎榜
  async getLongHuBang(date: string, limit = 10) {
    return apiClient.get('/api/market/long-hu-bang', {
      params: { date, limit }
    })
  },

  // 大宗交易
  async getBlockTrading(date: string, limit = 10) {
    return apiClient.get('/api/market/v2/block-trading', {
      params: { date, limit }
    })
  },

  // 个股资金流向排名
  async getStockFlowRanking(period = '1day', limit = 10) {
    return apiClient.get('/api/monitoring/stock/flow/ranking', {
      params: { period, limit }
    })
  },

  // 技术指标
  async getTechnicalIndicators(symbols: string[], indicators: string[]) {
    return apiClient.get('/api/indicators/calculate/batch', {
      params: { symbols: symbols.join(','), indicators: indicators.join(',') }
    })
  },

  // 持仓风险评估
  async getPositionRisk(userId: number) {
    return apiClient.get(`/api/v1/risk/position/assessment`, {
      params: { user_id: userId }
    })
  },

  // 策略状态
  async getActiveStrategies(userId: number) {
    return apiClient.get('/api/strategy-mgmt/strategies', {
      params: { user_id: userId, status: 'active' }
    })
  },

  // 系统监控
  async getSystemHealth() {
    return apiClient.get('/api/system/health')
  }
}
```

---

### Step 2: 更新Dashboard组件

**文件**: `src/views/artdeco-pages/ArtDecoDashboard.vue`

**修改点**:
1. 导入`dashboardService`
2. 将`marketData`等ref改为从API获取
3. 添加`onMounted`时调用API
4. 添加刷新数据函数
5. 处理加载状态和错误状态

**示例代码**:
```vue
<script setup>
import { ref, onMounted } from 'vue'
import { dashboardService } from '@/api/services/dashboardService'

// 响应式数据
const marketData = ref({
  shanghai: { index: '-', change: 0 },
  shenzhen: { index: '-', change: 0 },
  chuangye: { index: '-', change: 0 }
})

const loading = ref({
  market: false,
  fundFlow: false,
  indicators: false
})

// 获取市场概览数据
const fetchMarketOverview = async () => {
  loading.value.market = true
  try {
    const response = await dashboardService.getMarketOverview()
    // 处理ETF数据，筛选主要指数
    const etfData = response.data.data || []

    // 筛选上证、深证、创业板ETF
    const shanghaiETF = etfData.find(etf =>
      etf.symbol.startsWith('510300') || etf.symbol.startsWith('510050')
    )
    const shenzhenETF = etfData.find(etf =>
      etf.symbol.startsWith('159919') || etf.symbol.startsWith('159901')
    )
    const chuangyeETF = etfData.find(etf =>
      etf.symbol.startsWith('159915')
    )

    if (shanghaiETF) {
      marketData.value.shanghai = {
        index: shanghaiETF.latest_price,
        change: shanghaiETF.change_percent
      }
    }
    // ... 处理其他指数
  } catch (error) {
    console.error('Failed to fetch market overview:', error)
  } finally {
    loading.value.market = false
  }
}

// 页面挂载时获取数据
onMounted(() => {
  fetchMarketOverview()
  // 调用其他数据获取函数...
})
</script>
```

---

### Step 3: 添加加载状态UI

**示例**: 使用ArtDecoLoading组件

```vue
<template>
  <ArtDecoCard title="主要市场指标">
    <ArtDecoLoading v-if="loading.market" />
    <div v-else class="indicators-grid">
      <ArtDecoStatCard
        label="上证指数"
        :value="marketData.shanghai.index"
        :change="marketData.shanghai.change"
        change-percent
        variant="gold"
        size="large"
        glow
      />
      <!-- ... 其他指标 -->
    </div>
  </ArtDecoCard>
</template>
```

---

## 🎨 UI/UX优化建议

### 1. 使用数据密集样式

**目标**: 消除紧凑布局带来的留空

**方法**: 应用新创建的量化扩展令牌

```vue
<template>
  <!-- 使用紧凑统计卡片 -->
  <div class="quant-stat-card-compact">
    <div class="quant-stat-label">上证指数</div>
    <div class="quant-stat-value">3,128.45</div>
    <div class="quant-stat-change quant-up">+0.85%</div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-quant-extended.scss';
</style>
```

---

### 2. 添加实时更新动画

**目标**: 数据更新时提供视觉反馈

**方法**: 使用闪烁动画工具类

```vue
<template>
  <div
    :class="[
      'quant-data-display',
      priceChange > 0 ? 'quant-flash-up' : 'quant-flash-down'
    ]"
  >
    {{ lastPrice }}
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const lastPrice = ref(3128.45)
const priceChange = ref(0)

// 监听价格变化
watch(lastPrice, (newVal, oldVal) => {
  priceChange.value = newVal - oldVal
})
</script>
```

---

### 3. 增加数据密度

**目标**: 在有限空间内显示更多信息

**方法**: 使用3-4列网格布局

```scss
// 从2列改为3列
.content-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr); // 从1fr 1fr改为3列
  gap: var(--artdeco-dense-gap-sm); // 使用紧凑间距
}
```

---

## ✅ 验证清单

### 功能验证

- [ ] 主要市场指标实时更新（上证、深证、创业板）
- [ ] 资金流向数据正确显示（沪股通、深股通、北向资金）
- [ ] 板块热度动态刷新（前10名）
- [ ] 龙虎榜数据实时加载
- [ ] 大宗交易数据正确显示
- [ ] 资金流向排名动态更新
- [ ] 技术指标计算准确（RSI、MACD、KDJ等）
- [ ] 持仓风险评估正确
- [ ] 策略状态真实显示
- [ ] 系统监控数据准确

### UI/UX验证

- [ ] 无页面留空，数据密度合理
- [ ] 加载状态清晰（Loading组件）
- [ ] 错误处理友好（错误提示）
- [ ] 实时更新动画流畅
- [ ] 红涨绿跌颜色正确
- [ ] 等宽数字对齐
- [ ] 响应时间合理（<2秒）

### 性能验证

- [ ] API响应时间 < 500ms
- [ ] 页面首屏加载 < 2秒
- [ ] 数据刷新不阻塞UI
- [ ] 内存占用合理（<200MB）
- [ ] 无内存泄漏

---

## 📚 相关文档

### API文档
- `docs/api/reports/analysis/api_endpoints_statistics_report.md` - API统计报告
- `web/backend/app/api/dashboard.py` - Dashboard API实现
- `docs/reports/BACKEND_DASHBOARD_REAL_DATA_MIGRATION.md` - 后端迁移报告

### 前端文档
- `web/frontend/src/styles/artdeco-quant-extended.scss` - 量化扩展令牌
- `docs/reports/ARTDECO_QUANT_EXTENSION_COMPLETION_REPORT.md` - 扩展令牌报告
- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md` - ArtDeco组件目录

### 设计文档
- `docs/reports/UI_UX_DESIGN_ANALYSIS_REPORT.md` - UI/UX分析报告

---

## 🎉 总结

**Dashboard API丰富化目标**:
- ✅ 从8个Mock数据区域 → 8个真实API数据区域
- ✅ 从9个静态区域 → 13个动态数据区域（+4个新增）
- ✅ 数据密度提升2-3倍，消除留空
- ✅ 专业度提升，符合量化交易终端标准

**实施优先级**:
1. 🔴 **P0**: 主要市场指标、资金流向、板块热度
2. 🟡 **P1**: 龙虎榜、大宗交易、资金流向排名
3. 🟢 **P2**: 技术指标、风险监控、策略状态
4. ⚪ **P3**: 融资融券、期货数据、股票池

**预期成果**:
- Dashboard成为专业的量化交易指挥中心
- 所有数据实时更新，准确可靠
- 无页面留空，信息密度合理
- 用户体验流畅，性能优秀

---

**文档版本**: v1.0
**创建日期**: 2026-01-20
**最后更新**: 2026-01-20
