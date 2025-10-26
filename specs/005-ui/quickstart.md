# Quick Start Guide: UI系统改进

**Feature**: UI系统改进 - 字体系统、问财查询、自选股重构
**Target Audience**: 前端开发者
**Estimated Setup Time**: 10分钟
**Last Updated**: 2025-10-26

## 前置条件

在开始之前，确保你已经：

- ✅ Node.js 16+ 已安装
- ✅ npm 或 yarn 已安装
- ✅ 项目代码已clone到本地
- ✅ 已切换到 `005-ui` 分支
- ✅ 前端开发服务器可正常运行

## 快速开始

### 1. 环境准备（2分钟）

```bash
# 切换到项目根目录
cd /path/to/mystocks_spec

# 切换到feature分支（如果尚未切换）
git checkout 005-ui

# 进入前端目录
cd web/frontend

# 安装依赖（如果尚未安装）
npm install

# 启动开发服务器
npm run dev
```

开发服务器应该在 http://localhost:3000 启动。

### 2. 项目结构概览（3分钟）

#### 📁 关键目录

```
web/frontend/src/
├── assets/styles/
│   └── typography.css         # [NEW] 全局字体系统
├── components/
│   ├── settings/
│   │   └── FontSizeSetting.vue  # [MODIFY] 字体设置组件
│   ├── market/
│   │   ├── WencaiPanel.vue      # [MODIFY] 问财筛选面板
│   │   └── WencaiQueryList.vue  # [NEW] 预设查询列表
│   └── stock/
│       ├── WatchlistTabs.vue    # [MODIFY] 自选股选项卡
│       └── WatchlistTable.vue   # [MODIFY] 自选股表格
├── config/
│   └── wencaiQueries.js         # [NEW] 问财查询配置
└── stores/
    └── preferences.js           # [MODIFY] 偏好设置store
```

#### 🔑 核心文件

| 文件 | 作用 | 优先级 |
|------|------|--------|
| `typography.css` | 定义全局字体CSS Variables | P1 |
| `preferences.js` | 管理用户偏好设置（字体、标签页状态等） | P1 |
| `wencaiQueries.js` | 9个问财预设查询配置 | P2 |
| `WatchlistTabs.vue` | 自选股选项卡布局 | P3 |

### 3. 开发工作流（5分钟）

#### 步骤 1: 实施字体系统（P1）

**a. 创建全局字体样式**

创建 `src/assets/styles/typography.css`:

```css
/* Typography System - FR-001 to FR-005 */
:root {
  /* 基础字号变量 */
  --font-size-base: 16px;

  /* 字体层级（自动计算） */
  --font-size-helper: calc(var(--font-size-base) - 2px);  /* 辅助文字 */
  --font-size-body: var(--font-size-base);                /* 正文 */
  --font-size-subtitle: calc(var(--font-size-base) + 2px); /* 小标题 */
  --font-size-title: calc(var(--font-size-base) + 4px);   /* 标题 */
  --font-size-heading: calc(var(--font-size-base) + 8px); /* 主标题 */

  /* Typography字体族 - FR-004 */
  --font-family: "Helvetica Neue", Helvetica, "PingFang SC",
                 "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑",
                 Arial, sans-serif;

  /* 行高 - FR-005 */
  --line-height-base: 1.5;
}

/* 应用到body */
body {
  font-family: var(--font-family);
  font-size: var(--font-size-body);
  line-height: var(--line-height-base);
}

/* 工具类 */
.text-helper { font-size: var(--font-size-helper); }
.text-body { font-size: var(--font-size-body); }
.text-subtitle { font-size: var(--font-size-subtitle); }
.text-title { font-size: var(--font-size-title); }
.text-heading { font-size: var(--font-size-heading); }
```

**b. 在main.js中导入**

```javascript
// src/main.js
import './assets/styles/typography.css'
```

**c. 修改FontSizeSetting.vue**

关键代码片段：

```javascript
// 字体大小选项
const FONT_SIZES = [
  { value: '12px', label: '特小', key: 'xs' },
  { value: '14px', label: '小', key: 'sm' },
  { value: '16px', label: '中', key: 'md' },
  { value: '18px', label: '大', key: 'lg' },
  { value: '20px', label: '特大', key: 'xl' }
]

// 更新字体大小（FR-006）
function handleFontSizeChange(newSize) {
  // 立即更新CSS变量
  document.documentElement.style.setProperty('--font-size-base', newSize)

  // 保存到LocalStorage（FR-007）
  preferencesStore.updatePreference('fontSize', newSize)

  ElMessage.success(`字体大小已更新为 ${newSize}`)
}

// 页面加载时恢复（FR-008）
onMounted(() => {
  const savedSize = preferencesStore.preferences.fontSize || '16px'
  document.documentElement.style.setProperty('--font-size-base', savedSize)
})
```

#### 步骤 2: 实施问财查询（P2）

**a. 创建查询配置文件**

```javascript
// src/config/wencaiQueries.js
export const WENCAI_PRESET_QUERIES = [
  {
    id: 'qs_1',
    name: '连续上涨股票',
    description: '查询连续3天以上上涨的股票',
    query: '连续3天以上上涨',
    category: '趋势'
  },
  // ... qs_2 to qs_9
  // 参考 specs/005-ui/contracts/wencai-queries.json
]
```

