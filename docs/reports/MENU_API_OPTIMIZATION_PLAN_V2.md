# MyStocks Web菜单与API优化方案 v2.1

**项目**: MyStocks 量化交易平台  
**日期**: 2026-01-24  
**版本**: v2.1（ArtDeco合规版）  
**状态**: 待审批（已更新A股颜色规范）  
**类型**: 优化方案报告  
**设计理念**: 以用户为中心的渐进式优化 + **ArtDeco设计系统合规** + **A股颜色规范**

---

## 📋 目录

1. [执行摘要](#执行摘要)
2. [现状诊断](#现状诊断)
3. [菜单架构优化](#菜单架构优化)
4. [API全景盘点](#api全景盘点)
5. [未利用API利用方案](#未利用api利用方案)
6. [UI/UX设计改进](#uiux设计改进) ← 已更新：ArtDeco合规 + A股颜色
7. [实施路线图](#实施路线图)
8. [验收标准](#验收标准)

---

## 执行摘要

### 🎯 核心优化目标

基于v1.0方案，本版本进行以下关键改进：

| 改进维度 | v1.0 | v2.1 | 提升 |
|----------|------|------|------|
| **菜单结构** | 已有描述 | 详细树状图 + 交互逻辑 | 更清晰 |
| **API盘点** | 部分盘点 | 全量61个文件逐一分析 | 更完整 |
| **UI/UX** | 简单组件 | ArtDeco合规 + A股颜色规范 | 更专业 |
| **实施方案** | 模糊 | 明确验收标准 + 里程碑 | 更可控 |
| **风险控制** | 一般 | 详细回退方案 | 更安全 |

### 📊 关键数据

| 维度 | 数量 | 说明 |
|------|------|------|
| 后端API文件 | 61个 | 完整清单见附录 |
| 前端路由 | 28个 | 已实现28个 |
| 待优化页面 | 3个 | 自选股、行业池、筛选器 |
| ArtDeco组件 | 66个 | 6大类完整组件库 |
| 预计工时 | 5-7天 | 分3阶段执行 |

### ✨ v2.1核心亮点

1. **渐进式菜单重构**：保留所有功能，逐步优化导航结构
2. **API价值矩阵**：按业务价值和实现难度分类所有未使用API
3. **ArtDeco设计系统赋能**：充分利用ArtDeco 2.0设计系统（66个组件）
4. **A股颜色规范合规**：红色=上涨，绿色=下跌（符合A股习惯）
5. **用户体验优先**：每个改动都有明确的用户价值

### 📚 设计系统参考文档

| 文档 | 路径 | 说明 |
|------|------|------|
| ArtDeco实现报告 | `docs/web/ART_DECO_IMPLEMENTATION_REPORT.md` | 完整实现细节（725行） |
| ArtDeco快速参考 | `docs/web/ART_DECO_QUICK_REFERENCE.md` | 常用代码片段（820行） |
| ArtDeco组件目录 | `docs/web/ART_DECO_COMPONENTS_CATALOG.md` | 66个组件清单 |
| ArtDeco组件展示 | `docs/web/ART_DECO_COMPONENT_SHOWCASE_V2.md` | 组件示例 |
| ArtDeco设计指南 | `docs/design-references/artdeco-system-guide.md` | 设计原则 |
| ArtDeco界面设计 | `docs/design-references/artdeco-web-interface.md` | 完整设计规范 |

---

## 现状诊断

### 🔍 现有菜单结构分析

#### 当前问题诊断

**问题1：功能域划分模糊**
- "自选股管理"、"行业股票池"、"股票筛选器"分散在3个不同位置
- 用户需要多次点击才能找到相关功能
- 认知负荷高

**问题2：路由命名不规范**
- 部分路由使用中文，部分使用英文
- 命名不一致（如`/stocks/management` vs `/watchlist/manage`）
- 重定向逻辑复杂

**问题3：API利用率不均**
- 部分核心API使用率高（market.py 100%）
- 部分高级API完全未使用（stock_ratings_api.py 0%）
- 数据价值未能充分发挥

### 📊 功能使用热力图

```
用户访问频率分析（基于路由设计意图）：

┌─────────────────────────────────────────────────────────────┐
│  指挥中心     ████████░░  高频                              │
│  市场总览     ██████████  最高频                            │
│  ┗ 自选股     ████░░░░░░  中频 ← 散落在3处，访问困难        │
│  ┗ 交易管理   ██████░░░░  中高频                           │
│  ┗ 策略中心   █████░░░░░  中频                            │
│  ┗ 风险控制   ███░░░░░░░  低频                            │
│  ┗ 系统管理   ██░░░░░░░░  低频                            │
└─────────────────────────────────────────────────────────────┘
```

### 🎯 用户痛点矩阵

| 痛点 | 用户群体 | 发生频率 | 影响程度 |
|------|----------|----------|----------|
| 找不到"行业股票池" | 行业分析师 | 高 | 高 |
| 筛选器功能弱 | 量化研究员 | 高 | 高 |
| 自选股分组管理不便 | 个人投资者 | 中 | 中 |
| 新闻与自选股割裂 | 个人投资者 | 中 | 中 |
| 财报数据分散 | 价值投资者 | 低 | 中 |

---

## 菜单架构优化

### 🌳 目标菜单结构（v2.0）

```
MyStocks 量化交易平台
│
├─ 🏠 指挥中心                    [Dashboard]
│  └─ /dashboard                 仪表盘首页
│
├─ 📊 市场总览                    [Market] 9项
│  ├─ /market/realtime           实时行情 [LIVE]
│  ├─ /market/technical          技术指标
│  ├─ /market/fund-flow          资金流向
│  ├─ /market/etf                ETF行情
│  ├─ /market/concept            概念板块
│  ├─ /market/auction            竞价抢筹
│  ├─ /market/longhubang         龙虎榜
│  ├─ /market/institution        机构荐股
│  └─ /market/wencai             问财选股
│
├─ 📋 自选股 ⭐ [NEW]             [Watchlist] 3项 ← 新增功能域
│  ├─ /watchlist/manage          自选股管理 [核心重构]
│  ├─ /watchlist/industry-pools  行业股票池 [新增页面]
│  └─ /watchlist/screener        股票筛选器 [功能增强]
│
├─ 💼 交易管理                    [Trading] 4项
│  ├─ /trading/signals           交易信号
│  ├─ /trading/history           历史订单
│  ├─ /trading/positions         持仓监控
│  └─ /trading/attribution       绩效归因
│
├─ 🎯 策略中心                    [Strategy] 5项
│  ├─ /strategy/design           策略设计
│  ├─ /strategy/management       策略管理
│  ├─ /strategy/backtest         策略回测
│  ├─ /strategy/gpu-backtest     GPU加速回测 [PRO]
│  └─ /strategy/optimization     参数优化
│
├─ ⚠️ 风险控制                    [Risk] 5项
│  ├─ /risk/overview             风险概览
│  ├─ /risk/alerts               告警中心 [3]
│  ├─ /risk/indicators           风险指标
│  ├─ /risk/sentiment            舆情监控
│  └─ /risk/announcement         公告监控
│
└─ ⚙️ 系统管理                    [System] 5项
   ├─ /system/monitoring         运维监控
   ├─ /system/settings           系统设置
   ├─ /system/data-update        数据更新
   ├─ /system/data-quality       数据质量
   └─ /system/api-health         API健康
```

### 🎨 菜单设计原则

#### 1. 功能域相邻原则
- **市场总览** → 了解市场（数据消费）
- **自选股** → 管理关注（数据组织）
- **交易管理** → 执行交易（行动）
- **策略中心** → 策略开发（创造）

#### 2. 访问频率分层
- **顶层**（最多3项）：指挥中心、市场总览、自选股
- **中层**（3-5项）：交易管理、策略中心
- **底层**（2-3项）：风险控制、系统管理

#### 3. 功能完整性
- 每个功能域包含完整的生命周期操作
- 自选股域：查看（管理）→ 分析（筛选）→ 组织（行业池）

### 📐 交互规范

#### 导航行为设计

| 场景 | 预期行为 | 实现方式 |
|------|----------|----------|
| 进入功能域 | 显示该域的统计概览 | 面包屑自动生成 |
| 切换子菜单 | 平滑过渡，无白屏 | Vue transition |
| 深层嵌套 | 最多3层，超过则拆分 | 路由设计约束 |
| 快速跳转 | Ctrl+K 打开命令面板 | 全局快捷键 |

#### 状态反馈设计

| 状态 | 视觉表现 | 交互表现 |
|------|----------|----------|
| 加载中 | ArtDecoSkeleton骨架屏 | 禁用操作 |
| 成功 | 绿色Toast提示 | 自动消失 |
| 错误 | 红色Alert警告 | 可重试 |
| 空状态 | 插画+引导文案 | 提供快捷操作 |

---

## API全景盘点

### 📊 API价值矩阵

按**业务价值**和**实现难度**两个维度分类：

```
                    实现难度
                    低 ────────────────→ 高
              ┌─────────────────────────────┐
              │                             │
        高    │  🎯 快速-win              │  🌟 战略投资
              │  • watchlist增强          │  • 财报分析
业务          │  • 行业股票池             │  • 股票评级
价值          │  • 筛选器优化             │  • ML预测
              │                             │
              ├─────────────────────────────┤
              │  🔧 基础完善              │  💡 探索性
              │  • 缓存优化               │  • 情感分析
              │  • 错误处理               │  • 知识图谱
              │                             │
              └─────────────────────────────┘
                    低
```

### 📋 详细API清单（按模块分类）

#### 1. 核心业务API（已使用70%+）

| 模块 | API文件 | 端点数 | 已使用 | 使用率 | 状态 |
|------|---------|--------|--------|--------|------|
| **Market** | `market.py` | 8 | 8 | 100% | ✅ 完美 |
| **Dashboard** | `dashboard.py` | 1 | 1 | 100% | ✅ 完美 |
| **Trading** | `signals.py`, `history.py`, `positions.py` | 3 | 3 | 100% | ✅ 完美 |
| **Strategy** | `strategy_management.py` | 4 | 4 | 100% | ✅ 完美 |
| **Risk** | `risk_management.py` | 5 | 3 | 60% | ⚠️ 部分 |
| **System** | `monitoring.py`, `tasks.py` | 5+ | 4 | 80% | ✅ 良好 |

#### 2. 待利用API（高优先级）

| 模块 | API文件 | 端点数 | 优先级 | 建议方案 |
|------|---------|--------|--------|----------|
| **自选股增强** | `watchlist.py` | 6 | 🔴 高 | 行业池、分组管理 |
| **股票筛选** | `stock_search.py` | 1+ | 🔴 高 | 高级筛选器 |
| **行业分析** | `industry_concept_analysis.py` | 10+ | 🔴 高 | 行业股票池页面 |
| **公告新闻** | `announcement.py` | 2+ | 🟠 中 | 自选股新闻面板 |
| **财报数据** | `data.py`, `metrics.py` | 10+ | 🟠 中 | 财报分析页面 |

#### 3. 高级功能API（中优先级）

| 模块 | API文件 | 端点数 | 优先级 | 建议方案 |
|------|---------|--------|--------|----------|
| **股票评级** | `stock_ratings_api.py` | 10+ | 🟠 中 | 评级分析页面 |
| **技术分析** | `technical_analysis.py` | 10+ | 🟡 低 | 指标库增强 |
| **机器学习** | `ml.py` | 15+ | 🟡 低 | 智能选股推荐 |
| **问财** | `wencai.py` | 10+ | 🟡 低 | 智能选股集成 |

#### 4. 基础设施API（低优先级）

| 模块 | API文件 | 端点数 | 状态 | 说明 |
|------|---------|--------|------|------|
| **缓存** | `cache.py` | 5+ | ✅ 后端使用 | 无需前端 |
| **认证** | `auth.py` | 10+ | ✅ 已使用 | 登录/注册 |
| **监控** | `prometheus_exporter.py` | 5+ | ✅ 后端使用 | 运维监控 |

### 🎯 API利用优先级排序

| 优先级 | API模块 | 端点数 | 预期价值 | 实现难度 | 工时估算 |
|--------|---------|--------|----------|----------|----------|
| **P0** | 自选股增强 | 6 | 高 | 低 | 1天 |
| **P0** | 行业股票池 | 10+ | 高 | 中 | 2天 |
| **P1** | 股票筛选器增强 | 5+ | 高 | 低 | 0.5天 |
| **P1** | 新闻资讯集成 | 5+ | 中 | 中 | 1天 |
| **P2** | 财报分析 | 15+ | 中 | 中 | 2天 |
| **P2** | 股票评级 | 10+ | 中 | 中 | 1.5天 |

---

## 未利用API利用方案

### 🎯 方案1：自选股管理增强（P0）

#### 目标
充分利用`watchlist.py`的所有6个端点

#### 功能设计

```
自选股管理 (/watchlist/manage)
│
├─ 核心功能
│  ├─ 股票列表（GET /api/watchlist）
│  ├─ 添加股票（POST /api/watchlist/add）
│  ├─ 删除股票（DELETE /api/watchlist/{id}）
│  └─ 更新股票（PUT /api/watchlist/{id}）
│
├─ 新增功能（利用现有API）
│  ├─ 搜索功能（GET /api/watchlist/search）← 新增
│  ├─ 分组管理（利用PUT扩展）← 新增
│  └─ 批量操作（利用POST扩展）← 新增
│
└─ 增值功能
   ├─ 导入导出（扩展API）← 建议
   └─ 智能推荐（扩展API）← 建议
```

#### 页面布局

```
┌─────────────────────────────────────────────────────────────┐
│  自选股管理                              [+ 添加股票]      │
├─────────────────────────────────────────────────────────────┤
│  [搜索...]  [筛选▼]  [分组▼]  [批量操作▼]  [导出▼]        │
├──────────────────┬────────────────────────────────────────┤
│  📋 分组列表     │  📊 股票列表                              │
│                 │                                          │
│  ★ 全部 (28)    │  ┌─────────────────────────────────┐    │
│  📌 重点关注(5) │  │ 000001 平安银行    ¥12.35 +0.52% │    │
│  📈 策略股(10)  │  │ 000002 万 科Ａ    ¥15.20 -0.35% │    │
│  🏦 银行股(8)   │  │ 600036 招商银行    ¥45.80 +1.20% │    │
│  🏭 地产股(5)   │  │ ...                              │    │
│                 │  └─────────────────────────────────┘    │
│  [+ 新建分组]    │                                          │
└──────────────────┴────────────────────────────────────────┘
```

#### API调用设计

```typescript
// services/watchlistService.ts

export interface WatchlistAPI {
  // 核心CRUD
  getList(params?: ListParams): Promise<WatchlistItem[]>
  add(item: AddItemRequest): Promise<WatchlistItem>
  remove(id: number): Promise<void>
  update(id: number, data: UpdateItemRequest): Promise<WatchlistItem>
  
  // 搜索（未使用API）
  search(query: SearchRequest): Promise<WatchlistItem[]>
  
  // 分组管理（扩展功能）
  createGroup(name: string): Promise<Group>
  deleteGroup(id: number): Promise<void>
  moveToGroup(itemId: number, groupId: number): Promise<void>
  
  // 批量操作（扩展功能）
  batchAdd(items: AddItemRequest[]): Promise<BatchResult>
  batchRemove(ids: number[]): Promise<BatchResult>
}
```

### 🎯 方案2：行业股票池页面（P0）

#### 目标
利用`industry_concept_analysis.py`创建独立行业管理页面

#### 功能设计

```
行业股票池 (/watchlist/industry-pools)
│
├─ 行业概览
│  ├─ 行业分类（银行、科技、医药等12大类）
│  ├─ 行业涨跌排行（今日/周/月）
│  └─ 行业资金流向
│
├─ 行业详情
│  ├─ 行业热门股（按涨跌幅/成交额排序）
│  ├─ 行业成分股列表
│  ├─ 行业基本面（PE、PB均值）
│  └─ 行业新闻
│
└─ 自选股联动
   ├─ 一键添加到自选
   ├─ 从自选移除
   └─ 分组管理
```

#### 页面布局

```
┌─────────────────────────────────────────────────────────────────────┐
│  行业股票池                                            [刷新数据] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ 🏦 银行 │ │ 💻 科技 │ │ 💊 医药 │ │ ⚡ 能源 │ │ 🏭 材料 │ ...   │
│  │ +1.2%  │ │ +2.5%  │ │ -0.8%  │ │ +0.5%  │ │ +1.1%  │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│  🏦 银行业                            [自选股管理] [行业对比]       │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 热门股票         │ 涨跌幅    │ 成交额    │ 自选              │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │ 601398 工商银行   │ +1.25%   │ 28.5亿   │ ⭐               │    │
│  │ 600036 招商银行   │ +2.10%   │ 15.2亿   │ ⭐               │    │
│  │ 000001 平安银行   │ +0.85%   │ 8.5亿    │                   │    │
│  │ ...                                                             │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### API调用设计

```typescript
// services/industryService.ts

export interface IndustryAPI {
  // 行业列表
  getIndustryList(): Promise<IndustryCategory[]>
  
  // 行业概览
  getIndustryOverview(industryId: string): Promise<IndustryOverview>
  
  // 行业热门股
  getIndustryHotStocks(industryId: string, sortBy?: string): Promise<StockItem[]>
  
  // 行业成分股
  getIndustryStocks(industryId: string, params?: FilterParams): Promise<PaginatedResult<StockItem>>
  
  // 自选股联动
  addToWatchlist(symbol: string, groupId?: string): Promise<void>
  removeFromWatchlist(symbol: string): Promise<void>
}
```

### 🎯 方案3：股票筛选器增强（P0）

#### 目标
利用`stock_search.py`增强筛选功能，集成更多API

#### 功能设计

```
股票筛选器 (/watchlist/screener)
│
├─ 基础筛选
│  ├─ 代码/名称搜索
│  ├─ 交易所筛选（上交所/深交所/港交所/美股）
│  └─ 股票类型筛选（A股/ETF/港股/ADR）
│
├─ 条件筛选（新增）
│  ├─ 估值指标（PE、PB、PS、EV/EBITDA）
│  ├─ 成长指标（营收增速、净利润增速、ROE）
│  ├─ 规模指标（市值、流通市值）
│  ├─ 技术指标（RSI、MACD、布林带位置）
│  └─ 质量指标（资产负债率、流动比率）
│
├─ 智能筛选（新增）
│  ├─ 均线多头排列
│  ├─ 低估值高成长（PEG < 1）
│  ├─ 连续放量上涨
│  └─ 创新高/新低
│
└─ 结果管理
   ├─ 保存筛选条件
   ├─ 导出结果
   └─ 一键添加到自选
```

#### 页面布局

```
┌─────────────────────────────────────────────────────────────────────┐
│  股票筛选器                              [保存条件] [导出结果]     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────┐  ┌─────────────────────────┐          │
│  │ 📊 估值指标            │  │ 📈 成长指标              │          │
│  │ PE: 0 ~ 50            │  │ 营收增速: > 10%          │          │
│  │ PB: 0 ~ 10            │  │ ROE: > 8%               │          │
│  │ 股息率: > 2%           │  │ 净利润增速: > 15%        │          │
│  └─────────────────────────┘  └─────────────────────────┘          │
│                                                                      │
│  ┌─────────────────────────┐  ┌─────────────────────────┐          │
│  │ 📦 规模指标            │  │ 🎯 技术指标              │          │
│  │ 市值: 100亿 ~ 5000亿   │  │ RSI: 0 ~ 80             │          │
│  │ 成交额: > 1亿          │  │ MACD: 金叉/死叉          │          │
│  └─────────────────────────┘  └─────────────────────────┘          │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│  筛选结果: 128只股票                              [一键添加到自选] │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 代码     │ 名称    │ PE   │ ROE  │ 涨跌幅  │ 自选    │ 操作 │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │ 000001   │ 平安银行 │ 5.2  │ 12.5 │ +1.25%  │ ⭐      │ 添加 │    │
│  │ 600036   │ 招商银行 │ 6.8  │ 15.2 │ +2.10%  │         │ 添加 │    │
│  │ ...                                                           │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 🎯 方案4：新闻资讯集成（P1）

#### 目标
利用`announcement.py`为自选股页面增加新闻资讯面板

#### 功能设计

```
集成位置：自选股管理页面右侧面板
│
├─ 智能新闻聚合
│  ├─ 根据自选股自动聚合相关新闻
│  ├─ 按时间/来源/情感筛选
│  └─ 实时推送（WebSocket）
│
├─ 情感分析
│  ├─ 自动判断利好/中性/负面
│  ├─ 情感关键词高亮
│  └─ 情感趋势图
│
└─ 股票关联
   ├─ 新闻中股票自动高亮
   ├─ 点击股票快速查看
   └─ 相关股票推荐
```

#### API调用设计

```typescript
// services/newsService.ts

export interface NewsAPI {
  // 新闻列表
  getNewsList(params?: NewsParams): Promise<PaginatedResult<NewsItem>>
  
  // 自选股相关新闻
  getWatchlistRelatedNews(watchlist: string[]): Promise<NewsItem[]>
  
  // 单只股票新闻
  getStockNews(symbol: string): Promise<NewsItem[]>
  
  // 情感分析
  getNewsSentiment(newsId: string): Promise<SentimentResult>
  
  // WebSocket实时推送
  subscribeNews(symbols: string[]): Observable<NewsItem>
}
```

### 🎯 方案5：财报分析页面（P2）

#### 目标
利用`data.py`、`metrics.py`创建独立财报分析功能

#### 功能设计

```
财报分析 (/watchlist/financial-analysis)
│
├─ 股票选择
│  ├─ 从自选股选择
│  ├─ 搜索股票
│  └─ 历史记录
│
├─ 核心指标卡片
│  ├─ PE/PB/PS/EV
│  ├─ ROE/ROA/ROIC
│  ├─ 营收/净利润增长
│  └─ 毛利率/净利率
│
├─ 趋势图表
│  ├─ 5年/10年数据
│  ├─ 同行业对比
│  └─ 雷达图对比
│
└─ 操作功能
   ├─ 导出Excel
   ├─ 保存到收藏
   └─ 分享报告
```

---

## UI/UX设计改进

### 🎨 ArtDeco设计系统应用

本项目已集成完整的 **ArtDeco Design System v2.0**，包含66个专业组件。所有新增页面必须遵循ArtDeco设计规范，确保视觉一致性和用户体验统一。

#### 设计原则

1. **一致性**
   - 所有新增页面使用统一的ArtDeco组件库
   - 遵循ArtDeco 2.0设计规范
   - 保持视觉语言统一

2. **渐进式披露**
   - 默认显示核心信息
   - 高级功能通过展开/折叠展示
   - 避免信息过载

3. **即时反馈**
   - 操作后立即反馈状态
   - 加载状态使用骨架屏
   - 错误状态提供解决建议

#### 组件使用规范

| 组件 | 用途 | 使用场景 | 路径 |
|------|------|----------|------|
| `ArtDecoCard` | 容器组件 | 所有卡片、面板 | `@/components/artdeco/base/` |
| `ArtDecoButton` | 操作按钮 | 主要操作、次要操作、文字链接 | `@/components/artdeco/base/` |
| `ArtDecoInput` | 输入控件 | 搜索、筛选条件 | `@/components/artdeco/base/` |
| `ArtDecoTable` | 数据表格 | 股票列表、结果展示 | `@/components/artdeco/trading/` |
| `ArtDecoFilterBar` | 筛选栏 | 条件筛选面板 | `@/components/artdeco/business/` |
| `ArtDecoStatCard` | 统计卡片 | 概览数据 | `@/components/artdeco/base/` |
| `ArtDecoBreadcrumb` | 面包屑 | 导航路径 | `@/components/artdeco/core/` |
| `ArtDecoDialog` | 弹窗 | 确认操作、详情展示 | `@/components/artdeco/base/` |
| `ArtDecoBadge` | 徽章 | 状态标签、涨跌标识 | `@/components/artdeco/base/` |

#### A股颜色语义规范 ⚠️

**重要**：A股市场颜色约定与西方市场相反：
- **红色** = 上涨/正面 (涨)
- **绿色** = 下跌/负面 (跌)

```scss
// ArtDeco设计系统A股颜色定义
var(--artdeco-color-up)        // #FF5252 - 红色 (上涨/利好)
var(--artdeco-color-down)      // #00E676 - 绿色 (下跌/利空)
var(--artdeco-color-flat)      // #B0B3B8 - 灰色 (平盘/中性)
```

| 颜色 | 色值 | 语义 | 使用场景 |
|------|------|------|----------|
| 红色 | `#FF5252` | 上涨/正面 | 涨幅、正面新闻、成功状态 |
| 绿色 | `#00E676` | 下跌/负面 | 跌幅、负面新闻、风险提示 |
| 灰色 | `#B0B3B8` | 中性 | 次要信息、禁用状态、平盘 |
| 金色 | `#D4AF37` | 主品牌色 | 品牌元素、重要操作、标题 |

#### ArtDeco组件使用示例

```vue
<template>
  <!-- 股票涨跌标识（A股：红涨绿跌） -->
  <span class="stock-change" :class="change > 0 ? 'up' : 'down'">
    {{ change > 0 ? '+' : '' }}{{ change }}%
  </span>

  <!-- 自选股管理页面 -->
  <ArtDecoCard title="自选股管理" subtitle="管理您的关注股票">
    <ArtDecoInput
      v-model="searchQuery"
      label="搜索股票"
      placeholder="输入代码或名称"
    />
    <ArtDecoTable :data="stockList" :columns="columns">
      <template #change="{ row }">
        <ArtDecoBadge
          :text="formatChange(row.change)"
          :variant="row.change >= 0 ? 'rise' : 'fall'"
        />
      </template>
    </ArtDecoTable>
  </ArtDecoCard>
</template>

<script setup lang="ts">
import { ArtDecoCard, ArtDecoInput, ArtDecoTable, ArtDecoBadge } from '@/components/artdeco'

// A股颜色类名映射
const changeClass = (change: number) => change >= 0 ? 'text-red' : 'text-green'
</script>

<style scoped lang="scss">
.stock-change {
  &.up {
    color: var(--artdeco-color-up);    // 红色 - 上涨
  }
  &.down {
    color: var(--artdeco-color-down);  // 绿色 - 下跌
  }
}
</style>
```

#### 设计系统文件参考

| 文档 | 路径 | 用途 |
|------|------|------|
| 实现报告 | `docs/web/ART_DECO_IMPLEMENTATION_REPORT.md` | 完整实现细节 |
| 快速参考 | `docs/web/ART_DECO_QUICK_REFERENCE.md` | 常用代码片段 |
| 组件目录 | `docs/web/ART_DECO_COMPONENTS_CATALOG.md` | 66个组件清单 |
| 设计指南 | `docs/design-references/artdeco-system-guide.md` | 设计原则 |
| 组件源码 | `web/frontend/src/components/artdeco/` | Vue组件源码 |
| 设计令牌 | `web/frontend/src/styles/artdeco-*.scss` | SCSS变量和mixin |

#### 财务专用设计令牌

ArtDeco 2.0提供了丰富的财务专用设计令牌：

```scss
// 技术指标
var(--artdeco-indicator-macd-positive)      // #00E676 - MACD阳性
var(--artdeco-indicator-macd-negative)      // #FF5252 - MACD阴性
var(--artdeco-indicator-rsi-overbought)     // #FF5252 - RSI超买
var(--artdeco-indicator-rsi-oversold)       // #00E676 - RSI超卖

// 风险等级
var(--artdeco-risk-low)                      // #00E676 - 低风险
var(--artdeco-risk-medium)                   // #FFD700 - 中风险
var(--artdeco-risk-high)                     // #FF5252 - 高风险

// GPU状态
var(--artdeco-gpu-normal)                    // #00E676 - 正常
var(--artdeco-gpu-busy)                      // #FFD700 - 繁忙
var(--artdeco-gpu-overload)                  // #FF5252 - 过载
```

#### 导入样式

```scss
// 在每个.vue文件中导入
@import '@/styles/artdeco-tokens.scss';
@import '@/styles/artdeco-patterns.scss';
@import '@/styles/artdeco-financial.scss';  // 财务专用令牌
```

### 📐 响应式设计规范

#### 断点定义

| 断点 | 屏幕宽度 | 布局变化 |
|------|----------|----------|
| `xs` | < 768px | 不支持（仅桌面端） |
| `sm` | 768px - 1024px | 不支持 |
| `md` | 1024px - 1440px | 侧边栏收起 |
| `lg` | 1440px - 1920px | 标准布局 |
| `xl` | > 1920px | 宽屏布局 |

#### 布局模板

```
桌面端 (1440px+):
┌─────────────────────────────────────────────────────────────────┐
│  Sidebar(320px)  │  Main Content(1120px+)                    │
├─────────────────────────────────────────────────────────────────┤
│                  │  Page Content                             │
│                  │  ┌─────────────────────────────────────┐ │
│                  │  │  Header                              │ │
│                  │  ├─────────────────────────────────────┤ │
│                  │  │  Stats                               │ │
│                  │  ├─────────────────────────────────────┤ │
│                  │  │  Main Content                       │ │
│                  │  └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### ♿ 无障碍设计

#### 基础要求

| 特性 | 要求 | 实现方式 |
|------|------|----------|
| 键盘导航 | 支持Tab/Enter导航 | semantic HTML + focus样式 |
| ARIA标签 | 所有交互元素有标签 | aria-label, aria-describedby |
| 颜色对比 | 4.5:1最低对比度 | WCAG 2.1 AA标准 |
| 屏幕阅读 | 支持NVDA/JAWS | 语义化标签 |

#### 实现示例

```vue
<!-- 按钮 -->
<ArtDecoButton
  variant="solid"
  @click="handleAdd"
  aria-label="添加股票到自选股"
>
  添加到自选
</ArtDecoButton>

<!-- 搜索框 -->
<ArtDecoInput
  v-model="searchQuery"
  placeholder="搜索股票代码或名称"
  aria-label="搜索股票"
/>

<!-- 表格 -->
<ArtDecoTable
  :data="stockList"
  aria-label="股票列表"
>
  <template #symbol="{ row }">
    <span role="link" @click="viewDetail(row)">
      {{ row.symbol }}
    </span>
  </template>
</ArtDecoTable>
```

---

## 实施路线图

### 📅 三阶段实施计划

#### Phase 1：基础优化（1-2天）

| 任务 | 内容 | 工时 | 验收标准 |
|------|------|------|----------|
| 菜单重构 | 创建`/watchlist`功能域 | 0.5天 | 路由正确，页面可访问 |
| 自选股增强 | 增强管理页面（分组、批量） | 1天 | 所有watchlist API被调用 |
| 筛选器优化 | 增强筛选条件 | 0.5天 | 筛选功能完整 |

**里程碑1**：用户可通过`/watchlist/manage`访问增强版自选股管理

#### Phase 2：新增页面（2-3天）

| 任务 | 内容 | 工时 | 验收标准 |
|------|------|------|----------|
| 行业股票池 | 创建独立页面 | 2天 | 行业数据完整，操作流畅 |
| 新闻面板 | 集成到自选股页面 | 1天 | 新闻实时推送，情感分析准确 |

**里程碑2**：用户可通过`/watchlist/industry-pools`访问行业股票池

#### Phase 3：高级功能（2天）

| 任务 | 内容 | 工时 | 验收标准 |
|------|------|------|----------|
| 财报分析 | 创建独立页面 | 1.5天 | 财报数据完整，图表准确 |
| 股票评级 | 创建独立页面 | 0.5天 | 评级数据完整 |

**里程碑3**：完整功能上线，API利用率达到85%+

### 🔄 开发流程

```
需求评审 → 设计评审 → 开发实现 → 代码评审 → 测试验证 → 上线部署
   │           │           │           │           │           │
   ▼           ▼           ▼           ▼           ▼           ▼
  明确需求    UI/UX评审   组件开发    PR审核     自动化测试   灰度发布
   
每个阶段产出：
- 需求评审：需求文档
- 设计评审：UI设计稿 + 交互说明
- 开发实现：代码 + 单元测试
- 代码评审：修改意见 + 最终代码
- 测试验证：测试报告
- 上线部署：部署文档 + 监控配置
```

### 🛡️ 回退方案

| 场景 | 回退方案 | 恢复时间 |
|------|----------|----------|
| 路由配置错误 | 使用git checkout恢复 | 5分钟 |
| API集成失败 | 使用Mock数据降级 | 10分钟 |
| 页面性能问题 | 懒加载 + 骨架屏 | 即时 |
| 用户反馈差 | A/B测试对比 | 1天 |

---

## 验收标准

### ✅ 功能验收

| 验收项 | 验收标准 | 测试方法 |
|--------|----------|----------|
| 路由正确 | 所有路由可正常访问 | 手动测试 + 自动化测试 |
| API调用 | 所有计划API被调用 | 接口日志审查 |
| 页面加载 | 首屏 < 2秒 | Lighthouse审计 |
| 交互反馈 | 操作响应 < 500ms | 性能监控 |
| 错误处理 | 错误信息友好 | 手动测试 |

### 🎨 UI/UX验收

| 验收项 | 验收标准 | 测试方法 |
|--------|----------|----------|
| 设计一致性 | 符合ArtDeco设计规范 | 设计评审 |
| 响应式适配 | 1440px+正常显示 | 浏览器测试 |
| 无障碍 | 满足WCAG 2.1 AA | 自动化测试 + 屏幕阅读 |
| 用户满意度 | NPS > 50 | 用户调研 |

### 📊 数据验收

| 验收项 | 验收标准 | 测试方法 |
|--------|----------|----------|
| API覆盖率 | 利用率 > 85% | 日志分析 |
| 数据准确性 | 与源数据100%一致 | 数据比对 |
| 实时性 | WebSocket延迟 < 1s | 性能监控 |

---

## 附录

### A. API端点完整清单

详见：`/opt/claude/mystocks_spec/web/backend/app/api/`

### B. 前端路由完整清单

详见：`/opt/claude/mystocks_spec/web/frontend/src/router/index.ts`

### C. ArtDeco组件清单

详见：`/opt/claude/mystocks_spec/web/frontend/src/components/artdeco/`

### D. 术语表

| 术语 | 定义 |
|------|------|
| ArtDeco | 项目设计系统 |
| P0/P1/P2 | 优先级分类（P0最高） |
| WCAG | Web内容无障碍指南 |
| NPS | 净推荐值 |

---

**文档版本**: v2.1  
**创建日期**: 2026-01-24  
**作者**: Claude Code AI  
**状态**: 待审批（已更新ArtDeco合规 + A股颜色规范）

**更新日志**:
- v2.1: 添加ArtDeco设计系统合规指南（2026-01-24）
- v2.0: 初始版本（2026-01-24）

---

## 审批流程

### 审批项

| 项 | 内容 | 负责人 | 日期 |
|---|------|--------|------|
| ✅ 菜单结构 | 确认"自选股"功能域位置和内容 | [待填写] | [待填写] |
| ✅ API清单 | 确认API优先级排序 | [待填写] | [待填写] |
| ✅ 实施方案 | 确认三阶段计划 | [待填写] | [待填写] |
| ✅ 验收标准 | 确认验收指标 | [待填写] | [待填写] |

### 审批签字

| 角色 | 姓名 | 签字 | 日期 |
|------|------|------|------|
| 产品负责人 | | | |
| 技术负责人 | | | |
| UI/UX负责人 | | | |
| 项目经理 | | | |

---

**审批后**: 请将本文档移至 `/opt/claude/mystocks_spec/docs/reports/APPROVED/` 目录，并更新版本号为v2.2。
