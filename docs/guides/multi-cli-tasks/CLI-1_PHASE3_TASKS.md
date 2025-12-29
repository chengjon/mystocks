# CLI-1: Phase 3 前端K线图可视化与UI优化

**CLI编号**: CLI-1
**阶段**: Phase 3 - Enhanced K-line Charts + UI Style
**执行轮次**: 第一轮 (Day 1-15)
**状态**: ⏳ 待审批

---

## 基本信息

| 项目 | 内容 |
|------|------|
| **工作目录** | `/opt/claude/mystocks_frontend_phase3` |
| **Git分支** | `feature/phase3-kline-ui` |
| **基于分支** | `main` |
| **合并目标** | `main` |
| **技术栈** | Vue 3.4+, TypeScript 5.3+, klinecharts 9.6.0 |
| **任务数量** | 12个 (10个K线 + 2个UI Style) |
| **预计工作量** | 15天 |
| **优先级** | 🔴 高（Phase 3是Phase 4-5的基础） |

---

## 核心职责

完成 Phase 3 **前端K线图可视化**和**UI风格优化**，包括：

1. ✅ **K线图渲染组件** (ProKLineChart.vue)
2. ✅ **调用后端API获取K线数据和技术指标** (CLI-3提供)
3. ✅ **A股特性可视化** (涨跌停线/复权/T+1标记)
4. ✅ **图表交互优化** (缩放/平移/十字光标)
5. ✅ **性能优化到60fps**
6. ✅ **UI Style Agents风格统一** (/opt/iflow/myhtml/prompts)

**架构原则**:
- ✅ 前端只负责**展示**，不计算指标
- ✅ 所有指标数据从后端API获取（CLI-3提供）
- ✅ 利用后端TA-Lib + GPU加速计算
- ✅ 统一应用UI Style Agents设计规范

---

## 依赖关系

### 输入依赖

- ✅ **Phase 1-2 已完成**: 深色主题 + TypeScript环境
- ✅ **klinecharts 9.6.0**: 已在 dependencies 中
- ⏳ **CLI-2 API契约**: 需要OpenAPI schema和TypeScript类型定义 (并行开发，可先用Mock)
- ⏳ **CLI-3 后端实现**: TA-Lib指标计算 + A股规则引擎 (第二轮，可先用Mock API)

### 输出依赖

- ➡️ **为CLI-3提供**: 前端指标展示需求，帮助CLI-3设计API接口
- ➡️ **为CLI-4提供**: K线图组件，AI筛选结果可在K线图上可视化
- ➡️ **为CLI-5提供**: 性能基准，GPU监控可参考前端渲染性能

---

## 关键API端点（由CLI-2定义，CLI-3实现）

**在CLI-2完成之前，使用Mock API数据开发**

```typescript
// 1. K线数据
GET /api/market/kline
  ?symbol=000001.SZ
  &interval=1d           // 1m/5m/15m/1h/1d/1w/1M
  &start_date=2024-01-01
  &end_date=2024-12-29
  &adjust=qfq            // qfq前复权/hfq后复权/none不复权

Response: {
  code: 0,
  data: {
    symbol: "000001.SZ",
    interval: "1d",
    adjust: "qfq",
    candles: [
      {
        timestamp: 1704067200000,  // Unix timestamp (ms)
        open: 10.5,
        high: 11.2,
        low: 10.3,
        close: 10.8,
        volume: 1000000,
        amount: 10800000
      }
    ]
  }
}

// 2. 主图叠加指标
GET /api/indicators/overlay
  ?symbol=000001.SZ
  &interval=1d
  &indicators=MA,EMA,BOLL  // 可叠加多个
  &params={"MA_period":20,"EMA_period":12,"BOLL_period":20}

Response: {
  code: 0,
  data: {
    MA: [
      { timestamp: 1704067200000, value: 10.6 }
    ],
    EMA: [...],
    BOLL: [
      {
        timestamp: 1704067200000,
        upper: 11.5,
        middle: 10.8,
        lower: 10.1
      }
    ]
  }
}

// 3. 副图震荡指标
GET /api/indicators/oscillator
  ?symbol=000001.SZ
  &interval=1d
  &indicators=MACD,RSI,KDJ
  &params={"MACD_fast":12,"MACD_slow":26}

Response: {
  code: 0,
  data: {
    MACD: [
      {
        timestamp: 1704067200000,
        dif: 0.12,
        dea: 0.09,
        macd: 0.03
      }
    ],
    RSI: [
      { timestamp: 1704067200000, value: 65.2 }
    ]
  }
}

// 4. A股涨跌停限制
GET /api/astock/stop-limit
  ?symbol=000001.SZ
  &date=2024-12-29
  &prev_close=10.5

Response: {
  code: 0,
  data: {
    limit_up: 11.55,    // 涨停价
    limit_down: 9.45,   // 跌停价
    limit_pct: 0.10     // 涨跌停比例 (10%)
  }
}

// 5. T+1可卖查询
GET /api/astock/t1-sellable
  ?buy_date=2024-12-28

Response: {
  code: 0,
  data: {
    sellable_date: "2024-12-29",
    t_status: "T+1"  // T+0当天买入/T+1次日可卖
  }
}
```

