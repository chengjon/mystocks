# ArtDecoPageTemplate Test Matrix

> **说明**
> 本文用于把 [`ARTDECO_COMPONENT_GOVERNANCE_RECORD_ARTDECO_PAGE_TEMPLATE.md`](/opt/claude/mystocks_spec/docs/plans/ARTDECO_COMPONENT_GOVERNANCE_RECORD_ARTDECO_PAGE_TEMPLATE.md) 中的测试要求落成可执行矩阵。
> 目标不是一次性写完所有测试，而是先定义 `ArtDecoPageTemplate` 进入 P1 治理时的最小保护网。

---

## 1. 目标

这份矩阵聚焦四件事：

1. 冻结页面骨架的最小契约
2. 防止多状态壳层回归
3. 防止 tabs / trace id / emit 行为漂移
4. 为未来 ArtDeco CLI 页面模板提供可继承的测试样板

---

## 2. 测试分层建议

建议采用三层保护：

- **单元测试**: 验证 props、slots、状态切换、事件回传、默认行为
- **组件集成测试**: 验证 API 返回结构、空态 / 错误态 / trace id / tabs 联动
- **最小视觉回归**: 验证页面骨架区域没有出现结构性破坏

当前优先顺序：

1. 单元测试
2. 组件集成测试
3. 最小视觉回归

---

## 3. 测试前提

### 推荐测试工具

- `Vitest`
- `@vue/test-utils`
- 必要时使用 `msw` 或等价 fetch mock

### 推荐 Mock 原则

- 不直接依赖真实后端
- 所有接口返回必须模拟统一响应结构
- 必须覆盖：
  - 顶层 `request_id`
  - 嵌套 `data.request_id`
  - `success: false`
  - 空数组 / 空对象
  - 抛错或 rejected promise

### 推荐样板页面

优先参考现有页面：

- [`web/frontend/src/views/risk/Center.vue`](/opt/claude/mystocks_spec/web/frontend/src/views/risk/Center.vue)

它已经是当前最接近真实业务页的落地样例。

---

## 4. 最小必测用例

### A. 基础渲染契约

| 编号 | 用例 | 目标 | 优先级 |
|------|------|------|--------|
| A1 | 传入 `pageConfig.title` 后正确渲染标题 | 冻结 header 基础契约 | P0 |
| A2 | 未传 `header-actions` slot 时显示默认刷新按钮 | 冻结默认动作区行为 | P0 |
| A3 | 传入 `header-actions` slot 后覆盖默认按钮 | 冻结 slot 覆盖规则 | P0 |
| A4 | 未提供 `footer` slot 时不渲染 footer 容器 | 防止空壳层污染 DOM | P1 |

### B. 权限与多状态壳层

| 编号 | 用例 | 目标 | 优先级 |
|------|------|------|--------|
| B1 | 权限不足时显示 `访问受限` 区块 | 冻结权限拒绝壳层 | P0 |
| B2 | `loading && !dataLoaded` 时显示骨架屏 | 冻结初始加载态 | P0 |
| B3 | 请求失败时显示错误态与重试按钮 | 冻结错误壳层 | P0 |
| B4 | 返回空数组时显示空态 | 冻结空数据判定 | P0 |
| B5 | 返回空对象时显示空态 | 冻结对象空态判定 | P1 |
| B6 | 无 `apiUrl` 时直接进入内容态，不误判为空态 | 防止静态页面被模板误伤 | P0 |

### C. 数据请求与事件契约

| 编号 | 用例 | 目标 | 优先级 |
|------|------|------|--------|
| C1 | `GET` 模式下 mounted 自动请求 | 冻结默认加载协议 | P0 |
| C2 | `POST` 模式下使用 `postData` 请求 | 冻结请求方式切换 | P0 |
| C3 | 请求成功后触发 `data-loaded` 并回传 payload | 冻结成功事件契约 | P0 |
| C4 | 请求失败后触发 `data-error` | 冻结失败事件契约 | P0 |
| C5 | 点击刷新按钮后再次发起请求 | 冻结 refresh 行为 | P0 |
| C6 | `cacheTime` 生效时避免重复请求 | 冻结缓存门槛逻辑 | P1 |

