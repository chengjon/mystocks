# Design: add-policy-driven-directory-governance

> **历史文档说明**:
> 本文件属于已归档变更留下的历史规格、设计附件或过程材料，用于补充还原当时方案与结构。
> 它不再是当前治理口径或当前实现状态的默认真相源；如与现行 specs、共享规则或代码实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际代码实现为准。


## Overview

本设计引入“策略清单驱动”的目录治理检查器，将目录检查从硬编码 Bash 逻辑升级为：

1. **治理策略**：使用 YAML 声明根目录白名单、历史债务容忍项、递归放置规则和扫描排除项
2. **检查引擎**：使用 Python 解析策略并输出结构化结果
3. **兼容入口**：保留 `scripts/maintenance/check-structure.sh`，内部转调 Python 引擎
4. **增量接入**：为 pre-commit、`.githooks` 和 CI 提供变更范围检查模式

## Goals

- 将“目录规则”与“检查逻辑”解耦
- 区分 `error` / `warning` / `info`
- 在不清空历史债务的前提下阻止新违规继续堆积
- 为未来目录收敛提供可渐进更新的策略基线

## Non-Goals

- 不尝试一次性定义全仓所有目录的精细规则
- 不在本变更中实现自动修复
- 不在本变更中直接执行目录迁移

## Architecture

### Policy File

新增 `governance/mainline/policies/directory-structure.yaml`，包含：

- `root.allowed_files`
- `root.allowed_directories`
- `root.tolerated_files`
- `root.tolerated_directories`
- `root.forbidden_file_patterns`
- `scan.ignore_directory_names`
- `rules[]`：递归路径规则

### Engine

新增 `scripts/maintenance/check_structure.py`：

- 读取策略 YAML
- 计算根目录条目分类
- 递归扫描路径规则
- 生成 `errors / warnings / infos / summary`
- 提供 `text` 与 `json` 输出
- 默认仅在存在 `error` 时返回非零
- `--strict` 时 `warning` 也会导致非零
- 支持 `--path` 传入变更文件列表
- 支持 `--staged` 直接读取 Git 暂存区文件列表

### Wrapper

更新 `scripts/maintenance/check-structure.sh`：

- 保持原命令名不变
- 将参数直接转发给 Python 引擎

### Hook and CI Integration

- `.pre-commit-config.yaml` 使用 `directory-governance` 本地 hook 调用 `--staged`
- `.githooks/pre-commit` 调用同一检查器，并保留 `DISABLE_DIR_STRUCTURE_CHECK=1`
- `.github/workflows/code-quality.yml` 仅对本次变更文件运行目录治理检查

## Policy Strategy

策略采取“双轨治理”：

- **新增违规**：未在白名单、且不属于容忍历史债务的条目，判定为 `error`
- **历史债务**：当前仓库已存在、但目标结构希望后续收敛的条目，判定为 `warning`

这使工具既能立即上岗，又不会因为存量债务导致完全不可用。

## Initial Rule Set

首批规则仅覆盖最有价值的高频问题：

1. 根目录白名单
2. 根目录运行时产物禁入（如 `.log`、`.tmp`、`.coverage`、覆盖率文件）
3. 文档/报告收敛提示：
   - `docs/completion_reports/**`
   - `docs/phase_reports/**`
   - `docs/test_reports/**`
   - `docs/monitoring_reports/**`
   - `reviews/**`
4. 归档/备份收敛提示：
   - `archived/**`
   - `backups/**`

## Testing Strategy

使用 pytest 为引擎添加单元测试，覆盖：

- 意外根目录文件 → `error`
- tolerated legacy 根目录条目 → `warning`
- 根目录运行时产物 → `error`
- 路径规则命中 → `warning`
- 变更路径范围下忽略无关历史错误
- 变更路径范围下命中新违规 → `error`
- JSON 输出结构

## Rollout Plan

1. 提交策略文件与检查引擎
2. 兼容包装脚本切换到新引擎
3. 运行单元测试验证行为
4. 对当前仓库执行一次真实检查，确认输出分层合理

## Future Extensions

- 支持 rule owner / debt ticket / target directory 字段
- 支持按路径生成迁移建议
- 支持 CI 基线对比与 trend reporting
