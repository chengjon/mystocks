# MyStocks UI 设计系统总索引

**版本**: v1.0.0
**最后更新**: 2025-12-25
**维护者**: UI Design Team
**位置**: `docs/standards/`

---

## 📚 文档导航

本文档体系提供完整的 MyStocks Web 界面设计规范、组件库和页面设计指南。

### 🎯 快速开始

如果你是**新加入的设计师/开发者**，建议按以下顺序阅读：

1. **[设计总览](#00-设计总览)** - 了解项目背景、技术栈和核心功能
2. **[设计系统](#01-设计系统)** - 掌握颜色、字体、布局等基础设计规范
3. **[组件库](#02-组件库)** - 熟悉可复用的 UI 组件
4. **[页面设计](#03-页面设计)** - 查看具体页面的设计规范
5. **[交互流程](#04-交互流程)** - 理解用户操作流程和交互逻辑

---

## 🎨 设计原则

MyStocks 的设计遵循以下核心原则：

### 1. **专业可信** (Professional & Trustworthy)
- **颜色选择**: 使用沉稳的蓝灰色调，传达专业和稳定
- **数据可视化**: 清晰准确的图表，避免过度装饰
- **信息层次**: 严格的视觉层次，突出关键信息

### 2. **高效操作** (Efficient Operations)
- **减少点击**: 常用操作一步到位
- **快捷键支持**: 为高频操作提供键盘快捷键
- **批量操作**: 支持多选和批量处理

### 3. **实时响应** (Real-time Feedback)
- **数据推送**: WebSocket 实时行情推送
- **加载状态**: 明确的加载进度提示
- **错误反馈**: 友好的错误信息和恢复建议

### 4. **可访问性** (Accessibility)
- **键盘导航**: 完整的键盘操作支持
- **色彩对比**: 符合 WCAG 2.1 AA 标准
- **屏幕阅读器**: 语义化 HTML 和 ARIA 标签

---

## 🛠️ 技术栈

### 前端框架
- **Vue 3.4+**: 渐进式 JavaScript 框架
- **TypeScript 5.3+**: 类型安全的 JavaScript
- **Vite 5.4+**: 快速的构建工具

### UI 组件库
- **Element Plus**: 基于 Vue 3 的企业级 UI 库
  - [Element Plus 官网](https://element-plus.org/)
  - [Element Plus 设计指南](https://element-plus.org/en-US/guide/design.html)

### 状态管理
- **Pinia**: Vue 3 官方推荐的状态管理库

### 图表库
- **ECharts 5.x**: 专业数据可视化
- **KlineChart**: 专业 K 线图组件

### 实时通信
- **Socket.IO**: 双向实时通信
- **SSE (Server-Sent Events)**: 服务器推送事件

---

## 📖 文档结构

```
docs/standards/
├── UI_DESIGN_SYSTEM.md                 # 本文档 - 总索引
├── 00-DESIGN_OVERVIEW.md               # 设计总览
├── 01-DESIGN_SYSTEM/                   # 设计系统
│   ├── README.md
│   ├── color-system.md                 # 颜色系统
│   ├── typography.md                   # 字体系统
│   ├── layout-system.md                # 布局系统
│   └── design-tokens.md                # 设计 Tokens
├── 02-COMPONENT_LIBRARY/               # 组件库
│   ├── README.md
│   ├── base-components.md              # 基础组件
│   ├── business-components.md          # 业务组件
│   ├── chart-components.md             # 图表组件
│   └── composite-components.md         # 复合组件
├── 03-PAGE_DESIGNS/                    # 页面设计 (9个页面)
│   ├── README.md
│   ├── 01-dashboard.md                 # 仪表盘
│   ├── 02-market-quotes.md             # 市场行情
│   ├── 03-market-data.md               # 市场数据
│   ├── 04-stock-management.md          # 股票管理
│   ├── 05-data-analysis.md             # 数据分析
│   ├── 06-risk-management.md           # 风险管理
│   ├── 07-strategy-backtest.md         # 策略回测
│   ├── 08-trading-management.md        # 交易管理
│   └── 09-other-pages.md               # 其他页面
└── 04-INTERACTION_FLOWS/               # 交互流程
    ├── README.md
    └── user-flows.md                   # 用户流程
```

---

## 🎯 设计决策说明

### 为什么选择 Vue 3 + Element Plus？

**Vue 3 优势**:
- ✅ **Composition API**: 更好的逻辑复用和代码组织
- ✅ **性能提升**: 相比 Vue 2 性能提升 1.5-2 倍
- ✅ **TypeScript 支持**: 原生 TypeScript 类型定义
- ✅ **生态成熟**: 丰富的插件和工具链

**Element Plus 优势**:
- ✅ **企业级**: 专为后台管理系统设计
- ✅ **组件丰富**: 60+ 高质量组件
- ✅ **主题定制**: 支持深度主题定制
- ✅ **国际化**: 完整的中文支持
- ✅ **可访问性**: 符合 WAI-ARIA 标准

### 为什么选择 TypeScript？

**类型安全**:
```typescript
// ✅ 编译时类型检查
interface StockQuote {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
}

function updateQuote(quote: StockQuote) {
  // 类型安全，IDE 智能提示
  console.log(quote.price.toFixed(2))
}
```

**更好的开发体验**:
- IDE 智能提示和自动补全
- 重构更安全（全局重命名）
- 减少运行时错误

### 为什么选择 ECharts？

**金融数据可视化优势**:
- ✅ **K 线图**: 专业蜡烛图支持
- ✅ **实时更新**: 高性能增量渲染
- ✅ **交互丰富**: 缩放、平移、十字线
- ✅ **主题定制**: 深色/浅色主题切换

---

## 🌈 主题系统

### 默认主题 - 专业蓝

```scss
// 主色调
$primary-color: #409EFF      // Element Plus 默认蓝
$success-color: #67C23A      // 成功绿
$warning-color: #E6A23C      // 警告橙
$danger-color: #F56C6C       // 危险红
$info-color: #909399         // 信息灰

// 涨跌颜色
$rise-color: #F56C6C         // 涨 (红色)
$fall-color: #67C23A         // 跌 (绿色)

// 中性色
$text-primary: #303133       // 主要文本
$text-regular: #606266       // 常规文本
$text-secondary: #909399     // 次要文本
$text-placeholder: #C0C4CC   // 占位文本

// 背景色
$bg-color: #FFFFFF           // 白色背景
$bg-page: #F2F3F5            // 页面背景
$bg-overlay: #000000         // 遮罩层
```

### 深色主题 (Dark Mode)

```scss
// 深色主题
$dark-bg-color: #141414
$dark-bg-page: #0a0a0a
$dark-text-primary: #E5EAF3
$dark-text-regular: #CFD3DC
$dark-border-color: #4C4D4F
```

---

## 📐 响应式断点

```scss
// 断点定义
$breakpoint-xs: 480px   // 超小屏幕
$breakpoint-sm: 768px   // 小屏幕 (平板)
$breakpoint-md: 992px   // 中屏幕 (桌面)
$breakpoint-lg: 1200px  // 大屏幕
$breakpoint-xl: 1920px  // 超大屏幕

// 使用 Mixin
@mixin respond-to($breakpoint) {
  @if $breakpoint == 'sm' {
    @media (max-width: $breakpoint-sm) { @content; }
  }
  @else if $breakpoint == 'md' {
    @media (max-width: $breakpoint-md) { @content; }
  }
}
```

**响应式布局示例**:
```vue
<template>
  <div class="dashboard" :class="{ 'mobile': isMobile }">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <!-- 卡片 -->
      </el-col>
    </el-row>
  </div>
</template>
```

---

## 🔧 设计 Tokens

### 间距系统

```scss
// 8点网格系统
$spacing-xs: 4px    // 0.25rem
$spacing-sm: 8px    // 0.5rem
$spacing-md: 16px   // 1rem
$spacing-lg: 24px   // 1.5rem
$spacing-xl: 32px   // 2rem
$spacing-xxl: 48px  // 3rem
```

### 圆角系统

```scss
$radius-xs: 2px     // 小圆角
$radius-sm: 4px     // 默认圆角
$radius-md: 8px     // 中圆角
$radius-lg: 12px    // 大圆角
$radius-xl: 16px    // 超大圆角
```

### 阴影系统

```scss
$shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.05)
$shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1)
$shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1)
$shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1)
$shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15)
```

---

## 📱 页面布局

### 标准页面结构

```
┌─────────────────────────────────────────────────────────┐
│  顶部导航栏 (Header)                                      │
│  Logo | 主菜单 | 用户信息                                 │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│  侧边栏   │            主内容区 (Content)                 │
│ (Sidebar)│                                              │
│          │  ┌────────────────────────────────────────┐  │
│ 菜单      │  │ 面包屑 (Breadcrumb)                    │  │
│ - 仪表盘  │  ├────────────────────────────────────────┤  │
│ - 行情    │  │ 页面标题 (Page Title)                   │  │
│ - 数据    │  ├────────────────────────────────────────┤  │
│ - 分析    │  │                                        │  │
│ - 风险    │  │  内容区域 (Main Content)                │  │
│ - 策略    │  │                                        │  │
│ - 交易    │  │                                        │  │
│          │  └────────────────────────────────────────┘  │
└──────────┴──────────────────────────────────────────────┘
```

### 布局组件

```vue
<template>
  <el-container class="layout-default">
    <!-- 顶部导航 -->
    <el-header height="60px">
      <app-header />
    </el-header>

    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="240px">
        <app-sidebar />
      </el-aside>

      <!-- 主内容区 -->
      <el-main>
        <el-breadcrumb />
        <page-title />
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
```

---

## 🎯 组件使用指南

### Element Plus 常用组件

| 组件 | 用途 | 文档链接 |
|-----|------|---------|
| `el-table` | 数据表格 | [文档](https://element-plus.org/en-US/component/table.html) |
| `el-form` | 表单 | [文档](https://element-plus.org/en-US/component/form.html) |
| `el-dialog` | 对话框 | [文档](https://element-plus.org/en-US/component/dialog.html) |
| `el-message` | 消息提示 | [文档](https://element-plus.org/en-US/component/message.html) |
| `el-card` | 卡片 | [文档](https://element-plus.org/en-US/component/card.html) |
| `el-tabs` | 标签页 | [文档](https://element-plus.org/en-US/component/tabs.html) |
| `el-select` | 下拉选择 | [文档](https://element-plus.org/en-US/component/select.html) |
| `el-date-picker` | 日期选择 | [文档](https://element-plus.org/en-US/component/date-picker.html) |

### 自定义业务组件

详见 [组件库文档](./02-COMPONENT_LIBRARY/README.md)。

---

## 🚀 开发工具

### 开发环境

```bash
# 进入前端目录
cd web/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问地址
http://localhost:3020
```

### 代码规范

```bash
# 代码格式化
npm run format

# 代码检查
npm run lint

# 类型检查
npm run type-check
```

### 构建部署

```bash
# 生产构建
npm run build

# 预览构建结果
npm run preview
```

---

## 📝 设计规范更新日志

### v1.0.0 (2025-12-25)
- ✅ 初始版本
- ✅ 建立文档结构
- ✅ 定义设计系统基础
- ✅ 组件库规范
- ✅ 9个页面设计规范

---

## 🤝 贡献指南

### 设计规范更新流程

1. **创建分支**: `git checkout -b design/update-component-name`
2. **更新文档**: 修改对应的设计文档
3. **提交 PR**: 说明变更内容和影响范围
4. **代码审查**: 由设计团队审查
5. **合并发布**: 更新版本号和变更日志

### 文档编写规范

1. **使用 Markdown**: 保持格式统一
2. **提供示例**: 代码示例必须可运行
3. **截图说明**: 关键界面提供截图
4. **交叉引用**: 建立文档间的链接
5. **版本控制**: 每次更新记录版本号

---

## 📞 联系方式

- **设计团队**: design@mystocks.com
- **前端团队**: frontend@mystocks.com
- **Issue 跟踪**: [GitHub Issues](https://github.com/chengjon/mystocks/issues)

---

## 📚 相关资源

### 项目内部文档
- [前端开发者指南](../guides/onboarding/DEVELOPER_GUIDE.md)
- [项目交互指南](../overview/IFLOW.md)
- [API 文档](../api/README.md)

### 外部资源
- [Vue 3 官方文档](https://vuejs.org/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [Element Plus 官方文档](https://element-plus.org/)
- [Pinia 官方文档](https://pinia.vuejs.org/)
- [Vite 官方文档](https://vitejs.dev/)
- [ECharts 官方文档](https://echarts.apache.org/)
- [Web Content Accessibility Guidelines (WCAG)](https://www.w3.org/WAI/WCAG21/quickref/)

---

## 📋 下一步阅读

根据你的角色选择合适的文档：

### 设计师
1. [设计系统](./01-DESIGN_SYSTEM/README.md) - 了解颜色、字体、布局
2. [组件库](./02-COMPONENT_LIBRARY/README.md) - 查看可复用组件
3. [页面设计](./03-PAGE_DESIGNS/README.md) - 浏览页面设计规范

### 前端开发者
1. [前端开发者指南](../guides/onboarding/DEVELOPER_GUIDE.md) - 开发规范
2. [组件库](./02-COMPONENT_LIBRARY/README.md) - 组件使用方法
3. [交互流程](./04-INTERACTION_FLOWS/README.md) - 用户交互逻辑

### 产品经理
1. [设计总览](./00-DESIGN_OVERVIEW.md) - 项目概览
2. [页面设计](./03-PAGE_DESIGNS/README.md) - 功能页面
3. [交互流程](./04-INTERACTION_FLOWS/README.md) - 用户流程

---

**文档版本**: v1.0.0
**最后更新**: 2025-12-25
**维护者**: UI Design Team
**位置**: `docs/standards/UI_DESIGN_SYSTEM.md`
