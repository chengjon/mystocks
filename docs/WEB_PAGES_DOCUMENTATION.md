# MyStocks Web Frontend - 页面信息完整文档

## 📋 概述

本文档详细记录了MyStocks Web前端应用的所有页面信息，包括菜单结构、路由地址、页面元素及其显示内容。

**当前运行环境**：
- 前端地址：http://localhost:3001
- 后端API：http://localhost:8000
- 数据模式：真实数据（REAL）

---

## 🎯 菜单结构及页面详情

### 1. 仪表盘 (`/dashboard`)
**URL**: http://localhost:3001/dashboard
**菜单位置**: 顶部 > 仪表盘
**组件文件**: `/src/views/Dashboard.vue`

#### 页面元素：
- **智能数据源指示器**
  - 显示模式：真实数据
  - 状态：已连接

- **统计卡片组**
  - 总资产 (Total Assets)
  - 可用资金 (Available Cash)
  - 持仓价值 (Position Value)
  - 总盈亏 (Total Profit/Loss)

- **市场热度中心**
  - 标签页：
    - 市场热度
    - 领涨板块
    - 市场分布
    - 资金流向

- **行业资金流向图**
  - 行业标准选择器
  - 资金流向图表

- **板块表现表格**
  - 收藏夹标签页
  - 表格数据：板块名称、涨跌幅、成交额等

---

### 2. 市场行情

#### 2.1 实时行情 (`/market`)
**URL**: http://localhost:3001/market
**菜单位置**: 市场行情 > 实时行情
**组件文件**: `/src/views/Market.vue`

#### 页面元素：
- **资产概览卡片**
  - 总资产
  - 可用资金
  - 持仓价值
  - 总盈亏

- **交易统计标签页**
  - 交易数据：总交易次数、买入次数、卖出次数、已实现盈亏
  - 资产分布：总资产、现金比例、持仓比例、收益率

- **持仓信息标签页**
  - 详细持仓表格

#### 2.2 TDX行情 (`/tdx-market`)
**URL**: http://localhost:3001/tdx-market
**菜单位置**: 市场行情 > TDX行情
**组件文件**: `/src/views/TdxMarket.vue`

---

### 3. 市场数据

#### 3.1 资金流向 (`/market-data/fund-flow`)
**URL**: http://localhost:3001/market-data/fund-flow
**菜单位置**: 市场数据 > 资金流向
**组件文件**: `/src/components/market/FundFlowPanel.vue`

#### 页面元素：
- **搜索表单**
  - 股票代码输入框
  - 时间周期选择器
  - 日期范围选择器
  - 搜索按钮

- **资金流向数据表**
  | 列名 | 格式/类型 | 说明 |
  |------|------------|------|
  | 交易日期 | YYYY-MM-DD | 交易日期 |
  | 时间周期 | 文本 | 如：1分钟、5分钟 |
  | 主力净流入 | 数值 | 带正负号 |
  | 主力净占比 | 百分比 | 如：+5.23% |
  | 散户净流入 | 数值 | 带正负号 |
  | 散户净占比 | 百分比 | 如：+2.15% |

#### 3.2 ETF行情 (`/market-data/etf`)
**URL**: http://localhost:3001/market-data/etf
**菜单位置**: 市场数据 > ETF行情
**组件文件**: `/src/components/market/ETFDataTable.vue`

#### 3.3 竞价抢筹 (`/market-data/chip-race`)
**URL**: http://localhost:3001/market-data/chip-race
**菜单位置**: 市场数据 > 竞价抢筹
**组件文件**: `/src/components/market/ChipRaceTable.vue`

#### 3.4 龙虎榜 (`/market-data/lhb`)
**URL**: http://localhost:3001/market-data/lhb
**菜单位置**: 市场数据 > 龙虎榜
**组件文件**: `/src/components/market/LongHuBangTable.vue`

#### 3.5 问财筛选 (`/market-data/wencai`)
**URL**: http://localhost:3001/market-data/wencai
**菜单位置**: 市场数据 > 问财筛选
**组件文件**: `/src/components/market/WencaiPanelV2.vue`

