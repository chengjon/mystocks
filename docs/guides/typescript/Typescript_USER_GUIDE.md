# TypeScript 用户手册

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**版本**: v1.0 | **更新时间**: 2026-01-20 | **适用人群**: 全体开发人员

> MyStocks项目TypeScript完整使用手册,从入门到精通的全方位指南。

---

## 📋 目录

1. [快速入门](#快速入门)
2. [日常开发工作流](#日常开发工作流)
3. [类型系统基础](#类型系统基础)
4. [Vue 3 + TypeScript开发](#vue-3--typescript开发)
5. [API集成与类型安全](#api集成与类型安全)
6. [测试与类型安全](#测试与类型安全)
7. [常见任务指南](#常见任务指南)
8. [团队协作规范](#团队协作规范)

---

## 🚀 快速入门

### 30分钟上手TypeScript

#### Step 1: 环境准备 (5分钟)

```bash
# 1. 确认Node.js版本
node --version  # 应该 >= v18

# 2. 安装依赖
cd web/frontend
npm install

# 3. 验证TypeScript版本
npm list typescript
```

#### Step 2: 运行类型检查 (5分钟)

```bash
# 快速类型检查(仅.ts文件)
npm run type-check

# 完整类型检查(包含.vue文件)
npm run type-check:vue

# 查看错误详情
npm run type-check 2>&1 | tee type-errors.txt
```

#### Step 3: 修复第一个错误 (10分钟)

**示例错误**:
```
error TS2532: Object is possibly 'undefined'
src/components/MyComponent.vue:25:3

The quick brown fox jumps over the lazy dog
The quick brown fox jumps over the lazy dog
```

**修复方法**:
```vue
<!-- ❌ 修复前 -->
<template>
  <div>{{ user.name }}</div>  <!-- user可能undefined -->
</template>

<!-- ✅ 修复后 -->
<template>
  <div>{{ user?.name || 'Guest' }}</div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface User {
  name: string
  email?: string
}

const user = ref<User | undefined>(undefined)
</script>
```

#### Step 4: 验证修复 (5分钟)

```bash
# 再次运行类型检查
npm run type-check

# 确认错误已修复
# ✅ No errors found

# 如果有其他错误,重复Step 3
```

#### Step 5: 提交代码 (5分钟)

```bash
# 运行完整检查
npm run lint
npm run type-check:vue

# 提交代码
git add .
git commit -m "fix: 修复TypeScript类型错误"
```

---

## 🔄 日常开发工作流

### 标准开发流程

```
┌──────────────────┐
│ 1. 创建分支      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 2. 开发功能      │
│ (编写TypeScript) │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 3. 类型检查      │
│ npm run type-check │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌────────┐
│ 有错误  │  │ 无错误  │
└───┬────┘  └────┬───┘
    │            │
    ▼            ▼
┌──────────┐  ┌──────────┐
│ 修复错误  │  │ 代码检查 │
│ (循环)    │  │ npm run lint│
└─────┬────┘  └────┬─────┘
      │            │
      └────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ 4. 提交代码   │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ 5. 创建PR    │
    └──────────────┘
```

### 开发前检查清单

**开始开发前**:
- [ ] 运行 `npm run type-check` 确认基线无错误
- [ ] 拉取最新代码: `git pull origin main`
- [ ] 切换到新分支: `git checkout -b feature/xxx`

**开发过程中**:
- [ ] 保存文件后自动运行类型检查(VS Code)
- [ ] 每30分钟运行一次完整检查: `npm run type-check:vue`
- [ ] 遇到类型错误立即修复,不要累积

**提交代码前**:
- [ ] 运行完整类型检查: `npm run type-check:vue`
- [ ] 运行ESLint: `npm run lint`
- [ ] 修复所有错误和警告
- [ ] 构建验证: `npm run build`

### 典型开发场景

#### 场景1: 新增Vue组件

```typescript
<!-- 1. 创建组件文件 -->
<!-- src/components/MyComponent.vue -->

<template>
  <div class="my-component">
    <h2>{{ title }}</h2>
    <p>{{ description }}</p>
    <button @click="handleClick">{{ buttonText }}</button>
  </div>
</template>

<script setup lang="ts">
// 2. 定义Props接口
interface Props {
  title: string
  description?: string
  buttonText?: string
}

// 3. 定义Props默认值
const props = withDefaults(defineProps<Props>(), {
  description: '默认描述',
  buttonText: '点击'
})

// 4. 定义Emits
interface Emits {
  click: [value: number]
}

const emit = defineEmits<Emits>()

// 5. 定义响应式状态
const count = ref<number>(0)

// 6. 定义方法
const handleClick = () => {
  count.value++
  emit('click', count.value)
}
</script>

<style scoped>
.my-component {
  /* 样式 */
}
</style>
```

#### 场景2: 新增API服务

```typescript
// src/api/user.ts

// 1. 定义类型
export interface User {
  id: string
  name: string
  email: string
  created_at: string
}

export interface CreateUserRequest {
  name: string
  email: string
  password: string
}

export interface UpdateUserRequest {
  name?: string
  email?: string
}

// 2. 定义API响应类型
export interface APIResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  timestamp: string
}

// 3. 定义API适配器
class UserAdapter {
  static adaptFromAPI(apiData: any): User {
    return {
      id: apiData.id || '',
      name: apiData.name || '',
      email: apiData.email || '',
      created_at: apiData.created_at || ''
    }
  }

  static adaptToRequest(user: Partial<User>): any {
    const request: any = {}
    if (user.name) request.name = user.name
    if (user.email) request.email = user.email
    return request
  }
}

// 4. 定义API服务
export const userService = {
  async getUsers(): Promise<User[]> {
    const response = await apiClient.get<APIResponse<User[]>>('/api/users')
    if (response.data.success && response.data.data) {
      return response.data.data.map(UserAdapter.adaptFromAPI)
    }
    throw new Error(response.data.message || '获取用户列表失败')
  },

  async getUserById(id: string): Promise<User> {
    const response = await apiClient.get<APIResponse<User>>(`/api/users/${id}`)
    if (response.data.success && response.data.data) {
      return UserAdapter.adaptFromAPI(response.data.data)
    }
    throw new Error(response.data.message || '获取用户失败')
  },

  async createUser(request: CreateUserRequest): Promise<User> {
    const response = await apiClient.post<APIResponse<User>>(
      '/api/users',
      request
    )
    if (response.data.success && response.data.data) {
      return UserAdapter.adaptFromAPI(response.data.data)
    }
    throw new Error(response.data.message || '创建用户失败')
  },

  async updateUser(id: string, request: UpdateUserRequest): Promise<User> {
    const response = await apiClient.put<APIResponse<User>>(
      `/api/users/${id}`,
      UserAdapter.adaptToRequest(request)
    )
    if (response.data.success && response.data.data) {
      return UserAdapter.adaptFromAPI(response.data.data)
    }
    throw new Error(response.data.message || '更新用户失败')
  }
}
```

#### 场景3: 新增Store (Pinia)

```typescript
// src/stores/user.ts

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  // 1. 定义状态
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // 2. 定义Getters
  const userCount = computed(() => users.value.length)
  const isLoggedIn = computed(() => currentUser.value !== null)

  // 3. 定义Actions
  async function fetchUsers() {
    loading.value = true
    error.value = null

    try {
      const data = await userService.getUsers()
      users.value = data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取用户列表失败'
    } finally {
      loading.value = false
    }
  }

  async function fetchCurrentUser(id: string) {
    loading.value = true
    error.value = null

    try {
      const user = await userService.getUserById(id)
      currentUser.value = user
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取用户失败'
    } finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  // 4. 返回状态和方法
  return {
    // 状态
    users,
    currentUser,
    loading,
    error,

    // Getters
    userCount,
    isLoggedIn,

    // Actions
    fetchUsers,
    fetchCurrentUser,
    clearError
  }
})
```

---

## 🎨 类型系统基础

### 基本类型

```typescript
// 原始类型
let num: number = 42
let str: string = 'Hello'
let bool: boolean = true
let empty: null = null
let notDefined: undefined = undefined

// 数组
let numbers: number[] = [1, 2, 3]
let strings: Array<string> = ['a', 'b', 'c']

// 对象
let user: { name: string; age: number } = {
  name: 'John',
  age: 30
}

// 函数
let add: (a: number, b: number) => number = (a, b) => a + b

// 可选属性
let config: { required: string; optional?: number } = {
  required: 'value'
}

// 联合类型
let value: string | number = 'hello'
value = 42  // OK

// 字面量类型
let direction: 'up' | 'down' | 'left' | 'right' = 'up'
```

### 接口 vs 类型别名

```typescript
// 接口(Interface)
interface User {
  id: string
  name: string
  email?: string  // 可选
}

interface AdminUser extends User {
  permissions: string[]
}

// 类型别名(Type Alias)
type ID = string | number

type UserWithRoles = User & {
  roles: string[]
}

// 使用场景
// ✅ 接口: 定义对象结构,可扩展
interface APIResponse {
  success: boolean
  data?: any
}

// ✅ 类型别名: 联合类型,交叉类型,映射类型
type Status = 'pending' | 'success' | 'error'
type Nullable<T> = T | null
```

### 泛型

```typescript
// 泛型函数
function identity<T>(arg: T): T {
  return arg
}

const num = identity<number>(42)
const str = identity('hello')  // 类型推断

// 泛型接口
interface Box<T> {
  value: T
}

const box: Box<number> = { value: 42 }

// 泛型约束
interface Lengthwise {
  length: number
}

function logLength<T extends Lengthwise>(arg: T): void {
  console.log(arg.length)
}

logLength({ length: 10, value: 'hello' })  // OK
// logLength({ value: 'hello' })  // Error

// 泛型类
class Storage<T> {
  private items: T[] = []

  add(item: T): void {
    this.items.push(item)
  }

  get(index: number): T | undefined {
    return this.items[index]
  }
}

const storage = new Storage<number>()
storage.add(1)
storage.add(2)
```

---

## 🖼️ Vue 3 + TypeScript开发

### 组件Props类型

```vue
<script setup lang="ts">
// 方式1: 简单类型(默认值)
const props = defineProps<{
  title: string
  count?: number
}>()

// 方式2: 接口定义
interface Props {
  label: string
  value: number | string
  disabled?: boolean
}

const props = defineProps<Props>()

// 方式3: 默认值
const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

// 方式4: 构造函数类型
const props = defineProps<{
  size: 'small' | 'medium' | 'large'
  modelValue: string | number
}>()
</script>
```

### Emits类型

```vue
<script setup lang="ts">
// 方式1: 简单类型
const emit = defineEmits<{
  click: []
  change: [value: number]
}>()

// 使用
emit('click')
emit('change', 42)

// 方式2: 运行时声明 + TypeScript类型
const emit = defineEmits({
  click: null,
  change: (value: number) => true
})

// TypeScript类型定义
interface Emits {
  click: []
  change: [value: number]
  update:modelValue: [value: string]
}

const emit = defineEmits<Emits>()
</script>
```

### Ref类型

```vue
<script setup lang="ts">
import { ref } from 'vue'

// 简单类型
const count = ref<number>(0)
const message = ref<string>('hello')

// 对象类型
interface User {
  id: string
  name: string
}

const user = ref<User | null>(null)

// 数组类型
const items = ref<ItemType[]>([])

// 泛型Ref
interface Ref<T> {
  value: T
}

const data = ref<DataType>({ key: 'value' })

// 初始值推断
const count = ref(0)  // 推断为 Ref<number>
const list = ref([])  // 推断为 Ref<any[]>,不推荐
```

### Reactive类型

```vue
<script setup lang="ts">
import { reactive } from 'vue'

// 接口定义
interface State {
  user: User | null
  loading: boolean
  error: string | null
}

const state = reactive<State>({
  user: null,
  loading: false,
  error: null
})

// 泛型
function useState<T>(initial: T) {
  return reactive<T>(initial)
}

const state = useState({
  count: 0,
  name: ''
})
</script>
```

### Computed类型

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

const count = ref<number>(0)

// 自动推断
const doubled = computed(() => count.value * 2)
// doubled类型: ComputedRef<number>

// 显式指定
const formatted = computed<string>(() => {
  return count.value.toFixed(2)
})

// Getter和Setter
const fullName = computed<string>({
  get() {
    return `${firstName.value} ${lastName.value}`
  },
  set(value: string) {
    [firstName.value, lastName.value] = value.split(' ')
  }
})
</script>
```

### Watch和WatchEffect类型

```vue
<script setup lang="ts">
import { ref, watch, watchEffect } from 'vue'

const count = ref<number>(0)

// watch - 单个源
watch(count, (newVal, oldVal) => {
  console.log(`count changed from ${oldVal} to ${newVal}`)
})

// watch - 多个源
const firstName = ref<string>('')
const lastName = ref<string>('')

watch([firstName, lastName], ([newFirst, newLast], [oldFirst, oldLast]) => {
  console.log(`name changed from ${oldFirst} ${oldLast} to ${newFirst} ${newLast}`)
})

// watch - getter函数
watch(
  () => count.value * 2,
  (newVal, oldVal) => {
    console.log(`doubled count changed from ${oldVal} to ${newVal}`)
  }
)

// watchEffect - 自动追踪
watchEffect(() => {
  console.log(`count is: ${count.value}`)
})
</script>
```

---

## 🔌 API集成与类型安全

### API响应类型定义

```typescript
// src/types/api.ts

// 1. 标准API响应
export interface APIResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  code?: string
  timestamp: string
}

// 2. 分页响应
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

// 3. 列表响应
export interface ListResponse<T> extends APIResponse<T[]> {
  total?: number
  page?: number
  pageSize?: number
}
```

### API客户端类型

```typescript
// src/api/client.ts

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

export interface APIClientConfig {
  baseURL: string
  timeout?: number
  headers?: Record<string, string>
}

export class APIClient {
  private client: AxiosInstance

  constructor(config: APIClientConfig) {
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      headers: config.headers
    })
  }

  async get<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<APIResponse<T>>> {
    return this.client.get<APIResponse<T>>(url, config)
  }

  async post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<APIResponse<T>>> {
    return this.client.post<APIResponse<T>>(url, data, config)
  }

  async put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<APIResponse<T>>> {
    return this.client.put<APIResponse<T>>(url, data, config)
  }

  async delete<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<APIResponse<T>>> {
    return this.client.delete<APIResponse<T>>(url, config)
  }
}

// 使用
export const apiClient = new APIClient({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})
```

### API服务层示例

```typescript
// src/services/strategyService.ts

import { apiClient } from '@/api/client'
import type { Strategy, StrategyAdapter } from '@/api/types/strategy'

export class StrategyService {
  /**
   * 获取策略列表
   */
  async getStrategies(): Promise<Strategy[]> {
    const response = await apiClient.get<Strategy[]>('/api/strategies')

    if (response.data.success && response.data.data) {
      return response.data.data.map(StrategyAdapter.adaptFromAPI)
    }

    throw new Error(response.data.message || '获取策略列表失败')
  }

  /**
   * 获取单个策略
   */
  async getStrategy(id: string): Promise<Strategy> {
    const response = await apiClient.get<Strategy>(`/api/strategies/${id}`)

    if (response.data.success && response.data.data) {
      return StrategyAdapter.adaptFromAPI(response.data.data)
    }

    throw new Error(response.data.message || '获取策略失败')
  }

  /**
   * 创建策略
   */
  async createStrategy(request: CreateStrategyRequest): Promise<Strategy> {
    const response = await apiClient.post<Strategy>(
      '/api/strategies',
      StrategyAdapter.adaptToRequest(request)
    )

    if (response.data.success && response.data.data) {
      return StrategyAdapter.adaptFromAPI(response.data.data)
    }

    throw new Error(response.data.message || '创建策略失败')
  }

  /**
   * 更新策略
   */
  async updateStrategy(id: string, request: UpdateStrategyRequest): Promise<Strategy> {
    const response = await apiClient.put<Strategy>(
      `/api/strategies/${id}`,
      StrategyAdapter.adaptToRequest(request)
    )

    if (response.data.success && response.data.data) {
      return StrategyAdapter.adaptFromAPI(response.data.data)
    }

    throw new Error(response.data.message || '更新策略失败')
  }

  /**
   * 删除策略
   */
  async deleteStrategy(id: string): Promise<void> {
    const response = await apiClient.delete<void>(`/api/strategies/${id}`)

    if (!response.data.success) {
      throw new Error(response.data.message || '删除策略失败')
    }
  }
}

export const strategyService = new StrategyService()
```

---

## 🧪 测试与类型安全

### 单元测试类型

```typescript
// tests/utils/dateUtils.test.ts

import { describe, it, expect } from 'vitest'
import { formatDate, parseDate } from '@/utils/dateUtils'

describe('DateUtils', () => {
  describe('formatDate', () => {
    it('should format date correctly', () => {
      const date: Date = new Date('2026-01-20')
      const formatted: string = formatDate(date, 'YYYY-MM-DD')
      expect(formatted).toBe('2026-01-20')
    })

    it('should handle invalid date', () => {
      const result: string = formatDate(new Date('invalid'), 'YYYY-MM-DD')
      expect(result).toBe('Invalid Date')
    })
  })

  describe('parseDate', () => {
    it('should parse date string', () => {
      const date: Date | null = parseDate('2026-01-20', 'YYYY-MM-DD')
      expect(date).not.toBeNull()
      expect(date?.getFullYear()).toBe(2026)
    })

    it('should return null for invalid input', () => {
      const date: Date | null = parseDate('invalid', 'YYYY-MM-DD')
      expect(date).toBeNull()
    })
  })
})
```

### Vue组件测试类型

```typescript
// tests/components/MyComponent.test.ts

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent', () => {
  it('renders props correctly', () => {
    const wrapper = mount(MyComponent, {
      props: {
        title: 'Test Title',
        count: 42
      } as {
        title: string
        count: number
      }
    })

    expect(wrapper.props('title')).toBe('Test Title')
    expect(wrapper.props('count')).toBe(42)
  })

  it('emits event with correct payload', async () => {
    const wrapper = mount(MyComponent)

    await wrapper.find('button').trigger('click')

    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click')[0]).toEqual([1])
  })
})
```

---

## 📋 常见任务指南

### 任务1: 添加新的类型定义

**场景**: 需要为新功能添加类型定义

**步骤**:

1. **创建类型文件**
   ```bash
   # 在src/types/下创建类型文件
   touch src/types/feature.ts
   ```

2. **定义类型**
   ```typescript
   // src/types/feature.ts

   export interface FeatureConfig {
     enabled: boolean
     priority: number
     options?: Record<string, any>
   }

   export interface FeatureResult {
     success: boolean
     data?: any
     error?: string
   }
   ```

3. **导出类型**
   ```typescript
   // src/types/index.ts

   export * from './feature'
   export * from './user'
   export * from './strategy'
   ```

4. **使用类型**
   ```typescript
   import type { FeatureConfig, FeatureResult } from '@/types'

   const config: FeatureConfig = {
     enabled: true,
     priority: 1
   }
   ```

### 任务2: 修复类型错误

**场景**: 类型检查报错需要修复

**步骤**:

1. **运行类型检查**
   ```bash
   npm run type-check 2>&1 | tee errors.txt
   ```

2. **分析错误**
   ```bash
   # 统计错误类型
   grep "error TS" errors.txt | awk '{print $2}' | sort | uniq -c
   ```

3. **选择修复策略**
   - **P0错误**: 阻塞编译,立即修复
   - **P1错误**: 影响功能,优先修复
   - **P2错误**: 非关键,稍后修复

4. **应用修复**
   - 参考故障排除指南
   - 使用批量修复脚本
   - 验证修复效果

### 任务3: 更新第三方库类型

**场景**: 安装了新的第三方库,需要类型定义

**步骤**:

1. **查找类型包**
   ```bash
   npm search @types/<package-name>
   ```

2. **安装类型定义**
   ```bash
   npm install --save-dev @types/<package-name>
   ```

3. **验证类型**
   ```typescript
   import * as Package from 'package-name'
   // 类型应该自动可用
   ```

4. **如无官方类型,创建自定义类型**
   ```typescript
   // src/types/third-party.d.ts

   declare module 'package-name' {
     export interface API {
       method(): void
     }

     const api: API
     export default api
   }
   ```

### 任务4: 迁移JavaScript到TypeScript

**场景**: 将现有.js文件迁移到.ts

**步骤**:

1. **重命名文件**
   ```bash
   mv utils/helper.js utils/helper.ts
   ```

2. **添加类型注解**
   ```typescript
   // ❌ 迁移前
   export function add(a, b) {
     return a + b
   }

   // ✅ 迁移后
   export function add(a: number, b: number): number {
     return a + b
   }
   ```

3. **定义接口**
   ```typescript
   // 定义参数和返回值类型
   interface UserData {
     name: string
     age: number
   }

   export function processUser(user: UserData): string {
     return `${user.name} is ${user.age} years old`
   }
   ```

4. **验证迁移**
   ```bash
   npm run type-check
   npm run lint
   ```

---

## 👥 团队协作规范

### 代码审查检查点

**TypeScript相关检查**:

- [ ] 所有函数都有类型注解
- [ ] 组件Props/Emits正确定义
- [ ] 没有`@ts-ignore`注释(除非有充分理由)
- [ ] 没有`any`类型(除明确标注)
- [ ] 类型检查通过: `npm run type-check:vue`
- [ ] ESLint检查通过: `npm run lint`

### Pull Request模板

```markdown
## TypeScript类型检查

- [ ] 所有类型错误已修复
- [ ] 类型覆盖率保持或提升
- [ ] 新增类型已定义并导出
- [ ] API适配器已更新

## 类型检查结果

```bash
npm run type-check
# ✅ No errors found
```

## ESLint检查结果

```bash
npm run lint
# ✅ No warnings found
```
```

### 文档更新要求

**需要更新文档的情况**:

1. **新增类型定义**
   - 更新`src/types/README.md`
   - 添加使用示例

2. **新增API服务**
   - 更新API文档
   - 添加请求/响应类型

3. **新增组件**
   - 添加Props/Emits文档
   - 提供使用示例

---

## 📚 相关文档

### 快速参考
- 📖 [TypeScript快速开始](./Typescript_QUICKSTART.md)
- 📖 [TypeScript最佳实践](./Typescript_BEST_PRACTICES.md)

### 深入学习
- 📖 [TypeScript配置参考](./Typescript_CONFIG_REFERENCE.md)
- 📖 [TypeScript故障排除](./Typescript_TROUBLESHOOTING.md)

### 培训文档
- 📖 [TypeScript新手培训](./Typescript_TRAINING_BEGINNER.md)
- 📖 [TypeScript高级培训](./Typescript_TRAINING_ADVANCED.md)

---

**文档维护**: 本文档应随项目发展持续更新
**最后更新**: 2026-01-20
**维护者**: Main CLI (Claude Code)
**版本**: v1.0
