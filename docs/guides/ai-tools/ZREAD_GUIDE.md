# Zread Guide

> **参考指南说明**:
> 本文件是 AI 阅读与使用 `zread` 的补充操作指南，不是仓库共享规则、当前实现边界或当前主流程的唯一事实来源。
> 若涉及仓库级治理规则、审批门禁或执行约束，请优先遵循 `architecture/STANDARDS.md` 与仓库根目录 `AGENTS.md`；若涉及 proposal、plan、spec、能力新增或架构调整，再结合 `openspec/AGENTS.md` 一并核对。

> **最后更新**: 2026-04-20
> **适用对象**: AI agent、代码评审者、需要快速理解仓库结构的开发者

---

## 1. 什么是 zread

`zread` 是一个为代码仓库生成 wiki 风格文档的 CLI。

它的作用不是替代源码、测试或 GitNexus，而是给 AI 提供一层更高密度的“仓库认知入口”：

- 先用生成好的 wiki 理解项目结构、模块边界、主要链路
- 再进入真实代码、契约、测试和运行入口做精确核对
- 避免在大仓库里一开始就进行低效的逐目录扫描

对 MyStocks 这类大体量、多领域、前后端混合仓库，`zread` 最适合做：

- 新人 onboarding
- 陌生模块快速入门
- 改动前入口定位
- 架构总览和业务域 mapping
- AI 上下文压缩

---

## 2. zread 在本项目里的定位

在本仓库中，`zread` 的角色是“理解层”，不是“真相源”。

优先级应保持为：

1. `architecture/STANDARDS.md` 与仓库治理入口
2. 当前代码、路由、契约、测试、运行脚本
3. `GitNexus` 的符号级 / 流程级分析
4. `zread` 生成的 wiki 作为导航和概览层

结论：

- `zread` 适合回答“系统是怎么组织的”
- `GitNexus` 适合回答“改这个会影响谁”
- 源码和测试适合回答“当前实现是否真实存在且可运行”

---

## 3. AI 的推荐使用顺序

当 AI 接到新任务时，优先按下列顺序执行：

### 场景 A：需要先理解仓库或模块

1. 读 `architecture/STANDARDS.md`
2. 若任务涉及 proposal / plan / spec / 新能力 / 架构变更，再读 `openspec/AGENTS.md`
3. 检查 `./.zread/wiki/current` 是否存在
4. 若存在，优先读取 zread wiki 的目录和相关页面
5. 根据 wiki 定位真实代码入口、路由入口、API 入口和测试入口
6. 再进入源码、GitNexus、测试命令做精确分析

### 场景 B：需要修改代码

1. 先按“场景 A”完成最小化理解
2. 使用 GitNexus 做 impact / context 分析
3. 阅读受影响代码和测试
4. 再进行修改与验证

### 场景 C：只需要回答架构或入口问题

1. 先读 zread wiki
2. 再抽样核对 1 到 3 个关键代码入口
3. 输出“wiki 结论 + 代码核对结果”，避免纯文档回答

---

## 4. 本项目中优先读取哪些 zread 文件

如果仓库已经生成 wiki，不要先运行 `zread browse` 或重新生成。
优先直接读取磁盘文件：

- `./.zread/wiki/current`
  - 当前激活的 wiki 版本
- `./.zread/wiki/versions/<id>/wiki.json`
  - 页面目录、标题、分组、文件名
- `./.zread/wiki/versions/<id>/<page>.md`
  - 具体页面内容

建议读取流程：

1. 先读 `current`
2. 再读对应版本下的 `wiki.json`
3. 根据页面标题筛选目标主题
4. 最后读少量高相关页面，不要一次性加载全部 markdown

### 本项目中的实际目录示例

在 MyStocks 本地仓库中，执行完 `zread` 后，会在项目根目录生成 `./.zread/` 目录。

典型结构如下：

```text
/opt/claude/mystocks_spec/.zread/
  wiki/
    current
    versions/
      2026-04-19-215936/
        wiki.json
        1-xiang-mu-zong-lan-mystocks-liang-hua-jiao-yi-ping-tai-ding-wei-yu-he-xin-jie-zhi.md
        10-shuang-shu-ju-ku-jia-gou-tdengine-shi-xu-cun-chu-yu-postgresql-guan-xi-cun-chu-de-zhi-ze-hua-fen.md
        ...
```

需要特别注意：

- `./.zread/wiki/current` 用于指向当前激活版本
- `./.zread/wiki/versions/<时间戳版本号>/` 才是实际生成的分析文档目录
- 具体的仓库分析内容以该版本目录下的各个 `.md` 文件为主
- 如果要人工或由 AI 浏览生成结果，应优先进入该版本目录查看所有 markdown 页面

以当前仓库为例，可直接浏览：

- [`current`](/opt/claude/mystocks_spec/.zread/wiki/current)
- [`2026-04-19-215936`](/opt/claude/mystocks_spec/.zread/wiki/versions/2026-04-19-215936)

也就是说，AI 在回答“zread 文档在哪”这一类问题时，不应只停留在 `./.zread/wiki/` 层，而应进一步落到：

`./.zread/wiki/versions/2026-04-19-215936/`

然后在该目录下读取对应主题的 `.md` 页面。

---

## 5. MyStocks 仓库中的典型读法

面向本项目，AI 可以优先按这些主题读取 zread 页面：

### 整体入门