---

### 4. 股票管理

#### 4.1 股票列表 (`/stocks`)
**URL**: http://localhost:3001/stocks
**菜单位置**: 股票管理
**组件文件**: `/src/views/Stocks.vue`

#### 4.2 股票详情 (`/stock-detail/:symbol`)
**URL**: http://localhost:3001/stock-detail/{symbol}
**菜单位置**: 动态路由
**组件文件**: `/src/views/StockDetail.vue`

#### 页面元素：
- **股票信息头部**
  - 股票名称
  - 股票代码
  - 所属市场
  - 行业分类
  - 概念标签

- **实时价格显示**
  - 当前价格
  - 涨跌额
  - 涨跌幅

- **K线图容器**
  - 图表类型选择器
  - 时间周期选择器：1周、1月、3月、6月、1年
  - 交互式K线图

- **基本信息卡片**
  - 股票基本信息
  - 市值信息
  - 成交信息

- **技术指标面板**
  - MA5、MA10、MA20
  - RSI、MACD指标
  - 指标参数显示

- **交易摘要**
  - 周期选择器
  - 交易统计数据

---

### 5. 数据分析

#### 5.1 数据分析概览 (`/analysis`)
**URL**: http://localhost:3001/analysis
**菜单位置**: 数据分析
**组件文件**: `/src/views/Analysis.vue`

#### 5.2 行业概念分析 (`/analysis/industry-concept`)
**URL**: http://localhost:3001/analysis/industry-concept
**菜单位置**: 数据分析 > 行业概念分析
**组件文件**: `/src/views/IndustryConceptAnalysis.vue`

---

### 6. 技术分析

#### 6.1 技术分析 (`/technical`)
**URL**: http://localhost:3001/technical
**菜单位置**: 技术分析 > 技术分析
**组件文件**: `/src/views/TechnicalAnalysis.vue`

#### 页面元素：
- **股票搜索栏**
  - 搜索输入框
  - 搜索按钮

- **日期选择器**
  - 开始日期
  - 结束日期

- **周期选择器**
  - 选项：日线、周线、月线

- **操作按钮**
  - 刷新按钮
  - 重试按钮
  - 指标设置按钮
  - 配置管理下拉菜单

- **K线图容器**
  - ECharts图表显示区域
  - 支持缩放和平移

- **指标面板**
  - 可选技术指标列表
  - 参数配置面板

#### 6.2 指标库 (`/indicators`)
**URL**: http://localhost:3001/indicators
**菜单位置**: 技术分析 > 指标库
**组件文件**: `/src/views/IndicatorLibrary.vue`

#### 页面元素：
- **统计卡片**
  - 总指标数：161
  - 各分类指标数量统计
  - 类别标签：趋势、动量、波动率、成交量、K线形态

- **搜索和筛选**
  - 指标搜索框
  - 分类筛选器
  - 标签筛选器

- **指标详情卡片**
  | 字段 | 内容格式 | 说明 |
  |------|----------|------|
  | 缩写 | 英文缩写 | 如：MACD |
  | 全称 | 英文全称 | 如：Moving Average Convergence Divergence |
  | 中文名 | 中文 | 如：平滑异同移动平均线 |
  | 分类 | 标签数组 | 如：趋势、动量 |
  | 描述 | 文本段落 | 指标功能说明 |
  | 参数 | 表格 | 参数名称、默认值、取值范围 |
  | 输出字段 | 列表 | 输出数据字段说明 |
  | 参考线 | 列表 | 支持的参考线类型 |

---

### 7. 风险监控

#### 7.1 风险监控 (`/risk`)
**URL**: http://localhost:3001/risk
**菜单位置**: 风险监控
**组件文件**: `/src/views/RiskMonitor.vue`

#### 7.2 公告监控 (`/announcement`)
**URL**: http://localhost:3001/announcement
**菜单位置**: 风险监控 > 公告监控
**组件文件**: `/src/views/announcement/AnnouncementMonitor.vue`

