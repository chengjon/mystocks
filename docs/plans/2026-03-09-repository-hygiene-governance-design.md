# Repository Hygiene Governance Design

## Context

当前仓库已经落地了策略清单驱动的目录治理检查器，但仓库卫生相关任务仍然分散在：

- `docs/reports/cleanup/FILE_CLEANUP_TASK.md`
- `scripts/maintenance/rotate_logs.sh`
- `scripts/compliance/file_size_guardrail.py`
- `scripts/dev/check_file_sizes.py`
- `scripts/dev/cleanup_temp_files.py`
- `scripts/dev/execute_cleanup.py`

这些内容部分重复、部分过时，而且目标目录并不完全一致。继续按原任务单并行推进，会让治理规则、清理脚本、目录层级再次分叉。

## Goals

- 把当前目录治理与 P1/P2 清理任务整合为同一条主线
- 明确 `docs/`、`reports/`、`archive/`、`var/` 四类稳定层
- 给日志轮转、自动清理、文件大小监控建立统一入口
- 把文档整理从零散搬运升级为生命周期治理

## Non-Goals

- 不在本轮一次性搬迁全仓文档
- 不在本轮自动修复所有历史债务
- 不在本轮做高风险的全自动移动/删除

## Options

### 方案 A：按旧任务单直接补脚本

- 优点：短期看最快
- 缺点：与现有目录治理脱节，重复脚本会更多

### 方案 B：以目录治理为骨架整合 P1/P2（推荐）

- 优点：目标目录、脚本入口、治理策略一致
- 缺点：需要先补规格和计划，再逐步实施

### 方案 C：直接做全自动清理迁移器

- 优点：表面上一次到位
- 缺点：误删和误搬风险高，不适合当前仓库

## Recommended Design

采用 **方案 B：治理优先、批次实施**。

### 一、稳定层

- `docs/`：活跃说明、指南、设计与操作文档
- `reports/`：版本化证据、阶段报告、治理报告
- `archive/`：历史冻结资产
- `var/`：运行时与本地生成物

### 二、入口层

- `scripts/cleanup/auto_cleanup.sh`
- `scripts/maintenance/rotate_logs.sh`
- `scripts/maintenance/monitor_file_size.sh`

新入口统一要求：

- 支持 `--dry-run`
- 支持结构化输出
- 输出落点清晰

### 三、收敛层

优先收敛：

1. 根目录 `error` 级问题
2. 日志 / 覆盖率 / 备份 / 临时文件的运行时落点
3. 重复脚本收敛
4. `docs/` 与 `reports/` / `archive/` 的边界

## Rollout

### Phase 0

- 刷新 `docs/reports/cleanup/FILE_CLEANUP_TASK.md`
- 更新策略允许的目标目录

### Phase 1

- 收敛日志轮转、文件大小监控、自动清理入口
- 默认先以 dry-run 运行

### Phase 2

- 处理当前根目录 `error` 项
- 为后续 warning 收敛铺路

### Phase 3

- 梳理 `docs/` 的活跃/证据/历史边界
- 形成迁移清单后分批实施

## Success Criteria

- 目标目录不再互相冲突
- 清理与监控脚本入口统一
- 目录治理检查器支持并认可新的 canonical targets
- 后续目录收敛可以按批次推进，而不是靠一次性手工整理
