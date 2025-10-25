# Contract: .gitignore配置规范契约

**Feature**: 系统规范化改进
**Branch**: 006-0-md-1
**Date**: 2025-10-16
**Type**: Git Configuration

## 目的

定义.gitignore配置标准，确保Git仓库清洁、避免敏感信息泄露、减少无意义的提交冲突。

## 必须排除的文件类型清单

### 1. 环境变量和配置 (P1 - 安全)

```gitignore
# 环境变量文件 (但保留示例模板)
.env
.env.local
.env.*.local
!.env.example  # ✅ 保留作为模板
```

**理由**: `.env`包含敏感信息(数据库密码、API密钥等)，绝对不能提交到Git

### 2. Python缓存文件 (P1 - 清洁度)

```gitignore
# Python字节码
__pycache__/
*.py[cod]
*$py.class
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Virtual环境
venv/
ENV/
env/
.venv
```

**当前问题**: ❌ `__pycache__/`目录未被忽略，导致Git status显示大量缓存文件

### 3. 日志和临时文件 (P1 - 清洁度)

```gitignore
# 日志文件
*.log
*.log.*
logs/
*.out

# 临时文件
temp/
*.tmp
*.temp
*.swp
*.swo
*~
.DS_Store
Thumbs.db
```

### 4. IDE配置 (P2 - 个人偏好)

```gitignore
# VSCode
.vscode/
*.code-workspace
.history/

# PyCharm
.idea/
*.iml
*.ipr
*.iws
out/

# Sublime Text
*.sublime-project
*.sublime-workspace

# Vim
*.swp
*.swo
*~
.*.swp

# Emacs
\#*\#
.\#*

# Eclipse
.project
.pydevproject
.settings/
```

### 5. 测试和覆盖率 (P2 - 生成文件)

```gitignore
# Pytest
.pytest_cache/
.tox/
.nox/

# Coverage
.coverage
.coverage.*
htmlcov/
.hypothesis/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyright
.pyright/
```

### 6. Node.js / 前端 (P1 - 前端项目)

```gitignore
# 依赖
node_modules/
jspm_packages/

# 构建输出
dist/
build/
.next/
out/

# 缓存
.npm
.eslintcache
.stylelintcache

# 日志
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
```

### 7. 数据库和备份 (P1 - 大文件)

```gitignore
# 数据库文件
*.db
*.sqlite
*.sqlite3

# 备份文件
*.sql
*.dump
*.bak
backups/
```

### 8. 系统和OS文件 (P2 - 系统生成)

```gitignore
# macOS
.DS_Store
.AppleDouble
.LSOverride

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini
$RECYCLE.BIN/

# Linux
*~
.directory
.Trash-*
```

## 通用规则 vs 特定规则

### 根目录 .gitignore (通用规则)

**位置**: `/opt/claude/mystocks_spec/.gitignore`

包含:
- ✅ Python相关 (所有.py项目通用)
- ✅ IDE配置 (团队成员可能使用不同IDE)
- ✅ 日志和临时文件
- ✅ 环境变量文件
- ✅ 测试覆盖率报告

**不包含**:
- ❌ Node.js特定规则 (应在web/frontend/.gitignore)
- ❌ 特定子项目的临时文件

### 子目录 .gitignore (特定规则)

**位置**: `web/frontend/.gitignore`

包含:
- ✅ node_modules/
- ✅ dist/
- ✅ build/
- ✅ .next/
- ✅ npm-debug.log*
- ✅ .env.local (前端环境变量)

**规则优先级**: 子目录规则 > 根目录规则

## 排除规则 (!)

用于保留特定应该被忽略模式下的文件:

```gitignore
# 忽略所有.env文件
.env*

# 但保留.env.example作为模板
!.env.example
```

**其他使用场景**:
```gitignore
# 忽略所有日志
*.log

# 但保留重要的示例日志
!example.log
```

## 验证命令

### 检查当前未跟踪文件

```bash
# 查看所有未跟踪文件
git status --untracked-files=all

# 预期结果: 不应显示以下类型
# - __pycache__/
# - *.pyc, *.log
# - .env (但.env.example可见)
# - IDE配置目录
```

