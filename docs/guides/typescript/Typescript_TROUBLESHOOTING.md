# TypeScript 故障排除指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**版本**: v1.0 | **更新时间**: 2026-01-20 | **阅读时间**: 10分钟

> 完整的TypeScript错误诊断、排查和修复指南，涵盖20+种常见错误及解决方案。

---

## 📋 目录

1. [快速诊断流程](#快速诊断流程)
2. [常见错误分类排查](#常见错误分类排查)
3. [20+种错误代码详解](#20种错误代码详解)
4. [性能问题诊断](#性能问题诊断)
5. [构建失败处理](#构建失败处理)
6. [IDE问题解决](#ide问题解决)
7. [高级诊断技巧](#高级诊断技巧)

---

## 🔍 快速诊断流程

### 流程图

```
┌─────────────────┐
│ 运行类型检查    │
│ npm run type-check │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 查看错误数量    │
│ 和类型分布      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐  ┌───────┐
│ <100个 │  │ >100个│
│ 错误   │  │ 错误   │
└───┬───┘  └───┬───┘
    │          │
    ▼          ▼
┌───────┐  ┌───────┐
│按优先级│  │批量修复│
│手动修复│  │+脚本  │
└───────┘  └───────┘
```

### Step 1: 运行完整诊断

```bash
# 完整类型检查（包含Vue组件）
npm run type-check:vue 2>&1 | tee type-check-output.txt

# 统计错误数量
ERROR_COUNT=$(grep -c "error TS" type-check-output.txt)
echo "总错误数: $ERROR_COUNT"

# 统计错误类型分布
grep "error TS" type-check-output.txt | \
  sed 's/.*error TS[0-9]*: //' | \
  sort | uniq -c | sort -nr | \
  head -10
```

### Step 2: 识别错误模式

```bash
# 查找重复错误模式
grep "error TS" type-check-output.txt | \
  awk '{print $2}' | \
  sort | uniq -c | sort -nr

# 输出示例:
#   28 TS2484  Export declaration conflicts
#   13 TS7006  implicitly has an 'any' type
#    8 TS2532  Object is possibly 'undefined'
```

### Step 3: 选择修复策略

| 错误数量 | 修复策略 | 工具 | 预计时间 |
|---------|---------|------|---------|
| **< 10个** | 手动修复 | VS Code | 10分钟 |
| **10-50个** | 批量+手动 | Perl脚本 | 30分钟 |
| **50-100个** | 批量为主 | ESLint + Perl | 1小时 |
| **> 100个** | 从源头修复 | 生成脚本 | 2-4小时 |

---

## 🔧 常见错误分类排查

### 分类1: 类型导入错误 (最关键)

**症状**:
```
error TS2305: has no exported member 'XXX'
error TS2307: Cannot find module '@/types/YYY'
```

**排查步骤**:

1. **确认导出位置**
   ```bash
   # 搜索类型定义
   grep -r "export.*XXX" src/ --include="*.ts"

   # 搜索文件位置
   find src -name "YYY.ts" -o -name "YYY.d.ts"
   ```

2. **检查导入路径**
   ```typescript
   // ❌ 错误路径
   import { Strategy } from '@/types/strategy'

   // ✅ 正确路径
   import { Strategy } from '@/api/types/strategy'
   ```

3. **验证模块导出**
   ```typescript
   // 确认文件末尾有正确的导出
   // src/api/types/strategy.ts
   export interface Strategy { /* ... */ }

   // 或使用批量导出
   export type { Strategy }
   ```

### 分类2: 类型定义错误

**症状**:
```
error TS2304: Cannot find name 'Dict'
error TS2304: Cannot find name 'List'
error TS2339: Property 'xxx' does not exist on type 'YYY'
```

**排查步骤**:

1. **查找类型定义位置**
   ```bash
   # 搜索类型定义
   grep -r "interface Dict" src/
   grep -r "type Dict" src/

   # 检查生成文件
   cat src/api/types/generated-types.ts | grep "Dict"
   ```

2. **添加类型定义**
   ```typescript
   // 在文件顶部或全局类型文件中添加
   export type Dict = Record<string, any>;
   export type List<T = any> = T[];
   export type T = any;
   export type date_type = string;
   ```

3. **扩展现有类型**
   ```typescript
   // 扩展浏览器API类型
   interface NavigatorWithConnection extends Navigator {
     connection?: NetworkConnection
   }

   const nav = navigator as NavigatorWithConnection
   ```

### 分类3: Vue组件类型错误

**症状**:
```
error TS2740: Property 'label' is missing
error TS2339: Property 'xxx' does not exist on component instance
```

**排查步骤**:

1. **检查Props定义**
   ```typescript
   // ❌ 缺少Props接口
   const props = defineProps(['label', 'value'])

   // ✅ 正确定义Props
   interface Props {
     label: string
     value: number
   }
   const props = defineProps<Props>()
   ```

2. **验证组件使用**
   ```vue
   <!-- ❌ 缺少必需属性 -->
   <ArtDecoStatCard title="统计" :value="123" />

   <!-- ✅ 正确使用 -->
   <ArtDecoStatCard label="统计" :value="123" />
   ```

3. **检查Emits定义**
   ```typescript
   // ❌ 未定义Emits类型
   const emit = defineEmits(['click', 'change'])

   // ✅ 正确定义Emits
   const emit = defineEmits<{
     click: [value: number]
     change: [newValue: number]
   }>()
   ```

### 分类4: 类型推断错误

**症状**:
```
error TS7006: Parameter 'xxx' implicitly has an 'any' type
error TS7022: 'xxx' implicitly has type 'any'
```

**排查步骤**:

1. **添加显式类型注解**
   ```typescript
   // ❌ 隐式any
   const handleData = (data) => { return data.value }

   // ✅ 显式类型
   const handleData = (data: { value: number }) => {
     return data.value
   }

   // ✅ 使用泛型
   const handleData = <T extends { value: any }>(data: T) => {
     return data.value
   }
   ```

2. **配置编译选项**
   ```json
   // tsconfig.json
   {
     "compilerOptions": {
       "noImplicitAny": true,
       "strictNullChecks": true
     }
   }
   ```

### 分类5: 类型不匹配错误

**症状**:
```
error TS2322: Type 'XXX' is not assignable to type 'YYY'
error TS2345: Argument of type 'XXX' is not assignable to parameter of type 'YYY'
```

**排查步骤**:

1. **查看类型定义**
   ```bash
   # 查看实际类型
   npm run type-check 2>&1 | grep -A 5 "TS2322"

   # 使用IDE查看类型
   # VS Code: Ctrl+Click (Mac: Cmd+Click) 跳转到定义
   ```

2. **使用类型断言**
   ```typescript
   // ❌ 直接赋值
   const value: string = someValue  // Type 'number' is not assignable

   // ✅ 类型断言
   const value = someValue as string

   // ✅ 类型守卫
   if (typeof someValue === 'string') {
     const value: string = someValue
   }
   ```

3. **添加类型转换**
   ```typescript
   // ✅ 使用适配器转换
   const strategy = StrategyAdapter.adaptFromAPI(apiData)

   // ✅ 使用工厂函数
   const result = Result.success(data)
   ```

---

## 💻 20种错误代码详解

### TS2304: Cannot find name 'XXX'

**含义**: 找不到名称XXX的定义

**常见原因**:
1. 缺少类型定义
2. 命名空间导入错误
3. 作用域问题

**解决方案**:
```typescript
// 原因1: 缺少类型定义
// ✅ 添加类型定义
export type Dict = Record<string, any>;

// 原因2: 导入错误
// ❌ import { DataTypes } from 'sequelize-typescript'
// ✅ import { DataTypes } from 'sequelize'

// 原因3: 使用this前未初始化
// ✅ 确保类属性已声明
class MyClass {
  private value: number = 0  // 声明并初始化
}
```

### TS2305: has no exported member 'XXX'

**含义**: 模块中没有导出成员XXX

**常见原因**:
1. 导入路径错误
2. 成员未导出
3. 模块名称拼写错误

**解决方案**:
```typescript
// 原因1: 导入路径错误
// ❌ import { Strategy } from '@/types/strategy'
// ✅ import { Strategy } from '@/api/types/strategy'

// 原因2: 成员未导出
// ❌ export interface Strategy { /* ... */ }
//    export { StrategyAPI }  // Strategy未导出

// ✅ 添加导出
export interface Strategy { /* ... */ }
export { Strategy }

// 原因3: 拼写错误
// ❌ import { Stratagy } from './strategy'
// ✅ import { Strategy } from './strategy'
```

### TS2307: Cannot find module '@/types/XXX'

**含义**: 找不到模块文件

**常见原因**:
1. 文件路径错误
2. 文件扩展名错误
3. TypeScript配置错误

**解决方案**:
```typescript
// 原因1: 路径错误
// ❌ import { User } from '@/types/user'
// ✅ import { User } from '@/api/types/user'

// 原因2: 文件扩展名
// ❌ import { utils } from './utils'
// ✅ import { utils } from './utils.ts'

// 原因3: tsconfig.json路径别名
// ✅ 确保正确配置
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

### TS2339: Property 'XXX' does not exist on type 'YYY'

**含义**: 类型YYY上不存在属性XXX

**常见原因**:
1. 属性名拼写错误
2. 类型定义不完整
3. 动态属性未声明

**解决方案**:
```typescript
// 原因1: 拼写错误
// ❌ const name = user.nmae  // nmae拼写错误
// ✅ const name = user.name

// 原因2: 类型不完整
interface User {
  id: string
  name: string
  // ❌ 缺少email属性
}

// ✅ 添加缺失属性
interface User {
  id: string
  name: string
  email?: string
}

// 原因3: 动态属性
// ✅ 使用索引签名
interface DynamicObject {
  [key: string]: any
}

// ✅ 使用Record类型
type Dict = Record<string, any>
```

### TS2345: Argument of type 'XXX' is not assignable to parameter of type 'YYY'

**含义**: 参数类型不匹配

**常见原因**:
1. 参数类型错误
2. 缺少类型转换
3. 函数签名不匹配

**解决方案**:
```typescript
// 原因1: 类型不匹配
function processUser(user: User) { /* ... */ }

// ❌ processUser({ name: 'John' })  // 缺少id
// ✅ processUser({ id: '1', name: 'John' })

// 原因2: 需要类型转换
const data: any = apiResponse

// ✅ 使用类型断言
processUser(data as User)

// ✅ 使用类型守卫
if (isUser(data)) {
  processUser(data)
}

// 原因3: 可选参数
function greet(name: string, greeting?: string) {
  return `${greeting || 'Hello'}, ${name}`
}

// ✅ 正确调用
greet('John')  // 使用默认greeting
greet('John', 'Hi')  // 提供greeting
```

### TS2322: Type 'XXX' is not assignable to type 'YYY'

**含义**: 类型不兼容

**常见原因**:
1. 赋值类型不匹配
2. 接口属性不兼容
3. 泛型约束不满足

**解决方案**:
```typescript
// 原因1: 基本类型不兼容
let count: number = 0

// ❌ count = "123"  // string不能赋值给number
// ✅ count = Number("123")
// ✅ count = parseInt("123")

// 原因2: 接口不兼容
interface User {
  id: string
  name: string
}

interface APIUser {
  id: number  // 类型不同
  name: string
  email: string
}

// ✅ 使用适配器转换
function adaptUser(apiUser: APIUser): User {
  return {
    id: String(apiUser.id),
    name: apiUser.name
  }
}

// 原因3: 可选属性
interface Config {
  required: string
  optional?: number
}

// ✅ 满足约束
const config1: Config = { required: 'value' }
const config2: Config = { required: 'value', optional: 123 }
```

### TS2532: Object is possibly 'undefined'

**含义**: 对象可能为undefined

**常见原因**:
1. 可选属性访问
2. 数组越界访问
3. 条件分支未覆盖

**解决方案**:
```typescript
// 原因1: 可选属性
interface Data {
  items?: Item[]
}

const data: Data = {}

// ❌ const first = data.items[0]  // items可能undefined
// ✅ 使用可选链
const first = data.items?.[0]
// ✅ 使用非空断言（确定不为空时）
const first = data.items![0]
// ✅ 使用条件检查
if (data.items && data.items.length > 0) {
  const first = data.items[0]
}

// 原因2: 数组访问
const arr: string[] = []

// ❌ const first = arr[0]  // 可能undefined
// ✅ 使用可选链
const first = arr[0]
// ✅ 使用类型守卫
if (arr.length > 0) {
  const first = arr[0]
}

// 原因3: 函数返回值
function findUser(id: string): User | undefined {
  return users.find(u => u.id === id)
}

// ✅ 处理undefined情况
const user = findUser('123')
if (user) {
  console.log(user.name)
}
```

### TS2533: Object is possibly 'null'

**含义**: 对象可能为null

**常见原因**:
1. 未初始化的对象
2. 可能返回null的函数
3. 联合类型包含null

**解决方案**:
```typescript
// 原因1: 未初始化
let user: User | null = null

// ❌ console.log(user.name)  // user可能null
// ✅ 使用可选链
console.log(user?.name)
// ✅ 使用条件检查
if (user) {
  console.log(user.name)
}
// ✅ 使用非空断言（确定不为null时）
console.log(user!.name)

// 原因2: 函数返回null
function getUser(): User | null {
  return Math.random() > 0.5 ? user : null
}

// ✅ 处理null情况
const user = getUser()
if (user !== null) {
  console.log(user.name)
}

// ✅ 使用nullish coalescing
const name = user?.name ?? 'Unknown'
```

### TS7006: Parameter 'XXX' implicitly has an 'any' type

**含义**: 参数XXX隐式具有any类型

**常见原因**:
1. 函数参数缺少类型注解
2. 回调函数未定义类型
3. 解构参数未定义类型

**解决方案**:
```typescript
// 原因1: 参数缺少类型
// ❌ const add = (a, b) => a + b
// ✅ const add = (a: number, b: number) => a + b

// 原因2: 回调函数
// ❌ items.map(item => item.value)
// ✅ items.map((item: any) => item.value)
// ✅ 使用接口
interface Item { value: number }
// ✅ items.map((item: Item) => item.value)

// 原因3: 解构参数
// ❌ const fn = ({ name, age }) => { /* ... */ }
// ✅ const fn = ({ name, age }: { name: string; age: number }) => { /* ... */ }
// ✅ 使用接口
interface Params {
  name: string
  age: number
}
// ✅ const fn = ({ name, age }: Params) => { /* ... */ }
```

### TS7008: Member 'XXX' implicitly has an 'any' type

**含义**: 成员XXX隐式具有any类型

**常见原因**:
1. 类属性缺少类型
2. 对象属性未定义
3. 模块导出未定义类型

**解决方案**:
```typescript
// 原因1: 类属性
class User {
  // ❌ name  // 隐式any
  // ✅ name: string
  // ✅ name!: string  // 确定会被初始化
}

// 原因2: 对象属性
// ❌ const obj = { name: 'John', age: 30 }  // 类型被推断
// ✅ const obj: { name: string; age: number } = { name: 'John', age: 30 }
// ✅ 使用interface
interface Person {
  name: string
  age: number
}
// ✅ const obj: Person = { name: 'John', age: 30 }

// 原因3: 模块导出
// ❌ export const config = { /* ... */ }
// ✅ export const config: Config = { /* ... */ }
```

### TS6133: 'XXX' is declared but its value is never read

**含义**: 变量XXX已声明但从未使用

**常见原因**:
1. 未使用的导入
2. 未使用的变量
3. 调试代码遗留

**解决方案**:
```typescript
// 原因1: 未使用的导入
// ❌ import { UserService, Logger } from './services'
// ✅ import { UserService } from './services'
// ✅ import { Logger } from './services'  // 如果确实使用

// 原因2: 未使用的变量
// ❌ const data = fetchData()
//     console.log('done')
// ✅ const data = fetchData()
//     console.log(data)

// 原因3: 下划线前缀
// ✅ const _unused = getSomeValue()
// ✅ function process(_data: any) { /* ... */ }
```

### TS2484: Export declaration conflicts with exported declaration

**含义**: 导出声明与已导出的声明冲突

**常见原因**:
1. 重复导出
2. 类型和值重复导出
3. 文件末尾批量导出

**解决方案**:
```typescript
// ❌ 错误: 重复导出
export interface ChartTheme { /* ... */ }
export type { ChartTheme }  // 冲突

// ✅ 解决: 删除重复导出
export interface ChartTheme { /* ... */ }
// 已在定义时导出，无需重复

// ❌ 错误: 文件末尾批量导出
export interface Type1 { /* ... */ }
export interface Type2 { /* ... */ }
// ... 其他类型
export type {
  Type1,
  Type2,
  // ... 所有类型
}

// ✅ 解决: 删除文件末尾的export type块
// 所有类型已在定义时使用export导出
```

### TS2614: Module has no exported member 'XXX' or it was exported as 'default'

**含义**: 模块没有导出成员XXX或作为默认导出

**常见原因**:
1. 命名导出和默认导出混淆
2. 导入方式不匹配
3. 导出方式错误

**解决方案**:
```typescript
// 原因1: 默认导出 vs 命名导出
// utils.ts
// ❌ export default function utils() { /* ... */ }
//    import { utils } from './utils'  // 错误导入

// ✅ export default function utils() { /* ... */ }
//    import utils from './utils'  // 正确导入

// ✅ export function utils() { /* ... */ }
//    import { utils } from './utils'  // 正确导入

// 原因2: 混合导出
// utils.ts
export default function utils() { /* ... */ }
export function helper() { /* ... */ }

// ✅ 正确导入
import utils, { helper } from './utils'

// 原因3: 导出为default但作为命名导入
// component.ts
// ❌ export default { name: 'Component' }
//    import { Component } from './component'

// ✅ export const Component = { name: 'Component' }
//    import { Component } from './component'
```

### TS2740: Type 'XXX' is missing the following properties from type 'YYY'

**含义**: 类型XXX缺少类型YYY的以下属性

**常见原因**:
1. Props缺少必需属性
2. 接口未完全实现
3. 类型不兼容

**解决方案**:
```typescript
// 原因1: Vue组件Props
interface Props {
  label: string  // 必需
  value: number
  variant?: string  // 可选
}

// ❌ <MyComponent value={123} />  // 缺少label
// ✅ <MyComponent label="Count" value={123} />
// ✅ <MyComponent label="Count" value={123} variant="primary" />

// 原因2: 接口实现
interface User {
  id: string
  name: string
  email: string
}

// ❌ const user: User = { id: '1', name: 'John' }  // 缺少email
// ✅ const user: User = { id: '1', name: 'John', email: 'john@example.com' }

// 原因3: 可选属性
interface User {
  id: string
  name: string
  email?: string  // 可选
}

// ✅ const user: User = { id: '1', name: 'John' }  // email可选
```

### TS2352: Conversion of type 'XXX' to type 'YYY' may be a mistake

**含义**: 类型转换可能是错误的

**常见原因**:
1. 不安全的类型断言
2. 双重断言使用
3. 泛型断言错误

**解决方案**:
```typescript
// 原因1: 不安全断言
const value: any = '123'

// ❌ const num: number = value  // 类型不匹配
// ⚠️ const num: number = value as number  // 可能错误
// ✅ const num: number = Number(value)
// ✅ const num: number = parseInt(value)

// 原因2: 双重断言
const obj: object = {}

// ❌ const user = obj as User  // 直接断言可能错误
// ✅ const user = obj as unknown as User  // 双重断言
// ⚠️ 谨慎使用: 确保转换安全性
// ✅ 使用类型守卫
function isUser(obj: any): obj is User {
  return obj && typeof obj.id === 'string' && typeof obj.name === 'string'
}

if (isUser(obj)) {
  const user: User = obj
}

// 原因3: 泛型断言
function identity<T>(arg: T): T {
  return arg
}

// ❌ const result = identity<string>(123)  // 类型不匹配
// ✅ const result = identity<number>(123)
```

---

## ⚡ 性能问题诊断

### 问题1: 类型检查缓慢

**症状**: `npm run type-check` 需要很长时间

**诊断**:
```bash
# 测量类型检查时间
time npm run type-check

# 检查项目规模
find src -name "*.ts" -o -name "*.tsx" -o -name "*.vue" | wc -l

# 查找大文件
find src -name "*.ts" -exec wc -l {} \; | sort -nr | head -10
```

**解决方案**:
```json
// tsconfig.json
{
  "compilerOptions": {
    // 启用增量编译
    "incremental": true,
    "tsBuildInfoFile": ".tsbuildinfo",

    // 排除不必要的文件
    "exclude": [
      "node_modules",
      "dist",
      "**/*.test.ts",
      "**/*.spec.ts"
    ]
  }
}
```

### 问题2: 内存占用过高

**症状**: TypeScript编译器占用大量内存

**诊断**:
```bash
# 检查进程内存使用
ps aux | grep tsc

# 使用Node.js内存限制
NODE_OPTIONS="--max-old-space-size=4096" npm run type-check
```

**解决方案**:
```json
// package.json
{
  "scripts": {
    "type-check": "tsc --noEmit",
    "type-check:mem": "node --max-old-space-size=4096 node_modules/.bin/tsc --noEmit"
  }
}
```

### 问题3: IDE响应缓慢

**症状**: VS Code输入卡顿，类型提示延迟

**诊断**:
```bash
# 检查TypeScript版本
npm list typescript

# 检查VS Code扩展
code --list-extensions | grep -i typescript
```

**解决方案**:

1. **排除不必要的文件**
   ```json
   // tsconfig.json
   {
     "exclude": [
       "node_modules",
       "dist",
       "build",
       "coverage",
       "**/*.test.ts"
     ]
   }
   ```

2. **调整TypeScript服务设置**
   ```json
   // .vscode/settings.json
   {
     "typescript.tsserver.maxTsServerMemory": 4096,
     "typescript.tsserver.watchOptions": {
       "watchFile": "useFsEvents",
       "watchDirectory": "useFsEvents",
       "synchronousWatchDirectory": true
     }
   }
   ```

3. **禁用不必要的扩展**
   - 暂禁用大型项目专用的扩展
   - 只保留必需的TypeScript相关扩展

---

## 🏗️ 构建失败处理

### 问题1: Vite构建失败

**症状**: `npm run build` 失败，显示类型错误

**诊断**:
```bash
# 查看完整构建日志
npm run build 2>&1 | tee build.log

# 检查构建配置
cat vite.config.mts | grep -A 10 "build:"
```

**解决方案**:
```typescript
// vite.config.mts
export default defineConfig({
  build: {
    // 禁用构建时的类型检查（推荐在CI中单独检查）
    // @ts-ignore
    terserOptions: {
      compress: {
        drop_console: true
      }
    }
  }
})
```

### 问题2: 类型检查通过但构建失败

**症状**: `npm run type-check` 通过，但`npm run build` 失败

**诊断**:
```bash
# 运行vue-tsc完整检查
npm run type-check:vue

# 检查Vue组件
find src -name "*.vue" -exec echo "Checking: {}" \;
```

**解决方案**:
```bash
# 使用vue-tsc替代tsc
npm run type-check:vue

# 修复Vue组件类型错误
# 1. 检查Props定义
# 2. 检查Emits定义
# 3. 检查组件引用
```

### 问题3: 第三方库类型错误

**症状**: `node_modules`中的类型定义错误

**诊断**:
```bash
# 检查类型定义包
npm list @types/* --depth=0

# 查找类型定义位置
find node_modules -name "*.d.ts" | grep <package-name>
```

**解决方案**:

1. **安装类型定义**
   ```bash
   npm install --save-dev @types/<package-name>
   ```

2. **创建项目级类型声明**
   ```typescript
   // src/types/third-party.d.ts
   declare module 'missing-package' {
     export interface API {
       method(): void
     }
   }
   ```

3. **忽略类型检查（最后手段）**
   ```typescript
   // tsconfig.json
   {
     "compilerOptions": {
       "skipLibCheck": true  // 跳过.d.ts文件检查
     }
   }
   ```

---

## 🎨 IDE问题解决

### 问题1: VS Code不显示错误

**症状**: 代码有错误但VS Code没有显示

**诊断**:
```bash
# 检查TypeScript扩展
code --list-extensions | grep -i typescript

# 检查工作区设置
cat .vscode/settings.json | grep typescript
```

**解决方案**:

1. **重启TypeScript服务器**
   - VS Code: Command Palette (Ctrl+Shift+P)
   - 输入: "TypeScript: Restart TS Server"

2. **检查TypeScript版本**
   ```json
   // .vscode/settings.json
   {
     "typescript.tsdk": "node_modules/typescript/lib"
   }
   ```

3. **清除缓存**
   ```bash
   # 删除.tscache
   rm -rf .tscache
   rm -rf .tsbuildinfo
   ```

### 问题2: 自动导入不工作

**症状**: 输入代码时没有自动导入提示

**诊断**:
```json
// .vscode/settings.json
{
  "typescript.suggest.autoImports": true,
  "typescript.preferences.includePackageJsonAutoImports": "auto"
}
```

**解决方案**:

1. **启用自动导入**
   ```json
   {
     "editor.codeActionsOnSave": {
       "source.fixAll.eslint": true
     }
   }
   ```

2. **配置路径映射**
   ```json
   // tsconfig.json
   {
     "compilerOptions": {
       "baseUrl": ".",
       "paths": {
         "@/*": ["src/*"]
       }
     }
   }
   ```

### 问题3: IntelliSense不工作

**症状**: 没有代码提示、类型信息不显示

**诊断**:
```bash
# 检查TypeScript服务器状态
# VS Code Output > TypeScript
```

**解决方案**:

1. **检查文件是否在索引中**
   ```json
   // .vscode/settings.json
   {
     "files.exclude": {
       "**/node_modules": true,
       "**/dist": true
     }
   }
   ```

2. **启用严格的类型检查**
   ```json
   // tsconfig.json
   {
     "compilerOptions": {
       "strict": true
     }
   }
   ```

---

## 🔬 高级诊断技巧

### 技巧1: 使用TypeScript编译器API

```typescript
// diagnostic-tool.ts
import ts from 'typescript'

const program = ts.createProgram(['src/index.ts'], {
  strict: true
})

const diagnostics = ts.getPreEmitDiagnostics(program)

diagnostics.forEach(diagnostic => {
  const message = ts.flattenDiagnosticMessageText(diagnostic.messageText, '\n')
  const { line, character } = diagnostic.file!.getLineAndCharacterOfPosition(diagnostic.start!)
  console.log(`${diagnostic.file!.fileName} (${line + 1},${character + 1}): ${message}`)
})
```

### 技巧2: 使用tsc的--traceResolution

```bash
# 追踪模块解析过程
npx tsc --traceResolution --noEmit

# 输出所有模块解析信息
npx tsc --listFiles --noEmit
```

### 技巧3: 使用--explainFiles

```bash
# 解释为什么文件被包含在编译中
npx tsc --explainFiles --noEmit
```

### 技巧4: 分析类型检查性能

```bash
# 生成性能报告
npx tsc --extendedDiagnostics --noEmit

# 输出示例:
# Files: 500
# Lines: 150000
# Identifiers: 500000
# Symbols: 250000
# Types: 100000
# Instantiations: 50000
# Memory used: 500MB
# I/O time: 2s
# Parse time: 5s
// ...
```

---

## 📚 相关文档

### 快速参考
- 📖 [TypeScript快速开始](./Typescript_QUICKSTART.md)
- 📖 [TypeScript最佳实践](./Typescript_BEST_PRACTICES.md)

### 深入学习
- 📖 [TypeScript配置参考](./Typescript_CONFIG_REFERENCE.md)
- 📖 [TypeScript新手培训](./Typescript_TRAINING_BEGINNER.md)
- 📖 [TypeScript高级培训](./Typescript_TRAINING_ADVANCED.md)

### 历史经验
- 📊 [TypeScript修复案例研究](../reports/TYPESCRIPT_FIX_BEST_PRACTICES.md)
- 📊 [TypeScript技术债务管理](../reports/TYPESCRIPT_TECHNICAL_DEBTS.md)

---

**文档维护**: 本文档应随新错误模式发现持续更新
**最后更新**: 2026-01-20
**维护者**: Main CLI (Claude Code)
**版本**: v1.0
