# MyStocks Web端页面HTML样本

> **参考指南说明**:
> 本文件用于提供某一局部主题的使用方法、操作步骤、背景说明或参考材料，帮助理解仓库中的具体实践。
> 其中的命令、路径、流程和示例应与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果一并核对，不应单独视为共享规则或当前状态的唯一事实来源。


**生成时间**: 2026-01-02
**版本**: v1.0
**项目**: MyStocks量化交易数据管理系统

---

## 📋 概述

本目录包含MyStocks项目Web端核心页面的HTML样本文件，用于：
- 展示页面结构和功能布局
- 标注API接口调用
- 提供UI/UX设计参考
- 辅助前后端开发协作

---

## 📁 文件列表

| 序号 | 文件名 | 页面名称 | 说明 |
|------|--------|----------|------|
| 1 | `01_Dashboard.html` | 市场总览 | 仪表盘首页，展示市场概览、热度分析、板块表现 |
| 2 | `02_StockDetail.html` | 股票详情 | 单个股票详情页面，K线图、技术指标、交易信号 |
| 3 | `03_StrategyManagement.html` | 策略管理 | 策略CRUD管理，列表展示、创建编辑、批量操作 |
| 4 | `04_BacktestAnalysis.html` | 回测分析 | 策略回测，参数配置、结果展示、交易记录 |
| 5 | `05_RiskMonitor.html` | 风险监控 | 风险仪表板，风险等级、预警列表、VaR分析 |
| 6 | `06_Market.html` | 市场行情 | 市场行情列表，实时报价、涨跌幅、排序筛选 |
| 7 | `07_TechnicalAnalysis.html` | 技术分析 | 技术分析工具，K线图表、技术指标、形态识别 |
| 8 | `08_Login.html` | 用户登录 | 登录页面，用户认证、社交登录 |

---

## 🎨 设计规范

### 颜色系统

```css
/* 主题色 */
--primary-color: #409EFF;      /* 蓝色 - 主要按钮、链接 */
--success-color: #67C23A;      /* 绿色 - 上涨、成功 */
--warning-color: #E6A23C;      /* 橙色 - 警告 */
--danger-color: #F56C6C;       /* 红色 - 下跌、危险 */
--info-color: #909399;         /* 灰色 - 中性、信息 */

/* 文本颜色 */
--text-primary: #333;          /* 主要文本 */
--text-secondary: #666;        /* 次要文本 */
--text-tertiary: #999;         /* 辅助文本 */

/* 背景颜色 */
--bg-primary: #ffffff;         /* 主背景 */
--bg-secondary: #f5f5f5;       /* 次背景 */
--bg-tertiary: #f9f9f9;        /* 卡片背景 */
```

### 字体系统

```css
/* 字体大小 */
--font-size-xl: 28px;          /* 页面标题 */
--font-size-lg: 24px;          /* 卡片标题 */
--font-size-md: 18px;          /* 区块标题 */
--font-size-base: 16px;        /* 正文 */
--font-size-sm: 14px;          /* 辅助文本 */
--font-size-xs: 12px;          /* 标签、注释 */

/* 字体粗细 */
--font-weight-bold: bold;      /* 标题 */
--font-weight-medium: 500;     /* 强调 */
--font-weight-normal: normal;  /* 正文 */
```

### 间距系统

```css
/* 间距 */
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 12px;
--spacing-lg: 16px;
--spacing-xl: 20px;
--spacing-xxl: 30px;

/* 圆角 */
--border-radius-sm: 4px;
--border-radius-md: 8px;
--border-radius-lg: 12px;

/* 阴影 */
--shadow-sm: 0 2px 8px rgba(0,0,0,0.1);
--shadow-md: 0 4px 16px rgba(0,0,0,0.15);
--shadow-lg: 0 10px 40px rgba(0,0,0,0.2);
```

---

## 🔄 数据流示例

### 示例1: Dashboard数据流

