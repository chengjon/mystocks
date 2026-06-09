# HTML5 Runtime Operations Guide

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## Scope

这份 guide 只覆盖 `implement-html5-migration-experience-optimization` 当前已经存在的 HTML5 runtime 能力的运维观察面与排障入口，重点是：

1. PWA runtime surface 当前能看什么
2. IndexedDB 当前能查什么
3. Web Workers 当前能查什么
4. 哪些事项仍然不能被误写成“已进入生产级监控闭环”

若需要能力清单，请先看 [HTML5_RUNTIME_CAPABILITY_GUIDE.md](./HTML5_RUNTIME_CAPABILITY_GUIDE.md)。

> **产品口径说明（2026-05-08）**:
> 当前前端产品范围以 **Desktop-only** 为准。
> 因此本文中的 PWA / Service Worker / IndexedDB / Web Worker 排障步骤，应按桌面浏览器运行时表面理解，而不是移动端运维支持承诺。

## 1. Current Monitoring Surface

### 1.1 PWA / Service Worker

当前可直接观察的 repo-owned runtime surface：

- 浏览器入口：[web/frontend/index.html](../../../web/frontend/index.html)
  - 挂接 `manifest.json`
  - 注入了 PWA 相关 meta
- 活跃入口：[web/frontend/src/main-standard.ts](../../../web/frontend/src/main-standard.ts)
  - `window.load` 后注册 `/sw.js`
  - 注册失败时输出 `SW registration failed`
  - 初始化超时或失败会输出 `Security init timed out` / `Security init failed`
- Service Worker 文件：[web/frontend/public/sw.js](../../../web/frontend/public/sw.js)
  - 已定义缓存名
  - 已实现 API / 静态资源 / 导航请求的不同缓存策略

在 **Desktop-only** 口径下，上述检查用于确认桌面浏览器安装/缓存表面是否仍然存在，不代表移动端 PWA 产品链路已纳入当前运维范围。

当前可用的最小检查：

```bash
curl -I http://localhost:3020/manifest.json
curl -I http://localhost:3020/sw.js
```

### 1.2 IndexedDB

当前 IndexedDB 的直接运维观察面：

- wrapper：[web/frontend/src/utils/indexedDB.ts](../../../web/frontend/src/utils/indexedDB.ts)
- 活跃消费点：[web/frontend/src/stores/marketData.ts](../../../web/frontend/src/stores/marketData.ts)
- 直接单测入口：[web/frontend/tests/unit/utils/indexedDB.spec.ts](../../../web/frontend/tests/unit/utils/indexedDB.spec.ts)
- 配额观察：`indexedDB.getStorageQuota()` 使用 `navigator.storage.estimate()` 返回 `usage` / `quota` / `usageRatio`，`indexedDB.isStorageQuotaNearLimit()` 提供默认 `80%` 阈值判断。

当前 schema 可预期存在 4 个 object store：

- `market_data`
- `technical_indicators`
- `user_preferences`
- `api_cache`

浏览器侧的直接检查路径：

- Chrome DevTools
  - `Application -> Storage -> IndexedDB -> MyStocksDB`
- Console
  - `await navigator.storage.estimate()`

当前边界：

- 配额能力是 repo-local utility / browser surface，不等价于生产级告警。
- `system/Settings.vue` 中的配额展示仍不作为 quota runtime truth source。

### 1.3 Web Workers

当前 Web Workers 的直接观察面：

- 协议层：[web/frontend/src/workers/protocol.ts](../../../web/frontend/src/workers/protocol.ts)
- 指标 worker：[web/frontend/src/workers/indicatorDataWorker.worker.ts](../../../web/frontend/src/workers/indicatorDataWorker.worker.ts)
- manager façade：[web/frontend/src/utils/workersManager/workers-manager.ts](../../../web/frontend/src/utils/workersManager/workers-manager.ts)
- 活跃接入点：[web/frontend/src/stores/marketData.ts](../../../web/frontend/src/stores/marketData.ts)
- 直接守护测试：[web/frontend/tests/unit/config/indicator-worker-types-cleanup.spec.ts](../../../web/frontend/tests/unit/config/indicator-worker-types-cleanup.spec.ts)

