# MyStocks 前端主线测试总体方案

> 日期：2026-04-02
> 范围：前端 Web 主链页面验证与修复总纲
> 适用仓库：`/opt/claude/mystocks_spec`
> Graphiti 记忆组：`mystocks_spec`

## 1. 背景

本轮测试与修复不再沿用“自后向前”的方式，不再先从后端实现倒推前端页面，而是改为“自前向后”：

1. 先确认前端页面是否真实存在、是否能跑起来、是否具备功能树中声明的能力。
2. 将 `Mock` 与 `Real` 数据模式彻底分开，分别回答两个问题：
   - `Mock`：前端功能是否已经实现。
   - `Real`：前后端链路是否真正打通。
3. 按页面主线逐批推进，逐页测试、逐页修复、逐页留痕。

本方案的目标，是为后续所有前端测试、修复、验收提供统一主线，避免再次因入口混乱、配置漂移或后端未运行而隐藏问题。

## 2. 当前基线

### 2.1 真值来源

- 业务能力归属真值：`docs/FUNCTION_TREE.md`
- 页面入口真值：`web/frontend/src/router/index.ts`
- 前端主链页面清单：`docs/plans/frontend-page-optimization-list.md`

### 2.2 当前已确认事实

- 功能树共有 `10` 个业务域：
  - 市场数据与行情
  - 技术分析与指标
  - 策略管理与回测
  - 风险管理与监控
  - 投资组合与交易
  - 监控与告警
  - 高级分析与 AI
  - 系统管理与配置
  - 数据存储与管理
  - 公告与信息
- 前端主链页面按当前口径为 `34` 页。
- 当前命名路由总数为 `37`，其中主链外页面为：
  - `/detail/graphics/:symbol`
  - `/detail/news/:symbol`
  - `/:pathMatch(.*)*`

### 2.3 当前主要问题

1. 真值源分裂
   - `router/index.ts` 才是页面入口真值。
   - `pageConfig.ts` 仍包含旧 API 口径与旧映射。
   - `menu.config.js` 仍包含旧路径与旧菜单投影。
   - 结论：`pageConfig.ts` 与 `menu.config.js` 只能作为被验证对象，不能反向指导测试。

2. 运行态不健康
   - 前端 `http://localhost:3020` 可访问。
   - 后端 `http://localhost:8020` 当前不可达。
   - PM2 中前端在线，后端处于 `waiting`。

3. 测试资产过多且新旧混杂
   - 仓库中存在大量旧 E2E、旧页面、旧路由口径。
   - 如不先冻结主线，会继续出现“页面没问题但测试打错入口”或“接口已变但配置仍旧”的噪音。

### 2.4 当前已有可利用机制

- App 壳层已有后端就绪检测与 Mock fallback 机制。
- Mock 与 Real 环境文件已经存在：
  - `web/frontend/.env.mock`
  - `web/frontend/.env.real`
- 前端已有分层测试脚本，包括：
  - `npm run test:e2e:business-smoke`
  - `npm run test:e2e:stable`
  - `npm run test:e2e:axe`
  - `bash scripts/run_e2e_pm2.sh`

## 3. 总体目标

本方案的交付目标不是“跑完一些测试”，而是建立一条稳定、可复用、可审计的前端主线验证体系。

需要最终回答的核心问题只有四个：

1. 功能树中的页面是否真的存在并可访问？
2. 页面是否在 `Mock` 条件下完整表达了预期功能？
3. 页面是否在 `Real` 条件下能够消费真实接口并稳定渲染？
4. 页面涉及写操作时，是否能完成最小闭环或正确降级？

## 4. 基本原则

### 4.1 真值统一

- 页面路径、鉴权、组件挂载，以 `router` 为唯一真值。
- 业务域归属、能力边界，以 `FUNCTION_TREE` 为唯一真值。
- `pageConfig.ts`、`menu.config.js`、旧测试脚本，只能被验证，不能充当主线事实。

### 4.2 Mock / Real 分离

- `Mock` 模式只验证前端功能表达能力，不代表真实业务链路通过。
- `Real` 模式只验证真实接口联通、数据映射与行为闭环，不代表前端设计质量天然过关。
- 所有报告必须将 `Mock` 与 `Real` 分开。
- 禁止使用一个 `PASS` 混淆两种结果。

### 4.3 前端优先

- 优先让页面跑起来，再判断后端链路问题。
- 不允许因“后端未启动”而跳过前端功能是否存在的核验。
- 不允许继续依赖从后端代码静态阅读去猜页面是否实现。

### 4.4 逐页留痕

- 每个页面都必须产出独立结论。
- 每个结论都必须落到明确分类，而不是笼统写“有问题”。

## 5. 页面统一测试模型

每个页面固定按 4 层执行，不允许跳层：

### 5.1 `route-shell`

验证页面是否作为页面存在：

- 路由是否可达
- 页面是否挂载成功
- 是否出现白屏
- 是否存在致命 console/runtime error
- 登录与鉴权跳转是否符合预期

### 5.2 `mock-render`

验证页面在 Mock 模式下是否具备功能表达能力：

- 核心布局存在
- 关键 DOM 可见
- 空态/错态存在
- 主表格/主卡片/主图表能渲染
- 关键按钮、筛选器、交互入口存在

这一层用于回答：

`这个页面前端到底做没做出来？`

### 5.3 `real-read`

验证页面在真实接口下是否能读通：

- 主接口族可达
- 返回结构可被页面消费
- 空数据不崩溃
- 字段差异不导致页面失效
- 错误提示和 Request ID 能显化

这一层用于回答：

`这个页面前后端读链到底有没有打通？`

### 5.4 `real-write/degrade`

对存在写操作的页面，验证最小可闭环行为：

- 新增
- 编辑
- 删除
- 启停
- 提交回测
- 批量更新

