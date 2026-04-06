# MyStocks 前端主线测试 Phase 1 详细推进表

> 日期：2026-04-02
> 上游总纲：`docs/plans/2026-04-02-frontend-mainline-testing-overall-plan.md`
> 范围：Phase 1 六个页面的 Mock / Real 双轨验证与修复推进

## 1. 目标

Phase 1 的目标不是把所有业务功能一次做完，而是优先回答三件事：

1. 前端启动链是否稳定，页面是否真实存在。
2. 市场主链页面是否已经具备前端功能表达能力。
3. 在真实接口接入后，页面是否能完成最小读链验证。

本批次页面：

- `Login`
- `Dashboard`
- `Market-Realtime`
- `Market-Technical`
- `Market-LHB`
- `Data-Industry`

## 2. 进入条件

执行 Phase 1 前，固定先确认以下条件：

### 2.1 页面真值

- 路由真值：`web/frontend/src/router/index.ts`
- 功能树真值：`docs/FUNCTION_TREE.md`
- 主链清单真值：`docs/plans/frontend-page-optimization-list.md`

### 2.2 当前已知漂移

- `Dashboard` 在主链清单中仍有历史命名 `DealingRoom` 痕迹，但当前页面真路径以 `/dashboard` 为准。
- `pageConfig.ts` 含旧 API 口径，不能作为页面测试入口。
- `menu.config.js` 含旧路径，不能作为页面访问依据。

### 2.3 运行前提

Mock 轨：

- 前端可独立启动
- 后端可不在线
- Readiness probe 允许 stub

Real 轨：

- `mystocks-backend` 必须恢复到可访问状态
- `http://localhost:8020/health` 必须可达
- 若端口不是 `8020`，必须在报告中写明真实端口与绝对日期

## 3. 执行顺序

Phase 1 固定按以下顺序推进：

1. `Login`
2. `Dashboard`
3. `Market-Realtime`
4. `Market-Technical`
5. `Market-LHB`
6. `Data-Industry`

原因：

- `Login` 和 `Dashboard` 决定整条应用壳层是否可进入。
- `Market-Realtime`、`Market-Technical`、`Market-LHB` 是市场主链的最短路径。
- `Data-Industry` 是首个跨市场数据域的独立数据分析页，最容易暴露真实接口消费问题。

## 4. 统一执行模型

每个页面都固定跑以下 4 层：

1. `route-shell`
2. `mock-render`
3. `real-read`
4. `real-write/degrade`

对本批次而言，`real-write/degrade` 主要适用于：

- `Login`
- `Dashboard` 的刷新入口
- 其余页面只需验证最小降级与错误提示，不强求写链

## 5. Phase 1 页面矩阵

## 5.1 Login

### 页面基线

- 路由：`/login`
- 组件：`web/frontend/src/views/Login.vue`
- 功能域：认证与系统入口
- 当前已知关键 DOM：
  - `data-testid="username-input"`
  - `data-testid="password-input"`
  - `data-testid="login-button"`
  - 标题：`LOGIN`

### Canonical 接口

- 真实登录：`/api/v1/auth/login`
- 壳层探针：`/api/health/ready` 或 `/health/ready`
- CSRF：`/api/csrf-token`

### 现有可复用测试

- `web/frontend/tests/e2e/auth-login.spec.ts`

### Mock 轨要求

- 访问保护页时，应跳转至 `/login?redirect=...`
- 登录页表单结构必须完整
- stub 登录接口后，完成 UI 登录并回跳到 `/dashboard`
- localStorage 中必须写入 `auth_token` 与 `auth_user`

### Real 轨要求

- 真实 `admin/admin123` 可完成一次成功登录
- 成功后进入 `/dashboard`
- 错误账号口径需显示明确错误信息，不能静默失败

### 通过条件

- 登录页无白屏
- 输入框、按钮、提示账号存在
- 成功登录后进入保护页
- 本地鉴权态与页面路由一致

### 高概率问题分类

- `frontend render gap`
- `backend contract/runtime gap`

## 5.2 Dashboard

### 页面基线

