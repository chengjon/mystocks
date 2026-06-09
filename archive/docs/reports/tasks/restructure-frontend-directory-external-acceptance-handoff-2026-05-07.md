# restructure-frontend-directory 外部验收交接文档

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **交接目的**:
> 本文档面向后续接手 `restructure-frontend-directory` 的外部流程执行者。
> 它不替代 OpenSpec、PR 历史、部署系统或运行时事实；共享口径仍以 `architecture/STANDARDS.md`、`openspec/changes/restructure-frontend-directory/tasks.md` 和实际执行结果为准。

**最后更新**: 2026-05-07
**对应 OpenSpec change**: `restructure-frontend-directory`
**当前进度**: `openspec list` 显示 `76/92 tasks`

---

## 1. 当前状态概览

这条线的 **repo-local 重构、验证和文档收口已经完成**，但 **外部流程门禁仍未完成**。

当前已经明确的边界：

- phases `0-5` 已通过仓库内 verified micro-batch、route truth reconciliation、smoke gate 和 Playwright matrix/mainline 验证闭合
- phase `6` 的本地 comprehensive review 与 security review 已完成，并已落盘到 change package
- 当前剩余开放项全部依赖外部 PR 流程、架构审批、merge/deploy、staging 验证、issue / channel 收尾或 archive 时机
- `2026-05-07` 的 shared-PM2 Chromium 全量验证已恢复为 `295/295`，说明当前前端路由和主要页面主线在本机浏览器路径上已回到绿色基线

---

## 2. 已完成事实

截至 2026-05-07，下面这些事实已经成立：

- `openspec validate restructure-frontend-directory --strict` 通过
- canonical frontend structure truth 已收口到 `docs/guides/frontend-structure.md`
- route/layout 账本、wrapper retention、domain canonical entrypoint truth 已收口
- safe smoke gate chain 已在 repo-local 范围内闭合：
  - `npm run test:e2e:stable`
  - `npm run test:e2e:axe`
  - `npm run test:e2e:lighthouse`
- Playwright 阶段矩阵与 focused route truth 已闭合
- shared-PM2 Chromium stable 子集通过 `10/10`
- shared-PM2 full Chromium project 通过 `295/295`
- local review evidence 已存在：
  - `openspec/changes/restructure-frontend-directory/REVIEW.md`
  - `openspec/changes/restructure-frontend-directory/SECURITY-REVIEW.md`

关键真相源：

- [tasks.md](/opt/claude/mystocks_spec/openspec/changes/restructure-frontend-directory/tasks.md)
- [MIGRATION_PROGRESS.md](/opt/claude/mystocks_spec/openspec/changes/restructure-frontend-directory/MIGRATION_PROGRESS.md)
- [REVIEW.md](/opt/claude/mystocks_spec/openspec/changes/restructure-frontend-directory/REVIEW.md)
- [SECURITY-REVIEW.md](/opt/claude/mystocks_spec/openspec/changes/restructure-frontend-directory/SECURITY-REVIEW.md)
- [frontend-structure.md](/opt/claude/mystocks_spec/docs/guides/frontend-structure.md)
- [2026-05-07-frontend-chromium-full-suite-recovery.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-05-07-frontend-chromium-full-suite-recovery.md)

---

## 3. 剩余外部项

当前剩余项全部应按外部流程理解，而不是继续当作仓库内开发 backlog：

### 3.1 PR / 审批流程

- `14.1` Front-end Lead posts `"Ready for Review"` comment on PR
- `14.5` Obtain final approval from Architecture Board

### 3.2 Merge / Deploy

- `15.1` Merge PR to `main`
- `15.2` Trigger CI pipeline
- `15.3` Verify staging deployment succeeds

### 3.3 Staging 验收

- `16.1` Run smoke suite against staging environment
- `16.2` Verify all URLs resolve
- `16.3` Perform quick UI sanity check on main navigation
- `16.4` Verify that all domain pages load correctly
- `16.5` Post deployment verification report to PR

### 3.4 Archive / 外部收尾

- `17.1` Run `openspec archive restructure-frontend-directory --yes`
- `17.2` Verify change moved to archive
- `17.3` Run `openspec validate --strict` on archived change
- `17.4` Commit archive changes
- `19.4` Close any related GitHub issues
- `19.5` Post final summary to project channel

