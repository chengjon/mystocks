# WatchlistGroupManager.vue 组件元素清单

文件路径: `src/components/watchlist/WatchlistGroupManager.vue`
总行数: 313行
生成时间: 2025-11-08 22:35

---

## 📋 组件概览

**功能**: 自选股分组管理器
**类型**: 可复用组件 (Reusable Component)
**API**: Composition API (Vue 3)

---

## 🎨 模板元素 (Template Elements)

### 1. 根容器
```vue
<div class="watchlist-group-manager">
```
- **类型**: DIV容器
- **CSS类**: `.watchlist-group-manager`
- **作用**: 组件根元素

---

### 2. 分组列表头部 (Group Header)
```vue
<div class="group-header">
  <h3>自选股分组</h3>
  <el-button type="primary" size="small" icon="Plus" @click="showCreateDialog">
    新建分组
  </el-button>
</div>
```

#### 子元素:
- **标题 (H3)**
  - 文本: "自选股分组"
  - CSS类: 无

- **新建分组按钮 (el-button)**
  - 类型: `primary` (主要按钮)
  - 尺寸: `small`
  - 图标: `Plus`
  - 点击事件: `@click="showCreateDialog"`
  - 文本: "新建分组"

---

### 3. 分组列表容器 (Group List Container)
```vue
<el-scrollbar height="500px">
  <div v-loading="loading" class="group-list">
    <!-- 分组项循环 -->
  </div>
</el-scrollbar>
```

#### 元素属性:
- **滚动容器 (el-scrollbar)**
  - 高度: `500px`
  - Element Plus 滚动条组件

- **列表容器 (div)**
  - 加载状态: `v-loading="loading"`
  - CSS类: `.group-list`

---

### 4. 分组项 (Group Item)
```vue
<div
  v-for="group in groups"
  :key="group.id"
  :class="['group-item', { active: group.id === modelValue }]"
  @click="selectGroup(group)"
>
```

#### 元素属性:
- **循环指令**: `v-for="group in groups"`
- **唯一键**: `:key="group.id"`
- **动态类名**:
  - 基础类: `group-item`
  - 激活类: `active` (条件: `group.id === modelValue`)
- **点击事件**: `@click="selectGroup(group)"`

#### 子元素结构:

##### 4.1 分组信息区 (Group Info)
```vue
<div class="group-info">
  <span class="group-name">{{ group.group_name }}</span>
  <el-tag v-if="showStockCount" size="small" type="info">
    {{ group.stock_count }}只
  </el-tag>
</div>
```

**包含元素**:
- **分组名称 (span)**
  - CSS类: `.group-name`
  - 数据绑定: `{{ group.group_name }}`

- **股票数量标签 (el-tag)**
  - 条件渲染: `v-if="showStockCount"`
  - 尺寸: `small`
  - 类型: `info`
  - 数据绑定: `{{ group.stock_count }}只`

##### 4.2 操作按钮区 (Group Actions)
```vue
<div class="group-actions">
  <el-button
    v-if="group.group_name !== '默认分组'"
    size="small"
    icon="Edit"
    link
    @click.stop="showEditDialog(group)"
  />
  <el-button
    v-if="group.group_name !== '默认分组'"
    size="small"
    icon="Delete"
    link
    type="danger"
    @click.stop="confirmDelete(group)"
  />
</div>
```

**包含元素**:
- **编辑按钮 (el-button)**
  - 条件显示: `v-if="group.group_name !== '默认分组'"`
  - 尺寸: `small`
  - 图标: `Edit`
  - 样式: `link` (链接样式)
  - 点击事件: `@click.stop="showEditDialog(group)"`
  - 事件修饰符: `.stop` (阻止事件冒泡)

- **删除按钮 (el-button)**
  - 条件显示: `v-if="group.group_name !== '默认分组'"`
  - 尺寸: `small`
  - 图标: `Delete`
  - 样式: `link`
  - 类型: `danger` (危险操作)
  - 点击事件: `@click.stop="confirmDelete(group)"`
  - 事件修饰符: `.stop`

