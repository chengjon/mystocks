# README.md 优化建议

> 基于当前 README.md（1747 行）的结构分析，提出精简与重组方案，供审核。

---

## 一、当前问题诊断

### 1.1 文件过长

当前 1747 行，远超 README 的合理长度（建议 200-400 行）。每次读取全文消耗大量上下文。

### 1.2 职责混乱

README 同时承担了以下角色，应分离：

| 角色 | 占比（估算）| 应归属 |
|------|-----------|--------|
| 项目简介与快速开始 | ~10% | README |
| 架构说明（数据分类/存储策略） | ~25% | `docs/architecture/` |
| 完整代码示例 | ~15% | `docs/guides/` |
| 功能特性文档（GPU/数据源V2/WebSocket） | ~25% | `docs/guides/` 或 `docs/reports/` |
| 历史变更记录（Phase 2/3/Week 3/安全加固） | ~15% | `docs/reports/` 或 `CHANGELOG.md` |
| 文件/模块目录详解 | ~10% | `docs/standards/PROJECT_MODULES.md`（已存在） |

### 1.3 信息过时

| 位置 | 过时内容 | 当前真实值 |
|------|---------|-----------|
| 端口分配表 | 前端 `3000`/`3001`，后端 `8000`/`8001` | 前端 `3020`/`3021`，后端 `8020`/`8021` |
| 缓存说明 | README 将 Redis 表述为默认缓存真相 | 当前默认运行时口径不应再把 Redis 写成必需依赖；历史/可选能力需单独标注范围 |
| Vue UI 框架 | "Element Plus UI 组件库" | 当前主视觉与组件体系以 ArtDeco 设计系统为准 |
| 前端访问地址 | `http://localhost:5173` | `http://localhost:3020` |
| Web API 端点 | README 直接维护静态端点总览 | 应改为链接 OpenAPI / API mapping 文档，避免 README 再次成为过时真相源 |

### 1.4 重复内容

- 数据分类体系在"核心特点"和"一、数据分类与存储策略"中重复描述
- 导入示例在"文件与模块说明"中重复出现（统一导入路径、各模块详解中都有）
- 项目目录结构在"目录结构"和"根目录入口点文件"中有重叠

---

## 二、优化方案

### 2.1 README 保留内容（目标 300 行以内）

```
1. 项目名称 + 一句话描述 + 徽章
2. 关键文档入口与唯一真相源（已有）
3. 快速开始（环境准备 + 启动命令，仅核心 3-5 步）
4. 项目目录结构（精简版，仅一级 + 二级目录）
5. 技术栈概览（表格，5 行以内）
6. 许可证
```

### 2.2 需迁移出去的内容

| 当前章节 | 迁移目标 | 说明 |
|---------|---------|------|
| `🧭 MongoDB Multi-CLI Coordination` | `docs/guides/multi-cli-tasks/` 下的已有文档 | 仅在 README 保留一行链接 |
| `🔒 Git Worktree 多 CLI 协作强制规则` | `.multi-cli-tasks/guides/` 已有 | 仅保留链接 |
| `✅ 2026-03-03 前端页面优化清单收口` | `docs/reports/` 或 `docs/plans/` 已有报告 | 历史记录，不归 README |
| `📊 代码清单扫描工具上线` | `src/monitoring/code_inventory/README.md` 已有 | 仅保留链接 |
| `🔒 安全加固完成` | `docs/api/security-remediation-report.md` 已有 | 仅保留链接 |
| `🏗️ 架构重构与收敛完成` | `architecture/DOMAIN_BOUNDARIES.md` 已有 | 仅保留链接 |
| `⚡ Week 3 重大更新` | `docs/reports/` | 历史变更 |
| `📋 Phase 2 前端优化` / `🌐 Phase 3 WebSocket` | `docs/reports/` | 历史变更 |
| `## 📊 一~三 数据分类/调用/架构` 全部 | `docs/architecture/DATA_ARCHITECTURE.md`（新建或合并到已有架构文档） | 详细的架构说明 |
| `## 🚀 GPU API System` 全部 | `src/gpu/api_system/README.md` 已有（88 页） | 详细的 GPU 系统文档 |
| `## 🔧 数据源管理工具 V2.0` 全部 | `docs/guides/data-source/` 已有 | 详细的功能文档 |
| `## 📁 文件与模块说明` 全部 | `docs/standards/PROJECT_MODULES.md` 已有 | 详细的模块清单 |
| `## 🌐 Web 平台使用` + API 端点 | `docs/api/` 已有多份文档 | API 文档 |

