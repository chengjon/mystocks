# MyStocks Web 界面重构设计需求文档

> 定位: 历史设计需求草案，仅供回溯，不代表当前主线状态
> 约束: 不能作为当前实施规范；当前实施仍以活跃规范、代码与已批准方案为准

> 生成日期: 2026-03-29
> 审核修订: 2026-03-29（基于 router/index.ts 和实际代码库验证）
> 用途: 通过 Google Stitch 等 AI 工具重新设计 UI

---

## 1. 系统概览与目标

*   **核心目标**：个人量化交易全栈管理平台，支持多策略回测、实盘交易、风险监控
*   **当前痛点**：
  * 页面数量庞大（260 个 Vue 文件），信息密度过高
  * 存在 ArtDeco 和旧版两套设计系统共存，需要统一
  * 部分页面使用 Mock 数据，真实/模拟状态混杂
*   **设计偏好**：ArtDeco 装饰艺术风格，深色模式为主，需要现代化重构
*   **平台支持策略**：仅支持桌面端 Web（最小分辨率 1280x720），不做移动端/平板适配

---

## 2. 核心功能模块

### 模块 A：行情/看板 (Market)

| 功能 | 路由路径 | 核心指标 |
|------|----------|----------|
| 实时行情 | `/market/realtime` | 涨跌家数、涨跌幅排行、龙虎榜 |
| K线分析 | `/market/technical` | 技术指标、买卖信号、多周期切换 |
| 龙虎榜 | `/market/lhb` | 机构买卖、营业部排行、资金流入 |

### 模块 B：数据分析 (Data)

| 功能 | 路由路径 | 内容 |
|------|----------|------|
| 板块动向 | `/data/industry` | 行业板块热度、资金流入流出 |
| 概念动向 | `/data/concept` | 概念板块轮动、题材热度 |
| 资金流向 | `/data/fund-flow` | 主/散户资金流向、大单监控 |
| 指标分析 | `/data/indicator` | 技术指标自定义分析、组合指标 |

### 模块 C：自选管理 (Watchlist)

| 功能 | 路由路径 | 核心功能 |
|------|----------|----------|
| 组合管理 | `/watchlist/manage` | 自选股组合管理、分组 |
| 信号雷达 | `/watchlist/signals` | 策略信号聚合、触发提醒 |
| 策略选股 | `/watchlist/screener` | 条件筛选、批量选股 |

### 模块 D：策略管理 (Strategy)

| 功能 | 路由路径 | 展示内容 |
|------|----------|----------|
| 策略仓库 | `/strategy/repo` | 策略列表、收益曲线、运行状态 |
| 策略参数 | `/strategy/parameters` | 参数配置面板、参数调优 |
| 策略信号 | `/strategy/signals` | 实时信号、触发条件、信号强度 |
| 回测引擎 | `/strategy/backtest` | 资金曲线、回撤、胜率、绩效归因 |
| GPU监控 | `/strategy/gpu` | 加速状态、显存使用、任务队列 |
| 参数优化 | `/strategy/opt` | 参数寻优结果、最优参数组合 |
| 仓位管理 | `/strategy/pos` | 当前持仓、配仓比例、仓位预警 |

### 模块 E：交易管理/实盘 (Trading)

| 功能 | 路由路径 | 核心功能 |
|------|----------|----------|
| 头寸管理 | `/trade/positions` | 持仓明细、市值占比、成本价 |
| 交易操作 | `/trade/terminal` | 一键下单、撤单、委托确认 |
| 信号监控 | `/trade/signals` | 策略信号、触发提醒、信号过滤 |
| 持仓透视 | `/trade/portfolio` | 多维度持仓分析、行业分布、风险敞口 |
| 历史对账 | `/trade/history` | 成交记录、委托状态、手续费统计 |

### 模块 F：风控与预警 (Risk)

| 功能 | 路由路径 | 功能描述 |
|------|----------|----------|
| 风险管理 | `/risk/management` | 风控中心面板、整体风险评分 |
| 风险概览 | `/risk/overview` | VaR、CVaR、敞口监控、保证金 |
| 组合盈亏 | `/risk/pnl` | 实时盈亏、浮动收益、日盈亏曲线 |
| 止损雷达 | `/risk/stop-loss` | 止损触发条件、预警阈值设置 |
| 告警中心 | `/risk/alerts` | 告警规则、实时推送、多渠道 |
| 舆情预警 | `/risk/news` | 公告监控、异常预警、新闻聚合 |

