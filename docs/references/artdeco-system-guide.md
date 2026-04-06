# MyStocks ArtDeco Web Interface - Complete Design System

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或当前执行口径，请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，并结合当前代码实现与主线治理文档使用。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码或主线文档冲突，应以后者为准。


## 📚 Project Overview

**Project Name**: A股量化交易管理系统 - ArtDeco Edition
**Design Style**: ArtDeco Modern (几何美学 + 奢华金融)
**Pages**: 9 Core Pages
**Status**: Historical design reference snapshot; the old `Phase 1 Complete (3/9 pages fully implemented)` line describes an early design milestone, not current frontend mainline status

---

## 🎨 Design System Specifications

### Color Palette

| Category | Color Name | Hex Code | Usage |
|----------|-----------|----------|-------|
| **Backgrounds** | Global BG | `#0F1215` | Deep midnight blue-black |
| | Card BG | `#161B22` | Slightly lighter for cards |
| | Header/Sidebar | `#0A0C0E` | Ultra-dark navigation |
| **Primary** | Gold Primary | `#D4AF37` | Metallic gold for accents |
| | Gold Hover | `#F4CF57` | Highlight gold |
| | Gold Muted | `#8A7120` | Dim gold for subtle elements |
| **Secondary** | Silver Text | `#E5E4E2` | Platinum gray for primary text |
| | Silver Dim | `#8B9BB4` | Cool gray for secondary text |
| **A股 Colors** | Rise/Buy | `#C94042` | Ruby red (A股习惯: 红涨) |
| | Fall/Sell | `#3D9970` | Emerald green (A股习惯: 绿跌) |
| | Flat | `#B8B8B8` | Gray for unchanged |

### Typography

| Usage | Font | Size | Weight | Characteristics |
|-------|------|------|--------|-----------------|
| **Headers** | Cinzel / Playfair Display | Variable | 600-700 | All-caps, 2px letter-spacing |
| **Body** | Montserrat / Helvetica Neue | 14-16px | 400-500 | Clean, readable sans-serif |
| **Data/Mono** | JetBrains Mono / Source Code Pro | 12-14px | 400-600 | Monospace for numbers |
| **Display** | Cinzel (Roman numerals) | Variable | 600 | Decorative, geometric |

### Visual Elements

**Corner Decorations**:
- L-shaped brackets at card corners (16px × 16px)
- Double borders: outer 1px solid, inner 1px solid at 30% opacity
- Sharp corners (0px radius) or minimal 2px radius

**Effects**:
- Glow: `0 0 20px rgba(212, 175, 55, 0.3)` for gold elements
- Hover: `translateY(-2px)` + intensified border glow
- Pulse animation for live indicators

**Patterns**:
- Diagonal crosshatch background (repeating 45° and -45° lines)
- Opacity: 0.03 (subtle texture)
- Fixed position, z-index: 0

---

## 📄 Implemented Pages (Phase 1)

### ✅ 1. Dashboard (01-dashboard.html)

**Features**:
- Real-time market overview with 4 stat cards (上证/深证/创业板/北向资金)
- Major indices intra-day chart (ECharts line chart)
- Sector heatmap (2×2 matrix visualization)
- Limit up/down statistics (涨停/跌停/平盘)
- Data source status monitoring (AKShare/Tushare/通达信/北向)

**API Endpoints**:
```
GET /api/v1/market/overview
GET /api/v1/market/limit
GET /api/v1/fund/north_flow
GET /api/v1/sector/heatmap
WebSocket: ws://localhost:8020/ws/market/realtime
```

**Key Components**:
- `.artdeco-stats-grid` - 4-column responsive stat cards
- `.artdeco-chart-container` - ECharts integration
- `.artdeco-status` - Live status indicators with pulse animation

---

### ✅ 2. Market Center (02-market-center.html)

