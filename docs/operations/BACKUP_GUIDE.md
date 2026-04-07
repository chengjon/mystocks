# MyStocks 项目备份指南

> **使用说明**:
> 本文件是备份操作参考，不是当前仓库共享规则、统一备份策略或跨机器通用命令模板的唯一事实来源。
> 若涉及当前运维基线、路径规范或审批门禁，请优先阅读 `architecture/STANDARDS.md`；若涉及运维执行流程或协作约束，再结合根目录 `AGENTS.md` 与 `docs/operations/README.md`。
>
> 文内目标路径、排除项和清理命令带有明显机器/时间上下文；执行前必须逐项核对，尤其 `rsync --delete` 与 `rm -rf` 示例只能在确认目标路径正确后使用。

## 快速备份命令

```bash
rsync -avh --progress --delete --exclude='.git/' --exclude='node_modules/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='.mypy_cache/' --exclude='.ruff_cache/' --exclude='htmlcov/' --exclude='.coverage' --exclude='coverage/' --exclude='var/log/' --exclude='*.log' --exclude='dist/' --exclude='venv/' --exclude='.env' --exclude='*.pyc' --exclude='*.pyo' --exclude='.DS_Store' --exclude='scripts/dev/' --exclude='temp/' --exclude='playwright-report/' /opt/claude/mystocks_spec/ /mnt/wd_mycode/mystocks_bak2/
```

## 预览模式（不实际执行）

添加 `-n` 参数：

```bash
rsync -avhn --progress --delete --exclude='.git/' --exclude='node_modules/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='.mypy_cache/' --exclude='.ruff_cache/' --exclude='htmlcov/' --exclude='.coverage' --exclude='coverage/' --exclude='var/log/' --exclude='*.log' --exclude='dist/' --exclude='venv/' --exclude='.env' --exclude='*.pyc' --exclude='*.pyo' --exclude='.DS_Store' --exclude='scripts/dev/' --exclude='temp/' --exclude='playwright-report/' /opt/claude/mystocks_spec/ /mnt/wd_mycode/mystocks_bak2/
```

## 排除项说明

| 排除项 | 原因 | 预估大小 |
|--------|------|----------|
| `.git/` | Git历史，可重新clone | ~大 |
| `node_modules/` | npm依赖，可 `npm install` 恢复 | ~800M |
| `scripts/dev/` | 开发依赖包 | ~1G |
| `var/log/`, `*.log` | 日志文件 | ~235M |
| `htmlcov/`, `coverage/` | 测试覆盖率报告 | ~100M |
| `__pycache__/`, `*.pyc`, `*.pyo` | Python编译缓存 | - |
| `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` | 工具缓存 | - |
| `dist/` | 构建产物 | - |
| `venv/` | Python虚拟环境（注意：`.venv/` 保留） | - |
| `.env` | 敏感配置（建议手动备份） | - |
| `temp/`, `playwright-report/` | 临时文件 | - |

## 保留项（不排除）

- `.venv/` - 项目虚拟环境
- `.opencode/` - OpenCode配置

## 参数说明

| 参数 | 作用 |
|------|------|
| `-a` | 归档模式（保留权限、时间戳等） |
| `-v` | 详细输出 |
| `-h` | 人类可读的文件大小 |
| `--progress` | 显示传输进度 |
| `--delete` | 删除目标中源不存在的文件 |
| `-n` | dry-run，仅预览不执行 |

## 清理目标目录残留

如果目标目录有旧备份残留无法删除：

```bash
rm -rf /mnt/wd_mycode/mystocks_bak2/{utils,manager,interfaces,factory,db_manager,adapters}
```

---

**创建日期**: 2026-01-16
**备份目标**: `/mnt/wd_mycode/mystocks_bak2/`