若真实写链暂时不闭环，则至少验证：

- 按钮禁用逻辑是否正确
- 错误提示是否清晰
- 降级或回退是否明确可见
- 不允许静默失败

## 6. 缺陷分类规范

所有问题统一归入以下三类：

### 6.1 `route/config drift`

适用于：

- 路由路径与菜单配置不一致
- `pageConfig.ts` 中 API 口径落后
- 旧别名、旧路径、旧菜单投影仍被引用
- 测试脚本打到旧页面入口

### 6.2 `frontend render gap`

适用于：

- 页面结构缺失
- 关键组件未实现
- DOM 不可见
- 渲染报错
- 空态、错态缺失
- Mock 下仍无法表达该页面功能

### 6.3 `backend contract/runtime gap`

适用于：

- 真实接口不可达
- 接口契约与页面消费结构不一致
- 后端健康检查失败
- 写链不可闭环
- 数据字段变更导致页面真实模式失效

## 7. 分阶段推进

整体按 `34` 页主链推进，固定 4 个批次。

### 7.1 Phase 0：基线冻结

目标：

- 冻结 34 页主链清单
- 把旧测试与旧页面从主门禁剥离
- 确认后续所有页面均以 `router + FUNCTION_TREE + 主链清单` 为准

主要动作：

- 清点旧路由/旧入口测试
- 标记 `navigation-debt` 与 `config-debt`
- 建立主线页面矩阵

### 7.2 Phase 1：启动链与市场域首批验证

页面：

- Login
- Dashboard
- Market-Realtime
- Market-Technical
- Market-LHB
- Data-Industry

目标：

- 先确认系统壳层、登录页、市场主链是否真实存在并可运行
- 优先暴露白屏、路由漂移、接口口径错误、页面骨架缺失

### 7.3 Phase 2：数据分析与自选管理

页面：

- Data-Concept
- Data-FundFlow
- Data-Indicator
- Watchlist-Manage
- Watchlist-Signals
- Watchlist-Screener

目标：

- 验证分析页与自选管理页在 Mock / Real 双轨下是否能完成读链与基本交互

### 7.4 Phase 3：策略与交易主链

页面：

- Strategy-Repo
- Strategy-Parameters
- Strategy-Signals
- Strategy-Backtest
- Strategy-GPU
- Strategy-Opt
- Strategy-Pos
- Trade-Positions
- Trade-Terminal
- Trade-Signals
- Trade-Portfolio
- Trade-History

目标：

- 验证高价值读写链
- 重点检查写操作闭环、回测、交易终端与组合透视

### 7.5 Phase 4：风险与系统域

页面：

- Risk-Management
- Risk-Overview
- Risk-PnL
- Risk-StopLoss
- Risk-Alerts
- Risk-News
- System-Config
- System-Health
- System-API
- System-Data

目标：

- 验证监控、告警、健康矩阵、配置管理等系统页
- 收口系统级读链、导出链和批量写链

## 8. 运行与验收门禁

### 8.1 强制门禁

每批结束时，必须至少报告：

- 结构性语法错误是否为 `0`
- 类型错误是否高于基线
- PM2 服务状态：
  - `mystocks-backend`
  - `mystocks-frontend`
- 访问地址：
  - `http://localhost:8020`
  - `http://localhost:3020`
- E2E 实际执行情况：
  - 执行命令
  - 浏览器项目
  - 通过数
  - 失败数
  - 跳过数

### 8.2 当前类型基线

当前前端类型错误基线来自：

`reports/analysis/tech-debt-baseline.json`

现有基线为：

- `frontend_type_errors = 0`

因此，任何新增类型错误都视为回归。

### 8.3 推荐执行层级

#### 层级 A：本地页面扫描

- `npm run dev:mock`
- `npm run dev:real`

#### 层级 B：前端业务冒烟

- `npm run test:e2e:business-smoke`
- `npm run test:e2e:stable`

#### 层级 C：无障碍与视觉补充

- `npm run test:e2e:axe`
- `npm run test:visual`

#### 层级 D：PM2 环境门禁

- `bash scripts/run_e2e_pm2.sh`

## 9. 产出物要求

每个 Phase 必须产出以下工件：

### 9.1 页面矩阵

建议路径：

`reports/analysis/frontend-mainline-phase-X-matrix.md`

内容至少包括：

- 页面名
- 功能域
- 路由
- 组件
- Mock 结果
- Real 结果
- 问题分类
- 当前结论
- 下一步动作

### 9.2 状态汇总

建议路径：

`reports/analysis/frontend-mainline-phase-X-status.json`

内容至少包括：

- 页面总数
- 通过数
- 阻塞数
- Mock / Real 分开统计
- 缺陷分类统计

### 9.3 Graphiti 记忆

每批结束后，将以下内容写入 `mystocks_spec`：

- 本批页面范围
- Mock / Real 结果
- 已修复问题
- 未解决阻塞
- 剩余债务

## 10. 当前结论

在当前仓库状态下，后续工作的正确起点不是继续阅读后端实现，而是：

1. 冻结主链页面基线。
2. 优先跑 `Phase 1` 的 Mock 扫描。
3. 在后端恢复后，再补跑 `Phase 1` 的 Real 验证。

这条顺序能够最早暴露以下真实问题：

- 页面是否根本不存在
- 页面是否只是配置残留
- 页面是否只有壳没有功能
- 页面是否只在 Mock 下可用
- 页面是否真实接口一接就崩

## 11. 下一步

本方案确认后，下一份文档进入执行层：

`Phase 1 详细推进表`

该文档将逐页列出：

- 页面目标
- Mock / Real 对应接口
- 核心 DOM
- 验收条件
- 建议测试命令
- 常见失败分类
- 预期输出工件
