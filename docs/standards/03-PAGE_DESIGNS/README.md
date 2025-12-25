# 页面设计

**版本**: v1.0.0
**最后更新**: 2025-12-25
**上级文档**: [UI_DESIGN_SYSTEM.md](../UI_DESIGN_SYSTEM.md)

---

## 📋 目录

本目录包含 MyStocks 所有页面的设计规范。

### 📄 页面列表

1. **[仪表盘](./01-dashboard.md)** - Dashboard
   - 市场概况
   - 三大指数
   - 自选股监控
   - 重要告警

2. **[市场行情](./02-market-quotes.md)** - Market Quotes
   - 实时行情列表
   - 技术指标分析
   - 分时图和K线图
   - 市场热度

3. **[市场数据](./03-market-data.md)** - Market Data
   - 历史行情数据
   - 财务数据
   - 公司资料
   - 公告资讯

4. **[股票管理](./04-stock-management.md)** - Stock Management
   - 自选股分组
   - 股票池管理
   - 股票对比
   - 价格提醒

5. **[数据分析](./05-data-analysis.md)** - Data Analysis
   - 技术指标计算
   - 交易信号生成
   - 指标叠加分析
   - 自定义指标

6. **[风险管理](./06-risk-management.md)** - Risk Management
   - VaR 计算
   - 压力测试
   - 风险预警
   - 风险报告

7. **[策略回测](./07-strategy-backtest.md)** - Strategy Backtest
   - 策略列表
   - 回测配置
   - 回测执行
   - 绩效报告

8. **[交易管理](./08-trading-management.md)** - Trading Management
   - 订单管理
   - 持仓查询
   - 成交记录
   - 交易设置

9. **[其他页面](./09-other-pages.md)** - Other Pages
   - 系统设置
   - 数据管理
   - 用户管理
   - 帮助中心

---

## 🎨 页面设计原则

### 1. 一致的布局结构

所有页面遵循统一的布局模式：

```
┌─────────────────────────────────────────────────────────┐
│  Header (导航栏)                                          │
│  Logo | 主菜单 | 用户信息                                 │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│  Sidebar │            Main Content (主内容区)            │
│  (侧边栏) │                                              │
│          │  ┌────────────────────────────────────────┐  │
│ 菜单      │  │ Breadcrumb (面包屑)                    │  │
│ - 仪表盘  │  ├────────────────────────────────────────┤  │
│ - 行情    │  │ Page Title (页面标题)                   │  │
│ - 数据    │  ├────────────────────────────────────────┤  │
│ - 分析    │  │                                        │  │
│ - 风险    │  │  Content (内容区域)                     │  │
│ - 策略    │  │                                        │  │
│ - 交易    │  │                                        │  │
│          │  └────────────────────────────────────────┘  │
└──────────┴──────────────────────────────────────────────┘
```

### 2. 清晰的信息层次

- **H1 (24px)**: 页面标题
- **H2 (20px)**: 区块标题
- **H3 (18px)**: 卡片标题
- **Body (14px)**: 正文内容
- **Small (12px)**: 辅助说明

### 3. 一致的间距系统

- **页面级**: 48px
- **区块级**: 32px
- **组件级**: 24px
- **元素级**: 16px
- **紧凑级**: 8px

### 4. 统一的卡片设计

所有卡片遵循以下样式：

```vue
<template>
  <el-card class="default-card">
    <!-- 卡片标题 -->
    <template #header>
      <div class="card-header">
        <span class="title">卡片标题</span>
        <el-button-group>
          <el-button size="small">刷新</el-button>
          <el-button size="small">更多</el-button>
        </el-button-group>
      </div>
    </template>

    <!-- 卡片内容 -->
    <div class="card-body">
      <!-- 内容区域 -->
    </div>
  </el-card>
</template>

<style lang="scss" scoped>
.default-card {
  border-radius: $--border-radius-base;
  box-shadow: $--box-shadow-light;

  &:hover {
    box-shadow: $--box-shadow-base;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .title {
    font-size: $font-size-h3;
    font-weight: $font-weight-semibold;
    color: $--color-text-primary;
  }
}

.card-body {
  padding: $spacing-md;
}
</style>
```

---

## 📱 响应式设计

### 断点系统

| 断点 | 宽度 | 布局调整 |
|-----|------|---------|
| **xs** | < 480px | 单列布局，隐藏侧边栏 |
| **sm** | ≥ 480px | 单列布局 |
| **md** | ≥ 768px | 两列布局 |
| **lg** | ≥ 992px | 三列布局 |
| **xl** | ≥ 1200px | 完整布局 |

### 响应式布局示例

```vue
<template>
  <el-row :gutter="20">
    <el-col :xs="24" :sm="24" :md="12" :lg="8" :xl="6">
      <!-- 卡片 1 -->
    </el-col>
    <el-col :xs="24" :sm="24" :md="12" :lg="8" :xl="6">
      <!-- 卡片 2 -->
    </el-col>
    <el-col :xs="24" :sm="24" :md="12" :lg="8" :xl="6">
      <!-- 卡片 3 -->
    </el-col>
    <el-col :xs="24" :sm="24" :md="12" :lg="8" :xl="6">
      <!-- 卡片 4 -->
    </el-col>
  </el-row>
</template>
```

