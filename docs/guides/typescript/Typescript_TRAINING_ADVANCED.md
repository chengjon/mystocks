# TypeScript 高级培训

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**版本**: v1.0 | **更新时间**: 2026-01-20

> TypeScript高级类型系统深度培训,包括条件类型、映射类型、类型体操等。

---

## 🎯 培训目标

- 掌握高级类型系统特性
- 理解类型推导机制
- 学会类型级编程
- 掌握性能优化技巧

**预计时间**: 4小时
**前置要求**: 完成Typescript_TRAINING_BEGINNER.md

---

## 📚 第一部分: 高级类型 (60分钟)

### 1. 条件类型 (Conditional Types)

**基本语法**:
```typescript
type IsArray<T> = T extends any[] ? true : false

// 使用
type Test1 = IsArray<string>  // false
type Test2 = IsArray<number[]>  // true
```

**实际应用**:
```typescript
// API响应类型处理
type ApiResponse<T> = T extends string
  ? { message: T }
  : { data: T }

type StringResponse = ApiResponse<'Success'>  // { message: 'Success' }
type DataResponse = ApiResponse<{ id: number }>  // { data: { id: number } }
```

**分布式条件类型**:
```typescript
type ToArray<T> = T extends any ? T[] : never

// 联合类型会被分配
type Result = ToArray<string | number>  // string[] | number[]
```

---

### 2. 映射类型 (Mapped Types)

**基础映射**:
```typescript
type Readonly<T> = {
  readonly [P in keyof T]: T[P]
}

type Partial<T> = {
  [P in keyof T]?: T[P]
}
```

**高级映射**:
```typescript
// 添加/移除修饰符
type CreateMutable<T> = {
  -readonly [P in keyof T]: T[P]
}

type Required<T> = {
  [P in keyof T]-?: T[P]
}

// 模板字面量键
type Getters<T> = {
  [P in keyof T as `get${Capitalize<string & P>}`]: () => T[P]
}

interface Person {
  name: string
  age: number
}

type PersonGetters = Getters<Person>
// {
//   getName: () => string
//   getAge: () => number
// }
```

---

### 3. 模板字面量类型 (Template Literal Types)

**基本用法**:
```typescript
type EventName<T extends string> = `on${Capitalize<T>}`

type ClickEvent = EventName<'click'>  // 'onClick'
type MouseEvent = EventName<'mouse'>  // 'onMouse'
```

**实际应用**:
```typescript
// CSS属性类型
type CssProperties<T extends string> = `--${T}`

type ThemeVars = CssProperties<'color' | 'background' | 'font'>
// '--color' | '--background' | '--font'

// 路由类型
type Routes = `/api/${'users' | 'posts'}/${number}`

const route1: Routes = '/api/users/123'  // ✅
const route2: Routes = '/api/products/456'  // ❌
```

---

### 4. 递归类型

**树形结构**:
```typescript
type TreeNode<T> = {
  value: T
  left?: TreeNode<T>
  right?: TreeNode<T>
}

// JSON类型
type JSONValue =
  | string
  | number
  | boolean
  | null
  | JSONValue[]
  | { [key: string]: JSONValue }
```

**类型级递归**:
```typescript
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object
    ? DeepReadonly<T[P]>
    : T[P]
}

interface User {
  name: string
  address: {
    city: string
    street: string
  }
}

type ReadonlyUser = DeepReadonly<User>
// 所有层级都是 readonly
```

---

## 🎓 第二部分: 类型体操 (60分钟)

### 1. 类型推断 (Inference)

**infer关键字**:
```typescript
type Unpromise<T> = T extends Promise<infer U> ? U : T

type Test = Unpromise<Promise<number>>  // number

// 提取函数返回值
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : any

// 提取数组元素类型
type ElementType<T> = T extends (infer U)[] ? U : never
```

**实际应用**:
```typescript
// Vue 3 ref类型推断
type UnwrapRef<T> = T extends Ref<infer V> ? V : T

function useRef<T>(value: T): Ref<T> {
  return ref(value)
}

const count = useRef(0)
type CountType = UnwrapRef<typeof count>  // number
```

---

