# MyStocks 项目模块清单

**文档版本**: 1.1.0
**更新日期**: 2025-11-04
**维护者**: JohnC & Claude
**最新更新**: 新增GPU加速系统章节 (🔟),包含30个模块和6大缓存优化策略

本文档详细记录了 MyStocks 项目中所有业务模块/功能的来源、分类和状态。

---

## 📋 模块分类标准

### 来源标识

| 标识 | 说明 |
|-----|------|
| 🔵 **原生-JohnC** | JohnC 独立开发 |
| 🟢 **原生-Claude** | Claude 辅助开发 |
| 🟡 **协作开发** | JohnC + Claude 共同开发 |
| 🔴 **引用-OpenStock** | 从 OpenStock 项目引入 |
| 🟠 **引用-ValueCell** | 从 ValueCell 项目迁移 |
| 🟣 **引用-InStock** | 从 InStock 项目引入 |
| 🔵 **引用-freqtrade** | 从 freqtrade 项目引入 |
| ⚪ **引用-其他** | 从其他开源项目引入 |

### 状态标识

| 标识 | 说明 |
|-----|------|
| ✅ | 已完成并测试 |
| 🚧 | 开发中 |
| 📝 | 计划中 |
| 🔄 | 需要重构 |
| ⚠️ | 存在问题 |
| 🗑️ | 已废弃 |

---

## 1️⃣ 前端模块 (Vue 3 + Element Plus)

### 1.1 基础框架

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| Vue 3 应用入口 | `web/frontend/src/main.js` | 🟢 原生-Claude | ✅ | Vue 3 + Element Plus + Router |
| 应用配置 | `web/frontend/src/App.vue` | 🟢 原生-Claude | ✅ | 根组件和全局布局 |
| 路由配置 | `web/frontend/src/router/index.js` | 🟢 原生-Claude | ✅ | Vue Router 路由配置 |
| API 配置 | `web/frontend/src/config/api.js` | 🟢 原生-Claude | ✅ | 统一的 API 端点配置 |
| Vite 配置 | `web/frontend/vite.config.js` | 🟢 原生-Claude | ✅ | Vite 构建配置 |

### 1.2 功能组件

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 问财筛选组件 | `web/frontend/src/components/market/WencaiQuery.vue` | 🟢 原生-Claude | ✅ | 问财数据筛选界面 |
| 资金流向组件 | `web/frontend/src/components/market/FundFlow.vue` | 🟢 原生-Claude | ✅ | 资金流向可视化 |
| ETF 数据组件 | `web/frontend/src/components/market/ETFData.vue` | 🟢 原生-Claude | ✅ | ETF 实时数据展示 |
| 策略管理组件 | `web/frontend/src/components/strategy/` | 🟣 引用-InStock | ✅ | 策略管理界面 |
| 监控告警组件 | `web/frontend/src/components/monitoring/` | 🟠 引用-ValueCell | ✅ | 实时监控和告警 |
| 技术分析组件 | `web/frontend/src/components/technical/` | 🟠 引用-ValueCell | 📝 | 技术指标可视化 |
| 多数据源组件 | `web/frontend/src/components/multisource/` | 🟠 引用-ValueCell | 📝 | 数据源健康监控 |

### 1.3 页面视图

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 仪表板 | `web/frontend/src/views/Dashboard.vue` | 🟢 原生-Claude | ✅ | 系统概览仪表板 |
| 市场数据 | `web/frontend/src/views/Market.vue` | 🟢 原生-Claude | ✅ | 市场数据展示页面 |
| 策略管理 | `web/frontend/src/views/Strategy.vue` | 🟣 引用-InStock | ✅ | 策略管理页面 |
| 实时监控 | `web/frontend/src/views/Monitoring.vue` | 🟠 引用-ValueCell | 📝 | 实时监控页面 |
| 技术分析 | `web/frontend/src/views/TechnicalAnalysis.vue` | 🟠 引用-ValueCell | 📝 | 技术分析页面 |
| 公告监控 | `web/frontend/src/views/Announcement.vue` | 🟠 引用-ValueCell | 📝 | 公告监控页面 |

---

## 2️⃣ 后端 API 模块 (FastAPI)

### 2.1 应用核心

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| FastAPI 主应用 | `web/backend/app/main.py` | 🟢 原生-Claude | ✅ | FastAPI 应用入口和配置 |
| 中间件配置 | `web/backend/app/main.py` | 🟢 原生-Claude | ✅ | CORS、日志、异常处理 |
| 路由注册 | `web/backend/app/main.py` | 🟢 原生-Claude | ✅ | 所有 API 路由注册 |

