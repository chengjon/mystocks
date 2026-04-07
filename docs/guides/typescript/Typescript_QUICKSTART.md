# TypeScript 快速开始指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**版本**: v1.0 | **更新时间**: 2026-01-20 | **阅读时间**: 5分钟

> 本指南帮助你在5分钟内掌握MyStocks项目的TypeScript类型检查、错误修复和最佳实践。

---

## 🎯 30秒速查

### 最常用命令

```bash
# 类型检查（本地开发）
npm run type-check              # tsc快速检查
npm run type-check:vue          # vue-tsc完整检查

# 修复类型错误
npm run generate-types          # 重新生成类型（源头修复）
npm run lint -- --fix           # ESLint自动修复

# 验证修复
npm run type-check && npm run build  # 检查+构建验证
```

### 错误修复优先级

| 优先级 | 错误类型 | 修复策略 | 预计时间 |
|-------|---------|---------|---------|
| **P0** | 类型导入错误 | 修复生成脚本 | 30分钟 |
| **P1** | 重复导出冲突 | 删除重复声明 | 3分钟/文件 |
| **P2** | 隐式any类型 | 添加类型注解 | 2分钟/文件 |

---

## 🚀 快速诊断流程

### Step 1: 运行类型检查

```bash
# 完整类型检查（包含Vue组件）
npm run type-check:vue

# 输出示例:
# src/api/strategy.ts:10:5 - error TS2305: has no exported member 'Strategy'
# src/components/MyComponent.vue:25:3 - error TS2532: Object is possibly 'undefined'
```

### Step 2: 统计错误分布

```bash
# 统计错误类型
npm run type-check 2>&1 | grep "error TS" | sed 's/.*error TS[0-9]*: //' | sort | uniq -c | sort -nr

# 输出示例:
#  28 Export declaration conflicts with exported declaration
#  13 Parameter implicitly has an 'any' type
#   8 Property 'label' is missing
```

### Step 3: 选择修复策略

根据错误类型选择策略:

**重复导出 (TS2484)** → 删除文件末尾的`export type { ... }`
```typescript
// ❌ 错误
export interface ChartTheme { /* ... */ }
export type { ChartTheme }  // 重复导出

// ✅ 修复
export interface ChartTheme { /* ... */ }  // 已在定义时导出
```

**隐式any (TS7006)** → 添加类型注解
```typescript
// ❌ 错误
const handleData = (data) => { return data.value }

// ✅ 修复
const handleData = (data: any) => { return data.value }
```

**类型缺失 (TS2532)** → 使用可选链
```typescript
// ❌ 错误
const name = data.items[0].name

// ✅ 修复
const name = data.items[0]?.name
```

---

## 🔧 常见错误快速修复

### 错误1: 重复导出声明 (最常见)

**错误代码**: `TS2484: Export declaration conflicts with exported declaration`

**症状**: 文件末尾有`export type { ... }`批量导出

**快速修复**:
```bash
# 批量删除重复导出声明
find src -name "*.ts" -exec perl -i -pe 's/^export type \{[^}*\};$//s' {} \;
```

**手动修复**:
```typescript
// 删除文件末尾的重复导出部分（约39行）
// 所有类型已在定义时使用 export 关键字导出
```

### 错误2: 导入路径错误

**错误代码**: `TS2307: Cannot find module '@/types/xxx'`

**快速修复**:
```bash
# 查找正确的导入路径
grep -r "export.*xxx" src/ --include="*.ts"

# 修正导入路径
# ❌ import { Strategy } from '@/types/strategy'
# ✅ import { Strategy } from '@/api/types/strategy'
```

### 错误3: 缺少组件Props

**错误代码**: `TS2740: Property 'label' is missing`

**症状**: ArtDeco组件缺少必需的`label`属性

**快速修复**:
```vue
<!-- ❌ 错误 -->
<ArtDecoStatCard title="统计" :value="123" />

<!-- ✅ 修复 -->
<ArtDecoStatCard label="统计" :value="123" />
```

### 错误4: 隐式any类型

**错误代码**: `TS7006: Parameter 'x' implicitly has an 'any' type`

**快速修复**:
```bash
# 批量添加类型注解（使用Perl）
perl -i -pe 's/\.map\((\w+)\s*=>/\.map(($1: any) =>/g' src/**/*.vue
perl -i -pe 's/\.forEach\((\w+)\s*=>/\.forEach(($1: any) =>/g' src/**/*.vue
```

### 错误5: 回调函数类型缺失

**错误代码**: `TS7006: Parameter 'callback' implicitly has an 'any' type`

**快速修复**:
```typescript
// ❌ 错误
items.map(item => item.value)

// ✅ 修复
items.map((item: any) => item.value)

// 更好的做法：定义接口
interface Item { value: number }
items.map((item: Item) => item.value)
```