---

### 5. 创建/编辑对话框 (Dialog)
```vue
<el-dialog
  v-model="dialogVisible"
  :title="dialogMode === 'create' ? '新建分组' : '编辑分组'"
  width="400px"
>
```

#### 对话框属性:
- **显示控制**: `v-model="dialogVisible"`
- **动态标题**:
  - 创建模式: "新建分组"
  - 编辑模式: "编辑分组"
- **宽度**: `400px`

#### 对话框内容:

##### 5.1 表单 (el-form)
```vue
<el-form :model="form" label-width="80px">
  <el-form-item label="分组名称">
    <el-input
      v-model="form.group_name"
      placeholder="请输入分组名称"
      maxlength="100"
      show-word-limit
    />
  </el-form-item>
</el-form>
```

**表单元素**:
- **表单容器 (el-form)**
  - 数据模型: `:model="form"`
  - 标签宽度: `80px`

- **表单项 (el-form-item)**
  - 标签: "分组名称"

- **输入框 (el-input)**
  - 双向绑定: `v-model="form.group_name"`
  - 占位符: "请输入分组名称"
  - 最大长度: `100`
  - 显示字数统计: `show-word-limit`

##### 5.2 对话框底部按钮 (Footer)
```vue
<template #footer>
  <el-button @click="dialogVisible = false">取消</el-button>
  <el-button type="primary" @click="submitForm">确定</el-button>
</template>
```

**按钮元素**:
- **取消按钮 (el-button)**
  - 点击事件: `@click="dialogVisible = false"`
  - 文本: "取消"

- **确定按钮 (el-button)**
  - 类型: `primary`
  - 点击事件: `@click="submitForm"`
  - 文本: "确定"

---

## 🔧 脚本元素 (Script Elements)

### 1. 导入模块
```javascript
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
```

- **Vue 3 API**: `ref`, `onMounted`
- **Element Plus**: `ElMessage`, `ElMessageBox`
- **HTTP客户端**: `axios`

---

### 2. Props定义
```javascript
const props = defineProps({
  modelValue: {
    type: Number,
    default: null
  },
  showStockCount: {
    type: Boolean,
    default: true
  }
})
```

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `modelValue` | Number | `null` | 当前选中的分组ID (用于v-model) |
| `showStockCount` | Boolean | `true` | 是否显示股票数量 |

---

### 3. Emits定义
```javascript
const emit = defineEmits([
  'update:modelValue',
  'group-selected',
  'group-created',
  'group-updated',
  'group-deleted'
])
```

| 事件名 | 触发时机 | 传递参数 |
|--------|----------|----------|
| `update:modelValue` | 选择分组时 | 分组ID |
| `group-selected` | 选择分组时 | 分组对象 |
| `group-created` | 创建分组成功后 | 新分组对象 |
| `group-updated` | 更新分组成功后 | 更新后的分组数据 |
| `group-deleted` | 删除分组成功后 | 被删除的分组对象 |

---

### 4. 响应式数据
```javascript
const groups = ref([])              // 分组列表
const loading = ref(false)          // 加载状态
const dialogVisible = ref(false)    // 对话框显示状态
const dialogMode = ref('create')    // 对话框模式: 'create' | 'edit'
const form = ref({                  // 表单数据
  id: null,
  group_name: ''
})
```

| 变量名 | 类型 | 初始值 | 说明 |
|--------|------|--------|------|
| `groups` | Array | `[]` | 分组列表数据 |
| `loading` | Boolean | `false` | 列表加载状态 |
| `dialogVisible` | Boolean | `false` | 对话框可见性 |
| `dialogMode` | String | `'create'` | 对话框模式 |
| `form.id` | Number/null | `null` | 编辑时的分组ID |
| `form.group_name` | String | `''` | 分组名称 |