### 2. 类型守卫 (Type Guards)

**typeof类型守卫**:
```typescript
function isString(value: unknown): value is string {
  return typeof value === 'string'
}

function process(value: unknown) {
  if (isString(value)) {
    console.log(value.toUpperCase())  // 类型安全
  }
}
```

**in类型守卫**:
```typescript
interface Fish {
  swim: () => void
}

interface Bird {
  fly: () => void
}

function isFish(pet: Fish | Bird): pet is Fish {
  return 'swim' in pet
}
```

**instanceof类型守卫**:
```typescript
class Dog {
  bark() {}
}

class Cat {
  meow() {}
}

function isAnimal(value: unknown): value is Dog | Cat {
  return value instanceof Dog || value instanceof Cat
}
```

---

### 3. 判别联合 (Discriminated Unions)

```typescript
interface SuccessResponse {
  status: 'success'
  data: unknown
}

interface ErrorResponse {
  status: 'error'
  error: string
}

type ApiResponse = SuccessResponse | ErrorResponse

function handleResponse(response: ApiResponse) {
  if (response.status === 'success') {
    console.log(response.data)  // 类型安全
  } else {
    console.log(response.error)  // 类型安全
  }
}
```

---

## ⚡ 第三部分: 性能优化 (60分钟)

### 1. 类型计算优化

**避免过度复杂**:
```typescript
// ❌ 不好: 过度复杂
type Bad<T> = T extends { a: infer A } ?
  A extends { b: infer B } ?
    B extends { c: infer C } ? C : never : never : never

// ✅ 好: 分步处理
type Step1<T> = T extends { a: infer A } ? A : never
type Step2<T> = T extends { b: infer B } ? B : never
type Step3<T> = T extends { c: infer C } ? C : never
type Good<T> = Step3<Step2<Step1<T>>>
```

**使用类型别名缓存**:
```typescript
// ✅ 好: 类型别名被缓存
type User = {
  name: string
  email: string
}

type AdminUser = User & { role: 'admin' }
type GuestUser = User & { role: 'guest' }
```

---

### 2. 泛型约束优化

**合理约束**:
```typescript
// ✅ 好: 合理约束
function length<T extends { length: number }>(arg: T): number {
  return arg.length
}

// ❌ 不好: 过度约束
function badLength<T extends string | any[]>(arg: T): number {
  return arg.length
}
```

**多重约束**:
```typescript
type WithLength = { length: number }
type WithSlice = { slice: (start: number, end?: number) => any }

function process<T extends WithLength & WithSlice>(arg: T) {
  return arg.slice(0, arg.length)
}
```

---

### 3. 条件类型优化

**提前返回**:
```typescript
// ❌ 不好: 嵌套过深
type BadType<T> = T extends string
  ? 'string'
  : T extends number
    ? 'number'
    : T extends boolean
      ? 'boolean'
      : 'other'

// ✅ 好: 分步处理
type IsString<T> = T extends string ? 'string' : never
type IsNumber<T> = T extends number ? 'number' : never
type IsBoolean<T> = T extends boolean ? 'boolean' : never

type GoodType<T> =
  | IsString<T>
  | IsNumber<T>
  | IsBoolean<T>
  | 'other'
```

---

## 🔧 第四部分: 实战案例 (60分钟)

### 案例1: 通用API适配器

```typescript
// 定义API方法
type ApiMethod = 'GET' | 'POST' | 'PUT' | 'DELETE'

interface ApiConfig<T> {
  url: string
  method: ApiMethod
  data?: T
  headers?: Record<string, string>
}

// 类型安全的API调用
async function apiCall<T, R>(
  config: ApiConfig<T>
): Promise<R> {
  const response = await fetch(config.url, {
    method: config.method,
    headers: config.headers,
    body: config.data ? JSON.stringify(config.data) : undefined
  })

  return response.json()
}

// 使用
interface LoginRequest {
  username: string
  password: string
}

interface LoginResponse {
  token: string
  userId: string
}

const result = await apiCall<LoginRequest, LoginResponse>({
  url: '/api/login',
  method: 'POST',
  data: { username: 'user', password: 'pass' }
})
```

---

