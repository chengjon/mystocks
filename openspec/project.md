# Project Context

## Purpose
MyStocks_spec 是一套面向量化交易的全栈数据管理系统，核心目标是：
1. 整合多源市场数据（股票/ETF/行业资金流向等），提供实时监控、技术分析、风险评估能力；
2. 基于双数据库架构（TDengine+PostgreSQL）实现高频时序数据与结构化数据的高效存储/查询；
3. 支撑量化策略回测、实时交易风控、多维度数据可视化（60+前端页面）；
4. Phase 5+ 核心目标：完成E2E测试覆盖、容器化/K8s部署、性能优化（API响应≤300ms）、生产级监控，最终达到99.9%服务可用性。

## Tech Stack
### 核心技术栈
- 后端：Python 3.11+、FastAPI（异步API）、Pydantic（类型校验）
- 前端：Vue、ECharts（可视化）、WebSocket（实时数据推送）
- 数据库：TDengine 3.0+（高频时序数据）、PostgreSQL 15+（TimescaleDB扩展，日线/结构化数据）
- 缓存：Redis 7.0+（API缓存、会话管理）
- 部署/运维：pm2（进程守护）、tmux（多窗管理），Docker（不支持）、K8s（不支持）
- 测试：pytest（单元/集成测试）、Playwright（E2E测试）、Chrome DevTools（性能分析）
- 监控/日志：Prometheus + Grafana（监控）、lnav（日志聚合）
- 协作工具：Claude Code多Agent（代码分析/优化/部署配置）、Git（版本控制），MCP，Hooks

### 辅助工具链
- 数据适配：7个数据源适配器（支持故障自动转移）
- 格式处理：Black（代码格式化）、vulture（死代码检测）、jscpd（重复代码检测）
- 调度：CI/CD（GitLab/GitHub Actions）

## Project Conventions

### Code Style
1. 通用规则
   - Python代码：严格遵循Black格式化（line-length=88），全量添加类型注解（无裸函数/变量）；
   - 命名规范：
     - 后端：函数/方法用snake_case，类用PascalCase，常量用UPPER_SNAKE_CASE，API路径用kebab-case（如`/api/market-data/stock`）；
     - 前端（Vue）：组件变量用camelCase（如`stockChart`），页面函数用snake_case（如`render_fund_flow`）；
     - 数据库：表名用snake_case+模块前缀（如`market_daily_kline`），TDengine超表用`ts_`前缀（如`ts_tick_data`）。
2. 代码结构
   - 后端：按“模块（API）→ 服务 → 数据层”分层（如`app/api/market_v2/ → app/services/market/ → app/db/tdengine/`）；
   - 前端：按“页面 → 组件 → 工具函数”组织（如`ui/pages/fund_flow/ → ui/components/chart/ → ui/utils/`）；
   - 测试代码：与业务代码目录结构镜像（如`tests/api/market_v2/`对应`app/api/market_v2/`）。
3. 注释规范
   - 所有函数/类必须添加docstring（Google风格），包含“功能、参数、返回值、异常场景”；
   - 核心业务逻辑（如风控规则、数据适配）添加行内注释；
   - 配置文件（K8s/Docker）添加关键参数说明（如资源限制、健康检查规则）。

### Architecture Patterns
1. 核心架构
   - 后端：分层架构（API层→服务层→数据层）+ 依赖注入（避免硬编码依赖）；
   - 数据库：双库专库专用（TDengine存Tick/分钟级数据，PostgreSQL存日线/元数据），数据同步通过定时任务实现；
   - 前端：组件化+单向数据流（事件驱动，避免全局状态混乱）。
2. 关键模式
   - 数据源适配：适配器模式（统一多数据源接口，支持故障转移）；
   - API设计：RESTful + WebSocket（实时数据），所有API返回标准化格式（`{code: int, data: any, msg: string}`）；
   - 缓存策略：多级缓存（Redis→应用内存→数据库），高频API（如`/api/market/tick`）缓存TTL=5分钟；
   - 部署模式：K8s最小化部署（Deployment+Service+ConfigMap/Secret），无状态服务（API/前端）多实例部署，有状态服务（数据库）单实例+持久化存储。

