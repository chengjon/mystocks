# 🔄 CI/CD 类型检查快速参考

> **使用说明**:
> 本文件是类型检查 quick reference，适合补充查阅，不是当前 CI/CD 门禁、当前类型基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及运维执行流程、协作约束或专项操作说明，再结合根目录 `AGENTS.md` 与 `docs/operations/README.md` 及主线测试/类型检查文档。

> 本文档提供 Python (mypy) 和 TypeScript (vue-tsc) 类型检查的快速参考。

---

## 🚀 快速开始

### 本地类型检查

#### Python (mypy)
```bash
# 基本检查
mypy src/

# 严格模式
mypy src/ --strict

# 增量模式（使用缓存）
mypy src/ --incremental

# 生成 HTML 报告
mypy src/ --html-report ./html-report
```

#### TypeScript (vue-tsc)
```bash
cd web/frontend

# 基本检查
npm run type-check

# 监视模式（实时反馈）
npm run type-check:watch

# 仅 .ts 文件（快速）
npm run type-check:tsc

# CI 模式（强制检查）
npm run type-check:ci
```

---

## 📊 CI/CD Workflows

### Python 类型检查
**Workflow**: `.github/workflows/python-type-check.yml`

| 阶段 | 描述 | 阈值 |
|------|------|------|
| 增量检查 | 快速反馈（使用缓存） | 无限制 |
| 完整检查 | 全面检查（包含测试） | 50 错误 |
| 覆盖率分析 | 统计类型注解比例 | - |
| 质量门禁 | 评估是否通过 | 50/20 错误 |

### TypeScript 类型检查
**Workflow**: `.github/workflows/typescript-type-check.yml`

| 阶段 | 描述 | 阈值 |
|------|------|------|
| TSC 检查 | 仅 .ts 文件 | 无限制 |
| Vue-tsc 检查 | .ts + .vue 文件 | 40 错误 |
| ESLint 检查 | 代码风格 | 100 问题 |
| 质量门禁 | 评估是否通过 | 40 错误 |

---

## 🔧 常用命令

### Python 开发
```bash
# 1. 开发新功能
vim src/features/new_feature.py

# 2. 添加类型注解
def process_data(data: list[dict[str, Any]]) -> dict[str, Any]:
    return {"result": data}

# 3. 本地检查
mypy src/features/new_feature.py

# 4. 运行测试
pytest tests/features/test_new_feature.py

# 5. 提交
git add src/features/new_feature.py
git commit -m "feat: add new feature with type hints"
git push
```

### TypeScript 开发
```bash
# 1. 开发新组件
cd web/frontend
vim src/components/NewComponent.vue

# 2. 添加类型定义
<script setup lang="ts">
interface Props {
  title: string
  items: Item[]
}
const props = defineProps<Props>()
const selected = ref<Item | null>(null)
</script>

# 3. 本地检查（终端1）
npm run type-check:watch

# 4. 开发服务器（终端2）
npm run dev

# 5. 提交
git add src/components/NewComponent.vue
git commit -m "feat: add new component with type safety"
git push
```

---

## 📝 类型注解模式

### Python 常用模式

```python
# 函数签名
def fetch_user(user_id: str) -> dict[str, Any]:
    return {"id": user_id, "name": "Alice"}

# 可选参数
from typing import Optional

def find_user(user_id: str) -> Optional[User]:
    return User.query.get(user_id)

# 泛型
from typing import TypeVar, Generic

T = TypeVar('T')

class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value
```

### TypeScript/Vue 常用模式

```vue
<script setup lang="ts">
// Props 类型
interface Props {
  title: string
  count?: number  // 可选
}

const props = defineProps<Props>()

// Ref 类型
interface User {
  id: string
  name: string
}

const selectedUser = ref<User | null>(null)
const users = ref<User[]>([])

// Computed 类型
const doubleCount = computed(() => count.value * 2)

// API 调用类型
interface ApiResponse<T> {
  data: T
  code: number
}

async function fetchData(): Promise<User> {
  const res = await axios.get<ApiResponse<User>>('/api/users/1')
  return res.data.data
}
</script>
```

---

## 🎯 质量门禁

### 触发条件
- ✅ Push 到 `main` 或 `develop` 分支
- ✅ Pull Request 到 `main` 分支
- ✅ 手动触发（GitHub Actions 页面）

### 失败处理
1. 查看 GitHub Actions 日志
2. 下载类型检查报告（Artifacts）
3. 修复类型错误
4. 推送修复或更新 PR

### 常见错误
| 错误类型 | Python 修复 | TypeScript 修复 |
|---------|------------|----------------|
| 参数无类型 | 添加 `: Type` | 添加 `: Type` |
| 返回值无类型 | 添加 `-> Type` | 添加 `: Promise<Type>` |
| 未定义导入 | `# type: ignore` | `// @ts-ignore` |
| 第三方库 | 配置 `overrides` | 安装 `@types/*` |

---

## 📚 相关文档

- **完整指南**: [CI/CD 类型检查集成指南](./CICD_TYPE_CHECK_INTEGRATION_GUIDE.md)
- **Python typing**: https://docs.python.org/3/library/typing.html
- **Mypy 文档**: https://mypy.readthedocs.io/
- **TypeScript**: https://www.typescriptlang.org/docs/
- **Vue TypeScript**: https://vuejs.org/guide/typescript/

---

**版本**: v1.0 | **更新**: 2026-01-12
