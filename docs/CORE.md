# MyStocks 核心文档入口

> **版本**: 1.0 | **更新日期**: 2026-07-12
> **维护者**: 文档治理团队
> **文档类型**: 总入口导航
> **规划依据**: [文档重构规划](plans/2026-07-12-documentation-restructure-plan.md)

---

## 按角色分流

| 角色 | 手册 | 关键能力 |
|------|------|---------|
| 🖥️ **开发** | [开发手册](dev/index.md) | API 开发、前端组件、数据源接入、架构红线、治理门禁 |
| 🧪 **测试** | [测试手册](test/index.md) | 测试策略、E2E 指南、CI/CD 管道、质量门禁 |
| ⚙️ **运维** | [运维手册](ops/index.md) | 部署、监控、备份恢复、排障、运行手册 |
| 🤖 **AI 工具** | [AI 工具手册](ai/index.md) | LLM API、AI 工具链、prompt 工程 |
| 📑 **API 契约** | [API 契约管理](api/index.md) | 契约文件、错误码、Apifox、集成指南 |

---

## 按功能域速查（10 域，详见 [FUNCTION_TREE.md](FUNCTION_TREE.md)）

| 域 | 核心代码路径 | API 前缀 | 开发入口 | 测试入口 | 运维入口 |
|---|---|---|---|---|---|
| 01-市场数据与行情 | `src/adapters/tdx/`, `src/adapters/akshare/` | `/api/market/*` | [dev/data-sources.md](dev/data-sources.md) | [市场 API 测试](../tests/api/file_tests/test_market_api.py) | [ops/monitoring.md](ops/monitoring.md) |
| 02-技术分析与指标 | `src/indicators/`, `src/analysis/` | `/api/technical/*` | [dev/api-development.md](dev/api-development.md) | [test/strategy.md](test/strategy.md) | — |
| 03-策略管理与回测 | `src/strategies/`, `src/backtest/` | `/api/strategy/*` | [guides/quant-trading/](../guides/quant-trading/) | [test/strategy.md](test/strategy.md) | — |
| 04-风险管理与监控 | `src/risk/`, `monitoring-stack/` | `/api/risk/*` | [dev/data-sources.md](dev/data-sources.md) | [test/quality-gate.md](test/quality-gate.md) | [ops/monitoring.md](ops/monitoring.md) |
| 05-投资组合与交易 | `src/portfolio/`, `src/trading/` | `/api/portfolio/*` | [dev/api-development.md](dev/api-development.md) | — | — |
| 06-监控与告警 | `monitoring-stack/` | `/api/monitoring/*` | — | — | [ops/monitoring.md](ops/monitoring.md) |
| 07-高级分析与 AI | `src/ai/`, `gpu_api_system/` | `/api/ai/*` | [ai/index.md](ai/index.md) | — | — |
| 08-系统管理与配置 | `config/`, `web/backend/app/core/` | `/api/config/*` | [dev/api-development.md](dev/api-development.md) | — | [ops/deployment.md](ops/deployment.md) |
| 09-数据存储与管理 | `src/db/`, `sql/` | `/api/data/*` | [dev/data-sources.md](dev/data-sources.md) | — | [ops/backup-recovery.md](ops/backup-recovery.md) |
| 10-公告与信息 | `src/info/` | `/api/info/*` | — | — | — |

---

## 通用入口（不分角色）

| 入口 | 位置 | 用途 |
|------|------|------|
| 架构红线 | [architecture/STANDARDS.md](../architecture/STANDARDS.md) | 编码红线、治理门禁、审批流程 |
| CI/CD 管道 | [operations/ci-cd/ARCHITECTURE.md](../operations/ci-cd/ARCHITECTURE.md) | 三层管道、36 workflow、本地 CI |
| 功能树 | [FUNCTION_TREE.md](FUNCTION_TREE.md) | 全部功能模块、入口链接、测试路径 |
| 治理主线 | [governance/mainline/](../governance/mainline/) | 治理规范、任务卡模板、门禁脚本 |
| Design 规格 | [design/](../design/) | Figma 指南、Token 定义、ArtDeco 规格 |
| Standards | [standards/](../standards/) | 安全标准、编码规范、文件组织规则 |
| 完整 Archives | [archive/](../archive/) | 历史 phase 报告、一次性产物归档 |

---

## 快速命令

```bash
# 本地开发
cd web/backend && uvicorn app.main:app --port 8020 --reload
cd web/frontend && npm run dev -- --port 3020

# 本地 CI 快跑
bash scripts/dev/ci/local_ci_check.sh
python3 scripts/ci/run_local_ci.py --quick

# 冒烟测试
python3 smoke_test.py

# Pre-commit 全量
pre-commit run --all-files

# 文档索引更新
python scripts/tools/docs_indexer.py --categories
```

---

> **文档完整度统计**（2026-07-12 起算）：完整 5 手册 / 分角色入口 5 个 / 功能域 10 域全覆盖。
> **重构状态**：Phase 1 骨架搭建中。[进度详情](plans/2026-07-12-documentation-restructure-plan.md)
