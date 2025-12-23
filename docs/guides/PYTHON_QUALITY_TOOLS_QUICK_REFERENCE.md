# Python 质量检查工具 - 快速参考

## 一行命令快速修复

```bash
# 日常开发：一键修复所有问题
ruff check --fix .

# 提交前：运行所有检查
pre-commit run --all-files

# 每周分析：生成测试质量报告
pylint --rcfile=.pylint.test.rc --output=pylint_test_report.html --output-format=html tests/
```

---

## 工具版本

| 工具 | 版本 | 用途 |
|------|------|------|
| Ruff | 0.9.10 | 日常开发（格式化 + Lint） |
| Black | 25.11.0 | 格式化兜底 |
| Pylint | 4.0.3 | 深度质量分析 |
| MyPy | (在 dev) | 类型检查 |
| Bandit | 1.7.5+ | 安全扫描 |
| Safety | 2.3.0+ | 依赖安全 |

---

## 四阶段流程

| 阶段 | 触发时机 | 工具 | 时间 |
|------|----------|------|------|
| **1. 日常开发** | 每次保存 | Ruff | 秒级 |
| **2. 提交前** | git commit | Pre-commit | 分钟级 |
| **3. 定期分析** | 每周/迭代末 | Pylint | 分钟级 |
| **4. CI/CD** | 每次 push | Ruff→MyPy→Bandit→Safety | 分钟级 |

---

## 关键配置

**统一行长度**: 120 (所有工具)

**配置文件**:
- `pyproject.toml` - Ruff, Black, MyPy, Pylint (常规)
- `.pylint.test.rc` - Pylint (测试专用)
- `.pre-commit-config.yaml` - Pre-commit hooks
- `config/.security.yml` - 安全配置

---

## 常用命令

### Ruff (日常开发)
```bash
ruff check --fix .          # 修复所有问题
ruff format .               # 格式化代码
ruff check .                # 仅检查
```

### Pre-commit (提交前)
```bash
pre-commit install          # 首次安装
pre-commit run --all-files  # 手动运行
pre-commit autoupdate       # 更新 hooks
```

### Pylint (定期分析)
```bash
pylint --rcfile=.pylint.test.rc tests/                    # 检查测试
pylint --rcfile=.pylint.test.rc --output=report.html --output-format=html tests/  # HTML报告
pylint src/                                              # 检查源码
```

### 安全检查
```bash
bandit -r src/ -c config/.security.yml    # 安全扫描
safety check --json                       # 依赖检查
```

---

## 避坑指南

### ❌ 错误做法
```bash
# 手动运行所有工具（太慢）
ruff check . && black . && pylint . && mypy . && bandit . && safety check

# 每次提交都运行 Pylint（太慢，阻塞开发）
```

### ✅ 正确做法
```bash
# 日常：仅 Ruff
ruff check --fix .

# 提交前：Pre-commit 自动运行（已配置）
git commit -m "message"

# 定期：Pylint 生成报告（不阻塞）
pylint --rcfile=.pylint.test.rc --output=report.html --output-format=html tests/
```

---

## 工作流程图

```
开发代码 → ruff check --fix . → 保存
    ↓
git add → git commit → pre-commit hooks 自动运行
    ↓
    ├─ Ruff (fix)
    ├─ Black (format)
    ├─ Ruff (check)
    ├─ MyPy
    ├─ Bandit
    └─ Safety
    ↓
提交成功 → 推送到远程 → CI/CD 运行
    ↓
每周末 → pylint --rcfile=.pylint.test.rc tests/ → 生成报告
```

---

## 故障排查

### Pre-commit 不工作
```bash
# 检查是否安装
pre-commit --version

# 重新安装
pre-commit install

# 手动运行查看错误
pre-commit run --all-files --verbose
```

### Ruff 和 Black 冲突
```bash
# 确保行长度一致
grep "line-length" pyproject.toml

# 重新运行
ruff check --fix .
black .
```

### Pylint 报告太多问题
```bash
# 使用测试专用配置（只关注核心问题）
pylint --rcfile=.pylint.test.rc tests/

# 生成 HTML 报告，方便查看
pylint --rcfile=.pylint.test.rc --output=report.html --output-format=html tests/
```

---

## 完整文档

详细工作流程请参阅: [docs/guides/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md](docs/guides/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md)

---

## 核心原则

**Ruff 优先** - 日常开发快速修复
**Black 兜底** - 确保格式统一
**Pylint 深度** - 定期质量分析
**安全必保** - Bandit + Safety 不可替代
