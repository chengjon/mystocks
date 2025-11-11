# 文件组织规则 (File Organization Rules)

> **版本**: 1.0
> **最后更新**: 2025-11-10
> **状态**: 生效中

## 📌 核心原则

**Philosophy**: 保持根目录清洁、最小化，按功能进行逻辑分类。每个文件都应该有明确的、基于规则的位置。

---

## 🗂️ 根目录标准

### 只允许这5个核心文件在根目录

```
/
├── README.md           # 项目概述和主要文档
├── CLAUDE.md          # Claude Code 集成指南
├── CHANGELOG.md       # 版本历史和变更记录
├── requirements.txt   # Python 依赖
└── .mcp.json         # MCP 服务器配置
```

**所有其他文件必须组织到子目录中**。

---

## 📁 目录结构和规则

### 1. **scripts/** - 所有可执行脚本

按功能组织为4个类别：

#### **scripts/tests/** - 测试文件
- **匹配模式**: 文件前缀为 `test_`
- **用途**: 单元测试、集成测试、验收测试
- **示例**:
  - `test_config_driven_table_manager.py`
  - `test_financial_adapter.py`
  - `test_dual_database_architecture.py`
- **特殊文件**: `test_requirements.txt`, `coverage.xml`

#### **scripts/runtime/** - 生产运行时脚本
- **匹配模式**: 文件前缀为 `run_`, `save_`, `monitor_`, 或 `*_demo.py`
- **用途**: 生产数据收集、监控、演示
- **示例**:
  - `run_realtime_market_saver.py`
  - `save_realtime_data.py`
  - `system_demo.py`

#### **scripts/database/** - 数据库操作
- **匹配模式**: 文件前缀为 `check_`, `verify_`, `create_`
- **用途**: 数据库初始化、验证、管理
- **示例**:
  - `check_tdengine_tables.py`
  - `verify_tdengine_deployment.py`
  - `create_monitoring_tables.py`

#### **scripts/dev/** - 开发工具
- **匹配模式**: 不符合其他类别的开发工具
- **用途**: 代码验证、测试工具、开发辅助
- **示例**:
  - `gpu_test_examples.py`
  - `validate_documentation_consistency.py`
- **特殊文件**: `git_commit_comments.txt`

---

### 2. **docs/** - 文档文件

#### **docs/guides/** - 用户和开发者指南
- **文件**: `QUICKSTART.md`, `IFLOW.md`, 教程文档
- **用途**: 快速入门指南、工作流文档

#### **docs/archived/** - 已废弃文档
- **文件**: `START_HERE.md`, `TASKMASTER_START_HERE.md`（保留供历史参考）
- **用途**: 保留旧文档但不影响当前文档
- **规则**: 归档时在文件顶部添加废弃通知

#### **docs/architecture/** - 架构设计文档
- **用途**: 系统设计、技术架构文档
- **示例**: 数据库设计文档、系统架构图

#### **docs/api/** - API 文档
- **用途**: API 参考、端点文档、SDK 指南

#### **docs/standards/** - 标准和规范
- **用途**: 项目规范、编码标准、流程文档
- **示例**:
  - `项目开发规范与指导文档.md`
  - `FILE_ORGANIZATION_RULES.md`（本文档）

---

### 3. **config/** - 配置文件

**所有配置文件**（不论扩展名）：
- **扩展名**: `.yaml`, `.yml`, `.ini`, `.toml`, `docker-compose.*.yml`
- **示例**:
  - `mystocks_table_config.yaml` - 表结构定义
  - `docker-compose.tdengine.yml` - Docker 设置
  - `pytest.ini` - 测试配置
  - `.readthedocs.yaml` - 文档构建配置

---

### 4. **reports/** - 生成的报告和分析

**匹配模式**: 由分析脚本生成的文件，如有重复则加时间戳
- **扩展名**: `.json`, `.txt`, 分析输出
- **示例**:
  - `database_assessment_20251019_165817.json`
  - `query_patterns_analysis.txt`
  - `dump_result.txt`
  - `WENCAI_INTEGRATION_FILES.txt`

**命名约定**: 对于时间戳文件使用 ISO 日期格式：`YYYYMMDD_HHMMSS`

---

## 🔄 文件生命周期管理

