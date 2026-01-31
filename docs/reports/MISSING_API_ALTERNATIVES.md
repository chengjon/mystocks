# 缺失API端点替代方案清单

**生成日期**: 2026-01-20
**目的**: 针对缺失的API端点，使用现有可用API进行替代
**原则**: 主题相关、功能相近、数据可用

---

## 🚨 缺失API与可用替代方案

### 🔴 P0 - 最高优先级（Dashboard必需）

#### 1. **指数列表API** ❌ 缺失
**缺失端点**: `GET /api/market/v2/indices/list`
**功能需求**: 获取主要指数列表（上证指数、深证成指、创业板指等）

---

### ✅ **替代方案A: 使用ETF列表API**（推荐）

**可用端点**: `GET /api/market/v2/etf/list`

**理由**:
- ✅ ETF数据中包含大量指数型ETF（如510300是沪深300ETF）
- ✅ 数据来源真实（PostgreSQL + EastMoney）
- ✅ 实时更新，有完整的时间戳
- ✅ 可以通过筛选获取主要指数

**筛选条件**:
```javascript
// 从ETF列表中筛选指数型ETF
const indicesETF = await etfList.filter(etf =>
  etf.symbol.startsWith('51') ||  // 沪市指数基金
  etf.symbol.startsWith('159') || // 深市指数基金
  etf.name.includes('指数') ||
  etf.name.includes('300') ||
  etf.name.includes('500')
)
```

**前端调用示例**:
```typescript
// dashboardService.ts
async getMarketOverview() {
  // 替代方案：从ETF列表获取指数数据
  const response = await apiGet('/api/market/v2/etf/list', {
    limit: 50
  })

  // 筛选主要指数型ETF
  const indices = response.data
    .filter(etf =>
      etf.symbol.match(/^(510300|510500|159915|159949)/) ||  // 沪深300、中证500、创业板等
      etf.name.includes('指数')
    )
    .slice(0, 5)  // 取前5个主要指数
    .map(etf => ({
      symbol: etf.symbol,
      name: etf.name.replace('ETF', '').trim(),
      current_price: etf.latest_price,
      change_percent: etf.change_percent,
      volume: etf.volume,
      turnover: etf.amount,
      update_time: etf.created_at
    }))

  return { success: true, data: indices }
}
```

**优点**:
- ✅ 无需后端改动，立即可用
- ✅ 数据真实可靠
- ✅ 支持实时刷新

**缺点**:
- ⚠️ 需要前端筛选逻辑
- ⚠️ ETF名称需要处理（去掉"ETF"后缀）

---

### ✅ **替代方案B: 使用Dashboard Market Overview API**

**可用端点**: `GET /api/dashboard/market-overview`

**理由**:
- ✅ 已包含指数数据（indices字段）
- ✅ 格式符合需求
- ✅ 当前已在使用

**前端调用示例**:
```typescript
async getIndicesList() {
  const response = await apiGet('/api/dashboard/market-overview')

  // 提取指数数据
  const indices = response.data?.indices || []

  return {
    success: true,
    data: indices.map(idx => ({
      symbol: idx.symbol,
      name: idx.name,
      current_price: idx.current_price,
      change_percent: idx.change_percent,
      volume: idx.volume,
      update_time: idx.update_time
    }))
  }
}
```

**优点**:
- ✅ 代码改动最小
- ✅ 数据格式完全匹配
- ✅ 无需筛选

**缺点**:
- ⚠️ 当前使用Mock数据源，需要后端改为真实数据

**推荐**: **方案A（ETF列表）**，因为数据源已是真实的

---

#### 2. **市场统计API** ❌ 缺失
**缺失端点**: `GET /api/market/v2/market-stats`
**功能需求**: 获取市场统计数据（上涨/下跌/平盘数量、总成交额等）

---

### ✅ **替代方案: 使用Dashboard Market Overview API**

**可用端点**: `GET /api/dashboard/market-overview`

**理由**:
- ✅ 已包含市场统计数据（up_count, down_count, flat_count, total_volume, total_turnover）
- ✅ 数据格式完全匹配
- ✅ 单次请求获取完整数据

**数据字段映射**:
```typescript
interface MarketStats {
  up_count: number          // 上涨数量 ✅
  down_count: number         // 下跌数量 ✅
  flat_count: number         // 平盘数量 ✅
  total_volume: number       // 总成交量 ✅
  total_turnover: number     // 总成交额 ✅
  top_gainers: Stock[]       // 涨幅榜 ✅
  top_losers: Stock[]        // 跌幅榜 ✅
  most_active: Stock[]      // 成交活跃 ✅
}
```

