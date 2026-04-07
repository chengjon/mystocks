# Directory Structure

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 当前执行口径请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，并结合当前代码实现与主线治理文档使用。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码或主线文档冲突，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、当前代码与主线治理文档为准。


**Last mapped**: 2026-04-05

## Top-Level Layout

```
mystocks_spec/
├── src/                    # Python 核心业务代码 (38 子目录)
├── web/
│   ├── backend/app/        # FastAPI 后端 (530 Python 文件)
│   └── frontend/src/       # Vue 3 前端 (908 .vue+.ts 文件)
├── tests/                  # 测试文件 (908 文件)
├── scripts/                # 脚本工具
├── config/                 # 配置文件
├── docs/                   # 文档
├── architecture/           # 架构设计文档
├── reports/                # 生成的分析报告
├── monitoring-stack/       # 监控栈
├── gpu_api_system/         # GPU 加速系统
├── .worktrees/             # Git worktree (4个, 2.5GB)
├── core.py                 # 兼容 shim
├── data_access.py          # 兼容 shim
├── monitoring.py           # 兼容 shim
└── unified_manager.py      # 兼容 shim
```

## src/ — Python 核心代码

```
src/
├── adapters/               # 数据源适配器 (akshare, efinance, tdx, financial)
├── interfaces/adapters/    # ⚠️ 适配器接口层（与 adapters/ 完全重复，缺 import）
├── advanced_analysis/      # 高级分析
├── algorithms/             # 算法（HMM, SVM, naive_bayes 等）
├── application/            # 应用服务层（portfolio, watchlist, market_data, bootstrap）
├── backtesting/            # 回测
├── calcu/                  # ⚠️ 命名不规范（应为 calculator）
├── core/                   # 核心模块（unified_manager, config, cache, data_classification）
├── cron/                   # 定时任务
├── data_access/            # 数据访问层（TDengine, PostgreSQL, factory, interfaces）
├── data_access_pkg/        # ⚠️ 另一份数据访问包（与 data_access/ 重叠）
├── data_governance/        # 数据治理
├── data_sources/           # 数据源（mock/, real/）
├── database/               # 数据库服务（connection, query, service）
├── database_optimization/  # ⚠️ 数据库优化（与 database/ 重叠）
├── db_manager/             # ⚠️ 仅含 __init__.py（空壳）
├── domain/                 # 领域模型
├── factories/              # 工厂模式
├── governance/             # 治理
├── gpu/                    # GPU 加速（api_system, acceleration, core/kernels）
├── indicators/             # 技术指标
├── infrastructure/         # 基础设施（market_data, event_bus, caching）
├── interfaces/             # 接口定义（⚠️ 含 adapters/ 子目录与 src/adapters/ 重复）
├── logging/                # 日志
├── ml_strategy/            # ML 策略（automation, predefined_tasks）
├── mock/                   # Mock 数据（40+ 文件，按业务模块组织）
├── monitoring/             # 监控（alert_history, decoupled_monitoring, alert_notifier）
├── portfolio/              # 组合管理
├── reporting/              # 报告
├── routes/                 # ⚠️ 路由（应在 web/backend/app/api/）
├── api/                    # ⚠️ 额外路由（与 routes/ 和 web/backend/app/api/ 重叠）
├── services/               # 服务层
├── storage/                # 存储层（database/manager 按 part1/part2/part3 拆分）
├── styles/                 # 样式（在 Python src/ 中）
├── trading/                # 交易
├── utils/                  # 工具函数
└── visualization/          # 可视化
```

## web/backend/app/ — FastAPI 后端

```
web/backend/app/
├── main.py                 # 应用入口 (885 行, 含 CSRF 管理)
├── app_factory.py          # 应用工厂 (432 行)
├── openapi_config.py       # OpenAPI 配置 (724 行)
├── router_registry.py      # 路由注册中心
├── api/                    # API 路由 (205 个文件)
│   ├── VERSION_MAPPING.py  # API 版本映射
│   ├── v1/                 # v1 版本路由
│   ├── contract/           # 契约测试路由
│   └── [200+ 独立路由文件]
├── core/                   # 核心配置
│   ├── config.py           # Pydantic Settings
│   ├── database.py         # 数据库连接
│   ├── exception_handler.py
│   ├── middleware/          # 中间件（性能监控等）
│   └── socketio_manager.py
├── services/               # 业务服务 (14 子目录)
├── models/                 # 数据模型
├── schemas/                # Pydantic Schema
├── middleware/             # 中间件（响应格式等）
├── mock/                   # 后端 Mock 数据 (11 文件)
└── adapters/               # 后端适配器
```

## web/frontend/src/ — Vue 3 前端

```
web/frontend/src/
├── main.js                 # 实际入口
├── main-*.js/ts            # ⚠️ 7 个多余入口文件
├── App.vue                 # 根组件
├── router/                 # 路由配置
├── stores/                 # Pinia 状态管理
├── api/                    # API 调用层
├── services/               # 前端服务
├── composables/            # 组合式函数
├── components/             # 组件
│   ├── Charts/             # ⚠️ 大写
│   ├── charts/             # ⚠️ 小写（与 Charts/ 冲突）
│   ├── Common/             # ⚠️ 大写
│   ├── common/             # ⚠️ 小写
│   ├── Market/             # ⚠️ 大写
│   ├── market/             # ⚠️ 小写
│   ├── artdeco/            # ArtDeco 设计系统组件
│   └── [其他 11 个目录]
├── views/                  # 页面
│   ├── artdeco-pages/      # ⚠️ 143 个文件（含 backup 和空目录）
│   ├── converted.archive/  # ⚠️ 归档旧页面（在源码树中）
│   ├── demo/               # ⚠️ 33 个 demo 文件
│   ├── composables/        # ⚠️ 应在 src/composables/ 下
│   └── [其他 20+ 目录]
├── types/                  # TypeScript 类型定义
├── utils/                  # 工具函数
├── layouts/                # 布局组件
└── styles/                 # 全局样式
```