- 项目总览
- 快速开始
- 功能树导航
- 整体架构概览
- 工程红线与治理准则

### 前端相关任务

- Vue 3 前端结构
- ArtDeco 设计系统
- API 契约同步

然后再下钻：

- `web/frontend/src/router/index.ts`
- `docs/guides/frontend-structure.md`
- 具体页面和组件

### 后端相关任务

- FastAPI 后端结构
- 事件驱动与依赖注入
- 市场数据与行情

然后再下钻：

- `web/backend/app/`
- OpenAPI / schema / service / API 路由

### 数据与存储相关任务

- 统一数据访问层
- 双数据库架构
- 多数据源适配器体系

然后再下钻：

- `src/data_access/`
- `src/adapters/`
- `src/core/`

### 量化 / 策略 / 交易相关任务

- 量化算法体系
- 策略管理与回测
- 实时交易引擎

然后再下钻：

- `src/backtesting/`
- `src/ml_strategy/`
- 交易服务与风控模块

---

## 6. AI 应该如何向用户暴露 zread 的价值

推荐让 AI 先用 zread 做“入口定位”，再给出精确执行建议。

合适的表达方式：

- “我先读 zread wiki，确认这个功能域的入口、依赖和测试位置。”
- “这个仓库已有 zread 文档，我先从 wiki 定位模块边界，再做 GitNexus impact 分析。”
- “先用 zread 总结系统结构，再下钻当前实现，避免全仓盲扫。”

不推荐的做法：

- 把 zread 当成唯一事实源
- 只根据 wiki 内容直接下结论而不核对代码
- 每次任务开始都重新生成 wiki

---

## 7. 什么时候应该重新生成 wiki

只有在以下情况下，才建议运行 `zread generate`：

- `./.zread/wiki/current` 不存在
- 仓库结构已明显变化，现有 wiki 不再可信
- 用户明确要求刷新 zread 文档
- 需要为新的大范围模块重构生成新的理解层

重新生成前，AI 必须先确认：

- 用户明确同意执行
- 已知 `generate` 会消耗 LLM token
- 已知 `generate` 会写入 `./.zread/`
- 当前仓库根目录是正确的执行目录

推荐命令：

```bash
zread generate -y --stdio
```

如果存在上次未完成的草稿：

```bash
zread generate --draft resume -y --stdio
```

若需要丢弃旧草稿并重建：

```bash
zread generate --draft clear -y --stdio
```

说明：

- `-y` 避免卡在确认提示
- `--stdio` 便于 agent 程序化消费输出
- 不要让 AI 去解析交互式 TUI

---

## 8. 什么时候不该运行 zread generate

以下情况不应该默认重生成：

- 仓库已经有可用 wiki，且本次只需要理解局部模块
- 本次任务是精确修 bug、补测试、修类型错误
- 当前真正缺的是 impact 分析，而不是架构概览
- 用户只是让 AI 回答某个具体文件或某个符号的问题

这些情况下，正确顺序通常是：

1. 先读现有 wiki
2. 再用 GitNexus
3. 再读代码

---

## 9. 与 GitNexus 的配合方式

`zread` 和 `GitNexus` 应组合使用，不要互相替代。

推荐组合：

1. `zread`
   - 找系统入口
   - 找业务域和模块边界
   - 找应该读哪些目录和页面
2. `GitNexus`
   - 做 impact 分析
   - 查 caller / callee
   - 查 execution flow
3. 源码 / 测试 / 路由 / OpenAPI
   - 验证真实实现
   - 完成修改和验证

一句话概括：

- `zread` 负责“先看懂”
- `GitNexus` 负责“先评估风险”
- 代码与测试负责“确认真实行为”

---

## 10. AI 回答模板建议

### 模板 A：仓库入门

```md
我先读 zread wiki 的目录和相关页面，确认这个仓库的模块边界、入口和依赖关系，再回到真实代码核对实现。
```

### 模板 B：修改前说明

```md
我先用 zread 确认这个功能域的结构和入口，再用 GitNexus 做 impact 分析，最后再改代码。
```

### 模板 C：解释结论时

```md
下面的结论先来自 zread 生成的仓库 wiki，我已经再用实际路由 / 代码入口做了抽样核对。
```

---

## 11. 最小实践清单

AI 在本仓库使用 zread 时，至少满足以下要求：

- 不跳过 `architecture/STANDARDS.md`
- 不把 zread 当作唯一真相源
- 有现成 wiki 时优先读磁盘，不先重生成
- 只读取必要页面，不一次性塞满上下文
- 涉及代码改动前仍要做 GitNexus impact 分析
- 输出结论时说明哪些来自 wiki，哪些已被代码核对

---

## 12. 推荐命令速查

```bash
# 查看 zread 是否可用
zread version

# 生成 wiki
zread generate -y --stdio

# 恢复未完成草稿
zread generate --draft resume -y --stdio

# 清理旧草稿并重建
zread generate --draft clear -y --stdio

# 本地浏览 wiki
zread browse --stdio
```

---

## 13. 结论

对 MyStocks 这样的仓库，`zread` 最适合充当 AI 的“仓库阅读加速器”。

正确姿势不是“让 zread 替代源码”，而是：

- 用 zread 快速看懂结构
- 用 GitNexus 做精确影响分析
- 用代码、契约、测试和运行结果确认真实行为

这样可以显著减少大仓库中的盲读、误判和上下文浪费。