当前最小 repo-local 检查：

```bash
cd web/frontend
npm run test -- tests/unit/utils/indexedDB.spec.ts tests/unit/config/indicator-worker-types-cleanup.spec.ts
```

## 2. Current Operational Checks

### 2.1 Runtime File Reachability

共享 PM2 前端在线时，先确认：

```bash
curl -I http://localhost:3020/
curl -I http://localhost:3020/manifest.json
curl -I http://localhost:3020/sw.js
```

期望：

- `/` 返回 `200`
- `/manifest.json` 返回 `200`
- `/sw.js` 返回 `200`

### 2.2 Manifest Asset Sanity

当前 `manifest.json` 本身存在，且 Desktop-only manifest asset consistency 已闭合；未纳入当前闭合范围的是生产级品牌图标替换、移动端 screenshots / splash screens 和 shortcut 图标设计。

可直接检查：

```bash
test -f web/frontend/public/icons/icon-192.png
test -f web/frontend/public/icons/icon-512.png
npm run test -- tests/unit/config/pwa-manifest-assets.spec.ts
```

当前 repo-truth：

- `icon-192.png` 存在
- `icon-512.png` 存在
- Desktop-only manifest 当前只引用 `public/` 下存在的核心 PWA 图标。
- `screenshots/*` 与 `shortcut-*.png` 不再作为当前 manifest 引用项。
- `form_factor: "narrow"` 移动端截图声明不属于当前 Desktop-only scope。

这属于已知边界，不应被当成线上突发故障。

### 2.3 Browser-side Inspection

建议的浏览器排查顺序：

1. `Application -> Manifest`
2. `Application -> Service Workers`
3. `Application -> IndexedDB`
4. `Console`

重点看：

- manifest 是否被浏览器识别
- service worker 是否注册成功
- `MyStocksDB` 是否创建成功
- 是否出现 `SW registration failed` / `IndexedDB initialization failed`

## 3. Troubleshooting

### 3.1 `manifest.json` 可访问，但安装体验不完整

症状：

- manifest 正常返回
- 浏览器安装体验不稳定
- 当前 manifest 不提供移动端 screenshots 或 shortcuts

当前最可能原因：

- `vite-plugin-pwa` 仍禁用
- 当前仓库未完成 `2.1.5`
- 当前 `2.1.2` 只按 Desktop-only manifest asset consistency 收口，不包含生产级品牌图标替换、移动端 screenshots / splash screens 或 shortcut 图标设计。

当前处理原则：

- 视为已知未闭合任务，不当作突发运行回归

### 3.2 Service Worker 未注册

症状：

- 浏览器控制台看到 `SW registration failed`
- `Application -> Service Workers` 中看不到 `sw.js`

排查：

1. 确认 `http://localhost:3020/sw.js` 可访问
2. 确认入口仍为 `index.html -> src/main-standard.ts`
3. 检查控制台是否先出现其他初始化失败导致链路中断

### 3.3 IndexedDB 初始化失败

症状：

- 控制台出现 `IndexedDB initialization failed`
- `Application -> IndexedDB` 中没有 `MyStocksDB`

排查：

1. 先跑：

```bash
cd web/frontend
npm run test -- tests/unit/utils/indexedDB.spec.ts
```

2. 再检查浏览器是否处于无痕 / 隐私限制环境
3. 确认当前活跃 store 是否实际命中了 `marketData.ts` 的缓存链路

### 3.4 Worker 路径存在，但性能编排与预期不符

症状：

- 协议和 worker 文件都在
- 但运行效果不像完整 worker orchestration

当前最可能原因：

- `workers-manager.ts` 当前仍是轻量 façade
- 现阶段不能按“企业级 worker 生命周期管理已闭环”来判断

当前处理原则：

