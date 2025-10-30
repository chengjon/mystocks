# Web 页面可视化元素清单 (v1.0)

## 说明
- **编号规则**: 页面(P)-模块(M)-元素(E), 如 P01-M01-E01
- **更新日期**: 2025-10-29
- **项目**: MyStocks 量化交易系统
- **Vue版本**: Vue 3 + Element Plus
- **前端路径**: /opt/claude/mystocks_spec/web/frontend/src

---

## 目录索引

### 核心页面 (P01-P06)
- [P01: 登录页](#p01-登录页-loginvue) - `/login`
- [P02: 仪表盘](#p02-仪表盘-dashboardvue) - `/dashboard` ⭐重点
- [P03: 市场行情](#p03-市场行情-marketvue) - `/market`
- [P04: 技术分析](#p04-技术分析-technicalanalysisvue) - `/technical` ⭐重点
- [P05: 自选股](#p05-自选股-watchlistvue) - `/watchlist`
- [P06: 指标库](#p06-指标库-indicatorlibraryvue) - `/indicators`

### 市场数据页面 (P07-P11)
- [P07: 资金流向](#p07-资金流向-fundflowpanelvue) - `/market-data/fund-flow`
- [P08: ETF行情](#p08-etf行情-etfdatatablevue) - `/market-data/etf`
- [P09: 竞价抢筹](#p09-竞价抢筹-chipracetablevue) - `/market-data/chip-race`
- [P10: 龙虎榜](#p10-龙虎榜-longhubangdatatablevue) - `/market-data/lhb` ⭐重点
- [P11: 系统设置](#p11-系统设置-settingsvue) - `/settings`

### 布局与导航 (L01)
- [L01: 主布局](#l01-主布局-layoutindexvue) - 侧边栏+顶部导航

---

## 页面-模块层级关系

### 核心功能页面
1. **登录页 (P01)** - `/login`
   - M01: 登录表单模块
   - M02: 操作按钮模块
   - M03: 测试账号提示模块

2. **仪表盘 (P02)** - `/dashboard` ⭐重点页面
   - M01: 统计卡片模块 (4个卡片)
   - M02: 市场热度中心模块 (4个Tab图表)
   - M03: 行业资金流向图表模块
   - M04: 板块表现模块 (4个Tab表格)

3. **市场行情 (P03)** - `/market`
   - M01: 功能开发中提示

4. **技术分析 (P04)** - `/technical` ⭐重点页面
   - M01: 工具栏模块 (股票搜索+日期+刷新+指标设置+配置管理)
   - M02: K线图表区域
   - M03: 指标选择面板 (抽屉)
   - M04: 数据统计信息栏

5. **自选股 (P05)** - `/watchlist`
   - M01: Tab切换模块 (用户自选/系统自选/策略自选/监控列表)
   - M02: 股票列表表格模块
   - M03: 操作按钮模块

6. **指标库 (P06)** - `/indicators`
   - M01: 页面头部模块
   - M02: 统计卡片模块 (6个卡片)
   - M03: 搜索筛选模块
   - M04: 指标详情卡片列表模块

### 市场数据页面
7. **资金流向 (P07)** - `/market-data/fund-flow`
   - M01: 查询表单模块
   - M02: 资金流向数据表格模块
   - M03: 资金流向趋势图模块

8. **ETF行情 (P08)** - `/market-data/etf`
   - M01: 查询工具栏模块
   - M02: ETF数据表格模块
   - M03: ETF详情抽屉模块

9. **竞价抢筹 (P09)** - `/market-data/chip-race`
   - M01: 查询工具栏模块
   - M02: 抢筹数据表格模块
   - M03: 统计信息卡片模块

10. **龙虎榜 (P10)** - `/market-data/lhb` ⭐重点页面
    - M01: 查询工具栏模块
    - M02: 龙虎榜数据表格模块
    - M03: 统计信息卡片模块
    - M04: 详情对话框模块

11. **系统设置 (P11)** - `/settings`
    - M01: 基本设置Tab
    - M02: 显示设置Tab
    - M03: 数据库配置Tab
    - M04: 用户管理Tab
    - M05: 运行日志Tab
    - M06: 关于Tab

### 布局组件
12. **主布局 (L01)** - 全局布局
    - M01: 侧边栏导航模块
    - M02: 顶部导航栏模块
    - M03: 内容区域模块

---

## 元素详情表

### P01: 登录页 (Login.vue)

**路由**: `/login`
**文件**: `views/Login.vue`

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P01-M01-E01 | 登录表单 | 用户名输入框 | el-input | type:text, size:large, prefix-icon:User | 接收用户名输入 | 本地表单 | - | 必填项 |
| P01-M01-E02 | 登录表单 | 密码输入框 | el-input | type:password, size:large, prefix-icon:Lock, show-password | 接收密码输入 | 本地表单 | - | 必填项,最少6位 |
| P01-M02-E01 | 操作按钮 | 登录按钮 | el-button | type:primary, size:large, loading:动态 | 提交登录表单 | POST /api/auth/login | - | 验证通过后触发 |
| P01-M03-E01 | 测试账号 | 测试账号提示 | el-divider + p | - | 显示测试账号信息 | 静态文本 | - | 管理员: admin/admin123 |
| P01-M03-E02 | 测试账号 | 测试账号提示 | p | - | 显示测试账号信息 | 静态文本 | - | 普通用户: user/user123 |

---

### P02: 仪表盘 (Dashboard.vue)

**路由**: `/dashboard`
**文件**: `views/Dashboard.vue`
**重要程度**: ⭐⭐⭐⭐⭐ (核心页面)

#### M01: 统计卡片模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P02-M01-E01 | 数据卡片 | 总股票数卡片 | el-card | - | 显示总股票数统计 | GET /api/dashboard/summary | - | 动态更新 |
| P02-M01-E02 | 数据卡片 | 活跃股票卡片 | el-card | - | 显示活跃股票数统计 | GET /api/dashboard/summary | - | 动态更新 |
| P02-M01-E03 | 数据卡片 | 数据更新卡片 | el-card | - | 显示数据更新次数 | GET /api/dashboard/summary | - | 动态更新 |
| P02-M01-E04 | 数据卡片 | 系统状态卡片 | el-card | - | 显示系统运行状态 | GET /api/dashboard/summary | - | 动态更新 |

#### M02: 市场热度中心模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P02-M02-E01 | 市场热度中心 | 市场热度Tab | el-tab-pane | name:heat | 市场热度横向柱状图 | Mock数据 | ECharts | 显示8个热门板块 |
| P02-M02-E02 | 市场热度中心 | 领涨板块Tab | el-tab-pane | name:leading | 领涨板块横向柱状图 | Mock数据 | ECharts | 显示8个领涨板块 |
| P02-M02-E03 | 市场热度中心 | 涨跌分布Tab | el-tab-pane | name:distribution | 涨跌分布饼图 | Mock数据 | ECharts | 5种状态分布 |
| P02-M02-E04 | 市场热度中心 | 资金流向Tab | el-tab-pane | name:capital | 资金流向横向柱状图 | Mock数据 | ECharts | 4种资金类型 |

#### M03: 行业资金流向图表模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P02-M03-E01 | 资金流向 | 行业标准选择器 | el-select | size:small | 切换行业分类标准 | 本地状态 | - | 证监会/申万一级/申万二级 |
| P02-M03-E02 | 资金流向 | 资金流向图表 | div+echarts | height:400px | 显示行业资金流向 | GET /api/dashboard/summary | ECharts | 横向柱状图 |

#### M04: 板块表现模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P02-M04-E01 | 板块表现 | 自选股Tab | el-tab-pane | name:favorites | 显示自选股列表 | GET /api/dashboard/summary | el-table | 7列数据 |
| P02-M04-E02 | 板块表现 | 策略选股Tab | el-tab-pane | name:strategy | 显示策略选股列表 | GET /api/dashboard/summary | el-table | 7列数据+信号标签 |
| P02-M04-E03 | 板块表现 | 行业选股Tab | el-tab-pane | name:industry | 显示行业选股列表 | GET /api/dashboard/summary | el-table | 7列数据 |
| P02-M04-E04 | 板块表现 | 概念选股Tab | el-tab-pane | name:concept | 显示概念选股列表 | GET /api/dashboard/summary | el-table | 6列数据+概念标签 |
| P02-M04-E05 | 板块表现 | 刷新按钮 | el-button | type:primary, size:small | 刷新Dashboard数据 | 触发API调用 | - | - |

---

### P03: 市场行情 (Market.vue)

**路由**: `/market`
**文件**: `views/Market.vue`

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P03-M01-E01 | 功能提示 | 开发中提示 | el-empty | - | 显示功能开发中 | 静态 | - | 占位页面 |
| P03-M01-E02 | 功能提示 | 刷新按钮 | el-button | type:primary, size:small | 占位功能 | - | - | - |

---

### P04: 技术分析 (TechnicalAnalysis.vue)

**路由**: `/technical`
**文件**: `views/TechnicalAnalysis.vue`
**重要程度**: ⭐⭐⭐⭐⭐ (核心页面)

#### M01: 工具栏模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P04-M01-E01 | 工具栏 | 股票搜索框 | StockSearchBar | v-model | 输入股票代码搜索 | 自定义组件 | StockSearchBar | 支持搜索 |
| P04-M01-E02 | 工具栏 | 日期范围选择器 | el-date-picker | type:daterange | 选择数据日期范围 | 本地状态 | - | 带快捷选项 |
| P04-M01-E03 | 工具栏 | 刷新数据按钮 | el-button | type:primary, icon:Refresh | 刷新K线数据 | POST /api/indicators/calculate | - | 带loading状态 |
| P04-M01-E04 | 工具栏 | 指标设置按钮 | el-button | icon:Setting | 打开指标面板 | 触发抽屉显示 | - | - |
| P04-M01-E05 | 工具栏 | 配置管理下拉菜单 | el-dropdown | icon:FolderOpened | 保存/加载/管理配置 | API /api/indicators/configs | - | 3个菜单项 |

#### M02: K线图表区域

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P04-M02-E01 | K线图表 | K线图表容器 | KLineChart | ohlcv-data, indicators | 显示K线和指标 | POST /api/indicators/calculate | KLineChart | 基于klinecharts |
| P04-M02-E02 | K线图表 | 空状态提示 | el-empty | image-size:200 | 无数据时显示 | - | - | 提示选择股票 |

#### M03: 指标选择面板 (抽屉)

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P04-M03-E01 | 指标面板 | 指标面板抽屉 | IndicatorPanel | v-model, selected-indicators | 选择技术指标 | GET /api/indicators/registry | IndicatorPanel | 侧边抽屉 |

#### M04: 数据统计信息栏

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P04-M04-E01 | 统计栏 | 股票代码显示 | el-text | tag:b | 显示当前股票代码 | 来自API响应 | - | - |
| P04-M04-E02 | 统计栏 | 数据点数显示 | el-text | tag:b | 显示数据点数量 | 来自API响应 | - | - |
| P04-M04-E03 | 统计栏 | 计算耗时显示 | el-text | tag:b | 显示指标计算耗时 | 来自API响应 | - | 单位:ms |
| P04-M04-E04 | 统计栏 | 已添加指标数 | el-text | tag:b | 显示已选指标数量 | 本地状态 | - | - |

---

### P05: 自选股 (Watchlist.vue)

**路由**: `/watchlist`
**文件**: `views/Watchlist.vue`

#### M01-M02: Tab切换与股票列表 (通过 WatchlistTabs 组件实现)

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P05-M01-E01 | Tab切换 | 用户自选Tab | el-tab-pane | name:user, icon:User | 用户自选股列表 | GET /api/watchlist/category/user | WatchlistTabs | 默认Tab |
| P05-M01-E02 | Tab切换 | 系统自选Tab | el-tab-pane | name:system, icon:MagicStick | 系统推荐股票列表 | GET /api/watchlist/category/system | WatchlistTabs | - |
| P05-M01-E03 | Tab切换 | 策略自选Tab | el-tab-pane | name:strategy, icon:TrendCharts | 策略筛选股票列表 | GET /api/watchlist/category/strategy | WatchlistTabs | - |
| P05-M01-E04 | Tab切换 | 监控列表Tab | el-tab-pane | name:monitor, icon:Warning | 监控关注股票列表 | GET /api/watchlist/category/monitor | WatchlistTabs | - |
| P05-M02-E01 | 股票表格 | 自选股表格 | el-table | height:calc(100vh-400px) | 显示股票列表 | 各自Tab API | WatchlistTable | 带分页 |
| P05-M03-E01 | 操作按钮 | 查看按钮 | el-button | type:primary, size:small | 查看股票详情 | - | - | link样式 |
| P05-M03-E02 | 操作按钮 | 移除按钮 | el-button | type:danger, size:small | 从列表移除股票 | DELETE /api/watchlist/stock/{id} | - | 需确认 |

---

### P06: 指标库 (IndicatorLibrary.vue)

**路由**: `/indicators`
**文件**: `views/IndicatorLibrary.vue`

#### M01: 页面头部模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P06-M01-E01 | 页面头部 | 页面标题 | h1 | - | 显示页面标题 | 静态 | - | "技术指标库" |
| P06-M01-E02 | 页面头部 | 副标题 | p.subtitle | - | 显示指标总数信息 | 静态 | - | 161个TA-Lib指标 |

#### M02: 统计卡片模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P06-M02-E01 | 统计卡片 | 总指标数卡片 | el-card | shadow:hover | 显示总指标数 | GET /api/indicators/registry | - | icon:DataLine |
| P06-M02-E02 | 统计卡片 | 趋势指标卡片 | el-card | shadow:hover | 显示趋势指标数量 | GET /api/indicators/registry | - | icon:TrendCharts |
| P06-M02-E03 | 统计卡片 | 动量指标卡片 | el-card | shadow:hover | 显示动量指标数量 | GET /api/indicators/registry | - | icon:Connection |
| P06-M02-E04 | 统计卡片 | 波动率指标卡片 | el-card | shadow:hover | 显示波动率指标数量 | GET /api/indicators/registry | - | icon:Histogram |
| P06-M02-E05 | 统计卡片 | 成交量指标卡片 | el-card | shadow:hover | 显示成交量指标数量 | GET /api/indicators/registry | - | icon:PieChart |
| P06-M02-E06 | 统计卡片 | K线形态卡片 | el-card | shadow:hover | 显示K线形态数量 | GET /api/indicators/registry | - | icon:Timer |

#### M03: 搜索筛选模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P06-M03-E01 | 搜索筛选 | 搜索输入框 | el-input | size:large, prefix-icon:Search | 搜索指标 | 本地过滤 | - | 支持名称/缩写/描述 |
| P06-M03-E02 | 搜索筛选 | 分类选择器 | el-select | size:large | 按分类筛选 | 本地过滤 | - | 6个选项 |

#### M04: 指标详情卡片列表

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P06-M04-E01 | 指标卡片 | 指标详情卡片 | el-card | shadow:hover | 显示单个指标完整信息 | GET /api/indicators/registry | - | 包含参数/输出/参考线 |
| P06-M04-E02 | 指标卡片 | 参数配置表格 | el-table | size:small, border | 显示指标参数列表 | - | - | 5列 |
| P06-M04-E03 | 指标卡片 | 输出字段描述 | el-descriptions | column:2, size:small | 显示输出字段说明 | - | - | - |

---

### P07: 资金流向 (FundFlowPanel.vue)

**路由**: `/market-data/fund-flow`
**文件**: `components/market/FundFlowPanel.vue`

#### M01: 查询表单模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P07-M01-E01 | 查询表单 | 行业分类选择器 | el-select | - | 选择行业分类标准 | 本地状态 | - | 证监会/申万一级/申万二级 |
| P07-M01-E02 | 查询表单 | 日期范围选择器 | el-date-picker | type:daterange | 选择查询日期范围 | 本地状态 | - | - |
| P07-M01-E03 | 查询表单 | 查询按钮 | el-button | type:primary, icon:Search | 查询资金流向数据 | GET /api/market/v3/fund-flow | - | - |
| P07-M01-E04 | 查询表单 | 刷新按钮 | el-button | icon:Refresh | 刷新最新数据 | GET /api/market/v3/fund-flow | - | - |

#### M02: 资金流向数据表格模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P07-M02-E01 | 数据表格 | 资金流向表格 | el-table | stripe, border, height | 显示资金流向数据 | GET /api/market/v3/fund-flow | - | 11列数据 |
| P07-M02-E02 | 数据表格 | 行业名称列 | el-table-column | fixed | 显示行业名称(可点击) | - | - | 可点击查看趋势 |
| P07-M02-E03 | 数据表格 | 主力净流入列 | el-table-column | sortable, align:right | 显示主力净流入金额 | - | - | 红绿配色 |
| P07-M02-E04 | 数据表格 | 超大单列 | el-table-column | sortable, align:right | 显示超大单净流入 | - | - | 红绿配色 |
| P07-M02-E05 | 数据表格 | 大单列 | el-table-column | sortable, align:right | 显示大单净流入 | - | - | 红绿配色 |
| P07-M02-E06 | 数据表格 | 中单列 | el-table-column | sortable, align:right | 显示中单净流入 | - | - | 红绿配色 |
| P07-M02-E07 | 数据表格 | 小单列 | el-table-column | sortable, align:right | 显示小单净流入 | - | - | 红绿配色 |
| P07-M02-E08 | 数据表格 | 分页控件 | el-pagination | layout:完整 | 分页显示数据 | 本地分页 | - | 支持pageSize选择 |

#### M03: 资金流向趋势图模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P07-M03-E01 | 趋势图 | 趋势图卡片 | el-card | shadow:never | 显示选中行业趋势 | - | FundFlowTrendChart | 点击行业后显示 |
| P07-M03-E02 | 趋势图 | 当前选中标签 | el-tag | type:success, size:small | 显示当前选中行业 | 本地状态 | - | - |

---

### P08: ETF行情 (ETFDataTable.vue)

**路由**: `/market-data/etf`
**文件**: `components/market/ETFDataTable.vue`

#### M01: 查询工具栏模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P08-M01-E01 | 查询工具栏 | ETF代码输入框 | el-input | clearable | 输入ETF代码筛选 | 本地状态 | - | - |
| P08-M01-E02 | 查询工具栏 | 关键词输入框 | el-input | clearable | 输入名称/代码搜索 | 本地状态 | - | - |
| P08-M01-E03 | 查询工具栏 | 显示数量选择器 | el-input-number | min:10, max:500 | 设置显示数量 | 本地状态 | - | 步长10 |
| P08-M01-E04 | 查询工具栏 | 查询按钮 | el-button | type:primary, icon:Search | 查询ETF数据 | GET /api/market/etf/list | - | - |
| P08-M01-E05 | 查询工具栏 | 刷新按钮 | el-button | icon:Refresh | 刷新全市场ETF数据 | POST /api/market/etf/refresh | - | - |

#### M02: ETF数据表格模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P08-M02-E01 | 数据表格 | ETF表格 | el-table | stripe, border | 显示ETF行情数据 | GET /api/market/etf/list | - | 12列数据 |
| P08-M02-E02 | 数据表格 | 代码列 | el-table-column | width:100, fixed | 显示ETF代码 | - | - | - |
| P08-M02-E03 | 数据表格 | 名称列 | el-table-column | width:180, fixed | 显示ETF名称 | - | - | - |
| P08-M02-E04 | 数据表格 | 最新价列 | el-table-column | sortable, align:right | 显示最新价格 | - | - | 3位小数 |
| P08-M02-E05 | 数据表格 | 涨跌幅列 | el-table-column | sortable, align:right | 显示涨跌幅 | - | - | 红绿配色 |
| P08-M02-E06 | 数据表格 | 成交量列 | el-table-column | sortable, align:right | 显示成交量 | - | - | 格式化显示 |
| P08-M02-E07 | 数据表格 | 换手率列 | el-table-column | align:right | 显示换手率 | - | - | 百分比 |
| P08-M02-E08 | 数据表格 | 流通市值列 | el-table-column | sortable, align:right | 显示流通市值 | - | - | 格式化显示 |

#### M03: ETF详情抽屉模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P08-M03-E01 | 详情抽屉 | ETF详情抽屉 | el-drawer | size:50% | 显示ETF详细信息 | 点击行触发 | - | - |
| P08-M03-E02 | 详情抽屉 | 详情描述列表 | el-descriptions | column:2, border | 显示ETF详细数据 | - | - | 8个字段 |

---

### P09: 竞价抢筹 (ChipRaceTable.vue)

**路由**: `/market-data/chip-race`
**文件**: `components/market/ChipRaceTable.vue`

#### M01: 查询工具栏模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P09-M01-E01 | 查询工具栏 | 抢筹类型选择 | el-radio-group | - | 选择早盘/尾盘抢筹 | 本地状态 | - | 2个选项 |
| P09-M01-E02 | 查询工具栏 | 交易日期选择器 | el-date-picker | type:date | 选择交易日期 | 本地状态 | - | - |
| P09-M01-E03 | 查询工具栏 | 最小抢筹金额 | el-input-number | min:0, step:10000000 | 设置最小金额过滤 | 本地状态 | - | 单位:元 |
| P09-M01-E04 | 查询工具栏 | 显示数量选择器 | el-input-number | min:10, max:500 | 设置显示数量 | 本地状态 | - | 步长10 |
| P09-M01-E05 | 查询工具栏 | 查询按钮 | el-button | type:primary, icon:Search | 查询抢筹数据 | GET /api/market/v3/chip-race | - | - |
| P09-M01-E06 | 查询工具栏 | 刷新按钮 | el-button | icon:Refresh | 刷新最新数据 | GET /api/market/v3/chip-race | - | - |

#### M02: 抢筹数据表格模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P09-M02-E01 | 数据表格 | 抢筹表格 | el-table | stripe, border | 显示抢筹数据 | GET /api/market/v3/chip-race | - | 9列数据 |
| P09-M02-E02 | 数据表格 | 排名列 | el-table-column | type:index, align:center | 显示排名序号 | - | - | 自动编号 |
| P09-M02-E03 | 数据表格 | 代码列 | el-table-column | width:100, fixed | 显示股票代码 | - | - | - |
| P09-M02-E04 | 数据表格 | 名称列 | el-table-column | width:120, fixed | 显示股票名称 | - | - | - |
| P09-M02-E05 | 数据表格 | 收盘价列 | el-table-column | sortable, align:right | 显示收盘价 | - | - | - |
| P09-M02-E06 | 数据表格 | 涨跌幅列 | el-table-column | sortable, align:right | 显示涨跌幅 | - | - | 红绿配色 |
| P09-M02-E07 | 数据表格 | 抢筹强度列 | el-table-column | sortable, align:right | 显示抢筹强度 | - | - | 进度条显示 |
| P09-M02-E08 | 数据表格 | 净量列 | el-table-column | sortable, align:right | 显示净量 | - | - | 格式化显示 |
| P09-M02-E09 | 数据表格 | 买盘量列 | el-table-column | sortable, align:right | 显示买盘量 | - | - | 红色 |
| P09-M02-E10 | 数据表格 | 卖盘量列 | el-table-column | sortable, align:right | 显示卖盘量 | - | - | 绿色 |

#### M03: 统计信息卡片模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P09-M03-E01 | 统计卡片 | 个股数量统计 | el-statistic | suffix:只 | 显示个股数量 | 计算属性 | - | - |
| P09-M03-E02 | 统计卡片 | 总净量统计 | el-statistic | suffix:亿元 | 显示总净量 | 计算属性 | - | - |
| P09-M03-E03 | 统计卡片 | 平均净量统计 | el-statistic | suffix:亿元 | 显示平均净量 | 计算属性 | - | - |
| P09-M03-E04 | 统计卡片 | 上涨占比统计 | el-statistic | suffix:% | 显示上涨个股占比 | 计算属性 | - | - |

---

### P10: 龙虎榜 (LongHuBangTable.vue)

**路由**: `/market-data/lhb`
**文件**: `components/market/LongHuBangTable.vue`
**重要程度**: ⭐⭐⭐⭐⭐ (重点页面)

#### M01: 查询工具栏模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P10-M01-E01 | 查询工具栏 | 股票代码输入框 | el-input | clearable | 输入股票代码筛选 | 本地状态 | - | 如: 600519 |
| P10-M01-E02 | 查询工具栏 | 日期范围选择器 | el-date-picker | type:daterange | 选择查询日期范围 | 本地状态 | - | - |
| P10-M01-E03 | 查询工具栏 | 最小净买入额 | el-input-number | min:0, step:10000000 | 设置最小净买入额过滤 | 本地状态 | - | 单位:元 |
| P10-M01-E04 | 查询工具栏 | 显示数量选择器 | el-input-number | min:10, max:500 | 设置显示数量 | 本地状态 | - | 步长10 |
| P10-M01-E05 | 查询工具栏 | 查询按钮 | el-button | type:primary, icon:Search | 查询龙虎榜数据 | GET /api/market/v3/dragon-tiger | - | - |
| P10-M01-E06 | 查询工具栏 | 刷新按钮 | el-button | icon:Refresh | 刷新最新数据 | GET /api/market/v3/dragon-tiger | - | - |

#### M02: 龙虎榜数据表格模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P10-M02-E01 | 数据表格 | 龙虎榜表格 | el-table | stripe, border, @row-click | 显示龙虎榜数据 | GET /api/market/v3/dragon-tiger | - | 11列数据,可点击行 |
| P10-M02-E02 | 数据表格 | 交易日期列 | el-table-column | sortable, fixed | 显示交易日期 | - | - | - |
| P10-M02-E03 | 数据表格 | 代码列 | el-table-column | width:100, fixed | 显示股票代码 | - | - | - |
| P10-M02-E04 | 数据表格 | 名称列 | el-table-column | width:120, fixed | 显示股票名称 | - | - | - |
| P10-M02-E05 | 数据表格 | 上榜原因列 | el-table-column | min-width:200 | 显示上榜原因 | - | - | 带Tag标签 |
| P10-M02-E06 | 数据表格 | 净买入额列 | el-table-column | sortable, align:right | 显示净买入额 | - | - | 红绿配色 |
| P10-M02-E07 | 数据表格 | 买入总额列 | el-table-column | sortable, align:right | 显示买入总额 | - | - | 红色 |
| P10-M02-E08 | 数据表格 | 卖出总额列 | el-table-column | sortable, align:right | 显示卖出总额 | - | - | 绿色 |
| P10-M02-E09 | 数据表格 | 换手率列 | el-table-column | sortable, align:right | 显示换手率 | - | - | 百分比 |
| P10-M02-E10 | 数据表格 | 机构买入列 | el-table-column | sortable, align:right | 显示机构买入金额 | - | - | - |
| P10-M02-E11 | 数据表格 | 机构卖出列 | el-table-column | sortable, align:right | 显示机构卖出金额 | - | - | - |
| P10-M02-E12 | 数据表格 | 机构净买入列 | el-table-column | align:right | 显示机构净买入金额 | - | - | 计算列 |

#### M03: 统计信息卡片模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P10-M03-E01 | 统计卡片 | 上榜次数统计 | el-statistic | suffix:次 | 显示上榜次数 | 计算属性 | - | - |
| P10-M03-E02 | 统计卡片 | 总净买入额统计 | el-statistic | suffix:亿元 | 显示总净买入额 | 计算属性 | - | 带图标 |
| P10-M03-E03 | 统计卡片 | 总买入额统计 | el-statistic | suffix:亿元 | 显示总买入额 | 计算属性 | - | - |
| P10-M03-E04 | 统计卡片 | 总卖出额统计 | el-statistic | suffix:亿元 | 显示总卖出额 | 计算属性 | - | - |

#### M04: 详情对话框模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P10-M04-E01 | 详情对话框 | 龙虎榜详情对话框 | el-dialog | width:60% | 显示龙虎榜详细信息 | 点击行触发 | - | - |
| P10-M04-E02 | 详情对话框 | 详情描述列表 | el-descriptions | column:2, border | 显示龙虎榜详细数据 | - | - | 10个字段 |

---

### P11: 系统设置 (Settings.vue)

**路由**: `/settings`
**文件**: `views/Settings.vue`

#### M01: 基本设置Tab

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P11-M01-E01 | 基本设置 | 系统名称显示 | el-input | disabled | 显示系统名称 | 静态 | - | MyStocks |
| P11-M01-E02 | 基本设置 | 系统版本显示 | el-input | disabled | 显示系统版本 | 静态 | - | 1.0.0 |
| P11-M01-E03 | 基本设置 | API地址显示 | el-input | disabled | 显示API地址 | 静态 | - | http://localhost:8000 |

#### M02: 显示设置Tab

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P11-M02-E01 | 显示设置 | 字体大小设置 | FontSizeSetting | - | 设置全局字体大小 | LocalStorage | FontSizeSetting | 4档可选 |
| P11-M02-E02 | 显示设置 | 字体家族选择器 | el-select | - | 选择全局字体家族 | LocalStorage | - | 8种字体 |
| P11-M02-E03 | 显示设置 | 字体预览区域 | div | - | 预览字体效果 | - | - | 3行示例文本 |
| P11-M02-E04 | 显示设置 | 保存按钮 | el-button | type:primary | 保存字体设置 | LocalStorage | - | - |
| P11-M02-E05 | 显示设置 | 恢复默认按钮 | el-button | - | 恢复默认字体设置 | - | - | - |

#### M03: 数据库配置Tab

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P11-M03-E01 | 数据库配置 | 数据库列表表格 | el-table | stripe, border | 显示数据库配置列表 | 本地配置 | - | 4个数据库 |
| P11-M03-E02 | 数据库配置 | 测试连接按钮 | el-button | type:primary, size:small | 测试单个数据库连接 | POST /api/system/test-connection | - | 带loading |
| P11-M03-E03 | 数据库配置 | 测试所有连接按钮 | el-button | type:primary | 测试所有数据库连接 | 批量调用API | - | - |
| P11-M03-E04 | 数据库配置 | 连接状态标签 | el-tag | type:动态 | 显示连接状态 | API响应 | - | 4种状态 |

#### M04: 用户管理Tab

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P11-M04-E01 | 用户管理 | 添加用户按钮 | el-button | type:primary, size:small | 添加新用户 | - | - | 占位功能 |
| P11-M04-E02 | 用户管理 | 用户列表表格 | el-table | stripe | 显示用户列表 | - | - | 空数据 |

#### M05: 运行日志Tab

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P11-M05-E01 | 运行日志 | 筛选按钮 | el-button | type:动态 | 切换显示全部/问题日志 | 本地状态 | - | - |
| P11-M05-E02 | 运行日志 | 日志级别选择器 | el-select | clearable | 按级别筛选日志 | 本地状态 | - | 4个选项 |
| P11-M05-E03 | 运行日志 | 日志分类选择器 | el-select | clearable | 按分类筛选日志 | 本地状态 | - | 4个选项 |
| P11-M05-E04 | 运行日志 | 刷新按钮 | el-button | icon:Refresh | 刷新日志列表 | GET /api/system/logs | - | - |
| P11-M05-E05 | 运行日志 | 日志统计卡片 | el-card | shadow:never | 显示日志统计信息 | GET /api/system/logs/summary | - | 4个统计项 |
| P11-M05-E06 | 运行日志 | 日志列表表格 | el-table | stripe, border, v-loading | 显示日志记录 | GET /api/system/logs | - | 8列数据 |
| P11-M05-E07 | 运行日志 | 详情按钮 | el-button | type:text, size:small | 查看日志详情 | - | - | 弹出对话框 |
| P11-M05-E08 | 运行日志 | 分页控件 | el-pagination | layout:完整 | 分页显示日志 | API分页 | - | 支持pageSize选择 |

#### M06: 关于Tab

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| P11-M06-E01 | 关于 | 项目信息描述列表 | el-descriptions | column:1, border | 显示项目基本信息 | 静态 | - | 5项信息 |

---

### L01: 主布局 (layout/index.vue)

**文件**: `layout/index.vue`
**作用**: 全局布局容器

#### M01: 侧边栏导航模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| L01-M01-E01 | 侧边栏 | Logo区域 | div.logo | - | 显示系统Logo | 静态 | - | 可折叠 |
| L01-M01-E02 | 侧边栏 | 仪表盘菜单项 | el-menu-item | index:/dashboard, icon:Odometer | 跳转仪表盘 | router | - | - |
| L01-M01-E03 | 侧边栏 | 市场行情子菜单 | el-sub-menu | index:/market | 市场行情导航 | router | - | 2个子项 |
| L01-M01-E04 | 侧边栏 | 市场数据子菜单 | el-sub-menu | index:/market-data | 市场数据导航 | router | - | 5个子项 |
| L01-M01-E05 | 侧边栏 | 股票管理菜单项 | el-menu-item | index:/stocks | 跳转股票管理 | router | - | - |
| L01-M01-E06 | 侧边栏 | 数据分析菜单项 | el-menu-item | index:/analysis | 跳转数据分析 | router | - | - |
| L01-M01-E07 | 侧边栏 | 技术分析菜单项 | el-menu-item | index:/technical | 跳转技术分析 | router | - | - |
| L01-M01-E08 | 侧边栏 | 指标库菜单项 | el-menu-item | index:/indicators | 跳转指标库 | router | - | - |
| L01-M01-E09 | 侧边栏 | 风险监控菜单项 | el-menu-item | index:/risk | 跳转风险监控 | router | - | - |
| L01-M01-E10 | 侧边栏 | 交易管理菜单项 | el-menu-item | index:/trade | 跳转交易管理 | router | - | - |
| L01-M01-E11 | 侧边栏 | 策略管理菜单项 | el-menu-item | index:/strategy | 跳转策略管理 | router | - | - |
| L01-M01-E12 | 侧边栏 | 回测分析菜单项 | el-menu-item | index:/backtest | 跳转回测分析 | router | - | - |
| L01-M01-E13 | 侧边栏 | 迁移项目子菜单 | el-sub-menu | index:/migration | 迁移项目导航 | router | - | 5个子项 |
| L01-M01-E14 | 侧边栏 | 系统设置菜单项 | el-menu-item | index:/settings | 跳转系统设置 | router | - | - |

#### M02: 顶部导航栏模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| L01-M02-E01 | 顶部导航 | 折叠按钮 | el-icon | @click | 折叠/展开侧边栏 | 本地状态 | - | - |
| L01-M02-E02 | 顶部导航 | 用户信息下拉菜单 | el-dropdown | - | 显示用户信息和操作 | authStore | - | 2个菜单项 |
| L01-M02-E03 | 顶部导航 | 个人信息菜单项 | el-dropdown-item | command:profile | 查看个人信息 | - | - | 占位功能 |
| L01-M02-E04 | 顶部导航 | 退出登录菜单项 | el-dropdown-item | command:logout | 退出登录 | authStore.logout() | - | 需确认 |

#### M03: 内容区域模块

| 元素编号 | 所属模块 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 依赖组件 | 备注 |
|---------|---------|---------|---------|---------|---------|------------|---------|------|
| L01-M03-E01 | 内容区域 | 路由视图容器 | router-view | - | 渲染当前路由组件 | router | - | - |

---

## 共享组件清单

### C01: K线图表组件 (KLineChart.vue)

**文件**: `components/technical/KLineChart.vue`
**用途**: 技术分析K线图表

| 元素编号 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 依赖库 | 备注 |
|---------|---------|---------|---------|---------|--------|------|
| C01-E01 | 图表加载状态 | div+el-icon | - | 显示加载状态 | - | Loading图标 |
| C01-E02 | 图表容器 | div | ref:chartContainer | K线图表渲染容器 | klinecharts | - |
| C01-E03 | 周期切换器 | el-radio-group | - | 切换K线周期 | - | 6个周期 |
| C01-E04 | 图表类型下拉菜单 | el-dropdown | - | 切换图表类型 | - | 5种类型 |
| C01-E05 | 指标标签 | el-tag | closable | 显示已添加指标 | - | 可移除 |
| C01-E06 | 重置按钮 | el-button | icon:Refresh | 重置图表缩放 | - | - |

### C02: 指标选择面板 (IndicatorPanel.vue)

**文件**: `components/technical/IndicatorPanel.vue`
**用途**: 技术指标选择抽屉

| 元素编号 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 备注 |
|---------|---------|---------|---------|---------|------------|------|
| C02-E01 | 指标搜索框 | el-input | prefix-icon:Search | 搜索指标 | 本地过滤 | - |
| C02-E02 | 分类标签组 | el-radio-group | - | 按分类筛选 | 本地状态 | 6个分类 |
| C02-E03 | 已选指标列表 | div | - | 显示已选指标 | props | 可移除 |
| C02-E04 | 清空全部按钮 | el-button | type:danger, text | 清空所有指标 | - | - |
| C02-E05 | 指标卡片 | el-card | shadow:hover, @click | 显示指标详情 | GET /api/indicators/registry | 可点击 |
| C02-E06 | 添加按钮 | el-button | type:primary, size:small | 添加指标到图表 | emit事件 | - |
| C02-E07 | 参数配置对话框 | el-dialog | append-to-body | 配置指标参数 | - | 动态生成表单 |

### C03: 股票搜索栏 (StockSearchBar.vue)

**文件**: `components/technical/StockSearchBar.vue`
**用途**: 股票代码搜索输入框

| 元素编号 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 备注 |
|---------|---------|---------|---------|---------|------------|------|
| C03-E01 | 搜索输入框 | el-input | v-model, clearable | 输入股票代码 | 本地状态 | 支持autocomplete |
| C03-E02 | 搜索建议列表 | el-autocomplete | fetch-suggestions | 显示搜索建议 | - | 动态加载 |

### C04: 自选股Tabs (WatchlistTabs.vue)

**文件**: `components/stock/WatchlistTabs.vue`
**用途**: 自选股分类Tab切换

| 元素编号 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 备注 |
|---------|---------|---------|---------|---------|------------|------|
| C04-E01 | Tab容器 | el-tabs | type:card, v-model | Tab切换容器 | 本地状态 | 4个Tab |
| C04-E02 | Tab内容 | WatchlistTable | :group | 显示股票列表 | - | 动态加载 |

### C05: 自选股表格 (WatchlistTable.vue)

**文件**: `components/stock/WatchlistTable.vue`
**用途**: 自选股票列表表格

| 元素编号 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源/API | 备注 |
|---------|---------|---------|---------|---------|------------|------|
| C05-E01 | 股票表格 | el-table | stripe, border, height | 显示股票列表 | GET /api/watchlist/category/{category} | 10列数据 |
| C05-E02 | 分页控件 | el-pagination | layout:完整 | 分页显示 | usePagination | - |
| C05-E03 | 查看按钮 | el-button | type:primary, size:small, link | 查看股票详情 | emit事件 | - |
| C05-E04 | 移除按钮 | el-button | type:danger, size:small, link | 移除股票 | DELETE API | 需确认 |

### C06: 资金流向趋势图 (FundFlowTrendChart.vue)

**文件**: `components/market/FundFlowTrendChart.vue`
**用途**: 行业资金流向趋势折线图

| 元素编号 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 依赖库 | 备注 |
|---------|---------|---------|---------|---------|--------|------|
| C06-E01 | 趋势图容器 | div+echarts | height:300px | 显示资金流向趋势 | ECharts | 折线图 |

### C07: 字体大小设置 (FontSizeSetting.vue)

**文件**: `components/settings/FontSizeSetting.vue`
**用途**: 全局字体大小设置

| 元素编号 | 元素名称 | 元素类型 | 参数详情 | 用途描述 | 数据来源 | 备注 |
|---------|---------|---------|---------|---------|---------|------|
| C07-E01 | 字体大小选择器 | el-radio-group | - | 选择字体大小 | LocalStorage | 4档可选 |
| C07-E02 | 预览区域 | div | - | 预览字体效果 | - | 示例文本 |
| C07-E03 | 保存按钮 | el-button | type:primary | 保存设置 | LocalStorage | - |

---

## API端点汇总

### 认证相关
- `POST /api/auth/login` - 用户登录

### Dashboard相关
- `GET /api/dashboard/summary` - 获取Dashboard汇总数据

### 市场数据相关
- `GET /api/market/v3/dragon-tiger` - 获取龙虎榜数据
- `GET /api/market/v3/fund-flow` - 获取资金流向数据
- `GET /api/market/v3/chip-race` - 获取竞价抢筹数据
- `GET /api/market/etf/list` - 获取ETF行情列表
- `POST /api/market/etf/refresh` - 刷新ETF数据

### 技术指标相关
- `GET /api/indicators/registry` - 获取指标注册表
- `POST /api/indicators/calculate` - 计算技术指标
- `GET /api/indicators/configs` - 获取指标配置列表
- `POST /api/indicators/configs` - 创建指标配置
- `GET /api/indicators/configs/{id}` - 获取指标配置详情
- `DELETE /api/indicators/configs/{id}` - 删除指标配置

### 自选股相关
- `GET /api/watchlist/category/{category}` - 获取分类自选股
- `DELETE /api/watchlist/stock/{id}` - 移除自选股

### 系统相关
- `POST /api/system/test-connection` - 测试数据库连接
- `GET /api/system/logs` - 获取系统日志
- `GET /api/system/logs/summary` - 获取日志统计

---

## Element Plus 组件使用统计

### 布局组件
- `el-container` - 布局容器 (L01)
- `el-aside` - 侧边栏 (L01)
- `el-header` - 头部 (L01)
- `el-main` - 主内容区 (L01)
- `el-row` / `el-col` - 栅格布局 (多处)

### 导航组件
- `el-menu` - 导航菜单 (L01)
- `el-menu-item` - 菜单项 (L01)
- `el-sub-menu` - 子菜单 (L01)
- `el-tabs` / `el-tab-pane` - 标签页 (P02, P04, P05, P11)
- `el-dropdown` - 下拉菜单 (L01, P04)

### 数据展示
- `el-table` - 表格 (P02, P05, P07-P11) ⭐高频使用
- `el-table-column` - 表格列 (多处)
- `el-card` - 卡片 (多处) ⭐高频使用
- `el-tag` - 标签 (多处) ⭐高频使用
- `el-descriptions` - 描述列表 (P06, P08, P10, P11)
- `el-statistic` - 统计数值 (P09, P10, P11)
- `el-empty` - 空状态 (多处)
- `el-progress` - 进度条 (P09)

### 表单组件
- `el-form` / `el-form-item` - 表单 (多处)
- `el-input` - 输入框 (P01, P07-P11) ⭐高频使用
- `el-input-number` - 数字输入框 (P07-P10)
- `el-select` / `el-option` - 选择器 (P02, P06, P07-P11) ⭐高频使用
- `el-date-picker` - 日期选择器 (P04, P07-P10) ⭐高频使用
- `el-radio-group` / `el-radio-button` - 单选按钮组 (P06, P09, C01)

### 反馈组件
- `el-button` - 按钮 (多处) ⭐高频使用
- `el-pagination` - 分页 (P05, P07-P11) ⭐高频使用
- `el-loading` - 加载指令 (多处)
- `el-message` - 消息提示 (JS调用)
- `el-dialog` - 对话框 (P04, P10)
- `el-drawer` - 抽屉 (P04, P08)

### 其他组件
- `el-icon` - 图标 (多处) ⭐高频使用
- `el-divider` - 分割线 (P01)
- `el-space` - 间距 (P04, P06)
- `el-scrollbar` - 滚动条 (C02)

---

## 技术栈总结

### 前端框架
- **Vue 3** - Composition API
- **Vue Router 4** - 路由管理
- **Pinia** - 状态管理 (authStore)

### UI组件库
- **Element Plus** - 主UI库
- **@element-plus/icons-vue** - 图标库

### 图表库
- **ECharts** - 数据可视化 (P02仪表盘)
- **klinecharts** - K线图表库 (P04技术分析)

### 其他依赖
- **axios** - HTTP客户端
- **dayjs** - 日期处理

### 自定义工具
- **usePagination** - 分页Composable
- **useUserPreferences** - 用户偏好Composable
- **indicatorService** - 指标服务封装
- **dataApi** - 数据API封装
- **watchlistApi** - 自选股API封装

---

## 统计数据

### 页面统计
- **总页面数**: 11个主要页面
- **核心页面**: 5个 (登录、仪表盘、技术分析、自选股、龙虎榜)
- **市场数据页面**: 5个
- **设置管理页面**: 1个

### 组件统计
- **共享组件**: 7个
- **自定义组件**: 多个业务组件

### Element Plus组件使用
- **高频组件**: el-table, el-card, el-tag, el-button, el-input, el-select, el-date-picker, el-pagination, el-icon
- **布局组件**: 完整的el-container布局体系
- **表单组件**: 覆盖所有常用表单控件

### API端点
- **总API数**: 约20个
- **分类**: 认证(1) + Dashboard(1) + 市场数据(5) + 技术指标(6) + 自选股(2) + 系统(3)

---

## 更新日志

| 版本 | 日期 | 说明 | 作者 |
|-----|------|------|------|
| v1.0 | 2025-10-29 | 初始版本,完整清单 | Claude |

---

**文档结束**
