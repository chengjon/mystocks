# 🚀 部署与运维监控文档

## 📁 目录说明

本模块包含MyStocks项目的部署指南、运维监控、故障处理等文档，是确保系统稳定运行和高效运维的核心资料。

## 📄 核心文档列表

### 🚀 部署相关文档
- **[deployment/README.md](./deployment/README.md)** - 部署文档总览
- **[deployment/SETUP_GRAFANA.md](./deployment/SETUP_GRAFANA.md)** - Grafana 设置与部署
- **[deployment/DEPLOYMENT.md](./deployment/DEPLOYMENT.md)** - 部署手册
- **[deployment/PORT_CONFIGURATION.md](./deployment/PORT_CONFIGURATION.md)** - 端口配置指南
- **[deployment-guide.md](./deployment-guide.md)** - 当前运维部署指南
- **[ci-cd/CICD_CONTINUOUS_OPTIMIZATION.md](./ci-cd/CICD_CONTINUOUS_OPTIMIZATION.md)** - CI/CD 持续优化指南
- **[ci-cd/CICD_TYPE_CHECK_INTEGRATION_GUIDE.md](./ci-cd/CICD_TYPE_CHECK_INTEGRATION_GUIDE.md)** - 类型检查 CI/CD 集成指南
- **[ci-cd/CICD_TYPE_CHECK_QUICK_REFERENCE.md](./ci-cd/CICD_TYPE_CHECK_QUICK_REFERENCE.md)** - 类型检查快速参考
- **[ci-cd/LOCAL_CI_INTEGRATION.md](./ci-cd/LOCAL_CI_INTEGRATION.md)** - 本地开发环境 CI 集成指南
- **[ci-cd/MYSTOCKS_CI_CD_DAILY_APPLICATION.md](./ci-cd/MYSTOCKS_CI_CD_DAILY_APPLICATION.md)** - CI/CD 日常应用规划与执行清单
- **[ci-cd/QUALITY_GATE_MANAGEMENT.md](./ci-cd/QUALITY_GATE_MANAGEMENT.md)** - 质量门禁管理参考文档
- **[ci-cd/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md](./ci-cd/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md)** - Python 代码质量保证工作流程
- **[ci-cd/PYTHON_QUALITY_TOOLS_QUICK_REFERENCE.md](./ci-cd/PYTHON_QUALITY_TOOLS_QUICK_REFERENCE.md)** - Python 质量工具快速参考

### 📊 监控与运维文档
- **[monitoring/MONITORING_GUIDE.md](./monitoring/MONITORING_GUIDE.md)** - 监控指标、告警规则、可观测性说明
- **[monitoring/ASYNC_MONITORING_GUIDE.md](./monitoring/ASYNC_MONITORING_GUIDE.md)** - 异步监控系统使用指南
- **[monitoring/MYSTOCKS_MONITORING_OPTIMIZATION_DEPLOYMENT.md](./monitoring/MYSTOCKS_MONITORING_OPTIMIZATION_DEPLOYMENT.md)** - 监控栈深度优化部署指南
- **[monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md](./monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md)** - 交易信号监控指标系统设计方案
- **[monitoring/TMUX_LNAV_ADAPTER_MONITORING.md](./monitoring/TMUX_LNAV_ADAPTER_MONITORING.md)** - tmux + lnav 适配器日志监控方案
- **[monitoring/告警规则设置方法.md](./monitoring/%E5%91%8A%E8%AD%A6%E8%A7%84%E5%88%99%E8%AE%BE%E7%BD%AE%E6%96%B9%E6%B3%95.md)** - Prometheus 告警规则设置方法
- **[MYSTOCKS_MONITORING_SYSTEM_OVERVIEW.md](./MYSTOCKS_MONITORING_SYSTEM_OVERVIEW.md)** - 企业级监控系统总览
- **[OPS_MANUAL.md](./OPS_MANUAL.md)** - 运维操作总手册
- **[运维效果分析报告.md](./运维效果分析报告.md)** - 运维效果与现状分析

### 🔧 故障处理文档
- **[PRODUCTION_INFO.md](./PRODUCTION_INFO.md)** - 生产环境信息与服务访问入口
- **[BACKUP_GUIDE.md](./BACKUP_GUIDE.md)** - 项目备份指南
- **[INFRASTRUCTURE_CHECKLIST.md](./INFRASTRUCTURE_CHECKLIST.md)** - 基础设施检查手册
- **[quick-start.md](./quick-start.md)** - MyStocks 快速启动指南
- **[STOCKS_SPEC_COMMAND_GUIDE.md](./STOCKS_SPEC_COMMAND_GUIDE.md)** - `stocks_spec` 服务管理命令指南
- **[PHASE6_SERVER_RECOVERY_TEST_PROCEDURE.md](./PHASE6_SERVER_RECOVERY_TEST_PROCEDURE.md)** - 服务器恢复后测试流程
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - 系统故障排查手册
- **[TROUBLESHOOTING_QUICK_REFERENCE.md](./TROUBLESHOOTING_QUICK_REFERENCE.md)** - 故障排除快速手册
- **[数据同步故障排除.md](./数据同步故障排除.md)** - 数据同步相关故障排查
- **[日志查看工具集成.md](./日志查看工具集成.md)** - 日志工具与查看方式说明
- **[LNAV_INTEGRATION_GUIDE.md](./LNAV_INTEGRATION_GUIDE.md)** - lnav 日志分析与导出指南

