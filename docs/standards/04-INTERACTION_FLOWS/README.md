# 交互流程

> **补充规范说明**:
> 本文件是项目补充标准、执行细则或专题规范，不是仓库共享规则的唯一事实来源。
> 仓库级共享规则总入口仍以 `architecture/STANDARDS.md` 为准；执行流程、命令与协作约束再参考根目录 `AGENTS.md`。本文件用于补充某一专题的执行细则、约束或参考模板。
>
> 若本文件与 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 或当前已批准执行口径不一致，应优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 与当前实现；若无冲突，则按本文件的专题范围执行。


**版本**: v1.0.0
**最后更新**: 2025-12-25
**上级文档**: [UI_DESIGN_SYSTEM.md](../UI_DESIGN_SYSTEM.md)

---

## 📋 目录

- [交互原则](#交互原则)
- [核心流程](#核心流程)
- [页面跳转](#页面跳转)
- [操作反馈](#操作反馈)
- [错误处理](#错误处理)
- [键盘导航](#键盘导航)

---

## 交互原则

MyStocks 的交互设计遵循以下原则：

### 1. 预防优于治疗

- **提前验证**: 在用户提交前验证输入
- **清晰提示**: 明确告知用户要求
- **默认值**: 提供合理的默认值
- **撤销操作**: 允许用户撤销操作

### 2. 即时反馈

- **加载状态**: 显示加载进度
- **成功提示**: 操作成功后立即反馈
- **错误提示**: 清晰说明错误原因
- **操作确认**: 危险操作需要二次确认

### 3. 简化流程

- **减少步骤**: 最多3步完成操作
- **智能默认**: 记住用户选择
- **批量操作**: 支持批量处理
- **快捷键**: 提供键盘快捷方式

### 4. 一致性

- **统一模式**: 相似操作使用相同模式
- **术语一致**: 使用统一的术语
- **位置一致**: 按钮位置保持一致
- **样式一致**: 相同功能使用相同样式

---

## 核心流程

### 1. 用户登录流程

```
开始
  ↓
访问系统
  ↓
未登录? ──Yes──→ 跳转到登录页
  ↓No                  ↓
显示页面          输入账号密码
                      ↓
                  点击登录
                      ↓
                  验证中...
                      ↓
              ┌───────┴───────┐
              ↓               ↓
          验证成功          验证失败
              ↓               ↓
          跳转首页        显示错误
          显示欢迎        重新输入
              ↓               ↓
          进入系统          (循环)
```

**代码示例**:
```vue
<template>
  <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
    <el-form-item prop="username">
      <el-input v-model="form.username" placeholder="用户名" />
    </el-form-item>
    <el-form-item prop="password">
      <el-input v-model="form.password" type="password" placeholder="密码" />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" native-type="submit" :loading="loading">
        登录
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
  ],
}

const handleLogin = async () => {
  loading.value = true
  try {
    await login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>
```

---

### 2. 股票搜索流程

```
开始
  ↓
输入关键词
  ↓
实时搜索
  ↓
显示搜索建议 (5条)
  ↓
用户选择?
  ↓Yes
跳转到股票详情页
  ↓
显示股票信息
  ↓
结束
```

**代码示例**:
```vue
<template>
  <el-autocomplete
    v-model="keyword"
    :fetch-suggestions="querySearch"
    placeholder="搜索股票代码/名称"
    @select="handleSelect"
    @keyup.enter="handleSearch"
  >
    <template #default="{ item }">
      <div class="stock-option">
        <span class="symbol">{{ item.symbol }}</span>
        <span class="name">{{ item.name }}</span>
      </div>
    </template>
  </el-autocomplete>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const keyword = ref('')

const querySearch = async (queryString: string, cb: any) => {
  if (!queryString) {
    cb([])
    return
  }

  const results = await searchStocks(queryString)
  cb(results.slice(0, 5)) // 只显示前5条
}

const handleSelect = (item: StockOption) => {
  router.push(`/stock/${item.symbol}`)
}

const handleSearch = () => {
  if (keyword.value) {
    router.push(`/search?q=${keyword.value}`)
  }
}
</script>
```

---

### 3. 下单交易流程

```
开始
  ↓
选择股票
  ↓
点击交易
  ↓
打开交易对话框
  ↓
输入交易信息
  - 方向 (买入/卖出)
  - 价格类型 (限价/市价)
  - 价格
  - 数量
  ↓
验证输入
  ↓
显示预估金额
  ↓
确认下单?
  │
  ├─ No → 关闭对话框
  │
  └─ Yes → 提交订单
            ↓
        订单处理中...
            ↓
        ┌─────┴─────┐
        ↓           ↓
    下单成功     下单失败
        ↓           ↓
    显示成功      显示错误
    关闭对话框   重新输入
        ↓
    结束
```

**代码示例**:
```vue
<template>
  <el-dialog v-model="visible" title="下单" width="500px" @close="handleClose">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="方向" prop="direction">
        <el-radio-group v-model="form.direction">
          <el-radio-button label="buy">买入</el-radio-button>
          <el-radio-button label="sell">卖出</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="价格类型" prop="priceType">
        <el-select v-model="form.priceType">
          <el-option label="限价" value="limit" />
          <el-option label="市价" value="market" />
        </el-select>
      </el-form-item>

      <el-form-item label="价格" prop="price" v-if="form.priceType === 'limit'">
        <el-input-number v-model="form.price" :precision="2" :step="0.01" />
      </el-form-item>

      <el-form-item label="数量" prop="quantity">
        <el-input-number v-model="form.quantity" :min="100" :step="100" />
      </el-form-item>

      <el-alert
        v-if="estimatedAmount"
        :title="`预估金额: ¥${estimatedAmount.toFixed(2)}`"
        type="info"
        :closable="false"
      />
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="loading">
        确认下单
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const visible = ref(false)
const loading = ref(false)

const form = reactive({
  direction: 'buy',
  priceType: 'limit',
  price: 0,
  quantity: 100,
})

const rules = {
  direction: [{ required: true }],
  priceType: [{ required: true }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
}

const estimatedAmount = computed(() => {
  if (form.priceType === 'market') return 0
  return form.price * form.quantity
})

const handleSubmit = async () => {
  // 验证表单
  const valid = await formRef.value?.validate()
  if (!valid) return

  // 二次确认
  try {
    await ElMessageBox.confirm(
      `确认${form.direction === 'buy' ? '买入' : '卖出'} ${form.quantity} 股?`,
      '确认下单',
      { type: 'warning' }
    )
  } catch {
    return
  }

  loading.value = true
  try {
    await placeOrder(form)
    ElMessage.success('下单成功')
    visible.value = false
  } catch (error) {
    ElMessage.error('下单失败')
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  visible.value = false
  // 重置表单
  form.direction = 'buy'
  form.priceType = 'limit'
  form.price = 0
  form.quantity = 100
}
</script>
```

---

### 4. 策略回测流程

```
开始
  ↓
选择策略
  ↓
配置参数
  - 股票代码
  - 时间范围
  - 初始资金
  - 策略参数
  ↓
验证配置
  ↓
开始回测?
  │
  ├─ No → 保存配置
  │
  └─ Yes → 执行回测
            ↓
        显示进度
            ↓
        回测完成
            ↓
        显示报告
        - 收益率
        - 最大回撤
        - 夏普比率
        - 交易明细
            ↓
        导出报告?
        保存配置?
            ↓
        结束
```

---

## 页面跳转

### 路由结构

```
/ (首页)
├── /dashboard (仪表盘)
├── /market (市场)
│   ├── /quotes (行情)
│   ├── /data (数据)
│   └── /:symbol (股票详情)
├── /analysis (分析)
│   ├── /indicators (技术指标)
│   └── /signals (交易信号)
├── /risk (风险)
│   ├── /overview (风险概览)
│   └── /stress-test (压力测试)
├── /strategy (策略)
│   ├── /list (策略列表)
│   ├── /backtest (回测)
│   └── /report/:id (回测报告)
└── /trade (交易)
    ├── /order (下单)
    ├── /position (持仓)
    └── /history (成交记录)
```

### 编程式导航

```typescript
import { useRouter } from 'vue-router'

const router = useRouter()

// 跳转到股票详情
router.push(`/stock/${symbol}`)

// 带查询参数
router.push({
  path: '/search',
  query: { q: keyword },
})

// 返回上一页
router.back()

// 替换当前路由 (不能返回)
router.replace('/dashboard')
```

---

## 操作反馈

### 1. 成功反馈

```vue
<script setup lang="ts">
import { ElMessage } from 'element-plus'

// 简单提示
ElMessage.success('操作成功')

// 带图标
ElMessage({
  message: '保存成功',
  type: 'success',
  icon: 'SuccessFilled',
})

// 可关闭
ElMessage({
  message: '操作成功',
  type: 'success',
  showClose: true,
  duration: 3000,
})
</script>
```

### 2. 错误反馈

```vue
<script setup lang="ts">
import { ElMessage, ElNotification } from 'element-plus'

// 消息提示
ElMessage.error('操作失败')

// 通知 (更适合详细错误)
ElNotification({
  title: '错误',
  message: '网络请求失败，请检查网络连接',
  type: 'error',
  duration: 0, // 不自动关闭
})
</script>
```

### 3. 确认对话框

```vue
<script setup lang="ts">
import { ElMessageBox } from 'element-plus'

// 简单确认
try {
  await ElMessageBox.confirm('确认删除?', '提示', {
    type: 'warning',
  })
  // 用户点击确认
} catch {
  // 用户点击取消
}

// 自定义按钮
try {
  await ElMessageBox.confirm(
    '此操作将永久删除文件, 是否继续?',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
} catch {
  // 取消
}
</script>
```

---

## 错误处理

### 网络错误

```typescript
// utils/request.ts
import { ElMessage } from 'element-plus'

export const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
})

// 响应拦截器
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 网络错误
    if (!error.response) {
      ElMessage.error('网络连接失败，请检查网络')
      return Promise.reject(error)
    }

    // HTTP 错误
    const { status, data } = error.response

    switch (status) {
      case 400:
        ElMessage.error(data.message || '请求参数错误')
        break
      case 401:
        ElMessage.error('未授权，请重新登录')
        // 跳转到登录页
        router.push('/login')
        break
      case 403:
        ElMessage.error('拒绝访问')
        break
      case 404:
        ElMessage.error('请求的资源不存在')
        break
      case 500:
        ElMessage.error('服务器错误')
        break
      default:
        ElMessage.error(`请求失败 (${status})`)
    }

    return Promise.reject(error)
  }
)
```

### 表单验证

```vue
<template>
  <el-form ref="formRef" :model="form" :rules="rules">
    <el-form-item label="股票代码" prop="symbol">
      <el-input v-model="form.symbol" placeholder="如: 600000" />
    </el-form-item>
    <el-form-item label="数量" prop="quantity">
      <el-input-number v-model="form.quantity" :min="100" :step="100" />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="handleSubmit">提交</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const formRef = ref()
const form = reactive({
  symbol: '',
  quantity: 100,
})

const rules = {
  symbol: [
    { required: true, message: '请输入股票代码', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '请输入6位数字代码', trigger: 'blur' },
  ],
  quantity: [
    { required: true, message: '请输入数量', trigger: 'blur' },
    { type: 'number', min: 100, message: '最少100股', trigger: 'blur' },
  ],
}

const handleSubmit = async () => {
  try {
    // 验证表单
    await formRef.value.validate()

    // 提交数据
    await submitForm(form)

  } catch (error) {
    console.log('表单验证失败', error)
  }
}
</script>
```

---

## 键盘导航

### 快捷键定义

| 快捷键 | 功能 | 位置 |
|-------|------|------|
| `Ctrl + K` | 打开搜索框 | 全局 |
| `Ctrl + /` | 快捷键帮助 | 全局 |
| `Esc` | 关闭对话框/模态框 | 全局 |
| `Enter` | 确认/提交 | 表单/对话框 |
| `↑ ↓` | 选择上一项/下一项 | 列表/下拉框 |
| `Page Up/Down` | 上一页/下一页 | 分页 |

### 快捷键实现

```vue
<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

const handleKeydown = (e: KeyboardEvent) => {
  // Ctrl + K: 打开搜索
  if (e.ctrlKey && e.key === 'k') {
    e.preventDefault()
    openSearch()
  }

  // Esc: 关闭对话框
  if (e.key === 'Escape') {
    closeDialog()
  }

  // Ctrl + /: 显示快捷键帮助
  if (e.ctrlKey && e.key === '/') {
    e.preventDefault()
    showShortcutHelp()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>
```

---

## ✅ 交互检查清单

在设计交互流程时，请确保：

- [ ] 提供清晰的操作反馈
- [ ] 处理所有错误情况
- [ ] 危险操作需要二次确认
- [ ] 支持键盘快捷键
- [ ] 加载状态明确显示
- [ ] 表单验证及时反馈
- [ ] 成功操作有明确提示
- [ ] 支持撤销重要操作
- [ ] 交互流程简洁高效
- [ ] 符合用户习惯

---

## 📚 相关资源

- [Element Plus 交互指南](https://element-plus.org/en-US/guide/design.html#interaction)
- [Nielsen Norman Group - 交互设计](https://www.nngroup.com/articles/interaction-design/)
- [Material Design 交互](https://material.io/design/interaction/)
- [WCAG 可访问性指南](https://www.w3.org/WAI/WCAG21/quickref/)

---

**文档版本**: v1.0.0
**最后更新**: 2025-12-25
**维护者**: UI Design Team
**位置**: `docs/standards/04-INTERACTION_FLOWS/README.md`
