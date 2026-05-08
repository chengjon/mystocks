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

- 浏览器入口：[web/frontend/index.html](/opt/claude/mystocks_spec/web/frontend/index.html)
  - 挂接 `manifest.json`
  - 注入了 PWA 相关 meta
- 活跃入口：[web/frontend/src/main-standard.ts](/opt/claude/mystocks_spec/web/frontend/src/main-standard.ts)
  - `window.load` 后注册 `/sw.js`
  - 注册失败时输出 `SW registration failed`
  - 初始化超时或失败会输出 `Security init timed out` / `Security init failed`
- Service Worker 文件：[web/frontend/public/sw.js](/opt/claude/mystocks_spec/web/frontend/public/sw.js)
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

- wrapper：[web/frontend/src/utils/indexedDB.ts](/opt/claude/mystocks_spec/web/frontend/src/utils/indexedDB.ts)
- 活跃消费点：[web/frontend/src/stores/marketData.ts](/opt/claude/mystocks_spec/web/frontend/src/stores/marketData.ts)
- 直接单测入口：[web/frontend/tests/unit/utils/indexedDB.spec.ts](/opt/claude/mystocks_spec/web/frontend/tests/unit/utils/indexedDB.spec.ts)

当前 schema 可预期存在 4 个 object store：

- `market_data`
- `technical_indicators`
- `user_preferences`
- `api_cache`

浏览器侧的直接检查路径：

- Chrome DevTools
  - `Application -> Storage -> IndexedDB -> MyStocksDB`

### 1.3 Web Workers

当前 Web Workers 的直接观察面：

- 协议层：[web/frontend/src/workers/protocol.ts](/opt/claude/mystocks_spec/web/frontend/src/workers/protocol.ts)
- 指标 worker：[web/frontend/src/workers/indicatorDataWorker.worker.ts](/opt/claude/mystocks_spec/web/frontend/src/workers/indicatorDataWorker.worker.ts)
- manager façade：[web/frontend/src/utils/workersManager/workers-manager.ts](/opt/claude/mystocks_spec/web/frontend/src/utils/workersManager/workers-manager.ts)
- 活跃接入点：[web/frontend/src/stores/marketData.ts](/opt/claude/mystocks_spec/web/frontend/src/stores/marketData.ts)
- 直接守护测试：[web/frontend/tests/unit/config/indicator-worker-types-cleanup.spec.ts](/opt/claude/mystocks_spec/web/frontend/tests/unit/config/indicator-worker-types-cleanup.spec.ts)

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

当前 `manifest.json` 本身存在，但引用资源不是全量闭环。

可直接检查：

```bash
test -f web/frontend/public/icons/icon-192.png
test -f web/frontend/public/icons/icon-512.png
test -f web/frontend/public/screenshots/dashboard.png
test -f web/frontend/public/screenshots/analysis.png
```

当前 repo-truth：

- `icon-192.png` 存在
- `icon-512.png` 存在
- `screenshots/dashboard.png` 不存在
- `screenshots/analysis.png` 不存在

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
- shortcuts / screenshots 缺项

当前最可能原因：

- `vite-plugin-pwa` 仍禁用
- manifest 引用的截图资源缺失
- 当前仓库未完成 `2.1.2` 和 `2.1.5`

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

- 当前 full Chromium `295/295` 通过，不等价于 PWA 离线闭环已验收，因为多个 spec 显式 `serviceWorkers: 'block'`。
- 当前没有独立的 PM2 / backend 指标面专门暴露 service worker、IndexedDB 或 worker lifecycle 数据。
- 当前没有证据支持把 `3.2.x`、`3.3.x`、`2.9.x` 写成已完成。

## 5. Recommended Reader Path

1. 先看 [HTML5_RUNTIME_CAPABILITY_GUIDE.md](./HTML5_RUNTIME_CAPABILITY_GUIDE.md)
2. 再看本文档的运维检查和排障部分
3. 如需部署 history mode，再看 [history-mode-deployment-guide.md](./history-mode-deployment-guide.md)
4. 如需任务完成状态，以 OpenSpec task 清单和最近验证结果为准