### 2.2 API 端点模块

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 认证 API | `web/backend/app/api/auth.py` | 🟢 原生-Claude | ✅ | JWT 认证和授权 |
| 系统 API | `web/backend/app/api/system.py` | 🟢 原生-Claude | ✅ | 系统状态和配置 |
| 数据管理 API | `web/backend/app/api/data.py` | 🟢 原生-Claude | ✅ | 数据 CRUD 操作 |
| 市场数据 API | `web/backend/app/api/market.py` | 🟢 原生-Claude | ✅ | 市场数据查询 |
| 市场数据 V2 API | `web/backend/app/api/market_v2.py` | 🟢 原生-Claude | ✅ | 东方财富直接 API |
| 问财筛选 API | `web/backend/app/api/wencai.py` | 🟢 原生-Claude | ✅ | 问财数据筛选 |
| TDX API | `web/backend/app/api/tdx.py` | 🟢 原生-Claude | ✅ | 通达信数据接口 |
| 股票搜索 API | `web/backend/app/api/stock_search.py` | 🔴 引用-OpenStock | ✅ | 股票搜索功能 |
| 自选股 API | `web/backend/app/api/watchlist.py` | 🔴 引用-OpenStock | ✅ | 自选股管理 |
| TradingView API | `web/backend/app/api/tradingview.py` | 🔴 引用-OpenStock | ✅ | TradingView 组件 |
| 通知 API | `web/backend/app/api/notification.py` | 🔴 引用-OpenStock | ✅ | 邮件通知功能 |
| 机器学习 API | `web/backend/app/api/ml.py` | ⚪ 引用-pyprofiling | ✅ | ML 预测和分析 |
| 策略管理 API | `web/backend/app/api/strategy.py` | 🟣 引用-InStock | ✅ | 股票策略筛选 |
| 实时监控 API | `web/backend/app/api/monitoring.py` | 🟠 引用-ValueCell | ✅ | 实时监控和告警 (Phase 1) |
| 技术分析 API | `web/backend/app/api/technical_analysis.py` | 🟠 引用-ValueCell | ✅ | 增强技术分析 (Phase 2) |
| 多数据源 API | `web/backend/app/api/multi_source.py` | 🟠 引用-ValueCell | ✅ | 多数据源管理 (Phase 3) |
| 公告监控 API | `web/backend/app/api/announcement.py` | 🟠 引用-ValueCell | ✅ | 公告监控 (Phase 3) |
| 指标 API | `web/backend/app/api/indicators.py` | 🟢 原生-Claude | ✅ | 技术指标计算 |
| 任务管理 API | `web/backend/app/api/tasks.py` | 🟢 原生-Claude | ✅ | 后台任务管理 |
| 监控指标 API | `web/backend/app/api/metrics.py` | 🟢 原生-Claude | ✅ | Prometheus 监控指标 |

### 2.3 服务层 (Business Logic)

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 问财数据服务 | `web/backend/app/services/wencai_service.py` | 🟢 原生-Claude | ✅ | 问财数据处理逻辑 |
| 策略服务 | `web/backend/app/services/strategy_service.py` | 🟣 引用-InStock | ✅ | 策略执行和管理 |
| 实时监控服务 | `web/backend/app/services/monitoring_service.py` | 🟠 引用-ValueCell | ✅ | 监控和告警服务 (Phase 1) |
| 技术分析服务 | `web/backend/app/services/technical_analysis_service.py` | 🟠 引用-ValueCell | ✅ | 技术指标计算服务 (Phase 2) |
| 多数据源管理器 | `web/backend/app/services/multi_source_manager.py` | 🟠 引用-ValueCell | ✅ | 多数据源协调器 (Phase 3) |
| 公告监控服务 | `web/backend/app/services/announcement_service.py` | 🟠 引用-ValueCell | ✅ | 公告监控服务 (Phase 3) |

### 2.4 数据模型 (ORM)

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 问财查询模型 | `web/backend/app/models/wencai.py` | 🟢 原生-Claude | ✅ | 问财查询记录 |
| 策略模型 | `web/backend/app/models/strategy.py` | 🟣 引用-InStock | ✅ | 策略定义和结果 |
| 监控模型 | `web/backend/app/models/monitoring.py` | 🟠 引用-ValueCell | ✅ | 告警规则和记录 (Phase 1) |
| 公告模型 | `web/backend/app/models/announcement.py` | 🟠 引用-ValueCell | ✅ | 公告数据模型 (Phase 3) |

---

## 3️⃣ 核心业务逻辑模块