- 按 repo-truth 视作“能力面已存在、编排闭环未完成”
- 不把这类现象误判为本轮回归

## 4. Important Boundaries

- 普通 Chromium smoke / mainline 结果应按实际执行命令和用例数报告；它们不等价于 PWA 离线闭环已验收，因为多个 spec 显式 `serviceWorkers: 'block'`。
- 当前没有独立的 PM2 / backend 指标面专门暴露 service worker、IndexedDB 或 worker lifecycle 数据。
- 当前没有证据支持把 `3.2.x`、`3.3.2-3.3.3`、`2.9.x` 写成已完成；`3.3.1` 仅按 repo-local production preview server PWA support 闭合，不代表生产部署或 release owner 签收。

## 5. Server PWA Support Checklist

本清单用于后续验证服务器是否具备 Desktop-only HTML5 runtime 所需的 PWA 静态资源支持。

它只定义检查材料；只有在目标环境实际执行并记录结果后，才能作为 `3.3.1` 的候选验收证据。

### 5.1 Required Server Behaviors

- `/` 应返回当前 SPA 入口。
- `/manifest.json` 应可达，并使用 JSON 相关 content type。
- `/sw.js` 应可达，并使用 JavaScript 相关 content type。
- `/offline.html` 应可达，作为离线 fallback 资源。
- 静态 assets 可缓存，但 `sw.js` 不应被长时间强缓存到无法及时更新。
- History mode fallback 不应吞掉 `/manifest.json`、`/sw.js`、`/offline.html` 这类 PWA 资源请求。
- 目标环境应使用 HTTPS，或明确为 localhost / 开发环境例外。

### 5.2 Minimum Checks

```bash
curl -I http://localhost:3020/
curl -I http://localhost:3020/manifest.json
curl -I http://localhost:3020/sw.js
curl -I http://localhost:3020/offline.html
```

记录时至少保留：

- HTTP status
- `content-type`
- `cache-control`
- 执行环境和域名
- 是否经过代理、Nginx、Apache、CDN 或 PM2 静态服务

### 5.3 Server Support Record Template

```markdown
## HTML5 Runtime Server PWA Support Record

- Date:
- Environment:
- Domain / base URL:
- Release owner:
- Static serving layer:
- HTTPS status:
- `/` result:
- `/manifest.json` result:
- `/sw.js` result:
- `/offline.html` result:
- Cache-control notes:
- History fallback notes:
- Residual risk:
- Accepted by:
```

### 5.4 Non-Goals

- 不把本地 PM2 可达性自动外推为生产服务器已配置完成。
- 不把 History mode fallback 配置等同于 PWA server support 已完成。
- 不把 manifest / service worker 文件存在等同于完整 PWA 安装和离线闭环。
- 不覆盖移动端、平板端或应用商店式安装分发。

## 6. Offline Validation Matrix Template

本模板用于后续 Desktop-only PWA 离线验收。

它只定义离线验证矩阵；只有在允许 service worker 的浏览器环境中实际执行并记录结果后，才能作为 `3.2.1` 的候选验收证据。

### 6.1 Preconditions

- 不复用显式 `serviceWorkers: 'block'` 的 Playwright smoke 结果声明离线闭环。
- 先确认 `/manifest.json`、`/sw.js`、`/offline.html` 在目标环境可达。
- 先清理旧 service worker / cache，避免旧资产影响验证结论。
- 只覆盖 Desktop-only 核心浏览器场景，不扩展到 mobile/tablet。

### 6.2 Route Matrix

| Route | Expected online state | Offline expectation | Evidence |
|-------|-----------------------|---------------------|----------|
| `/login` | Login shell renders | Shell or offline fallback renders | |
| `/dashboard` | Dashboard shell renders | Cached shell or fallback behavior recorded | |
| `/market/realtime` | Market route shell renders | Cached shell or fallback behavior recorded | |
| `/strategy/repo` | Strategy route shell renders | Cached shell or fallback behavior recorded | |
| `/risk/overview` | Risk route shell renders | Cached shell or fallback behavior recorded | |
| `/trade/terminal` | Trade terminal shell renders | Cached shell or fallback behavior recorded | |

