# HTML5 Runtime Rollback Runbook

> **权威来源声明**:
> 本文件是 `implement-html5-migration-experience-optimization` 的 Desktop-only HTML5 runtime 回滚执行材料。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及任务完成状态，请以 OpenSpec task 清单和最近验证结果为准。

## Scope

本 runbook 只覆盖桌面浏览器中的 HTML5 runtime 表面：

- `index.html` 中的 manifest / PWA meta 挂接
- `src/main-standard.ts` 中的 service worker 注册表面
- `public/sw.js` 及浏览器侧已安装的 service worker / cache 影响
- IndexedDB / Web Worker 相关运行时观察面

不覆盖移动端、平板端、原生安装体验、生产发布审批或外部监控平台接线。

## Owner And Entry

- Release owner: 前端发布负责人或当次灰度负责人
- Reviewer: OpenSpec change owner
- Runtime evidence owner: 执行本 runbook 的当次值守人
- Canonical task: `openspec/changes/implement-html5-migration-experience-optimization/tasks.md` 的 `3.3.3`

执行前必须记录：

- 当前 commit / branch
- 触发原因
- 影响范围
- 已观察到的浏览器、PM2、E2E 或 Lighthouse 证据

## Rollback Triggers

满足任一条件时，可以进入 rollback 判断：

- 桌面端主入口无法加载，且问题与 manifest / service worker 注册表面相关。
- `/sw.js` 返回异常、注册失败或激活后导致页面反复加载旧资产。
- 浏览器 cache / service worker 影响使已修复前端仍持续展示过期 bundle。
- IndexedDB 缓存或 worker façade 造成桌面端核心市场页面不可用，且无法通过局部清理恢复。
- Lighthouse smoke 或按实际命令执行的 Chromium smoke/mainline 在 HTML5 runtime 相关路径出现新增阻断失败。

不应触发 rollback 的已知边界：

- Desktop-only manifest 未包含移动端 screenshots / splash screens 或 shortcuts。
- `vite-plugin-pwa` 仍未启用。
- 移动端安装体验或移动端响应式能力缺口。
- 当前未完成的 RUM / performance dashboard / production alerting 能力。

## Alert Signals

当前仓库内只有 repo-local / manual signals，不存在独立生产告警闭环。

可用信号：

- PM2 进程状态：`mystocks-frontend` 和 `mystocks-backend` 是否在线。
- HTTP 可达性：`/`、`/manifest.json`、`/sw.js` 是否返回预期状态。
- 浏览器控制台：是否出现 `SW registration failed`、`IndexedDB initialization failed`、`Security init failed`。
- Chrome DevTools：`Application -> Service Workers` 是否存在异常激活、反复更新或旧 cache 残留。
- Playwright / Lighthouse：按实际命令执行的桌面 Chromium smoke/mainline 或 Lighthouse smoke 是否新增失败。

这些信号只能支撑人工判断；在外部监控、告警路由和验收记录形成前，不能把 `3.3.3` 判定为完整闭环。

## Rollback Procedure

### 1. Freeze Scope

1. 停止继续扩散 UI polish、mobile/tablet 适配或无关重构。
2. 确认当前问题与 HTML5 runtime 表面相关，而不是后端 API、鉴权或路由配置的独立故障。
3. 记录当前 `git status --short`，避免在脏工作树中误回退他人改动。

### 2. Disable Registration Surface

优先使用最小回滚：

1. 回退或临时停用 `web/frontend/src/main-standard.ts` 中的 `/sw.js` 注册逻辑。
2. 如 manifest 引发安装或缓存问题，再回退 `web/frontend/index.html` 中的 manifest / PWA meta 挂接。
3. 不删除 IndexedDB、worker 或 PWA 资产文件，除非已有独立审批和功能树判定。

### 3. Clear Browser Runtime State

在受影响桌面浏览器中执行：

1. Chrome DevTools -> `Application -> Service Workers`，unregister 当前站点 service worker。
2. Chrome DevTools -> `Application -> Storage`，清理 site data 或定向清理 Cache Storage。
3. 强制刷新页面，确认不再由旧 service worker 响应。

### 4. Rebuild And Restart

按当次环境选择最小验证路径：

```bash
cd web/frontend
npm run build:no-types
```

如果共享 PM2 环境参与验证，再确认：

```bash
pm2 list
curl -I http://localhost:3020/
curl -I http://localhost:3020/manifest.json
curl -I http://localhost:3020/sw.js
```

### 5. Validate Desktop Baseline

至少执行一种桌面端验证：

```bash
cd web/frontend
env PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test --config playwright.config.js --project=chromium tests/e2e/phase4-mainline-matrix.spec.ts
```

如本次影响首屏或 install surface，再补充：

```bash
cd web/frontend
npm run test:e2e:lighthouse
```

## Validation Record Template

```markdown
## HTML5 Runtime Rollback Record

- Date:
- Branch / commit:
- Release owner:
- Trigger:
- Scope:
- Rollback action:
- Browser state cleared:
- PM2 status:
- HTTP checks:
- Playwright / Lighthouse result:
- Residual risk:
- Follow-up task:
```

## Completion Boundary

本 runbook 只能补齐回滚执行材料。

`3.3.3` 仍需以下证据才能关闭：

- 一次真实或演练 rollback validation record。
- 明确的 release owner / reviewer 签收。
- 监控告警信号进入实际发布验收链路。
- OpenSpec task 清单同步记录验证命令与结果。