---

## 📊 从源头修复类型生成

### 问题根源: 自动生成的类型文件有错误

**症状**:
- `src/api/types/generated-types.ts` 有大量错误
- 修改后会自动重新生成（每次运行`npm run generate-types`）

### 正确的修复方法

**步骤1**: 修复生成脚本
```bash
# 编辑生成脚本
vi scripts/generate_frontend_types.py
```

**步骤2**: 常见修复点
```python
# 修复1: 移除重复导出（第519-524行）
def generate_index_file(domains: List[str]) -> str:
    # ❌ 删除这部分重复导出
    # if 'common.ts' in domain_files:
    #     lines.append("export * from './common';")

    # ✅ 统一在循环中导出
    for domain in sorted(domains):
        domain_file = OUTPUT_DIR / f"{domain}.ts"
        if domain_file.exists():
            lines.append(f"export * from './{domain}';")

# 修复2: 处理 list[...] 类型
if "list[" in type_str:
    type_str = type_str.replace("list[", "").replace("]", "[]")
    # list[str] → str[], list[int] → int[]

# 修复3: 添加 date_type 映射
TYPE_MAP = {
    # ... 其他映射
    'date_type': 'string',  # 日期类型映射为字符串
}
```

**步骤3**: 重新生成类型
```bash
# 重新生成
npm run generate-types

# 验证修复
npm run type-check
```

### 详细文档
- 📖 [TypeScript源头修复完整指南](./TYPESCRIPT_SOURCE_FIX_GUIDE.md)
- 📖 [TypeScript错误快速修复指南](./TYPESCRIPT_ERROR_FIXING_GUIDE.md)

---

## 🛡️ 类型安全最佳实践

### 1. 接口设计原则

```typescript
// ✅ 推荐: 使用可选属性
interface APIResponse<T = any> {
  success: boolean
  data?: T              // 可选，避免频繁错误
  message?: string
  timestamp: string
}

// ❌ 避免: 所有属性必填
interface APIResponse<T = any> {
  success: boolean
  data: T               // 必填，容易导致错误
  message: string       // 必填，经常为空
}
```

### 2. 适配器模式应用

```typescript
// ✅ 推荐: 使用适配器统一转换
class StrategyAdapter {
  static adaptFromAPI(apiData: any): Strategy {
    return {
      id: apiData.id || '',
      name: apiData.name || 'Unnamed',
      created_at: apiData.created_at || apiData.createdAt || '',
      performance: apiData.performance ? this.adaptPerformance(apiData.performance) : undefined
    }
  }
}
```

### 3. 类型守卫使用

```typescript
// ✅ 推荐: 类型守卫确保运行时安全
function isStrategy(obj: any): obj is Strategy {
  return obj &&
         typeof obj.id === 'string' &&
         typeof obj.name === 'string' &&
         typeof obj.created_at === 'string'
}

function processStrategy(data: unknown): Strategy | null {
  if (isStrategy(data)) {
    return data
  }
  console.warn('Invalid strategy data:', data)
  return null
}
```

### 4. Vue 3组件Props类型

```typescript
// ✅ 推荐: 定义Props接口
interface Props {
  label: string
  value: number | string
  change?: number
}

const props = defineProps<Props>()

// ✅ 推荐: 定义Emits类型
const emit = defineEmits<{
  click: [value: number]
  change: [newValue: number]
}>()
```

---

## ⚡ 批量修复工具

### Perl脚本（最快速）

```bash
# 批量删除重复导出
find src -name "*.ts" -exec perl -i -pe 's/^export type \{[^}*\};$//s' {} \;

# 批量添加回调类型注解
find src -name "*.vue" -exec perl -i -pe '
  s/\.map\((\w+)\s*=>/\.map(($1: any) =>/g;
  s/\.forEach\((\w+)\s*=>/\.forEach(($1: any) =>/g;
' {} \;
```

### ESLint自动修复

```bash
# 自动修复可修复的问题
npm run lint -- --fix

# 自动修复范围:
# - 缺失的分号
# - 未使用的变量
# - 引号不一致
# - 简单的类型问题
```

---

## 📈 CI/CD质量门禁

### GitHub Actions工作流

