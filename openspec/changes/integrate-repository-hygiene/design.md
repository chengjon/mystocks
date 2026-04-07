# Design: integrate-repository-hygiene

> **设计方案说明**:
> 本文件用于记录某项变更的设计思路、结构拆分、实现取舍或技术路径，属于方案设计层材料。
> 它不是共享规则正文，也不直接代表当前仓库已落地状态；落地判断应结合 `architecture/STANDARDS.md`、对应 proposal/tasks、审批结果与实际代码验证。


## Overview

本设计将现有“目录检查器”扩展为“仓库卫生治理体系”，核心原则是：

1. **同一套策略定义目标结构**
2. **同一套脚本入口执行日常卫生动作**
3. **同一套生命周期目录承接迁移结果**
4. **先 dry-run 与报表，再做变更动作**

目标不是增加更多脚本，而是把当前分散在 `docs/FILE_CLEANUP_TASK.md`、`scripts/dev/*`、`scripts/maintenance/*` 里的零散能力收敛为统一模型。

## Goals

- 将 P1/P2 任务整合进当前目录治理体系
- 建立稳定的生命周期目录边界
- 为日志、缓存、覆盖率、备份、历史文档提供明确去向
- 让自动清理与文件大小监控拥有统一、可验证的入口
- 将文档整理从一次性搬迁升级为长期治理流程

## Non-Goals

- 本轮不做全仓自动迁移
- 本轮不做“发现问题即自动修复”的高风险行为
- 本轮不试图消除所有历史目录债务

## Alternatives Considered

### Option A: 继续按 `docs/FILE_CLEANUP_TASK.md` 独立推进

优点：
- 短期看实现成本低

缺点：
- 与当前 policy-driven directory governance 脱节
- 继续放大脚本重复与目标目录不一致问题

### Option B: 以目录治理为主线整合 P1/P2 任务（推荐）

优点：
- 规则、脚本、目录目标一致
- 能先处理结构性根因，再做批量清理
- 更适合长期治理与 CI / hook / 巡检接入

缺点：
- 前期需要先补规格与计划，不是“立刻写个脚本就完”

### Option C: 做一个全自动迁移器统一搬文件

优点：
- 理论上一次性见效快

缺点：
- 风险最高
- 很容易误搬活跃文档和运行资产
- 不适合作为当前仓库的第一步

## Recommended Approach

采用 **Option B：治理优先、能力分层、迁移分批**。

### Layer 1: Policy and Canonical Targets

先统一目录目标：

- `docs/`：活跃说明、设计、指南、操作手册
- `reports/`：版本化证据、阶段报告、治理报表
- `archive/`：历史冻结资产，包括历史文档归档
- `var/`：运行时产物与本地生成物，如日志、覆盖率、临时报告、备份

这一步先解决“文件该去哪儿”的根本问题。

### Layer 2: Hygiene Entry Points

统一以下入口：

- `scripts/cleanup/auto_cleanup.sh`
- `scripts/maintenance/rotate_logs.sh`
- `scripts/maintenance/monitor_file_size.sh`

其中：

- `auto_cleanup.sh` 负责临时文件、Python 缓存、覆盖率、可归档备份、整理报告
- `rotate_logs.sh` 负责日志轮转与归档
- `monitor_file_size.sh` 负责查找大文件并生成告警

新增入口必须优先复用现有脚本逻辑，而不是重新造一套并行实现。

### Layer 3: Reports and Dry-Run

所有会修改文件系统状态的操作都必须先支持：

- `--dry-run`
- 结构化结果输出
- 面向治理的报告落点

推荐输出到：

- `reports/governance/`：版本化治理报告
- `var/reports/`：本地运行时报告与临时产物

### Layer 4: Documentation Lifecycle

文档不再只按“文档种类”放置，还需要按生命周期区分：

- 活跃文档留在 `docs/`
- 证据性/阶段性输出收敛到 `reports/`
- 失活或冻结文档归档到 `archive/docs/YYYY/Qn/`

这样可以避免 `docs/` 同时承担“说明文档 + 历史证据 + 已过期材料”三种角色。

## Implementation Phases

### Phase 0: Spec Alignment

- 刷新 `docs/FILE_CLEANUP_TASK.md` 的真实基线
- 更新策略允许的 canonical targets
- 明确 `archive/` 与 `var/` 的边界

### Phase 1: Script Convergence

- 升级现有日志轮转脚本
- 新增统一文件大小监控入口
- 新增自动清理入口，默认 dry-run
- 复用或替换现有重复脚本

### Phase 2: Root Error Remediation

- 先处理根目录 `error` 级问题
- 将运行时产物迁移到 `var/`
- 将历史资产迁移到 `archive/` / `reports/`

### Phase 3: Documentation Convergence

- 按分类和生命周期梳理 `docs/`
- 形成迁移清单
- 分批迁移并逐步缩减 tolerated warnings

## Validation Strategy

- OpenSpec：`openspec validate integrate-repository-hygiene --strict`
- 单元测试：覆盖新脚本的 dry-run、路径解析、报告输出、阈值行为
- 集成验证：目录治理检查器能识别新 canonical targets，且不会把目标目录当成新违规
- 运行验证：自动清理、日志轮转、文件大小监控都能生成可审计输出

## Rollout Guidance

推荐每一批只做一类动作：

1. 规则更新
2. 脚本入口落地
3. 根目录阻塞项收敛
4. 文档迁移

不要把“加规则、写脚本、搬大量文件”放在同一个提交中。