### Pre-Classification (主动预分类)

**创建新文件时**，直接放在正确位置：

1. **确定文件用途**: 测试？运行时？配置？文档？
2. **匹配规则**: 使用上述目录结构
3. **在正确位置创建**: 除非是5个核心文件之一，否则不要在根目录创建

#### ✅ 正确示例
```python
# 创建新测试文件
with open('scripts/tests/test_new_feature.py', 'w') as f:
    f.write(test_code)
```

#### ❌ 错误示例
```python
# 在根目录创建
with open('test_new_feature.py', 'w') as f:
    f.write(test_code)
```

---

### Post-Classification (响应式后分类)

**整理现有文件时**：

1. **识别错误放置的文件**: 使用 `ls` 或 `find` 列出根目录文件
2. **按规则分类**: 将每个文件与目录结构规则匹配
3. **规划重组**: 执行前创建分类计划
4. **使用 git mv**: 移动已跟踪的文件时保留文件历史
5. **更新引用**: 更新所有导入路径、文档链接
6. **验证**: 测试移动后的文件是否正常工作

#### 后分类工作流

```bash
# 1. 列出根目录文件（排除核心5个）
ls -1 | grep -v -E '^(README\.md|CLAUDE\.md|CHANGELOG\.md|requirements\.txt|\.mcp\.json)$'

# 2. 对每个文件，使用上述规则确定正确位置

# 3. 移动文件（对已跟踪文件使用 git mv）
git mv test_something.py scripts/tests/
git mv run_collector.py scripts/runtime/
git mv config.yaml config/
git mv analysis_report.txt reports/

# 4. 更新受影响文件中的引用

# 5. 用描述性消息提交
git commit -m "refactor: organize files according to directory structure rules"
```

---

## 🐍 脚本的导入路径管理

### 关键规则
所有嵌套目录中的脚本必须正确计算项目根目录。

### scripts/**/ 中脚本的标准模式

```python
import sys
import os
from pathlib import Path

# 计算项目根目录（从脚本位置向上3层）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 现在可以从项目根目录导入
from src.core import ConfigDrivenTableManager
from src.adapters.akshare_adapter import AkshareDataSource
from src.db_manager import DatabaseTableManager
```

### 说明
- 脚本位于 `scripts/tests/test_something.py`
- `__file__` → `scripts/tests/test_something.py`
- `os.path.dirname(__file__)` → `scripts/tests/`
- `os.path.dirname(os.path.dirname(__file__))` → `scripts/`
- `os.path.dirname(os.path.dirname(os.path.dirname(__file__)))` → 项目根目录 `/opt/claude/mystocks_spec/`

---

## 📝 Git 最佳实践

### 对已跟踪文件始终使用 `git mv`

#### ✅ 正确：保留文件历史
```bash
git mv old_location/file.py new_location/file.py
```

#### ❌ 错误：破坏文件历史
```bash
mv old_location/file.py new_location/file.py
git add new_location/file.py
```

### 对未跟踪文件
```bash
# 对尚未在 git 中的文件
mv untracked_file.log reports/
```

---

## ✅ 验证清单

文件重组后的检查项：

- [ ] 根目录只包含5个核心文件
- [ ] 所有脚本正确分类在 scripts/{tests,runtime,database,dev}
- [ ] 所有文档在 docs/{guides,archived,architecture,api,standards}
- [ ] 所有配置文件在 config/
- [ ] 所有报告在 reports/
- [ ] 所有移动的脚本已更新导入路径（3层 dirname）
- [ ] 所有文档链接已更新到新路径
- [ ] `git status` 显示移动（不是删除+添加）
- [ ] 重组后所有测试通过
- [ ] `scripts/README.md` 已更新

---

## ⚠️ 常见错误避免

1. **在根目录创建文件**: 始终使用子目录，除非是5个核心文件之一
2. **错误的导入路径**: 记住对嵌套目录中的脚本使用3层 dirname
3. **使用 `mv` 而不是 `git mv`**: 始终保留 git 历史
4. **忘记更新引用**: 检查所有导入、文档链接
5. **混合用途**: 不要把测试文件放在 runtime/，或配置文件放在 docs/

---

## 📚 参考文档

