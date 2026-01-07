# Element Plus 渐进式迁移状态报告

**日期**: 2026-01-07
**状态**: 🔄 进行中

## 已完成（Phase 1 基础设施）

✅ **依赖安装**
- element-plus 已安装
- vue-grid-layout 已安装
- @element-plus/icons-vu e 已安装

✅ **主题配置**
- `/src/styles/element-plus-compact.scss` 已创建
- 紧凑CSS变量已定义（字体12-13px，padding 16px，高度32px）
- A股颜色支持（红涨绿跌）

✅ **main.js配置**
- Element Plus已导入
- ArtDeco样式已移除
- 紧凑主题已应用

## 当前问题

⚠️ **批量迁移挑战**
- Element Plus API与自建组件存在差异
- el-table需要el-table-column子组件（结构差异）
- el-tag使用slot而非:text属性
- 简单的sed替换无法处理所有情况

## 调整后的策略（渐进式迁移）

### 阶段1: 清理ArtDeco组件（立即执行）

1. **归档所有ArtDeco组件**
   ```bash
   mkdir -p /opt/mydoc/design/ArtDeco/components
   mv /opt/claude/mystocks_spec/web/frontend/src/components/artdeco/* /opt/mydoc/design/ArtDeco/components/
   ```

2. **删除ArtDeco样式文件**
   ```bash
   rm -f /opt/claude/mystocks_spec/web/frontend/src/styles/artdeco-*.scss
   ```

3. **删除ArtDeco路由**
   - 移除 `/src/views/artdeco/` 相关路由配置

### 阶段2: 核心视图优先迁移

**优先级排序**（按使用频率）：
1. Dashboard.vue
2. Market.vue
3. BacktestAnalysis.vue
4. RiskMonitor.vue
5. StrategyManagement.vue

**每个视图的迁移步骤**：
1. 创建Element Plus版本
2. 保留原版本备份（命名为`*.backup.vue`）
3. 测试功能
4. 验证通过后删除备份

### 阶段3: Element Plus组件使用指南

#### DataTable → el-table 迁移模板

**旧代码**:
```vue
<DataTable
  :columns="columns"
  :data="data"
  :loading="loading"
/>
```

**新代码**:
```vue
<el-table
  :data="data"
  v-loading="loading"
  stripe
  style="width: 100%"
>
  <el-table-column
    v-for="col in columns"
    :key="col.key"
    :prop="col.key"
    :label="col.label"
    :sortable="col.sortable ? 'custom' : false"
    :formatter="col.format"
  />
</el-table>
```

#### DataCard → el-card 迁移模板

**旧代码**:
```vue
<DataCard
  title="标题"
  subtitle="副标题"
  :hoverable="true"
>
  内容
</DataCard>
```

**新代码**:
```vue
<el-card>
  <template #header>
    <div class="card-header">
      <span>标题</span>
      <span class="subtitle">副标题</span>
    </div>
  </template>
  内容
</el-card>
```

#### ActionButton → el-button 迁移模板

**旧代码**:
```vue
<ActionButton
  variant="primary"
  size="sm"
  :loading="loading"
  @click="handleClick"
>
  按钮
</ActionButton>
```

**新代码**:
```vue
<el-button
  type="primary"
  size="small"
  :loading="loading"
  @click="handleClick"
>
  按钮
</el-button>
```

#### StatusBadge → el-tag 迁移模板

**旧代码**:
```vue
<StatusBadge
  :text="status"
  variant="success"
/>
```

**新代码**:
```vue
<el-tag
  :type="getStatusType(status)"
>
  {{ status }}
</el-tag>

<script setup>
function getStatusType(status) {
  const map = {
    success: 'success',
    error: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return map[status] || 'info'
}
</script>
```

### 阶段4: Vue-GridLayout集成（Phase 3）

**创建网格仪表板组件**:
```vue
<!-- DashboardGrid.vue -->
<template>
  <grid-layout
    v-model:layout="layout"
    :col-num="12"
    :row-height="30"
    :is-draggable="true"
    :is-resizable="true"
  >
    <grid-item
      v-for="item in layout"
      :key="item.i"
      :x="item.x"
      :y="item.y"
      :w="item.w"
      :h="item.h"
      :i="item.i"
    >
      <component :is="item.component" v-bind="item.props" />
    </grid-item>
  </grid-layout>
</template>
```

## 下一步行动

### 立即执行（今日）

1. **归档ArtDeco组件** (5分钟)
2. **清理ArtDeco样式** (5分钟)
3. **迁移Dashboard.vue** (30分钟)
4. **迁移Market.vue** (20分钟)
5. **迁移BacktestAnalysis.vue** (20分钟)

### 验证测试

- [ ] TypeScript编译无错误
- [ ] 核心页面可访问
- [ ] 数据显示正确
- [ ] 交互功能正常

## 预计完成时间

- **今日**: 核心视图迁移（3-4个视图）
- **明日**: 剩余视图迁移（8-10个视图）
- **后日**: Vue-GridLayout集成和优化

## 参考资料

- [Element Plus官方文档](https://element-plus.org/en-US/component/table)
- [Element Plus组件API](https://element-plus.org/en-US/component/button)
- [Vue-GridLayout文档](https://jbaysolutions.github.io/vue-grid-layout/)
- 紧凑主题: `/src/styles/element-plus-compact.scss`

---

**状态**: 🔄 等待用户确认新策略
**下一步**: 执行阶段1（清理ArtDeco）