**Features**:
- Stock search bar (代码/名称/拼音缩写)
- Stock info panel (6 key metrics display)
- Multi-period K-line chart (1分/5分/15分/30分/60分/日线/周线/月线)
- Adjustment toggle (前复权/后复权/不复权)
- Market watch table with sorting (8 columns, click-to-sort)
- Real-time quote updates (3-second auto-refresh)

**API Endpoints**:
```
GET /api/v1/market/kline?stock_code={code}&period={period}&adjust={adjust}&limit={limit}
GET /api/v1/market/quote?stock_code={code}
GET /api/v1/market/watchlist
```

**Key Components**:
- `.artdeco-period-selector` - 8 time period buttons
- `.artdeco-kline-container` - Klinecharts professional integration
- `.artdeco-market-watch` - Sortable table with hover effects

**Chart Configuration**:
- Klinecharts v9.8.9
- Candlestick + Volume chart
- A股 colors: Red for rise, Green for fall
- Custom tooltip with ArtDeco styling

---

### ✅ 3. Stock Screener (03-stock-screener.html)

**Features**:
- 4 stock pool tabs (自选股/策略股/行业股/概念股)
- Advanced filter panel with 8 filter criteria:
  - 行业板块 (Sector)
  - 涨跌幅范围 (Change range)
  - 市值范围 (Market cap range)
  - 市盈率 PE-TTM range
  - 换手率 range
  - 成交量 range
  - 技术指标 (MACD/KDJ/RSI/BOLL)
  - 排序方式 (10+ sort options)
- Results table with 9 columns, sortable
- Pagination (20 items per page)
- Export to CSV functionality
- Add to watchlist action
- Real-time search filtering

**API Endpoints**:
```
GET /api/v1/stocks/pool?pool_type={pool}&filters={filters}
POST /api/v1/user/watchlist
DELETE /api/v1/user/watchlist/{stock_code}
```

**Key Components**:
- `.artdeco-filter-panel` - 4-column responsive filter grid
- `.artdeco-tabs` - Stock pool type switching
- `.artdeco-results-table` - Sortable, hoverable results
- `.artdeco-pagination` - Page navigation with info display

---

## 🚧 Remaining Pages (Phase 2 - Templates)

### 4. Data Analysis (04-data-analysis.html)

**Purpose**: 财务分析、多维数据关联、IC分析

**Key Features to Implement**:
- Financial statement analysis (利润表/资产负债表/现金流量表)
- Ratio analysis (ROE/ROA/毛利率/净利率)
- IC analysis (Information Coefficient for factor effectiveness)
- Multi-factor correlation heatmap
- Custom report generation

**API Endpoints**:
```
GET /api/v1/data/financial?stock_code={code}&report_type={type}
GET /api/v1/data/ratios?stock_code={code}
GET /api/v1/analysis/ic?factor={factor}&period={period}
```

**Layout Template**:
```
┌─────────────────────────────────────────────┐
│ Stock Selector + Date Range Picker         │
├─────────────────────────────────────────────┤
│                                             │
│  [Financial Statements] [Ratios] [IC]     │
│                                             │
│  ┌──────────────────┐  ┌─────────────────┐ │
│  │ Balance Sheet   │  │ Income Statement│ │
│  │ (Table)         │  │ (Table)         │ │
│  └──────────────────┘  └─────────────────┘ │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │ IC Analysis Chart (Correlation Heatmap)│  │
│  └──────────────────────────────────────┘  │
│                                             │
│  [Export Report] [Generate PDF]            │
└─────────────────────────────────────────────┘
```

---

### 5. Strategy Lab (05-strategy-lab.html)

**Purpose**: 策略开发、参数配置、模型管理

**Key Features to Implement**:
- Strategy creation wizard (step-by-step)
- Parameter optimization grid
- Backtest configuration UI
- Factor combination builder
- Strategy performance preview

**API Endpoints**:
```
GET /api/v2/strategy/list
POST /api/v2/strategy/create
PUT /api/v2/strategy/{id}/update
DELETE /api/v2/strategy/{id}
GET /api/v2/strategy/{id}/parameters
```

