# Vue 3 + Element Plus 快速参考手册

## 一、组件不显示 - 快速诊断（3分钟）

```bash
# 1. 硬刷新浏览器
Windows/Linux: Ctrl + Shift + R
Mac: Cmd + Shift + R

# 2. 检查构建
npm run build 2>&1 | grep -i error

# 3. 如果有错误，90%是这三类：
```

### 错误类型速查

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `"XXX" is not exported` | 导入的内容不存在 | 检查导入名称是否正确 |
| `Cannot find module` | 文件路径错误 | 检查路径拼写和文件是否存在 |
| `Unexpected token` | 语法错误 | 检查括号、引号、分号是否匹配 |

## 二、Element Plus 图标速查

### 常用图标对照表

```javascript
// ✅ 存在的图标
Search      // 搜索
Edit        // 编辑
Delete      // 删除
Plus        // 加号
Minus       // 减号
Refresh     // 刷新
Download    // 下载
Upload      // 上传
View        // 查看
Clock       // 时钟/历史  ⚠️ 注意：不是History！
Timer       // 计时器
Calendar    // 日历
Setting     // 设置
User        // 用户
Document    // 文档
Folder      // 文件夹
```

### 图标使用模板

```vue
<template>
  <el-icon><Search /></el-icon>
</template>

<script setup>
import { Search } from '@element-plus/icons-vue'
</script>
```

## 三、API配置模板

```javascript
// src/config/api.js
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const API_ENDPOINTS = {
  yourModule: {
    list: `${API_BASE_URL}/api/your-module/list`,
    create: `${API_BASE_URL}/api/your-module/create`,
    detail: (id) => `${API_BASE_URL}/api/your-module/${id}`,
  }
}
```

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000

# .env.production
VITE_API_BASE_URL=https://api.yourdomain.com
```

## 四、常见问题一键解决

### 问题1: 点击菜单没反应

**诊断**:
```javascript
// 在handleMenuSelect中添加日志
const handleMenuSelect = (index) => {
  console.log('Menu clicked:', index)  // 如果打印了，说明菜单工作
  router.push(index)
}
```

**解决**:
```vue
<!-- 确保menu配置正确 -->
<el-menu :router="false" @select="handleMenuSelect">
  <el-menu-item index="/your-path">菜单项</el-menu-item>
</el-menu>
```

### 问题2: 页面空白，Console无错误

**可能原因**: 浏览器缓存

**解决**: `Ctrl + Shift + R` (硬刷新)

### 问题3: API请求404

**诊断**:
```javascript
// 检查URL
console.log('API URL:', API_ENDPOINTS.yourModule.list)

// 测试后端
curl http://localhost:8000/api/your-module/list
```

**解决**:
- 检查后端服务是否启动
- 检查API路径拼写
- 检查CORS配置

### 问题4: 组件报错 "is not exported"

**快速修复**:
```bash
# 1. 找到错误的导入
grep -n "from '@element-plus/icons-vue'" src/components/YourComponent.vue

# 2. 检查图标是否存在
grep "export.*YourIcon" node_modules/@element-plus/icons-vue/dist/index.js

# 3. 如果不存在，替换为存在的图标（参考上面的常用图标表）
```

## 五、Vue 3 组件标准模板

```vue
<template>
  <div class="your-component">
    <!-- 头部 -->
    <el-card class="header">
      <template #header>
        <span>标题</span>
      </template>
      <p>描述</p>
    </el-card>

    <!-- 主体内容 -->
    <div v-loading="loading">
      <el-empty v-if="items.length === 0" description="暂无数据" />
      <div v-else>
        <!-- 数据展示 -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { API_ENDPOINTS } from '@/config/api'

// 状态
const loading = ref(false)
const items = ref([])

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const response = await fetch(API_ENDPOINTS.yourModule.list)
    if (!response.ok) throw new Error('加载失败')

    const data = await response.json()
    items.value = data.items || []

    ElMessage.success('加载成功')
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.your-component {
  padding: 20px;
}
</style>
```

## 六、调试命令速查

```bash
# 前端相关
npm run dev              # 启动开发服务器
npm run build           # 构建生产版本
npm run preview         # 预览构建结果

# 检查语法
npm run lint            # 运行linter

# 依赖管理
npm install             # 安装依赖
npm list @element-plus/icons-vue  # 检查特定包版本

# 服务检查
ps aux | grep vite      # 检查前端服务
lsof -i :3001          # 检查3001端口占用
```

## 七、浏览器开发者工具速查

```bash
F12                     # 打开开发者工具
Ctrl + Shift + R       # 硬刷新（清除缓存）
Ctrl + Shift + C       # 元素选择器

# Console标签
console.log(data)      # 查看数据
console.error(error)   # 查看错误
console.table(array)   # 表格显示数组

# Network标签
- 查看所有网络请求
- 检查API状态码
- 查看请求/响应数据

# Vue Devtools
- Components: 查看组件树
- Router: 查看路由状态
- Pinia/Vuex: 查看状态管理
```

## 八、Element Plus 常用组件速查

```vue
<!-- 按钮 -->
<el-button type="primary" @click="handleClick">按钮</el-button>

<!-- 消息提示 -->
<script>
ElMessage.success('成功')
ElMessage.error('失败')
ElMessage.warning('警告')
</script>

<!-- 加载状态 -->
<div v-loading="loading">内容</div>

<!-- 空状态 -->
<el-empty description="暂无数据" />

<!-- 表格 -->
<el-table :data="tableData" border stripe>
  <el-table-column prop="name" label="名称" />
  <el-table-column prop="value" label="值" />
</el-table>

<!-- 对话框 -->
<el-dialog v-model="visible" title="标题">
  <p>内容</p>
  <template #footer>
    <el-button @click="visible = false">取消</el-button>
    <el-button type="primary" @click="confirm">确定</el-button>
  </template>
</el-dialog>

<!-- 分页 -->
<el-pagination
  v-model:current-page="currentPage"
  v-model:page-size="pageSize"
  :total="total"
  layout="total, sizes, prev, pager, next"
/>
```

## 九、错误排查优先级

```
1. 先看构建错误（npm run build）
   ↓
2. 再看浏览器Console红色错误
   ↓
3. 然后看Network请求失败
   ↓
4. 最后检查业务逻辑
```

## 十、救命命令（遇到问题先试这些）

```bash
# 1. 清除所有缓存，重新安装
rm -rf node_modules package-lock.json
npm install

# 2. 重启开发服务器
Ctrl + C
npm run dev

# 3. 硬刷新浏览器
Ctrl + Shift + R

# 4. 检查服务是否正常
curl http://localhost:3001        # 前端
curl http://localhost:8000/docs   # 后端

# 5. 查看日志
tail -f /tmp/frontend.log         # 前端日志
tail -f /tmp/backend.log          # 后端日志
```

---

## 本次问财筛选问题总结

**问题**: 组件不显示
**原因**: 导入了不存在的 `History` 图标
**解决**: 替换为 `Clock` 图标
**教训**:
1. 先运行 `npm run build` 检查编译错误
2. Element Plus 图标要查文档，不要猜名字
3. 浏览器Console的错误要分优先级，不是所有红色都重要

**快速验证图标是否存在**:
```bash
grep "export.*IconName" node_modules/@element-plus/icons-vue/dist/index.js
```

如果返回结果 → ✅ 图标存在
如果无返回 → ❌ 图标不存在，需要换一个

---

**提示**: 将这个文件加入书签，遇到问题时快速查找！