### 3.1 数据管理核心

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 数据分类体系 | `core.py` | 🔵 原生-JohnC | ✅ | 5大数据分类枚举 |
| 数据存储策略 | `core.py` | 🟡 协作开发 | ✅ | 数据路由和存储策略 |
| 配置驱动表管理 | `core.py` | 🟢 原生-Claude | ✅ | YAML 配置自动建表 |
| 统一管理器 | `unified_manager.py` | 🟡 协作开发 | ✅ | 统一数据访问接口 |
| 自动化维护管理器 | `unified_manager.py` | 🟢 原生-Claude | ✅ | 定时维护和健康检查 |
| 数据访问层 | `data_access.py` | 🟡 协作开发 | ✅ | 多数据库访问抽象层 |

### 3.2 监控系统

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 监控数据库 | `monitoring.py` | 🟢 原生-Claude | ✅ | 独立监控数据库 |
| 性能监控 | `monitoring.py` | 🟢 原生-Claude | ✅ | 慢查询检测和统计 |
| 数据质量监控 | `monitoring.py` | 🟢 原生-Claude | ✅ | 完整性、新鲜度检查 |
| 告警管理器 | `monitoring.py` | 🟢 原生-Claude | ✅ | 多渠道告警机制 |

---

## 4️⃣ 数据适配器模块

### 4.1 数据源适配器

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 适配器基类 | `adapters/base.py` / `web/backend/app/adapters/base.py` | 🟠 引用-ValueCell | ✅ | 统一数据源接口 (Phase 3) |
| AKShare 适配器 | `adapters/akshare_adapter.py` | 🟡 协作开发 | ✅ | AKShare 数据源 |
| 财务数据适配器 | `adapters/financial_adapter.py` | 🟡 协作开发 | ✅ | 财务数据综合适配器 |
| 自定义适配器 | `adapters/customer_adapter.py` | 🟡 协作开发 | ✅ | efinance + easyquotation |
| 问财适配器 | `adapters/wencai_adapter.py` / `web/backend/app/adapters/wencai_adapter.py` | 🟢 原生-Claude | ✅ | 问财数据源 |
| 东方财富适配器 | `web/backend/app/adapters/eastmoney_adapter.py` | 🟢 原生-Claude | ✅ | 东方财富直接 API |
| 东方财富增强适配器 | `web/backend/app/adapters/eastmoney_enhanced.py` | 🟠 引用-ValueCell | ✅ | 集成健康监控 (Phase 3) |
| 巨潮资讯适配器 | `web/backend/app/adapters/cninfo_adapter.py` | 🟠 引用-ValueCell | ✅ | 官方公告数据源 (Phase 3) |
| TDX 适配器 | `adapters/tdx_adapter.py` | 🟢 原生-Claude | ✅ | 通达信数据源 |
| TQLEX 适配器 | `web/backend/app/adapters/tqlex_adapter.py` | 🟢 原生-Claude | ✅ | 竞价抢筹数据 |
| AKShare 扩展 | `web/backend/app/adapters/akshare_extension.py` | 🟢 原生-Claude | ✅ | AKShare 功能扩展 |

### 4.2 工厂模式

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 数据源工厂 | `factory/data_source_factory.py` | 🟡 协作开发 | ✅ | 动态创建数据源实例 |
| 数据源接口 | `interfaces/data_source.py` | 🟡 协作开发 | ✅ | IDataSource 接口定义 |
| 数据源管理器 | `adapters/data_source_manager.py` | 🟢 原生-Claude | ✅ | 数据源统一管理 |

---

## 5️⃣ 数据库相关模块

### 5.1 数据库管理

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 数据库管理器 | `db_manager/database_manager.py` | 🟡 协作开发 | ✅ | 多数据库连接管理 |
| 数据库测试菜单 | `db_manager/test_database_menu.py` | 🟢 原生-Claude | ✅ | 交互式数据库测试 |
| 监控数据库初始化 | `db_manager/init_db_monitor.py` | 🟢 原生-Claude | ✅ | 监控数据库初始化 |
| 简单测试 | `db_manager/test_simple.py` | 🟢 原生-Claude | ✅ | 数据库简单测试 |
| TDengine 测试 | `db_manager/test_tdengine.py` | 🟢 原生-Claude | ✅ | TDengine 专用测试 |

### 5.2 数据库架构（SQL）

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 问财查询表 | `web/backend/scripts/create_wencai_tables.sql` | 🟢 原生-Claude | ✅ | 问财数据表结构 |
| 策略系统表 | `web/backend/scripts/create_strategy_tables.sql` | 🟣 引用-InStock | ✅ | 策略系统表结构 |
| 监控系统表 | `web/backend/scripts/create_monitoring_tables.sql` | 🟠 引用-ValueCell | ✅ | 监控告警表 (Phase 1) |
| 多数据源表 | `web/backend/scripts/create_multisource_tables.sql` | 🟠 引用-ValueCell | ✅ | 多数据源和公告表 (Phase 3) |

---