**Layout Template**:
```
┌─────────────────────────────────────────────┐
│ [+ New Strategy] [Import Strategy]         │
├─────────────────────────────────────────────┤
│                                             │
│  Strategy List (Card Grid)                  │
│  ┌────────┐ ┌────────┐ ┌────────┐          │
│  │Strat #1│ │Strat #2│ │Strat #3│          │
│  │Active  │ │Draft   │ │Active  │          │
│  └────────┘ └────────┘ └────────┘          │
│                                             │
│  Parameter Configuration Panel               │
│  [Factor Selector] [Weight Slider]         │
│                                             │
│  [Save] [Backtest] [Deploy]                │
└─────────────────────────────────────────────┘
```

---

### 6. Backtest Arena (06-backtest-arena.html)

**Purpose**: 历史回测、性能报告、参数优化

**Key Features to Implement**:
- Backtest job submission (date range/initial capital/slippage config)
- Real-time progress tracking
- Performance report (收益率/最大回撤/夏普比率/卡尔比率)
- Equity curve chart
- Drawdown chart
- Trade list with entry/exit details
- Parameter optimization results

**API Endpoints**:
```
POST /api/v2/backtest/run
GET /api/v2/backtest/{job_id}/status
GET /api/v2/backtest/{job_id}/report
GET /api/v2/backtest/{job_id}/trades
POST /api/v2/backtest/optimize
```

**Layout Template**:
```
┌─────────────────────────────────────────────┐
│ [Backtest Config] [Parameter Optimization] │
├─────────────────────────────────────────────┤
│                                             │
│  Date Range: [DatePicker]                   │
│  Initial Capital: [Input]                   │
│  Commission: [Input] Slippage: [Input]      │
│                                             │
│  [Run Backtest] [Stop] [Export Report]      │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │ Equity Curve Chart                  │    │
│  │ (Cumulative Returns)                │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  Performance Metrics Table                   │
│  ┌──────────────────────────────────────┐   │
│  │ Total Return | Max DD | Sharpe | ... │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  Trade List (Sortable, Filterable)          │
└─────────────────────────────────────────────┘
```

---

### 7. Trade Station (07-trade-station.html)

**Purpose**: 模拟/实盘交易、持仓管理、订单流

**Key Features to Implement**:
- Order placement panel (市价/限价/止损)
- Position management table
- Order book (level 2 market data)
- Real-time P&L calculation
- Trade history
- Account summary

**API Endpoints**:
```
GET /api/v1/trade/account
GET /api/v1/trade/positions
GET /api/v1/trade/orders
POST /api/v1/trade/order
DELETE /api/v1/trade/order/{order_id}
GET /api/v1/trade/orderbook?symbol={code}
```

**Layout Template**:
```
┌─────────────────────────────────────────────┐
│ Account: ¥1,000,000 | P&L: +¥12,345 (1.23%) │
├─────────────────────────────────────────────┤
│                                             │
│  [Place Order] [Positions] [Orders]        │
│                                             │
│  Order Entry Panel                           │
│  Stock: [Input] Price: [Input] Qty: [Input] │
│  [Buy] [Sell]                               │
│                                             │
│  Position Table                              │
│  Code | Name | Qty | Cost | Current | P&L   │
│                                             │
│  Order Book (Level 2)                        │
│  Bid | Ask | Volume                         │
└─────────────────────────────────────────────┘
```

---

### 8. Risk Center (08-risk-center.html)

**Purpose**: 账户风控、合规检查、系统日志

**Key Features to Implement**:
- Portfolio risk metrics (VaR/波动率/贝塔)
- Position concentration analysis
- Exposure breakdown by sector/style
- Risk event alerts
- Compliance checker
- System health monitoring

**API Endpoints**:
```
GET /api/v1/risk/portfolio
GET /api/v1/risk/exposure
GET /api/v1/risk/alerts
GET /api/v1/risk/compliance
GET /api/v1/monitoring/health
```