```yaml
# .github/workflows/typescript-type-check.yml

# 阶段1: tsc快速检查
- name: Run TypeScript compiler (tsc)
  run: npx tsc --noEmit

# 阶段2: vue-tsc完整检查（智能过滤）
- name: Run vue-tsc (full check)
  run: npx vue-tsc --noEmit --force

# 阶段3: ESLint检查
- name: Run ESLint
  run: npx eslint src --ext .ts,.tsx,.vue

# 阶段4: 类型覆盖率分析
- name: Analyze type coverage
  run: python scripts/analyze_type_coverage.py

# 阶段5: 质量门禁评估
- name: Evaluate quality gate
  run: |
    ERROR_COUNT=$(cat vue-tsc-filtered.txt | wc -l)
    if [ "$ERROR_COUNT" -gt 40 ]; then
      echo "❌ 类型错误超过阈值: $ERROR_COUNT > 40"
      exit 1
    fi
```

### 质量门禁阈值

| 检查项 | 阈值 | 失败条件 |
|-------|------|---------|
| TypeScript错误 | 40个 | 超过40个错误 |
| ESLint问题 | 100个 | 超过100个问题 |
| 类型覆盖率 | 85% | 低于85% |

---

## 🎓 进阶学习路径

### 初学者路径（第1周）

1. ✅ 阅读本快速指南
2. ✅ 熟悉常用命令（type-check, generate-types）
3. ✅ 掌握5种常见错误修复
4. ✅ 了解从源头修复的方法

### 进阶路径（第2-4周）

1. 📖 阅读[TypeScript最佳实践](./Typescript_BEST_PRACTICES.md)
2. 📖 学习[TypeScript配置参考](./Typescript_CONFIG_REFERENCE.md)
3. 📖 掌握[故障排除指南](./Typescript_TROUBLESHOOTING.md)
4. 🔧 实践: 修复10个真实错误

### 高级路径（2-3个月）

1. 📖 研究[TypeScript技术债务管理](../reports/TYPESCRIPT_TECHNICAL_DEBTS.md)
2. 📖 学习[事前预防系统设计](../architecture/typescript_prevention_system.md)
3. 📖 理解[事中监控系统设计](../architecture/typescript_monitoring_system.md)
4. 🏗️ 参与: 完善项目的类型检查基础设施

---

## 📚 相关文档

### 核心指南
- 📖 [TypeScript最佳实践](./Typescript_BEST_PRACTICES.md)
- 📖 [TypeScript配置参考](./Typescript_CONFIG_REFERENCE.md)
- 📖 [TypeScript故障排除](./Typescript_TROUBLESHOOTING.md)

### 培训文档
- 📖 [TypeScript新手培训](./Typescript_TRAINING_BEGINNER.md)
- 📖 [TypeScript高级培训](./Typescript_TRAINING_ADVANCED.md)

### 架构设计
- 📖 [事前预防系统设计](../architecture/typescript_prevention_system.md)
- 📖 [事中监控系统设计](../architecture/typescript_monitoring_system.md)
- 📖 [事后验证系统设计](../architecture/typescript_hooks_system.md)

### 历史文档
- 📊 [TypeScript修复案例研究](../reports/TYPESCRIPT_FIX_BEST_PRACTICES.md)
- 📊 [TypeScript技术债务管理](../reports/TYPESCRIPT_TECHNICAL_DEBTS.md)

---

## 💡 快速提示

### ⚠️ 避免的陷阱

1. **不要手动修改 `generated-types.ts`**
   - ❌ 直接编辑会丢失（下次生成时覆盖）
   - ✅ 修复 `generate_frontend_types.py` 脚本

2. **不要删除代码，要注释**
   - ❌ `const data = []`  // 删除了类型
   - ✅ `// const data: SomeType[] = []`  // 保留类型信息

3. **不要过度使用 `any`**
   - ❌ 所有类型都用 `any`
   - ✅ 优先定义接口，必要时用 `any`

### ✅ 推荐做法

1. **批量处理相同错误**
   - 使用脚本一次性修复所有相同模式错误
   - 例如: 所有重复导出、所有回调函数类型

2. **从源头修复**
   - 优先修复生成脚本，而非手动修改生成文件
   - 一次修复，永久生效

3. **遵循最小修改原则**
   - 只修复类型错误，不改变业务逻辑
   - 保持向后兼容性

---

## 🆘 获取帮助

### 遇到问题时

1. **查看错误信息**: 阅读完整的TypeScript错误消息
2. **搜索修复案例**: 查看 [TYPESCRIPT_FIX_BEST_PRACTICES.md](../reports/TYPESCRIPT_FIX_BEST_PRACTICES.md)
3. **查阅故障排除**: 参考 [Typescript_TROUBLESHOOTING.md](./Typescript_TROUBLESHOOTING.md)
4. **询问团队**: 在团队频道提问，附上错误信息

### 报告问题

发现新的错误模式或修复方法时，请更新文档并分享给团队。

---

**文档维护**: 本文档应随项目TypeScript配置更新而持续更新。
**最后更新**: 2026-01-20
**维护者**: Main CLI (Claude Code)
**版本**: v1.0