---

## 4. 当前环境约束

接手前必须知道这几个现实约束：

1. 当前工作树不是干净主线
   - 当前分支不是 `main`
   - 当前仓库存在大量既有 staged / unstaged 变更
   - 因此 `gitnexus detect_changes(scope=\"staged\")` 在本机会被全局噪音污染，不能单独作为本条线微批范围 verdict

2. 当前 PM2 服务是可用的本机验证壳，不是 staging 成功证据
   - `mystocks-backend`: `http://localhost:8020`
   - `mystocks-frontend`: `http://localhost:3020`
   - 这些结果可用于 repo-local smoke，不等同于 `15.x` / `16.x` 的外部部署完成

3. Chromium 浏览器路径阻塞已经解除
   - 当前不再需要把 Playwright 失败默认归因于“缺少 Chromium binary”
   - 若后续 staging/browser 出现失败，应先按真实运行时断言、文案、数据契约、路由或部署问题排查

---

## 5. 推荐执行顺序

建议按下面顺序推进，不要跳步勾选：

1. 先完成 `14.1` / `14.5`
   - 先把 PR 与架构审批门禁补齐

2. 再做 `15.1-15.3`
   - merge、CI、staging 成功是后续一切外部验收前提

3. 再做 `16.1-16.5`
   - 基于 staging URL 做真实 smoke、URL、导航和页面加载验收

4. 最后做 `17.x` 和 `19.4-19.5`
   - archive、issue 关闭和项目频道总结都应放在部署后证据齐备的末尾

---

## 6. 每类任务需要的证据

### 6.1 PR / 审批流程

至少记录：

- PR 链接
- `"Ready for Review"` 评论链接或截图
- Architecture Board 审批记录路径或截图

### 6.2 Merge / Deploy

至少记录：

- merge commit hash
- CI workflow URL
- staging 部署完成日志或 release record

### 6.3 Staging 验收

至少记录：

- staging URL
- 实际执行命令
- 浏览器项目
- 通过/失败/跳过数量
- 关键页面截图或验证报告

### 6.4 Archive / 外部收尾

至少记录：

- archive 执行命令
- archive commit hash
- 相关 issue 关闭链接
- 项目频道总结链接或文本归档路径

---

## 7. 现场命令入口

### 7.1 OpenSpec 与状态确认

```bash
openspec validate restructure-frontend-directory --strict
openspec list | rg "restructure-frontend-directory"
```

### 7.2 PM2 / 服务状态

```bash
pm2 jlist
curl http://localhost:8020/health/ready
curl -I http://localhost:3020/
```

### 7.3 Shared-PM2 Chromium 验证

```bash
cd web/frontend
env PLAYWRIGHT_EXTERNAL_FRONTEND=1 \
  FRONTEND_BASE_URL=http://127.0.0.1:3020 \
  E2E_FRONTEND_URL=http://127.0.0.1:3020 \
  npx playwright test --config playwright.config.js --project=chromium
```

---

## 8. 更新规则

后续接手者在关闭外部项时，建议同时更新这些位置：

1. [tasks.md](/opt/claude/mystocks_spec/openspec/changes/restructure-frontend-directory/tasks.md)
2. [MIGRATION_PROGRESS.md](/opt/claude/mystocks_spec/openspec/changes/restructure-frontend-directory/MIGRATION_PROGRESS.md)
3. 相关部署 / staging / archive 报告，放在 `docs/reports/` 下
4. Graphiti memory

不要做的事：

- 不要把本机 PM2 通过写成 staging 成功
- 不要把 shared-PM2 Chromium `295/295` 写成已完成 `15.x` / `16.x`
- 不要继续在 repo-local 范围内寻找不存在的“剩余代码改动”

---

## 9. 当前结论

`restructure-frontend-directory` 现在不是“继续重构前端目录”的问题，而是“按外部流程与部署顺序收证据”的问题。

如果后续目标仍然是这条 change 的闭合，最自然的下一步是：

1. 补齐 PR `"Ready for Review"` 与 Architecture Board 审批
2. 完成 merge / staging deploy
3. 基于 staging 做 smoke 与页面加载验收
4. 证据齐备后再执行 archive 和外部收尾
