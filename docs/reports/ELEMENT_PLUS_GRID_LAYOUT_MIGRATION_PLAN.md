# Element Plus + Vue-GridLayout 迁移方案

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


**日期**: 2026-01-07
**版本**: v2.0
**状态**: 📋 计划阶段

---

## 执行摘要

**目标**: 使用**Element Plus标准组件** + **Vue-GridLayout**替代ArtDeco和自建data组件，避免重复造轮子。

**核心原则**:
1. ✅ **使用成熟组件库** - Element Plus（Vue 3官方推荐）
2. ✅ **CSS变量覆盖** - 精确控制尺寸和样式，避免ArtDeco的"过大"问题
3. ✅ **网格布局系统** - Vue-GridLayout实现灵活多窗口仪表板
4. ✅ **数据密集设计** - 紧凑表格、小字体、高信息密度

**避免ArtDeco的问题**:
- ❌ 自定义组件维护成本高
- ❌ 组件尺寸不合适（padding过大、字体过大）
- ❌ 缺乏灵活性
- ❌ TypeScript类型定义不完整

---

## 技术栈选型

### 1. Element Plus - 核心组件库

**优势**:
- Vue 3官方推荐UI库
- 完整的TypeScript支持
- 丰富的组件（60+）
- 主题定制（CSS变量）
- 活跃的社区支持