---

## 任务清单（12个任务）

### T3.1: ProKLineChart核心组件搭建 ⭐

**优先级**: 🔴 高
**预计时间**: 2天
**依赖**: Phase 1-2完成

**详细描述**:

1. 创建ProKLineChart.vue组件
   - 基于klinecharts 9.6.0 API
   - 支持多周期切换 (1m/5m/15m/1h/1d/1w/1M)
   - 支持复权模式切换 (前复权/后复权/不复权)

2. 实现Mock K线数据加载
   - 先用本地Mock数据开发（等待CLI-3后端实现）
   - Mock数据格式与API契约一致

3. 基本K线渲染
   - 蜡烛图渲染
   - X轴时间轴
   - Y轴价格轴
   - 成交量柱状图

**验收标准**:
- [ ] ProKLineChart组件正常渲染
- [ ] 支持7个周期切换（1分/5分/15分/1小时/日/周/月）
- [ ] 支持3种复权模式切换
- [ ] Mock数据加载正常
- [ ] 响应式布局适配不同屏幕尺寸

**关键文件**:
```
web/frontend/src/components/Charts/ProKLineChart.vue
web/frontend/src/api/mockKlineData.ts  # Mock数据
web/frontend/src/types/kline.ts        # K线类型定义
```

---

### T3.2: 后端API集成（K线数据）

**优先级**: 🔴 高
**预计时间**: 1.5天
**依赖**: T3.1完成 + CLI-2 API契约定义

**详细描述**:

1. 集成后端K线数据API
   - 替换Mock数据为真实API调用
   - 使用Axios或Fetch封装HTTP请求
   - 错误处理和重试机制

2. 实现数据缓存
   - LocalStorage缓存最近访问的K线数据
   - 减少重复API请求
   - 缓存过期策略（1小时）

3. 加载状态管理
   - Loading动画
   - 错误提示
   - 空数据处理

**验收标准**:
- [ ] 成功调用后端 /api/market/kline 接口
- [ ] 数据缓存机制正常工作
- [ ] Loading状态正确显示
- [ ] 错误处理和用户提示完善
- [ ] 支持复权模式切换（API参数传递）

**关键文件**:
```
web/frontend/src/api/klineApi.ts
web/frontend/src/utils/cacheManager.ts
web/frontend/src/stores/klineStore.ts  # Pinia状态管理
```

---

### T3.3: A股特性可视化（涨跌停/复权/T+1） ⭐

**优先级**: 🔴 高
**预计时间**: 2天
**依赖**: T3.2完成

**详细描述**:

1. 涨跌停可视化
   - 调用 `/api/astock/stop-limit` 获取涨跌停价格
   - 绘制红色涨停线（10%主板 / 5% ST / 30%北交所）
   - 绘制绿色跌停线
   - 鼠标悬停显示涨跌停价格和比例

2. 复权计算展示
   - 前复权: 显示"前复权"标签
   - 后复权: 显示"后复权"标签
   - 不复权: 显示"不复权"标签
   - 复权切换按钮

3. T+1交易标记
   - 调用 `/api/astock/t1-sellable` 判断可卖日期
   - 当日买入K线标记"T+0"（红色）
   - 次日可卖K线标记"T+1"（绿色）

**验收标准**:
- [ ] 涨跌停线准确显示（误差<0.01元）
- [ ] 不同板块涨跌停比例正确（主板10%/ST 5%/北交所30%）
- [ ] 复权模式标签正确显示
- [ ] T+1标记在当日K线上显示
- [ ] 单元测试覆盖率>80%

**关键文件**:
```
web/frontend/src/components/Charts/ProKLineChart.vue
web/frontend/src/utils/astock/StopLimitOverlay.ts  # 涨跌停绘制
web/frontend/src/utils/astock/T1Marker.ts          # T+1标记
web/frontend/src/api/astockApi.ts                  # A股API调用
```

---

### T3.4: 主图技术指标叠加（调用后端API）

**优先级**: 🔴 高
**预计时间**: 2天
**依赖**: T3.3完成 + CLI-3后端指标API实现

