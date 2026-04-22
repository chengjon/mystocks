# ArtDeco Component Governance Record: ArtDecoPageTemplate

> **说明**
> 本文基于 [`ARTDECO_COMPONENT_GOVERNANCE_RECORD_TEMPLATE.md`](/opt/claude/mystocks_spec/docs/plans/ARTDECO_COMPONENT_GOVERNANCE_RECORD_TEMPLATE.md) 产出，是首批样板组件的第三份实战治理记录草案。

---

## 1. 组件基本信息

- **组件名称**: `ArtDecoPageTemplate`
- **组件路径**: [`web/frontend/src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue`](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue)
- **关联逻辑**: [`web/frontend/src/views/artdeco-pages/_templates/composables/useArtDecoPageTemplate.ts`](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/_templates/composables/useArtDecoPageTemplate.ts)
- **所属层级**: `Core Skeleton`
- **所属业务域**: `页面骨架 / 通用`
- **当前状态**: `候选`

---

## 2. 选择该组件的原因

- **高频程度**: `中`
- **选择原因**:
  - 页面骨架影响大
  - 适合作为 CLI 模板来源
  - Base / Domain 之外需要单独定义骨架层
  - 可观测性与状态一致性承载点明确

### 补充说明

当前直接使用点不算很多，但它的治理价值高于“引用次数”本身。

抽样确认的直接使用点包括：

- [`web/frontend/src/views/risk/Center.vue`](/opt/claude/mystocks_spec/web/frontend/src/views/risk/Center.vue)
- [`web/frontend/src/views/artdeco-pages/_templates/ExampleRiskManagement.vue`](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/_templates/ExampleRiskManagement.vue)

它之所以应该优先治理，是因为它已经把以下平台职责打包在一起：

1. 页面头部与动作区骨架
2. 权限 / loading / error / empty 多状态壳层
3. tabs + trace id + content panel 的统一组织方式
4. 数据加载、刷新、事件回传的默认协议

这说明它不是普通 Base 组件，而是未来页面脚手架最有价值的标准壳。

---

## 3. 当前主要问题

勾选项：

- Base / Domain 边界不适用，需要补充 `Core Skeleton` 层定义
- 页面依赖方式需要冻结
- 测试保护不足
- 可观测性契约需要固定
- CLI 模板价值高但当前接口仍偏松散

### 问题摘要

- `ArtDecoPageTemplate` 当前实际职责已经超出 Base 组件范畴，继续按普通组件治理会造成层级误判。
- 它把 `pageConfig`、`stats`、`tabs`、`defaultTab`、多个 slots，以及 `data-loaded` / `data-error` / `tab-change` 事件组合成了页面骨架契约，这个契约一旦漂移，会影响整批页面模板。
- `useArtDecoPageTemplate` 同时处理接口请求、缓存时间、空态判定、权限检查、请求 ID 提取和 tab 焦点管理，说明“页面骨架逻辑”已经实质存在，但尚未被平台规则正式命名。
- 当前错误路径里仍直接 `console.error`，与项目“统一 logger / observability”方向相比，后续需要纳入更明确的页面层监控策略。

---

## 4. token 影响记录

- **涉及的视觉类别**:
  - 间距
  - 状态语义
  - 页面骨架层级
  - tabs / footer / shell 容器视觉

- **现有 token 可复用项**:
  - 页面内大量 ArtDeco Base / Core 组件已复用现有 token 体系
  - `ArtDecoHeader` / `ArtDecoButton` / `ArtDecoSkeleton` / `ArtDecoStatCard` 已构成骨架层基础积木

- **需要新增 token 项**:
  - 当前阶段不建议先新增 token
  - 应先冻结页面骨架结构，再决定是否抽离 `page-shell / tabs-shell / footer-shell` 专属 token 家族

- **需要合并 / 淘汰 token 项**:
  - 后续需核查页面模板样式文件中是否存在仅服务单一页面模板、却应回收为通用骨架 token 的命名

- **暂不处理项**:
  - 骨架层装饰性视觉微调不应先于结构契约冻结

---

## 5. 结构治理记录

- **当前判定**: `提升为 Core Skeleton`

- **结构治理动作**:
  - 明确新增骨架层定义
  - 冻结页面模板契约
  - 拆分“可稳定复用的页面壳职责”和“业务页自定义内容”
  - 明确 CLI 页面模板来源

### 治理理由

- `ArtDecoPageTemplate` 不是 Base，因为它不是最小视觉积木；也不是 Domain，因为它不携带具体业务语义。
- 它更适合被定义为 `Core Skeleton`，即“页面级标准壳层”，位于 Base/Core 组件之上、业务页面之下。
- 该层一旦定义清楚，可以把“标题区、刷新动作、权限页、空态页、错误态、trace id、标签页导航、默认内容容器”变成标准能力，而不是每个页面各写一遍。
- 这类骨架层稳定之后，才适合进入未来 ArtDeco CLI，成为页面生成模板的真相源。

---

## 6. 测试与门禁要求

- **是否需要最小单测**: `是`
- **是否需要视觉回归保护**: `是`
- **是否需要交互测试**: `是`
- **是否需要样式门禁关注**: `是`

### 建议测试项

- `pageConfig` 基础渲染
- 默认刷新按钮显示与禁用条件
- 权限拒绝态
- 初始 loading / error / empty 三类状态切换
- `data-loaded` / `data-error` / `tab-change` 事件触发
- `showStats` / `showTabs` / `showTraceId` 开关行为
- `defaultTab` 回退逻辑
- tabs 键盘可访问性
- 请求 ID 提取与展示

---

## 7. 对 CLI 模板的价值

- **是否适合作为 CLI 模板来源**: `是`

- **适用模板类型**:
  - 页面模板
  - 页面壳层模板
  - tabs 页面模板
  - 带数据加载状态的业务页模板

### 原因

- 未来如果建设 ArtDeco CLI，最有价值的不是先生成“单个按钮”，而是生成“可运行页面骨架”。
- `ArtDecoPageTemplate` 已天然包含页面启动期最需要统一的结构：header、refresh、loading、error、empty、tabs、content、footer、trace id。
- 它是最接近“页面级脚手架真相源”的现成资产，治理完成后非常适合成为 CLI 的首批 page scaffold。

---

## 8. 最终结论

本组件建议作为第 1 批治理对象，但治理方式应区别于 Base 组件。

原因：

- 虽然直接引用量不如 `ArtDecoCard` / `ArtDecoButton`，但页面骨架影响范围更大
- 它决定未来 ArtDeco 是否真正具备“平台化页面模板”能力
- 它是承接可观测性、状态一致性和脚手架输出的关键壳层

治理重点：

- 正式定义 `Core Skeleton` 层，而不是把它继续混在 Base / Domain 讨论里
- 冻结 `pageConfig + slots + emits + trace id` 的页面骨架契约
- 明确哪些职责留在模板层，哪些职责必须下沉到业务页面
- 为未来 CLI 页面模板准备最小稳定输入面

测试重点：

- 页面多状态切换
- tabs 与可访问性交互
- 请求 ID / refresh / data emit 的骨架行为
- 最小视觉回归保护

CLI 价值：

- 可作为未来 ArtDeco CLI 的页面脚手架核心样板
- 可把“页面骨架标准化”从人工复制，推进到自动生成

---

## 9. 一句话总结

`ArtDecoPageTemplate` 的价值不在于“又一个可复用组件”，而在于它已经接近 MyStocks ArtDeco 平台里的页面骨架真相源，应该被作为 `Core Skeleton` 层优先冻结，而不是继续按普通组件自然生长。
