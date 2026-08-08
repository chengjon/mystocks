# 开发手册

> **版本**: 1.0 | **更新日期**: 2026-07-12
> **维护者**: 开发测试组长
> **文档类型**: 手册主页
> **上游入口**: [CORE.md](../CORE.md) → 开发角色

---

## 本手册范围

覆盖日常开发任务：API 开发、前端组件、数据源接入、架构红线治理、AI 工具调用。

---

## 快速入口

| 场景 | 文档 | 简介 |
|------|------|------|
| 全新上手 | [operations/quick-start.md](../operations/quick-start.md) | 环境搭建、首次运行、冒烟测试 |
| 新增 API | [api-development.md](api-development.md) | 契约先行 → FastAPI 实现 → 版本映射 |
| 新增前端组件 | [前端组件指南](../guides/frontend/) | ArtDeco 组件、CSS/SCSS 规范、变更卫生 |
| 新增数据源 | [data-sources.md](data-sources.md) | 数据源注册、适配器、fallback 链 |
| AI 集成 | [AI 工具手册](../ai/index.md) | LLM API、prompt、AI 工具链 |
| 架构红线 | [architecture/STANDARDS.md](../architecture/STANDARDS.md) | 编码红线、审批门禁、六步走战略 |
| 治理门禁 | [governance/](../guides/governance/) | 删除证据门禁、file size 门禁、PM2 一等公民 |
| API 契约 | [api/](../api/index.md) | 契约文件、错误码、Apifox 同步 |

---

## 开发流程六步走

1. **规范基线**：先读 [ARCHITECTURE.md](../architecture/STANDARDS.md) 确认约束
2. **能力盘点**：检索 `src/` `web/` `config/` `docs/` 已存在实现
3. **实现**：最小变更、`from src.*` 绝对导入、完整类型注解
4. **验证**：`bash scripts/dev/ci/local_ci_check.sh` + `pre-commit run`
5. **文档**：同步 `FUNCTION_TREE.md` 入口 + 更新相关指南
6. **合并**：PR 卡片 + 三道门禁（质量/安全/审查）

---

## 常用规范（子目录索引）

| 规范 | 位置 | 要点 |
|------|------|------|
| 编码红线 | [architecture/STANDARDS.md](../architecture/STANDARDS.md) | 零根配置、Docker 一等公民、Logic Gravity |
| 前端规范 | [guides/frontend/](../guides/frontend/) | TypeScript 渐进治理、CSS/SCSS 零错误、≤800 行 |
| 文件组织 | [standards/](../standards/) | 零根配置、Logic Gravity、API 注册 |
| Large File 拆分 | [architecture/standards/large_file_splitting_principles.md](../architecture/standards/large_file_splitting_principles.md) | Python>800、Vue>500、TS>500 |
| 技术债治理 | [docs/standards/technical-debt-governance-charter-v1.md](../standards/technical-debt-governance-charter-v1.md) | 门禁、基线、豁免 |
| Commit 规范 | [guides/frontend/frontend-change-hygiene-and-micro-commit-guide.md](../guides/frontend/frontend-change-hygiene-and-micro-commit-guide.md) | 微提交、卫生检查 |

---

> 跨手册链接：测试入口 [test/](../test/index.md) · 运维入口 [ops/](../ops/index.md) · API 契约 [api/](../api/index.md)