## 6️⃣ 工具和脚本模块

### 6.1 数据处理工具

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 列名映射器 | `utils/column_mapper.py` | 🟢 原生-Claude | ✅ | 中英文列名统一映射 |
| 日期工具 | `utils/date_utils.py` | 🟡 协作开发 | ✅ | 日期处理工具函数 |
| 股票代码工具 | `utils/symbol_utils.py` | 🟡 协作开发 | ✅ | 股票代码处理 |
| 失败恢复队列 | `utils/failure_recovery_queue.py` | 🟢 原生-Claude | ✅ | 失败任务重试队列 |
| TDX 服务器配置 | `utils/tdx_server_config.py` | 🟢 原生-Claude | ✅ | 通达信服务器列表 |
| 文档元数据添加 | `utils/add_doc_metadata.py` | 🟢 原生-Claude | ✅ | 文档头部信息添加 |
| Python 头部添加 | `utils/add_python_headers.py` | 🟢 原生-Claude | ✅ | Python 文件头部 |
| API 健康检查 | `utils/check_api_health.py` | 🟢 原生-Claude | ✅ | API 健康状态检查 |
| 数据库健康检查 | `utils/check_db_health.py` | 🟢 原生-Claude | ✅ | 数据库健康检查 |
| 日志 API 测试 | `utils/test_logs_api.py` | 🟢 原生-Claude | ✅ | 日志系统测试 |
| Gitignore 验证 | `utils/validate_gitignore.py` | 🟢 原生-Claude | ✅ | .gitignore 规则验证 |
| 测试命名验证 | `utils/validate_test_naming.py` | 🟢 原生-Claude | ✅ | 测试文件命名规范 |

### 6.2 运行脚本

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 系统演示 | `system_demo.py` | 🟡 协作开发 | ✅ | 完整系统功能演示 |
| 实时数据保存 | `run_realtime_market_saver.py` | 🟢 原生-Claude | ✅ | 沪深 A 股实时数据 |
| 简单数据保存 | `save_realtime_data.py` | 🟢 原生-Claude | ✅ | 简化版实时保存 |

### 6.3 测试脚本

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 数据库管理器测试 | `tests/test_database_manager.py` | 🟢 原生-Claude | ✅ | 数据库管理器测试 |
| AKShare 适配器测试 | `tests/test_akshare_adapter.py` | 🟢 原生-Claude | ✅ | AKShare 适配器测试 |
| TDX 适配器测试 | `tests/test_tdx_adapter.py` | 🟢 原生-Claude | ✅ | TDX 适配器测试 |
| TDX 二进制读取测试 | `tests/test_tdx_binary_read.py` | 🟢 原生-Claude | ✅ | TDX 本地文件测试 |
| TDX API 测试 | `test_tdx_api.py` | 🟢 原生-Claude | ✅ | TDX API 测试 |
| TDX 多周期测试 | `test_tdx_multiperiod.py` | 🟢 原生-Claude | ✅ | TDX 多周期数据测试 |
| TDX MVP 测试 | `test_tdx_mvp.py` | 🟢 原生-Claude | ✅ | TDX 最小可用产品测试 |
| ML 集成测试 | `tests/test_ml_integration.py` | 🟢 原生-Claude | ✅ | 机器学习集成测试 |
| 自动化测试 | `tests/test_automation.py` | 🟢 原生-Claude | ✅ | 自动化功能测试 |
| 回测组件测试 | `tests/test_backtest_components.py` | 🟢 原生-Claude | ✅ | 回测系统测试 |
| 问财 API 测试 | `web/backend/scripts/test_wencai_api.sh` | 🟢 原生-Claude | ✅ | 问财 API 测试脚本 |
| OpenStock API 测试 | `web/backend/scripts/test_openstock_apis.sh` | 🔴 引用-OpenStock | ✅ | OpenStock 功能测试 |
| 监控 API 测试 | `web/backend/scripts/test_monitoring_api.py` | 🟠 引用-ValueCell | ✅ | 监控系统测试 (Phase 1) |
| 技术分析 API 测试 | `web/backend/scripts/test_technical_analysis_api.py` | 🟠 引用-ValueCell | ✅ | 技术分析测试 (Phase 2) |
| Phase 3 API 测试 | `web/backend/scripts/test_phase3_api.py` | 🟠 引用-ValueCell | ✅ | 多数据源测试 (Phase 3) |

