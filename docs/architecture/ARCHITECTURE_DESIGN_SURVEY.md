# MyStocks 项目架构设计文档调查报告

> **生成时间**: 2026-07-29
> **调查范围**: `architecture/`, `docs/architecture/`, `docs/api/`, `docs/design/`, `docs/guides/frontend/`, `docs/standards/`, `docs/`
> **调查方法**: 逐层遍历索引文件 + 关键文档深度阅读 + 源码交叉验证
> **文档数量**: 涉及约 300+ 篇架构相关文档，精读约 30 篇核心文档

---

## 目录

- [一、架构核心入口与顶层文档](#一架构核心入口与顶层文档)
- [二、前端框架架构](#二前端框架架构)
- [三、后端 API 实现架构](#三后端-api-实现架构)
- [四、API 契约管理](#四api-契约管理)
- [五、数据库架构](#五数据库架构)
- [六、领域驱动设计（DDD）架构](#六领域驱动设计ddd架构)
- [七、工程红线与开发流程](#七工程红线与开发流程)
- [八、其他重要架构文档](#八其他重要架构文档)
- [九、搜索建议与导航](#九搜索建议与导航)

---

## 一、架构核心入口与顶层文档

### 1.1 架构红线与准则

- **文件**: `architecture/STANDARDS.md`
- **版本**: V3.1
- **核心内容**:
  - **方案先行准则** — 任何菜单结构/UI-UX/核心架构变更必须先提交方案并获审批
  - **六步走战略** — 契约先行 → 单体骨架 → Mock 驱动 → 垂直切片 → 可观测性 → 自动化防护网
  - **前端开发红线** — 路由纯净度、路径语义化、ArtDeco 令牌引用、TRACE_ID 显化
  - **后端开发红线** — 单例防御、导入安全性、响应标准化（UnifiedResponse）
  - **环境一致性** — PM2/Docker 优先，不容忍碎片化命令行启动

### 1.2 架构域边界

- **文件**: `architecture/DOMAIN_BOUNDARIES.md`
- **5 大架构域**:
  1. **核心域** (`src/core/`) — 配置驱动表管理、统一管理器、数据分类、数据库连接池
  2. **数据访问域** (`src/data_access/`) — TDengine/PostgreSQL 双路访问层、智能路由
  3. **业务服务域** (`src/services/`, `src/adapters/`) — 7 个数据源适配器、实时行情、回测引擎
  4. **监控与质量域** (`src/monitoring/`) — 监控数据库、告警管理、数据质量监控
  5. **Web 与 API 域** (`web/`) — FastAPI 后端、Vue 3 前端

### 1.3 架构文档索引

| 文件 | 文档数 | 说明 |
|------|--------|------|
| `architecture/INDEX.md` | 99 | 架构目录归档索引 |
| `docs/architecture/INDEX.md` | 107 | 活跃架构文档索引 |

### 1.4 核心文档入口

- **文件**: `docs/CORE.md`
- **5 角色分流**: 开发手册 / 测试手册 / 运维手册 / AI 工具手册 / API 契约手册
- **10 功能域速查**: 每个域对应的代码路径、API 前缀、开发入口、测试入口、运维入口
- **通用入口**: 架构红线、CI/CD 管道、功能树、治理主线、Design 规格、Standards

### 1.5 功能树

- **文件**: `docs/FUNCTION_TREE.md`（570 行）
- **11 大功能域**:

| 域 | 完成度 | API 前缀 |
|----|--------|----------|
| 01-市场数据与行情 | 95% | `/api/market/*`, `/api/tdx/*` |
| 02-技术分析与指标 | 90% | `/api/indicators/*`, `/api/technical/*` |
| 03-策略管理与回测 | 85% | `/api/strategy_management/*`, `/api/backtest/*` |
| 04-风险管理与监控 | 80% | `/api/risk/*` |
| 05-投资组合与交易 | 70% | `/api/portfolio/*` |
| 06-监控与告警 | 75% | `/api/monitoring/*` |
| 07-高级分析与 AI | 50% | `/api/ai/*` |
| 08-系统管理与配置 | 85% | `/api/config/*` |
| 09-数据存储与管理 | 90% | `/api/data/*` |
| 10-公告与信息 | 80% | `/api/info/*` |
| 11-文档治理与基础设施 | 85% | — |

---

## 二、前端框架架构

### 2.1 技术栈清单

| 类别 | 选型 | 版本 | 用途 |
|------|------|------|------|
| 核心框架 | **Vue 3** (Composition API) | ^3.4.0 | 前端主框架 |
| UI 组件库 | **Element Plus** | ^2.13.0 | 桌面级 UI 组件（表格/表单/导航） |
| 状态管理 | **Pinia** | ^2.2.0 | 全局状态与 API 数据管理 |
| 路由 | **Vue Router 4** | ^4.3.0 | 前端路由（含 Meta 扩展） |
| 构建工具 | **Vite 5** | ^5.4.0 | 前端构建与 HMR |
| 图表引擎 | **ECharts 5** | ^5.5.0 | 通用数据可视化 |
| K 线图表 | **KLineCharts** | ^9.8.12 | 金融 K 线图专用 |
| 类型系统 | **TypeScript** | ~5.3.0 | 类型安全 |
| 类型检查 | **vue-tsc** | ^1.8.27 | 编译时类型检查 |
| HTTP 客户端 | **Axios** | ^1.13.2 | API 调用（拦截器模式） |
| Mock | **MSW** | ^2.12.14 | 前端 Mock 数据服务 |
| 设计令牌 | **ArtDeco** (SCSS) | 自定义 | 统一视觉系统 |
| CSS 引擎 | **Sass/SCSS** | ^1.77.0 | 样式预处理器 |
| 单元测试 | **Vitest** + **@vue/test-utils** | ^4.0.16 / ^2.4.6 | 组件/逻辑测试 |
| E2E 测试 | **Playwright** | ^1.57.0 | 端到端浏览器测试 |
| 组件自动化 | **unplugin-vue-components** | ^0.27.0 | 自动注册组件 |
| i18n | **vue-i18n** | ^11.2.8 | 国际化 |
| 自动化导入 | **unplugin-auto-import** | ^0.18.6 | 自动导入 API |

### 2.2 关键架构文档清单

| 文档路径 | 内容概要 | 建议场景 |
|----------|----------|----------|
| `docs/architecture/MENU_ARCHITECTURE_V3.2_ELITE.md` | 菜单架构完整方案 | 导航/路由设计 |
| `docs/architecture/FRONTEND_OPTIMIZATION_STRATEGY_V3.md` | 前端优化 V3.0，461 行 | 页面清理/能力提取 |
| `docs/architecture/FRONTEND_OPTIMIZATION_IMPLEMENTATION_PLAN_V2.md` | 前端代码优化实施方案 | 性能优化 |
| `docs/design/MYSTOCKS_DESIGN_SPECIFICATION.md` | 完整设计规范，728 行 | UI 设计/组件开发 |
| `docs/design/COMPONENT_LIBRARY_SPECIFICATION.md` | 组件库规范 | 组件开发 |
| `docs/api/PINIA_API_STANDARDIZATION.md` | Pinia 数据获取标准化，910 行 | 前端与后端对接 |
| `docs/guides/frontend/FRONTEND_ROUTING_OPTIMIZATION_GUIDE.md` | 路由优化指南 | 路由重构 |
| `docs/guides/frontend/frontend-change-hygiene-and-micro-commit-guide.md` | 前端变更卫生规范 | 微提交规范 |
| `docs/guides/frontend/enhanced-ui-ux-guide.md` | UI-UX 增强指南 | 交互优化 |
| `docs/guides/frontend/css-scss-development-guide.md` | CSS/SCSS 开发指南 | 样式开发 |
| `docs/standards/WEB_USABILITY_STANDARDS.md` | Web 可用性标准 | 可访问性 |

### 2.3 前端分层架构

```
┌────────────────────────────────────────────┐
│ 组件层 (Vue Components)                     │
│  views/        — 页面级组件                  │
│  components/   — 通用/业务组件 (含 artdeco/) │
│  layouts/      — 布局组件 (ArtDecoLayout)    │
├────────────────────────────────────────────┤
│ Store层 (Pinia Stores)                      │
│  stores/       — 数据 + 状态 + 缓存管理      │
├────────────────────────────────────────────┤
│ 服务层 (API Services)                       │
│  api/apiClient.ts  — HTTP 客户端 (Axios)    │
│  api/unifiedApiClient.ts — 旧版兼容桥接      │
│  api/market.ts / strategy.ts / ...          │
│  api/artdeco/  — ArtDeco 专属 API 封装       │
├────────────────────────────────────────────┤
│ 基础设施层                                   │
│  router/index.ts  — 路由声明 + 守卫          │
│  utils/           — 工具函数                 │
│  composables/     — 组合式逻辑复用           │
│  mock/            — MSW Mock 数据定义        │
│  styles/          — 全局样式 + ArtDeco 令牌  │
└────────────────────────────────────────────┘
```

### 2.4 路由架构

- **入口文件**: `web/frontend/src/router/index.ts`（389 行）
- **路由结构**: `ArtDecoLayoutEnhanced.vue` 为统一布局包裹
- **路由 Meta 扩展**:

```typescript
interface RouteMeta {
  title: string          // 页面标题
  requiresAuth?: boolean // 是否需要登录
  icon?: string          // 菜单图标
  api?: string           // 关联的 API 端点
  layout?: 'ArtDeco' | 'Blank'  // 布局模板
  isDetail?: boolean     // 是否是详情页
  group?: string         // 业务域分组
}
```

- **7 大业务路由组**: market / data / watchlist / strategy / trade / risk / system
- **详情页路由**: `/detail/graphics/:symbol`（图形式）、`/detail/news/:symbol`（资讯式）
- **Home 路由**: `/dashboard`（交易室），`/dealing-room` 历史兼容重定向

### 2.5 菜单导航层级

根据 `MENU_ARCHITECTURE_V3.2_ELITE.md`：

| 层级 | 名称 | 特点 |
|------|------|------|
| P0 | 核心驾驶舱 (Dealing Room) | `/dashboard`，侧边栏隐藏 |
| P1 | 业务域菜单 | 7 大域，侧边栏显性入口 |
| P2 | 交互详情页 | 无菜单入口，点击触发 |

**7 大业务域**:
- **市场行情**: 实时行情流 / K 线分析 / 龙虎榜
- **数据分析**: 板块动向 / 概念动向 / 资金流向 / 指标分析
- **自选管理**: 组合管理 / 信号雷达 / 策略选股
- **策略管理**: 策略仓库 / 回测引擎 / GPU 加速 / 参数优化 / 仓位管理
- **交易管理**: 头寸管理 / 交易终端 / 信号监控 / 持仓透视 / 历史对账
- **风险管理**: 风险概览 / 组合盈亏 / 止损雷达 / 告警中心 / 舆情公告
- **系统设置**: 系统配置 / 健康矩阵 / API 终端 / 数据源管理

### 2.6 API Client 层设计与标准化

**统一 API 客户端** (`web/frontend/src/api/apiClient.ts`):
- 基于 Axios，带 JWT 与 CSRF 双令牌自动注入
- 统一 `UnifiedResponse<T>` 泛型响应包装
- 全链路 RequestId + ProcessTime 追溯提取
- 30 秒超时 + 带凭据请求
- 响应拦截器自动提取 tracing headers

**Pinia Store 标准化** (`docs/api/PINIA_API_STANDARDIZATION.md`):
- **Store First** — 所有 API 调用通过 Pinia Store
- **三元状态** — 每个 Store 提供 `data`、`loading`、`error`
- **缓存透明** — 5 分钟自动过期，支持 forceRefresh
- **错误友好** — `ContractValidationError` + 用户友好的错误提示
- **类型安全** — 完整 TypeScript 泛型

**前端类型自动生成**:
- `scripts/generate_frontend_types.py` 从 Pydantic 模型自动生成 TS 类型
- 作为 `npm run dev` 和 `npm run build` 的前置步骤

---

## 三、后端 API 实现架构

### 3.1 技术栈清单

| 类别 | 选型 | 说明 |
|------|------|------|
| Web 框架 | **FastAPI** | 异步高性能 |
| 数据验证 | **Pydantic v2** | Schema 定义与校验 |
| ORM | **SQLAlchemy 2.0** | 数据库 ORM |
| 任务队列 | **Celery** | 异步任务处理 |
| 缓存 | **Redis** | 缓存/会话/CSRF 令牌 |
| 监控 | **Prometheus + Grafana** | 指标收集与可视化 |

### 3.2 后端模块组织

```
web/backend/app/
├── main.py              # FastAPI 主入口（691 行）
├── app_factory.py       # 应用工厂模式
├── openapi_config.py    # OpenAPI 配置
├── router_registry.py   # 路由注册表
├── api/                 # API 路由
├── models/              # SQLAlchemy 模型
├── schemas/             # Pydantic Schema
├── services/            # 业务逻辑层
├── core/                # 核心基础设施
│   ├── config.py        # 配置管理
│   ├── database.py      # 数据库连接
│   ├── exception_handler.py  # 全局异常处理
│   ├── middleware/       # 性能监控中间件
│   ├── readiness.py     # 健康检查探针
│   ├── socketio_manager.py # WebSocket 管理
│   └── redis_client.py  # Redis 客户端
├── middleware/           # 中间件
│   └── response_format.py # UnifiedResponse 格式化
├── gateway/             # API 网关
├── repositories/        # 数据仓储层
├── tasks/               # Celery 任务
├── mock/                # Mock 数据
└── data_sources/        # 数据源管理
```

### 3.3 核心 API 端点

#### 认证模块

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 用户登录 |
| POST | `/api/v1/auth/logout` | 用户登出 |
| GET | `/api/v1/auth/me` | 获取当前用户 |
| POST | `/api/v1/auth/refresh` | 刷新 Token |
| GET | `/api/v1/auth/csrf` | 获取 CSRF Token |

#### 市场数据模块

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/v1/market/symbols` | 股票列表 |
| GET | `/api/v1/market/kline` | K 线数据 |
| GET | `/api/v1/market/realtime` | 实时行情 |
| GET | `/api/v1/market/quotes` | 盘口报价 |
| GET | `/api/v1/market/history` | 历史数据 |
| GET | `/api/v1/market/moneyflow` | 资金流向 |
| GET | `/api/v1/market/limit` | 涨跌停信息 |
| GET | `/api/v1/market/adj` | 复权因子 |

#### 策略管理模块

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/v1/strategies` | 策略列表 |
| POST | `/api/v1/strategies` | 创建策略 |
| GET | `/api/v1/strategies/{id}` | 策略详情 |
| PUT | `/api/v1/strategies/{id}` | 更新策略 |
| DELETE | `/api/v1/strategies/{id}` | 删除策略 |
| POST | `/api/v1/strategies/{id}/clone` | 克隆策略 |
| PUT | `/api/v1/strategies/{id}/status` | 更新状态 |

#### 回测模块

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/backtests` | 创建回测 |
| GET | `/api/v1/backtests/{id}` | 回测结果 |
| GET | `/api/v1/backtests/{id}/trades` | 回测交易记录 |
| GET | `/api/v1/backtests/{id}/equity` | 权益曲线 |
| GET | `/api/v1/backtests/{id}/metrics` | 回测指标 |
| DELETE | `/api/v1/backtests/{id}` | 删除回测 |

#### 交易模块

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/trade/order` | 下单 |
| POST | `/api/v1/trade/cancel` | 撤单 |
| GET | `/api/v1/trade/orders` | 查询委托 |
| GET | `/api/v1/trade/positions` | 查询持仓 |
| GET | `/api/v1/trade/account` | 查询账户 |

#### 系统监控模块

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/metrics` | Prometheus 指标 |
| GET | `/api/v1/system/status` | 系统状态 |
| GET | `/api/v1/system/info` | 系统信息 |
| GET | `/api/v1/system/version` | 版本信息 |

### 3.4 响应格式标准化

根据 `docs/standards/API_RESPONSE_STANDARDIZATION.md`（779 行）：

**通用格式**:
```json
{
  "success": true,
  "code": 0,
  "message": "请求成功",
  "data": { /* 实际数据 */ },
  "timestamp": "2025-11-28T11:30:00.123456Z",
  "pagination": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

- `success`: boolean，必需
- `code`: integer，业务状态码（0 成功 / 400 客户端错误 / 500 服务器错误）
- `message`: string，可选
- `data`: object/array，取决于端点
- `timestamp`: ISO 8601，必需
- `pagination`: 仅列表端点需要

---

## 四、API 契约管理

### 4.1 核心架构文档

| 文档路径 | 内容概要 |
|----------|----------|
| `docs/api/CONTRACT_MANAGEMENT_API.md` | 契约管理平台完整 API 文档（1005 行） |
| `docs/api/API_CONTRACT_ARCHITECTURE_ANALYSIS.md` | 契约架构完整分析（331 行） |
| `docs/api/contracts/market_api.yaml` | 市场 API 契约 YAML 定义 |
| `docs/api/PINIA_API_STANDARDIZATION.md` | 前端 API 获取标准化（910 行） |
| `docs/standards/API_RESPONSE_STANDARDIZATION.md` | 后端响应格式标准化（779 行） |
| `docs/api/API契约同步组件实现方案.md` | 契约同步组件实现 |
| `docs/api/API_CONTRACT_PLATFORM_DEPLOYMENT_REPORT.md` | 平台部署报告 |
| `docs/api/API_CONTRACT_PLATFORM_NEXT_STEPS.md` | 下一步计划 |

### 4.2 分层架构

```
┌─ api-contract-sync-manager（契约管理平台）───┐
│  契约仓库 | 版本控制 | 可视化编辑 | 权限管理    │
│  校验规则 | 差异检测                          │
├─ api-contract-sync（契约同步工具）───────────┤
│  AST 代码扫描 | 响应实时校验 | 测试生成        │
│  差异告警 | CI/CD 集成                       │
├─ API 实现层 ─────────────────────────────────┤
│  FastAPI + Pydantic + SQLAlchemy              │
└─ 外部集成层 ─────────────────────────────────┘
  前端调用 | 测试用例 | 三方系统 | API 网关
```

### 4.3 设计原则

1. **Schema First Architecture** — Pydantic 模型作为单一真相源
2. **Contract First Development** — 先更新契约，再修改代码
3. **语义化版本控制** — SemVer (MAJOR.MINOR.PATCH)
4. **自动化验证** — CI/CD 流水线集成

### 4.4 契约管理 API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/contracts/versions` | 创建契约版本 |
| GET | `/api/contracts/versions/{id}` | 获取版本详情 |
| PUT | `/api/contracts/versions/{id}` | 更新版本 |
| DELETE | `/api/contracts/versions/{id}` | 删除版本 |
| POST | `/api/contracts/versions/{id}/activate` | 激活版本 |
| POST | `/api/contracts/versions/{id}/diff` | 差异检测 |
| GET | `/api/contracts/validate` | 验证 OpenAPI 规范 |

### 4.5 同步工具核心能力

- **AST 解析**: 扫描 FastAPI 路由定义，提取 URL、方法、参数、响应模型
- **自动对比**: 代码实现与契约规范的字段级对比
- **类型校验**: 验证 Pydantic 模型与契约一致性
- **响应校验**: 运行时自动校验响应格式

---

## 五、数据库架构

### 5.1 双数据库策略

| 维度 | TDengine 3.0+ | PostgreSQL + TimescaleDB |
|------|---------------|--------------------------|
| **定位** | 高频时序数据 | 历史分析 & 交易数据 |
| **数据** | Tick 数据、分钟 K 线、深度数据 | 日线 K 线、技术指标、参考数据、交易记录、元数据 |
| **压缩** | ~20:1 | 标准 |
| **写入** | 百万级事件/秒 | 事务型 ACID |
| **查询** | 时序聚合查询 | 复杂 JOIN、全文搜索 |
| **保留策略** | 自动保留策略 | 自动分区 (TimescaleDB) |

### 5.2 数据分类与路由

**5 大数据分类** (`src/core/`):
- `TICK_DATA`: 逐笔成交
- `MINUTE_KLINE`: 分钟 K 线
- `DAILY_KLINE`: 日线数据
- `TECHNICAL_INDICATOR`: 技术指标
- `REFERENCE_DATA`: 参考数据

**智能路由**: `UnifiedDataAccessManager` 根据 `DataClassification` 枚举自动分配到对应引擎

### 5.3 数据库表设计

**TDengine 超表**:
```
market_data 数据库
├── tick_data (tags: symbol, exchange)
├── minute_kline (tags: symbol, frequency)
└── depth_data (tags: symbol, exchange)
```

**PostgreSQL 表**:
```
quant_research 数据库
├── daily_kline (TimescaleDB hypertable, 索引: symbol+date)
├── symbols (标准表, 索引: symbol/exchange/sector)
├── technical_indicators (hypertable)
├── quantitative_factors
├── model_outputs
├── trading_signals
├── order_records (hypertable)
├── transaction_records
├── position_records
├── account_funds
└── 元数据表 (data_sources, task_schedules, strategy_parameters, system_config)
```

### 5.4 关键文档

| 文档路径 | 内容概要 |
|----------|----------|
| `docs/architecture/DATABASE_ARCHITECTURE.md` | 数据库架构完整文档（601 行） |
| `docs/architecture/TDengine_Schema_Design.md` | TDengine 超表与查询设计 |
| `docs/architecture/PostgreSQL_Schema_Design.md` | PostgreSQL 表结构与索引 |
| `docs/architecture/DATASOURCE_AND_DATABASE_ARCHITECTURE.md` | 数据源与数据库架构说明 |
| `docs/architecture/ADAPTER_AND_DATABASE_ARCHITECTURE_EVALUATION.md` | 适配器与数据库评估报告 |
| `config/table_config.yaml` | 库表配置 YAML 定义 |

---

## 六、领域驱动设计（DDD）架构

### 6.1 单体骨架分层约束

根据 `architecture/STANDARDS.md`：

```
┌────────────────────────────────────┐
│  UI/API (最上层)                    │
│  Vue 组件 / FastAPI 路由            │
├────────────────────────────────────┤
│  Application (业务服务层)            │
│  业务服务逻辑                        │
├────────────────────────────────────┤
│  Infra (基础设施层)                  │
│  数据库适配器 / API Client / Redis   │
├────────────────────────────────────┤
│  Domain (领域层)                    │
│  纯实体定义（无业务逻辑）              │
├────────────────────────────────────┤
│  Core (最下层，无依赖)               │
│  工具类 / 配置 / 日志                │
└────────────────────────────────────┘
```

**关键约束**: 禁止底层模块依赖上层模块，禁止循环依赖。

### 6.2 关键文档

| 文档路径 | 内容概要 |
|----------|----------|
| `architecture/DDD_ARCHITECTURE_NOTES.md` | DDD 架构笔记 |
| `architecture/DDD_IMPLEMENTATION_PLAN.md` | DDD 实施计划 |
| `architecture/DDD_OPTIMIZATION_SUMMARY.md` | DDD 优化总结 |

---

## 七、工程红线与开发流程

### 7.1 六步走战略

取自 `architecture/STANDARDS.md`：

| 步骤 | 原则 | 核心要求 |
|------|------|----------|
| 1. 契约先行 | **Contract First** | 先定义 OpenAPI → 生成 Pydantic Models → 生成 TS 类型 |
| 2. 单体骨架 | **Monolithic Skeleton** | 分层约束，禁止循环依赖 |
| 3. Mock 驱动 | **Mock Driven** | 前后端解耦，MSW 或后端 Mock 模式 |
| 4. 垂直切片 | **Vertical Slicing** | 一次做一个 Feature 的完整垂直流 |
| 5. 可观测性 | **Observability** | RequestId 全链路追踪、Health 探针、启动校验 |
| 6. 自动化防护网 | **Safety Net** | CI/CD 自动冒烟测试，拒绝手动回归 |

### 7.2 技术工程红线

**前端红线**:
- 路由纯净度：`App.vue` 严禁硬编码业务组件，必须用 `<router-view />`
- 路径语义化：路径必须与路由实现一致，不一致时使用 `alias`
- 禁止硬编码样式：样式必须引用 `artdeco-tokens.scss` 变量
- TRACE_ID 显化：所有业务 Tab 必须在 UI 预留 Request ID 展示位

**后端红线**:
- 单例防御：所有 `global` 变量必须在模块顶层初始化为 `None`
- 导入安全性：重构后清理已废弃模块引用
- 响应标准化：所有 API 返回 `UnifiedResponse` 包装

### 7.3 环境一致性

- **PM2/Docker 优先**: `ecosystem.config.js` 及其配套环境是"一等公民"
- 严禁依赖碎片化的命令行启动

### 7.4 代码质量标准

| 类别 | 工具 | 配置 |
|------|------|------|
| 格式化 | **Black** | line-length: 120 |
| 类型检查 | **MyPy** | strict mode |
| 快速 Lint | **Ruff** | Black 兼容 |
| 深度分析 | **Pylint** | 评分目标 8.0+/10 |
| 安全扫描 | **Bandit** | CI 门禁 |
| 依赖安全 | **Safety** | 依赖漏洞扫描 |
| Pre-commit | **pre-commit** | 全量门禁 hooks |

**导入规范**:
- 绝对导入：`from src.core import ConfigDrivenTableManager`
- 分组：标准库 → 第三方 → 本地
- 禁止通配符导入
- 类型提示：函数参数和返回值必须有类型

---

## 八、其他重要架构文档

### 8.1 数据源架构

| 文档路径 | 内容概要 |
|----------|----------|
| `docs/architecture/DATASOURCE_ARCHITECTURE_FIRST_PRINCIPLES_ANALYSIS.md` | 数据源第一性原理评审 |
| `docs/architecture/ADAPTER_SIMPLIFICATION_COMPLETE_GUIDE.md` | 7 数据源适配器精简指南 |
| `docs/architecture/ADAPTER_EXTENSION_GUIDE.md` | 适配器扩展指南 |
| `docs/architecture/ADAPTER_ROUTING_GUIDE.md` | 适配器路由功能详解 |
| `docs/architecture/DATA_SOURCE_MANAGEMENT_V2.md` | 数据源注册与治理中心 V2 |
| `config/adapter_priority_config.yaml` | 适配器优先级配置 |
| `config/data_sources_registry.yaml` | 数据源注册表 |

### 8.2 7 大适配器（数据源）

| 适配器 | 优先级 | 状态 | 说明 |
|--------|--------|------|------|
| TDX (通达信) | 1 | ✅ | 主数据源，直连通达信 |
| AKShare | 2 | ✅ | 综合数据源，DataSourceFactory fallback |
| EFinance | 3 | ✅ | 东方财富数据 |
| BaoStock | 4 | ✅ | 高质量历史数据 |
| SinaFinance | 5 | ✅ | 股票评级 |
| Tushare | 6 | ⚠️ | 需 Token 配置 |
| Byapi | 7 | ⚠️ | 403 问题待修 |
| OpenStock | 8 | ✅ | 外部 HTTP 数据源，`/quotes`、`/kline` 路由 |

### 8.3 安全性架构

| 文档路径 | 内容概要 |
|----------|----------|
| `docs/standards/SECURITY_REMEDIATION_GUIDE.md` | 安全修复指南 |
| `docs/standards/SECURITY_AUDIT_REPORT_20251130.md` | 2025-11-30 安全审计 |
| `docs/standards/SECURITY_AUDIT_REPORT_2025-12-23.md` | 2025-12-23 安全审计 |
| `docs/standards/SECURITY_QUICK_REFERENCE.md` | 安全快速参考 |
| `docs/standards/PHASE0_CREDENTIAL_ROTATION_GUIDE.md` | 凭据轮换指南 |
| `docs/standards/RESOURCE_LEAK_AUDIT_REPORT.md` | 资源泄漏审计 |

### 8.4 E2E 测试架构

| 文档路径 | 内容概要 |
|----------|----------|
| `docs/guides/pm2/` | PM2 进程管理 |
| `config/ecosystem.playwright.config.js` | Playwright E2E PM2 配置 |
| `config/playwright.e2e.config.ts` | E2E Playwright 配置 |
| `config/playwright.config.ts` | 通用 Playwright 配置 |
| `scripts/run_e2e_pm2.sh` | E2E 冒烟测试脚本 |
| `docs/guides/frontend/PR_GATE_QUICK_REFERENCE.md` | PR 门禁快速参考 |

### 8.5 部署与运维

| 文档路径 | 内容概要 |
|----------|----------|
| `docker/docker-compose.prod.yml` | 生产 Docker Compose |
| `docker/docker-compose.test.yml` | 测试 Docker Compose |
| `docker/monitoring-stack.yml` | 监控栈（Prometheus+Grafana+Loki） |
| `config/ecosystem.production.config.js` | 生产 PM2 配置 |
| `config/prometheus.yml` | Prometheus 配置 |
| `config/alertmanager.yml` | 告警管理配置 |
| `config/grafana-dashboard-provider.yml` | Grafana 面板提供者 |

### 8.6 CI/CD 工作流

全部位于 `.github/workflows/`，涵盖：

| 工作流 | 用途 |
|--------|------|
| `code-quality.yml` | 代码质量（Black, MyPy, Ruff, Bandit, Safety） |
| `test-coverage.yml` | 测试覆盖率 |
| `security-testing.yml` | 安全扫描 |
| `comprehensive-testing.yml` | 全栈集成测试 |
| `e2e-testing.yml` | 端到端 Playwright |
| `api-compliance-testing.yml` | API 合规验证 |
| `contract-testing.yml` | 契约测试 |
| `frontend-testing.yml` | 前端测试 |
| `p0-quality-gate.yml` | P0 质量门禁 |
| `quant-strategy-validation.yml` | 量化策略验证 |

### 8.7 多 CLI 协作架构

| 文档路径 | 内容概要 |
|----------|----------|
| `docs/architecture/MULTI_CLI_COLLABORATION_V2_IMPLEMENTATION.md` | Git Worktree 多 CLI 协作 V2 |
| `docs/guides/multi-cli-tasks/` | 多 CLI 任务操作手册 |
| `docs/guides/multi-cli-tasks/MULTI_CLI_WORKTREE_MANAGEMENT.md` | Worktree 管理规则 |
| `TASK.md` + `TASK-REPORT.md` | Worker CLI 任务报告 |

### 8.8 Mock 与测试数据

| 文档路径 | 内容概要 |
|----------|----------|
| `docs/architecture/Mock数据系统指南.md` | Mock 数据系统使用指南 |
| `docs/guides/mock-data/` | Mock 数据指南 |
| `tests/` | 测试目录（unit/integration/e2e/contract/performance/security） |

---

## 九、搜索建议与导航

### 按关键词搜索

| 关键词 | 相关内容 |
|--------|----------|
| 菜单架构 | `MENU_ARCHITECTURE_V3.2_ELITE.md` — 导航层级、7 大域、详情页 |
| Pinia 标准化 | `PINIA_API_STANDARDIZATION.md` — Store First、三元状态、缓存 |
| ArtDeco | `docs/design/` — 设计令牌、颜色系统、组件库规范 |
| 契约管理 | `CONTRACT_MANAGEMENT_API.md` — 版本管理、差异检测、CI/CD |
| 双库架构 | `DATABASE_ARCHITECTURE.md` — TDengine vs PostgreSQL 路由 |
| 统一响应 | `API_RESPONSE_STANDARDIZATION.md` — UnifiedResponse 规范 |
| 六步走战略 | `architecture/STANDARDS.md` — 开发流程全流程 |
| 工程红线 | `architecture/STANDARDS.md` — 前端/后端/环境红线 |
| 功能树 | `FUNCTION_TREE.md` — 10 大域 API/代码/测试入口 |
| 适配器 | `ADAPTER_SIMPLIFICATION_COMPLETE_GUIDE.md` — 7 数据源 |
| E2E 测试 | `playwright.config.ts`、`scripts/run_e2e_pm2.sh` |
| DDD | `DDD_IMPLEMENTATION_PLAN.md` — 分层约束 |
| 安全 | `SECURITY_REMEDIATION_GUIDE.md` — CSRF/JWT/凭据 |
| 多 CLI 协作 | `MULTI_CLI_COLLABORATION_V2_IMPLEMENTATION.md` — Worktree |
| CI/CD | `.github/workflows/` — 36 工作流 |

### 快速命令

```bash
# 本地后端开发
cd web/backend && uvicorn app.main:app --port 8020 --reload

# 本地前端开发
cd web/frontend && npm run dev -- --port 3020

# 全量测试
pytest

# 前端类型检查
cd web/frontend && vue-tsc --noEmit

# 本地 CI 快速检查
bash scripts/dev/ci/local_ci_check.sh
python3 scripts/ci/run_local_ci.py --quick

# 冒烟测试
python3 smoke_test.py

# E2E 冒烟
bash scripts/run_e2e_pm2.sh

# 文档索引更新
python scripts/tools/docs_indexer.py --categories
```

### 服务地址

| 服务 | 地址 |
|------|------|
| 后端 API | `http://localhost:8020` |
| Swagger UI | `http://localhost:8020/docs` |
| ReDoc | `http://localhost:8020/redoc` |
| 前端 | `http://localhost:3020` |
| OpenAPI Schema | `http://localhost:8020/openapi.json` |
| Grafana | `http://localhost:3000` |
| Prometheus | `http://localhost:9090` |
| Health 探针 | `http://localhost:8020/health` |
| Metrics | `http://localhost:8020/metrics` |

---

*本文档由自动化架构调查生成，基于项目文档与源码的交叉验证。部分文档路径如存在重定向（如 ArtDeco Master Index），请以目标位置为准。*