### 6.3 Required Evidence

- Browser / Playwright project
- Service worker state before and after the run
- Cache Storage entries observed
- Online baseline result
- Offline reload result
- Console errors related to service worker, cache, IndexedDB, or worker lifecycle
- Whether the behavior is cached shell, API fallback, or `offline.html`

### 6.4 Offline Validation Record Template

```markdown
## HTML5 Runtime Offline Validation Record

- Date:
- Branch / commit:
- Browser project:
- Service workers allowed:
- Routes covered:
- Online baseline result:
- Offline reload result:
- Cache / service worker observations:
- IndexedDB observations:
- Console errors:
- Residual risk:
- Accepted by:
```

### 6.5 Non-Goals

- 不证明所有业务流程都可离线完成。
- 不证明交易、行情刷新或通知链路可离线执行。
- 不覆盖移动端或平板端安装体验。
- 不把静态 shell 可见性等同于核心业务全离线可用。

## 7. Cross-Browser PWA Validation Template

本模板用于后续 Desktop-only PWA 跨浏览器验证。

它只定义验证矩阵；只有在对应浏览器项目实际执行并记录结果后，才能作为 `3.2.2` 的候选验收证据。

### 7.1 Preconditions

- 不把单一 `chromium` smoke 结果扩写为 Chrome / Firefox / Safari / Edge 全部通过。
- 不复用默认 `serviceWorkers: "block"` 的结果声明 PWA 功能通过。
- 先记录 `web/frontend/playwright.config.js` / `playwright.config.ts` 使用的实际项目与 service worker 策略。
- 只覆盖 Desktop-only 浏览器项目，不扩展到 mobile browser emulation。

### 7.2 Browser Matrix

| Browser project | PWA install surface | Service worker registration | Offline fallback | Notes |
|-----------------|---------------------|-----------------------------|------------------|-------|
| Chromium / Chrome | Pending evidence | Pending evidence | Pending evidence | |
| Firefox | Pending evidence | Pending evidence | Pending evidence | |
| WebKit / Safari | Pending evidence | Pending evidence | Pending evidence | |
| Edge | Pending evidence | Pending evidence | Pending evidence | May require explicit environment or manual evidence |

### 7.3 Required Evidence

- Browser project and version
- Whether service workers were allowed or blocked
- `/manifest.json` result
- `/sw.js` registration state
- `Application` / equivalent browser storage observation where available
- Offline reload or fallback behavior
- Console errors and browser-specific limitations
- Whether the result is automated Playwright evidence or manual browser evidence

### 7.4 Cross-Browser Record Template

```markdown
## HTML5 Runtime Cross-Browser PWA Record

- Date:
- Branch / commit:
- Browser project:
- Browser version:
- Service workers allowed:
- Manifest result:
- Service worker result:
- Offline fallback result:
- Known browser-specific limitations:
- Evidence type:
- Residual risk:
- Accepted by:
```

### 7.5 Non-Goals

- 不承诺移动端浏览器支持。
- 不把 WebKit desktop smoke 结果等同于 iOS Safari 验收。
- 不把 browser shell 可打开等同于完整 PWA 安装和离线闭环。
- 不替代 `3.2.1` 的离线 route matrix 或 `3.3.2-3.3.3` 的灰度/回滚监控记录。

## 8. IndexedDB Persistence and Migration Validation Template

本模板用于后续 Desktop-only IndexedDB 持久化与迁移验证。

它只定义验证矩阵；只有在桌面浏览器中实际执行并记录结果后，才能作为 `3.2.3` 的候选验收证据。

### 8.1 Preconditions

- 先确认当前 canonical wrapper 仍是 `web/frontend/src/utils/indexedDB.ts`。
- 先确认活跃消费点仍包含 `web/frontend/src/stores/marketData.ts`。
- 不把 `indexedDB.spec.ts` 单测通过扩写为浏览器持久化、升级迁移和跨会话恢复全部通过。
- 只覆盖 Desktop-only 浏览器运行时，不扩展到 mobile/tablet storage 行为。