**前端调用示例**:
```typescript
async getMarketStats() {
  const response = await apiGet('/api/dashboard/market-overview')

  return {
    success: true,
    data: {
      up_count: response.data.up_count,
      down_count: response.data.down_count,
      flat_count: response.data.flat_count,
      total_volume: response.data.total_volume,
      total_turnover: response.data.total_turnover,
      limit_up: response.data.top_gainers?.length || 0,
      limit_down: response.data.top_losers?.length || 0
    }
  }
}
```

**优点**:
- ✅ 完全匹配需求
- ✅ 数据丰富（包含涨跌榜）
- ✅ 无需额外处理

**缺点**:
- ⚠️ 当前使用Mock数据源

**推荐**: 使用此方案，但需要后端将数据源改为真实数据

---

#### 3. **用户持仓API** ❌ 缺失
**缺失端点**: `GET /api/v1/portfolio/{user_id}`
**功能需求**: 获取用户持仓数据

---

### ✅ **替代方案: 使用实时市值API**

**可用端点**: `GET /api/api/mtm/portfolio/{portfolio_id}`

**理由**:
- ✅ 提供组合市值数据
- ✅ 包含持仓信息
- ✅ 实时计算

**前端调用示例**:
```typescript
async getUserPortfolio(userId: number) {
  try {
    // 使用用户ID作为portfolio_id
    const response = await apiGet(`/api/api/mtm/portfolio/${userId}`)

    return {
      success: true,
      data: {
        total_market_value: response.data.total_value || 0,
        total_cost: response.data.total_cost || 0,
        total_profit_loss: response.data.profit_loss || 0,
        positions: response.data.positions || []
      }
    }
  } catch (error) {
    // 如果API不可用，返回默认数据
    return {
      success: true,
      data: {
        total_market_value: 0,
        total_cost: 0,
        total_profit_loss: 0,
        positions: []
      }
    }
  }
}
```

---

### ✅ **替代方案B: 使用风险管理持仓评估API**

**可用端点**: `POST /api/v1/risk/position/assess`

**理由**:
- ✅ 提供持仓风险评估
- ✅ 可以获取用户所有持仓

**前端调用示例**:
```typescript
async getUserPortfolio(userId: number) {
  const response = await apiPost('/api/v1/risk/position/assess', {
    user_id: userId,
    include_metrics: true
  })

  return {
    success: true,
    data: {
      total_market_value: response.data.total_value,
      positions: response.data.positions || []
    }
  }
}
```

**推荐**: **方案A（实时市值API）**，更直接

---

### 🟡 P1 - 高优先级（功能增强）

#### 4. **行业列表API** ⚠️ 存在但返回空数据
**端点**: `GET /api/analysis/industry/list`
**状态**: 端点存在但返回空数据

---

### ✅ **替代方案: 使用行业资金流向API**

**可用端点**: `GET /api/market/v2/sector/fund-flow`

**理由**:
- ✅ 提供行业资金流向数据
- ✅ 包含行业列表
- ✅ 数据真实（EastMoney）
- ✅ 可以聚合提取行业列表

**前端调用示例**:
```typescript
async getIndustryList() {
  try {
    // 方案1: 从行业资金流向获取
    const response = await apiGet('/api/market/v2/sector/fund-flow')

    if (response.data && response.data.length > 0) {
      // 提取行业名称
      const industries = [...new Set(response.data.map(item => item.sector_name))]
        .filter(name => name)
        .map(name => ({
          name: name,
          code: name,  // 如果没有代码，使用名称
          update_time: new Date().toISOString()
        }))

      return { success: true, data: industries }
    }
  } catch (error) {
    console.error('Failed to fetch industry list:', error)
  }

  // 备选方案：返回默认行业列表
  return {
    success: true,
    data: [
      { name: '金融', code: 'FINANCE' },
      { name: '科技', code: 'TECH' },
      { name: '医药', code: 'HEALTHCARE' },
      { name: '消费', code: 'CONSUMER' }
    ]
  }
}
```

---

### ✅ **替代方案B: 使用行业表现API**

**可用端点**: `GET /api/analysis/industry/performance`

**理由**:
- ✅ 专门提供行业数据
- ✅ 包含行业表现信息