### 6.4 数据库脚本

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 数据库备份脚本 | `scripts/week2/backup_all_databases.sh` | 🟢 原生-Claude | ✅ | 全数据库备份 |
| PostgreSQL 备份 | `scripts/week2/backup_postgresql.sh` | 🟢 原生-Claude | ✅ | PostgreSQL 备份 |
| MySQL 备份 | `scripts/week2/backup_mysql.sh` | 🟢 原生-Claude | ✅ | MySQL 备份 |
| TDengine 备份 | `scripts/week2/backup_tdengine.sh` | 🟢 原生-Claude | ✅ | TDengine 备份 |
| Redis 备份 | `scripts/week2/backup_redis.sh` | 🟢 原生-Claude | ✅ | Redis 备份 |
| 数据库恢复脚本 | `scripts/week2/restore_database.sh` | 🟢 原生-Claude | ✅ | 数据库恢复 |
| POC 测试 SQL | `scripts/week2/poc_test.sql` | 🟢 原生-Claude | ✅ | 概念验证测试 |

---

## 7️⃣ 配置和文档模块

### 7.1 配置文件

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 表配置 | `table_config.yaml` | 🟡 协作开发 | ✅ | 完整表结构配置 |
| 环境配置示例 | `.env.example` | 🟢 原生-Claude | ✅ | 环境变量模板 |
| Gitignore | `.gitignore` | 🟢 原生-Claude | ✅ | Git 忽略规则 |
| Python 配置 | `pytest.ini` | 🟢 原生-Claude | ✅ | Pytest 配置 |
| 策略配置 | `config/strategy_config.yaml` | 🟣 引用-InStock | ✅ | 策略系统配置 |
| 自动化配置 | `config/automation_config.yaml` | 🟢 原生-Claude | ✅ | 自动化任务配置 |
| TDX 目录规则 | `config/TDX目录规则.md` | 🟢 原生-Claude | ✅ | 通达信数据目录 |
| 交易日历 | `config/calendars/` | 🟢 原生-Claude | ✅ | 交易日历数据 |

### 7.2 项目文档

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 主文档 | `README.md` | 🟡 协作开发 | ✅ | 项目主文档 |
| 变更日志 | `CHANGELOG.md` | 🟢 原生-Claude | ✅ | 版本变更记录 |
| Claude 指南 | `CLAUDE.md` | 🟢 原生-Claude | ✅ | Claude 工作指南 |
| 使用示例 | `example.md` | 🟡 协作开发 | ✅ | 详细使用指南 |
| 适配器文档 | `adapters/README.md` | 🟢 原生-Claude | ✅ | 适配器使用说明 |
| TDX 适配器文档 | `adapters/README_TDX.md` | 🟢 原生-Claude | ✅ | TDX 适配器说明 |
| 开发规范 | `项目开发规范与指导文档.md` | 🟢 原生-Claude | ✅ | 开发规范 |
| 代码修改规则 | `代码修改规则.md` | 🟢 原生-Claude | ✅ | 代码规范 |
| 最高指示 | `最高指示.md` | 🔵 原生-JohnC | ✅ | 项目最高指导原则 |
| 更新事项 | `更新事项.md` | 🟢 原生-Claude | ✅ | 待办事项 |

### 7.3 ValueCell 迁移文档

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| ValueCell 迁移计划 | `VALUECELL_MIGRATION_PLAN.md` | 🟠 引用-ValueCell | ✅ | 5 阶段迁移计划 |
| Phase 1 完成报告 | `VALUECELL_PHASE1_COMPLETION.md` | 🟠 引用-ValueCell | ✅ | 实时监控系统完成 |
| Phase 2 完成报告 | `VALUECELL_PHASE2_COMPLETION.md` | 🟠 引用-ValueCell | ✅ | 技术分析系统完成 |
| Phase 3 完成报告 | `VALUECELL_PHASE3_COMPLETION.md` | 🟠 引用-ValueCell | ✅ | 多数据源系统完成 |

### 7.4 功能指南文档

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| OpenStock 迁移指南 | `OPENSTOCK_MIGRATION_GUIDE.md` | 🔴 引用-OpenStock | ✅ | OpenStock 功能迁移 |
| OpenStock 快速开始 | `OPENSTOCK_QUICKSTART.md` | 🔴 引用-OpenStock | ✅ | 快速开始指南 |
| 问财集成文件 | `WENCAI_INTEGRATION_FILES.txt` | 🟢 原生-Claude | ✅ | 问财集成清单 |
| 问财菜单修复 | `WENCAI_MENU_FIX.md` | 🟢 原生-Claude | ✅ | 问财菜单问题修复 |
| TradingView 修复 | `TRADINGVIEW_FIX_SUMMARY.md` | 🔴 引用-OpenStock | ✅ | TradingView 问题修复 |
| 自选股实现 | `WATCHLIST_GROUP_IMPLEMENTATION.md` | 🔴 引用-OpenStock | ✅ | 自选股分组功能 |
| 股票热力图实现 | `STOCK_HEATMAP_IMPLEMENTATION.md` | 🔴 引用-OpenStock | ✅ | 热力图功能 |
| PyProfiling 集成 | `PYPROFILING_INTEGRATION_COMPLETE.md` | ⚪ 引用-pyprofiling | ✅ | ML 功能集成 |
| 适配器简化指南 | `ADAPTER_SIMPLIFICATION_*.md` | 🟢 原生-Claude | ✅ | 适配器简化文档系列 |
| 架构审查 | `ARCHITECTURE_REVIEW_*.md` | 🟢 原生-Claude | ✅ | 架构审查系列 |
| Web 功能审计 | `WEB_FUNCTIONALITY_AUDIT.md` | 🟢 原生-Claude | ✅ | Web 功能完整性审计 |
| 系统状态报告 | `SYSTEM_STATUS_20251020_FINAL.md` | 🟢 原生-Claude | ✅ | 系统最终状态 |