## 🚀 快速导航

### 运维负责人
1. 执行 **[deployment/README.md](./deployment/README.md)** 或 **[deployment-guide.md](./deployment-guide.md)** 进行系统部署
2. 结合 **[MYSTOCKS_MONITORING_SYSTEM_OVERVIEW.md](./MYSTOCKS_MONITORING_SYSTEM_OVERVIEW.md)** 与 **[monitoring/MONITORING_GUIDE.md](./monitoring/MONITORING_GUIDE.md)** 观察运行状态
3. 通过 **[运维效果分析报告.md](./运维效果分析报告.md)** 持续优化运维

### 系统管理员
- 学习 **[OPS_MANUAL.md](./OPS_MANUAL.md)** 提升故障处理能力
- 使用 **[数据同步故障排除.md](./数据同步故障排除.md)** 排查同步问题
- 使用 **[日志查看工具集成.md](./日志查看工具集成.md)** 进行日志排障

### 开发人员
- 参考 **[deployment/README.md](./deployment/README.md)** 配置开发环境
- 结合 **[ci-cd/LOCAL_CI_INTEGRATION.md](./ci-cd/LOCAL_CI_INTEGRATION.md)** 在本地预跑 CI/CD 门禁
- 了解 **[monitoring/MONITORING_GUIDE.md](./monitoring/MONITORING_GUIDE.md)** 中的监控要求
- 参考 **[ci-cd/QUALITY_GATE_MANAGEMENT.md](./ci-cd/QUALITY_GATE_MANAGEMENT.md)** 理解质量门禁与停止策略
- 通过 **[PRODUCTION_INFO.md](./PRODUCTION_INFO.md)** 与 **[OPS_MANUAL.md](./OPS_MANUAL.md)** 获取运行约束和值班操作

### 安全负责人
- 重点关注 **[monitoring/MONITORING_GUIDE.md](./monitoring/MONITORING_GUIDE.md)** 中的告警与追踪能力
- 结合 **[OPS_MANUAL.md](./OPS_MANUAL.md)** 审核运行流程
- 通过 **[日志查看工具集成.md](./日志查看工具集成.md)** 核对审计与日志方案

## 📝 文档维护规范

### 更新频率
- **deployment/README.md**: 部署流程变更时更新
- **monitoring/MONITORING_GUIDE.md**: 监控策略变更时更新
- **运维效果分析报告.md**: 每月更新
- **安全漏洞与修复跟踪.md**: 发现漏洞时实时更新
- **运维常见问题手册.md**: 实时补充新问题

### 责任人
- **运维负责人**: 部署指南、监控指南、运维效果分析
- **系统管理员**: OPS 手册、日志排障、数据同步排障
- **性能优化工程师**: 运维效果分析与监控配置

### 质量要求
1. **部署流程可靠**: 确保部署流程可重复、可回滚
2. **监控指标完整**: 覆盖系统、应用、业务各层面
3. **故障处理及时**: 提供快速、准确的故障解决方案
4. **安全措施有效**: 确保系统安全符合要求

## 📊 运维指标

| 指标类别 | 监控项 | 当前值 | 目标值 | 告警阈值 |
|----------|--------|--------|--------|----------|
| 系统资源 | CPU使用率 | 65% | 70% | 85% |
| 系统资源 | 内存使用率 | 70% | 75% | 90% |
| 系统资源 | 磁盘使用率 | 45% | 60% | 80% |
| 应用性能 | 接口响应时间 | 120ms | 100ms | 500ms |
| 应用性能 | 接口错误率 | 0.5% | 0.3% | 2% |
| 业务指标 | 数据同步成功率 | 98% | 99% | 95% |
| 业务指标 | 策略执行成功率 | 95% | 98% | 90% |

## 🚨 应急响应

### 一级故障（系统不可用）
1. 立即参考 **[OPS_MANUAL.md](./OPS_MANUAL.md)** 与 **[monitoring/MONITORING_GUIDE.md](./monitoring/MONITORING_GUIDE.md)** 排查
2. 30分钟内响应，2小时内恢复
3. 故障恢复后24小时内提交故障报告

### 二级故障（功能异常）
1. 参考 **[数据同步故障排除.md](./数据同步故障排除.md)** 与 **[日志查看工具集成.md](./日志查看工具集成.md)** 处理
2. 2小时内响应，8小时内修复
3. 修复后更新问题手册

### 三级故障（性能下降）
1. 使用 **[运维效果分析报告.md](./运维效果分析报告.md)** 与 **[monitoring/MONITORING_GUIDE.md](./monitoring/MONITORING_GUIDE.md)** 优化
2. 4小时内响应，24小时内优化
3. 更新 **[运维效果分析报告.md](./运维效果分析报告.md)**

## 🔗 相关文档

- 📋 [项目总览](../overview/)
- 🏗️ [架构文档](../architecture/)
- 🧪 [测试文档](../testing/)

## 📞 联系方式

- **运维负责人**: [联系方式]
- **安全负责人**: [联系方式]
- **系统管理员**: [联系方式]
- **7x24小时应急**: [联系方式]

---

*最后更新: 2025-12-06*
*维护人: 运维团队*