```javascript
// 1. 获取市场总览
GET /api/market/overview
→ 返回: 市场指数、涨跌统计、成交额等

// 2. 获取资金流向
GET /api/market/fund-flow?market=SH
→ 返回: 行业资金流向数据

// 3. 实时数据推送 (SSE)
EventSource('/api/sse/market/quotes')
→ 接收: 实时行情推送
```

### 示例2: StockDetail数据流

```javascript
// 1. 获取K线数据
GET /api/market/kline?symbol=600519.SH&interval=1d&limit=100
→ 返回: OHLCV数据

// 2. 获取技术指标
GET /api/technical/indicators?symbol=600519.SH
→ 返回: MACD, KDJ, RSI等指标

// 3. 获取交易信号
GET /api/technical/signals?symbol=600519.SH
→ 返回: 买卖信号列表
```

### 示例3: StrategyManagement数据流

```javascript
// 1. 获取策略列表
GET /api/v1/strategy/strategies?page=1&pageSize=10
→ 返回: 策略列表、分页信息

// 2. 创建新策略
POST /api/v1/strategy/strategies
Body: { name, type, parameters, ... }
→ 返回: 创建的策略ID

// 3. 运行策略
POST /api/v1/strategy/strategies/:id/run
→ 返回: 运行任务ID

// 4. 执行回测
POST /api/v1/strategy/backtest
Body: { strategy_id, start_date, end_date, ... }
→ 返回: 回测结果、性能指标
```

---

## 📊 页面布局模式

### MainLayout (主布局)

适用于: Dashboard, Analysis, Settings等

```
┌─────────────────────────────────────────┐
│  Header (Logo + Navigation)             │
├─────────────────────────────────────────┤
│  Sidebar Menu                           │
│  ├ Dashboard                            │
│  ├ Analysis                             │
│  ├ Stocks                               │
│  └ Settings                             │
├─────────────────────────────────────────┤
│  Main Content                           │
│  ┌─────────────────────────────────┐   │
│  │ Page Title + Actions            │   │
│  ├─────────────────────────────────┤   │
│  │                                 │   │
│  │  Charts / Tables / Forms        │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### MarketLayout (市场布局)

适用于: Market, TdxMarket, RealTimeMonitor等

```
┌─────────────────────────────────────────┐
│  Market Header (指数卡片)               │
├─────────────────────────────────────────┤
│  Filter Bar (市场/板块/排序)            │
├─────────────────────────────────────────┤
│  Table / Grid View                      │
│  ┌─────────────────────────────────┐   │
│  │ Stock List with Real-time Data │   │
│  ├─────────────────────────────────┤   │
│  │ Code | Name | Price | Change%  │   │
│  ├─────────────────────────────────┤   │
│  │  ... (Table Rows)              │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### StrategyLayout (策略布局)

适用于: StrategyManagement, BacktestAnalysis等

```
┌─────────────────────────────────────────┐
│  Strategy Header                        │
├─────────────────────────────────────────┤
│  Tab Navigation                         │
│  ├ [Strategy List] [Backtest]          │
├─────────────────────────────────────────┤
│  Main Content                           │
│  ┌───────────────────┬─────────────────┐│
│  │ Strategy List     │  Strategy Detail││
│  │                   │  or Config Panel││
│  │ (Table with CRUD) │                 ││
│  └───────────────────┴─────────────────┘│
└─────────────────────────────────────────┘
```

---

## 🔌 API端点映射

### 市场数据API

| 功能 | 方法 | 端点 | 使用页面 |
|------|------|------|----------|
| 市场总览 | GET | `/api/market/overview` | Dashboard, Market |
| K线数据 | GET | `/api/market/kline` | StockDetail, TechnicalAnalysis |
| 资金流向 | GET | `/api/market/fund-flow` | Dashboard, FundFlowPanel |
| ETF列表 | GET | `/api/market/etf/list` | ETFDataTable |
| 龙虎榜 | GET | `/api/market/lhb` | LongHuBangTable |

### 策略API