**b. 修改WencaiPanel.vue**

```vue
<template>
  <div class="wencai-panel">
    <!-- 预设查询列表 -->
    <el-card header="默认查询">
      <WencaiQueryList
        :queries="WENCAI_PRESET_QUERIES"
        @select="handleQuerySelect"
      />
    </el-card>

    <!-- 查询结果 -->
    <el-card header="查询结果" v-if="queryResults">
      <WencaiQueryTable :data="queryResults" />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { WENCAI_PRESET_QUERIES } from '@/config/wencaiQueries'
import { dataApi } from '@/api'

const queryResults = ref(null)

async function handleQuerySelect(query) {
  const response = await dataApi.wencaiQuery({ query: query.query })
  queryResults.value = response.data
}
</script>
```

#### 步骤 3: 实施自选股重构（P3）

**a. 修改Watchlist.vue**

```vue
<template>
  <div class="watchlist-page">
    <el-tabs v-model="activeTab" type="card" @tab-change="handleTabChange">
      <el-tab-pane label="用户自选" name="user">
        <WatchlistTable :data="stocks.user" group-highlight />
      </el-tab-pane>
      <el-tab-pane label="系统自选" name="system">
        <WatchlistTable :data="stocks.system" group-highlight />
      </el-tab-pane>
      <el-tab-pane label="策略自选" name="strategy">
        <WatchlistTable :data="stocks.strategy" group-highlight />
      </el-tab-pane>
      <el-tab-pane label="监控列表" name="monitor">
        <WatchlistTable :data="stocks.monitor" group-highlight />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import WatchlistTable from '@/components/stock/WatchlistTable.vue'

const activeTab = ref('user')

// FR-019: 页面加载时恢复标签页状态
onMounted(() => {
  const saved = localStorage.getItem('watchlist.activeTab')
  if (saved) activeTab.value = saved
})

// FR-019: 保存标签页状态
function handleTabChange(tab) {
  localStorage.setItem('watchlist.activeTab', tab)
}
</script>
```

**b. 修改WatchlistTable.vue添加分组高亮**

```vue
<el-table
  :data="data"
  :row-class-name="getRowClassName"
  height="600"
>
  <!-- columns -->
</el-table>

<script setup>
// FR-016: 分组高亮
function getRowClassName({ row }) {
  if (!row.groupId) return ''
  return `group-${row.groupId % 4}`
}
</script>

<style scoped>
.group-0 { background-color: #f0f9ff; } /* 蓝色系 */
.group-1 { background-color: #f0fdf4; } /* 绿色系 */
.group-2 { background-color: #fef3f2; } /* 红色系 */
.group-3 { background-color: #fefce8; } /* 黄色系 */
</style>
```

---

## 测试你的修改

### 手动测试清单

#### ✅ 字体系统测试

1. [ ] 访问系统设置 → 字体大小
2. [ ] 选择不同字体等级（12px/14px/16px/18px/20px）
3. [ ] 验证页面字体立即响应
4. [ ] 刷新页面，验证字体设置保留
5. [ ] 打开新标签页，验证字体设置同步

#### ✅ 问财查询测试

1. [ ] 访问市场数据 → 问财筛选
2. [ ] 验证显示9个预设查询
3. [ ] 点击任意查询（如qs_3）
4. [ ] 验证查询结果正确显示
5. [ ] 验证当前查询高亮显示

#### ✅ 自选股测试

1. [ ] 访问自选股页面
2. [ ] 验证显示4个标签页
3. [ ] 切换不同标签页
4. [ ] 验证表格固定表头
5. [ ] 验证分组高亮效果
6. [ ] 刷新页面，验证标签页状态保留

---

## 常见问题

### Q1: 字体大小不生效怎么办？

**A**: 检查以下几点：
1. 确认`typography.css`已在`main.js`中导入
2. 确认CSS Variables正确设置：`document.documentElement.style.getPropertyValue('--font-size-base')`
3. 检查浏览器控制台是否有CSS错误

### Q2: LocalStorage被禁用怎么办？

**A**: 实现了降级策略，使用默认值16px。可在`preferences.js`中添加try-catch：

```javascript
try {
  localStorage.setItem('test', 'test')
  localStorage.removeItem('test')
} catch (e) {
  console.warn('LocalStorage not available, using in-memory storage')
  // 使用内存存储
}
```

### Q3: 问财API返回错误怎么办？

**A**: 检查：
1. 后端服务是否正常运行
2. API endpoint是否正确：`/api/market/wencai/query`
3. 查询语句格式是否符合问财API规范

---

## 下一步

1. **运行 `/speckit.tasks`** 生成详细的任务清单
2. **运行 `/speckit.implement`** 开始实施任务
3. **提交代码** 使用规范的commit message

---

## 技术支持

- 📖 查看完整设计：[data-model.md](./data-model.md)
- 🔬 查看研究结果：[research.md](./research.md)
- 📋 查看实施计划：[plan.md](./plan.md)
- 🐛 遇到问题？查看项目README或提issue

Happy Coding! 🚀
