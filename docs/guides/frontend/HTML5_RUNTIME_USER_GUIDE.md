# HTML5 Runtime User Guide

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## Scope

这份 guide 面向当前 MyStocks 前端的使用者，说明 HTML5 runtime 相关能力在现阶段的实际使用方式与边界，覆盖：

1. PWA 安装体验
2. 离线使用预期
3. 通知设置当前状态

本 guide 只反映当前 repo-truth，不把未验收能力写成已完整上线。

> **产品口径说明（2026-05-08）**:
> 当前前端产品范围以 **Desktop-only** 为准。
> 因此本 guide 中提到的安装面、离线面和浏览器能力，应按桌面浏览器使用场景理解，而不是移动端产品承诺。

## 1. PWA Installation

### 1.1 Current User Expectation

当前前端已经具备基础 PWA runtime surface：

- 页面会加载 `manifest.json`
- 浏览器会尝试注册 `sw.js`
- 站点具备基础 icon / theme-color / web app compatibility meta

这意味着在支持的桌面浏览器里，用户**有机会**看到“安装应用”或“添加到桌面”的体验。

### 1.2 Important Limitation

当前安装体验不是完整闭环，原因包括：

- `vite-plugin-pwa` 仍未接入现行构建链
- 当前 Desktop-only manifest 只保留核心 PWA icons；移动端 screenshots / splash screens 与 shortcut 图标设计不属于当前已闭合范围
- 当前仓库并没有把“安装成功率”验收到完成状态

因此用户应把当前体验理解为：

- 已具备基础安装面
- 但不是经过完整产品化验收的 PWA 安装流程
- 也不应被理解成移动端安装体验是当前产品目标

### 1.3 Practical User Path

若浏览器支持并触发安装提示，可按浏览器默认流程安装。

若没有看到安装提示：

- 这不一定是故障
- 更可能是浏览器启发式条件未满足，或当前 runtime 仍处于部分落地状态

## 2. Offline Usage

### 2.1 Current User Expectation

当前前端已经存在 service worker 缓存策略与本地缓存能力：

- 静态资源缓存
- 部分 API 的 network-first / cache fallback
- IndexedDB 本地缓存

因此在网络波动时，用户可能看到：

- 部分页面资源仍可加载
- 部分历史缓存数据仍可显示

### 2.2 Important Limitation

当前离线能力仍不应被理解为“核心业务离线闭环已完成”，因为：

- 多个 Playwright 用例当前显式禁用了 service worker
- OpenSpec 中 11 路由离线测试和跨浏览器 PWA 验证仍未闭合；IndexedDB 当前只按 Desktop Chromium version `1` schema bootstrap / close-reopen persistence 闭合，不代表跨浏览器或未来 schema upgrade 迁移已验收
- 还没有“11 个路由离线可用”这类已验收结论

用户应按如下预期使用：

- 离线/弱网支持是 best-effort
- 不保证所有业务页面都可稳定离线使用
- 关键交易、风险、系统写操作不应依赖离线模式
- 当前重点仍是桌面端弱网容错，不是移动端离线产品化闭环

## 3. Notification Settings

### 3.1 Current User-facing Truth

当前通知能力的 repo-truth 是分层的：

- 后端有用户级通知偏好契约：`/api/notification/preferences`
- 前端 API 层已有对应读写方法
- 但当前**活跃系统设置页面** [Settings.vue](../../../web/frontend/src/views/system/Settings.vue) 只说明这条契约存在，没有暴露完整通知偏好表单

### 3.2 Important Limitation

仓库里虽然保留了一个 ArtDeco 风格的通知设置组件：

- [ArtDecoSettings.vue](../../../web/frontend/src/views/artdeco-pages/ArtDecoSettings.vue)
- [NotificationSettings.vue](../../../web/frontend/src/views/artdeco-pages/settings/NotificationSettings.vue)

但它不是当前 router 的活跃设置入口。

因此对普通用户来说，当前应理解为：

- 通知偏好契约已经存在
- 但当前活跃系统设置页还没有完整开放这套通知偏好 UI

### 3.3 Practical User Guidance

如果用户在现行设置页没有看到完整“通知偏好”表单，这属于当前产品边界，不是单点异常。

在当前状态下：

- 可以把通知能力理解为“后端契约与前端预留能力已存在”
- 不能把它理解为“现行设置页已完整支持用户自助配置通知策略”

## 4. Recommended Reading Order

如需更技术化的说明，建议按顺序阅读：

1. [HTML5_RUNTIME_CAPABILITY_GUIDE.md](./HTML5_RUNTIME_CAPABILITY_GUIDE.md)
2. [HTML5_RUNTIME_OPERATIONS_GUIDE.md](./HTML5_RUNTIME_OPERATIONS_GUIDE.md)
3. OpenSpec `implement-html5-migration-experience-optimization` 当前 task 状态