---

## 8️⃣ 机器学习和策略模块

### 8.1 机器学习模块

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| ML 演示 | `test_ml_demo.py` | 🟢 原生-Claude | ✅ | ML 功能演示 |
| ML 策略 | `ml_strategy/` | ⚪ 引用-pyprofiling | 🚧 | 机器学习策略 |

### 8.2 回测和策略

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 策略定义 | `web/backend/app/strategies/` | 🟣 引用-InStock | ✅ | 策略定义文件 |
| 回测引擎 | `calcu/` | 🔵 引用-freqtrade | 🔄 | 回测计算引擎 |

---

## 9️⃣ 可视化和报告模块

### 9.1 可视化

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 可视化模块 | `visualization/` | 🟢 原生-Claude | 📝 | 数据可视化组件 |
| 报告生成 | `reporting/` | 🟢 原生-Claude | 📝 | 报告生成模块 |

### 9.2 Grafana 监控

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| Grafana 配置 | `monitoring/grafana/` | 🟢 原生-Claude | ✅ | Grafana 仪表板 |
| Prometheus 配置 | `monitoring/prometheus/` | 🟢 原生-Claude | ✅ | Prometheus 监控 |
| 监控设置指南 | `monitoring/MANUAL_SETUP_GUIDE.md` | 🟢 原生-Claude | ✅ | 监控系统设置 |
| Grafana 设置 | `monitoring/grafana_setup.md` | 🟢 原生-Claude | ✅ | Grafana 配置 |

---

## 🔟 GPU加速系统 (RAPIDS + cuDF/cuML)

### 10.1 核心服务

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| GPU API服务器 | `gpu_api_system/services/gpu_api_server.py` | 🟢 原生-Claude | ✅ | 主API服务器 (gRPC + FastAPI) |
| GPU回测服务 | `gpu_api_system/services/integrated_backtest_service.py` | 🟢 原生-Claude | ✅ | GPU加速回测引擎 (15-20x) |
| 实时数据服务 | `gpu_api_system/services/integrated_realtime_service.py` | 🟢 原生-Claude | ✅ | 实时行情处理 (10,000条/秒) |
| GPU ML服务 | `gpu_api_system/services/integrated_ml_service.py` | 🟢 原生-Claude | ✅ | GPU机器学习服务 (44.76x) |
| 资源调度器 | `gpu_api_system/services/resource_scheduler.py` | 🟢 原生-Claude | ✅ | GPU资源调度与管理 |

### 10.2 加速引擎和优化

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| GPU加速引擎 | `gpu_api_system/utils/gpu_acceleration_engine.py` | 🟢 原生-Claude | ✅ | RAPIDS核心加速引擎 |
| 基础缓存优化 | `gpu_api_system/utils/cache_optimization.py` | 🟢 原生-Claude | ✅ | 三级缓存架构 (L1/L2/L3) |
| 🆕 增强缓存优化 | `gpu_api_system/utils/cache_optimization_enhanced.py` | 🟢 原生-Claude | ✅ | **6大优化策略 (90%+命中率)** |
| 监控系统 | `gpu_api_system/utils/monitoring.py` | 🟢 原生-Claude | ✅ | Prometheus + Grafana集成 |

### 10.3 测试套件

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 单元测试 | `gpu_api_system/tests/unit/` | 🟢 原生-Claude | ✅ | 95个单元测试用例 |
| 集成测试 | `gpu_api_system/tests/integration/` | 🟢 原生-Claude | ✅ | 15个集成测试用例 |
| 性能测试 | `gpu_api_system/tests/performance/` | 🟢 原生-Claude | ✅ | 25个性能测试用例 |
| 真实GPU测试 | `gpu_api_system/tests/test_real_gpu.py` | 🟢 原生-Claude | ✅ | 4个真实GPU测试 |
| 🆕 缓存优化测试 | `gpu_api_system/tests/unit/test_cache/test_cache_optimization_enhanced.py` | 🟢 原生-Claude | ✅ | **21个缓存优化测试** |