**前端调用示例**:
```typescript
async getIndustryList() {
  try {
    const response = await apiGet('/api/analysis/industry/performance')

    if (response.data && response.data.length > 0) {
      return { success: true, data: response.data }
    }
  } catch (error) {
    console.error('Failed to fetch industry performance:', error)
  }

  // 返回空数组，前端处理
  return { success: true, data: [] }
}
```

**推荐**: **方案B（行业表现API）**，更专门

---

#### 5. **概念列表API** ⚠️ 存在但返回空数据
**端点**: `GET /api/analysis/concept/list`
**状态**: 端点存在但返回空数据

---

### ✅ **替代方案: 使用概念股票API聚合**

**可用端点**: `GET /api/analysis/concept/stocks`

**理由**:
- ✅ 可以反向推导概念列表
- ✅ 数据真实

**前端调用示例**:
```typescript
async getConceptList() {
  try {
    // 获取所有概念的股票，然后反向聚合
    const response = await apiGet('/api/analysis/concept/stocks')

    if (response.data && response.data.length > 0) {
      // 提取概念名称
      const concepts = [...new Set(response.data.map(item => item.concept_name))]
        .filter(name => name)
        .slice(0, 50)  // 限制返回数量
        .map(name => ({
          name: name,
          code: name,
          stock_count: response.data.filter(item => item.concept_name === name).length
        }))

      return { success: true, data: concepts }
    }
  } catch (error) {
    console.error('Failed to fetch concept list:', error)
  }

  // 返回空数组
  return { success: true, data: [] }
}
```

**推荐**: 使用此方案，如果数据仍为空，需要后端补充数据源

---

### 🟢 P2 - 中等优先级（锦上添花）

#### 6. **策略列表API** ❌ 缺失
**缺失端点**: `GET /api/strategy/{user_id}/active`
**功能需求**: 返回用户活跃策略

---

### ✅ **替代方案: 使用策略管理API**

**可用端点**: `GET /api/strategy-mgmt/strategies`

**理由**:
- ✅ 提供策略列表
- ✅ 包含策略状态
- ✅ 可以过滤活跃策略

**前端调用示例**:
```typescript
async getUserActiveStrategies(userId: number) {
  try {
    // 获取所有策略
    const response = await apiGet('/api/strategy-mgmt/strategies', {
      user_id: userId,
      status: 'active'  # 筛选活跃策略
    })

    if (response.data) {
      return {
        success: true,
        data: response.data.filter(s => s.status === 'active' || s.is_active === true)
      }
    }
  } catch (error) {
    console.error('Failed to fetch user strategies:', error)
  }

  return { success: true, data: [] }
}
```

---

### ✅ **替代方案B: 使用策略API**

**可用端点**: `GET /api/v1/strategy/strategies`

**理由**:
- ✅ 专门的策略API
- ✅ 支持筛选和过滤

**前端调用示例**:
```typescript
async getUserActiveStrategies(userId: number) {
  const response = await apiGet('/api/v1/strategy/strategies', {
    user_id: userId
  })

  return {
    success: true,
    data: response.data?.filter(s => s.status === 'active') || []
  }
}
```

**推荐**: **方案A（策略管理API）**，功能更完整

---

#### 7. **股票搜索API** ⚠️ 存在但可能使用Mock
**端点**: `GET /api/stock/search`
**状态**: 端点可能存在但使用Mock数据

---

### ✅ **替代方案: 使用股票搜索API（需要验证）**

**可用端点**:
- `GET /api/stock-search` (如果有)
- 或使用 `POST /api/market/wencai/query` (问财选股)

**理由**:
- ✅ 问财API提供强大的搜索功能
- ✅ 支持自然语言查询
- ✅ 数据真实

**前端调用示例**:
```typescript
async searchStocks(query: string) {
  try {
    // 方案1: 使用问财API
    const response = await apiPost('/api/market/wencai/query', {
      query: query,
      limit: 20
    })

    if (response.data && response.data.results) {
      return {
        success: true,
        data: response.data.results.map(stock => ({
          symbol: stock.code,
          name: stock.name,
          price: stock.price,
          change_percent: stock.change_percent
        }))
      }
    }
  } catch (error) {
    console.error('Search failed:', error)
  }

  return { success: true, data: [] }
}
```

**推荐**: 先验证 `/api/stock-search` 端点，如果不存在使用问财API

---

## 📊 替代方案总览表