详细的目录内容和文件清单：
- **完整文档结构**: 参见 `docs/DOCUMENTATION_STRUCTURE.md`
- **脚本组织指南**: 参见 `scripts/README.md`
- **主要集成指南**: 参见 `CLAUDE.md`（完整项目上下文）

---

## 🔍 快速决策树

```
创建/移动文件？
│
├─ 是核心文件？(README/CLAUDE/CHANGELOG/requirements/.mcp.json)
│  └─ 是 → 放在根目录
│  └─ 否 → 继续
│
├─ 是脚本文件？(.py)
│  ├─ test_*.py → scripts/tests/
│  ├─ run_*, save_*, monitor_*, *_demo.py → scripts/runtime/
│  ├─ check_*, verify_*, create_* → scripts/database/
│  └─ 其他开发工具 → scripts/dev/
│
├─ 是文档文件？(.md, .rst, .txt)
│  ├─ 用户/开发指南 → docs/guides/
│  ├─ 已废弃文档 → docs/archived/
│  ├─ 架构设计 → docs/architecture/
│  ├─ API 文档 → docs/api/
│  └─ 标准规范 → docs/standards/
│
├─ 是配置文件？(.yaml, .yml, .ini, .toml, docker-compose.*)
│  └─ → config/
│
└─ 是报告/分析？(.json, .txt, 分析输出)
   └─ → reports/
```

---

## 📊 目录结构可视化

```
mystocks_spec/
├── README.md                    # ✅ 核心文件
├── CLAUDE.md                    # ✅ 核心文件
├── CHANGELOG.md                 # ✅ 核心文件
├── requirements.txt             # ✅ 核心文件
├── .mcp.json                    # ✅ 核心文件
│
├── scripts/                     # 📜 所有脚本
│   ├── tests/                   # 测试文件 (test_*.py)
│   ├── runtime/                 # 运行时脚本 (run_*, save_*, *_demo.py)
│   ├── database/                # 数据库操作 (check_*, verify_*, create_*)
│   └── dev/                     # 开发工具
│
├── docs/                        # 📚 所有文档
│   ├── guides/                  # 用户指南
│   ├── archived/                # 已废弃文档
│   ├── architecture/            # 架构文档
│   ├── api/                     # API 文档
│   └── standards/               # 标准规范（本文档在此）
│
├── config/                      # ⚙️ 所有配置
│   ├── *.yaml, *.yml
│   ├── *.ini, *.toml
│   └── docker-compose.*.yml
│
└── reports/                     # 📊 生成的报告
    ├── *_YYYYMMDD_HHMMSS.json
    └── *.txt (分析输出)
```

---

## 🎯 实施示例

### 场景1: 创建新的测试文件

```python
# ✅ 正确
# 直接在正确位置创建
import os
test_file_path = 'scripts/tests/test_new_api.py'
with open(test_file_path, 'w') as f:
    f.write("""import sys
import os

# 计算项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.core import ConfigDrivenTableManager

def test_new_api():
    pass
""")
```

### 场景2: 移动错误放置的文件

```bash
# 发现根目录有错误文件
$ ls -1
README.md
CLAUDE.md
analysis_report.json        # ❌ 应该在 reports/
test_feature.py            # ❌ 应该在 scripts/tests/
app_config.yaml            # ❌ 应该在 config/

# 使用 git mv 移动（保留历史）
git mv analysis_report.json reports/
git mv test_feature.py scripts/tests/
git mv app_config.yaml config/

# 更新 test_feature.py 的导入路径（如果需要）
# 提交变更
git commit -m "refactor: organize misplaced files according to directory rules"
```

### 场景3: 添加新的配置文件

```bash
# ✅ 正确：直接在 config/ 创建
cat > config/new_feature.yaml <<EOF
feature:
  enabled: true
  options:
    - option1
    - option2
EOF

# ❌ 错误：在根目录创建
# cat > new_feature.yaml <<EOF
```

---

## 📞 支持和更新

- **问题反馈**: 如果规则不清晰或有冲突，请更新本文档
- **规则更新**: 任何目录结构变更都应同步更新本文档
- **版本控制**: 重大变更时更新文档顶部的版本号

---

**最后更新**: 2025-11-10
**维护者**: Project Team
**状态**: ✅ 生效中
