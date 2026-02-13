# 任务分解：项目目录结构全面重组

## 变更标识
- **Change ID**: `reorganize-project-directory-structure`
- **状态**: `proposed`
- **总任务数**: 25
- **预计工期**: 3-4 天

---

## 阶段 0：准备工作

### Task 0.1：创建安全快照
- **状态**: `pending`
- **优先级**: `critical`
- **预计耗时**: 5 分钟
- **描述**: 在任何操作之前创建 git tag 作为回滚锚点
- **操作**:
  ```bash
  git tag backup/before-reorg-$(date +%Y%m%d)
  git stash list > /tmp/stash-backup.txt
  ```
- **验证**: `git tag -l 'backup/*'` 显示新 tag
- **回滚**: N/A（这是回滚基础）

### Task 0.2：生成当前状态基线报告
- **状态**: `pending`
- **优先级**: `high`
- **预计耗时**: 10 分钟
- **描述**: 记录整理前的目录/文件数量、磁盘占用，作为对比基准
- **操作**:
  ```bash
  echo "=== 基线报告 $(date) ===" > /tmp/reorg-baseline.txt
  find . -maxdepth 1 -type d ! -name '.*' | wc -l >> /tmp/reorg-baseline.txt
  find . -maxdepth 1 -type f ! -name '.*' | wc -l >> /tmp/reorg-baseline.txt
  du -sh . >> /tmp/reorg-baseline.txt
  find . -maxdepth 1 -type d ! -name '.*' | sort >> /tmp/reorg-baseline.txt
  find . -maxdepth 1 -type f ! -name '.*' | sort >> /tmp/reorg-baseline.txt
  ```
- **验证**: 基线报告文件存在且内容完整

### Task 0.3：验证禁区清单
- **状态**: `pending`
- **优先级**: `critical`
- **预计耗时**: 5 分钟
- **描述**: 确认 23 个隐藏目录 + 12 个隐藏文件全部存在，记录校验和
- **操作**:
  ```bash
  find . -maxdepth 1 -name '.*' -type d | sort > /tmp/dotdirs-before.txt
  find . -maxdepth 1 -name '.*' -type f | sort > /tmp/dotfiles-before.txt
  ```
- **验证**: 文件列表与设计文档中的禁区清单一致

---

## 阶段 1：垃圾清除（预计释放 ~237GB）

### Task 1.1：清除 logs/ 目录
- **状态**: `pending`
- **优先级**: `high`
- **预计耗时**: 15 分钟
- **描述**: 删除 236GB 的日志文件。执行前检查是否有进程正在写入
- **前置依赖**: Task 0.1, Task 0.2, Task 0.3
- **操作**:
  ```bash
  # 安全检查：确认无活跃写入
  lsof 2>/dev/null | grep "$(pwd)/logs/" && echo "⚠️ 有进程正在写入 logs/，请先停止" || echo "✅ 安全，可以删除"
  # 如果安全，执行删除
  rm -rf logs/
  ```
- **验证**: `ls -d logs/ 2>/dev/null` 返回空；`du -sh .` 显示空间释放
- **回滚**: `git checkout backup/before-reorg-$(date +%Y%m%d) -- logs/`（注意：如果 logs/ 未被 git 跟踪则无法回滚，但日志本身是可再生的）

### Task 1.2：清除 bak/ 目录
- **状态**: `pending`
- **优先级**: `high`
- **预计耗时**: 10 分钟
- **描述**: 删除 554MB 的旧备份（含完整 node_modules 副本）
- **前置依赖**: Task 0.1
- **操作**:
  ```bash
  # 先检查是否有非备份内容
  ls bak/ | head -20
  rm -rf bak/
  ```
- **验证**: `ls -d bak/ 2>/dev/null` 返回空

### Task 1.3：清除 htmlcov/ 目录
- **状态**: `pending`
- **优先级**: `medium`
- **预计耗时**: 5 分钟
- **描述**: 删除 90MB 的覆盖率报告（可随时重新生成）
- **前置依赖**: Task 0.1
- **操作**:
  ```bash
  rm -rf htmlcov/
  ```
- **验证**: 目录不存在

### Task 1.4：清除根目录临时文件
- **状态**: `pending`
- **优先级**: `medium`
- **预计耗时**: 10 分钟
- **描述**: 删除根目录的 .log 文件、coverage 文件、临时输出
- **前置依赖**: Task 0.1
- **操作**:
  ```bash
  rm -f *.log .coverage coverage.xml
  rm -f test-results.json pytest-results.json
  ```
- **验证**: `find . -maxdepth 1 -name '*.log' -o -name '.coverage' -o -name 'coverage.xml' | wc -l` 返回 0