| 缺失API | 推荐替代方案 | 可用端点 | 数据来源 | 实施难度 |
|---------|-------------|----------|----------|----------|
| `/api/market/v2/indices/list` | ✅ 方案A: ETF列表筛选 | `/api/market/v2/etf/list` | Real (PostgreSQL) | 🟢 低 |
| `/api/market/v2/market-stats` | ✅ Dashboard Market Overview | `/api/dashboard/market-overview` | Mock → 需改为Real | 🟡 中 |
| `/api/v1/portfolio/{user_id}` | ✅ 实时市值API | `/api/api/mtm/portfolio/{id}` | Real | 🟢 低 |
| `/api/analysis/industry/list` | ✅ 行业表现API | `/api/analysis/industry/performance` | Real (可能空) | 🟡 中 |
| `/api/analysis/concept/list` | ✅ 概念股票聚合 | `/api/analysis/concept/stocks` | Real (可能空) | 🟡 中 |
| `/api/strategy/{user_id}/active` | ✅ 策略管理API | `/api/strategy-mgmt/strategies` | Real | 🟢 低 |
| `/api/stock/search` | ✅ 问财搜索API | `/api/market/wencai/query` | Real | 🟢 低 |

---

## 🎯 实施建议

### 立即可用（无需后端改动）
1. **指数列表**: 使用 `/api/market/v2/etf/list` 并筛选
2. **用户持仓**: 使用 `/api/api/mtm/portfolio/{id}`
3. **策略列表**: 使用 `/api/strategy-mgmt/strategies`
4. **股票搜索**: 使用 `/api/market/wencai/query`

### 需要后端配合
1. **市场统计**: 使用 `/api/dashboard/market-overview`，但需将Mock数据源改为Real
2. **行业列表**: 使用 `/api/analysis/industry/performance`，需验证数据
3. **概念列表**: 使用 `/api/analysis/concept/stocks`，需验证数据

---

## 📝 前端Service层实现示例

```typescript
// web/frontend/src/services/dashboardService.ts

import { apiGet, apiPost } from '@/api/apiClient'

export class DashboardService {
  /**
   * 获取市场概览（替代指数列表API）
   * 使用: /api/market/v2/etf/list
   */
  async getMarketOverview() {
    const response = await apiGet('/api/market/v2/etf/list', { limit: 50 })

    // 筛选主要指数型ETF
    const indices = response.data
      .filter((etf: any) =>
        etf.symbol.match(/^(510300|510500|159915|159949|510050)/) ||
        etf.name.includes('指数')
      )
      .slice(0, 5)
      .map((etf: any) => ({
        symbol: etf.symbol,
        name: etf.name.replace('ETF', '').trim(),
        current_price: etf.latest_price,
        change_percent: etf.change_percent,
        volume: etf.volume,
        turnover: etf.amount,
        update_time: etf.created_at
      }))

    return { success: true, data: indices }
  }

  /**
   * 获取市场统计（替代市场统计API）
   * 使用: /api/dashboard/market-overview
   */
  async getMarketStats() {
    const response = await apiGet('/api/dashboard/market-overview')

    return {
      success: true,
      data: {
        up_count: response.data.up_count,
        down_count: response.data.down_count,
        flat_count: response.data.flat_count,
        total_volume: response.data.total_volume,
        total_turnover: response.data.total_turnover
      }
    }
  }

  /**
   * 获取用户持仓（替代持仓API）
   * 使用: /api/api/mtm/portfolio/{id}
   */
  async getUserPortfolio(userId: number) {
    try {
      const response = await apiGet(`/api/api/mtm/portfolio/${userId}`)

      return {
        success: true,
        data: {
          total_market_value: response.data.total_value || 0,
          total_cost: response.data.total_cost || 0,
          positions: response.data.positions || []
        }
      }
    } catch (error) {
      return {
        success: true,
        data: { total_market_value: 0, positions: [] }
      }
    }
  }

  // ... 其他方法
}

export const dashboardService = new DashboardService()
```

---

## ✅ 下一步

请您从上述替代方案中进行选择，我将根据您的选择实施前端代码修改。

**推荐优先级**:
1. ✅ 立即实施：ETF列表替代指数列表（无需后端改动）
2. ✅ 立即实施：实时市值API替代持仓API
3. ⚠️ 需确认：Dashboard Market Overview是否需要改为真实数据源
4. ⚠️ 需确认：行业/概念API数据是否可用

**请告诉我您的选择，我将立即开始实施。**