### D. Trace ID 与响应归一化

| 编号 | 用例 | 目标 | 优先级 |
|------|------|------|--------|
| D1 | 顶层 `request_id` 能被展示 | 冻结主链路 request id 展示 | P0 |
| D2 | 嵌套 `data.request_id` 能覆盖展示 | 冻结嵌套响应兼容 | P0 |
| D3 | 从 `headers['x-request-id']` 提取并展示 | 冻结 header 兼容路径 | P1 |
| D4 | `showTraceId=false` 时 trace 区域不显示 | 冻结显示开关契约 | P0 |

### E. Tabs 与交互可访问性

| 编号 | 用例 | 目标 | 优先级 |
|------|------|------|--------|
| E1 | 传入 tabs 且 `showTabs=true` 时渲染标签页 | 冻结 tabs 区块显示条件 | P0 |
| E2 | `defaultTab` 合法时作为初始激活项 | 冻结默认 tab 逻辑 | P0 |
| E3 | `defaultTab` 非法时回退到第一个 tab | 冻结回退逻辑 | P0 |
| E4 | 点击 tab 后触发 `tab-change` | 冻结 tab 事件契约 | P0 |
| E5 | 方向键切换 tab 并移动焦点 | 冻结键盘可访问性 | P1 |
| E6 | `showTabs=false` 或 tabs 为空时不渲染 tabs 壳层 | 防止无效骨架残留 | P0 |

### F. Slots 与扩展骨架

| 编号 | 用例 | 目标 | 优先级 |
|------|------|------|--------|
| F1 | `stats` slot 存在时显示统计区 | 冻结 stats 扩展位 | P0 |
| F2 | `content` slot 存在时覆盖默认占位内容 | 冻结核心内容插槽 | P0 |
| F3 | `empty-action` slot 存在时覆盖空态默认刷新动作 | 冻结空态扩展位 | P1 |
| F4 | 自定义 `tabs` slot 时仍能拿到 `activeTab/changeTab/traceId` | 冻结自定义 tabs API | P0 |

---

## 5. 最小视觉回归清单

这部分不追求完整像素比对，只验证页面骨架没有结构性损坏。

建议至少保留 3 个快照场景：

1. **默认内容态**
2. **错误态**
3. **带 tabs 的内容态**

若资源有限，可先只保留 `risk/Center` 对应的 1 条稳定视觉样板。

---

## 6. 建议的首批实现范围

如果只做第一批最小保护，建议先实现以下 12 个用例：

- A1
- A2
- A3
- B1
- B2
- B3
- B4
- B6
- C3
- C4
- D1
- E4

这 12 个用例已经能覆盖：

- 页面骨架是否正常出现
- 多状态壳层是否稳定
- 成功 / 失败事件是否正常
- request id 是否开始进入标准路径
- tabs 基础交互是否未回归

---

## 7. 不建议当前就扩展的测试

当前阶段不建议优先投入：

- 全量视觉黄金图
- 所有 slot 组合的穷举测试
- 每个 token 的视觉断言
- 与真实后端联调的页面模板测试

原因：

- 当前目标是冻结骨架契约，不是把模板测试做成庞大矩阵
- 过早追求全覆盖会稀释 P1 收敛速度

---

## 8. 退出标准

当以下条件同时成立时，可判定 `ArtDecoPageTemplate` 已具备进入 P1 批次治理的最小测试基础：

- P0 优先级用例全部存在
- 成功 / 错误 / 空态 / 权限态至少各有 1 条自动化断言
- tabs 与 `tab-change` 行为已被保护
- request id 展示链路已被保护
- 至少存在 1 条最小视觉回归样板

---

## 9. 一句话总结

`ArtDecoPageTemplate` 的第一批测试不该追求“大而全”，而应优先保护页面骨架最容易回归、最影响平台化脚手架稳定性的那部分契约。