---

### 8. 实时监控

#### 8.1 实时监控 (`/realtime`)
**URL**: http://localhost:3001/realtime
**菜单位置**: 实时监控（可能已启用）
**组件文件**: `/src/views/RealTimeMonitor.vue`

#### 页面元素：
- **SSE状态监控**
  - 连接状态：已连接
  - 最后更新时间
  - 自动重连状态

- **实时推送面板**
  - 训练进度
  - 回测进度
  - 风险告警
  - 系统消息

- **API测试工具**
  - SSE连接测试
  - 数据推送测试
  - 错误模拟

---

### 9. 交易管理

#### 9.1 交易管理 (`/trade`)
**URL**: http://localhost:3001/trade
**菜单位置**: 交易管理
**组件文件**: `/src/views/TradeManagement.vue`

---

### 10. 量化策略

#### 10.1 策略管理 (`/strategy`)
**URL**: http://localhost:3001/strategy
**菜单位置**: 量化策略 > 策略管理
**组件文件**: `/src/views/StrategyManagement.vue`

##### 子页面：

- **策略列表** (`/strategy`)
  - 组件：`/src/views/strategy/StrategyList.vue`

  - 策略名称、状态、创建时间列表

- **单次运行** (`/strategy/single-run`)
  - 组件：`/src/views/strategy/SingleRun.vue`
  - 策略参数配置、执行按钮

- **批量扫描** (`/strategy/batch-scan`)
  - 组件：`/src/views/strategy/BatchScan.vue`
  - 批量股票选择、扫描条件设置

- **结果查询** (`/strategy/results-query`)
  - 组件：`/src/views/strategy/ResultsQuery.vue`
  - 回测结果查询、筛选条件

- **统计分析** (`/strategy/stats-analysis`)
  - 组件：`src/views/strategy/StatsAnalysis.vue`
  - 收益分析图表、胜率统计

#### 10.2 回测分析 (`/backtest`)
**URL**: http://localhost:3001/backtest
**菜单位置**: 量化策略 > 回测分析
**组件文件**: `/src/views/BacktestAnalysis.vue`

---

### 11. 任务管理

#### 11.1 任务管理 (`/tasks`)
**URL**: http://localhost:3001/tasks
**菜单位置**: 任务管理
**组件文件**: `/src/views/TaskManagement.vue`

---

### 12. 系统设置

#### 12.1 系统设置 (`/settings`)
**URL**: http://localhost:3001/settings
**菜单位置**: 系统设置
**组件文件**: `/src/views/Settings.vue`

---

### 13. 系统管理

#### 13.1 系统架构 (`/system/architecture`)
**URL**: http://localhost:3001/system/architecture
**菜单位置**: 系统管理 > 系统架构
**组件文件**: `/src/views/system/Architecture.vue`

#### 页面元素：
- **架构概览**
  - 标题：Week 3 简化架构
  - 说明：移除了MySQL和Redis，专注于PostgreSQL+TDengine双核心架构

- **数据库架构图**
  - TDengine：高频时序数据（Tick、分钟K线）
  - PostgreSQL：所有其他数据类型

- **连接参数表格**
  | 参数 | 值 |
  |------|-----|
  | TDengine Host | 192.168.123.104 |
  | TDengine Port | 6030 |
  | PostgreSQL Host | 192.168.123.104 |
  | PostgreSQL Port | 5438 |

- **状态指标**
  - 连接池状态
  - 健康检查状态
  - 性能指标

#### 13.2 数据库监控 (`/system/database-monitor`)
**URL**: http://localhost:3001/system/database-monitor
**菜单位置**: 系统管理 > 数据库监控
**组件文件**: `/src/views/system/DatabaseMonitor.vue`

#### 13.3 智能数据源测试 (`/smart-data-test`)
**URL**: http://localhost:3001/smart-data-test
**菜单位置**: 系统管理 > 智能数据源测试
**组件文件**: `/src/views/SmartDataSourceTest.vue`

---

### 14. 功能演示

