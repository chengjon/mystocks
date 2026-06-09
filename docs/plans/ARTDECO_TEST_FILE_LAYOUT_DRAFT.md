# ArtDeco Test File Layout Draft

> **说明**
> 本文用于定义 ArtDeco 三层样板测试在前端仓库中的推荐落位方式。
> 它不是一次性重排现有测试目录，而是为接下来的 ArtDeco 测试新增文件提供统一入口，避免继续生成新的平行结构。

---

## 1. 目标

这份草案要解决四个问题：

1. `Base / Core Skeleton / Domain` 三层样板测试该放在哪里
2. 组件单测、纯数据测试、视觉样板应如何区分
3. 如何复用仓库现有 `__tests__ / __node_tests__` 习惯，而不再继续发散
4. 下一步开始写测试代码时，第一批文件应该创建在哪

---

## 2. 当前仓库现状观察

从当前前端目录可以确认：

- 组件与视图层测试大量使用 `__tests__`
- 纯数据或无 DOM 依赖测试大量使用 `__node_tests__`
- 少量历史 `.spec.ts` 直接与模块同目录共存

这说明仓库已经存在两条相对稳定的约定：

1. **组件 / DOM / Vue 渲染测试** 放入 `__tests__`
2. **纯数据 / Node 侧测试** 放入 `__node_tests__`

当前不应再新增第三套 ArtDeco 专属目录习惯。

---

## 3. 推荐总原则

### 原则 1：测试就近落位

测试文件应尽量靠近被测对象，而不是集中堆到一个新的全局目录。

原因：

- 降低查找成本
- 保持消费者和测试上下文一致
- 符合仓库当前已有做法

### 原则 2：按测试性质而不是按热情分目录

- 有 Vue 渲染、slot、emit、DOM 结构断言的测试，归入 `__tests__`
- 纯数据、常量、映射、变换、presence 校验的测试，归入 `__node_tests__`

### 原则 3：不为 ArtDeco 新增第三套平行结构

当前不建议新建：

- `__artdeco_tests__`
- `visual-tests/`
- `component-tests/`

这类新目录只会让测试组织再次分裂。

---

## 4. 三层样板推荐落位

### Base

被测对象：

- [`web/frontend/src/components/artdeco/base/ArtDecoCard.vue`](../../web/frontend/src/components/artdeco/base/ArtDecoCard.vue)
- [`web/frontend/src/components/artdeco/base/ArtDecoButton.vue`](../../web/frontend/src/components/artdeco/base/ArtDecoButton.vue)

推荐测试目录：

- `web/frontend/src/components/artdeco/base/__tests__/`

推荐文件：

- `ArtDecoCard.spec.ts`
- `ArtDecoButton.spec.ts`

原因：

- 这两者是标准组件渲染测试
- 应与组件本体保持近邻
- 不应绕到 views 侧或全局 tests 侧

### Core Skeleton

被测对象：

- [`web/frontend/src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue`](../../web/frontend/src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue)
- [`web/frontend/src/views/artdeco-pages/_templates/composables/useArtDecoPageTemplate.ts`](../../web/frontend/src/views/artdeco-pages/_templates/composables/useArtDecoPageTemplate.ts)

推荐测试目录：

- `web/frontend/src/views/artdeco-pages/_templates/__tests__/`
- `web/frontend/src/views/artdeco-pages/_templates/composables/__node_tests__/`

推荐文件：

- `ArtDecoPageTemplate.spec.ts`
- `useArtDecoPageTemplate.data.test.ts`

原因：

- 页面模板本体属于 Vue 渲染测试，应进入 `__tests__`
- 若后续把响应归一化、request id 提取等纯逻辑单独抽测，可进入 `__node_tests__`

### Domain

被测对象：

- [`web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskOverviewPanel.vue`](../../web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskOverviewPanel.vue)
- [`web/frontend/src/views/artdeco-pages/risk-tabs/riskManagementHelpers.ts`](../../web/frontend/src/views/artdeco-pages/risk-tabs/riskManagementHelpers.ts)