**详细描述**:

1. 集成主图叠加指标API
   - 调用 `/api/indicators/overlay` 获取MA/EMA/BOLL等指标
   - 在K线主图上绘制指标曲线
   - 支持多指标同时叠加（最多5个）

2. 指标选择器UI
   - 下拉菜单选择指标类型
   - 参数设置对话框（MA周期、EMA周期等）
   - 指标颜色自定义

3. 实时更新
   - 周期切换时自动刷新指标
   - 参数修改后实时重绘

**验收标准**:
- [ ] 成功调用后端 /api/indicators/overlay 接口
- [ ] 至少支持10个主图指标（MA/EMA/BOLL/SAR/KAMA等）
- [ ] 主图最多叠加5个指标
- [ ] 指标参数可自定义
- [ ] 指标颜色可自定义

**关键文件**:
```
web/frontend/src/components/Charts/IndicatorSelector.vue
web/frontend/src/components/Charts/IndicatorParameterDialog.vue
web/frontend/src/api/indicatorApi.ts
web/frontend/src/utils/indicatorRenderer.ts  # 指标绘制工具
```

---

### T3.5: 副图技术指标（MACD/RSI/KDJ）

**优先级**: 🔴 高
**预计时间**: 2天
**依赖**: T3.4完成

**详细描述**:

1. 集成副图震荡指标API
   - 调用 `/api/indicators/oscillator` 获取MACD/RSI/KDJ
   - 在副图区域绘制指标
   - 支持多副图（最多3个）

2. 副图布局管理
   - 动态调整主图和副图高度比例
   - 副图可拖拽调整顺序
   - 副图可关闭/隐藏

3. 指标坐标轴
   - 独立Y轴刻度
   - 自动缩放
   - 零轴线高亮

**验收标准**:
- [ ] 成功调用后端 /api/indicators/oscillator 接口
- [ ] 至少支持20个副图指标
- [ ] 副图最多显示3个指标
- [ ] 副图高度比例可调整
- [ ] 指标计算准确（对比TA-Lib标准值）

**关键文件**:
```
web/frontend/src/components/Charts/ProKLineChart.vue  # 副图管理
web/frontend/src/utils/oscillatorRenderer.ts
web/frontend/src/types/indicator.ts
```

---

### T3.6: 图表交互（缩放/平移/十字光标）

**优先级**: 🔴 高
**预计时间**: 2天
**依赖**: T3.5完成

**详细描述**:

1. 鼠标滚轮缩放
   - 放大: 显示更少K线，细节更清晰
   - 缩小: 显示更多K线，趋势更明显
   - 缩放中心: 鼠标位置

2. 鼠标拖拽平移
   - 左右拖拽浏览历史数据
   - 边界检测（不能平移到数据外）

3. 十字光标
   - 显示当前K线的OHLCV数据
   - 显示所有指标的当前值
   - 跟随鼠标移动
   - 时间和价格坐标显示

4. 移动端触摸支持
   - 双指缩放
   - 单指拖拽
   - 长按显示十字光标

**验收标准**:
- [ ] 缩放流畅（60fps）
- [ ] 平移流畅（60fps）
- [ ] 十字光标数据准确
- [ ] 移动端触摸操作正常
- [ ] 支持双指缩放（移动端）

**关键文件**:
```
web/frontend/src/utils/chartInteraction.ts
web/frontend/src/utils/crosshair.ts
```

---

### T3.7: 性能优化到60fps

**优先级**: 🔴 高
**预计时间**: 2天
**依赖**: T3.6完成

**详细描述**:

1. Canvas分层渲染
   - 静态层: K线主体、坐标轴
   - 动态层: 十字光标、指标
   - 减少不必要的重绘

2. 虚拟滚动
   - 只渲染可见区域的K线
   - 超出视口的K线不渲染
   - 滚动时动态加载

3. WebWorker后台计算
   - 指标数据处理移到Worker
   - 避免阻塞UI线程

4. 优化重绘策略
   - 使用requestAnimationFrame
   - 批量更新
   - 避免全量重绘

**验收标准**:
- [ ] 加载1000根K线渲染时间<500ms
- [ ] 滚动/缩放操作帧率≥60fps
- [ ] CPU占用率<30%（空闲时）
- [ ] 内存占用稳定（无泄漏）
- [ ] Lighthouse性能分数>90

**关键文件**:
```
web/frontend/src/utils/chartRenderer.ts
web/frontend/src/workers/indicatorDataWorker.worker.ts
```

---

### T3.8: UI Style Agents风格统一 ⭐

