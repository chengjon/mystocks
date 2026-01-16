# MyStocks 项目文件目录整理方案

**版本**: v1.4（根据用户建议修改）
**创建日期**: 2026-01-13
**审核日期**: 2026-01-13
**审核人**: Gemini CLI Agent, 用户
**状态**: 待审批

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [Phase 1 回顾](#2-phase-1-回顾)
3. [__init__.py 规范](#3-__initpy-规范)
4. [Phase 2: src/ 目录整理方案](#4-phase-2-src-目录整理方案)
5. [Phase 3: docs/ 目录整理方案](#5-phase-3-docs-目录整理方案)
6. [Phase 4: scripts/ 目录整理方案](#6-phase-4-scripts-目录整理方案)
7. [文件/文件夹迁移映射表](#7-文件文件夹迁移映射表)
8. [禁止移动列表](#8-禁止移动列表)
9. [缺失文件处理流程](#9-缺失文件处理流程)
10. [文件删除规则](#10-文件删除规则)
11. [持续合规监控](#11-持续合规监控)
12. [风险评估与回滚策略](#12-风险评估与回滚策略)
13. [验收标准](#13-验收标准)
14. [执行规范](#14-执行规范)
15. [时间估算](#15-时间估算)

---

## 1. 执行摘要

### 背景
项目经过长期开发，目录结构变得臃肿混乱：
- `src/` 目录包含 40+ 子目录，职责边界模糊
- `docs/` 目录有 44 个子目录，文档组织无章法
- `scripts/` 目录有 40+ 子目录，脚本用途不明确

### 目标
通过分阶段整理，建立清晰的目录结构，降低维护成本，提高开发效率。

### 范围

| Phase | 内容 | 状态 |
|-------|------|------|
| Phase 1 | 根目录基准文件恢复 | ✅ 已完成 |
| Phase 2 | src/ 目录整理 | ⏳ 待审批 |
| Phase 3 | docs/ 目录整理 | ⏳ 待审批 |
| Phase 4 | scripts/ 目录整理 | ⏳ 待审批 |

### 用户建议采纳情况

| 建议 | 采纳情况 |
|------|---------|
| `__init__.py` 使用规范 | ✅ 已采纳 |
| 缺失文件处理流程（查找→历史→优化→新建） | ✅ 已采纳 |
| 文件夹/文件迁移映射表 | ✅ 已采纳 |
| 禁止移动的文件/文件夹列表 | ✅ 已采纳 |
| 删除文件需审批 | ✅ 已采纳 |
| 空目录可清除 | ✅ 已采纳 |
| 持续合规监控 | ✅ 已采纳 |

---

## 2. Phase 1 回顾

### 已完成工作

| 文件 | 操作 | 来源 |
|------|------|------|
| GEMINI.md | 恢复 | docs/guides/ → 根目录 |
| AGENTS.md | 恢复 | docs/guides/ → 根目录 |
| core.py | 创建 | 入口文件 (重导出 src.core) |
| data_access.py | 创建 | 入口文件 (重导出 src.data_access) |
| monitoring.py | 创建 | 入口文件 (重导出 src.monitoring) |
| unified_manager.py | 创建 | 入口文件 (重导出 src.core.unified_manager) |

### Phase 1 验证结果

```
✅ src.* 导入 - 全部正常
✅ 根目录入口点导入 - 全部正常
✅ 所有导入验证通过
```

### Phase 1 教训

- ❌ 问题：未提前检查是否存在同名文件
- ❌ 问题：未使用 git 历史中的原始模板
- ❌ 问题：直接执行而未先出方案审批

---

## 3. __init__.py 规范

### 3.1 使用原则

| 场景 | 是否需要 __init__.py | 说明 |
|------|---------------------|------|
| 独立功能模块（需被导入） | ✅ 必须 | 作为子包管理，有专属初始化逻辑 |
| 存放辅助模块（仅存放，不独立导入） | ❌ 可选 | 仅作为普通文件夹 |
| 顶层包目录 | ✅ 推荐 | 保证兼容性，控制公共 API |

### 3.2 最佳实践

**推荐**：即使 Python 3.3+ 支持无 `__init__.py` 的命名空间包，普通项目仍推荐显式添加。

### 3.3 __init__.py 模板

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[模块名称]

模块职责说明...

创建日期: YYYY-MM-DD
版本: X.X.X
作者: JohnC& AI Dev Team (Claude, OpenCode, Gemini, IFLOW)
"""

# 版本信息
__version__ = "1.0.0"

# 作者信息
AUTHOR = "JohnC& AI Dev Team (Claude, OpenCode, Gemini, IFLOW)"

# 公共 API 定义
__all__ = [
    "ClassName",
    "function_name",
    "CONSTANT_NAME",
]

# 初始化逻辑（如需要）
def _init_module():
    """模块初始化逻辑"""
    pass

_init_module()
```

### 3.4 各 Phase __init__.py 要求

| Phase | 目录 | __init__.py 要求 |
|-------|------|-----------------|
| Phase 2 | src/*/ | ✅ 所有子目录必须有 |
| Phase 4 | scripts/*/ | ✅ 所有子目录必须有 |

---

## 4. Phase 2: src/ 目录整理方案

### 4.1 目标结构

```
src/
├── domain/                     # 领域层
│   ├── market_data/
│   ├── trading/
│   ├── portfolio/
│   ├── monitoring/
│   └── __init__.py
├── application/                # 应用层
│   ├── services/
│   ├── workflows/
│   ├── coordinators/
│   └── __init__.py
├── interfaces/                 # 接口层
│   ├── adapters/
│   ├── api/
│   ├── cli/
│   └── __init__.py
├── infrastructure/             # 基础设施层
│   ├── data_access/
│   ├── storage/
│   ├── messaging/
│   ├── logging/
│   ├── cache/
│   └── __init__.py
├── core/                       # 核心模块
│   ├── config/
│   ├── security/
│   ├── exceptions/
│   ├── patterns/
│   └── __init__.py
├── utils/                      # 工具层
│   ├── helpers/
│   ├── validators/
│   ├── converters/
│   └── __init__.py
├── ml_strategy/                # ML策略
│   ├── models/
│   ├── training/
│   ├── backtesting/
│   └── __init__.py
├── gpu/                        # GPU加速
│   ├── acceleration/
│   ├── resources/
│   └── __init__.py
└── __init__.py
```

### 4.2 迁移映射表

见第 7 节。

---

## 5. Phase 3: docs/ 目录整理方案

### 5.1 目标结构

```
docs/
├── getting-started/            # 入门指南
├── architecture/               # 架构设计
├── api/                        # API参考
├── guides/                     # 使用指南
├── references/                 # 参考文档
├── security/                   # 安全文档
├── deployment/                 # 部署文档
├── testing/                    # 测试文档
├── legacy/                     # 归档文档 (只读)
└── README.md
```

---

## 6. Phase 4: scripts/ 目录整理方案

### 6.1 目标结构

```
scripts/
├── runtime/                    # 运行时脚本
├── maintenance/                # 维护脚本
├── database/                   # 数据库脚本
├── deployment/                 # 部署脚本
├── testing/                    # 测试脚本
├── development/                # 开发工具
├── analysis/                   # 分析脚本
├── data-operations/            # 数据操作
├── security/                   # 安全脚本
├── archive/                    # 归档脚本
└── utils/                      # 实用工具
```

---

## 7. 文件/文件夹迁移映射表

### 7.1 Phase 2 完整迁移映射表（src/）

#### 7.1.1 保留目录（无需操作）

| 原路径 | 新路径 | 操作 | 风险 | 回滚方法 |
|--------|--------|------|------|---------|
| src/domain/ | src/domain/ | 保留 | 低 | 无需回滚 |
| src/application/services/ | src/application/services/ | 保留 | 低 | 无需回滚 |
| src/core/ | src/core/ | 保留 | 低 | 无需回滚 |
| src/utils/ | src/utils/ | 保留 | 低 | 无需回滚 |
| src/ml_strategy/ | src/ml_strategy/ | 保留 | 低 | 无需回滚 |
| src/gpu/ | src/gpu/ | 保留 | 低 | 无需回滚 |

#### 7.1.2 移动目录

| 原路径 | 新路径 | 操作 | 风险 | 回滚方法 |
|--------|--------|------|------|---------|
| src/adapters/ | src/interfaces/adapters/ | 移动 | 中 | `mv src/interfaces/adapters/ src/adapters/` |
| src/data_access/ | src/infrastructure/data_access/ | 移动 | 中 | `mv src/infrastructure/data_access/ src/data_access/` |
| src/monitoring/ | src/domain/monitoring/ | 移动 | 高 | `mv src/domain/monitoring/ src/monitoring/` |
| src/backtesting/ | src/ml_strategy/backtesting/ | 移动 | 中 | `mv src/ml_strategy/backtesting/ src/backtesting/` |
| src/db_manager/ | src/infrastructure/storage/ | 移动 | 高 | `mv src/infrastructure/storage/db_manager/ src/db_manager/` |

#### 7.1.3 合并目录

| 原路径 | 目标目录 | 操作 | 风险 | 回滚方法 |
|--------|---------|------|------|---------|
| src/interface/ | src/interfaces/api/ | 合并 | 高 | 需手动从 git 恢复 |
| src/interfaces/ | src/interfaces/ | 合并 | 中 | 需手动合并 |
| src/database/ | src/infrastructure/data_access/ | 合并 | 高 | 需手动合并 |
| src/api/ | src/interfaces/api/ | 合并 | 中 | 需手动合并 |

### 7.2 Phase 3 迁移映射表（docs/）

见完整文档。

### 7.3 Phase 4 迁移映射表（scripts/）

见完整文档。

---

## 8. 禁止移动列表

### 8.1 禁止移动规则

| 路径 | 原因 | 备注 |
|------|------|------|
| `src/temp/` | 临时文件目录 | 但需审批是否删除 |
| `src/mock/` | 符号链接到根目录 | 保持链接 |
| `.git/` | Git 版本控制 | 永远不要移动 |
| `.github/` | CI/CD 配置 | 永远不要移动 |
| `.claude/` | Claude Code 配置 | 永远不要移动 |
| `.opencode/` | OpenCode 配置 | 永远不要移动 |

---

## 9. 缺失文件处理流程

### 9.1 处理优先级

| 优先级 | 步骤 | 说明 |
|--------|------|------|
| **1** | 项目内查找 | 从项目其他目录寻找相似文件 |
| **2** | Git 历史查找 | 从 git 历史中恢复历史版本 |
| **3** | 历史版本优化 | 结合当前项目状况优化历史版本 |
| **4** | AI 新建 | 仅当前三步都失败时才允许新建 |

---

## 10. 文件删除规则

### 10.1 核心原则

| 规则 | 说明 |
|------|------|
| **禁止删除** | 不得随意删除文件，所有删除需审批 |
| **空目录可清** | 空目录（确认无用后）可直接清除 |
| **审批流程** | 删除文件需列成列表，说明原因，审批后执行 |
| **保留备份** | 删除前建议备份到 archive/ 目录 |

### 10.2 删除审批清单

| Phase | 路径 | 类型 | 原因 | 建议操作 |
|-------|------|------|------|---------|
| Phase 2 | src/temp/ | 目录 | 临时文件目录 | 删除 |
| | src/backup_recovery/ | 目录 | 功能重复 | 删除 |
| | src/contract_testing/ | 目录 | 已迁移 | 删除 |
| | src/backup/ | 目录 | 功能重复 | 合并或删除 |
| Phase 3 | docs/docs/ | 目录 | 空聚合 | 删除 |
| | docs/reports/ | 目录 | 空聚合 | 删除 |
| | docs/archived/ | 目录 | 重复 | 合并后删除 |
| | docs/归档文档/ | 目录 | 中文目录 | 删除 |
| Phase 4 | scripts/feedback/ | 目录 | 已废弃 | 删除 |
| | scripts/generate-types/ | 目录 | 已迁移 | 删除 |

---

## 11. 持续合规监控

### 11.1 监控策略概述

清理完成后，需要建立自动化监控机制，确保新生成的文件符合项目规则。

### 11.2 监控手段矩阵

| 手段 | 时机 | 检测内容 | 自动化程度 |
|------|------|---------|-----------|
| **Pre-commit Hooks** | git commit 前 | 文件命名、目录结构、__init__.py | ✅ 全自动 |
| **CI/CD 检查** | PR/Merge 时 | 目录结构、导入路径、测试 | ✅ 全自动 |
| **定时任务** | 每日/每周 | 目录合规性、文件统计 | ✅ 全自动 |
| **GitHub Actions** | 定时/事件触发 | 综合检查报告 | ✅ 全自动 |
| **文件监控** | 实时 | 文件变化监控 | ✅ 全自动 |

### 11.3 Pre-commit Hooks 配置

```yaml
# .pre-commit-hooks.yaml
# 在 git commit 前自动检查

- id: check-directory-structure
  name: 检查目录结构
  description: 验证新文件是否符合项目目录规范
  entry: python scripts/hooks/check_directory_structure.py
  language: system
  stages: [pre-commit]
  pass_filenames: false

- id: check-init-py
  name: 检查 __init__.py
  description: 验证新子目录是否包含 __init__.py
  entry: python scripts/hooks/check_init_py.py
  language: system
  stages: [pre-commit]
  pass_filenames: false

- id: check-file-naming
  name: 检查文件命名
  description: 验证文件名是否符合命名规范（英文、snake_case）
  entry: python scripts/hooks/check_file_naming.py
  language: system
  stages: [pre-commit]
  pass_filenames: false
```

### 11.4 监控检查脚本

#### 11.4.1 目录结构检查脚本

```python
# scripts/hooks/check_directory_structure.py
#!/usr/bin/env python3
"""
目录结构合规性检查脚本

检查新创建的文件/目录是否符合项目规范：
1. 新文件必须在允许的目录范围内
2. 新子目录必须包含 __init__.py
3. 不允许在禁止目录中创建文件
"""

import os
import sys
from pathlib import Path

# 允许的顶层目录
ALLOWED_TOP_DIRS = [
    "src/",
    "scripts/",
    "docs/",
    "tests/",
    "config/",
]

# 禁止创建文件的目录
FORBIDDEN_DIRS = [
    "src/temp/",
    "docs/docs/",
    "docs/reports/",
]

# 允许的目录结构模板
DIRECTORY_TEMPLATE = {
    "src/": [
        "domain/",
        "application/",
        "interfaces/",
        "infrastructure/",
        "core/",
        "utils/",
        "ml_strategy/",
        "gpu/",
    ],
    "scripts/": [
        "runtime/",
        "maintenance/",
        "database/",
        "deployment/",
        "testing/",
        "development/",
        "analysis/",
        "data-operations/",
        "security/",
        "archive/",
        "utils/",
    ],
    "docs/": [
        "getting-started/",
        "architecture/",
        "api/",
        "guides/",
        "references/",
        "security/",
        "deployment/",
        "testing/",
        "legacy/",
    ],
}


def get_staged_changes():
    """获取暂存的变更"""
    result = os.popen("git diff --cached --name-only").read()
    return [Path(f) for f in result.strip().split("\n") if f]


def check_file_location(file_path):
    """检查文件是否在允许的位置"""
    file_str = str(file_path)
    
    # 检查是否在允许的顶层目录下
    in_allowed_dir = any(file_str.startswith(d) for d in ALLOWED_TOP_DIRS)
    if not in_allowed_dir:
        print(f"❌ 文件 {file_path} 不在允许的目录范围内")
        print(f"   允许的顶层目录: {ALLOWED_TOP_DIRS}")
        return False
    
    return True


def check_init_py(file_path):
    """检查新子目录是否包含 __init__.py"""
    file_str = str(file_path)
    
    # 如果创建的是目录
    if file_path.is_dir():
        init_file = file_path / "__init__.py"
        if not init_file.exists():
            print(f"❌ 新目录 {file_path} 缺少 __init__.py")
            return False
    
    return True


def check_forbidden_dir(file_path):
    """检查是否在禁止的目录中创建文件"""
    file_str = str(file_path)
    
    for forbidden in FORBIDDEN_DIRS:
        if file_str.startswith(forbidden):
            print(f"❌ 不允许在 {forbidden} 中创建文件")
            return False
    
    return True


def main():
    """主函数"""
    staged_files = get_staged_changes()
    
    if not staged_files:
        print("✅ 没有暂存的变更")
        return 0
    
    errors = []
    
    for file_path in staged_files:
        # 检查文件位置
        if not check_file_location(file_path):
            errors.append(f"位置违规: {file_path}")
        
        # 检查禁止目录
        if not check_forbidden_dir(file_path):
            errors.append(f"禁止目录: {file_path}")
        
        # 检查 __init__.py
        if file_path.is_dir():
            if not check_init_py(file_path):
                errors.append(f"缺少 __init__.py: {file_path}")
    
    if errors:
        print("\n❌ 目录结构检查未通过")
        for error in errors:
            print(f"   - {error}")
        print("\n请修复上述问题后重新提交")
        return 1
    
    print("✅ 目录结构检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

#### 11.4.2 文件命名检查脚本

```python
# scripts/hooks/check_file_naming.py
#!/usr/bin/env python3
"""
文件命名规范检查脚本

检查文件名是否符合规范：
1. 必须使用英文
2. Python 文件使用 snake_case
3. 不允许使用中文、空格、特殊字符
"""

import os
import sys
import re
from pathlib import Path


def get_staged_changes():
    """获取暂存的变更"""
    result = os.popen("git diff --cached --name-only").read()
    return [Path(f) for f in result.strip().split("\n") if f]


def is_valid_filename(filename):
    """检查文件名是否规范"""
    # 允许的字符：英文、数字、下划线、连字符、点
    pattern = r'^[a-zA-Z0-9_\-\.]+$'
    
    # 禁止使用中文
    if re.search(r'[\u4e00-\u9fff]', str(filename)):
        return False, "文件名包含中文字符"
    
    # 检查是否包含空格
    if ' ' in str(filename):
        return False, "文件名包含空格"
    
    # Python 文件必须使用 snake_case
    if str(filename).endswith('.py'):
        if not re.match(r'^[a-z][a-z0-9_]*\.py$', str(filename)):
            return False, "Python 文件应使用 snake_case 命名"
    
    return True, None


def main():
    """主函数"""
    staged_files = get_staged_changes()
    
    if not staged_files:
        print("✅ 没有暂存的变更")
        return 0
    
    errors = []
    
    for file_path in staged_files:
        valid, reason = is_valid_filename(file_path.name)
        if not valid:
            errors.append(f"{file_path}: {reason}")
    
    if errors:
        print("\n❌ 文件命名检查未通过")
        for error in errors:
            print(f"   - {error}")
        print("\n请修复上述问题后重新提交")
        return 1
    
    print("✅ 文件命名检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

#### 11.4.3 __init__.py 检查脚本

```python
# scripts/hooks/check_init_py.py
#!/usr/bin/env python3
"""
__init__.py 规范检查脚本

检查新子目录是否包含规范的 __init__.py：
1. 必须包含 __version__
2. 必须包含 AUTHOR
3. 必须包含 __all__
"""

import os
import sys
from pathlib import Path


def get_staged_changes():
    """获取暂存的变更"""
    result = os.popen("git diff --cached --name-only").read()
    return [Path(f) for f in result.strip().split("\n") if f]


def check_init_py_content(init_file):
    """检查 __init__.py 内容是否规范"""
    if not init_file.exists():
        return False, "文件不存在"
    
    content = init_file.read_text()
    
    errors = []
    
    if "__version__" not in content:
        errors.append("缺少 __version__")
    
    if "AUTHOR" not in content:
        errors.append("缺少 AUTHOR")
    
    if "__all__" not in content:
        errors.append("缺少 __all__")
    
    if errors:
        return False, "; ".join(errors)
    
    return True, None


def main():
    """主函数"""
    staged_files = get_staged_changes()
    
    if not staged_files:
        print("✅ 没有暂存的变更")
        return 0
    
    errors = []
    
    for file_path in staged_files:
        if file_path.is_dir():
            init_file = file_path / "__init__.py"
            if init_file.exists():
                valid, reason = check_init_py_content(init_file)
                if not valid:
                    errors.append(f"{file_path}/__init__.py: {reason}")
    
    if errors:
        print("\n❌ __init__.py 检查未通过")
        for error in errors:
            print(f"   - {error}")
        print("\n请修复上述问题后重新提交")
        return 1
    
    print("✅ __init__.py 检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### 11.5 CI/CD 检查配置

```yaml
# .github/workflows/directory-compliance.yml
name: Directory Compliance Check

on:
  pull_request:
    paths:
      - 'src/**'
      - 'scripts/**'
      - 'docs/**'
  schedule:
    # 每周日凌晨 2 点执行全面检查
    - cron: '0 2 * * 0'

jobs:
  check-compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Check directory structure
        run: |
          echo "=== 目录结构检查 ==="
          python scripts/hooks/check_directory_structure.py || exit 1
      
      - name: Check file naming
        run: |
          echo "=== 文件命名检查 ==="
          python scripts/hooks/check_file_naming.py || exit 1
      
      - name: Check __init__.py
        run: |
          echo "=== __init__.py 检查 ==="
          python scripts/hooks/check_init_py.py || exit 1
      
      - name: Check for orphaned files
        run: |
          echo "=== 孤立文件检查 ==="
          python scripts/hooks/check_orphaned_files.py || exit 1
      
      - name: Generate compliance report
        run: |
          python scripts/hooks/generate_compliance_report.py
          
      - name: Upload compliance report
        uses: actions/upload-artifact@v4
        with:
          name: compliance-report
          path: reports/compliance/

  weekly-full-scan:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Full directory scan
        run: |
          python scripts/hooks/full_directory_scan.py --output reports/compliance/full_scan_$(date +%Y%m%d).json
      
      - name: Upload full scan report
        uses: actions/upload-artifact@v4
        with:
          name: full-scan-report
          path: reports/compliance/full_scan_*.json
```

### 11.6 定时合规报告

```python
# scripts/hooks/generate_compliance_report.py
#!/usr/bin/env python3
"""
合规报告生成脚本

生成项目目录结构合规报告：
1. 目录结构合规性
2. __init__.py 完整性
3. 文件命名规范性
4. 禁止目录检测
"""

import json
from datetime import datetime
from pathlib import Path


def generate_report():
    """生成合规报告"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "project_root": "/opt/claude/mystocks_spec",
        "checks": {},
        "summary": {
            "total_issues": 0,
            "critical_issues": 0,
            "warning_issues": 0,
        }
    }
    
    # 检查 1: 目录结构
    report["checks"]["directory_structure"] = check_directory_structure()
    
    # 检查 2: __init__.py 完整性
    report["checks"]["init_py"] = check_init_py_completeness()
    
    # 检查 3: 文件命名
    report["checks"]["file_naming"] = check_file_naming()
    
    # 检查 4: 禁止目录
    report["checks"]["forbidden_dirs"] = check_forbidden_dirs()
    
    # 汇总
    for check_name, check_result in report["checks"].items():
        if not check_result["passed"]:
            report["summary"]["total_issues"] += check_result["issue_count"]
            if check_result["severity"] == "critical":
                report["summary"]["critical_issues"] += check_result["issue_count"]
            else:
                report["summary"]["warning_issues"] += check_result["issue_count"]
    
    return report


def check_directory_structure():
    """检查目录结构"""
    # 实现细节...
    pass


def check_init_py_completeness():
    """检查 __init__.py 完整性"""
    # 实现细节...
    pass


def check_file_naming():
    """检查文件命名"""
    # 实现细节...
    pass


def check_forbidden_dirs():
    """检查禁止目录"""
    # 实现细节...
    pass


def main():
    """主函数"""
    report = generate_report()
    
    # 保存报告
    report_path = Path("/opt/claude/mystocks_spec/reports/compliance")
    report_path.mkdir(parents=True, exist_ok=True)
    
    report_file = report_path / f"compliance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    
    # 输出摘要
    print(f"合规报告已生成: {report_file}")
    print(f"问题总数: {report['summary']['total_issues']}")
    print(f"严重问题: {report['summary']['critical_issues']}")
    print(f"警告问题: {report['summary']['warning_issues']}")
    
    return 0


if __name__ == "__main__":
    main()
```

### 11.7 监控效果矩阵

| 监控手段 | 防止问题 | 自动化程度 | 拦截位置 |
|---------|---------|-----------|---------|
| Pre-commit Hooks | 新文件命名不规范 | ✅ 全自动 | git commit 前 |
| Pre-commit Hooks | 新目录缺少 __init__.py | ✅ 全自动 | git commit 前 |
| CI/CD 检查 | 目录结构混乱 | ✅ 全自动 | PR 时 |
| CI/CD 检查 | 导入路径错误 | ✅ 全自动 | PR 时 |
| 定时任务 | 规则遗漏 | ✅ 全自动 | 每日/每周 |
| GitHub Actions | 综合合规性 | ✅ 全自动 | 定时/事件 |

---

## 12. 风险评估与回滚策略

### 12.1 整体风险矩阵

| Phase | 风险等级 | 主要风险 | 影响范围 |
|-------|---------|---------|---------|
| Phase 1 | 低 | 导入路径变更 | 根目录脚本 |
| Phase 2 | 高 | 导入路径、循环依赖、误删 | 整个项目 |
| Phase 3 | 中 | 文档链接失效 | 文档站点 |
| Phase 4 | 中 | CI/CD 失效、cron 失效 | 部署流水线 |

### 12.2 通用回滚策略

```bash
# Git 回滚（推荐）
git checkout HEAD~1 -- src/ docs/ scripts/

# 使用迁移映射表回滚
python scripts/dev/rollback_migration.py --input migration_map.csv
```

---

## 13. 验收标准

### 13.1 __init__.py 规范（强制）

- 所有功能子目录必须包含 `__init__.py`
- `__init__.py` 必须包含：`__version__`、`AUTHOR`、`__all__`

### 13.2 Phase 2-4 验收标准

| 标准 | Phase 2 | Phase 3 | Phase 4 |
|------|---------|---------|---------|
| 目录数量 | 10-12 个 | 12-15 个 | 10-12 个 |
| 职责清晰 | ✅ | ✅ | ✅ |
| 无 temp/ 目录 | ✅ | - | - |
| 无聚合目录 | - | ✅ | - |
| 无时间标记 | - | - | ✅ |
| __init__.py 规范 | ✅ | - | ✅ |
| CI 通过 | ✅ | ✅ | ✅ |
| 无误删文件 | ✅ | ✅ | ✅ |
| 监控脚本就位 | ✅ | ✅ | ✅ |

---

## 14. 执行规范

### 14.1 自动化优先原则

所有重构操作应使用自动化脚本执行，减少手动错误。

### 14.2 全面测试验证

每完成一个小范围重构任务后，立即运行完整测试套件。

---

## 15. 时间估算

| Phase | 估算时间 |
|-------|---------|
| Phase 2: src/ 整理 | 22.5 小时 |
| Phase 3: docs/ 整理 | 9.5 小时 |
| Phase 4: scripts/ 整理 | 10.5 小时 |
| **总计** | **42.5 小时** |

---

## 审批意见

请审批以下内容：

1. **是否同意 Phase 1 作为已完成工作？**
2. **是否批准 Phase 2 方案？**
3. **是否批准 Phase 3 方案？**
4. **是否批准 Phase 4 方案？**
5. **是否批准删除审批清单中的待删除项？**
6. **是否批准持续合规监控方案？**

---

**文档版本**: v1.4
**作者**: Sisyphus AI Agent
**审核人**: Gemini CLI Agent, 用户
**创建日期**: 2026-01-13