**Layout Template**:
```
┌─────────────────────────────────────────────┐
│ Risk Score: 85/100 | Status: 🟢 Low Risk    │
├─────────────────────────────────────────────┤
│                                             │
│  [Portfolio Risk] [Exposure] [Alerts]      │
│                                             │
│  Risk Metrics Card Grid                      │
│  ┌────────┐ ┌────────┐ ┌────────┐          │
│  │VaR (95%)│ │Beta    │ │Volatility│         │
│  │¥12,345 │ │1.23    │ │15.6%    │          │
│  └────────┘ └────────┘ └────────┘          │
│                                             │
│  Sector Exposure Chart (Pie/Bar)            │
│                                             │
│  Risk Alerts Table                           │
│  Time | Level | Message | Resolved         │
└─────────────────────────────────────────────┘
```

---

### 9. System Settings (09-system-settings.html)

**Purpose**: 健康监控、本地设置持久化占位、以及指向真实数据源配置入口的系统页

**Key Features to Implement**:
- Health monitor summary sourced from backend readiness / health endpoints
- Local-only page settings persistence for non-destructive UI preferences
- Explicit handoff to `System-Data` for real datasource configuration writes
- Read-only system status / diagnostics view
- Clear degraded-state messaging when no unified backend system-settings contract exists

**API Endpoints**:
```
GET /api/v1/system/settings/general
PUT /api/v1/system/settings/general
GET /api/v1/system/settings/security
PUT /api/v1/system/settings/security
GET /api/health/detailed
GET /api/health
System-Data write family: /api/v1/data-sources/config/
System-Data batch write: /api/v1/data-sources/config/batch
Notification preferences: /api/notification/preferences
```

**Current Truth Note**:
- Active route `/system/config` resolves to `web/frontend/src/views/system/Settings.vue`; `ArtDecoSystemSettings.vue` is only a thin compatibility wrapper.
- The page is no longer local-draft only: the visible CTA `保存系统设置` writes the general section through `/api/v1/system/settings/general`.
- The settings truth is sectioned rather than monolithic. Do not invent a single unified `/api/system/settings` or `/api/v1/system/config` API as a parallel truth source.
- Datasource and notification writes remain with their canonical owner contracts instead of being folded into a duplicate merged store.

**Layout Template**:
```
┌─────────────────────────────────────────────┐
│ [Sectioned Settings] [Health Monitor] [Go to System-Data] │
├─────────────────────────────────────────────┤
│                                             │
│  Health / Status Table                       │
│  Source | Status | Latency | Last Update   │
│                                             │
│  General Section Form                        │
│  [Theme Toggle] [Notification Toggle]       │
│                                             │
│  Backend Save CTA                            │
│  [保存系统设置]                              │
│                                             │
│  Routed Section Owners                       │
│  security / datasource / notification        │
└─────────────────────────────────────────────┘
```

---

## 🛠️ Component Library

### Buttons

```html
<!-- Primary Button -->
<button class="artdeco-btn artdeco-btn-primary">提交</button>

<!-- Secondary Button -->
<button class="artdeco-btn artdeco-btn-secondary">取消</button>

<!-- Rise Button (A股 Red) -->
<button class="artdeco-btn artdeco-btn-rise">买入</button>

<!-- Fall Button (A股 Green) -->
<button class="artdeco-btn artdeco-btn-fall">卖出</button>
```

### Cards

```html
<div class="artdeco-card">
  <h3>Card Title</h3>
  <p>Card content with ArtDeco double border styling...</p>
</div>
```

### Tables

```html
<table class="artdeco-table">
  <thead>
    <tr>
      <th>Column 1</th>
      <th>Column 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Data 1</td>
      <td>Data 2</td>
    </tr>
  </tbody>
</table>
```

### Badges