- 路由：`/dashboard`
- 组件：`web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- 功能域：主交易室 / 市场总览
- 当前已知关键 DOM：
  - `QUANTIX`
  - `市场资金流向概览`
  - `主要市场指标`
  - `REQ:`
  - `刷新数据`

### Canonical 接口族

- `/api/v1/market/quotes`
- `/api/akshare/market/fund-flow/hsgt-summary`
- `/api/akshare/market/fund-flow/big-deal`
- `/api/v1/market/kline`
- `/api/v2/market/sector/fund-flow`
- `/health`
- `/api/v1/strategy/strategies`
- `/api/v1/trade/positions`

### 现有可复用测试

- `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`
- `web/frontend/tests/e2e/auth-login.spec.ts` 的登录后跳转部分

### Mock 轨要求

- stub readiness 与核心 API 后，Dashboard 必须完整渲染
- 顶部状态徽标、请求元信息条、资金流向卡、市场指标卡必须存在
- 任一单条 API 失败时，页面应保留壳层，不允许白屏

### Real 轨要求

- 市场概览主链至少一条真实数据可消费
- 接口返回空数组或空对象时，页面保持结构完整
- `REQ` 或 `Request ID` 位可见

### 通过条件

- 壳层、指标卡、刷新按钮、请求元信息条存在
- 至少一组真实读链能驱动页面内容更新
- 空态和“待接入真实接口”文案不导致布局塌陷

### 高概率问题分类

- `route/config drift`
- `backend contract/runtime gap`

## 5.3 Market-Realtime

### 页面基线

- 路由：`/market/realtime`
- 组件真入口：`web/frontend/src/views/market/Realtime.vue`
- ArtDeco 包装：`web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue`
- 当前已知关键 DOM：
  - `.market-realtime-tab`
  - `实时行情工作台`
  - `.stats-strip`
  - `.toolbar`
  - `.content-grid`
  - `刷新行情`

### Canonical 接口

- `/api/v1/market/quotes`

### 现有可复用测试

- `web/frontend/tests/e2e/market-data.spec.ts`

### Mock 轨要求

- `/market` 必须重定向到 `/market/realtime`
- stub `quotes` 后，页面壳层、统计卡、指数表格、涨跌分布都能渲染
- 市场 API 故障时页面仍保留工作台壳层

### Real 轨要求

- 真实 `quotes` 返回可映射为指数快照行
- 无数据时也要保持工作台结构
- TRACE / WINDOW / BOARD 元信息仍可显示

### 通过条件

- 工作台标题可见
- 统计卡区可见
- 表格区与分布区可见
- 刷新按钮可点击且不破坏页面

### 高概率问题分类

- `frontend render gap`
- `backend contract/runtime gap`

## 5.4 Market-Technical

### 页面基线

- 路由：`/market/technical`
- 组件真入口：`web/frontend/src/views/market/Technical.vue`
- ArtDeco 包装：`web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue`
- 当前已知关键 DOM：
  - `.market-kline-tab`
  - 标题：`K线分析工作台`
  - 副标题区：`K-Line Analysis`
  - `Real-time K-Line Data Stream Active`
  - `REQ:`
  - K 线表格

### Canonical 接口

- `/api/v1/market/kline`

### 现有可复用测试

- `web/frontend/tests/e2e/kline-chart.spec.ts`
- `web/frontend/tests/e2e/market-data.spec.ts`

### Mock 轨要求

- stub `kline` 后，页面壳层、占位图、数据摘要、近 5 行 K 线表格均可见
- 移动端与平板视口下布局不崩
- 不出现关键 console error

### Real 轨要求

- 真实 K 线响应可被 `extractKlineRows` 消费
- `POINTS`、`LAST CLOSE`、近 5 行表格能正常刷新
- 真实空数据时显示等待/空态，不崩溃

### 通过条件

- 工作台标题与分析标题可见
- `REQ:` 位可见
- 表格有表头
- 刷新 K 线动作不破坏页面

### 高概率问题分类

- `frontend render gap`
- `backend contract/runtime gap`

## 5.5 Market-LHB

### 页面基线

- 路由：`/market/lhb`
- 组件真入口：`web/frontend/src/views/market/LHB.vue`
- ArtDeco 包装：`web/frontend/src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue`
- 当前已知关键 DOM：
  - `龙虎榜工作台`
  - `龙虎榜数据`
  - 日期筛选器
  - 榜单过滤按钮：买入榜 / 卖出榜 / 机构榜

### Canonical 接口

- `/api/v2/market/lhb`

### 现有可复用测试

- `web/frontend/tests/e2e/market-data.spec.ts`
- `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`

### Mock 轨要求

- stub `lhb` 后，榜单页壳层和表格正常显示
- 日期切换和过滤切换不会打崩页面
- 空数据时仍保留工作台与筛选器结构

### Real 轨要求

- 真实接口返回可映射为榜单表格
- `limit=100` 的真实路径消费无结构性错误
- 不因筛选切换产生未处理异常

### 通过条件

- 工作台标题可见
- 榜单表格可见
- 日期选择器可见
- 过滤按钮可切换

### 高概率问题分类

- `frontend render gap`
- `backend contract/runtime gap`

## 5.6 Data-Industry

### 页面基线

- 路由：`/data/industry`
- 组件真入口：`web/frontend/src/views/data/Industry.vue`
- ArtDeco 包装：`web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue`
- 当前已知关键 DOM：
  - `.industry-analysis-page`
  - `板块动向工作台`
  - `DATA: REAL`
  - `REQ_ID:`
  - `板块热度排行`
  - `资金轮动快照`
  - `刷新板块`

### Canonical 接口

- `/api/v2/market/sector/fund-flow`
  - 参数：`sector_type=行业`
  - 参数：`timeframe=今日`
  - 参数：`limit=10`

### 现有可复用测试

- 当前仓库没有独立稳定的专用 E2E，优先纳入 `Phase 1` 新矩阵和 `comprehensive-all-pages` 覆盖

### Mock 轨要求

- stub 行业板块流向数据后，排行表和轮动快照均可见
- 空数据时应显示 `暂无板块数据`
- 接口失败时应显示 `板块数据加载失败`

### Real 轨要求

- 真实 `sector/fund-flow` 响应可映射为 `boardRows`
- `dataSource` 维持 `REAL`
- `REQ_ID` 和处理时间能显化

### 通过条件

- 工作台标题可见
- 至少一个状态卡可见
- 表格区和轮动区可见
- 空态、错态都存在并可触发

### 高概率问题分类

- `backend contract/runtime gap`
- `frontend render gap`

## 6. 批次执行命令建议

## 6.1 Mock 轨

前端启动：

```bash
cd web/frontend
npm run dev:mock
```

建议先跑：

```bash
cd web/frontend
npx playwright test tests/e2e/auth-login.spec.ts --project=chromium
npx playwright test tests/e2e/market-data.spec.ts --project=chromium
npx playwright test tests/e2e/kline-chart.spec.ts --project=chromium
```

必要时补跑：

```bash
cd web/frontend
npx playwright test tests/e2e/comprehensive-all-pages.spec.ts --project=chromium
```

## 6.2 Real 轨

前提：

- 后端恢复可用
- `http://localhost:8020/health` 可访问