### Task 1.5：阶段 1 验证
- **状态**: `pending`
- **优先级**: `critical`
- **前置依赖**: Task 1.1, Task 1.2, Task 1.3, Task 1.4
- **操作**:
  ```bash
  # 禁区完整性检查
  diff <(find . -maxdepth 1 -name '.*' -type d | sort) /tmp/dotdirs-before.txt
  diff <(find . -maxdepth 1 -name '.*' -type f | sort) /tmp/dotfiles-before.txt
  # 功能验证
  python -c "from src.core import *; print('✅ src imports OK')"
  ```
- **验证**: 禁区 diff 为空；import 成功

---

## 阶段 2：根文件归位

### Task 2.1：移动 TASK-*.md 报告文件
- **状态**: `pending`
- **优先级**: `high`
- **预计耗时**: 10 分钟
- **描述**: 将根目录的 TASK-*.md 文件移入 docs/reports/tasks/
- **前置依赖**: Task 1.5
- **操作**:
  ```bash
  mkdir -p docs/reports/tasks
  for f in TASK-*.md; do
    [ -f "$f" ] && git mv "$f" docs/reports/tasks/
  done
  ```
- **验证**: `find . -maxdepth 1 -name 'TASK-*.md' | wc -l` 返回 0

### Task 2.2：移动根目录散落的文档文件
- **状态**: `pending`
- **优先级**: `high`
- **预计耗时**: 15 分钟
- **描述**: 将非白名单的 .md 文件移入 docs/ 对应子目录
- **前置依赖**: Task 1.5
- **操作**:
  ```bash
  # 保留白名单：README.md, CLAUDE.md, IFLOW.md, AGENTS.md
  # 其余 .md 文件按内容分类移动
  mkdir -p docs/reports/misc
  for f in *.md; do
    case "$f" in
      README.md|CLAUDE.md|IFLOW.md|AGENTS.md) continue ;;
      *) git mv "$f" docs/reports/misc/ ;;
    esac
  done
  ```
- **验证**: 根目录 .md 文件仅剩白名单中的 4 个

### Task 2.3：移动根目录散落的 Python 脚本
- **状态**: `pending`
- **优先级**: `medium`
- **预计耗时**: 10 分钟
- **描述**: 将非兼容入口的 .py 文件移入 scripts/dev/
- **前置依赖**: Task 1.5
- **操作**:
  ```bash
  # 保留白名单：core.py, data_access.py, monitoring.py, unified_manager.py, __init__.py
  mkdir -p scripts/dev
  for f in *.py; do
    case "$f" in
      core.py|data_access.py|monitoring.py|unified_manager.py|__init__.py) continue ;;
      *) git mv "$f" scripts/dev/ ;;
    esac
  done
  ```
- **验证**: 根目录 .py 文件仅剩白名单中的 5 个

### Task 2.4：阶段 2 验证
- **状态**: `pending`
- **优先级**: `critical`
- **前置依赖**: Task 2.1, Task 2.2, Task 2.3
- **操作**:
  ```bash
  # 根文件计数
  echo "根文件数: $(find . -maxdepth 1 -type f ! -name '.*' | wc -l)"
  # 禁区完整性
  diff <(find . -maxdepth 1 -name '.*' -type d | sort) /tmp/dotdirs-before.txt
  # 功能验证
  python -c "from src.core import *; print('✅ OK')"
  git status --short | head -20
  ```

---

## 阶段 3：配置文件集中

### Task 3.1：移动散落的配置文件到 config/
- **状态**: `pending`
- **优先级**: `medium`
- **预计耗时**: 20 分钟
- **描述**: 将根目录和散落的 .yaml/.yml/.toml/.ini 配置文件集中到 config/
- **前置依赖**: Task 2.4
- **操作**:
  ```bash
  mkdir -p config/docker config/monitoring
  # docker-compose 文件
  git mv docker-compose.test.yml config/docker/ 2>/dev/null
  git mv docker-compose.prod.yml config/docker/ 2>/dev/null
  # 创建符号链接（高频文件）
  ln -sf config/docker/docker-compose.test.yml docker-compose.test.yml
  ln -sf config/docker/docker-compose.prod.yml docker-compose.prod.yml
  # 注意：pyproject.toml, package.json, tsconfig.json 保留在根目录（工具链要求）
  ```
- **验证**: config/ 下有对应文件；符号链接可正常解析

### Task 3.2：阶段 3 验证
- **状态**: `pending`
- **优先级**: `critical`
- **前置依赖**: Task 3.1
- **操作**:
  ```bash
  # 符号链接验证
  ls -la docker-compose.*.yml
  # Docker 验证（如果安装了 docker）
  docker compose -f docker-compose.test.yml config 2>/dev/null || echo "docker 未安装，跳过"
  # 禁区完整性
  diff <(find . -maxdepth 1 -name '.*' -type d | sort) /tmp/dotdirs-before.txt
  ```