### 检查.gitignore是否生效

```bash
# 测试某个文件是否被忽略
git check-ignore -v file_name

# 示例
git check-ignore -v __pycache__/test.cpython-312.pyc
# 预期输出: .gitignore:5:__pycache__/    __pycache__/test.cpython-312.pyc
```

### 清理已跟踪但应被忽略的文件

```bash
# ⚠️ 谨慎使用: 从Git中移除但保留本地文件
git rm -r --cached __pycache__/
git rm --cached *.pyc

# 提交更改
git add .gitignore
git commit -m "chore: update .gitignore to exclude __pycache__ and *.pyc"
```

## 子目录.gitignore策略

### web/frontend/.gitignore

**创建**: 如不存在则创建
**内容**:
```gitignore
# 依赖
node_modules/
/.pnp
.pnp.js

# 测试
/coverage

# 生产构建
/build
/dist
/.next/
/out/

# 杂项
.DS_Store
*.pem

# 调试
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# 本地环境变量
.env.local
.env.development.local
.env.test.local
.env.production.local

# Vercel
.vercel
```

### temp/ 目录

**处理**: temp/目录本身被忽略
```gitignore
# 临时文件目录
temp/

# 但保留README说明目录用途
!temp/README.md
```

### 其他子目录

**原则**: 除非有特殊需求，否则不在子目录创建.gitignore

## 完整 .gitignore 模板

**根目录** `/opt/claude/mystocks_spec/.gitignore`:

```gitignore
# ============================================================
# MyStocks 项目 .gitignore
# 版本: 2.1.0
# 最后更新: 2025-10-16
# ============================================================

# -------------------- 环境变量 --------------------
# 敏感配置文件 (保留.env.example作为模板)
.env
.env.local
.env.*.local
!.env.example

# -------------------- Python --------------------
# 字节码
__pycache__/
*.py[cod]
*$py.class
*.so

# 分发/打包
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 虚拟环境
venv/
ENV/
env/
.venv

# -------------------- IDE --------------------
# VSCode
.vscode/
*.code-workspace

# PyCharm
.idea/
*.iml

# Sublime Text
*.sublime-project
*.sublime-workspace

# Vim
*.swp
*.swo
*~

# -------------------- 日志和临时文件 --------------------
*.log
*.log.*
logs/
temp/
*.tmp
*.temp

# -------------------- 测试 --------------------
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/
.mypy_cache/

# -------------------- 数据库 --------------------
*.db
*.sqlite
*.sqlite3
backups/

# -------------------- 系统文件 --------------------
.DS_Store
Thumbs.db
Desktop.ini

# -------------------- 项目特定 --------------------
# 临时文件缓冲区 (保留README)
temp/
!temp/README.md

# 旧版本备份
*_backup.py
*_old.py
```

## 验收标准

### 必须满足 (SC-005)

- [ ] `git status` 不显示 `__pycache__/` 目录
- [ ] `git status` 不显示 `*.pyc` 文件
- [ ] `git status` 不显示 `*.log` 文件
- [ ] `git status` 不显示 `.env` 文件
- [ ] `.env.example` 文件可见且可跟踪

### 建议满足

- [ ] web/frontend/.gitignore 存在且包含Node.js规则
- [ ] IDE配置目录被正确忽略
- [ ] temp/目录被忽略但temp/README.md可见

### 检查清单

```bash
# 1. 应用新.gitignore后检查
git status

# 2. 不应显示以下内容
# - adapters/__pycache__/
# - utils/__pycache__/
# - *.pyc, *.pyo
# - .idea/ 或 .vscode/
# - *.log

# 3. 应该显示(如存在)
# - .env.example
# - temp/README.md (如创建)

# 4. 清理已跟踪的应忽略文件
git rm -r --cached __pycache__/
git add .gitignore
git commit -m "chore: update .gitignore and remove cached files"
```

---

**创建人**: Claude
**版本**: 1.0.0
**批准日期**: 待定
**最后修订**: 2025-10-16
**本次修订内容**: 基于R7研究结果创建.gitignore配置规范契约