推荐测试目录：

- `web/frontend/src/views/artdeco-pages/risk-tabs/__tests__/`
- `web/frontend/src/views/artdeco-pages/risk-tabs/__node_tests__/`

推荐文件：

- `ArtDecoRiskOverviewPanel.spec.ts`
- `riskManagementHelpers.test.ts` 或保持 helper 纯数据测试继续归 `__node_tests__`

原因：

- 仓库当前 `risk-tabs` 已同时存在 `__tests__` 与 `__node_tests__`
- 继续沿用这套结构最稳妥

---

## 5. 推荐的首批真实文件清单

如果下一步开始写测试代码，建议首批新增以下文件：

1. `web/frontend/src/views/artdeco-pages/_templates/__tests__/ArtDecoPageTemplate.spec.ts`
2. `web/frontend/src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskOverviewPanel.spec.ts`
3. `web/frontend/src/components/artdeco/base/__tests__/ArtDecoCard.spec.ts`
4. `web/frontend/src/components/artdeco/base/__tests__/ArtDecoButton.spec.ts`

如果只开第一批，不建议同时新增更多入口。

---

## 6. 命名建议

### 组件渲染测试

统一使用：

- `ComponentName.spec.ts`

例如：

- `ArtDecoPageTemplate.spec.ts`
- `ArtDecoRiskOverviewPanel.spec.ts`
- `ArtDecoCard.spec.ts`
- `ArtDecoButton.spec.ts`

### 纯数据或纯逻辑测试

统一使用：

- `xxx.test.ts`

例如：

- `useArtDecoPageTemplate.data.test.ts`
- `riskManagementHelpers.test.ts`

原因：

- 当前仓库已经隐含形成 `spec.ts` 偏 Vue 组件、`test.ts` 偏 Node / 数据逻辑 的习惯
- 不必绝对化，但 ArtDeco 这一批最好主动保持一致

---

## 7. 视觉回归文件如何处理

当前阶段不建议先为视觉回归新建独立目录体系。

建议策略：

- 先把最小视觉场景与组件测试文件同批规划
- 等真正选定视觉回归工具后，再决定快照或样板资源放置位置

也就是说，现阶段先定义“要有哪些视觉场景”，不要先扩张“视觉文件夹工程”。

---

## 8. 明确不建议的落位方式

当前不建议：

- 在 `web/frontend/src/tests/` 下新建整套 ArtDeco 组件单测
- 在 repo 根部新建 `tests/frontend/artdeco/`
- 在每个样板旁边混用 `.spec.ts` 与 `.test.ts` 两种组件命名
- 为同一组件同时建 `__tests__` 与同目录单文件 spec

原因：

- 这些做法都会把当前已经形成的弱约定再次打散

---

## 9. 与批次计划的关系

这份草案服务于 [`ARTDECO_P1_TEST_IMPLEMENTATION_BATCH_PLAN.md`](ARTDECO_P1_TEST_IMPLEMENTATION_BATCH_PLAN.md)。

两者关系是：

- 批次计划回答“先测谁、后测谁”
- 文件落位草案回答“测试文件落在哪里、怎么命名”

两者一起才能真正进入代码实现。

---

## 10. 当前最优起手式

如果下一步立刻进入测试代码实现，当前最优起手式是：

1. 先创建 `web/frontend/src/views/artdeco-pages/_templates/__tests__/ArtDecoPageTemplate.spec.ts`
2. 只完成 Skeleton 第一批 P0 用例
3. 再创建 `web/frontend/src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskOverviewPanel.spec.ts`
4. 再视情况补 `Base` 组件测试文件

这样可以最小化新增目录数量，也最符合当前治理顺序。

---

## 11. 一句话总结

ArtDeco 测试落位不该重新发明一套目录体系，而应沿用仓库现有 `__tests__ / __node_tests__` 习惯做就近落位；真正需要新增的不是新目录哲学，而是第一批真正写出来的测试文件。
