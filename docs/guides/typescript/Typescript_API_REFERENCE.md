# TypeScript API 参考手册

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**版本**: v1.0 | **更新时间**: 2026-01-20 | **API版本**: Phase 1.4

> MyStocks项目TypeScript相关API完整参考,包括编译器API、配置API、工具API等。

---

## 📋 目录

1. [TypeScript编译器API](#typescript编译器api)
2. [Vue 3 TypeScript API](#vue-3-typescript-api)
3. [工具函数API](#工具函数api)
4. [类型定义API](#类型定义api)

---

## 🔧 TypeScript编译器API

### 命令行API

```bash
# 类型检查
tsc --noEmit                           # 只检查不生成文件
tsc --noEmit --pretty                   # 友好输出
tsc --noEmit --incremental             # 增量编译

# 监视模式
tsc --noEmit --watch                   # 文件变化自动检查

# 生成d.ts
tsc --declaration                      # 生成类型声明文件

# 显示详细信息
tsc --listFiles                        # 列出所有文件
tsc --explainFiles                     # 解释文件包含原因
```

---

## 🖼️ Vue 3 TypeScript API

### defineProps

```typescript
// 简单类型
const props = defineProps<{
  title: string
  count?: number
}>()

// 接口类型
interface Props {
  label: string
  value: number
}

const props = defineProps<Props>()

// 默认值
const props = withDefaults(defineProps<Props>(), {
  value: 0
})
```

### defineEmits

```typescript
// 类型定义
const emit = defineEmits<{
  click: [value: number]
  change: [newValue: string]
}>()

// 使用
emit('click', 42)
```

### ref和reactive

```typescript
import { ref, reactive } from 'vue'

// ref
const count = ref<number>(0)
const user = ref<User | null>(null)

// reactive
interface State {
  count: number
  user: User | null
}

const state = reactive<State>({
  count: 0,
  user: null
})
```

### computed

```typescript
// 只读
const doubled = computed(() => count.value * 2)

// 可读写
const fullName = computed<string>({
  get() => `${first.value} ${last.value}`,
  set(value) => { [first.value, last.value] = value.split(' ') }
})
```

---

## 🛠️ 工具函数API

### 类型守卫

```typescript
// 类型守卫函数
function isUser(obj: any): obj is User {
  return obj && typeof obj.id === 'string' && typeof obj.name === 'string'
}

// 使用
if (isUser(data)) {
  console.log(data.name)  // 类型安全
}
```

### 类型断言

```typescript
// as断言
const value = data as string

// 非空断言
const name = user!.name

// 双重断言
const item = data as unknown as ItemType
```

---

**文档维护**: API参考应随代码更新持续维护
**最后更新**: 2026-01-20
**版本**: v1.0