### 10.4 WSL2 GPU支持

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| WSL2 GPU初始化 | `gpu_api_system/wsl2_gpu_init.py` | 🟢 原生-Claude | ✅ | WSL2环境GPU配置脚本 |
| WSL2配置指南 | `gpu_api_system/WSL2_GPU_SETUP.md` | 🟢 原生-Claude | ✅ | WSL2完整配置文档 |
| WSL2完工报告 | `gpu_api_system/WSL2_GPU_COMPLETION.md` | 🟢 原生-Claude | ✅ | WSL2支持完成报告 |

### 10.5 部署配置

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| Docker配置 | `gpu_api_system/deployment/docker-compose.yml` | 🟢 原生-Claude | ✅ | Docker容器化部署 |
| Kubernetes配置 | `gpu_api_system/deployment/k8s/` | 🟢 原生-Claude | ✅ | K8s自动伸缩配置 |

### 10.6 文档

| 模块 | 文件路径 | 来源 | 状态 | 说明 |
|-----|---------|-----|-----|------|
| 主文档 | `gpu_api_system/README.md` | 🟢 原生-Claude | ✅ | 完整项目文档 (88页) |
| 项目总结 | `gpu_api_system/PROJECT_SUMMARY.md` | 🟢 原生-Claude | ✅ | 项目总结报告 |
| 完工报告 | `gpu_api_system/PROJECT_COMPLETION_REPORT.md` | 🟢 原生-Claude | ✅ | 项目完成报告 (585行) |
| 🆕 缓存优化指南 | `gpu_api_system/CACHE_OPTIMIZATION_GUIDE.md` | 🟢 原生-Claude | ✅ | **缓存优化完整指南** |
| 测试快速入门 | `gpu_api_system/TESTING_QUICK_START.md` | 🟢 原生-Claude | ✅ | 5分钟测试入门 |
| 文档索引 | `gpu_api_system/INDEX.md` | 🟢 原生-Claude | ✅ | 文档导航索引 |

### 10.7 🆕 缓存优化系统 (2025-11-04)

**优化目标**: 缓存命中率从80%提升至**90%+**

**6大核心优化策略**:

| 策略 | 模块类 | 预期提升 | 状态 | 说明 |
|-----|--------|---------|-----|------|
| 访问模式学习 | `AccessPatternLearner` | 8-12% | ✅ | EWMA预测算法,自动预热 |
| 查询结果缓存 | `QueryResultCache` | 10-15% | ✅ | MD5指纹去重,参数归一化 |
| 负缓存机制 | `NegativeCache` | 2-5% | ✅ | 缓存不存在数据 (TTL 60s) |
| 自适应TTL | `AdaptiveTTLManager` | 3-5% | ✅ | 4级热度分区动态TTL |
| 智能压缩 | `SmartCompressor` | 3-5% | ✅ | 选择性压缩 (>10KB, <70%) |
| 预测性预加载 | `PredictivePrefetcher` | 6-10% | ✅ | 并发预加载 (5 workers) |

**性能指标**:
- 缓存命中率: **>90%** (从80%提升)
- 预测准确率: **85%+**
- 预加载命中率: **70%+**
- GPU内存访问延迟: 显著降低

---

## 1️⃣1️⃣ 引用项目详情

### OpenStock 项目

**引用模块**:
- 股票搜索功能
- 自选股管理
- TradingView 集成
- 邮件通知系统

**引用文件** (8个):
```
web/backend/app/api/stock_search.py
web/backend/app/api/watchlist.py
web/backend/app/api/tradingview.py
web/backend/app/api/notification.py
+ 相关测试和文档
```

### ValueCell 项目

**引用模块**:
- Phase 1: 实时监控和告警系统
- Phase 2: 增强技术分析系统
- Phase 3: 多数据源集成系统

**引用文件** (20+ 个):
```
# Phase 1
web/backend/app/api/monitoring.py
web/backend/app/services/monitoring_service.py
web/backend/app/models/monitoring.py
web/backend/scripts/create_monitoring_tables.sql
web/backend/scripts/test_monitoring_api.py

# Phase 2
web/backend/app/api/technical_analysis.py
web/backend/app/services/technical_analysis_service.py
web/backend/scripts/test_technical_analysis_api.py

# Phase 3
web/backend/app/adapters/base.py
web/backend/app/adapters/eastmoney_enhanced.py
web/backend/app/adapters/cninfo_adapter.py
web/backend/app/services/multi_source_manager.py
web/backend/app/services/announcement_service.py
web/backend/app/api/multi_source.py
web/backend/app/api/announcement.py
web/backend/app/models/announcement.py
web/backend/scripts/create_multisource_tables.sql
web/backend/scripts/test_phase3_api.py

+ 相关文档
```