### 8.2 Persistence Matrix

| Store | Write path | Reload expectation | Offline / API-failure expectation | Evidence |
|-------|------------|--------------------|-----------------------------------|----------|
| `market_data` | Market data cache | Data remains after reload | Cached market snapshot can be inspected or fallback behavior recorded | |
| `technical_indicators` | Indicator cache | Indicator result remains after reload | Cached indicator result can be inspected or fallback behavior recorded | |
| `user_preferences` | Preferences persistence | Preference remains after reload | Preference is still readable without network | |
| `api_cache` | API cache with TTL | Valid cache remains until TTL expiry | Expired vs valid cache behavior is recorded | |

### 8.3 Migration Checks

- Existing database version and object stores before the run.
- Database version and object stores after the run.
- Whether old records remain readable after reload.
- Whether missing stores are created without data loss.
- Whether localStorage-to-IndexedDB migration is implemented, not implemented, or out of scope for the current runtime path.
- Whether quota, corrupted records, or blocked IndexedDB access produce observable errors.

### 8.4 IndexedDB Validation Record Template

```markdown
## HTML5 Runtime IndexedDB Persistence and Migration Record

- Date:
- Branch / commit:
- Browser project:
- Browser version:
- IndexedDB database name:
- Initial schema / object stores:
- Post-run schema / object stores:
- Stores covered:
- Reload persistence result:
- Offline / API-failure result:
- Migration result:
- Quota / blocked-storage observations:
- Console errors:
- Residual risk:
- Accepted by:
```

### 8.5 Non-Goals

- 不证明所有业务数据都已迁移到 IndexedDB。
- 不把 wrapper API 单测通过等同于真实桌面浏览器持久化验收。
- 不承诺移动端、平板端或隐私模式下的持久化行为。
- 不替代 `3.1.2` 的 Web Workers 与 IndexedDB 数据流验证。

## 9. Web Worker Performance Quantification Template

本模板用于后续 Desktop-only Web Worker 性能提升量化。

它只定义测量口径；只有在同一数据集上实际执行主线程路径与 worker 路径对比，并记录结果后，才能作为 `3.2.4` 的候选验收证据。

### 9.1 Preconditions

- 先确认当前 worker 协议、worker 文件和 manager façade 仍分别位于：
  - `web/frontend/src/workers/protocol.ts`
  - `web/frontend/src/workers/indicatorDataWorker.worker.ts`
  - `web/frontend/src/utils/workersManager/workers-manager.ts`
- 不把 worker 文件存在扩写为性能收益已量化。
- 不把 `workers-manager.ts` 的 placeholder / façade 行为扩写为完整多 worker orchestration 已完成。
- 只覆盖 Desktop-only 浏览器运行时，不扩展到 mobile/tablet 性能口径。

### 9.2 Benchmark Matrix

| Workload | Dataset size | Main-thread baseline | Worker-path result | UI responsiveness observation | Evidence |
|----------|--------------|----------------------|--------------------|-------------------------------|----------|
| MA calculation | Pending evidence | Pending evidence | Pending evidence | Pending evidence | |
| EMA calculation | Pending evidence | Pending evidence | Pending evidence | Pending evidence | |
| MACD calculation | Pending evidence | Pending evidence | Pending evidence | Pending evidence | |
| RSI calculation | Pending evidence | Pending evidence | Pending evidence | Pending evidence | |
| Large K-line transformation | Pending evidence | Pending evidence | Pending evidence | Pending evidence | |

### 9.3 Required Metrics

- Browser project and version.
- Dataset source and row count.
- Indicator or transformation type.
- Main-thread elapsed time.
- Worker-path elapsed time.
- Long task count or main-thread blocking observation.
- Memory observation if available.
- Progress, cancellation, timeout, and error fallback behavior where applicable.

### 9.4 Web Worker Performance Record Template

