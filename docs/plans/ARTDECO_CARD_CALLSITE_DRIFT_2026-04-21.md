# ArtDecoCard Callsite Drift Inventory

> **说明**
> 本文用于补充 [`ARTDECO_COMPONENT_GOVERNANCE_RECORD_ARTDECO_CARD.md`](ARTDECO_COMPONENT_GOVERNANCE_RECORD_ARTDECO_CARD.md)，聚焦 `ArtDecoCard` 的调用侧漂移问题。
> 目标不是立即修复，而是先把“已确认的接口漂移”和“待进一步核查项”分开记录。

---

## 1. 当前组件真实 props

当前 [`ArtDecoCard.vue`](../../web/frontend/src/components/artdeco/base/ArtDecoCard.vue) 明确声明的 props 为：

- `title`
- `subtitle`
- `hoverable`
- `clickable`
- `variant`
- `aspectRatio`

因此，调用侧如果持续依赖其他旧属性，就属于接口漂移候选。

---

## 2. 已确认的调用侧漂移

### 漂移类型 A：调用侧仍传 `decorated`

已确认以下文件仍向 `ArtDecoCard` 传入 `:decorated="true"`：

- [`web/frontend/src/views/Analysis.vue`](../../web/frontend/src/views/Analysis.vue)
- [`web/frontend/src/views/Stocks.vue`](../../web/frontend/src/views/Stocks.vue)

判断：

- `decorated` 不在当前 `ArtDecoCard` props 列表中
- 这属于“调用侧历史接口残留”
- 需要在治理阶段决定：
  - 删除旧调用
  - 还是显式恢复兼容层

当前建议：

- 默认优先清理调用侧漂移，不建议继续扩大兼容接口

---

## 3. 已确认的高频稳定调用模式

当前已确认大量调用侧稳定使用以下 props：

- `title`
- `hoverable`
- `variant`
- `class`

这说明 `ArtDecoCard` 当前最主要的公共契约已经形成，但仍需要通过治理记录把它正式冻结为 Base 样板接口。

---

## 4. 待进一步核查项

以下内容目前不直接判定为漂移，只记录为后续核查项：

### 项目 A：旧页面和历史目录中的遗留调用

例如：

- 旧视图目录
- 归档入口
- `.backup` 文件

这些调用不应直接纳入当前主线契约，但需要在治理阶段明确：

- 是否仍属于活跃路径
- 是否只是历史残留
- 是否需要按迁移收口规则处理

### 项目 B：样式层对卡片契约的隐式依赖

虽然这不一定表现为 props 漂移，但以下情况也应在后续治理中核查：

- 调用侧通过类名假设卡片内部结构
- 页面样式依赖特定 header / body / footer 结构
- 变体语义与页面实际用法不一致

这些属于“结构契约漂移”，不是单纯的 prop 漂移。

---

## 5. 建议的治理顺序

建议按以下顺序处理：

1. 先确认主线路径中所有 `decorated` 调用
2. 再区分活跃文件与历史残留文件
3. 然后冻结 `ArtDecoCard` 的 Base 层 props 契约
4. 最后再处理结构契约与样式依赖问题

原因：

- props 漂移更容易确认和清理
- 结构契约问题更适合在样板治理时一并收口

---

## 6. 一句话总结

`ArtDecoCard` 当前最明确的调用侧漂移，是少量主线路径仍在使用未声明的旧属性 `decorated`；这说明它适合作为首批“冻结 Base 契约”的样板组件。
