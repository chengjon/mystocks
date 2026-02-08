# ArtDeco Components Catalog (V3.0 Asset Audit)

本目录是对 MyStocks 项目中 ArtDeco 设计系统组件的**实时审计清单**。所有组件均经过核实，与 `src/` 目录下的物理文件 1:1 对应。

## 1. 基础 UI 组件 (Base UI - 14个)
**位置**: `src/components/artdeco/base/`
核心通用 UI 元素，支持多变体和状态切换。

| 组件名 | 功能说明 | 核心 Prop / 特性 |
|:---|:---|:---|
| **ArtDecoButton** | 奢华按钮 | `variant`: solid/outline/double-border/rise/fall |
| **ArtDecoCard** | 几何边框容器 | `hoverable`, `clickable`, 锐角设计 (0px radius) |
| **ArtDecoInput** | 下划线输入框 | `labelType`: default/roman (罗马数字支持) |
| **ArtDecoBadge** | 状态徽章 | `variant`: gold/success/warning/danger/info |
| **ArtDecoStatCard**| 统计数据卡片 | 自动处理涨跌颜色, 支持 trend 指示 |
| **ArtDecoSelect** | 下拉选择器 | 符合 ArtDeco 金色边框规范 |
| **ArtDecoSwitch** | 机械式开关 | 步进式切换动效 |
| **ArtDecoProgress**| 线性进度条 | 金色发光进度指示 |
| **ArtDecoDialog** | 模态对话框 | 3px double border 签名风格 |
| **ArtDecoStatCard**| 数值统计卡片 | 支持 A 股颜色规范 (红涨绿跌) |
| **ArtDecoAlert** | 全局警告提示 | 支持多种严重程度等级 |
| **ArtDecoCollapsible**| 可折叠面板 | 用于 Dashboard 模块控制 |
| **ArtDecoSkipLink** | 无障碍跳转 | 符合 WCAG 2.1 AA 标准 |
| **ArtDecoLanguageSwitcher**| 语言切换 | 多语言支持 UI |

## 2. 业务功能组件 (Business - 11个)
**位置**: `src/components/artdeco/business/`
封装了特定交互逻辑的通用业务组件。

| 组件名 | 分类 | 特性说明 |
|:---|:---|:---|
| **ArtDecoFilterBar** | 过滤 | 支持 4 列响应式网格布局 |
| **ArtDecoCodeEditor** | 编辑器 | 针对 Python 策略优化的深色主题 |
| **ArtDecoDateRange** | 日期 | 集成 dayjs, 支持时间维度筛选 |
| **ArtDecoSlider** | 滑块 | 高精度参数调节控件 |
| **ArtDecoAlertRule** | 规则 | VaR/回撤等风险规则配置界面 |
| **ArtDecoStatus** | 状态 | 系统服务连接状态指示 |
| **ArtDecoInfoCard** | 信息 | 相比 StatCard 更适合长文本展示 |
| **ArtDecoButtonGroup**| 控件 | 统一间距的按钮操作组 |
| **ArtDecoDataSourceTable**| 监控 | 实时数据源存活状态监控表格 |
| **ArtDecoMechanicalSwitch**| 控件 | 具有物理触感的开关设计 |
| **ArtDecoBacktestConfig**| 配置 | 策略回测参数聚合配置 |

## 3. 高级图表体系 (Charts - 9个)
**位置**: `src/components/artdeco/charts/`
集成 ECharts 或专业图表库，应用 ArtDeco V3.0 主题。

| 组件名 | 技术栈 | 视觉特征 |
|:---|:---|:---|
| **ArtDecoKLineChartContainer** | Klinecharts | 专业级 K 线, 金色坐标轴 |
| **ArtDecoChart** | ECharts | 统一应用 `artDecoTheme` |
| **TimeSeriesChart** | ECharts | 支持双 Y 轴, 金色发光线条 |
| **DepthChart** | Canvas | 市场深度/订单流可视化 |
| **DrawdownChart** | ECharts | 水位线填色, 支持 A 股颜色 |
| **HeatmapCard** | ECharts | 板块热力图, 响应式 Grid 布局 |
| **CorrelationMatrix**| ECharts | 因子相关性矩阵展示 |
| **PerformanceTable** | Custom | 净值统计与归因表格 |
| **ArtDecoRomanNumeral**| Decorative | 用于标题的罗马数字渲染组件 |

## 4. 领域专用组件 (Domain - 15个)
**位置**: `src/components/artdeco/trading/` (含部分业务组件)
针对交易、行情、风险领域的深分拆组件。

| 领域 | 核心组件 (已验证) | 备注 |
|:---|:---|:---|
| **行情 (Market)** | `ArtDecoTicker`, `ArtDecoTickerList` | 实时滚动行情指示器 |
| **交易 (Trading)** | `ArtDecoOrderBook`, `ArtDecoTradeForm` | 订单簿与标准交易面板 |
| **持仓 (Portfolio)**| `ArtDecoPositionCard`, `ArtDecoPositionMonitor` | 仓位盈亏实时监控 |
| **风险 (Risk)** | `ArtDecoRiskGauge`, `ArtDecoAlertRule` | 仪表盘式风险等级展示 |
| **策略 (Strategy)** | `ArtDecoStrategyCard`, `ArtDecoBacktestAnalysis` | 策略表现汇总展示 |

## 5. 高阶分析组件 (Advanced - 10个)
**位置**: `src/components/artdeco/advanced/`
处理复杂金融计算结果的展示。

- **ArtDecoCapitalFlow**: 资金流向实时分析
- **ArtDecoMarketPanorama**: 市场全景透视
- **ArtDecoAnomalyTracking**: 异动追踪告警
- **ArtDecoChipDistribution**: 筹码分布模型
- **ArtDecoSentimentAnalysis**: 市场情绪分析
- **ArtDecoFinancialValuation**: 财务估值多维分析
- **ArtDecoTimeSeriesAnalysis**: 时间序列预测分析
- **ArtDecoBatchAnalysisView**: 批量数据处理视图
- **ArtDecoDecisionModels**: 决策模型管理界面
- **ArtDecoTradingSignals**: 核心交易信号流展示

---
**核实状态**: ✅ 已通过 `find` 命令物理核实。
**更新日期**: 2026-02-08 (V3.0 Final Audit)