---

## 🎯 页面模板

### 标准页面模板

```vue
<template>
  <div class="page-container">
    <!-- 面包屑 -->
    <el-breadcrumb class="breadcrumb" separator="/">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>模块</el-breadcrumb-item>
      <el-breadcrumb-item>页面</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">页面标题</h1>
      <div class="page-actions">
        <el-button type="primary" icon="Plus">新建</el-button>
        <el-button icon="Refresh">刷新</el-button>
      </div>
    </div>

    <!-- 筛选栏 (可选) -->
    <div v-if="showFilter" class="page-filter">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="请输入" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="请选择">
            <el-option label="全部" value="" />
            <el-option label="启用" value="enabled" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="handleSearch">
            搜索
          </el-button>
          <el-button icon="RefreshLeft" @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 主内容区 -->
    <div class="page-content">
      <!-- 内容区域 -->
      <slot />
    </div>

    <!-- 分页 (可选) -->
    <div v-if="showPagination" class="page-pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

// 筛选表单
const filterForm = reactive({
  keyword: '',
  status: '',
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0,
})

// 是否显示筛选栏
const showFilter = ref(true)

// 是否显示分页
const showPagination = ref(true)

// 方法
const handleSearch = () => {
  console.log('搜索', filterForm)
}

const handleReset = () => {
  filterForm.keyword = ''
  filterForm.status = ''
}

const handleSizeChange = (size: number) => {
  pagination.size = size
}

const handlePageChange = (page: number) => {
  pagination.page = page
}
</script>

<style lang="scss" scoped>
.page-container {
  padding: $spacing-lg;
}

.breadcrumb {
  margin-bottom: $spacing-md;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-lg;

  .page-title {
    font-size: $font-size-h1;
    font-weight: $font-weight-semibold;
    color: $--color-text-primary;
    margin: 0;
  }

  .page-actions {
    display: flex;
    gap: $spacing-sm;
  }
}

.page-filter {
  margin-bottom: $spacing-md;
  padding: $spacing-md;
  background-color: $--color-bg-white;
  border-radius: $--border-radius-base;
}

.page-content {
  margin-bottom: $spacing-lg;
}

.page-pagination {
  display: flex;
  justify-content: center;
}
</style>
```

---

## 📊 页面数据加载

### 加载状态

```vue
<template>
  <div class="page-container">
    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 加载完成 -->
    <div v-else-if="!loading">
      <!-- 页面内容 -->
    </div>

    <!-- 错误状态 -->
    <el-empty v-else description="加载失败">
      <el-button type="primary" @click="handleReload">
        重新加载
      </el-button>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const loading = ref(true)

const loadData = async () => {
  loading.value = true
  try {
    // 加载数据
    await fetchData()
  } catch (error) {
    console.error('加载失败', error)
  } finally {
    loading.value = false
  }
}

const handleReload = () => {
  loadData()
}

onMounted(() => {
  loadData()
})
</script>
```

---

## 🎨 页面样式规范

### 页面容器

```scss
.page-container {
  min-height: 100vh;
  padding: $spacing-lg;
  background-color: $--color-bg-page;
}

// 响应式
@media (max-width: $breakpoint-md) {
  .page-container {
    padding: $spacing-md;
  }
}

@media (max-width: $breakpoint-sm) {
  .page-container {
    padding: $spacing-sm;
  }
}
```

### 卡片网格

```vue
<template>
  <el-row :gutter="20" class="card-grid">
    <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="item in items" :key="item.id">
      <el-card>{{ item.name }}</el-card>
    </el-col>
  </el-row>
</template>

<style lang="scss" scoped>
.card-grid {
  margin-bottom: $spacing-lg;
}
</style>
```

---

## ✅ 页面检查清单

在设计新页面时，请确保：

- [ ] 遵循统一的布局结构
- [ ] 使用 Design Tokens
- [ ] 支持响应式布局
- [ ] 提供加载状态
- [ ] 处理错误状态
- [ ] 添加面包屑导航
- [ ] 优化页面性能
- [ ] 确保无障碍访问
- [ ] 添加页面注释
- [ ] 编写单元测试

---

## 📚 相关资源

- [Vue Router](https://router.vuejs.org/)
- [Element Plus Layout](https://element-plus.org/en-US/component/layout.html)
- [Element Plus Container](https://element-plus.org/en-US/component/container.html)
- [响应式设计指南](https://web.dev/responsive-web-design-basics/)

---

## 🔄 更新日志

### v1.0.0 (2025-12-25)
- ✅ 初始版本
- ✅ 定义页面设计原则
- ✅ 提供页面模板
- ✅ 建立页面检查清单

---

## 📞 联系方式

- **设计团队**: design@mystocks.com
- **前端团队**: frontend@mystocks.com
- **问题反馈**: [GitHub Issues](https://github.com/chengjon/mystocks/issues)

---

**文档版本**: v1.0.0
**最后更新**: 2025-12-25
**维护者**: UI Design Team
**位置**: `docs/standards/03-PAGE_DESIGNS/README.md`
