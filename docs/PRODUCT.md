# MyStocks 产品概览

> **生命周期**: supporting — 产品真相以根目录 [PRODUCT.md](../PRODUCT.md) 为准。本文档为 docs/ 读者提供便捷概览。

## 定位

MyStocks 是面向个人/小型量化投资者的 **本地化部署** 量化交易分析工具，覆盖 A 股市场。非 SaaS，非企业级多用户平台。

## 目标用户

| 用户类型 | 场景 |
|---------|------|
| 个人量化投资者 | 行情监控、策略回测、交易管理 |
| 小型量化团队 | 协作研究、信号分析、风险复盘 |

## 核心能力

| 能力 | 说明 |
|------|------|
| 行情监控 | 实时/历史行情、板块资金流、技术信号 |
| 策略回测 | 参数优化、ML 分析、批量回测 |
| 交易管理 | 持仓、盈亏、止损、委托跟踪 |
| 数据源集成 | 通达信、AkShare、Wencai 等多源数据 |

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + TypeScript + Pinia + ArtDeco 设计系统 |
| 后端 | Python / FastAPI / SQLAlchemy / Pydantic |
| 时序库 | TDengine 3.3+ |
| 关系库 | PostgreSQL 17+ / TimescaleDB |

## 快速入口

- 开发上手 → [guides/onboarding/](guides/onboarding/)
- API 文档 → [api/](api/)
- 部署运维 → [operations/](operations/)
- 设计系统 → [standards/](standards/)
- 产品真相 → [根目录 PRODUCT.md](../PRODUCT.md)