| 功能 | 方法 | 端点 | 使用页面 |
|------|------|------|----------|
| 策略列表 | GET | `/api/v1/strategy/strategies` | StrategyManagement |
| 创建策略 | POST | `/api/v1/strategy/strategies` | StrategyManagement |
| 更新策略 | PUT | `/api/v1/strategy/strategies/:id` | StrategyManagement |
| 删除策略 | DELETE | `/api/v1/strategy/strategies/:id` | StrategyManagement |
| 执行回测 | POST | `/api/v1/strategy/backtest` | BacktestAnalysis |

### 技术分析API

| 功能 | 方法 | 端点 | 使用页面 |
|------|------|------|----------|
| 技术指标 | GET | `/api/technical/indicators` | TechnicalAnalysis, StockDetail |
| 计算指标 | POST | `/api/technical/calculate` | TechnicalAnalysis |
| 形态识别 | GET | `/api/technical/patterns` | TechnicalAnalysis |
| 交易信号 | GET | `/api/technical/signals` | StockDetail |

### 风险监控API

| 功能 | 方法 | 端点 | 使用页面 |
|------|------|------|----------|
| 风险概览 | GET | `/api/risk/overview` | RiskMonitor |
| 风险预警 | GET | `/api/risk/alerts` | RiskMonitor |
| 持仓集中度 | GET | `/api/risk/concentration` | RiskMonitor |
| VaR分析 | GET | `/api/risk/var` | RiskMonitor |

### 认证API

| 功能 | 方法 | 端点 | 使用页面 |
|------|------|------|----------|
| 用户登录 | POST | `/api/auth/login` | Login |
| 刷新Token | POST | `/api/auth/refresh` | 全局 |
| 用户登出 | POST | `/api/auth/logout` | 全局 |

---

## 🎯 使用说明

### 1. 前端开发者

1. **参考页面结构**: 查看HTML样本了解页面布局
2. **API对接**: 查看JavaScript代码中的API调用示例
3. **样式规范**: 遵循CSS变量定义的设计系统
4. **组件拆分**: 将HTML拆分为Vue组件

### 2. 后端开发者

1. **API端点**: 查看JavaScript代码了解需要的API格式
2. **数据结构**: 参考注释中的响应示例
3. **错误处理**: 确保返回标准的错误响应

### 3. UI/UX设计师

1. **视觉参考**: 查看HTML样本的布局和样式
2. **交互设计**: 参考按钮、表单、表格的交互方式
3. **响应式**: 需考虑移动端适配

### 4. 产品经理

1. **功能清单**: 查看每个页面的功能点
2. **数据流**: 理解页面间的数据交互
3. **用户场景**: 基于页面设计用户故事

---

## 📝 开发注意事项

### 安全性

1. **认证**: 所有API请求需携带JWT Token (除了Login)
2. **权限**: 部分页面需要特定角色权限
3. **XSS防护**: 前端需对用户输入进行转义
4. **CSRF**: 非GET请求需携带CSRF Token

### 性能优化

1. **懒加载**: 大型表格使用虚拟滚动
2. **缓存**: 静态数据缓存到LocalStorage
3. **CDN**: 静态资源使用CDN加速
4. **压缩**: 启用GZip压缩

### 兼容性

1. **浏览器**: 支持Chrome 90+, Firefox 88+, Safari 14+
2. **分辨率**: 支持1920x1080及以上分辨率
3. **移动端**: 响应式设计，支持平板访问

---

## 🔗 相关文档

- [完整页面清单报告](PAGES_INVENTORY_REPORT.md)
- [API接口文档](/docs/api/)
- [前端开发规范](/docs/standards/FRONTEND_DEV_GUIDELINES.md)
- [项目架构文档](/docs/architecture/)

---

**维护说明**:
- 本目录的HTML文件仅供参考，不直接用于生产环境
- 实际页面使用Vue 3 + Element Plus实现
- 如有页面功能变更，请同步更新HTML样本文件

**最后更新**: 2026-01-02