---

### 5. 常量配置
```javascript
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'
const getToken = () => localStorage.getItem('token')
```

| 常量名 | 值 | 说明 |
|--------|-----|------|
| `API_BASE` | `'/api'` | API基础路径 (支持环境变量) |
| `getToken` | Function | 获取认证Token的函数 |

---

### 6. 方法函数

#### 6.1 fetchGroups() - 获取分组列表
```javascript
const fetchGroups = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/watchlist/groups`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    groups.value = response.data

    // 自动选中第一个分组
    if (!props.modelValue && groups.value.length > 0) {
      selectGroup(groups.value[0])
    }
  } catch (error) {
    ElMessage.error('获取分组失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}
```
- **API端点**: `GET /api/watchlist/groups`
- **认证**: Bearer Token
- **自动选中**: 首次加载时选中第一个分组

#### 6.2 selectGroup(group) - 选择分组
```javascript
const selectGroup = (group) => {
  emit('update:modelValue', group.id)
  emit('group-selected', group)
}
```
- **触发事件**: `update:modelValue`, `group-selected`
- **参数**: 分组对象

#### 6.3 showCreateDialog() - 显示创建对话框
```javascript
const showCreateDialog = () => {
  dialogMode.value = 'create'
  form.value = { id: null, group_name: '' }
  dialogVisible.value = true
}
```
- **重置表单**: 清空ID和名称
- **设置模式**: `'create'`

#### 6.4 showEditDialog(group) - 显示编辑对话框
```javascript
const showEditDialog = (group) => {
  dialogMode.value = 'edit'
  form.value = { id: group.id, group_name: group.group_name }
  dialogVisible.value = true
}
```
- **填充表单**: 使用现有分组数据
- **设置模式**: `'edit'`

#### 6.5 submitForm() - 提交表单
```javascript
const submitForm = async () => {
  if (!form.value.group_name?.trim()) {
    ElMessage.warning('请输入分组名称')
    return
  }

  try {
    if (dialogMode.value === 'create') {
      // POST /api/watchlist/groups
      const response = await axios.post(...)
      emit('group-created', response.data.group)
    } else {
      // PUT /api/watchlist/groups/{id}
      await axios.put(...)
      emit('group-updated', form.value)
    }

    dialogVisible.value = false
    await fetchGroups()
  } catch (error) {
    ElMessage.error('操作失败: ' + ...)
  }
}
```
- **创建API**: `POST /api/watchlist/groups`
- **更新API**: `PUT /api/watchlist/groups/{id}`
- **表单验证**: 检查名称是否为空
- **成功后**: 关闭对话框、刷新列表

#### 6.6 confirmDelete(group) - 确认删除
```javascript
const confirmDelete = async (group) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分组 "${group.group_name}" 吗？该分组下的所有股票也会被删除。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteGroup(group)
  } catch (error) {
    // 用户取消
  }
}
```
- **确认对话框**: ElMessageBox警告类型
- **提示信息**: 包含分组名称和后果说明

#### 6.7 deleteGroup(group) - 删除分组
```javascript
const deleteGroup = async (group) => {
  try {
    await axios.delete(`${API_BASE}/watchlist/groups/${group.id}`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    ElMessage.success('分组删除成功')
    emit('group-deleted', group)

    // 切换到其他分组
    if (props.modelValue === group.id && groups.value.length > 1) {
      const firstGroup = groups.value.find(g => g.id !== group.id)
      if (firstGroup) selectGroup(firstGroup)
    }

    await fetchGroups()
  } catch (error) {
    ElMessage.error('删除失败: ' + ...)
  }
}
```
- **API端点**: `DELETE /api/watchlist/groups/{id}`
- **智能切换**: 删除当前选中分组时自动切换到其他分组

---

### 7. 生命周期钩子
```javascript
onMounted(() => {
  fetchGroups()
})
```
- **挂载时**: 自动获取分组列表

---

### 8. 暴露方法
```javascript
defineExpose({
  fetchGroups
})
```
- **暴露给父组件**: `fetchGroups` 方法可被父组件调用

---

## 🎨 样式元素 (Style Elements)

### CSS类列表

| 类名 | 选择器 | 说明 |
|------|--------|------|
| `.watchlist-group-manager` | 根容器 | 高度100%、flex布局 |
| `.group-header` | 头部容器 | flex布局、底部边框 |
| `.group-list` | 列表容器 | padding: 10px |
| `.group-item` | 分组项 | flex布局、边框、圆角、hover效果 |
| `.group-item.active` | 激活的分组项 | 蓝色背景、蓝色边框 |
| `.group-info` | 分组信息区 | flex布局、gap: 10px |
| `.group-name` | 分组名称 | 字体粗细500、颜色#333 |
| `.group-actions` | 操作按钮区 | 默认透明、hover显示 |

### 关键样式特性

1. **悬停效果**
```css
.group-item:hover {
  background: #f5f7fa;
  border-color: #409eff;
}

.group-item:hover .group-actions {
  opacity: 1;  /* 显示操作按钮 */
}
```

2. **激活状态**
```css
.group-item.active {
  background: #ecf5ff;
  border-color: #409eff;
}

.group-item.active .group-name {
  color: #409eff;
}
```

3. **过渡动画**
```css
.group-item {
  transition: all 0.3s;
}

.group-actions {
  transition: opacity 0.3s;
}
```

---

## 📊 数据流图

```
┌─────────────────────────────────────────────┐
│          组件挂载 (onMounted)               │
└──────────────┬──────────────────────────────┘
               │
               ▼
         fetchGroups()
               │
               ▼
      ┌────────────────┐
      │  API请求       │
      │  GET /groups   │
      └────────┬───────┘
               │
               ▼
      ┌────────────────┐
      │ groups.value   │
      │ 更新分组列表    │
      └────────┬───────┘
               │
               ▼
      ┌────────────────┐
      │  模板渲染      │
      │  v-for循环     │
      └────────────────┘

用户交互流程:
1. 点击"新建分组" → showCreateDialog() → 显示对话框
2. 填写表单 → submitForm() → POST /groups → 刷新列表
3. 点击分组 → selectGroup() → emit事件 → 父组件响应
4. 点击"编辑" → showEditDialog() → 显示对话框
5. 点击"删除" → confirmDelete() → deleteGroup() → DELETE /groups/{id}
```

---

## 🔗 API端点清单

| 方法 | 端点 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/watchlist/groups` | 获取分组列表 | Bearer Token |
| POST | `/api/watchlist/groups` | 创建新分组 | Bearer Token |
| PUT | `/api/watchlist/groups/{id}` | 更新分组 | Bearer Token |
| DELETE | `/api/watchlist/groups/{id}` | 删除分组 | Bearer Token |

---

## 📝 组件特性总结

### ✅ 功能特性
- ✅ 分组CRUD操作完整
- ✅ 实时加载状态反馈
- ✅ 智能分组选中逻辑
- ✅ 删除二次确认机制
- ✅ 默认分组保护（不可编辑/删除）
- ✅ 操作按钮智能显示（hover时显示）
- ✅ 表单验证（非空检查）
- ✅ 错误处理和用户提示

### 🎨 UI/UX特性
- 悬停高亮效果
- 激活状态样式
- 平滑过渡动画
- 操作按钮渐显
- 滚动容器（500px高度）
- 响应式布局

### 🔧 技术特性
- Vue 3 Composition API
- v-model双向绑定支持
- 事件emit机制
- defineExpose暴露方法
- Element Plus组件集成
- Axios HTTP请求
- LocalStorage认证

---

生成工具: Claude Code
分析日期: 2025-11-08
