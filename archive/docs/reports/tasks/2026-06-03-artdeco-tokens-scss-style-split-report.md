# ArtDeco Tokens SCSS 拆分报告

## 任务范围

本轮处理 `web/frontend/src/styles/artdeco-tokens.scss` 的 SCSS 大文件违规。该文件是当前 Web ArtDeco token truth，因此本轮只做机械拆分：

- 保留 `artdeco-tokens.scss` 作为 facade。
- 新增同目录 token partial。
- 不修改任何 token 值、变量顺序、CSS selector、keyframes、mixin 或运行时语义。
- 不修改 router 路由、后端 API、OpenAPI/schema、frontend API client、Vue/TS 运行时逻辑。
- 不抽共享组件。

用户点名的两个路径在当前仓库中不是有效降债目标：

- `web/frontend/src/styles/zhihu-inspired.scss` 不存在。
- `web/frontend/src/styles/accessibility-enhancements.scss` 不存在。
- 真实相近文件 `web/frontend/src/styles/accessibility-focus-enhancement.scss` 为 428 行，低于 SCSS 500 行门槛。

## 拆分结果

| 文件 | 行数 | 角色 |
|---|---:|---|
| `web/frontend/src/styles/artdeco-tokens.scss` | 13 | Facade，只负责按顺序导入 token partial |
| `web/frontend/src/styles/artdeco-tokens.foundation.scss` | 195 | 字体加载、颜色、金融语义、字体尺度与字体权重 token |
| `web/frontend/src/styles/artdeco-tokens.motion.scss` | 144 | keyframes、按钮/卡片动效、价格闪烁、loader 动效 |
| `web/frontend/src/styles/artdeco-tokens.spacing-elevation.scss` | 100 | spacing、compact spacing、radius、shadow、transition token |
| `web/frontend/src/styles/artdeco-tokens.component-state.scss` | 120 | button/input/card/table/chip/tooltip/overlay 状态机 token |
| `web/frontend/src/styles/artdeco-tokens.layout-zindex.scss` | 33 | breakpoint、z-index、sidebar layout token |
| `web/frontend/src/styles/artdeco-tokens.mixins-utilities.scss` | 105 | ArtDeco mixin 与 layout/data utility mixin |

当前 `web/frontend/src/styles` 目录内 SCSS `>500` 行数量：`0`。

## 保真证据

从当前 facade 的 6 个 `@import` 依次读取 partial 后，与 `HEAD:web/frontend/src/styles/artdeco-tokens.scss` 原始内容重建对比：

- `raw_match: true`
- 原文件行数：692
- 重建行数：692
- CSS 变量声明数量：233
- CSS 变量声明顺序：完全一致
- 所有 facade/partial 行数均低于 500

## ArtDeco 检查口径

`artdeco-tokens.scss` facade 按普通 ArtDeco token 检查通过：

```bash
cd web/frontend
npm run lint:artdeco -- --target-file src/styles/artdeco-tokens.scss
```

结果：

```text
ArtDeco Token Validation Passed.
```

新增 partial 是 token definition source，必须保留原始 color/px literal 来定义 `--artdeco-*` 与 `--ad-*` token。因此 partial 不适用普通消费样式的 literal 禁止口径。

对 partial 追加 `--skip-literal-checks --forbid-legacy-tokens --forbid-legacy-sass --forbid-legacy-typography` 时，除 `foundation` 外均通过。`foundation` 命中：

```text
artdeco-tokens.foundation.scss:126: legacy token alias found
```

该行内容为：

```scss
--artdeco-font-normal: 400;
```

已对比 `HEAD` 原文件同一行，内容完全一致，属于原 token truth 文件既有内容，不是本轮拆分新增。

## GitNexus 影响分析

目标：

```text
File:web/frontend/src/styles/artdeco-tokens.scss
```

结果：

- 风险：LOW
- direct：2
- impactedCount：19
- affected_processes：0
- affected_modules：0

本地已按用户要求运行：

```bash
gitnexus analyze --index-only --max-file-size 64 --worker-timeout 10
```

结果：

- Repository indexed successfully
- 230,682 nodes
- 316,188 edges
- 300 flows

说明：GitNexus MCP `impact` 仍报告 `current_commit_differs_from_indexed_commit` stale metadata，这是本线已观察到的本地 CLI 与 MCP 元数据不同步问题；本轮没有使用 `npx gitnexus analyze`。

## 已通过验证

- Function Tree scope-check：8 个授权文件在 active authorization 内
- `git diff --check`：通过
- `web/frontend/src/styles` SCSS `>500` 行数量：0
- token facade 重建 partial：`raw_match: true`
- `npm run lint:artdeco -- --target-file src/styles/artdeco-tokens.scss`：通过
- `cd web/frontend && npm run build:no-types`：通过，Vite built in 43.67s

## 提交前 staged 验证

- staged allow-list：11 个文件均在本轮授权范围内
- 未暂存 `.governance/programs/artdeco-web-design-governance/tree.md`
- 未暂存 BacktestGPU 相关未提交工作
- 未暂存 `docs/reports/tasks/2026-06-02-gitnexus-usage-feedback.md`
- staged token facade 重建 partial：`raw_match: true`
- staged `web/frontend/src/styles` SCSS `>500` 行数量：0
- `git diff --cached --check`：通过

GitNexus staged `detect_changes`：

- changed_files：11
- risk_level：low
- affected_processes：0
- fresh_for_staged_diff：true
- changed_file_classes：config 3 / documentation 1 / style 7

最终本地 GitNexus 索引刷新：

```bash
gitnexus analyze --index-only --max-file-size 64 --worker-timeout 10
```

结果：

- Repository indexed successfully
- 230,698 nodes
- 316,204 edges
- 2730 clusters
- 300 flows
- 说明：`tree-sitter-proto` optional grammar 缺失告警仍存在，仅影响 `.proto` 解析；本轮未涉及 `.proto`。

PM2 服务状态：

- `mystocks-backend`：online，`http://localhost:8020`
- `mystocks-frontend`：online，`http://localhost:3020`

## Function Tree

- Program：`artdeco-web-design-governance`
- Node：`artdeco-tokens-scss-style-split`
- 当前目标：完成 closeout 后提交本轮授权文件。