### Testing Strategy
1. 测试分层
   - 单元测试：覆盖核心函数/方法（如数据处理、风控规则），100% Mock外部依赖（无真实数据源调用）；
   - 集成测试：覆盖API全链路（请求→处理→数据库→响应），使用测试数据库；
   - E2E测试（Phase 5核心）：基于Playwright覆盖15+核心业务场景（选股→分析→风控→可视化），验证“页面交互→API调用→数据渲染”全流程；
   - 性能测试：API压测（50+并发）、数据库查询测试（验证TDengine压缩比/写入性能）、前端加载测试（核心页面≤3s）。
2. 测试规范
   - 所有测试必须包含正常场景+边界场景（如空数据、网络超时、权限不足）；
   - 测试代码必须通过Black格式化+类型注解检查；
   - 测试通过率要求：单元测试≥95%，E2E测试≥95%，性能测试需满足预设基准（API P95响应≤300ms）。
3. 自动化执行
   - 本地：tmux分窗执行测试+监控日志（`pytest` + `lnav`）；
   - CI/CD：代码提交后自动执行单元测试+冒烟测试，合并主分支前执行全量E2E测试；
   - 失败处理：测试失败自动触发root-cause-debugger Agent分析原因，输出修复建议。

### Git Workflow
1. 分支策略
   - 主分支：`main`（生产环境）、`develop`（开发环境）；
   - 功能分支：`feature/phase5-e2e-test`（Phase 5 E2E测试）、`feature/phase6-cache-optimize`（Phase 6缓存优化）；
   - 修复分支：`hotfix/prod-api-500`（生产API 500修复）。
2. 提交规范
   - 提交信息格式：`[类型][模块]: 描述`（如`feat[market-api]: 新增资金流向接口`、`fix[tdengine]: 修复Tick数据写入失败`、`refactor[code-cleanup]: 删除冗余工具函数`）；
   - 类型枚举：feat（功能）、fix（修复）、refactor（重构）、test（测试）、docs（文档）、deploy（部署）；
   - 每次提交仅修改单一功能/问题，避免大杂烩提交。
3. 协作规则
   - 功能分支需通过Code Review（code-reviewer Agent审核）+ 测试通过后，方可合并到`develop`；
   - `develop`分支合并到`main`前，需执行全量测试+生产环境预部署验证；
   - 所有Agent生成的代码修改（如K8s配置、性能优化代码）需单独提交，标注Agent来源（如`feat[k8s][web-fullstack-architect]: 生成最小化部署配置`）。

## Domain Context
1. 核心业务概念
   - 量化交易：基于历史数据/技术指标构建策略，回测后执行实时交易；
   - 资金流向：市场/个股/行业的资金流入/流出数据（分钟级/日线级）；
   - 龙虎榜：交易所公布的机构/游资交易数据（核心分析维度）；
   - 风控规则：包含仓位限制、止损阈值、融资融券额度管控等核心逻辑；
   - 时序数据：Tick数据（逐笔成交）、分钟级/K线数据（聚合成交），TDengine按股票代码+时间分区存储。
2. 关键业务规则
   - 数据更新频率：Tick数据实时推送（WebSocket），日线数据每日收盘后更新；
   - 风控阈值：单股票仓位≤10%，单日最大亏损≤5%，触发后自动平仓；
   - 数据源优先级：优先使用官方数据源，失败后自动切换到备用数据源（7个数据源轮询）；
   - 缓存失效规则：市场闭市后清空当日缓存，开市前预加载热门股票数据。
3. 生产环境约束
   - 服务器资源：8核16G（K8s节点），TDengine分配4G内存，PostgreSQL分配2G内存；
   - 可用性要求：99.9%（每月故障时间≤43分钟）；
   - 数据保留：Tick数据保留3个月，分钟级数据保留1年，日线数据永久保留；
   - 安全要求：JWT Token有效期2小时，数据库密码存储在K8s Secret，API接口需鉴权（除公开行情接口）。