```html
<span class="artdeco-badge artdeco-badge-gold">Gold</span>
<span class="artdeco-badge artdeco-badge-rise">Rise</span>
<span class="artdeco-badge artdeco-badge-fall">Fall</span>
```

### Status Indicators

```html
<div class="artdeco-status">
  <span class="artdeco-status-dot online"></span>
  <span>在线</span>
</div>
```

---

## 📊 Chart Integration

### ECharts Configuration

```javascript
const option = {
  backgroundColor: 'transparent',
  tooltip: {
    backgroundColor: 'rgba(15, 18, 21, 0.95)',
    borderColor: '#D4AF37',
    borderWidth: 1,
    textStyle: {
      color: '#E5E4E2',
      fontFamily: 'JetBrains Mono'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    axisLine: { lineStyle: { color: '#5C6B7F' } },
    axisLabel: { color: '#8B9BB4', fontFamily: 'JetBrains Mono' }
  },
  yAxis: {
    axisLine: { lineStyle: { color: '#5C6B7F' } },
    axisLabel: { color: '#8B9BB4', fontFamily: 'JetBrains Mono' },
    splitLine: {
      lineStyle: { color: 'rgba(212, 175, 55, 0.1)', type: 'dashed' }
    }
  }
};
```

### Klinecharts Configuration

```javascript
klineChart.createChart('candle-solid', {
  styles: {
    candle: {
      type: 'candle-solid',
      bar: {
        upColor: '#C94042',    // A股 Red
        downColor: '#3D9970',  // A股 Green
        noChangeColor: '#888888'
      },
      tooltip: {
        text: {
          color: '#D4AF37',
          family: 'JetBrains Mono'
        }
      }
    }
  }
});
```

---

## 🔌 API Integration Guide

### Base Configuration

```javascript
const API_BASE_URL = '/api/v1';
const API_V2_URL = '/api/v2';
const WS_BASE_URL = 'ws://localhost:8020/ws/market/realtime';
```

### Standard Fetch Pattern

```javascript
async function fetchData(endpoint, params = {}) {
  try {
    const queryParams = new URLSearchParams(params);
    const url = `${API_BASE_URL}/${endpoint}?${queryParams}`;

    const response = await fetch(url);
    if (!response.ok) throw new Error('API请求失败');

    return await response.json();
  } catch (error) {
    console.error(`${endpoint} 请求失败:`, error);
    return getMockData(endpoint); // Fallback to mock data
  }
}
```

### WebSocket Connection

```javascript
function initWebSocket() {
  const ws = new WebSocket(WS_BASE_URL);

  ws.onopen = () => console.log('WebSocket连接成功');
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleRealtimeUpdate(data);
  };
  ws.onerror = (error) => console.error('WebSocket错误:', error);
  ws.onclose = () => {
    console.log('WebSocket连接关闭，5秒后重连...');
    setTimeout(initWebSocket, 5000);
  };
}
```

---

## 📁 File Structure

```
artdeco-system/
├── assets/
│   └── css/
│       └── artdeco-theme.css          # Core theme file
├── 01-dashboard.html                  # ✅ Complete
├── 02-market-center.html              # ✅ Complete
├── 03-stock-screener.html             # ✅ Complete
├── 04-data-analysis.html              # 🚧 Template
├── 05-strategy-lab.html               # 🚧 Template
├── 06-backtest-arena.html             # 🚧 Template
├── 07-trade-station.html              # 🚧 Template
├── 08-risk-center.html                # 🚧 Template
├── 09-system-settings.html            # 🚧 Template
└── README.md                           # This file
```

---

## 🎯 Implementation Priority

### Phase 1 (Complete) ✅
1. Dashboard - Market overview and monitoring
2. Market Center - Real-time quotes and K-line charts
3. Stock Screener - Advanced filtering and sorting

### Phase 2 (High Priority) 🚧
4. Data Analysis - Financial analysis and IC analysis
5. Strategy Lab - Strategy development and parameter tuning
6. Backtest Arena - Historical backtesting and performance reports

