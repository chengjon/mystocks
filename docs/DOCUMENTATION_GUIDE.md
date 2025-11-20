# 📚 文档导航指南

欢迎来到 MyStocks 项目！本指南帮助您快速找到所需的文档。

## 🚀 快速开始 (根目录)

如果您是新用户，从这些文件开始：

| 文件 | 用途 |
|------|------|
| [`README.md`](../README.md) | 项目完整介绍（必读） |
| [`START_HERE.md`](../START_HERE.md) | 项目快速导航 |
| [`QUICKSTART.md`](../QUICKSTART.md) | 5分钟快速开始 |
| [`IFLOW.md`](../IFLOW.md) | 工作流程图解 |

## 📁 文档分类导航

### 🏗️ 架构设计文档 (`architecture/`)

了解系统设计和架构决策：

- **核心架构评估**
  - `ARCHITECTURE_EVALUATION_REPORT_2025.md` - 2025年完整架构评估（推荐首先阅读）
  - `ARCHITECTURE_REVIEW_FIRST_PRINCIPLES.md` - 第一性原理分析

- **数据库架构**
  - `ADAPTER_AND_DATABASE_ARCHITECTURE_EVALUATION.md` - 适配器与数据库架构
  - `DATASOURCE_ARCHITECTURE_FIRST_PRINCIPLES_ANALYSIS.md` - 数据源架构深度分析
  - `DATASOURCE_AND_DATABASE_ARCHITECTURE.md` - 数据源与数据库集成

- **适配器模式**
  - `ADAPTER_EXTENSION_GUIDE.md` - 如何扩展适配器
  - `ADAPTER_ROUTING_GUIDE.md` - 适配器路由策略
  - `ADAPTER_SIMPLIFICATION_*.md` - 适配器简化方案系列

- **参考架构**
  - `QLIB_ARCHITECTURE_REVIEW_REPORT.md` - QLIB启发的架构评审
  - `ARCHITECTURE_REVIEW_INDEX.md` - 架构文档索引

### 📖 实现指南 (`guides/`)

学习如何部署和集成系统：

- **系统部署**
  - `DEPLOYMENT_GUIDE.md` - 完整部署指南
  - `IMPLEMENTATION_GUIDE.md` - 实现指南

- **数据库快速参考**
  - `TDENGINE_QUICK_REFERENCE.md` - TDengine快速参考

- **数据迁移**
  - `OPENSTOCK_MIGRATION_GUIDE.md` - OpenStock迁移指南
  - `OPENSTOCK_MIGRATION_SUMMARY.md` - 迁移总结
  - `VALUECELL_MIGRATION_PLAN.md` - 迁移方案
  - `INSTOCK_MIGRATION_REPORT.md` - InStock迁移报告

- **系统集成**
  - `FRONTEND_BACKEND_DATA_FLOW_REPORT.md` - 前后端数据流
  - `OPENSTOCK_DEMO_PAGE_GUIDE.md` - Demo页面指南

### 📋 开发规范 (`standards/`)

遵循项目的编码和开发规范：

- **编码规范**
  - `项目开发规范与指导文档.md` - 项目开发总体规范
  - `代码修改规则.md` - 代码修改规则
  - `代码修改规则-合并.md` - 代码修改规则（合并版）

- **项目结构**
  - `PROJECT_MODULES.md` - 项目模块详细说明
  - `MODULE_REGISTRY.md` - 模块注册表
  - `WEB_PAGE_STRUCTURE_GUIDE.md` - Web页面结构指南

- **工作流程**
  - `项目数据工作流程.md` - 数据工作流程说明

### ✨ 特性实现 (`features/`)

了解具体功能的实现细节：

- **股票相关特性**
  - `STOCK_HEATMAP_IMPLEMENTATION.md` - 股票热力图实现
  - `WATCHLIST_GROUP_IMPLEMENTATION.md` - 监控列表分组

- **数据源特性**
  - `WENCAI_MENU_FIX.md` - 问财菜单修复
  - `TRADINGVIEW_FIX_SUMMARY.md` - TradingView修复总结
  - `TRADINGVIEW_TROUBLESHOOTING.md` - TradingView故障排查

- **功能（三阶段）**
  - `VALUECELL_PHASE1_COMPLETION.md` - 第1阶段完成报告
  - `VALUECELL_PHASE2_COMPLETION.md` - 第2阶段完成报告
  - `VALUECELL_PHASE3_COMPLETION.md` - 第3阶段完成报告

### 📊 完成报告 (`reports/`)

查看项目任务和测试完成情况：

- **任务完成报告**
  - `TASK_2_COMPLETION_REPORT.md` - Task 2 完成报告
  - `TASK_2_1_COMPLETION_REPORT.md` - Task 2.1 完成报告
  - `SUBTASK_2_2_*.md` - 子任务2.2相关报告