**优先级**: 🟡 中
**预计时间**: 2天
**依赖**: T3.7完成 + /opt/iflow/myhtml/prompts

**详细描述**:

1. 研读UI Style Agents
   - 分析 `/opt/iflow/myhtml/prompts` 下的UI设计规范
   - 提取颜色、字体、间距、动画等设计Token
   - 理解Bloomberg/Wind风格的专业金融终端美学

2. 应用到ProKLineChart
   - 统一配色方案（深色主题）
   - 字体规范（Roboto Mono等宽字体用于数字）
   - 间距和布局（8px网格系统）
   - 动画规范（过渡300ms）

3. 创建Design Tokens
   - CSS变量定义颜色、字体、间距
   - 确保与Framework B一致

**验收标准**:
- [ ] 完整研读UI Style Agents文档
- [ ] ProKLineChart配色符合专业金融终端风格
- [ ] 字体和排版符合设计规范
- [ ] 间距和布局符合8px网格系统
- [ ] 动画过渡流畅自然

**关键文件**:
```
web/frontend/src/styles/design-tokens.scss  # Design Tokens
web/frontend/src/components/Charts/ProKLineChart.vue
docs/design/UI_STYLE_AGENTS_ANALYSIS.md  # UI风格分析文档
```

---

### T3.9: 响应式布局优化

**优先级**: 🟡 中
**预计时间**: 1.5天
**依赖**: T3.8完成

**详细描述**:

1. PC端布局
   - 1920x1080标准分辨率优化
   - 支持4K屏幕（3840x2160）

2. 平板布局
   - iPad Pro (1024x1366) 适配
   - 横屏/竖屏自适应

3. 移动端布局
   - iPhone (375x812) 适配
   - Android多分辨率适配
   - 触摸优化（按钮最小44px）

**验收标准**:
- [ ] PC端1920x1080完美显示
- [ ] 平板横竖屏切换正常
- [ ] 移动端375px最小宽度正常显示
- [ ] 触摸操作区域≥44px
- [ ] Responsive设计通过Chrome DevTools测试

**关键文件**:
```
web/frontend/src/components/Charts/ProKLineChart.vue
web/frontend/src/styles/responsive.scss
```

---

### T3.10: 单元测试覆盖ProKLineChart核心功能

**优先级**: 🟡 中
**预计时间**: 1.5天
**依赖**: T3.9完成

**详细描述**:

1. 测试ProKLineChart组件
   - 组件挂载和卸载
   - Props变化响应
   - 事件触发

2. 测试A股特性可视化
   - 涨跌停计算
   - 复权模式切换
   - T+1标记

3. 测试图表交互
   - 缩放事件
   - 平移事件
   - 十字光标

4. 测试API集成
   - Mock API调用
   - 错误处理
   - 缓存机制

**验收标准**:
- [ ] 单元测试覆盖率>80%
- [ ] 所有测试通过（100%）
- [ ] 关键路径有E2E测试
- [ ] 性能测试通过

**关键文件**:
```
web/frontend/tests/unit/ProKLineChart.spec.ts
web/frontend/tests/unit/AStockFeatures.spec.ts
web/frontend/tests/unit/ChartInteraction.spec.ts
```

---

### T3.11: E2E测试K线图加载和交互

**优先级**: 🟡 中
**预计时间**: 1.5天
**依赖**: T3.10完成

**详细描述**:

1. 测试K线图加载流程
   - 页面打开
   - 股票选择
   - K线数据加载
   - 指标叠加

2. 测试周期切换
   - 1分/5分/15分/1小时/日/周/月

3. 测试指标叠加和切换
   - 主图指标叠加
   - 副图指标叠加
   - 参数修改

4. 测试缩放和平移
   - 鼠标滚轮缩放
   - 鼠标拖拽平移

5. 测试十字光标
   - 鼠标悬停
   - 数据显示准确性

**验收标准**:
- [ ] E2E测试通过率100%
- [ ] 覆盖至少15个场景
- [ ] 每个场景有截图对比
- [ ] 性能测试通过（60fps）

**关键文件**:
```
web/frontend/tests/e2e/kline-chart.spec.ts
web/frontend/tests/e2e/fixtures/kline-data.json
```

---

### T3.12: Phase 3 完成报告与验收

**优先级**: 🔴 高
**预计时间**: 1天
**依赖**: T3.11完成

**详细描述**:

1. 运行完整测试套件
   - 单元测试
   - E2E测试
   - 性能测试
   - 响应式测试

2. 验收所有功能
   - 对照验收标准逐项检查
   - 记录问题和解决方案