**官方文档**:
- [Element Plus Table](https://element-plus.org/en-US/component/table)
- [Element Plus Theming](https://element-plus.org/en-US/guide/theming)

**关键CSS变量**:
```scss
// 表格样式覆盖
--el-table-border-color: #1A1A1A;
--el-table-bg-color: #0A0A0A;
--el-table-header-bg-color: #141414;
--el-table-row-hover-bg-color: #0F0F0F;
--el-table-text-color: #E5E5E5;
--el-table-header-text-color: #E5E5E5;

// 字体大小覆盖（关键！）
--el-font-size-extra-small: 10px;   // xs
--el-font-size-small: 12px;         // sm
--el-font-size-base: 13px;          // base (紧凑)
--el-font-size-medium: 14px;        // md
--el-font-size-large: 16px;         // lg

// 间距覆盖
--el-component-size-small: 28px;
--el-component-size-base: 32px;     // 紧凑
--el-component-size-large: 36px;
```

### 2. Vue-GridLayout - 仪表板布局

**优势**:
- 拖拽式网格布局
- 支持调整窗口大小
- 类似Gridster的功能
- 响应式列数配置

**官方文档**:
- [Vue-GridLayout Documentation](https://jbaysolutions.github.io/vue-grid-layout/)
- [NPM Package](https://www.npmjs.com/package/vue-grid-layout/v/2.0.1)

**替代方案**:
- **grid-layout-plus** (2025活跃fork)
- 基于gridster.js实现
- 性能优化

**中文资源**:
- [Vue Grid Layout 拖拽控制终极指南](https://blog.csdn.net/gitblog_00289/article/details/154417461)
- [vue-grid-layout数据可视化图表面板优化](https://zhuanlan.zhihu.com/p/600912455)

---

## 组件映射方案

### 原有组件 → Element Plus映射

| 原组件 | Element Plus替代 | CSS覆盖策略 |
|--------|-----------------|------------|
| DataCard | `el-card` | `--el-card-padding: 16px` |
| ActionButton | `el-button` | size="small", 自定义class |
| DataTable | `el-table` | `--el-table-*` 变量 |
| StatusBadge | `el-tag` | size="small", type映射 |
| FormField | `el-input` | size="small" |
| LoadingSpinner | `el-loading` | 自定义指令 |
| ArtDecoSidebar | `el-menu` | 折叠模式 |
| ArtDecoTopBar | 自定义header | 使用Element Plus图标 |

### 新增组件

| 需求 | Element Plus方案 |
|------|-----------------|
| 网格布局 | `vue-grid-layout` |
| 图表容器 | `el-card` + 网格item |
| 数据筛选器 | `el-form` + `el-select` |
| 分页器 | `el-pagination` |
| 日期选择 | `el-date-picker` |
| 开关 | `el-switch` |
| 滑块 | `el-slider` |

---

## 样式覆盖策略（关键！）

### 避免ArtDeco问题的核心方法

**问题根源**: ArtDeco的padding、字体、尺寸都偏大，不适合数据密集型仪表板。

**解决方案**: 通过CSS变量精确控制Element Plus的尺寸。

### 全局CSS变量覆盖

**文件**: `/opt/claude/mystocks_spec/web/frontend/src/styles/element-plus-compact.scss`

```scss
// Element Plus 紧凑主题覆盖
// 目标: 数据密集型量化交易仪表板

:root {
  // ========== 字体大小（关键） ==========
  --el-font-size-extra-small: 10px;   // 微小文字
  --el-font-size-small: 12px;         // 辅助文字
  --el-font-size-base: 13px;          // 正文（紧凑！）
  --el-font-size-medium: 14px;        // 标题
  --el-font-size-large: 16px;         // 大标题
  --el-font-size-extra-large: 18px;   // 页面标题

  // ========== 组件尺寸（关键） ==========
  --el-component-size-small: 28px;   // 小号
  --el-component-size-base: 32px;    // 默认（紧凑！）
  --el-component-size-large: 36px;   // 大号

  // ========== 表格样式（核心） ==========
  --el-table-border-color: #1A1A1A;
  --el-table-bg-color: #0A0A0A;
  --el-table-header-bg-color: #141414;
  --el-table-row-hover-bg-color: #0F0F0F;
  --el-table-text-color: #E5E5E5;
  --el-table-header-text-color: #E5E5E5;
  --el-table-current-row-bg-color: #1A1A1A;
  --el-table-border: 1px solid #1A1A1A;

  // ========== 卡片样式 ==========
  --el-card-padding: 16px;           // 紧凑padding！
  --el-card-border-color: #1A1A1A;
  --el-card-bg-color: #0A0A0A;
  --el-card-border-radius: 4px;

  // ========== 按钮样式 ==========
  --el-button-bg-color: #1A1A1A;
  --el-button-border-color: #2A2A2A;
  --el-button-text-color: #E5E5E5;
  --el-button-hover-bg-color: #252525;
  --el-button-hover-border-color: #3A3A3A;

  // ========== 输入框样式 ==========
  --el-input-bg-color: #0A0A0A;
  --el-input-border-color: #2A2A2A;
  --el-input-text-color: #E5E5E5;
  --el-input-placeholder-color: #666666;
  --el-input-hover-border-color: #3A3A3A;
  --el-input-focus-border-color: #3B82F6;

  // ========== Tag样式 ==========
  --el-tag-bg-color: #1A1A1A;
  --el-tag-border-color: #2A2A2A;
  --el-tag-text-color: #E5E5E5;

  // ========== 颜色系统 ==========
  --el-color-primary: #3B82F6;       // 蓝色
  --el-color-success: #00E676;       // 绿色（跌）
  --el-color-warning: #FFC107;       // 黄色
  --el-color-danger: #FF5252;        // 红色（涨）
  --el-color-info: #3B82F6;          // 信息蓝
}

// ========== 特定组件覆盖 ==========

// 表格单元格padding（紧凑！）
.el-table {
  .el-table__cell {
    padding: 8px 0;  // 默认12px → 8px
  }

  th.el-table__cell {
    padding: 8px 0;
  }
}

// 按钮紧凑模式
.el-button--small {
  padding: 4px 12px;
  height: 28px;
  font-size: 12px;
}

.el-button--default {
  padding: 6px 16px;
  height: 32px;  // 紧凑！
  font-size: 13px;
}

// 卡片紧凑模式
.el-card {
  --el-card-padding: 16px;  // 默认20px → 16px

  .el-card__header {
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 600;
  }

  .el-card__body {
    padding: 16px;
  }
}

// Tag紧凑模式
.el-tag {
  padding: 4px 10px;
  font-size: 12px;
  border-radius: 3px;
}

.el-tag--small {
  padding: 2px 6px;
  font-size: 11px;
}
```

---

## Vue-GridLayout集成方案

### 安装

```bash
npm install vue-grid-layout
# 或使用更新的fork
npm install grid-layout-plus
```

### 基础配置

**文件**: `src/components/DashboardGrid.vue`

```vue
<template>
  <grid-layout
    v-model:layout="layout"
    :col-num="12"
    :row-height="30"
    :is-draggable="true"
    :is-resizable="true"
    :is-mirrored="false"
    :vertical-compact="true"
    :margin="[10, 10]"
    :use-css-transforms="true"
  >
    <grid-item
      v-for="item in layout"
      :key="item.i"
      :x="item.x"
      :y="item.y"
      :w="item.w"
      :h="item.h"
      :i="item.i"
      :min-w="3"
      :min-h="2"
    >
      <el-card>
        <component :is="item.component" v-bind="item.props" />
      </el-card>
    </grid-item>
  </grid-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import GridLayout from 'vue-grid-layout'
import GridItem from 'vue-grid-layout'

interface LayoutItem {
  i: string
  x: number
  y: number
  w: number
  h: number
  component: string
  props?: Record<string, any>
}

const layout = ref<LayoutItem[]>([
  {
    i: '0',
    x: 0,
    y: 0,
    w: 6,
    h: 4,
    component: 'MarketDataTable',
    props: { title: '市场行情' }
  },
  {
    i: '1',
    x: 6,
    y: 0,
    w: 6,
    h: 4,
    component: 'StrategyTable',
    props: { title: '策略监控' }
  },
  {
    i: '2',
    x: 0,
    y: 4,
    w: 12,
    h: 6,
    component: 'KLineChart',
    props: { symbol: '000001' }
  }
])
</script>

<style scoped>
.vue-grid-layout {
  background: #000000;
}

.vue-grid-item {
  transition: all 150ms ease;
}

.vue-grid-item .vue-resizable-handle {
  background: #3B82F6;
  opacity: 0.3;
}

.vue-grid-item:hover .vue-resizable-handle {
  opacity: 0.6;
}
</style>
```

---

## 实施计划

### Phase 1: 基础设施搭建（1小时）

1. **安装依赖**
   ```bash
   npm install element-plus vue-grid-layout
   ```

2. **创建紧凑主题文件**
   - `src/styles/element-plus-compact.scss`
   - 定义所有CSS变量覆盖

3. **配置main.js**
   ```javascript
   import ElementPlus from 'element-plus'
   import 'element-plus/dist/index.css'
   import '@/styles/element-plus-compact.scss'
   ```

4. **创建网格布局组件**
   - `src/components/DashboardGrid.vue`

### Phase 2: 核心组件替换（2小时）

| 优先级 | 组件 | 文件 | 时间 |
|--------|------|------|------|
| P0 | DataTable → el-table | 所有视图 | 30min |
| P0 | DataCard → el-card | 所有视图 | 20min |
| P0 | ActionButton → el-button | 所有视图 | 20min |
| P1 | StatusBadge → el-tag | 所有视图 | 15min |
| P1 | FormField → el-input | 所有视图 | 15min |
| P2 | ArtDecoSidebar → el-menu | 布局文件 | 30min |
| P2 | LoadingSpinner → el-loading | 全局配置 | 10min |

### Phase 3: 仪表板布局改造（2小时）

1. **创建网格仪表板**
   - Dashboard.vue（使用vue-grid-layout）
   - ArtDecoDashboard.vue（迁移）
   - MonitoringDashboard.vue（迁移）

2. **配置窗口组件**
   - 可拖拽
   - 可调整大小
   - 保存布局配置

### Phase 4: 测试与优化（1小时）

1. **功能测试**
   - 所有组件正常显示
   - 交互功能正常
   - 数据绑定正确

2. **性能测试**
   - 渲染性能
   - 大数据量表格
   - 网格拖拽性能

3. **样式调整**
   - 字体大小合适
   - padding/margin一致
   - 颜色对比度足够

---

## 迁移检查清单

### 安装与配置

- [ ] 安装element-plus
- [ ] 安装vue-grid-layout
- [ ] 创建element-plus-compact.scss
- [ ] 配置main.js导入

### CSS变量覆盖

- [ ] 字体大小变量（10px-18px）
- [ ] 组件尺寸变量（28px-36px）
- [ ] 表格样式变量（颜色、padding）
- [ ] 卡片样式变量（padding: 16px）
- [ ] 按钮样式变量
- [ ] 输入框样式变量

### 组件替换

- [ ] el-table（13处）
- [ ] el-card（15处）
- [ ] el-button（14处）
- [ ] el-tag（11处）
- [ ] el-input（4处）
- [ ] el-menu（1处）
- [ ] el-loading（全局）

### 布局改造

- [ ] 创建DashboardGrid组件
- [ ] 配置网格布局参数
- [ ] 实现拖拽功能
- [ ] 实现调整大小功能
- [ ] 保存布局配置

### 测试验证

- [ ] TypeScript编译无错误
- [ ] 所有页面正常显示
- [ ] 交互功能正常
- [ ] 数据展示正确
- [ ] 性能可接受

---

## 常见问题解答

### Q1: Element Plus的默认样式太大怎么办？

**A**: 通过CSS变量精确控制。关键变量：
```scss
--el-font-size-base: 13px;        // 默认14px → 13px
--el-component-size-base: 32px;   // 紧凑高度
--el-card-padding: 16px;          // 默认20px → 16px
```

### Q2: 如何实现A股红涨绿跌？

**A**: 通过行类名和CSS：
```vue
<el-table
  :row-class-name="tableRowClassName"
>
</el-table>

<script setup>
function tableRowClassName({ row }) {
  if (row.change > 0) return 'rise-row'
  if (row.change < 0) return 'fall-row'
  return ''
}
</script>

<style>
.el-table .rise-row {
  color: #FF5252;
}

.el-table .fall-row {
  color: #00E676;
}
</style>
```

### Q3: Vue-GridLayout性能问题？

**A**:
1. 使用虚拟化表格（el-table-v2）
2. 限制网格item数量
3. 使用grid-layout-plus（性能优化版本）

### Q4: 如何保存用户的仪表板布局？

**A**: 保存到localStorage或后端：
```javascript
// 保存
localStorage.setItem('dashboard-layout', JSON.stringify(layout.value))

// 恢复
layout.value = JSON.parse(localStorage.getItem('dashboard-layout'))
```

---

## 优势总结

### 对比ArtDeco自建组件

| 维度 | ArtDeco自建 | Element Plus方案 |
|------|------------|-----------------|
| **维护成本** | ❌ 高（27个组件） | ✅ 低（使用成熟库） |
| **TypeScript** | ❌ 不完整 | ✅ 完整支持 |
| **文档** | ❌ 需自己写 | ✅ 官方文档完善 |
| **社区** | ❌ 无 | ✅ 活跃社区 |
| **Bug修复** | ❌ 自己修 | ✅ 官方维护 |
| **样式灵活性** | ⚠️ 硬编码 | ✅ CSS变量覆盖 |
| **尺寸控制** | ❌ 偏大 | ✅ 精确控制 |
| **布局灵活性** | ❌ 固定 | ✅ 拖拽网格 |

### 开发效率提升

- **组件开发时间**: -80%（使用现成组件）
- **样式调整时间**: -60%（CSS变量统一管理）
- **Bug修复时间**: -90%（官方维护）
- **文档维护时间**: -100%（官方文档）

---

## 参考资料

### Element Plus
- [官方文档 - Table](https://element-plus.org/en-US/component/table)
- [官方文档 - Theming](https://element-plus.org/en-US/guide/theming)
- [StackOverflow - Customization](https://stackoverflow.com/questions/78209850/how-to-customize-element-plus-el-table)
- [中文博客 - 样式修改](https://blog.csdn.net/weixin_47560716/article/details/129178026)

### Vue-GridLayout
- [官方文档](https://jbaysolutions.github.io/vue-grid-layout/)
- [拖拽控制指南](https://blog.csdn.net/gitblog_00289/article/details/154417461)
- [数据可视化优化](https://zhuanlan.zhihu.com/p/600912455)

### UI/UX设计
- UI/UX Pro Max 调研结果
- Data-Dense Dashboard设计原则
- Dark Mode (OLED)最佳实践

---

**下一步**: 用户确认方案 → 开始实施Phase 1

**预计总时间**: 6小时
**预计完成日期**: 2026-01-07（今日）