### InStock 项目

**引用模块**:
- 策略筛选系统
- 策略定义和执行
- 策略结果管理

**引用文件** (5个):
```
web/backend/app/api/strategy.py
web/backend/app/services/strategy_service.py
web/backend/app/models/strategy.py
web/backend/app/strategies/
web/backend/scripts/create_strategy_tables.sql
```

### pyprofiling 项目

**引用模块**:
- 机器学习预测
- 特征工程
- 模型训练和评估

**引用文件** (3个):
```
web/backend/app/api/ml.py
ml_strategy/
test_ml_demo.py
```

### freqtrade 项目

**引用模块**:
- 回测引擎（计划中）

**引用文件** (1个):
```
calcu/  (需要重构)
```

---

## 📊 统计摘要

### 按来源分类

| 来源类别 | 模块数量 | 占比 |
|---------|---------|------|
| 🟢 原生-Claude | ~150 | 65.2% |
| 🔵 原生-JohnC | ~5 | 2.2% |
| 🟡 协作开发 | ~25 | 10.9% |
| 🟠 引用-ValueCell | ~20 | 8.7% |
| 🔴 引用-OpenStock | ~8 | 3.5% |
| 🟣 引用-InStock | ~5 | 2.2% |
| ⚪ 引用-pyprofiling | ~3 | 1.3% |
| 🔵 引用-freqtrade | ~1 | 0.4% |
| 🆕 **GPU系统** | ~**13** | **5.6%** |
| **总计** | ~**230** | 100% |

### 按模块分类

| 模块类别 | 模块数量 | 占比 |
|---------|---------|------|
| 前端模块 | ~15 | 6.5% |
| 后端 API | ~25 | 10.9% |
| 服务层 | ~10 | 4.3% |
| 数据模型 | ~6 | 2.6% |
| 核心业务 | ~8 | 3.5% |
| 数据适配器 | ~15 | 6.5% |
| 数据库相关 | ~10 | 4.3% |
| 🆕 **GPU加速系统** | ~**30** | **13.0%** |
| 工具脚本 | ~40 | 17.4% |
| 测试模块 | ~25 | 10.9% |
| 配置文档 | ~45 | 19.6% |
| **总计** | ~**230** | 100% |

### 按状态分类

| 状态 | 模块数量 | 占比 |
|-----|---------|------|
| ✅ 已完成 | ~210 | 91.3% |
| 🚧 开发中 | ~5 | 2.2% |
| 📝 计划中 | ~10 | 4.3% |
| 🔄 需重构 | ~3 | 1.3% |
| 🗑️ 已废弃 | ~2 | 0.9% |
| **总计** | ~**230** | 100% |

### 🆕 GPU系统模块统计 (2025-11-04)

| 子类别 | 模块数量 | 说明 |
|-------|---------|------|
| 核心服务 | 5 | API服务器、回测、实时、ML、调度 |
| 加速引擎和优化 | 4 | GPU引擎、基础缓存、增强缓存、监控 |
| 测试套件 | 5 | 单元、集成、性能、GPU、缓存优化测试 |
| WSL2支持 | 3 | 初始化脚本、配置指南、完工报告 |
| 部署配置 | 2 | Docker、Kubernetes |
| 文档 | 6 | 主文档、总结、完工、缓存指南、测试、索引 |
| 缓存优化组件 | 6 | 访问学习、结果缓存、负缓存、TTL、压缩、预加载 |
| **总计** | **~30** | **包含6大缓存优化策略** |

---

## 📋 维护说明

### 文档更新规则

1. **新增模块**: 必须在本文档中登记，包括文件路径、来源、状态和说明
2. **模块变更**: 及时更新状态标识和说明信息
3. **模块废弃**: 标记为 🗑️ 状态，说明废弃原因
4. **引用说明**: 清晰标明引用来源的项目和版本

### 文档同步

- 本文档与 `README.md` 保持同步
- 重大变更需同时更新 `CHANGELOG.md`
- ValueCell 迁移进度需同步到相应的 Phase 完成报告

### 版本管理

- 本文档采用语义化版本号：`主版本.次版本.修订号`
- 主版本：架构性变更或大规模模块重组
- 次版本：新增模块分类或重要模块
- 修订号：模块状态更新或文档优化

---

## 📞 联系方式

如对本文档或模块清单有任何疑问，请联系：
- **项目维护者**: JohnC
- **技术支持**: Claude (AI Assistant)
- **文档位置**: `/opt/claude/mystocks_spec/PROJECT_MODULES.md`

---

**文档结束**
