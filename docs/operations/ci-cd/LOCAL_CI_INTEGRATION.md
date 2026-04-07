# MyStocks 本地开发环境CI集成指南

> **使用说明**:
> 本文件是本地 CI 集成专题指南，不是当前仓库统一开发流程、当前质量门禁或共享规则的唯一事实来源。
> 若涉及当前开发主线、环境一致性、审批门禁或统一治理规则，请优先阅读 `architecture/STANDARDS.md`；若涉及运维执行流程或协作约束，再结合根目录 `AGENTS.md` 与 `docs/operations/README.md`。

## 🎯 概述

本指南介绍如何在本地开发环境中集成CI/CD检查，确保代码质量从开发阶段就开始把控。

## 📋 前置要求

### 系统要求
- Python 3.12+
- Git 2.30+
- Node.js 16+ (前端开发)

### 依赖安装
```bash
# 安装pre-commit
pip install pre-commit

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装前端依赖 (如需要前端开发)
cd web/frontend && npm install
```

## 🚀 快速开始

### 1. 初始化pre-commit hooks
```bash
# 安装pre-commit hooks到本地仓库
pre-commit install

# (可选) 安装到commit-msg检查
pre-commit install --hook-type commit-msg
```

### 2. 运行本地CI检查
```bash
# 运行完整的本地CI检查
./scripts/ci/local_ci_check.sh

# 或使用pre-commit运行所有检查
pre-commit run --all-files

# 只运行本地CI检查
pre-commit run local-ci-check
```

### 3. 日常开发工作流

#### 开发前准备
```bash
# 确保分支是最新的
git checkout develop
git pull origin develop

# 创建功能分支
git checkout -b feature/new-quantization-strategy
```

#### 开发过程中
```bash
# 编写代码...

# 提交前自动检查 (pre-commit会自动运行)
git add .
git commit -m "feat: 实现新的量化策略"

# 如果检查失败，修复问题后重新提交
```

#### 推送到远程
```bash
# 推送到远程分支
git push origin feature/new-quantization-strategy

# 在GitHub上创建PR到develop分支
```

## 🔧 配置详解

### pre-commit hooks配置

项目已配置以下检查：

#### 1. 代码格式化 (Black)
- **作用**: 统一代码格式
- **触发**: 每次提交Python文件时
- **修复**: `black src/`

#### 2. 导入排序 (isort)
- **作用**: 规范化导入语句顺序
- **触发**: Python文件提交时

#### 3. 类型检查 (MyPy)
- **作用**: 静态类型检查
- **触发**: Python核心文件提交时

#### 4. 本地CI检查 (local-ci-check)
- **作用**: 快速质量验证
- **检查内容**:
  - Python环境验证
  - 代码格式检查
  - 快速类型检查
  - 安全扫描
  - 单元测试
  - 量化策略语法验证

#### 5. 量化策略验证 (quant-strategy-syntax)
- **作用**: 确保策略文件语法正确
- **触发**: `src/strategies/`目录下的Python文件

#### 6. 安全检查 (Bandit)
- **作用**: 发现潜在安全漏洞
- **触发**: 源代码文件提交时

### 自定义配置

#### 修改检查范围
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: local-ci-check
        files: \.(py|js|ts|vue)$  # 修改文件匹配模式
        exclude: ^tests/.*        # 排除测试目录
```

#### 跳过特定检查
```bash
# 临时跳过所有检查
git commit --no-verify -m "紧急修复"

# 跳过特定hook
SKIP=local-ci-check git commit -m "跳过本地CI检查"
```

## 🐛 故障排除

### 常见问题

#### pre-commit未安装
```bash
pip install pre-commit
pre-commit --version
```

#### 检查运行太慢
```bash
# 只运行特定检查
pre-commit run black
pre-commit run local-ci-check

# 使用缓存
pre-commit run --all-files  # 首次运行会建立缓存
```

#### Python路径问题
```bash
# 确保Python路径正确
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### 依赖缺失
```bash
# 检查并安装缺失的工具
pip install black mypy bandit ruff isort

# 前端检查工具
cd web/frontend && npm install eslint
```

### 调试技巧

#### 查看详细日志
```bash
# 运行时显示详细信息
pre-commit run --verbose

# 查看特定hook的日志
pre-commit run local-ci-check --verbose
```

#### 手动运行检查
```bash
# 测试本地CI脚本
bash -x ./scripts/ci/local_ci_check.sh

# 单独测试量化策略检查
python3 -c "
import sys
sys.path.insert(0, 'src')
# 策略检查代码
"
```

## 📊 检查内容详解

### 本地CI检查覆盖范围

| 检查项 | 说明 | 耗时 | 重要性 |
|--------|------|------|--------|
| Python环境 | 版本和依赖验证 | < 1s | 高 |
| 代码格式 | Black格式检查 | < 5s | 高 |
| 类型检查 | MyPy快速检查 | < 10s | 中 |
| 安全扫描 | Bandit基础检查 | < 5s | 高 |
| 单元测试 | 核心模块测试 | < 30s | 高 |
| 策略验证 | 量化策略语法 | < 2s | 高 |

### 性能优化

#### 缓存策略
- pre-commit会自动缓存检查结果
- 只有变更的文件会被重新检查
- 依赖包会被缓存到 `~/.cache/pre-commit`

#### 并行执行
```bash
# 使用多进程运行 (如果支持)
pre-commit run --all-files --jobs 4
```

## 🔄 集成到IDE

### VS Code配置
```json
// .vscode/settings.json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### PyCharm配置
1. **外部工具**: 添加pre-commit命令
2. **文件监听器**: 自动格式化
3. **提交前检查**: 集成pre-commit

## 📈 最佳实践

### 开发习惯
1. **频繁提交**: 小步快跑，避免大块修改
2. **提前检查**: 不要等到提交时才发现问题
3. **分支管理**: 使用描述性的分支名称

### 团队协作
1. **统一环境**: 所有开发者使用相同版本的工具
2. **定期更新**: 保持pre-commit hooks为最新版本
3. **问题反馈**: 及时报告配置问题

### 性能调优
1. **选择性检查**: 只对相关文件运行检查
2. **缓存利用**: 充分利用pre-commit缓存
3. **定期清理**: 清理不需要的缓存文件

## 🎯 成功指标

✅ **安装成功**: `pre-commit --version`正常运行
✅ **检查生效**: 提交时自动触发检查
✅ **问题发现**: 能及时发现代码质量问题
✅ **团队统一**: 所有成员使用相同标准
✅ **性能满意**: 检查耗时不超过30秒

---

**🎉 集成完成后，你的开发环境将具备企业级的代码质量保障！**
