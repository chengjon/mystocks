# TypeScript 修复最佳实践

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


> **用途**: 实战修复指南，快速解决 TypeScript 错误
> **更新**: 2026-02-15 | **项目**: MyStocks (Vue 3 + TypeScript)

---

## 🎯 修复三原则

1. **最小修改**: 只改必要的，不顺手重构
2. **显式优于隐式**: `(param: any)` 好于隐式 any
3. **验证即时**: 每次修复后立即 `npx tsc --noEmit`

---

## 🔧 7种核心错误模式

### 模式1: 类型转换优化
**错误码**: 无特定错误码，属于代码优化
**场景**: 不必要的 `as unknown` 转换

```typescript
// ❌ 错误
<el-tag :type="getValue() as unknown" />

// ✅ 正确
<el-tag :type="getValue()" />
```

---

### 模式2: 接口属性必填化
**错误码**: TS2322 (Type 'X' is not assignable to type 'Y')
**场景**: 可选属性 `?` 导致类型不匹配

```typescript
// ❌ 错误: 属性可能为 undefined
interface Item { price?: number }

// ✅ 正确: 明确必填
interface Item { price: number }
```

**判断标准**: 如果属性在所有使用场景中都必须存在，设为必填

---

### 模式3: 参数类型注解
**错误码**: TS7006 (Parameter implicitly has 'any' type)
**场景**: 函数参数缺少类型注解

```typescript
// ❌ 错误
const handler = (data) => { }

// ✅ 正确
const handler = (data: Record<string, any>): void => { }
```

**批量修复**:
```bash
perl -i -pe 's/\.map\((\w+)\s*=>/.map(($1: any) =>/g' **/*.ts
```

---

### 模式4: 错误对象处理
**错误码**: TS2339 (Property does not exist on type 'unknown')
**场景**: catch 中的 error 是 unknown 类型

```typescript
// ❌ 错误
catch (error: unknown) {
  console.log(error.message)  // 编译错误
}

// ✅ 正确
catch (error: unknown) {
  const err = error as Record<string, any>
  console.log(err?.message || 'Unknown error')
}
```

---

### 模式5: API响应转换
**错误码**: TS2345 (Argument of type 'unknown' is not assignable)
**场景**: API 返回 unknown 类型

```typescript
// ❌ 错误
const data = await api.get('/endpoint')
return adapter.transform(data)  // data 是 unknown

// ✅ 正确
const data = await api.get('/endpoint')
return adapter.transform(data as Record<string, unknown>)
```

---

### 模式6: 缺失类实现
**错误码**: TS2304 (Cannot find name 'X')
**场景**: 引用未定义的类

```typescript
// ❌ 错误
const instance = MyClass.getInstance()  // MyClass 未定义

// ✅ 正确: 创建最小实现
class MyClass {
  private static instance: MyClass
  static getInstance(): MyClass {
    if (!MyClass.instance) MyClass.instance = new MyClass()
    return MyClass.instance
  }
}
```

---

### 模式7: 类型定义补充
**错误码**: TS2304 (Cannot find name 'X')
**场景**: 使用未定义的类型别名

```typescript
// ❌ 错误
interface Contract { type: SignalType }  // SignalType 未定义

// ✅ 正确
type SignalType = 'buy' | 'sell' | 'hold'
interface Contract { type: SignalType }
```

---

## 📊 修复效率参考

| 模式 | 平均耗时 | 复杂度 | 可批量 |
|------|---------|--------|--------|
| 类型转换优化 | 2分钟 | ⭐ | ✅ |
| 接口属性必填化 | 3分钟 | ⭐ | ✅ |
| 参数类型注解 | 2分钟 | ⭐ | ✅ |
| 错误对象处理 | 3分钟 | ⭐⭐ | ✅ |
| API响应转换 | 4分钟 | ⭐⭐ | ✅ |
| 缺失类实现 | 8分钟 | ⭐⭐ | ❌ |
| 类型定义补充 | 5分钟 | ⭐⭐ | ❌ |

---

## 🛠️ 常用命令

```bash
# 类型检查
npx tsc --noEmit

# 统计错误分布
npx tsc --noEmit 2>&1 | grep "error TS" | \
  sed 's/.*error \(TS[0-9]*\).*/\1/' | sort | uniq -c | sort -rn

# 查找特定错误
npx tsc --noEmit 2>&1 | grep "TS7006"  # 隐式any
npx tsc --noEmit 2>&1 | grep "TS2339"  # 属性不存在
```

---

## 📋 修复检查清单

### 修复前
- [ ] 运行 `npx tsc --noEmit` 获取错误基线
- [ ] 识别错误模式（参考上方7种模式）
- [ ] 评估优先级：P0(阻塞) > P1(核心) > P2(可延后)

### 修复中
- [ ] 每次修复后立即验证
- [ ] 遵循最小修改原则
- [ ] 记录无法立即修复的债务

### 修复后
- [ ] `npx tsc --noEmit` 验证
- [ ] `npm run build` 构建成功
- [ ] 更新技术债务文档

---

## 💡 类型安全最佳实践

### 类型转换原则
```typescript
// ✅ 推荐: 最小必要转换
const data = response as Record<string, unknown>

// ⚠️ 可接受: 双重转换用于复杂类型
const data = response as unknown as ComplexType

// ❌ 避免: 无意义转换
const data = response as unknown
```

### 接口设计原则
```typescript
// ✅ 推荐: 必填与可选分离
interface Config {
  required: string
  optional?: string
}

// ❌ 避免: 全部可选导致混淆
interface Config {
  id?: string
  name?: string
  value?: number
}
```

### 错误处理原则
```typescript
// ✅ 推荐: 类型安全的错误处理
try {
  // ...
} catch (error: unknown) {
  const err = error as Record<string, any>
  const message = err?.message || 'Unknown error'
}
```

---

## 📚 相关文档

| 文档 | 用途 |
|------|------|
| [TYPESCRIPT_DOCUMENTATION_INDEX.md](./TYPESCRIPT_DOCUMENTATION_INDEX.md) | 快速定位修复方法 |
| [TYPESCRIPT_TECHNICAL_DEBT_MANAGEMENT.md](./TYPESCRIPT_TECHNICAL_DEBT_MANAGEMENT.md) | 债务管理策略 |
| [TYPESCRIPT_TECHNICAL_DEBTS.md](./TYPESCRIPT_TECHNICAL_DEBTS.md) | 当前债务清单 |

---

## 📈 项目进度

```
错误数趋势:
2026-01-13: 1160 ━━━━━━━━━━━━━━━━━━━━ 初始
2026-01-15:  160 ━━━━                 86% ↓
2026-02-01:  624 ━━━━━━━━━━━━         新增发现
2026-02-15:  223 ━━━━━━               64% ↓ 当前
目标:        <100 ━━                  基线
```

---

**维护**: 开发团队 | **版本**: v3.0
