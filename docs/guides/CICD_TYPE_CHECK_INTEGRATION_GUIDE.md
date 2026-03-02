# CI/CD 类型检查集成指南

本文档说明如何在 MyStocks 项目的 CI/CD 流程中使用 Python (mypy) 和 TypeScript (vue-tsc) 类型检查。

> 2026-03 说明：前端 E2E 任务默认使用 `web/frontend/playwright.config.js`（`tests/e2e`）。  
> CI 中如需执行标准浏览器链路，请使用 `cd web/frontend && npm run test:e2e`，不要直接运行未指定配置的 `playwright test`。

---

## 📋 目录

1. [概览](#概览)
2. [Python 类型检查 (mypy)](#python-类型检查-mypy)
3. [TypeScript 类型检查 (vue-tsc)](#typescript-类型检查-vue-tsc)
4. [本地开发工作流](#本地开发工作流)
5. [CI/CD 集成策略](#ci-cd-集成策略)
6. [常见问题](#常见问题)

---

## 概览

### 类型检查的重要性

**早期发现错误**: 类型检查在编译时发现错误，而不是运行时
**提升代码质量**: 强制使用类型注解，使代码更易维护
**更好的 IDE 支持**: 自动补全、重构、导航等功能更准确

### CI/CD 集成策略

| 阶段 | Python (mypy) | TypeScript (vue-tsc) |
|------|--------------|---------------------|
| **增量检查** | ✅ 快速反馈（仅检查变更文件） | ✅ 快速反馈（tsc 仅检查 .ts） |
| **完整检查** | ✅ 全面检查（包含测试） | ✅ 全面检查（包含 .vue 文件） |
| **质量门禁** | ✅ 阈值控制（50 错误） | ✅ 阈值控制（40 错误） |
| **覆盖率分析** | ✅ 统计函数类型注解比例 | ✅ 统计接口和类型别名数量 |

---

## Python 类型检查 (mypy)

### Workflow 文件

**位置**: `.github/workflows/python-type-check.yml`

**触发条件**:
- Push 到 `main` 或 `develop` 分支
- Pull Request 到 `main` 或 `develop` 分支
- 手动触发 (`workflow_dispatch`)

**触发路径**:
- `src/**/*.py`
- `tests/**/*.py`
- `pyproject.toml`

### 检查阶段

#### 阶段1: 增量类型检查（快速反馈）

```yaml
type-check-incremental:
  # 使用 mypy 缓存加速检查
  --incremental
  --cache-dir=.mypy_cache
```

**特点**:
- 使用缓存加速检查
- 适合频繁推送时快速反馈
- 不会阻塞 PR（`continue-on-error: true`）

#### 阶段2: 完整类型检查（严格模式）

```yaml
type-check-full:
  # 检查 src/ 和 tests/
  mypy src/ tests/ \
    --warn-unused-ignores \
    --warn-redundant-casts \
    --warn-unused-configs
```

**特点**:
- 检查所有源码和测试代码
- 启用严格警告选项
- 生成详细的错误报告

#### 阶段3: 类型覆盖率分析

统计带有类型注解的函数比例：

```python
def analyze_type_coverage(directory):
    total_funcs = 0
    typed_funcs = 0

    for py_file in Path(directory).rglob('*.py'):
        funcs = re.findall(r'^def\s+(\w+)\s*\((.*?)\)\s*(?:->\s*([^:]+))?:', content)
        for func_name, params, return_type in funcs:
            total_funcs += 1
            if return_type or any(': ' in param for param in params.split(',')):
                typed_funcs += 1

    func_coverage = (typed_funcs / total_funcs * 100) if total_funcs > 0 else 0
    print(f'函数类型覆盖率: {func_coverage:.1f}%')
```

**输出示例**:
```
函数类型覆盖率: 85.3% (423/496)
类总数: 42
```

#### 阶段4: 质量门禁

```yaml
type-check-gate:
  # 增量检查错误不超过 50 个
  if [ "$ERROR_COUNT" -gt 50 ]; then
    QUALITY_PASS=false
  fi

  # 完整检查严重错误不超过 20 个
  if [ "$CRITICAL_ERRORS" -gt 20 ]; then
    QUALITY_PASS=false
  fi
```

### 本地运行

#### 安装依赖

```bash
pip install mypy==1.14.1
pip install types-requests types-PyYAML
```

#### 基本检查

```bash
# 检查 src/ 目录
mypy src/

# 检查 src/ 和 tests/
mypy src/ tests/

# 增量模式（使用缓存）
mypy src/ --incremental
```

#### 严格模式

```bash
# 启用所有警告
mypy src/ \
  --warn-unused-ignores \
  --warn-redundant-casts \
  --warn-unused-configs \
  --warn-no-return \
  --warn-redundant-casts \
  --warn-unreachable
```

#### 配置文件

**pyproject.toml**:
```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "taos.*",
    "taosws.*",
    "pynvml.*",
    "sklearn.*",
    "pymongo.*",
]
ignore_missing_imports = true
```

### 类型注解最佳实践

#### 函数签名

```python
# ✅ 推荐: 完整类型注解
def fetch_user_data(user_id: str) -> dict[str, Any]:
    """获取用户数据"""
    return {"id": user_id, "name": "Alice"}

# ❌ 避免: 无类型注解
def fetch_user_data(user_id):
    return {"id": user_id, "name": "Alice"}
```

#### 类型别名

```python
# ✅ 推荐: 使用类型别名
from typing import TypedDict

class User(TypedDict):
    id: str
    name: str
    email: str

def process_user(user: User) -> None:
    """处理用户数据"""
    pass

# ❌ 避免: 使用 dict[str, Any]
def process_user(user: dict[str, Any]) -> None:
    pass
```

#### 泛型

```python
from typing import TypeVar, Generic

T = TypeVar('T')

class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value
```

---

## TypeScript 类型检查 (vue-tsc)

### Workflow 文件

**位置**: `.github/workflows/typescript-type-check.yml`

**触发条件**:
- Push 到 `main` 或 `develop` 分支
- Pull Request 到 `main` 或 `develop` 分支
- 手动触发 (`workflow_dispatch`)

**触发路径**:
- `web/frontend/src/**/*.{ts,tsx,vue}`
- `web/frontend/tsconfig.json`
- `web/frontend/vite.config.ts`
- `web/frontend/package.json`

### 检查阶段

#### 阶段1: TypeScript 编译器检查（仅 .ts 文件）

```yaml
type-check-typescript:
  # 仅检查 .ts/.tsx 文件
  npx tsc --noEmit \
    --pretty \
    --incremental
```

**特点**:
- 快速检查（不包含 .vue 文件）
- 使用增量编译加速
- 适合日常开发

#### 阶段2: Vue 类型检查（包含 .vue 文件）

```yaml
type-check-vue:
  # 检查所有 .ts 和 .vue 文件
  npx vue-tsc --noEmit \
    --pretty \
    --force
```

**过滤规则**（与本地 quality gate hook 一致）:

```bash
cat vue-tsc-output.txt | grep -v \
  -e "src/components/artdeco" \  # ArtDeco 组件已知问题
  -e "src/utils/cache.ts" \        # 缓存持久化错误
  -e "src/api/types/generated-types.ts" \  # 自动生成文件
  -e "Could not find a declaration file for module" \  # 第三方库
  > vue-tsc-filtered.txt
```

**质量门禁**:
```yaml
TYPE_CHECK_THRESHOLD: 40  # 允许的最大类型错误数

if [ "$ERROR_COUNT" -gt "$TYPE_CHECK_THRESHOLD" ]; then
  QUALITY_PASS=false
fi
```

#### 阶段3: ESLint TypeScript 检查

```yaml
eslint-typescript:
  npx eslint src --ext .ts,.tsx,.vue \
    --format json \
    --output-file eslint-report.json
```

#### 阶段4: 类型覆盖率分析

统计 TypeScript 文件中的接口和类型定义：

```python
for ts_file in Path(directory).rglob('*.ts'):
    interfaces = len(re.findall(r'interface\s+\w+', content))
    types = len(re.findall(r'type\s+\w+', content))

print(f'TypeScript 文件数: {total_files}')
print(f'接口定义数: {total_interfaces}')
print(f'类型别名数: {total_types}')
```

### 本地运行

#### NPM Scripts

```bash
# 基本类型检查
npm run type-check

# 监视模式（实时反馈）
npm run type-check:watch

# 仅使用 tsc（不检查 .vue 文件）
npm run type-check:tsc

# CI 模式（强制检查）
npm run type-check:ci

# 严格模式
npm run type-check:strict
```

#### 手动运行

```bash
# 进入前端目录
cd web/frontend

# 生成类型定义
npm run generate-types

# 运行 vue-tsc
npx vue-tsc --noEmit

# 运行 tsc（不检查 .vue 文件）
npx tsc --noEmit

# 运行 ESLint
npm run lint
```

#### VSCode 集成

**.vscode/settings.json**:
```json
{
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true,
  "volar.completion.autoImportComponent": true,
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact",
    "vue"
  ],
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

### Vue 3 + TypeScript 最佳实践

#### 组件 Props 类型

```vue
<script setup lang="ts">
// ✅ 推荐: 使用接口定义 Props
interface UserProps {
  id: string
  name: string
  email?: string  // 可选
}

const props = defineProps<UserProps>()
</script>

<!-- ❌ 避免: 使用 PropType<any> -->
<script setup lang="ts">
import { PropType } from 'vue'

const props = defineProps({
  user: {
    type: Object as PropType<any>,
    required: true
  }
})
</script>
```

#### Ref 类型

```vue
<script setup lang="ts">
// ✅ 推荐: 显式类型参数
import { ref } from 'vue'

interface User {
  id: string
  name: string
}

// 单个对象
const selectedUser = ref<User | null>(null)

// 数组
const users = ref<User[]>([])

// 基础类型
const count = ref<number>(0)
</script>

<!-- ❌ 避免: 不指定类型 -->
<script setup lang="ts">
import { ref } from 'vue'

const selectedUser = ref(null)  // Ref<never>
const users = ref([])            // Ref<never[]>
</script>
```

#### Computed 类型

```vue
<script setup lang="ts">
// ✅ 推荐: 自动推断或显式类型
import { ref, computed } from 'vue'

const count = ref(0)

// 自动推断
const doubleCount = computed(() => count.value * 2)

// 显式类型
const formattedCount = computed<string>(() => `Count: ${count.value}`)
</script>
```

#### API 调用类型

```typescript
// ✅ 推荐: 定义响应数据接口
interface ApiResponse<T> {
  data: T
  code: number
  message: string
}

interface User {
  id: string
  name: string
}

async function fetchUser(id: string): Promise<User> {
  const response = await axios.get<ApiResponse<User>>(`/api/users/${id}`)
  return response.data.data
}
```

---

## 本地开发工作流

### Python 开发流程

```bash
# 1. 开发新功能
vim src/features/new_feature.py

# 2. 添加类型注解
def process_data(data: list[dict[str, Any]]) -> dict[str, Any]:
    """处理数据"""
    return {"result": data}

# 3. 本地类型检查
mypy src/features/new_feature.py

# 4. 运行测试
pytest tests/features/test_new_feature.py

# 5. 提交代码
git add src/features/new_feature.py
git commit -m "feat: add new feature with type hints"

# 6. 推送触发 CI
git push origin feature-branch
```

### TypeScript 开发流程

```bash
# 1. 开发新组件
cd web/frontend
vim src/components/NewComponent.vue

# 2. 添加类型定义
<script setup lang="ts">
interface ComponentProps {
  title: string
  items: Item[]
}

const props = defineProps<ComponentProps>()
const selected = ref<Item | null>(null)
</script>

# 3. 本地类型检查（实时反馈）
npm run type-check:watch

# 4. 在另一个终端运行开发服务器
npm run dev

# 5. 提交代码
git add src/components/NewComponent.vue
git commit -m "feat: add new component with type safety"

# 6. 推送触发 CI
git push origin feature-branch
```

### Pre-commit Hook（自动化类型检查）

#### Python Pre-commit Hook

**.pre-commit-config.yaml**:
```yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.1
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
          - types-PyYAML
        args: [--config-file=pyproject.toml]
```

安装:
```bash
pip install pre-commit
pre-commit install
```

#### TypeScript Pre-commit Hook

**.pre-commit-config.yaml**:
```yaml
repos:
  - repo: local
    hooks:
      - id: vue-tsc
        name: Vue TypeScript Check
        entry: bash -c 'cd web/frontend && npm run type-check:ci'
        language: system
        pass_filenames: false
        files: \.(ts|tsx|vue)$
```

---

## CI/CD 集成策略

### 1. 渐进式集成

#### 阶段1: 报告模式（不阻塞）

```yaml
# 第一周: 仅收集错误，不阻塞 PR
- name: Run mypy
  run: mypy src/
  continue-on-error: true  # 不阻塞

- name: Upload results
  uses: actions/upload-artifact@v4
  with:
    name: mypy-results
    path: mypy-report.txt
```

#### 阶段2: 软性门禁（阈值）

```yaml
# 第二周: 设置宽松阈值
QUALITY_GATE_THRESHOLD=100  # 允许 100 个错误

if [ "$ERROR_COUNT" -gt "$QUALITY_GATE_THRESHOLD" ]; then
  QUALITY_PASS=false
fi
```

#### 阶段3: 严格门禁（逐步收紧）

```yaml
# 第三周: 收紧阈值
QUALITY_GATE_THRESHOLD=50

# 第四周: 进一步收紧
QUALITY_GATE_THRESHOLD=20

# 第五周: 零容忍（可选）
QUALITY_GATE_THRESHOLD=0
```

### 2. 并行执行

```yaml
jobs:
  # Python 和 TypeScript 类型检查并行执行
  python-type-check:
    runs-on: ubuntu-latest
    steps: [...]

  typescript-type-check:
    runs-on: ubuntu-latest
    steps: [...]

  # 等待两者都完成
  quality-gate:
    needs: [python-type-check, typescript-type-check]
    steps: [...]
```

### 3. 缓存优化

```yaml
# Python mypy 缓存
- name: Cache mypy cache
  uses: actions/cache@v4
  with:
    path: .mypy_cache
    key: ${{ runner.os }}-mypy-${{ hashFiles('pyproject.toml', 'src/**/*.py') }}

# TypeScript 缓存
- name: Cache node modules
  uses: actions/cache@v4
  with:
    path: web/frontend/node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('web/frontend/package-lock.json') }}
```

### 4. 分支策略

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

# develop 分支: 宽松阈值
env:
  TYPE_CHECK_THRESHOLD: 100

# main 分支: 严格阈值
# TYPE_CHECK_THRESHOLD: 20
```

---

## 常见问题

### Q1: Mypy 报告 "too many errors"

**问题**: Mypy 发现太多错误，难以一次性修复

**解决方案**:

1. **使用 `# type: ignore` 暂时忽略**
```python
def legacy_function(x):  # type: ignore
    """旧代码，暂时忽略类型检查"""
    pass
```

2. **逐文件修复**
```bash
# 每次修复一个文件
mypy src/legacy_module.py --no-error-summary 2>&1 | less
```

3. **使用 mypy 配置逐步启用严格模式**
```toml
[tool.mypy]
# 第一步: 仅启用基础检查
disallow_untyped_defs = false

# 第二步: 启用严格检查
disallow_untyped_defs = true
```

### Q2: Vue-tsc 检查太慢

**问题**: `vue-tsc` 检查耗时较长（5-10 分钟）

**解决方案**:

1. **使用 `tsc` 快速检查**
```bash
# 仅检查 .ts 文件（不包括 .vue）
npx tsc --noEmit
```

2. **使用增量编译**
```bash
# tsconfig.json
{
  "compilerOptions": {
    "incremental": true,
    "tsBuildInfoFile": ".tsbuildinfo"
  }
}
```

3. **仅检查变更文件**
```yaml
# Git diff 查找变更的文件
CHANGED_FILES=$(git diff --name-only HEAD~1 | grep '\.vue$')
npx vue-tsc --noEmit $CHANGED_FILES
```

### Q3: 第三方库缺少类型定义

**Python**:

```python
# 方案1: 使用 typing.stub 文件
# my_stubs.py
module_name: Any = ...

# 方案2: 配置 mypy 忽略
[[tool.mypy.overrides]]
module = "third_party_module"
ignore_missing_imports = true
```

**TypeScript**:

```bash
# 方案1: 安装类型定义
npm install --save-dev @types/third-party-lib

# 方案2: 创建类型声明文件
// src/types/third-party-lib.d.ts
declare module 'third-party-lib' {
  export interface SomeInterface {
    property: string
  }
}

# 方案3: 使用 // @ts-ignore
import { something } from 'third-party-lib'  // @ts-ignore
```

### Q4: 类型检查与 ESLint 冲突

**问题**: ESLint 报告的类型错误与 mypy/vue-tsc 不一致

**解决方案**:

1. **禁用 ESLint 类型规则（使用 mypy 替代）**
```json
// .eslintrc.json
{
  "rules": {
    "@typescript-eslint/no-unused-vars": "off",
    "@typescript-eslint/no-explicit-any": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off"
  },
  "overrides": [
    {
      "files": ["*.ts", "*.tsx"],
      "rules": {
        "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }]
      }
    }
  ]
}
```

2. **分工明确**
- **ESLint**: 代码风格、最佳实践
- **mypy/vue-tsc**: 类型安全

### Q5: CI 运行但本地没错误

**问题**: 本地运行类型检查通过，但 CI 失败

**解决方案**:

1. **检查环境一致性**
```bash
# 确保使用相同版本
mypy --version
python --version

# CI 使用
python -m pip install mypy==1.14.1
```

2. **清理缓存**
```bash
# Python
rm -rf .mypy_cache
mypy src/ --incremental

# TypeScript
rm -rf node_modules/.vite
npm run type-check:ci
```

3. **检查 CI 环境变量**
```yaml
# 确保 CI 配置与本地一致
env:
  MYPY_FORCE_COLOR: 0
  MYPY_CACHE_DIR: .mypy_cache
```

---

## 附录

### A. 类型检查命令速查表

#### Python (mypy)

| 命令 | 用途 |
|------|------|
| `mypy src/` | 基本检查 |
| `mypy src/ --incremental` | 增量检查 |
| `mypy src/ --strict` | 严格模式 |
| `mypy src/ --no-error-summary` | 仅显示错误 |
| `mypy src/ --html-report ./html` | 生成 HTML 报告 |

#### TypeScript (vue-tsc)

| 命令 | 用途 |
|------|------|
| `npm run type-check` | 基本 Vue 类型检查 |
| `npm run type-check:watch` | 监视模式 |
| `npm run type-check:tsc` | 仅 .ts 文件 |
| `npm run type-check:ci` | CI 模式（强制） |
| `npx tsc --noEmit --pretty` | 美化输出 |

### B. 配置文件位置

| 工具 | 配置文件 | 位置 |
|------|---------|------|
| **mypy** | `pyproject.toml` | 项目根目录 |
| **tsc** | `tsconfig.json` | `web/frontend/` |
| **ESLint** | `.eslintrc.json` | `web/frontend/` |
| **Pre-commit** | `.pre-commit-config.yaml` | 项目根目录 |

### C. 相关文档链接

- **Python typing**: https://docs.python.org/3/library/typing.html
- **Mypy documentation**: https://mypy.readthedocs.io/
- **TypeScript handbook**: https://www.typescriptlang.org/docs/handbook/intro.html
- **Vue TypeScript guide**: https://vuejs.org/guide/typescript/composition-api.html
- **Volar (Vue language server)**: https://github.com/vuejs/language-tools

---

**文档版本**: v1.0
**最后更新**: 2026-01-12
**维护者**: MyStocks Team
