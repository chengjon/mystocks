# Python 代码质量保证工作流程

> **参考指南说明**:
> 本文件是 Python 质量保证专题流程文档，不是当前仓库统一质量门禁或共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及运维执行流程或协作约束，再结合根目录 `AGENTS.md` 与 `docs/operations/README.md`。
>
> 文内工具组合、触发时机和流程分层应视为质量治理参考框架；若与当前 hook、CI 或主线治理文档冲突，应以 `architecture/STANDARDS.md`、当前 hook/CI 配置与主线治理文档为准。

**优化策略**: Ruff 优先 + Black 兜底 + Pylint 深度审查

**统一行长度**: 120 (Black/Ruff/Pylint 保持一致)

---

## 📊 四阶段质量保证流程

### 阶段 1: 日常开发 (效率优先)

**目标**: 快速修复代码问题，不影响开发效率

**工具**: Ruff (一站式格式化 + Lint)

**触发时机**: 每次保存文件后

**使用方法**:
```bash
# 一键修复所有问题（格式化 + Lint）
ruff check --fix .

# 仅格式化
ruff format .

# 仅检查（不修复）
ruff check .
```

**配置特点**:
- ✅ **测试专属规则**: 启用 PT (pytest 专属) 规则
- ✅ **快速失败**: 仅检查影响测试执行的错误
- ✅ **自动修复**: 大部分问题可自动修复
- ✅ **统一行长度**: 120 字符

**Ruff 规则选择**:
- `E, W`: 基础语法错误和警告
- `F`: Pyflakes 代码错误检测
- `IND`: 缩进错误检查
- `PT`: pytest 专属规则
- `I`: 导入排序

**排除规则**:
- `E501`: 行长度（由 Black 处理）
- `PT011, PT012, PT015`: 测试代码中的合理例外

---

### 阶段 2: 提交前检查 (格式兜底 + 核心检查)

**目标**: 确保提交的代码符合团队标准

**工具**: Pre-commit Hooks (自动触发)

**触发时机**: 每次 `git commit` 时自动运行

**执行顺序** (9 个步骤):
1. **Ruff (Lint & Fix)** - 快速修复错误型问题
2. **Black (Formatter)** - 统一代码风格（1-2秒）
3. **Ruff (Check only)** - 二次校验，确保无新问题
4. **MyPy** - 类型检查
5. **Bandit** - 安全扫描
6. **Safety** - 依赖安全检查
7. **通用文件检查** - 尾随空格、YAML/JSON 语法等
8. **密钥检测** - 防止提交敏感信息
9. **Python 语法检查** - 检查 blanket noqa/eval 等

**使用方法**:
```bash
# 首次安装
pip install pre-commit
pre-commit install

# 手动运行所有检查
pre-commit run --all-files

# 运行特定 hook
pre-commit run ruff --all-files
pre-commit run black --all-files
```

**配置特点**:
- ✅ **文件范围限制**: 仅检查 `src/` 和 `tests/` 目录
- ✅ **统一行长度**: Black 和 Ruff 都使用 120
- ✅ **自动修复**: Ruff 和 Black 支持自动修复
- ✅ **快速失败**: 错误直接阻断提交

---

### 阶段 3: 定期深度质量分析 (Pylint 核心价值)

**目标**: 发现代码质量深层次问题

**工具**: Pylint (测试代码专用配置)

**触发时机**: 每周 / 每迭代末

**使用方法**:
```bash
# 检查测试代码质量
pylint --rcfile=.pylint.test.rc tests/

# 生成 HTML 报告
pylint --rcfile=.pylint.test.rc --output=pylint_test_report.html --output-format=html tests/

# 检查源代码（使用默认 .pylintrc）
pylint src/
```

**配置特点**:
- ✅ **测试专用规则**: 只关注测试核心问题
- ✅ **禁用所有，启用核心**: `disable = all` + `enable = [...]`
- ✅ **更宽松的阈值**: max-args=15, max-locals=25, max-statements=100
- ✅ **pytest 专属规则**: PT001-PT025 (需要 pylint-pytest 插件)

