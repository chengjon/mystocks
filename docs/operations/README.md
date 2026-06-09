# Operations Runbooks

> **导航说明**:
> 本文件是 `docs/operations/` 的 canonical runbook trunk，用于部署、监控、故障排查与值班流程导航。
> 它不是当前运行指标、实时服务状态或仓库共享规则本身；这些内容应分别回到运行时检查结果与 `architecture/STANDARDS.md`。

## Start Here

- 部署与环境准备：
  [`deployment/README.md`](deployment/README.md),
  [`deployment-guide.md`](deployment-guide.md),
  [`quick-start.md`](quick-start.md)
- 监控与可观测性：
  [`monitoring/MONITORING_GUIDE.md`](monitoring/MONITORING_GUIDE.md),
  [`MYSTOCKS_MONITORING_SYSTEM_OVERVIEW.md`](MYSTOCKS_MONITORING_SYSTEM_OVERVIEW.md)
- 日常值班与故障排查：
  [`OPS_MANUAL.md`](OPS_MANUAL.md),
  [`PRODUCTION_INFO.md`](PRODUCTION_INFO.md),
  [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
- 本地质量门禁与 CI/CD：
  [`ci-cd/LOCAL_CI_INTEGRATION.md`](ci-cd/LOCAL_CI_INTEGRATION.md),
  [`ci-cd/QUALITY_GATE_MANAGEMENT.md`](ci-cd/QUALITY_GATE_MANAGEMENT.md)

## Reader Routing

- 若问题是仓库级运行门禁、审批门禁或环境一致性：
  先看 [`architecture/STANDARDS.md`](../../architecture/STANDARDS.md)
- 若问题是“服务现在是否健康”：
  先看 PM2、健康检查、日志与监控，而不是 README 中的历史目标表
- 若问题是部署细节：
  进入 [`deployment/`](deployment)
- 若问题是监控细节：
  进入 [`monitoring/`](monitoring)
- 若问题是 CI/CD 或本地质量流程：
  进入 [`ci-cd/`](ci-cd)

## Supporting Surfaces

- [`INDEX.md`](INDEX.md) 仅作为旧链接兼容索引保留
- root-level runbooks 如 [`BACKUP_GUIDE.md`](BACKUP_GUIDE.md)、
  [`INFRASTRUCTURE_CHECKLIST.md`](INFRASTRUCTURE_CHECKLIST.md)、
  [`STOCKS_SPEC_COMMAND_GUIDE.md`](STOCKS_SPEC_COMMAND_GUIDE.md)
  继续作为 supporting runbooks 保留
- 历史分析类文档如 [`运维效果分析报告.md`](运维效果分析报告.md) 只能作为 supporting/reporting material，不应被视为当前运行基线

## Governance Status

- `docs/operations/README.md` 保留为唯一 operations trunk
- root index 已停止承担“当前指标总表”职责
- 后续 cleanup 应围绕 active runbook families 收敛，而不是继续扩写根级总览