---

## 阶段 4：目录归并

### Task 4.1：归并一次性工具目录到 archived/
- **状态**: `pending`
- **优先级**: `high`
- **预计耗时**: 30 分钟
- **描述**: 将已完成使命的工具目录归档
- **前置依赖**: Task 3.2
- **操作**:
  ```bash
  mkdir -p archived/tools
  # 一次性工具
  for d in ai_test_optimizer_toolkit ts-quality-guard ai_generated_tests gpu_api_system; do
    [ -d "$d" ] && git mv "$d" archived/tools/
  done
  # 已完成的临时目录
  for d in 04-测试 code_quality code_refactoring; do
    [ -d "$d" ] && git mv "$d" archived/
  done
  ```
- **验证**: 上述目录不再存在于根目录

### Task 4.2：归并文档类目录到 docs/
- **状态**: `pending`
- **优先级**: `high`
- **预计耗时**: 20 分钟
- **描述**: 将散落的文档目录合并到 docs/ 下
- **前置依赖**: Task 3.2
- **操作**:
  ```bash
  # guides/ → docs/guides/（如果根目录有独立的 guides/）
  [ -d "guides" ] && git mv guides/* docs/guides/ 2>/dev/null && rmdir guides
  # standards/ → docs/standards/
  [ -d "standards" ] && git mv standards/* docs/standards/ 2>/dev/null && rmdir standards
  # archived/ 文档类 → docs/archived/
  [ -d "archived" ] && [ ! -d "docs/archived" ] && git mv archived docs/archived
  ```
- **验证**: 根目录无独立的 guides/、standards/ 目录

### Task 4.3：归并脚本类目录到 scripts/
- **状态**: `pending`
- **优先级**: `medium`
- **预计耗时**: 15 分钟
- **描述**: 将散落的脚本目录合并到 scripts/ 下
- **前置依赖**: Task 3.2
- **操作**:
  ```bash
  # 检查根目录是否有散落的脚本目录
  for d in tools utilities helpers; do
    [ -d "$d" ] && git mv "$d" scripts/
  done
  ```
- **验证**: 根目录无散落的脚本类目录

### Task 4.4：处理剩余杂项目录
- **状态**: `pending`
- **优先级**: `medium`
- **预计耗时**: 30 分钟
- **描述**: 逐一评估剩余的根目录，决定归并或归档
- **前置依赖**: Task 4.1, Task 4.2, Task 4.3
- **操作**:
  ```bash
  # 列出剩余的非目标根目录
  target_dirs="src web config scripts docs tests architecture data openspec reports"
  for d in $(find . -maxdepth 1 -type d ! -name '.*' ! -name 'node_modules' ! -name '__pycache__' -printf '%f\n' | sort); do
    echo "$target_dirs" | grep -qw "$d" || echo "待处理: $d"
  done
  # 根据输出逐一决定：归并到哪个目标目录，或归档到 archived/
  ```
- **验证**: 根目录非隐藏目录数接近目标 13

### Task 4.5：阶段 4 验证
- **状态**: `pending`
- **优先级**: `critical`
- **前置依赖**: Task 4.4
- **操作**:
  ```bash
  echo "根目录数: $(find . -maxdepth 1 -type d ! -name '.*' ! -name 'node_modules' ! -name '__pycache__' | wc -l)"
  echo "根文件数: $(find . -maxdepth 1 -type f ! -name '.*' | wc -l)"
  # 全面功能验证
  python -c "from src.core import *; print('✅ src OK')"
  python -c "import core; print('✅ compat entry OK')"
  # 禁区完整性
  diff <(find . -maxdepth 1 -name '.*' -type d | sort) /tmp/dotdirs-before.txt
  ```

---

## 阶段 5：深度整合与路径修复

### Task 5.1：更新所有内部路径引用
- **状态**: `pending`
- **优先级**: `high`
- **预计耗时**: 45 分钟
- **描述**: 修复因文件移动导致的路径引用断裂
- **前置依赖**: Task 4.5
- **操作**:
  ```bash
  # 搜索所有引用已移动文件的地方
  grep -rn 'TASK-' --include='*.md' --include='*.py' . | grep -v archived | grep -v docs/reports
  # 搜索引用旧路径的配置
  grep -rn 'docker-compose' --include='*.yml' --include='*.yaml' --include='*.md' . | head -20
  # 逐一修复
  ```
- **验证**: 无断裂的内部链接

