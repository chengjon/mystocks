> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及具体执行入口，再结合根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与验证结果核对。

# HTML5 Runtime Rollout Communication Guide

## Purpose

本指南用于收口 `implement-html5-migration-experience-optimization` 的“用户沟通和培训材料准备”任务。

它只回答两个问题：

1. 当前 HTML5 runtime 能对外怎么描述
2. 团队内部在灰度前后要如何统一口径

它**不**表示：

- PWA 已完成生产部署
- 离线能力已覆盖核心业务
- 通知系统已完成用户自助配置
- 团队培训和技术分享已经实际组织完成

## Current-State Release Posture

截至当前仓库事实，可对外使用的口径应固定为：

- 浏览器入口已统一到 `index.html -> src/main-standard.ts`
- 基础 PWA 安装面、manifest、service worker 注册、IndexedDB 包装层、Web Workers 协议面都已存在
- 但 `vite-plugin-pwa` 仍未启用
- 多个 Playwright spec 仍显式使用 `serviceWorkers: 'block'`
- 当前离线能力属于 `best-effort cache / fallback`
- 当前通知偏好后端契约已存在，但活跃 `system/Settings.vue` 路由未暴露完整通知偏好表单

因此当前最准确的外部表述是：

> HTML5 runtime 基础能力和配套文档已准备好，具备继续灰度验证的代码与文档基础；但完整 PWA 生产部署、离线闭环、通知闭环和团队培训仍是后续工作。

## User-Facing Communication Template

### Release Note Short Form

可直接复用的短说明：

> 本次前端 HTML5 runtime 优化已完成基础能力整理，包括浏览器入口统一、PWA 基础安装面、缓存与离线兜底、IndexedDB 存储能力、以及部分 Web Workers 支撑能力。  
> 当前版本的安装与离线体验仍属于渐进式启用阶段，部分能力会继续通过后续灰度和兼容性验证完善。

### What Users May Reliably Expect

- 页面仍通过当前常规浏览器访问
- 在支持环境下可看到基础安装入口和 manifest 能力
- 部分静态资源与数据请求具备缓存和离线兜底
- IndexedDB 与 Web Workers 相关底层能力已存在，为后续体验优化提供基础

### What Users Must Not Be Promised Yet

- “已经是完整可离线交易应用”
- “所有业务页面都支持离线访问”
- “推送通知已经全量开放并可在设置页完整管理”
- “所有浏览器都已完成一致性验收”

## Internal Enablement Checklist

面向产品、测试、支持、运维的统一口径：

1. 对外一律描述为“基础能力已具备，仍在灰度与验收阶段”
2. 不把 `best-effort offline` 说成“完整离线模式”
3. 不把通知后端契约说成“用户设置页已完整可用”
4. 遇到安装、缓存、离线、通知问题时，优先转到：
   - [`HTML5_RUNTIME_USER_GUIDE.md`](./HTML5_RUNTIME_USER_GUIDE.md)
   - [`HTML5_RUNTIME_OPERATIONS_GUIDE.md`](./HTML5_RUNTIME_OPERATIONS_GUIDE.md)
   - [`HTML5_RUNTIME_CAPABILITY_GUIDE.md`](./HTML5_RUNTIME_CAPABILITY_GUIDE.md)

## Support FAQ Draft

### Q1: 现在能把系统当作完整 PWA 使用吗？

不能这样描述。当前只有基础安装面和部分缓存/离线兜底，不构成完整产品化 PWA 闭环。

### Q2: 没网时还能不能继续使用？

只能说“部分页面和资源可能继续可见”，不能承诺核心业务流程在离线下完整可用。

### Q3: 通知设置是否已经向普通用户开放？

不能这么说。当前通知相关契约和预留能力已存在，但活跃设置页未暴露完整通知偏好表单。

### Q4: 现在是不是已经完成发布准备？

不是。当前只是“沟通与培训材料已准备”；真正的发布准备仍受以下任务约束：

- `3.3.1` 服务器 PWA 支持
- `3.3.2` 渐进式部署策略
- `3.3.3` 回滚机制和监控告警
- `3.4.4` 团队培训和技术分享

## Recommended Handoff Order

若后续进入真实灰度或培训阶段，建议引用顺序：

1. [`HTML5_RUNTIME_CAPABILITY_GUIDE.md`](./HTML5_RUNTIME_CAPABILITY_GUIDE.md)
2. [`HTML5_RUNTIME_USER_GUIDE.md`](./HTML5_RUNTIME_USER_GUIDE.md)
3. [`HTML5_RUNTIME_OPERATIONS_GUIDE.md`](./HTML5_RUNTIME_OPERATIONS_GUIDE.md)
4. 本文档作为统一沟通口径

## Closeout Boundary

本文档的完成只意味着：

- `3.3.4` 的“材料准备”有了 repo-local current-state 成果物

本文档**不**意味着：

- `3.3.1-3.3.3` 已完成
- `3.4.4` 已完成
- 任意 PWA / offline / notification success metric 已达标