前端启动：

```bash
cd web/frontend
npm run dev:real
```

建议执行：

```bash
cd web/frontend
npm run test:e2e:auth
npx playwright test tests/e2e/market-data.spec.ts --project=chromium
npx playwright test tests/e2e/kline-chart.spec.ts --project=chromium
```

若需要整批回归：

```bash
cd web/frontend
npm run test:e2e:business-smoke
```

## 7. 批次报告要求

Phase 1 完成时，报告中至少包含：

- 页面范围：6 页
- Mock：
  - 通过数 / 失败数 / 跳过数
- Real：
  - 通过数 / 失败数 / 跳过数
- 问题分类计数：
  - `route/config drift`
  - `frontend render gap`
  - `backend contract/runtime gap`
- 质量门禁：
  - 结构性语法错误
  - 类型错误是否高于基线
  - PM2 服务状态
  - 服务地址
- 当前阻塞项
- 下一批进入条件

## 8. 预期结论

Phase 1 结束后，必须能明确回答：

1. 登录链路是否稳定。
2. Dashboard 是否只是壳层，还是已经具备真实读链能力。
3. 市场主链 3 页是否在 Mock 下具备真实功能表达。
4. K 线、龙虎榜、行业板块页在 Real 模式下是否真正可消费真实响应。
5. 当前主要问题究竟集中在：
   - 配置漂移
   - 前端未实现
   - 后端契约/运行异常

## 9. 下一步

当本批次完成后，进入：

- `Phase 1 状态矩阵报告`
- `Phase 2 详细推进表`