### Phase 3 (Medium Priority) 📋
7. Trade Station - Order management and position tracking
8. Risk Center - Portfolio risk and compliance monitoring

### Phase 4 (Lower Priority) 📝
9. System Settings - Configuration and user management

---

## 🔧 Development Workflow

### Adding a New Page

1. **Copy Template**:
   ```bash
   cp 03-stock-screener.html 04-data-analysis.html
   ```

2. **Update Navigation**:
   - Change page title
   - Update breadcrumb
   - Set active nav item

3. **Implement Features**:
   - Add API calls in `<script>` section
   - Create page-specific CSS
   - Build HTML structure using component library

4. **Test Integration**:
   - Verify API endpoints
   - Check responsive layout
   - Test with real data

### Updating the Theme

All theme variables are in `artdeco-theme.css`:

```css
:root {
  /* Modify these to change colors */
  --artdeco-bg-global: #0F1215;
  --artdeco-gold-primary: #D4AF37;
  --artdeco-rise: #C94042;
  --artdeco-fall: #3D9970;

  /* Modify these to change fonts */
  --artdeco-font-display: 'Cinzel', serif;
  --artdeco-font-body: 'Montserrat', sans-serif;
  --artdeco-font-mono: 'JetBrains Mono', monospace;
}
```

---

## 📱 Responsive Breakpoints

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Desktop | >1440px | 4-column grids |
| Laptop | 1080px - 1440px | 2-column grids |
| Tablet | 768px - 1080px | 1-column grids, sidebar hidden |
| Mobile | <768px | Single column, topbar search hidden |

---

## 🚀 Performance Optimization

### Loading Strategy

1. **Lazy Load Charts**: Initialize charts only when tab/page is visible
2. **Debounce Search**: 300ms delay for search input
3. **Virtual Scrolling**: For tables with >1000 rows
4. **WebSocket Throttling**: Batch updates every 3 seconds max

### Caching Strategy

```javascript
const cache = new Map();

async function cachedFetch(url, ttl = 3000) {
  const cached = cache.get(url);
  if (cached && Date.now() - cached.timestamp < ttl) {
    return cached.data;
  }

  const data = await fetch(url).then(r => r.json());
  cache.set(url, { data, timestamp: Date.now() });
  return data;
}
```

---

## 📚 Resources

### Design Inspiration
- [ArtDeco Design Guide](./ArtDeco.md)
- [UI/UX Pro Max Skill](../../../.claude/skills/ui-ux-pro-max/SKILL.md)

### Technical Documentation
- [ECharts Documentation](https://echarts.apache.org/en/option.html)
- [Klinecharts Documentation](https://klinechart.org/)
- [FastAPI Backend](../../../../web/backend/app/api/VERSION_MAPPING.py)

### Fonts
- [Cinzel (Display)](https://fonts.google.com/specimen/Cinzel)
- [Montserrat (Body)](https://fonts.google.com/specimen/Montserrat)
- [JetBrains Mono (Data)](https://fonts.google.com/specimen/JetBrains+Mono)

---

## ✨ Design Philosophy

**"Form Follows Function"**

This ArtDeco-styled interface achieves:
- ✅ **Luxurious Aesthetics**: Metallic gold accents, geometric patterns
- ✅ **Professional Data Display**: Monospace fonts for numbers, high contrast
- ✅ **Efficient Workflow**: Responsive layout, real-time updates, fast filtering
- ✅ **A股 Native**: Red for rise, green for fall, 100-share lots
- ✅ **Accessibility**: WCAG AA compliant contrast ratios

---

## 🎓 Acknowledgments

**Design System**: ArtDeco Modern (1920s geometric aesthetics meets modern fintech)
**Implementation**: Claude Code Frontend Design Specialist
**Project**: MyStocks A股量化交易管理系统

**Version**: 1.0.0
**Last Updated**: 2025-01-03
**Status**: ✅ Phase 1 Complete | 🚧 Phase 2 In Progress