3. 生成Phase 3完成报告
   - 功能完成情况
   - 性能指标
   - 测试覆盖率
   - 已知问题和后续优化建议

**验收标准**:
- [ ] 所有验收标准通过
- [ ] 无阻塞性Bug
- [ ] 性能达标（60fps）
- [ ] 文档完整

**输出**:
```
docs/reports/PHASE3_COMPLETION_REPORT.md
```

---

## 总体验收标准

### 功能完整性
- [ ] ProKLineChart组件支持7个周期（1分/5分/15分/1小时/日/周/月）
- [ ] 成功调用后端API获取K线数据和技术指标
- [ ] A股涨跌停限制可视化（红色/绿色边界线）
- [ ] 前复权/后复权/不复权切换正常
- [ ] T+1交易标记准确显示
- [ ] 主图至少支持10个叠加指标
- [ ] 副图至少支持20个震荡指标
- [ ] 图表交互流畅（缩放/平移/十字光标）
- [ ] UI Style Agents风格统一应用

### 性能指标
- [ ] 图表渲染性能 ≥ 60fps
- [ ] 加载1000根K线时间 < 500ms
- [ ] CPU占用率 < 30%（空闲时）
- [ ] 内存占用稳定（无泄漏）
- [ ] Lighthouse性能分数 > 90

### 测试覆盖
- [ ] 单元测试覆盖率 > 80%
- [ ] E2E测试通过率 100%
- [ ] 性能测试通过
- [ ] 响应式测试通过（PC/平板/移动端）

### 文档完整性
- [ ] 用户使用指南完整
- [ ] API集成文档完整
- [ ] UI Style Agents分析文档完整
- [ ] Phase 3完成报告完整

---

## 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| CLI-2 API契约延迟 | 中 | 中 | 先用Mock API开发，契约定义后切换 |
| CLI-3 后端实现延迟 | 中 | 高 | 保持Mock API，增量集成后端 |
| 性能优化不达标 | 中 | 高 | 优先使用Canvas，必要时降级到SVG |
| 移动端兼容性问题 | 低 | 中 | 优先保证PC端，移动端渐进增强 |
| UI Style Agents理解偏差 | 低 | 中 | 与设计团队频繁沟通，及时调整 |

---

## 关键文件清单

```
web/frontend/
├── src/
│   ├── components/
│   │   └── Charts/
│   │       ├── ProKLineChart.vue          # 核心K线图组件
│   │       ├── IndicatorSelector.vue      # 指标选择器
│   │       └── IndicatorParameterDialog.vue  # 指标参数对话框
│   ├── api/
│   │   ├── klineApi.ts                    # K线数据API
│   │   ├── indicatorApi.ts                # 指标API
│   │   ├── astockApi.ts                   # A股规则API
│   │   └── mockKlineData.ts               # Mock数据
│   ├── utils/
│   │   ├── chartRenderer.ts               # 图表渲染优化
│   │   ├── chartInteraction.ts            # 图表交互逻辑
│   │   ├── crosshair.ts                   # 十字光标
│   │   ├── cacheManager.ts                # 缓存管理
│   │   ├── indicatorRenderer.ts           # 指标绘制
│   │   ├── oscillatorRenderer.ts          # 副图指标绘制
│   │   └── astock/
│   │       ├── StopLimitOverlay.ts        # 涨跌停绘制
│   │       └── T1Marker.ts                # T+1标记
│   ├── types/
│   │   ├── kline.ts                       # K线类型定义
│   │   └── indicator.ts                   # 指标类型定义
│   ├── stores/
│   │   └── klineStore.ts                  # K线状态管理（Pinia）
│   ├── styles/
│   │   ├── design-tokens.scss             # Design Tokens
│   │   └── responsive.scss                # 响应式样式
│   └── workers/
│       └── indicatorDataWorker.worker.ts  # 指标数据处理Worker
└── tests/
    ├── unit/
    │   ├── ProKLineChart.spec.ts
    │   ├── AStockFeatures.spec.ts
    │   └── ChartInteraction.spec.ts
    └── e2e/
        ├── kline-chart.spec.ts
        └── fixtures/
            └── kline-data.json
```

---

## 进度跟踪

**当前状态**: ⏳ 待启动
**完成任务**: 0/12 (0%)
**预计完成日期**: Day 15

**更新日志**:
- 2025-12-29: 任务分配文件创建（架构调整为TA-Lib后端+UI Style Agents整合）

---

**审批状态**: ⏳ 待审批
**审批人**: 项目负责人
**创建日期**: 2025-12-29
**架构版本**: v2.0 (TA-Lib Backend + GPU Acceleration + UI Style Agents)
