# TypeScript 新手培训指南

**版本**: v1.0 | **更新时间**: 2026-01-20 | **目标读者**: TypeScript初学者

> 从零开始学习TypeScript,2小时掌握MyStocks项目TypeScript开发基础。

---

## 📚 课程大纲

1. [TypeScript基础](#typescript基础) - 30分钟
2. [类型系统](#类型系统) - 30分钟
3. [Vue 3 + TypeScript](#vue-3--typescript) - 30分钟
4. [实战练习](#实战练习) - 30分钟

---

## 🎯 TypeScript基础

### 什么是TypeScript?

TypeScript是JavaScript的超集,添加了静态类型检查。

**关键优势**:
- ✅ 提前发现错误(编译时而非运行时)
- ✅ 更好的IDE支持(自动完成、重构)
- ✅ 更好的代码文档(类型即文档)

### 基本类型

```typescript
// 原始类型
let num: number = 42
let str: string = 'Hello'
let bool: boolean = true

// 数组
let numbers: number[] = [1, 2, 3]
let strings: string[] = ['a', 'b', 'c']

// 对象
let user: { name: string; age: number } = {
  name: 'John',
  age: 30
}

// 函数
function add(a: number, b: number): number {
  return a + b
}
```

### 接口定义

```typescript
// 定义接口
interface User {
  id: string
  name: string
  email?: string  // 可选
}

// 使用接口
const user: User = {
  id: '1',
  name: 'John'
}
```

---

## 🎨 类型系统

### 联合类型

```typescript
// 多种可能的类型
let value: string | number = 'hello'
value = 42  // OK

// 字面量类型
type Direction = 'up' | 'down' | 'left' | 'right'
```

### 泛型

```typescript
// 泛型函数
function identity<T>(arg: T): T {
  return arg
}

const num = identity<number>(42)
const str = identity('hello')

// 泛型接口
interface Box<T> {
  value: T
}

const box: Box<number> = { value: 42 }
```

---

## 🖼️ Vue 3 + TypeScript

### 组件Props

```vue
<script setup lang="ts">
interface Props {
  title: string
  count?: number
}

const props = defineProps<Props>()
</script>
```

### Ref和Reactive

```vue
<script setup lang="ts">
import { ref, reactive } from 'vue'

const count = ref<number>(0)

interface State {
  user: User | null
  loading: boolean
}

const state = reactive<State>({
  user: null,
  loading: false
})
</script>
```

### Emits

```vue
<script setup lang="ts">
const emit = defineEmits<{
  click: [value: number]
  change: [newValue: string]
}>()

emit('click', 42)
</script>
```

---

## 🎓 实战练习

### 练习1: 创建简单组件 (15分钟)

创建一个计数器组件,包含:
- Props: 初始值
- Emits: 计数变化事件
- Ref: 当前计数

### 练习2: API类型定义 (15分钟)

为以下API定义类型:
- GET /api/users - 获取用户列表
- POST /api/users - 创建用户
- PUT /api/users/:id - 更新用户

### 练习3: Store类型 (15分钟)

创建Pinia store:
- State: 用户列表、加载状态
- Actions: 获取用户、创建用户、删除用户

---

## 📚 进阶学习路径

**第1周**: 完成本培训指南 + 实战练习
**第2周**: 阅读[TypeScript最佳实践](./Typescript_BEST_PRACTICES.md)
**第3周**: 学习[TypeScript用户手册](./Typescript_USER_GUIDE.md)
**第4周**: 尝试修复真实的TypeScript错误

---

**文档维护**: 本文档应随TypeScript版本更新
**最后更新**: 2026-01-20
**维护者**: Main CLI (Claude Code)
**版本**: v1.0