**主要启用规则**:
1. **基础语法错误** (缩进、未定义变量)
2. **测试代码质量** (未用导入、变量过多、类方法过少)
3. **pytest 专属规则** (fixture 使用、函数命名、断言方式)
4. **代码质量警告** (未使用变量/参数、复杂度过高)

**输出分析**:
- 📊 **HTML 报告**: 可视化查看所有问题
- 🎯 **重点关注**:
  - 测试用例无断言
  - 测试代码圈复杂度高
  - 函数变量过多（>25）
  - 函数语句过多（>100）

---

### 阶段 4: CI/CD 集成 (快速失败 + 完整检查)

**目标**: 保证 CI 流水线效率

**工具顺序**: Ruff+Black → MyPy+Bandit+Safety → Pylint (仅记录)

**CI 配置建议**:
```yaml
# .github/workflows/ci.yml
jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      # 第一阶段：快速失败
      - name: Run Ruff
        run: ruff check . --output-format=github

      - name: Run Black
        run: black --check .

      # 第二阶段：核心检查
      - name: Run MyPy
        run: mypy src/

      - name: Run Bandit
        run: bandit -r src/

      - name: Run Safety
        run: safety check --json

      # 第三阶段：深度分析（不阻断构建）
      - name: Run Pylint (Tests)
        run: pylint --rcfile=.pylint.test.rc tests/ || true
        continue-on-error: true
```

**关键策略**:
- ✅ **快速失败**: Ruff/Black 问题直接失败
- ✅ **核心检查**: MyPy/Bandit/Safety 问题必须修复
- ✅ **记录报告**: Pylint 仅生成报告，不阻断构建

---

## 🛠️ 工具配置总结

### 1. Ruff (日常开发)

**配置位置**: `pyproject.toml`

**关键配置**:
```toml
[tool.ruff]
line-length = 120
target-version = "py39"

[tool.ruff.lint]
select = ["E", "W", "F", "IND", "PT", "I"]
ignore = ["E501", "I001", "PT011", "PT012", "PT015", "S101", "C901"]
fix = true

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "ARG001", "ARG002"]
```

**常用命令**:
```bash
# 修复所有问题
ruff check --fix .

# 格式化代码
ruff format .

# 检查但不修复
ruff check .
```

---

### 2. Black (格式化兜底)

**配置位置**: `pyproject.toml`

**关键配置**:
```toml
[tool.black]
line-length = 120
target-version = ['py39']
```

**常用命令**:
```bash
# 格式化代码
black .

# 检查格式（不修改）
black --check .
```

---

### 3. Pylint (深度分析)

**配置文件**:
- `.pylintrc` - 常规代码检查
- `.pylint.test.rc` - 测试代码检查（每周/每迭代末）

**测试专用配置**:
```ini
[MESSAGES CONTROL]
disable = all
enable =
    bad-indentation, E0602, E0601,  # 基础语法错误
    W0611, R0914, R0903,             # 测试代码质量
    PT001, PT002, ..., PT025,        # pytest 专属规则
    W0612, W0613, R0913, R0915,     # 复杂度检查
    C0304, C0305, C0321,             # 代码格式

[DESIGN]
max-args = 15
max-locals = 25
max-returns = 10
max-branches = 20
max-statements = 100
```

**常用命令**:
```bash
# 检查测试代码
pylint --rcfile=.pylint.test.rc tests/

# 生成 HTML 报告
pylint --rcfile=.pylint.test.rc --output=pylint_test_report.html --output-format=html tests/

# 检查源代码
pylint src/
```

---

### 4. Pre-commit Hooks (自动检查)

**配置位置**: `.pre-commit-config.yaml`

**执行顺序**:
1. Ruff (Lint & Fix)
2. Black (Formatter)
3. Ruff (Check only)
4. MyPy (Type Check)
5. Bandit (Security Scan)
6. Safety (Dependency Check)
7. 通用文件检查
8. 密钥检测
9. Python 语法检查