### Task 5.2：更新 README.md 目录结构描述
- **状态**: `pending`
- **优先级**: `high`
- **预计耗时**: 15 分钟
- **描述**: 更新 README.md 中的项目目录结构部分，反映新结构
- **前置依赖**: Task 5.1
- **操作**: 手动编辑 README.md 的「项目目录结构」章节
- **验证**: README 中的目录树与实际一致

### Task 5.3：更新 .gitignore
- **状态**: `pending`
- **优先级**: `medium`
- **预计耗时**: 10 分钟
- **描述**: 确保 .gitignore 覆盖新路径下的生成文件
- **前置依赖**: Task 5.1
- **操作**:
  ```bash
  # 确保以下条目存在
  # logs/
  # htmlcov/
  # bak/
  # *.log
  # .coverage
  # coverage.xml
  ```
- **验证**: `git status` 不显示应被忽略的文件

### Task 5.4：阶段 5 验证（全面回归测试）
- **状态**: `pending`
- **优先级**: `critical`
- **前置依赖**: Task 5.1, Task 5.2, Task 5.3
- **操作**:
  ```bash
  # Python 导入验证
  python -c "from src.core import *; from src.data_access import *; print('✅ all imports OK')"
  # 前端构建验证
  cd web/frontend && npm run build && cd ../..
  # 测试套件
  python -m pytest --co -q 2>/dev/null | tail -5
  # 禁区最终验证
  diff <(find . -maxdepth 1 -name '.*' -type d | sort) /tmp/dotdirs-before.txt
  diff <(find . -maxdepth 1 -name '.*' -type f | sort) /tmp/dotfiles-before.txt
  ```

---

## 阶段 6：防线建设

### Task 6.1：部署 git pre-commit hook
- **状态**: `pending`
- **优先级**: `high`
- **预计耗时**: 20 分钟
- **描述**: 安装 git hook 拦截根目录新增文件和隐藏目录操作
- **前置依赖**: Task 5.4
- **操作**: 创建 `.githooks/pre-commit`，包含：
  - 根目录新增文件检查（白名单外拒绝）
  - 隐藏目录移动/删除拦截
  - 根目录文件数阈值告警（>15 则警告）
- **验证**: 尝试在根目录创建 test.py 并 commit，应被拦截

### Task 6.2：配置 CI 目录结构检查
- **状态**: `pending`
- **优先级**: `medium`
- **预计耗时**: 15 分钟
- **描述**: 在 GitHub Actions 中添加目录结构合规性检查
- **前置依赖**: Task 5.4
- **操作**: 在 `.github/workflows/` 中添加或更新 CI 步骤
- **验证**: PR 触发时自动检查目录结构

### Task 6.3：生成整理完成报告
- **状态**: `pending`
- **优先级**: `medium`
- **预计耗时**: 10 分钟
- **描述**: 生成前后对比报告，记录所有变更
- **前置依赖**: Task 6.1, Task 6.2
- **操作**:
  ```bash
  echo "=== 整理完成报告 $(date) ===" > docs/reports/reorg-completion-report.md
  echo "### 前后对比" >> docs/reports/reorg-completion-report.md
  echo "整理前:" >> docs/reports/reorg-completion-report.md
  cat /tmp/reorg-baseline.txt >> docs/reports/reorg-completion-report.md
  echo "整理后:" >> docs/reports/reorg-completion-report.md
  find . -maxdepth 1 -type d ! -name '.*' | wc -l >> docs/reports/reorg-completion-report.md
  find . -maxdepth 1 -type f ! -name '.*' | wc -l >> docs/reports/reorg-completion-report.md
  du -sh . >> docs/reports/reorg-completion-report.md
  ```
- **验证**: 报告文件存在且内容完整

---

## 任务依赖图

```
Phase 0: [0.1] → [0.2] → [0.3]
                              ↓
Phase 1: [1.1] [1.2] [1.3] [1.4] → [1.5]  (1.1-1.4 可并行)
                                       ↓
Phase 2: [2.1] [2.2] [2.3] → [2.4]         (2.1-2.3 可并行)
                                ↓
Phase 3: [3.1] → [3.2]
                    ↓
Phase 4: [4.1] [4.2] [4.3] → [4.4] → [4.5] (4.1-4.3 可并行)
                                        ↓
Phase 5: [5.1] → [5.2] [5.3] → [5.4]       (5.2-5.3 可并行)
                                  ↓
Phase 6: [6.1] [6.2] → [6.3]               (6.1-6.2 可并行)
```

## 总计

| 指标 | 值 |
|------|-----|
| 总任务数 | 25 |
| 可并行任务组 | 5 组 |
| 关键路径任务 | 12 |
| 预计总工时 | 6-8 小时 |
| 预计日历时间 | 3-4 天（含验证和缓冲） |