```markdown
## HTML5 Runtime Web Worker Performance Record

- Date:
- Branch / commit:
- Browser project:
- Browser version:
- Workload:
- Dataset source / row count:
- Main-thread elapsed time:
- Worker-path elapsed time:
- UI responsiveness observation:
- Long task / blocking observation:
- Memory observation:
- Error / fallback behavior:
- Residual risk:
- Accepted by:
```

### 9.5 Non-Goals

- 不把存在 worker protocol / worker file 等同于性能提升已验证。
- 不把单一小数据集结果外推为所有市场数据处理场景。
- 不承诺 GPU 级加速、完整多 worker 调度或生产级 worker 健康治理。
- 不替代 `2.4.2` 的 K 线数据处理 worker 主链路实现或 `2.4.5` 的生命周期治理。

## 10. Progressive Rollout Strategy Template

本模板用于后续 Desktop-only HTML5 runtime 灰度。

它只定义灰度策略材料；只有产生真实执行记录、验证命令和 release owner 签收后，才能作为 `3.3.2` 的候选验收证据。

### 10.1 Rollout Phases

| Phase | Scope | Entry Gate | Exit Gate |
|-------|-------|------------|-----------|
| Phase 0 | Repo-local readiness | OpenSpec validate 通过；相关 guide 已更新 | 任务清单记录当前未闭合边界 |
| Phase 1 | Internal desktop smoke | PM2 前端可达；`/manifest.json` 和 `/sw.js` 可达 | Chromium smoke 或相关 runtime gate 通过 |
| Phase 2 | Limited desktop cohort | rollback runbook 可用；support FAQ 可用 | 无新增 service worker / cache 阻断问题 |
| Phase 3 | Wider desktop rollout | Phase 2 记录已签收 | 关键桌面路由和 Lighthouse smoke 无新增阻断失败 |
| Hold | Stop rollout | 任一中止条件触发 | 进入 rollback runbook 或修复后重启 Phase 1 |

### 10.2 Required Evidence Per Phase

- 日期、branch / commit、release owner
- phase scope 与受影响用户范围
- PM2 / HTTP reachability 结果
- Playwright / Lighthouse / runtime gate 结果
- service worker / cache / IndexedDB / worker 观察结论
- rollback 是否可执行，以及是否已触发
- 已知 residual risk 和 follow-up owner

### 10.3 Abort Conditions

满足任一条件时应暂停灰度：

- 桌面端主入口不可用，且与 service worker、manifest 或 cache 更新相关。
- 已修复代码仍被旧 service worker / cache 持续覆盖。
- 核心桌面路由在 Chromium smoke 中出现新增阻断失败。
- Lighthouse smoke 出现首屏、runtime 或 install surface 新增阻断失败。
- support / operations 不能按现有 guide 解释问题边界。

### 10.4 Non-Goals

- 不承诺移动端或平板端灰度。
- 不把 `best-effort cache / fallback` 宣称为完整离线业务闭环。
- 不把 manifest、service worker 文件存在等同于完整 PWA 发布。
- 不把人工观察信号等同于生产级监控告警。

### 10.5 Rollout Record Template

```markdown
## HTML5 Runtime Progressive Rollout Record

- Date:
- Branch / commit:
- Release owner:
- Phase:
- Scope:
- Entry gate evidence:
- Exit gate evidence:
- PM2 / HTTP checks:
- Playwright / Lighthouse result:
- Runtime observations:
- Abort / rollback status:
- Residual risk:
- Follow-up owner:
```

## 11. Architecture Integration Validation Templates

本节用于后续 Desktop-only HTML5 runtime 架构集成验证。

它只定义验证材料；只有实际执行并记录结果后，才能作为 `3.1.1` 或 `3.1.2` 的候选验收证据。

### 11.1 Menu and PWA Integration Template

该模板用于验证菜单系统与 PWA / service worker 表面的集成，不用于证明移动端安装体验。

#### Preconditions

