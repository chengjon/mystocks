# 2026-03-27 Frontend Directory Batch B：冻结列表

> 目标：明确当前目录治理过程中“绝对不动”的页面，禁止在后续批次中被迁移、重命名或改路由。

## 冻结规则

以下页面在当前目录治理阶段属于冻结对象：

- 不迁移
- 不重命名
- 不改 import 路径
- 不改路由落点
- 不作为试点迁移对象

## 一、用户明确指定的冻结列表

这批是本轮必须严格遵守的冻结项：

1. [Login.vue](/opt/claude/mystocks_spec/web/frontend/src/views/Login.vue)
2. [NotFound.vue](/opt/claude/mystocks_spec/web/frontend/src/views/NotFound.vue)
3. [TradingDashboard.vue](/opt/claude/mystocks_spec/web/frontend/src/views/TradingDashboard.vue)
4. [Screener.vue](/opt/claude/mystocks_spec/web/frontend/src/views/stocks/Screener.vue)
5. [AnnouncementMonitor.vue](/opt/claude/mystocks_spec/web/frontend/src/views/announcement/AnnouncementMonitor.vue)
6. [BacktestGPU.vue](/opt/claude/mystocks_spec/web/frontend/src/views/strategy/BacktestGPU.vue)

## 二、按风险规则追加的冻结项

基于 Batch B 风险分级，再追加 2 个当前不应触碰的高风险页：

7. [ArtDecoDashboard.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue)
8. [ArtDecoMonitoringDashboard.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue)

## 三、冻结原因

| 页面 | 原因 |
|---|---|
| `Login.vue` | 认证入口，影响登录链路 |
| `NotFound.vue` | 全局错误兜底页 |
| `TradingDashboard.vue` | 主交易终端，业务关键 |
| `Screener.vue` | 当前活跃选股页，且位于旧目录，需要单独决策 |
| `AnnouncementMonitor.vue` | 详情页落点仍依赖该组件 |
| `BacktestGPU.vue` | GPU 回测页，策略域关键功能 |
| `ArtDecoDashboard.vue` | 首页 Dashboard，所有主线导航中心 |
| `ArtDecoMonitoringDashboard.vue` | 系统监控工作台，观测能力核心页 |

## 四、Batch C 禁止事项

在进入下一批目录治理前，禁止对冻结列表做以下动作：

- `git mv`
- 文件重命名
- 切换到新域目录
- 替换路由组件落点
- 将其纳入“历史页 / demo 页 / deprecated 候选”

## 五、结论

当前 Batch B 的冻结范围共 8 个页面。  
后续 Batch C 的白名单筛选必须默认排除这 8 个页面。