### 模块 G：系统设置 (System)

| 功能 | 路由路径 |
|------|----------|
| 系统配置 | `/system/config` |
| 健康矩阵 | `/system/health` |
| API终端 | `/system/api` |
| 数据源管理 | `/system/data` |

### 模块 H：详情页 (Detail)

| 功能 | 路由路径 | 说明 |
|------|----------|------|
| 股票图形 | `/detail/graphics/:symbol` | K线分析详情 |
| 相关新闻 | `/detail/news/:symbol` | 个股公告/新闻 |

### 仪表盘 (Dashboard)

| 功能 | 路由路径 |
|------|----------|
| 交易室 | `/dashboard` |

### 认证页面

| 功能 | 路由路径 |
|------|----------|
| 登录 | `/login` |

---

## 3. 核心用户流程 (User Flow)

### 每日工作流程

1. **开盘前 (9:00-9:30)**
   - 访问 `/dashboard` 交易室查看大盘指数
   - 检查 `/strategy/repo` 策略运行状态
   - 审视 `/risk/overview` 风险敞口
   - 检查 `/watchlist/manage` 自选股动态

2. **盘中 (9:30-15:00)**
   - 监控 `/trade/signals` 策略信号
   - 通过 `/trade/terminal` 执行交易操作
   - 关注 `/risk/alerts` 告警中心
   - 查看 `/watchlist/signals` 信号雷达

3. **盘后 (15:00-17:00)**
   - 分析 `/strategy/backtest` 回测结果
   - 审视 `/trade/history` 历史对账
   - 查看 `/risk/pnl` 组合盈亏日报

---

## 4. 数据展示优先级 (非常重要)

### 必须第一眼看到 (Dashboard 首屏)

1. **大盘指数** - 上证/深证/创业板实时走势
2. **策略运行状态** - 运行中/暂停/异常 数量统计
3. **实时告警数量** - 未处理告警徽章

### 可以折叠/放在二级页面

| 数据 | 推荐位置 |
|------|----------|
| 详细技术指标 | `/market/technical` (独立页面) |
| 历史回测记录 | `/strategy/backtest` (分页列表) |
| 系统健康详情 | `/system/health` (展开面板) |
| GPU 显存详情 | `/strategy/gpu` (弹出详情) |
| 单一持仓详情 | `/trade/positions` (行内展开) |

---

## 5. 交互需求

### 手动干预功能

* **紧急平仓按钮** - `/trade/terminal` 页面需要醒目的紧急操作入口
* **手动调仓** - 支持手动修改配仓比例
* **一键撤单** - 批量撤单功能

### 筛选和搜索功能

* **股票代码搜索** - 支持 6 位代码模糊搜索
* **板块筛选** - 行业/概念多选
* **日期范围选择** - 自定义起止日期
* **状态筛选** - 持仓状态/告警级别/运行状态

---

## 6. 当前技术栈

* **前端框架**: Vue 3.4 + Composition API
* **UI 组件库**: Element Plus 2.13
* **图表库**: ECharts 5.5 + KLineCharts 9.8
* **状态管理**: Pinia 2.2
* **路由**: Vue Router 4.3
* **构建工具**: Vite 5.4

---

## 7. 设计系统现状

* **主设计系统**: ArtDeco (装饰艺术风格)
* **组件位置**: `web/frontend/src/components/artdeco/`（含 core/base/business/charts/trading/specialized/advanced 7 个子目录）
* **布局组件**: `src/layouts/ArtDecoLayoutEnhanced.vue`
* **现状**: 存在旧版 + ArtDeco 两套组件，需要统一

---

## 8. 页面统计

| 分类 | 数量 | 说明 |
|------|------|------|
| Vue 文件 (views) | 260 | 含 artdeco-pages、demo、archive 等 |
| ArtDeco 组件 | 73 | 分布在 7 个子目录 |
| 路由模块 | 8 大类 | market/data/watchlist/strategy/trade/risk/system/detail + dashboard/login |
| API 端点 | 400+ | web/backend/app/api/ 下的路由函数 |

---

## 9. 下一步建议

1. 统一设计系统（清理旧版组件）
2. 优化 Dashboard 信息密度
3. 建立数据优先级规则
4. 适配深色/浅色双主题

---

*本文档基于 `web/frontend/src/router/index.ts`、`package.json` 和代码库实际文件统计验证生成*