- **Web集成测试**
  - `WEB_COMPLETE_STATUS_20251020.md` - Web完成状态
  - `WEB_FINAL_STATUS_20251020.md` - Web最终状态
  - `WEB_FUNCTION_TEST_REPORT_FINAL.md` - Web功能测试最终报告
  - `WEB_INTEGRATION_EXECUTIVE_SUMMARY.md` - Web集成执行总结

- **系统总结**
  - `DEVELOPMENT_SUMMARY_2025.md` - 2025年开发总结
  - `SYSTEM_STATUS_20251020_FINAL.md` - 系统最终状态
  - `SESSION_COMPLETION_2025_11_06.md` - 会话完成总结

- **安全和性能**
  - `SQL_INJECTION_VULNERABILITY_REPORT.md` - SQL注入漏洞报告
  - `CODE_REVIEW_REPORT.md` - 代码审查报告
  - `WEB_PERFORMANCE_FIXES_SUMMARY.md` - 性能优化总结

### 📦 历史档案 (`archive/`)

这些文件是历史参考，通常不需要查看，但保留供参考：

- 过期的决策记录
- 历史规划文档
- 前期讨论材料
- 旧的建议和分析

## 🎯 按需求查找文档

### 我想...

| 需求 | 推荐文档 |
|------|---------|
| 快速了解项目 | [`README.md`](../README.md) + [`QUICKSTART.md`](../QUICKSTART.md) |
| 理解系统架构 | [`ARCHITECTURE_EVALUATION_REPORT_2025.md`](./architecture/ARCHITECTURE_EVALUATION_REPORT_2025.md) |
| 学习如何部署 | [`DEPLOYMENT_GUIDE.md`](./guides/DEPLOYMENT_GUIDE.md) |
| 遵循编码规范 | [`项目开发规范与指导文档.md`](./standards/项目开发规范与指导文档.md) |
| 了解数据流 | [`FRONTEND_BACKEND_DATA_FLOW_REPORT.md`](./guides/FRONTEND_BACKEND_DATA_FLOW_REPORT.md) |
| 查看功能实现 | 查看 [`features/`](./features/) 目录 |
| 检查任务进度 | 查看 [`reports/`](./reports/) 目录 |
| 参考TDengine | [`TDENGINE_QUICK_REFERENCE.md`](./guides/TDENGINE_QUICK_REFERENCE.md) |
| 迁移数据 | 查看 [`guides/`](./guides/) 的迁移相关文档 |

## 📚 按类型查找

### 给开发者的文档
- 规范：`standards/` 目录
- 架构：`architecture/` 目录的核心文档
- 实现：`guides/` 和 `features/` 目录
- 参考：`TDENGINE_QUICK_REFERENCE.md`

### 给测试工程师的文档
- 完成报告：`reports/` 目录的测试相关文档
- 安全报告：`SQL_INJECTION_VULNERABILITY_REPORT.md`
- 性能报告：`WEB_PERFORMANCE_FIXES_SUMMARY.md`

### 给项目经理的文档
- 总体进度：`reports/` 目录中的完成报告
- 系统状态：`reports/SYSTEM_STATUS_20251020_FINAL.md`
- 开发总结：`reports/DEVELOPMENT_SUMMARY_2025.md`

### 给运维人员的文档
- 部署指南：`guides/DEPLOYMENT_GUIDE.md`
- 快速参考：`guides/TDENGINE_QUICK_REFERENCE.md`
- 故障排查：`features/TRADINGVIEW_TROUBLESHOOTING.md`

## 🔄 文档的主要更新

最近的关键更新（2025年）：

- **Week 3 数据库简化**：4数据库 → 2数据库 (TDengine + PostgreSQL)
- **架构优化**：见 `ARCHITECTURE_EVALUATION_REPORT_2025.md`
- **Web集成完成**：见 `WEB_FINAL_STATUS_20251020.md`
- **全部完成**：3阶段完整，见 `VALUECELL_PHASE3_COMPLETION.md`

## 💡 使用建议

1. **初次接触项目**：按顺序读 `README.md` → `START_HERE.md` → `QUICKSTART.md`
2. **深入理解**：根据需求查阅相应分类的文档
3. **问题排查**：使用表格快速定位相关文档
4. **历史参考**：需要追溯决策历史时查看 `archive/` 目录

## 📞 文档位置总结

```
项目根目录/
├── README.md                    ← 从这里开始！
├── START_HERE.md
├── QUICKSTART.md
├── IFLOW.md
├── CLAUDE.md
├── CHANGELOG.md
├── TASKMASTER_START_HERE.md
│
└── docs/
    ├── architecture/            ← 架构设计
    ├── guides/                  ← 实现指南
    ├── standards/               ← 开发规范
    ├── features/                ← 功能实现
    ├── reports/                 ← 完成报告
    └── archive/                 ← 历史档案
```

---

**最后更新**: 2025-11-08
**维护者**: Claude Code + Project Team
**状态**: 持续维护中 ✨

有问题或建议？请参考相关部分的文档或联系项目团队。