### 2.3 过时内容需更新或删除

| 内容 | 建议 |
|------|------|
| 端口分配表（3000/8000） | 更新为 3020/8020（参考 `.env`） |
| "Element Plus UI 组件库" | 改为 "ArtDeco 自定义设计系统" |
| `http://localhost:5173` | 改为 `http://localhost:3020` |
| Redis 相关缓存说明 | 删除 README 中将 Redis 表述为默认运行依赖的描述；历史阶段或可选缓存架构迁移到对应文档并标注日期/范围 |
| "响应式设计" 描述 | 项目仅支持桌面端，删除移动端/响应式承诺，明确桌面端约束 |
| 静态 API 端点总览 | 从 README 删除，统一链接到 OpenAPI / API mapping 文档 |

---

## 三、建议的新 README 结构（大纲）

```markdown
# MyStocks 量化交易数据管理系统

> 一句话项目描述

[徽章行：版本/Python/Vue/License]

## 关键文档入口与唯一真相源
（已有，保持不变）

## 快速开始
### 环境要求
- Python 3.12+ / Node.js 18+ / PostgreSQL 17+ / TDengine 3.3+
### 启动服务
```bash
# 后端
cd web/backend && uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload
# 前端
cd web/frontend && npm install && npm run dev -- --port 3020
```
### 访问地址
- 前端：http://localhost:3020
- API 文档：http://localhost:8020/docs

## 项目结构
（精简版目录树，仅到二级）

## 技术栈
| 层 | 技术 |
|---|------|
| 后端 | Python 3.12 / FastAPI / SQLAlchemy |
| 前端 | Vue 3 / TypeScript / ArtDeco 设计系统 |
| 时序库 | TDengine 3.3 |
| 关系库 | PostgreSQL 17 + TimescaleDB |

## 核心架构文档
- 数据分类与存储策略 → docs/architecture/...
- 域边界定义 → architecture/DOMAIN_BOUNDARIES.md
- API 映射 → docs/api/MyStocks_API_Mapping_Document.md
- GPU 加速系统 → src/gpu/api_system/README.md

## 历史里程碑
（仅保留一行链接列表，不展开内容）
- 2026-03-14 Maestro 多 CLI 协作 → docs/reports/...
- 2026-03-03 前端页面优化收口 → docs/plans/...
- 2026-02-23 代码清单扫描工具 → reports/...
- 2026-02-09 安全加固 → docs/api/security-remediation-report.md
- 2026-02-08 架构重构 → architecture/DOMAIN_BOUNDARIES.md
- 2025-10-19 数据库简化（4→2）→ docs/architecture/...

## 许可证
MIT
```

---

## 四、实施建议

1. **先更新过时信息**（端口、UI 框架、访问地址），避免误导
2. **创建迁移文档** `docs/architecture/DATA_ARCHITECTURE.md`，将数据分类/存储/调用方案整体迁入
3. **逐步精简 README**，每个历史章节替换为一行链接
4. **检查 README 锚点引用**：执行 `rg "README\\.md#"`，避免章节删除后留下失效链接
5. **最终目标**：README 从 1747 行精简到 300 行以内

---

## 五、风险评估

| 风险 | 影响 | 缓解 |
|------|------|------|
| 迁移过程中丢失信息 | 低 | 所有内容迁入已有文档，不删除 |
| 外部链接指向 README 的锚点失效 | 低 | 检查 git grep `README.md#` 引用 |
| 新贡献者找不到信息 | 中 | README 的"关键文档入口"栏目确保覆盖所有入口 |

---

*建议人：Claude AI | 日期：2026-04-19*