### 案例2: 类型安全的Store工厂

```typescript
// 定义Store配置
interface StoreConfig<T, A> {
  state: T
  actions: A
}

// 创建Store
function createStore<T extends Record<string, any>, A extends Record<string, Function>>(
  config: StoreConfig<T, A>
) {
  return {
    state: config.state,
    actions: config.actions,
    getState<K extends keyof T>(key: K): T[K] {
      return config.state[key]
    },
    setState<K extends keyof T>(key: K, value: T[K]): void {
      config.state[key] = value
    }
  }
}

// 使用
interface UserState {
  name: string
  email: string
}

interface UserActions {
  updateName: (name: string) => void
  updateEmail: (email: string) => void
}

const store = createStore<UserState, UserActions>({
  state: {
    name: '',
    email: ''
  },
  actions: {
    updateName(name) {
      store.setState('name', name)
    },
    updateEmail(email) {
      store.setState('email', email)
    }
  }
})

// 类型安全访问
store.setState('name', 'Alice')  // ✅
store.setState('age', 25)  // ❌ 编译错误
```

---

### 案例3: 事件系统

```typescript
// 定义事件映射
type EventMap = {
  click: { x: number; y: number }
  keydown: { key: string; code: string }
  scroll: { scrollTop: number }
}

// 事件监听器
type EventListener<K extends keyof EventMap> = (
  event: EventMap[K]
) => void

// 事件发射器
class EventEmitter<T extends Record<string, any>> {
  private listeners: Map<keyof T, Set<Function>> = new Map()

  on<K extends keyof T>(
    event: K,
    listener: EventListener<K>
  ): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(listener)
  }

  off<K extends keyof T>(
    event: K,
    listener: EventListener<K>
  ): void {
    this.listeners.get(event)?.delete(listener)
  }

  emit<K extends keyof T>(
    event: K,
    data: T[K]
  ): void {
    this.listeners.get(event)?.forEach(listener => {
      listener(data)
    })
  }
}

// 使用
const emitter = new EventEmitter<EventMap>()

emitter.on('click', (event) => {
  console.log(event.x, event.y)  // 类型安全
})

emitter.emit('click', { x: 100, y: 200 })  // ✅
emitter.emit('click', { x: 100 })  // ❌ 缺少y
```

---

## 📝 实战练习

### 练习1: 深度Nullable

创建一个工具类型,将对象的所有属性(包括嵌套)变为可选:

```typescript
// 实现 DeepNullable
type DeepNullable<T> = // 你的代码

// 测试
interface Test {
  user: {
    name: string
    address: {
      city: string
    }
  }
}

type Result = DeepNullable<Test>
// 期望: { user?: { name?: string; address?: { city?: string } } }
```

### 练习2: 函数组合器

创建一个类型安全的函数组合工具:

```typescript
// 实现 compose
function compose<T extends any[], R,>(
  ...fns: Function[]
): Function {
  // 你的代码
}

// 测试
const add = (a: number) => (b: number) => a + b
const multiply = (a: number) => (b: number) => a * b

const addAndMultiply = compose(add(2), multiply(3))
console.log(addAndMultiply(4))  // (2 + 4) * 3 = 18
```

### 练习3: 路径类型

创建一个从对象类型生成路径字符串的类型:

```typescript
// 实现 PathType
type PathType<T> = // 你的代码

interface User {
  name: string
  profile: {
    age: number
    address: {
      city: string
    }
  }
}

// 期望: 'name' | 'profile' | 'profile.age' | 'profile.address' | 'profile.address.city'
```

---

## 🎓 进阶资源

### 推荐阅读

1. **TypeScript Handbook - Advanced Types**
   - 官方高级类型文档

2. **TypeScript Type System playground**
   - 在线类型体操练习

3. **Utility Types参考**
   - TypeScript内置工具类型

### 实践项目

1. **类型状态机**: 使用类型系统实现状态机
2. **类型安全的表单**: 完全类型驱动的表单验证
3. **类型级DSL**: 领域特定语言的类型定义

---

**文档维护**: 高级培训应随TypeScript版本更新
**最后更新**: 2026-01-20
**版本**: v1.0