- 菜单 canonical SSOT 仍是 `web/frontend/src/layouts/MenuConfig.ts`。
- 当前业务域仍按 Market / Data / Watchlist / Strategy / Trade / Risk / System 七个桌面端域理解。
- 不复用 `serviceWorkers: "block"` 的 smoke 结果声明离线菜单已验收。
- 不把菜单 online 可点击等同于 PWA 离线菜单能力完成。

#### Menu / PWA Matrix

| Domain | Canonical route group | Online navigation | Service worker allowed | Offline shell / fallback | Evidence |
|--------|-----------------------|-------------------|-------------------------|--------------------------|----------|
| Market | `/market/*` | Pending evidence | Pending evidence | Pending evidence | |
| Data | `/data/*` | Pending evidence | Pending evidence | Pending evidence | |
| Watchlist | `/watchlist/*` | Pending evidence | Pending evidence | Pending evidence | |
| Strategy | `/strategy/*` | Pending evidence | Pending evidence | Pending evidence | |
| Trade | `/trade/*` | Pending evidence | Pending evidence | Pending evidence | |
| Risk | `/risk/*` | Pending evidence | Pending evidence | Pending evidence | |
| System | `/system/*` | Pending evidence | Pending evidence | Pending evidence | |

#### Menu / PWA Record Template

```markdown
## HTML5 Runtime Menu and PWA Integration Record

- Date:
- Branch / commit:
- Browser project:
- Service workers allowed:
- Menu source checked:
- Domains covered:
- Online navigation result:
- Offline shell / fallback result:
- Console errors:
- Residual risk:
- Accepted by:
```

### 11.2 Web Workers and IndexedDB Data Flow Template

该模板用于验证 Web Workers 与 IndexedDB 在市场数据链路中的数据流，不用于证明 worker 性能收益或 IndexedDB 迁移闭环。

#### Preconditions

- IndexedDB wrapper 仍是 `web/frontend/src/utils/indexedDB.ts`。
- 活跃消费点仍包含 `web/frontend/src/stores/marketData.ts`。
- Worker 协议和 manager surface 仍分别由 `web/frontend/src/workers/protocol.ts` 与 `web/frontend/src/utils/workersManager/workers-manager.ts` 承载。
- 明确记录 `workers-manager.ts` 是否仍是 façade / placeholder 状态。

#### Data Flow Matrix

| Flow | Expected handoff | IndexedDB observation | Worker observation | Evidence |
|------|------------------|-----------------------|--------------------|----------|
| Market overview cache | Network or fallback writes cache | `market_data` or `api_cache` updated | Not required | |
| Market analysis cache | Network or fallback writes cache | `market_data` or `api_cache` updated | Not required | |
| Technical indicator calculation | `marketData.ts` requests calculation | `technical_indicators` may persist result | Worker façade / worker path recorded | |
| Cached indicator reload | Existing cached result is read | `technical_indicators` read observed | Worker bypass or recalculation recorded | |

#### Data Flow Record Template

```markdown
## HTML5 Runtime Workers and IndexedDB Data Flow Record

- Date:
- Branch / commit:
- Browser project:
- Route / user flow:
- Dataset / symbol:
- IndexedDB stores observed:
- Worker path observed:
- Manager façade status:
- Data handoff result:
- Console errors:
- Residual risk:
- Accepted by:
```

### 11.3 Cache Strategy and Realtime Consistency Template

该模板用于验证 cache-first / network-first / fallback 策略是否与实时市场数据展示保持一致，不用于证明 cache analytics 或生产级实时监控已经完成。

#### Preconditions

- 先确认 `web/frontend/public/sw.js` 仍承载静态资源、导航请求和 API 请求缓存策略。
- 先确认 `web/frontend/src/utils/indexedDB.ts` 仍提供 `api_cache` TTL 行为。
- 先确认相关市场数据消费路径仍经过 `web/frontend/src/stores/marketData.ts`。
- 不把静态资源 cache 命中扩写为实时行情一致性已验收。

#### Consistency Matrix

