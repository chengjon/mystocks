# reorganize-project-directory-structure

## 概述

对 MyStocks 项目进行全面的文件目录重组，将当前 83 个根目录 + 50 个根文件精简至 13 个标准目录 + ~10 个必要根文件。

## 状态

| 字段 | 值 |
|------|-----|
| 状态 | `planned` |
| 优先级 | `high` |
| 预估工期 | 3-4 天 |
| 前置条件 | 无活跃开发分支冲突 |
| 替代/继承 | 替代已完成的 `implement-file-directory-migration` |

## 背景

2025-11-09 的首次重组将 42 个根目录精简至 13 个，但随着 AI 工具链扩展和日常开发积累，根目录再次膨胀至 83 个目录 + 50 个文件。本次重组基于《文件目录整理方法论指南 v2.1》制定，是一次系统性的深度治理。

## 核心目标

1. 根目录从 83 个目录精简至 13 个
2. 根文件从 50 个精简至 ~10 个
3. 释放 ~240GB+ 磁盘空间（logs/、bak/ 等）
4. 建立长效防护机制（git hook + CI + 定期审计）

## 执行阶段

| 阶段 | 名称 | 内容 | 预估时间 |
|------|------|------|----------|
| Phase 0 | 准备 | 创建备份分支、生成快照、确认禁区 | 30 分钟 |
| Phase 1 | 清除垃圾 | 删除 logs/、bak/、htmlcov/、缓存目录 | 1 小时 |
| Phase 2 | 归档历史 | 移动已完成/过时的目录到 .archive/ | 2 小时 |
| Phase 3 | 归并同类 | 合并功能重叠的目录 | 3 小时 |
| Phase 4 | 根文件整理 | 移动根文件到对应目录 | 2 小时 |
| Phase 5 | 路径修复 | 更新 import、config、CI 引用 | 3 小时 |
| Phase 6 | 防护部署 | 安装 git hook、更新文档 | 1 小时 |

## 关键约束

- **禁区保护**：23 个 dot-directories + 12 个 dot-files 不可触碰
- **兼容入口**：4 个根级 .py 文件（core.py、data_access.py、monitoring.py、unified_manager.py）必须保留
- **子模块自治**：web/ 内部结构不在本次整理范围
- **Monorepo 根配置**：package.json、vitest.config.ts 是根级工具配置，非冗余

## 参考文档

- [方法论指南](../../docs/guides/文件目录整理方法论指南.md)
- [具体方案](../../docs/plans/项目文件目录整理具体方案.md)
- [审查报告](../../docs/reviews/PROJECT_STRUCTURE_PLAN_REVIEW.md)
- [文件组织规则](../../docs/standards/FILE_ORGANIZATION_RULES.md)

## 文件结构

```
reorganize-project-directory-structure/
├── README.md          # 本文件 - 变更概述
├── design.md          # 详细设计文档
├── tasks.md           # 任务分解与执行清单
└── specs/
    └── file-organization/
        └── target-structure.md  # 目标结构规格说明
```
