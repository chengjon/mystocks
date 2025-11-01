# MyStocks Web端页面结构详细文档

**文档版本**: v1.0
**创建日期**: 2025-10-20
**适用范围**: MyStocks量化交易数据管理系统 Web前端

---

## 📋 目录结构

- [1. 登录页面](#1-登录页面)
- [2. 仪表盘页面](#2-仪表盘页面)
- [3. 市场行情页面](#3-市场行情页面)
- [4. TDX行情页面](#4-tdx行情页面)
- [5. 市场数据模块](#5-市场数据模块)
  - [5.1 资金流向](#51-资金流向)
  - [5.2 ETF行情](#52-etf行情)
  - [5.3 竞价抢筹](#53-竞价抢筹)
  - [5.4 龙虎榜](#54-龙虎榜)
  - [5.5 问财筛选](#55-问财筛选)
- [6. 股票管理页面](#6-股票管理页面)
- [7. 数据分析页面](#7-数据分析页面)
- [8. 技术分析页面](#8-技术分析页面)
- [9. 指标库页面](#9-指标库页面)
- [10. 风险监控页面](#10-风险监控页面)
- [11. 交易管理页面](#11-交易管理页面)
- [12. 策略管理页面](#12-策略管理页面)
- [13. 回测分析页面](#13-回测分析页面)
- [14. 任务管理页面](#14-任务管理页面)
- [15. 系统设置页面](#15-系统设置页面)

---

## 1. 登录页面

**路由**: `/login`
**组件**: `src/views/Login.vue`
**认证状态**: 无需认证

### 页面容器

| 容器名称 | 容器类型 | 位置 | 用途 |
|---------|---------|------|------|
| `login-container` | div | 页面主容器 | 登录页面整体布局 |
| `login-form-card` | el-card | 居中 | 登录表单卡片 |

### 交互元素

| 元素名称 | 元素类型 | 位置 | 功能 | 数据源 |
|---------|---------|------|------|--------|
| 用户名输入框 | el-input | 表单顶部 | 输入用户名 | 本地输入 |
| 密码输入框 | el-input | 用户名下方 | 输入密码（type=password） | 本地输入 |
| 记住我复选框 | el-checkbox | 密码框下方 | 记住登录状态 | 本地状态 |
| 登录按钮 | el-button | 表单底部 | 提交登录请求 | - |

### API调用

```javascript
POST /api/auth/login
Body: username=admin&password=admin123 (x-www-form-urlencoded)
Response: { access_token, token_type, expires_in, user }
```

### 数据流

1. 用户输入 → 表单验证
2. 点击登录 → 调用`authApi.login()`
3. 成功 → 保存token到localStorage → 跳转到仪表盘
4. 失败 → 显示错误提示

---

## 2. 仪表盘页面

**路由**: `/` 或 `/dashboard`
**组件**: `src/views/Dashboard.vue`
**认证状态**: 需要登录

### 页面布局结构

```
仪表盘
├── 统计卡片区（第一行）
│   ├── 总股票数卡片
│   ├── 活跃股票卡片
│   ├── 数据更新卡片
│   └── 系统状态卡片
├── 图表区（第二行）
│   ├── 市场热度中心卡片（左侧，占16列）
│   │   ├── Tab: 市场热度
│   │   ├── Tab: 领涨板块
│   │   ├── Tab: 涨跌分布
│   │   └── Tab: 资金流向
│   └── 行业资金流向卡片（右侧，占8列）
│       └── 行业分类选择器
└── 板块表现区（第三行）
    ├── Tab: 自选股
    ├── Tab: 策略选股
    ├── Tab: 行业选股
    └── Tab: 概念选股
```

### 页面容器详情

#### 2.1 统计卡片区

| 容器名称 | 容器类型 | Grid布局 | 用途 |
|---------|---------|---------|------|
| `stats-row` | el-row | gutter:20 | 统计数据卡片行容器 |
| `stat-card` | el-card | xs:24, sm:12, md:6 | 单个统计卡片 |

**统计卡片内容**:

| 卡片标题 | 显示值 | 趋势指标 | 图标 | 颜色 | 数据源 |
|---------|--------|---------|------|------|--------|
| 总股票数 | 动态获取 | 较昨日 +0 | TrendCharts | 蓝色 | `GET /api/market/stocks` |
| 活跃股票 | 0（模拟） | 较昨日 +0 | DataLine | 绿色 | 模拟数据 |
| 数据更新 | 0（模拟） | 今日更新 | Refresh | 橙色 | 模拟数据 |
| 系统状态 | 正常 | 所有服务运行中 | CircleCheck | 绿色 | 模拟数据 |

#### 2.2 市场热度中心

| 容器名称 | 容器类型 | 尺寸 | 用途 |
|---------|---------|------|------|
| `market-tabs` | el-tabs | - | 市场数据Tab容器 |
| `marketHeatChartRef` | div | 350px高 | 市场热度图表容器 |
| `leadingSectorChartRef` | div | 350px高 | 领涨板块图表容器 |
| `priceDistributionChartRef` | div | 350px高 | 涨跌分布图表容器 |
| `capitalFlowChartRef` | div | 350px高 | 资金流向图表容器 |

**Tab页签内容**:

| Tab名称 | 图表类型 | X轴 | Y轴 | 数据来源 |
|---------|----------|-----|-----|----------|
| 市场热度 | 横向柱状图 | 热度指数 | 概念板块 | 模拟数据（人工智能、新能源车等） |
| 领涨板块 | 横向柱状图 | 涨幅(%) | 板块名称 | 模拟数据（8个板块） |
| 涨跌分布 | 饼图 | - | - | 模拟数据（涨停、上涨、平盘、下跌、跌停） |
| 资金流向 | 横向柱状图 | 资金流向(亿元) | 单据类型 | 模拟数据（超大单、大单、中单、小单） |

#### 2.3 行业资金流向

| 容器名称 | 容器类型 | 尺寸 | 用途 |
|---------|---------|------|------|
| `industryChartRef` | div | 400px高 | 行业资金流向图表 |
| 行业分类选择器 | el-select | 120px宽 | 切换行业分类标准 |

**行业分类选项**:

| 选项值 | 选项标签 | 数据维度 |
|--------|---------|----------|
| `csrc` | 证监会 | 8个行业（金融业、房地产业等） |
| `sw_l1` | 申万一级 | 8个行业（计算机、电子等） |
| `sw_l2` | 申万二级 | 8个行业（半导体、光学光电子等） |

#### 2.4 板块表现区

| Tab名称 | 表格列 | 数据量 | 数据来源 |
|---------|--------|--------|----------|
| 自选股 | 代码、名称、现价、涨跌幅、成交量、换手率、所属行业 | 5条 | 模拟数据 |
| 策略选股 | 代码、名称、现价、涨跌幅、策略名称、评分、信号 | 5条 | 模拟数据 |
| 行业选股 | 代码、名称、现价、涨跌幅、所属行业、行业排名、市值 | 5条 | 模拟数据（白酒行业） |
| 概念选股 | 代码、名称、现价、涨跌幅、热门概念、概念热度 | 5条 | 模拟数据 |

### 交互元素

| 元素名称 | 元素类型 | 位置 | 功能 | API调用 |
|---------|---------|------|------|---------|
| 刷新按钮 | el-button | 板块表现卡片头部 | 刷新数据 | `dataApi.getStocksBasic()` |
| Tab切换器 | el-tabs | 各图表区域 | 切换不同视图 | - |
| 行业标准选择器 | el-select | 资金流向卡片头部 | 切换行业分类 | - |

### 图表库

- **ECharts 5.x**: 用于所有图表渲染
- **图表自适应**: 监听window resize事件

### 数据模型

```javascript
// 统计数据
stats = [
  { title, value, trend, trendClass, icon, color }
]

// 自选股数据
favoriteStocks = [
  { symbol, name, price, change, volume, turnover, industry }
]

// 策略选股数据
strategyStocks = [
  { symbol, name, price, change, strategy, score, signal }
]

// 行业数据
industryData = {
  csrc: { categories: [], values: [] },
  sw_l1: { categories: [], values: [] },
  sw_l2: { categories: [], values: [] }
}
```

---

## 3. 市场行情页面

**路由**: `/market`
**组件**: `src/views/Market.vue`
**认证状态**: 需要登录
**当前状态**: ⚠️ 功能开发中

### 页面结构

```
市场行情
└── 提示卡片
    └── "功能开发中..." (el-empty)
```

### 页面容器

| 容器名称 | 容器类型 | 内容 |
|---------|---------|------|
| `market-container` | div | 主容器 |
| `market-card` | el-card | 空状态卡片 |

### 交互元素

| 元素名称 | 元素类型 | 位置 | 功能 | 状态 |
|---------|---------|------|------|------|
| 刷新按钮 | el-button | 卡片头部右侧 | 刷新数据 | 未实现 |

**建议扩展**:
- 实时行情表格
- 市场概览
- 热点板块
- 涨跌幅榜单

---

## 4. TDX行情页面

**路由**: `/tdx-market`
**组件**: `src/views/TdxMarket.vue`
**认证状态**: 需要登录

### 页面布局结构

```
TDX行情
├── 指数监控面板（顶部）
│   ├── 上证指数
│   ├── 深证成指
│   ├── 创业板指
│   └── 科创50
├── 左侧列（8列宽）
│   └── 实时行情卡片
│       ├── 股票搜索框
│       ├── 当前股票行情
│       └── 详细数据表格
└── 右侧列（16列宽）
    └── K线图卡片
        ├── 周期选择器
        ├── K线图表区域
        └── 成交量图表区域
```

### 页面容器详情

#### 4.1 指数监控面板

| 容器名称 | 容器类型 | 样式 | 用途 |
|---------|---------|------|------|
| `index-monitor` | el-card | shadow:never | 指数监控卡片 |
| `index-list` | div | flex布局 | 指数列表容器 |
| `index-item` | div | 可点击 | 单个指数项 |

**指数项内容**:

| 字段 | 显示内容 | 样式类 | 数据字段 |
|------|---------|--------|----------|
| 指数名称 | index.name | index-name | `name` |
| 指数价格 | index.price | index-price, 涨跌颜色 | `price` |
| 涨跌额 | index.change | index-change, 涨跌颜色 | `change` |
| 涨跌幅 | index.change_pct | index-change, 涨跌颜色 | `change_pct` |

#### 4.2 实时行情卡片

| 容器名称 | 容器类型 | 位置 | 用途 |
|---------|---------|------|------|
| `quote-card` | el-card | 左侧 | 行情展示卡片 |
| `stock-search` | div | 卡片顶部 | 搜索区域 |
| `quote-display` | div | 搜索框下方 | 行情展示区 |
| `quote-details` | el-row | 行情下方 | 详细数据网格 |

**搜索框**:

| 元素 | 类型 | 属性 | 功能 |
|------|------|------|------|
| 输入框 | el-input | placeholder="输入股票代码" | 输入代码 |
| 搜索按钮 | el-button | icon=Search, @click=fetchQuote | 查询行情 |

**行情显示**:

| 区域 | 字段 | 样式 | 颜色规则 |
|------|------|------|----------|
| 标题栏 | 股票代码、名称 | quote-header | - |
| 主价格 | 当前价 | price-large | 涨红跌绿 |
| 涨跌信息 | 涨跌额、涨跌幅 | change-info | 涨红跌绿 |

**详细数据**:

| 字段名 | 标签 | 数值字段 | 格式 |
|--------|------|----------|------|
| 今开 | `今开:` | open | 保留2位小数 |
| 昨收 | `昨收:` | pre_close | 保留2位小数 |
| 最高 | `最高:` | high | 保留2位小数 |
| 最低 | `最低:` | low | 保留2位小数 |
| 成交量 | `成交量:` | volume | 数量格式化 |
| 成交额 | `成交额:` | amount | 金额格式化 |
| 换手率 | `换手率:` | turnover | 百分比 |
| 量比 | `量比:` | volume_ratio | 保留2位小数 |

#### 4.3 K线图卡片

| 容器名称 | 容器类型 | 尺寸 | 用途 |
|---------|---------|------|------|
| `chart-card` | el-card | - | K线图卡片 |
| `chart-container` | div | 500px高 | K线图表容器 |

**周期选择器**:

| 按钮组 | 周期选项 | 数据字段 |
|--------|---------|----------|
| el-button-group | 日K、周K、月K、5分钟、15分钟、30分钟、60分钟 | period |

**K线图配置**:
- 上半部分: K线主图 (70%高度)
- 下半部分: 成交量柱状图 (30%高度)
- X轴: 时间
- Y轴: 价格/成交量

### 交互元素

| 元素名称 | 类型 | 位置 | 功能 | API调用 |
|---------|------|------|------|---------|
| 刷新指数按钮 | el-button (circle) | 指数卡片头部 | 刷新指数数据 | `GET /api/market/quotes` (指数) |
| 股票搜索框 | el-input | 左侧卡片 | 输入股票代码 | - |
| 搜索按钮 | el-button | 搜索框右侧 | 查询股票行情 | `GET /api/market/quotes?symbols={code}` |
| 指数项 | div | 指数列表 | 点击查看该指数K线 | selectStock() |
| 周期按钮 | el-button | K线图上方 | 切换K线周期 | `GET /api/market/kline` |

### API调用

```javascript
// 获取指数行情
GET /api/market/quotes
Response: [{ code, name, price, change, change_pct, ... }]

// 获取个股行情
GET /api/market/quotes?symbols=600519
Response: { code, name, price, open, high, low, ... }

// 获取K线数据
GET /api/market/kline?symbol=600519&period=daily&limit=100
Response: [{ date, open, high, low, close, volume }]
```

### 数据源

- **TDX适配器**: 通达信行情服务器
- **实时更新**: 手动刷新
- **历史数据**: K线数据回溯

---

## 5. 市场数据模块

**路由**: `/market-data/*`
**布局**: 子路由页面
**认证状态**: 需要登录

### 5.1 资金流向

**路由**: `/market-data/fund-flow`
**组件**: `src/components/market/FundFlowPanel.vue`

#### 页面布局

```
资金流向
├── 查询表单卡片
│   ├── 股票代码输入框
│   ├── 时间维度选择器
│   ├── 日期范围选择器
│   ├── 查询按钮
│   └── 刷新数据按钮
└── 数据展示卡片
    └── 资金流向表格
```

#### 容器详情

| 容器名称 | 容器类型 | 用途 |
|---------|---------|------|
| `fund-flow-panel` | div | 主容器 |
| `search-card` | el-card | 查询表单卡片 |
| `data-card` | el-card | 数据表格卡片 |

#### 查询表单

| 字段名 | 元素类型 | 宽度 | 选项/提示 | 默认值 |
|--------|---------|------|-----------|--------|
| 股票代码 | el-input | 160px | placeholder="如: 600519.SH" | - |
| 时间维度 | el-select | 120px | 今日/3日/5日/10日 | 1 |
| 日期范围 | el-date-picker | 240px | daterange | - |

#### 数据表格列

| 列名 | 字段 | 宽度 | 排序 | 格式 | 颜色 |
|------|------|------|------|------|------|
| 交易日期 | trade_date | 120px | ✓ | YYYY-MM-DD | - |
| 时间维度 | timeframe | 90px | - | N天 (Tag) | - |
| 主力净流入 | main_net_inflow | 140px | ✓ | 金额格式 | 涨红跌绿 |
| 主力净占比 | main_net_inflow_rate | 120px | ✓ | 百分比 | 涨红跌绿 |
| 超大单 | super_large_net_inflow | 140px | ✓ | 金额格式 | 涨红跌绿 |
| 大单 | large_net_inflow | 140px | ✓ | 金额格式 | 涨红跌绿 |
| 中单 | medium_net_inflow | 140px | ✓ | 金额格式 | 涨红跌绿 |
| 小单 | small_net_inflow | 140px | ✓ | 金额格式 | 涨红跌绿 |

#### API调用

```javascript
// 查询资金流向
GET /api/market/fund-flow?symbol={symbol}&start_date={start}&end_date={end}&timeframe={days}
Response: [{ trade_date, timeframe, main_net_inflow, ... }]

// 刷新资金流向数据
POST /api/market/fund-flow/refresh?symbol={symbol}&trade_date={date}
```

#### 数据源

- **东方财富网**: via AkShare
- **数据库表**: `stock_fund_flow`
- **当前数据量**: 2条记录

---

### 5.2 ETF行情

**路由**: `/market-data/etf`
**组件**: `src/components/market/ETFDataTable.vue`

#### 页面布局

```
ETF行情
├── 查询工具栏卡片
│   ├── ETF代码输入框
│   ├── 关键词搜索框
│   ├── 显示数量输入框
│   ├── 查询按钮
│   └── 刷新全市场数据按钮
└── ETF数据表格卡片
    └── 数据表格 (支持排序)
```

#### 容器详情

| 容器名称 | 容器类型 | 用途 |
|---------|---------|------|
| `etf-data-table` | div | 主容器 |
| `search-card` | el-card | 查询表单卡片 |
| `data-card` | el-card | 数据表格卡片 |

#### 查询表单

| 字段名 | 元素类型 | 宽度 | 提示/选项 |
|--------|---------|------|-----------|
| ETF代码 | el-input | 140px | placeholder="如: 510300" |
| 关键词 | el-input | 160px | placeholder="名称/代码搜索" |
| 显示数量 | el-input-number | 120px | min=10, max=500, step=10 |

#### 数据表格列

| 列名 | 字段 | 宽度 | 固定 | 排序 | 格式 |
|------|------|------|------|------|------|
| 代码 | symbol | 100px | ✓ | - | - |
| 名称 | name | 180px | ✓ | - | 超长省略 |
| 最新价 | latest_price | 100px | - | ✓ | 保留3位小数 |
| 涨跌幅 | change_percent | 100px | - | ✓ | 百分比+颜色 |
| 涨跌额 | change_amount | 100px | - | ✓ | 保留3位小数+颜色 |
| 成交量 | volume | 120px | - | ✓ | 单位换算 |
| 成交额 | amount | 120px | - | ✓ | 单位换算 |
| 今开 | open_price | 100px | - | - | 保留3位小数 |
| 最高 | high_price | 100px | - | - | 保留3位小数 |
| 最低 | low_price | 100px | - | - | 保留3位小数 |
| 昨收 | prev_close | 100px | - | - | 保留3位小数 |
| 换手率 | turnover_rate | 100px | - | ✓ | 百分比 |
| 总市值 | total_market_cap | 140px | - | ✓ | 亿元 |
| 流通市值 | circulating_market_cap | 140px | - | ✓ | 亿元 |
| 交易日期 | trade_date | 120px | - | - | YYYY-MM-DD |

#### API调用

```javascript
// 查询ETF列表
GET /api/market/etf/list?limit={N}&symbol={code}&keyword={kw}
Response: [{ symbol, name, latest_price, change_percent, ... }]

// 刷新ETF数据
POST /api/market/etf/refresh
```

#### 数据源

- **东方财富网**: ETF实时行情
- **数据库表**: `etf_spot_data`
- **当前数据量**: 1,269条记录

---

### 5.3 竞价抢筹

**路由**: `/market-data/chip-race`
**组件**: `src/components/market/ChipRaceTable.vue`

#### 页面布局

```
竞价抢筹
├── 查询工具栏卡片
│   ├── 股票代码输入框
│   ├── 日期范围选择器
│   ├── 最小抢筹金额输入框
│   ├── 显示数量输入框
│   ├── 查询按钮
│   └── 刷新最新数据按钮
└── 竞价抢筹数据表格卡片
    └── 数据表格
```

#### 数据表格列

| 列名 | 字段 | 宽度 | 排序 | 格式 |
|------|------|------|------|------|
| 交易日期 | trade_date | 120px | ✓ | YYYY-MM-DD |
| 代码 | symbol | 100px | - | - |
| 名称 | name | 120px | - | - |
| 竞价金额 | bid_amount | 140px | ✓ | 金额格式 |
| 竞价量 | bid_volume | 120px | ✓ | 数量格式 |
| 成交额占比 | amount_ratio | 100px | ✓ | 百分比 |
| 涨跌幅 | change_percent | 100px | ✓ | 百分比+颜色 |
| 抢筹强度 | intensity | 100px | ✓ | 数值 |

#### API调用

```javascript
// 查询竞价抢筹数据
GET /api/market/chip-race?limit={N}&symbol={code}&start_date={start}&end_date={end}
Response: []  // 当前为空

// 刷新竞价抢筹数据
POST /api/market/chip-race/refresh?trade_date={date}
```

#### 数据源

- **TQLEX适配器**: 通达信竞价数据
- **数据库表**: `chip_race_data`
- **当前数据量**: 0条 (需配置)

---

### 5.4 龙虎榜

**路由**: `/market-data/lhb`
**组件**: `src/components/market/LongHuBangTable.vue`

#### 页面布局

```
龙虎榜
├── 查询工具栏卡片
│   ├── 股票代码输入框
│   ├── 日期范围选择器
│   ├── 最小净买入额输入框
│   ├── 显示数量输入框
│   ├── 查询按钮
│   └── 刷新最新数据按钮
└── 龙虎榜数据表格卡片
    └── 数据表格
```

#### 数据表格列

| 列名 | 字段 | 宽度 | 固定 | 排序 | 格式 |
|------|------|------|------|------|------|
| 交易日期 | trade_date | 120px | ✓ | ✓ | YYYY-MM-DD |
| 代码 | symbol | 100px | ✓ | - | - |
| 名称 | name | 120px | ✓ | - | 超长省略 |
| 上榜原因 | reason | 200px | - | - | Tag标签 |
| 净买入额 | net_amount | 140px | - | ✓ | 金额+颜色 |
| 买入总额 | buy_amount | 140px | - | ✓ | 金额格式 |
| 卖出总额 | sell_amount | 140px | - | ✓ | 金额格式 |
| 换手率 | turnover_rate | 100px | - | ✓ | 百分比 |
| 机构买入 | institution_buy | 140px | - | - | 金额格式 |
| 机构卖出 | institution_sell | 140px | - | - | 金额格式 |

#### API调用

```javascript
// 查询龙虎榜数据
GET /api/market/lhb?limit={N}&symbol={code}&start_date={start}&end_date={end}&min_net_amount={amount}
Response: [{ trade_date, symbol, name, reason, net_amount, ... }]

// 刷新龙虎榜数据
POST /api/market/lhb/refresh?trade_date={date}
```

#### 数据源

- **东方财富网**: via AkShare
- **数据库表**: `stock_lhb_detail`
- **当前数据量**: 463条记录

---

### 5.5 问财筛选

**路由**: `/market-data/wencai`
**组件**: `src/components/market/WencaiPanelV2.vue`

#### 页面布局

```
问财筛选
├── 查询工具栏卡片
│   ├── 查询类型选择器
│   ├── 自然语言输入框
│   ├── 页数输入框
│   ├── 查询按钮
│   └── 清除结果按钮
└── 查询结果表格卡片
    └── 动态列表格
```

#### 查询表单

| 字段名 | 元素类型 | 宽度 | 选项 |
|--------|---------|------|------|
| 查询类型 | el-select | 180px | 股票选择/概念选择/资讯选择/指数选择 |
| 查询条件 | el-input | textarea | placeholder="输入自然语言查询条件..." |
| 查询页数 | el-input-number | 120px | min=1, max=10 |

#### API调用

```javascript
// 问财查询
POST /api/market/wencai/query
Body: { query_name, query_content, pages }
Response: { columns: [], data: [[]], total: N }
```

#### 数据源

- **同花顺问财**: 自然语言查询接口
- **实时查询**: 不缓存

---

## 6. 股票管理页面

**路由**: `/stocks`
**组件**: `src/views/Stocks.vue`

### 页面布局

```
股票管理
└── 股票列表卡片
    ├── 工具栏
    │   ├── 搜索框
    │   ├── 搜索按钮
    │   └── 刷新按钮
    ├── 数据表格
    └── 分页器
```

### 容器详情

| 容器名称 | 容器类型 | 用途 |
|---------|---------|------|
| `stocks` | div | 主容器 |
| `stocks-card` | el-card | 股票列表卡片 |

### 工具栏

| 元素名称 | 元素类型 | 宽度 | 功能 |
|---------|---------|------|------|
| 搜索框 | el-input | 200px | 搜索股票代码或名称 |
| 搜索按钮 | el-button | - | 执行搜索 |
| 刷新按钮 | el-button | - | 刷新列表 |

### 数据表格列

| 列名 | 字段 | 宽度 | 说明 |
|------|------|------|------|
| 股票代码 | symbol | 120px | - |
| 股票名称 | name | 150px | - |
| 所属行业 | industry | - | - |
| 地区 | area | 100px | - |
| 市场 | market | 100px | - |
| 上市日期 | list_date | 120px | - |
| 操作 | - | 200px | 查看、分析按钮 |

### 分页器

| 配置项 | 值 |
|--------|---|
| 每页数量选项 | 10, 20, 50, 100 |
| 默认每页 | 20条 |
| 布局 | total, sizes, prev, pager, next, jumper |

### API调用

```javascript
// 获取股票列表
GET /api/market/stocks?limit={N}&offset={M}&search={keyword}
Response: { success: true, data: [...], total: N }
```

### 数据源

- **AkShare**: 股票基本信息
- **数据库表**: `stock_info`
- **当前数据量**: 5,438条记录

---

## 7. 数据分析页面

**路由**: `/analysis`
**组件**: `src/views/Analysis.vue`
**状态**: ⚠️ 功能开发中

---

## 8. 技术分析页面

**路由**: `/technical`
**组件**: `src/views/TechnicalAnalysis.vue`
**状态**: ⚠️ 功能开发中

---

## 9. 指标库页面

**路由**: `/indicators`
**组件**: `src/views/IndicatorLibrary.vue`
**状态**: ⚠️ 功能开发中

---

## 10. 风险监控页面

**路由**: `/risk`
**组件**: `src/views/RiskMonitor.vue`
**状态**: ⚠️ 功能开发中

---

## 11. 交易管理页面

**路由**: `/trade`
**组件**: `src/views/TradeManagement.vue`
**状态**: ⚠️ 功能开发中

---

## 12. 策略管理页面

**路由**: `/strategy`
**组件**: `src/views/StrategyManagement.vue`
**状态**: ⚠️ 功能开发中

---

## 13. 回测分析页面

**路由**: `/backtest`
**组件**: `src/views/BacktestAnalysis.vue`
**状态**: ⚠️ 功能开发中

---

## 14. 任务管理页面

**路由**: `/tasks`
**组件**: `src/views/TaskManagement.vue`
**状态**: ⚠️ 功能开发中

---

## 15. 系统设置页面

**路由**: `/settings`
**组件**: `src/views/Settings.vue`
**状态**: ⚠️ 功能开发中

---

## 🎨 UI组件库

### Element Plus组件使用清单

| 组件名称 | 用途 | 使用页面 |
|---------|------|----------|
| el-card | 卡片容器 | 所有页面 |
| el-table | 数据表格 | Dashboard, 股票管理, 市场数据模块 |
| el-input | 输入框 | 登录, 搜索, 查询表单 |
| el-button | 按钮 | 所有页面 |
| el-tabs | 标签页 | Dashboard, TDX行情 |
| el-select | 选择器 | Dashboard, 查询表单 |
| el-date-picker | 日期选择器 | 查询表单 |
| el-input-number | 数字输入框 | 查询表单 |
| el-pagination | 分页器 | 股票管理 |
| el-tag | 标签 | 数据表格 |
| el-empty | 空状态 | 开发中页面 |
| el-row / el-col | 栅格布局 | Dashboard, TDX行情 |
| el-form | 表单 | 登录, 查询表单 |
| el-checkbox | 复选框 | 登录 |

### 图表库

| 库名称 | 版本 | 用途 |
|--------|------|------|
| ECharts | 5.x | 所有图表渲染 |

---

## 📊 数据流架构

### API层级

```
前端组件
  ↓
src/api/index.js (Axios封装)
  ↓
Vite代理 (/api → http://localhost:8000)
  ↓
FastAPI后端
  ↓
数据库 / 适配器
```

### 状态管理

| 存储方式 | 用途 | 示例 |
|---------|------|------|
| localStorage | Token存储 | `token`, `user` |
| Pinia Store | 全局状态 | `authStore` |
| 组件 ref | 页面状态 | `loading`, `tableData` |

### 数据刷新策略

| 页面模块 | 刷新方式 | 频率 |
|---------|---------|------|
| 仪表盘 | 手动刷新 | 按需 |
| TDX行情 | 手动刷新 | 按需 |
| ETF行情 | 手动/定时 | 按需/5-10分钟 |
| 龙虎榜 | 手动刷新 | 每日20:30后 |
| 资金流向 | 手动刷新 | 按需 |

---

## 🎯 功能完成度统计

| 页面/模块 | 完成度 | 数据状态 | 优先级 |
|----------|--------|----------|--------|
| 登录页面 | 100% | ✅ | P0 |
| 仪表盘 | 90% | ⚠️ 部分模拟 | P1 |
| 市场行情 | 10% | ❌ 待开发 | P2 |
| TDX行情 | 95% | ✅ | P1 |
| 资金流向 | 100% | ⚠️ 数据少(2条) | P1 |
| ETF行情 | 100% | ✅ 1,269条 | P1 |
| 竞价抢筹 | 100% | ❌ 0条(需配置) | P2 |
| 龙虎榜 | 100% | ✅ 463条 | P1 |
| 问财筛选 | 95% | ✅ | P2 |
| 股票管理 | 100% | ✅ 5,438条 | P1 |
| 数据分析 | 0% | ❌ 待开发 | P3 |
| 技术分析 | 0% | ❌ 待开发 | P3 |
| 其他功能 | 0% | ❌ 待开发 | P3 |

**综合完成度**: **约60%**
**核心功能完成度**: **95%**

---

## 📝 使用建议

### 高优先级改进

1. **仪表盘数据实时化** (P1)
   - 将模拟数据替换为真实API数据
   - 连接实时行情接口
   - 添加自动刷新机制

2. **增加资金流向数据** (P1)
   - 当前仅2条记录
   - 填充热门股票资金流向
   - 目标: 100+条记录

3. **配置竞价抢筹** (P2)
   - 配置TQLEX适配器
   - 填充chip_race_data表

### 中优先级扩展

4. **完善市场行情页** (P2)
   - 实时行情表格
   - 市场概览卡片
   - 热点板块展示

5. **开发数据分析页** (P3)
   - 技术指标计算
   - 图表分析工具
   - 策略回测功能

---

**文档维护**: Claude Code
**最后更新**: 2025-10-20 13:00:00
**版本**: v1.0