| Scenario | Expected strategy | Freshness expectation | Fallback expectation | Evidence |
|----------|-------------------|-----------------------|----------------------|----------|
| Static asset reload | Cache-first | Asset version matches current build or known cache version | Old asset does not hide blocking runtime fixes | |
| Navigation request | Cached shell / fallback | Route shell remains usable | `offline.html` or cached shell behavior recorded | |
| Market overview API | Network-first or IndexedDB fallback | New network data supersedes stale cache | Stale cache is visibly bounded or recorded | |
| Realtime market route | Network-first for dynamic data | UI does not present stale data as fresh realtime data | Error / stale-data state is visible or recorded | |
| API cache TTL expiry | IndexedDB TTL behavior | Expired cache is not treated as fresh | Fallback behavior is recorded | |

#### Cache Consistency Record Template

```markdown
## HTML5 Runtime Cache Strategy and Realtime Consistency Record

- Date:
- Branch / commit:
- Browser project:
- Route / API flow:
- Service worker state:
- IndexedDB cache state:
- Network result:
- Cached / fallback result:
- Freshness indicator observed:
- Stale-data handling:
- Console errors:
- Residual risk:
- Accepted by:
```

### 11.4 HTML5 APIs Compatibility Template

该模板用于验证当前仍在 Desktop-only scope 内的 HTML5 runtime API 与现有功能是否兼容，不用于恢复已去作用域的移动端 API 目标。

#### Preconditions

- 只验证当前仓库仍有活跃代码面的 API：manifest、service worker、IndexedDB、Web Workers、Network Information / online status 等。
- Geolocation、Vibration、Battery、Device Orientation 等移动端/无关 API 在当前 scope 下保持 de-scoped，不作为兼容性验收目标。
- 不把浏览器支持某 API 扩写为业务功能已完整接入。
- 不覆盖 mobile/tablet browser compatibility。

#### Compatibility Matrix

| API surface | Active repo-owned surface | Compatibility check | Evidence |
|-------------|---------------------------|---------------------|----------|
| Manifest | `index.html` + `public/manifest.json` | Manifest is parsed without blocking desktop shell | |
| Service Worker | `src/main-standard.ts` + `public/sw.js` | Registration behavior does not break desktop routes | |
| IndexedDB | `src/utils/indexedDB.ts` | Initialization failure is handled without blank screen | |
| Web Workers | `src/workers/*` + `workersManager` surface | Worker or façade failure does not block market shell | |
| Network status | `src/composables/useNetworkStatus.ts` | Online/offline state changes do not break active UI | |

#### Compatibility Record Template

```markdown
## HTML5 Runtime API Compatibility Record

- Date:
- Branch / commit:
- Browser project:
- API surfaces covered:
- Route / feature flow:
- Compatibility result:
- Fallback behavior:
- Console errors:
- De-scoped APIs confirmed excluded:
- Residual risk:
- Accepted by:
```

### 11.5 Non-Goals

- 不证明完整离线业务闭环。
- 不证明所有路由都完成 PWA 离线验收。
- 不证明 Web Worker 性能提升已经量化。
- 不证明 future IndexedDB schema upgrade migration、跨浏览器持久化或生产数据迁移已经完成。
- 不覆盖移动端或平板端菜单/安装体验。
- 不恢复 Geolocation、Vibration、Battery、Device Orientation 等已去作用域移动端/无关 API。

## 12. Recommended Reader Path

1. 先看 [HTML5_RUNTIME_CAPABILITY_GUIDE.md](./HTML5_RUNTIME_CAPABILITY_GUIDE.md)
2. 再看本文档的运维检查和排障部分
3. 如需处理 HTML5 runtime 回滚，再看 [HTML5_RUNTIME_ROLLBACK_RUNBOOK.md](./HTML5_RUNTIME_ROLLBACK_RUNBOOK.md)
4. 如需部署 history mode，再看 [history-mode-deployment-guide.md](./history-mode-deployment-guide.md)
5. 如需任务完成状态，以 OpenSpec task 清单和最近验证结果为准
