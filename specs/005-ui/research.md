# Research & Technology Decisions

**Feature**: UI系统改进 - 字体系统、问财查询、自选股重构
**Date**: 2025-10-26
**Status**: Completed

## Overview

本文档记录了在实施UI系统改进过程中的技术决策和研究结果。

## 研究项目

### R1: CSS Variables vs Sass Variables for Dynamic Font Sizing

**研究问题**: 如何实现动态字体大小调整且能立即响应用户设置变更？

**选项评估**:

| 方案 | 优点 | 缺点 | 评分 |
|------|------|------|------|
| CSS Variables | 运行时动态更新、浏览器原生支持、无需重编译 | 不支持IE11 | ⭐⭐⭐⭐⭐ |
| Sass Variables | 编译时优化、更好的IDE支持 | 无法运行时更新、需要重新编译 | ⭐⭐ |
| JavaScript动态样式 | 灵活性高 | 性能较差、代码复杂度高 | ⭐⭐⭐ |

**决策**: **选择CSS Variables**

**理由**:
1. 支持运行时动态更新，满足FR-006"用户更改字体大小时立即更新"需求
2. 通过`document.documentElement.style.setProperty()`可以立即生效
3. 现代浏览器支持良好（Chrome 49+, Firefox 31+, Safari 9.1+）
4. 项目不需要支持IE11（已在Technical Context中声明）

**实施方案**:
```css
:root {
  --font-size-base: 16px;
  --font-size-helper: calc(var(--font-size-base) - 2px);
  --font-size-body: var(--font-size-base);
  --font-size-subtitle: calc(var(--font-size-base) + 2px);
  --font-size-title: calc(var(--font-size-base) + 4px);
  --font-size-heading: calc(var(--font-size-base) + 8px);
  --font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB",
                 "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  --line-height-base: 1.5;
}
```

**参考资料**:
- MDN: Using CSS custom properties https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties
- Can I Use: CSS Variables https://caniuse.com/css-variables

---

### R2: LocalStorage vs SessionStorage for Preference Persistence

**研究问题**: 用户字体偏好应该使用LocalStorage还是SessionStorage？

**选项评估**:

| 方案 | 持久化 | 作用域 | 容量 | 评分 |
|------|--------|--------|------|------|
| LocalStorage | 永久（除非手动清除） | 同源所有标签页 | 5-10MB | ⭐⭐⭐⭐⭐ |
| SessionStorage | 会话期间 | 当前标签页 | 5-10MB | ⭐⭐ |
| Cookie | 可设置过期时间 | 同源所有标签页 | 4KB | ⭐⭐⭐ |
| IndexedDB | 永久 | 同源所有标签页 | >50MB | ⭐⭐ (过度设计) |

**决策**: **选择LocalStorage**

**理由**:
1. 满足FR-007和FR-008关于持久化的需求（刷新页面后保持设置）
2. 用户期望字体设置在关闭浏览器后仍然保留
3. 数据量小（<1KB），不需要IndexedDB的大容量
4. 同源所有标签页共享，用户体验一致

**实施方案**:
```javascript
// Pinia store: stores/preferences.js
export const usePreferencesStore = defineStore('preferences', {
  state: () => ({
    fontSize: '16px'
  }),
  actions: {
    updatePreference(key, value) {
      this[key] = value
      localStorage.setItem(`preferences.${key}`, value)
    },
    loadPreferences() {
      const fontSize = localStorage.getItem('preferences.fontSize')
      if (fontSize) this.fontSize = fontSize
    }
  }
})
```

**降级策略**: 如果LocalStorage不可用（私密模式或禁用），使用内存变量（当前会话有效）

**参考资料**:
- MDN: Window.localStorage https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage

---

### R3: Element Plus Tabs Component Best Practices

**研究问题**: 如何使用Element Plus Tabs实现自选股的选项卡布局？

**技术方案**:

使用`el-tabs`组件，配合`v-model`实现标签页切换：

```vue
<template>
  <el-tabs v-model="activeTab" type="card">
    <el-tab-pane label="用户自选" name="user">
      <WatchlistTable :data="userWatchlist" group-highlight />
    </el-tab-pane>
    <el-tab-pane label="系统自选" name="system">
      <WatchlistTable :data="systemWatchlist" group-highlight />
    </el-tab-pane>
    <el-tab-pane label="策略自选" name="strategy">
      <WatchlistTable :data="strategyWatchlist" group-highlight />
    </el-tab-pane>
    <el-tab-pane label="监控列表" name="monitor">
      <WatchlistTable :data="monitorWatchlist" group-highlight />
    </el-tab-pane>
  </el-tabs>
</template>
```