#### 14.1 Phase 4 Dashboard (`/demo/phase4-dashboard`)
**URL**: http://localhost:3001/demo/phase4-dashboard
**菜单位置**: 功能演示 > Phase 4 Dashboard
**组件文件**: `/src/views/demo/Phase4Dashboard.vue`

#### 14.2 Wencai (`/demo/wencai`)
**URL**: http://localhost:3001/demo/wencai
**菜单位置**: 功能演示 > Wencai
**组件文件**: `/src/views/demo/Wencai.vue`

#### 页面元素：
- **标签导航**
  - 查询：主查询界面
  - 我的：保存的查询
  - 分析：查询分析
  - 指南：使用指南

- **预定义查询模板**（9个）
  1. "连续3天上涨的股票"
  2. "今日强势股"
  3. "低估值高成长"
  4. "高成交量突破"
  5. "技术指标金叉"
  6. "主力资金流入"
  7. "热点板块龙头"
  8. "破位新高"
  9. "回调企稳"

#### 14.3 OpenStock (`/demo/openstock`)
**URL**: http://localhost:3001/demo/openstock
**菜单位置**: 功能演示 > OpenStock
**组件文件**: `/src/views/demo/OpenStockDemo.vue`

#### 14.4 PyProfiling (`/demo/pyprofiling`)
**URL**: http://localhost:3001/demo/pyprofiling
**菜单位置**: 功能演示 > PyProfiling
**组件文件**: `/src/views/demo/PyprofilingDemo.vue`

#### 14.5 Freqtrade (`/demo/freqtrade`)
**URL**: http://http://localhost:3001/demo/freqtrade
**菜单位置**: 功能演示 > Freqtrade
**组件文件**: `/src/views/demo/FreqtradeDemo.vue`

#### 14.6 Stock Analysis (`/demo/stock-analysis`)
**URL**: http://localhost:3001/demo/stock-analysis
**菜单位置**: 功能演示 > Stock-Analysis
**组件文件**: `/src/views/demo/StockAnalysisDemo.vue`

#### 14.7 TDX Python (`/demo/tdxpy`)
**URL**: http://localhost:3001/demo/tdxpy
**菜单位置**: 功能演示 > pytdx
**组件文件**: `/src/views/demo/TdxpyDemo.vue`

---

### 15. 特殊页面

#### 15.1 登录页 (`/login`)
**URL**: http://localhost:3001/login
**组件文件**: `/src/views/Login.vue`
**状态**: 认证功能已禁用

#### 15.2 404页面 (`/not-found`)
**URL**: http://localhost:3001/not-found
**组件文件**: `/src/views/NotFound.vue`

---

## 📊 UI组件规范

### 通用组件
- **Element Plus组件库**
  - el-table：数据表格
  - el-card：卡片容器
  - el-tabs：标签页
  - el-form：表单
  - el-select：选择器
  - el-date-picker：日期选择器
  - el-button：按钮
  - el-icon：图标

### 数据展示格式
- **数值显示**：
  - 价格：2位小数（如：150.25）
  - 百分比：2位小数加%符号（如：+5.23%）
  - 金额：千分位分隔（如：1,000,000）

- **日期格式**：YYYY-MM-DD
- **时间格式**：HH:mm:ss

### 状态指示
- **加载状态**：Loading spinner
- **错误状态**：红色警告
- **成功状态**：绿色提示
- **警告状态**：黄色警告

---

## 🔗 路由配置说明

- **基础路径**：http://localhost:3001
- **模式**：History模式（支持浏览器前进/后退）
- **404处理**：自动跳转到 /not-found 页面
- **权限控制**：基于角色的菜单过滤

## 📝 备注

1. **端口配置**：前端当前运行在3001端口，可根据需要调整
2. **数据源**：已启用真实数据模式，实时从后端API获取
3. **实时更新**：部分页面支持SSE（Server-Sent Events）实时推送
4. **响应式设计**：支持移动端和桌面端适配

---

**最后更新**：2025-12-06
**版本**：v2.0.0