**常用命令**:
```bash
# 首次安装
pre-commit install

# 手动运行所有
pre-commit run --all-files

# 更新 hooks
pre-commit autoupdate
```

---

### 5. 安全工具 (不可替代)

**Bandit** - 代码安全扫描
**Safety** - 依赖安全检查

**配置位置**: `config/.security.yml`

**常用命令**:
```bash
# Bandit 安全扫描
bandit -r src/ -c config/.security.yml

# Safety 依赖检查
safety check --json
```

---

## 🎯 避坑指南

### 1. 格式化冲突

**问题**: Ruff 和 Black 同时格式化导致冲突

**解决方案**:
- ✅ **统一行长度**: Ruff 和 Black 都设置为 120
- ✅ **禁用冲突规则**: Ruff 中禁用 `E501` (行长度)
- ✅ **执行顺序**: Ruff → Black → Ruff (二次校验)

### 2. 测试代码容错

**问题**: 测试代码中的合理模式被误报

**解决方案**:
- ✅ **测试文件豁免**:
  ```toml
  [tool.ruff.lint.per-file-ignores]
  "tests/**/*.py" = ["S101", "ARG001", "ARG002"]
  ```
- ✅ **禁用过于严格的规则**: `PT011`, `PT012`, `PT015`

### 3. Pylint 性能

**问题**: Pylint 检查太慢，影响日常开发

**解决方案**:
- ✅ **定期运行**: 仅每周/每迭代末运行
- ✅ **限制范围**: 仅检查 `tests/` 目录
- ✅ **精简规则**: 只启用核心规则，禁用所有其他规则

### 4. CI 流水线效率

**问题**: 所有工具都运行导致 CI 太慢

**解决方案**:
- ✅ **快速失败**: Ruff/Black 问题直接失败
- ✅ **记录报告**: Pylint 仅生成报告，不阻断构建
- ✅ **并行执行**: 独立的工具可以并行运行

---

## 📋 检查清单

### 日常开发 (每次保存)
- [ ] 运行 `ruff check --fix .`
- [ ] 运行 `ruff format .`

### 提交前 (每次 commit)
- [ ] Pre-commit hooks 自动运行
- [ ] 修复所有被阻断的问题

### 每周/每迭代末
- [ ] 运行 `pylint --rcfile=.pylint.test.rc tests/`
- [ ] 查看生成的 HTML 报告
- [ ] 修复高优先级问题

### CI/CD
- [ ] Ruff + Black 快速失败
- [ ] MyPy + Bandit + Safety 核心检查
- [ ] Pylint 生成报告（不阻断）

---

## 🔧 安装和设置

### 首次设置

```bash
# 1. 安装开发依赖
pip install -e ".[dev]"

# 2. 安装 pre-commit hooks
pre-commit install

# 3. 安装 pylint-pytest 插件（可选，用于测试代码检查）
pip install pylint-pytest

# 4. 验证安装
ruff --version
black --version
pylint --version
mypy --version
bandit --version
safety --version
```

### 更新工具

```bash
# 更新 pre-commit hooks
pre-commit autoupdate

# 更新 Python 工具
pip install -U ruff black pylint mypy bandit safety
```

---

## 📚 参考文档

- [Ruff 文档](https://docs.astral.sh/ruff/)
- [Black 文档](https://black.readthedocs.io/)
- [Pylint 文档](https://pylint.pycqa.org/)
- [MyPy 文档](https://mypy.readthedocs.io/)
- [Bandit 文档](https://bandit.readthedocs.io/)
- [Safety 文档](https://github.com/pyupio/safety)
- [Pre-commit 文档](https://pre-commit.com/)

---

## 🎉 总结

通过这四个阶段的流程，我们实现了：

1. **日常开发** - Ruff 快速修复，不影响开发效率
2. **提交前** - Pre-commit 自动检查，确保代码质量
3. **定期分析** - Pylint 深度审查，发现潜在问题
4. **CI/CD** - 快速失败 + 完整检查，保证流水线效率

**核心原则**: **效率优先 + 质量保证 + 安全防线**