**关键特性**:
1. **标签页状态持久化**: 使用LocalStorage记住activeTab
2. **懒加载**: 使用`lazy`属性延迟加载标签页内容
3. **滚动位置保持**: 使用`keep-alive`保持组件状态

**最佳实践**:
- 使用`type="card"`获得卡片式外观
- 每个tab-pane使用唯一的name作为标识
- 通过`v-model`绑定activeTab实现双向数据绑定

**参考资料**:
- Element Plus Tabs文档: https://element-plus.org/en-US/component/tabs.html

---

### R4: 问财API集成方案

**研究问题**: 如何配置和调用9个问财预设查询？

**现有API分析**:

根据代码库分析，问财API端点为`/api/market/wencai/*`，已在后端实现。

**配置方案**:

创建前端配置文件`config/wencaiQueries.js`：

```javascript
export const WENCAI_PRESET_QUERIES = [
  {
    id: 'qs_1',
    name: '连续上涨股票',
    description: '查询连续3天以上上涨的股票',
    query: '连续3天以上上涨',
    category: '趋势'
  },
  {
    id: 'qs_2',
    name: '放量突破',
    description: '成交量放大且突破前期高点',
    query: '成交量放大且突破前期高点',
    category: '突破'
  },
  {
    id: 'qs_3',
    name: '资金流入前20',
    description: '主力资金净流入排名前20',
    query: '主力资金净流入排名前20',
    category: '资金'
  },
  // ... qs_4 to qs_9
]
```

**调用方式**:
```javascript
async function executePresetQuery(queryId) {
  const query = WENCAI_PRESET_QUERIES.find(q => q.id === queryId)
  const response = await dataApi.wencaiQuery({ query: query.query })
  return response.data
}
```

**决策**: 使用前端配置文件 + API调用

**理由**:
1. 查询模板相对稳定，前端配置即可
2. 便于维护和更新查询内容
3. 支持未来扩展（用户自定义查询）

**参考资料**:
- 现有WencaiPanel.vue组件实现

---

### R5: 表格分组高亮实现方案

**研究问题**: 如何在el-table中实现分组高亮效果？

**技术方案**:

使用`row-class-name`回调函数动态添加CSS类：

```vue
<template>
  <el-table
    :data="tableData"
    :row-class-name="getRowClassName"
  >
    <!-- columns -->
  </el-table>
</template>

<script setup>
function getRowClassName({ row, rowIndex }) {
  if (!row.group_id) return ''
  return `group-${row.group_id % 4}` // 循环使用4种颜色
}
</script>

<style scoped>
.group-0 { background-color: #f0f9ff; } /* 蓝色系 */
.group-1 { background-color: #f0fdf4; } /* 绿色系 */
.group-2 { background-color: #fef3f2; } /* 红色系 */
.group-3 { background-color: #fefce8; } /* 黄色系 */
</style>
```

**替代方案对比**:

| 方案 | 优点 | 缺点 | 评分 |
|------|------|------|------|
| row-class-name | Element Plus原生支持、性能好 | 需要预定义CSS类 | ⭐⭐⭐⭐⭐ |
| cell-style | 更灵活 | 性能较差、代码复杂 | ⭐⭐⭐ |
| 自定义渲染 | 完全自由 | 失去el-table优势 | ⭐⭐ |

**决策**: 使用row-class-name

**参考资料**:
- Element Plus Table文档: https://element-plus.org/en-US/component/table.html#table-attributes

---

## 技术栈总结

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.4.0 | 前端框架 |
| Element Plus | 2.8.0 | UI组件库 |
| Pinia | 2.2.0 | 状态管理 |
| Vite | 5.4.0 | 构建工具 |
| CSS Variables | - | 动态字体系统 |
| LocalStorage | - | 偏好设置持久化 |

## 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| CSS Variables性能影响 | 低 | 中 | Phase 1进行性能基准测试 |
| LocalStorage被禁用 | 低 | 低 | 实现降级策略（使用默认值） |
| 现有组件兼容性 | 中 | 中 | 手动测试所有受影响页面 |
| 问财API变更 | 低 | 高 | 使用配置文件隔离API变更影响 |

## 下一步

Phase 1将基于这些研究结果生成：
1. data-model.md - 数据结构设计
2. contracts/wencai-queries.json - 完整的9个查询配置
3. quickstart.md - 开发者快速开始指南
