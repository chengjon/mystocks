# Vue 3 + TypeScript 开发规范与最佳实践

**版本**: v1.0
**最后更新**: 2026-01-12
**目标**: 避免类型错误，提高代码质量，实现零错误质量门禁

---

## 📋 目录

1. [问题分析](#问题分析)
2. [核心理念](#核心理念)
3. [开发前准备](#开发前准备)
4. [编码规范](#编码规范)
5. [标准模板](#标准模板)
6. [工作流程](#工作流程)
7. [团队规范](#团队规范)
8. [常见陷阱](#常见陷阱)
9. [检查清单](#检查清单)

---

## 问题分析

### 我们遇到的40个错误

**根本原因**: Vue 3 Composition API 的 `ref(null)` 和 `ref([])` 会被 TypeScript 推断为 `never` 类型，导致所有属性访问都报错。

```typescript
// ❌ 错误写法
const selected = ref(null)        // Ref<never>
const items = ref([])            // Ref<never[]>

// 模板中访问属性
{{ selected.name }}  // ❌ Property 'name' does not exist on type 'never'
```

**修复成本**: 40个错误 × 平均10分钟 = 6.6小时
**预防成本**: 每个组件多花2分钟定义接口 = 几乎零额外时间

---

## 核心理念

### 🎯 三大原则

1. **接口优先** - 总是先定义接口，再声明变量
2. **显式类型** - 永远不依赖 TypeScript 的类型推断
3. **实时反馈** - 开发时立即看到类型错误

### 💡 开发哲学

> "先想清楚数据结构，再写代码。定义接口的时间永远比修复错误的时间短。"

---

## 开发前准备

### IDE 配置

**VSCode 设置** (`.vscode/settings.json`)

```json
{
  // TypeScript 严格检查
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.tsserver.watchOptions": {
    "excludeDirectories": ["**/node_modules", "**/.git"]
  },

  // 实时类型反馈
  "typescript.preferences.includePackageJsonAutoImports": "auto",
  "editor.semanticHighlighting.enabled": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.ts": "explicit"
  },

  // Vue 支持
  "vue.server.hybridMode": true,
  "volar.autoCompleteRefs": true,
  "vue.inlayHints.missingProps": true,

  // 实时检查
  "typescript.tsserver.enablePromptUsedLibraryThreshold": 5
}
```

### VSCode 插件（必装）

```bash
code --install-extension Vue.volar
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
```

### TypeScript 严格模式

**tsconfig.json**

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

---

## 编码规范

### 规范 1: 接口定义优先

**❌ 反模式**

```typescript
<script setup lang="ts">
// 直接使用，没有定义类型
const users = ref([])
const selected = ref(null)
const loading = ref(false)

// 业务逻辑
const fetchUsers = async () => {
  // ...
}
</script>
```

**✅ 正确模式**

```typescript
<script setup lang="ts">
// ========================================
// 1️⃣ 类型定义区 - 总是放在最前面
// ========================================

interface User {
  id: string
  name: string
  email: string
  role: 'admin' | 'user'
}

// ========================================
// 2️⃣ 响应式变量声明（带类型参数）
// ========================================

const users = ref<User[]>([])
const selected = ref<User | null>(null)
const loading = ref<boolean>(false)

// ========================================
// 3️⃣ 业务逻辑
// ========================================

const fetchUsers = async (): Promise<void> => {
  loading.value = true
  try {
    // ...
  } finally {
    loading.value = false
  }
}
</script>
```

### 规范 2: ref() 类型参数规则

**规则**: 所有 `ref()` 调用必须显式指定类型参数

```typescript
// ✅ 单个可选值
const selected = ref<User | null>(null)

// ✅ 数组（必须指定元素类型）
const items = ref<Item[]>([])

// ✅ 基础类型可以省略（类型明显）
const loading = ref(false)
const count = ref(0)
const message = ref('')

// ❌ 以下写法禁止
const items = ref([])           // 类型推断失败
const selected = ref(null)      // 类型推断失败
```

### 规范 3: reactive() 类型标注

```typescript
// ✅ 推荐：显式标注复杂对象
interface FormData {
  name: string
  email: string
  age: number
}

const form = reactive<FormData>({
  name: '',
  email: '',
  age: 0
})

// ✅ 简单对象可以省略（会自动推断）
const simple = reactive({
  count: 0,
  name: ''
})
```

### 规范 4: 函数类型标注

```typescript
// ✅ 所有函数都标注参数和返回值类型
const getUser = (id: string): User => {
  return users.value.find(u => u.id === id)!
}

const updateUser = async (id: string, data: Partial<User>): Promise<void> => {
  await api.update(id, data)
}

const formatName = (first: string, last: string): string => {
  return `${first} ${last}`
}

// ✅ 箭头函数（回调）也要标注
items.value.filter((item: Item) => item.active)
```

---

## 标准模板

### 模板 1: 基础列表组件

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'

// ============================================================
// 类型定义
// ============================================================

interface Item {
  id: string
  name: string
  description: string
}

interface ApiResponse {
  data: Item[]
  success: boolean
}

// ============================================================
// 响应式状态
// ============================================================

const items = ref<Item[]>([])
const loading = ref<boolean>(false)
const error = ref<string | null>(null)

// ============================================================
// 方法
// ============================================================

const fetchItems = async (): Promise<void> => {
  loading.value = true
  error.value = null

  try {
    const response = await api.get<ApiResponse>('/items')
    items.value = response.data
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unknown error'
  } finally {
    loading.value = false
  }
}

const selectItem = (item: Item): void => {
  console.log('Selected:', item.name)
}

// ============================================================
// 生命周期
// ============================================================

onMounted(() => {
  fetchItems()
})
</script>

<template>
  <div v-loading="loading">
    <div v-for="item in items" :key="item.id" @click="selectItem(item)">
      {{ item.name }}
    </div>
    <div v-if="error" class="error">
      {{ error }}
    </div>
  </div>
</template>
```

### 模板 2: 表单组件

```vue
<script setup lang="ts">
import { reactive, ref } from 'vue'

// ============================================================
// 类型定义
// ============================================================

interface FormData {
  username: string
  email: string
  age: number
  role: 'admin' | 'user' | 'guest'
  subscribe: boolean
}

interface FormRules {
  username: { required: boolean; message: string }
  email: { required: boolean; type: string; message: string }
}

// ============================================================
// 响应式状态
// ============================================================

const form = reactive<FormData>({
  username: '',
  email: '',
  age: 0,
  role: 'user',
  subscribe: false
})

const rules: FormRules = {
  username: { required: true, message: 'Username is required' },
  email: { required: true, type: 'email', message: 'Invalid email' }
}

const submitting = ref<boolean>(false)

// ============================================================
// 方法
// ============================================================

const validate = (): boolean => {
  // 简单验证逻辑
  return form.username.length > 0 && form.email.includes('@')
}

const submit = async (): Promise<void> => {
  if (!validate()) {
    return
  }

  submitting.value = true
  try {
    await api.submit('/users', form)
    // 成功处理
  } finally {
    submitting.value = false
  }
}

const reset = (): void => {
  Object.assign(form, {
    username: '',
    email: '',
    age: 0,
    role: 'user',
    subscribe: false
  })
}
</script>

<template>
  <form @submit.prevent="submit">
    <input v-model="form.username" type="text" />
    <input v-model="form.email" type="email" />
    <input v-model.number="form.age" type="number" />
    <button type="submit" :disabled="submitting">
      {{ submitting ? 'Submitting...' : 'Submit' }}
    </button>
  </form>
</template>
```

### 模板 3: 详情/编辑组件

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

// ============================================================
// 类型定义
// ============================================================

interface User {
  id: string
  name: string
  email: string
  department: string
  status: 'active' | 'inactive'
}

interface ApiResponse {
  data: User
  success: boolean
}

// ============================================================
// 状态
// ============================================================

const route = useRoute()
const userId = computed(() => route.params.id as string)

const user = ref<User | null>(null)
const loading = ref<boolean>(false)
const editing = ref<boolean>(false)

// ============================================================
// Computed
// ============================================================

const canEdit = computed(() => {
  return user.value?.status === 'active'
})

// ============================================================
// 方法
// ============================================================

const fetchUser = async (id: string): Promise<void> => {
  loading.value = true
  try {
    const response = await api.get<ApiResponse>(`/users/${id}`)
    user.value = response.data
  } finally {
    loading.value = false
  }
}

const saveUser = async (): Promise<void> => {
  if (!user.value) return

  loading.value = true
  try {
    await api.put(`/users/${user.value.id}`, user.value)
    editing.value = false
  } finally {
    loading.value = false
  }
}

// ============================================================
// 生命周期
// ============================================================

// 监听路由参数变化
watch(() => userId.value, (newId) => {
  if (newId) {
    fetchUser(newId)
  }
}, { immediate: true })
</script>

<template>
  <div v-loading="loading">
    <div v-if="user">
      <h1>{{ user.name }}</h1>
      <p>{{ user.email }}</p>
      <p>Department: {{ user.department }}</p>
      <button @click="editing = true" :disabled="!canEdit">
        Edit
      </button>
    </div>
  </div>
</template>
```

---

## 工作流程

### 开发时工作流

#### 步骤 1: 启动项目

```bash
# Terminal 1: 开发服务器
npm run dev

# Terminal 2: 实时类型检查（必需！）
npx vue-tsc --noEmit --watch
```

**为什么需要两个终端？**
- `npm run dev` - Vite 的快速类型检查（可能遗漏某些错误）
- `vue-tsc --noEmit --watch` - 完整的 TypeScript 类型检查（实时监听）

#### 步骤 2: 创建新组件

```
1. 复制对应的模板（模板1/2/3）
2. 修改类型定义区（根据实际需求）
3. 实现业务逻辑
4. 查看 Terminal 2 的类型检查结果
5. 修复所有类型错误后继续
```

#### 步骤 3: 提交代码

```bash
# Pre-commit hook 会自动运行类型检查
git add .
git commit -m "feat: add user component"

# 如果类型检查失败，commit 会被阻止
# 修复所有错误后重新提交
```

### 实时反馈循环

```
写代码 → 保存文件 →
vue-tsc 立即检查（Terminal 2） →
发现类型错误 →
立即修复 →
继续开发
```

**好处**:
- 问题秒级发现（不是小时级）
- 避免错误累积
- 保持代码质量

---

## 团队规范

### Git Pre-commit Hook

**安装 Husky**

```bash
npm install -D husky
npx husky install
npm run prepare
```

**配置 Pre-commit Hook**

```bash
# .husky/pre-commit
#!/bin/bash
echo "🔍 Running type check..."

npx vue-tsc --noEmit

if [ $? -ne 0 ]; then
  echo ""
  echo "❌ TypeScript errors found!"
  echo "📝 Please fix the following errors before committing:"
  echo ""
  npx vue-tsc --noEmit
  echo ""
  echo "💡 Tip: Keep 'npx vue-tsc --noEmit --watch' running for real-time feedback"
  exit 1
fi

echo "✅ Type check passed"
```

**添加可执行权限**

```bash
chmod +x .husky/pre-commit
```

### PR Review 检查清单

**代码审查时必须检查**:

```markdown
## TypeScript 类型检查清单

### ref() 使用 ✅
- [ ] 所有 `ref(null)` 都有类型参数：`ref<Type | null>(null)`
- [ ] 所有 `ref([])` 都有类型参数：`ref<Type[]>([])`
- [ ] 没有使用 `ref()` 而不指定类型参数

### 类型定义 ✅
- [ ] 接口定义放在文件顶部（容易查找）
- [ ] 接口命名清晰（使用 PascalCase）
- [ ] 避免使用 `any` 类型（除非有充分理由并注释）
- [ ] 复杂对象都有对应的 interface 定义

### 函数类型 ✅
- [ ] 所有函数参数都有类型标注
- [ ] 所有函数返回值都有类型标注
- [ ] async 函数返回 `Promise<Type>`
- [ ] 回调函数参数有类型标注

### 代码组织 ✅
- [ ] 类型定义区在最前面
- [ ] 响应式变量声明区清晰
- [ ] 方法和生命周期区分离
- [ ] 遵循组件模板结构

### 类型检查 ✅
- [ ] 本地运行 `npx vue-tsc --noEmit` 无错误
- [ ] Pre-commit hook 通过
- [ ] 没有 TypeScript 编译警告
```

### 团队培训要点

**新成员入职培训**:

1. **30分钟类型安全培训**
   - Vue 3 + TypeScript 类型推断机制
   - 常见错误和修复方法
   - 实时类型检查工具使用

2. **提供快速参考卡**
   - 打印本文档的"常见陷阱"章节
   - 贴在工位上随时查阅

3. **Code Review 示范**
   - 每次PR都检查类型定义
   - 不符合规范的代码要求修改

---

## 常见陷阱

### 陷阱 1: 忘记类型参数

**症状**: `Property 'xxx' does not exist on type 'never'`

```typescript
// ❌ 错误
const items = ref([])

// ✅ 正确
interface Item { id: string }
const items = ref<Item[]>([])
```

### 陷阱 2: reactive() 的类型推断

```typescript
// ❌ 可能有问题
const form = reactive({
  name: '',
  count: 0
})
// TypeScript 可能推断出错误的类型

// ✅ 显式标注
interface Form {
  name: string
  count: number
}

const form = reactive<Form>({
  name: '',
  count: 0
})
```

### 陷阱 3: computed 推断失败

```typescript
// ❌ 不推荐
const items = computed(() => {
  return ref([])  // 返回 Ref<never[]>
})

// ✅ 正确
interface Item { id: string }
const items = ref<Item[]>([])
// 或者
const items = computed(() => {
  return [] as Item[]
})
```

### 陷阱 4: DOM 事件类型

```typescript
// ❌ 类型错误
const handleClick = (event) => {
  console.log(event.target.value)  // event 是 any
}

// ✅ 正确
const handleClick = (event: Event) => {
  const target = event.target as HTMLInputElement
  console.log(target.value)
}
```

### 陷阱 5: Props 类型定义

```typescript
// ❌ 运行时定义（无类型检查）
const props = defineProps({
  modelValue: String,
  disabled: Boolean
})

// ✅ 编译时定义（完整类型检查）
interface Props {
  modelValue: string
  disabled?: boolean
}

const props = defineProps<Props>()
```

### 陷阱 6: emit 类型定义

```typescript
// ❌ 无类型检查
const emit = defineEmits(['update', 'delete'])

// ✅ 完整类型检查
const emit = defineEmits<{
  update: [value: string]
  delete: [id: string]
}>()
```

### 陷阱 7: provide/inject 类型

```typescript
// ❌ 无类型
provide('theme', 'dark')
const theme = inject('theme')

// ✅ 使用 InjectionKey
import { InjectionKey } from 'vue'

const THEME_KEY = Symbol('theme') as InjectionKey<string>

provide(THEME_KEY, 'dark')
const theme = inject(THEME_KEY)
```

---

## 检查清单

### 开发前检查 ✅

- [ ] VSCode 已安装 Volar 插件
- [ ] 已打开 `vue-tsc --noEmit --watch`
- [ ] `tsconfig.json` 开启 `strict: true`
- [ ] Pre-commit hook 已配置

### 编码时检查 ✅

- [ ] 类型定义放在文件最前面
- [ ] 所有 `ref()` 都有类型参数
- [ ] 所有函数参数都有类型
- [ ] 所有函数返回值都有类型
- [ ] 没有使用 `any` 类型（除非必要并注释）

### 提交前检查 ✅

- [ ] `npx vue-tsc --noEmit` 零错误
- [ ] Pre-commit hook 通过
- [ ] ESLint 检查通过（如果配置）
- [ ] 代码符合团队规范

### PR Review 检查 ✅

- [ ] 所有新增的 `ref()` 都有类型参数
- [ ] 所有接口定义清晰合理
- [ ] 没有 `@ts-ignore` 或 `@ts-expect-error`（除非必要）
- [ ] 复杂逻辑有类型注释
- [ ] 遵循组件标准模板

---

## 快速参考

### Vue 3 + TypeScript 常用模式

```typescript
// ========================================
// ref() 模式
// ========================================

// 单个值（可选）
const value = ref<string | null>(null)

// 数组
const items = ref<Item[]>([])

// 基础类型（可省略）
const count = ref(0)
const loading = ref(false)

// ========================================
// reactive() 模式
// ========================================

// 显式标注（推荐）
interface User {
  name: string
  age: number
}
const user = reactive<User>({ ... })

// 简单对象（可省略）
const simple = reactive({ count: 0 })

// ========================================
// computed() 模式
// ========================================

// getter
const double = computed(() => count.value * 2)

// getter + setter
const value = computed({
  get: () => count.value * 2,
  set: (val: number) => { count.value = val / 2 }
})

// ========================================
// 函数模式
// ========================================

// 普通函数
const add = (a: number, b: number): number => a + b

// async 函数
const fetch = async (): Promise<void> => {
  // ...
}

// 回调函数
items.filter((item: Item) => item.active)

// ========================================
// 组件 API 模式
// ========================================

// Props
interface Props {
  modelValue: string
  disabled?: boolean
}
const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  update: [value: string]
}>()

//Expose
defineExpose({
  refresh,
  validate
})
```

---

## 工具和资源

### VSCode 扩展

```bash
# 必装
code --install-extension Vue.volar

# 推荐
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension Editorial.Calendar
```

### 命令行工具

```bash
# 类型检查
npx vue-tsc --noEmit

# 实时监听
npx vue-tsc --noEmit --watch

# 单文件检查
npx vue-tsc --noEmit src/components/MyComponent.vue
```

### 参考文档

- [Vue 3 TypeScript 支持](https://vuejs.org/guide/typescript/overview)
- [Composition API FAQ](https://vuejs.org/guide/extras/composition-api-faq.html)
- [TypeScript 手册](https://www.typescriptlang.org/docs/handbook/intro.html)

---

## 附录：错误类型速查表

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `Property 'xxx' does not exist on type 'never'` | `ref(null)` 没有类型参数 | 改为 `ref<Type \| null>(null)` |
| `Element implicitly has an 'any' type` | 数组项没有类型标注 | 改为 `ref<Item[]>([])`，或 `filter((item: Item) => ...)` |
| `Parameter 'xxx' implicitly has an 'any' type` | 函数参数没有类型 | 添加参数类型：`(item: Item) => ...` |
| `Type 'X' is not assignable to type 'Y'` | 类型不匹配 | 检查接口定义，确保类型一致 |

---

## 版本历史

- **v1.0** (2026-01-12) - 初始版本，基于40个类型错误的修复经验

---

## 贡献指南

如果你有改进建议或发现了新的模式，请更新本文档，确保团队知识持续积累。

**记住**: "预防胜于治疗" - 按照本文档的规范开发，可以避免绝大多数常见的 TypeScript 类型错误。
